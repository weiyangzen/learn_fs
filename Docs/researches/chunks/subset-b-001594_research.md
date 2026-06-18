# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 32308-34753

## Scope

This chunk covers 2,446 lines from the generated DCN 1.0 register shift/mask header. It starts at the tail of the `DIG1_AFMT_CNTL` definitions, contains `DIG1_AFMT_VBI_PACKET_CONTROL1`, then covers the complete `dce_dc_dio_dp1_dispdec`, `dce_dc_dio_dig2_dispdec`, and `dce_dc_dio_dp2_dispdec` address blocks. It ends inside the `dce_dc_dio_dig3_dispdec` block at `DIG3_AFMT_AUDIO_INFO1`; the rest of the DIG3 audio-format fields continue in the following chunk.

The source is not executable C. It exports preprocessor constants of the form `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` for DCN 1.0 DisplayPort, HDMI/TMDS, DIG, and AFMT register fields. These macros pair with `dcn_1_0_offset.h` register addresses and with AMD display register helper macros such as `REG_UPDATE`, `REG_GET`, `REG_SET`, and the `SE_SF`/`LE_SF` mask-list builders used by DCN10 stream and link encoders.

## Purpose

The chunk describes the bit layouts for three display-output lanes/engines:

- `DP1_*` and `DP2_*` DisplayPort encoder state: link control, pixel format, MSA fields, video stream enable/status, DPHY training/test/CRC controls, secondary-data packets, audio M/N, MST/MSE slot-allocation tables, MSO, DSC control, double-buffering, and MSA/VBID misc controls.
- `DIG2_*` digital encoder state: front-end and back-end control, output CRC/test-pattern generation, FIFO status, HDMI mode/control/status, HDMI audio and ACR packet controls, HDMI infoframe and generic packet controls, AFMT packet/audio metadata, TMDS control and test generation, DIG version/lane enable, AFMT clock control, and AFMT VBI generic-packet update triggers.
- The beginning of the analogous `DIG3_*` digital encoder state, from DIG front-end/output-test fields through HDMI/AFMT generic packets, ACR registers, status readback, and the start of audio infoframe fields.

These definitions let higher-level DCN10 code address replicated hardware blocks by instance while writing generic field names. The generated macros preserve the concrete hardware layout for DP1/DP2/DIG2/DIG3, including fields that are writable controls, read-only status, sticky interrupt/overflow flags, and pending bits used for synchronized hardware updates.

## Important Macro Families

The `DIG1_AFMT_VBI_PACKET_CONTROL1` tail defines per-generic-packet update controls for AFMT generic slots 0 through 7. For each slot it exposes frame-update, frame-update-pending, immediate-update, and immediate-update-pending bits. This is used to schedule auxiliary/audio-format packet payload changes either at a frame boundary or immediately.

The `DP1_*` and `DP2_*` blocks are structurally repeated and include:

- Link and stream controls: `DP_LINK_CNTL`, `DP_PIXEL_FORMAT`, `DP_MSA_COLORIMETRY`, `DP_CONFIG`, `DP_VID_STREAM_CNTL`, `DP_LINK_FRAMING_CNTL`, `DP_VID_MSA_VBID`, `DP_VID_INTERRUPT_CNTL`, and `DP_MSA_VBID_MISC`.
- Stream timing and M/N generation: `DP_VID_TIMING`, `DP_VID_N`, `DP_VID_M`, and `DP_MSA_TIMING_PARAM1` through `PARAM4`.
- PHY training and diagnostics: `DP_DPHY_CNTL`, `DP_DPHY_TRAINING_PATTERN_SEL`, `DP_DPHY_SYM0` through `SYM2`, `DP_DPHY_8B10B_CNTL`, PRBS/scrambler/CRC controls and results, fast-training controls/status, byte/symbol swap controls, and HBR2 pattern selection.
- Secondary-data and audio transport: `DP_SEC_CNTL`, `DP_SEC_CNTL1` through `CNTL7`, `DP_SEC_FRAMING1` through `FRAMING4`, `DP_SEC_AUD_N`, `DP_SEC_AUD_M`, readback registers, `DP_SEC_TIMESTAMP`, and `DP_SEC_PACKET_CNTL`.
- MST/MSO/DSC support: `DP_MSE_RATE_CNTL`, `DP_MSE_RATE_UPDATE`, `DP_MSE_SAT0` through `SAT2`, `DP_MSE_SAT_UPDATE`, `DP_MSE_LINK_TIMING`, `DP_MSE_MISC_CNTL`, status mirrors, `DP_MSO_CNTL`, `DP_MSO_CNTL1`, and `DP_DSC_CNTL`.
- Double-buffer controls: `DP_DB_CNTL` exposes pending, taken, clear, lock, and disable bits for synchronized register updates.

The `DIG2_*` block and the visible `DIG3_*` portion provide HDMI/TMDS and AFMT controls:

- DIG front-end and test/readback fields: `DIG_FE_CNTL`, output CRC control/result, clock/test/random patterns, and FIFO underflow/overflow interrupt, ack, mask, and force bits.
- HDMI mode and packets: `HDMI_CONTROL`, `HDMI_STATUS`, audio packet, ACR packet, VBI packet, infoframe controls, generic packet controls, general-control packet, deep-color/scrambler/keepout fields, ACR CTS/N programming and readback, and double-buffer status.
- AFMT metadata/audio fields: interrupt status, audio packet control, ISRC packet data, MPEG info, generic packet header and 32-byte generic payload banks, audio infoframe fields, IEC 60958 channel-status words, audio CRC, ramp/test controls, AFMT status, audio source selection, and AFMT clock enable/status.
- TMDS controls: encoder enable, sync/control-character patterns, DCBalancer, stereo-sync selection, lane/control-bit generation, per-control-symbol data selection, delays, inversion, modulation, feedback, and pattern output.
- DIG back-end and lane state: `DIG_BE_CNTL`, `DIG_BE_EN_CNTL`, `DIG_VERSION`, and `DIG_LANE_ENABLE`.

## APIs, Types, and Functions

There are no C functions, structs, enums, or runtime APIs in this chunk. The macros themselves are the ABI-like interface between generated ASIC metadata and DCN display code:

- `*_SHIFT` values are the bit offsets for packing or extracting a field.
- `*_MASK` values are already-positioned bit masks for read/modify/write helpers.
- Address-block comments group replicated hardware instances: `dce_dc_dio_dp1_dispdec`, `dce_dc_dio_dig2_dispdec`, `dce_dc_dio_dp2_dispdec`, and the start of `dce_dc_dio_dig3_dispdec`.

Integration code maps the instance-specific macros into per-object register structures. For example, `dcn10_stream_encoder.h` lists DP and DIG stream encoder registers such as `DP_SEC_CNTL`, `DP_MSE_RATE_CNTL`, `DP_VID_STREAM_CNTL`, `HDMI_CONTROL`, and AFMT audio registers, then uses `SE_SF(DP0_..., FIELD, mask_sh)` aliases so generic encoder code can operate on a selected instance. `dcn10_link_encoder.h` similarly maps link-side DP MST slot-allocation and video-stream fields through `LE_SF(...)`.

## Control Flow

This header has no control flow by itself. The runtime sequences are in DCN10 link and stream encoder code that consumes these masks:

1. Resource construction includes `dcn_1_0_offset.h` and this header, then builds register address and shift/mask tables for each stream/link encoder instance.
2. Mode-set and link-training code programs DP link, pixel, lane, DPHY, M/N, framing, stream-enable, and secondary-data fields with register helper macros.
3. HDMI setup writes `HDMI_CONTROL`, packet-control, ACR, infoframe, AFMT, and TMDS fields according to the signal type, pixel clock, color depth, audio layout, and infoframe payloads.
4. MST setup writes `DP_MSE_SAT*`, `DP_MSE_RATE_*`, and update bits, then polls pending/keepout/status fields before considering slot allocation active.
5. Stream disable paths clear `DP_VID_STREAM_ENABLE`, may program `DP_VID_STREAM_DIS_DEFER`, and wait for `DP_VID_STREAM_STATUS` to drop before proceeding.
6. Generic packet, AFMT, double-buffer, CRC, FIFO, overflow, and interrupt-style fields expose status, pending, ack, mask, and clear bits that caller code must order correctly around hardware update points.

The replicated DP1/DP2 and DIG2/DIG3 names are not arbitrary aliases: their prefixes encode the physical register instance. A mismatch between offset and shift/mask instance can program the wrong display engine or corrupt a neighboring field in the right engine.

## State and Persistence

The header stores no software state, but every macro describes persistent hardware register state in DCN display output blocks. Relevant state includes:

- DP link/stream state: link training complete/status, embedded-panel mode, lane count, pixel encoding/depth, video stream enable/status, M/N generation, MSA/VBID placement, interrupt state, and enhanced framing.
- DP PHY/test state: training pattern selection, custom symbol patterns, 8b/10b disable, PRBS/scrambler toggles, CRC enable/reset/continuous mode/result, fast-training status, and byte/symbol swap controls.
- DP secondary-data and audio state: global and per-packet enables, packet line numbers, MSA/audio timestamping, audio M/N values and readbacks, packet priority, generic stream-packet send/pending bits, and VSC SDP metadata.
- MST/MSO/DSC state: payload slot allocation, rate update pending status, keepout status, link timing, MSO segment mapping and timing fields, and DSC mode enable.
- HDMI/TMDS/AFMT state: deep color, scrambler, keepout, packet enable/line controls, ACR N/CTS, infoframes, generic payload bytes, ISRC/MPEG/audio info fields, IEC 60958 channel status, audio source/channel layout, CRC/ramp test state, TMDS symbols, and DIG lane enables.

These hardware fields persist until overwritten, reset, disabled by power management, or reinitialized by firmware/driver mode-set flows. Pending, taken, ack, clear, interrupt, overflow, and status fields are especially stateful because some are read-only hardware observations while others require write-one-to-clear or explicit update sequences. The generated header does not encode those semantics beyond the field names.

## Dependencies and Integration Points

Direct dependencies are limited to the C preprocessor and the companion register offset file `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h`. Real users include:

- `display/dc/resource/dcn10/dcn10_resource.c`, which includes both DCN 1.0 offset and shift/mask headers while constructing DCN10 hardware resource tables.
- `display/dc/dio/dcn10/dcn10_stream_encoder.h` and `.c`, which consume DP secondary-data, DP video stream, HDMI, AFMT, ACR, and audio-field masks.
- `display/dc/dio/dcn10/dcn10_link_encoder.h` and `.c`, which consume `DP_VID_STREAM_CNTL`, `DP_SEC_CNTL1`, and MST `DP_MSE_SAT*` fields.
- `display/dc/irq/dcn10/irq_service_dcn10.c`, GPIO translation/factory code, and DCN20 GPIO translation code, which include this generated header as part of the shared DCN register description surface.
- Shared display register helpers from `reg_helper.h`, whose macros rely on consistent shift/mask naming to generate correct MMIO read/modify/write operations.

The DP and DIG block structures are repeated across instances and generations. Later DCN stream encoder headers show the same conceptual field groups, which is a useful consistency check when validating generated DCN 1.0 masks.

## Risks

The highest risk is silent hardware misprogramming. A wrong shift or mask in this generated header can compile cleanly while changing an unrelated field inside a live DP, HDMI, AFMT, or TMDS register.

Chunk-boundary risk is present at both ends. The chunk starts after the `DIG1_AFMT_CNTL__AFMT_AUDIO_CLOCK_EN__SHIFT` definition but includes its `AFMT_AUDIO_CLOCK_ON` shift and both masks. It also ends midway through `DIG3_AFMT_AUDIO_INFO1`; the later merge lane must combine this with adjacent chunks to avoid treating partial register families as complete.

Instance-alignment errors are possible because DP1/DP2 and DIG2/DIG3 are repeated with near-identical fields. Code that pairs `mmDP2_*` offsets with `DP1_*` masks, or DIG2 offsets with DIG3 masks, may hit a valid-looking register with wrong instance semantics.

Several fields have order-sensitive hardware behavior. `DP_VID_STREAM_ENABLE` and `DP_VID_STREAM_STATUS` are used in disable/enable waits; `DP_MSE_SAT_UPDATE` and keepout fields gate MST slot changes; `DP_MSE_RATE_UPDATE_PENDING`, `DP_SEC_GSP*_SEND_PENDING`, double-buffer pending/taken bits, and AFMT VBI update-pending bits require polling or frame-boundary synchronization. Incorrect masks here can cause hangs, lost packets, or visible mode-set glitches.

Audio/video packet fields have protocol-visible consequences. Bad ACR N/CTS, IEC 60958, AFMT audio info, HDMI infoframe, generic packet, or DP secondary-data masks can produce broken HDMI/DP audio, missing HDR/VRR/VSC metadata, invalid AVI/SPD/vendor packets, or sink compatibility failures without crashing the driver.

Diagnostic and interrupt fields can hide real faults. FIFO underflow/overflow masks, CRC controls/results, DPHY training status, fast-training status, and interrupt ack/mask fields are often used for hardware bring-up and failure handling; incorrect masks may suppress errors or report false positives.

## Test Signals

Useful validation signals include:

- Build coverage for DCN10/DCN20 display code that includes `dcn_1_0_sh_mask.h`, especially stream/link encoder, resource, IRQ, and GPIO translation objects.
- Generated-header checks that each `REGISTER__FIELD__SHIFT` has a matching `REGISTER__FIELD_MASK`, masks align with shifts, and repeated DP1/DP2 and DIG2/DIG3 blocks stay structurally equivalent where hardware intends them to be equivalent.
- Diff checks against AMD's authoritative DCN 1.0 register database or known-good upstream generated headers.
- DP link-training and mode-set smoke tests that exercise `DP_LINK_CNTL`, `DP_CONFIG`, `DP_DPHY_*`, `DP_VID_STREAM_CNTL`, MSA/M/N, and video-stream disable waits.
- MST tests that program payload slot allocations through `DP_MSE_SAT*`, assert update/keepout behavior, and verify payload bandwidth on multiple streams.
- HDMI tests across color depths and pixel clocks that validate `HDMI_CONTROL`, scrambler/deep-color, ACR N/CTS, audio packet transmission, infoframes, and TMDS lane behavior.
- Audio and metadata tests for AFMT audio source/channel layout, IEC 60958 channel status, audio infoframes, generic packet payloads, HDR/VSC/SPD/AVI metadata, and DP secondary packets.
- Hardware diagnostic tests for output CRC, DPHY CRC, PRBS/scrambler patterns, FIFO overflow/underflow reporting, and interrupt ack/mask fields.

## Cross-Chunk Notes

This chunk is a middle slice of a large generated header. It should be merged with neighboring chunks for a complete per-file report: the preceding chunk owns the earlier DIG1/DIG0 families, and the following chunk continues `DIG3_AFMT_AUDIO_INFO1` and the rest of the DIG3/DIG/DP replicated blocks. Treat this document as coverage for the DP1/DIG2/DP2 complete blocks plus partial DIG1 and DIG3 boundaries, not as a standalone module boundary.
