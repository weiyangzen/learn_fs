# subset-b-006571 research

This grouped report covers the assigned bootconfig, ftrace conversion, classic BPF utility, and bpftool source files under `sources/distributed-fs/ceph-client/tools`. Each file section is delimited for deterministic splitting into the mapped source-tree-aligned research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bootconfig/main.c -->
# sources/distributed-fs/ceph-client/tools/bootconfig/main.c

Purpose: this is the userspace `bootconfig` utility for applying, deleting, and displaying Linux bootconfig data in an initrd image, or for rendering a standalone bootconfig file. The initrd format it manages appends bootconfig text plus padding and a footer of little-endian size, little-endian checksum, and `BOOTCONFIG_MAGIC`.

Important APIs/types/functions: it is built around `linux/bootconfig.h` APIs such as `xbc_init()`, `xbc_exit()`, `xbc_root_node()`, `xbc_node_get_child()`, `xbc_node_get_next()`, `xbc_node_compose_key()`, `xbc_calc_checksum()`, and `xbc_get_info()`. `load_xbc_from_initrd()` validates the footer, size, checksum, and parser state. `apply_xbc()` validates a config file, removes any previous bootconfig, appends the new payload/footer, and rolls back partial writes. `delete_xbc()` truncates an existing appended bootconfig. `show_xbc()` chooses initrd extraction first, then treats small files as standalone bootconfig text. `xbc_show_compact_tree()` and `xbc_show_list()` provide tree and flattened key-value views.

Control flow: `main()` parses mutually exclusive `-a`, `-d`, and `-l` options, then dispatches to apply, delete, or show. Apply flow loads the config, computes `strlen(buf) + 1` as the stored size, validates parse errors with line/column reporting, deletes any previous footer block, computes `BOOTCONFIG_ALIGN` padding from the current initrd size, and appends data plus footer with `O_APPEND`. Show flow opens the target, attempts footer extraction, falls back to parsing the file as raw bootconfig if there is no footer and the size is within `XBC_DATA_MAX`, then prints either compact tree syntax or list syntax.

State and persistence: persistent state is the target initrd file contents. Apply mutates the initrd by appending bootconfig bytes, zero padding, and footer; delete mutates it by truncating exactly `size + BOOTCONFIG_FOOTER_SIZE` bytes from the tail. Parser state is global to the xbc library and is exited before writing. In-memory buffers are dynamically allocated per operation and freed on normal exits; some error paths in `apply_xbc()` can return `-ENOMEM` after allocating `buf` without freeing it, which is process-lifetime leakage only.

Dependencies and integration points: the tool depends on standard POSIX file APIs, endian conversion helpers, and the kernel bootconfig parser compiled into tools. Its on-disk contract must match the kernel initrd bootconfig loader. The shell scripts in `tools/bootconfig/scripts` call `bootconfig -l` as their canonical flattening mechanism.

Risks: the footer detection treats a matching tail magic as authoritative, so corrupted size/checksum data produces hard errors. `load_xbc_fd()` does not enforce that `read()` returns the full requested size; short reads can flow into parse/checksum handling. `apply_xbc()` calculates checksum before adding padding, so readers must use the stored size and same checksum convention. Partial write rollback maps short successful writes to `-ENOSPC`, but rollback failure leaves an explicitly warned potentially corrupted initrd. `show_xbc()` prints an empty parsed tree if a large non-initrd file has no footer because fallback parsing is only for small files.

Test signals: `test-bootconfig.sh` exercises basic show/delete/apply, repeated apply replacement, footer size alignment, deletion truncation, parse error locations, maximum node count, maximum data size, same-key append/override behavior, quotes, whitespace preservation/removal, and expected good/bad sample files. Additional useful tests would inject short reads/writes, checksum mismatch, oversized footer size, and rollback failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bootconfig/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bootconfig/scripts/bconf2ftrace.sh -->
# sources/distributed-fs/ceph-client/tools/bootconfig/scripts/bconf2ftrace.sh

Purpose: this script converts a bootconfig file describing `kernel.*` and `ftrace.*` settings into tracefs/debugfs writes. It can print the commands only, apply them with root privileges, and optionally initialize ftrace before applying.

Important APIs/functions: `run_cmd()` echoes every operation and conditionally executes it under `--apply`. `xbc_init`, `xbc_get_val`, `xbc_has_key`, `xbc_has_branch`, and `xbc_subkeys` come from `xbc.sh` and provide flattened bootconfig access. `set_value_of()` and `set_array_of()` map scalar and array bootconfig keys to tracefs files. Histogram helpers (`print_one_histogram()`, `print_hist_array()`, `print_hist_actions()`, `setup_histograms()`) build ftrace trigger syntax. `setup_event()`, `setup_events()`, and `setup_instance()` apply event, instance, tracing, buffer, and snapshot settings.

Control flow: the script parses `--debug`, `--apply`, and `--init`, locates tracefs or debugfs tracing, optionally sources `ftrace.sh` and runs `initialize_ftrace`, then sources `xbc.sh` and flattens the bootconfig. It first applies global kernel knobs such as `kernel.dump_on_oops`, graph depth, graph filters, and graph notrace. It exits early if no `ftrace` branch exists. Otherwise it applies the root instance, creates configured `ftrace.instance.*` directories, and applies each instance's options/events.

State and persistence: without `--apply`, it only prints commands. With `--apply`, it persists changes in live tracefs files and `/proc/sys/kernel/ftrace_dump_on_oops`; with `--init`, it first resets tracing state through `ftrace.sh`. Bootconfig parsing uses a temporary flattened file created by `xbc.sh` and removed on exit. Tracefs state includes options, clocks, CPU masks, tracers, buffer sizes, snapshots, filters, dynamic probes, synthetic events, triggers, histograms, and enable flags.

Dependencies and integration points: it requires a working `bootconfig` binary, a mounted tracefs or debugfs tracing directory, root permissions for writes, POSIX shell tools, and ftrace file semantics. It integrates with `ftrace.sh` for reset and `xbc.sh` for key lookup. It understands bootconfig schemas for `ftrace.event.GROUP.EVENT`, `kprobes`, `synthetic`, histogram actions, and per-instance configuration.

Risks: many command strings are built through unquoted shell variables and executed with `eval`, so bootconfig values are effectively shell input when `--apply` is used. Several tests use unquoted filenames and key names. Appending with `>>` is correct for trigger-style files but may duplicate settings on repeated application unless initialized. Kprobe and synthetic event creation depends on exact ftrace syntax and ordering. `size2kb()` runs through `eval`, so malformed `buffer_size` values are dangerous. Histogram action ordering and variable references can be fragile when bootconfig ordering differs from ftrace dependency ordering.

Test signals: dry-run output should be compared with expected tracefs commands for scalar settings, arrays, events, filters, kprobes, synthetic events, histograms, and instances. Root-only integration tests should run against a disposable tracefs namespace or VM, with `--init` followed by apply and `ftrace2bconf.sh` round-trip checks. Security-focused tests should cover quoting, spaces, semicolons, and shell metacharacters in bootconfig values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bootconfig/scripts/bconf2ftrace.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bootconfig/scripts/ftrace.sh -->
# sources/distributed-fs/ceph-client/tools/bootconfig/scripts/ftrace.sh

Purpose: this file provides shell helper functions for resetting and toggling ftrace state inside a tracefs directory. It is intended to be sourced and run from `$TRACEFS` or an instance directory, not executed as a standalone command.

Important APIs/functions: simple controls include `clear_trace()`, `disable_tracing()`, `enable_tracing()`, and `reset_tracer()`. Cleanup helpers include `reset_trigger_file()`, `reset_trigger()`, `reset_events_filter()`, `reset_ftrace_filter()`, `disable_events()`, and `clear_synthetic_events()`. `initialize_ftrace()` orchestrates a full reset to nop tracer, disabled events, no filters/triggers/probes, cleared PID filters, optional snapshot reset, empty trace buffer, and tracing re-enabled.

Control flow: `initialize_ftrace()` stops tracing, resets current tracer, removes triggers before filters/events, clears function filters and PID filters when files exist, clears kprobe/uprobe/synthetic event definitions, resets snapshot, clears trace, and enables tracing again. Trigger reset removes action triggers first because ftrace requires action triggers to be deleted before their associated hist/trigger commands in some cases.

State and persistence: all state is live tracefs state. There is no durable file written by the script itself. The operations write to tracing control files and can destroy existing user tracing setup in the current tracefs scope.

Dependencies and integration points: it assumes current working directory contains tracefs files such as `trace`, `tracing_on`, `current_tracer`, `events/*/*/trigger`, `events/*/*/filter`, `set_ftrace_filter`, and dynamic event files. `bconf2ftrace.sh --init` sources this file and calls `initialize_ftrace`.

Risks: glob expansion over `events/*/*` can fail or act unexpectedly on kernels without matching files or with special event layouts. Several commands parse trigger/filter lines using `grep`, `cut`, and shell word splitting, which can mishandle unusual trigger syntax. `reset_ftrace_filter()` clears `set_ftrace_filter` before trying to read back entries, so the later loop is effectively operating on already-cleared state on some shells/kernels. This script is destructive by design.

Test signals: integration tests should verify that synthetic events, kprobes, uprobes, normal triggers, hist action triggers, event filters, ftrace filters, tracers, snapshots, and trace output are cleared on representative kernels. Idempotency tests should run initialization twice and on kernels lacking optional files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bootconfig/scripts/ftrace.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bootconfig/scripts/ftrace2bconf.sh -->
# sources/distributed-fs/ceph-client/tools/bootconfig/scripts/ftrace2bconf.sh

Purpose: this script inspects live tracefs/debugfs ftrace state and emits a bootconfig representation to stdout. It is the inverse companion to `bconf2ftrace.sh`, with explicit warnings for ftrace settings that cannot be faithfully recovered.

Important APIs/functions: `emit_kv()` prints bootconfig assignments. `global_options()` captures graph depth and warns about expanded graph filters. `kprobe_event_options()` and `synth_event_options()` export dynamic events. `per_event_options()`, `event_options()`, and `instance_options()` walk events and instances. Helper-variable tracking uses `defined_vars()`, `referred_vars()`, `DEFINED_VARS`, `UNRESOLVED_EVENTS`, and `retry_unresolved()` to delay histogram triggers that reference variables defined by other events.

Control flow: after option parsing and tracefs discovery, the script emits global kernel options, root `ftrace` instance options, and then each directory under `$TRACEFS/instances`. For each instance it emits non-default trace options, non-local trace clock, buffer size, snapshot allocation, CPU mask, tracing_on off state, current tracer, warnings for unsupported ftrace filters, and event configuration. Event traversal emits global/group enablement, per-event trigger actions, enable flags when not inherited, and filters. Unresolved histogram dependencies are retried up to three times.

State and persistence: it does not mutate tracefs; it reads live files and emits text. Its transient state is shell variables tracking histogram-defined and unresolved variables. The emitted bootconfig can later be persisted by redirecting stdout or applied with `bconf2ftrace.sh`.

Dependencies and integration points: it requires tracefs/debugfs, standard shell utilities, and ftrace file formats. The output schema is consumed by `bconf2ftrace.sh`. It intentionally cannot preserve wildcard expressions for graph/ftrace filters after the kernel expands them.

Risks: live ftrace state can change during traversal, so output is not atomic. `ls`-based traversal and unquoted paths assume conventional event and instance names. Trigger parsing treats non-comment trigger lines as opaque action strings but still has special histogram variable dependency logic based on regexes, which may miss complex trigger syntax. Return kprobes are skipped with a warning. Non-`kprobes` dynamic kprobe group names are normalized to `kprobes`, losing the original group. Unsupported wildcard filters produce warnings rather than output.

Test signals: round-trip tests should initialize ftrace, apply bootconfig, dump back to bootconfig, and compare normalized output for trace options, clocks, buffers, event enables, filters, dynamic kprobes, synthetic events, and hist triggers. Tests should also assert warnings for return probes, expanded filters, unsupported graph filters, and unresolved histogram variables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bootconfig/scripts/ftrace2bconf.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bootconfig/scripts/xbc.sh -->
# sources/distributed-fs/ceph-client/tools/bootconfig/scripts/xbc.sh

Purpose: this file is a small shell adapter around the `bootconfig -l` flattened output format. It gives other bootconfig scripts key lookup, branch detection, value extraction, and subkey enumeration.

Important APIs/functions: initialization resolves `BOOTCONFIG` from the sibling build output or `PATH`. `xbc_init()` creates a temporary file, traps cleanup, and stores `bootconfig -l FILE` output. `xbc_get_val()` extracts values for a key and uses `sed`/`xargs` to split bootconfig arrays into one value per line, optionally limited by `xargs -L`. `xbc_has_key()` and `xbc_has_branch()` are grep probes. `xbc_subkeys()` computes prefix depth and extracts child key names.

Control flow: callers source the file, call `xbc_init BCONF`, then issue grep-based queries against `$XBC_TMPFILE`. Cleanup removes the temporary file on exit or termination.

State and persistence: the only state is `$XBC_TMPFILE`, `$BOOTCONFIG`, and helper-local shell variables. The temporary flattened bootconfig file is removed by `xbc_cleanup()` unless the process is killed in a way that bypasses traps.

Dependencies and integration points: it depends on a compatible `bootconfig` binary, `mktemp`, `grep`, `cut`, `sed`, `xargs`, and POSIX shell. `bconf2ftrace.sh` depends on its key model and assumes flattened keys are emitted as `key = value`.

Risks: key names are interpolated directly into grep regular expressions, so regex metacharacters in keys can change matching semantics. Values are split through `xargs`, which strips quoting and can transform whitespace. `mktemp bconf-XXXX` creates the file in the current directory rather than a private temp directory. The error message spells "Erorr", and command lookup via `which` can be non-portable.

Test signals: tests should cover scalar values, arrays with spaces and quotes, nested keys, duplicate/same-key append behavior, missing keys, branch prefixes that are substrings of other prefixes, and cleanup of the temporary file after normal and signal exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bootconfig/scripts/xbc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bootconfig/test-bootconfig.sh -->
# sources/distributed-fs/ceph-client/tools/bootconfig/test-bootconfig.sh

Purpose: this is the shell regression test for the `bootconfig` tool. It creates temporary initrd/config/output files, applies and removes bootconfig payloads, and verifies parser behavior against sample good and bad files.

Important APIs/functions: `xpass()` expects a command to succeed and increments the test counter; `xfail()` expects a command to fail. `cleanup()` removes temporaries and exits with the accumulated failure count. The script calls `bootconfig`, `dd`, `wc`, `expr`, `grep`, `diff`, `awk`, and sample files under `samples/`.

Control flow: the test starts with basic command and delete-without-bootconfig checks, creates a 4096-byte initrd and simple config, applies it, checks show output and exact aligned size, repeats apply to ensure replacement rather than growth, deletes and checks truncation, then tests noisy invalid tail bytes. It then exercises maximum node count, maximum file size, same-key append and override, quotes, duplicate tree branches, trailing-space behavior, parse error line/column reporting, all expected failure samples, and all expected success samples with rendered-output diffs.

State and persistence: all files are temporary under the requested test directory or current directory and are removed by the trap. `NG` and `NO` track failed and total test cases. The script mutates temporary initrd content repeatedly and relies on sample files for expected parser behavior.

Dependencies and integration points: it assumes the compiled binary is `${TESTDIR}/bootconfig`, `ALIGN=4`, and sample file names under `samples/`. It exercises the `main.c` initrd footer contract and the bootconfig parser linked into the tool.

Risks: unquoted variables and command arguments can break if `TESTDIR` contains spaces. Some test names and comments contain typos but do not affect behavior. The maximum-size test relies on `base64 -w0`, which is GNU-specific. The expected sample loop uses relative `samples/...` paths, so it must be run from the bootconfig source directory or an equivalent working directory.

Test signals: this script is itself the main signal for `main.c` correctness. Additional CI hardening could run it under a temp directory path containing spaces, under fault-injection wrappers for short writes/truncation failures, and with sanitizers for the C binary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bootconfig/test-bootconfig.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/Makefile -->
# sources/distributed-fs/ceph-client/tools/bpf/Makefile

Purpose: this Makefile builds and installs the standalone BPF tools `bpf_jit_disasm`, `bpf_dbg`, and `bpf_asm`, and delegates to `bpftool` and `resolve_btfids`. It also generates lexer/parser sources for the classic BPF assembler.

Important targets/variables: `PROGS` lists the three standalone binaries. Pattern rules generate `%.yacc.c` with bison and `%.lex.c` with flex, compile objects, and link binaries. `FEATURE_TESTS` checks `libbfd` and disassembler ABI variants; `feature-disassembler-four-args` and `feature-disassembler-init-styled` add compatibility defines. Targets include `all`, `clean`, `install`, `bpftool`, `bpftool_install`, `bpftool_clean`, `resolve_btfids`, and `resolve_btfids_clean`.

Control flow: the Makefile derives `srctree` for in-tree and selftests/out-of-tree invocation, conditionally includes feature detection unless the goal is only clean-like, compiles objects under `$(OUTPUT)`, links `bpf_jit_disasm` with libopcodes/libbfd/libdl, `bpf_dbg` with readline, and `bpf_asm` with generated parser/lexer objects. `all` always includes delegated `bpftool`.

State and persistence: build products live under `$(OUTPUT)` when set or the source directory otherwise. Generated state includes `.o`, generated yacc/lex files, feature dumps, and delegated build outputs. Install persists binaries under `$(DESTDIR)$(prefix)/bin`.

Dependencies and integration points: it depends on kernel tools make infrastructure, flex, bison, libbfd/opcodes, readline, and exported kernel headers. It is integrated into the larger kernel tools build and selftests environments.

Risks: feature detection is skipped for some clean targets only; missing libbfd/readline/flex/bison will fail relevant builds. If `OUTPUT` is unset, generated files can appear in the source directory. `bpf_jit_disasm` ABI compatibility depends on feature probes matching the installed binutils headers and libraries.

Test signals: useful checks are `make -C tools/bpf`, `make clean`, out-of-tree `OUTPUT=...`, install with `DESTDIR`, and feature matrix builds with/without libbfd/readline/flex/bison. Generated parser rebuilds should be tested after touching `bpf_exp.l` or `bpf_exp.y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpf_asm.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpf_asm.c

Purpose: this is the minimal command-line driver for the classic BPF assembler. It reads an assembler program from stdin or the first openable filename argument and calls the parser/compiler to emit classic BPF bytecode in comma format or C initializer format.

Important APIs/functions: `main()` handles `-c`, opens an input file if supplied, and calls external `bpf_asm_compile(FILE *fp, bool cstyle)` implemented by the bison grammar in `bpf_exp.y`. `cstyle` controls whether output is `{ code, jt, jf, k }` initializer lines or `len,code jt jf k,...` format suitable for other tools.

Control flow: arguments are scanned left to right. Any argument beginning with `-c` enables C-style output. The first subsequent argument that can be opened becomes input; failed opens are ignored and stdin remains selected. There is no explicit usage output or error exit for nonexistent files.

State and persistence: no persistent state is written. The input file stream is closed by `bpf_asm_compile()` if it is not stdin. Output goes to stdout.

Dependencies and integration points: it depends on the generated lexer/parser and classic BPF definitions in `linux/filter.h`. Its output can be consumed by `bpf_dbg`, socket filter loaders, tc/xt_bpf-related tooling, or test fixtures.

Risks: silently falling back to stdin on open failure can confuse scripts. `-cfoo` is accepted as `-c` because `strncmp("-c", argv[i], 2)` is used. There is no validation in this wrapper; parse and instruction-limit errors abort inside the compiler.

Test signals: assemble from stdin and file, check `-c` output, check nonexistent file behavior, and compare parser output against known `tcpdump -ddd` or documented classic BPF examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpf_asm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpf_dbg.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpf_dbg.c

Purpose: this is an interactive classic BPF debugger and interpreter. It loads classic BPF bytecode, validates it with the kernel, maps a tcpdump-format pcap file, and lets users run, step, disassemble, dump, select packets, and set breakpoints.

Important APIs/types/functions: core types include `struct shell_cmd`, `struct pcap_filehdr`, `struct pcap_pkthdr`, and `struct bpf_regs`. Global state includes `bpf_image`, `bpf_prog_len`, `bpf_breakpoints`, register history `bpf_regs`, current registers `bpf_curr`, pcap file descriptor/mapping/cursor, and packet counter. Execution is handled by `bpf_single_step()`, `bpf_run_all()`, and `bpf_run_stepping()`. Loading is handled by `cmd_load_bpf()`, `try_load_pcap()`, and `cmd_load()`. Shell commands are dispatched through `execf()` and readline completion.

Control flow: `main()` optionally opens command input/output files and enters `run_shell_loop()`. The shell parses full command names from `cmds`. `load bpf` parses the comma-separated `len,code jt jf k,...` format and validates the program with `SO_ATTACH_FILTER`. `load pcap` mmaps a regular pcap file and validates magic. `run` executes the current program over packets until the end, a requested limit, or a breakpoint. `step` advances a configurable number of instructions, supports negative register-history restore, and moves to the next packet after return. `select` positions the pcap cursor by packet index.

State and persistence: process state persists across shell commands: loaded program, mapped pcap, packet cursor, breakpoints, current registers, and register history. Readline history is read from and written to `$HOME/.bpf_dbg_history`; readline init may come from `$HOME/.bpf_dbg_init`. No pcap or BPF program is modified.

Dependencies and integration points: it depends on readline/history, mmap, pcap classic file format, Linux classic BPF socket filter validation, and classic BPF instruction constants. It intentionally does not support kernel BPF extensions during interpretation after validation detects `SKF_AD_OFF` loads.

Risks: pcap parsing assumes native tcpdump magic endianness only and does not support swapped magic or pcapng. It uses `MAP_LOCKED`, which can fail under low memlock limits. Some bounds checks use `>= pcap_map_size`, making exact-end packets invalid. `BPF_LDX_W | BPF_LEN` appears to set `A` rather than `X`, which is a possible interpreter bug. Long-running BPF programs rely on kernel validation but the local interpreter does not independently enforce every safety property. `getenv("HOME")` can be NULL, which would break history path construction.

Test signals: tests should load known `bpf_asm` and `tcpdump -ddd` programs, run against small pcaps with pass/fail expectations, verify stepping/backtracking, breakpoint dumps, disassembly formatting, pcap cursor wrapping, malformed pcap rejection, oversized/short BPF strings, and interpreter agreement with kernel/socket filter behavior for representative instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpf_dbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpf_exp.l -->
# sources/distributed-fs/ceph-client/tools/bpf/bpf_exp.l

Purpose: this flex lexer tokenizes the low-level classic BPF assembly language used by `bpf_asm`.

Important APIs/tokens: it recognizes instruction mnemonics such as `ldb`, `ldh`, `ld`, `ldi`, `ldx`, `ldxi`, `ldxb`, `st`, `stx`, jump operations, ALU operations, `ret`, `tax`, and `txa`. It maps extension aliases such as `proto`, `type`, `poff`, `ifidx`, `nla`, `mark`, `queue`, `cpu`, VLAN fields, and `rand` to `SKF_AD_*` numbers. It returns punctuation tokens, `number`, `label`, `extension`, and `K_PKT_LEN` to the bison parser.

Control flow: flex rules are case-insensitive and skip C comments, semicolon comments, preprocessor-style line comments, spaces, tabs, and newlines. Numeric literals support hex, binary, signed/unsigned decimal, and octal. Labels are duplicated with `strdup()` and later freed by the parser's label cleanup.

State and persistence: lexer state is generated flex state. `yylval` carries labels and numbers. No persistent files are written.

Dependencies and integration points: it includes `linux/filter.h` and the generated `bpf_exp.yacc.h` token definitions. Its token choices are tightly coupled to grammar productions in `bpf_exp.y`.

Risks: label regex requires at least two characters because it uses `[a-zA-Z_][a-zA-Z0-9_]+`, so one-character labels are not accepted. Unknown characters call `yyerror()` after printing a message without a newline. Numeric conversion does not check overflow. `strdup()` failure is not handled before returning a label token.

Test signals: lexer/parser tests should cover every mnemonic, extension alias with and without `#`, numeric base, comments, whitespace, labels, single-character label rejection, unknown characters, and case-insensitivity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpf_exp.l -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpf_exp.y -->
# sources/distributed-fs/ceph-client/tools/bpf/bpf_exp.y

Purpose: this bison grammar parses classic BPF assembly and emits `struct sock_filter` instructions. It also resolves symbolic labels into classic BPF branch offsets.

Important APIs/types/functions: grammar rules map load/store, jump, ALU, return, and misc instructions to `BPF_*` opcodes through `bpf_set_curr_instr()`. `bpf_set_curr_label()` and `bpf_set_jmp_label()` collect labels for current instruction and pending branch targets. `bpf_stage_1_insert_insns()` runs `yyparse()`, `bpf_stage_2_reduce_labels()` resolves `k`, `jt`, and `jf` labels, and `bpf_asm_compile()` orchestrates init, parse, reduction, cleanup, and output. Static arrays include `out[BPF_MAXINSNS]` and label arrays for direct jumps and true/false branch labels.

Control flow: parse productions accept classic forms for absolute/indirect loads, packet length, memory slots, immediate loads, `ldxb 4*([off]&0xf)`, stores, unconditional jumps, conditional jumps with one or two labels, inverse convenience jumps (`jneq`, `jlt`, `jle` encoded by swapping false branches), ALU ops with constants or X, returns, and A/X transfers. After parsing, unconditional `JA` labels are resolved to signed deltas stored in `k`; conditional labels are resolved to 8-bit forward offsets in `jt` and `jf`.

State and persistence: compiler state is process-local static state reset in `bpf_init()` and freed in `bpf_destroy()`. Output is printed to stdout. There is no persistent storage. Fatal parse, allocation assertion, label, and range errors call `exit(1)`.

Dependencies and integration points: it depends on `linux/filter.h`, generated lexer tokens, and classic BPF instruction encoding. `bpf_asm.c` provides the CLI, and `bpf_dbg.c` can consume the non-C output format.

Risks: conditional jump labels can only target forward instructions because `bpf_encode_jt_jf_offset()` rejects negative offsets and offsets above 255, matching classic BPF branch encoding but surprising users. Unconditional `JA` negative offsets are stored through unsigned `k`; kernel validation may reject unsafe loops, but assembler messaging is limited. `assert()` is used for label-array allocation. Label memory is freed only after successful parse/reduction; fatal exits leak process memory. Duplicate labels resolve to the first matching label with no diagnostic.

Test signals: parser tests should cover every production, label resolution, out-of-range conditional jumps, missing labels, duplicate labels, maximum instruction count, C-style and numeric output, inverse branch aliases, and kernel validation of assembled programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpf_exp.y -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpf_jit_disasm.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpf_jit_disasm.c

Purpose: this tool extracts the last BPF JIT image dumped in kernel logs or a supplied log file and disassembles it with binutils, or writes the raw image to a file.

Important APIs/functions: `get_klog_buff()` uses `klogctl()` to read kernel log contents. `get_flog_buff()` reads a regular file. `get_last_jit_image()` searches for the last `flen=... proglen=... pass=... image=...` header and parses following `JIT code` hex lines into a byte buffer. `get_asm_insns()` initializes BFD/disassembler state using the current executable's architecture and prints disassembled instructions plus optional opcode bytes. `main()` handles `-o`, `-O`, and `-f`.

Control flow: after option parsing and `bfd_init()`, the tool reads the selected log buffer, extracts the last image, and either disassembles it to stdout or writes it to `-O` output. Extraction compiles a regex, walks to the last matching header, bounds `proglen` at 1,000,000, allocates the image, tokenizes following log lines by newline, and converts hex bytes from lines containing `JIT code`.

State and persistence: it reads kernel log or a file, allocates an image buffer, and optionally writes a binary output file with `O_CREAT|O_TRUNC`. It does not clear kernel logs or otherwise mutate kernel state.

Dependencies and integration points: it depends on BFD/opcodes, disassembler compatibility glue, `sys/klog.h`, regex, and kernel BPF JIT debug log format produced when `/proc/sys/net/core/bpf_jit_enable` is set to `2`. It is built with feature-detected disassembler ABI defines from the Makefile.

Risks: many internal failures use `assert()`, which can abort instead of returning diagnostics. The parser assumes a specific log format and mutates the log buffer with `strtok()`. It asserts that parsed bytes equal `proglen`; truncated logs abort. BFD architecture selection from the current executable may not match offloaded or cross-architecture dumps. `-h` is documented but not present in the getopt string, so it falls into usage through the default case.

Test signals: tests should use fixture log files with one and multiple JIT images, truncated images, oversized `proglen`, malformed headers, opcode display, raw output writes, stdin/file inputs, and binutils ABI variants. Integration tests require enabling BPF JIT debug logs on a test kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpf_jit_disasm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/Documentation/Makefile -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/Documentation/Makefile

Purpose: this Makefile builds, installs, cleans, and uninstalls bpftool man pages from reStructuredText sources.

Important targets/variables: `MAN8_RST` collects `bpftool*.rst`, `DOC_MAN8` maps them to `$(OUTPUT)*.8`, and `RST2MAN_DEP` checks for `rst2man`. The `see_also` make function appends a generated SEE ALSO section referencing `bpf(2)`, `bpf-helpers(7)`, and sibling bpftool pages. Targets include `man`, `man8`, pattern `$(OUTPUT)%.8`, `clean`, `install`, and `uninstall`.

Control flow: the default goal `man` builds all man8 pages. Each page concatenates the source `.rst` with generated SEE ALSO text and pipes it through `rst2man --verbose --strip-comments`. Install creates `$(DESTDIR)$(man8dir)` and installs generated pages mode 644.

State and persistence: generated `.8` files are written under `$(OUTPUT)`. Install/uninstall mutate the destination man directory. No source `.rst` files are modified.

Dependencies and integration points: it uses kernel tools `Makefile.include`, `rst2man`, install/rm/rmdir, and is invoked by the parent bpftool Makefile's `doc*` targets.

Risks: missing `rst2man` causes a make-time error only when generating pages. The generated SEE ALSO list depends on current wildcard results and excludes the source page being built by basename filtering. If `OUTPUT` is unset, generated man pages land in the documentation source directory.

Test signals: run `make man`, `make clean`, `make install DESTDIR=...`, and `make uninstall DESTDIR=...`; verify generated pages include SEE ALSO entries and no stale pages remain after clean.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/Documentation/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/Makefile -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/Makefile

Purpose: this is the main bpftool build system. It builds libbpf for target and bootstrap use, optionally builds BPF skeletons, compiles bpftool objects, links the final bpftool binary, installs bash completion, and delegates documentation targets.

Important targets/variables: `LIBBPF`, `LIBBPF_BOOTSTRAP`, include directories, internal libbpf headers, `BPFTOOL_BOOTSTRAP`, `SRCS`, `OBJS`, `BOOTSTRAP_OBJS`, `VMLINUX_BTF_PATHS`, `BUILD_BPF_SKELS`, and feature flags drive the build. Feature tests cover clang CO-RE, LLVM, libcap, libbfd variants, and libelf zstd. Targets include `all`, `bootstrap`, `clean`, `install-bin`, `install`, `uninstall`, and `doc*`.

Control flow: the Makefile derives `srctree`, creates output directories, builds target libbpf and host bootstrap libbpf, imports internal headers, runs feature detection unless only doc/clean goals are requested, chooses LLVM or libbfd JIT disassembly support, optionally removes `jit_disasm.c` and `sign.c`, generates `vmlinux.h` and skeleton headers with bootstrap bpftool when CO-RE prerequisites are available, compiles `kernel/bpf/disasm.c` as `disasm.o`, and links `bpftool`.

State and persistence: build state is under `$(OUTPUT)` or current directory: target and bootstrap libbpf trees, dependency files, objects, skeleton headers, `vmlinux.h`, feature dumps, and `bpftool`. Install persists the binary under `$(prefix)/sbin` and bash completion under `$(bash_compdir)`.

Dependencies and integration points: it depends on tools libbpf, kernel headers, libelf, zlib, optional zstd, libcap, libcrypto, LLVM/clang/strip, libbfd/opcodes, and a valid vmlinux BTF source for skeleton generation. It integrates with kernel build outputs through `O`, `KBUILD_OUTPUT`, `VMLINUX_BTF`, and `VMLINUX_H`.

Risks: optional feature detection strongly changes compiled command coverage, especially JIT disassembly, signing, libcap permission handling, and skeleton-backed commands. Host and target compiler flag separation must remain correct for cross builds. If no BTF source is found or clang CO-RE is unavailable, skeleton-dependent functionality is compiled out through `BPFTOOL_WITHOUT_SKELETONS`. Unset `OUTPUT` can place many generated files in the source tree.

Test signals: build matrix coverage should include native, cross, `OUTPUT=`, `SKIP_LLVM=1`, `SKIP_LIBBFD=1`, `SKIP_CRYPTO=1`, with/without libcap, with explicit `VMLINUX_H`, and doc/install/uninstall flows. Runtime smoke tests should verify compiled-out feature messaging when optional dependencies are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/btf.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/btf.c

Purpose: this implements the `bpftool btf` command family: listing BTF objects and dumping BTF data in raw or C header form from kernel BTF IDs, programs, maps, or files.

Important APIs/types/functions: `dump_btf_type()` formats individual BTF kinds, including int, ptr, array, struct/union, enum/enum64, fwd, func/proto, var, datasec, float, decl tags, type tags, and modifiers. `dump_btf_raw()` emits raw type records. `dump_btf_c()` uses libbpf `btf_dump` to generate `vmlinux.h`-style C, with optional stable sorting from `sort_btf_c()`. `dump_btf_kfuncs()` emits weak kfunc prototypes based on decl tags. `do_dump()` parses BTF sources and dump options. `do_show()` lists BTF objects and references from programs/maps/PIDs using hashmaps built by `build_btf_tables()`.

Control flow: `do_btf()` dispatches `show/list`, `dump`, and `help`. Dump flow first resolves the source: map/prog file descriptor, BTF ID, or one or more files. Map dumps can restrict roots to key, value, kv, or all; `root_id` can filter arbitrary root types unless other filtering was already selected. File dumps can merge multiple split BTF files with a required base BTF, automatically loading `/sys/kernel/btf/vmlinux` when sysfs module paths are used. It then loads BTF if needed, validates root IDs before emitting C boilerplate, and chooses raw or C format.

State and persistence: command state is transient. It opens kernel object FDs, loads/parses BTF objects, builds in-memory hashmaps for references, and writes output to stdout/json writer. It does not mutate kernel BTF state. The global `base_btf` from bpftool options may be used or populated for module fallback.

Dependencies and integration points: it depends on libbpf BTF APIs, kernel `bpf_btf_*`, map/prog FD parsers from `common.c`, bpftool JSON helpers, object reference tracking from other bpftool modules, and `/sys/kernel/btf/vmlinux` for common base BTF fallback. Generated C output is consumed by BPF CO-RE builds.

Risks: BTF source parsing has many combinations and error paths; invalid root IDs are checked before C output to avoid half-emitted headers. Sorting C output uses hashes and names for stability but still depends on libbpf type traversal behavior. Multiple file merge requires correct base BTF or can fail/dedup incorrectly. Kernel module BTF loaded by ID without a base triggers fallback warning and sysfs base loading. `build_btf_type_table()` frees only the failing hashmap on some errors, so callers must handle paired cleanup carefully.

Test signals: tests should cover raw and C dumps from map/prog/id/file, root filters, invalid and duplicate root IDs, map key/value/kv/all modes, JSON raw dump, JSON rejection for C dump, module BTF with and without base, multi-file merge, kfunc prototype emission, enum64/decl-tag/type-tag formatting, and list output with program/map/PID references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/btf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/btf_dumper.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/btf_dumper.c

Purpose: this file formats typed BTF data values and BTF line-info snippets for bpftool map/program output. It bridges raw bytes plus BTF metadata into JSON/plain textual representations.

Important APIs/functions: `btf_dumper_type()` dispatches recursive value dumping through `btf_dumper_do_type()`. Helpers handle pointers (`btf_dumper_ptr()`), modifiers, enums and enum64, arrays including char arrays as strings, 128-bit integers, bitfields, ints, structs/unions, vars, and datasecs. `btf_dumper_type_only()` renders type-only/function signatures. `btf_dump_linfo_plain()`, `btf_dump_linfo_json()`, and `btf_dump_linfo_dotlabel()` print source line info for plain, JSON, and graph labels.

Control flow: value dumping resolves BTF kind and recursively advances byte offsets based on resolved element sizes and bit offsets. Struct/union dumping iterates members, handling kflag bitfield encodings. Function pointer dumping can optionally interpret a 32-bit pointer value as a BPF program ID and print the matching program function name plus ID. Type-only rendering recursively prints C-like signatures for int, typedef, float, struct, union, enum, array, pointer, modifiers, function prototypes, functions, vars, and datasecs.

State and persistence: the dumper itself is stateless apart from the caller-provided `struct btf_dumper`, JSON writer, and flags such as `is_plain_text` and `prog_id_as_func_ptr`. It opens program FDs transiently when resolving program IDs in function pointer fields, then closes them.

Dependencies and integration points: it depends on libbpf BTF APIs, bpftool JSON writer, BPF program info syscalls, and the `struct btf_dumper` contract from `main.h`. `cfg.c` and xlated dumpers use line-info dot labels for graph output.

Risks: many routines trust that caller-provided data buffers are large enough for the BTF type; size enforcement belongs to callers. Pointer dumping casts to `unsigned long`, so output follows host pointer width. Char array detection rejects non-printable strings and requires a terminator within array length. Bitfield and 128-bit handling is endian-sensitive through `__BIG_ENDIAN_BITFIELD`/`__LITTLE_ENDIAN_BITFIELD`. Unsupported or forward kinds produce marker strings and often `-EINVAL`, which can leave partially emitted JSON objects.

Test signals: typed map dump tests should cover ints of all widths/encodings, bool, char printable/nonprintable, enum/enum64 named and unknown values, arrays, strings, nested structs/unions, bitfields crossing bytes, 128-bit values, datasecs, vars, pointers with and without program-ID resolution, and plain/json/dot line-info escaping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/btf_dumper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/cfg.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/cfg.c

Purpose: this file builds and prints a Graphviz DOT control-flow graph for translated eBPF instructions. It is used by bpftool's xlated dump path when graph output is requested.

Important APIs/types/functions: internal graph types are `struct cfg`, `struct func_node`, `struct bb_node`, and `struct edge_node`. `cfg_partition_funcs()` finds BPF-to-BPF subprogram starts from pseudo-call targets. `func_partition_bb_head()`, `func_partition_bb_tail()`, and `func_add_special_bb()` partition each function into basic blocks plus ENTRY/EXIT nodes. `func_add_bb_edges()` adds fallthrough and jump edges. `cfg_dump()` emits DOT, and public `dump_xlated_cfg()` builds, dumps, and destroys the graph.

Control flow: `dump_xlated_cfg()` treats the input byte buffer as `struct bpf_insn[]`, initializes a `cfg`, partitions functions, partitions each function into basic blocks, adds entry/exit and edges, prints DOT subgraphs per function, then frees all nodes and edges. Blocks start at function start, jump targets, and conditional fallthroughs. Basic block tails are computed from the next block head or function end.

State and persistence: all graph state is heap-allocated and freed in `cfg_destroy()`. Output is written to stdout as DOT. It does not mutate kernel or bpftool state.

Dependencies and integration points: it depends on Linux list helpers, eBPF instruction macros, bpftool error reporting, and `dump_xlated_for_graph()` from the xlated dumper to render instructions inside record-shaped nodes. The header `cfg.h` exposes only `dump_xlated_cfg()`.

Risks: pointer arithmetic assumes jump targets and pseudo-call targets are valid within the provided instruction buffer; invalid buffers can produce missing destination blocks or undefined behavior. Error paths during graph construction may return without freeing partially allocated graph state because `cfg_destroy()` is called only after successful build in `dump_xlated_cfg()`. DOT labels rely on the xlated dumper to escape instruction text. The predecessor edge list is only populated for exit's incoming edge; most graph traversal uses successor lists, so this is enough for output but not a complete bidirectional graph.

Test signals: graph tests should cover straight-line programs, unconditional jumps, conditional jumps, exits, calls/subprograms, line info/opcode options, invalid jump targets, empty buffers, and DOT rendering accepted by Graphviz.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/cfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/cfg.h -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/cfg.h

Purpose: this header exposes the bpftool eBPF control-flow graph dumping entry point.

Important APIs/types/functions: it includes `xlated_dumper.h` and declares `dump_xlated_cfg(struct dump_data *dd, void *buf, unsigned int len, bool opcodes, bool linum)`. The `dump_data` argument carries formatting and BTF/line-info context for instruction rendering.

Control flow: there is no executable control flow in the header. Its include guard prevents duplicate declarations.

State and persistence: no state is declared or persisted.

Dependencies and integration points: consumers call this from translated program dump code to produce DOT graphs. The declaration couples `cfg.c` to the xlated dumper's public data structure.

Risks: callers must pass a buffer containing whole `struct bpf_insn` records and a length in bytes. The header does not document ownership or validation; those assumptions are enforced only by implementation behavior.

Test signals: compile coverage is the main signal. Runtime graph tests belong to `cfg.c` and xlated dump command tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/cgroup.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/cgroup.c

Purpose: this implements `bpftool cgroup` commands for showing, tree-walking, attaching, and detaching BPF programs on cgroups.

Important APIs/functions: `parse_attach_type()` accepts libbpf attach type strings and legacy/prefix strings. `show_bpf_prog()` prints one attached program, resolving program names and optional attach BTF names from vmlinux BTF. `show_effective_bpf_progs()` and `show_attached_bpf_progs()` query attachment lists. `do_show()`, `do_show_tree()`, `do_attach()`, and `do_detach()` implement user commands. `find_cgroup_root()` finds the cgroup v2 mount from `/proc/mounts`.

Control flow: `do_cgroup()` dispatches subcommands. Show opens the requested cgroup, checks whether any supported attach type has programs, optionally starts JSON/table headers, loads vmlinux BTF, and iterates `cgroup_attach_types`. Tree show resolves a root path or cgroup v2 mount, then uses `nftw()` to visit directories and query attached programs. Attach/detach open the cgroup, parse attach type, parse a program handle through shared helpers, parse optional `multi`/`override` flags for attach, and call `bpf_prog_attach()` or `bpf_prog_detach2()`.

State and persistence: show commands are read-only. Attach and detach persist kernel cgroup BPF attachment state. Static state includes `query_flags`, `btf_vmlinux`, and `btf_vmlinux_id` for the current command; program and cgroup FDs are closed after use.

Dependencies and integration points: it depends on libbpf string helpers, BPF cgroup attach/query syscalls, shared program parsers from `common.c`, bpftool JSON output, BTF lookup, `/proc/mounts`, and cgroup v2 filesystem paths.

Risks: the fixed arrays for queried program IDs and attach flags hold 1024 entries; more attachments can be truncated depending on kernel query behavior. `btf_vmlinux` is assigned repeatedly and not freed in this file, relying on process lifetime or libbpf ownership assumptions. Attach flag parsing permits both `multi` and `override` together even if the kernel rejects the combination. Tree walking can be expensive on large cgroup hierarchies and races with cgroup deletion.

Test signals: tests should cover show/list and tree with and without effective mode, JSON/plain output, all accepted attach type aliases, attach and detach with id/name/tag/pinned program handles, multi/override flags, absent cgroup v2 mount, unsupported attach types returning `EINVAL`, and BTF attach-name resolution for fentry/fexit-like cgroup programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/common.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/common.c

Purpose: this file contains shared bpftool utilities for diagnostics, resource limits, bpffs/tracefs mounting, pinned object access, object pinning, fd/type parsing, object lookup by id/name/tag/path, device printing, kernel config reading, and small formatting helpers.

Important APIs/functions: diagnostics are `p_err()` and `p_info()`. `set_max_rlimit()` probes memcg-vs-rlimit accounting and raises `RLIMIT_MEMLOCK` when needed. Mount helpers include `mount_tracefs()`, `create_and_mount_bpffs_dir()`, and `mount_bpffs_for_file()`. Object helpers include `open_obj_pinned()`, `open_obj_pinned_any()`, `do_pin_fd()`, and `do_pin_any()`. Parsers include `prog_parse_fds()`, `prog_parse_fd()`, `map_parse_fds()`, `map_parse_fd()`, `map_parse_fd_and_info()`, and `parse_u32_arg()`. Other helpers include pinned-object table building, `get_prog_full_name()`, fdinfo reading, network device/offload printing, attach type string conversion, and `read_kernel_config()`.

Control flow: most helpers are called by command modules. Program/map parsing consumes `argc/argv` tokens by handle type (`id`, `name`, `tag`, `pinned`), opens matching FDs, and returns one or many descriptors. Name/tag lookup enumerates kernel IDs and filters info records. Pinning ensures a bpffs mount exists unless `--nomount` blocked it. Kernel config reading tries `/boot/config-$(uname -r)` then `/proc/config.gz`, validates the generated-file marker, and extracts requested `CONFIG_` values.

State and persistence: persistent mutations include mounting tracefs/bpffs, creating directories for pinning, and pinning BPF objects. Static transient state includes page-size cache and globals used by `nftw()` callbacks for pinned-object tables. Returned FDs and allocated strings/hashmaps transfer cleanup responsibility to callers.

Dependencies and integration points: it depends on libbpf, BTF APIs, zlib, Linux mount/proc/sysfs files, bpftool globals from `main.h`, and hashmap utilities. Nearly every bpftool command module uses these helpers for object handles and output.

Risks: `known_to_need_rlimit()` temporarily sets process soft memlock to zero; bpftool is single-threaded, but embedding this code elsewhere would be unsafe. Auto-mounting bpffs/tracefs changes system mount state unless `--nomount` is used. Name-based program/map lookup can match multiple objects and returns errors where a single FD is required. `get_fd_type()` relies on `/proc/self/fd` symlink text containing `bpf-map`, `bpf-prog`, or `bpf-link`. Kernel config parsing assumes the second line is the generated-file marker and may skip valid distro configs with different headers.

Test signals: command tests should cover every object handle form, multiple matches, stale IDs, pinned paths outside bpffs, auto-mount allowed/blocked, pin path already exists, map read-only open flags, program full-name fallback to BTF func info, offload device printing, kernel config fallback paths, and cleanup of allocated pinned-object tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/feature.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/feature.c

Purpose: this implements `bpftool feature`, including kernel/device feature probing and listing libbpf-known built-in program, map, attach, link, and helper names.

Important APIs/functions: printing helpers include `print_bool_feature()`, `print_kernel_option()`, and section start/end functions for plain, JSON, or C macro output. Probes include procfs sysctl readers, `probe_kernel_image_config()`, `probe_bpf_syscall()`, program/map type probing, helper probing, and miscellaneous instruction-set/prog-size probes. `handle_perms()` validates or drops capabilities for privileged/unprivileged probing. `do_probe()` parses options and runs all sections; `do_list_builtins()` prints built-in name lists.

Control flow: `do_feature()` dispatches `probe`, `list_builtins`, and `help`. Probe parsing accepts optional `kernel` or `dev NAME`, `full`, `unprivileged`, and `macros [prefix PREFIX]`. It raises memlock limits as needed, checks permissions/capabilities, starts JSON root if requested, scans system config, tests `bpf()` syscall availability, and only then probes program types, map types, helpers, and miscellaneous features. Device probing restricts program and map probes to offload-relevant types and uses `prog_ifindex`/`map_ifindex`.

State and persistence: probing can load short BPF programs and create maps transiently, closing FDs immediately. With libcap and `unprivileged`, it can drop effective capabilities in the running process. It reads procfs, sysfs, and kernel config files but does not persist configuration changes. Static state includes `full_mode` and optionally `run_as_unprivileged`.

Dependencies and integration points: it depends on libbpf probe helpers, BPF syscalls, `common.c` for memlock/kernel config support, optional libcap, procfs, sysfs netdevice vendor files, and bpftool JSON output. Macro output is intended for build-time feature gating in external BPF code.

Risks: probes are sensitive to permissions, LSM policy, lockdown, kernel config availability, backports, and offload driver behavior. Helper probing in non-full mode intentionally skips helpers that can emit dmesg messages. `probe_misc_feature()` treats `fd >= 0 || !errno` as success, so unusual libbpf errno behavior can affect results. Fixed `supported_types[128]` assumes program type values fit. Device vendor-specific helper log parsing currently special-cases Netronome. Capability handling differs when bpftool is built without libcap.

Test signals: tests should cover plain/json/macro output, macro prefixes, kernel-only and device-only probes, unprivileged mode with libcap, missing procfs, missing kernel config, missing capabilities, helper skip behavior with and without `full`, list_builtins groups, and expected behavior on kernels without BPF syscall or specific feature support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/feature.c -->
