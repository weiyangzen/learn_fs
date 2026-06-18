<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/vectors.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/vectors.h

Purpose: computes kernel and exception vector virtual addresses for Xtensa, including MMU V3 remapping and optional configurable vector base. Important definitions include `KERNELOFFSET`, `RESET_VECTOR1_VADDR`, `VECBASE_VADDR`, `VECTOR_VADDR`, and addresses for user, kernel, double exception, window, interrupt-level, and debug vectors.

Control flow is compile-time address selection based on MMU, PTP MMU, spanning-way, kernel virtual address, and vector-base capability. Persistent state is linker/boot mapping expectations rather than runtime variables. Dependencies include `asm/core.h`, `asm/kmem_layout.h`, XCHAL vector constants, and Kconfig. Integration points are vector assembly, linker script, boot MMU initialization, secondary reset vector, and exception dispatch. Risks include wrong vector address under VECBASE or MMU V3, a likely typo mapping `INTLEVEL7_VECTOR_VADDR` to the level 6 constant in the non-VECBASE branch, and stale XCHAL undef behavior. Test signals include boot on VECBASE/non-VECBASE cores, interrupt/debug exception entry, map-file validation, and vector relocation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/vectors.h -->
