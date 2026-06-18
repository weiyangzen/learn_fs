# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_ccorr.h

## Purpose
This header defines CCORR register offsets and masks for MDP3 color-correction relay/size programming.

## Important APIs, Types, and Functions
Macros cover enable, config, and size registers plus masks.

## Control Flow
The CCORR component ops enable relay mode and write tile size during subframe configuration.

## State and Persistence
The state is volatile CCORR MMIO state for each command queue job.

## Dependencies and Integration Points
Included by `mtk-mdp3-comp.c`, primarily for MT8183 CCORR support.

## Risks and Edge Cases
The size mask encodes two 13-bit dimensions; invalid tile widths/heights from SCP would be truncated by masked writes.

## Test Signals
MT8183 CCORR relay paths and CMDQ register dumps are useful validation.
