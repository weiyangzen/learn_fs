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
