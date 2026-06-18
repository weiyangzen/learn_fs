# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/aqua_vanjaram.c

## Purpose
This file contains Aqua Vanjaram ASIC support for doorbell layout, SOC instance configuration, XCP compute partition management, memory-partition compatibility, and structured register-state capture for PCIE, XGMI, WAFL, and USR debug data. It is the ASIC-specific implementation behind the generic XCP manager contract.

## Important APIs, types, and functions
`aqua_vanjaram_doorbell_index_init()` programs layout-1 doorbell ranges for KIQ, MEC, user queues, XCC, SDMA, IH, VCN, and non-CP ranges. The XCP function table `aqua_vanjaram_xcp_funcs` supplies `switch_partition_mode`, `query_partition_mode`, `get_ip_details`, `get_xcp_res_info`, and `get_xcp_mem_id`.

Partition helpers derive and validate mode. `__aqua_vanjaram_calc_xcp_mode()` derives SPX/DPX/TPX/QPX/CPX from XCC count and XCCs per XCP. `aqua_vanjaram_query_partition_mode()` compares derived mode against NBIO-reported compute partition mode on non-SR-IOV systems. `__aqua_vanjaram_get_xcc_per_xcp()` maps mode to XCCs per XCP. `__aqua_vanjaram_get_xcp_ip_info()` fills IP instance masks and function tables for GFXHUB, GFX, SDMA, and VCN. `__aqua_vanjaram_get_px_mode_info()`, `aqua_vanjaram_get_xcp_res_info()`, `__aqua_vanjaram_get_auto_mode()`, and `__aqua_vanjaram_is_valid_mode()` connect compute modes to memory partition compatibility and resource sharing.

`aqua_vanjaram_switch_partition_mode()` performs the KFD-aware switch sequence. `aqua_vanjaram_get_xcp_mem_id()` maps XCPs to memory partitions, using ACPI NUMA information on APP APUs. `aqua_vanjaram_init_soc_config()` derives AID, SDMA, VCN, and JPEG instance counts, initializes the XCP manager, and initializes IP mapping.

The register-state path is exposed through `aqua_vanjaram_get_reg_state()`, which dispatches to PCIE, XGMI, WAFL, USR, or USR_1 readers. Each reader validates the output buffer, fills a versioned common header, writes per-instance headers, and captures SMN/PCI config values into packed AMDGPU register-state structures.

## Control flow
SOC init computes SDMA/AID topology from masks, clears VCN/JPEG harvest config, counts media instances, initializes XCP manager, updates supported modes, and builds IP maps. A partition switch first handles AUTO mode or validates the requested mode against the current memory partition, optionally locks KFD, calls generic pre-switch hooks, asks GFX to switch XCC grouping, reinitializes XCPs, calls generic post-switch hooks, refreshes available modes, and unlocks KFD.

Register-state capture switches by requested state type. PCIE capture reads fixed SMN ranges and upstream bridge PCIe status/AER fields. XGMI and WAFL capture iterate active AIDs and two links per AID using SMN base offsets. USR capture iterates active AIDs and reads one of two register lists with different increments.

## State and persistence behavior
The file mutates `adev` doorbell fields, SDMA/VCN/JPEG counts, `aid_mask`, XCP manager state, XCP resource/memory ids, and register-state output buffers. It does not persist data outside driver memory, but partition choices affect scheduler/KFD-visible topology and memory affinity. Register-state output is caller-provided diagnostic data.

## Dependencies
It depends on AMDGPU core, SOC15 accessors, register-state definitions, generic XCP APIs, GFX v9.4.3, GFXHUB v1.2, SDMA v4.4.2, KFD lock APIs, ACPI memory information, NBIO compute partition callbacks, GMC partition callbacks, and PCI config helpers.

## Integration points
Generic XCP calls enter through `aqua_vanjaram_xcp_funcs`. KFD is coordinated during live partition switching. GFX, GFXHUB, and SDMA provide per-IP XCP state transitions. Debug and support tooling consume `aqua_vanjaram_get_reg_state()` outputs. SOC initialization wires this ASIC into broader IP discovery and mapping.

## Risks and edge cases
Mode validation depends on memory partition mode and XCC divisibility; incorrect masks can produce invalid resource sharing or divide-by-zero-like assumptions when resource counts are smaller than XCP count. SR-IOV disables partition switching by mutating the global function table pointer, which is risky if shared across devices with different virtualization state. `aqua_vanjaram_get_xcp_res_info()` computes `num_shared = num_xcp / max_res[i]` when a resource count is lower than XCP count; a zero media-resource count would be unsafe if the mode expects sharing. Register-state readers use fixed max instance counts and set `num_instances` to those maxima rather than the number actually iterated, so consumers must interpret inactive/missing slots carefully. PCI upstream bridge traversal assumes expected bridge topology.

## Test signals
Useful tests cover every supported compute mode against NPS1/NPS2/NPS4, AUTO mode on APU and dGPU layouts, KFD lock failure rollback, XCP IP mask/resource accounting, APP APU NUMA memory-id mapping, SR-IOV VF behavior, and buffer-size validation for each register-state type. Hardware validation should compare captured SMN/PCI registers against known-good service dumps.
