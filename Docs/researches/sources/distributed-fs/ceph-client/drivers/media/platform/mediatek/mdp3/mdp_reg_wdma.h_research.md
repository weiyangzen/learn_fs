# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_wdma.h

## Purpose
This header defines MDP3 WDMA register offsets and masks for destination DMA output without rotation.

## Important APIs, Types, and Functions
Macros cover enable/reset/config, source and clip geometry, destination pitches, alpha, buffer controls, plane offsets, flow-control debug, and destination base addresses.

## Control Flow
WDMA ops reset the block, program frame buffer addresses/pitches/config/alpha, program subframe offsets/source/clip/coordinate, enable WDMA, wait EOF, and disable it.

## State and Persistence
WDMA MMIO state is volatile per job/subframe.

## Dependencies and Integration Points
Used by `mtk-mdp3-comp.c`, primarily for MT8183 WDMA paths in the current implementation.

## Risks and Edge Cases
Address/offset mistakes can corrupt output buffers. Reset polling uses flow-control status. The current component code reads WDMA shared fields only under MT8183 checks, so MT8195 WDMA use would need review.

## Test Signals
WDMA output jobs, multi-plane offsets, alpha, reset/EOF events, and IOMMU fault monitoring.
