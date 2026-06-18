<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/current.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/current.h

## Purpose
Defines how Xtensa obtains the current task pointer in C and assembly.

## Important APIs, Types, And Functions
Provides `get_current()`, `current`, `current_stack_pointer` bound to register `a1`, and assembly macro `GET_CURRENT(reg, sp)`.

## Control Flow
C callers obtain `current_thread_info()->task`. Assembly callers derive thread info from the stack pointer via `GET_THREAD_INFO` and load `TI_TASK`.

## State And Persistence
No owned state; reads stack/thread-info state maintained by scheduler and entry code.

## Dependencies And Integration Points
Depends on `thread_info.h`, generated thread-info offsets, and Xtensa stack pointer register conventions.

## Risks And Edge Cases
Stack alignment and thread-info placement must match `GET_THREAD_INFO`. Binding `current_stack_pointer` to `a1` relies on compiler/register ABI correctness.

## Test Signals
Scheduler/context-switch tests, assembly exception-entry tests, and compile coverage for C and assembly users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/current.h -->
