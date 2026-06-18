# sources/distributed-fs/ceph-client/lib/syscall.c

## Purpose
Provides a helper to inspect the current syscall state of a task, primarily for diagnostics that need to describe what a blocked task is doing without using unsafe user register APIs while a syscall is in progress.

## APIs, Control Flow, and State
The exported API is `task_current_syscall()`. For `current`, it directly calls `collect_syscall()`. For another task, it snapshots `target->__state`, rejects runnable tasks with `-EAGAIN`, waits for the task to be inactive, collects registers and syscall data, then waits again and verifies the context-switch count is unchanged. `collect_syscall()` pins the task stack with `try_get_task_stack()`, obtains `task_pt_regs()`, records user stack pointer and instruction pointer, gets the syscall number, fetches up to six arguments when in a syscall, releases the stack, and fills `info->data.nr = -1` when the task has no stack or is not in a syscall.

No persistent state is stored; all output is written into the caller-provided `struct syscall_info`.

## Dependencies, Integration, Risks, and Tests
Depends on task stacks, ptrace register helpers, scheduler inactive waits, architecture `asm/syscall.h`, and task state fields. Integration points include `/proc`, scheduler debug, hung-task reporting, tracing, and crash diagnostics. Risks include races if the task wakes or changes syscall state between waits, architecture register helpers returning unavailable data, current-task inspection being less stable than blocked-task inspection, and callers treating `nr == -1` as an error instead of a valid non-syscall result. Test signals include proc syscall reporting tests, blocked syscall scenarios, runnable task `-EAGAIN` cases, architecture syscall argument tests, and race stress with rapidly waking tasks.
