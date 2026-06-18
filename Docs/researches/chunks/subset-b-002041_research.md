# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 34937-37346

## Scope

This chunk is a generated DCN 3.2.1 register-field shift/mask slice for AMDGPU Display Core. It contains preprocessor constants only: 2,164 `#define` entries in this range, with 1,081 `_SHIFT` macros and 1,083 `_MASK` macros. There are no C functions, structs, enums, executable branches, allocations, locks, or direct MMIO accesses in the chunk.

The range starts inside the `DIG4_HDMI_STATUS` register, after the earlier status field shifts from the preceding chunk, and continues through the rest of the `DIG4` HDMI, audio-format, backend, and TMDS field definitions. It then covers five repeated DIO-associated audio-format blocks, `AFMT0` through `AFMT4`; five dynamic metadata engine blocks, `DME0` through `DME4`; five video packet generator blocks, `VPG0` through `VPG4`; and ends at the beginning of the `DP_AUX0_AUX_CONTROL` field list. The final `DP_AUX0_AUX_CONTROL__SPARE_1_MASK` and subsequent AUX fields are outside this chunk.

## Purpose And Hardware Surface

This header is part of the generated register ABI used by the DCN 3.2.1 display driver. The companion offset header names the MMIO registers, while this file supplies the bit positions and masks used by register helper macros to pack fields into 32-bit hardware registers and extract readback/status fields.

Major hardware areas represented here:

- `DIG4` HDMI packet generation and status: HDMI audio delay, ACR generation, VBI packets, audio/MPEG infoframes, 15 generic packet slots, generic packet line scheduling, generic packet checksums, double-buffer enable/pending state, general-control packet fields, ACR N/CTS values for 32/44.1/48 kHz families, and ACR readback.
- `DIG4` digital backend and TMDS output: AFMT audio clock gating, backend enable/source/mode/HPD select, TMDS sync phase, control characters, feedback path selection, stereo sync selection, sync patterns, TMDS control bits, DC balancer controls, generated control-symbol controls, digital version, and force-disable state.
- `AFMT0` through `AFMT4`: per-DIO audio formatting blocks for HDMI/DP audio packet limits, audio layout/channel/stream selection, audio infoframe bytes, IEC 60958 channel-status fields, audio CRC test/readback, audio ramp/test data, AFMT status, audio sample send controls, audio source selection, and AFMT memory power state.
- `DME0` through `DME4`: per-DIO dynamic metadata engines with HUBP requestor selection, enable, stream type, double-buffer pending/taken/clear/disable state, missed-transmission status/clear, and DME memory power controls.
- `VPG0` through `VPG4`: per-DIO video packet generators for indexed generic packet data bytes, frame-update and immediate-update triggers for generic packet slots 0-14, update-pending readback, conflict status/clear, GSP memory power controls, ISRC indexed data access, and MPEG infoframe payload/update fields.
- `DP_AUX0_AUX_CONTROL`: the opening of the first DP AUX block, including AUX enable/reset/read/update-disable behavior, HPD-disconnect handling, mode detect, HPD selection, impedance calibration request enable, test mode, deglitch, and spare fields.

## Important Definitions

The naming convention is consistent with generated AMD DC register headers:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted 32-bit field mask.
- `//<REGISTER>` comments group fields by register.
- `// addressBlock: ...` comments mark generated hardware block boundaries such as `dce_dc_dio_dig0_afmt_afmt_dispdec`, `dce_dc_dio_dig0_dme_dme_dispdec`, `dce_dc_dio_dig0_vpg_vpg_dispdec`, and `dce_dc_dio_dp_aux0_dispdec`.

Important macro families in this chunk:

- `DIG4_HDMI_GENERIC_PACKET_CONTROL0/6` define send, continuous-send, line-reference, and update-lock-disable bits for HDMI generic packet slots 0-14. `CONTROL1/2/3/4/7/8/9/10` provide line-number scheduling, checksum bytes, double-buffer enable bits, and double-buffer pending status for those slots.
- `DIG4_HDMI_DB_CONTROL` defines packet double-buffer handshake state: pending, taken, clear, lock, disable, and vupdate-pending/taken/clear fields.
- `DIG4_HDMI_ACR_*` and `DIG4_HDMI_ACR_STATUS_*` define audio clock regeneration CTS/N programming and readback fields. The fixed 20-bit masks are used for HDMI audio sample-rate timing families.
- `DIG4_TMDS_*` define TMDS serializer and control-symbol behavior, including control-character enable, feedback selection/delay, sync character patterns, DC-balance behavior, generated CTL0-CTL3 data select/delay/invert/modulation/feedback/pattern fields, and the two-bit counter enable.
- `AFMTn_AFMT_AUDIO_PACKET_CONTROL2`, `AFMTn_AFMT_AUDIO_INFO0/1`, `AFMTn_AFMT_60958_0/1/2`, and `AFMTn_AFMT_AUDIO_PACKET_CONTROL` are repeated for instances 0-4. They are the per-stream audio-format programming surface used to route audio source IDs, select audio layout/channel map, program HDMI audio infoframes and IEC 60958 channel status, trigger channel-status updates, and control audio sample sending.
- `AFMTn_AFMT_AUDIO_CRC_CONTROL/RESULT`, `AFMTn_AFMT_RAMP_CONTROL0-3`, and `AFMTn_AFMT_STATUS` define audio diagnostics and status: CRC enable/continuous/source/channel/count, CRC completion/result, generated ramp bounds/increment/decrement, FIFO overflow, HBR state, audio-enable state, and audio-enable-change status.
- `DMEn_DME_CONTROL` defines metadata-engine runtime state and side-effecting status clear bits for dynamic metadata transmission. `DMEn_DME_MEMORY_CONTROL` defines memory power force/disable/state/default-low-power fields.
- `VPGn_VPG_GENERIC_PACKET_ACCESS_CTRL` and `VPGn_VPG_GENERIC_PACKET_DATA` define indexed payload access to generic packet data. `VPGn_VPG_GSP_FRAME_UPDATE_CTRL` and `VPGn_VPG_GSP_IMMEDIATE_UPDATE_CTRL` define frame-synchronous versus immediate update requests plus corresponding pending readback for generic packets 0-14.
- `VPGn_VPG_GENERIC_STATUS`, `VPGn_VPG_MEM_PWR`, `VPGn_VPG_ISRC1_2_*`, and `VPGn_VPG_MPEG_INFO*` define packet update conflict handling, GSP memory light-sleep state, ISRC payload byte access, and MPEG infoframe bytes/update state.
- `DP_AUX0_AUX_CONTROL` starts the AUX channel control surface, but this chunk only contains part of that register's definitions. The next chunk is needed for the complete AUX0 block.

## Control Flow And State Behavior

This chunk has no executable control flow. Runtime behavior comes from Display Core code that includes `dcn_3_2_1_offset.h` and `dcn_3_2_1_sh_mask.h`, initializes register/shift/mask tables, and then uses helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, `REG_WAIT`, `SRI(...)`, `SR_ARR(...)`, and `SE_SF(...)` to access MMIO registers.

Typical runtime flow using these fields:

1. `dcn321_resource.c` includes the DCN 3.2.1 generated offset and shift/mask headers and expands mask-list macros into typed shift and mask structures for stream encoders, VPG, AFMT, DIO, AUX, and related blocks.
2. During stream encoder construction, per-instance register tables map logical stream encoder objects onto `DIG`, `AFMT`, `DME`, and `VPG` register instances. The repeated `AFMT0-4`, `DME0-4`, and `VPG0-4` fields in this chunk supply the instance-zero field names used by the `SE_SF(...)` style macros, then are applied across instances through register arrays.
3. HDMI enable and modeset paths program `DIG4` HDMI packet controls, ACR N/CTS, infoframes, generic packet scheduling, DB handshakes, TMDS symbols, backend mode/source selection, and AFMT audio clock state.
4. Audio setup paths program AFMT audio source selection, channel enable masks, audio layout overrides, IEC 60958 channel-status fields, audio infoframe fields, sample-send control, HBR/OSF override bits, and diagnostic CRC/ramp fields.
5. Dynamic metadata paths enable DME, select the HUBP requestor and stream type, coordinate metadata double-buffer state, and clear taken or missed-transmission statuses.
6. Generic packet paths write VPG indexed payload bytes, request immediate or frame-synchronous updates for generic packet slots 0-14, and watch pending/conflict status before reusing packet storage.
7. AUX initialization paths begin by using `DP_AUX0_AUX_CONTROL` fields for enable/reset/update/read behavior; complete AUX software transaction, arbitration, interrupt, and timing programming is in following lines outside this chunk.

The state described here is hardware register state:

- Persistent programmed state includes HDMI generic-packet scheduling policy, ACR timing values, TMDS control-symbol generation, DIG4 backend source/mode/HPD selection, AFMT channel/audio-info/channel-status programming, DME enable/requestor/stream selection, VPG packet payload bytes, MPEG/ISRC data bytes, and memory power policy bits.
- Volatile readback includes HDMI packet/error and DB pending/taken state, ACR status N/CTS readback, AFMT audio enable/HBR/FIFO overflow/audio-enable-change status, audio CRC done/result, DME DB pending/taken and missed-transmission status, VPG update-pending and conflict status, VPG/DME/AFMT memory power state, and AUX reset-done/read-control status.
- Side-effecting fields include HDMI/VUPDATE DB clear bits, HDMI generic send triggers, AFMT audio FIFO overflow and audio-enable-change acknowledgements, AFMT channel-status update, DME DB-taken clear, DME missed-transmission clear, VPG frame/immediate update triggers, VPG conflict clear, and AUX reset.

There is no disk persistence or driver-owned durable storage in this header. Values persist only in hardware registers until reset, power gating, suspend/resume, hotplug reconfiguration, a new modeset, or another driver path rewrites them.

## Dependencies And Integration Points

This chunk depends on generated-name consistency across the DCN 3.2.1 register header set. The register names and base-index symbols in `dcn_3_2_1_offset.h` must match these shift/mask names, and the Display Core mask-list macros must refer to fields that exist in this generated header.

Known integration points include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`, which includes `dcn/dcn_3_2_1_offset.h` and `dcn/dcn_3_2_1_sh_mask.h`, builds DCN321 shift/mask tables, and maps VPG/AFMT/DME register blocks to DIO stream encoder instances.
- `drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_stream_encoder.h`, whose `SE_COMMON_MASK_SH_LIST_DCN32` refers to HDMI generic packet fields, `DIG0_AFMT_CNTL`, and `DME0_DME_CONTROL` fields that correspond to the repeated generated definitions in this chunk.
- `drivers/gpu/drm/amd/display/dc/dcn31/dcn31_afmt.h`, which defines AFMT register lists and masks for audio packet control, audio source selection, IEC 60958 channel-status fields, and audio sample send behavior.
- `drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.h` and related VPG implementations, which define VPG register lists and fields for generic packet data, frame/immediate update controls, conflict handling, and memory power state.
- `drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_stream_encoder.c` and inherited stream encoder code paths, which program AFMT clocks/audio packets, HDMI ACR values, infoframes/generic packets, and DME metadata controls through the generated register tables.
- `drivers/gpu/drm/amd/display/dce/dce_aux.c` and DCN AUX resource initialization, which use the generated AUX shift/mask table for `DP_AUX0_AUX_CONTROL` and subsequent AUX registers.

The repeated hardware-instance pattern is the central integration constraint. The generated macros are instance-specific (`AFMT0` versus `AFMT4`, `DME0` versus `DME4`, `VPG0` versus `VPG4`, `DIG4` versus other DIGs), while Display Core tables often use instance-zero field names as field descriptors and separate register address tables for each instance. A mismatched instance prefix can compile if a table is wired incorrectly, but it can program the wrong encoder block at runtime.

## Risks And Maintenance Notes

- Numeric mask/shift drift is the primary risk. Incorrect values for HDMI generic packet sends, line references, DB handshakes, ACR N/CTS, TMDS control symbols, AFMT channel maps, DME clear bits, or VPG update requests can compile successfully and fail only on DCN 3.2.1 hardware.
- The chunk boundaries split registers. `DIG4_HDMI_STATUS` is only partially present at the beginning, and `DP_AUX0_AUX_CONTROL` is only partially present at the end. Per-file reconciliation must merge adjacent chunks before making complete-register claims.
- Side-effecting clear, ack, update, send, and reset fields are sensitive. A wrong mask can clear the wrong DME/VPG/AFMT/HDMI status, fail to clear a stale event, repeatedly send stale metadata, or leave an update pending.
- Generic packet slots 0-14 have repetitive fields spread across several HDMI and VPG registers. Off-by-one or copied-mask mistakes may affect only a specific packet slot, making failures mode-specific, such as HDR metadata, vendor packets, MPEG infoframes, or ISRC packets.
- AFMT audio programming is format-sensitive. Bad channel-status, sample frequency, channel map, HBR override, or audio layout masks can produce silent audio, wrong speaker mapping, bad AVR reporting, or failures only at particular sample rates and channel counts.
- DME and HDMI/VPG double-buffer fields need synchronization with vupdate or stream update locks. Incorrect pending/taken/clear behavior can cause metadata tearing, dropped HDR dynamic metadata, missed-transmission flags, or stale packet payloads.
- TMDS fields are HDMI/DVI output critical. Incorrect control-symbol, sync-pattern, DC-balance, or generated CTL bit masks can break link stability, deep-color modes, or compliance tests while leaving DisplayPort paths unaffected.
- Memory power fields in AFMT, DME, and VPG blocks can cause intermittent issues if programmed with wrong masks, especially after suspend/resume, display idle, power gating, or hotplug.
- `DP_AUX0_AUX_CONTROL` bits affect low-level AUX channel reset and enable behavior. Because this chunk ends mid-register, any analysis or edits involving AUX0 must include the next chunk for the full field set.

## Test Signals

Useful validation should combine generated-header checks with DCN321 display hardware coverage:

- Build AMDGPU Display Core with DCN 3.2.1 enabled and verify that `dcn321_resource.c`, DIO stream encoders, AFMT, VPG, DME, and AUX users resolve all generated fields from the header.
- Run generated-register consistency checks for this range: paired `_SHIFT`/`_MASK` macros where full registers are inside the chunk, 32-bit mask fit, expected non-overlap within each register, repeated `AFMT0-4`, `DME0-4`, and `VPG0-4` structural parity, and explicit allowance for the split `DIG4_HDMI_STATUS` and `DP_AUX0_AUX_CONTROL` boundary registers.
- Exercise HDMI through the `DIG4` stream encoder with audio enabled, deep color and scrambling where applicable, AVI/audio/MPEG infoframes, vendor/HDR generic packets, general-control packets, ACR sample-rate families at 32/44.1/48 kHz multiples, and TMDS compliance/test-pattern scenarios.
- Validate AFMT audio behavior across 2-channel and multichannel layouts, HBR modes, sample-rate changes, channel-status updates, audio source switching, FIFO overflow handling, and audio CRC/ramp diagnostic paths.
- Test DME dynamic metadata with HDR dynamic metadata enabled and disabled, HUBP requestor changes, stream type changes, DB pending/taken clear sequences, missed-transmission clear handling, and vupdate timing.
- Exercise VPG generic packet updates for slots 0-14 with both frame-synchronous and immediate updates. Watch update-pending, conflict, conflict-clear, payload index/data writes, and memory power state.
- Stress suspend/resume, display blank/unblank, hotplug, modeset, and idle power transitions while monitoring AFMT/DME/VPG memory power states, stale pending bits, packet conflicts, metadata missed flags, HDMI errors, and audio recovery.
- Validate AUX0 reset/enable behavior only together with the following chunk, because this range does not include the complete AUX0 control register or the software/arbitration/interrupt AUX registers.

## Chunk-Specific Summary

Lines 34937-37346 define DCN 3.2.1 bit shifts and masks for the tail of `DIG4` HDMI/status and packet generation, `DIG4` AFMT/backend/TMDS controls, repeated `AFMT0-4` audio-format blocks, repeated `DME0-4` dynamic metadata blocks, repeated `VPG0-4` packet-generator blocks, and the opening of `DP_AUX0_AUX_CONTROL`. The content is generated register ABI rather than executable driver logic. Correctness depends on exact numeric masks, careful instance mapping, safe handling of side-effecting update/clear/send/reset fields, and validation across HDMI audio/metadata, AFMT audio formatting, DME dynamic metadata, VPG packet updates, TMDS output, memory power transitions, and AUX initialization.
