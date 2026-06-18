# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 59203-61489

## Purpose

This chunk is a generated AMD DCN 3.6.0 register shift/mask slice for Azalia/HD-audio endpoint register fields. It contains no executable C logic; its public surface is C preprocessor constants that give bit positions and masks for fields inside DCN 3.6 audio codec endpoint registers. Driver code combines these constants with the companion register-offset header to pack, extract, and update individual MMIO fields without repeating literal bit layouts.

The requested range contains 2,027 `#define` entries: 1,015 `__SHIFT` constants and 1,012 `_MASK` constants. The range is not a semantic hardware boundary. It starts in the middle of `AZF0ENDPOINT6_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_1`, covers the rest of endpoint 6's pin/audio-status tail, all of output endpoint 7, all of input endpoints 0 through 5, and ends in the middle of input endpoint 6's digital-converter control group. Adjacent chunks are required to recover the complete endpoint 6 and input endpoint 6 register groups.

Although the repository path is under a `ceph-client` mirror, this source is AMDGPU display hardware metadata. It does not implement Ceph, storage, or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocation paths, locks, callbacks, or direct I/O routines in this line range. The only API is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the low-bit position of a field within a 32-bit register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate or preserve that field in read/modify/write register operations.

The main macro families in this chunk are:

- `AZF0ENDPOINT6_*`: the tail of output endpoint 6. This begins with IEC 60958 channel-status override fields for clock accuracy, word length, sampling frequency, original sampling frequency, sample-frequency coefficient, MPEG surround information, CGMS-A, and channel-number fields. It then defines association information, digital-output activity, LPIB snapshot/LPIB/timer snapshot, coding type, format-change status and response, wireless-display identification, remote keepalive, audio enable status, audio enabled/disabled/format-changed interrupt status, and endpoint fine-grain clock-gating reporting disable.
- `AZF0ENDPOINT7_*`: a full output endpoint register block. It includes converter audio-widget capabilities, converter format programming, channel/stream ID, digital-converter bits (`DIGEN`, validity, VCFG, pre-emphasis, copyright, non-audio, professional, level, category code, keepalive), stream formats, supported sample-size/rate capabilities, stripe control, ramp rate, GTC embedding and counter-delta limits, pin widget capabilities, pin capability bits, unsolicited response controls, pin sense, widget control, speaker/channel mapping, ACP data, audio descriptors 0 through 13, multichannel enable fields, lipsync, HBR, sink information, hot-plug/audio-enabled state, forced unsolicited response payload, configuration default fields, multichannel mode, IEC 60958 channel-status overrides, association info, output status, LPIB state, coding type, format-change signaling, wireless-display identification, remote keepalive, audio enable/disable/format-change interrupt status, and endpoint FGCG reporting disable.
- `AZF0INPUTENDPOINT0_*` through `AZF0INPUTENDPOINT5_*`: six complete input endpoint register blocks. Each block defines input-converter widget capabilities, input converter format, channel/stream ID, digital-converter fields, stream format/rate capability fields, input-pin widget capabilities, input-pin capabilities, unsolicited response control, input pin-sense response, widget control, multichannel enable and multichannel enable2 fields, HBR response, channel allocation, hot-plug control, forced unsolicited response payload, configuration default fields, LPIB snapshot/LPIB/timer snapshot, input status control, and received infoframe fields.
- `AZF0INPUTENDPOINT6_*`: the beginning of input endpoint 6. This chunk covers its converter widget capabilities, converter format, channel/stream ID, and most of the digital-converter control fields before the line range ends. The stream-format, supported-size/rate, and pin-side fields continue in the next chunk.

The register families are mechanically repeated per endpoint instance. Output endpoint 7 mirrors the same conceptual layout used by earlier output endpoints, and input endpoints 0 through 5 share the same field layout with only the endpoint instance number changing.

## Control Flow

This header has no runtime control flow. The effective runtime flow is in consumers:

1. DCN 3.6 display code includes `dcn_3_6_0_offset.h` and this `dcn_3_6_0_sh_mask.h` file.
2. Register-table macros token-paste register and field names into offset, shift, and mask tables for DCN 3.6 blocks.
3. AMDGPU display and audio-related paths use register helper macros such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` to access the Azalia endpoint MMIO fields described here.
4. Hardware and firmware consume the resulting register state to advertise codec capabilities, configure audio stream formats, route audio channels, handle hot-plug and unsolicited-response events, report pin/converter status, and synchronize audio buffer position snapshots.

The macros do not encode ordering rules. Consumers remain responsible for programming converter format before enabling a stream, aligning channel/stream IDs with the active display/audio pipe, using HBR and multichannel fields only when supported, coordinating hot-plug and audio enable state with display link state, and acknowledging or masking interrupt/status bits according to hardware semantics.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes hardware-visible DCN Azalia endpoint state:

- Converter capability and format state: audio channel capabilities, amplifier and format override support, stripe support, processing widget support, unsolicited-response capability, connection-list presence, digital/power-control/LR-swap support, widget delay, type, number of channels, bits per sample, sample-base divisor/multiple/rate, and stream type.
- Digital-converter state: digital enable, validity, validity configuration, pre-emphasis, copyright, non-audio/professional flags, level bit, category code, and keepalive.
- Stream capability state: supported stream formats, supported audio rates, and supported bit depths.
- Output pin state: pin widget capabilities, pin capability bits, unsolicited-response tag and enable, pin sense, widget enable/control, speaker allocation, ACP packet bytes, audio descriptor metadata, multichannel enable/mute/channel-ID fields, lipsync, HBR capability/enable, sink information, hot-plug clock-gating/audio-enable state, forced unsolicited-response payloads, configuration defaults, channel-status override bytes, association info, output-active status, LPIB snapshots, coding type, format-change state, wireless-display identification, remote keepalive, and audio interrupt status.
- Input pin state: input pin capabilities, pin sense, multichannel enable/mute/channel-ID fields, HBR, channel allocation, hot-plug/audio-enabled state, configuration default, input activity, channel layout, input activity and channel-layout/channel-status-infoframe unsolicited-response enables, and incoming audio infoframe channel count/allocation/valid fields.
- Endpoint interrupt/status state: audio enabled, audio disabled, and audio format changed flags, masks, and type bits for output endpoints; input endpoints expose input activity and infoframe-change signaling through their input status control fields.

Persistence is hardware-defined. Configuration fields generally remain until reprogrammed by modeset, hot-plug handling, audio stream setup, power-gating, suspend/resume, GPU reset, or ASIC reset paths. Status, snapshot, interrupt, and forced-response fields may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the endpoint block is powered and clocked. This generated shift/mask header does not identify those access semantics; the register specification and consuming driver code must supply them.

## Dependencies And Integration Points

The chunk depends on generated register naming staying synchronized across the DCN 3.6 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h` supplies the matching register offsets for the field names defined here.
- Other DCN 3.6 generated headers such as enum and default-value tables may provide symbolic values or reset expectations for the same Azalia fields.
- AMDGPU display resource, IRQ, DMUB, link, and audio/display integration code use the generated DCN 3.6 offset and mask headers through register helper tables.
- HDMI/DisplayPort audio flows depend on these fields indirectly when exposing an HDA codec to the OS, reporting sink capabilities from ELD/infoframe-like metadata, programming sample rate/word length/channel allocation, handling hot-plug audio enablement, and supporting HBR or multichannel playback/capture.
- Firmware and hardware integrations may rely on the same endpoint state for unsolicited responses, GTC timestamp embedding, LPIB snapshots, remote keepalive, and endpoint clock-gating behavior.

Important cross-file consistency is with the matching offset header. A field mask without the matching register offset, or an offset table entry paired with the wrong instance prefix, can compile in some macro paths but access the wrong endpoint or bitfield at runtime.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong mask or shift compiles cleanly and can corrupt neighboring MMIO fields, especially in dense format, channel ID, channel-status, and interrupt/status registers.
- The file is generated. Manual edits risk diverging from AMD's authoritative register database, companion offsets, firmware expectations, and silicon documentation.
- The line boundaries are artificial. This chunk begins after the start of `AZF0ENDPOINT6_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_1` and ends before the rest of `AZF0INPUTENDPOINT6`; complete endpoint analysis must merge adjacent chunks.
- Output and input endpoint blocks are highly repetitive. Generator drift or copy mistakes can affect one endpoint instance while leaving others correct, making endpoint-count and instance-index tests important.
- Audio format fields are user-visible. Incorrect `NUMBER_OF_CHANNELS`, `BITS_PER_SAMPLE`, sample-base divisor/multiple/rate, stream type, or stream ID masks can cause silent audio, wrong sample rate, channel swapping, or HBR/non-HBR negotiation failures.
- IEC 60958 channel-status override masks are interoperability-sensitive. Bad clock-accuracy, word-length, sampling-frequency, original-frequency, CGMS-A, or channel-number masks can confuse HDMI/DP receivers even when audio appears to play.
- Multichannel enable/mute/channel-ID fields are packed densely. Width or shift errors can enable the wrong channel, mute active channels, or route audio to the wrong logical position.
- Hot-plug, unsolicited-response, and audio enable/disable interrupt fields are side-effect-sensitive. Confusing status, mask, type, force, and ack-like bits can cause missed audio hot-plug notifications, stale codec state, interrupt storms, or absent OS-level audio devices.
- LPIB snapshot and timer fields are synchronization-sensitive. Incorrect masks can break audio-position reporting, leading to underruns, drift, or bad A/V sync diagnostics.
- Input endpoint infoframe and input-activity fields are stateful and timing-dependent. A mask error can hide input activity, report stale channel allocation, or mis-handle channel-layout/channel-status infoframe changes.
- Keepalive, remote keepalive, GTC embedding, and FGCG reporting fields can interact with power management and clock gating; bugs may show up only after idle, suspend/resume, remote-display, or link-power transitions.

## Test Signals

Useful validation combines generated-header checks with DCN 3.6 audio/display behavior:

- Build AMDGPU display support with DCN 3.6 enabled. Missing or renamed macros should surface in register-table construction or DCN 3.6 audio/display code that includes the generated headers.
- Mechanically compare this line range against AMD's authoritative DCN 3.6.0 register source and the matching `dcn_3_6_0_offset.h` names. The comparison should account for the chunk starting and ending in the middle of endpoint groups.
- Run static consistency checks that every complete register group has paired `__SHIFT` and `_MASK` definitions across adjacent chunks, and that repeated endpoint instances have expected field parity.
- Exercise HDMI and DisplayPort audio hot-plug, unplug, modeset, suspend/resume, GPU reset, and monitor power-cycle paths while checking that HDA codec nodes appear and disappear correctly.
- Validate audio playback across stereo, multichannel, HBR, multiple sample rates, multiple bit depths, and channel allocations on outputs that map to endpoint 7 and nearby endpoints.
- Validate input endpoint behavior, if supported by the platform path, for input activity detection, channel layout, channel allocation, infoframe valid changes, HBR capability/enablement, and LPIB snapshot reporting.
- Inspect kernel logs, audio diagnostics, and display diagnostics for missing codec devices, bad ELD/sink info, wrong channel maps, audio underruns, A/V sync drift, unexpected unsolicited responses, stuck audio enable/disable/format-change status, and resume-only failures.
- Use register dumps or tracepoints to confirm packed fields such as channel/stream IDs, multichannel enable groups, channel-status override bytes, hot-plug audio-enabled bits, and digital-converter keepalive bits land in the expected bit positions.

## Cross-Chunk Notes

The previous chunk contains the beginning of output endpoint 6, including the start of the channel-status override group whose tail appears here. The next chunk continues input endpoint 6 after the digital-converter control fields and then completes the remaining input endpoint namespace. The final per-file research document should merge these chunks before making whole-file claims about all DCN 3.6 Azalia endpoints or all generated shift/mask definitions.
