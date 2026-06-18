<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-none.c -->
# sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-none.c

Purpose: appears to be an obsolete or non-built prototype for a no-thread queue worker. It is not listed in `src/common/mgmt/module.mk.in`, and its implementation does not match the active `PINT_worker_impl` signature used by `pint-worker.h`.

Important observations: functions named `PINT_worker_queues_init/destroy/queue_add/queue_remove/post/do_work` try to manage queues and service operations in the caller/test path. The exported `PINT_worker_queues_impl` uses name `NONE`, but the initializer is syntactically inconsistent with the active vtable definition. The code references fields and functions not present in the active headers, such as `inst->queues.ops`, `PINT_manager_serviced`, `PINT_MGMT_DEBUG`, and sometimes passes queue entries or links without address operators.

Control flow mirrors the active `pint-worker-queues.c`: add queues to a list, post operations to queues, round-robin over queues, wait/pull operations, service them, and push unserviced work back if the timeout expires. However, the code as read is unlikely to compile against the current active API.

State is intended to be in `PINT_worker_queues_s`, with queue list, operation buffers, locks, and condition variable. Dependencies include `pint-queue`, manager types, generated ids, locks, and errors.

Risks: high. This file looks stale and should remain excluded unless repaired. If accidentally added to the build it would likely fail compilation or conflict with `PINT_worker_queues_impl` from `pint-worker-queues.c`. Test signal is primarily build-system validation that it is intentionally excluded, or a dedicated cleanup task to delete/modernize it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-none.c -->
