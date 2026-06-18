# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_0_1_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003407`: lines 1-4534, `Docs/researches/chunks/subset-b-003407_research.md`
- `subset-b-003408`: lines 4535-5462, `Docs/researches/chunks/subset-b-003408_research.md`

## Chunk Research

### subset-b-003407: lines 1-4534

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_0_1_sh_mask.h lines 1-4534

## Scope

This chunk covers the first 4,534 lines of the generated SMU 7.0.1 shift/mask header. The file section starts at the license and include guard, then defines 4,509 preprocessor macros for SMU, clock, power-management, thermal, firmware, and firmware-table bitfields. The source file continues after this chunk; this chunk ends in the middle of the `CG_FREQ_TRAN_VOTING_0` register after `GRBM_9_FREQ_THROTTLING_VOTE_EN`.

The covered range includes:

- Clock and PLL controls for DCLK, VCLK, ECLK, ACLK, DFS bypass, SPLL, clock pins, thermal clocks, miscellaneous clock muxes, and PLL test paths.
- SMC indirect register access windows, SMC message/response/argument mailboxes, syscon reset/clock controls, SMC scratch, GPIO pads, and RCU/CC fuse and boot-status fields.
- SMU firmware-load/status registers, efuse fields, and a large `DPM_TABLE_1` through `DPM_TABLE_510` firmware table layout.
- Firmware flags, TDC status/limits, feature-status bits, entity temperatures, MCARB DRAM timing table fields, MC register table fields, fan table fields, soft-register table fields, PM fuse fields, and `SMU_PM_STATUS_0` through `SMU_PM_STATUS_127`.
- Thermal interrupt/control/status, FDO fan control, tachometer control/status, thermal strap and TMON data fields.
- General power-management, CNB power-management, SCLK power-management, current/target profile index, and the first part of frequency-transition voting.

This file chunk is a generated C preprocessor bitfield map only. It defines no functions, structs, variables, storage, loops, branches, or executable control flow.

## Purpose

The purpose of this header section is to provide the bit-level ABI between AMDGPU SMU/power-management code and SMU 7.0.1 hardware/firmware registers. Each field is represented by the generated pair:

- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask used to isolate or compose the field.
- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when shifting field values.

Driver code normally combines these macros with the matching SMU 7.0.1 offset/default headers and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32`, `WREG32`, `RREG32_SMC`, `WREG32_SMC`, or ASIC-specific indirect-access helpers. The offset header supplies addresses or indirect indices; this header supplies field positions and masks.

## Important Macro Families

### Clock, DFS, and PLL Registers

The opening section defines clock-divider and status fields for `CG_DCLK_CNTL`, `CG_VCLK_CNTL`, `CG_ECLK_CNTL`, and `CG_ACLK_CNTL`. The layout is regular: a low `*_DIVIDER`, direction-control enable/toggle bits, and a direction-control divider, with status registers exposing current status and done-toggle bits for DCLK/VCLK/ECLK.

`GCK_DFS_BYPASS_CNTL` exposes bypass enables for ECLK, LCLK, EVCLK, DCLK, VCLK, DISPCLK, DPREFCLK, ACLK, ADIVCLK, PSPCLK, SAMCLK, and SCLK, plus `USE_SPLL_BYPASS_EN`. `GCK_ADFS_CLK_BYPASS_CNTL1` later provides multi-bit bypass controls for similar domains. These fields are hardware clock-routing controls and should be coordinated with SMU clock policy rather than used as standalone debug toggles.

The SPLL families (`CG_SPLL_FUNC_CNTL`, `_2` through `_7`, `SPLL_CNTL_MODE`, `CG_SPLL_SPREAD_SPECTRUM`, and `_2`) describe reset, power, divider enable, bypass, reference divider, post-divider update/enable, feedback divider, spread-spectrum, lock/test, baby-step/update, bandwidth, and status fields. Clock pin and miscellaneous clock families (`MPLL_BYPASSCLK_SEL`, `CG_CLKPIN_CNTL`, `CG_CLKPIN_CNTL_2`, `CG_CLKPIN_CNTL_DC`, `THM_CLK_CNTL`, `MISC_CLK_CTRL`, and `GCK_PLL_TEST_CNTL`) define reference-clock routing, oscillator/input enables, test source selection, and thermal monitor clock selection.

### SMC Access, Mailbox, Syscon, GPIO, and RCU/CC Fuses

The chunk includes several SMC indirect access windows:

- `GCK_SMC_IND_INDEX/DATA`
- `SMC_IND_INDEX/DATA` and numbered `SMC_IND_INDEX_0..7` / `SMC_IND_DATA_0..7`
- `SMU_SMC_IND_INDEX/DATA`

Their masks are full-width address/data fields, with `SMC_IND_ACCESS_CNTL` providing auto-increment bits for the eight numbered windows. These macros back indirect reads and writes into SMC/SMU address spaces.

`SMC_MESSAGE_0..11`, `SMC_RESP_0..11`, and `SMC_MSG_ARG_0..11` define host-to-SMC message IDs, responses, and argument registers. They are key integration points for command/response flows: software writes arguments and message IDs, then polls or reads response fields. The macros do not encode mailbox ordering, timeout, or busy semantics; those must come from the caller.

`SMC_SYSCON_RESET_CNTL`, `SMC_SYSCON_CLOCK_CNTL_0..2`, `SMC_SYSCON_MSG_ARG_0`, `SMC_PC_C`, and `SMC_SCRATCH9` define SMC reset, clock gating, wake-on-IRQ, message argument, program-counter, and scratch-state fields. GPIO families define pad strength, masks, output/input/enables, pin straps 0 through 30, interrupt status/enable/type/polarity/acknowledge, external trigger control, receiver select, and pull-up/pull-down enables.

`RCU_UC_EVENTS`, `RCU_MISC_CTRL`, `CC_RCU_FUSES`, `CC_SMU_MISC_FUSES`, `CC_SCLK_VID_FUSES`, `CC_GIO_*`, `CC_SMU_TST_EFUSE1_MISC`, `CC_TST_ID_STRAPS`, and `CC_FCTRL_FUSES` expose reset-controller events, boot sequencing, fuse-disable flags, repair/test disable flags, device/revision straps, minimum SCLK DID, post-reset clock DID, VCE/IOMMU disable fuses, and PCIe/fabric lockout flags. These are read-mostly platform identity, manufacturing, fuse, and security/disable-state fields.

### SMU Firmware and DPM Table Layout

`SMU_MAIN_PLL_OP_FREQ`, `SMU_STATUS`, `SMU_FIRMWARE`, `SMU_INPUT_DATA`, and `SMU_EFUSE_0` cover firmware status, firmware-read/write block controls, mode/selector bits, firmware input start address, and a single full-width efuse data word.

The largest family is `DPM_TABLE_1` through `DPM_TABLE_510`. It maps the SMU firmware dynamic power-management table as 32-bit words and packed fields. Major subregions visible in this chunk include:

- Graphics, memory, and link PID controller coefficients and precision fields.
- System flags, SMIO masks, and VDDC/VDDCI/MVDD level counts.
- VDDC, VDDCI, and MVDD voltage-level entries with standard voltage, voltage, SMIO, and padding fields.
- Level counts for UVD, link, memory, graphics, SAMU, ACP, and VCE.
- Eight graphics DPM levels carrying flags, minimum VDDC/phases, SCLK frequency, activity level, SPLL settings, spread-spectrum settings, CAC/power-dynamic values, throttle/activity enables, display watermark, SCLK DID, hysteresis, power throttle, and deep-sleep divider.
- Memory ACPI level and memory DPM levels 0 through 5 in this chunk, with minimum voltages, MCLK frequency, stutter/RTT/EDC controls, activity/throttle enable flags, strobe settings, hysteresis, activity level, MPLL control words, MCLK power-management, DLL control, and spread-spectrum fields.
- Link levels 0 through 7 with PCIe generation speed, lane count, activity enable, and up/down thresholds.
- ACPI level graphics fields, UVD levels 0 through 7, VCE/ACP/SAMU levels 0 through 7, ULV values, SMIO words 0 through 31, boot levels and intervals, temperature/voltage response limits, DTE/PCIe boot link settings, thermal/AC/DC/VR-hot GPIOs, SVI2 enable, display CAC, nominal/max power, FPS thresholds, BAPM matrices, GPU thermal limits, boot voltages, DRAM log addresses/sizes, and BAPM temperature gradient.

These macros describe firmware-owned table memory rather than ordinary MMIO registers. They are used when host code constructs, patches, uploads, reads back, or decodes the SMU power-play/DPM table. Any field drift changes the firmware ABI.

### Firmware Flags, Current Limits, Features, and Firmware Tables

`FIRMWARE_FLAGS` exposes firmware interrupt enable and test-count fields. `TDC_STATUS`, `TDC_MV_AVERAGE`, and `TDC_VRM_LIMIT` expose VDD/VDDC boost/throttle status, averaged current, and VRM current limits.

`FEATURE_STATUS` is a compact status bitmap for enabled or forced features: SCLK/MCLK/LCLK/UVD/VCE/ACP/SAMU/PCIe DPM, BAPM, LPMX, NBDPM, LHTC, VPC, voltage controller, TDC limit, GPU CAC, AVS, SPMI, and forced DPM controls. This family is a useful diagnostic surface for whether firmware policy features are active.

`ENTITY_TEMPERATURES_1` exposes a full-width GPU temperature field. `MCARB_DRAM_TIMING_TABLE_1..144` maps an 8-by-6 style matrix of memory-controller arbitration timing data, timing2 data, padding bytes, and burst-time fields. `MC_REGISTERS_TABLE_1..113` maps memory-controller register programming data: a `last` marker, address pairs for 16 addresses, and six groups of 16 full-width data values. `FAN_TABLE_1..9` maps firmware fan-curve parameters such as temperature min/med/max/current, FDO mode/min/max, slopes, hysteresis, PWM current, response limit, refresh period, and temperature source.

`SOFT_REGISTERS_TABLE_1..30` maps firmware soft registers for reference clock, PM timer period, feature enables, display/VBlank/training delays, voltage and MVDD switching timing, handshakes, display PHY configurations, average graphics/memory/GIO activity, enabled DPM level masks for SCLK/MCLK/LCLK/PCIe/UVD/VCE/ACP/SAMU, and reserved words.

`PM_FUSES_1..19` maps power-management fuse data for BAPM VDDC VIDs, VDDC VIDs, SVI load-line controls, TDC package and throttle release limits, LPML temperature limits/scalers, GNB LPML entries and VID bounds, and BAPM VDDC base leakage values.

### PM Status, Thermal, Fan, and TMON Registers

`SMU_PM_STATUS_0..127` are 128 full-width status words. They likely serve as firmware-visible or debug-visible status slots; the macros provide only `DATA` masks and shifts, so field-level interpretation must come from firmware documentation or higher-level decoder code.

Thermal and fan control families include:

- `CG_THERMAL_INT_ENA`, with set/clear enables for high, low, and trigger thermal interrupts.
- `CG_THERMAL_INT_CTRL`, with digital high/low thresholds, GNB temperature threshold, interrupt masks, trigger-CNB mask, and GNB hardware enable.
- `CG_THERMAL_INT_STATUS`, `CG_THERMAL_CTRL`, `CG_THERMAL_STATUS`, `CG_THERMAL_INT`, `CG_MULT_THERMAL_CTRL`, and `CG_MULT_THERMAL_STATUS`, covering thermal event detection, DPM event source, CTF pad controls, FDO PWM duty status, alert/generic status, CTF/high/low thresholds, thermal range reset, temp selection, ASIC max temp, and CTF temp.
- `CG_FDO_CTRL0..2`, with static/spinup duty, manual PWM, hysteresis, ramp, min/max duty, mode, spinup time, TMIN/TMAX, response rate, and power-down bit.
- `CG_TACH_CTRL` and `CG_TACH_STATUS`, with edge-per-revolution, target period, and measured tach period fields.
- `CC_THM_STRAPS0`, with TMON bandgap adjust, fuse/config source, acquisition count, clock selection, CTF disable, per-TMON disable bits, and unused bit.
- `THM_TMON0_RDIL0..15_DATA`, `THM_TMON0_RDIR0..15_DATA`, `THM_TMON0_INT_DATA`, and `THM_TMON0_DEBUG`, with repeated `Z`, `VALID`, and `TEMP` fields for thermal monitor readings plus debug selection/data.

These fields back thermal interrupt handling, fan control, telemetry reads, and safety throttling. Some bits are configuration thresholds, some are status/valid bits, and some are command-like set/clear bits.

### Power-Management Control and Frequency Voting

`GENERAL_PWRMGT` exposes global power-management enable, static PM enable, thermal protection disable/type, SMIO index selection, low-voltage ACPI D2/D3 behavior, voltage power-management enable, GPU counter controls, ACPI D3 VID, dynamic spread-spectrum enable, and spare fields.

`CNB_PWRMGT_CNTL` exposes GNB slow-mode controls, a forced NB power-state bit, DPM enable, and spare bits. `SCLK_PWRMGT_CNTL` is a dense control register for SCLK power management: off/low-D1, dynamic power-down, busy/SCLK counter resets, dynamic GFX clock-off control, force/request off/on controls, ACPI D1/D2/D3 clock-off, light sleep, pulse skip, light-sleep counter, dynamic PM, DPM dynamic power-down controls, voltage-update enable, forced PM interrupts, and graphics voltage-change controls.

`TARGET_AND_CURRENT_PROFILE_INDEX` encodes current and target state plus current/target MCLK, SCLK, and LCLK indices. This is a key status/control surface for DPM state transitions.

The chunk ends in `CG_FREQ_TRAN_VOTING_0`, defining frequency-throttling vote enables for BIF, HDP, ROM, IH semaphore, PDMA, DRM, IDCT, ACP, SDMA, UVD, VCE, DC_AZ, SAM, AVP, and GRBM blocks 0 through 9. The remaining GRBM 10 through 15 and later voters continue in the next chunk, so this family is incomplete in this document.

## Control Flow and State Behavior

There is no source-level runtime control flow in this chunk. Its effect is compile-time: it determines how callers pack and unpack 32-bit hardware register values and SMU firmware table words.

The persistent state represented by the macros lives in hardware registers, SMC/SMU indirect address spaces, fuses, or SMU firmware-owned RAM tables. Important persistent or semi-persistent state includes PLL/clock-divider configuration, SMC mailbox arguments/responses, syscon reset/clock state, GPIO/pinstrap state, fuse-derived feature disable state, DPM table entries, fan table entries, soft-register timing knobs, PM fuse values, PM status words, thermal thresholds and interrupt masks, fan PWM/tach controls, general/SCLK power-management controls, and current/target DPM profile indices.

The macros do not distinguish between read-only, read/write, write-one-to-clear, sticky, strobe, or command fields. Examples that need external sequencing include SMC mailbox message/response polling, SPLL update/lock status, SMC reset bits, GPIO interrupt acknowledge bits, firmware load/read-done state, thermal interrupt set/clear bits, FDO fan control, tachometer target/status reads, SCLK force/request-off bits, voltage-update/change-enable bits, and frequency-throttling vote enables.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `smu_7_0_1_offset.h` supplies the register offsets or indirect addresses that correspond to these field names.
- `smu_7_0_1_default.h`, where available, supplies reset/default values.
- AMDGPU register helper macros consume the `__SHIFT` and `_MASK` constants to avoid hard-coded bit positions.
- SMU/powerplay code and firmware-table structures must agree with the generated `DPM_TABLE_*`, `FAN_TABLE_*`, `SOFT_REGISTERS_TABLE_*`, `PM_FUSES_*`, and `SMU_PM_STATUS_*` layouts.

Likely integration points in this source tree include AMDGPU SMU 7 / powerplay initialization, firmware loading, DPM table construction, thermal/fan management, clock/PLL setup, SMC message submission, indirect SMC register access, suspend/resume, reset handling, and debug/status dumping. Consumers must include the matching SMU 7.0.1 offset/mask/default set together; nearby SMU generations can have similar names with different packed layouts.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write unrelated clock, power, thermal, fuse, or firmware-table fields.
- The `DPM_TABLE_*` region is firmware ABI, not just driver-local metadata. Incorrect packing can break voltage/frequency levels, PCIe link levels, UVD/VCE/ACP/SAMU levels, fan/thermal policy, BAPM coefficients, boot voltages, or DRAM logging.
- SMC mailbox and indirect access fields require strict ordering and timeout handling. Misusing full-width argument/data masks can send malformed firmware commands or read/write the wrong indirect address.
- Clock/PLL and DFS bypass fields can destabilize the ASIC if changed outside the expected SMU sequencing.
- Fuse and strap fields are read-mostly policy inputs. Treating disable/repair/security bits as writable configuration would be unsafe.
- Thermal and fan fields affect device protection. Bad thresholds, interrupt masks, PWM values, tach settings, or TMON validity handling can cause missed throttling or noisy fan behavior.
- Repetitive generated table families are easy to corrupt mechanically. `DPM_TABLE`, `MCARB_DRAM_TIMING_TABLE`, `MC_REGISTERS_TABLE`, `SMU_PM_STATUS`, TMON data, and PM fuse groups rely on exact numbering and field order.
- This chunk ends mid-family in `CG_FREQ_TRAN_VOTING_0`; a final merged report must reconcile the remaining voting fields from the next chunk.

## Test and Validation Signals

Useful validation is mostly build and hardware/firmware integration coverage:

- Build AMDGPU and powerplay code that includes `smu/smu_7_0_1_sh_mask.h`; this catches missing or renamed macros.
- SMU firmware-load tests should verify `SMU_STATUS`, `SMU_FIRMWARE`, `SMU_INPUT_DATA`, mailbox argument/response fields, and indirect SMC access windows.
- DPM validation should upload/read back the DPM table and verify graphics, memory, link, UVD, VCE, ACP, SAMU, voltage, boot-level, interval, BAPM, and thermal fields decode as expected.
- Clock tests should exercise DCLK/VCLK/ECLK/ACLK dividers, SPLL programming, DFS bypass controls, spread-spectrum settings, and lock/status bits under the supported SMU sequence.
- Thermal/fan tests should cover high/low/trigger interrupts, CTF and TMON readings, fan PWM/FDO controls, tachometer period reporting, thermal straps, and safety throttling.
- Power-management tests should verify feature-status bits, TDC boost/throttle/current/limit fields, general PM enables, SCLK power-management controls, target/current profile indices, and frequency-transition votes.
- Suspend/resume and reset tests should confirm syscon reset/clock controls, GPIO interrupt state, PM status words, and firmware tables survive or reinitialize according to ASIC expectations.

### subset-b-003408: lines 4535-5462

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_0_1_sh_mask.h lines 4535-5462

## Scope

This chunk covers the final portion of the SMU 7.0.1 generated shift/mask header. It starts in the middle of `CG_FREQ_TRAN_VOTING_0` graphics/RLC throttling vote fields and runs through the end of the include guard. The covered content is entirely C preprocessor register-field metadata: each hardware field is represented as a `_MASK` macro, a `__SHIFT` macro, or both. There are no functions, structs, storage objects, allocation paths, locks, or executable branches in this range.

The register families in this chunk are:

- `CG_FREQ_TRAN_VOTING_0` through `CG_FREQ_TRAN_VOTING_7` frequency-transition throttling vote enables.
- PLL, static-screen, display-gap, ACPI, SCLK deep-sleep, LCLK deep-sleep, ULV, and SCLK minimum-divider controls.
- `TARGET_AND_CURRENT_PROFILE_INDEX_1` current/target voltage and PCIe profile index fields.
- LCAC threshold/override controls for SX0, MC0 through MC3, and CPL.
- ROM indirect access, ROM clocking/timing, ROM page mirror, ROM indexed/software command/data, ROM busy/done status, and the 64 full-width `ROM_SW_DATA_n` payload registers.
- Current power-gating status bits for VCE and UVD, plus `SMC_SYSCON_MISC_CNTL` prefetcher enable.

## Purpose

The purpose of this section is to define the bit-level ABI used by AMDGPU SMU/clock/power-management code when it reads or writes SMU 7.0.1 registers. The sibling SMU offset header supplies register addresses. This header supplies the field masks and bit positions required to compose register values, extract status fields, and preserve unrelated bits during read/modify/write updates.

Consumers typically use these macros through AMDGPU register helpers and bitfield helpers, for example `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32`, `WREG32`, `RREG32_SMC`, or ASIC-specific register access wrappers. The macros are not meaningful by themselves; their correctness depends on exact alignment with the ASIC register specification and the corresponding offset/default headers.

## Important Macro Families

### Frequency Transition Voting

Lines 4535-4982 are dominated by `CG_FREQ_TRAN_VOTING_*` field pairs. `CG_FREQ_TRAN_VOTING_0` is already in progress at the start of the chunk and contributes the tail fields for `GRBM_10` through `GRBM_15` and `RLC`. `CG_FREQ_TRAN_VOTING_1` through `CG_FREQ_TRAN_VOTING_7` then repeat a regular layout.

Each full voting register exposes one-bit enable fields for blocks that can participate in frequency throttling or frequency transition votes:

- BIF, HDP, ROM, IH semaphore, PDMA, DRM, IDCT, ACP, SDMA, UVD, VCE, DC/AZ, SAM, and AVP.
- `GRBM_0` through `GRBM_15`, mapping per-GRBM graphics busy/throttling participants.
- RLC at bit 30.

The repeated layout makes these fields especially likely to be used by generic tables or initialization sequences that program all voting slots consistently. A wrong mask in this family can leave a hardware client unable to vote for throttling, or can allow an unintended client to stall a clock/frequency transition.

### Clock and Display Power Parameters

`PLL_TEST_CNTL` at lines 4983-4992 provides test source/reference select fields, reference/test count fields, and a test reset bit. This is diagnostic/control-plane register metadata rather than a normal runtime data path.

`CG_STATIC_SCREEN_PARAMETER` and `CG_DISPLAY_GAP_CNTL`/`CG_DISPLAY_GAP_CNTL2` at lines 4993-5008 define the thresholds and timing used by display-aware clock-gating logic. The static-screen fields encode a threshold and unit; display-gap fields encode display gap selection, vertical blanking interval timer count/unit, memory-change display gap behavior, timer disable, and a full-width prediction register.

`CG_ACPI_CNTL` at lines 5009-5012 defines SCLK ACPI divisor and SCLK-change skip control. These fields integrate SMU clock behavior with platform power-management states.

### SCLK Deep Sleep Controls

`SCLK_DEEP_SLEEP_CNTL` at lines 5013-5050 describes the main system-clock deep-sleep register. It includes:

- Divider, ramp disable, and hysteresis fields.
- Mask bits for activity or permission signals such as SCLK running, self-refresh, NBP-state allowance, BIF busy, UVD busy, MC SRBM busy, MC allow, SMU busy, MBUS2 active, VCE busy, and AZ busy.
- Fast-exit and entry-mode fields.
- `ENABLE_DS` at bit 31.

`SCLK_DEEP_SLEEP_CNTL2` at lines 5051-5082 extends the busy-mask set with RLC, HDP, ROM, IH semaphore, PDMA, IDCT, SDMA, DC/AZ, ACP stutter permission, UVD/VCE/SAM clock-gating status, RLC GFXCLK-off, shallow divider, and in/out cushion fields.

`SCLK_DEEP_SLEEP_CNTL3` at lines 5083-5114 maps `GRBM_0` through `GRBM_15` SMU busy-mask bits. This pairs with the graphics throttling vote fields earlier in the chunk and lets firmware/driver policy decide which graphics blocks block SCLK deep-sleep entry.

`SCLK_DEEP_SLEEP_MISC_CNTL` at lines 5115-5124 adds DPM and OCP divider controls, including OCP enable and deep/shallow sleep divider IDs. `SCLK_MIN_DIV` at lines 5201-5204 defines fractional and integer minimum SCLK divider fields.

### LCLK Deep Sleep Controls

`LCLK_DEEP_SLEEP_CNTL` at lines 5125-5134 mirrors the basic deep-sleep shape for link clock: divider ID, ramp disable, hysteresis, reserved bits, and `ENABLE_DS`.

`LCLK_DEEP_SLEEP_CNTL2` at lines 5135-5180 contains link/PCIe-oriented masks and wake state fields. It covers RFE, BIF LCLK busy, L1/L2 IMU idle signals, SCLK running, SMU busy, multiple PCIe LCLK idle lines, inbound/outbound wake and wake-ack signals, DMA activity, RLC GFXCLK-off, and reserved high bits. These fields are part of the condition set that gates LCLK deep-sleep entry and exit.

### Profile, ULV, and LCAC Controls

`TARGET_AND_CURRENT_PROFILE_INDEX_1` at lines 5181-5196 packs current and target indices for VDDCI, MVDD, VDDC, and PCIe profile levels. Each index is a 4-bit nibble. Driver or firmware code can use this register to observe transition state between current and requested power/voltage/PCIe profiles.

`CG_ULV_PARAMETER` at lines 5197-5200 defines the Ultra Low Voltage threshold and its unit. This is clock-gating/power-management policy input rather than persistent software state.

The `LCAC_*` registers at lines 5205-5276 define threshold controls and full-width override select/value registers for SX0, memory-controller channels MC0 through MC3, and CPL. Each `*_CNTL` register uses a consistent field layout:

- enable bit at bit 0,
- threshold at bits 16:1,
- block ID at bits 21:17,
- signal ID at bits 29:22.

The override select/value registers are 32-bit wide fields. These definitions are likely used by low-current/activity counter or clock/activity classification logic where a selected block/signal pair is compared against a threshold, with optional override behavior.

### ROM and SMC Indirect Access

Lines 5277-5456 describe ROM-side control and data registers:

- `ROM_SMC_IND_INDEX` and `ROM_SMC_IND_DATA` provide full-width indirect SMU/ROM address/data fields.
- `ROM_CNTL` controls SCK overwrite, ROM clock gating, chip-select setup/hold timing, and SCK prescalers for reference and crystal clocks.
- `PAGE_MIRROR_CNTL` controls page mirror base address, invalidation, enable, and usage.
- `ROM_STATUS` exposes the `ROM_BUSY` bit.
- `CGTT_ROM_CLK_CTRL0` provides ROM clock-gating on-delay, off-hysteresis, and soft override bits.
- `ROM_INDEX`, `ROM_DATA`, and `ROM_START` expose indexed ROM access fields.
- `ROM_SW_CNTL`, `ROM_SW_STATUS`, and `ROM_SW_COMMAND` define software-command sizing, return-data enable, done status, instruction, and address fields.
- `ROM_SW_DATA_1` through `ROM_SW_DATA_64` are full-width payload/result words.

These macros support command-style ROM access paths. The implicit control flow lives in consumers: program command/data/control fields, start or issue the transaction, poll `ROM_BUSY` or `ROM_SW_DONE`, then read data payload registers. This header only provides the field encodings for those steps.

### Tail Status Bits

At lines 5457-5460, `CURRENT_PG_STATUS` exposes VCE and UVD power-gating status masks. Unlike most fields in this chunk, these two masks do not include companion shift macros in the covered range. `SMC_SYSCON_MISC_CNTL__pre_fetcher_en` then defines a single prefetcher enable bit and shift before the header closes at line 5462.

## APIs, Types, and Functions

This chunk defines no callable APIs, C types, inline helpers, enums, or data structures. The exported interface is the macro namespace itself. The naming convention is the API contract:

- `<REGISTER>__<FIELD>_MASK` gives the bit mask for a field.
- `<REGISTER>__<FIELD>__SHIFT` gives the field shift.
- Full-width data fields use mask `0xffffffff` and shift `0x0`.

The macros are intended to be included by AMDGPU/SMU C code that knows the target ASIC generation. They must not be interpreted independently of the matching register-offset header and the register access domain for the target block.

## Control Flow

There is no direct control flow in the header. The hardware workflows implied by the fields are:

- Frequency transition setup: enable or disable per-block throttling votes in `CG_FREQ_TRAN_VOTING_*` registers.
- Deep-sleep policy setup: program dividers, hysteresis, enable bits, and busy-mask bits for SCLK and LCLK deep sleep, then hardware/SMU logic uses live block activity to enter or exit low-power states.
- Profile tracking: read current/target profile nibbles to observe voltage and PCIe power-state transitions.
- ROM access: program index/command/data registers, wait for busy/done status, and read back payload words.

All sequencing, synchronization, timeout handling, and read/modify/write preservation must be implemented by the caller.

## State and Persistence Behavior

The macros describe memory-mapped hardware register state. Any persistence is hardware/firmware persistence, not software persistence. Writes to these fields change volatile ASIC state and may be reset by GPU reset, suspend/resume, power-gating transitions, firmware reinitialization, or driver reprogramming.

Several fields affect persistent behavior while the GPU is powered:

- `CG_FREQ_TRAN_VOTING_*` fields influence which blocks can block or request throttled frequency transitions.
- SCLK/LCLK deep-sleep enable, divider, hysteresis, and mask fields affect low-power entry/exit behavior until reprogrammed.
- ROM timing and command fields affect active ROM transactions and clocking.
- LCAC threshold/override fields change activity/threshold classification for selected blocks/signals.

Because these are shared hardware registers, callers must preserve unrelated bits and account for firmware ownership. Blind writes can corrupt adjacent fields in the same register.

## Dependencies and Integration Points

Primary dependencies are:

- Matching SMU 7.0.1 register offset/default headers in the same AMDGPU ASIC register tree.
- AMDGPU register access helpers for SMU, MMIO, and indexed/indirect register spaces.
- SMU firmware/power-management code that owns clock-gating, dynamic power management, deep sleep, ULV, profile transition, and ROM access policy.
- Display, UVD, VCE, SDMA, ACP, BIF/PCIe, RLC, GRBM, and memory-controller blocks whose busy, idle, or vote signals are named by the masks.

Integration is low-level and hardware-facing. Higher layers should not depend on literal mask values; they should use these macros through the normal AMDGPU field helpers so ASIC-specific layout stays localized to generated register headers.

## Risks and Edge Cases

- Generated-header drift: if this mask header and the corresponding offset/default headers come from different register database revisions, callers can write correct-looking bitfields to the wrong addresses or wrong bit positions.
- Read/modify/write hazards: many registers pack unrelated controls into one word. Updating one field without preserving the others can disable deep sleep, alter ROM timing, or change vote eligibility for unrelated hardware blocks.
- Reserved bits: `LCLK_DEEP_SLEEP_CNTL` and `LCLK_DEEP_SLEEP_CNTL2` expose reserved masks. Software should avoid using reserved ranges as writable policy fields unless the ASIC programming guide requires a specific value.
- Busy-mask polarity mistakes: fields named `*_BUSY_MASK_MASK` or `*_IDLE_MASK_MASK` are easy to misread. Enabling a mask generally changes whether that signal participates in low-power gating decisions; it is not the same as reporting the live busy/idle state.
- ROM command timeout risk: consumers using `ROM_BUSY` or `ROM_SW_DONE` need bounded polling. A bad command size, address, timing value, or clock-gating override can leave firmware/software waiting on hardware status.
- Repeated register layouts: `CG_FREQ_TRAN_VOTING_1` through `_7`, `SCLK_DEEP_SLEEP_CNTL3`, `LCAC_*`, and `ROM_SW_DATA_1` through `_64` are repetitive. Copy/paste or generation errors can be subtle and should be checked mechanically.
- Tail masks without shifts: `CURRENT_PG_STATUS__VCE_PG_STATUS_MASK` and `CURRENT_PG_STATUS__UVD_PG_STATUS_MASK` appear without companion shift macros in this chunk. Callers that expect every field to have both forms need to handle these status bits explicitly or confirm the shift definitions elsewhere.

## Test Signals

Useful validation signals for code that consumes this chunk include:

- Build coverage for AMDGPU configurations that include SMU 7.0.1 headers, catching missing macro names or malformed generated definitions.
- Static checks that each non-status bitfield used by driver code has the expected `_MASK`/`__SHIFT` pair and that `REG_SET_FIELD`/`REG_GET_FIELD` invocations reference the right register namespace.
- Hardware smoke tests around clock/power management: DPM transitions, SCLK/LCLK deep-sleep entry/exit, suspend/resume, display idle/static-screen behavior, and ACPI power-state changes.
- Media and graphics workload tests while deep-sleep/vote fields are active, especially UVD, VCE, SDMA, RLC, and GRBM activity, to catch incorrect busy-mask or vote programming.
- ROM access tests with bounded polling for `ROM_BUSY`/`ROM_SW_DONE`, including readback of indexed/software data paths.
- Register readback or debugfs-style dumps, where available, to confirm programmed masks preserve adjacent fields and reserved bits.
