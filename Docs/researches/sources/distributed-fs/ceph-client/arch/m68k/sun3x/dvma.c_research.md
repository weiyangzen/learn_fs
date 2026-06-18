# sources/distributed-fs/ceph-client/arch/m68k/sun3x/dvma.c

## Purpose

implements Sun-3x DVMA allocation and IOMMU mapping for the 68030-based Sun-3x platform

## Important APIs, Types, and Functions

Source read size: 200 lines, 4670 bytes. Includes: `linux/kernel.h`, `linux/init.h`,
`linux/bitops.h`, `linux/mm.h`, `linux/memblock.h`, `linux/vmalloc.h`, `asm/sun3x.h`, `asm/dvma.h`,
`asm/io.h`, `asm/page.h`, `asm/tlbflush.h`. Defined functions: `dvma_print`, `dvma_map_cpu`,
`dvma_map_iommu`, `dvma_unmap_iommu`. Declared functions: `pr_info`, `pr_debug`, `flush_tlb_all`,
`dvma_entry_set`, `dvma_print`. Key macros/defines: `IOMMU_ADDR_MASK`, `IOMMU_CACHE_INHIBIT`,
`IOMMU_FULL_BLOCK`, `IOMMU_MODIFIED`, `IOMMU_USED`, `IOMMU_WRITE_PROTECT`, `IOMMU_DT_MASK`,
`IOMMU_DT_INVALID`, `IOMMU_DT_VALID`, `IOMMU_DT_BAD`, `dvma_entry_paddr(index)`,
`dvma_entry_vaddr(index,paddr)`, `dvma_entry_set(index,addr)`, `dvma_entry_clr(index)`,
`dvma_entry_hash(addr)`.

## Control Flow and Behavior

dvma_map_align(), dvma_unmap(), dvma_malloc_align(), dvma_free(), and initialization paths manage
DVMA address space and page-table/IOMMU entries

## State and Persistence

persistent state includes the DVMA allocator, IOMMU page tables, virtual mapping ranges, and driver-
visible bus addresses

## Dependencies and Integration Points

integrates with Sun-3x PROM/MMU setup, asm/dvma.h, SBus/VME-style drivers, and generic DMA mapping
assumptions

## Risks and Test Signals

alignment and IOMMU PTE bugs cause device data corruption; SCSI/network DMA, allocation/free churn,
and boot with multiple DVMA users are signals
