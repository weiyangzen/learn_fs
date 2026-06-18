# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v1_7.c

## Purpose

This file implements Data Fabric 1.7 callbacks for AMDGPU. It initializes DF software hash-status defaults, provides broadcast-mode control, decodes framebuffer/HBM channel interleave fields, manages medium-grain clock gating, reports clock-gating state, and exposes an ECC parity write read-modify-write control hook.

## Important APIs and Functions

- `df_v1_7_sw_init()` clears `adev->df.hash_status.hash_64k`, `hash_2m`, and `hash_1g`.
- `df_v1_7_sw_fini()` is a no-op placeholder for the DF callback table.
- `df_v1_7_enable_broadcast_mode()` toggles `FabricConfigAccessControl__CfgRegInstAccEn` or restores `mmFabricConfigAccessControl_DEFAULT`.
- `df_v1_7_get_fb_channel_number()` reads `mmDF_CS_AON0_DramBaseAddress0` and extracts `IntLvNumChan`.
- `df_v1_7_get_hbm_channel_number()` maps the encoded interleave value through `df_v1_7_channel_number[]`.
- `df_v1_7_update_medium_grain_clock_gating()` enters broadcast mode, writes `DF_PIE_AON0_DfGlobalClkGater.MGCGMode`, and exits broadcast mode.
- `df_v1_7_get_clockgating_state()` reports `AMD_CG_SUPPORT_DF_MGCG` if the 15-cycle MGCG mode is present.
- `df_v1_7_enable_ecc_force_par_wr_rmw()` uses `WREG32_FIELD15` to set `ForceParWrRMW`.
- `df_v1_7_funcs` binds these operations into `struct amdgpu_df_funcs`.

## Control Flow and State

Initialization only resets software hash flags. Runtime operations are direct register reads/writes through SOC15 macros. Broadcast mode is used as a temporary register-access mode around MGCG updates, and the code restores the default access-control register afterward. The persistent state is hardware register state plus the hash-status booleans in `adev->df`.

## Dependencies and Integration Points

The file depends on `amdgpu.h`, `df_v1_7.h`, and generated DF 1.7 default/offset/mask headers. It is consumed through `adev->df.funcs`, so higher-level AMDGPU power, memory, RAS, and clock-gating paths can call revision-specific DF behavior without knowing register details.

## Risks and Test Signals

Risks include incorrect interleave-to-channel mapping, leaving broadcast mode enabled after MGCG programming, failing to honor `AMD_CG_SUPPORT_DF_MGCG`, and register field drift against generated headers. Tests should verify reported HBM channel counts, clock-gating enable/disable and state reporting, ECC force-parity write behavior, and suspend/resume or power-management paths that repeatedly toggle DF MGCG.
