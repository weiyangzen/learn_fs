# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001833`: lines 1-2578, `Docs/researches/chunks/subset-b-001833_research.md`
- `subset-b-001834`: lines 2579-4946, `Docs/researches/chunks/subset-b-001834_research.md`
- `subset-b-001835`: lines 4947-7218, `Docs/researches/chunks/subset-b-001835_research.md`
- `subset-b-001836`: lines 7219-9704, `Docs/researches/chunks/subset-b-001836_research.md`
- `subset-b-001837`: lines 9705-12036, `Docs/researches/chunks/subset-b-001837_research.md`
- `subset-b-001838`: lines 12037-14354, `Docs/researches/chunks/subset-b-001838_research.md`
- `subset-b-001839`: lines 14355-17019, `Docs/researches/chunks/subset-b-001839_research.md`
- `subset-b-001840`: lines 17020-19538, `Docs/researches/chunks/subset-b-001840_research.md`
- `subset-b-001841`: lines 19539-22071, `Docs/researches/chunks/subset-b-001841_research.md`
- `subset-b-001842`: lines 22072-24583, `Docs/researches/chunks/subset-b-001842_research.md`
- `subset-b-001843`: lines 24584-27100, `Docs/researches/chunks/subset-b-001843_research.md`
- `subset-b-001844`: lines 27101-29604, `Docs/researches/chunks/subset-b-001844_research.md`
- `subset-b-001845`: lines 29605-32147, `Docs/researches/chunks/subset-b-001845_research.md`
- `subset-b-001846`: lines 32148-34607, `Docs/researches/chunks/subset-b-001846_research.md`
- `subset-b-001847`: lines 34608-36980, `Docs/researches/chunks/subset-b-001847_research.md`
- `subset-b-001848`: lines 36981-39374, `Docs/researches/chunks/subset-b-001848_research.md`
- `subset-b-001849`: lines 39375-41781, `Docs/researches/chunks/subset-b-001849_research.md`
- `subset-b-001850`: lines 41782-44191, `Docs/researches/chunks/subset-b-001850_research.md`
- `subset-b-001851`: lines 44192-46599, `Docs/researches/chunks/subset-b-001851_research.md`
- `subset-b-001852`: lines 46600-49100, `Docs/researches/chunks/subset-b-001852_research.md`
- `subset-b-001853`: lines 49101-51572, `Docs/researches/chunks/subset-b-001853_research.md`
- `subset-b-001854`: lines 51573-54012, `Docs/researches/chunks/subset-b-001854_research.md`
- `subset-b-001855`: lines 54013-56454, `Docs/researches/chunks/subset-b-001855_research.md`
- `subset-b-001856`: lines 56455-58975, `Docs/researches/chunks/subset-b-001856_research.md`
- `subset-b-001857`: lines 58976-61482, `Docs/researches/chunks/subset-b-001857_research.md`
- `subset-b-001858`: lines 61483-61832, `Docs/researches/chunks/subset-b-001858_research.md`

## Chunk Research

### subset-b-001833: lines 1-2578

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 1-2578

## Scope

This chunk is the opening slice of the generated DCN 3.1.4 register-field mask header. It contains the MIT license text, the `_dcn_3_1_4_SH_MASK_HEADER` include guard, address-block/register comments, and C preprocessor constants only. The exported constants are `_SHIFT` macros for field bit positions and `_MASK` macros for raw register bitmasks. There are no C functions, structs, enums, branches, loops, allocations, or direct MMIO operations in this range.

The requested range covers the full opening HDA/Azalia controller and legacy VGA indexed-register mask surface, sink-description and CRC result blocks, all 16 Azalia stream latency/FIFO blocks, complete endpoint 0 and endpoint 1 audio codec converter/pin macro groups, and most of endpoint 2 through `AZF0ENDPOINT2_AZALIA_F0_CODEC_PIN_CONTROL_FORMAT_CHANGED`. The line boundary stops before endpoint 2 wireless-display, remote-keepalive, and audio interrupt-status fields that continue later in the source file.

## Purpose And Hardware Surface

The purpose of this generated header section is to provide the bit-layout ABI used by AMDGPU Display Core and audio/display integration code for DCN 3.1.4 hardware registers. Companion generated headers provide register addresses and instance maps; this file provides the field positions and masks used by register helper macros to pack, update, and decode register values without embedding literal bit numbers in functional driver code.

Major hardware areas represented here:

- `dce_dc_hda_azcontroller_azdec`: HDA/Azalia controller ring-buffer and immediate-command fields, including CORB/RIRB pointers, DMA engine enables, memory-error status, response interrupt controls, command busy/result-valid state, and DMA position-buffer base addresses.
- Legacy VGA indexed blocks: sequencer (`SEQ00`-`SEQ04`), CRTC (`CRT00`-`CRT22` subset), graphics controller (`GRA00`-`GRA08`), and attribute controller (`ATTR00`-`ATTR14`) masks for reset, clocking, plane maps, font selection, timing totals, blank/sync ranges, cursor, addressing mode, graphics write/read mode, palette, panning, and color-select fields.
- `azendpoint_sinkinfoind`: display sink identity and text description fields, including manufacturer/product IDs, description length, port IDs, and 18 one-byte sink description registers.
- Azalia input/output CRC result blocks: `AZALIA_INPUT_CRC0/1_CHANNEL0..7` and `AZALIA_CRC0/1_CHANNEL0..7`, each exposing full-width 32-bit CRC readbacks per channel.
- `azf0stream0_streamind` through `azf0stream15_streamind`: repeated stream FIFO sizing and latency-counter fields for 16 audio streams, including min/max FIFO size, max latency support, latency counter reset, worst-case/cumulative latency counts, and cumulative request counts.
- `azf0endpoint0_endpointind`, `azf0endpoint1_endpointind`, and the in-scope part of `azf0endpoint2_endpointind`: HDMI/DP audio codec converter and pin-control fields for widget capabilities, stream format, channel/stream IDs, digital converter status/control, supported rates, stripe/ramp/GTC timing, pin capabilities, unsolicited responses, ELD/sink info, hot-plug audio enable, configuration default, multichannel routing, IEC 60958 channel-status overrides, LPIB snapshots, coding type, and format-change status.

## Important Definitions

The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit index.
- `<REGISTER>__<FIELD>_MASK` gives the field's unshifted bitmask in the register value.
- `// addressBlock: ...` comments delimit hardware address blocks.
- `//<REGISTER>` comments group each register's field macros.

Important field families in this chunk:

- HDA ring/control fields: `AZCONTROLLER0_CORB_*`, `AZCONTROLLER0_RIRB_*`, `AZCONTROLLER0_RESPONSE_INTERRUPT_COUNT`, and immediate command/response fields define command output ring buffer, response input ring buffer, DMA enable, pointer reset, response overrun, and immediate verb/result access. DMA position buffer base-address fields also expose the low-bit enable and unimplemented alignment bits.
- VGA compatibility fields: `SEQ*`, `CRT*`, `GRA*`, and `ATTR*` define classic VGA control masks. These are low-width fields, often byte-sized, and include timing bit splits such as CRTC vertical total/display/sync high bits in `CRT07` and addressing/scan mode fields in `CRT09`, `CRT14`, and `CRT17`.
- Sink identity and ELD-style description fields: `AZALIA_F2_CODEC_PIN_CONTROL_*`, `SINK_DESCRIPTION0..17`, and endpoint `SINK_INFO0..8` macros expose manufacturer/product IDs, port IDs, description length, and packed description bytes.
- CRC result fields: input CRC and CRC result registers are full-width readbacks, one 32-bit mask per channel. These are diagnostic/validation fields rather than configuration controls.
- Stream latency and FIFO fields: each `AZF0STREAMN_AZALIA_FIFO_SIZE_CONTROL` has min FIFO size, max FIFO size, and max-latency-support fields; each stream also has reset and full-width worst-case/cumulative latency and request counters.
- Codec converter fields: endpoint converter capability, format, channel stream ID, digital converter, stream format, supported size/rate, stripe control, ramp rate, and GTC embedding/counter-delta fields map HDA codec verbs to hardware audio converter state.
- Pin capability and control fields: pin widget capability, jack/output/input/HDMI/DP capability, unsolicited response, pin sense, widget output enable, channel/speaker allocation, lipsync, HBR, hot-plug audio enable, and configuration-default fields describe and control HDMI/DP audio pins.
- Audio descriptor and multichannel fields: endpoint audio descriptor 0-13 groups describe max channels, supported frequencies, and descriptor byte 2; multichannel enable/mute/channel-id fields route channel pairs or individual odd channels.
- IEC 60958 channel-status override fields: `CODEC_CS_OVERRIDE_0..8` define source number, clock accuracy, word length, sampling frequency, original sampling frequency, CGMS-A, MPEG surround info, and channel-number overrides.
- Runtime audio-position and format fields: LPIB snapshot lock/wrap count, LPIB, LPIB timer snapshot, coding type, format-changed flag, format-change reason, and format-change response fields support audio position accounting and dynamic audio-format change reporting.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when AMDGPU Display Core, DC audio, or HDA-related code combines these constants with matching DCN 3.1.4 register addresses and register access helpers. A typical usage pattern is:

1. Driver code chooses an Azalia controller, stream, endpoint, or VGA register offset from a companion generated register header/table.
2. The caller uses this chunk's `_SHIFT` and `_MASK` values through helper macros such as field pack/update/get operations.
3. The display register layer performs an MMIO read, write, or read/modify/write.
4. Hardware stores persistent configuration, returns volatile status/counter data, or consumes side-effecting command/reset/clear bits.

The state represented here is hardware register state, not driver-owned memory:

- Persistent configuration includes CORB/RIRB base/pointer/control settings, stream FIFO/latency support settings, converter formats, stream IDs, digital converter state, pin widget controls, channel/speaker allocation, hot-plug audio enable, multichannel routing, channel-status overrides, and configuration defaults.
- Volatile readback includes command busy/result-valid state, memory-error indications, response interrupt/overrun status, CRC results, latency counters, request counters, pin sense, HBR capability/status, output active state, LPIB snapshots, coding type, and format-change status.
- Side-effecting write paths include pointer resets, DMA engine enables, response interrupt controls/clears, immediate command writes, latency counter reset, unsolicited response force, LPIB snapshot lock, format-change acknowledge/response fields, and interrupt-like audio enable/disable/format-change status fields in the complete endpoint blocks.
- Repeated stream and endpoint definitions are instance-specific. The macros themselves do not enforce that endpoint 0, 1, or 2 is wired to a particular connector; caller-side resource mapping must choose the correct register instance.

## Dependencies And Integration Points

This chunk depends on generated-name consistency across the DCN 3.1.4 register header family. It is normally consumed together with matching DCN 3.1.4 offset/address headers, generated register-list tables, and the AMDGPU Display Core register helper layer.

Primary integration points include:

- HDA/Azalia controller bring-up paths that program CORB/RIRB DMA, ring pointers, immediate codec verbs, response interrupts, and DMA position-buffer reporting.
- HDMI/DisplayPort audio code that configures codec converter formats, stream/channel IDs, digital converter bits, supported rate/size capabilities, pin widgets, ELD/sink information, speaker/channel allocation, HBR, and lipsync data.
- Audio stream accounting and debug paths that consume FIFO-size capability fields, latency counters, request counters, LPIB snapshots, coding type, and format-change flags.
- Hot-plug and connector-audio integration that updates sink manufacturer/product/port/description fields, pin configuration defaults, hot-plug audio enable state, unsolicited responses, and remote/format-change notification fields in the larger endpoint blocks.
- Display validation tooling that reads input/output CRC channel registers and sink/audio descriptor state.
- Legacy VGA emulation or compatibility paths that program sequencer, CRTC, graphics-controller, and attribute-controller indexed fields during early display or fallback modes.
- Power-management and reset sequences that must coordinate HDA DMA engine state, stream counter resets, endpoint hot-plug audio enable, and volatile status readbacks across suspend/resume or display block gating.

Because these are macros, missing or renamed fields generally fail at compile time only where referenced. Incorrect numeric masks or shifts can compile successfully and then misprogram MMIO registers at runtime.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.1.4 register specification is the central risk. A wrong mask or shift can alter the wrong register bits, affecting HDA command transport, ring DMA, HDMI/DP audio format, sink reporting, interrupts, or diagnostics.
- The file is generated and highly repetitive. Stream `AZF0STREAM0..15` and endpoint `AZF0ENDPOINT0..2` definitions share almost identical field layouts; prefix mistakes can target the wrong stream or endpoint while still compiling if the mistaken macro exists.
- The requested chunk boundary is not a full logical file boundary. It stops after endpoint 2 format-change masks; endpoint 2 wireless-display identification and later fields are visible immediately after the requested range and must be covered by a later chunk.
- Side-effecting bits require careful writes. Pointer reset, latency counter reset, interrupt clear/ack/mask/type, unsolicited response force, LPIB snapshot lock, and format-change response fields should not be toggled accidentally by generic read/modify/write updates.
- Ring-buffer and DMA-position base-address fields include unimplemented/alignment bits. Callers must preserve alignment semantics and avoid treating low address bits as usable address data.
- Format and stream-ID fields have cross-register dependencies. Converter format, channel/stream ID, pin output enable, multichannel routing, and speaker allocation must agree with the audio stream descriptor and display link mode.
- Sink description fields are split across byte or packed-byte registers. Length handling and byte ordering must match the hardware contract, or ELD/sink identity reported to audio clients can become inconsistent.
- Full-width CRC, counter, LPIB, and GTC fields have no type or range checking at the macro layer. Callers must interpret wraparound, snapshot locking, and read ordering correctly.
- Legacy VGA fields are narrow and historically overloaded. Reusing them without respecting indexed-register semantics, split timing bits, and reset/clock dependencies can break compatibility display paths.

## Test Signals

Useful validation for this chunk is mostly generated-header consistency plus hardware/display-audio behavior:

- Build AMDGPU/DCN 3.1.4 code and ensure all referenced generated macro names from this range resolve.
- Run generated-header checks that each in-scope field has the expected `_SHIFT` and `_MASK` pair, masks fit in 32 bits, and fields do not overlap unexpectedly inside a register.
- Compare generated values against the authoritative DCN 3.1.4 register specification, with special attention to repeated stream/endpoint prefixes and the endpoint 2 chunk boundary.
- Exercise HDA/Azalia command transport by programming CORB/RIRB DMA, resetting pointers, issuing immediate commands, and checking busy/result-valid, response interrupt, overrun, and memory-error status behavior.
- Validate HDMI/DP audio modes across endpoints 0 and 1 and the in-scope endpoint 2 fields, checking converter format, stream/channel IDs, digital converter enable/status, supported rates, pin output enable, speaker/channel allocation, HBR, lipsync, and hot-plug audio enable.
- Run audio latency/accounting diagnostics that reset and read worst-case/cumulative latency and request counters for streams 0-15.
- Exercise ELD/sink information paths and confirm manufacturer/product IDs, port IDs, description length, description bytes, audio descriptors, and configuration defaults are packed as expected.
- Read CRC result registers under known audio/display validation scenarios and confirm per-channel input/output CRC values are stable and correctly decoded.
- Test LPIB snapshot paths, including snapshot lock, wrap count, LPIB value, timer snapshot, and coding-type readbacks.
- Trigger audio format-change paths and confirm format-changed flags, acknowledge/UR-enable, reason, and response fields behave as expected for the endpoint blocks covered by this chunk.
- Smoke-test legacy VGA fallback or early-display paths that touch sequencer, CRTC, graphics, and attribute indexed registers.
- Run suspend/resume or runtime power tests with active display audio to ensure DMA, stream counters, endpoint state, and volatile status readbacks recover correctly.

## Chunk-Specific Summary

Lines 1-2578 define the opening DCN 3.1.4 register mask/shift surface rather than executable logic. The chunk's most important responsibilities are Azalia controller command/ring transport, legacy VGA indexed-register compatibility, sink/CRC readbacks, 16 stream FIFO and latency-counter blocks, and endpoint 0/1 plus partial endpoint 2 HDMI/DP audio codec converter and pin-control metadata. Correctness depends on exact generated masks and shifts, instance-correct macro use, careful handling of side-effecting command/reset/interrupt fields, and hardware tests that cover HDA command transport, HDMI/DP audio setup, ELD/sink reporting, stream latency counters, CRC diagnostics, LPIB snapshots, format-change notification, and VGA compatibility paths.

### subset-b-001834: lines 2579-4946

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

### subset-b-001835: lines 4947-7218

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 4947-7218

## Scope

This chunk is a generated AMD DCN 3.1.4 register shift/mask table for Azalia/HDA audio endpoint fields. The reviewed span contains 2,024 preprocessor definitions, almost entirely paired `__SHIFT` and `_MASK` constants, and no C functions, structs, enums, storage, or executable control flow. It starts in the `AZF0ENDPOINT7` output endpoint pin-control register set and then covers repeated `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7` input endpoint field maps.

The header belongs to the AMDGPU display register contract. It is consumed with the paired `dcn_3_1_4_offset.h` register/index definitions and with register helper macros such as `FD_MASK`, `FD_SHIFT`, `SF`, `REG_SET`, and the Azalia indirect access path in display audio code.

## Purpose

The chunk gives bit positions and masks for DCN 3.1.4 Azalia codec endpoint registers. These constants let driver code pack, unpack, read, and update fields inside HDA/HDMI/DP audio endpoint registers without embedding literal bit arithmetic at every call site.

The output endpoint 7 section describes fields for advertised sink/audio capabilities and runtime audio state, including unsolicited response control, pin sense, widget output enable, channel and speaker allocation, audio descriptors, multichannel routing, lipsync, HBR capability, sink identity strings, hot-plug audio enable, configuration default, channel-status overrides, LPIB snapshots, format-change notifications, wireless display identification, remote keepalive, and audio enable/disable interrupt status fields.

The input endpoint sections describe repeated per-endpoint converter and input-pin fields. Each endpoint has fields for audio widget capabilities, converter format, channel/stream ID, digital converter status, supported formats/rates, input-pin capabilities, unsolicited response handling, pin sense, widget input enable, multichannel enable/mute/channel IDs, HBR response, channel allocation, hot-plug audio enable, configuration default, LPIB snapshot registers, input activity status, and infoframe metadata.

## Important Definitions

The key API surface is the macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the right-shift count for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted in-register bit mask for that field.
- Register names beginning with `AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_` apply to the output endpoint 7 pin-control/codec endpoint namespace.
- Register names beginning with `AZF0INPUTENDPOINT<n>_AZALIA_F0_CODEC_INPUT_` apply to input endpoint `n`, where this chunk covers `0` through `7`; endpoint 7 starts here but continues after this chunk.

Important output endpoint 7 groups:

- `*_UNSOLICITED_RESPONSE`: `TAG` and `ENABLE` fields for HDA unsolicited responses.
- `*_RESPONSE_PIN_SENSE`: output pin impedance sense.
- `*_WIDGET_CONTROL`: `OUT_ENABLE`.
- `*_CHANNEL_SPEAKER`: speaker allocation, channel allocation, HDMI/DP connection flags, extra connection info, LFE playback level, level shift, and downmix inhibit.
- `*_AUDIO_DESCRIPTOR0` through `*_AUDIO_DESCRIPTOR13`: maximum channels, supported frequencies, descriptor byte 2, and for descriptor 0 the stereo frequency byte.
- `*_MULTICHANNEL_ENABLE` and `*_MULTICHANNEL_ENABLE2`: enable/mute/channel-ID fields for even and odd multichannel lanes.
- `*_RESPONSE_LIPSYNC`, `*_RESPONSE_HBR`, `*_SINK_INFO0` through `*_SINK_INFO8`: video/audio latency, high-bit-rate audio capability/enablement, EDID-derived manufacturer/product IDs, port IDs, and display-name bytes.
- `*_HOT_PLUG_CONTROL`: clock-gating disable, clock-on state, and `AUDIO_ENABLED`.
- `*_RESPONSE_CONFIGURATION_DEFAULT`: HDA pin default fields such as sequence, association, misc, color, connection type, default device, location, and port connectivity.
- `*_PIN_CONTROL_CODEC_CS_OVERRIDE_*`: channel-status override bytes and validity bits.
- `*_LPIB*`, `*_CODING_TYPE`, `*_FORMAT_CHANGED`, `*_REMOTE_KEEPALIVE`, and `*_AUDIO_*_INT_STATUS`: DMA position/status, stream format change, keepalive, and audio interrupt status fields.

Important repeated input endpoint groups:

- `*_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: converter widget feature flags such as amplifier presence, format override, digital, power control, unsolicited-response capability, delay, and type.
- `*_CODEC_INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`: number of channels, bits per sample, base divisor/multiple/rate, and stream type.
- `*_CODEC_INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID`: channel ID and stream ID.
- `*_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`: digital enable/status, validity, copyright/non-audio/professional flags, category code, and keepalive.
- `*_CODEC_INPUT_CONVERTER_PARAMETER_STREAM_FORMATS` and `*_SUPPORTED_SIZE_RATES`: supported stream formats, sample rates, and sample sizes.
- `*_CODEC_INPUT_PIN_PARAMETER_*`: pin widget and pin capability maps for HDMI/DP-style digital input pins.
- `*_CODEC_INPUT_PIN_CONTROL_*`: runtime control/status registers for input pin unsolicited response, pin sense, widget input enable, multichannel layout, HBR, hot-plug, defaults, LPIB, input activity, and infoframe state.

## Control Flow

There is no local control flow in this chunk. All behavior is compile-time macro expansion.

At runtime, audio code writes endpoint-internal Azalia registers indirectly. In `dce_audio.c`, `AZ_REG_READ(reg_name)` and `AZ_REG_WRITE(reg_name, value)` expand an `ix...` endpoint register index, write it into `AZALIA_F0_CODEC_ENDPOINT_INDEX`, then read or write `AZALIA_F0_CODEC_ENDPOINT_DATA`. The register data values are assembled with helper macros that use the shift/mask definitions from ASIC-specific generated headers.

For DCN 3.1.4, `dcn314_resource.c` includes `dcn/dcn_3_1_4_offset.h` and this header, builds `audio_regs[]` through `AUD_COMMON_REG_LIST(id)`, and builds `audio_shift`/`audio_mask` through `SF(..., __SHIFT)` and `SF(..., _MASK)` expansion. `dce_audio_create()` receives those tables so common DCE audio code can operate on the DCN 3.1.4 register layout.

## State and Persistence

The header itself owns no state and persists nothing. Its values describe hardware register layout, so state is held in the DCN/Azalia hardware blocks:

- Endpoint index/data registers select and expose endpoint-internal HDA codec registers.
- Audio descriptor and sink-info registers cache EDID-derived audio capabilities and display identity for the hardware/OS audio path.
- Hot-plug and unsolicited-response bits control whether audio activity and notification state are visible to higher layers.
- LPIB and timer snapshot fields report live buffer position/timing state.
- Interrupt status fields represent hardware-latched audio enable/disable/format-change events.

Persistence across boot or suspend is not handled here. Correct restoration depends on DC resource construction and audio configuration paths reprogramming these registers when display/audio state changes.

## Dependencies

Primary dependencies:

- `dcn_3_1_4_offset.h` supplies the matching register addresses, base indices, and endpoint internal indexes.
- `reg_helper.h` and AMD display helper macros consume `__SHIFT`/`_MASK` pairs for register packing.
- `drivers/gpu/drm/amd/display/dc/dce/dce_audio.c` performs generic Azalia endpoint reads/writes and uses HDA/HDMI/DP audio fields such as descriptors, sink info, HBR, lipsync, hot-plug audio enable, and channel allocation.
- `drivers/gpu/drm/amd/display/dc/dce/dce_audio.h` defines the audio register/shift/mask table shapes and common audio register list macros.
- `drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c` binds DCN 3.1.4 generated offsets and masks into the display resource pool's audio object construction.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c` and `drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c` include the same generated DCN 3.1.4 offset and mask headers for other register-table and IRQ setup paths.

This chunk is also coupled to adjacent generated ASIC generations such as DCE 12.0 and DCN 3.2.0, which carry similar Azalia macro families. That similarity is useful for consistency checks but also means copy/generation errors can propagate.

## Integration Points

The audio integration path is:

1. DCN 3.1.4 resource construction selects generated register addresses and masks for each audio instance.
2. Common DCE audio code selects endpoint-internal Azalia indexes with `AZALIA_F0_CODEC_ENDPOINT_INDEX`.
3. Common DCE audio code reads/writes `AZALIA_F0_CODEC_ENDPOINT_DATA`.
4. The fields described in this chunk shape payloads for HDMI/DP audio capability advertisement, hot-plug audio enablement, multichannel layout, HBR support, sink identity, lipsync, and status reporting.

The chunk's output endpoint 7 fields are especially relevant to display connector audio programming and sink capability exposure. The input endpoint blocks are repeated hardware surfaces for capture/input-style audio endpoint handling and status, even when most display paths primarily exercise output endpoint codec controls.

## Risks

- Bitfield drift: any incorrect mask or shift silently corrupts hardware register programming. Failures can appear as missing HDMI/DP audio, wrong channel count, unsupported format advertisement, broken HBR audio, stale sink names, or lost unsolicited responses.
- Paired-header mismatch: these macros must match `dcn_3_1_4_offset.h` register indexes. A correct field mask with an incorrect index still writes the wrong endpoint-internal register.
- Repetition errors: the input endpoint 0-7 blocks are mechanically repeated. A single endpoint-specific typo can break only one pipe/endpoint and be missed in broad testing.
- Width/type assumptions: masks use `L` suffixed constants and include high-bit values such as `0x80000000L` and full-width `0xFFFFFFFFL`; call sites should keep using unsigned 32-bit register values to avoid sign-extension surprises.
- Chunk boundary: endpoint 7 input support is partial in this chunk; the input endpoint 7 pin-parameter/control definitions continue after line 7218. Whole-file reconciliation must merge neighboring chunks before making conclusions about endpoint 7 completeness.
- Generated-file maintainability: hand edits are risky. Updates should come from the ASIC register generation source so offset and mask headers remain synchronized.

## Test Signals

Useful validation signals for changes affecting this chunk:

- Kernel build coverage for DCN 3.1.4 paths, especially expansion of `dcn314_resource.c`, `dmub_dcn314.c`, and `irq_service_dcn314.c` against this header.
- Static comparison against adjacent known-good generated headers, especially DCE 12.0/DCN 3.2.0 Azalia endpoint field maps, to catch missing or shifted fields.
- Runtime HDMI/DP audio smoke tests on DCN 3.1.4 hardware: audio device enumeration, hot-plug/replug, enable/disable, suspend/resume, monitor-name propagation, and multi-display endpoint selection.
- EDID audio capability tests for PCM and compressed formats to confirm descriptor fields, supported frequencies, channel counts, and HBR capability are advertised correctly.
- Multichannel playback tests for 2-channel, 6-channel, and 8-channel layouts to validate channel/speaker allocation and multichannel enable/channel-ID fields.
- Interrupt/status tests for audio format-change and enable/disable events if the platform exposes those paths.

## Open Questions for Merge

- Confirm in neighboring chunks whether all output endpoints 0-7 have the same pin-control field coverage and whether endpoint 7 is intentionally the last output endpoint in this generation.
- Confirm after line 7218 that `AZF0INPUTENDPOINT7` has the same input pin-control tail as endpoints 0-6.
- Cross-check the generated DCN 3.1.4 Azalia endpoint field set against the hardware register database used to generate `dcn_3_1_4_offset.h` and `dcn_3_1_4_sh_mask.h`.

### subset-b-001836: lines 7219-9704

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 7219-9704

## Scope

This chunk is a generated AMD Display Core Next 3.1.4 register-field mask slice. It contains C preprocessor constants only: `_SHIFT` macros for field least-significant-bit positions, `_MASK` macros for raw 32-bit field masks, and comment markers that group those definitions by hardware register and address block. There are no C functions, structs, enums, variables, branches, loops, allocations, locks, or direct MMIO accesses in this range.

The requested range begins in the `AZF0INPUTENDPOINT7` HD-audio input endpoint pin definitions after the input-converter stream-format and supported-size/rate fields from the prior chunk. It then covers audio descriptor index registers, legacy VGA/MMHUBBUB register fields, HDA/Azalia immediate-command endpoint registers, a large DCCG display clock-generation and gating block, an Azalia F2 codec/output-pin/input-pin register surface, and ends at the first register of the DC perfmon0 block, `DC_PERFMON0_PERFCOUNTER_CNTL`. The following `DC_PERFMON0_PERFCOUNTER_CNTL2` group starts after the requested line boundary.

## Purpose And Hardware Surface

The purpose of this header range is to provide the bit layout ABI between AMDGPU display code and DCN 3.1.4 display hardware. Companion generated offset headers provide the register addresses; this mask header provides the field positions and masks that register helper macros use to pack values, extract readback fields, and perform read/modify/write operations without embedding numeric bit positions in functional code.

Major hardware areas represented here:

- `AZF0INPUTENDPOINT7` input pin metadata and controls for an HDA/Azalia input endpoint. These fields describe audio widget capabilities, pin capabilities, unsolicited responses, pin sense, widget enable state, multichannel enable/mute/channel IDs, HBR capability/enable, channel allocation, hot-plug audio state, configuration defaults, LPIB snapshots, input activity, infoframe state, and channel status.
- `azendpoint_descriptorind` audio descriptor registers `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`. Each descriptor exposes short audio descriptor fields such as channel count, sample-rate mask, byte slots, format code, bit-rate/code fields, and maximum bit rate for HDMI/DP audio capability advertisement.
- `dce_dc_mmhubbub_vga_dispdec[72..76]` and `dce_dc_mmhubbub_vga_dispdec` legacy VGA/MMHUBBUB fields. These include VGA memory page addressing, render/control state, sequencer reset/control, VGA modes, pitch and surface addresses, HDP/cache controls, per-pipe VGA controls, interrupt/status/clear fields, CRTC/attribute/graphics sequencer indexed ports, DAC access, source select, QoS, and test controls.
- HDA immediate command output/input endpoint register pairs for Azalia endpoint and input endpoint data/index access.
- `dce_dc_dccg_dccg_dispdec` display clock-generation fields. The chunk covers PHYPLL pixel-clock resync controls, DP DTO/DBUF enables, DSC/DPP/DTB/audio DTO parameters, clock gating/test toggles, gate-disable controls, stream-clock controls, global fine-grain clock-gating reporting, GTC DTO/current controls, millisecond/microsecond timebase dividers, display clock frequency-change controls, memory power requests, CAC/status, pixel-rate controls for OTG0-OTG3, symbol-clock controls/enables, DCCG soft reset, vsync latch/counter controls, HDMI/PHY stream clock controls, DMCUB clock control, and dentist DISPCLK control.
- `AZALIA_F2` codec root, function, converter, output pin, and input endpoint fields. These definitions expose HDA codec identity/capability data, function power/reset/synchronization controls, converter format/channel/digital-converter controls, widget capability/rate/format parameters, output pin connection/widget/unsolicited/pin-sense/configuration/default/speaker/channel-allocation/multichannel/LPIB/status/keepalive controls, input converter controls, and input pin activity/infoframe/channel-status/capability fields.
- The first `dce_dc_dccg_dccg_dcperfmon0_dc_perfmon_dispdec` performance counter control register. `DC_PERFMON0_PERFCOUNTER_CNTL` selects the event, counted value, increment mode, hardware/run-enable behavior, restart/interrupt/off-mask behavior, active status, and counter control selection.

## Important Definitions

The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit index.
- `<REGISTER>__<FIELD>_MASK` gives the field's raw mask within the 32-bit register.
- `// addressBlock: ...` comments identify the display hardware aperture for following definitions.
- `//<REGISTER>` comments group field definitions by MMIO register.

Important field families in this chunk:

- Azalia input endpoint pin fields include `AUDIO_WIDGET_CAPABILITIES`, `CAPABILITIES`, `UNSOLICITED_RESPONSE`, `RESPONSE_INPUT_PIN_SENSE`, `WIDGET_CONTROL`, `MULTICHANNEL_ENABLE`, `MULTICHANNEL_ENABLE2`, `RESPONSE_HBR`, `CHANNEL_ALLOCATION`, `HOT_PLUG_CONTROL`, `UNSOLICITED_RESPONSE_FORCE`, `RESPONSE_CONFIGURATION_DEFAULT`, `LPIB`, `INPUT_STATUS_CONTROL`, `INFOFRAME`, and channel-status readbacks. These are the bit-level contract for input audio pin discovery, routing, event reporting, and stream status.
- Audio descriptor fields are repeated for descriptors 0 through 13. Each register carries `MAX_CHANNELS`, `SUPPORTED_FREQUENCIES`, `DESCRIPTOR_BYTE_2`, `FORMAT_CODE`, `SUPPORTED_CODECS`, `DESCRIPTOR_BYTE_3`, and `MAX_BIT_RATE`, allowing the driver or firmware to expose sink audio capabilities through indexed descriptor storage.
- VGA fields cover stateful legacy display emulation. Key controls include render enable/stop status, graphics/address mode, chain/odd-even modes, host read/write select, surface pitch/address selection, memory base high/low, HDP enable/flush/invalidation, cache enable/flush/invalid flags, per-pipe VGA enable/mode/source control, interrupts, status clears, source select, and indexed VGA I/O register data paths.
- DCCG clocking fields are broad and timing-sensitive. The block includes pixel clock resync bypass/enable/status for PHYPLLA-E, stream clock source/enables, DP DTO phase/modulo controls, DSC/DPP/DTB/audio DTO phase/modulo and source controls, gate-disable fields for DISPCLK, DPPCLK, DSCCLK, DTO clocks, PHY/SYM clocks, HDMI character/stream clocks, DMCUBCLK, and fine-grain/CGTT clock-gating controls.
- DCCG timing counters and synchronization fields include GTC DTO increment/modulo/current, millisecond and microsecond time-base divisors, vsync latch values for OTG0-OTG5, vsync counter control/int control, and dentist DISPCLK divider controls. These fields feed timing correlation, firmware services, and clock-domain synchronization.
- DCCG power and reset fields include display clock frequency-change control, memory global power request control, DCCG soft-reset bits for clock slices, global fine-grain clock-gating reporting, CAC status, and clock-on-state or enable readbacks. These fields interact with runtime power management and safe clock transitions.
- Azalia F2 codec root/function fields expose vendor/device/revision/subordinate-node data, power states, subsystem ID response bytes, converter synchronization, function reset, group type, supported sample sizes/rates, stream formats, and power-state capability masks.
- Azalia F2 converter fields program HDA stream format and routing: stream type, sample base rate/multiple/divisor, bits per sample, channel count, channel/stream ID, digital-converter status bits, stripe control, ramp rate, GTC embedding, widget capabilities, supported sizes/rates, and stream format masks.
- Azalia F2 output pin fields cover widget enable, unsolicited response, pin sense, configuration defaults split across multiple byte-oriented registers, speaker allocation, channel allocation, down-mix inhibit, audio descriptor selection/data, multichannel pair and single-channel controls, lipsync, HBR, audio sink info index/data, channel-status overrides, association info, digital output status, LPIB snapshots, coding type, format-change notification/response, wireless-display identification, remote keepalive, and pin capability/readback data.
- Azalia F2 input endpoint fields mirror the input path: converter format/channel/digital-converter controls, widget capability/rate/format parameters, input pin widget and unsolicited-response controls, pin sense and configuration defaults, channel allocation, per-channel multichannel enable/mute/channel ID fields, HBR, LPIB, input activity/change unsolicited-response enables, infoframe validity/channel allocation, channel-status readbacks, and input pin capability masks.
- `DC_PERFMON0_PERFCOUNTER_CNTL` fields identify one hardware performance counter's event select, counted-value select, increment mode, hardware control select, run-enable mode, count-off start disable, restart enable, interrupt enable, off mask, active status, and counter-control select.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears only when AMDGPU Display Core, DMUB support code, or related generated register tables combine these macros with register offsets and MMIO helper APIs. A typical usage pattern is:

1. Select a DCN 3.1.4 register address from the companion generated offset table.
2. Use this chunk's `_SHIFT` and `_MASK` constants to pack or extract a field value.
3. Read, write, or update the register through display register helpers or firmware register tables.
4. Let display hardware retain configuration fields, update status fields, or consume side-effecting command/clear bits.

The state represented here is hardware register state rather than driver-owned memory:

- Persistent configuration fields include Azalia stream formats, channel/stream IDs, multichannel enable/mute/channel IDs, HBR enable, channel allocation, descriptor contents, VGA render/mode/cache/HDP/source selections, DCCG clock source and DTO parameters, clock gating disables, soft-reset controls, timebase dividers, function power state, converter synchronization, and perfmon event/control selects.
- Volatile readback/status fields include pin sense/presence, hot-plug audio enabled state, input activity, infoframe validity, LPIB and timer snapshots, VGA busy/stop/status/interrupt flags, cache/HDP flush-done state, clock-on/status bits, CAC status, vsync latches/counters, GTC current values, digital output status, format-changed state, and perfcounter active status.
- Side-effecting write fields include unsolicited-response force bits, VGA status clear and interrupt controls, cache/HDP flush or invalidation triggers, sequencer reset controls, DCCG soft-reset fields, frequency-change controls, vsync counter interrupt clears/masks, Azalia function reset, format-change acknowledgement/response fields, remote keepalive enable, LPIB snapshot lock, and perfcounter restart/interrupt enables.
- Indexed or indirect register paths need ordered access. VGA CRTC/attribute/graphics/sequencer index/data pairs and Azalia immediate-command index/data registers require callers to select an index before data access and to serialize against other users of the same indexed aperture.
- Clock and audio state are sequencing-sensitive. DCCG DTO parameters, stream-clock enables, gate disables, PHYPLL pixel-rate controls, audio DTO source/phase/module fields, and Azalia converter/pin controls must be coordinated with active links, stream enable/disable, audio packet programming, and power-gating transitions.

The masks do not encode ordering or locking requirements. Correct callers still need to hold the relevant display locks, respect register access domains, avoid touching clock-gated blocks prematurely, use update or reset sequencing where required, and avoid read/modify/write patterns that accidentally rewrite clear, force, reset, or trigger bits.

## Dependencies And Integration Points

This chunk is used with generated DCN 3.1.4 register headers and the AMD display register abstraction:

- `display/dmub/src/dmub_dcn314.c` includes both `dcn/dcn_3_1_4_offset.h` and this `dcn/dcn_3_1_4_sh_mask.h`, then builds DCN 3.1 register tables with field masks and shifts. This confirms the header participates in table-driven register access for DCN 3.1.4 DMUB support.
- Companion generated offset/address headers provide the `reg...` values that pair with these `_SHIFT` and `_MASK` macros.
- AMDGPU Display Core register helper macros consume field names through generated tables for `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, `FD_SHIFT`, and similar access patterns.
- Display audio and HDMI/DP audio code depends on the Azalia F0/F2 codec, converter, pin, descriptor, channel-allocation, HBR, LPIB, infoframe, channel-status, and sink-info definitions to program audio routing and expose HDA codec capabilities.
- Hot-plug and unsolicited-response handling integrates with pin sense, presence-detect, unsolicited-response tag/enable/force, format-changed, input-activity, and keepalive fields.
- Legacy VGA support and early boot/framebuffer handoff paths depend on the VGA render, memory, surface, pitch, source-select, indexed I/O, DAC, cache, HDP, status, and interrupt fields.
- Display clock management depends on DCCG fields for stream clocks, DTOs, pixel-rate divisions, PHYPLL resync, clock gating, soft reset, timebase generation, vsync latching/counters, dentist DISPCLK control, DMCUBCLK control, and audio clock DTO generation.
- Runtime power management and suspend/resume paths integrate with DCCG clock-on states, gate-disable controls, soft resets, memory power requests, frequency-change state, and Azalia power/reset fields.
- Diagnostics and performance tooling can use the DC perfmon0 counter control fields, DCCG CAC/status fields, clock status readbacks, VGA status, LPIB snapshots, and audio infoframe/channel-status readbacks.
- The related enum headers, such as `soc21_enum.h` and older generation enum headers, document semantic values for several Azalia F2 fields. This mask header only provides bit positions and masks, not the named field values.

Because these are generated macros, missing macro names generally fail at compile time only where referenced. Incorrect numeric masks or shifts can compile cleanly and then misprogram display hardware at runtime.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.1.4 register specification is the primary risk. A wrong shift or mask can write the wrong bit in clock, VGA, audio, or perfmon hardware, causing display audio failures, clock instability, legacy VGA breakage, or invalid performance counter results.
- The chunk contains several repetitive blocks. Audio descriptors 0-13, multichannel controls, per-channel enable registers, and repeated DCCG pixel-rate/DTO controls are vulnerable to copy-generation or prefix mistakes that still compile if the wrong macro name exists.
- The range starts and ends mid-topic. It begins after prior `AZF0INPUTENDPOINT7` input-converter fields and ends after `DC_PERFMON0_PERFCOUNTER_CNTL`, before `DC_PERFMON0_PERFCOUNTER_CNTL2`. The merge lane must combine adjacent chunks for a complete per-file picture.
- Side-effecting fields require care with read/modify/write helpers. Unsolicited-response force, reset, clear, flush, invalidate, interrupt clear, status clear, restart, and snapshot lock fields should not be accidentally rewritten while changing adjacent configuration bits.
- Clock-generation fields are highly timing-sensitive. Bad DTO phase/modulo, pixel-rate divider, stream-clock source, gate-disable, soft-reset, or dentist DISPCLK values can break active display pipes or audio clocking in ways that are not caught by compile-time checks.
- Audio routing fields must match the active connector, stream, and sink. Incorrect stream format, channel count, channel allocation, HBR, audio descriptor, infoframe, LPIB, or channel-status values can produce silent audio, malformed HDMI/DP audio metadata, or unstable hot-plug behavior despite normal video output.
- Indexed VGA and HDA immediate-command accesses can be corrupted by interleaving. Callers need serialization around index/data register pairs or descriptor-indirect paths.
- Legacy VGA fields interact with boot firmware state and framebuffer handoff. Incorrect render stop, memory mapping, surface address, cache/HDP invalidation, or source selection can disrupt console takeover or low-level modesetting.
- Full-width or wide fields such as descriptor data, LPIB snapshots, channel status, GTC/current counters, DTO phase/modulo values, surface addresses, and perfcounter event fields provide no type or range checking here. Callers must validate units and ranges before packing values.
- Power and reset state can make readbacks unreliable. Clock-on, busy, reset, and gate states must be sequenced before trusting DCCG, VGA, or Azalia status bits.

## Test Signals

Useful validation signals for this chunk are mostly generated-header checks plus hardware-facing display/audio behavior:

- Build AMDGPU with DCN 3.1.4 and DMUB support enabled and confirm all referenced generated field names resolve.
- Run generated-header consistency checks that every in-scope field has the expected `_SHIFT`/`_MASK` pair, masks fit within 32 bits, and fields do not overlap unexpectedly within each register.
- Compare the generated values against the authoritative DCN 3.1.4 register specification, with special attention to repeated descriptor, multichannel, DCCG DTO, and gate-disable blocks.
- Exercise HDMI and DisplayPort audio playback across common formats, channel counts, sample rates, HBR modes, and hot-plug cycles; verify audio descriptors, channel allocation, infoframes, channel status, LPIB snapshots, and converter stream IDs behave as expected.
- Test audio input/status paths where hardware exposes them, checking input activity, channel layout, input infoframe validity, channel status readbacks, unsolicited-response enables, and pin-sense/presence behavior.
- Validate Azalia codec enumeration and power transitions by checking vendor/device/revision/subordinate-node responses, power state handling, function reset, converter synchronization, and supported size/rate/format fields.
- Exercise legacy VGA handoff and console/modeset transitions, validating VGA render control, source selection, surface address/pitch, indexed CRTC/attribute/graphics/sequencer access, cache/HDP flush/invalidate behavior, and VGA interrupt/status clear behavior.
- Run display modesets over all relevant DCN 3.1.4 pipes while observing DCCG clock source, DTO phase/modulo, pixel-rate controls, PHYPLL resync status, stream-clock enables, and clock gating state.
- Test suspend/resume and runtime power-management transitions that toggle DCCG soft reset, gate-disable fields, DMCUBCLK, DISPCLK frequency-change controls, memory power requests, and Azalia power states.
- Validate vsync/GTC/timebase behavior by checking millisecond/microsecond dividers, GTC DTO/current values, vsync latch values for OTG0-OTG5, and vsync counter interrupt mask/type/status behavior.
- Use display diagnostics or perf tooling to program `DC_PERFMON0_PERFCOUNTER_CNTL`, select events, start/restart counting, enable interrupts where supported, and confirm active status and counted behavior match expectations.

## Chunk-Specific Summary

Lines 7219-9704 define a dense DCN 3.1.4 register-field mask surface, not executable logic. The chunk's most important responsibilities are HDA/Azalia F0 input endpoint pin status, indexed audio descriptors, legacy VGA/MMHUBBUB controls, HDA immediate command endpoints, DCCG clock/DTO/gating/timebase/reset controls, Azalia F2 codec/output/input endpoint fields, and the first DC perfmon0 control register. Correctness depends on exact generated masks and shifts, instance-correct macro use, careful handling of indexed and side-effecting registers, and hardware tests that cover display audio, hot-plug, VGA handoff, DCCG clock sequencing, power transitions, timing counters, and perfmon operation.

### subset-b-001837: lines 9705-12036

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 9705-12036

## Scope

This chunk is a generated DCN 3.1.4 register-field shift/mask slice from `dcn_3_1_4_sh_mask.h`. It contains preprocessor constants only: `_SHIFT` macros for field low-bit positions, `_MASK` macros for raw 32-bit register masks, and generated comments that group fields by MMIO register and address block. There are no C functions, structs, enums, loops, branches, allocations, or driver-owned state objects in this range.

The slice starts in the tail of `DC_PERFMON0_PERFCOUNTER_CNTL`, completes `DC_PERFMON0`, defines full `DC_PERFMON1` and `DC_PERFMON2` blocks, covers DC power-gating (`DCPG`) domain control/status and interrupt controls, covers DMU miscellaneous controls, covers the DMCU firmware/register/interrupt/mailbox register surface, and ends in the first `DISP_INTERRUPT_STATUS` fields in the DMU IHC block.

## Purpose And Hardware Surface

The purpose of this header range is to provide the bit-layout ABI between AMDGPU Display Core code and DCN 3.1.4 display hardware. Companion generated offset headers identify the MMIO register addresses; this header identifies each field's bit shift and mask so callers can pack values, decode readbacks, and perform read/modify/write updates through the display register helpers without embedding magic bit numbers.

Major hardware areas represented here:

- Display perfmon instances `DC_PERFMON0`, `DC_PERFMON1`, and `DC_PERFMON2`, including event selection, counter value selection, increment mode, hardware start/stop/count-off controls, per-counter state readback, global perfmon state, counter interrupts, and low/high counter readback windows.
- `dce_dc_dmu_dc_pg_dispdec` power-gating controls for domains 0-3 and 16-19, with force-on/gate controls, desired power-state readback, PGFSM power status, power-up/down interrupt status, interrupt mask/clear controls, and `DC_IP_REQUEST_CNTL`.
- `dce_dc_dmu_dmu_misc_dispdec` miscellaneous DMU controls, including DC pipe disable/DMCUB enable, DMU/DMCU/RBBMIF clock gating/status, DMCU ERAM/IRAM memory power controls, DMCU-to-SMU and SMU-to-DC interrupt registers, Z-state/SOC access controls, and deep-sleep force controls.
- `dce_dc_dmu_dmcu_dispdec` DMCU microcontroller controls, including reset, clock/soft reset, firmware address/checksum, RAM access windows for ERAM/IRAM, event triggers, uC internal/static-screen interrupt status, ABM, vblank, DCPG, OTG range timing, perfmon, DPRX, DCIO DPCS, and mailbox/communication registers.
- `dce_dc_dmu_ihc_dispdec` interrupt-host-controller fields, including GPU timer start-position/read controls and the first `DISP_INTERRUPT_STATUS` bits for OPTC underflow, OTG1 events, DP fast-training/stream-disable, HPD/AUX/I2C, DIO ALPM, RBBMIF timeout, DMCU, and ABM events.

## Important Definitions

The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a register field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted 32-bit mask for that field.
- `// addressBlock: ...` comments identify the display hardware aperture for following registers.
- `//<REGISTER>` comments group field macros by MMIO register.

Important field families in this chunk:

- `DC_PERFMON*_PERFCOUNTER_CNTL` fields expose `PERFCOUNTER_EVENT_SEL`, `PERFCOUNTER_CVALUE_SEL`, `PERFCOUNTER_INC_MODE`, `PERFCOUNTER_HW_CNTL_SEL`, `PERFCOUNTER_RUNEN_MODE`, `PERFCOUNTER_CNTOFF_START_DIS`, `PERFCOUNTER_RESTART_EN`, `PERFCOUNTER_INT_EN`, `PERFCOUNTER_OFF_MASK`, `PERFCOUNTER_ACTIVE`, and selector bits. Instance 0 begins mid-register at this chunk boundary; instances 1 and 2 are complete.
- `DC_PERFMON*_PERFCOUNTER_CNTL2` fields define counted value type, hardware stop selectors, count-off selector, and a high-bit selector. `DC_PERFMON*_PERFCOUNTER_STATE` packs eight 2-bit counter states with per-counter select bits.
- `DC_PERFMON*_PERFMON_CNTL` and `CNTL2` fields define perfmon state, report count, count-off interrupt AND/OR, interrupt enable/status/ack, clock enable, and run-enable start/stop selection. `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW` provide counter interrupt status/ack and 48-bit-style readback windows split across low/high registers.
- `DOMAIN{0,1,2,3,16,17,18,19}_PG_CONFIG` and `DOMAIN*_PG_STATUS` fields expose `DOMAIN_POWER_FORCEON`, `DOMAIN_POWER_GATE`, `DOMAIN_DESIRED_PWR_STATE`, and `DOMAIN_PGFSM_PWR_STATUS`.
- `DCPG_INTERRUPT_STATUS`, `DCPG_INTERRUPT_STATUS_2`, `DCPG_INTERRUPT_CONTROL_1`, and `DCPG_INTERRUPT_CONTROL_3` fields cover power-up/down events and mask/clear controls for power domains 0-3 and 16-19.
- `CC_DC_PIPE_DIS` fields disable DC pipes and expose `DC_DMCUB_ENABLE`. `DMU_CLK_CNTL` controls and reports clock-gating state for DMU, DMCU, and RBBMIF display clocks. `DMU_MEM_PWR_CNTL` controls DMCU ERAM/IRAM memory power force/disable/state.
- `DMCU_CTRL`, `DMCU_STATUS`, firmware address/checksum, and RAM access registers define the legacy display microcontroller control surface: uC reset/enable/status bits, PC/start/end/ISR addresses, checksum words, ERAM/IRAM read/write auto-increment windows, and host-read/write access controls.
- `DMCU_EVENT_TRIGGER`, `DMCU_UC_INTERNAL_INT_STATUS`, and `DMCU_SS_INTERRUPT_CNTL_STATUS` define event and microcontroller interrupt state for ABM, static screen, external SW, DCPG, vblank, and internal exception/read-timeout conditions.
- `DMCU_INTERRUPT_STATUS`, `DMCU_INTERRUPT_STATUS_1`, `DMCU_INTERRUPT_STATUS_CONTINUE`, and `DMCU_INTERRUPT_STATUS_2` are latched interrupt-status/clear registers. They cover ABM1-3 histogram/luma/backlight update events, MCP/external/SCP/uC events, DCPG domain power transitions for domains 0-21 across base/continue/2 registers, vblank 1-6, OTG range timing update 0-5, and DCIO DPCS TXA-TXG events.
- `DMCU_INTERRUPT_TO_HOST_EN_MASK`, `DMCU_INTERRUPT_TO_UC_EN_MASK*`, and `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL*` route the same display events either to host interrupt handling or to the DMCU/uC path and select XIRQ versus IRQ delivery.
- `MASTER_COMM_*` and `SLAVE_COMM_*` registers define 32-bit communication payload words split into two 16-bit fields, command bytes plus byte-valid bits, and simple control bits for host/uC mailbox-style command exchange.
- `DMCU_PERFMON_INTERRUPT_STATUS*`, `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK*`, and `DMCU_PERFMON_INTERRUPT_TO_UC_XIRQ_IRQ_SEL*` expose perfmon counter interrupts and routing for DMU, DIO, DCCG, HPO, HUBP0-7, HUBBUB, DPP0-7, WB0-2, MMHUBBUB, MPC, OPP, OPTC, HDA, and DSC0-5 blocks.
- `DMCU_DPRX_INTERRUPT_STATUS1`, `DMCU_DPRX_INTERRUPT_TO_UC_EN_MASK1`, and `DMCU_DPRX_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1` expose DisplayPort receiver-side events for two stream decoders (`SD0P0`, `SD1P0`) and DPHY/AUX conditions such as MSA received, VBID stream-status toggled, vertical interrupts, SDP received, BS/SR/symbol/disparity/training/test-pattern/ECF errors, SR lock detect, loss of align/deskew, excessive errors, deskew FIFO overflow, AUX/I2C/CPU interrupts, and AUX message timeouts.
- `DMCU_INT_CNT`, `DMCU_INT_CNT_CONTINUE`, `DMCU_INT_CNT_CONT2`, and `DMCU_INT_CNT_CONT3` provide 8-bit interrupt counters for ABM histogram/luma/backlight events across ABM instances.
- `DC_GPU_TIMER_START_POSITION_V_UPDATE`, `DC_GPU_TIMER_START_POSITION_VSTARTUP`, `DC_GPU_TIMER_READ`, and `DC_GPU_TIMER_READ_CNTL` define GPU timer start-position selection/readback fields for display pipes D1-D6 and VUpdate/VStartup/VSync nominal timing points.
- The trailing `DISP_INTERRUPT_STATUS` fields define top-level display interrupt bits for OPTC1 underflow, OTG1 snapshot/force-vsync/force-count/trigger/vsync-nom/DRR minimum-total events, DIGA DP fast-training and stream-disable events, HPD1/HPD1_RX, AUX1 SW/LS done, DIO ALPM, RBBMIF timeout, DC I2C SW done, DMCU internal/SCP, ABM1, and continuation chaining.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when AMDGPU Display Core code combines these constants with matching register offsets and helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, generated `DMUB_SR`/`DMUB_SF` tables, or similar display register-access wrappers.

A typical runtime path is:

1. Select the DCN 3.1.4 register address from the companion offset/header tables.
2. Use this chunk's `_SHIFT` and `_MASK` macros to pack a write value, extract a readback field, or build a read/modify/write mask.
3. Access the MMIO register through the AMD display register abstraction.
4. Let display hardware retain, consume, latch, clear, or report the represented state.

The state represented here is hardware state rather than driver-owned memory:

- Persistent configuration fields include perfmon event/routing controls, power-gate force/gate requests, DMU clock-gating override bits, DMCU memory power controls, DMCU firmware and RAM access setup, interrupt enable/routing masks, XIRQ/IRQ selection bits, host/uC mailbox command/data fields, and GPU timer read/start-position selectors.
- Volatile readback fields include perfmon active/state/counter readbacks, domain desired/power FSM state, DMU/DMCU/RBBMIF clock-on bits, ERAM/IRAM power state, DMCU running/sleeping/stalled status, internal exception bits, interrupt occurrence bits, DPRX/DPCS error/status bits, ABM interrupt counters, and GPU timer readback values.
- ACK, clear, reset, trigger, and command fields are side-effecting write paths. Examples include perfmon counter interrupt ACKs, DCPG interrupt clear bits, DMCU interrupt clear bits, DMCU event trigger bits, software reset/uc reset controls, ERAM/IRAM write/read access windows, mailbox command byte-valid bits, DPRX interrupt clears, and DMCU internal interrupt clears.
- Many interrupt status and clear fields intentionally share the same bit position/mask. A write used to clear an event is not equivalent to setting persistent configuration; call sites must avoid read/modify/write patterns that accidentally acknowledge pending status.
- The chunk includes both host-facing and uC-facing routing controls for the same event families. Misrouting an interrupt can remove host visibility, wake the wrong DMCU path, or select the wrong XIRQ/IRQ delivery mode even when the top-level `DISP_INTERRUPT_STATUS` source bit is correct.

Correct sequencing is imposed by hardware and functional driver code, not by these macros. Callers still need to respect display power state, DMCU/DMUB ownership, interrupt locking, firmware load/start ordering, RAM-access handshakes, power-gate transition polling, vblank/vupdate timing, and perfmon counter lifecycle rules.

## Dependencies And Integration Points

This chunk integrates with:

- The matching DCN 3.1.4 offset/address headers in the same `asic_reg/dcn` namespace. The mask/shift macros are meaningful only when paired with the correct register address for the same ASIC revision.
- AMDGPU Display Core register helper macros and generated register tables that consume `<register>__<field>__SHIFT` and `<register>__<field>_MASK` names for `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_GET_2`, and related accessors.
- DMUB/DMCU code paths that instantiate DCN 3.1.4 register tables. DCN 3.1.4 DMUB setup includes this generated mask header through register-list macros, so changed names or bit positions can break compile-time macro expansion or runtime firmware-register programming.
- Display interrupt handling and IRQ source mapping. The top-level `DISP_INTERRUPT_STATUS` fields correspond to interrupt source definitions under `include/ivsrcid/dcn`, while DMCU interrupt/routing registers decide whether events are exposed to the host, the uC, or both.
- Power-management code that drives DCPG domains, clock gating, memory power state, Z-state/SOC access, and deep sleep. The domain power-gate fields in this chunk are paired with status and interrupt bits used to confirm transitions.
- Firmware bring-up and diagnostics paths that reset/enable DMCU, configure firmware start/end/ISR addresses and checksums, access ERAM/IRAM windows, and poll DMCU status.
- Mailbox and command exchange paths using `MASTER_COMM_*` and `SLAVE_COMM_*` data/command/control registers for host-to-uC and uC-to-host signaling.
- ABM/static-screen/backlight paths using DMCU ABM histogram/luma/backlight update interrupts, interrupt counters, host/uC routing masks, and top-level `DISP_INTERRUPT_STATUS` ABM bits.
- Perfmon/debug tooling that programs DCCG/DMU perfmon instances, routes perfmon counter interrupts to DMCU/uC, reads low/high counter values, and clears counter interrupts.
- DisplayPort diagnostics and AUX/DPRX handling that observe and route the DPRX/DPCS interrupt fields for stream-status, DPHY errors, AUX/I2C/CPU events, and timeouts.
- Timing and IHC code that reads GPU timer values and tracks OTG/OPTC/HPD/AUX/I2C/DMCU events through `DISP_INTERRUPT_STATUS` and continuation status registers in later chunks.

Because this is generated preprocessor data, name mismatches usually fail at compile time only when a macro is referenced. Numeric drift in shifts or masks can compile cleanly and then misprogram live MMIO fields at runtime.

## Risks And Maintenance Notes

- Generated-header drift is the main risk. A stale or wrong `_SHIFT`/`_MASK` value can silently write the wrong hardware bit, especially for packed interrupt routing, counter state, mailbox command, and power-gate control registers.
- Chunk boundary risk exists at both ends. This slice starts in the middle of `DC_PERFMON0_PERFCOUNTER_CNTL` and ends in the middle of `DISP_INTERRUPT_STATUS`; final per-file reconciliation must merge neighboring chunks to avoid presenting those registers as incomplete.
- Status/clear aliasing is pervasive. Fields such as `*_OCCURRED` and `*_CLEAR`, or perfmon status and ACK bits, often share masks. Treating these as ordinary stored booleans can clear events before service or lose interrupt evidence.
- Host/uC interrupt routing has duplicated families across status, enable, and XIRQ/IRQ selector registers. Updating one register family without the corresponding enable/selector/status definition can leave events stuck, unhandled, or delivered to the wrong consumer.
- Power-gate and clock-gate fields are live hardware controls. Incorrect force/gate values or missing status polling can produce display hangs, failed DMCU access, broken ABM/static-screen handling, or timeouts during suspend/resume.
- DMCU RAM access fields are side-effecting indexed windows. Incorrect auto-increment, address, or write/read sequencing can corrupt firmware-visible memory or read the wrong diagnostic data.
- Perfmon counter readback is split across low/high/misc registers and selector fields. Callers must use the intended read-selection order to avoid mixing high/low halves or acknowledging counter interrupts unexpectedly.
- Interrupt source naming must remain aligned with `ivsrcid` tables and display IRQ code. For example, `DISP_INTERRUPT_STATUS` bits for HPD1, AUX1, DMCU, ABM, RBBMIF timeout, and OTG1 events are part of host-visible IRQ source mapping.

## Test Signals

Useful validation signals for changes touching this generated range include:

- Build coverage for DCN 3.1.4 display code that includes `dcn_3_1_4_sh_mask.h` and expands register/field macros in DMUB, interrupt, power, and perfmon tables.
- Compile-time failures for renamed or missing macros in generated register tables; these catch symbol drift but not wrong numeric masks.
- Suspend/resume and display power-management tests that exercise DCPG domain force/gate transitions, DMU/DMCU clock gating, ERAM/IRAM memory power state, and Z-state/SOC access controls.
- Firmware bring-up or DMUB/DMCU diagnostics that confirm DMCU reset/start/status behavior, firmware address/checksum programming, RAM window access, and host/uC mailbox command exchange.
- IRQ tests for HPD1/HPD1_RX, AUX1 SW/LS done, DC I2C SW done, OTG1 events, vblank/range-timing events, DMCU internal/SCP, ABM histogram/luma/backlight events, and RBBMIF timeout handling.
- Perfmon tests that configure `DC_PERFMON0/1/2`, start/stop counters, read low/high values, trigger counter-value interrupts, acknowledge them, and verify routing through `DMCU_PERFMON_INTERRUPT_*` fields.
- DP/DPRX diagnostic or error-injection tests that verify DPRX stream, DPHY, AUX/I2C/CPU, and timeout status/clear/routing bits.
- Register readback comparison against hardware documentation or known-good generated headers for DCN 3.1.4, especially for packed fields where bit offsets are non-contiguous or have continuation registers.

### subset-b-001838: lines 12037-14354

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 12037-14354

## Scope

This chunk is a generated DCN 3.1.4 register-field mask slice from `dcn_3_1_4_sh_mask.h`. It contains C preprocessor constants only: `_SHIFT` macros for bit positions, `_MASK` macros for raw 32-bit register masks, and comment markers naming registers and address blocks. There are no functions, structs, enums, branches, loops, or driver-owned state objects in this range.

The slice starts in the tail of `DISP_INTERRUPT_STATUS`, covers `DISP_INTERRUPT_STATUS_CONTINUE` through `DISP_INTERRUPT_STATUS_CONTINUE25`, defines a broad set of display interrupt destination registers, then covers DMCUB/RBBMIF security, timeout, memory-region, content-window, and interrupt-control field masks through the beginning of `DMCUB_INTERRUPT_STATUS`.

## Purpose And Hardware Surface

The purpose of this header range is to provide the bit layout ABI between AMDGPU Display Core/DMUB code and DCN 3.1.4 display hardware. Companion offset headers provide MMIO register addresses; this mask header supplies the field masks and shifts used by register helper macros to pack, update, or decode individual fields without hard-coded bit numbers.

Major hardware areas represented here:

- Display interrupt status continuation chain: `DISP_INTERRUPT_STATUS_CONTINUE*` fields expose latched interrupt status bits across display pipes, encoders, HPD/AUX, HUBP/HUBBUB, DPP, OPP, OPTC/OTG, DCCG, MMHUBBUB, WB/WBSCL, DCPG, DCIO/DPCS, AZ audio, DSC, HPO, ABM, DPIA, and DMCUB events.
- Interrupt destination controls: `*_INTERRUPT_DEST` registers route interrupt sources for DCCG, DMU/DMCUB/DMCU, DCPG, MMHUBBUB, WB, DCHUB, DPP, MPC, OPP, OPTC, OTG0-OTG5, DIG, I2C/DDC/HPD, DIO/DCIO, AZ audio, AUX, DSC, and HPO.
- DMCUB security and RBBM interface state: `DMCUB_RBBMIF_SEC_CNTL`, `RBBMIF_TIMEOUT`, `RBBMIF_STATUS`, `RBBMIF_STATUS_2`, `RBBMIF_INT_STATUS`, timeout-disable registers, and status flags define trust/source metadata, timeout timing, fault-client decode, timeout address/op/status readback, per-client timeout masking, and secure/nonsecure region status.
- DMCUB memory aperture programming: `DMCUB_REGION0/1/2/4/5/6/7_*` and `DMCUB_REGION3_CW0` through `CW7` base/top/offset registers describe lower and upper address bits, 29-bit base/top fields, enable bits, and offset alignment for DMCUB firmware/data windows.
- DMCUB interrupt control: `DMCUB_INTERRUPT_ENABLE`, `DMCUB_INTERRUPT_ACK`, and the beginning of `DMCUB_INTERRUPT_STATUS` define timer, inbox/outbox, GPINT, IH GPINT, undefined address fault, instruction fetch fault, and data write fault fields.

## Important Definitions

The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted bit mask within the 32-bit register.
- `//<REGISTER>` comments group definitions by MMIO register.
- `// addressBlock: ...` comments identify hardware address blocks for the following register groups.

Important field families in this chunk:

- `DISP_INTERRUPT_STATUS_CONTINUE` through `CONTINUE5` map pipe/connector events for OPTC data underflow, OTG snapshot/force-count/trigger/vsync/set-v-total-min events, DIGB-DIGF fast-training-complete and video-stream-disable events, HPD2-HPD6 and HPD RX, AUX2-AUX6 software/link-service done events, OTG vertical interrupts, and WBSCL overflow.
- `DISP_INTERRUPT_STATUS_CONTINUE6` through `CONTINUE12` add DPP performance counters, WB/WBSCL performance and overflow, DCCG latch/DRR/perfmon events, MPCC stall events, VGA CRT interrupt, MPC counters, and continuation bits that chain the interrupt-status register bank.
- `DISP_INTERRUPT_STATUS_CONTINUE13` through `CONTINUE18` map HUBBUB VM/timeout/compbuf and perfmon signals, DCPG domain0-domain7 power-up/down events, HUBP0-HUBP7 vblank/vline/vline2/timeout/flip/flip-away events, OPP/OPTC/MMHUBBUB perfmon events, DCIO DPCS TX/RX error events, and AZ perfmon events.
- `DISP_INTERRUPT_STATUS_CONTINUE19` through `CONTINUE25` cover AZ endpoint audio format/enabled/disabled interrupts, DIGG/DIGH fast-training/video-stream-disable events, DCPG domain16-domain21 power-up/down events, DSC0-DSC5 input-underflow/core-error/perfmon events, DMCUB high/low priority inbox/outbox/timer/general data/undefined address fault interrupts, ABM2-ABM5 ready/backlight-update events, DPIA, DMCUB whitelist invalid access, HPO perfmon, and MMHUBBUB warmup.
- Destination registers mirror many of the status families with `*_DEST` fields. These bits select where individual interrupt sources are delivered inside the interrupt handling fabric, so the same source families appear as routing controls rather than status readbacks.
- OTG destination fields repeat per timing generator instance (`OTG0_INTERRUPT_DEST` through `OTG5_INTERRUPT_DEST`) and include CPU subsecond, DRR timing, vupdate, snapshot, force-count, force-vsync-next-line, trigger A/B, GSL vsync gap, vertical0/1/2, vstartup, vready, vsync nominal, no-lock vupdate, and DRR vtotal reach events.
- DMCUB region fields use 64-bit address composition split across low/high offset registers. Offset low fields are shifted by 8 with mask `0xFFFFFF00`, offset-high fields use mask `0x0000FFFF`, and top/base fields use a 29-bit `0x1FFFFFFF` address mask plus a top-address enable bit at bit 31.
- `DMCUB_INTERRUPT_ENABLE`, `ACK`, and `STATUS` share the timer0/timer1, inbox0/1 ready/done, outbox0/1 ready/done, GPINT0-GPINT6, GPINT IH, and undefined-address-fault layout. `DMCUB_INTERRUPT_STATUS` also exposes instruction-fetch and data-write fault status bits in this chunk.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior occurs when Display Core, IRQ service, or DMUB service code combines these constants with register addresses from `dcn_3_1_4_offset.h` and register helper macros such as `REG_GET`, `REG_SET`, `REG_SET_2`, `REG_UPDATE`, `REG_WRITE`, and generated field-table initializers.

The state represented here is hardware register state:

- Status fields are volatile hardware observations. `DISP_INTERRUPT_STATUS_CONTINUE*`, `RBBMIF_STATUS*`, `RBBMIF_INT_STATUS`, `RBBMIF_STATUS_FLAG`, and `DMCUB_INTERRUPT_STATUS` fields reflect latched or live hardware events such as underflow, vblank/vline, HPD/AUX completion, DCPG power transitions, DPCS errors, DMCUB mailbox/timer/GPINT events, and DMCUB/RBBM faults.
- Destination fields are persistent routing configuration. `*_INTERRUPT_DEST` bits determine how display interrupt sources enter the interrupt handling path; a wrong destination bit can leave a real hardware event unhandled or routed to the wrong consumer.
- RBBMIF timeout controls are persistent diagnostic and fault-handling configuration. Timeout delay/hold fields, timeout-disable bitmaps, and timeout client/status flags influence whether bus/interface stalls are reported and how timeout state is decoded.
- DMCUB region and content-window registers persist memory aperture configuration used by the DMCUB firmware interface. The base/top/offset/high/enable fields define which physical or GPU-address windows the display microcontroller can access.
- DMCUB ACK fields are side-effecting write paths. Interrupt service code typically writes an ACK bit and then clears it back to zero, so generic read/modify/write handling must preserve the intended pulse semantics.
- Continuation bits at bit 31 in most `DISP_INTERRUPT_STATUS_CONTINUE*` registers indicate that another status register must be examined. Consumers that walk the interrupt status chain must not treat each register as an isolated final status word.

Ordering constraints are not encoded in these masks. Correct callers still need to coordinate with IRQ masking, display locks, DMCUB firmware state, power-domain sequencing, mailbox ownership, and MMIO read/write ordering.

## Dependencies And Integration Points

This chunk integrates with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`, which includes `dcn_3_1_4_offset.h` and this mask header to build `dmub_srv_dcn314_regs`.
- DMUB field lists such as `dmub_dcn31.h` and `dmub_dcn315.h`, which expand `DMUB_SF(register, field)` into generated mask and shift table entries. Fields from this chunk include DMCUB region top/enable fields and DMCUB interrupt enable/ACK fields.
- DC IRQ service tables such as `display/dc/irq/dcn314/irq_service_dcn314.c`, which reference DMCUB interrupt ACK fields for DMCUB outbox interrupt handling.
- OPTC/OTG resources and timing-generator code, including DCN 3.1/3.1.4 OPTC headers, which use `OTG*_INTERRUPT_DEST` fields to route vertical, vupdate, snapshot, DRR, and trigger interrupts.
- Display resource and hardware-sequencing code that lists and writes `RBBMIF_TIMEOUT_DIS` and `RBBMIF_TIMEOUT_DIS_2`, including timeout-disable setup in the DCE/DCN hardware sequence.
- DMUB service code for later DCN generations that shows the same programming pattern for `DMCUB_REGION3_CW*` windows: write low/high offsets, write base address, then set top address and enable fields with `REG_SET_2`.
- IV source ID headers under `include/ivsrcid/dcn/`, which map named interrupt sources such as HPD, AUX, DIG fast training, and video stream disable to corresponding `DISP_INTERRUPT_STATUS_CONTINUE*` fields.
- Display diagnostics, perfmon, and debug paths that depend on perf counter interrupts, RBBM timeout readbacks, DSC error/underflow signals, DPCS errors, HUBP timeout/flip/vblank/vline events, and DMCUB fault bits.

Because this file is generated, many dependencies are indirect through macros. A macro name mismatch tends to fail at compile time where the field is referenced, but a numeric mask/shift drift can compile cleanly and misprogram MMIO at runtime.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.1.4 register specification is the primary risk. Incorrect masks or shifts can misroute interrupts, miss latched faults, program DMCUB memory windows incorrectly, or acknowledge the wrong DMCUB event.
- The continuation status chain is easy to truncate. Missing a `DISP_INTERRUPT_STATUS_CONTINUE*_MASK` bit can hide later-register events such as DMCUB mailbox interrupts, DSC faults, ABM events, or MMHUBBUB warmup.
- Destination fields are configuration, not status. Treating `*_INTERRUPT_DEST` bits like harmless readback fields can change interrupt delivery behavior and break HPD, AUX, vblank/vline, DMUB, DSC, audio, or power-domain event handling.
- The register names are highly repetitive across instances. Prefix mistakes such as `OTG4` versus `OTG5`, `AUX5` versus `AUX6`, `DIGG` versus `DIGH`, or `DCPG_INTERRUPT_DEST` versus `DCPG_INTERRUPT_DEST2` can target a different hardware block while still compiling if the mistaken macro exists.
- DMCUB memory region fields are address-sensitive. Base/top fields expose only 29 bits, low offsets are 256-byte aligned, and high offsets are split into separate registers; callers must validate ranges and preserve alignment before packing values.
- DMCUB ACK bits are side-effecting. Read/modify/write helpers that leave an ACK bit set or clear unrelated bits can lose interrupts or generate repeated acknowledgements.
- RBBMIF timeout and security fields affect fault visibility and access permissions. Disabling timeout sources or programming trust/source fields incorrectly can hide real bus faults or create invalid DMCUB access behavior.
- Some event names reflect hardware spelling, including `OCCURED` and `INTERRPUT`; generated names must be preserved exactly because driver code depends on the macro spelling.
- This chunk starts and ends mid-file. It begins after the initial `DISP_INTERRUPT_STATUS` shift definitions and ends before the rest of `DMCUB_INTERRUPT_STATUS` and following DMCUB registers; the merge lane must combine adjacent chunks for a complete per-file report.

## Test Signals

Useful validation signals for this chunk are compile-time, generated-header consistency, and display/DMUB hardware behavior:

- Build AMDGPU with DCN 3.1.4 support and ensure all generated field names used by DMUB, IRQ, OPTC, resource, and hardware-sequencing code resolve.
- Run generated-header consistency checks that every field has the expected `_SHIFT`/`_MASK` pair, masks fit in 32 bits, continuation bits occupy bit 31 where expected, and fields do not overlap unexpectedly within each register.
- Exercise HPD and HPD RX events across HPD1-HPD6, and verify the expected `DISP_INTERRUPT_STATUS_CONTINUE*` bits and `HPD_INTERRUPT_DEST` routing behavior.
- Exercise AUX and I2C/DDC transactions, including software done, link-service done, hardware done, DDC read-request, and AUX GTC sync lock/error paths.
- Run vblank/vline/vline2, flip, flip-away, vupdate, vertical0/1/2, snapshot, DRR timing, and force-count/force-vsync timing tests across active OTG/HUBP instances.
- Exercise DisplayPort link events that map to DIG fast-training-complete and video-stream-disable interrupts for DIGB through DIGH.
- Validate DCPG power-up/down interrupts for domain0-domain7 and domain16-domain21 during display power sequencing, suspend/resume, and power-gating transitions.
- Run DSC-enabled modes and check DSC input-underflow/core-error/perfmon interrupts for DSC0-DSC5.
- Verify DMCUB mailbox and GPINT flows, including DMCUB high/low priority inbox/outbox ready/done, timer, general data in/out, GPINT, GPINT IH, undefined address fault, whitelist invalid access, instruction fetch fault, and data write fault reporting/ACK behavior.
- Exercise DMUB region programming during firmware boot and reinitialization, confirming base/top/offset/high/enable programming produces valid windows and that readbacks match expected alignment and ranges.
- Trigger or simulate RBBMIF timeout diagnostics where available, checking timeout delay/hold configuration, timeout-disable registers, decoded client status, timeout address/op/read-write status, and secure/nonsecure status flags.
- Run audio enable/disable/format-change tests for AZ endpoints 0-7 and verify status and destination bits correspond to the expected endpoint.

## Chunk-Specific Summary

Lines 12037-14354 define a dense DCN 3.1.4 register-field surface for interrupt status, interrupt routing, RBBMIF/DMCUB fault state, DMCUB memory apertures, and DMCUB interrupt enable/ACK/status control. Correctness depends on exact generated masks and shifts, preserving hardware spelling and instance prefixes, walking the `DISP_INTERRUPT_STATUS_CONTINUE*` chain fully, programming DMCUB region fields with correct alignment/range, and handling side-effecting ACK and timeout/security fields with the required MMIO sequencing.

### subset-b-001839: lines 14355-17019

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 14355-17019

## Purpose

This chunk is generated AMD DCN 3.1.4 register field metadata. It contains no executable C logic; it publishes preprocessor constants for field bit positions and masks inside DCN display-engine MMIO registers. The companion offset header gives register addresses, while this header gives the field layout used by register-helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

Although the path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata and has no Ceph or distributed filesystem behavior.

The requested range covers the tail of the DMCUB interrupt-status block, the rest of the DMCUB service interface fields, MCIF writeback and MMHUBBUB fields, HDA/Azalia stream/controller/root/input endpoint fields, DCHUBBUB SDPIF/return-path/arbitration/diagnostic fields, `DC_PERFMON3` through `DC_PERFMON5` field sets, and the start of DCN VM context page-table fields. This slice has 2,072 `#define` lines: 1,026 `__SHIFT` definitions and 1,046 `_MASK` definitions across 459 register-name groups. The count imbalance is caused by chunk boundaries: it starts with `DMCUB_INTERRUPT_STATUS` masks whose shifts are in the previous chunk, and it ends inside `DCN_VM_CONTEXT10_CNTL` before the final block-size mask.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, locks, allocations, or direct persistence APIs in this line range. Its public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: field bit offset.
- `<REGISTER>__<FIELD>_MASK`: field bit mask.

Important register families in this chunk:

- DMCUB interrupt and control fields: `DMCUB_INTERRUPT_STATUS`, `DMCUB_INTERRUPT_TYPE`, external interrupt status/context/ack, fault-address registers, `DMCUB_SEC_CNTL`, memory QoS control, inbox/outbox base/size/read/write pointers, timers, scratch registers 0 through 15, GPINT input/output registers, low-speed wake interrupt enable, DMCUB memory power control, processor ID, and `DMCUB_CNTL2`.
- MCIF writeback buffer manager fields for writeback instance 0: software control, status, pitch, four buffer status/status2 blocks, arbitration, SCLK change, debug index/data, Y/C addresses and high address halves, VCE control, NB p-state/watermark controls, clock/self-refresh controls, QoS, luma/chroma sizes, per-buffer resolution, VMID, and minimum time-to-output.
- MMHUBBUB fields: p-state/watermark/warmup registers, warmup base and region, writeback/SMU watermark-change handshake, WBIF0 write-combine and outstanding counters, VGA split, memory power status/control, clock gating, soft reset, DMU interface error status, client unit IDs, and warmup VMID control.
- VGAIF MCIF fields for latency counters, write-combine timeout, and outstanding request counters.
- Perfmon instances `DC_PERFMON3`, `DC_PERFMON4`, and `DC_PERFMON5`: event selection, counted value selection, increment/run/interrupt controls, per-counter states, repeat count, count-off interrupt controls, counter interrupt status/ack, and high/low counter readback.
- HDA/Azalia fields: stream index/data windows for streams 0 through 15, clock gating, codec endpoint index/data windows, controller DTO/SOCCLK/DMA/RIRB/CORB/cyclic-buffer/global-capability/arbitration fields, CRC controls/results, memory power controls/status, root codec vendor/revision/capability/power/reset/subsystem/synchronization fields, audio port connectivity, GTC group offsets, and input endpoint index/data windows 0 through 7.
- DCHUBBUB SDPIF and VM aperture fields: SDPIF credit/status/error/snoop controls, VM physical-request selection, force-IO status and address reporting, framebuffer base/top/offset, AGP aperture, local HBM start/end/lock, and SDPIF memory power state.
- DCHUBBUB return-path and hub fields: return-path memory power, CRC controls and values, DCC statistic controls/counters, compression-buffer and DET controls, memory power mode/status, reserved compression-buffer space, debug controls, outstanding request limits, saturation/QoS forcing, DRAM-state controls, A/B/C/D watermark sets for urgency, self-refresh, Z8 self-refresh, DRAM clock change, and fractional urgent bandwidth.
- DCHUBBUB runtime/diagnostic fields: host-VM controls, watermark-change request/status, timeout enable, global timer, surface check addresses, VTG0 through VTG3 controls, soft reset, clock controls, DCFCLK gating delay, latency/ROB measurement controls, vline snapshot, overflow status/clear, timeout detection and interrupt status, FMON controls, and debug index/data.
- DCN VM context fields: `DCN_VM_CONTEXT0` through `DCN_VM_CONTEXT9` complete control/base/start/end page-table fields, plus the start of `DCN_VM_CONTEXT10_CNTL`.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display and DMUB code that includes the generated DCN 3.1.4 offset and mask headers.

Typical flow:

1. DCN314 resource, IRQ, and DMUB code include `dcn_3_1_4_offset.h` and `dcn_3_1_4_sh_mask.h`.
2. Resource and IRQ code builds block-specific register tables using `SR`, `SRI`, `SRII`, field-list, and token-paste helper macros.
3. DMUB code builds `struct dmub_srv_dcn31_regs` for DCN314 by expanding `DMUB_DCN31_REGS()` and `DMUB_DCN31_FIELDS()` through `FD_MASK` and `FD_SHIFT`.
4. Runtime paths use those generated offsets/shifts/masks to program DMCUB reset/release, firmware windows, inbox/outbox rings, GPINT, scratch/status registers, interrupt status/ack, writeback memory, audio stream windows, hub watermarks, power/clock gating, VM context address ranges, and performance counters.

The masks do not encode ordering or access side effects. Consumers must still follow the hardware programming sequences around reset assertion/release, power gating, clock enabling, watermark updates, mailbox pointer ordering, write-one-to-clear status bits, indexed register windows, DMA enablement, VM table programming, and suspend/resume restore.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on disk. It describes fields for MMIO-backed GPU state. State represented by these definitions includes:

- DMCUB firmware service state: interrupt status/type/ack, fault addresses, security reset/fault clear, memory QoS, inbox/outbox ring base/size/read/write pointers, timers, scratch registers, GPINT payloads, wake interrupts, memory power, processor ID, soft reset, and boot/control bits.
- Writeback and MMHUBBUB state: buffer manager ownership/status, buffer addresses and resolutions, arbitration, p-state/watermark coordination, self-refresh, QoS, VMID selection, outstanding request counters, memory power state, clock gating, and soft reset.
- HDA/Azalia state: indexed stream and endpoint register accesses, controller DMA/ring/cyclic-buffer controls, DTO/SOCCLK controls, CRC setup/results, global capabilities, stream arbitration, codec root parameters, audio power state, reset, connectivity overrides, GTC offsets, and audio memory power.
- DCHUBBUB memory fabric state: SDPIF port/credit/error status, VM aperture and AGP/HBM address windows, CRC/DCC statistics, compression buffers, DET allocations, hub memory power state, arbitration watermarks for sets A through D, host-VM policy, timer/surface-check diagnostics, timeout detection, and latency/ROB measurement state.
- DCN VM context state: page-table depth and block size, page-directory base address, logical page start/end ranges, and framebuffer/AGP aperture translation inputs.

Persistence is hardware-defined. Some fields are configuration bits that remain until modeset, reset, power gating, suspend/resume, or ASIC reset. Other fields are read-only status, sticky error, write-one-to-clear, self-clearing request, or indexed-window data fields. This generated header does not express those access classes; driver code and hardware documentation must supply that context.

## Dependencies And Integration Points

This chunk must match the generated DCN 3.1.4 register database and the companion offset file:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h`

Direct include sites found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`

Key integration points:

- `dmub_dcn314.c` expands `DMUB_DCN31_FIELDS()` into DCN314 mask and shift tables. Fields from this chunk directly back DMUB control paths such as `DMCUB_CNTL`, `DMCUB_CNTL2`, `DMCUB_SEC_CNTL`, inbox/outbox pointers, interrupt enable/ack, scratch registers, `MMHUBBUB_SOFT_RESET`, `DCN_VM_FB_LOCATION_BASE`, and `DCN_VM_FB_OFFSET`.
- `dmub_srv.c` selects `dmub_srv_dcn314_regs` for `DMUB_ASIC_DCN314`, then shares common `dmub_dcn31_*` operations for reset, window setup, mailbox setup, GPINT, boot options, diagnostic data, and timer reads.
- `irq_service_dcn314.c` uses the same generated field namespace for interrupt-source status, acknowledgement, and routing tables, including display, hub, audio, hotplug, AUX/DDC, and perfmon events.
- `dcn314_resource.c` includes this header while constructing DCN314 display resources, register blocks, IRQ service, DIO/stream encoders, DSC instances, timing generators, hardware sequencer, and resource capability tables.
- Clock manager, DML, and HWSS DCN314 code do not necessarily include this header directly, but they depend on the register tables and hardware behavior configured through it when programming watermarks, clock/power state, VM apertures, and hub arbitration.

## Risks And Edge Cases

- Generated macro drift is the main risk. A wrong constant compiles cleanly but can program the wrong bit, corrupt adjacent fields, or misread status.
- This range has two artificial boundary splits. The `DMCUB_INTERRUPT_STATUS` shift definitions are in the prior chunk, while `DCN_VM_CONTEXT10_CNTL__VM_CONTEXT10_PAGE_TABLE_BLOCK_SIZE_MASK` is in the next line/chunk. File-level reconciliation must merge adjacent chunks before making complete claims about those registers.
- DMCUB fields are high impact. Incorrect reset, security, mailbox pointer, interrupt, GPINT, scratch, timer, or fault-address masks can prevent firmware boot, lose command ring traffic, create stuck interrupts, or hide useful fault diagnostics.
- Indexed HDA/Azalia stream and endpoint windows are sequencing-sensitive. Incorrect index/write-enable/data fields can target the wrong stream or codec node and break HDMI/DP audio setup, ring/DMA operation, or codec power-state reporting.
- MCIF writeback and MMHUBBUB fields influence memory traffic and power management. Bad buffer address, VMID, pitch, outstanding-counter, watermark, self-refresh, or clock-gating fields can cause writeback corruption, display underflow, failed p-state changes, or resume problems.
- DCHUBBUB watermark and arbitration fields govern display memory-service latency. Incorrect A/B/C/D watermark, urgent-bandwidth, host-VM, timeout, or surface-check fields can lead to underflow, excessive power use, false timeout interrupts, or hard-to-diagnose stalls.
- VM aperture and context fields must agree with GPU memory manager state. Bad page-table base/start/end, FB/AGP/HBM aperture, or lock fields can translate display requests to the wrong physical memory.
- Perfmon fields are diagnostic but side-effectful. Wrong event selects, run-enable controls, or ack masks can make performance data misleading or leave counter interrupts stuck.
- Memory power and soft-reset fields affect live hardware blocks. Applying these masks outside the expected disable/reset sequence can power down active audio, writeback, hub, or DMCUB state.

## Test Signals

Useful validation combines build checks, generated-header consistency checks, and hardware behavior:

- Build AMDGPU/DC with DCN314 enabled. Missing or renamed macros should fail in `dmub_dcn314.c`, `irq_service_dcn314.c`, and `dcn314_resource.c`.
- Mechanically verify that complete fields in this range have paired `__SHIFT` and `_MASK` definitions, while allowing the known boundary exceptions for `DMCUB_INTERRUPT_STATUS` and `DCN_VM_CONTEXT10_CNTL`.
- Compare the field values against AMD's authoritative DCN 3.1.4 register database and adjacent generated DCN 3.1.x headers where fields are expected to remain compatible.
- Exercise DMUB/DCN314 boot: reset/release, secure reset status, firmware window setup, inbox/outbox ring pointer traffic, GPINT acknowledgement/response, scratch/status readback, timer readback, and fault-address reporting.
- Exercise IRQ behavior: vblank/vline, hotplug/HPD RX, AUX/DDC, audio, DMCUB GPINT IH, DCHUBBUB timeout, watermark-change done, and perfmon interrupts. Watch for missing, stuck, or misrouted events.
- Exercise writeback and hub memory paths: MCIF writeback buffers, pitch/resolution/address programming, VMID selection, p-state/watermark changes, self-refresh, outstanding-counter readback, and memory power transitions.
- Exercise HDMI/DP audio: stream index/data programming, controller DMA/RIRB/CORB/cyclic-buffer paths, DTO/SOCCLK controls, codec power/reset, endpoint register access, and CRC diagnostics.
- Exercise DCHUBBUB watermarks and VM paths under bandwidth stress, p-state changes, host-VM traffic, AGP/FB aperture changes, timeout detection, surface-check diagnostics, and suspend/resume.
- Exercise perfmon instances 3 through 5 by selecting events, enabling counters, reading high/low values, causing/clearing counter interrupts, and verifying stable state transitions.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DMCUB_INTERRUPT_STATUS`, including the shift definitions for the status masks present at this range's start. The next chunk owns the remainder of `DCN_VM_CONTEXT10_CNTL` and later VM context fields. The final per-file research document should merge adjacent chunks before drawing full-file conclusions about DMCUB interrupt status or the complete set of DCN VM contexts.

### subset-b-001840: lines 17020-19538

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 17020-19538

## Scope

This chunk is part of AMDGPU Display Core Next 3.1.4 ASIC register metadata. It contains C preprocessor constants for register field shifts and masks, not executable code. The covered range starts in the global DCN VM register area and then defines display hub pipe register fields for HUBP/HUBPREQ/HUBPRET/CURSOR/perfmon instances 0 and 1, plus HUBP2 and the first portion of HUBPREQ2.

The file is paired with `dcn_3_1_4_offset.h`: offset macros identify where a register is in MMIO space, while this header gives `REG__FIELD__SHIFT` and `REG__FIELD_MASK` values used to pack and unpack individual bitfields.

## Purpose

The purpose of this chunk is to describe hardware-visible state for the DCN 3.1.4 display memory-fetch path:

- DCN VM contexts 10-15, default VM address registers, and VM fault control/status/address fields.
- HUBP surface configuration fields for pipes 0, 1, and 2, including pixel format, rotation, mirroring, tiling, viewport coordinates, request sizes, blanking behavior, clock enable/gating, virtual memory page configuration, and debug/measurement controls.
- HUBPREQ surface request fields for pipes 0, 1, and the start of 2, including surface pitch, VMID, primary/secondary luma and chroma addresses, metadata addresses, TMZ/DCC controls, flip control, flip interrupts, in-use address latches, TTU/QoS controls, VM aperture/TLB fields, destination/vblank/nominal/flip timing parameters, prefetch configuration, cursor timing settings, and request-memory power state.
- HUBPRET return-path controls for pipes 0 and 1, including detile buffer control, blank-enable flow control, detile buffer power gating, read-line controls/status, and HUBPRET interrupt status/mask/clear fields.
- Cursor 0 fields for pipes 0 and 1, including enable/mode/pitch, address, size, position, hotspot, stereo control, destination offset, memory power state, DMDATA address/control/QoS/status/software data fields.
- DC perfmon blocks 6 and 7, with event selection, counter state, active windows, manual trigger, interrupt, mode, and counter value fields.

## Important APIs, Types, and Macros

There are no functions or C types in this chunk. The exported interface is macro names consumed by DC register-helper macros:

- `*_SHIFT` constants give the field low-bit position.
- `*_MASK` constants give the field bit mask.
- Register/field naming follows `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`, for example `HUBPREQ0_DCSURF_FLIP_CONTROL__SURFACE_FLIP_PENDING_MASK`.

Integration code commonly expands these through helper macros such as `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `HUBP_SF(...)`, `REG_SET`, `REG_UPDATE`, and related MMIO accessors. In this source tree, `dmub/src/dmub_dcn314.c` includes this header and uses `DMUB_DCN31_FIELDS()` with `FD_MASK`/`FD_SHIFT` to initialize the DMUB register field tables. `dc/irq/dcn314/irq_service_dcn314.c` also includes it alongside the matching offset header for DCN 3.1.4 IRQ register metadata. Generic HUBP resource code follows the same pattern: register lists are built with `SRI(...)`, and field mask/shift structures are built with `HUBP_MASK_SH_LIST_DCN31(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN31(_MASK)`.

## Register Groups Covered

The VM portion completes higher-numbered display VM contexts:

- `DCN_VM_CONTEXT10_*` through `DCN_VM_CONTEXT15_*` define page-table depth, block size, page-directory base address, and logical page start/end fields.
- `DCN_VM_DEFAULT_ADDR_MSB/LSB` defines default address and SPA/snoop bits.
- `DCN_VM_FAULT_CNTL` defines status-clear, status mode, interrupt enable, range-fault disable, and PRQ-fault disable bits.
- `DCN_VM_FAULT_STATUS` exposes fault status, error VMID, translation-response error VMID, table level, pipe, and interrupt status.
- `DCN_VM_FAULT_ADDR_MSB/LSB` captures the faulting address.

Each HUBP instance defines static surface interpretation:

- `DCSURF_SURFACE_CONFIG`: pixel format, rotation, horizontal mirroring, alpha plane enable.
- `DCSURF_ADDR_CONFIG` and `DCSURF_TILING_CONFIG`: pipe/interleave/compressed-fragment/packer fields plus swizzle mode, dimensionality, metadata linearity, and pipe alignment.
- Primary/secondary viewport start/dimension pairs, including chroma `_C` variants.
- `DCHUBP_REQ_SIZE_CONFIG` and `_C`: chunk dimensions, minimum chunk size, meta chunk dimensions, DPTE group sizing.
- `DCHUBP_CNTL`: hubp enable, blank enable, detile-buffer flush, underflow and mem-power status flags, stall controls, data return flags, clock-gate disable, and request-limit controls.
- `HUBP_CLK_CNTL`: clock enable/force bits and DCFCLK/DPPCLK force-on flags.
- `DCHUBP_VMPG_CONFIG`, debug registers, and DCFCLK/DPPCLK measurement-window controls.

Each HUBPREQ instance defines the dynamic fetch programming surface:

- Pitch and VMID settings.
- Primary/secondary surface address and high-address registers for luma and chroma planes.
- Primary/secondary metadata surface address and high-address registers for luma and chroma metadata.
- `DCSURF_SURFACE_CONTROL`: trusted memory zone bits, DCC enable bits, DCC independent-block fields, and equivalent chroma/metadata security bits.
- `DCSURF_FLIP_CONTROL`, `DCSURF_FLIP_CONTROL2`, and `DCSURF_SURFACE_FLIP_INTERRUPT`: update locks, flip type, pending/away status, stereo sync, pending delay/min-time, GSL, triple-buffering, interrupt masks/status, and write-one-clear style clear bits.
- Surface in-use and earliest-in-use address latches, with high address and VMID fields for luma/chroma.
- TTU/QoS controls (`DCN_TTU_QOS_WM`, `DCN_GLOBAL_TTU_CNTL`, surface/cursor TTU controls), VM DMDATA status/clear bits, VM aperture low/high address fields, and L1 TLB enable/system-access/VMID fields.
- Timing/prefetch registers: blank offsets, destination dimensions, after-scaler dimensions, vblank parameters, flip parameters, nominal parameters, per-line delivery, cursor settings, ref-frequency-to-pixel-frequency ratio, and destination Y delta request limit.
- Memory power control/status bits for light sleep, shutdown, force, and disallow status.

HUBPRET and cursor/perfmon blocks cover complementary status and instrumentation state:

- `HUBPRET*_HUBPRET_CONTROL` configures detile-buffer size, crossbar source selection, blank-enable acknowledgement, and global clocks.
- `HUBPRET*_HUBPRET_MEM_PWR_*` mirrors request-side memory power controls for detile buffers.
- `HUBPRET*_HUBPRET_READ_LINE_*` and `*_INTERRUPT` define read-line compare/control, occurrence/status/mask/clear fields, and read-line/current-vblank/flip status.
- `CURSOR0_*` registers define cursor fetch address, geometry, blending mode, stereo behavior, destination offset, memory power state, and DMDATA sideband fetch/control/status/software-write fields.
- `DC_PERFMON6_*` and `DC_PERFMON7_*` define counter event selection, increment/run modes, trigger mode, window state, region/window selection, manual triggers, interrupt control/status/clear, and 64-bit counter values split across low/high registers.

## Control Flow and State Behavior

This header has no runtime control flow. Runtime behavior is induced by display driver code that writes or reads registers using these field constants:

1. Resource initialization builds per-block register address tables from offset macros and builds shift/mask tables from this header.
2. Atomic display programming writes HUBP/HUBPREQ fields to describe framebuffer format, tiling, addresses, metadata, viewport, VMID, QoS, cursor state, and prefetch/deadline timing.
3. Page flips update surface address and flip-control fields, then hardware reports pending/occurred/in-use state through `DCSURF_FLIP_CONTROL`, `DCSURF_SURFACE_FLIP_INTERRUPT`, and in-use address registers.
4. VM faults and DMDATA faults persist in status registers until cleared through explicit clear fields.
5. Underflow, memory-power, read-line, and perfmon fields expose hardware status for diagnostics, interrupt handling, and performance measurement.

The persistence is hardware state, not kernel memory persistence. Register writes remain in the display engine until reset, power gating, mode reprogramming, or later MMIO writes alter them. Several fields are status/clear pairs, so a stale or missed clear can cause repeated interrupt/status observations.

## Dependencies and Integration Points

This chunk depends on exact DCN 3.1.4 hardware register layout. The most direct dependencies are:

- Matching register offsets from `drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`.
- AMD display register access macros that combine offset, shift, and mask metadata.
- HUBP resource and implementation code under `drivers/gpu/drm/amd/display/dc/hubp/` and `drivers/gpu/drm/amd/display/dc/resource/`, which expect field names such as `DCSURF_SURFACE_PITCH`, `DCSURF_FLIP_CONTROL`, `CURSOR_CONTROL`, and `DCN_TTU_QOS_WM` to exist for each pipe instance.
- DMUB support in `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`, which includes this header to populate field arrays used by the display microcontroller service layer.
- DCN 3.1.4 IRQ service code, especially page-flip and vblank/vupdate IRQ source mapping; flip interrupt state is represented by the HUBPREQ surface flip interrupt fields in this chunk.

The instance naming is important. The chunk covers concrete prefixes (`HUBP0`, `HUBPREQ0`, `HUBPRET0`, `CURSOR0_0`, `DC_PERFMON6`, then corresponding instance 1 and partial instance 2). Generic code relies on macro expansion to map logical pipe IDs to these concrete register names.

## Risks and Edge Cases

- Bitfield drift is the main risk. These generated constants must match the ASIC specification exactly; an incorrect mask or shift silently writes the wrong hardware bits.
- Instance skew is risky because fields are repeated with only prefixes changed. A typo in one instance can affect only a subset of pipes, producing display failures that depend on pipe allocation.
- Split 64-bit addresses require coordinated low/high writes and correct high-bit masks. Surface, metadata, cursor, fault, in-use, and VM page-table addresses can become invalid if high fields are truncated or paired with stale low fields.
- Security and memory-protection bits are sensitive. TMZ, VMID, VM aperture, TLB, default address, and fault-control fields affect how display fetches memory and how faults are reported or suppressed.
- Flip status fields mix control, pending, interrupt status, and clear semantics. Incorrect clear/mask usage can lose page-flip completion events or leave page flips appearing stuck.
- QoS/TTU/prefetch timing fields are performance and correctness critical. Bad values can lead to underflow, visible corruption, missed vblank deadlines, or unnecessary memory-clock pressure.
- Memory power control fields can affect wake latency and data availability if light-sleep/shutdown force or disallow bits are programmed inconsistently with active fetches.
- Perfmon fields are observational but can still perturb diagnostics if counter selection, active windows, or clear/restart bits are wrong.

## Test Signals

Useful signals for changes touching these masks are mostly integration and hardware behavior checks:

- Build coverage for AMDGPU display code with DCN 3.1.4 enabled; missing or renamed macros should fail compilation where register tables expand.
- Boot and modeset on matching hardware/APU, with multiple active pipes to exercise instance 0, 1, and 2 register names.
- Page-flip stress tests checking that page-flip IRQs arrive, pending bits clear, and no stuck `SURFACE_FLIP_PENDING` state remains.
- Cursor tests across formats, sizes, stereo/rotation/mirroring cases, and cursor movement while page flips are active.
- VM fault injection or fault telemetry checks verifying that `DCN_VM_FAULT_STATUS`, fault address, VMID, and clear behavior report expected values.
- Display underflow and DCC/TMZ test coverage for compressed/protected framebuffers.
- Power-management tests that enter/exit display memory power states while scanout, cursor, and DMDATA fetches remain correct.
- Perfmon smoke tests validating event selection, counter start/stop, interrupt/status, and high/low counter reads for perfmon blocks 6 and 7.

### subset-b-001841: lines 19539-22071

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 19539-22071

## Purpose

This chunk is generated AMD DCN 3.1.4 register field metadata. It contains no executable C logic; it publishes `#define` constants for register-field bit shifts and bit masks in `dcn_3_1_4_sh_mask.h`. Consumers use the constants with the matching DCN 3.1.4 offset header to build typed register tables for AMDGPU display hardware.

The range starts inside the `HUBPREQ2_DCN_DMDATA_VM_CNTL` field set, then covers the rest of HUBP/HUBPREQ/HUBPRET/cursor/perfmon metadata for pipe instance 2, full HUBP/HUBPREQ/HUBPRET/cursor/perfmon metadata for pipe instance 3, and the beginning of DPP0 color-pipeline metadata through `CM0_CM_GAMCOR_RAMB_REGION_24_25`. It is a chunk of one large generated header, so the first and last register groups are partial.

Although the source tree path is under a local `ceph-client` mirror, this file is AMDGPU display-driver hardware metadata and is unrelated to Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this range. The public interface is the macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT`: the field lsb position within a hardware register.
- `<REGISTER>__<FIELD>_MASK`: the register bit mask for that field.
- `// addressBlock: ...` comments: generated register-database block boundaries, useful for mapping repeated display-pipe instances.

Major macro families in this chunk:

- `HUBPREQ2_*`: tail of pipe-2 HUBP request metadata. It includes display metadata VM status/clear/done fields, system aperture limits, L1 TLB control, blanking and destination timing fields, prefetch ratios, vblank/flip/nominal PTE and metadata request timing, per-line delivery, cursor request offsets, reference-to-pixel frequency conversion, DRQ limit, request-cache memory power control/status, and additional VM/PTE/meta timing fields for flip and vblank.
- `HUBPRET2_*`: pipe-2 return-side HUBP metadata. Fields describe DET buffer plane base, 3-to-2 packing disable, component crossbar routing, DMROB/PIXCDC memory power control and status, read-line control and status, and HUBPRET interrupt status/clear/mask behavior.
- `CURSOR0_2_*`: pipe-2 cursor and display metadata registers. Fields cover cursor enable/mode, request mode, magnification, pitch, chunking, address high/low, size, position, hot spot, stereo enable/mode, destination offset, cursor memory power, DMDATA address/control/QoS/status, and software DMDATA write path.
- `DC_PERFMON8_*`: pipe-2 HUBP perfmon counter control/state/value fields, including counter enable, clear, freeze, field-selection muxes, counter mode, elapsed counter, histogram mode, and low/high counter values.
- `HUBP3_*` and `HUBPREQ3_*`: full pipe-3 HUBP and request metadata for surface config, tiling, viewport, request sizing, blank/underflow/soft reset/status controls, VM page configuration, debug windows, surface pitch, VMID, primary/secondary surface and metadata addresses, DCC/TMZ surface control, flip control and interrupts, in-use/earliest-in-use addresses, expansion mode, QoS/TTU controls, DMDATA VM control, system aperture, L1 TLB, timing/prefetch/vblank/flip/nominal delivery fields, cursor request settings, and memory power control/status.
- `HUBPRET3_*`, `CURSOR0_3_*`, and `DC_PERFMON9_*`: pipe-3 equivalents of the pipe-2 return, cursor, DMDATA, and perfmon fields.
- `DPP_TOP0_*`, `CNVC_CFG0_*`, `CNVC_CUR0_*`, and `DSCL0_*`: start of DPP0 display-pipe processor metadata for DPP clock/reset/CRC/host-read control, pixel format conversion, FP bias/scale, color keying, alpha LUT, pre-dealpha/pre-CSC/pre-degamma/pre-realpha, cursor colors/scale bias, scaler coefficient RAM, scaler mode/tap/init/ratio controls, black color, update/autocal, overscan, recout/MPC size, line-buffer format/memory, DSCL memory power, and output buffer controls.
- `CM0_CM_*`: DPP0 color-management metadata. This chunk includes CM bypass/current-state controls, post-CSC and gamut-remap matrices, bias, gamcor LUT control/data/index, and large RAMA/RAMB piecewise-linear gamma-correction region tables up to `CM0_CM_GAMCOR_RAMB_REGION_24_25`.

## Control Flow

This header has no runtime control flow. Runtime code supplies the sequencing:

1. DCN 3.1.4 resource and IRQ code includes this header with `dcn_3_1_4_offset.h`.
2. Resource constructors in `display/dc/resource/dcn314/dcn314_resource.c` build register address tables from the offset header and build shift/mask tables from this header.
3. For HUBP, `hubp_shift` and `hubp_mask` are initialized with `HUBP_MASK_SH_LIST_DCN31(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN31(_MASK)`. Those macro lists paste register and field names, so fields from `HUBPREQ2_*`, `HUBP3_*`, `HUBPREQ3_*`, `HUBPRET3_*`, and `CURSOR0_3_*` must match the expected instance-0 field names after token substitution.
4. For DPP, `tf_shift` and `tf_mask` are initialized with `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)`, which ultimately depend on `TF_SF`/`TF2_SF` field macro expansion against `DPP_TOP0_*`, `CNVC_CFG0_*`, `DSCL0_*`, and `CM0_CM_*`.
5. Constructed objects such as `dcn20_hubp` and `dcn3_dpp` receive pointers to these tables. Runtime paths then use register helpers like `REG_UPDATE`, `REG_GET`, `REG_SET`, `REG_READ`, and `REG_WRITE` to program fields indirectly by symbolic field names.

The chunk itself does not encode modeset ordering. Correct sequencing is owned by HUBP, DPP, DML, resource, IRQ, and HW sequencing code that programs clocks, power gates, surface addresses, VM/TLB setup, prefetch timing, cursor/DMDATA updates, scaling, color transforms, LUTs, and interrupt/status handling.

## State And Persistence Behavior

This chunk stores no software state and persists nothing. It describes fields in MMIO-backed display hardware state:

- HUBP request state includes active/in-use surface addresses, flip/update-lock status, VMID/TLB/aperture programming, DCC/TMZ controls, underflow and blanking status, request sizing, VM/PTE/meta delivery timing, QoS/TTU ramping, cursor fetch settings, and memory power state.
- HUBPRET state includes buffer allocation, return-data component routing, read-line capture/status, interrupt bits, and local memory power state.
- Cursor and DMDATA state includes cursor image address/size/position/hot spot/mode, stereo controls, destination offsets, DMDATA memory address, update/repeat/size/mode, QoS, status done, and software data injection fields.
- Perfmon state includes selectable counters, counter mode, enable/clear/freeze control, histogram mode, and low/high counter values.
- DPP state includes DPP clock/reset/CRC controls, color conversion format and coefficients, scaler coefficients and ratios, line buffer format, recout/MPC dimensions, memory power state, cursor colors, and color-management LUT/control/region tables.

Persistence is hardware-defined. Many configuration fields retain values until a modeset, plane disable, power gating, suspend/resume, or ASIC reset. Status, interrupt, clear, read-line, CRC, perfmon, memory-power status, and current-state fields may be read-only, sticky, write-one-to-clear, self-clearing, or double-buffered. This generated header does not distinguish those semantics; consuming driver code must know them.

## Dependencies And Integration Points

Primary dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h` supplies matching register offsets and base-index macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c` includes this header and constructs DCN314 register/shift/mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn31/dcn31_hubp.h` defines `HUBP_MASK_SH_LIST_DCN31`, which consumes HUBP/HUBPREQ/HUBPRET/CURSOR field masks and shifts.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn31/dcn31_hubp.c` uses the constructed HUBP tables in functions such as `hubp31_set_unbounded_requesting`, `hubp31_soft_reset`, `hubp31_program_extended_blank_value`, and `hubp31_get_det_config_error`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp.h` and later DPP headers define `TF_SF`/`TF2_SF` and DPP mask-list macros that consume DPP0, DSCL0, CNVC0, and CM0 fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c` and `display/dc/irq/dcn314/irq_service_dcn314.c` also include the DCN 3.1.4 register headers for DMUB and interrupt mapping, though this chunk is mostly HUBP/DPP field data.

The central integration pattern is preprocessor token pasting. A field such as `HUBPREQ3_PREFETCH_SETTINGS__VRATIO_PREFETCH_MASK` is not referenced manually in most code; instead, macro lists instantiate a `struct dcn_hubp2_mask` member used by `REG_UPDATE(PREFETCH_SETTINGS, VRATIO_PREFETCH, value)` after the HUBP instance's register table maps `PREFETCH_SETTINGS` to the concrete instance-3 register.

## Risks And Edge Cases

- Shift/mask drift is the main risk. These macros are untyped constants; a bad bit position or mask can compile cleanly while writing the wrong field or silently truncating values.
- Repeated pipe instances are copy-sensitive. Instance 2 and 3 HUBP/HUBPREQ/HUBPRET/CURSOR/PERFMON blocks are structurally similar, so a single wrong suffix, field width, or cross-instance paste error may only appear when using the affected display pipe.
- Chunk boundaries are partial. The first line starts after the `DMDATA_VM_DONE__SHIFT` group has already begun, and the last line stops inside the `CM0_CM_GAMCOR_RAMB_REGION_*` table. Adjacent chunks are required for whole-file conclusions.
- VM, TLB, aperture, DCC, and TMZ fields affect memory translation and protected/display-compression surfaces. Incorrect masks can cause faults, underflow, wrong addresses, or security-sensitive surface access behavior.
- Timing and QoS fields are tightly coupled to DML calculations. Bad `REFCYC`, `DST_Y`, PTE/meta, TTU, or prefetch masks can cause underruns, late requests, flip glitches, or failures limited to high-bandwidth formats.
- Cursor and DMDATA fields are update-sensitive. Wrong address, size, status, or software-update masks can cause cursor corruption, stale DMDATA, repeated metadata, or stuck done/status polling.
- Power-control and status fields can be sequencing-sensitive around clock gating and power gating. Incorrect force/disable/status masks can leave memories powered unexpectedly or inaccessible when the display code assumes they are available.
- DPP scaler and color-management fields have visual output risk. Bad coefficient, CSC, gamut, gamma, LUT, or region masks can produce incorrect color, broken scaling, CRC mismatches, or hard-to-diagnose pipe-specific visual defects.

## Test Signals

Useful validation is mostly build-time generated-header consistency plus hardware display coverage:

- Build AMDGPU/DC with DCN314 enabled. Missing or renamed macros should fail in `dcn314_resource.c`, HUBP/DPP headers, IRQ, or DMUB code during shift/mask table initialization.
- Mechanically verify that every `__SHIFT` macro in lines 19539-22071 has a matching `_MASK` macro for the same register and field, accounting for the partial first field and partial final register group.
- Diff this chunk against AMD's authoritative DCN 3.1.4 register database and nearby DCN 3.1/3.1.5 generated headers where compatibility is expected.
- Exercise systems or emulation with four display pipes so HUBP instance 3 is actually allocated: multi-monitor modesets, plane enable/disable, flips, stereo/secondary viewport paths, cursor movement, and pipe reassignment.
- Test memory-backed display paths: DCC on/off, TMZ/protected surfaces if supported, VM faults/clears, system aperture setup, suspend/resume, page flips, and high-bandwidth modes that stress PTE/meta prefetch.
- Validate visual pipeline behavior through DPP0: scaling, color keying, pre/post CSC, gamut remap, gamma correction LUT programming, CRC capture, and format conversion for RGB and chroma surfaces.
- Watch kernel logs and display diagnostics for HUBP underflow, DMDATA VM fault/late/underflow status, stuck flip pending, stale cursor/DMDATA done bits, perfmon counter anomalies, read-line interrupt issues, color CRC mismatches, and resume failures.

## Cross-Chunk Notes

Earlier chunks own the start of the pipe-2 HUBPREQ register groups. Later chunks continue `CM0_CM_GAMCOR_RAMB_REGION_*` and then the remaining DPP color-management/register-mask namespace. The final per-file research document should merge adjacent chunks before making complete claims about all DCN 3.1.4 register fields or the full `dcn_3_1_4_sh_mask.h` generated interface.

### subset-b-001842: lines 22072-24583

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 22072-24583

## Purpose

This chunk is generated AMD DCN 3.1.4 display-controller register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit shifts and masks used to pack and unpack fields inside MMIO registers. Runtime DCN314 code combines these definitions with the companion `dcn_3_1_4_offset.h` register offsets through `REG_SET`, `REG_UPDATE`, `REG_GET`, and related AMD display register helpers.

The range covers the tail of DPP0 color-management definitions and then moves into DPP1 display-pipe definitions. It contains 2,113 `#define` lines: 1,055 `__SHIFT` macros and 1,058 `_MASK` macros. The apparent three-macro difference is because the requested range starts after some fields in an already-open register family and ends inside the `CM1_CM_BLNDGAM_RAMB_*` family. Although the path is under a local `ceph-client` source mirror, this header is AMDGPU display-driver ASIC metadata and does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, local variables, dynamic allocations, locks, or includes in this slice. Its interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

Major register families visible in this chunk:

- `CM0_CM_BLNDGAM_*`: DPP0 blend-gamma control, LUT index/data/control, RAM A/B piecewise-linear region starts, slopes, bases, offsets, and 34-region segment descriptors.
- `CM0_CM_HDR_MULT_COEF`, `CM0_CM_DEALPHA`, `CM0_CM_COEF_FORMAT`, `CM0_CM_MEM_PWR_*`, `CM0_CM_SHAPER_*`, and `CM0_CM_3DLUT_*`: DPP0 HDR multiplier, dealpha, coefficient format, gamma/shaper/3DLUT memory power state, shaper LUT programming, 3D LUT data/index/control, output normalization/offset/scale, and test debug fields.
- `DC_PERFMON10_*`: DPP0 display performance monitor fields for event selection, counter modes, hardware start/stop selection, counter state selection, report count, interrupts/status/ack, high/low counter values, and clock/run enable.
- `DPP_TOP1_*`: DPP1 top-level clock gating, soft reset, DPP CRC readback/control, and host-read rate control.
- `CNVC_CFG1_*` and `CNVC_CUR1_*`: DPP1 input converter fields for surface pixel format, format expansion/conversion/bypass, FP bias/scale, color-key ranges, alpha LUTs, pre-dealpha/pre-realpha, pre-CSC matrix banks, pre-degamma, and cursor control/colors/FP scale-bias.
- `DSCL1_*`: DPP1 scaler coefficient RAM selection/data, scaler modes, tap control, 2-tap controls, scale ratios, filter init values, overscan, output sizes, line-buffer format/partitioning/counters, scaler memory power/status, and output-buffer controls.
- `CM1_CM_*`: DPP1 color-management fields for post-CSC, gamut remap, bias, gamcor LUT/PWL RAM A/B regions, blend gamma LUT/PWL RAM A regions, and the beginning of blend-gamma RAM B start fields.

The repeated `*_RAMA_REGION_N_M` and `*_RAMB_REGION_N_M` macros encode two LUT region descriptors per register: region N fields occupy low bits with LUT offset at shift `0x0` and segment count at `0xc`; region M fields occupy high bits with LUT offset at `0x10` and segment count at `0x1c`. These are used by color pipeline code to program double-buffered PWL curve RAMs.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by the display driver:

1. DCN314 resource, IRQ, and DMUB code include `dcn_3_1_4_offset.h` and this mask header.
2. Register-list construction in the DC resource layer token-pastes names such as `CM1_CM_GAMCOR_CONTROL`, `DSCL1_SCL_MODE`, or `DPP_TOP1_DPP_CRC_CTRL` into per-block register and shift/mask tables.
3. DPP, scaler, color, cursor, CRC, perfmon, IRQ, and DMUB paths use the tables with AMD register helpers to read, update, or poll specific fields.
4. Hardware latches or reports field changes according to each register's semantics; this generated file only defines field geometry and does not encode when values may be safely written.

Important ordering constraints therefore live outside this chunk: clocks and memory must be powered before programming LUTs or scaler buffers; mode changes must respect update-pending/current-status fields; LUT RAM selection must be coordinated with RAM A/B double buffering; CRC and perfmon interrupt/status bits require driver-managed clear/ack sequencing.

## State And Persistence Behavior

The chunk stores no software state and writes no persistent files. It describes MMIO-backed GPU state:

- Color-management state: post-CSC and gamut-remap matrices, coefficient formats, bias, gamma-correction and blend-gamma LUTs, shaper LUTs, HDR/3DLUT controls, and RAM A/B PWL region geometry.
- DPP1 conversion/cursor state: surface pixel format, alpha-plane enable, format expansion/conversion, color keying, pre-CSC/pre-degamma, dealpha/re-alpha, cursor enable/mode/color, and update-pending indicators.
- DPP1 scaler state: coefficient RAM contents, taps, scale ratios, initial phases, overscan, RECOUT/MPC dimensions, line-buffer memory partitioning, and OBUF/LB memory power state.
- Diagnostic and performance state: DPP CRC values/control, DPP0 perfmon counter configuration, interrupt status/ack fields, and test debug selectors/data.

Persistence is hardware-defined. Most configuration fields retain values only while the relevant display block remains powered and not reset; status/current/update-pending/perfmon/counter/interrupt fields can be read-only, sticky, self-clearing, or write-one-to-clear depending on the underlying register. This header does not distinguish those semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.1.4 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`, which defines the companion `mm...` register addresses.
- AMD display register helper macros that consume register, shift, and mask tables.

Direct include sites in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`

The main integration surface for the visible fields is the DCN314 DPP and color pipeline. Resource construction maps these generated macros into the DPP, DSCL, CNVC, CM, CRC, perfmon, IRQ, and DMUB abstractions; later higher-level display code programs them during modeset, plane updates, color-management updates, cursor updates, CRC capture, diagnostics, suspend/resume, and low-power transitions.

## Risks And Edge Cases

- Bitfield drift is the central risk. These are untyped integer constants, so a wrong shift or mask can compile cleanly while causing writes to the wrong hardware bits.
- The chunk is boundary-partial. It starts after the beginning of `CM0_CM_GAMCOR_RAMB_REGION_24_25` and stops inside `CM1_CM_BLNDGAM_RAMB_START_SLOPE_CNTL_B`; adjacent chunks are required for complete per-file claims.
- Repeated CM RAM region macros are copy-sensitive. Region numbers, RAM A/B selection, and RGB channel suffixes must match the hardware table; a one-register typo can corrupt only specific curve segments or only one color channel.
- Double-buffered LUT and mode-current fields are sequencing-sensitive. Programming the inactive RAM, toggling select bits, and waiting for `*_CURRENT` or `*_UPDATE_PENDING` state must be done by consumers in the right order.
- Memory-power fields for gamma, shaper, HDR3DLUT, scaler LUT/LB groups, and OBUF can make other writes ineffective or unsafe if a block is gated, forced off, or still transitioning.
- Perfmon and CRC fields include status and ack bits. Incorrect masks can leave interrupts stuck, miss counter events, or produce misleading diagnostic data.
- DPP1 CNVC/DSCL fields affect pixel interpretation and scaling. Incorrect masks can produce wrong color channel routing, alpha behavior, cursor format, scaling phase, line-buffer sizing, underflow, or visible corruption on only some formats or plane sizes.

## Test Signals

Useful validation is mostly generated-header consistency plus display hardware behavior:

- Build AMDGPU/DC with DCN314 enabled; missing or renamed macros should fail in `dcn314_resource.c`, `irq_service_dcn314.c`, or `dmub_dcn314.c` register-table construction.
- Mechanically verify that every field in lines 22072-24583 has coherent shift/mask geometry and that masks match their documented bit widths after applying the shift.
- Diff this chunk against AMD's authoritative DCN 3.1.4 register database and nearby generated DCN headers where register layouts are expected to match.
- Exercise color-management paths: post-CSC, gamut remap, bias, gamma correction, blend gamma, shaper LUT, 3D LUT, HDR multiplier, RAM A/B switching, and suspend/resume restoration.
- Exercise DPP1 plane paths with RGB/YUV, alpha, cursor, color keying, pre-CSC/pre-degamma, scaling up/down, chroma scaling, overscan, and line-buffer partition changes.
- Validate diagnostics: DPP CRC enable/one-shot/continuous modes, perfmon event selection/counting/interrupt ack, and debug index/data access.
- Watch kernel logs and visual output for update-pending timeouts, underflow, CRC mismatch, bad cursor colors, color banding, incorrect alpha, scaling artifacts, perfmon interrupt storms, and resume failures.

## Cross-Chunk Notes

Previous chunks own the beginning of the DPP0 color-management section, including earlier `CM0_CM_GAMCOR_RAMB_*` definitions. Later chunks continue the DPP1 `CM1_CM_BLNDGAM_RAMB_*` region definitions and the rest of the DCN 3.1.4 generated shift/mask namespace. The final per-file research document should merge adjacent chunk reports before making whole-file claims about all DCN314 DPP instances or the complete `dcn_3_1_4_sh_mask.h` register-field map.

### subset-b-001843: lines 24584-27100

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 24584-27100

## Scope

This chunk covers lines 24584-27100 of the generated AMD DCN 3.1.4 shift/mask header. It contains only preprocessor constants and generated register grouping comments: 2,112 `#define` entries, made up of 1,057 `__SHIFT` constants and 1,055 `_MASK` constants, plus 6 `addressBlock` comments. There are no functions, structs, enums, variables, allocations, locks, or executable statements in this range.

The range starts in the middle of the DPP1 color-management `CM1_CM_BLNDGAM_RAMB` block, continues through the end of DPP1 color-management shaper and 3D LUT masks, then moves into DPP1 perfmon and DPP2 register blocks. The DPP2 portion covers top-level DPP control, CNVC conversion/pre-CSC masks, DSCL scaler/memory-power masks, and most of the DPP2 color-management pipeline through the beginning of `CM2_CM_SHAPER_RAMA_REGION_2_3`. The chunk ends mid-register-family; later lines continue the remaining CM2 shaper RAM region definitions.

Although the source tree path is under a local `ceph-client` mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

## Purpose

The purpose of this header slice is to publish symbolic bit positions and masks for DCN 3.1.4 display pipe processor registers. AMDGPU display code combines these macros with the matching `dcn_3_1_4_offset.h` register-address constants and register-helper macros to pack MMIO writes, update individual fields, and decode hardware status without hard-coding numeric field layouts.

This is a generated hardware contract rather than algorithmic code. Runtime behavior is produced by code that includes this header and expands token-pasted field names into these constants. The important behavior is therefore the exact macro name, the associated register/field grouping, and the numeric shift/mask value.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT` gives a field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask within the register word.
- `//<REGISTER>` comments group all fields for one logical register.
- `// addressBlock: ...` comments mark generated hardware address blocks for DPP1 perfmon, DPP2 top, DPP2 CNVC, DPP2 DSCL, and DPP2 CM.

Major constant groups in this slice include:

- DPP1 `CM1_CM_BLNDGAM_RAMB_*` blend-gamma RAM B metadata: per-channel start, start segment, start slope, start base, end base, end slope, offsets, and 34 exponential-region descriptors packed as pairs `REGION_0_1` through `REGION_32_33`.
- DPP1 color-management controls after blend gamma: `CM1_CM_HDR_MULT_COEF`, `CM1_CM_MEM_PWR_CTRL`, `CM1_CM_MEM_PWR_STATUS`, `CM1_CM_DEALPHA`, `CM1_CM_COEF_FORMAT`, shaper control/offset/scale/LUT-index/LUT-data/write-enable masks, shaper RAM A and RAM B start/end/region descriptors, `CM1_CM_MEM_PWR_CTRL2`, `CM1_CM_MEM_PWR_STATUS2`, `CM1_CM_3DLUT_MODE`, `CM1_CM_3DLUT_INDEX`, `CM1_CM_3DLUT_DATA`, `CM1_CM_3DLUT_DATA_30BIT`, `CM1_CM_3DLUT_READ_WRITE_CONTROL`, 3D LUT normalization/output offsets, and CM test-debug index/data masks.
- `DC_PERFMON11_*` DPP1 perfmon field masks for performance-counter source selection, clear/reset/free-run behavior, slice and threshold configuration, start/stop/continue/clear control, counter status, counter value, high/low count words, interrupt status, interrupt type, mode, and auto-clear behavior.
- `DPP_TOP2_*` masks for DPP2 enablement, clock gating, dithering, CRC results/control, soft reset, and host read control.
- `CNVC_CFG2_*` masks for DPP2 surface pixel format, alpha/dealpha/realpha behavior, expansion mode, floating-point conversion bias/scale, color-key controls, 2-bit alpha LUT values, pre-degamma, pre-CSC mode, pre-CSC coefficient pairs for normal and B matrices, and coefficient-format selection.
- `DSCL2_*` masks for DPP2 scaler coefficient RAM tap selection/data, scaler mode and taps, DSCL control, 2-tap mode, manual replication, horizontal/vertical luma and chroma scale ratios and initial phases, black color, update/autocal, overscan, OTG blanking, recout/MPC sizes, line-buffer data format, memory power control/status, vertical counter, and output-buffer memory power control.
- DPP2 `CM2_CM_*` color-management masks: main control and post-CSC/gamut-remap matrices, bias fields, gamma-correction LUT control and RAM A/B region metadata, blend-gamma LUT control and RAM A/B metadata, HDR multiplier, memory power controls/status, dealpha, coefficient format, shaper control/offset/scale/LUT access, and the beginning of shaper RAM A region metadata.

The repeated gamma and shaper region registers use a common packed layout: two regions per register, each with a LUT offset field and a number-of-segments field. Start/end control registers split per-channel R/G/B fixed-point values across start, start-segment, base, end, and slope fields.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time token expansion:

1. DCN 3.1.4 display code includes `dcn_3_1_4_offset.h` and `dcn_3_1_4_sh_mask.h`.
2. Register helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, `REG_SET_*`, and `REG_UPDATE` paste register and field names into generated tokens.
3. The C preprocessor resolves those tokens to the shift and mask constants from this file.
4. Runtime display code performs MMIO reads/writes against the register offsets from the matching offset header.

The declaration order follows the hardware register database rather than driver execution order. In this range the generated sequence finishes a DPP1 CM block, emits DPP1 perfmon masks, then describes DPP2 top/CNVC/DSCL/CM blocks.

## State And Persistence Behavior

The header itself stores no state and persists nothing. It describes fields within hardware registers whose state is owned by the display engine.

Configuration-like fields in this chunk can program DPP color transforms, degamma/gamma/blend-gamma/shaper/3D LUT state, pre-CSC and post-CSC matrices, gamut remap matrices, scaler ratios and phase initialization, color keying, alpha handling, memory power controls, CRC capture, and perfmon counting. These values generally persist until the display driver rewrites them, a modeset or pipe reprogramming path changes them, power gating resets the block, suspend/resume restores state, or the GPU/ASIC is reset.

Status and observation fields include current shaper mode, memory power state, 3D LUT configuration status, perfmon counter state/value/interrupt fields, DPP CRC results/status-style fields, scaler vertical counter, DSCL memory status, and CM memory-power status. These values are hardware-updated and may change independently of any software-visible state transition in this header.

The masks do not encode access type. Consumers must know from the hardware specification and surrounding driver logic which fields are read-only, write-only, sticky, self-clearing, write-one-to-clear, double-buffered, or sequencing-sensitive.

## Dependencies And Integration Points

This chunk depends on the matching generated DCN 3.1.4 offset header. For example, the corresponding offsets for this slice include `regCM1_CM_BLNDGAM_RAMB_*`, `regCM1_CM_3DLUT_*`, `regDC_PERFMON11_*`, `regDPP_TOP2_*`, `regCNVC_CFG2_*`, `regDSCL2_*`, and `regCM2_CM_*` definitions in `dcn_3_1_4_offset.h`; the masks in this file only describe field placement, not register addresses or base-index selection.

Direct include sites found in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`, which includes the DCN 3.1.4 offset and mask headers while constructing the DCN314 display resource layer.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`, which includes the same headers and builds `dmub_srv_dcn314_regs` using `FD_MASK` and `FD_SHIFT` expansion through `DMUB_DCN31_FIELDS()`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c`, which includes the headers for DCN314 interrupt-service register definitions.

Broader integration is through AMD display DPP/CM/DSCL/perfmon helpers that use generated register tables and field macros. Color management code programs gamma correction, blend gamma, shaper LUTs, 3D LUTs, CSC matrices, gamut remap, HDR multiplier, and dealpha behavior. Scaler code programs DSCL tap coefficients, ratios, viewport/recout dimensions, line-buffer format, blanking, and memory controls. DMUB service code consumes masks/shifts to communicate register metadata to firmware-facing services.

The generated offset and mask headers must come from the same register database. Mixing DCN 3.1.4 offsets with masks from DCN 3.1.2, DCN 3.2.x, or DCN 4.x would be risky because many names repeat while block counts and field layouts can diverge.

## Risks And Edge Cases

- The chunk starts inside `CM1_CM_BLNDGAM_RAMB`; the preceding `START_CNTL_B` and earlier RAM B fields are owned by the previous chunk. A final per-file summary must merge adjacent chunks before describing DPP1 blend-gamma RAM B as a complete block.
- The chunk ends inside the `CM2_CM_SHAPER_RAMA_REGION_*` sequence. It includes the start/end controls and regions `0_1` and `2_3`, but later chunks own the remaining shaper RAM A and likely RAM B region definitions.
- Many register families are highly repetitive across CM1/CM2, RAM A/RAM B, and R/G/B channels. Generator drift can be subtle because lines differ only by instance number, RAM bank letter, channel suffix, or region index.
- These are untyped numeric constants. A wrong mask or shift can compile successfully while corrupting adjacent hardware fields or silently misreading status.
- Full-width and high-bit masks appear in perfmon counters, LUT data, CRC values, coefficient fields, and packed pair registers. Callers must avoid signed-width assumptions and should use the register helper types expected by AMD display code.
- LUT and region programming is sequencing-sensitive. `*_LUT_INDEX`, `*_LUT_DATA`, write-enable masks, RAM A/B selection, current-mode/status fields, 3D LUT 30-bit mode, and start/end/region metadata must be programmed in the order required by the display pipeline, not merely with the correct masks.
- Memory-power control fields can gate gamma, blend-gamma, shaper, 3D LUT, scaler line-buffer, and output-buffer memories. Incorrect force/disable values can produce blank output, stale LUT contents, or invalid reads after power transitions.
- Perfmon controls mix counter setup, clear/reset/start/stop behavior, counter value reporting, and interrupt state. Blind read-modify-write patterns can perturb measurement or interrupt behavior if the field access semantics are not followed.
- CNVC and DSCL fields affect visible pixel interpretation and scaling. Errors may manifest only for particular pixel formats, chroma formats, alpha modes, color-key paths, viewport sizes, scaler ratios, or overscan settings.

## Test Signals

Useful validation is mostly build-time consistency plus hardware display behavior:

- Build AMDGPU display code for a DCN314-enabled configuration to catch missing or renamed macros in `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE` expansion.
- Mechanically verify that every complete field in this line range has a consistent shift/mask pair, while accounting for artificial chunk boundaries at the start of `CM1_CM_BLNDGAM_RAMB` and the end of `CM2_CM_SHAPER_RAMA`.
- Compare this slice against AMD's authoritative DCN 3.1.4 register database and the matching `dcn_3_1_4_offset.h` so every register comment here has a corresponding offset/base-index definition.
- Exercise DCN314 display modes that use DPP2 CNVC and DSCL: different surface pixel formats, alpha/dealpha/realpha paths, pre-CSC/pre-degamma, scaling ratios, chroma/luma filtering, overscan, recout sizing, and line-buffer formats.
- Exercise color-management programming on DPP1 and DPP2: degamma/gamma correction, blend-gamma LUTs, shaper LUTs, 3D LUT enable/disable, HDR multiplier, post-CSC, gamut remap, coefficient-format changes, and bank switching between RAM A and RAM B.
- Validate suspend/resume, display hotplug, modeset, and GPU reset paths for correct restoration of CM, DSCL, memory-power, and LUT state.
- Use CRC and perfmon diagnostics where available to confirm that DPP CRC values and `DC_PERFMON11` counters change as expected and do not stick after clear/reset/start/stop sequences.
- Watch kernel logs, display selftests, visual output, color-calibration tests, scaling tests, and hardware CRC/perfmon traces for failures limited to DPP1/DPP2 or to one RAM bank/channel/region.

## Cross-Chunk Notes

The previous chunk should cover the beginning of `CM1_CM_BLNDGAM_RAMB`, including the missing start-control fields immediately before line 24584. The next chunk should complete the `CM2_CM_SHAPER_RAMA_REGION_*` sequence and any following CM2 shaper RAM B or later DPP2 blocks. The final per-file research document should reconcile these boundaries before making whole-file claims about DCN 3.1.4 DPP color-management coverage.

### subset-b-001844: lines 27101-29604

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 27101-29604

## Scope And Purpose

This chunk is a generated-style AMD DCN 3.1.4 register shift/mask header segment. It contains C preprocessor constants only: no functions, structs, enums, storage definitions, or executable control flow. The range covers lines 27101-29604 of `dcn_3_1_4_sh_mask.h` and defines 2116 macros: 1058 `__SHIFT` constants and 1058 matching `_MASK` constants across 371 register symbols.

The purpose of this chunk is to describe field layouts for part of the display pipe color-management and DPP programming surface. It starts mid-register-family in the `CM2` color-management shaper RAMA region definitions, completes the visible `CM2` shaper RAMB region and HDR 3D LUT/test-debug fields, then moves through DPP instance 3 blocks: `DC_PERFMON12`, `DPP_TOP3`, `CNVC_CFG3`, `CNVC_CUR3`, `DSCL3`, and a large portion of `CM3`. The `CM3` range covers color matrix/remap controls, gamma-correction LUTs and piecewise-linear RAMs, blend gamma LUTs and RAMs, HDR multiplier and memory-power fields, dealpha/coefficient format, and most shaper LUT/RAM definitions through `CM3_CM_SHAPER_RAMB_REGION_28_29`.

Every field is represented as a pair:

- `REGISTER__FIELD__SHIFT`, the bit offset for the field.
- `REGISTER__FIELD_MASK`, the field mask already shifted into register position.

This is the ABI consumed by AMDGPU/DC display register helpers together with companion DCN 3.1.4 offset/address headers. The file gives no semantic values itself; it provides the bit positions that make typed display programming code target the correct hardware fields.

## Important Macro Families

The `CM2_CM_SHAPER_*` tail covers the second color-management block's shaper lookup-table segmentation. The visible RAMA and RAMB region registers use pairs of regions per register, with LUT offset fields at low and high halves and segment-count fields at bit positions `0xc` and `0x1c`. The RAMB control groups include per-channel start and end controls for B/G/R, using 18-bit start values, 7-bit start-segment values, 16-bit end values, and 14-bit end-base values. These fields are used when programming piecewise shaper curves before 3D LUT processing.

The `CM2_CM_MEM_PWR_CTRL2` and `CM2_CM_MEM_PWR_STATUS2` fields expose memory-power force/disable/state bits for shaper and HDR 3D LUT memories. The `CM2_CM_3DLUT_*` fields describe 3D LUT mode/size/current mode, 11-bit LUT index, 16-bit paired LUT data, optional 30-bit data mode, write masks, RAM selection, read selection, output normalization, per-channel output offset/scale, and test-debug index/data access.

The `DC_PERFMON12_*` block defines display performance-monitor fields for DPP2/perfmon address block instance 12. It includes event selection, counted-value selection, increment/run modes, hardware start/stop/control selection, interrupt enable/status/ack fields, eight counter-state fields, perfmon state/report count, clock enable, run start/stop selectors, 48-bit-ish value readout split through low/high/misc fields, and read-selection fields. Consumers use these fields for diagnostics and performance counter collection rather than normal modeset image programming.

The `DPP_TOP3_*` block covers DPP instance 3 top-level controls: DPP clock enable and clock-gating disables, test-clock selection, soft reset for CNVC/DSCL/CM/OBUF sub-blocks, CRC result readback for RGBA components, CRC control, and host-read control. These fields are integration points for pipe bring-up, reset, debug CRC validation, and low-level host read access.

The `CNVC_CFG3_*` block describes the DPP3 converter configuration path. It includes surface pixel format, format control, floating-point conversion bias/scale per channel, color keyer enable and per-channel key values, alpha 2-bit LUT, pre-dealpha, pre-CSC mode and matrix coefficients, alternate `B` pre-CSC coefficient registers, coefficient format, pre-degamma mode, and pre-realpha controls. These fields sit early in per-plane processing and determine how source pixels are interpreted and transformed before scaling/color management.

The `CNVC_CUR3_*` block covers cursor overlay controls for DPP3: cursor enable/format, 2x magnification, pitch, line-per-chunk, color0/color1 values, and floating-point scale/bias. These constants are used by cursor programming paths for DPP3 cursor composition.

The `DSCL3_*` block defines DPP3 scaler and line-buffer fields. It includes coefficient RAM tap select/data, scaler mode and tap controls, two-tap hardcoded/sharpness controls, manual replication, horizontal/vertical scale ratios and initial phases for luma and chroma including bottom-field values, black color, update pending, autocal pipe metadata, overscan, OTG blanking, recout and MPC dimensions, line-buffer format and partitioning, line-buffer vertical counters, DSCL/LB/LUT memory-power controls and state readbacks, OBUF bypass/full-buffer/hold controls, and OBUF memory-power fields.

The `CM3_CM_*` block is the largest part of this chunk. It defines:

- Core bypass/update state in `CM3_CM_CONTROL`.
- Post-CSC mode/current mode plus 3x4 coefficient matrices for normal and `B` banks.
- Gamut remap mode/current mode plus 3x4 coefficient matrices for normal and `B` banks.
- Bias controls for Cr/R and Y/G/Cb/B channels.
- Gamma-correction mode/select/PWL-disable/current fields, LUT index/data/control, and RAMA/RAMB start, slope, base, end, offset, and region segmentation fields.
- Blend-gamma mode/select/PWL-disable/current fields, LUT index/data/control, and parallel RAMA/RAMB piecewise-linear controls.
- HDR multiplier coefficient, CM memory-power control/status, dealpha, coefficient-format controls, shaper control, shaper offsets/scales, shaper LUT access, shaper LUT write mask, and most shaper RAMA/RAMB segmentation fields.

The repeated `RAMA`/`RAMB` region families encode 34 piecewise regions as packed pairs. The recurring masks show a 9-bit LUT offset (`0x000001FF` or `0x01FF0000`) and a 3-bit segment count (`0x00007000` or `0x70000000`) for each region. Start/end controls and offsets are separated by color channel, reflecting the per-channel PWL programming model.

## APIs, Types, And Functions

There are no callable APIs, C types, function bodies, or inline helpers in this chunk. The effective API is the generated macro naming convention used by AMD register helpers:

- The register symbol prefix, such as `DSCL3_SCL_MODE` or `CM3_CM_GAMCOR_CONTROL`, identifies a hardware register whose address is supplied by a companion `dcn_3_1_4_*offset*` or address header.
- The field name between the double underscores identifies the programmable or readable bitfield.
- The `__SHIFT` macro gives the insertion/extraction shift.
- The `_MASK` macro gives the pre-shifted bit mask.

Some field names themselves end in `MASK`, producing generated identifiers such as `CM2_CM_3DLUT_READ_WRITE_CONTROL__CM_3DLUT_WRITE_EN_MASK_MASK` and `CM3_CM_SHAPER_LUT_WRITE_EN_MASK__CM_SHAPER_LUT_WRITE_EN_MASK_MASK`. These names are awkward but intentional because the generator preserves the hardware field name and then appends the macro-role suffix.

## Control Flow

The header has no local runtime control flow. The implied control flow lives in display driver code that includes this header:

1. Select the DCN 3.1.4 register address for a DPP/CM/DSCL/CNVC/perfmon register.
2. Compose or read a 32-bit MMIO register value.
3. Clear a field with `REGISTER__FIELD_MASK`.
4. Insert a value shifted by `REGISTER__FIELD__SHIFT`.
5. Write the register or extract readback/status fields through AMDGPU/DC register access macros.

The field families imply several external programming sequences. A DPP pipe setup typically enables clocks and releases soft resets, programs CNVC pixel format and pre-CSC/color-key/cursor state, configures DSCL ratios/taps/recout/line-buffer state, then programs CM post-CSC, gamut remap, gamma, blend gamma, shaper, and optional HDR 3D LUT state in a carefully ordered update sequence. LUT and PWL programming flows normally select an index or RAM bank, write data and region descriptors, set write-enable masks, then switch modes or wait for current-mode/update-pending fields to reflect hardware state. Perfmon flows select events and counter modes, start counting, read low/high value registers, and clear/ack interrupt status.

## State And Persistence Behavior

The macros do not hold software state. They describe persistent hardware register state in the DCN display controller. Values written through these fields remain in the relevant DPP/CM/DSCL/CNVC/perfmon hardware registers until reset, power-gating, modeset reprogramming, or hardware state-machine side effects change them.

State domains visible in this chunk include:

- Per-pipe DPP3 top-level clock, reset, host-read, and CRC diagnostic state.
- DPP3 converter source format, floating-point conversion, pre-CSC, color-key, pre-dealpha/pre-realpha, and cursor state.
- DPP3 scaler ratios, taps, coefficient RAM contents, phase initialization, recout/MPC dimensions, overscan/blanking, line-buffer partitioning, update-pending state, and DSCL/OBUF memory-power state.
- CM2 shaper/HDR 3D LUT and CM3 gamma/blend-gamma/shaper/3D-color-management LUT programming state.
- CM3 matrix state for post-CSC and gamut remap, including alternate `B` coefficient banks and current-mode readbacks.
- Memory-power force/disable/status state for CM, shaper, HDR 3D LUT, DSCL LUT/LB groups, and OBUF memories.
- Perfmon event selection, run state, interrupt status/ack state, and counter readback state.

Many fields are mode-programming state, but others are hardware-observed status or handshake state. Examples include `*_MODE_CURRENT`, `CM_UPDATE_PENDING`, `SCL_UPDATE_PENDING`, memory-power `*_STATE`, CRC values, perfmon active/status bits, counter interrupt status/ack bits, and line-buffer vertical counters. Callers must treat these according to the hardware specification, especially for write-one-to-clear or readback-latched status fields.

## Dependencies And Integration Points

This chunk depends only on the C preprocessor, but it is useful only with AMDGPU/DCN register infrastructure:

- Companion DCN 3.1.4 register address/offset headers provide the MMIO addresses corresponding to these shift/mask macros.
- AMD display-core register helper macros combine register addresses, field masks, and shifts for `REG_SET`, `REG_UPDATE`, `REG_GET`, or generated table-style accessors.
- DPP/DPP3 resource construction and pipe programming code consumes `DPP_TOP3`, `CNVC_CFG3`, `CNVC_CUR3`, `DSCL3`, and `CM3` fields for per-plane image processing.
- Color-management code consumes `CM*_CM_POST_CSC`, `CM*_CM_GAMUT_REMAP`, `CM*_CM_GAMCOR`, `CM*_CM_BLNDGAM`, `CM*_CM_SHAPER`, and `CM*_CM_3DLUT` fields when programming CSC matrices, transfer functions, gamma ramps, shaper LUTs, blend gamma, and HDR 3D LUTs.
- Scaling code consumes `DSCL3_*` fields for tap programming, scale ratios, initial phase, line-buffer memory, output size, and scaler update.
- Cursor code consumes `CNVC_CUR3_*` fields for cursor format, colors, pitch, magnification, and FP scale/bias.
- Debug and validation paths consume `DPP_TOP3_DPP_CRC_*`, `CM2_CM_TEST_DEBUG_*`, and `DC_PERFMON12_*` fields for CRC, test/debug access, and performance counters.
- Power-management and clock-gating code consumes memory-power and clock-gating fields to save power or force memories on for programming/debug.

The repeated instance prefixes are integration-critical. `CM2` belongs to one DPP/color-management instance, while `DPP_TOP3`, `CNVC_CFG3`, `CNVC_CUR3`, `DSCL3`, and `CM3` belong to instance 3. Using the wrong instance prefix can silently program the wrong pipe.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. Shift/mask constants compile as ordinary macros; if one value is wrong, callers can overwrite reserved bits or unrelated fields without compiler warnings. Symptoms would appear as incorrect color, broken scaling, missing cursor, failed LUT programming, black screens, power-gating issues, CRC mismatches, or invalid perfmon data.

Boundary risk is high for this chunk. It begins inside `CM2_CM_SHAPER_RAMA_REGION_2_3`, because the `REGION2` shift/mask entries and part of the `REGION3` entries are in the prior chunk. It also ends inside the `CM3_CM_SHAPER_RAMB_REGION_28_29` family, before the remaining mask entries and later shaper RAMB regions appear in the next chunk. The final per-file report must reconcile adjacent chunks before describing those register families as complete.

The repeated PWL region patterns are copy/generation-sensitive. Region pairs use fixed positions for low/high LUT offsets and segment counts; an off-by-one region number, swapped channel suffix, or mismatched RAMA/RAMB prefix would only affect particular gamma/shaper curve segments and may be visible only on specific color-management configurations.

Mode/current and update-pending fields are sequencing-sensitive. Programming CM matrices, gamut remap, gamma, blend gamma, shaper, and 3D LUT state requires callers to respect bank selection, write-enable masks, current-mode readbacks, and update handshakes. Incorrect ordering can leave stale LUTs or half-applied color transforms.

Memory-power fields can interact with programming. Forcing memories off or relying on power-gated RAM while writing DSCL coefficient RAM, line-buffer state, shaper RAMs, gamma RAMs, or HDR 3D LUT entries can cause writes to be lost or readbacks to look invalid. Status fields should be polled or managed through existing power sequencing.

Mask literal width is a C-integration risk. Many masks use `L` suffixes, including `0xFFFFFFFFL`, `0xFFFF0000L`, and high-bit masks. Callers should use unsigned 32-bit-safe intermediates through the existing register helpers rather than ad hoc signed arithmetic.

Perfmon and debug fields can perturb state if used carelessly. Counter control, interrupt ack, debug index/write-enable, CRC one-shot/continuous state, and host-read controls are meant for diagnostics. Accidental writes during normal modeset paths can hide real performance data or disturb debug/readback flows.

## Test Signals

Useful validation signals are mostly build, static-generation, and hardware integration checks:

- Build coverage for DCN 3.1.4 display code that includes `dcn_3_1_4_sh_mask.h` and instantiates register-field tables for DPP, DSCL, CNVC, cursor, CM, and perfmon blocks.
- Static checks that every `REGISTER__FIELD__SHIFT` in this range has the expected `REGISTER__FIELD_MASK`, masks align to shifts, and generated high/low packed fields do not overlap.
- Diff checks against AMD's authoritative DCN 3.1.4 register database or generated header source, especially around the partial chunk boundaries and repeated RAMA/RAMB region families.
- Modeset tests using DPP3 with scaling enabled/disabled, different pixel formats, chroma formats, pre-CSC, color keying, cursor formats, and recout/MPC sizes.
- Color-management tests covering post-CSC, gamut remap, gamma correction, blend gamma, shaper LUTs, HDR multiplier, HDR 3D LUT, 30-bit 3D LUT mode, alternate coefficient banks, and update-pending/current-mode transitions.
- LUT/RAM programming tests that write and read back gamma, blend-gamma, shaper, DSCL coefficient RAM, and 3D LUT entries across boundary indices and region pairs.
- Power-management tests that exercise CM, DSCL, line-buffer, OBUF, shaper, and HDR 3D LUT memory power states across suspend/resume, blanking, and pipe enable/disable.
- CRC/debug/perfmon tests that enable DPP3 CRC, read RGBA CRC values, configure `DC_PERFMON12` events/counters/interrupt ack paths, and verify counter values remain stable across normal display operation.

## Cross-Chunk Notes

This is chunk 12 of 26 for `dcn_3_1_4_sh_mask.h`. It should be merged with prior chunks for the start of `CM2` shaper/gamma/color-management definitions and with following chunks for the rest of `CM3_CM_SHAPER_RAMB_REGION_28_29`, later `CM3` fields, and subsequent DCN 3.1.4 register blocks. The final per-file document should present this as generated field metadata for the full DCN 3.1.4 display register set, not as an independently complete API module.

### subset-b-001845: lines 29605-32147

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 29605-32147

## Scope

This chunk is `subset-b-001845`, covering lines 29605-32147 of the generated DCN 3.1.4 register shift/mask header. It is a source-aligned chunk document only; the full per-file research document is expected to be assembled later from all chunks for `dcn_3_1_4_sh_mask.h`.

The chunk starts mid-definition for `CM3_CM_SHAPER_RAMB_REGION_28_29`, continues through several color-management and output-pixel-processor register blocks, covers the complete `OTG0` timing-generator field surface, and ends in the first half of `OTG1_OTG_TRIGA_CNTL`.

## Purpose

`dcn_3_1_4_sh_mask.h` provides generated C preprocessor constants for AMD DCN 3.1.4 display hardware register fields. For each hardware register field, it defines a `__SHIFT` value and a `_MASK` value. Driver code combines these constants with register offsets from `dcn_3_1_4_offset.h` to read, write, and update individual bitfields in memory-mapped display registers.

Within this chunk, the constants describe:

- Color-management shaper RAM and 3D LUT programming fields for `CM3`.
- Display performance-monitor counter control/status/value fields for DPP perfmon instance 13 and OPP perfmon instance 14.
- Formatter (`FMT0`-`FMT3`) clamp, pixel encoding, subsampling, dithering, truncation, 4:2:0 memory, and 4:2:2 control fields.
- Display pattern generator (`DPG0`-`DPG3`) fields for test-pattern enable, ramp generation, colors, dimensions, and status.
- Output pixel processor buffer and pipe fields (`OPPBUF0`-`OPPBUF3`, `OPP_PIPE0`-`OPP_PIPE3`), including 3D parameters and CRC controls/results.
- Output data path support fields in `OPP_TOP`, ABM, DSC remapper (`DSCRM0`-`DSCRM3`), and ODM/OPTC input (`ODM0`-`ODM3`).
- Full `OTG0` timing-generator fields for horizontal/vertical timing, vtotal/DRR control, triggers, stereo/interlace, status readback, interrupts, update locks, CRC capture, global sync lock, DSC start position, pipe update status, and spare storage.
- The beginning of equivalent `OTG1` timing-generator fields, through `OTG1_OTG_TRIGA_CNTL`.

## Important API Surface

This header chunk does not declare C functions or types. Its API is the macro namespace exported to the AMD display driver.

Every definition follows the generated field convention:

- `REGISTER__FIELD__SHIFT` gives the low bit position for `FIELD` inside `REGISTER`.
- `REGISTER__FIELD_MASK` gives the bit mask for the same field.

The common AMD display helpers depend on this exact spelling. In `display/dc/inc/reg_helper.h`, `FN(reg, field)` expands to `FD(reg##__##field)`, and `FD` is supplied by each hardware block to fetch the shift/mask pair from its register-field table. In lower-level/common code, `CGS_REG_FIELD_SHIFT(reg, field)` and `CGS_REG_FIELD_MASK(reg, field)` use the same token-pasting naming contract.

The DCN314 resource setup includes this file alongside `dcn_3_1_4_offset.h`, then uses block-specific field-list macros to populate register descriptors. A mismatch between these generated names and the field lists in files such as `display/dc/opp/*`, `display/dc/optc/*`, or `display/dmub/src/*` usually fails at compile time because the token-pasted macro or struct member no longer exists.

Important macro families in this chunk:

- `CM3_CM_SHAPER_RAMB_REGION_*`, `CM3_CM_MEM_PWR_*`, and `CM3_CM_3DLUT_*`: fields for shaper LUT region layout, memory power control/status, 3D LUT mode/index/data/read-write selection/output normalization, RGB output offsets/scales, and CM test-debug access.
- `DC_PERFMON13_*` and `DC_PERFMON14_*`: performance-counter event selection, counted value selection, increment/run/interrupt modes, counted-value type, hardware stop controls, counter state, perfmon state, run-enable start/stop selection, interrupt status/ack bits, and low/high counter value access.
- `FMT{0,1,2,3}_*`: repeated formatter instance fields for clamp bounds, dynamic expansion, output pixel encoding/subsampling, spatial and temporal dithering, truncation depth/mode, pseudo-random dither seeds, clamp control, side-by-side stereo, 4:2:0 map-memory power, and 4:2:2 control.
- `DPG{0,1,2,3}_*`: repeated display-pattern-generator fields for enable, ramp mode, ramp increment, dimensions, color components, offset segment, and status.
- `OPPBUF{0,1,2,3}_*`: active width, pixel repetition, display segmentation, 3D vactive space sizes, left/right eye offsets, and additional buffer control.
- `OPP_PIPE_CRC{0,1,2,3}_*`: CRC enable/source/stereo/reset/window/control fields and result registers for red/green and blue channels.
- `ODM{0,1,2,3}_OPTC_*`: OPTC input global control, segment source selection, data format/DSC mode, bytes per pixel, slice/segment width, input clock gating/status, memory selection, and spare register fields.
- `OTG0_OTG_*`: the broadest family in this chunk, defining the complete timing-generator control surface for one OTG instance.
- `OTG1_OTG_*`: the same generated naming pattern for a second OTG instance begins near the end of the chunk, but this chunk stops before completing `OTG1`.

## Control Flow

There is no runtime control flow in this header. Its control-flow impact is indirect:

1. DCN314 initialization includes the generated offset and shift/mask headers.
2. Resource construction macros create per-block register and field tables for OPP, OPTC/OTG, DMUB, and other display components.
3. Runtime display code invokes helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `OPP_SF`, or `SF`-based tables with semantic field names.
4. The helpers use the generated shifts and masks to preserve unrelated register bits while packing or extracting the requested field.

For example, OTG timing code can update `OTG0_OTG_H_TOTAL__OTG_H_TOTAL` or `OTG0_OTG_V_TOTAL_CONTROL__OTG_V_TOTAL_MIN_SEL` through token-pasted field names without hard-coding bit positions in the functional timing-generator implementation. Similarly, OPP code can program formatter dither/truncation fields using the `FMT0_*` field definitions, and CRC/debug code can read back `OPP_PIPE_CRC*_OPP_PIPE_CRC_RESULT*` or `OTG0_OTG_CRC*_DATA_*` fields.

The chunk also contains many write-one-to-clear or ack-style interrupt fields, such as `*_ACK`, `*_CLEAR`, and `*_INT_STATUS`. The header does not encode side effects, but its masks are the exact bits later used by interrupt handlers or polling paths.

## State And Persistence Behavior

The macros themselves are compile-time constants and maintain no software state. The state they address lives in DCN hardware registers and associated memories:

- `CM3_CM_SHAPER_RAMB_REGION_*` and `CM3_CM_3DLUT_*` fields select and populate color LUT RAM state. These values persist in display hardware until reprogrammed, reset, power-gated, or overwritten during a mode/color pipeline update.
- `CM3_CM_MEM_PWR_CTRL2` and `CM3_CM_MEM_PWR_STATUS2` represent hardware memory power requests and observed memory power state for shaper and HDR 3D LUT RAMs.
- `FMT*` fields persist formatter output behavior: clamp limits, pixel encoding, dithering/truncation mode, dither seeds, 4:2:0 memory power, and 4:2:2 conversion state.
- `DPG*` fields persist pattern-generator mode and color/ramp parameters, typically used for test patterns or diagnostics.
- `OPPBUF*` and `OPP_PIPE*` fields persist OPP buffer layout, segmentation/MSO-related configuration, and pipe routing.
- `OPP_PIPE_CRC*`, `OTG0_OTG_CRC*`, and perfmon fields expose accumulating or latched diagnostic state. Some status bits are cleared through paired `ACK` or `CLEAR` fields.
- `ODM*` fields persist input segmentation and DSC/format selection for the OPTC path. These are central to multi-stream/output-split modes and need to match pipe/resource allocation.
- `OTG0` timing fields persist the active timing-generator configuration: totals, blanking, sync timing/polarity, dynamic refresh rate ranges, master enable, global update lock state, vertical interrupt positions, global sync lock behavior, CRC windows, and pipe update status.

Most of these registers are not persisted across GPU reset, suspend/resume reinitialization, or display engine power-down. Driver state reconstruction depends on the DC resource and hardware-sequencing layers reprogramming the correct fields from current display state.

## Dependencies And Integration Points

Primary dependencies:

- `dcn_3_1_4_offset.h`: provides the matching register addresses and base-index macros. The shift/mask definitions in this chunk are only meaningful when paired with the corresponding offsets.
- `display/dc/inc/reg_helper.h`: supplies generic field packing/unpacking helpers used by display hardware blocks.
- `display/dc/resource/dcn314/dcn314_resource.c`: includes this header and wires DCN314 register definitions into resource construction.
- OPP implementation and headers, including `display/dc/opp/dcn10/dcn10_opp.h` and later OPP layers: consume the `FMT*`, `OPPBUF*`, and `OPP_PIPE_CRC*` field names through OPP field-list macros.
- OPTC/OTG implementation and headers, including `display/dc/optc/dcn32/dcn32_optc.h` and related timing-generator code: consume the `OTG0_*` and `ODM0_*` fields and instantiate repeated blocks for other hardware instances.
- DMUB display code: includes the DCN314 shift/mask header for firmware-facing register access tables.

Integration is heavily macro-driven. The visible register prefix often encodes a hardware instance (`FMT0`, `FMT1`, `ODM0`, `OTG0`, `OTG1`), while functional code often uses a block-local register table and an instance id. The resource layer maps instance-specific offsets and shift/mask values into those tables so shared OPP/OPTC code can operate on instance-agnostic field members.

## Register Block Notes

### CM3 Color Management

The chunk starts at line 29605 inside `CM3_CM_SHAPER_RAMB_REGION_28_29`, so the first two shift definitions for region 28 are in the previous chunk. The visible lines complete region 29 shifts and the region 28/29 masks, then define region pairs 30/31 and 32/33. Each pair uses 9-bit LUT offset masks (`0x000001FF`/`0x01FF0000`) and 3-bit segment-count masks (`0x00007000`/`0x70000000`) packed into low and high halfwords.

`CM3_CM_MEM_PWR_CTRL2` and `CM3_CM_MEM_PWR_STATUS2` describe force/disable controls and status fields for shaper and HDR 3D LUT memories. `CM3_CM_3DLUT_MODE`, index, data, 30-bit data, read/write control, normalization, RGB offset/scale, and test-debug registers form the programming surface for the 3D LUT path.

### Performance Monitors

`DC_PERFMON13_*` is attached to `dce_dc_dpp3_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`, and `DC_PERFMON14_*` is attached to `dce_dc_opp_opp_dcperfmon_dc_perfmon_dispdec`. Both blocks expose the same structure:

- `PERFCOUNTER_CNTL` for event selection, counted value source, increment mode, hardware/run enable, restart, interrupt enable, active status, and counter select.
- `PERFCOUNTER_CNTL2` for counted-value type, stop selectors, count-off selector, and second-level selector.
- `PERFCOUNTER_STATE` for eight packed counter states and selection bits.
- `PERFMON_CNTL`/`PERFMON_CNTL2` for perfmon state, repeat count, count-off interrupt behavior, clock enable, and run-enable start/stop selectors.
- `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW` for interrupt status/ack and counter value readback.

These fields are diagnostic and performance-observation infrastructure. Bugs here may not break basic scanout but can break perf counters, debug tooling, or tests that rely on perfmon interrupts and value reads.

### OPP Formatter And Test/CRC Blocks

The `FMT0` through `FMT3` register groups are repeated with identical field layouts. They control output formatting per OPP instance: color clamp lower/upper limits per component, dynamic expansion enable/mode, pixel encoding and subsampling, stereo override, dithering/truncation enable/depth/mode, temporal dither parameters, random seed registers, clamp behavior, 4:2:0 memory power, and 4:2:2 control.

`DPG0` through `DPG3` provide per-OPP pattern-generator controls. Fields cover enable/mode, ramp increment, dimensions, RGB/YCbCr color registers, offset segment, and status. These are likely used by diagnostics, bring-up, or validation paths rather than normal composition.

`OPPBUF0` through `OPPBUF3` cover active width, pixel repetition, display segmentation, overlap pixels, 3D vactive space sizing, 3D offset parameters, and buffer control. These fields integrate with multi-stream output, stereo/3D, and segmentation decisions made above the OPP layer.

`OPP_PIPE_CRC0` through `OPP_PIPE_CRC3` provide CRC enable/source/mode/reset/window selection and result fields. They are important for display validation, pipe CRC debugfs-style tests, and visual correctness checks.

`OPP_TOP_CLK_CONTROL` and `OPP_ABM_CONTROL` provide top-level OPP clock gating/status and ABM pipe source selection. `DSCRM0` through `DSCRM3` define DSC forward-remapper configuration, including source selection, enable/disable state, and memory power fields.

### ODM And OPTC Input

`ODM0` through `ODM3` describe the OPTC input and output data merger path. Their fields include underflow status/clear, double-buffer pending state, segment source selectors, number of input segments, memory selection, DSC/data format mode, DSC bytes per pixel, DSC slice width, segment width, input clock enable/on/gate-disable, and spare registers.

These definitions are used when a stream is split across multiple pipes or when DSC/ODM combine/split modes are active. The segment source fields must stay consistent with pipe topology and timing-generator programming.

### OTG0 Timing Generator

The `OTG0` block is the largest part of this chunk. It defines the bitfield surface for one output timing generator:

- Basic timing: horizontal total, hblank start/end, hsync start/end/control, timing divide mode, vertical total/min/max/mid, vblank, vsync, and vsync mode.
- Dynamic refresh and vtotal control: min/max selection, mid replacing min/max, forced lock, event active period, mid frame count, set-vtotal-min mask, DRR timing interrupts, DRR reach range, change limit, trigger window, average frame, and last-used vtotal.
- Triggers and flow: trigger A/B source, pipe select, polarity, edge detect, delay, clear/manual trigger; force-count-now controls; flow-control position/delay; manual trigger/flow-control bits.
- Enable/status/readback: master enable, current master enable state, start/disable point control, field number, output mux, pixel data readback, blanking/status/position/frame/vf/hv count, count reset/control, interlace status/control, and stereo status/control.
- Interrupts: generic OTG interrupt control, vertical interrupt 0/1/2 positions and controls, force-vsync-next-line status/clear, vtotal interrupt status, and vsync nominal clear.
- Update synchronization: update lock, double-buffer controls, master update lock/status, global update controls, vstartup/vupdate/vready, global sync status, global sync lock control/window, vupdate keepout, and global control registers.
- CRC/static screen/debug: CRC control, CRC windows, CRC data registers, CRC signature masks, static screen event/status masks, 3D structure, clock control/status, DSC start position, pipe update status, and spare register.

The chunk then begins `OTG1`, repeating the initial timing fields and reaching `OTG1_OTG_TRIGA_CNTL`. The rest of OTG1 is outside this chunk.

## Risks

- Generated header drift is high impact. If a shift or mask does not match the hardware register specification, the functional code may compile and run while silently writing the wrong bits.
- Repeated instance blocks are easy to misalign. `FMT0`-`FMT3`, `DPG0`-`DPG3`, `OPPBUF0`-`OPPBUF3`, `ODM0`-`ODM3`, and `OTG0`/`OTG1` must retain identical field layouts where the hardware expects repeated instances.
- Boundary chunks can obscure complete register definitions. This chunk starts inside `CM3_CM_SHAPER_RAMB_REGION_28_29` and ends inside `OTG1_OTG_TRIGA_CNTL`; merge/reconciliation must join adjacent chunks before treating those registers as fully documented.
- Interrupt fields with `ACK`, `CLEAR`, `MSK`, `STATUS`, and `INT_TYPE` have hardware side effects that are not visible in this header. Callers must know whether a field is read-only, write-one-to-clear, level-triggered, or edge-triggered from the register spec or existing driver behavior.
- Timing-generator fields are mode-critical. Incorrect masks for totals, blanking, sync, update locks, or DRR can cause blank screens, unstable refresh rates, hangs waiting for pending updates to clear, or missed vertical interrupts.
- CRC/perfmon fields are test-critical. They may not affect ordinary desktop output, but regressions break validation tools, pipe CRC tests, performance instrumentation, and display debug workflows.
- Power-control fields can create resume or low-power bugs. Incorrect memory power force/disable masks for LUT, formatter map memory, DSC remapper, or OPP top clock control can manifest only after power-gating, suspend/resume, or mode-set sequences.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Build coverage for DCN314 display code, especially `dcn314_resource.c`, OPP, OPTC, and DMUB users. Token-pasted field references catch many naming mismatches at compile time.
- KMS mode-set tests across multiple timing generators, including single-display and multi-display configurations, to exercise `OTG0` and `OTG1` timing fields.
- Variable refresh / DRR tests that verify vtotal min/max/mid programming, DRR trigger windows, update pending status, and vtotal reach interrupts.
- Pipe CRC tests that compare stable CRC output from `OPP_PIPE_CRC*` and `OTG0_OTG_CRC*` result fields under known frame content.
- Dithering, truncation, pixel-format, 4:2:0, and 4:2:2 output-format tests to cover the `FMT*` field families.
- DSC and ODM split-mode tests to exercise `DSCRM*` and `ODM*` source, format, width, bytes-per-pixel, and memory-selection fields.
- Display pattern generator diagnostics for `DPG*` ramp/color/dimension fields.
- Suspend/resume and display power-gating tests to reveal incorrect memory power and clock-gating masks.
- Perfmon/debug tests that program `DC_PERFMON13` and `DC_PERFMON14` event counters, verify interrupt status/ack handling, and read low/high counter values.

## Research Notes

The line range was read directly from the source header and cross-checked against `Docs/researches/chunk_manifest.tsv`, which maps `subset-b-001845` to lines 29605-32147 and output path `Docs/researches/chunks/subset-b-001845_research.md`. No final source-tree report was written, and `Docs/researches/blueprint_checklist.md` was not modified.

### subset-b-001846: lines 32148-34607

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 32148-34607

## Purpose

This chunk is generated AMD DCN 3.1.4 register field metadata. It contains no executable C logic; it exposes preprocessor constants that describe bit shifts and masks for MMIO-backed display timing-generator, OPTC miscellaneous, ODM memory-power, and display perfmon registers.

The requested range covers 2,460 source lines and contains 2,142 `#define` entries: 1,066 `__SHIFT` macros and 1,076 `_MASK` macros. It starts in the middle of `OTG1_OTG_TRIGA_CNTL`, continues through the rest of the OTG1 timing-generator block, includes complete OTG2 and OTG3 timing-generator blocks, covers `dce_dc_optc_optc_misc_dispdec`, and ends at the first field of `DC_PERFMON15_PERFMON_CNTL` in the `dce_dc_optc_optc_dcperfmon_dc_perfmon_dispdec` block.

Although the local path is under a `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct register accesses in this range. The public API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a named hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

These constants are consumed together with `dcn_3_1_4_offset.h` and AMD display register helper macros such as `SR`, `SF`, `HWS_SF`, `REG_GET`, `REG_SET`, `REG_SET_2`, and `REG_UPDATE`. The masks and shifts are intentionally untyped; correctness depends on token-pasting the register and field names into the proper generated macro.

Major register families in this slice:

- OTG1 tail: completes `OTG1_OTG_TRIGA_CNTL` and covers manual triggers, trigger B, force-count-now, flow control, core OTG enable/control/status, interlace and stereo controls, snapshot fields, interrupt control, update locks, vertical interrupts, CRC configuration/data, static-screen controls, 3D structure fields, global sync and GSL controls, master update-lock timing windows, dynamic refresh-rate fields, M_CONST DTO, DSC start position, pipe update status, and spare register.
- Full OTG2 and OTG3 blocks: complete per-instance timing generator definitions for horizontal and vertical timing, blank/sync windows, timing dividers, vtotal min/max/mid and DRR controls, trigger A/B, flow control, stereo/interlace, status counters, snapshots, interrupts, CRC windows/data, global sync events, GSL windows, update-lock windows, DSC start position, and pipe update status.
- OPTC misc block: `GSL_SOURCE_SELECT`, `OPTC_CLOCK_CONTROL`, `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL3`, `ODM_MEM_PWR_STATUS`, and `OPTC_MISC_SPARE_REGISTER`.
- DC perfmon block start: `DC_PERFMON15_PERFCOUNTER_CNTL`, `DC_PERFMON15_PERFCOUNTER_CNTL2`, `DC_PERFMON15_PERFCOUNTER_STATE`, and the first `DC_PERFMON15_PERFMON_CNTL__PERFMON_STATE__SHIFT` field.

The OTG fields define the low-level vocabulary for programming display scanout timing: total and active/blank counts, sync polarity/mode, live status position, frame/vblank/hv counters, vertical interrupts, update barriers, CRC sampling windows, global update lock, GSL synchronization, DRR vtotal windows, and DSC start position. OPTC misc fields provide shared global sync source routing, display-clock gating state, and ODM memory power controls. The perfmon fields define event selection, counted-value type, counter gating/stop policy, interrupt enable/status, and per-counter state selection for DC performance counters.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes this generated header and constructs register tables or direct register writes from the macros:

1. DCN314 code includes `dcn/dcn_3_1_4_offset.h` and `dcn/dcn_3_1_4_sh_mask.h`.
2. Resource, timing-generator, IRQ, hwseq, and DMUB code expands register-table macros such as `SR(...)`, `SF(...)`, and `HWS_SF(...)`.
3. Register helper macros combine a selected register offset with these shift/mask constants to read, set, or update individual MMIO fields.
4. Higher-level display sequencing decides when to enable OTGs, program timing totals, lock updates, arm vertical interrupts, change DRR timing, collect CRCs, route GSL readiness, control ODM memory power, and configure perf counters.

The generated constants do not encode required order. Consumers must still follow hardware sequencing rules around blanking periods, double-buffered updates, vupdate/vready/vstartup events, update locks, interrupt ack/clear fields, power gating, DRR changes, and multi-pipe synchronization.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on its own. It describes fields in hardware registers whose state is owned by the display engine.

Persistent or configuration-like hardware state represented here includes:

- Timing values: horizontal and vertical totals, blank intervals, sync intervals, sync polarity, timing divider mode, interlace/stereo modes, DSC start position, M_CONST DTO phase/modulo, and request mode.
- Enable and routing state: `OTG_MASTER_EN`, `OTG_OUT_MUX`, trigger source selections, flow-control source/polarity, GSL enable/master/source routing, global update lock selection, DIG update position, and OPTC display-clock gate/test-clock settings.
- Power policy: ODM memory force/disable fields, unassigned and vblank power modes, and per-bank memory power status fields.
- Perfmon setup: selected perf event, count mode, run-enable mode, hardware stop selection, count-off source, restart and interrupt enable policy, counter select, and per-counter state selectors.

Volatile or event-like hardware state includes:

- Current scanout status: vblank/hblank/active/sync bits, vertical/horizontal counters, nominal vertical count, frame/vf/hv counters, current field/eye, current master enable state, and pipe update pending flags.
- Sticky events and interrupts: trigger occurred bits, force-count-now occurred/clear, force-vsync-next-line occurred/clear, snapshot occurred/clear/manual trigger, vertical interrupt status/clear, vtotal-min event ack/mask, DRR timing/vtotal-reach event clear, global vstartup/vupdate/vready event clear/status, perf counter interrupt status/ack, and count-off interrupt state.
- Measurement outputs: pixel readback values, CRC data registers, CRC one-shot pending bits, global sync status bits, ODM power-state readback, and perf counter active/state readback.

Persistence and side effects are hardware-defined. Many configuration fields retain values until modeset, reset, suspend/resume restore, power-gating transition, or ASIC reset. Status and interrupt fields may be read-only, sticky, self-clearing, write-one-to-clear, or clear-on-write. This mask header does not identify access permissions or side effects; caller logic and hardware documentation must supply that knowledge.

## Dependencies And Integration Points

This generated mask chunk must match `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`, which provides the corresponding register offsets and base-index selectors. A mismatch between the offset and mask files can compile but write the wrong bits in the wrong register.

Direct include sites for this DCN314 mask header in the tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`, which builds DMUB service register tables for DCN 3.1.4.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c`, which maps DCN314 hardware interrupt registers and fields into DAL IRQ sources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`, which constructs the DCN314 resource pool and hardware register/field tables.

The OTG and GSL fields integrate with timing-generator code under `display/dc/optc`, especially `dcn314_optc.h` and the inherited DCN timing-generator functions. `GSL_SOURCE_SELECT` is exposed in DCN314 OPTC register definitions and is used by shared timing-generator sequencing for global sync lock source routing. ODM memory-power fields integrate with hwseq/resource code through `ODM_MEM_PWR_CTRL3` register definitions and `HWS_SF` field mappings. The DC perfmon fields integrate with the broader DC perfmon infrastructure that programs event selectors and counter state through generated register tables.

The chunk is source-tree-aligned with generated ASIC register metadata, not with Ceph. It should be merged with adjacent chunks for complete file-level claims because it begins mid-register in OTG1 and ends mid-register in the perfmon15 block.

## Risks And Edge Cases

- Shift/mask drift is the primary risk. These are raw constants, so a wrong bit position or mask can compile cleanly while corrupting unrelated hardware fields.
- Chunk boundaries are partial. The range starts after earlier `OTG1_OTG_TRIGA_CNTL` fields and stops after only `DC_PERFMON15_PERFMON_CNTL__PERFMON_STATE__SHIFT`; final per-file analysis must reconcile neighboring chunks.
- OTG instances are highly repetitive. Copy or generator errors can affect only one timing generator, producing failures limited to one pipe, connector, or multi-display topology.
- Many fields are sequencing-sensitive. Update locks, double-buffer pending flags, vstartup/vupdate/vready events, vertical interrupts, DRR timing updates, and clear/ack fields can race with scanout if updated outside the intended blanking or lock window.
- Interrupt and status fields are side-effect-prone. Blind read-modify-write can accidentally clear sticky events or acknowledge interrupts if the field access type is not respected.
- DRR and vtotal fields affect visible timing. Incorrect min/max/mid vtotal, trigger windows, or vtotal-reach masks can cause VRR/FreeSync instability, frame pacing issues, flicker, or stuck timing updates.
- CRC and pixel-readback fields are test-critical but easy to misconfigure. Wrong CRC window, selection, interlace/stereo mode, or one-shot pending handling can make display validation report false failures.
- GSL/global update lock fields coordinate multiple pipes. Incorrect source selection, timing windows, or master mode can break synchronized flips, ODM/MPC multi-pipe updates, or stereo/interlaced update ordering.
- ODM memory power control can affect power and stability. Incorrect force/disable/vblank power fields may leave memory blocks powered unnecessarily or power them down while still needed.
- Perfmon fields pack many control bits in one register. Incorrect event selection, counter select, interrupt enable, or stop/run mode can produce misleading counters or interrupt storms.

## Test Signals

Useful validation signals are a mix of generated-header consistency checks and hardware/display behavior:

- Build AMDGPU display, DCN314 resource, IRQ, OPTC, hwseq, and DMUB paths that include `dcn_3_1_4_sh_mask.h`; missing or renamed macros should fail in register table construction.
- Mechanically verify that every complete field in lines 32148-34607 has a consistent shift/mask pair, accounting for the intentional partial `OTG1_OTG_TRIGA_CNTL` and `DC_PERFMON15_PERFMON_CNTL` boundaries.
- Diff this range against AMD's authoritative DCN 3.1.4 register database and neighboring DCN generated headers where field layouts are expected to match.
- Exercise DCN314 modesets across one, two, and three active OTGs, including enable/disable, blank/unblank, hotplug, suspend/resume, link retraining, and display clock changes.
- Validate scanout timing through mode programming that stresses horizontal/vertical totals, sync polarity, interlace, stereo, DSC start position, and horizontal timing divider behavior.
- Test synchronized updates: atomic flips, cursor updates, multi-plane updates, ODM or multi-pipe configurations, global update lock, GSL source selection, and vupdate keepout windows.
- Exercise DRR/VRR paths and watch for vtotal-min, DRR timing update, and vtotal-reach interrupts, plus visible flicker, frame pacing errors, or stuck pending update bits.
- Use debug CRC and pixel-readback paths to confirm CRC window selection, one-shot/continuous CRC behavior, stereo/interlace CRC modes, and CRC data readout.
- Check IRQ handling for vertical interrupts, snapshot interrupts, trigger interrupts, force-count-now, force-vsync-next-line, vstartup/vupdate/vready events, and perfmon count-off/per-counter interrupts.
- Monitor power-management behavior around ODM memory power controls and OPTC display-clock gating with runtime PM, blanked displays, idle optimization, and resume.
- Use DC perfmon tooling or debug hooks to confirm event selection, counter active state, interrupt status/ack, and count-off behavior on DC perfmon15.

## Cross-Chunk Notes

Previous chunks own the beginning of the DCN314 OPTC/OTG metadata and the earlier part of `OTG1_OTG_TRIGA_CNTL`. Later chunks own the remainder of the DC perfmon15 block after `DC_PERFMON15_PERFMON_CNTL__PERFMON_STATE__SHIFT`. The final per-file research document should merge those boundaries before making complete claims about all DCN314 OTG, OPTC misc, and perfmon register fields.

### subset-b-001847: lines 34608-36980

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 34608-36980

## Purpose

This chunk is generated AMD DCN 3.1.4 register field metadata. It contains C preprocessor constants for hardware register field shifts and masks; it has no executable C logic, no declarations with storage, and no local data structures.

The requested range covers 2,373 lines with 2,179 `#define` entries: 1,089 `__SHIFT` macros and 1,090 `_MASK` macros. It starts inside the `DC_PERFMON15_PERFMON_CNTL` field block, completes the tail of perfmon15, covers the DIO display-output I2C/DDC block, DIO misc/link/power/clock registers, HPD0 through HPD4 hot-plug-detect blocks, a complete `DC_PERFMON16` block, complete DP AUX0 through DP AUX2 blocks, and ends partway through DP AUX3 at `DP_AUX3_AUX_LS_DATA`.

Although the source tree path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU display-driver hardware metadata copied into the tree. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, typedefs, includes, variables, locks, or allocation paths in this range. The interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for the named hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field.

These constants are consumed with the matching DCN 3.1.4 offset header and AMD display register helpers such as `FD_SHIFT`, `FD_MASK`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and DMUB register-table macros. A shift/mask macro is only meaningful when paired with the correct MMIO register address from `dcn_3_1_4_offset.h`.

Major register families in this slice:

- `DC_PERFMON15_*` tail and `DC_PERFMON16_*`: display-controller performance monitor control, counter selection/state, report counts, clock enable, counter-off interrupt controls, counter-value low/high fields, and per-counter interrupt status/ack bits.
- `DC_I2C_*`: software I2C control, arbitration between software/hardware/DMCU access, interrupt status/ack/mask for SW and DDC hardware engines, SW transfer status/error bits, DDC1 through DDC5 hardware status, DDC speed/setup timing, transaction descriptors 0 through 3, data FIFO access, EDID detect control, and read-request interrupt controls.
- `DIO_SCRATCH0` through `DIO_SCRATCH7`: 32-bit scratch registers with full-width payload masks.
- `DIO_*` misc controls: DP ALPM wakeup interrupt status, memory power status/control, DIO clock enables and gating/disconnect bits, power-management idle status, HDMI RX status timer, generic interrupt message/clear fields, and per-link `DIO_LINKA_CNTL` through `DIO_LINKF_CNTL`.
- `DIG_SOFT_RESET`: per-DIG soft reset bits for DIGA through DIGF plus AUX, HPD, and I2C reset controls.
- `HPD0_*` through `HPD4_*`: hot-plug interrupt status, interrupt enable/ack/mask/polarity/timer, HPD line state/enable/connection timer, fast-train delay/select, and toggle-filter timing fields.
- `DP_AUX0_*`, `DP_AUX1_*`, and `DP_AUX2_*`: AUX enable/reset/control, SW transaction control, arbitration, SW/LS/GTC-sync interrupts, detailed SW and link-service status/error fields, SW/LS data windows, DPHY TX/RX controls and status, GTC sync control/error/status, and AUX PHY wake controls.
- `DP_AUX3_*` partial block: AUX3 control, SW control, arbitration, interrupt control, SW status, LS status, and SW/LS data fields. Its DPHY/GTC/PHY-wake registers continue after this chunk.

Representative field names show the semantics exposed by the generated constants: `DC_I2C_GO`, `DC_I2C_TRANSACTION_COUNT`, `DC_I2C_SW_USE_I2C_REG_REQ`, `DC_I2C_DMCU_DONE_USING_I2C_REG`, `DC_I2C_SW_TIMEOUT`, `DC_I2C_SW_STOPPED_ON_NACK`, `DC_I2C_DDC<n>_EDID_DETECT_STATE`, `DIO_MEM_PWR_DIS`, `DIO_MEM_PWR_STATE`, `DISPCLK_G_R_DIO_GATE_DIS`, `DIG<n>_RESET`, `DC_HPD_INT_ACK`, `DC_HPD_SENSE`, `AUX_SW_GO`, `AUX_REG_RW_CNTL_STATUS`, `AUX_SW_RX_TIMEOUT`, `AUX_LS_CP_IRQ`, `AUX_GTC_SYNC_LOCK_DONE_INT`, and `DP_AUX_PHY_WAKE_ACK`.

## Control Flow

This header does not contain runtime control flow. Runtime sequencing is supplied by AMDGPU display and DMUB code:

1. DCN 3.1.4 code includes the offset header and this shift/mask header.
2. Register helper macros paste register and field names into generated tokens such as `DP_AUX1_AUX_SW_STATUS__AUX_SW_RX_TIMEOUT_MASK`.
3. Drivers or firmware-service setup code use the offset and field metadata to compose read/modify/write operations, poll hardware status, acknowledge interrupts, and build firmware-visible register tables.
4. Display link, hotplug, AUX, DDC/I2C, clock/power, reset, and perfmon code provide the real ordering around those MMIO accesses.

The macros do not encode any sequencing constraints. Consumers must still perform protocol-specific ordering, such as requesting I2C/AUX register ownership before starting a software transaction, clearing or acknowledging sticky interrupt bits in the hardware-defined way, waiting for AUX reset completion, respecting HPD debounce/filter timing, and restoring DIO clocks/power before touching blocks that may be gated.

## State And Persistence Behavior

The chunk stores no software state and persists nothing. It describes fields in hardware registers whose persistence and side effects are defined by DCN 3.1.4 hardware.

The represented hardware state includes:

- Performance monitor state: counter mode, selected event/state sources, current counter values, report-count thresholds, interrupt status and acks, clock enable, and run-enable start/stop selectors.
- I2C/DDC state: active transaction count, selected DDC line, arbitration ownership, abort signals, software transfer status and errors, DDC hardware request/done/urgent status, EDID-detect state, speed/setup timing, transaction opcodes/stop/start flags, FIFO data/indexing, and read-request interrupts.
- DIO misc state: scratch payloads, link-power and memory-power status, DIO clock-gating controls, soft-reset bits, generic interrupt payload/clear values, HDMI timer programming, and link training override/disable bits for links A through F.
- HPD state: sensed connector level, interrupt routing and acknowledgement, connect/disconnect timer values, HPD enablement, and fast-training/toggle-filter controls.
- DP AUX state: software and link-service transfer control, request/done status, protocol error reporting, reply byte count, arbitration state, DPHY calibration/status, GTC sync status, CP IRQ indication, and AUX PHY wake handshakes.

Many of these fields are likely volatile or side-effect-sensitive: interrupt ack bits may be write-one-to-clear or self-clearing, status bits may be sticky until acknowledged, reset/go/abort bits may trigger hardware state machines, and data-window index fields may auto-increment. This generated mask header does not identify access permissions or side effects, so consumers must rely on the hardware specification and surrounding driver patterns.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.1.4 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`, which supplies the corresponding register offsets and base-index selectors.
- DCN 3.1.4 display register-access helpers in AMDGPU display code, including field helper macros that map symbolic register/field names to `_MASK` and `__SHIFT` constants.
- DMUB service code for DCN 3.1.4. The neighboring offset research identifies `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c` as an include/integration point for the offset and shift/mask headers.
- Display connector management code paths that program DDC/I2C and DP AUX engines for EDID/DPCD access, HPD interrupt handling, link training, DisplayPort sideband activity, power management, and diagnostics.

The line range is source-tree-aligned to `dcn_3_1_4_sh_mask.h` but is not a semantic file boundary. It begins after the first `DC_PERFMON15_PERFMON_CNTL` field and ends before the DP AUX3 DPHY/GTC/PHY-wake field families, so final per-file analysis must reconcile neighboring chunks before presenting complete per-block coverage.

## Risks And Edge Cases

- Shift/mask drift is the main correctness risk. These macros are untyped constants, so an incorrect generated value can compile cleanly while corrupting unrelated MMIO bits.
- Protocol engines are side-effect-heavy. Blind read/modify/write on I2C, AUX, HPD, reset, or interrupt registers can lose status, retrigger interrupts, abort in-flight transfers, or start hardware transactions unexpectedly.
- I2C and AUX arbitration fields represent shared ownership among software, hardware engines, and DMCU/DMUB paths. Incorrect ownership sequencing can deadlock register access or race firmware/hardware transfers.
- DDC/EDID and DP AUX errors are user-visible as missing displays, failed EDID reads, broken DPCD access, bad link training, MST instability, or intermittent hotplug behavior.
- HPD timing and polarity fields are connector-sensitive. Wrong masks can produce interrupt storms, missed plug/unplug events, or fast-training behavior on the wrong HPD instance.
- Clock, memory-power, and reset fields can make otherwise valid register programming fail if a block is gated or held in reset. The mask header does not state which blocks require ungating first.
- Repeated DP AUX0/1/2 layouts invite copy/paste or generator skew. A per-instance mismatch might affect only one connector path, making failures hardware-port-specific.
- The chunk contains partial boundaries for perfmon15 and AUX3. Any automated check that expects complete register families in this file slice must account for the preceding and following chunks.

## Test Signals

Useful validation combines generated-header checks with hardware and driver behavior:

- Build AMDGPU display and DMUB code paths that include `dcn_3_1_4_sh_mask.h`; renamed, missing, or malformed macros should fail where register tables or field helpers reference them.
- Mechanically verify that complete field groups in lines 34608-36980 have consistent `__SHIFT`/`_MASK` pairs, with explicit exceptions for the chunk boundaries at `DC_PERFMON15_PERFMON_CNTL` and `DP_AUX3_AUX_LS_DATA`.
- Diff this range against AMD's authoritative DCN 3.1.4 register database and nearby generated DCN headers where DIO, HPD, I2C, AUX, and perfmon layouts should match.
- Exercise DDC/I2C EDID reads across all exposed connectors, including NACK, timeout, unplug, suspend/resume, and repeated hotplug cases.
- Exercise DP AUX and link-training flows on AUX0 through AUX3-capable hardware: DPCD reads/writes, HPD disconnect during AUX, CP IRQ/link-service status, MST sideband access, and AUX timeout/overflow paths.
- Validate HPD0 through HPD4 interrupt behavior by plugging/unplugging displays and checking that the expected connector reports events without interrupt storms or missed disconnects.
- Test power-management and reset paths through display suspend/resume, runtime power transitions, and modesets while watching for stuck DIO memory power state, gated-clock access failures, or blocks left in reset.
- Use perfmon/debug paths, where available, to confirm counter reads, counter-off interrupts, and current-value high/low fields behave consistently.

## Cross-Chunk Notes

The previous chunk owns the start of the `DC_PERFMON15` field family, including earlier `DC_PERFMON15_PERFCOUNTER_*` definitions and the first `DC_PERFMON15_PERFMON_CNTL__PERFMON_STATE__SHIFT` line. The next chunk should continue from `DP_AUX3_AUX_DPHY_TX_REF_CONTROL` and cover the remainder of AUX3 plus later register blocks. The merge lane should combine these chunks before making complete claims about all DIO, HPD, perfmon, or AUX instances in `dcn_3_1_4_sh_mask.h`.

### subset-b-001848: lines 36981-39374

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 36981-39374

## Purpose

This chunk is generated AMD DCN 3.1.4 register field metadata. It contains no executable C logic; it publishes C preprocessor constants for field shifts and bit masks used by AMDGPU display code to address MMIO register fields on DCN 3.1.4 hardware.

The requested range covers 2,394 source lines and 2,171 `#define` entries: 1,096 `__SHIFT` constants and 1,075 `_MASK` constants. The apparent mismatch is caused by the artificial chunk boundary: the range ends inside `VPG1_VPG_GSP_FRAME_UPDATE_CTRL` after 21 shift definitions, while that register's remaining masks continue after line 39374. Aside from that expected boundary effect, the complete registers in this slice have paired shift and mask definitions.

Although the path sits under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, or exported runtime symbols in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same hardware field.

These constants are meaningful only with the matching offset header, especially `dcn_3_1_4_offset.h`, and with AMD display register helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

Major register families in this chunk:

- `DP_AUX3_*` tail fields: AUX3 DPHY TX/RX timing, AUX GTC synchronization, GTC error/status reporting, and AUX PHY wake controls.
- Complete `DP_AUX4_*` block: AUX4 enable/reset, HPD selection, low-speed read, software AUX transaction control, arbitration between software and DMCU-style users, AUX done/error interrupts, software and low-speed transaction status/data windows, DPHY TX/RX tuning/status, GTC sync control/status, and AUX PHY wake handshaking.
- `VPG0_*`: video packet generator generic packet indexed data, generic secondary packet frame/immediate update controls, conflict/status bits, memory power controls, ISRC data, and MPEG packet info.
- `AFMT0_*`: audio formatter and HDMI/DP audio packet fields, including VBI audio packet placement, audio layout/channel enable, DP audio stream ID, HBR and 60958 overrides, audio infoframe payload fields, IEC 60958 channel-status bytes, audio CRC generation/results, test ramp controls, FIFO overflow/audio-enable status, audio packet send/update controls, audio source selection, and AFMT memory power controls.
- `DME0_*`: display metadata engine enablement, HUBP requestor ID, stream type, double-buffer pending/taken state, missed-transmission status/clear bits, and memory low-power controls.
- `DIG0_*`: digital front-end/back-end source selection, stereo and bypass routing, Dolby Vision enable/missed metadata status, output CRC, clock/test/random patterns, FIFO reset/calibration/error state, HDMI metadata packets, HDMI core control/status, ACR packets and CTS/N values, generic packet controls, HDMI double-buffering, TMDS control pattern generation, data balancing, sync characters, and DIG version/force-disable bits.
- `DP0_*`: DisplayPort link, pixel format, main-stream attributes, video stream enable/status, steering FIFO/TU overflow, DPHY training/symbol/scrambler/CRC/PRBS/FEC controls, fast training, secondary-data packet controls, audio timestamp/N/M fields, multi-stream transport MSE slot/rate controls, MSO controls, DSC control, secondary metadata transmission, ALPM controls, generic secondary packet 8-11 controls, generic packet enable double-buffer status, and AUX-less ALPM wake/sleep interrupt controls.
- Beginning of `VPG1_*`: generic packet access/data plus the start of `VPG1_VPG_GSP_FRAME_UPDATE_CTRL`, ending before the register's mask definitions complete.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display and DMUB code:

1. DCN 3.1.4-specific code includes `dcn_3_1_4_offset.h` and `dcn_3_1_4_sh_mask.h`.
2. Register table or direct register-access macros paste register and field names into tokens such as `DP_AUX4_AUX_CONTROL__AUX_EN_MASK` or `DIG0_HDMI_CONTROL__HDMI_DATA_SCRAMBLE_EN__SHIFT`.
3. Helper macros such as `FD_MASK` and `FD_SHIFT` populate field tables or construct read-modify-write operations.
4. Higher-level display code performs the actual ordering: AUX transactions for DPCD/I2C-over-AUX, HDMI/DP audio setup, generic packet scheduling, metadata double-buffer updates, DisplayPort link training and stream enablement, MST/MSO/DSC programming, ALPM transitions, interrupt acknowledgements, and suspend/resume restoration.

The generated masks do not encode ordering or access permissions. For example, the same chunk describes one-shot control bits, sticky status bits, clear/ack bits, read-only status, programmable timing fields, and double-buffer handshakes. Consumers must know the required sequence from hardware documentation and driver logic.

## State And Persistence Behavior

This chunk stores no software state and persists nothing in memory or on disk. It describes fields in hardware registers whose values are owned by the display engine.

Hardware state represented by these fields includes:

- AUX channel state: enable/reset state, HPD association, software transaction queues, low-speed read windows, DPHY timing, GTC sync lock/error state, transaction reply/error status, CP IRQ/update flags, and PHY wake request/ack state.
- Packet-generation state: generic packet payload bytes, frame/immediate update requests and pending flags, ISRC/MPEG info payloads, packet lock/conflict status, and VPG memory power state.
- Audio formatter state: audio channel layout, enabled channels, DP stream ID, HBR and IEC 60958 controls, audio infoframe payloads, channel-status overrides, CRC/test generation, FIFO overflow, audio enable-change status, source selection, and AFMT memory power state.
- Metadata state: DME enablement, requestor routing, double-buffer pending/taken state, missed metadata transmission status, and DME memory power state.
- HDMI/TMDS state: scrambling, deep color, AVMUTE status, ACR generation, generic packet send/line/update controls, HDMI double-buffer locks, CTS/N values, audio/video metadata packet state, TMDS sync/control patterns, DC-balance controls, and DIG enable/clock status.
- DisplayPort state: link status, lane count, pixel encoding/depth, MSA fields, stream enable/status, steering FIFO and TU overflow, DPHY training/test/scrambler/CRC/FEC controls, secondary-data packet timing, MST allocation, MSO, DSC, secondary metadata, ALPM/AUX-less ALPM, generic secondary packet scheduling, and wake/sleep interrupt state.

Persistence is hardware-defined. Configuration fields generally retain values until modeset, link reprogramming, power gating, suspend/resume, or ASIC reset. Status, pending, interrupt, ack, clear, force, and done bits may be volatile, sticky, self-clearing, or write-one-to-clear depending on the register. This mask header does not say which fields have side effects.

## Dependencies And Integration Points

The masks in this chunk must match the generated DCN 3.1.4 offset database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h`

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`, which includes the offset and mask headers and expands DCN register/field tables through `DMUB_DCN31_REGS()`, `DMUB_DCN31_FIELDS()`, `FD_MASK`, and `FD_SHIFT`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c`, which includes the same generated headers and uses token-pasted register/mask names for interrupt register descriptors.

Broader integration is with AMDGPU display code that programs the DIG, DP, HDMI, AFMT, VPG, DME, and AUX blocks. The generated constants are coupled to same-generation register lists and to repeated-instance naming conventions (`DIG0`, `DP0`, `VPG0`, `VPG1`, `DP_AUX4`, etc.). A field-name drift or wrong bit position can compile successfully if a token still exists, but it can cause hardware misprogramming at runtime.

## Risks And Edge Cases

- Shift/mask drift is the central risk. These are untyped integer constants, so an incorrect mask can silently corrupt neighboring hardware fields.
- The chunk boundary is partial at both the file-context level and the ending register level. It starts in the tail of the `DP_AUX3` address block and ends inside `VPG1_VPG_GSP_FRAME_UPDATE_CTRL`; final file-level analysis must merge adjacent chunks before making complete block-level claims.
- AUX register fields include arbitration, queued transaction, timeout, overflow, HPD disconnect, low-speed update, CP IRQ, GTC sync, and PHY wake bits. Blind read-modify-write or wrong ack handling can hang AUX transactions, lose HPD/CPIRQ signals, or break DPCD/I2C-over-AUX communication.
- HDMI/AFMT fields include audio packet send controls, ACR generation, HBR/layout overrides, FIFO overflow acknowledgements, channel-status updates, and infoframe payload fields. Mistakes can produce missing HDMI/DP audio, wrong channel maps, audio dropouts, bad CTS/N timing, or stuck audio interrupts.
- Generic packet and metadata fields rely on frame/immediate update and double-buffer pending/taken handshakes. Misprogramming can miss HDR/Dolby Vision/AVI/audio/vendor packets or update them on the wrong frame.
- DP0 fields cover link training, FEC, scrambler, MSA, stream enable, MST allocation, DSC, MSO, secondary packets, and ALPM. Errors can be mode-specific and appear only with MST, DSC, FEC, high bit rates, panel replay/low-power modes, or AUX-less ALPM.
- Several fields are replicated patterns, such as generic packet 0-14 updates and DP GSP 8-11 controls. Copy-generation errors may affect one packet slot while the rest work, making failures hard to localize.
- Memory power fields for VPG, AFMT, and DME must be coordinated with active use. Forcing low-power state at the wrong time can cause dropped packets or stale status.

## Test Signals

Useful validation combines generated-header consistency with hardware behavior:

- Build DCN 3.1.4 AMDGPU display and DMUB code. Missing or renamed macros should fail at `dmub_dcn314.c`, IRQ descriptor construction, register tables, or direct register-access compile sites.
- Mechanically verify that complete registers in lines 36981-39374 have matching `__SHIFT` and `_MASK` definitions. The known exception is `VPG1_VPG_GSP_FRAME_UPDATE_CTRL`, whose mask definitions continue after this chunk.
- Diff this slice against AMD's authoritative DCN 3.1.4 register database and neighboring DCN mask headers where repeated blocks are expected to remain layout-compatible.
- Exercise DisplayPort AUX reads/writes, I2C-over-AUX EDID reads, DPCD link-status reads, HPD/HPD-RX handling, CP IRQ handling, and suspend/resume on hardware using DCN 3.1.4 paths.
- Validate HDMI and DisplayPort audio across hotplug, modeset, sample-rate changes, HBR, stereo, multichannel, and receiver capability changes; watch for audio FIFO overflow, bad channel status, and missing audio devices.
- Validate generic packets and metadata: AVI/audio/vendor infoframes, HDR/Dolby Vision metadata, ISRC/MPEG packets, frame-update versus immediate-update behavior, and double-buffer pending/taken transitions.
- Exercise DP link modes that stress this slice: link training, FEC on/off, DSC, MST allocation, MSO/eDP panel modes, stream enable/disable interrupts, fast training, CRC/PRBS diagnostics, and ALPM/AUX-less ALPM wake/sleep paths.
- Monitor kernel logs, display artifacts, audio diagnostics, and connector-specific failures for stuck interrupts, AUX timeouts, packet deadline misses, metadata transmission missed flags, steering/TU overflows, link-training failures, or behavior limited to one DIG/DP/AUX instance.

## Cross-Chunk Notes

Earlier chunks own the beginning of the `DP_AUX3` block, including its control/software/arbitration/status/data registers before `DP_AUX3_AUX_DPHY_TX_REF_CONTROL`. Later chunks continue `VPG1_VPG_GSP_FRAME_UPDATE_CTRL` with the remaining mask definitions and then the rest of the DIG1 VPG block. The final per-file document should reconcile those boundaries before summarizing complete address blocks for `dcn_3_1_4_sh_mask.h`.

### subset-b-001849: lines 39375-41781

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 39375-41781

## Scope And Purpose

This chunk is a generated AMD DCN 3.1.4 register shift/mask header slice. It contains only preprocessor constants and generated grouping comments: `__SHIFT` macros define bit positions, `_MASK` macros define raw 32-bit field masks, and `// addressBlock:` comments delimit display I/O hardware register blocks. There are no functions, structs, enums, executable statements, allocations, locks, or software-owned storage in this range.

The purpose of the slice is to expose the field layout ABI used by AMDGPU Display Core and DMUB-facing DCN 3.1.4 code when programming digital display output hardware. The companion `dcn_3_1_4_offset.h` header supplies register addresses and base indices; this file supplies the bit packing for those registers. Runtime code consumes these symbols through AMD display register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `SF`, `SRI`, `SE_SF`, and related generated register-list macros.

The range starts mid-register in the `VPG1_VPG_GSP_FRAME_UPDATE_CTRL` field list, continues through VPG1, AFMT1, DME1, DIG1, and DP1 display-output blocks, then covers VPG2, AFMT2, DME2, and the beginning of DIG2. It ends in the middle of `DIG2_HDMI_GENERIC_PACKET_CONTROL0`, so the following DIG2 HDMI generic packet masks are outside this assigned chunk. The slice contains 2,169 `#define` lines: 1,090 shift definitions and 1,079 mask definitions.

This file lives under a local `ceph-client` source mirror, but the content is AMDGPU Display Core register metadata, not Ceph filesystem logic.

## Register Blocks Covered

The tail of `dce_dc_dio_dig1_vpg_vpg_dispdec` covers VPG1 packet update and payload fields:

- Generic secondary packet frame-update and immediate-update control for generic packets 0 through 14, with corresponding pending bits.
- `VPG_GENERIC_STATUS` lock/conflict reporting and conflict clear.
- VPG memory light-sleep controls and memory power state.
- ISRC1/2 indexed data access, MPEG infoframe payload bytes, and MPEG info update fields.

The `dce_dc_dio_dig1_afmt_afmt_dispdec` block covers AFMT1 audio-format and audio-packet state:

- VBI packet controls for ACP and HDMI audio packet scheduling.
- Audio packet layout override, layout select, channel enable mask, DP audio stream ID, HBR override, and IEC 60958 override.
- Audio infoframe payload fields such as checksum, channel count, coding type, checksum offset, extension type, channel allocation, level shift, downmix inhibit, and LFE playback level.
- IEC 60958 channel-status fields across `AFMT_60958_0`, `AFMT_60958_1`, and `AFMT_60958_2`.
- Audio CRC enable/source/channel/count and CRC result/done readback.
- Audio ramp/test controls, AFMT status, audio sample send/update controls, infoframe update, interrupt status, audio source select, and AFMT memory power force/disable/state.

The `dce_dc_dio_dig1_dme_dme_dispdec` block defines DME1 controls for DME enable, stream/MTN mode, dummy stream generation, DME AUX select and connection state, plus DME memory power force/disable/state.

The `dce_dc_dio_dig1_dispdec` block covers DIG1 front-end/back-end and HDMI/TMDS control:

- DIG front-end/back-end enable, source select, CRC controls/results, clock/test/random pattern controls, FIFO controls/status, DB control, version, and force-disable fields.
- HDMI metadata packet scheduling, HDMI control/status, audio delay, ACR packet control and N/CTS values for 32 kHz, 44.1 kHz, and 48 kHz families, ACR status readback, VBI packets, audio/MPEG infoframe controls, generic packet controls 0 through 14, generic immediate send/pending bits, and HDMI GC fields.
- TMDS controls for clock pattern selection, control characters, feedback, stereosync control, sync character patterns, control bits, DC balancer controls, and CTL generation.

The `dce_dc_dio_dp1_dispdec` block is the largest part of the chunk. It covers DP1 link and stream control:

- Link control, pixel format, MSA colorimetry/misc fields, DP configuration, video stream enable/mode/blanking controls, steer FIFO, video M/N timing, link framing, VBID/MSA placement, and video stream-disable interrupt fields.
- DPHY control for FEC, scrambler selection, bypass/skew behavior, training-pattern selection, symbol patterns, 8b/10b state, PRBS generation, scrambler controls, DPHY CRC, MST CRC phase status, fast training, and HBR2 pattern support.
- Secondary-data-packet controls for audio stream packets, timestamps, audio copy management, GSP0 through GSP11, ISRC, MPEG packets, generic packet priorities, line references, send/pending/active/deadline status, and SDP framing widths.
- DP audio N/M and readback registers, ASP packet coding/version/channel override, and audio mute/collision state.
- MST/MSE rate, slot allocation table, slot-allocation update, link timing, status readbacks, and misc blank/timestamp/zero-encoder fields.
- DPIA spare, MSA timing parameters, MSO controls, DSC enable/slice/pixel-clock controls, SEC control extensions, DB control, MSA VBID misc, metadata transmission, ALPM controls, GSP8 through GSP11 controls, GSP enable double-buffer pending status, and AUX-less ALPM timing/wakeup/FEC/interrupt controls.

The `dce_dc_dio_dig2_vpg_vpg_dispdec`, `dce_dc_dio_dig2_afmt_afmt_dispdec`, and `dce_dc_dio_dig2_dme_dme_dispdec` blocks repeat the same VPG, AFMT, and DME surfaces for instance 2. The final `dce_dc_dio_dig2_dispdec` section starts DIG2 and runs through shifts for HDMI generic packet control 0.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit in a 32-bit register.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted field mask in the register word.
- Instance prefixes such as `VPG1`, `AFMT1`, `DME1`, `DIG1`, `DP1`, `VPG2`, `AFMT2`, `DME2`, and `DIG2` are part of the ABI and select the generated hardware instance.
- Generated comments such as `// addressBlock: dce_dc_dio_dp1_dispdec` and `//DP1_DP_SEC_CNTL` are not compiled, but they are important for source-tree-aligned reconciliation because they describe hardware grouping and partial chunk boundaries.

Important field families include:

- Generic packet data and scheduling: `VPG_GENERIC_PACKET_ACCESS_CTRL`, `VPG_GENERIC_PACKET_DATA`, `VPG_GSP_FRAME_UPDATE_CTRL`, `VPG_GSP_IMMEDIATE_UPDATE_CTRL`, HDMI `GENERIC_PACKET_CONTROL*`, DP `DP_SEC_GSP*`, and DP metadata transmission controls.
- Audio formatting and packetization: AFMT channel enable/layout, stream ID, HBR override, IEC 60958 channel status, audio infoframe fields, audio CRC, ramp/test controls, HDMI ACR and DP audio M/N fields.
- Link and PHY control: DP pixel/MSA/config/stream fields, DPHY FEC/scrambler/training/pattern/CRC/PRBS fields, TMDS control characters and DC balancing, HDMI scrambling/deep-color/error fields.
- MST/MSO/DSC and bandwidth allocation: DP MSE rate, slot allocation tables/status, MSO mode/format/pixel mode, DSC enable/slice/pixel-clock fields, and MSA timing parameters.
- Power and status: VPG/AFMT/DME memory power fields, FIFO reset/error/calibration fields, HDMI and DP interrupt/ack/clear/status fields, fast-training and ALPM status, and GSP double-buffer pending status.

The primary include site found in this tree for this exact generated header pair is `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`, which includes both `dcn/dcn_3_1_4_offset.h` and `dcn/dcn_3_1_4_sh_mask.h`. Shared DCN31 display code also defines the consumer shapes for these register families, for example `display/dc/dcn31/dcn31_afmt.h` maps AFMT fields through `AFMT_DCN31_REG_LIST(id)` and `DCN31_AFMT_MASK_SH_LIST(mask_sh)`.

## Control Flow

This chunk has no direct runtime control flow. Its effective flow is compile-time symbol binding followed by runtime register access in other code:

1. A DCN 3.1.4 consumer includes the generated offset and shift/mask headers.
2. Register-list macros bind instance-specific register addresses from `dcn_3_1_4_offset.h` with field shifts and masks from this header.
3. Runtime display, link, audio, HDMI, DP, DMUB, or diagnostic code calls register helpers that combine a register address with the relevant shift/mask pair.
4. Hardware latches, reports, clears, or consumes the resulting MMIO field according to the register's hardware semantics.

The declaration order mirrors the hardware register database. Within most register groups, all `__SHIFT` definitions precede the corresponding `_MASK` definitions. Instance 2 VPG/AFMT/DME definitions intentionally repeat the instance 1 shape with a different prefix. The DP1 block is ordered from stream/link controls through DPHY, secondary packet, MST/MSO/DSC, metadata, and ALPM controls.

The assigned lines have two partial boundaries. The first lines are the end of `VPG1_VPG_GSP_FRAME_UPDATE_CTRL`, with the earlier generic0 through generic5 pending shifts in the previous chunk. The final lines stop after `DIG2_HDMI_GENERIC_PACKET_CONTROL0` shifts, before its masks and later DIG2 HDMI controls.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes hardware register state in the DCN 3.1.4 display I/O subsystem.

Writable state represented by these fields includes packet payload bytes, frame/immediate send requests, audio infoframes, IEC 60958 channel status, audio source and channel layout, audio ACR/N/M values, HDMI scrambling/deep color, TMDS patterns, DP video stream enablement, DPHY training/test controls, FEC and scrambler controls, MST slot allocation, DSC enablement, MSO format/mode, ALPM timing and wake/FEC scheduling, FIFO reset/configuration, and memory power force/disable controls.

Readback or status state includes pending packet updates, generic-packet lock/conflict state, memory power state, CRC results and valid bits, FIFO reset-done/error/calibration, HDMI active AVMUTE and packet errors, DPHY CRC and MST phase status, fast-training state and completion, secondary-packet collision/mute status, MSE slot-allocation status, GSP send pending/active/deadline status, double-buffer pending flags, ALPM current state and wake interrupt state, and DME AUX connection state.

Persistence is hardware-defined. Programmed control fields usually remain until rewritten, reset, power-gated, or reinitialized during display modeset, suspend/resume, hot-plug, link retraining, or firmware-assisted sequences. Status, pending, interrupt, and ACK/clear fields are volatile and may be edge-sensitive or write-one-to-clear. This header does not encode access type, reset values, volatility, clear-on-read behavior, sequencing requirements, or read-only/write-only constraints.

## Dependencies And Integration Points

The critical dependency is the matching generated offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h` supplies register addresses and base indices. Examples in the companion file include `regAFMT1_AFMT_AUDIO_PACKET_CONTROL2` at `0x2175`, `regDP1_DP_LINK_CNTL` at `0x2208`, `regVPG2_VPG_GENERIC_PACKET_ACCESS_CTRL` at `0x2268`, and `regDIG2_HDMI_GENERIC_PACKET_CONTROL0` at `0x229b`, all with base index `2`.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c` includes this header pair for DCN 3.1.4 DMUB register access.
- `drivers/gpu/drm/amd/display/dc/dcn31/dcn31_afmt.h` defines the AFMT register-list and field-list shape used by DCN31-family AFMT/audio code. The AFMT1/AFMT2 macros in this chunk must match that consumer shape.
- DCN link, HDMI, DP, audio, and diagnostic code under `drivers/gpu/drm/amd/display/dc` consumes this kind of generated metadata through shared register helper conventions rather than by manually spelling numeric masks.

Integration is mostly by token concatenation. A missing or renamed generated macro generally fails compilation when a register-list macro expands. A wrong numeric mask or shift is more dangerous because it can compile cleanly and then write or read the wrong hardware bits.

## Risks And Edge Cases

- The chunk starts in the middle of `VPG1_VPG_GSP_FRAME_UPDATE_CTRL`; merge/reconciliation must combine it with the previous chunk before presenting VPG1 frame-update control as complete.
- The chunk ends in the middle of `DIG2_HDMI_GENERIC_PACKET_CONTROL0`; the mask definitions for that register and the rest of DIG2 HDMI/DIG/DP2 surfaces belong to later chunks.
- The register families are highly repetitive across instances. Prefix drift such as using `AFMT1` where `AFMT2` is intended, or `DIG1` where `DIG2` is intended, can target the wrong display output instance.
- Many fields are packed into adjacent single-bit controls. Generic packet controls, DP GSP controls, FIFO controls, interrupt ACK/mask bits, and ALPM wake/FEC controls are vulnerable to read-modify-write mistakes that preserve the wrong neighbor bits.
- Several masks use the high bit, for example `0x80000000L` in generic packet update-lock disable, ALPM sleep state, and other fields. Consumers should treat register values as unsigned 32-bit quantities to avoid signedness surprises.
- Status and ACK/clear fields share the same generated macro style as ordinary configuration fields. Examples include HDMI error ACK, DP stream-disable ACK, DPHY MST phase error ACK, fast-training complete ACK, ALPM interrupt clear, and packet collision ACK. Generic write helpers must respect side effects.
- Packet timing fields are line/frame sensitive. Wrong line references, any-line settings, priorities, or pending-bit handling can cause missed generic packets, stale HDR/metadata packets, or packet collisions without a direct software error.
- DP link controls are sequencing-sensitive. FEC, scrambler, training pattern, PRBS, fast training, MSE slot allocation, DSC, MSO, and ALPM fields interact with link training, DPCD state, sink capabilities, and stream timing.
- Memory power controls for VPG, AFMT, and DME can invalidate dependent packet/audio/DME programming if forced or disabled while the corresponding block is active.
- Cross-generation reuse is risky. DCN 3.1.4 names resemble DCN 3.1.2 and other DCN headers, but the offset and sh/mask headers must be paired by the same ASIC generation.

## Test Signals

Useful validation is mostly build-time, generated-header consistency, and hardware integration:

- Build AMDGPU display/DMUB code with DCN 3.1.4 support enabled to catch missing generated macro names in `dmub_dcn314.c` and shared DCN31-family register-list consumers.
- Preprocess representative `REG_SET`, `REG_UPDATE`, `REG_GET`, `SF`, `SRI`, and `SE_SF` users to confirm token concatenation resolves to the intended `VPG1`, `AFMT1`, `DME1`, `DIG1`, `DP1`, `VPG2`, `AFMT2`, `DME2`, and `DIG2` symbols.
- Compare this chunk against `dcn_3_1_4_offset.h` and the authoritative AMD register database to verify every covered register selector has the expected shift/mask layout.
- Run static generated-header checks for paired shift/mask definitions, 32-bit mask fit, expected non-overlap within each register, and intentional partial-boundary exceptions at the start and end of this slice.
- Exercise HDMI audio on DCN 3.1.4 hardware: channel layout, IEC 60958 values, HBR override, ACR/N/CTS programming, audio infoframe updates, AVMUTE, deep color, scrambling, and VBI/generic packet scheduling.
- Exercise DisplayPort link training, FEC, DPHY CRC, PRBS/test patterns, fast training, MST slot allocation, DSC/MSO paths, secondary-data packets, metadata transmission, and AUX-less ALPM transitions.
- Verify hot-plug, modeset, suspend/resume, link retrain, audio enable/disable, metadata update, and display reset paths while watching for stale pending bits, missed packets, packet collisions, FIFO errors, and memory-power state mismatches.

## Open Cross-Chunk Questions

- Whole-file reconciliation should join this with adjacent chunks before describing complete VPG1 frame-update or DIG2 HDMI generic-packet coverage.
- Whole-file research should map how DCN 3.1.4 resource construction instantiates the DIO/DIG/DP/AFMT/VPG blocks and whether every generated instance is exposed on every product.
- Whole-file research should compare DCN 3.1.4 DIO field layouts with DCN 3.1.2 to distinguish intended carry-over from ASIC-specific additions such as AUX-less ALPM, MSO, DSC, and extended GSP controls.

### subset-b-001850: lines 41782-44191

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 41782-44191

## Purpose

This chunk is generated AMD DCN 3.1.4 display register field metadata. It contains preprocessor constants for bit positions (`__SHIFT`) and field masks (`_MASK`) inside memory-mapped display-controller registers. The matching `dcn_3_1_4_offset.h` header supplies register addresses; this header supplies the bit layout that AMD display register helpers use to update individual fields.

The requested range is a middle slice of the DIO display output area. It starts inside the DIG2 HDMI generic-packet field definitions, completes the remainder of the DIG2 HDMI/TMDS tail, covers a full DP2 stream/link packet block, covers VPG3, AFMT3, DME3, and a full DIG3 HDMI/TMDS stream-encoder block, then enters the DP3 block and stops inside `DP3_DP_DPHY_SYM0`. There are no functions, structs, branches, loops, local includes, or direct runtime side effects in this range.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata rather than distributed filesystem code.

## Register Blocks Covered

The DIG2 tail begins with `DIG2_HDMI_GENERIC_PACKET_CONTROL0` masks for generic packet slots 0 through 7, then defines slots 8 through 14 in `DIG2_HDMI_GENERIC_PACKET_CONTROL6` and immediate-send/pending fields for slots 0 through 14 in `DIG2_HDMI_GENERIC_PACKET_CONTROL5`. The DIG2 range also includes HDMI general control (`HDMI_GC`), generic-packet line-number controls, data-buffer disable controls, HDMI audio clock regeneration fields for 32/44.1/48 kHz families, AFMT bridge control, DIG back-end lane and enable controls, TMDS control characters, stereosync selection, sync-character patterns, DC balancer controls, TMDS control-bit generation, DIG version, and forced DIG disable.

The full `dce_dc_dio_dp2_dispdec` block describes DP2 DisplayPort stream fields. It includes link status and embedded-panel mode, pixel encoding/component depth and one/two-pixel processing mode, MSA colorimetry and misc bytes, lane-count configuration, video stream enable/status/defer, steer FIFO reset and overflow reporting, video `M/N` timing generation, link framing, HBR2 eye pattern enable, MSA/VBID placement, video-stream-disable interrupt controls, DPHY FEC/scrambler/bypass/test/training fields, symbol pattern and PRBS controls, DPHY CRC controls/results/status, fast training controls/status, DP secondary-data packet controls, audio `M/N` fields, MST/MSE rate and stream allocation table fields, DPHY byte-swap and pattern controls, MSA timing parameters, MSO fields, DSC enable, extended SEC control registers, data-buffer controls, MSA/VBID misc overrides, metadata transmission, ALPM and AUX-less ALPM controls, and generic stream packet controls/status for GSP8 through GSP11.

The VPG3 block defines video packet generator fields for generic packet access/data, generic stream packet frame-update and immediate-update controls, packet update/conflict status, memory power controls, ISRC access/data, and MPEG info registers. These fields are used to stage and trigger stream metadata packets.

The AFMT3 block defines audio formatter fields: VBI/audio packet controls, audio infoframe payload fields, IEC 60958 channel-status words, audio CRC controls/results, ramp controls, formatter status, main audio packet controls, infoframe control, interrupt status, audio source selection, and AFMT memory power. This is the stream audio and HDMI/DP packet formatting surface for stream instance 3.

The DME3 block defines display micro-engine control fields including stream/video enable, clock enable, data enable, request/ack status, and memory low-power controls.

The DIG3 block defines stream encoder front-end and back-end fields. It includes front-end clock/mode/reset/enable/status and link target fields, output CRC controls/results, clock/test/random patterns, FIFO control and calibration fields, HDMI metadata/control/status/audio/ACR/VBI/infoframe/generic-packet controls, AFMT bridge control, DIG back-end lane controls, TMDS packet/control-character/sync/DC-balancer fields, DIG version, and forced disable.

The DP3 block begins at `dce_dc_dio_dp3_dispdec` and is only partially present in this chunk. The visible fields cover link status, pixel format, MSA colorimetry and misc bytes, lane-count config, video stream control, steer FIFO and overflow controls, alternate DPHY scrambler reset, video timing and `M/N`, link framing, HBR2 eye pattern enable, MSA/VBID location, video disable interrupt controls, DPHY FEC/scrambler/bypass/test controls, training-pattern selection, and the first two masks in `DP3_DP_DPHY_SYM0`. The rest of DP3 continues in a later chunk.

## Important APIs, Types, And Macros

The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a field inside a 32-bit MMIO register.
- `<REGISTER>__<FIELD>_MASK` gives the field mask used to isolate or update that field.
- Comments such as `//DP2_DP_SEC_CNTL` and `// addressBlock: dce_dc_dio_dp2_dispdec` delimit generated register groups but are not compiled APIs.

The visible macro prefixes are `DIG2_`, `DP2_`, `VPG3_`, `AFMT3_`, `DME3_`, `DIG3_`, and partial `DP3_`. They map onto generic driver field names through token-pasting register-list macros in the AMD display stack. For example, stream-encoder code talks about fields such as `HDMI_GENERIC8_SEND`, `DP_VID_STREAM_ENABLE`, `DP_VID_N`, `DP_MSA_MISC0`, `AFMT_AUDIO_CLOCK_EN`, `TMDS_PIXEL_ENCODING`, and `DIG_FIFO_RESET`; resource construction binds those generic names to the instance-specific generated macros in this file.

The runtime objects that receive these shift/mask tables include `struct dcn10_stream_encoder_shift`, `struct dcn10_stream_encoder_mask`, `struct dcn31_vpg_shift`, `struct dcn31_vpg_mask`, `struct dcn31_afmt_shift`, and `struct dcn31_afmt_mask`. This chunk itself does not define those types; it supplies constants consumed by their initializers.

## Control Flow

This header has no control flow. Runtime sequencing is supplied by DCN 3.1.4 resource construction and DIO stream-encoder methods:

1. `dcn314_resource.c` includes `dcn_3_1_4_offset.h` and this shift/mask header.
2. Resource macros such as `SR`, `SRI`, and related token-pasting helpers bind offsets from the companion header to per-instance register tables.
3. Shift/mask initializers bind field constants from this header to stream encoder, VPG, AFMT, DSC, DWB, MPC, DCCG, AUX, and other DCN hardware objects.
4. Runtime code later calls register helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, and `REG_WAIT` to program HDMI, TMDS, DP, VPG, AFMT, DME, and packet fields through those tables.

The sequencing requirements are not encoded in the macros. Consumers must still order FIFO resets, clock enables, stream enable/disable, packet double-buffer updates, AFMT/VPG packet staging, DP link training, video `M/N` programming, DSC PPS packet programming, interrupt acknowledge/clear operations, memory power transitions, and suspend/resume restoration correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes MMIO-backed GPU display state. The represented hardware state includes:

- HDMI/TMDS stream encoder configuration, including generic packets, metadata packets, infoframes, audio clock regeneration, AVMUTE, TMDS symbols, lane enables, data-buffer controls, output CRC, test patterns, and FIFO controls.
- DisplayPort stream and link state for DP2 and partial DP3, including link status, pixel format, video stream enable/status, timing `M/N`, MSA/VBID fields, link framing, DPHY FEC/scrambler/training/test/CRC controls, secondary-data packet controls, MST allocation tables, MSO/DSC controls, ALPM, and AUX-less ALPM fields.
- Packet generator state in VPG3, including generic packet data windows, frame/immediate update triggers, conflict/status flags, ISRC/MPEG payloads, and memory power state.
- Audio formatter state in AFMT3, including audio infoframes, channel-status words, sample/audio clock enables, audio packet controls, CRC telemetry, ramp controls, and memory power state.
- DME3 control and memory low-power state.

Configuration fields generally persist until the driver reprograms them, the block is reset, display power/clock gating changes state, firmware changes the register, suspend/resume restores state, or the ASIC resets. Status, pending, interrupt, CRC, overflow, and readback fields are hardware-defined and may be read-only, sticky, write-one-to-clear, self-clearing, or timing-sensitive; this generated header does not distinguish those semantics.

## Dependencies And Integration Points

This chunk must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`. The offset header provides `reg...` register addresses and `_BASE_IDX` selectors; this file provides the matching field layouts. A generated-name mismatch can break compilation, while a wrong numeric shift or mask can compile and corrupt register updates at runtime.

Direct include sites in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`

The main functional integration point is `dcn314_resource.c`. It constructs VPG instances, AFMT instances, five stream encoders, AUX/I2C engines, link encoders, DSC, DWB, MPC, DCCG, and other DCN objects from generated offset and shift/mask tables. For this chunk, the most direct consumers are the VPG3, AFMT3, DIG2/DIG3 stream-encoder, DP2, and partial DP3 field tables.

Stream encoder behavior is implemented in `display/dc/dio/dcn314/dcn314_dio_stream_encoder.c` and inherited DCN10/DCN30 helper code. Those paths program fields represented here when setting HDMI/DVI stream attributes, enabling HDMI scrambling and infoframes, sending generic packets, setting AVMUTE, blanking/unblanking DP, programming DP video `M/N`, resetting/enabling DIG FIFO state, updating DP secondary-data packets, reading encoder state, and configuring DSC-related DP secondary packet behavior.

`irq_service_dcn314.c` uses the same generated headers for interrupt status/mask/ack field definitions. `dmub_dcn314.c` uses the generated register metadata for DMUB-facing register offsets and masks when display firmware services need DCN314 register access.

## Risks And Edge Cases

The highest risk is generated-header drift from the hardware specification or from the companion offset header. These macros are untyped constants; an incorrect mask or shift can compile cleanly while modifying the wrong bits in a stream encoder, packet generator, audio formatter, DP link, or interrupt/status register.

The chunk has artificial boundaries. It starts after the `DIG2_HDMI_GENERIC_PACKET_CONTROL0` shift definitions and ends inside `DP3_DP_DPHY_SYM0`; adjacent chunk reports are required before the final per-file document can make complete claims about all DIG2 or DP3 fields.

Repeated instance families are copy-sensitive. DP2 and DP3, DIG2 and DIG3, and the VPG/AFMT/DME instance naming scheme are structurally similar but not interchangeable. A field error may only reproduce on a specific connector, stream encoder, MST route, or multi-display topology.

Packet-update fields are timing-sensitive. VPG/AFMT generic packet update, HDMI generic immediate send, DP secondary-data packet sends, pending bits, conflict flags, and line-number fields interact with vertical blanking and double-buffered update timing. Wrong masks can cause stale metadata, missing infoframes, repeated packets, or update conflicts without a simple kernel crash.

DP link and video-stream fields are mode-sensitive. `DP_VID_STREAM_ENABLE`, `DP_VID_STREAM_STATUS`, `DP_VID_M/N`, MSA timing, DPHY FEC/scrambler/training controls, and MST allocation fields must match link training, timing, lane count, link rate, DSC, and MSO configuration. Errors often appear as blank displays, intermittent link training failures, corrupted MST payloads, or failures only at high bandwidth.

FIFO, data-buffer, CRC, and overflow fields are diagnostic and stateful. Incorrect reset/ack/mask handling can hide underflow/overflow problems or produce misleading CRC/test-pattern results. `DP_STEER_FIFO`, `DIG_FIFO_CTRL*`, and DB disable controls are especially sensitive around stream enable/disable and mode changes.

Memory-power fields in VPG3, AFMT3, and DME3 are power-management sensitive. Forcing light sleep or disabling memory while a stream, audio path, or packet generator is active can produce failures around hotplug, blanking, suspend/resume, or rapid modesets.

## Test Signals

Build-time validation should compile AMDGPU display support with DCN314 enabled. High-signal failures are missing or renamed generated macros referenced by `dcn314_resource.c`, `irq_service_dcn314.c`, `dmub_dcn314.c`, `dcn314_dio_stream_encoder.c`, `dcn10_stream_encoder.h`, `dcn31_vpg.h`, and `dcn31_afmt.h`.

Mechanical checks should verify that every field in this range has the expected paired `__SHIFT` and `_MASK` definitions except where the chunk boundary intentionally includes only a tail or head of a register group. Cross-checking against AMD's generated DCN 3.1.4 register database is the strongest regression signal because the file is generated metadata.

Runtime stream tests should cover DP and HDMI outputs that map to DIG2/DIG3 and DP2/DP3 where the ASIC routing allows it. Useful signals include successful modesets, link training, stream blank/unblank, FIFO reset/enable completion, no unexpected `DP_VID_STREAM_STATUS` stalls, no steer/TU overflow flags, and stable display across link-rate and lane-count changes.

Packet and audio validation should cover HDMI infoframes, generic packets 0 through 14, HDMI metadata packets, AVMUTE, ACR programming/readback, DP secondary-data packets, VPG generic packets, ISRC/MPEG metadata, AFMT audio sample/clock enable, IEC 60958 channel status, and audio playback over HDMI/DP.

DP advanced-feature validation should exercise MST/MSE allocation updates, DSC PPS secondary packets, MSO controls, DPHY FEC and scrambler settings, HBR2 test pattern paths, DPHY CRC capture, ALPM, AUX-less ALPM, and suspend/resume on DP2 and DP3 paths.

Diagnostic checks should inspect kernel logs and display traces for AUX/DP link failures, hotplug storms, audio dropouts, infoframe mismatch, CRC mismatch, FIFO underflow/overflow, stuck packet pending bits, stuck interrupt status, and resume failures.

## Cross-Chunk Notes

Previous chunks own the beginning of the DIG2 HDMI generic-packet register group, including shift definitions that precede the visible `DIG2_HDMI_GENERIC_PACKET_CONTROL0` masks. Later chunks continue the DP3 register block after `DP3_DP_DPHY_SYM0`. The final per-file research document should merge adjacent chunk reports before claiming complete coverage of the full `dcn_3_1_4_sh_mask.h` DIO, VPG, AFMT, DME, DIG, or DP field namespace.

### subset-b-001851: lines 44192-46599

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 44192-46599

## Scope And Purpose

This chunk is part of AMD's generated DCN 3.1.4 ASIC register shift/mask header. It contains C preprocessor constants for hardware bitfields: `<REGISTER>__<FIELD>__SHIFT` gives the bit position and `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask. The companion `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h` supplies the matching `reg*` register addresses and base indices.

The range starts in the middle of the DisplayPort 3 PHY-symbol block, covers the rest of the `DP3` stream/security/audio/metadata sideband fields, then covers the `VPG4`, `AFMT4`, `DME4`, and `DIG4` blocks. It ends in the `DP4` block after `DP4_DP_ALPM_CNTL`; the following chunk continues with later DP4 fields. There are no functions, structs, branches, or direct side effects in this source. The runtime behavior comes from AMD display code that binds these generated masks and shifts into register tables and uses `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_READ`, and `REG_WAIT` helpers.

## Register Blocks Covered

The `DP3` tail covers DisplayPort PHY and stream-side control for the fourth DIO stream encoder instance:

- PHY symbol/test controls: `DP_DPHY_SYM1`, `DP_DPHY_SYM2`, 8b/10b reset/disparity controls, PRBS generation, scrambler control, CRC enable/control/result, MST CRC phase status, HBR2 patterns, byte/stream swap controls, and fast-training request/status.
- Secondary-data-packet controls: `DP_SEC_CNTL`, `DP_SEC_CNTL1` through `DP_SEC_CNTL7`, `DP_GSP8_CNTL` through `DP_GSP11_CNTL`, GSP double-buffer enable status, and metadata transmission fields.
- Audio and timing payload fields: DP audio M/N read/write registers, timestamp mode/count, packet control, MSE rate and allocation table fields, MSA timing parameters, VBID/misc override fields, MSO controls, DSC mode selection, and DP double-buffer control.
- Link power and low-power fields: `DP_ALPM_CNTL` and `DP_AUXLESS_ALPM_CNTL1` through `DP_AUXLESS_ALPM_CNTL5` for main-link sleep/standby, AUX-less ALPM enable/status/CRC/mask/timeout/ignore controls, and FEC/PHY sleep sequence state.

The `VPG4` block is the video packet generator for the same DIO instance. It defines indexed generic-packet data access, frame-update and immediate-update bits for generic packets 0 through 14, lock/conflict status and clear fields, GSP memory power state, ISRC 1/2 indexed data, and MPEG info packet bytes.

The `AFMT4` block is the audio format/infoframe block. It defines VBI and audio packet controls, audio channel/layout/sample-send fields, audio infoframe payload bytes, IEC 60958 channel-status packing for channels 0 through 7, CRC controls/results, ramp-generator controls, AFMT status and interrupts, audio source select, and AFMT memory-power fields.

The `DME4` block exposes metadata engine enable, HUBP requestor, stream type, MSI routing, and memory power state for dynamic metadata packet handling.

The `DIG4` block covers the front-end digital stream encoder and HDMI/TMDS path. It includes DIG source selection, FE enable, DVI/HDMI/DP output selection, stereosync, Dolby Vision enable, symclk FE status, output CRC controls/results, clock/test/random patterns, FIFO controls, HDMI metadata packet controls, HDMI core control/status, HDMI audio/ACR/VBI/infoframe/generic packet controls, deep color and scrambling controls, guard-band/general-control packet fields, ACR programmed and readback values for 32/44.1/48 kHz families, AFMT clock enable, BE controls, TMDS character/pattern/control/DC-balancer fields, DIG version, and force-disable fields.

The `DP4` section begins a full repeated DisplayPort stream block for the fifth DIO instance. In this chunk it covers link control, pixel format, colorimetry, config, video stream enable/status, FIFO steering, MSA misc/timing, DPHY internal/PHY/training/CRC/fast-training controls, DP secondary packet controls, audio M/N/timestamp, MSE SAT/rate fields, MSO, DSC, GSP controls, double-buffer controls, metadata packet transmission, and `DP_ALPM_CNTL`.

## Important APIs, Types, And Macros

This chunk's API is entirely generated macro metadata. The major naming families are `DP3_DP_*`, `VPG4_VPG_*`, `AFMT4_AFMT_*`, `DME4_DME_*`, `DIG4_*`, and `DP4_DP_*`. Each family must match the corresponding address macros in `dcn_3_1_4_offset.h`, such as `regDP3_DP_SEC_CNTL`, `regVPG4_VPG_GENERIC_PACKET_ACCESS_CTRL`, `regAFMT4_AFMT_AUDIO_PACKET_CONTROL`, `regDME4_DME_CONTROL`, `regDIG4_HDMI_CONTROL`, and `regDP4_DP_LINK_CNTL`.

The primary consumers are the DCN 3.1.4 display resource and DIO stream encoder paths:

- `display/dc/resource/dcn314/dcn314_resource.c` includes `dcn_3_1_4_offset.h` and `dcn_3_1_4_sh_mask.h`, builds stream encoder, VPG, AFMT, and DME register tables, and maps VPG/AFMT/DME blocks to DIO engine instances.
- `display/dc/dio/dcn314/dcn314_dio_stream_encoder.h` defines `SE_DCN314_REG_LIST(id)` and `SE_COMMON_MASK_SH_LIST_DCN314(mask_sh)`. Those macros bind fields such as `DP_SEC_STREAM_ENABLE`, `DP_SEC_GSP*`, `DP_MSA_TIMING_PARAM*`, `DP_DSC_MODE`, `DP_SEC_METADATA_PACKET_*`, `HDMI_GENERIC*`, `HDMI_ACR_*`, `DME_CONTROL`, `DIG_FIFO_*`, and `DIG_CLOCK_PATTERN` to the generated symbols in this header.
- `display/dc/dio/dcn314/dcn314_dio_stream_encoder.c` uses the bound tables to program DP/HDMI enable sequences, FIFO reset/enable, HDMI/DVI setup, secondary packet state readback, metadata packet controls, and audio/timing fields.
- `display/dc/dcn31/dcn31_vpg.h` and `display/dc/dcn31/dcn31_vpg.c` consume VPG masks for generic-packet data, frame/immediate updates, conflict clearing, and VPG memory power.
- `display/dc/dcn31/dcn31_afmt.h` and `display/dc/dcn31/dcn31_afmt.c` consume AFMT masks for audio channel status, audio info updates, audio source selection, sample sending, and AFMT memory power.
- `display/dmub/src/dmub_dcn314.c` and `display/dc/irq/dcn314/irq_service_dcn314.c` include the same generated DCN 3.1.4 headers for firmware-facing register access and interrupt tables, although this specific chunk is most directly tied to DIO stream encoder, VPG, AFMT, DME, and DP/HDMI packet programming.

## Control Flow And State Behavior

The header itself has no control flow. Runtime state is MMIO hardware state inside the DCN 3.1.4 display controller. Configuration fields remain programmed until the driver, firmware, reset logic, or power-management transitions change them. Status and telemetry fields are live or sticky hardware observations.

Typical DP stream programming uses this metadata to set pixel format, MSA timing, video M/N, stream enable, FIFO steering, and DP secondary-packet controls. `DP_SEC_CNTL` and the GSP control registers gate video stream SDPs, audio stream packets, audio timestamp packets, adaptive-sync/metadata packets, MPEG packets, and generic sideband packets. `DP_SEC_CNTL2` through `DP_SEC_CNTL7` provide send, pending, deadline-missed, any-line, line-number, double-buffer-disable, active, and in-idle state for the extended generic sideband slots.

MSA, MSE, MSO, and DSC fields are timing-sensitive. MSA timing parameters must match the active stream. MSE SAT and rate registers describe MST allocation timing and update-pending state. MSO controls split a stream across multiple output segments. `DP_DSC_CNTL.DP_DSC_MODE` gates compressed-stream behavior. Misordered or mismatched programming can leave an enabled stream with wrong timing, missing secondary packets, failed MST scheduling, or bad DSC/MSO behavior.

VPG state is indexed and update-driven. Packet payload bytes are written through `VPG_GENERIC_PACKET_ACCESS_CTRL` and `VPG_GENERIC_PACKET_DATA`; frame-update and immediate-update bits decide when packet payloads become active. Conflict/status bits are sticky diagnostic surfaces that must be cleared with the matching clear field. VPG memory power controls affect whether generic packet storage is available.

AFMT state is packet and audio-channel metadata state. Audio infoframe fields, IEC 60958 channel-status fields, audio source selection, audio sample-send, mute/validity flags, ramp controls, CRC, and AFMT memory power persist in AFMT registers. Audio programming must coordinate with HDMI/DP packet enables so that N/CTS, channel status, audio infoframes, and audio sample transmission align with the active transport.

DIG4 and HDMI/TMDS fields are the front-end and HDMI packet state for one DIG instance. HDMI generic packet controls have continuation/send/line fields for packet slots 0 through 14. ACR controls and programmed N/CTS values are stateful audio-clock recovery surfaces. FIFO reset/enable fields are actively polled in the DCN314 stream encoder; `DIG_FIFO_RESET_DONE`, `DIG_FIFO_ENABLE`, `DIG_SYMCLK_FE_ON`, and output pixel mode determine whether the stream encoder can safely feed the link.

Low-power fields (`DP_ALPM_CNTL`, AUX-less ALPM, AFMT/VPG/DME memory-power registers) interact with link training, panel self refresh, idle behavior, and suspend/resume. They are persistent control state mixed with pending/status readback, so tests need to distinguish command bits from status bits.

## Dependencies And Integration Points

The generated masks and shifts depend on AMD's DCN 3.1.4 register specification and must stay synchronized with `dcn_3_1_4_offset.h`. A mismatch can compile if names still line up but can silently program the wrong bits. The macro contract also depends on AMD display's register helper conventions: `SRI(...)` selects the instance-specific register address, while `SE_SF(...)` and related field-list macros select the instance-0 field names that are reused for all instances.

This chunk integrates with the DRM/KMS display pipeline through DCN314 resource construction. It directly supports DisplayPort and HDMI stream encoders, VPG packet generation, AFMT audio packet generation, DME metadata packets, MST MSE allocation programming, DSC/MSO stream mode, dynamic metadata transmission, HDMI infoframes/generic packets, DP SDPs, audio N/CTS and channel status, FIFO enable/reset, and link low-power entry/exit.

The `DP3`, `VPG4`, `AFMT4`, `DME4`, and `DIG4` groups are a coherent DIO instance. `DP4` starts the next repeated DP stream instance. The range boundaries are therefore partial: DP3 starts before this chunk, and DP4 continues after it. File-level reconciliation should combine neighboring chunk research before treating either repeated stream encoder instance as fully covered.

## Risks And Edge Cases

Generated field drift is the primary risk. Wrong masks or shifts in this range can break DP or HDMI modes without causing obvious software errors: wrong MSA timing, incorrect pixel format, missing secondary data packets, bad HDR/VRR metadata, bad HDMI generic packet scheduling, broken audio N/CTS/channel-status programming, FIFO stalls, or display link-training failures.

DP secondary-packet controls mix enable, send, pending, deadline-missed, double-buffer, active, and in-idle fields. Full-register writes or wrong masks can accidentally drop packet enables, miss sticky failure status, or schedule packets on the wrong line. This is especially sensitive for VSC, HDR static metadata, DSC PPS/GSP11, adaptive sync, and MST sideband scheduling.

The VPG and AFMT blocks use indexed data windows and update bits. A valid mask with a stale index, wrong update mode, or powered-down packet memory writes data to the wrong packet slot or leaves payload changes pending. Conflict and interrupt status bits must be explicitly cleared with their matching masks.

HDMI generic packet controls are dense and split across several registers. Slot 0-14 continuation/send/line fields are easy to cross-wire when generated names or field-list macros are changed. A bug may only show up with multiple concurrent infoframes or dynamic metadata, not with a basic HDMI display.

Audio fields are transport-sensitive. `AFMT_*`, `HDMI_ACR_*`, `DP_SEC_AUD_*`, and `DP_SEC_TIMESTAMP` must agree with the selected DP/HDMI mode, audio sample rate, channel layout, and deep-color/scrambling state. Bad values can produce silent audio, intermittent audio, or bad channel status while video remains stable.

Power and low-power fields can create mode-change-only failures. Forcing VPG/AFMT/DME memory power down, entering ALPM/AUX-less ALPM at the wrong time, or leaving pending sleep/standby state around link training can cause failures around hotplug, PSR, idle entry, suspend/resume, and fast link retraining.

## Test Signals

Build-time coverage should catch renamed or missing symbols in `dcn314_resource.c`, `dcn314_dio_stream_encoder.h`, `dcn31_vpg.h`, and `dcn31_afmt.h`. High-signal compile failures include missing `DP0_DP_SEC_*`, `DIG0_HDMI_*`, `VPG0_VPG_*`, `AFMT0_AFMT_*`, `DME0_DME_CONTROL`, or `DIG0_DIG_FIFO_CTRL0` fields used by DCN314 register-list macros.

Runtime DP validation should exercise DCN 3.1.4 DP connectors routed through the affected DIO instances, with modes that cover SST, MST where available, DSC, MSO, HDR metadata, adaptive sync/VRR metadata, audio, hotplug, link retraining, and suspend/resume. Useful signals include correct MSA timing readback, secondary-packet enable state, no stuck MSE rate update pending, no GSP deadline-missed status, stable DSC/MSO modes, and successful audio/video after low-power transitions.

Runtime HDMI validation should cover DVI/HDMI enable paths, deep color, scrambling, audio N/CTS for 32/44.1/48 kHz families, audio infoframes, general-control packets, generic packet slots, HDR metadata, Dolby Vision enable where applicable, FIFO reset/enable polling, and repeated modesets. Expected signals are stable video, correct infoframe/metadata capture on a protocol analyzer, working audio, and no FIFO reset timeout.

VPG/AFMT/DME validation should program generic packets through indexed data windows, switch frame versus immediate update, verify conflict clear behavior, toggle memory power around idle and resume, and confirm DME metadata packet enable/line programming. Register dumps are valuable because many failures are wrong-packet or wrong-line errors rather than kernel crashes.

Low-power validation should cover DP ALPM and AUX-less ALPM entry/exit around active video, PSR-like idle paths, fast retraining, HPD cycles, and suspend/resume. Status fields such as pending bits, PHY sleep/standby requests, AUX-less CRC/result/timeout/mask fields, and memory power state should transition coherently and not leave the stream encoder unable to re-enable video or packets.

### subset-b-001852: lines 46600-49100

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 46600-49100

## Purpose

This chunk is generated AMD DCN 3.1.4 register field metadata. It contains no executable C logic; it publishes preprocessor constants for MMIO register field shifts and bit masks used by AMDGPU display code when programming DCN 3.1.4 display links, GPIO/AUX/DDC pads, panel power sequencing, backlight PWM, and the first Display Stream Compression block.

The requested range covers 2,501 physical lines with 2,101 `#define` entries: 1,051 `__SHIFT` macros and 1,050 `_MASK` macros. It starts at the final two masks for `DP4_DP_ALPM_CNTL`, then covers `DP4` secondary-data packet and AUX-less ALPM fields, several DCIO/DCIO-chip address blocks, `UNIPHY1` through `UNIPHY4` reserved macro-control fields, `PWRSEQ0` and `PWRSEQ1` panel/backlight fields, and the beginning of `DSC0` through `DSCC0_DSCC_PPS_CONFIG13`. The line range ends inside `DSCC0_DSCC_PPS_CONFIG13`, so later chunk research must cover the rest of the DSC PPS/range and diagnostic fields.

Although the repository path is under a `ceph-client` source mirror, this header is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, or allocation paths in this chunk. The interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

These constants are consumed with the matching DCN 3.1.4 offset header and register helper macros. `drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c` includes `dcn/dcn_3_1_4_offset.h` and `dcn/dcn_3_1_4_sh_mask.h`, then builds mask/shift tables used by DCN 3.1.4 resource construction. For DSC specifically, `drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.h` uses `DSC_SF()` and `DSC_REG_LIST_SH_MASK_DCN20(mask_sh)` to paste names such as `DSCC0_DSCC_PPS_CONFIG1__BITS_PER_PIXEL_MASK` into typed field tables.

Major register families in this slice:

- `DP4_DP_GSP8_CNTL` through `DP4_DP_GSP11_CNTL`, `DP4_DP_GSP_EN_DB_STATUS`, and `DP4_DP_AUXLESS_ALPM_CNTL1` through `CNTL5`: DisplayPort instance 4 secondary generic-stream-packet controls, double-buffer pending status, main-link PHY sleep timing, AUX-less ALPM wake/FEC events, hardware-mode state, frame/line scheduling, and wakeup interrupt fields.
- `DC_GENERICA`, `DC_GENERICB`, `DCIO_CLOCK_CNTL`, `DC_REF_CLK_CNTL`, `UNIPHYA/B/C_LINK_CNTL`, `UNIPHY[A-E]_CHANNEL_XBAR_CNTL`, `DC_PINSTRAPS`, `INTERCEPT_STATE`, `DCIO_PATTERN_GEN_*`, GSL/genlock/swaplock pad controls, and `DCIO_SOFT_RESET`: display IO clocks, generic outputs, link-channel inversion/crossbar mapping, pinstrap observations, pattern generation, global sync/lock pad routing, and soft reset fields for UNIPHY/DSYNC/PWRSEQ blocks.
- `DC_GPIO_GENERIC_*`, `DC_GPIO_DDC1` through `DDC5`, `DC_GPIO_DDCVGA`, `DC_GPIO_GENLK`, `DC_GPIO_HPD`, `DC_GPIO_PWRSEQ*`, `PHY_AUX_CNTL`, `DC_GPIO_TX12_EN`, `DC_GPIO_AUX_CTRL_0` through `5`, `DC_GPIO_RXEN`, `DC_GPIO_PULLUPEN`, and `AUXI2C_PAD_ALL_PWR_OK`: GPIO mask/output/input/enable fields, DDC/AUX pad mode and receive state, hotplug detect mask/enable/output fields, pad strength, AUX level/control fields, and power-good state.
- `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED57`, repeated for `UNIPHY2`, `UNIPHY3`, and `UNIPHY4`: full-width reserved macro-control register definitions. Each reserved register exposes a single `UNIPHY_MACRO_CNTL_RESERVED` field with shift 0 and mask `0xFFFFFFFFL`.
- `PWRSEQ0_*` and `PWRSEQ1_*`: panel GPIO enables/drive controls, panel power-sequence control/state, power-up/down delays, reference dividers, backlight PWM control/period, group-1 register locking/double-buffer update state, frame-start update behavior, and spare fields.
- `DSC_TOP0_*`, `DSCCIF0_*`, and the first part of `DSCC0_*`: DSC top clock/debug controls, DSC input-interface underflow recovery/status, input pixel format and component depth, picture size, compressor slice topology, double-buffer update status, rate-buffer interrupt/status bits, and PPS fields from config 0 through the first `RC_BUF_THRESH4` mask in config 13.

## Control Flow

This header has no runtime control flow. Runtime sequencing is provided by the AMD display driver:

1. DCN 3.1.4 resource and hardware blocks include the generated offset and shift/mask headers.
2. Register-list macros paste instance, register, and field tokens into constants such as `DC_GPIO_AUX_CTRL_5__DDC_PAD3_I2CMODE_MASK`, `PWRSEQ0_BL_PWM_CNTL__BL_PWM_EN_MASK`, or `DSCC0_DSCC_PPS_CONFIG13__RC_BUF_THRESH4_MASK`.
3. `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, `FD_SHIFT`, `LE_SF`, `DSC_SF`, and related helper patterns use those constants to build MMIO writes or field tables.
4. Runtime display flows program these registers during link initialization, AUX/DDC transactions, hotplug handling, panel power-up/down, backlight updates, DP ALPM entry/exit, DSC PPS programming, and error/status polling.

The macros do not encode ordering. Consumers must still perform the hardware-specific sequence: hold or release soft resets at the right time, set pad modes before AUX/DDC activity, observe HPD and power-good state, lock or double-buffer backlight updates where required, program DSC PPS fields before enabling the compressor path, and clear or mask status/interrupt bits with correct access semantics.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on its own. It describes hardware register fields whose state is held by the display ASIC.

Hardware state represented by the fields includes DP4 secondary-packet scheduling, ALPM sleep/wakeup timing, link PHY sleep state, DCIO clock/test selections, UNIPHY channel polarity and source crossbar state, GPIO output/mask/input state, DDC/AUX pad modes and levels, HPD detect state, PWRSEQ and BLON/DIGON/VARY_BL panel GPIO state, panel power-sequencer state, PWM period/duty/update state, and DSC0 compressor/PPS/configuration/status state.

Persistence is hardware-defined. Configuration fields generally survive until modeset reprogramming, link/panel reset, display power-gating, suspend/resume, or ASIC reset. Status-like fields such as `*_PENDING`, `*_ACTIVE`, `*_OCCURRED`, `*_STATUS`, `*_STATE`, `*_RECV`, `FRAME_START_EVENT_RECOGNIZED`, and `AUXI2C_PAD_ALL_PWR_OK` may be read-only, sticky, self-clearing, or write-one-to-clear depending on the register specification. This generated header only gives bit positions; it does not describe access type or side effects.

## Dependencies And Integration Points

The constants in this range must match the generated DCN 3.1.4 register-offset file at `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`. They are also tied to DCN base-address definitions and register helper code included by `dcn314_resource.c`.

Important in-tree integration points include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`, which includes this header and constructs DCN 3.1.4 resource register tables. The file also locally supplies missing `DSCC0_DSCC_CONFIG0__ICH_RESET_AT_END_OF_LINE` shift/mask definitions, showing that generated DSC field coverage is supplemented in the resource layer.
- `drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.h`, whose `DSC_REG_LIST_DCN20(id)` and `DSC_REG_LIST_SH_MASK_DCN20(mask_sh)` consume the `DSC_TOP0`, `DSCCIF0`, and `DSCC0` fields in this chunk for DSC programming across DCN generations.
- Link-encoder helpers such as `dcn20_link_encoder.h` and `dcn21_link_encoder.h`, which expose `DCIO_SOFT_RESET` fields for UNIPHY reset control.
- GPIO/DDC/AUX helpers such as `display/dc/gpio/ddc_regs.h`, which reference `DC_GPIO_AUX_CTRL_*` and DDC pad fields through generated shift/mask names.
- Panel-control and hardware-sequencer layers, which use panel power-sequence and backlight PWM fields to coordinate embedded-panel power, brightness, and frame-start update behavior.

The chunk is boundary-sensitive. It starts after most of `DP4_DP_ALPM_CNTL` was defined in the previous chunk and ends before `DSCC0_DSCC_PPS_CONFIG13` is complete. Final file-level research should merge neighboring chunks before making complete claims about DP4 ALPM and DSC0 PPS coverage.

## Risks And Edge Cases

- Shift/mask drift is the primary risk. These are untyped macros, so a wrong bit position can compile successfully while corrupting adjacent hardware fields.
- Many fields are side-effect-sensitive. DP secondary-packet send bits, ALPM wakeup/FEC pending bits, HPD receive/status fields, AUX/DDC pad controls, panel power-sequencer target/override bits, PWM update locks, DSC interrupt/status bits, and DSC double-buffer pending bits may not tolerate generic read-modify-write patterns.
- Repeated generated families are copy-sensitive. `DP4_DP_GSP8` through `GSP11`, DDC1 through DDC5 plus DDCVGA, UNIPHY reserved blocks, and `PWRSEQ0`/`PWRSEQ1` are structurally similar; a single instance-prefix or mask-width error can break only one connector, panel, or PHY.
- GPIO and pad fields affect physical link behavior. Incorrect AUX/DDC pad mode, pull-up, receive-enable, TX12, or pad-strength programming can produce link-training failures, EDID/I2C failures, missing HPD, or intermittent hotplug.
- Panel power and backlight fields have user-visible and hardware-safety implications. Bad delay, polarity, override, or PWM lock/update fields can cause blank panels, flicker, incorrect brightness, or power sequencing outside panel requirements.
- DSC PPS fields are tightly coupled to `drm_dsc` parameters and link bandwidth calculations. Wrong picture/slice dimensions, bits-per-pixel/component, chunk size, rate-control model, offsets, or buffer thresholds can cause corrupted output only in modes that require DSC.
- Reserved UNIPHY macro-control registers expose full 32-bit masks. The header defines their layout but does not imply that arbitrary writes are safe; consumers should only touch reserved fields when backed by hardware programming guidance.

## Test Signals

Useful validation is a combination of generated-header consistency, build coverage, and hardware behavior:

- Build AMDGPU display paths for DCN 3.1.4 so includes of `dcn_3_1_4_sh_mask.h`, `dcn314_resource.c`, link encoder tables, GPIO/DDC helpers, panel-control code, and DSC register-table construction catch missing or renamed macros.
- Mechanically verify that every complete field in lines 46600-49100 has a matching `__SHIFT` and `_MASK` pair, accounting for the intentional boundary exceptions at the beginning `DP4_DP_ALPM_CNTL` masks and the ending partial `DSCC0_DSCC_PPS_CONFIG13`.
- Compare this generated chunk against AMD's authoritative DCN 3.1.4 register database and adjacent DCN generation headers where repeated layouts are expected to be identical.
- Exercise DP4 behavior on hardware: secondary-data packet send paths, MST/MSO-related packet controls, AUX-less ALPM sleep/wakeup, FEC wake scheduling, and deadline/pending status reporting.
- Test DDC/AUX and HPD across all represented pads/connectors: EDID reads, AUX transactions, hotplug/unplug, suspend/resume, MST topology changes, and failure recovery after transient HPD or AUX errors.
- Test embedded-panel sequencing and backlight: cold boot, modeset, blank/unblank, suspend/resume, brightness changes, frame-start synchronized PWM updates, and both PWRSEQ0/PWRSEQ1 paths where available.
- Validate DSC-required modes, especially high-resolution/high-refresh configurations, DSC enable/disable transitions, suspend/resume with DSC, and visual corruption or DSC underflow/overflow status.

## Cross-Chunk Notes

The previous chunk owns most of `DP4_DP_ALPM_CNTL`; this chunk only includes its final `DP_ML_PHY_SLEEP_PATTERN_NUM_MASK` and `DP_ML_PHY_SLEEP_STANDBY_LINE_NUM_MASK` lines before the `DP4_DP_GSP8_CNTL` block. The next chunk must continue `DSCC0_DSCC_PPS_CONFIG13` after `RC_BUF_THRESH4_MASK`, then cover the remaining DSC0 PPS threshold/range, memory-power, error, fullness, and debug fields. The final per-file document should reconcile those boundaries before summarizing full DP4 ALPM or DSC0 behavior.

### subset-b-001853: lines 49101-51572

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 49101-51572

## Scope

This chunk is a generated AMD DCN 3.1.4 shift/mask header segment. It contains preprocessor constants only: each register field is represented by a `...__SHIFT` macro and a matching `..._MASK` macro. The slice has 2,472 source lines and about 2,134 `#define` lines, with 16 generated address-block markers.

The chunk starts in the middle of the DSC0 DSCC PPS field definitions at `DSCC0_DSCC_PPS_CONFIG13`, covers the rest of DSC0 rate/PPS/status masks, complete DSC1, DSC2, and DSC3 mask families, DC perfmon blocks 17 through 21, and the first part of DWB0 writeback/color-processing masks. It ends in the middle of the DWB output-gamma RAMA region table: `DWB_OGAM_RAMA_REGION_26_27` begins immediately after the requested line range, so the DWB OGAM RAMA and RAMB field families continue in the next chunk.

## Purpose

The purpose of this header segment is to provide bitfield positions and masks for DCN 3.1.4 display-compression and display-writeback hardware registers. Driver code combines these constants with companion register-offset macros from `dcn_3_1_4_offset.h` and with AMDGPU register helper macros to perform read-modify-write operations without hard-coding numeric bit layouts.

This is data-like source rather than executable logic. Its correctness is still critical: an incorrect shift or mask can silently program the wrong hardware bits while all C code still compiles.

## Register Families And Important Macros

The DSC/DSCC portion defines masks for Display Stream Compression instances:

- `DSC_TOP1_DSC_TOP_CONTROL`, `DSC_TOP2_DSC_TOP_CONTROL`, and `DSC_TOP3_DSC_TOP_CONTROL` cover per-instance DSC clock enable and clock-gating control. Each instance also has `DSC_DEBUG_CONTROL` masks for debug enable and test-clock mux selection.
- `DSCCIF1_DSCCIF_CONFIG*`, `DSCCIF2_DSCCIF_CONFIG*`, and `DSCCIF3_DSCCIF_CONFIG*` describe the DSC compressor input interface: underflow recovery/status/interrupt enable, input pixel format, bits per component, YCbCr 4:2:0/4:2:2 mode, and slice-width-minus-one fields.
- `DSCC1_DSCC_CONFIG*`, `DSCC2_DSCC_CONFIG*`, and `DSCC3_DSCC_CONFIG*` cover compressor configuration such as ICH reset timing, slices per line, alternate ICH encoding, vertical slice count, and the DSCC rate-control buffer model size.
- `DSCC*_DSCC_STATUS` provides the double-buffer update-pending bit.
- `DSCC*_DSCC_INTERRUPT_CONTROL_STATUS` provides overflow/underflow status and interrupt-enable masks for four rate buffers and four rate-control buffer models.
- `DSCC*_DSCC_PPS_CONFIG0` through `PPS_CONFIG22` map the DSC picture parameter set into hardware fields: DSC version, PPS identifier, line buffer depth, bits per component/pixel, VBR/simple/native 4:2:2/4:2:0 modes, chunk size, picture and slice dimensions, initial transmit/decode delays, scale increment/decrement intervals, BPG offsets, initial/final offsets, flatness QP limits, RC model size, RC quantization limits, target offsets, RC buffer thresholds 0-13, and range table entries 0-14.
- `DSCC*_DSCC_MEM_POWER_CONTROL` defines low-power state, force/disable, observed power state, and native 4:2:2 memory power-control fields.
- `DSCC*_DSCC_R_Y/G_CB/B_CR_SQUARED_ERROR_*` and `DSCC*_DSCC_MAX_ABS_ERROR*` expose error/statistics readback fields for DSC quality or validation paths.
- `DSCC*_DSCC_RATE_BUFFER*_MAX_FULLNESS_LEVEL` and `DSCC*_DSCC_RATE_CONTROL_BUFFER*_MAX_FULLNESS_LEVEL` define fullness counters or maximum fullness observations for four compressor lanes/models.
- `DSCC*_DSCC_TEST_DEBUG_BUS_ROTATE` defines rotate selectors for four DSC debug buses.

The perfmon blocks are structurally repeated for DSC instances and DWB:

- `DC_PERFMON17_*`, `DC_PERFMON18_*`, `DC_PERFMON19_*`, and `DC_PERFMON20_*` sit after DSC0 through DSC3 respectively.
- `DC_PERFMON21_*` sits after the DWB0 top block.
- Each perfmon block defines counter-control fields, counter state, clock-enable and counter-enable control, event-selection masks, trigger/enable/status fields, current-value interrupt selection, and low/high counter readback masks.

The DWB0 top and color-processing portion defines masks for display writeback:

- `DWB_ENABLE_CLK_CTRL` and `DWB_MEM_PWR_CTRL` cover DWB top enable, clock gating, test-clock selection, and OGAM LUT memory power state.
- `FC_MODE_CTRL`, `FC_FLOW_CTRL`, `FC_WINDOW_START`, `FC_WINDOW_SIZE`, and `FC_SOURCE_SIZE` describe frame-capture enable/rate, crop window, stereo-eye selection, new-content status, first-pixel delay, and source/window dimensions.
- `DWB_UPDATE_CTRL` exposes update lock and pending state.
- `DWB_CRC_CTRL`, `DWB_CRC_MASK_R_G`, `DWB_CRC_MASK_B_A`, `DWB_CRC_VAL_R_G`, and `DWB_CRC_VAL_B_A` provide writeback CRC control, channel masks, and channel signature readbacks.
- `DWB_OUT_CTRL` defines output format, denorm, max, and min fields.
- `DWB_MMHUBBUB_BACKPRESSURE_CNT_*`, `DWB_HOST_READ_CONTROL`, `DWB_OVERFLOW_STATUS`, `DWB_OVERFLOW_COUNTER`, `DWB_SOFT_RESET`, and `DWB_DEBUG_CTRL` cover memory-hub backpressure, host-read throttling, overflow status/clearing/interrupt enable, overflow counters, soft reset, and debug selection.
- `DWB_HDR_MULT_COEF`, `DWB_GAMUT_REMAP_MODE`, `DWB_GAMUT_REMAP_COEF_FORMAT`, and `DWB_GAMUT_REMAPA/B_*` define HDR multiplier and A/B gamut-remap matrix fields.
- `DWB_OGAM_CONTROL`, `DWB_OGAM_LUT_INDEX`, `DWB_OGAM_LUT_DATA`, `DWB_OGAM_LUT_CONTROL`, and `DWB_OGAM_RAMA_*` define output-gamma LUT mode/select/current state, LUT index/data access, channel write/read controls, RAMA start/end/base/slope/offset fields, and RAMA region-pair LUT-offset/segment-count fields through region pair 24-25 in this chunk.

## Control Flow And Runtime Behavior

There is no direct C control flow in this header. Runtime behavior is through generated register tables and register access helpers. DCN314 resource code includes `dcn_3_1_4_offset.h` and `dcn_3_1_4_sh_mask.h`, then builds per-block tables whose fields are populated from these macros.

For DSC, `dcn314_resource.c` constructs `struct dcn20_dsc` instances with `dsc2_construct(...)`, passing `dsc_regs[inst]`, `dsc_shift`, and `dsc_mask`. The field list comes from `display/dc/dsc/dcn20/dcn20_dsc.h`, where `DSC_REG_LIST_SH_MASK_DCN20(__SHIFT)` and `DSC_REG_LIST_SH_MASK_DCN20(_MASK)` select fields such as `DSCC_PPS_CONFIG*`, rate-buffer overflow/underflow bits, error counters, memory power state, and debug-bus rotation.

For DWB, `dcn314_resource.c` includes `dcn30/dcn30_dwb.h`, builds `dwbc30_shift` and `dwbc30_mask` via `DWBC_COMMON_MASK_SH_LIST_DCN30(__SHIFT)` and `DWBC_COMMON_MASK_SH_LIST_DCN30(_MASK)`, then constructs `struct dcn30_dwbc` with `dcn30_dwbc_construct(...)`. DWB color-management code in `dcn30_dwb_cm.c` consumes these shifts/masks when programming OGAM/gamut-remap state and when mapping common gamma helper fields onto DWB-specific register fields.

The hardware flows represented by this chunk are:

- DSC enable/configuration, PPS programming, rate-control configuration, double-buffer update observation, error/statistics readback, rate-buffer fullness monitoring, underflow/overflow interrupt handling, and memory power control.
- Per-block perf counter selection, enablement, trigger/status handling, and counter readback for DSC and DWB diagnostics.
- DWB frame-capture setup, crop/source geometry, update locking, CRC generation, output format and denorm range programming, backpressure/overflow observation, soft reset, HDR/gamut remap, and output-gamma LUT/RAMA curve programming.

## State And Persistence

The macros themselves hold no state and allocate no storage. They describe persistent hardware bitfields. Values written through consumers persist in the DCN display hardware until a later register write, hardware reset, power-gating transition, suspend/resume restore, or full display reprogramming changes them.

Several represented fields have stateful behavior:

- DSC PPS and DSCC configuration fields are part of the active compression stream setup. Incorrect writes can affect the compressed stream immediately or at the next double-buffered update point.
- `DSCC_DOUBLE_BUFFER_REG_UPDATE_PENDING` is read as hardware state and is used to observe when pending DSC programming has taken effect.
- DSC interrupt/status fields can be latched by hardware for overflow and underflow conditions; clear/enable sequencing is handled by consumers outside this header.
- DSC rate-buffer and error/max-error fields are readback/statistical state maintained by hardware.
- DSC and DWB memory-power fields include requested and observed power states, so they interact with display power sequencing.
- DWB `DWB_UPDATE_LOCK` and `DWB_UPDATE_PENDING` coordinate when writeback register changes become visible to the hardware pipeline.
- DWB overflow, backpressure, CRC, and perfmon fields expose live or latched diagnostic state.
- DWB OGAM programming is index/data and bank/region based; consumers must select the intended mode, host path, channel, and region before writing LUT or piecewise-linear curve parameters.

## Dependencies And Integration Points

This chunk depends on the rest of the generated DCN 3.1.4 register set:

- `dcn_3_1_4_offset.h` supplies the companion MMIO register offsets used with these field masks.
- `display/dc/dsc/dcn20/dcn20_dsc.h` defines the common DSC register, shift, and mask table layout consumed by DCN314 DSC construction.
- `display/dc/resource/dcn314/dcn314_resource.c` includes this generated header and binds DCN314 resources to `dsc_shift`, `dsc_mask`, `dwbc30_shift`, and `dwbc30_mask`.
- `display/dc/dwb/dcn30/dcn30_dwb.h` defines DWB register/field table macros and `struct dcn30_dwbc_shift` / `struct dcn30_dwbc_mask`.
- `display/dc/dwb/dcn30/dcn30_dwb_cm.c` uses the DWB OGAM and gamut-remap masks to program writeback color management.
- Higher-level DSC paths use DRM DSC types from `drm/display/drm_dsc.h` and AMD DSCC types from `display/dc/dsc/dscc_types.h`; those semantic values are packed into hardware fields described by this header.

The generated macro names form a compile-time API. Renaming or deleting a field macro breaks the table initializers. Changing a numeric shift or mask can compile cleanly but corrupt runtime register programming.

## Risks And Edge Cases

- Generated-header drift is the main risk. A single wrong mask width or shift can mispack DSC PPS data, interrupt enables, memory power controls, DWB crop/output fields, or OGAM/gamut-remap coefficients.
- The chunk begins and ends on partial logical blocks. DSC0 `PPS_CONFIG13` starts before line 49101, and DWB OGAM RAMA continues after line 51572. The merge lane must not treat either family as complete based only on this chunk.
- Instance parity matters for DSC1, DSC2, and DSC3. The masks are structurally repeated; an instance-specific generation error can affect only one compressor and may appear only on displays using that DSC engine.
- Some fields are status or latch bits, not plain configuration bits. Consumers need the correct clear/read/enable order for DSCC overflow/underflow, DWB overflow, CRC, and perfmon state.
- DSC PPS fields have tight bit-width expectations from the DSC specification and DRM DSC structures. Truncation or signedness mistakes in caller code can be hidden by a valid-looking mask.
- DWB OGAM LUT and RAMA fields are only part of the complete curve programming surface in this chunk. Region pairs 26-27 through 32-33 and RAMB fields continue later, so documentation and validation must join adjacent chunks.
- Power-control fields combine force, disable, requested low-power state, and observed state. Programming them outside the intended DCN314 power sequencing can leave DSC or DWB memory unavailable during active use.

## Test Signals

Useful validation signals are mostly build-time, generation-time, and hardware/display regression signals:

- Build AMDGPU DCN314 display code to catch missing or renamed `DSCC*`, `DC_PERFMON*`, and `DWB*` shift/mask macros.
- Compare `dcn_3_1_4_sh_mask.h` against `dcn_3_1_4_offset.h` and the register-list macros so every field referenced by `DSC_REG_LIST_SH_MASK_DCN20` and `DWBC_COMMON_MASK_SH_LIST_DCN30` exists with the expected name.
- Run generated-header parity checks across DSC1/DSC2/DSC3 field families and across perfmon17/18/19/20 blocks where the layout is expected to repeat.
- Exercise DSC enable/disable modes, native 4:2:2/4:2:0 modes, VBR/simple 4:2:2 modes, slice count/dimension programming, PPS generation, suspend/resume restore, and DSC power-gating paths.
- Monitor DSCC overflow/underflow interrupt status, rate-buffer maximum fullness, rate-control-buffer maximum fullness, and error/max-error readbacks under high-bandwidth DSC modes.
- Exercise DWB frame capture with crop windows, multiple output formats, CRC enable/readback, host-read throttling, backpressure/overflow counters, soft reset, and update-lock sequencing.
- Exercise DWB color-management paths for HDR multiplier, gamut remap A/B matrices, OGAM bypass/RAMA modes, LUT index/data writes, and RAMA region programming; adjacent chunks are needed for full RAMA/RAMB coverage.
- Read perfmon17 through perfmon21 counters with known event selections and verify enable, trigger, current-value interrupt, low/high readback, and rollover behavior.

## Open Questions For Merge Lane

- Confirm the previous chunk contains the start of DSC0 `DSCC_PPS_CONFIG13` and earlier DSC0 field definitions.
- Confirm the next chunk completes `DWB_OGAM_RAMA_REGION_26_27` through `DWB_OGAM_RAMA_REGION_32_33` and the DWB RAMB field family.
- In the final per-file report, avoid describing this chunk as a complete DWB writeback mask surface; it is only the DWB top/DWBCP opening portion.

### subset-b-001854: lines 51573-54012

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 51573-54012

## Scope

This chunk covers lines 51573-54012 of the generated AMD DCN 3.1.4 shift/mask header. It is entirely preprocessor metadata: 2,123 `#define` entries across 2,440 source lines, with 1,061 `__SHIFT` constants and 1,062 `_MASK` constants plus generated register and `addressBlock` comments. There are no functions, structs, enums, variables, includes, allocation paths, locks, or executable statements in this range.

The range starts in the middle of `DWB_OGAM_RAMA_REGION_24_25` with the final mask for RAMA region 25, then covers the tail of DWB OGAM RAMA region definitions, the full DWB OGAM RAMB programming block, DCHVM host-VM/control fields, HPO DisplayPort stream encoder instances 0 and 1, their APG/DME/VPG companion blocks, SYM32 encoder instances 0 and 1, HPO DP link encoders 0 and 1, and DPHY SYM32 instances 0 and 1. It ends at the comment for `DP_DPHY_SYM321_DP_DPHY_SYM32_CRC_CONFIG0`; the CRC config field definitions continue in the next chunk.

## Purpose

The purpose of this header slice is to publish exact bit positions and masks for DCN 3.1.4 display hardware registers. AMDGPU display code combines these macros with the matching DCN 3.1.4 offset header and register helper macros to pack MMIO writes, read individual status fields, and construct DMUB/display register tables without embedding raw bit numbers in driver logic.

This is a generated hardware contract. Its correctness depends on the macro names and numeric values matching the ASIC register database. Runtime behavior is implemented by consumers that use these constants; this file only supplies field layout.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask within a 32-bit register value.
- `//<REGISTER>` comments group fields belonging to a logical register.
- `// addressBlock: ...` comments group registers by decoded hardware block.

Major constant families in this chunk include:

- `DWB_OGAM_RAMA_REGION_26_27` through `DWB_OGAM_RAMA_REGION_32_33` and `DWB_OGAM_RAMB_*`, covering DWB output gamma RAM region starts, bases, slopes, ends, offsets, and per-region LUT offsets/segment counts for RGB channels.
- `DCHVM_CTRL0/1`, `DCHVM_CLK_CTRL`, `DCHVM_MEM_CTRL`, `DCHVM_RIOMMU_CTRL0`, and `DCHVM_RIOMMU_STAT0`, covering host-VM initialization, display/DCF clock gating controls, GPUVM retention power controls, RIOMMU prefetch requests, and RIOMMU active/done status.
- `DP_STREAM_ENC0_*` and `DP_STREAM_ENC1_*`, covering HPO DP stream encoder clock enable/reset/status, input mux stream source selection, audio stream source selection, clock-ramp-adjuster FIFO control/status, and spare fields.
- `APG0_*` and `APG1_*`, covering audio packet generator reset/enable, DP audio stream ID, channel-count override, debug audio generator controls, ACP/audio-info packet source selection, audio CRC control/result/status, output-active status, memory power, and spare registers.
- `DME5_*` and `DME6_*`, covering dynamic metadata engine requestor IDs, enablement, stream type, double-buffer pending/taken/clear/disable fields, missed-transmission status/clear, and DME memory power controls.
- `VPG5_*` and `VPG6_*`, covering generic packet indexed data access, generic sideband packet frame and immediate update controls for packet slots 0-14, conflict/lock status, VPG memory power, ISRC indexed data, and MPEG info packet fields.
- `DP_SYM32_ENC0_*` and `DP_SYM32_ENC1_*`, covering 32-bit symbol encoder enable/reset, video FIFO control, MSA and pixel-format double buffering, pixel format, MSA words 0-8, HBLANK minimum width, 15 generic sideband packet controls, SDP stream/audio/metadata packet controls, MSA/VBID scheduling, video stream enable/status, panel replay tunneling optimization, video CRC control/results/status, memory power, and spare fields.
- `DP_LINK_ENC0_*` and `DP_LINK_ENC1_*`, covering HPO DP link encoder clock enable and clock-on-SYMCLK32 controls.
- `DP_DPHY_SYM320_*` and `DP_DPHY_SYM321_*`, covering DPHY enable/reset/precoder/mode/lane count, status, SAT update, four virtual-channel rate controls, SAT VC configuration/status, training pattern configuration, PRBS seeds, square-pulse/custom test patterns, error status, and per-stream symbol override controls.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time token expansion:

1. DCN 3.1.4 display code includes the generated offset and shift/mask headers.
2. Register helpers concatenate register and field identifiers to resolve `__SHIFT` and `_MASK` macros from this file.
3. Runtime driver code uses the resolved constants to perform MMIO or indexed-register reads, writes, read-modify-write updates, and field decoding.

The declaration order mirrors hardware organization. Within the HPO DP area, instance 0 is declared first, followed by its APG, DME, VPG, SYM32 encoder, link encoder, and DPHY blocks; instance 1 repeats the same structure. Repeated field layouts are intentionally duplicated per instance so helper macros can resolve instance-specific names.

## State And Persistence Behavior

The header itself stores no software state and persists no data. It describes bit locations for hardware state in DCN 3.1.4 registers.

Writable fields in this range can program DWB output gamma transfer curves, DCHVM power/clock/RIOMMU behavior, HPO DP stream encoder clocking and routing, APG audio packet generation, DME metadata transmission, VPG generic packet scheduling, SYM32 video/audio/metadata sideband packet generation, video stream enablement, panel replay optimization, DPHY mode/lane/rate/SAT/training-pattern behavior, and memory power controls for several subblocks.

Hardware-updated fields expose FIFO reset/done/active/error state, APG CRC/status/FIFO overflow, DME pending/taken/missed status, VPG lock/conflict/update-pending status, SYM32 double-buffer pending, stream status, CRC valid/results, DPHY active/reset/current-mode/update-pending/error/CRC-related status, RIOMMU state, and memory power state. Access type, reset values, read-clear or write-one-to-clear semantics, and required sequencing are not encoded in this header.

Programmed values persist according to the underlying hardware power and reset domains. They may survive until rewritten, display block reset, audio/link reinitialization, suspend/resume restore, GPU reset, or ASIC reset. Status and counter-like observations can change asynchronously relative to C code that includes this header.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.1.4 register offset header for addresses. The shift/mask header identifies bit placement only; it does not say where a register is mapped.

Primary consumers are AMDGPU display register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, `FD_SHIFT`, and generated register tables that paste register and field names into these macro symbols. A missing or renamed symbol usually fails at build time. A wrong numeric shift or mask can compile successfully and only show up as hardware misprogramming or misread status.

Key integration areas are:

- DWB/gamma programming paths that load output gamma RAM region descriptors and per-channel start/end/base/slope/offset values.
- Display VM and power-management paths that manipulate DCHVM clock, retention, and RIOMMU request/status fields.
- HPO DisplayPort bring-up and modeset paths that configure stream encoders, link encoders, DPHY instances, virtual-channel rates, SAT slots, stream source selection, symbol encoding, training/test patterns, and CRC diagnostics.
- Display audio and packet-generation paths that use APG, VPG, DME, and SYM32 SDP fields for DP audio packets, generic sideband packets, metadata packets, ISRC/MPEG info, and audio/video CRC validation.
- Panel replay, MST/SAT, and metadata scheduling paths that rely on line-number, SOF-reference, double-buffer, pending, and deadline-missed fields being packed correctly.

The generated offset and shift/mask headers must come from the same DCN 3.1.4 register database. Mixing this file with DCN 3.1.2, DCN 3.1, or later ASIC headers is risky because many field names are structurally similar while offsets or bit layouts can diverge.

## Risks And Edge Cases

- The chunk starts mid-register. Only the final `DWB_OGAM_RAMA_REGION_24_25__DWB_OGAM_RAMA_EXP_REGION25_NUM_SEGMENTS_MASK` line for `DWB_OGAM_RAMA_REGION_24_25` is present; preceding shifts/masks for that register are in the previous chunk.
- The chunk ends at the `DP_DPHY_SYM321_DP_DPHY_SYM32_CRC_CONFIG0` comment. The actual CRC config shifts and masks for DPHY instance 1 continue in the next chunk.
- Repeated HPO instance layouts are copy-sensitive. `DP_STREAM_ENC0`/`1`, `APG0`/`1`, `VPG5`/`6`, `DP_SYM32_ENC0`/`1`, `DP_LINK_ENC0`/`1`, and `DP_DPHY_SYM320`/`321` differ mostly by instance number, so generator drift can be difficult to review manually.
- Many fields are control/status adjacent. For example, enable/reset fields sit near reset-done/status bits; sideband packet trigger bits sit near pending/deadline bits; CRC enable bits sit near result/status fields. Blind read-modify-write patterns must respect hardware access rules outside this header.
- High-bit packed fields such as transmission line numbers (`0xFFFF0000L`), VC rate X values (`0xFE000000L`), DPHY symbol override stream fields, and OGAM region descriptors can corrupt unrelated settings if a shift or mask is wrong.
- Full-width masks such as spare registers and MSA data words use `0xFFFFFFFFL`; consumers should avoid signed-width assumptions and preserve 32-bit register semantics.
- DPHY training pattern, PRBS seed, custom pattern, symbol override, and error-status fields are link-training and diagnostic sensitive. Incorrect masks can break link bring-up or make CRC/error diagnostics misleading while still compiling.
- VPG/APG/DME update-pending and double-buffer fields imply hardware sequencing. This header does not document when software should poll, clear, or defer updates.

## Test Signals

Useful validation is mostly build-time consistency plus hardware integration:

- Build AMDGPU display code for a DCN 3.1.4-enabled configuration to catch missing or renamed macros used by register helper expansion.
- Mechanically verify that each complete register in this line range has matching `__SHIFT` and `_MASK` symbols for every field, while accounting for the partial first and last registers.
- Compare this slice against the authoritative DCN 3.1.4 register database and the matching offset header to ensure every register comment has the intended address and every field has the intended bit layout.
- Exercise DWB output gamma programming with nontrivial transfer functions, checking for channel-specific artifacts that would indicate bad RAMB/RAMA start, segment, slope, offset, or region fields.
- Exercise HPO DisplayPort link bring-up, modeset, stream enable/disable, MST/SAT scheduling, link training, training-pattern diagnostics, sideband packet transmission, metadata packet scheduling, panel replay, and CRC capture on DCN 3.1.4 hardware.
- Exercise DP audio paths through APG/VPG/SYM32 fields: stream ID routing, packet generation, ISRC/MPEG info, audio CRC, mute/status behavior, hotplug/resume reprogramming, and multichannel/HBR-like stress cases where available.
- Watch for FIFO errors, DME metadata missed-transmission bits, VPG generic packet conflicts, SYM32 double-buffer pending stuck states, DPHY rate/SAT update pending states, and DPHY error-status bits during display/audio tests.

## Open Cross-Chunk Notes

The merge lane should combine this chunk with the previous chunk to describe `DWB_OGAM_RAMA_REGION_24_25` completely. It should combine this chunk with the next chunk to describe `DP_DPHY_SYM321_DP_DPHY_SYM32_CRC_CONFIG0` and the remainder of the DPHY/SYM32 instance 1 diagnostics completely. Whole-file analysis should reconcile this chunk with neighboring DCN 3.1.4 generated-header chunks before making final claims about the complete set of HPO DP, DWB, DCHVM, APG, DME, VPG, and DPHY registers exposed by `dcn_3_1_4_sh_mask.h`.

### subset-b-001855: lines 54013-56454

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h

Chunk: `subset-b-001855`
Covered source range: lines 54013-56454 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h`

## Purpose

This chunk is a generated AMD DCN 3.1.4 register field mask header section. It contains C preprocessor constants for bit shifts and masks in display hardware registers; it is not executable logic and does not define functions, structs, or storage.

The covered range spans three major display areas:

- the tail of `DP_DPHY_SYM321` CRC fields for a 32-symbol DisplayPort DPHY block;
- HPO DisplayPort stream encoder instance 2 and instance 3 support blocks, including `DP_STREAM_ENC`, APG audio packet generator, DME metadata engine, VPG video packet generator, and `DP_SYM32_ENC` video/symbol encoder fields;
- MPC/MPCC composition fields for MPCC instances 0 through 3 and the beginning of MPCC output-gamma (`MPCC_OGAM0`) programming for LUT, gamut/gamma mode, RAM A region descriptors, and the start of RAM B region descriptors.

The chunk starts mid-register: `DP_DPHY_SYM321_DP_DPHY_SYM32_CRC_CONFIG0` begins before line 54013, and this range starts at its field definitions. It ends mid-register-family: `MPCC_OGAM0_MPCC_OGAM_RAMB_REGION_14_15` is only partially present at line 56454, with the remaining mask fields and later MPCC OGAM registers in the next chunk. The final per-file merge should preserve both boundary splits.

## Important APIs, Types, And Macros

There are no runtime APIs, types, or functions in this range. The public interface is the generated macro contract:

- `<REGISTER>__<FIELD>__SHIFT` is the bit position used when packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK` is the 32-bit field mask used by register helpers.
- Companion address macros live in `dcn_3_1_4_offset.h` as `reg<REGISTER>` or related base-index definitions; this header supplies only field layout.

Important macro families in this chunk include:

- `DP_DPHY_SYM321_DP_DPHY_SYM32_CRC_*`: DPHY symbol CRC enable/reset, source selection, scheduler selection, start/end event selection, symbol count, CRC done/status, CRC value, and counted-symbol reporting.
- `DP_STREAM_ENC2_*` and `DP_STREAM_ENC3_*`: HPO DP stream encoder clock enable/source status, pixel stream mux, audio stream mux, clock-ramp FIFO enable/reset/status/error, FIFO calibration and override levels, and spare bits.
- `APG2_*` and `APG3_*`: audio packet generator reset, enable, DP audio stream ID, ASP channel-count override, debug audio generation, packet source selection, audio CRC control/result, audio/HBR/FIFO overflow status, output active state, memory power control, and spare bits.
- `DME7_*` and `DME8_*`: metadata engine requestor ID, enable, stream type, double-buffer pending/taken status, clear bits, double-buffer disable, missed-transmission latch/clear, and metadata-engine memory power state.
- `VPG7_*` and `VPG8_*`: generic packet data access and indexed byte payloads, frame/immediate generic stream packet update controls, generic status, memory power control, ISRC packet access/data, and MPEG infoframe payload fields.
- `DP_SYM32_ENC2_*` and `DP_SYM32_ENC3_*`: symbol encoder enable/reset/status, video FIFO enable/reset/watermark/error, MSA and pixel-format double buffering, pixel encoding and component depth, MSA lane bytes, hblank minimum symbol width, generic stream packet controls, SDP/audio/metadata packet controls, MSA/VBID/stream control, panel replay controls, video CRC control/result/status, memory power control, and spare bits.
- `MPCC0_*` through `MPCC3_*`: top and bottom MPC input selection, OPP ID, alpha/multiplied-alpha/pre-multiplied-alpha mode, background color, shared memory power, MPCC status, update-lock selection, stereo/mode fields, and gain controls for top/bottom and inside/outside alpha.
- `MPCC_OGAM0_*`: output gamma mode/select/PWL disable/current status, LUT index/data/indexing control, RAM A and RAM B start/end/slope/base/offset fields per B/G/R channel, and paired region descriptors for regions 0-33 in RAM A and regions 0-15 at the end of this chunk.

## Control Flow

This header chunk has no internal control flow. All behavior occurs in code that includes this header and uses the generated constants to build register tables.

The runtime pattern is:

1. DCN314 display resource or block code includes `dcn_3_1_4_offset.h` and `dcn_3_1_4_sh_mask.h`.
2. Register-list macros select the instance addresses from the offset header.
3. Mask/shift list macros select the field constants from this header.
4. Block constructors store register addresses, shifts, and masks in per-block structures.
5. Display code later calls `REG_SET`, `REG_UPDATE`, `REG_GET`, or related helper macros, which use these masks and shifts to perform read/modify/write or polling operations.

Concrete integration points in this source tree:

- `display/dc/resource/dcn314/dcn314_resource.c` includes this header and builds DCN314 resource tables. Its HPO stream encoder tables use `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST(id)` and `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST(__SHIFT/_MASK)`, so the `DP_STREAM_ENC*` and `DP_SYM32_ENC*` fields in this chunk become the HPO stream encoder's register-field metadata.
- `display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h` defines the shared HPO DP stream encoder field list. It maps fields such as `DP_STREAM_ENC_CLOCK_EN`, `FIFO_RESET`, `FIFO_RESET_DONE`, `DP_SYM32_ENC_ENABLE`, pixel-format fields, MSA double-buffer fields, stream enable/status, SDP enable, audio enables, video CRC fields, and hblank symbol width to the generated masks and shifts.
- `display/dc/resource/dcn314/dcn314_resource.c` maps HPO stream encoders to sub-blocks: VPG register blocks 6-9 map to HPO DP instances 0-3, and APG register blocks 0-3 map to HPO DP instances 0-3. In this chunk, instance 2 uses `VPG7`/`APG2`, and instance 3 uses `VPG8`/`APG3`.
- `display/dc/mpc/dcn10/dcn10_mpc.h`, `display/dc/mpc/dcn30/dcn30_mpc.h`, `display/dc/mpc/dcn32/dcn32_mpc.h`, and related resource headers consume the MPCC fields. The `MPCC0..3` fields form per-MPCC composition metadata, while `MPCC_OGAM0` fields support MPCC output gamma and gamut-remap programming.
- `display/dc/resource/dcn32/dcn32_resource.h` shows the MPC register-list pattern used by later DCN resource code: MPCC registers and MPCC OGAM LUT/RAM A/RAM B region registers are collected through `SRII(..., MPCC_OGAM, inst)` entries and then paired with these generated mask/shift constants.
- `display/dmub/src/dmub_dcn314.c` includes the DCN314 offset and mask headers for DMUB service register definitions. This chunk is part of the same ASIC-specific register namespace available to DMUB-facing code, although the fields in this range are primarily display datapath and HPO/MPC fields.

## State And Persistence Behavior

The header itself is stateless. It performs no I/O, owns no memory, and has no persistence beyond compiled constants in driver objects.

The hardware fields described by these macros are persistent register state in display blocks until changed by driver writes, firmware writes, power gating, display block reset, ASIC reset, suspend/resume restore, or link/stream reprogramming. Important state categories include:

- HPO DP stream routing and clocks: `DP_STREAM_ENC_CLOCK_EN`, clock-on-source status bits, pixel/audio stream mux fields, and FIFO enable/reset/status fields.
- HPO video-symbol encoding: `DP_SYM32_ENC_ENABLE`, reset/done bits, FIFO enable/reset/error, pixel format, MSA lane data, VBID compressed-stream flag behavior, stream enable/status, panel replay markers, and video CRC status.
- Packet generation: APG audio packet enable/reset/CRC/status, VPG generic packet payload/index/update state, ISRC/MPEG packet data, SDP generic-stream controls, SDP audio controls, metadata packet enable, and DME double-buffer handoff/missed-transmission status.
- Memory power controls: APG, DME, VPG, DP SYM32 encoder, MPCC, and MPCC OGAM memory power force/disable/state/default-low-power fields.
- Composition pipeline state: MPCC top/bottom input selection, OPP routing, alpha/multiply/pre-multiply controls, stereo/mode controls, update-lock selection, background color, gain factors, and status.
- Output gamma state: MPCC OGAM mode, selected LUT RAM, LUT index/data programming state, RAM A/B per-channel start/end/base/slope/offset values, and region LUT offsets/segment counts.

Several fields are status or latch/clear style, for example APG audio FIFO overflow clear, DME double-buffer taken clear, metadata transmission missed clear, CRC done clear/status fields, FIFO reset done, and stream/FIFO status fields. The macros do not encode access type or ordering requirements; those are enforced by hardware documentation and by the existing register helper sequences in HPO, VPG/APG, stream encoder, and MPC code.

## Dependencies And Integration Points

Direct dependencies are minimal:

- the C preprocessor;
- the matching DCN 3.1.4 offset header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`;
- AMD display register helper conventions (`REG_SET`, `REG_UPDATE`, `REG_GET`, `FD`, `FN`, `SF`, `SE_SF`, `SRI`, `SRII`, and related macros) that assemble register addresses with masks and shifts.

Functional dependencies are the display blocks represented by the register names:

- DCN314 resource construction decides how many stream encoders, HPO stream encoders, HPO link encoders, MPCCs, and MPCC OGAM/LUT resources exist.
- HPO DP stream encoder code depends on these constants to program the stream encoder, symbol encoder, MSA, VBID, generic packet, audio packet, metadata packet, and CRC fields.
- APG/VPG/DME helper objects depend on the APG, VPG, and DME masks for audio packet, generic packet, metadata, and memory-power controls.
- MPC/MPCC code depends on the MPCC and MPCC OGAM fields for plane composition, blending, update locking, output gamma programming, and debug state capture.
- DC debug and diagnostic paths can read MPCC OGAM state; `dc.h` includes debug arrays for `mpcc_ogam_mode`, `mpcc_ogam_select`, and `mpcc_ogam_pwl_disable`, which correspond to fields in `MPCC_OGAM0_MPCC_OGAM_CONTROL`.

This chunk is also tightly coupled to generated ASIC naming. Instance numbering matters: `DP_STREAM_ENC2` pairs with `DP_SYM32_ENC2`, `APG2`, `DME7`, and `VPG7`; `DP_STREAM_ENC3` pairs with `DP_SYM32_ENC3`, `APG3`, `DME8`, and `VPG8`. Callers should not infer a simple one-to-one APG/DME/VPG numeric suffix from the HPO stream encoder suffix without checking the resource mapping.

## Risks And Edge Cases

The largest risk is silent field-layout drift. If a mask or shift is wrong, the driver still compiles, but read/modify/write helpers can program the wrong bits in display hardware. High-impact examples in this chunk include stream enable/reset, FIFO reset/status, packet enables, memory power state, MPCC source selection, MPCC alpha modes, and MPCC OGAM LUT/region programming.

Boundary splits are easy to mishandle during automated analysis. This chunk starts without the `//DP_DPHY_SYM321_DP_DPHY_SYM32_CRC_CONFIG0` comment and without any preceding macros for that register. It ends after only the `__SHIFT` fields and first mask for `MPCC_OGAM0_MPCC_OGAM_RAMB_REGION_14_15`; its remaining mask fields and later RAM B regions are outside this chunk.

Instance mismatches are another risk. HPO DP stream encoder instance 2 uses APG2 but DME7/VPG7, and instance 3 uses APG3 but DME8/VPG8. Register table generation must preserve these mappings or HPO streams may send packets, metadata, audio, or video over the wrong sub-block.

Status and clear bits need access-type discipline. Fields such as APG FIFO overflow clear, DME double-buffer/missed-transmission clear, CRC done clear, reset done, and FIFO error/status fields are not ordinary persistent configuration values. Treating all fields as plain read/write fields can lose events, fail to clear latches, or race with hardware state changes.

MPCC OGAM programming spans many related registers. LUT mode/select, LUT index/data, RAM A/B channel start/end/slope/base/offset, and region descriptors need coherent update ordering. Partial writes or bank-selection mistakes can produce visible color errors, stale gamma curves, or debug readbacks that disagree with intended state.

Generated macro consumers often use compile-time field-list expansion. Renaming a macro, changing the generated suffix, or moving a field between address blocks will break table initialization for DCN314 resource code or, worse, compile if a same-named field from a different instance is accidentally selected.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing rather than unit-level:

- Build coverage for DCN314 display code with `dcn314_resource.c`, `irq_service_dcn314.c`, `dmub_dcn314.c`, HPO stream encoder code, APG/VPG/DME code, and MPC/MPCC code enabled. This catches missing or renamed generated macros.
- Static checks comparing `dcn_3_1_4_sh_mask.h` against the matching `dcn_3_1_4_offset.h` and against adjacent generated ASIC versions for expected field names and instance counts.
- HPO DP functional tests that enable HPO stream encoders 2 and 3, verify stream mux selection, reset/done sequencing, FIFO reset/enable, stream enable/status, MSA programming, VBID compressed-stream flags, and hblank symbol width.
- DP packet tests for VPG/APG/DME behavior: generic SDP insertion, metadata packet enable/double-buffer handoff, audio packet enable/mute/CRC, ISRC/MPEG infoframe writes, and APG/VPG memory power transitions.
- CRC diagnostics: symbol CRC and video CRC enable/reset/result/status paths should report stable values for known test patterns and clear/reset cleanly across stream disable/enable.
- MPC/MPCC composition tests with multiple planes: top/bottom selection, alpha and pre-multiplied-alpha modes, update-lock selection, background color, and gain programming should produce expected blending output.
- MPCC OGAM tests: program LUT RAM A/B, switch selected bank, verify PWL enable/disable, read back LUT index/data and region descriptors, and compare output color/gamma against expected ramp behavior.
- Suspend/resume and power-gating tests for APG, DME, VPG, DP SYM32, MPCC, and MPCC OGAM memory power state restoration.

## Notes For Final Merge

This chunk should be merged with adjacent chunks for the same header before producing a final per-file report. The previous chunk owns the beginning of the `DP_DPHY_SYM321_DP_DPHY_SYM32_CRC_CONFIG0` block; the next chunk owns the rest of `MPCC_OGAM0_MPCC_OGAM_RAMB_REGION_14_15`, later RAM B region descriptors, and subsequent MPCC OGAM/gamut-remap fields. The final file-level report should describe the whole header as generated DCN314 register-field metadata, not as independent handwritten driver logic.

### subset-b-001856: lines 56455-58975

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 56455-58975

## Purpose

This chunk is generated AMD DCN 3.1.4 display-controller register field metadata for the MPC/MPCC portion of the display pipeline. It contains no executable C logic; it publishes preprocessor constants that describe bit positions and masks for fields inside DCN314 MPC output gamma, output color-space conversion, global MPC configuration, DWB routing, and RMU shaper registers. Runtime display code combines these field constants with register offsets from `dcn_3_1_4_offset.h` and DC register helper macros before issuing MMIO reads, writes, read-modify-writes, waits, or debug captures.

The requested range contains 2,089 `#define` lines: 1,044 `__SHIFT` macros and 1,045 `_MASK` macros. It starts in the tail of the `MPCC_OGAM0` RAMB region definitions, covers complete `MPCC_OGAM1`, `MPCC_OGAM2`, and `MPCC_OGAM3` field blocks, covers the MPC global configuration and output CSC/denorm blocks, and ends inside the first RMU0 shaper RAMA region table. Although this repository path is under a `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata, not Ceph filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, local variables, includes, allocation paths, or locks in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

Major macro families covered here:

- `MPCC_OGAM0_*`: the chunk begins after the start of `MPCC_OGAM0_MPCC_OGAM_RAMB_REGION_14_15`, then completes RAMB region descriptors from regions 16 through 33 and the OGAM0 gamut-remap coefficient format, gamut-remap mode, and A/B matrix coefficient fields.
- `MPCC_OGAM1_*`, `MPCC_OGAM2_*`, and `MPCC_OGAM3_*`: complete per-MPCC output gamma controls for three instances, including `MPCC_OGAM_CONTROL`, host LUT index/data/control, RAMA/RAMB start/end/slope/base/offset fields, piecewise-linear region descriptors for regions 0 through 33, and per-MPCC gamut-remap coefficient format/mode and 3x4 matrix coefficient fields.
- `MPC_CLOCK_CONTROL` and `MPC_SOFT_RESET`: global MPC clock gating/test-clock and soft-reset fields for MPCC0-3 plus MPC SFR/SFT subblocks and the global MPC reset bit.
- `MPC_CRC_*`: fields for enabling MPC CRC, continuous and one-shot capture, stereo/interlace modes, CRC source selection, update lock/status, source selection for DPP/OPP/DWB, CRC mask, and AR/GB/C result registers.
- `MPC_BYPASS_BG_*`, `MPC_HOST_READ_CONTROL`, `MPC_DPP_PENDING_STATUS`, and `MPC_PENDING_STATUS_MISC`: fields for bypass background color, host-read throttling, pending surface/config/cursor updates for DPP0-3, pending OPP/MPCC/DWB updates, and DWB mux routing.
- `ADR_CFG_CUR_VUPDATE_LOCK_SET<n>`, `ADR_CFG_VUPDATE_LOCK_SET<n>`, `ADR_VUPDATE_LOCK_SET<n>`, `CFG_VUPDATE_LOCK_SET<n>`, and `CUR_VUPDATE_LOCK_SET<n>` for instances 0 through 3: one-bit vertical-update lock request fields used to coordinate address/config/cursor update timing.
- `MPC_OUT0_*` through `MPC_OUT3_*`: output mux selection, rate/flow-control fields, denormalization clamp min/max fields, denorm mode fields, output CSC coefficient-format selection, per-output CSC mode/current status, and A/B banks of 3x4 output CSC matrix coefficient fields.
- `MPC_RMU_*` and `MPC_RMU0_SHAPER_*`: RMU mux routing/status, RMU memory power control for RMU0/RMU1 shaper and 3D LUT memories, RMU0 shaper mode/current status, RGB offset/scale fields, shaper LUT index/data/write-enable fields, and the beginning of RMU0 shaper RAMA region descriptors.

Several field names intentionally produce repeated suffixes such as `MPC_CRC_SEL_CONTROL__MPC_CRC_MASK_MASK` and `MPC_RMU0_SHAPER_LUT_WRITE_EN_MASK__MPC_RMU_SHAPER_LUT_WRITE_EN_MASK_MASK`. These are generated from fields whose hardware names include `MASK`; they are not accidental duplicate-mask definitions.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by the AMD display driver:

1. DCN314 resource, IRQ, and DMUB code include `dcn_3_1_4_sh_mask.h` together with the matching `dcn_3_1_4_offset.h`.
2. Token-pasting helpers such as `SF(...)`, `SR(...)`, `SRI(...)`, `SRII(...)`, and `SRII_MPC_RMU(...)` bind offsets, shifts, and masks into typed register/shift/mask tables.
3. `dcn314_resource.c` builds the `dcn30_mpc_registers`, `dcn30_mpc_shift`, and `dcn30_mpc_mask` tables using `MPC_REG_LIST_DCN3_0(0..3)`, `MPC_OUT_MUX_REG_LIST_DCN3_0(0..3)`, `MPC_RMU_GLOBAL_REG_LIST_DCN3AG`, `MPC_RMU_REG_LIST_DCN3AG(0..1)`, `MPC_DWB_MUX_REG_LIST_DCN3_0(0)`, and `MPC_COMMON_MASK_SH_LIST_DCN30(...)`.
4. MPC implementation code uses those tables to program MPCC composition/output gamma, output muxing, OCSC/denorm, CRC/debug capture, pending-update coordination, RMU shaper state, and memory-power controls during modesets, color updates, pipe routing changes, diagnostics, and power transitions.

The macros themselves do not encode ordering. Consumers must still sequence clock enablement, soft reset, memory power-up, update locks, double-buffered register updates, LUT bank selection, LUT writes, CSC bank programming, current-mode polling, CRC capture, DWB/RMU routing, and suspend/resume restoration according to hardware rules.

## State And Persistence Behavior

The file stores no software state and persists nothing. It describes MMIO-backed hardware state whose lifetime and side effects are hardware-defined. Represented state includes:

- MPCC output gamma mode/select bits, current-mode/current-select status, PWL disable, host LUT addressing/data, LUT write-color/read-color/debug/host/config controls, and RAMA/RAMB piecewise-linear segmentation for blue, green, and red channels.
- MPCC gamut remap coefficient format, active/current remap mode, and A/B banks of gamut-remap matrix coefficients.
- Global MPC clock/test/reset state, CRC enable/source/mode/update-lock state, CRC result state, bypass background color, host-read rate control, update-pending status, and vertical-update lock request fields.
- Output routing from MPC outputs 0 through 3, including rate-control overflow/ack/disable bits, flow-control mode/count, denorm clamp ranges, OCSC coefficient format, OCSC mode/current status, and A/B OCSC matrix banks.
- RMU routing/status, RMU memory power force/disable/low-power/state bits, RMU0 shaper offset/scale/LUT data, and the beginning of RMU0 shaper RAMA region segmentation.

Configuration fields generally retain values until a modeset, color pipeline update, power-gating event, suspend/resume path, or ASIC reset changes them. Status/current fields, pending-update fields, CRC result/pending fields, clock-gating controls, soft-reset controls, memory-power controls, and LUT index/data ports may be read-only, write-sensitive, sticky, self-clearing, banked, or sequencing-sensitive. This generated header only gives bit layout; it does not encode access type, reset value, volatility, or clear semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN314 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`, which provides the matching register offsets and `_BASE_IDX` selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`, which includes this header and builds the DCN314 MPC register, shift, and mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.h`, which defines the reusable MPC register-list and mask/shift-list macros consumed by the DCN314 resource layer.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`, which also include the generated DCN314 headers for register access and service tables.
- Common MPC, OPP, color-management, hardware sequencer, DMUB, CRC, DWB, and debug paths that reach these fields through the resource-layer register tables rather than by including this chunk directly.
- Enum headers such as `include/soc24_enum.h`, which document legal values for related MPC/MPCC concepts including CRC modes, VUPDATE lock booleans, OGAM LUT bank/select/mode values, and OGAM region segment counts.

The resource table exposes four MPC/MPCC/output instances for DCN314 and includes RMU global plus RMU0/RMU1 register lists while leaving a third RMU list commented out. Generated constants can therefore exist for broader hardware metadata than every actively instantiated path in a given ASIC configuration.

## Risks And Edge Cases

- Bitfield drift is the main risk. These are untyped constants; a wrong shift or mask can compile cleanly and cause read-modify-write operations to touch the wrong hardware bits.
- The range has artificial chunk boundaries. It starts after the first fields of `MPCC_OGAM0_MPCC_OGAM_RAMB_REGION_14_15` and ends before the rest of `MPC_RMU0_SHAPER_RAMA_REGION_12_13` and subsequent RMU shaper definitions, so adjacent chunks are required for complete OGAM0/RMU coverage.
- MPCC OGAM RAMA/RAMB definitions are highly repetitive. Instance or region copy-generation mistakes can affect only specific MPCCs, LUT banks, color channels, or high-index PWL regions.
- LUT programming is banked and port-based. Confusing LUT host selection, RAMA/RAMB selection, write-color masks, read-color selection, index width, data width, or region descriptors can produce incorrect gamma curves, channel swaps, stale bank activation, or visible color discontinuities.
- Gamut remap and output CSC use A/B coefficient banks plus current-mode fields. Writing the wrong bank or interpreting `*_CURRENT` fields as programming bits can lead to tearing during color updates or stale matrix activation.
- MPC soft reset, clock gating, memory power, and RMU power fields are sequencing-sensitive. Access while a block is gated or reset may be ignored, return stale status, or break polling paths.
- Pending-update and VUPDATE-lock fields affect atomic update timing. Incorrect masks can leave surface/config/cursor updates stuck, prematurely unlocked, or synchronized to the wrong pipe.
- CRC and output mux fields are diagnostic and routing critical. Wrong source select, result mask, rate-control ack, flow-control count, or DWB/RMU mux status fields can make CRC debugging misleading, hide output stalls, or route capture/composition paths incorrectly.
- Denorm and CSC masks are format-sensitive. Wrong clamp bounds, denorm mode, coefficient format, or matrix coefficient masks can cause clipped output, color-space conversion errors, HDR/SDR mismatch, or failures limited to particular pixel formats and output paths.
- Generated names containing `_MASK_MASK` are valid and should not be normalized away by cleanup scripts or manual edits.

## Test Signals

Useful validation combines generated-header consistency with display hardware behavior:

- Build AMDGPU/DC with DCN314 enabled; missing or renamed macros should fail in `dcn314_resource.c`, `irq_service_dcn314.c`, `dmub_dcn314.c`, or shared MPC headers.
- Mechanically verify that each complete in-range register field has a matching shift/mask pair, while allowing the documented boundary partials at `MPCC_OGAM0_MPCC_OGAM_RAMB_REGION_14_15` and `MPC_RMU0_SHAPER_RAMA_REGION_12_13`.
- Diff this range against AMD's authoritative DCN 3.1.4 register database and adjacent generated DCN 3.x headers where MPC/MPCC/RMU layouts are expected to match.
- Exercise MPCC output gamma programming on MPCC0-3, including RAMA/RAMB bank changes, PWL region programming, RGB write masks, LUT readback/debug paths, and transitions between bypassed and enabled modes.
- Exercise gamut remap and output CSC on outputs 0-3 with SDR, HDR, limited/full range, RGB/YCbCr, and color-management updates; watch for color shifts, clipping, stale matrices, or per-output-only failures.
- Test atomic modesets, plane updates, cursor movement, and multi-display configurations while checking DPP/OPP/MPCC/DWB pending-status bits and VUPDATE lock behavior.
- Validate MPC CRC capture in one-shot and continuous modes, different source selections, stereo/interlace modes, and CRC masks; compare against expected CRC stability and result registers.
- Test DWB and RMU routing plus RMU shaper programming where supported, including memory-power transitions, suspend/resume, runtime power management, and LUT/3D-LUT low-power behavior.
- Watch kernel logs and display diagnostics for stuck update locks, failed register waits, CRC mismatches, blank output after reset/power changes, color corruption, LUT bank mismatches, output mux overflow errors, or failures limited to higher-numbered MPC/MPCC instances.

## Cross-Chunk Notes

The previous chunk owns the beginning of `MPCC_OGAM0`, including the start of its RAMB region table. This chunk completes most of the OGAM0 tail and covers full OGAM1-3 generated field blocks plus MPC global/output metadata. The next chunk continues the RMU shaper region table after `MPC_RMU0_SHAPER_RAMA_REGION_12_13` and is required before making file-level claims about all RMU shaper and 3D LUT fields in `dcn_3_1_4_sh_mask.h`.

### subset-b-001857: lines 58976-61482

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 58976-61482

## Purpose

This chunk is generated AMD DCN 3.1.4 register field metadata. It contains no executable C logic; it publishes preprocessor constants for field shifts and bit masks used to pack and unpack 32-bit MMIO register fields in the display controller.

The requested range covers 2,118 `#define` lines, split evenly between 1,059 `__SHIFT` constants and 1,059 `_MASK` constants. It starts inside the MPC RMU0 shaper RAM A region table, covers the rest of RMU0 shaper RAM A and RAM B metadata, complete RMU0/RMU1 3D LUT and shaper metadata, DC performance monitor blocks 22 and 23, HPO HDMI/DP packet and stream-mapper blocks, and most of ABM instances 0 through 3. The final line stops inside `ABM3_DC_ABM1_ACE_OFFSET_SLOPE_3`, so later chunks are needed for the rest of ABM3.

Although this file lives under a local `ceph-client` source mirror, this is AMDGPU display-driver hardware metadata, not Ceph or distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this chunk. Its interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

Major register families in this slice:

- `MPC_RMU0_*` and `MPC_RMU1_*`: gamut/remap unit shaper LUT controls, RAM A/RAM B piecewise curve region descriptors, channel start/end controls, 3D LUT mode/index/data/read-write controls, output normalization, and per-channel output offsets.
- `DC_PERFMON22_*` and `DC_PERFMON23_*`: display performance counter select, clear, start, stop, state, mode, counter value, and threshold/mask fields.
- `AFMT5_*`: HDMI/audio formatter fields for VBI/audio packet controls, channel status words, audio infoframes, audio CRC, audio ramp generation, status, source select, infoframe update, and AFMT memory power.
- `VPG9_*`: video packet generator fields for generic packet indexed access, 15 frame-update bits, 15 immediate-update bits, conflict status/clear, memory power, ISRC data, and MPEG info.
- `DME9_*`: Display Micro Engine control and memory-control fields.
- `HPO_TOP_*`: high-performance output clock-gating/test-clock and HPO IO enable fields.
- `DP_STREAM_MAPPER_CONTROL0` through `CONTROL3`: DP stream-to-link target fields.
- `ABM0_*`, `ABM1_*`, `ABM2_*`, and partial `ABM3_*`: adaptive backlight/PWM registers, ABM enable and bypass, IPCSC coefficient select, ACE slope/offset and threshold fields, HGLS read-progress and lock fields, histogram/luma-stat controls and results, sample-rate controls, and master-lock fields.

Several patterns repeat with fixed field widths. RMU shaper region registers pack two regions per 32-bit register: low-region LUT offset at shift `0x0`, low-region segment count at `0xc`, high-region LUT offset at `0x10`, and high-region segment count at `0x1c`. ABM PWM level registers expose 17-bit duty/level values. Many result/data registers are full-width `0xFFFFFFFF` payload fields.

## Control Flow

This header has no runtime control flow. The runtime path is supplied by DCN register helper code:

1. DCN 3.1.4 resource, IRQ, and DMUB files include `dcn_3_1_4_offset.h` together with this `dcn_3_1_4_sh_mask.h`.
2. Resource construction builds register address tables from the offset header and field tables from this mask header. For example, `dcn314_resource.c` defines `SR`, `SRI`, `SRII`, and `SRII_MPC_RMU` token-pasting helpers, then fills MPC RMU register tables with `MPC_RMU_REG_LIST_DCN3AG(0)` and `(1)`.
3. Block-specific headers map these generated constants into typed shift/mask structs using macros such as `SF`, `SE_SF`, `HWS_SF`, and `ABM_SF`.
4. Driver code later uses `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET_*`, `REG_GET`, and polling helpers. Those helpers combine the register address, field shift, and field mask from the generated tables.

The chunk itself does not encode sequencing. Consumers must still handle ordering around display clocking, memory power, double-buffered updates, vblank/frame boundaries, link state, histogram-read timing, ABM firmware interaction, and performance-counter start/clear/read ordering.

## State And Persistence Behavior

The chunk stores no software state and persists nothing. It describes MMIO-backed GPU state.

The represented hardware state includes:

- RMU shaper and 3D LUT programming for color pipeline remap, including RAM bank selection, LUT write enable masks, mode/current-mode fields, and per-region curve descriptors.
- Display performance monitor configuration and counters, including selected event IDs, counter state, clear/start/stop controls, overflow/threshold status, and high/low counter value registers.
- HDMI/DP secondary-data packet generation state through AFMT and VPG fields, including audio infoframes, channel-status words, generic packets, ISRC/MPEG packets, conflict status, and packet update timing.
- HPO output control, stream mapper selection, clock-gating control, and DME/VPG/AFMT memory-power state.
- ABM/PWM state for ambient/user/current/target/final/minimum backlight levels, ABM enable/bypass flags, histogram and luma-stat sampling, ACE curve parameters, result registers, and register-lock/update-pending bits.

Persistence is hardware-defined. Configuration registers generally retain values until modeset, power gating, suspend/resume, or ASIC reset. Status/counter/result/clear fields may be read-only, sticky, self-clearing, write-one-to-clear, or updated by hardware at frame/sample cadence. This generated header does not mark those side effects; the consuming block code and hardware programming guides determine safe access sequences.

## Dependencies And Integration Points

This chunk must match the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`

Direct include sites for the DCN 3.1.4 generated headers in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`

Important consumer modules and contracts:

- `display/dc/mpc/dcn30/dcn30_mpc.c` uses the RMU shaper and 3D LUT fields while programming transfer functions, region descriptors, RAM A/B selection, LUT index/data ports, and read/write control.
- `display/dc/mpc/dcn30/dcn30_mpc.h` defines the MPC RMU register, shift, and mask field lists that consume `MPC_RMU*_...` macros from this chunk.
- `display/dc/dce/dce_abm.c` and `display/dc/dce/dmub_abm_lcd.c` write ABM sample-rate, histogram/luma-stat, IPCSC, PWM level, and read-progress fields; DMUB command paths also use ABM state for firmware-mediated backlight control.
- `display/dc/dce/dce_abm.h` maps ABM fields into register lists and shift/mask structs with `ABM_SF`.
- `display/dc/dcn31/dcn31_afmt.h` and `.c` consume AFMT audio/packet/memory-power fields.
- `display/dc/dcn31/dcn31_vpg.h` and `.c` consume VPG generic-packet, update, status, and memory-power fields.
- `display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h` and `.c` consume `DP_STREAM_MAPPER_CONTROL*` fields to route DP streams to HPO links.
- `dcn314_resource.c` includes HPO clock and IO fields in `HWSEQ_DCN31_MASK_SH_LIST`, tying `HPO_TOP_CLOCK_CONTROL` and `HPO_TOP_HW_CONTROL` into hardware sequencing.

## Risks And Edge Cases

- Shift/mask drift is the central risk. These constants are untyped preprocessor values, so an incorrect mask can compile cleanly while corrupting adjacent MMIO fields.
- Generated namespaces are copy-sensitive. RMU0/RMU1, ABM0-ABM3, and performance monitor 22/23 are structurally similar but instance-specific; a wrong instance prefix may only fail on a particular pipe, link, or panel.
- The chunk boundaries are artificial. The first visible line is the tail of `MPC_RMU0_SHAPER_RAMA_REGION_12_13`, and the final lines stop inside ABM3 ACE offset/slope registers.
- RMU shaper/3D LUT programming is stateful. Wrong RAM bank selection, write-enable mask, LUT index/data field, or region descriptor can produce color corruption, failed color management, or a transient glitch during modeset.
- ABM fields have frame/sample cadence and firmware interactions. Incorrect sample-rate, read-progress clear, lock, or PWM fields can cause stale histogram/luma data, missed-frame flags, brightness jumps, or conflicts with DMUB-controlled ABM updates.
- AFMT/VPG packet update fields are timing-sensitive. Incorrect update masks or memory-power fields can cause missing HDMI/DP infoframes, audio loss, metadata corruption, or packet conflicts.
- HPO and stream-mapper fields affect link routing and clocks. Bad masks can route a DP stream to the wrong link target or leave HPO IO/stream clocks disabled.
- Perfmon fields mix control, state, counters, and clear bits. Incorrect masks can silently invalidate diagnostics or leave counters stuck/overflowing.

## Test Signals

Useful validation combines generated-header consistency, compile coverage, and hardware behavior:

- Build AMDGPU display code with DCN 3.1.4 enabled; resource, IRQ, DMUB, MPC, ABM, AFMT, VPG, and HPO consumers should compile without missing or renamed shift/mask symbols.
- Mechanically verify that every field in lines 58976-61482 has exactly one `__SHIFT` and one `_MASK` define, and that field names match the companion `dcn_3_1_4_offset.h` register names.
- Diff the chunk against AMD's authoritative DCN 3.1.4 register database or adjacent generated DCN 3.x headers where register compatibility is expected.
- Exercise color-management paths that program RMU shaper and 3D LUT state, including modesets, gamma/degamma changes, HDR/color transforms, suspend/resume, and multi-plane composition.
- Exercise ABM/backlight paths on panels that support adaptive backlight: enable/disable ABM, change user brightness, read current/target levels, verify histogram/luma-stat updates, and test suspend/resume.
- Exercise HDMI/DP audio and metadata paths: audio playback, infoframes, generic packets, ISRC/MPEG metadata, packet update timing, and memory power transitions.
- Exercise HPO DP stream mapping with multiple links/streams, link training, hotplug, MST or high-bandwidth modes when available.
- Use perfmon/debug tools to confirm counters can be selected, cleared, started, stopped, and read without stuck state or bogus overflow/threshold status.
- Watch kernel logs and display diagnostics for blank displays, color corruption, audio dropouts, packet conflicts, ABM missed-frame flags, brightness jumps, link-routing failures, stuck interrupts, and resume regressions.

## Cross-Chunk Notes

Previous chunks own the beginning of RMU0 shaper RAM A, including regions before the visible `REGION_12_13` tail. Later chunks finish ABM3 and continue the remaining DCN 3.1.4 shift/mask namespace. The final per-file research document should merge adjacent chunks before making complete claims about all MPC RMU fields, all ABM3 registers, or the complete `dcn_3_1_4_sh_mask.h` hardware map.

### subset-b-001858: lines 61483-61832

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 61483-61832

## Scope

This chunk is the final slice of the generated DCN 3.1.4 register-field shift/mask header `dcn_3_1_4_sh_mask.h`. It contains C preprocessor constants only: `_SHIFT` macros for field low-bit positions, `_MASK` macros for raw register bit masks, register-name comments, address-block comments, and the closing `#endif`. There are no functions, structs, enums, allocations, branches, loops, or driver-owned state objects in this range.

The slice starts in the tail of the `ABM3_DC_ABM1_ACE_OFFSET_SLOPE_3` definitions, completes the `ABM3` automatic backlight module/statistics field definitions, then defines small `DPIA_MU`, HDA `AZCONTROLLER1`, `AZENDPOINT1`, and `AZINPUTENDPOINT1` register field groups. It ends the whole generated header.

## Purpose And Hardware Surface

The purpose of this header range is to provide the bit-layout ABI between AMDGPU Display Core code and DCN 3.1.4 display hardware. Companion offset headers, especially `dcn_3_1_4_offset.h`, provide the MMIO register addresses and base indices; this file provides the masks and shifts used by register helper macros to pack writes and decode readbacks without hard-coded bit positions.

Major hardware areas represented here:

- `ABM3_DC_ABM1_*` fields describe the third ABM instance's `ABM1` control and result register layout. The visible fields cover adaptive contrast enhancement slopes, offsets, thresholds, histogram/luma/backlight statistics control, missed-frame status, sample rates, histogram-bin shift metadata, histogram results, and a backlight master lock bit.
- `dce_dpia_dpia_mu0_dpiadec` fields describe the DPIA micro-unit RBBM interface timeout and invalid-access status surface. These fields expose timeout delay/hold, timeout disable, invalid access flag/type/address, timeout readback, and status clear.
- `dce_dc_hda_azcontroller_azdec` fields describe the display HDA controller command/response DMA rings and immediate-command path: CORB, RIRB, immediate command output, immediate response input, busy/result status, and DMA position buffer base address fields.
- `dce_dc_hda_azendpoint_azdec` fields provide endpoint immediate-command output data/index fields.
- `dce_dc_hda_azinputendpoint_azdec` fields provide input-endpoint immediate-command input data/index fields.

The chunk is hardware-definition data rather than active logic. Its correctness matters because higher-level display, DMUB, ABM, audio, interrupt, and diagnostics code uses these symbols as the source of truth for MMIO field layout.

## Important Definitions

The exported API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted bit mask within the register.
- `//<REGISTER>` comments group the field macros by hardware register.
- `// addressBlock: ...` comments mark the hardware aperture for following registers.

Important field families in this chunk:

- `ABM3_DC_ABM1_ACE_OFFSET_SLOPE_3` and `ABM3_DC_ABM1_ACE_OFFSET_SLOPE_4` provide 11-bit adaptive contrast enhancement slope fields, 11-bit offset fields starting at bit 16, and an `ABM1_ACE_LOCK` bit at bit 31. The range begins mid-register for slope/offset 3, so earlier fields for this register are in the previous chunk.
- `ABM3_DC_ABM1_ACE_THRES_12` and `ABM3_DC_ABM1_ACE_THRES_34` pack 10-bit ACE thresholds in the low and high halves of the register. `ACE_THRES_34` also exposes ignore-master-lock, double-buffer readback, update-pending, and lock bits in bits 28-31.
- `ABM3_DC_ABM1_ACE_CNTL_MISC` reports and clears ACE register writes that missed the target frame.
- `ABM3_DC_ABM1_HGLS_REG_READ_PROGRESS` exposes histogram (`HG`), luma statistics (`LS`), and backlight (`BL`) register-read-in-progress bits, missed-frame bits, and corresponding missed-frame clear bits.
- `ABM3_DC_ABM1_HG_MISC_CTRL` configures histogram/statistics behavior: number of bins, VMAX mode, fine mode, bin bit width, over-scan pixel processing, double-buffered readback, frame-start display selection, update-at-frame-start, master-lock bypass, update-pending readback, and HGLS register lock.
- `ABM3_DC_ABM1_LS_*` read back luma statistics: sum of luma, min/max luma, filtered min/max luma, pixel count plus sum MSBs, threshold programming for min/max pixel-value counters, and 24-bit min/max pixel-value counts.
- `ABM3_DC_ABM1_HG_SAMPLE_RATE` and `ABM3_DC_ABM1_LS_SAMPLE_RATE` enable sample-rate counters, reset their frame counters, program 8-bit frame-count values, program initial reset values, and share the HGLS register lock bit.
- `ABM3_DC_ABM1_HG_BIN_*` fields expose packed histogram-bin shift flags and shift index words for bins 1-32.
- `ABM3_DC_ABM1_HG_RESULT_1` through `ABM3_DC_ABM1_HG_RESULT_24` expose full 32-bit histogram result words.
- `ABM3_DC_ABM1_BL_MASTER_LOCK` exposes the backlight master lock bit at bit 31.
- `DPIA_MU_RBBMIF_TIMEOUT_CTRL`, `DPIA_MU_RBBMIF_TIMEOUT_CTRL2`, and `DPIA_MU_RBBMIF_STATUS` define timeout delay/hold, timeout disable, invalid access flag/type/address, timeout status readback, and invalid-access status clear.
- `AZCONTROLLER1_CORB_*` fields define the HDA CORB write pointer, read pointer/reset, control, status, and ring size/capability fields.
- `AZCONTROLLER1_RIRB_*` fields define lower/upper RIRB base address, write pointer/reset, response interrupt count, control, status, and ring size/capability fields.
- `AZCONTROLLER1_IMMEDIATE_*` fields define immediate command output payload/codec address, output data/index windows, response input readback, and busy/result-valid status bits.
- `AZCONTROLLER1_DMA_POSITION_*` fields define the DMA position buffer enable bit and the split lower/upper base-address fields. The lower address reserves bits 1-6 as unimplemented and stores the aligned base at bit 7.
- `AZENDPOINT1_AZENDPOINT_IMMEDIATE_COMMAND_OUTPUT_INTERFACE_*` and `AZINPUTENDPOINT1_AZENDPOINT_IMMEDIATE_COMMAND_INPUT_INTERFACE_*` define endpoint immediate-command data and 17-bit index fields.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when AMDGPU Display Core, DMUB, ABM, or HDA-related code combines these constants with matching `reg*` offsets and register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WRITE`, generated `DMUB_SF` field tables, or equivalent MMIO accessor wrappers.

A typical use path is:

1. Select a DCN 3.1.4 register address and base index from `dcn_3_1_4_offset.h`.
2. Select the matching field mask and shift from this header.
3. Pack a value, extract a readback, or build a read/modify/write mask through the display register abstraction.
4. Let hardware store, latch, consume, report, or clear the represented field.

The state represented here is hardware state:

- Persistent configuration fields include ABM ACE slopes, offsets, thresholds, sample-rate controls, histogram mode controls, readback/double-buffer options, frame-start update controls, lock bits, DPIA timeout delay/hold/disable controls, HDA CORB/RIRB ring base/size/control registers, immediate command output fields, and DMA position buffer enable/base programming.
- Volatile readback fields include ABM luma sums, min/max luma, filtered min/max luma, pixel counts, min/max pixel-value counts, histogram-bin metadata, histogram result words, update-pending flags, read-in-progress flags, missed-frame flags, DPIA invalid-access and timeout status, HDA CORB/RIRB status, immediate command busy, and immediate result valid.
- Side-effecting write fields include missed-frame clear bits, sample-rate frame-counter resets, lock/master-lock bits when used to stage updates, `RBBMIF_INVALID_ACCESS_STATUS_CLEAR`, CORB/RIRB pointer reset bits, interrupt/status clear-style HDA fields, immediate command write windows, and DMA position buffer enable.
- Several ABM fields explicitly expose double-buffer and frame-start update behavior. Incorrect writes can land in the wrong frame, be missed by the hardware latch, or leave an update pending until a later vertical boundary.

The sequencing rules are not encoded in the macros. Callers must still respect display lock/update timing, ABM ownership, frame-start/vblank timing, display power state, register double-buffering, DPIA timeout/fault clearing semantics, and HDA ring/command protocols.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.1.4 register-address definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`. For the visible fields, that header maps examples such as `regABM3_DC_ABM1_HG_MISC_CTRL`, `regABM3_DC_ABM1_HG_RESULT_24`, `regABM3_DC_ABM1_BL_MASTER_LOCK`, `regDPIA_MU_RBBMIF_TIMEOUT_CTRL`, `regAZCONTROLLER1_CORB_WRITE_POINTER`, `regAZCONTROLLER1_IMMEDIATE_COMMAND_STATUS`, `regAZCONTROLLER1_DMA_POSITION_LOWER_BASE_ADDRESS`, and endpoint immediate-command registers to concrete offsets and base indices.

Known source integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`, which includes `dcn_3_1_4_sh_mask.h` and the matching offset header to build the DCN 3.1.4 DMUB register interface.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c`, which includes this header for DCN 3.1.4 interrupt/register field definitions.
- ABM/backlight and panel-control code paths that program automatic brightness management, adaptive contrast enhancement, histogram collection, luma statistics, and backlight locks through generated ABM register lists.
- DMUB/display diagnostics and hardware-sequencing code that may configure or decode DPIA RBBMIF timeout/invalid-access behavior.
- HDA/audio controller paths that use AZ controller register definitions to manage command output rings, response input rings, immediate codec commands, and DMA position buffer programming.
- Other generated ASIC revision headers in the same directory. The same field families appear across DCN 3.0, 3.2, 3.5.1, 3.6, and 4.1 headers, so maintenance often involves cross-revision comparison while preserving DCN 3.1.4-specific offsets and field availability.

Because the file is generated, most use is indirect through macros. A missing or misspelled field usually fails compilation where a `REG_FIELD`, `SF`, `DMUB_SF`, or register-list macro expands. A wrong numeric mask or shift can compile cleanly and cause runtime MMIO misprogramming.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.1.4 register specification is the primary risk. Incorrect masks or shifts can corrupt ABM thresholds, histogram readbacks, HDA ring pointers, immediate command fields, or timeout status decoding.
- This chunk begins in the middle of `ABM3_DC_ABM1_ACE_OFFSET_SLOPE_3`. The merge/reconciliation lane should preserve that neighboring chunks are needed for the full per-file story and should not infer that the register starts at line 61483.
- ABM field names are repetitive and instance-qualified. Confusing `ABM3` with another ABM instance, or confusing `HG`, `LS`, `BL`, and `ACE` fields, can target a valid but wrong hardware function.
- Lock bits and frame-start update bits are timing-sensitive. Using generic read/modify/write flows without observing ABM double-buffering and vblank/frame-start constraints can produce missed-frame flags or stale readbacks.
- Several status and clear fields share the same register family. `ABM1_ACE_REG_WR_MISSED_FRAME_CLEAR`, HGLS missed-frame clear bits, and `RBBMIF_INVALID_ACCESS_STATUS_CLEAR` should be treated as write-side effects, not persistent configuration values.
- Histogram and luma result fields are full-width or packed counters. Consumers must preserve the documented masks when combining `LS_SUM_OF_LUMA` with `LS_SUM_OF_LUMA_MSB`, interpreting 24-bit pixel counts, or reading `HG_RESULT_1..24`.
- HDA ring fields use small pointer and capability widths. Incorrect CORB/RIRB size, reset, DMA-enable, or base-address packing can break codec command transport or DMA position reporting.
- The AZ endpoint and input-endpoint data/index registers share similar offsets and names. Data versus index and output versus input confusion can still compile if a wrong macro exists.
- The closing `#endif` belongs to the whole generated header. Accidental edits near this chunk can break inclusion of the entire DCN 3.1.4 mask file.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Compile coverage for AMDGPU Display Core with DCN 3.1.4 enabled. This catches missing macro names, malformed generated constants, and broken include guards.
- Static comparison against the authoritative DCN 3.1.4 register database or a regenerated `dcn_3_1_4_sh_mask.h`, especially for bit positions, masks, and register/field spelling.
- Cross-revision spot checks against adjacent generated headers where hardware is expected to be compatible, while confirming DCN 3.1.4-specific differences are intentional.
- ABM functional testing on DCN 3.1.4 hardware: backlight changes, adaptive brightness/contrast behavior, histogram/luma readback sanity, missed-frame counters remaining clear during normal updates, and no stuck HGLS update-pending/read-in-progress flags.
- Display diagnostics for DPIA RBBMIF timeout and invalid-access handling, including status decode and clear behavior after induced or logged invalid accesses.
- Audio-over-display testing for HDA codec command transport: CORB/RIRB ring operation, immediate command busy/result-valid behavior, response interrupts, and DMA position buffer updates during playback.
- Runtime register dumps before and after ABM, DPIA, or HDA operations. Packed values should affect only the intended masked bits and preserve unrelated fields.

## Open Questions For Merge

- The exact high-level consumers for the `ABM3_DC_ABM1_*` fields are likely generated register lists in ABM resource code outside this chunk. The final per-file report should connect this end-of-file chunk with earlier ABM chunks that define the same instance's control, coefficient, and backlight fields.
- This chunk documents field layout only. The final merged report should avoid claiming behavioral sequencing beyond what is visible in the macros unless corroborated by functional source files.
