# sources/distributed-fs/ceph-client/arch/arm/lib/call_with_stack.S

Purpose: provides `call_with_stack(fn, arg, sp)`, a helper that switches to a supplied stack, calls a function with one argument, and returns to the original stack with unwind-compatible frame setup.

Control flow saves FP/LR using either frame-pointer APCS or EHABI unwind annotations, moves `sp` to the caller-supplied stack, branches through the function pointer, restores the old stack/frame, and returns. State is the live stack pointer only. Dependencies include `asm/assembler.h`, unwind metadata, and `unwind.c`, which has special handling for this known stack transition. Risks are invalid stack pointers, broken unwinding across the stack switch, and callee assumptions about stack alignment. Test signals include stack-switch users executing successfully and backtraces crossing `call_with_stack` without false stack overflow failures.
