# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 44670-47065

## Scope

This chunk is a generated AMD DCN 3.2.1 register-field shift/mask slice. It contains preprocessor constants only: 2,139 `#define` entries for bit positions and bit masks across 213 register groups. There are no C functions, structs, enums, branches, allocations, locks, direct MMIO operations, or durable-storage operations in this range.

The chunk begins in the middle of `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL13`, covers the tail of HPO `DP_SYM32_ENC0`, then covers repeated HPO DisplayPort stream encoder blocks for stream instances 1 and 2, and continues into stream instance 3. It ends in the middle of `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL6`; the remaining fields for that register and the rest of encoder 3 are in the next manifest chunk. Final file-level conclusions need to merge this with neighboring chunks.

## Purpose And Hardware Surface

This header is part of the AMDGPU Display Core register ABI for DCN 3.2.1. The paired `dcn_3_2_1_offset.h` file supplies MMIO register offsets; this `*_sh_mask.h` file supplies field shifts and unshifted 32-bit masks used by register helper macros to read, write, and wait on individual fields.

The hardware surface in this slice is centered on the HPO DisplayPort stream path:

- Tail of `DP_SYM32_ENC0`: generic secondary-data packet controls, SDP stream/audio controls, metadata packet controls, video MSA/VBID/stream controls, panel replay tunneling optimization, video CRC, memory power, and spare bits.
- `DP_STREAM_ENC1`, `DP_STREAM_ENC2`, and `DP_STREAM_ENC3`: stream encoder clock enable/status fields, pixel/audio input mux selectors, clock ramp adjuster FIFO control/status, FIFO calibration/read-level fields, and spare fields.
- `APG1`, `APG2`, and `APG3`: audio packet generator reset, enable, stream ID, debug audio generation, packet source selection, audio CRC control/result/status, FIFO overflow status/clear, output active status, memory power controls, and spare fields.
- `DME7`, `DME8`, and `DME9`: metadata engine requestor ID, engine enable, stream type, double-buffer pending/taken/clear/disable state, missed-transmission status/clear, and memory power controls.
- `VPG7`, `VPG8`, and `VPG9`: video packet generator generic packet data access, generic packet payload bytes, frame-update and immediate-update controls for generic packet slots 0-14, update-pending bits, conflict status/clear, memory power state, ISRC data access, and MPEG infoframe fields.
- `DP_SYM32_ENC1` and `DP_SYM32_ENC2`: full symbol encoder instances for video/SDP/audio/metadata, including reset/enable, pixel-to-symbol FIFO, MSA double-buffering, pixel format, MSA data words, HBlank minimum symbol width, 15 GSP control registers, audio mute/packet enables, metadata packet timing, stream/VBID controls, panel replay tunneling, CRC, memory power, and spare fields.
- Beginning of `DP_SYM32_ENC3`: reset/enable, video FIFO, MSA and pixel-format double buffering, pixel format, MSA data words, HBlank control, and GSP control registers 0 through part of 6.

The repeated instance pattern is deliberate. The generated names encode both block type and instance number, for example `VPG8_VPG_GSP_FRAME_UPDATE_CTRL__VPG_GENERIC12_FRAME_UPDATE_PENDING_MASK` or `DP_SYM32_ENC2_DP_SYM32_ENC_VID_STREAM_CONTROL__VID_STREAM_ENABLE_MASK`. This lets one set of runtime helper structures select the proper offsets and masks for each stream instance.

## Important Definitions

The naming convention is consistent across this chunk:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted 32-bit mask for the field.
- `//<REGISTER>` comments group field macros by register.
- `// addressBlock: ...` comments mark generated hardware address-block boundaries such as `dce_dc_hpo_dp_stream_enc1_dispdec`, `dce_dc_hpo_dp_stream_enc1_apg_apg_dispdec`, `dce_dc_hpo_dp_stream_enc1_dme_dme_dispdec`, `dce_dc_hpo_dp_stream_enc1_vpg_vpg_dispdec`, and the corresponding stream 2 and stream 3 blocks.

Important register families in this chunk:

- `DP_STREAM_ENC*_DP_STREAM_ENC_CLOCK_CONTROL` defines `DP_STREAM_ENC_CLOCK_EN` and clock-on status bits for `DISPCLK`, `SOCCLK`, `DPSTREAMCLK`, and `SYMCLK32`.
- `DP_STREAM_ENC*_DP_STREAM_ENC_INPUT_MUX_CONTROL` and `DP_STREAM_ENC*_DP_STREAM_ENC_AUDIO_CONTROL` define 3-bit pixel and audio stream source selectors.
- `DP_STREAM_ENC*_DP_STREAM_ENC_CLOCK_RAMP_ADJUSTER_FIFO_STATUS_CONTROL0/1` define FIFO enable/reset/read-start-level/read-clock-source/status/error fields and calibration/overwrite/min/max/average-level fields.
- `APG*_APG_CONTROL` and `APG*_APG_CONTROL2` define APG reset/done, enable, DisplayPort audio stream ID, and ASP channel-count override.
- `APG*_APG_DBG_GEN_CONTROL`, `APG*_APG_PACKET_CONTROL`, `APG*_APG_AUDIO_CRC_CONTROL*`, `APG*_APG_AUDIO_CRC_RESULT`, and `APG*_APG_STATUS*` define audio debug generation, ACP/audio-info source selection, audio CRC start/count/channel/result/done/clear, audio/HBR enable status, FIFO overflow status/clear, and output active state.
- `DME*_DME_CONTROL` defines metadata request routing and double-buffer lifecycle fields: `METADATA_HUBP_REQUESTOR_ID`, `METADATA_ENGINE_EN`, `METADATA_STREAM_TYPE`, `METADATA_DB_PENDING`, `METADATA_DB_TAKEN`, `METADATA_DB_TAKEN_CLR`, `METADATA_DB_DISABLE`, `METADATA_TRANSMISSION_MISSED`, and `METADATA_TRANSMISSION_MISSED_CLR`.
- `VPG*_VPG_GENERIC_PACKET_ACCESS_CTRL` and `VPG*_VPG_GENERIC_PACKET_DATA` define indexed writes of four generic packet bytes at a time.
- `VPG*_VPG_GSP_FRAME_UPDATE_CTRL` and `VPG*_VPG_GSP_IMMEDIATE_UPDATE_CTRL` define update request and pending bits for generic packet slots 0-14, split between low update bits and high pending bits.
- `VPG*_VPG_GENERIC_STATUS` defines lock/conflict status and conflict clear fields.
- `VPG*_VPG_ISRC1_2_*` and `VPG*_VPG_MPEG_INFO*` define indexed ISRC payload bytes and MPEG infoframe/checksum/update fields.
- `DP_SYM32_ENC*_DP_SYM32_ENC_CONTROL` defines symbol encoder enable/reset/reset-done.
- `DP_SYM32_ENC*_DP_SYM32_ENC_VID_FIFO_CONTROL` defines pixel-to-symbol FIFO enable/reset/reset-done/overflow.
- `DP_SYM32_ENC*_DP_SYM32_ENC_VID_PIXEL_FORMAT` defines DP 2.0-style pixel encoding, uncompressed encoding, and component depth fields.
- `DP_SYM32_ENC*_DP_SYM32_ENC_VID_MSA0` through `VID_MSA8` carry 32-bit MSA data words, while `VID_MSA_CONTROL` and `VID_MSA_DOUBLE_BUFFER_CONTROL` control MSA line timing, stereo override, and double-buffer state.
- `DP_SYM32_ENC*_DP_SYM32_ENC_SDP_GSP_CONTROL0-14` define per-generic-packet transmission policy: video/idle continuous transmission enables, one-shot trigger and trigger position, double-buffer enable/pending, payload size, SOF reference, transmission deadline missed/pending, and transmission line number.
- `DP_SYM32_ENC*_DP_SYM32_ENC_SDP_AUDIO_CONTROL0/1` define ASP/ATP/AIP/ACM/ISRC enables, ASP priority, ATP version, audio mute/status, and ASP concatenation sample-count controls for 2-channel, 8-channel, and HBR layouts.
- `DP_SYM32_ENC*_DP_SYM32_ENC_SDP_METADATA_PACKET_CONTROL` defines metadata packet enable, double-buffer enable/pending, SOF reference, and transmission line number.
- `DP_SYM32_ENC*_DP_SYM32_ENC_VID_STREAM_CONTROL`, `VID_VBID_CONTROL`, `VID_PANEL_REPLAY_CONTROL`, `VID_CRC_*`, and `MEM_POWER_CONTROL` define stream enable/status, compressed-stream VBID timing, panel replay tunneling optimization, video CRC control/result/valid state, and local memory low-power state.

## Control Flow And Runtime Behavior

This chunk has no executable control flow by itself. Runtime behavior appears when Display Core code includes `dcn_3_2_1_sh_mask.h`, initializes typed register shift/mask tables, and calls register helpers such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_WAIT`, and generated field macros such as `SE_SF(...)`.

The DCN321 resource path includes this header in `drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c` together with `dcn_3_2_1_offset.h`. That file initializes the HPO stream encoder, VPG, APG, stream encoder, and other register tables with macros such as `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST(__SHIFT)`, `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST(_MASK)`, `DCN3_VPG_MASK_SH_LIST(__SHIFT)`, and `DCN31_APG_MASK_SH_LIST(_MASK)`.

The main runtime flows that consume fields in this chunk include:

1. Resource construction maps generated offsets plus these shift/mask values into per-instance structures for HPO DP stream encoders, VPGs, APGs, and stream encoders.
2. HPO DP stream enable paths turn on `DP_STREAM_ENC_CLOCK_EN`, reset and enable `DP_SYM32_ENC`, route the input mux, enable the video stream, reset/enable the pixel-to-symbol FIFO, reset/enable the clock-ramp-adjuster FIFO, and optionally enable video CRC diagnostics.
3. Stream attribute programming uses `DP_SYM32_ENC_VID_PIXEL_FORMAT`, MSA data registers, MSA double buffering, VBID compressed stream timing, HBlank symbol width, metadata packet controls, and GSP packet controls.
4. Blank/disable paths clear `VID_STREAM_ENABLE`, wait on `VID_STREAM_STATUS`, disable SDP transmission, disable FIFOs, and eventually disable the symbol encoder and stream encoder clocks.
5. VPG paths write generic packet payload bytes through indexed access registers, then request frame-bound or immediate update for generic packet slots and monitor conflict/pending status.
6. APG paths reset/enable audio packet generation, assign DisplayPort audio stream IDs, configure debug generation and audio CRC, and monitor audio enable/HBR/FIFO overflow/output-active state.
7. DME paths enable metadata delivery from a selected HUBP requestor, use metadata double-buffer state, and clear taken or missed-transmission status.

## State And Persistence Behavior

The state represented here is hardware register state, not driver-owned persistent data. It persists only as long as the relevant display hardware remains powered and configured, and can be reset or overwritten by modesets, link retraining, hotplug handling, power gating, suspend/resume, or firmware/display microcontroller activity.

Programmed state includes:

- Stream encoder clock enables, mux selections, FIFO read levels, FIFO overwrite/calibration controls, and symbol encoder enable/reset state.
- Video stream enable, pixel format, MSA data words, MSA and pixel-format double-buffer enables, HBlank minimum symbol width, and compressed-stream VBID timing.
- SDP stream enable, GSP transmission policy, GSP payload size, SOF references, line numbers, metadata packet enable/timing, and audio packet enables/mute.
- APG enable, DP audio stream ID, debug generation, packet source selection, audio CRC parameters, and APG memory power controls.
- DME metadata requestor ID, engine enable, stream type, DB disable, and DME memory power controls.
- VPG generic packet bytes, packet update requests, ISRC data bytes, MPEG info fields, and VPG memory power controls.

Volatile readback/status includes:

- FIFO reset done, video stream active, FIFO error, FIFO min/max/average/calibrated status, `VID_STREAM_STATUS`, CRC valid/results, audio mute status, and memory power state.
- GSP trigger-pending, double-buffer-pending, and deadline-missed fields.
- APG reset done, audio/HBR enable status, FIFO overflow status, output active state, audio CRC done/result, and memory power state.
- DME DB pending/taken, metadata transmission missed, and memory power state.
- VPG generic lock/conflict status and update-pending bits for frame and immediate packet updates.

Side-effecting fields need special care: reset toggles, status clear bits such as `APG_AUDIO_FIFO_OVERFLOW_STATUS_CLEAR`, `APG_AUDIO_CRC_DONE_CLEAR`, `METADATA_DB_TAKEN_CLR`, `METADATA_TRANSMISSION_MISSED_CLR`, `VPG_GENERIC_CONFLICT_CLR`, one-shot GSP triggers, update requests, FIFO recalibration/recompute controls, and memory-power force fields can change hardware state when written.

## Dependencies And Integration Points

This chunk depends on generated-name consistency across the DCN 3.2.1 register header set. The register names in this file must match offsets in `dcn_3_2_1_offset.h` and the field names expected by Display Core mask-list macros. A missing macro is usually a compile-time failure; a wrong numeric shift or mask can compile and fail only on real hardware.

Primary integration points include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`, which includes `dcn_3_2_1_sh_mask.h` and builds DCN321 register, shift, and mask tables.
- `drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h`, where `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST` consumes `DP_STREAM_ENC0_*` and `DP_SYM32_ENC0_*` field names from generated headers and maps them into reusable per-instance field structures.
- `drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.c`, which uses the HPO stream encoder register helpers for clock enable, reset/wait, FIFO reset/enable, stream enable/status, pixel format, MSA, SDP, metadata, audio, and CRC operations.
- `drivers/gpu/drm/amd/display/dc/dcn30/dcn30_vpg.h` and VPG implementation code, which consume `VPG*_VPG_*` fields for generic packet payload writes, update triggering, and conflict handling.
- `drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.h` and APG implementation code, which consume `APG*_APG_*` fields for HPO audio packet generation.
- Shared register helper infrastructure in `reg_helper.h`, where `_SHIFT` and `_MASK` constants become typed values used by `REG_*` macros.

The generated instance-0 mask lists often reference `DP_STREAM_ENC0_*`, `DP_SYM32_ENC0_*`, `VPG0_*`, or `APG0_*` field names and then reuse those shift/mask values for other instances through per-instance offset tables. This works only if the repeated hardware instances keep identical field layouts. This chunk shows repeated layouts for stream/APG/VPG/DME/SYM32 instances 1-3, so it is a useful cross-check against the instance-0 definitions in earlier chunks.

## Risks And Maintenance Notes

- Numeric drift in these generated constants is the highest risk. Incorrect masks for stream enables, reset-done bits, FIFO controls, packet update requests, metadata DB clears, or audio CRC/status fields can compile cleanly and produce runtime-only display/audio/metadata failures.
- The chunk boundaries split real register groups. `DP_SYM32_ENC0_SDP_GSP_CONTROL13` is partial at the start, and `DP_SYM32_ENC3_SDP_GSP_CONTROL6` is partial at the end. Any audit that checks field completeness must include adjacent chunks.
- Repeated instance families create copy-generation hazards. `DP_STREAM_ENC1/2/3`, `APG1/2/3`, `DME7/8/9`, `VPG7/8/9`, and `DP_SYM32_ENC1/2/3` are similar, but code may still rely on a subset of instance-0 fields. Cross-instance differences must be intentional and verified against the hardware register database.
- GSP and VPG update controls are timing-sensitive. Wrong update or pending masks can leave stale HDR/metadata/generic packets active, miss a frame update, or trigger a packet at the wrong time.
- Metadata and audio clear bits are side-effecting. A bad clear mask can hide metadata transmission misses, leave `DB_TAKEN` asserted, clear the wrong APG FIFO overflow, or make CRC diagnostics unreliable.
- FIFO reset and calibration fields are in display timing paths. Bad reset-done, enable, level, or error masks can cause black screens, intermittent stream start failures, or timing-dependent failures after modeset and resume.
- Memory-power force/default/state fields appear for APG, DME, VPG, and SYM32 blocks. Wrong masks can cause excess power draw, inaccessible memories during packet updates, or failures only around clock/power transitions.
- Panel replay tunneling and compressed-stream VBID fields are user-visible only on specific panels or compressed stream configurations, so regressions may escape basic display tests.

## Test Signals

Useful validation should combine build-time checks with DCN321 hardware behavior:

- Build AMDGPU Display Core with DCN321 enabled and confirm `dcn321_resource.c` resolves `dcn_3_2_1_sh_mask.h` and all HPO stream encoder, VPG, APG, and DME mask-list fields.
- Run generated-header consistency checks for this range: paired `_SHIFT`/`_MASK` definitions, 32-bit mask width, no unexpected field overlap within a register, and expected repeated layouts across instances 1, 2, and 3.
- Exercise HPO DisplayPort stream enable/blank/disable on streams backed by `DP_STREAM_ENC1`, `DP_STREAM_ENC2`, and `DP_STREAM_ENC3`; monitor reset-done bits, `VID_STREAM_STATUS`, FIFO reset/enable state, and FIFO error fields.
- Validate stream attribute changes across RGB, YCbCr444, YCbCr422, YCbCr420, 8/10/12 bpc, compressed stream, and double-buffered updates; watch MSA/pixel-format pending behavior and VBID compressed-stream timing.
- Test SDP and GSP packet delivery with HDR metadata, adaptive sync metadata, DSC-related packets, audio sample/timestamp packets, and generic packet slots 0-14; monitor GSP pending, double-buffer pending, deadline-missed, and VPG update-pending/conflict signals.
- Validate APG audio paths with basic audio, HBR audio where available, stream ID changes, audio mute/unmute, FIFO overflow status/clear, and APG audio CRC done/result handling.
- Exercise DME metadata flows with multiple HUBP requestor IDs, metadata stream types, double-buffer update/taken/clear behavior, DB disable, and missed-transmission clear/status.
- Stress power transitions: display idle, blank/unblank, hotplug, suspend/resume, and power gating while checking APG/DME/VPG/SYM32 memory power state fields and packet/FIFO recovery.
- Use CRC and status diagnostics: video CRC valid/result fields, APG audio CRC result, VPG generic conflict status, FIFO calibrated/min/max/error state, metadata missed status, and GSP deadline-missed bits before and after modesets and packet updates.

## Chunk-Specific Summary

Lines 44670-47065 define DCN 3.2.1 bit shifts and masks for the tail of HPO symbol encoder 0, full stream/APG/DME/VPG/SYM32 coverage for stream instances 1 and 2, and the beginning of stream instance 3. The content is generated register ABI rather than executable logic. Correctness depends on exact numeric field values, instance-prefix consistency, careful handling of side-effecting reset/clear/update/trigger fields, and validation across HPO DisplayPort stream bring-up, packet generation, metadata, audio, FIFO, CRC, and power-management scenarios.
