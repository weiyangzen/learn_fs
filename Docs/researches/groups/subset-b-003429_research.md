# subset-b-003429 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_13_0_2_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_13_0_2_sh_mask.h

## Purpose

`thm_13_0_2_sh_mask.h` is a generated AMDGPU ASIC register bitfield header for the THM block on SMU/PM firmware generation 13.0.2 hardware. It does not define executable code; it defines C preprocessor constants that describe bit shifts and bit masks for fields inside THM, thermal monitor, fan, pump, clock/power, SBRMI, SBTSI, and SMBus registers. The companion offset header supplies register addresses; this file supplies the layout of each 32-bit register value once a caller has read or is preparing to write the register.

The header is consumed by the AMDGPU power-management stack through `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0.c`, which includes both `thm_13_0_2_offset.h` and this mask file. The most visible uses are thermal interrupt programming and fan/tachometer programming, where the driver combines `RREG32_SOC15`/`WREG32_SOC15` register IO with `REG_GET_FIELD` and `REG_SET_FIELD` bitfield helpers.

## Important APIs, types, and constants

The exported interface is entirely macro based:

- `REGISTER__FIELD__SHIFT` constants define the low bit position of a field.
- `REGISTER__FIELD_MASK` constants define the full field mask in the 32-bit register word.
- Register comments such as `//THM_TCON_CUR_TMP` and `//CG_FDO_CTRL0` segment the generated field table by hardware register.
- The include guard is `_thm_13_0_2_SH_MASK_HEADER`.

Important register families covered by this header include:

- `THM_TCON_CUR_TMP`: current temperature register fields such as `CUR_TEMP`, `CUR_TEMP_RANGE_SEL`, `CUR_TEMP_TJ_SEL`, `CUR_TEMP_TJ_SLEW_SEL`, and `MCM_EN`. `CUR_TEMP` occupies bits 31:21 via `0xFFE00000`, which is the field used by temperature-reading paths on related SMU generations.
- `THM_TCON_HTC` and `THM_TCON_THERM_TRIP`: hardware thermal control, PROCHOT, hysteresis, thermal trip enable/status, and software thermal trip fields.
- `THM_GPIO_*_CTRL`: common GPIO pad control layouts for PROCHOT, thermtrip, PWM, tach input, pump out, and pump in pins. These define pull-up/down, Schmitt enable, output enable override, pin data, and readback bits.
- `THM_THERMAL_INT_ENA`, `THM_THERMAL_INT_CTRL`, and `THM_THERMAL_INT_STATUS`: thermal interrupt set/clear, high/low threshold, trigger mask, PROCHOT mask, IH hardware enable, and interrupt credit fields.
- `THM_TMON0_*`, `THM_TMON1_*`, `THM_DIE*_TEMP`, `THM_TMON_CONFIG*`, and `THM_TMON*_COEFF`: a dense thermal monitor sensor map. The RDIL/RDIR arrays expose repeated `Z`, `VALID`, and `TEMP` fields for many sensor lanes; control/configuration fields define power-down, acquisition, calibration, coefficient, and present-bit behavior.
- `CG_MULT_THERMAL_*` and `CG_THERMAL_RANGE`: filtered/multiple thermal status and ASIC min/max thermal range fields.
- `CG_FDO_*`, `CG_TACH_*`, and `CG_THERMAL_STATUS`: fan duty, fan spin-up, manual PWM mode, hysteresis, ramp, tach target, tach status, and PWM duty readback fields.
- `CG_PUMP_*`: pump duty, pump spin-up, manual PWM mode, tach, and status fields paralleling the fan control group.
- `THM_TCON_LOCAL*`: local temperature-controller state such as global TMAX/TMIN values, sensor IDs, Tj max fields, TMON power-down controls, and boot completion.
- `XTAL_CNTL` and `THM_PWRMGT`: THM reference-clock, clock gate, fan/pump gate, and prototype TSEN clock toggle controls.
- `SBTSI_REMOTE_TEMP`, `SBRMI_*`, `SMBUS_*`, and remote TMON start/end fields: sideband temperature and management bus command/data/timing/UDID register layouts.

The file contains 1,111 `#define` lines and 1297 total lines. It is significantly broader than the v14 mask file in this work item because it includes the TMON0/TMON1 sensor arrays and remote TMON start/end definitions.

## Control flow

There is no runtime control flow inside the header. It affects control flow indirectly by making call sites select, set, clear, or decode specific hardware bits. In `smu_v13_0.c`, the constants participate in these flows:

- Fan control writes `regCG_FDO_CTRL2` and `regCG_FDO_CTRL0` with `REG_SET_FIELD(..., CG_FDO_CTRL2, TMIN, ...)`, `FDO_PWM_MODE`, and `FDO_STATIC_DUTY`.
- Fan speed conversion reads `regCG_FDO_CTRL1` and extracts `CG_FDO_CTRL1.FMAX_DUTY100`.
- Tachometer target programming writes `regCG_TACH_CTRL.TARGET_PERIOD`.
- Thermal interrupt disable masks `THERM_INTH_MASK` and `THERM_INTL_MASK`, then writes `regTHM_THERMAL_INT_ENA` to clear/disable interrupt delivery.
- Thermal interrupt enable/configuration sets `MAX_IH_CREDIT`, `THERM_IH_HW_ENA`, `DIG_THERM_INTH`, and `DIG_THERM_INTL`, then clears pending high/low/trigger bits using the `THM_THERMAL_INT_ENA__*_CLR__SHIFT` constants.
- Thermal interrupt handling adjusts high/low threshold fields in response to IH events and clears the trigger mask using `THM_THERMAL_INT_CTRL__THERM_TRIGGER_MASK_MASK`.

Because the macro names encode the register and field names, the Linux register helper macros can token-paste the selected register and field into the correct mask/shift constant. Any rename or field-layout change in this file can therefore alter compile-time expansion for driver code without changing the C call sites.

## State and persistence behavior

The file stores no software state and allocates no memory. The state it describes lives in hardware registers in the THM, fan, pump, sensor, and sideband-management blocks. Persistence is therefore governed by ASIC reset, power-management transitions, firmware initialization, BACO/low-power sequences, and suspend/resume behavior, not by this header.

Some described fields are explicitly stateful hardware latches or controls:

- Thermal interrupt status/detect bits record threshold crossings until cleared.
- `THM_TCON_HTC__HTC_ACTIVE_LOG_MASK` records HTC activity.
- `THM_TCON_THERM_TRIP__SW_THERM_TP_MASK` can assert a software thermal trip.
- TMON `VALID` fields qualify sensor data before consumers should trust `TEMP`.
- Fan and pump manual/static duty fields persist as programmed register values until another driver/firmware path changes them.
- SMBus/SBRMI command status bits describe command completion, unsupported command, abort, and status nibbles.

Driver code must treat these values as live hardware state, often shared with SMU firmware, not as ordinary software configuration.

## Dependencies and integration points

Primary dependencies are the AMDGPU register access stack and companion generated register headers:

- `thm_13_0_2_offset.h` supplies `reg...` addresses for the same THM register names.
- `smu_v13_0.c` includes this file and uses the fields through `RREG32_SOC15`, `WREG32_SOC15`, `REG_GET_FIELD`, and `REG_SET_FIELD`.
- `soc15_common.h` and AMDGPU SMU support code provide the register access and field helper semantics.
- THM interrupt programming integrates with the AMDGPU interrupt handler path through thermal source IDs and `SMU_THERMAL_MINIMUM_ALERT_TEMP`/alert-range logic.
- BACO paths in `smu_v13_0.c` integrate with THM-related low-power behavior, although the visible v13 BACO control flow mostly uses SMU messages rather than directly writing the `THM_BACO_*` fields from this header.

The generated names intentionally match hardware register specifications. The value of the file is not local abstraction; it is exact ABI compatibility with silicon.

## Risks

The main risk is silent hardware misprogramming if masks or shifts do not match the target ASIC. A wrong thermal threshold mask can suppress interrupts, fire interrupts at the wrong temperature, or leave trigger bits uncleared. A wrong fan or pump duty field can produce incorrect cooling behavior. A wrong GPIO bit can invert or disable PROCHOT/THERMTRIP signaling. A wrong SMBus/SBRMI field can corrupt sideband commands.

There is also a cross-generation compatibility risk. Many names match older and newer THM headers, but field presence and reserved ranges differ. For example, this v13 file lacks `THM_TCON_CUR_TMP__REMOTE_TJ_SEL`, which appears in the v14 mask file. Consumers must include the header matching the IP version selected by the SMU code and must not assume all generations expose identical fields.

Because these are preprocessor constants, type checking is minimal. If a register address from one generation is paired with masks from another generation, the code can compile while programming the wrong bits.

## Test signals

Useful validation signals include:

- Build coverage of `smu_v13_0.c` with this header included, proving all token-pasted fields resolve.
- Register read/write traces showing expected values in `regTHM_THERMAL_INT_CTRL`, `regTHM_THERMAL_INT_ENA`, `regCG_FDO_CTRL*`, and `regCG_TACH_CTRL`.
- Thermal interrupt tests that cross high/low thresholds and confirm IH delivery, threshold reprogramming, and clear-bit behavior.
- Fan control tests that set PWM modes and duty cycles and verify tachometer feedback.
- Hardware-monitor readings that compare decoded `CUR_TEMP`, ASIC max temperature, and TMON/DIE valid/temp fields against SMU telemetry.
- Suspend/resume and BACO tests that confirm THM state is reinitialized or preserved according to firmware expectations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_13_0_2_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_14_0_2_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_14_0_2_offset.h

## Purpose

`thm_14_0_2_offset.h` is the generated register-address map for the AMD THM block on SMU/PM firmware generation 14.0.2 hardware. It supplies register offsets and base-index constants, while `thm_14_0_2_sh_mask.h` supplies the matching field masks and shifts. The address block comment identifies `thm_thm_SmuThmDec` with base address `0x59800`; the exported `reg...` values are offsets relative to the THM block as used by the SOC15 register access macros.

The header is included by `drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0.c`. In that integration, callers access registers such as `regTHM_THERMAL_INT_CTRL` through `RREG32_SOC15(THM, 0, reg...)` and `WREG32_SOC15(THM, 0, reg..., value)`.

## Important APIs, types, and constants

The interface consists of `#define` constants only:

- `regNAME` gives the register offset.
- `regNAME_BASE_IDX` gives the SOC15 base index, always `0` in this file.
- The include guard is `_thm_14_0_2_OFFSET_HEADER`.

The THM register window starts with thermal and cooling controls:

- `regTHM_TCON_CUR_TMP` through `regTHM_THERMAL_INT_STATUS` cover current temperature, HTC, thermal trip, CTF delay, GPIO controls, and thermal interrupt state.
- `regTHM_SW_TEMP`, `regCG_MULT_THERMAL_CTRL`, `regCG_MULT_THERMAL_STATUS`, and `regCG_THERMAL_RANGE` cover software temperature and range/status controls.
- `regCG_FDO_CTRL0/1/2`, `regCG_TACH_CTRL`, `regCG_TACH_STATUS`, and `regCG_THERMAL_STATUS` cover fan PWM and tachometer behavior.
- `regCG_PUMP_CTRL0/1/2`, `regCG_PUMP_TACH_CTRL`, `regCG_PUMP_TACH_STATUS`, and `regCG_PUMP_STATUS` cover pump PWM and tachometer behavior.
- `regTHM_TCON_LOCAL2` through `regTHM_TCON_LOCAL15` cover local THM metadata, global min/max IDs, sensor Tj max fields, and boot-done state.
- `regTHM_BACO_CNTL`, `regTHM_BACO_TIMING0/1/2`, and `regTHM_BACO_TIMING` cover bus-active/chip-off related timing and control registers.
- `regXTAL_CNTL` and `regTHM_PWRMGT` cover clock/reference and THM power-management controls.

The sideband-management region starts later at offsets `0x0158` through `0x018c`:

- `regSMUSBI_*` covers SBI address/data/control/timing and SMBus pad/alert registers.
- `regSBTSI_REMOTE_TEMP` exposes a remote temperature sensor register.
- `regSBRMI_*` exposes command, write-data, read-data, core-enable, APIC, and MCE status registers.
- `regSMBUS_*` exposes SMBus command enables, timing, trigger, UDID, BACO dummy, and address-range registers.

This file has 228 lines and is small enough to audit directly. It defines addresses but no bit semantics; consumers need the matching sh/mask file for field-level programming.

## Control flow

The header has no executable control flow. It controls hardware access routing by naming the register offsets used in SMU v14 code. In `smu_v14_0.c`, representative direct uses include:

- Reading `regTHM_THERMAL_INT_CTRL` before masking or programming thermal interrupts.
- Writing `regTHM_THERMAL_INT_CTRL` after setting `DIG_THERM_INTH`, `DIG_THERM_INTL`, `MAX_IH_CREDIT`, and mask bits from the sh/mask header.
- Writing `regTHM_THERMAL_INT_ENA` to clear or disable high/low/trigger thermal interrupt bits.

For those flows, this offset header selects which THM register is accessed, while `thm_14_0_2_sh_mask.h` selects which bits inside that register are changed. A correct offset but wrong mask still misprograms a register; a wrong offset with correct masks writes the right bit pattern into the wrong hardware register.

## State and persistence behavior

This header stores no state. The state addressed by its constants is hardware register state in the THM block and associated sideband controllers. That state can include live temperature readings, interrupt masks and pending bits, fan/pump control programming, BACO timing/control, SMBus/SBRMI command state, and clock-gating state.

Persistence follows hardware rules. Some registers hold configuration until reset or power-management transitions; others are live status registers or write-one-to-clear command/status registers. The base-index constants being all `0` indicates this generated view expects a single THM instance under the selected SOC15 THM hardware block for this IP version.

## Dependencies and integration points

The key dependencies are:

- `thm_14_0_2_sh_mask.h`, which must be paired with this header for field manipulation.
- `smu_v14_0.c`, which includes both generated THM headers.
- AMDGPU SOC15 register IO helpers that interpret the `THM` hardware block, instance number, base index, and register offset.
- SMU firmware and power-management flows that may also own or initialize these registers.

The file also aligns with the broader AMDGPU generated-register convention where offset headers use `reg...` names for newer IP blocks, unlike older `mm...` or `ix...` naming in some other ASIC headers.

## Risks

The highest-risk failure mode is address drift between the header and silicon. Thermal interrupt, fan, pump, BACO, or sideband-management writes would then target the wrong register. Because all values are compile-time constants and many registers are adjacent, such errors may compile cleanly and only surface as thermal, interrupt, suspend/resume, or platform-management failures on hardware.

There is also a pairing risk: this offset header should be used with `thm_14_0_2_sh_mask.h`, not with v13, v15, or older THM mask headers. Similar register names across generations make accidental cross-inclusion plausible in manual changes.

Finally, the sideband region contains registers capable of influencing SMBus, SBRMI, BACO address ranges, and alert pins. Mistakes in these offsets can affect management-bus behavior outside ordinary temperature polling.

## Test signals

Useful signals include:

- Successful build of SMU v14 code with all `reg...` symbols resolved.
- Runtime register tracing showing THM accesses land at the expected offset under base address `0x59800`.
- Thermal high/low interrupt tests that verify writes to `regTHM_THERMAL_INT_CTRL` and `regTHM_THERMAL_INT_ENA` have the expected effect.
- Fan/pump and tachometer tests if v14 platform code uses these registers directly or through shared helpers.
- BACO and suspend/resume tests that exercise `regTHM_BACO_*`, `regXTAL_CNTL`, and `regTHM_PWRMGT` state transitions.
- Platform-management tests for SMBus/SBRMI if those registers are touched by firmware or debug paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_14_0_2_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_14_0_2_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_14_0_2_sh_mask.h

## Purpose

`thm_14_0_2_sh_mask.h` is the generated bitfield-layout companion for `thm_14_0_2_offset.h`. It defines the masks and shifts for THM register fields on AMDGPU SMU/PM firmware generation 14.0.2 hardware. The file is included by `drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0.c`, where its constants drive thermal interrupt programming through `REG_SET_FIELD`, `REG_GET_FIELD`, and direct bit operations.

This header is not a driver by itself. Its purpose is to encode the hardware contract between AMDGPU software and the THM register block: current-temperature fields, interrupt fields, GPIO pad controls, fan/pump fields, local thermal state, BACO fields, clock/power controls, and sideband-management register fields.

## Important APIs, types, and constants

The file exports macro constants only:

- `REGISTER__FIELD__SHIFT` is the field shift.
- `REGISTER__FIELD_MASK` is the full 32-bit mask.
- The include guard is `_thm_14_0_2_SH_MASK_HEADER`.

Important groups include:

- `THM_TCON_CUR_TMP`: current-temperature and slew-selection fields. v14 includes `REMOTE_TJ_SEL` at bits 14:13, which is not present in the v13.0.2 mask from this work item. `CUR_TEMP` remains a high-bit field with mask `0xFFE00000`.
- `THM_TCON_HTC`: HTC enable, internal/external PROCHOT, active/log bits, interrupt routing to IH, PROCHOT event source, temperature limit, hysteresis, and slew selection.
- `THM_TCON_THERM_TRIP` and `THM_CTF_DELAY`: thermal-trip polarity/status/enable/limit/software-trip and CTF delay count fields. Compared with the v13 mask, this v14 file does not expose the large `RSVD3` field in the visible thermal trip layout.
- `THM_GPIO_PROCHOT_CTRL`, `THM_GPIO_THERMTRIP_CTRL`, `THM_GPIO_PWM_CTRL`, `THM_GPIO_TACHIN_CTRL`, `THM_GPIO_PUMPOUT_CTRL`, and `THM_GPIO_PUMPIN_CTRL`: uniform GPIO pad control fields.
- `THM_THERMAL_INT_ENA`, `THM_THERMAL_INT_CTRL`, and `THM_THERMAL_INT_STATUS`: set/clear/status bits, high/low thresholds, trigger/PROCHOT masks, IH hardware enable, and interrupt credit fields.
- `THM_SW_TEMP`, `CG_MULT_THERMAL_CTRL`, `CG_MULT_THERMAL_STATUS`, and `CG_THERMAL_RANGE`: software temperature and aggregate thermal range/status.
- `CG_FDO_*`, `CG_TACH_*`, `CG_THERMAL_STATUS`, `CG_PUMP_*`, `CG_PUMP_TACH_*`, and `CG_PUMP_STATUS`: fan and pump PWM/tachometer layouts.
- `THM_TCON_LOCAL2` through `THM_TCON_LOCAL15`: local temperature-controller metadata, global min/max, IDs, boot-done, and TSEN-specific Tj max fields. v14 adds `use_tsen_for_temp_sel` and `use_tro_for_temp_sel` fields in `THM_TCON_LOCAL2` compared with the v13.0.2 file.
- `THM_BACO_CNTL` and `THM_BACO_TIMING*`: BACO mode, isolation, reset, clock/refclock, exit, scratch/fence, idle, and timing count fields.
- `XTAL_CNTL` and `THM_PWRMGT`: reference-clock and clock-gating controls, including `DBG_CLK_GATE_EN`.
- `SMUSBI_*`, `SBTSI_REMOTE_TEMP`, `SBRMI_*`, and `SMBUS_*`: sideband interface, remote temperature, command/data/status, SMBus timing, trigger, UDID, pad, alert, BACO dummy, and BACO address-range fields.

The file has 813 `#define` lines and 940 total lines. It is narrower than the v13 mask in this work item because it does not include the large TMON RDIL/RDIR sensor arrays, but it includes v14 BACO, SMUSBI pad/alert, and SMBus BACO address range fields that line up with the v14 offset file.

## Control flow

The header has no functions, branches, or runtime execution. It shapes the behavior of SMU v14 code at compile time by providing field names for the register-helper macros. In `smu_v14_0.c`, direct uses include:

- Masking thermal interrupts by setting `THM_THERMAL_INT_CTRL.THERM_INTH_MASK` and `THERM_INTL_MASK`.
- Enabling thermal interrupt delivery by setting `MAX_IH_CREDIT`, `THERM_IH_HW_ENA`, clearing high/low masks, and programming `DIG_THERM_INTH`/`DIG_THERM_INTL`.
- Clearing pending thermal interrupt bits by shifting `1` by `THM_THERMAL_INT_ENA__THERM_INTH_CLR__SHIFT`, `THERM_INTL_CLR__SHIFT`, and `THERM_TRIGGER_CLR__SHIFT`.
- Handling thermal events by updating the relevant threshold field and clearing `THM_THERMAL_INT_CTRL__THERM_TRIGGER_MASK_MASK`.

The fan, pump, BACO, GPIO, and sideband constants are available to any v14 code or shared helper that includes this header, even if not all are used directly in the current `smu_v14_0.c` paths inspected for this work item.

## State and persistence behavior

No software state is stored in this header. The defined fields describe hardware state. That state includes live thermal readings, programmed thresholds, pending interrupt bits, fan/pump PWM settings, BACO control/timing, clock-gating status, remote temperature status, sideband command completion, SMBus timing, and pad/alert state.

Persistence is hardware dependent. Thermal status and current-temperature fields are live or latched by the THM hardware. Interrupt enable/clear bits often have write-one or set/clear semantics. BACO, clock-gate, SMBus, and fan/pump control fields persist as register programming until reset, firmware reinitialization, suspend/resume, BACO transition, or another driver/firmware writer changes them. Because SMU firmware participates in platform thermal and power management, direct software writes must be coordinated with firmware expectations.

## Dependencies and integration points

Primary integration points are:

- `thm_14_0_2_offset.h`, which provides the `reg...` register offsets for these fields.
- `smu_v14_0.c`, which includes the v14 THM offset and mask headers.
- AMDGPU SOC15 register helpers and field helper macros.
- AMDGPU interrupt handling for thermal high-to-low and low-to-high threshold events.
- SMU firmware, BACO, fan, pump, and platform-management paths that may own or rely on these THM fields.

The file must remain synchronized with AMD hardware specifications and with generated headers for related blocks such as MP1. It is part of a larger generated-register surface rather than a hand-maintained abstraction layer.

## Risks

The main risk is incorrect field layout for a targeted ASIC revision. Thermal interrupt fields are especially sensitive: wrong masks can disable critical thermal notifications, fail to clear pending events, or set thresholds in the wrong bit positions. Fan and pump masks can change cooling behavior. BACO timing/control masks can affect low-power entry/exit. SMBus/SBRMI fields can affect sideband management communication and alert behavior.

Cross-generation drift is also important. This v14 header is similar to v13 and v15 THM headers but not identical. `REMOTE_TJ_SEL`, TSEN/TRO selection, BACO fields, and reserved thermal-trip ranges differ. Reusing the wrong generation's masks can compile cleanly while producing wrong hardware programming.

Because these constants are macros, there is no runtime validation that a `reg...` offset and field macro belong to the same generation. Code review and generated-header provenance are therefore important safeguards.

## Test signals

Useful validation signals include:

- Compile coverage of `smu_v14_0.c` and any platform-specific v14 code that token-pastes these field names.
- Hardware traces confirming writes to `regTHM_THERMAL_INT_CTRL` manipulate only the expected high/low threshold, mask, IH enable, and credit bits.
- Thermal interrupt tests that confirm high/low threshold crossings produce expected IH events and that clear bits work.
- Fan/pump tests where supported, verifying duty settings, PWM modes, tach target/status, and status readback.
- BACO and suspend/resume tests covering `THM_BACO_*`, `XTAL_CNTL`, and `THM_PWRMGT` behavior.
- Sideband-management validation for SBRMI/SBTSI/SMBus command, timing, alert, and address-range fields if the platform exercises those paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_14_0_2_sh_mask.h -->
