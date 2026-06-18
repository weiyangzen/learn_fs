<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/64/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/64/pgalloc.h

## Purpose
This header provides 64-bit nohash page-table allocation and population helpers for P4D/PUD/PMD levels and declares vmemmap backing metadata.

## Important APIs, Types, And Functions
`struct vmemmap_backing` tracks physical and virtual backing chunks for the vmemmap. Helpers include `p4d_populate()`, `pud_alloc_one()`, `pud_free()`, `pud_populate()`, `pmd_populate_kernel()`, `pmd_populate()`, `pmd_alloc_one()`, `pmd_free()`, `__pmd_free_tlb()`, and `__pud_free_tlb()`.

## Control Flow
Generic MM allocates page-table pages from `PGT_CACHE()` slabs with `pgtable_gfp_flags()`, stores child table addresses with `*_set()`, and frees them either immediately or via TLB-gather callbacks.

## State And Persistence Behavior
Persistent state consists of allocated PUD/PMD pages and encoded parent entries. `vmemmap_list` records sparse vmemmap backing mappings that survive across memory hotplug operations until removed.

## Dependencies And Integration Points
It depends on slab, cpumask, percpu, `PGT_CACHE`, and nohash 64 pgtable setters. It integrates with vmemmap mapping creation/removal and generic page-table teardown.

## Risks And Edge Cases
The cache index must match table geometry or slab object sizes become wrong. Freeing through TLB gather must preserve the encoded shift. vmemmap backing needs hotplug-safe lifetime management.

## Test Signals
Run 64-bit Book3E/nohash builds with sparsemem/vmemmap, memory hotplug where available, mmap/unmap stress, and page-table allocation failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/64/pgalloc.h -->
