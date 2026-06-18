<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-miscdev.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-miscdev.h

Purpose: Provides the common ioctl type ID for PAPR misc character devices.

Important APIs/types/functions: Enum value `PAPR_MISCDEV_IOC_ID = 0xb2`.

Control flow: PAPR UAPI headers use this ID when constructing ioctl numbers for their misc devices.

State and persistence: No runtime state; it reserves an ioctl namespace.

Dependencies and integration points: Included by PAPR sysparm, VPD, indices, dump, attestation, and hvpipe headers.

Risks: Changing the ID renumbers every PAPR miscdev ioctl.

Test signals: Compile-time ioctl-number checks across PAPR headers and userspace tool compatibility tests.

Source read size: 9 lines, 199 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-miscdev.h -->
