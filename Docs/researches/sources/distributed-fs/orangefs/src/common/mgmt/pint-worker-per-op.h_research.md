<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-per-op.h -->
# sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-per-op.h

Purpose: declares the thread-per-operation worker attributes, state, and implementation vtable.

Important types: `PINT_worker_per_op_attr_t` contains `max_threads`, intended to bound concurrent service threads. `struct PINT_worker_per_op_s` stores the copied attributes and current `service_count`. The header exports `PINT_worker_per_op_impl`.

Control flow is defined in the C file: each post spawns a detached thread that services and completes one operation. There are no queue APIs for this worker type.

State behavior: `service_count` is a runtime counter used by destroy to reject teardown while operations are active. No persistent state or cross-process coordination exists.

Dependencies are `pint-op.h`, pthread use in the implementation, and the aggregate worker API. Integration is selected through `PINT_WORKER_TYPE_PER_OP`.

Risks: the header's `max_threads` contract is stronger than the implementation, which does not enforce it. Callers relying on backpressure may overload the process. Tests should assert whether `max_threads` is honored; current expected behavior would reveal it is not.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-per-op.h -->
