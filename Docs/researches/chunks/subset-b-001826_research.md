# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 59189-60782

## Scope

This chunk is the final 1,594-line slice of the generated AMD DCN 3.1.2 register shift/mask header. It contains only preprocessor constants and generated grouping comments; there are no functions, structs, enums, storage objects, or executable statements in this range.

The range starts in the middle of `AZF0INPUTENDPOINT1_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`, continues through the tail of input endpoint 1, then covers complete generated `azf0inputendpoint2_inputendpointind` through `azf0inputendpoint7_inputendpointind` blocks. It ends with the header guard `#endif`. The slice contains 1,430 `#define` entries: 714 `__SHIFT` definitions and 716 `_MASK` definitions. The mask count is larger because the first two shift fields for endpoint 1's default-configuration register are in the previous chunk, while their masks remain in this chunk.

This file sits under a local `ceph-client` source mirror, but the content is AMDGPU Display Core hardware metadata, not Ceph filesystem logic.

## Purpose

The purpose of this header region is to give DCN 3.1.2 display-audio code symbolic bit positions and masks for Azalia/HD-audio function 0 input endpoint registers. Runtime code combines these constants with the matching DCN 3.1.2 offset/index header and AMD display register helpers to pack fields for writes or extract fields from register reads without hard-coded bit arithmetic.

The covered register fields describe HDMI/DisplayPort-style audio input converter and input pin state. They model converter widget capabilities, stream format selection, channel and stream IDs, digital converter flags, stream-format and size/rate capability bitmaps, input pin capabilities, unsolicited responses, pin sense, widget input enablement, multichannel routing, HBR capability/enablement, channel allocation, hot-plug audio state, forced unsolicited-response payloads, HDA pin default configuration, LPIB snapshots, input activity/status, and decoded audio infoframe summary data.

The behavioral contract here is the exact generated macro namespace and numeric bit layout. Changing a macro value is equivalent to changing the hardware register ABI for DCN 3.1.2.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated preprocessor convention:

- `AZF0INPUTENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT` gives the bit offset for an input endpoint field.
- `AZF0INPUTENDPOINT<n>_<REGISTER>__<FIELD>_MASK` gives the field mask for the same field.
- Generated comments such as `// addressBlock: azf0inputendpoint2_inputendpointind` group fields by indexed input-endpoint block.
- Generated comments such as `//AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME` group fields by logical indexed register.

The endpoint 1 tail includes the latter part of `RESPONSE_CONFIGURATION_DEFAULT`, then `LPIB_SNAPSHOT_CONTROL`, `LPIB`, `LPIB_TIMER_SNAPSHOT`, `INPUT_STATUS_CONTROL`, and `INFOFRAME`.

Input endpoints 2 through 7 each repeat a complete 23-register input endpoint layout:

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

Important field families:

- Converter capability fields: channel capability, amplifier presence, amplifier override, format override, stripe, processing widget, unsolicited response capability, connection list, digital, power control, LR swap, widget delay, and widget type.
- Converter format fields: number of channels, bits per sample, sample base divisor, sample base multiple, sample base rate, and stream type.
- Routing fields: 4-bit channel ID and 4-bit stream ID.
- Digital converter fields: `DIGEN`, validity, validity configuration, preemphasis, copy, non-audio, professional, level, category code, and keepalive.
- Capability bitmaps: full-width stream formats plus audio rate and bit-depth capability fields.
- Pin capability fields: impedance sense, trigger-required, jack detection, headphone drive, output/input capability, balanced I/O, HDMI, VREF control, EAPD, and DisplayPort.
- Event and status fields: unsolicited response tag/enable, forced unsolicited response payload/force bit, pin sense presence detect, input activity, channel layout, and infoframe validity.
- Multichannel fields: two packed registers cover slots 0-7, with each slot exposing enable, mute, and 4-bit channel ID fields.
- HBR, channel, and hot-plug fields: HBR capability/enable, 8-bit channel allocation, clock-gating disable, clock-on state, and high-bit `AUDIO_ENABLED`.
- Default pin configuration fields: sequence, default association, misc, color, connection type, default device, location, and port connectivity.
- LPIB fields: snapshot lock, cyclic-buffer wrap count, full-width LPIB, and full-width LPIB timer snapshot.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time symbol resolution:

1. DCN 3.1.2 consumers include `dcn_3_1_2_offset.h` and `dcn_3_1_2_sh_mask.h`.
2. Register helper macros concatenate register and field tokens to find matching `__SHIFT` and `_MASK` definitions.
3. Runtime code uses those constants when reading or writing the Azalia input endpoint indexed-register data value.

The declaration order mirrors hardware organization. The chunk finishes endpoint 1, then proceeds through input endpoints 2, 3, 4, 5, 6, and 7 in ascending endpoint order. Within each register group, generated shift definitions appear before mask definitions for the same fields.

Azalia endpoint access is indirect: software selects an endpoint indexed register and then reads or writes a data register. This header describes the bit layout of the data values, not the sequencing policy for the index/data transactions.

## State And Persistence Behavior

The header itself stores no software state and persists no data. It describes hardware state in DCN 3.1.2 Azalia input endpoint registers.

Writable control fields can represent audio input format, stream/channel binding, digital converter behavior, input widget enablement, multichannel routing, HBR enablement, channel allocation, hot-plug audio state, unsolicited-response setup, forced event generation, and LPIB snapshot locking. Capability and status fields can represent advertised widget/pin capabilities, supported stream formats and rates, pin presence, input activity, infoframe contents, LPIB snapshots, timer snapshots, and clock/audio enabled state.

Persistence is hardware-defined. Programmed fields generally remain until rewritten, reset by the display/audio block, restored during suspend/resume, or cleared by a broader ASIC reset. Capability and live status fields may change with sink topology, hot-plug state, audio activity, or display/audio power state. The shift/mask header does not encode access type, volatility, reset values, read-only behavior, clear-on-read behavior, or write-one-to-clear semantics.

## Dependencies And Integration Points

This chunk depends on the matching generated DCN 3.1.2 offset header:

- `dcn_3_1_2_offset.h` defines direct MMIO index/data windows for `regAZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX` through `regAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_ENDPOINT_DATA`, with base index `2`.
- The same offset header defines the indexed `ixAZF0INPUTENDPOINT<n>_...` selectors for the logical registers described here. For each endpoint, converter controls occupy indexed offsets `0x0001` through `0x0006`, input pin controls include `0x0020` through `0x0024`, multichannel/HBR controls occupy `0x0036` through `0x0038`, channel/hotplug/default controls occupy `0x0053` through `0x0056`, and LPIB/status/infoframe controls occupy `0x0064` through `0x0068`.
- `drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, `drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c`, and `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c` include `dcn_3_1_2_offset.h` and `dcn_3_1_2_sh_mask.h`. Those files are the DCN 3.1 generation integration points for generated register symbols.
- `dcn31_resource.c` reports `num_audio = 5`, so the generated register database exposes more input endpoint instances than every resource configuration necessarily instantiates as live audio resources.
- Shared display audio code such as `drivers/gpu/drm/amd/display/dc/dce/dce_audio.c` implements Azalia endpoint index/data programming for display audio. The input endpoint constants in this chunk must remain compatible with that broader indirect-register model even when the most visible resource table entries use output endpoint macros.

The main integration contract is token naming. Helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, `FD_SHIFT`, `SF`, and `SRI` rely on exact macro suffixes. A missing or renamed symbol usually fails at compile time; an incorrect numeric mask or shift can compile and then misprogram hardware.

## Risks And Edge Cases

- The chunk starts mid-register. Endpoint 1's `RESPONSE_CONFIGURATION_DEFAULT` register comment plus `SEQUENCE__SHIFT` and `DEFAULT_ASSOCIATION__SHIFT` are in the previous chunk, while this slice contains the remaining shifts and all masks for that register.
- This is the final chunk of `dcn_3_1_2_sh_mask.h` and ends with `#endif`. The merge lane should not treat the guard close as a hardware register definition.
- The input endpoint blocks are highly repetitive. Generator or hand-edit drift affecting only one endpoint can be hard to spot because most lines differ only by endpoint number.
- Several fields sit at bit 31: `PRESENCE_DETECT`, `AUDIO_ENABLED`, and `INFOFRAME_VALID`. Wrong signedness or wrong high-bit masks can produce status interpretation failures.
- Full-width masks use `0xFFFFFFFFL` for fields such as stream formats, LPIB, and LPIB timer snapshots. Consumers should use appropriate unsigned 32-bit register types and avoid sign-extension assumptions.
- Capability, status, and control fields use the same macro style. The header does not prevent a caller from writing capability/status registers or from missing special read/clear semantics if the hardware assigns them.
- `UNSOLICITED_RESPONSE_FORCE` can synthesize a response payload. Bad writes can create misleading audio, hot-plug, input-activity, or pin-response events.
- Multichannel enable registers pack four channel slots per word. An incorrect mask, endpoint prefix, or read-modify-write sequence can alter neighboring enable, mute, or channel-ID fields.
- Generated endpoint count and active audio resource count are not identical. DCN 3.1.2 exposes endpoint 0-7 register windows, while DCN 3.1 resource capabilities in this tree report five audio resources.
- Cross-generation reuse is risky. DCN 3.1.2 field names resemble DCN 3.0.x and other DCN headers, but offset and shift/mask headers must be paired by the same ASIC generation.

## Test Signals

Useful validation is mostly build-time and hardware-integration oriented:

- Build AMDGPU display code for a DCN 3.1/DCN 3.1.2-enabled configuration to catch unresolved generated macro names.
- Preprocess representative users of `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, `FD_SHIFT`, `SF`, and `SRI` to ensure token concatenation resolves to the expected `AZF0INPUTENDPOINT*` macros.
- Compare this slice against `dcn_3_1_2_offset.h` to verify every input endpoint indexed register selector has matching field shift/mask definitions.
- Compare the generated field values against the authoritative AMD register database for DCN 3.1.2, especially high-bit fields, full-width fields, and packed multichannel fields.
- Exercise HDMI/DisplayPort audio bring-up on DCN 3.1-family hardware and verify converter format, stream/channel IDs, digital converter state, channel allocation, HBR state, hot-plug audio enablement, and input status/infoframe reporting.
- Test hot-plug, audio enable/disable, audio format changes, suspend/resume, and display reset paths while checking that endpoint state is reprogrammed or re-read consistently.
- Validate endpoint-instance symmetry for endpoints 2 through 7 while preserving the endpoint-specific prefixes and matching index/data windows.

## Open Cross-Chunk Questions

- The merge lane should combine this with the previous chunk before describing endpoint 1 as complete, because this chunk begins after the start of endpoint 1's default-configuration register.
- Whole-file research should reconcile generated input endpoint coverage with DCN 3.1.2 resource limits and any product-specific audio endpoint disablement.
- Whole-file research should compare the final DCN 3.1.2 Azalia input endpoint layout with adjacent DCN 3.1 and DCN 3.0.x generated headers to distinguish intended register-database continuity from accidental divergence.
