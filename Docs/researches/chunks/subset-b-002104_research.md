# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 37643-39861

## Purpose

This chunk is a generated AMD DCN 3.5.1 shift/mask header segment. It has no executable code; it supplies compile-time bit positions and masks for display-core hardware registers consumed by AMDGPU/DC register access macros. The covered lines span several display output blocks: DC performance monitors 19-21, DSC compressor instance 3, DWB frame capture/writeback and output gamma, display host VM controls, HPO DisplayPort stream/link/PHY encoders, APG audio packet generator 0, DME metadata engine 5, and VPG generic/video packet generator 5.

The chunk begins in the middle of `DC_PERFMON19_PERFCOUNTER_CNTL`: only the tail masks for that register are present here, while its shifts and earlier masks are in the previous chunk. It ends in the middle of `DP_DPHY_SYM320_DP_DPHY_SYM32_CRC_CONFIG0`: the remaining CRC mask fields continue after this chunk.

## Important macros and register fields

- `DC_PERFMON19_*`, `DC_PERFMON20_*`, and `DC_PERFMON21_*` describe display-core performance monitor units. Each complete perfmon block has counter control selection, counted-value type and stop/source controls, eight packed counter-state fields, perfmon run/control interrupt fields, counter-value interrupt/status/ack fields, and low/high readback fields. These are the field surfaces used when selecting events, starting/stopping counters, reading counter values, and acknowledging perf counter interrupts.
- `DSC_TOP3_*`, `DSCCIF3_*`, and `DSCC3_*` define DSC compressor instance 3 control. The fields cover DSC clock enable/gating, input-interface underflow recovery/status, input pixel format and bits per component, picture dimensions, slice layout, rate-control buffer model size, double-buffer pending status, overflow/underflow interrupt enables, PPS payload registers 0-22, memory power control, squared/max error readbacks, and rate-buffer fullness watermarks.
- `DWB_*` and `FC_*` define the display writeback path. They cover DWB enable and clock gating, output FIFO and OGAM LUT memory power, frame-capture mode/rate/window/source geometry, update lock/pending state, CRC controls/results/masks, output formatting and denorm/min/max controls, MMHUBBUB backpressure counters, host read rate control, overflow status/counters, soft reset, gamut remap coefficients, and large output-gamma programming state for RAM A and RAM B.
- `DCHVM_*` describes display host VM integration: host VM init request, display/DCF clock gating controls, clock-request modes, fine-grain clock-gating repeat disable, GPUVM retention memory power controls, RIOMMU prefetch request/power status, RIOMMU active state, and prefetch-done status.
- `DP_STREAM_ENC0_*`, `DP_SYM32_ENC0_*`, `DP_LINK_ENC0_*`, and `DP_DPHY_SYM320_*` describe HPO DisplayPort stream/link/PHY encoder instance 0. The fields cover stream encoder clocks and input muxes, clock-ramp FIFO calibration/status, DP symbol encoder reset/enable, video FIFO, MSA double buffering and payload fields, pixel format, HBLANK control, SDP/GSP slots 0-14, audio SDP controls, metadata packet control, MSA/VBID/stream/panel replay controls, video CRC, symbol encoder memory power, link encoder clocking, DPHY enable/reset/precoder/mode/lane count, stream VC rates, slot-allocation-table controls/status, test pattern and PRBS/custom symbols, error status, symbol override, and the start of CRC config.
- `APG0_*` defines audio packet generator 0: reset/done, APG enable and DP audio stream ID, debug generator controls, ACP/audio-info source selection, audio CRC control/result, audio/HBR/FIFO status, output-active status, memory power state, and spare bits.
- `DME5_*` and `VPG5_*` define metadata and video packet generation for stream path 5. DME fields select the HUBP requestor and stream type, enable metadata, expose double-buffer pending/taken status, and clear missed/taken flags. VPG fields cover generic packet data access, generic packet frame/immediate update controls for many packet slots, generic status, memory power, ISRC data, and MPEG info-frame payload bytes.

## Control flow and usage model

There is no direct control flow in this header. Runtime code includes this ASIC-specific generated header together with the matching offset header, builds register field tables with macros such as `SE_SF`, `SF_DWB2`, or similar AMDGPU/DC helpers, and then uses `REG_UPDATE`, `REG_GET`, and related wrappers to encode or decode the bit fields.

The effective runtime pattern is:

1. DCN 3.5.1 resource initialization selects this shift/mask header and the corresponding register offsets for the active ASIC.
2. Block-specific code initializes structures for perfmon, DSC, DWB, HPO DP stream/link encoders, APG, DME, and VPG instances.
3. Driver code writes packed register values by shifting field values and applying the generated masks, normally preserving unrelated bits through read/modify/write helpers.
4. Hardware state is observed by reading status, pending, interrupt, CRC, overflow, FIFO, memory-power, or error fields through the same masks.

The key dynamic flows represented by this chunk are DSC programming before enabling compressed output; DWB capture setup, update locking, CRC collection, and overflow handling; HPO DP stream/link enablement with MSA/SDP/audio metadata programming; APG audio packet generation; VPG/DME metadata packet dispatch; and perfmon counter selection/readback around diagnostic or profiling paths.

## State and persistence behavior

The macros themselves hold no state. State lives in DCN hardware registers and follows display hardware lifetime rules: it may persist across normal modeset operations until explicitly reprogrammed, but can be reset by GPU reset, display IP reset, power-gating transitions, suspend/resume, or stream teardown/recreate paths.

Several fields represent latched or clear-on-write-style hardware state rather than durable configuration. Examples include perf counter interrupt status/ack bits, DSC overflow/underflow status bits, DWB overflow flags and counters, APG audio CRC done/clear and FIFO overflow clear bits, DME metadata-taken/missed clear bits, VPG update pending/taken status, DP symbol/DPHY error status, and CRC done/value fields. Memory-power state fields in `DSCC3`, `DWB`, `DCHVM`, `APG0`, `DME5`, and `DP_SYM32_ENC0` reflect power-management state machines and should not be treated as ordinary software-owned storage.

Double-buffered fields matter in DSC, DWB, DP symbol encoder MSA/pixel format, DME, and VPG paths. Programming order must account for update lock, update pending, and taken/pending flags so hardware observes a coherent packet, timing, or color-processing configuration.

## Dependencies and integration points

- Depends on the matching DCN 3.5.1 offset/register headers for addresses such as `regDWB_ENABLE_CLK_CTRL`, `regDSCC3_DSCC_PPS_CONFIG*`, `regDP_SYM32_ENC0_*`, and `regDP_DPHY_SYM320_*`. This file only supplies field encodings.
- Integrates with AMDGPU display register helper macros, especially the generated mask/shift table patterns used by DWB (`dcn30_dwb`/`dcn35_dwb`), HPO DP stream/link encoder code (`dcn31`/`dcn32` HPO headers), audio/APG, VPG/DME, DSC, and perfmon code.
- Sits under `drivers/gpu/drm/amd/include/asic_reg/dcn`, making it ASIC/IP-version-specific generated data. Neighboring DCN versions repeat many layouts, so cross-version comparisons are useful but must not replace the DCN 3.5.1 source of truth.
- Touches externally visible display behavior: DSC compression packets, DP stream timing/metadata/audio SDPs, writeback capture output, CRC diagnostics, and power/clock gating.

## Risks and edge cases

- Chunk-boundary incompleteness: `DC_PERFMON19_PERFCOUNTER_CNTL` and `DP_DPHY_SYM320_DP_DPHY_SYM32_CRC_CONFIG0` are split across adjacent chunks. Any generated-header audit must reconcile the neighboring lines before deciding a field set is missing.
- Packed-register corruption: most registers combine unrelated bit fields. Full-register writes or wrong masks can corrupt reserved bits, interrupt a double-buffered update, or change hardware-owned status bits.
- Width and encoding mistakes: PPS DSC fields, DP MSA/VC-rate/SAT fields, DWB geometry, OGAM region descriptors, APG/VPG payload bytes, and perfmon selectors have narrow bit widths. Callers must clamp or validate values before shifting.
- Ordering hazards: DSC, DP stream encoder, VPG, DME, and DWB update paths use pending/taken/status bits. Writing payload data without respecting update or reset sequencing can produce torn packets, stale metadata, bad compression state, or link training/display artifacts.
- Power-management interactions: memory power force/disable/status and clock-gating bits can hide bugs, increase power draw, or make reads unreliable if accessed while a block is gated or powered down.
- Diagnostic-only fields are hardware-sensitive: CRC, test pattern, PRBS, symbol override, perfmon, and DPHY error controls can disturb normal DP output if enabled unintentionally.

## Test signals

- Build coverage with DCN 3.5.1 enabled should catch missing or renamed field macros in consumers that instantiate register tables for DSC, DWB, HPO DP, APG, DME, VPG, and perfmon blocks.
- Header consistency checks should compare split boundary registers with adjacent chunks and compare repeated instances (`DC_PERFMON19/20/21`, DWB OGAM RAM A/B regions, VPG packet slot fields, DP SDP GSP controls 0-14) for expected identical layouts.
- Runtime display tests should exercise DP link bring-up, HPO stream enable/disable, modesets, panel replay paths, DSC on/off modes, audio over DP, metadata packet transmission, and writeback capture.
- Status-path tests should read and clear DWB overflow, APG FIFO overflow/audio CRC done, DME missed/taken, DP DPHY error, CRC done/value, and perfmon interrupt status fields to verify ack/clear semantics.
- Power tests should cover suspend/resume, display idle, clock-gating toggles, and memory power transitions while checking that DWB, APG, DME, DCHVM, DSCC, and DP symbol encoder status fields settle as expected.
- Visual and protocol validation should include DSC sink compatibility, DP MSA correctness, SDP/GSP/audio packet observation where tooling is available, and DWB CRC/readback comparison against known frames.
