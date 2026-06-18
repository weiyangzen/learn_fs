# sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/user.h

## Purpose

`user.h` defines Hexagon `struct user_regs_struct`, the UAPI register layout exposed to ptrace, core dumps, and signal context. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The type lists 32 GPRs plus loop registers, modifiers, predicate/user status, GP/UGP, optional CS registers, PC, cause, and bad virtual address. Concrete declarations observed in the file: Macros: `HEXAGON_ASM_USER_H`. Types referenced or declared: `user_regs_struct`.

## Control Flow, State, And Persistence

There is no local control flow. State is persisted transiently in ptrace/core/signal ABI objects and must mirror the kernel `pt_regs` save set.

## Dependencies And Integration Points

It integrates with `sigcontext.h`, `ptrace.c` regsets, KGDB register mapping, ELF core note generation, and userspace debuggers.

## Risks And Test Signals

Risks are field ordering changes, incomplete architecture-version guards, and mismatch with ptrace offsets. Test signals are GDB register display, core-dump note validation, signal context restore, and UAPI header compile checks.
 A local static signal for this file is that it has 66 lines and 1370 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
