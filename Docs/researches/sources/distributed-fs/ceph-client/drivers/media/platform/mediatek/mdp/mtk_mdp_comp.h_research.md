# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_comp.h

## Purpose
This header defines the legacy MDP component model and clock/resource helper prototypes.

## Important APIs, Types, and Functions
`enum mtk_mdp_comp_type` names RDMA, RSZ, WDMA, and WROT. `struct mtk_mdp_comp` stores a list node, OF node, two possible clocks, and type. The declared helpers initialize/deinitialize components and toggle component clocks.

## Control Flow
The core driver includes this header to build a component list during probe and to control clocks during PM transitions.

## State and Persistence
The header defines per-component in-memory state that persists for the driver binding lifetime.

## Dependencies and Integration Points
It is consumed by `mtk_mdp_core.c` and `mtk_mdp_comp.c`, and indirectly by the context/device definitions in `mtk_mdp_core.h`.

## Risks and Edge Cases
The fixed `clk[2]` array assumes no component needs more clocks. Adding new component types requires updating DT matching and any clock special cases.

## Test Signals
Compile coverage and runtime probe on DT nodes for every enum type validate the header contract.
