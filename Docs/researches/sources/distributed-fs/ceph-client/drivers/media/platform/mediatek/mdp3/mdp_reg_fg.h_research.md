# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_fg.h

## Purpose
This header defines MDP3 FG block register offsets and masks for trigger, control, clock-enable, and tile information programming.

## Important APIs, Types, and Functions
Macros cover `MDP_FG_TRIGGER`, `MDP_FG_FG_CTRL_0`, `MDP_FG_FG_CK_EN`, and two tile-info registers.

## Control Flow
FG component ops pulse reset/trigger, configure frame control/clock bits, then write tile info per subframe.

## State and Persistence
The state is volatile FG MMIO state per command queue job.

## Dependencies and Integration Points
Included by `mtk-mdp3-comp.c` for MT8195/MT8188 foreground blocks.

## Risks and Edge Cases
Trigger/control mask mistakes can leave the block disabled or clock-gated. Tile-info fields are full-width and rely entirely on SCP correctness.

## Test Signals
FG-enabled pipeline CMDQ dumps and output comparison against relay/bypass expectations.
