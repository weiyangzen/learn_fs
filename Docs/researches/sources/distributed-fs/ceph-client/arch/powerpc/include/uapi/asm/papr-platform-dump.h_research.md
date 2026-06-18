<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-platform-dump.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-platform-dump.h

Purpose: Defines ioctls for PAPR platform dump handle creation and invalidation.

Important APIs/types/functions: `PAPR_PLATFORM_DUMP_IOC_CREATE_HANDLE` and `PAPR_PLATFORM_DUMP_IOC_INVALIDATE`, both keyed by dump tag.

Control flow: Userspace creates a file descriptor for a platform dump tag, reads dump data through the handle, and can invalidate the firmware dump record.

State and persistence: Platform dump content persists in firmware/driver storage until invalidated.

Dependencies and integration points: Depends on PAPR miscdev ioctl ID and platform dump driver.

Risks: Invalidating the wrong tag can discard diagnostic data. Ioctl numbers are ABI.

Test signals: Platform dump discovery/read/invalidate tests on pSeries and error-path tests for missing tags.

Source read size: 16 lines, 528 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-platform-dump.h -->
