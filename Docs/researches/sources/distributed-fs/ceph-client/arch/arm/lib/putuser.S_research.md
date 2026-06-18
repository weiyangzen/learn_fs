# sources/distributed-fs/ceph-client/arch/arm/lib/putuser.S

Purpose: implements low-level `__put_user_1/2/4/8` helpers, storing r2/r3 values to user memory and returning an error code in r0.

Control flow validates address limits with `check_uaccess`, performs user stores with size-appropriate instructions or byte splitting on older CPUs, and uses exception-table fixups to return `-EFAULT`. State is user memory only. Dependencies include uaccess/domain macros, exception tables, and register conventions from `asm/uaccess.h`. Risks include partial stores on faults, endian handling for 16-bit stores on pre-v6 CPUs, and preserving required registers. Test signals include put_user tests for each size, invalid pointers, page-boundary faults, and BE/LE builds.
