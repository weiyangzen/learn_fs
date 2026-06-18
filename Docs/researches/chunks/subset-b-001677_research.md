# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 51899-54266

## Scope

This chunk is part of AMDGPU's generated DCN 2.1.0 register shift/mask header. It contains preprocessor constants only: no functions, structs, enums, storage objects, or executable control flow. The exported surface is the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macro pairs used by AMD display register helpers to encode and decode fields in DCN 2.1 Azalia/HDA display-audio endpoint registers.

The range covers 2,368 source lines with 2,048 `#define` entries: 1,025 shift constants and 1,023 mask constants. It starts in the middle of the `AZF0ENDPOINT3` output endpoint block, fully covers output endpoints 4, 5, and 6, and ends in the early audio-descriptor portion of output endpoint 7. The repeated endpoint model is visible through the `addressBlock: azf0endpoint4_endpointind`, `azf0endpoint5_endpointind`, `azf0endpoint6_endpointind`, and `azf0endpoint7_endpointind` comments.

## Purpose

This header chunk describes bit layouts for DCN 2.1 display audio output endpoint registers. The endpoint names use AMD's `AZF0ENDPOINTn_AZALIA_F0_*` convention, where each endpoint is an indexed HDA/Azalia codec endpoint used for HDMI/DisplayPort audio exposure and control.

The covered register families provide field positions and masks for:

- Converter stream binding, including channel ID, stream ID, converter sample format, stream type, and advertised stream formats/rates.
- Digital converter state, including digital enable, valid/config/pre-emphasis/copyright/non-audio/professional/channel-status category fields, generation level, and keepalive.
- Audio stream synchronization support, including stripe control, ramp rate, Global Time Counter embedding controls, and GTC delta/min/max readback fields.
- Pin capability and control state, including HDA widget capabilities, pin capabilities, unsolicited response tags, pin sense, output enable, channel/speaker allocation, and HDMI/DP connection indicators.
- Short audio descriptor storage, with descriptor registers 0 through 13 for full endpoint blocks and descriptor 0 through 7 for the partial endpoint 7 tail in this chunk.
- Multichannel routing and mute/channel-ID assignment through `MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2`.
- Sink/ELD-style metadata, including manufacturer/product IDs, sink description length, port IDs, and 18 bytes of sink description spread across `SINK_INFO4` through `SINK_INFO8`.
- Hot-plug audio enablement, forced unsolicited responses, default pin configuration, channel-status override words, LPIB snapshots, coding type, format-change response, wireless display identification, remote keepalive, and audio enable/disable/format-change interrupt status.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The interface is the macro namespace and the guarantee that consumers can paste a register name and field name into AMD register helper macros.

Key conventions:

- `*_SHIFT` gives the low bit position for a field.
- `*_MASK` gives the already-shifted bit mask for that field.
- Register-heading comments such as `//AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL` group the field macros belonging to one generated register.
- Address-block comments identify indexed endpoint register windows, not C scopes.

Representative converter groups include `AZF0ENDPOINTn_AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `...CONVERTER_CONTROL_CONVERTER_FORMAT`, `...CONVERTER_CONTROL_CHANNEL_STREAM_ID`, `...CONVERTER_CONTROL_DIGITAL_CONVERTER`, `...PARAMETER_STREAM_FORMATS`, `...PARAMETER_SUPPORTED_SIZE_RATES`, `...STRIPE_CONTROL`, `...CONTROL_RAMP_RATE`, `...CONTROL_GTC_EMBEDDING`, and `...GTC_COUNTER_DELTA*`.

Representative pin groups include `AZF0ENDPOINTn_AZALIA_F0_CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `...PIN_PARAMETER_CAPABILITIES`, `...PIN_CONTROL_UNSOLICITED_RESPONSE`, `...RESPONSE_PIN_SENSE`, `...WIDGET_CONTROL`, `...CHANNEL_SPEAKER`, `...AUDIO_DESCRIPTOR0` through `...AUDIO_DESCRIPTOR13`, `...MULTICHANNEL_ENABLE`, `...RESPONSE_LIPSYNC`, `...RESPONSE_HBR`, `...SINK_INFO0` through `...SINK_INFO8`, `...HOT_PLUG_CONTROL`, `...UNSOLICITED_RESPONSE_FORCE`, `...RESPONSE_CONFIGURATION_DEFAULT`, and `...MULTICHANNEL_ENABLE2`.

Endpoint bookkeeping and interrupt/status groups include `...PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8`, `...CODEC_PIN_ASSOCIATION_INFO`, `...DIGITAL_OUTPUT_STATUS`, `...LPIB_SNAPSHOT_CONTROL`, `...LPIB`, `...LPIB_TIMER_SNAPSHOT`, `...CODING_TYPE`, `...FORMAT_CHANGED`, `...WIRELESS_DISPLAY_IDENTIFICATION`, `...REMOTE_KEEPALIVE`, `...AUDIO_ENABLE_STATUS`, `...AUDIO_ENABLED_INT_STATUS`, `...AUDIO_DISABLED_INT_STATUS`, and `...AUDIO_FORMAT_CHANGED_INT_STATUS`.

## Control Flow

This chunk has no local control flow. Runtime control flow appears in consumers that include the matching DCN 2.1 offset and shift/mask headers, build register-field tables, and access MMIO or indexed Azalia registers through AMD display helper macros.

A typical path is:

1. DCN21 resource, IRQ, GPIO, DMUB, or audio-related display code includes `dcn_2_1_0_offset.h` and `dcn_2_1_0_sh_mask.h`.
2. Generation-specific tables are assembled with macro expansion helpers such as register/field initializers and mask/shift lists.
3. Runtime code programs endpoint registers during display audio setup, hotplug processing, modeset, audio stream changes, interrupt handling, suspend/resume, or DMUB-assisted flows.
4. Register helpers use the `_MASK` and `__SHIFT` constants to preserve unrelated bits while setting or extracting individual fields.

The control-sensitive hardware flows represented here are endpoint-to-stream assignment, converter format programming, digital converter enable/metadata programming, HDMI/DP sink audio descriptor propagation, multichannel channel mapping, hot-plug audio enablement, forced unsolicited response generation, channel-status override programming, LPIB snapshot capture, audio coding/format-change tracking, and audio enable/disable/format-change interrupt reporting.

The macros do not encode sequencing, access permissions, volatile status behavior, write-one-to-clear semantics, self-clearing behavior, or required clock/power state. Callers must supply those semantics from the register programming model and the surrounding DC/audio code.

## State And Persistence Behavior

The file itself stores no software state and performs no persistence. It describes hardware register state whose lifetime is controlled by the DCN 2.1 display-audio block, driver programming, hotplug/modeset activity, power management, and GPU reset.

State represented in this chunk includes:

- Converter configuration: channel and stream IDs, sample size/rate encoding, stream type, supported stream formats/rates, stripe/ramp settings, and GTC presentation-time embedding state.
- Digital audio metadata: enable/valid/configuration bits, pre-emphasis, copyright and non-audio flags, professional mode, category code, level, and remote/stream keepalive state.
- Pin and sink state: pin capabilities, pin sense, output-enable state, channel/speaker allocation, HDMI/DP connection markers, descriptor payloads, lipsync/HBR response fields, ELD-like sink information, and default pin configuration.
- Routing state: multichannel enable, mute, and channel-ID fields for paired even channels in `MULTICHANNEL_ENABLE` and odd channels in `MULTICHANNEL_ENABLE2`.
- Position and status state: LPIB snapshot controls, snapshot values, timer snapshots, coding type, format-change response, wireless display identification, digital output status, endpoint association, and audio enablement status.
- Interrupt state: audio enabled, audio disabled, and audio format changed flag/mask/type fields for each complete endpoint block in the range.

Some of these fields are capability constants, some are writable configuration latches, some are live status readbacks, and some are interrupt status or masking controls. Misprogrammed values can persist until the next audio reconfiguration, hotplug event, modeset, suspend/resume reinitialization, or full GPU reset.

## Dependencies And Integration Points

The direct companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`, which supplies the matching register addresses and indexed endpoint offsets. This chunk supplies the bit layout within those registers.

Visible include sites for the DCN 2.1.0 offset and shift/mask headers in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, where DCN21 resource construction wires generation-specific display, link, audio, GPIO, and IRQ register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`, where generated masks feed interrupt source definitions and status/ack handling.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c` and `.../hw_translate_dcn21.c`, which include the same generated namespace for DCN21 GPIO object creation and translation.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`, where DCN21 DMUB support uses generation-specific register definitions.

The display-audio endpoint constants integrate with the common AMD display audio path that programs HDMI/DP audio capabilities, stream formats, sink descriptors, channel allocation, HBR state, and endpoint interrupts. Although the repository prefix is `distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata and has no Ceph filesystem or distributed-storage behavior.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A bad mask or shift compiles cleanly, but register helpers may update the wrong bits, truncate a value, fail to preserve neighboring fields, or misread status.

Endpoint repetition creates copy/generation hazards. Endpoint 4, 5, and 6 are full repeated blocks and should be structurally aligned. Endpoint 3 starts mid-block because earlier endpoint 3 definitions live in the previous chunk. Endpoint 7 is incomplete in this chunk and continues in the next chunk after `AUDIO_DESCRIPTOR7`. Merge/reconciliation should avoid treating those chunk boundaries as hardware boundaries.

Audio protocol behavior is sensitive to these constants. Errors in converter format, stream ID, supported rates, digital converter metadata, pin capabilities, audio descriptors, HBR, channel allocation, sink info, or channel-status override fields can lead to missing HDMI/DP audio, wrong sample rate/channel exposure, incorrect non-PCM handling, bad IEC 60958 metadata, or endpoint-specific failures after hotplug.

Interrupt/status fields are also sensitive. `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS` combine flag, mask, and type fields. Incorrect field definitions can leave interrupts stuck, masked, unacknowledged, or attributed to the wrong endpoint. Forced unsolicited-response fields can also create misleading HDA codec events if payload and force bits are mishandled.

LPIB and GTC fields cross timing and presentation domains. Wrong snapshot, timer, or GTC embedding masks can break audio position reporting or presentation-time correlation in ways that appear as drift, stale position reads, or format-change glitches rather than obvious register failures.

## Test Signals

Useful validation signals are a mix of generated-header consistency checks and DCN21 display-audio behavior:

- Build coverage for DCN21 resource, IRQ, GPIO, DMUB, and display audio paths that include `dcn_2_1_0_sh_mask.h`.
- Generated-register validation that every field in this chunk has a matching register definition in `dcn_2_1_0_offset.h`, and that each mask is consistent with its shift and field width.
- Structural comparison across `AZF0ENDPOINT4`, `AZF0ENDPOINT5`, and `AZF0ENDPOINT6`, with special handling for the partial `AZF0ENDPOINT3` and `AZF0ENDPOINT7` chunk boundaries.
- HDMI and DisplayPort audio tests for endpoint stream binding, PCM and non-PCM formats, sample-rate changes, multichannel layouts, channel allocation, HBR, descriptor updates, and channel-status override behavior.
- Hotplug and modeset tests that verify audio enablement, ELD/sink-info propagation, unsolicited response behavior, and audio recovery after disconnect/reconnect and suspend/resume.
- Interrupt tests that confirm audio enabled, audio disabled, and audio format changed events report, mask, clear, and route correctly per endpoint.
- LPIB/GTC sanity checks during playback that confirm snapshot locks, LPIB values, timer snapshots, and presentation-time delta fields move plausibly and do not regress across format changes.

Regression symptoms from bad constants include no HDMI/DP audio, wrong channel count or sample rate, missing or stale sink descriptions, broken HBR/non-PCM playback, incorrect channel-status metadata, audio disappearing after hotplug, stuck audio interrupts, or endpoint-specific failures that only affect one generated `AZF0ENDPOINTn` instance.

## Cross-Chunk Notes

This is chunk 22 of 24 for `dcn_2_1_0_sh_mask.h`. The previous chunk contains the beginning of `AZF0ENDPOINT3`, and the next chunk continues `AZF0ENDPOINT7` after `AUDIO_DESCRIPTOR7`. The final per-file research document should merge these slices into the full generated DCN 2.1 register-layout contract and should not infer architectural boundaries from this artificial line range.
