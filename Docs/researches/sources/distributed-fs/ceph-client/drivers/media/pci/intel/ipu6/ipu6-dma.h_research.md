# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-dma.h

## Purpose
This header declares IPU6 DMA/MMU mapping APIs and the `ipu6_dma_mapping` container used by the IPU6 MMU direct-map layer.

## Important APIs, types, and functions
`struct ipu6_dma_mapping` contains an `ipu6_mmu_info` pointer and an `iova_domain`. Public APIs cover cache sync for single allocations and scatterlists, DMA allocation/free, userspace mmap, SG map/unmap, and SG-table map/unmap.

## Control flow and integration points
The DMA helpers are consumed by firmware package creation, buttress firmware mapping, fw-com shared queue allocation, and ISYS video queue paths. They are part of the exported `INTEL_IPU6` namespace and rely on each `ipu6_bus_device` carrying a valid MMU pointer.

## State, persistence, and dependencies
The header has no runtime state but defines the IOVA domain holder used by `ipu6-mmu.c` and `ipu6-dma.c`. It depends on Linux IOVA, scatterlist, types, and IPU6 bus definitions.

## Risks and test signals
Risks are API misuse with unmapped or non-synced buffers, incorrect direction/attrs assumptions, and missing MMU initialization. Test signals include modular builds, firmware shared-memory setup, video buffer mapping, mmap capture paths, and clean unmap/free under error injection.
