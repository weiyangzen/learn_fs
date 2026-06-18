<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/64/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/64/pgtable.h

## Purpose
This header defines the 64-bit nohash Book3E page-table layout, kernel virtual address regions, PMD/PUD/P4D accessors, hugepage helpers, swap encoding, vmemmap mapping hooks, and exception patching hook.

## Important APIs, Types, And Functions
Key definitions include `PGTABLE_EADDR_SIZE`, `PGTABLE_RANGE`, `KERN_VIRT_START`, `VMALLOC_*`, `KERN_IO_*`, `IOREMAP_*`, `VMEMMAP_*`, `PTE_RPN_MASK`, `pmd_set()/clear()`, `pud_set()/clear()`, `pmd_page_vaddr()`, `pmd_page()`, `pud_pgtable()`, `pud_page()`, `pud_write()`, `p4d_set()`, `huge_ptep_set_wrprotect()`, swap conversion macros, `vmemmap_create_mapping()`, `vmemmap_remove_mapping()`, and `patch_exception()`.

## Control Flow
Generic MM uses the inline accessors for page-table walks and modifications. Hugepage write-protect calls `pte_update()` with the huge flag. Memory hotplug invokes vmemmap map/remove hooks. Exception setup can patch handler addresses through `patch_exception()`.

## State And Persistence Behavior
Persistent state lives in page tables, swap PTE encodings, vmemmap mappings, and patched exception vectors. The kernel virtual space is partitioned into vmalloc, vmemmap, IO, ioremap, and fixmap regions.

## Dependencies And Integration Points
It depends on 4K nohash geometry, barriers, `asm-const`, e500 PTE bits, and generic nohash pgtable code. It integrates with Book3E MMU setup, hugeTLB, sparse vmemmap, IO mapping, and low-level exception code.

## Risks And Edge Cases
Address-region constants are ABI-like for the architecture. `pmd_bad()`/`pud_bad()` require kernel virtual child table addresses. Swap encoding borrows bit 7 for exclusivity. Exception patching must target valid text symbols.

## Test Signals
Run 64-bit Book3E page-table debug, swap, hugepage mprotect/COW, vmalloc/ioremap/fixmap tests, sparsemem hotplug validation, and boot-time exception path tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/64/pgtable.h -->
