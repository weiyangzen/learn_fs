# sources/distributed-fs/ceph-client/include/linux/rwlock_api_smp.h

## Purpose
`rwlock_api_smp.h` declares the SMP rwlock API wrappers around raw architecture lock operations with lockdep and preemption/IRQ accounting.

## Important APIs, types, and functions
It exposes `__raw_read_lock()`, `__raw_write_lock()`, interruptible variants where present, trylock helpers, unlock helpers, IRQ/BH save/restore variants, and macro wrappers that map public raw rwlock operations to instrumented implementations.

## Control flow, state, and persistence
Lock wrappers acquire lockdep state, disable preemption or interrupts as required, invoke arch raw rwlock operations, and release instrumentation on unlock. State persists in the lock object plus lockdep maps when enabled.

## Dependencies and integration points
It depends on SMP builds, architecture rwlock primitives, lockdep, preempt count, IRQ flag helpers, and debug spinlock instrumentation. `rwlock.h` includes it for SMP raw rwlock behavior.

## Risks and test signals
Risks include mismatched IRQ restore flags, missing lockdep acquire/release pairs, architecture primitive bugs hidden by wrappers, and using the wrong variant for interrupt context. Test signals include lockdep splats staying clean, locktorture rwlock runs, IRQ/BH nesting tests, trylock failure paths, and SMP contention stress.
