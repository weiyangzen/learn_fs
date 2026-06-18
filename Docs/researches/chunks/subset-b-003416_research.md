# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_2_sh_mask.h lines 1-4517

## Scope

This chunk covers the first 4,517 lines of the generated AMD SMU 7.1.2 shift/mask header. The range starts with the file license and include guard, then defines C preprocessor constants for SMU/SMC register fields through the start of `THM_TMON1_RDIL5_DATA`. The file is not executable driver logic; it is a hardware ABI description used by AMDGPU and power-management code to extract and compose bitfields in SMU, clock, power, fuse, DPM, memory timing, fan, and thermal registers.

Each register field follows the AMD generated naming pattern:

- `<REGISTER>__<FIELD>_MASK` gives the field bitmask in the raw 32-bit register value.
- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit for shifting values into or out of the mask.

The companion register-address header, `smu_7_1_2_d.h`, supplies register offsets. This header supplies only field layout.

## Purpose

The purpose of this chunk is to preserve exact bit positions for SMU 7.1.2 hardware programming. Consumers use these constants with AMDGPU register helpers, indirect SMC/SMU accessors, and power-management table loaders to:

- Program GPU and media clocks, dividers, PLL bypass, spread spectrum, and clock-pin controls.
- Exchange messages with SMC/SMU firmware through mailbox, response, and argument registers.
- Decode boot, fuse, feature-status, current-limit, and firmware status fields.
- Pack and unpack firmware DPM table words for graphics, memory, PCIe, voltage, BAPM, SMIO, clock stretching, boot levels, and thermal policy.
- Describe memory-controller timing tables, MC register save/restore tables, fan-control tables, soft registers, and PM status slots.
- Configure thermal interrupts, fan PWM/tachometer controls, and thermal monitor calibration/readout fields.

Because the constants mirror hardware layout, the file is part of the driver/hardware contract. Seemingly small changes to a mask or shift can silently corrupt adjacent hardware fields.

## Important Macro Families

### Clock, PLL, and Bypass Fields

The opening block defines field layout for clock control and PLL programming:

- `CG_DCLK_CNTL`, `CG_VCLK_CNTL`, `CG_ECLK_CNTL`, and `CG_ACLK_CNTL` expose divider fields plus direct-control enable/toggle/divider fields. Matching status registers report current status and done-toggle bits for DCLK, VCLK, and ECLK.
- `GCK_DFS_BYPASS_CNTL` and `GCK_ADFS_CLK_BYPASS_CNTL1` map bypass controls for ECLK, LCLK, EVCLK, DCLK, VCLK, DISPCLK, DPREFCLK/DRREFCLK, ACLK, ADIVCLK, PSPCLK, SAMCLK, and SCLK.
- `CG_SPLL_FUNC_CNTL` through `_7`, `CG_SPLL_STATUS`, `SPLL_CNTL_MODE`, and `CG_SPLL_SPREAD_SPECTRUM(_2)` define SPLL reset, power, divider, bypass, mux, feedback divider, spread-spectrum, test, lock, and update controls.
- `MPLL_BYPASSCLK_SEL`, `CG_CLKPIN_CNTL`, `CG_CLKPIN_CNTL_2`, `CG_CLKPIN_CNTL_DC`, `THM_CLK_CNTL`, `MISC_CLK_CTRL`, `GCK_PLL_TEST_CNTL`, and `GCK_PLL_TEST_CNTL_2` describe clock source selection, crystal/oscillator paths, thermal monitor clocking, deep-sleep/ZCLK selection, and PLL test counters.

These macros are integration points for display/video clock setup, SCLK transitions, boot/power-state changes, BACO sequences, and diagnostic PLL testing.

### Indirect SMU/SMC Access and Mailboxes

The file defines several indexed access windows:

- `GCK_SMC_IND_INDEX`/`GCK_SMC_IND_DATA`.
- `SMC_IND_INDEX`/`SMC_IND_DATA` plus numbered windows 0 through 7.
- `SMU_IND_INDEX_0`/`SMU_IND_DATA_0` through numbered windows 7.
- `SMU_SMC_IND_INDEX`/`SMU_SMC_IND_DATA`.
- `SMC_IND_ACCESS_CNTL` auto-increment bits for indirect windows 0 through 15.

The mailbox families `SMC_MESSAGE_0` through `SMC_MESSAGE_11`, `SMC_RESP_0` through `SMC_RESP_11`, and `SMC_MSG_ARG_0` through `SMC_MSG_ARG_11` describe command, response, and argument fields used for host-to-SMC communication. `SMC_SYSCON_*`, `SMC_PC_C`, and `SMC_SCRATCH9` expose reset, clock gating, wake-on-IRQ, DMA-outstanding, PC, and scratch-value fields around the SMC system-controller block.

### GPIO, Reset, Events, and Fuse Fields

The GPIO section describes register fields for software interrupt status, drive strength, masks, output/input values, enables, pin straps, interrupt enable/status/acknowledge/type/polarity, external trigger controls, receiver selection, and pull-up/pull-down state. Most GPIO fields are full-width or bit-per-pin masks; interrupt acknowledgement fields are individually enumerated.

The RCU and fuse block includes:

- `RCU_UC_EVENTS`, `RCU_MISC_CTRL`, and `RCU_VIRT_RESET_REQ` for boot sequence, reset mode, breakpoints, interrupt enablement, driver reset behavior, virtual-function reset request bits, and PF reset request.
- `CC_RCU_FUSES`, `CC_SMU_MISC_FUSES`, `CC_SCLK_VID_FUSES`, `CC_GIO_IOCCFG_FUSES`, `CC_GIO_IOC_FUSES`, `CC_SMU_TST_EFUSE1_MISC`, `CC_TST_ID_STRAPS`, `CC_FCTRL_FUSES`, and `CC_HARVEST_FUSES` for SKU/harvest state, disable bits, debug/fuse-read restrictions, PCIe/init limitations, device and revision ID straps, voltage IDs, and block-disable fuses for VCE/UVD/ACP/DC and related units.

These fields are read by platform bring-up and feature-discovery paths, and some fields gate whether later power-management features should be enabled.

### Firmware, Feature, Power, and Status Fields

The chunk defines top-level SMU status and control metadata:

- `SMU_MAIN_PLL_OP_FREQ`, `SMU_STATUS`, `SMU_FIRMWARE`, `SMU_INPUT_DATA`, `SMU_EFUSE_0`, and `FIRMWARE_FLAGS` describe firmware load state, SMU completion/pass flags, SRAM read/write block state, firmware mode/select bits, auto-start, efuse data, and firmware interrupt/test flags.
- `TDC_STATUS`, `TDC_MV_AVERAGE`, and `TDC_VRM_LIMIT` expose current-limit/current-average status for VDD/VDDC boost, throttle, IDD, and IDDC.
- `FEATURE_STATUS` packs enable and forced-state bits for SCLK, MCLK, LCLK, UVD, VCE, ACP, SAMU, PCIe, BAPM, LPMX, NBDPM, LHTC, VPC, voltage controller, TDC limit, GPU CAC, AVS, and SPMI.
- `ENTITY_TEMPERATURES_1` provides a full-width GPU temperature field.

These fields are common diagnostic signals for confirming firmware boot, DPM feature enablement, current limiting, and thermal/power-management availability.

### DPM Table Layout

`DPM_TABLE_1` through `DPM_TABLE_490` dominate the middle of this chunk. They describe the packed 32-bit words of the SMU powerplay/DPM table rather than ordinary MMIO control registers. The table includes:

- Graphics, memory, and link PID controller parameters, including integrator coefficients, windup limits, precision fields, maximum state, and state-shift values.
- System flags, VR configuration, SMIO masks, SMIO voltage-pattern tables, voltage-level counts, VDDC/VDDGFX/VDDCI/MVDD tables, SIDD/BAPM VID data, and BAPM temperature/current model coefficients.
- Graphics DPM levels 0 through 7, with minimum voltage fields, SCLK frequency, activity level, deep-sleep divider, PCIe DPM level, SPLL programming words, spread-spectrum words, dynamic power registers, throttle/activity enables, display watermark, SCLK DID, power throttle, and hysteresis fields.
- Memory ACPI and memory levels 0 through 3, with MCLK frequency, MVDD, stutter/RTT/EDC controls, activity/throttle enables, strobe controls, hysteresis, display watermark, MPLL programming words, MCLK power-management controls, DLL controls, and spread-spectrum fields.
- PCIe link levels 0 through 7, with SPC, activity enable, lane count, generation speed, up/down thresholds, and reserved words.
- UVD, VCE, ACP, and SAMU clock/voltage levels and boot-level selectors.
- Thermal, voltage, PCIe generation, boot voltage, TDP, FPS threshold, clock stretcher, SMIO array, BAPM, DTE, GPIO, SVI2 enable, phase/voltage response, and low-SCLK interrupt fields.

The DPM table definitions form a packed firmware data contract. Consumers must use the exact field masks when filling or decoding table words; the header does not describe validation ranges or unit conversions.

### Memory Timing, MC Register, Fan, Soft Register, and PM Status Tables

The chunk continues with generated table layouts for SMU-managed memory and telemetry data:

- `MCARB_DRAM_TIMING_TABLE_1` through `_96` encode a matrix of memory-arbiter DRAM timing entries. Each entry carries `McArbDramTiming`, `McArbDramTiming2`, and a byte-sized `McArbBurstTime` with padding.
- `MC_REGISTERS_TABLE_1` through `_81` describe memory-controller register save/restore table entries, including register addresses, value fields, and sequence metadata.
- `FAN_TABLE_1` through `_9` encode fan-control state such as temperature/duty/PWM parameters and related fan policy values.
- `SOFT_REGISTERS_TABLE_1` through `_30` expose firmware soft-register values, including packed table entries for fields not mapped to direct hardware registers in this chunk.
- `PM_FUSES_1` through `_15` describe packed power-management fuse data.
- `SMU_PM_STATUS_0` through `_127` provide full-width `DATA` slots for SMU power-management status reporting.

These tables are typically consumed as firmware-visible structures. Layout correctness matters across suspend/resume, firmware initialization, DPM table uploads, and debug/status dumps.

### Thermal, Fan, Tachometer, and TMON Fields

Lines 4151-4517 define thermal interrupt and fan-control registers plus the start of thermal monitor readout tables:

- `CG_THERMAL_INT_ENA`, `CG_THERMAL_INT_CTRL`, `CG_THERMAL_INT_STATUS`, `CG_THERMAL_CTRL`, `CG_THERMAL_STATUS`, and `CG_THERMAL_INT` describe high/low/critical thermal interrupt enable, mask, threshold, status, event source, CTF pad, DPM threshold, and thermal interrupt fields.
- `CG_MULT_THERMAL_CTRL` and `CG_MULT_THERMAL_STATUS` select and report multi-sensor thermal values, including ASIC max temperature and CTF temperature.
- `CG_FDO_CTRL0`, `CG_FDO_CTRL1`, `CG_FDO_CTRL2`, `CG_TACH_CTRL`, and `CG_TACH_STATUS` define fan PWM duty, spin-up, hysteresis, ramping, min/max temperature and duty, power-down, tachometer edge count, target period, and measured tach period.
- `CC_THM_STRAPS0` captures thermal monitor strap/fuse settings for bandgap adjustment, acquisition count, clock source, source selection, CTF disable, and per-TMON disable bits.
- `THM_TMON0_RDIL*`, `THM_TMON0_RDIR*`, and the start of `THM_TMON1_RDIL*` define thermal monitor sample/calibration data fields: `Z`, `VALID`, and `TEMP`.

The range ends after `THM_TMON1_RDIL5_DATA__Z_MASK`, so the remainder of `THM_TMON1_RDIL5_DATA` and later TMON fields are outside this chunk.

## Important APIs, Types, and Functions

This header defines no functions, no C types, no inline helpers, and no software objects. Its exported interface is the set of preprocessor macros. Important consumer-side APIs are outside the file and include AMDGPU/DRM register access helpers and power-management table code, such as:

- Field extraction/composition helpers like `REG_GET_FIELD`, `REG_SET_FIELD`, and related AMDGPU macro patterns.
- MMIO and indexed access helpers used with companion register offset macros.
- Powerplay and legacy DPM code that packs table entries or emits read-modify-write command tables.
- BACO and media-block code that uses SPLL and indirect SMC fields for low-power entry/exit and block bring-up.

Searches in the tree show direct inclusion in powerplay BACO/SMU manager paths and media blocks, and direct uses of SPLL fields in legacy DPM and BACO command sequences. That confirms this header is part of runtime hardware programming, not merely documentation.

## Control Flow

There is no executable control flow in this chunk. Runtime flow is implied by consumers:

1. Select a register address from the matching SMU 7.1.2 address header or an indexed SMC/SMU address.
2. Read a 32-bit value through MMIO or indirect-index/data registers.
3. Extract fields with the `*_MASK` and `*__SHIFT` constants, or clear/set fields by read-modify-write.
4. For firmware table data, pack several logical fields into one 32-bit table word before uploading or handing the table to SMU firmware.
5. Poll status bits, response registers, thermal interrupt status, or PM status slots as required by the hardware sequence.

For SMC messages, the implied sequence is to write arguments, clear or observe a response slot, write a message field, then poll the corresponding response field. For clock and PLL transitions, the implied sequence is to program divider/bypass/update bits and poll status/acknowledgement bits. For fan/thermal controls, consumers program thresholds, masks, PWM/tach fields, then inspect status and interrupt-detect bits.

## State and Persistence Behavior

The header itself stores no state. All state described here lives in hardware registers or SMU firmware-visible tables.

State classes include:

- Clock and PLL programming state: divider values, bypass bits, mux selections, update bits, spread-spectrum values, and lock/test status.
- SMC/SMU communication state: mailbox message, response, argument, indirect access, auto-increment, scratch, PC, reset, and clock-gating fields.
- GPIO and interrupt state: pin masks, output/input/enables, strap samples, interrupt status/acknowledge/type/polarity, and external trigger controls.
- Fuse and strap state: hardware-derived capability, disable, device-ID, voltage-ID, harvest, and debug/fuse-access policy fields.
- Firmware and DPM state: uploaded or firmware-owned power tables, feature-enable flags, current-limit status, boot levels, and PM status slots.
- Memory timing and MC register table state: firmware table data used to program memory-controller timing and save/restore sequences.
- Fan and thermal state: PWM/tachometer settings, thresholds, interrupt enables/status, TMON calibration/sample data, and thermal monitor strap controls.

Persistence is determined by the ASIC reset domain, firmware behavior, BACO/suspend/resume flow, and driver save/restore paths. The masks do not encode whether a field is sticky, write-one-to-clear, read-only, reset-on-read, or volatile. Consumers must rely on the hardware programming guide and existing AMDGPU sequencing for clearing status bits and restoring state after reset or resume.

## Dependencies and Integration Points

This chunk depends on the generated AMD ASIC register-header ecosystem:

- Companion SMU 7.1.2 offset definitions provide register addresses.
- AMDGPU register access helpers perform MMIO, indexed SMC/SMU access, and field extraction/composition.
- Powerplay and legacy DPM managers consume the DPM, clock, SPLL, voltage, fan, and thermal definitions.
- BACO entry/exit command tables use indirect SMC data plus SPLL masks to bypass, reset, or power down PLL-related state.
- UVD/VCE and other media paths include this header when programming clock/power fields for SMU 7-generation ASICs.
- Platform firmware and SMU firmware share the packed DPM, soft-register, fuse, PM status, and thermal-monitor table layout.

Because this path is under `drivers/gpu/drm/amd/include/asic_reg/smu`, the file should remain source-tree-aligned with other generated SMU headers. Final merged research should preserve the distinction between this `_sh_mask.h` field-layout header and the companion `_d.h` register-address header.

## Risks

- Bitfield drift: a wrong mask or shift can program the wrong clock divider, SPLL bit, voltage table value, thermal threshold, or firmware table field.
- Packed-table corruption: DPM, memory timing, MC register, fan, soft-register, and PM fuse tables pack multiple logical values into one 32-bit word. Incorrect masks can clobber adjacent fields.
- Hardware sequencing hazards: SPLL reset, bypass, power, and update bits are sequence-sensitive. Using the right field with the wrong timing can hang clocks or break low-power transitions.
- Mailbox protocol errors: SMC message, response, and argument fields are raw hardware mailboxes. Clearing or polling the wrong response slot can deadlock a command path or misinterpret firmware failure.
- Ambiguous access semantics: the header does not say which fields are read-only, sticky, write-one-to-clear, volatile, or firmware-owned. Treating status fields as ordinary writable values is unsafe.
- SKU and fuse misinterpretation: fuse/harvest fields gate hardware availability. Misdecoding disable bits can enable blocks that are fused off or hide functional blocks.
- Thermal/fan misconfiguration: threshold, PWM, tachometer, and CTF controls can affect thermal safety and acoustic behavior. Incorrect programming can suppress thermal alerts or drive bad fan duty cycles.
- Cross-generation assumptions: SMU 7.1.2 resembles adjacent SMU 7.x headers, but field positions and table layouts are ASIC-specific. Shared code must include the correct generation header.

## Test Signals

Useful validation signals for consumers of this chunk include:

- Build coverage for AMDGPU configurations that include SMU 7.1.2 powerplay, BACO, media, and legacy DPM paths without missing or conflicting macro definitions.
- Compile-time or unit-style checks that representative `REG_SET_FIELD`/`REG_GET_FIELD` operations round-trip for packed fields such as `FEATURE_STATUS`, `CG_SPLL_FUNC_CNTL`, `DPM_TABLE_*`, `CG_THERMAL_INT_CTRL`, and `CG_FDO_CTRL*`.
- Hardware smoke tests that load SMU firmware, send a mailbox command, and verify response/argument handling through the `SMC_MESSAGE_*`, `SMC_RESP_*`, and `SMC_MSG_ARG_*` fields.
- DPM validation that verifies expected SCLK/MCLK/PCIe levels, boot levels, voltage tables, and feature-status bits after table upload.
- BACO and suspend/resume tests that confirm SPLL bypass/reset/power fields and indirect SMC register accesses leave clocks and firmware communication usable after entry/exit.
- Thermal tests that exercise high/low/critical thresholds, interrupt status, fan PWM duty, tachometer period, and TMON valid/temperature fields.
- Fuse/harvest diagnostics that compare decoded disable and strap fields against expected SKU capabilities.
- GPU reset and resume tests that verify firmware status, DPM tables, PM status slots, memory timing tables, fan state, and thermal interrupts are restored or reinitialized according to driver policy.
