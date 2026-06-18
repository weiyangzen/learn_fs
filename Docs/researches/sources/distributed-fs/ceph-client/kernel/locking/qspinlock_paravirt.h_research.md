# sources/distributed-fs/ceph-client/kernel/locking/qspinlock_paravirt.h

## Purpose
Implements paravirtual queued spinlocks, replacing long busy-waits in guests with hypervisor wait/kick operations. It extends qspinlock with a slow locked value, per-node vCPU state, a lock-to-node hash table, and hybrid queued/unfair lock stealing.

## Important APIs, Types, and Functions
- `enum vcpu_state` tracks `VCPU_RUNNING`, `VCPU_HALTED`, and `VCPU_HASHED`.
- `struct pv_node` overlays qspinlock MCS nodes with CPU and state.
- `__pv_init_lock_hash()` allocates the PV hash table.
- `pv_hybrid_queued_unfair_trylock()`, `set_pending()`, and `trylock_clear_pending()` implement hybrid acquisition.
- `pv_hash()` and `pv_unhash()` map lock addresses to halted nodes.
- `pv_wait_node()`, `pv_kick_node()`, `pv_wait_head_or_lock()`, `__pv_queued_spin_unlock_slowpath()`, and `__pv_queued_spin_unlock()` implement wait/kick protocol.

## Control Flow
An incoming waiter may briefly steal the lock while no pending bit is set. Queued nodes initialize PV state and may halt early if their predecessor vCPU is not running. Queue-head waiters set pending to suppress stealing, try to acquire for a bounded spin, then hash themselves and store `_Q_SLOW_VAL` so unlock can find and kick them. Unlock normally cmpxchg-releases `_Q_LOCKED_VAL` to zero; if the byte is `_Q_SLOW_VAL`, it unhashes the queue-head node, releases the lock, and kicks that vCPU.

## State and Persistence
State is in-memory: qspinlock locked byte values, per-node vCPU state, and a boot-allocated open-addressed hash table sized to possible CPUs. No persistent storage.

## Dependencies and Integration Points
Requires architecture paravirt hooks `pv_wait()` and `pv_kick()`, `asm/qspinlock_paravirt.h` thunk support, memblock/hash allocation, qspinlock stat wrappers, and debug locks.

## Risks
Hash table correctness is critical: a slow-value unlock assumes exactly one discoverable hash entry. Ordering between hash insertion, `_Q_SLOW_VAL`, unhash, and wake/kick is enforced with barriers and must not be weakened. Hybrid unfair stealing improves light contention but depends on pending-bit discipline to avoid starving queued vCPUs.

## Test Signals
Boot and lock torture under overcommitted virtual machines, PV hash hop counters, kick/wake latency counters, corrupted slow-value warnings, `nopvspin` comparison, and stress of halted/running predecessor transitions.
