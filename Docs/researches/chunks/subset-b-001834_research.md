# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 2579-4946

## Purpose

This chunk is generated AMD DCN 3.1.4 register field metadata for the Azalia/HD-audio endpoint register namespace. It contains no executable C logic; it publishes preprocessor constants that describe bit shifts and bit masks for fields inside DCN314 audio endpoint indirect registers. Consumers combine these field constants with register offsets from `dcn_3_1_4_offset.h` and DC register helper macros to read, write, update, or decode the relevant MMIO-backed hardware fields.

The requested range contains 2,049 `#define` lines: 1,023 `__SHIFT` macros and 1,026 `_MASK` macros. It starts in the tail of `AZF0ENDPOINT2_AZALIA_F0_CODEC_PIN_CONTROL_FORMAT_CHANGED`, covers the remaining endpoint 2 status/interrupt fields, covers complete `azf0endpoint3_endpointind` through `azf0endpoint6_endpointind` address blocks, and ends early in `azf0endpoint7_endpointind` after `AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_PARAMETER_CAPABILITIES`. Although this repository path is under a `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata, not Ceph filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, local variables, includes, allocation paths, or locks in this chunk. The public interface is the generated macro namespace:

- `AZF0ENDPOINT<n>_<register>__<field>__SHIFT`: bit position for a field in an Azalia endpoint register.
- `AZF0ENDPOINT<n>_<register>__<field>_MASK`: bit mask for the same field.

Major field families covered here:

- Converter capability and format fields: `CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT`, `CHANNEL_STREAM_ID`, `DIGITAL_CONVERTER`, stream-format capability, supported size/rate capability, stripe control, ramp rate, and GTC embedding/counter-delta fields.
- Pin capability and status fields: `CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `CODEC_PIN_PARAMETER_CAPABILITIES`, unsolicited response controls, pin sense, widget control, channel/speaker allocation, pin association, digital output status, coding type, wireless display identification, and remote keepalive.
- Audio descriptor fields: `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13` expose speaker/channel count, sample rates, byte fields, channel allocation, down-mix inhibit, and descriptor validity for HDMI/DP audio sink descriptions.
- Multichannel fields: `MULTICHANNEL_ENABLE`, `MULTICHANNEL_ENABLE2`, and `MULTICHANNEL_MODE` define enable, mute, and channel-ID fields for multichannel audio mapping.
- Sink and link capability fields: `RESPONSE_LIPSYNC`, `RESPONSE_HBR`, `SINK_INFO0` through `SINK_INFO8`, and `HOT_PLUG_CONTROL` describe sink latency, high-bit-rate audio, ELD-like sink identity/capability data, clock gating, and audio-enabled state.
- Channel-status override fields: `PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8` describe IEC/channel-status override words used for digital audio metadata.
- Audio endpoint interrupt/status fields: `AUDIO_ENABLE_STATUS`, `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS` provide flag, mask, and type bits for endpoint audio enable/disable/format-change events.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by the AMD display driver:

1. DCN314-specific code includes this header together with `dcn_3_1_4_offset.h`.
2. Register table construction macros such as `SF(...)`, `SR(...)`, and related token-pasting helpers bind field shifts/masks and register offsets into per-block structures.
3. Audio construction in `drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c` builds `dce_audio_registers`, `dce_audio_shift`, and `dce_audio_mask` entries from this generated namespace, then creates `dce_audio` objects for active audio instances.
4. IRQ and DMUB paths include the same generated headers for DCN314 register access, while common audio code performs the actual read-modify-write, status read, interrupt clear/mask, and audio programming sequences.

The macros do not express ordering constraints. Consumers must still sequence audio enablement, hotplug response, sink capability discovery, audio format programming, channel allocation, channel-status programming, interrupt masking/acking, clock gating, and suspend/resume restoration according to hardware rules.

## State And Persistence Behavior

The file stores no software state and persists nothing. It describes fields in hardware-owned registers. The represented state includes:

- Converter configuration for sample base rate, base multiple/divisor, bits per sample, channel count, stream ID, channel ID, digital converter flags, keepalive, stripe mode, ramp rate, and GTC presentation-time embedding.
- Capability snapshots for widgets, pins, stream formats, supported rates/bit depths, HBR support, DP/HDMI pin capability, power-control capability, unsolicited responses, and sink information.
- Runtime pin/audio state for audio enabled/disabled status, format-change status, hotplug/audio-enabled state, LPIB snapshots, lipsync responses, remote keepalive, and forced unsolicited responses.
- Per-endpoint interrupt state for audio enabled, audio disabled, and audio format changed conditions, with separate flag, mask, and type fields.

Persistence is hardware-defined. Some fields are configuration bits that may survive until modeset, audio teardown, power gating, suspend/resume, or ASIC reset. Others are read-only capability/status fields, sticky interrupt flags, self-clearing controls, write-one-to-clear fields, or indirect-register values. This generated header only gives bit layout; it does not encode access type, reset value, volatility, or clear semantics.

## Dependencies And Integration Points

This chunk depends on the generated DCN314 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`, which provides the matching register offsets and base-index macros.
- `drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`, which includes both DCN314 generated headers and uses the `AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX`/`DATA` field macros in the DCN314 audio shift/mask tables.
- `drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c` and `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`, which also include the DCN314 generated offset and shift/mask headers.
- Common audio implementation under `drivers/gpu/drm/amd/display/dc/dce/`, which consumes the resource-layer register, shift, and mask tables to program display audio.
- Interrupt source definitions such as `include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`, where Azalia endpoint audio format-changed, enabled, and disabled interrupts are identified by endpoint context IDs.

The generated endpoint namespace is broader than the active DCN314 resource count. `dcn314_resource.c` defines audio register entries for endpoint IDs 0 through 6 but sets `num_audio = 5`; endpoint constants in this chunk may exist for generated hardware completeness even when a specific ASIC/resource table does not expose every endpoint to higher layers.

## Risks And Edge Cases

- Bitfield drift is the central risk. These are untyped constants; an incorrect shift or mask can compile cleanly while causing bad read-modify-write behavior on hardware.
- The chunk boundaries are artificial. It begins after the first three `FORMAT_CHANGED` shift fields for endpoint 2 and ends before the rest of endpoint 7 pin-control/status fields, so adjacent chunks are required for complete endpoint 2 and endpoint 7 coverage.
- Endpoint families are highly repetitive. Copy-generation mistakes between endpoints 3, 4, 5, 6, and 7 may only show up on specific display/audio instance mappings or multi-monitor configurations.
- The `_MASK_MASK` names in interrupt-status registers are intentional generated names for a field called `AUDIO_*_MASK`. Review tools must not collapse or rename them as duplicates.
- Interrupt fields are side-effect-sensitive. Confusing flag, mask, and type bits can leave audio interrupts stuck, masked unexpectedly, or acknowledged incorrectly.
- Audio capability/status fields cross hardware and OS audio-stack expectations. Wrong HBR, ELD/sink info, channel allocation, sample-rate, or channel-status masks can produce silent audio, stereo-only fallback, invalid HDMI/DP info, or format-change storms.
- Some generated endpoints may not be exposed by `num_audio` on DCN314. Tests should distinguish a bad generated field from an intentionally unused endpoint.

## Test Signals

Useful validation combines generated-header consistency with hardware audio behavior:

- Build AMDGPU/DC with DCN314 support enabled; missing or renamed macros should fail in `dcn314_resource.c`, `irq_service_dcn314.c`, or `dmub_dcn314.c`.
- Mechanically verify that every field in lines 2579-4946 has the expected shift/mask pair where the chunk contains the full register definition, while allowing the known boundary partials at endpoint 2 start and endpoint 7 end.
- Diff this range against AMD's authoritative DCN 3.1.4 register database and nearby generated DCN 3.1.x/3.2.x headers where endpoint layouts are expected to match.
- Exercise HDMI and DisplayPort audio across available DCN314 audio instances: enable/disable audio during modesets, change sample rates and bit depths, test stereo and multichannel channel allocation, and verify HBR-capable formats.
- Test hotplug, display unplug/replug, suspend/resume, runtime power transitions, and audio stream start/stop while watching for audio enabled/disabled/format-changed interrupts, stuck flags, repeated events, or missing events.
- Validate sink data exposed to the OS audio stack, including ELD-like sink info, speaker allocation, latency/lipsync, channel-status values, and wireless-display/keepalive behavior where applicable.
- Use kernel logs and display/audio diagnostics to look for lost audio, invalid channel maps, format negotiation failures, interrupt storms, register readback mismatches, or failures limited to higher-numbered endpoints.

## Cross-Chunk Notes

Earlier chunks own the start of endpoint 2, including most of its pin-control fields. Later chunks continue endpoint 7 after `CODEC_PIN_PARAMETER_CAPABILITIES` and cover the remaining Azalia endpoint register field namespace. The final per-file research document should merge adjacent chunks before making complete claims about all eight Azalia endpoints or all fields in `dcn_3_1_4_sh_mask.h`.
