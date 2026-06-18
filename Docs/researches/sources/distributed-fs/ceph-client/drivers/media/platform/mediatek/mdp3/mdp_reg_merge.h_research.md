# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_merge.h

## Purpose
This header defines MDP3 MERGE block offsets and masks used when RSZ2/RSZ3 paths require merge assistance on MT8195-like platforms.

## Important APIs, Types, and Functions
Macros include enable and several config registers: `MDP_MERGE_CFG_0`, `_4`, `_12`, `_24`, and `_25`, all with full-width masks.

## Control Flow
RSZ subframe configuration writes merge config registers, enables bypass mode, and turns on MERGE when the selected RSZ path has a companion merge block.

## State and Persistence
MERGE MMIO state is volatile and per path/subframe.

## Dependencies and Integration Points
Used by RSZ operations in `mtk-mdp3-comp.c` together with MMSYS RSZ merge routing.

## Risks and Edge Cases
Full-width writes make SCP-provided values and register-map accuracy critical. Missing companion merge components break RSZ2/RSZ3 setup.

## Test Signals
Dual-pipe or RSZ2/RSZ3 jobs, MMSYS merge routing traces, and CMDQ register dumps validate behavior.
