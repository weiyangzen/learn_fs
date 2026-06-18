# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 41782-44191

## Purpose

This chunk is generated AMD DCN 3.1.4 display register field metadata. It contains preprocessor constants for bit positions (`__SHIFT`) and field masks (`_MASK`) inside memory-mapped display-controller registers. The matching `dcn_3_1_4_offset.h` header supplies register addresses; this header supplies the bit layout that AMD display register helpers use to update individual fields.

The requested range is a middle slice of the DIO display output area. It starts inside the DIG2 HDMI generic-packet field definitions, completes the remainder of the DIG2 HDMI/TMDS tail, covers a full DP2 stream/link packet block, covers VPG3, AFMT3, DME3, and a full DIG3 HDMI/TMDS stream-encoder block, then enters the DP3 block and stops inside `DP3_DP_DPHY_SYM0`. There are no functions, structs, branches, loops, local includes, or direct runtime side effects in this range.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata rather than distributed filesystem code.

## Register Blocks Covered

The DIG2 tail begins with `DIG2_HDMI_GENERIC_PACKET_CONTROL0` masks for generic packet slots 0 through 7, then defines slots 8 through 14 in `DIG2_HDMI_GENERIC_PACKET_CONTROL6` and immediate-send/pending fields for slots 0 through 14 in `DIG2_HDMI_GENERIC_PACKET_CONTROL5`. The DIG2 range also includes HDMI general control (`HDMI_GC`), generic-packet line-number controls, data-buffer disable controls, HDMI audio clock regeneration fields for 32/44.1/48 kHz families, AFMT bridge control, DIG back-end lane and enable controls, TMDS control characters, stereosync selection, sync-character patterns, DC balancer controls, TMDS control-bit generation, DIG version, and forced DIG disable.

The full `dce_dc_dio_dp2_dispdec` block describes DP2 DisplayPort stream fields. It includes link status and embedded-panel mode, pixel encoding/component depth and one/two-pixel processing mode, MSA colorimetry and misc bytes, lane-count configuration, video stream enable/status/defer, steer FIFO reset and overflow reporting, video `M/N` timing generation, link framing, HBR2 eye pattern enable, MSA/VBID placement, video-stream-disable interrupt controls, DPHY FEC/scrambler/bypass/test/training fields, symbol pattern and PRBS controls, DPHY CRC controls/results/status, fast training controls/status, DP secondary-data packet controls, audio `M/N` fields, MST/MSE rate and stream allocation table fields, DPHY byte-swap and pattern controls, MSA timing parameters, MSO fields, DSC enable, extended SEC control registers, data-buffer controls, MSA/VBID misc overrides, metadata transmission, ALPM and AUX-less ALPM controls, and generic stream packet controls/status for GSP8 through GSP11.

The VPG3 block defines video packet generator fields for generic packet access/data, generic stream packet frame-update and immediate-update controls, packet update/conflict status, memory power controls, ISRC access/data, and MPEG info registers. These fields are used to stage and trigger stream metadata packets.

The AFMT3 block defines audio formatter fields: VBI/audio packet controls, audio infoframe payload fields, IEC 60958 channel-status words, audio CRC controls/results, ramp controls, formatter status, main audio packet controls, infoframe control, interrupt status, audio source selection, and AFMT memory power. This is the stream audio and HDMI/DP packet formatting surface for stream instance 3.

The DME3 block defines display micro-engine control fields including stream/video enable, clock enable, data enable, request/ack status, and memory low-power controls.

The DIG3 block defines stream encoder front-end and back-end fields. It includes front-end clock/mode/reset/enable/status and link target fields, output CRC controls/results, clock/test/random patterns, FIFO control and calibration fields, HDMI metadata/control/status/audio/ACR/VBI/infoframe/generic-packet controls, AFMT bridge control, DIG back-end lane controls, TMDS packet/control-character/sync/DC-balancer fields, DIG version, and forced disable.

The DP3 block begins at `dce_dc_dio_dp3_dispdec` and is only partially present in this chunk. The visible fields cover link status, pixel format, MSA colorimetry and misc bytes, lane-count config, video stream control, steer FIFO and overflow controls, alternate DPHY scrambler reset, video timing and `M/N`, link framing, HBR2 eye pattern enable, MSA/VBID location, video disable interrupt controls, DPHY FEC/scrambler/bypass/test controls, training-pattern selection, and the first two masks in `DP3_DP_DPHY_SYM0`. The rest of DP3 continues in a later chunk.

## Important APIs, Types, And Macros

The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a field inside a 32-bit MMIO register.
- `<REGISTER>__<FIELD>_MASK` gives the field mask used to isolate or update that field.
- Comments such as `//DP2_DP_SEC_CNTL` and `// addressBlock: dce_dc_dio_dp2_dispdec` delimit generated register groups but are not compiled APIs.

The visible macro prefixes are `DIG2_`, `DP2_`, `VPG3_`, `AFMT3_`, `DME3_`, `DIG3_`, and partial `DP3_`. They map onto generic driver field names through token-pasting register-list macros in the AMD display stack. For example, stream-encoder code talks about fields such as `HDMI_GENERIC8_SEND`, `DP_VID_STREAM_ENABLE`, `DP_VID_N`, `DP_MSA_MISC0`, `AFMT_AUDIO_CLOCK_EN`, `TMDS_PIXEL_ENCODING`, and `DIG_FIFO_RESET`; resource construction binds those generic names to the instance-specific generated macros in this file.

The runtime objects that receive these shift/mask tables include `struct dcn10_stream_encoder_shift`, `struct dcn10_stream_encoder_mask`, `struct dcn31_vpg_shift`, `struct dcn31_vpg_mask`, `struct dcn31_afmt_shift`, and `struct dcn31_afmt_mask`. This chunk itself does not define those types; it supplies constants consumed by their initializers.

## Control Flow

This header has no control flow. Runtime sequencing is supplied by DCN 3.1.4 resource construction and DIO stream-encoder methods:

1. `dcn314_resource.c` includes `dcn_3_1_4_offset.h` and this shift/mask header.
2. Resource macros such as `SR`, `SRI`, and related token-pasting helpers bind offsets from the companion header to per-instance register tables.
3. Shift/mask initializers bind field constants from this header to stream encoder, VPG, AFMT, DSC, DWB, MPC, DCCG, AUX, and other DCN hardware objects.
4. Runtime code later calls register helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, and `REG_WAIT` to program HDMI, TMDS, DP, VPG, AFMT, DME, and packet fields through those tables.

The sequencing requirements are not encoded in the macros. Consumers must still order FIFO resets, clock enables, stream enable/disable, packet double-buffer updates, AFMT/VPG packet staging, DP link training, video `M/N` programming, DSC PPS packet programming, interrupt acknowledge/clear operations, memory power transitions, and suspend/resume restoration correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes MMIO-backed GPU display state. The represented hardware state includes:

- HDMI/TMDS stream encoder configuration, including generic packets, metadata packets, infoframes, audio clock regeneration, AVMUTE, TMDS symbols, lane enables, data-buffer controls, output CRC, test patterns, and FIFO controls.
- DisplayPort stream and link state for DP2 and partial DP3, including link status, pixel format, video stream enable/status, timing `M/N`, MSA/VBID fields, link framing, DPHY FEC/scrambler/training/test/CRC controls, secondary-data packet controls, MST allocation tables, MSO/DSC controls, ALPM, and AUX-less ALPM fields.
- Packet generator state in VPG3, including generic packet data windows, frame/immediate update triggers, conflict/status flags, ISRC/MPEG payloads, and memory power state.
- Audio formatter state in AFMT3, including audio infoframes, channel-status words, sample/audio clock enables, audio packet controls, CRC telemetry, ramp controls, and memory power state.
- DME3 control and memory low-power state.

Configuration fields generally persist until the driver reprograms them, the block is reset, display power/clock gating changes state, firmware changes the register, suspend/resume restores state, or the ASIC resets. Status, pending, interrupt, CRC, overflow, and readback fields are hardware-defined and may be read-only, sticky, write-one-to-clear, self-clearing, or timing-sensitive; this generated header does not distinguish those semantics.

## Dependencies And Integration Points

This chunk must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`. The offset header provides `reg...` register addresses and `_BASE_IDX` selectors; this file provides the matching field layouts. A generated-name mismatch can break compilation, while a wrong numeric shift or mask can compile and corrupt register updates at runtime.

Direct include sites in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`

The main functional integration point is `dcn314_resource.c`. It constructs VPG instances, AFMT instances, five stream encoders, AUX/I2C engines, link encoders, DSC, DWB, MPC, DCCG, and other DCN objects from generated offset and shift/mask tables. For this chunk, the most direct consumers are the VPG3, AFMT3, DIG2/DIG3 stream-encoder, DP2, and partial DP3 field tables.

Stream encoder behavior is implemented in `display/dc/dio/dcn314/dcn314_dio_stream_encoder.c` and inherited DCN10/DCN30 helper code. Those paths program fields represented here when setting HDMI/DVI stream attributes, enabling HDMI scrambling and infoframes, sending generic packets, setting AVMUTE, blanking/unblanking DP, programming DP video `M/N`, resetting/enabling DIG FIFO state, updating DP secondary-data packets, reading encoder state, and configuring DSC-related DP secondary packet behavior.

`irq_service_dcn314.c` uses the same generated headers for interrupt status/mask/ack field definitions. `dmub_dcn314.c` uses the generated register metadata for DMUB-facing register offsets and masks when display firmware services need DCN314 register access.

## Risks And Edge Cases

The highest risk is generated-header drift from the hardware specification or from the companion offset header. These macros are untyped constants; an incorrect mask or shift can compile cleanly while modifying the wrong bits in a stream encoder, packet generator, audio formatter, DP link, or interrupt/status register.

The chunk has artificial boundaries. It starts after the `DIG2_HDMI_GENERIC_PACKET_CONTROL0` shift definitions and ends inside `DP3_DP_DPHY_SYM0`; adjacent chunk reports are required before the final per-file document can make complete claims about all DIG2 or DP3 fields.

Repeated instance families are copy-sensitive. DP2 and DP3, DIG2 and DIG3, and the VPG/AFMT/DME instance naming scheme are structurally similar but not interchangeable. A field error may only reproduce on a specific connector, stream encoder, MST route, or multi-display topology.

Packet-update fields are timing-sensitive. VPG/AFMT generic packet update, HDMI generic immediate send, DP secondary-data packet sends, pending bits, conflict flags, and line-number fields interact with vertical blanking and double-buffered update timing. Wrong masks can cause stale metadata, missing infoframes, repeated packets, or update conflicts without a simple kernel crash.

DP link and video-stream fields are mode-sensitive. `DP_VID_STREAM_ENABLE`, `DP_VID_STREAM_STATUS`, `DP_VID_M/N`, MSA timing, DPHY FEC/scrambler/training controls, and MST allocation fields must match link training, timing, lane count, link rate, DSC, and MSO configuration. Errors often appear as blank displays, intermittent link training failures, corrupted MST payloads, or failures only at high bandwidth.

FIFO, data-buffer, CRC, and overflow fields are diagnostic and stateful. Incorrect reset/ack/mask handling can hide underflow/overflow problems or produce misleading CRC/test-pattern results. `DP_STEER_FIFO`, `DIG_FIFO_CTRL*`, and DB disable controls are especially sensitive around stream enable/disable and mode changes.

Memory-power fields in VPG3, AFMT3, and DME3 are power-management sensitive. Forcing light sleep or disabling memory while a stream, audio path, or packet generator is active can produce failures around hotplug, blanking, suspend/resume, or rapid modesets.

## Test Signals

Build-time validation should compile AMDGPU display support with DCN314 enabled. High-signal failures are missing or renamed generated macros referenced by `dcn314_resource.c`, `irq_service_dcn314.c`, `dmub_dcn314.c`, `dcn314_dio_stream_encoder.c`, `dcn10_stream_encoder.h`, `dcn31_vpg.h`, and `dcn31_afmt.h`.

Mechanical checks should verify that every field in this range has the expected paired `__SHIFT` and `_MASK` definitions except where the chunk boundary intentionally includes only a tail or head of a register group. Cross-checking against AMD's generated DCN 3.1.4 register database is the strongest regression signal because the file is generated metadata.

Runtime stream tests should cover DP and HDMI outputs that map to DIG2/DIG3 and DP2/DP3 where the ASIC routing allows it. Useful signals include successful modesets, link training, stream blank/unblank, FIFO reset/enable completion, no unexpected `DP_VID_STREAM_STATUS` stalls, no steer/TU overflow flags, and stable display across link-rate and lane-count changes.

Packet and audio validation should cover HDMI infoframes, generic packets 0 through 14, HDMI metadata packets, AVMUTE, ACR programming/readback, DP secondary-data packets, VPG generic packets, ISRC/MPEG metadata, AFMT audio sample/clock enable, IEC 60958 channel status, and audio playback over HDMI/DP.

DP advanced-feature validation should exercise MST/MSE allocation updates, DSC PPS secondary packets, MSO controls, DPHY FEC and scrambler settings, HBR2 test pattern paths, DPHY CRC capture, ALPM, AUX-less ALPM, and suspend/resume on DP2 and DP3 paths.

Diagnostic checks should inspect kernel logs and display traces for AUX/DP link failures, hotplug storms, audio dropouts, infoframe mismatch, CRC mismatch, FIFO underflow/overflow, stuck packet pending bits, stuck interrupt status, and resume failures.

## Cross-Chunk Notes

Previous chunks own the beginning of the DIG2 HDMI generic-packet register group, including shift definitions that precede the visible `DIG2_HDMI_GENERIC_PACKET_CONTROL0` masks. Later chunks continue the DP3 register block after `DP3_DP_DPHY_SYM0`. The final per-file research document should merge adjacent chunk reports before claiming complete coverage of the full `dcn_3_1_4_sh_mask.h` DIO, VPG, AFMT, DME, DIG, or DP field namespace.
