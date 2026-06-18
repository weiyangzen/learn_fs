# sources/distributed-fs/ceph-client/include/linux/rwlock.h

## Purpose
`rwlock.h` is the generic public include for kernel read/write spinlocks.

## Important APIs, types, and functions
It selects the appropriate raw or RT implementation and exposes standard rwlock operations such as initialization, read/write lock/unlock, trylock, IRQ-save/IRQ-restore variants, BH variants, and lock state assertions through included API/type headers.

## Control flow, state, and persistence
Non-RT rwlocks are spinning locks that allow multiple readers or one writer; RT builds may route to sleeping/PI-aware implementations. The lock word and optional debug state persist in each `rwlock_t` object.

## Dependencies and integration points
It depends on architecture rwlock primitives, lockdep, preempt/IRQ helpers, and RT conditional headers. It is used throughout kernel code that needs short read-mostly critical sections.

## Risks and test signals
Risks include deadlock from recursive write locking, writer starvation on some patterns, using sleeping code inside raw rwlock sections, IRQ state mismatches, and semantic differences under PREEMPT_RT. Test signals include locktorture, lockdep IRQ/BH nesting checks, trylock behavior, RT and non-RT builds, and architecture primitive tests.
