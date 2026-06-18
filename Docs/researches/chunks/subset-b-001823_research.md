# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 51865-54474

## Scope

This chunk covers lines 51865-54474 of the generated DCN 3.1.2 shift/mask header. It contains only preprocessor constants and generated register grouping comments: 2070 `#define` entries, made up of 1034 `__SHIFT` constants and 1036 `_MASK` constants, plus 35 `addressBlock` group comments. There are no functions, structs, enums, storage objects, or executable statements in this range.

The range starts in the middle of `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL8`, after several shift definitions that belong to the previous chunk, and ends in the middle of the `AZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` / following pin-capability area that continues in the next chunk. Complete register families in the body cover HPO DisplayPort stream encoder 3 sideband/audio/video fields, HPO DP link encoder instances 0 and 1, HPO DP DPHY SYM32 instances 0 and 1, display HVM control, legacy VGA indexed register masks, Azalia F2 codec endpoint/input/root blocks, audio descriptor and sink-info indexed blocks, Azalia CRC result blocks, and Azalia F0 stream latency blocks 0-15.

## Purpose

The purpose of this region is to expose symbolic bit positions and masks for DCN 3.1.2 display, DisplayPort, VGA compatibility, and display-audio hardware registers. AMDGPU display code combines these macros with the matching DCN 3.1.2 offset header and register helper macros to pack writes, update individual fields, and decode status values without hard-coding raw bit layouts.

This is a generated hardware contract rather than algorithmic code. Its behavioral importance is the exact macro name and numeric bit layout. Runtime behavior is produced by consumers that use these constants for MMIO or indexed-register access.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask within a 32-bit register.
- `// addressBlock: ...` comments identify indexed or decoded register blocks.
- `//<REGISTER>` comments group the field macros for one logical register.

Major constant groups in this chunk include:

- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL8` through `GSP_CONTROL14`, with GSP sideband packet controls such as video/idle continuous transmission enable, one-shot trigger, one-shot position, double-buffer enable/pending, payload size, SOF reference, transmission pending/deadline status, and transmission line number.
- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_CONTROL`, `SDP_AUDIO_CONTROL0/1`, and `SDP_METADATA_PACKET_CONTROL`, covering sideband stream enable, CRC16 enable, audio packet enables for ASP/ATP/AIP/ACM/ISRC, audio mute/status, ATP version, audio packet concatenation limits, metadata packet enable, metadata double buffering, SOF reference, and line-number scheduling.
- `DP_SYM32_ENC3_DP_SYM32_ENC_VID_*` registers for main-stream attributes, VBID compressed-stream flag scheduling, stream enable/defer/status, panel replay tunneling optimization, video CRC control/results/status, memory power control, and spare bits.
- `DP_LINK_ENC0` and `DP_LINK_ENC1` clock-control/spare fields for link-encoder clock enable/force-on behavior.
- `DP_DPHY_SYM320` and `DP_DPHY_SYM321` DPHY SYM32 registers for reset/enable/status, output mode, lane count, scheduler status, SAT update and VC rate control, per-VC SAT configuration/status, training-pattern selection, PRBS seeds, square-pulse/custom test pattern data, error status, symbol override, and CRC configuration/status/count.
- `DCHVM_*` display HVM controls for enablement, VMID/PASID, clock control, memory interface settings, RIOMMU control, and RIOMMU status.
- Legacy VGA indexed masks for sequencer (`SEQ00`-`SEQ04`), CRT controller (`CRT00`-`CRT18`, `CRT1E`, `CRT1F`, `CRT22`), graphics controller (`GRA00`-`GRA08`), and attribute controller (`ATTR00`-`ATTR14`) fields.
- `AZALIA_F2_CODEC_*` endpoint, input-endpoint, and root-function registers for converter format, channel/stream ID, digital converter flags, stream/rate capability bitmaps, pin widget controls, unsolicited responses, pin sense, default configuration words, speaker/channel allocation, audio descriptors, multichannel enablement, HBR, lipsync, LPIB snapshots, coding type, format-change flags, wireless display identification, remote keepalive, subsystem IDs, power state, reset, and codec function parameters.
- `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13` and `SINK_DESCRIPTION0` through `SINK_DESCRIPTION17`, plus manufacturer/product IDs, sink description length, and port IDs used by the Azalia sink-info/descriptor indexed blocks.
- Azalia input/output CRC result blocks: `AZALIA_INPUT_CRC0/1_CHANNEL0-7` and `AZALIA_CRC0/1_CHANNEL0-7`.
- `AZF0STREAM0` through `AZF0STREAM15` stream latency and FIFO metrics: minimum FIFO size, maximum FIFO size, max latency support, latency-counter reset, worst-case latency count, cumulative latency count, and cumulative request count.
- The beginning of `AZF0ENDPOINT0` F0 endpoint converter/pin macros for audio widget capabilities, converter format, stream/channel routing, digital converter flags, stream formats, supported size/rates, stripe control, ramp rate, GTC embedding, GTC counter deltas, and the start of pin audio-widget capability fields.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time token expansion:

1. DCN 3.1.2 display code includes the matching offset and shift/mask headers.
2. Register helper macros concatenate register and field names to resolve these `__SHIFT` and `_MASK` constants.
3. Runtime display, DP, VGA, or audio code performs MMIO or indexed-register reads/writes using the resolved numeric layout.

The declaration order mirrors hardware organization. The chunk finishes part of DP stream encoder 3, then moves through HPO DP link/DPHY blocks, display VM, VGA indexed registers, Azalia F2 endpoint/root/descriptor/sink/CRC/input blocks, 16 F0 stream blocks, and finally starts the F0 endpoint 0 block.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes bit locations for hardware state in DCN 3.1.2 registers.

Writable fields in the described registers can program DP sideband packet timing, audio packet generation, metadata scheduling, video stream enablement, panel replay optimization, CRC capture, DPHY reset/enable/rate/test-pattern/CRC behavior, HVM/RIOMMU control, VGA compatibility state, Azalia converter formats, stream IDs, channel allocation, multichannel routing, digital converter flags, codec power/reset state, LPIB snapshot control, and latency-counter reset.

Hardware-updated or capability fields can expose DP stream/CRC status, DPHY scheduler/update/error/CRC status, RIOMMU status, VGA indexed register state, Azalia widget and pin capabilities, supported stream formats and sample rates, pin sense, hot-plug/audio status, input status, infoframe data, sink descriptors, CRC results, FIFO limits, and cumulative/worst-case latency counters. Access type, reset values, read-clear/write-one-to-clear behavior, and required programming order are not encoded here; consumers must follow the hardware spec and surrounding display/audio driver logic.

Programmed values persist according to hardware power/reset domains. They may survive until rewritten, display block reset, audio function reset, suspend/resume reinitialization, GPU reset, or ASIC reset. Counter and status fields are live hardware observations and can change without any C-visible state transition in this header.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.1.2 register offset header for addresses and indexed-register selectors. The shift/mask header alone only identifies bit positions; it does not identify where a register lives.

Primary integration points are AMD display register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT`, which rely on the generated suffix convention. A missing or renamed macro usually fails at compile time, while a wrong numeric mask or shift can compile successfully and surface only as broken hardware programming or misread status.

Related generated enum definitions exist outside this file for several fields, especially `DP_DPHY_SYM32_*` modes/status values and `AZALIA_F2_CODEC_*` converter format/digital-converter values. Those enums provide semantic values; this header provides the bit placement used to write or read those values.

Hardware-module integration spans multiple display subsystems:

- HPO DP stream/link/DPHY code consumes the `DP_SYM32_ENC3`, `DP_LINK_ENC*`, and `DP_DPHY_SYM32*` fields during link bring-up, stream enable/disable, training/test-pattern control, MST/SAT scheduling, CRC capture, and diagnostics.
- Display VM setup consumes the `DCHVM_*` masks for memory and RIOMMU control/status.
- VGA compatibility paths consume `SEQ*`, `CRT*`, `GRA*`, and `ATTR*` masks when legacy indexed VGA state must be programmed or preserved.
- Display audio/Azalia code consumes the F2 codec, descriptor, sink-info, CRC, stream, and F0 endpoint macros for HDMI/DisplayPort audio capabilities, stream configuration, status reporting, and latency/CRC diagnostics.

The offset header and this shift/mask header must be generated from the same register database. Cross-generation mixing with DCN 3.1, 3.0.x, or later ASIC headers is risky because names are similar but field layouts can diverge.

## Risks And Edge Cases

- The chunk starts mid-register. `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL8` has earlier shift fields in the previous chunk; this chunk begins at `GSP_TRIGGER_TRANSMISSION_DEADLINE_MISSED__SHIFT` and contains all masks for that register.
- The chunk ends mid-block. The `AZF0ENDPOINT0` F0 endpoint pin capability/register sequence continues in the next chunk, so this note should not be treated as a complete endpoint-0 analysis.
- Two HPO DPHY instances, `DP_DPHY_SYM320` and `DP_DPHY_SYM321`, repeat many field layouts. Generator drift or manual edits can be hard to spot because most lines differ only by instance number.
- Full-width masks such as CRC counts, custom test-pattern data, sink-description words, LPIB values, GTC deltas, latency counters, and stream-format bitmaps use `0xFFFFFFFFL`; consumers should avoid signed-width assumptions.
- Many fields are packed into high bits, including line-number fields at `0xFFFF0000L`, CRC/status bits, DPHY control bits, and VGA/Azalia configuration fields. Off-by-one shifts can corrupt unrelated control or status state.
- Capability, status, control, and reset fields use the same macro style. This header does not prevent writes to read-only/status fields or incorrect clear semantics.
- Azalia unsolicited-response, format-change, hot-plug, keepalive, LPIB snapshot, and latency-counter reset fields can affect event generation and diagnostics; incorrect programming may produce misleading audio hotplug or stream-position behavior.
- Legacy VGA indexed registers are included next to modern DCN/HPO/Azalia blocks. Consumers must use the correct indexed access path for the address block rather than assuming normal flat MMIO semantics.
- DPHY training pattern, symbol override, and CRC controls are diagnostic/link-training sensitive. Wrong masks can disrupt link training or make CRC diagnostics invalid while still compiling cleanly.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration oriented:

- Build AMDGPU display code for a DCN 3.1.2-enabled configuration to catch missing symbols in register helper expansion.
- Preprocess representative users of `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT` to confirm token concatenation resolves to the expected `DP_SYM32_ENC3`, `DP_LINK_ENC*`, `DP_DPHY_SYM32*`, `DCHVM`, VGA, and Azalia macros.
- Compare this slice against the matching DCN 3.1.2 offset header and AMD register database so every register comment has matching offsets and every field has the intended mask/shift pair.
- Exercise HPO DisplayPort link bring-up, link training, MST/SAT scheduling, stream enable/disable, sideband packet transmission, metadata/audio packet generation, panel replay, and CRC capture on DCN 3.1.2 hardware.
- Exercise HDMI/DisplayPort audio with format changes, multichannel and HBR modes, sink descriptor reads, hotplug, suspend/resume, LPIB snapshots, latency counters, and audio CRC paths.
- Verify VGA fallback/compatibility paths if the ASIC exposes those legacy indexed registers in the tested configuration.
- Pay special attention to boundary fields split across chunks: `GSP_CONTROL8` at the beginning and `AZF0ENDPOINT0` pin capability/pin control fields at the end.

## Open Cross-Chunk Questions

- The merge lane should combine this chunk with subset `subset-b-001822` to describe `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL8` as a complete register.
- The merge lane should combine this chunk with subset `subset-b-001824` to describe the complete `AZF0ENDPOINT0` F0 endpoint block.
- Whole-file analysis should reconcile generated DCN 3.1.2 register exposure with actual resource counts and product configurations, especially the number of HPO DP, Azalia endpoint, and stream instances that are live on a given ASIC.
