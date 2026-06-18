# sources/distributed-fs/ceph-client/include/linux/kdebug.h

## Purpose
Declares the architecture die-notifier interface for trap, fault, oops, and debug exception notifications.

## Important APIs, Types, And Functions
Includes `asm/kdebug.h` for `enum die_val` and architecture definitions. `struct die_args` carries `pt_regs`, message string, error code, trap number, and signal number. APIs are `register_die_notifier()`, `unregister_die_notifier()`, and `notify_die()`.

## Control Flow
Architecture exception paths call `notify_die()` with a reason and register/error context. Registered notifier blocks can inspect or handle the event according to notifier-chain semantics.

## State And Persistence
State is the global die notifier chain maintained by implementation code. Registered notifier blocks persist until unregistered.

## Dependencies And Integration Points
Depends on architecture debug definitions, `struct pt_regs`, and notifier infrastructure. Integrates with kprobes, KGDB/KDB, oops handling, tracing, and architecture trap code.

## Risks
Die notifiers run in sensitive exception context and must avoid sleeping or causing recursive faults. Registration ordering can affect which subsystem handles a trap. Bad notifiers can destabilize panic/oops paths.

## Test Signals
Signals include notifier registration tests, controlled trap/breakpoint handling, KGDB/kprobe interactions, unregister safety, and architecture-specific die reason coverage.
