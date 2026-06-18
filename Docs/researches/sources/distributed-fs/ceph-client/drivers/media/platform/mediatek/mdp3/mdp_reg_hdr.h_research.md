# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_hdr.h

## Purpose
This header defines MDP3 HDR block register offsets and masks for top/relay control, size windows, histogram controls, histogram address, and tile position.

## Important APIs, Types, and Functions
Macros include `MDP_HDR_TOP`, `MDP_HDR_RELAY`, `MDP_HDR_SIZE_0..2`, histogram controls/address, and tile position masks.

## Control Flow
HDR component ops enable the block, set relay/top frame bits, then program per-subframe tile size, clipping offsets, histogram controls, and histogram enable/address.

## State and Persistence
HDR register state is volatile and programmed through CMDQ for each job/subframe.

## Dependencies and Integration Points
Used by `mtk-mdp3-comp.c` and SCP shared-memory structs for MT8195 HDR paths.

## Risks and Edge Cases
Histogram fields are sensitive to buffer/address setup not visible in this header. Mask drift can corrupt reserved HDR controls.

## Test Signals
HDR-enabled pipelines, histogram buffer validation, and register traces are high-value tests.
