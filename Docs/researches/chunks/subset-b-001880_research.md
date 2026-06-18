# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 37423-39826

## Purpose

This chunk is a generated DCN 3.1.5 ASIC register field header segment for AMD display hardware. It provides C preprocessor constants for register bit shifts and masks, not executable logic. The constants are consumed with the companion `dcn_3_1_5_offset.h` register-offset header by AMDGPU display code to build typed register tables and to drive `REG_GET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT` helper paths.

The range contains 2,166 macro definitions across 197 visible register names: 1,082 `__SHIFT` constants and 1,084 `_MASK` constants. It starts inside the `DP4_DP_SEC_METADATA_TRANSMISSION` register definition, after some field shifts were emitted in the previous chunk, and ends after the first `VPG3_VPG_MPEG_INFO0__VPG_MPEG_INFO_CHECKSUM__SHIFT` definition, before the rest of that register appears in the next chunk.

## Covered Hardware Blocks

- `DP4` tail fields: DisplayPort secondary-data metadata transmission, DSC bytes-per-pixel, ALPM PHY sleep/standby control, generic secondary packet controls for GSP8-GSP11, and generic packet enable double-buffer status.
- `DIG4` display encoder/front-end block: source selection, stereosync, start control, bypass, input pixel selection, Dolby Vision status, TMDS encoding/color, output CRC, test/random patterns, FIFO status, HDMI metadata/audio/VBI/infoframe/generic-packet/ACR/general-control registers, HDMI double-buffer controls, AFMT selection, backend enable/control, TMDS control characters, DC-balance, sync characters, generated control bits, version, and force-disable.
- `AFMT0` through `AFMT4`: repeated audio formatter field maps for VBI/audio packet controls, audio infoframes, IEC 60958 channel-status words, audio CRC controls/results, test ramps, status, audio source select, and memory power control.
- `DME0` through `DME3`: metadata engine controls and memory power controls for DIO instances 0-3.
- `VPG0` through `VPG3`: visual/generic packet generator packet data indexing, byte data, frame-update and immediate-update controls for generic packets 0-14, conflict/status bits, memory power controls, ISRC packet byte access, and MPEG infoframe fields. `VPG3_MPEG_INFO0` is incomplete in this chunk because of the line boundary.

## Important APIs, Types, and Macros

The header itself exposes macros only. The naming scheme is:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register value space.

Important consumers visible in this tree include:

- `display/dmub/src/dmub_dcn315.c`, where `dcn_3_1_5_sh_mask.h` is included and `FD_MASK(reg, field)` / `FD_SHIFT(reg, field)` populate `dmub_srv_dcn315_regs`.
- `display/dc/resource/dcn315/dcn315_resource.c`, where `SRI`, `SRII`, `SE_SF`, and related macros combine offsets from `dcn_3_1_5_offset.h` with masks/shifts from this file to instantiate DCN 3.1.5 hardware objects.
- `display/dc/dcn31/dcn31_vpg.h` and `display/dc/dcn31/dcn31_afmt.h`, whose `DCN31_VPG_MASK_SH_LIST` and `DCN31_AFMT_MASK_SH_LIST` macros reference representative instance-0 field names such as `VPG0_VPG_*` and `AFMT0_AFMT_*`; `dcn315_resource.c` uses the generated register and field tables for all DIO instances.
- `display/dc/dcn31/dcn31_vpg.c` and `display/dc/dcn31/dcn31_afmt.c`, where fields from this chunk such as `VPG_MEM_PWR`, `VPG_GSP_MEM_LIGHT_SLEEP_DIS`, `VPG_GSP_LIGHT_SLEEP_FORCE`, `VPG_GSP_MEM_PWR_STATE`, `AFMT_MEM_PWR_DIS`, `AFMT_MEM_PWR_FORCE`, and `AFMT_MEM_PWR_STATE` are used by register helper calls.

There are no functions, structs, enums, storage objects, syscalls, or direct control-flow statements in this chunk.

## Control Flow and State

Runtime control flow is indirect. Build-time macro expansion copies these constants into register descriptor structures. Later, display code calls register helper macros that use those descriptors to read, mask, shift, update, poll, or clear hardware registers.

The visible state is hardware state:

- Double-buffer lifecycle bits: `*_DB_PENDING`, `*_DB_TAKEN`, `*_DB_TAKEN_CLR`, `*_DB_LOCK`, `*_DB_DISABLE`, `*_VUPDATE_DB_PENDING`, and `*_VUPDATE_DB_TAKEN*` in DP, HDMI, DME, and generic-packet paths. These fields synchronize software writes with vblank/vupdate or packet-generator update points.
- Packet send state: `SEND`, `CONT`, `IMMEDIATE_SEND`, `SEND_PENDING`, `SEND_ACTIVE`, `SEND_DEADLINE_MISSED`, `LINE_REFERENCE`, and line-number fields for HDMI generic packets and DP GSP packets.
- Error and clear/ack state: HDMI error/status bits, metadata packet missed bits, DME metadata transmission missed/clear fields, VPG generic conflict/clear fields, audio FIFO overflow/ack, and audio-enable change ack.
- Power state: `AFMT_MEM_PWR_*`, `DME_MEM_PWR_*`, and `VPG_GSP_MEM_*` fields expose block-local memory power force/disable/state/default-low-power controls.
- Indexed payload state: VPG generic, ISRC, and MPEG infoframe data fields expose byte-wide packet payload storage behind an access index. Payload contents persist in hardware packet RAM/register state until overwritten or reset by display hardware sequencing.

## Dependencies and Integration Points

This file depends on exact DCN 3.1.5 hardware register layout. It must stay aligned with:

- `dcn_3_1_5_offset.h` for register addresses and base-index selection.
- DCN 3.1/3.0 display object headers such as `dcn31_vpg.h`, `dcn31_afmt.h`, `dcn30_dio_stream_encoder.h`, and stream encoder/resource constructors that expect particular field names.
- Register helper macros in `reg_helper.h` and DMUB register helpers that interpret these masks and shifts.
- DRM/AMDGPU display bring-up, hotplug/IRQ, audio, HDMI/DP stream encoder, DMUB service, and resource-pool construction code that includes the DCN 3.1.5 generated headers.

The repeated instance prefixes are significant. `AFMT0`-`AFMT4`, `DME0`-`DME3`, and `VPG0`-`VPG3` are separate hardware instances. Resource code maps VPG/AFMT/DME blocks to DIO stream encoders, and later comments in `dcn315_resource.c` also map higher VPG instances to HPO DP stream encoders outside this chunk.

## Risks and Edge Cases

- A wrong mask or shift silently writes the wrong hardware bits. Failure modes include blank output, broken HDMI/DP metadata, missing HDR/Dolby Vision metadata, audio channel/status corruption, packet deadline misses, FIFO overflow, or display power-management regressions.
- The chunk boundaries split complete register definitions. `DP4_DP_SEC_METADATA_TRANSMISSION` begins in a previous chunk, and `VPG3_VPG_MPEG_INFO0` continues in a later chunk; the merge lane must combine adjacent research to avoid treating those registers as incomplete in the final per-file report.
- Repeated instance blocks are easy to mix up. Instance-0 field names are often used to define common masks/shifts for object classes, while offsets select the concrete instance. Manual edits that copy `AFMT0` fields into `AFMT4` or vice versa could compile but program the wrong table.
- Clear/ack fields such as `*_CLR`, `*_ACK`, and conflict clear bits may have write-one-to-clear semantics in hardware. Generic read-modify-write code must avoid unintentionally asserting them.
- Pending/status fields are hardware-synchronized. Poll loops or update paths need timeouts and must account for vblank/vupdate timing, disabled streams, and power-gated memories.
- Some fields represent line numbers or packet slots with limited masks. Out-of-range line placement or packet index values can be truncated by the mask and may only show up as missed/deadline status bits.

## Test and Validation Signals

- Kernel build coverage for DCN 3.1.5 display code verifies that every referenced field macro still exists and has the expected naming shape.
- Register-table initialization in `dcn315_resource.c` and `dmub_dcn315.c` should compile without missing `FD_MASK`, `FD_SHIFT`, `SE_SF`, or `SRI` expansions.
- Display smoke tests should cover HDMI and DP link bring-up, mode sets, vblank/vupdate behavior, suspend/resume, and stream disable/enable cycles.
- Feature tests should cover HDMI audio, audio channel layouts, IEC 60958 channel-status updates, audio CRC/test paths, infoframes, generic packets, HDR/Dolby Vision metadata, DP secondary-data packets, DSC bytes-per-pixel programming, and ALPM PHY sleep/standby transitions.
- Useful runtime diagnostics include HDMI/DP packet missed/deadline bits, audio FIFO overflow/status bits, VPG generic conflict status, DME metadata transmission missed status, double-buffer pending/taken fields, and VPG/AFMT/DME memory power state reads.
