<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/device.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/device.h

## Purpose
This header defines SPARC architecture extensions for `struct device`.

## Important APIs, Types, and Functions
It supplies architecture-specific DMA/IOMMU or platform metadata fields embedded in device structures.

## Control Flow
Device discovery and bus setup initialize the archdata; DMA and IOMMU paths later consume it.

## State and Persistence Behavior
Per-device archdata persists for the lifetime of the device.

## Dependencies and Integration Points
It integrates with OF platform devices, PCI/SBUS, DMA mapping, and IOMMU code.

## Risks
Missing or stale archdata can route DMA through the wrong translation path.

## Test Signals
Enumerate OF/PCI/SBUS devices and run DMA-capable driver tests under IOMMU and direct mapping modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/device.h -->
