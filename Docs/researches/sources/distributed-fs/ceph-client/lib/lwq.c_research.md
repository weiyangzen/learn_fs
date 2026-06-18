# sources/distributed-fs/ceph-client/lib/lwq.c

Purpose: lightweight queue built from an atomic producer `llist` plus a spinlocked ready list for single-item or batch dequeue by consumers.

Important APIs/types/functions: `__lwq_dequeue()`, `lwq_dequeue_all()`, optional `lwq_exercise()` and `lwq_test()` under `CONFIG_LWQ_TEST`.

Control flow: dequeue first checks `lwq_empty()`, takes the lock, consumes `ready` if present, otherwise marks ready with a temporary non-null sentinel, drains `new` with `llist_del_all()`, reverses it to FIFO order, and advances `ready`. Batch dequeue clears `ready`, drains `new`, unlocks, appends reversed new entries after the old ready chain, and returns the whole list.

State/persistence: `struct lwq` owns an atomic `new` llist, spinlock, and `ready` chain. Optional test allocates nodes, starts kthreads, re-enqueues work, and prints queue contents.

Dependencies/integration: depends on `llist` helpers, RCU/update headers, spinlocks, wait variables, and queue macros from `linux/lwq.h`.

Risks: sentinel `(void *)1` relies on `lwq_empty()` semantics and must not leak as a real node. Multiple dequeuers are serialized by the spinlock, while producers can enqueue from any context.

Test signals: optional module test stresses threaded dequeue/requeue, batch dequeue, safe iteration deletion, and remaining order.
