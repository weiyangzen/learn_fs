# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_1_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003413`: lines 1-4454, `Docs/researches/chunks/subset-b-003413_research.md`
- `subset-b-003414`: lines 4455-4866, `Docs/researches/chunks/subset-b-003414_research.md`

## Chunk Research

### subset-b-003413: lines 1-4454

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

### subset-b-003414: lines 4455-4866

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_1_sh_mask.h lines 4455-4866

## Scope

This chunk is the tail of the generated SMU 7.1.1 shift/mask header. It covers the final display power timer fields, VDDGFX idle-detection fields, LCAC memory/controller counter fields, ROM and ROM software-command register fields, current power-gating status masks, and the closing `SMU_7_1_1_SH_MASK_H` include guard.

The file is not executable driver logic. It is a hardware register metadata header: each `*_MASK` constant identifies writable or readable bits in a 32-bit SMU register, and each matching `*__SHIFT` constant gives the low bit for that field. The sibling address header `smu_7_1_1_d.h` supplies the corresponding `ix*` and `mm*` register addresses.

## Purpose

The chunk lets AMDGPU and PowerPlay code program SMU 7.1.1 registers without hard-coding bit positions at every call site. It documents several hardware blocks:

- `PWR_DISP_TIMER_5_CONTROL` through `PWR_DISP_TIMER_15_CONTROL`, plus `PWR_DISP_TIMER_CONTROL2`, for display-related interrupt timer setup and status.
- `VDDGFX_IDLE_PARAMETER`, `VDDGFX_IDLE_CONTROL`, and `VDDGFX_IDLE_EXIT`, for graphics-voltage idle thresholding, detection, SMC idle-state visibility, forced exit, and BIF exit requests.
- `LCAC_MC0..MC3_*` and `LCAC_CPL_*`, for load/current activity counter controls and override registers.
- `ROM_SMC_IND_INDEX/DATA`, `ROM_CNTL`, `PAGE_MIRROR_CNTL`, `ROM_STATUS`, `CGTT_ROM_CLK_CTRL0`, `ROM_INDEX`, `ROM_DATA`, `ROM_START`, `ROM_SW_CNTL`, `ROM_SW_STATUS`, `ROM_SW_COMMAND`, and `ROM_SW_DATA_1..64`, for SMU-side ROM access, SPI timing/control, page mirroring, and bulk software-command payloads.
- `CURRENT_PG_STATUS__VCE_PG_STATUS_MASK` and `CURRENT_PG_STATUS__UVD_PG_STATUS_MASK`, for checking whether video encode/decode engines are power-gated before touching their clock-gating registers.

## Important Symbols

The display timer controls repeat the same layout for timers 6 through 15, with this chunk also completing timer 5:

- `DISP_TIMER_INT_COUNT` uses bits 0-24 where present.
- `DISP_TIMER_INT_ENABLE` is bit 25.
- `DISP_TIMER_INT_RUNNING` is bit 26.
- `DISP_TIMER_INT_MASK` as a field/control bit appears at bit 27, while the generated macro names include both `..._INT_MASK_MASK` and `..._INT_MASK__SHIFT`.
- `DISP_TIMER_INT_STAT`, `DISP_TIMER_INT_STAT_AK`, and `DISP_TIMER_INT` occupy bits 28, 29, and 30.
- `PWR_DISP_TIMER_CONTROL2__DISP_TIMER_PULSE_WIDTH_MASK` is a 10-bit pulse-width field at bits 0-9.

The VDDGFX idle group defines a 16-bit threshold, a 4-bit threshold unit, an enable bit, a detection bit, a forced-exit bit, an SMC state bit, and `VDDGFX_IDLE_EXIT__BIF_EXIT_REQ_MASK`.

Each LCAC control register has the same shape: enable at bit 0, threshold in bits 1-16, block id in bits 17-21, and signal id in bits 22-29. Each `OVR_SEL` and `OVR_VAL` register is a full 32-bit field.

The ROM group includes:

- Full-width indirect index/data fields for `ROM_SMC_IND_INDEX` and `ROM_SMC_IND_DATA`.
- `ROM_CNTL` fields for SCK overwrite, clock gating, chip-select setup/hold timing, and SCK prescale values for refclk and crystal clock.
- `PAGE_MIRROR_CNTL` fields for base address, invalidate, enable, and usage.
- `ROM_STATUS__ROM_BUSY_MASK`, ROM clock-gating delay/hysteresis/override fields, 24-bit `ROM_INDEX` and `ROM_START`, and full-width `ROM_DATA`.
- `ROM_SW_CNTL` data size, command size, and return-data enable; `ROM_SW_STATUS__ROM_SW_DONE_MASK`; `ROM_SW_COMMAND` instruction and 24-bit address fields; and 64 full-width `ROM_SW_DATA_N` payload registers.

## APIs, Types, and Functions

This chunk defines no C functions, structs, enums, or runtime APIs. Its API surface is the set of preprocessor constants exported to AMDGPU code that includes the generated ASIC register headers.

The symbols are normally paired with address definitions from `smu_7_1_1_d.h`. For example, the address header maps `ixPWR_DISP_TIMER_5_CONTROL` through `ixPWR_DISP_TIMER_15_CONTROL`, `ixVDDGFX_IDLE_*`, `ixLCAC_*`, `ixROM_CNTL`, `ixROM_SW_*`, and `ixCURRENT_PG_STATUS` to SMU indirect register addresses. Runtime code then uses helpers such as `RREG32_SMC`, `WREG32_SMC`, `cgs_read_ind_register`, or `cgs_write_ind_register` to access those registers.

These constants are hardware ABI definitions. A value change is not a local refactor; it changes how the driver encodes or decodes hardware state.

## Control Flow

The header itself has no control flow beyond the include guard. Runtime flow appears in consumers:

1. Display or power-management code can compose display timer control words using count, enable, mask, acknowledge, status, and pulse-width fields.
2. SMU power-management code can set VDDGFX idle thresholds and enable/force idle exit behavior, then observe detect/state bits.
3. LCAC initialization code writes MC and CPL control registers, often first with low enable/threshold values, then after a short delay with block/signal selector bits set.
4. BIOS/ROM read paths save `ROM_CNTL`, enable or override ROM signaling, read BIOS contents, and restore the saved control value.
5. Video IP clock-gating query paths read `ixCURRENT_PG_STATUS` or an APU variant and skip UVD/VCE clock-gating register reads while the corresponding engine is power-gated.
6. ROM software-command flows would fill `ROM_SW_CNTL`, `ROM_SW_COMMAND`, and `ROM_SW_DATA_1..64`, then poll `ROM_SW_STATUS__ROM_SW_DONE_MASK`; this chunk supplies the field layout even though the sampled local call sites mostly use the simpler `ROM_CNTL` path.

Concrete local examples include `cik_read_disabled_bios()` and `vi_read_disabled_bios()`, which read `ixROM_CNTL`, set `ROM_CNTL__SCK_OVERWRITE_MASK` while calling `amdgpu_read_bios()`, and restore the original value afterward. `smu7_hwmgr.c` programs `ixLCAC_MC0_CNTL`, `ixLCAC_MC1_CNTL`, and `ixLCAC_CPL_CNTL` through SMC indirect writes. `uvd_v6_0_get_clockgating_state()` and `vce_v3_0_get_clockgating_state()` test the UVD/VCE masks before reading video clock-gating registers.

## State and Persistence

All state represented here lives in hardware registers or in ROM command payload latches, not in this header:

- Display timer count, enable, mask, running, interrupt, status, and acknowledge bits persist in SMU timer control registers while the device remains powered and initialized.
- VDDGFX idle threshold and unit fields configure idle-detection policy. Detect/state/exit bits are live hardware state that can change as graphics and bus activity changes.
- LCAC control registers persist the selected monitored block/signal, threshold, and enable state; override select/value registers force or mask measurement inputs until cleared.
- ROM control fields persist SPI/ROM access timing and clocking policy. BIOS-read code that changes `ROM_CNTL` must restore it because the register affects subsequent ROM transactions.
- ROM software-command data registers are command-buffer-like hardware state. `ROM_SW_DATA_1..64` are full-width payload slots, while `ROM_SW_STATUS__ROM_SW_DONE_MASK` is transient completion state.
- Current power-gating status bits are live status flags for media blocks. They are read to avoid touching register spaces that may be inaccessible or invalid while a block is power-gated.

The header contains no persistence, locking, or synchronization. Consumers must provide ordering, mutual exclusion, and restore logic around hardware register writes.

## Dependencies and Integration Points

Primary dependencies:

- `drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_1_d.h` for matching register addresses, including `ixPWR_DISP_TIMER_*`, `ixVDDGFX_IDLE_*`, `ixLCAC_*`, `ixROM_*`, and `ixCURRENT_PG_STATUS`.
- AMDGPU SMC indirect register access helpers such as `RREG32_SMC` and `WREG32_SMC`, and PowerPlay CGS indirect access helpers.
- Common register field helper conventions in AMDGPU, where masks and shifts are combined through `REG_SET_FIELD`-style code or direct bitwise operations.
- Power-management, BIOS-loading, display-timer, and media IP clock-gating code that needs SMU 7.1.1-specific bit layouts.

The LCAC symbols integrate with PowerPlay/hwmgr current-activity setup. The ROM symbols integrate with early device bring-up and disabled-BIOS reads on CIK/VI-class paths. The `CURRENT_PG_STATUS` masks integrate with UVD and VCE clock-gating reporting so those IP blocks are not queried while powered down.

## Risks and Edge Cases

- The generated names around `DISP_TIMER_INT_MASK` are easy to misread: `PWR_DISP_TIMER_N_CONTROL__DISP_TIMER_INT_MASK_MASK` is the field mask for a field named `DISP_TIMER_INT_MASK`, while `PWR_DISP_TIMER_N_CONTROL__DISP_TIMER_INT_MASK` is a separate interrupt bit at bit 30. Direct readers must distinguish the field name from the `_MASK` suffix convention.
- Timer 5 is incomplete in this chunk because its count field appears in the previous chunk; timers 6-15 are complete here. Reconciliation must merge adjacent chunks for a full per-file view.
- `PWR_DISP_TIMER_14_CONTROL` and `PWR_DISP_TIMER_15_CONTROL` have addresses far from the timer 2-13 sequence in `smu_7_1_1_d.h`; code must use the address macros rather than assuming contiguous timer addresses.
- Narrow fields must be shifted and masked, not ORed with raw values. Examples include 25-bit timer counts, 10-bit pulse width, 16-bit VDDGFX thresholds, 4-bit threshold units, 5-bit LCAC block ids, 8-bit LCAC signal ids, 24-bit ROM addresses, and 2-bit ROM command sizes.
- ROM code often saves and restores `ROM_CNTL`. Any early return between setting `ROM_CNTL__SCK_OVERWRITE_MASK` and restoring the original value can leave ROM clocking or SPI behavior altered.
- `ROM_STATUS__ROM_BUSY_MASK` and `ROM_SW_STATUS__ROM_SW_DONE_MASK` are polling signals. Consumers need timeouts to avoid boot or resume hangs if hardware never transitions.
- `PAGE_MIRROR_CNTL` includes invalidate and enable bits near the base/usage fields. Accidental writes that preserve neither old state nor intended invalidation ordering can stale or disable the mirror mapping.
- Full-width `ROM_SW_DATA_N` fields do not validate command length. The software-command flow must keep `DATA_SIZE` consistent with the number of data registers populated.
- Power-gating status bits protect access to UVD/VCE clock-gating registers. Ignoring them risks register reads while the engine is power-gated, which can return invalid values or trigger access problems depending on platform state.
- These headers are generated from hardware descriptions; hand edits can diverge from firmware/ASIC documentation and silently corrupt register programming.

## Test Signals

Useful validation signals for code that consumes this chunk:

- Compile coverage for SMU 7.1.1 builds should catch renamed or missing symbols in CIK/VI, PowerPlay, UVD, and VCE paths.
- BIOS-read tests on disabled-ROM configurations should show `ROM_CNTL` saved, `ROM_CNTL__SCK_OVERWRITE_MASK` set during the read, and the original value restored on exit.
- Hardware traces or debug reads should confirm LCAC writes to `ixLCAC_MC0_CNTL`, `ixLCAC_MC1_CNTL`, and `ixLCAC_CPL_CNTL` set enable, threshold, block, and signal bits exactly as intended.
- Display/power tests should confirm display timer interrupts transition through enable/running/status/ack states without spurious unmasked interrupts.
- VDDGFX idle tests should observe threshold/unit programming, idle-detect transitions, SMC idle-state reporting, and forced-exit behavior under graphics load and idle conditions.
- UVD/VCE clock-gating debug output should report that state cannot be read while the corresponding `CURRENT_PG_STATUS` bit says the engine is power-gated, and should resume normal reporting after power-up.
- ROM software-command tests, if present on this ASIC path, should verify command-size/data-size encoding, `ROM_SW_DONE` polling with timeout coverage, and correct use of the 64 payload registers.
