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
