# subset-b-001325 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_xcp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_xcp.h

## Purpose
This header defines the AMDGPU XCP, or accelerator partition, contract used to expose and manage compute partitions inside one physical GPU. It models partition modes, per-partition IP instance ownership, resource counts, per-XCP DRM-facing state, and the function-table interface that ASIC-specific code such as Aqua Vanjaram implements.

## Important APIs, types, and functions
`MAX_XCP` caps manager-owned partitions at eight. `AMDGPU_XCP_MODE_NONE`, `AMDGPU_XCP_MODE_TRANS`, `AMDGPU_XCP_FL_LOCKED`, `AMDGPU_XCP_NO_PARTITION`, and `AMDGPU_XCP_OPS_KFD` define sentinel and operation flags used by partition switching paths. `XCP_INST_MASK()` maps an instance count and partition id to a contiguous bitmask.

`enum AMDGPU_XCP_IP_BLOCK` names partitionable IP classes: GFXHUB, GFX, SDMA, and VCN. `enum AMDGPU_XCP_STATE` names suspend/resume phases. `enum amdgpu_xcp_res_id` names user-visible resources: XCC, DMA, decode, and JPEG.

`struct amdgpu_xcp_ip_funcs` provides per-IP prepare/suspend/resume hooks over an instance mask. `struct amdgpu_xcp_ip` binds those hooks to one IP block and mask. `struct amdgpu_xcp` stores partition identity, memory id, validity, refcount, DRM device aliases, scheduler arrays, sysfs object, and a unique id. `struct amdgpu_xcp_mgr` stores the owning `amdgpu_device`, lock, function table, XCP array, active mode, supported/available mode bitmaps, resource configuration, and memory allocation mode. `struct amdgpu_xcp_mgr_funcs` is the ASIC extension point for querying and switching partition modes, deriving IP details, mapping memory ids, and optional state transitions.

The exported functions cover manager initialization, XCP initialization, partition query/switch/restore, partition lookup by IP instance, scheduler selection/release, XCP DRM-device registration/open/unplug, KFD-aware pre/post partition switching, supported mode refresh, and sysfs init/fini. `amdgpu_xcp_get_num_xcp()`, `amdgpu_get_next_xcp()`, and `for_each_xcp` are inline iteration helpers.

## Control flow
The header itself has no executable flow beyond helper iteration. Its API implies a standard flow: initialize the manager with ASIC callbacks, query or derive the current mode, initialize `xcp[]` entries, ask ASIC callbacks for each partition's IP masks and resources, then let scheduler/open paths pick per-XCP scheduling state. Mode switches flow through `amdgpu_xcp_pre_partition_switch()`, ASIC `switch_partition_mode`, `amdgpu_xcp_init()`, and `amdgpu_xcp_post_partition_switch()`.

## State and persistence behavior
XCP state is in-memory kernel state attached to `amdgpu_device`. It persists for the lifetime of the device driver instance and is exposed through DRM devices, scheduler lists, and sysfs kobjects. The manager lock serializes mutation. Refcounts and kobjects are important lifetime boundaries for partition device users.

## Dependencies
The header depends on Linux PCI and xarray types, DRM device/scheduler concepts, `amdgpu_ctx.h`, and many declarations from broader AMDGPU headers. ASIC-specific implementers provide `amdgpu_xcp_mgr_funcs`; GFXHUB/GFX/SDMA implementations provide `amdgpu_xcp_ip_funcs`.

## Integration points
Aqua Vanjaram is a direct consumer and implementer of this contract. KFD integration is signaled through `AMDGPU_XCP_OPS_KFD`, scheduler arrays, and partition scheduler update APIs. DRM file open paths use `amdgpu_xcp_open_device()`, and sysfs uses per-XCP kobjects and resource config kobjects.

## Risks and edge cases
The bitmask math assumes contiguous allocation and sane `num_inst`; invalid mode-to-instance ratios can expose empty masks or overlapping partitions. `amdgpu_xcp_get_num_xcp(NULL)` returns one, preserving non-partitioned behavior but requiring callers to understand the fallback. Lifetime bugs around DRM aliases, kobjects, and refcounts would be high impact because XCPs are user-visible devices. Mode switches must coordinate with KFD and schedulers or active queues can point at stale partition topology.

## Test signals
Useful validation comes from ASIC partition-mode switching tests, KFD queue creation across modes, sysfs resource/mode enumeration, suspend/resume across XCPs, and scheduler selection for each hardware IP. Static checks should cover max XCP count, mask overlap, and resource accounting for all supported modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_xcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_xgmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_xgmi.c

## Purpose
This file implements AMDGPU XGMI hive management, topology publication, link status reporting, XGMI/WAFL RAS handling, reset-on-init coordination, and a few bandwidth/address helpers. XGMI joins multiple GPUs into one high-speed peer fabric and shared addressing model, so this code acts as both an inter-device registry and the bridge to PSP topology firmware, sysfs, reset domains, and RAS.

## Important APIs, types, and functions
Global state consists of `xgmi_mutex` and `xgmi_hive_list`. `amdgpu_get_xgmi_hive()` finds or creates a hive kobject for `adev->gmc.xgmi.hive_id`, initializes `hive_lock`, task barrier, reset domain, pstate fields, and NPS request state, and returns a kobject reference. `amdgpu_put_xgmi_hive()` releases that reference.

Topology APIs include `amdgpu_xgmi_add_device()`, `amdgpu_xgmi_remove_device()`, `amdgpu_xgmi_update_topology()`, `amdgpu_xgmi_get_hops_count()`, `amdgpu_xgmi_get_bandwidth()`, `amdgpu_xgmi_get_is_sharing_enabled()`, `amdgpu_xgmi_get_ext_link()`, and `amdgpu_get_xgmi_link_status()`. Sysfs helpers expose hive id, device id, physical id, error count, hops, link count, and optional port mapping.

RAS support is split between legacy PCS register scans and ACA/MCA paths for XGMI v6.4.x. `amdgpu_xgmi_ras_sw_init()` registers the `xgmi_wafl` RAS block, `amdgpu_xgmi_ras_late_init()` resets counters and binds ACA on supported IPs, `amdgpu_xgmi_query_ras_error_count()` routes to MCA or legacy queries, `amdgpu_xgmi_reset_ras_error_count()` clears counters, and `amdgpu_ras_error_inject_xgmi()` triggers PSP RAS injection after disallowing DF cstate and XGMI power-down.

Reset and partition helpers include `amdgpu_xgmi_reset_on_init()`, its scheduled work item, and `amdgpu_xgmi_request_nps_change()`. `amdgpu_xgmi_same_hive()`, `amdgpu_xgmi_get_relative_phy_addr()`, `amdgpu_xgmi_early_init()`, and `amgpu_xgmi_set_max_speed_width()` provide smaller utility surfaces.

## Control flow
Adding a device first initializes PSP XGMI if PSP is present, reads hive and node ids, obtains the hive object, locks it, appends the device, rebuilds topology node arrays, updates PSP topology on all devices, optionally fetches extended topology data, and creates sysfs files and links. Removal reverses task-barrier registration, sysfs publication, list membership, and references; when the last device leaves, the hive is removed from the global list and released.

Link status rejects SR-IOV VF and single-node cases, reads version-specific PCS state registers for v6.4.x, returns active for LS0, no-link for disabled, and inactive otherwise. RAS flow selects either legacy register arrays by ASIC type/IP version or MCA banks by active AID mask, logs decoded error names, increments CE/UE statistics, and clears status. Reset-on-init waits until the hive has all expected physical nodes, schedules an XGMI reset-domain work item, resets the device list, and initializes bad-page information afterward.

## State and persistence behavior
Hive state persists as kobjects and list nodes while any device in the hive is loaded. Sysfs links mirror that state under each DRM device. The PSP topology cache in each `adev->psp.xgmi_context.top_info` is rewritten as devices join. RAS counters are hardware/firmware state and are cleared after queries/reset. Requested NPS mode is atomic hive state used to avoid duplicate unload-time requests.

## Dependencies
The implementation depends on AMDGPU core structures, PSP XGMI and RAS services, reset domains, DF FICA helpers, SMN/PCIE/MCA register access macros, ACA error-cache code, DPM power policy functions, task barriers, kobjects, and sysfs. Version-specific register addresses come from XGMI and WAFL generated headers.

## Integration points
Device bring-up and teardown call add/remove. Sysfs consumers read topology and error attributes under DRM device nodes. RAS core calls the registered block hooks. Reset code consumes the hive reset domain and reset context. Peer-memory and P2P decisions use `amdgpu_xgmi_same_hive()` and bandwidth/hops helpers. GMC partition shutdown uses the NPS change request path.

## Risks and edge cases
Hive lifetime is subtle: kobject references, `adev->hive`, global list membership, and `number_devices` must stay consistent. The sysfs removal path names `node%d` using the current device count, which is sensitive to removal order. `amdgpu_xgmi_set_pstate()` currently returns early because of a firmware bug, leaving dead code below it. Topology failure after list insertion can leave partially updated state unless every error path is audited. Legacy RAS arrays are ASIC-specific and easy to misalign with register definitions. RAS injection restores power policies only when no RAS interrupt is triggered, so interrupt-triggered paths rely on later recovery logic. Link-status helpers return a mix of negative errors and AMDGPU link constants that callers must distinguish.

## Test signals
High-value tests include multi-GPU probe/unprobe order, sysfs link correctness, PSP topology update failure injection, SR-IOV VF topology paths, v6.4.x link status for active/inactive/disabled links, RAS counter query/reset on legacy and ACA paths, reset-on-init with complete and incomplete hives, and NPS request rollback after a failed device request.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_xgmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_xgmi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_xgmi.h

## Purpose
This header declares the public XGMI data structures and helper APIs used by AMDGPU core, memory management, reset, RAS, and topology code. It defines the hive object, per-device XGMI fields, bandwidth reporting enums, and the cleanup helper used with `__free`.

## Important APIs, types, and functions
`struct amdgpu_hive_info` is the central multi-GPU state object: it has a kobject, hive id, device list, global list node, device count, hive mutex, pstate request tracking, task barrier, reset domain, RAS recovery/event manager, reset-on-init work, and requested NPS mode.

`struct amdgpu_xgmi` is embedded in GMC state and stores PSP-derived node and hive ids, node segment size, physical node id/count, list node, support flag, RAS pointers, CPU-connectivity flag, and max speed/width. `struct amdgpu_pcs_ras_field` maps decoded PCS error names to masks and shifts. `enum amdgpu_xgmi_bw_mode` distinguishes per-link versus per-peer bandwidth ranges; `enum amdgpu_xgmi_bw_unit` selects GB/s or MB/s units.

The declared API covers hive acquisition/release, topology updates, add/remove, pstate, hops, bandwidth, sharing, relative physical address calculation, hive comparison, RAS init, reset-on-init, NPS change requests, link status, external link mapping, early max-speed initialization, and manual max-speed override. `DEFINE_FREE(xgmi_put_hive, ...)` provides scope cleanup for hive references.

## Control flow
The header defines no execution beyond cleanup macro expansion. Callers typically check `adev->gmc.xgmi.supported`, add the device to a hive during initialization, query PSP-derived topology through helpers, use same-hive/bandwidth/hops during peer decisions, and remove the device at teardown.

## State and persistence behavior
The declared structures persist in memory for the lifetime of each device or hive. `amdgpu_hive_info` is kobject-owned and reference-counted; `amdgpu_xgmi` is device-owned. State exported here is not persistent across driver unload, though hive ids and node ids come from firmware and hardware topology.

## Dependencies
It depends on DRM `task_barrier`, AMDGPU RAS types, Linux kobject/list/mutex/atomic/work abstractions through included headers, and broader AMDGPU structures forward-declared elsewhere.

## Integration points
The header is included by XGMI implementation, GMC, reset, RAS, and peer-memory code. The cleanup macro is useful for functions that take hive references and need deterministic `amdgpu_put_xgmi_hive()` on return.

## Risks and edge cases
`amgpu_xgmi_set_max_speed_width` is misspelled in both declaration and definition; callers must use that exact symbol. Hive fields mix kobject lifetime, list lifetime, and reset-domain lifetime, so consumers must use the provided get/put API instead of borrowing pointers indefinitely. Bandwidth helpers depend on max speed/width having been initialized for the GC/IP version.

## Test signals
Compile coverage is important because many symbols are cross-module. Runtime signals include correct hive ref cleanup under early returns, accurate sysfs topology after add/remove, and bandwidth reporting after `amdgpu_xgmi_early_init()` or firmware override.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_xgmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgv_sriovmsg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgv_sriovmsg.h

## Purpose
This header is an ABI definition for AMD GPU SR-IOV shared memory and mailbox communication between host PF and guest VF drivers. It fixes the layout, versions, offsets, packed structures, feature flags, telemetry buffers, mailbox messages, and compile-time size checks for PF2VF, VF2PF, VBIOS, bad-page, and RAS telemetry regions.

## Important APIs, types, and functions
The v1 layout macros define 64 KiB VBIOS, 1 KiB PF2VF, 1 KiB VF2PF, 2 KiB bad-page, and 64 KiB RAS telemetry areas, with offsets and total initialization-data size. `enum amd_sriov_crit_region_version` and `enum amd_sriov_msg_table_id_enum` model v1/v2 discovery, with v2 using an `amd_sriov_msg_init_data_header` that names offsets and sizes for dynamically allocated tables.

`AMD_SRIOV_MSG_FW_VRAM_PF2VF_VER` and `AMD_SRIOV_MSG_FW_VRAM_VF2PF_VER` declare the current PF2VF/VF2PF schema versions. `enum amd_sriov_ucode_engine_id` enumerates firmware engines carried in guest reports. Packed unions define host feature flags, VF register access flags, RAS capabilities, and guest OS flags.

`struct amd_sriov_msg_pf2vf_info` is the 1 KiB host-to-guest payload: checksum, feature flags, video limits, firmware offsets/sizes, bad-page info, update interval, UUID/function identity, register access flags, VCN bandwidth limits, PCIE atomic support, GPU capacity, host BDF, and RAS caps. `struct amd_sriov_msg_vf2pf_info` is the 1 KiB guest-to-host payload: checksum, driver/OS/certification info, FB and engine usage/health, required PF2VF version, firmware versions, dummy page, and MES info.

Mailbox enums define guest requests such as GPU init/fini/reset access, init data, PSP VF command relay, VF error logging, ready-to-reset, RAS poison/count/CPER/bad-page requests, and host responses such as access grants, FLR notifications, success/fail, alive query, init-data ready, RMA, and RAS notifications. RAS telemetry structures define block error counts, CPER dump cursors, critical-hit status, host-push union, UniRAS shared memory, and the top-level telemetry object. `amd_sriov_msg_checksum()` is declared for host/guest checksum agreement.

## Control flow
The header has no runtime control flow. Runtime users map shared memory, use version/offset headers to locate tables, populate PF2VF or VF2PF structures, validate checksums, and exchange mailbox request/response ids. RAS users write or read telemetry bodies according to the selected mailbox event.

## State and persistence behavior
The structures describe persistent shared VRAM/critical-region state visible across PF and VF contexts. Packing and static assertions preserve byte-exact layout. Checksums, versions, and `valid_tables` are state guards. Some fields, such as VF utilization and RAS counts, are periodically updated; others, such as VBIOS offsets and feature flags, are initialization-time data.

## Dependencies
The file depends on fixed-width integer types and Linux compile-time `_Static_assert` when built in kernel context. It intentionally avoids AMDGPU private structures so the ABI can be shared across host, guest, and firmware-adjacent components.

## Integration points
AMDGPU SR-IOV PF/VF code, AMDGIM/GIM history, mailbox handlers, PSP relay paths, RAS telemetry paths, ROCm SMI UUID/function reporting, and VF firmware loading consume these definitions. Firmware and host tools must agree on sizes and field meanings.

## Risks and edge cases
This is ABI-sensitive: changing packing, field order, reserved sizes, or enum values can break host/guest compatibility. The `AMD_SRIOV_MSG_*_FILLED_SIZE` constants must match real field growth or the reserved arrays will no longer keep 1 KiB payloads. Bitfield layout is compiler-sensitive in general, so the code relies on a consistent build environment and packed C layout. The v2 dynamic offset header requires strict validation of sizes and checksums before trusting shared memory.

## Test signals
Compile-time static assertions check PF2VF/VF2PF size, ucode reserve alignment/capacity, and telemetry size. Runtime validation should cover checksum compatibility, version negotiation, v1 and v2 offset parsing, mailbox request/response round trips, and RAS telemetry bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgv_sriovmsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/aqua_vanjaram.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/aqua_vanjaram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/arct_reg_init.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/arct_reg_init.c

## Purpose
This small Arcturus initialization file fills AMDGPU's per-HWIP register-base table from generated Arcturus IP offset data. It makes later `SOC15` register macros resolve the right base arrays for GC, HDP, MMHUB, ATHUB, NBIO, MP0/MP1, UVD, DF, OSSSYS, SDMA0-7, SMUIO, THM, UMC, and RSMU.

## Important APIs, types, and functions
`arct_reg_base_init(struct amdgpu_device *adev)` is the only function. It loops over `MAX_INSTANCE` and assigns `adev->reg_offset[HWIP][i]` pointers to the matching generated `*_BASE.instance[i]` tables from `arct_ip_offset.h`.

## Control flow
The function is linear: for every possible instance index, assign all supported HWIP base pointers, then return zero. There is no validation or conditional behavior.

## State and persistence behavior
It mutates `adev->reg_offset`, which persists for the driver lifetime and is used by subsequent register reads/writes. No hardware registers are accessed directly here.

## Dependencies
It depends on AMDGPU core types, SOC15 common definitions, and generated Arcturus IP offset tables. The correctness of every pointer depends on `arct_ip_offset.h` matching the ASIC.

## Integration points
ASIC bring-up calls this before code uses SOC15 register accessors. ATHUB, SDMA, GC, MMHUB, and other IP blocks rely on these offsets indirectly through `RREG32_SOC15`/`WREG32_SOC15`.

## Risks and edge cases
The function assumes all generated base arrays have `MAX_INSTANCE` entries. A wrong HWIP-to-base mapping causes broad register access corruption. It intentionally initializes only blocks used by the driver; new driver code for another block must add that block here.

## Test signals
Compile-time coverage checks symbol availability. Runtime validation is indirect: IP init succeeds, SOC15 register reads hit expected hardware, and register dumps show sane offsets for every initialized HWIP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/arct_reg_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v1_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v1_0.c

## Purpose
This file implements ATHUB v1.0 clock-gating controls for SOC15-era ASICs. It toggles medium-grain clock gating and memory light sleep bits in `ATHUB_MISC_CNTL`, skipping writes on SR-IOV VFs.

## Important APIs, types, and functions
`athub_v1_0_set_clockgating()` is the exported setter. It supports ATHUB IP versions 9.0.0, 9.1.0, 9.2.0, 9.3.0, 9.4.0, and 1.5.0. `athub_v1_0_get_clockgating()` reads current hardware bits into the common AMDGPU clock-gating flag mask. Internal helpers `athub_update_medium_grain_clock_gating()` and `athub_update_medium_grain_light_sleep()` update `CG_ENABLE` and `CG_MEM_LS_ENABLE` respectively.

## Control flow
The setter returns immediately for SR-IOV VF. For supported versions it calls both update helpers with `state == AMD_CG_STATE_GATE`. Each helper reads the register, conditionally sets or clears its bit based on requested state and `adev->cg_flags`, and writes only if the value changes. The getter reads `ATHUB_MISC_CNTL` and ORs output flags when bits are set.

## State and persistence behavior
The persistent state is the hardware clock-gating register. The function does not cache state. Getter output is accumulated into a caller-provided `u64`.

## Dependencies
It depends on AMDGPU core, `athub_1_0` generated offset/mask headers, Vega10 enum definitions, SOC15 register accessors, SR-IOV detection, and common clock-gating flags.

## Integration points
AMDGPU power-management and IP block init/fini paths call the set/get hooks selected for ATHUB v1.x ASICs. The flags contribute to debug and runtime power-management reporting.

## Risks and edge cases
`athub_v1_0_get_clockgating()` sets `*flags = 0` for SR-IOV VF but does not return immediately, so it can still read hardware and set flags afterward. This differs from setters and may be intentional or a latent VF-access issue. Light sleep requires both MC and HDP light-sleep support flags, while reported output maps to ATHUB-specific flags; flag naming must remain consistent.

## Test signals
Tests or hardware checks should verify gate/ungate transitions, no writes on unsupported IP versions, VF behavior, and reported flags matching `ATHUB_MISC_CNTL` bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v1_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v1_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v1_0.h

## Purpose
This header declares the ATHUB v1.0 clock-gating interface used by AMDGPU IP block setup code.

## Important APIs, types, and functions
It declares `athub_v1_0_set_clockgating(struct amdgpu_device *adev, enum amd_clockgating_state state)` and `athub_v1_0_get_clockgating(struct amdgpu_device *adev, u64 *flags)`.

## Control flow
There is no runtime flow in the header. It supplies prototypes for the implementation in `athub_v1_0.c`.

## State and persistence behavior
No state is defined. The declared functions operate on `amdgpu_device` hardware clock-gating state and caller-provided flag storage.

## Dependencies
The prototypes rely on `struct amdgpu_device`, `enum amd_clockgating_state`, and `u64` being visible to includers through broader AMDGPU headers.

## Integration points
ATHUB v1.x IP block registration and power-management code include this header to call the versioned set/get functions.

## Risks and edge cases
The header has no include of AMDGPU types, so include order matters. Prototype drift from the implementation would break compile coverage.

## Test signals
Compile testing of ATHUB v1.x users is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v1_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v2_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v2_0.c

## Purpose
This file implements ATHUB v2.0 clock-gating and light-sleep control for IP versions 1.3.1, 2.0.0, and 2.0.2.

## Important APIs, types, and functions
`athub_v2_0_set_clockgating()` toggles clock gating for supported versions and returns zero. `athub_v2_0_get_clockgating()` reports hardware state into AMDGPU clock-gating flags. Internal helpers update `ATHUB_MISC_CNTL__CG_ENABLE_MASK` and `ATHUB_MISC_CNTL__CG_MEM_LS_ENABLE_MASK`.

## Control flow
The setter skips SR-IOV VF. For supported IP versions, it calls medium-grain clock-gating and light-sleep helpers. Unlike v1.0, each helper returns early if the matching support flags are not present, which means unsupported features are left unchanged rather than force-cleared. If supported, the helper reads `ATHUB_MISC_CNTL`, sets or clears the bit based on `state`, and writes changed values.

## State and persistence behavior
Only the ATHUB hardware register is modified. No software cache is maintained. Getter output is caller-owned.

## Dependencies
It depends on AMDGPU core, generated ATHUB 2.0 offset/mask/default headers, SOC15 accessors, SR-IOV detection, and clock-gating flag definitions.

## Integration points
The AMDGPU IP block layer uses these functions as the v2.0 ATHUB clock-gating callbacks during power-management transitions and diagnostics.

## Risks and edge cases
Because unsupported features are left unchanged, stale firmware or bootloader register bits can remain set if support flags are absent. Getter does not special-case SR-IOV VF, unlike the setter. The supported IP-version switch must be updated when a new ASIC reuses the same register layout.

## Test signals
Hardware tests should verify the support-flag early returns, gate/ungate writes for each listed IP version, getter flag accuracy, and VF no-op setter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v2_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v2_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v2_0.h

## Purpose
This header declares the ATHUB v2.0 clock-gating API.

## Important APIs, types, and functions
It declares `athub_v2_0_set_clockgating()` and `athub_v2_0_get_clockgating()` with the standard AMDGPU clock-gating callback shape.

## Control flow
The file is declarative only.

## State and persistence behavior
No state is stored in the header; the implementation mutates hardware state through `amdgpu_device`.

## Dependencies
The header assumes AMDGPU core type declarations are already available to the includer.

## Integration points
IP block and power-management code include it to bind the v2.0 ATHUB implementation.

## Risks and edge cases
Include-order dependency is the main risk. Any signature mismatch would be caught by compiler users.

## Test signals
Compile coverage of ATHUB v2.0 users validates the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v2_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v2_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v2_1.c

## Purpose
This file provides ATHUB v2.1 clock-gating support for IP versions 2.1.0, 2.1.1, 2.1.2, and 2.4.0.

## Important APIs, types, and functions
`athub_v2_1_set_clockgating()` is the exported setter and `athub_v2_1_get_clockgating()` is the exported reporter. Internal helpers directly update `CG_ENABLE` and `CG_MEM_LS_ENABLE` in `ATHUB_MISC_CNTL` according to requested state and support flags.

## Control flow
The setter exits on SR-IOV VF. For supported versions it applies both helpers. Each helper reads `ATHUB_MISC_CNTL`, sets the relevant bit only if the requested state is gate and the relevant support flags are set, otherwise clears it, and writes only on change. The getter reads the same register and ORs ATHUB MGCG/LS support bits into the caller's flags when the hardware bits are set.

## State and persistence behavior
The only persistent state is the ATHUB hardware register. Caller-provided flags are updated in place.

## Dependencies
It depends on AMDGPU core, ATHUB 2.1 generated offset/mask headers, SOC15 accessors, SR-IOV detection, and common clock-gating flags.

## Integration points
The functions are selected by ATHUB v2.1/v2.4 IP block setup for runtime clock-gating transitions and diagnostics.

## Risks and edge cases
This version force-clears bits when support flags are absent, unlike v2.0's early-return behavior. Getter still reads on SR-IOV VF. Version coverage must stay synchronized with ASIC tables.

## Test signals
Test signals are register bit transitions under all four listed IP versions, support-flag gating behavior, VF setter no-op, and getter flag accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v2_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v2_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v2_1.h

## Purpose
This header declares the ATHUB v2.1 clock-gating callbacks.

## Important APIs, types, and functions
It exposes `athub_v2_1_set_clockgating()` and `athub_v2_1_get_clockgating()`.

## Control flow
No executable flow is present.

## State and persistence behavior
The header defines no state; implementation state is hardware register state.

## Dependencies
It relies on includers having AMDGPU clock-gating types in scope.

## Integration points
Used by AMDGPU ATHUB v2.1/v2.4 IP registration and power-management code.

## Risks and edge cases
Include-order and prototype drift are the main risks.

## Test signals
Compile coverage of users validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v2_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v3_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v3_0.c

## Purpose
This file implements ATHUB v3.0 clock-gating control, including per-IP-version register address quirks for ATHUB 3.0.1 and 3.3.0.

## Important APIs, types, and functions
`athub_v3_0_set_clockgating()` supports IP versions 3.0.0, 3.0.1, 3.0.2, and 3.3.0. `athub_v3_0_get_clockgating()` reports register state. `athub_v3_0_get_cg_cntl()` and `athub_v3_0_set_cg_cntl()` abstract the `ATHUB_MISC_CNTL` address difference: 3.0.1 uses `0x00d7`, 3.3.0 uses `0x00d8`, and other supported versions use the generated `regATHUB_MISC_CNTL`.

## Control flow
The setter skips SR-IOV VF. For supported IP versions, it reads the proper control register, toggles `CG_ENABLE` if `AMD_CG_SUPPORT_ATHUB_MGCG` allows it, toggles `CG_MEM_LS_ENABLE` if `AMD_CG_SUPPORT_ATHUB_LS` allows it, and writes changed values through the version-aware setter. The getter reads through the version-aware helper and maps bits to AMDGPU flags.

## State and persistence behavior
State is entirely in the version-specific ATHUB control register. No software cache is kept.

## Dependencies
It depends on AMDGPU core, ATHUB 3.0 generated headers, Navi enum definitions, SOC15 accessors, and clock-gating flags.

## Integration points
AMDGPU ATHUB v3.x IP block callbacks use this during power-management and reporting. The register quirk helpers isolate callers from per-revision address differences.

## Risks and edge cases
Using the wrong register address for 3.0.1 or 3.3.0 would silently report or modify the wrong register. Getter has no SR-IOV VF guard. The setter ignores unsupported versions without warning, so misclassified ASICs may leave clock gating unchanged.

## Test signals
Hardware validation should cover each supported IP version's register address, gate/ungate transitions, getter flag reporting, and no-op behavior on unsupported revisions and SR-IOV VF setters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v3_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v3_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v3_0.h

## Purpose
This header declares ATHUB v3.0 clock-gating entry points.

## Important APIs, types, and functions
It declares `athub_v3_0_set_clockgating()` and `athub_v3_0_get_clockgating()`.

## Control flow
No executable logic is present.

## State and persistence behavior
The header holds no state; implementation state is hardware register state.

## Dependencies
AMDGPU device and clock-gating types must already be declared for includers.

## Integration points
ATHUB v3.x IP block code includes this header to wire power-management callbacks.

## Risks and edge cases
The simple header depends on include order and compile coverage.

## Test signals
Successful compilation of v3.x ATHUB users is the direct signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v3_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v4_1_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v4_1_0.c

## Purpose
This file provides ATHUB v4.1.0 clock-gating control for the IP version 4.1.0 register layout.

## Important APIs, types, and functions
`athub_v4_1_0_set_clockgating()` toggles clock gating for version 4.1.0. `athub_v4_1_0_get_clockgating()` reports hardware state. Internal helpers `athub_v4_1_0_get_cg_cntl()` and `athub_v4_1_0_set_cg_cntl()` read/write `regATHUB_MISC_CNTL` only for IP_VERSION(4,1,0); unsupported versions read as zero and ignore writes.

## Control flow
The setter exits for SR-IOV VF, switches on ATHUB IP version, and applies MGCG and LS helpers for 4.1.0. Each helper reads control state, sets or clears its bit based on requested state and support flags, and writes changed state through the version-aware setter. The getter reads the version-aware control register and maps enabled bits into the caller's flags.

## State and persistence behavior
Only `ATHUB_MISC_CNTL` hardware state persists. The code does not maintain a software cache.

## Dependencies
It depends on AMDGPU core, ATHUB 4.1.0 generated offset/mask headers, SOC15 accessors, SR-IOV detection, and AMDGPU clock-gating flags.

## Integration points
Used by ATHUB 4.1.0 IP block callbacks during device power-management transitions and diagnostics.

## Risks and edge cases
Unsupported versions produce a zero getter result and no write, which is safe but can mask a missing version entry. Getter has no explicit SR-IOV VF skip. The support flag for light sleep is ATHUB-specific, unlike earlier versions that sometimes check MC/HDP light-sleep flags.

## Test signals
Verify register bit transitions on IP 4.1.0, no-op behavior on unsupported versions and SR-IOV VF setters, and getter flag accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v4_1_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v4_1_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v4_1_0.h

## Purpose
This header declares the ATHUB v4.1.0 clock-gating callbacks.

## Important APIs, types, and functions
It exposes `athub_v4_1_0_set_clockgating()` and `athub_v4_1_0_get_clockgating()`.

## Control flow
The file is declarative only.

## State and persistence behavior
No state is declared here.

## Dependencies
It assumes AMDGPU clock-gating types are visible before inclusion.

## Integration points
ATHUB 4.1.0 IP setup includes this header to bind the versioned implementation.

## Risks and edge cases
The header is minimal; include-order and signature drift are the main risks.

## Test signals
Compile coverage of ATHUB 4.1.0 users validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v4_1_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atom.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atom.c

## Purpose
This file implements the legacy ATOM BIOS bytecode interpreter and parser used by AMDGPU to run firmware command tables for ASIC initialization and display programming. It validates ROM headers, indexes command/data/IIO tables, interprets ATOM opcodes, accesses device registers through driver callbacks, manages interpreter scratch/workspace state, and extracts VBIOS identity strings.

## Important APIs, types, and functions
The public functions are `amdgpu_atom_parse()`, `amdgpu_atom_execute_table()`, `amdgpu_atom_asic_init()`, `amdgpu_atom_destroy()`, `amdgpu_atom_parse_data_header()`, and `amdgpu_atom_parse_cmd_header()`. `amdgpu_atom_debug` controls verbose interpreter logging.

`atom_exec_context` carries one command-table invocation: parameter-space pointer/size, workspace pointer/size, parameter shift, command start offset, last jump tracking, and abort flag. `atom_iio_execute()` interprets indirect-I/O mini-programs for ATOM IIO ports. `atom_get_src_int()`, `atom_get_dst()`, `atom_put_dst()`, and skip/direct helpers implement operand decoding for registers, parameter space, workspace, scratch FB, immediate values, PLL, MC, and data-table offsets.

The opcode table maps ATOM bytecodes to functions for move, arithmetic, bitwise operations, shifts, compares/tests, jumps, switch, delay, calltable, set data block, set register block, set port, mask, debug, processds, and 32-bit multiply/divide. Unimplemented save/restore/repeat opcodes log messages. `amdgpu_atom_execute_table_locked()` performs the actual command walk and loop-abort handling; `amdgpu_atom_execute_table()` serializes execution with `ctx->mutex` and resets global interpreter state before entry.

Parser helpers include `atom_index_iio()`, VBIOS name/date/part-number/version/build extraction helpers, and `atom_print_vbios_info()`.

## Control flow
Parsing allocates an `atom_context`, validates BIOS, ATI, and ATOM magic strings, reads master command/data table offsets, indexes IIO methods, optionally reads firmware revision, extracts VBIOS metadata, prints summary info, and returns the context. Command execution locks the context, resets mutable interpreter globals, reads command table metadata, allocates workspace if needed, then repeatedly fetches opcodes from BIOS memory until invalid opcode or EOT. Opcode handlers mutate the instruction pointer, state registers, workspace/parameter memory, scratch memory, and hardware via callback reads/writes. Jump handling detects repeated jumps stuck longer than 20 seconds and aborts the table.

## State and persistence behavior
Persistent state lives in `atom_context`: BIOS pointer, table offsets, IIO table index, interpreter globals, scratch pointer/size, mutex, and VBIOS strings. Each command allocates transient workspace, uses caller-provided parameter storage, and can mutate hardware registers, PLL registers, MC registers, scratch memory, and context globals. The mutex serializes command execution because those globals are shared per context.

## Dependencies
The interpreter depends on ATOM generated type/name/bit headers, unaligned little-endian helpers, DRM logging/utilities, AMDGPU core, driver-supplied `card_info` register/PLL/MC callbacks, Linux memory allocation, delay, jiffies, and string helpers.

## Integration points
Display code uses this interpreter through ATOM command tables for CRTC, DP, encoder, PLL, power-gating, spread-spectrum, and AUX operations. ASIC initialization calls `amdgpu_atom_asic_init()`. Header parsers are used by many ATOMBIOS helper files to select parameter structure revisions.

## Risks and edge cases
The interpreter consumes untrusted or corrupted BIOS data with limited bounds checking; bad offsets can drive reads outside intended ROM memory. Scratch FB bounds checks use `>` rather than `>=`, which deserves care at exact-size boundaries. IIO index checks use both `0x7F` and `0xFF` masks in different paths. Several opcode paths are unimplemented. Parameter-space writes use little-endian conversion and unaligned reads, so caller buffer sizing matters. Long-running loops are detected only when repeatedly jumping to the same target and after a wall-clock timeout. Hardware callbacks can execute arbitrary register side effects from firmware bytecode.

## Test signals
Useful tests include parsing valid/invalid ROM headers, executing known ATOM command snippets, operand decoding for every storage class and alignment, workspace and parameter bounds, IIO mini-program indexing, timeout behavior, nested calltable failure propagation, VBIOS metadata extraction, and fuzzing corrupted table offsets/opcodes under a fake `card_info`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atom.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atom.h

## Purpose
This header defines the legacy ATOM BIOS interpreter API, ROM/table constants, operand encodings, workspace identifiers, IIO opcodes, and the `card_info`/`atom_context` structures shared by the parser, interpreter, and ATOMBIOS display helpers.

## Important APIs, types, and functions
Constants define BIOS magic values and offsets, ATOM ROM command/data pointers, common command/data table indexes, command-table metadata offsets, opcode count/EOT opcode, switch/case magic, operand source classes, source alignments, workspace pseudo-registers, indirect-I/O opcodes, I/O modes, and string buffer lengths.

`struct card_info` supplies driver callbacks for MM register, MC register, and PLL register reads/writes and carries the DRM device pointer. `struct atom_context` stores the card, mutex, BIOS pointer, command/data table offsets, IIO table, current data block, scratch FB base, division/multiply results, I/O attributes, register block, shift, compare flags, I/O mode, scratch pointer/size, and VBIOS metadata strings.

The public API declares parsing, command execution, ASIC init, destruction, and command/data table header parsing. It also includes `atom-types.h`, `atombios.h`, and `ObjectID.h`, making generated ATOM structures available to includers.

## Control flow
The header itself is declarative. Runtime users create an `atom_context` with `amdgpu_atom_parse()`, run command tables with `amdgpu_atom_execute_table()`, query table revisions with parse-header helpers, and free with `amdgpu_atom_destroy()`.

## State and persistence behavior
`atom_context` is long-lived driver state tied to a parsed VBIOS image. Its mutex protects mutable interpreter fields. Scratch memory is caller-provided through the context and is used by command execution.

## Dependencies
It depends on Linux integer types, DRM forward declaration, generated ATOM headers, ObjectID definitions, and AMDGPU code that fills `card_info` callbacks.

## Integration points
All legacy ATOMBIOS display helpers depend on this header for command-table constants and parameter structures. ASIC init and VBIOS metadata reporting also depend on the context.

## Risks and edge cases
The header exposes many low-level mutable fields, so consumers can accidentally bypass interpreter invariants. Include order matters for generated ATOM structures. Constants must remain synchronized with ATOM firmware format; incorrect offsets break parser safety.

## Test signals
Compile coverage across ATOMBIOS helpers, fake-card interpreter tests, and parser tests over known VBIOS images validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_crtc.c

## Purpose
This file implements legacy ATOMBIOS CRTC and PLL programming helpers for display modes. It translates DRM mode, connector, encoder, spread-spectrum, deep-color, and PLL state into versioned ATOM command-table parameter blocks executed through `amdgpu_atom_execute_table()`.

## Important APIs, types, and functions
Basic CRTC helpers are `amdgpu_atombios_crtc_overscan_setup()`, `amdgpu_atombios_crtc_scaler_setup()`, `amdgpu_atombios_crtc_lock()`, `amdgpu_atombios_crtc_enable()`, `amdgpu_atombios_crtc_blank()`, `amdgpu_atombios_crtc_powergate()`, `amdgpu_atombios_crtc_powergate_init()`, and `amdgpu_atombios_crtc_set_dtd_timing()`.

PLL and clock helpers include `amdgpu_atombios_crtc_program_ss()`, `amdgpu_atombios_crtc_adjust_pll()`, `amdgpu_atombios_crtc_set_disp_eng_pll()`, `amdgpu_atombios_crtc_set_dce_clock()`, `is_pixel_clock_source_from_pll()`, `amdgpu_atombios_crtc_program_pll()`, `amdgpu_atombios_crtc_prepare_pll()`, and `amdgpu_atombios_crtc_set_pll()`. Several unions wrap ATOM parameter revisions for spread spectrum, adjusted display PLL, set pixel clock, and set DCE clock.

## Control flow
The simple helpers zero a parameter structure, fill CRTC id or state fields, and execute a named command table. Overscan computes borders according to RMX center/aspect/full behavior. DTD timing converts DRM CRTC timing fields and sync flags into ATOM timing parameters.

PLL preparation sets default bpc and spread-spectrum state, reads monitor bpc and connector DP clock, selects spread-spectrum type by encoder mode, then calls `amdgpu_atombios_crtc_adjust_pll()`. The adjust path applies HDMI deep-color clock scaling, handles DVO/TV/LCD flags, calls versioned `AdjustDisplayPll`, and stores returned reference/post dividers in the CRTC. `amdgpu_atombios_crtc_set_pll()` computes PLL dividers, disables spread spectrum if needed, programs the versioned `SetPixelClock` table, computes SS amount/step, and re-enables spread spectrum.

## State and persistence behavior
The file mutates display hardware through ATOM command tables and updates software state in `amdgpu_crtc`: bpc, `ss_enabled`, spread-spectrum parameters, PLL flags/reference/post dividers, and adjusted clock. It also updates selected `adev->clock.ppll[]` fields before computing dividers. No standalone persistent storage is created.

## Dependencies
It depends on DRM CRTC/display mode types, AMDGPU CRTC/encoder/connector structures, ATOM interpreter APIs, ATOM command parameter definitions, connector helpers, encoder mode helpers, PLL compute code, and ATOMBIOS spread-spectrum helpers.

## Integration points
Legacy display modesetting calls these helpers when setting up scaler/overscan/timing, enabling or blanking CRTCs, power-gating display pipes, and programming display PLLs. DP helpers feed `dp_clock` into PLL adjustment. Encoder helpers provide encoder mode and transmitter identity.

## Risks and edge cases
Every command table has multiple firmware revisions; unsupported revisions only log and return, leaving hardware unchanged. HDMI deep-color clock conversion and ATOM v5/v6/v7 parameter semantics are easy to regress. Spread spectrum is skipped when another active CRTC shares the PLL, so PLL ownership tracking must be correct. Connector/private pointers are assumed present in several paths. Arithmetic uses kHz/10 kHz/100 Hz conversions that must match ATOM expectations. External spread-spectrum handling differs by PLL id and encoder mode.

## Test signals
Validation should cover all supported ATOM table revisions, HDMI 8/10/12/16 bpc clocks, DP/eDP/LVDS/DVI spread-spectrum selection, shared PLL disable-skip behavior, RMX overscan/scaler modes, invalid/missing command tables, and pixel-clock divider results compared against known BIOS traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_crtc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_crtc.h

## Purpose
This header declares the legacy ATOMBIOS CRTC, timing, display-clock, and PLL helper API.

## Important APIs, types, and functions
It declares helpers for overscan, scaler, CRTC lock/enable/blank, display power gating, DTD timing, display-engine PLL programming, DCE clock programming, pixel PLL programming, PLL preparation, and final PLL set.

## Control flow
The header is declarative. Modesetting code calls the declared functions in the order required by the legacy display pipeline: prepare PLL, program timing/scaler/overscan, enable or blank CRTC, and set PLL/clock state.

## State and persistence behavior
No state is stored in the header. Implementations mutate hardware through ATOM command tables and update `amdgpu_crtc`/clock fields.

## Dependencies
The prototypes rely on DRM CRTC/display mode types, AMDGPU device types, and `struct amdgpu_atom_ss` from ATOMBIOS headers being visible.

## Integration points
Legacy display code, encoder code, and modeset paths include this header to invoke CRTC/PLL helpers.

## Risks and edge cases
As a prototype header, the main risk is include-order or signature drift. The large `program_pll` signature is error-prone because many adjacent `u32` arguments share units-sensitive meanings.

## Test signals
Compile coverage and modeset execution through all declared helpers validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_crtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_dp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_dp.c

## Purpose
This file implements legacy ATOMBIOS DisplayPort support: AUX transfer through ATOM command tables, DPCD discovery, DP link configuration selection, panel mode detection, sink power control, link-training state machine, and encoder-service queries.

## Important APIs, types, and functions
`amdgpu_atombios_dp_aux_init()` initializes the DRM DP AUX adapter around the AMDGPU DDC bus and ATOM AUX transfer callback. `amdgpu_atombios_dp_process_aux_ch()` executes `ProcessAuxChannelTransaction` using the ATOM scratch area and returns reply status/data. `amdgpu_atombios_dp_aux_transfer()` translates DRM AUX messages into the ATOM packet format.

Discovery/config helpers include `amdgpu_atombios_dp_get_sinktype()`, `amdgpu_atombios_dp_probe_oui()`, `amdgpu_atombios_dp_ds_ports()`, `amdgpu_atombios_dp_get_dpcd()`, `amdgpu_atombios_dp_get_panel_mode()`, `amdgpu_atombios_dp_set_link_config()`, `amdgpu_atombios_dp_mode_valid_helper()`, `amdgpu_atombios_dp_needs_link_train()`, and `amdgpu_atombios_dp_set_rx_power_state()`.

Link training uses `struct amdgpu_atombios_dp_link_train_info`, `amdgpu_atombios_dp_get_adjust_train()`, `amdgpu_atombios_dp_update_vs_emph()`, `amdgpu_atombios_dp_set_tp()`, `amdgpu_atombios_dp_link_train_init()`, clock recovery `amdgpu_atombios_dp_link_train_cr()`, channel equalization `amdgpu_atombios_dp_link_train_ce()`, finish `amdgpu_atombios_dp_link_train_finish()`, and public `amdgpu_atombios_dp_link_train()`.

## Control flow
AUX init installs `amdgpu_atombios_dp_aux_transfer()` into the connector's DDC bus. Transfers build a four-byte DP AUX header, append payload for writes, call the ATOM AUX transaction table under the bus mutex, convert timeout/error reply statuses to Linux errors, copy received bytes from ATOM scratch, and set `msg->reply`.

DPCD discovery reads receiver caps, copies them into connector private state, probes OUI and downstream port data, or clears DPCD on failure. Link config chooses the lowest sufficient lane/rate pair from 1.62, 2.7, and 5.4 Gbit/s, with a Nutmeg bridge special case fixed at 2.7 Gbit/s. Link training powers the sink, enables downspread/eDP config, sets lane count and link rate, starts source training, performs clock recovery with max-voltage and repeated-voltage limits, performs channel equalization with TP2/TP3, then disables training patterns on both sink and source.

## State and persistence behavior
The file mutates connector private DP state: DPCD cache, downstream ports, sink type, lane count, DP clock, and panel mode. It mutates sink DPCD registers over AUX and source encoder/transmitter state through ATOM encoder helpers. AUX transactions use `atom_context->scratch` as transient shared storage. The DDC bus mutex serializes AUX command-table access.

## Dependencies
It depends on DRM DP helper functions, AMDGPU connector/encoder/DDC structures, ATOM interpreter and command tables, ATOMBIOS encoder helpers, and connector bpc/bridge helpers.

## Integration points
Connector detection reads DPCD and sink type through this file. Modeset validation uses `amdgpu_atombios_dp_mode_valid_helper()`. Modeset setup calls `set_link_config`, power state, and link training. CRTC PLL code uses the selected DP clock.

## Risks and edge cases
AUX transfers are limited to 16-byte payloads and depend on scratch memory layout at offsets 4 and 20. `amdgpu_atombios_dp_ds_ports()` clears downstream ports whenever `drm_dp_dpcd_read()` returns any nonzero value, which appears inverted relative to the usual positive-byte-count success convention and deserves review. Link config ignores 8b/10b overhead beyond the simple `* 8 / bpp` formula and has fixed rates. Link training returns only through logs; final failure does not propagate to callers. Some paths assume connector private data and DDC bus are present. Training loop limits and delays must track DP spec evolution.

## Test signals
Tests should cover AUX native/I2C read/write formatting, reply-status error mapping, DPCD read failure handling, OUI/downstream-port handling, bridge-specific link selection, DP1.2 5.4 Gbit/s validation, eDP panel mode detection, link-training success and max-voltage/retry failures, and sink power state writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_dp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_dp.h

## Purpose
This header declares the legacy ATOMBIOS DisplayPort helper interface.

## Important APIs, types, and functions
It declares AUX initialization, sink-type query, DPCD read, panel-mode query, link configuration selection, mode validation, link-train-needed check, sink power state update, and link training.

## Control flow
The header has no runtime flow. Display connector and modeset code call these functions during DP detection, validation, setup, and training.

## State and persistence behavior
No state is stored in the header. Implementations update connector private DP state, sink DPCD state, and source encoder state.

## Dependencies
The prototypes require AMDGPU connector types, DRM connector/encoder/display mode types, and fixed-width boolean/integer types in the include environment.

## Integration points
Legacy DP connector, encoder, and modeset paths include this header to bind ATOMBIOS DP behavior.

## Risks and edge cases
As a thin prototype header, include-order and signature drift are the main concerns. The API returns mixed boolean, int, and void results, so callers must know which operations can fail visibly.

## Test signals
Compile coverage plus DP detection/modeset/link-training execution validates the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_dp.h -->
