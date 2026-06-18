# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 46813-49204

## Scope

This chunk covers lines 46813-49204 of the generated DCN 3.0.0 register shift/mask header. It contains 2,174 `#define` entries and register/address-block comments only; there are no C functions, structs, enums, variables, or executable branches in this slice. The exported interface is the generated macro namespace of `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` constants consumed by AMD display register helpers.

The range starts in the tail of the `DP4` DisplayPort encoder block, then covers the complete `DIG5` instance sideband/video-packet/audio-format/metadata/digital-encoder blocks, most of the `DP5` DisplayPort block, shared DCIO/UNIPHY/pinstrap controls, and the start of LVTMA panel power sequencing. The last line is only the `//LVTMA_PWRSEQ_REF_DIV` heading; that register's field definitions continue in the following chunk.

## Purpose

The purpose of this chunk is to describe the bit layout for one late digital output instance and shared display I/O registers on DCN 3.0 hardware. Driver code includes this header with the matching offset header and turns the generated constants into per-block register tables and field metadata. That keeps the functional display code from hard-coding raw bit positions for DisplayPort stream setup, HDMI/TMDS packet programming, audio metadata, generic packet scheduling, physical link routing, pinstrap reads, and panel power sequencing.

Major hardware areas covered here are:

- `DP4` MSO, DSC, secondary-data, generic-stream-packet, double-buffer, MSA/VBID, metadata-transmission, DSC bytes-per-pixel, and ALPM field definitions.
- `VPG5` generic-packet, frame-update, immediate-update, ISRC, MPEG infoframe, status, and memory-power fields.
- `AFMT5` HDMI/DP audio packet, audio infoframe, IEC 60958 channel-status, audio CRC, ramp-test, status, source-select, and memory-power fields.
- `DME5` metadata engine enable, HUBP requestor selection, stream type, double-buffer state, and memory-power fields.
- `DIG5` front-end/backend digital encoder fields for source routing, CRC/test patterns, FIFO status, HDMI metadata and generic packets, audio clock recovery, TMDS control characters, lane enablement, and force-disable controls.
- `DP5` link, pixel-format, MSA, stream, main-link DPHY, MST, secondary-data, MSO, DSC, packet, ALPM, and generic-packet fields.
- Shared `DCIO` fields for generic clock outputs, DCIO clock gating, reference clock output selection, UNIPHY A-F link/channel crossbar control, write-command delay, hardware pinstraps, and LVTMA power sequencing.

## Important APIs, Types, And Constants

There are no callable APIs in this header chunk. The important API surface is the generated macro shape:

- `REGISTER__FIELD__SHIFT` gives the field bit position.
- `REGISTER__FIELD_MASK` gives the already-shifted field mask.
- Address block comments such as `// addressBlock: dce_dc_dio_dig5_dispdec` partition the macros by hardware instance.
- Register comments such as `//DP5_DP_DPHY_CNTL` and `//LVTMA_PWRSEQ_CNTL` identify the register whose following field constants are being defined.

Important macro groups include:

- `DP4_DP_MSO_CNTL`, `DP4_DP_MSO_CNTL1`, `DP4_DP_DSC_CNTL`, `DP4_DP_SEC_CNTL2` through `DP4_DP_SEC_CNTL7`, `DP4_DP_GSP8_CNTL` through `DP4_DP_GSP11_CNTL`, and `DP4_DP_GSP_EN_DB_STATUS`, which describe multi-stream operation, DSC slice width/mode, secondary-data send/pending/deadline status, per-packet line numbers, and double-buffer pending state for DisplayPort instance 4.
- `VPG5_VPG_GENERIC_PACKET_ACCESS_CTRL`, `VPG5_VPG_GENERIC_PACKET_DATA`, `VPG5_VPG_GSP_FRAME_UPDATE_CTRL`, and `VPG5_VPG_GSP_IMMEDIATE_UPDATE_CTRL`, which expose indexed packet payload bytes plus update/pending bits for generic packet slots 0-14.
- `AFMT5_AFMT_AUDIO_PACKET_CONTROL2`, `AFMT5_AFMT_AUDIO_INFO0`, `AFMT5_AFMT_AUDIO_INFO1`, `AFMT5_AFMT_60958_0` through `AFMT5_AFMT_60958_2`, and `AFMT5_AFMT_AUDIO_PACKET_CONTROL`, which define audio layout/channel/HBR controls, audio infoframe contents, IEC 60958 channel status, ACK bits, channel swap, and audio test fields.
- `DME5_DME_CONTROL` and `DME5_DME_MEMORY_CONTROL`, which define the metadata engine enable path, requestor ID, stream type, double-buffer pending/taken/clear bits, memory power force/disable/state, and default low-power state.
- `DIG5_DIG_FE_CNTL`, `DIG5_DIG_BE_CNTL`, `DIG5_DIG_BE_EN_CNTL`, `DIG5_DIG_LANE_ENABLE`, and `DIG5_FORCE_DIG_DISABLE`, which describe digital front-end source selection, stereo sync, start/bypass/pixel selection, Dolby Vision flags, backend source/mode/HPD selection, lane enables, and the force-disable bit.
- `DIG5_HDMI_*` and `DIG5_TMDS_*` registers, which cover HDMI metadata packets, scrambling/deep color/error ACK, ACR send/source/N/CTS programming, generic packet controls 0-10, AVMUTE/general-control state, HDMI double buffering, TMDS sync/control-character generation, DC balancing, and ACR status readback.
- `DP5_DP_LINK_CNTL`, `DP5_DP_PIXEL_FORMAT`, `DP5_DP_VID_STREAM_CNTL`, `DP5_DP_STEER_FIFO`, `DP5_DP_VID_TIMING`, `DP5_DP_DPHY_*`, `DP5_DP_SEC_*`, `DP5_DP_MSE_*`, `DP5_DP_MSA_TIMING_PARAM*`, `DP5_DP_MSO_*`, `DP5_DP_DSC_*`, and `DP5_DP_ALPM_CNTL`, which mirror the DisplayPort link, main-link PHY, secondary-data, MST, MSA, MSO, DSC, and low-power controls for instance 5.
- `DC_GENERICA`, `DC_GENERICB`, `DCIO_CLOCK_CNTL`, and `DC_REF_CLK_CNTL`, which select and gate generic display clock outputs and reference-clock outputs.
- `UNIPHY[A-F]_LINK_CNTL` and `UNIPHY[A-F]_CHANNEL_XBAR_CNTL`, which repeat the same physical-link field layout across six UNIPHY blocks: pixel-valid reset, minimum low duration, per-channel inversion, lane stagger, HPD link-enable mask, channel crossbar source, and link enable.
- `DC_PINSTRAPS`, whose `DC_PINSTRAPS_AUDIO` field is read by DCN resource code to populate resource strap data.
- `LVTMA_PWRSEQ_CNTL` and `LVTMA_PWRSEQ_STATE`, which define panel power sequence enable/target state, DIGON/SYNCEN/BLON override/polarity bits, and readback/done/state fields. `LVTMA_PWRSEQ_REF_DIV` starts at the chunk end and must be reconciled with the next chunk.

## Control Flow

This chunk has no runtime control flow. Its behavior is compile-time macro expansion:

1. DCN 3.0 display code includes generated offset and mask headers.
2. Register-list macros concatenate register and field names to resolve these `SHIFT` and `MASK` definitions.
3. Runtime helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WAIT`, `FN(...)`, and generated `*_MASK_SH_LIST` tables use the resulting constants when reading or writing MMIO registers.

The order of definitions still matters operationally for maintenance. Each register generally lists all shifts first and masks second, and the repeated instance layout (`DP4` followed by `DIG5`/`DP5`) lets generated diffs catch field drift across otherwise similar encoder blocks. Reordering would usually compile, but it would make generator output review and cross-instance comparison harder.

## State And Persistence Behavior

The header itself stores no software state and persists nothing. It describes hardware state that persists in GPU display registers until overwritten, reset, or power-gated:

- DisplayPort secondary-data and generic-stream-packet registers hold send requests, pending/active status, deadline-missed bits, line numbers, and double-buffer state for HDR metadata, infoframes, PPS packets, and related sideband data.
- VPG and HDMI generic-packet registers store indexed packet payload bytes and update scheduling bits. Incorrect masks can cause stale, partial, or mistimed packets to be sent on a live stream.
- AFMT fields represent audio packet generation state, channel layout, HBR/60958 state, CRC/test behavior, FIFO overflow status, and ACK bits.
- DIG5 fields control encoder source routing, timing/test-pattern output, FIFO status, HDMI/TMDS output behavior, and lane enables. These settings directly affect link bring-up and visible output.
- DP5 DPHY fields configure training patterns, FEC state, 8b/10b behavior, PRBS, scrambling, CRC, fast-training controls, and MST CRC windows.
- UNIPHY fields route logical encoder channels to physical lanes and control link enable/inversion/stagger behavior; bad values can persist as lane mapping or link-training failures.
- LVTMA fields control panel power, backlight enable, DIGON/SYNCEN sequencing, override bits, polarity, and readback state. These interact with panel-control code and with the backlight registers that continue after this chunk.

Several registers mix control, status, ACK, clear, pending, and mask fields in one word. For example `*_DB_TAKEN_CLR`, `*_ERROR_ACK`, `*_FIFO_OVERFLOW_ACK`, and `*_SEND_PENDING` style fields require callers to know whether a bit is read-only status, write-one-to-clear, or a control latch; the generated macro names only encode bit positions.

## Dependencies And Integration Points

This header chunk depends on exact naming compatibility with AMD's generated display register infrastructure and the matching `dcn_3_0_0_offset.h` offsets. The constants are normally integrated through:

- DCN register accessor macros that build field metadata from `FN(register, field)`, `FD_MASK(register, field)`, and `FD_SHIFT(register, field)`.
- Resource construction code that passes per-block register, shift, and mask tables into link encoders, audio objects, VPG objects, AFMT objects, and panel control objects.
- `drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`, which reads `DC_PINSTRAPS__DC_PINSTRAPS_AUDIO` through `generic_reg_get()` and constructs panel control, audio, and VPG objects using generated tables.
- `drivers/gpu/drm/amd/display/dc/dce/dce_panel_cntl.h` and `dce_panel_cntl.c`, which map `LVTMA_PWRSEQ_CNTL`, `LVTMA_PWRSEQ_STATE`, and `LVTMA_PWRSEQ_REF_DIV` fields into panel-control shift/mask structs and use them for panel power/backlight sequencing.
- Link encoder and DIO paths that bind DIG/DP/UNIPHY field masks with offsets for routing a display stream to a physical encoder and link.
- HDMI/DP audio and packet paths that depend on `AFMT5`, `VPG5`, `DIG5_HDMI_*`, and `DP5_DP_SEC_*` definitions for audio infoframes, generic packets, ACR values, metadata packets, and secondary-data scheduling.

The visible `DP5` and `DIG5` names are instance-specific. They are not generic aliases: consumers must select the correct instance table before using these fields, or they risk programming the wrong display encoder.

## Risks And Edge Cases

- A wrong shift or mask silently corrupts MMIO field access. C compilation only proves that the macro exists, not that its numeric value matches the ASIC register database.
- This range covers repeated per-instance blocks. Copy/paste or generator drift between `DP4`, `DP5`, and adjacent DIG instances can leave one encoder instance broken while others work.
- `*_MASK_MASK` names such as `HDMI_ERROR_MASK_MASK`, `DP_STEER_OVERFLOW_MASK_MASK`, and `DP_VID_STREAM_DISABLE_MASK_MASK` are generated from fields named `*_MASK`; they are easy to misread during manual review.
- ACK/clear fields share registers with status fields. Read-modify-write sequences that preserve stale status bits can accidentally acknowledge errors or double-buffer state.
- Packet update bits and pending bits are timing-sensitive. Bad masks in VPG, HDMI generic packet, DP secondary-data, or DME double-buffer fields can cause metadata changes to miss a frame boundary or occur immediately when a vertical-update path expected deferral.
- `LVTMA_PWRSEQ_REF_DIV` begins at the final line without its field definitions. Any final file report must merge this chunk with the next one before making complete claims about panel PWM/reference-divider fields.
- UNIPHY crossbar and lane inversion fields affect physical routing. Incorrect values can manifest as DP/HDMI link training failures, lane swaps, blank displays, or intermittent errors rather than obvious software faults.
- Several masks use high bits or broad fields, including `0x80000000L`, `0xFFFF0000L`, and `0xFF000000L`. Callers must preserve unsigned 32-bit semantics when composing values.
- Cross-ASIC reuse is risky because adjacent DCN families share many names while adding, dropping, or moving fields.

## Test Signals

Useful validation signals for this chunk are mostly build-time, generated-header diff, and hardware-integration oriented:

- Build DCN 3.0 display code with consumers that include `dcn_3_0_0_sh_mask.h`, especially resource, link encoder, audio, VPG, AFMT, and panel-control paths.
- Preprocessor or compile-time checks that `FN`, `FD_MASK`, `FD_SHIFT`, and generated `*_MASK_SH_LIST` expansions resolve all `DP5`, `DIG5`, `VPG5`, `AFMT5`, `DME5`, `DC_PINSTRAPS`, and `LVTMA` fields used by DCN 3.0 tables.
- Generated-header comparison against the authoritative AMD register database and against adjacent DCN families where the same register instance is expected to remain layout-compatible.
- Display bring-up tests on outputs mapped to DIG/DP instance 5, including hotplug, modeset, stream enable/disable, link training, MST, DSC, FEC, and ALPM transitions.
- HDMI validation for scrambling, deep color, ACR N/CTS programming, audio packet send, infoframe updates, generic packet scheduling, AVMUTE/general-control behavior, and TMDS test/control-character paths.
- DP metadata validation for secondary-data packets, PPS packets, HDR or other metadata line scheduling, GSP pending/active/deadline status, and double-buffer update timing.
- Panel-control tests for LVTMA power sequencing, DIGON/SYNCEN/BLON overrides, backlight enable/restore, suspend/resume, and eDP panel power state readback.
- PHY/routing tests for UNIPHY A-F channel crossbar selection, lane inversion, link enable, HPD-mask behavior, and clock/ref output selection.

## Open Cross-Chunk Questions

- The next chunk must provide the `LVTMA_PWRSEQ_REF_DIV` fields and subsequent backlight PWM fields before the final per-file report can fully describe panel-control coverage.
- Whole-file reconciliation should compare this mask header with `dcn_3_0_0_offset.h` to ensure every register represented here has the expected offset and base-index entry.
- If generator provenance exists elsewhere in the repository, the final report should identify it, because manual edits to this generated header are high risk.
