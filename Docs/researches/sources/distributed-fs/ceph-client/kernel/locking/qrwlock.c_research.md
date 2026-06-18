# sources/distributed-fs/ceph-client/kernel/locking/qrwlock.c

## Purpose
Provides slow paths for queued read/write spin locks. The implementation uses a small counter field for reader/writer state and a queued `wait_lock` to serialize slow readers and writers.

## Important APIs, Types, and Functions
- Exports `queued_read_lock_slowpath()` and `queued_write_lock_slowpath()`.
- Uses `struct qrwlock` fields `cnts` and `wait_lock`.
- Uses `_QW_LOCKED`, `_QW_WAITING`, and `_QR_BIAS` from qrwlock definitions.

## Control Flow
Slow readers in interrupt context do not queue; they spin with acquire semantics until no writer holds the lock. Process-context readers subtract their speculative read bias, queue on `wait_lock`, re-add the reader bias, wait until the writer-locked bit clears, and release the queue head. Writers take `wait_lock`, try to set `_QW_LOCKED` directly when no readers exist, otherwise set `_QW_WAITING` and spin until the counters equal waiting-only, then atomically promote to locked.

## State and Persistence
State is the in-memory `cnts` atomic and embedded queue spinlock. No external persistence.

## Dependencies and Integration Points
Depends on architecture spinlock primitives, SMP atomics, trace lock events, and interrupt context checks. Integrated under the raw rwlock implementation on architectures selecting queued rwlocks.

## Risks
Reader behavior differs in interrupt context to avoid blocking behind a queued writer that is not yet owner. Writer fairness depends on setting `_QW_WAITING` so new readers observe pending writer state. Memory ordering in `atomic_cond_read_acquire()` and `atomic_try_cmpxchg_acquire()` is required for critical-section ordering.

## Test Signals
Stress with mixed interrupt/process readers, writer-heavy contention, lockdep, and trace `LCB_F_READ`/`LCB_F_WRITE` contention. Regression symptoms are writer starvation, reader admission while writer locked, or deadlocks on `wait_lock`.
