# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 32580-34984

## Scope

This chunk is a generated AMD DCN 3.6.0 register field shift/mask header segment. It contains preprocessor constants only: every exported item is a `#define` naming a hardware register field's bit shift or bit mask. There are no functions, structs, control statements, allocations, locks, or direct MMIO accesses in this slice. Runtime behavior is created by code that includes this header and feeds these constants into AMD display register helper macros.

The covered lines span the tail of the `dce_dc_dio_dig0_dispdec` block, the complete `dce_dc_dio_dp1_dispdec` block visible in this slice, the `dce_dc_dio_dig1_dispdec` block, and the beginning of `dce_dc_dio_dp2_dispdec`.

## Purpose

The chunk supplies bitfield metadata for the DCN 3.6 display I/O encoder path:

- `DIG0_*` and `DIG1_*` define Digital Front End, HDMI, AFMT, backend clock, TMDS, FIFO, CRC, test pattern, metadata, generic packet, audio clock regeneration, deep color, double-buffer, and version fields for two DIG instances.
- `DP1_*` defines DisplayPort stream/link/PHY/secondary-data/MST/ALPM/debug counters for DP instance 1.
- `DP2_*` begins the same DisplayPort field set for DP instance 2 and continues past the end of this chunk.

These constants let generic display code write field names such as `HDMI_DEEP_COLOR_ENABLE`, `DP_SEC_GSP0_ENABLE`, or `DP_MSE_SAT_UPDATE` without embedding numeric bit positions in the driver source.

## Important Defines And Register Areas

### DIG0 HDMI/TMDS Tail

The chunk starts in the DIG0 clock-control tail, then defines:

- `DIG0_DIG_FE_EN_CNTL`, `DIG0_DIG_OUTPUT_CRC_CNTL`, `DIG0_DIG_OUTPUT_CRC_RESULT`, `DIG0_DIG_CLOCK_PATTERN`, `DIG0_DIG_TEST_PATTERN`, and `DIG0_DIG_RANDOM_PATTERN_SEED` for front-end enable, output CRC, deterministic/static/random test patterns, and FIFO controls.
- `DIG0_DIG_FIFO_CTRL0` and `DIG0_DIG_FIFO_CTRL1` for FIFO enable/reset, read-start level, output pixel mode, reset/error status, overwrite level, average/min/max calibration, and recalculation triggers.
- `DIG0_HDMI_METADATA_PACKET_CONTROL`, `DIG0_HDMI_CONTROL`, `DIG0_HDMI_STATUS`, `DIG0_HDMI_AUDIO_PACKET_CONTROL`, `DIG0_HDMI_ACR_PACKET_CONTROL`, and `DIG0_HDMI_VBI_PACKET_CONTROL` for HDMI metadata scheduling, scrambling, deep color, Dolby Vision flags, TMDS encoding/color format, AVMUTE/error status, ACR packet generation, and VBI packet sends.
- `DIG0_HDMI_GENERIC_PACKET_CONTROL0` through `CONTROL10`, plus `CONTROL5` and `CONTROL6`, for generic HDMI packet 0-14 sends, continuous mode, line references, line numbers, immediate-send pending bits, and enable double-buffer pending status.
- `DIG0_HDMI_DB_CONTROL` for HDMI/VUPDATE double-buffer pending/taken/clear/lock/disable control.
- `DIG0_HDMI_ACR_32_*`, `ACR_44_*`, `ACR_48_*`, and `ACR_STATUS_*` for CTS/N values and readback.
- `DIG0_AFMT_CNTL`, `DIG0_DIG_BE_CLK_CNTL`, `DIG0_DIG_BE_CNTL`, and `DIG0_DIG_BE_EN_CNTL` for audio formatter and backend clock/enable state.
- `DIG0_TMDS_*` registers for TMDS enable, control characters, sync patterns, stereo sync, control bits, DC balancer behavior, and per-control-symbol generation.

### DP1 DisplayPort Block

`DP1_DP_LINK_CNTL`, `DP1_DP_PIXEL_FORMAT`, `DP1_DP_MSA_COLORIMETRY`, `DP1_DP_CONFIG`, and `DP1_DP_VID_STREAM_CNTL` define base link, pixel encoding/depth, MSA miscellaneous colorimetry, lane count, video-stream enable/status/defer/keepout fields.

PHY and low-level link fields include:

- `DP1_DP_STEER_FIFO` for steer FIFO reset and overflow/TU overflow flags, interrupts, acknowledgements, masks, and TU size.
- `DP1_DP_DPHY_INTERNAL_CTRL`, `DP1_DP_DPHY_CNTL`, `DP1_DP_DPHY_TRAINING_PATTERN_SEL`, `DP1_DP_DPHY_SYM0..2`, `DP1_DP_DPHY_8B10B_CNTL`, `DP1_DP_DPHY_PRBS_CNTL`, and `DP1_DP_DPHY_SCRAM_CNTL` for alternate scrambler reset, FEC enable/readiness/status, ALPM FEC disable mode, scrambler selection/disable/advance, bypass/skew bypass, training pattern selection, symbol patterns, 8b/10b reset/disp, and PRBS setup.
- `DP1_DP_DPHY_CRC_CONTROL0/1`, `CRC_RESULT0..3`, `CRC_STATUS`, `FAST_TRAINING`, and `FAST_TRAINING_STATUS` for PHY CRC capture/validity/phase status and fast-training trigger/done fields.

Video timing and framing fields include `DP1_DP_VID_TIMING`, `DP1_DP_VID_N`, `DP1_DP_VID_M`, `DP1_DP_LINK_FRAMING_CNTL`, `DP1_DP_VID_MSA_VBID`, `DP1_DP_VID_INTERRUPT_CNTL`, `DP1_DP_MSA_MISC`, `DP1_DP_MSA_TIMING_PARAM1..4`, `DP1_DP_MSO_CNTL`, `DP1_DP_MSO_CNTL1`, and `DP1_DP_DSC_CNTL`. These expose M/N generation, enhanced frame mode, VBID/MSA placement, stream-disable interrupts, detailed MSA timing values, multi-stream output controls, and DSC mode.

Secondary-data and packet scheduling fields include:

- `DP1_DP_SEC_CNTL` and `DP1_DP_SEC_CNTL1..7` for ASP/ATP/AIP/ACM/MPG/ISRC/GSP0-11 enables, line reference/line number, send/send-any-line/send-in-idle, pending, active, deadline-missed, PPS, audio mute, collision status/ack, and enable double-buffer disable controls.
- `DP1_DP_SEC_FRAMING1..4`, `DP1_DP_SEC_AUD_N`, `DP1_DP_SEC_AUD_M`, readback registers, `DP1_DP_SEC_TIMESTAMP`, and `DP1_DP_SEC_PACKET_CNTL` for SDP frame/start/idle/hblank/vblank placement, audio M/N, timestamp mode, ASP coding type, priority, version, and channel count override.
- `DP1_DP_SEC_METADATA_TRANSMISSION` for metadata packet enable, line reference, MSO metadata enable, and packet line.

MST/MSE fields include `DP1_DP_MSE_RATE_CNTL`, `DP1_DP_MSE_RATE_UPDATE`, `DP1_DP_MSE_SAT0..2`, `DP1_DP_MSE_SAT_UPDATE`, `DP1_DP_MSE_LINK_TIMING`, `DP1_DP_MSE_MISC_CNTL`, and `DP1_DP_MSE_SAT0_STATUS..2_STATUS`. They define MSE rate numerator/denominator style fields, pending updates, source-to-slot allocation table entries for streams 0-5, encryption bits, slot counts, SAT update modes, 16-MTP keepout, link frame/line timing, blank/timestamp/zero-encoder behavior, and SAT readback status.

Power-management and diagnostics include `DP1_DP_ALPM_CNTL`, `DP1_DP_AUXLESS_ALPM_CNTL1..5`, `DP1_DP_DPIA_SPARE`, `DP1_DP_DB_CNTL`, `DP1_DP_MSA_VBID_MISC`, `DP1_DP_GSP8_CNTL..GSP11_CNTL`, `DP1_DP_GSP_EN_DB_STATUS`, and stream/link symbol counters. These fields cover ALPM sleep/standby send and pending states, wake/FEC timing, HW-mode state, wake interrupts, double-buffer state, VBID overrides, generic SDP 8-11 scheduling, and counters for stream blanking symbols, link SR symbols, and link cycles.

### DIG1 HDMI/TMDS Block

`DIG1_*` largely mirrors the DIG0 definitions in this chunk, adding `DIG1_DIG_FE_CNTL` at the start of the block and ending with `DIG1_DIG_DEBUG` and `DIG1_DIG_VERSION`. The repeated field families are front-end clock/enable, output CRC, test pattern, FIFO, HDMI metadata/control/status/audio/ACR/VBI/infoframe/generic packet control, HDMI DB control, AFMT, backend clock/control/enable, TMDS control characters, sync patterns, control bits, DC balancer, and TMDS control-symbol generation.

Because field names are instance-prefixed (`DIG1_...`) while internal field suffixes often match DIG0, the instance prefix is the important binding to the correct register address table.

### DP2 Start

The chunk ends at `DP2_DP_DPHY_FAST_TRAINING` and includes the same early DP fields seen for DP1: link control, pixel format, MSA colorimetry, lane config, video stream control, steer FIFO, MSA misc, DPHY internal control, video timing M/N, link framing, HBR2 eye pattern, MSA/VBID, video interrupt, DPHY control/training symbols/8b10b/PRBS/scrambler, and DPHY CRC control/status/result. Later DP2 secondary-data and ALPM fields are outside this chunk.

## APIs, Types, And Consumers

This header does not define C APIs or types. Its effective API is the stable naming convention:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

AMD display code consumes these values through generated register tables and helper macros. Nearby consumers include:

- `display/dc/inc/reg_helper.h`, where `FN`, `REG_SET`, `REG_UPDATE`, and `REG_GET` combine register addresses with shift/mask entries.
- `display/dmub/src/dmub_reg.h`, which has a parallel `FD`/`FN` and `REG_*` helper layer for DMUB-side register access.
- DCN 3.6 users that include this exact header: `display/dmub/src/dmub_dcn36.c`, `display/dc/irq/dcn36/irq_service_dcn36.c`, and `display/dc/resource/dcn36/dcn36_resource.c`.
- DIO stream/link encoder headers and sources such as `display/dc/dce/dce_stream_encoder.h`, `display/dc/dce/dce_stream_encoder.c`, and newer `display/dc/dio/dcn*_dio_stream_encoder.h`, which map fields like HDMI generic packet sends/lines and DP secondary packet/GSP enables into per-encoder register structs.

The field constants must also align with the address-register header for the same ASIC generation, typically `dcn_3_6_0_offset.h`, and with resource macros that instantiate per-DIG/per-DP address arrays.

## Control Flow

There is no local control flow. In runtime code, the typical flow is:

1. A DCN 3.6 resource or encoder constructor selects the DCN 3.6 register, shift, and mask tables.
2. A stream/link encoder operation calls a helper such as `REG_UPDATE`, `REG_UPDATE_N`, `REG_SET`, or `REG_GET`.
3. The helper resolves a field by name to this header's shift/mask constants and the companion address constant.
4. The helper reads, masks, shifts, and writes the MMIO register or extracts a status field.

For fields in this chunk, that runtime flow controls HDMI infoframe/generic packets, HDMI ACR/deep-color/scrambling, TMDS legacy/link behavior, DP stream enablement, DP PHY training/CRC/test patterns, DP secondary packet scheduling, DP MST slot allocation, DP ALPM state changes, and status counter reads.

## State And Persistence Behavior

The header itself is stateless and has no persistence. The constants describe persistent hardware register bits whose values live in display engine registers until reset, power-gated, or overwritten by the driver/firmware. State-bearing fields in this chunk include:

- Enable bits such as `DIG*_DIG_FE_ENABLE`, `HDMI_METADATA_PACKET_ENABLE`, `DP_VID_STREAM_ENABLE`, `DP_SEC_STREAM_ENABLE`, `DP_DSC_MODE`, and ALPM HW-mode enables.
- Request/pending/status/ack fields such as HDMI generic immediate-send pending bits, HDMI/DP double-buffer pending/taken bits, DP secondary-packet pending/active/deadline-missed fields, DP MSE rate update pending, DP ALPM wake/FEC pending/status, and DPHY CRC valid/phase error acknowledgements.
- Readback/counter fields such as ACR CTS/N status, DP SAT status, DP stream symbol counts, DP link SR/cycle counts, CRC results, FIFO status, and version/debug fields.

Drivers using these fields must respect hardware sequencing. A mask/shift typo can silently target the wrong bit and leave display hardware in a stale or inconsistent state across modesets, link training, hotplug handling, or runtime power transitions.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register namespace being internally consistent:

- Register address macros for `DIG0`, `DIG1`, `DP1`, and `DP2` must use matching register names and instance numbering.
- Field list macros in DIO/DCE resource headers must refer to fields that exist in this header. For example, searches show resource and encoder code referencing HDMI generic packet registers, TMDS control bits, DP secondary GSP fields, DP MSE SAT fields, and ALPM-related DP fields.
- The shift and mask pairs must be compatible: every field should have the same bit position in `__SHIFT` that its mask implies. Many one-bit fields use masks such as `0x00000010L` with shifts such as `0x4`; multi-bit fields like line numbers, M/N values, slot counts, and timing parameters expose wider masks.
- Instance-specific fields use `DIG0_`, `DIG1_`, `DP1_`, and `DP2_` prefixes. Generic consumer macros often remove or remap instance prefixes through resource macros, so the prefix/address pairing is critical.

The header is indirectly integrated into Linux DRM/KMS behavior through AMD DC stream encoding, link encoding, DP MST, HDMI infoframes, audio packet scheduling, DSC/PPS transport, link training, interrupt service, and DMUB interactions.

## Risks And Edge Cases

- Generated-header drift: if `dcn_3_6_0_sh_mask.h` diverges from the matching offset/header tables, helpers can write valid-looking fields to the wrong register address or bit lane.
- Copy/paste instance errors: DIG0 and DIG1, and DP1 and DP2, are near duplicates. A single wrong prefix or missing field in one instance can break only one connector/encoder instance and be hard to detect in single-display testing.
- Write-one-to-clear and ack semantics: fields named `*_ACK`, `*_CLR`, `*_STATUS`, `*_PENDING`, and `*_DEADLINE_MISSED` should not be treated as ordinary read/write state by higher-level code. Incorrect read-modify-write sequences can clear interrupts or leave pending bits stuck.
- Double-buffer timing: HDMI and DP `*_DB_*`, `*_EN_DB_PENDING`, and `VUPDATE_DB_*` fields imply synchronized update behavior. Misusing masks can apply packet or stream changes on the wrong vertical update boundary.
- Link-training and PHY diagnostics: DP DPHY training, PRBS, scrambler, CRC, and fast-training fields can disrupt active links if written outside expected training/debug paths.
- MST allocation: `DP_MSE_SAT*` source, encryption, and slot count fields define payload allocation. Incorrect shifts or consumers can route slots to the wrong stream or corrupt MST bandwidth accounting.
- ALPM sequencing: sleep, standby, wake, FEC enable, AUX-less timing, and interrupt fields affect low-power link transitions; mistakes can cause black screens, wake failures, or intermittent link loss.
- Chunk boundary risk: this slice starts after the beginning of DIG0 and ends at the start of DP2 fast training. Cross-chunk reconciliation must include adjacent chunks to understand complete DIG0 and DP2 coverage.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/display integration signals:

- Build the AMDGPU display driver with DCN 3.6 enabled; missing or renamed macros should fail compilation in resource, IRQ, DMUB, or DIO code that includes `dcn_3_6_0_sh_mask.h`.
- Run static consistency checks comparing `__SHIFT` values against masks, checking that `(mask >> shift)` forms a contiguous field for non-reserved fields.
- Compare DIG0/DIG1 and DP1/DP2 repeated field families for expected symmetry, allowing only known generation/instance differences.
- Exercise HDMI modes with deep color, scrambling, infoframes, metadata packets, AVMUTE, audio ACR, and generic packets; watch for packet deadline/pending/status anomalies.
- Exercise DisplayPort SST and MST modes, including DSC/PPS secondary packets, GSP scheduling, MSE SAT updates, DP audio M/N, link training, FEC, CRC diagnostics, and stream/link symbol counter reads.
- Exercise ALPM and AUX-less ALPM paths on supported panels/links, checking sleep/wake/FEC pending/status fields and display resume reliability.
- Monitor DRM logs and hardware status reads for FIFO errors, steer/TU overflow, secondary-packet deadline misses, double-buffer pending bits that never clear, and DPHY CRC phase errors.

## Open Questions For Merge Lane

- Adjacent chunks should confirm the complete DIG0 block before line 32580 and the remaining DP2 secondary-data/MST/ALPM fields after line 34984.
- The final per-file report should identify the generator source, if present in the repository, because this file is generated and should normally be fixed at generator/input data level rather than by hand editing the header.
