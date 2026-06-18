# sources/distributed-fs/ceph-client/drivers/scsi/arm/queue.c

Purpose: implements a small exported SCSI command queue helper for ARM/Acorn-style SCSI host drivers. It stores `struct scsi_cmnd *` values in a fixed pool of queue entries and supports ordered insertion, target/lun/tag lookup, exclusion by busy target/lun bitmap, and command removal.

Important APIs/types/functions: private `QE_t` wraps a `list_head`, `SCpnt`, and optional debug magic. `queue_initialise()` allocates `NR_QE` entries with `kmalloc_objs()` and populates the free list. `__queue_add()` moves an entry from `free` to `head`, optionally at the head for priority commands. `queue_remove()`, `queue_remove_exclude()`, `queue_remove_tgtluntag()`, `queue_remove_cmd()`, `queue_remove_all_target()`, and `queue_probetgtlun()` traverse or modify the queue. All public symbols are exported for other SCSI drivers.

Control flow: callers initialize `Queue_t`, enqueue commands through the macros in `queue.h` or direct `__queue_add()`, then dequeue based on scheduling needs. `__queue_remove()` is the central primitive: it deletes a used entry, marks it free, pushes it back to the free list, and returns the stored command. Most operations take `queue_lock` with IRQ saving, making them usable in interrupt-adjacent host-driver paths.

State and persistence: all state is in-memory and per `Queue_t`: active commands in `head`, available entry objects in `free`, and the original allocation pointer in `alloc`. There is no persistence across driver unload or host reset. Debug magic detects use/free list corruption during development.

Dependencies and integration: depends on Linux list APIs, spinlocks, slab allocation, SCSI command/device APIs, request tags via `scsi_cmd_to_rq()`, and SCSI constants such as `REQUEST_SENSE`. Integration is by exported helper symbols consumed by legacy SCSI host drivers.

Risks and test signals: queue depth is fixed at 32 entries, so callers must handle enqueue failure. `queue_remove_all_target()` removes entries during `list_for_each()` without using a safe iterator; because `__queue_remove()` relinks the current node onto the free list, this is a list-walk corruption risk if more matching or nonmatching entries follow. `queue_remove_exclude()` indexes `target * 8 + (lun & 7)`, so high LUNs alias. Test signals are enqueue failure at capacity, REQUEST_SENSE head insertion, removal by tag, excluded busy LUN scheduling, concurrent IRQ-safe access, and debug-magic BUGs under misuse.
