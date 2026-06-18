<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/opal-prd.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/opal-prd.h

Purpose: Defines the userspace ABI for OPAL runtime diagnostics daemon access on PowerNV systems.

Important APIs/types/functions: `OPAL_PRD_KERNEL_VERSION`, ioctls `OPAL_PRD_GET_INFO`, `OPAL_PRD_SCOM_READ`, `OPAL_PRD_SCOM_WRITE`, `struct opal_prd_info`, and `struct opal_prd_scom`.

Control flow: The PRD daemon opens `/dev/opal-prd`, queries interface info, and requests SCOM reads/writes with chip/address/data fields and firmware return code.

State and persistence: The kernel mediates firmware diagnostic state; SCOM accesses target persistent hardware registers.

Dependencies and integration points: Depends on OPAL firmware, PowerNV PRD driver, ioctl encoding, and userspace opal-prd daemon.

Risks: SCOM access is privileged and hardware-sensitive. ABI versioning must remain backward compatible.

Test signals: opal-prd daemon startup, GET_INFO ioctl, SCOM read/write error-path tests on PowerNV, and headers compile tests.

Source read size: 59 lines, 1784 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/opal-prd.h -->
