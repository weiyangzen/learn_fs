# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 37656-39874

## Purpose

This chunk is part of the generated AMD DCN 3.5.0 register shift/mask header used by the DRM AMD display driver. It does not implement executable control flow. Instead, it provides preprocessor constants that describe bit positions and bit masks for hardware register fields in several display blocks: display core performance monitors, Display Stream Compression block 3, Display Writeback, VPG generic packet generation, DisplayPort stream/symbol/link encoders, APG audio packet generation, DCHVM virtual memory control, and DP DPHY symbol32 controls.

The exported surface is the set of `#define` names following the register-field convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the already-shifted bit mask for that field.

Driver code combines these constants with generated register offsets from neighboring `*_offset.h`/`*_sh_mask.h` headers and common AMD display register macros to write, update, or read individual fields without hard-coding bit arithmetic at each call site.

## Macro Families In This Chunk

The chunk begins mid-register for `DC_PERFMON19_PERFCOUNTER_CNTL` and then defines complete field layouts for `DC_PERFMON19`, `DC_PERFMON20`, and `DC_PERFMON21` performance monitor instances. These macros cover performance counter event selection, counted value type, hardware stop selectors, count-off selectors, counter state selectors for counters 0 through 7, performance monitor state, report count, count-off interrupt enable/status/ack, clock enable, run-enable start/stop selection, counter interrupt status/ack bits, and low/high counter value reads.

The DSC portion describes `DSC_TOP3`, `DSCCIF3`, and `DSCC3` registers. It includes DSC top clock gates, DSCCIF input underflow recovery/status/interrupt fields, input pixel format and bits-per-component fields, picture width/height, DSCC slice layout, rate-control buffer model size, double-buffer pending status, overflow/underflow interrupt status and interrupt-enable bits for rate buffers and rate-control model buffers, many PPS configuration fields, memory power-control fields, squared-error and max-absolute-error readback fields, and maximum fullness counters.

The DWB section covers the Display Writeback pipe. It includes writeback enable and clock gates, memory power control for output FIFO and OGAM LUT memories, frame-capture mode/rate/crop/eye fields, crop/source/window dimensions, update lock/pending bits, CRC controls and masks, output format/denorm/min/max fields, MMHUBBUB backpressure counters, host read rate control, overflow status/counter fields, soft reset, gamut remap coefficients for RAM A/B, OGAM LUT access, OGAM mode, region control, start/end base/slope/offset controls for RAM A and RAM B, and HDR multiplier coefficient.

The VPG5 block defines generic packet controls for frame-update and immediate-update scheduling, packet access/data windows, generic packet lock/conflict status, VPG memory power state, ISRC data access, and MPEG info packet payload fields. The repeated `VPG_GENERIC0` through `VPG_GENERIC14` fields encode individual update request and pending bits in one register word.

The DP encoder area defines the first DisplayPort symbol32/stream/link encoder instance in this chunk. It includes symbol encoder enable/reset/status, video FIFO control, MSA double-buffering and MSA payload registers, pixel-format controls, SDP generic secondary-data-packet controls for GSP packet slots 0 through 14, SDP metadata packet controls, SDP audio controls, stream clock controls and ramp-adjuster FIFO status/control registers, input mux, audio control, link encoder clock control/spare, and DPHY symbol32 controls.

The tail of the chunk reaches `DP_DPHY_SYM320_DP_DPHY_SYM32_*` fields. These describe DPHY enable/reset/precoder/mode/lane control, status and pending update bits, SAT update controls, virtual-channel rate controls, SAT slot/source controls and status for VC0 through VC3, test-pattern selection and PRBS seeds, custom test-pattern payloads, DPHY error status bits, stream symbol override fields, and the first part of DPHY CRC configuration.

## Important APIs, Types, And Functions

There are no C functions, structs, enums, or inline helpers in this line range. The important API is the generated macro namespace consumed by C code elsewhere in the AMD display stack.

Important naming patterns:

- `DC_PERFMON19_*`, `DC_PERFMON20_*`, and `DC_PERFMON21_*` identify repeated performance monitor instances. The field layout is nearly identical across the instances, so users can share programming logic while substituting the instance-specific register macro names.
- `DSCC3_*`, `DSCCIF3_*`, and `DSC_TOP3_*` identify DSC engine instance 3 and its interface/top-level controls.
- `DWB_*` names describe Display Writeback programming, color processing, CRC, error, and memory-power registers.
- `VPG5_*` names describe generic packet generator instance 5.
- `DP_SYM32_ENC0_*`, `DP_STREAM_ENC0_*`, `DP_LINK_ENC0_*`, and `DP_DPHY_SYM320_*` describe DisplayPort output instance 0 in symbol32 mode.
- `APG0_*`, `DME5_*`, and `DCHVM_*` provide audio packet generator, DME, and display VM controls that integrate with the stream/output path.

Callers usually interact with these definitions through AMD register-access helpers such as register read/modify/write wrappers, field setter macros, or generated register tables in the DC resource code. Those helpers expect the `__SHIFT` and `_MASK` suffixes to be mechanically consistent.

## Control Flow And Runtime Behavior

This header chunk has no runtime branches, loops, calls, or side effects. Runtime control flow appears in the driver code that includes it. At that higher layer, the typical pattern is:

1. Select a hardware block instance and register address from generated offset tables.
2. Use this header's `__SHIFT` and `_MASK` values to compose a field value or extract a field from a read register word.
3. Program hardware by writing the containing register, often through a register-update macro that preserves unrelated fields.
4. Poll status or pending bits such as double-buffer pending, reset done, update pending, overflow status, interrupt status, rate/SAT pending, or conflict status.

The macro values encode the hardware contract that makes those operations correct. For example, double-buffer pending bits in DSCCIF/DSCC/DWB/DP symbol encoder blocks tell callers whether staged state has been latched, while interrupt status and ack masks define how error/overflow conditions are observed and cleared.

## State And Persistence Behavior

The file itself persists no software state. It represents persistent and transient hardware state fields in memory-mapped registers:

- Configuration state: clock enables, resets, pixel formats, DSC PPS values, DWB output formats, gamut/OGAM coefficients, DP SDP packet controls, MSA payloads, DPHY mode/lane controls, and virtual-channel rates.
- Latched or double-buffered state: update pending bits for DWB, DSC, VPG generic packets, DP MSA/pixel-format controls, and DP/DPHY SAT or rate updates.
- Status and error state: performance counter activity and values, underflow/overflow status, reset done/status, CRC values, backpressure counters, rate buffer fullness, DPHY error bits, VPG conflict status, and interrupt status/ack fields.
- Power-management state: memory power-force/disable/state fields for DSCC, DWB, VPG, DP symbol encoder memory, APG, DME, and DCHVM.

Because these masks are used for direct hardware programming, incorrect values can persist until the next register write, mode set, reset, or power-cycle depending on the affected block.

## Dependencies And Integration Points

This chunk depends on the AMDGPU DCN register-generation scheme. It is meaningful only when paired with:

- Register offset/address headers for DCN 3.5.0.
- AMD display register access helpers that consume `__SHIFT` and `_MASK` names.
- Block-specific DC code for DSC, DWB, VPG, DP stream/link/symbol encoding, APG audio packet setup, DCHVM, and performance monitoring.
- Hardware documentation or generator inputs that define the authoritative field positions for DCN 3.5.0 ASICs.

The integration points are mostly compile-time. If a C source includes this header and references one of these macros, the compiler substitutes the constants into register programming code. There is no link-time symbol from this chunk.

## Risks And Maintenance Notes

- This is generated hardware description data. Manual edits are high risk because a single wrong bit position can silently corrupt an unrelated field in a memory-mapped register.
- Several register names are repeated across numbered hardware instances. Copy/paste or generator bugs can produce instance-specific drift that compiles cleanly but targets the wrong hardware bit.
- The chunk starts in the middle of `DC_PERFMON19_PERFCOUNTER_CNTL` and ends in the middle of `DP_DPHY_SYM320_DP_DPHY_SYM32_CRC_CONFIG0`; complete review of both registers requires adjacent chunks.
- Large repeated layouts, especially `DWB_OGAM_RAMA/RAMB_REGION_*`, `VPG5_VPG_GSP_*`, and `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL*`, are easy places for off-by-one field numbering or mask/shift mismatch.
- Status/ack fields such as overflow, interrupt, conflict, reset, and pending bits may have write-one-to-clear or read-only semantics in hardware. The masks do not encode access type, so callers must rely on the register programming guide or higher-level driver conventions.
- Signed or packed coefficient fields such as gamut remap, OGAM bases/slopes/offsets, and DSC PPS ranges require callers to format values correctly before applying the mask.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, generator, and hardware integration checks:

- Build coverage for AMD display code that references DCN 3.5.0 DSC, DWB, VPG, DP encoder, APG, DCHVM, and perfmon macros.
- Generator diff checks against the upstream register database to confirm every `__SHIFT` has the expected paired `_MASK`, no fields are missing, and repeated instance layouts remain consistent.
- Static checks that each mask is compatible with its shift and field width, especially for multi-bit ranges such as DSC PPS values, DWB OGAM/gamut coefficients, VPG generic update bitmaps, DP SDP GSP controls, and DPHY VC rate controls.
- Mode-set and display validation on DCN 3.5.0 hardware using DSC, writeback, DP audio/SDP packets, panel replay/MSA changes, and DPHY symbol32 paths.
- Error-path tests or diagnostics for underflow/overflow interrupts, CRC readback, reset-done polling, update-pending polling, DPHY error reporting, VPG conflict handling, and performance counter readback.
- Power-management tests that toggle memory light-sleep/power fields and verify no hangs or stale pending bits across display enable, disable, suspend, resume, and hotplug flows.
