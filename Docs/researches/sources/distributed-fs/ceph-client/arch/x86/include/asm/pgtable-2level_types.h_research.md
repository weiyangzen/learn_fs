# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable-2level_types.h

Purpose: defines the fundamental value types and geometry for traditional 32-bit two-level x86 paging.

Important APIs, types, and functions: typedefs `pteval_t`, `pmdval_t`, `pudval_t`, `p4dval_t`, `pgdval_t`, and `pgprotval_t` as `unsigned long`, and defines `pte_t` as a union exposing `pte` and `pte_low`. Geometry constants include `ARCH_PAGE_TABLE_SYNC_MASK`, `PGDIR_SHIFT`, `PTRS_PER_PGD`, `PTRS_PER_PMD`, `PTRS_PER_PTE`, and `PGD_KERNEL_START`.

Control flow: no executable code. Configuration is fixed for non-PAE i386: page directory entries cover 4 MiB (`PGDIR_SHIFT` 22), PMD is folded, and PTE pages contain 1024 entries.

State and persistence: no state is owned.

Dependencies and integration points: used by `pgtable_32_types.h`, `pgtable_types.h`, and generic folded-level page-table code. `PGD_KERNEL_START` derives the kernel/user split from `CONFIG_PAGE_OFFSET`.

Risks: value type widths are part of the page-table ABI for the architecture. Changing geometry breaks low-level MM, swap encoding, boot page tables, and kernel/user split calculations.

Test signals: non-PAE i386 builds, page-table walking, `CONFIG_PAGE_OFFSET` variants, boot-time initial page-table reservation sizing, and generic MM compile-time assertions.
