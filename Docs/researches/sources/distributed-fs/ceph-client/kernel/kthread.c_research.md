# sources/distributed-fs/ceph-client/kernel/kthread.c

## Purpose
`kthread.c` provides the kernel thread creation, lifecycle, parking/stopping, affinity, worker-queue, delayed-work, temporary-mm, and block-cgroup helper APIs used across the kernel.

## Important APIs, Types, And Functions
Key types are `struct kthread_create_info` and private `struct kthread`. Public APIs include `kthread_create_on_node()`, `kthread_create_on_cpu()`, `kthread_bind()`, `kthread_stop()`, `kthread_park()`, `kthread_unpark()`, `kthread_should_stop()`, `kthread_should_park()`, `kthread_worker_fn()`, worker create/destroy/queue/flush/cancel helpers, `kthread_use_mm()`, and `kthread_unuse_mm()`. Global state includes `kthreadd_task`, `kthread_create_list`, and `kthread_affinity_list`.

## Control Flow
Callers enqueue create requests under `kthread_create_lock` and wake `kthreadd`. `kthreadd()` clones a child running `kthread()`, which initializes private metadata, reports completion, sleeps until explicitly woken/stopped, applies default affinity, parks if requested, then runs the caller function and exits through `kthread_exit()`. Stop and park set flag bits, wake the task, and wait on completions/inactive states. Worker APIs run a loop that dequeues work under a raw spinlock, executes callbacks, handles freezing, and supports delayed timers.

## State And Persistence
Each kthread stores flags, CPU/node preference, result, function/data, completions, optional full name, preferred affinity, and optional blkcg association in `task->worker_private`. Worker objects persist until destroyed and own pending/current/delayed work lists. Affinity preferences are kept on a global list and refreshed on housekeeping/cpuhp changes.

## Dependencies And Integration Points
The file integrates with scheduler states, completions, freezer, cgroups, cpusets/housekeeping isolation, CPU hotplug, NUMA, timers, tracepoints, membarrier/MMU context switching, and block cgroups. It is foundational for subsystem daemon threads such as the kprobe optimizer.

## Risks And Edge Cases
Races around creation cancellation, park/unpark, delayed work timer cancellation, worker destruction, and CPU hotplug are the main hazards. Callers must not queue one work item to multiple workers. `kthread_use_mm()` must maintain membarrier and TLB ordering. Affinity APIs require inactive tasks before first wakeup.

## Test Signals
Signals include successful creation under `kthreadd`, killable creation interruption, stop return values, park/unpark state transitions, CPU-bound and preferred-affinity behavior across hotplug/isolation changes, worker queue/flush/cancel/delayed-work semantics, freezer handling, and temporary-mm adoption ordering.
