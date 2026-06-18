# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 34400-35366

## Scope

This chunk covers the final 967 lines of the generated DCN 3.0.3 shift/mask header. It contains only C preprocessor constants and generated grouping comments; there are no functions, structs, enums, storage objects, or executable statements in this slice.

The line range starts in the middle of the `AZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER` mask list, continues through the rest of input endpoint 4, covers complete input endpoint 5, input endpoint 6, and input endpoint 7 register-field maps, and ends with the header's closing `#endif`. The range contains 868 `#define` entries: 432 `__SHIFT` definitions and 436 `_MASK` definitions. The mask count is larger because the range begins with the remaining four endpoint-4 digital-converter masks whose shift definitions are in the previous chunk.

This is the tail of the Azalia function 0 input-endpoint portion of the DCN 3.0.3 hardware register map. Endpoint 4 is partial in this chunk; endpoints 5, 6, and 7 are complete indexed input-endpoint blocks.

## Purpose

The purpose of this header region is to provide symbolic bit positions and masks for DCN 3.0.3 display-audio input endpoint registers. AMDGPU display code can include the header with the matching DCN 3.0.3 offset header and use register helper macros to extract or update fields without embedding raw bit positions.

The covered registers describe HD-audio/Azalia-style input converter and input pin state for display audio paths. They expose the register fields for converter widget capabilities, stream format selection, stream/channel IDs, digital converter control flags, advertised stream formats and sample size/rate support, input pin capabilities, unsolicited response controls, pin sense, widget input enablement, multichannel routing, high-bit-rate audio status, channel allocation, hot-plug audio status, forced unsolicited responses, default pin configuration, LPIB snapshots, input activity status, and audio infoframe data.

This file is a hardware contract. Its important behavior is the exact macro naming and numeric bit layout consumed by ASIC-specific DCN303 register code, not local algorithmic logic.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the preprocessor naming convention:

- `AZF0INPUTENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT` gives the field bit offset for input endpoint `n`.
- `AZF0INPUTENDPOINT<n>_<REGISTER>__<FIELD>_MASK` gives the field bit mask for the same register field.
- Generated comments such as `// addressBlock: azf0inputendpoint5_inputendpointind` group constants by indexed input-endpoint register block.
- Generated comments such as `//AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME` group field macros by logical register.

The partial endpoint 4 tail includes:

- The final `AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER` masks for `PRO`, `L`, `CC`, and `KEEPALIVE`.
- `INPUT_CONVERTER_PARAMETER_STREAM_FORMATS`, a full-width stream-format bitmap.
- `INPUT_CONVERTER_PARAMETER_SUPPORTED_SIZE_RATES`, with audio rate capability bits and audio bit-depth capability bits.
- `INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, with fields for audio channel capability, amplifier presence, amplifier override, stripe, processing widget, unsolicited response capability, connection list, digital, power control, LR swap, widget delay, and type.
- `INPUT_PIN_PARAMETER_CAPABILITIES`, with impedance sense, trigger-required, jack-detection, headphone-drive, output/input capability, balanced I/O, HDMI, VREF control, EAPD, and DisplayPort capability fields.
- Input pin controls for unsolicited response tag/enable, input pin sense, widget input enable, multichannel enable and mute/channel IDs for slots 0-7, HBR capability/enable, channel allocation, hot-plug audio status, forced unsolicited-response payload/force bit, default configuration, LPIB snapshot control, LPIB position, LPIB timer snapshot, input activity/status, and infoframe data.

Input endpoints 5, 6, and 7 repeat the complete 23-register input-endpoint pattern:

- `AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`
- `AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`
- `AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID`
- `AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`
- `AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_STREAM_FORMATS`
- `AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_SUPPORTED_SIZE_RATES`
- `AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`
- `AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_CAPABILITIES`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_INPUT_PIN_SENSE`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_WIDGET_CONTROL`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE2`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_HBR`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_CHANNEL_ALLOCATION`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE_FORCE`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB_TIMER_SNAPSHOT`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME`

Important field families in the complete endpoint blocks include:

- Converter capability fields: channel capability, input/output amplifier presence, amplifier parameter override, format override, stripe, processing widget, unsolicited response capability, connection list, digital, power control, LR swap, widget delay, and widget type.
- Converter format fields: number of channels, bits per sample, sample base divisor, sample base multiple, sample base rate, and stream type.
- Channel/stream routing fields: 4-bit channel ID and 4-bit stream ID.
- Digital converter flags: `DIGEN`, validity, validity configuration, preemphasis, copy, non-audio, professional, level, category code, and keepalive.
- Capability bitmaps: full-width stream formats plus audio rate and bit-depth capability fields.
- Pin capability fields: impedance sense, trigger-required, jack-detection, headphone-drive, output/input capability, balanced I/O, HDMI, VREF control, EAPD, and DisplayPort.
- Unsolicited response fields: tag/enable plus forced unsolicited response payload and force bit.
- Pin sense fields: impedance sense value and high-bit presence detect.
- Multichannel routing fields: four packed slots per register, each with enable, mute, and channel-ID fields; the second register covers slots 4-7.
- HBR/channel/status fields: HBR capability/enable, 8-bit channel allocation, hot-plug clock gating state, clock-on state, and high-bit `AUDIO_ENABLED`.
- Default pin configuration fields: sequence, default association, misc, color, connection type, default device, location, and port connectivity.
- LPIB fields: snapshot lock, cyclic buffer wrap count, full-width LPIB, and full-width timer snapshot.
- Input status/infoframe fields: input activity, channel layout, unsolicited-response enables for activity and channel-layout/channel-status infoframe changes, channel count, channel allocation, infoframe byte 5, and high-bit infoframe valid.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time token resolution:

1. DCN303 display code includes `dcn_3_0_3_offset.h` and `dcn_3_0_3_sh_mask.h`.
2. Register helper macros concatenate register and field tokens to find the matching `__SHIFT` and `_MASK` constants.
3. Runtime MMIO or indexed-register code uses those constants to pack write values, update fields without disturbing neighboring bits, or extract status fields from hardware register reads.

The declaration order still reflects hardware organization. The chunk first finishes input endpoint 4, then enters `azf0inputendpoint5_inputendpointind`, `azf0inputendpoint6_inputendpointind`, and `azf0inputendpoint7_inputendpointind` in ascending endpoint order. Within each register group, generated shift definitions appear before mask definitions for the same fields.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes where state lives in DCN 3.0.3 Azalia input endpoint hardware registers.

Writable converter and pin-control fields can represent programmed audio input format, stream/channel association, digital converter behavior, channel allocation, multichannel routing, HBR enablement, hot-plug audio enablement, unsolicited-response setup, forced event generation, and LPIB snapshot lock state. Read-only or hardware-updated fields can represent capability bitmaps, widget/pin capability declarations, presence detect, input activity, channel layout, infoframe validity/data, position-buffer snapshots, timer snapshots, and hot-plug status. The header does not encode access type, reset value, write-one-to-clear behavior, or ordering rules; those remain hardware/manual and driver responsibilities.

Persistence is hardware-defined. Programmed control fields may survive until reprogramming, display/audio block reset, suspend/resume restore, or ASIC reset. Capability and status fields may change as the display audio topology, hot-plug state, input activity, or hardware power state changes.

## Dependencies And Integration Points

This chunk depends on the matching generated DCN 3.0.3 register offset file:

- `dcn_3_0_3_offset.h` defines the MMIO index/data register pairs for `AZF0INPUTENDPOINT4` through `AZF0INPUTENDPOINT7` and the indexed `ixAZF0INPUTENDPOINT<n>_...` offsets for each logical input converter and input pin register described here.
- The endpoint index/data pairs are in the `dce_dc_hda_azf0inputendpoint<n>_dispdec` address blocks, while the field macros in this chunk are in the corresponding `azf0inputendpoint<n>_inputendpointind` indexed blocks.
- The offset header and this shift/mask header must stay generated from the same register database. A field macro without a matching indexed register, or an indexed register without field macros, breaks the intended register-helper contract.

Direct include integration observed in the DCN303 tree:

- `drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.c` includes `dcn_3_0_3_offset.h` and `dcn_3_0_3_sh_mask.h` while constructing DCN303 resources. That file declares `num_audio = 2`, so not every endpoint exposed by the generated register database is necessarily used as a live audio instance on every product configuration.
- `drivers/gpu/drm/amd/display/dc/irq/dcn303/irq_service_dcn303.c` includes the same headers for DCN303 interrupt-service setup.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn303.c` includes the same headers and uses `FD_MASK` and `FD_SHIFT` style expansion for DMUB common register fields.

The broader AMD display register framework provides the main integration point. Helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT` rely on the exact suffix convention used here. Missing or renamed symbols generally fail at compile time; wrong numeric masks or shifts can compile cleanly and fail only as incorrect hardware programming or status interpretation.

## Risks And Edge Cases

- The chunk begins mid-register group. Endpoint 4's `DIGEN`, `V`, `VCFG`, `PRE`, `COPY`, and `NON_AUDIO` digital-converter shifts/masks are in the previous chunk, while this chunk starts at the remaining `PRO`, `L`, `CC`, and `KEEPALIVE` masks.
- This is the final chunk of the header and ends with the include guard close. Any merge-lane whole-file summary should avoid treating the trailing `#endif` as a register artifact.
- The endpoint blocks are highly repetitive. Copy/generator drift affecting only endpoint 5, 6, or 7 can be difficult to detect in review because most lines differ only by endpoint number.
- Shift/mask mismatches are high risk for fields at the edge of the word, especially `PRESENCE_DETECT`, `AUDIO_ENABLED`, and `INFOFRAME_VALID`, all of which use bit 31.
- Several full-width fields use `0xFFFFFFFFL`, including stream formats, LPIB, and timer snapshots. Consumers should avoid signed-width assumptions and should use the expected unsigned register-width types.
- Capability, status, and control registers share identical macro style. This header does not prevent writes to read-only capability/status fields or incorrect handling of clear-on-read/write-one-to-clear semantics if any apply in the hardware model.
- `UNSOLICITED_RESPONSE_FORCE` can synthesize an event payload. Incorrect writes could create misleading hot-plug, input activity, or pin-response notifications.
- Multichannel enable registers pack enable, mute, and 4-bit channel-ID fields for four slots per register. Bad masks or wrong endpoint prefixes can corrupt neighboring slot state while still producing valid C code.
- Endpoint count and hardware exposure are not the same concept. The generated register map exposes input endpoints 4-7 here, but DCN303 resource configuration may instantiate fewer usable audio resources.
- Cross-generation reuse is risky. DCN 3.0.3 names are close to DCN 3.0.2 and other DCN headers, but code must include offset and shift/mask files for the same ASIC generation.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration oriented:

- Build the AMDGPU display code for a DCN303-enabled configuration to catch missing macro names in register helper expansions.
- Preprocess representative users of `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE` to ensure token concatenation resolves to `AZF0INPUTENDPOINT4` through `AZF0INPUTENDPOINT7` macros where expected.
- Compare this header slice against `dcn_3_0_3_offset.h` to verify that every input-endpoint indexed register in endpoints 4-7 has matching shift/mask field definitions.
- Compare generated masks and shifts against the authoritative AMD register database for DCN 3.0.3, especially high-bit fields, full-width fields, and packed multichannel slot fields.
- Exercise DCN303 display-audio bring-up on hardware with HDMI/DisplayPort audio paths and verify input endpoint capability reads, stream format/rate support, channel allocation, HBR state, hot-plug audio enabled state, and input activity/status fields.
- Test hotplug, audio enable/disable, suspend/resume, and display reset paths while checking that driver state is reprogrammed or re-read consistently for converter format, stream/channel ID, digital converter flags, multichannel routing, LPIB snapshots, infoframe status, and unsolicited response controls.
- Validate that generated endpoint 5-7 field layouts match endpoint 4 and earlier input endpoint blocks where hardware intends symmetry, while preserving endpoint-specific prefixes.

## Open Cross-Chunk Questions

- The merge lane should combine this with the previous chunk to present endpoint 4 as a complete input endpoint, because this chunk starts after the beginning of `AZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`.
- Whole-file analysis should verify the expected number of DCN 3.0.3 Azalia input and output endpoint blocks and reconcile the generated endpoint map with DCN303 `num_audio` resource limits.
- Whole-file analysis should compare the DCN 3.0.3 generated field layout against nearby generations, especially DCN 3.0.2, to flag any intentional or accidental register-database divergence.
