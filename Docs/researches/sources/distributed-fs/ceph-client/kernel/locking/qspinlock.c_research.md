# sources/distributed-fs/ceph-client/kernel/locking/qspinlock.c

## Purpose
Implements the queued spinlock slow path for compact 32-bit `qspinlock` words. It combines a pending-bit fast handoff with an MCS-style per-CPU queue encoded into the tail bits, and can recursively include itself to generate paravirtualized spinlock slow paths.

## Important APIs, Types, and Functions
- Exports `queued_spin_lock_slowpath()`.
- Maintains per-CPU `qnodes[_Q_MAX_NODES]`.
- Uses helpers from `qspinlock.h`: `encode_tail()`, `decode_tail()`, `grab_mcs_node()`, `xchg_tail()`, `clear_pending_set_locked()`, and `set_locked()`.
- Uses PV callback aliases `pv_init_node()`, `pv_wait_node()`, `pv_kick_node()`, and `pv_wait_head_or_lock()`.
- Defines the `nopvspin` early parameter when paravirt spinlocks are enabled.

## Control Flow
The slow path first handles a pending-only transient, then tries to set the pending bit when the lock has no queue. If it becomes pending, it waits for the locked byte to clear and atomically becomes owner. If contention exists, it allocates a per-CPU MCS node by nesting index, initializes it, optionally retries the lock, publishes its encoded tail with `xchg_tail()`, links after a predecessor, and waits until it reaches queue head. At head, it waits for locked and pending bits to clear or lets PV code acquire; then it either clears the tail and takes the lock or sets only the locked byte and wakes its successor.

## State and Persistence
State is a compact lock word containing locked, pending, and tail fields, plus per-CPU queue nodes. It is volatile only. Nested contexts are limited to task, softirq, hardirq, and nmi; overflow falls back to direct trylock spinning.

## Dependencies and Integration Points
Depends on architecture qspinlock definitions, MCS spinlock helpers, per-CPU storage, trace lock events, optional PV spinlocks, and lock event counters. This is the slow path behind architecture `queued_spin_lock()`.

## Risks
The 32-bit encoding relies on architecture support for atomic byte/halfword operations and CPU count fitting in tail bits. Memory barriers before tail publication and acquire waits at queue head are correctness-critical. Node nesting overflow is rare but intentionally less fair. PV generation through recursive inclusion can be fragile when macros change.

## Test Signals
SMP lock torture, nested interrupt locking, high CPU-count builds, paravirt and native build matrix, `nopvspin` boot parameter tests, and lock event counters for pending, slowpath, no-node, and node-index usage.
