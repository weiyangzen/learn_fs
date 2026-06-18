<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pgtable.h

## Purpose
This header defines the 32-bit nohash page-table geometry, virtual-memory layout, selected processor-specific PTE bit header, PMD accessors, and swap PTE encoding.

## Important APIs, Types, And Functions
It defines PTE/PMD/PUD/PGD index sizes, table sizes, `PGDIR_SHIFT`, `PTRS_PER_*`, `USER_PTRS_PER_PGD`, `FIXADDR_TOP`, `IOREMAP_*`, and `VMALLOC_*`. It selects `pte-44x.h`, `pte-e500.h`, or `pte-8xx.h`, sets `PTE_RPN_SHIFT`, `PTE_RPN_MASK`, and `MAX_POSSIBLE_PHYSMEM_BITS`, and provides `pmd_none()`, `pmd_bad()`, `pmd_present()`, `pmd_clear()`, `pmd_pfn()`, `pmd_page()`, and swap conversion macros.

## Control Flow
There is little runtime control flow beyond inline accessors. Page fault, mmap, swap, and ioremap code consume the geometry and accessors while walking or modifying page tables.

## State And Persistence Behavior
The file owns no mutable state. It defines how state is stored in page-table entries, including whether PMDs carry physical addresses or BookE kernel virtual addresses and how swap type/offset/exclusive bits are encoded.

## Dependencies And Integration Points
It depends on `asm-generic/pgtable-nopmd.h`, scheduler/thread constants, `asm/mmu.h`, highmem/KASAN options, and the selected nohash PTE format. It integrates with generic MM, swap, fixmap, vmalloc, and ioremap code.

## Risks And Edge Cases
The VM layout is constrained by highmem, KASAN, early ioremap growth, and `ioremap_bot`. PTEs may be 64-bit on 32-bit systems with extended physical addressing. BookE PMD virtual-address encoding is a common portability trap.

## Test Signals
Build 44x, 85xx, and 8xx variants, enable swap, highmem, KASAN where supported, run page-table debug checks, and exercise vmalloc/ioremap overlap boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pgtable.h -->
