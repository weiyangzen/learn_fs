# sources/distributed-fs/ceph-client/include/uapi/asm-generic/signal-defs.h

## Purpose
Provides generic signal action flag definitions, signal mask operation constants, and handler/restorer pointer typedefs shared by architectures.

## Important APIs, Types, And Functions
Exports `SA_NOCLDSTOP`, `SA_NOCLDWAIT`, `SA_SIGINFO`, `SA_UNSUPPORTED`, `SA_EXPOSE_TAGBITS`, `SA_ONSTACK`, `SA_RESTART`, `SA_NODEFER`, `SA_RESETHAND`, aliases `SA_NOMASK` and `SA_ONESHOT`, `SIG_BLOCK`, `SIG_UNBLOCK`, `SIG_SETMASK`, `__sighandler_t`, `__sigrestore_t`, `SIG_DFL`, `SIG_IGN`, and `SIG_ERR`.

## Control Flow
Only preprocessor guards are present. Architecture headers can define existing flag values before inclusion; otherwise the generic values are used. Handler typedefs are skipped for assembly.

## State, Persistence, And Dependencies
No persistent state. The constants persist as part of the user/kernel ABI for `sigaction` and `rt_sigprocmask`. It depends on `<linux/compiler.h>` for `__user` and `__force`.

## Integration Points
Included by generic `signal.h` and architecture `asm/signal.h` variants. `SA_UNSUPPORTED` is specifically used by userspace probing of `sigaction` flag support.

## Risks
Flag bit reuse is dangerous because several holes are reserved by older architectures. `SA_UNSUPPORTED` semantics rely on old kernels not clearing unknown flags, so changing that value would break feature detection.

## Test Signals
Compile UAPI headers for C and assembly, run `sigaction` flag probing tests, verify `SA_EXPOSE_TAGBITS` address-tag behavior on supporting architectures, and ensure legacy aliases match their modern equivalents.
