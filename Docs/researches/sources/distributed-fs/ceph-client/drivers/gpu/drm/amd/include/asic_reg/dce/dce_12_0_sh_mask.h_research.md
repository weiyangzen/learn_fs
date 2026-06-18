# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001537`: lines 1-2510, `Docs/researches/chunks/subset-b-001537_research.md`
- `subset-b-001538`: lines 2511-4961, `Docs/researches/chunks/subset-b-001538_research.md`
- `subset-b-001539`: lines 4962-7315, `Docs/researches/chunks/subset-b-001539_research.md`
- `subset-b-001540`: lines 7316-9643, `Docs/researches/chunks/subset-b-001540_research.md`
- `subset-b-001541`: lines 9644-12065, `Docs/researches/chunks/subset-b-001541_research.md`
- `subset-b-001542`: lines 12066-14850, `Docs/researches/chunks/subset-b-001542_research.md`
- `subset-b-001543`: lines 14851-17344, `Docs/researches/chunks/subset-b-001543_research.md`
- `subset-b-001544`: lines 17345-19846, `Docs/researches/chunks/subset-b-001544_research.md`
- `subset-b-001545`: lines 19847-22341, `Docs/researches/chunks/subset-b-001545_research.md`
- `subset-b-001546`: lines 22342-24835, `Docs/researches/chunks/subset-b-001546_research.md`
- `subset-b-001547`: lines 24836-27328, `Docs/researches/chunks/subset-b-001547_research.md`
- `subset-b-001548`: lines 27329-29825, `Docs/researches/chunks/subset-b-001548_research.md`
- `subset-b-001549`: lines 29826-32324, `Docs/researches/chunks/subset-b-001549_research.md`
- `subset-b-001550`: lines 32325-34820, `Docs/researches/chunks/subset-b-001550_research.md`
- `subset-b-001551`: lines 34821-37188, `Docs/researches/chunks/subset-b-001551_research.md`
- `subset-b-001552`: lines 37189-39651, `Docs/researches/chunks/subset-b-001552_research.md`
- `subset-b-001553`: lines 39652-42116, `Docs/researches/chunks/subset-b-001553_research.md`
- `subset-b-001554`: lines 42117-44587, `Docs/researches/chunks/subset-b-001554_research.md`
- `subset-b-001555`: lines 44588-47203, `Docs/researches/chunks/subset-b-001555_research.md`
- `subset-b-001556`: lines 47204-49875, `Docs/researches/chunks/subset-b-001556_research.md`
- `subset-b-001557`: lines 49876-52500, `Docs/researches/chunks/subset-b-001557_research.md`
- `subset-b-001558`: lines 52501-54982, `Docs/researches/chunks/subset-b-001558_research.md`
- `subset-b-001559`: lines 54983-57512, `Docs/researches/chunks/subset-b-001559_research.md`
- `subset-b-001560`: lines 57513-59880, `Docs/researches/chunks/subset-b-001560_research.md`
- `subset-b-001561`: lines 59881-62207, `Docs/researches/chunks/subset-b-001561_research.md`
- `subset-b-001562`: lines 62208-64603, `Docs/researches/chunks/subset-b-001562_research.md`
- `subset-b-001563`: lines 64604-64798, `Docs/researches/chunks/subset-b-001563_research.md`

## Chunk Research

### subset-b-001537: lines 1-2510

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 1-2510

## Scope

This chunk covers lines 1-2510 of a much larger AMD DCE 12.0 ASIC register mask header. The file is generated-style C preprocessor metadata: it defines bit shifts and masks for fields inside memory-mapped display-controller registers. It contains no functions, no structs, and no executable control flow. Consumers include AMDGPU display code that combines these `__SHIFT` and `_MASK` constants with register address headers and read/modify/write helpers.

## Purpose

The header provides field-level definitions for several DCE display blocks:

- VGA page-address aliases at the start of the display decode space.
- DC performance monitor instances `DC_PERFMON0`, `DC_PERFMON13`, `DC_PERFMON1`, and `DC_PERFMON9`.
- Display PLL and PLL macro register fields, including frequency-control, calibration, observation, update, and reserved PLL macro slots.
- MCIF writeback engines `MCIF_WB0`, `MCIF_WB1`, and `MCIF_WB2`.
- Capture writeback engines `CWB0` and `CWB1`.
- Main display decode VGA, legacy indexed VGA registers, D1-D6 VGA routing controls, PHY PLL pixel-clock resync controls, DCCG clock controls, pin straps, display-stream DTO, audio DTO, and the beginning of `DCE_VERSION`.

Each register field is represented by a pair such as `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`. Driver code can write a field by clearing `FIELD_MASK`, shifting a value by `FIELD__SHIFT`, and ORing it back into the register value.

## Important Macro Families

The first address blocks define `dispdec_VGA_MEM_WRITE_PAGE_ADDR` and `dispdec_VGA_MEM_READ_PAGE_ADDR`, each with page 0 and page 1 fields at shifts `0x0` and `0x10` and 10-bit masks. Later, equivalent unprefixed `VGA_MEM_WRITE_PAGE_ADDR` and `VGA_MEM_READ_PAGE_ADDR` macros appear in the main `dce_dc_dispdec` block.

The repeated `DC_PERFMON*` blocks expose the same performance-monitor register layout for several monitor instances. The key fields are:

- `PERFCOUNTER_CNTL`: event selection, counted-value selector, increment mode, hardware/run-enable controls, count-off selection, restart, interrupt enable/status behavior, active bit, interrupt type, and counter selector.
- `PERFCOUNTER_CNTL2`: counted-value type and hardware stop selectors.
- `PERFCOUNTER_STATE`: eight packed counter state fields and selector bits.
- `PERFMON_CNTL` and `PERFMON_CNTL2`: monitor state, report count, count-off interrupt enable/status/ack, clock enable, and start/stop run-enable selectors.
- `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW`: interrupt status/ack bits and counter-value readout fields.

The `PPLL_*` display PLL block defines analog and timing controls. Notable groups include `PPLL_FREQ_CTRL0/1/2/3` for fractional and integer frequency control words, denominator, slew, refclk divider, VCO pre-divider, fractional-N enable, spread-spectrum enable, frequency jump enable, TDC resolution, and DPLL config bits. `PPLL_CAL_CTRL`, `PPLL_LOOP_CTRL`, `PPLL_REFCLK_CNTL`, `PPLL_CLKOUT_CNTL`, `PPLL_OBSERVE0/1`, and `PPLL_UPDATE_CNTL` cover calibration, loop behavior, reference selection, output clocks, observability, lock/update state, and ready/pending bits. `PLL_MACRO_CNTL_RESERVED0` through `PLL_MACRO_CNTL_RESERVED41` are full-width reserved register masks.

The `MCIF_WB0`, `MCIF_WB1`, and `MCIF_WB2` sections define identical writeback buffer-manager layouts per engine. They include software control, current-line/status registers, pitch, four buffer status pairs, arbitration, SCLK/NB P-state watermark controls, luma/chroma buffer address and offset fields, VCE lock/interrupt/slice-size control, QoS, clock gating, warm-up, self-refresh, and luma/chroma sizes. Buffer status fields track active/locked/overflow/disable/mode/tag/next-buffer/field/current-line and long-line, short-line, and frame-length errors.

The `CWB0` and `CWB1` sections define capture writeback formatting and validation fields: enable, output color depth, zero padding, chroma swap, 4:2:2 luma/chroma swap, 4:4:4 rounding, pack format, output/error dimensions, CRC enable/continuous/source controls, CRC masks, and CRC result counters.

The main `dce_dc_dispdec` block includes VGA render, sequencer reset, mode, surface, memory base, HDP, cache, per-display `D1VGA_CONTROL` through `D6VGA_CONTROL`, VGA status/interrupt/clear registers, test/QoS controls, legacy VGA indexed register windows, DAC registers, source selection, PHY PLL pixel-clock resync controls for PHY PLL A-E, DCFEV pixel-rate controls, symbol-clock enables, DPREF/REF/DSI clock-gating controls, DCCG performance clock enables, CBUS write-command delay, display/audio straps, display-stream DTO and control registers, symbol-clock G enable, DPREF source control, AOM clock enables, and audio DTO2 phase/modulo.

## APIs, Types, and Functions

There are no callable APIs, C types, or function definitions in this chunk. The exported surface is entirely preprocessor constants. The naming convention is the effective API:

- `REGISTER__FIELD__SHIFT` gives the bit offset.
- `REGISTER__FIELD_MASK` gives the already-positioned bit mask.
- Register names are grouped by address-block comments, which connect the masks to companion register-address headers.

Because these macros are global C preprocessor symbols, correctness depends on exact names matching the rest of AMDGPU's generated register database and display driver helper macros.

## Control Flow

This chunk has no runtime branches or loops. The operational control flow is in callers that use these constants for register programming. Typical caller flow is:

1. Read a MMIO register by its address macro.
2. Clear one or more `*_MASK` fields.
3. Shift new field values with matching `*__SHIFT` constants.
4. Write the updated value back to hardware.
5. For status/interrupt registers, read fields such as `*_STATUS`, write ack/clear bits, or poll ready/pending fields.

The order-sensitive behavior is therefore external to this header, but several fields imply hardware sequences: PLL update locking/pending/ready, perfmon interrupt ack, MCIF buffer-manager lock/interrupt ack, VGA status clear, pixel-clock enable/resync, and DCCG DTO enable/status.

## State and Persistence

The header itself stores no software state. Its constants describe persistent hardware state held in display-controller registers until changed by MMIO writes, reset, power management, or firmware/hardware side effects. Important state domains visible in this chunk are:

- Performance-monitor configuration, counters, interrupt status, and readback values.
- PLL frequency, calibration, reference-clock, post-divider, lock, observation, and update-pending state.
- MCIF writeback buffer ownership, current buffer, line counters, overrun/error state, address fences, QoS/watermarks, and clock/self-refresh policy.
- CWB output format, frame fence dimensions, and CRC accumulation/results.
- VGA mode/routing/status/interrupt state across up to six display pipes.
- DCCG clock enable, source selection, DTO phase/modulo, hardware calibration, and clock-gating delay state.

Some macros represent write-one-to-ack or write-one-to-clear style bits by name, such as `*_INT_ACK`, `VGA_STATUS_CLEAR__*`, and `PPLL_OBSERVE0__pw_pc_clear_sticky_lock`. Caller code must follow register semantics from the hardware spec; this header only provides bit positions.

## Dependencies and Integration Points

This header depends only on the C preprocessor and include guards. It is integrated through the AMDGPU/DRM display stack under `drivers/gpu/drm/amd/include/asic_reg/dce`, typically alongside companion headers that define register offsets and base addresses for the same DCE 12.0 blocks. It is intended for low-level display code, including:

- Register accessor helpers that accept register address, mask, and shift definitions.
- Display clock and PLL programming paths.
- VGA compatibility setup and teardown paths.
- Writeback/capture setup, interrupt handling, and diagnostics.
- Performance-monitor setup and counter collection.
- ASIC-specific display initialization and power-management code.

The repeated instance prefixes (`DC_PERFMON0`, `DC_PERFMON1`, `DC_PERFMON9`, `DC_PERFMON13`, `MCIF_WB0`, `MCIF_WB1`, `MCIF_WB2`, `CWB0`, `CWB1`) are integration signals: callers select an engine instance by choosing the corresponding macro family.

## Risks

The main risk is silent hardware misprogramming. A wrong mask or shift compiles cleanly but can modify reserved bits, target the wrong subfield, leave stale state uncleared, or break timing-sensitive display hardware.

Generated-name consistency is also critical. Many blocks are repeated with near-identical layouts; copy or generation errors between instances could cause one engine to use another engine's field names or masks. Macros such as `*_MASK_MASK` are syntactically awkward but intentional for fields whose names end in `_MASK`; reviewers should not "clean them up" without checking all users.

Full-width masks such as `0xFFFFFFFFL` for address, DTO, reserved, and counter fields make width and type assumptions visible. Callers using narrower or signed intermediates can truncate values. Conversely, small legacy VGA masks such as `0xFFL`, `0x3FL`, and `0x08L` describe byte-sized indexed register windows and should not be treated as normal 32-bit display registers without the matching access path.

Several fields interact with interrupts, clock gating, and power state. Misuse of `*_INT_ACK`, clock-enable, self-refresh, NB P-state, PLL update, or reset fields can hang polling paths, lose writeback frames, or produce display underflow rather than an immediate software error.

## Test Signals

Useful validation signals are mostly integration and hardware-facing:

- Build coverage for translation units that include `dce_12_0_sh_mask.h`, especially with generated register helper macros.
- Static checks that every `REGISTER__FIELD__SHIFT` has a matching `REGISTER__FIELD_MASK`, and that masks align with shifts and expected field widths.
- Diff checks against the authoritative ASIC register-generation source for DCE 12.0.
- Display smoke tests across modesets, VGA disable/compatibility paths, link bring-up, and pixel-clock changes.
- Perfmon tests that configure counters, read low/high values, and exercise interrupt ack/status fields.
- Writeback tests for MCIF/CWB engines, including buffer rotation, pitch/address setup, overflow detection, CRC result generation, and NB P-state/clock-gating transitions.
- Runtime register readback around PLL update, DCCG DTO enable/status, and MCIF buffer-manager status to verify that programmed fields land in the intended bits.

## Cross-Chunk Notes

This is only the first 2510 lines of a 64798-line header. The final per-file research should reconcile this chunk with later chunks to identify all DCE 12.0 register families, later continuation of `DCE_VERSION`, any additional perfmon/clock/writeback instances, and the terminating include guard.

### subset-b-001538: lines 2511-4961

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 2511-4961

## Purpose

This chunk is a generated AMD DCE 12.0 register shift/mask section. It contains no executable code; it defines preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for memory-mapped display-engine registers. Consumers use these constants with the paired DCE 12.0 register-address headers and AMDGPU/DC register access helpers to compose, read, update, and decode 32-bit MMIO register fields.

The covered range starts at the tail of `DCE_VERSION` and then covers a large block of display clock generator (`DCCG`) and pixel-rate controls, frame buffer compression (`FBC`), display pipe and DSI/DCFEV power gating, display memory interface (`DMIF`) arbitration and buffering, DCI memory/clock/power controls, DVMM page-table and fault controls, DCHUB aperture/status registers, writeback/capture (`WB`/`CNV`) and writeback scaler (`WBSCL`) controls, and the beginning of the display microcontroller (`DMCU`) firmware/RAM/interrupt register block. The chunk ends mid-register at `DMCU_INTERRUPT_TO_UC_EN_MASK__VBLANK3_INT_TO_UC_EN__SHIFT`; the remaining masks and any subsequent DMCU fields must be reconciled with the following chunk.

## Important APIs, Types, and Register Domains

The public API surface is entirely macro names. There are no functions, structs, enums, storage declarations, or inline helpers in this range.

Major macro groups:

- DCE/DCCG timing and clocking: `DCE_VERSION`, `PHYPLLG_PIXCLK_RESYNC_CNTL`, `PHYPLLF_PIXCLK_RESYNC_CNTL`, `PIXCLK0/1/2_RESYNC_CNTL`, `DCCG_GTC_*`, `DENTIST_DISPCLK_CNTL`, `MILLISECOND_TIME_BASE_DIV`, `MICROSECOND_TIME_BASE_DIV`, `DISPCLK_FREQ_CHANGE_CNTL`, `DCCG_PERFMON_CNTL`, `DCCG_GATE_DISABLE_CNTL`, `DCCG_GATE_DISABLE_CNTL2`, `DISPCLK_CGTT_BLK_CTRL_REG`, `SCLK_CGTT_BLK_CTRL_REG`, `SYMCLK_CGTT_BLK_CTRL_REG`, `DCCG_SOFT_RESET`, `SYMCLKA` through `SYMCLKF_CLOCK_ENABLE`, `DCCG_AUDIO_DTO_SOURCE`, `DCCG_AUDIO_DTO0/1_PHASE`, and `DCCG_AUDIO_DTO0/1_MODULE`.
- CRTC and link-rate DTO programming: repeated `CRTC0` through `CRTC5_PIXEL_RATE_CNTL`, `DP_DTO0` through `DP_DTO5_PHASE/MODULO`, and `CRTC0` through `CRTC5_PHYPLL_PIXEL_RATE_CNTL` fields select pixel-rate sources, enable DP DTOs, apply add/drop pixel correction, report DISP output FIFO errors, and select PHYPLL/pixel-rate PLL sources.
- Legacy and panel clock helpers: `MIPI_DTO_*`, `DAC_CLK_ENABLE`, `DVO_CLK_ENABLE`, `DVOACLKC/DVOACLKD_*`, `AVSYNC_COUNTER_*`, `SMU_CONTROL`, `SMU_INTERRUPT_CONTROL`, and `DMCU_SMU_INTERRUPT_CNTL`.
- Frame buffer compression: `FBC_CNTL`, `FBC_IDLE_FORCE_CLEAR_MASK`, `FBC_START_STOP_DELAY`, `FBC_COMP_CNTL`, `FBC_COMP_MODE`, `FBC_IND_LUT0` through `FBC_IND_LUT15`, CSM region offsets, client region masks, `FBC_DEBUG_COMP`, `FBC_MISC`, `FBC_STATUS`, `FBC_ALPHA_CNTL`, and `FBC_ALPHA_RGB_OVERRIDE`.
- Power gating and power interrupts: repeated `PIPE0` through `PIPE5_PG_CONFIG/ENABLE/STATUS`, `DSI_PG_*`, `DCFEV0_PG_*`, `DCFEV1_PG_*`, `DCPG_INTERRUPT_STATUS`, `DCPG_INTERRUPT_CONTROL`, `DCPG_INTERRUPT_CONTROL2`, `DC_IP_REQUEST_CNTL`, and `DC_PGCNTL_STATUS_REG`.
- Display memory interface and arbitration: `DMIFV_STATUS`, `DMIF_CONTROL`, `DMIF_STATUS`, `DMIF_ARBITRATION_CONTROL`, `PIPE0` through `PIPE7_ARBITRATION_CONTROL3`, `DMIF_P_VMID`, `DMIF_ADDR_CALC`, `DMIF_STATUS2`, `PIPE0` through `PIPE7_MAX_REQUESTS`, `LOW_POWER_TILING_CONTROL`, `MCIF_CONTROL`, `MCIF_WRITE_COMBINE_CONTROL`, phase outstanding counters, `CC_DC_PIPE_DIS`, `SMU_WM_CONTROL`, `RBBMIF_TIMEOUT`, `RBBMIF_STATUS`, `RBBMIF_TIMEOUT_DIS`, `RBBMIF_STATUS_FLAG`, and `DMIF_URG_OVERRIDE`.
- DCI clocking, memory power, and reset: `DCI_CLK_CNTL`, `DCI_CLK_CNTL2`, `DCI_MEM_PWR_CNTL`, `DCI_MEM_PWR_CNTL2`, `DCI_MEM_PWR_CNTL3`, `DCI_MEM_PWR_CNTL4`, `DCI_MEM_PWR_STATUS`, `DCI_MEM_PWR_STATUS2`, `DCI_MEM_PWR_STATUS3`, and `DCI_SOFT_RESET`.
- DVMM and DCHUB address translation: `DVMM_REG_RD_STATUS`, `DVMM_REG_RD_DATA`, `DVMM_PTE_REQ`, `DVMM_CNTL`, `DVMM_FAULT_STATUS`, `DVMM_FAULT_ADDR`, `FMON_CTRL`, `DVMM_PTE_PGMEM_CONTROL`, `DVMM_PTE_PGMEM_STATE`, and DCHUB framebuffer, AGP, DRAM aperture, and control/status fields.
- Writeback/capture and scaler: `WB_ENABLE`, `WB_EC_CONFIG`, `CNV_MODE`, `CNV_WINDOW_START`, `CNV_WINDOW_SIZE`, `CNV_UPDATE`, `CNV_SOURCE_SIZE`, `CNV_CSC_*`, `CNV_TEST_*`, `CNV_INPUT_SELECT`, `WB_SOFT_RESET`, `WB_WARM_UP_MODE_CTL1/2`, `WBSCL_COEF_RAM_SELECT`, `WBSCL_COEF_RAM_TAP_DATA`, `WBSCL_MODE`, `WBSCL_TAP_CONTROL`, destination size, horizontal/vertical scale ratios and initial phases, round/clamp, overflow and coefficient-conflict interrupts, outside-pixel strategy, test CRCs, backpressure counter, MCIF backpressure counter, and RAM shutdown.
- Display microcontroller: `DMCU_CTRL`, `DMCU_STATUS`, firmware start/end/ISR/checksum address fields, host access to ERAM/IRAM through `DMCU_RAM_ACCESS_CTRL` plus read/write control/data registers, event trigger bits, `DMCU_UC_INTERNAL_INT_STATUS`, static-screen interrupt control/status, `DMCU_INTERRUPT_STATUS`, `DMCU_INTERRUPT_TO_HOST_EN_MASK`, and the first part of `DMCU_INTERRUPT_TO_UC_EN_MASK`.

## Control Flow and State Behavior

This header has no runtime control flow. The control flow exists in driver consumers that perform read-modify-write sequences against MMIO registers using these shift/mask definitions. The field names reveal several state machines and sequencing contracts:

- Clock changes use toggle/done/status fields such as `DENTIST_DISPCLK_CHGTOG`, `DENTIST_DISPCLK_DONETOG`, `DENTIST_DISPCLK_CHG_DONE`, DP reference clock change bits, and `DISPCLK_FREQ_RAMP_DONE`. Callers must program divider/source fields and then poll or sequence against completion bits.
- Pixel-rate programming is replicated per CRTC. `CRTCn_PIXEL_RATE_SOURCE`, `DP_DTOn_ENABLE`, DTO phase/modulo, add/drop pixel correction, half-rate output, FIFO-error, and error-count fields are tied to mode-set and link-clock programming order.
- Power gating has force-on, gate request, desired state, and PGFSM status fields for pipes, DSI, and DCFEV blocks. Interrupt status/control registers expose power-up/down occurrence, mask, and clear bits, so callers need explicit clear-after-observe behavior.
- FBC state is persistent in hardware until disabled, invalidated, reset, or fault-cleared. Control fields enable compression, select compressor behavior, define memory regions/LUTs, and expose decompression error and enable-status bits.
- DMIF, MCIF, DCI, DVMM, and DCHUB fields control request throttling, VMID assignment, buffer allocation, outstanding request counters, memory power states, address apertures, page-table request generation, fault status, and hub credit errors. Incorrect programming can affect display fetch, writeback, and memory translation across multiple pipes.
- Writeback/capture uses update-lock style fields (`CNV_UPDATE_PENDING`, `CNV_UPDATE_TAKEN`, `CNV_UPDATE_LOCK`), window/source geometry, CSC coefficient registers, scaler coefficient RAM selection/tap data, and CRC/overflow/host-conflict interrupt fields. These are stateful programming surfaces where geometry, filter coefficients, and enable bits should be latched coherently.
- DMCU control includes microcontroller reset/enable, IRQ/XIRQ routing, register-read timeout, firmware address/checksum fields, ERAM/IRAM host access with auto-increment and select bits, event trigger fields, and interrupt occurrence/clear/enable masks. Host code must treat RAM access and interrupt clear bits as register protocol operations, not ordinary RAM variables.

Persistence is hardware-register persistence only. The macros allocate no memory and maintain no software state; after consumers write MMIO registers, the state lives in the display engine until later register writes, resets, power transitions, or firmware actions change it.

## Dependencies and Integration Points

The chunk depends on generated-name compatibility with the rest of `dce_12_0_sh_mask.h` and companion DCE 12.0 register address/offset headers under the AMD ASIC register tree. Numeric values are coupled to AMD DCE 12.0 hardware documentation and to existing AMDGPU/DC register helper conventions that expect `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` names.

Primary integration points:

- AMDGPU display clock and link programming uses the DCCG, DENTIST, DTO, pixel-rate, PHYPLL, symbol-clock, DAC/DVO/MIPI, and AV sync fields during mode set, link bring-up, and display clock changes.
- Power-management paths use SMU, DMCU-SMU, display memory global power request, DCPG interrupt, pipe/DSI/DCFEV power-gate, DCI clock-gate, memory power, and soft-reset fields.
- Plane fetch and memory arbitration use DMIF/MCIF/DCI/DVMM/DCHUB fields for VMID, address aperture, tiling, request bursts, urgent levels, outstanding counters, low-power tiling, page-table requests, memory power state, and fault diagnostics.
- FBC code uses the FBC control/status/misc/LUT/region/alpha fields to enable compression, tune compressor behavior, handle invalidation or decompression faults, and validate enable/compression status.
- Writeback and capture paths use WB/CNV/WBSCL controls for capture enable, crop/window/source geometry, stereo/interlace capture metadata, CSC, scaling coefficients, CRC testing, backpressure counters, and writeback RAM power controls.
- DMCU firmware loading and event handling code uses DMCU reset/enable/status, PC/firmware/checksum registers, IRAM/ERAM host-access fields, event triggers, and interrupt routing/clear masks for microcontroller-managed display features such as ABM/static-screen handling and power-event notification.

## Risks and Edge Cases

- The constants are a hardware ABI. A one-bit shift or mask change can silently corrupt unrelated fields in a shared 32-bit MMIO register.
- Many registers use negative polarity or control-by-disable naming, such as `*_GATE_DISABLE`, `*_MEM_PWR_DIS`, `*_DS_DISABLE`, `DISABLE_IRQ_TO_UC`, and `PSTATE_URGENT_DISABLE`. Call sites must not infer polarity from a generic enable/disable helper without checking field meaning.
- Clear and occurrence bits often share the same bit position and mask, especially in `DMCU_INTERRUPT_STATUS`, `DMCU_UC_INTERNAL_INT_STATUS`, and static-screen interrupt status. Read/modify/write helpers must avoid preserving stale write-one-to-clear bits.
- Interrupt mask fields have repeated names ending in `_MASK_MASK`, for example `DCPG_INTERRUPT_CONTROL__DCFE0_POWER_UP_INT_MASK_MASK` and `DMCU_INTERRUPT_TO_HOST_EN_MASK__..._MASK_MASK`. This is generated but visually error-prone when grepping or wrapping macros.
- Several repeated per-pipe families are not perfectly symmetric across all display blocks. The chunk covers pipes 0-5 for power gating and DMIF buffer controls, pipes 0-7 for some arbitration/max-request/DVMM PTE state fields, and DCFEV/DSI special cases. Generic loops in consumers need validated register lists, not just a pipe count assumption.
- `DCCG_AUDIO_DTO0_MODULE` and `DCCG_AUDIO_DTO1_MODULE` use `MODULE` rather than the more common `MODULO`; this generated spelling must be preserved for source compatibility.
- This range starts after the first `DCE_VERSION__MAJOR_VERSION__SHIFT` line and ends before the full `DMCU_INTERRUPT_TO_UC_EN_MASK` register definition completes. The final merged per-file research should join adjacent chunks before making claims about complete DCE version or DMCU interrupt-to-UC coverage.
- DCHUB aperture, DVMM fault, VMID, and memory-power fields influence memory access behavior. Misprogramming can produce display underflow, stale translations, invalid requests, or faults that look unrelated to the original register write.

## Test Signals

Useful validation is mostly compile-time plus hardware/display behavior:

- Kernel or targeted AMDGPU header builds should catch missing macro names, syntax errors, duplicate definitions, and generated-name drift.
- Static checks can verify that representative shifts/masks match expected bit positions for DCCG clock controls, `CRTCn_PIXEL_RATE_CNTL`, `DCPG_INTERRUPT_CONTROL`, `DMIF_CONTROL`, `DCI_MEM_PWR_CNTL*`, `DVMM_CNTL`, `CNV_UPDATE`, `WBSCL_OVERFLOW_STATUS`, and `DMCU_INTERRUPT_STATUS`.
- Mode-set tests should exercise display clock changes, DP DTO programming, PHYPLL source selection, pixel add/drop correction, and DISP output FIFO error reporting across multiple CRTCs.
- Power-management tests should cover pipe/DSI/DCFEV power gating, DCPG interrupt clear/mask paths, SMU/DMCU static-screen events, clock gating, DCI memory power transitions, and soft resets.
- Memory-fetch and writeback tests should check DMIF buffer allocation/completion, arbitration/urgent settings, VMID/aperture setup, DVMM PTE and fault reporting, DCHUB credit error handling, FBC enable/invalidate/error paths, and MCIF/writeback backpressure counters.
- Capture/scaler validation should cover CNV window/source sizing, CSC coefficients and clamps, update lock/taken/pending sequencing, WBSCL coefficient RAM programming, overflow/host-conflict interrupts, CRC outputs, and scaled writeback image correctness.
- DMCU tests should verify firmware start/checksum programming, ERAM/IRAM host access auto-increment behavior, event trigger delivery, interrupt-to-host and interrupt-to-UC masks, write-one-to-clear interrupt behavior, and register-read timeout reporting.

### subset-b-001539: lines 4962-7315

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 4962-7315

## Scope And Purpose

This chunk is part of AMDGPU's generated DCE 12.0 register shift/mask header. It contains no executable code; it is compile-time hardware register metadata for the display controller engine. Each pair of `__SHIFT` and `_MASK` macros describes how a named bitfield is packed inside a 32-bit display MMIO or indirect register.

The requested range starts in the middle of `DMCU_INTERRUPT_TO_UC_EN_MASK`, then covers DMCU interrupt routing, DMCU scratch/communication registers, BL1 PWM backlight and ABM controls, ABM histogram/luma-statistics registers, DMCU perfmon interrupt routing, Azalia display-audio controller and codec-function registers, audio port-connectivity overrides, GTC group offsets, and the beginning of the DAC/analog output block. It ends inside `DAC_FIFO_STATUS`, before the following `DC_I2C_CONTROL` block.

The path is under a Ceph source mirror, but this file is AMDGPU Linux kernel display-driver metadata. There is no Ceph filesystem logic in this chunk.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or runtime variables in this range. The API surface is the generated macro contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for the field.
- `<REGISTER>__<FIELD>_MASK` gives the raw bit mask for the field in the register.
- Consumers combine these with matching address macros from `dce_12_0_offset.h` and register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_SET_FIELD()`, `REG_GET_FIELD()`, `set_reg_field_value()`, and `get_reg_field_value()`.

The DMCU and ABM-related macros dominate the first half of the chunk. `DMCU_INTERRUPT_TO_UC_EN_MASK` and `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL` describe whether ABM, MCP, DSI/DCFE power, static-screen, external software, and VBLANK events are sent to the display microcontroller and how they map to XIRQ selection bits. The `_1` variants and `DMCU_DPRX_*` families add more interrupt status, enable, and XIRQ-selection layouts for extra static-screen, DPRX, HPD RX, AUX, GPIO, timer, software, and command-complete events. `DMCU_INT_CNT`, `DC_DMCU_SCRATCH`, `DMCU_FW_CHECKSUM_SMPL_BYTE_POS`, and `DMCU_UC_CLK_GATING_CNTL` define counters, scratch storage, firmware-checksum byte sampling, and microcontroller IRAM/ERAM read-delay or clock-gating fields.

The master/slave communication-port registers are byte-sliced. `MASTER_COMM_DATA_REG1` through `REG3`, `MASTER_COMM_CMD_REG`, `MASTER_COMM_CNTL_REG`, `SLAVE_COMM_DATA_REG1` through `REG3`, `SLAVE_COMM_CMD_REG`, and `SLAVE_COMM_CNTL_REG` expose four byte fields per data/command register plus interrupt and "message to host in progress" control bits. These fields back firmware/driver mailbox-style communication with the display microcontroller.

The backlight and ABM families include `BL1_PWM_AMBIENT_LIGHT_LEVEL`, `BL1_PWM_USER_LEVEL`, `BL1_PWM_TARGET_ABM_LEVEL`, `BL1_PWM_CURRENT_ABM_LEVEL`, `BL1_PWM_FINAL_DUTY_CYCLE`, `BL1_PWM_MINIMUM_DUTY_CYCLE`, `BL1_PWM_ABM_CNTL`, `BL1_PWM_BL_UPDATE_SAMPLE_RATE`, and `BL1_PWM_GRP2_REG_LOCK`. They describe ambient/user/target/current/final/minimum brightness levels, ABM PWM enable, graduated-step timing, update-sample rate, and group register locking.

`DC_ABM1_*` fields describe the adaptive backlight module's control, coefficient selection, ambient contrast enhancement offsets/slopes/thresholds, luma-statistics and histogram outputs, sample rates, shift metadata, overscan pixel value, master lock, and read-progress state. The chunk includes luma sum, min/max, filtered min/max, pixel count, overscan-bin, threshold, min/max pixel-value counts, and 24 histogram result registers.

The Azalia block covers display audio control and codec metadata. `AZALIA_CONTROLLER_CLOCK_GATING`, `AZALIA_AUDIO_DTO`, `AZALIA_AUDIO_DTO_CONTROL`, `AZALIA_SOCCLK_CONTROL`, several DMA-control registers, `AZALIA_RIRB_AND_DP_CONTROL`, cyclic-buffer position/sync, global capabilities, payload capabilities, stream-arbiter control, input/output CRC controls/results, and memory power-control/status define the controller-side audio transport, clocking, DMA, CRC, and memory power-gating layout. `AZALIA_F0_CODEC_*` macros define vendor/device/revision IDs, channel count, resync FIFO control, supported rates and formats, power states, power-state control, reset, subsystem ID response, and converter synchronization for codec function 0.

The final portion starts the DAC/analog-output register set. `DAC_ENABLE`, `DAC_SOURCE_SELECT`, CRC control/signature registers, sync tristate control, stereosync select, autodetect controls/status/interrupt, forced output data, powerdown and control bits, comparator enable/output, power control, DFT config, and the first `DAC_FIFO_STATUS` fields describe analog-output enablement, test/CRC diagnostics, load detect, forced output, per-channel power, comparator state, and FIFO calibration/status fields.

## Control Flow

This chunk has no local control flow. Runtime behavior is determined by distant display-driver code that includes `dce_12_0_offset.h` and `dce_12_0_sh_mask.h`, builds ASIC-specific register tables, and then reads or writes hardware registers through the DAL/DC register helper layer.

A typical consumer sequence is:

1. Select the DCE 12.0 register offset from `dce_12_0_offset.h`.
2. Read a register with `REG_READ`, direct MMIO helpers, or an indirect accessor such as the Azalia endpoint path.
3. Extract a field with the generated mask and shift, or through `REG_GET`/`get_reg_field_value`.
4. Update one or more fields with the generated mask and shift, usually through `REG_SET`, `REG_UPDATE`, `REG_SET_FIELD`, or `set_reg_field_value`.
5. Write the packed value back to the hardware register in the ordering required by the display block, firmware mailbox, audio endpoint, or power-management path.

Observed integration patterns in the tree include DCE 12.0 code including this header in `dce120_timing_generator.c`, `dce120_hwseq.c`, `dce120_resource.c`, `irq_service_dce120.c`, and DCE 12.0 GPIO translation/factory code. The common audio implementation in `display/dc/dce/dce_audio.c` uses register/mask/shift tables and indirect Azalia endpoint reads/writes, while DCE 12.0 resource construction provides the corresponding mask/shift values for newer ASIC-specific instances.

Because the file is macro-only, a wrong definition does not fail locally. It changes the behavior of later driver flows: interrupt routing to DMCU, backlight/ABM programming, firmware communication, Azalia audio setup, audio DMA/CRC/memory power behavior, codec capability exposure, analog DAC load detection, and DAC diagnostic reads.

## State And Persistence Behavior

The header itself stores no state and has no persistence. It describes state held in display-controller hardware registers, firmware-visible mailboxes, counters, or status latches. The persistence lifetime is controlled by hardware, firmware, suspend/resume, display reinitialization, power gating, hotplug events, link/audio stream setup, and ASIC reset.

State categories in this chunk include:

- DMCU interrupt routing and status: enable, XIRQ selection, and status bits decide which display events are delivered to the microcontroller and host-visible paths.
- DMCU communication state: scratch, master/slave data bytes, command bytes, interrupt bits, and host-message progress bits carry mailbox payloads and synchronization status.
- Backlight and ABM state: PWM brightness levels, final/minimum duty, ABM enable, step timing, sample rates, locks, ambient/contrast coefficients, luma statistics, pixel counts, histogram bins, and overscan values represent both programmed policy and measured display content.
- Perfmon and DPRX interrupt state: per-monitor interrupt status, mask, and routing fields report and gate performance, AUX/HPD, GPIO, timer, software, and command-completion events.
- Azalia audio state: clock gating, DTO phase/module values, SOCCLK control, DMA engine status, RIRB/DP control, cyclic buffer position/sync, capabilities, stream payload limits, CRC captures, memory power state, and codec function identity/capability/power/reset fields.
- DAC state: analog source selection, CRC mode/results, sync tristate, autodetect mode/status/interrupt, forced output, per-channel powerdown, comparator references/outputs, power-control mode, DFT config, and FIFO calibration/status.

The macros do not encode access semantics. Field names alone do not say whether a bit is read-only, sticky, write-one-to-clear, self-clearing, firmware-owned, safe only while a block is disabled, or latched on specific frame boundaries. Consumers must rely on ASIC programming guides and existing display-driver sequencing.

## Dependencies And Integration Points

This header depends on the generated AMD register-header layout. The matching DCE 12.0 address definitions live in `dce_12_0_offset.h`; this `*_sh_mask.h` file supplies the field layout inside those addresses.

Primary integration points are:

- DCE 12.0 resource initialization, where register addresses, masks, and shifts are assembled into per-block tables for timing generators, link encoders, audio objects, memory input, IRQ service, GPIO, and hardware sequencing.
- The display register helper layer in `reg_helper.h`, which expects the `__SHIFT` and `_MASK` naming convention used here.
- DMCU firmware loading and control paths, including DMCU ERAM/IRAM firmware IDs tracked by AMDGPU firmware and PSP/SMU code, and DMCU mailbox-style master/slave communication registers.
- Backlight and adaptive backlight management paths that consume BL1 PWM and `DC_ABM1_*` fields to program brightness policy, content statistics, histogram reading, and lock/update behavior.
- IRQ service and static-screen/DPRX/AUX/HPD paths that consume interrupt status, mask, and XIRQ-selection fields.
- Display audio resource and codec programming. DCE audio code uses Azalia endpoint index/data registers for indirect codec-function programming, and DCE 12.0 resources provide compatible field masks for Azalia DTO, DMA, capabilities, CRC, memory power, and codec metadata.
- Analog output and diagnostic paths for DAC enable/source selection, CRC signatures, autodetect/load-detect, forced output, comparator state, powerdown, DFT, and FIFO calibration.

The DMCU, ABM, audio, and DAC blocks cross subsystem boundaries. DMCU settings interact with firmware, ABM interacts with panel/backlight policy, Azalia interacts with DRM audio/HDMI/DP stream setup, and DAC fields interact with legacy analog encoder and load-detection behavior.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A one-bit mask or shift error can corrupt adjacent fields during read-modify-write, route interrupts to the wrong destination, misread sticky status, or expose incorrect audio/display capabilities.

High-risk fields include DMCU interrupt enables and XIRQ selections, master/slave communication interrupt and progress bits, ABM group locks, backlight target/current/final/minimum duty fields, histogram/luma result fields, Azalia DMA controls, cyclic-buffer sync, memory power control/status, codec power/reset fields, and DAC autodetect/powerdown/forced-output controls. Errors in these areas can present as missed display firmware events, stuck mailbox transactions, flickering or incorrect backlight levels, failed ABM updates, missing HDMI/DP audio, DMA/RIRB failures, incorrect codec enumeration, failed analog load detection, or damaged diagnostics.

Repeated byte-sliced and interrupt-family definitions are vulnerable to generated-copy mistakes. The communication registers repeat four byte fields at shifts `0x0`, `0x8`, `0x10`, and `0x18`; status/mask/XIRQ families repeat the same event ordering across several registers. A suffix or bit-position mismatch would compile cleanly and only fail when that event or byte lane is used.

Some fields have paired enable/value semantics. Examples include clock gating enable/state, ABM enable plus timing/level fields, DAC CRC enable plus control and signature masks, autodetect mode plus status/ack/interrupt enable, and connectivity override-enable plus connectivity value. Writing the value field without the enable field, or enabling an override with stale data, can produce misleading behavior.

Firmware and hardware ownership boundaries are important. DMCU scratch/communication, ABM statistic/result, perfmon status, Azalia DMA/status, and DAC FIFO/autodetect fields may be updated asynchronously by hardware or firmware. Callers need appropriate polling, locking, interrupt acknowledgement, and frame/update ordering; this generated header does not provide those rules.

The requested range starts after the first `DMCU_INTERRUPT_TO_UC_EN_MASK` shift definitions have already begun and ends immediately before the next register block after `DAC_FIFO_STATUS`. The merge lane should treat both as chunk-boundary artifacts, not as absent definitions in the full file.

## Test Signals

Useful validation is mostly build-time plus hardware/display behavior:

- AMDGPU display builds that include DCE 12.0 headers should compile without unresolved mask/shift names in DCE 12.0 timing generator, hardware sequencing, resource, IRQ, GPIO, and GMC/display paths.
- Register table initialization should populate DCE 12.0 mask/shift structures with the expected field names for audio, IRQ, timing, link, and memory-input code.
- DMCU firmware loading and mailbox communication should complete without stuck master/slave interrupt or "message in progress" states.
- ABM/backlight testing should show stable brightness transitions, correct minimum/final duty behavior, correct ambient/user/target/current levels, and plausible luma/histogram statistics across static and changing content.
- Static-screen, VBLANK, DPRX, AUX, HPD, GPIO, timer, software, perfmon, and command-complete interrupt tests should show expected status, mask, and routing behavior without missed or spurious events.
- HDMI/DP audio testing should enumerate the expected codec identity/capabilities, program supported formats/rates, keep audio DMA/cyclic-buffer state sane, and preserve audio across modeset, hotplug, suspend/resume, and clock/power-gating transitions.
- Azalia CRC and memory-power tests should produce stable CRC results and avoid underflow, RIRB/CORB, or BDL DMA faults when streams start and stop.
- Analog DAC tests, where hardware supports them, should validate source selection, forced output, CRC signatures, autodetect/load status, comparator outputs, per-channel powerdown, and FIFO calibration/status behavior.

Regression symptoms from incorrect constants include black screens after firmware/display setup, no backlight or unstable brightness, missed DMCU/ABM interrupts, stuck firmware mailboxes, missing HDMI/DP audio devices, audio stream underflows, incorrect codec power state, false DAC connect status, failed analog detection, wrong CRC diagnostics, or FIFO calibration status being read from the wrong bits.

## Cross-Chunk Notes

Earlier lines in `dce_12_0_sh_mask.h` define preceding display-controller fields and the beginning of the first DMCU interrupt mask register. Later lines continue from `DAC_FIFO_STATUS` into the DCE I2C and subsequent display register families. The final per-file report should describe this file as generated AMDGPU DCE 12.0 register metadata rather than algorithmic driver code.

### subset-b-001540: lines 7316-9643

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 7316-9643

## Purpose

This chunk is a generated AMD DCE 12.0 display-engine register shift/mask header segment. It contains no executable C logic; its public surface is a dense set of `#define` constants named as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. Driver code uses these symbols to compose, update, and decode memory-mapped display-controller registers without embedding raw bit positions or masks directly at call sites.

The assigned range starts in the tail of the `DAC_FIFO_STATUS` field definitions and then covers the main DCE display I2C/DDC control block, generic I2C access, display interrupt status continuation banks, DCO/DCIO power-clock-reset controls, display-output PHY link routing, panel power sequencing and backlight PWM registers, global swaplock/genlock routing, GPU timer readback, external VSYNC routing, and the beginning of DCIO/UNIPHY/AUX impedance calibration fields. The chunk ends mid-register at `DCIO_IMPCAL_CNTL_CD__IMPCAL_ARB_STATE__SHIFT`; the matching masks and any later calibration fields are owned by the next chunk.

The constants are hardware ABI definitions. Their purpose is to preserve exact bitfield layout for the DCE 12.0 ASIC register interface used by AMDGPU display code.

## Important APIs, Types, and Register Domains

There are no functions, structs, typedefs, or runtime APIs in this chunk. The important API surface is the generated macro namespace consumed by AMDGPU/DC register helpers. Every register field generally appears as a pair:

- `*_SHIFT`: the starting bit position for a field.
- `*_MASK`: the full pre-shifted mask used to isolate or update the field.

Major register domains in this range:

- `DAC_FIFO_STATUS`: tail fields for FIFO overwrite level, calibrated average/min/max level, calibration status, and force-recalibration/recompute bits. The chunk begins after the first few `DAC_FIFO_STATUS` shift definitions, so the full register definition spans the previous chunk and this one.
- `DC_I2C_*`: display-controller I2C engine control, arbitration, interrupt control, software status, DDC hardware status, bus speed/setup for DDC1-DDC6 and DDCVGA, multi-transaction descriptors, data FIFO/index access, EDID detect control, and read-request interrupt bits.
- `GENERIC_I2C_*`: a parallel generic I2C engine with control, interrupt, status, speed/setup, transaction, data, and pin-selection fields.
- `DCO_SCRATCH0` through `DCO_SCRATCH7`: raw 32-bit scratch registers represented by full-width value masks.
- `DCE_VCE_CONTROL`: VCE clock gating and display/VCE memory request behavior.
- `DISP_INTERRUPT_STATUS` and `DISP_INTERRUPT_STATUS_CONTINUE*`: display interrupt summary/status banks, including continuation-chain bits. These cover CRTC/vblank/vline/snapshot/trigger interrupts, SCL mode changes, blender underflows, DIG/DP fast-training and stream-disable events, HPD and HPD RX events, AUX software/light-sleep/GTC sync events, performance monitor counter interrupts, CWB buffer-manager interrupts, static-screen interrupts, generic DCO/PSP interrupts, and HDCP/AUX register-ready interrupts.
- `DCO_MEM_PWR_STATUS`, `DCO_MEM_PWR_STATUS1`, `DCO_MEM_PWR_CTRL`, and `DCO_MEM_PWR_CTRL2`: memory power status and light-sleep/shutdown/force controls for I2C, MVP, DPA-DPG, HDMI0-HDMI6, DMIF pipe memories, MCIF writeback memories, DCRX, and DCFEV memories.
- `DCO_CLK_CNTL`, `DCO_CLK_CNTL2`, and `DCO_CLK_CNTL3`: clock enable/disable and power-domain controls for display blocks such as DCO, DPP, DMIF, DCF, FBC, GPIO, HDCP, I2C, DCI, DCCG, ABM, APG, BLND, CWB, MCIFWB, DCRX, DCFEV0/1, and SCLV.
- `DCO_POWER_MANAGEMENT_CNTL`, `DCO_SOFT_RESET`, `DIG_SOFT_RESET`, and `DIG_SOFT_RESET_2`: power-management guard and soft reset controls for DCO, DCO performance, DIGA-DIGG, DP AUX engines, DCO audio, DCO memory power FSM, DCFEV front ends, DPREF clocking, and PHY-specific digital paths.
- `DCO_STEREOSYNC_SEL`, `DCO_DCFE_EXT_VSYNC_CNTL`, `DC_GENERICA`, `DC_GENERICB`, `DCIO_GSL_*`, and `DC_GPU_TIMER_*`: synchronization, generic interrupt, swaplock/genlock/GSL, CRTC external VSYNC, and GPU-timer start/readback bitfields.
- `FMT_MEMORY0_CONTROL` through `FMT_MEMORY5_CONTROL`: per-formatter memory power status, shutdown control, and light-sleep disable controls.
- `UNIPHYA_LINK_CNTL` through `UNIPHYG_LINK_CNTL` and matching `*_CHANNEL_XBAR_CNTL`: per-UNIPHY link controls for pixel-valid reset, minimum low duration, per-channel inversion, lane-stagger delay, HPD-mask based link enable, channel crossbar lane source selection, and link enable.
- `DCIO_WRCMD_DELAY`, `DC_DVODATA_CONFIG`, `DC_PAD_EXTERN_SIG`, `DC_REF_CLK_CNTL`, `DC_GPIO_DEBUG`, and `DCIO_CLOCK_CNTL`: write-command delay tuning, DVO/VIP alternate mapping, external-pad signal select, reference-clock gating, GPIO debug routing, and DCIO test-clock/gating fields.
- `LVTMA_PWRSEQ_*` and `BL_PWM_*`: embedded panel/power-sequencer controls for target state, DIGON/SYNCEN/BLON polarity and override, power-up/down delay programming, reference dividers, PWM duty/period, PWM enable, and group register lock/update behavior.
- `DCIO_SOFT_RESET` and `DCIO_DPHY_SEL`: resets for UNIPHY/DSYNC A-G, DAC, DCRXPHY, DPHY, ZCAL, LPA/LPB paths, plus DPHY lane source selection.
- `UNIPHY_IMPCAL_LINKA/B/C/D`, `UNIPHY_IMPCAL_PERIOD`, `UNIPHY_IMPCAL_PSW_AB`, `AUXP_IMPCAL`, `AUXN_IMPCAL`, `DCIO_IMPCAL_CNTL`, and partial `DCIO_IMPCAL_CNTL_CD`: impedance calibration enable/status/error/override/step-delay/value controls for UNIPHY and AUX pads, calibration period and power-switch values, global calibration soft reset/status/arbitration state, and AUX calibration interval.

## Control Flow and State Behavior

This header has no direct control flow. The effective flow is in consumers that use these symbols with MMIO helpers to perform read-modify-write updates, poll status bits, or acknowledge hardware events.

Stateful hardware behavior encoded by the masks includes:

- I2C/DDC transaction sequencing: `DC_I2C_CONTROL__DC_I2C_GO`, `*_SOFT_RESET`, `*_SEND_RESET`, `*_SW_STATUS_RESET`, DDC selection, transaction count, transaction start/stop/read/write/count fields, and indexed data access describe how software stages I2C transactions and starts hardware execution.
- I2C ownership and arbitration: `DC_I2C_ARBITRATION` fields distinguish software and DMCU ownership requests/done signals, software priority, queued-go behavior, and software/hardware transfer aborts.
- I2C completion/error state: software and hardware status fields expose done, aborted, timeout, interrupted, overflow, NACK, request, urgent, EDID detect status, number of valid detect tries, and EDID detect state. These are read by polling paths and interrupt handlers.
- Interrupt aggregation: `DISP_INTERRUPT_STATUS*` fields form a chained summary tree. The continuation bit at bit 31 in many banks indicates another status register has active bits, so interrupt walkers must follow the chain rather than checking only the root register.
- Power and clock state: memory power status and control fields track or force light sleep/shutdown for DCO sub-block memories. Clock-control bits enable, disable, or power down display sub-block clocks. These are persistent hardware states until rewritten or reset by power-management paths.
- Reset sequencing: DCO, DIG, and DCIO soft reset fields can hold sub-blocks in reset. Callers must assert and release them in hardware-defined order around PHY/link/power transitions.
- Link routing and lane state: UNIPHY channel crossbar and inversion fields persistently define how logical lanes map to physical channels, which links are enabled, and whether HPD masking participates in link enable. These values are central to connector bring-up.
- Panel sequencing and backlight PWM: LVTMA and BL PWM fields describe staged panel power-up/power-down, backlight enable, override, polarity, duty cycle, period, and double-buffered update locking. `BL_PWM_GRP1_REG_UPDATE_PENDING` is a latch/status signal for safe brightness updates.
- Synchronization and timing: genlock/swaplock/GSL select fields, external VSYNC mux fields, GPU timer start-position fields, and CRTC manual-flow-control bits determine how display pipes synchronize timing, flips, and timer capture.
- Impedance calibration: UNIPHY/AUX calibration fields initiate calibration, report calout/error status, acknowledge error, set step delays, override measured values, and choose calibration targets. These influence electrical characteristics and must be managed with reset/PHY state.

Persistence is entirely in hardware registers after driver writes. The macros themselves have no memory ownership, allocation, locking, I/O, or persistent on-disk state.

## Dependencies and Integration Points

This chunk has no `#include` dependencies and no standalone compile unit. It depends on generated register-address headers for the matching DCE 12.0 register offsets and on the companion enum/value headers for legal field encodings. It is tightly coupled to the AMD DCE 12.0 hardware specification and to AMDGPU display code that uses generated `*_SHIFT`/`*_MASK` names in register-programming macros.

Expected integration points include:

- Display I2C/DDC and EDID probing code uses `DC_I2C_*`, `GENERIC_I2C_*`, and DDCVGA/DDC1-DDC6 speed/setup/status fields for monitor detection, EDID reads, AUX/DDC fallback paths, and DMCU/software arbitration.
- Interrupt handlers and diagnostics use `DISP_INTERRUPT_STATUS*` fields to route vblank/vline, CRTC trigger, underflow, HPD, AUX, DP, performance monitor, CWB, HDCP, static-screen, PSP, and generic interrupt events.
- Display power-management and clock-gating code uses `DCO_MEM_PWR_*`, `DCO_CLK_CNTL*`, `DCO_POWER_MANAGEMENT_CNTL`, formatter memory controls, and DCO/DCIO reset registers during suspend/resume, mode set, idle gating, and hardware bring-up.
- Link encoder and PHY setup code uses `UNIPHY*_LINK_CNTL`, `UNIPHY*_CHANNEL_XBAR_CNTL`, `DCIO_SOFT_RESET`, `DIG_SOFT_RESET*`, `DCIO_DPHY_SEL`, `DCIO_WRCMD_DELAY`, and impedance calibration fields during DisplayPort/HDMI/eDP link initialization.
- Panel/backlight code uses `LVTMA_PWRSEQ_*`, `BL_PWM_*`, and `DC_REF_CLK_CNTL` to sequence embedded panel power and apply backlight updates.
- Multi-display synchronization and flip-timing code uses `DCO_STEREOSYNC_SEL`, `DCIO_GSL_*`, `DCO_DCFE_EXT_VSYNC_CNTL`, and `DC_GPU_TIMER_*`.
- Debug and firmware/secure-processor paths can consume DCO scratch registers, DCO generic interrupt message/clear fields, DCO PSP interrupt status/clear, GPIO debug selection, and VCE/display memory request controls.

## Risks and Edge Cases

- Bit masks and shifts are hardware ABI. Any numeric change can silently program the wrong register bits even if the kernel still compiles.
- The chunk boundaries are not semantic boundaries. `DAC_FIFO_STATUS` starts in the previous chunk, and `DCIO_IMPCAL_CNTL_CD` continues in the next chunk. Per-file synthesis must merge adjacent chunks before treating either register family as complete.
- Many repeated register families differ only by instance number, for example DDC1-DDC6, DIGA-DIGG, DPA-DPG, CRTC1-CRTC6, UNIPHYA-UNIPHYG, HDMI0-HDMI6, and DCFE0-DCFE5. Mechanical copy errors in generated headers or hand edits could map a field to the wrong instance while preserving a plausible mask pattern.
- Interrupt continuation bits use bit 31 in many status registers. Interrupt handling that ignores continuation bits can miss events in later banks; code that assumes every bit is a leaf event can misinterpret the continuation flag.
- Some status names encode historical spelling from hardware documentation, such as `OCCURED`. These names should not be corrected locally unless all generated headers and call sites are regenerated together.
- Mask polarity is not uniform. Fields named `*_MASK`, `*_DIS`, `*_GATE_DIS`, `*_LIGHT_SLEEP_DIS`, `*_FORCE`, `*_OVRD`, and `*_ACK` have different semantics even though they are all represented as masks. Callers must follow the register meaning, not infer boolean polarity from the C macro pattern.
- I2C arbitration exposes software and DMCU ownership. Incorrect request/done ordering or failure to abort/reset on error can stall EDID/DDC access or conflict with firmware.
- Panel power and backlight controls have ordering requirements outside this header. Misprogramming target state, delay fields, polarity, or override bits risks blank panels, flicker, or unsafe panel sequencing.
- Clock, memory power, and soft reset controls are cross-domain. Gating or resetting an active block can cause underflows, link loss, stuck interrupts, or failed resume.
- Impedance calibration override and error acknowledgement fields affect PHY electrical behavior. Forced override values or mishandled calibration errors can produce marginal DisplayPort/HDMI/AUX signaling.
- Full-width masks such as scratch registers, timer reads, calibration periods, and I2C data/count fields need correct value range validation at call sites; the header only exposes field layout.

## Test Signals

Useful validation is mainly compile-time plus hardware-facing display behavior:

- Kernel build or targeted header inclusion should catch syntax errors, duplicate macro definitions, and missing generated identifiers used by AMDGPU/DC code.
- Static checks can compare selected `*_SHIFT` and `*_MASK` pairs against expected DCE 12.0 register documentation, especially for repeated DDC, interrupt, UNIPHY, and power-control families.
- EDID/DDC tests should cover DDC1-DDC6 and DDCVGA selection, normal read completion, NACK handling, timeout handling, software status reset, transaction chaining, and arbitration with firmware/DMCU users.
- Hotplug and AUX/DP tests should verify HPD, HPD RX, AUX SW done, AUX LS done, AUX GTC sync lock/error, DP fast-training complete, and DP stream-disable interrupt reporting through the continuation chain.
- Display mode-set and page-flip tests should exercise vblank/vline, CRTC trigger/snapshot/force-count interrupts, blender underflow status, GPU timer start/readback, external VSYNC routing, genlock/swaplock, and GSL selections.
- Suspend/resume and runtime power-management tests should inspect DCO memory power status, light-sleep/shutdown force bits, clock gating controls, formatter memory controls, and soft reset sequencing.
- Embedded panel tests should validate LVTMA power-up/down delays, DIGON/SYNCEN/BLON state, PWM period/duty programming, frame-start update behavior, and backlight group-lock update pending behavior.
- Link bring-up tests should cover UNIPHY lane crossbar/inversion programming, link-enable behavior, DCIO/DIG soft resets, DPHY lane selection, and UNIPHY/AUX impedance calibration status/error handling.

### subset-b-001541: lines 9644-12065

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 9644-12065

## Scope And Purpose

This chunk is a generated AMDGPU DCE 12.0 register field mask/shift header. It contains no executable C code; it publishes preprocessor constants that describe bit positions and bit masks for display-controller MMIO registers. Consumers combine these field macros with address macros from `dce_12_0_offset.h` and register helper macros to read, write, or update specific fields on DCE 12.0/Vega-era display hardware.

The requested range begins in the middle of the UNIPHY impedance-calibration table and then covers several display I/O domains:

- UNIPHY impedance calibration for links E/F, impedance calibration control for the E/F link pair, and calibration pulse-width fields for C/D and E/F link pairs.
- Low-power UNIPHY link controls and channel crossbar controls for `UNIPHYLPA` and `UNIPHYLPB`.
- DCIO DPCS TX/RX interrupt field definitions and DCIO semaphore fields.
- A large GPIO section for generic pins, DVO data/control/clock pins, DDC1-DDC6, DDCVGA, sync, genlock/swaplock, HPD, power-sequencing pins, pad strength, I2C pads, I2S/SPDIF pins, TX12/RX enable controls, and AUX/HPD analog pad controls.
- DSI/DAC/DPHY macro control and reserved fields.
- DPRX AUX receiver/transmitter controls, DMCU interrupt status/ack fields, indexed AUX/EDID/DPCD/message/KSV buffers, message pending flags, and scratch registers.
- DPRX DPHY DPCD-facing link-training fields, lane quality status, readiness/lock/alignment status, per-lane error thresholds and counters, block-symbol error counters, lane setup, dynamic deskew, bypass, and internal reset controls.

The path is under a local `ceph-client` mirror, but this specific file is AMDGPU Linux kernel display-driver hardware metadata. It does not define Ceph filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, or runtime APIs in this chunk. The exported API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the raw 32-bit field mask, typically with an `L` suffix.
- `<REGISTER>` names correspond to MMIO addresses defined in the companion `dce_12_0_offset.h`, for example `mmDC_GPIO_DDC1_A`, `mmDPRX_AUX_CONTROL`, or `mmDPRX_DPHY_INT_RESET`.

The UNIPHY/DCIO portion defines fields for `UNIPHY_IMPCAL_LINKE`, `UNIPHY_IMPCAL_LINKF`, `DCIO_IMPCAL_CNTL_EF`, `UNIPHY_IMPCAL_PSW_EF`, `UNIPHYLPA_LINK_CNTL`, `UNIPHYLPB_LINK_CNTL`, `UNIPHYLPA_CHANNEL_XBAR_CNTL`, `UNIPHYLPB_CHANNEL_XBAR_CNTL`, `DCIO_DPCS_TX_INTERRUPT`, `DCIO_DPCS_RX_INTERRUPT`, and `DCIO_SEMAPHORE0` through `DCIO_SEMAPHORE7`. These cover calibration enable/status/override values, low-power link enablement, pixel-valid reset and lane inversion/stagger controls, channel source muxing, and interrupt type/mask/occur bits for TX/RX PHY lanes.

The GPIO macros form a repeated register-family contract:

- `*_MASK` registers expose software mask and pull-down or receiver controls.
- `*_A` registers expose pin assignment/alternate-function selection bits.
- `*_EN` registers expose output-enable or function-enable bits.
- `*_Y` registers expose output value/readback fields.

This pattern appears for `DC_GPIO_GENERIC_*`, `DC_GPIO_DVODATA_*`, `DC_GPIO_DDC1_*` through `DC_GPIO_DDC6_*`, `DC_GPIO_DDCVGA_*`, `DC_GPIO_SYNCA_*`, `DC_GPIO_GENLK_*`, `DC_GPIO_HPD_*`, `DC_GPIO_PWRSEQ_*`, `DC_GPIO_I2CPAD_*`, and `DC_GPIO_I2S_SPDIF_*`. Additional GPIO control registers include pad drive strength (`DC_GPIO_PAD_STRENGTH_1`, `DC_GPIO_PAD_STRENGTH_2`, `DC_GPIO_I2CPAD_STRENGTH`, `DC_GPIO_I2S_SPDIF_STRENGTH`, `DVO_STRENGTH_CONTROL`), DVO reference/skew controls, `DC_GPIO_TX12_EN`, `DC_GPIO_RXEN`, `PHY_AUX_CNTL`, `AUXI2C_PAD_ALL_PWR_OK`, `DC_GPIO_PULLUPEN`, and `DC_GPIO_AUX_CTRL_0` through `DC_GPIO_AUX_CTRL_6`.

The DPRX AUX macros describe a DisplayPort receiver AUX engine: `DPRX_AUX_REFERENCE_PULSE_DIV`, `DPRX_AUX_CONTROL`, `DPRX_AUX_HPD_CONTROL1/2`, `DPRX_AUX_RX_STATUS`, `DPRX_AUX_RX_ERROR_MASK`, DPHY TX/RX timing controls, DPHY TX/RX status, DMCU hardware interrupt status and ack fields, CPU-to-DMCU and DMCU-to-CPU interrupt handshakes, and indexed storage/data ports for AUX, EDID, DPCD, messages, and KSV values.

The DPRX DPHY macros describe receiver-side DisplayPort link-training and error-monitoring surfaces: DPCD lane count, training pattern and MST enable fields; per-lane link-quality set/status fields; ready, comma lock, symbol recovery lock, interlane alignment, FIFO level, and wait-count fields; per-lane symbol/disparity/test-pattern error thresholds and counters; block-symbol interval/cp error counters; lane map/inversion fields; LFSR/error-correction controls; enhanced framing, MTP header count force, dynamic deskew match/control data, deskew bypass, and broad internal reset bits for lane align, static/dynamic deskew, 8b/10b decoder, lane count, inversion, lane reversal, enable, control, training, header parse, and SDOUT logic.

## Control Flow

This chunk has no runtime control flow. Every line is a `#define` that supplies a constant.

The runtime control flow is in consumers that include this header. DCE120 GPIO code shows the common pattern:

1. Include `dce_12_0_offset.h` for `mm<REGISTER>` addresses and `dce_12_0_sh_mask.h` for the field masks.
2. Compose an MMIO address through the local `REG(reg_name)` macro, which adds the SOC base segment from `vega10_ip_offset.h` to `mm<REGISTER>`.
3. Store or compare field masks such as `DC_GPIO_DDC1_A__DC_GPIO_DDC1DATA_A_MASK`, `DC_GPIO_HPD_A__DC_GPIO_HPD1_A_MASK`, or `DC_GPIO_GENLK_A__DC_GPIO_GENLK_CLK_A_MASK`.
4. Let generic register helper code perform field extraction or read-modify-write using the selected register address, mask, and shift metadata.

In `display/dc/gpio/dce120/hw_translate_dce120.c`, `offset_to_id()` maps `DC_GPIO_*_A` offsets and masks back to logical `GPIO_ID_*` and enum values. `id_to_offset()` maps logical DDC data/clock, generic, HPD, sync, and genlock/swaplock IDs to `DC_GPIO_*_A` offsets and matching field masks. It then derives the companion Y/EN/MASK offsets by adding or subtracting from the selected `*_A` register, relying on the generated address and field layout being regular.

In `display/dc/gpio/dce120/hw_factory_dce120.c`, the same mask header initializes `hpd_sh_mask`, `ddc_shift`, and `ddc_mask` tables through `HPD_MASK_SH_LIST()` and `DDC_MASK_SH_LIST()`. Those tables are handed to hardware GPIO/DDC/HPD objects so higher-level display code can manipulate pins without hard-coding bit positions.

For the AUX and DPRX DPHY sections, expected runtime flows are hardware and firmware oriented: program AUX timing/control fields, inspect RX/TX status, handle DMCU interrupt status/ack fields, index AUX/EDID/DPCD/message buffers, program link-training-visible DPCD fields, and read or clear receiver PHY error counters and alignment/deskew status. This header only supplies the bitfield constants; protocol sequencing lives in display core, firmware-facing DMCU code, or hardware initialization paths outside this chunk.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. It describes hardware-backed state in display MMIO registers.

The represented hardware state includes:

- Calibration state: UNIPHY impedance calibration enable/status/error, calibration values, overrides, pulse-width values, and arbitration state.
- Link and PHY state: low-power link enablement, channel inversion/crossbar selection, DPCS interrupt status/masks, and per-lane TX/RX interrupt occurrence bits.
- GPIO pin state: mux/assignment bits, mask bits, output enables, output/readback values, pull-down/pull-up controls, receiver enables, HPD and AUX analog pad filter/slew/bias controls, and drive-strength settings.
- DSI/DAC/DPHY macro state: DSI dual control and many reserved macro-control slots.
- DPRX AUX state: AUX/HPD control, RX/TX PHY timing and status, error masks, DMCU interrupt status/ack/mask bits, indexed AUX/EDID/DPCD/message/KSV storage, scratch registers, and pending flags.
- DPRX DPHY state: link-training-visible DPCD values, MST enable, lane quality pattern state, ready/lock/alignment status, error thresholds, sticky or sampled error counters, clear bits, lane mapping/inversion, deskew configuration, enhanced-frame state, and reset/bypass controls.

Persistence depends on the register and power domain. Control settings generally remain until another driver/firmware write, display engine reset, PHY reset, suspend/resume transition, power-gating transition, or full GPU reset. Status bits may reflect current hardware state, sampled state, sticky interrupt status, or write-one-to-clear/acknowledge behavior. The mask header does not encode access direction, reset defaults, self-clearing behavior, volatile status timing, or reserved-bit write requirements.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register header contract. It is normally paired with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h`, which defines the corresponding `mm<REGISTER>` address and `mm<REGISTER>_BASE_IDX` constants.
- DCE120 display code using SOC base offsets from `soc15_hw_ip.h` and `vega10_ip_offset.h`.
- AMD display register helpers such as `reg_helper.h`, plus block-specific register list headers such as `hpd_regs.h` and `ddc_regs.h`.

Direct include points for `dce_12_0_sh_mask.h` in this source tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_translate_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_factory_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c`

The strongest visible integration in this chunk is the DCE120 GPIO layer. `hw_translate_dce120.c` uses the GPIO field masks to translate between raw register/mask pairs and logical DDC, HPD, generic, sync, and genlock/swaplock pin identifiers. `hw_factory_dce120.c` packages generated masks and shifts into DDC and HPD hardware objects. Higher layers then use these objects for EDID/DDC communication, hotplug detection, connector routing, and display pin control.

The UNIPHY, AUX, and DPRX DPHY constants integrate with display link bring-up, DisplayPort AUX and link-training behavior, DMCU/firmware interrupt routing, debug/status collection, and receiver-side test or validation modes. Some macros may be unused in this Linux tree while still reflecting fields present in AMD's generated ASIC register database.

## Risks And Edge Cases

The main risk is silent bitfield drift. A wrong mask or shift compiles cleanly but causes consumers to read or write the wrong field in a live hardware register. For GPIO/DDC/HPD paths, that can mean the wrong pin is selected, an output is enabled unexpectedly, HPD detection is masked or filtered incorrectly, AUX/DDC pad mode is misprogrammed, or EDID reads fail.

The GPIO section has dense repeated patterns with small differences between DDC instances, HPD instances, generic pins, and companion `MASK/A/EN/Y` registers. Copy or generator mistakes are easy to miss by inspection. DCE120 translation code also assumes that for a selected `*_A` offset, the matching `*_Y`, `*_EN`, and `*_MASK` registers are at `+2`, `+1`, and `-1`; bad address or mask definitions break that abstraction.

Fields whose semantic names include `MASK` can produce confusing macro names such as `DC_GPIO_HPD_MASK__DC_GPIO_HPD1_MASK_MASK` or `DCIO_DPCS_TX_INTERRUPT__DCIO_DPCS_TXA_INT_MASK_MASK`. The first `MASK` is part of the hardware register or field name, while the second `_MASK` is the generated bit-mask suffix. Reviewers and manual patches must preserve this distinction.

Control and status semantics are not represented here. Many fields are likely write-one-to-clear, sticky status, read-only, self-clearing reset, reserved, or power-domain-sensitive. Using only the presence of a `_MASK` macro to infer writable behavior is unsafe.

The AUX/DPRX and DPHY sections include protocol-sensitive state. Incorrect AUX timing, DMCU interrupt ack/mask handling, DPCD indexed-buffer access, lane count/training pattern fields, deskew controls, or error counter clear bits can break DisplayPort receiver behavior, diagnostics, or firmware handshakes. Reset fields in `DPRX_DPHY_INT_RESET` cover many sub-blocks and could disrupt link recovery if toggled out of sequence.

The chunk boundary starts immediately after `DCIO_IMPCAL_CNTL_CD` masks and continues with `UNIPHY_IMPCAL_PSW_CD`, so the preceding lines in an earlier chunk define the matching `DCIO_IMPCAL_CNTL_CD` shifts. The range also ends in the middle of the `DPRX_DPHY_INT_RESET` field list, before later lines continue with remaining masks and threshold-exceeded status registers. The merge lane should treat these as chunk boundaries, not file-level omissions.

## Test Signals

Useful validation is mostly compile-time plus hardware display behavior:

- AMDGPU/DCE120 builds should compile without missing field definitions in all direct include sites.
- Generated-register validation can compare every field mask and shift in this chunk against AMD's source register database and confirm each field has the expected companion address in `dce_12_0_offset.h`.
- GPIO translation tests should verify DDC1-DDC6, DDCVGA, I2C pad, HPD1-HPD6, generic GPIOs, sync, and genlock/swaplock mappings round-trip through offset/mask to logical ID and back.
- EDID/DDC tests should cover all exposed DDC lines and the DDCVGA/I2C-pad paths because their field masks and offsets are selected from this chunk.
- Hotplug tests should watch HPD assertion/deassertion, interrupt masking, glitch filtering/slew settings, suspend/resume, and multi-monitor connector combinations.
- DisplayPort AUX tests should cover successful AUX transactions, timeout/error paths, HPD IRQ behavior, DMCU interrupt status/ack handling, and indexed AUX/DPCD/EDID/message buffer accesses.
- Link-training or receiver diagnostics should monitor DPRX DPHY ready, comma/SR lock, interlane alignment, lane-quality pattern detect, symbol/disparity/test-pattern counters, block-symbol interval errors, and clear-bit behavior.
- Low-power and reset tests should exercise display suspend/resume, link disable/enable, UNIPHY calibration state, DPRX DPHY reset fields, and AUX/HPD pad power controls.

Regression symptoms from bad constants include blank displays, failed EDID reads, hotplug storms or missed HPD events, AUX timeouts, incorrect DDC line selection, broken genlock/swaplock pins, unexpected GPIO output drive, DisplayPort link-training failures, persistent receiver error counts, failed recovery after reset, or failures that appear only on a specific connector, lane count, or DDC/HPD instance.

## Cross-Chunk Notes

Earlier chunks of `dce_12_0_sh_mask.h` define preceding DCE 12.0 display-controller field masks and the start of the UNIPHY impedance-calibration area. Later chunks continue after `DPRX_DPHY_INT_RESET` with the remaining DPRX DPHY status/interrupt masks and the rest of the generated display register-field namespace. The final per-file research should present the complete file as generated AMDGPU DCE 12.0 register mask/shift metadata rather than as algorithmic driver logic.

### subset-b-001542: lines 12066-14850

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 12066-14850

## Purpose

This chunk is a generated AMD DCE 12.0 shift/mask header section. It contains no executable driver logic; it publishes preprocessor constants that describe bit positions and packed masks for display-controller MMIO registers. Consumers combine these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` values with register offsets from the companion `dce_12_0_offset.h` file and with AMD display register helpers such as `REG_UPDATE`, `REG_SET`, and read/modify/write wrappers.

The range begins at a chunk boundary inside the `DPRX_DPHY_INT_RESET` register, carrying the final reset masks for `HEADERPARSE_RESET` and `SDOUT_RESET`. It then covers several DCE 12.0 display and audio hardware areas:

- DisplayPort receiver DPHY threshold/error/lock/align/deskw status fields.
- DCRX clock gating, soft reset, light sleep, test clock, clock enable, and a large reserved PHY macro range.
- I2S/SPDIF audio control, status, and CRC-test registers.
- Azalia/HD-audio stream, endpoint, and input-endpoint indexed register windows.
- The first DCP0 display controller pipe register block, including graphics surface format, tiling, addresses, update/flip, prescale, CSC, gamut, dithering, cursor, LUT, CRC, PTE, GSL, regamma, alpha, XDMA recovery/underflow, and surface counters.
- The beginning of the LB0 line-buffer block through buffer urgency control.

Although the repository path is under a `ceph-client` source tree mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph filesystem behavior, storage replication, network messaging, or distributed state management.

## Important APIs, Types, And Constants

There are no C functions, structs, enums, global variables, or runtime types in this chunk. The public API is the generated macro namespace:

- `REGISTER__FIELD__SHIFT` gives the bit offset for a field.
- `REGISTER__FIELD_MASK` gives the already-shifted bit mask for that field.
- Names ending in `_MASK_MASK` are legitimate generated constants for hardware fields whose field name is `*_MASK`; they are not duplicate-mask typos.
- Full-register reserved/spare fields use `0xFFFFFFFFL` masks, for example `DPRX_DPHY_SPARE__DPHY_SPARE_MASK`, `DCRX_PHY_MACRO_CNTL_RESERVED*__DCRX_PHY_MACRO_CNTL_RESERVED_MASK`, and `ZCAL_MACRO_CNTL_RESERVED*__ZCAL_MACRO_CNTL_RESERVED_MASK`.

Important macro families in this range include:

- `DPRX_DPHY_*_STATUS`: status/ack/mask fields for BS interval error threshold, symbol error threshold, disparity error threshold, test-pattern error threshold, SR lock detection, loss of align, loss of deskew, excessive error, and deskew FIFO overflow. These follow a repeated flag/ack/mask layout, with `DETECT_SR_LOCK_STATUS` also exposing a type bit.
- `DCRX_*`: gate-disable fields for DCRX display and symbol clocks, soft-reset fields for display/symbol/ref/S clocks, light-sleep disable fields for AUX and DPRX, display-clock gate delay fields, the `DCRX_SYMCLK_RX_P_ENABLE` clock enable bit, test-clock select/invert fields, and hundreds of reserved PHY macro control slots.
- `I2S*` and `SPDIF*`: control and status fields for two I2S and two SPDIF paths, including word size, sample alignment/order, LRCLK polarity, word alignment, enable, FIFO start address, stream audio enable/idle/data-ready/sample-rate status, and CRC-test enable/reset/continuous/sample-count/data fields.
- `CRC_I2S_CONT_REPEAT_NUM` and `CRC_SPDIF_CONT_REPEAT_NUM`: repeat-count fields used by continuous CRC-test modes.
- `AZF0STREAM[0-15]_*`: indexed Azalia stream access windows with an 8-bit register index, a write-enable bit, and 32-bit data.
- `AZF0ENDPOINT[0-7]_*` and `AZF0INPUTENDPOINT[0-7]_*`: indexed Azalia codec endpoint and input-endpoint access windows with 14-bit index fields and 32-bit data fields.
- `DCP0_GRPH_*`: graphics enable, keyer alpha selection, scanout depth/format/tiling/swizzle, surface addresses and high address bits, pitch, viewport offsets/start/end, update locks, update pending/taken status, flip timing, DFQ controls/status, page-flip interrupts, compression surface metadata, outstanding request limits, XDMA flip and cache-underflow controls, and surface-counter fields.
- `DCP0_*COLOR*`, `DCP0_*CSC*`, `DCP0_*GAMMA*`, `DCP0_*LUT*`, and `DCP0_*DITHER*`: input/output color pipeline fields for prescale, input CSC, output CSC, common matrix transforms, denorm, output rounding/clamp, key ranges, degamma, gamut remap, spatial dithering, DC LUT access/autofill/control/offsets, DCP CRC, and A/B regamma curve programming.
- `DCP0_CUR_*`: cursor enable/mode/2x magnification, pitch, line-per-chunk, address, size, high address, position, hot spot, color, update lock/pending/taken flags, request filter, and stereo cursor controls.
- `DCP0_DVMM_PTE_*`: page-table/cache policy and arbitration fields for display virtual memory/PTE behavior.
- `DCP0_DCP_GSL_CONTROL`: global swap lock group, master, enable, reset-delay, and check-all-fields behavior.
- `LB0_LB_*`: line-buffer data format, memory sizing/partition/configuration, desktop height, vline/vline2 windows, vertical counters, vblank/vline interrupt masks and status/ack bits, sync reset selection/delay/duration, black/keyer colors, keyer replacement colors, buffer level status, and buffer urgency thresholds.

## Control Flow

This header has no runtime control flow. Every line is a compile-time `#define` mapping a hardware field name to a numeric bit shift or mask.

Runtime behavior appears in AMD display code that includes `dce_12_0_sh_mask.h`, especially the DCE 12.0 resource and timing-generator paths under `drivers/gpu/drm/amd/display/dc/dce120/`. A typical use sequence is:

1. A DCE 12.0 component selects a register offset from `dce_12_0_offset.h`, often through a generated register-list macro such as memory-input, transform, timing-generator, audio, AUX, or hardware-sequencer register tables.
2. The same component stores matching shift and mask values from this header in per-block tables, for example `MI_DCE12_MASK_SH_LIST(__SHIFT)`, `MI_DCE12_MASK_SH_LIST(_MASK)`, `XFM_COMMON_MASK_SH_LIST_SOC_BASE(__SHIFT)`, and `XFM_COMMON_MASK_SH_LIST_SOC_BASE(_MASK)`.
3. Driver code converts DRM/DC state into hardware field values, then uses register helpers to clear and insert only the relevant field bits.
4. Hardware latches the resulting register state immediately, at a display update boundary, on a page flip, after an ACK/clear write, or after block-specific reset/power sequencing.

Examples visible in the tree show this contract directly. `dce120_resource.c` builds DCE 12.0 shift/mask tables for transforms and memory inputs. `dce_transform.h` consumes fields from this chunk such as `LB0_LB_DATA_FORMAT`, `LB0_LB_MEMORY_CTRL`, clamp, dithering, gamut, output CSC, and regamma fields. `dce_mem_input.c` uses DCE 12.0 `DCP0_GRPH_CONTROL` masks to program GFX9 scanout swizzle, bank count, shader-engine count, pipe count, color expansion, and shader-engine enable.

Several register groups imply hardware control sequences even though this file does not implement them. Azalia stream/endpoint registers use an index/data access pattern. Audio CRC-test registers are configured, optionally reset, then observed through CRC data fields. Graphics updates can be locked, queued, taken on retrace, or forced immediate depending on `DCP0_GRPH_UPDATE` and `DCP0_GRPH_FLIP_CONTROL`. Cursor and LUT updates have pending/taken or indexed-write semantics. Interrupt/status registers expose occurrence/status, mask, ack, clear, or type bits that must be handled in the correct order by callers.

## State And Persistence Behavior

The macros do not store state and do not persist anything. They describe state held in DCE 12.0 hardware registers after other driver code writes those registers.

Hardware state represented by this chunk includes:

- DP receiver DPHY error, lock, alignment, deskew, excessive-error, FIFO-overflow, ack, and interrupt-mask state.
- DCRX power/clock/reset state, including clock-gate disable, light-sleep disable, soft reset, symbol-clock enable, test-clock routing, and reserved PHY macro configuration.
- Audio interface state for I2S/SPDIF formatting, enablement, FIFO placement, status, sample-rate observation, and CRC-test collection.
- Azalia stream/endpoint indexed register state for HDMI/DP audio codec programming.
- Display pipe scanout state: graphics enable, pixel depth/format, tiling/swizzle, surface addresses, pitch, viewport, compression metadata, update locks, flip controls, page-flip interrupt state, and outstanding request limits.
- Color pipeline state: prescale, input/output CSC matrices, common matrices, denorm, rounding, clamp, keying, degamma, gamut remap, spatial dithering, LUT contents/control, CRC configuration, regamma LUT/curve A and B programming, and alpha/cursor blending.
- Cursor state: surface address, format/mode, size, position, hot spot, colors, update synchronization, filter mode, and stereo behavior.
- Display VM/PTE arbitration and cache policy state.
- GSL synchronization state for coordinated flips or reset/update behavior.
- XDMA recovery, cache-underflow count/status/ack/mask, flip timeout, average delay, and graphics surface counter state.
- LB0 line-buffer configuration, interrupt masks/status, sync-reset controls, key colors, buffer levels, and urgency thresholds.

Persistence is register-specific. Control values generally remain until overwritten, reset, power-gated, or restored during modeset/suspend/resume/GPU-reset handling. Status and interrupt bits may be sticky until ACK or clear bits are written. Indexed data windows persist in their underlying audio/LUT/register files rather than in the index selector alone. Update-pending/taken and FIFO/reset-ack fields are transient reflections of hardware progress. This generated header does not encode read-only, write-one-to-clear, self-clearing, double-buffered, reserved, or power-domain semantics; consumers must know those rules from the ASIC programming model and existing AMD display code.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header ecosystem:

- The surrounding `dce_12_0_sh_mask.h` include guard and earlier/later field definitions in the same file.
- Register offsets and base indices in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h`.
- DCE 12.0 display code under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/`, including resource construction, timing generation, hardware sequencing, audio, AUX/I2C, transforms, and memory-input programming.
- Shared DCE display helper headers such as `dce_transform.h`, `dce_mem_input.c`, and related `REG_UPDATE`/field-table macros that expect each field to have both shift and mask constants.
- Vega-era display and graphics tiling conventions. The DCP0 graphics-control fields include GFX9-style swizzle, bank, shader-engine, pipe, and color-expansion fields, so they integrate with DC tiling information and framebuffer scanout setup.
- Audio-over-display paths. I2S/SPDIF and Azalia indexed fields feed HDMI/DisplayPort audio programming, status, and CRC diagnostics.
- Interrupt and validation paths for page flip, vline/vblank, DP receiver errors, line-buffer status, XDMA underflow/timeout, and CRC/test-pattern diagnostics.

The most direct source-tree consumers found for this DCE generation are the DCE 12.0 resource pool and timing-generator code. They include `dce_12_0_offset.h` and `dce_12_0_sh_mask.h`, build register/shift/mask tables, and then hand those tables to common DCE components. The same audio mask-list convention is reused by newer DCN resource files for common audio fields, so some DCE 12.0 audio definitions serve as a shared compatibility contract beyond the original DCE 12.0 resource path.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These constants are plain integers, so an incorrect shift or mask can compile cleanly and still corrupt an adjacent field, leave a field unchanged, or target the wrong hardware behavior.

Specific risk areas:

- The requested range begins mid-register. The first two macros are only the tail of `DPRX_DPHY_INT_RESET`; per-file reconciliation must combine them with the previous chunk before reasoning about the complete reset register.
- Status registers often combine occurrence/status, ACK, interrupt, type, clear, and mask bits. Confusing `*_ACK`, `*_CLEAR`, and `*_MASK` fields can lose events, leave interrupts storming, or hide important DP/graphics/LB/XDMA faults.
- Field names ending in `_MASK_MASK`, such as `DCP0_GRPH_XDMA_FLIP_TIMEOUT__GRPH_XDMA_FLIP_TIMEOUT_MASK_MASK`, represent the mask bit of a hardware field named `...MASK`. Scripts or reviewers should not collapse or rename them.
- Many masks use high bits, including `0x80000000L` and other upper-half values. Callers should compose values with unsigned 32-bit arithmetic to avoid sign-extension or overflow surprises.
- DCRX clock-gate, light-sleep, and soft-reset fields can disable or reset active display receiver clocks. Incorrect sequencing can break AUX/DPRX behavior, interrupt reporting, or link recovery.
- Reserved PHY/ZCAL macro control fields are wide writable-looking fields. Production code should not invent writes to these reserved locations without an AMD programming sequence or hardware documentation.
- DCP0 graphics-control fields are tightly tied to framebuffer layout. Bad depth, format, swizzle, bank, shader-engine, pipe, address-translation, privilege, pitch, or surface-address values can cause corrupted scanout, memory faults, display underflow, or blank output.
- Surface address fields are split between low and high registers, with low addresses shifted by 8 bits in several places. Consumers must preserve alignment and high-address handling for large GPU addresses.
- Update-lock, pending/taken, immediate flip, H-retrace, multiple-update-disable, and ignore-lock fields affect visible atomicity. Misuse can cause tearing, stale frames, missed flips, or updates that never take effect.
- Color pipeline fields are dense and repeated. Bad CSC, gamut, denorm, clamp, dither, LUT, or regamma masks can produce wrong colors, clipped output, broken HDR/gamma behavior, or failed CRC comparisons without crashing the driver.
- Cursor fields combine address, mode, expansion, color, position, hot spot, update, and stereo state. Incorrect mask layout can create misplaced cursors, wrong cursor colors, stale cursor updates, or stereo cursor mismatch.
- Azalia stream/endpoint windows are indexed. Writing data with the wrong index or write-enable bit can alter the wrong audio codec register while appearing as a valid MMIO write.
- Audio CRC and status fields are diagnostic-oriented and may be timing-sensitive. Resetting or enabling CRC collection at the wrong time can make test results unreliable.
- LB0 memory size, partitioning, pixel-depth, urgency, and interrupt fields interact with display bandwidth and underflow handling. Bad values can cause line-buffer underruns, vblank/vline interrupt loss, or unstable high-resolution modes.
- The chunk ends inside `LB0_LB_BUFFER_URGENCY_CTRL`; the following chunk owns the rest of the LB0 block. The final per-file report should avoid treating LB0 as fully covered by this chunk alone.

## Test Signals

Useful validation is mostly build-time, generated-header, and hardware-integration oriented:

- Kernel/AMDGPU builds for DCE 12.0 paths should compile with no missing field constants in `dce120_resource.c`, `dce120_timing_generator.c`, `dce120_hwseq.c`, memory-input, transform, audio, AUX, and shared DCE helper code.
- Generated-register validation should compare every field in lines 12066-14850 against AMD's authoritative DCE 12.0 register database and the matching offsets in `dce_12_0_offset.h`.
- Static checks can verify that each register field has matching `__SHIFT` and `_MASK` definitions, masks do not overlap unexpectedly within a register, full-register reserved fields remain full-width, and high-bit masks are represented with unsigned-safe 32-bit values.
- Display scanout tests should exercise DCP0 graphics enable, depth/format, tiling/swizzle, pitch, surface address high/low, viewport, compression metadata, and outstanding request programming across linear and tiled framebuffers.
- Page-flip and atomic-update tests should watch `DCP0_GRPH_UPDATE`, `DCP0_GRPH_FLIP_CONTROL`, page-flip interrupts, in-use address fields, immediate/H-retrace updates, lock/unlock paths, and multiple-update behavior.
- Color-management tests should cover prescale, input CSC, output CSC, gamut remap, degamma, LUT writes/autofill, regamma A/B regions, clamp, rounding, dithering, and DCP CRC output.
- Cursor tests should cover mode changes, 2x magnification, address high/low, size, position, hot spot, color, update locking, request filtering, and stereo controls.
- HDMI/DisplayPort audio tests should cover I2S/SPDIF enable/status, sample-rate reporting, CRC-test paths, and Azalia stream/endpoint indexed register access.
- DP receiver fault diagnostics should verify DPHY threshold, lock, align, deskew, excessive-error, FIFO-overflow, ack, and mask behavior during link bring-up and fault injection.
- Suspend/resume, runtime power-management, hotplug, and GPU-reset tests should verify that DCRX gate/reset/light-sleep state and DCP/LB/LUT/color state are restored or reinitialized correctly.
- Line-buffer tests should exercise LB0 pixel-depth/memory configuration, vblank/vline/vline2 interrupt masks and ACKs, sync-reset selection, key colors, buffer level reporting, urgency thresholds, and underflow recovery at bandwidth-stressing modes.
- XDMA diagnostics should observe cache-underflow count/status/ack/mask, flip timeout, average flip delay, recovery surface address, and surface counters on platforms or modes that use XDMA display paths.

Regression symptoms from bad constants include blank or corrupted displays, wrong colors or gamma, cursor artifacts, failed page flips, display underflows, lost vblank/vline/page-flip interrupts, failed EDID/audio behavior indirectly caused by receiver/audio misconfiguration, stuck Azalia indexed accesses, unreliable CRC diagnostics, broken suspend/resume recovery, or hardware faults when scanout addresses and tiling fields are misprogrammed.

## Cross-Chunk Notes

Earlier chunks of `dce_12_0_sh_mask.h` define the preceding DCE 12.0 field namespace and the first part of `DPRX_DPHY_INT_RESET`. This chunk starts with only the last two masks from that register and then continues through DCRX, audio, Azalia, DCP0, and early LB0 fields.

Later chunks continue the LB0 line-buffer block and the rest of the generated DCE 12.0 shift/mask namespace. The final per-file research document should frame this source as a generated hardware bitfield contract paired with `dce_12_0_offset.h`, not as standalone algorithmic driver code.

### subset-b-001543: lines 14851-17344

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 14851-17344

## Purpose

This chunk is a generated AMD DCE 12.0 register shift/mask section. It has no executable C logic; it publishes preprocessor constants that describe bit positions and bit masks for display-controller registers. Consumers combine these macros with DCE 12.0 register address macros from `dce_12_0_offset.h` and AMDGPU Display Core register helpers to read, write, lock, poll, or acknowledge hardware state.

The range covers the end of the `LB0` block and then several display pipe blocks for pipe 0 plus the beginning and most of the DCP pipe 1 register field map. It defines 2,130 `#define` entries for 341 register names in this line range. The major address blocks are:

- `LB0`: line-buffer urgency, empty/full, no-outstanding-request, and MVP flip/swap-lock control fields.
- `dce_dc_dcfe0_dispdec`: DCFE0 clock gating, soft reset, memory power control/status, miscellaneous, and flush fields.
- `dce_dc_dc_perfmon3_dispdec`: display performance-monitor counter selection, trigger/mask/window state, high/low counter values, and compare-value interrupt fields.
- `dce_dc_dmif_pg0_dispdec`: DMIF pipe arbitration, watermark mask, urgency, stutter, low-power, repeater, pre-processing check, and DVMM forced-flip status fields.
- `dce_dc_scl0_dispdec`: scaler coefficient RAM, mode, tap counts, filter ratios/init values, viewport/overscan, update, sharpness, ALU, and mode-change detection fields.
- `dce_dc_blnd0_dispdec`: blender mode, stereo/alpha/feedthrough controls, update/underflow interrupt state, V-update locks, and per-client pending-update status.
- `dce_dc_crtc0_dispdec`: timing generator totals, blank/sync windows, trigger events, force/count/status controls, interrupts, test pattern, master update locks, colors, vertical interrupts, CRC, external timing sync, static-screen, 3D, global swap-lock, and DRR/range timing fields.
- `dce_dc_fmt0_dispdec`: formatter clamp, dynamic expansion, pixel encoding/subsampling, dither, CRC, side-by-side stereo, and 4:2:0 hblank fields.
- `dce_dc_dcp1_dispdec`: graphics plane enable/control/surface addresses, update/flip/interrupt/compression fields, color-prescale/CSC/gamut/regamma matrices, denorm/clamp/key/degamma/dither fields, cursor state, LUT state, CRC/DVMM/GSL/rotation/XDMA fields, and regamma LUT region fields.

Although this path lives under a `ceph-client` source mirror, the content is AMDGPU display hardware metadata. It does not implement Ceph filesystem behavior, networking, distributed storage state, or persistence.

## Important APIs, Types, And Constants

There are no functions, structs, typedefs, variables, or call sites in this chunk. Its public surface is the macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the low bit position for a field.
- `REGISTER__FIELD_MASK` gives the field mask in its final register position.

This naming shape is consumed by AMD Display Core macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_UPDATE_N`, `set_reg_field_value`, and `get_reg_field_value`. Per-block header macros convert these generated constants into typed register, shift, and mask tables. Representative consumers elsewhere in this tree include `dce120_timing_generator.c`, which includes `dce/dce_12_0_sh_mask.h`, updates `CRTC0_CRTC_CRC_*` fields, and reads `CRTC0_CRTC_CRC*_DATA_*` fields; `dce_mem_input.h` and `dce_mem_input.c`, which map and program `DCP*_GRPH_UPDATE` and `DMIF_PG*_DPG_PIPE_URGENCY_CONTROL`; and `dce_ipp.h`/`dce_ipp.c`, which map cursor and `DCFE*_DCFE_MEM_PWR_CTRL` fields.

Important register families in this chunk include:

- Line-buffer and MVP fields: `LB0_LB_BUFFER_URGENCY_STATUS`, `LB0_LB_BUFFER_STATUS`, `LB0_MVP_AFR_FLIP_*`, `LB0_MVP_FLIP_LINE_NUM_INSERT`, and `LB0_DC_MVP_LB_CONTROL`.
- DCFE0 power/clock/reset fields: `DCFE0_DCFE_CLOCK_CONTROL`, `DCFE0_DCFE_SOFT_RESET`, `DCFE0_DCFE_MEM_PWR_CTRL`, `DCFE0_DCFE_MEM_PWR_CTRL2`, `DCFE0_DCFE_MEM_PWR_STATUS`, and `DCFE0_DCFE_FLUSH`.
- Performance-monitor fields: `DC_PERFMON3_PERFCOUNTER_CNTL`, `DC_PERFMON3_PERFCOUNTER_CNTL2`, `DC_PERFMON3_PERFCOUNTER_STATE`, `DC_PERFMON3_PERFMON_CNTL`, `DC_PERFMON3_PERFMON_CVALUE_INT_MISC`, `DC_PERFMON3_PERFMON_CVALUE_LOW`, `DC_PERFMON3_PERFMON_HI`, and `DC_PERFMON3_PERFMON_LOW`.
- DMIF/watermark fields: `DMIF_PG0_DPG_PIPE_ARBITRATION_CONTROL*`, `DMIF_PG0_DPG_WATERMARK_MASK_CONTROL`, `DMIF_PG0_DPG_PIPE_URGENCY_CONTROL`, `DMIF_PG0_DPG_PIPE_URGENT_LEVEL_CONTROL`, `DMIF_PG0_DPG_PIPE_STUTTER_CONTROL*`, `DMIF_PG0_DPG_PIPE_LOW_POWER_CONTROL`, and `DMIF_PG0_DPG_DVMM_STATUS`.
- Scaler fields: `SCL0_SCL_COEF_RAM_SELECT`, `SCL0_SCL_COEF_RAM_TAP_DATA`, `SCL0_SCL_MODE`, `SCL0_SCL_TAP_CONTROL`, horizontal/vertical filter ratio/init registers, `SCL0_SCL_UPDATE`, `SCL0_SCL_COEF_RAM_CONFLICT_STATUS`, viewport/overscan registers, and mode-change detectors.
- Blender fields: `BLND0_BLND_CONTROL`, `BLND0_BLND_SM_CONTROL2`, `BLND0_BLND_CONTROL2`, `BLND0_BLND_UPDATE`, `BLND0_BLND_UNDERFLOW_INTERRUPT`, `BLND0_BLND_V_UPDATE_LOCK`, and `BLND0_BLND_REG_UPDATE_STATUS`.
- CRTC0 fields: the largest group in this chunk, spanning mode timing, trigger A/B, counters, stereo, snapshots, update locks, test patterns, vertical interrupts, CRC, external sync, static-screen detection, 3D structure, GSL, and DRR/range timing.
- FMT0 fields: clamp ranges, formatter dynamic expansion/control, bit-depth/dither control, random seeds, CRC signatures/masks, stereo control, and 4:2:0 hblank early-start.
- DCP1 fields: graphics surface setup, flip/update handshakes, compression metadata, prescale/input CSC/output CSC/common matrices, denorm/clamp/keying, degamma/gamut remap, spatial dither/random seeds, cursor programming, LUT and regamma programming, DCP CRC, DVMM PTE controls, GSL control, rotation, and XDMA recovery.

## Control Flow

This header section has no runtime branches or sequencing. The runtime flow is imposed by AMDGPU/DC consumers that use the shift/mask constants.

A typical write path is:

1. Driver code computes desired display state from DRM atomic state, mode timing, plane state, cursor state, color-management state, watermark calculations, CRC settings, or power-management policy.
2. The code selects a register address from the matching DCE 12.0 offset header and one or more field names from this shift/mask header.
3. Register helper macros clear the field with `*_MASK`, shift the new value by `*_SHIFT`, merge it with the old register value if needed, and write through `dm_write_reg`, `dm_write_reg_soc15`, `REG_SET`, or `REG_UPDATE`.
4. Hardware latches the resulting state immediately, at a vertical-update boundary, behind a block-specific update lock, after a double-buffer update, or after an interrupt/status acknowledge depending on the register.

A typical read/poll path is:

1. Driver code reads a register with `dm_read_reg`, `dm_read_reg_soc15`, `REG_GET`, or a related helper.
2. The helper masks with `REGISTER__FIELD_MASK` and right-shifts by `REGISTER__FIELD__SHIFT`.
3. The extracted value is interpreted as pending/taken status, CRC data, current counter position, memory power state, line-buffer state, underflow, interrupt status, outstanding request status, or performance-counter value.

Important sequencing implied by this chunk but implemented elsewhere includes:

- Update-lock sequencing for DCP, SCL, BLND, CRTC master update, and graphics surface updates.
- CRTC timing programming before enabling scanout or master enable.
- Scaler coefficient RAM selection and tap-data writes before scaler update completion.
- Cursor address/size/hotspot/color programming before enabling the cursor.
- DCFE memory-power disable/enable around LUT, regamma, cursor, line-buffer, scaler, or blender memory use.
- Interrupt and status acknowledgement for underflow, vertical interrupts, CRTC set-v-total events, static-screen events, CRC, external timing sync, and line-buffer empty/full events.

## State And Persistence Behavior

The file itself stores no state. It defines constants for state held in DCE hardware registers and for software's view of those registers.

Hardware state represented here includes:

- Line-buffer fullness/emptiness, urgency level, no-outstanding-request status, and MVP flip/swap-lock status.
- DCFE clock gating, soft reset, memory power force/disable/mode selection, memory power status, and flush controls.
- Performance-monitor selection, enable, windowing, event state, compare thresholds, and high/low sampled counter values.
- DMIF request arbitration, urgent/low/high watermarks, watermark masks, stutter/self-refresh controls, low-power controls, and DVMM mapped/unmapped forced-flip status.
- Scaler coefficient RAM contents and conflict status, viewport/overscan rectangles, filter ratios, filter initial phases, tap counts, sharpness controls, ALU mode-change detection, and update-pending state.
- Blender composition mode, stereo mode, alpha mode, feedthrough, global gain/alpha, underflow interrupt state, V-update locks, and pending update status for DCP/SCL/BLND clients.
- CRTC timing, blanking, sync polarity/windows, vertical-total min/max/DRR controls, trigger state, counter/status snapshots, stereo/3D, static-screen detection, test patterns, CRC windows/data, external sync windows, vertical interrupts, GSL synchronization, and master update locks.
- Formatter clamp/dither/CRC/pixel-encoding/subsampling state.
- DCP1 graphics plane addresses, pitch, surface extents, pixel format/control, flip mode, DFQ state, compression base/pitch, color matrices, LUT/regamma tables, gamut remap, spatial dither, cursor state, PTE/DVMM state, CRC, GSL, rotation, and XDMA recovery state.

Persistence is register-specific. Some fields are durable until the next modeset, plane update, cursor update, color update, power transition, or GPU reset. Others are transient status bits, pending/taken bits, clear/ack bits, latched counters, or hardware-owned readback fields. The header does not encode reset defaults, access permissions, write-one-to-clear behavior, polling deadlines, or safe ordering; those rules live in hardware documentation and in the display driver code that uses these masks.

## Dependencies And Integration Points

This chunk depends on the generated DCE 12.0 register corpus. It is meaningful only with the matching register address/header set, especially:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h`, which defines the `mm*` register addresses and base indices for the fields in this chunk.
- Nearby generated enum and shift/mask headers that define value encodings and adjacent field families.
- AMD Display Core helper macros that consume `*_SHIFT` and `*_MASK` names to create per-IP register tables and bitfield updates.

Observed integration points in the source tree include:

- `display/dc/dce120/dce120_timing_generator.c`: includes this header and programs CRTC timing, CRC, status, and max-total fields through `CRTC_REG_UPDATE_*`, `dm_read_reg_soc15`, and `get_reg_field_value`.
- `display/dc/dce/dce_mem_input.h` and `display/dc/dce/dce_mem_input.c`: map `GRPH_UPDATE`, `GRPH_UPDATE_LOCK`, `GRPH_SURFACE_UPDATE_PENDING`, and `DPG_PIPE_URGENCY_CONTROL` fields for plane update locking and watermark/urgency programming.
- `display/dc/dce/dce_ipp.h` and `display/dc/dce/dce_ipp.c`: map cursor fields and `DCFE*_DCFE_MEM_PWR_CTRL` fields used when enabling/disabling LUT-related memory power.
- DCE compressor and timing-generator offset calculations that use `mmDCP1_GRPH_CONTROL - mmDCP0_GRPH_CONTROL` to address repeated pipe instances.
- OPP/DPP/scaler code patterns that use equivalent scaler coefficient, formatter, dither, and regamma field concepts on later DCN ASICs; these are not the same registers, but they show the same generated shift/mask consumption model.

The integration boundary is low level. Higher layers such as DRM atomic modeset, CRC debugfs, cursor IOCTL handling, color management, power management, and HPD/modeset policy do not include this header for business logic; they call hardware abstraction methods that eventually program the registers described by these constants.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These macros are plain preprocessor constants, so an incorrect mask or shift can compile cleanly while causing the driver to write the wrong bits.

High-risk areas in this chunk are:

- Timing generator fields. Bad CRTC totals, blanking windows, sync windows, polarity, master enable, vertical-total min/max, or DRR fields can produce a blank display, unstable refresh, underrun/underflow symptoms, or a mode that a sink cannot lock to.
- Update-lock and double-buffer fields. Incorrect use of `*_UPDATE_LOCK`, `*_UPDATE_PENDING`, and `*_UPDATE_TAKEN` can cause tearing, stale plane state, missed flips, or deadlocked waits for pending updates to clear.
- Interrupt/status/ack fields. Many fields pair occurred/status bits with clear/ack/mask/type bits. Writing the wrong mask can lose vertical interrupt, underflow, static-screen, external sync, CRC, trigger, or line-buffer events, or generate interrupt storms.
- DMIF watermark and urgency fields. Bad low/high watermark, urgent level, stutter, or arbitration values can cause display underflow, poor memory power behavior, excessive latency, or failure to enter/exit stutter states correctly.
- DCFE memory power controls. Forcing or disabling LUT, regamma, scaler coefficient, cursor, line-buffer, or blender memories while the relevant block is active can corrupt visible output or hang a programming sequence that expects memory to be powered.
- Scaler coefficient RAM fields. Wrong tap-pair, phase, filter type, coefficient enable, ratio, init, or update bits can produce bad scaling quality, color/chroma alignment issues, or host conflicts while hardware is reading coefficients.
- Blender alpha/stereo/feedthrough fields. Wrong blend mode, global alpha/gain, stereo polarity, overlap-only, or multiplied-alpha settings can hide planes, compose them with incorrect opacity, or break stereo presentation.
- Formatter and color fields. Wrong dither, clamp, pixel-encoding, subsampling, CSC, gamut, degamma, regamma, LUT, denorm, or clamp masks can cause visible color errors, CRC mismatches, or HDMI/DP format mismatches.
- DCP1 address and compression fields. Wrong surface address, high address, pitch, in-use/readback, compression address/pitch, or pipe request limit fields can cause corrupted scanout, memory faults, wrong framebuffer fetches, or compression metadata misuse.
- Cursor fields. Incorrect cursor surface address, size, hotspot, mode, position, or color fields can cause missing cursors, cursor corruption, or out-of-bounds fetch behavior.
- Repeated-instance naming. This chunk mixes pipe 0 blocks (`SCL0`, `BLND0`, `CRTC0`, `FMT0`, `DCFE0`, `DMIF_PG0`, `LB0`) with `DCP1`. Consumers that rely on instance offsets must combine the correct address base with the matching shift/mask table.

Generated-header maintenance is also risky. Manual edits, line wrapping changes, or generator regressions can break downstream macros that assume exact `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` spellings.

## Test Signals

Useful validation signals are build-time, generated-data, and hardware-behavior oriented:

- Kernel build coverage for DCE 12.0 display paths that include `dce_12_0_sh_mask.h`; missing or renamed macros should fail compilation in timing generator, memory input, IPP/cursor, color/LUT, and register-table code.
- Generated-header diffing against AMD's authoritative DCE 12.0 register database, checking every register/field shift and mask in this line range.
- Register-table self-consistency checks verifying that each `*_MASK` aligns with its `*_SHIFT`, has the expected field width, and does not overlap unrelated fields within the same register.
- Modeset tests across common and edge timing modes, including interlace/stereo/3D where supported, DRR or vertical-total variation, external timing sync, and master update lock paths.
- Page-flip and plane-update tests that watch `GRPH_UPDATE`, CRTC/blender/scaler update-pending bits, and visible tear-free transitions.
- Display CRC tests through `amdgpu_dm_crc`, including enabling/disabling CRTC CRC, programming CRC windows, reading CRC0/CRC1 data, and checking stable CRC output with and without dither.
- Watermark/underflow tests under memory pressure and low-power transitions, watching DMIF urgency/stutter behavior and `BLND_UNDERFLOW_INTERRUPT`.
- Scaler tests covering coefficient programming, horizontal/vertical scaling ratios, viewport/overscan, nearest/2-tap modes, and coefficient RAM conflict status.
- Color-management tests for LUT, regamma, degamma, CSC, gamut remap, clamp, denorm, spatial dither, and formatter bit-depth/pixel-encoding fields.
- Cursor tests for enable/disable, modes, address high/low, size, hotspot, color, position, 2x magnify, and update locking.
- Suspend/resume, runtime power, and GPU reset tests verifying that DCFE memory power and block reset state is restored before display programming resumes.

Regression symptoms from incorrect constants include blank or unstable displays, wrong timing, corrupted scanout, underflows, stuck pending updates, missing vertical interrupts, bad CRC reads, bad scaling, wrong colors, cursor corruption, failed flips, inability to enter stutter/low power, and failure to recover display state after reset or resume.

## Cross-Chunk Notes

This is a middle chunk of the large generated `dce_12_0_sh_mask.h` file. Earlier chunks define preceding DCE 12.0 register fields, and later chunks continue after `DCP1_GRPH_XDMA_RECOVERY_SURFACE_ADDRESS`. The final per-file merge should present the whole file as one generated hardware bitfield map for DCE 12.0, paired with offset and enum headers, rather than as independent executable modules.

The chunk begins mid-context with the mask for `LB0_LB_BUFFER_URGENCY_CTRL__LB_BUFFER_URGENCY_MARK_OFF_MASK`, so the matching shift and other fields for that register are in the previous chunk. It ends at the start of `DCP1_GRPH_XDMA_RECOVERY_SURFACE_ADDRESS`, so the mask and any following DCP1 fields are in the next chunk. Merge reconciliation should preserve those boundary relationships.

### subset-b-001544: lines 17345-19846

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 17345-19846

## Scope And Purpose

This chunk is a generated AMDGPU DCE 12.0 display-engine register mask/shift slice. It contains no executable code; it publishes preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for MMIO register fields. The assigned range has 2,130 `#define` entries: 1,065 shift constants and the matching 1,065 mask constants.

The range starts at the tail of the DCP1 display controller plane block, beginning with XDMA recovery/underflow and graphics surface counters. It then covers DCE pipe instance 1 support blocks: line buffer (`LB1`), DC front end (`DCFE1`), performance monitor 4, DMIF page 1 arbitration and power/stutter controls, scaler (`SCL1`), blender (`BLND1`), CRTC timing/status/CRC controls (`CRTC1`), and formatter (`FMT1`). The last section begins the DCP2 display controller plane block and runs through DCP2 regamma LUT write-enable masks. The chunk ends mid-DCP2 regamma family, so later chunks own the remaining DCP2 regamma region controls and subsequent blocks.

The file path is under a local `ceph-client` mirror, but this is AMDGPU Linux kernel display hardware metadata. It has no Ceph filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or local storage objects in this chunk. The public interface is the generated macro namespace. Consumers pair these field constants with the matching DCE 12.0 register-address definitions, usually through AMD display register helpers that compose read-modify-write operations.

The macro naming contract is:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the full bit mask for that field in the register.
- Prefixes such as `LB1_`, `SCL1_`, `CRTC1_`, `FMT1_`, and `DCP2_` identify display pipe or plane instances.
- `addressBlock` comments group adjacent registers by generated hardware block, such as `dce_dc_lb1_dispdec`, `dce_dc_scl1_dispdec`, `dce_dc_crtc1_dispdec`, and `dce_dc_dcp2_dispdec`.

Major register families in this slice:

- Late `DCP1` graphics-plane diagnostics: XDMA recovery address high bits, XDMA underflow count/status/interrupt acknowledgement, flip timeout status/mask/ack, average flip delay, and graphics surface min/max counters.
- `LB1` line-buffer configuration and status: pixel depth/expansion/reduction, prefill/prefetch/request mode, memory size/partitioning, desktop height, vline/vblank interrupt windows and acknowledgements, sync reset selection, black/keyer color values, buffer/FIFO level and urgency status, no-outstanding-request status, and MVP AFR flip helpers.
- `DCFE1`, `DC_PERFMON4`, and `DMIF_PG1`: front-end clock/reset/memory-power/flush bits, performance counter control/state/value fields, DMIF page arbitration, watermark mask selection, urgent/stutter/low-power controls, repeater programming, pre-processing checks, and DVMM status.
- `SCL1` scaler fields: coefficient RAM selection/tap data, scaler mode and tap counts, bypass/manual replication/automatic mode controls, horizontal and vertical filter setup, scale ratios/init phases, bottom-field init, rounding offsets, update lock/pending/taken state, sharpening/ALU controls, coefficient RAM conflict status, viewport start/size, overscan, and scaler mode-change detection/masking.
- `BLND1` blender fields: blend controls, shared-mode controls, update locks, underflow interrupt status/ack/mask, vertical update lock, and register update status.
- `CRTC1` timing generator fields: horizontal/vertical total, blanking, sync A/B positions and polarities, vertical total min/max and control, vertical total/vsync interrupts, trigger A/B, force count, flow control, stereo, AV sync counter, enable/blank/interlace/status/readback fields, frame/vblank counters, snapshot controls, interrupt controls, update locks, test patterns, master update state, MVP status, vertical interrupts 0-2, overscan/blank/black colors, CRC windows/data, external timing sync, static-screen control, 3D structure, GSL timing/control, range timing interrupt status, and DRR control.
- `FMT1` formatter fields: component clamps, dynamic expansion, pixel encoding/subsampling, spatial dither frame controls, 4:2:0 phase/early-start status, bit-depth/truncation/dithering controls, dither random seeds, clamp mode, CRC control/masks/signatures, and side-by-side stereo control.
- `DCP2` graphics-plane and color pipeline fields: graphics enable/control/swap/LUT bypass, primary/secondary surface addresses and in-use addresses, pitch/offset/window extents, gamma/update/flip controls, DFQ status, graphics interrupts, compressed surface metadata, outstanding request limits, prescale values, input/output CSC matrices, common matrix A/B transforms, denorm/round/clamp, keying ranges, degamma/gamut remap, spatial dither/random seeds, cursor surface/size/position/hotspot/colors/update/stereo, DC LUT programming/autofill/control/offsets, DCP CRC, DVMM PTE control/arbitration, flip-rate control, GSL/XDMA synchronization, line-buffer data gaps, stereo sync flip, hardware rotation, XDMA underflow counter control, and the start of regamma LUT access.

## Control Flow

This header slice has no runtime control flow. Every line is declarative metadata consumed by driver code when programming DCE 12.0 hardware registers.

The implied consumer flow is:

1. Select a register address macro from the paired DCE 12.0 address header for the relevant block and instance.
2. Use this chunk's `__SHIFT` and `_MASK` constants to pack, extract, or update a field value.
3. Read, write, or read-modify-write the MMIO register through AMDGPU/DC register helpers.
4. For stateful hardware operations, poll or acknowledge the status fields defined here, such as update-pending/taken bits, interrupt status/ack bits, CRC readbacks, coefficient RAM conflict status, underflow status, DVMM status, and vblank/vline/vsync events.

The header does not enforce sequencing. Correct ordering is owned by the display core: scaler coefficients must be selected and updated coherently, CRTC timing and formatter changes must obey update-lock/double-buffer rules, page flips and cursor updates must respect pending/taken state, and interrupt/ack fields must be handled with the polarity expected by the hardware.

## State And Persistence Behavior

The macros themselves have no mutable software state, allocation, locking, or persistence. They describe hardware-backed state in DCE 12.0 MMIO registers.

Hardware state represented by the chunk includes display pipe timing, line-buffer allocation, scaler and formatter programming, plane surface addresses, color matrices and LUTs, cursor state, CRC capture, performance counters, low-power and stutter controls, DVMM/PTE behavior, interrupt masks/status, update-lock state, and sticky diagnostics such as underflow and conflict indicators.

Persistence is register-specific and external to this header. Many control fields remain programmed until a later modeset, atomic commit, suspend/resume reprogramming, power-gating transition, or GPU reset. Status fields can be live, latched, sticky, write-one-to-clear, or self-clearing depending on the hardware block. The mask/shift header does not encode read-only/write-only semantics, reset defaults, volatile behavior, or required delays.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register contract for DCE 12.0. It is normally used with the companion address and enum headers in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/`, especially the DCE 12.0 register address header and enum definitions. The numeric masks and shifts must match AMD's hardware register database.

Observed direct include points for `dce_12_0_sh_mask.h` in this source tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c`

Practical integration surfaces are the AMD display core and AMDGPU memory/display initialization paths for DCE 12-era ASICs. These constants support mode set, vblank/vline/vsync IRQ service, CRTC timing, scaler setup, format conversion and dithering, plane flips, cursor updates, CRC testing, color-management programming, DMIF arbitration/watermark behavior, performance monitoring, and DVMM/PTE setup.

## Risks And Edge Cases

The primary risk is silent bitfield corruption. A wrong mask or shift can compile cleanly while programming the wrong bits in an MMIO register, leading to blank displays, bad timing, incorrect scaling, color errors, cursor corruption, failed flips, stuck interrupts, underflow, or power-management instability.

Instance repetition is a review hazard. This slice is mostly instance-1 display pipe metadata plus the start of DCP2, and many fields mirror equivalent DCP0/DCP1/LB0/SCL0/CRTC0/FMT0 definitions elsewhere in the file. A one-bit generator or copy error can affect only one display pipe, so single-display testing may miss it.

Status and acknowledgement fields need careful polarity handling. Names such as `*_ACK`, `*_MASK`, `*_INT`, `*_OCCURRED`, `*_PENDING`, `*_TAKEN`, `*_LOCK`, `*_CLEAR`, and `*_DISABLE` encode hardware conventions, not generic boolean API semantics. In particular, interrupt masks and write-one-to-clear acknowledgements are easy to misuse if callers infer behavior only from the suffix.

Timing and update-lock fields are high impact. CRTC timing, scaler ratio/init, formatter 4:2:0 phase, DCP surface address, LUT, CSC, cursor, and blender updates can be double-buffered or synchronized to vblank. Updating related fields without the right lock/pending/taken sequence can cause transient artifacts or missed flips.

Color pipeline fields are numerically dense. CSC matrices, gamut remap matrices, prescale values, clamp ranges, denorm/rounding, degamma/regamma LUT access, and dither controls use adjacent packed fields. Incorrect packing can produce subtle color regressions rather than obvious failures.

The requested range begins in the middle of a DCP1 register family and ends in the middle of the DCP2 regamma family. The final per-file synthesis should treat both as chunk-boundary artifacts and merge with neighboring chunk research before describing the full DCE 12.0 mask header.

## Test Signals

Useful validation is mostly build-time, generated-header comparison, and hardware/display behavior:

- Kernel or AMDGPU targeted builds should compile all DCE 12.0 users with no missing or duplicate macro names.
- Generated-register validation can compare every shift/mask pair against AMD's register database and ensure masks align with shifts and field widths.
- MMIO trace tests can verify that DCE 12.0 modeset, scaler, formatter, plane, cursor, and color-management paths write expected field values.
- Display mode tests should cover multiple pipes/connectors, common and high-refresh timings, interlace where supported, DRR, stereo/GSL paths, suspend/resume, and hotplug recovery.
- Page flip and cursor tests should watch update-pending/update-taken behavior, surface-address in-use registers, flip interrupts, and timeout/underflow diagnostics.
- CRC and formatter tests should exercise CRTC/FMT/DCP CRC controls and compare captured signatures across bit depths, pixel encodings, dithering modes, and 4:2:0 paths.
- IRQ tests should cover vblank, vline, vertical interrupt 0-2, underflow, range timing, external timing sync, and blender underflow acknowledgement/masking.
- Memory pressure and low-power tests should monitor DMIF urgency, stutter, DVMM/PTE status, line-buffer urgency, no-outstanding-request status, and XDMA/cache-underflow counters.

Regression symptoms from bad constants include blank or unstable output, wrong scanout dimensions, scaling artifacts, color shifts, broken cursor placement or format, persistent interrupt storms, missed vblank events, failed CRC validation, flicker around flips, underflow reports, and failures limited to the second or third display pipe.

## Cross-Chunk Notes

Earlier chunks of `dce_12_0_sh_mask.h` define the prior DCP1 regamma and graphics-plane fields that this range continues. Later chunks complete the DCP2 regamma block and continue through the remaining DCE 12.0 display register mask/shift namespace. The merge lane should present the full file as generated AMDGPU register bitfield metadata rather than algorithmic driver code.

### subset-b-001545: lines 19847-22341

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 19847-22341

## Scope And Purpose

This chunk is a generated AMD DCE 12.0 register shift/mask header section. It contains C preprocessor constants only: no functions, structs, enums, mutable storage, allocation, or executable control flow. Each register field is represented by paired macros named `...__SHIFT` and `..._MASK`, giving the bit offset and bit mask used by display-driver code when composing or decoding MMIO register values.

The range starts at the tail of pipe 2 DCP regamma LUT definitions, covers most of the pipe 2 front-end/display pipe register blocks, and ends in the early pipe 3 DCP cursor update definitions. The covered hardware domains are `DCP2`, `LB2`, `DCFE2`, `DC_PERFMON5`, `DMIF_PG2`, `SCL2`, `BLND2`, `CRTC2`, `FMT2`, and the first part of `DCP3`.

The purpose is to preserve the DCE 12.0 hardware ABI in source form. Consumers include this header together with the matching DCE 12.0 address/offset headers and use these constants through register-helper macros to program graphics planes, gamma/color processing, line buffers, display front-end clocks and memory power, performance counters, memory-interface watermarks, scalers, blenders, timing generators, formatters, CRC/readback blocks, interrupts, and cursor state.

## Important APIs, Types, And Macro Families

The public API surface is the macro namespace. The file does not define callable APIs or C types, but these macros are part of the low-level interface consumed by AMDGPU/DC display code.

Important macro groups in this chunk:

- `DCP2_REGAMMA_*`: pipe 2 output regamma LUT programming fields, including LUT write-enable mask and paired A/B piecewise region programming (`START_CNTL`, `SLOPE_CNTL`, `END_CNTL*`, and region `0_1` through `14_15`). These fields describe LUT offsets, segment counts, start/end values, slopes, and bases for color transfer programming.
- `DCP2_ALPHA_CONTROL` and `DCP2_GRPH_XDMA_*`: pipe 2 alpha rounding/cursor alpha blend fields and XDMA recovery/cache-underflow detection/status fields for display-plane recovery behavior.
- `LB2_*`: line-buffer format and memory controls, desktop height, vline/vline2/vblank counters and interrupt status, sync reset selection, black/keyer colors, buffer fill/urgency/empty/full status, no-outstanding-request status, and MVP AFR flip/swap-lock helper fields.
- `DCFE2_*`: pipe 2 display front-end clock gating, soft reset, memory power control/status for DCP LUT/regamma/cursor, scaler coefficient, line-buffer, and blender memories, plus misc and flush status fields.
- `DC_PERFMON5_*`: performance-counter control/state, low/high counter values, counter-off and interrupt controls, and cvalue interrupt/status fields for display performance monitoring.
- `DMIF_PG2_DPG_*`: pipe 2 display memory-interface arbitration, watermark masks, urgency levels, stutter/self-refresh behavior, low-power/P-state controls, repeater programming, pre-processing buffer checks, and DVMM forced-flip status/clear fields.
- `SCL2_*`: scaler coefficient RAM select/data, mode, taps, bypass/replication/auto-ratio controls, horizontal and vertical ratios and initial phases, rounding offsets, update-lock/update-taken state, sharpness, ALU disable, coefficient RAM conflict interrupt/status, viewport and overscan geometry, and scaler mode-change detection/masking.
- `BLND2_*`: blender global gain/alpha/mode/stereo/feedthrough controls, super-AA and PTI fields, blender update locks, underflow interrupt status/ack/mask, vertical-update lock fanout for DCP/SCL/BLND blocks, and register-update pending status.
- `CRTC2_*`: timing-generator fields for horizontal and vertical totals, blanking, sync A/B windows, polarity, triggers, force-count-now, flow control, stereo/interlace, master enable, blanking, readback/status counters, snapshots, interrupts, double buffering, test patterns, master update locks/modes, MVP in-band controls, overscan colors, CRC windows/data, external timing sync, static-screen detection, 3D structure, GSL, range timing update, and DRR control.
- `FMT2_*`: formatter clamp component limits, dynamic expansion, pixel encoding/subsampling, spatial/temporal dithering, random seeds, clamp control, formatter CRC setup/signatures, side-by-side stereo width, and 4:2:0 hblank early start fields.
- `DCP3_*` opening block: pipe 3 graphics enable/control, surface addressing, viewport, desktop/windowing, flip/update/interrupt fields, prescale/CSC/color matrices, denorm/round/clamp/keying, degamma/gamut remap, DCP spatial dither, random seeds, converted-field readout, and cursor control/surface/size/position/hotspot/color/update fields through `DCP3_CUR_UPDATE__CURSOR_UPDATE_TAKEN_MASK`.

## Control Flow And Data Flow

There is no runtime control flow in this header. Data flow is compile-time substitution: a caller includes `dce_12_0_sh_mask.h`, picks a field macro, shifts a value by `...__SHIFT`, masks it with `..._MASK`, and writes the resulting bits through an AMDGPU/DC MMIO helper to the address from a matching `dce_12_0_*` register-address header.

The implied hardware flows are stateful:

- Plane programming uses DCP fields to set graphics surface format, tiling/swizzle metadata, addresses, viewport, flip behavior, color transforms, gamma/gamut controls, dither, keying, and cursor registers. Update and lock fields determine when programmed state becomes active.
- Timing programming uses CRTC fields to stage totals, blank/sync windows, interlace/stereo, master-enable, update locks, snapshots, interrupts, CRC windows, DRR, GSL, and external timing sync.
- Memory and bandwidth programming uses LB and DMIF fields to set line-buffer formats, buffer levels, urgency thresholds, watermarks, stutter/self-refresh, P-state allowance, and underrun/underflow acknowledgement.
- Scaling and blending use SCL and BLND fields to load coefficient RAM, choose filter modes and ratios, define viewports/overscan, latch updates, blend planes/cursors, and surface underflow events.
- Formatter and CRC paths use FMT and CRTC CRC fields to clamp, dither, encode pixels, control 4:2:0/subsampling behavior, seed random dithering, and capture output signatures for validation.
- DCFE and PERFMON fields participate in clock/memory power sequencing, soft resets, flush detection, and performance counter collection.

Ordering is not encoded here, but consumers must respect hardware sequencing. Examples include locking updates before multi-register changes, waiting for `*_UPDATE_TAKEN` or pending bits to clear, acknowledging interrupt/status bits with the correct clear field, programming coefficient/LUT RAM through index/data windows without conflicts, and avoiding clock or memory power gating while dependent blocks are active.

## State And Persistence Behavior

The header itself has no persistence. The state represented by these constants lives in DCE 12.0 hardware registers after the driver writes them and persists until overwritten, reset, power-gated, or reinitialized during modeset, suspend/resume, GPU reset, or display pipeline teardown.

State categories represented here include:

- Color and pixel-processing state: regamma regions/LUT enables, prescale, input/output CSC matrices, degamma/gamut remap, denorm, rounding, clamping, dithering, formatter dynamic expansion, and CRC capture controls.
- Plane and cursor state: graphics enable, surface addresses, tiling/swizzle metadata, pitch, viewport, flip/pending status, cursor enable/mode/address/size/position/hotspot/colors, alpha blend, and update locks.
- Timing-generator state: active/blank/sync geometry, interlace/stereo, master enable, blanking, frame/line counters, snapshots, forced sync/count operations, DRR, GSL, static-screen detection, test patterns, and external timing sync.
- Bandwidth and memory-interface state: line-buffer configuration, buffer levels, urgency marks, DMIF arbitration weights, watermarks, stutter/self-refresh, P-state change controls, and flush/no-outstanding-request status.
- Power and reset state: DCFE clock gating, soft reset, memory power force/disable/mode/status fields for pipe-local memories.
- Interrupt and diagnostic state: vblank/vline status, underflow/cache-underflow, CRTC events, external sync loss, scaler coefficient conflicts, performance counter interrupts, CRC signatures, and readback registers.

Many fields are acknowledgement, clear, status, pending, or mask bits. These should be treated as hardware side effects, not ordinary software state. Writing the wrong bit can clear evidence, leave interrupts asserted, unmask an interrupt unexpectedly, or latch partially programmed display state.

## Dependencies And Integration Points

This generated header depends on consistency with the DCE 12.0 register database and sibling generated headers that provide register offsets and enumerated values. The masks and shifts are useful only when paired with the correct register address for the same ASIC generation and display pipe.

Primary integration points:

- AMDGPU/DC register access helpers that use generated shift/mask fields to implement `REG_SET`, `REG_UPDATE`, bitfield read/modify/write, and traceable MMIO programming.
- DCE 12.0 resource construction and hardware sequencing code that maps logical pipes to `DCP`, `SCL`, `BLND`, `CRTC`, `FMT`, `LB`, `DMIF`, and `DCFE` register blocks.
- Atomic modeset, page-flip, cursor, color-management, scaling, and blending paths that program the DCP/SCL/BLND/CRTC/FMT fields.
- Interrupt handling for vblank/vupdate, vline, underflow, scaler conflicts, CRTC events, external timing sync, static-screen, and performance-monitor events.
- Power-management and bandwidth code that adjusts DMIF watermarks, stutter/P-state behavior, DCFE memory power, clock gating, and flush/no-outstanding-request status.
- Diagnostics and validation paths that use CRTC/FMT CRC registers, pixel readback, counters, and performance monitor fields.

The chunk is also structurally tied to repeated pipe instances. Pipe 2 register blocks dominate the range, and the final section begins pipe 3 DCP definitions. Generated maintenance must preserve the pipe index in macro names and the corresponding address block selected by caller code.

## Risks And Edge Cases

The major risk is generated-header drift. These constants are hardware ABI: a one-bit shift or mask error compiles cleanly but programs the wrong register field.

Specific risks:

- Chunk boundaries are partial. The range starts after the beginning of the `DCP2_REGAMMA_LUT_WRITE_EN_MASK` block and ends in the middle of `DCP3_CUR_UPDATE`; adjacent chunks are needed for complete per-file synthesis.
- Repeated pipe and register families make copy/generation errors hard to spot. `DCP2`, `LB2`, `SCL2`, `BLND2`, `CRTC2`, `FMT2`, and `DCP3` names are similar but must match the correct pipe address block.
- Many fields have write-one-to-clear or acknowledgement semantics (`*_ACK`, `*_CLEAR`, `*_CLR`, `*_RESET`, `*_UPDATE_TAKEN`, interrupt occurred bits). Treating them as normal read/write values can lose events or wedge status bits.
- Mask polarity is not uniform. Fields named `*_MASK`, `*_INT_MSK`, `*_DIS`, `*_DISABLE`, `*_GATE_DISABLE`, or `*_FORCE_*` require hardware-specific interpretation.
- LUT and coefficient RAM fields are index/data style and may conflict with hardware readers. Misordered access can corrupt gamma or scaler coefficients, producing color or scaling artifacts.
- Timing and update-lock fields can cause visible glitches if related CRTC/SCL/BLND/DCP fields are not latched atomically at the intended vertical update.
- Bandwidth, urgency, stutter, P-state, and memory-power fields can cause underflow, flicker, self-refresh failures, or power regressions even when the display still lights up.
- Formatter pixel encoding, 4:2:0, dithering, clamp, and CRC fields interact with connector/output format expectations; wrong masks can produce subtle color-depth or validation failures.

## Test Signals

There are no standalone unit tests for this macro section. Useful validation signals are build coverage, generated-header comparison, and hardware behavior:

- Build AMDGPU/DC configurations that include `dce_12_0_sh_mask.h`; this catches syntax errors, missing macros, and duplicate definitions.
- Compare this range against the authoritative DCE 12.0 register database or a known-good upstream generated header, especially repeated pipe 2 blocks and the transition into pipe 3.
- Exercise modeset, page flip, cursor movement, color-management gamma/degamma/gamut, scaling, blending, overscan, stereo/interlace, DRR, and 4:2:0 output paths on DCE 12.0 hardware.
- Validate vblank/vline/vupdate, CRTC trigger, underflow, scaler conflict, external timing sync, static-screen, and performance-monitor interrupts for correct mask/ack behavior.
- Run CRC and pixel-readback validation through CRTC/FMT CRC windows and compare signatures across known test patterns.
- Stress suspend/resume, GPU reset, clock gating, memory power, stutter/self-refresh, and P-state transitions to catch DCFE/DMIF/LB sequencing mistakes.
- Inspect MMIO traces for representative register writes to ensure field values are shifted and masked into the expected bit positions.

### subset-b-001546: lines 22342-24835

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 22342-24835

## Purpose

This chunk is a generated AMDGPU DCE 12.0 display-engine shift/mask header section. It contains no executable C functions; it publishes compile-time `#define` constants that describe bit positions and bit masks for memory-mapped display controller registers. Driver code combines these field macros with address macros from `dce_12_0_offset.h` and generic register helpers to read, write, and update hardware fields safely.

The assigned range starts at the tail of the DCP3 cursor update field list, then covers several complete DCE pipe-3 register blocks: DCP3 color/cursor/CRC/DVMM/XDMA fields, line buffer `LB3`, display front-end `DCFE3`, performance monitor `DC_PERFMON6`, display memory interface `DMIF_PG3`, scaler `SCL3`, blender `BLND3`, CRTC timing generator `CRTC3`, formatter `FMT3`, and the beginning of DCP4 graphics-plane/color fields. The range ends mid-family after `DCP4_COMM_MATRIXB_TRANS_C13_C14__COMM_MATRIXB_TRANS_C13_MASK`; the continuation of DCP4 matrix B and later DCP4 fields belongs to the next chunk.

## Important APIs, Types, And Macros

The API surface is the macro namespace. Every field generally has a pair:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit index.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask in the 32-bit MMIO register value.

The chunk contains no structs, enums, functions, storage, or inline logic. Its value is in exact hardware ABI names and encodings. Important register families in this chunk are:

- `DCP3_CUR_*`: cursor request filtering and stereo offsets, plus inherited cursor update lock/pending/taken fields from the chunk boundary.
- `DCP3_DC_LUT_*` and `DCP3_REGAMMA_*`: input/display LUT programming, LUT read/write mode/index/data, 10-bit color packing, per-channel black/white offsets, autofill status, regamma LUT index/data/write-enable, and dual regamma region programming tables `CNTLA` and `CNTLB`.
- `DCP3_DCP_CRC_*`, `DCP3_GRPH_XDMA_*`, and `DCP3_GRPH_SURFACE_COUNTER_*`: DCP CRC controls/current/last values, XDMA underflow/timeout/average-delay diagnostics, recovery surface address, interrupt/ack bits, and graphics surface event counters.
- `DCP3_DVMM_*`, `DCP3_DCP_GSL_CONTROL`, `DCP3_GRPH_FLIP_RATE_CNTL`, `DCP3_GRPH_STEREOSYNC_FLIP`, `DCP3_HW_ROTATION`, and `DCP3_ALPHA_CONTROL`: virtual-memory PTE sizing/arbitration, genlock/swaplock synchronization, flip pacing, stereo flip pending state, hardware rotation, and cursor alpha blending.
- `LB3_*`: line-buffer pixel format/depth/alpha, memory size/configuration, vline/vblank interrupt masks and status/ack fields, sync reset selection, keyer colors, buffer level/urgency/empty/full status, no-outstanding-request status, and MVP/AFR flip controls.
- `DCFE3_*`: display front-end clock gating, soft reset, memory power control/status, and flush control, including many per-memory-bank power fields.
- `DC_PERFMON6_*`: eight performance-counter control/select/state fields, global performance monitor state, counter-off interrupt status/ack, counter value high/low reads, and per-counter interrupt status/ack fields.
- `DMIF_PG3_*`: DPG arbitration weights, watermark mask selection, urgent/stutter/self-refresh/P-state controls, repeater programming, preprocessor check disable, and DVMM forced-flip status/clear fields.
- `SCL3_*`: coefficient RAM selection/data, scaler mode/tap/bypass/replication/automatic-ratio controls, horizontal/vertical ratios and initial phases, round offsets, update lock/pending/taken fields, sharpening, ALU disable, coefficient conflict interrupt/ack, viewport/overscan geometry, and mode-change detection/masking.
- `BLND3_*`: blender global gain/alpha/mode/stereo controls, state-machine controls, pixel timing improvement and SuperAA controls, update lock/pending/taken fields, underflow interrupt fields, vertical update locks spanning DCP/SCL/BLND, and aggregate register-update status.
- `CRTC3_*`: timing totals, blank/sync windows, min/max vertical total and DRR support, triggers A/B, force-count-now, flow control, stereo/AV sync, CRTC enable/blank/interlace/status counters, snapshots, start-line and interrupt controls, update locks, double buffering, VGA parameter capture, test patterns, master update locks/modes, MVP in-band status, vupdate/vblank-like interrupt positions, colors, CRC windows/data, external timing sync, static screen status, 3D structure, GSL timing, range timing status, and DRR controls.
- `FMT3_*`: formatter clamp limits, dynamic expansion, pixel encoding/subsampling, 4:2:0 phase status/clear, truncation/spatial/temporal dithering, random seeds, clamp control, formatter CRC control/signatures/masks, side-by-side stereo width, and 4:2:0 hblank early-start.
- `DCP4_*`: first part of pipe-4 graphics plane programming, including enable/control/tiling/swizzle metadata, surface addresses and pitch, offsets and extents, input gamma, graphics update/flip controls, DFQ status/reset, page-flip interrupts, compression surface metadata, outstanding request limit, prescale, input/output CSC matrices, and the start of common color transformation matrices.

## Control Flow

There is no local runtime control flow. The control flow is imposed by consumers that include `dce_12_0_sh_mask.h` and use macros such as `FD(reg__field)` through register helpers. For example, DCE 12.0 timing code includes this file and `dce_12_0_offset.h`, then uses CRTC register update wrappers around `generic_reg_update_soc15()` and `generic_reg_set_soc15()`; resource code derives per-pipe offsets such as `mmCRTC3_CRTC_CONTROL - mmCRTC0_CRTC_CONTROL`; IRQ code builds interrupt register descriptors from address and mask macros.

Several macro groups encode hardware sequencing even though this header does not implement the sequence:

- Update paths use `*_UPDATE_PENDING`, `*_UPDATE_TAKEN`, `*_UPDATE_LOCK`, `*_DISABLE_MULTIPLE_UPDATE`, master update locks, and vertical update lock fields. Consumers must program related registers while locked and then release/update in the right vertical timing window.
- Interrupt/status paths use `*_OCCURRED`, `*_STATUS`, `*_INT`, `*_MASK`, `*_CLEAR`, and `*_ACK` fields across CRTC, LB, BLND, FMT, DCP/XDMA, perfmon, and external timing sync. These fields are often sticky or write-one-to-clear at the hardware level.
- Memory and power paths use DMIF watermarks, stutter/self-refresh, P-state change, DVMM, DCFE memory power, line-buffer urgency, and DCP outstanding-request fields. Driver sequencing has to match display mode, memory clock, and surface layout.
- Color and scaling paths write LUTs, regamma regions, CSC matrices, scaler coefficients, formatter dither/clamp controls, and viewport geometry. Updates must be synchronized to avoid visible tearing, wrong color, or inconsistent scaler coefficients.

## State And Persistence Behavior

The header itself stores no state and has no persistence. It is generated static metadata consumed at compile time.

The represented state lives in DCE 12.0 hardware registers after MMIO writes. Some fields are durable configuration until the next modeset, plane update, suspend/resume reprogramming, display pipe reset, or GPU reset. Examples include CRTC timings, scaler ratios, color matrices, LUT modes, DMIF watermarks, line-buffer memory layout, DCP surface format, and formatter dithering.

Other fields reflect transient or sticky hardware state: update pending/taken bits, vblank/vline/vertical interrupt occurrence, trigger occurrence, CRC data, current counters, underflow/timeout status, perfmon counter values, power status, buffer level/urgency status, and mode-change detection. Clear/ack fields are state-transition controls rather than persistent settings. The macros do not encode access type, reset value, polling requirements, or write-one-to-clear semantics; those are owned by the hardware specification and call-site logic.

## Dependencies And Integration Points

This chunk depends on the generated AMD DCE 12.0 register-header contract. The practical pair is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h`, where matching `mm...` address macros and base indices are defined. It is also tied to the generated enum/value headers and to SOC15 base-address definitions used by DCE 12.0 display code.

Direct source-tree include points for DCE 12.0 offset and shift/mask headers include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_factory_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_translate_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c`

The functional integration surface is AMD display core for Vega/DCE 12.0-era hardware: mode set, page flip, cursor, scaler, color management, line-buffer programming, DMIF/watermark and low-power behavior, interrupts, CRC capture, underflow diagnostics, and pipe synchronization. The path is under a local `ceph-client` source mirror, but this chunk is AMDGPU display hardware metadata, not Ceph filesystem logic.

## Risks And Edge Cases

- Bit masks and shifts are hardware ABI. A single wrong value can compile cleanly while corrupting unrelated register fields or leaving the intended field unchanged.
- The range is highly repetitive across pipe instances. DCP3, LB3, SCL3, BLND3, CRTC3, FMT3, and DCP4 names differ mainly by block index, making generator or manual review mistakes hard to spot.
- The chunk begins and ends inside larger register families. The first lines continue `DCP3_CUR_UPDATE`, and the last lines stop in `DCP4_COMM_MATRIXB_TRANS_C13_C14`; per-file synthesis must merge adjacent chunks before treating the DCP3 cursor or DCP4 matrix coverage as complete.
- `*_MASK_MASK` identifiers are legitimate generated names for fields whose hardware name itself ends in `MASK`; they should not be simplified or deduplicated.
- Acknowledgement, clear, reset, and interrupt mask fields often have different polarity from ordinary enable fields. Misuse can leave interrupts stuck, drop vblank/vline events, fail to clear underflow/timeouts, or mask critical diagnostics.
- Update-lock misuse can produce partial plane, scaler, blender, or CRTC programming on a live scanout. Relevant fields include DCP graphics/cursor update locks, SCL update lock, BLND update lock, BLND vertical update lock, CRTC update/master update locks, and formatter or CRTC double-buffered state.
- DMIF, line-buffer, DCFE power, and DVMM fields are timing- and memory-sensitive. Bad watermarks, stutter/P-state settings, PTE parameters, or buffer limits can appear as underflow, flicker, page-flip delay, self-refresh instability, or resume failures.
- Color/scaler fields are packed signed/fixed-point or table-index values. Incorrect shifts for LUT deltas, regamma regions, CSC matrices, prescale bias/scale, scaler ratios, or dither controls can cause subtle image-quality regressions rather than obvious failures.
- CRTC timing and synchronization fields affect global display behavior. Wrong total/blank/sync, DRR, external timing sync, stereo, GSL, or trigger fields can break mode validation, genlock/swaplock, frame pacing, stereo output, or multi-display synchronization.

## Test Signals

Useful validation is mostly build-time plus hardware/display runtime behavior:

- Kernel or targeted AMDGPU display builds should compile all DCE 12.0 include users without missing macro names, duplicate definitions, or syntax issues.
- Generated-register validation can compare every `__SHIFT`/`_MASK` pair in this chunk against AMD's source register database and against the adjacent `dce_12_0_offset.h` address names.
- Modeset tests should cover pipe 3 and pipe 4 usage across common resolutions, interlaced/progressive modes, stereo/3D modes, DRR, external timing sync, and multi-display synchronization.
- Plane/page-flip tests should exercise DCP3/DCP4 graphics update locks, surface address changes, compression metadata, DFQ status, page-flip interrupts, XDMA flip timeout/average-delay diagnostics, and recovery surface behavior.
- Cursor tests should cover DCP3 cursor update locking, stereo offsets, request filtering, cursor alpha blending, and simultaneous cursor plus plane updates.
- Color tests should validate DC LUT, regamma LUT/regions, CSC/common matrices, prescale, formatter clamp, dynamic expansion, and dither/truncation paths with CRC or visual comparison.
- Scaler tests should cover coefficient RAM programming, horizontal/vertical ratios, viewport/overscan changes, update completion, coefficient conflict handling, mode-change detection, and bypass/replication modes.
- Memory and power tests should monitor DMIF watermarks, stutter/self-refresh, P-state change, DVMM forced-flip status, line-buffer urgency/empty/full status, DCFE memory power status, and display underflow during high bandwidth, low refresh, and suspend/resume scenarios.
- Interrupt and diagnostics tests should verify vblank/vline/vupdate, CRTC vertical interrupts, BLND underflow, FMT/CRTC/DCP CRC capture, perfmon counter-off interrupts, and all relevant ack/clear paths.

## Cross-Chunk Notes

Earlier chunks of `dce_12_0_sh_mask.h` define the preceding DCP3 graphics, color, cursor, and possibly other DCE register fields. Later chunks continue DCP4 from the middle of `DCP4_COMM_MATRIXB_TRANS_C13_C14` into the remaining DCP4 color, clamp, keyer, gamma, cursor, LUT, CRC, DVMM, line-buffer, scaler, blender, CRTC, formatter, and following pipe blocks. The final merged per-file report should treat this file as generated AMDGPU DCE 12.0 shift/mask metadata and should avoid inferring algorithmic behavior from this chunk alone.

### subset-b-001547: lines 24836-27328

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 24836-27328

## Scope And Purpose

This chunk is a generated AMD DCE 12.0 register field shift/mask header section. It contains C preprocessor constants only: no functions, structs, enums, storage, or executable logic. Each register field is represented by a `__SHIFT` macro and a matching `_MASK` macro that callers use to pack or extract bitfields for DCE 12.0 display-engine MMIO registers.

The range begins mid-register at the final mask for `DCP4_COMM_MATRIXB_TRANS_C13_C14`, then covers the rest of the DCP4 color/cursor/LUT/CRC/update-control fields, complete address blocks for `dce_dc_lb4_dispdec`, `dce_dc_dcfe4_dispdec`, `dce_dc_dc_perfmon7_dispdec`, `dce_dc_dmif_pg4_dispdec`, `dce_dc_scl4_dispdec`, `dce_dc_blnd4_dispdec`, `dce_dc_crtc4_dispdec`, and `dce_dc_fmt4_dispdec`, and then starts `dce_dc_dcp5_dispdec` through `DCP5_GRPH_UPDATE`.

The purpose is hardware-description support for AMDGPU/DC, not Ceph filesystem behavior. The source tree is a Ceph-client mirror that includes Linux GPU driver code; this file belongs to the AMD display stack and gives register programming code stable symbolic bit positions for pipe 4 and the beginning of pipe 5 on DCE 12.0 hardware.

## Important APIs, Types, And Macro Families

There are no callable APIs or C types in this chunk. The exported interface is the macro namespace. Macro names follow the generated form `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`, with field positions encoded as hexadecimal shifts and masks encoded as 32-bit literals ending in `L`.

The DCP4 section covers display controller pipe 4 plane and color-pipeline fields. It includes matrix coefficients for `COMM_MATRIXB_TRANS_*`, denorm and output rounding/clamp controls, color key ranges, degamma and gamut remap controls, spatial dithering and random seeds, cursor enable/mode/address/size/position/hotspot/color/update/stereo fields, DC LUT read/write/autofill/control/offset fields, DCP CRC control/mask/current/last fields, DVMM PTE control and arbitration, flip-rate/GSL controls, line-buffer data-gap fields, stereo flip control, hardware rotation, XDMA cache-underflow detection/status, regamma LUT and piecewise-region fields for CNTLA/CNTLB, alpha control, XDMA recovery surface addresses, flip timeout/delay, and surface counter controls.

The LB4 line-buffer block defines input data format, interleave and alpha enable, pixel-depth and dynamic expansion/reduction controls, memory size/status, desktop height, vline/vline2/vblank interrupt status and masks, sync reset selection, black/keyer color fields, buffer level/urgency/status/no-outstanding-request fields, and MVP AFR flip/FIFO/line insert controls.

The DCFE4 block defines display front-end clock gating, software reset bits for DCP/SCL/BLND/FMT/CRTC, memory power controls for DCP/LB/SCL/BLND/CRTC/FMT memories, power-status mirrors, miscellaneous DCP global-alpha polarity, and flush controls. These fields are power-management and block-reset sensitive.

The DC_PERFMON7 block defines perf counter selection, count modes, run/stop behavior, interrupt controls, per-counter state fields for counters 0 through 7, perfmon state/control fields, current-value interrupt/mask/status fields, and high/low counter readback fields. It is a display-engine performance-monitor register bank, not Linux perf infrastructure.

The DMIF_PG4 block defines pipe arbitration, watermark mask, urgent/stutter/low-power controls, repeat programming, checksum pre-process control, and DVMM status fields for display memory-interface pipe group 4. These fields directly affect display memory fetch timing, latency tolerance, stutter entry/exit, and virtual-memory fault/status reporting.

The SCL4 scaler block defines coefficient RAM selection and tap data fields, scaler mode/tap/bypass/manual-replicate/automatic-mode controls, horizontal and vertical filter ratios/initial phases, round offsets, update lock/pending/taken controls, sharpness and ALU controls, coefficient conflict status, primary/secondary viewport start and size, external overscan, and mode-change detection/masking fields.

The BLND4 block defines blender enable/mode/alpha/stereo/current-eye controls, SM control, feeding-pixel and clamp controls, update lock/pending/taken controls, underflow interrupt/mask/clear/status fields, V-update lock behavior, and register-update status fields. This is the composition stage between DCP/SCL/FMT/CRTC.

The CRTC4 timing-generator block is the largest complete block in this chunk. It covers horizontal and vertical totals, blanking, sync A/B timing and polarity, variable vertical total control, total/nominal-vsync/vupdate/range timing interrupt status, trigger A/B controls, force-count and flow controls, stereo/interlace controls and status, CRTC enable/master/update locks, blanking/test-pattern/readback/status/counter/snapshot fields, vertical interrupt 0/1/2 controls, CRTC CRC windows and data, external timing sync controls and interrupt state, static-screen control, 3D structure, GSL, DRR, overscan/blank/black color registers, and MVP status/insert fields.

The FMT4 formatter block defines clamp bounds, dynamic expansion, pixel encoding, subsampling, 4:2:0 phase state, truncation/spatial/temporal dithering, random seeds and offsets, clamp format, formatter CRC control/signature/masks, side-by-side stereo active width, and 4:2:0 hblank early start fields.

The DCP5 opening section begins the next pipe's graphics-plane state. It includes enable/keyer alpha, surface format/depth/tiling geometry, address-translation and privileged-access controls, shader-engine/pipe layout fields, 10-bit LUT bypass, endian and color-channel crossbar controls, primary/secondary surface addresses and high address bits, pitch, viewport offsets, X/Y start/end, input gamma mode, and the start of graphics update status/lock fields.

## Control Flow And Data Flow

This header has no internal runtime control flow. Data flow is compile-time macro substitution: a C source file includes `dce_12_0_sh_mask.h`, combines these field descriptions with a companion register address from `dce_12_0_offset.h`, and reads or writes the target hardware register through AMDGPU/DC helpers.

The DCE 12.0 timing-generator code shows the typical pattern. `display/dc/dce120/dce120_timing_generator.c` includes this header and uses helper macros such as `CRTC_REG_UPDATE`, `CRTC_REG_SET`, and `FD(reg__field)` to pass field descriptors into `generic_reg_update_soc15()` or `generic_reg_set_soc15()`. Those helpers use the `__SHIFT` and `_MASK` values to update one or more fields without manually spelling bit arithmetic at each call site.

Interrupt registration follows a similar compile-time composition path. `display/dc/irq/dce120/irq_service_dce120.c` builds `irq_source_info` entries with macros such as `IRQ_REG_ENTRY`, `vblank_int_entry`, `vupdate_int_entry`, and `pflip_int_entry`; those entries pair DCE 12.0 register offsets with field masks such as vertical interrupt enable/clear, v-update clear, and graphics page-flip interrupt mask/clear fields.

Hardware sequencing, resource setup, GPIO translation/factory code, and `amdgpu/gmc_v9_0.c` also include the DCE 12.0 offset and shift/mask headers. Some of this chunk's fields may be used indirectly through shared DCE macros that target pipe instance 0 with a runtime pipe offset, while the generated pipe-4 and pipe-5 names document the replicated hardware layout.

## State And Persistence Behavior

The file stores no state and performs no I/O. The mutable state represented by these constants lives in DCE 12.0 display hardware registers. Driver writes using these macros can persist until another modeset, page flip, cursor update, color update, interrupt acknowledgement, power-management transition, suspend/resume sequence, or hardware reset rewrites the block.

Important state categories represented here include color pipeline state, LUT and regamma programming, cursor surface and position state, graphics primary/secondary surface address state, scaler ratios and viewport state, line-buffer memory and urgency state, DMIF watermark/stutter/urgent state, timing-generator totals/sync/blanking/counter state, interrupt masks and sticky status bits, CRC capture windows and signatures, formatter dithering and pixel encoding, and display-front-end reset or memory power state.

Several fields are double-buffered, latched, or synchronization-sensitive. Examples include `*_UPDATE_LOCK`, `*_UPDATE_PENDING`, `*_UPDATE_TAKEN`, `CRTC_MASTER_UPDATE_LOCK`, `CRTC_MASTER_UPDATE_MODE`, `SCL_UPDATE`, `BLND_UPDATE`, cursor update locks, graphics surface update locks, vertical update locks, GSL controls, DRR controls, and trigger controls. The macro definitions do not enforce sequencing; callers must program them in the order required by the display hardware.

Status and interrupt fields are also stateful. Many masks describe bits that enable, mask, acknowledge, clear, or report sticky events. Misidentifying a status bit as an enable bit, or writing a clear mask at the wrong time, can lose diagnostic information or leave interrupt sources active.

## Dependencies And Integration Points

This chunk depends on the rest of `dce_12_0_sh_mask.h` for a complete include-guarded header and on `dce_12_0_offset.h`/`dce_12_0_d.h` for matching register addresses. It is meaningful only when paired with DCE 12.0 register offsets and the SOC15 base-index model used by the AMDGPU display code.

Direct includes in this tree include `display/dc/dce120/dce120_timing_generator.c`, `display/dc/hwss/dce120/dce120_hwseq.c`, `display/dc/irq/dce120/irq_service_dce120.c`, `display/dc/gpio/dce120/hw_translate_dce120.c`, `display/dc/gpio/dce120/hw_factory_dce120.c`, `display/dc/resource/dce120/dce120_resource.c`, and `amdgpu/gmc_v9_0.c`.

The main integration surfaces are DRM/KMS modesetting, vblank/vupdate/page-flip interrupt handling, display hardware sequencing, display pipe resource construction, cursor programming, surface flips, color management, scaling, formatter output programming, display memory fetch control, power gating/reset, display performance counters, CRC capture, and GPU memory-controller diagnostics involving DCE clients.

The generated names are ASIC-generation specific. Nearby headers for DCE 6.0, 8.0, 10.0, 11.0, 11.2, and DCE 12.0 offsets contain overlapping block and field names with generation-specific addresses or field coverage. Mixing DCE versions can compile in some macro contexts but program the wrong hardware field.

## Risks And Edge Cases

The highest risk is numeric drift from the authoritative ASIC register database. These constants are opaque to the compiler: a wrong shift or mask still builds but can silently program unrelated bits in display hardware.

This chunk starts and ends inside larger logical blocks. It begins with only the final mask for `DCP4_COMM_MATRIXB_TRANS_C13_C14`, whose shift definitions and first mask are in the previous chunk, and ends in `DCP5_GRPH_UPDATE`, before DCP5 graphics flip/address-in-use/interrupt and later DCP5 fields. The final merged file report should avoid treating this range as a complete DCP4 or DCP5 description.

Repeated pipe-instance names are easy to confuse. Pipe 4 macros such as `CRTC4_*`, `DCP4_*`, `SCL4_*`, `BLND4_*`, `LB4_*`, `FMT4_*`, and `DMIF_PG4_*` mirror other pipe instances. Copying a field from the wrong instance or combining a pipe-4 field with the wrong offset/base can affect another display pipe or no useful register at all.

Wide masks and packed 16-bit fields appear throughout matrix, color, clamp, CRC, position, and seed registers. Off-by-one shifts or sign/width assumptions can corrupt adjacent channels, coordinates, coefficients, or control bits. Surface address fields split low and high address bits; programming only one side or applying the wrong alignment mask can point scanout or cursor fetches at the wrong memory.

Timing and memory-fetch fields can cause visible failures. Wrong CRTC totals, blanking, sync polarity, DRR, GSL, or trigger fields can blank a monitor or destabilize vblank accounting. Wrong DMIF urgency/stutter/watermark fields can cause underflow. Wrong SCL/FMT/DCP color and dithering fields can produce subtle image quality regressions that compile and modeset successfully.

Power/reset fields in DCFE4 are sensitive because they affect multiple sub-block memories and clocks. Incorrect use can leave a sub-block reset, powered down, or reporting stale status while later programming assumes it is live.

## Test Signals

There are no unit tests for this header chunk alone. Useful validation starts with build coverage for AMDGPU/DC configurations that include `dce_12_0_sh_mask.h`, especially DCE 12.0 timing generator, IRQ service, hardware sequencing, GPIO, resource, and GMC code.

Generated-header integrity should be checked against the authoritative DCE 12.0 register database or a known-good upstream generated header. The comparison should focus on this chunk's repeated pipe-4 blocks, the DCP4-to-LB4 and FMT4-to-DCP5 boundaries, packed coefficient/color fields, interrupt clear/mask fields, and address high/low masks.

Runtime signals include successful modeset across all available DCE 12.0 pipes, stable vblank and vupdate events, correct page flips and cursor updates, no display underflow interrupts, correct suspend/resume reprogramming, and no hangs during display power-gating transitions.

Pipeline validation should exercise framebuffer formats, tiling/swizzle settings, primary and secondary surface addresses, cursor formats and positions, color keying, degamma/gamut/regamma/LUT updates, scaling ratios and viewport changes, formatter pixel encodings including 4:2:0 and stereo modes, spatial/temporal dithering, and clamp behavior.

Interrupt and diagnostic validation should cover CRTC vertical interrupts, vupdate and range timing status, DCP page-flip and underflow status, BLND underflow status, DC_PERFMON7 counter programming/readback, DCP/CRTC/FMT CRC capture paths, DMIF DVMM status, and surface counter outputs. These tests catch polarity, clear-mask, latch, and field-width mistakes that compile-time checks cannot see.

### subset-b-001548: lines 27329-29825

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 27329-29825

## Scope And Purpose

This chunk is a generated AMD DCE 12.0 register field mask/shift table for display instance 5. It contains no executable C logic. Its purpose is to publish compile-time bitfield metadata used by AMDGPU display code when composing or decoding MMIO register values for the sixth display pipe/controller path.

The source path is under a local `ceph-client` mirror, but this file is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The chunk starts in the middle of `DCP5_GRPH_UPDATE`: lines 27329-27337 contain only the remaining `*_MASK` definitions for graphics surface/mode update state, update locks, and XDMA flip controls. The earlier `DCP5_GRPH_UPDATE` shifts and first masks are owned by the previous chunk. The chunk then covers full or near-full mask/shift families for:

- `DCP5_*`: display controller plane 5 graphics, color, cursor, LUT, CRC, XDMA, and surface-counter fields.
- `LB5_*`: line-buffer 5 data format, memory, vline/vblank interrupts, keyer, buffer-status, urgency, and MVP flip fields.
- `DCFE5_*`: display controller front-end 5 clock, reset, memory power, flush, and miscellaneous fields.
- `DC_PERFMON8_*`: performance counter/monitor 8 control, status, counted-value, high/low, and interrupt fields.
- `DMIF_PG5_*`: display memory interface page 5 pipe arbitration, watermark, urgency, stutter, low-power, and DVMM status fields.
- `SCL5_*`: scaler 5 coefficient RAM, mode/taps/filter ratios, viewport, update, sharpening, overscan, and mode-change detector fields.
- `BLND5_*`: blender 5 control, secondary-mode, update, underflow interrupt, v-update lock, and register-update status fields.
- `CRTC5_*`: timing-generator/CRTC 5 timing, sync, trigger, count, blanking, stereo, snapshot, interrupt, CRC, external timing sync, static-screen, 3D, GSL, range-timing, and DRR fields.
- `FMT5_*`: formatter 5 clamp, dynamic expansion, pixel encoding/subsampling, and the shift half of bit-depth/dither control.

The chunk ends inside `FMT5_FMT_BIT_DEPTH_CONTROL`: lines 29809-29825 define the shifts for truncation, spatial dither, randomization, temporal dither, temporal levels, reset, and FRC selectors, while the corresponding masks continue in the following chunk.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or storage objects in this range. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register prefixes identify repeated display-pipe instance 5 blocks, while the companion address header provides `mm<REGISTER>` addresses and base-index macros.

The companion address file for this ASIC is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h`. This mask header is included by DCE 12.0 display code such as `dce120_resource.c`, `dce120_timing_generator.c`, `irq_service_dce120.c`, `dce120_hwseq.c`, GPIO translation/factory code, and `amdgpu/gmc_v9_0.c`.

Important field groups in this chunk:

- `DCP5_GRPH_*` covers plane address-in-use fields, display flip queue control/status, page-flip interrupt status/control, compressed surface address and pitch, outstanding-request limits, prescale bias/scale fields, input/output CSC matrices, common transform matrices, denorm, output rounding/clamp, keying ranges, degamma/gamut/regamma controls, DCP spatial dither, cursor state, LUT programming, DCP CRC, DVMM PTE controls, GSL, stereo sync flip, rotation, XDMA underflow/flip timeout/delay/recovery, alpha control, and surface-counter output.
- `DCP5_CUR_*` exposes cursor enable/type/mode/2x-magnify/force-MC-on bits, cursor size/address/position/hot spot/color registers, cursor update pending/taken/lock/stereo fields, request filtering, and stereo-offset controls.
- `DCP5_DC_LUT_*` and `DCP5_REGAMMA_*` define color LUT and piecewise/regamma region metadata, including index, data, write-enable masks, autofill, control flags, black/white offsets, region counts, slopes, bases, and segment offsets.
- `LB5_*` defines line-buffer format and memory mode controls, vertical line interrupt windows/status, vblank status, sync reset selection, black/keyer colors, urgency controls/status, buffer status, no-outstanding-request status, and MVP AFR/in-band flip controls.
- `DCFE5_*` defines front-end clock enables/gates, soft reset and reset status bits, memory powerdown/shutdown/force controls and status for cursor/WDATA/REQ/pipe/channel/TLB memories, delayed memory powerdown delay, and flush trigger/status fields.
- `DC_PERFMON8_*` defines performance counter selection and enablement, counter clear/send/reset/start actions, counted-value type/unit/threshold, interrupt enable/status/clear/type, high/low counter data, and monitor state selectors.
- `DMIF_PG5_*` defines pipe arbitration slots, urgency latency/watermark controls, watermark-mask selection, urgent-level thresholds, stutter enable/deep-sleep/watermark fields, stutter-exit self-refresh settings, low-power/repeater controls, preprocessor check controls, and DVMM status flags.
- `SCL5_*` defines scaler coefficient RAM select and tap data, scaling mode, tap counts, bypass/manual-replicate/auto-mode controls, horizontal/vertical filter controls, scale ratios, phase inits, round offsets, update-mode/taken/pending bits, sharpening, ALU, coefficient RAM conflict status, viewport start/size, overscan, and mode-change detection/masking.
- `BLND5_*` defines blender enable/mode/alpha/select flags, stereo and feedthrough controls, source current, viewport enable, secondary-mode format/blanking/input alpha/lut/transfer fields, update and underflow interrupt bits, v-update lock timing, and update status flags.
- `CRTC5_*` is the largest group in this chunk. It includes horizontal/vertical totals, blank and sync ranges, V-total min/max/DRR controls, nominal and update interrupt status, trigger A/B source/polarity/frequency/delay fields, manual trigger bits, force-count-now and flow-control state, AV sync counters, CRTC enable/control/blank/interlace/field indication/status/count fields, stereo control/status, snapshot fields, start-line control, interrupt control, update locks, double buffering, VGA capture, test patterns, master update lock/mode, MVP in-band control, master enable, stop-off counters, overscan/blank/black colors, vertical interrupt windows/control, CRC windows/data, external timing sync/loss/signal interrupts, static-screen detection, 3D structure, GSL controls, range-timing interrupt status, and DRR/XDMA prefetch metadata.
- `FMT5_*` begins formatter 5 output-stage metadata: component clamps, dynamic expansion enable/mode, format control for stereo sync override, spatial dither frame counter, pixel encoding, subsampling mode/order, CbCr bit-reduction bypass, source select, 4:2:0 phase lock and clear, plus the shift definitions for bit-depth/truncation/dither/FRC control.

## Control Flow

This chunk has no runtime control flow. Every meaningful line is a preprocessor definition that the C compiler substitutes into register-helper expressions.

Runtime flow exists in consumers that pair these masks/shifts with addresses and base offsets. DCE 12.0 code includes this header alongside `dce_12_0_offset.h`, `soc15_hw_ip.h`, and `vega10_ip_offset.h`. Register helpers such as `generic_reg_update_soc15`, `generic_reg_set_soc15`, `dm_read_reg_soc15`, `get_reg_field_value`, and FD-style field descriptors build read-modify-write operations from this generated metadata.

A representative control path for CRTC fields is visible in `dce120_timing_generator.c`: the timing generator reads `mmCRTC0_CRTC_STATUS` with an instance offset and decodes `CRTC_V_BLANK`, updates `CRTC0_CRTC_MASTER_UPDATE_MODE`, updates `CRTC0_CRTC_MASTER_UPDATE_LOCK`, reads `CRTC0_CRTC_STATUS_FRAME_COUNT`, and uses field macros through helper wrappers. For controller 5, the same register layout is represented by the `CRTC5_*` macro family in this chunk and addressed through per-instance offsets built in resource code.

A representative interrupt integration path is visible in `irq_service_dce120.c`: IRQ table macros compose enable, ack, status registers, and field masks for HPD, page-flip, vupdate, and vblank sources. The `DCP5_GRPH_INTERRUPT_*`, `CRTC5_CRTC_INTERRUPT_CONTROL`, `CRTC5_CRTC_V_UPDATE_INT_STATUS`, and `CRTC5_CRTC_VERTICAL_INTERRUPT*_CONTROL` definitions in this chunk are the instance-5 bitfield vocabulary for those interrupt paths.

Because the header is declarative, it does not enforce sequencing. Consumers must order writes around update locks, double-buffered pending/taken bits, self-clearing clears, interrupt masks, power-gated blocks, PLL/timing enablement, and display blanking windows.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. The macros describe state in hardware MMIO registers.

The hardware state represented here spans several display pipeline categories:

- Plane state: graphics surface in-use addresses, update pending/taken bits, flip queue state, compressed-surface metadata, cursor metadata, LUT/regamma state, CSC matrices, keying, dither, alpha, and XDMA recovery/underflow status.
- Memory/frontend state: line-buffer format/memory/urgency state, DCFE clock/reset/memory-power state, DMIF arbitration/watermark/stutter/DVMM state, and front-end flush state.
- Timing state: CRTC totals, blanks, syncs, counters, status positions, master/update locks, static-screen state, 3D/stereo state, range timing, GSL, external timing sync, vertical interrupts, vblank/vupdate status, CRC capture windows, and DRR state.
- Output formatting state: formatter clamp, dynamic expansion, pixel encoding/subsampling, source select, and dither/truncation mode fields.
- Diagnostic state: DCP/CRTC CRC data, DC performance counters, line-buffer and blender underflow/status bits, scaler coefficient conflict status, and XDMA/cache-underflow detection.

Persistence is register-specific and not encoded by this generated table. Some fields are durable control bits that remain programmed until another driver write, block reset, suspend/resume transition, power-gating transition, modeset, or GPU reset. Other fields are transient hardware status, sticky interrupt/status bits, write-one-to-clear bits, self-clearing update requests, or read-only counters. The naming hints at behavior (`*_CLEAR`, `*_STATUS`, `*_PENDING`, `*_TAKEN`, `*_UPDATE_LOCK`, `*_RESET`, `*_ACK`, `*_INT_STATUS`, `*_INT_ENABLE`, `*_INT_MSK`), but this header does not declare access type or side effects.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header convention and on DCE 12.0 hardware documentation. It is meaningful only when used with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h` for MMIO addresses and base-index macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_enum.h` for symbolic field values where applicable.
- SOC15 base-address metadata from `soc15_hw_ip.h` and `vega10_ip_offset.h`.
- AMD display register helpers such as `reg_helper.h`, `generic_reg_update_soc15`, `generic_reg_set_soc15`, `dm_read_reg_soc15`, `get_reg_field_value`, and generated FD macros.

The direct include surface found in this source tree includes:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_factory_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_translate_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c`

The practical integration points are AMD display core resource construction, CRTC/timing generator programming, page flip and vblank/vupdate IRQ handling, graphics plane and cursor programming, scaler/line-buffer/blender programming, display-memory-front-end power and arbitration control, color pipeline programming, CRC/debug validation, and formatter output setup.

The instance-5 nature matters. DCE 12.0 resource code constructs offsets for six CRTC instances (`CRTC0` through `CRTC5`) and similar repeated display blocks. These macros must stay layout-compatible with the corresponding `DCP5`, `LB5`, `DCFE5`, `DMIF_PG5`, `SCL5`, `BLND5`, `CRTC5`, and `FMT5` address definitions in the offset header.

## Risks And Edge Cases

- Numeric masks and shifts are hardware ABI. A one-bit error can compile cleanly but cause incorrect MMIO updates, corrupt neighboring fields, leave interrupts uncleared, or program the wrong display behavior.
- The chunk is generated and highly repetitive. Human edits to a single `5` instance, line-buffer/scaler/blender prefix, or similarly named field are easy to miss in review. Prefer regenerating from the authoritative register database over hand-editing.
- The chunk boundaries split register families. Any per-file synthesis must merge this document with adjacent chunk research before treating `DCP5_GRPH_UPDATE` or `FMT5_FMT_BIT_DEPTH_CONTROL` as fully described.
- Update-lock and pending/taken fields are sequencing-sensitive. Misuse of `DCP5_GRPH_UPDATE`, `DCP5_CUR_UPDATE`, `SCL5_SCL_UPDATE`, `BLND5_BLND_UPDATE`, `CRTC5_CRTC_UPDATE_LOCK`, `CRTC5_CRTC_MASTER_UPDATE_LOCK`, or `CRTC5_CRTC_DOUBLE_BUFFER_CONTROL` can create torn updates, missed latches, or modeset races.
- Interrupt and status fields mix enable/mask/status/clear semantics. Page-flip, vblank, vupdate, vertical interrupt, CRTC static-screen, external timing sync, range timing, LB vline/vblank, and blender underflow fields must be used with the correct clear or mask polarity.
- Memory/power fields touch live display fetch paths. Incorrect DCFE memory power, DMIF arbitration/watermark/stutter, line-buffer memory, or DCP DFQ/XDMA settings can surface as underflow, black frames, page-flip stalls, display corruption, resume failures, or power-management regressions.
- Color pipeline fields are format-sensitive. CSC matrices, prescale, denorm, output rounding/clamp, key ranges, LUT/regamma, formatter pixel encoding/subsampling, and dither/truncation fields must match pixel format, color depth, gamut, and link encoding expectations.
- CRTC timing and DRR fields are mode-sensitive. Incorrect totals, min/max vertical totals, sync ranges, DRR control, external timing sync, GSL, stereo/3D, or master update mode can break vblank timing, variable refresh, genlock/swaplock, frame counting, or stereo output.
- Status fields are not self-describing. The macro table does not state whether a field is read-only, sticky, write-one-to-clear, write-zero-to-clear, reserved, or power-domain gated; callers need the hardware spec or existing driver sequence.

## Test Signals

Useful validation is mostly compile-time plus hardware/display behavior:

- Build AMDGPU/DC code for DCE 12.0 targets with warnings treated seriously; missing or renamed macros are caught at compile time by resource, timing-generator, IRQ, GPIO, and hwseq users.
- Compare generated masks/shifts against `dce_12_0_offset.h`, adjacent DCE 12.0 chunks, and older DCE/DCN generated headers for repeated register families to catch accidental instance or bit-position drift.
- Exercise modesets on all six display pipes, especially pipe/controller 5, and verify CRTC enable/disable, vblank counters, vupdate events, page flips, cursor movement, scaling, blending, color programming, and formatter output.
- Run vblank/page-flip interrupt tests and check that `DCP5_GRPH_INTERRUPT_*`, `CRTC5_CRTC_VERTICAL_INTERRUPT*`, and `CRTC5_CRTC_V_UPDATE_INT_STATUS` paths enable, fire, and clear without storms or lost events.
- Test high-risk modes: deep color, YCbCr/subsampled output, cursor and plane flips under load, scaling up/down, DRR/variable refresh, stereo/3D if supported, external timing sync/GSL paths, suspend/resume, display hotplug, and multi-display configurations using the last pipe.
- Use CRC/debug paths where available: DCP CRC, CRTC CRC windows, performance monitor counters, line-buffer/scaler/blender underflow or conflict status, XDMA/cache underflow status, and DMIF/DVMM status can provide direct evidence that the fields are mapped correctly.
- Watch for negative signals in kernel logs and display behavior: underflow reports, stuck vblank/page-flip waits, failed modeset commits, black screens, link retraining, cursor corruption, color shifts, flicker during flips, frame-counter anomalies, or power-management resume regressions.

### subset-b-001549: lines 29826-32324

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 29826-32324

## Purpose

This chunk is a generated AMD DCE 12.0 shift/mask register header section. It contains C preprocessor constants only; there are no functions, structs, storage objects, or executable algorithms. The constants define bit positions (`__SHIFT`) and bit masks (`_MASK`) for display-engine registers used by AMDGPU display programming.

The range starts at the tail of the `dce_dc_fmt5_dispdec` formatter block, then covers a full video/underlay display pipe path for instance 0: `UNP0`, `LBV0`, `SCLV0`, `COL_MAN0`, `DCFEV0`, `DC_PERFMON11`, `DMIFV_PG0`, `BLNDV0`, and the beginning of `CRTCV0`. These blocks describe how software programs surface fetch, line buffers, scaling, color management, clock/power/reset, performance monitoring, display memory interface watermarks, blending, timing generation, interrupts, CRC capture, and external timing synchronization.

The header is hardware ABI metadata. Consumer code combines these masks and shifts with the matching register offsets from `dce_12_0_offset.h` and enum values from related DCE headers, then reads or writes GPU registers through AMDGPU/DAL register helpers.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The public surface is a large set of `#define` names following this pattern:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same register field after shifting.

Major register families in this chunk are:

- `FMT5_FMT_*`: formatter instance 5 fields for bit-depth control, dither random seeds, clamp control, formatter CRC setup/signature registers, side-by-side stereo active width, and 4:2:0 horizontal blank early start. These fields participate late in the display pipe where pixels are clamped, dithered, optionally CRC-sampled, and formatted for output.
- `UNP0_UNP_GRPH_*`: underlay/graphics plane fields for enabling scanout, selecting graphics depth/format, tiling/banking, pipe configuration, endian and RGB crossbar swaps, luma/chroma primary and secondary surface addresses, bottom-field addresses, high address bits, pitch, source offsets, source rectangle start/end, update locking, in-use surface readback, stereo flip state, page-flip interrupt state, CRC capture, line-buffer gap, and hardware rotation.
- `UNP0_UNP_DVMM_*`: virtual-memory PTE behavior for luma and chroma planes, including single-PTE use, page width/height, minimum PTEs before flip, PTE buffer modes, PTE requests per chunk, and outstanding PTE request limits. These fields connect surface flip/display fetch to GPU memory translation.
- `LBV0_LBV_*`: line-buffer vertical block fields for pixel depth/expansion/reduction, interleave, dynamic pixel depth, dither, prefetch, request mode, alpha enable, memory control/size, desktop height, vertical line interrupt windows, vertical counters and snapshot counters, interrupt masks, vline/vblank status and ack bits, reset selection, black/keyer color controls, buffer level/urgency/status, and no-outstanding-request status.
- `SCLV0_SCLV_*`: scaler vertical block fields for coefficient RAM selection/data, scaler mode, tap counts, boundary/early-EOL/phase controls, manual and automatic replicate/ratio calculation, horizontal and vertical filter ratios and initial phases for luma and chroma, bottom-field initial phases, round offsets, update lock/taken/pending status, viewport start/size for primary/secondary and chroma planes, extended overscan, and mode-change detection/ack.
- `COL_MAN0_*`: color-management fields for update locking, input CSC mode/type/conversion, input and output CSC matrix coefficients for A/B banks, prescale mode and RGB bias/scale values, output CSC mode, denorm clamp, floating-point converted-field access, regamma control and LUT index/data/write masks, piecewise regamma regions for A/B banks, pack/output FIFO errors and acks, input gamma LUT autofill/index/data/color, input gamma control, black/white offsets, degamma mode, gamut-remap mode, and gamut-remap matrix coefficients.
- `DCFEV0_*`: front-end vertical block clock gating, block soft reset, DMIFV clock/reset/buffer mode, DMIFV and local memory power control/status, memory-power mode selection, luma/chroma flush status and clear bits, and miscellaneous self-refresh allowance.
- `DC_PERFMON11_*`: display performance monitor counter fields for event selection, current-value selection, increment/run/offset/restart/interrupt controls, counter state, performance monitor control, current-value interrupt thresholds/status/clear, and low/high counter value readback.
- `DMIFV_PG0_DPGV0_*` and `DMIFV_PG0_DPGV1_*`: display memory interface pipe-group fields for arbitration weights, watermark masks, urgency low/high watermarks, DPM enable, stutter/self-refresh controls, NB P-state change controls, non-latched stutter controls, repeater programming, and pre-processing buffer-check disable. Both DPGV0 and DPGV1 expose the same shape for two pipe-group instances.
- `BLNDV0_BLNDV_*`: blender vertical block fields for global gain/alpha, blend mode, stereo type/polarity, feedthrough, alpha mode, overlap-only and premultiplied behavior, stereo matrix control, pixel-through-insert/new-pixel controls, update locking, underflow interrupt status/ack/mask/pipe index, V-update locking across graphics/surface/cursor/scaler/blender clients, and aggregate register-update status.
- `CRTCV0_CRTCV_*`: beginning of timing-generator instance 0 fields for horizontal and vertical totals, blanking and sync windows, sync polarities, VBI end, dynamic vertical total min/max/control, vertical-total and nominal-vsync interrupt status, DTM test controls, trigger A/B controls and manual trigger, force-count-now, flow control, stereo force/AV-sync counters, CRTC enable/control/status, blank/interlace/field control, pixel readback, count/reset/snapshot/status readback, stereo control/status, update locks, test pattern programming, master update controls, MVP in-band control insertion, master enable, V-update interrupt status, overscan/blank/black colors including extension bits, vertical interrupt positions/controls, CRTC CRC setup/windows/data, and external timing sync control/window/loss interrupt fields.

## Control Flow

This header chunk has no runtime control flow. It contributes symbolic bit positions and masks that are consumed by display driver code.

A typical runtime use pattern outside this header is:

1. AMDGPU display code computes a modeset, plane, scaling, color, memory, or timing state from DRM state and hardware capabilities.
2. The driver selects the corresponding register address from `dce_12_0_offset.h`, such as `mmUNP0_UNP_GRPH_UPDATE`, `mmSCLV0_SCLV_UPDATE`, `mmCOL_MAN0_COL_MAN_UPDATE`, `mmCRTCV0_CRTCV_CONTROL`, or `mmDMIFV_PG0_DPGV0_PIPE_STUTTER_CONTROL`.
3. It inserts field values using the `__SHIFT` and `_MASK` constants in this header, often via `REG_UPDATE`, `REG_SET`, `dm_read_reg`, `dm_write_reg`, `RREG32`, or `WREG32` style helpers.
4. Hardware latches some values immediately and others only when update-lock and vertical-update rules are satisfied.
5. Status, pending, taken, interrupt, CRC, counter, and in-use fields are later read back through the same field definitions.

Several block families show explicit sequencing constraints through their field names:

- `*_UPDATE` registers have pending/taken/lock bits (`UNP0_UNP_GRPH_UPDATE`, `SCLV0_SCLV_UPDATE`, `COL_MAN0_COL_MAN_UPDATE`, `BLNDV0_BLNDV_UPDATE`). These imply that mode, surface, coefficient, color, and blender updates are intended to be staged and latched atomically.
- Interrupt/status registers pair event bits with clear or ack bits, such as `UNP0_UNP_GRPH_INTERRUPT_STATUS`, `LBV0_LBV_VLINE_STATUS`, `COL_MAN0_PACK_FIFO_ERROR`, `BLNDV0_BLNDV_UNDERFLOW_INTERRUPT`, `CRTCV0_CRTCV_V_TOTAL_INT_STATUS`, and `CRTCV0_CRTCV_VERTICAL_INTERRUPT*_CONTROL`.
- Memory and power control registers pair force/disable/select fields with status fields, such as `DCFEV0_DCFEV_DMIFV_MEM_PWR_CTRL` and `DCFEV0_DCFEV_DMIFV_MEM_PWR_STATUS`.
- CRC and performance monitor fields require enable/select programming followed by readback from result registers (`UNP0_UNP_CRC_*`, `FMT5_FMT_CRC_*`, `CRTCV0_CRTCV_CRC*`, `DC_PERFMON11_*`).

## State And Persistence Behavior

The header itself stores no state and persists nothing. The state described by these macros lives in GPU display registers and in the driver state that decides what to write.

Important hardware state represented by this chunk includes:

- Formatter output processing state: truncation, spatial/temporal dithering, random seeds, clamp enable and color format, formatter CRC enable/mode/window/signature state, stereo active width, and 4:2:0 blanking alignment.
- Plane fetch state: plane enable, pixel format/depth, tiling, bank geometry, pipe configuration, address translation, privileged access, endian/channel crossbar, surface addresses for luma/chroma primary/secondary/top/bottom fields, pitch, offsets, source rectangle, surface-update locks, in-use surface addresses, flip-pending state, page-flip interrupt state, and hardware rotation.
- Display virtual-memory fetch state: PTE page dimensions, PTE buffering, minimum PTEs before flip, request chunking, and outstanding PTE limits for luma and chroma.
- Line-buffer state: pixel format expansion/reduction, prefetch/request behavior, vertical counter snapshots, vline/vblank event state, buffer occupancy and urgency, black/keyer color values, reset selection, and outstanding request completion.
- Scaler state: coefficient RAM contents, selected filter type/phase/tap pair, tap counts, scale ratios, initial phases for luma/chroma and top/bottom fields, viewport geometry, overscan, update locks, and mode-change detection.
- Color state: CSC matrices, prescale values, denorm clamp, regamma LUT and piecewise region descriptors, input gamma LUT/control, black/white offsets, degamma/gamut-remap modes and coefficients, and FIFO error status.
- Front-end and memory-power state: clock gating, soft reset assertion, DMIFV clock/reset, buffer mode, memory power force/disable/mode selection, memory power status, and luma/chroma flush completion.
- Memory-interface state: pipe arbitration, urgency and stutter watermarks, DPM and self-refresh behavior, NB P-state change allowance, and DPG repeater/check behavior.
- Blender state: blend mode, alpha policy, stereo policy, feedthrough, super-AA degamma/regamma, underflow interrupt state, and cross-block V-update locks/status.
- Timing generator state: active timing totals and sync positions, dynamic refresh/vertical total controls, triggers, flow control, AV sync/stereo status, CRTC enable/blank/interlace/test pattern/master update state, scanout position counters, interrupt enables/clears, CRC windows/results, and external timing sync state.

Persistence is register-specific. Many fields persist until a modeset, plane update, color update, reset, suspend/resume, runtime power transition, or GPU reset changes them. Pending/status/interrupt/ack/clear fields are transient and may be consumed or cleared by hardware or interrupt handlers. In-use surface address and counter fields are readback snapshots of live hardware state rather than durable software state. LUT, coefficient, and matrix fields persist in display-block memory/registers while the block remains powered, but they can be lost or invalidated by display block reset or power-gating transitions.

## Dependencies And Integration Points

This chunk depends on the generated DCE 12.0 register contract. Its constants are meaningful only with sibling address and enum headers under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/`, especially:

- `dce_12_0_offset.h`, which provides `mm*` register addresses and base-index macros for the register names defined here.
- Other `dce_12_0_*` headers that provide related register definitions and any enum/value encodings used in these fields.
- Earlier and later sections of `dce_12_0_sh_mask.h`, because this chunk starts in the middle of `FMT5` and ends in the middle of `CRTCV0`; complete per-file research must merge this chunk with neighboring chunks.

Primary integration points are AMDGPU display and Display Core code paths that program DCE hardware:

- DRM plane and framebuffer setup maps DRM formats, tiling metadata, pitches, GPU addresses, source rectangles, and stereo/rotation state into `UNP0_UNP_GRPH_*`, `UNP0_UNP_DVMM_*`, and `LBV0_LBV_*` fields.
- Atomic update paths coordinate `UNP0`, `SCLV0`, `COL_MAN0`, `BLNDV0`, and `CRTCV0` update locks so visible state changes latch coherently on vblank/update boundaries.
- Scaling setup writes `SCLV0` taps, filter ratios, coefficient RAM, viewport geometry, chroma-specific geometry, and overscan.
- Color-management setup writes `COL_MAN0` CSC, prescale, clamp, degamma, regamma, input gamma, and gamut-remap fields.
- Display memory bandwidth and power-management code programs `DMIFV_PG0` arbitration/watermark/stutter/P-state fields and `DCFEV0` memory power/clock/reset fields.
- Interrupt handlers and vblank/event code interact with `LBV0`, `UNP0`, `BLNDV0`, and `CRTCV0` status/ack/clear fields.
- Debug and validation tooling uses CRC registers in `FMT5`, `UNP0`, and `CRTCV0`, performance monitor 11 registers, timing status counters, snapshot registers, test pattern registers, and pixel readback fields.

Although the path is under a `ceph-client` source mirror, this file is AMD GPU display hardware metadata. It does not implement Ceph filesystem behavior, network protocols, storage replication, distributed locking, or persistent filesystem state.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These are plain integer macros; a wrong mask, wrong shift, stale generated value, or mismatched register address can compile successfully while causing display corruption, blank screens, hangs, lost interrupts, or power-management failures.

High-risk areas in this chunk include:

- Surface address and format programming. `UNP0_UNP_GRPH_*ADDRESS*`, pitch, tiling, pipe config, bank geometry, luma/chroma pairing, source offsets, and graphics format fields must match the actual framebuffer allocation and memory layout. Bad values can fetch the wrong memory, produce color/channel corruption, trigger memory faults, or underflow the display pipe.
- Virtual-memory display fetch. `UNP0_UNP_DVMM_*` PTE dimensions, minimum-PTE-before-flip, and outstanding request limits affect flip safety and memory-translation latency. Incorrect tuning can cause page flips before enough PTEs are ready, visible corruption, underflow, or faults during scanout.
- Update locking. `*_UPDATE_LOCK`, `*_UPDATE_PENDING`, `*_UPDATE_TAKEN`, `BLNDV0_BLNDV_V_UPDATE_LOCK`, and `CRTCV0_CRTCV_UPDATE_LOCK` fields are used to align multi-register updates with display timing. Missing or incorrectly ordered locks can expose partially updated surfaces, scaler ratios, color matrices, or timing state.
- Interrupt ack and clear bits. Fields named `ACK`, `CLEAR`, `INT_CLEAR`, or status masks may be write-one-to-clear or otherwise edge-sensitive depending on hardware semantics. A read-modify-write that preserves an ack bit accidentally, or clears before software records state, can lose vblank, vline, underflow, page-flip, vertical-total, external-sync, or FIFO error events.
- Color pipeline precision. CSC, prescale, denorm clamp, LUT, regamma region, degamma, and gamut-remap fields encode signed/fixed-point hardware formats. Off-by-one ranges, wrong coefficient bank, wrong write mask, or wrong LUT index sequencing can cause incorrect gamma, color-space conversion, clipping, banding, or invalid HDR/SDR presentation.
- Scaler coefficient and viewport programming. Coefficient RAM selection/data, tap counts, ratios, initial phases, chroma-specific ratios, and bottom-field phases must be consistent with source dimensions, interlace state, and 4:2:0 formats. Bad values can cause shimmering, line phase errors, chroma misalignment, or scaler mode-change events.
- Memory-interface watermarks. `DMIFV_PG0_DPGV*` urgency/stutter/NB P-state/self-refresh fields directly affect bandwidth and power behavior. Underestimated watermarks can cause underflow; overconservative values can block power savings or clock transitions.
- Clock, reset, and memory power controls. `DCFEV0` soft reset and power fields can invalidate state in dependent blocks. Programming these fields while a pipe is active, or failing to reinitialize LUT/coeff/state after reset or power gating, can break scanout.
- Timing generator programming. `CRTCV0` totals, blanking, sync, dynamic vertical total, trigger, flow control, stereo, interlace, and external timing sync fields are timing-sensitive. Invalid combinations can violate mode timings, break vblank accounting, interfere with variable refresh, or destabilize genlock/external sync.
- CRC and test/debug registers. CRC windows, select fields, continuous/one-shot modes, performance counters, test patterns, pixel readback, and DTM test fields can alter validation behavior and should not be left enabled unintentionally in normal modeset paths.

Generated-header maintenance is also risky. The same register names appear with addresses in `dce_12_0_offset.h`; masks here must remain synchronized with those addresses and with hardware documentation. Since the chunk starts after the beginning of `FMT5` and stops before the end of `CRTCV0`, reviewers need neighboring chunks before making whole-file conclusions.

## Test Signals

Useful validation signals for code that consumes this chunk include:

- Build coverage for AMDGPU display code that includes DCE 12.0 headers, catching missing or renamed macros.
- Modeset tests across common RGB and YUV/4:2:0 formats, tiled and linear framebuffers, multiple pitches, primary/secondary surfaces, stereo/interlace paths, and hardware rotation.
- Plane update and page-flip tests that verify pending/taken bits drain and no partial updates appear during atomic commits.
- CRC-based display tests using `FMT5`, `UNP0`, or `CRTCV0` CRC registers to confirm deterministic output for known framebuffers and color/scaler settings.
- Color-management tests for CSC matrices, gamma/degamma/regamma LUT programming, gamut remap, clamp ranges, and 10/12-bit paths.
- Scaler tests covering up/downscale ratios, luma/chroma viewports, coefficient loading completion, interlaced bottom-field initialization, and overscan.
- Interrupt tests for vblank/vline/page-flip/underflow/vertical-total/external-sync events, including verifying ack/clear behavior and absence of interrupt storms.
- Memory-bandwidth and power tests that exercise DPM, stutter, self-refresh, NB P-state changes, and watermark programming under high-resolution/high-refresh modes.
- Suspend/resume, runtime power management, GPU reset, and display hotplug tests that verify clock/reset/memory-power state is restored and no stale LUT/coefficient/surface state remains.
- Debug/performance monitor tests that confirm performance counter start/stop/restart/threshold behavior and CRTC status counter readback under active scanout.

### subset-b-001550: lines 32325-34820

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 32325-34820

## Purpose

This chunk is a generated AMD DCE 12.0 register shift/mask section. It has no executable logic; it publishes C preprocessor constants that describe bit positions and masks for display-engine registers. Driver code combines these constants with DCE 12.0 register addresses and enum values to program AMDGPU display hardware through register read/write helpers.

The range begins inside `CRTCV0_CRTCV_EXT_TIMING_SYNC_LOSS_INTERRUPT_CONTROL`, then covers the tail of CRTC vertical pipe 0 external timing/static-screen/3D/GSL fields. It then defines complete field maps for pipe-1 display blocks: `UNP1` underlay/graphics fetch, `LBV1` line buffer, `SCLV1` scaler, `COL_MAN1` color management, `DCFEV1` display front-end control, `DC_PERFMON12` performance counters, `DMIFV_PG1` display memory-interface arbitration for DPGV0/DPGV1, `BLNDV1` blender, and the beginning of `CRTCV1` timing-generator fields through the first fields of external timing sync loss interrupt control.

Although this path lives under a `ceph-client` source mirror, the content is AMDGPU kernel display hardware metadata. It does not implement Ceph filesystem behavior, distributed filesystem state, networking, or storage persistence.

## Important APIs, Types, And Constants

There are no functions, structs, typedefs, global variables, or runtime APIs in this chunk. The public interface is a set of `#define` constants named in the generated pattern:

- `<REGISTER>__<FIELD>__SHIFT`: low bit position for a register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field after placement in the 32-bit register value.

Major register families in this range are:

- `CRTCV0_CRTCV_EXT_TIMING_SYNC_*`, `CRTCV0_CRTCV_STATIC_SCREEN_CONTROL`, `CRTCV0_CRTCV_3D_STRUCTURE_CONTROL`, and `CRTCV0_CRTCV_GSL_*`: late pipe-0 timing fields for external sync enable/status/clear/type, static-screen interrupts, stereo/3D frame structure, and global swap-lock vsync gap/window/check-line control.
- `UNP1_UNP_GRPH_*`: pipe-1 graphics/underlay enable, surface format, tiling geometry, endian/channel crossbar, luma/chroma primary/secondary and bottom-field surface addresses, high address bits, pitch, source offsets, start/end coordinates, update locking, outstanding-request limits, in-use address readback, DVMM PTE sizing/arbitration, page-flip interrupts, stereo/interlace surface flip tracking, CRC registers, line-buffer data gap, and hardware rotation.
- `LBV1_LBV_*`: pipe-1 line-buffer data format, memory size/partition configuration, desktop height, vline/vline2/vblank interrupt windows and status/ack bits, sync reset selection, black/keyer colors, request/data FIFO level status, urgency thresholds, empty/full status and a no-outstanding-request indicator.
- `SCLV1_SCLV_*`: pipe-1 scaler coefficient RAM selection and tap data, scaler mode/tap count/control, manual replication, automatic ratio calculation, horizontal/vertical luma and chroma ratios and initial phases, bottom-field phase values, rounding offsets, scaler update lock/status, viewport start/size for primary/secondary and chroma paths, overscan extents, and mode-change detection.
- `COL_MAN1_*`: pipe-1 color-management update locking, input/output CSC mode and A/B coefficient matrices, prescale controls, denorm/clamp ranges, floating-point converted-field access, regamma control/LUT/index/write-enable fields, regamma region definitions for CNTLA/CNTLB, FIFO error ack fields, input-gamma LUT autofill/read-write/data controls, black/white offsets, degamma control, and gamut-remap matrix fields.
- `DCFEV1_DCFEV_*`: pipe-1 display front-end clock gates, soft resets for UNP/SCLV/CRTC/PSCLV/COL_MAN, DMIFV clock and soft reset, DMIFV and block memory power force/disable/status controls, luma/chroma flush indicators, and miscellaneous self-refresh ECO enable.
- `DC_PERFMON12_*`: DCE display performance-counter event selection, counter value selection, run/interrupt/restart/off-mask control, counter state/status, performance-monitor mode/control, compare-value interrupt fields, and high/low counter readout registers.
- `DMIFV_PG1_DPGV0_*` and `DMIFV_PG1_DPGV1_*`: display memory-interface arbitration, urgency watermarks, DPM enable, stutter and non-latched stutter controls, northbridge P-state change controls, repeater programming, and DMIF buffer pre-check disable for two DPGV instances.
- `BLNDV1_BLNDV_*`: pipe-1 blender gain/mode/stereo/alpha/feedthrough controls, stereo-matrix controls, pixel transport and SuperAA degamma/regamma controls, update locks, underflow interrupt ack/mask/pipe-index fields, V-update lock aggregation, and register-update pending status for graphics, surface, cursor, scaler, and blender clients.
- `CRTCV1_CRTCV_*`: pipe-1 timing generator fields for horizontal/vertical totals, blanking and sync windows, polarity controls, vertical-total min/max and events, trigger A/B selection/status/clear, force-count/force-vsync controls, flow control, AV sync, master enable, blank/interlace/stereo controls, status/readback counters, snapshot controls, start-line and interrupt control, double-buffering, VGA capture, test pattern, master-update lock/mode, MVP in-band status, overscan/blank/black colors, vertical interrupt 0/1/2, CRC windows/data, and external timing sync control/window fields.

The chunk is boundary-split: it starts after the first fields of `CRTCV0_CRTCV_EXT_TIMING_SYNC_LOSS_INTERRUPT_CONTROL` and ends after the first four `CRTCV1_CRTCV_EXT_TIMING_SYNC_LOSS_INTERRUPT_CONTROL` shift macros. Neighboring chunks are needed for the complete definitions of those two register groups.

## Control Flow

This header has no runtime control flow. Each line is a compile-time constant used by other AMDGPU display code.

Typical consumer control flow is:

1. Display code computes a software state such as mode timing, framebuffer address, tiling, scaling ratio, CSC matrix, gamma curve, power-management watermark, vblank interrupt policy, or CRC capture window.
2. The state is converted to field values, often using companion enum headers and block-specific programming helpers.
3. A register value is built by shifting values by the `__SHIFT` constants and constraining them with the matching `_MASK` constants.
4. The value is written through AMDGPU/DAL register helpers such as direct register macros or `REG_UPDATE`-style field update helpers.
5. Hardware latches the state immediately, at vertical update, after an update lock is released, after an interrupt ack/clear, or after a reset/power transition depending on the target register.

Several field groups represent synchronization points rather than simple configuration: `*_UPDATE_PENDING`, `*_UPDATE_TAKEN`, `*_UPDATE_LOCK`, `*_ACK`, `*_CLEAR`, `*_OCCURED`, `*_INT_STATUS`, `*_FORCE`, and `*_STATE` fields are normally used in polling, interrupt handling, or sequenced modeset flows.

## State And Persistence Behavior

The header itself stores no state and persists nothing. It describes state that lives in DCE 12.0 display hardware registers and in driver programming conventions.

Hardware state represented by this chunk includes:

- Scanout/underlay state: graphics enable, pixel depth/format, tiling layout, luma/chroma addresses, pitch, viewport coordinates, pending surface flips, stereo/interlace flip state, DVMM PTE behavior, and hardware rotation.
- Line-buffer state: pixel expansion/reduction/dither/prefetch policy, memory sizing, vertical line windows, vblank/vline interrupt flags, keyer colors, FIFO levels, urgency marks, and outstanding request completion.
- Scaler state: coefficient RAM selection/data, tap counts, luma/chroma scale ratios, initial phases for top/bottom fields, viewport and overscan extents, update lock state, and mode-change detection status.
- Color pipeline state: input/output CSC matrices, prescale and clamp values, degamma/regamma/gamut-remap modes, regamma LUT and region programming, input gamma LUT data and access mode, and FIFO underflow/overflow state.
- Front-end and memory-interface state: clock-gate disables, soft reset assertions, memory power force/disable/select/status bits, flush/deep-flush state, arbitration weights, DPM/stutter controls, self-refresh and NB P-state watermarks, and DMIF buffer checks.
- Blender and timing-generator state: alpha/stereo/feedthrough modes, update locks, underflow interrupts, CRTC horizontal/vertical timing, sync polarity, trigger inputs, AV sync counters, blanking/interlace/stereo flags, snapshot counters, vertical interrupt positions, CRC windows/data, test pattern controls, external timing sync windows, and static-screen/3D/GSL state inherited from the pipe-0 tail.

Persistence is register-specific. Many configuration bits persist until modeset, atomic commit, suspend/resume, GPU reset, display block reset, or runtime power management reprograms them. Status and interrupt fields are transient and may be level-sensitive, edge-latched, or write-one-to-clear depending on the register. Update-lock and double-buffer bits affect when pending writes become visible; power and reset bits can invalidate assumptions about downstream register contents.

## Dependencies And Integration Points

This file depends on AMD's generated ASIC register database. The constants in this chunk are meaningful only with the corresponding DCE 12.0 register address headers and enum headers in the same directory tree, especially generated `dce_12_0_*_d.h`, `dce_12_0_enum.h`, and adjacent sections of `dce_12_0_sh_mask.h`.

Important integration points include:

- AMDGPU Display Core and legacy DCE register programming paths that include generated shift/mask headers to implement modesets, page flips, color programming, interrupts, and power sequencing.
- DRM/KMS atomic state and framebuffer setup, where surface addresses, pitch, tiling, pixel format, viewport, scaler, color, and blender state are translated into `UNP1`, `LBV1`, `SCLV1`, `COL_MAN1`, and `BLNDV1` registers.
- Timing-generator and vblank handling code, where `CRTCV1` timing totals, blank/sync windows, status counters, vertical interrupts, snapshot, force-vsync, and update-lock fields drive CRTC enable/disable and event delivery.
- Display power-management and watermark calculations, where `DMIFV_PG1` arbitration, urgency, stutter, DPM, self-refresh, NB P-state, and `DCFEV1` memory-power fields are programmed from bandwidth and clock-state decisions.
- Color-management paths for CSC, degamma/regamma LUTs, gamut remap, clamp, and gamma LUT programming.
- Diagnostics and validation paths, including `UNP1` and `CRTCV1` CRC capture, `DC_PERFMON12` counters, test patterns, pixel readback, FIFO error status, and underflow interrupts.

The register fields also integrate with interrupt-service code. `UNP1_UNP_GRPH_INTERRUPT_*`, `LBV1_LBV_*_STATUS`, `BLNDV1_BLNDV_UNDERFLOW_INTERRUPT`, and `CRTCV1_CRTCV_*_INT*` fields provide mask, type, status, ack, and clear bits that must match the kernel's IRQ enable and acknowledgement ordering.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These are untyped integer macros; a wrong shift or mask can compile cleanly while corrupting a neighboring field or programming the wrong hardware behavior.

High-risk areas include:

- Surface address and layout fields. Incorrect address shifts, high-address masks, pitch, tiling, bank geometry, pipe config, array mode, endian swap, or luma/chroma split handling can cause blank scanout, corrupted images, channel swaps, page faults, or reads from the wrong framebuffer.
- Update synchronization. Misusing `*_UPDATE_LOCK`, `*_PENDING`, `*_TAKEN`, `*_DOUBLE_BUFFER`, and vertical-update lock fields can make atomic commits tear, remain pending indefinitely, or update only part of the pipe.
- Interrupt acknowledgement. `*_ACK`, `*_CLEAR`, `*_MASK`, `*_INT_STATUS`, and `*_INT_TYPE` fields are easy to confuse. Clearing before software samples status can lose vblank, vline, page-flip, underflow, trigger, snapshot, or external-sync events; failing to clear can flood IRQ handling.
- Watermark and memory-interface programming. Bad urgency, stutter, self-refresh, NB P-state, DPM, or arbitration values can produce display underflows, memory power transition failures, flicker during clock changes, or excessive power draw.
- Clock, reset, and memory-power controls. Asserting soft resets or forcing memory power states while a pipe is active can blank displays or leave dependent blocks in inconsistent state. Status fields must be polled or sequenced according to hardware rules not captured by this header.
- Color pipeline programming. CSC, regamma, input gamma, gamut remap, clamp, LUT index/data, and write-enable fields are dense and repetitive. Copy/paste or generation errors can produce wrong colors, banding, HDR/SDR range errors, or FIFO errors.
- CRTC timing fields. Off-by-one or mask-width mistakes in totals, blanking, sync, vertical interrupts, CRC windows, and external timing sync windows can break mode validation, vblank timing, CRC tests, stereo/interlace behavior, or synchronization to external sources.
- Chunk boundary splits. A reader looking only at this chunk will not see the complete `CRTCV0_CRTCV_EXT_TIMING_SYNC_LOSS_INTERRUPT_CONTROL` or `CRTCV1_CRTCV_EXT_TIMING_SYNC_LOSS_INTERRUPT_CONTROL` definitions. The merge lane should reconcile those with adjacent chunks before making per-register conclusions.

## Test Signals

Useful validation signals are mostly compile-time, generated-header, and hardware-behavior oriented:

- Kernel build coverage for DCE 12.0 display code that includes this header; renamed or missing field macros should fail compilation.
- Generated-register-map comparison against AMD's authoritative DCE 12.0 register database, verifying every shift and mask in lines 32325-34820.
- Modeset tests across multiple resolutions, refresh rates, interlace/progressive modes, stereo modes, blanking/sync polarities, and vertical interrupt positions.
- Page-flip and atomic commit tests that check `UNP1` surface update pending/taken state, update locks, in-use addresses, and vblank event delivery.
- Framebuffer format and tiling tests covering luma/chroma planes, bottom-field addresses, endian/channel crossbar behavior, pitch, offsets, hardware rotation, and DVMM/PTE cases.
- Scaler and viewport tests covering luma/chroma ratios, taps, coefficient RAM programming, overscan, bottom-field initialization, mode-change detection, and coefficient update completion.
- Color-management tests for input/output CSC matrices, prescale, denorm/clamp, regamma LUT and region setup, input gamma LUT access/autofill, degamma, and gamut remap.
- Underflow and power-management tests that exercise `LBV1`, `BLNDV1`, `DCFEV1`, and `DMIFV_PG1` status fields under high bandwidth, clock changes, stutter/self-refresh, suspend/resume, and GPU reset.
- CRC and test-pattern diagnostics verifying `UNP1` CRC, `CRTCV1` CRC0/CRC1 windows/data, pixel readback, and test pattern color/dynamic-range fields.
- Interrupt tests for vblank, vline/vline2, page flip, snapshot, vertical interrupts 0/1/2, trigger A/B, force-vsync, underflow, and external timing sync loss/status.

Regression symptoms from incorrect constants include corrupted or blank scanout, wrong colors, missed or repeated vblank/page-flip events, stuck update locks, display underflows, failed CRC validation, bad scaling, failed suspend/resume recovery, excess power use, or unstable external synchronization.

## Cross-Chunk Notes

This is one chunk of the large generated `dce_12_0_sh_mask.h` register map. Earlier chunks define preceding DCE 12.0 register field maps and the beginning of pipe-0 CRTC external timing sync loss control. Later chunks complete `CRTCV1_CRTCV_EXT_TIMING_SYNC_LOSS_INTERRUPT_CONTROL` and continue the remaining pipe-1 CRTC and subsequent display blocks. The final per-file document should treat this as generated hardware ABI metadata, not as a standalone module with independent initialization or control flow.

### subset-b-001551: lines 34821-37188

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h

Chunk: `subset-b-001551`
Covered source range: lines 34821-37188 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h`

## Purpose

This chunk is a generated AMD DCE 12.0 register field mask header section. It contains C preprocessor constants for bit positions and masks in display controller registers; it is not executable driver logic.

The covered range spans several display hardware areas:

- the tail of `CRTCV1_CRTCV_EXT_TIMING_SYNC_LOSS_INTERRUPT_CONTROL`, then `CRTCV1` external timing sync, static-screen, 3D-structure, and genlock/swaplock control fields;
- `HPD0` through `HPD5` hot-plug detect interrupt/status/control, fast-train, and toggle-filter fields;
- `DC_PERFMON2` performance counter and monitor control/status/value fields;
- `DP_AUX0` through `DP_AUX5` DisplayPort AUX controller fields, including software transaction control, arbitration, interrupts, line-status data, DPHY TX/RX tuning/status, and GTC sync status;
- the beginning of the `DIG0` stream encoder front-end fields: `DIG_FE_CNTL`, `DIG_OUTPUT_CRC_CNTL`, and the first `DIG_OUTPUT_CRC_RESULT` shift macro.

The chunk starts mid-register: the comment and most field definitions for `CRTCV1_CRTCV_EXT_TIMING_SYNC_LOSS_INTERRUPT_CONTROL` begin before line 34821. It also ends mid-register: `DIG0_DIG_OUTPUT_CRC_RESULT__DIG_OUTPUT_CRC_RESULT__SHIFT` appears at line 37188, while its matching mask and later DIG0 registers are in the next chunk. The final file-level report should reconcile these boundary splits.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime APIs in this range. The public interface is the macro naming contract used throughout AMDGPU display code:

- `<REGISTER>__<FIELD>__SHIFT` gives the right shift used to encode or decode a register field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask.
- Register address macros live in the companion `dce_12_0_offset.h` header as `mm<REGISTER>` and `mm<REGISTER>_BASE_IDX`.

Important macro families in this chunk include:

- `CRTCV1_CRTCV_EXT_TIMING_SYNC_*`: interrupt enable/status/clear/type fields for external timing sync loss, sync, and sync-signal events.
- `CRTCV1_CRTCV_STATIC_SCREEN_CONTROL`: static screen event mask, frame count, status, CPU interrupt enable/status/clear/type fields.
- `CRTCV1_CRTCV_3D_STRUCTURE_CONTROL`: stereo/3D enable, double-buffer enable, vertical update mode, stereo override, frame-count reset/status, and frame count.
- `CRTCV1_CRTCV_GSL_*`: genlock/swaplock vsync gap limits, source selection, mode, clear/status, window start/end, check line, forced delay, and all-fields check.
- `HPD0..HPD5_DC_HPD_*`: hot-plug interrupt status, HPD sense and delayed sense, HPD RX interrupt status, interrupt acknowledge/polarity/enable, RX interrupt acknowledge/enable, connection/RX timers, HPD enable, fast-train delays/enables, and connect/disconnect debounce filter delays.
- `DC_PERFMON2_*`: event selection, counted value selection/type, increment/run/stop modes, interrupt enables/status/clear, counter state machine fields, 64-bit counter high/low values, and current-value interrupt comparison controls.
- `DP_AUX0..DP_AUX5_AUX_*`: AUX enable/reset/reset-done, HPD selection, mode detection, software transaction start/write-byte/index/data fields, arbitration request/done state, software done/timeout/error statuses, line-status protocol errors, DPHY timing controls, DPHY TX/RX status, and GTC sync error/status fields.
- `DIG0_DIG_FE_CNTL`: source select, stereo sync select/gate, digital start, symbol-clock state, TMDS pixel encoding, and TMDS color format.
- `DIG0_DIG_OUTPUT_CRC_CNTL`: output CRC enable, link select, and data select.

## Control Flow

This header chunk has no internal control flow. The preprocessor exposes constants that compile into display driver register tables and read/modify/write operations.

Runtime control flow appears in consumers:

1. DCE 12 code includes `dce_12_0_offset.h` and `dce_12_0_sh_mask.h`.
2. Macro tables combine `mm*` addresses, `*_BASE_IDX` values, and this chunk's `_MASK`/`__SHIFT` constants.
3. Register helper code reads a 32-bit register, clears fields with `_MASK`, shifts values by `__SHIFT`, writes the result, and sometimes polls status bits.

Concrete integration examples in the tree:

- `display/dc/irq/dce120/irq_service_dce120.c` builds HPD and HPD RX interrupt source entries from `HPD0..5_DC_HPD_INT_CONTROL` enable/ack masks and `HPD0..5_DC_HPD_INT_STATUS` status registers.
- `display/dc/dce/dce_aux.h` defines `DCE12_AUX_MASK_SH_LIST`, which maps `DP_AUX0_AUX_CONTROL`, `DP_AUX0_AUX_ARB_CONTROL`, `DP_AUX0_AUX_SW_CONTROL`, `DP_AUX0_AUX_SW_DATA`, `DP_AUX0_AUX_SW_STATUS`, and `DP_AUX0_AUX_INTERRUPT_CONTROL` fields into the AUX engine's register-field tables.
- `display/dc/dce120/dce120_timing_generator.c` programs static-screen control through register helper macros, clamping the frame count to 8 bits before writing the static-screen frame-count field.
- `display/dc/dce/dce_stream_encoder.h` includes `DIG0_DIG_FE_CNTL` fields in stream encoder field maps used to start the DIG front end, select the source, and configure TMDS/stereo behavior.
- `display/dc/resource/dce120/dce120_resource.c` includes this header while constructing DCE 12 resource objects for timing generators, stream encoders, link encoders, AUX, I2C, IRQ, clocks, and related display blocks.

## State And Persistence Behavior

The header itself is stateless. It does not allocate memory, perform I/O, or persist data. Its only persistence is as compiled constants in driver objects.

The hardware fields represented here are persistent GPU register state until changed by driver writes, firmware, a display block reset, ASIC reset, hot-plug activity, suspend/resume, or link retraining. Important state categories include:

- HPD line state, delayed sense state, HPD/RX interrupt latches, interrupt polarity, and debounce timers;
- AUX controller enable/reset state, software transaction buffers, arbitration ownership, timeout/error bits, reply byte counts, line-status capture, DPHY tuning, and GTC sync error latches;
- timing-generator static-screen detection state, external sync interrupt state, 3D frame count/reset state, and genlock/swaplock window/gap state;
- DC perfmon counter configuration, active state, interrupt state, comparison values, and high/low counter values;
- DIG front-end start/source/TMDS/stereo configuration and output CRC enable/result state.

Many status and interrupt bits use write-one-to-clear or acknowledge-style fields in nearby control registers. These macros do not encode access type, ordering, locking, or ownership; consumers must follow the register specification and existing register helper conventions.

## Dependencies And Integration Points

The immediate dependency is the C preprocessor. The practical dependency is the companion DCE 12.0 offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h`

The offset header defines matching register addresses, including `mmCRTCV1_CRTCV_GSL_CONTROL`, `mmHPD0_DC_HPD_INT_STATUS` through `mmHPD5_DC_HPD_TOGGLE_FILT_CNTL`, `mmDC_PERFMON2_*`, `mmDP_AUX0_AUX_CONTROL` through `mmDP_AUX5_AUX_GTC_SYNC_STATUS`, and `mmDIG0_DIG_FE_CNTL` through `mmDIG0_DIG_OUTPUT_CRC_RESULT`.

Known local DCE 12 consumers include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_translate_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_factory_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c`

The chunk also shares field names and patterns with generic DCE/DC helper headers such as `display/dc/dce/dce_aux.h` and `display/dc/dce/dce_stream_encoder.h`, where `AUX_SF` and `SE_SF` macros construct per-generation mask/shift tables.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These constants are untyped preprocessor values, so the compiler cannot verify that a mask is paired with the intended register address, that a field value fits before shifting, or that a status/ack/control field is used with the correct access semantics.

Boundary split risks matter for this chunk. The first register family is incomplete at the start, and `DIG0_DIG_OUTPUT_CRC_RESULT` is incomplete at the end. Chunk-local checks for complete mask/shift pairs must allow these boundaries; file-level reconciliation should verify that the pairs exist across adjacent chunks.

Repeated instance blocks are easy to mix up. `HPD0..5` and `DP_AUX0..5` have nearly identical field layouts with different register addresses. Copying the wrong instance prefix can compile cleanly while acknowledging the wrong HPD interrupt, selecting the wrong AUX engine, or reading stale status from another physical connector path.

Several field groups are timing-sensitive or protocol-sensitive:

- HPD polarity, enable, acknowledge, debounce, and fast-train fields affect connector detection and IRQ storms/loss.
- AUX software transaction, arbitration, timeout, and data-index fields affect DPCD/EDID reads, DP link training, and MST/sideband reliability.
- AUX DPHY fields affect electrical receive/transmit windows and can cause intermittent AUX failures if copied across ASIC generations without validation.
- CRTC external sync and GSL fields affect genlock/swaplock timing and can cause multi-display synchronization faults.
- DIG front-end source/start/TMDS fields affect visible display output, HDMI/DVI encoding, and CRC/debug capture.

High-bit masks such as `0x80000000L` depend on unsigned 32-bit treatment in consumers. Callers should use the existing register helper macros and fixed-width `uint32_t` values instead of ad hoc signed arithmetic.

Generated headers can drift from register specs or offset headers. A stale mask with a correct address, or a correct mask with a stale shift, usually still builds and may only fail on hardware.

## Test Signals

Useful validation signals include:

- compile coverage for DCE 12 translation units that include `dce_12_0_sh_mask.h`, especially `irq_service_dce120.c`, `dce120_timing_generator.c`, `dce120_hwseq.c`, `dce120_resource.c`, GPIO factory/translation files, and `gmc_v9_0.c`;
- generated-header consistency checks across the complete file, ensuring each `_MASK` has a matching `__SHIFT` and each field macro has a matching `mm*` address in `dce_12_0_offset.h`;
- duplicate-definition checks to ensure repeated HPD/AUX instance macros are identical where intended and uniquely prefixed by instance;
- hot-plug tests across all supported connectors, checking HPD connect, disconnect, delayed sense, RX IRQ, debounce behavior, interrupt ack/reenable, suspend/resume, and rapid cable-toggle cases;
- DisplayPort AUX transaction tests, including EDID/DPCD reads, link training, AUX timeout/error handling, HPD disconnect during AUX, MST sideband traffic, and CP IRQ handling;
- timing-generator tests for static-screen detection, vblank/vactive waits, external sync loss/sync/signal interrupts, 3D stereo modes, and genlock/swaplock operation where hardware supports it;
- DC perfmon tests that program event selection, start/stop counters, read low/high values, and verify interrupt/compare behavior without corrupting adjacent counter controls;
- stream encoder tests for DIG source selection, DIG start/stop, TMDS pixel encoding/color format, stereo sync gating, and output CRC enable/result readback;
- hardware readback tests after representative safe writes, using the register helper APIs to confirm that shifted values occupy only the intended masked bits.

### subset-b-001552: lines 37189-39651

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 37189-39651

## Scope

This chunk covers lines 37189-39651 of the generated-style AMD DCE 12.0 register shift/mask header. It contains C preprocessor constants only: no functions, structs, enums, or executable code. The range starts in the tail of `DIG0_DIG_OUTPUT_CRC_RESULT`, covers the rest of the `DIG0` digital encoder block, the full `DP0` DisplayPort field block, the full `DIG1` and `DP1` repeated blocks, and then begins `DIG2` through `DIG2_AFMT_ISRC1_3`.

The chunk defines 2156 `#define` entries under 299 register-comment lines. These macros are the field-level API used by AMD display code to combine DCE 12.0 register addresses with bit masks and shifts.

## Purpose

The purpose of this range is to describe bit positions for digital display link programming:

- `DIG0`, `DIG1`, and the beginning of `DIG2` HDMI/DVI/TMDS encoder controls.
- HDMI packet generation, infoframes, general-control packets, ACR audio clock regeneration, audio-packet scheduling, AVMUTE state, and deep-color/scrambling fields.
- AFMT audio formatter fields for HDMI/DP audio metadata, audio channel enables, IEC 60958 channel status, ISRC payload bytes, generic packet payloads, AVI/MPEG/audio infoframe bytes, audio CRC, audio test ramp, status, and source selection.
- TMDS control fields for clocking, control characters, DC balance, sync character patterns, lane/control-bit generation, stereo sync, and link version/lane enable.
- `DP0` and `DP1` DisplayPort link, stream, secondary packet, DPHY training, CRC, fast training, MSA override, and MST/MSE slot-allocation fields.

Each logical field is represented by a `REGISTER__FIELD__SHIFT` macro and a matching `REGISTER__FIELD_MASK` macro. Consumers use these constants with companion register address macros from DCE 12.0 address headers and register helper macros such as read/modify/write field setters.

## Important Macro Families

The `DIG*_DIG_*` families define the front-end/back-end controls for each digital encoder instance. Key registers include `DIG_FE_CNTL`, `DIG_BE_CNTL`, `DIG_BE_EN_CNTL`, `DIG_OUTPUT_CRC_CNTL`, `DIG_OUTPUT_CRC_RESULT`, `DIG_CLOCK_PATTERN`, `DIG_TEST_PATTERN`, `DIG_RANDOM_PATTERN_SEED`, `DIG_FIFO_STATUS`, `DIG_VERSION`, `DIG_LANE_ENABLE`, and `AFMT_CNTL`. These cover pipe source selection, encoder start, symbol-clock state, TMDS pixel encoding and color format, output CRC selection/results, diagnostic test patterns, FIFO error/level calibration, back-end enable, lane enables, and audio-formatter enable.

The `DIG*_HDMI_*` families describe HDMI control and packet state. `HDMI_CONTROL` exposes keepout mode, data scrambling, clock-channel rate, null packet behavior, packet generator version, error ack/mask, deep-color enable, and deep-color depth. `HDMI_STATUS` exposes active AVMUTE and audio/VBI packet error interrupt state. Packet-control registers drive audio packet timing, ACR send/continuous/source/auto-send fields, null/general-control/ISRC/ACP VBI packet scheduling, AVI/audio/MPEG infoframe send/continuous bits, generic packet send/line selection, and general-control AVMUTE/packing phase fields.

The `DIG*_AFMT_*` families define audio formatter payload and status fields. Important groups include:

- `AFMT_AUDIO_PACKET_CONTROL2`, `AFMT_AUDIO_PACKET_CONTROL`, `AFMT_VBI_PACKET_CONTROL`, and `AFMT_INFOFRAME_CONTROL0` for layout overrides, channel enables, DP stream ID, HBR/60958 overrides, audio sample send, and packet enable/continuous behavior.
- `AFMT_ISRC1_*` and `AFMT_ISRC2_*` for 8-bit packed UPC/EAN/ISRC payload bytes plus status/continue/valid flags.
- `AFMT_AVI_INFO*`, `AFMT_MPEG_INFO*`, `AFMT_AUDIO_INFO*`, `AFMT_GENERIC_HDR`, and `AFMT_GENERIC_0` through `AFMT_GENERIC_7` for HDMI/DP metadata payload bytes and checksums.
- `AFMT_60958_*` for IEC 60958 professional/audio mode, copyright, category, source/channel numbers, sampling frequency, word length, and original sampling-frequency fields.
- `AFMT_AUDIO_CRC_CONTROL` and `AFMT_AUDIO_CRC_RESULT` for audio CRC enable/continuous/source/channel selection and CRC/sample-count results.
- `AFMT_RAMP_CONTROL0` through `AFMT_RAMP_CONTROL3` for audio test-ramp maximum/count/minimum/delta patterns.
- `AFMT_STATUS` and `AFMT_AUDIO_SRC_CONTROL` for FIFO overflow, outstanding audio sample send, and source selection/status.

The `DIG*_TMDS_*` families describe HDMI/DVI physical encoding controls. They cover TMDS enable/dual-link pixel rate/clock pattern, control characters, feedback, stereo sync selection, sync character patterns, data-control bits, DC-balancer enable/test state, and per-control-symbol generation.

The `DP0_DP_*` and `DP1_DP_*` families cover DisplayPort stream and PHY programming. Core link fields include link enable, enhanced framing, stream enable, pixel encoding/depth, component mode, MSA colorimetry/misc bits, timing source, stream ID, and DP-to-DIG FIFO steering. Video timing and transfer-rate fields include `DP_VID_TIMING`, `DP_VID_N`, `DP_VID_M`, `DP_MSA_V_TIMING_OVERRIDE*`, and `DP_VID_MSA_VBID`. Link-training and PHY fields include DPHY control, training pattern selection, symbol patterns, 8b/10b control, PRBS/scrambler control, CRC enable/control/result, MST CRC control/status, fast-training controls/status, byte-swap/sr-swap, and HBR2 pattern control. Secondary and MST/MSE families include `DP_SEC_*`, audio N/M and readbacks, timestamp, packet control, MSE rate/update, SAT payload/status fields, link timing, and miscellaneous MSE controls.

## APIs, Types, and Functions

There are no callable APIs or C types in this chunk. The API surface is the macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the field bit offset.
- `REGISTER__FIELD_MASK` gives the field mask already shifted into register position.
- Instance prefixes such as `DIG0`, `DP0`, `DIG1`, `DP1`, and `DIG2` select the replicated hardware block.

The macro names must match generated DCE 12.0 address headers and AMDGPU register helper conventions. Fields whose names end in `MASK` intentionally produce names such as `HDMI_CONTROL__HDMI_ERROR_MASK_MASK`; this is awkward but part of the generated ABI used by callers.

## Control Flow

This header has no local runtime control flow. The implied programming flow in display driver users is:

1. Select a DIG/DP/AFMT instance by address macro and instance offset.
2. Read a MMIO register or prepare a literal register value.
3. Clear the relevant `*_MASK` bits and insert a new value shifted by the matching `*__SHIFT`.
4. Write the register back through AMDGPU/DM register access helpers.
5. Poll status fields, read CRC/readback fields, or write ack bits for error/status conditions.

Several field families imply strict external sequencing. DP link training configures link rate, lane/symbol patterns, DPHY training pattern selection, scrambler/8b10b state, and fast-training status before enabling a stream. HDMI audio setup programs ACR N/CTS values, audio infoframes, 60958 fields, and packet send/continuous bits before active audio transmission. AFMT/HDMI status and FIFO error fields require ack and readback handling in interrupt or validation paths.

## State and Persistence

The macros do not store software state. They describe persistent hardware register state held by the display controller until MMIO writes, reset, power transitions, or hardware side effects change it. State domains visible in this range include:

- Per-link encoder source, start, back-end enable, lane-enable, symbol-clock, TMDS encoding, and FIFO calibration/error state.
- HDMI packet generator configuration, packet line scheduling, ACR values/status, AVMUTE, deep color, scrambling, and packet error interrupt state.
- AFMT payload contents for AVI, MPEG, audio, ISRC, and generic packets, plus audio layout/channel-enable/source-selection state.
- IEC 60958 channel-status metadata and HBR/60958 override state.
- Audio CRC, ramp-test, FIFO overflow, and outstanding sample-send diagnostic state.
- DisplayPort stream enable, link framing, pixel format, MSA/VBID/timing values, link-training patterns, DPHY scrambler/PRBS/CRC state, fast-training state, secondary-packet audio/timestamp state, and MST/MSE bandwidth-slot allocation.

Status fields such as `DIG_FIFO_LEVEL_ERROR`, `HDMI_ERROR_INT`, `AFMT_AUDIO_FIFO_OVERFLOW`, DP CRC status, fast-training status, MSE SAT status, and ACR CTS/N readbacks are hardware-observed state. Ack fields such as `DIG_FIFO_ERROR_ACK` and `HDMI_ERROR_ACK` require caller-side knowledge of write-one-to-clear semantics from the hardware specification.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor, but it is useful only with the surrounding AMDGPU register infrastructure:

- Companion DCE 12.0 address headers, especially `dce_12_0_d.h`/offset headers, provide the MMIO register addresses corresponding to these fields.
- DCE 12.0 enum headers provide symbolic values for many fields, such as HDMI/DP pixel encodings, audio CRC source/channel selections, and packet modes.
- AMDGPU and display-core register helpers combine address macros, instance offsets, masks, and shifts for low-level register programming.
- HDMI/DVI setup paths consume the DIG/HDMI/TMDS field groups for modesets, deep-color selection, scrambling, AVMUTE, and infoframe/packet setup.
- DisplayPort link-training and MST paths consume the `DP0`/`DP1` field groups for PHY training, MSA timing, secondary packet/audio metadata, CRC diagnostics, and MSE slot allocation.
- Audio-over-HDMI/DP paths consume AFMT, 60958, ACR, audio infoframe, ramp, and CRC fields.

Direct textual users in this source tree include older DCE code that writes AFMT CRC/ramp registers and SI-era HDMI-control programming. The DCE 12.0-specific consumers normally use the same generated field naming pattern through ASIC-specific include stacks rather than hard-coded bit numbers.

## Risks

The primary risk is silent hardware misprogramming. Incorrect masks or shifts compile cleanly but can target the wrong field, overwrite reserved bits, leave status uncleared, or produce link-training, audio, or packet-generation failures that only appear on specific displays.

The repeated instance structure increases copy/generation risk. `DIG0`, `DIG1`, and `DIG2` fields are intentionally near-identical, as are `DP0` and `DP1`; a single mismatched field width or prefix can route programming to the wrong block or make one connector behave differently from another.

Boundary risk matters for this chunk. It begins after the `DIG0_DIG_OUTPUT_CRC_RESULT__SHIFT` line and ends mid-register at `DIG2_AFMT_ISRC1_3__AFMT_UPC_EAN_ISRC10__SHIFT`; final per-file research must merge adjacent chunks before drawing complete conclusions about `DIG0_DIG_OUTPUT_CRC_RESULT` and the rest of `DIG2_AFMT_ISRC1_3`.

Several fields interact with hardware state machines. DP training, fast training, scrambler/PRBS, MST/MSE SAT updates, HDMI ACR send/continuous state, AVMUTE, audio packet generation, AFMT CRC, and FIFO-error ack fields are order-sensitive. Wrong sequencing can cause black screens, audio loss, CRC mismatches, or interrupt storms rather than an immediate software assertion.

The `L` suffix on masks and large masks such as `0x80000000L`, `0xFFFFFFFFL`, and `0x3FFFFFFFL` rely on callers using unsigned or sufficiently wide intermediates. Sign extension or truncation in ad hoc code can corrupt field assembly.

## Test Signals

Useful validation signals for this chunk are mostly hardware and integration tests:

- Build coverage for every DCE 12.0 translation unit that includes this header and uses generated register helpers.
- Static generation checks that each `REGISTER__FIELD__SHIFT` has the expected matching `REGISTER__FIELD_MASK`, masks align to shifts, and repeated `DIG0`/`DIG1`/`DIG2` and `DP0`/`DP1` blocks remain consistent where the hardware layout is meant to match.
- HDMI/DVI modeset tests covering deep color, scrambling, TMDS pixel encoding, AVMUTE, null/general-control packets, AVI/audio/MPEG infoframes, and generic packet transmission.
- HDMI/DP audio tests covering ACR N/CTS programming, 60958 channel status, audio infoframes, channel enables, source selection, HBR override, ramp generation, audio CRC, FIFO overflow, and sample-send status.
- DisplayPort link-training tests across lane counts/rates, DPHY training patterns, scrambler/PRBS behavior, fast training, MSA timing overrides, CRC readback, secondary-packet audio, and MST/MSE slot allocation/readback.
- Interrupt/status tests that exercise `DIG_FIFO_STATUS`, `HDMI_STATUS`, `AFMT_STATUS`, DP video interrupt controls, DPHY CRC status, fast-training status, and MSE SAT status.
- Diff checks against AMD's authoritative generated DCE 12.0 register database to catch off-by-one field positions or copied masks across repeated instances.

## Cross-Chunk Notes

This is a middle chunk of `dce_12_0_sh_mask.h`. It should be reconciled with prior chunks for the beginning of the DIG0 and DP0 sections and with following chunks for the remainder of the DIG2/DP2 and later digital-display register instances. The final per-file document should avoid treating this chunk's partial start and partial end as complete register-family coverage.

### subset-b-001553: lines 39652-42116

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 39652-42116

## Scope

This chunk covers lines 39652-42116 of the generated AMD DCE 12.0 register shift/mask header. The range starts in the middle of the `DIG2` audio formatter ISRC register sequence and ends in the middle of the `DIG4_HDMI_GENERIC_PACKET_CONTROL1` definition. It contains only C preprocessor constants for bit shifts and masks; there are no functions, structs, enums, runtime branches, or storage declarations.

The covered register families are:

- The tail of `dce_dc_dig2_dispdec`: `DIG2` AFMT, HDMI ACR/audio/infoframe, TMDS backend, lane enable, and AFMT control fields.
- The complete `dce_dc_dp2_dispdec` address block: `DP2` link, pixel format, video timing, DPHY, secondary-data/audio packet, and MST/MSE fields.
- The complete `dce_dc_dig3_dispdec` address block: `DIG3` frontend/backend, HDMI, AFMT, TMDS, CRC, FIFO, and lane fields.
- The complete `dce_dc_dp3_dispdec` address block: `DP3` equivalents of the `DP2` DisplayPort link and secondary-data fields.
- The beginning of `dce_dc_dig4_dispdec`: `DIG4` frontend, HDMI, AFMT, and generic info-packet fields through `HDMI_GENERIC_PACKET_CONTROL1`.

Because this is a large generated header, the line boundaries split repeated hardware instances. The merge lane should reconcile this document with adjacent chunks before drawing whole-file conclusions.

## Purpose

The header gives AMDGPU display code the field-level metadata needed to program DCE 12.0 display encoder, HDMI, TMDS, DisplayPort, audio formatter, and secondary-packet registers. Each hardware field is represented by a pair of macros:

- `REGISTER__FIELD__SHIFT`: bit offset of the field within the 32-bit MMIO register.
- `REGISTER__FIELD_MASK`: already-positioned bit mask for clearing, extracting, or validating the field.

This chunk is mostly about the digital output path for display encoders 2, 3, and 4, plus DisplayPort links 2 and 3. It covers fields used when a driver:

- Starts or stops a digital encoder stream and selects the source pipe.
- Programs HDMI packet generation, AVI/audio/MPEG/generic infoframes, ISRC payload bytes, ACR values, audio-channel status, ramp/test behavior, and audio CRCs.
- Configures TMDS control symbols, DC balancer behavior, sync patterns, feedback bits, and lane enable state.
- Configures DisplayPort link status, pixel format, M/N timing, video stream enablement, DPHY training/test/scrambling/CRC behavior, secondary-data packets, audio timestamps, and MST slot-allocation tables.

## Important Macro Families

The `DIG2` portion begins with `DIG2_AFMT_ISRC1_3` and continues through `DIG2_AFMT_CNTL`. It includes ISRC byte payload fields (`AFMT_UPC_EAN_ISRC8` through `AFMT_UPC_EAN_ISRC31` in this range), AVI infoframe payload and checksum fields, MPEG info fields, generic info-packet header and bytes 0-31, HDMI generic packet control for generic packets 2 and 3, HDMI ACR values for 32/44.1/48 kHz families, audio infoframe payload fields, IEC 60958 channel-status fields, AFMT CRC control/result fields, ramp/test-generator controls, audio packet/VBI/infoframe controls, audio source select, backend controls, TMDS controls, version/lane-enable fields, and AFMT enable/status control.

The `DP2` block spans `DP2_DP_LINK_CNTL` through `DP2_DP_MSE_SAT2_STATUS`. It covers link-training completion/status and eDP mode, pixel encoding/dynamic range/YCbCr range/component depth, MSA colorimetry override, lane count, stream enable/status/deferred disable, steering FIFO overflow/ack/mask state, MSA misc/timing fields, video `N` and `M`, enhanced framing/VBID behavior, HBR2 eye pattern, video interrupts, DPHY analog/test bypasses, training pattern selection, custom 8b/10b symbols, 8b/10b reset/disparity controls, PRBS generation, scrambler controls, DPHY CRC enable/control/results, MST CRC slots/status, fast-training state/ack, vertical-timing overrides, secondary-packet framing, audio `N`/`M` programming and readback, secondary timestamps, audio sample-packet coding/version/channel override, MSE rate programming, MST slot allocation tables and status readbacks, MSE update, link timing, blank/timestamp/zero-encoder controls, bit-stream/symbol-reset swap status, and HBR2 pattern controls.

The `DIG3` block is a full digital encoder instance and mirrors the same design as adjacent DIG blocks. It starts with frontend source selection and stream start (`DIG3_DIG_FE_CNTL`), output CRC control/result, clock/test/random-pattern controls, FIFO status and recalibration fields, then HDMI control/status/audio/ACR/VBI/infoframe/generic-packet/global-control fields. Its AFMT section includes audio layout/channel enable/DP stream ID/HBR override, complete ISRC1/ISRC2 byte payloads, AVI/MPEG/generic info-packet payloads, ACR registers, audio infoframe and IEC 60958 fields, audio CRC, ramp generator, packet controls, source selection, backend enable, TMDS controls, version, lane enable, and AFMT status.

The `DP3` block is structurally parallel to `DP2`, with `DP3_` prefixes over the same DisplayPort link, DPHY, secondary-data, audio, and MST/MSE field set. This repetition is important: callers select the physical/logical link by choosing the macro prefix, not by passing an instance index to this header.

The `DIG4` portion starts another full digital encoder instance. This chunk covers frontend/CRC/test/FIFO fields, HDMI controls, AFMT audio-packet layout controls, complete ISRC byte payload groups, AVI/MPEG/generic packet payload fields, and ends at `DIG4_HDMI_GENERIC_PACKET_CONTROL1` fields for generic packets 2 and 3. Later `DIG4` fields continue in the next chunk.

## APIs, Types, and Functions

There are no callable APIs, concrete C types, or function definitions here. The macro naming convention is the exported interface. Consumers combine these constants with companion register-address headers and AMDGPU register helpers to perform field writes and reads.

Typical use is equivalent to:

1. Read a register value using the matching register offset macro from a companion DCE header.
2. Clear one or more fields with `REGISTER__FIELD_MASK`.
3. Shift the desired value by `REGISTER__FIELD__SHIFT`.
4. Write the merged value back to the hardware register.

The macros with names ending in `_MASK_MASK`, such as `HDMI_ERROR_MASK_MASK`, `DP_STEER_OVERFLOW_MASK_MASK`, `DP_VID_STREAM_DISABLE_MASK_MASK`, `DPHY_CRC_MASK_MASK`, and `DPHY_FAST_TRAINING_COMPLETE_MASK_MASK`, are intentional: the hardware field name is itself `*_MASK`, and the generated suffix adds the second `_MASK`.

## Control Flow

This chunk has no runtime control flow. The sequencing implied by the field names lives in the display driver and hardware:

- HDMI packet flow: program payload bytes and checksums, select send/continuous bits, optionally choose target line numbers, then enable packet generation. Status and error bits are read back through HDMI status/control fields.
- Audio clock regeneration flow: program ACR `N` and CTS values for 32, 44.1, and 48 kHz clock families, enable/send the ACR packet, and monitor ACR status/readback fields.
- AFMT audio flow: program channel count/allocation, 60958 channel-status fields, source selection, HBR/layout overrides, packet controls, and CRC/ramp test controls before enabling audio transport.
- Digital encoder flow: select source, pixel encoding/color format, start stream generation, enable lanes, and use FIFO status/error-ack fields to diagnose underflow or calibration issues.
- DisplayPort flow: configure lane count and pixel/MSA settings, set video `M/N`, train the DPHY, enable scrambler/8b10b/stream controls, configure secondary packets and MST slot allocation, then read status/update-pending/CRC fields.

Order matters for callers even though this header cannot enforce it. For example, ack bits such as `HDMI_ERROR_ACK`, `DIG_FIFO_ERROR_ACK`, `DP_STEER_OVERFLOW_ACK`, `DP_TU_OVERFLOW_ACK`, `DP_VID_STREAM_DISABLE_ACK`, `DP_SEC_COLLISION_ACK`, and fast-training completion ack fields are meaningful only when used with the hardware-defined interrupt/status sequence.

## State and Persistence

The header itself stores no state. Its constants describe persistent hardware register fields held in DCE 12.0 MMIO registers until changed by driver writes, display resets, power-management transitions, or hardware side effects.

The state domains visible in this chunk include:

- HDMI transmitter state: deep-color enable/depth, data scrambling, AVMUTE, packet generator version, packet scheduling lines, ACR packet configuration, audio/VBI packet errors, and generic/infoframe/ISRC send state.
- AFMT state: audio layout, enabled channels, DP audio stream ID, HBR/60958 overrides, channel-status words, audio infoframe payload, packet enable/continuous bits, CRC accumulation, ramp generator status, and audio source selection.
- TMDS/backend state: backend enable, encoder version, lane enable bits, control characters, sync characters, DC balancer, stereosync, feedback, and control-bit generator fields.
- DIG frontend diagnostics: source selection, stream start, symbol-clock status, output CRC result, test/random pattern configuration, FIFO error, calibration, min/max/average levels, and recalibration requests.
- DisplayPort link state: link-training complete/status, lane count, stream enable/status, MSA colorimetry and timing, video `M/N`, DPHY training/scrambling/PRBS/CRC state, fast-training status, secondary packet enables/framing, audio `M/N` and timestamps, MST slot allocations, MSE rate/update-pending status, and MSE allocation readback status.

Several fields are readback or status-only by convention (`*_STATUS`, `*_READBACK`, `*_RESULT`, `*_PENDING`, `*_OCCURRED`, `*_CALIBRATED`), while others are write-trigger, ack, mask, or enable fields. The generated header does not encode access permissions; driver code must use the ASIC register specification and existing access helpers.

## Dependencies and Integration Points

This header depends only on the C preprocessor and its include guard in the full file. It is normally included by AMDGPU/DRM display code together with register-offset headers for DCE 12.0. The constants are integrated with:

- Low-level MMIO read/modify/write helpers used by AMDGPU display code.
- Encoder setup paths for HDMI, DVI/TMDS, and DisplayPort outputs.
- Audio-over-HDMI/DP paths that program AFMT, ACR, audio infoframes, channel status, and secondary-data audio packets.
- DisplayPort link training, link validation, MST allocation, and diagnostic CRC paths.
- Modeset and timing paths that program pixel encoding, component depth, MSA, video timing, M/N generation, and stream enablement.
- Debug and validation paths that use output CRC, DPHY CRC, FIFO status, packet error, fast-training, and MSE status fields.

The repeated instance prefixes are integration-critical. `DIG2`, `DIG3`, and `DIG4` refer to distinct digital encoder blocks; `DP2` and `DP3` refer to distinct DisplayPort decode/link blocks. The masks are not generic templates at compile time: each caller chooses a concrete macro family matching the hardware block it is programming.

## Risks

The main risk is silent hardware misprogramming. A bad shift or mask compiles cleanly but may write reserved bits, corrupt adjacent fields, or target the wrong display encoder/link instance. That can appear as link-training failures, missing HDMI/DP audio, bad infoframes, display underflow, MST slot-allocation errors, or intermittent modeset failures.

The repeated block structure increases copy/generation risk. `DP2` and `DP3` should remain structurally aligned, and `DIG2`/`DIG3`/`DIG4` should differ only where the hardware generation intentionally differs. Since this chunk starts and ends mid-instance, reviewers must avoid assuming the visible `DIG2` or `DIG4` sections are complete.

Fields named as masks, acks, pending bits, continuous-send bits, and status bits have hardware-specific semantics. Misusing `*_ACK` or `*_MASK` fields can lose interrupts or leave error states stuck. Misprogramming stream enable/defer, ACR, audio `M/N`, secondary-packet framing, or MST slot allocation can produce subtle timing bugs rather than immediate software failures.

Several payload fields are byte-packed into 32-bit registers. The ISRC, AVI, MPEG, generic packet, audio infoframe, and CRC result fields use repeated 8-bit masks at shifts `0x0`, `0x8`, `0x10`, and `0x18`. Callers must keep endian/packing assumptions consistent with hardware packet layout rather than treating the register as an opaque host-order integer payload.

Full-width and wide fields such as `DP_SEC_*` framing widths, `DP_MSE_RATE_*`, `DP_VID_M/N`, audio `M/N`, packet line numbers, and packed slot tables need correctly sized unsigned intermediates. Signed or narrow temporary values can truncate or sign-extend before masking.

## Test Signals

Useful validation signals include:

- Build coverage for AMDGPU display translation units that include `dce_12_0_sh_mask.h` and reference `DIG2`, `DIG3`, `DIG4`, `DP2`, or `DP3` field macros.
- Static/generated-header checks that each `__SHIFT` macro has a matching `_MASK`, masks align to shifts, byte-packed fields keep the expected `0x000000FF/0x0000FF00/0x00FF0000/0xFF000000` pattern, and repeated `DP2`/`DP3` layouts remain structurally equivalent.
- Diff checks against the authoritative DCE 12.0 ASIC register database, especially around chunk boundaries where `DIG2` and `DIG4` are partial.
- HDMI/DVI smoke tests that exercise deep-color modes, scrambling, AVMUTE, AVI/audio/MPEG/generic infoframes, ISRC packets, and ACR programming.
- HDMI/DP audio tests for channel allocation, HBR override, 60958 status words, audio source selection, ACR/audio `M/N`, mute handling, and packet continuity.
- DisplayPort link-training tests over DP2/DP3 paths, including lane-count changes, stream enable/disable-defer behavior, MSA colorimetry, video `M/N`, scrambling, PRBS/training patterns, and fast-training ack/status handling.
- MST tests that validate MSE rate programming, slot allocation table updates, update-pending clearing, and SAT status readback.
- Diagnostic tests that read output CRC, DPHY CRC, FIFO status, packet errors, collision status, and overflow flags before and after modesets or hotplug events.

## Cross-Chunk Notes

This chunk is one segment of a 64798-line generated mask header. Adjacent chunks are needed to complete the `DIG2` instance before line 39652 and the `DIG4` instance after line 42116. The final per-file document should reconcile all digital encoder and DisplayPort instances, verify that repeated macro families stay aligned across `DIG0`-style and `DP0`-style blocks elsewhere in the file, and describe the whole-file include guard and generation pattern.

### subset-b-001554: lines 42117-44587

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 42117-44587

## Scope

This chunk covers lines 42117-44587 of the generated-style AMD DCE 12.0 register shift/mask header. It contains C preprocessor constants only: no functions, no structs, no local variables, and no executable control flow. The exported interface is the set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros used by low-level AMDGPU display code to compose and decode memory-mapped register values.

The range starts in the tail of the `DIG4_HDMI_GENERIC_PACKET_CONTROL1` definitions, completes the remainder of the DIG4 digital/audio-format/TMDS field definitions, covers the full `dce_dc_dp4_dispdec` DisplayPort block, covers the full `dce_dc_dig5_dispdec` and `dce_dc_dp5_dispdec` blocks, and then enters `dce_dc_dig6_dispdec` through the first `DIG6_TMDS_CONTROL0_FEEDBACK` shift macro. Because the range begins and ends in the middle of larger generated register families, the final file-level research should reconcile this with adjacent chunks.

## Purpose

The purpose of this slice is to describe bit layouts for DCE 12.0 display encoder instances 4, 5, and 6, plus DisplayPort stream/link instances 4 and 5. These constants let driver code program HDMI, DisplayPort, audio infoframes, secondary data packets, TMDS control symbols, CRC/test logic, lane enables, stream timing, and MST slot allocation without hard-coding numeric bit positions at each call site.

Major areas covered are:

- DIG4 continuation: HDMI ACR values and status, AFMT audio info and IEC 60958 channel status, audio CRC/test ramp controls, AFMT status and packet controls, backend enable/routing, TMDS control-symbol generation, lane enable, and AFMT clock control.
- DP4: link status/training, pixel format/MSA metadata, video-stream enable and timing M/N generation, link framing, DPHY training/scrambling/CRC/fast-training controls, secondary packet generation, audio M/N, MST rate and slot allocation table fields, link timing, and DPHY byte-swap/HBR2/status fields.
- DIG5: complete digital front-end and backend field set for HDMI/DVI-style output, including output CRC, test/random patterns, FIFO status, HDMI control/status/audio/ACR/VBI/infoframe/generic packet controls, AFMT ISRC/AVI/MPEG/generic/audio metadata registers, IEC 60958 audio channel status, audio CRC/ramp/status, TMDS generator fields, lane enable, and AFMT clock gating.
- DP5: the same DisplayPort field layout as DP4, instance-prefixed for the next physical/logical DP block.
- DIG6 beginning: digital front-end, output CRC/test/FIFO/HDMI/AFMT packet and metadata definitions through the first TMDS feedback field.

## Important Macro Families

The `DIG4_*`, `DIG5_*`, and `DIG6_*` families describe digital encoder blocks. `DIG*_DIG_FE_CNTL` selects the source stream, toggles stereo sync and clock-pattern output, enables SYMCLK FE, and routes display test patterns. `DIG*_DIG_BE_CNTL` handles backend enable-side state such as dual-link mode, swap, FE source selection, DIG mode, and HPD selection; `DIG*_DIG_BE_EN_CNTL` exposes backend enable and symbol-clock status. `DIG*_DIG_LANE_ENABLE` turns individual lanes and the DIG clock on or off.

The HDMI-specific groups include `DIG*_HDMI_CONTROL`, `DIG*_HDMI_STATUS`, `DIG*_HDMI_AUDIO_PACKET_CONTROL`, `DIG*_HDMI_ACR_PACKET_CONTROL`, `DIG*_HDMI_VBI_PACKET_CONTROL`, `DIG*_HDMI_INFOFRAME_CONTROL0/1`, `DIG*_HDMI_GENERIC_PACKET_CONTROL0/1`, `DIG*_HDMI_GC`, and fixed-rate ACR registers for 32, 44.1, and 48 kHz families. They expose deep color, pixel packing, HDMI enable, keepout, audio delay, ACR send/source/auto-send/N-multiple, null/general-control/ISRC/AVI/audio/MPEG/generic packet scheduling, line-number placement, AVMUTE, default/packing phase, and readback of current CTS/N.

The AFMT groups package HDMI/DP audio and metadata payloads. `DIG*_AFMT_AUDIO_INFO0/1` and `DIG*_AFMT_60958_0/1/2` define audio infoframe fields, IEC 60958 channel status bits, valid flags, sampling/word-length fields, and per-channel numbers. `DIG*_AFMT_AUDIO_PACKET_CONTROL` and `DIG*_AFMT_AUDIO_PACKET_CONTROL2` gate sample sending, reset FIFO on audio disable, enable test mode, acknowledge FIFO/audio-enable changes, swap channels, update channel-status words, select layout, enable channels, select DP stream ID, and override HBR/60958 behavior. `DIG*_AFMT_ISRC*`, `DIG*_AFMT_AVI_INFO*`, `DIG*_AFMT_MPEG_INFO*`, `DIG*_AFMT_GENERIC_HDR`, and `DIG*_AFMT_GENERIC_0` through `_7` map packet payload bytes and metadata fields into 32-bit registers.

The TMDS groups cover DVI/HDMI symbol-generation details. `DIG*_TMDS_CONTROL_CHAR`, `DIG*_TMDS_CTL_BITS`, `DIG*_TMDS_CTL0_1_GEN_CNTL`, and `DIG*_TMDS_CTL2_3_GEN_CNTL` define control-character output enables, data selection, delays, inversion, modulation, feedback path selection, feedback sync continuation, and pattern output enables. `DIG*_TMDS_SYNC_CHAR_PATTERN_0_1`, `_2_3`, `DIG*_TMDS_STEREOSYNC_CTL_SEL`, `DIG*_TMDS_CONTROL0_FEEDBACK`, and `DIG*_TMDS_DCBALANCER_CONTROL` cover sync character programming, stereo-sync selection, control feedback source, and DC-balancer test/enable/seed/status fields.

The `DP4_*` and `DP5_*` families are parallel instance definitions for DisplayPort links. They include:

- Link and stream control: `DP*_DP_LINK_CNTL`, `DP*_DP_CONFIG`, `DP*_DP_VID_STREAM_CNTL`, `DP*_DP_VID_INTERRUPT_CNTL`, and `DP*_DP_LINK_FRAMING_CNTL`.
- Pixel and MSA metadata: `DP*_DP_PIXEL_FORMAT`, `DP*_DP_MSA_COLORIMETRY`, `DP*_DP_MSA_MISC`, `DP*_DP_VID_MSA_VBID`, and vertical timing override registers.
- M/N timing: `DP*_DP_VID_TIMING`, `DP*_DP_VID_N`, `DP*_DP_VID_M`, `DP*_DP_SEC_AUD_N`, `DP*_DP_SEC_AUD_M`, and readback variants.
- DPHY diagnostics and training: `DP*_DP_DPHY_CNTL`, training pattern select, symbol registers, 8b/10b control, PRBS, scrambler, CRC enable/control/result, MST CRC control/status, fast-training control/status, byte-swap/load controls, and HBR2 pattern control.
- Secondary data and MST: `DP*_DP_SEC_CNTL`, `DP*_DP_SEC_CNTL1`, `DP*_DP_SEC_FRAMING1` through `_4`, `DP*_DP_SEC_TIMESTAMP`, `DP*_DP_SEC_PACKET_CNTL`, `DP*_DP_MSE_RATE_CNTL`, `DP*_DP_MSE_RATE_UPDATE`, `DP*_DP_MSE_SAT0` through `_SAT2`, SAT status registers, SAT update, link timing, and MSE miscellaneous control.

## APIs, Types, and Functions

There are no callable APIs, no C type definitions, and no functions in this chunk. The macros are the API surface. Each field normally appears as a pair:

- `REGISTER__FIELD__SHIFT`: bit offset for the field.
- `REGISTER__FIELD_MASK`: already shifted mask for the field.

Consumers combine these with companion register-address headers and AMDGPU register helpers. A typical caller clears `REGISTER__FIELD_MASK` in a 32-bit register value, inserts `(value << REGISTER__FIELD__SHIFT) & REGISTER__FIELD_MASK`, then writes the result through MMIO. Status paths reverse the operation by masking and shifting readback values.

The naming convention is part of the integration contract. Instance prefixes such as `DIG4`, `DIG5`, `DIG6`, `DP4`, and `DP5` select the hardware block. Field names ending in `MASK` create intentionally awkward symbols such as `DP5_DP_DPHY_CRC_CNTL__DPHY_CRC_MASK_MASK`; these are generated names for a field whose hardware name itself includes "mask".

## Control Flow

This header has no runtime control flow. The control sequences are implied by the hardware fields and are implemented in display driver code that includes this header. Important implied flows include:

1. HDMI enablement: configure source/routing and deep-color or pixel packing in `DIG*_HDMI_CONTROL`, program AVI/audio/MPEG/generic payload registers, set infoframe packet controls, program ACR CTS/N and ACR packet control, then enable backend and lanes.
2. DisplayPort stream bring-up: configure lane count, pixel format, MSA fields, video M/N, link framing, stream enable, and interrupt masks; poll link/status/training fields as required.
3. DP secondary data and audio: program audio M/N, packet coding/version/channel override, secondary packet framing widths and positions, enable ASP/AIP/ACM/GSP/AVI/MPG/ISRC packets, and monitor collision/audio-mute status.
4. MST setup: program MSE rate X/Y, slot allocation table entries, SAT update bits, and read SAT status/link timing fields to verify allocation state.
5. Diagnostics: enable output CRC or DPHY/audio CRC, set CRC selectors and masks, poll result-valid/done bits, read result registers, and acknowledge error or completion status fields.
6. Training and test patterns: select DPHY training pattern, PRBS seed/mode, scrambler behavior, fast-training timing/start bits, TMDS control-character pattern generation, or DIG test/random patterns for compliance and bring-up.

Order and polling requirements are not encoded here. Callers must still obey the DCE 12.0 register specification for write-one-to-ack bits, read-only status bits, double-buffered updates, and timing-sensitive stream disable/enable sequences.

## State and Persistence

The header itself stores no software state. It describes persistent hardware state held in MMIO registers until reset, power management, firmware activity, hotplug/retraining, or later driver writes change it.

Key state represented in this range includes:

- Encoder routing and enable state: FE source selection, backend source selection, DIG mode, HPD selection, lane enables, symbol-clock status, and audio clock enable/on state.
- HDMI state: HDMI enable, deep-color depth, pixel packing phase, keepout behavior, audio packet timing, ACR scheduling, AVMUTE, infoframe/generic packet send/continuous state, line placement, and CTS/N readback.
- AFMT/audio state: audio infoframe payloads, IEC 60958 channel-status words, layout/channel enables, DP audio stream ID, HBR/60958 overrides, audio FIFO overflow status/ack, audio-enable change status/ack, CRC control/results, and test ramp counters.
- DP link and stream state: link training complete/status, embedded panel mode, lane count, stream enable/status/deferred disable, TU/steer FIFO overflow flags and acks, MSA metadata, video timing M/N values, and VBID/MSA placement.
- DPHY state: training pattern, scrambler settings, 8b/10b reset/current disparity, PRBS parameters, CRC selection/result/MST phase status, fast-training capability/start/state/completion, byte swap/load controls, and HBR2 eye/pattern enable.
- Secondary-packet and MST state: packet enable bits, GSP send/pending/deadline status, frame/vblank/hblank/idle transmit widths, secondary collision/audio mute state, audio M/N readback, MSE rate update pending, slot allocation table fields, and SAT status readback.

Fields with names such as `*_ACK`, `*_STATUS`, `*_PENDING`, `*_RESULT_VALID`, `*_DONE`, `*_MASK`, and `*_UPDATE` are especially stateful from the caller's perspective. Misclassifying them as ordinary writable configuration bits can leave sticky status uncleared or mask interrupts unexpectedly.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor, but it is useful only with the rest of the AMDGPU register-definition stack. It is expected to be included with companion DCE 12.0 headers that define register offsets, base indexes, and higher-level register helper tables.

Primary integration points are:

- AMDGPU DC/DCE display link code that configures DP link training, DP stream timing, MSA values, secondary data packets, and MST slot allocation.
- HDMI/DVI encoder paths that configure HDMI control, infoframes, ACR packets, general-control packets, generic packets, TMDS control symbols, lane enables, and backend routing.
- Audio-over-HDMI/DP paths that program AFMT audio info, IEC 60958 channel status, channel/layout enables, DP audio stream IDs, sample sending, and FIFO/enable-change acknowledgements.
- Diagnostics and compliance paths using output CRC, AFMT audio CRC, DPHY CRC, PRBS, test patterns, random pattern seeds, HBR2 eye patterns, and fast-training status.
- Interrupt or polling paths that consume FIFO overflow, stream disable, collision, fast-training completion, MST phase error, SAT update/status, and CRC result-valid fields.

The repeated instance prefixes are an important integration signal: DP4 pairs naturally with the fourth DisplayPort link block, DP5 with the fifth, and DIG4/DIG5/DIG6 with their corresponding digital encoder blocks. Adjacent chunks likely define the preceding address macros and the remainder of DIG6; callers generally expect all instance families to be complete across the full header.

## Risks

The highest risk is silent hardware misprogramming. A single wrong shift or mask can compile cleanly while writing a neighboring field, reserved bits, or a status/ack bit. That can produce display blanking, failed link training, audio loss, FIFO underflow/overflow, broken MST allocation, or stuck polling loops rather than a clear software exception.

Repeated generated blocks create copy/generation risk. DP4 and DP5 should have matching layouts with only the instance prefix changed; DIG5 and DIG6 should similarly match until this chunk's partial DIG6 boundary. Any divergence should be checked against the authoritative ASIC register source before assuming it is intentional.

Some masks expose non-byte-aligned or full-width fields. Examples include 20-bit ACR CTS fields shifted by `0xc`, 24-bit M/N and CRC payloads, 26-bit MSE rate Y, 6-bit slot counts, 12-bit frame-start locations, and high-bit status fields. Callers using signed or narrow intermediates can truncate or sign-extend values if they do not use the existing 32-bit register helper patterns.

Status, ack, and mask naming is easy to misuse. Fields such as `DP*_DP_STEER_FIFO__DP_STEER_OVERFLOW_ACK_MASK`, `DP*_DP_VID_INTERRUPT_CNTL__DP_VID_STREAM_DISABLE_ACK_MASK`, `DP*_DP_DPHY_FAST_TRAINING_STATUS__DPHY_FAST_TRAINING_COMPLETE_ACK_MASK`, `DIG*_AFMT_AUDIO_PACKET_CONTROL__AFMT_AUDIO_FIFO_OVERFLOW_ACK_MASK`, and `DIG*_AFMT_AUDIO_PACKET_CONTROL__AFMT_AZ_AUDIO_ENABLE_CHG_ACK_MASK` likely have write-one-to-ack semantics determined by hardware. Treating them as ordinary persistent configuration bits can either fail to clear events or clear events too early.

The chunk boundaries are also risky for reviewers and tooling. Line 42117 begins after the `DIG4_HDMI_GENERIC_PACKET_CONTROL1` comment and initial fields, and line 44587 ends after only the `DIG6_TMDS_CONTROL0_FEEDBACK__TMDS_CONTROL0_FEEDBACK_SELECT__SHIFT` definition. A per-file merge must not interpret this chunk as complete coverage for those two boundary registers.

## Test Signals

Useful validation signals for this chunk are mostly build, static-generation, and hardware-integration oriented:

- Compile coverage for AMDGPU display translation units that include `dce_12_0_sh_mask.h` and instantiate DIG4/DIG5/DIG6 or DP4/DP5 register macros.
- Static checks that every complete field in the range has a matching shift/mask pair, masks align with shifts, and repeated DP4/DP5 or DIG5/DIG6 layouts differ only where the generated register database says they should.
- Diff or regeneration checks against the authoritative DCE 12.0 ASIC register description, especially for repeated HDMI/AFMT/TMDS and DP/MST blocks.
- HDMI smoke tests on encoders mapped to DIG4-DIG6: modeset, deep color, audio, AVI/audio infoframes, generic packet send/continuous modes, AVMUTE, and TMDS test-pattern behavior.
- DisplayPort link tests on DP4 and DP5: lane-count configuration, link training, stream enable/disable, pixel-format changes, M/N timing, MSA override/colorimetry, and stream-disable interrupt handling.
- DP audio and secondary-packet tests: ASP/AIP/ACM/GSP/AVI/MPG/ISRC enablement, audio M/N readback, packet framing, collision detection/ack, and audio mute status.
- MST validation on DP4/DP5: MSE rate programming, SAT slot allocation/update, SAT status readback, link timing, and MST CRC phase lock/error/ack behavior.
- Diagnostic tests: output CRC, DPHY CRC, AFMT audio CRC, PRBS, fast training, HBR2 pattern/eye pattern, FIFO overflow injection where possible, and register readback after each programmed field group.

## Cross-Chunk Notes

This is one slice of a 64798-line generated header. The final per-file research should merge this with adjacent chunks to capture the full DIG4 register beginning before line 42117 and the remaining DIG6 TMDS/backend/lane/AFMT definitions after line 44587. This chunk should remain source-tree-aligned under `Docs/researches/chunks/` and should not be treated as the final per-file report.

### subset-b-001555: lines 44588-47203

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 44588-47203

## Purpose

This chunk is part of AMDGPU's generated DCE 12.0 register field mask header. It contains no executable C logic; it publishes compile-time bit layout constants for display-controller registers used by the Vega/DCE 12 display stack.

The range is centered on the final digital/DP instance and the first two DCIO ComboPHY instances:

- Tail of `DIG6` TMDS and digital-output fields, including TMDS feedback, stereo sync, sync-character patterns, TMDS control bits, DC balancer control, control-bit generator settings, lane enable, and AFMT audio-clock control.
- `DP6` DisplayPort stream/link fields, including link status, pixel format, MSA colorimetry and misc fields, video timing `M/N`, DPHY training/test/CRC/scrambler controls, secondary-data packet controls, audio `M/N` values, multi-stream transport allocation tables, and MSE status.
- `DCIO_UNIPHY0` and `DCIO_UNIPHY1` reserved macro-control ranges, represented as many full-width `RESERVED<n>` registers.
- `DC_COMBOPHYCMREGS0` and `DC_COMBOPHYCMREGS1` common PHY fields for fuses, lane power management, transmit common controls, lane resets, Z-calibration, and reserved-for-future-use registers.
- `DC_COMBOPHYTXREGS0` and `DC_COMBOPHYTXREGS1` per-lane transmit controls for lanes 0-3, including lane enable/ready, margin/de-emphasis, link-speed and PCS clock settings, boost, gang mode, and per-lane RFU registers.
- `DC_COMBOPHYPLLREGS0` plus the first part of `DC_COMBOPHYPLLREGS1`, covering frequency-control words, fractional/spread-spectrum controls, bandwidth tuning, calibration, loop controls, voltage-regulator configuration, observation, and DFT data for instance 0, then the same sequence through part of `VREG_CFG` for instance 1.

Each field is represented by paired macros. `REGISTER__FIELD__SHIFT` gives the low bit position, and `REGISTER__FIELD_MASK` gives the already-positioned mask. Driver code combines these masks with matching register-address macros from `dce_12_0_offset.h` and the display register helper macros that consume `FD(reg__field)` style names.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or storage objects in this chunk. The macro namespace is the entire API surface.

The `DIG6_*` definitions describe the sixth digital stream encoder's TMDS/HDMI-oriented controls. Important groups include `DIG6_TMDS_CONTROL0_FEEDBACK`, `DIG6_TMDS_STEREOSYNC_CTL_SEL`, `DIG6_TMDS_SYNC_CHAR_PATTERN_0_1`, `DIG6_TMDS_SYNC_CHAR_PATTERN_2_3`, `DIG6_TMDS_CTL_BITS`, `DIG6_TMDS_DCBALANCER_CONTROL`, `DIG6_TMDS_CTL0_1_GEN_CNTL`, `DIG6_TMDS_CTL2_3_GEN_CNTL`, `DIG6_DIG_VERSION`, `DIG6_DIG_LANE_ENABLE`, and `DIG6_AFMT_CNTL`.

The `DP6_*` definitions describe a DisplayPort stream/link block for instance 6. Major register families are:

- Link and stream enable/status: `DP6_DP_LINK_CNTL`, `DP6_DP_CONFIG`, `DP6_DP_VID_STREAM_CNTL`, and `DP6_DP_STEER_FIFO`.
- Pixel and MSA programming: `DP6_DP_PIXEL_FORMAT`, `DP6_DP_MSA_COLORIMETRY`, `DP6_DP_MSA_MISC`, `DP6_DP_VID_TIMING`, `DP6_DP_VID_N`, `DP6_DP_VID_M`, `DP6_DP_LINK_FRAMING_CNTL`, and `DP6_DP_VID_MSA_VBID`.
- DPHY training and diagnostics: `DP6_DP_DPHY_CNTL`, `DP6_DP_DPHY_TRAINING_PATTERN_SEL`, `DP6_DP_DPHY_SYM0` through `SYM2`, `DP6_DP_DPHY_8B10B_CNTL`, `DP6_DP_DPHY_PRBS_CNTL`, `DP6_DP_DPHY_SCRAM_CNTL`, CRC enable/control/result/status registers, fast-training control/status, bit/serializer swap control, and HBR2 pattern control.
- Secondary-data, audio, and MST/MSE programming: `DP6_DP_SEC_CNTL`, `DP6_DP_SEC_CNTL1`, `DP6_DP_SEC_FRAMING1` through `FRAMING4`, audio `N` and `M` programming/readback, timestamp, packet control, `DP6_DP_MSE_RATE_CNTL`, SAT0/SAT1/SAT2 allocation fields, SAT update, link timing, misc control, and SAT status registers.

The `DCIO_UNIPHY0_*` and `DCIO_UNIPHY1_*` macro groups are intentionally repetitive: each `UNIPHY_MACRO_CNTL_RESERVED<n>` exposes a full-width `reserved<n>` field. These registers are part of the generated DCIO address space and may be used by firmware, diagnostics, or later hardware-specific code even when normal driver paths do not name individual fields.

The ComboPHY common register groups are mirrored for instances 0 and 1. `COMMON_FUSE1` through `COMMON_FUSE3` expose HDMI/LVDS/DP fuse and calibration fields such as impedance, pre-emphasis, margin, de-emphasis, spread-spectrum, FFE, and control-swing data. `COMMON_LANE_PWRMGMT`, `COMMON_TXCNTRL`, `COMMON_LANE_RESETS`, and `COMMON_ZCALCODE_CTRL` expose PHY power sequencing, transmit mode, transmitter enable, per-lane reset, and impedance-calibration controls.

The ComboPHY TX register groups are also mirrored across instances and lanes. For each lane, `CMD_BUS_TX_CONTROL_LANE<n>` exposes `tx_en`, `tx_pg_en`, and `tx_rdy`; `MARGIN_DEEMPH_LANE<n>` exposes margin, de-emphasis, and margin-enable fields; `CMD_BUS_GLOBAL_FOR_TX_LANE<n>` exposes two-symbol mode, link speed, gang mode, max link rate, PCS frequency/clocking, PLL always-on, read-clock division, TX boost, and RON-code offset. The `TX_DISP_RFU0_LANE<n>` through `TX_DISP_RFU12_LANE<n>` registers are full-width RFU fields.

The ComboPHY PLL register groups define low-level PLL programming. `FREQ_CTRL0` and `FREQ_CTRL1` carry fractional and integer frequency-control words. `FREQ_CTRL2` carries denominator and slew fraction. `FREQ_CTRL3` exposes reference-clock division, VCO pre-division, fractional-N enable, SSC enable, FCW select, frequency jump, TDC resolution, and DPLL config bits. `BW_CTRL_COARSE`, `BW_CTRL_FINE`, `CAL_CTRL`, `LOOP_CTRL`, and `VREG_CFG` expose bandwidth, calibration, loop, PRBS, phase, regulator, and analog tuning controls. Instance 0 continues through observe and DFT output fields inside this chunk; instance 1 is cut off inside `VREG_CFG`.

## Control Flow

This header range has no runtime control flow. It is preprocessor data. Runtime behavior appears only in consumers that pair these field constants with register addresses and register helper macros.

A typical display-driver flow is:

1. Select the DCE 12 register address from `dce_12_0_offset.h`, often through resource tables in the DCE 12 display code.
2. Use a generated mask/shift field such as `FD(DP6_DP_VID_STREAM_CNTL__DP_VID_STREAM_ENABLE)` or a direct mask/shift pair.
3. Read a register through display-service helpers such as `dm_read_reg_soc15()` or a higher-level `generic_reg_update_soc15()` wrapper.
4. Extract, clear, or insert the field using the generated shift/mask constants.
5. Write the updated value back when the target field is writable and the display engine/PHY sequencing permits it.

Control-sensitive hardware actions represented by this chunk include enabling DP video streams, deferring stream disable, resetting and monitoring DP steer/TU FIFOs, changing DP pixel encoding/depth/range, programming DP `M/N` timing, selecting training/test patterns, enabling/disabling scrambling or CRC capture, sending secondary/audio packets, updating MST allocation tables, enabling digital lanes and AFMT audio clocks, resetting PHY lanes, powering lanes, changing PHY link-speed/PCS/PLL settings, and overriding analog TX margin/de-emphasis. The macros themselves do not enforce sequencing or valid value ranges.

## State And Persistence Behavior

The file stores no software state and has no persistence mechanism. It describes state held in display hardware registers.

The state represented here spans several layers:

- Stream-encoder state: TMDS control symbol generation, digital lane enables, AFMT audio clock enable/status, DP video stream enable/status, pixel encoding, MSA metadata, and VBID fields.
- Link-training and diagnostic state: DPHY training pattern selection, PRBS controls, scrambler seed/reset, CRC enable/masks/results, fast-training status, FIFO overflow flags and ACK bits, and MSE SAT status.
- Secondary-data and audio state: DP secondary packet enable/update scheduling, framing bytes, audio `N/M` programming and readbacks, timestamp, packet-line selection, and MST stream-allocation controls.
- PHY state: UNIPHY reserved register payloads, ComboPHY fuses, lane power management, common TX mode, lane resets, per-lane ready/enabled state, margin/de-emphasis/boost, link-speed hints, PCS clocking, PLL frequency words, spread-spectrum/fractional-N selection, calibration, loop/PRBS settings, regulator controls, observe selections, and DFT output.

Persistence depends on each hardware register's semantics. Some fields are latched programming values, some are live status bits, some are sticky diagnostic/status bits that require explicit ACK or clear fields, some are fuse/strap-derived read-only values, and some are reserved or RFU payloads. Values can be changed by the display driver, firmware/BIOS, hardware self-clearing behavior, link training, mode set, hotplug handling, suspend/resume, power-gating, or ASIC reset. This generated header does not encode read-only, write-one-to-clear, self-clearing, or sequencing rules.

## Dependencies And Integration Points

This chunk depends on the generated DCE 12 register-header ecosystem. The companion address definitions are in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h`; this file supplies the field layout inside those addresses.

Direct include points for `dce_12_0_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_translate_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_factory_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c`

The display code includes both `dce_12_0_offset.h` and this mask header, then uses macros such as `FD(reg__field)`, `generic_reg_update_soc15()`, and `generic_reg_set_soc15()` to write packed register fields. `dce120_resource.c` also builds DCE 12 resource tables from generated `mm...` addresses and field metadata; these tables feed stream encoders, link encoders, timing generators, IRQ services, GPIO/AUX/I2C, and hardware sequencing code.

Although this repository path is under a local `ceph-client` source tree, the content of this chunk is AMDGPU display-driver hardware metadata. It has no Ceph filesystem protocol behavior, distributed filesystem state, or storage persistence.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A wrong mask or shift can compile successfully while updating the wrong bit, failing to update the intended field, or corrupting adjacent fields during read-modify-write register updates.

High-risk display fields in this chunk include `DP6_DP_VID_STREAM_ENABLE`, deferred stream disable/status bits, DP pixel encoding/depth/range fields, MSA override fields, DP video timing `M/N` generation controls, DPHY training/test/scrambler/CRC controls, secondary-data packet controls, MST allocation table fields, and AFMT audio clock bits. Bad constants in these areas can produce blank displays, wrong color format or dynamic range, missing audio/infoframes, MST allocation failures, broken compliance test patterns, or incorrect CRC diagnostics.

PHY fields are especially sensitive. Lane enable/ready, lane power-management, lane reset, link-speed, PCS clock, PLL frequency-control, fractional-N/SSC, calibration, regulator, margin, de-emphasis, boost, and RON-code fields affect analog signaling. Incorrect values can cause failed link training, intermittent display dropouts, eye-margin failures, compliance failures, excess power, or hangs during mode set and resume.

The repeated instance/lane layout creates copy-generation risk. `DC_COMBOPHYTXREGS0` and `DC_COMBOPHYTXREGS1` repeat the same lane 0-3 pattern, and each lane has many similarly named RFU registers. An instance suffix or lane suffix mismatch would be hard to detect at compile time and might only fail on one physical transmitter or one lane configuration.

Reserved and RFU fields require conservative handling. Many `DCIO_UNIPHY*_UNIPHY_MACRO_CNTL_RESERVED<n>` and `TX_DISP_RFU<n>_LANE<m>` fields are full-width masks. Normal driver code should avoid inventing semantics for these fields unless backed by ASIC documentation or known golden-register programming.

This chunk has artificial line-boundary splits. It starts after the first `DIG6_TMDS_CONTROL0_FEEDBACK__TMDS_CONTROL0_FEEDBACK_SELECT__SHIFT` line and ends before the remaining masks for `DC_COMBOPHYPLLREGS1_VREG_CFG`. The final per-file merge should treat those as chunk boundaries, not source omissions.

## Test Signals

Useful validation is mostly compile-time plus display and hardware behavior:

- Kernel/driver builds for DCE 12/Vega display paths should compile all generated field names referenced by DCE 12 timing, IRQ, GPIO, resource, and hardware-sequencing code.
- Generated-register validation should compare every `*_MASK`/`*__SHIFT` pair in this range against AMD's register database and the adjacent address definitions in `dce_12_0_offset.h`.
- Display mode-set tests should exercise DP6 and DIG6 paths across HDMI/TMDS and DisplayPort outputs where hardware exposes those instances.
- DP link training, fast-training, HBR2 pattern, PRBS, scrambling, and CRC diagnostics should show expected bit transitions and stable link status.
- MST tests should verify MSE SAT programming, rate updates, link timing, and SAT status for multi-stream displays.
- Audio/infoframe tests should confirm AFMT clock enable/status, secondary packet scheduling, audio `N/M` programming, and packet framing are correct.
- Suspend/resume, hotplug, HPD IRQ, runtime power-management, and full modeset stress tests should not leave PHY lanes powered incorrectly, stuck in reset, or trained with bad margin/de-emphasis/PLL settings.
- Lab PHY/compliance tests should validate lane margin, de-emphasis, boost, SSC/fractional-N, PLL lock, and DFT/observe paths for both ComboPHY instances and all four lanes.

Regression symptoms from bad constants include blank or flickering display, wrong colors or quantization, DP link stuck at a lower rate, MST stream loss, missing HDMI/DP audio, repeated hotplug or link-training failures, CRC/test-pattern mismatches, PHY compliance failures, resume failures, or diagnostics showing activity on the wrong lane or PHY instance.

## Cross-Chunk Notes

Earlier chunks of `dce_12_0_sh_mask.h` define the preceding DCE 12 display register field families and the start of the `DIG6` TMDS block. Later chunks complete `DC_COMBOPHYPLLREGS1_VREG_CFG` and continue through subsequent DCE 12 register-mask families. The final per-file report should describe this source as one generated display hardware layout contract rather than as independent algorithmic code.

### subset-b-001556: lines 47204-49875

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 47204-49875

## Scope

This chunk covers lines 47204-49875 of the generated AMD DCE 12.0 register shift/mask header. It begins in the tail of `DC_COMBOPHYPLLREGS1_VREG_CFG`, covers the remaining observation/DFT fields for COMBOPHY PLL instance 1, then defines complete UNIPHY reserved-register blocks for UNIPHY2, UNIPHY3, and UNIPHY4. Between those reserved blocks it covers COMBOPHY common, TX-lane, and PLL register masks for instances 2 and 3. It ends at the start of `dce_dc_dc_combophycmregs4_dispdec`, after the full `DC_COMBOPHYCMREGS4_COMMON_FUSE1` field definitions and just before `COMMON_FUSE2`.

The file content is generated-style C preprocessor metadata only. There are no functions, structs, enums, inline helpers, includes, or executable statements in this range. The exported surface is a large set of `#define` constants naming bit shifts and already-positioned masks for memory-mapped AMD display PHY registers.

## Purpose

The chunk provides field-level definitions for DCE 12.0 display PHY hardware programming. The visible register families describe:

- PLL instance 1 diagnostic tail fields: `DC_COMBOPHYPLLREGS1_VREG_CFG` masks for voltage-regulator/DPLL config bits, `OBSERVE0`, `OBSERVE1`, and `DFT_OUT`.
- UNIPHY macro reserved windows for instances 2, 3, and 4: `DCIO_UNIPHY{2,3,4}_UNIPHY_MACRO_CNTL_RESERVED0` through `...RESERVED159`, each modeled as a full 32-bit reserved payload.
- COMBOPHY common registers for instances 2 and 3: fuse calibration, margin/de-emphasis nominal defaults, lane power management, TX common controls, TMDS/DisplayPort mode fields, lane resets, Z-calibration control, and display reserved-for-future-use registers.
- COMBOPHY TX-lane registers for instances 2 and 3: per-lane command-bus TX control, per-lane margin/de-emphasis, per-lane global TX controls, and lane-local reserved slots across lanes 0-3.
- COMBOPHY PLL registers for instances 2 and 3: frequency-control words, bandwidth control, calibration, loop control, voltage-regulator configuration, observation selectors, lock timing, and DFT output.
- The start of COMBOPHY common instance 4 fuse metadata: `DC_COMBOPHYCMREGS4_COMMON_FUSE1`.

These constants let AMDGPU display code compose precise MMIO read/modify/write values without embedding raw bit offsets and masks at each call site.

## Important Macro Families

`DC_COMBOPHYPLLREGS1_*` in this range is partial. Lines 47204-47208 finish the `VREG_CFG` mask list with `sel_bump`, `sel_rladder_x`, `short_rc_filt_x`, `vref_pwr_on`, and `dpll_cfg_2`. The following `OBSERVE0` fields expose lock-detection TDC steps, sticky-lock clear, lock-detect disable, DCO config, and analog observation select. `OBSERVE1` exposes digital observation selectors, trigger selectors/dividers, and a `lock_timer`. `DFT_OUT` is a full-width `dft_data` readout.

`DCIO_UNIPHY2_UNIPHY_MACRO_CNTL_RESERVED*`, `DCIO_UNIPHY3_UNIPHY_MACRO_CNTL_RESERVED*`, and `DCIO_UNIPHY4_UNIPHY_MACRO_CNTL_RESERVED*` are highly regular blocks. Each instance has 160 register comments in this chunk, numbered `0` through `159`. Each register defines exactly one field, `UNIPHY_MACRO_CNTL_RESERVED`, with shift `0x0` and mask `0xFFFFFFFFL`. These are placeholders for a contiguous reserved hardware-control aperture; the generated header still publishes symbols so offset/mask tables stay aligned with the ASIC register database.

`DC_COMBOPHYCMREGS2_COMMON_*` and `DC_COMBOPHYCMREGS3_COMMON_*` share the same layout. `COMMON_FUSE1`, `COMMON_FUSE2`, and `COMMON_FUSE3` carry validity bits, impedance override values, lane/RON/RTT controls, refresh calibration, drive/current controls, mode enables, and spare or unpopulated fields. `COMMON_MAR_DEEMPH_NOM` stores nominal de-emphasis and margin selections. `COMMON_LANE_PWRMGMT` exposes lane power state fields. `COMMON_TXCNTRL` includes common TX enable/termination-style controls. `COMMON_TMDP` covers TMDS/DP-related common-mode behavior. `COMMON_LANE_RESETS` contains per-lane reset controls and related reset-state fields. `COMMON_ZCALCODE_CTRL` controls impedance calibration code behavior. `COMMON_DISP_RFU1` through `COMMON_DISP_RFU7` are full-width reserved display registers.

`DC_COMBOPHYTXREGS2_*` and `DC_COMBOPHYTXREGS3_*` repeat per physical TX lane. For each of lanes 0-3, the block defines `CMD_BUS_TX_CONTROL_LANE<n>`, `MARGIN_DEEMPH_LANE<n>`, `CMD_BUS_GLOBAL_FOR_TX_LANE<n>`, and `TX_DISP_RFU0_LANE<n>` through `TX_DISP_RFU12_LANE<n>`. The command-bus fields include TX enable/reset-style controls. Margin/de-emphasis fields expose per-lane electrical tuning. The global command bus fields include broader TX configuration bits, while the RFU registers preserve full-width masks for unused or undocumented per-lane slots.

`DC_COMBOPHYPLLREGS2_*` and `DC_COMBOPHYPLLREGS3_*` also share a generated layout. `FREQ_CTRL0` through `FREQ_CTRL3` define fractional/integer frequency control, denominator or ref-divider style fields, slew and spread-spectrum related fields, and DPLL configuration fragments. `BW_CTRL_COARSE` and `BW_CTRL_FINE` expose loop bandwidth tuning. `CAL_CTRL` covers calibration start/enable/override-style controls. `LOOP_CTRL` includes loop filter, DCO, and PLL control parameters. `VREG_CFG` carries regulator and DPLL config bits. `OBSERVE0` and `OBSERVE1` mirror the instance-1 observation fields, and `DFT_OUT` publishes full-width design-for-test data.

`DC_COMBOPHYCMREGS4_COMMON_FUSE1` is only the first register of the next COMBOPHY common instance. It defines fuse validity, RON override value/control, RTT override value/control, refresh calibration enable, spare bits, and several unpopulated fields. `COMMON_FUSE2` is named at line 49875 but its fields are outside this chunk.

## APIs, Types, and Functions

There are no callable APIs or C type definitions in this chunk. The relevant interface is the macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the field's bit offset.
- `REGISTER__FIELD_MASK` gives the positioned bit mask for the same field.
- Address-block comments such as `dce_dc_dc_combophypllregs2_dispdec` map groups of masks to companion register-address definitions in other ASIC headers.

Driver code normally consumes these constants through generated or handwritten AMDGPU register helper macros. The correctness contract is therefore name-based: the register name, field name, instance number, lane number, shift, and mask must match the hardware register database and the corresponding register offset header.

## Control Flow

This chunk has no runtime control flow. The effective control flow exists in display-driver callers that use these constants when programming hardware:

1. Select an instance-specific register address, usually from a companion `dce_12_0_*` register header.
2. Read the MMIO value, or build a fresh register value where the hardware programming sequence allows it.
3. Clear affected bits with one or more `*_MASK` constants.
4. Shift field values by the matching `*__SHIFT` constants and OR them into the value.
5. Write the value back to the display PHY register.
6. For lock, calibration, observation, or DFT paths, poll or read back status/diagnostic fields after the write sequence.

The field names imply several order-sensitive external sequences: PLL frequency setup before enable/update, calibration and Z-calibration sequencing, lane reset release before link training, per-lane TX margin/de-emphasis programming during link setup, sticky-lock clear before lock diagnostics, and DFT/observation selector programming before debug readout.

## State and Persistence

The header itself has no mutable software state and writes nothing. It describes persistent or semi-persistent hardware state in display PHY registers. That state remains in the device until changed by MMIO, reset, power-gating, firmware initialization, or hardware side effects.

Important hardware state represented here includes:

- PLL instance state: frequency controls, bandwidth controls, calibration controls, loop behavior, regulator settings, lock-detection behavior, observation mux selection, lock timers, and DFT output.
- UNIPHY macro reserved state: 160 full-width reserved registers for each of UNIPHY2, UNIPHY3, and UNIPHY4. Even though semantically reserved, these addresses may be preserved for register-map compatibility.
- COMBOPHY common state: fuse-derived impedance/current settings, per-lane power-management controls, common TX controls, TMDS/DP mode state, lane reset state, and Z-calibration code behavior.
- COMBOPHY lane state: lane-local TX enable/control, margin and de-emphasis tuning, global per-lane TX configuration, and reserved lane slots.
- Diagnostic state: observation selectors, sticky lock clear, digital trigger selection/dividers, lock timers, and full-width DFT data outputs.

Several fields are likely interpreted by hardware as control strobes or status-affecting toggles rather than ordinary stored software values. The header does not encode read/write, write-one-to-clear, timing, or reset-default semantics; consumers must follow the DCE 12.0 hardware programming guide and existing AMDGPU sequencing.

## Dependencies and Integration Points

The only direct dependency is the C preprocessor. There are no local includes in this range. Integration depends on the wider AMDGPU register-header set under `drivers/gpu/drm/amd/include/asic_reg/dce`, especially files that define register offsets for the same DCE 12.0 address blocks.

Likely integration points in the AMDGPU display stack include:

- Display Core link encoder and PHY programming paths that configure COMBOPHY TX lanes for DisplayPort, HDMI, or DVI signaling.
- Clock and PLL programming paths that choose COMBOPHY PLL frequency, loop, calibration, and regulator settings for a requested pixel/link clock.
- Link training and modeset paths that adjust per-lane margin, de-emphasis, lane power, and reset state.
- ASIC initialization, resume, and power-management code that preserves or restores PHY register state.
- Hardware debug and diagnostics paths that use observation, DFT, lock-detection, and reserved-register readback.
- Generated register accessor macros that expect all field names and masks to be globally visible.

The repeated instance suffixes are part of the integration contract. Code must select `COMBOPHYCMREGS2/TXREGS2/PLLREGS2` for one PHY instance and `COMBOPHYCMREGS3/TXREGS3/PLLREGS3` for another; mixing instance-specific macros can silently program the wrong physical PHY.

## Risks

The main risk is silent hardware misprogramming. These macros compile to constants, so an incorrect shift or mask will not usually fail at build time. It can instead alter reserved bits, choose the wrong lane, corrupt PLL state, or destabilize display link training.

The UNIPHY reserved blocks are especially sensitive. They are full-width masks over names marked reserved; casual writes through these symbols can affect undocumented hardware behavior. Their presence should be treated as register-map completeness, not as permission to freely program them.

The repeated layouts create copy/generation risk. Instances 2 and 3 should remain structurally identical where the hardware says they are identical, while instance prefixes must still be distinct. Lane blocks must preserve lane numbers in every macro name. A single wrong prefix in a generated macro can route a caller to the wrong PHY instance or lane.

PLL and TX electrical fields are timing and board dependent. Bad frequency-control, loop, regulator, impedance, margin, de-emphasis, or calibration values can cause link instability, black screens, intermittent training failure, high error rates, or excessive signal margin changes without a clear software exception.

Mask width and type are another concern. Many fields use `0xFFFFFFFFL`, and smaller fields use long-suffixed masks such as `0x0003FC00L`. Callers should use appropriate unsigned 32-bit intermediates and helper macros rather than signed arithmetic or narrower storage.

The chunk starts and ends inside larger logical families. A per-file reader must reconcile this with the previous chunk for the start of `DC_COMBOPHYPLLREGS1_VREG_CFG` and with the next chunk for the rest of `DC_COMBOPHYCMREGS4_COMMON_FUSE2` and later instance-4 common/TX/PLL definitions.

## Test Signals

Useful validation is mostly build-time, static, and hardware-integration oriented:

- Compile coverage for AMDGPU display translation units that include `dce_12_0_sh_mask.h`.
- Static checks that every `REGISTER__FIELD__SHIFT` has a matching `REGISTER__FIELD_MASK`, and that every mask aligns with its shift and implied width.
- Generated-header diff checks against the authoritative DCE 12.0 register database for COMBOPHY, UNIPHY, and DCIO blocks.
- Instance- and lane-consistency checks comparing `COMBOPHYCMREGS2` with `COMBOPHYCMREGS3`, `COMBOPHYTXREGS2` with `COMBOPHYTXREGS3`, and lane 0-3 layouts within each TX block.
- Modeset and link-training smoke tests across ports that exercise PHY instances 2 and 3, including DisplayPort and HDMI/DVI paths where applicable.
- PLL programming tests that verify requested clocks, lock status, sticky-lock clearing, and stable output after bandwidth/calibration/regulator programming.
- Electrical tuning tests or hardware lab validation for lane margin, de-emphasis, impedance, and Z-calibration fields.
- Suspend/resume and runtime power-management tests that catch lost lane power, reset, PLL, or calibration state.
- Debug readback tests for `OBSERVE0`, `OBSERVE1`, and `DFT_OUT` fields to confirm selector and data masks target the intended bits.

## Cross-Chunk Notes

This is a middle slice of a much larger generated header. It is not a complete file-level view. The final merged research should connect this chunk to the preceding COMBOPHYPLLREGS1 definitions and the following COMBOPHYCMREGS4/TXREGS4/PLLREGS4 material, then summarize all DCE 12.0 PHY instances and reserved register apertures consistently.

### subset-b-001557: lines 49876-52500

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 49876-52500

## Purpose

This chunk is part of AMD's generated DCE 12.0 register shift/mask header. It defines C preprocessor constants for bit-field positions (`__SHIFT`) and bit-field masks (`_MASK`) used by the AMDGPU display driver when programming DCE display PHY, DisplayPort transmitter, PLL, and DCIO UNIPHY registers.

The assigned range covers the tail of the `dce_dc_dc_combophycmregs4_dispdec` block, all of the COMBOPHY TX and PLL mask definitions for PHY instances 4 and 5, the DCIO UNIPHY reserved-register masks for UNIPHY5 and UNIPHY6, and the beginning of the COMBOPHY instance 6 common/TX/PLL definitions. It ends inside `DC_COMBOPHYPLLREGS6_LOOP_CTRL`, so the remaining PLL6 loop-control masks and subsequent PLL6 fields are owned by the following chunk.

The data here is hardware-description surface, not executable logic. Its purpose is to give display code stable names for bit operations such as "set the TX lane power field", "read PLL lock/observe fields", or "compose a fractional clock-control word" without hard-coding numeric shifts and masks at each call site.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime APIs in this slice. The important interface is the generated macro namespace consumed by register helper macros elsewhere in the AMD display stack.

Key macro families in this chunk:

- `DC_COMBOPHYCMREGS4_COMMON_*`, `DC_COMBOPHYCMREGS5_COMMON_*`, and `DC_COMBOPHYCMREGS6_COMMON_*`: common COMBOPHY fields for fuse data, nominal TX margin/de-emphasis values, lane power management, TX control, lane resets, impedance/calibration override, and display RFU registers.
- `DC_COMBOPHYTXREGS4_*`, `DC_COMBOPHYTXREGS5_*`, and `DC_COMBOPHYTXREGS6_*`: per-lane transmitter fields for lanes 0 through 3 on each covered PHY instance. Each lane has `CMD_BUS_TX_CONTROL`, `MARGIN_DEEMPH`, `CMD_BUS_GLOBAL_FOR_TX`, and thirteen `TX_DISP_RFU*` full-width reserved fields.
- `DC_COMBOPHYPLLREGS4_*`, `DC_COMBOPHYPLLREGS5_*`, and the start of `DC_COMBOPHYPLLREGS6_*`: PLL frequency-control, bandwidth-control, calibration, loop-control, regulator, observation, and DFT-output fields.
- `DCIO_UNIPHY5_UNIPHY_MACRO_CNTL_RESERVED*` and `DCIO_UNIPHY6_UNIPHY_MACRO_CNTL_RESERVED*`: 160 reserved full-width DCIO UNIPHY register masks per instance, each represented as shift 0 and mask `0xFFFFFFFFL`.

Representative fields with behavioral meaning include:

- Common PHY fuse fields: `fuse*_valid`, `fuse1_ron_override_val`, `fuse1_rtt_override_val`, `fuse2_tx_fifo_ptr`, and `fuse3_ei_det_thresh_sel`.
- Common PHY control fields: `pgdelay`, `pgmask`, `vprot_en`, `clkgate_dis`, `slew_rate_ctl_gen1/2/3`, `dual_dvi_mstr_en`, `dual_dvi_en`, lane reset bits, `zcalcode_override`, and `tx_binary_code_override_val`.
- TX lane fields: `tx_pwr`, `tx_pg_en`, `tx_rdy`, `txmarg_sel`, `deemph_sel`, `tx_margin_en`, `link_speed`, `gang_mode`, `max_linkrate`, `pcs_freq`, `pcs_clken`, `pcs_clkdone`, `pll1_always_on`, `rdclk_div2_en`, `tx_boost_adj`, `tx_boost_en`, and `tx_binary_ron_code_offset`.
- PLL fields: `fcw*_frac`, `fcw*_int`, `fcw_denom`, `fcw_slew_frac`, `refclk_div`, `vco_pre_div`, `fracn_en`, `ssc_en`, `freq_jump_en`, `tdc_resolution`, coarse/fine bandwidth controls, calibration gates and ratios, loop feedback controls, regulator controls, observation selectors, and DFT output data.

## Control Flow

This header has no control flow of its own. It is included by DCE120 display implementation files such as `display/dc/resource/dce120/dce120_resource.c`, `display/dc/dce120/dce120_timing_generator.c`, `display/dc/irq/dce120/irq_service_dce120.c`, GPIO translation/factory code, and DCE120 hardware sequencing code. Those C files combine the masks and shifts with generated offset definitions from `dce_12_0_offset.h`.

The runtime pattern in consumers is:

1. Register list macros, for example `SR()` and `SRI()` in `dce120_resource.c`, map generated `mm...` offset constants to MMIO addresses.
2. Mask/shift list macros in the display component headers expand selected `*_MASK` and `*__SHIFT` names into per-block mask/shift structs.
3. Register helper code uses those fields to read, update, and write MMIO registers with correctly positioned bit values.

This chunk only supplies the compile-time constants for that flow. It does not perform MMIO, branch, loop, allocate, or validate values.

## State And Persistence Behavior

The macros are compile-time constants and have no software state. They do not persist data, allocate memory, hold locks, or create side effects.

The hardware state affected by these definitions is indirect. When a display component uses one of these masks to program a register, the resulting state lives in the GPU display block until reset, power-gating, link reprogramming, or a later MMIO write changes it. Examples include persistent lane power/reset state, PLL frequency/calibration state, transmitter margin/de-emphasis settings, and reserved or diagnostic register values.

Because reserved fields are represented with full-width masks, the generated header permits consumers to describe the whole register word. Correct behavior still depends on higher-level code avoiding writes to reserved fields unless the hardware specification or firmware sequence requires them.

## Dependencies

This header depends on the DCE 12.0 register database that generated the symbolic names, shifts, and masks. It is paired with `dce_12_0_offset.h`, which provides the matching `mm...` register offsets and base indices. The shift/mask names are useful only when the consumer also knows the target register address.

Important integration dependencies include:

- The AMDGPU display core register-helper layer, which expects mask and shift constants in the generated `REG__FIELD_MASK` and `REG__FIELD__SHIFT` naming convention.
- DCE120 resource construction, which includes this header and builds register, mask, and shift tables for timing generators, link encoders, stream encoders, AUX, memory input, audio, and hardware sequencing.
- Link encoder and clock-source code that programs DisplayPort/DVI PHY behavior, lane controls, link speed, PLL configuration, and display clocking.
- The ASIC register-generation process. Manual edits risk desynchronizing this mask header from the offset header and from the actual hardware specification.

## Integration Points

The covered COMBOPHY common registers integrate with display PHY setup. Fuse and calibration masks describe hardware-programmed trim and override fields; lane power management and reset masks support link bring-up, power gating, and recovery; TX control masks describe clock gating, slew, and dual-DVI behavior.

The COMBOPHY TX register families integrate with DisplayPort and DVI link training. Per-lane `tx_pwr`, `tx_pg_en`, and `tx_rdy` fields are relevant to lane enable and readiness sequencing. `txmarg_sel`, `deemph_sel`, and `tx_margin_en` represent signal-integrity controls. `CMD_BUS_GLOBAL_FOR_TX` fields connect lane programming to link rate, PCS clocking, gang mode, PLL behavior, and transmitter boost/impedance adjustment.

The COMBOPHY PLL register families integrate with DCE120 clock-source setup. Frequency-control fields encode fractional and integer FCW values and reference/VCO divisors. Calibration and bandwidth fields influence lock behavior, loop stability, spread-spectrum clocking, and dynamic frequency changes. Observation and DFT fields support diagnostics and bring-up validation.

The DCIO UNIPHY reserved-register masks preserve register-map coverage for UNIPHY instances 5 and 6. These definitions may be used by generated tables, debug dumps, or low-level sequences that need to address a full reserved register word, but they do not convey semantic subfields beyond "the entire 32-bit register."

The range boundaries matter for reconciliation: the first line is inside the COMBOPHY4 common fuse area that began before this chunk, and the final line only includes the first PLL6 loop-control mask. The merge lane should combine this with adjacent chunks before drawing per-file conclusions about the complete COMBOPHY4 and PLL6 register groups.

## Risks And Edge Cases

- A wrong shift or mask silently corrupts MMIO field programming. For display PHY and PLL registers, that can appear as link-training failures, unstable clocks, blank displays, intermittent hotplug failures, or power-management regressions.
- The generated naming is highly repetitive across PHY instances 4, 5, and 6. Copy/paste or generator drift between instances can create asymmetric behavior where one connector path fails while another works.
- Some fields are active-low or status-oriented by hardware convention, but the header does not encode access type, reset value, read/write permission, or sequencing requirements. Consumers must rely on the register spec and higher-level driver logic.
- Reserved fields have full-width masks. Accidentally treating an RFU or `UNIPHY_MACRO_CNTL_RESERVED*` definition as safe writable configuration could disturb undocumented hardware state.
- The chunk starts and ends mid-address-block. Research or tooling that treats this slice as a complete file region would miss `COMMON_FUSE1/FUSE2` context before line 49876 and the rest of `DC_COMBOPHYPLLREGS6_LOOP_CTRL` after line 52500.
- The constants use `L`-suffixed masks such as `0xFFFFFFFFL`. Refactors should preserve unsigned 32-bit MMIO semantics and avoid sign-extension surprises when values are widened or combined.
- These masks must stay synchronized with the corresponding `dce_12_0_offset.h` definitions and with the ASIC base-index mapping used by `BASE()`, `SR()`, and `SRI()` macros.

## Test Signals

Useful validation signals are primarily compile-time, hardware bring-up, and display conformance checks:

- AMDGPU display code that includes `dce_12_0_sh_mask.h` should compile without missing mask or shift symbols for DCE120 resources, IRQ, timing-generator, GPIO, AUX, link-encoder, and hardware-sequencing paths.
- Static checks can compare each `*_MASK` against its `*__SHIFT` and expected field width, and compare repeated PHY instances 4, 5, and 6 for intentional symmetry.
- Register-generation validation should confirm this header matches the same DCE 12.0 source database as `dce_12_0_offset.h`.
- Display bring-up on DCE12 hardware should complete without PLL lock failures, PHY power sequencing timeouts, lane readiness timeouts, or link-training errors on connectors mapped to the covered PHY/UNIPHY instances.
- DisplayPort validation should exercise multiple link rates, lane counts, voltage-swing/pre-emphasis levels, spread-spectrum settings, power-gating transitions, hotplug cycles, suspend/resume, and monitor reconnects.
- Diagnostics should confirm that debug or trace register writes using these masks preserve unrelated bits in the same register word.
- Regression tests should include connectors backed by each repeated instance, because instance-asymmetric mask mistakes often show up only on a subset of physical ports.

### subset-b-001558: lines 52501-54982

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 52501-54982

## Scope

This chunk covers lines 52501-54982 of the generated-style AMD DCE 12.0 register shift/mask header. It contains only C preprocessor constants for bit positions and already-positioned masks. There are no structs, functions, inline helpers, branches, or executable statements in this slice.

The slice starts in the tail of the `DC_COMBOPHYPLLREGS6` PLL register family, then defines the full `UNIPHY8`, `COMBOPHYCMREGS8`, `COMBOPHYTXREGS8`, and `COMBOPHYPLLREGS8` display PHY families, then begins the `DSI0` and `DSI1` MIPI DSI display-interface register families. The chunk ends inside `DSI1_DISP_DSI_DLN0_PHY_ERROR`, so the final per-file merge should reconcile that register with the following chunk.

## Purpose

The purpose of this header region is to publish field-level metadata for low-level AMDGPU display driver code programming DCE 12.0 memory-mapped registers. Each register field appears as a `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` pair. Callers combine these constants with companion register-address headers and AMDGPU register access macros to encode, decode, poll, clear, or acknowledge hardware register bits.

The covered hardware domains are:

- COMBOPHY PLL instance 6 tail fields for loop, voltage-regulator, observation, and DFT readout.
- UNIPHY8 macro reserved registers `DCIO_UNIPHY8_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED159`, each modeled as a full-width reserved field.
- COMBOPHY common instance 8 controls for fuses, lane power management, TX control, TMDS/DisplayPort mode behavior, lane resets, calibration code, and RFU registers.
- COMBOPHY TX instance 8 per-lane controls for four lanes, including command-bus TX settings, margin/de-emphasis, global TX controls, and lane RFU slots.
- COMBOPHY PLL instance 8 frequency, bandwidth, calibration, loop, VREG, observation, and DFT fields.
- DSI0 and the first part of DSI1 MIPI DSI controller fields, including enable/reset, mode programming, DMA command/data windows, command mode, readback, trigger, external TE/reset, lane CRC, ULPS/stop controls, error reporting, timers, PHY clock timing, EOT, BIST, interrupt masking, clock control/status, FIFOs, tearing-effect control, lane status, perf controls, readback count, and command-memory power controls.

## Important Macro Families

`DC_COMBOPHYPLLREGS6_*` at the beginning is a continuation from the prior chunk. It includes PLL loop fields such as feedback slip disable, TDC/NCTL clock selection, PRBS enable, clock gate enable, and phase offset, plus `VREG_CFG`, `OBSERVE0`, `OBSERVE1`, and `DFT_OUT`. These fields are relevant to PHY PLL stability, analog observation, sticky-lock handling, and design-for-test readback.

`DCIO_UNIPHY8_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED159` are repetitive full-register definitions. Each exposes a single `UNIPHY_MACRO_CNTL_RESERVED` field at shift 0 with mask `0xFFFFFFFFL`. Their value is mostly structural: they preserve generated register-map coverage for the UNIPHY8 decode region even when the fields are reserved or undocumented for normal driver programming.

`DC_COMBOPHYCMREGS8_COMMON_*` describes the common PHY-side configuration for instance 8. `COMMON_FUSE1/2/3` expose calibration/fuse controls such as spare fuses, PLL REFCLK/VCO mode fuses, receiver termination, lane-mode margin/de-emphasis values, and RDAC/termination references. `COMMON_LANE_PWRMGMT`, `COMMON_TXCNTRL`, `COMMON_TMDP`, and `COMMON_LANE_RESETS` define lane power, TX bus isolation, data enable, TMDS/DP link mode, and per-lane reset/powerdown controls. `COMMON_ZCALCODE_CTRL` and `COMMON_DISP_RFU1` through `RFU7` cover impedance calibration and reserved-for-future-use fields.

`DC_COMBOPHYTXREGS8_*_LANE0` through `LANE3` repeats the same TX register layout per physical lane. `CMD_BUS_TX_CONTROL_LANE*` contains TX enable, high-impedance, and bus isolation controls. `MARGIN_DEEMPH_LANE*` carries transmit margin and de-emphasis settings. `CMD_BUS_GLOBAL_FOR_TX_LANE*` includes boost, calibration, CDR, driver current, bypass, and slew/mode control fields. The `TX_DISP_RFU*_LANE*` registers are full-width RFU slots for each lane.

`DC_COMBOPHYPLLREGS8_*` is the complete PLL instance 8 field set. `FREQ_CTRL0/1/2/3` cover fractional and integer feedback/divider controls, refclk divider, VCO pre-divider, fractional-N enable, spread-spectrum enable, frequency-jump behavior, TDC resolution, and DPLL configuration. `BW_CTRL_COARSE`, `BW_CTRL_FINE`, `CAL_CTRL`, `LOOP_CTRL`, `VREG_CFG`, `OBSERVE0`, `OBSERVE1`, and `DFT_OUT` define loop bandwidth, calibration, lock detection, analog/digital observation, regulator behavior, PRBS/test controls, and full-width DFT data.

`DSI0_DISP_DSI_*` is a broad MIPI DSI controller register set. Key groups include:

- `CTRL` and `STATUS` for DSI enable, video/command mode enable, data-lane and clock-lane enables, PHY enables, clock resets, CRTC selection, ECC/CRC checks, busy bits, FIFO state, overflow/underflow status, trigger state, and clear bits.
- `VIDEO_MODE_*` for virtual channel, destination format, traffic mode, low-power behavior during blanking/sync regions, sync/data packet types, payload lengths, pixel datatype, and blanking packet datatype.
- `COMMAND_MODE_*`, `DMA_*`, `DENG_DATA_LENGTH`, `CMD_FIFO_*`, and software trigger registers for command-mode packet construction, DMA command/data addressing, DCS commands, FIFO control, and software-driven command/BTA/reset events.
- `ACK_ERROR_REPORT`, `RDBK_DATA*`, `RDBK_DATATYPE*`, and `RDBK_NUM` for MIPI ACK/error packet classification and readback payload capture.
- `TRIG_CTRL`, `EXT_MUX`, `EXT_TE_PULSE_DETECTION_CTRL`, `EXT_RESET`, and `TE_CTRL` for command trigger source selection, external tearing-effect muxing/polarity/timing, external reset, and TE filtering.
- `LANE_CRC_*`, `PIXEL_CRC_CTRL`, `LANE_CTRL`, `DLN0_PHY_ERROR`, `LANE_STATUS`, and timer/PHY-clock timing registers for lane CRC/readback, ULPS request/exit, force-stop, high-speed clock request, PHY error state, lane stop/ULPS status, low-power/high-speed timers, and D-PHY timing.
- `MIPI_BIST_*` for built-in self-test frame/block size, LFSR mode/init/seed, start, status, and expected/generated CRC.
- `ERROR_INTERRUPT_MASK`, `INTERRUPT_CTRL`, `CLK_CTRL`, `CLK_STATUS`, `DENG_FIFO_STATUS`, `DENG_FIFO_CTRL`, `PERF_CTRL`, `HSYNC_LENGTH`, and `CMD_MEM_PWR_CTRL` for interrupt masking/ack, DSI/byte/escape clock request/enable/status, data-engine FIFO watermarks, performance counters, sync-length programming, and command-memory power gating.

`DSI1_DISP_DSI_*` repeats the same initial DSI register layout as DSI0 from `CTRL` through `LANE_CTRL`, and this chunk includes the beginning of `DLN0_PHY_ERROR`. The naming and masks mirror DSI0 for the covered range, enabling callers to select the DSI instance by macro prefix.

## APIs, Types, and Functions

There are no callable APIs, C types, or functions. The exported interface is the macro namespace itself:

- `REGISTER__FIELD__SHIFT` gives the low-bit offset for an encoded register field.
- `REGISTER__FIELD_MASK` gives the already shifted field mask.
- Some hardware fields naturally end with `_MASK`, producing names such as `*_ERR_ESC_MASK__SHIFT` and `*_ERR_ESC_MASK_MASK`; these are intentional generated symbols, not double-application mistakes.
- Clear/ack fields often share a bit position and mask with the corresponding status field, for example `*_OVERFLOW` and `*_OVERFLOW_CLR` or DSI ACK error bits and their `_CLR` forms.

Because these are global preprocessor symbols, the field names are part of the ABI between generated register metadata and the low-level display driver code. Any rename or mask change can break build-time references or, worse, compile while programming the wrong hardware bit.

## Control Flow

This chunk has no direct control flow. The runtime sequences are implemented by callers using these constants. Typical flows implied by the fields are:

1. Configure PHY/PLL values by masking and shifting frequency, bandwidth, calibration, VREG, or loop-control fields, then poll lock/ready/observation bits through the corresponding register family.
2. Program DSI controller mode: select video or command mode, enable lanes/PHY/clock lane, release DSI clock resets, set CRTC source and packet checking, and then enable the interface.
3. Program MIPI video-mode packetization and timings by writing virtual-channel, datatype, payload, blanking, traffic-mode, and sync fields.
4. Program command-mode DMA and command FIFO offsets, lengths, pitches, dimensions, DCS command controls, and trigger source selection, then issue hardware or software triggers.
5. Monitor DSI status, FIFO, lane, timeout, error, and clock-status fields; clear sticky status or interrupt bits using the matching `_CLR` or ack fields.
6. Enter or exit lane low-power states through ULPS request/exit bits, force TX stop controls, clock-lane high-speed request, timer values, and lane status polling.
7. Exercise diagnostics through lane/pixel CRC, MIPI BIST, readback data registers, DFT outputs, and PHY observation selectors.

The important ordering rules are external hardware rules rather than C code in this header. In particular, resets, PLL changes, DSI clock requests, lane enable/ULPS transitions, BTA/readback, and interrupt clear/ack behavior must be sequenced by the caller against the DCE register specification.

## State and Persistence

The header stores no software state. It describes persistent hardware state held in DCE display registers until reset, power-gated, reprogrammed, or updated by hardware side effects.

State domains visible in this slice include:

- PHY/PLL analog state: calibration codes, loop bandwidth, regulator configuration, lock detection, observation muxes, PRBS/test state, and DFT readout.
- PHY lane state: lane powerdown/reset, TX enable/high-Z/isolation, TMDS/DP mode selection, transmit margin/de-emphasis, driver current, and per-lane RFU state.
- DSI mode state: controller enable, video versus command mode, lane enables, PHY enables, reset state, CRTC routing, ECC/CRC checking, and interleave/pre-trigger behavior.
- DSI packetization state: MIPI virtual channel, traffic mode, datatype values, payload lengths, blanking packet types, command-mode packet types, DMA offsets and dimensions, FIFO thresholds, and null packet values.
- DSI status and error state: busy bits, FIFO empty/full/overflow/underflow, TE abort/contention, ACK/error-report bits, readback data, timeout status, lane PHY error bits, interrupt mask/status/ack, and clock status.
- DSI power/timing state: low-power and high-speed timers, clock timing, EOT packet behavior, command-memory power control, and ULPS/force-stop controls.

Many status fields are sticky until explicitly cleared. The paired `_CLR` and ack macros show write-one-to-clear or write-one-to-ack style behavior, but the header does not encode access type. Callers must avoid normal read/modify/write patterns that accidentally set clear bits or preserve stale clear bits.

## Dependencies and Integration Points

This header depends only on the C preprocessor and companion generated AMD DCE register headers for addresses, offsets, and block instances. It integrates with the AMDGPU DRM display stack under `drivers/gpu/drm/amd`, especially low-level display, clock, PHY, link, and panel/DSI programming paths.

Likely integration points include:

- Register accessor macros that take an address macro plus `*_MASK` and `*__SHIFT` values.
- Display PHY/UNIPHY initialization code selecting COMBOPHY instance 8 and lane 0-3 fields.
- PLL programming and diagnostics for COMBOPHY PLL instances 6 and 8.
- MIPI DSI panel bring-up, command-mode transfer, video-mode transfer, BTA/readback, TE synchronization, reset handling, and lane power-state management.
- Interrupt handling and diagnostics for DSI error/status, FIFO, timeout, lane, and clock events.
- Hardware validation paths using DSI BIST, CRC, DFT, and observation registers.

The parallel `DSI0` and `DSI1` prefix structure is an instance-selection mechanism. The merge lane should check the following chunk for the rest of `DSI1` and determine whether all DSI0 fields are repeated for DSI1.

## Risks

The main risk is silent hardware misprogramming. A wrong shift or mask compiles cleanly but can write reserved bits, acknowledge the wrong interrupt, clear sticky error state unexpectedly, enable the wrong lane, or leave the display PHY in an unstable mode.

Reserved and RFU registers are especially sensitive. The `UNIPHY8_UNIPHY_MACRO_CNTL_RESERVED*`, `COMMON_DISP_RFU*`, and `TX_DISP_RFU*_LANE*` full-width masks preserve register-map shape but should not be treated as freely writable feature controls without hardware documentation.

Repeated instance and lane layouts create copy/generation hazards. DSI0 and DSI1, four COMBOPHY TX lanes, and many reserved UNIPHY slots are almost identical. A one-character prefix or lane-number mismatch can direct a caller at the wrong register field while remaining syntactically valid.

Status/clear aliases require care. Several fields define both a state bit and a `_CLR` bit at the same mask. Generic helper code that reads a register, modifies unrelated bits, and writes the entire value back can inadvertently clear errors or interrupts if it preserves a read value containing set status bits.

Clock, reset, PLL, and ULPS fields are timing-sensitive. Misordering DSI clock enables, reset release, PLL calibration/lock polling, D-PHY timing, lane stop/ULPS transitions, or command triggers can cause hangs, FIFO underflow, packet errors, or panels failing to respond rather than a clean software failure.

Type width is also relevant. Full-width masks use `0xFFFFFFFFL`; callers should use unsigned 32-bit arithmetic or existing register helpers to avoid sign-extension or truncation issues on unusual host/compiler combinations.

## Test Signals

Useful validation signals for this chunk are mostly build, static, and hardware-integration tests:

- Compile coverage for AMDGPU display translation units that include `dce_12_0_sh_mask.h` and reference COMBOPHY8 or DSI0/DSI1 fields.
- Generated-header consistency checks ensuring every `__SHIFT` has a matching `_MASK`, masks align with shifts, and repeated DSI/lane families match expected widths.
- Diff checks against the authoritative DCE 12.0 register database, especially around the chunk boundaries for `DC_COMBOPHYPLLREGS6` and `DSI1_DISP_DSI_DLN0_PHY_ERROR`.
- Display PHY/link smoke tests that exercise COMBOPHY lane enable, reset, margin/de-emphasis, PLL frequency/calibration, and observation/DFT readback.
- MIPI DSI panel tests covering video mode, command mode, DMA command transfer, BTA/readback, external reset, TE triggering, and clock/reset sequencing on both DSI0 and DSI1 where hardware exposes both instances.
- Error-path tests or register readback diagnostics for DSI FIFO overflow/underflow, ACK error report bits, timeout status, lane PHY errors, interrupt mask/ack behavior, and clear-on-write semantics.
- Diagnostics using DSI lane/pixel CRC and MIPI BIST expected/generated CRC fields to confirm that encoded masks land in the intended bits.
- Power-management tests around DSI command-memory power control, DSI/byte/escape clock request/status, lane ULPS request/exit, and force-stop transitions.

## Cross-Chunk Notes

The beginning of this chunk depends on the previous chunk for the start of `DC_COMBOPHYPLLREGS6_LOOP_CTRL`. The end of this chunk stops after the first `DSI1_DISP_DSI_DLN0_PHY_ERROR__DLN0_ERR_CONTENTION_LP1__SHIFT` definition, before the remaining masks and later DSI1 registers. The final per-file research should merge this with adjacent chunks before drawing conclusions about the complete COMBOPHY6 and DSI1 register families.

### subset-b-001559: lines 54983-57512

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 54983-57512

## Scope

This chunk covers lines 54983-57512 of the generated-style AMD DCE 12.0 register shift/mask header. It contains only C preprocessor constants: no functions, structs, enums, inline helpers, or executable code. The chunk starts inside the `DSI1_DISP_DSI_DLN0_PHY_ERROR` macro family and ends at the first two definitions for `AZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_CONTROL_WIRELESS_DISPLAY_IDENTIFICATION`; the following endpoint registers continue in later lines.

The slice contains 2530 source lines, with 2053 `#define` lines and 411 register/address-block comments. Its exported interface is the set of globally visible register-field macros that AMDGPU display code combines with companion offset headers and MMIO/indexed-register access helpers.

## Purpose

The macros describe bit offsets and already-positioned masks for several DCE display, DisplayPort receiver, performance, and Azalia audio register blocks:

- Tail of DSI1 MIPI DSI control and status: lane-zero PHY error bits, low-power/high-speed timeout timers, PHY timing, EOT packet fields, generic escape triggering, MIPI BIST setup/status, error interrupt masks, DSI interrupt control, DSI clock state, FIFO state/control, TE handling, lane status, performance mode, readback count, and command-memory power control.
- `dce_dc_dprx_sd0_dispdec` and `dce_dc_dprx_sd1_dispdec`: two DisplayPort receiver stream decoder instances with stream enable, MSA/VBID decode, current-line and display-timer state, MSE saturation, pixel format, received/toggled stream status, line-number triggers, main and secondary deframing errors, VCPF phase state, majority-vote and pixel FIFO errors, SDP steering/data/errors, audio headers, FIFO errors, measured totals, BS counter, and MSE action handling.
- `dce_dc_dc_perfmon10_dispdec`: one display performance monitor instance with counter-control, event-selection, state, monitor-control, interrupt, and counter-value registers.
- `dce_dc_dc_zcalregs_dispdec`: impedance/calibration-related control, DFX, and fuse fields.
- Sparse VGA memory page address aliases for write/read page address blocks.
- `dce_dc_azdec`: Azalia HDA controller command/response rings, immediate command windows, DMA position buffer base, and wall-clock alias fields.
- `dce_dc_azstream0_azdec` through `dce_dc_azstream7_azdec`: eight Azalia output stream descriptor instances.
- `azf0stream0_streamind` through `azf0stream15_streamind`: sixteen indexed Azalia stream performance/latency and FIFO-size control blocks.
- Beginning of `azf0endpoint0_endpointind`: endpoint0 converter and pin-widget definitions, including format/channel control, digital converter state, supported formats/rates, GTC embedding/counter deltas, pin capabilities, unsolicited responses, pin sense, speaker/channel allocation, audio descriptors, multichannel enables, lipsync/HBR response fields, sink information strings, hot-plug/audio-enable control, configuration defaults, IEC 60958 channel-status override fields, LPIB snapshots, coding type, format-change notification, and wireless-display identification.

## Important Macro Families

Every field follows the generated naming convention:

- `REGISTER__FIELD__SHIFT` gives the bit offset.
- `REGISTER__FIELD_MASK` gives the field mask in its final register position.
- If the hardware field itself is named `*_MASK`, the generated macro becomes `REGISTER__FIELD_MASK__SHIFT` plus `REGISTER__FIELD_MASK_MASK`; this awkward-looking double `MASK` form is intentional.

The DSI1 section exposes order-sensitive control fields. Timeout registers provide `LP_RX_TO`, `BTA_TO`, and `HS_TX_TO`; status registers pair timeout status bits with same-position clear bits. Error interrupt coverage spans readback ECC/CRC/incomplete-packet errors, error packets, interleave/TE aborts, D-PHY lane errors, timeout events, DMA/command FIFO underflows, display-engine FIFO overflow/underflow, per-lane HS FIFO overflows, LP FIFO overflow, and interleave-operation contention. `DSI_INTERRUPT_CTRL` uses repeated status/ack/mask triplets for command-mode DMA/DENG completion, video-mode done, error, software BTA done, and TE trigger. FIFO and lane status macros surface underflow/overflow, FIFO full/empty, packet counts, lane busy/ready/stop-state, and ULPS active flags.

The DPRX stream decoder blocks are nearly identical for `DPRX_SD0` and `DPRX_SD1`. They expose stream and packet decode state: MSA words, VBID, current line, timer snapshot/mode, MSE SAT values, force-update and active state, vertical parameter, pixel format, MSA received/toggled bits, line-number match interrupts, detailed main/secondary deframing errors, VCPF phase lock/error, majority-vote errors, pixel FIFO errors, SDP payload sizing and steering, SDP received levels/data/errors, audio header and FIFO error state, SDP control, measured vertical/horizontal totals, BS counter, and MSE active-action handling.

`DC_PERFMON10` mirrors the perfmon layout seen in other DCE chunks. It includes event selection, counted-value selectors, increment mode, hardware gating, count-off and restart controls, interrupt enable/status/ack, active state, interrupt type, counter-selection fields, counted-value type, stop selectors, packed counter state fields, perfmon report count and state, clock enable, and low/high counter-value readback.

The Azalia controller and stream descriptor macros describe HDA-like ring-buffer and stream state. `CORB_*` and `RIRB_*` cover write/read pointers, control, status, size, and base addresses. Immediate command windows include input/output data and indices plus status. `DMA_POSITION_*` and `WALL_CLOCK_COUNTER_ALIAS` expose DMA position and timing. Each `AZSTREAM0` through `AZSTREAM7` descriptor has the same control/status layout: stream reset/run, IOCE/FEIE/DEIE interrupt enables, descriptor error/FIFO-ready/status flags, traffic priority, stripe control, stream number, link position, cyclic buffer length, last valid index, FIFO size, format fields, BDL pointer lower/upper address, and link-position alias.

The indexed `AZF0STREAM0` through `AZF0STREAM15` blocks are compact and repeated: FIFO size allocation, latency counter reset/enable, worst-case latency, cumulative latency, and cumulative request count. These are likely selected through an indexed endpoint/stream register window rather than direct MMIO offsets.

The endpoint0 converter/pin section maps display-audio codec semantics. Converter fields cover audio widget capabilities, channel count, supported PCM size/rate and stream formats, converter sample format, channel/stream ID, digital converter enable/validity/category/copyright/non-audio/professional bits, stripe control, ramp rate, GTC embedding, and min/current/max GTC deltas. Pin fields cover pin widget capabilities, capabilities flags, unsolicited response tag/enable, pin-sense, output enable, speaker/channel allocation and HDMI/DP connection flags, audio descriptors 0-13, multichannel lane/channel enable/mute/channel IDs, lipsync/HBR responses, sink info bytes, hot-plug/audio-enabled flags, forced unsolicited response payloads, configuration default fields, IEC 60958 channel-status overrides, association info, digital output active state, LPIB snapshot/position/timer state, coding type, format-change reporting, and wireless-display identification.

## APIs, Types, and Functions

There are no callable APIs, C types, or functions in this chunk. The macro names are the ABI-like surface used by AMDGPU display code. Callers are expected to use matching register address macros from companion generated offset headers, then apply these field macros through register helpers or normal read/modify/write code.

This file is included directly by DCE 12.0 display components, including `display/dc/dce120/dce120_timing_generator.c`, `display/dc/irq/dce120/irq_service_dce120.c`, `display/dc/hwss/dce120/dce120_hwseq.c`, `display/dc/resource/dce120/dce120_resource.c`, DCE 12.0 GPIO factory/translation code, and `amdgpu/gmc_v9_0.c`. The macro names therefore need to remain stable for both display core code and low-level AMDGPU integration.

## Control Flow

The header has no runtime control flow. Hardware programming flow is implied by the fields:

1. Select a register instance by choosing the macro family, such as `DPRX_SD0` versus `DPRX_SD1`, `AZSTREAM0` through `AZSTREAM7`, or `AZF0STREAM0` through `AZF0STREAM15`.
2. Read a MMIO or indexed register through the matching offset/address macro.
3. Clear existing bits with `*_MASK`, shift new values with `*__SHIFT`, then write the combined value back.
4. For status and interrupt registers, read status bits and write ack/clear bits named `*_ACK`, `*_AK`, `*_CLR`, or `*_CLEAR` according to the hardware register semantics.
5. For FIFOs, rings, stream descriptors, and perfmon counters, poll or snapshot status/readback fields after enabling run or measurement fields.

The most sequencing-sensitive areas are DSI timeout/error clearing, DSI interrupt ack/mask handling, DSI clock and FIFO readiness, DPRX line-number/deframing/SDP error status, perfmon start/stop and interrupt ack, Azalia CORB/RIRB pointer/control updates, stream descriptor reset/run transitions, and endpoint format/audio-enable changes.

## State and Persistence

The header itself stores no software state and has no persistence. Its constants describe hardware state fields that persist in display-controller, receiver, performance-monitor, and audio registers until reset, power-management transitions, firmware/hardware updates, or driver writes change them.

Visible state domains include:

- DSI1 D-PHY lane error latches, timeout counters/status, packet/EOT control, BIST configuration and completion, interrupt status/masks/acks, clock ready/error state, DENG and command FIFO state, TE trigger/line state, lane stop/ULPS/ready/busy state, and command-memory power state.
- DPRX SD0/SD1 stream decode state, MSA/VBID snapshots, timer/current-line state, MSE saturation, stream-status toggles, deframing/majority-vote/pixel-FIFO/SDP/audio FIFO error latches, measured frame totals, and MSE action state.
- Perfmon10 configuration, event selection, active state, interrupt latches, and low/high counter values.
- ZCAL control/DFX/fuse state that can affect calibration behavior.
- Azalia controller ring state, immediate command status, DMA position base, wall-clock counter, stream descriptor run/reset/interrupt/error state, buffer positions, audio format, BDL pointers, latency counters, and endpoint codec/pin configuration.
- Endpoint0 display-audio pin state, including sink descriptors, hot-plug/audio-enabled state, unsolicited response behavior, IEC 60958 channel status overrides, LPIB snapshots, format-change state, and wireless display identification.

Several fields are full-width `0xFFFFFFFFL` values for data, address, counter, association, payload, and description registers. Others are single-bit status/enable/ack fields. Callers must preserve reserved bits and use the correct access width/path, especially for indexed Azalia endpoint and stream registers.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor, but it is useful only with the generated DCE 12.0 offset/address headers and AMDGPU display register access helpers. Its integration points are low-level and hardware-facing:

- DCE 12.0 display core code that includes `dce_12_0_sh_mask.h`.
- DSI command/video-mode, D-PHY, FIFO, timeout, BIST, and interrupt handling paths.
- DisplayPort receiver diagnostics or bring-up code that reads stream decoder MSA/VBID, line, SDP, audio, FIFO, and deframing fields.
- Display performance-monitor setup and counter collection paths.
- Calibration or bring-up code touching ZCAL fields.
- HDMI/DP audio code using Azalia HDA controller, stream descriptor, stream latency/FIFO, converter, pin-widget, channel allocation, sink info, lipsync, HBR, channel-status, and LPIB fields.
- Companion ASIC-generation data: the same endpoint and pin-control names appear in nearby ASIC families and offset headers, so this chunk must reconcile with per-ASIC offset files rather than standalone names.

Repeated instance prefixes are important integration signals. `DPRX_SD0`/`DPRX_SD1`, `AZSTREAM0`-`AZSTREAM7`, and `AZF0STREAM0`-`AZF0STREAM15` have parallel layouts; callers should select the instance explicitly instead of deriving names manually.

## Risks

The primary risk is silent hardware misprogramming. Any incorrect mask or shift compiles normally but can update the wrong register field, corrupt reserved bits, miss an interrupt ack, or leave status latches uncleared. These failures may present as display link instability, DSI command timeouts, missing TE/BTA completion, DisplayPort receiver decode errors, audio stream failures, or lost interrupts rather than a direct software fault.

Boundary risk exists for this chunk: it starts after the beginning of `DSI1_DISP_DSI_DLN0_PHY_ERROR` and ends before the complete wireless-display/remote-keepalive/audio-enable endpoint region. The final per-file reconciliation should merge adjacent chunks before treating the DSI PHY-error and endpoint0 sections as complete.

Generated names ending in `MASK_MASK` are easy to misread but represent legitimate fields named `*_MASK`. Renaming or simplifying them would break existing generated-code conventions and call sites.

Repeated register layouts increase copy/generation risk. A one-bit drift between `DPRX_SD0` and `DPRX_SD1`, between `AZSTREAM*` instances, or among `AZF0STREAM*` latency blocks would be hard to see in review and may only affect a subset of links or audio streams.

Status/ack/clear fields are especially sensitive. Some bits share the same shift and mask for status and clear/ack semantics, so drivers must know whether a write-one-to-clear, write-one-to-ack, or read-only access is required from the hardware spec. Blind read/modify/write can accidentally clear latched errors or acknowledge interrupts.

Audio fields combine HDA, HDMI/DP audio-infoframe-like, IEC 60958, and display hotplug semantics. Incorrect channel allocation, descriptor, format, stream ID, or channel-status fields can produce user-visible audio failures even when display modesetting succeeds.

## Test Signals

Useful validation signals for this chunk are mostly static and hardware-integration oriented:

- Build coverage for all DCE 12.0 translation units that include `dce_12_0_sh_mask.h`.
- Generated-header consistency checks that every `REGISTER__FIELD__SHIFT` has a matching mask, masks align with their shifts, repeated instances have identical field layouts where expected, and no duplicate macro names collide.
- Diff or regeneration checks against the authoritative ASIC register database for DCE 12.0.
- DSI hardware smoke tests covering command mode, video mode, timeout/error clearing, TE events, BTA completion, FIFO underflow/overflow reporting, lane stop/ULPS state, and MIPI BIST done/status.
- DPRX receiver diagnostics that verify MSA/VBID decode, line-number triggers, measured totals, SDP reception/data/error paths, audio FIFO errors, deframing errors, and stream-status toggles on both SD0 and SD1.
- Perfmon tests that program `DC_PERFMON10`, start/stop counting, read low/high values, and exercise interrupt status/ack fields.
- Azalia/HDMI/DP audio tests that start and stop stream descriptors, verify CORB/RIRB and immediate command paths, check DMA/LPIB position snapshots, validate channel allocation and audio descriptors, test multichannel/HBR/lipsync paths, and confirm hot-plug/audio-enabled and unsolicited-response behavior.
- Register readback tests around full-width address/data/counter fields to catch truncation from signed or narrow intermediates.

## Cross-Chunk Notes

This is one interior slice of a 64798-line generated header. The final per-file document should reconcile this research with adjacent chunks for the beginning of the DSI1 PHY-error block before line 54983 and the continuation of endpoint0 remote-keepalive/audio-enable/status registers after line 57512.

### subset-b-001560: lines 57513-59880

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 57513-59880

## Scope

This chunk covers lines 57513-59880 of the AMD DCE 12.0 generated register mask header. The source is C preprocessor metadata only: it exports `__SHIFT` and `_MASK` constants for bitfields in Azalia HD-audio endpoint registers. There are no C functions, structs, enums, or executable statements in this slice.

The chunk begins in the tail of `azf0endpoint0_endpointind`, contains complete repeated blocks for `azf0endpoint1_endpointind` through `azf0endpoint4_endpointind`, and ends at the start of `azf0endpoint5_endpointind` after `AZF0ENDPOINT5_AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_PIN_SENSE` is introduced. The repeated register families describe the HDMI/DisplayPort audio codec converter and pin widgets exposed by the GPU display engine.

## Purpose

The macros let AMDGPU display/audio code address individual fields in DCE 12.0 Azalia function-0 endpoint registers without hard-coded bit arithmetic. For each endpoint, the header describes:

- Converter widget capabilities and stream format controls.
- Converter channel/stream routing, digital converter status/control bits, supported formats, supported sample sizes/rates, striping, ramp-rate, and GTC presentation-time embedding.
- Pin widget capabilities, unsolicited response controls, pin-sense response, widget control, speaker/channel allocation, ELD/audio descriptors, sink information, hot-plug/unsolicited-response forcing, configuration defaults, multichannel enable/mode fields, IEC 60958 channel-status overrides, LPIB snapshots, coding type, format-change reporting, wireless-display identification, remote keepalive, and audio enable/disable/format-change interrupt status.

These definitions are part of the low-level display register database. They are normally paired with companion address headers and accessor helpers that select the endpoint register offset, then use this file's mask/shift values to pack or extract fields.

## Important Macro Families

`AZF0ENDPOINT0_*` appears only as a continuation from the previous chunk. In this slice it completes endpoint 0 fields for wireless-display identification, remote keepalive, audio-enable status, and audio enabled/disabled/format-changed interrupt status.

`AZF0ENDPOINT1_*`, `AZF0ENDPOINT2_*`, `AZF0ENDPOINT3_*`, and `AZF0ENDPOINT4_*` are complete repeated endpoint layouts. Each instance has the same field structure with only the endpoint number changed. Important groups include:

- `AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: channel, amplifier, format override, stripe, processing, unsolicited response, connection-list, digital, power-control, LR-swap, delay, and widget type fields.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT`: number of channels, bits per sample, sample-base divisor/multiple/rate, and stream type.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_CHANNEL_STREAM_ID`: packed channel and stream IDs.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_DIGITAL_CONVERTER`: digital enable, validity/config/preemphasis/copy/non-audio/professional flags, category code, and keepalive.
- `AZALIA_F0_CODEC_CONVERTER_PARAMETER_STREAM_FORMATS` and `SUPPORTED_SIZE_RATES`: advertised HDA stream formats, sample-rate capability bits, and bit-depth capability bits.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_GTC_EMBEDDING` plus `GTC_COUNTER_DELTA`, `GTC_COUNTER_DELTA_MIN`, and `GTC_COUNTER_DELTA_MAX`: presentation-time embedding controls and full-width timing-delta counters.
- `AZALIA_F0_CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `PIN_PARAMETER_CAPABILITIES`: pin widget capability fields such as HDMI/DP indication, EAPD, VREF control, input/output support, jack detection, and widget type.
- `AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`: ELD-style audio descriptor fields, including coding type, channel count, rates, byte fields, bit rates, profile/level, and other sink descriptor bytes.
- `AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2`: per-channel enable bits and mapped channel IDs for multi-channel audio.
- `AZALIA_F0_CODEC_PIN_CONTROL_SINK_INFO0` through `SINK_INFO8`: sink metadata bytes and connection/port/sink state fields.
- `AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8`: IEC 60958 channel-status override fields for professional/consumer, audio/non-audio, copyright, category, source/channel number, clock accuracy, sample frequency, word length, CGMSA, and original frequency bits.
- `AZALIA_F0_AUDIO_ENABLE_STATUS`, `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS`: status/interrupt flag, mask, and type fields for audio state transitions.

`AZF0ENDPOINT5_*` starts a fifth repeated endpoint block but this chunk only covers its converter registers, pin audio-widget capability, pin capability register, and the declaration of the pin-sense control block. Later lines must be reconciled to capture the rest of endpoint 5.

## APIs, Types, and Functions

There are no callable APIs, type declarations, or functions. The exported interface is the generated macro naming convention:

- `REGISTER__FIELD__SHIFT` defines the bit offset for a field.
- `REGISTER__FIELD_MASK` defines the already-positioned mask for that field.
- Register comments such as `//AZF0ENDPOINT3_AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL` and address-block comments such as `// addressBlock: azf0endpoint3_endpointind` group macros by hardware block.

Several field names naturally produce macros ending in `MASK_MASK`, such as `AUDIO_ENABLED_INT_STATUS__AUDIO_ENABLED_MASK_MASK`. This is intentional: the field itself is named `AUDIO_ENABLED_MASK`, and the suffix adds the generated mask constant.

## Control Flow

This chunk has no runtime control flow. The implied caller flow is the standard register read/modify/write sequence:

1. Select an endpoint-specific Azalia register address from the matching address header.
2. Read the MMIO or indirect endpoint register.
3. Clear fields with the corresponding `_MASK` constants.
4. Insert values shifted by the matching `__SHIFT` constants.
5. Write the result, or read and decode status fields for interrupts, sink information, format changes, and timing snapshots.

Hardware behavior implied by the field names is order-sensitive outside this header. Examples include enabling unsolicited responses before expecting UR events, programming converter format/channel/stream IDs before enabling audio output, reading or locking LPIB snapshots consistently, clearing or acknowledging format-change responses, and handling audio enabled/disabled/format-changed interrupt flags with their mask/type fields.

## State and Persistence

The header stores no software state. Its constants describe persistent hardware register state for DCE Azalia endpoint widgets. State domains visible in this chunk include:

- Per-endpoint converter configuration: format, channel count, bit depth, sample-rate parameters, stream ID, digital converter flags, category code, keepalive, stripe control, ramp rate, and GTC presentation-time embedding.
- Per-endpoint pin capabilities and runtime pin state: HDMI/DP capability, unsolicited response tag/enable, presence/pin-sense response, widget control, channel speaker allocation, digital-output active status, hot-plug control, wireless-display identity, and remote keepalive.
- Sink and ELD-like metadata: audio descriptors 0-13, sink info 0-8, association info, configuration default, coding type, and HBR/lipsync response fields.
- Multichannel routing state: enable bits and channel IDs across `MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2`.
- IEC 60958 channel-status override state across override registers 0-8.
- Audio transition status: audio enable status plus interrupt flag/mask/type fields for enabled, disabled, and format-changed events.
- Timing/readback state: LPIB snapshot lock, cyclic-buffer wrap count, LPIB value, LPIB timer snapshot, and GTC counter delta/min/max values.

Persistence is in hardware registers, not in the macro file. Values remain until changed by MMIO writes, reset, power transitions, display link reconfiguration, or hardware-generated events.

## Dependencies and Integration Points

The only direct dependency is the C preprocessor. Practically, these macros integrate with:

- Companion DCE 12.0 register address headers that provide the register offsets for the same `AZF0ENDPOINT*` names.
- AMDGPU display-manager and DC code that programs HDMI/DP audio, HDA codec widgets, ELD/sink metadata, and stream routing.
- Interrupt paths that handle audio enabled, disabled, and format-change events.
- Modeset/link-configuration paths that update hot-plug state, sink info, speaker/channel allocation, HBR/lipsync response, and wireless-display or remote-keepalive fields.
- Register helper macros that combine address, mask, and shift definitions for packed field writes.

The repeated endpoint prefixes are an important integration contract. Callers choose a display/audio endpoint by selecting the matching macro family; mixing endpoint numbers would compile but access the wrong per-endpoint bit layout.

## Risks

The primary risk is silent hardware misprogramming. An incorrect shift or mask can corrupt adjacent fields, reserved bits, or per-endpoint state while still compiling cleanly.

The repeated endpoint blocks are vulnerable to copy/generation drift. Endpoint 1-4 should remain structurally identical, and endpoint 5 should continue the same pattern in the following chunk. Any mismatch may indicate either a real hardware difference or a generation error that needs confirmation against the ASIC register source.

Interrupt and status fields are especially easy to misuse. Fields named `*_FLAG`, `*_MASK`, and `*_TYPE` sit in the same register; caller code must avoid treating the mask bit as the generated C mask suffix. Format-change, unsolicited-response, hot-plug, and audio transition fields can create lost events if writes are ordered incorrectly or if status bits require write-one-to-clear semantics documented outside this header.

Full-width masks such as `0xFFFFFFFFL` appear for stream formats, GTC counters, association info, LPIB, and timer snapshots. Callers should use unsigned 32-bit values and avoid signed narrowing. Small packed fields such as 4-bit channel IDs, 6-bit tags, byte-sized sink-info fields, and IEC 60958 nibbles require range validation before packing.

Because this is generated register metadata, manual edits are high risk. Renaming awkward generated symbols, changing `L` suffixed constants, or normalizing repeated blocks by hand can break include users or desynchronize the header from the hardware database.

## Test Signals

Useful validation signals for this chunk are mostly build, static, and hardware integration checks:

- Compile coverage for AMDGPU display/audio code that includes `dce_12_0_sh_mask.h`.
- Static checks that every `__SHIFT` constant in the chunk has the corresponding `_MASK`, and that masks align with their shifts and expected widths.
- Generated-header diffing against the authoritative DCE 12.0 ASIC register specification.
- Endpoint consistency checks comparing the repeated register families for endpoints 1-4 and the continuation of endpoint 5 in the next chunk.
- HDMI/DP audio smoke tests across modesets, stream format changes, multi-channel audio, HBR audio, hot-plug, and sink re-detection.
- Runtime register readback around converter format, stream/channel ID, digital converter enable, pin widget control, speaker allocation, ELD/audio descriptors, sink info, and channel-status override programming.
- Interrupt tests that exercise audio enabled, audio disabled, and audio format changed status/mask/type fields.
- Timing diagnostics that verify LPIB snapshot behavior and GTC counter delta/min/max fields when presentation-time embedding is enabled.

## Cross-Chunk Notes

This chunk continues endpoint 0 from earlier lines and stops mid-endpoint 5. The final per-file research should reconcile adjacent chunks so that endpoint 0 and endpoint 5 are not treated as incomplete hardware blocks. Later chunks should also confirm whether additional endpoint instances follow and whether their generated layouts match the endpoint 1-4 pattern documented here.

### subset-b-001561: lines 59881-62207

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 59881-62207

## Scope

This chunk covers lines 59881-62207 of the generated-style DCE 12.0 shift/mask header. The source is C preprocessor register metadata, not executable driver logic. In this range the header defines 2036 `#define` constants over 274 indexed-register names: 1019 `__SHIFT` definitions and 1017 `_MASK` definitions for AMD Azalia F0 HDMI/DP audio codec endpoints.

The chunk begins in the middle of `AZF0ENDPOINT5` pin-control definitions, then covers complete `azf0endpoint6_endpointind` and `azf0endpoint7_endpointind` output endpoint blocks, complete `azf0inputendpoint0_inputendpointind` through `azf0inputendpoint2_inputendpointind` input endpoint blocks, and the beginning of `azf0inputendpoint3_inputendpointind`.

## Purpose

These macros describe bit positions for DCE 12.0 Azalia codec indexed registers. DCE exposes each audio endpoint through an endpoint index/data register pair in the companion offset header, and this file supplies the field-level masks and shifts for the register payload selected by that index. The hardware represented here is the display audio side of AMDGPU: output converter/pin widgets for HDMI/DisplayPort audio, plus input endpoint widgets for audio capture/status paths.

The exported contract is the standard generated AMD register-field naming pattern:

- `REGISTER__FIELD__SHIFT` gives the low bit of the field.
- `REGISTER__FIELD_MASK` gives the already-positioned field mask.
- Address-block comments such as `azf0endpoint6_endpointind` and `azf0inputendpoint0_inputendpointind` map the macro family to the matching indexed endpoint register namespace in `dce_12_0_offset.h`.

Because the file is consumed by preprocessor-based register helpers, the exact macro names are the API. A rename or numeric change can silently misprogram audio hardware even though the C code still compiles.

## Important Macro Families

The tail of `AZF0ENDPOINT5` contains pin-control fields for an output audio endpoint. It starts with pin sense and widget output enable, then covers speaker/channel allocation, audio descriptors 0-13, multichannel routing, lipsync/HBR capability, sink information, hot-plug and unsolicited response controls, default pin configuration, channel-status overrides, association and output status, LPIB snapshots, coding type, format-changed state, wireless-display identification, remote keepalive, and audio enable/disable/format-change interrupt status.

`AZF0ENDPOINT6` and `AZF0ENDPOINT7` repeat the full output endpoint layout. Their converter register families include:

- audio widget capabilities: channel capability, amplifier/format override capability, striping, processing widget, unsolicited response capability, connection list, digital/power/LR-swap capability, widget delay, and widget type;
- converter format: channel count, bits per sample, sample-base divisor/multiple/rate, and stream type;
- channel/stream ID routing;
- digital converter status/control bits such as `DIGEN`, validity, validity configuration, pre-emphasis, copy, non-audio, professional, level, channel status category code, and keepalive;
- stream format and supported size/rate capability masks;
- stripe control and ramp rate;
- global time counter embedding and counter delta/min/max fields.

The output endpoint pin families for endpoints 6 and 7 include:

- pin audio-widget and pin-capability parameters, including HDMI/DP capability, EAPD, VREF, balanced I/O, trigger requirement, presence-detect and unsolicited-response capability;
- unsolicited response tag/enable and forced response payload/force fields;
- pin sense impedance status and widget output enable;
- channel/speaker allocation fields for HDMI and DP connections, extra connection info, LFE level, level shift, and down-mix inhibit;
- short audio descriptor registers `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, where descriptor 0 also carries stereo-frequency capability;
- two multichannel enable layouts: pair-based `MULTICHANNEL01/23/45/67` fields and odd-channel `MULTICHANNEL1/3/5/7` fields, each with enable, mute, and channel ID subfields;
- `MULTICHANNEL_MODE`, channel-status override registers 0-8, association information, digital output status, LPIB snapshot registers, coding type, format-change tracking, wireless-display identification, remote keepalive, and audio enabled/disabled/format-change interrupt status.

`AZF0INPUTENDPOINT0`, `AZF0INPUTENDPOINT1`, and `AZF0INPUTENDPOINT2` repeat an input endpoint layout. They include input converter widget capability, converter format, channel/stream ID, digital converter bits, stream formats, supported size/rates, input pin widget/capability parameters, unsolicited response control, input pin sense, widget control, two multichannel-enable layouts, HBR response, channel allocation, hot-plug/audio-enable state, forced unsolicited response, default pin configuration, LPIB snapshot registers, input activity/status controls, and an input audio infoframe register.

`AZF0INPUTENDPOINT3` begins at the end of the chunk. Lines 62128-62207 cover its input converter capability, format, channel/stream ID, digital converter, stream formats, supported size/rates, and the start of input pin audio-widget capabilities. The rest of input endpoint 3 continues in the next chunk.

## APIs, Types, and Functions

This chunk defines no functions, structs, enums, or callable APIs. Its interface is entirely preprocessor constants used by AMDGPU's register programming macros. The companion APIs live in the display and GPU driver code that includes `dce_12_0_sh_mask.h`, particularly register helper macros that combine an address, mask, shift, and value into read/modify/write operations.

The adjacent generated headers are part of the same API surface:

- `dce_12_0_offset.h` provides the `mmAZF0ENDPOINT*_..._INDEX`, `mmAZF0ENDPOINT*_..._DATA`, `ixAZF0ENDPOINT*_...`, `mmAZF0INPUTENDPOINT*_..._INDEX`, `mmAZF0INPUTENDPOINT*_..._DATA`, and `ixAZF0INPUTENDPOINT*_...` constants that identify the indexed registers.
- `vega10_enum.h` provides generated enum values for many Azalia fields, such as audio widget capability types and boolean capability values.

## Control Flow

There is no runtime control flow in the header. The practical control flow is imposed by callers and by the indexed-register access model:

1. Select an endpoint instance, such as endpoint 6, endpoint 7, or input endpoint 1.
2. Write the indexed-register selector from `dce_12_0_offset.h`.
3. Read or write the endpoint data register.
4. Use this chunk's `*_MASK` and `*__SHIFT` macros to extract or update fields in the selected data payload.
5. For status or interrupt-style registers, read status fields and write the appropriate ack/clear bits according to hardware semantics.

Several field names imply order-sensitive hardware procedures that are implemented outside this header: enabling digital converters, setting stream/channel IDs and audio formats, advertising sink descriptors, programming multichannel allocation, forcing or enabling unsolicited responses, handling hot-plug/audio enabled state, acknowledging audio enable/disable/format-change interrupts, and snapshotting LPIB/timer state.

## State and Persistence

The header itself stores no state. It describes stateful hardware fields in the DCE Azalia function. Those fields persist in hardware registers until changed by MMIO/indexed-register writes, hardware events, reset, power management, or firmware-side initialization.

Important state domains in this chunk include:

- output converter stream setup: sample format, channel count, bit depth, stream ID, channel ID, digital converter enable, channel status bits, keepalive, striping, ramp rate, and GTC embedding;
- output pin capabilities and sink description: HDMI/DP capability, speaker/channel allocation, audio descriptors, lipsync, HBR capability/enable, manufacturer/product IDs, port IDs, and sink description bytes;
- routing and muting: multichannel enable, mute, channel ID, multichannel mode, association info, and digital output active/mute/status fields;
- event and interrupt state: unsolicited response enable/force payloads, audio enabled/disabled/format-change interrupt status and ack bits, input activity UR enables, and input channel-layout/infoframe change UR enables;
- timing/progress state: LPIB values, LPIB snapshot lock, cyclic buffer wrap count, timer snapshots, GTC counter delta ranges, and remote keepalive state;
- input endpoint state: input activity, channel layout, input audio infoframe channel count/allocation/byte 5/valid bit, input pin sense, HBR, hot-plug audio-enabled state, and input converter stream configuration.

Many fields are single-bit controls or status flags, but several are packed multi-bit values: descriptor bytes, channel allocation, channel IDs, manufacturer/product IDs, port IDs, sink description bytes, LPIB snapshots, GTC counters, unsolicited response payloads, and channel-status override bytes.

## Dependencies and Integration Points

This header has only preprocessor-level dependencies, but its values are coupled to several generated and driver-level pieces:

- The register offsets in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h` must match the endpoint and input-endpoint macro families in this chunk.
- DCE 12.0 display code includes this header from timing-generator, IRQ service, GPIO factory/translation, hardware sequencing, resource, and GMC paths. Direct references to the AZF0 endpoint field names may be sparse because many register accesses are generated through macro concatenation.
- The Linux DRM/AMDGPU audio integration depends on these fields indirectly when display audio is configured for HDMI/DP links, when audio hotplug/ELD-like sink capability information is surfaced, and when DCE reports audio-related interrupts.
- `vega10_enum.h` supplies semantic values for several of the same Azalia field names; this shift/mask header supplies placement, while enum headers supply possible values.
- The endpoint index/data access pattern is an integration constraint: using the right field mask against the wrong endpoint instance or wrong index selector can corrupt a different logical widget.

## Risks

The main risk is silent hardware misprogramming. A bad shift or mask will still compile but can place audio format, channel ID, interrupt ack, or sink-descriptor data in the wrong bits. That can show up as missing HDMI/DP audio, wrong channel mapping, stale sink capabilities, interrupt storms, lost format-change events, or incorrect HBR/multichannel behavior.

The repeated endpoint layouts create copy/generation hazards. `AZF0ENDPOINT6` and `AZF0ENDPOINT7` should be structurally identical output endpoint instances, and `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT2` should be structurally identical input endpoint instances. Any one-off field-width difference should be treated as suspicious unless the hardware spec explains it. The chunk also starts and ends mid-block, so reconciliation with adjacent chunks is required before drawing per-file conclusions about endpoint 5 or input endpoint 3.

The indexed-register model increases the blast radius of mistakes. The data register is generic for an endpoint instance, and the selected index controls which logical register is being accessed. If driver code writes data with masks from one indexed register after selecting another, these macros cannot protect against the error.

Interrupt/status fields need special care. Fields named `*_INT_ACK`, `*_INT_STATUS`, `*_AUDIO_ENABLED`, `*_FORMAT_CHANGED`, `UNSOLICITED_RESPONSE_FORCE`, and input activity/infoframe UR enables may have write-one-to-clear, sticky, or event-generation semantics in hardware. Treating them like ordinary read/write configuration bits can drop events or cause repeated unsolicited responses.

Several full-width or wide masks, such as `0xFFFFFFFFL` for stream formats, port IDs, LPIB snapshots, GTC counter deltas, and wireless display identification, rely on callers using 32-bit unsigned intermediates. Signed or narrower temporaries can truncate payloads or propagate sign bits.

## Test Signals

Useful validation is mostly build, static, and hardware integration coverage:

- compile coverage for all DCE 12.0 translation units that include `dce_12_0_sh_mask.h`;
- generated-header checks that every field has a matching shift/mask pair, masks align with shifts and expected field widths, and output/input endpoint instances remain structurally consistent;
- cross-header checks that every `AZF0ENDPOINT*` and `AZF0INPUTENDPOINT*` field macro has the corresponding indexed register in `dce_12_0_offset.h`;
- HDMI/DP audio smoke tests over endpoints 5-7, including hotplug, stream start/stop, mute/unmute, sample-rate/bit-depth changes, channel-count changes, and HBR-capable modes;
- multichannel audio tests that verify speaker allocation, channel allocation, multichannel enable/mute/channel ID fields, and down-mix inhibit behavior;
- sink-capability tests that read back or validate audio descriptor, manufacturer/product ID, port ID, sink-description, lipsync, and HDMI/DP connection fields after monitor hotplug;
- interrupt tests for audio enabled, disabled, format changed, unsolicited responses, input activity, and input channel-layout/infoframe changes;
- LPIB/GTC/keepalive readback tests around active streams to confirm snapshot locks, wrap counts, timer snapshots, counter deltas, and remote keepalive fields land in expected bits.

## Cross-Chunk Notes

This chunk is chunk 25 of 27 for `dce_12_0_sh_mask.h`. The previous chunk contains the beginning of `AZF0ENDPOINT5`, including earlier converter and pin parameter fields. The next chunk continues `AZF0INPUTENDPOINT3` and then likely completes the remaining input endpoint families and file tail. The final per-file research should merge these chunks into one description of DCE 12.0 display audio register masks, preserving the distinction between direct MMIO register fields and indexed Azalia endpoint fields.

### subset-b-001562: lines 62208-64603

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 62208-64603

Chunk: `subset-b-001562`
Covered source range: lines 62208-64603 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h`

## Purpose

This chunk is a generated AMD DCE 12.0 register field mask header section. It contains no executable driver logic; it publishes C preprocessor constants that encode bit positions and masks for display-controller audio and legacy VGA indexed registers.

The range is dominated by Azalia/HD-audio codec metadata for GPU display audio. It covers the tail of `AZF0INPUTENDPOINT3`, complete input endpoint blocks for `AZF0INPUTENDPOINT4` through `AZF0INPUTENDPOINT7`, the `AZALIA_F2_CODEC` function and pin/input-pin register families, descriptor and sink-info indexed blocks, Azalia CRC result blocks, and the beginning of VGA sequencer/CRT indexed fields.

Each register field is represented by generated macro pairs:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned mask for the field.

The companion address header, `dce_12_0_offset.h`, supplies the `mm*` and `ix*` register offsets. This header supplies the field layout inside those offsets.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or storage objects in this chunk. The macro namespace is the API.

Major covered macro families are:

- `AZF0INPUTENDPOINT3_*`: this chunk begins in the middle of endpoint 3 input-pin audio widget capability definitions, then covers endpoint 3 input-pin capability, unsolicited-response, pin-sense, widget-control, multichannel, HBR, channel-allocation, hot-plug, configuration-default, LPIB, input-status, and infoframe fields.
- `AZF0INPUTENDPOINT4_*` through `AZF0INPUTENDPOINT7_*`: repeated input endpoint blocks for input converter and input pin controls. Converter fields include audio widget capabilities, format fields (`BASE_RATE`, `MULTICHANNEL_TYPE`, `CHANNELS`, `BITS_PER_SAMPLE`, `NUMBER_OF_CHANNELS`), stream/channel IDs, digital converter state (`DIGITAL_ENABLE`, `PROFESSIONAL`, `NONAUDIO`, `COPYRIGHT`, `EMPHASIS`, `CATEGORY_CODE`, `VALIDITY`, `KEEPALIVE_ENABLE`, `DESIRED_SAMPLE_RATE`, `DIGITAL_DEFAULT`), supported formats, and supported sizes/rates. Pin fields include capabilities, unsolicited responses, input pin sense, widget input enable, multichannel enables for channels 0-7, HBR capability/enable, channel allocation, hot-plug audio enable, forced unsolicited responses, default configuration, LPIB snapshots, input activity, channel layout, and incoming infoframe fields.
- `AZALIA_F2_CODEC_ROOT_*` and `AZALIA_F2_CODEC_FUNCTION_*`: root/function-level codec identity, revision, subordinate node count, function power state, subsystem ID response words, converter synchronization, function reset, group type, supported sample sizes/rates, stream formats, and supported power states.
- `AZALIA_F2_CODEC_CONVERTER_*`: output converter format, channel/stream ID, digital converter status/control, stripe control, ramp rate, GTC embedding, converter audio widget capabilities, supported sizes/rates, and stream formats.
- `AZALIA_F2_CODEC_PIN_*`: output pin controls and parameters, including connection-list entry, widget control, unsolicited response, pin sense, configuration default words, speaker allocation, channel allocation, down-mix info, audio descriptor index/data, multichannel enable groups, lip-sync, HBR, sink-info index/data, multichannel mode, codec channel-status override words, pin association info, digital output status, LPIB snapshots, coding type, format-change status, wireless display identification, remote keepalive, pin audio widget capabilities, pin capabilities, and connection-list length.
- `AZALIA_F2_CODEC_INPUT_*`: input converter and input pin counterparts for format, stream ID, digital converter fields, input pin control, pin sense/configuration, channel allocation, per-channel multichannel enables, HBR, LPIB snapshots, input activity/channel layout, input infoframe, channel-status low/high words, and input pin capabilities.
- `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`: packed descriptor slots for maximum channels, sample-rate mask, and stereo/6/8-channel PCM or compressed audio coding flags. These describe EDID/ELD-like audio capability descriptors made visible through the Azalia sink path.
- `AZALIA_F2_CODEC_PIN_CONTROL_*` sink-info fields and `SINK_DESCRIPTION0` through `SINK_DESCRIPTION17`: manufacturer/product ID, sink description length, port IDs, and packed 32-bit sink-description words.
- `AZALIA_INPUT_CRC0_CHANNEL0..7`, `AZALIA_INPUT_CRC1_CHANNEL0..7`, `AZALIA_CRC0_CHANNEL0..7`, and `AZALIA_CRC1_CHANNEL0..7`: full-width 32-bit CRC result fields for input and general Azalia CRC result indexed blocks.
- `SEQ00` through `SEQ04`: legacy VGA sequencer fields, including sequencer reset bits, 8-dot/shift/pixel-clock controls, plane map enables, font select bits, 256K, odd/even, and chain mode.
- `CRT00` through `CRT11`: the beginning of legacy VGA CRT controller fields, including horizontal timing, vertical timing extension bits, row scan/byte pan, cursor start/end/location, display start, vertical sync start/end, vertical interrupt clear/enable, refresh-cycle select, and write-protect behavior.

The range starts after earlier endpoint 3 converter definitions and ends at `CRT11`; `CRT12` and later CRT fields continue in the next chunk.

## Control Flow

This file has no runtime control flow. It is a sequence of `#define` directives inside the larger generated include guard.

Runtime control flow appears in consumers that:

1. choose a register address from `dce_12_0_offset.h`, such as an `ixAZF0INPUTENDPOINT4_*`, `ixAZALIA_F2_CODEC_*`, `ixAUDIO_DESCRIPTOR*`, `ixSINK_DESCRIPTION*`, `ixAZALIA_CRC*`, `ixSEQ*`, or `ixCRT*` offset;
2. access the correct direct or indexed register window for that DCE/Azalia/VGA block;
3. extract fields with `(value & FIELD_MASK) >> FIELD__SHIFT`, or clear and insert fields with the same pair;
4. write the result back only when the hardware register is writable and the caller follows the required audio/display sequencing.

The generated constants do not enforce any codec verb ordering, stream enable sequencing, hot-plug ordering, LPIB snapshot locking, CRC-latch behavior, or legacy VGA timing restrictions. Those requirements live in display/audio driver code and in the DCE hardware programming guide.

## State And Persistence Behavior

The header itself has no mutable software state and persists only as compiled constants.

The fields describe hardware state in the DCE 12.0 display audio and VGA blocks. State represented by this chunk includes:

- converter and pin widget capability values reported to the HDA/Azalia codec model;
- stream format, channel count, channel ID, stream ID, and digital converter status/control bits;
- input and output pin capabilities, jack/presence sense, unsolicited response enable/tag state, and forced unsolicited response payloads;
- hot-plug audio enable and clock-gating control bits;
- high-bit-rate audio enable/capability and HDMI/DisplayPort channel allocation state;
- LPIB and timer snapshots plus cyclic buffer wrap count state;
- input activity, channel layout, infoframe validity, and channel-status words;
- sink capability data, audio descriptors, port IDs, and sink description words;
- CRC result snapshots for Azalia output/input paths;
- legacy VGA sequencer and CRT timing/cursor/display-start register state.

Persistence depends on the register class. Some fields are read-only capability or status reports, some are writable controls, some are sticky or latched diagnostic values, and some reflect firmware, BIOS, connector, EDID/ELD, or hardware strap-derived state. Values can be reset or reinitialized by display mode set, audio stream setup/teardown, HPD handling, runtime power management, suspend/resume, GPU reset, display core reset, or full device power loss.

## Dependencies And Integration Points

The direct dependency is the matching generated DCE 12.0 offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h`

That file defines the direct endpoint index/data registers, such as `mmAZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX` and `mmAZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_ENDPOINT_DATA`, and the indexed offsets used with this chunk, such as `ixAZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`, `ixAZALIA_F2_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR`, `ixAUDIO_DESCRIPTOR0`, `ixSINK_DESCRIPTION0`, `ixAZALIA_CRC0_CHANNEL0`, `ixSEQ00`, and `ixCRT00`.

Known local include points for `dce_12_0_sh_mask.h` include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_translate_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_factory_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c`

The broader integration path is AMDGPU Display Core on DCE 12.0 ASICs. Display audio setup, hot-plug handling, stream formatting, infoframe generation, sink capability exposure, and diagnostic CRC readback all depend on the register layout matching the ASIC. Legacy VGA sequencer/CRT fields integrate with early display/VGA compatibility paths and mode/timing programming.

Although the repository path is under `ceph-client`, this chunk is AMDGPU kernel driver register metadata. It has no distributed filesystem protocol behavior and no Ceph persistence semantics.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. Bad masks or shifts compile cleanly but can read the wrong bit, fail to update the target field, or corrupt neighboring fields in packed registers.

This chunk is highly repetitive. Endpoint 4 through endpoint 7 share nearly identical register shapes, and many multichannel fields repeat for channels 0-7. A generation or copy error can put a correct-looking field under the wrong endpoint, channel, or register prefix. Such errors may only appear when a specific input endpoint or channel layout is exercised.

Audio control fields are sequencing-sensitive. Misusing stream format, channel/stream ID, digital converter, HBR enable, channel allocation, hot-plug audio enable, or widget input-enable fields can produce missing audio, wrong channel mapping, incorrect sample size/rate reporting, or broken HDMI/DisplayPort HBR audio behavior.

Presence, unsolicited response, and force-response fields affect event delivery. Incorrect masks can suppress hot-plug or pin-sense notifications, generate spurious responses, or cause the audio stack to believe a sink has changed when it has not.

LPIB and timer snapshot fields are diagnostic/timing-sensitive. Callers must respect the snapshot lock and wrap-count semantics when correlating audio buffer position with display/audio timing; the mask header does not encode that protocol.

Sink-info and audio-descriptor fields are externally visible to audio policy. Incorrect descriptor bits can advertise unsupported codecs, sample rates, channel counts, or sink identity values, leading to bad userspace audio choices or failed link validation.

CRC fields are full-width values. They should be treated as diagnostic readback values, not as bitfield controls, even though they follow the same generated mask/shift naming pattern.

Legacy VGA sequencer and CRT fields are narrow 8-bit-style indexed registers embedded in a 32-bit macro namespace. Using 32-bit assumptions without respecting VGA indexed-register access and timing semantics can corrupt display-start, cursor, blanking, or sync behavior. The chunk ends before the rest of the CRT register family, so file-level analysis must merge the following chunk before validating complete VGA CRT coverage.

## Test Signals

Useful validation signals include:

- kernel build coverage for DCE 12.0/Vega display paths that include `dce_12_0_sh_mask.h`;
- generated-header consistency checks that every `*_MASK` has a matching `__SHIFT` across the complete file, with this chunk's first and last line-boundary splits resolved during file-level merge;
- comparison against the authoritative DCE 12.0 register database and the adjacent `dce_12_0_offset.h` register names;
- static checks that endpoint-specific masks are used with the matching endpoint offsets and index/data windows;
- HDMI and DisplayPort audio bring-up tests across stereo, multichannel, compressed formats, HBR, sample-rate changes, and stream enable/disable cycles;
- hot-plug and pin-sense tests that verify unsolicited response tags/enables, presence-detect state, sink re-enumeration, and audio enable state;
- EDID/ELD or sink-capability inspection tests that confirm audio descriptors, speaker allocation, manufacturer/product IDs, port IDs, and sink descriptions are decoded as expected;
- LPIB snapshot and audio position tests that compare reported buffer position/timer snapshots with playback progress under wraparound;
- CRC diagnostic tests that read `AZALIA_INPUT_CRC*` and `AZALIA_CRC*` channels under known audio/display traffic;
- legacy VGA smoke tests for early console, mode set, cursor, blanking, and suspend/resume paths on DCE 12.0 hardware or emulation.

Regression symptoms from bad constants include missing HDMI/DP audio devices, wrong channel layout, HBR audio failure, spurious or missing audio hot-plug events, incorrect sink capability reporting, unstable playback position reporting, CRC diagnostics changing on the wrong channel, or broken VGA compatibility display behavior.

## Cross-Chunk Notes

This chunk starts inside `AZF0INPUTENDPOINT3_AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`; earlier endpoint 3 converter and the start of that pin capability block are in the previous chunk. It ends at `CRT11`; `CRT12` and the rest of the VGA CRT indexed register block continue in the next chunk. The final per-file research document should treat these boundaries as chunking artifacts, not as source-level omissions.

### subset-b-001563: lines 64604-64798

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 64604-64798

## Scope

This chunk covers the final 195 lines of the DCE 12.0 generated register shift/mask header. It begins in the middle of the legacy VGA CRT controller indexed-register definitions, continues through the VGA graphics-controller and attribute-controller indexed-register blocks, and ends the file with the closing `#endif` for `_dce_12_0_SH_MASK_HEADER`.

The source contains no C functions, structs, enums, or executable logic. Its exported surface is a set of C preprocessor constants named as `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`. These constants are consumed by AMDGPU display code together with companion DCE 12.0 register offset definitions and register read/modify/write helpers.

## Purpose

The chunk describes bit layouts for the legacy VGA indexed register space preserved inside AMD display hardware:

- `CRT11` through `CRT22` fields for CRT controller vertical timing, display pitch, address counting, sync enable, line compare, graphics decode readback, and latch data.
- `vgagrphind` block entries `GRA00` through `GRA08` for VGA graphics-controller set/reset, compare, rotate/function select, read map, write/read mode, odd/even addressing, graphics/address-select mode, compare don't-care, and bit mask.
- `vgaattrind` block entries `ATTR00` through `ATTR14` for attribute palette entries, attribute mode control, overscan, plane enable/source mux, pixel pan, and color-select extension bits.

These are compatibility definitions for byte-sized VGA index/data registers, not high-level display-pipe controls. Their masks are mostly `0xFFL`, sub-byte nibbles, or single-bit values because the registers are the classic VGA CRTC/graphics/attribute indexed registers represented through DCE's generated ASIC register database.

## Important Macro Families

The CRT controller tail includes:

- `CRT11__V_SYNC_END`, `CRT11__V_INTR_CLR`, `CRT11__V_INTR_EN`, `CRT11__SEL5_REFRESH_CYC`, and `CRT11__C0T7_WR_ONLY` masks. This chunk starts at the last two `CRT11` masks, so the associated shifts are in the immediately preceding chunk.
- `CRT12__V_DISP_END`, `CRT15__V_BLANK_START`, `CRT16__V_BLANK_END`, and `CRT18__LINE_CMP`, each with full byte-width `0xFFL` masks.
- `CRT13__DISP_PITCH`, also byte-width, for the legacy display pitch field.
- `CRT14__UNDRLN_LOC`, `CRT14__ADDR_CNT_BY4`, and `CRT14__DOUBLE_WORD`, splitting underline location and addressing mode bits.
- `CRT17__RA0_AS_A13B`, `RA1_AS_A14B`, `VCOUNT_BY2`, `ADDR_CNT_BY2`, `WRAP_A15TOA0`, `BYTE_MODE`, and `CRTC_SYNC_EN`, which encode classic VGA CRTC addressing/sync behavior.
- `CRT1E__GRPH_DEC_RD1`, `CRT1F__GRPH_DEC_RD0`, and `CRT22__GRPH_LATCH_DATA` readback/latch fields.

The `vgagrphind` block defines graphics-controller fields:

- `GRA00__GRPH_SET_RESET0` through `GRPH_SET_RESET3` and `GRA01__GRPH_SET_RESET_ENA0` through `ENA3` for per-plane set/reset values and enables.
- `GRA02__GRPH_CCOMP` and `GRA07__GRPH_XCARE0` through `XCARE3` for color compare and compare don't-care masks.
- `GRA03__GRPH_ROTATE` and `GRA03__GRPH_FN_SEL` for rotate count and raster-operation/function select.
- `GRA04__GRPH_RMAP` for read-map plane selection.
- `GRA05__GRPH_WRITE_MODE`, `GRPH_READ1`, `CGA_ODDEVEN`, `GRPH_OES`, and `GRPH_PACK` for VGA read/write mode and packed/odd-even access behavior.
- `GRA06__GRPH_GRAPHICS`, `GRPH_ODDEVEN`, and `GRPH_ADRSEL` for graphics/text mode, odd/even addressing, and aperture/address select.
- `GRA08__GRPH_BMSK` as an 8-bit bit-mask register.

The `vgaattrind` block defines attribute-controller fields:

- `ATTR00` through `ATTR0F` all expose `ATTR_PAL` at shift `0x0` with mask `0x3FL`, representing the 16 internal 6-bit VGA attribute palette entries.
- `ATTR10` splits attribute mode control into graphics mode, mono enable, line graphics enable, blink enable, pan/top-only behavior, pixel-clock divide-by-two, and color-select enable bits.
- `ATTR11__ATTR_OVSC` is the 8-bit overscan/border color field.
- `ATTR12__ATTR_MAP_EN` and `ATTR12__ATTR_VSMUX` cover plane/map enable and video-status mux bits.
- `ATTR13__ATTR_PPAN` gives the 4-bit pixel-panning field.
- `ATTR14__ATTR_CSEL1` and `ATTR14__ATTR_CSEL2` provide the low and high color-select extension fields.

## APIs, Types, and Functions

There are no callable APIs, C data types, or functions in this chunk. The macros are the API contract:

- `*_SHIFT` values give the bit offset of a field inside the indexed register value.
- `*_MASK` values give the already-positioned bit mask to clear, test, or combine with shifted values.
- The address-block comments, especially `vgagrphind` and `vgaattrind`, identify which generated register-index namespace the following byte-register fields belong to.

The file-level include guard closes at line 64798. Because this chunk terminates the header, any generation or merge error here can affect every translation unit that includes `dce_12_0_sh_mask.h`.

## Control Flow

This chunk has no intrinsic runtime control flow. The operational flow exists in the AMDGPU display/VGA access paths that use these masks:

1. Select a legacy VGA indexed register through the relevant CRTC, graphics-controller, or attribute-controller index path.
2. Read or prepare the byte-sized data value.
3. Use the matching `*_MASK` and `*_SHIFT` constants to isolate or update a field.
4. Write the value back through the VGA indexed data path, or interpret readback status/latch fields.

The macros also describe order-sensitive hardware behavior indirectly. For example, vertical interrupt bits in `CRT11`, CRTC sync enable in `CRT17`, graphics write/read mode in `GRA05`, and attribute palette/index behavior in `ATTR00`-`ATTR14` are meaningful only when the caller follows the VGA register access sequence and any display-mode ownership rules already enforced by the surrounding driver.

## State and Persistence

The header stores no software state. It describes persistent hardware register state in the legacy VGA compatibility block. State represented here includes:

- CRTC vertical timing, blanking, sync-ending, pitch, line-compare, addressing, and sync-enable state.
- VGA graphics-controller per-plane set/reset, compare, read/write mode, map selection, addressing mode, and bit-mask state.
- Attribute-controller palette, mode-control, overscan, plane-enable, pixel-panning, and color-select state.

These values persist in hardware until changed by MMIO/indexed-register writes, reset, VGA disable/ownership transitions, power-management transitions, or firmware/hardware initialization. The interrupt-clear style field `CRT11__V_INTR_CLR_MASK` is especially stateful: caller code must know whether the hardware expects a write-one-to-clear or other legacy VGA clear sequence; this header only supplies the bit position.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor and the rest of the same generated header. It integrates with:

- `dce_12_0_offset.h`, which is the companion DCE 12.0 offset header in this tree.
- AMDGPU/DCE 12.0 display sources that include `dce/dce_12_0_sh_mask.h`, including DCE 12.0 timing-generator, hardware-sequencer, IRQ, GPIO, resource, and GMC code.
- Shared AMD display register helper patterns that combine `REG`/address macros with `*_MASK` and `*_SHIFT` constants.
- Legacy VGA routing/control code in the display stack that still needs VGA CRTC, graphics, and attribute indexed-register compatibility even when the normal display path is driven by modern DCE blocks.

The same macro families are repeated in earlier DCE and later DCN generated mask headers, which is a useful integration signal: these fields are stable legacy VGA definitions carried across ASIC generations.

## Risks

The main risk is silent hardware misprogramming. These are small, densely packed legacy fields, so a wrong shift or mask can alter adjacent VGA timing, address, palette, or mode bits without compiler diagnostics.

Chunk-boundary risk is present because this slice begins at `CRT11` masks while the matching `CRT11` shifts are immediately before line 64604. The merge lane should reconcile the preceding chunk so `CRT11__SEL5_REFRESH_CYC_MASK` and `CRT11__C0T7_WR_ONLY_MASK` are documented with their matching shifts.

Legacy VGA register semantics are easy to misuse from modern display code. Attribute-controller registers require the correct index/data access sequence, palette entries are only 6-bit despite living in byte registers, and CRTC/graphics-controller addressing bits interact with memory aperture and text/graphics mode behavior. Treating these constants like ordinary 32-bit DCE pipe registers can produce invalid accesses or stale state.

Interrupt and sync fields have display-visible failure modes. Misprogramming `CRT11__V_INTR_CLR`, `CRT11__V_INTR_EN`, or `CRT17__CRTC_SYNC_EN` can lose vertical interrupt state, leave unexpected interrupts enabled, or affect legacy sync generation. Palette and blink/pixel-pan fields can cause visible color, cursor/blink, or alignment artifacts in VGA compatibility modes.

Because this chunk closes the include guard, truncation after these definitions or a malformed guard terminator would break all users of the header at compile time. Conversely, duplicated or renamed macros would compile only until a user includes conflicting generated headers in the same scope.

## Test Signals

Useful validation signals include:

- Basic build coverage for all translation units that include `dce_12_0_sh_mask.h`.
- Static generated-header checks that every field has both a `__SHIFT` and `_MASK`, that masks align with shifts, and that this file has a single intact `_dce_12_0_SH_MASK_HEADER` guard ending at line 64798.
- Diff checks against AMD's authoritative DCE 12.0 register-generation source and against nearby DCE/DCN generations for these stable VGA fields.
- VGA compatibility smoke tests that exercise mode set/disable paths, VGA memory aperture handling, palette writes, pixel panning, blink/line-graphics behavior, and text/graphics mode transitions.
- Interrupt/readback tests around `CRT11` vertical interrupt clear/enable and CRTC status readback where hardware access is available.
- Visual or register-readback checks after programming `GRA05`, `GRA06`, `ATTR10`, `ATTR12`, and `ATTR14`, because those fields affect memory interpretation and displayed color/mode behavior.

## Cross-Chunk Notes

This is the terminating chunk of a 64,798-line generated header. The final per-file report should merge it with earlier chunks for the full VGA section: the beginning of `CRT11` appears before this slice, and earlier portions of the file cover the modern DCE display, clocking, writeback, interrupt, DCP, and other register blocks. This chunk should be treated as the final legacy VGA indexed-register tail plus the include-guard terminator, not as a standalone hardware module.
