# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/trinityd.h

## Purpose

`trinityd.h` is the Trinity DPM register and bitfield definition header. It maps SMU, SMC, clock-gating, thermal, power-management, fuse, scratch, and display-related register offsets plus field masks/shifts used by `trinity_dpm.c` and `trinity_smc.c`.

## Important APIs, Types, and Functions

- DPM state table registers: `SMU_SCLK_DPM_STATE_0_CNTL_0`, `_CNTL_1`, `_CNTL_3`, `_AT`, `_PG_CNTL`, and `SMU_SCLK_DPM_STATE_1_CNTL_0`.
- Field macros define DPM level validity, clock divider, VID/LVRT, deep-sleep dividers, display/VCE watermarks, GNB slow, forced NB P-state, and activity threshold values.
- Global DPM controls include `SMU_SCLK_DPM_CNTL`, `SMU_SCLK_DPM_TT_CNTL`, `SMU_SCLK_DPM_TTT`, `PM_I_CNTL_1`, `GENERAL_PWRMGT`, `SCLK_PWRMGT_CNTL`, and `TARGET_AND_CURRENT_PROFILE_INDEX`.
- UVD/NB/media controls include `SMU_UVD_DPM_STATES`, `SMU_UVD_DPM_CNTL`, `NB_PSTATE_CONFIG`, and `DC_CAC_VALUE`.
- Power-gating and clock-gating controls include `GFX_POWER_GATING_CNTL`, `SMU_S_PG_CNTL`, `CG_GIPOTS`, `CG_PG_CTRL`, `CG_CGTT_LOCAL_0/1`, `CGTS_SM_CTRL_REG`, and `CG_MISC_REG`.
- SMC communication registers are `SMC_INT_REQ`, `SMC_MESSAGE_0`, `SMC_RESP_0`, and `SMU_SCRATCH0`.

## Control Flow

The header has no runtime control flow. It enables the DPM implementation to perform read/modify/write sequences with named fields and register offsets.

## State and Persistence Behavior

Every macro names hardware state that persists in MMIO or SMC register space. The C driver caches only selected values elsewhere; the authoritative DPM, thermal, clock-gating, and SMC message state resides in hardware/firmware registers.

## Dependencies and Integration Points

- Used by Trinity DPM and SMC files through Radeon register access macros such as `RREG32`, `WREG32`, `RREG32_SMC`, and `WREG32_SMC`.
- Constants must match the Trinity hardware register map and firmware expectations for DPM state-table spacing.

## Risks and Edge Cases

- Macros are simple shifts and masks with no range checking. Callers can silently truncate or overflow fields if values exceed bit width.
- Register offsets are hardware ABI. A wrong value can corrupt unrelated GPU state.
- `TRINITY_SIZEOF_DPM_STATE_TABLE` in `trinity_dpm.h` depends on the spacing between definitions in this header.

## Test Signals

- Register programming tests should compare known-good traces against generated values for DPM levels, thermal thresholds, NB P-states, and clock-gating sequences.
- Static review should verify mask/shift pairs and DPM state-table spacing whenever register definitions change.
