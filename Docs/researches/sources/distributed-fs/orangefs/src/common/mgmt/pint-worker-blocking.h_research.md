<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-blocking.h -->
# sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-blocking.h

Purpose: declares the blocking worker implementation object. It is a small integration header included by `pint-worker.h` so the manager can select `PINT_worker_blocking_impl` for `PINT_WORKER_TYPE_BLOCKING`.

Important API: `extern struct PINT_worker_impl PINT_worker_blocking_impl;`. There are no attributes or instance state for this worker type.

Control flow and state are defined by the vtable in `pint-worker-blocking.c`: posting runs the operation synchronously and returns a completion/error status. No queue, thread, or persistent state is associated with this header.

Dependencies: includes `pint-op.h` for operation types and depends on `struct PINT_worker_impl` being visible through include ordering in `pint-worker.h` users.

Risks are mostly integration-level: this header must not be included in a context that requires the full `PINT_worker_impl` definition before `pint-worker.h` supplies it. Test signals are compile checks through the aggregate worker header and manager creation that always installs a blocking worker.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-blocking.h -->
