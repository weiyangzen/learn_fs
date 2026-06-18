# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 35012-37422

## Scope

This chunk is part of AMDGPU DCN 3.1.5 generated register metadata. It contains C preprocessor constants for register field shifts and masks, not executable code. The exact chunk spans line 35012 through line 37422 of `dcn_3_1_5_sh_mask.h`; line 35012 starts mid-register with the `DIG2_HDMI_GC__HDMI_PACKING_PHASE_OVERRIDE_MASK` constant, and line 37422 ends mid-register inside `DP4_DP_SEC_METADATA_TRANSMISSION`.

The definitions are consumed by AMD display driver register access helpers that combine an address header with these `__SHIFT` and `_MASK` constants to read, write, and update individual DCN register fields. The values are hardware ABI: they encode bit positions in the DCN display I/O, HDMI/TMDS, DisplayPort, secondary packet, MST/MSE, DSC, CRC, and double-buffer control registers.

## Purpose

The purpose of this chunk is to expose bitfield layout for several display encoder instances:

- Tail of the `DIG2` HDMI/TMDS back-end block, including HDMI generic packet line selection, HDMI double-buffer status/control, HDMI audio clock regeneration values, AFMT audio clock gating, DIG back-end enable/source selection, TMDS control-symbol generation, sync patterns, and forced DIG disable.
- Complete `DP3` DisplayPort register field set for the `dce_dc_dio_dp3_dispdec` address block, covering link control, pixel/MSA/video timing, DPHY training and test controls, secondary data packets, MST stream allocation, DSC, ALPM, GSP8-GSP11, and double-buffer status.
- Complete `DIG3` front-end/back-end HDMI/TMDS register field set for the `dce_dc_dio_dig3_dispdec` address block, covering DIG front-end control, output CRC/test pattern/FIFO status, HDMI metadata/control/status, generic packet scheduling, TMDS generation, and back-end enable/source selection.
- Start-to-tail `DP4` DisplayPort register field set for the `dce_dc_dio_dp4_dispdec` address block through the first three fields of `DP4_DP_SEC_METADATA_TRANSMISSION`.

These constants let common DC code address replicated hardware pipes by selecting a register block (`DIG2`, `DIG3`, `DP3`, `DP4`) while using stable field names for the operations.

## Important Definitions

The public surface is macro-only. Every meaningful item has one of two forms:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset for the field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for the same field.

Important groups in this chunk:

- HDMI generic packet controls for `DIG2` and `DIG3`: `HDMI_GENERIC_PACKET_CONTROL0/1/2/3/4/5/6/7/8/9/10` define send, continuous send, line reference, update-lock-disable, immediate-send, immediate-send-pending, line number, and enable-double-buffer-pending bits for generic packets 0-14. `DIG2` has only the tail of this group in this chunk; `DIG3` has the full group.
- HDMI packet/status controls: `HDMI_CONTROL`, `HDMI_STATUS`, `HDMI_AUDIO_PACKET_CONTROL`, `HDMI_ACR_PACKET_CONTROL`, `HDMI_VBI_PACKET_CONTROL`, `HDMI_INFOFRAME_CONTROL0/1`, `HDMI_GC`, `HDMI_DB_CONTROL`, and ACR N/CTS registers define data scrambling, deep color, AVMUTE, audio/VBI packet triggers, infoframe line numbers, ACR sample-rate parameters, and vupdate/double-buffer handshakes.
- DIG/TMDS controls: `DIG_FE_CNTL`, `DIG_BE_CNTL`, `DIG_BE_EN_CNTL`, `DIG_OUTPUT_CRC_*`, `DIG_TEST_PATTERN`, `DIG_FIFO_STATUS`, `TMDS_*`, and `FORCE_DIG_DISABLE` define frontend start/symclk state, Dolby Vision metadata status, back-end source and HPD selection, output CRC selection/result, test pattern generation, FIFO calibration/error fields, TMDS control character generation, DC balance, sync characters, and control-lane data selection.
- DisplayPort link/video/DPHY controls for `DP3` and `DP4`: `DP_LINK_CNTL`, `DP_PIXEL_FORMAT`, `DP_CONFIG`, `DP_VID_STREAM_CNTL`, `DP_STEER_FIFO`, `DP_MSA_*`, `DP_VID_*`, `DP_DPHY_*`, and `DP_LINK_FRAMING_CNTL` define stream enable, pixel encoding, MSA timing/colorimetry, VBID/MSA location, FIFO overflow reporting, lane test patterns, FEC, scrambler, 8b/10b, PRBS, CRC, MST CRC slot selection, and fast training.
- DisplayPort secondary packet and audio controls: `DP_SEC_CNTL`, `DP_SEC_CNTL1` through `DP_SEC_CNTL7`, `DP_SEC_FRAMING1` through `DP_SEC_FRAMING4`, `DP_SEC_AUD_N/M`, readbacks, timestamp mode, `DP_SEC_PACKET_CNTL`, and `DP_SEC_METADATA_TRANSMISSION` define ASP/ATP/AIP/ACM/GSP/MPG/ISRC enables, send/pending/deadline/idle status, packet framing windows, audio N/M values, coding type, metadata packet enable, and line references.
- MST/MSE/MSO and DSC controls: `DP_MSE_RATE_*`, `DP_MSE_SAT*`, `DP_MSE_SAT*_STATUS`, `DP_MSE_LINK_TIMING`, `DP_MSO_CNTL*`, `DP_DSC_CNTL`, and `DP_DSC_BYTES_PER_PIXEL` define stream allocation table entries, encryption flags, slot counts, update status, link timing, multi-stream-output secondary packet enables, DSC mode/slice width, and bytes-per-pixel.
- Low-power and extra GSP controls: `DP_ALPM_CNTL`, `DP_GSP8_CNTL` through `DP_GSP11_CNTL`, and `DP_GSP_EN_DB_STATUS` are visible for `DP3`, defining PHY sleep/standby signaling and extended generic secondary packet scheduling. The `DP4` part of this chunk does not reach the corresponding GSP8-GSP11 section before the chunk ends.

## Control Flow and State

There is no runtime control flow in this header. Runtime behavior emerges when driver code includes this file and passes these constants to register helpers. Typical flow is:

1. The driver selects a display encoder/link instance and a register address from the matching DCN 3.1.5 address header.
2. It prepares a field value by shifting it by `<REGISTER>__<FIELD>__SHIFT` and masking with `<REGISTER>__<FIELD>_MASK`, usually through local register helper macros rather than manual arithmetic.
3. It writes a memory-mapped register or reads one and extracts the field with the same shift/mask pair.
4. Hardware state changes asynchronously, and status fields such as `*_PENDING`, `*_TAKEN`, `*_ACTIVE`, `*_DEADLINE_MISSED`, `*_RESULT_VALID`, `*_FIFO_LEVEL_ERROR`, and `*_FAST_TRAINING_COMPLETE_OCCURRED` are observed by later driver reads.

The chunk describes several stateful hardware protocols:

- Double buffering: `DIG*_HDMI_DB_CONTROL`, `DP*_DP_DB_CNTL`, `HDMI_GENERIC*_EN_DB_PENDING`, `DP_SEC_GSP*_EN_DB_DISABLE`, and `DP_GSP_EN_DB_STATUS` govern or report when updates are pending, taken, locked, disabled, or synchronized to vupdate.
- Packet scheduling: HDMI generic packets and DP secondary/GSP packets have send, continuous, immediate, pending, active, deadline missed, idle-send, line-reference, and line-number fields. Driver sequencing must account for pending bits and missed-deadline status before assuming packet delivery.
- Link training and DPHY test state: `DP_DPHY_FAST_TRAINING*`, `DP_DPHY_TRAINING_PATTERN_SEL`, CRC, PRBS, 8b/10b, HBR2 pattern, and BS/SR swap fields describe hardware modes where writes initiate training/test actions and reads confirm completion/status.
- Stream allocation and timing: `DP_MSE_SAT*`, `DP_MSE_RATE_*`, `DP_MSO_CNTL*`, `DP_MSA_TIMING_PARAM*`, and `DP_VID_*` fields persist as programmed register state controlling current video and MST/MSO stream behavior.

## Dependencies and Integration Points

This header depends on the generated AMD ASIC register naming contract. It is useful only alongside:

- The corresponding DCN 3.1.5 register address definitions that name the same registers without the `__FIELD` suffix.
- AMDGPU display register helper macros/functions that accept register fields as shift/mask pairs, such as the DC `REG_GET`, `REG_SET`, `REG_UPDATE`, or similar generated macro layers used elsewhere in the driver.
- DC link encoder, stream encoder, audio, HDMI, DP, MST, DSC, and diagnostics code that needs per-generation field layouts.

Integration is intentionally compile-time. These macros become literal constants in C expressions, so there is no symbol linkage or persistence within the header itself. The persistence is in hardware registers after memory-mapped writes.

The replicated prefixes matter for integration:

- `DIG2` and `DIG3` identify separate digital encoder instances.
- `DP3` and `DP4` identify separate DisplayPort link/PHY instances.
- Shared suffixes with identical masks across `DP3` and `DP4` allow common code to operate on indexed register tables while preserving per-instance register names.

## Risks and Edge Cases

- Generated-header drift is the main risk. If a mask or shift is wrong, the driver can silently program the wrong bitfield, causing display blanking, packet loss, audio issues, failed link training, incorrect DSC/MST allocation, or missed interrupts.
- Chunk boundaries are not semantic boundaries. This chunk starts after the `DIG2_HDMI_GC` shift constants and ends before the `DP4_DP_SEC_METADATA_TRANSMISSION` mask constants. A per-file merge must combine neighboring chunks before making whole-register claims about those two registers.
- Field names ending in `MASK_MASK`, such as `DPHY_CRC_MASK_MASK` and `DPHY_FAST_TRAINING_COMPLETE_MASK_MASK`, are intentional generated names for fields named `*_MASK`; reviewers should not simplify them without changing all users.
- Several fields represent write-one-to-clear or handshake behavior by name (`*_ACK`, `*_CLR`, `*_PENDING`, `*_TAKEN`). The header does not encode access semantics; driver code and hardware documentation must enforce correct read/write sequencing.
- Many packet-line fields are 16-bit or 6-bit line selectors. Passing out-of-range values through raw helpers can truncate into neighboring fields if callers do not mask/validate before update.
- The `DP3` and `DP4` blocks are similar but not identical in this chunk due to chunk truncation and because `DP3` includes `DP_DSC_BYTES_PER_PIXEL`, `DP_ALPM_CNTL`, and `DP_GSP8` through `DP_GSP11` before `DIG3`; `DP4` does not reach those definitions here. Merge logic should avoid interpreting absence in this chunk as absence from the full source file.

## Test Signals

There are no unit-testable functions in this chunk. Useful validation signals are structural and integration-focused:

- Compile coverage: AMDGPU/DC code that includes `dcn_3_1_5_sh_mask.h` must build with no undefined register-field macros for DCN 3.1.5.
- Generated consistency checks: for each field, the mask should align with the shift and expected width; duplicated `DP3`/`DP4` and `DIG2`/`DIG3` register families should keep identical field layouts where the hardware block is replicated.
- Runtime display validation: HDMI and DP modes should light up across affected links, with audio infoframes/ACR, generic packets, DSC, MST/MSO, and fast training paths exercised.
- Diagnostics: CRC/test-pattern/PRBS paths and FIFO/overflow/error status fields can be checked with display test tooling or kernel debug traces.
- Hardware handshakes: tests should observe that `*_PENDING`, `*_TAKEN`, `*_ACTIVE`, `*_DEADLINE_MISSED`, and `*_RESULT_VALID` bits transition as expected after the corresponding driver writes.

## Chunk Notes for Merge Lane

- This chunk contains 2,411 source lines and 2,168 `#define` lines by prefix distribution: 221 `DIG2`, 756 `DP3`, 560 `DIG3`, and 631 `DP4`.
- The merge lane should combine this with adjacent chunks before writing the final per-file research document for `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h`.
- The chunk has no local includes, typedefs, structs, enums, functions, or writable software state.
