<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/sg.h -->
# sources/distributed-fs/ceph-client/include/scsi/sg.h

## Purpose
This header defines the SCSI generic userspace ABI for SG v3 and legacy SG interfaces: SG_IO request headers, iovec compatibility, status/info flags, ioctl numbers, reset values, defaults, request table entries, and old `sg_header`.

## Important APIs, Types, And Functions
Key ABI types are `sg_iovec_t`, `sg_io_hdr_t`, kernel-only `compat_sg_io_hdr`, `sg_scsi_id_t`, `sg_req_info_t`, and legacy `struct sg_header`. Constants define transfer directions (`SG_DXFER_*`), flags (`DIRECT_IO`, `MMAP_IO`, queue placement, no transfer), info bits, obsolete driver/status helpers, SG ioctl numbers, reset scopes, buffer/default queue sizes, timeout defaults, command queue controls, debug controls, and alternate typedef names.

## Control Flow
The ABI supports synchronous `SG_IO` and write/read style command submission. Userspace fills `sg_io_hdr`, command and data pointers, timeout, flags, and pack IDs; the kernel returns SCSI/masked/message/host/driver status, sense length, residual, duration, and info. Legacy `sg_header` paths preserve old write/read behavior and command-length override ioctls.

## State And Persistence
No kernel state is owned by the header, but ioctl constants manipulate per-file sg driver state such as reserved buffer size, force-pack-id, keep-orphan, command queueing, timeout, and debug flags. ABI structs must remain stable for userspace.

## Dependencies And Integration Points
It depends on compiler annotations and kernel compat types under `__KERNEL__`. It integrates userspace passthrough utilities, sg driver implementation, block/SCSI status packing, ioctl reset handling, and compatibility for 32-bit userspace.

## Risks
This is ABI-sensitive: layout, ioctl numbers, and shifted legacy status values must not change. User pointers and iovec counts require strict validation in implementation. Direct/mmap/no-transfer flags can affect data exposure and copying. Obsolete status/driver fields are retained for compatibility even when mid-layer semantics changed.

## Test Signals
Run SG_IO read/write/no-data passthrough, direct and mmap IO, iovec scatter-gather, sense-buffer truncation, residual and duration reporting, pack-id/orphan behavior, reset ioctls, compat 32-bit SG_IO, legacy `sg_header` commands, and ioctl number ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/sg.h -->
