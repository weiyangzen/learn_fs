# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 56930-59302

## Scope

This chunk is a generated register field header slice from the AMD DCN 3.0.2 ASIC register tables. It contains C preprocessor `#define` constants for bit shifts and masks, not executable functions. The specific range spans the tail of Azalia endpoint 1 pin/audio fields, the complete repeated field maps for Azalia endpoints 2 through 5, and the start of endpoint 6 converter widget capability fields.

The slice defines 2046 shift/mask macros across 313 endpoint-specific register blocks. The naming pattern is:

`AZF0ENDPOINT<N>_<REGISTER>__<FIELD>__SHIFT` and `AZF0ENDPOINT<N>_<REGISTER>__<FIELD>_MASK`

where `N` is an Azalia audio endpoint instance and `<REGISTER>` names an indirectly addressed HDMI/DP audio codec endpoint register.

## Purpose

The purpose of this header range is to give the display/audio driver exact bit positions for DCN 3.0.2 Azalia codec endpoint registers. The masks are consumed by register helper macros such as `SF()`, `FN()`, `REG_SET()`, `REG_GET()`, and `set_reg_field_value()` through resource-specific shift/mask tables. They prevent hard-coded bit arithmetic in the audio implementation and keep the driver aligned with the generated ASIC register specification.

In the wider DCN 3.0.2 integration, `dcn302_resource.c` includes both `dcn_3_0_2_offset.h` and this `dcn_3_0_2_sh_mask.h`. It creates `audio_regs[]` for audio instances 0 through 6 and initializes `struct dce_audio_shift` / `struct dce_audio_mask` from the generated symbols. Runtime Azalia access is performed by `dce_audio.c`, which writes an endpoint index register and then reads or writes endpoint data.

## Important Register Families

This chunk is dominated by repeated endpoint-local register families:

- `AZF0ENDPOINT1_*`: tail of endpoint 1 pin control fields. The chunk begins after `SINK_INFO8` has already started in the previous chunk, then covers hot-plug control, forced unsolicited responses, default pin configuration, multichannel controls, IEC 60958 channel status overrides, LPIB snapshot state, format-change state, remote keepalive, and audio enable/disable/format-change interrupt status.
- `AZF0ENDPOINT2_*`, `AZF0ENDPOINT3_*`, `AZF0ENDPOINT4_*`, `AZF0ENDPOINT5_*`: complete repeated maps for four Azalia codec endpoints. These include converter capability/control fields, pin capability/control fields, descriptor fields, sink information fields, channel status overrides, LPIB state, and interrupt/status fields.
- `AZF0ENDPOINT6_*`: start of endpoint 6, covering `CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` through the beginning of `CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT`; the rest of endpoint 6 continues in the next chunk.

The main field groups are:

- Converter capabilities and format: `AUDIO_CHANNEL_CAPABILITIES`, amplifier presence/override flags, `FORMAT_OVERRIDE`, `STRIPE`, `PROCESSING_WIDGET`, `UNSOLICITED_RESPONSE_CAPABILITY`, `CONNECTION_LIST`, `DIGITAL`, `POWER_CONTROL`, `LR_SWAP`, widget delay, type, `NUMBER_OF_CHANNELS`, `BITS_PER_SAMPLE`, sample base divisor/multiple/rate, and stream type.
- Converter stream routing: `STREAM_ID`, `CHANNEL_ID`, digital converter enable/validity, category code, pre-emphasis, copy/level flags, professional/consumer status, and V-bit or validity behavior.
- Timing and GTC: `GTC_EMBEDDING_ENABLE`, `GTC_EMBEDDING_GROUP`, `GTC_EMBEDDING_HBR_AUDIO_PACKET_ALIGN`, and counter delta/min/max fields.
- Pin capabilities and controls: impedance/presence detect, trigger requirement, HDMI/DP/HBR support bits, unsolicited response tag/enable, pin sense, widget enable, channel/speaker allocation, and multiple CEA-like audio descriptor fields.
- Multichannel and speaker mapping: base `MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2` fields encode enable/mute/channel-id triplets for odd channel lanes 1/3/5/7 and related channel layout state.
- Sink and descriptor metadata: audio descriptors 0-13, `SINK_INFO0` through `SINK_INFO8`, manufacturer/product/port IDs, sink description bytes, and default configuration fields such as sequence, default association, color, connection type, default device, location, and port connectivity.
- IEC 60958 channel status overrides: `PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8` cover source number, clock accuracy, word length, sampling frequency, original frequency, sampling-frequency coefficient, MPEG surround, CGMS-A, and channel numbers.
- Runtime/status fields: hot-plug clock gating and `AUDIO_ENABLED`, `OUTPUT_ACTIVE`, `LPIB`, `LPIB_TIMER_SNAPSHOT`, cyclic buffer wrap count, coding type, format-change reason/response, wireless display identification, remote keepalive capability, and enabled/disabled/format-changed interrupt flag/mask/type fields.

## APIs, Types, and Macros

This slice does not declare functions, structs, enums, or storage. Its API surface is the macro namespace exported by the header.

Important consumers in the AMD display tree include:

- `dcn302_resource.c`, which includes this header and builds DCN 3.0.2 audio register descriptors. `audio_regs[]` binds per-instance MMIO endpoint index/data registers, while `audio_shift` and `audio_mask` are initialized with generated `_SHIFT` and `_MASK` constants.
- `struct dce_audio_registers`, `struct dce_audio_shift`, and `struct dce_audio_mask` in `dce_audio.h`, which carry register addresses and common field layout information into the DCE audio implementation.
- `dce_audio.c`, where `write_indirect_azalia_reg()` and `read_indirect_azalia_reg()` program `AZALIA_ENDPOINT_REG_INDEX` and `AZALIA_ENDPOINT_REG_DATA`. Higher-level audio paths then use `AZ_REG_READ()` and `AZ_REG_WRITE()` with indirect register indices such as `AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL`.

The endpoint-specific macros in this chunk are generated for all endpoints, but the common DCE audio code mostly abstracts access through the selected audio instance and generic Azalia register names. The resource layer chooses the correct instance registers, and the shift/mask table supplies the bit layout.

## Control Flow and Data Flow

There is no direct control flow in this header chunk. Runtime flow through the surrounding driver is:

1. DCN 3.0.2 resource construction includes the generated offset and sh/mask headers.
2. Resource initialization creates audio objects for available instances, using `audio_regs[inst]`, `audio_shift`, and `audio_mask`.
3. Higher layers assign audio resources to display streams based on sink EDID audio information, stream signal type, and available audio endpoints.
4. Audio configuration code uses indirect Azalia reads/writes. It first writes an endpoint register index to the endpoint index MMIO register, then reads/writes endpoint data.
5. Field helpers apply the generated shifts and masks to set fields such as `CLOCK_GATING_DISABLE`, `AUDIO_ENABLED`, descriptor fields, channel allocation, HBR capability, and lipsync/format values.

For this chunk, the most visible runtime state mutation is hot-plug/audio enable behavior. `dce_aud_az_enable()` reads `AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL`, sets `CLOCK_GATING_DISABLE` and `AUDIO_ENABLED`, writes the register, then clears clock-gating disable. `dce_aud_az_disable()` performs the inverse for `AUDIO_ENABLED`. The endpoint 1-5 hot-plug control masks in this chunk specify the exact bits used for the endpoint-local versions of that register.

## State and Persistence

The macros themselves are compile-time constants and hold no mutable state. The state they describe is hardware state in Azalia codec endpoint registers:

- Persistent while programmed: endpoint data fields such as audio descriptors, sink metadata, default configuration, channel allocation, IEC 60958 overrides, and multichannel setup stay in hardware until reprogrammed, reset, power-gated, or overwritten by another driver path.
- Volatile/status-like: pin sense, output active, LPIB snapshots, timer snapshots, audio enable status, and interrupt flag fields reflect hardware activity and can change asynchronously.
- Control/ack fields: forced unsolicited response, format-change acknowledgement/response, interrupt masks, and clock gating/audio enable fields can affect event delivery and hardware behavior.

Because this is an ASIC register definition file, persistence semantics are determined by the hardware block and the driver sequences in `dce_audio.c`, not by this header.

## Dependencies and Integration Points

This chunk depends on the generated DCN 3.0.2 register naming contract:

- Address macros from `dcn_3_0_2_offset.h` define MMIO and indirect register indices, including endpoint index/data registers and `ixAZF0ENDPOINT*` indirect indices.
- Shift/mask macros from this file define how to extract or update fields within those registers.
- Register helper infrastructure (`reg_helper.h`) uses the shift and mask structs to implement field update macros.
- DC resource files for a specific ASIC generation, especially `dcn302_resource.c`, bind generated register metadata to audio objects.
- DCE audio code (`dce_audio.c`) performs the actual HDMI/DP audio programming and status reads.

The repeated endpoint layout is an integration contract between hardware generation files and the generic audio code. If a field name changes here, the `SF()`/`FN()` expansions that expect that field name fail at compile time. If a mask value changes incorrectly, the driver can compile but program the wrong hardware bits.

## Risks and Edge Cases

- Chunk boundary risk: this range starts mid endpoint 1 sink-info sequence and ends mid endpoint 6 converter format. A final merged per-file report must reconcile this chunk with adjacent chunks to avoid treating endpoint 1 or endpoint 6 as incomplete hardware support.
- Generated-header drift: hand-editing any mask or shift can silently break audio enablement, EDID-derived audio descriptors, HBR reporting, channel mapping, or interrupt behavior.
- Endpoint repetition risk: endpoint 2 through 5 definitions are structurally identical by design. Copy/generation errors for a single endpoint can affect only that audio instance and may appear as connector-specific audio failure.
- Indirect register access risk: the endpoint register data path relies on writing the correct index before data access. Wrong `ix` indices from the paired offset header or wrong masks here can make reads/writes target valid but unintended fields.
- Status/control overlap: fields such as `FORMAT_CHANGED`, interrupt flags/masks, and `AUDIO_ENABLED` can be touched by hotplug, stream reconfiguration, and interrupt handling paths. Incorrect masks can leave interrupts stuck, suppress notifications, or report stale audio state.
- Hardware-variant risk: this file is specific to DCN 3.0.2. Sharing assumptions with nearby generations such as DCN 3.0.1, 3.0.3, or 3.2.x should be validated against their own generated headers.

## Test Signals

Useful validation signals for changes involving this header or its consumers:

- Build the AMDGPU display driver with DCN 3.0.2 resource support enabled; field name mismatches in `SF()`/`FN()` initializers should fail compilation.
- Exercise HDMI/DP audio on hardware using audio instances corresponding to endpoints 1 through 6, including plug/unplug and stream reconfiguration.
- Confirm `AUDIO_ENABLED` transitions by checking driver logs around `dce_aud_az_enable()` and `dce_aud_az_disable()` or by reading the Azalia hot-plug control endpoint register.
- Validate EDID audio descriptor propagation for LPCM and compressed formats, channel counts, sample rates, HBR capability, speaker allocation, sink name/manufacturer/product metadata, and lipsync fields.
- Test multichannel and HBR audio paths because this chunk contains both base and secondary multichannel enable fields plus HBR response/capability masks.
- Check interrupt behavior for audio enabled, audio disabled, and audio format changed status fields; stuck or missing events can indicate incorrect flag/mask/type bit definitions.
- Compare generated masks against the ASIC register source or a known-good generated header when updating DCN 3.0.2 register files.

## Summary

Lines 56930-59302 of `dcn_3_0_2_sh_mask.h` are a generated DCN 3.0.2 Azalia endpoint field map. They provide the bit-level contract for HDMI/DP audio endpoint registers, especially endpoints 2 through 5 and boundary portions of endpoints 1 and 6. The driver integrates these constants through DCN 3.0.2 resource initialization and the generic DCE audio indirect-register path; correctness is primarily validated by compile-time field expansion plus runtime HDMI/DP audio, hotplug, descriptor, multichannel, HBR, and interrupt behavior.
