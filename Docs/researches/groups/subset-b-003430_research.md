# subset-b-003430 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_15_0_0_offset.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_15_0_0_offset.h

### Purpose
`thm_15_0_0_offset.h` is a generated AMDGPU thermal-management register offset header for the THM block named `thm_thm_SmuThmDec`, whose documented base address is `0x59800`. It defines symbolic register offsets and base-index constants for THM 15.0.0 hardware so driver code can address temperature, hot-throttle, thermal-trip, SMU SBI, SBRMI, and SMBus registers through SOC15 register access helpers.

### Important APIs, Types, And Functions
This file exports only preprocessor constants. The main API surface is the `reg...` namespace, for example `regTHM_TCON_CUR_TMP`, `regTHM_TCON_HTC`, `regTHM_TCON_THERM_TRIP`, `regCG_MULT_THERMAL_STATUS`, `regTHM_DIE1_TEMP`, `regSMUSBI_SBIREGADDR`, `regSBRMI_COMMAND`, and `regSMBUS_CNTL0`. Every offset has a companion `..._BASE_IDX` macro, all set to `0`, for use by AMDGPU's indexed SOC register macros.

### Control Flow
There is no runtime control flow. At compile time, including code expands these macros into numeric offsets. At runtime, call sites pass the symbols to helpers such as `RREG32_SOC15()` and `WREG32_SOC15()`; those helpers combine the THM block instance, base index, and offset to perform MMIO reads and writes.

### State, Persistence, And Dependencies
The header stores no software state and performs no persistence. The persistent state is the hardware register file addressed by these constants. It depends on matching AMD ASIC register-generation data and on consumers including the corresponding shift/mask header, especially `thm_15_0_0_sh_mask.h`, to decode or modify fields after reading a register.

### Integration Points
The direct in-tree include is `pm/swsmu/smu15/smu_v15_0.c`, where this header is paired with `thm_15_0_0_sh_mask.h` and MP 15 register headers. The THM register names integrate with the AMDGPU power-management stack, SMU firmware interface code, interrupt/thermal handling, and platform-management paths that need thermal status or sideband control.

### Risks
Because this file maps symbolic names to hardware addresses, an incorrect offset can make the driver read or write the wrong THM register. The THM 15.0.0 map is not a strict superset of THM 9.0: newer `reg` names omit many fan, pump, BACO, and thermal-interrupt offsets present in the older `mm` map while adding a compact local-temperature and SMU-sideband set. Mixing this header with a mismatched sh/mask header or older `mm...` call sites would silently corrupt field interpretation.

### Test Signals
Useful signals are successful AMDGPU builds for SMU 15 targets, boot logs without THM register access faults, correct temperature readings through hwmon/SMU paths, no unexpected PROCHOT/thermal-trip events, and register readback checks on THM 15.0.0 hardware that confirm offsets such as `regCG_MULT_THERMAL_STATUS` and `regSMBUS_CNTL0` land on documented registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_15_0_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_15_0_0_sh_mask.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_15_0_0_sh_mask.h

### Purpose
`thm_15_0_0_sh_mask.h` defines bit shifts and masks for the THM 15.0.0 register offsets. It gives AMDGPU code stable field names for extracting current temperature, programming HTC/PROCHOT behavior, reading thermal ranges, managing THM clock gating, accessing die-temperature validity bits, and configuring SMU sideband, SBRMI, and SMBus behavior.

### Important APIs, Types, And Functions
The exported API is a set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros. Important groups include `THM_TCON_CUR_TMP` fields for slew settings, temperature source selection, MCM enable, and `CUR_TEMP`; `THM_TCON_HTC` fields for HTC enable/status/logging, interrupt enables, PROCHOT source, limit, hysteresis, and slew; `THM_TCON_THERM_TRIP` fields for CTF/therm-trip thresholds and status; `CG_MULT_THERMAL_STATUS` fields for ASIC max temperature and CTF temperature; `THM_DIE{1,2,3}_TEMP` fields for per-die temperature and valid bits; and sideband groups for `SMUSBI_*`, `SBRMI_*`, `SMBUS_*`, `SMUSBI_SMBUS`, and `SMUSBI_ALERT`.

### Control Flow
The file has no executable control flow. Consumers typically read a register, apply a mask, shift the result down, and make policy decisions from the decoded value. For writes, consumers compose values by clearing the mask and inserting shifted field values. The field macros are also compatible with AMDGPU helper macros such as `REG_GET_FIELD()` and `REG_SET_FIELD()` where the helper's naming convention matches the register symbols.

### State, Persistence, And Dependencies
No software state is retained. Hardware state is represented by the live MMIO registers addressed by `thm_15_0_0_offset.h`. The header depends on exact alignment with THM 15.0.0 register layout; mask widths encode data sizes such as 9-bit temperatures, 11-bit local/die temperatures, 7-bit HTC limits, 20-bit CTF delay, and full 32-bit payload/status registers.

### Integration Points
The direct consumer path is the SMU 15 power-management layer via `smu_v15_0.c`, which includes this file alongside `thm_15_0_0_offset.h`. The field definitions connect hardware register state to driver features such as temperature reporting, throttling, interrupt routing, thermal-trip handling, remote sensor access, SMBus alert signaling, SBRMI command/data exchange, and SMUSBI timing/control.

### Risks
Bitfield drift is the main risk. A stale shift or mask can produce plausible but wrong thermal values, program wrong PROCHOT polarity/source bits, or mis-handle sideband bus transactions. Several fields control safety-relevant behavior, including thermal-trip enable/status, HTC limits, PROCHOT routing, and SMBus alert GPIO controls. Full-width masks for data/status registers also make it easy for callers to overwrite reserved or hardware-owned bits if they do not follow register programming guidance.

### Test Signals
Signals include compile coverage for all field names used by SMU 15 code, runtime validation of reported temperatures and valid bits, thermal-throttle interrupt tests, PROCHOT/therm-trip tests where available, and hardware register readback after field writes. Static checks can compare each mask to its shift and expected width to catch overlapping or out-of-range fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_15_0_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_9_0_default.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_9_0_default.h

### Purpose
`thm_9_0_default.h` records reset/default values for THM 9.0 registers. It is the companion to the THM 9.0 offset and shift/mask headers, giving Vega-era power-management code the expected baseline values for thermal controller registers, GPIO controls, thermal interrupts, TMON sensor banks, fan and pump controls, BACO timing, SBRMI, SMBus, and remote-monitor ranges.

### Important APIs, Types, And Functions
The file exports `mm..._DEFAULT` macros only. Important defaults include `mmTHM_TCON_HTC_DEFAULT` (`0x00004000`), `mmTHM_TCON_THERM_TRIP_DEFAULT` (`0x00000001`), GPIO defaults such as `mmTHM_GPIO_PROCHOT_CTRL_DEFAULT`, interrupt defaults such as `mmTHM_THERMAL_INT_CTRL_DEFAULT`, fan/pump defaults such as `mmCG_FDO_CTRL0_DEFAULT`, `mmCG_FDO_CTRL1_DEFAULT`, and `mmCG_FDO_CTRL2_DEFAULT`, thermal aggregation defaults such as `mmCG_MULT_THERMAL_CTRL_DEFAULT`, BACO defaults such as `mmTHM_BACO_TIMING0_DEFAULT`, and SMBus defaults such as `mmSMBUS_CNTL0_DEFAULT`, `mmSMBUS_TIMING_CNTL0_DEFAULT`, and `mmSMBUS_UDID_CNTL2_DEFAULT`.

### Control Flow
There is no control flow in this header. Consumers use the constants for reset expectations, register tables, diagnostics, or initialization code that wants to compare against or restore documented reset values. The macros become compile-time literals in any code that includes a THM 9.0 platform include such as `vega10_inc.h` or `vega12_inc.h`.

### State, Persistence, And Dependencies
The header stores no state. It documents hardware reset state, while live state resides in THM registers and may be changed by BIOS, SMU firmware, power-management code, or runtime thermal policy. It depends on the THM 9.0 offset header for register names and on `thm_9_0_sh_mask.h` for interpreting each default value's fields.

### Integration Points
`vega10_inc.h` and `vega12_inc.h` include this file with the THM 9.0 offset and sh/mask headers. Those include feed Vega thermal and power-management files that read or program fan controls, pump controls, current temperature, thermal-interrupt thresholds, BACO state, and CTF temperature through SOC15 helpers. Defaults also provide reference values for bring-up and debug against the generated ASIC register map.

### Risks
Default values are not necessarily safe runtime write values on every board because firmware, board straps, and platform policy may legitimately alter thermal, GPIO, SMBus, and fan/pump configuration after reset. Copying a default value wholesale can clear sticky status, disable interrupts, or undo firmware configuration. The file also covers a broad register set; if paired with the wrong ASIC generation or offset map, defaults may describe the wrong register.

### Test Signals
Useful tests include building Vega10/Vega12 power-management code, comparing early boot register dumps against defaults where firmware has not modified state, validating fan/pump behavior after initialization, checking thermal interrupt thresholds, and ensuring debug or reset paths do not blindly write defaults over firmware-owned fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_9_0_default.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_9_0_offset.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_9_0_offset.h

### Purpose
`thm_9_0_offset.h` defines the THM 9.0 register offset map for the `thm_thm_SmuThmDec` address block at base `0x59800`. It is the address layer used by Vega-era AMDGPU thermal, fan, pump, BACO, interrupt, SMBus, SBRMI, and remote temperature monitor code.

### Important APIs, Types, And Functions
The file exports `mm...` offset macros and `..._BASE_IDX` companions. Major groups include core thermal-control registers (`mmTHM_TCON_CUR_TMP`, `mmTHM_TCON_HTC`, `mmTHM_TCON_THERM_TRIP`), GPIO controls for PROCHOT, thermal trip, PWM, tach, pump in/out, thermal interrupt registers, two TMON banks with left/right data and debug registers, die temperature registers, `mmCG_MULT_THERMAL_CTRL/STATUS`, fan-output and tach registers (`mmCG_FDO_*`, `mmCG_TACH_*`), pump registers (`mmCG_PUMP_*`), local TCON registers, BACO and XTAL controls, SBRMI command/data/status registers, SMBus controls/timing/UDID/BACO ranges, MACO GPIO enable, and remote TMON range markers.

### Control Flow
The header contains no runtime control flow. Included driver code passes these offsets to SOC15 read/write helpers, which perform the actual MMIO transactions. Higher-level thermal code then uses the separate sh/mask header to decode temperatures, thresholds, fan duty fields, interrupt status, and BACO control bits.

### State, Persistence, And Dependencies
No software state is maintained in the header. Live state persists in hardware registers and may be affected by reset, firmware, BIOS tables, SMU commands, and driver writes. The header depends on the SOC15 register-access framework and must stay synchronized with `thm_9_0_default.h` and `thm_9_0_sh_mask.h`.

### Integration Points
`vega10_inc.h` and `vega12_inc.h` include this file, making it available to Vega thermal paths such as `vega10_thermal.c`, `vega12_thermal.c`, `vega20_thermal.c`, BACO sequences, and related hwmgr code. In-tree references show offsets like `mmCG_MULT_THERMAL_STATUS`, `mmCG_FDO_CTRL*`, `mmTHM_THERMAL_INT_CTRL`, and `mmTHM_BACO_CNTL` being read or written for temperature reporting, fan control, thermal alerts, and low-power entry/exit sequencing.

### Risks
Offset errors are high impact because they redirect MMIO reads/writes. Fan and pump registers affect cooling behavior, thermal-interrupt registers affect over-temperature handling, and BACO registers affect power-state transitions. The THM 9.0 map is wider and uses the `mm` naming convention, while newer THM 15.0.0 headers use `reg` names and a different offset set; accidental cross-generation reuse can compile in some macro contexts but address the wrong hardware.

### Test Signals
Signals include successful builds for Vega include users, working hwmon temperature and fan reporting, fan duty/tachometer tests, thermal interrupt enable/disable tests, BACO transition tests, and register-dump comparison against the documented offset sequence. Static checks should verify that every `mm..._DEFAULT` and sh/mask register name has a matching offset where expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_9_0_offset.h -->
