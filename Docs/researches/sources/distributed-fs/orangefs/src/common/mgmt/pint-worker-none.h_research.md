<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-none.h -->
# sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-none.h

Purpose: companion header for the obsolete/non-built `pint-worker-none.c` queue worker prototype. It is not included by the active aggregate `pint-worker.h` in this tree.

Important definitions: it includes `pint-mgmt.h`, defines `PINT_worker_queues_attr_t` with `ops_per_queue` and `timeout`, and defines `struct PINT_worker_queues_s` with arrays of ids, service callbacks, service pointers, hints, and a queue list. This conflicts conceptually with the active `pint-worker-queues.h`, which uses `PINT_queue_entry_t *qentries`, mutex, and condition variable.

Control flow is declarative only. It provides data shape for a worker that would service operations without dedicated threads, but the implementation and active API have diverged.

State behavior is intended as in-memory queue-worker state; there is no persistence. Dependencies are management and queue/list types through included headers.

Risks: duplicate names with the active queues worker can cause type redefinition or ABI confusion if included together. It also omits include guards, increasing accidental multi-include risk. Test signal is a compile/include scan proving no active source includes this header; if it must be revived, first add guards and reconcile it with `pint-worker-queues.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-none.h -->
