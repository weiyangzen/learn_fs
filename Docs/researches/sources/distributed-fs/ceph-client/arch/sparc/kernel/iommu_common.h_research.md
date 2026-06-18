# sources/distributed-fs/ceph-client/arch/sparc/kernel/iommu_common.h

## Purpose
`iommu_common.h` defines shared constants and helpers for UltraSPARC SBUS/PCI IOMMU code.

## Important APIs, Types, and Functions
It defines `IO_PAGE_SHIFT`, `IO_PAGE_SIZE`, `IO_PAGE_MASK`, `IO_PAGE_ALIGN()`, `IO_TSB_ENTRIES`, `IO_TSB_SIZE`, `IOMMU_PAGE_SHIFT`, `SG_ENT_PHYS_ADDRESS()`, and helper `is_span_boundary()`.

## Control Flow and State
The only executable logic is `is_span_boundary()`, which computes a physical address from the output SG entry, computes the number of IO pages covering the merged output length plus candidate SG length, and delegates to `iommu_is_span_boundary()`.

## Persistence and Dependencies
There is no persistent state. The header depends on Linux SG/device/IOMMU helper definitions and `<asm/iommu.h>`.

## Integration Points, Risks, and Test Signals
The constants define the IOMMU page geometry used by `iommu.c` and `iommu-common.c`. Risks include mismatch with hardware IOTLB page size or incorrect SG virtual-to-physical assumptions for non-linear scatterlists. Test signals are SG DMA mappings that respect segment boundaries, correct table sizing, and no off-by-one mapping around 8 KiB IO page boundaries.
