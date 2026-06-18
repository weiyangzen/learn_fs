# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 49894-52359

## Purpose

This chunk is generated AMD DCN 4.2.0 register-field metadata. It contains only C preprocessor constants for hardware bit positions and masks; it does not implement executable driver logic. AMDGPU display code combines these `...__SHIFT` and `..._MASK` constants with the matching DCN 4.2.0 register offsets to pack, extract, preserve, clear, or update individual MMIO fields through common register helpers.

The requested range contains 2,121 `#define` lines: 1,062 shift macros and 1,059 mask macros across 307 register-like macro groups. The shift/mask imbalance is caused by the range ending inside `DP_STREAM_ENC1_DP_STREAM_ENC_CLOCK_RAMP_ADJUSTER_FIFO_STATUS_CONTROL1`; the remaining three masks for that register are on lines 52360-52362, immediately after this chunk. The first included register, `DSCC3_DSCC_PPS_CONFIG6`, is complete in this range, although its comment line is immediately before the chunk at line 49893.

Although the source path sits under a local `ceph-client` mirror, this header is AMDGPU display hardware metadata, not Ceph or distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, allocations, locks, or includes in this range. The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset used to encode or decode a hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate, clear, preserve, or update that field.

Major register families covered in this chunk:

- `DSCC3_DSCC_*`: tail of DSC compressor 3 picture-parameter-set metadata, memory power controls, compression quality/error counters, output and rate-buffer fullness telemetry, and test/debug index/data registers. PPS fields include DSC version-adjacent rate-control values such as BPG offsets, initial/final offsets, flatness QP limits, RC model size, buffer thresholds, and 15 range min-QP/max-QP/BPG-offset entries.
- `DC_PERFMON20_*` and `DC_PERFMON21_*`: display performance monitor counter selection, counter-control, counter-state, perfmon control, interrupt/status/mask fields, and high/low counter-value access. `DC_PERFMON20` is under the DSC3 perfmon address block; `DC_PERFMON21` is under the writeback perfmon block.
- `DWB_*` and `FC_*`: writeback top-level clock/memory power, frame-composition mode/flow/window/source-size controls, update and CRC controls, CRC masks/values, output control, MMHUBBUB backpressure counting, host-read control, overflow status/counter, soft reset, debug controls, HDR multiplier, gamut remap modes and coefficients, output gamma controls, OGAM LUT index/data/control, and OGAM RAM A/B start/end/offset/region programming.
- `DCHVM_*`: display client HVM control, clock control, memory control, RIOMMU control, and RIOMMU status fields.
- `DP_STREAM_ENC0_*` and beginning of `DP_STREAM_ENC1_*`: HPO DisplayPort stream encoder clock gating/status, pixel/audio input muxes, APG clock enable, clock-ramp-adjuster FIFO control/status, FIFO level calibration fields, and spare fields. The `DP_STREAM_ENC1` FIFO status/control1 group is partial at the chunk boundary.
- `APG5_*`: audio packet generator debug audio generation and APG memory power fields for stream encoder 0.
- `DME5_*`: data mapper engine control and memory control fields, including enable/reset-style control fields and low-power memory controls.
- `VPG5_*`: video packet generator generic packet access/data, generic stream packet frame-update and immediate-update controls, generic status, memory power, and ISRC1/2 packet access/data fields.
- `DP_SYM32_ENC0_*`: HPO DP 32-symbol encoder controls for video FIFO, MSA double buffering, pixel format, MSA payload fields, HBLANK behavior, generic SDP/GSP controls 0-14, audio SDP controls, metadata packet control, MSA/VBID/stream/panel-replay controls, video CRC control/results/status, symbol counting, ALPM sleep/wake/request/ready/hardware-mode/status/start/interrupt fields, memory power control, and spare fields.
- `DP_LINK_ENC0_*`: HPO DP link encoder clock control and spare fields.
- `DP_DPHY_SYM320_*`: HPO DP DPHY/SYM32 control and status, SAT update and virtual-channel rate control/status, eDP mode and ASSR seeds, ALPM sleep/wake/control parameters, test-pattern configuration and PRBS/custom pattern data, error-status bits, and symbol/cycle counting controls.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code:

1. DCN 4.2.0 source files include `dcn_4_2_0_sh_mask.h` together with `dcn_4_2_0_offset.h`.
2. Resource, DMUB, GPIO, DWB, HPO DP, DSC, and packet-generator code builds register tables by token-pasting symbolic register names with matching offset, shift, and mask macros.
3. Runtime paths call register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, and poll/wait variants.
4. The constants in this chunk determine which bits those helpers touch while programming DSC PPS/rate-control state, writeback capture and color processing, performance counters, HPO DP stream/link/symbol encoders, packet generators, DPHY/SAT/eDP/ALPM state, and related debug or status registers.

The macros do not encode ordering rules. Consumers must still follow hardware sequencing for DSC enable and PPS load, writeback clock and memory power-up, LUT and gamma programming, update latching, CRC/overflow status handling, DP stream encoder FIFO reset/calibration, VPG packet update timing, MSA/SDP/VBID programming, DPHY virtual-channel setup, ALPM entry/exit, and interrupt/status acknowledgement.

## State And Persistence Behavior

This chunk stores no mutable software state and persists nothing to disk. It describes hardware-backed register state in DCN 4.2.0 display blocks:

- DSC compressor state: PPS and rate-control fields configure how DSCC3 compresses a stream, while quality/error/fullness/debug counters expose compressor health and diagnostics.
- Performance monitor state: counter-selection, enable, overflow, interrupt, and value fields are live hardware telemetry controlled by perfmon programming.
- Writeback state: DWB/FC fields configure capture dimensions, source and output routing, CRC masking/readback, overflow tracking, backpressure counts, host reads, soft resets, gamut remap matrices, HDR multiplier, and OGAM LUT/RAM state.
- Power and clock state: `*_MEM_PWR*`, clock-control, APG, DME, VPG, stream encoder, symbol encoder, DPHY, and HVM fields can control or reflect power-gated or clock-gated domains.
- DisplayPort packet and stream state: HPO stream encoder, VPG, DP SYM32, link encoder, and DPHY fields control stream source muxes, audio source muxes, generic packets, SDP/GSP timing, MSA/pixel format/VBID, video CRC, symbol counters, virtual-channel rates, eDP ASSR, ALPM, and test patterns.
- Diagnostic state: debug buses, counters, CRC results, overflow flags, symbol counts, DPHY error bits, FIFO calibration/status, and SAT virtual-channel status are readback-oriented or event/status-oriented fields.

Persistence is hardware-defined. Values may survive only until modeset, stream disable/enable, writeback disable, display block reset, GPU reset, suspend/resume, firmware reinitialization, or clock/power gating. Status and event fields can be read-only, sticky, self-clearing, write-one-to-clear, or valid only while their block clock is active. The generated shift/mask header does not distinguish configuration fields from status, write-clear, or latch-trigger fields; consuming code and the hardware programming guide must supply those semantics.

## Dependencies And Integration Points

This chunk must remain synchronized with AMD's generated DCN 4.2.0 register database and the matching offset/base-index definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h`.

Direct inclusion points found in this source tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_factory_dcn42.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_translate_dcn42.c`

Functional integration points include:

- DSC programming paths that construct PPS register writes and read compressor error/fullness telemetry.
- DWB and color-management paths, including generic DWB register definitions in `display/dc/dwb/dcn30/dcn30_dwb.h` and OGAM programming in `display/dc/dwb/dcn30/dcn30_dwb_cm.c`.
- HPO DP stream encoder code that uses stream encoder field lists such as `DP_STREAM_ENC_CLOCK_EN` in `display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h`.
- VPG/APG/DME packet and audio-data paths for generic stream packets, ISRC packets, audio packet generation, and data mapping.
- DP SYM32/DPHY/link encoder paths that program MSA, SDP, VBID, CRC, symbol-count, ALPM, SAT virtual-channel, eDP ASSR, and test-pattern behavior.
- Perfmon and diagnostic tooling that reads display counter, CRC, overflow, FIFO, symbol-count, DPHY error, and debug-bus fields.

The critical ABI is the macro name and numeric value. Register-helper tables rely on exact symbolic spellings such as `DWB_OGAM_RAMA_REGION_0_1__DWB_OGAM_RAMA_EXP_REGION0_LUT_OFFSET_MASK` or `DP_STREAM_ENC0_DP_STREAM_ENC_CLOCK_CONTROL__DP_STREAM_ENC_CLOCK_EN__SHIFT`, while the paired offset header supplies the register address and base index.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong hardware bits.
- This is generated metadata. Manual edits risk divergence from AMD's source register database, the paired offset header, firmware expectations, and silicon documentation.
- The range ends inside `DP_STREAM_ENC1_DP_STREAM_ENC_CLOCK_RAMP_ADJUSTER_FIFO_STATUS_CONTROL1`. Complete validation for that register requires the three following mask lines outside this chunk.
- Many blocks are instance-sensitive. `DSCC3`, `DC_PERFMON20/21`, `APG5`, `DME5`, `VPG5`, `DP_STREAM_ENC0/1`, `DP_SYM32_ENC0`, `DP_LINK_ENC0`, and `DP_DPHY_SYM320` prefixes must match the intended hardware instance; a copied macro with the wrong instance can target a plausible but unrelated register.
- Writeback color processing is highly table-sensitive. Bad OGAM region, offset, base, slope, or gamut-remap masks can produce subtle color, HDR, or capture-output corruption rather than an obvious failure.
- DSC PPS/rate-control fields are stream-format sensitive. Incorrect BPG, QP, threshold, offset, or model-size masks can cause visible compression artifacts, underflow, or link-bandwidth mismatches.
- Clock, memory-power, reset, FIFO, and calibration fields often require strict sequencing and polling. Correct masks used in the wrong order can leave DWB, packet, stream encoder, or DPHY blocks inactive or partially calibrated.
- Status and interrupt fields can be sticky or write-clear. Bad masks can clear unrelated error bits, miss overflow/CRC/FIFO/ALPM events, or report stale diagnostics.
- DPHY SAT/eDP/ALPM/test-pattern fields affect link-layer behavior and may fail only for specific panels, link rates, MST/SST topologies, power states, or compliance-test modes.
- High-bit masks such as `0x80000000L` should be handled with unsigned-safe register operations by consumers.

## Test Signals

Useful validation combines generated-header consistency checks with hardware-facing display tests:

- Build AMDGPU display support with DCN 4.2.0 enabled. Missing or renamed macros should fail in DMUB, resource, GPIO, DWB, HPO DP, DSC, packet-generator, or register-table code.
- Mechanically verify that each complete register field in the chunk has one `__SHIFT` and one `_MASK`, allowing the expected boundary exception for `DP_STREAM_ENC1_DP_STREAM_ENC_CLOCK_RAMP_ADJUSTER_FIFO_STATUS_CONTROL1`.
- Diff this slice against AMD's authoritative DCN 4.2.0 register database and against nearby generated DCN headers where layout compatibility is expected.
- Exercise DSC-enabled display modes across bpp, slice sizes, native 4:2:0/4:2:2, suspend/resume, modeset, and link retraining; watch for compressor underflow, quality/error counters, rate-buffer fullness, and visible artifacts.
- Exercise DWB capture with scaling/window/source-size changes, CRC generation, overflow/backpressure monitoring, host reads, gamut remap, HDR multiplier, and OGAM LUT/RAM programming; compare captured color output and CRC/error counters.
- Exercise HPO DP stream encoder and DP SYM32 paths across hotplug, MST/SST where supported, audio packets, generic SDP/GSP metadata, MSA/pixel-format changes, VBID, panel replay, ALPM, and video CRC.
- Exercise DPHY/eDP/SAT behavior with ASSR, ALPM sleep/wake, virtual-channel rate fields, symbol/cycle counters, PRBS/custom test patterns, and error-status readback.
- Monitor kernel logs, DCN debug traces, register dumps, perfmon counters, CRC results, FIFO status, DPHY error status, symbol counters, overflow counters, and visual/audio output for stuck status bits, wrong channel routing, missed packet updates, color corruption, or resume-only failures.

## Cross-Chunk Notes

The previous line, 49893, contains the comment for `DSCC3_DSCC_PPS_CONFIG6`; all six shift/mask definitions for that register are included in this chunk. The following lines 52360-52362 contain the remaining `FIFO_MAXIMUM_LEVEL`, `FIFO_CAL_AVERAGE_LEVEL`, and `FIFO_CALIBRATED` masks for `DP_STREAM_ENC1_DP_STREAM_ENC_CLOCK_RAMP_ADJUSTER_FIFO_STATUS_CONTROL1`, followed by `DP_STREAM_ENC1_DP_STREAM_ENC_SPARE`. The final per-file report should reconcile this boundary before making complete claims about every `DP_STREAM_ENC1` stream-encoder register in `dcn_4_2_0_sh_mask.h`.
