# Research Report: subset-b-006607

This grouped report covers three `tools/perf` builtin implementations from the Ceph client source snapshot. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-stat.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/builtin-stat.c

## Purpose

`builtin-stat.c` implements `perf stat`, plus the `perf stat record` and `perf stat report` subcommands. The command measures hardware, software, tool, metric, BPF, cgroup, I/O-stat, and topology-aware counter groups around a workload, an existing task/thread, or system-wide CPU targets. It is responsible for parsing the high-level CLI, choosing default event or metric groups, opening and reading counters, computing aggregation maps, handling repeated and interval runs, recording stat events into `perf.data`, and replaying recorded stat sessions.

The file sits at the boundary between user-facing `perf stat` behavior and the lower-level perf utility libraries. It does not implement raw perf-event syscalls directly in most places; it delegates event creation, maps, reads, metrics, output formatting, BPF counters, and perf-data synthesis to shared `util/` APIs.

## Important APIs, Types, and State

Key local types:

- `struct rusage_stats` holds `stats` objects for user and system time derived from `wait4()` rusage, used as fallback data for tool PMU time events when the measured process exits before normal counter reads succeed.
- `struct perf_stat` stores stat recording/report session state: `record`, `struct perf_data`, `struct perf_session *`, bytes written, `struct perf_tool` callbacks, maps, and aggregation mode chosen for report-side processing.
- `struct opt_aggr_mode` is a temporary CLI decoding structure for mutually independent aggregation flags such as socket, die, cache, core, thread, node, or no aggregation.
- `enum counter_recovery` models whether an event-open failure should skip the event or retry after a fallback adjustment.

Important globals:

- `evsel_list` is the process-wide event list for this command.
- `stat_config` is the shared perf stat configuration defined outside this file and populated by CLI parsing.
- `target` captures `-a`, `-p`, `-t`, `-C`, BPF program targets, inheritance, and enable-on-exec behavior.
- `perf_stat` stores record/report state and is also statically initialized later for report mode defaults.
- `child_pid`, `done`, `signr`, and `workload_exec_errno` coordinate signal handling and workload lifecycle.
- `metrics`, `pre_cmd`, `post_cmd`, `sync_run`, `forever`, `append_file`, `output_name`, and `output_fd` hold parsed command behavior.
- `smi_cost` and `smi_reset` track temporary writes to `FREEZE_ON_SMI_PATH`.
- `all_counters_use_bpf` is optimized around bperf/BPF counter mode; it suppresses non-BPF reads/enables when every selected event is BPF-backed.

Important helper families:

- Counter reads: `read_single_counter()`, `read_counter_cpu()`, `read_counters_with_affinity()`, `read_bpf_map_counters()`, `read_tool_counters()`, `read_counters()`.
- Counter processing and output: `process_counters()`, `process_interval()`, `print_counters()`.
- Counter creation and failure recovery: `create_perf_stat_counter()`, `stat_handle_error()`, weak-group retry logic in `__run_perf_stat()`.
- Runtime control: `enable_counters()`, `disable_counters()`, `dispatch_events()`, `process_evlist()`, `handle_interval()`.
- Aggregation: `perf_stat_init_aggr_mode()`, `perf_stat__exit_aggr_mode()`, cache topology helpers, `aggr_mode__get_aggr()`, `aggr_mode__get_id()`, and report-side `*_file` variants that derive IDs from recorded `perf_env`.
- Defaults and metrics: `add_default_events()`, `append_metric_groups()`, `parse_cputype()`, `parse_pmu_filter()`, `parse_cache_level()`, `parse_tpebs_mode()`.
- Record/report: `__cmd_record()`, `init_features()`, `process_synthesized_event()`, `evsel__write_stat_event()`, `process_stat_config_event()`, `process_stat_round_event()`, `process_thread_map_event()`, `process_cpu_map_event()`, `__cmd_report()`.

## Control Flow

`cmd_stat()` is the entry point. It initializes locale and `evsel_list`, builds a large option table, parses normal commands and `record`/`report` subcommands, maps aggregation flags into `stat_config.aggr_mode`, normalizes CSV and output settings, validates incompatible options, and validates the target. It then determines whether system-wide mode should be implicit with `setup_system_wide()`.

For normal `perf stat`, control flow is:

1. Parse and validate output, interval, timeout, repeat, cgroup, metric, BPF, iostat, aggregation, and target options.
2. Parse delayed metric groups with `metricgroup__parse_groups()` once the target mode is known.
3. Add default metrics/events with `add_default_events()` when no events were requested, or when detailed, transaction, topdown, or SMI modes ask for specific metric groups.
4. Expand cgroup events if `--for-each-cgroup` was used, warn about requested CPUs, and force CPU maps for BPF counters that cannot run on CPU `-1`.
5. Create CPU/thread maps with `evlist__create_maps()`, sanitize grouped-event CPU maps with `evlist__check_cpu_maps()`, initialize thread comms for `--per-thread`, and initialize NUMA data when needed.
6. Initialize aggregation maps and allocate stats/raw-count storage.
7. Install signal handlers and control-fd handling.
8. Run `run_perf_stat()` for each repeat iteration, resetting previous raw counts between runs.
9. Print the final summary unless interval-only output suppresses it.
10. Finalize control fd, write stat-record tail events and headers if recording, clean aggregation maps/stats, restore SMI sysfs state if changed, and delete the evlist.

`run_perf_stat()` optionally executes `pre_cmd`, calls `sync()`, delegates the measurement to `__run_perf_stat()`, and optionally executes `post_cmd`.

`__run_perf_stat()` is the measurement core. If a command workload is present, `evlist__prepare_workload()` forks/prepares it but delays exec until counters are configured. It loads BPF counters, opens non-BPF perf events per CPU/thread, retries weak groups in a second pass when group-open constraints fail, stores IDs for record/group reads, writes perf-data headers/stat config for record mode, enables counters immediately or after `target.initial_delay`, starts the workload, waits through `dispatch_events()`, disables counters, stores walltime/rusage stats, reads final counts, processes counters, and closes the evlist for non-record mode.

`dispatch_events()` multiplexes target lifetime, workload lifetime, interval timers, timeout, and control-fd events. It polls the evlist with a dynamic sleep time, periodically calls `process_interval()`, reacts to control commands by printing interval snapshots on enable/disable transitions, and stops when the child exits, an attached target disappears, a timeout occurs, interval count is exhausted, or a signal sets `done`.

`process_interval()` reads counters, processes them, writes a `PERF_STAT_ROUND_TYPE__INTERVAL` event when recording, updates walltime stats with the configured interval length, and prints an interval snapshot. Final output uses `print_counters()` which delegates to `evlist__print_counters()`.

For `perf stat record`, `__cmd_record()` parses stat options in record context, creates a writable `perf_session`, enables all applicable header features except irrelevant ones, marks `perf_stat.record`, and lets the normal run path synthesize stat events into the data file. It rejects repeat/forever because the record format path expects a single run.

For `perf stat report`, `__cmd_report()` opens a `perf.data` input, installs `perf_tool` callbacks for attributes, event updates, maps, stat config, stat values, and stat-round markers, replaces the global `evsel_list` with the session evlist, and replays events with `perf_session__process_events()`. `process_stat_config_event()` rebuilds stat config and aggregation maps from either pipe-local maps or recorded `perf_env`; `process_stat_round_event()` processes accumulated counts and prints snapshots.

## State and Persistence Behavior

Most state is in memory and tied to one invocation. Counter values live in `evsel->counts`, previous raw counts, aggregation stats, and metric/event structures owned by the evlist. Repeat and interval modes update `stat_config.walltime_nsecs_stats`, `walltime_run`, and rusage-derived stats across runs.

Persistence happens in three places:

- Optional text/JSON/CSV output goes to stderr, `--output`, or `--log-fd`.
- `perf stat record` persists stat-specific perf events, stat config, CPU/thread maps, attributes, and synthesized kernel mmap/header records into `perf.data` or a pipe.
- SMI cost mode writes to `bus/event_source/devices/cpu/freeze_on_smi` and records `smi_reset` so it can restore the sysfs knob to `0` at exit if this invocation enabled it.

The command also uses process signals as state transitions. `skip_signal()` sets `done`, captures the signal number, and clears `child_pid` to avoid killing a recycled PID. `sig_atexit()` blocks `SIGCHLD`, terminates a still-live child, restores the default signal handler, and re-raises the captured signal.

## Dependencies and Integration Points

This file depends heavily on the perf userspace library stack:

- Event parsing and event lists: `util/parse-events.h`, `util/evlist.h`, `util/evsel.h`, libperf `perf/evlist.h`.
- Metrics/topdown: `util/metricgroup.h`, `util/topdown.h`, `util/intel-tpebs.h`.
- Stats and output: `util/stat.h`, `util/counts.h`, `util/color.h`, `util/iostat.h`.
- Targets and maps: `util/target.h`, `util/cpumap.h`, `util/thread_map.h`, `internal/threadmap.h`.
- Perf data/session: `util/session.h`, `util/header.h`, `util/synthetic-events.h`, `util/tool.h`.
- BPF counters: `util/bpf_counter.h`, optional generated `bperf_cgroup` skeleton.
- Topology and sysfs/procfs helpers: `api/fs/fs.h`, `cpu__setup_cpunode_map()`, cache map builders, `sysfs__read_int()` and `sysfs__write_int()`.
- Optional libpfm event parsing via `parse_libpfm_events_option`.

Important integration contracts include `perf_stat_process_counter()`, `perf_stat_merge_counters()`, `perf_stat_process_percore()`, `evlist__print_counters()`, and the stat config serialization/deserialization used by `perf_event__synthesize_stat_events()` and `perf_event__read_stat_config()`.

## Risks and Edge Cases

- `update_rusage_stats()` names fields as usec stats but stores nanosecond values; consumers must treat the stored unit consistently with tool PMU events.
- `dispatch_events()` combines child wait, target liveness, control-fd polling, interval output, and timeout. Changes here can regress short-lived workloads, attached target termination, or interval-count semantics.
- Weak group fallback is deliberately deferred to a second pass because mixed group/non-group reads across CPUs are not supported. Reordering open/close behavior risks skew or kernel read-format mismatches.
- `evlist__check_cpu_maps()` silently removes mismatched members from groups after warnings. This prevents invalid groups but can surprise metrics that assume group semantics.
- SMI cost mode mutates a sysfs knob. Early exits must continue to run cleanup that restores `freeze_on_smi`.
- `perf stat record` uses special stat events and headers that older tools may partially understand; the kernel mmap record is synthesized mainly to avoid misleading warnings.
- Aggregation IDs come from live topology in normal mode and recorded `perf_env` in report mode. Cache, die, cluster, and NUMA behavior depends on complete topology data.
- BPF counter paths intentionally skip standard reads/enables when all events are BPF-backed. Mixed BPF/non-BPF event sets must keep `all_counters_use_bpf` correct.
- Option incompatibility checks are user-visible API. `--metric-only` with repeat or per-thread, timeout with interval, cgroup/no-aggregation without system-wide mode, and bad interval-count usage all have explicit failures.

## Test Signals

Useful validation signals for this file include:

- `perf stat true`, `perf stat -e cycles,instructions true`, and unsupported-event cases for default/open/fallback paths.
- `perf stat -I 100 --interval-count 2 sleep 1` for interval snapshots and stop condition.
- `perf stat --timeout 100 sleep 10` for timeout kill/wait behavior.
- `perf stat -r 3 --table true` for repeat statistics and walltime table allocation.
- `perf stat -a -A`, `--per-socket`, `--per-core`, `--per-cache`, `--per-node`, and `--per-thread` for aggregation maps.
- `perf stat -M <metric>` and `--topdown` on supported PMUs for metric parsing/default event insertion.
- `perf stat record -o perf.data true` followed by `perf stat report -i perf.data` for stat event persistence and replay.
- `perf stat --control fd:...` for control-fd enable/disable/snapshot interactions.
- BPF/cgroup/iostat builds should cover `--bpf-counters`, `--for-each-cgroup`, and `--iostat` where supported by the kernel and build config.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-timechart.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/builtin-timechart.c

## Purpose

`builtin-timechart.c` implements `perf timechart`, a command that records or reads trace data and renders an SVG timeline of CPU activity, task scheduling, power states, wakeups, and optionally I/O activity. The file has two major roles: constructing `perf record` argument vectors for `perf timechart record`, and replaying an existing `perf.data` file into in-memory timelines that are drawn through `util/svghelper.h`.

The implementation is tracepoint-driven. It maps selected tracepoint names to local handlers, extracts fields with `evsel__intval()`, updates local process/power/I/O structures, then emits an SVG whose rows are CPUs or tasks and whose bars represent scheduling, P/C states, wakeup paths, or syscall durations.

## Important APIs, Types, and State

Core data structures:

- `struct timechart` owns the `perf_tool`, linked lists of process data, power events, and wake events, CPU count, min/max/turbo frequencies, first/last timestamps, display mode flags, force flag, I/O mode settings, event counts, and visualization thresholds.
- `struct per_pid` represents a kernel task identity, including pid, ppid, start/end times, aggregate running time, aggregate I/O bytes, display flag, and a list/current pointer for command names.
- `struct per_pidcomm` tracks one command name used by a pid across exec boundaries, with CPU samples, I/O samples, accumulated runtime and bytes, display row, current scheduling state, and state start timestamp.
- `struct cpu_sample` is a sched-state interval for one task: running, waiting, or blocked on a CPU, with optional backtrace text.
- `struct io_sample` is a syscall interval for read/write/sync/network/poll operations, including fd, return/error, byte count, and merge count.
- `struct power_event` stores C-state or P-state intervals per CPU.
- `struct wake_event` stores wakeup relationships, timestamps, and optional backtrace text.
- `struct process_filter` stores user filters by name or numeric pid.

Important global arrays:

- `cpus_cstate_start_times` and `cpus_cstate_state` track currently open C-state intervals by CPU.
- `cpus_pstate_start_times` and `cpus_pstate_state` track currently open P-state intervals by CPU.
- The arrays are sized to `MAX_CPUS` (`4096`) and allocated in `cmd_timechart()`.
- `use_old_power_events` is compiled under `SUPPORT_OLD_POWER_EVENTS` and selects legacy power tracepoints when modern ones are unavailable.

Important helper groups:

- Process model: `find_create_pid()`, `create_pidcomm()`, `pid_set_comm()`, `pid_fork()`, `pid_exit()`, `pid_put_sample()`.
- Scheduling and power handlers: `c_state_start()`, `c_state_end()`, `p_state_end()`, `p_state_change()`, `sched_wakeup()`, `sched_switch()`.
- Tracepoint dispatch: `process_sample_event()` and `process_sample_*()` callbacks for power, sched, syscall enter, and syscall exit events.
- Backtrace formatting: `cat_backtrace()`.
- I/O tracking: `pid_begin_io_sample()`, `pid_end_io_sample()`, enter/exit handlers for disk, network, sync, and poll syscalls.
- Display selection and SVG: `sort_pids()`, `determine_display_tasks*()`, `draw_c_p_states()`, `draw_wakeups()`, `draw_cpu_usage()`, `draw_io_bars()`, `draw_process_bars()`, `write_svg_file()`.
- Record command construction: `timechart__record()` and `timechart__io_record()`.

## Control Flow

`cmd_timechart()` initializes default display state (`proc_num = 15`, `min_time = 1ms`, `merge_dist = 1000ns`), declares normal and record-specific options, allocates CPU state arrays, parses options/subcommands, validates mutually exclusive `--power-only` and `--tasks-only`, and either delegates to a recording path or renders an SVG from input.

For `perf timechart record`, the command does not record directly. It builds a synthetic argv and calls `cmd_record()`:

- `timechart__record()` records scheduling and power tracepoints with common args `record -a -R -c 1 -o <data>`. It can add `-g` for callchains. It omits task tracepoints for `--power-only`, omits power tracepoints for `--tasks-only`, and falls back from `power:cpu_idle/cpu_frequency` to old `power:power_*` tracepoints when needed.
- `timechart__io_record()` records syscall enter/exit tracepoints for disk, network, and polling operations. It validates tracepoint availability with `is_valid_tracepoint()`, filters out the current perf process with `common_pid != getpid()`, and calls `cmd_record()`.

For rendering, `cmd_timechart()` calls `setup_pager()` and then `__cmd_timechart()`.

`__cmd_timechart()` creates a `perf_data` reader and ordered `perf_tool`, installs callbacks for comm/fork/exit/sample events, opens a `perf_session`, initializes symbols, processes header sections to learn CPU count and optional topology map, verifies trace availability, attaches tracepoint handlers with `perf_session__set_tracepoints_handlers()`, and replays events with `perf_session__process_events()`. After replay it closes open P-state intervals with `end_sample_processing()`, sorts pids, writes the SVG, prints a summary, and deletes the session.

During sample replay, `process_sample_event()` updates `first_time` and `last_time` from sample timestamps, then invokes the event-specific handler attached to the `evsel`. Event-specific handlers decode trace fields by name:

- `power:cpu_idle` starts or ends C-state intervals depending on `state == PWR_EVENT_EXIT`.
- `power:cpu_frequency` ends the previous P-state interval and starts a new one, tracking min/max/turbo frequency.
- `sched:sched_wakeup` records a wakeup edge and transitions the wakee from blocked to waiting when appropriate.
- `sched:sched_switch` closes the previous task's running interval, closes the next task's waiting/blocked interval, marks next as running, and marks previous as waiting or blocked based on `prev_state`.
- Syscall enter handlers start an `io_sample`; syscall exit handlers close it, stretch it to a minimum visual duration, adjust overlaps, record errors/bytes, and merge nearby compatible samples.

Finally, `write_svg_file()` chooses which tasks to display. If filters were provided, only matching pids/comms are displayed. Otherwise it lowers runtime or byte thresholds until at least `proc_num` rows are visible. I/O mode renders I/O bars and an I/O legend; normal mode renders CPU boxes, CPU usage, optional task bars, optional C/P-state bars, and wakeup lines.

## State and Persistence Behavior

All analysis state is in memory. The replay model is linked-list based and append-prepends most samples/events, then drawing functions traverse those lists. There is no on-disk intermediate format beyond the input `perf.data` and output SVG. `perf timechart record` persists trace samples by invoking the regular `perf record` machinery.

The time bounds `first_time` and `last_time` are global for the chart. Missing task end times are filled with `last_time`; special `start_time == 1` values are normalized to `first_time`. P-state intervals are closed at the end for every CPU up to `numcpus`; C-state closeout is present but disabled under `#if 0`, so C-state bars rely on explicit exit samples.

Backtraces are stored as heap strings returned by `cat_backtrace()` and referenced from CPU/wakeup samples. The command frees the CPU state arrays before exit but does not deeply free all timeline lists; this is acceptable for a short-lived CLI but relevant for leak-checking tests.

## Dependencies and Integration Points

Main dependencies:

- Perf sessions/tools/events: `util/session.h`, `util/tool.h`, `util/event.h`, `util/header.h`, `util/data.h`.
- Tracepoint APIs: `util/tracepoint.h`, `event-parse.h`, `evsel__intval()`, `perf_session__set_tracepoints_handlers()`.
- Symbol/callchain support: `util/symbol.h`, `util/thread.h`, `util/callchain.h`, `machine__resolve()`, `thread__find_symbol()`.
- SVG rendering: `util/svghelper.h`, including `open_svg()`, `svg_time_grid()`, `svg_legenda()`, `svg_cpu_box()`, `svg_process()`, state bars, I/O boxes, wake lines, topology map helpers, and highlight globals.
- CLI handling: `subcmd/parse-options.h`, pager setup, and symbol filesystem config.
- Recording integration: direct calls into `cmd_record()` with constructed argv vectors.

The file depends on tracepoint field names such as `state`, `cpu_id`, `common_flags`, `common_pid`, `pid`, `prev_pid`, `next_pid`, `prev_state`, `fd`, and `ret`. Kernel tracepoint ABI changes or missing syscalls affect both recording and replay.

## Risks and Edge Cases

- CPU arrays are fixed at `MAX_CPUS` and handlers trust tracepoint CPU IDs. Systems or malformed data with CPU IDs >= 4096 can index out of bounds.
- `end_sample_processing()` loops `cpu <= tchart->numcpus`, which includes one slot past the nominal CPU count if `numcpus` is a count rather than max index.
- Several allocations use `assert()` or return without full cleanup. In production builds where asserts are disabled, allocation assumptions can become null dereferences.
- `timechart__io_record()` reuses one allocated `filter` string pointer across many argv positions and does not free duplicated strings after `cmd_record()`. This is fine for process lifetime but noisy under leak checkers.
- `passes_filter()` calls `strcmp(filt->name, c->comm)` without a local null check for `c->comm`. Many paths set comms, but incomplete traces could expose null names.
- I/O matching is stack-like per `per_pidcomm`; overlapping or nested syscall events for the same task can be dropped or warned as invalid.
- C-state finalization is disabled, so open idle intervals without exit events are not drawn to the chart end.
- Old power tracepoint support is compile-time and dynamically selected, so tests must cover kernels with both new and legacy tracepoints when possible.
- SVG output quality depends on thresholds, min visual duration, and merge distance; changing these can drastically alter perceived behavior without changing underlying data.

## Test Signals

Useful validation signals include:

- `perf timechart record sleep 1` followed by `perf timechart -i perf.data -o output.svg` for normal sched/power flow.
- `perf timechart record -T` and `perf timechart record -P` to verify mutually exclusive task/power event selection.
- `perf timechart record -I` plus rendering to verify syscall enter/exit matching, byte totals, EAGAIN skipping, min-time stretching, and merge-distance behavior.
- `perf timechart --process <pid-or-comm>` to exercise display filtering.
- `perf timechart --highlight <duration-or-name>` to exercise SVG highlight globals.
- Rendering a perf.data with callchains recorded by `-g` to validate `cat_backtrace()` and symbol resolution.
- Header-driven topology tests with `--topology`.
- Negative tests for no trace data, missing tracepoints, conflicting `-P -T`, and invalid `--io-min-time`/`--io-merge-dist` units.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-timechart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-top.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/builtin-top.c

## Purpose

`builtin-top.c` implements `perf top`, the live interactive profiler that continuously samples one or more perf events, resolves samples to symbols, aggregates them in histograms, and refreshes either a stdio or TUI display. It combines record-like event setup with report-like symbol, callchain, annotation, sorting, filtering, and browser functionality, but it runs continuously against mmap ring buffers instead of processing a completed `perf.data` file.

The file owns command-line parsing, default event setup, target/map creation, counter opening/mmap setup, live sample ingestion, ordered event processing, display threads, keyboard controls, source annotation updates, and cleanup.

## Important APIs, Types, and State

Most command state is stored in `struct perf_top`, defined in shared headers and initialized in `cmd_top()`. Fields used heavily here include:

- `evlist`, `session`, `tool`, and optional `sb_evlist` for the main event set and side-band BPF events.
- `record_opts`, including target, mmap pages, sampling frequency/period, overwrite mode, branch stack settings, namespace/cgroup tracking, and BPF event settings.
- Display controls such as `delay_secs`, `print_entries`, `winsize`, `min_percent`, `count_filter`, `zero`, `use_tui`, `use_stdio`, and hide-user/kernel flags.
- Annotation controls including `sym_filter`, `sym_filter_entry`, `sym_evsel`, `max_stack`, `stitch_lbr`, and vmlinux warning state.
- Sample/loss/drop counters such as `samples`, `kernel_samples`, `us_samples`, `guest_*`, `exact_samples`, `lost`, `lost_total`, `drop`, and `drop_total`.
- Ordered-event queue state `qe`, with two `ordered_events` buffers, a mutex, condition variable, input queue pointer, and rotate flag.

Local globals:

- `done` ends collection/display.
- `resize` records `SIGWINCH` events for terminal resize handling.
- `last_timestamp` tracks the newest sample timestamp seen by mmap reading and drives stale-event dropping.

Important function groups:

- Display sizing and stdio output: `perf_top__update_print_entries()`, `winch_sig()`, `perf_top__resize()`, `perf_top__print_sym_table()`, `perf_top__resort_hists()`.
- Annotation and source view: `perf_top__parse_source()`, `__zero_source_counters()`, `ui__warn_map_erange()`, `perf_top__record_precise_ip()`, `perf_top__show_details()`.
- Interactive key handling: prompt helpers, `perf_top__print_mapped_keys()`, `perf_top__key_mapped()`, `perf_top__handle_keypress()`.
- Threads: `display_thread_tui()`, `display_thread()`, `process_thread()`, `init_process_thread()`, `exit_process_thread()`.
- Sample processing: `perf_event__process_sample()`, `hist_iter__top_callback()`, lost-event handlers, `deliver_event()`.
- Ring-buffer reading: `perf_top__mmap_read_idx()`, `perf_top__mmap_read()`.
- Counter setup: `perf_top__overwrite_check()`, `perf_top_overwrite_fallback()`, `perf_top__start_counters()`.
- Entry point and option setup: `cmd_top()`, `__cmd_top()`, config and callchain parsers.

## Control Flow

`cmd_top()` is the entry point. It initializes histogram and annotation subsystems, creates an evlist, loads config via `perf_config()`, captures host environment and CPUID for annotation, parses a large option table, validates symbol/annotation/target arguments, defaults to system-wide mode if no target is provided, creates default events when the user did not provide `-e`, initializes event switching, resolves incompatible hierarchy/fields and LBR/callchain combinations, configures branch/callchain behavior, sets sort mode to top, chooses stdio or TUI browser mode, creates an in-memory `perf_session`, sets up sorting and uid filters, creates CPU/thread maps, configures record options, initializes symbol/annotation support, creates optional BPF side-band events, starts the side-band thread, and then calls `__cmd_top()`.

`__cmd_top()` performs runtime setup:

1. Resolve `objdump` if annotation needs it.
2. Register callchain parameters when enabled.
3. Register the idle thread and enable multithreaded mode for thread synthesis.
4. Initialize the ordered-event processing queues.
5. Configure namespace/cgroup event processing flags.
6. Synthesize existing BPF, cgroup, and thread metadata into the session.
7. Read CPU topology when socket output requires it.
8. Uniquify event names and open/mmap counters with `perf_top__start_counters()`.
9. Set ID header sizes and enable events for non-empty targets.
10. Start the processing thread and a display thread.
11. Optionally set realtime scheduling priority.
12. Poll once, read initial mmap data, then loop reading mmaps and polling until `done`.
13. Join display and process threads, restore single-threaded mode, and release ordered-event queues.

`perf_top__start_counters()` applies record options to the evlist, checks that all events agree on overwrite mode, opens each evsel, handles overwrite fallback if `write_backward` is unsupported, applies generic evsel fallbacks, applies filters, and mmaps the evlist.

The data path starts in `perf_top__mmap_read()`. For overwrite mode it toggles backward mmap state, then iterates each mmap and calls `perf_top__mmap_read_idx()`. That function initializes mmap reading, reads raw events, parses timestamps into `last_timestamp`, queues copied events into the current ordered-events input queue, consumes mmap data, and coordinates queue rotation with the processing thread.

`process_thread()` watches the active queue. When events are available, it swaps input queues with `rotate_queues()`, asks the reader to stop using the old queue through a condition variable handshake, and flushes the old queue with `ordered_events__flush(..., OE_FLUSH__TOP)`. `deliver_event()` is the ordered-events callback.

`deliver_event()` drops stale sample events that are more than `delay_secs` behind `last_timestamp`, parses samples, maps sample IDs to evsels, applies event switching, increments counters by CPU mode, chooses the host or guest machine, honors hide-user/kernel flags, dispatches samples to `perf_event__process_sample()`, accounts lost events, or passes metadata events to `machine__process_event()`.

`perf_event__process_sample()` resolves the sample to an address location, handles guest/missing-machine cases, warns about restricted kernel symbols or missing vmlinux data, enables LBR stitching on the thread when requested, and adds the sample to the evsel histograms under the hists lock via `hist_entry_iter__add()`. The add-entry callback records precise IP data for annotation and accounts branch cycles.

Display has two modes:

- `display_thread()` is the stdio mode. It unshares `CLONE_FS` for namespace symbol access, installs signal handlers, sets quiet terminal input, repeatedly prints the symbol table, polls stdin for keypresses, and applies interactive changes such as delay, entry count, active event, filters, hide flags, symbol annotation, and zeroing.
- `display_thread_tui()` is the TUI mode. It repeatedly resorts hists, sets uid filters, calls `evlist__tui_browse_hists()`, handles reload by zeroing, and stops the profiler on exit.

`perf_top__resort_hists()` decays or deletes entries when events are enabled depending on `zero`, collapses hists, matches group members to leaders, and output-resorts each evsel. `perf_top__print_sym_table()` clears the console, prints the top header, warns on newly observed lost chunks, and either shows annotation details or recalculates column widths and prints histogram rows.

## State and Persistence Behavior

`perf top` is intentionally live and does not write a normal `perf.data` file from this implementation. Persistent effects are limited to terminal display, optional symbol/annotation subprocess/tool lookups, and live perf-event kernel state while counters are open. Runtime state lives in:

- Kernel perf_event fds and mmap buffers owned by evsels/evlist.
- In-memory histograms under each evsel.
- In-memory symbol, map, DSO, machine, cgroup, namespace, BPF, and thread metadata in `perf_session`.
- Two copied ordered-event queues used to decouple mmap reading from event processing.
- Terminal state managed by `set_term_quiet_input()`/`tcsetattr()` in stdio display mode.

The command can start side-band BPF event collection through `sb_evlist`; this is stopped after `__cmd_top()` unless BPF events were disabled. Display-thread signal handlers set `done`/`session_done` rather than directly tearing down counters.

## Dependencies and Integration Points

Major dependencies:

- Event setup and mmap: `util/evlist.h`, `util/evsel.h`, `util/evsel_config.h`, `util/mmap.h`, libperf `perf/mmap.h`, `record_opts__config()`.
- Session/machine/symbols: `util/session.h`, `util/machine.h`, `util/map.h`, `util/dso.h`, `util/symbol.h`, `util/synthetic-events.h`.
- Histograms/report UI: `util/top.h`, `util/sort.h`, `util/annotate.h`, `ui/ui.h`, TUI browser APIs, hists and hist-entry iteration.
- Callchains and branches: `util/callchain.h`, `util/parse-branch-options.h`, LBR stitching support, branch cycle accounting.
- Targets, cgroups, uid filters, namespaces, BPF metadata: `util/cgroup.h`, `util/bpf-event.h`, `util/intlist.h`, `evswitch`.
- CLI/config: `subcmd/parse-options.h`, `perf_config()`, `perf_default_config()`, annotation config helpers.
- Platform helpers: `arch/common.h`, `dwarf-regs.h`, `sysctl__max_stack()`, scheduler/terminal/signal syscalls.

The file integrates with both record-style configuration and report-style presentation. This makes option interactions delicate: changing defaults or record options can affect mmap setup, sample IDs, sorting fields, annotation, callchains, and UI output at the same time.

## Risks and Edge Cases

- `done`, `resize`, and `last_timestamp` are shared across threads with minimal synchronization. Existing design relies on simple signal-safe flags and queue synchronization; deeper changes must avoid races with mmap reading and event flushing.
- Ordered queue rotation uses a condition-variable handshake between the reader and process thread. If the rotate flag or signal order changes, the processing thread can stall or read from a queue still being appended.
- `should_drop()` drops samples older than `delay_secs` relative to the newest timestamp. This protects interactivity but can bias output under heavy load.
- Overwrite mode must be consistent across all events. Mixed per-event overwrite terms are rejected; fallback from overwrite to non-overwrite only happens when the first event reveals missing kernel support.
- Annotation updates lock per-symbol annotations while hists locks may also be held. `perf_top__record_precise_ip()` explicitly unlocks hists before sleeping on warnings; lock-order changes are risky.
- Missing or restricted kernel symbols are warned lazily on first unresolved kernel samples. This means tests must trigger actual samples to cover those paths.
- Stdio mode manipulates terminal attributes and must restore them on exits from key handling, signal paths, and normal shutdown.
- TUI and stdio display paths share histogram state but have different refresh mechanics; changes to resorting/zeroing must preserve both.
- `target__none()` defaults to system-wide mode, so permission failures are common on restrictive kernels and should produce clear errors through `evsel__open_strerror()`.
- BPF side-band setup is optional and best-effort; failures should not prevent profiling, but they reduce BPF symbol resolution.

## Test Signals

Useful validation signals include:

- `perf top --stdio -d 1 -E 5` or a short controlled run under a timeout wrapper to exercise stdio refresh and counter setup.
- `perf top -e cycles`, grouped events, and invalid/unsupported events for open fallback and error messages.
- `perf top --overwrite` on kernels with and without backward mmap support to validate fallback.
- `perf top -p <pid>` and `perf top -a -C <cpu>` to validate target maps.
- Interactive stdio keys: `d`, `e`, `E`, `f`, `F`, `K`, `U`, `s`, `S`, `z`, and `q`.
- `perf top --tui` where slang support is built, to cover TUI browse/reload behavior.
- `perf top -g`, `--call-graph`, `--children`, branch options, and `--stitch-lbr` to cover callchain/branch validation and histogram accounting.
- `perf top --sym-annotate <symbol>`, `--objdump`, and `--addr2line` for annotation initialization and source counters.
- `--uid`, `--cgroup`, `--all-cgroups`, `--namespaces`, and BPF-event paths where kernel/build support exists.
- Heavy sampling or constrained mmap pages to trigger lost/drop warnings and stale-event dropping.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-top.c -->
