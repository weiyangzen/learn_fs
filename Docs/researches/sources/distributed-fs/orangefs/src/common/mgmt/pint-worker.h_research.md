<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker.h -->
# sources/distributed-fs/orangefs/src/common/mgmt/pint-worker.h

Purpose: aggregate worker interface for the management subsystem. It defines worker ids, worker type selection, the attribute union, the implementation-instance union, and the vtable contract used by `pint-mgmt.c`.

Important types: `PINT_worker_type_t` enumerates queue, threaded queue, per-op, pool, blocking, and external workers. `PINT_worker_attr_t` combines a type with a union of implementation-specific attributes. `PINT_worker_inst` stores one implementation-specific state struct. `struct PINT_worker_impl` defines callbacks for init, destroy, queue add/remove, post, do-work, and cancel.

Control flow: managers create workers by type, copy attributes into the instance, then call vtable methods. Queue-capable workers implement queue add/remove and often post to a specific queue. Workers with background execution omit `do_work`; workers that require polling implement it. `post()` returns `PINT_MGMT_OP_POSTED`, `PINT_MGMT_OP_COMPLETE`, or a negative error according to the contract.

State behavior is delegated to implementation instances. The shared contract says posted `PINT_operation_t` objects are managed outside the worker and can be queued directly via embedded entries.

Dependencies include every worker-specific header and `pint-context.h`, so this header is a broad integration point. Risks: including all worker headers increases coupling and can expose stale types. The comments mention `PINT_MGMT_OP_COMPLETE`, while code uses `PINT_MGMT_OP_COMPLETED`, so documentation and names should be checked. Tests should compile every worker type through manager creation and verify vtable NULL callback handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker.h -->
