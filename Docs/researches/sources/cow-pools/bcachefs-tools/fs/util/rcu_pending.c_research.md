# File Research: sources/cow-pools/bcachefs-tools/fs/util/rcu_pending.c

Purpose: Per-CPU batching layer for processing objects after RCU or SRCU grace periods.

Key APIs and behavior:
- Supports generic process callbacks plus special kvfree and call_rcu modes.
- Uses per-CPU `rcu_pending_pcpu` state with a darray of genradix-backed batches and fallback linked lists.
- Tracks grace-period poll cookies and moves expired objects into processing.
- Uses a single RCU callback per CPU to schedule worker processing, rearming while pending items remain.
- Provides dequeue APIs, including predicate-based claim/dequeue from current or all CPUs.

Integration:
- Implements `rcu_pending.h`.
- Wraps normal RCU and SRCU operations behind helper functions.
- Uses `darray`, `generic-radix-tree`, percpu allocation, workqueues, and `bch2_alloc_percpu_init`.

Risks and invariants:
- Locking is subtle: per-CPU spinlocks protect queues, but callbacks and work processing drop locks before invoking callbacks.
- kvfree mode encodes a low-bit flag in `rcu_head->func` for allocated heads.
- `rcu_pending_exit()` loops on barriers and work flushing until all pending/armed state drains.
