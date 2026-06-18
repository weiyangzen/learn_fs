# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 5539-7886

## Scope And Purpose

This chunk covers lines 5539-7886 of the generated AMD DCN 4.2.0 shift/mask header. It contains register-field constants for the Azalia/HDA display-audio endpoint indirect-register blocks. The range starts in the middle of `AZF0ENDPOINT4` pin-control multichannel definitions, then covers the tail of output endpoint 4, complete output endpoints 5-7, complete input endpoint 0, and the beginning of input endpoint 1 through `AZF0INPUTENDPOINT1_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_HBR`.

The file is not executable driver logic. Its purpose is to publish the hardware bit layout used by AMDGPU Display Core register helpers: `REGISTER__FIELD__SHIFT` gives a bit position, and `REGISTER__FIELD_MASK` gives the already-positioned bit mask. Companion offset definitions in `dcn_4_2_0_offset.h` provide the endpoint index/data register addresses and indirect register indices; this header supplies the field extraction and update constants.

This assigned range contains 2,348 source lines, 2,045 `#define` lines, 1,018 shift definitions, 1,027 mask definitions, 293 comment/register markers, and five address-block markers.

## Register Families In This Chunk

The covered output endpoint families are `AZF0ENDPOINT4`, `AZF0ENDPOINT5`, `AZF0ENDPOINT6`, and `AZF0ENDPOINT7`. Endpoint 4 is partial because earlier lines contain its converter and pin blocks; endpoints 5-7 are complete output endpoint maps in this chunk. Each full output endpoint exposes:

- Converter capabilities and controls: audio widget capabilities, converter format, channel/stream ID, digital converter status/control bits, supported stream formats, supported size/rate capabilities, stripe control, and ramp rate.
- Pin widget capabilities and controls: pin audio widget capabilities, HDMI/DP pin capabilities, unsolicited response enable/tag, pin sense, widget output enable, speaker/channel mapping, ACP packet data, audio descriptor registers, multichannel enable and channel-ID fields, HBR/lipsync response fields, sink information, hot-plug/audio enable status, forced unsolicited response, and default configuration response.
- IEC 60958 channel-status override registers `CODEC_CS_OVERRIDE_0` through `CODEC_CS_OVERRIDE_8`, covering mode/source number, clock accuracy, word length, sampling frequency, original sampling frequency, CGMS-A, channel numbers, and channel status validity bits.
- Runtime endpoint status fields for audio enablement, enabled/disabled interrupts, format-changed interrupts, and fine-grain clock-gating repeat-disable.

The covered input endpoint families are `AZF0INPUTENDPOINT0` and the first part of `AZF0INPUTENDPOINT1`. Input endpoint 0 is complete in this chunk; input endpoint 1 continues into the following chunk. These input blocks expose input converter format, stream/channel ID, digital converter status bits, supported formats/rates, input pin capabilities, input pin sense, input enable, multichannel layout, HBR response, channel allocation, hot-plug/audio enable, forced unsolicited response, default configuration, LPIB snapshots, input activity/channel-layout status, and captured infoframe fields.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or callable APIs declared here. The interface is the generated macro naming contract:

- `AZF0ENDPOINT<n>_AZALIA_F0_<REGISTER>__<FIELD>__SHIFT`
- `AZF0ENDPOINT<n>_AZALIA_F0_<REGISTER>__<FIELD>_MASK`
- `AZF0INPUTENDPOINT<n>_AZALIA_F0_<REGISTER>__<FIELD>__SHIFT`
- `AZF0INPUTENDPOINT<n>_AZALIA_F0_<REGISTER>__<FIELD>_MASK`

The most important field groups are:

- Format fields: `NUMBER_OF_CHANNELS`, `BITS_PER_SAMPLE`, `SAMPLE_BASE_DIVISOR`, `SAMPLE_BASE_MULTIPLE`, `SAMPLE_BASE_RATE`, and `STREAM_TYPE` describe the HDA converter stream format word.
- Stream routing fields: `CHANNEL_ID`, `STREAM_ID`, multichannel `*_ENABLE`, `*_MUTE`, and `*_CHANNEL_ID` fields connect codec channel widgets to HDA streams and logical speaker/channel placement.
- Digital audio status fields: `DIGEN`, validity/configuration bits, pre-emphasis, copy/non-audio/professional mode, level, channel-status category/code fields, and `KEEPALIVE` describe IEC 60958/HDMI/DP audio stream metadata.
- Sink and descriptor fields: audio descriptors encode channel count, sample rates, byte offsets, and sample sizes. Sink info fields encode manufacturer/product IDs, port IDs, and up to 18 bytes of sink description.
- Event and status fields: unsolicited response enable/force, pin sense/presence detect, hot-plug audio enabled, enabled/disabled/format-changed interrupt masks, input activity, channel layout, and infoframe valid bits.
- Position reporting fields: `LPIB`, `LPIB_SNAPSHOT_LOCK`, `CYCLIC_BUFFER_WRAP_COUNT`, and timer snapshots expose audio DMA position tracking for output and input endpoints.

The constants are consumed through AMD register helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, `FD_SHIFT`, and structure initializers that build per-block mask/shift tables.

## Control Flow And Hardware Behavior

This header has no local control flow. It participates in control flow when AMDGPU display/audio code includes the generated offset and shift/mask headers and performs register operations.

The HDA/Azalia endpoint model is indirect: `dcn_4_2_0_offset.h` defines per-endpoint index and data registers such as `regAZF0ENDPOINT5_AZALIA_F0_CODEC_ENDPOINT_INDEX`, `regAZF0ENDPOINT5_AZALIA_F0_CODEC_ENDPOINT_DATA`, `regAZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX`, and `regAZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_ENDPOINT_DATA`. It also defines matching indirect register indices such as `ixAZF0ENDPOINT5_AZALIA_F0_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT` and `ixAZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME`. Callers select an indirect endpoint register through the index register, then read or write the data register using the masks and shifts from this chunk.

Driver-side behavior is therefore a sequence of register-table setup, indirect register selection, field extraction/update, and hardware response polling or interrupt handling. Converter format fields control how an HDA stream is interpreted. Pin and multichannel fields determine which endpoint channels are enabled, muted, or mapped. Status and interrupt fields expose changes such as audio enabled/disabled and format changes. LPIB fields let software snapshot audio buffer progress without racing a live hardware counter.

## State And Persistence Behavior

The header itself has no runtime state and persists no data. It is a compile-time hardware ABI description.

The underlying registers are hardware-resident state. Some fields are configuration that persists until reset or a later write, such as stream format, channel stream ID, digital converter enables, multichannel mapping, channel-status override enables, unsolicited-response enables, hot-plug/audio enable controls, and input activity unsolicited-response enables. Other fields are status or latched event state, such as pin sense, HBR capability/enable response, audio enabled status, interrupt status bits, format-changed flags, LPIB values, timer snapshots, input activity, infoframe validity, and cyclic-buffer wrap counts.

The header does not encode access type, reset value, ownership, or side effects. In particular, similarly named status, mask, clear, and force fields must be interpreted through the hardware register specification and existing driver programming sequences. Reserved or undocumented bits should be preserved by read-modify-write operations.

## Dependencies And Integration Points

The direct generated dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h`, which supplies the physical endpoint index/data register offsets and indirect register indices aligned with these field masks.

Known DCN 4.2 integration points include:

- `display/dc/resource/dcn42/dcn42_resource.c`, which includes both `dcn_4_2_0_offset.h` and `dcn_4_2_0_sh_mask.h` while building DCN 4.2 display-resource register tables, including audio-related DCN/DCE components.
- `display/dmub/src/dmub_dcn42.c`, which includes this header and initializes DMUB register mask/shift tables through `FD_MASK` and `FD_SHIFT`; that file mainly uses DMCUB fields from other chunks of the same header, but it demonstrates the generated-header consumption pattern.
- `display/dc/irq/dcn42/irq_service_dcn42.c`, which includes this header for interrupt register masks and acknowledges. Audio endpoint interrupt status definitions in this chunk are part of the broader generated IRQ/status surface for DCN 4.2.
- `display/dc/gpio/dcn42/hw_factory_dcn42.c`, `display/dc/gpio/dcn42/hw_translate_dcn42.c`, and `display/dc/clk_mgr/dcn42/dcn42_clk_mgr.c`, which include the same generated header for DCN 4.2 register access infrastructure.
- Higher-level DCE audio and DCN stream-encoder code, which relies on Azalia/HDA endpoint programming to expose HDMI/DisplayPort audio capabilities, set stream formats, update channel allocation, and respond to hot-plug or sink-capability changes.

The output endpoint repetition is an integration contract: endpoints 5-7 have the same field layout, and endpoint 4 appears to share the same layout across adjacent chunks. Generic endpoint-indexed code depends on identical bit positions across endpoint instances. Input endpoints use a related but distinct input-specific layout with `INPUT_CONVERTER` and `INPUT_PIN` names.

## Risks And Edge Cases

- A wrong mask or shift silently targets the wrong hardware bit. For audio this can manifest as missing HDMI/DP audio, wrong channel count, swapped or muted channels, invalid channel-status metadata, failed HBR audio, or broken sink capability reporting.
- The line range starts and ends inside repeated endpoint families. Endpoint 4 and input endpoint 1 are partial in this chunk, so final per-file analysis must merge adjacent chunks before concluding that fields are absent.
- Output endpoint and input endpoint names are similar but not interchangeable. Accidentally using `AZF0ENDPOINT` masks for `AZF0INPUTENDPOINT` registers, or vice versa, can corrupt unrelated indirect endpoint state.
- The endpoint index/data access model makes address/mask alignment critical. A correct field mask applied after selecting the wrong indirect index still reads or writes the wrong codec register.
- Interrupt and unsolicited-response fields have enable, force, payload, and status-like names. Confusing those semantics can drop hot-plug/audio events or generate unexpected unsolicited responses.
- Full-width masks such as `0xFFFFFFFFL` for LPIB, timer snapshot, stream formats, port IDs, and description/descriptor payload fields require callers to preserve only the intended field ownership and avoid assuming narrower values.
- Channel-status override registers include paired value and override-enable fields. Enabling stale override values can advertise the wrong sampling frequency, word length, channel number, or content metadata to an HDMI/DP sink.
- The generated header lacks access policy. Some fields may be read-only, write-only, sticky, self-clearing, firmware-owned, or affected by power state; callers cannot infer that from `_SHIFT` and `_MASK` constants alone.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, generated-header consistency, and hardware audio behavior:

- Build AMDGPU display code with DCN 4.2 enabled. Missing or renamed macros should fail in users of the generated register helpers and DCN 4.2 resource/IRQ/DMUB setup.
- Run generated-register consistency checks that every `__SHIFT` field has a matching `_MASK`, masks have widths and positions compatible with their shifts, and every register family in this range has matching indirect indices in `dcn_4_2_0_offset.h`.
- Compare endpoint 5, 6, and 7 output field layouts and endpoint 0/1 input field layouts for expected bit-position symmetry.
- On DCN 4.2 hardware or simulation, exercise HDMI/DisplayPort audio enumeration, hot-plug, ELD/sink-info reporting, speaker allocation, stereo and multichannel PCM, HBR-capable streams, mute/unmute, and format changes.
- Validate LPIB and timer-snapshot behavior during active playback/capture so position reporting is monotonic and wrap-count fields behave as expected.
- Check kernel logs for AMDGPU DC audio failures, HDA codec enumeration errors, missing audio devices after hot-plug, wrong channel allocation, unsolicited-response storms, interrupt storms, and audio loss across suspend/resume or display mode changes.
