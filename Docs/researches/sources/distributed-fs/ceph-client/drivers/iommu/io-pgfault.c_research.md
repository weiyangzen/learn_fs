<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgfault.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/io-pgfault.c

Purpose: generic I/O page-fault framework used by IOMMU drivers. It groups PRI page-request faults, routes them to the correct domain IOPF handler, manages per-device fault queues, sends failure responses on errors/removal, and flushes outstanding fault work.

Important APIs/types/functions: exported functions include `iommu_report_device_fault()`, `iopf_queue_alloc()`, `iopf_queue_free()`, `iopf_queue_add_device()`, `iopf_queue_remove_device()`, `iopf_queue_flush_dev()`, `iopf_group_response()`, `iopf_free_group()`, and `iopf_queue_discard_partial()`. Internal helpers manage `iommu_fault_param` references, partial faults, group allocation, and attach-handle lookup.

Control flow: drivers report low-level faults through `iommu_report_device_fault()`. Non-last group faults are copied to a per-device partial list. The last fault creates a group, moves matching partial faults before the last fault, registers it pending, finds the domain/PASID attach handle, and calls the domain `iopf_handler`. Handlers must later call `iopf_group_response()` and `iopf_free_group()`. Error paths respond invalid/failure and free groups. Queue add installs a refcounted fault parameter under RCU; removal invalidates partial and pending groups, sends invalid responses, unlinks the device, and drops the RCU reference.

State and persistence: per-device `fault_param` stores partial/pending lists, queue pointer, lock, refcount, and device pointer. Queue state stores a workqueue, device list, and lock. Fault groups persist until handlers respond/free them.

Dependencies and integration: used by Intel PRQ and generic SVA. It depends on core IOMMU attach handles, per-domain `iopf_handler`, device `iommu_ops->page_response`, RCU, mutexes, and workqueues.

Risks: callers must stop new hardware faults before flushing/removing queues. Partial group matching uses `grpid` only within a device fault parameter. Missing page-response ops rejects queue add. User-managed PASID tables route PASID faults through the nested RID domain when direct PASID handle lookup fails.

Test signals: multi-fault group assembly, non-last fault postponement, handler success/failure, queue flush on PASID teardown, queue remove with pending groups, overflow partial discard, and RCU/refcount stress with concurrent reports/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgfault.c -->
