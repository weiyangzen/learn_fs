<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/hwcap.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/hwcap.h

Purpose: Defines legacy RISC-V ELF HWCAP bits exposed to userspace.

Important APIs/types/functions: Defines `COMPAT_HWCAP_ISA_*` bits for base ISA letters such as I/M/A/F/D/C/V.

Control flow: Kernel populates auxvec HWCAP based on probed ISA; userspace reads it.

State and persistence: Per-process auxvec hardware capability state.

Dependencies and integration points: Used by ELF loader, libc dispatch, and CPU feature parsing.

Risks: Wrong bits cause userspace to execute unsupported instructions or miss optimizations.

Test signals: getauxval/hwcap tests, libc ifunc dispatch, QEMU extension matrix.

Source read size: 26 lines, 973 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/hwcap.h -->
