# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_10_0_sh_mask.h

## Purpose

`thm_10_0_sh_mask.h` is a generated AMDGPU ASIC register bitfield header for THM 10.0. It defines `_SHIFT` and `_MASK` constants for thermal controller, temperature monitor, fan/thermal status, sideband, SBRMI, and SMBus registers. The file has no functions or data objects; its job is to provide the bit layout contract used by driver code when extracting fields from, or composing values for, THM MMIO registers.

The header complements THM 10.0 offset headers such as `thm_10_0_offset.h`, where register addresses are defined. Together, address macros and field macros let AMDGPU PM and thermal code use helpers like `REG_GET_FIELD`, `REG_SET_FIELD`, `PHM_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15` without hard-coding literal shifts and masks at call sites.

## Important APIs, Types, And Constants

There are no C APIs, structs, enums, or inline helpers. The exported interface is entirely preprocessor definitions grouped by hardware register.

Important groups include:

- `THM_TCON_CUR_TMP`: current temperature controller fields such as `PER_STEP_TIME_UP`, `TMP_MAX_DIFF_UP`, `CUR_TEMP_TJ_SEL`, `CUR_TEMP_RANGE_SEL`, `MCM_EN`, and the high-bit `CUR_TEMP` field. Consumers decode the current temperature by masking `THM_TCON_CUR_TMP__CUR_TEMP_MASK` and shifting by `THM_TCON_CUR_TMP__CUR_TEMP__SHIFT`.
- `THM_TCON_HTC`: hardware thermal control enable, active/log bits, PROCHOT routing, interrupt enables, limit and hysteresis fields.
- `THM_TCON_THERM_TRIP`: critical thermal trip pad polarity, trip enable, trip limit, sensed trip status, and software trip bit.
- `THM_THERMAL_INT_ENA`, `THM_THERMAL_INT_CTRL`, and `THM_THERMAL_INT_STATUS`: thermal interrupt set/clear/status controls, high/low threshold fields, interrupt masks, PROCHOT mask, hardware interrupt enable, and IH credit limit.
- `THM_TMON0_RDIL*_DATA`, `THM_TMON0_RDIR*_DATA`, and `THM_TMON0_INT_DATA`: repeated sensor result layouts with `Z`, `VALID`, and `TEMP` fields for local/remote thermal monitor inputs.
- `THM_TMON0_CTRL`, `THM_TMON0_CTRL2`, `THM_TMON_CONFIG`, `THM_TMON_CONFIG2`, and `THM_TMON0_COEFF`: thermal monitor power, calibration, acquisition, coefficient, and presence bitmaps.
- `THM_DIE1_TEMP`, `THM_DIE2_TEMP`, `THM_DIE3_TEMP`, and `THM_SW_TEMP`: die and software temperature fields.
- `CG_MULT_THERMAL_CTRL`, `CG_MULT_THERMAL_STATUS`, and `CG_THERMAL_RANGE`: selected/max/min temperature handling and thermal range reset.
- `THM_TCON_LOCAL0` through `THM_TCON_LOCAL13`: TMON power-down, global max/min temperature and ID, per-TMON maximum values, and boot-done status.
- `THM_PWRMGT`: THM-side clock gating controls.
- `SMUSBI_*`, `SBTSI_REMOTE_TEMP`, `SBRMI_*`, and `SMBUS_*`: sideband register address/data, timing, command, read/write byte lanes, core/APIC/MCE status, SMBus timing, UDID, alert, and GPIO-like pad controls.
- `THM_TMON*_REMOTE_START` and `THM_TMON*_REMOTE_END`: full-width remote thermal monitor window marker fields.

## Control Flow

This header has no runtime control flow. Compile-time inclusion makes the macros available to C files that implement thermal and PM behavior. Runtime flow happens in the consumers:

1. Driver code reads a THM register with a SOC15 accessor or indirect register accessor.
2. A field helper masks and shifts the value using the macros in this file.
3. The code interprets the extracted field as a temperature, validity bit, interrupt mask, GPIO override, or sideband command/status.
4. For writes, driver code reads the register, updates selected fields with the mask/shift pair, and writes the result back.

For example, `smu10_thermal_get_temperature()` reads `mmTHM_TCON_CUR_TMP`, extracts `CUR_TEMP`, and applies range-dependent conversion to driver temperature units. Thermal interrupt enable paths use the `THM_THERMAL_INT_CTRL` and `THM_THERMAL_INT_ENA` masks to program thresholds and clear events.

## State And Persistence Behavior

The header stores no state and performs no persistence. Its constants describe fields inside hardware registers whose values are volatile MMIO state owned by the GPU/SMU thermal controller. Changes made by consumer code persist only in the hardware register until reset, firmware action, power transition, or another driver write changes them.

Because the macros are compile-time constants, any error in a field width, shift, or mask becomes baked into every compiled consumer. There is no runtime validation layer in this header.

## Dependencies

The file depends only on the C preprocessor and its include guard `_thm_10_0_SH_MASK_HEADER`. It has no include directives.

It is functionally dependent on generated AMD register naming conventions:

- Register field macros are named `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`.
- Consumers expect masks to be unshifted field masks in register position and shifts to be bit indices.
- Macros are designed for AMDGPU helper patterns such as `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` and `REG_GET_FIELD(value, REGISTER, FIELD)`.

## Integration Points

The main integration points are AMDGPU thermal, fan, power, and sideband paths under `drivers/gpu/drm/amd/pm/` and related ASIC code. These paths combine this file with THM register offset headers and SOC15 accessors.

Notable consumer patterns visible in the tree include:

- SMU10 thermal temperature reading uses `THM_TCON_CUR_TMP__CUR_TEMP_MASK`, `THM_TCON_CUR_TMP__CUR_TEMP__SHIFT`, and `THM_TCON_CUR_TMP__CUR_TEMP_RANGE_SEL_MASK`.
- PowerPlay and SMU thermal interrupt setup use `THM_THERMAL_INT_CTRL` and `THM_THERMAL_INT_ENA` fields to set high/low thresholds, enable hardware interrupt delivery, mask events, and clear stale interrupt status.
- Thermal trip, PROCHOT, and HTC fields integrate with over-temperature protection and interrupt handling.
- TMON, SBTSI, SBRMI, and SMBus fields support sensor telemetry and low-level sideband management paths, even where a particular ASIC generation or board SKU only uses a subset.

## Risks

- Field-definition drift is high impact. If a mask or shift disagrees with the hardware specification, driver code can silently read the wrong temperature, program the wrong interrupt threshold, or alter unrelated register bits.
- Repeated sensor field layouts create copy/paste risk. The many `RDIL` and `RDIR` registers share identical `Z`, `VALID`, and `TEMP` fields; one inconsistent entry would be difficult to spot in review.
- Several fields describe safety-critical behavior, including thermal trip, PROCHOT, HTC, and interrupt thresholds. Incorrect values can cause missed throttling/shutdown events or spurious thermal interrupts.
- Some macros expose reserved fields such as `RSVD2` and `RSVD3`. Consumer code should avoid writing reserved fields except as directed by hardware programming guides.
- The header does not encode units or signedness. Temperature conversion is left to consumer code, so using a field mask where a range-selection or scaling bit is expected can produce wrong thermal readings.

## Test Signals

Useful validation signals are build-time and hardware/driver behavior oriented:

- Compile coverage for AMDGPU PM configurations that include THM 10.0 headers and exercise `REG_GET_FIELD`/`REG_SET_FIELD` expansion.
- Static checks comparing `_MASK` values against contiguous bit ranges implied by corresponding `_SHIFT` values and documented field widths.
- Runtime temperature sanity on supported THM 10.0 hardware: current temperature should track expected Celsius range and respond plausibly to load changes.
- Thermal interrupt tests should verify high/low threshold programming, event clear bits, and absence of interrupt storms.
- Fan/thermal safety validation should include over-temperature trip and PROCHOT behavior where the platform test plan permits it.
