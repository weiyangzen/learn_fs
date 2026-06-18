# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 57718-60079

## Scope

This chunk is generated AMD DCN 3.1.5 display register field metadata. It contains C preprocessor constants only: paired `__SHIFT` and `_MASK` macros for fields inside Azalia/HDA display-audio indexed registers, plus generated register and address-block comments. There are no functions, structs, enums, branches, loops, allocations, includes, or software-owned state in this range.

The reviewed span contains 2,041 `#define` entries: 1,041 shift definitions and 1,012 mask definitions. The mismatch is caused by chunk boundaries: the range begins in the middle of `AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_PARAMETER_CAPABILITIES`, so some endpoint-4 shifts precede their masks in this chunk, and it ends inside `AZF0INPUTENDPOINT1_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, before the rest of that input endpoint block.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU Display Core hardware metadata rather than distributed filesystem code.

## Purpose And Hardware Surface

The purpose of this header slice is to describe bit layouts for DCN 3.1.5 Azalia F0 display-audio codec endpoint registers. The companion `dcn_3_1_5_offset.h` header supplies register/index addresses such as the `ixAZF0ENDPOINT<n>_*` and `ixAZF0INPUTENDPOINT<n>_*` names; this file supplies the masks and shifts used by AMD display register helpers to pack writes and decode readbacks.

The hardware surface covered here is the repeated HDA/Azalia endpoint namespace:

- The tail of output endpoint 4, starting at pin parameter capabilities and covering pin control, audio descriptors, multichannel controls, sink information, hotplug, channel-status overrides, LPIB snapshots, coding/format status, keepalive, audio-enable status, and interrupt-status fields.
- Complete output endpoint blocks 5, 6, and 7, each containing converter capability/control fields and the same pin-control/status layout used for display audio over HDMI/DisplayPort sinks.
- The complete input endpoint 0 block, including input converter controls, input pin capabilities, input multichannel routing, HBR, hotplug/audio-enable, LPIB snapshots, input activity/status, and audio infoframe readback.
- The beginning of input endpoint 1, through the input converter audio-widget capability fields.

The field layouts let higher-level display-audio code treat endpoint instances uniformly while still targeting endpoint-specific generated macro names.

## Important Definitions

The exported API is the generated macro naming convention:

- `AZF0ENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT` gives the low-bit position for a field in output endpoint `n`.
- `AZF0ENDPOINT<n>_<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- `AZF0INPUTENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT` and `_MASK` do the same for input endpoint `n`.
- `//AZF0ENDPOINT...` comments group field macros by generated register name.
- `// addressBlock: azf0endpoint<n>_endpointind` and `// addressBlock: azf0inputendpoint<n>_inputendpointind` mark the indexed endpoint register aperture.

Important output endpoint families in this range:

- `CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` reports converter widget properties: channel capability, input/output amplifier presence, override support, stripe/processing flags, unsolicited response capability, connection-list, digital, power-control, left/right swap, delay, and widget type.
- `CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT` packs channel count, bits per sample, sample base divisor/multiple/rate, and stream type.
- `CODEC_CONVERTER_CONTROL_CHANNEL_STREAM_ID` maps channel ID and stream ID into the converter.
- `CODEC_CONVERTER_CONTROL_DIGITAL_CONVERTER` contains digital audio status/control bits such as enable, V, VCFG, pre-emphasis, copyright, non-audio, professional, level, category code, generation level, and copy-protection level.
- `CODEC_CONVERTER_PARAMETER_STREAM_FORMATS` and `PARAMETER_SUPPORTED_SIZE_RATES` expose supported PCM/non-PCM formats, sample sizes, and sample rates.
- `CODEC_CONVERTER_STRIPE_CONTROL`, `CONTROL_RAMP_RATE`, `CONTROL_GTC_EMBEDDING`, `GTC_COUNTER_DELTA`, `GTC_COUNTER_DELTA_MIN`, and `GTC_COUNTER_DELTA_MAX` define converter striping, ramp, and global time counter embedding/readback fields.
- `CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `CODEC_PIN_PARAMETER_CAPABILITIES` describe the endpoint pin widget, including impedance sense, jack detection, output/input capability, HDMI, DP, VREF, EAPD, and related capability bits.
- `CODEC_PIN_CONTROL_UNSOLICITED_RESPONSE` and `UNSOLICITED_RESPONSE_FORCE` define unsolicited-response tag/enable and forced payload/trigger fields.
- `CODEC_PIN_CONTROL_RESPONSE_PIN_SENSE`, `WIDGET_CONTROL`, `CHANNEL_SPEAKER`, `ACP_DATA`, `RESPONSE_LIPSYNC`, `RESPONSE_HBR`, `HOT_PLUG_CONTROL`, and `RESPONSE_CONFIGURATION_DEFAULT` cover sink presence/sense, output enable, speaker/channel allocation, ACP packet data, audio/video lipsync, high-bit-rate audio capability/enable, audio hotplug enable/clock gating, and default pin configuration.
- `CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13` describe per-format audio descriptor fields: max channels, supported frequencies, descriptor byte 2, and for descriptor 0 the stereo frequency byte.
- `CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2` map channel-pair enable/mute/channel-ID fields for channels 0-7.
- `CODEC_PIN_CONTROL_SINK_INFO0` through `SINK_INFO8` expose ELD/sink information payload fields such as manufacturer, product ID, sink description, port ID, audio latency, video latency, and HDMI/DP sink flags.
- `PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8` define IEC 60958 channel-status override bytes and word select/readback fields.
- `CODEC_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`, `LPIB`, and `LPIB_TIMER_SNAPSHOT` expose link-position-in-buffer snapshot lock, wrap count, LPIB, and timer snapshot readbacks.
- `CODEC_PIN_CONTROL_FORMAT_CHANGED`, `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS` define interrupt state, mask, ack, and polarity fields.

Important input endpoint families in this range:

- `CODEC_INPUT_CONVERTER_*` mirrors the converter capability, format, channel/stream ID, digital converter, stream format, and supported-size/rate fields for input-side audio capture/receive paths.
- `CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `CODEC_INPUT_PIN_PARAMETER_CAPABILITIES` describe the input pin widget and its HDA capabilities.
- `CODEC_INPUT_PIN_CONTROL_RESPONSE_INPUT_PIN_SENSE` adds `PRESENCE_DETECT` at bit 31 on top of the impedance-sense field.
- `CODEC_INPUT_PIN_CONTROL_WIDGET_CONTROL` exposes `IN_ENABLE`, while output endpoint widget control exposes `OUT_ENABLE`.
- `CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2` provide one channel per byte for input channels 0-7, with enable, mute, and channel-ID fields.
- `CODEC_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL` exposes input activity, channel layout, input activity unsolicited-response enable, and channel-layout/channel-status infoframe-change unsolicited-response enable.
- `CODEC_INPUT_PIN_CONTROL_INFOFRAME` exposes input audio infoframe channel count, channel allocation, byte 5, and valid flag.

## Control Flow

This header has no executable control flow. Runtime sequencing is supplied by AMDGPU Display Core code that includes `dcn_3_1_5_offset.h` and `dcn_3_1_5_sh_mask.h`, constructs register and field tables through token-pasting macros, and then calls MMIO/indexed-register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, or related generated field helpers.

A typical use path is:

1. A DCN315 display-audio or resource path selects an Azalia endpoint instance, such as endpoint 5 or input endpoint 0.
2. The companion offset header supplies the indexed register selector for that endpoint register.
3. This shift/mask header supplies the field position and mask.
4. Register helpers pack a new field value, preserve unrelated bits, read a status field, or acknowledge an interrupt/status bit.
5. Hardware latches, reports, clears, or consumes the represented endpoint state according to the Azalia/HDA register protocol.

The macros do not encode HDA command ordering, codec verb sequencing, hotplug timing, ELD update timing, stream disable/enable ordering, or write-one-to-clear semantics. Callers must still follow those rules in functional driver code.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes MMIO/indexed hardware state in the GPU display-audio block.

Configuration-like hardware fields include converter format, stream ID, channel ID, digital converter control, stripe control, GTC embedding control, pin widget output/input enable, speaker/channel allocation, ACP packet data, multichannel enable/mute/channel mapping, HBR enable, hotplug audio enable, unsolicited response enable/tag, default configuration, channel-status override bytes, remote keepalive, and audio-enable controls.

Readback/status fields include audio widget and pin capabilities, supported stream formats and size/rates, pin sense/impedance/presence, sink info/ELD data, lipsync delay values, HBR capability, LPIB and timer snapshots, format-changed flags, audio enabled/disabled/format-changed interrupt status, input activity, input channel layout, and input audio infoframe validity.

Several fields are likely side-effecting when written, based on their names and HDA register conventions: interrupt acknowledge fields, interrupt masks/polarities, forced unsolicited response trigger, LPIB snapshot lock, hotplug/audio enable, remote keepalive, and channel-status override selection/control. The generated masks do not distinguish read-only, sticky, self-clearing, or write-one-to-clear behavior; that behavior must be inferred from the hardware specification and the driver code using the fields.

## Dependencies And Integration Points

This chunk must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`. The offset header defines the indexed register numbers and base selectors; this header defines the bit layouts. A missing macro name generally fails compilation, while an incorrect numeric mask or shift can compile and silently program or decode the wrong hardware bits.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`, which includes the DCN315 offset and shift/mask headers for DMUB-facing register metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`, which includes the same generated headers for DCN315 interrupt/register field definitions.
- DCN315 resource construction reached from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_resource.c`, which creates the DCN315 resource pool and binds generated register metadata into display hardware objects.

Functional consumers are indirect. Display-audio helpers and stream encoders select Azalia audio instances, enable audio packets, configure audio source/channel mapping, program infoframes and IEC 60958 channel-status data, react to hotplug and format changes, and service audio-related interrupts using register tables built from generated headers. Local code also documents sink-description handling around `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT` in `display/dc/core/dc_resource.c`.

The endpoint macros are highly instance-specific. `AZF0ENDPOINT5`, `AZF0ENDPOINT6`, and `AZF0ENDPOINT7` have nearly identical layouts, while `AZF0INPUTENDPOINT0` and `AZF0INPUTENDPOINT1` use input-specific register names and field names. Resource and audio code must bind the correct generated prefix to the intended audio endpoint.

## Risks And Maintenance Notes

- The primary risk is generated-header drift from the DCN 3.1.5 register database. A wrong mask or shift can corrupt audio format programming, channel routing, HBR enablement, sink/ELD interpretation, LPIB readback, or interrupt acknowledge behavior without producing a compile error.
- This range starts mid-register family. `AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_PARAMETER_CAPABILITIES` has earlier shift definitions before line 57718; the final per-file report should merge adjacent chunks before presenting endpoint 4 as complete.
- This range ends inside input endpoint 1. Only `AZF0INPUTENDPOINT1_AZALIA_F0_CODEC_INPUT_CONVERTER_PIN_DEBUG` and the beginning of `CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` are visible here; later chunks own the rest of input endpoint 1.
- Output endpoint blocks 5-7 are repetitive. A generator error affecting only one instance can still compile and only fail on connector/audio paths routed through that endpoint.
- Output and input endpoint names are similar but not interchangeable. Confusing `CODEC_PIN_CONTROL_WIDGET_CONTROL__OUT_ENABLE` with `CODEC_INPUT_PIN_CONTROL_WIDGET_CONTROL__IN_ENABLE`, or `RESPONSE_PIN_SENSE` with `RESPONSE_INPUT_PIN_SENSE`, can target a valid-looking but wrong field.
- Channel mapping fields are dense and repeated. The multichannel enable registers pack enable, mute, and channel ID into byte-sized groups; off-by-one channel or pair mapping errors can appear as swapped, muted, or missing audio channels.
- Interrupt/status fields expose mask, ack, polarity, and status bits in the same family. Treating an acknowledge bit like ordinary persistent state can clear events unexpectedly, while failing to preserve mask/polarity bits can break audio hotplug or format-change notification.
- Sink information and descriptor fields are protocol-facing. Bad masks can make the driver advertise the wrong speaker allocation, channel allocation, latency, HBR capability, HDMI/DP connection type, or supported sample rates to higher display-audio logic.

## Test Signals

Useful validation for changes touching this chunk includes:

- Compile AMDGPU Display Core with DCN315 enabled. This catches missing or malformed generated macro names referenced by DCN315 resource, IRQ, DMUB, audio, and stream-encoder code.
- Regenerate or mechanically compare `dcn_3_1_5_sh_mask.h` against the authoritative DCN 3.1.5 register database, especially for `AZF0ENDPOINT4` tail fields, complete `AZF0ENDPOINT5`-`7`, and `AZF0INPUTENDPOINT0`/`1` boundary fields.
- Check that each complete register group in this slice has expected paired `__SHIFT` and `_MASK` definitions, while allowing boundary exceptions at the beginning and end of the chunk.
- Preprocess representative `REG_GET`, `REG_SET`, `REG_UPDATE`, field-table, and audio register-list macros to ensure token concatenation resolves to the intended `AZF0ENDPOINT<n>` or `AZF0INPUTENDPOINT<n>` symbols.
- Runtime HDMI/DP audio tests on DCN315 hardware for endpoints routed through output endpoints 5-7: modeset, hotplug, audio enable/disable, PCM playback, channel mapping, multichannel playback, sample-rate changes, HBR/encoded audio where supported, and suspend/resume.
- Sink/ELD validation by comparing reported monitor audio capabilities, speaker allocation, latency, manufacturer/product/port fields, and audio descriptors against known-good EDID/ELD data.
- Interrupt and status validation for audio enabled, audio disabled, format changed, unsolicited response, input activity, and infoframe-change paths, including checking that status bits clear only when expected.
- Register-dump validation before and after audio setup. Writes should affect only the intended masked bits and preserve neighboring fields in dense registers such as multichannel enables, channel-status overrides, hotplug control, and interrupt status/control.

## Cross-Chunk Notes

Previous chunks own the beginning of endpoint 4, including earlier converter and pin parameter fields before line 57718. Later chunks continue input endpoint 1 after the partial audio-widget capability block. The final per-file research document should merge adjacent chunk reports before making complete claims about all DCN 3.1.5 Azalia output endpoints or the full input endpoint namespace.
