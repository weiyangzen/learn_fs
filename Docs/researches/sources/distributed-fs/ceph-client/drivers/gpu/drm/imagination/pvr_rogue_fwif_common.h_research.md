# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_common.h

Purpose: This small shared header centralizes FWIF alignment requirements, firmware data-master IDs, GPU utilization state IDs, and register-programmer write limits used by the broader Rogue FWIF ABI.

Important APIs/types/functions: `PVR_FW_ALIGNMENT_LSB` requires low three bits clear for 8-byte granularity. `PVR_FW_STRUCT_SIZE_ASSERT(type)` statically checks ABI struct sizes. Data-master IDs define GP, 2D/TDM, GEOM, FRAG, CDM, RAY, GEOM2-4, `PVR_FWIF_DM_LAST`, and `PVR_FWIF_DM_MAX`. GPU util states are idle, active, blocked, count, and mask. `PVR_MAX_NUM_REGISTER_PROGRAMMER_WRITES` caps firmware/register-programmer write batches at 128.

Control flow: None, apart from compile-time `static_assert` expansion.

State and persistence behavior: No local state. The constants size arrays in persistent shared structs such as HWR recovery flags and utilization counters.

Dependencies and integration points: Depends on `linux/build_bug.h`. Included by central FWIF headers and any code needing stable DM IDs. It integrates with scheduler DM routing, HWR per-DM arrays, utilization accounting, and register programming validation.

Risks: Changing DM numeric values breaks firmware/host interpretation of per-DM state and command routing. A wrong utilization mask corrupts packed time/state words. Weakening alignment checks can hide ABI drift.

Test signals: Build-time assertions, HWR array size checks, GPU utilization accounting tests, and workloads across all supported DMs.
