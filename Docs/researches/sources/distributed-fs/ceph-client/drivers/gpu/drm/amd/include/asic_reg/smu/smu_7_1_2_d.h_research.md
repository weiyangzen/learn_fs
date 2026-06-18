# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_2_d.h

## Purpose

`smu_7_1_2_d.h` is a generated AMDGPU register-address header for the SMU 7.1.2 hardware register set. It exports symbolic offsets for direct MMIO-style registers and indexed SMU address-space registers used by the Radeon/AMDGPU power-management stack, SMC firmware interface, clock generation, thermal/fan control, dynamic power management tables, memory-controller programming tables, power-gating status, and ROM access paths.

The file contains no executable logic. Its ABI value is the mapping from stable C preprocessor names to numeric hardware addresses. The include guard is `SMU_7_1_2_D_H`.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or mutable variables. The public interface is a flat namespace of `#define` constants. Prefixes identify the register access space:

- `mm*` names are memory-mapped register offsets for indirect-index/data windows and mailbox-style SMC registers.
- `ix*` names are indexed-register addresses in SMU, clock, thermal, power, ROM, fuse, and table address spaces.

Important exported groups include:

- `mmGCK*_GCK_SMC_IND_INDEX`, `mmGCK*_GCK_SMC_IND_DATA`, `mmSMC*_SMC_IND_*`, `mmSMU*_SMU_SMC_IND_*`, and `mmROM*_ROM_SMC_IND_*`: replicated indirect index/data apertures. Several aliases point at the same offsets, and the numbered forms expose multiple windows at `0x80`/`0x81`, `0x82`/`0x83`, and later pairs through `0x8f`, with an additional `mmSMC_IND_INDEX_11`/`DATA_11` pair at `0x1ac`/`0x1ad`.
- `mmSMC_MESSAGE_*`, `mmSMC_RESP_*`, and `mmSMC_MSG_ARG_*`: SMC firmware mailbox registers for posting commands, passing arguments, and reading responses across channels 0 through 11.
- `ixCG_*`, `ixGCK_*`, `ixSPLL_*`, `ixMPLL_*`, `ixTHM_CLK_CNTL`, and `ixMISC_CLK_CTRL`: clock-generator controls for DCLK/VCLK/ECLK/ACLK, SPLL setup/status/spread-spectrum, clock pins, DFS bypass, PLL testing, and miscellaneous clock control.
- `ixSMC_SYSCON_*`, `ixSMC_PC_C`, and `ixSMC_SCRATCH9`: SMC microcontroller system, clock, reset, message argument, program-counter, and scratch registers.
- `mmGPIOPAD_*`: GPIO pad state, mask, enable, interrupt status/acknowledge, interrupt type/polarity, trigger, receiver, pull-up, and pull-down controls.
- `ixRCU_*` and `ixCC_*`: reset/control-unit events, virtual reset requests, and configuration/fuse/strap registers.
- `ixSMU_MAIN_PLL_OP_FREQ`, `ixSMU_STATUS`, `ixSMU_FIRMWARE`, `ixSMU_INPUT_DATA`, `ixFIRMWARE_FLAGS`, `ixTDC_*`, `ixFEATURE_STATUS`, and `ixENTITY_TEMPERATURES_1`: SMU status, firmware, telemetry, feature, and temperature-reporting registers.
- `ixDPM_TABLE_1` through `ixDPM_TABLE_490`: a large contiguous dynamic power-management table window from `0x3f000` through `0x3f7a4`.
- `ixMCARB_DRAM_TIMING_TABLE_1` through `ixMCARB_DRAM_TIMING_TABLE_96` and `ixMC_REGISTERS_TABLE_1` through `ixMC_REGISTERS_TABLE_81`: contiguous memory-controller arbitration, DRAM timing, and memory-controller programming tables.
- `ixFAN_TABLE_*`, `ixSOFT_REGISTERS_TABLE_*`, `ixPM_FUSES_*`, and `ixSMU_PM_STATUS_0` through `ixSMU_PM_STATUS_127`: fan tuning data, software-visible SMU table registers, power-management fuses, and a broad PM status block.
- `ixCG_THERMAL_*`, `ixCG_MULT_THERMAL_*`, `ixCG_FDO_*`, `ixCG_TACH_*`, `ixCC_THM_STRAPS0`, `ixTHM_TMON0_*`, and `ixTHM_TMON1_*`: thermal interrupt/control/status, fan-duty/tachometer, thermal straps, and two thermal monitor data/debug/status banks.
- `ixGENERAL_PWRMGT`, `ixCNB_PWRMGT_CNTL`, `ixSCLK_*`, `ixLCLK_*`, `ixCG_FREQ_TRAN_VOTING_*`, `ixCG_DISPLAY_GAP_CNTL*`, `ixCG_ACPI_CNTL`, `ixVDDGFX_IDLE_*`, and `ixPWR_*`: global, SCLK/LCLK, ACPI, display-gap, clock-voting, idle-voltage, and display timer power-management controls.
- `ixLCAC_*`: leakage/current/acoustic-style control and override registers for MC0 through MC3 and CPL domains.
- `ixROM_*`, `ixPAGE_MIRROR_CNTL`, `ixCGTT_ROM_CLK_CTRL0`, and `ixROM_SW_DATA_1` through `ixROM_SW_DATA_64`: ROM control/status/index/data and software-command/data windows.
- `ixCURRENT_PG_STATUS` and `ixCURRENT_PG_STATUS_APU`: current power-gating status addresses for discrete and APU contexts.

## Control Flow And Data Flow

This header has no local control flow. Driver control flow uses these constants as address operands:

1. The SMU or power-management driver selects an address macro, such as an SMC mailbox register, an indexed clock-control register, a DPM table entry, a thermal monitor register, or a ROM command/data register.
2. For `mm*` registers, the driver reads or writes the MMIO offset directly through AMDGPU register helpers. For `ix*` registers, the driver normally programs an appropriate indirect index register and transfers data through the corresponding indirect data register.
3. Field-level values are composed or decoded using matching `*_sh_mask.h` constants or local bit helpers.
4. Higher-level SMU flows use the hardware side effects: send a firmware message and poll a response, update DPM tables, adjust clock/power/thermal parameters, read telemetry, inspect fuses, read ROM data, or query/reset power-gating state.

The mailbox and table groups imply important ordering. For example, SMC messages generally require argument writes before the message write and response polling afterward. Indexed tables require the selected index/address window to match the target register space before data is read or written.

## State And Persistence Behavior

The file stores no software state and performs no persistence. The constants describe stateful hardware registers whose values live in the GPU/SMU until changed by firmware, driver writes, reset, or power transitions.

State represented by these addresses includes:

- SMC command state: message, response, and argument mailboxes.
- SMU firmware and telemetry state: firmware flags, TDC readings/limits, feature status, temperatures, PM status words, and scratch/system registers.
- Clock state: PLL setup, spread spectrum, clock pin controls, DFS bypass, deep-sleep controls, transition voting, and display-gap controls.
- Power-management policy state: DPM table entries, power fuses, soft-register table entries, VDDGFX idle parameters, power-gating status, and LCAC override state.
- Thermal and fan state: thermal interrupts, multi-thermal status, fan duty/tachometer controls, and per-monitor thermal data.
- Memory-controller policy state: DRAM timing, MC register tables, and memory arbiter values.
- ROM state: ROM command/status/index/data and software transfer windows.

Because these addresses are part of the kernel-to-ASIC ABI, an incorrect value can persist as a device misconfiguration until corrected or reset.

## Dependencies And Integration Points

The header depends only on the C preprocessor and can be included without other declarations. It is intended to be paired with compatible SMU 7.1.2 field-mask and enum headers, particularly `smu_7_1_2_sh_mask.h` when field definitions are needed and `smu_7_1_2_enum.h` for mailbox command IDs, tiling/format constants, debug block IDs, and power-control enum values.

Integration points include:

- AMDGPU SMU/PowerPlay code that sends SMC messages, uploads or reads power tables, and controls firmware-managed power features.
- Register helpers that distinguish direct `mm*` offsets from indirect `ix*` indexed addresses.
- Clock and PLL initialization, dynamic clock selection, spread-spectrum, and deep-sleep paths.
- Thermal, fan, tachometer, and hardware thermal-control code.
- DPM, TDP/TDC, load-line, voltage, BAPM, NBDPM, LCLK/SCLK, and display-gap power-management paths.
- Memory-controller timing and register programming coordinated with firmware tables.
- ROM-reading and page-mirror support during device discovery or firmware/VBIOS access.
- Reset, virtual reset, power-gating, and GPIO/strap/fuse discovery paths.

## Risks And Edge Cases

- This is generated hardware ABI data. Manual edits are high risk because consumers rarely validate numeric addresses at compile time.
- `mm*` and `ix*` names use different access paths. Using an indexed address with a direct MMIO helper, or the reverse, can access the wrong register or fail silently.
- Many aliases share the same numeric address. This is intentional for replicated indirect windows and block-specific naming, but code reviewers must verify that a renamed macro still uses the intended aperture.
- The SMC mailbox sequence is order-sensitive. Writing a message before arguments are visible or polling the wrong response register can wedge command processing.
- Large contiguous table ranges invite off-by-one mistakes. `ixDPM_TABLE_*`, `ixMCARB_DRAM_TIMING_TABLE_*`, `ixMC_REGISTERS_TABLE_*`, `ixSMU_PM_STATUS_*`, and `ixROM_SW_DATA_*` must remain aligned and count-correct.
- Power, thermal, fuse, and voltage-related registers can affect hardware stability, throttling, or safety limits. The address header does not encode access permissions or safe value ranges.
- Register semantics such as read-only, write-one-to-clear, latch-on-read, firmware-owned, or reset-only are not visible in this file; consumers must rely on hardware docs and mask headers.
- Version coupling matters. Mixing SMU 7.1.2 addresses with field masks or enums from another generation can silently write valid-looking values to incompatible registers.

## Test Signals

Useful validation signals for changes involving this header are compile-time and hardware-integration focused:

- Build AMDGPU configurations that include SMU 7.1.2 register headers; missing or renamed macros should fail at compile time.
- Diff the generated constants against AMD's canonical SMU 7.1.2 register database or the upstream kernel source used as the import base.
- Boot/probe on matching ASICs and verify SMU firmware load, SMC message/response handshakes, and no mailbox timeouts.
- Exercise DPM and power-management transitions, including SCLK/LCLK changes, voltage/TDP/TDC messages, BAPM/NBDPM configuration, and suspend/resume.
- Validate thermal/fan behavior with temperature telemetry, fan duty/tachometer readings, thermal interrupts, and throttling thresholds.
- Run GPU reset and power-gating tests that read `ixCURRENT_PG_STATUS`/`ixCURRENT_PG_STATUS_APU` and related SMU/RCU status.
- Test ROM access paths that use `ixROM_INDEX`, `ixROM_DATA`, `ixROM_SW_COMMAND`, and the `ixROM_SW_DATA_*` window.
- Run memory-controller and display stability tests after table programming, especially where DPM, DRAM timing, and display-gap registers interact.
