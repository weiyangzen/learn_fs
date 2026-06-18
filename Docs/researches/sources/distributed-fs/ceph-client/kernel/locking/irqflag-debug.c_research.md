# sources/distributed-fs/ceph-client/kernel/locking/irqflag-debug.c

## Purpose
`irqflag-debug.c` provides a debug helper for IRQ flag misuse: it warns when `raw_local_irq_restore()` is called while IRQs are already enabled.

## Important APIs, Types, and Functions
The only function is exported `noinstr void warn_bogus_irq_restore(void)`. It wraps `WARN_ONCE(1, ...)` with `instrumentation_begin()` and `instrumentation_end()`.

## Control Flow
Low-level IRQ flag restore debugging code calls this helper on invalid restore state. The helper emits a one-time warning and returns.

## State and Persistence Behavior
The only state is the internal `WARN_ONCE` static state that suppresses repeated warnings. It has no persistent storage.

## Dependencies and Integration Points
It depends on bug/warn infrastructure, export symbols, and irqflags code. `noinstr` plus explicit instrumentation bracketing keeps it usable from low-level contexts.

## Risks and Test Signals
Because it is called from instrumentation-sensitive paths, adding tracing or sleeping code would be unsafe. Tests should exercise DEBUG_IRQFLAGS misuse under lockdep/debug kernels and verify the symbol exports for architecture/raw irqflag code.
