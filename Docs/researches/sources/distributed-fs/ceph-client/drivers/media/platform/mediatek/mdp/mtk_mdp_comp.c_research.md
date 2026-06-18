# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_comp.c

## Purpose
This file manages legacy MDP component discovery resources, specifically device-tree node references and clocks for RDMA, RSZ, WDMA, and WROT blocks.

## Important APIs, Types, and Functions
`mtk_mdp_comp_init()` records the component OF node, type, and clocks. `mtk_mdp_comp_deinit()` drops the node reference. `mtk_mdp_comp_clock_on()` and `mtk_mdp_comp_clock_off()` enable/disable all stored clocks, with RDMA allowed two clocks and other components stopping after the first clock.

## Control Flow
The core driver allocates a `struct mtk_mdp_comp` for each matched sibling/child node, calls init, links it into `mdp->comp_list`, then runtime PM suspend/resume or driver-wide clock helpers iterate the list to toggle clocks.

## State and Persistence
Component state is in `struct mtk_mdp_comp`: list node, retained OF node, up to two clock pointers, and component type. The state lasts for the platform device lifetime.

## Dependencies and Integration Points
The file depends on common clock APIs and OF node lookup. It is used by `mtk_mdp_core.c` for probe/remove and runtime PM.

## Risks and Edge Cases
Clock acquisition treats any missing clock as fatal, but only RDMA is expected to have two clocks. If device-tree clock ordering changes, RDMA secondary-clock behavior can break. Clock enable failures are logged but `mtk_mdp_comp_clock_on()` continues enabling remaining clocks and does not unwind already enabled clocks.

## Test Signals
Probe with old and new MT8173 device-tree layouts, missing clocks, disabled components, runtime suspend/resume, and repeated open/close cycles while checking balanced clock prepare counts.
