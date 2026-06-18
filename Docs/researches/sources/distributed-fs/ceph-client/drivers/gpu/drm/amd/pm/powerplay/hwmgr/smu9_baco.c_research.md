# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu9_baco.c

Purpose: provides SMU9 BACO/BAMACO support probing and current BACO state reporting.

Important APIs and functions: `smu9_get_bamaco_support()` checks `PHM_PlatformCaps_BACO`, writes/reads magic registers `0x12074/0x12075`, then reads SOC15 NBIF `RCC_BIF_STRAP0` and returns `BACO_SUPPORT` only when `STRAP_PX_CAPABLE` is set. `smu9_baco_get_state()` reads `mmBACO_CNTL` and maps `BACO_MODE` to `BACO_STATE_IN` or `BACO_STATE_OUT`.

Control flow and state: this file does not enter or exit BACO. It only reports support and current state from hardware registers. No driver-side state is persisted.

Dependencies and integration: uses SOC15/Vega10 register headers, `amdgpu.h`, `smu9_baco.h`, register macros, platform caps, and common BACO types. Higher-level power-management code consumes these queries.

Risks and test signals: magic support-probe registers are undocumented in code and may be ASIC-specific. No null checks are present for `hwmgr` or `state`. Test support detection on PX/non-PX SMU9 platforms and state reads before/after higher-level BACO transitions.
