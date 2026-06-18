# Research: subset-b-003428 THM ASIC register headers

This grouped report covers four AMDGPU thermal-management register headers from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/`. Each section is bounded for the reconciliation lane and is also split into the required per-file research document path.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_10_0_sh_mask.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_10_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_11_0_2_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_11_0_2_offset.h

## Purpose

`thm_11_0_2_offset.h` is a compact generated register-address header for the THM 11.0.2 block. It maps selected THM, clock-gating thermal, fan, tachometer, BACO, and thermal status registers to MMIO offsets and base-index macros. Unlike a shift/mask header, it does not describe bitfields; it supplies the register identifiers used by SOC15 register access helpers.

The file is used with `thm_11_0_2_sh_mask.h` and other ASIC-specific headers so AMDGPU PM code can address THM registers by symbolic names such as `mmTHM_THERMAL_INT_CTRL` and then manipulate fields with matching mask/shift definitions.

## Important APIs, Types, And Constants

There are no functions, types, or storage declarations. The public interface is a set of `#define` constants:

- `mmCG_MULT_THERMAL_STATUS` at `0x005f`: multi-thermal status register for ASIC max and CTF temperature fields.
- `mmCG_FDO_CTRL0`, `mmCG_FDO_CTRL1`, and `mmCG_FDO_CTRL2` at `0x0067` through `0x0069`: fan duty and PWM mode controls.
- `mmCG_TACH_CTRL` and `mmCG_TACH_STATUS` at `0x006a` and `0x006b`: tachometer target/control and status registers.
- `mmTHM_THERMAL_INT_ENA` and `mmTHM_THERMAL_INT_CTRL` at `0x000a` and `0x000b`: thermal interrupt clear/set and threshold/mask control.
- `mmTHM_TCON_THERM_TRIP` at `0x0002`: thermal trip configuration and status.
- `mmTHM_BACO_CNTL` at `0x0081`: BACO power-state control used by power-management flows.
- `mmCG_THERMAL_STATUS` at `0x006c`: thermal/fan duty status.
- Every register has a matching `_BASE_IDX` macro set to `0`, matching the SOC15 accessor convention.

## Control Flow

This header has no executable flow. Runtime flow is created by consumers:

1. A PM or SMU function chooses a THM register macro from this file.
2. It passes the macro and base index to `RREG32_SOC15` or `WREG32_SOC15`.
3. It uses field macros from `thm_11_0_2_sh_mask.h` to preserve or update specific fields.

Examples from the tree include SMU11 fan control reading `mmCG_FDO_CTRL1`, writing `mmCG_FDO_CTRL0`, and updating `mmCG_FDO_CTRL2`; SMU11 interrupt setup reading and writing `mmTHM_THERMAL_INT_CTRL`; and SMU11 BACO entry paths touching `mmTHM_BACO_CNTL` on supported ASICs.

## State And Persistence Behavior

The header itself has no mutable state and persists nothing. Its offsets identify hardware registers whose values are live GPU MMIO state. Writes made through these offsets can change fan duty, thermal interrupt routing, tachometer behavior, or power-state control until hardware reset, firmware intervention, or another driver write changes the register.

Because offsets are compile-time constants, a wrong address causes all consumers to access the wrong register without any local runtime check.

## Dependencies

The file is guarded by `_thm_11_0_2_OFFSET_HEADER` and has no includes. It depends on AMDGPU SOC15 register-access conventions:

- `mm*` names are consumed by access macros that know the THM instance and base-index model.
- `_BASE_IDX` entries are expected next to each `mm*` register define.
- Field-level operations depend on companion `thm_11_0_2_sh_mask.h` macros.

## Integration Points

Direct include sites include SMU11 and some SMU13 power-management files such as `navi10_ppt.c`, `sienna_cichlid_ppt.c`, `arcturus_ppt.c`, `smu_v11_0.c`, `aldebaran_ppt.c`, and `smu_v13_0_6_ppt.c`. These consumers use this header for older SMU11-compatible THM layouts even when the surrounding power-management generation is newer.

Important integration paths:

- Fan PWM control: `smu_v11_0_set_fan_speed_pwm()` and related functions read `mmCG_FDO_CTRL1`, write `mmCG_FDO_CTRL0`, and update `mmCG_FDO_CTRL2`.
- Thermal IRQ programming: SMU11 IRQ code reads/writes `mmTHM_THERMAL_INT_CTRL`, clears events through `mmTHM_THERMAL_INT_ENA`, and relies on bit definitions from the matching shift/mask header.
- BACO power transitions: SMU and legacy PowerPlay paths use `mmTHM_BACO_CNTL` or ASIC-specific alternatives when entering BACO/BAMACO sequences.

## Risks

- Address drift between ASIC revisions is the primary risk. THM 11.0.2 offsets differ from THM 13.0.2 `reg*` offsets; using the wrong header for an ASIC can program unrelated registers.
- The header defines only a small subset of THM registers. Consumers that assume broader coverage may fail to build or may mix register maps from multiple ASIC versions.
- `mmTHM_BACO_CNTL` is power-state sensitive. A bad offset or wrong ASIC selection can corrupt BACO entry/exit behavior.
- Fan control registers are safety and acoustics sensitive. Wrong `CG_FDO_*` offsets can leave manual fan control ineffective or incorrectly configured.

## Test Signals

Useful signals include:

- Build coverage of SMU11/SMU13 files that include `thm_11_0_2_offset.h`.
- Runtime fan PWM tests verifying that writes to `mmCG_FDO_CTRL0/1/2` change reported duty and physical fan behavior as expected.
- Thermal IRQ enable/disable tests checking threshold programming, mask bits, and event delivery.
- BACO suspend/resume or runpm tests on ASICs using `mmTHM_BACO_CNTL`.
- Register trace comparison against ASIC register specifications or known-good driver versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_11_0_2_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_11_0_2_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_11_0_2_sh_mask.h

## Purpose

`thm_11_0_2_sh_mask.h` is the companion bitfield header for the THM 11.0.2 register offsets. It defines field shifts and masks for a focused subset of thermal, fan, tachometer, interrupt, trip, and thermal status registers. The scope is much smaller than the THM 10.0 mask header, matching the limited register subset exported by `thm_11_0_2_offset.h`.

The file enables AMDGPU PM code to set fan duty/PWM mode, compute tachometer periods, configure thermal interrupt thresholds and masks, decode multi-thermal status, and handle thermal trip fields through symbolic field names.

## Important APIs, Types, And Constants

There are no functions, structs, enums, or variables. Exported constants include:

- `CG_MULT_THERMAL_STATUS__ASIC_MAX_TEMP` and `CG_MULT_THERMAL_STATUS__CTF_TEMP`: 9-bit temperature fields for maximum ASIC and critical-temperature-fault values.
- `CG_FDO_CTRL0__FDO_STATIC_DUTY`: static fan duty field.
- `CG_FDO_CTRL1__FMAX_DUTY100`: fan controller value corresponding to full duty.
- `CG_FDO_CTRL2__TMIN` and `CG_FDO_CTRL2__FDO_PWM_MODE`: minimum temperature and PWM mode fields used when switching manual/static fan modes.
- `CG_TACH_CTRL__TARGET_PERIOD`: tachometer target period field, starting at bit 3 and occupying the upper register bits.
- `THM_THERMAL_INT_ENA` fields: set/clear bits for high, low, and trigger thermal interrupts.
- `THM_THERMAL_INT_CTRL` fields: high/low threshold bytes, `TEMP_THRESHOLD`, interrupt masks, PROCHOT mask, hardware interrupt enable, and `MAX_IH_CREDIT`.
- `THM_TCON_THERM_TRIP` fields: trip pad polarity, trip state/sense, threshold-exceeded bit, enable, limit, reserved spans, and software trip.
- `CG_THERMAL_STATUS__FDO_PWM_DUTY`: reported fan PWM duty field.

## Control Flow

The header has no runtime control flow. It participates in consumer flow through field helpers:

1. Fan code reads `mmCG_FDO_CTRL1`, extracts `FMAX_DUTY100`, scales a requested user PWM value to hardware duty, writes `FDO_STATIC_DUTY` into `mmCG_FDO_CTRL0`, and sets `FDO_PWM_MODE` in `mmCG_FDO_CTRL2`.
2. RPM fan control computes a tach target period and writes `CG_TACH_CTRL__TARGET_PERIOD`.
3. Thermal IRQ code reads `mmTHM_THERMAL_INT_CTRL`, sets `MAX_IH_CREDIT`, enables hardware interrupt delivery, unmasks high/low events, programs `DIG_THERM_INTH` and `DIG_THERM_INTL`, clears trigger masking, and writes clear bits through `mmTHM_THERMAL_INT_ENA`.
4. Trip handling and status code can use `THM_TCON_THERM_TRIP` and `CG_THERMAL_STATUS` fields for protection and reporting.

## State And Persistence Behavior

This file has no state. It describes bit positions in live hardware registers. Consumers mutate hardware state by writing values produced with these masks. That state may affect fan behavior, interrupt delivery, thermal trip configuration, and tachometer targets until changed by the driver, firmware, or a reset.

The header does not encode field value ranges beyond mask width. Consumers are responsible for clipping inputs, as SMU11 fan PWM code does by limiting speed to 255 and rejecting zero `FMAX_DUTY100`.

## Dependencies

The header is protected by `_thm_11_0_2_SH_MASK_HEADER` and has no includes. It depends on:

- `thm_11_0_2_offset.h` for matching register addresses.
- AMDGPU register-field helper macros that concatenate register and field names.
- Consumer code using the correct ASIC generation and THM instance.

## Integration Points

Direct integrations are visible in SMU11 PM files:

- `smu_v11_0_set_fan_static_mode()` uses `CG_FDO_CTRL2__TMIN` and `CG_FDO_CTRL2__FDO_PWM_MODE`.
- `smu_v11_0_set_fan_speed_pwm()` uses `CG_FDO_CTRL1__FMAX_DUTY100` and `CG_FDO_CTRL0__FDO_STATIC_DUTY`.
- SMU11 interrupt setup uses `THM_THERMAL_INT_CTRL` fields for high/low thresholds, interrupt masks, `THERM_IH_HW_ENA`, and `MAX_IH_CREDIT`, plus `THM_THERMAL_INT_ENA` clear-bit shifts.
- Legacy and PM code may also use the same `CG_FDO_*` names when hardware layouts match.

## Risks

- Fan control correctness depends on matching `FMAX_DUTY100`, `FDO_STATIC_DUTY`, and `FDO_PWM_MODE` widths. A bad field definition can make fan speed requests ineffective or unsafe.
- `CG_TACH_CTRL__TARGET_PERIOD_MASK` covers almost the whole register except the low three bits. Consumers must preserve reserved/other low bits when updating it.
- Thermal IRQ fields are byte-sized for high/low thresholds. Consumers clamp temperature values, but incorrect masks or shifts would still result in wrong interrupt points.
- The file exposes reserved thermal trip fields. Accidental writes through broad masks could alter reserved bits.
- Because this is generated hardware-interface data, ordinary unit tests are unlikely to catch semantic errors unless they compare against hardware specs or known-good register traces.

## Test Signals

Recommended signals include:

- Compile checks for all SMU11 and SMU11-compatible PM files that include the header.
- Fan PWM tests checking manual mode, duty scaling, `FMAX_DUTY100 == 0` rejection, and duty reporting through `CG_THERMAL_STATUS__FDO_PWM_DUTY`.
- RPM/tachometer tests verifying target period programming and reported tach status on hardware with a tach input.
- Thermal interrupt tests verifying high/low threshold programming, masks, event clearing, and delivery to the interrupt handler.
- Static generated-header validation that every mask aligns with its shift and expected field width.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_11_0_2_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_13_0_2_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_13_0_2_offset.h

## Purpose

`thm_13_0_2_offset.h` is the generated register-address map for the THM 13.0.2 block. It defines `reg*` register offsets and matching base-index macros for the thermal controller aperture whose base address is documented in the file as `0x59800`. It covers current temperature, HTC, thermal trip, GPIO-style thermal pins, interrupts, TMON sensor data, die/software temperatures, fan and pump controls, local thermal-controller state, THM power management, sideband/SBRMI, SMBus, and remote TMON windows.

This file supplies addresses only. Field definitions live in the companion `thm_13_0_2_sh_mask.h`; some field names are also compatible with earlier THM mask headers where hardware layout is shared. SMU13 code uses these `reg*` names with SOC15 register accessors.

## Important APIs, Types, And Constants

There are no functions, types, or variables. The interface is a large list of register offset constants:

- Core thermal controller registers: `regTHM_TCON_CUR_TMP`, `regTHM_TCON_HTC`, `regTHM_TCON_THERM_TRIP`, `regTHM_CTF_DELAY`, and GPIO controls for PROCHOT, THERMTRIP, PWM, tach input, pump out, and pump input.
- Interrupt registers: `regTHM_THERMAL_INT_ENA`, `regTHM_THERMAL_INT_CTRL`, and `regTHM_THERMAL_INT_STATUS`.
- TMON0 and TMON1 sensor data: repeated `RDIL0` through `RDIL15`, `RDIR0` through `RDIR15`, and `INT_DATA` registers, plus `regTHM_TMON0_CTRL` and `regTHM_TMON0_CTRL2`.
- Temperature and thermal aggregation: `regTHM_DIE1_TEMP`, `regTHM_DIE2_TEMP`, `regTHM_DIE3_TEMP`, `regTHM_SW_TEMP`, `regCG_MULT_THERMAL_CTRL`, `regCG_MULT_THERMAL_STATUS`, `regCG_THERMAL_RANGE`, `regTHM_TMON_CONFIG`, `regTHM_TMON_CONFIG2`, and TMON coefficient registers.
- Fan/tach/pump controls: `regCG_FDO_CTRL0`, `regCG_FDO_CTRL1`, `regCG_FDO_CTRL2`, `regCG_TACH_CTRL`, `regCG_TACH_STATUS`, `regCG_THERMAL_STATUS`, `regCG_PUMP_CTRL0`, `regCG_PUMP_CTRL1`, `regCG_PUMP_CTRL2`, `regCG_PUMP_TACH_CTRL`, `regCG_PUMP_TACH_STATUS`, and `regCG_PUMP_STATUS`.
- Local THM state: `regTHM_TCON_LOCAL0` through `regTHM_TCON_LOCAL15`, with `LOCAL13` intentionally listed after `LOCAL14` and `LOCAL15` by its generated offset order.
- Clock/power and MACO: `regXTAL_CNTL`, `regTHM_PWRMGT`, and `regTHM_GPIO_MACO_EN_CTRL`.
- Sideband and management interfaces: `regSBTSI_REMOTE_TEMP`, `regSBRMI_CONTROL`, `regSBRMI_COMMAND`, SBRMI write/read data, core enable, APIC, and MCE status registers.
- SMBus controls: `regSMBUS_CNTL0`, `regSMBUS_CNTL1`, block read/write command controls, timing controls, trigger control, and UDID controls.
- Remote TMON windows: `regTHM_TMON0_REMOTE_START/END`, `regTHM_TMON1_REMOTE_START/END`, and `regTHM_TMON2_REMOTE_START/END`.
- Each register has a `_BASE_IDX` macro set to `0`.

## Control Flow

The header has no executable control flow. Runtime behavior is in SMU13 consumers:

1. SMU13 code includes this offset header and the matching shift/mask header.
2. It reads or writes a THM register using `RREG32_SOC15(THM, 0, reg...)` or `WREG32_SOC15(THM, 0, reg...)`.
3. It extracts or sets fields with `REG_GET_FIELD` and `REG_SET_FIELD`.

For example, `smu_v13_0_set_fan_speed_pwm()` reads `regCG_FDO_CTRL1`, scales a user PWM request by `CG_FDO_CTRL1__FMAX_DUTY100`, writes `regCG_FDO_CTRL0` with `CG_FDO_CTRL0__FDO_STATIC_DUTY`, and then switches the controller into static PWM mode. Other SMU13 thermal paths use the interrupt and temperature-related offsets in the same access pattern.

## State And Persistence Behavior

The header stores no software state and persists nothing. Its register offsets point to hardware MMIO state. Writes through these offsets can persist in THM hardware until reset, firmware action, suspend/resume transition, or another register write changes them.

Because the file represents a complete register map for an ASIC generation, address stability is critical. A single incorrect offset can redirect driver writes to a different THM register and cause persistent hardware misconfiguration for the current boot session.

## Dependencies

The header is guarded by `_thm_13_0_2_OFFSET_HEADER` and has no includes. It depends on:

- SOC15 THM instance access conventions that understand `reg*` names and `_BASE_IDX`.
- Companion field definitions, usually `thm_13_0_2_sh_mask.h`.
- Correct ASIC selection in PM/SMU code so THM 13.0.2 offsets are not used on incompatible hardware.

## Integration Points

The main visible integration point is `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0.c`, which includes this header and uses `regCG_FDO_CTRL*` in fan PWM control. Other SMU13 platform files can rely on the same register map for thermal interrupt handling, temperature telemetry, fan/tach/pump control, and sideband/SMBus operations.

The register groups indicate integration with:

- Thermal telemetry paths for current, die, software, local/remote TMON, max/min, and critical temperature reporting.
- Thermal safety paths for HTC, thermal trip, CTF delay, PROCHOT, THERMTRIP, and interrupt routing.
- Cooling-device paths for fan duty, static PWM mode, tachometer target/status, and pump control/status.
- Power-management paths for THM clock gating, MACO enable, XTAL control, and sideband interfaces.
- Platform-management side channels via SBRMI and SMBus command/status registers.

## Risks

- ASIC-generation mismatch is the dominant risk. THM 13.0.2 uses `reg*` offsets that do not match the smaller THM 11.0.2 `mm*` map; mixing headers can access wrong registers.
- The file contains many repeated TMON offsets. Off-by-one generation errors in repeated `RDIL`/`RDIR` blocks could skew sensor selection while still compiling cleanly.
- Fan, pump, and thermal trip registers are operationally sensitive. Wrong offsets can affect cooling, acoustic control, or thermal protection.
- Sideband and SMBus register offsets can affect platform-management communication; incorrect writes may break command transactions or expose stale status.
- `LOCAL13` appears after `LOCAL14` and `LOCAL15` in generated order. Consumers should use symbolic names, not assume monotonic source order implies semantic sequence.

## Test Signals

Good validation signals include:

- Build coverage for SMU13 code that includes `thm_13_0_2_offset.h`.
- Register-access trace comparison against THM 13.0.2 hardware specifications or a known-good AMDGPU version.
- Fan PWM validation on SMU13 hardware: manual mode should change `regCG_FDO_CTRL0` duty and reported duty/status predictably.
- Temperature telemetry tests covering current, die, TMON, and aggregated max/min readings across idle and load.
- Thermal interrupt and trip tests checking threshold writes, event clear/status behavior, and interrupt delivery.
- Suspend/resume, runtime PM, and MACO/BACO-adjacent tests to catch registers that lose or incorrectly retain THM state across power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_13_0_2_offset.h -->
