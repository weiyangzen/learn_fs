# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_pad.h

## Purpose
This header defines MDP3 padding block offsets and masks for padding control and picture/width/height size registers.

## Important APIs, Types, and Functions
Macros cover `MDP_PAD_CON`, `MDP_PAD_PIC_SIZE`, `MDP_PAD_W_SIZE`, and `MDP_PAD_H_SIZE`.

## Control Flow
PAD component ops initialize the block, clear width/height sizes, and program picture size per subframe.

## State and Persistence
State is volatile PAD block MMIO state.

## Dependencies and Integration Points
Used by `mtk-mdp3-comp.c` for MT8195/MT8188 pad components.

## Risks and Edge Cases
Padding geometry comes from SCP and is written directly; invalid dimensions can affect downstream components.

## Test Signals
PAD-enabled path register dumps and output dimension tests validate use.
