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
