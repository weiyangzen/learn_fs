# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-platform-dump.c

## Purpose
Implements `/dev/papr-platform-dump`, a userspace interface for streaming platform dumps from the hypervisor and invalidating completed dumps.

## Important APIs, Types, And Functions
The core state is `struct ibm_platform_dump_params`. Major functions are `rtas_ibm_platform_dump`, `papr_platform_dump_handle_read`, `papr_platform_dump_handle_release`, `papr_platform_dump_invalidate_ioctl`, `papr_platform_dump_create_handle`, and `papr_platform_dump_dev_ioctl`. Global synchronization uses `platform_dump_list_mutex` and `platform_dump_list`.

## Control Flow
Userspace passes a dump tag to the miscdevice create-handle ioctl. The driver rejects duplicate in-progress tags, allocates params and a 4K work area, creates an anonymous fd, and adds the request to the list. Each read calls RTAS with the current dump tag and sequence numbers, copies returned bytes to userspace, and updates sequence/status. When firmware reports complete, the next read returns EOF and marks the local buffer length zero. A handle ioctl invalidates the completed dump by calling RTAS with a NULL buffer.

## State And Persistence
Each open dump fd owns RTAS sequence numbers, bytes returned, status, work area, and list membership. The hypervisor retains the dump until userspace invalidates it after complete retrieval. Kernel state is freed on fd release.

## Dependencies And Integration Points
Depends on RTAS `ibm,platform-dump`, RTAS work areas, anonymous inodes, miscdevice/ioctl/read handlers, and uapi `papr-platform-dump` definitions.

## Risks And Edge Cases
Duplicate dump tags are blocked to avoid interleaving one dump stream. Reads require at least 1 KiB and are capped to the 4K work area. Firmware-reported bytes larger than the user buffer are treated as a kernel/firmware bug and fail. Invalidating before complete returns `-EINPROGRESS`; mismatched dump tags return `-EINVAL`.

## Test Signals
Test create/read/invalidate/release with complete and multi-read dumps, duplicate dump tag rejection, small read buffers, unauthorized and hardware RTAS errors, invalidation before EOF, mismatched invalidation tag, and cleanup when userspace closes without invalidating.
