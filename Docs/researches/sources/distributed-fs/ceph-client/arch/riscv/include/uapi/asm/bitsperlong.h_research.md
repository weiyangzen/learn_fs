<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/bitsperlong.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/bitsperlong.h

Purpose: Defines UAPI word-size selection for RISC-V user headers.

Important APIs/types/functions: Sets `__BITS_PER_LONG` based on ABI and includes generic bitsperlong.

Control flow: No runtime flow; compile-time ABI selection.

State and persistence: No state; affects userspace struct layout.

Dependencies and integration points: Used by all UAPI headers with long-sized fields.

Risks: Wrong value breaks 32-bit/64-bit userspace ABI.

Test signals: headers_install, RV32/RV64 libc builds, and ABI struct-size checks.

Source read size: 14 lines, 377 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/bitsperlong.h -->
