
# sources/distributed-fs/ceph-client/include/trace/events/swiotlb.h

## Purpose
Defines the `swiotlb_bounced` tracepoint for observing DMA mappings that require bounce buffering through the software I/O TLB.

## Important APIs, Types, and Functions
`swiotlb_bounced` takes a `struct device *`, device DMA address, and size. It records device name, DMA mask, device address, transfer size, and whether bouncing was forced by `is_swiotlb_force_bounce(dev)`.

## Control Flow
DMA/SWIOTLB mapping code emits the event when a mapping bounces. The tracepoint snapshots device metadata and bounce cause before returning to DMA mapping flow.

## State and Persistence
The header owns no DMA state. Trace records persist copied device name, DMA mask, address, size, and force/normal mode. They do not retain bounce-buffer contents.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h`, device DMA fields, and SWIOTLB helpers. Integrates with DMA mapping code, IOMMU/SWIOTLB diagnostics, confidential-computing forced-bounce modes, and device-driver performance analysis.

## Risks
Tracing only bounced mappings can hide successful direct mappings, so rates must be interpreted in context. DMA addresses and device names can be sensitive diagnostics. Call sites must pass valid devices with stable names.

## Test Signals
Signals include forced SWIOTLB boot modes, devices with restricted DMA masks, large DMA mappings, confidential VM bounce behavior, and trace correlation with DMA mapping failures or performance drops.
