# sources/distributed-fs/ceph-client/kernel/sched/autogroup.h

## Purpose
`autogroup.h` declares the scheduler autogroup interface and provides no-op fallbacks when `CONFIG_SCHED_AUTOGROUP` is disabled.

## Important APIs, Types, And Functions
When enabled, it defines `struct autogroup` with `kref`, `task_group *tg`, `rw_semaphore lock`, `id`, and `nice`. It declares `autogroup_init()`, `autogroup_free()`, `task_group_is_autogroup()`, `task_wants_autogroup()`, `autogroup_task_group()`, and `autogroup_path()`. The key inline `autogroup_task_group()` reads `sysctl_sched_autogroup_enabled` and redirects eligible root-group tasks to `p->signal->autogroup->tg`.

## Control Flow
Scheduler code calls `autogroup_task_group(p, tg)` when resolving a task's effective task group. If autogrouping is enabled and `task_wants_autogroup()` accepts the task/root group combination, the inline returns the signal's autogroup task group; otherwise it returns the original group. Disabled builds return original groups and empty helpers.

## State And Persistence
The header itself has no state. It exposes the runtime state managed by `autogroup.c`: autogroup references, task-group pointers, nice values, and sysctl enablement.

## Dependencies And Integration Points
It includes `sched.h` and is consumed by scheduler core/fair/debug paths that need task-group selection or path formatting. It is also included by `autogroup.c` for the concrete implementation.

## Risks
Because this header contains inline task-group selection, changes can affect hot scheduler paths. It dereferences `p->signal->autogroup` only when the implementation says the task wants autogrouping, so caller locking and signal lifetime assumptions must remain valid.

## Test Signals
Build coverage with `CONFIG_SCHED_AUTOGROUP=y` and `n` validates the enabled declarations and disabled stubs. Runtime task-group selection can be observed through scheduler debug/proc output and autogroup behavior under fork/session/cgroup tests.
