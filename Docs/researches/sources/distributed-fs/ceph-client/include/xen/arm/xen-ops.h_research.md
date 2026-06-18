<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/xen-ops.h -->
# sources/distributed-fs/ceph-client/include/xen/arm/xen-ops.h

## Purpose
This header wires ARM devices to Xen DMA operations when Xen SWIOTLB is required.

## Important APIs, Types, And Functions
- `xen_setup_dma_ops(struct device *dev)` assigns `dev->dma_ops = &xen_swiotlb_dma_ops` under `CONFIG_XEN` when `xen_swiotlb_detect()` is true.

## Control Flow
Device setup calls `xen_setup_dma_ops()`. In Xen builds, the helper detects the SWIOTLB condition and installs Xen-aware DMA operations; otherwise it does nothing.

## State And Persistence
It mutates per-device DMA ops state. No global state is declared.

## Dependencies And Integration Points
It depends on `<xen/swiotlb-xen.h>`, `<xen/xen-ops.h>`, `struct device`, and Xen SWIOTLB DMA ops. It integrates with platform/OF/PCI device initialization.

## Risks And Edge Cases
Calling this too late can leave devices with stale DMA ops. Assigning Xen DMA ops unnecessarily can reduce performance; failing to assign them can cause devices to DMA to addresses Xen cannot translate.

## Test Signals
Signals include per-device `dma_ops` set under Xen direct-mapped/legacy Dom0 conditions, unchanged ops outside Xen, and successful DMA mapping/unmapping under Xen.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/xen-ops.h -->
