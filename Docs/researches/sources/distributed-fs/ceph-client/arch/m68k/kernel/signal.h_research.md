# sources/distributed-fs/ceph-client/arch/m68k/kernel/signal.h

## Purpose

`signal.h` is the private header that declares m68k signal resume and return entry points for assembly and sibling C files.

## Important APIs, Types, and Functions

It declares `do_notify_resume(struct pt_regs *regs)`, `do_sigreturn(struct pt_regs *regs, struct switch_stack *sw)`, and `do_rt_sigreturn(struct pt_regs *regs, struct switch_stack *sw)` with `asmlinkage`.

## Control Flow

There is no in-header control flow. The declared functions are reached from low-level return-to-user and signal-return syscall paths.

## State and Persistence Behavior

No state is owned by the header. The implementation in `signal.c` mutates current task signal state, saved registers, FPU state, and user stack frames.

## Dependencies and Integration Points

It depends on `<linux/linkage.h>` and on declarations of `struct pt_regs` and `struct switch_stack` being visible at use sites. It connects entry assembly to `signal.c`.

## Risks and Edge Cases

Calling convention drift would corrupt the stack around signal return, because `do_sigreturn()` returns an adjusted switch-stack pointer.

## Test Signals

Signal delivery and return tests, especially nested frame-size cases, validate the contract represented by these declarations.
