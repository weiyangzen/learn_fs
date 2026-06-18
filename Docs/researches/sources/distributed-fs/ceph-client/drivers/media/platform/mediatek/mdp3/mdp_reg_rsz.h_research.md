# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_rsz.h

## Purpose
This header defines MDP3 resizer register offsets and masks for enable/reset, control, input/output size, coefficient steps, luma/chroma offsets, and extra control.

## Important APIs, Types, and Functions
Macros include `PRZ_ENABLE`, `PRZ_CONTROL_1/2`, input/output image, horizontal/vertical coefficient steps, integer/subpixel luma and chroma offsets, and `RSZ_ETC_CONTROL`.

## Control Flow
RSZ component ops reset/enable the block, configure frame-level scaling controls and coefficients, program per-subframe source/output sizes and subpixel offsets, optionally coordinate merge blocks, and undo DCM workarounds.

## State and Persistence
RSZ register state is volatile per CMDQ job.

## Dependencies and Integration Points
Used by `mtk-mdp3-comp.c` and MMSYS RSZ merge routing on MT8195-like platforms.

## Risks and Edge Cases
Subpixel offsets and coefficient steps must match SCP scaler calculations. DCM/merge workarounds are platform-flag dependent. Small-sample and bypass paths need separate coverage.

## Test Signals
Scale-up/down, bypass, small-sample, RSZ2/RSZ3 merge, and subframe tiling tests validate this map.
