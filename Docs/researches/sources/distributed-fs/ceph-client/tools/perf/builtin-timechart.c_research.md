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
