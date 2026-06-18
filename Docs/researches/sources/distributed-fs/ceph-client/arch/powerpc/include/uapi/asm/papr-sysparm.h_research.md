<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-sysparm.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-sysparm.h

Purpose: Defines PAPR system-parameter get/set ioctl payload and limits.

Important APIs/types/functions: `PAPR_SYSPARM_MAX_INPUT`, `PAPR_SYSPARM_MAX_OUTPUT`, `struct papr_sysparm_io_block`, `PAPR_SYSPARM_IOC_GET`, and `PAPR_SYSPARM_IOC_SET`.

Control flow: Userspace supplies parameter ID, length, and optional data. GET may use input data for special parameters and returns output length/data; SET sends the supplied data to firmware.

State and persistence: System parameters persist in platform firmware or partition configuration; the ioctl block is transient.

Dependencies and integration points: Depends on PAPR miscdev ioctl ID and RTAS `ibm,get-system-parameter`/set equivalents.

Risks: GET uses `_IOWR` because input data can matter. On errors data is indeterminate, so callers must not reuse stale values. Bounds and firmware errno mapping are important.

Test signals: GET/SET ioctl tests for supported/unsupported parameters, bad lengths/formats, permission failures, and ABI size checks.

Source read size: 58 lines, 2072 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-sysparm.h -->
