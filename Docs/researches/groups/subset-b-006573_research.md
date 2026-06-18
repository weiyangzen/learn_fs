# subset-b-006573 research

Grouped research report for the requested source files. Each source section preserves the source path as its title and is wrapped for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/prog.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/prog.c

Purpose: Implements the `bpftool prog` command family: listing, dumping, pinning, loading, attaching, test-running, profiling, and trace-log streaming for BPF programs. It is the main user-facing program control surface and coordinates libbpf object loading, BPF syscalls, generated-loader execution, signing, bpffs pinning, map reuse, BTF metadata printing, and skeleton-based profiling.

Important APIs, types, and functions: `do_prog()` dispatches subcommands. `parse_attach_type()` maps CLI strings to `enum bpf_attach_type`. `prep_prog_info()` sizes and overlays variable-length `bpf_prog_info` buffers for xlated/JIT dump data, ksyms, function info, and line info. `show_prog()`, `print_prog_json()`, and `print_prog_plain()` render `bpf_prog_info`, pinned paths, map ids, refs, memlock, load time, BTF id, runtime counters, and metadata variables prefixed with `bpf_metadata_`. `prog_dump()` writes raw instruction images or calls JIT disassembly and xlated dump helpers. `do_run()` wraps `bpf_prog_test_run_opts()`. `load_with_options()` handles `load` and `loadall`, map replacement by index or name, offload and XDP metadata ifindexes, custom kernel BTF, autoattach, and map/program pinning. `do_loader()` and `try_loader()` exercise libbpf's generated loader, optionally sign programs through `bpftool_prog_sign()` and add certificates through `register_session_key()`. The non-`BPFTOOL_WITHOUT_SKELETONS` block wires `profiler.skel.h` to perf events for `prog profile`.

Control flow: The show path optionally builds pinned-object and PID-reference tables, then either parses explicit program selectors or walks program ids with `bpf_prog_get_next_id()`. The dump path parses `xlated` or `jited`, gathers fds, performs a two-pass `bpf_prog_get_info_by_fd()` around `prep_prog_info()`, and sends data to raw file output, disassembler output, graph output, JSON, or plain xlated dumpers. The load path parses all options before opening the ELF, assigns program type and expected attach type per program, resolves map reuse, loads the object, mounts or creates bpffs targets, pins programs and optionally maps, and unwinds pins on failure. The profile path opens target fd, resolves its BTF function name, opens the profiler skeleton, resizes maps for selected metrics and CPUs, attaches fentry/fexit programs, sleeps or waits for SIGINT, reads per-CPU accumulators, prints, and destroys resources.

State and persistence: Persistent effects include bpffs pins for programs, maps, or autoattached links, possible bpffs directory creation/mounts, BPF program attachments, generated-loader kernel objects, session keyring additions for signed loader programs, and output files for dump/test-run data. Global state includes `prog_table`, shared `refs_table`, selected profile metrics, profiler object/fds/name, signing globals from `main.h`, and configuration flags such as `json_output`, `show_pinned`, `verifier_logs`, `relaxed_maps`, `use_loader`, and `block_mount`.

Dependencies and integration points: Depends on libbpf, kernel BPF syscalls, BTF, perf events, keyctl, OpenSSL-backed signing in `sign.c`, xlated dumping in `xlated_dumper.c`, JIT disassembly, bpftool common parsers and JSON writer, bpffs helpers, skeleton-generated `profiler.skel.h`, and kernel support for program runtime stats, line info, generated loader, BPF stream reads, or perf events depending on subcommand.

Risks: Many paths require capabilities, kernel feature availability, BTF, kallsyms visibility, mounted bpffs/tracefs, or perf permission. `get_run_data()` accepts stdin for one input only and grows buffers to `UINT32_MAX`, so large input handling relies on allocation failures. `load_with_options()` has complex unwind semantics around object load and pinning; partial pins are explicitly unpinned only after certain failures. Profile uses global state and signal cleanup, so interrupted setup before full initialization must tolerate null/negative fds. Some output depends on `kernel.kptr_restrict`, BTF presence, and libbpf section-name inference.

Test signals: Useful coverage includes `bpftool prog show/list` JSON and plain output, dump xlated/jited with and without BTF line info/opcodes/file output, load/loadall with map reuse by name and index, autoattach fallback, run with data and ctx files/stdin validation, attach/detach for supported attach types, generated loader with and without signing, and profile metric combinations including the four-metric limit and offline CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/sign.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/sign.c

Purpose: Provides OpenSSL and keyring support for signed generated-loader execution in bpftool. It reads a private key and certificate, creates a detached CMS signature over loader instructions, computes the SHA-256 program hash, and can add the certificate to the session keyring.

Important APIs, types, and functions: `display_openssl_errors()` drains OpenSSL error details. `read_private_key()` reads PEM private keys. `read_x509()` accepts DER or PEM X.509 by probing the first bytes. `register_session_key()` converts the X.509 certificate to DER and calls `add_key("asymmetric", ..., KEY_SPEC_SESSION_KEYRING)`. `bpftool_prog_sign()` builds a CMS object with `CMS_NOCERTS`, `CMS_BINARY`, `CMS_DETACHED`, `CMS_USE_KEYID`, and `CMS_NOATTR`, fills `opts->excl_prog_hash`, `opts->signature`, and `opts->signature_sz`.

Control flow: Signing starts with an in-memory BIO for `opts->insns`, loads `private_key_path` and `cert_path`, creates a partial CMS, adds one signer, finalizes over the instruction BIO, hashes the instruction bytes, DER-encodes CMS to a memory BIO, validates signature buffer capacity, copies the signature to caller storage, and frees OpenSSL objects.

State and persistence: The signing path mutates the caller's `bpf_load_and_run_opts` buffers. `register_session_key()` persists the certificate in the process session keyring. No local files are written.

Dependencies and integration points: Used by `prog.c` generated-loader path. Depends on OpenSSL EVP, BIO, X509, PEM, CMS APIs and Linux `add_key` syscall. Global `private_key_path` and `cert_path` are supplied by bpftool option parsing.

Risks: Certificate format detection is heuristic; DER is assumed from ASN.1 SEQUENCE length bytes. CMS signature length can exceed `opts->signature_sz`. The code reports OpenSSL errors only when OpenSSL has queued errors, so syscall failures rely on errno. Session key insertion requires keyring permissions and a valid asymmetric key parser in the kernel.

Test signals: Unit-style tests can feed PEM/DER certs, invalid files, undersized signature buffers, and missing private keys. Integration needs generated-loader signing with `bpftool prog load -L -S -k key -i cert` and verification that the session key is registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/sign.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/skeleton/pid_iter.bpf.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/skeleton/pid_iter.bpf.c

Purpose: BPF iterator program used by bpftool to discover processes holding BPF object file descriptors. It runs over `iter/task_file`, filters files by BPF object type, and emits `pid_iter_entry` records.

Important APIs, types, and functions: Defines local CO-RE compatible representations for perf links/events and a local link-type enum. `obj_type` is a volatile rodata selector matching bpftool object types. `get_obj_id()` reads ids from `bpf_prog`, `bpf_map`, `bpf_link`, or `btf`. `get_bpf_cookie()` extracts the perf event cookie from perf-event links. `iter()` is the iterator entrypoint and writes records with `bpf_seq_write()`.

Control flow: For each task/file pair, `iter()` rejects null entries, selects expected `file_operations` symbol for the requested object type, handles weak `bpf_link_fops_poll`, filters non-matching files, fills pid, object id, optional perf-event BPF cookie, and comm, then emits the fixed record.

State and persistence: No persistent state. Runtime state is only the current iterator context and `obj_type` configured by userspace before loading.

Dependencies and integration points: Depends on kernel BTF for CO-RE reads, ksyms for BPF file operation symbols, `pid_iter.h` record layout, and bpftool userspace reader. It integrates with bpftool PID reference reporting.

Risks: Relies on kernel internal layout and symbol availability. Weak `bpf_link_fops_poll` support covers newer kernels but missing symbols or changed link internals can suppress records. `comm` is fixed to 16 bytes.

Test signals: Load iterator for each object kind, hold BPF object fds in test processes, and confirm emitted pid/id/comm records and perf-event cookie presence for perf links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/skeleton/pid_iter.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/skeleton/pid_iter.h -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/skeleton/pid_iter.h

Purpose: Shared record layout for `pid_iter.bpf.c` and bpftool userspace. It defines the binary entry emitted by the BPF iterator.

Important APIs, types, and functions: `struct pid_iter_entry` contains BPF object id, pid, optional `bpf_cookie`, `has_bpf_cookie`, and 16-byte comm. There are no functions.

Control flow: Not applicable; this header is a data contract.

State and persistence: No state. The struct layout is serialized directly through `bpf_seq_write()`.

Dependencies and integration points: Must stay synchronized with bpftool userspace parsing and the enum/object-type comment in `pid_iter.bpf.c`. Uses kernel fixed-width types and `bool`.

Risks: Layout changes break binary iterator consumers. Padding and bool size assumptions should remain compiler/BPF ABI compatible.

Test signals: Build skeleton and run bpftool reference listing; mismatched layout would show malformed pid/id/cookie output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/skeleton/pid_iter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/skeleton/profiler.bpf.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/skeleton/profiler.bpf.c

Purpose: BPF side of `bpftool prog profile`. It attaches to a target program's fentry/fexit, reads perf event counters around each invocation, accumulates deltas per metric, and counts samples.

Important APIs, types, and functions: Defines `events` perf-event-array map, `fentry_readings`, `accum_readings`, and `counts` percpu-array maps. `num_cpu` and `num_metric` are rodata set by userspace. `fentry_XXX()` snapshots perf counters before target execution. `fexit_XXX()` reads after counters, increments sample count, and calls `fexit_update_maps()` to accumulate deltas.

Control flow: fentry looks up per-metric slots first, then reads each perf event at key `cpu + metric * num_cpu`. fexit reads all after-values before modifying maps, then updates count and accumulators if a valid before counter exists.

State and persistence: State is in BPF maps and is per-CPU. It persists only for the lifetime of the loaded profiler object and is read by `prog.c` cleanup/print logic.

Dependencies and integration points: Loaded from `profiler.skel.h` by bpftool. Depends on perf-event-array map entries populated by userspace, attach target replacement for `XXX`, and BPF helpers `bpf_perf_event_read_value()` and `bpf_get_smp_processor_id()`.

Risks: Hard limit `MAX_NUM_METRICS` is 4. Missing fentry readings suppress accumulation. Perf event read errors abort each probe invocation. Counter deltas can be affected by multiplexing, shown through enabled/running in userspace.

Test signals: Profile a BPF program with one to four selected metrics, verify counts increase, accumulators are nonzero, and offline CPU handling is managed by userspace map setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/skeleton/profiler.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/struct_ops.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/struct_ops.c

Purpose: Implements `bpftool struct_ops` subcommands for listing, dumping, registering, and unregistering BPF struct_ops maps.

Important APIs, types, and functions: `get_btf_vmlinux()` loads kernel BTF. `get_map_info_type_id()` finds BTF for `struct bpf_map_info` and sizes allocations to the running kernel's layout. `get_next_struct_ops_map()` iterates map ids and filters `BPF_MAP_TYPE_STRUCT_OPS`. `do_search()`, `do_one_id()`, and `do_work_on_struct_ops()` centralize selection by name/id/all. `__do_show()`, `__do_dump()`, and `__do_unregister()` perform per-map work. `do_register()` opens an object, loads it, attaches every struct_ops map with `bpf_map__attach_struct_ops()`, optionally pins BPF links, and reports map/link ids.

Control flow: Show/dump parse optional `id` or `name`, iterate selected struct_ops maps, and render either short metadata or BTF-dumped map info and value. Unregister requires a selector and deletes key zero from the map. Register loads an ELF, iterates maps, attaches struct_ops maps, obtains map/link info, optionally pins links under a bpffs directory, disconnects links so kernel state remains registered, and fails if no struct_ops maps exist.

State and persistence: Register can persist struct_ops state in the kernel and optionally pinned links in bpffs. Unregister removes the map element at key zero to unload. Static globals cache `btf_vmlinux`, `map_info_type`, allocation length, and type id for the command lifetime.

Dependencies and integration points: Depends on kernel BTF, libbpf struct_ops APIs, bpffs helpers, bpftool JSON/BTF dumper, BPF map/link syscalls, and `BPF_F_LINK` map flag semantics.

Risks: Requires `CONFIG_DEBUG_INFO_BTF`; without it most operations fail. Running-kernel `bpf_map_info` layout is handled via BTF allocation, but older kernels or missing fields can still affect dump fidelity. Register can partially attach maps while others fail, returning error after reporting successes.

Test signals: Exercise show/list all, show by name/id, dump JSON/plain, register object with and without `BPF_F_LINK`, link pinning, unregister by id/name, and kernels lacking BTF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/struct_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/token.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/token.c

Purpose: Implements `bpftool token show/list`, reporting bpffs mounts configured with delegation token options.

Important APIs, types, and functions: `sets[]` maps display headers to mount option keys. `has_delegate_options()` detects any delegate option. `get_delegate_value()` tokenizes comma-separated mount options and returns the value for one key. `print_items_per_line()` and `split_json_array_str()` format colon-separated option values. `show_token_info_plain()` and `show_token_info_json()` render one mount. `show_token_info()` scans `/proc/mounts`.

Control flow: The command opens `/proc/mounts`, optionally starts a JSON array, visits each mount entry with type prefix `bpf`, filters entries with delegation options, prints all four configured sets, ends JSON, and closes the mount table.

State and persistence: Read-only. It duplicates mount option strings because `strtok_r()` mutates them.

Dependencies and integration points: Depends on bpffs mount options `delegate_cmds`, `delegate_maps`, `delegate_progs`, and `delegate_attachs`, libc mount table APIs, and bpftool JSON globals.

Risks: Type check uses `strncmp(ent->mnt_type, "bpf", 3)`, so any mount type beginning with `bpf` is considered. Token parsing is simple string splitting and assumes colon-separated values with no escaping. Missing delegate key prints empty list/header.

Test signals: Mount bpffs with different delegation options and verify plain alignment and JSON arrays, plus empty output when no delegate options exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/token.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/tracelog.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/tracelog.c

Purpose: Implements legacy `bpftool prog tracelog` tailing of tracefs `trace_pipe`, used to view BPF trace output.

Important APIs, types, and functions: `validate_tracefs_mnt()` confirms filesystem magic. `get_tracefs_pipe()` checks known tracefs locations, scans `/proc/mounts`, and optionally mounts tracefs. `exit_tracelog()` closes resources and closes JSON output on signals. `do_tracelog()` opens the pipe, installs signal handlers, and loops on `getline()`.

Control flow: JSON mode starts an array before locating tracefs. The tool tries `/sys/kernel/tracing` and `/sys/kernel/debug/tracing`, then `/proc/mounts`, then mounts tracefs unless `block_mount` is set. It reads each line forever and prints either strings in JSON or raw text.

State and persistence: Holds global `trace_pipe_fd` and `buff` for signal cleanup. It may mount tracefs, which persists after command exit.

Dependencies and integration points: Used by `prog.c` when no stdout/stderr stream mode is requested. Depends on tracefs, bpftool mount helper, Linux magic constants, JSON writer, and signal delivery.

Risks: Long-running process by design. If JSON mode returns early before a signal, the array may not be closed on ordinary error paths. Automatic mounting can fail due to permissions or `block_mount`. Trace output can be high volume and unbounded.

Test signals: Run with existing tracefs, with tracefs absent and mount allowed/blocked, plain and JSON modes, and signal interruption to confirm cleanup and JSON closure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/tracelog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/xlated_dumper.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/xlated_dumper.c

Purpose: Formats translated BPF instructions for bpftool dump output in plain text, JSON, and DOT graph labels, with helper/subprogram/map immediate annotation and optional BTF line/function info.

Important APIs, types, and functions: `kernel_syms_load()`, `kernel_syms_destroy()`, and `kernel_syms_search()` manage `/proc/kallsyms` lookup. `print_call()` resolves helper and pseudo-call targets. `print_imm()` annotates map fd/value/index and pseudo-function immediates. `dump_xlated_json()`, `dump_xlated_plain()`, and `dump_xlated_for_graph()` iterate `struct bpf_insn` arrays and call `print_bpf_insn()` with callbacks.

Control flow: Kallsyms load reads symbols, records `__bpf_call_base`, rejects restricted zero addresses, and sorts by address. Dump functions skip the second half of double-wide `BPF_LD | BPF_IMM | BPF_DW` instructions, emit function prototypes when `func_info` offsets match, emit line info via `bpf_prog_linfo__lfind()`, print disassembly, and optionally print raw opcodes.

State and persistence: State is contained in `struct dump_data`; `scratch_buff` is reused by callbacks. No persistence.

Dependencies and integration points: Called from `prog.c` dump and loader debug paths and from CFG visual code. Depends on libbpf disassembler callbacks, BTF dumper helpers, bpftool JSON writer, and `/proc/kallsyms` visibility.

Risks: `kernel_syms_cmp()` subtracts unsigned long addresses into int, which follows existing code but can be sensitive to large deltas. Graph escaping uses fixed 64-byte buffer and truncates long instruction strings. Kallsyms restrictions reduce helper and subprogram annotation quality.

Test signals: Dump xlated instructions with helpers, map immediates, pseudo-calls, double-wide loads, BTF function/line info, JSON opcodes, and DOT graph output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/xlated_dumper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/xlated_dumper.h -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/xlated_dumper.h

Purpose: Declares data structures and dump function prototypes used by bpftool translated-instruction dumpers.

Important APIs, types, and functions: `struct kernel_sym` stores address, name, and module. `struct dump_data` carries kallsyms, JIT ksym array, BTF, function info, line info, and scratch buffer. Function declarations cover symbol loading/search/destruction and JSON/plain/graph xlated dumping.

Control flow: Not applicable in the header, but callers initialize `dump_data`, optionally load symbols, and pass instruction buffers to one of the dump functions.

State and persistence: No static state. The caller owns `dump_data` lifecycle and must call `kernel_syms_destroy()` after `kernel_syms_load()`.

Dependencies and integration points: Included by `prog.c`, `xlated_dumper.c`, and CFG dumping code. References `struct bpf_prog_linfo`, `struct btf`, and bpftool/libbpf types through included compilation units.

Risks: Header layout is a cross-file ABI inside bpftool; changes to `dump_data` require all dump users to initialize new fields. Scratch buffer size constrains symbol/immediate rendering.

Test signals: Compile bpftool and run all xlated dump modes; missing initialization usually appears as bad symbol names or null BTF/line output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/xlated_dumper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/resolve_btfids/Makefile -->
# sources/distributed-fs/ceph-client/tools/bpf/resolve_btfids/Makefile

Purpose: Builds the host-side `resolve_btfids` tool and its private libbpf/libsubcmd dependencies in the kernel tools build environment.

Important APIs, types, and functions: Defines `srctree`, `OUTPUT`, host tool variables, `HOST_OVERRIDES`, `BPFOBJ`, `SUBCMDOBJ`, `BINARY`, and `BINARY_IN`. Targets include `all`, `prepare`, libsubcmd/libbpf builds, object build through `tools/build/Makefile.include`, final link, `clean`, and `tags`.

Control flow: `all` builds `$(BINARY)`. `prepare` builds dependency archives and installs headers into output-local include directories. `$(BINARY_IN)` invokes the tools build system for `resolve_btfids`. Final link uses `HOSTCC`, `KBUILD_HOSTLDFLAGS`, optional `EXTRA_LDFLAGS`, libbpf, libsubcmd, libelf, and zlib.

State and persistence: Writes generated objects, static archives, installed headers, and binary under `OUTPUT`, defaulting to `tools/bpf/resolve_btfids/`. `clean` removes these outputs.

Dependencies and integration points: Integrates with `tools/scripts/Makefile.include`, `Makefile.arch`, `tools/build`, `tools/lib/bpf`, and `tools/lib/subcmd`. Uses `pkg-config` for libelf/zlib flags with fallbacks.

Risks: Static libelf fallback includes `-lzstd`, which assumes availability. Host/cross overrides intentionally clear target cross flags; incorrect environment can still mix host and target flags. `clean_objects` is computed at parse time, so stale outputs created after parse are handled by wildcard expansion only on invocation.

Test signals: `make -C tools/bpf/resolve_btfids`, static and dynamic libelf builds, `OUTPUT=` out-of-tree builds, `V=1`, and `make clean`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/resolve_btfids/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/resolve_btfids/main.c -->
# sources/distributed-fs/ceph-client/tools/bpf/resolve_btfids/main.c

Purpose: Host utility that resolves `__BTF_ID__*` symbols in an ELF `.BTF_ids` section to numeric BTF type ids, emits raw `.BTF`, `.BTF_ids`, and optional `.BTF.base` blobs, transforms kfunc BTF for implicit arguments, and can patch a `.BTF_ids` blob back into an ELF.

Important APIs, types, and functions: `struct object` carries ELF, BTF, base BTF, rb-trees of unresolved ids, counters, and options. `struct btf_id` tracks one requested symbol/set and all ELF addresses that need patching. `elf_collect()` opens ELF and finds symbol and `.BTF_ids` sections, endian-swapping `.BTF_ids` if needed. `symbols_collect()` parses `__BTF_ID__{struct,union,typedef,func,set,set8}__...` symbols. `load_btf()`, `symbols_resolve()`, `symbols_patch()`, `sets_patch()`, and `dump_raw_*()` implement the core resolve-and-dump flow. `btf2btf()` and helpers detect `bpf_kfunc` decl tags, find kfunc flags from set8 entries, and rewrite BTF for `KF_IMPLICIT_ARGS`. `finalize_btf()` optionally distills base BTF and sorts types by name. `patch_btfids()` updates an ELF `.BTF_ids` section from a blob. `main()` parses options and sequences the work.

Control flow: Normal mode initializes rb-trees, parses options, collects ELF sections, marks BTF-id resolution optional when `.BTF_ids` or symbols are absent, collects symbols, loads BTF or split BTF, performs kfunc BTF transformations, finalizes/sorts BTF, resolves collected symbols by scanning all BTF types, patches all ids and set counts/sorting into `.BTF_ids`, dumps `<elf>.BTF_ids`, dumps `<elf>.BTF`, and optionally dumps `<elf>.BTF.base`. `--patch_btfids` bypasses resolution and validates file size before replacing the ELF section and writing the ELF.

State and persistence: Mutates in-memory ELF `.BTF_ids` data and writes sidecar raw files named by appending `.BTF_ids`, `.BTF`, and `.BTF.base` to the ELF path. Patch mode writes the ELF itself. It maintains warning count and can make warnings fatal. All rb-tree allocations and BTF/ELF handles are freed at exit.

Dependencies and integration points: Used by kernel build/link flows that need BTF ID tables. Depends on libelf/GELF, libbpf BTF APIs, Linux rb-tree/zalloc helpers, `linux/btf_ids.h`, `linux/kallsyms.h`, and subcmd parse-options. It understands the macro-generated symbol names emitted by kernel BTF_ID declarations.

Risks: Symbol parsing is strict and assumes `__BTF_ID__...__N` suffix format. `ADDR_CNT` limits repeated symbol addresses to 100. Duplicate BTF names produce warnings and keep the first id. Unresolved non-set symbols patch zero and warn. Endian swapping must occur exactly before dump for cross-endian targets. Kfunc implicit-arg transformation mutates BTF type graphs and must preserve decl tags and prototypes. Patch mode fails on size mismatch but writes in-place on success.

Test signals: Build-time tests should include objects with all supported BTF id kinds, set and set8 sorting, duplicate names, unresolved symbols with and without `--fatal_warnings`, split BTF with `--btf_base`, `--distill_base`, cross-endian `.BTF_ids`, `KF_IMPLICIT_ARGS` kfuncs, and `--patch_btfids` size mismatch/success cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/resolve_btfids/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/certs/print-cert-tbs-hash.sh -->
# sources/distributed-fs/ceph-client/tools/certs/print-cert-tbs-hash.sh

Purpose: Computes the Linux blacklist key description for a certificate by hashing the TBSCertificate region with the certificate signature hash algorithm and printing `tbs:<hash>` without a newline.

Important APIs, types, and functions: Shell variables capture certificate path, ASN.1 offset/length/digest, and selected digest command. Uses `openssl x509`, `openssl asn1parse`, `openssl list -digest-commands`, `dd`, `openssl dgst`, `sed`, and `awk`.

Control flow: Validates one file argument, converts DER or PEM input to normalized PEM, parses line 2 for TBSCertificate offset/length and line 7 for signature digest OID name, matches the digest against OpenSSL digest commands, converts the cert to DER, extracts the TBS byte range with `dd`, hashes it, and prints the prefixed digest.

State and persistence: Read-only; intended output is redirected by the caller for later PKCS#7 signing and keyctl loading.

Dependencies and integration points: Integrates with Linux asymmetric key blacklist workflow and references kernel X.509 parser behavior. Requires OpenSSL command-line tools and POSIX shell utilities.

Risks: ASN.1 parsing assumes specific OpenSSL output line positions. `dd count` is set to `OFFSET + length` while also using `skip=OFFSET`, so this mirrors current script behavior but is a subtle area to verify against expected byte counts. Digest matching depends on OpenSSL command names containing the signature digest text.

Test signals: Run on PEM and DER certificates with SHA-256/SHA-1 signatures, invalid files, and compare against kernel-generated blacklist descriptions where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/certs/print-cert-tbs-hash.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/cgroup/iocost_coef_gen.py -->
# sources/distributed-fs/ceph-client/tools/cgroup/iocost_coef_gen.py

Purpose: Generates blk-iocost linear cost model coefficients by running destructive or file-backed fio benchmarks and printing a line suitable for `/sys/fs/cgroup/io.cost.model`.

Important APIs, types, and functions: `dir_to_dev()` maps a path to whole block device and major:minor. `create_testfile()` creates a direct-IO test file, attempts `chattr +C`, and fills it from `/dev/urandom` through `pv` and `dd`. `run_fio()` runs fio with JSON output and returns aggregate bandwidth. `restore_elevator_nomerges()` restores scheduler and merge settings.

Control flow: Parses benchmark parameters, validates required commands, chooses raw block device or file target, records current scheduler and `nomerges`, disables scheduler/merges, runs six fio workloads for sequential bandwidth and 4K sequential/random IOPS in read/write directions, restores settings, and prints `MAJ:MIN rbps=...`.

State and persistence: Can write a large test file in the current directory. It writes `/sys/block/<dev>/queue/scheduler` and `nomerges` and registers an `atexit` restoration handler. Raw `--testdev` writes to the whole device and is destructive.

Dependencies and integration points: Requires fio, findmnt, pv, dd, sysfs block queue controls, and root-level permissions for raw devices/sysfs. Output integrates with cgroup v2 io.cost.model.

Risks: Shell command construction uses paths directly and assumes trusted arguments. Raw device mode can destroy data. If the process is killed with SIGKILL, scheduler/nomerges may not restore. The fio JSON parser assumes job read/write keys and bandwidth fields exist.

Test signals: Use a loop device or disposable block device, short durations, quiet/verbose modes, missing command detection, existing correctly-sized testfile reuse, and restoration after exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/cgroup/iocost_coef_gen.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/cgroup/iocost_monitor.py -->
# sources/distributed-fs/ceph-client/tools/cgroup/iocost_monitor.py

Purpose: drgn-based monitor for blk-iocost controller state and per-cgroup IO cost statistics.

Important APIs, types, and functions: `BlkgIterator` recursively walks blkcg hierarchy and resolves `struct blkcg_gq` by queue id. `IocStat` snapshots controller-global fields such as period, vtime rates, busy level, and auto parameters. `IocgStat` snapshots per-cgroup weights, hweights, inflight, usage, wait, debt, delay, and address. Main code locates the target queue/iocg through `blkcg_root.blkg_tree`.

Control flow: Parses target device, optional cgroup regex, interval, and JSON flag; validates kernel iocost symbols; resolves constants; finds the requested device's queue id and root `ioc`; exits early for interval 0; otherwise loops, builds global and per-cgroup output, filters inactive or regex-mismatched groups, prints table or JSON lines, flushes, and sleeps.

State and persistence: Read-only against live kernel memory. Maintains local filter and interval state. No files are written.

Dependencies and integration points: Requires drgn, kernel debug info/symbols, blk-cgroup and iocost enabled, and access to live kernel memory. Integrates with block controller internals rather than stable UAPI.

Risks: Kernel structure changes can break field access. Broad exception handling while locating queues may hide unexpected errors. Table path truncates cgroup names from the left. JSON mode emits one JSON object per line rather than a single array.

Test signals: Run on kernels with and without iocost, valid and invalid device names, `--interval 0`, table and JSON modes, cgroup filtering, and inactive group omission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/cgroup/iocost_monitor.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/cgroup/memcg_shrinker.py -->
# sources/distributed-fs/ceph-client/tools/cgroup/memcg_shrinker.py

Purpose: Reports the largest per-memcg shrinker counts by correlating debugfs shrinker entries with cgroup inode numbers.

Important APIs, types, and functions: `scan_cgroups()` walks `/sys/fs/cgroup/` and maps inode to path. `scan_shrinkers()` walks `/sys/kernel/debug/shrinker/`, reads each `count` file, and records count, shrinker name, and memcg inode. `main()` sorts and prints nonzero entries with optional line limit.

Control flow: Parse `--lines`, build cgroup map, collect shrinker counts, sort descending by count, map inode 0/1 to root, map unknown inodes to `unknown (<ino>)`, print until zero count or limit.

State and persistence: Read-only. No persistent state.

Dependencies and integration points: Depends on cgroup filesystem and shrinker debugfs layout. Intended for kernel memory reclaim diagnostics.

Risks: Assumes count file lines split into inode and count. Permission or missing debugfs will raise exceptions. Inode-to-path mapping may race with cgroup creation/removal.

Test signals: Run with debugfs mounted, `-n` limits, no shrinker entries, and cgroups removed while scanning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/cgroup/memcg_shrinker.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/cgroup/memcg_slabinfo.py -->
# sources/distributed-fs/ceph-client/tools/cgroup/memcg_slabinfo.py

Purpose: drgn script that prints slab cache statistics for a memory cgroup and can emulate cgroup v1 `memory.kmem.slabinfo` behavior.

Important APIs, types, and functions: `find_memcg_ids()` maps cgroup ids to `struct mem_cgroup`. `detect_kernel_config()` detects SLUB/SLAB and shared slab page support. `slub_get_slabinfo()` aggregates node slab counters and partial free objects. `for_each_slab()` scans pages for slab folios. `cache_show()` prints slabinfo-format rows.

Control flow: Parses target cgroup path, resolves its inode to a memcg, detects allocator config, prints header, then either scans all slab pages and object cgroup vectors for shared slab pages or iterates the memcg's `kmem_caches` list for older per-memcg caches.

State and persistence: Read-only against live kernel memory. Uses global `MEMCGS` mapping.

Dependencies and integration points: Requires drgn, kernel symbols/debug info, cgroup memory controller, SLUB support, and kernel layouts for slab, obj_cgroup, mem_cgroup, and kmem_cache.

Risks: SLAB allocator is detected but not supported. Whole-memory page scanning can be expensive. Structure layout and page type constants are kernel-version sensitive. Faults while scanning pages are ignored only in `for_each_slab()`.

Test signals: Run against root and non-root cgroups on shared-slab and older kernels, verify output resembles slabinfo, and confirm graceful error on unsupported allocator or unknown cgroup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/cgroup/memcg_slabinfo.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/counter/Makefile -->
# sources/distributed-fs/ceph-client/tools/counter/Makefile

Purpose: Builds and installs userspace counter examples `counter_example` and `counter_watch_events`.

Important APIs, types, and functions: Defines `ALL_TARGETS`, `ALL_PROGRAMS`, CFLAGS with generated include directory and kernel tools include, `prepare` symlink for `linux/counter.h`, per-target object and link rules, `clean`, and `install`.

Control flow: `all` depends on output programs. `prepare` creates `$(OUTPUT)include/linux/counter.h` symlink from kernel UAPI. Each object invokes `tools/build`, then links with `$(CC)`. Install copies programs to `$(DESTDIR)$(bindir)`.

State and persistence: Creates output binaries, object files, generated dependency files, and a symlinked UAPI header under `$(OUTPUT)include`.

Dependencies and integration points: Uses kernel tools build system and UAPI `include/uapi/linux/counter.h`. Intended for in-tree and out-of-tree tools builds.

Risks: Header symlink assumes relative path from tools/counter. Clean removes `$(OUTPUT)include` and object/dependency files. Build depends on `OUTPUT` semantics from tools environment.

Test signals: `make`, `make OUTPUT=/tmp/...`, `make install DESTDIR=...`, and `make clean`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/counter/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/counter/counter_example.c -->
# sources/distributed-fs/ceph-client/tools/counter/counter_example.c

Purpose: Minimal userspace example for the Linux Counter character device API. It watches count values on `/dev/counter0` and prints event data indefinitely.

Important APIs, types, and functions: Static `watches[2]` configures two `struct counter_watch` entries for Count 0 and Count 1, scope count, event index, channel 0. `main()` opens the device, adds watches with `COUNTER_ADD_WATCH_IOCTL`, enables events with `COUNTER_ENABLE_EVENTS_IOCTL`, reads two `struct counter_event` records at a time, and prints timestamps, values, and status strings.

Control flow: Open, add both watches, enable events, then infinite blocking read loop. Any ioctl/read/short-read error exits.

State and persistence: Configures watches and event enablement on the open counter fd. No file persistence.

Dependencies and integration points: Depends on `/dev/counter0` and UAPI `linux/counter.h`. Demonstrates the counter character device event API for driver developers.

Risks: Hardcoded device, event type, component parents, and assumption that reads return exactly two events. It leaks the fd on early ioctl error by process exit only.

Test signals: Run on a counter device supporting index events for two counts, inject events, verify read sizes and status handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/counter/counter_example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/counter/counter_watch_events.c -->
# sources/distributed-fs/ceph-client/tools/counter/counter_watch_events.c

Purpose: Flexible test utility for configuring one or more Counter API watches from command-line suboptions and reading matching event records.

Important APIs, types, and functions: Name arrays map event/component/scope enum values to strings. `print_watch()` dumps configured watches. `print_usage()` documents CLI. `counter_watch_subopts[]` maps `getsubopt()` tokens to enum-like indices. `main()` does a first option pass to count watches and parse common options, a second pass to fill `struct counter_watch` entries, then opens `/dev/counterN`, adds watches, enables events, and reads events.

Control flow: If no `-w` is provided, uses `simple_watch`. Otherwise allocates one watch per `-w`, parses comma-separated scope/component/event/channel/id/parent tokens, optionally prints debug, opens the target device, adds all watches, enables events, reads until `--loop` count or forever, prints timestamp/value/event/channel, and reports per-event status errors.

State and persistence: Configures watches and event enablement on a device fd. Allocates dynamic watch array when needed.

Dependencies and integration points: Depends on Counter UAPI and `/dev/counterN`. Integrates with kernel counter drivers for exercising event coverage.

Risks: `errno` is not reset before `strtoul()`/`strtol()` conversions, so prior errno can cause false failures. Name arrays are indexed by kernel enum values and need updates if UAPI changes. Unknown suboption error prints `value`, which may be null for flag-style unknown tokens.

Test signals: Parse all suboptions, invalid numeric values, no-watch default, multiple watches, finite loop count, debug output, unsupported watches, and short read behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/counter/counter_watch_events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/crypto/ccp/Makefile -->
# sources/distributed-fs/ceph-client/tools/crypto/ccp/Makefile

Purpose: Builds the AMD Dynamic Boost Control C shim as `dbc_library.so` for Python ctypes clients.

Important APIs, types, and functions: Sets UAPI include flags, target name, `all`, shared library rule from `dbc.c`, removes executable bit, and `clean`.

Control flow: `make` compiles `dbc.c` with `$(CC) $(CFLAGS) $(LDFLAGS) -shared` to `dbc_library.so` and `chmod -x` on the result.

State and persistence: Creates `dbc_library.so` in the current directory.

Dependencies and integration points: Depends on `include/uapi/linux/psp-dbc.h` and is loaded by `dbc.py` via `ctypes.CDLL("./dbc_library.so")`.

Risks: Does not pass `-fPIC`; platform/toolchain defaults determine whether shared build succeeds. Relative library location must match Python working directory.

Test signals: `make`, import `dbc.py` from the same directory, and `make clean`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/crypto/ccp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/crypto/ccp/dbc.c -->
# sources/distributed-fs/ceph-client/tools/crypto/ccp/dbc.c

Purpose: Small C library wrapping AMD Secure Processor Dynamic Boost Control ioctls for Python ctypes.

Important APIs, types, and functions: `get_nonce()` wraps `DBCIOCNONCE`, optionally copying a signature and returning nonce bytes. `set_uid()` wraps `DBCIOCUID`. `process_param()` wraps `DBCIOCPARAM`, passes message index/signature/parameter, then returns updated parameter and signature.

Control flow: Each function asserts required pointers, populates the corresponding UAPI struct, invokes ioctl, returns `errno` on failure or 0 on success, and copies output fields back to caller buffers.

State and persistence: Mutates device state through `/dev/dbc` ioctls. No local persistence.

Dependencies and integration points: Depends on `linux/psp-dbc.h` and is consumed by `dbc.py`. Integrates with AMD PSP DBC kernel driver.

Risks: `assert()` checks disappear under `NDEBUG`, so invalid null pointers could crash. Return value is positive errno, matching Python wrapper expectations but not typical negative errno convention. `process_param()` initializes `param` from `*data`, so caller must always pass a valid data pointer.

Test signals: ctypes calls against supported `/dev/dbc`, invalid signatures, invalid ioctl payload tests in `test_dbc.py`, and no-device handling at Python layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/crypto/ccp/dbc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/crypto/ccp/dbc.py -->
# sources/distributed-fs/ceph-client/tools/crypto/ccp/dbc.py

Purpose: Python ctypes wrapper for `dbc_library.so`, exposing Dynamic Boost Control nonce, UID, and parameter operations.

Important APIs, types, and functions: Constants define UID, nonce, signature sizes, message tuples, and default device path. `handle_error()` raises `OSError`. `get_nonce()`, `set_uid()`, and `process_param()` validate arguments, allocate ctypes buffers, call C functions, translate nonzero return codes, and return Python values.

Control flow: Import-time loads `./dbc_library.so`. Each API validates required device/signature/message, calls a C wrapper with `device.fileno()`, and converts outputs to bytes/int tuples.

State and persistence: No Python persistence, but operations mutate `/dev/dbc` driver state. Import depends on current working directory.

Dependencies and integration points: Used by `dbc_cli.py` and `test_dbc.py`. Depends on ctypes, os, the local shared library, and the kernel DBC device.

Risks: Message constants are one-element tuples; `process_param()` rejects bare ints. `get_nonce()` rejects missing device but allows unauthenticated signature `None`. `ctypes.create_string_buffer(signature, len(signature))` omits a null terminator intentionally but relies on exact signature size. Relative library loading is fragile.

Test signals: Import from tool directory, call wrappers with missing args, invalid message type, invalid signatures, and live `/dev/dbc` operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/crypto/ccp/dbc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/crypto/ccp/dbc_cli.py -->
# sources/distributed-fs/ceph-client/tools/crypto/ccp/dbc_cli.py

Purpose: Command-line interface for Dynamic Boost Control operations through `dbc.py`.

Important APIs, types, and functions: `ERRORS` maps errno values to user-friendly messages. `messages` maps command message names to DBC tuples. `_pretty_buffer()` hex-formats bytes. `parse_args()` declares `get-nonce`, `get-param`, `set-param`, and `set-uid`. `pretty_error()` prints known errno text.

Control flow: Parses arguments, validates device existence, reads optional signature and UID files with exact length checks, parses decimal or hex data, opens the device, dispatches command, validates get/set message direction, calls wrapper functions, and prints nonce/parameter/signature or friendly errors.

State and persistence: Mutates DBC device state for set UID and set parameter. Reads signature/UID files. No local writes.

Dependencies and integration points: Depends on `dbc.py`, local shared library, `/dev/dbc`, and Python standard modules. Intended as a user tool for AMD PSP DBC.

Risks: Opening device with text mode `open(args.device)` is adequate for fd use but not explicit binary/read-write. Some required combinations, such as missing signature for set-param, are left for wrapper errors. `_pretty_buffer()` returns Python bytes repr text, not a bare hex string.

Test signals: CLI argument validation, invalid file lengths, get/set message mismatch, missing device, and expected errno translations on secured/unfused systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/crypto/ccp/dbc_cli.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/crypto/ccp/test_dbc.py -->
# sources/distributed-fs/ceph-client/tools/crypto/ccp/test_dbc.py

Purpose: unittest suite for AMD DBC userspace wrappers and kernel ioctl behavior across unsupported, secured, and unfused systems.

Important APIs, types, and functions: `system_is_secured()` reads CCP `fused_part`. `DynamicBoostControlTest` opens/closes `DEVICE_NODE` and supplies dummy signature/UID. Test classes cover unsupported systems, invalid ioctl structs via `ioctl_opt`, invalid signatures on fused systems, and valid/unfused parameter operations.

Control flow: Tests skip based on device existence, ioctl_opt availability, and fused state. Invalid ioctl tests construct bad ioctl numbers/structures and expect `EINVAL`. Secured tests expect unauthenticated nonce success but authenticated operations with dummy signatures to fail. Unfused tests establish identity, read ranges, set and restore fmax/power caps, and expect graphics mode to be unimplemented.

State and persistence: Mutates DBC device state for UID and power/fmax caps, attempting to restore original values. Adds delays between set commands. Reads sysfs fused state.

Dependencies and integration points: Depends on `dbc.py`, optional `ioctl_opt`, `/dev/dbc`, CCP PCI sysfs, and live hardware/firmware behavior.

Risks: `glob(...)[0]` in `system_is_secured()` can raise if no CCP path exists. Set tests alter hardware limits and rely on restoration paths. Dummy signatures and errno expectations are firmware/kernel behavior dependent.

Test signals: Running the suite itself is the signal, with skip accounting for unsupported systems. Hardware-backed CI would need isolated unfused/fused platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/crypto/ccp/test_dbc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/crypto/tcrypt/tcrypt_speed_compare.py -->
# sources/distributed-fs/ceph-client/tools/crypto/tcrypt/tcrypt_speed_compare.py

Purpose: Parses two kernel `tcrypt` speed-test dmesg logs and prints per-algorithm/per-operation performance differences.

Important APIs, types, and functions: `parse_title()` extracts algorithm and encryption/decryption operation. `parse_item()` parses either operations-per-duration or cycles-per-operation lines. `parse()` builds nested `alg -> op -> list` data. `merge()` pairs base and new entries. `format()` prints tables and average/total differences. `main()` drives parse/merge/format.

Control flow: CLI expects base and new log paths. Each file is scanned linearly, setting current alg/op on title lines and appending parsed result items. Merge assumes identical algorithm/op/item ordering in both logs. Format calculates percentage differences row-by-row.

State and persistence: Read-only log parsing; writes report to stdout.

Dependencies and integration points: Intended for logs produced by kernel crypto `tcrypt` module. Uses Python regex and sys only.

Risks: No validation for missing algorithms, reordered rows, zero base values, or mismatched operation/cycle modes. `ops_total_speed_up` formula uses `(base_sum - new_sum) * 100 / base_sum`, which has opposite sign from row-level `(new - base)` for operations.

Test signals: Compare known operation logs, cycle logs, mismatched logs, and check sign conventions for improvements/regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/crypto/tcrypt/tcrypt_speed_compare.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/debugging/Makefile -->
# sources/distributed-fs/ceph-client/tools/debugging/Makefile

Purpose: Installs the shell debugging utility `kernel-chktaint`.

Important APIs, types, and functions: Defines `PREFIX`, `BINDIR`, `INSTALL`, `TARGET`, `all`, empty `clean`, and `install`.

Control flow: `all` depends on the script target. `install` copies it executable to `$(DESTDIR)$(PREFIX)/$(BINDIR)/kernel-chktaint`.

State and persistence: Install writes one executable file to the destination.

Dependencies and integration points: Part of kernel tools install flow. Uses standard `install`.

Risks: `clean` intentionally does nothing because the target is source. Build rule relies on the existing script file.

Test signals: `make install DESTDIR=...` and verifying mode/path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/debugging/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/debugging/kernel-chktaint -->
# sources/distributed-fs/ceph-client/tools/debugging/kernel-chktaint

Purpose: Decodes the Linux kernel taint bitmask from `/proc/sys/kernel/tainted` or a supplied integer, printing reasons, the taint string, and tainted modules.

Important APIs, types, and functions: Shell `usage()` prints help. `addout()` appends one-character taint flags to `out`. The main body shifts through taint bits 0 through 19 and prints descriptions for set bits.

Control flow: Validates optional integer/help argument, reads `/proc/sys/kernel/tainted` when no argument, exits early for zero, repeatedly tests `T % 2`, appends the corresponding flag or space, divides `T` by 2, prints raw value/string, optionally scans `/sys/module/*/taint`, and prints documentation pointers.

State and persistence: Read-only. No persistent state.

Dependencies and integration points: Uses `/proc/sys/kernel/tainted`, `/sys/module`, and standard shell utilities. Aligns with Linux tainted-kernels documentation.

Risks: Script declares `/bin/sh` but uses `==`, which is not POSIX in all shells. Numeric tests and unquoted variables are mostly controlled but still shell-sensitive. Bit descriptions must track kernel taint flag additions.

Test signals: Run with `0`, known integer masks, invalid input, no argument on a live kernel, and under different `/bin/sh` implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/debugging/kernel-chktaint -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/dma/Makefile -->
# sources/distributed-fs/ceph-client/tools/dma/Makefile

Purpose: Builds and installs `dma_map_benchmark`, a userspace frontend for the kernel DMA map benchmark debugfs interface.

Important APIs, types, and functions: Defines `srctree`, `CFLAGS`, `ALL_TARGETS`, `prepare` symlink for `linux/map_benchmark.h`, direct compile rule for `dma_map_benchmark`, `clean`, and `install`.

Control flow: `all` builds the program. `prepare` creates `$(OUTPUT)include/linux/map_benchmark.h` symlink from UAPI. The target compiles `dma_map_benchmark.c` directly. Install copies built programs to `bindir`.

State and persistence: Creates binary, output include symlink, and build artifacts; install writes destination binary.

Dependencies and integration points: Uses tools build include, UAPI `linux/map_benchmark.h`, and supports both tools and selftests build contexts.

Risks: Compile rule targets `dma_map_benchmark` in the current directory rather than `$(OUTPUT)dma_map_benchmark`, while `ALL_PROGRAMS` uses `$(OUTPUT)%`; this is existing behavior to watch in out-of-tree builds. Clean removes output include and generated files.

Test signals: In-tree make, `OUTPUT=` builds, selftests environment with `srctree=.`, install, and clean.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/dma/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/dma/config -->
# sources/distributed-fs/ceph-client/tools/dma/config

Purpose: Kconfig fragment enabling the kernel DMA map benchmark support required by the userspace tool.

Important APIs, types, and functions: Contains `CONFIG_DMA_MAP_BENCHMARK=y`.

Control flow: Not executable; consumed as configuration input.

State and persistence: Sets a build-time kernel config option when merged into a kernel configuration.

Dependencies and integration points: Pairs with `dma_map_benchmark.c` and the kernel debugfs benchmark interface.

Risks: Enabling benchmark code may expose debug/test interfaces and should be restricted to test kernels.

Test signals: Merge config, build kernel, confirm `/sys/kernel/debug/dma_map_benchmark` exists with debugfs mounted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/dma/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/dma/dma_map_benchmark.c -->
# sources/distributed-fs/ceph-client/tools/dma/dma_map_benchmark.c

Purpose: Userspace CLI for the kernel DMA mapping benchmark debugfs ioctl.

Important APIs, types, and functions: `main()` parses options for threads, seconds, NUMA node, DMA mask bits, direction, transmit delay, granule, and mode; validates against UAPI limits; fills `struct map_benchmark`; opens `/sys/kernel/debug/dma_map_benchmark`; invokes `DMA_MAP_BENCHMARK`; and prints average/stddev map and unmap latencies.

Control flow: Defaults to single thread, 20 seconds, NUMA no node, 32-bit bidirectional single mode, granule 1. Invalid mode/thread/seconds/delay/bits/direction/granule exits. Successful ioctl prints mode, parameters, and latency metrics in microseconds.

State and persistence: Read/write interaction with debugfs benchmark endpoint; no local persistence.

Dependencies and integration points: Requires kernel built with `CONFIG_DMA_MAP_BENCHMARK`, debugfs mounted, UAPI `linux/map_benchmark.h`, and permission to open the debugfs file.

Risks: Uses `atoi()` without full parse validation. Direction indexes must remain compatible with `directions[]`. Benchmark can stress DMA mapping paths and should be run on test systems.

Test signals: Run valid defaults, each map mode/direction, invalid bounds, missing debugfs file, and compare kernel-populated latency fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/dma/dma_map_benchmark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/check-variable-fonts.py -->
# sources/distributed-fs/ceph-client/tools/docs/check-variable-fonts.py

Purpose: Python wrapper that detects problematic Noto CJK variable fonts for kernel documentation PDF/LaTeX builds.

Important APIs, types, and functions: Adds `tools/lib/python` to `sys.path`, imports `kdoc.latex_fonts.LatexFontChecker`, builds argparse description from checker, accepts `--deny-vf`, calls `LatexFontChecker(args.deny_vf).check()`, prints any returned message, and exits with status 1.

Control flow: Always runs the font check once and exits 1 regardless of whether a message was printed.

State and persistence: May read fontconfig data under the optional deny-vf config directory. No writes in this wrapper.

Dependencies and integration points: Depends on the kernel documentation Python helper package and local/fontconfig font state. Used by documentation build checks.

Risks: The unconditional `sys.exit(1)` means callers must interpret output or this script may be intended only as a failing guard. Behavior depends on `LatexFontChecker` implementation and system fonts.

Test signals: Run with and without problematic fonts, with `--deny-vf`, and verify caller expectations for exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/check-variable-fonts.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/checktransupdate.py -->
# sources/distributed-fs/ceph-client/tools/docs/checktransupdate.py

Purpose: Checks whether translated documentation files lag behind their original English documentation based on git history.

Important APIs, types, and functions: `get_origin_path()` maps `Documentation/translations/<locale>/...` to the original path. `get_latest_commit_from()` shells out to `git log` and parses hash/author/commit dates/message. `get_origin_from_trans_smartly()` extracts tracked origin hashes from translation commit messages. `get_origin_from_trans()` falls back to author-date walk. `get_commits_count_between()` and `pretty_output()` report pending commits. `list_files_with_excluding_folders()` discovers rst files. `DmesgFormatter` and `config_logging()` configure timestamped logs. `main()` handles locale, logging, missing translations, file/directory inputs.

Control flow: With no files, it scans all non-translation `Documentation/**/*.rst`, maps each to the requested locale, logs missing translations, and checks existing translations. With files/directories, it expands inputs. It converts paths relative to the kernel root, changes cwd to that root, and checks each translation by comparing origin commit tracked by translation vs latest origin HEAD commit.

State and persistence: Writes a log file, default `checktransupdate.log`, in the caller's current directory at configuration time. It does not modify docs.

Dependencies and integration points: Depends on git history, commit message conventions, documentation tree layout, and Python logging. Supports localization maintenance workflows.

Risks: Uses `os.popen()` with formatted file/commit strings and assumes trusted paths. Author-date fallback can be inaccurate across rebases or backports. `valid_locales()` raises literal `"Invalid locale: {locale}"` without interpolation. `config_logging()` ignores the `--logfile` argument because `main()` calls it without passing `args.logfile`.

Test signals: Check one translation file with known tracked commit, directory expansion, default locale scan, missing translation reporting toggles, invalid locale, and log file option behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/checktransupdate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/documentation-file-ref-check -->
# sources/distributed-fs/ceph-client/tools/docs/documentation-file-ref-check

Purpose: Perl tool that scans the kernel tree for references to `Documentation/...` files and reports or attempts to fix references to missing files.

Important APIs, types, and functions: Uses `Getopt::Long` for `--fix`, `--warn`, and help. `%false_positives` records accepted missing references. Step 1 scans Sphinx `:doc:` references and plain `Documentation/` references with `git grep`. Step 2, enabled by `--fix`, searches likely replacements and applies `sed` replacements.

Control flow: Exits early if not in a git tree. For `:doc:` references, resolves absolute or relative `.rst` targets and reports missing ones. For general references, filters Makefiles/scripts/hidden/build output/URLs/known patterns, normalizes punctuation and wrappers, checks glob existence, applies tools-relative exceptions, then reports or accumulates for fixing. Fix mode tries devicetree `.yaml`, basename searches, `.txt` to `.rst`, dash/underscore variants, and single-match replacement.

State and persistence: Normal mode is read-only. `--fix` edits files in place through `sed -i`.

Dependencies and integration points: Depends on git grep, find, sed, Perl, and kernel Documentation layout. Used by documentation maintenance.

Risks: Parsing is regex-based and intentionally heuristic. `--fix` can modify broad matches from `git grep -l` and requires manual review. Some generated or historical references need explicit false positives.

Test signals: Run normal/warn/fix modes on a controlled branch with missing docs, `:doc:` broken references, devicetree txt-to-yaml renames, multiple replacement candidates, and false positive entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/documentation-file-ref-check -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/features-refresh.sh -->
# sources/distributed-fs/ceph-client/tools/docs/features-refresh.sh

Purpose: Regenerates architecture support tables under `Documentation/features/*/*/arch-support.txt` by scanning arch Kconfig files for configured feature symbols.

Important APIs, types, and functions: Shell loop over feature files; extracts `#         Kconfig:` line; supports plain `K` and negated `!K`; scans `arch/*/Kconfig*`; writes a temporary table and moves it into place.

Control flow: For each feature file, determine operator and Kconfig token, warn if the token is invalid across all arches, write preserved comment header and table header, iterate architectures, set status to `ok` when the feature rule matches, otherwise preserve existing status row or default to `TODO`, close table, and replace original file.

State and persistence: Mutates every `arch-support.txt` file in place through temporary files.

Dependencies and integration points: Depends on being run from kernel tree root with Documentation/features and arch directories. Uses grep, find, sed, shell globbing.

Risks: `grep "$K"` is substring-based rather than Kconfig-symbol aware. Invalid negated features can still be rewritten. No `set -e`, so command failures may continue. Existing non-comment rows are preserved only by matching `" $ARCH:"`.

Test signals: Run on a clean tree and inspect diff, features with normal and negated Kconfig symbols, renamed/missing Kconfig tokens, and arch additions/removals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/features-refresh.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/find-unused-docs.sh -->
# sources/distributed-fs/ceph-client/tools/docs/find-unused-docs.sh

Purpose: Finds C files under a given directory that contain exported kernel-doc comments but are not included by formatted documentation.

Important APIs, types, and functions: Validates kernel tree root and one directory argument. Builds `FILES_INCLUDED` associative array from `Documentation/**/*.rst` lines containing `.. kernel-doc`. Runs `tools/docs/kernel-doc -export` on candidate C files.

Control flow: From root validation, changes to the docs tool directory then kernel root, collects included files from Documentation, returns to root, finds `*.c` under the requested directory, skips files already included, invokes kernel-doc export, and prints files with non-empty exported documentation.

State and persistence: Read-only. Writes file paths to stdout.

Dependencies and integration points: Requires Bash, grep, find, and `tools/docs/kernel-doc`. Used by documentation coverage audits.

Risks: Uses whitespace splitting for included paths and `for file in \`find ...\``, so paths with spaces break. Only C files are checked. Inclusion detection is simple and may miss kernel-doc directives with unusual formatting.

Test signals: Run on a small directory with known included/unincluded exported kernel-doc comments, invalid cwd, missing argument, and nonexistent directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/find-unused-docs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/gen-redirects.py -->
# sources/distributed-fs/ceph-client/tools/docs/gen-redirects.py

Purpose: Generates static HTML redirect pages for renamed documentation pages from `gen-renames.py` output.

Important APIs, types, and functions: Parses `--output`, reads stdin lines containing old and new documentation names without `Documentation/` and `.rst`, builds old/new `.html` paths, creates old output directories, computes relative target path, and writes a meta-refresh HTML file.

Control flow: For each stdin line, split into old and new names, skip with warning if target HTML does not exist, create parent directories as needed, and write redirect content pointing to relative new page.

State and persistence: Writes HTML files under the output directory.

Dependencies and integration points: Consumes `tools/docs/gen-renames.py` output and Sphinx-built HTML output. Uses Python os/sys only.

Risks: `line.split(' ', 2)` is unpacked into two variables, which will fail if a line contains more than one separator field; current producer emits exactly one space. Generated HTML does not escape names/paths. Requires target pages built before redirects.

Test signals: Pipe known rename pairs, verify relative links at nested depths, missing target warning, and malformed input handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/gen-redirects.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/gen-renames.py -->
# sources/distributed-fs/ceph-client/tools/docs/gen-renames.py

Purpose: Walks git history to generate old-to-current documentation page rename mappings for `.rst` files.

Important APIs, types, and functions: `normalize()` strips `Documentation/` prefix and `.rst` suffix. `Name` tracks the chain of names for a file. Main code runs `git log --reverse --find-renames --diff-filter=RD --name-status` from `v4.8` to `--rev`, updates rename chains, drops deleted chains, collects current `.rst` files with `git ls-tree`, and prints old/current pairs excluding recreated names.

Control flow: Rename records move a `Name` chain from old key to new key or create a new chain. Delete records remove active chains. After history traversal, current files are used to avoid redirecting names that exist again. All old names in surviving chains map to the final name.

State and persistence: Read-only git queries; writes mappings to stdout.

Dependencies and integration points: Depends on git history, tag `v4.8`, Documentation tree, and downstream `gen-redirects.py`.

Risks: Rename detection depends on git similarity heuristics. Deletes remove chain state and do not propose alternatives. Only `.rst` files are tracked. History range assumes `v4.8` exists in the repo.

Test signals: Run at HEAD, at older revisions, with synthetic rename/delete/recreate histories, and verify no mapping points from a currently existing page.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/gen-renames.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/get_abi.py -->
# sources/distributed-fs/ceph-client/tools/docs/get_abi.py

Purpose: Command-line frontend for parsing ABI documentation, emitting ReST, validating ABI files, searching ABI symbols, and checking undefined sysfs ABI entries on the local machine.

Important APIs, types, and functions: Imports `AbiParser`, `AbiRegex`, `ABI_DIR`, `DEBUG_HELP`, and `SystemSymbols` from tools Python libraries. `AbiRest`, `AbiValidate`, `AbiSearch`, and `AbiUndefined` each register an argparse subcommand and implement `run()`. `main()` sets common debug/dir options, installs subcommands, configures logging, and dispatches.

Control flow: `rest` parses ABI docs, checks issues, and prints generated documentation with optional line markers/raw/no-file behavior. `validate` parses and checks issues only. `search` parses and searches symbols by regex. `undefined` builds regex search data and compares documented ABI symbols against sysfs entries with optional hints, multiprocessing, chunk size, found output, and dry run.

State and persistence: Read-only with respect to ABI docs and sysfs; outputs to stdout/stderr/logging. No files written by this wrapper.

Dependencies and integration points: Depends on `tools/lib/python/abi` modules, kernel ABI documentation tree, sysfs for undefined checks, Python argparse/logging, and optional multiprocessing inside helpers.

Risks: Wrapper behavior is only as stable as helper modules and ABI parser contracts. Undefined checks can be expensive on large sysfs trees. The `--show-hints` option in `rest` is accepted but not used directly here.

Test signals: Run all subcommands against a small ABI dir, search known symbols, validate malformed docs, run undefined with `--dry-run`, `--found`, and `-j` variations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/get_abi.py -->
