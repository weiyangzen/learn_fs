<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcf_pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcf_pgalloc.h

## Purpose
`mcf_pgalloc.h` implements ColdFire page-table allocation helpers for the m68k MMU memory-management code.

## Important APIs, Types, and Functions
It defines `pte_free_kernel()`, `pte_alloc_one_kernel()`, `pmd_alloc_kernel()`, `pmd_populate()`, `pmd_populate_kernel`, `__pte_free_tlb()`, `pte_alloc_one()`, `pte_free()`, `pmd_free()`, `pgd_free()`, and `pgd_alloc()`. It uses `ptdesc` helpers and copies `swapper_pg_dir` into new PGDs.

## Control Flow, State, and Persistence
Allocation functions request DMA-capable zeroed page-table memory, run page-table constructors, and free on constructor failure. `pgd_alloc()` initializes a new PGD from the kernel swapper directory and clears user entries below `PAGE_OFFSET`.

## Dependencies and Integration Points
It depends on TLB headers, page-table descriptor helpers, `swapper_pg_dir`, and m68k page-table constants. The MM subsystem calls these functions during address-space creation, teardown, and TLB gather.

## Risks
Page tables are allocated with `GFP_DMA`, constraining memory sources. `pmd_free()` is `BUG()` because PMDs are embedded in PGDs; any generic MM path that tries to free one is fatal. Constructor/destructor pairing must stay exact.

## Test Signals
Signals include process creation/exit under memory pressure, mmap/munmap churn, fork/exec, TLB teardown, page-table leak checks, and validation that no generic path calls `pmd_free()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcf_pgalloc.h -->
