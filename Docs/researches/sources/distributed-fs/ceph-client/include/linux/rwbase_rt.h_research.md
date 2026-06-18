# sources/distributed-fs/ceph-client/include/linux/rwbase_rt.h

## Purpose
`rwbase_rt.h` declares the PREEMPT_RT base implementation used by RT read/write locks and semaphores.

## Important APIs, types, and functions
It defines the RT reader/writer base structure and low-level initialization/acquire/release helpers used by `rwlock_rt.h` and related RT locking code.

## Control flow, state, and persistence
On RT kernels, rw locking is built on sleeping/PI-aware primitives rather than raw spinning for long sections. The base tracks reader/writer ownership and serializes transitions through RT-mutex-like state. State persists in the lock object.

## Dependencies and integration points
It depends on RT mutex infrastructure, atomic counters or owner tracking from the implementation, and PREEMPT_RT Kconfig selection. It integrates with `rwlock_rt.h`, `rwsem.h` RT variants, lockdep annotations, and scheduler priority inheritance.

## Risks and test signals
Risks include sleeping in contexts that expected raw rwlocks, reader/writer starvation or PI inversion, and differences from non-RT rwlock semantics. Test signals include PREEMPT_RT lock tests, lockdep class coverage, reader/writer contention stress, interrupt-context misuse detection, and latency tests.
