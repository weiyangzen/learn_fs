# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 44386-46812

## Scope

This chunk is a generated AMD DCN 3.0.0 register shift/mask slice. It contains no C functions, structs, enums, variables, includes, locks, or executable logic. Its exported interface is entirely preprocessor constants of the form `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`, consumed with matching register-offset constants from `dcn_3_0_0_offset.h`.

The requested range contains 2,164 `#define` entries: 1,078 shift constants and 1,086 mask constants. It starts in the tail of `DIG3_HDMI_GENERIC_PACKET_CONTROL10`, finishes the remaining DIG3 HDMI/audio/TMDS/backend field masks, covers a complete `DP3` DisplayPort stream/link block, covers the `VPG4`, `AFMT4`, `DME4`, and `DIG4` stream-encoder companion blocks, and then enters `DP4` through `DP4_DP_MSA_TIMING_PARAM3`. The final requested line is only the `//DP4_DP_MSA_TIMING_PARAM4` section marker; its fields start after this chunk and should be handled by the following chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata, not distributed filesystem logic.

## Purpose

The purpose of this slice is to describe bit layouts for DCN 3.0 display I/O registers so driver code can program HDMI, TMDS, DisplayPort, audio, generic secondary-data packets, metadata packets, link training, MST allocation, DSC-over-DP control, and stream timing through symbolic field names instead of hard-coded bit positions.

The major hardware areas covered here are:

- DIG3 tail: HDMI generic packet double-buffer status, HDMI double-buffer control, HDMI ACR N/CTS values for 32/44.1/48 kHz families, AFMT audio clock status, DIG backend routing/enables, TMDS control characters, sync patterns, DC balancer fields, DIG version/lane enables, and forced disable.
- DP3: DisplayPort link, pixel format, MSA colorimetry/timing, video stream enable/status, steer FIFO, video M/N, DPHY training/test/scrambler/CRC/fast-training fields, secondary-data packet controls, audio M/N readback, MST/MSE payload timing and slot allocation, DSC mode/slice width, metadata transmission, ALPM, GSP8-GSP11, and generic-packet double-buffer status.
- VPG4: generic packet RAM access/data, frame and immediate update requests/pending flags for generic packets 0-14, generic packet conflict/lock status, VPG memory power, ISRC indexed data, and MPEG infoframe fields.
- AFMT4: HDMI/DP audio packet controls, audio infoframe bytes, IEC 60958 channel-status words, audio CRC/test ramp controls, audio status/ack fields, source select, infoframe update, and AFMT memory power.
- DME4: dynamic metadata engine enable, HUBP requestor select, stream type, double-buffer pending/taken/clear/disable, and DME memory power fields.
- DIG4: front-end source selection/start/bypass/input-pixel/Dolby Vision fields, output CRC, test/clock/random patterns, FIFO status, HDMI metadata/control/status/audio/ACR/VBI/infoframe/generic packet controls, HDMI double-buffering, AFMT bridge control, backend routing/enables, TMDS fields, lane enables, DIG version, and forced disable.
- DP4 partial: DisplayPort link, pixel format, MSA colorimetry, lane config, video stream control, timing, video M/N, link framing, HBR2 pattern, interrupt control, DPHY training/symbol/scrambler/CRC/fast-training, secondary packet/audio/MST/MSE controls, and MSA timing parameters 1-3.

## Important APIs, Types, And Macros

There are no callable APIs. The important API surface is the generated macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the bit offset for a field within a 32-bit MMIO register.
- `REGISTER__FIELD_MASK` gives the pre-shifted bit mask for that field.
- Register comments such as `//DP3_DP_SEC_CNTL` and address-block comments such as `// addressBlock: dce_dc_dio_dp3_dispdec` group constants by hardware register block.

Driver helper macros such as `FD_SHIFT`, `FD_MASK`, `REG_SET`, `REG_UPDATE`, and `REG_GET` depend on these names being stable. Stream-encoder register lists typically use token-pasting against instance 0 names in structure definitions while instance register tables map `DP`, `DIG`, `VPG`, `AFMT`, and `DME` IDs to concrete `DP3`, `DIG4`, and similar register names.

High-value field groups in this chunk include:

- Double-buffer state and synchronization: `HDMI_DB_PENDING`, `HDMI_DB_TAKEN`, `HDMI_DB_TAKEN_CLR`, `VUPDATE_DB_PENDING`, `DP_SEC_DB_*`, `METADATA_DB_*`, and generic packet update pending fields.
- DisplayPort link and stream control: `DP_LINK_TRAINING_COMPLETE`, `DP_LINK_STATUS`, `DP_VID_STREAM_ENABLE`, `DP_VID_STREAM_STATUS`, `DP_UDI_LANES`, `DP_PIXEL_ENCODING`, `DP_COMPONENT_DEPTH`, `DP_MSA_MISC0`, and MSA timing fields.
- Link training and diagnostics: `DPHY_TRAINING_PATTERN_SEL`, `DPHY_SCRAMBLER_BS_COUNT`, PRBS/scrambler controls, CRC enable/result/MST status fields, fast-training state/ack/mask fields, and HBR2 pattern controls.
- Secondary packet and audio transport: `DP_SEC_STREAM_ENABLE`, `DP_SEC_ASP_ENABLE`, `DP_SEC_GSP[0-7]_ENABLE`, `DP_SEC_GSP*_SEND`, deadline/pending/any-line fields, line-number fields, `DP_SEC_AUD_N/M` and readback fields, timestamp mode, packet coding/version/channel-count override, and collision/audio mute fields.
- MST and DSC: `DP_MSE_RATE_X/Y`, payload slot allocation tables/status, SAT update, link timing, blank-code/timestamp/zero-encoder controls, `DP_DSC_MODE`, `DP_DSC_SLICE_WIDTH`, and PPS/metadata-related GSP fields.
- HDMI/TMDS: HDMI control/status/audio/ACR/VBI/infoframe/generic packet fields, TMDS sync patterns, control character generation, DC balance, lane enables, backend/front-end source routing, and AVMUTE/general-control fields.
- Audio formatter fields: `AFMT_AUDIO_CHANNEL_ENABLE`, layout override/select, HBR and 60958 overrides, audio infoframe channel/count/type/allocation fields, CRC controls/results, FIFO overflow status/ack, and audio source selection.
- Memory and power fields: `VPG_MEM_PWR`, `AFMT_MEM_PWR`, and `DME_MEMORY_CONTROL` fields that describe low-power state controls for packet/audio/metadata helper blocks.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by display-driver consumers:

1. DCN 3.0 resource, IRQ, GPIO, clock, DIO, and DMUB code includes this mask header with the matching offset header.
2. Register-list macros build tables for stream encoders and supporting blocks using symbolic registers such as `DP_SEC_CNTL`, `AFMT_AUDIO_PACKET_CONTROL`, `DME_CONTROL`, and `HDMI_GENERIC_PACKET_CONTROL*`.
3. Field helper macros paste register and field tokens into this header's `SHIFT` and `MASK` constants.
4. Functional code then sequences MMIO reads/writes for modeset, link training, packet setup, audio enablement, metadata transmission, MST payload allocation, DSC setup, CRC/debug capture, suspend/resume, and interrupt handling.

The ordering in the header is still meaningful for generated-header maintenance. Each register normally lists all shift fields followed by masks; repeated instance blocks (`DP3` then `DP4`, `DIG3` then `DIG4`) are expected to remain structurally aligned where the hardware block is replicated.

## State And Persistence Behavior

The file persists no software state. It describes fields in hardware registers whose values persist according to DCN hardware rules until overwritten, reset, power-gated, or cleared by register-specific side effects.

State represented by this chunk includes:

- Stream encoder routing and enable state for DIG3 and DIG4, including FE/BE source selection, backend enable, symbol clock on/status, lane enables, and forced-disable controls.
- HDMI packet and audio state: generic packet line scheduling, immediate/frame update requests, double-buffer pending/taken state, AVMUTE, ACR N/CTS values, metadata packet configuration, and VBI/infoframe/audio controls.
- TMDS physical/link symbol state: control characters, sync patterns, DC balance, test/feedback paths, and static/random pattern generation.
- DP3 and DP4 stream state: active stream enable/status, pixel encoding/depth, MSA fields, video timing, M/N values, link framing, training pattern, scrambler/PRBS/CRC controls, DPHY status, and fast-training completion/ack state.
- DP secondary-packet state: stream/audio packet enablement, GSP scheduling, line references, collision status/ack, audio mute/status, audio M/N values, timestamp mode, and packet coding/version fields.
- MST state: MSE rate, payload slot allocation and status, SAT update pending, link frame/line timing, and related encoding controls.
- VPG4, AFMT4, and DME4 local RAM/power/status state for generic packets, ISRC/MPEG data, HDMI/DP audio formatting, audio CRC/test paths, and dynamic metadata packet generation.

Several fields are status, pending, ack, clear, or write-one-to-clear style controls. The macro names expose the bit location but do not encode access semantics. Consumers must know the register model before using a field in read/modify/write paths.

## Dependencies And Integration Points

This chunk depends on generated consistency with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, which supplies the corresponding `mm...` register offsets and `_BASE_IDX` selectors.
- DCN base-address headers such as `sienna_cichlid_ip_offset.h`, which make offset/base-index pairs addressable.
- AMD display register helpers that expand `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)` into the constants in this file.

Direct include sites in this tree include `display/dc/resource/dcn30/dcn30_resource.c`, `display/dc/irq/dcn30/irq_service_dcn30.c`, `display/dc/irq/dcn302/irq_service_dcn302.c`, `display/dc/gpio/dcn30/hw_factory_dcn30.c`, `display/dc/gpio/dcn30/hw_translate_dcn30.c`, `display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`, `display/dmub/src/dmub_dcn30.c`, and `display/dmub/src/dmub_dcn302.c`.

The most relevant functional integration is the DIO stream-encoder stack. `display/dc/dio/dcn10/dcn10_stream_encoder.h` defines register and field lists for AFMT audio controls, DP secondary-packet controls, DP audio N/M, metadata controls, and HDMI packet controls. Newer stream encoder implementations program the same conceptual registers with `REG_UPDATE`, `REG_SET`, and `REG_GET` for MSA timing, DP packet enablement, metadata packets, HDMI metadata, and audio enablement. This chunk supplies the instance-specific DCN 3.0 bit positions for those shared register-list abstractions.

## Risks And Edge Cases

- A wrong shift or mask can compile cleanly while corrupting a hardware field at runtime. This is especially risky for enable, ack, clear, and power fields.
- Chunk boundaries are artificial. The range starts after the beginning of `DIG3_HDMI_GENERIC_PACKET_CONTROL10` and ends before the fields for `DP4_DP_MSA_TIMING_PARAM4`; adjacent chunk research is required before making complete file-level claims.
- Repeated instance copy errors can be localized. `DP3` and `DP4`, and `DIG3` and `DIG4`, are similar but not safe to assume interchangeable; a single mismatched field can affect only one connector/encoder instance.
- Double-buffer and pending/taken fields are sequencing-sensitive. Misusing `*_TAKEN_CLR`, `*_DB_DISABLE`, or pending masks can cause stale HDMI/DP infoframes, metadata updates at the wrong vblank, or lost packet updates.
- DP secondary packet and GSP fields are dense and side-effect-prone. Incorrect `SEND`, `PENDING`, `DEADLINE_MISSED`, line-number, PPS, or any-line fields can break audio packets, HDR metadata, DSC PPS delivery, or MST secondary-data scheduling.
- DisplayPort link training and DPHY fields affect physical link stability. Errors in training pattern, scrambler, CRC, HBR2, or fast-training bits may present only at particular link rates, lane counts, panels, or resume paths.
- MSA timing, pixel format, and video M/N fields directly describe the stream sent to the sink. Wrong fields can cause blank displays, bad color/depth negotiation, timing mismatch, flicker, or audio/video synchronization failures.
- Audio formatter fields can fail silently as audio dropouts, incorrect channel mapping, wrong IEC 60958 status, HBR mode issues, FIFO overflow handling problems, or invalid HDMI/DP audio infoframes.
- Memory-power fields for VPG/AFMT/DME can interact with clock gating and block reset. Programming packet or metadata RAM while the block is in low-power state can lose updates or produce transient status conflicts.

## Test Signals

Useful validation signals are mostly build-time macro coverage plus hardware display behavior:

- Build AMDGPU/DC with DCN 3.0 and DCN 3.0.2 support enabled. Missing or renamed macros should fail where stream-encoder, IRQ, GPIO, clock, resource, or DMUB tables are generated.
- Mechanically compare this slice against the matching generated register database and `dcn_3_0_0_offset.h` to ensure every field mask/shift belongs to a register with a valid offset and that shift/mask pairs remain aligned.
- Exercise display outputs that map to DIG/DP instances 3 and 4: hotplug, modeset, DP link training, HDMI/TMDS modes, lane enable/disable, suspend/resume, and forced link-rate/lane-count combinations.
- Validate DP stream setup with RGB/YCbCr formats, different component depths, MSA timing programming, video M/N values, stream enable/disable deferral, and keepout behavior.
- Test DP secondary packet paths: audio playback, audio M/N readback, ASP/ATP/AIP/ACM packet enablement, GSP scheduling, generic packet send/pending/deadline flags, HDR/metadata packets, and DSC PPS delivery where supported.
- Exercise MST payload programming and status readback for MSE rate, SAT slot allocation, SAT update pending, and link timing fields.
- Run HDMI audio/infoframe paths on DIG3/DIG4: ACR N/CTS values, generic packet frame/immediate updates, double-buffer pending/taken/clear behavior, AVMUTE, VBI packet controls, and metadata packet delivery.
- Use CRC/debug features where available: DIG output CRC, DP DPHY CRC, audio CRC, TMDS test patterns, random/static test patterns, and FIFO/status readbacks.
- Watch kernel logs, display diagnostics, and sink behavior for link-training failures, AUX/DP timeouts, blanking, bad color format, audio FIFO overflow, missing HDR/DSC metadata, packet update conflicts, stuck pending bits, and resume-only regressions.

## Cross-Chunk Notes

This is a constants-only chunk. The final per-file report should merge it with neighboring chunks before drawing complete conclusions about the whole `dcn_3_0_0_sh_mask.h` file. In particular, the previous chunk owns the beginning of DIG3 HDMI generic packet control definitions, and the next chunk owns `DP4_DP_MSA_TIMING_PARAM4`, DP4 MSO, and the remaining DP4/next-block field definitions.
