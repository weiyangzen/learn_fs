# sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_follower.bpf.c

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_follower.bpf.c

Purpose: this BPF program is the per-session follower for shared bperf counters. Attached as fexit to the shared leader, it filters each leader delta by global/CPU/PID/TGID scope and accumulates matching deltas into the session's map.

Important maps and globals: `diff_readings` is reused from the leader, `accum_readings` is the per-session per-filter accumulator, and `filter` maps CPU/pid/tgid keys to accumulator indexes plus exit state. BSS globals `type`, `enabled`, and `inherit` control behavior.

Control flow: `fexit_XXX()` exits unless enabled, chooses a filter key from current CPU or pid/tgid, looks up `filter`, optionally deletes exited entries, reads leader delta key 0, and adds it to `accum_readings[accum_key]`. `on_newtask()` inherits PID/TGID filter membership from parent tasks into children. `on_exittask()` marks pid filter entries as exited so the fexit path can delete them after final accounting.

State and persistence: filter rows and accumulated readings live for the session. Mark-then-delete exit state avoids racing final counts. Inherited children share the parent's accumulator key.

Dependencies and integration: `bpf_counter.c` sets attach target to the leader's `on_switch`, reuses the leader diff map fd, sizes accumulators, populates filters, sets globals, and decides whether to attach only fexit or all programs for inheritance.

Risks: global mode bypasses filters and uses accumulator key zero. Non-inherited TGID uses pid as filter key to avoid counting new tasks, which can surprise readers expecting tgid matching. Hash map capacity is fixed at 102400. Correctness depends on fexit seeing leader deltas before user-space reads.

Test signals: run bperf global, CPU, PID, TGID, inherited and non-inherited workloads; fork/exit tasks during measurement; and compare accumulator rows with ordinary perf counts.
