# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_cfg_data.c

## Purpose
This file is the static SoC configuration database for MDP3. It maps public component IDs to SCP inner IDs, component types, aliases, MM subsystem IDs, clock/resource metadata, blend/auxiliary components, supported V4L2 formats, image limits, pipe/mutex routing, probe infrastructure, and per-platform feature flags for MT8183, MT8188, and MT8195-family data.

## Important APIs, Types, and Functions
It defines internal component-ID enums, `mdp_platform_config` instances, mutex-index tables, `mdp_comp_data` arrays, subcomponent DT match tables, format arrays, default limits, pipe-info arrays, and exported driver-data objects `mt8183_mdp_driver_data`, `mt8188_mdp_driver_data`, and `mt8195_mdp_driver_data`. Lookup helpers are `mdp_cfg_get_id_inner()`, `mdp_cfg_get_id_public()`, and `mdp_cfg_comp_is_dummy()`.

## Control Flow
The core chooses one exported driver-data object from OF match data. Component discovery uses `comp_data` and alias counters to bind DT nodes to public IDs. CMDQ path building uses the pipe/mutex tables and platform flags. V4L2 mem2mem uses the format arrays and default limits for negotiation. SCP configuration uses the inner/public ID mapping.

## State and Persistence
Most data is immutable static const configuration. The lookup helpers read current `mdp_dev->mdp_data`. There is no runtime persistence beyond the selected pointer in the probed device.

## Dependencies and Integration Points
The file depends on `mtk-img-ipi.h`, `mtk-mdp3-core.h`, `mtk-mdp3-comp.h`, and register/type definitions. It integrates device-tree compatibles, MMSYS/mutex indices, SCP platform IDs, V4L2 fourccs, and component operation code.

## Risks and Edge Cases
The tables must remain internally consistent: public ID, inner ID, alias order, DT node order, mutex index, pipe info, and shared-memory layout all have to agree. `mdp_cfg_get_id_public()` treats `inner_id == 0` as invalid, so components with zero inner IDs are intentionally not returned by that path. `mdp_cfg_comp_is_dummy()` indexes `comp_data[id]` after lookup and assumes the lookup did not return `MDP_COMP_NONE` in a way that underflows. MT8188 reuses MT8195 platform config/format/limits, which must remain valid for both SoCs.

## Test Signals
Probe tests on each supported SoC, DT alias ordering tests, component discovery logs, V4L2 format enumeration, pipe/mutex routing for one- and two-postprocessor jobs, and SCP-generated config validation are key signals.
