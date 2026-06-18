# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_tdshp.h

## Purpose
This header defines TDSHP sharpness/histogram register offsets and masks for MDP3 display-quality processing.

## Important APIs, Types, and Functions
Macros cover histogram config, control/config, input/output size/offset, luma histogram initialization, constrain result initialization, and contour histogram initialization.

## Control Flow
TDSHP ops enable the block/FIFO, reset histogram memories, apply frame config, and write per-subframe input/output and histogram configuration.

## State and Persistence
Histogram and TDSHP configuration state is volatile but may retain values across jobs unless reset by init operations.

## Dependencies and Integration Points
Used by `mtk-mdp3-comp.c`, with histogram counts and constraints controlled by platform flags from `mdp_cfg_data.c`.

## Risks and Edge Cases
Histogram reset loops depend on `tdshp_hist_num`; off-by-one errors can leave stale histogram state. Mask drift can affect image quality or processing hangs.

## Test Signals
TDSHP-enabled pipelines, histogram reset traces, contour/constrain platform variants, and output comparison tests.
