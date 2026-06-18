# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 59303-61604

## Scope

This chunk covers 2,302 lines from the generated DCN 3.0.2 shift/mask header. It contains only C preprocessor constants and generated grouping comments; there are no functions, structs, enums, storage objects, or executable statements in this slice.

The line range is part of the AMD display Azalia function 0 register field map. It starts in the middle of the `AZF0ENDPOINT6_AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` field list, continues through the rest of output endpoint 6, covers a complete output endpoint 7 block, then covers complete input endpoint 0 through input endpoint 3 blocks and the beginning of input endpoint 4. It ends inside `AZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL`, after the `CLOCK_GATING_DISABLE_MASK` definition and before the remaining masks and later input endpoint 4 pin-control groups.

The chunk contains 2,035 `#define` entries: 1,014 `__SHIFT` definitions and 1,021 `_MASK` definitions. The named register groups include 70 output endpoint 6 groups, 71 output endpoint 7 groups, 23 groups each for input endpoints 0-3, and 16 groups for the partial input endpoint 4 block.

## Purpose

The purpose of this header region is to provide symbolic bit positions and bit masks for DCN 3.0.2 display-audio hardware registers. The AMDGPU display code can use these generated constants through register helper macros instead of embedding raw shifts and masks when it programs or reads Azalia/HD-audio-style converter and pin registers.

For output endpoints 6 and 7, this chunk describes converter format, stream/channel routing, digital converter state, supported stream formats and size/rate capabilities, stripe/ramp/GTC controls, pin widget and pin capabilities, speaker/channel mapping, audio descriptors, multichannel routing, lipsync and HBR state, sink information, hot-plug state, forced unsolicited responses, default configuration, IEC channel-status overrides, LPIB snapshots, coding type, format-change state, wireless-display identification, remote keepalive, audio enable status, and audio enable/disable/format-change interrupt status.

For input endpoints 0 through 4, it describes input converter capabilities, input stream format selection, channel/stream IDs, digital converter flags, supported input stream formats and size/rates, input pin capabilities, unsolicited-response controls, input pin-sense state, widget input enable, multichannel routing, HBR, channel allocation, hot-plug audio state, default configuration, LPIB snapshots, input activity/status controls, and audio infoframe fields. Input endpoint 4 is incomplete in this chunk and continues in the next source range.

This is a hardware contract file. Its value is the exact macro name and numeric field layout consumed by ASIC-specific DCN register code, not local algorithmic behavior.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the preprocessor naming contract:

- `AZF0ENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT` gives the bit offset for an output endpoint register field.
- `AZF0ENDPOINT<n>_<REGISTER>__<FIELD>_MASK` gives the mask for the same output endpoint field.
- `AZF0INPUTENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT` and `_MASK` provide the equivalent contract for input endpoint registers.
- Comments such as `// addressBlock: azf0endpoint7_endpointind` and `//AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL` group generated constants by indexed register block and logical register.

The output endpoint register families covered here include:

- `AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, with widget capability fields such as channel capability, amplifier presence, format override, stripe, processing widget, unsolicited response, connection list, digital, power control, LR swap, widget delay, and type. Endpoint 6's first capability group is partial in this range; endpoint 7's is complete.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT`, which maps number of channels, bits per sample, sample base divisor, sample base multiple, sample base rate, and stream type.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_CHANNEL_STREAM_ID`, with channel ID and stream ID fields.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_DIGITAL_CONVERTER`, which maps `DIGEN`, validity/config/preemphasis/copy/non-audio/professional flags, category code, and `KEEPALIVE`.
- `AZALIA_F0_CODEC_CONVERTER_PARAMETER_STREAM_FORMATS` and `AZALIA_F0_CODEC_CONVERTER_PARAMETER_SUPPORTED_SIZE_RATES`, which expose supported format, rate, and bit-depth bitmaps.
- `AZALIA_F0_CODEC_CONVERTER_STRIPE_CONTROL`, `CONTROL_RAMP_RATE`, `CONTROL_GTC_EMBEDDING`, and `GTC_COUNTER_DELTA*`, which cover striping, ramp rate, GTC embedding, and GTC delta counters.
- `AZALIA_F0_CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `AZALIA_F0_CODEC_PIN_PARAMETER_CAPABILITIES`, which describe pin-side widget and pin capabilities including HDMI/DP, EAPD, VREF, input/output capability, balanced I/O, presence-detect, trigger, and headphone drive fields.
- `AZALIA_F0_CODEC_PIN_CONTROL_CHANNEL_SPEAKER`, `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, `MULTICHANNEL_ENABLE`, `MULTICHANNEL_ENABLE2`, and `MULTICHANNEL_MODE`, which describe speaker allocation, channel allocation, SAD-like descriptor bytes, per-channel enable/mute/channel-ID fields, and multichannel mode.
- `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_LIPSYNC`, `RESPONSE_HBR`, and `SINK_INFO0` through `SINK_INFO8`, which expose video/audio latency, HBR capability/enablement, manufacturer/product identity, port ID, sink description bytes, connection info, and converter ID.
- `AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8`, which define IEC 60958 channel-status override value and enable fields such as mode, category code, source number, channel numbers, clock accuracy, word length, sampling frequency, original sampling frequency, CGMS-A, and MPEG surround information.
- `AZALIA_F0_CODEC_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`, `LPIB`, and `LPIB_TIMER_SNAPSHOT`, which describe position/timer snapshot fields.
- `AZALIA_F0_AUDIO_ENABLE_STATUS`, `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS`, which define audio enabled state plus interrupt flag/mask/type fields.

The input endpoint register families covered here include:

- `AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`, `INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID`, `INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`, `INPUT_CONVERTER_PARAMETER_STREAM_FORMATS`, and `INPUT_CONVERTER_PARAMETER_SUPPORTED_SIZE_RATES`, mirroring the converter-side output endpoint fields with input endpoint names.
- `AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `INPUT_PIN_PARAMETER_CAPABILITIES`, which define input pin widget and pin capability fields.
- `INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE`, `RESPONSE_INPUT_PIN_SENSE`, and `WIDGET_CONTROL`, which cover unsolicited response tags/enables, impedance/presence bits, and input widget enable.
- `INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2`, which pack enable, mute, and channel-ID fields for input multichannel slots 0-7.
- `INPUT_PIN_CONTROL_RESPONSE_HBR`, `CHANNEL_ALLOCATION`, `HOT_PLUG_CONTROL`, `UNSOLICITED_RESPONSE_FORCE`, `RESPONSE_CONFIGURATION_DEFAULT`, `LPIB*`, `INPUT_STATUS_CONTROL`, and `INFOFRAME`, which cover input-side HBR, channel allocation, hot-plug audio enable state, forced unsolicited responses, pin default configuration, position snapshots, input activity/channel layout, and infoframe contents.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time macro resolution:

1. DCN 3.0.2 display code includes this `*_sh_mask.h` header together with the matching DCN 3.0.2 register offset header.
2. Register helper macros in the AMD display stack concatenate register and field tokens to resolve `__SHIFT` and `_MASK` constants.
3. Runtime code uses those resolved constants in MMIO read/modify/write paths, register-table initialization, or status extraction.

The declaration order still carries generated hardware structure. The chunk begins inside output endpoint 6, enters a complete `// addressBlock: azf0endpoint7_endpointind` block, then enters `azf0inputendpoint0_inputendpointind` through `azf0inputendpoint4_inputendpointind` blocks in ascending order. Within each register group, shift definitions generally appear before mask definitions for the same fields.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes bit layout for hardware state in the DCN 3.0.2 display audio block:

- Converter controls represent programmed audio stream shape, stream/channel association, IEC/digital converter flags, keepalive behavior, stripe/ramp configuration, and GTC timing/counter relationships.
- Capability registers represent hardware-advertised widget, pin, stream-format, sample-rate, and sample-size support. The macro file does not encode read/write permissions, so consumers must follow the hardware programming model.
- Output pin controls represent HDMI/DisplayPort audio presentation state, including speaker/channel allocation, audio descriptor data, lipsync, HBR, sink identity, sink connection data, hot-plug audio enablement, format-change state, wireless-display identification, and remote keepalive.
- IEC channel-status override fields can alter transmitted channel-status metadata when the paired override-enable bits are programmed.
- LPIB and timer snapshot fields represent hardware position/timing state, including snapshot lock and cyclic-buffer wrap count fields.
- Interrupt status fields represent audio enabled, disabled, and format-changed flag/mask/type state.
- Input pin controls represent input activity, channel layout, infoframe validity/data, input pin sense, unsolicited-response setup, and multichannel channel-slot routing.

Persistence is hardware-defined. Writable control fields may retain values until driver reprogramming, display/audio block reset, suspend/resume restore, or ASIC reset. Status and capability fields may change asynchronously as hardware state, connected sinks/sources, or display audio paths change.

## Dependencies And Integration Points

This chunk depends on generated DCN 3.0.2 register files staying synchronized:

- `dcn_3_0_2_offset.h` supplies matching `mm...` indirect index/data register addresses and `ix...` indexed register offsets for the register names whose fields are defined here. For example, the matching offset header defines the endpoint 7 indexed register access pair and input endpoint 4 indexed register offsets through `ixAZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME`.
- AMD display register helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT` rely on the exact `__SHIFT` and `_MASK` suffix convention.
- DCN resource, audio, HDMI, and DisplayPort paths integrate with these constants when programming display audio endpoints, reading sink capabilities/status, handling audio hotplug, and restoring register state around power transitions.
- Hardware register databases and generated offset/value headers provide the source-of-truth semantics for field values. This header only maps field positions and masks.

The main integration point is the preprocessor name contract. Missing or renamed macros usually fail at compile time. Wrong numeric shifts or masks can compile successfully while causing incorrect MMIO field extraction or writes.

## Risks And Edge Cases

- The chunk starts mid-register group and ends mid-register group. Endpoint 6's first converter capability group and input endpoint 4's hot-plug and later pin controls must be reconciled with adjacent chunks before whole-endpoint completeness claims are made.
- The endpoint blocks are mechanically repetitive. Generator drift affecting only one endpoint number can be hard to notice during review because most lines differ only by the endpoint prefix.
- Shift/mask mismatches are high risk. Bad definitions for high-bit fields such as `AUDIO_ENABLED`, `PRESENCE_DETECT`, `INFOFRAME_VALID`, `DOWN_MIX_INHIBIT`, or interrupt type/mask bits may not be caught by compilation.
- Several full-width masks use `0xFFFFFFFFL`, including stream formats, GTC deltas, LPIB, timer snapshots, and association/info payload fields. Consumers should avoid signed-width assumptions when combining these values.
- Capability, status, and control fields share the same macro style. This header does not prevent writes to read-only or write-one-to-clear style fields.
- `UNSOLICITED_RESPONSE_FORCE` fields can synthesize events. Incorrect writes to force bits could create misleading audio, hotplug, or pin notifications.
- Multichannel enable registers pack enable, mute, and 4-bit channel-ID fields for four slots per register. An incorrect mask can corrupt adjacent slot fields.
- IEC channel-status override registers use both values and override-enable bits. Programming only a value field, or using the wrong endpoint's override field, can silently leave transmitted metadata unchanged.
- Cross-generation reuse is risky. DCN 3.0.2 Azalia field names are similar to earlier DCN headers, but code must include the offset and shift/mask files that match the target ASIC.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration oriented:

- Compile the DCN 3.0.2 AMD display code that includes this header to catch missing macro names in register-helper expansions.
- Preprocess representative users of `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE` for Azalia endpoint fields to verify that expected `AZF0ENDPOINT*` and `AZF0INPUTENDPOINT*` macros resolve.
- Compare this header against `dcn_3_0_2_offset.h` and the generator's register database to ensure every indexed endpoint register has matching field definitions and that field masks align with documented bit ranges.
- Exercise HDMI and DisplayPort audio enumeration on DCN 3.0.2 hardware, checking advertised widget/pin capabilities, stream format/rate support, SAD/audio descriptor fields, sink info, and channel allocation.
- Test audio enable/disable, format-change, and hotplug paths while observing `AUDIO_ENABLE_STATUS`, `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, `AUDIO_FORMAT_CHANGED_INT_STATUS`, and hot-plug `AUDIO_ENABLED` fields.
- Exercise stereo, multichannel, and HBR audio modes to validate multichannel enable/mute/channel-ID fields, HBR capability/enable bits, speaker/channel allocation, and IEC channel-status overrides.
- Test suspend/resume and display reset paths to confirm converter, pin, sink info, hotplug, LPIB snapshot, infoframe, interrupt, and keepalive state is restored or re-read correctly.
- For input endpoints, validate input activity, channel layout, infoframe-valid, input pin sense, channel allocation, and unsolicited-response behavior if the platform exposes those input audio paths.

## Open Cross-Chunk Questions

- The merge lane should combine this with the previous chunk to present the beginning of `AZF0ENDPOINT6_AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` accurately.
- The merge lane should combine this with the next chunk to complete `AZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL` and the remaining input endpoint 4 register groups.
- Whole-file analysis should verify the expected number of DCN 3.0.2 output and input Azalia endpoint blocks and compare generated masks/shifts against the authoritative AMD register source.
