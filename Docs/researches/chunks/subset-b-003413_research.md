# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_1_sh_mask.h lines 1-4454

## Scope

This chunk covers the first 4,454 lines of the generated AMD SMU 7.1.1 shift/mask header. It begins with the license, include guard, and low-level clock/PLL register fields, then spans SMC indirect access and message windows, GPIO and reset/control/fuse fields, memory controller timing/register tables, the bulk of the SMU DPM table layout, soft registers, firmware/status tables, thermal/fan controls, power-management controls, frequency-transition voting fields, deep-sleep controls, and the start of display timer control registers through `PWR_DISP_TIMER_5_CONTROL__DISP_TIMER_INT_COUNT`.

The chunk is a C preprocessor register-field map only. It defines constants of the form `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT`; it does not define C functions, structs, storage, locks, allocation, or executable branches.

## Purpose

The purpose of this header section is to encode the bit-level ABI for the SMU 7.1.1 hardware block used by AMDGPU power-management code. The matching SMU register-offset header provides register addresses, while this file provides field locations inside those registers. Runtime code can compose or decode register values with helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, and the AMDGPU MMIO/indirect-register accessors.

The fields in this range are especially sensitive because they describe firmware communication, clock generation, voltage tables, DPM state tables, thermal thresholds, fan output, deep sleep, and power throttling. A bad mask or shift here can make apparently ordinary driver code write the wrong hardware bit.

## Important Macro Families

### Clock, PLL, and Bypass Controls

The opening block maps core clock controls:

- `CG_DCLK_CNTL`, `CG_VCLK_CNTL`, `CG_ECLK_CNTL`, and `CG_ACLK_CNTL` expose divider, direct-control enable, toggle, and direct-control divider fields, with corresponding status registers for DCLK/VCLK/ECLK.
- `GCK_DFS_BYPASS_CNTL` and `GCK_ADFS_CLK_BYPASS_CNTL1` select DFS/ADFS bypass behavior for ECLK, LCLK, EVCLK, DCLK, VCLK, DISPCLK, DPREFCLK/DRREFCLK, ACLK, ADIVCLK, PSPCLK, SAMCLK, and SCLK.
- `CG_SPLL_FUNC_CNTL*`, `SPLL_CNTL_MODE`, `CG_SPLL_SPREAD_SPECTRUM*`, `MPLL_BYPASSCLK_SEL`, `PLL_TEST_CNTL`, `GCK_PLL_TEST_CNTL*`, and `SCLK_MIN_DIV` define SPLL/MPLL reset, power, divider, mux, feedback, spread-spectrum, test, and fractional/integer divider fields.
- `CG_CLKPIN_CNTL*`, `THM_CLK_CNTL`, and `MISC_CLK_CTRL` select crystal, external clock, thermal monitor clock, deep-sleep clock, ZCLK, and DFT clock inputs.

These macros are integration points for ASIC clock programming and DPM transitions. They do not sequence the PLLs themselves; consumers must use the SMU/clock-management programming order required by the hardware.

### SMC and SMU Firmware Communication

The chunk defines multiple indirect and mailbox-style windows:

- `GCK_SMC_IND_INDEX/DATA`, `SMC_IND_INDEX/DATA`, `SMC_IND_INDEX_0..7`, `SMC_IND_DATA_0..7`, `SMU_IND_INDEX_0..7`, `SMU_IND_DATA_0..7`, and `SMU_SMC_IND_INDEX/DATA` provide full-width address/data fields for indirect SMC or SMU register access.
- `SMC_IND_ACCESS_CNTL` exposes auto-increment enables for indirect channels 0 through 15.
- `SMC_MESSAGE_0..11`, `SMC_RESP_0..11`, and `SMC_MSG_ARG_0..11` define 16-bit message/response fields and 32-bit arguments for firmware command exchange.
- `SMC_SYSCON_RESET_CNTL`, `SMC_SYSCON_CLOCK_CNTL_*`, `SMC_SYSCON_MSG_ARG_0`, `SMC_PC_C`, `SMC_SCRATCH9`, `SMU_STATUS`, `SMU_FIRMWARE`, `SMU_INPUT_DATA`, `SMU_EFUSE_0`, and `FIRMWARE_FLAGS` expose reset, clock gating, firmware load/read status, firmware mode/select, input data address/autostart, efuse, interrupt-enabled, and test-count fields.

The implied runtime flow is a mailbox or indirect-access protocol: select an indirect address, read or write the data aperture, optionally use auto-increment for bulk transfers, and coordinate firmware commands through message, argument, and response registers. The header only supplies field packing; it does not encode command IDs, polling rules, timeout values, or ownership arbitration between host driver and SMU firmware.

### GPIO, Interrupt, and Reset/Fuse Fields

GPIO-related macros include `GPIOPAD_SW_INT_STAT`, `GPIOPAD_STRENGTH`, `GPIOPAD_MASK`, `GPIOPAD_A`, `GPIOPAD_EN`, `GPIOPAD_Y`, `GPIOPAD_PINSTRAPS`, `GPIOPAD_INT_STAT_EN`, `GPIOPAD_INT_STAT`, `GPIOPAD_INT_STAT_AK`, `GPIOPAD_INT_EN`, `GPIOPAD_INT_TYPE`, `GPIOPAD_INT_POLARITY`, `GPIOPAD_EXTERN_TRIG_CNTL`, `GPIOPAD_RCVR_SEL`, `GPIOPAD_PU_EN`, and `GPIOPAD_PD_EN`. These cover pad masks, direction/output/input-like values, pinstrap bits 0 through 30, interrupt status/enables/acknowledge/type/polarity, external trigger control, receiver select, and pull-up/pull-down enables.

Reset and fuse families include `RCU_UC_EVENTS`, `RCU_MISC_CTRL`, `CC_RCU_FUSES`, `CC_SMU_MISC_FUSES`, `CC_SCLK_VID_FUSES`, `CC_GIO_IOCCFG_FUSES`, `CC_GIO_IOC_FUSES`, `CC_SMU_TST_EFUSE1_MISC`, `CC_TST_ID_STRAPS`, `CC_FCTRL_FUSES`, `CC_HARVEST_FUSES`, and `PM_FUSES_1..21`. These fields describe boot events, driver reset mode, memory repair disable, feature disables, debug/ROM/SMU IOC/PCIE/DSMU fuse state, device/revision straps, harvested IP such as VCE/UVD/ACP/DC, VID/fuse voltage data, load-line trim, TDC limits, LPML temperature scaling, fan fuse parameters, and leakage data.

Fuse and strap fields are normally read-only or firmware-owned in practice, even though this header does not mark access permissions. Consumers should treat them as hardware identity and calibration inputs unless the register specification says otherwise.

### Memory Controller Tables

`MCARB_DRAM_TIMING_TABLE_1..96` describes a regular 8 by 4 timing matrix. For each entry it exposes full-width `McArbDramTiming` and `McArbDramTiming2` words plus packed padding and `McArbBurstTime` bytes.

`MC_REGISTERS_TABLE_1..81` maps a table header (`last` plus reserved bytes), 16 pairs of `address_N_s0/s1` fields, and data words for values 0 through 15 across data rows 0 through 3. These macros are likely used when SMU firmware or driver power-management code stores memory-controller register programming payloads for memory clock states.

The register tables are data layouts, not direct algorithms. Their correctness matters because a shifted address or data value can cause the SMU to program the wrong memory controller register during an MCLK/DPM transition.

### DPM Table Layout

The largest part of the chunk is `DPM_TABLE_1..370`. It maps the SMU dynamic power-management table in 32-bit words:

- `DPM_TABLE_1..27` define PID controller parameters for graphics, memory, and link clocks, including Ki, windup limits, precision, offsets, max state, max low-frequency fraction, and state shifts.
- `DPM_TABLE_28..35` carry system flags, SMIO masks, and counts for VDDC, VDDCI, and MVDD levels.
- `DPM_TABLE_36..67` describe voltage levels for VDDC 0..7, VDDCI 0..3, and MVDD 0..3, with voltage, standard high/low SIDD voltage, SMIO, and padding fields.
- `DPM_TABLE_68..73` record master deep-sleep control, graphics/memory/link level counts, and reserved words.
- `DPM_TABLE_74..169` describe graphics DPM levels 0..7. Each level contains minimum VDDC, VDDC phase data, SCLK frequency, activity level, deep-sleep divider, PCIe DPM level, SPLL/spread-spectrum words, power dynamic registers, throttle/activity/display-watermark enable fields, SCLK DID, power throttle, and hysteresis values.
- `DPM_TABLE_170..259` describe the memory ACPI level and memory levels 0..3, including minimum VDDC/VDDCI/MVDD, MCLK frequency, stutter/RTT/EDC controls, activity/throttle/strobe controls, hysteresis, display watermark, activity level, MPLL programming, MCLK power-management control, DLL control, and MPLL spread-spectrum words.
- `DPM_TABLE_260..291` describe link levels 0..7 with SPC, activity enable, PCIe lane count, PCIe generation speed, up/down thresholds, and reserved words.
- `DPM_TABLE_292..304` describe the ACPI graphics level, including flags, minimum voltage, SCLK frequency, deep-sleep divider, display watermark, SCLK DID, SPLL programming, spread spectrum, and power dynamic registers.
- `DPM_TABLE_305..337` cover SCLK step size and `Smio_0..31`.
- `DPM_TABLE_338..370` contain global DPM policy values such as graphics and memory intervals, thermal and voltage intervals, boot levels, high/low temperature limits, merged VDDCI, response times, DTE/PCIe intervals, GPIO selections, SVI2 enable, display CAC, nominal and maximum power, FPS thresholds, BAPM coefficients, GPU Tj limits, boot voltages, BAPM temperature gradient, low-SCLK interrupt threshold, VDDGFX recheck wait, and PPM temperature limit fields.

This table is a firmware contract. Driver code that builds or patches it must preserve the exact packing and revision-specific ordering.

### Soft Registers, Feature Status, PM Status, and Telemetry

`SOFT_REGISTERS_TABLE_1..29` maps firmware-visible software registers for reference clock frequency, DRAM log address/buffer fields, display PHY configuration, average graphics/memory/GIO activity, enabled DPM-level bitmasks for PCIe/LCLK/MCLK/SCLK, ULV counts/time, ucode load status, and reserved words.

`FEATURE_STATUS` exposes feature enable/forced bits for SCLK, MCLK, LCLK, UVD, VCE, SAMU, ACP, PCIe, BAPM, LPMX, NBDPM, LHTC, VPC, voltage controller, TDC limit, GPU CAC, AVS, and SPMI. `TDC_STATUS`, `TDC_MV_AVERAGE`, and `TDC_VRM_LIMIT` expose boost/throttle and current-limit telemetry. `ENTITY_TEMPERATURES_1` exposes a full-width GPU temperature field.

`SMU_PM_STATUS_0..127` are 128 full-width status/data words. The header does not name the internal meaning of each word beyond `DATA`; consumers need firmware table documentation or existing SMU code to decode them.

### Thermal, Fan, and Temperature Monitor Fields

The chunk maps the thermal interrupt and fan-control surface:

- `CG_THERMAL_INT_ENA`, `CG_THERMAL_INT_CTRL`, `CG_THERMAL_INT_STATUS`, `CG_THERMAL_CTRL`, `CG_THERMAL_STATUS`, and `CG_THERMAL_INT` cover high/low/trigger interrupt set/clear, digital thermal thresholds, interrupt masks, hardware enable, detection status, DPM event source, CTF pad control, fan duty status, thermal alert, and CTF/INTH/INTL thresholds.
- `CG_MULT_THERMAL_CTRL` and `CG_MULT_THERMAL_STATUS` cover thermal sensor filtering, range reset, selected temperature source, ready clear, ASIC maximum temperature, and CTF temperature.
- `CG_FDO_CTRL0..2`, `CG_TACH_CTRL`, and `CG_TACH_STATUS` cover static fan duty, spin-up duty/time, manual PWM, PWM hysteresis/ramp, min/max duty, powerdown, temperature bounds, tachometer target period, edge-per-revolution, and measured tach period.
- `CC_THM_STRAPS0` exposes thermal monitor calibration/configuration straps and disable bits.
- `THM_TMON0_RDIL0..15_DATA`, `THM_TMON0_RDIR0..15_DATA`, `THM_TMON0_INT_DATA`, `THM_TMON0_DEBUG`, and `THM_TMON0_STATUS` expose repeated Z, valid, and temperature fields plus monitor debug/status signals.

These macros feed temperature reporting, thermal interrupts, fan control, and DPM throttling. The repeated temperature monitor data fields make `VALID` checks important before interpreting packed temperature values.

### Power Management, Deep Sleep, Voting, and Display Timers

`GENERAL_PWRMGT`, `CNB_PWRMGT_CNTL`, `SCLK_PWRMGT_CNTL`, `TARGET_AND_CURRENT_PROFILE_INDEX`, `TARGET_AND_CURRENT_PROFILE_INDEX_1`, `PWR_PCC_CONTROL`, and `PWR_PCC_GPIO_SELECT` expose global power-management enables, PCIe/thermal/DPM behavior, CNB slow mode and NB power state forcing, SCLK dynamic/light sleep control, current/target DPM indices for MCLK/SCLK/LCLK/VDDCI/MVDD/VDDC/PCIe, and PCC GPIO control.

`CG_FREQ_TRAN_VOTING_0..7` are dense repeated bitmaps enabling frequency-throttling votes from BIF, HDP, ROM, IH semaphore, PDMA, DRM, IDCT, ACP, SDMA, UVD, VCE, DC/AZ, SAM, AVP, GRBM 0..15, and RLC. These fields gate which engines can vote in frequency transitions.

`CG_STATIC_SCREEN_PARAMETER`, `CG_DISPLAY_GAP_CNTL`, `CG_DISPLAY_GAP_CNTL2`, `CG_ACPI_CNTL`, and `CG_ULV_PARAMETER` cover static-screen thresholds, display-gap/VBI timing, VBI prediction, ACPI SCLK divider/change-skip, and ULV thresholds.

`SCLK_DEEP_SLEEP_CNTL`, `SCLK_DEEP_SLEEP_CNTL2`, `SCLK_DEEP_SLEEP_CNTL3`, `SCLK_DEEP_SLEEP_MISC_CNTL`, `LCLK_DEEP_SLEEP_CNTL`, and `LCLK_DEEP_SLEEP_CNTL2` define deep-sleep divider, ramp, hysteresis, enable, shallow/deep divider, in/out cushion, and many busy/idle mask fields for memory, BIF, UVD, VCE, SAM, RLC, HDP, ROM, SDMA, GRBM instances, PCIe/L1IMU/L2IMU/ORB, wake, DMA active, and SMU signals.

The chunk ends in the display timer family. `PWR_DISP_TIMER_0_CONTROL..4` are complete and expose interrupt count, enable, running, interrupt mask, status, status acknowledge, and interrupt bits. `PWR_DISP_TIMER_5_CONTROL` begins at the chunk boundary with only `DISP_TIMER_INT_COUNT` covered here.

## Control Flow

There is no direct executable control flow in this header. Runtime control flow is implied by the hardware protocols that use the constants:

1. Clock and DPM code reads current status/index registers, prepares new DPM-table or PLL fields with these masks, writes values through MMIO/SMU/SMC accessors, and waits for firmware or status acknowledgements.
2. Firmware mailbox code writes an argument register, writes a message register, polls a response/status field, and interprets success or failure according to SMU firmware protocol.
3. Thermal/fan code programs thresholds and fan PWM/tach parameters, then services detection/status/ack bits from interrupt registers.
4. Deep-sleep code programs divider/hysteresis/enable fields and masks off busy sources only when platform policy allows those sources to be ignored.
5. Display timing code programs timer counts, enables interrupts, watches running/status bits, and acknowledges status using the appropriate `*_STAT_AK` field.

The exact ordering, timeouts, and clear semantics are outside this generated mask file and must come from the SMU 7.1.1 programming guide or existing AMDGPU SMU/powerplay code.

## State and Persistence Behavior

This header owns no software state. It names hardware and firmware-visible state:

- Volatile control state: clock dividers, bypass selections, PLL controls, deep-sleep enables, frequency-vote enables, display timers, GPIO control, and fan/thermal control registers.
- Firmware communication state: indirect access address/data registers, mailbox messages/responses/arguments, firmware flags, firmware load/read status, and scratch/status words.
- Firmware table state: DPM, memory controller, MC register, soft-register, PM-status, and PM-fuse table layouts.
- Calibration and identity state: fuse, strap, VID, leakage, harvested-IP, thermal strap, and PM fuse fields.
- Telemetry/status state: feature status, TDC status/current averages/limits, PM status words, thermal status, tach status, temperature monitor values, and current/target profile indices.

Persistence is hardware-defined. Some fields may reset on ASIC reset, GPU reset, SMC reset, suspend/resume, BACO-like low-power entry, or firmware reload; others may reflect nonvolatile fuses or straps. The masks do not encode access type, stickiness, write-one-to-clear behavior, or save/restore policy.

## Dependencies and Integration Points

This chunk depends on the rest of the generated ASIC register ecosystem:

- Companion SMU 7.1.1 offset/address headers identify the actual register addresses.
- AMDGPU register helper macros perform field extraction, field insertion, MMIO, and indirect access.
- AMDGPU SMU/powerplay code consumes the DPM table, soft-register table, feature status, PM status, voltage, fan, thermal, and deep-sleep fields.
- Firmware loading and mailbox paths consume the SMC/SMU message, argument, response, input-data, firmware, status, and indirect-access fields.
- Clock and display integration consumes SPLL/MPLL, display-gap, VBI, ACPI SCLK, and display timer fields.
- Platform and board policy code consumes fuse, strap, voltage, power-limit, thermal-limit, fan, GPIO, and harvested-IP fields.

Because the names mirror AMD hardware documentation, downstream code should avoid renaming these macros. Wrappers are useful only when they enforce a broader, checked hardware sequence.

## Risks

- Register layout drift: every mask and shift must match SMU 7.1.1 hardware and firmware tables exactly. A single wrong bit position can corrupt voltage, clock, fan, or firmware mailbox state.
- Firmware ABI mismatch: the DPM, soft-register, PM-status, and MC tables are revision-specific contracts. Reusing this layout with incompatible firmware can silently mispack fields.
- Dangerous power/thermal writes: thermal thresholds, fan PWM, voltage levels, TDC limits, deep-sleep controls, and throttling votes directly affect stability, thermals, and user-visible performance.
- Incorrect status clearing: interrupt/status fields such as GPIO, thermal, and display timer status/ack bits may have special write-one-to-clear or acknowledge semantics not represented by the masks.
- Busy-mask misuse: deep-sleep masks can permit low-power entry while engines are active if programmed incorrectly.
- Indirect access races: multiple indirect channels and auto-increment bits require ownership discipline. Interleaved users can clobber the selected address or data window.
- Repeated-field copy errors: generated families such as `DPM_TABLE_*`, `SMU_PM_STATUS_*`, `THM_TMON0_*`, `CG_FREQ_TRAN_VOTING_*`, and display timers are large and regular; suffix mismatches are easy to miss.
- Boundary risk: this chunk ends mid-family at `PWR_DISP_TIMER_5_CONTROL`, so the final merged per-file document must reconcile the remaining display timer fields from the next chunk.

## Test Signals

Useful validation signals for consumers of this header include:

- Kernel build coverage for the AMDGPU SMU 7.1.1 paths with no missing macro or redefinition diagnostics.
- Unit or compile-time checks, where practical, that representative `REG_SET_FIELD`/`REG_GET_FIELD` operations round-trip packed fields such as DPM table bytes, voltage halves, profile indices, thermal thresholds, and display timer status bits.
- Firmware mailbox tests that send a benign SMU message, verify argument/response handling, and confirm timeouts do not leave indirect or mailbox state wedged.
- DPM bring-up tests that compare programmed SCLK/MCLK/LCLK/PCIe levels, current/target indices, feature-status bits, and SMU PM status words against expected firmware state.
- Thermal/fan tests that validate temperature monitor `VALID` bits, threshold interrupts, fan PWM/tach behavior, and status acknowledge paths.
- Suspend/resume and GPU reset tests that verify clock, DPM, fan, thermal, display timer, and deep-sleep registers are restored or intentionally reinitialized.
- Hardware telemetry checks that TDC, temperature, PM status, and feature status values remain sane across workload changes and power-source transitions.
- Negative tests for deep sleep and frequency voting: active engines should block low-power entry unless their busy masks are intentionally configured, and disabled vote sources should not force throttling.
