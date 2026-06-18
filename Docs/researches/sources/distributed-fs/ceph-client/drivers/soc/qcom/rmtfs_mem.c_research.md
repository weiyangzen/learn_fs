# sources/distributed-fs/ceph-client/drivers/soc/qcom/rmtfs_mem.c

## Purpose

`rmtfs_mem.c` exposes a reserved memory region for Qualcomm remote filesystem use as `/dev/qcom_rmtfs_mem<client_id>` plus sysfs attributes. It allows userspace remote-filesystem daemons to read, write, and mmap modem-owned shared memory and optionally assigns SCM VM permissions.

## Important APIs, Types, and Functions

`struct qcom_rmtfs_mem` embeds `struct device` and `struct cdev`, the write-combined mapping, physical address, size, client id, and SCM permission mask. File operations implement open/read/write/release/mmap. Sysfs attributes expose `phys_addr`, `size`, and `client_id`. Probe parses reserved memory, `qcom,client-id`, optional guard pages, optional `qcom,vmid`, creates the cdev device, maps memory, and performs `qcom_scm_assign_mem()` when requested.

## Control Flow

Module init registers class, allocates a char-dev major range, and registers the platform driver. Probe locates reserved memory, trims guard pages if requested, initializes the embedded device, maps the region with `MEMREMAP_WC`, registers the cdev, parses up to two VMIDs, and if VMIDs are present assigns the memory to HLOS plus those VMs with RW permissions. Reads/writes clamp count at region size and copy to/from the mapped memory. Mmap remaps the physical range with write-combine protection. Remove reassigns memory to HLOS when permissions were changed, deletes the cdev, and drops the device reference.

## State and Persistence Behavior

The reserved memory contents persist independently of the driver and are visible to remote firmware/userspace. Driver state persists while the platform device exists. SCM permission changes affect secure world memory ownership until remove reassigns them or the system resets.

## Dependencies and Integration Points

Dependencies include reserved-memory DT, char device core, custom class, sysfs, memremap, mmap remapping, copy_to/from_user, and Qualcomm SCM. It integrates with remote filesystem userspace and remote processors expecting the shared physical memory and client id.

## Risks and Edge Cases

Guard-page trimming subtracts 8 KiB without checking the reserved region is large enough. Client ids map directly to device minor numbers; invalid ids above `MINORMASK` are not explicitly rejected before `MKDEV()`. Read/write arithmetic uses `*f_pos + count`, which can overflow `loff_t`/size_t combinations. No locking protects concurrent readers/writers. VMID parsing with zero elements and absent property relies on OF return conventions.

## Test Signals

Test reserved-memory absence, missing client id, small guard-page regions, invalid client ids, read/write at boundaries and EOF, mmap larger than region, SCM unavailable/deferred/failure paths, permission reassignment on remove, cdev registration failure, and concurrent open/remove lifetime handling.
