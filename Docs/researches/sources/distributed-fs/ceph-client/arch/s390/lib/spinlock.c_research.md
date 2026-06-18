# sources/distributed-fs/ceph-client/arch/s390/lib/spinlock.c

## Purpose
Implements out-of-line s390 spinlock and rwlock wait paths, including queued locking for dedicated CPUs and yield behavior for preempted virtual CPUs.

## Important APIs, Types, And Functions
Exports `arch_spin_lock_wait()`, `arch_spin_trylock_retry()`, `arch_read_lock_wait()`, `arch_write_lock_wait()`, and `arch_spin_relax()`. `arch_spin_lock_setup()` initializes per-CPU queue nodes. Boot/sysctl state is `spin_retry`, configurable via `spin_retry=` and `/proc/sys/kernel/spin_retry`. Internal helpers decode queue tails, issue NIAI-assisted loads/cmpxchg where available, choose yield targets, and implement queued or classic spin acquisition.

## Control Flow And State
Dedicated CPUs use `arch_spin_lock_queued()`: enqueue a per-CPU node into the lock word tail, optionally yield to the owner, wait for predecessor release, acquire the lock with bounded retry/yield loops, then pass queue ownership to the next node. Non-dedicated CPUs use classic spinning with retry-yield loops. RW lock wait paths serialize through an embedded spinlock wait queue and manipulate reader/writer bits in `rw->cnts`.

## Dependencies And Integration
Depends on s390 lowcore, SMP yield APIs, machine type checks, alternatives/NIAI facility 49, sysctl init, and generic arch spinlock types.

## Risks And Test Signals
Risks include queue corruption, incorrect CPU/index encoding, lock stealing fairness bugs, missing memory ordering, interrupt-context read-lock behavior, and virtualization yield heuristics. Signals include lock torture tests, lockdep, SMP stress on LPAR and non-LPAR, sysctl changes, and performance/regression measurements under contention.
