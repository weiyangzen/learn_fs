# Research: subset-b-003404

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_6_0_d.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_6_0_d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_6_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_6_0_sh_mask.h

## Purpose

`smu_6_0_sh_mask.h` is the SMU 6.0 field-layout companion to `smu_6_0_d.h`. It exports generated bit masks and shift values for Southern Islands SMU, clock, thermal, GPIO, power-management, LCAC/CAC, and SMC indirect/mailbox registers. It has no executable code; its role is to let consumers compose and decode register values safely by symbolic field names.

The include guard is `SMU_6_0_SH_MASK_H`. The generated naming convention is:

- `REGISTER__FIELD_MASK` is the bit mask already positioned in the 32-bit register value.
- `REGISTER__FIELD__SHIFT` is the shift amount for encoding or decoding the field.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or variables. The macro namespace is the API.

Important groups include:

- Clock-gating and timer fields: `CG_AT__CG_R/L`, `CG_BSP__BSP/BSU`, `CG_GIT__CG_GICST/CG_GIPOT`, `CG_SSP__SST/SSTU`, `CG_FFCT_0__UTC_0/DTC_0`, and `CG_CAC_CTRL__CAC_WINDOW`.
- Clock pin and display gap fields: `CG_CLKPIN_CNTL__XTALIN_DIVIDE`, `CG_CLKPIN_CNTL__BCLK_AS_XCLK`, `CG_CLKPIN_CNTL_2__FORCE_BIF_REFCLK_EN`, `CG_CLKPIN_CNTL_2__MUX_TCLK_TO_XCLK`, and `CG_DISPLAY_GAP_CNTL__*`.
- SPLL fields: `CG_SPLL_FUNC_CNTL__SPLL_RESET`, `SPLL_SLEEP`, `SPLL_BYPASS_EN`, `SPLL_REF_DIV`, `SPLL_PDIV_A`; `CG_SPLL_FUNC_CNTL_2__SCLK_MUX_SEL`, `SPLL_CTLREQ_CHG`, `SCLK_MUX_UPDATE`; `CG_SPLL_FUNC_CNTL_3__SPLL_FB_DIV`, `SPLL_DITHEN`; `CG_SPLL_STATUS__SPLL_CHG_STATUS`; and spread-spectrum fields `SSEN`, `CLK_S`, and `CLK_V`.
- Thermal/fan fields: `CG_THERMAL_CTRL__DPM_EVENT_SRC/DIG_THERM_DPM`, `CG_THERMAL_STATUS__FDO_PWM_DUTY`, `CG_THERMAL_INT__DIG_THERM_INTH/INTL` and interrupt masks, multi-thermal temperature fields, `CG_FDO_CTRL*`, and `CG_TACH_*`.
- General power and SCLK fields: `GENERAL_PWRMGT__GLOBAL_PWRMGT_EN`, static PM, thermal protection, SMIO index, voltage PM, dynamic spread spectrum, and `SCLK_PWRMGT_CNTL__*` clock-off/light-sleep controls.
- GPIO fields: whole-pad masks for `GPIOPAD_A`, `EN`, `Y`, `MASK`, pull-up/down, receiver select, interrupt enable/polarity/type/status/status-enable, software interrupt bits, pinstrap bits `0..30`, strength fields, and external trigger controls.
- LCAC fields: `LCAC_MC0_*` through `LCAC_MC5_*` enable, threshold, override-select, and override-value fields.
- SMC indirect/mailbox fields: `SMC_IND_ACCESS_CNTL__AUTO_INCREMENT_IND_0..3`, 32-bit data/index fields, `SMC_MESSAGE_*__SMC_MSG`, `SMC_RESP_*__SMC_RESP`, and `SMC_PC_C__smc_pc_c`.
- Thermal monitor indexed data fields: repeated `THM_TMON0_*` and `THM_TMON1_*` definitions for `TEMP`, `VALID`, and `Z` across `INT_DATA`, `RDIL0..15`, and `RDIR0..15`, plus debug fields.

## Control Flow And Data Flow

This header has no runtime control flow. In consumers, the data flow is:

1. Select an address from `smu_6_0_d.h`.
2. Read a register value or initialize a new value.
3. Clear fields with `~REGISTER__FIELD_MASK`.
4. Encode new values with `value << REGISTER__FIELD__SHIFT` and the corresponding mask, or decode by masking and shifting right.
5. Write the final value through the appropriate MMIO or SMC helper.

Concrete flows in this tree include:

- `si_smc.c` uses `SMC_IND_ACCESS_CNTL__AUTO_INCREMENT_IND_0_MASK` to enable auto-increment while streaming SMC firmware words through `mmSMC_IND_DATA_0`, then clears it after the upload. The same field is disabled for single-address SRAM reads/writes.
- `si_dpm.c` decodes `CG_SPLL_FUNC_CNTL__SPLL_PDIV_A`, `CG_SPLL_FUNC_CNTL_3__SPLL_FB_DIV`, and spread-spectrum fields to build an SMC SPLL divider table, then constructs new SPLL register values with the same masks and shifts when calculating SCLK parameters.
- `amdgpu/si.c` uses SPLL bypass/reset/sleep/status and `SPLL_CNTL_MODE__SPLL_SW_DIR_CONTROL` fields in reset recovery and clock bypass logic.
- `amdgpu/cik.c` and related generation-specific code share similarly named field semantics for clock-pin division on later paths, which makes version matching important.

## State And Persistence Behavior

The header itself has no memory or persistent state. It describes fields in persistent hardware registers. State represented by the fields includes:

- Clock and PLL state: reset, sleep, bypass, reference divider, post divider, feedback divider, mux selection/update, change-status, and spread-spectrum controls.
- Power-management state: global/static PM enable, thermal protection mode/masks, voltage PM, SCLK clock-off requests, dynamic light sleep, and ULV/display-gap controls.
- Thermal/fan state: digital thermal thresholds, sensor selections, max/CTF temperature status, fan duty/PWM mode, tach response, tach target period, and tach measured period.
- GPIO state: pad value/output enable/mask, pull states, receiver select, pinstrap readback, interrupt configuration/status/acknowledge, and software-generated interrupt status.
- SMC indirect access state: selected SMC address, auto-increment flags, message registers, response registers, and SMC program-counter capture.
- Thermal monitor sample state: repeated sensor `TEMP`, `VALID`, and raw `Z` values for two monitor blocks.

These fields are part of the driver-to-ASIC ABI. Incorrect masks can preserve, clear, or set the wrong bits and leave the device in a bad state until reset or reprogramming.

## Dependencies And Integration Points

This header depends only on the C preprocessor and is normally included with `smu_6_0_d.h`.

Primary integration points are:

- Southern Islands SMC firmware copy, mailbox, and SRAM helper code in `pm/legacy-dpm/si_smc.c`.
- Southern Islands DPM/SPLL setup in `pm/legacy-dpm/si_dpm.c`.
- SI reset and clock bypass code in `amdgpu/si.c`.
- DCE6 GPIO translation and any GPIO/thermal/fan code that needs SMU 6.0 field layout.
- Common AMDGPU register helpers and generated field-helper idioms.

## Risks And Edge Cases

- Version coupling is critical. The field names mirror SMU 6.0 register layouts and should not be used with SMU 7.x or later address headers unless the consumer has explicitly verified compatibility.
- Generated masks include a few unusual literal forms, for example `CG_SPLL_FUNC_CNTL__SPLL_PDIV_A_MASK 0x007F00000` and `CG_SPLL_SPREAD_SPECTRUM_2__CLK_V_MASK 0x00000200L` with shift `0`. Consumers must trust the generated layout rather than infer width from naming.
- `SMC_IND_ACCESS_CNTL__AUTO_INCREMENT_IND_*` controls affect stateful SMC indirect accesses. Leaving auto-increment enabled after a streaming write can cause later single-register accesses to hit unexpected addresses.
- SPLL fields are used during reset and DPM transitions. Wrong masks or shifts can hang clocks, fail clock-change handshakes, or generate invalid divider tables.
- Thermal and fan fields can affect protection behavior; incorrect writes can mask thermal interrupts or set unsafe fan/PWM behavior.
- Large repeated GPIO and thermal monitor bit definitions invite copy/paste or generation drift. A single off-by-one shift in pinstrap, interrupt ack, or thermal valid/temp fields can make diagnostics misleading.
- Many full-width fields such as SMC data/index/message/response use `0xffffffffL`; consumers need external validation for value range, alignment, and semantics.

## Test Signals

Useful validation signals are:

- Build coverage for SI legacy DPM, SI SMC, SI reset, and DCE6 GPIO paths.
- SMC firmware upload tests that verify auto-increment writes, endian conversion, and subsequent single dword reads/writes.
- SMC mailbox tests that send commands, observe `mmSMC_RESP_0`, and detect timeout regressions.
- SCLK/DPM tests that cover SPLL divider table generation, SCLK switching, spread-spectrum programming, ULV/CAC controls, and suspend/resume.
- GPU reset tests that exercise SPLL bypass, reset, sleep, and change-status polling.
- Thermal/fan telemetry tests for threshold decode, sensor valid bits, PWM duty, tachometer periods, and thermal interrupts.
- GPIO tests for pinstrap readback, interrupt ack/status, pull-up/down, and receiver/strength configuration where hardware exposes those paths.
- Register-generation comparison against AMD's SMU 6.0 database to validate masks and shifts mechanically.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_6_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_0_0_d.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_0_0_d.h -->
