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
