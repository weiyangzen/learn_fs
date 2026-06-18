# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 19738-22220

## Purpose

This chunk is a middle slice of AMD's generated GC 11.5.0 shift/mask register-field header. It has no executable C logic; it exports preprocessor constants that describe bit positions and bit masks for graphics-core MMIO register fields. Driver code pairs these macros with the matching GC 11.5.0 register offset header and AMDGPU register helper macros to pack, unpack, and update individual fields in hardware registers.

The requested range contains 2,160 `#define` entries: 1,081 `__SHIFT` macros and 1,079 `_MASK` macros. The chunk boundary starts inside `CB_COLOR7_VIEW` and ends inside `SPI_RESOURCE_RESERVE_CU_2`, so a few field pairs are intentionally split with adjacent chunks. The content spans the tail of color-buffer render-target metadata, then several GC address blocks covering command processor controls, GRBM, PA/SC rasterizer and binning controls, shader/SQ state, CP queue debug state, DIDT/EDC throttling, SPI/TCP/GDS/UTCL1/GCR controls, CAC/EDC power accounting, and the beginning of SPI per-CU resource reservation fields.

Although the repository path is under a local `ceph-client` source tree, this file is AMDGPU hardware metadata and does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field.
- `<REGISTER>__<FIELD>_MASK`: mask used to isolate or preserve a field.

The main register families in this range are:

- `CB_COLOR*`: color-buffer target fields for `CB_COLOR7_VIEW`, `CB_COLOR7_INFO`, `CB_COLOR7_ATTRIB`, `CB_COLOR7_FDCC_CONTROL`, DCC base extension fields for targets 0-7, and `ATTRIB2`/`ATTRIB3` geometry and swizzle metadata for color targets 0-7.
- `CP_MEC_CNTL`, `CP_ME_CNTL`, `CP_FETCHER_SOURCE`, and `CP_HPD_*`: command processor micro-engine controls, halt/reset and clock-gating controls, high-priority dispatch ROQ offsets, and HPD queue status/force/freeze fields.
- `GRBM_GFX_CNTL` and `GRBM_NOWHERE`: graphics register bus manager instance selection and nowhere-routing fields used by low-level register access paths.
- `PA_SC_*` and `PA_PH_*`: primitive assembly, scan converter, variable-rate shading, primitive binning, FIFO sizing, event controls, perf counters, screen trap locks, and out-of-order/PBB enhancement knobs.
- `SQ_*` and `SH_MEM_*`: shader runtime/debug status, shader memory bases/configuration, trap base address and memory address fields.
- `DIDT_*`, `GC_EDC_*`, `GC_THROTTLE_*`, `PCC_*`, and `PWRBRK_*`: dynamic inductive/droop thermal controls, energy droop control thresholds, stall patterns, hysteresis, throttle sources, status, overflow, rolling power delta, and performance counters.
- `SPI_*`, `PC_CONFIG_*`, and `SPI_COMPUTE_WF_CTX_SAVE_STATUS`: shader processor interface debug stalls/traps, arbitration and resource limits, primitive control configuration, compute wavefront context-save busy bits across pipes and queues, and per-CU resource reservation fields.
- `TCP_*`, `GDS_*`, `UTCL1_*`, `GCR*`: texture cache invalidation/status/cntl fields, GDS clock-gating restore controls, UTCL1 control and FIFO sizing, GCR target disable, cache/TLB command status, credits, and spare fields.
- `GC_CAC_*`, `SE_CAC_*`, and numerous `*_CAC_WEIGHT_*` registers: global and shader-engine CAC windows, aggregate counters, indirect index/data accessors, and subsystem-specific weighting fields for CP, EA, UTCL2, GDS, GL2C, SDMA, SQ, TCP, CB, DB, PA, SC, SPI, and related blocks.

Several names include `MASK` as part of the hardware field name, such as `GC_EDC_CTRL__THROTTLE_SRC0_MASK__SHIFT` paired with `GC_EDC_CTRL__THROTTLE_SRC0_MASK_MASK`. Consumers must treat the full macro spelling as generated ABI rather than applying ad hoc suffix parsing.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from AMDGPU code that includes this generated header:

1. GC 11.5.0 initialization code selects register offset, shift, and mask tables for the ASIC.
2. Register-list macros token-paste symbolic register and field names into helper calls or table initializers.
3. Runtime paths use AMDGPU helpers to read, write, or update MMIO registers while applying these masks and shifts.
4. Hardware blocks then interpret the programmed values for render-target setup, rasterization/binning behavior, queue management, shader debugging, cache/TLB invalidation, throttling, and power/accounting controls.

The macros do not encode sequencing, access permissions, side effects, reset values, or read/write legality. Consumers still need hardware-specific ordering around CP queue changes, GRBM instance selection, cache invalidation, CAC/EDC/throttle programming, shader trap setup, suspend/resume restore, and reset recovery.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes hardware state held in GC 11.5.0 registers:

- Color-buffer state for target format, view, DCC/FDCC compression, base extension, dimensions, swizzle mode, resource type, and DCC pipe alignment.
- PA/SC state for variable-rate shading feedback, PBB/binning, out-of-order scan conversion, FIFO sizing, wave ID tables, event masks, and perf counters.
- SQ/SPI/PC state for debug stalls, trap enablement, shader memory base/configuration, resource limits, wave context-save status, and primitive/attribute flow control.
- CP and HPD queue state for micro-engine control, queue availability, fetch/MQD activity, pending transfer size, force/freeze controls, and ROQ offsets.
- Cache and translation state for TCP invalidation, UTCL1 controls, GCR target disable/status, TLB shootdown, request credits, and error status.
- Power and reliability state for DIDT, EDC, PCC, PWRBRK, CAC windows, aggregate counters, weight registers, throttle status, overflow counters, and stretch/performance counters.

Persistence is defined by the hardware block and power domain. Many configuration fields persist until modeset, engine reinitialization, power-gating, suspend/resume, GPU reset, or ASIC reset. Status and counter fields may be read-only, sticky, write-one-to-clear, self-clearing, saturating, indirect-indexed, or only valid while related clocks are active. This header does not mark those semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated GC 11.5.0 register database and must stay synchronized with the companion offset and default-value headers for the same ASIC family, especially:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h`, which provides matching register offsets.
- Other generated `gc_11_5_0_*` headers that describe default values or field values where present.
- AMDGPU GC, CP, RLC, MEC, KFD, power-management, reset, debug, and performance-monitoring code that builds register tables or direct register helper calls from these macro names.
- Firmware and microcode interfaces for CP/MEC/HPD queues, DIDT/EDC throttling, CAC accounting, and cache/TLB control, where driver-visible register programming must match firmware expectations.

The most behaviorally sensitive integration points are render-target programming (`CB_COLOR*`), rasterizer/binning configuration (`PA_SC_*`), queue/debug controls (`CP_*`, `SQ_*`, `SPI_*`), cache/TLB invalidation and target disable (`TCP_*`, `UTCL1_*`, `GCR*`), and thermal/power throttling (`DIDT_*`, `GC_EDC_*`, `GC_CAC_*`, `SE_CAC_*`).

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong mask or shift can compile successfully while programming the wrong MMIO bits.
- Manual edits are high risk because this generated file must match AMD's authoritative register database, the offset header, firmware assumptions, and silicon behavior.
- The chunk has artificial boundaries. `CB_COLOR7_VIEW__SLICE_START__SHIFT` is before this range while its mask is inside it, and `SPI_RESOURCE_RESERVE_CU_2` continues after line 22220.
- Some generated field names contain `MASK` before the suffix. Tools that strip `_MASK` or `__SHIFT` naively can report false mismatches or generate wrong field names for `GC_EDC_CTRL__THROTTLE_SRC*_MASK`.
- Repeated register families invite single-instance generator errors. `CB_COLOR0-7`, `PA_SC_BINNER_EVENT_CNTL_0-3`, CAC weight families, and `SPI_RESOURCE_RESERVE_CU_*` should be checked per instance, not assumed correct from one representative.
- Side-effect-sensitive status/control fields can cause hangs, interrupt storms, bad queue state, or broken reset recovery if consumers confuse read-only status, write-one-to-clear status, force/freeze controls, or clock-gating overrides.
- Power/throttle fields can affect stability and performance. Incorrect DIDT, EDC, PCC, PWRBRK, CAC, or stall-pattern fields may over-throttle, under-throttle, misreport counters, or break firmware-mediated power management.
- Cache/TLB and target-disable fields are correctness-sensitive. Wrong `GCR_CMD_STATUS`, UTCL1, TCP invalidation, or target disable masks can leave stale translations/cache lines or incorrectly disable shader-engine/GL2 targets.

## Test Signals

Useful validation signals include:

- Build AMDGPU with GC 11.5.0 support enabled. Missing or renamed macros should fail where GC 11.5 register tables and helper calls reference these fields.
- Mechanically compare this range against the authoritative AMD generated register database and the matching `gc_11_5_0_offset.h` register names.
- Run a shift/mask pairing check that understands fields whose generated names already contain `MASK`, and allow the expected chunk-boundary splits at `CB_COLOR7_VIEW` and `SPI_RESOURCE_RESERVE_CU_2`.
- Exercise graphics workloads that stress MRT color targets, DCC/FDCC compression, mips/array slices, MSAA fragments, PBB/binning, VRS, primitive discard/null primitive paths, and out-of-order scan conversion.
- Exercise compute and queue paths through KFD/AMDGPU: queue create/destroy, preemption, context save/restore, CP/MEC reset, MQD fetch, and debug halt/freeze paths.
- Validate cache/TLB behavior under VM faults, eviction, TLB shootdowns, GPU reset, suspend/resume, and heavy memory pressure.
- Monitor power-management and telemetry behavior for DIDT/EDC/PCC/PWRBRK/CAC counters, throttle status, overflow counters, and performance regressions under thermal or power-limit stress.
- Watch kernel logs, GPU reset traces, debugfs/sysfs telemetry, perf counters, and hang reports for invalid register programming, stuck busy bits, queue state mismatches, cache invalidation failures, or unexpected throttling.

## Cross-Chunk Notes

This is not the whole `gc_11_5_0_sh_mask.h` file. Earlier chunks contain the header guard, many preceding GC register families, and the first part of `CB_COLOR7_VIEW`. Later chunks continue `SPI_RESOURCE_RESERVE_CU_2` and the rest of the GC 11.5.0 generated shift/mask namespace. The final per-file research document should synthesize all chunks before making whole-file claims about complete register coverage or all GC 11.5.0 integration points.
