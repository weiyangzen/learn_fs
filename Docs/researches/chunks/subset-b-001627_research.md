# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 42128-44549

## Scope And Purpose

This chunk is generated AMD DCN 2.0 register bitfield metadata. It contains no executable C logic. Its purpose is to publish compile-time `__SHIFT` and `_MASK` constants used by AMDGPU display-core register helpers to pack, update, and read fields inside MMIO registers.

The file is under a local `ceph-client` source mirror, but this path is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The range contains 2,166 macros: 1,083 field shifts and 1,083 matching masks. The chunk starts at the tail of the DP1 DisplayPort block, covers the full DIG2/DP2 instance pair, and enters the DIG3 block:

- `DP1_DP_MSA_TIMING_PARAM*`, `DP1_DP_MSO_*`, `DP1_DP_DSC_*`, `DP1_DP_SEC_*`, `DP1_DP_DB_CNTL`, `DP1_DP_MSA_VBID_MISC`, `DP1_DP_SEC_METADATA_TRANSMISSION`, `DP1_DP_DSC_BYTES_PER_PIXEL`, and `DP1_DP_ALPM_CNTL`.
- `DIG2_*` display encoder front-end/back-end, HDMI, audio formatter, generic packet, ACR, ISRC, MPEG, CRC, FIFO, TMDS, lane enable, and force-disable fields.
- `DP2_*` DisplayPort link, pixel format, MSA, stream, DPHY, CRC, secondary packet, audio timestamp, MST slot allocation, MSO, DSC, metadata, double-buffer, and ALPM fields.
- The beginning of `DIG3_*`, covering the same display encoder/HDMI/audio/TMDS families as `DIG2` through `DIG3_DIG_BE_EN_CNTL`.

Every macro follows the generated naming contract `<INSTANCE>_<REGISTER>__<FIELD>__SHIFT` or `<INSTANCE>_<REGISTER>__<FIELD>_MASK`. The corresponding register offsets are in `dcn_2_0_0_offset.h`, including `mmDP1_DP_MSO_CNTL`, `mmDIG2_DIG_FE_CNTL`, `mmDP2_DP_LINK_CNTL`, and `mmDIG3_DIG_FE_CNTL`.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or storage objects in this range. The public interface is the macro set consumed by register-table initializers and register access helpers.

Important macro families:

- DP MSA timing fields: `DP*_DP_MSA_TIMING_PARAM1` through `PARAM4` pack vertical/horizontal totals, starts, sync widths, sync polarities, active height, and active width. These fields are used when software explicitly writes DP main stream attribute timing values.
- DP MSO/DSC fields: `DP*_DP_MSO_CNTL`, `DP*_DP_MSO_CNTL1`, `DP*_DP_DSC_CNTL`, and `DP*_DP_DSC_BYTES_PER_PIXEL` describe multi-stream output link grouping, secondary-packet enable routing per SST link, DSC mode, DSC slice width, and compressed bytes-per-pixel programming.
- DP secondary packet and metadata fields: `DP*_DP_SEC_CNTL2` through `CNTL7`, `DP*_DP_SEC_METADATA_TRANSMISSION`, `DP*_DP_SEC_FRAMING*`, `DP*_DP_SEC_PACKET_CNTL`, and audio `N`/`M`/timestamp fields cover GSP packet send requests, pending/deadline status, line targeting, active/idle state, metadata packet mode, audio packet coding, and DP secondary-packet framing.
- DP link and DPHY fields: `DP2_DP_LINK_CNTL`, `DP2_DP_PIXEL_FORMAT`, `DP2_DP_CONFIG`, `DP2_DP_VID_STREAM_CNTL`, `DP2_DP_STEER_FIFO`, `DP2_DP_DPHY_*`, `DP2_DP_DPHY_CRC_*`, `DP2_DP_DPHY_FAST_TRAINING*`, `DP2_DP_MSE_*`, and `DP2_DP_ALPM_CNTL` cover training status, lane count, stream enable/deferred disable, steering FIFO status/ack/masks, training patterns, scrambler/PRBS/test symbols, CRC capture, fast training, MST slot allocation, and alternate low-power mode.
- DIG front/back end fields: `DIG[2-3]_DIG_FE_CNTL`, `DIG[2-3]_DIG_BE_CNTL`, `DIG[2-3]_DIG_BE_EN_CNTL`, `DIG[2-3]_DIG_LANE_ENABLE`, `DIG[2-3]_DIG_OUTPUT_CRC_*`, `DIG[2-3]_DIG_FIFO_STATUS`, `DIG[2-3]_DIG_TEST_PATTERN`, and `DIG[2-3]_DIG_VERSION` cover stream source select, stereo sync, digital bypass, TMDS encoding/color format, back-end enable, mode/HPD select, lane enables, output CRC, FIFO underflow/overflow, random test patterns, and version/status fields.
- HDMI packet fields: `DIG[2-3]_HDMI_METADATA_PACKET_CONTROL`, `HDMI_GENERIC_PACKET_CONTROL*`, `HDMI_CONTROL`, `HDMI_STATUS`, `HDMI_AUDIO_PACKET_CONTROL`, `HDMI_ACR_PACKET_CONTROL`, `HDMI_INFOFRAME_CONTROL*`, `HDMI_GC`, and `HDMI_DB_CONTROL` define HDMI infoframe/generic-packet send modes, ACR packet behavior, audio layout/sample controls, deep-color and YCbCr420 indications, VBI packet update state, and HDMI double-buffer controls.
- AFMT/audio fields: `DIG[2-3]_AFMT_AUDIO_PACKET_CONTROL*`, `AFMT_AUDIO_INFO*`, `AFMT_60958_*`, `AFMT_AUDIO_CRC_*`, `AFMT_RAMP_CONTROL*`, `AFMT_STATUS`, `AFMT_AUDIO_SRC_CONTROL`, `AFMT_CNTL`, and `AFMT_VBI_PACKET_CONTROL*` define audio channel enable/layout overrides, IEC 60958 channel-status words, audio infoframe payload, audio CRC/ramp test controls, FIFO overflow/ack, generic packet lock/conflict/update state, and audio source selection.
- Generic packet payload fields: `DIG[2-3]_AFMT_GENERIC_HDR` and `AFMT_GENERIC_0` through `AFMT_GENERIC_7` provide byte-level masks for generic packet header bytes and payload bytes 0 through 31. ISRC and MPEG infoframe families similarly expose byte or bitfield packing for their payloads.
- TMDS fields: `DIG[2-3]_TMDS_CNTL`, `TMDS_CONTROL_CHAR`, `TMDS_CONTROL0_FEEDBACK`, `TMDS_STEREOSYNC_CTL_SEL`, `TMDS_SYNC_CHAR_PATTERN_*`, `TMDS_CTL_BITS`, `TMDS_DCBALANCER_CONTROL`, `TMDS_SYNC_DCBALANCE_CHAR`, and `TMDS_CTL*_GEN_CNTL` describe HDMI/DVI TMDS sync/control character generation, DC balancer settings, control-bit outputs, per-control data selection/delay/invert/modulation, and feedback paths.

Consumer-side APIs are macro-driven rather than function calls:

- `SE_SF(...)` and `LE_SF(...)` in stream/link encoder headers store field shifts and masks into per-block `mask_sh` structs.
- `SRI(...)` and related register-list macros pair offsets from `dcn_2_0_0_offset.h` with these bitfield constants.
- `REG_SET`, `REG_SET_2`, `REG_SET_4`, `REG_UPDATE`, `REG_UPDATE_3`, `REG_GET`, and `REG_WAIT` use the masks/shifts to modify or poll fields without hand-written bit arithmetic.

## Control Flow

This header chunk has no internal runtime control flow. Its data flow is compile-time substitution: DCN 2.0 code includes `dcn_2_0_0_sh_mask.h`, expands the generated macro names into field masks and shifts, and then the DC register helpers use those constants during MMIO reads, writes, updates, and waits.

Representative runtime flows in local consumers:

- `display/dc/dce/dce_stream_encoder.h` and `display/dc/dio/dcn10/dcn10_stream_encoder.h` list the DIG/DP/AFMT/HDMI registers and field names consumed by stream encoder code. The chunk supplies many of the backing masks for fields such as `DP_MSA_HTOTAL`, `DP_SEC_GSP4_SEND`, `HDMI_ACR_CTS_32`, `AFMT_60958_CS_CHANNEL_NUMBER_*`, `AFMT_AUDIO_SAMPLE_SEND`, and `DIG_SOURCE_SELECT`.
- `display/dc/dio/dcn10/dcn10_stream_encoder.c` programs DP MSA timing with `REG_SET_2` and `REG_SET_4`, triggers DP secondary GSP packets through `DP_SEC_CNTL2`, waits for packet send pending state, and programs HDMI ACR `CTS`/`N` values using the masks provided here.
- `display/dc/dce/dce_stream_encoder.c` has parallel DCE stream-encoder flows for MSA timing, HDMI ACR, and AFMT/audio/infoframe programming.
- `display/dc/dio/dcn10/dcn10_link_encoder.h` maps link-encoder register fields for DP link training, stream enable, DP lane count, MSE slot allocation, DPHY training, scrambler, PRBS, HBR2 pattern, and DIG back-end enable/mode/source fields. This chunk supplies the DP2 and DIG2/DIG3 instance-specific field constants for those generic field names.
- `display/dc/dio/dcn20/dcn20_link_encoder.h` extends the link-encoder masks for DCN2 features such as FEC and lane enable, while still relying on the generated DCN2 mask/header convention used by this chunk.
- `display/dmub/src/dmub_dcn20.c`, `display/dc/resource/dcn20/dcn20_resource.c`, `display/dc/irq/dcn20/irq_service_dcn20.c`, `display/dc/gpio/dcn20/hw_factory_dcn20.c`, and `display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c` include the DCN 2.0 offset and mask headers as part of DCN20 device/resource integration.

Because this file is declarative, it does not enforce required sequencing. Consumers must decide when to take update locks, program timing before stream enable, wait for packet pending bits, clear sticky status bits, avoid writing status-only fields, sequence DP link training, and coordinate HDMI/audio metadata updates with vblank or frame boundaries.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. The macros describe fields in hardware MMIO registers.

The represented hardware state includes:

- DP link and stream state: link training complete/status, eDP mode, lane count, stream enable/status, deferred disable, video timing, MSA misc/VBID, pixel encoding/depth/range, DPHY training/scrambler/PRBS/test/CRC state, fast-training status, FEC-adjacent DPHY control fields, and ALPM controls.
- DP secondary data state: audio `N`/`M` programming and readbacks, secondary timestamps, packet coding/category/channel overrides, GSP send/pending/deadline/line-number state, metadata packet enable/mode, and packet-active/idle indicators.
- MST/MSO/DSC state: MSE rate programming, slot allocation table entries and status readbacks, link timing, blank/timestamp modes, MSO SST-link mapping, DSC mode/slice width, and DSC bytes-per-pixel.
- DIG routing/encoding state: source selection, stereo sync, bypass, stream-start/symclock indicators, back-end mode and HPD selection, lane enable bits, output CRC configuration/results, test/random patterns, and FIFO status.
- HDMI state: metadata and generic packet sends, infoframe updates, audio packet control, ACR auto-send/source/priority and `CTS`/`N` values, deep color, YCbCr420, VBI state, double-buffer lock/update behavior, and HDMI status.
- AFMT/audio state: audio sample send enable, audio source selection, channel layout and channel enables, IEC 60958 channel status, audio infoframe payload, CRC/ramp test configuration/results, FIFO overflow/ack bits, generic packet payload buffers, ISRC and MPEG infoframes, and audio-clock/status fields.
- TMDS state: sync/control character patterns, control-bit generation, feedback delay/select, stereo sync select, DC balancer enable/test/force settings, and per-control signal generation.

Persistence is hardware-specific and not encoded in this file. Some fields are durable programming knobs that remain until a modeset, reset, power-gating transition, suspend/resume, or explicit rewrite. Others are read-only status, sticky interrupt/status, write-one-to-clear acknowledgements, self-clearing send/update requests, pending bits, line-number latches, CRC result fields, or double-buffered values latched at frame boundaries. Names such as `*_STATUS`, `*_ACK`, `*_CLR`, `*_PENDING`, `*_SEND`, `*_UPDATE`, `*_LOCK`, `*_DONE`, and `*_READBACK` signal possible side effects but do not define access type by themselves.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header contract:

- `dcn_2_0_0_offset.h` supplies the matching MMIO register offsets for these field masks and shifts.
- DCN/DCE enum headers and DisplayPort/HDMI/DSC protocol definitions supply legal symbolic field values.
- AMD display register helper macros in `drivers/gpu/drm/amd/display/dc` use the mask/shift structs initialized from these macros.

Direct and practical integration points include:

- Stream encoder setup for DP, HDMI, and audio formatter programming in `display/dc/dio/dcn10/dcn10_stream_encoder.*` and `display/dc/dce/dce_stream_encoder.*`.
- Link encoder setup for DP link training, DPHY, MST slot allocation, DIG back-end routing, HDMI/TMDS mode, lane enable, and hotplug-linked back-end selection in `display/dc/dio/dcn10/dcn10_link_encoder.*` and `display/dc/dio/dcn20/dcn20_link_encoder.*`.
- DCN20 resource construction in `display/dc/resource/dcn20/dcn20_resource.c`, which ties the generated offsets/masks to instantiated display resources.
- DMUB, IRQ, GPIO, and clock-manager integration that includes the DCN2 generated headers for hardware-service and display-resource operation.
- Diagnostic and validation paths that read output CRC, DPHY CRC, AFMT audio CRC, FIFO status, link status, MSE status, packet pending/deadline flags, and HDMI/AFMT status fields.

## Risks And Edge Cases

- These constants are hardware ABI. A wrong mask or shift can compile cleanly but write the wrong bits in a live display register.
- The chunk boundary is not semantic. It starts after the first two `DP1_DP_MSE_SAT2_STATUS` lines and ends after `DIG3_DIG_BE_EN_CNTL`, leaving complete DP1 context before the chunk and the rest of DIG3 after it to adjacent chunks.
- Instance repetition is easy to damage manually. `DIG2` and `DIG3` share many field layouts, while `DP1` and `DP2` share the later DP register families. One incorrect instance prefix or copied mask can affect only one physical encoder or connector path.
- DP MSA timing masks are timing-critical. Incorrect total/start/sync/active fields can cause black screens, bad link timing, incorrect sink-reported video parameters, flicker, or failed modesets.
- DP secondary packet fields have request, pending, deadline, and line-target side effects. Bad masks can leave HDR/metadata/audio packets unsent, sent on the wrong line, repeatedly pending, or reported as deadline-missed.
- MST/MSO/DSC fields are bandwidth and packetization critical. Slot-count, source, MSO link-count, DSC mode, slice-width, or bytes-per-pixel drift can produce corrupted MST streams, broken DSC output, or link bandwidth mismatches.
- HDMI ACR and AFMT fields are audio-critical. Bad `CTS`/`N`, channel status, layout, sample-send, FIFO-ack, or audio-source masks can cause silent audio, wrong channel mapping, audio drift, or FIFO overflow loops.
- Generic packet and infoframe byte masks directly shape HDMI/DP metadata payloads. Incorrect payload-byte masks can corrupt AVI, audio, HDR/generic, ISRC, or MPEG packets while leaving video otherwise functional.
- TMDS control/DC-balancer fields are encoding-critical for HDMI/DVI. Wrong bit positions can produce sink compatibility failures, intermittent display loss, or subtle link errors.
- Status/ack/clear fields are intermixed with programming fields in the same generated header. Using a `_MASK` without respecting hardware access semantics can accidentally clear sticky state or fail to acknowledge a condition.

## Test Signals

Useful validation is build coverage plus hardware/display behavior:

- Build AMDGPU/DC with DCN20 support enabled. Missing or renamed macros should fail in DCN20 stream encoder, link encoder, resource, DMUB, IRQ, GPIO, or clock-manager paths.
- Compare this generated mask range against the matching `dcn_2_0_0_offset.h` range and adjacent DCN family headers such as `dcn_2_0_1_sh_mask.h`, `dcn_2_1_0_sh_mask.h`, and `dcn_3_0_0_sh_mask.h` to catch unintended instance or field-layout drift.
- Exercise DP modesets on DCN20 hardware through the relevant DP1/DP2 paths: link training, stream enable/disable, lane-count changes, MST slot allocation, DSC where supported, MSO where supported, suspend/resume, and hotplug.
- Validate DP timing and metadata: correct MSA values at the sink, stable vblank/page flips, HDR or other GSP metadata delivery, audio over DP, no stuck `DP_SEC_*_PENDING`, and no repeated deadline-missed status.
- Exercise HDMI/DVI on DIG2/DIG3 paths: TMDS mode, deep color, YCbCr420, generic/infoframe packets, HDMI audio ACR, AFMT channel layout, audio source selection, and audio FIFO overflow recovery.
- Run diagnostic reads for output CRC, DPHY CRC, AFMT audio CRC, FIFO status, HDMI/AFMT status, MSE slot status, and link status; mismatches or stuck status bits are strong signals of mask/shift issues.
- Watch kernel logs and display behavior for black screens, flicker, failed link training, MST topology failures, DSC corruption, missed vblank/page-flip completion, audio silence or drift, EDID/hotplug instability on encoder paths, CRC mismatches, FIFO overflow messages, and suspend/resume regressions.
