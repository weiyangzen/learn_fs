# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable-3level_types.h

Purpose: defines PAE i386 page-table value types and geometry for three-level paging.

Important APIs, types, and functions: typedefs page-table value/protection types as `u64`, defines `pte_t` and `pmd_t` unions with low/high 32-bit halves and full 64-bit values, and sets `ARCH_PAGE_TABLE_SYNC_MASK`, `PGDIR_SHIFT`, `PTRS_PER_PGD`, `PMD_SHIFT`, `PTRS_PER_PMD`, `PTRS_PER_PTE`, `MAX_POSSIBLE_PHYSMEM_BITS`, and `PGD_KERNEL_START`.

Control flow: no code executes. The constants describe PAE layout: four top-level PGD entries, PMDs with 512 entries mapping 2 MiB each, and PTE pages with 512 entries.

State and persistence: no state is owned.

Dependencies and integration points: included by `pgtable_32_types.h` under `CONFIG_X86_PAE`, consumed by PAE page-table operations, boot page-table allocation, and generic MM level-folding code.

Risks: split low/high representation underlies ordered update code in `pgtable-3level.h`. Geometry changes would invalidate boot page tables, swap encoding, and the 36-bit possible physical memory assumption.

Test signals: PAE 32-bit builds, highmem boot, page-table walk tests, PMD huge mapping where supported, swap encoding round trips, and compile-time checks for folded levels.
