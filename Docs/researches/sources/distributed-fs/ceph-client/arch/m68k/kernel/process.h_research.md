# sources/distributed-fs/ceph-client/arch/m68k/kernel/process.h

## Purpose

`process.h` is the private declaration header for m68k process-related syscall wrappers.

## Important APIs, Types, and Functions

It forward-declares `struct pt_regs` and declares `asmlinkage int m68k_clone(struct pt_regs *regs);` plus `asmlinkage int m68k_clone3(struct pt_regs *regs);`.

## Control Flow

There is no executable control flow. The declarations let syscall entry code and `process.c` agree that clone wrappers receive a register-frame pointer.

## State and Persistence Behavior

The header owns no state. Runtime state changes happen in `process.c` through child stack/thread initialization.

## Dependencies and Integration Points

It depends on `<linux/linkage.h>` and on entry/syscall code that routes clone syscalls to these wrappers because m68k cannot directly use generic argument extraction.

## Risks and Edge Cases

If clone argument extraction moves out of `process.c`, this header must track the calling convention. A mismatch would be severe because the wrapper interprets saved registers as syscall arguments.

## Test Signals

Compile-time coverage plus runtime `clone`/`clone3` tests through libc or syscall tests are the relevant signals.
