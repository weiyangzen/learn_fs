# sources/distributed-fs/ceph-client/tools/sched_ext/scx_userland.bpf.c

Purpose: BPF half of a demonstration sched_ext scheduler that delegates scheduling of unrestricted tasks to a userspace scheduler while directly scheduling CPU-affine tasks in-kernel.

Important APIs, types, and functions: defines rodata `usersched_pid` and `num_possible_cpus`, stats counters (`nr_failed_enqueues`, `nr_kernel_enqueues`, `nr_user_enqueues`), shared work counters (`nr_queued`, `nr_scheduled`), queue maps `enqueued` and `dispatched`, task storage map `task_ctx_stor`, and struct_ops callbacks `userland_select_cpu`, `userland_enqueue`, `userland_dispatch`, `userland_update_idle`, `userland_init_task`, `userland_init`, and `userland_exit`.

Control flow: `userland_init()` validates userspace initialized CPU count and scheduler pid. Each task gets `task_ctx` storage. CPU-affine tasks (`nr_cpus_allowed < num_possible_cpus`) are handled in kernel: `select_cpu` tries previous or any idle CPU and marks `force_local`; `enqueue` inserts to local or global DSQ and counts kernel enqueues. Non-affine tasks, except the scheduler task itself, are encoded as `scx_userland_enqueued_task` records and pushed to the `enqueued` queue map. The userspace scheduler later pushes selected PIDs to `dispatched`; `userland_dispatch()` pops those PIDs, looks up live tasks, and inserts them into the global DSQ. `usersched_needed` wakes the scheduler task through `dispatch_user_scheduler()` and idle CPU kicks.

State and persistence: kernel/user coordination is through queue maps and BSS counters. `usersched_needed` is an atomic-style flag. Per-task `force_local` is task-local. `nr_queued` is incremented in BPF-side enqueue and is expected to be decremented/cleared by userspace after draining; `nr_scheduled` is written by userspace to show outstanding user-scheduled tasks.

Dependencies and integration points: depends on sched_ext helpers, task storage, BPF queue maps, `bpf_task_from_pid()`, and the shared layout in `scx_userland.h`. It is paired with `scx_userland.c`, which must keep the scheduler task itself under sched_ext.

Risks: queue overflow falls back to global DSQ and increments failed enqueue stats, reducing fidelity. The BPF side trusts userspace to maintain `nr_queued` and `nr_scheduled`; stale counters may cause unnecessary or missing scheduler wakeups. PID dispatch races are tolerated by dropping missing tasks, but PID reuse remains a conceptual risk in simple examples. Userspace scheduler failure can strand unrestricted tasks.

Test signals: successful init requires positive `usersched_pid` and CPU count. Counters should show kernel enqueues for affinity-constrained tasks and user enqueues for unrestricted tasks. `nr_failed_enqueues` should stay zero under normal queue sizes. Idle CPUs should trigger scheduler wakeups when work remains.
