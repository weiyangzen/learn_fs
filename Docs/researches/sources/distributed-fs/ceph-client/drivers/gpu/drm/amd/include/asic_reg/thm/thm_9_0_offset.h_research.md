# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_9_0_offset.h

## Purpose
`thm_9_0_offset.h` defines the THM 9.0 register offset map for the `thm_thm_SmuThmDec` address block at base `0x59800`. It is the address layer used by Vega-era AMDGPU thermal, fan, pump, BACO, interrupt, SMBus, SBRMI, and remote temperature monitor code.

## Important APIs, Types, And Functions
The file exports `mm...` offset macros and `..._BASE_IDX` companions. Major groups include core thermal-control registers (`mmTHM_TCON_CUR_TMP`, `mmTHM_TCON_HTC`, `mmTHM_TCON_THERM_TRIP`), GPIO controls for PROCHOT, thermal trip, PWM, tach, pump in/out, thermal interrupt registers, two TMON banks with left/right data and debug registers, die temperature registers, `mmCG_MULT_THERMAL_CTRL/STATUS`, fan-output and tach registers (`mmCG_FDO_*`, `mmCG_TACH_*`), pump registers (`mmCG_PUMP_*`), local TCON registers, BACO and XTAL controls, SBRMI command/data/status registers, SMBus controls/timing/UDID/BACO ranges, MACO GPIO enable, and remote TMON range markers.

## Control Flow
The header contains no runtime control flow. Included driver code passes these offsets to SOC15 read/write helpers, which perform the actual MMIO transactions. Higher-level thermal code then uses the separate sh/mask header to decode temperatures, thresholds, fan duty fields, interrupt status, and BACO control bits.

## State, Persistence, And Dependencies
No software state is maintained in the header. Live state persists in hardware registers and may be affected by reset, firmware, BIOS tables, SMU commands, and driver writes. The header depends on the SOC15 register-access framework and must stay synchronized with `thm_9_0_default.h` and `thm_9_0_sh_mask.h`.

## Integration Points
`vega10_inc.h` and `vega12_inc.h` include this file, making it available to Vega thermal paths such as `vega10_thermal.c`, `vega12_thermal.c`, `vega20_thermal.c`, BACO sequences, and related hwmgr code. In-tree references show offsets like `mmCG_MULT_THERMAL_STATUS`, `mmCG_FDO_CTRL*`, `mmTHM_THERMAL_INT_CTRL`, and `mmTHM_BACO_CNTL` being read or written for temperature reporting, fan control, thermal alerts, and low-power entry/exit sequencing.

## Risks
Offset errors are high impact because they redirect MMIO reads/writes. Fan and pump registers affect cooling behavior, thermal-interrupt registers affect over-temperature handling, and BACO registers affect power-state transitions. The THM 9.0 map is wider and uses the `mm` naming convention, while newer THM 15.0.0 headers use `reg` names and a different offset set; accidental cross-generation reuse can compile in some macro contexts but address the wrong hardware.

## Test Signals
Signals include successful builds for Vega include users, working hwmon temperature and fan reporting, fan duty/tachometer tests, thermal interrupt enable/disable tests, BACO transition tests, and register-dump comparison against the documented offset sequence. Static checks should verify that every `mm..._DEFAULT` and sh/mask register name has a matching offset where expected.
