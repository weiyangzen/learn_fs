# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 57513-59880

## Scope

This chunk covers lines 57513-59880 of the AMD DCE 12.0 generated register mask header. The source is C preprocessor metadata only: it exports `__SHIFT` and `_MASK` constants for bitfields in Azalia HD-audio endpoint registers. There are no C functions, structs, enums, or executable statements in this slice.

The chunk begins in the tail of `azf0endpoint0_endpointind`, contains complete repeated blocks for `azf0endpoint1_endpointind` through `azf0endpoint4_endpointind`, and ends at the start of `azf0endpoint5_endpointind` after `AZF0ENDPOINT5_AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_PIN_SENSE` is introduced. The repeated register families describe the HDMI/DisplayPort audio codec converter and pin widgets exposed by the GPU display engine.

## Purpose

The macros let AMDGPU display/audio code address individual fields in DCE 12.0 Azalia function-0 endpoint registers without hard-coded bit arithmetic. For each endpoint, the header describes:

- Converter widget capabilities and stream format controls.
- Converter channel/stream routing, digital converter status/control bits, supported formats, supported sample sizes/rates, striping, ramp-rate, and GTC presentation-time embedding.
- Pin widget capabilities, unsolicited response controls, pin-sense response, widget control, speaker/channel allocation, ELD/audio descriptors, sink information, hot-plug/unsolicited-response forcing, configuration defaults, multichannel enable/mode fields, IEC 60958 channel-status overrides, LPIB snapshots, coding type, format-change reporting, wireless-display identification, remote keepalive, and audio enable/disable/format-change interrupt status.

These definitions are part of the low-level display register database. They are normally paired with companion address headers and accessor helpers that select the endpoint register offset, then use this file's mask/shift values to pack or extract fields.

## Important Macro Families

`AZF0ENDPOINT0_*` appears only as a continuation from the previous chunk. In this slice it completes endpoint 0 fields for wireless-display identification, remote keepalive, audio-enable status, and audio enabled/disabled/format-changed interrupt status.

`AZF0ENDPOINT1_*`, `AZF0ENDPOINT2_*`, `AZF0ENDPOINT3_*`, and `AZF0ENDPOINT4_*` are complete repeated endpoint layouts. Each instance has the same field structure with only the endpoint number changed. Important groups include:

- `AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: channel, amplifier, format override, stripe, processing, unsolicited response, connection-list, digital, power-control, LR-swap, delay, and widget type fields.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT`: number of channels, bits per sample, sample-base divisor/multiple/rate, and stream type.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_CHANNEL_STREAM_ID`: packed channel and stream IDs.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_DIGITAL_CONVERTER`: digital enable, validity/config/preemphasis/copy/non-audio/professional flags, category code, and keepalive.
- `AZALIA_F0_CODEC_CONVERTER_PARAMETER_STREAM_FORMATS` and `SUPPORTED_SIZE_RATES`: advertised HDA stream formats, sample-rate capability bits, and bit-depth capability bits.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_GTC_EMBEDDING` plus `GTC_COUNTER_DELTA`, `GTC_COUNTER_DELTA_MIN`, and `GTC_COUNTER_DELTA_MAX`: presentation-time embedding controls and full-width timing-delta counters.
- `AZALIA_F0_CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `PIN_PARAMETER_CAPABILITIES`: pin widget capability fields such as HDMI/DP indication, EAPD, VREF control, input/output support, jack detection, and widget type.
- `AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`: ELD-style audio descriptor fields, including coding type, channel count, rates, byte fields, bit rates, profile/level, and other sink descriptor bytes.
- `AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2`: per-channel enable bits and mapped channel IDs for multi-channel audio.
- `AZALIA_F0_CODEC_PIN_CONTROL_SINK_INFO0` through `SINK_INFO8`: sink metadata bytes and connection/port/sink state fields.
- `AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8`: IEC 60958 channel-status override fields for professional/consumer, audio/non-audio, copyright, category, source/channel number, clock accuracy, sample frequency, word length, CGMSA, and original frequency bits.
- `AZALIA_F0_AUDIO_ENABLE_STATUS`, `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS`: status/interrupt flag, mask, and type fields for audio state transitions.

`AZF0ENDPOINT5_*` starts a fifth repeated endpoint block but this chunk only covers its converter registers, pin audio-widget capability, pin capability register, and the declaration of the pin-sense control block. Later lines must be reconciled to capture the rest of endpoint 5.

## APIs, Types, and Functions

There are no callable APIs, type declarations, or functions. The exported interface is the generated macro naming convention:

- `REGISTER__FIELD__SHIFT` defines the bit offset for a field.
- `REGISTER__FIELD_MASK` defines the already-positioned mask for that field.
- Register comments such as `//AZF0ENDPOINT3_AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL` and address-block comments such as `// addressBlock: azf0endpoint3_endpointind` group macros by hardware block.

Several field names naturally produce macros ending in `MASK_MASK`, such as `AUDIO_ENABLED_INT_STATUS__AUDIO_ENABLED_MASK_MASK`. This is intentional: the field itself is named `AUDIO_ENABLED_MASK`, and the suffix adds the generated mask constant.

## Control Flow

This chunk has no runtime control flow. The implied caller flow is the standard register read/modify/write sequence:

1. Select an endpoint-specific Azalia register address from the matching address header.
2. Read the MMIO or indirect endpoint register.
3. Clear fields with the corresponding `_MASK` constants.
4. Insert values shifted by the matching `__SHIFT` constants.
5. Write the result, or read and decode status fields for interrupts, sink information, format changes, and timing snapshots.

Hardware behavior implied by the field names is order-sensitive outside this header. Examples include enabling unsolicited responses before expecting UR events, programming converter format/channel/stream IDs before enabling audio output, reading or locking LPIB snapshots consistently, clearing or acknowledging format-change responses, and handling audio enabled/disabled/format-changed interrupt flags with their mask/type fields.

## State and Persistence

The header stores no software state. Its constants describe persistent hardware register state for DCE Azalia endpoint widgets. State domains visible in this chunk include:

- Per-endpoint converter configuration: format, channel count, bit depth, sample-rate parameters, stream ID, digital converter flags, category code, keepalive, stripe control, ramp rate, and GTC presentation-time embedding.
- Per-endpoint pin capabilities and runtime pin state: HDMI/DP capability, unsolicited response tag/enable, presence/pin-sense response, widget control, channel speaker allocation, digital-output active status, hot-plug control, wireless-display identity, and remote keepalive.
- Sink and ELD-like metadata: audio descriptors 0-13, sink info 0-8, association info, configuration default, coding type, and HBR/lipsync response fields.
- Multichannel routing state: enable bits and channel IDs across `MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2`.
- IEC 60958 channel-status override state across override registers 0-8.
- Audio transition status: audio enable status plus interrupt flag/mask/type fields for enabled, disabled, and format-changed events.
- Timing/readback state: LPIB snapshot lock, cyclic-buffer wrap count, LPIB value, LPIB timer snapshot, and GTC counter delta/min/max values.

Persistence is in hardware registers, not in the macro file. Values remain until changed by MMIO writes, reset, power transitions, display link reconfiguration, or hardware-generated events.

## Dependencies and Integration Points

The only direct dependency is the C preprocessor. Practically, these macros integrate with:

- Companion DCE 12.0 register address headers that provide the register offsets for the same `AZF0ENDPOINT*` names.
- AMDGPU display-manager and DC code that programs HDMI/DP audio, HDA codec widgets, ELD/sink metadata, and stream routing.
- Interrupt paths that handle audio enabled, disabled, and format-change events.
- Modeset/link-configuration paths that update hot-plug state, sink info, speaker/channel allocation, HBR/lipsync response, and wireless-display or remote-keepalive fields.
- Register helper macros that combine address, mask, and shift definitions for packed field writes.

The repeated endpoint prefixes are an important integration contract. Callers choose a display/audio endpoint by selecting the matching macro family; mixing endpoint numbers would compile but access the wrong per-endpoint bit layout.

## Risks

The primary risk is silent hardware misprogramming. An incorrect shift or mask can corrupt adjacent fields, reserved bits, or per-endpoint state while still compiling cleanly.

The repeated endpoint blocks are vulnerable to copy/generation drift. Endpoint 1-4 should remain structurally identical, and endpoint 5 should continue the same pattern in the following chunk. Any mismatch may indicate either a real hardware difference or a generation error that needs confirmation against the ASIC register source.

Interrupt and status fields are especially easy to misuse. Fields named `*_FLAG`, `*_MASK`, and `*_TYPE` sit in the same register; caller code must avoid treating the mask bit as the generated C mask suffix. Format-change, unsolicited-response, hot-plug, and audio transition fields can create lost events if writes are ordered incorrectly or if status bits require write-one-to-clear semantics documented outside this header.

Full-width masks such as `0xFFFFFFFFL` appear for stream formats, GTC counters, association info, LPIB, and timer snapshots. Callers should use unsigned 32-bit values and avoid signed narrowing. Small packed fields such as 4-bit channel IDs, 6-bit tags, byte-sized sink-info fields, and IEC 60958 nibbles require range validation before packing.

Because this is generated register metadata, manual edits are high risk. Renaming awkward generated symbols, changing `L` suffixed constants, or normalizing repeated blocks by hand can break include users or desynchronize the header from the hardware database.

## Test Signals

Useful validation signals for this chunk are mostly build, static, and hardware integration checks:

- Compile coverage for AMDGPU display/audio code that includes `dce_12_0_sh_mask.h`.
- Static checks that every `__SHIFT` constant in the chunk has the corresponding `_MASK`, and that masks align with their shifts and expected widths.
- Generated-header diffing against the authoritative DCE 12.0 ASIC register specification.
- Endpoint consistency checks comparing the repeated register families for endpoints 1-4 and the continuation of endpoint 5 in the next chunk.
- HDMI/DP audio smoke tests across modesets, stream format changes, multi-channel audio, HBR audio, hot-plug, and sink re-detection.
- Runtime register readback around converter format, stream/channel ID, digital converter enable, pin widget control, speaker allocation, ELD/audio descriptors, sink info, and channel-status override programming.
- Interrupt tests that exercise audio enabled, audio disabled, and audio format changed status/mask/type fields.
- Timing diagnostics that verify LPIB snapshot behavior and GTC counter delta/min/max fields when presentation-time embedding is enabled.

## Cross-Chunk Notes

This chunk continues endpoint 0 from earlier lines and stops mid-endpoint 5. The final per-file research should reconcile adjacent chunks so that endpoint 0 and endpoint 5 are not treated as incomplete hardware blocks. Later chunks should also confirm whether additional endpoint instances follow and whether their generated layouts match the endpoint 1-4 pattern documented here.
