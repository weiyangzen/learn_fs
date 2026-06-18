# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 56842-59188

## Scope

This chunk covers a generated region of the DCN 3.1.2 shift/mask header. It contains only C preprocessor constants and generated grouping comments; there are no functions, structs, enums, storage objects, or executable statements in this slice.

The line range starts in the tail of `AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE`, continues through the rest of output endpoint 4, covers complete output endpoint 5, output endpoint 6, and output endpoint 7 blocks, and then enters input endpoint 0 and the beginning of input endpoint 1. The range contains 2,040 `#define` entries: 1,018 `__SHIFT` definitions and 1,022 `_MASK` definitions. The mask count is higher because the range begins with six endpoint-4 multichannel masks whose shifts are in the previous chunk and ends after two input-endpoint-1 default-configuration shifts whose masks are in the next chunk.

The main hardware area represented here is Azalia function 0 display audio for DCN 3.1.2: HDMI/DisplayPort-style output pins/converters and the first two input endpoint register groups. The generated comments identify indexed register address blocks such as `azf0endpoint5_endpointind`, `azf0endpoint6_endpointind`, `azf0endpoint7_endpointind`, `azf0inputendpoint0_inputendpointind`, and `azf0inputendpoint1_inputendpointind`.

## Purpose

The purpose of this header region is to provide symbolic bit positions and masks for DCN 3.1.2 Azalia audio endpoint registers. AMDGPU display code can pair these field constants with the matching DCN 3.1.2 offset header and register-helper macros, avoiding hard-coded bit positions in code that programs or reads audio hardware state.

The output endpoint blocks describe converter format selection, stream/channel routing, digital converter flags, supported format and rate capability fields, pin capabilities, speaker/channel descriptors, sink identification, lip-sync and HBR state, hot-plug audio status, LPIB snapshots, channel-status overrides, remote keepalive, and audio enable/disable/format-change interrupt status. The input endpoint blocks describe a similar input-converter and input-pin contract, with input activity, infoframe status, and input-specific pin sense fields.

This file is a hardware contract rather than an algorithm. Its important behavior is the exact macro spelling and numeric bit layout consumed by ASIC-specific DCN 3.1 register tables and register-access helpers.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated preprocessor convention:

- `AZF0ENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT` gives a bit offset for output endpoint `n`.
- `AZF0ENDPOINT<n>_<REGISTER>__<FIELD>_MASK` gives the corresponding output endpoint field mask.
- `AZF0INPUTENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT` and `_MASK` do the same for input endpoint `n`.
- Grouping comments name the hardware register, and `// addressBlock: ...` comments mark transitions between indexed endpoint blocks.

The partial endpoint 4 tail includes masks for multichannel slots `45` and `67`, then complete pin-side groups for:

- `RESPONSE_LIPSYNC`, with 8-bit video and audio lip-sync fields.
- `RESPONSE_HBR`, with HBR capable and enable bits.
- `SINK_INFO0` through `SINK_INFO8`, covering manufacturer/product IDs, sink-description length, two 32-bit port-ID words, and 18 bytes of sink description.
- `HOT_PLUG_CONTROL`, with clock-gating disable, clock-on state, and high-bit `AUDIO_ENABLED`.
- `UNSOLICITED_RESPONSE_FORCE`, with a 26-bit payload and force bit.
- `RESPONSE_CONFIGURATION_DEFAULT`, with sequence, association, misc, color, connection type, default device, location, and port-connectivity fields.
- `MULTICHANNEL_ENABLE2`, `MULTICHANNEL_MODE`, `CODEC_CS_OVERRIDE_0` through `_8`, association info, digital-output status, LPIB snapshot/LPIB/timer snapshot, coding type, format-change fields, wireless display identification, remote keepalive, and audio enable/disable/format-change interrupt status.

Output endpoints 5, 6, and 7 repeat the complete endpoint pattern. Important register families include:

- Converter parameters: `CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `PARAMETER_STREAM_FORMATS`, and `PARAMETER_SUPPORTED_SIZE_RATES`.
- Converter controls: `CONTROL_CONVERTER_FORMAT`, `CONTROL_CHANNEL_STREAM_ID`, `CONTROL_DIGITAL_CONVERTER`, `STRIPE_CONTROL`, `CONTROL_RAMP_RATE`, `CONTROL_GTC_EMBEDDING`, and GTC counter delta/min/max.
- Pin parameters and controls: `CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `CODEC_PIN_PARAMETER_CAPABILITIES`, unsolicited response, pin sense, widget control, channel speaker, audio descriptors 0-13, multichannel enable registers, lip-sync, HBR, sink info, hot-plug control, forced unsolicited response, default configuration, channel-status overrides, association info, digital output status, LPIB controls, coding type, format changed, wireless display identification, and remote keepalive.
- Per-endpoint audio status/interrupt registers: `AUDIO_ENABLE_STATUS`, `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS`.

Input endpoint 0 is complete in this chunk. Its register families include:

- Input converter capability, format, channel/stream ID, digital converter flags, supported stream formats, and supported size/rate bitmaps.
- Input pin widget and pin capability fields, including impedance sense, trigger-required, jack detect, headphone drive, output/input capability, HDMI, VREF, EAPD, and DisplayPort capability bits.
- Input pin controls for unsolicited response, input pin sense, widget input enable, multichannel slots 0-7, HBR, channel allocation, hot-plug audio state, forced unsolicited response, default configuration, LPIB snapshot/LPIB/timer snapshot, input activity/status control, and infoframe fields.

Input endpoint 1 starts with the same input-converter and input-pin pattern and reaches the beginning of `AZF0INPUTENDPOINT1_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`; the rest of that register and later input-endpoint-1 registers are outside this line range.

Common field families in the chunk include:

- Audio format fields: number of channels, bits per sample, sample base divisor/multiple/rate, and stream type.
- Routing fields: 4-bit channel IDs and 4-bit stream IDs.
- Digital converter flags: `DIGEN`, validity, validity configuration, preemphasis, copy, non-audio, professional, level, category code, and keepalive.
- Capability bitmaps: full-width stream formats plus rate and bit-depth capabilities.
- Multichannel packed slots: enable, mute, and 4-bit channel IDs, either as `01/23/45/67` output pairs or individual input slots split across two registers.
- Event/status fields: unsolicited response tag/enable/force, HBR capability/enable, hot-plug clock state, audio enabled, audio enabled/disabled/format-changed interrupt masks/acks, LPIB snapshots, input activity, and infoframe validity.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time token resolution:

1. DCN 3.1 display code includes `dcn_3_1_2_offset.h` and `dcn_3_1_2_sh_mask.h`.
2. Register tables and helpers concatenate register and field tokens to find matching `__SHIFT` and `_MASK` macros.
3. Runtime MMIO or indexed-register helper code uses those constants to pack write values, preserve neighboring fields during updates, or extract status fields from hardware reads.

The declaration order reflects hardware organization. The slice first finishes output endpoint 4, then walks output endpoints 5, 6, and 7 in order, then starts input endpoints 0 and 1. Within each register group, shift definitions normally precede mask definitions; the exceptions are caused by this chunk starting and ending mid-register group.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes where state lives in DCN 3.1.2 Azalia endpoint hardware registers.

Writable converter and pin-control fields can represent programmed audio format, stream/channel association, digital converter behavior, speaker/channel routing, multichannel enablement and mute state, HBR enablement, hot-plug audio enablement, channel-status overrides, forced unsolicited responses, GTC embedding, LPIB snapshot locking, and interrupt mask/ack state. Read-only or hardware-updated fields can represent capability declarations, sink identity, pin sense, lip-sync values, LPIB/timer snapshots, audio enable state, format-change status, input activity, and infoframe validity/data.

Persistence is hardware-defined. Programmed control fields may remain until reprogramming, display/audio block reset, suspend/resume restore, or ASIC reset. Capability and status fields may change with connector hot-plug, link training, audio stream changes, input activity, sink EDID/ELD-derived state, or DCN power management. The header does not encode access type, reset value, volatile behavior, clear-on-read, or write-one-to-clear semantics; consumers must rely on the hardware specification and established AMD display register helpers.

## Dependencies And Integration Points

This chunk depends on the matching generated DCN 3.1.2 register offset file:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h` supplies MMIO and indexed-register offsets such as the `ixAZF0ENDPOINT<n>_...` and `ixAZF0INPUTENDPOINT<n>_...` names corresponding to the fields in this shift/mask header.
- The offset header and shift/mask header must come from the same register database. A field macro without a matching register offset, or a register offset with stale field masks, breaks the register-helper contract.

Observed direct include users in the DCN 3.1 tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c`, which includes `yellow_carp_offset.h`, `dcn_3_1_2_offset.h`, and this shift/mask header, then builds DMUB register shift and mask tables with `FD_MASK` and `FD_SHIFT`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c`, which includes the same register headers for DCN31 interrupt-service setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, which includes the same register headers while constructing DCN31 resources. That file declares seven audio register table entries, `audio_regs(0)` through `audio_regs(6)`, while the resource capability block sets `num_audio = 5`; generated endpoints and instantiated audio resources are related but not identical concepts.

The broader AMD display register framework is the main integration point. Helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT` rely on exact macro suffixes. Missing or renamed symbols generally fail at compile time; incorrect numeric masks or shifts can compile cleanly and only surface as wrong hardware programming or status interpretation.

## Risks And Edge Cases

- The range starts mid-register: endpoint 4 multichannel `45` and `67` shift definitions are in the previous chunk, while only their masks appear here.
- The range ends mid-register: input endpoint 1 default-configuration `SEQUENCE` and `DEFAULT_ASSOCIATION` shifts appear here, but the remaining fields and masks are in the next chunk.
- The output endpoint blocks are highly repetitive. Endpoint-specific generator drift can be hard to notice because most lines differ only by `AZF0ENDPOINT5`, `AZF0ENDPOINT6`, or `AZF0ENDPOINT7`.
- Several high-bit fields use bit 31, including `AUDIO_ENABLED`, `PRESENCE_DETECT`, and audio interrupt status/ack fields. Wrong signedness or width assumptions can corrupt status interpretation.
- Full-width fields such as stream format bitmaps, LPIB, timer snapshots, port IDs, GTC counter deltas, and wireless display identification use `0xFFFFFFFFL`; consumers should use unsigned 32-bit register values.
- Capability, control, status, and interrupt registers all use the same macro style. This header does not prevent writing read-only capability/status fields or mishandling write-one-to-clear or mask/ack behavior.
- `UNSOLICITED_RESPONSE_FORCE` can synthesize event payloads. Incorrect writes could create misleading hot-plug, pin-response, input-activity, or format-change notifications.
- Multichannel registers pack several enable, mute, and channel-ID fields into one word. A wrong mask or wrong endpoint prefix can alter neighboring channel state while still compiling.
- Cross-generation reuse is risky. Many DCN and DCE headers contain near-identical Azalia field names, but DCN 3.1.2 code must keep the `dcn_3_1_2_offset.h` and `dcn_3_1_2_sh_mask.h` pair aligned.
- Generated endpoint count can exceed the product's exposed audio count. Resource configuration, connector topology, BIOS straps, and SKU limits determine which generated endpoints are actually active.

## Test Signals

Useful validation is mostly build-time and hardware-integration oriented:

- Build AMDGPU display code for a DCN31/DCN 3.1.2-enabled configuration to catch missing macro names in register-helper expansions.
- Preprocess representative users of `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE` to ensure token concatenation resolves to the intended `AZF0ENDPOINT4` through `AZF0ENDPOINT7` and `AZF0INPUTENDPOINT0`/`1` macros.
- Compare this slice against `dcn_3_1_2_offset.h` to verify that every endpoint indexed register named in this chunk has matching register offsets.
- Compare generated masks and shifts against the authoritative AMD register database for DCN 3.1.2, especially high-bit status fields, full-width fields, GTC/LPIB fields, sink-info bytes, and packed multichannel slots.
- Exercise HDMI/DisplayPort audio bring-up on DCN31 hardware and verify converter format programming, stream/channel ID routing, digital converter flags, speaker allocation/audio descriptors, sink info, HBR state, lip-sync responses, and hot-plug audio enabled state.
- Test hotplug, audio enable/disable, audio format changes, suspend/resume, and display reset paths while checking that driver state is reprogrammed or re-read consistently for converter state, channel-status overrides, multichannel routing, LPIB snapshots, input status, and unsolicited response controls.
- Validate interrupt behavior around `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS`, including mask and ack fields.
- For input endpoints, validate input activity, channel layout, infoframe valid/data, and input pin sense transitions if the platform exposes these paths.

## Open Cross-Chunk Questions

- The merge lane should combine this with neighboring chunks to present endpoint 4 and input endpoint 1 as complete logical blocks, because both are split at this chunk boundary.
- Whole-file analysis should reconcile generated endpoint blocks with DCN31 resource limits such as `audio_regs[]` entries and `num_audio = 5`.
- Whole-file analysis should compare this DCN 3.1.2 Azalia layout with nearby generated headers such as DCN 3.1.5/3.1.6 and DCE 12.0 to distinguish intentional register-database reuse from accidental drift.
