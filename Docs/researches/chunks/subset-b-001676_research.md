# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 49415-51898

## Scope

This chunk is a generated constants-only slice of AMDGPU's DCN 2.1.0 register shift/mask header. It contains no functions, structs, enums, storage objects, or executable code. The exported interface is 2,030 preprocessor definitions: 1,015 `__SHIFT` constants and 1,015 already-positioned `_MASK` constants for fields in DCN 2.1 Azalia/display-audio registers.

The range starts at the tail of sink description byte fields (`SINK_DESCRIPTION15` through `SINK_DESCRIPTION17`), then covers Azalia input/output CRC result windows, the function-2 input codec node, function-2 root/function codec parameters, sixteen `AZF0STREAM*` stream latency/FIFO windows, full function-0 output endpoint blocks 0 through 2, and the opening converter fields of output endpoint 3. The source line boundary is artificial: endpoint 3 continues after this chunk and the earlier sink description fields begin in the previous chunk.

## Purpose

The header provides exact bit positions and masks for DCN 2.1.0 display-audio hardware registers. Consumers use these generated constants with matching address macros from `dcn_2_1_0_offset.h` so generic register helpers can read, compose, update, and decode hardware fields without hard-coding bit arithmetic at each call site.

Major hardware areas represented in this chunk are:

- `SINK_DESCRIPTION15` through `SINK_DESCRIPTION17`: final single-byte sink description fields, used by audio sink/ELD-style metadata paths.
- `AZALIA_INPUT_CRC{0,1}_CHANNEL0..7` and `AZALIA_CRC{0,1}_CHANNEL0..7`: 32-bit per-channel input and output audio CRC result fields for diagnostic validation.
- `AZALIA_F2_CODEC_INPUT_*`: function-2 input converter and input pin controls, including stream format, channel/stream binding, digital converter status, pin enable, unsolicited response, pin sense, default configuration, channel allocation, multichannel enable/mute/channel IDs, HBR, LPIB snapshots, input activity, infoframe fields, channel status, widget capabilities, and pin capabilities.
- `AZALIA_F2_CODEC_ROOT_*` and `AZALIA_F2_CODEC_FUNCTION_*`: root/function-level vendor/device, revision, subordinate-node, power-state, subsystem-ID, converter synchronization, reset, supported rate/format, group type, and power-state capability fields.
- `AZF0STREAM0` through `AZF0STREAM15`: repeated FIFO sizing and latency counter controls for each audio stream, including manual/ack/update flags, RAM byte count, worst-case latency count, cumulative latency count, and cumulative request count.
- `AZF0ENDPOINT0`, `AZF0ENDPOINT1`, and `AZF0ENDPOINT2`: repeated function-0 HDMI/DisplayPort output audio endpoint register fields for converter controls, pin controls, sink information, audio descriptors, multichannel routing, channel-status overrides, LPIB snapshots, format-change tracking, remote keepalive, and audio enable/disable/format-change interrupt status.
- `AZF0ENDPOINT3`: the first converter capability and converter-format fields for a fourth output endpoint, with the remainder outside this line range.

Although the repository path is under `sources/distributed-fs/ceph-client`, this source is AMD display hardware metadata. It has no Ceph filesystem, distributed storage, network protocol, or persistent storage behavior.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The API contract is the generated macro naming scheme:

- `REGISTER__FIELD__SHIFT` gives the low bit position for a field.
- `REGISTER__FIELD_MASK` gives the field mask already shifted into register position.
- Register comments such as `//AZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL` group fields by hardware register.
- Address-block comments such as `// addressBlock: azf0stream0_streamind` and `// addressBlock: azf0endpoint0_endpointind` identify indexed hardware register windows.

The input codec group exposes HDA-style format and capability fields. Representative macros include `AZALIA_F2_CODEC_INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT__NUMBER_OF_CHANNELS_MASK`, `...BITS_PER_SAMPLE_MASK`, `...SAMPLE_BASE_DIVISOR_MASK`, `...SAMPLE_BASE_MULTIPLE_MASK`, `...SAMPLE_BASE_RATE_MASK`, and `...STREAM_TYPE_MASK`; `AZALIA_F2_CODEC_INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID__CHANNEL_ID_MASK` and `...STREAM_ID_MASK`; `AZALIA_F2_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER__DIGEN_MASK`, `...V_MASK`, `...NON_AUDIO_MASK`, `...PRO_MASK`, `...CC_MASK`, and `...KEEPALIVE_MASK`; and input pin status/infoframe fields such as `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL__INPUT_ACTIVITY_MASK` and `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_INFOFRAME__INFOFRAME_VALID_MASK`.

The stream blocks repeat a small latency/FIFO model per `AZF0STREAMn`. Each stream has `AZALIA_FIFO_SIZE_CONTROL` fields for `AZALIA_FIFO_SIZE_MANUAL`, `AZALIA_FIFO_SIZE_UPDATE`, `AZALIA_FIFO_SIZE_ACK`, and `AZALIA_FIFO_SIZE_RAM`; plus `AZALIA_LATENCY_COUNTER_CONTROL`, `AZALIA_WORSTCASE_LATENCY_COUNT`, `AZALIA_CUMULATIVE_LATENCY_COUNT`, and `AZALIA_CUMULATIVE_REQUEST_COUNT`.

The endpoint blocks repeat a dense output codec model. Important groups include:

- `AZF0ENDPOINTn_AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` for audio widget capability flags, delay, and type.
- `...CONVERTER_CONTROL_CONVERTER_FORMAT` for channel count, sample size, sample-rate encoding, and PCM/non-PCM stream type.
- `...CONVERTER_CONTROL_CHANNEL_STREAM_ID` for stream-to-channel binding.
- `...CONVERTER_CONTROL_DIGITAL_CONVERTER` for digital enable, validity, pre-emphasis, copyright, non-audio/professional metadata, category code, generation level, and keepalive.
- `...CONVERTER_PARAMETER_STREAM_FORMATS`, `...SUPPORTED_SIZE_RATES`, `...STRIPE_CONTROL`, `...CONTROL_RAMP_RATE`, `...CONTROL_GTC_EMBEDDING`, and `...GTC_COUNTER_DELTA*` for capabilities and presentation-time/GTC synchronization.
- `...CODEC_PIN_PARAMETER_*` and `...CODEC_PIN_CONTROL_*` for pin capabilities, unsolicited response, pin sense, output enable, speaker/channel allocation, audio descriptors 0 through 13, multichannel enable/mute/channel IDs, lipsync, HBR, sink info, hot-plug audio enable, forced unsolicited response payloads, configuration default, LPIB, coding type, format-change state, wireless display identification, and remote keepalive.
- `...PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8` for IEC 60958 channel-status override fields.
- `...AUDIO_ENABLE_STATUS`, `...AUDIO_ENABLED_INT_STATUS`, `...AUDIO_DISABLED_INT_STATUS`, and `...AUDIO_FORMAT_CHANGED_INT_STATUS` for endpoint audio state and interrupt metadata.

## Control Flow

This header has no local control flow. Runtime behavior occurs in the DCN 2.1 display driver code that includes the offset and mask headers and expands register tables through helper macros.

A typical path is:

1. DCN 2.1 resource, IRQ, GPIO, DMUB, or audio code includes `dcn_2_1_0_offset.h` and this `dcn_2_1_0_sh_mask.h`.
2. Register-table macros such as `REG_OFFSET`, `SRI`, `SR`, `SF`, `FD_MASK`, and `FD_SHIFT` paste register and field names into generated macro names.
3. Driver code stores the resulting offsets, masks, and shifts in generation-specific register structures.
4. Common helpers issue MMIO or indexed Azalia endpoint accesses, using the masks and shifts to update or decode individual fields.

The control-sensitive flows represented by this chunk include display-audio stream format programming, stream ID assignment, digital converter enable/metadata handling, endpoint/pin capability reporting, channel and speaker allocation, high-bit-rate audio enablement, sink descriptor propagation, hot-plug audio enablement, latency counter sampling, LPIB snapshot locking, format-change acknowledgment, and audio enable/disable/format-change interrupt reporting.

## State And Persistence Behavior

The file itself stores no state and performs no persistence. It describes hardware register state whose lifetime is controlled by DCN/Azalia hardware, driver writes, power management, reset, and hotplug/modeset activity.

State represented in this range includes:

- CRC readback state for input and output audio channels, useful for validation rather than normal configuration.
- Input converter state: stream format, channel/stream routing, digital converter control, keepalive, supported size/rate masks, and supported stream formats.
- Input pin state: pin enable, unsolicited response tag/enable, pin sense, default configuration bytes, channel allocation, multichannel enable/mute/channel IDs, HBR capability/enable, LPIB snapshots, input activity, channel layout, infoframe contents, and channel-status words.
- Root/function codec state: vendor/device/revision identity, subordinate node counts, power-state request/actual state, clock-stop capability, reset, group type, supported size/rates, supported stream formats, and subsystem ID bytes.
- Stream telemetry state: FIFO size update/ack bits plus worst-case and cumulative latency/request counters.
- Output endpoint state: converter format, stream binding, digital converter metadata, presentation-time/GTC embedding, endpoint/pin capabilities, output active/enable status, audio descriptor and sink information, hot-plug audio enable state, channel-status overrides, LPIB snapshots, coding type, format-change response fields, wireless display identity, remote keepalive, and interrupt flags/masks/types.

Some of these fields are writable configuration latches, some are read-only or hardware-updated status/counter values, and some combine status, mask, type, enable, force, and acknowledgment semantics. The generated header does not encode access permissions or ordering rules; consumers must apply the hardware programming sequence correctly.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`, which supplies matching register addresses and indexed offsets. This chunk supplies the field layout within those registers. Both headers depend on AMD display helper conventions that paste register and field identifiers into `_MASK` and `__SHIFT` names.

Visible DCN 2.1 include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, which includes the generated headers and builds DCN 2.1 resource tables, including `audio_regs`, `audio_shift`, and `audio_mask`. Its audio mask list uses `AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX` and `AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_DATA` fields as the indexed access pair for output audio endpoints.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h`, which defines the common `AUD_COMMON_REG_LIST` and audio field-list macros consumed by DCN resource files.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`, which includes this header for DCN 2.1 interrupt register and field definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c` and `hw_translate_dcn21.c`, which include the same generated header for GPIO/HPD translation and register-mask tables elsewhere in the file.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`, which uses `FD_MASK` and `FD_SHIFT` expansions from the generated header for DMUB common field tables.

The Azalia field names also align with generated enum headers such as `soc24_enum.h` and `vega10_enum.h`, which document symbolic values for fields like input converter bits per sample, number of channels, sample-base divisor/multiple/rate, stream type, digital enable, multichannel mute, unsolicited response enable, and input pin enable.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A wrong shift or mask will usually compile cleanly but can set or read the wrong bit, truncate a field, leave stale bits behind during read/modify/write, or acknowledge/mask the wrong interrupt.

Display audio fields are externally visible. Bad converter format, sample-rate, channel-count, stream-type, stream-ID, digital-converter, channel-allocation, audio-descriptor, sink-info, HBR, or IEC 60958 channel-status masks can lead to no HDMI/DisplayPort audio, incorrect PCM/non-PCM handling, wrong channel layout, bad sample rate/word length metadata, broken HBR audio, or endpoint-specific audio failures after hotplug.

Interrupt and event fields are sensitive because they mix flag, mask, type, response, enable, and force fields. Incorrect constants in `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, `AUDIO_FORMAT_CHANGED_INT_STATUS`, `UNSOLICITED_RESPONSE`, `UNSOLICITED_RESPONSE_FORCE`, or `FORMAT_CHANGED` can drop events, generate spurious events, fail to clear sticky status, or route events to the wrong endpoint.

The generated repetition creates copy/generation hazards. `AZF0STREAM0` through `AZF0STREAM15` should remain structurally aligned; `AZF0ENDPOINT0` through `AZF0ENDPOINT2` are near-identical endpoint instances; and endpoint 3 begins with the same converter pattern. Any one-off difference in a repeated shift or mask should be verified against the ASIC register database rather than assumed intentional.

Chunk boundaries matter. This range begins after the first sink-description fields and ends after only the opening `AZF0ENDPOINT3` converter format definitions. The final per-file research merge should avoid treating this slice as a complete Azalia or endpoint inventory.

## Test Signals

Useful validation signals include:

- Build coverage for DCN 2.1 resource, IRQ, GPIO, DMUB, and audio code that includes `dcn_2_1_0_sh_mask.h`.
- Generated-header consistency checks that every `__SHIFT` has a matching `_MASK`, masks align with their shifts and expected widths, and every register appears in the matching `dcn_2_1_0_offset.h`.
- Repetition checks across `AZF0STREAM0..15` and `AZF0ENDPOINT0..3` to detect accidental drift in repeated generated instances.
- HDMI/DisplayPort audio playback tests across PCM and non-PCM formats, sample-rate changes, word-length changes, two-channel and multichannel layouts, HBR, hotplug, modeset, suspend/resume, and monitor replacement.
- Audio event tests confirming enabled, disabled, and format-changed interrupt flags/masks/types assert and clear as expected for each endpoint.
- Sink metadata tests that validate audio descriptor, sink info, channel allocation, speaker allocation, channel-status override, and ELD-derived behavior reported to the audio stack.
- CRC and latency telemetry checks that audio CRC, FIFO-size update/ack, worst-case latency, cumulative latency, request counts, LPIB, and timer snapshots move plausibly while audio streams are active.

Regression symptoms from bad constants include missing or distorted HDMI/DP audio, incorrect channel count or sample rate, stuck audio interrupts, repeated unsolicited responses, failure to detect format changes, broken HBR streams, bad sink capability reporting, or a failure that affects only one generated stream or endpoint instance.

## Cross-Chunk Notes

This is one artificial line-range chunk from a generated whole-file register map. The previous chunk owns earlier sink description fields and likely more Azalia/global audio definitions. The next chunk continues `AZF0ENDPOINT3` and later endpoint/input-endpoint material. The final merge lane should present this as part of the DCN 2.1 generated register contract rather than as an independently maintained module.
