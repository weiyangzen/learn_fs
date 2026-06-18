# subset-b-006608 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-trace.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-trace.c

### Purpose
`builtin-trace.c` implements the `perf trace` builtin: a strace-like live/replay tracer that formats syscall enter/exit events, arbitrary tracepoints, page faults, callchains, scheduler runtime, and optional BPF-augmented syscall payloads. It is the main integration point between perf's evlist/session machinery, tracefs tracepoint metadata, syscall tables, beauty printers, BTF pretty printing, and summary reporting.

### Important APIs, Types, And Functions
The central state is `struct trace`, which owns the perf tool callbacks, evlist, host machine, syscall cache, filters, summary hashmaps, ordered-events queue, output, and many formatting flags. `struct syscall` caches per-architecture syscall metadata, tracepoint format fields, argument formatters, BPF programs, and flags such as `is_open` and `is_exit`. `struct thread_trace` is per-thread state for pending syscall entry strings, syscall timing, fd-to-path cache, vfs filename staging, page-fault counts, and summary stats. `struct syscall_arg_fmt` and `struct syscall_fmt` describe how syscall arguments and returns are rendered and parsed for tracepoint filters.

Key control functions are `cmd_trace()`, `trace__run()`, `trace__replay()`, `trace__sys_enter()`, `trace__sys_exit()`, `trace__event_handler()`, `trace__pgfault()`, `trace__vfs_getname()`, `trace__parse_events_option()`, and `trace__init_syscalls_bpf_prog_array_maps()`. Helper families initialize tracepoint field readers, expand string enum filter expressions, resolve BTF types, and dump syscall summaries.

### Control Flow
`cmd_trace()` builds a default `struct trace`, parses perf config and command-line options, decides whether syscall tracing is implicit, prepares BPF augmentation when available, configures evsel handlers, validates targets, and dispatches either record mode, replay mode, or live tracing. Live mode in `trace__run()` creates syscall/page-fault/sched evsels, creates maps, initializes symbols and threads, prepares optional workload execution, opens events, applies pid/syscall filters, mmaps ring buffers, enables events, drains perf mmap buffers, and prints optional summaries before cleanup.

For syscalls, `trace__sys_enter()` resolves the syscall id to metadata, formats arguments into the thread's pending `entry_str`, records entry timestamp, and handles exit-like syscalls specially. `trace__sys_exit()` resolves the return event, updates summary stats, computes duration, applies duration/failure/stack filters, prints the saved entry plus return value, and updates fd path caches for successful open/openat calls. Generic tracepoints use `trace__event_handler()` and `trace__fprintf_tp_fields()`, while replay mode maps perf.data samples through `perf_session__process_events()`.

### State And Persistence
State is mostly process-local and transient: evlists, machines, thread privates, syscall metadata caches, BPF maps, ordered-events queues, and output streams. Persistent or external state includes optional output files, perf.data replay input, tracefs/kprobe definitions for `vfs_getname`, BPF program/map state, `/proc/<pid>/fd` lookups, and `.perfconfig` `trace.*` settings. `trace__open_output()` rotates an existing output file to `.old`. Per-thread fd path caches are invalidated on `close` only when that syscall is traced; otherwise fd path beautification is disabled.

### Dependencies And Integration Points
The file depends on perf core libraries (`evlist`, `evsel`, `machine`, `thread`, `session`, `record`, `parse-events`, `callchain`, `ordered_events`), traceevent metadata, syscall tables, trace beauty formatters, libbpf/BTF when enabled, tracefs paths, cgroups, symbol resolution, and Linux perf mmap APIs. It also coordinates with generated `trace_augment` BPF objects and BPF summary helpers.

### Risks
The code has a broad kernel-version surface: raw syscall tracepoint field names, syscall aliases, tracefs formats, BTF availability, BPF support, and arch-specific syscall tables can diverge. Argument augmentation uses size/offset heuristics and static buffering, so raw payload layout assumptions are important. fd path caches can be stale if `close` is filtered out. Summary stats currently key total stats only by syscall id and note mixed-ABI inaccuracies. Filter expression expansion relies on formatter reverse parsers and can reject valid-looking filters when a resolver is missing.

### Test Signals
Strong signals include `perf trace` smoke tests for live, workload, pid/tid, system-wide, input replay, `record`, syscall qualifiers including aliases/globs/negation, event filters using symbolic constants, duration/failure filtering, page faults, callchains, `--sort-events`, BPF augmentation on/off, BTF enum/struct formatting, fd path tracking across open/close, `vfs_getname` fallback, and summaries by thread/total/BPF. Cross-kernel and cross-architecture runs are especially valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-version.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-version.c

### Purpose
This file implements `perf version`. It prints the perf version string and, when requested by `--build-options` or `-v`, prints the status of build-time optional features.

### Important APIs, Types, And Functions
`struct version` stores the `build_options` flag. `version_options` defines `--build-options` using the subcmd parse-options API. `library_status()` iterates the global `supported_features[]` array declared in `builtin.h` and prints each feature through `feature_status__printf()`. `cmd_version()` is the builtin entry point called from `perf.c`.

### Control Flow
`cmd_version()` parses options with `PARSE_OPT_STOP_AT_NON_OPTION`, prints `perf version %s` using `perf_version_string`, then conditionally calls `library_status()` if the option was set or global `verbose` is positive.

### State And Persistence
State is limited to one static `version` instance and global `verbose`. The command does not write persistent data.

### Dependencies And Integration Points
It depends on `util/header.h` for `perf_version_string`, `util/debug.h` for `verbose`, `color.h`/feature status formatting, generated `tools/config.h`, and `builtin.h` for supported feature metadata.

### Risks
Output correctness depends on `supported_features[]` staying in sync with build configuration. The static `version` object is not reset between hypothetical in-process invocations, though perf normally exits per command.

### Test Signals
Run `perf version`, `perf version --build-options`, and `perf -vv` and verify version output plus expected feature rows for enabled/disabled libraries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-version.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin.h -->
# sources/distributed-fs/ceph-client/tools/perf/builtin.h

### Purpose
`builtin.h` is the common declaration point for perf builtin command entry functions and build-feature reporting helpers. It lets the command dispatcher call each builtin without exposing implementation headers.

### Important APIs, Types, And Functions
`struct feature_status` describes a build option by display name, macro, help tip, and builtin status. `supported_features[]` and `feature_status__printf()` are used by `perf version`. The rest of the header declares help helpers and `cmd_*()` entry points for perf subcommands such as `record`, `stat`, `trace`, `script`, `daemon`, and `kwork`.

### Control Flow
This header has no runtime control flow, but its declarations define the contract used by `perf.c`'s `commands[]` table. Each `cmd_*()` accepts the conventional `(int argc, const char **argv)` pair and returns an exit status.

### State And Persistence
Only external feature metadata is declared. No state is defined in this header.

### Dependencies And Integration Points
It integrates all builtin implementations with the central dispatcher and completion/listing paths. Conditional compilation happens in `perf.c`, while this header exposes all possible command signatures.

### Risks
Adding/removing a builtin requires keeping this header, the implementation, build files, and `perf.c` command table aligned. A stale declaration will fail at build/link time or hide a command from dispatch.

### Test Signals
Build coverage is the main signal. Runtime checks are `perf --list-cmds`, command help routing, and executing newly added commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/check-header_ignore_hunks/lib/list_sort.c -->
# sources/distributed-fs/ceph-client/tools/perf/check-header_ignore_hunks/lib/list_sort.c

### Purpose
This file is not C source; it is a diff hunk allowlist used by `check-headers.sh` when comparing `tools/lib/list_sort.c` against the kernel's `lib/list_sort.c`. It records an intentional difference to ignore.

### Important APIs, Types, And Functions
The hunk adds a local `u8 count` and a periodic `cmp(priv, b, b)` callback in the remainder-linking loop of `list_sort` merge logic. The comment explains that highly unbalanced merges, such as already sorted input, may otherwise run many iterations without comparator callbacks, so the callback gives clients a chance to call `cond_resched()`.

### Control Flow
`check-headers.sh` pipes unified diff output through `grep -vf` using this file. Lines matching this hunk are filtered before counting remaining differences.

### State And Persistence
The file persists an expected synchronization exception. It has no runtime state.

### Dependencies And Integration Points
It is tightly coupled to `tools/perf/check-headers.sh` and the textual shape of the upstream diff for `lib/list_sort.c`.

### Risks
Because this is pattern-based diff filtering, upstream edits can make the ignore hunk fail to match or accidentally match too broadly. The file must be reviewed whenever `list_sort.c` is resynced.

### Test Signals
Run `tools/perf/check-headers.sh` from a full kernel tree and verify `lib/list_sort.c` does not report a failure except for new, real differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/check-header_ignore_hunks/lib/list_sort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/check-headers.sh -->
# sources/distributed-fs/ceph-client/tools/perf/check-headers.sh

### Purpose
`check-headers.sh` validates that perf's vendored copies of kernel UAPI, arch, library, syscall-table, and beauty-generator inputs remain synchronized with their source files in the kernel tree.

### Important APIs, Types, And Functions
Arrays `FILES`, `SYNC_CHECK_FILES`, and `BEAUTY_FILES` enumerate files compared under `tools/`, files compared with sync-ignore regexes, and trace beauty copies under `tools/perf/trace/beauty/`. Functions `check_2()`, `check()`, `beauty_check()`, and `check_ignore_some_hunks()` build diff commands and append failures to `FAILURES`.

### Control Flow
The script first skips cleanly when `../../include` is missing, which handles detached tools tarballs. It changes to the kernel root, runs simple diffs, sync-check diffs, special regex-ignored diffs, non-symmetric syscall-table comparisons, beauty comparisons, duplicated hashmap checks, and finally `check_ignore_some_hunks lib/list_sort.c`. At the end it prints warning lines with `diff -u` commands for every recorded failure.

### State And Persistence
State is shell variables and the `FAILURES` array only. It does not update files; it reports drift.

### Dependencies And Integration Points
It assumes execution from `tools/perf`, access to the kernel source two levels up, GNU-ish `diff`, `grep`, `wc`, Bash arrays, and the ignore-hunk tree under `tools/perf/check-header_ignore_hunks`.

### Risks
The script uses `eval` to run assembled diff commands, so quoted arguments must remain controlled by static arrays. Regex ignore rules can mask unintended changes if too broad. Missing source files are skipped by `check_2()` if the original does not exist, so tree layout changes can reduce coverage.

### Test Signals
Run in a full kernel checkout and in a detached tools-only tree. Expected signals are zero warnings for synced trees, warning commands for deliberately modified copies, and correct skip behavior without `../../include`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/check-headers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/dlfilters/dlfilter-show-cycles.c -->
# sources/distributed-fs/ceph-client/tools/perf/dlfilters/dlfilter-show-cycles.c

### Purpose
This sample `perf script --dlfilter` plugin prints cumulative cycle counts and deltas at the start of each output line, using IPC-derived `cyc_cnt` fields.

### Important APIs, Types, And Functions
It uses the public `perf_dlfilter.h` ABI. `filter_event_early()` accumulates counts before normal script filtering. `filter_event()` prints totals and deltas. `filter_description()` exposes help text. Counts are stored per CPU in `cycles[MAX_CPU][MAX_ENTRY]` or per TID in an open-addressed hash table when CPU is not recorded.

### Control Flow
`event_entry()` classifies event names into instructions, branches, or other. Early filtering adds `sample->cyc_cnt` to the relevant bucket. Later filtering prints the current total and the difference from the last reported value, then updates the reported snapshot.

### State And Persistence
All state is static process memory: per-CPU arrays, per-TID table, and report snapshots. It is reset on each plugin load and not persisted.

### Dependencies And Integration Points
The plugin is loaded by perf's dlfilter mechanism and relies on `perf_dlfilter_sample.event`, `cpu`, `tid`, and `cyc_cnt` being populated by perf script.

### Risks
`MAX_CPU` is fixed at 4096; higher CPU ids fall back only if TID is present. The TID hash table caps at half full and has no deletion. Event classification is prefix based, so renamed events may fall into `OTHER_CYC`.

### Test Signals
Run `perf script --dlfilter dlfilter-show-cycles.so` on perf.data with IPC fields and verify per-line totals/deltas for branch, instruction, and other events, including data without CPU but with TID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/dlfilters/dlfilter-show-cycles.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/dlfilters/dlfilter-test-api-v0.c -->
# sources/distributed-fs/ceph-client/tools/perf/dlfilters/dlfilter-test-api-v0.c

### Purpose
This test dlfilter validates backward compatibility with the original v0 perf dlfilter C API. It intentionally copies the old struct and function table definitions instead of including the current header.

### Important APIs, Types, And Functions
The local v0 `struct perf_dlfilter_sample`, `struct perf_dlfilter_al`, and `struct perf_dlfilter_fns` define the ABI being tested. `start()` validates `--dlarg` argument delivery and allocates `filter_data`. `filter_event_early()` and `filter_event()` call `do_checks()` to validate sample fields, address resolution, event attributes, and object-code reads. `stop()` checks lifecycle ordering and frees state.

### Control Flow
The test expects exactly one early callback and one normal callback unless early filtering is configured to suppress the normal event. It compares sample fields against fixed test values, checks symbol resolution for `foo` and `bar`, verifies `resolve_address()` matches `resolve_ip()`, and returns either keep/filter results according to `do_early`.

### State And Persistence
State is one heap-allocated `filter_data` pointer plus counters proving callback ordering. It is released in `stop()`.

### Dependencies And Integration Points
It is used by perf's dlfilter API test harness, which must synthesize expected sample values, dlargs, symbols, attr data, and object code.

### Risks
The test is deliberately strict; changes in fixture values or event naming require coordinated updates. Because it embeds the old ABI, it must not be mechanically changed to match the current header.

### Test Signals
The `dlfilter C API` perf test should load this shared object and pass under both keep and early-filter modes, proving v0 layout and function slots still work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/dlfilters/dlfilter-test-api-v0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/dlfilters/dlfilter-test-api-v2.c -->
# sources/distributed-fs/ceph-client/tools/perf/dlfilters/dlfilter-test-api-v2.c

### Purpose
This test dlfilter validates the v2 perf dlfilter API, including the `machine_pid`/`vcpu` sample extension marker and `al_cleanup()` address-location cleanup hook, while preserving compatibility behavior from the v0 test.

### Important APIs, Types, And Functions
The file copies v2 definitions for `perf_dlfilter_sample`, `perf_dlfilter_al`, and `perf_dlfilter_fns`. Compared with v0, the sample adds `machine_pid` and `vcpu`, address locations add private data, and the function table adds `al_cleanup()` while reducing reserved slots. The callback functions mirror the v0 test and additionally call `al_cleanup()` when present after `resolve_address()`.

### Control Flow
`start()` parses test arguments and stores expected IP/address values. The early and normal callbacks enforce one-shot ordering, validate sample fields, test `attr()`, and, when configured, resolve IP, data address, arbitrary address, and object code. `stop()` verifies lifecycle and frees state.

### State And Persistence
Only the heap `filter_data` and static lifecycle guard are retained during one plugin run.

### Dependencies And Integration Points
It is consumed by the perf dlfilter API self-test and depends on perf providing a v2-compatible function table but tolerating older optional function absence.

### Risks
As an ABI fixture, field ordering and reserved slot count are sensitive. Accidentally including the live header would stop testing compatibility with the historical v2 layout.

### Test Signals
The perf dlfilter C API test should pass with `al_cleanup()` available or absent, verifying v2 callbacks, struct size checks, symbol resolution, object-code reads, and early filtering behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/dlfilters/dlfilter-test-api-v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/include/perf/perf_dlfilter.h -->
# sources/distributed-fs/ceph-client/tools/perf/include/perf/perf_dlfilter.h

### Purpose
This public header defines the stable C ABI for shared objects loaded by `perf script --dlfilter`. It exposes sample data, resolved address metadata, helper callbacks, and optional plugin entry points.

### Important APIs, Types, And Functions
`struct perf_dlfilter_sample` carries perf sample fields, branch stack/callchain pointers, event name, and virtualization fields `machine_pid` and `vcpu`. `struct perf_dlfilter_al` describes resolved address-location data, including symbol, DSO, build-id, kernel/user flags, command name, and private data. `struct perf_dlfilter_fns` is the helper table exported by perf: `resolve_ip`, `resolve_addr`, `args`, `resolve_address`, `insn`, `srcline`, `attr`, `object_code`, optional `al_cleanup`, and reserved slots. Optional plugin functions are `start`, `stop`, `filter_event`, `filter_event_early`, and `filter_description`.

### Control Flow
Perf loads the shared object, fills `perf_dlfilter_fns`, calls `start()` if present, invokes early and normal filter callbacks per sample, and calls `stop()` at the end. Filters return 0 to keep, 1 to filter, or negative error.

### State And Persistence
The ABI itself has no state. Plugins may store opaque state through `start()`'s `data` pointer. Struct `size` fields support compatibility checks as the ABI grows.

### Dependencies And Integration Points
The header depends on Linux perf event and integer types and is included by out-of-tree dlfilter plugins, sample filters, and perf tests.

### Risks
ABI layout is the major risk. Fields must be appended compatibly, reserved slots managed carefully, and plugins must check optional callbacks before use. Pointers are owned by perf unless explicitly documented otherwise.

### Test Signals
Compile sample filters, run v0/v2/current dlfilter API tests, and verify older plugin binaries still load and receive valid callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/include/perf/perf_dlfilter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/jvmti/jvmti_agent.c -->
# sources/distributed-fs/ceph-client/tools/perf/jvmti/jvmti_agent.c

### Purpose
`jvmti_agent.c` implements the low-level jitdump writer used by perf's Java JVMTI agent. It creates a perf-discoverable jitdump file and writes code load, debug info, and close records for JIT-compiled Java code.

### Important APIs, Types, And Functions
Public functions from `jvmti_agent.h` are `jvmti_open()`, `jvmti_close()`, `jvmti_write_code()`, and `jvmti_write_debug_info()`. Helpers include `create_jit_cache_dir()`, `perf_open_marker_file()`, `perf_close_marker_file()`, `get_e_machine()`, `perf_get_timestamp()`, and optional architecture timestamp support via `JITDUMP_USE_ARCH_TIMESTAMP`.

### Control Flow
`jvmti_open()` initializes timestamp mode, creates `$JITDUMPDIR/.debug/jit` or `$HOME/.debug/jit`, creates a dated temporary directory and `jit-<pid>.dump`, mmaps the file executable as a marker for perf, writes the jitdump header, and returns a `FILE *`. `jvmti_write_code()` writes a `JIT_CODE_LOAD` record, symbol name, and optional code bytes under `flockfile()`. `jvmti_write_debug_info()` writes source-line records. `jvmti_close()` writes `JIT_CODE_CLOSE`, closes the stream, and unmaps the marker.

### State And Persistence
Persistent output is the jitdump file under `.debug/jit`. Static state includes `jit_path`, `marker_addr`, timestamp mode, and a monotonically increasing code generation counter. Writes are protected at the `FILE *` level for multi-threaded JVM callbacks.

### Dependencies And Integration Points
It depends on perf's `util/jitdump.h`, Linux `/proc/self/exe` ELF headers, mmap marker behavior consumed by perf record/report, environment variables `JITDUMPDIR`, `HOME`, and `JITDUMP_USE_ARCH_TIMESTAMP`, and JVMTI-facing types from the header.

### Risks
Path construction can fail for long environment paths. `perf_open_marker_file()` leaks the raw fd path on some early error paths before `fdopen()`. Timestamp source must match perf's expectations. Debug info size calculations depend on all filenames being valid.

### Test Signals
Run a Java workload with the agent under `perf record`, then verify a jitdump file is produced, perf.data contains the marker mapping, `perf inject/report` resolves Java JIT symbols, and line info appears when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/jvmti/jvmti_agent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/jvmti/jvmti_agent.h -->
# sources/distributed-fs/ceph-client/tools/perf/jvmti/jvmti_agent.h

### Purpose
This header declares the jitdump writer interface shared between the JVMTI callback layer and the low-level writer implementation.

### Important APIs, Types, And Functions
`jvmti_line_info_t` carries a program counter, source line number, discriminator, and `jmethodID`. The public functions open/close an agent writer and emit code load and debug-info records: `jvmti_open`, `jvmti_close`, `jvmti_write_code`, and `jvmti_write_debug_info`.

### Control Flow
The intended lifecycle is open once during `Agent_OnLoad`, write code/debug records from compiled-method callbacks, then close during `Agent_OnUnload`.

### State And Persistence
The header defines no state. The opaque `void *agent` returned by `jvmti_open()` is owned by the implementation and currently represents a `FILE *`.

### Dependencies And Integration Points
It includes `<jvmti.h>` for `jmethodID` and uses `extern "C"` guards for C++ consumers. `libjvmti.c` is the primary caller.

### Risks
Because the handle is opaque but not type-safe, callers can pass invalid pointers. The comment on the final include guard names `__JVMTI_H__` instead of `__JVMTI_AGENT_H__`, a cosmetic mismatch.

### Test Signals
Build the JVMTI agent, load it into a JVM, and verify the callback layer links against these declarations and writes jitdump records successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/jvmti/jvmti_agent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/jvmti/libjvmti.c -->
# sources/distributed-fs/ceph-client/tools/perf/jvmti/libjvmti.c

### Purpose
`libjvmti.c` is the actual JVM agent entry point. It registers JVMTI callbacks for compiled Java methods and dynamic code, resolves method/class/source metadata, and forwards JIT code and optional line mappings to `jvmti_agent.c`.

### Important APIs, Types, And Functions
`Agent_OnLoad()` and `Agent_OnUnload()` are the JVM entry points. `compiled_method_load_cb()` handles `JVMTI_EVENT_COMPILED_METHOD_LOAD`; `code_generated_cb()` handles dynamic generated code. When `HAVE_JVMTI_CMLR` is available, `get_line_numbers()` walks compiled-method-load inline records and `do_get_line_number()` maps bytecode indices to source lines. `get_source_filename()`, `copy_class_filename()`, and `fill_source_filenames()` build source file paths for debug records.

### Control Flow
On load, the agent opens the jitdump writer, gets a JVMTI v1 environment, requests compiled-method-load capability, optionally requests line/source capabilities when JVM location format is BCI, installs callbacks, and enables events. For each compiled method, it optionally extracts line info, obtains class signature and method name/signature, writes debug info first, then writes a code load record named as class+method+signature. On unload it closes the jitdump writer.

### State And Persistence
Global `jvmti_agent` stores the writer handle and `has_line_numbers` records optional capability availability. Persistent data is written through the jitdump writer.

### Dependencies And Integration Points
It depends on JVMTI/JNI, optional `jvmticmlr.h`, perf's jitdump writer API, and JVM callback semantics. It integrates with perf report through the jitdump format produced by the writer.

### Risks
Callback error handling logs and returns, so missing metadata can reduce symbol/debug quality without failing the JVM. `Agent_OnLoad()` returns after some failure paths without closing an already opened writer. Source filename construction assumes Java class signatures map naturally to paths. Inline caller frames are ignored; only leaf methods are recorded.

### Test Signals
Load the built agent into HotSpot with JIT compilation enabled, record with perf, and verify Java method symbols and optional line information appear. Exercise builds with and without `HAVE_JVMTI_CMLR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/jvmti/libjvmti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/perf-archive.sh -->
# sources/distributed-fs/ceph-client/tools/perf/perf-archive.sh

### Purpose
`perf-archive.sh` packages or unpacks build-id debug symbol files needed to analyze a `perf.data` file on another machine. With `--all` it also bundles `perf.data`.

### Important APIs, Types, And Functions
The script parses `--all`, `--unpack`, `--exclude-buildids`, and an optional perf.data or archive path. It uses `perf buildid-list -i <data> --with-hits` to collect build ids, constructs a tar manifest from `.build-id` links and resolved debug files, and creates bzip2 tar archives.

### Control Flow
Unpack mode locates or validates an archive, distinguishes `perf.all*.tar.bz2` bundles from symbol-only archives, prompts before overwriting current-directory files, then extracts symbols into `~/.debug`. Pack mode resolves `PERF_BUILDID_DIR` or defaults to `~/.debug`, builds a temporary build-id list with optional exclusions, generates a manifest, and writes either `perf.data.tar.bz2` or `perf.all-<host>-<date>.tar.bz2`.

### State And Persistence
Persistent outputs are tarballs and extracted files under `~/.debug`. Temporary build-id and manifest files are created under `/tmp` and normally removed. Existing unpack targets can be overwritten after prompting.

### Dependencies And Integration Points
It depends on Bash, `perf`, `tar`, `grep`, `comm`, `readlink`, `mktemp`, `hostname`, `date`, and the perf build-id cache layout.

### Risks
Several variable expansions are unquoted in pack paths, so paths with spaces are risky. Unpack auto-discovery errors when multiple matching archives exist. Exclusion semantics require a correctly formatted build-id list.

### Test Signals
Create archives from perf.data with and without `--all`, apply an exclusion list, unpack into a clean home/debug directory, and verify `perf report` resolves symbols from the archive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/perf-archive.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/perf-completion.sh -->
# sources/distributed-fs/ceph-client/tools/perf/perf-completion.sh

### Purpose
This script provides Bash and Zsh completion for perf commands, options, subcommands, event names, PMU events, and metric names.

### Important APIs, Types, And Functions
Compatibility helpers `__my_reassemble_comp_words_by_ref()`, `__perf_get_comp_words_by_ref()`, and `__perf__ltrim_colon_completions()` replace missing bash-completion functions. `__perfcomp()` and `__perfcomp_colon()` generate completions. `__perf_prev_skip_opts()` identifies the active perf subcommand. `__perf_main()` contains the completion decision tree. Shell-specific `_perf()` functions register completion for Zsh or Bash.

### Control Flow
The script first detects whether helper functions are preloaded. Completion determines the current word, finds the nearest command context, then completes top-level commands/options, event names after `-e/--event`, `--pfm-events`, stat metrics after `-M/--metrics`, nested subcommands, or long options. It queries perf dynamically via `--list-cmds`, `--list-opts`, and `perf list --raw-dump`.

### State And Persistence
It mutates shell completion variables such as `COMPREPLY`, `COMP_WORDBREAKS`, and Zsh `_ret`. No files are written.

### Dependencies And Integration Points
It integrates with Bash programmable completion, Zsh `compdef`, the installed `perf` executable, `/sys/bus/event_source/devices/cpu/events`, and shell pattern matching.

### Risks
Dynamic calls to `perf list` and sysfs can be slow or unavailable. Some expansions intentionally split on spaces and assume event names are completion-safe. Architecture-specific sysfs checks special-case aarch64 only.

### Test Signals
Source the script in Bash and Zsh and test top-level command completion, `perf record -e`, comma-separated events, `perf stat -M`, long options, and nested commands like `perf script`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/perf-completion.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/perf-iostat.sh -->
# sources/distributed-fs/ceph-client/tools/perf/perf-iostat.sh

### Purpose
`perf-iostat.sh` is a thin compatibility wrapper implementing `perf iostat` by delegating to `perf stat --iostat`.

### Important APIs, Types, And Functions
There are no functions. It chooses a delimiter and invokes `perf stat --iostat$DELIMITER$*`.

### Control Flow
If the first argument is `list` or looks like a PCI device selector (`hex:hex` optionally followed by comma), it uses `=` so the argument is attached as `--iostat=<value>`. Otherwise it uses a space, producing `--iostat <args>`.

### State And Persistence
No state is persisted; all behavior is delegated to `perf stat`.

### Dependencies And Integration Points
It depends on Bash regex matching and the installed `perf` executable. `perf.c` lists `iostat` as an external command (`fn == NULL`) so the dispatcher can run `perf-iostat`.

### Risks
Arguments are forwarded through `$*` unquoted, so whitespace-containing arguments are not preserved. Regex detection is simple and may misclassify unusual input.

### Test Signals
Run `perf iostat list`, `perf iostat <pci-selector>`, and normal interval/count forms, verifying the equivalent `perf stat --iostat` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/perf-iostat.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/perf-read-vdso.c -->
# sources/distributed-fs/ceph-client/tools/perf/perf-read-vdso.c

### Purpose
`perf-read-vdso.c` is a small helper that writes the current process's `[vdso]` mapping bytes to stdout. Perf uses this kind of helper to capture vDSO contents for symbolization or tests.

### Important APIs, Types, And Functions
It includes `util/find-map.c` to reuse `find_map()`. `main()` locates the mapping named `[vdso]`, calculates `end - start`, writes it to stdout in a loop with `fwrite()`, flushes stdout, and returns nonzero on failure.

### Control Flow
The program exits with 1 if the vDSO map cannot be found, if any write returns zero, or if `fflush()` fails. Otherwise it streams the exact mapped bytes and exits 0.

### State And Persistence
It has no persistent state and writes only to stdout.

### Dependencies And Integration Points
It depends on Linux process maps and the shared `find_map()` implementation also used by perf's vDSO utility code.

### Risks
Pointer arithmetic is performed on `void *`, which relies on compiler extension support common in this codebase. Short writes are handled, but write errors only surface as zero writes or flush failure.

### Test Signals
Run the helper and verify it emits an ELF-like vDSO blob on Linux, returns nonzero in environments without `[vdso]`, and produces bytes that downstream perf tooling can parse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/perf-read-vdso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/perf-sys.h -->
# sources/distributed-fs/ceph-client/tools/perf/perf-sys.h

### Purpose
`perf-sys.h` provides a tiny wrapper around the `perf_event_open` syscall for code that wants direct syscall access without libc support.

### Important APIs, Types, And Functions
It forward-declares `struct perf_event_attr` and defines `sys_perf_event_open()`, which calls `syscall(__NR_perf_event_open, attr, pid, cpu, group_fd, flags)`.

### Control Flow
The inline function returns the raw syscall result: a file descriptor on success or `-1` with `errno` set on failure.

### State And Persistence
No state is stored.

### Dependencies And Integration Points
It depends on `<sys/syscall.h>` exposing `__NR_perf_event_open`, POSIX `syscall()`, and Linux perf event attributes. It is included by `perf.c` and other perf internals.

### Risks
Availability is Linux-specific. Callers must initialize `perf_event_attr` correctly and handle permission/sysctl failures.

### Test Signals
Build on supported Linux architectures and run perf commands that open events, checking error paths under restrictive `perf_event_paranoid` settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/perf-sys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/perf.c -->
# sources/distributed-fs/ceph-client/tools/perf/perf.c

### Purpose
`perf.c` is the main executable dispatcher for perf. It initializes global perf infrastructure, parses top-level options, routes internal commands to `cmd_*()` functions, and falls back to external `perf-<cmd>` helpers.

### Important APIs, Types, And Functions
`struct cmd_struct` maps command names to builtin functions and option flags. `commands[]` is the authoritative command list used for dispatch and completion. Top-level option handling is in `handle_options()`. `run_builtin()` applies pager/browser config and executes a builtin. `handle_internal_command()`, `execv_dashed_external()`, and `run_argv()` implement internal and external command lookup. `main()` initializes config, paths, libperf printing, build-id directory, signal behavior, and unknown-command help.

### Control Flow
Startup initializes debug, exec path, pager, libperf, config, and build-id directory. If invoked as `perf-foo`, it tries direct internal dispatch. If invoked as `trace`, it directly calls `cmd_trace()` when built with libtraceevent. Otherwise it strips top-level options, prints help when no command is given, sets up PATH, blocks SIGWINCH, then loops attempting internal dispatch or external `perf-<cmd>` execution. Unknown commands are passed through `help_unknown_cmd()` once.

### State And Persistence
Global state includes `use_pager`, `debug_fp`, perf config globals, build-id directory, environment variables for pager/paths, and optional debug output file. It does not create command-specific persistent state itself.

### Dependencies And Integration Points
It integrates with every builtin declared in `builtin.h`, libsubcmd, perf config, UI browser setup, parse-events, tracing path configuration, build-id cache, libperf logging, and shell completion through `--list-cmds`/`--list-opts`.

### Risks
Command tables must stay synchronized with declarations, build conditionals, man/help docs, and external scripts such as `perf-archive` and `perf-iostat`. Top-level option parsing stops before command options, so ambiguous flags must be handled carefully. External fallback relies on PATH setup and status conventions from `run_command_v_opt()`.

### Test Signals
Run top-level help/version/listing options, builtin commands, external script commands, `perf-<cmd>` symlink invocation, unknown command suggestions, pager/no-pager behavior, debug file setup, and builds with optional features disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/perf.h -->
# sources/distributed-fs/ceph-client/tools/perf/perf.h

### Purpose
`perf.h` is a small shared perf header defining global constants and affinity mode identifiers used by perf internals.

### Important APIs, Types, And Functions
It defines `MAX_NR_CPUS` as 4096 and `enum perf_affinity` values `PERF_AFFINITY_SYS`, `PERF_AFFINITY_NODE`, `PERF_AFFINITY_CPU`, and `PERF_AFFINITY_MAX`.

### Control Flow
No runtime control flow exists.

### State And Persistence
No state is defined.

### Dependencies And Integration Points
It is included by `perf.c` and other perf code needing common CPU/affinity definitions.

### Risks
`MAX_NR_CPUS` is a fixed compile-time limit that can be too low for very large systems if used for static arrays. Enum values are API-like within perf and should stay stable for users of the type.

### Test Signals
Build coverage plus runtime tests on large CPU-count systems or code paths that select system/node/CPU affinity modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/perf.h -->
