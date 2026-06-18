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
