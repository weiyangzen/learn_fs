<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/livepatch_sched.h -->
# sources/distributed-fs/ceph-client/include/linux/livepatch_sched.h

## Purpose
This header connects livepatch task transitions to scheduler activity. It lets the scheduler opportunistically switch a task's patch state when a static key is enabled.

## Important APIs, Types, and Functions
With `CONFIG_LIVEPATCH`, it declares `__klp_sched_try_switch()` and `DECLARE_STATIC_KEY_FALSE(klp_sched_try_switch_key)`. `klp_sched_try_switch(struct task_struct *curr)` checks the static key and the task state. Without livepatch it compiles to an empty inline.

## Control Flow
On scheduler paths, the inline checks `static_branch_unlikely()` and whether the current task has `TASK_FREEZABLE` state bits before calling the out-of-line transition helper.

## State and Persistence Behavior
State is runtime livepatch transition state and a static branch key. Nothing persists across boot.

## Dependencies and Integration Points
It depends on jump labels and scheduler task state. It integrates with livepatch consistency transitions and scheduler code that can safely observe current tasks.

## Risks and Test Signals
Risks include missed transition opportunities, excessive scheduler overhead if the static key is mishandled, and incorrect state filtering. Test signals are livepatch transition selftests, static-key enable/disable tracing, and confirmation that tasks converge out of `TIF_PATCH_PENDING`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/livepatch_sched.h -->
