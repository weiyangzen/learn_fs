# sources/distributed-fs/ceph-client/include/linux/rseq_types.h

## Purpose
`rseq_types.h` defines the per-task and per-mm storage structures used by restartable sequences and scheduler MM CID support.

## Important APIs, types, and functions
Important types are `struct rseq_event`, `struct rseq_ids`, `union rseq_slice_state`, `struct rseq_slice`, `struct rseq_data`, `struct sched_mm_cid`, `struct mm_cid_pcpu`, and `struct mm_mm_cid`. Constants include `RSEQ_HAS_RSEQ_VERSION_MASK`, `MM_CID_UNSET`, `MM_CID_ONCPU`, and `MM_CID_TRANSIT`.

## Control flow, state, and persistence
The header has no functions; it defines state layouts. `rseq_event` packs scheduler, ID-change, user-IRQ, registration-version, fatal, and slowpath flags for efficient stores. `rseq_ids` caches values last written to user space. Slice state tracks enabled/granted/yielded and expiration time. MM-CID structures track task CID ownership, per-CPU CIDs, deferred affinity updates, users, and locks for per-mm allocation/convergence.

## Dependencies and integration points
It depends on irq work and workqueue type definitions, cacheline alignment, raw spinlocks, mutexes, hlist nodes, and Kconfig options `CONFIG_RSEQ`, `CONFIG_RSEQ_SLICE_EXTENSION`, and `CONFIG_SCHED_MM_CID`. Scheduler, rseq syscall, fork/exit, affinity, and exit-to-user code consume these layouts through `task_struct` and `mm_struct`.

## Risks and test signals
Risks include layout changes that break optimized single-word stores, event-bit clearing that drops registration version, false sharing in hot paths, MM-CID state machine races, and empty-struct compatibility when configs are disabled. Test signals include build coverage across Kconfig matrices, scheduler migration/CID selftests, rseq ABI registration tests, cacheline/layout assertions, fork/exit CID cleanup, and affinity mode-change stress.
