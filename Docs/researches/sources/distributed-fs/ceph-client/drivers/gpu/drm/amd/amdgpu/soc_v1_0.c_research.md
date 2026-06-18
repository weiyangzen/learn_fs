# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc_v1_0.c

## Purpose

`soc_v1_0.c` implements a newer AMDGPU common block for SOC v1.0/GC12.1-style multi-XCC devices. It provides standard ASIC/common lifecycle callbacks, VCN 5.0.2 codec capabilities, extended SMN addressing, doorbell setup, GRBM selection with XCC ID, and substantial XCP compute partition management for spatial/compute partition modes.

## Important APIs, Types, And Functions

Exports include `soc_v1_0_common_ip_block`, `soc_v1_0_encode_ext_smn_addressing()`, `soc_v1_0_grbm_select()`, `soc_v1_0_xcp_funcs`, `soc_v1_0_init_soc_config()`, and register normalization helpers. `soc_v1_0_doorbell_index_init()` assigns KIQ, MEC, MES, user queues, XCC doorbell range, SDMA ranges derived from SDMA instance count, IH, VCN, and non-CP ranges. `soc_v1_0_asic_reset_method()` only supports Mode2 for CPU-connected XGMI or MP1 15.0.8. XCP helpers derive/query partition modes, compute XCCs per XCP, describe XCP-owned GFXHUB/GFX/SDMA/VCN instances, calculate resource sharing, switch partitions through IMU, and optionally map XCPs to memory partition IDs through ACPI NUMA data.

## Control Flow

Early init installs PCIe indirect/extended/port accessors, ASIC callbacks, revision IDs, and minimal GC12.1 CG/PG flags. Common hw init/fini only toggles doorbell apertures. `soc_v1_0_init_soc_config()` derives AID mask from groups of four XCCs, builds an SDMA mask with two SDMA instances per XCC, initializes the XCP manager, updates supported modes, and initializes the IP map. Partition switching validates requested or auto mode against memory partitions, optionally locks KFD, runs pre-switch hooks, asks IMU firmware to switch compute partitioning, reinitializes XCP objects, runs post-switch hooks, and refreshes available modes.

## State And Persistence Behavior

Persistent driver state includes `adev->aid_mask`, `sdma_mask`, SDMA instance counts, `xcp_mgr` mode/availability/resource maps, IP maps, doorbell assignments, and `asic_funcs`. Hardware state includes doorbell aperture enablement, GRBM selection per XCC through RLC shadow writes, IMU-controlled compute partitioning, and extended SMN routing. Register normalization functions encode assumptions about XCC and MID1 register windows and directly affect cross-die register access paths.

## Dependencies And Integration Points

The file depends on SOC15 common macros, GC12.1 and MP15 register headers, GFXHUB v12.1, SDMA v7.1, GFX v12.1 XCP funcs, AMDGPU IMU, KFD locking, ACPI NUMA memory information when available, XGMI/GMC partition state, and AMDGPU IP map infrastructure.

## Risks And Test Signals

Partition math is the primary risk: invalid XCC/memory partition combinations can produce wrong resource masks or KFD-visible topology. `soc_v1_0_xcp_funcs` mutates its `switch_partition_mode` pointer for SR-IOV VFs, which is global static state and must be considered carefully. Reset support is intentionally narrow; non-Mode2 requests fail. Tests should cover SOC config derivation for different XCC masks, all valid SPX/DPX/TPX/QPX/CPX modes, auto mode, KFD lock/unlock paths, IMU partition switch failures, XCP resource maps, ACPI memory-ID mapping, register normalization, extended SMN addressing, and doorbell/ring operation.
