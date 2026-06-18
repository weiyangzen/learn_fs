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
