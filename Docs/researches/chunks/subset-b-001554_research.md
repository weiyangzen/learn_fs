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
