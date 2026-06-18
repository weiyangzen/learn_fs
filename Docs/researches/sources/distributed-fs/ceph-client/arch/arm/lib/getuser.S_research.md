# sources/distributed-fs/ceph-client/arch/arm/lib/getuser.S

Purpose: implements low-level `__get_user_1/2/4/8` helpers, plus big-endian transfer variants, returning an error code in r0 and loaded value in r2/r3.

Control flow validates address limits with `check_uaccess`, performs user loads with size-appropriate instructions or byte assembly on older CPUs, and uses exception-table fixups to zero outputs and return `-EFAULT`. State is none besides loaded registers. Dependencies include uaccess macros, domain/PAN configuration, exception tables, and `asm/uaccess.h` register conventions. Risks are preserving required registers, endian assembly for subword values, and fault handling for the high word of 64-bit loads. Test signals include get_user tests for each size, invalid pointers, boundary crossings, and BE-specific variants.
