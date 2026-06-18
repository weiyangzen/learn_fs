# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 49550-51891

## Scope

This chunk covers 2,342 lines from the generated DCN 3.0.1 shift/mask header. It contains only C preprocessor constants and register grouping comments; there are no functions, structs, enums, storage objects, or executable statements in this slice.

The chunk is part of the AMD display Azalia function 0 register field map. It starts in the middle of the `AZF0ENDPOINT4` output endpoint block, covers complete `AZF0ENDPOINT5`, `AZF0ENDPOINT6`, and `AZF0ENDPOINT7` output endpoint blocks, then transitions to input endpoint blocks. It includes complete `AZF0INPUTENDPOINT0` and `AZF0INPUTENDPOINT1` blocks and ends at the first field of `AZF0INPUTENDPOINT2_AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`. The section contains 2,037 `#define` entries, split almost evenly between `__SHIFT` and `_MASK` definitions, across 288 grouped register names.

## Purpose

The purpose of this header region is to describe bit positions and masks for DCN 3.0.1 display-audio hardware registers. These generated constants let AMDGPU display code address HD-audio/Azalia codec-style converter and pin fields by symbolic name instead of embedding raw bit arithmetic in implementation files.

For output endpoints, the chunk describes:

- Converter capabilities, stream format fields, stream/channel routing, digital converter flags, stream-format support, size/rate capabilities, stripe/ramp/GTC controls, and GTC counter deltas.
- Pin widget capabilities and pin controls for channel/speaker mapping, audio descriptors, multichannel routing, lipsync, HBR, sink information, hot-plug state, forced unsolicited responses, default configuration, IEC 60958 channel-status overrides, LPIB snapshots, coding type, format-change status, wireless display identification, remote keepalive, audio enable state, and audio enable/disable/format-change interrupt status.

For input endpoints, the chunk describes:

- Input converter capabilities, format selection, stream/channel IDs, digital converter flags, supported stream formats, and supported audio size/rate fields.
- Input pin capabilities and controls for unsolicited responses, input pin sense, widget input enable, multichannel routing, HBR, channel allocation, hot-plug audio state, forced unsolicited responses, default configuration, LPIB snapshots, input status, and audio infoframe fields.

This is a hardware contract file. Its value is not algorithmic behavior but precise, stable naming and numeric field layout consumed by register helper macros elsewhere in the AMD display stack.

## Important APIs, Types, And Constants

There are no callable APIs or types in this chunk. The exported interface is the macro naming scheme:

- `AZF0ENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT` gives a field bit offset for an output endpoint register.
- `AZF0ENDPOINT<n>_<REGISTER>__<FIELD>_MASK` gives the corresponding field mask.
- `AZF0INPUTENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT` and `_MASK` provide the same contract for input endpoint registers.
- Comments such as `// addressBlock: azf0endpoint5_endpointind` and `//AZF0ENDPOINT5_AZALIA_F0_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT` group generated constants by hardware block and register.

The output endpoint blocks in this chunk follow a repeated register family:

- `AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` exposes channel, amplifier, format override, stripe, processing, unsolicited response, connection-list, digital, power-control, LR-swap, delay, and type capability fields.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT` maps the audio stream format fields: number of channels, bits per sample, sample base divisor, sample base multiple, sample base rate, and stream type.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_CHANNEL_STREAM_ID` maps channel ID and stream ID fields.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_DIGITAL_CONVERTER` covers digital converter enable/status bits such as `DIGEN`, validity/config/preemphasis/copy/non-audio/professional flags, category code, and `KEEPALIVE`.
- `AZALIA_F0_CODEC_CONVERTER_PARAMETER_STREAM_FORMATS` and `SUPPORTED_SIZE_RATES` expose format, sample-rate, and bit-depth capability masks.
- `AZALIA_F0_CODEC_CONVERTER_STRIPE_CONTROL`, `CONTROL_RAMP_RATE`, `CONTROL_GTC_EMBEDDING`, and `GTC_COUNTER_DELTA*` describe converter timing and packing controls.
- `AZALIA_F0_CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `PIN_PARAMETER_CAPABILITIES` describe pin-side widget and pin capabilities, including HDMI/DP, presence-detect, trigger, EAPD, VREF, input/output, and balanced I/O flags.
- `AZALIA_F0_CODEC_PIN_CONTROL_CHANNEL_SPEAKER`, `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, `MULTICHANNEL_ENABLE`, and `MULTICHANNEL_ENABLE2` describe audio channel mapping, SAD-like descriptor data, and per-channel enable/mute/channel-ID slots.
- `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_LIPSYNC`, `RESPONSE_HBR`, and `SINK_INFO0` through `SINK_INFO8` expose sink latency, high-bit-rate audio, manufacturer/product/port, string, connection, and converter-identification fields.
- `AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8` define IEC 60958 channel-status override fields for mode, source number, clock accuracy, word length, sampling frequency, original sampling frequency, CGMS-A, MPEG surround, and channel numbers 0-7.
- `AZALIA_F0_AUDIO_ENABLE_STATUS`, `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS` provide audio state and interrupt flag/mask/type field definitions.

The input endpoint blocks use a smaller but related register family:

- `AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`, `INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID`, `INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`, `INPUT_CONVERTER_PARAMETER_STREAM_FORMATS`, and `INPUT_CONVERTER_PARAMETER_SUPPORTED_SIZE_RATES` mirror the converter-side output endpoint fields with input endpoint naming.
- `AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `INPUT_PIN_PARAMETER_CAPABILITIES` describe input pin widget and pin capabilities.
- `INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE`, `RESPONSE_INPUT_PIN_SENSE`, `WIDGET_CONTROL`, `MULTICHANNEL_ENABLE`, `MULTICHANNEL_ENABLE2`, `RESPONSE_HBR`, `CHANNEL_ALLOCATION`, `HOT_PLUG_CONTROL`, `UNSOLICITED_RESPONSE_FORCE`, `RESPONSE_CONFIGURATION_DEFAULT`, `LPIB*`, `INPUT_STATUS_CONTROL`, and `INFOFRAME` cover input-side status, routing, default configuration, snapshot, and infoframe state.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time macro resolution:

1. A DCN 3.0.1 source file includes this header together with the matching register-offset header.
2. AMD display register helpers concatenate a register token and field token to resolve a `__SHIFT` or `_MASK` constant.
3. Runtime code uses the resolved constants in MMIO read/modify/write sequences or register-table initialization.

The ordering still carries generated-structure meaning. The chunk starts with the remaining output endpoint 4 pin/audio status fields, then enumerates complete output endpoints 5-7 in ascending endpoint order. It then starts the input endpoint register space, with complete input endpoints 0-1 and the beginning of input endpoint 2. Within each register group, shift definitions generally precede mask definitions for the same fields.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes hardware state in the GPU display audio block:

- Converter control fields represent programmed audio stream shape, stream/channel association, IEC/digital converter flags, keepalive, stripe/ramp behavior, and GTC embedding/counter relationships.
- Capability fields represent hardware-advertised audio widget, pin, stream format, and sample size/rate support. These are typically read-oriented even though the header only encodes bit placement, not access permissions.
- Output pin control fields represent HDMI/DP-style audio presentation state: speaker/channel mapping, audio descriptors, lipsync, HBR enablement, sink identity data, sink connection data, hot-plug audio enable state, and remote keepalive.
- IEC 60958 channel-status override fields can change transmitted channel-status metadata such as sampling frequency, word length, source number, clock accuracy, CGMS-A, and channel numbers.
- LPIB and timer snapshot fields represent hardware position/timing state, with snapshot lock and cyclic-buffer wrap count fields.
- Interrupt status fields represent audio enabled, disabled, and format-changed flag/mask/type state.
- Input pin fields represent input activity, channel layout, infoframe contents, input pin sense, unsolicited response setup, and multichannel channel-slot routing.

Persistence is hardware-defined. A write to a writable control field may survive until the next driver update, audio/display block reset, or ASIC reset. Read-only status and capability fields can be masked by the same helpers as writable fields, so callers must rely on the hardware programming model rather than this header to decide legal access direction.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.0.1 register set staying synchronized across related files:

- The matching DCN 3.0.1 offset header supplies register addresses for the register names whose fields are defined here.
- AMD display register helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT` consume the `__SHIFT` and `_MASK` suffix conventions.
- Generated enum/value headers and hardware specs provide semantic values for fields such as stream format, widget type, pin configuration, channel allocation, and IEC channel-status fields.
- DRM display audio and ALSA-facing HDMI/DisplayPort audio paths integrate with these definitions when programming or reading GPU display audio endpoints.

The most important integration point is the preprocessor name contract. Missing or renamed macros usually fail at compile time, but wrong numeric masks or shifts can compile cleanly and produce incorrect MMIO accesses. The repeated endpoint shape also implies that generator consistency matters across endpoint instances.

## Risks And Edge Cases

- The chunk starts mid-output-endpoint 4 and ends mid-input-endpoint 2. Final per-file reconciliation must merge adjacent chunks before making whole-endpoint completeness claims.
- The output endpoint blocks are mechanically repetitive. A single endpoint-specific generator drift can be difficult to spot because most lines differ only by endpoint number.
- Shift/mask mismatches are high risk: a bad high-bit field such as `AUDIO_ENABLED`, `PRESENCE_DETECT`, or `INFOFRAME_VALID` would not necessarily be caught by compilation.
- Several full-register masks use `0xFFFFFFFFL`, including association info, LPIB, timer snapshots, stream formats, and GTC deltas. Callers need unsigned-width-safe handling.
- Capability/status fields and control fields share the same macro style. This header does not prevent software from attempting writes to read-only fields.
- `UNSOLICITED_RESPONSE_FORCE` fields can synthesize events. Accidental writes to the force bit could create misleading hotplug or audio notifications.
- Multichannel enable registers pack enable, mute, and channel-ID fields for four channel slots per register. Incorrect masks can cross into adjacent channel slot fields.
- IEC channel-status override fields include paired override-enable bits for some metadata. Programming a value without the matching enable bit, or using the wrong endpoint's override field, can silently leave transmitted metadata unchanged.
- Cross-generation reuse is risky. DCN 3.0.0 and DCN 3.0.1 have similar Azalia names, but consumers should include the ASIC-specific header that matches the register offsets used for the target hardware.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration oriented:

- Compile the DCN 3.0.1 AMD display code that includes this header to catch missing macro names in register-helper expansions.
- Preprocess representative users of `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE` for Azalia output/input endpoint fields to verify the expected macros resolve.
- Compare this header against the generated offset header and the register database to ensure every endpoint register has matching field definitions and that no endpoint block is truncated.
- Exercise HDMI and DisplayPort audio enumeration on DCN 3.0.1 hardware, checking advertised pin/widget capabilities, SAD/audio descriptor data, stream format/rate support, sink info, and channel allocation.
- Test audio enable/disable, format-change, and hotplug paths while watching the audio enable status and interrupt status fields.
- Exercise stereo, multichannel, and HBR audio modes to validate multichannel enable/mute/channel-ID fields, HBR capability/enable bits, and IEC channel-status overrides.
- Test suspend/resume and display reset paths to confirm converter, pin, hotplug, LPIB snapshot, infoframe, and interrupt state is restored or re-read correctly.
- For input endpoints, validate input activity, infoframe-valid, channel-layout, input pin sense, and unsolicited-response behavior if the hardware path exposes those features.

## Open Cross-Chunk Questions

- The later merge lane should combine this with the previous chunk to present endpoint 4 as a complete output endpoint block.
- The later merge lane should combine this with the next chunk to present `AZF0INPUTENDPOINT2` as a complete input endpoint block.
- Whole-file analysis should verify whether all expected output and input endpoint counts for DCN 3.0.1 are present and whether generated field layouts match the authoritative AMD register source.
