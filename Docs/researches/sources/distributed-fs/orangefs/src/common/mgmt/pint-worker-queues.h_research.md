<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-queues.h -->
# sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-queues.h

Purpose: declares the active non-threaded queue worker attributes, state, and vtable.

Important types: `PINT_worker_queues_attr_t` has `ops_per_queue`, the batch size before moving to the next queue, and `timeout`, the microsecond wait for new operations where `0` means no timeout. `struct PINT_worker_queues_s` stores attributes, some legacy arrays (`ids`, `callouts`, `service_ptrs`, `hints`) that are not used in the visible active implementation, the managed queue list, pulled `qentries` buffer, mutex, and condition variable.

Control flow is defined by `pint-worker-queues.c`: posts enqueue operations; manager test/wait drives `do_work()` to service queued operations. No background threads are created.

State behavior: queues are external objects with separate lifetime, but the worker registers itself as producer/consumer while attached. Runtime state is process-local and protected by the worker mutex plus individual queue locks.

Dependencies include `pint-op.h`, `pint-queue.h`, generated locks, and the aggregate worker interface. Integration is through `PINT_WORKER_TYPE_QUEUES`.

Risks: unused fields may reflect stale design and can mislead maintainers. Attribute validation is not visible, so `ops_per_queue <= 0` would lead to invalid allocation or queue waits. Tests should include invalid attributes, attach/detach lifecycle, producer/consumer refs, and progress via manager polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-queues.h -->
