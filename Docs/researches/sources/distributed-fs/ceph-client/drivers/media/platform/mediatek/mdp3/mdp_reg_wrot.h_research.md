# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_wrot.h

## Purpose
This header defines MDP3 WROT register offsets and masks for rotated/scaled output DMA.

## Important APIs, Types, and Functions
Macros cover control, buffer size, soft reset/status, crop/target size, plane offsets/strides, dither, pre-ultra, input size, rotation enable, FIFO, matrix, 10-bit scan, pending-zero, and base addresses.

## Control Flow
WROT ops reset the block, program frame base addresses/strides/control/matrix/fifo/10-bit/pre-ultra settings, program subframe offsets/source/target/crop/main-buffer fields, enable rotation output, wait EOF, and disable it.

## State and Persistence
WROT register state is volatile but reset at job start.

## Dependencies and Integration Points
Used by `mtk-mdp3-comp.c`; values come from SCP shared-memory layouts and platform flags.

## Risks and Edge Cases
Soft reset polling, DMA address offsets, 10-bit fields, and filter constraints are sensitive hardware paths. Output rotation and stride must match V4L2 compose/crop state.

## Test Signals
0/90/180/270 rotation jobs, 10-bit output, multi-plane strides, filter-constraint variants, EOF event timing, and output buffer integrity.
