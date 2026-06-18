# sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/sigcontext.h

## Purpose

`sigcontext.h` defines the Hexagon `struct sigcontext` UAPI wrapper around `struct user_regs_struct`. It is the register payload embedded in `ucontext` for `rt_sigreturn`. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The key type is `sigcontext.sc_regs`; it is populated in `setup_sigcontext` and consumed by `restore_sigcontext`. Concrete declarations observed in the file: Includes: `asm/user.h`. Macros: `_ASM_SIGCONTEXT_H`. Types referenced or declared: `sigcontext`, `user_regs_struct`.

## Control Flow, State, And Persistence

No local runtime logic exists. The persistent contract is the userspace signal frame layout, which must remain stable across kernel versions.

## Dependencies And Integration Points

It depends on `asm/user.h` and integrates with `kernel/signal.c`, libc signal trampolines, debuggers, and unwinding code.

## Risks And Test Signals

Risks are irreversible UAPI layout drift or incomplete register restore. Test signals are signal-handler ABI tests, `rt_sigreturn`, unwinder behavior, and ptrace/signal register comparisons.
 A local static signal for this file is that it has 35 lines and 1167 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
