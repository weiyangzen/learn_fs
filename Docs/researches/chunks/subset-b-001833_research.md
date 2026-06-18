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
