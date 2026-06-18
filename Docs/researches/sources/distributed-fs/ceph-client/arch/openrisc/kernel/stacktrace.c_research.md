<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/stacktrace.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/stacktrace.c

## Purpose
Adapts the OpenRISC unwinder to Linux `struct stack_trace` collection APIs.

## Important APIs, Types, And Functions
Implements `save_stack_trace()`, `save_stack_trace_tsk()`, and `save_stack_trace_regs()`, plus callbacks that only record reliable entries and optionally skip scheduler functions.

## Control Flow
For current task it starts near a local stack variable; for another task it pins the task stack, derives the saved kernel context from `thread_info->ksp`, unwinds, then drops the stack reference.

## State And Persistence
Fills caller-provided stack trace buffers. Does not persist internal state.

## Dependencies And Integration Points
Depends on `unwind_stack()`, scheduler stack helpers, `thread_info->ksp`, and stacktrace export APIs.

## Risks
If unwinder marks entries unreliable, traces can be empty. Deriving another task's SP depends on the context-switch frame layout.

## Test Signals
Stacktrace users such as lockdep, perf, WARN/Oops output, and task stack traces under `CONFIG_FRAME_POINTER`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/stacktrace.c -->
