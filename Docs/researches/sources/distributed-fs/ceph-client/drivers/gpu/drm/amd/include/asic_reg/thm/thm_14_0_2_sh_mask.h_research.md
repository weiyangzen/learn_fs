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
