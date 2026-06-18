# sources/distributed-fs/ceph-client/kernel/kstack_erase.c

## Purpose
`kstack_erase.c` implements STACKLEAK/KSTACK_ERASE behavior: it tracks the lowest stack pointer reached by a task and poisons the used portion of the kernel stack before returning to userspace to reduce information disclosure and uninitialized stack attack surface.

## Important APIs, Types, And Functions
The entry points are `stackleak_erase()`, `stackleak_erase_on_task_stack()`, `stackleak_erase_off_task_stack()`, and exported `__sanitizer_cov_stack_depth()`. `__stackleak_erase()` computes erase bounds with `stackleak_task_low_bound()`, `stackleak_task_high_bound()`, `stackleak_find_top_of_poison()`, `current_stack_pointer`, and `current->lowest_stack`. Optional runtime disable uses static key `stack_erasing_bypass` and sysctl `kernel/stack_erasing`.

## Control Flow
Instrumentation calls `__sanitizer_cov_stack_depth()` to lower `current->lowest_stack` when a deeper stack pointer is observed. On syscall/return paths, erase wrappers skip if disabled, then poison from the previous poison top to either the current stack pointer or the top of the task stack depending on whether execution is on the task stack. The lowest marker resets to the stack high bound for the next syscall.

## State And Persistence
Per-task `lowest_stack` and optional `prev_lowest_stack` carry state across kernel entries. The runtime-disable static key persists globally until sysctl toggles it.

## Dependencies And Integration Points
The file depends on low-level stack helpers, `noinstr` entry constraints, sysctl, jump labels, and compiler sanitizer stack-depth instrumentation. It explicitly exports `__sanitizer_cov_stack_depth` for instrumentation references.

## Risks And Edge Cases
The erase range must not clobber active frames, so wrong `on_task_stack` selection or stack-bound helpers can crash the kernel. `CONFIG_KSTACK_ERASE_TRACK_MIN_SIZE` must not exceed search depth. Runtime disable weakens security and logs a warning. The code is `noinstr`, so instrumentation and tracing constraints are strict.

## Test Signals
Signals include sysctl enable/disable behavior, poison pattern visibility in stack tests, no corruption on task and entry stacks, stack-depth tracking under deep calls, metrics updates when configured, and build-time `BUILD_BUG_ON` coverage.
