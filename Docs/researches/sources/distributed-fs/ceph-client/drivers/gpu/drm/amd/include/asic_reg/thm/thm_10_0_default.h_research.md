<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_10_0_default.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_10_0_default.h

## Purpose
`thm_10_0_default.h` defines reset/default values for THM 10.0 registers in the `thm_thm_SmuThmDec` address block. It is generated-style metadata used by AMDGPU code and register tooling to understand expected power-on values for thermal, temperature-monitor, SBI/SBRMI, SMBus, and remote-monitor registers.

## Important APIs, Types, And Macros
The header exports `mm..._DEFAULT` constants only. There are no functions, structs, enums, or stateful objects.

Important default groups include:

- Thermal controller and interrupt defaults: `mmTHM_TCON_CUR_TMP_DEFAULT`, `mmTHM_TCON_HTC_DEFAULT`, `mmTHM_TCON_THERM_TRIP_DEFAULT`, `mmTHM_CTF_DELAY_DEFAULT`, `mmTHM_GPIO_PROCHOT_CTRL_DEFAULT`, `mmTHM_THERMAL_INT_ENA_DEFAULT`, `mmTHM_THERMAL_INT_CTRL_DEFAULT`, and `mmTHM_THERMAL_INT_STATUS_DEFAULT`.
- Temperature monitor data defaults: `mmTHM_TMON0_RDIL0_DATA_DEFAULT` through `RDIL15`, `mmTHM_TMON0_RDIR0_DATA_DEFAULT` through `RDIR15`, `mmTHM_TMON0_INT_DATA_DEFAULT`, `mmTHM_TMON0_CTRL_DEFAULT`, `mmTHM_TMON0_CTRL2_DEFAULT`, and `mmTHM_TMON0_DEBUG_DEFAULT`.
- Temperature and clock-gating/thermal-range defaults: `mmTHM_DIE1_TEMP_DEFAULT`, `mmTHM_DIE2_TEMP_DEFAULT`, `mmTHM_DIE3_TEMP_DEFAULT`, `mmTHM_SW_TEMP_DEFAULT`, `mmCG_MULT_THERMAL_CTRL_DEFAULT`, `mmCG_MULT_THERMAL_STATUS_DEFAULT`, and `mmCG_THERMAL_RANGE_DEFAULT`.
- TMON configuration/calibration defaults: `mmTHM_TMON_CONFIG_DEFAULT`, `mmTHM_TMON_CONFIG2_DEFAULT`, `mmTHM_TMON0_COEFF_DEFAULT`, and local threshold/control registers `mmTHM_TCON_LOCAL0_DEFAULT` through `LOCAL13`.
- Power-management, SBI, SBTSI, SBRMI, and SMBus defaults: `mmTHM_PWRMGT_DEFAULT`, `mmSMUSBI_*_DEFAULT`, `mmSBTSI_REMOTE_TEMP_DEFAULT`, `mmSBRMI_*_DEFAULT`, `mmSMBUS_*_DEFAULT`, `mmSMUSBI_SMBUS_DEFAULT`, and `mmSMUSBI_ALERT_DEFAULT`.
- Remote TMON range defaults for `TMON0` through `TMON3`, each with start and end registers defaulting to zero.

## Control Flow
There is no executable control flow. Consumers use these constants for register reset verification, golden-setting comparison, diagnostics, or generated initialization metadata. Runtime thermal-control code would use the companion offset and shift/mask headers for actual register access; this header only provides expected default values.

## State And Persistence Behavior
The header is stateless. The values describe hardware state after reset or default initialization. Many defaults are zero, but several registers have meaningful nonzero defaults, including thermal trip/control, PROCHOT GPIO control, thermal interrupt control, TMON control/config/coefficient values, `CG_MULT_THERMAL_CTRL`, `THM_PWRMGT`, SBI timing/control, SMBus control/timing/UDID fields, and SBRMI core-enable count. These defaults may be overwritten by firmware, BIOS, SMU, or driver initialization after reset.

## Dependencies
This file depends on the THM 10.0 address map and pairs with `thm_10_0_offset.h` and shift/mask definitions for the same generation. Consumers must not treat defaults as writable masks; they are complete reset-value constants.

## Integration Points
The header integrates with AMDGPU thermal-management support, SMU diagnostics, register dump tooling, and any golden-register validation paths that compare live THM registers against expected reset values. It is especially relevant to thermal interrupt setup, PROCHOT handling, SMBus/SBI sideband communication, and SBRMI remote-management state.

## Risks
- Treating defaults as mandatory runtime values can overwrite firmware-calibrated thermal settings.
- Nonzero defaults encode important board/IP assumptions, such as SMBus timing and TMON coefficients; accidental edits can invalidate diagnostics.
- Reset defaults may not match post-BIOS or post-SMU state, so tests must distinguish reset validation from runtime policy validation.
- SMBus and SBRMI defaults affect sideband-management expectations; mismatches can be misdiagnosed as communication failures.

## Test Signals
- Register-dump comparison after cold reset should match documented defaults before firmware or driver policy changes.
- Thermal bring-up tests should verify that nonzero defaults such as `THM_TCON_HTC`, `THM_THERMAL_INT_CTRL`, `THM_TMON_CONFIG`, and `THM_TMON0_COEFF` are sane for the ASIC.
- SMBus/SBI/SBRMI tests should validate timing and control defaults before active transactions.
- Runtime tests should verify that driver initialization may intentionally diverge from these defaults without being reported as an error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_10_0_default.h -->
