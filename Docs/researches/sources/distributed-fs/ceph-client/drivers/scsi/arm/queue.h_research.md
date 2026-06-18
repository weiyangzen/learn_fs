# sources/distributed-fs/ceph-client/drivers/scsi/arm/queue.h

Purpose: declares the public contract for the ARM SCSI queue helper implemented in `queue.c`.

Important APIs/types/functions: `Queue_t` owns the active list, free list, spinlock, and allocation base. The header declares initialization, teardown, generic dequeue, exclude-based dequeue, target/lun/tag dequeue, target-wide removal, target/lun probing, command-specific removal, and raw `__queue_add()`. `queue_add_cmd_ordered()` places `REQUEST_SENSE` at the head; `queue_add_cmd_tail()` appends normally.

Control flow: host drivers include this header, allocate a `Queue_t`, call `queue_initialise()`, enqueue commands through the macros, dequeue with the selector matching their scheduler or error-recovery path, and finally call `queue_free()`.

State and persistence: `Queue_t` is intentionally small and caller-owned. The helper manages only volatile command pointers and list nodes; commands themselves remain owned by the SCSI mid-layer or host driver.

Dependencies and integration: requires prior visibility of `struct list_head`, `spinlock_t`, `struct scsi_cmnd`, and `REQUEST_SENSE` through including C files. It is a narrow integration layer between SCSI host drivers and the queue implementation exports.

Risks and test signals: the macro API evaluates `SCpnt` more than once, so callers should pass stable expressions. The header exposes `__queue_add()`, allowing callers to bypass ordering policy. Build tests should compile users with modern SCSI headers; behavioral tests should verify macro ordering and every declared symbol links to the exported implementation.
