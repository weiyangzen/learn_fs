# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 69053-71029

## Scope

This chunk covers the final 1,977 lines of the generated DCN 3.0.0 shift/mask header. It contains only preprocessor register-field constants and register grouping comments; there are no C functions, structs, enums, or executable statements in this slice.

The chunk is the tail of the `AZF0INPUTENDPOINT` register mask section for AMD display audio. It begins inside the endpoint 0 input-pin audio-widget-capability register, then defines the rest of endpoint 0 input-pin fields. It then provides complete, repeated register field definitions for `AZF0INPUTENDPOINT1` through `AZF0INPUTENDPOINT7`, and ends with the file's closing `#endif`.

## Purpose

The purpose of this header region is to describe the bit layout of DCN 3.0.0 Azalia function 0 input endpoint registers. These are HD-audio codec-style registers exposed through the GPU display audio path. Driver code combines these `__SHIFT` and `_MASK` constants with register-offset definitions from the companion offset header and with AMD display register helper macros to read, write, or compose specific fields without hard-coding numeric bit positions in implementation files.

At a higher level, the section models eight hardware input endpoints. For each endpoint, the generated macros describe:

- Input converter widget capabilities, format controls, stream/channel routing, digital-converter flags, stream format support, and supported sample size/rate capabilities.
- Input pin widget capabilities and pin capabilities, including HDMI/DP capability bits, jack/presence related fields, and output/input capability flags.
- Pin controls for unsolicited responses, input-pin sense, widget input enable, multichannel routing, high-bit-rate audio capability/enable, channel allocation, hot-plug audio enable state, forced unsolicited responses, default configuration, link-position snapshots, input activity state, and audio infoframe contents.

This file is part of the generated hardware contract. Its correctness matters because display audio programming code generally consumes the symbolic field names through macro concatenation rather than checking masks manually.

## Important APIs, Types, And Constants

There are no callable APIs or local types in this chunk. The exported interface is the macro namespace:

- `AZF0INPUTENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT`: bit offset for a field in a specific input endpoint register.
- `AZF0INPUTENDPOINT<n>_<REGISTER>__<FIELD>_MASK`: 32-bit mask for the same field.
- Register comments such as `//AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME` group each field set.
- Address-block comments such as `// addressBlock: azf0inputendpoint7_inputendpointind` identify the generated register block for each endpoint.

The complete endpoint blocks in this chunk are endpoints 1 through 7. Endpoint 0 is partial because previous lines already defined its input-converter register fields and the first input-pin audio-widget capability shifts. Within each complete endpoint, the key register families are:

- `AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: exposes widget capability flags such as channel capability, input/output amplifier presence, format override, stripe, processing widget, unsolicited response capability, connection list, digital, power control, LR swap, delay, and widget type.
- `AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`: encodes stream format fields including number of channels, bits per sample, sample base divisor, sample base multiple, sample base rate, and stream type.
- `AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID`: maps a converter to `CHANNEL_ID` and `STREAM_ID`.
- `AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`: describes digital converter control and IEC-style status bits such as `DIGEN`, validity/config/preemphasis/copy/non-audio/professional flags, category code, and keepalive.
- `AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_STREAM_FORMATS` and `SUPPORTED_SIZE_RATES`: full stream-format capability mask plus separate audio rate and bit-depth capability masks.
- `AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: pin widget capabilities, similar to converter widget capabilities but without `FORMAT_OVERRIDE`.
- `AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_CAPABILITIES`: pin capability fields for impedance sense, trigger requirement, jack detection, headphone drive, input/output capability, balanced I/O, HDMI, VREF control, EAPD, and DP.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE`: unsolicited response `TAG` and `ENABLE` fields.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_INPUT_PIN_SENSE`: 31-bit impedance sense plus the high `PRESENCE_DETECT` bit.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_WIDGET_CONTROL`: input widget enable bit.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2`: per-channel enable, mute, and channel-ID fields for multichannel indices 0-7.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_HBR`: high-bit-rate capability and enable fields.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_CHANNEL_ALLOCATION`: 8-bit channel allocation field.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL`: clock-gating disable, clock-on state, and high-bit `AUDIO_ENABLED`.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE_FORCE`: forced unsolicited response payload and force trigger bit.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`: HD-audio default pin configuration fields, including sequence, association, misc, color, connection type, default device, location, and port connectivity.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`, `LPIB`, and `LPIB_TIMER_SNAPSHOT`: lock/wrap-count and 32-bit link-position snapshot fields.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL`: input activity, channel layout, and unsolicited-response enables for activity and channel-status/infoframe changes.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME`: channel count, channel allocation, byte 5, and infoframe-valid fields.

The repeated endpoint shape is mechanically consistent: complete endpoints 1 through 7 each contribute 232 `#define` entries, while endpoint 0 contributes only the remaining 153 entries present in this chunk because its earlier converter fields precede line 69053.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time macro expansion:

1. C files include this generated shift/mask header, usually with the matching offset header for DCN 3.0.0 register addresses.
2. Register helper macros concatenate a register name and field name to resolve `__SHIFT` and `_MASK` constants.
3. Runtime driver code uses the resolved values in MMIO read/modify/write helpers or generated register-field tables.

The ordering is still semantically useful for maintainers and generators. Each register section generally lists all `__SHIFT` values first and then all `_MASK` values. Endpoint blocks are ordered numerically, and fields within a complete endpoint follow the HD-audio input converter and input pin register sequence.

## State And Persistence Behavior

The header itself stores no software state and persists no data. It describes hardware register state owned by the GPU display audio block:

- Converter state includes selected audio stream format, channel count, sample rate/base parameters, channel and stream IDs, digital converter flags, keepalive, and advertised format/rate capabilities.
- Pin state includes capabilities and policy fields that report or control audio presentation through HDMI/DisplayPort style endpoints.
- Unsolicited response fields control whether hardware can report asynchronous activity or configuration changes and which tag is used for those events.
- Input pin sense and presence fields report physical or logical endpoint status, including the high-bit `PRESENCE_DETECT` indicator.
- Multichannel enable and mute fields determine how up to eight channel slots are enabled and mapped.
- Hot-plug control contains clock-gating and audio-enable state; wrong bit definitions here can leave audio disabled or clocks held on/off incorrectly.
- LPIB and timer snapshot fields expose hardware playback/capture position style state, including a snapshot lock and cyclic-buffer wrap count.
- Infoframe and input-status fields expose current channel layout/activity and HDMI/DP audio infoframe data validity.

Persistence is hardware-defined. Writes to these registers can remain effective until another driver write, a display/audio reset, or an ASIC reset. Read-only capability and status fields must not be treated as writable simply because this generated header provides masks for them.

## Dependencies And Integration Points

This chunk depends on the generated DCN register model staying synchronized across several files:

- `dcn_3_0_0_offset.h` supplies the register offsets that pair with these field masks.
- `dcn_3_0_0_sh_mask.h` supplies the field layout consumed by AMD display register macros such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.
- Adjacent generated enum headers, for example `soc24_enum.h`, define symbolic values for many similarly named Azalia codec fields. Those enums provide meaning for field values, while this header provides bit placement.
- AMD display audio, DMUB, and DC register-table code can include this header indirectly when building DCN 3.0 register access tables.

The direct integration point is not a function call; it is the preprocessor name contract. Consumer code must spell the same generated register and field names used here. Any rename or missing define breaks macro expansion at build time, while a wrong numeric mask can compile successfully but corrupt MMIO behavior.

The section also integrates conceptually with the Linux DRM/ALSA display-audio path: hotplug, HDMI/DP audio capability exposure, channel allocation, infoframe validity, and stream-format programming all depend on these hardware fields matching the DCN 3.0.0 register specification.

## Risks And Edge Cases

- This chunk begins mid-register for endpoint 0. Whole-file reconciliation must combine it with the prior chunk to avoid falsely reporting endpoint 0 as missing converter fields or initial pin-widget shifts.
- The endpoint blocks are highly repetitive. Copy/generator drift in a single endpoint could be hard to see in review but would affect only one hardware endpoint at runtime.
- Numeric mask errors compile cleanly if the macro names still exist. A shifted `AUDIO_ENABLED`, `PRESENCE_DETECT`, `INFOFRAME_VALID`, or multichannel `CHANNEL_ID` field can produce silent display-audio failures.
- Some masks cover full 32-bit values, such as stream formats, LPIB, and timer snapshots. Callers need width-safe arithmetic and should avoid signed interpretation of full-register masks.
- Several fields are capability/status fields rather than normal writable controls. Register helpers do not encode access permissions, so caller correctness depends on the hardware programming model.
- `UNSOLICITED_RESPONSE_FORCE` can synthesize events. Using the force bit accidentally in a read/modify/write path could generate spurious audio or hotplug-related notifications.
- Multichannel enable and mute fields pack four channel slots per register. Incorrect channel-ID masks can cross-contaminate adjacent channel slot settings.
- Cross-ASIC reuse is risky. Similar Azalia endpoint field names appear in other generated AMD ASIC headers, but field coverage or semantics can vary by generation.
- The file ends at the include guard immediately after endpoint 7 infoframe masks. Any generator truncation here would likely surface as missing endpoint 7 or missing `#endif`, so keeping this tail stable is a basic structural integrity signal.

## Test Signals

Useful validation signals for this header are build-time and hardware-integration oriented:

- Compile AMD DCN 3.0 display code with `W=1` or equivalent warning coverage to catch missing generated field names in macro expansions.
- Preprocess or compile representative register-table users that expand `FD_MASK` and `FD_SHIFT` for Azalia/input-endpoint fields.
- Compare this header against `dcn_3_0_0_offset.h` and the register generator source to confirm every endpoint register with fields has matching shift and mask definitions.
- Exercise HDMI and DisplayPort audio enumeration on DCN 3.0 hardware, checking that endpoint capability reporting, stream format/rate reporting, and pin default configuration are sane.
- Run hotplug and audio enable/disable tests across connectors, watching `AUDIO_ENABLED`, unsolicited response behavior, and infoframe-valid status.
- Test multichannel audio modes, including channel allocation and 8-channel enable/mute/channel-ID programming.
- Validate high-bit-rate audio paths where `HBR_CAPABLE` and `HBR_ENABLE` are expected to be used.
- Exercise suspend/resume and display reset paths to catch stale converter, pin, hotplug, LPIB snapshot, or infoframe state after hardware reinitialization.

## Open Cross-Chunk Questions

- The final per-file report should merge this with the previous chunk to present endpoint 0 as a complete block.
- Whole-file reconciliation should verify that the generated endpoint count and field layout match the hardware specification for DCN 3.0.0, not just nearby ASIC headers.
- If the repository keeps generation provenance, the final report should identify whether these masks are imported from AMD register database output or hand-maintained snapshots, because manual edits would be unusually high risk.
