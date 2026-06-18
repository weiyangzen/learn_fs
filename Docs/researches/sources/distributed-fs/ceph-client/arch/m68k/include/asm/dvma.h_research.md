<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/dvma.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/dvma.h

## Purpose
This header declares and describes DVMA/IOMMU support for Sun3 and Sun3x m68k systems, including allocation, mapping, unmapping, VME address conversion, and Sun3x onboard DMA register definitions.

## Important APIs, Types, And Functions
- Page constants define 8 KiB DVMA page size/alignment.
- Core APIs include `dvma_init()`, `dvma_map_iommu()`, `dvma_map_align()`, `dvma_malloc_align()`, `dvma_unmap()`, and `dvma_free()`.
- Convenience macros include `dvma_malloc()`, `dvma_map()`, `dvma_map_vme()`, and VME conversion helpers.
- Sun3 defines DVMA pmeg range, `DVMA_START/END/SIZE`, IOMMU entries, and virtual/physical/VME conversion macros.
- Sun3x defines larger IOMMU entry counts, `dvma_map_cpu()`, `dvma_unmap_iommu()`, `struct sparc_dma_registers`, `enum dvma_rev`, and `struct Linux_SBus_DMA`.
- Numerous `DMA_*` condition register bits describe DMA engine status, reset, direction, FIFO, burst, interrupt, and error controls.

## Control Flow
Initialization prepares DVMA mapping resources. Drivers allocate or map kernel buffers into DVMA bus space, program DMA engines with returned bus addresses, and unmap/free after completion. Sun3x SBus DMA code uses revision and condition-register bits to control transfers.

## State And Persistence Behavior
Persistent state is in the DVMA allocator/IOMMU tables, CPU mappings, DMA engine registers, and `dma_chain`. Mappings remain valid until explicitly unmapped/freed.

## Dependencies And Integration Points
It integrates with Sun3/Sun3x SCSI, Ethernet, VME, SBus-style DMA, MMU/IOMMU setup, and platform memory management.

## Risks And Edge Cases
DVMA alignment and address windows are strict, especially Sun3's empirical 0x10000 region alignment. Leaked mappings exhaust IOMMU entries. Revision-specific DMA bits overlap and must be interpreted by hardware revision.

## Test Signals
Sun3/Sun3x boot, DVMA allocation/free stress, SCSI and Ethernet DMA transfers, VME address conversions, IOMMU map/unmap validation, and DMA error/interrupt handling validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/dvma.h -->
