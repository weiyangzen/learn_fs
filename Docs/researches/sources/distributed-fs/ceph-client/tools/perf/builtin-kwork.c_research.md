# sources/distributed-fs/ceph-client/tools/perf/builtin-kwork.c

## Purpose

`builtin-kwork.c` implements `perf kwork`, a kernel work profiler for IRQ handlers, softirqs, workqueues, and scheduler activity. It can record the relevant tracepoints, report runtime totals, report raise-to-entry latency, print chronological time histories, and compute a top-like task CPU-usage view. Some report/top modes can also use BPF skeleton helpers when the build enables them.

## Important APIs, Types, and Functions

The central state object is `struct perf_kwork` from `util/kwork.h`. It owns the `perf_tool`, selected work classes, atom pages, comparison and sort lists, sorted output tree, profile filters, time window, CPU bitmap, report type, counters for lost and skipped events, and BPF integration hooks. `struct kwork_class` describes a supported work family with tracepoint names, class initialization, work identity extraction, and display-name generation. `struct kwork_work` is a per-work aggregate stored in RB trees. `struct kwork_atom` records individual raise/entry/exit timestamps; atoms are allocated from `struct kwork_atom_page` pools using a bitmap.

Important helpers include `setup_event_list()`, `setup_sorting()`, `sort_dimension__add()`, `work_findnew()`, `work_push_atom()`, `work_pop_atom()`, `profile_event_match()`, `perf_kwork__check_config()`, `perf_kwork__read_events()`, `perf_kwork__report()`, `perf_kwork__timehist()`, and `perf_kwork__top()`. Class-specific handlers map tracepoints to generic state transitions for IRQ, softirq, workqueue, and sched classes.

## Control Flow

`cmd_kwork()` initializes the static `perf_kwork`, registers mmap and sample callbacks, parses the subcommand, adds an `id` comparison for identity lookups, and dispatches. `record` selects default classes `irq, softirq, workqueue` unless overridden, then builds a `perf record -a -R -m 1024 -c 1` argv with each selected tracepoint as `-e`.

For offline reporting, `perf_kwork__read_events()` opens the input perf.data, initializes symbols, calls `perf_kwork__check_config()` to select operation handlers and register tracepoint handlers, parses CPU/time filters, validates callchain availability, optionally prints a timehist header, and processes the session. Tracepoint samples are routed through `perf_kwork__process_tracepoint_sample()` to the evsel handler installed by each class.

The runtime report path records entry atoms and consumes them on exit, updating total runtime, max runtime, and count. The latency path records raise atoms and consumes them on entry, updating total latency, max latency, and count. The timehist path records raise and entry atoms, resolves optional callchains at entry time, and prints one line when the matching exit is seen. The top path uses scheduler switch events as task runtime spans, also tracks irq/softirq runtime, subtracts interrupt time from task time where possible, computes per-CPU totals and idle/load ratios, merges tasks by PID except idle tasks remain per CPU, sorts by rate/runtime/tid, and prints CPU summaries plus task rows.

## State and Persistence Behavior

State is in memory only, except for perf.data written by the record subcommand. Atom pages are never individually freed during processing; atoms are returned to page bitmaps as transitions complete. Unmatched atoms left on work lists are counted as skipped events during output. The static `perf_kwork` is initialized once per process invocation and carries selected class list, sort list, profile filters, and counters through the selected subcommand.

BPF modes start a live trace, wait for a signal using `pause()`, finish tracing, read BPF maps into the same aggregate structures, and clean up BPF resources. Time filtering updates `timestart` and `timeend` only when summary mode is enabled.

## Dependencies and Integration Points

The file depends on perf data/session/event APIs, libtraceevent tracepoint field decoding, symbol and callchain resolution, RB tree/list/bitmap helpers, `util/kwork.h`, optional BPF skeleton functions, pager setup, and ordinary `cmd_record()`. It integrates with kernel tracepoints `irq:irq_handler_entry/exit`, `irq:softirq_raise/entry/exit`, `workqueue:workqueue_activate_work/execute_start/execute_end`, and `sched:sched_switch`.

## Risks and Edge Cases

State matching is tracepoint-order sensitive. Missing raise, entry, or exit events produce skipped atom counts and can bias runtime or latency. `work_push_atom()` can overwrite a previous unmatched atom and count it as skipped. Filtering by name is disabled for top until all task runtime is collected, so later merge/filter behavior must be correct. Work identity differs by report type: IRQ and softirq use interrupt IDs for most reports but common pid in top mode. Workqueue names depend on kernel-address resolution and may be null. The class objects are static and linked into lists; duplicate setup in an unusual reentrant invocation would be unsafe. BPF behavior depends on build support and runtime privileges.

## Test Signals

Good tests include record argv contents for default and explicit `--kwork`, runtime reports over synthetic irq/softirq/workqueue traces, latency reports with raise/entry pairs, skipped-event accounting for missing pairs, CPU/name/time filters, timehist with and without callchains, top reports with scheduler-only and scheduler-plus-interrupt traces, BPF report/top smoke tests where available, invalid sort and event names, lost-event summaries, and builds without BPF skeleton support.
