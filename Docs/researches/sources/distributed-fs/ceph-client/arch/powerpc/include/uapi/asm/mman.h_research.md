<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/mman.h

Purpose: Defines PowerPC memory mapping and protection flags.

Important APIs/types/functions: `PROT_SAO`, PowerPC `MAP_*` values, `MCL_*` values, and pkey execute-disable override with `PKEY_ACCESS_MASK`.

Control flow: mmap/mprotect/mlock/pkey syscalls decode these bits from userspace and apply PowerPC memory-management semantics.

State and persistence: Bits contribute to VMA protection and locking state maintained by mm core.

Dependencies and integration points: Depends on generic mman-common and PowerPC pkey support.

Risks: Flag collisions break syscall ABI. `PROT_SAO` and pkey execute-disable must match architecture behavior.

Test signals: mmap/mprotect/mlock tests, pkey permission tests including execute disable, and compat ABI checks.

Source read size: 35 lines, 1294 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/mman.h -->
