# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_aal.h

## Purpose
This header defines MDP3 AAL block register offsets and write masks for adaptive ambient/light processing or relay configuration.

## Important APIs, Types, and Functions
It exports macros for enable, configuration, input/output size, output offset, and main config registers plus their masks.

## Control Flow
`mtk-mdp3-comp.c` uses these macros in AAL init/frame/subframe operations to enable the block and apply SCP-provided tile geometry/configuration through CMDQ writes.

## State and Persistence
The macros describe volatile AAL MMIO state programmed per frame/subframe.

## Dependencies and Integration Points
The header is included only by component programming code and must match the MDP3 hardware register map.

## Risks and Edge Cases
Mask errors can overwrite reserved bits. Size/offset masks imply 13-bit dimensions and limited offset fields, so SCP-generated values must fit.

## Test Signals
CMDQ packet inspection and MT8195 AAL path tests with tile offsets/sizes validate this contract.
