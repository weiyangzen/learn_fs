<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pr.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pr.h

Purpose: defines persistent reservation ioctl payloads, status values, reservation types, and key-query structures for block devices.

Important APIs and types: `enum pr_status` reports success, I/O error, reservation conflict, retryable path failure, fast path failure, and failed path states. `enum pr_type` includes write-exclusive, exclusive-access, registrants-only, and all-registrants modes. `struct pr_reservation`, `pr_registration`, `pr_preempt`, and `pr_clear` carry command arguments. `struct pr_read_keys` and `struct pr_read_reservation` query registered keys and the current reservation. `IOC_PR_*` ioctls register, reserve, release, preempt, clear, and read reservation state; `PR_FL_IGNORE_KEY` and `PR_KEYS_MAX` bound behavior.

Control flow: userspace reservation tools issue ioctls through the block layer using these structs to register keys, reserve, release, preempt, clear, or report reservation behavior. Kernel block/SCSI code translates requests to persistent reservation commands.

State and persistence: reservation keys and reservation state persist in target storage device firmware according to SCSI PR semantics. Header structs serialize commands but do not store state locally.

Dependencies and integration points: depends on Linux types. Integrates with block device ioctls, SCSI/NVMe reservation support, multipath clustering, fencing, and shared-storage failover tools.

Risks and test signals: risks include data-loss from incorrect preempt/clear, key pointer validation in read-key queries, unsupported target semantics, and cluster split-brain. Test registration/reserve/release/preempt/clear against capable devices or scsi_debug, read keys/reservation buffer sizing, multipath failover, permission checks, and invalid type/flag rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pr.h -->
