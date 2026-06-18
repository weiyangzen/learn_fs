# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 56832-59202

## Purpose

This chunk is a generated AMD DCN 3.6.0 register shift/mask slice. It contains no executable logic; it exports C preprocessor constants that describe bit positions and masks for memory-mapped display/audio controller registers. Driver code combines these constants with the companion `dcn_3_6_0_offset.h` offsets so register helper macros can pack, unpack, and update specific hardware fields without spelling numeric bit layouts at each call site.

The requested range is focused on Azalia/HD-audio endpoint-indirect register fields for display audio. It contains 2,048 `#define` entries, including 1,023 `__SHIFT` macros and 1,037 `_MASK` macros, plus 311 register-name comments and 4 `addressBlock` comments. The line boundaries are artificial: the chunk starts midway through `AZF0ENDPOINT2` pin audio descriptor and multichannel definitions, includes complete or near-complete endpoint blocks for `AZF0ENDPOINT3`, `AZF0ENDPOINT4`, and `AZF0ENDPOINT5`, and ends midway through `AZF0ENDPOINT6` pin/channel-status definitions. The next chunk begins `AZF0ENDPOINT7`.

Although the file sits under a local `ceph-client` source mirror, this chunk is AMDGPU display/audio hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, allocations, includes, or direct I/O operations in this range. The interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field inside the named register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or preserving that field in read/modify/write operations.

The main register families covered are:

- `AZF0ENDPOINT2_*`: tail of endpoint 2 pin control metadata, starting in audio descriptor 3-13 and multichannel control, then lip-sync/HBR response, sink information, hot-plug/audio enablement, unsolicited-response force, default configuration, IEC 60958 channel-status overrides, association information, LPIB snapshot/counter fields, coding type, format-change signaling, remote keepalive, audio enable/disable/format-change interrupt status, and endpoint fine-grain clock-gating repeat disable.
- `AZF0ENDPOINT3_*`, `AZF0ENDPOINT4_*`, and `AZF0ENDPOINT5_*`: repeated endpoint-indirect blocks containing converter widget capability and format controls, stream/channel IDs, digital converter channel-status bits, stream format and supported rate parameters, stripe control, ramp rate, GTC embedding/counter delta telemetry, pin widget capabilities, pin capabilities, unsolicited-response and pin-sense controls, widget output enable, channel/speaker mapping, ACP packet data, audio descriptors 0-13, multichannel pair/single controls, sink metadata, hot-plug/audio state, IEC 60958 override registers, LPIB/status/format-change registers, and audio interrupt status. Endpoint 5 also has `CODEC_CONVERTER_CONTROL_GTC_OFFSET_DEBUG`.
- `AZF0ENDPOINT6_*`: begins another repeated endpoint-indirect block and reaches through pin control multichannel mode and `PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8` plus the start of the post-override pin/status area before the chunk boundary.

Important field groups include:

- Audio format programming: `NUMBER_OF_CHANNELS`, `BITS_PER_SAMPLE`, `SAMPLE_BASE_DIVISOR`, `SAMPLE_BASE_MULTIPLE`, `SAMPLE_BASE_RATE`, and `STREAM_TYPE`.
- Stream routing and digital output: `CHANNEL_ID`, `STREAM_ID`, `DIGEN`, validity/copy/non-audio/professional bits, category/channel count, and `KEEPALIVE`.
- Sink and ELD-like metadata: manufacturer/product IDs, port IDs, display-description bytes, audio descriptor `MAX_CHANNELS`, supported frequencies, descriptor byte 2, and stereo frequency support for descriptor 0.
- Pin/output control: `OUT_ENABLE`, HDMI/DP connection indicators, speaker/channel allocation, LFE/downmix/level-shift bits, HBR capability/enable, lipsync values, hot-plug clock/audio state, and default association/configuration fields.
- Multichannel programming: pair-mode fields for `MULTICHANNEL01/23/45/67`, single odd-channel fields for `MULTICHANNEL1/3/5/7`, mute bits, per-channel IDs, and `MULTICHANNEL_MODE`.
- IEC 60958 channel-status override fields: mode, source number, clock accuracy, word length, sampling frequency, original sampling frequency, frequency coefficient, MPEG surround, CGMS-A, and channel numbers for left/right/2-7.
- Runtime observability and events: LPIB snapshot lock, cyclic wrap count, LPIB value, LPIB timer snapshot, coding type, format-changed flag/ack/reason/response, wireless display identification, remote keepalive capability, audio enable state, audio enabled/disabled/format-changed interrupt flags, masks, types, and endpoint fine-grain clock-gating repeat disable.

The symbolic enum values for many Azalia fields live outside this header, notably in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h`, while this chunk supplies only positions and masks.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display/audio code that includes the generated DCN 3.6 headers:

1. DCN 3.6 code includes `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h`.
2. Register-list macros token-paste register and field names into per-block address, shift, and mask tables.
3. DCN 3.6 resource, IRQ, and DMUB setup code wires those tables into display block objects and firmware-facing register descriptions.
4. Runtime display/audio paths use register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` to manipulate only the intended MMIO fields.

The macros do not encode sequencing. Consumers still have to program audio format, channel mapping, IEC 60958 status, infoframes/AFMT state, sink metadata, enable bits, and interrupt/status bits in the order required by the display engine, HD-audio controller, and link type. They also have to coordinate with DRM connector state, ELD notification, hotplug, stream commit, suspend/resume, and display power/clock gating.

## State And Persistence Behavior

This chunk stores no software state and persists nothing directly. It describes hardware-visible state in Azalia endpoint registers:

- Converter state for current audio sample format, stream ID/channel ID, digital-converter status bits, supported stream formats/rates, ramp behavior, stripe control, and GTC embedding/counter-delta telemetry.
- Pin state for output enablement, channel/speaker mapping, ACP packet metadata, audio descriptors, multichannel enable/mute/channel IDs, lipsync/HBR capabilities, sink identity/description, default configuration, hot-plug/audio enable state, forced unsolicited responses, and association info.
- Channel-status override state for IEC 60958 fields consumed by HDMI/DP audio sinks and audio packet generation paths.
- Runtime status and event state for LPIB snapshots, coding type, audio format changes, wireless display/remote keepalive, audio enable/disable status, and endpoint interrupt flags/masks/types.
- Power/clock-related state through endpoint fine-grain clock-gating repeat disable and hot-plug clock state fields.

Persistence is hardware-defined. Configuration fields usually remain until a modeset, audio stream reprogramming, hotplug handling, suspend/resume, power-gating transition, GPU reset, or ASIC reset rewrites them. Status, interrupt, snapshot, LPIB, GTC, and debug fields may be read-only, sticky, write-one-to-clear, self-clearing, clock-gated, or valid only while the related endpoint and display pipe are powered. This generated header does not identify those access semantics; consumers must rely on the register specification and the block-specific driver logic.

## Dependencies And Integration Points

This file must remain synchronized with AMD's generated DCN 3.6.0 register database and the matching offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h` supplies the matching MMIO offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c` includes both DCN 3.6 generated headers while initializing DMUB register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c` includes them for DCN 3.6 interrupt-source setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c` includes them for DCN 3.6 resource construction and hardware register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h` provides symbolic values for many Azalia audio format, digital converter, pin, multichannel, and soft-reset fields whose masks are defined here.
- Display manager audio paths in `amdgpu_dm.c` maintain connector audio instances, expose ELD through the DRM audio component, fill audio info from EDID/SAD data, and notify audio clients when endpoints change.
- AFMT/APG code under `display/dc/dcn31/` handles audio packet and 60958 programming for nearby DCN generations; DCN 3.6 consumers use the same generated-header style even when field names are routed through version-specific register tables.

The most direct behavioral integration is HDMI/DisplayPort audio enumeration and playback: EDID-derived audio modes become stream/audio-info state, DCN audio/AFMT/APG logic programs endpoint and packet fields, and the Linux audio component obtains ELD/pin notifications for the HDA side.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong MMIO bit, clobbering an adjacent field, or silently leaving an audio feature disabled.
- The file is generated. Manual edits risk divergence from the authoritative register database, the offset header, firmware assumptions, and silicon documentation.
- The chunk boundaries are not semantic. Endpoint 2 starts before this range, endpoint 6 continues after this range, and the final per-file report should merge adjacent chunks before making whole-endpoint coverage claims.
- Endpoint blocks are highly repetitive. Generator drift in one endpoint can be hard to spot because endpoint 3, 4, 5, and 6 use near-identical field names with different prefixes.
- Audio format fields are interoperability-sensitive. Incorrect `NUMBER_OF_CHANNELS`, sample rate, bit depth, stream type, or stream/channel ID masks can cause missing audio, wrong sample rate, channel swaps, or sink rejection.
- IEC 60958 channel-status fields are subtle. Wrong clock accuracy, word length, sample frequency, source number, CGMS-A, or channel-number masks can create sink-specific failures even when simple stereo PCM works.
- Multichannel fields are user-visible. Pair-mode versus single-mode mistakes, incorrect mute bits, or wrong channel IDs can break surround audio, downmix behavior, or old audio-driver compatibility.
- Sink metadata and audio descriptors feed ELD-like behavior. Bad manufacturer/product IDs, port IDs, display description bytes, SAD descriptor fields, speaker allocation, or lipsync/HBR fields can cause ALSA/HD-audio clients to expose wrong capabilities.
- Status/interrupt fields are side-effect-sensitive. Confusing flag, mask, type, clear, or ack behavior can cause missed enable/disable/format-change notifications or interrupt storms.
- LPIB, timer snapshot, GTC, and wrap-count fields can be timing-sensitive and may be invalid while endpoints are gated, disabled, or in reset.
- Clock-gating and hot-plug audio state can interact with suspend/resume and runtime power management; wrong masks may produce failures only after idle, link retraining, or hotplug cycles.

## Test Signals

Useful validation combines generated-header checks with audio/display behavior on DCN 3.6 hardware:

- Build AMDGPU display support with DCN 3.6 enabled. Missing or renamed constants should fail in DCN36 DMUB, IRQ, resource, register-helper, audio, AFMT, or APG table construction if those fields are referenced.
- Mechanically compare this range against AMD's authoritative DCN 3.6.0 register source and the adjacent `dcn_3_6_0_offset.h` names. Account for the artificial start in endpoint 2 and artificial end in endpoint 6.
- Run static consistency checks that each complete register group has paired `__SHIFT` and `_MASK` definitions once adjacent chunks are considered.
- Exercise HDMI and DisplayPort audio hotplug with EDID/SAD parsing, ELD retrieval through the DRM audio component, connector audio instance assignment, and pin ELD notification.
- Validate stereo PCM and multichannel playback across 2/6/8 channel modes, 44.1/48/96/192 kHz rates where supported, 16/20/24-bit depths, HBR/non-PCM paths, and sink replug/retrain events.
- Check speaker allocation, channel allocation, LFE/downmix behavior, multichannel mute/channel IDs, pair versus single multichannel mode, and IEC 60958 channel-status reporting with a receiver or analyzer.
- Exercise format changes while audio is active and verify format-changed status/interrupt handling, LPIB progress, timer snapshots, and absence of stale endpoint status.
- Run suspend/resume, GPU reset, runtime power management, display off/on, and repeated modeset cycles while monitoring for lost audio, stale ELD, wrong sink capabilities, interrupt floods, or endpoint clock-gating failures.

## Cross-Chunk Notes

The previous chunk contains the beginning of `AZF0ENDPOINT2` converter/pin/audio descriptor definitions. This chunk continues endpoint 2, covers endpoint blocks 3 through 5, and starts endpoint 6. The next chunk continues endpoint 6 and begins endpoint 7. The final per-file research document should reconcile these neighboring chunks before summarizing all Azalia endpoint coverage in `dcn_3_6_0_sh_mask.h`.
