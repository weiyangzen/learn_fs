<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/autosleep.c -->
# sources/distributed-fs/ceph-client/kernel/power/autosleep.c

Purpose: Implements opportunistic system autosleep, queueing suspend/hibernate attempts whenever wakeup-source accounting indicates the system can enter a configured sleep state.

Important APIs/types/functions: `queue_up_suspend_work()`, `pm_autosleep_state()`, `pm_autosleep_lock()`, `pm_autosleep_unlock()`, `pm_autosleep_set_state()`, and `pm_autosleep_init()`. Internal state includes `autosleep_state`, `autosleep_wq`, `autosleep_lock`, `autosleep_ws`, and work item `suspend_work`.

Control flow: `try_to_suspend()` obtains a wakeup count, locks autosleep, saves the count, checks `SYSTEM_RUNNING`, skips if state is `PM_SUSPEND_ON`, then calls `hibernate()` for disk states or `pm_suspend()` for suspend states. After unlock it rechecks wakeup count; if no wakeup count changed, it sleeps half a second to avoid tight suspend/resume loops, then requeues if autosleep remains enabled. `pm_autosleep_set_state()` holds a wakeup source while changing state, toggles wakeup-source autosleep behavior, and queues work when enabling.

State and persistence: Runtime state is the selected sleep state, ordered workqueue, mutex, and wakeup source. State is not persistent across reboot; userspace typically drives it through PM sysfs.

Dependencies/integration: Integrates with wakeup source accounting, system suspend/hibernate core, system state, workqueues, and `power.h` PM internals.

Risks: The comment warns that `autosleep_lock` is safe to lock only while a wakeup source is active or interruptibly, otherwise deadlock with freezing is possible. Wakeup count races determine whether suspend attempts proceed. Autosleep can repeatedly suspend if userspace or drivers mismanage wakeup sources.

Test signals: enable/disable autosleep states, suspend and hibernate paths, wakeup count save failure, wakeup-source active protection while changing state, `SYSTEM_RUNNING` rejection, tight-loop delay when final count equals initial count, workqueue allocation failure, and lockdep coverage for freeze interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/autosleep.c -->
