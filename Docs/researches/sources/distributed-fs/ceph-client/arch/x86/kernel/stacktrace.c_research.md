# sources/distributed-fs/ceph-client/arch/x86/kernel/stacktrace.c

## Purpose
`stacktrace.c` provides x86 implementations of generic kernel, reliable kernel, and userspace stack walking.

## Important APIs, Types, And Functions
The arch hooks are `arch_stack_walk()`, `arch_stack_walk_reliable()`, and `arch_stack_walk_user()`. `copy_stack_frame()` reads userspace `struct stack_frame_user { next_fp, ret_addr }` with page faults disabled.

## Control Flow
Normal kernel walking optionally emits `regs->ip`, starts the unwinder, and feeds return addresses until completion or consumer stop. Reliable walking rejects uncertain frames, kernel exception frames with frame pointers, null addresses, and unwind errors. User walking emits current IP, follows frame pointers from BP, and stops on inaccessible, below-SP, or zero-return frames.

## State, Persistence, Dependencies, Integration
No persistent state is modified. It depends on the x86 unwinder, task stacks, `pt_regs`, user access checks, and stacktrace consumer callbacks. Generic stacktrace, livepatch, tracing, profiling, and debugging code consume these hooks.

## Risks And Test Signals
Reliable unwinding intentionally fails on ambiguous generated code and kernel-mode register frames. User walking is heuristic. Test ORC/frame-pointer configs, livepatch reliable stacks, interrupt/preemption frames, user stacks with bad frame pointers, inaccessible memory, and consumer early stop.
