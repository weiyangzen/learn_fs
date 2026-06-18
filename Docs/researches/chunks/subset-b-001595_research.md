# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 34754-37195

## Research Scope

This chunk covers `subset-b-001595`, a line-bounded section of AMD DCN 1.0 register field definitions from `dcn_1_0_sh_mask.h`. The span is generated-style C preprocessor data: it contains no functions, structs, control statements, or storage declarations. Its exported surface is the set of `#define` constants used by display driver code to compose, extract, and acknowledge bitfields in DIG, HDMI, AFMT, TMDS, and DisplayPort register blocks.

The chunk begins inside `DIG3_AFMT_AUDIO_INFO1`, so only the final two mask constants for that register are included in this work item. It ends at `DIG5_AFMT_AUDIO_PACKET_CONTROL2`; the following `DIG5_AFMT_ISRC*` register definitions continue outside this chunk. Downstream merge should preserve those boundary facts when synthesizing the full-file report.

## Purpose

The purpose of this range is to define bit positions (`__SHIFT`) and bit masks (`_MASK`) for several display encoder instances:

- `DIG3` audio formatter and TMDS/backend fields.
- `DP3` DisplayPort link, main stream attribute, DPHY, secondary data packet, MST/MSE, DSC, and double-buffer fields.
- `DIG4` front-end, HDMI, audio formatter, generic packet, TMDS, backend, lane, and VBI update fields.
- `DP4` DisplayPort fields equivalent to the `DP3` block for a separate hardware instance.
- The start of `DIG5`, covering front-end, HDMI, CRC/test/FIFO, generic packet, global control, and audio packet control fields.

The driver can use these macros with register accessor helpers to write only selected fields without hardcoding numeric bit layouts at call sites.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The important interface is the macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low-bit position of a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned bit mask for the same field.
- Register prefixes such as `DIG3_`, `DP3_`, `DIG4_`, `DP4_`, and `DIG5_` identify repeated display encoder/link instances.

I counted 2,162 `#define` lines in the requested range: 1,080 `__SHIFT` defines, 1,082 `_MASK` defines, and 267 distinct register names. The two extra masks are due to the chunk starting after the corresponding `DIG3_AFMT_AUDIO_INFO1` shift definitions.

Key register families in this chunk include:

- Audio formatter fields: `AFMT_60958_*`, `AFMT_AUDIO_INFO*`, `AFMT_AUDIO_CRC_*`, `AFMT_AUDIO_PACKET_CONTROL*`, `AFMT_STATUS`, `AFMT_RAMP_CONTROL*`, `AFMT_VBI_PACKET_CONTROL*`, `AFMT_GENERIC_*`, `AFMT_MPEG_INFO*`, and ISRC-adjacent packet controls.
- HDMI fields: `HDMI_CONTROL`, `HDMI_STATUS`, `HDMI_AUDIO_PACKET_CONTROL`, `HDMI_ACR_*`, `HDMI_VBI_PACKET_CONTROL`, `HDMI_INFOFRAME_CONTROL*`, `HDMI_GENERIC_PACKET_CONTROL*`, `HDMI_DB_CONTROL`, and `HDMI_GC`.
- DIG/TMDS fields: `DIG_FE_CNTL`, `DIG_BE_CNTL`, `DIG_BE_EN_CNTL`, `DIG_LANE_ENABLE`, `DIG_FIFO_STATUS`, `DIG_TEST_PATTERN`, `DIG_RANDOM_PATTERN_SEED`, `DIG_OUTPUT_CRC_*`, `TMDS_*`, and `DIG_VERSION`.
- DisplayPort fields: `DP_LINK_CNTL`, `DP_PIXEL_FORMAT`, `DP_CONFIG`, `DP_VID_STREAM_CNTL`, `DP_MSA_*`, `DP_VID_*`, `DP_DPHY_*`, `DP_SEC_*`, `DP_MSE_*`, `DP_MSO_*`, `DP_DSC_CNTL`, `DP_DB_CNTL`, and `DP_MSA_VBID_MISC`.

## Register Coverage Notes

The `DIG3` portion finishes audio formatter, backend, TMDS, lane, and VBI packet control definitions, then transitions to the full `dce_dc_dio_dp3_dispdec` address block. `DP3` contains a complete-looking DisplayPort register-field group in this chunk, including link status/training, video format and timing, MSA metadata, physical-layer training and CRC, secondary packets, audio N/M timestamp data, MST allocation table fields, MSO controls, DSC enable, generic secondary packet send status/line controls, double-buffer control, and VBID/MSA override fields.

The `DIG4` portion starts with `dce_dc_dio_dig4_dispdec` and covers a broad digital encoder block: front-end source selection, output CRC, clock/test/random patterns, FIFO status, HDMI control and status, HDMI audio clock regeneration, VBI/infoframe/generic packet controls, HDMI guard-band/global control, AFMT audio layout/channel stream selection, ISRC and MPEG metadata payload bytes, generic packet header/body bytes, ACR parameter/status values, 60958 channel-status fields, audio CRC/ramp/status, backend enable and HPD selection, TMDS pattern generation, lane enable, AFMT clock state, and generic VBI frame/immediate update handshakes.

The `DP4` portion mirrors the `DP3` DisplayPort field set for another link instance. It repeats link/training, video timing, DPHY, secondary packet, MST/MSE, MSO, DSC, double-buffer, and VBID override definitions with `DP4_` prefixes. Because the fields and masks match the `DP3` shape, code using instance-specific register tables can select equivalent behavior for encoder/link 4.

The `DIG5` portion begins `dce_dc_dio_dig5_dispdec` and covers only the early part of that block in this chunk: front-end selection, CRC/test/fifo controls, HDMI control/status/audio/ACR/VBI/infoframe/generic packet fields, global control, and `AFMT_AUDIO_PACKET_CONTROL2`. The chunk ends before the `DIG5_AFMT_ISRC*` continuation.

## Control Flow

This header chunk has no runtime control flow. Its values participate in control flow indirectly when compiled driver code uses them in register programming sequences. Typical usage is expected to be:

1. Select a register for a DIG, DP, HDMI, TMDS, or AFMT hardware instance.
2. Shift a field value by the matching `__SHIFT` value.
3. Mask it with the matching `_MASK` value, often via generated AMD register macros or helper functions.
4. Write, read, poll, or acknowledge the underlying MMIO register.

Several field groups imply hardware handshakes even though no code executes here. Examples include `_UPDATE_PENDING`, `_SEND_PENDING`, `_SEND_ACTIVE`, `_ACK`, `_CLR`, `_DONE`, `_STATUS`, and `_MASK` interrupt/status bits. Correct caller control flow must respect those hardware semantics in implementation files outside this header.

## State And Persistence Behavior

The macros themselves are compile-time constants and persist only in object code after preprocessing. They do not allocate memory or maintain software state.

The hardware fields they describe do represent persistent device state until changed by MMIO writes or hardware events. Notable state categories in this chunk are:

- Enable state: audio clocks, DIG enable, DP secondary streams, HDMI packet sends, DSC enable, lane enables, test patterns, deep color, and data scrambling.
- Status/interrupt state: FIFO errors, HDMI packet errors, DPHY CRC status, link status, audio enable changes, secondary packet collisions, send pending/deadline missed, MSE allocation status, and double-buffer pending/taken state.
- Packet payload state: audio infoframes, MPEG info, ISRC data, generic packet headers/body bytes, HDMI ACR N/CTS values, 60958 channel-status words, and DisplayPort audio M/N values.
- Timing/allocation state: DP MSA timings, MSE slot allocation tables, MSO link count/secondary stream enables, and secondary packet framing positions.

Because these values map directly to hardware registers, incorrect masks can persist wrong state in display hardware across modesets until the driver reprograms the block or resets the encoder.

## Dependencies

This chunk depends on the rest of the AMD display register-definition system for register addresses, register access helpers, and generated table glue. The local file provides only field positions and masks; address definitions are expected in sibling register headers such as offset/address headers for DCN 1.0.

Integration normally depends on:

- C preprocessor inclusion by AMDGPU DC display code.
- Register accessor macros/functions that accept `*_MASK` and `*__SHIFT` constants.
- Instance-specific DIG/DP register tables that pair these field constants with register addresses.
- Hardware documentation or generated register databases that define the authoritative bit layouts.

There are no external library dependencies in this chunk.

## Integration Points

The definitions are intended for AMDGPU DCN display encoder paths, especially code that configures HDMI, DisplayPort, audio formatting, secondary packets, TMDS output, link training, MST/MSO, DSC, and mode timing. Likely consumers include encoder enable/disable paths, link training routines, audio setup, infoframe programming, CRC/test utilities, hotplug/backend selection, and modeset validation or commit code.

The repeated `DIG3`/`DIG4`/`DIG5` and `DP3`/`DP4` prefix pattern is important for instance mapping. Driver code can use the same logical sequence for different hardware pipes while selecting register constants for the active encoder instance.

## Risks And Edge Cases

- Bitfield drift is the primary risk. A wrong mask or shift can silently program the wrong hardware field, causing display link failures, missing audio, bad infoframes, MST allocation errors, or difficult-to-debug training/status behavior.
- The file is generated-style and highly repetitive. Manual edits are risky because one instance can diverge from equivalent `DIG`/`DP` siblings.
- Boundary chunks are partial. This work item starts after some `DIG3_AFMT_AUDIO_INFO1` shift definitions and ends before the `DIG5_AFMT_ISRC*` continuation, so a full-file report must merge neighboring chunks before making complete statements about those registers.
- Status and acknowledge fields require careful write behavior. Fields ending in `_ACK`, `_CLR`, or status-like names may be write-one-to-clear or hardware-owned; consumers must follow register reference semantics, not infer behavior from mask names alone.
- Some names include `_MASK_MASK` patterns, such as complete-mask fields for interrupt/status masking. These are not duplicate suffix mistakes in this generated naming scheme and should not be normalized away.
- The same field layout appears across `DP3` and `DP4` and across `DIG3`/`DIG4`/`DIG5` subsets. Tests or code generation checks should verify expected equivalence without assuming every instance is complete inside this chunk.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration oriented:

- The header should preprocess cleanly with AMDGPU DC code and produce no duplicate or malformed macro names for this line range.
- Register accessor code should build against every `*_MASK`/`*__SHIFT` name referenced by DCN 1.0 DIG, HDMI, DP, AFMT, and TMDS implementation files.
- Generated-header consistency checks should compare sibling instance layouts, especially `DP3` vs `DP4` and overlapping `DIG3`/`DIG4`/`DIG5` register families.
- Runtime display tests should exercise HDMI and DisplayPort modesets, audio enablement, infoframe programming, DP link training, MST slot allocation, DSC enable paths, CRC/test-pattern paths, and status/ack flows.
- Negative signals include missing audio packets, HDMI/DP link training failure, stuck `_PENDING` bits, FIFO or packet error interrupts, bad MSA timing, wrong MST payload allocation, or failed CRC/readback checks.
