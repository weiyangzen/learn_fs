<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-op.h -->
# sources/distributed-fs/orangefs/src/common/mgmt/pint-op.h

Purpose: defines the management operation object and service callback signature. It is the shared payload type that managers post to workers and workers service.

Important types: `PINT_op_id` is a generated id. `PINT_service_callout` takes a user operation pointer and `PVFS_hint`, returning `0` or a negative OrangeFS error. `PINT_operation_t` stores the id, service callback, optional cancel callback, operation pointer, hint, timestamp for queue/service timing, and embedded `PINT_queue_entry_t` to avoid extra allocation when queued.

Important helpers: `PINT_op_queue_find_op_id_callback()` supports queue search by id. `PINT_op_from_qentry(qe)` recovers the containing `PINT_operation_t`. `PINT_operation_fill` appears intended to initialize operations but references fields/names that do not match the struct (`op_id`, `fn`, `operation`), so it looks stale or broken.

State behavior: operations are usually embedded inside `struct PINT_op_entry` owned by `pint-mgmt.c`, and their queue entry moves through worker queues. No persistence is involved.

Risks: intrusive queue embedding means an operation can be in only one queue at a time, and queue link fields must be zeroed before reuse. The stale fill macro should be treated as a warning sign and tested or removed if unused. Test signals include service callback invocation with hints, queue container recovery, cancel callback expectations, and compile checks for macros under strict warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-op.h -->
