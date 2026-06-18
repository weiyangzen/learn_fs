# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 37371-39761

## Scope

This chunk covers 2,391 lines from the generated DCN 3.1.2 display register shift/mask header. It contains preprocessor constants and generated register-group comments only; there are no C functions, structs, enums, storage definitions, branches, loops, or local algorithms in this range.

The range starts in the middle of `DP3_DP_DPHY_SYM0`, after the `DPHY_SYM1` mask and before the remaining `DPHY_SYM2`/`DPHY_SYM3` masks. It then covers the tail of the DisplayPort 3 link/secondary-data-packet surface, the full `dce_dc_dio_dig3_dispdec` digital encoder and HDMI/TMDS surface, the full `dce_dc_dio_dp4_dispdec` DisplayPort 4 surface, and the beginning of `dce_dc_dio_dig4_dispdec`. It ends inside `DIG4_HDMI_GENERIC_PACKET_CONTROL5`, after generic packet 8 immediate-send pending mask; masks for generic packets 9 through 14 continue in the next chunk.

The chunk contains 2,174 `#define` entries: 1,092 `__SHIFT` definitions and 1,090 `_MASK` definitions. The uneven count is expected for this slice because it begins and ends inside register groups. Generated comments identify register blocks for the DP3 tail, `DIG3`, full `DP4`, and early `DIG4`.

## Purpose

This header slice gives DCN 3.1.2 AMD display code symbolic bit offsets and bit masks for DisplayPort and digital encoder register fields. Runtime code pairs these constants with the matching offset header and AMD display register helpers to construct MMIO read/modify/write operations without embedding literal bit arithmetic at call sites.

For `DP3`, the chunk covers the lower-level DisplayPort PHY and stream-control tail: DPHY training symbols, 8b/10b state, PRBS and scrambler controls, CRC controls and results, MST CRC phase status, fast-training controls/status, secondary-data-packet enablement and framing, audio N/M values and readbacks, packet coding and channel-count override, multi-stream encoder rate and slot-allocation table controls/status, MSA timing parameters, MSO controls, DSC enablement, double-buffer controls, VBID misc, SDP metadata transmission, DSC bytes-per-pixel, ALPM controls, and GSP8 through GSP11 controls/status.

For `DIG3`, the chunk maps the digital encoder instance that can drive HDMI/TMDS style output paths. It includes front-end source selection and start state, output CRC generation, clock/test/random patterns, FIFO status, HDMI metadata and control/status fields, audio and ACR packet controls, VBI and infoframe scheduling, generic HDMI packet send/continue/line/update-lock/immediate-send controls, DB control, audio clock regeneration values for 32/44.1/48 kHz families, AFMT controls, back-end enablement, TMDS control characters, sync patterns, DC balancer controls, TMDS generated-control bits, version, and force-disable controls.

For `DP4`, the chunk covers a complete DisplayPort transmitter instance. It maps link status/training state, pixel format and colorimetry, DP configuration and video stream control, FIFO steering, MSA misc/timing/VBID fields, DPHY internal controls, video timing and M/N values, link framing, HBR2 eye pattern and test controls, video interrupts, DPHY training/scrambler/CRC/fast-training controls, secondary-data-packet and audio timing controls, MST/MSE rate and slot-allocation controls/status, MSO controls, DSC controls, packet double-buffering, metadata transmission, DSC byte-per-pixel fields, ALPM controls, and GSP8 through GSP11 packet controls/status.

For `DIG4`, the chunk begins the next digital encoder instance and maps its front-end/output-CRC/test-pattern/FIFO fields plus the early HDMI packet-control surface through the first half of `HDMI_GENERIC_PACKET_CONTROL5`.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated preprocessor naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field's 32-bit mask.
- Comments such as `// addressBlock: dce_dc_dio_dp4_dispdec`, `//DP4_DP_LINK_CNTL`, and `//DIG3_HDMI_CONTROL` group constants by generated hardware block and register.

Important `DP3` register families in this range include:

- `DP3_DP_DPHY_*`: symbol pattern words, 8b/10b reset/disparity fields, PRBS enable/select/seed fields, scrambler disable/advance/BS count/K-code fields, CRC enable/control/result fields, MST CRC phase-lock/error/ack fields, and fast-training capability/start/timing/status fields.
- `DP3_DP_SEC_*`: secondary-data-packet stream/ASP/ATP/AIP/ACM/GSP/MPG enables, GSP0 scheduling and pending/deadline status, SDP framing positions and widths, audio mute/collision status, audio N/M and readback fields, timestamp mode, packet coding type, packet priority, SDP version, and audio channel-count override.
- `DP3_DP_MSE_*`: MST multi-stream encoder rate numerator/denominator fields, rate-update pending state, SAT source/slot-count fields, SAT update controls, link-frame/link-line timing, blank-code/timestamp/zero-encoder controls, and SAT status readbacks.
- `DP3_DP_MSA_*`, `DP3_DP_MSO_*`, and `DP3_DP_DSC_*`: main stream attribute timings, MSO segment/link-count/enable controls, and DSC mode/bytes-per-pixel fields.
- `DP3_DP_ALPM_CNTL` and `DP3_DP_GSP8_CNTL` through `DP3_DP_GSP11_CNTL`: ALPM pattern/symbol/error-status fields and extended generic SDP line, send, pending, and update controls.

Important `DIG3` register families include:

- `DIG3_DIG_FE_CNTL`, `DIG3_DIG_BE_CNTL`, and `DIG3_DIG_BE_EN_CNTL`: source selection, stereo sync, start, bypass, input-pixel selection, Dolby Vision enable/missed status, symbol-clock state, TMDS pixel/color encoding, back-end mode, and enable state.
- `DIG3_DIG_OUTPUT_CRC_*`, `DIG3_DIG_CLOCK_PATTERN`, `DIG3_DIG_TEST_PATTERN`, `DIG3_DIG_RANDOM_PATTERN_SEED`, and `DIG3_DIG_FIFO_STATUS`: diagnostic output CRC, clock/test-pattern generation, random-pattern seed, and FIFO overflow/underflow/depth/sync status fields.
- `DIG3_HDMI_*`: metadata packet controls, HDMI enable/deep-color/packing/reorder/scrambler/control-period controls, HDMI status, audio packet enable/continue fields, ACR packet source/send/continue/select controls, VBI null/general-control/ISRC send controls, audio and MPEG infoframe send/line controls, generic packet controls 0 through 14, immediate-send pending bits, generic packet line controls, DB control, ACR N/CTS programming/status for 32 kHz, 44.1 kHz, and 48 kHz bases, and HDMI general-control fields.
- `DIG3_AFMT_CNTL` and `DIG3_TMDS_*`: AFMT audio/HDMI state and forced audio-clock controls plus TMDS modulation, control-character, sync-character, stereo-sync, control-bit, DC-balancer, and generated-control fields.

Important `DP4` register families include:

- `DP4_DP_LINK_CNTL`, `DP4_DP_PIXEL_FORMAT`, `DP4_DP_MSA_COLORIMETRY`, `DP4_DP_CONFIG`, `DP4_DP_VID_STREAM_CNTL`, `DP4_DP_STEER_FIFO`, and `DP4_DP_MSA_MISC`: link-training completion/status, embedded-panel mode, component depth, pixel encoding, dynamic range, colorimetry, stereo/alternate-scrambler/DP clock settings, stream enable/mode/start/stop, FIFO steering, and MSA misc values.
- `DP4_DP_DPHY_INTERNAL_CTRL`, `DP4_DP_DPHY_CNTL`, `DP4_DP_DPHY_TRAINING_PATTERN_SEL`, `DP4_DP_DPHY_SYM*`, `DP4_DP_DPHY_8B10B_CNTL`, `DP4_DP_DPHY_PRBS_CNTL`, `DP4_DP_DPHY_SCRAM_CNTL`, `DP4_DP_DPHY_CRC_*`, and `DP4_DP_DPHY_FAST_TRAINING*`: PHY ownership, link clock controls, bypass/skew settings, training symbols, scrambler/PRBS/CRC diagnostics, MST CRC phase status, and fast-training state.
- `DP4_DP_VID_TIMING`, `DP4_DP_VID_N`, `DP4_DP_VID_M`, `DP4_DP_LINK_FRAMING_CNTL`, `DP4_DP_HBR2_EYE_PATTERN`, `DP4_DP_VID_MSA_VBID`, and `DP4_DP_VID_INTERRUPT_CNTL`: stream timing, M/N generation, link framing, HBR2 eye-pattern testing, VBID, and video interrupt status/mask/ack controls.
- `DP4_DP_SEC_*`, `DP4_DP_MSE_*`, `DP4_DP_MSA_TIMING_PARAM*`, `DP4_DP_MSO_*`, `DP4_DP_DSC_*`, `DP4_DP_DB_CNTL`, `DP4_DP_MSA_VBID_MISC`, `DP4_DP_SEC_METADATA_TRANSMISSION`, `DP4_DP_ALPM_CNTL`, and `DP4_DP_GSP*`: packetization, audio timing, MST/MSE, MSA timing, multi-stream output, DSC, double-buffering, metadata, ALPM, and generic SDP fields for the fourth DP transmitter.

Important `DIG4` register families in this partial range mirror the early `DIG3` surface: `DIG4_DIG_FE_CNTL`, output CRC, test-pattern, FIFO, HDMI metadata/control/status, audio/ACR/VBI/infoframe packet controls, and generic packet controls through the first half of `DIG4_HDMI_GENERIC_PACKET_CONTROL5`.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time symbol resolution:

1. DCN 3.1.2 display code includes `dcn_3_1_2_sh_mask.h` together with the matching DCN 3.1.2 offset header.
2. AMD display register helper macros concatenate register and field tokens to resolve `__SHIFT` and `_MASK` constants.
3. Runtime MMIO paths use the resolved constants to insert, update, or extract hardware register fields.

The declaration order follows the generated hardware register order. The range starts inside `DP3_DP_DPHY_SYM0`, continues through the rest of the DP3 display transmitter fields covered by this generated address block, enters `dce_dc_dio_dig3_dispdec`, then `dce_dc_dio_dp4_dispdec`, then starts `dce_dc_dio_dig4_dispdec`. Within complete register groups, shift macros normally precede mask macros for the same fields.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes bit layout for state stored in DCN 3.1.2 display hardware:

- DisplayPort link and DPHY fields describe programmed training, scrambling, PRBS, CRC, 8b/10b, link-framing, timing, and diagnostic state.
- DisplayPort video, MSA, M/N, VBID, MSO, DSC, and ALPM fields describe stream format, stream timing, transport framing, compression, and low-power link behavior.
- Secondary-data-packet, audio N/M, generic SDP, and HDMI generic packet fields describe packet enablement, scheduling, immediate-send requests, pending status, line references, metadata transmission, and audio clock generation.
- HDMI/TMDS fields describe encoder mode, deep color, audio/infoframe/VBI packet scheduling, ACR values, TMDS control characters, sync patterns, and DC-balance behavior.
- CRC, FIFO, interrupt, status, pending, collision, phase-error, and readback fields describe hardware-observed state that can change asynchronously with link training, hotplug, stream enablement, packet transmission, and diagnostic operations.

Persistence is hardware-defined. Writable fields may remain programmed until driver reconfiguration, stream disable, display block reset, suspend/resume restore, or ASIC reset. Status and pending fields may be volatile, sticky, masked, or acknowledge-driven depending on the underlying register semantics; this generated shift/mask header does not encode access permissions, reset values, side effects, or write-one-to-clear rules.

## Dependencies And Integration Points

This chunk depends on generated DCN 3.1.2 register files staying synchronized:

- `dcn_3_1_2_offset.h` supplies the matching register offsets and base indices. Examples near this chunk include `regDP3_DP_DPHY_SYM0` at `0x2419`, `regDIG3_DIG_FE_CNTL` at `0x238b`, `regDP4_DP_LINK_CNTL` at `0x2508`, and `regDIG4_HDMI_GENERIC_PACKET_CONTROL5` at `0x249c`, all with base index `2`.
- AMD display register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT` rely on the exact generated suffix convention used here.
- DisplayPort link training, MST allocation, DSC, ALPM, audio packetization, HDMI packet scheduling, TMDS programming, diagnostics, interrupt handling, and power-management paths integrate with these constants when programming or reading the DCN display engines.
- The generated register database remains the source of truth for legal values, access modes, reset values, and sequencing constraints. This file only captures numeric bit positions and masks.

The main integration contract is preprocessor naming. Missing or renamed fields typically fail at compile time when helper macros expand, while wrong numeric masks or shifts can compile cleanly and produce incorrect MMIO reads or writes.

## Risks And Edge Cases

- The chunk starts and ends mid-register group. `DP3_DP_DPHY_SYM0` must be completed from the previous chunk, and `DIG4_HDMI_GENERIC_PACKET_CONTROL5` must be completed from the next chunk before whole-register conclusions are made.
- The `DP3` and `DP4` blocks are highly repetitive. A generated prefix, endpoint number, or field-width mismatch can be hard to notice because most lines differ only by transmitter instance.
- `DIG3` and early `DIG4` HDMI/TMDS fields are similarly repetitive. Confusing encoder instances can program the wrong output path while leaving the intended path unchanged.
- Full-width or high-bit masks such as `0xFFFFFFFFL`, `0xFF000000L`, `0xC0000000L`, and `0x80000000L` require unsigned-safe handling in consumers. Signed temporary values can corrupt comparisons or shifts.
- Control and status fields use the same macro style. The header cannot prevent callers from writing read-only status fields, missing required acknowledges, or treating pending/status bits as ordinary configuration.
- Packet send and immediate-send fields are side-effect prone. Incorrect writes can schedule HDMI generic packets, SDPs, infoframes, ISRC packets, or audio packets at the wrong time or on the wrong line.
- MST/MSE slot-allocation and rate fields are compact and instance-specific. Wrong masks can corrupt adjacent source/slot fields or create invalid bandwidth allocation.
- Link training, PRBS, scrambler, CRC, fast-training, and HBR2 pattern controls are diagnostic or sequencing-sensitive. Programming them outside the expected link-training flow can disrupt active streams.
- DSC, MSO, ALPM, and metadata fields interact with stream capabilities and sink/link state. A bitfield definition may be numerically correct but still unsafe to use without the proper higher-level capability checks.
- Cross-generation reuse is risky. DCN 3.1.2 layouts are close to neighboring DCN generations, but code must include the offset and shift/mask headers that match the target ASIC.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration oriented:

- Build AMDGPU DCN 3.1.2 display code that includes this header to catch missing macro names in register-helper expansions.
- Preprocess representative users of `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE` for DP3, DP4, DIG3, and DIG4 fields to confirm the expected constants resolve.
- Compare this file with `dcn_3_1_2_offset.h` and the generated register database to ensure register offsets and field masks remain paired for each transmitter and digital encoder instance.
- Exercise DP link training and retraining on DCN 3.1.2 hardware, watching link status, DPHY training, scrambler, fast-training, CRC, and video interrupt fields for plausible transitions.
- Test MST configurations that use MSE rate and SAT programming, including multi-stream slot updates and SAT status readback.
- Exercise DSC, MSO, ALPM, and SDP metadata paths with capable sinks, checking that DP4 fields produce correct stream bring-up and that DB/status bits settle as expected.
- Validate HDMI/DIG3 output modes including deep color, audio, ACR, infoframes, VBI packets, generic packets, TMDS encoding, output CRC, and FIFO status.
- Validate DIG4 paths covered by this partial chunk in the same way, but defer full generic-packet-control conclusions until the next chunk completes `DIG4_HDMI_GENERIC_PACKET_CONTROL5`.
- Run suspend/resume, display reset, hotplug, and mode-set tests to ensure programmed DP, HDMI, packet, audio, and diagnostic state is restored or re-read correctly.

## Open Cross-Chunk Questions

- The merge lane should combine this with the previous chunk to complete the beginning of `DP3_DP_DPHY_SYM0`.
- The merge lane should combine this with the next chunk to complete `DIG4_HDMI_GENERIC_PACKET_CONTROL5` and the rest of the DIG4 HDMI/TMDS block.
- Whole-file analysis should verify all DP and DIG instance counts for DCN 3.1.2 and compare the repeated instance layouts against the authoritative generated register source.
