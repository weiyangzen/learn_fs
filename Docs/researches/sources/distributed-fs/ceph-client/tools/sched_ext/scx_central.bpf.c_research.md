# sources/distributed-fs/ceph-client/tools/sched_ext/scx_central.bpf.c

Purpose: BPF implementation of a central FIFO sched_ext scheduler where one central CPU makes dispatch decisions for all CPUs, demonstrates LOCAL_ON dispatching, tickless infinite slices, timer-driven preemption, and kthread priority handling.

Important APIs/types/functions: rodata inputs are `central_cpu`, `nr_cpu_ids`, and `slice_ns`. State includes `central_q` BPF queue of PIDs, resizable arrays `cpu_gimme_task` and `cpu_started_at`, a `central_timer`, counters, and `UEI_DEFINE(uei)`. Struct_ops callbacks are `central_select_cpu()`, `central_enqueue()`, `central_dispatch()`, `central_running()`, `central_stopping()`, `central_init()`, and `central_exit()`.

Control flow: wakeups are steered to the central CPU. Enqueue sends single-CPU kthreads directly to local DSQs with preemption; other tasks are pushed into `central_q` or fallback DSQ on overflow, and the central CPU is kicked. Central dispatch services other CPUs that set `cpu_gimme_task`, then itself. Non-central CPUs consume fallback tasks, mark themselves as needing work, and kick the central CPU. The timer periodically checks CPU runtime against `slice_ns` and kicks CPUs that should rotate.

State and persistence: BPF maps and globals persist while the scheduler is loaded. `cpu_started_at` tracks running slice start times, `cpu_gimme_task` is the request bitmap, and counters expose behavior to user space.

Dependencies and integration: uses sched_ext DSQs, BPF queue maps, BPF timers, task lookup by PID, CPU kicks, and `SCX_OPS_ENQ_LAST`. User space must resize arrays to `nr_cpu_ids` before load.

Risks: central scheduling can bottleneck on one CPU. Queue overflow falls back to DSQ 0. PID lookup can fail after enqueue, counted as lost. BPF timer CPU pinning falls back when unsupported, but pinned-mode mismatch is considered fatal. Correctness relies on dispatch buffer slot availability and explicit retry kicks.

Test signals: run with default and nonzero central CPU, observe counters for queued/dispatch/retry/mismatch/overflow, test with nohz_full for tickless behavior, verify kthreads remain forward-progress safe, and trigger hotplug restart handling from user space.
