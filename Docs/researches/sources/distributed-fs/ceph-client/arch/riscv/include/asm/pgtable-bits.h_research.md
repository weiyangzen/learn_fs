<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable-bits.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable-bits.h

Purpose: Centralizes RISC-V PTE bit definitions shared by 32-bit and 64-bit pgtable code.

Important APIs/types/functions: Defines hardware bits such as `_PAGE_PRESENT`, `_PAGE_READ`, `_PAGE_WRITE`, `_PAGE_EXEC`, `_PAGE_USER`, `_PAGE_GLOBAL`, `_PAGE_ACCESSED`, `_PAGE_DIRTY`, plus Linux software bits like `_PAGE_PROT_NONE`, `_PAGE_SPECIAL`, `_PAGE_TABLE`, `_PAGE_LEAF`, soft-dirty, uffd-wp, and swap-exclusive encodings.

Control flow: No runtime flow; macros compose hardware and software permissions used by page table creation and mutation.

State and persistence: PTE bit layout is persistent ABI-like kernel state because live page tables, swap PTEs, and migration entries store these values.

Dependencies and integration points: Consumed by `pgtable.h`, `pgtable-32.h`, `pgtable-64.h`, fault handlers, swap code, THP, and userfaultfd/soft-dirty support.

Risks: Bit collisions with hardware extensions or vendor PMA/Svpbmt bits can make valid entries fault, grant unintended access, or lose swap metadata.

Test signals: Build matrix for soft-dirty, uffd-wp, THP, swap, Svrsw60t59b, Svpbmt, and page-table selftests.

Source read size: 78 lines, 2334 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable-bits.h -->
