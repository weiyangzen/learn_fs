# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_0_0_d.h

## Purpose

`smu_7_0_0_d.h` is a generated AMDGPU register-address header for the SMU 7.0.0 hardware generation. It exports symbolic offsets for GCK/SMC indirect ports, SMC host message/response/argument mailboxes, SMU system-control and firmware registers, clock/PLL registers, DPM and soft-register tables, LCLK DPM state tables, fuse/PM telemetry registers, package power and BAPM/AVS/HTC controls, PM status banks, and power-management/LCAC registers.

The file contains no executable code. It is a hardware ABI map used by Kaveri/CIK-era AMDGPU power-management and SMC code.

Macro prefixes distinguish register access paths:

- `mm*` macros are direct MMIO offsets, especially SMC/GCK indirect index/data ports and host mailbox registers.
- `ix*` macros are indexed SMC or SMU addresses used with SMC-indexed helpers.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or variables. The exported `#define` constants are the API.

Important groups include:

- `mmGCK_SMC_IND_*` and `mmSMC_IND_*`: indirect index/data ports for GCK/SMC access, including numbered ports `0..7`, access control, and aliases such as `mmSMC_IND_INDEX_0`.
- `mmSMC_MESSAGE_0..11`, `mmSMC_RESP_0..11`, and `mmSMC_MSG_ARG_0..11`: host-to-SMU/SMC message, response, and argument mailboxes. `mmSMC_MSG_ARG_11` is notably mapped at `0x91`, outside the contiguous `0xa4..0xbf` sequence.
- Clock/PLL indexed registers: `ixCG_DCLK_CNTL`, `ixCG_VCLK_CNTL`, `ixCG_ECLK_CNTL`, `ixCG_ACLK_CNTL`, `ixCG_SPLL_FUNC_CNTL*`, `ixSPLL_CNTL_MODE`, spread-spectrum registers, clock-pin controls, thermal/misc clock controls, and PLL test/bypass registers.
- SMC system-control and firmware registers: `ixSMC_SYSCON_RESET_CNTL`, `ixSMC_SYSCON_CLOCK_CNTL_*`, `ixSMC_SYSCON_MISC_CNTL`, `ixSMC_SYSCON_MSG_ARG_0`, `ixSMC_PC_C`, `ixSMC_SCRATCH9`, `ixSMU_STATUS`, `ixSMU_FIRMWARE`, and `ixSMU_INPUT_DATA`.
- Fuse and RCU registers: `ixRCU_*`, `ixCC_*`, `ixSMU_EFUSE_0`, and `ixPM_FUSES_1..65`.
- DPM and soft table ranges: `ixDPM_TABLE_1..191` at 4-byte intervals from `0x3f000` through `0x3f2f8`, and `ixSOFT_REGISTERS_TABLE_1..21` from `0x3f900` through `0x3f950`.
- LCLK DPM controls: `ixSMU_LCLK_DPM_STATE_0..7_CNTL_0..3`, `ixSMU_LCLK_DPM_STATE_0..7_ACTIVITY_THRESHOLD`, `ixGIO_PID_CONTROLLER_CNTL_0..8`, `ixSMU_LCLK_DPM_LEVEL_COUNT`, `ixSMU_LCLK_DPM_CNTL`, current/target state, and thermal-throttling registers.
- PM telemetry/control registers: firmware flags, temperature read addresses, current temperatures, feature status, PM intervals, VPC/display PHY power limits, package/GPU power, BAPM parameters/status, SVI telemetry, HTC/VPC status, entity temperatures, CU/GPU/NTE power, TDC status, AVS/SPMI/PDM controls, and monitor port80 setup.
- PM status bank: `ixSMU_PM_STATUS_0..127` from `0x3fe00` through `0x3fffc`.
- Power-management and LCAC registers: `ixGENERAL_PWRMGT`, `ixCNB_PWRMGT_CNTL`, `ixSCLK_PWRMGT_CNTL`, profile-index registers, frequency transition voting registers, display-gap/ACPI/deep-sleep/ULV registers, and `ixLCAC_SX0_*`, `ixLCAC_MC0..3_*`, `ixLCAC_CPL_*`.

## Control Flow And Data Flow

This header has no control flow. It feeds register-access control flow in consumers:

1. Include `smu_7_0_0_d.h`, often with `smu_7_0_0_sh_mask.h`.
2. For direct host mailboxes, write a message or argument to `mmSMC_MESSAGE_*` or `mmSMC_MSG_ARG_*`, then poll `mmSMC_RESP_*`.
3. For indexed SMC/SMU state, use `RREG32_SMC(ix...)` or `WREG32_SMC(ix..., value)`, which drive the SMC indirect index/data path.
4. For table uploads or table reads, access the generated table address range one dword at a time or through higher-level SMC SRAM/table helpers.

Concrete flows in this tree include:

- `pm/legacy-dpm/kv_smc.c` writes `mmSMC_MESSAGE_0`, polls `mmSMC_RESP_0`, writes parameters to `mmSMC_MSG_ARG_0`, reads `ixSMC_SYSCON_MSG_ARG_0`, and uses `mmSMC_IND_INDEX_0`, `mmSMC_IND_DATA_0`, and `mmSMC_IND_ACCESS_CNTL` for SMC SRAM access.
- `pm/legacy-dpm/kv_dpm.c` starts DPM by setting `GENERAL_PWRMGT__GLOBAL_PWRMGT_EN_MASK` in `ixGENERAL_PWRMGT`, then sends SMC DPM enable/disable messages.
- `amdgpu/cik.c` reads `ixGENERAL_PWRMGT` on APUs and `ixCG_CLKPIN_CNTL` on discrete paths to compute the reference clock division.
- PowerPlay SMU managers for CI/SMU7 write `mmSMC_MESSAGE_0` to notify firmware, using the same direct mailbox concept.

## State And Persistence Behavior

The header stores no software state. It describes stateful SMU/SMC registers and firmware-owned tables whose contents persist until firmware, driver, reset, or power transitions change them.

Represented state includes:

- SMC indirect access state: selected index address, data windows, and auto-increment control.
- Host firmware command state: message, response, and argument mailboxes.
- Clock and PLL state for DCLK, VCLK, ECLK, ACLK, SPLL, clock pins, spread spectrum, DFS bypass, and test controls.
- Firmware execution/system state: SMC reset, clock control, misc control, program counter, scratch, firmware/status/input data, and RCU event/misc state.
- DPM table state, soft-register table state, LCLK DPM levels, activity thresholds, PID controller configuration, level count, current/target state, and thermal throttling.
- Fuse and calibration state read from CC/PM/SMU fuse windows.
- Runtime telemetry and policy state for temperatures, package/GPU power, BAPM, SVI, HTC, VPC, AVS, TDC, SPMI, PDM, and PM status slots.
- General power-management, SCLK, display gap, deep sleep, ULV, voltage status, transition voting, and LCAC state.

The table ranges and status banks are especially sensitive: they represent firmware contracts rather than ordinary driver-local data.

## Dependencies And Integration Points

This file depends only on the preprocessor and is normally paired with `smu_7_0_0_sh_mask.h` for field definitions.

Primary integration points are:

- Kaveri legacy SMC code in `pm/legacy-dpm/kv_smc.c`.
- Kaveri legacy DPM policy/control code in `pm/legacy-dpm/kv_dpm.c`.
- CIK initialization and reference-clock logic in `amdgpu/cik.c`.
- SMU7/CI PowerPlay managers that use compatible mailbox and clock-control register names.
- AMDGPU register helper families for direct MMIO and SMC-indexed register access.

## Risks And Edge Cases

- Version coupling is strict. SMU 7.0.0 table bases and field layouts differ from SMU 6.0 and other 7.x variants. Using this address map with the wrong ASIC can silently access the wrong firmware table or hardware block.
- The SMC mailbox sequence relies on correct message, response, and argument addresses. A wrong macro can cause SMC command timeouts, stale responses, or firmware-side invalid-command errors.
- `mmSMC_MSG_ARG_11` is not contiguous with the other high argument registers. Code that assumes a simple base-plus-index formula instead of symbolic macros can break.
- DPM and PM status table ranges are long generated sequences. Off-by-one table indexes can corrupt adjacent firmware-owned state.
- SMC indirect index/data ports and auto-increment control are stateful. Misprogramming them can make later SRAM/table reads and writes target unintended addresses.
- Power, clock, thermal, AVS, BAPM, HTC, SPMI, and package power registers influence live power-management policy. Bad addresses can destabilize clocks, voltage, throttling, or telemetry.
- Several names have equivalent or near-equivalent aliases (`mmGCK_*`, `mmSMU_*`, `mmSMC*`). Consumers must choose the alias expected by their helper/register aperture, not only by numeric equality.

## Test Signals

Useful validation signals are:

- Build coverage for `kv_smc.c`, `kv_dpm.c`, `amdgpu/cik.c`, and SMU7/CI PowerPlay manager paths.
- Kaveri/SMU7 hardware boot/probe tests that verify SMC firmware responds to `mmSMC_MESSAGE_0` and returns expected `mmSMC_RESP_0` values.
- SMC SRAM/table read/write tests, including unaligned/bounds-negative cases in the caller logic and auto-increment behavior.
- DPM enable/disable, SCLK/LCLK transition, BAPM, AVS, HTC, and suspend/resume tests.
- Reference-clock tests on APU and discrete paths that exercise `ixGENERAL_PWRMGT` and `ixCG_CLKPIN_CNTL`.
- Telemetry checks for temperatures, package/GPU power, TDC, PM status, feature status, and firmware flags.
- Register-generation diff checks against AMD's SMU 7.0.0 source database, especially table ranges and mailbox offsets.
