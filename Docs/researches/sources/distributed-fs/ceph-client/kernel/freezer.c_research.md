<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/freezer.c -->
# sources/distributed-fs/ceph-client/kernel/freezer.c

Purpose: implements the generic task freezer used by system suspend/hibernate, cgroup v1 freezer state, and freezer-aware kernel threads. It decides when a task must stop, transitions eligible tasks into `TASK_FROZEN`, wakes tasks so they can enter the refrigerator, and thaws them back to either running or their saved sleep state.

Important APIs/types/functions: exported state includes `freezer_active`, `pm_freezing`, and `pm_nosig_freezing`. Public helpers are `freezing_slow_path()`, `frozen()`, `__refrigerator()`, `freeze_task()`, `__thaw_task()`, `thaw_process()`, and `set_freezable()`. Internal helpers include `fake_signal_wake_up()`, `__set_task_frozen()`, `__freeze_task()`, and `__restore_freezer_state()`. `freezer_lock` serializes freezing and thawing state transitions.

Control flow: `freezing_slow_path()` filters out `PF_NOFREEZE`, suspend-task, and OOM-victim tasks, then accepts cgroup freezing, nosignal PM freezing, or userspace PM freezing for non-kthreads. `freeze_task()` checks whether a task is freezing and not already frozen, attempts direct state conversion with `task_call_func()`, and otherwise nudges the task with a fake signal for userspace or `wake_up_state()` for kthreads. `__refrigerator()` repeatedly sets current to `TASK_FROZEN`, clears stale saved state, checks whether freezing is still active and whether a kthread stop should break the loop, schedules, then returns to `TASK_RUNNING`.

State and persistence behavior: all state is runtime-only task state and global freezer flags. `saved_state` preserves a task's original sleep state when converting `TASK_FREEZABLE`, stopped, or traced tasks to `TASK_FROZEN`; thawing restores that state when possible or wakes `TASK_FROZEN` sleepers. `set_freezable()` clears `PF_NOFREEZE` under `freezer_lock` and immediately tries to freeze if a freeze request is visible.

Dependencies and integration points: integrates with scheduler task states, `task_call_func()`, `pi_lock`, signal wakeups, kthread stop checks, suspend flags, cgroup v1 freezer, OOM victim detection, and lockdep diagnostics for freezing with locks held. `fork.c` uses `TASK_FREEZABLE` during vfork waits, so the freezer can suspend a parent blocked on child exec/exit.

Risks: races around saved state and wakeups can leave tasks stuck frozen or lose a legitimate wakeup. Freezing tasks holding locks can deadlock suspend, which is why lockdep warns unless marked unsafe. Misclassifying OOM victims, kthreads, or cgroup-frozen tasks can block suspend progress or freeze tasks that must continue running.

Test signals: suspend/resume and hibernate stress, cgroup freezer tests, kthread `set_freezable()` and stop races, ptraced/stopped/freezable sleep state restoration, lockdep coverage for unsafe freezing, OOM victim exclusion, and vfork wait interaction with `TASK_FREEZABLE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/freezer.c -->
