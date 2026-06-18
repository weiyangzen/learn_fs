<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/dma-mapping.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/dma-mapping.h

## Purpose
This header connects SPARC to the generic DMA mapping API.

## Important APIs, Types, and Functions
It declares/defines architecture DMA mapping hooks and includes generic DMA helpers as needed.

## Control Flow
Drivers call generic DMA APIs, which dispatch through SPARC DMA ops selected for the device/platform.

## State and Persistence Behavior
Header state is none; DMA mappings persist in IOMMU/direct mapping state managed elsewhere.

## Dependencies and Integration Points
It integrates drivers with SPARC IOMMU, PCI/SBUS, and DMA coherent allocation.

## Risks
Incorrect DMA ops selection causes data corruption or bus faults.

## Test Signals
Run DMA API debug, network/storage driver I/O, and IOMMU mapping/unmapping stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/dma-mapping.h -->
