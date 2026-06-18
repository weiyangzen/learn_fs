<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable-32.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable-32.h

Purpose: Defines the RV32 page-table geometry and PTE bit masks used by the common RISC-V pgtable layer.

Important APIs/types/functions: Key definitions are `PGDIR_SHIFT`, `PGDIR_SIZE`, `PGDIR_MASK`, `MAX_POSSIBLE_PHYSMEM_BITS`, `_PAGE_PFN_MASK`, `_PAGE_CHG_MASK`, and zero-valued cacheability attributes.

Control flow: There is no runtime control flow; including `asm-generic/pgtable-nopmd.h` folds PMD and higher levels for Sv32.

State and persistence: No state is stored; constants shape every RV32 page-table walk and swap/PFN encoding.

Dependencies and integration points: Used by `pgtable.h` for non-64-bit builds and by generic MM macros that consume folded page-table levels.

Risks: Changing shifts or PFN masks breaks Sv32 virtual layout, physical address reach, and swap/PTE preservation semantics.

Test signals: RV32 defconfig build, boot, mmap boundary tests, highmem/physical-memory sizing, and page-table selftests.

Source read size: 39 lines, 1092 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable-32.h -->
