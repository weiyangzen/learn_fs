<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/current.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/current.h

## Purpose
This header defines how m68k obtains the current task pointer and current stack pointer.

## Important APIs, Types, And Functions
- On MMU builds, `current` is a register variable bound to `%a2`.
- On non-MMU builds, `get_current()` returns `current_thread_info()->task` and `current` maps to that helper.
- `current_stack_pointer` is a register variable bound to `sp`.

## Control Flow
MMU code reads `current` directly from the reserved address register. Non-MMU code computes it from thread info. There is no other runtime logic.

## State And Persistence Behavior
The current task pointer is maintained by low-level entry/context-switch code. This header exposes it to C code and does not own the state.

## Dependencies And Integration Points
It integrates with m68k entry code, context switching, thread_info layout, scheduler, and all kernel code using `current`.

## Risks And Edge Cases
MMU builds reserve `%a2`; compiler and assembly code must honor that convention. Non-MMU correctness depends on `current_thread_info()` being valid for the current stack.

## Test Signals
Context-switch stress, syscall/interrupt entry tests, scheduler tests, and builds for MMU/non-MMU configs validate current pointer handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/current.h -->
