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
