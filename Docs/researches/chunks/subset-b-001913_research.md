# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 39767-42179

## Purpose

This chunk is generated AMD DCN 3.1.6 register field metadata. It contains no executable C logic; it publishes preprocessor constants that describe hardware MMIO bit positions (`__SHIFT`) and bit masks (`_MASK`). AMD display code includes this header with the matching `dcn_3_1_6_offset.h` so per-ASIC register tables can combine register offsets with field encodings and then use common register helpers to read, set, update, or poll individual fields.

The requested range covers the tail of the `DP4_DP_DPHY_SYM2` group, then a large portion of the fourth DisplayPort/DIG stream encoder instance, the DIG4 HDMI/TMDS front-end and back-end registers, AFMT0 through AFMT4 audio formatter fields, DME0/DME1 metadata-engine fields, VPG0 generic secondary-packet fields, and the beginning of VPG1 generic secondary-packet fields. Although this path is under a local `ceph-client` mirror, the file is AMDGPU display hardware metadata and has no Ceph or distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocation paths, locks, includes, or direct register operations in this chunk. Its exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position of a field in a hardware register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or updating that field.
- `// addressBlock: ...` comments: generated grouping metadata for the following register family.

Major register families in this slice:

- `DP4_DP_DPHY_*`: DisplayPort physical/link-layer controls for 8b/10b reset/disparity, PRBS generation, scrambler behavior, CRC enable/control/result, MST CRC slot/status, fast training, byte-swap/scrambler-reset swap, and HBR2 pattern control.
- `DP4_DP_SEC_*`, `DP4_DP_GSP*`, and `DP4_DP_SEC_METADATA_TRANSMISSION`: DP secondary-data packet control for audio, ASP/ATP/AIP/ACM, generic secondary packets GSP0-GSP11, MPEG/ISRC style packet enables, PPS/metadata packet enable and line timing, collision/audio mute status, stream enable, and send/pending/deadline bits.
- `DP4_DP_MSE_*`, `DP4_DP_MSO_*`, `DP4_DP_MSA_*`, and `DP4_DP_MSA_VBID_MISC`: MST stream allocation-table fields, link timing, MSO lane/segment controls, main-stream-attribute timing fields, VBID misc bits, and update/status latches.
- `DP4_DP_DSC_*`, `DP4_DP_ALPM_CNTL`, and `DP4_DP_DB_CNTL`: DSC mode/bytes-per-pixel fields, ALPM enable/force/wake/status controls, and double-buffer control/status.
- `DIG4_DIG_*`, `DIG4_HDMI_*`, and `DIG4_TMDS_*`: DIG4 front-end source, start, pixel/TMDS encoding, stereo sync, FIFO status, CRC/test/random pattern controls, HDMI metadata/audio/ACR/VBI/infoframe/generic packet controls, HDMI deep-color/scrambling/status controls, data-bypass controls, and TMDS control/data-balance/sync-character fields.
- `AFMT0_AFMT_*` through `AFMT4_AFMT_*`: audio formatter packet control, audio source/channel enable, HDMI/DP audio info fields, IEC 60958 channel-status fields, CRC/ramp/status registers, and memory power controls for five AFMT instances.
- `DME0_DME_*` and `DME1_DME_*`: metadata engine requestor ID, engine enable, stream type, double-buffer pending/taken/clear/disable, missed-transmission status/clear, and memory power/default-low-power fields.
- `VPG0_VPG_*` and beginning of `VPG1_VPG_*`: video packet generator generic packet data-index/data-byte fields, frame/immediate update bits and pending bits for generic slots 0-14, conflict status/clear, memory power, ISRC access/data, MPEG info, and the start of VPG1 frame-update controls.

Representative fields that are directly useful to consumers include `DP_SEC_STREAM_ENABLE`, `DP_SEC_GSP*_ENABLE`, `DP_SEC_GSP*_SEND`, `DP_SEC_GSP*_LINE_NUM`, `DP_SEC_GSP11_PPS`, `DP_SEC_METADATA_PACKET_ENABLE`, `DP_MSA_HTOTAL`, `DP_MSA_VTOTAL`, `DP_MSA_HSTART`, `DP_MSA_VSTART`, `DP_MSA_HSYNCWIDTH`, `DP_MSA_VSYNCWIDTH`, `DP_DSC_MODE`, `DP_DSC_BYTES_PER_PIXEL`, `DIG_SOURCE_SELECT`, `DIG_START`, `DIG_FIFO_LEVEL_ERROR`, `HDMI_GENERIC*_SEND`, `HDMI_GENERIC*_CONT`, `HDMI_GENERIC*_LINE`, `HDMI_ACR_*`, `AFMT_AUDIO_SRC_SELECT`, `AFMT_AUDIO_CHANNEL_ENABLE`, `AFMT_60958_CS_UPDATE`, `AFMT_AUDIO_SAMPLE_SEND`, `AFMT_MEM_PWR_*`, `VPG_GENERIC_DATA_INDEX`, `VPG_GENERIC_DATA_BYTE*`, `VPG_GENERIC*_FRAME_UPDATE`, `VPG_GENERIC*_IMMEDIATE_UPDATE`, and `VPG_GENERIC_CONFLICT_*`.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that consumes the generated constants:

1. DCN316 resource setup includes `dcn_3_1_6_offset.h` and this `dcn_3_1_6_sh_mask.h`.
2. `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` expands register-list macros such as `SE_DCN3_REG_LIST(id)`, `VPG_DCN31_REG_LIST(id)`, and `AFMT_DCN31_REG_LIST(id)` into per-instance address tables, using offsets from the offset header.
3. The same file expands shift/mask lists into typed tables: `se_shift`/`se_mask`, `vpg_shift`/`vpg_mask`, and `afmt_shift`/`afmt_mask`. Those values come from macros in this generated header.
4. `dcn316_stream_encoder_create()` maps a stream engine to its stream encoder, VPG, and AFMT instances, then passes the register, shift, and mask tables into `dcn30_dio_stream_encoder_construct()`.
5. Runtime methods in the DIO stream encoder, VPG, and AFMT modules use `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_WRITE`, `REG_GET`, and `REG_WAIT` helpers. Those helpers rely on the field shifts and masks from this chunk to program hardware.

Important runtime sequences represented by these fields include:

- HDMI infoframe updates: the stream encoder writes generic packet payload through the VPG, then sets `HDMI_GENERIC*_CONT`, `HDMI_GENERIC*_SEND`, and `HDMI_GENERIC*_LINE` fields for the selected packet slot.
- DP DSC PPS transmission: the stream encoder enables PPS handling with `DP_SEC_GSP11_PPS`, loads PPS chunks into VPG generic slots, sets `DP_SEC_GSP11_LINE_NUM`, and coordinates VBID/PPS line timing.
- DP and HDMI audio setup: AFMT programs audio source, channel enable, 60958 channel-status fields, audio sample send, and memory power; DP secondary-data fields handle audio packet and timestamp paths.
- VPG generic packet writes: `vpg3_update_generic_info_packet()` waits for `VPG_GENERIC_CONFLICT_OCCURED` to clear, clears conflict status, sets `VPG_GENERIC_DATA_INDEX`, writes packet header/body bytes through `VPG_GENERIC_PACKET_DATA`, and triggers either frame update or immediate update bits for slots 0-14.

The macros themselves do not encode required ordering, access type, locking, or side effects. Consumers must preserve the hardware-specific sequencing around stream enable/disable, packet double-buffering, update locks, symbol clocks, AFMT/VPG memory power, DSC PPS timing, and interrupt/status clears.

## State And Persistence Behavior

This chunk stores no software state and persists nothing in memory or on disk. It describes MMIO-backed GPU display state:

- DP4 link-layer state: PRBS, scrambler, CRC, MST CRC, fast training, HBR2 pattern, MSE/MST allocation, MSO, MSA timing, VBID misc, DSC, ALPM, and double-buffer controls.
- DP4 secondary-packet state: stream enable, packet enable bits, packet send and pending bits, line reference/line number selection, audio N/M values and readbacks, PPS/metadata controls, collision status, and audio mute status.
- DIG4 HDMI/TMDS state: HDMI packet generation, generic packet line/send/continuous controls, ACR CTS/N values, deep color, scrambling, keepout, VBI packets, TMDS symbol/control/data-balance settings, DIG FIFO status, CRC/test pattern state, and DIG enable/disable status.
- AFMT0-4 audio formatter state: audio source routing, active channel mask, audio/infoframe update bits, IEC 60958 channel status, ramp/CRC/status, audio sample transmission, and AFMT memory power force/disable/status fields.
- DME0-1 metadata state: engine enable, stream type, HUBP requestor ID, double-buffer status/clear bits, missed transmission status/clear bits, and metadata-engine memory power policy/status.
- VPG0 and partial VPG1 packet-generator state: generic packet payload index/data windows, frame/immediate update triggers, update-pending bits, conflict status/clear, VPG memory power, ISRC data, and MPEG info fields.

Persistence is hardware-defined. Configuration fields generally remain in the display block until a modeset, stream disable, power-gating transition, suspend/resume, or ASIC reset changes them. Status, pending, readback, conflict, clear, ack, missed, CRC-result, memory-power-state, and training-status fields may be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive. The generated header provides masks and shifts only; it does not document access semantics.

## Dependencies And Integration Points

This chunk must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`, which supplies the matching register offsets and base-index macros.
- DCN316 base-address definitions and register-table construction in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`.
- Common register-helper macros in AMD display code, especially the `SE_SF`, `SRI`, `REG_*`, `FN`, and per-block shift/mask table patterns.

Direct DCN316 include and construction points found in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` includes this header and builds `stream_enc_regs`, `vpg_regs`, `afmt_regs`, `se_shift`, `se_mask`, `vpg_shift`, `vpg_mask`, `afmt_shift`, and `afmt_mask`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c` includes the same generated DCN316 register headers for DMUB-facing register metadata, though this particular chunk is primarily DIO/VPG/AFMT stream metadata.

Important shared consumers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_stream_encoder.h` defines `SE_DCN3_REG_LIST(id)` and `SE_COMMON_MASK_SH_LIST_DCN30(...)`, which reference many fields in this chunk for HDMI packet control, DP secondary packets, MSA timing, DSC, stream enable, AFMT clock, DIG source/start, FIFO status, and metadata packets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_stream_encoder.c` uses those tables to update HDMI info packets, stop generic packets, program DP DSC/PPS packets, and control stream packet behavior.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_vpg.c` use the VPG0 masks/shifts from this chunk as the canonical field layout for all VPG instances.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_afmt.h`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_afmt.c`, and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_afmt.c` use the AFMT0 masks/shifts from this chunk as the canonical field layout for AFMT instances.

## Risks And Edge Cases

- Field drift is the main risk. These macros are untyped constants, so an incorrect mask or shift can compile cleanly while programming the wrong hardware bits.
- The chunk boundaries are artificial. The first requested line starts at the tail of `DP4_DP_DPHY_SYM2`, and the last requested line stops inside `VPG1_VPG_GSP_FRAME_UPDATE_CTRL`; adjacent chunks are required for complete file-level claims.
- Instance symmetry is assumed by consumer code. DCN316 uses instance-0 field names in shift/mask tables and applies them to multiple stream/VPG/AFMT instances. If a later instance has a different layout, the shared-table pattern would silently misprogram that instance.
- DP secondary-packet bits are sequencing-sensitive. Wrong GSP enable, send, pending, line number, PPS, or stream-enable fields can cause missing HDR/DSC/audio/metadata packets, PPS line conflicts, or sink compatibility failures.
- VPG generic-packet access is conflict-sensitive. Bad `VPG_GENERIC_CONFLICT_*`, data-index, data-byte, frame-update, or immediate-update masks can corrupt infoframes or race hardware reads of packet memory.
- HDMI generic-packet controls are slot-specific. Incorrect `HDMI_GENERIC*_SEND`, `CONT`, or `LINE` masks can disable mandatory packets, transmit stale packets every frame, or send packets on invalid lines.
- AFMT fields affect audio routing and memory power. Incorrect audio source, channel-enable, 60958, sample-send, or memory-power masks can cause silent audio, wrong channel mapping, audio dropouts after power transitions, or read-modify-write of status bits.
- DSC/MSA/MST timing fields are mode-sensitive. Incorrect MSA timing, MSO, MSE allocation, DSC mode, bytes-per-pixel, or PPS packet fields may only fail on high-refresh, MST, DSC, deep-color, or multi-stream configurations.
- Status, ack, clear, pending, readback, and power-state fields may have side effects or read-only semantics not represented here. Generic read-modify-write on such fields can be unsafe unless the consumer knows the register contract.
- Generated-register changes can create broad compile or behavior failures because stream encoder, VPG, AFMT, DMUB, and resource construction code all depend on exact macro names.

## Test Signals

Useful validation combines generated-header consistency checks and hardware-facing display tests:

- Build AMDGPU/DC with DCN316 support enabled. Missing or renamed fields should fail in `dcn316_resource.c`, `dcn30_dio_stream_encoder`, `dcn31_vpg`, `dcn31_afmt`, and DMUB DCN316 code.
- Mechanically verify that visible `__SHIFT` entries in lines 39767-42179 have matching `_MASK` entries for fields that the register schema defines as writable/readable bitfields.
- Diff this slice against AMD's authoritative DCN 3.1.6 register database and adjacent generated DCN 3.1.x headers where the hardware block is expected to be layout-compatible.
- Exercise HDMI modes that use generic packets: AVI, vendor, gamut, SPD, HDR static metadata, HF-VSIF, VRR/VTEM, deep color, scrambling above 340 MHz, and packet stop/restart paths.
- Exercise DP modes with secondary packets: audio, HDR metadata, DSC PPS, MST, MSO, ALPM, high refresh, and modes that require correct MSA/VBID timing.
- Run DSC display tests and check for PPS packet delivery, valid decompression, no corruption, and correct transition when DSC is enabled/disabled.
- Test VPG generic packet update paths with both immediate and frame-update modes, including repeated updates and conflict-polling behavior.
- Validate AFMT audio behavior across HDMI and DP: channel mapping, audio infoframes, 60958 channel status, mute/unmute, sample send, suspend/resume, and AFMT memory power transitions.
- Watch kernel logs and display diagnostics for DIG FIFO level errors, DP secondary-packet collision/deadline-missed flags, VPG conflict flags, audio mute/status mismatches, DSC failures, MST allocation problems, and resume-only failures.

## Cross-Chunk Notes

The previous chunk owns the beginning of the DP4 DPHY symbol group and earlier DP4 stream fields. Later chunks continue VPG1 after `VPG1_VPG_GSP_FRAME_UPDATE_CTRL` and cover the remaining VPG/DME/AFMT/DIG/DP instances and other generated DCN 3.1.6 register families. The final per-file report should merge adjacent chunks before making complete statements about all DCN316 stream encoders, all packet-generator instances, or the full `dcn_3_1_6_sh_mask.h` hardware map.
