# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_15_0_0_sh_mask.h

## Purpose
`thm_15_0_0_sh_mask.h` defines bit shifts and masks for the THM 15.0.0 register offsets. It gives AMDGPU code stable field names for extracting current temperature, programming HTC/PROCHOT behavior, reading thermal ranges, managing THM clock gating, accessing die-temperature validity bits, and configuring SMU sideband, SBRMI, and SMBus behavior.

## Important APIs, Types, And Functions
The exported API is a set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros. Important groups include `THM_TCON_CUR_TMP` fields for slew settings, temperature source selection, MCM enable, and `CUR_TEMP`; `THM_TCON_HTC` fields for HTC enable/status/logging, interrupt enables, PROCHOT source, limit, hysteresis, and slew; `THM_TCON_THERM_TRIP` fields for CTF/therm-trip thresholds and status; `CG_MULT_THERMAL_STATUS` fields for ASIC max temperature and CTF temperature; `THM_DIE{1,2,3}_TEMP` fields for per-die temperature and valid bits; and sideband groups for `SMUSBI_*`, `SBRMI_*`, `SMBUS_*`, `SMUSBI_SMBUS`, and `SMUSBI_ALERT`.

## Control Flow
The file has no executable control flow. Consumers typically read a register, apply a mask, shift the result down, and make policy decisions from the decoded value. For writes, consumers compose values by clearing the mask and inserting shifted field values. The field macros are also compatible with AMDGPU helper macros such as `REG_GET_FIELD()` and `REG_SET_FIELD()` where the helper's naming convention matches the register symbols.

## State, Persistence, And Dependencies
No software state is retained. Hardware state is represented by the live MMIO registers addressed by `thm_15_0_0_offset.h`. The header depends on exact alignment with THM 15.0.0 register layout; mask widths encode data sizes such as 9-bit temperatures, 11-bit local/die temperatures, 7-bit HTC limits, 20-bit CTF delay, and full 32-bit payload/status registers.

## Integration Points
The direct consumer path is the SMU 15 power-management layer via `smu_v15_0.c`, which includes this file alongside `thm_15_0_0_offset.h`. The field definitions connect hardware register state to driver features such as temperature reporting, throttling, interrupt routing, thermal-trip handling, remote sensor access, SMBus alert signaling, SBRMI command/data exchange, and SMUSBI timing/control.

## Risks
Bitfield drift is the main risk. A stale shift or mask can produce plausible but wrong thermal values, program wrong PROCHOT polarity/source bits, or mis-handle sideband bus transactions. Several fields control safety-relevant behavior, including thermal-trip enable/status, HTC limits, PROCHOT routing, and SMBus alert GPIO controls. Full-width masks for data/status registers also make it easy for callers to overwrite reserved or hardware-owned bits if they do not follow register programming guidance.

## Test Signals
Signals include compile coverage for all field names used by SMU 15 code, runtime validation of reported temperatures and valid bits, thermal-throttle interrupt tests, PROCHOT/therm-trip tests where available, and hardware register readback after field writes. Static checks can compare each mask to its shift and expected width to catch overlapping or out-of-range fields.
