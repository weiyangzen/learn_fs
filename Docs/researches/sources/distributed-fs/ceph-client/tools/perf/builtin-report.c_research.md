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
