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
