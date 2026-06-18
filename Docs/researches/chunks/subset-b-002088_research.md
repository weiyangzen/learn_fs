# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 2216-4415

## Purpose

This chunk is generated AMD DCN 3.5.1 register field metadata. It contains no executable driver logic; it exports C preprocessor constants that describe bit shifts and masks for Azalia/HD Audio codec endpoint registers. The constants follow the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming pattern and are consumed with the matching DCN 3.5.1 offset header and AMD display register helper macros.

The requested range covers the tail of output endpoint 3, full output endpoints 4 through 7, full input endpoint 0, and the beginning of input endpoint 1. These endpoint blocks describe HDMI/DisplayPort audio converter and pin-widget capabilities, stream format fields, channel/stream ID assignment, IEC 60958 channel-status overrides, sink/audio descriptor data, HBR, unsolicited responses, LPIB snapshots, hot-plug/audio state, GTC timestamp embedding, multichannel routing, and input-infoframe/activity state.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or callbacks in this range. The exported interface is entirely generated macros:

- `AZF0ENDPOINT*_...__FIELD__SHIFT`: bit position for an Azalia output endpoint field.
- `AZF0ENDPOINT*_...__FIELD_MASK`: bit mask for the same output endpoint field.
- `AZF0INPUTENDPOINT*_...__FIELD__SHIFT`: bit position for an Azalia input endpoint field.
- `AZF0INPUTENDPOINT*_...__FIELD_MASK`: bit mask for the same input endpoint field.

Major macro families in this chunk:

- Endpoint 3 tail: `AZF0ENDPOINT3_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_4` mask tail, `CODEC_CS_OVERRIDE_5` through `8`, pin association, digital-output active status, LPIB snapshot registers, coding type, format-change state/ack, wireless display identification, remote keepalive, audio enable status, and audio enabled/disabled/format-changed interrupt status fields.
- Output endpoints 4-7: repeated full codec converter and pin-control field maps for each endpoint instance. The converter side includes audio-widget capabilities, converter format, channel/stream ID, digital converter flags, supported stream formats, supported size/rates, stripe control, ramp rate, GTC embedding controls, and GTC counter delta/min/max registers.
- Output endpoint pin widgets: repeated audio-widget and pin-capability fields, unsolicited response enable/tag and force payload, pin sense, output widget enable, speaker/channel allocation, SAD/audio descriptors 0-13, sink information 0-8, HBR, lipsync, hot-plug control, multichannel mode, multichannel enables for channels 0-7, response configuration defaults, IEC 60958 channel-status override words 0-8, LPIB snapshots, coding type, format-change control, wireless display identification, remote keepalive, and audio status/interrupt fields.
- Input endpoint 0: input converter capabilities and stream-format controls, input pin capabilities, unsolicited response controls, input pin sense with presence detect, input widget enable, multichannel input routing, HBR, channel allocation, hot-plug/audio-enable state, response configuration defaults, LPIB snapshots, input status/control, and input infoframe fields.
- Input endpoint 1 boundary: only the start of `AZF0INPUTENDPOINT1_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` is present; this chunk includes all fourteen shift definitions and only the first six mask definitions before the requested range ends.

The range is highly repetitive by endpoint instance. Output endpoints 4, 5, 6, and 7 each contribute the same endpoint-local register groups with instance-specific macro prefixes, while input endpoint 0 has a related but input-specific register layout.

## Control Flow

This header has no runtime control flow. It becomes part of runtime behavior only when included by AMD display code that constructs register metadata tables:

1. DCN 3.5.1 display modules include `dcn_3_5_1_sh_mask.h` together with the corresponding offset header.
2. Register-list macros token-paste register and field names into mask/shift tables.
3. Runtime code calls helper operations such as `REG_GET`, `REG_SET`, `REG_UPDATE`, and related AMD display register macros. Those helpers use these constants to isolate a field, shift values into position, and preserve unrelated bits during read-modify-write operations.
4. Hardware sequencing, ownership, access ordering, and status interpretation live in the consuming driver and firmware paths. This generated header only states bit locations.

For this chunk, the implied runtime flows are audio endpoint discovery/configuration, HDMI/DP audio format programming, stream/channel mapping, speaker and SAD propagation, HBR enablement, audio hot-plug and enable/disable event handling, input-audio status reporting, GTC audio timestamp embedding, LPIB snapshot reading, and unsolicited response programming.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed GPU display/audio state.

Represented hardware state includes per-endpoint converter format and stream IDs, digital converter flags such as `DIGEN`, validity/copy/non-audio/pro mode bits, endpoint capability fields, sink descriptor bytes, speaker allocation, IEC 60958 channel status, multichannel enable/mute/channel IDs, hot-plug clock/audio enable state, remote keepalive, LPIB position snapshots, audio enable and format-change status, GTC timing deltas, input activity/channel layout, and audio infoframe validity.

Persistence is determined by the Azalia/DCN hardware block. Capability fields are effectively hardware-described constants. Control fields usually persist until reprogrammed, modeset, suspend/resume, power gating, audio block reset, or ASIC reset. Status, interrupt, force, ack, and snapshot fields may be sticky, self-clearing, read-only, write-one-to-clear, or latched depending on the register semantics supplied by the hardware specification and consuming code.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5.1 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h`, which provides the corresponding MMIO offsets and base-index selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h`, which contains symbolic enum values for many Azalia input endpoint fields such as audio-widget capabilities, pin capabilities, HBR capability, and pin/control options.
- AMD display register helper infrastructure that consumes generated shift/mask constants through `REG_*`, `SF`, `SRI`, and related table-building macros.

Representative integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`, which includes `dcn_3_5_1_sh_mask.h` as part of the DCN 3.5.1 register interface.
- AMD display audio paths that program Azalia codec converter and pin-widget state for HDMI/DP audio, including converter format, channel/stream IDs, digital converter state, channel allocation, speaker allocation, SAD data, HBR, and IEC 60958 channel status.
- Display hotplug and interrupt service paths that depend on audio enabled/disabled/format-changed status fields and unsolicited-response enable/force fields.
- Diagnostics or debug paths that read LPIB snapshots, GTC counter deltas, audio enable state, sink-info fields, input activity, and input infoframe fields.

The later merge lane should combine this with adjacent chunks for the complete Azalia endpoint map. This chunk starts in the middle of endpoint 3 and ends inside the input endpoint 1 audio-widget capability register.

## Risks And Edge Cases

- Shift/mask drift is the main risk. These are untyped constants, so an incorrect bit position can compile while silently targeting the wrong hardware bit.
- Repeated endpoint blocks are copy-sensitive. Output endpoints 4-7 are near-identical; a single instance-specific typo can affect only one display/audio endpoint and be missed by basic single-monitor testing.
- The chunk begins at masks for `AZF0ENDPOINT3_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_4` without the matching shifts in this range. Adjacent chunk data is needed to validate endpoint 3 completely.
- The chunk ends after only the first six masks for `AZF0INPUTENDPOINT1_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`. Adjacent chunk data is needed to validate input endpoint 1 completely.
- Audio format fields are compact and interdependent. Wrong masks for channel count, sample base divisor/multiple/rate, bits per sample, stream type, stream ID, or channel ID can produce silent audio, wrong channel mapping, or intermittent format negotiation failures.
- IEC 60958 channel-status override and SAD/sink-info fields affect what downstream receivers see. Bad masks can advertise incorrect sample rates, channel counts, coding types, speaker allocations, copyright/category bits, or validity flags.
- Interrupt and unsolicited-response bits are sensitive. Incorrect flag/mask/type, ack-enable, tag, enable, or force-payload metadata can cause missed audio events, stale format-change notifications, or unsolicited response storms.
- LPIB and timer snapshot fields are full-width or latch-sensitive. Consumers must apply hardware-specified locking/snapshot ordering; the macros do not encode ordering rules.
- Hot-plug and clock-gating fields can be unsafe or ineffective if accessed while the Azalia block is power-gated, reset, or not clocked.
- GTC embedding and counter-delta fields cross audio/video timing domains. Wrong field locations can break timestamp embedding or make synchronization diagnostics misleading.

## Test Signals

Useful validation signals are a combination of generated-header checks and hardware behavior:

- Build AMDGPU/DC with DCN 3.5.1 support enabled; missing, renamed, or malformed macros should fail in register table construction or direct register helper use.
- Mechanically verify that every complete register group in lines 2216-4415 has paired `__SHIFT` and `_MASK` definitions and that masks align with shifts and expected field widths. Exclude the known artificial boundaries at endpoint 3 `CODEC_CS_OVERRIDE_4` and input endpoint 1 audio-widget capabilities until adjacent chunks are merged.
- Diff this chunk against AMD's authoritative DCN 3.5.1 register source and nearby generated generations, especially `dcn_3_5_0_sh_mask.h`, where endpoint layouts are expected to remain compatible.
- Exercise HDMI and DisplayPort audio on endpoints corresponding to Azalia output endpoints 4-7: hotplug, audio enable/disable, stream start/stop, sample-rate changes, bit-depth changes, stereo and multichannel layouts, HBR formats, and suspend/resume.
- Verify receiver-visible data: EDID/SAD-derived audio descriptors, speaker/channel allocation, IEC 60958 channel-status fields, coding type, sink info, lipsync, and wireless display identification where applicable.
- Exercise unsolicited response handling and audio format-change paths, watching for missed events, repeated interrupts, stale status bits, and wrong reason/response fields.
- Read LPIB and LPIB timer snapshots during playback/capture and check for sane monotonic position reporting under wrap conditions.
- For input endpoint 0, test input activity detection, channel layout reporting, input infoframe validity, channel allocation, presence detect, HBR capability/enable, and multichannel input routing.
- Monitor kernel logs and display/audio diagnostics for audio dropouts, wrong channel mapping, hotplug regressions, DPCD/EDID audio inconsistencies, stuck audio interrupts, and suspend/resume audio failures.

## Cross-Chunk Notes

Previous chunks own the earlier Azalia endpoint 3 definitions, including the missing shifts for the `CODEC_CS_OVERRIDE_4` masks that open this range. Later chunks own the rest of input endpoint 1 and likely additional input endpoint/register definitions. The final per-file report should merge adjacent chunks before making complete claims about all DCN 3.5.1 Azalia endpoints or the full `dcn_3_5_1_sh_mask.h` register field map.
