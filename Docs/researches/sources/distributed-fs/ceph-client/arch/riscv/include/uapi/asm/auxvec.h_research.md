<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/auxvec.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/auxvec.h

Purpose: Defines RISC-V ELF auxiliary vector constants for userspace capability discovery.

Important APIs/types/functions: Defines `AT_SYSINFO_EHDR`, cache geometry auxvec keys, and RISC-V-specific entries such as hardware capability exposure.

Control flow: ELF loader populates auxvec entries at exec; userspace reads them through libc/getauxval.

State and persistence: Auxvec values are per-process exec-time ABI state.

Dependencies and integration points: Used by ELF loader, vDSO setup, libc, dynamic linkers, and hwcap code.

Risks: Changing numbers breaks userspace ABI.

Test signals: getauxval tests, vDSO mapping checks, dynamic linker smoke tests, and cache/hwcap reporting.

Source read size: 40 lines, 1232 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/auxvec.h -->
