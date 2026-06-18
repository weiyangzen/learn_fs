<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/wakeup-latency.pl -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/wakeup-latency.pl
Purpose: Perl report script computing scheduler wakeup-to-switch latency statistics.

Important APIs/types/functions: `sched::sched_wakeup` records wakeup timestamp by target CPU; `sched::sched_switch` computes latency for the CPU's last wakeup; `trace_begin` initializes min/max; `trace_end` prints total, average, min, and max latency.

Control flow: Wakeup events store `nsecs(common_secs, common_nsecs)` in `%last_wakeup` keyed by target CPU. Switch events use the current CPU's stored timestamp, update total/min/max, increment wakeup count, and clear the timestamp. End processing prints stats and unhandled events.

State and persistence: `%last_wakeup`, min/max, total latency, wakeup count, and `%unhandled` live for one replay. No persistence beyond stdout.

Dependencies and integration points: Paired with `bin/wakeup-latency-record` and report wrapper. Uses `Perf::Trace::Util` for nanosecond arithmetic and average.

Risks: Matching wakeup by CPU only is approximate and can be overwritten by multiple wakeups before a switch. Initial min value is fixed at 1s and will print even if no wakeups occur. Requires sched tracepoint availability.

Test signals: Replaying sched wakeup/switch events should produce nonzero total wakeups and reasonable min/avg/max values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/wakeup-latency.pl -->
