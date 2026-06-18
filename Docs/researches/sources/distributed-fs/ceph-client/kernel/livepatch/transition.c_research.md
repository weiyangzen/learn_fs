# sources/distributed-fs/ceph-client/kernel/livepatch/transition.c

## Purpose
`transition.c` implements the livepatch consistency model. It tracks the currently transitioning patch, target patch state, per-task patch states, pending thread flags, reliable-stack checks, scheduler-assisted task switching, transition reversal, forced completion, and final cleanup once every task has safely moved to the target patch state.

## Important APIs, Types, and Functions
Global transition state is `klp_transition_patch`, `klp_target_state`, `klp_signals_cnt`, per-CPU `klp_stack_entries`, and static key `klp_sched_try_switch_key`. Public functions are `klp_init_transition()`, `klp_start_transition()`, `klp_try_complete_transition()`, `klp_cancel_transition()`, `klp_reverse_transition()`, `klp_force_transition()`, `klp_update_patch_state()`, `__klp_sched_try_switch()`, and `klp_copy_process()`.

Important helpers include `klp_synchronize_transition()`, `klp_complete_transition()`, `klp_check_stack_func()`, `klp_check_stack()`, `klp_check_and_switch_task()`, `klp_try_switch_task()`, and `klp_send_signals()`. Delayed work `klp_transition_work` periodically retries straggler tasks.

## Control Flow
`klp_init_transition()` sets `klp_transition_patch`, chooses target state, initializes all tasks and idle tasks to the opposite initial state, issues ordering barriers, and marks every function in the patch as `transition = true`. `klp_start_transition()` sets `TIF_PATCH_PENDING` for tasks whose `patch_state` differs from the target, marks idle tasks pending, enables scheduler switching through a static key, and resets signal retry count.

`klp_try_complete_transition()` attempts to move normal and idle tasks by checking whether they are already switched or can be switched safely. With reliable stacks, inactive tasks are inspected for frames in to-be-patched or to-be-unpatched functions; if safe, `patch_state` is updated and `TIF_PATCH_PENDING` is cleared. Incomplete transitions schedule retry work and periodically wake kthreads or set notify signals on userspace tasks.

When complete, `klp_complete_transition()` handles replace cleanup, unpatches objects on disable, synchronizes against ftrace handler readers, clears function transition flags, resets every task to `KLP_TRANSITION_IDLE`, invokes post callbacks, and clears global transition state. Disabled patches or replaced patches are then asynchronously freed by `klp_try_complete_transition()`.

## State and Persistence Behavior
Transition state is transient and process-wide. Per-task `task->patch_state` and `TIF_PATCH_PENDING` define which function stack entry ftrace may expose to that task. The scheduler static key remains enabled only during an active transition. Forced transitions clear pending flags even if tasks are active, marking patches as forced so cleanup avoids unsafe module reference drops.

## Dependencies and Integration Points
This file integrates with scheduler hooks (`__klp_sched_try_switch()`), fork path (`klp_copy_process()`), tasklist and CPU iteration, reliable stacktrace support, ftrace stack state from `patch.c`, object callbacks and patch list helpers from `core.c`, and architecture support signaled by `klp_have_reliable_stack()`.

## Risks and Test Signals
Correctness depends on memory barriers between task states, function transition flags, and ftrace stack visibility. Architectures without reliable stacks may leave transitions pending until kernel exit or force. Forced completion can break the consistency model and is deliberately administrator-controlled. Tests should cover patch and unpatch transitions, long-sleeping tasks on patched functions, CPU-bound kthreads, idle/offline CPUs, fork during transition, reverse transition via sysfs, forced transition, atomic replace cleanup, and no stale `TIF_PATCH_PENDING` after completion.
