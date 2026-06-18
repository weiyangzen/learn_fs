# sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_leader.bpf.c

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_leader.bpf.c

Purpose: this BPF program is the shared bperf leader. It reads one perf-event counter per CPU on scheduler switches or explicit test-run triggers and writes the latest delta into a per-CPU map for followers.

Important maps and programs: `events` is the perf-event array populated by user space with `BPF_F_PRESERVE_ELEMS`; `prev_readings` stores previous per-CPU readings; `diff_readings` stores current deltas. `on_switch` is a raw tracepoint program.

Control flow: on each invocation, `on_switch` uses the current CPU as the perf-event array key, reads the event value, subtracts the previous reading stored at key zero in per-CPU storage, writes counter/enabled/running deltas, and updates the previous reading.

State and persistence: previous and diff readings are per-CPU arrays and persist as long as the leader link exists. The leader program and maps can be shared through a pinned attr map and a bpf_link id held by user-space sessions.

Dependencies and integration: `bpf_counter.c` sizes `events`, attaches this program, stores link and diff-map ids, and opens perf-event fds. `bperf_follower.bpf.c` reuses `diff_readings`.

Risks: only one metric is handled by this skeleton instance; user space creates separate leaders by perf_event_attr. If `bpf_perf_event_read_value()` fails, no delta is produced. Initial deltas depend on zeroed previous readings and enable/follower semantics.

Test signals: verify leader reload, preserved perf-event array entries, per-CPU delta values, and explicit test-run refresh before reads.
