# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 47146-49525

## Scope

This chunk is a generated AMD DCN 3.1.5 register-field shift/mask slice. It contains C preprocessor constants only: `_SHIFT` macros for field low-bit positions, `_MASK` macros for raw register bit masks, register-name comments, and address-block comments. There are no functions, structs, enums, branches, loops, allocations, locks, or driver-owned state containers in this range.

The slice starts at the `APG0` audio packet generator status/memory-power tail, then defines the HPO DisplayPort stream encoder instance 0 metadata engine (`DME6`), video packet generator (`VPG6`), and full `DP_SYM32_ENC0` field layout. It continues through full HPO stream encoder instance 1 coverage (`DP_STREAM_ENC1`, `APG1`, `DME7`, `VPG7`, `DP_SYM32_ENC1`) and then begins instance 2 (`DP_STREAM_ENC2`, `APG2`, `DME8`, `VPG8`, and the opening `DP_SYM32_ENC2` fields). The chunk ends inside `DP_SYM32_ENC2_DP_SYM32_ENC_SDP_AUDIO_CONTROL1`; the remainder of instance 2 is in the next chunk.

## Purpose And Hardware Surface

The purpose of this header range is to publish the bit-layout ABI between AMDGPU Display Core code and DCN 3.1.5 HPO DisplayPort hardware. The matching `dcn_3_1_5_offset.h` header supplies register addresses and base indices; this file supplies the field masks and shifts used by register helper macros to pack writes and decode readbacks.

Major hardware areas represented here:

- `APG0`, `APG1`, and `APG2` audio packet generator fields for audio enable/HBR status, FIFO overflow status and clear, output-active status, memory power control, packet/debug/audio CRC control, and spare registers.
- `DME6`, `DME7`, and `DME8` metadata engines for HPO stream encoders. They expose metadata HUBP requestor IDs, engine enable, stream type, double-buffer pending/taken status, clear/disable bits, missed-transmission status/clear bits, and DME memory power controls.
- `VPG6`, `VPG7`, and `VPG8` video packet generators. They define generic packet data-index/data-byte windows, frame-update and immediate-update controls for generic slots 0-14, lock/conflict status, memory power fields, ISRC data windows, and MPEG infoframe words.
- `DP_STREAM_ENC1` and `DP_STREAM_ENC2` stream encoder front-end fields for clock gate/enable controls, stream source muxing, audio stream selection, clock ramp adjuster FIFO status, and spare fields.
- `DP_SYM32_ENC0`, `DP_SYM32_ENC1`, and the beginning of `DP_SYM32_ENC2` symbol encoders for HPO DP video, secondary data packets, audio packets, metadata packets, CRC, and memory power.

This is hardware-definition data rather than active logic. Its correctness matters because the display stack treats these constants as the source of truth for MMIO field packing on DCN 3.1.5.

## Important Definitions

The exported API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted bit mask within the 32-bit register.
- `//<REGISTER>` comments group macros by hardware register.
- `// addressBlock: ...` comments identify the hardware aperture for the following register group.

Important field families in this chunk:

- `APG*_APG_STATUS`, `APG*_APG_STATUS2`, `APG*_APG_MEM_PWR`, and `APG*_APG_SPARE` expose audio packet generator status and power-management fields. Instance 0 begins in the previous chunk, while instances 1 and 2 include their control, debug, packet, CRC, status, power, and spare groups here.
- `APG*_APG_CONTROL` and `APG*_APG_CONTROL2` define reset/reset-done, APG enable, DP audio stream ID, channel-count override, HBR audio stream ID, and layout override fields for instances 1 and 2.
- `APG*_APG_DBG_GEN_CONTROL`, `APG*_APG_PACKET_CONTROL`, `APG*_APG_AUDIO_CRC_CONTROL`, `APG*_APG_AUDIO_CRC_CONTROL2`, and `APG*_APG_AUDIO_CRC_RESULT` define debug audio generation, audio info source selection, CRC enable/continuous/channel/count programming, CRC done/clear, and 16-bit CRC result fields.
- `DME*_DME_CONTROL` packs metadata routing and state fields: `METADATA_HUBP_REQUESTOR_ID`, `METADATA_ENGINE_EN`, `METADATA_STREAM_TYPE`, `METADATA_DB_PENDING`, `METADATA_DB_TAKEN`, `METADATA_DB_TAKEN_CLR`, `METADATA_DB_DISABLE`, `METADATA_TRANSMISSION_MISSED`, and `METADATA_TRANSMISSION_MISSED_CLR`.
- `DME*_DME_MEMORY_CONTROL` exposes DME memory power force, disable, state, and default low-power-state fields.
- `VPG*_VPG_GENERIC_PACKET_ACCESS_CTRL` and `VPG*_VPG_GENERIC_PACKET_DATA` define the indexed generic packet payload window with 8-bit index and four 8-bit data-byte fields.
- `VPG*_VPG_GSP_FRAME_UPDATE_CTRL` and `VPG*_VPG_GSP_IMMEDIATE_UPDATE_CTRL` define generic packet slot update triggers for slots 0-14 and corresponding pending bits at bits 16-30.
- `VPG*_VPG_GENERIC_STATUS` exposes generic packet lock status, conflict status, and conflict clear fields. `VPG*_VPG_MEM_PWR` exposes VPG GSP memory light-sleep disable, force, and state fields.
- `VPG*_VPG_ISRC1_2_ACCESS_CTRL`, `VPG*_VPG_ISRC1_2_DATA`, `VPG*_VPG_MPEG_INFO0`, and `VPG*_VPG_MPEG_INFO1` provide ISRC and MPEG packet data windows, checksum and payload-byte fields, update flags, and frame-rate/mode metadata.
- `DP_SYM32_ENC*_DP_SYM32_ENC_CONTROL` defines enable, reset, and reset-done bits for symbol encoder instances.
- `DP_SYM32_ENC*_DP_SYM32_ENC_VID_FIFO_CONTROL` defines pixel-to-symbol FIFO enable/reset/reset-done and overflow status bits.
- `DP_SYM32_ENC*_DP_SYM32_ENC_VID_PIXEL_FORMAT` and its double-buffer control define pixel encoding type, uncompressed encoding, component depth, double-buffer enable, and pending status.
- `DP_SYM32_ENC*_DP_SYM32_ENC_VID_MSA0` through `VID_MSA8` expose full 32-bit MSA data words. `VID_MSA_CONTROL` and `VID_MSA_DOUBLE_BUFFER_CONTROL` add line-number/SOF control and double-buffer enable/pending fields.
- `DP_SYM32_ENC*_DP_SYM32_ENC_HBLANK_CONTROL` defines the minimum hblank symbol width.
- `DP_SYM32_ENC*_DP_SYM32_ENC_SDP_GSP_CONTROL0` through `CONTROL14` repeat a common layout for 15 generic secondary data packet slots: video-continuous enable, idle-continuous enable, one-shot trigger, one-shot position, double-buffer enable, payload size, SOF reference, deadline missed, transmission pending, double-buffer pending, and 16-bit transmission line number.
- `DP_SYM32_ENC*_DP_SYM32_ENC_SDP_CONTROL` exposes SDP stream enable, GSP0 priority, and CRC16 enable fields.
- `DP_SYM32_ENC*_DP_SYM32_ENC_SDP_AUDIO_CONTROL0` exposes ASP/ATP/AIP/ACM/ISRC enables, ASP priority, ATP version number, audio mute, and audio mute status. `SDP_AUDIO_CONTROL1` adds ASP concatenation enable and max sample-count fields for 2-channel, 8-channel, and HBR layouts.
- For instances fully covered in this chunk, later `DP_SYM32_ENC*` fields define metadata packet control, MSA/VBID line controls, stream enable/status/deferred-disable, panel replay tunneling optimization, video CRC enable/results/status, memory power control, and spare fields. For instance 2, those later groups continue in the next chunk.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when AMDGPU Display Core and DMUB code combine these constants with matching `reg*` offsets and register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, generated `SE_SF` field tables, or `DMUB_SF` field tables.

A typical use path is:

1. Select a DCN 3.1.5 register address and base index from `dcn_3_1_5_offset.h`.
2. Select the matching field mask and shift from this header.
3. Pack a value, decode a readback, or build a read/modify/write operation through the display register abstraction.
4. Let hardware latch, report, clear, or consume the field.

The state represented here is hardware state:

- Persistent configuration fields include APG enable/audio stream selection/debug generation, DME metadata routing and memory-power controls, VPG packet data and update controls, stream encoder source muxing, DP symbol encoder enable, video pixel format, MSA contents, VBID control, SDP/GSP transmission mode, audio packet enables, metadata packet control, panel replay optimization, CRC mode, and memory power policy.
- Volatile readback fields include reset-done, APG output-active, FIFO overflow, CRC done/result, DME double-buffer pending/taken and missed-transmission status, VPG update-pending/lock/conflict status, stream enable/status, audio mute status, CRC valid/result words, and memory-power state readbacks.
- Side-effecting write fields include reset bits, clear bits such as APG FIFO overflow clear, APG CRC done clear, DME double-buffer taken clear, DME missed-transmission clear, VPG conflict clear, generic packet update triggers, immediate-update triggers, one-shot GSP sends, and CRC enable/continuous mode controls.
- Double-buffered state appears repeatedly in DME metadata, VPG generic packet update controls, MSA and pixel-format controls, GSP packet controls, and metadata packet controls. Callers must respect frame/SOF timing and pending-bit semantics; those sequencing rules are not encoded in the macros.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.1.5 register-address definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`.

Known integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`, which includes `dcn_3_1_5_offset.h` and this header to build DMUB register offset/mask/shift tables through `DMUB_DCN315_FIELDS()`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`, which includes the DCN315 generated offset and mask headers for interrupt service register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h` and `.c`, whose HPO DP stream encoder register and mask/shift lists use `DP_SYM32_ENC0_*` field names for generic register-field table construction. Those tables are later instanced by resource code for concrete HPO stream encoder instances.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.h` and `.c`, which define APG register lists and mask/shift lists such as `APG0_APG_CONTROL`, `APG0_APG_CONTROL2`, `APG0_APG_DBG_GEN_CONTROL`, and `APG0_APG_MEM_PWR`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.h` and `.c`, plus resource-list macros such as `VPG_DCN3_REG_LIST_RI`, which map VPG generic packet and update-control fields into per-instance VPG objects.
- DCN31/DCN314/DCN316/DCN32/DCN35/DCN36/DCN321/DCN401 resource code patterns that allocate HPO stream encoders and map VPG, APG, DME, and DP_SYM32 register blocks to HPO DP instances. The common mapping pattern is VPG6/APG0/DME6/SYM32_ENC0 for HPO DP instance 0, VPG7/APG1/DME7/SYM32_ENC1 for instance 1, and VPG8/APG2/DME8/SYM32_ENC2 for instance 2.
- Display audio, generic SDP/infoframe, DP metadata, panel replay, CRC diagnostics, and HPO stream programming paths that indirectly consume these fields through the above register tables.

Because the header is generated, most use is indirect. A missing or misspelled macro usually fails compilation through `SE_SF`, `SRI`, `SRI_ARR`, `REG_FIELD`, or `DMUB_SF` expansion. A wrong numeric mask or shift can compile cleanly and cause runtime MMIO misprogramming.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.1.5 register database is the main risk. Incorrect masks or shifts can corrupt HPO DP stream setup, packet scheduling, metadata routing, audio packet generation, CRC diagnostics, or memory-power programming.
- This chunk starts in the middle of the APG0 register family and ends in the middle of the DP_SYM32_ENC2 audio-control family. The merge lane must combine adjacent chunks before making complete statements about APG0 or DP_SYM32_ENC2.
- The instance numbering is easy to confuse: APG instances use 0/1/2 while DME and VPG instances use 6/7/8 for the same HPO stream encoder slots. A valid macro for the wrong instance can compile and target the wrong hardware block.
- GSP controls are highly repetitive across slots 0-14 and across DP_SYM32 instances. Copy/paste mistakes among GSP slot numbers, pending bits, line-number fields, and payload-size fields are difficult to catch by type checking.
- Clear bits share registers with status bits. APG FIFO overflow clears, APG CRC done clears, DME status clears, and VPG conflict clears must be treated as write-side effects rather than normal persistent configuration.
- Double-buffer and SOF/line-number controls are timing-sensitive. Incorrect update ordering can leave pending bits set, miss a desired frame boundary, or transmit stale metadata/infoframes.
- Audio packet fields combine ASP/ATP/AIP/ACM/ISRC enables, mute state, HBR stream IDs, version fields, and concatenation sample-count limits. Wrong bit packing may produce silent audio failures or malformed display-audio packets.
- CRC and diagnostic fields can be mistaken for production data-path controls. CRC enable/continuous mode and result clear/status fields should be isolated to validation and debug flows.
- Memory power controls for APG, DME, VPG, and DP_SYM32 blocks expose force/disable/state fields. Writes must be coordinated with stream enable/disable sequencing so register accesses do not race a powered-down block.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Compile coverage for AMDGPU Display Core with DCN 3.1.5 enabled. This catches missing macro names, malformed generated constants, and broken macro syntax.
- Static comparison against the authoritative DCN 3.1.5 register database or a regenerated `dcn_3_1_5_sh_mask.h`, especially for instance numbering, repeated GSP slot fields, audio packet fields, and clear/status masks.
- Cross-revision spot checks against nearby generated headers such as DCN 3.1.4, 3.1.6, 3.2.0, and 3.5.1 where HPO DP register layout is expected to remain compatible, while preserving intentional DCN315 differences.
- HPO DP functional testing on DCN 3.1.5 hardware: stream enable/disable, pixel format changes, MSA programming, VBID/compressed-stream signaling, panel replay tunneling optimization, and link stability at expected modes.
- Generic SDP/infoframe testing: VPG packet payload writes through index/data windows, frame-update and immediate-update triggers, GSP packet scheduling by line/SOF, metadata packet double-buffering, and pending bits clearing after frame boundaries.
- Display audio testing: APG enable/disable, stream ID selection, HBR paths, audio mute/unmute, ASP/ATP/AIP/ACM/ISRC packet transmission, and audio CRC done/result behavior.
- Metadata engine testing for DME6/DME7/DME8: HUBP requestor routing, metadata enable/disable, double-buffer taken/pending behavior, missed-transmission detection, and clear-bit behavior.
- Runtime register dumps around HPO stream setup, packet updates, audio changes, CRC reads, and power transitions. Packed values should affect only the intended masked bits and preserve unrelated fields.

## Open Questions For Merge

- The exact DCN315 resource constructor mapping for HPO stream encoder instances is outside this generated header and should be reconciled with resource chunks before final per-file claims.
- Later chunks complete `DP_SYM32_ENC2` and likely continue additional HPO stream/link/audio definitions. The final per-file document should avoid treating this chunk as complete coverage of all HPO DP instance 2 fields.
