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
