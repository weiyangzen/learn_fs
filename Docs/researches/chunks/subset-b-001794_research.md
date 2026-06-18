# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 32086-34399

## Scope

This chunk covers 2,314 lines from the generated DCN 3.0.3 shift/mask header. It contains only preprocessor constants and generated grouping comments; there are no C functions, structs, enums, storage definitions, branches, loops, or local algorithms in this range.

The range is part of the AMD display Azalia function 0 register field map. It starts inside `AZF0ENDPOINT5_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE2`, covers the tail of output endpoint 5, then covers complete output endpoint 6 and output endpoint 7 blocks, complete input endpoint 0 through input endpoint 3 blocks, and the beginning of input endpoint 4. It ends inside `AZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`, after `NON_AUDIO_MASK`; later masks for that register and the rest of input endpoint 4 continue in the next chunk.

The chunk contains 2,032 `#define` entries: 1,013 `__SHIFT` definitions and 1,019 `_MASK` definitions. Generated register-group comments identify 23 endpoint-5 groups, 71 endpoint-6 groups, 71 endpoint-7 groups, 23 groups each for input endpoints 0 through 3, and 4 early input-endpoint-4 groups.

## Purpose

This header slice gives DCN 3.0.3 display-audio code symbolic bit positions and masks for Azalia/HD-audio-style converter and pin registers. Runtime code can combine these constants with the matching offset/index header and AMD display register helper macros to read, update, or decode hardware fields without hard-coded bit arithmetic.

For output endpoint 5, the range covers the remaining pin-control fields: multichannel slots, IEC 60958 channel-status override registers, association and digital-output status, LPIB snapshot data, coding type, format-change status/acknowledgement, wireless-display identification, remote keepalive, audio enable state, and audio enabled/disabled/format-change interrupt status.

For output endpoints 6 and 7, the range maps the full endpoint field surface: converter capabilities, converter format, stream/channel routing, digital converter state, stream format/rate/size support, stripe/ramp/GTC timing controls, pin capabilities, unsolicited responses, pin sense, widget control, channel speaker allocation, audio descriptors, multichannel routing, lipsync, HBR, sink information, hot-plug state, forced unsolicited responses, default pin configuration, IEC channel-status overrides, LPIB snapshots, coding type, format-change state, wireless-display identification, remote keepalive, audio enable status, and audio interrupt status.

For input endpoints 0 through 3, the range maps the full input endpoint pattern: input converter capabilities and format controls, input stream/channel IDs, digital converter flags, supported stream formats and sample sizes/rates, input pin capabilities, unsolicited response state, input pin sense, widget enable, multichannel routing, HBR capability/enablement, channel allocation, hot-plug audio state, forced unsolicited responses, pin default configuration, LPIB snapshots, input activity/status controls, and infoframe fields. Input endpoint 4 is only partially present through the beginning of its digital converter register.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated preprocessor naming contract:

- `AZF0ENDPOINT<n>_...__<FIELD>__SHIFT` gives a field bit offset for an output endpoint indexed register.
- `AZF0ENDPOINT<n>_...__<FIELD>_MASK` gives the corresponding output endpoint field mask.
- `AZF0INPUTENDPOINT<n>_...__<FIELD>__SHIFT` and `_MASK` provide the same contract for input endpoint indexed registers.
- Comments such as `// addressBlock: azf0endpoint6_endpointind` and `//AZF0INPUTENDPOINT3_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME` group constants by generated address block and logical register.

Important output endpoint register families in this chunk include:

- `AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, exposing widget attributes such as channel capability, amplifier presence, format override, stripe, processing widget, unsolicited response support, connection list, digital, power control, LR swap, widget delay, and widget type.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT`, mapping number of channels, bits per sample, sample base divisor, sample base multiple, sample base rate, and stream type.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_CHANNEL_STREAM_ID`, mapping channel ID and stream ID.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_DIGITAL_CONVERTER`, mapping `DIGEN`, validity/config/preemphasis/copy/non-audio/professional flags, category code, and keepalive.
- `AZALIA_F0_CODEC_CONVERTER_PARAMETER_STREAM_FORMATS` and `SUPPORTED_SIZE_RATES`, exposing supported stream formats, audio rate capabilities, and bit-depth capabilities.
- `AZALIA_F0_CODEC_CONVERTER_STRIPE_CONTROL`, `CONTROL_RAMP_RATE`, `CONTROL_GTC_EMBEDDING`, and `GTC_COUNTER_DELTA*`, mapping striping, ramp rate, GTC embedding enable, and GTC counter delta values.
- `AZALIA_F0_CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `AZALIA_F0_CODEC_PIN_PARAMETER_CAPABILITIES`, defining pin widget and physical pin capability fields such as HDMI/DP, EAPD, VREF, input/output capability, presence-detect, trigger, balanced I/O, and headphone drive.
- `AZALIA_F0_CODEC_PIN_CONTROL_CHANNEL_SPEAKER`, `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, `MULTICHANNEL_ENABLE`, `MULTICHANNEL_ENABLE2`, and `MULTICHANNEL_MODE`, covering speaker/channel allocation, short-audio-descriptor bytes, channel enable/mute/channel-ID slots, and multichannel mode.
- `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_LIPSYNC`, `RESPONSE_HBR`, and `SINK_INFO0` through `SINK_INFO8`, covering audio/video latency, HBR capable/enable bits, sink manufacturer/product identity, port ID, sink description bytes, connection information, and converter ID.
- `AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL`, `UNSOLICITED_RESPONSE_FORCE`, and `RESPONSE_CONFIGURATION_DEFAULT`, mapping hot-plug clock/audio state, forced unsolicited response payloads, and default pin-configuration fields.
- `AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8`, defining IEC 60958 channel-status override values and override-enable fields for mode, category code, source number, clock accuracy, word length, sampling frequency, original sampling frequency, CGMS-A, MPEG surround, and channel numbers.
- `AZALIA_F0_CODEC_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`, `LPIB`, and `LPIB_TIMER_SNAPSHOT`, defining audio position and timer snapshot fields.
- `AZALIA_F0_CODEC_PIN_CONTROL_FORMAT_CHANGED`, `AUDIO_ENABLE_STATUS`, `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS`, defining format-change flags/reasons/responses and audio enable/disable/change interrupt flag/mask/type fields.

Important input endpoint register families include:

- `AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`, `INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID`, `INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`, `INPUT_CONVERTER_PARAMETER_STREAM_FORMATS`, and `INPUT_CONVERTER_PARAMETER_SUPPORTED_SIZE_RATES`, mirroring converter-side audio format, routing, capability, and digital metadata fields for input paths.
- `AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `INPUT_PIN_PARAMETER_CAPABILITIES`, defining input pin capability bits.
- `INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE`, `RESPONSE_INPUT_PIN_SENSE`, and `WIDGET_CONTROL`, defining unsolicited-response tagging/enabling, impedance/presence sense, and input widget enable.
- `INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2`, packing enable, mute, and 4-bit channel IDs for input multichannel slots 0 through 7.
- `INPUT_PIN_CONTROL_RESPONSE_HBR`, `CHANNEL_ALLOCATION`, `HOT_PLUG_CONTROL`, `UNSOLICITED_RESPONSE_FORCE`, `RESPONSE_CONFIGURATION_DEFAULT`, `LPIB*`, `INPUT_STATUS_CONTROL`, and `INFOFRAME`, defining HBR, channel allocation, hot-plug audio enable state, default configuration, position snapshots, input activity/channel layout, infoframe validity, and infoframe channel metadata.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time symbol resolution:

1. DCN 3.0.3 display code includes `dcn_3_0_3_sh_mask.h` with the matching DCN 3.0.3 offset header.
2. Register helper macros concatenate register and field tokens to resolve `__SHIFT` and `_MASK` symbols.
3. Runtime MMIO or indexed-register paths use the resolved constants to mask, shift, insert, or extract fields.

The declaration order mirrors the generated hardware address-block order. The range starts in endpoint 5 pin-control fields, enters `azf0endpoint6_endpointind`, then `azf0endpoint7_endpointind`, then `azf0inputendpoint0_inputendpointind` through `azf0inputendpoint4_inputendpointind`. Within most register groups, shift macros precede mask macros for the same fields.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes the layout of state held by DCN 3.0.3 display-audio hardware:

- Converter control fields represent programmed audio stream shape, channel/stream association, digital converter flags, keepalive behavior, stripe/ramp settings, and GTC timing relationships.
- Capability fields represent hardware-advertised widget, pin, stream-format, sample-rate, and sample-size support. This header does not encode whether a field is read-only, read/write, volatile, sticky, or write-one-to-clear.
- Output pin fields represent sink-facing HDMI/DisplayPort audio state: speaker and channel allocation, SAD/audio descriptor payloads, lipsync, HBR, sink identity, sink information, hot-plug audio state, format-change response, wireless-display identification, remote keepalive, and IEC channel-status overrides.
- LPIB and timer snapshot fields represent hardware audio position and timing snapshots, including snapshot lock and cyclic-buffer wrap count.
- Interrupt fields represent audio enabled, disabled, and format-changed flag/mask/type state.
- Input pin fields represent input activity, channel layout, infoframe validity/data, input pin sense, unsolicited-response behavior, and multichannel routing.

Persistence is hardware-defined. Writable fields may retain values until the driver reprograms them, the display/audio block is reset, suspend/resume state is restored, or the ASIC is reset. Status and capability fields can change asynchronously with hardware state, sink/source connection state, and display audio routing.

## Dependencies And Integration Points

This chunk depends on generated DCN 3.0.3 register files staying synchronized:

- `dcn_3_0_3_offset.h` supplies the matching indexed MMIO access registers and `ix...` register offsets. For example, it defines `mmAZF0ENDPOINT6_AZALIA_F0_CODEC_ENDPOINT_INDEX` at `0x03aa`, `ixAZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_REMOTE_KEEPALIVE` at `0x006a`, and `ixAZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_SUPPORTED_SIZE_RATES` at `0x0006`.
- AMD display register helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT` rely on the exact `__SHIFT` and `_MASK` suffix convention used here.
- DCN audio, HDMI, DisplayPort, hotplug, interrupt, and power-management paths integrate with these constants when programming or reading display audio endpoints.
- Generated register databases are the source of truth for field semantics. This header captures numeric bit layout, not legal value ranges, write permissions, reset values, or sequencing rules.

The main integration contract is preprocessor naming. Missing or renamed fields usually fail at compile time, while wrong numeric masks or shifts can compile cleanly and cause incorrect MMIO field extraction or writes.

## Risks And Edge Cases

- The range starts and ends mid-register group. Endpoint 5 `MULTICHANNEL_ENABLE2` must be reconciled with the previous chunk, and input endpoint 4 `INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER` must be completed from the next chunk before making whole-group claims.
- The endpoint blocks are highly repetitive. A generator or manual merge error affecting only one endpoint number may be difficult to spot because most lines differ only by endpoint prefix.
- Shift/mask mismatches are high risk for fields such as `AUDIO_ENABLED`, `PRESENCE_DETECT`, `INFOFRAME_VALID`, `DOWN_MIX_INHIBIT`, `KEEPALIVE`, interrupt masks/types, and multichannel channel IDs.
- Several payload fields use `0xFFFFFFFFL`, including stream formats, GTC deltas, LPIB values, timer snapshots, association information, and sink information. Consumers should avoid signed-width assumptions when combining these masks with intermediate integer types.
- Capability, status, interrupt, and control fields share identical macro style. This file does not protect callers from writing read-only fields, clearing sticky status incorrectly, or confusing mask bits with value bits.
- `UNSOLICITED_RESPONSE_FORCE` fields can synthesize hardware notifications. Incorrect use can create misleading audio, hotplug, or pin events.
- Multichannel enable registers pack multiple enable, mute, and channel-ID fields into one 32-bit word. An incorrect mask or endpoint prefix can corrupt adjacent slots.
- IEC channel-status override registers contain both value and override-enable bits. Programming only value fields, or using the wrong endpoint's override fields, may silently leave transmitted channel-status metadata unchanged.
- Cross-generation reuse is risky. DCN 3.0.3 Azalia fields are similar to adjacent DCN/DCE generations, but code must include the offset and shift/mask headers that match the target ASIC.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration oriented:

- Build the AMDGPU DCN 3.0.3 display code that includes this header to catch missing macro names in register-helper expansions.
- Preprocess representative users of `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE` for Azalia fields to confirm the expected `AZF0ENDPOINT*` and `AZF0INPUTENDPOINT*` macros resolve.
- Compare this header against `dcn_3_0_3_offset.h` and the generator register database to ensure indexed endpoint registers have matching field definitions and that masks align with documented bit ranges.
- Exercise HDMI and DisplayPort audio enumeration on DCN 3.0.3 hardware, checking widget and pin capabilities, supported stream formats/rates/sizes, audio descriptors, sink information, HBR state, and channel allocation.
- Test audio enable/disable, format-change, hotplug, and unsolicited-response paths while observing `AUDIO_ENABLE_STATUS`, audio interrupt status fields, hot-plug `AUDIO_ENABLED`, and `FORMAT_CHANGED` fields.
- Exercise stereo, multichannel, and HBR audio modes to validate multichannel enable/mute/channel-ID packing, speaker/channel allocation, IEC channel-status override behavior, and converter stream/channel routing.
- Test suspend/resume and display reset paths to confirm converter, pin, sink info, hotplug, LPIB snapshot, infoframe, interrupt, and keepalive state is restored or re-read correctly.
- If input audio paths are exposed by the platform, validate input activity, channel layout, input pin sense, infoframe validity/data, channel allocation, and forced/ordinary unsolicited-response behavior.

## Open Cross-Chunk Questions

- The merge lane should combine this with the previous chunk to complete the beginning of `AZF0ENDPOINT5_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE2`.
- The merge lane should combine this with the next chunk to finish `AZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER` and the remainder of input endpoint 4.
- Whole-file analysis should verify the expected output/input endpoint count for DCN 3.0.3 and compare generated field layouts with the authoritative AMD register source.
