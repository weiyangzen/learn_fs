<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/osq_lock.h -->
# sources/distributed-fs/ceph-client/include/linux/osq_lock.h

## Purpose
This header declares the optimistic spin queue lock used by sleeping locks such as mutexes and rwsems to perform MCS-like optimistic spinning.

## Important APIs, types, and functions
`struct optimistic_spin_queue` contains an atomic encoded tail CPU value. `OSQ_UNLOCKED_VAL` and `OSQ_LOCK_UNLOCKED` initialize the lock. APIs are `osq_lock_init()`, `osq_lock()`, `osq_unlock()`, and `osq_is_locked()`.

## Control flow
Callers initialize the queue, attempt `osq_lock()` while optimistic spinning is allowed, and call `osq_unlock()` to hand off/clear the queue. `osq_is_locked()` reads whether the tail differs from unlocked.

## State and persistence
The only persistent state is `tail`, an atomic queue tail encoding. Per-CPU queue nodes and handoff details live in implementation code.

## Dependencies and integration points
It depends on atomic operations and integrates with mutex/rwsem optimistic spinning and scheduler owner-running heuristics.

## Risks and test signals
Risks include stale CPU encoding, unlock handoff races, spinning when owner cannot run, initialization omissions, and architecture atomic ordering bugs. Test mutex/rwsem contention, preemption/CPU hotplug stress, lockdep/debug builds, and fairness/latency under heavy contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/osq_lock.h -->
