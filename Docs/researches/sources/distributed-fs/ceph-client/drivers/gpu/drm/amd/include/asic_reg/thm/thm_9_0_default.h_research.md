# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_9_0_default.h

## Purpose
`thm_9_0_default.h` records reset/default values for THM 9.0 registers. It is the companion to the THM 9.0 offset and shift/mask headers, giving Vega-era power-management code the expected baseline values for thermal controller registers, GPIO controls, thermal interrupts, TMON sensor banks, fan and pump controls, BACO timing, SBRMI, SMBus, and remote-monitor ranges.

## Important APIs, Types, And Functions
The file exports `mm..._DEFAULT` macros only. Important defaults include `mmTHM_TCON_HTC_DEFAULT` (`0x00004000`), `mmTHM_TCON_THERM_TRIP_DEFAULT` (`0x00000001`), GPIO defaults such as `mmTHM_GPIO_PROCHOT_CTRL_DEFAULT`, interrupt defaults such as `mmTHM_THERMAL_INT_CTRL_DEFAULT`, fan/pump defaults such as `mmCG_FDO_CTRL0_DEFAULT`, `mmCG_FDO_CTRL1_DEFAULT`, and `mmCG_FDO_CTRL2_DEFAULT`, thermal aggregation defaults such as `mmCG_MULT_THERMAL_CTRL_DEFAULT`, BACO defaults such as `mmTHM_BACO_TIMING0_DEFAULT`, and SMBus defaults such as `mmSMBUS_CNTL0_DEFAULT`, `mmSMBUS_TIMING_CNTL0_DEFAULT`, and `mmSMBUS_UDID_CNTL2_DEFAULT`.

## Control Flow
There is no control flow in this header. Consumers use the constants for reset expectations, register tables, diagnostics, or initialization code that wants to compare against or restore documented reset values. The macros become compile-time literals in any code that includes a THM 9.0 platform include such as `vega10_inc.h` or `vega12_inc.h`.

## State, Persistence, And Dependencies
The header stores no state. It documents hardware reset state, while live state resides in THM registers and may be changed by BIOS, SMU firmware, power-management code, or runtime thermal policy. It depends on the THM 9.0 offset header for register names and on `thm_9_0_sh_mask.h` for interpreting each default value's fields.

## Integration Points
`vega10_inc.h` and `vega12_inc.h` include this file with the THM 9.0 offset and sh/mask headers. Those includes feed Vega thermal and power-management files that read or program fan controls, pump controls, current temperature, thermal-interrupt thresholds, BACO state, and CTF temperature through SOC15 helpers. Defaults also provide reference values for bring-up and debug against the generated ASIC register map.

## Risks
Default values are not necessarily safe runtime write values on every board because firmware, board straps, and platform policy may legitimately alter thermal, GPIO, SMBus, and fan/pump configuration after reset. Copying a default value wholesale can clear sticky status, disable interrupts, or undo firmware configuration. The file also covers a broad register set; if paired with the wrong ASIC generation or offset map, defaults may describe the wrong register.

## Test Signals
Useful tests include building Vega10/Vega12 power-management code, comparing early boot register dumps against defaults where firmware has not modified state, validating fan/pump behavior after initialization, checking thermal interrupt thresholds, and ensuring debug or reset paths do not blindly write defaults over firmware-owned fields.
