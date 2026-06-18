<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/fixmap.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/fixmap.h

## Purpose
Defines Xtensa fixed virtual mapping slots for highmem temporary mappings.

## Important APIs, Types, And Functions
Under `CONFIG_HIGHMEM`, defines `enum fixed_addresses` with `FIX_KMAP_BEGIN` and `FIX_KMAP_END`, plus `FIXADDR_END`, `FIXADDR_SIZE`, `FIXADDR_START`, and `FIXADDR_TOP`.

## Control Flow
No runtime flow. The preprocessor sizes fixed mapping space using `KM_MAX_IDX`, `NR_CPUS`, and `DCACHE_N_COLORS`, then includes generic fixmap support.

## State And Persistence
Controls virtual address layout for kmap local/atomic mappings. Runtime PTE state is managed elsewhere.

## Dependencies And Integration Points
Depends on highmem, page tables, cache coloring, and generic fixmap APIs.

## Risks And Edge Cases
Address layout must be PMD-aligned to handle cache aliasing. Incorrect slot count breaks highmem mappings on SMP or colored-cache systems.

## Test Signals
Build and boot highmem configurations, stress kmap local/atomic users, and run highmem filesystem/page-cache workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/fixmap.h -->
