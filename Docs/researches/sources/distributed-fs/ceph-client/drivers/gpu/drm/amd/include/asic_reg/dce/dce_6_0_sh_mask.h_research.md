# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_6_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001565`: lines 1-3622, `Docs/researches/chunks/subset-b-001565_research.md`
- `subset-b-001566`: lines 3623-7461, `Docs/researches/chunks/subset-b-001566_research.md`
- `subset-b-001567`: lines 7462-9948, `Docs/researches/chunks/subset-b-001567_research.md`

## Chunk Research

### subset-b-001565: lines 1-3622

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_6_0_sh_mask.h lines 1-3622

## Scope

This chunk covers the first 3,622 lines of the AMD DCE 6.0 generated register shift/mask header. It starts with the copyright and `DCE_6_0_SH_MASK_H` include guard, then defines C preprocessor constants for many early DCE 6.0 display-engine register fields. The file continues beyond this chunk through lines 3623-9948, so this document covers only chunk 1 of 3 for the source file.

The source contains no C functions, structs, enums, executable statements, or persisted software data. Its exported surface is generated macros named as `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`. Each pair describes an already-positioned 32-bit register mask and the bit offset for one hardware field.

## Purpose

The header lets AMDGPU DCE 6.0 code program and decode display controller registers without hand-written bit arithmetic. This chunk covers several major hardware surfaces:

- AFMT HDMI/DP audio packet formatting, IEC 60958 channel status, AVI/MPEG/generic/ISRC infoframes, audio CRC/debug/test-ramp controls, and AFMT status.
- Legacy VGA attribute, CRTC, and pipe-specific VGA control fields.
- DisplayPort AUX arbitration, software/native link-service transactions, DPHY transmit/receive timing, interrupts, HPD disconnect reporting, and AUX pad impedance calibration.
- Azalia/HD-audio DMA, codec function, converter, pin, sink, multichannel, HBR/lipsync, channel-status override, FIFO, latency, and debug registers.
- Backlight/PWM and ABM1 content-adaptive brightness registers, including ambient light, current/target/user/final duty levels, histogram/luma-sum controls, thresholds, and double-buffer/update locks.
- Analog DAC and BPHY DAC controls for autodetect, comparators, clocks, CRC, powerdown, force output, source select, FIFO status, and sync tristate.
- CRTC timing, blanking, sync, frame/snapshot/status, interrupts, stereo/3D, trigger, vtotal, cursor, and pixel-rate controls.
- DCCG clock/audio DTO/GTC/perf/debug controls, DCFE resets and memory light-sleep controls, and DC GPIO/DDC/DVO/generic/genlock pads up to the chunk boundary.

## Important Macro Families

The chunk begins with debug and audio-formatting fields:

- `ABM_TEST_DEBUG_DATA` and `ABM_TEST_DEBUG_INDEX` expose ABM test debug data/index/write-enable fields.
- `AFMT_60958_0`, `_1`, and `_2` define IEC 60958 channel-status bits: mode, source/channel numbers, category code, sampling/original sampling frequency, clock accuracy, word length, validity flags, and channels 2-7.
- `AFMT_AUDIO_PACKET_CONTROL` and `AFMT_AUDIO_PACKET_CONTROL2` control audio sample send, FIFO reset/overflow acknowledge, test mode, channel swap, channel enable, DP audio stream ID, layout override/select, HBR override, and Azalia audio-enable-change acknowledge.
- `AFMT_AUDIO_INFO0/1`, `AFMT_AVI_INFO0-3`, `AFMT_MPEG_INFO0/1`, `AFMT_GENERIC_HDR`, `AFMT_GENERIC_0-7`, and `AFMT_ISRC1/2_*` describe HDMI-style infoframe payload/header bytes and update controls.
- `AFMT_AUDIO_CRC_CONTROL/RESULT`, `AFMT_AUDIO_DBG_DTO_CNTL`, `AFMT_RAMP_CONTROL0-3`, `AFMT_STATUS`, and `AFMT_VBI_PACKET_CONTROL` provide test, CRC, DTO debug, ramp, status, and generic-packet update fields.

Legacy indexed VGA compatibility fields appear early and again later:

- `ATTR00` through `ATTR14`, `ATTRDR`, `ATTRDW`, and `ATTRX` describe VGA attribute palette, mode, overscan, map-enable, pixel-pan, color-select, data, index, and palette read/write enable bits.
- `CRT00` through `CRT22` cover classic CRT controller timing, blanking, sync, cursor, address, vertical interrupt, pitch, underline, count/address mode, line compare, graphics decode readback, and latch data.
- `D1VGA_CONTROL` through `D6VGA_CONTROL` select per-display VGA mode enable, timing source, sync polarity, overscan color, and rotation.

DisplayPort AUX and GPIO-related AUX fields are another large group:

- `AUX_ARB_CONTROL` coordinates software and DMCU ownership of the AUX register interface, including pending/use/done bits and queued transaction gating.
- `AUX_CONTROL` configures AUX enable, HPD selection, HPD disconnect handling, light-service read/update behavior, mode detection, impedance-calibration request, deglitch, and test mode.
- `AUX_DPHY_RX_CONTROL0/1`, `AUX_DPHY_RX_STATUS`, `AUX_DPHY_TX_CONTROL`, `AUX_DPHY_TX_REF_CONTROL`, and `AUX_DPHY_TX_STATUS` define timing windows, thresholds, transition filtering, precharge, reference divider/rate, active state, and half-symbol period readback.
- `AUX_SW_CONTROL`, `AUX_SW_DATA`, and `AUX_SW_STATUS` are the software AUX transaction interface: go bit, byte count, start delay, data/index/RW/autoincrement fields, done/request bits, arbitration status, reply count, HPD disconnect, non-AUX mode, timeout state, and RX error flags.
- `AUX_LS_DATA` and `AUX_LS_STATUS` mirror link-service transaction data and status/error reporting.
- `AUX_INTERRUPT_CONTROL`, `AUX_GTC_SYNC_CONTROL`, `AUXN_IMPCAL`, and `AUXP_IMPCAL` define interrupt ack/mask/status, GTC sync enable, and positive/negative AUX pad impedance calibration controls.

Azalia/HD-audio definitions dominate the middle of this chunk:

- `AZALIA_*_DMA_CONTROL`, `AZALIA_DATA_DMA_CONTROL`, `AZALIA_RIRB_AND_DP_CONTROL`, and `AZALIA_BDL_DMA_CONTROL` describe non-snoop and isochronous DMA behavior, underflow handling, and interrupt-on-completion generation.
- `AZALIA_AUDIO_DTO`, `AZALIA_AUDIO_DTO_CONTROL`, `AZALIA_SCLK_CONTROL`, `AZALIA_CYCLIC_BUFFER_SYNC`, FIFO-size, latency-count, request-count, and underflow filler sample fields describe audio clocking, DMA synchronization, latency instrumentation, and underflow behavior.
- `AZALIA_F0_CODEC_*` macros expose HD-audio function 0 root/function/converter/pin parameters, stream formats, power states, resets, endpoint indirect index/data, codec debug, converter channel/stream IDs, converter format, digital-converter flags, stripe control, GTC embedding, ramp rate, and widget capabilities.
- `AZALIA_F0_CODEC_PIN_CONTROL_*` covers ELD/audio descriptors 0-13, channel/speaker allocation, multichannel enable/mode, hot-plug/audio enabled, configuration defaults, HBR, lipsync, pin sense, sink info, unsolicited response, and widget output enable.
- `AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_0-8` and corresponding `AZALIA_F2_PIN_CONTROL_CODEC_CS_OVERRIDE_0-8` define IEC 60958 channel-status override fields for source/channel numbers, clock accuracy, word length, sampling/original frequency, CGMS-A, MPEG surround, coefficients, and per-channel numbering.
- `AZALIA_F2_CODEC_*` repeats a smaller function/pin-control view for function 2, including audio descriptors, sink info index/data, manufacturer/product IDs, port IDs, multichannel fields, default configuration, pin sense/presence, speaker allocation, unsolicited response, and widget capabilities.

Backlight, ABM, analog, and color-transform controls are visible around the transition into display-pipe state:

- `BL_PWM_*` and `BL1_PWM_*` describe PWM enable, period, fractional mode, frame-update locks, ABM-derived/user/ambient/current/target/final duty values, minimum duty, and update sample-rate controls.
- `DC_ABM1_*` covers ABM enable/source select, master lock, ACE thresholds and offset/slope tables, histogram bin controls/results, luma-sum/min/max/counts, overscan pixel value/binning, sample rates, read-progress/missed-frame flags, and HGLS/ACE register update locks.
- `BPHYC_DAC_*` provides DAC auto-calibration and analog macro fields.
- `DAC_*` covers analog-output autodetect, comparator controls/output, clock enables, DAC enable/resync FIFO state, CRC generation and signatures, force output data, indexed DAC data/mask/read/write indices, powerdown, source select, stereo sync, and sync tristate.
- `COMM_MATRIXA_TRANS_*` and `COMM_MATRIXB_TRANS_*` define 3x4 color-space/communication matrix coefficient fields packed two 16-bit coefficients per register.

CRTC and cursor fields form the largest display-timing section in this chunk:

- `CRTC0_PIXEL_RATE_CNTL` through `CRTC5_PIXEL_RATE_CNTL` select pixel-rate sources, enable DP DTOs, and expose add/drop pixel and dispout FIFO/error counts per CRTC.
- `CRTC_CONTROL`, `CRTC_MASTER_EN`, `CRTC_COUNT_CONTROL`, `CRTC_DOUBLE_BUFFER_CONTROL`, `CRTC_UPDATE_LOCK`, and `CRTC_DCFE_CLOCK_CONTROL` describe enable/update/clock-gate behavior.
- `CRTC_H_TOTAL`, `CRTC_H_BLANK_START_END`, `CRTC_H_SYNC_A/B`, `CRTC_V_TOTAL`, `CRTC_V_TOTAL_MIN/MAX`, `CRTC_V_BLANK_START_END`, and `CRTC_V_SYNC_A/B` define timing totals, blank windows, sync ranges, and vtotal min/max controls.
- `CRTC_STATUS*`, `CRTC_SNAPSHOT_*`, `CRTC_COUNT_RESET`, `CRTC_FORCE_COUNT_NOW_CNTL`, `CRTC_MANUAL_FORCE_VSYNC_NEXT_LINE`, and `CRTC_VERT_SYNC_CONTROL` provide live scanout/frame counts, snapshot controls, force/reset events, and vblank/vsync state.
- `CRTC_INTERRUPT_CONTROL`, `CRTC_VSYNC_NOM_INT_STATUS`, `CRTC_V_UPDATE_INT_STATUS`, and `CRTC_V_TOTAL_INT_STATUS` describe interrupt mask/type/clear/status fields.
- `CRTC_3D_STRUCTURE_CONTROL`, `CRTC_STEREO_*`, `CRTC_GSL_*`, `CRTC_TRIGA/B_*`, `CRTC_TEST_PATTERN_*`, and `CRTC_MVP_*` cover stereo/3D, genlock/swaplock timing windows, external/manual triggers, test pattern generation, and multi-view/flip events.
- `CUR_*` macros expose cursor color, enable/mode, hot spot, position, size, surface address/high, request filtering, update lock/pending/taken, and urgent behavior.

The chunk ends in display clock, front-end, and GPIO definitions:

- `DCCG_AUDIO_DTO0/1_*`, `DCCG_AUDIO_DTO_SOURCE`, `DCCG_GATE_DISABLE_CNTL`, `DCCG_GTC_*`, `DCCG_PERFMON_CNTL`, `DCCG_SOFT_RESET`, `DCCG_TEST_*`, and `DCCG_VPCLK_CNTL` describe display/audio clock generation, clock gating, global time counter, perf monitoring, test clocks, and light-sleep/memory-shutdown controls across DMCU, DMIF, FBC, MCIF, VGA, VIP, and Azalia domains.
- `DCDEBUG_*`, `DC_DMCU_SCRATCH`, and `DC_DVODATA_CONFIG` expose debug-bus selection/output/pin override, DMCU scratch storage, and DVO/VIP data mapping.
- `DCFE0_SOFT_RESET` through `DCFE5_SOFT_RESET`, `DCFE_DBG_SEL`, and `DCFE_MEM_LIGHT_SLEEP_CNTL` define per-pipe soft resets and memory/light-sleep controls for DCP, scaler, CRTC, cursor/LUT/line-buffer/regamma memories, and overlay/scaler blocks.
- `DC_GENERICA`, `DC_GENERICB`, and `DC_GPIO_*` define generic clock selections plus DDC1-DDC6, DDCVGA, DVO data, generic GPIO, and genlock/swaplock pad A/enable/mask/Y fields. The chunk stops in `DC_GPIO_GENLK_MASK`, so that register family continues in the next chunk.

## APIs, Types, and Functions

There are no callable APIs, C data types, or functions in this chunk. The macros themselves are the API contract:

- `*_MASK` constants are already shifted into their register bit positions and are suitable for clearing or testing fields.
- `*__SHIFT` constants are field offsets used when packing or unpacking values.
- Full-width fields use masks such as `0xffffffffL`; byte/nibble/single-bit fields use narrower masks with the same naming convention.
- Several names naturally produce `MASK_MASK`, for example `AUX_INTERRUPT_CONTROL__AUX_SW_DONE_MASK_MASK` or `DAC_CRC_SIG_CONTROL_MASK__DAC_CRC_SIG_CONTROL_MASK_MASK`, because the hardware field name itself includes `MASK`.

These constants are intended to be paired with companion address macros from `dce_6_0_d.h` and register helper code such as `set_reg_field_value`, `dm_read_reg`, `dm_write_reg`, `RREG32`, and `WREG32`.

## Control Flow

This chunk has no intrinsic runtime control flow. The implied operational flow in consumers is the standard register read/modify/write sequence:

1. Select the DCE 6.0 register address from the companion address header, sometimes adding a pipe or block offset.
2. Read the current 32-bit MMIO or indirect-register value, unless programming a full-width register.
3. Clear field bits with `*_MASK`.
4. Insert a validated value shifted by `*__SHIFT`.
5. Write the new value back, or decode status bits after a hardware event.

Some register groups imply hardware sequencing that is not encoded in this header. AUX transactions require ownership/arbitration, data/index setup, `AUX_SW_GO`, polling or interrupt handling, and error/reply decoding. Azalia programming requires converter format/channel/stream setup, pin/sink metadata updates, and event handling around hot-plug or audio-format changes. CRTC and cursor updates often require update locks, double-buffer pending/taken checks, or vblank-safe writes. ABM and PWM fields include master/update locks and frame-start update controls. Interrupt fields require the caller to know the clear/ack semantics from hardware documentation or existing driver code.

## State and Persistence

The header stores no state. It describes hardware state that persists in DCE 6.0 registers until changed by MMIO/indirect writes, reset, display modeset, power-management transition, firmware initialization, or hardware-generated events.

State domains represented in this chunk include:

- Audio packet, channel-status, infoframe, CRC/test, and Azalia codec/DMA/pin/sink state.
- AUX controller transaction queues, arbitration ownership, HPD disconnect, RX/TX status, DPHY timing, and pad calibration state.
- Legacy VGA attribute/CRTC state and per-pipe VGA routing.
- CRTC timing, vblank/vsync state, frame counters, snapshots, interrupts, trigger state, stereo/3D state, GSL timing, and test-pattern configuration.
- Cursor surface address/high bits, position, size, color, mode, urgent, and update state.
- Backlight PWM/ABM current, target, ambient, user, final duty cycle, histogram/luma accumulation, thresholds, and update locks.
- Analog DAC autodetect, comparator, power, force-output, source, CRC, and FIFO calibration state.
- Display clock gating, DTO/GTC, DCFE soft reset and memory light-sleep state.
- GPIO/DDC/DVO/generic/genlock pad output, enable, mask, receive, pull-down, polarity, and strength state.

Several state fields are event-like or write-sensitive, including `*_ACK`, `*_CLEAR`, `*_OCCURRED`, `*_PENDING`, `*_DONE`, and interrupt mask/type bits. The generated masks identify bit positions only; they do not specify whether a bit is sticky, write-one-to-clear, read-only, double-buffered, or self-clearing.

## Dependencies and Integration Points

Direct dependency is only the C preprocessor. Practical integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_6_0_d.h`, the companion DCE 6.0 address/offset header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce60/dce60_timing_generator.c`, which includes `dce/dce_6_0_sh_mask.h` and uses CRTC masks such as `CRTC_H_TOTAL__CRTC_H_TOTAL_MASK` and `CRTC_V_TOTAL__CRTC_V_TOTAL_MASK` when defining timing-generator limits.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/si_dpm.c`, which includes the DCE 6.0 address and mask headers for Southern Islands display/power-management register access.
- Shared display register helper patterns that combine address macros, pipe offsets, and mask/shift macros for read/modify/write operations.
- Sibling generated ASIC headers such as `dce_10_0_sh_mask.h`, `dce_11_2_sh_mask.h`, `dce_12_0_sh_mask.h`, and later DCN mask headers, which repeat many macro families with generation-specific additions or prefixes.

This header is ASIC-generation-specific. Code must include the matching DCE 6.0 address and mask headers together; mixing masks from another generation may compile but program the wrong field layout.

## Risks

The primary risk is silent hardware misprogramming. These macros are compile-time constants, so a wrong mask/shift, wrong generation include, or wrong register address can corrupt adjacent hardware fields without type or runtime checking.

Generated-name awkwardness is a real maintenance risk. Fields whose hardware name includes `MASK` produce identifiers ending in `MASK_MASK`; normalizing those names manually would break consumers or desynchronize the file from the register database. Full-width masks use `L` suffixes and should be treated as unsigned 32-bit register masks by callers to avoid signed or width surprises.

Many groups are repeated by pipe, endpoint, channel, or pad number. Copy/paste mistakes can compile while accessing the wrong CRTC (`CRTC0` versus `CRTC5`), DDC pad, Azalia function, AUX ownership state, or multichannel audio slot. The repeated blocks should be validated against generation output rather than hand-edited.

Timing and update fields have display-visible failure modes. Incorrect CRTC total/blank/sync masks can prevent modesets, cause unstable scanout, or break vblank interrupt behavior. Cursor surface/address or update mistakes can cause visible cursor corruption or stale updates. ABM/PWM mistakes can create backlight flicker or incorrect brightness. AUX errors can break EDID/DPCD access and hot-plug handling. Azalia mistakes can break HDMI/DP audio, ELD, channel allocation, or audio hot-plug events.

Chunk-boundary risk exists at both ends. This chunk starts the include guard and early register families, but the header continues through two more chunks. The final `DC_GPIO_GENLK_MASK` fields are incomplete here and must be reconciled with chunk 2. Any per-file report should avoid treating this chunk as a complete description of DCE 6.0 masks.

## Test Signals

Useful validation signals include:

- Build coverage for all translation units that include `dce_6_0_sh_mask.h`, especially DCE 6.0 timing-generator and Southern Islands power-management code.
- Static generated-header checks that each field has the expected `_MASK` and `__SHIFT` pair, that masks align with shifts and field widths, and that no duplicate macro has conflicting values.
- Diffing this generated header against AMD's authoritative DCE 6.0 register database and against nearby generation headers for stable fields such as CRTC timing, AFMT audio packet control, AUX software control, and VGA compatibility registers.
- Modeset tests on DCE 6.0/Southern Islands hardware, checking CRTC enable/disable, htotal/vtotal limits, vblank/vsync interrupts, frame counters, cursor updates, stereo/3D disable paths, and test-pattern programming where available.
- DisplayPort AUX/HPD tests that exercise EDID/DPCD reads, link-service transactions, HPD disconnect, AUX arbitration, timeout/error handling, and interrupt ack/mask behavior.
- HDMI/DP audio tests covering stream enable/disable, sample format changes, IEC 60958 channel status, AVI/audio infoframes, ELD/sink metadata, HBR, multichannel allocation, and audio format-change interrupts.
- Backlight and ABM tests checking PWM enable/period/fractional mode, ABM source select, histogram/luma result readback, lock/update-pending behavior, and visible brightness stability.
- Analog/VGA compatibility tests for DAC autodetect/comparator status, legacy VGA palette/indexed registers, per-pipe VGA routing, and DAC CRC/readback where analog outputs are supported.
- Power-management and clock-gating tests around DCCG/VPCLK, DCFE soft resets, and memory light-sleep fields, because these masks are included from legacy DPM code.

## Cross-Chunk Notes

This is chunk 1 of 3 for `dce_6_0_sh_mask.h`. Later chunks continue the DC GPIO/genlock family and cover the rest of the generated DCE 6.0 register field database. The final per-file research document should merge this chunk with `subset-b-001566` and `subset-b-001567`, deduplicate repeated macro-family descriptions, and confirm the include guard closes correctly at the end of the full file.

### subset-b-001566: lines 3623-7461

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_6_0_sh_mask.h lines 3623-7461

## Purpose

This chunk is part of the generated AMDGPU DCE 6.0 register field mask/shift header. It contains no executable C code; it publishes compile-time constants for decoding and programming bit fields in Southern Islands / DCE 6.0 display-engine registers.

Each register field is represented by paired macros:

- `REGISTER__FIELD_MASK` gives the already-positioned bit mask.
- `REGISTER__FIELD__SHIFT` gives the least-significant bit position for inserting or extracting the field.

Driver code combines these masks and shifts with register address constants from the matching `dce_6_0_d.h` header and with AMDGPU register helpers such as `RREG32()`, `WREG32()`, and `REG_SET_FIELD()`. The header is therefore a hardware-layout contract: correctness depends on exact bit positions rather than local algorithms in this file.

## Important APIs, Types, And Macros

There are no functions, structs, enums, storage objects, or runtime APIs in this chunk. The macro namespace is the API surface consumed by display, interrupt, GPIO, power, graphics plane, and HDMI/audio code.

Major macro groups in this line range are:

- Display GPIO and pin control: `DC_GPIO_GENLK_*`, `DC_GPIO_HPD_*`, `DC_GPIO_I2CPAD_*`, `DC_GPIO_PWRSEQ_*`, and `DC_GPIO_SYNCA_*` define masks for genlock, swaplock, hotplug detect, I2C DDC pads, panel power sequencing pins, and sync outputs. These fields cover output values, output enables, input reads, mask bits, pull-up/pull-down controls, and pad drive strengths.
- GPU timer and hotplug detect: `DC_GPU_TIMER_*` gives timing read and event-position fields for vsync, page flip, and vertical update; `DC_HPD1_*` through `DC_HPD6_*` define connection timers, HPD enable, interrupt status/ack/enable/polarity, RX interrupt handling, fast-train delays, and toggle filtering.
- Display clock, reset, and power control: `DCI_*`, `DCO_*`, `DENTIST_DISPCLK_CNTL`, `DIG_SOFT_RESET`, `DCI_SOFT_RESET`, `DCO_SOFT_RESET`, memory power-state fields, light-sleep disables, clock ramp controls, and `DISPCLK_FREQ_CHANGE_CNTL` describe display clocking, display controller resets, memory power gating, and clock-change sequencing.
- Interrupt routing and status: `DISP_INTERRUPT_STATUS*`, `DMCU_INTERRUPT_STATUS*`, `DMCU_INTERRUPT_TO_HOST_EN_MASK*`, `DMCU_INTERRUPT_TO_UC_EN_MASK*`, `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL*`, and `DC_I2C_INTERRUPT_CONTROL*` expose display, DMCU, HPD, I2C, and pipeline interrupt status and routing fields.
- DMCU and debug access: `DMCU_*`, `DCIO_DEBUG*`, `DCI_TEST_DEBUG_*`, `DCP_TEST_DEBUG_*`, `DCPG_TEST_DEBUG_*`, `DMIF_TEST_DEBUG_*`, and `DOUT_SCRATCH*` define microcontroller RAM/ERAM/IRAM access, firmware address/checksum state, internal interrupt state, debug index/data windows, and scratch fields.
- Display pipe, DCP, DMIF, LUT, and FBC controls: `DCP_*`, `DC_LUT_*`, `DEGAMMA_CONTROL`, `DENORM_CONTROL`, `DMIF_*`, `DPG_PIPE_*`, `FBC_*`, and `FMT_*` cover color processing, dithering, CRC, LUT access, display memory interface address/arbitration/status, pipe stutter/NB p-state controls, frame buffer compression, formatter CRC, and bit-depth controls.
- Digital output, DisplayPort, DVO, and HDMI packet fields: `DIG_*`, `DOUT_*`, `DP_*`, `DVO*`, `HDMI_*`, `GENFC_*`, and `GENMO_*` describe digital encoder controls, FIFO/status/test-pattern controls, DP secondary packets/MSE/audio framing/PHY symbols, DVO FIFO and mode controls, legacy VGA fields, HDMI ACR/audio/infoframe/generic-packet controls, deep-color state, keepout, AVMUTE, and packing phase.
- Legacy VGA and graphics plane fields: `GRA00` through `GRA08`, `GRPH8_*`, and `GRPH_*` define VGA graphics-controller fields plus primary display-surface state: depth, format, tiling, bank/pipe layout, pitch, primary/secondary/compressed surface addresses, DFQ status/reset, page-flip interrupts, LUT bypass, stereo flip, endian/component swap, update locking and pending/taken bits, visible surface offsets, and source rectangle coordinates.

The range starts in the middle of the `DC_GPIO_GENLK_MASK` block and ends inside the HDMI infoframe-control block. Earlier and later chunks complete the full `dce_6_0_sh_mask.h` namespace.

## Control Flow

This file has no runtime control flow. Every line is a preprocessor definition.

Runtime behavior appears in consumers that follow a read-modify-write pattern:

1. Select a register address from `dce_6_0_d.h`, such as `mmDC_HPD1_CONTROL`, `mmHDMI_GC`, or `mmGRPH_CONTROL`.
2. Read the register through AMDGPU's MMIO helpers.
3. Extract, clear, or insert a field using the `*_MASK` and `*__SHIFT` macros, often through `REG_SET_FIELD()`.
4. Write the result back when the register is writable and the display block is in a valid state for the operation.

Control-sensitive fields in this chunk include HPD interrupt enable/ack/polarity, DMCU interrupt routing, display clock ramp/frequency-change controls, soft resets, memory power-state controls, DPG stutter and NB p-state controls, graphics surface update locking/pending fields, page-flip interrupt controls, HDMI packet send/continuous/auto-send controls, and DP secondary-packet framing fields. The header itself does not enforce sequencing; that responsibility stays in the display and power-management code.

## State And Persistence Behavior

The header stores no software state and has no persistence mechanism. It describes state held in display-engine hardware registers.

The represented hardware state includes connector GPIO levels, HPD sense and interrupt latches, DDC/I2C transaction status, display clock and reset bits, DMCU program/RAM/debug state, display interrupt status and masks, LUT and color-pipeline controls, DMIF arbitration and status, FBC controls, display-pipe stutter policy, graphics surface addresses and tiling, page-flip/update-pending state, DP and HDMI packet generator state, and legacy VGA register fields.

Persistence is hardware-specific. Some fields are read-only status snapshots, some are sticky interrupt/status bits cleared by ack fields, some are latched until the next vblank or surface update, and some are programmed control bits that remain until a later driver/firmware write, modeset, suspend/resume, display reset, ASIC reset, or power-gating transition. The mask header does not encode access permissions, volatility, write-one-to-clear behavior, or timing requirements.

## Dependencies And Integration Points

This chunk depends on the generated DCE 6.0 address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_6_0_d.h`

Direct include points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v6_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v6_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v6_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/si_dpm.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce60/dce60_timing_generator.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce60/hw_factory_dce60.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce60/hw_translate_dce60.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce60/dce60_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce60/irq_service_dce60.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce60/dce60_resource.c`

Concrete consumers in `dce_v6_0.c` use this chunk's fields to enable and disable HPD pins with `DC_HPD1_CONTROL__DC_HPD1_EN_MASK`, configure HPD interrupt controls, program HDMI audio and infoframe packet controls with `HDMI_*` fields, mute HDMI through `HDMI_GC__HDMI_GC_AVMUTE`, and construct display surface format/swap values with `GRPH_CONTROL__GRPH_DEPTH__SHIFT`, `GRPH_CONTROL__GRPH_FORMAT__SHIFT`, and `GRPH_SWAP_CNTL__*` fields.

Although the source tree path is under a local `ceph-client` mirror, this file is AMDGPU Linux kernel display-register metadata. It has no Ceph filesystem semantics, no distributed-storage protocol behavior, and no persistent filesystem state.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. Incorrect masks or shifts can compile successfully while reading the wrong status bit, failing to update the intended field, or corrupting adjacent bits in packed display registers.

High-risk areas include HPD and DDC fields. Bad HPD masks can cause missed monitor hotplug events, interrupt storms, wrong connector sense, or broken eDP/LVDS behavior. Bad I2C/DDC transaction or arbitration fields can break EDID reads and connector detection.

Clock, reset, and power fields are also sensitive. Incorrect `DENTIST_DISPCLK_CNTL`, `DISPCLK_FREQ_CHANGE_CNTL`, `DCI_*`, `DCO_*`, or soft-reset definitions can destabilize modesets, suspend/resume, dynamic power management, display memory power gating, or DMCU communication.

Graphics surface fields carry direct scanout risk. Wrong `GRPH_CONTROL`, address, pitch, tiling, endian-swap, component-crossbar, update-lock, or page-flip interrupt definitions can produce corrupted display output, scanout from the wrong address, bad big-endian behavior, missed flip completion, or hangs while waiting for update-pending bits.

HDMI/DP packet fields affect protocol compliance. Bad ACR, infoframe, audio packet, generic packet, deep color, keepout, AVMUTE, DP secondary-packet, or MSE fields can cause missing audio, incorrect color/deep-color signaling, bad infoframes, link protocol errors, or display compatibility regressions.

The chunk boundaries are artificial. The first lines continue a `DC_GPIO_GENLK_MASK` register started earlier, and the final lines stop in the HDMI infoframe area before the header continues. The later per-file merge should not interpret these line-range boundaries as real module boundaries.

## Test Signals

Useful validation signals are mostly compile-time and hardware-behavior oriented:

- Kernel build coverage for Southern Islands / DCE 6.0 AMDGPU paths that include `dce_6_0_sh_mask.h`.
- Static comparison of every generated `*_MASK` and `*__SHIFT` pair against AMD's register database and the adjacent address definitions in `dce_6_0_d.h`.
- Connector hotplug tests across HPD1-HPD6, including connect/disconnect, interrupt ack/polarity, eDP/LVDS cases, and repeated DPMS or suspend/resume cycles.
- DDC/EDID reads through all relevant GPIO/I2C pads, including timeout, NACK, arbitration, and software/hardware I2C status paths.
- Modeset and page-flip tests that exercise all supported framebuffer formats, tiling modes, endian/component swap paths, surface address changes, update locks, flip interrupts, and vblank synchronization.
- HDMI audio/video tests covering ACR N/CTS programming, audio packet enablement, infoframe transmission, AVMUTE, generic packets, deep color, and keepout behavior.
- DisplayPort secondary-packet and MSE tests, plus PHY symbol/status checks where available.
- Power-management and reset tests that cover display clock frequency changes, stutter/NB p-state transitions, memory power states, DMCU interrupts, and resume from system/runtime suspend.
- CRC/FBC/debug validation where lab or debugfs tooling can compare expected display CRCs, frame-buffer compression state, interrupt status, and debug-index/data reads.

Regression symptoms from bad constants include no display after modeset, corrupted scanout, wrong colors or byte order, missed or repeated hotplug interrupts, EDID read failures, missing HDMI audio, incorrect HDMI/DP infoframes, page-flip timeouts, vblank/interrupt loss, display clock instability, suspend/resume display failures, and DMCU or FBC diagnostics reporting inconsistent state.

## Cross-Chunk Notes

Earlier chunks of `dce_6_0_sh_mask.h` define AFMT, audio, cursor, CRTC, viewport, scaler, and the beginning of the GPIO namespace. Later chunks continue HDMI/infoframe, memory-display latency/watermark, overlay, scaler, stereo, vblank/vline, viewport, and related DCE 6.0 display fields. The final per-file research document should treat the full header as one generated DCE 6.0 register-layout contract rather than as independent algorithms per chunk.

### subset-b-001567: lines 7462-9948

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_6_0_sh_mask.h lines 7462-9948

## Scope And Purpose

This chunk is the tail section of the generated AMD DCE 6.0 register shift/mask header. It contains C preprocessor constants only: no functions, structs, enums, storage, or executable control flow. Each exported symbol describes either the bit mask or shift for one hardware register field, normally consumed through AMDGPU/DC helper macros such as `REG_SET_FIELD()` or direct mask writes.

The source tree is a Ceph-client repository that vendors Linux GPU driver code; this file belongs to the AMD display engine support code, not to Ceph filesystem behavior. The purpose of this header section is to give DCE 6.0 display, memory-interface, encoder, PLL, VGA, and XDMA programming code stable symbolic names for MMIO bit positions.

The chunk begins in the middle of the `HDMI_INFOFRAME_CONTROL0` macro family: the `HDMI_AUDIO_INFO_SEND_MASK` definition is in the previous chunk, while this chunk starts with its `__SHIFT`. It then covers HDMI packet/status fields, CSC/gamma/keyer and line-buffer controls, LVDS/LVTMA panel power sequencing, MCIF and DMIF-related status, MVP multi-view/AFR controls, overlay surface/scaler/update fields, pipe arbitration and power-gating fields for pipes 0 through 5, PLL/display-clock programming, prescale/regamma/scaler fields, VGA sequencer and legacy VGA aperture controls, TMDS/UNIPHY encoder/link controls, XDMA master/slave fields, and a final commented block for selected data format, line-buffer, priority, interrupt, vline/vblank, and scaler-init fields before the include guard closes.

## Important APIs, Types, And Macro Families

There are no callable APIs or C types in this range. The interface is the macro namespace. Most names follow `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`, with register fields encoded as hexadecimal masks and shift values.

Major display-output and packet families include `HDMI_INFOFRAME_CONTROL0/1`, `HDMI_STATUS`, and `HDMI_VBI_PACKET_CONTROL`. These describe AVI/audio/MPEG infoframe send/continuous modes, line placement, AVMUTE and packet error state, and VBI packets such as GC, ISRC, ACP, and NULL packets.

Color pipeline and blending families include `INPUT_CSC_*`, `INPUT_CSC_CONTROL`, `INPUT_GAMMA_CONTROL`, `KEY_CONTROL`, `KEY_RANGE_*`, `OUTPUT_CSC_*`, `OUTPUT_CSC_CONTROL`, `PRESCALE_*`, `REGAMMA_*`, `REGAMMA_LUT_*`, and `OUT_ROUND_CONTROL`. These provide packed coefficient fields, LUT mode selection, color-key limits, prescale bias/scale fields, regamma piecewise-region controls for CNTLA/CNTLB, and truncation/rounding controls.

Line-buffer, timing, and interrupt families include `LB_*`, `DATA_FORMAT`, `DC_LB_MEMORY_SPLIT`, `DC_LB_MEM_SIZE`, `INT_MASK`, `PRIORITY_A_CNT`, `PRIORITY_B_CNT`, `VLINE_STATUS`, `VBLANK_STATUS`, `VIEWPORT_SIZE`, and `VIEWPORT_START`. These fields control interlace/data fetch formatting, line-buffer allocation and memory split, urgent watermark priority, vblank/vline masking and acknowledgement, and viewport geometry.

Panel, encoder, and link families include `LVDS_DATA_CNTL`, `LVTMA_PWRSEQ_*`, `PHY_AUX_CNTL`, `TMDS_*`, `SYMCLK[A-F]_CLOCK_ENABLE`, and `UNIPHY_*`. These cover LVDS 24-bit and dual-link timing pins, embedded-panel power-up/down sequencing and status, AUX pad behavior, TMDS control-character generation and DC balancing, symbol clock gating/forcing, UNIPHY test-pattern generation, lane crossbar/inversion, data synchronization, impedance calibration, PLL configuration, power control, soft reset, and transmitter voltage/pre-emphasis settings.

Display memory, power, and diagnostics families include `MC_DC_INTERFACE_NACK_STATUS`, `MCIF_CONTROL`, `MCIF_MEM_CONTROL`, `MCIF_VMID`, `MCIF_WRITE_COMBINE_CONTROL`, `PIPE[0-5]_*`, `LIGHT_SLEEP_CNTL`, `LOW_POWER_TILING_CONTROL`, `SCLK_CGTT_BLK_CTRL_REG`, `MILLISECOND_TIME_BASE_DIV`, and `MICROSECOND_TIME_BASE_DIV`. These describe memory-client NACK status/clear bits, address translation and privileged access, MCIF cache and VMID fields, write-combine timeout, per-pipe DMIF buffer allocation, maximum requests, power-gating force/gate/status fields, memory light-sleep/shutdown disables, low-power tiling geometry, clock-gating delays, and display timebase dividers.

MVP and overlay families include `MVP_*`, `OVL_*`, and `OVLSCL_EDGE_PIXEL_CNTL`. The MVP block contains AFR flip FIFO control, mixer/channel/flow-control state, CRC masks/results, debug taps, FIFO underflow/overflow acknowledgement/status, flip-line insertion, in-band control, slave receive counters, and test debug index/data. Overlay fields describe surface format/depth/tiling, address translation, privileged access, primary/secondary surface addresses and high bits, in-use addresses, DFQ controls/status, start/end/offset geometry, stereo sync flip state, channel crossbars, endian swap, update lock/pending/taken, and overlay scaler edge color.

PLL and clock families include `PIXCLK[0-2]_RESYNC_CNTL`, `PLL_ANALOG`, `PLL_CNTL`, `PLL_DEBUG_CNTL`, `PLL_DISPCLK_*`, `PLL_DS_CNTL`, `PLL_FB_DIV`, `PLL_IDCLK_CNTL`, `PLL_POST_DIV`, `PLL_REF_DIV`, `PLL_SS_*`, `PLL_UNLOCK_DETECT_CNTL`, `PLL_UPDATE_*`, `PLL_VREG_CNTL`, and the legacy `VGA25/28/41_PPLL_*` blocks. These fields are used for display PLL reset, power, ref/post/fb dividers, spread-spectrum controls, DTO updates, lock detection, VCO/analog tuning, and VGA pixel-clock PLLs.

Scaler and LUT families include `SCL_*` and `SCL_TAP_CONTROL`. They define scaler enable/bypass, coefficient RAM select/tap data, coefficient conflict interrupt/status/ack, sharpness controls, horizontal and vertical ratios, filter initial phases, mode-change detection and masking, update lock/pending/taken, tap counts, and test/debug registers.

Legacy VGA families include `SEQ*`, `VGA_*`, and `VGADCC_DBG_DCCIF_C`. They describe VGA sequencer reset, font/map/chain controls, debug readback, VGA display buffers and memory base, HDP/reset/page select, interrupt mask/status/clear bits, main/render/mode/cache controls, source selection, pitch/height selection, and test controls.

XDMA families include `XDMA_CLOCK_GATING_CNTL`, `XDMA_IF_BIF_STATUS`, `XDMA_INTERRUPT`, `XDMA_LOCAL_SURFACE_TILING*`, `XDMA_MC_PCIE_CLIENT_CONFIG`, `XDMA_MEM_POWER_CNTL`, `XDMA_MSTR_*`, `XDMA_SLV_*`, and `XDMA_TEST_DEBUG_*`. They describe cross-GPU/display DMA clock gating, BIF errors, urgent/underflow interrupts, local surface tiling, VMID/swap/privilege, memory power, master and slave enable/reset/ready bits, addresses, pitches, request size/prefetch, NACK status/tag/clear fields, urgent thresholds, latency counters, writeback rate, and debug indexes.

## Control Flow And Data Flow

The chunk has no internal runtime control flow. Data flow is compile-time substitution: source files include `dce_6_0_sh_mask.h`, combine these field descriptors with companion register offsets from DCE 6.0 address headers, and read or write MMIO registers through AMDGPU register helpers.

The classic AMDGPU DCE 6.0 path shows representative use. In `amdgpu/dce_v6_0.c`, HDMI audio enable logic reads `mmHDMI_INFOFRAME_CONTROL0`, updates `HDMI_AVI_INFO_SEND`, `HDMI_AVI_INFO_CONT`, `HDMI_AUDIO_INFO_SEND`, and `HDMI_AUDIO_INFO_CONT` through `REG_SET_FIELD()`, then writes the register back. The same file writes `DATA_FORMAT__INTERLEAVE_EN_MASK` directly when programming interlaced scanout, and uses `INPUT_CSC_CONTROL__INPUT_CSC_GRPH_MODE__SHIFT`, `INPUT_CSC_CONTROL__INPUT_CSC_OVL_MODE__SHIFT`, `PRESCALE_*_BYPASS_MASK`, and `INPUT_GAMMA_CONTROL` shifts while loading a CRTC LUT.

Interrupt handling is another direct integration path. `amdgpu/dce_v6_0.c` acknowledges vblank and vline interrupts by writing `VBLANK_STATUS__VBLANK_ACK_MASK` or `VLINE_STATUS__VLINE_ACK_MASK`. The DC IRQ service for DCE 6.0 builds `irq_source_info` entries with `INT_MASK__VBLANK_INT_MASK` as the enable/mask field and `VBLANK_STATUS__VBLANK_ACK_MASK` as the acknowledgement value.

Because this header is generated, the field names also act as a contract for generic field manipulation helpers. A wrong `_MASK` or `__SHIFT` value still compiles but causes callers to set, clear, or test the wrong hardware bits.

## State And Persistence Behavior

This file stores no process state and performs no I/O. The mutable state represented by the constants lives in DCE 6.0 display hardware registers. Writes made with these masks persist in the device until the driver reprograms the register, a modeset or page flip updates latched state, an interrupt acknowledgement clears sticky status, a power-management transition resets a block, or a GPU reset/suspend-resume sequence restores display state.

Important persistent or latched state categories represented by this chunk include HDMI infoframe and packet generation state, CSC/gamma/regamma/LUT programming, overlay surface address and tiling state, scaler ratios and coefficient RAM state, line-buffer memory split and priority watermarks, vblank/vline interrupt masks and sticky acknowledgements, LVDS/eDP-style power-sequencing state, TMDS/UNIPHY link and transmitter electrical state, PLL clock state, VGA compatibility state, MCIF/DMIF and pipe power-gating status, MVP FIFO/CRC/debug state, and XDMA transfer/configuration/status state.

Several fields are sequencing-sensitive. `*_UPDATE_LOCK`, `*_UPDATE_PENDING`, `*_UPDATE_TAKEN`, `MASTER_UPDATE_*`, `PLL_UPDATE_*`, `OVL_UPDATE`, `SCL_UPDATE`, power-gate status, LVTMA power-sequence target/done state, FIFO reset/ack bits, and interrupt clear/ack bits require caller-side ordering. The macros do not encode whether a bit is write-one-to-clear, read-only status, latch control, or ordinary configuration; the call site must know the hardware contract.

## Dependencies And Integration Points

This chunk depends on the rest of `dce_6_0_sh_mask.h` for include guard context and for fields that start before line 7462. It also depends on companion DCE 6.0 offset/register definition headers, especially the `mm...` register address symbols used by AMDGPU/DC code.

Direct include users in this tree include `amd/amdgpu/dce_v6_0.c`, `amd/amdgpu/gfx_v6_0.c`, `amd/amdgpu/gmc_v6_0.c`, `amd/amdgpu/si.c`, `amd/pm/legacy-dpm/si_dpm.c`, and DCE 6.0 DC files such as `display/dc/dce60/dce60_timing_generator.c`, `display/dc/hwss/dce60/dce60_hwseq.c`, `display/dc/resource/dce60/dce60_resource.c`, and `display/dc/irq/dce60/irq_service_dce60.c`.

The primary integration surfaces are DRM/KMS modesetting, CRTC timing and vblank handling, HDMI/DP audio and infoframe setup, panel and encoder link bring-up, color management and gamma LUT programming, overlay plane scanout, scaler setup, display memory fetch and arbitration, pipe power gating, legacy VGA handling, display PLL programming, suspend/resume restoration, debug/CRC paths, and XDMA-based display data movement.

The names are ASIC-generation specific. Many register fields have close analogs in DCE 8/10/11/12 and DCN headers, but those versions may have different offsets, replicated instance names, or additional/missing fields. Mixing DCE generation headers with the wrong offset table is a high-risk integration error.

## Risks And Edge Cases

The highest risk is silent numeric drift from the authoritative AMD register database. The compiler validates macro syntax, not hardware correctness. An incorrect mask or shift can modify adjacent fields, leave a status bit uncleared, disable a clock or lane, corrupt a surface address, or destabilize display timing while still building cleanly.

This is a partial file chunk. It starts after the first `HDMI_INFOFRAME_CONTROL0` mask in the previous chunk and ends at the `#endif` for the header. The final merged per-file report should not treat the beginning as a complete HDMI family, but it can treat the end as the end of the source file.

Packed fields are common. CSC coefficients, prescale bias/scale, regamma regions, viewport/geometry fields, PLL dividers, link electrical settings, VGA page addresses, and XDMA addresses/pitches often share 32-bit registers. Off-by-one shifts, signedness assumptions, or stale field widths can cause adjacent channel, clock, address, or status corruption.

Interrupt and status fields are easy to misuse because many names have parallel mask, status, occurred, ack, clear, and interrupt bits. Examples include HDMI error bits, MVP FIFO status, SCL coefficient conflict, VGA interrupt status/clear, XDMA interrupt/NACK fields, MC interface NACK fields, and vblank/vline status. Writing a status mask where an ack mask is required can lose events or leave interrupts asserted.

Clock, link, and panel power fields have visible failure modes. Wrong PLL, UNIPHY, TMDS, SYMCLK, LVDS, or LVTMA power-sequence fields can produce blank displays, unstable link training, incorrect color depth, stuck backlight/panel power, or failure to resume after suspend.

Memory-fetch and DMA fields can cause underflow or memory faults. Overlay tiling/address fields, MCIF/VMID/privilege fields, pipe buffer allocation, priority marks, low-power tiling, and XDMA master/slave configuration must agree with framebuffer layout, memory controller setup, and display timing.

## Test Signals

There are no meaningful unit tests for this header chunk alone. Useful validation starts with build coverage for DCE 6.0 AMDGPU/DC configurations that include `dce_6_0_sh_mask.h`, ensuring all macro names used by call sites resolve.

Generated-header integrity should be checked against the authoritative DCE 6.0 register database or a known-good upstream header. Focus areas for this chunk are the partial `HDMI_INFOFRAME_CONTROL0` boundary, packed CSC/regamma/prescale fields, interrupt ack/mask/status bits, pipe 0-5 repeated fields, PLL/UNIPHY electrical fields, VGA compatibility fields, XDMA address/NACK/urgent fields, and the final commented block before `#endif`.

Runtime validation signals include successful modeset on DCE 6.0 hardware, stable vblank/vline interrupt delivery and acknowledgement, correct HDMI/DP audio/infoframe behavior, correct LUT/gamma/color conversion output, no display underflow or FIFO error interrupts, working overlay/scaler configurations, correct panel backlight/power sequencing, stable suspend/resume, and no link-training or PLL lock failures.

Targeted diagnostic tests should exercise interlaced and progressive scanout (`DATA_FORMAT`), vblank/vline interrupt enable and ack paths, color LUT reload, overlay primary/secondary address flips, scaler coefficient updates, HDMI AVMUTE and infoframes, VGA legacy register access if enabled, pipe power-gate status transitions, and XDMA master/slave NACK/underflow/urgent reporting.
