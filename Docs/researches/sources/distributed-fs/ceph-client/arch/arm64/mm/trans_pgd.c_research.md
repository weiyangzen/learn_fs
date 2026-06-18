# sources/distributed-fs/ceph-client/arch/arm64/mm/trans_pgd.c

## Purpose
This file builds transitional page tables for hibernate restore and kexec. These tables are used when the normal kernel page tables may be overwritten during a world transition, so the code can keep executing and access required mappings safely.

## Important APIs, Types, and Functions
Main public APIs are `trans_pgd_create_copy()`, `trans_pgd_idmap_page()`, and `trans_pgd_copy_el2_vectors()`. Internal recursive copy helpers are `copy_page_tables()`, `copy_p4d()`, `copy_pud()`, `copy_pmd()`, and `copy_pte()`. Allocation is abstracted through `struct trans_pgd_info` and `trans_alloc()`.

## Control Flow
`trans_pgd_create_copy()` allocates a new top-level table, then calls `copy_page_tables()` for the requested virtual range. The copy walk follows the current kernel page tables from PGD down. Missing entries are skipped. Table entries allocate destination tables as needed. Leaf entries are copied after making them valid kernel mappings and writable with `pte_mkvalid_k()`/`pmd_mkvalid_k()`/`pud_mkvalid_k()` and `*_mkwrite_novma()` so the transitional context can access them.

`trans_pgd_idmap_page()` constructs a TTBR0 page table bottom-up for one physical page that may be outside the VA range normally handled by kernel populate helpers. It computes whether 48-bit or 52-bit physical coverage is needed, allocates levels from leaf upward, fills the index for the destination physical address, and returns `trans_ttbr0` plus the matching `TCR_T0SZ`.

`trans_pgd_copy_el2_vectors()` allocates a page, copies `trans_pgd_stub_vectors`, and cleans/invalidates caches to the point of unification and coherency before returning the physical vector address.

## State and Persistence
All page tables and copied vectors are allocated through the caller-provided allocator and persist only for the transition. The file does not own global state. Output state is returned through `dst_pgdp`, `trans_ttbr0`, `t0sz`, and `el2_vectors`.

## Dependencies and Integration Points
The file integrates with hibernate, kexec, ARM64 page-table primitives, cache maintenance, and the assembly vector table in `trans_pgd-asm.S`. It depends on `trans_pgd_info` callers to provide zeroed, suitably aligned pages and lifetime management.

## Risks
Copying invalid or overly permissive attributes could break the transition; this file intentionally forces valid writable kernel mappings for accessibility. Allocation failure must abort cleanly. The bottom-up idmap assumes a single-page mapping and maximum T0SZ calculation; errors there can make restart/restore code unreachable. Cache maintenance is required after copying EL2 vectors.

## Test Signals
Hibernate resume and kexec reboot are the main integration tests. Tests should cover high physical addresses requiring 52-bit handling, allocation failure injection, and EL2 vector copy paths. Failures show as transition hangs, faults after page-table switch, or failed soft restart/vector setup.
