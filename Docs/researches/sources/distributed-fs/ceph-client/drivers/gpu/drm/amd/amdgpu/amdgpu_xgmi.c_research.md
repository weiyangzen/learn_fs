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
