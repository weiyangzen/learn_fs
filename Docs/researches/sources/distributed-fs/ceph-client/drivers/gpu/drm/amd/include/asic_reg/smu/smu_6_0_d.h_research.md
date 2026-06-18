# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_6_0_d.h

## Purpose

`smu_6_0_d.h` is a generated AMDGPU SMU 6.0 register-address header. It contains no executable logic; it exports symbolic constants for Southern Islands-era SMU, clock, thermal, GPIO, CAC, and SMC mailbox/register windows. Consumers use these constants with AMDGPU MMIO and indexed-SMC access helpers to avoid hard-coded numeric addresses.

The include guard is `SMU_6_0_D_H`. The exported macro namespace follows the AMD register convention:

- `mm*` macros name directly addressed MMIO register offsets, such as `mmCG_SPLL_FUNC_CNTL`, `mmSPLL_CNTL_MODE`, `mmSMC_IND_INDEX_0`, and `mmSMC_MESSAGE_0`.
- `ix*` macros name indexed SMC or thermal-monitor addresses, such as `ixSMC_PC_C`, `ixTHM_TMON0_RDIL0_DATA`, and `ixTHM_TMON1_RDIR15_DATA`.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or data objects. The public API is the set of `#define` register offsets.

Important groups are:

- `ixLCAC_MC0_*` through `ixLCAC_MC5_*`: LCAC memory-controller control, override-select, and override-value indexed registers.
- `mmCG_SPLL_*`, `mmSPLL_CNTL_MODE`, `mmCG_CLKPIN_CNTL*`, `mmTHM_CLK_CNTL`, and `mmMISC_CLK_CNTL`: system PLL, spread-spectrum, clock pin, thermal clock, and miscellaneous clock-control registers.
- `mmCG_THERMAL_*`, `mmCG_MULT_THERMAL_*`, `mmCG_FDO_CTRL*`, `mmCG_TACH_*`: thermal status/interrupt, fan duty/PWM, tachometer, and multi-thermal sensor registers.
- `mmGENERAL_PWRMGT`, `mmSCLK_PWRMGT_CNTL`, `mmTARGET_AND_CURRENT_PROFILE_INDEX`, `mmCG_FTV`, `mmCG_FFCT_0`, `mmCG_BSP`, `mmCG_AT`, `mmCG_GIT`, `mmCG_SSP`, `mmCG_DISPLAY_GAP_CNTL`, `mmCG_ULV_*`, and `mmCG_CAC_CTRL`: legacy power-management, dynamic clocking, display gap, ultra-low-voltage, and CAC controls.
- `ixTHM_TMON0_*` and `ixTHM_TMON1_*`: two thermal monitor banks with debug, interrupt data, and repeated left/right diode data entries `RDIL0..15` and `RDIR0..15`.
- `mmGPIOPAD_*`: GPIO pad strength, mask, data, enable, pinstrap, interrupt, pull-up/down, receiver, and external trigger registers.
- `mmSMC_IND_*`, `mmSMC_MESSAGE_*`, and `mmSMC_RESP_*`: SMC indirect SRAM/register access and host-to-SMC message/response mailboxes.

## Control Flow And Data Flow

This header has no runtime control flow. It participates in driver flows by supplying addresses to register helpers:

1. Driver code includes `smu_6_0_d.h`, usually with `smu_6_0_sh_mask.h`.
2. Code reads or writes a direct register through helpers such as `RREG32(mmCG_SPLL_FUNC_CNTL)` or `WREG32(mmSMC_MESSAGE_0, msg)`.
3. For SMC indexed access, code writes an address to `mmSMC_IND_INDEX_0`, toggles `mmSMC_IND_ACCESS_CNTL`, and transfers data through `mmSMC_IND_DATA_0`.
4. For indexed SMC/thermal addresses, code uses SMC-specific helpers such as `RREG32_SMC(...)` or `WREG32_SMC(...)` with an `ix*` address.

Concrete integration flows in this tree include:

- `pm/legacy-dpm/si_smc.c` sets the SMC SRAM address with `mmSMC_IND_INDEX_0`, controls auto-increment through `mmSMC_IND_ACCESS_CNTL`, copies firmware bytes through `mmSMC_IND_DATA_0`, starts/resets the SMC with `SMC_SYSCON_*` indexed addresses, and sends messages through `mmSMC_MESSAGE_0` while polling `mmSMC_RESP_0`.
- `pm/legacy-dpm/si_dpm.c` calculates and uploads SCLK/SPLL tables by decoding or constructing fields in registers addressed by `mmCG_SPLL_FUNC_CNTL`, `mmCG_SPLL_FUNC_CNTL_3`, `mmCG_SPLL_SPREAD_SPECTRUM`, and related macros.
- `amdgpu/si.c` uses the SPLL addresses during PCI reset/bypass paths to put the clock into bypass, poll `mmCG_SPLL_STATUS`, reset/sleep the SPLL, and manage clock-control mode.
- `display/dc/gpio/dce60/hw_translate_dce60.c` includes the address header for DCE6 GPIO translation against the `mmGPIOPAD_*` namespace.

## State And Persistence Behavior

The header itself stores no state. It describes stateful hardware registers whose contents persist in the device until changed by the driver, SMU firmware, reset, suspend/resume, or power transitions.

State represented by these addresses includes:

- SMC firmware SRAM address/data cursor and message/response mailbox state.
- SPLL, spread-spectrum, clock-pin, SCLK power-management, ULV, and display-gap configuration.
- Thermal monitor readings, valid bits, interrupt thresholds/masks, fan PWM duty, tachometer target/status, and multi-sensor temperature selection/status.
- GPIO pad output/input, interrupt enable/status/acknowledge, pinstrap, pull-up/pull-down, receiver, and strength state.
- LCAC/CAC power-estimation and override state.

Because these are hardware ABI constants, a bad address can leave persistent device state corrupted until a later corrective write or reset.

## Dependencies And Integration Points

This file depends only on the C preprocessor. It is meant to be paired with `smu_6_0_sh_mask.h`, which supplies field masks and shifts for many of the same registers.

Primary integration points are:

- AMDGPU MMIO helpers `RREG32`, `WREG32`, `WREG32_P`, `RREG32_SMC`, and `WREG32_SMC`.
- Southern Islands legacy power management in `pm/legacy-dpm/si_dpm.c`.
- Southern Islands SMC firmware loading, SRAM access, and mailbox messaging in `pm/legacy-dpm/si_smc.c`.
- SI GPU reset/clock bypass paths in `amdgpu/si.c`.
- DCE6 GPIO translation code that needs the SMU/GPIO register namespace.

## Risks And Edge Cases

- Address/mask generation drift is the main risk. The driver generally cannot validate that `mm*` or `ix*` constants target the intended hardware; wrong values can silently write unrelated registers.
- `mmSMC_IND_ACCESS_CNTL` auto-increment control must match the selected data/index port. Incorrect auto-increment can corrupt the wrong SMC SRAM words during firmware upload.
- SMC SRAM access requires 4-byte alignment and limit checks in the consumers. The header exposes raw addresses only, so boundary protection is entirely in caller logic.
- `mmSMC_MESSAGE_*` and `mmSMC_RESP_*` are mailbox registers with polling semantics. A wrong mailbox address or stale response can cause timeouts or false success when sending power-management commands.
- SPLL and power-management registers are used in reset, bypass, and DPM transitions. Incorrect constants can prevent reset recovery, hang clocks, or destabilize display/memory timing.
- Thermal and fan registers influence protection behavior. Mismapped thermal interrupt or fan-duty registers can affect throttling, over-temperature handling, or noisy fan control.
- Some names overlap conceptually with later SMU generations but not necessarily at the same address. Mixing SMU 6.0 address headers with later-generation masks or ASIC paths is unsafe.

## Test Signals

Useful validation signals for changes around this header are:

- Compile coverage for SI/SMU6 paths, especially `si_smc.c`, `si_dpm.c`, `amdgpu/si.c`, and DCE6 GPIO code.
- Boot/probe on Southern Islands hardware with SMC firmware loading enabled; failures often show as SMC SRAM write errors, firmware start failures, or mailbox timeouts.
- DPM enable/disable, SCLK transition, ULV/CAC, and suspend/resume tests that exercise SMC messages and SPLL register programming.
- GPU reset tests that enter clock bypass and SPLL powerdown paths.
- Thermal/fan telemetry tests for sensor validity, interrupt thresholds, fan PWM duty, and tachometer readings.
- Register-database diff checks against AMD's canonical SMU 6.0 definitions to catch accidental address drift.
