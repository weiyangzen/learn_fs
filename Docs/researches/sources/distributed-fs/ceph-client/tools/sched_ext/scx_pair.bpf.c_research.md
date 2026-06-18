# sources/distributed-fs/ceph-client/tools/sched_ext/scx_pair.bpf.c

Purpose: BPF core-scheduling demo that pairs CPUs and ensures each pair runs tasks from the same CPU cgroup during a batch window.

Important APIs/types/functions: rodata/resizable arrays `nr_cpu_ids`, `pair_batch_dur_ns`, `pair_cpu`, `pair_id`, and `in_pair_idx`; `struct pair_ctx` with spin lock, current cgid, start time, draining, active and preempted masks; cgroup queue maps `top_q`, `cgrp_q_arr`, `cgrp_q_idx_hash`, `cgrp_q_len`, and IDR-like busy/cursor arrays. Main callbacks are `pair_enqueue()`, `pair_dispatch()`, `pair_cpu_acquire()`, `pair_cpu_release()`, `pair_cgroup_init()`, `pair_cgroup_exit()`, and `pair_exit()`.

Control flow: enqueue maps a task's cgroup to a per-cgroup FIFO and pushes the cgroup ID to `top_q` when it transitions from empty to non-empty. Dispatch clears this CPU's active bit, expires/drains the current cgroup when the batch expires or empties, waits for the pair CPU or higher-priority preemption to clear, opportunistically selects the next non-empty cgroup, then pops a PID from that cgroup queue and dispatches it globally. CPU release marks the pair preempted and kicks the pair CPU with wait; acquire clears preemption and kicks the pair again.

State and persistence: BPF arrays, queues, hash maps, counters, and pair contexts persist while loaded. Per-cgroup queue indices are allocated on cgroup init and freed on exit.

Dependencies and integration: uses sched_ext cgroup callbacks, CPU acquire/release callbacks, BPF queues, array-of-maps populated by user space, spin locks, task lookup by PID, and shared `scx_pair.h` limits.

Risks: the implementation is intentionally complex due to BPF map and synchronization limitations. It does not handle dequeues from per-cgroup PID queues, so missing PIDs are retried. Top queue can contain duplicate cgroup IDs. Requires even CPU count and correct user-space pairing arrays.

Test signals: cgroup workloads pinned to paired CPUs, higher-priority scheduler preemption, odd CPU count rejection in user space, queue overflow/error counters, and pair consistency under different stride values.
