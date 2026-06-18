# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_rdma.h

## Purpose
This header defines the MDP3 RDMA register map and masks for source DMA, cropping, transform, UFO/10-bit data, SMI/pre-ultra thresholds, and event/status handling.

## Important APIs, Types, and Functions
Macros cover enable/reset/control, GMCIF, source format/control, background/source/clip sizes, offsets, transform, DMA buffer thresholds, monitor status, base/end addresses, and UFO decode length bases.

## Control Flow
RDMA component ops reset the block, configure source format/address/pitch/transform/ESL thresholds at frame scope, configure offsets/source/clip per subframe, enable RDMA, wait for EOF, and disable it.

## State and Persistence
RDMA register state is volatile and reprogrammed through CMDQ per job.

## Dependencies and Integration Points
Used heavily by `mtk-mdp3-comp.c`; field values come from SCP shared-memory config generated for MT8183/MT8195 layouts.

## Risks and Edge Cases
RDMA touches DMA addresses and memory pressure thresholds, so mask or address mistakes can cause memory faults or underruns. 10-bit/UFO paths require matching color-format flags and extra address registers. Reset polling relies on hardware status bit semantics.

## Test Signals
RDMA reset/EOF events, IOMMU fault absence, 10-bit/UFO formats, multi-plane formats, tiled subframes, and ESL threshold register traces are important signals.
