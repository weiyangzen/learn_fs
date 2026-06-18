# sources/distributed-fs/ceph-client/tools/sched_ext/scx_userland.c

Purpose: userspace scheduler component for `scx_userland.bpf.c`, implementing a simple vruntime-sorted list for tasks delegated by the BPF scheduler.

Important APIs, types, and functions: uses generated `scx_userland.bpf.skel.h`, queue map file descriptors, `sched_setscheduler(..., SCHED_EXT, ...)`, `mlockall()`, pthread stats printing, and BSD `LIST_*` macros. Important functions include `init_tasks()`, `dispatch_task()`, `update_enqueued()`, `vruntime_enqueue()`, `drain_enqueued_map()`, `dispatch_batch()`, `run_stats_printer()`, `pre_bootstrap()`, `bootstrap()`, and `sched_main_loop()`.

Control flow: `pre_bootstrap()` allocates a PID-indexed task array sized from `/proc/sys/kernel/pid_max`, installs signals, moves the scheduler process to `SCHED_EXT`, parses `-b`/`-v`, and locks memory to avoid allocation stalls later. `bootstrap()` resets state, opens and loads BPF, sets rodata CPU count and scheduler pid, captures queue map FDs, starts the stats thread, and attaches struct_ops. The main loop drains the BPF `enqueued` queue with lookup-and-delete, updates each task's vruntime from kernel-provided `sum_exec_runtime` and weight, inserts into sorted order, dispatches up to `batch_size` lowest-vruntime tasks to the `dispatched` queue, updates BPF counters, and yields.

State and persistence: `tasks` persists across restarts but is zeroed in `bootstrap()`. Each PID slot stores last runtime and accumulated vruntime. `min_vruntime` bounds new/returning tasks. BPF BSS counters and queue maps are shared live state. The stats thread reads BPF and userspace atomics until shutdown.

Dependencies and integration points: depends on libbpf, sched_ext userspace helpers, pthreads, syscall availability for `SCHED_EXT`, and the shared `scx_userland_enqueued_task` layout. Kernel pid_max drives memory use.

Risks: the PID-indexed array can be large and the help text explicitly warns about OOM if pid_max is high. The vruntime queue is an O(n) sorted list, acceptable for demonstration but not scalable. PID reuse and missing lifecycle callbacks can confuse per-PID slots. Dispatch failures reinsert the task and stop the batch, potentially limiting progress. A userspace scheduler crash can affect unrestricted task scheduling.

Test signals: successful run prints BPF enqueue and userspace vruntime counters. Changing `-b` should alter dispatch batch behavior. Under mixed affinity workloads, kernel and user enqueue counters should both move. `UEI_ECODE_RESTART()` should tear down and re-bootstrap.
