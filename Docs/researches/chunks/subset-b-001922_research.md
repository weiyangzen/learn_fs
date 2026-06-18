# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 61650-62727

## Purpose

This chunk is the end of the generated AMD DCN 3.1.6 shift/mask header. It contains no executable C logic; it publishes preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for Azalia F0 codec input endpoint registers. Consumers pair these constants with the matching DCN 3.1.6 offset header and AMD display register helpers to compose, update, or decode MMIO register fields.

The range starts mid-register in `AZF0INPUTENDPOINT3`, covering the remaining configuration-default masks plus the endpoint-3 LPIB, activity/status, and infoframe fields. It then defines complete repeated blocks for `AZF0INPUTENDPOINT4` through `AZF0INPUTENDPOINT7`, and ends the file with the final include-guard `#endif`. The chunk defines 962 preprocessor constants: 480 shift constants and 482 mask constants.

Although this source tree is rooted under `ceph-client`, this file is AMDGPU display hardware metadata, not distributed-filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, locks, allocation paths, includes, or direct register accesses in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the low bit index of a hardware field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for isolating or updating that field.
- `// addressBlock: azf0inputendpointN_inputendpointind`: generated grouping comments for indexed Azalia input endpoint instances.

The covered register groups are:

- `AZF0INPUTENDPOINT3_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`: the tail masks for `MISC`, `COLOR`, `CONNECTION_TYPE`, `DEFAULT_DEVICE`, `LOCATION`, and `PORT_CONNECTIVITY`.
- `AZF0INPUTENDPOINT3` runtime input-pin controls: `LPIB_SNAPSHOT_CONTROL`, `LPIB`, `LPIB_TIMER_SNAPSHOT`, `INPUT_STATUS_CONTROL`, and `INFOFRAME`.
- `AZF0INPUTENDPOINT4` through `AZF0INPUTENDPOINT7`: complete input endpoint blocks, each with converter debug, converter audio-widget capabilities, converter format, channel/stream ID, digital-converter control, supported stream formats/rates, pin widget capabilities, pin capabilities, unsolicited response control, input-pin sense, widget input enable, multichannel controls, HBR, channel allocation, hot-plug/audio control, forced unsolicited response, default configuration, LPIB snapshot/value/timer, input status, and infoframe fields.

Representative fields include:

- Audio capability fields: channel capability, amplifier presence, format override, stripe, processing widget, unsolicited response capability, connection list, digital, power control, LR swap, delay, and widget type.
- Converter programming fields: number of channels, bits per sample, sample base divisor/multiple/rate, stream type, channel ID, stream ID, digital enable, validity/configuration flags, pre-emphasis, copyright, non-audio, professional mode, category code, and keepalive.
- Pin capability and control fields: impedance sense, trigger required, jack detection, input/output capability, HDMI/DP flags, VREF, EAPD, input enable, HBR capability/enable, channel allocation, clock gating disable, clock-on state, and audio enabled.
- Multichannel routing fields: `MULTICHANNEL0` through `MULTICHANNEL7` enable, mute, and channel-ID fields split across `MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2`.
- Event/status fields: unsolicited response tag/enable/force payload, input activity, channel layout, input-activity unsolicited-response enable, channel-layout/channel-status infoframe-change unsolicited-response enable, and infoframe channel count/allocation/byte 5/valid.
- Audio-position snapshot fields: LPIB snapshot lock, cyclic buffer wrap count, full-width LPIB value, and full-width LPIB timer snapshot.

## Control Flow

This header chunk has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h`, then uses token-pasting helper macros such as field/mask/shift table builders to bind symbolic register fields to per-ASIC register tables.

For the Azalia input endpoint fields represented here, the expected runtime sequence is outside the header:

1. DCN 3.1.6 display/audio code selects an Azalia endpoint register or indexed endpoint aperture.
2. The matching offset macro provides the register address or index/data aperture.
3. The shift/mask macro from this header isolates or updates a specific field.
4. Higher-level audio code sequences stream format, pin state, hotplug/audio enablement, infoframe programming, multichannel/HBR setup, LPIB snapshot reads, and unsolicited-response handling.

The generated constants do not encode ordering, access type, volatility, or side effects. Callers must still obey the hardware sequence for active display audio streams, hotplug changes, power-gating transitions, suspend/resume, reset, and snapshot locking.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to memory, disk, or firmware. It describes MMIO-backed GPU state in DCN 3.1.6 Azalia input endpoint hardware.

The represented hardware state includes:

- Static or advertised capabilities for input converter and pin widgets.
- Active converter state such as sample format, stream/channel ID, digital converter flags, and supported rate/size masks.
- Pin state for input enablement, HDMI/DP capability, jack/presence/impedance sense, HBR, multichannel routing, channel allocation, clock gating, audio enabled, and default configuration metadata.
- Event and status state for unsolicited responses, input activity, channel layout, infoframe changes, and infoframe validity.
- Position/timer observations through LPIB snapshot lock, cyclic-buffer wrap count, LPIB, and LPIB timer snapshot fields.

Persistence is hardware-defined. Programmed configuration usually lasts until stream reconfiguration, modeset, power gating, suspend/resume, or ASIC reset. Sense/status/unsolicited-response/LPIB fields may be read-only, sticky, latched, timing-sensitive, self-clearing, or write-one-to-clear depending on the register definition outside this generated mask file.

## Dependencies And Integration Points

This chunk must remain synchronized with the rest of the DCN 3.1.6 generated register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h` supplies the matching register offsets and base-index macros.
- DCN base segment definitions in DCN316 display code turn generated offsets into MMIO addresses.
- AMD display register helpers use token-pasted register and field names to retrieve masks and shifts.

Observed include sites for `dcn_3_1_6_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`, which builds the DCN316 DMUB register mask/shift tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which builds DCN316 resource objects and register tables, including DIO/audio-related structures.

Relevant runtime integration is with the shared AMD display audio path under `display/dc/dce/dce_audio.c` and `display/dc/dce/dce_audio.h`. That code programs Azalia codec endpoint index/data registers, hot-plug audio control, HBR, speaker/channel information, sink information, supported formats/rates, and default configuration. This chunk's `AZF0INPUTENDPOINT*` names describe the generated input-endpoint field geometry for endpoint instances 3 through 7; the standard audio code may reach related hardware through generic indexed endpoint access rather than spelling these generated macro names directly.

## Risks And Edge Cases

- Field drift is the main risk. These macros are untyped constants, so an incorrect bit position or mask can compile cleanly while programming or decoding the wrong hardware bits.
- The chunk starts in the middle of `AZF0INPUTENDPOINT3`. Adjacent chunk `subset-b-001921` is required for complete endpoint-3 analysis.
- The complete endpoint blocks for 4 through 7 are repetitive and instance-specific. A copy-generation error in one endpoint can affect only one physical/logical audio path, making failures connector- or routing-dependent.
- Audio format fields are user-visible. Bad masks for sample size/rate, stream type, channel count, stream ID, or channel ID can cause silence, distorted audio, wrong channel mapping, or failures limited to multichannel/HBR modes.
- Digital converter flags affect validity, non-audio/professional/copyright metadata, category code, and keepalive behavior. Misprogramming can break sink interpretation or audio continuity during blanking/idle periods.
- Hotplug, unsolicited response, input activity, and infoframe-change fields are event-sensitive. Incorrect masks can cause missed notifications, spurious events, stuck status, or resume-only audio failures.
- LPIB snapshot fields are timing-sensitive. Misinterpreting lock, wrap count, LPIB, or timer snapshot fields can produce wrong audio position accounting or races while a stream is active.
- The final `#endif` is in this range. Accidental edits at the tail can break the entire generated header's include guard and fail all DCN316 users.

## Test Signals

Useful validation should combine generated-header checks with display/audio behavior:

- Build AMDGPU display code with DCN316 enabled. Include or token-paste mismatches should surface in `dmub_dcn316.c`, `dcn316_resource.c`, or shared register-table helpers.
- Mechanically verify that every field in endpoint blocks 4 through 7 has the expected `__SHIFT`/`_MASK` pair where the generated schema requires both, and that full-register fields such as LPIB use `0xFFFFFFFFL` masks.
- Diff the endpoint 4 through 7 layouts against neighboring generated DCN headers or AMD's authoritative register database where compatibility is expected.
- Exercise HDMI/DP audio on DCN316 hardware across stereo, multichannel PCM, multiple sample rates and bit depths, HBR-capable formats, stream start/stop, plug/unplug, blanking, modeset, suspend, and resume.
- Watch for no-sound-on-one-endpoint bugs, channel swaps, incorrect channel allocation, hotplug notification storms, missed audio endpoint changes, stuck activity/status bits, invalid infoframe state, LPIB position anomalies, and audio regressions after resume.

## Cross-Chunk Notes

This is chunk 26 of 26 for `dcn_3_1_6_sh_mask.h`. Earlier chunks cover the beginning of the generated header and the earlier Azalia endpoint blocks. The final per-file report should merge this tail with `subset-b-001921` before making complete claims about `AZF0INPUTENDPOINT3`, and with all earlier chunks before summarizing the whole DCN 3.1.6 shift/mask namespace.
