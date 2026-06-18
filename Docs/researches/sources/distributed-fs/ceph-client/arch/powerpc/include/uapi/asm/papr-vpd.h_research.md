<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-vpd.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-vpd.h

Purpose: Defines PAPR VPD location-code ioctl ABI.

Important APIs/types/functions: `struct papr_location_code` with 80-byte string and `PAPR_VPD_IOC_CREATE_HANDLE`.

Control flow: Userspace passes a location code and receives a handle file descriptor to read matching VPD data.

State and persistence: VPD data is platform firmware state; the location-code block is ioctl input.

Dependencies and integration points: Depends on PAPR miscdev ioctl ID and VPD driver/firmware interfaces.

Risks: Location code length is fixed by PAPR. Missing NUL or overlong strings must be rejected safely.

Test signals: VPD handle creation/read tests, invalid location-code tests, and structure layout checks.

Source read size: 22 lines, 553 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-vpd.h -->
