# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 54331-56831

## Purpose

This chunk is generated AMD DCN 3.6.0 register shift/mask metadata for the display audio, or Azalia/HDA, hardware path. It contains no executable C logic. Its public surface is C preprocessor constants that encode bit positions and bit masks for DCN 3.6 audio codec, stream, CRC, endpoint, sink-info, and channel-status registers.

The requested range contains 2,039 `#define` entries, split into 1,020 `__SHIFT` macros and 1,019 `_MASK` macros, across 382 register-name groups. It starts just after the `AZALIA_F2_CODEC_PIN_CONTROL_FORMAT_CHANGED` group from the previous chunk and ends in the middle of `AZF0ENDPOINT2_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE`, so both boundaries are artificial line-split boundaries rather than complete hardware-block boundaries.

Although this file is under a local `ceph-client` source mirror, this chunk is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, locks, allocation paths, or direct MMIO operations in this range. The interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or updating that field.

The main register families in this chunk are:

- `AZALIA_F2_CODEC_PIN_*`: tail of F2 pin status/parameter support, including wireless display identification, remote keepalive, audio widget capabilities, pin capabilities, and connection-list length.
- `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`: codec descriptor format fields for max channels, supported frequencies, descriptor byte 2, and stereo-frequency support.
- `AZALIA_F2_CODEC_PIN_CONTROL_*` sink metadata: manufacturer/product IDs, sink description length, port IDs, and monitor-name bytes `SINK_DESCRIPTION0` through `SINK_DESCRIPTION17`.
- `AZALIA_INPUT_CRC0/1_CHANNEL*` and `AZALIA_CRC0/1_CHANNEL*`: per-channel input and output CRC result fields for channels 0-7.
- `AZALIA_F2_CODEC_INPUT_*`: input converter and input pin controls for converter format, channel/stream ID, digital converter status, widget capabilities, supported sizes/rates, stream formats, unsolicited responses, pin sense, default configuration, channel allocation, multichannel enablement, HBR response, LPIB snapshots, input status, infoframe, and channel status.
- `AZALIA_F2_CODEC_ROOT_*` and `AZALIA_F2_CODEC_FUNCTION_*`: root/function node identity, revision, subordinate-node count, power state, subsystem ID response, converter synchronization, reset, supported size/rates, stream formats, group type, and power states.
- `AZF0STREAM0` through `AZF0STREAM15`: repeated Azalia stream FIFO-size and latency-counter controls, worst-case latency, cumulative latency, and cumulative request counters.
- `AZF0ENDPOINT0`, `AZF0ENDPOINT1`, and the beginning of `AZF0ENDPOINT2`: repeated F0 endpoint codec converter and pin fields for audio widget capabilities, converter format, channel/stream ID, digital converter control, supported formats/rates, stripe control, ramp rate, GTC embedding/counter deltas, pin capabilities, unsolicited responses, pin sense, widget output enable, speaker/channel allocation, ACP data, audio descriptors, multichannel enablement, lipsync, HBR, sink info, hot-plug control, unsolicited-response force, default configuration, IEC 60958 channel-status overrides, association info, digital output status, LPIB snapshots, coding type, format-changed state, wireless display identification, remote keepalive, audio enable/disable/format-change interrupt status, and endpoint fine-grain clock-gating repeat disable.

Many groups are mechanically repeated per stream or endpoint. The repeated shapes are intentional: one wrong generated field in a single instance can break only that stream or connector while adjacent instances still work.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from AMDGPU display code that includes this generated header with the matching DCN 3.6 offset header:

1. DCN 3.6 code includes `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h`.
2. Register-list and field-list macros token-paste register and field names into per-block register, shift, and mask tables.
3. DCN 3.6 setup code wires those tables into DMUB, IRQ, resource, audio, and hardware-sequencer paths.
4. Runtime code reads, writes, or updates registers through helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `AZ_REG_READ`, `AZ_REG_WRITE`, `set_reg_field_value`, `FD_MASK`, and `FD_SHIFT`.

The chunk only defines bit layout. Sequencing is supplied by consumers. For example, `dce_audio.c` programs audio descriptors from EDID-derived audio modes, computes available bandwidth before exposing HBR support, writes sink manufacturer/product/name/port metadata, programs lipsync fields, and toggles hot-plug/audio-related fields through the Azalia register helpers.

## State And Persistence Behavior

This chunk stores no software state and persists nothing directly. It describes hardware-visible DCN 3.6 audio state:

- Codec capability state, including widget capabilities, pin capabilities, supported sample sizes/rates, stream format support, power states, and connection-list length.
- Audio format descriptor state for HDMI/DP audio format exposure, max channel count, sample-frequency support, descriptor byte 2, and stereo-frequency support.
- Input and output audio transport state for converter format, stream/channel IDs, digital converter bits, multichannel enable/mute/channel-ID fields, channel allocation, channel status, HBR capability/enablement, ACP packets, and infoframes.
- Sink identity state for ELD-like monitor information: manufacturer ID, product ID, sink description length, port IDs, and display-name bytes.
- Runtime status and diagnostics for output-active status, format-change notification/reason/response, audio enable/disable/format-change interrupt status, unsolicited responses, pin sense, LPIB and timer snapshots, stream FIFO size, stream latency counters, and per-channel CRC results.
- Timing and synchronization state for lipsync response fields, GTC embedding, GTC counter deltas/min/max, converter synchronization, and LPIB snapshot locking/wrap count.
- Power and clock-related state for codec/function power state, hot-plug control clock-gating bits, endpoint audio-enabled state, and endpoint fine-grain clock-gating repeat disable.

Persistence is hardware-defined. Configuration fields generally remain until modeset/audio reconfiguration, connector hotplug, stream teardown, suspend/resume, power gating, GPU reset, or ASIC reset. Status, interrupt, CRC, counter, snapshot, force, reset, and acknowledge fields can be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the associated audio controller, stream, endpoint, and display link are powered and clocked. This generated header does not describe access semantics; consumers must follow the register specification and block-specific driver code.

## Dependencies And Integration Points

This file must stay synchronized with AMD's generated DCN 3.6.0 register database and with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h`, which supplies matching MMIO offsets and base indexes. A shift/mask header from one ASIC generation paired with a different offset header can compile while programming incorrect bits.

Direct DCN 3.6 integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c`, which includes the offset and shift/mask headers and initializes DMUB register masks/shifts with `FD_MASK` and `FD_SHIFT`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c`, which includes both generated headers for DCN 3.6 resource construction.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c`, which includes both generated headers for interrupt source setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.h`, whose register list includes Azalia-level resources such as `AZALIA_AUDIO_DTO` and `AZALIA_CONTROLLER_CLOCK_GATING`.
- Shared audio code such as `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.c`, which programs the same Azalia/HDA semantic fields for HBR capability, audio descriptors, lipsync, sink info, and hot-plug/audio control through generation-specific register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h`, which supplies semantic enum values for many Azalia field families such as converter format, digital converter bits, audio descriptor format codes, multichannel mute/mode, unsolicited-response enablement, and widget output enablement.

The behavioral integration surface is display audio over HDMI/DP, including EDID/ELD-derived capability exposure, audio stream formatting, bandwidth/HBR decisions, multichannel layout, sink identification, link-associated audio status, interrupt reporting, CRC diagnostics, and stream latency observability.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong mask or shift can compile cleanly while updating the wrong MMIO bits or preserving the wrong adjacent fields.
- The file is generated. Manual edits risk diverging from the authoritative register database, the matching offset header, firmware expectations, and silicon documentation.
- The chunk boundaries are not semantic. The previous chunk contains part of `AZALIA_F2_CODEC_PIN_CONTROL_FORMAT_CHANGED`; the next chunk continues the `AZF0ENDPOINT2_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE` masks and later endpoint fields.
- Repeated stream and endpoint layouts can hide one-instance generator drift. Streams 0-15 and endpoints 0-2 should not be assumed correct merely because another instance works.
- Audio descriptor fields are user-visible through HDMI/DP audio capability reporting. Bad max-channel, frequency, or descriptor-byte masks can expose unsupported formats or hide valid formats, causing no-audio, fallback stereo, or compressed-audio failures.
- HBR, multichannel, and channel-status fields are interoperability-sensitive. Wrong masks can break 192 kHz/8-channel checks, compressed bitstream modes, IEC 60958 channel numbers, mute state, or channel mapping.
- Sink-info fields pack byte strings and IDs. Off-by-one masks or wrong byte lanes can corrupt monitor names, manufacturer/product IDs, or port identifiers consumed by audio user space.
- Interrupt/status fields are side-effect-sensitive. Confusing enable, status, clear, force, and response fields can cause missed audio format-change notifications, unsolicited-response storms, or stale hotplug/audio status.
- LPIB, timer snapshot, CRC, and latency-counter fields are diagnostic and timing-sensitive. Incorrect definitions can make debugging audio underruns, synchronization, or channel corruption misleading.
- Power, clock-gating, hot-plug, reset, and function power-state fields can interact with runtime PM and display power sequencing; invalid updates may only reproduce during suspend/resume, rapid hotplug, or clock-gated idle transitions.

## Test Signals

Useful validation should combine generated-header consistency checks with DCN 3.6 display-audio behavior:

- Build AMDGPU display support with DCN 3.6 enabled. Missing or renamed fields should fail where DCN36 DMUB, IRQ, resource, audio, or register-helper tables reference them.
- Mechanically compare this line range against AMD's authoritative DCN 3.6.0 register source and verify that all complete register groups have matching `__SHIFT` and `_MASK` entries, allowing for the known partial groups at both boundaries.
- Exercise HDMI and DisplayPort audio on DCN 3.6 hardware across stereo, 5.1/7.1 LPCM, 44.1/48/96/192 kHz, compressed formats, and HBR-capable modes.
- Verify EDID/ELD-derived audio descriptors and sink info from user space, including monitor name length/bytes, manufacturer/product IDs, port IDs, channel counts, sample rates, and compressed-format capability exposure.
- Test hotplug, unplug/replug, MST, suspend/resume, runtime power management, audio stream start/stop, and rapid modesets while watching for no-audio, stale audio devices, missing format-change events, or interrupt storms.
- Validate multichannel mapping and mute/channel-ID programming with channel-order tests and compressed bitstream playback.
- Use CRC, LPIB snapshot, latency-counter, and debug/status reads where available to confirm counters update and snapshots are coherent while audio is active.
- Watch kernel logs and display/audio diagnostics for HBR exposure mismatches, ELD corruption, HDMI/DP audio underruns, incorrect channel allocation, stuck audio-enabled/disabled interrupt status, and resume-only audio failures.

## Cross-Chunk Notes

The final per-file research document should merge this with adjacent chunks before making whole-file claims about all DCN 3.6 Azalia register fields. The preceding chunk owns the beginning of the `FORMAT_CHANGED` group, and the following chunk owns the rest of `AZF0ENDPOINT2` plus later endpoint and audio blocks.
