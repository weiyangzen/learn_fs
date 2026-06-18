# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_color.h

## Purpose
This header defines MDP3 COLOR block offsets and masks for start, interrupt, output selection, internal image size, and color-matrix enable registers.

## Important APIs, Types, and Functions
Macros include window positions, `MDP_COLOR_START`, interrupt enable, output select, internal width/height, and CM enable masks.

## Control Flow
Component init resets matrix state, enables interrupts and output selection; frame/subframe ops program start and internal tile dimensions.

## State and Persistence
Volatile COLOR block register state is configured per CMDQ job.

## Dependencies and Integration Points
Used by `mtk-mdp3-comp.c` for MT8195 COLOR components in SCP-generated paths.

## Risks and Edge Cases
Incorrect start/out-select bits can stall downstream components. Width/height masks must match tile geometry range.

## Test Signals
Color relay/path jobs, interrupt/event completion, and register trace validation.
