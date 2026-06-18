# sources/distributed-fs/ceph-client/include/linux/rwlock_rt.h

## Purpose
`rwlock_rt.h` provides the PREEMPT_RT implementation and API mapping for rwlocks.

## Important APIs, types, and functions
It defines RT-specific `rwlock_t` initialization and maps read/write lock, unlock, trylock, BH, IRQ, and IRQ-save forms onto RT-aware helper functions. It relies on the RT rwbase layer rather than pure spinning.

## Control flow, state, and persistence
RT rwlocks preserve source-level rwlock APIs while turning contended sections into sleeping/priority-inheritance aware waits where possible. IRQ/BH variants keep API compatibility but must respect RT's restrictions on sleeping locks. State persists in the RT lock object and lockdep metadata.

## Dependencies and integration points
It depends on PREEMPT_RT, `rwbase_rt.h`, scheduler/PI locking, lockdep, and public rwlock type definitions. It integrates with code compiled unchanged across RT and non-RT kernels.

## Risks and test signals
Risks include code assuming hard spinning or IRQ-safe semantics when RT may sleep, lock ordering differences, and trylock behavior under priority inheritance. Test signals include PREEMPT_RT locktorture, IRQ-context misuse tests, lockdep class validation, and latency benchmarks under reader/writer contention.
