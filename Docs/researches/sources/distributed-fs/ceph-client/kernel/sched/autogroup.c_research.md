# sources/distributed-fs/ceph-client/kernel/sched/autogroup.c

## Purpose
`autogroup.c` implements scheduler autogrouping, which automatically places tasks from the same session/signal group into scheduler task groups under the root group. It improves interactive fairness without requiring explicit cgroup configuration and provides proc/sysctl controls for enabling and adjusting group nice values.

## Important APIs, Types, And Functions
Global state includes `sysctl_sched_autogroup_enabled`, `autogroup_default`, and `autogroup_seq_nr`. Core functions are `autogroup_init()`, `autogroup_create()`, `autogroup_destroy()`, `autogroup_free()`, `task_wants_autogroup()`, `sched_autogroup_create_attach()`, `sched_autogroup_detach()`, `sched_autogroup_fork()`, `sched_autogroup_exit()`, `sched_autogroup_exit_task()`, `proc_sched_autogroup_set_nice()`, `proc_sched_autogroup_show_task()`, and `autogroup_path()`. Reference management uses `struct kref`; group updates use `signal->siglock` and the autogroup `rw_semaphore`.

## Control Flow
Boot initialization attaches the init task's signal to `autogroup_default`, points it at `root_task_group`, initializes locking and reference state, and registers the sysctl when enabled. Creating an autogroup allocates `struct autogroup`, creates a scheduler `task_group`, optionally redirects RT scheduling entities to the root group, stores the backpointer, and online-links it under root. Attaching a process takes the target signal lock, swaps `signal->autogroup`, moves all threads with `sched_move_task()`, releases the lock, and drops the previous reference.

Fork copies a reference from the current task's autogroup into the new signal. Exit drops that reference. The proc nice setter checks range, LSM permission, `can_nice()`, admin throttling, converts nice to scheduler shares, updates group shares under write lock, and records the nice value. Display takes a read lock and emits `/autogroup-ID nice N`.

## State And Persistence
Autogroup state is in memory and tied to `signal_struct` lifetime. References count potential users rather than current thread membership. `sysctl_sched_autogroup_enabled` is mutable at runtime and can be disabled at boot with `noautogroup`. Per-autogroup nice values and IDs persist only while the autogroup exists.

## Dependencies And Integration Points
The file integrates with CFS task groups, root task group, scheduler migration via `sched_move_task()`, fork/exit paths, procfs task status output, sysctl, security hooks, nice permission checks, and optional RT group scheduling. It is included by `build_utility.c` under `CONFIG_SCHED_AUTOGROUP`.

## Risks
The main risks are lifetime and locking mistakes around `signal->autogroup`, races with cgroup attachment, exiting threads, and task-group destruction. RT group redirection is subtle because RT tasks use root RT bandwidth while the autogroup remains a CFS grouping concept. Proc nice updates take heavy scheduler locks and are rate-limited for non-admin callers to reduce abuse.

## Test Signals
Signals include booting with and without `noautogroup`, toggling `/proc/sys/kernel/sched_autogroup_enabled`, observing `/proc/<pid>/autogroup`, changing autogroup nice values, running fork/session workloads, and testing interaction with cgroups, RT policy changes, and task exit under lockdep/KASAN.
