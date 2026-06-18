# Research: subset-b-006605

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-record.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-record.c

## Purpose

`builtin-record.c` implements the `perf record` builtin. It parses recording options, configures perf events and target process/CPU maps, streams kernel ring-buffer records into `perf.data`, synthesizes metadata needed by later tools, optionally splits output files, and finalizes headers/build-id/cache state for consumption by `perf report`, `perf script`, and other perf readers.

This file is the write-side half of the record/report workflow: it owns capture-time decisions about event attributes, sample fields, mmap/AUX buffers, sideband events, compression, build-id policy, and output-file layout.

## Important APIs, Types, And Functions

Key local types:

- `struct switch_output`: state for `--switch-output`, including trigger mode (`signal`, `size`, `time`), file rotation list, and current index.
- `struct thread_mask`: two `mmap_cpu_mask` bitmaps, one for mmap ownership and one for reader thread affinity.
- `struct record_thread`: per-reader-thread state: TID, masks, control pipes, private `fdarray`, mmap pointer arrays, per-thread sample/wakeup/write/compression counters, and back-pointer to `struct record`.
- `struct pollfd_index_map`: maps main evlist pollfd positions to per-thread pollfd positions so non-perf control descriptors can be reflected back to the main evlist.
- `struct record`: command-level state combining `perf_tool`, `record_opts`, `perf_data`, `perf_session`, evlists, auxtrace recorder, build-id and switch-output flags, compression/debuginfod settings, counters, thread masks/data, and pollfd index map.

Important entry points and callbacks:

- `cmd_record()` is the public builtin entry. It initializes global defaults, parses config/options, validates option combinations, configures events, maps target CPUs/threads, initializes thread masks, and calls `__cmd_record()`.
- `__cmd_record()` runs the actual recording lifecycle: create session, prepare workload, configure/open evsels, mmap buffers, write initial header, synthesize metadata, start sideband/reader threads, run the poll/read loop, drain and finalize output, handle workload exit, lost samples, build IDs, compression metadata, and cleanup.
- `record__open()` opens every evsel, applies fallback/removal behavior for events that cannot be opened, applies filters, mmaps buffers, and binds the evlist into the session.
- `record__mmap_evlist()` calls `evlist__mmap_ex()`, initializes control fd handling, allocates per-thread mmap/pollfd state, and in parallel streaming mode creates a perf data directory with per-mmap files.
- `record__mmap_read_evlist()` and `record__mmap_read_all()` drain normal and overwrite mmap buffers, optionally through AIO, and append `PERF_RECORD_FINISHED_ROUND` markers in single-output mode.
- `record__write()` is the central write helper. It writes to the session file or per-map file, updates byte counters, enforces `--max-size`, and triggers size-based output switching.
- `record__pushfn()` is the `perf_mmap__push()` callback for normal synchronous writes; it also handles zstd compression framing and padding.
- `record__aio_*()` functions implement optional asynchronous trace writing when `HAVE_AIO_SUPPORT` is available.
- `record__synthesize()` emits synthetic metadata such as time conversion, id index, auxtrace info, kernel/module maps, guest OS maps, extra attrs, thread maps, CPU maps, BPF events, cgroups, and task/mmaps.
- `record__finish_output()` computes final data sizes, processes build IDs when enabled, writes the final file header, and updates the build-id cache.
- `record__switch_output()` finalizes the current file, switches to a timestamped output, rotates old outputs if `--switch-max-files` was used, and synthesizes tracking events for the new file.
- `record__start_threads()`, `record__thread()`, and `record__stop_threads()` implement parallel trace streaming using detached pthreads, per-thread poll loops, and pipe-based startup/shutdown acknowledgements.
- `record__init_thread_*_masks()` functions derive reader-thread mmap/affinity assignments for CPU, core, package, NUMA, user-specified, or default single-thread modes.
- `record__auxtrace_init()`, `record__process_auxtrace()`, `record__read_auxtrace_snapshot()`, and `record__auxtrace_snapshot_exit()` integrate AUX area tracing and snapshot mode.
- `perf_record_config()` reads `record.*` config keys, including build-id policy, AIO control block count, and debuginfod.
- `__record_options[]` exposes command-line options for event selection, target selection, sampling fields, callchains, branch/memory/AUX/cgroup/namespace data, switch-output, AIO, compression, control fd, threads, off-CPU analysis, and BPF filter setup.

## Control Flow

`cmd_record()` starts by creating an evlist, applying perf config, parsing options, and normalizing target defaults. No workload and no explicit target implies system-wide recording; UID filtering also forces system-wide mode. It rejects or rewrites incompatible option combinations such as latency profiling with system-wide collection, parallel streaming with AIO/affinity/timestamp-output, switch-output in parallel mode, unsupported cgroup/switch-event kernel features, and pipe/AUX modes incompatible with parallel streaming.

After option normalization, `cmd_record()` initializes symbol support, auxtrace options, default events when no event was requested, target maps, text-poke/off-CPU/tracking events, `record_opts`, and thread masks. It then calls `__cmd_record()`.

`__cmd_record()` installs signal handlers and initializes a `perf_tool` whose callbacks process samples, mmap events, task events, namespaces, aux/timestamp boundary events, and build-id mmap filtering. It creates `perf_session`, initializes zstd state, optionally creates a wakeup `eventfd`, checks kcore readability, initializes clock metadata, and prepares the workload when command arguments remain.

The recording setup phase uniquifies evsel names, configures evsels from `record_opts`, opens events with fallback/removal logic, maps mmap/AUX buffers, writes the initial header or pipe header, checks build-id feasibility, starts sideband event collection, synthesizes initial metadata, optionally raises scheduling priority, starts reader threads, enables events, starts the workload, applies initial delay and timed event-enable windows, marks triggers ready, and writes `PERF_RECORD_FINISHED_INIT`.

The main loop drains mmap buffers, handles overwrite-buffer state, auxtrace snapshot triggers, switch-output triggers, poll wakeups, fd errors/hangups, control-fd commands, event-enable timers, and final disabling. It breaks when `done` or draining state reaches a quiescent point. On exit it stops triggers, emits final BPF metadata, handles snapshot-on-exit, reports workload exec failures, writes final init/workload metadata, stops reader threads, drains buffers synchronously, synchronizes AIO, waits for the workload, writes off-CPU data, reads lost-sample counters, synthesizes tail metadata, finalizes or switches output, invokes record-end hooks, prints capture summary, closes sideband/eventfd/session state, and returns either recording error or workload exit status.

## State And Persistence Behavior

Persistent output is `perf.data`, a pipe stream, or a directory-form perf data layout when kcore or parallel streaming is enabled. `record__write()` and `record__finish_output()` maintain byte counters and header sizes so readers can locate data and features. In directory mode, individual mmap files receive samples and have independent file sizes recorded.

The file writes synthetic event records for reconstructing context later: kernel/module/user mmap events, comm/fork/exit/namespace/cgroup data, BPF metadata, CPU/thread maps, event attributes, id index, time conversion, auxtrace info, finished-init/finished-round markers, lost-sample records, optional off-CPU data, and optional kcore copies. Build IDs are either embedded in mmap2 events when supported, generated at the end by scanning the file, skipped, cached, or disabled for compression/switch-output performance depending on options.

Runtime state includes global `done`, signal state (`signr`, `child_finished`, optional `done_fd`), trigger objects for auxtrace snapshots and output switching, thread-local `record_thread *thread`, thread masks, per-thread counters, evlist control fd state, AIO control blocks, zstd stream state, sideband evlist state, and timestamp boundaries. Signal handlers set flags and use `eventfd` to wake blocking polls, then `record__sig_exit()` re-raises terminating signals after cleanup.

Switch-output persistence is timestamped. `record__switch_output()` finishes the current file, writes a timestamped file, resets session data size for the next file, rotates tracked filenames, and recreates initial tracking events for subsequent output files.

## Dependencies And Integration Points

The file depends heavily on perf internal subsystems:

- Event parsing/configuration: `parse-events`, `evlist`, `evsel`, `record_opts`, PMU/PFM helpers.
- Data/session/header: `perf_data`, `perf_session`, `perf_header`, feature bits, id headers, build-id cache.
- Ring buffers: `util/mmap`, `perf_mmap__push`, AUX trace mmap helpers, AIO support, zstd support.
- Target/topology: `target`, `cpumap`, `thread_map`, CPU/core/package/NUMA topology helpers, scheduler affinity.
- Synthetic events: `synthetic-events`, BPF, cgroup, namespace, task, time conversion, kernel/module/guest maps.
- Analysis compatibility: build-id and mmap event choices are designed for later `perf report`/`perf script` symbol resolution.
- External kernel/process APIs: `perf_event_open` through evsel helpers, `/proc/kcore`, `/proc/kallsyms`, `/proc/modules`, `eventfd`, `poll`, `pthread`, `sched_setaffinity`, signals, `wait`, file descriptors, and AIO.
- Optional build features: `HAVE_AIO_SUPPORT`, `HAVE_ZSTD_SUPPORT`, `HAVE_EVENTFD_SUPPORT`, `HAVE_LIBBPF_SUPPORT`, `HAVE_LIBPFM`, `HAVE_BPF_SKEL`, and architecture hook `arch__add_leaf_frame_record_opts()`.

Notable command integration points are `record_options` exported for shared perf code, `record_usage`, perf hook calls around record start/end and crash recovery, sideband BPF event collection, control-fd commands (`enable`, `disable`, `snapshot`, etc.), and auxtrace extension hooks.

## Risks And Edge Cases

- The recording loop is signal- and poll-sensitive. Without `eventfd` support, a signal that sets `done` just before a blocking poll may rely on later events or signals to wake the loop.
- Parallel streaming has many intentional exclusions: no pipe mode, no full AUX tracing, no AIO, no `--affinity`, no timestamp filename, no switch-output. Future option additions need to preserve these invariants.
- Event open fallback can remove evsels and reassign tracking. Bugs here can leave no non-dummy events, lose sideband tracking, or produce mismatched evsel indices.
- Build-id behavior is subtle: kernel support for build-id mmap events disables final build-id header generation; compression disables end-of-session build-id processing; switch-output defaults to disabling build-id cache unless explicitly overridden.
- AIO writes must handle partial writes, refcount mmap buffers correctly, and restore file offsets on errors. Compression must preserve perf record size alignment.
- Output switching has races with overwrite buffers and SIGUSR2/timer triggers; the loop explicitly rereads if a trigger lands around `record__mmap_read_all()`.
- Thread-mask parsing rejects empty and overlapping map/affinity masks, but relies on CPU topology data and `cpu__max_cpu()` bounds.
- Lost samples are synthesized after recording from counters and BPF filter state; mismatched fd/sample-id arrays skip lost-count reading.
- Off-CPU, cgroup, BPF, kcore, namespace, and AUX features are build- and kernel-capability dependent; user-visible errors should remain specific.
- Workload failure handling must distinguish recorder errors, child exit status, child signal termination, and exec failure passed through SIGUSR1.

## Test Signals

Useful verification points include:

- CLI parse and validation: incompatible option combinations, default target behavior, no-event default evlist, `--dry-run`, UID/cgroup/system-wide behavior.
- Event open fallback: weak groups, unsupported events, dummy-only failure, tracking event reassignment.
- Output behavior: normal file, pipe mode, directory mode, kcore copy, timestamp filename, switch-output by signal/size/time, `--switch-max-files`, and `--max-size`.
- Data integrity: final header sizes, feature bits, id index, finished-init/round markers, build-id generation/cache behavior, lost-sample records, timestamp boundary metadata.
- Runtime loops: SIGINT/SIGTERM/SIGCHLD, control fd stop/snapshot, event-enable timers, workload exec failure, initial delay, overwrite buffer draining.
- Optional paths: AIO enabled/disabled builds, zstd compression levels and ratios, auxtrace snapshot/sample/full modes, BPF sideband/final metadata, off-CPU synthesis.
- Parallel streaming: CPU/core/package/NUMA/user mask specs, per-thread files, detached reader startup/shutdown acknowledgements, pollfd mapping of non-perf descriptors, and rejection of unsupported options.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-report.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-report.c

## Purpose

`builtin-report.c` implements the `perf report` builtin. It reads a `perf.data` file or pipe, processes recorded perf events through a `perf_session`, resolves addresses to DSOs/symbols/source information, accumulates samples into histograms, and presents the result through stdio, TUI, GTK, stats, or task-map modes.

This file is the primary read-side counterpart to `builtin-record.c`: it interprets sample fields and metadata that record wrote, validates that requested reporting modes are supported by the file, and controls sorting, callchain, branch, memory, latency, time, and annotation behavior.

## Important APIs, Types, And Functions

Key local type:

- `struct report`: command state for the report run. It contains `perf_tool`, `perf_session`, event switch filters, UI mode flags, report modes (`mem`, `stats`, `tasks`, `mmaps`, header-only), branch/group/callchain/latency controls, display filters, sample counters, CPU/time filters, branch type stats, total cycles/block reporting state, and per-thread read values.

Important functions:

- `cmd_report()` is the builtin entry. It initializes hist/annotation/config state, parses options, opens a `perf_session`, configures callbacks and mode state, validates sorting/reporting requirements, initializes symbols/time filters/annotation support, and calls `__cmd_report()`. It also supports TUI reload or input-data switching by looping back to session creation.
- `report__config()` reads config keys such as `report.group`, `report.percent-limit`, `report.children`, `report.queue-size`, `report.sort_order`, and `report.skip-empty`.
- `process_sample_event()` is the main sample callback. It applies time, event-switch, CPU, and unresolved-symbol filters, resolves sample address locations, selects the proper hist iterator mode, accounts cycles/parallelism, and adds histogram entries.
- `hist_iter__report_callback()` and `hist_iter__branch_callback()` update per-symbol/address sample annotation counters and branch type stats as hist entries are added.
- `process_feature_event()` handles feature records, ends header-only pipe processing when the feature end marker is seen, and forces event leaders after feature delivery.
- `process_read_event()` accumulates `PERF_RECORD_READ` values for `--threads`.
- `report__setup_sample_type()` derives combined sample type, accounts for itrace-synthesized callchains/branches, validates requested parent/callchain/branch/memory modes, sets callchain parameters, disables impossible cumulative callchains, and handles LBR stitching constraints.
- `__cmd_report()` runs processing and output: optional CPU bitmap/read-values setup, mode-specific tool setup, session event processing, latency-column cancellation, mem-load aux checks, stats/tasks handling, kernel symbol warning, histogram collapse/sort, total-cycles block report setup, and browser/stdio output.
- `report__collapse_hists()` merges/resorts histograms, configures pipe-mode hierarchy formats, applies symbol/socket filters, and links group members to leaders when event grouping is active.
- `report__output_resort()` performs final output sorting and optional symbol IPC annotation preparation through `hists__resort_cb()`.
- `evlist__tty_browse_hists()`, `report__browse_hists()`, `report__gtk_browse_hists()`, and `evlist__tui_block_hists_browse()` select and drive presentation.
- `stats_setup()`/`stats_print()` implement `--stats`; `tasks_setup()`/`tasks_print()` implement task and mmap listing modes.
- `task_list_cmp()`, `thread_level()`, `task__print_level()`, and `maps__fprintf_task()` build a parent/child task tree and print recorded memory maps.
- Option parsers include `report_parse_callchain_opt()`, `parse_time_quantum()`, `report_parse_ignore_callees_opt()`, `parse_branch_mode()`, `parse_percent_limit()`, `report_parse_addr2line_config()`, and `process_attr()`.

## Control Flow

`cmd_report()` initializes histograms and keeps exited threads so task mode and off-CPU samples can reference threads that exited during capture. It initializes annotation options, applies config, parses CLI options, treats a leftover single positional argument as a symbol filter, copies disassembler/objdump/addr2line paths into global annotation/symbol state, validates annotation and symbol filters, chooses default input (`stdin` pipe or `perf.data`), and enters a repeatable session loop.

For each input session, it initializes `perf_data` in read mode, sets `symbol_conf.skip_empty`, initializes a `perf_tool` with ordered-event processing by default, and assigns callbacks for samples, mmap/mmap2, comm, namespace, cgroup, exit, fork, context switch, lost/read/attr/build-id/id-index/auxtrace/feature/update events. It creates `perf_session`, initializes event switching, initializes zstd decompression, applies ordered-event queue size, installs itrace synth options, detects branch-stack support, handles grouping, chooses branch/memory/callchain/data-type modes, selects UI mode, handles header/stats/tasks special cases, checks latency/parallelism requirements, sets up sorting fields, optionally prints header info, initializes annotation and symbols, parses time ranges, wires libtraceevent kernel address resolution, and calls `__cmd_report()`.

`__cmd_report()` installs SIGINT handling, configures CPU bitmaps and thread read-value storage, validates sample type requirements, swaps callback setup for stats/tasks modes, and processes all events through `perf_session__process_events()`. After event ingestion, it can cancel the Latency column for effectively single-threaded profiles, check memory load auxiliary data, return stats or task output, warn about restricted kernel symbol maps, count hist entries, optionally dump verbose session/DSO/raw trace data, collapse related hist entries, exit early if interrupted or no samples, resort output, construct total-cycles block reports, and browse/print hists.

When TUI browsing returns `K_SWITCH_INPUT_DATA` or `K_RELOAD`, `cmd_report()` deletes the session, resets callchain use for compatibility between files, and repeats session setup. Otherwise it tears down time ranges, block reports, zstd, session, annotation options, and generated sort help strings.

## State And Persistence Behavior

`perf report` primarily reads rather than writes persistent state. It mutates in-memory session state: machines, threads, maps, DSOs, evlists, hists, callchains, branch stats, read values, auxtrace-synthesized events, annotation data, time ranges, and UI browser state. Output is written to stdout or interactive UI; no new `perf.data` is persisted by this file.

The processing state is split between local `struct report`, global perf configuration objects (`symbol_conf`, `callchain_param`, `sort_order`, `field_order`, `annotate_opts`, `use_browser`, `dump_trace`, `quiet`, `verbose`), and session-owned structures. `session_done` is set by the SIGINT handler and by feature processing for header-only pipe mode.

The file persists derived display state only for the life of a run: histograms are filled during `perf_session__process_events()`, collapsed, then resorted for output. `show_threads_values` is allocated and later destroyed by stdio output. `block_reports` are allocated for total-cycles branch mode and freed during cleanup. Time ranges are parsed into `report.ptime_range`, also installed into itrace synth options, then cleared and freed.

## Dependencies And Integration Points

Major dependencies include:

- Perf session/data/event machinery: `perf_session__new/process_events/delete`, `perf_tool`, `perf_event__process_*`, `evlist`, `evsel`, ordered events, feature events, auxtrace, and zstd decompression.
- Symbolization and maps: `machine__resolve`, `thread`, `map`, `dso`, `symbol`, build-id processing, srcline, addr2line, kallsyms/vmlinux configuration, and kernel pointer restriction warnings.
- Hist/reporting stack: `hist`, `sort`, `callchain`, `branch`, `mem-info`, `mem-events`, `block-info`, `values`, `annotate`, and hpp formatting.
- UI stack: stdio output, TUI/SLang if built, GTK if built, progress bars, browser reload/input-switch keys, tips lookup from `TIPDIR`/`DOCDIR`.
- Itrace and auxtrace: synthetic callchain/branch additions, time-range propagation, auxtrace info/event processing.
- Optional libraries: libtraceevent for trace data and function resolver, libdw/libunwind for DWARF callchains and data-type profiling, dynamic GTK lookup through `dlsym`.

It integrates directly with record-time decisions: branch mode requires `PERF_SAMPLE_BRANCH_STACK` or itrace-added last branches; memory mode requires `PERF_SAMPLE_DATA_SRC` with an Arm SPE compatibility fix; latency/parallelism requires switch events from `perf record --latency`; parent/callchain sorting requires recorded or synthesized callchain data; build-id/map events determine symbol resolution quality.

## Risks And Edge Cases

- Several modes depend on sample bits that may be absent. `report__setup_sample_type()` rejects or silently disables impossible combinations, but changes to record defaults can affect report behavior.
- Pipe mode lacks full header information up front, so hierarchy formats and header-only feature processing have special handling.
- Branch mode is a tristate: default auto-enables when branch stacks are present unless branch call mode is active. This can surprise sort/callchain behavior and disables cumulative callchains.
- Memory mode and branch mode are mutually exclusive. Older Arm SPE files may lack `PERF_SAMPLE_DATA_SRC`; the file patches sample type for compatibility based on event names.
- Latency and parallelism reporting is disabled unless ordered switch events are available; `--disable-order` is incompatible with those columns and filters.
- Kernel symbol warnings depend on restricted `/proc/{kallsyms,modules}` and whether kernel maps were hit; warnings must avoid false confidence when addresses cannot be resolved.
- Task tree sorting recursively resolves parents; missing parent threads generate errors and fallback ordering, which can matter for malformed or incomplete data files.
- Annotation-related modes allocate extra symbol state and require external tooling/build support; data-type profiling fails without DWARF support.
- TUI reload/input switching must tear down session state and reset callchain assumptions to avoid stale settings between files.
- `symbol_ipc`, total-cycles block reporting, and annotation counters require per-address sample accounting, so callback changes can affect interactive annotation accuracy.

## Test Signals

Useful verification points include:

- Input selection and session creation: default `perf.data`, stdin pipe, forced input, invalid or compressed data, zstd initialization failure warning.
- Header modes: `--header`, `--header-only` on normal files and pipes, feature end-marker behavior.
- Sample-type validation: parent sort without callchains, `-g` without callchain/branch data, branch-stack mode without branches, memory mode without data source, Arm SPE compatibility.
- Sorting/filtering: `--sort`, `--fields`, hierarchy, event grouping, group-sort index validation, symbol/DSO/comm/pid/tid/cpu/time/parallelism filters, percent limits, skip-empty.
- Output modes: stdio, TUI, GTK, raw trace dump, stats, tasks, mmaps, show-threads read values, total-cycles block reports.
- Itrace paths: synthesized callchains, last branches, time-range propagation, LBR stitching warning.
- Symbolization: vmlinux/kallsyms/symfs/module options, restricted kernel pointer warnings, addr2line/objdump/disassembler path handling, demangling, inline names.
- Error and cleanup behavior: SIGINT/session_done, no-sample files, TUI reload/input switch, block report freeing, time range clearing, zstd/session deletion.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-report.c -->
