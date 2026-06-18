# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 56953-59328

## Scope

This chunk is generated AMD DCN 3.1.6 register field metadata. It contains C preprocessor constants only: paired `__SHIFT` and `_MASK` macros for Azalia/HDA display-audio codec endpoint indexed registers. There are no functions, structs, enums, branches, loops, allocations, includes, or software-owned variables in this range.

The reviewed span contains 2,046 `#define` entries: 1,041 shift definitions and 1,005 mask definitions. The mismatch is from chunk boundaries. The range begins after the first endpoint-1 `ACP_DATA` masks and starts at `ACP_TYPE_DEPENDENT_BYTE1__SHIFT`, then continues through endpoint-1 descriptor and pin-control status fields. It covers complete output endpoint blocks 2, 3, and 4. It then covers the beginning and most of output endpoint 5 through the first mask in `AZF0ENDPOINT5_AZALIA_F0_CODEC_PIN_CONTROL_SINK_INFO4`; the remaining sink-info masks and later endpoint-5 fields are in the next chunk.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU Display Core hardware metadata, not distributed filesystem code.

## Purpose

The header supplies DCN 3.1.6 bit layouts for Azalia F0 display-audio codec endpoint registers. The companion `dcn_3_1_6_offset.h` header supplies the matching indexed register numbers and endpoint index/data apertures, for example `regAZF0ENDPOINT2_AZALIA_F0_CODEC_ENDPOINT_INDEX`, `regAZF0ENDPOINT2_AZALIA_F0_CODEC_ENDPOINT_DATA`, and `ixAZF0ENDPOINT2_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR0`. This shift/mask file supplies the field positions used by AMD display register helpers to pack writes and decode readbacks.

The hardware surface in this chunk is the repeated output endpoint namespace for HDMI/DisplayPort audio. These endpoint registers represent HDA/Azalia converter and pin widgets attached to display outputs. Runtime display-audio code can program stream format, stream/channel IDs, digital audio status, supported formats, sink ELD data, HBR support, multichannel routing, unsolicited responses, LPIB snapshots, and audio status interrupts without hard-coding numeric bit positions.

## Important Definitions

The exported API is the generated macro naming convention:

- `AZF0ENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT` gives the field low bit.
- `AZF0ENDPOINT<n>_<REGISTER>__<FIELD>_MASK` gives the raw 32-bit field mask.
- `//AZF0ENDPOINT...` comments group field macros by indexed Azalia register.
- `// addressBlock: azf0endpoint<n>_endpointind` marks the repeated endpoint register block.

Endpoint 1 coverage starts mid-pin-control block and includes:

- `CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`: per-audio-format descriptor fields. Descriptor 0 has max channels, supported frequencies, descriptor byte 2, and stereo supported frequencies; descriptors 1-13 have max channels, supported frequencies, and descriptor byte 2.
- `CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2`: enable, mute, and channel-ID fields for channel pairs or single-channel mappings across channels 0-7.
- `RESPONSE_LIPSYNC`, `RESPONSE_HBR`, and `SINK_INFO0` through `SINK_INFO8`: audio/video latency, HBR capability/enable, manufacturer/product ID, port ID, and sink description/latency bytes.
- `HOT_PLUG_CONTROL`, `UNSOLICITED_RESPONSE_FORCE`, `RESPONSE_CONFIGURATION_DEFAULT`, `MULTICHANNEL_MODE`, channel-status override registers `CODEC_CS_OVERRIDE_0` through `_8`, `ASSOCIATION_INFO`, `DIGITAL_OUTPUT_STATUS`, `LPIB` snapshot/readback, coding type, format-changed, wireless-display identification, remote keepalive, audio-enable status, and audio enabled/disabled/format-changed interrupt status fields.

Endpoints 2, 3, and 4 are complete repeated output endpoint blocks. Each includes:

- `CODEC_CONVERTER_PIN_DEBUG`: a generated debug field.
- `CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: converter widget properties including channel capability, input/output amplifier presence, amplifier/format override support, stripe support, processing-widget support, unsolicited-response capability, connection-list, digital, power-control, left/right swap, delay, and widget type.
- `CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT`: number of channels, bits per sample, sample base divisor, sample base multiple, base rate, and stream type.
- `CODEC_CONVERTER_CONTROL_CHANNEL_STREAM_ID`: converter channel ID and stream ID.
- `CODEC_CONVERTER_CONTROL_DIGITAL_CONVERTER`: digital audio enable and IEC 60958-style status/control bits such as validity, VCFG, pre-emphasis, copyright, non-audio, professional mode, level, category code, and keepalive.
- `CODEC_CONVERTER_PARAMETER_STREAM_FORMATS` and `PARAMETER_SUPPORTED_SIZE_RATES`: supported stream formats, audio rate capabilities, and audio bit capabilities.
- `CODEC_CONVERTER_STRIPE_CONTROL`, `CONTROL_RAMP_RATE`, `CONTROL_GTC_EMBEDDING`, `CONTROL_GTC_OFFSET_DEBUG`, and `GTC_COUNTER_DELTA*`: converter striping, ramp, presentation-time/GTC embedding, offset debug, and min/current/max GTC delta readback fields.
- `CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `CODEC_PIN_PARAMETER_CAPABILITIES`: pin widget capability fields such as impedance sense, trigger requirement, jack detection, headphone drive, output/input capability, balanced pins, HDMI, DP, VREF, and EAPD.
- `CODEC_PIN_CONTROL_UNSOLICITED_RESPONSE`, `RESPONSE_PIN_SENSE`, `WIDGET_CONTROL`, `CHANNEL_SPEAKER`, `ACP_DATA`, `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, multichannel controls, lipsync, HBR, sink info, hotplug, default configuration, channel-status override, LPIB, format-change, remote keepalive, audio enable status, and audio interrupt status fields.

Endpoint 5 coverage starts at its address block and continues through `CODEC_PIN_CONTROL_SINK_INFO4`. It has the same converter and pin-control structure as endpoints 2-4 up to the partial sink-info boundary.

## APIs, Types, And Functions

There are no C functions or types declared by this chunk. The important interface is the macro namespace itself. Callers normally consume these symbols through AMD Display Core register helper macros and generated field tables rather than using the numeric values directly.

Related semantic enum names live outside this chunk, for example in `include/soc24_enum.h`, which defines values for fields such as `AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_MODE_MULTICHANNEL_MODE`, `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_HBR_HBR_CAPABLE`, and several audio-widget or pin-capability booleans. Older DCE audio programming code uses the same descriptor field shape when it maps EDID SAD entries to `AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR0` fields and writes endpoint registers via audio endpoint helpers.

## Control Flow

This header has no executable control flow. Runtime sequencing is supplied by AMDGPU/DC code that includes `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h`, builds register/field tables, then uses MMIO or indexed-register helpers to read, update, or acknowledge fields.

The implied control flow for consumers is:

1. Select the output audio endpoint for a display pipe or connector.
2. Use the companion offset header to address the endpoint index/data aperture and the specific `ixAZF0ENDPOINT<n>_*` register.
3. Use these shift/mask macros to compose a read-modify-write, status read, or interrupt acknowledge operation.
4. Let hardware latch converter format, stream ID, sink data, channel mapping, hotplug/audio enable, or interrupt state according to the Azalia/HDA register protocol.

The macros do not encode HDA verb ordering, stream disable/enable sequencing, ELD update timing, hotplug timing, write-one-to-clear behavior, or read-only versus writable status. Functional code and hardware documentation must supply those rules.

## State And Persistence Behavior

This chunk persists no software state. It describes hardware state held in DCN 3.1.6 display-audio endpoint registers.

Configuration-like fields include converter format, channel/stream ID, digital converter control, supported format/rate advertisement, stripe and GTC embedding control, pin output enable, speaker and channel allocation, ACP packet data, audio descriptors, multichannel enable/mute/channel mapping, HBR enable, hotplug audio enable, unsolicited-response enable/tag, default pin configuration, channel-status override bytes, wireless display identification, and remote keepalive.

Readback/status fields include converter and pin capabilities, stream format support, pin sense/impedance, sink information/ELD bytes, lipsync latency, HBR capability, digital output status, LPIB and timer snapshots, format-changed status, audio enabled state, and audio enabled/disabled/format-changed interrupt state.

Several fields are side-effecting or sticky in typical hardware use: interrupt acknowledge bits, interrupt masks and polarities, forced unsolicited-response trigger, LPIB snapshot lock, GTC delta clear, audio hotplug enable, audio keepalive, and format-change/audio-enable status. The generated masks do not mark those semantics; they only identify the bit positions.

## Dependencies And Integration Points

This chunk must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`. The offset header defines the endpoint index/data apertures and indexed register IDs, while this file defines bit layouts. A missing macro name usually fails compilation; a wrong numeric mask or shift can compile and silently program or decode the wrong hardware bits.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`, which includes the DCN316 offset and shift/mask headers for DMUB register metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes the same generated headers while constructing DCN316 display resources.

Functional integration is mostly indirect through Display Core audio, stream encoder, resource, IRQ, and DMUB register tables. HDMI/DP audio paths use these endpoint fields to populate monitor audio capabilities from EDID/ELD/SAD data, select stream IDs and formats, enable or disable audio on hotplug, route multichannel audio, enable HBR or encoded audio, service audio format-change and audio enable/disable interrupts, and expose link-position or timing readbacks such as LPIB/GTC information.

## Risks And Edge Cases

- This is generated hardware metadata. Manual edits risk divergence from the authoritative DCN 3.1.6 register database and from sibling offset/default/enum headers.
- The chunk begins and ends inside register groups. Endpoint 1 `ACP_DATA` starts before this range, and endpoint 5 `SINK_INFO4` continues after line 59328. Whole-file conclusions must merge adjacent chunks.
- Endpoint blocks are highly repetitive. A generator or copy error in only one endpoint can compile but fail only on connectors routed through that endpoint.
- Output endpoint names are instance-specific. Accidentally using `AZF0ENDPOINT3_*` masks for endpoint 4, or using generic/non-DCN masks from an older ASIC generation, can target valid-looking but wrong hardware fields.
- Dense channel-mapping registers pack enable, mute, and channel ID fields into adjacent nibbles and bytes. Wrong shifts can cause muted, swapped, or missing channels.
- Descriptor and sink-info fields are protocol-facing. Bad masks can advertise the wrong sample rates, channel count, speaker allocation, HBR capability, HDMI/DP connection type, sink identity, or latency to higher-level audio logic.
- Interrupt fields combine status, mask, ack, and polarity concepts. Treating acknowledge bits like persistent state can clear events unexpectedly; failing to preserve mask or polarity bits can break audio hotplug or format-change notification.
- Some capability and status fields are likely read-only or hardware-owned. The presence of a mask does not imply a caller should write the field.

## Test Signals

Useful validation signals for this chunk are mostly build, generation, and hardware integration checks:

- Compile AMDGPU Display Core with DCN316 enabled, including DMUB and DCN316 resource paths, to catch missing or malformed macro names.
- Regenerate or mechanically compare `dcn_3_1_6_sh_mask.h` against the authoritative DCN 3.1.6 register database and verify consistency with `dcn_3_1_6_offset.h`.
- Check paired `__SHIFT` and `_MASK` definitions for complete endpoint 2-4 register groups, while allowing known boundary exceptions at endpoint 1 start and endpoint 5 end.
- Preprocess representative DC register field-table macros to confirm token pasting resolves to the intended `AZF0ENDPOINT<n>` symbols for DCN316.
- Run HDMI/DisplayPort audio validation on DCN316 hardware for endpoints routed through output endpoints 1-5: hotplug, modeset, audio enable/disable, PCM playback, sample-rate changes, multichannel playback, channel allocation, encoded/HBR audio where supported, and suspend/resume.
- Validate ELD/SAD-derived sink data by comparing programmed audio descriptors, speaker allocation, latency, manufacturer/product IDs, port IDs, HBR capability, and sink-description bytes against known-good EDID/ELD data.
- Exercise audio enabled, audio disabled, format-changed, and unsolicited-response interrupt paths and verify status, mask, polarity, and ack bits behave as expected.
- Use register dumps around audio setup to confirm read-modify-write operations affect only intended masked bits in dense registers such as multichannel enable, channel-status override, hotplug control, and interrupt status/control.

## Cross-Chunk Notes

The previous chunk owns the beginning of endpoint 1, including the rest of `CODEC_PIN_CONTROL_ACP_DATA`. The next chunk owns the rest of endpoint 5 after `SINK_INFO4`, including later sink-info, hotplug, channel-status override, LPIB, remote keepalive, and audio interrupt fields if the generated layout continues like endpoints 2-4. The final per-file research document should reconcile these boundaries before presenting complete endpoint coverage for DCN 3.1.6.
