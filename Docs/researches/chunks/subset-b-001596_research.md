# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 37196-39642

## Scope

This chunk is an interior slice of AMDGPU's generated DCN 1.0 register shift/mask header. It contains only preprocessor definitions: no functions, structs, enums, storage, or executable C logic. The exported surface is a set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants that describe bit positions inside display-controller MMIO registers.

The range covers 2447 source lines and 2161 `#define` lines. It starts at `DIG5_AFMT_ISRC1_0`, after earlier DIG5 HDMI/AFMT packet-control definitions, and ends inside `DP6_DP_SEC_CNTL2`, after the first generic-secondary-packet masks. The final per-file reconciliation should treat those start/end points as chunk boundaries, not source omissions.

## Purpose

The macros describe the bit layout for late DCN 1.0 DIO instance 5 and early/mid DIO instance 6 display output blocks:

- Tail of `DIG5` audio formatter and HDMI/TMDS support, including ISRC/UPC/EAN bytes, generic HDMI packet controls, double-buffer control, MPEG infoframe bytes, generic packet payload bytes, audio clock regeneration values, audio info packets, IEC 60958 channel-status words, audio CRC, ramp generator controls, AFMT status, packet controls, audio source selection, backend enable controls, TMDS control-symbol generation, lane enable, and AFMT clock control.
- Complete `DP5` DisplayPort stream/link register fields, including link status, pixel format, MSA colorimetry/misc/timing metadata, video timing `M/N`, link framing, HBR2/test pattern controls, VBID and interrupts, DPHY training/PRBS/scrambler/CRC controls, secondary-data packet controls, audio `N/M` values, timestamping, MST/MSE allocation tables, Multi-Stream Operation controls, DSC enable, generic secondary-packet send state, debug controls, and MSA VBID miscellaneous status.
- Most of `DIG6`, beginning at `DIG6_DIG_FE_CNTL` and continuing through the same HDMI/audio/TMDS/AFMT register families seen for DIG5.
- Beginning of `DP6`, from DisplayPort link and stream programming through `DP6_DP_SEC_CNTL2` generic secondary-packet send fields.

These constants are an ABI-like contract between generated ASIC register data and AMDGPU display code. The companion offset header gives the register addresses, while this file gives each field's packed bit position and mask.

## Important Macro Families

Every normal field appears as a pair:

- `REGISTER__FIELD__SHIFT`: the low bit for a field.
- `REGISTER__FIELD_MASK`: the already-positioned field mask.

The `DIG5_*` and `DIG6_*` groups describe digital encoder instances used for HDMI/TMDS and audio-infoframe handling. Important fields include ISRC status/valid/continue bits, packed ISRC byte payloads, generic packet header/payload bytes, generic packet send/continuous/line controls, HDMI double-buffer pending/taken/lock/disable bits, MPEG infoframe bytes, HDMI audio clock regeneration values for 32/44.1/48 kHz families, AFMT audio info bytes, IEC 60958 channel-status bytes, audio CRC engine controls/results, audio test-ramp controls, AFMT status and packet send controls, VBI packet controls, infoframe update behavior, and audio source selection.

The `DIG5_DIG_BE_CNTL`, `DIG5_DIG_BE_EN_CNTL`, `DIG6_DIG_BE_CNTL`, and `DIG6_DIG_BE_EN_CNTL` groups expose backend stream enable and timing selection fields. `DIG6_DIG_FE_CNTL` additionally selects the front-end source, stereo sync, start state, digital bypass select, symbol-clock state, TMDS pixel encoding, and color format.

The TMDS groups for both instances cover character/control-symbol programming: `TMDS_CNTL`, `TMDS_CONTROL_CHAR`, `TMDS_CONTROL0_FEEDBACK`, `TMDS_STEREOSYNC_CTL_SEL`, sync-character patterns, `TMDS_CTL_BITS`, DC balancer settings, and `TMDS_CTL0_1_GEN_CNTL` / `TMDS_CTL2_3_GEN_CNTL`. These fields are used when the digital encoder is operating in HDMI/DVI-style TMDS modes rather than native DisplayPort stream mode.

`DP5_*` is the most complete DisplayPort block in this chunk. It includes:

- Link and stream basics: `DP_LINK_CNTL`, `DP_PIXEL_FORMAT`, `DP_CONFIG`, `DP_VID_STREAM_CNTL`, and `DP_STEER_FIFO`.
- Main Stream Attribute programming: `DP_MSA_COLORIMETRY`, `DP_MSA_MISC`, `DP_VID_TIMING`, `DP_VID_N`, `DP_VID_M`, `DP_LINK_FRAMING_CNTL`, `DP_VID_MSA_VBID`, `DP_MSA_TIMING_PARAM1` through `PARAM4`, and `DP_MSA_VBID_MISC`.
- DPHY training and diagnostics: `DP_DPHY_CNTL`, training pattern selection, symbol pattern registers, 8b/10b, PRBS, scrambler, CRC enable/control/result, MST CRC control/status, fast-training control/status, BS/SR swap, and HBR2 pattern controls.
- Secondary-data and audio packet state: `DP_SEC_CNTL`, `DP_SEC_CNTL1`, `DP_SEC_CNTL2` through `CNTL7`, framing bytes, audio `N/M` programming and readback, timestamp, packet control, debug control, and generic secondary-packet send/pending/deadline bits.
- MST/MSE/MSO and DSC: MSE rate control/update, SAT allocation and status registers, SAT update/link timing/misc fields, MSO secondary stream enable masks, and `DP_DSC_CNTL__DP_DSC_EN`.

`DP6_*` repeats the same DisplayPort layout as `DP5_*` through the middle of `DP_SEC_CNTL2`. Because the range ends at line 39642, this chunk does not contain the remaining `DP6_DP_SEC_CNTL2` masks or later DP6 registers.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The macro namespace is the interface.

Consumers combine these macros with address definitions from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h`, such as `mmDIG5_AFMT_ISRC1_0`, `mmDP5_DP_LINK_CNTL`, and `mmDIG6_DIG_FE_CNTL`. DCN display code includes both the offset and mask headers, then feeds the generated names into register helpers and resource tables.

Direct include points found in this tree include DCN 1.0 GPIO factory/translation code, DCN 1.0 IRQ service code, DCN 1.0 resource setup, and DCN 2.0 GPIO translation code that reuses the DCN 1.0 register definitions. The chunk is therefore part of the low-level display hardware contract, not a Ceph filesystem or distributed-storage implementation despite the repository path prefix.

## Control Flow

This header has no runtime control flow. It supplies constants used by runtime code that performs MMIO or indexed-register operations.

The implied programming flow is:

1. Choose the correct digital/DP instance, for example DIG5 versus DIG6 or DP5 versus DP6.
2. Select the matching register address from `dcn_1_0_offset.h`.
3. Read the register when preserving unrelated fields is required.
4. Clear the target field with `*_MASK`, shift the new value by `*__SHIFT`, and write the combined register value.
5. For status, ack, pending, deadline-missed, taken, clear, or update bits, follow the hardware access semantics rather than assuming ordinary read/modify/write behavior.

The hardware sequencing implied by this chunk is sensitive around stream enable/disable, audio packet enable, infoframe update timing, HDMI double-buffer locking, DP link training/test pattern selection, scrambler and CRC controls, MST/MSE allocation updates, MSO secondary stream enabling, DSC enable, TMDS symbol programming, and lane/backend enable transitions. The generated macros do not encode valid value ranges, access type, self-clearing behavior, or required ordering.

## State And Persistence Behavior

The file itself stores no state and has no persistence. It describes fields inside display-engine registers whose values persist according to hardware behavior.

State represented by the DIG/AFMT/HDMI/TMDS groups includes audio-infoframe payloads, ISRC and MPEG metadata bytes, generic packet payloads, HDMI packet send state, double-buffer pending/taken/lock state, audio clock regeneration values and readbacks, IEC 60958 channel-status overrides, AFMT CRC and ramp-test state, packet transmission enables, backend/front-end source selection, lane enables, TMDS control characters, and AFMT clock enable/status.

State represented by the DP groups includes link-training-complete/status bits, embedded-panel mode, pixel encoding/depth/range, MSA colorimetry/misc/timing fields, stream enable/status/deferred-disable state, FIFO reset/overflow/ack state, DPHY training and test-pattern state, PRBS/scrambler/CRC configuration and results, secondary-data packet send/pending/deadline state, audio timing values, timestamps, MST stream allocation tables, MSE rate and SAT update state, MSO stream packet enables, DSC enable, debug fields, and MSA VBID readback/miscellaneous state.

Some fields are latched programming values, some are live status, some are sticky error/status bits, some are write-one-to-clear or write-one-to-ack, and some may be hardware- or firmware-updated during link training, hotplug handling, modeset, power management, suspend/resume, or ASIC reset. This header does not distinguish those access classes.

## Dependencies And Integration Points

The immediate dependency is the generated DCN 1.0 register ecosystem:

- `dcn_1_0_offset.h` supplies register addresses and base indices.
- `dcn_1_0_sh_mask.h` supplies field shifts and masks.
- AMDGPU display register helpers consume these names through local macros and read/modify/write wrappers.

Integration points include:

- DCN 1.0 resource construction, where stream encoders, link encoders, IRQ sources, GPIO/AUX/I2C, and hardware sequencing are wired to generated register names.
- HDMI/DVI output paths that program DIG5/DIG6 TMDS, generic packets, infoframes, AV mute, audio layout, ACR values, IEC 60958 metadata, and audio CRC/test state.
- DisplayPort output paths that program DP5/DP6 stream attributes, link training, pixel format, MSA/VBID metadata, scrambler/CRC/test features, secondary-data packets, audio timing, MST allocation, MSO state, and DSC.
- IRQ and diagnostic code that reads status, overflow, CRC, pending, deadline, and update bits.
- Reuse by later DCN-family code where register layouts are compatible enough to include the DCN 1.0 mask header.

The repeated instance names are important. `DIG5` pairs with `DP5`, and `DIG6` pairs with `DP6`, but callers must still select the correct physical stream/link encoder from resource tables; these macros do not encode topology or connector routing.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A wrong mask or shift compiles normally but can update the wrong bit, corrupt adjacent fields, or leave a required bit unchanged.

High-risk DIG/HDMI/AFMT fields include audio layout, channel enable, DP audio stream ID, ACR values, IEC 60958 channel-status bytes, generic packet send/line controls, HDMI double-buffer lock/clear, AV mute, infoframe update behavior, backend/frontend source selection, lane enable, and TMDS control-symbol settings. Errors here can produce missing or malformed audio, wrong HDMI packets, black screens, bad colors, failed DVI/HDMI modes, or compliance failures.

High-risk DP fields include stream enable and deferred-disable bits, pixel encoding/depth/range, MSA timing and VBID fields, DPHY training pattern/test/PRBS/scrambler controls, CRC controls/results, FIFO reset/overflow ack bits, secondary-data packet send/deadline bits, MST/MSE SAT programming, MSO secondary-packet enables, and DSC enable. Errors can appear as failed link training, flicker, blank displays, wrong colorimetry, lost MST streams, missing audio, bad CRC diagnostics, or incorrect DisplayPort compliance patterns.

Repeated generated layouts create copy/paste or generator drift risk. DP5 and DP6 should remain layout-compatible across many register families; a suffix mismatch or one-bit drift may affect only one output instance and can be hard to catch with build-only testing.

Chunk-boundary risk is explicit in this work item. The range begins after earlier DIG5 HDMI controls and ends before `DP6_DP_SEC_CNTL2` is complete. Any per-file summary should merge adjacent chunks before claiming full coverage of DIG5 or DP6.

Reserved semantics are not visible here. Some fields named status, pending, clear, update, taken, or deadline-missed likely have special read/write behavior. Generic register updates that preserve or write back status bits without respecting hardware rules can clear events, trigger sends, miss packet deadlines, or leave FIFOs in a bad state.

## Test Signals

Useful validation signals are mostly static generation checks plus hardware/display behavior:

- Build coverage for DCN 1.0 display resource, GPIO, IRQ, and modeset code that includes `dcn_1_0_sh_mask.h`.
- Generated-register consistency checks that every complete `REGISTER__FIELD__SHIFT` has the expected matching mask, masks align with shifts, and repeated DP5/DP6 and DIG5/DIG6 fields match where the hardware layout is intended to match.
- Diff/regeneration checks against AMD's authoritative DCN 1.0 register database and the companion `dcn_1_0_offset.h` addresses.
- HDMI/DVI tests on DIG5/DIG6-capable hardware covering modeset, AV mute, generic/infoframe packet sends, ACR/audio layout/channel programming, IEC 60958 metadata, audio CRC/ramp diagnostics, and suspend/resume.
- DisplayPort tests on DP5/DP6 covering link training, fast training, HBR2/test patterns, scrambler/PRBS/CRC diagnostics, stream enable/disable, pixel format/colorimetry/range, MSA/VBID programming, and FIFO overflow/reset paths.
- MST/MSO/DSC tests that exercise MSE SAT programming and status, rate updates, secondary-packet enables, DSC enable, and generic secondary-packet deadline/pending bits.
- Hotplug, HPD IRQ, runtime power-management, and full modeset stress tests that detect stale packet state, stuck pending bits, bad lane/backend enables, and incorrect restoration of display register state after reset or resume.

Regression symptoms from bad constants include blank display, flicker, link stuck at a lower rate, wrong colors or quantization, missing HDMI/DP audio, malformed infoframes, repeated hotplug/link-training failures, MST stream loss, CRC/test-pattern mismatches, or failures isolated to the fifth or sixth digital output instance.

## Cross-Chunk Notes

Earlier chunks of `dcn_1_0_sh_mask.h` define the beginning of the DIG5 HDMI/AFMT block and earlier DCN 1.0 display registers. Later chunks complete `DP6_DP_SEC_CNTL2` and continue through the remaining DP6 register families and subsequent DCN 1.0 hardware blocks. The final per-file document should present this source as a generated hardware register layout contract rather than as algorithmic driver logic.
