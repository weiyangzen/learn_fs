# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 44675-47070

## Scope

This chunk is part of the generated AMDGPU DCN 3.2.0 register shift/mask header. It contains C preprocessor constants only; there are no executable functions, structs, enums, or runtime branches in the covered lines. The public interface is the generated bitfield macro contract:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

The covered lines start at the beginning of `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL14`, finish the tail of HPO DP symbol encoder instance 0, cover full HPO DP stream/APG/DME/VPG/SYM32 blocks for instances 1 and 2, then cover most of the instance 3 stream/APG/DME/VPG setup and the start of `DP_SYM32_ENC3` GSP controls. The chunk ends mid-register at `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL7__GSP_SOF_REFERENCE__SHIFT`; the corresponding pending/status/mask lines for that register continue after this chunk.

## Purpose

The chunk exposes bitfield layouts for the DCN 3.2 HPO DisplayPort transmit path. The repeated address blocks define how software configures and observes:

- `DP_STREAM_ENC1`, `DP_STREAM_ENC2`, and `DP_STREAM_ENC3` stream encoder clocking, pixel/audio input muxing, and clock-ramp FIFO status/control.
- `APG1`, `APG2`, and `APG3` audio packet generator reset, enable, stream ID, debug generation, packet source, audio CRC, FIFO status, and memory power controls.
- `DME7`, `DME8`, and `DME9` DisplayPort metadata engine routing, enable, double-buffer handshakes, transmission-missed status, and memory power controls.
- `VPG7`, `VPG8`, and `VPG9` video packet generator generic packet data windows, generic packet frame/immediate update triggers, pending status, conflict status/clear, memory power, ISRC packet bytes, and MPEG infoframe fields.
- `DP_SYM32_ENC1`, `DP_SYM32_ENC2`, and partial `DP_SYM32_ENC3` symbol encoder controls for enable/reset, pixel-to-symbol FIFO, MSA double buffering, pixel format, MSA payload data, hblank symbol width, generic secondary data packet transmission controls, audio SDP, metadata SDP, VBID, stream enable/status, panel replay tunneling, video CRC, memory power, and spare registers.
- The final `DP_SYM32_ENC0` tail fields for GSP slot 14 and post-GSP SDP/audio/video/CRC/memory controls.

These constants are hardware ABI for the DCN 3.2 display engine. Driver code combines them with matching register-offset headers and register helper macros to read or write memory-mapped display registers without hard-coding bit positions in the operational code.

## Important APIs, Types, and Definitions

There are no C APIs or types declared here. The important definitions are the register-field macro groups.

`DP_STREAM_ENC{1,2,3}_*` describes per-HPO-DP stream encoder control:

- `DP_STREAM_ENC_CLOCK_CONTROL` exposes clock enable and clock-on status bits for `DISPCLK`, `SOCCLK`, `DPSTREAMCLK`, and `SYMCLK32`.
- `DP_STREAM_ENC_INPUT_MUX_CONTROL` selects the pixel stream source.
- `DP_STREAM_ENC_AUDIO_CONTROL` selects the audio stream source.
- `DP_STREAM_ENC_CLOCK_RAMP_ADJUSTER_FIFO_STATUS_CONTROL0` controls FIFO enable/reset, read-start level, read clock source, reset-done, video-active, and FIFO error readback.
- `DP_STREAM_ENC_CLOCK_RAMP_ADJUSTER_FIFO_STATUS_CONTROL1` controls or reports overwrite level, recalibration/recompute triggers, minimum/maximum/calculated average FIFO level, and calibrated status.
- `DP_STREAM_ENC_SPARE` is a full-register spare field.

`APG{1,2,3}_*` describes audio packet generators for HPO DP:

- `APG_CONTROL` exposes reset and reset-done bits.
- `APG_CONTROL2` enables the APG, carries the DP audio stream ID, and exposes an ASP channel count override bit.
- `APG_DBG_GEN_CONTROL` exposes debug generator enable/reset, enabled test channels, and disabled test channels.
- `APG_PACKET_CONTROL` selects ACP and audio-info packet sources.
- `APG_AUDIO_CRC_CONTROL`, `APG_AUDIO_CRC_CONTROL2`, and `APG_AUDIO_CRC_RESULT` control audio CRC generation, channel selection, count/default count, done status, done clear, and result.
- `APG_STATUS` and `APG_STATUS2` expose audio enable, HBR enable, FIFO overflow status/clear, and sample flatline status.
- `APG_MEM_PWR` controls APG memory power force/disable/state/default low-power state.

`DME7`, `DME8`, and `DME9` describe metadata engines associated with the HPO stream path:

- `DME_CONTROL` carries `METADATA_HUBP_REQUESTOR_ID`, engine enable, stream type, double-buffer pending/taken/taken-clear bits, double-buffer disable, and transmission-missed status/clear.
- `DME_MEMORY_CONTROL` exposes memory power force, disable, state, and default low-power state.

`VPG7`, `VPG8`, and `VPG9` describe video packet generator programming:

- `VPG_GENERIC_PACKET_ACCESS_CTRL` selects a generic packet byte index.
- `VPG_GENERIC_PACKET_DATA` packs four generic packet bytes into one 32-bit register.
- `VPG_GSP_FRAME_UPDATE_CTRL` provides update trigger bits and pending bits for generic packets 0 through 14.
- `VPG_GSP_IMMEDIATE_UPDATE_CTRL` provides immediate-update trigger bits and pending bits for the same generic packet slots.
- `VPG_GENERIC_STATUS` exposes lock status, conflict occurrence, and conflict clear.
- `VPG_MEM_PWR` controls GSP memory light-sleep disable, light-sleep force, and power-state readback.
- `VPG_ISRC1_2_ACCESS_CTRL` and `VPG_ISRC1_2_DATA` expose indexed ISRC1/2 packet byte programming.
- `VPG_MPEG_INFO0` and `VPG_MPEG_INFO1` expose MPEG infoframe checksum, metadata bytes, mode/frame fields, and update trigger.

`DP_SYM32_ENC{1,2}_*` and the covered `DP_SYM32_ENC3_*` prefix describe the 32-symbol DisplayPort encoder:

- `DP_SYM32_ENC_CONTROL` exposes enable, reset, and reset-done.
- `DP_SYM32_ENC_VID_FIFO_CONTROL` exposes pixel-to-symbol FIFO enable/reset/reset-done and FIFO read-start level.
- `DP_SYM32_ENC_VID_MSA_DOUBLE_BUFFER_CONTROL` and `DP_SYM32_ENC_VID_PIXEL_FORMAT_DOUBLE_BUFFER_CONTROL` enable double buffering for MSA and pixel-format programming.
- `DP_SYM32_ENC_VID_PIXEL_FORMAT` encodes pixel encoding type, uncompressed pixel encoding, and component depth.
- `DP_SYM32_ENC_VID_MSA0` through `DP_SYM32_ENC_VID_MSA8` are full-register MSA data words.
- `DP_SYM32_ENC_HBLANK_CONTROL` defines the minimum hblank symbol width.
- `DP_SYM32_ENC_SDP_GSP_CONTROL0` through `CONTROL14` each carry generic SDP/GSP controls: video continuous transmission, idle continuous transmission, one-shot trigger, one-shot position, double buffer enable, payload size, SOF reference, missed-deadline status, pending status, double-buffer pending, and transmission line number.
- `DP_SYM32_ENC_SDP_CONTROL` exposes SDP stream enable, GSP0 priority, and SDP CRC16 enable.
- `DP_SYM32_ENC_SDP_AUDIO_CONTROL0` exposes ASP/ATP/AIP/ACM/ISRC enables, ASP priority, ATP version, audio mute, and mute status.
- `DP_SYM32_ENC_SDP_AUDIO_CONTROL1` controls ASP concatenation and max sample counts for 2-channel, 8-channel, and HBR layouts.
- `DP_SYM32_ENC_SDP_METADATA_PACKET_CONTROL` controls metadata packet enable, double buffering, SOF reference, double-buffer pending, and transmission line.
- `DP_SYM32_ENC_VID_MSA_CONTROL` and `DP_SYM32_ENC_VID_VBID_CONTROL` schedule MSA and VBID fields relative to SOF/line positions.
- `DP_SYM32_ENC_VID_STREAM_CONTROL` exposes stream enable, deferred disable, and stream status.
- `DP_SYM32_ENC_VID_PANEL_REPLAY_CONTROL` exposes panel replay tunneling optimization enable and double-buffer enable.
- `DP_SYM32_ENC_VID_CRC_CONTROL`, `VID_CRC_RESULT0`, `VID_CRC_RESULT1`, and `VID_CRC_STATUS` control video CRC, continuous mode, result readback lanes, and valid status.
- `DP_SYM32_ENC_MEM_POWER_CONTROL` exposes default low-power state, memory power force, disable, and state.

## Control Flow

This header has no control flow. Runtime flow is supplied by AMD display code that includes the header and uses the generated constants through register-helper tables:

1. Per-generation resource code selects a HPO DP stream encoder, APG, VPG, and DME instance from the display engine/resource mapping.
2. Register-list macros provide offsets from `dcn_3_2_0_offset.h` for the selected block.
3. Mask/shift-list macros use generated `SE_SF(...)`, `SF(...)`, `FD_MASK(...)`, or `FD_SHIFT(...)` style helpers to copy these constants into `*_shift` and `*_mask` structs.
4. Operational code calls `REG_UPDATE`, `REG_GET`, `REG_WAIT`, or related helpers on logical register/field names.
5. The helper shifts/masks the value using this header's constants and performs a memory-mapped register read or write.
6. Hardware accepts the write immediately, defers it through a double-buffer/update boundary, or reports status through pending/done/clear/status fields depending on the register.

The chunk supports several hardware sequencing protocols:

- Reset/enable handshakes for APG, stream encoder, symbol encoder, and FIFOs use `*_RESET`, `*_RESET_DONE`, `*_ENABLE`, and status fields.
- Packet programming writes indexed packet data into VPG or SDP/GSP registers, then triggers frame or immediate update bits and observes pending/status bits.
- Metadata engine programming selects a HUBP requestor and stream type, enables the engine, then relies on double-buffer pending/taken and missed-transmission status bits.
- Audio programming enables APG/ASP/ATP/AIP/ACM/ISRC paths, assigns the stream ID, optionally uses debug generation, and can validate output through audio CRC and FIFO-overflow fields.
- Video stream programming configures pixel format, MSA payloads, VBID, hblank width, stream enable/deferred disable, and optional CRC readback.
- Memory-power fields persistently request low-power or forced states and expose hardware power-state readback.

## State and Persistence

The macros are compile-time constants and store no state. Persistent state lives in the display hardware registers after memory-mapped writes. Important persistent and observable state represented by this chunk includes:

- HPO stream encoder clock and FIFO setup for instances 1 through 3.
- APG enable/reset state, selected audio stream IDs, packet source selection, debug audio generation settings, audio CRC state/results, FIFO overflow indicators, flatline status, and APG memory power state.
- DME metadata engine enable/routing, metadata stream type, double-buffer pending/taken status, disable state, missed-transmission status, and DME memory power state.
- VPG generic packet contents, ISRC packet contents, MPEG infoframe contents, update/immediate trigger requests, pending status, conflict status/clear, lock status, and GSP memory power state.
- Symbol encoder enable/reset, pixel-to-symbol FIFO state, pixel format, MSA data words, hblank width, generic SDP/GSP transmission mode, metadata packet scheduling, audio SDP state, VBID scheduling, stream enable/status, panel replay optimization, video CRC results, and memory power state.

Fields named `*_PENDING`, `*_STATUS`, `*_DONE`, `*_RESET_DONE`, `*_TAKEN`, `*_MISSED`, `*_VALID`, `*_STATE`, `*_ACTIVE`, `*_ERROR`, and `*_CLEAR` should be treated as hardware handshake/readback/clear fields rather than ordinary storage. The header does not encode whether a field is read-only, write-one-to-clear, self-clearing, latched, or update-boundary synchronized; that behavior must come from the caller and the hardware specification.

## Dependencies and Integration Points

This header depends on the generated AMD ASIC register contract:

- `dcn_3_2_0_offset.h` supplies the register offsets with matching register names.
- `dcn_3_2_0_sh_mask.h` supplies the field shifts and masks covered here.
- `dmub/src/dmub_dcn32.c` includes both headers and initializes DMUB register offset/mask/shift storage with `FD_MASK` and `FD_SHIFT`.
- HPO DP stream encoder code in `display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h` shows the consumer pattern for these names: instance register lists include `DP_STREAM_ENC_*` and `DP_SYM32_ENC_*`, while mask/shift lists use fields such as `DP_STREAM_ENC_CLOCK_EN`, `FIFO_RESET`, `DP_SYM32_ENC_ENABLE`, `PIXEL_ENCODING_TYPE`, `VID_STREAM_ENABLE`, `SDP_STREAM_ENABLE`, GSP controls, metadata packet enable, audio mute/enables, CRC controls, and hblank width.
- VPG code in `display/dc/dcn31/dcn31_vpg.h` maps generic packet, update, status, and memory-power fields into `struct dcn31_vpg_shift` and `struct dcn31_vpg_mask`.
- APG code in `display/dc/dcn31/dcn31_apg.h` maps reset, enable, audio stream ID, debug channel enable, and memory-power fields into APG shift/mask tables.
- Resource code for nearby DCN 3.x paths documents the HPO mapping: VPG register blocks 6 through 9 map to HPO DP 0 through 3, and APG register blocks 0 through 3 map to HPO DP 0 through 3. In this chunk, `VPG7`, `VPG8`, and `VPG9` therefore correspond to HPO DP instances 1, 2, and 3; `APG1`, `APG2`, and `APG3` correspond to the same HPO DP instances.
- DME register blocks `DME7`, `DME8`, and `DME9` align with the same HPO stream encoder instance group and provide metadata-engine support for DP metadata packets.

The repeated instance prefixes are significant. Code generally uses instance-relative register tables, but the generated mask/shift tables are built from a representative instance prefix such as `DP_SYM32_ENC0_*`, `VPG0_*`, or `APG0_*`. These definitions must remain layout-compatible across instances for that reuse pattern to work.

## Risks and Edge Cases

- Generated-header drift is the main risk. A single incorrect shift or mask can silently write the wrong hardware bits, causing failed HPO DP bring-up, missing audio, packet transmission errors, CRC failures, stuck pending bits, or display corruption.
- The chunk boundaries are not semantic boundaries. It starts after previous `DP_SYM32_ENC0` GSP controls and ends inside `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL7`. Whole-register analysis for boundary registers must merge neighboring chunks.
- Many fields are one-bit triggers or clear bits next to status bits. Treating `*_CLR`, `*_CLEAR`, `*_RESET`, `*_FRAME_UPDATE`, or `*_IMMEDIATE_UPDATE` as persistent configuration can retrigger hardware actions or fail to clear latched events correctly.
- Double-buffered and pending fields require update-boundary awareness. GSP controls, metadata controls, MSA/pixel-format double buffering, and DME double-buffer bits may not take effect at the moment software writes them.
- FIFO and stream status fields are timing sensitive. Polling `FIFO_RESET_DONE`, `FIFO_VIDEO_STREAM_ACTIVE`, `VID_STREAM_STATUS`, `APG_AUDIO_FIFO_OVERFLOW_STATUS`, or `VPG_GENERIC_LOCK_STATUS` without appropriate timeouts can hang control paths.
- Several data registers pack byte lanes or small fields into one 32-bit register. Out-of-range caller values for packet data indexes, payload size, stream IDs, sample counts, line numbers, or FIFO levels will be truncated by masks unless the caller validates them before writes.
- Memory power controls can race programming sequences. Powering down APG, DME, VPG, or SYM32 memories while packet/LUT-like indexed writes or packet updates are in flight can produce stale data, missed packets, or invalid readback.
- Instance mapping must be kept aligned. VPG indices in this chunk are 7 through 9 while APG and stream encoder indices are 1 through 3; confusing physical block numbers with HPO DP logical instance numbers can route packets or audio to the wrong stream.
- Some fields are present in the generated header but not necessarily used by the current operational tables. Removing apparently unused definitions can still break future table expansion, firmware register initialization, or out-of-tree diagnostics.

## Test Signals

This chunk has no directly unit-testable function behavior. Useful validation signals are structural and integration-oriented:

- Build AMDGPU display and DMUB code for DCN 3.2 with this header included; undefined macro errors catch missing or renamed generated fields.
- Compare the generated `__SHIFT` and `_MASK` pairs against the authoritative DCN 3.2 ASIC register database.
- Mechanically validate mask/shift consistency: each field should have both shift and mask definitions, masks should align with shifts, byte-lane fields should not overlap, and full-register data/spare fields should use `0xFFFFFFFFL`.
- Exercise HPO DP link bring-up on ports using HPO DP instances 1 through 3 and confirm stream encoder clock, FIFO reset, symbol encoder reset, and stream-enable status transitions complete.
- Exercise DP audio through APG1/APG2/APG3, including mute/unmute, stream ID assignment, HBR status, FIFO overflow status/clear, and audio CRC result paths.
- Exercise VPG generic packet, ISRC, MPEG infoframe, and SDP metadata updates, then check frame/immediate pending bits drain and conflict status remains clear.
- Exercise DME metadata paths by enabling metadata transmission and checking double-buffer pending/taken and missed-transmission status/clear behavior.
- Exercise video CRC controls on HPO streams and verify `CRC_VALID` plus result fields behave consistently across stable frames.
- Exercise low-power transitions for APG, DME, VPG, stream encoder, and symbol encoder memories; status fields should match requested force/disable/default-low-power settings and active streams should recover.
