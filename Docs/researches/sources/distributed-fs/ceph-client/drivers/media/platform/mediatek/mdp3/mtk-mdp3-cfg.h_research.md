# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-cfg.h

## Purpose
This header exposes MDP3 SoC driver-data objects and component-ID lookup helpers.

## Important APIs, Types, and Functions
It declares `mt8183_mdp_driver_data`, `mt8188_mdp_driver_data`, and `mt8195_mdp_driver_data`, forward-declares `struct mdp_dev` and `enum mtk_mdp_comp_id`, and declares inner/public/dummy lookup helpers.

## Control Flow
The core selects one driver-data object at probe. Component and CMDQ code call lookup helpers to translate SCP inner IDs to kernel public IDs and to skip dummy path-only components.

## State and Persistence
The header itself is stateless. The declared driver data are immutable static data in `mdp_cfg_data.c`.

## Dependencies and Integration Points
It is included by core, CMDQ, component, and config data files.

## Risks and Edge Cases
Lookup helpers depend on a valid `mdp_dev->mdp_data`; callers must avoid using them before probe data is installed.

## Test Signals
Compile/link coverage and SoC-specific component discovery tests validate the declarations.
