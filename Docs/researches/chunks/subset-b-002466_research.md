# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 42336-44165

## Scope

This chunk is the tail of the generated AMD GC 10.1.0 shift/mask register header. It contains only C preprocessor constants: each field has a `__SHIFT` value and a matching `__MASK` value used to pack or extract bitfields from GC 10.1/Navi10 graphics registers. There are no functions, structs, enums, variables, includes, locks, allocations, callbacks, or executable branches in this range.

The selected lines start inside the sample-delay register family, continue through the complete visible `sqind` wave-debug block, then cover the complete visible `didtind` dynamic throttling block for SQ, DB, TD, and TCP clients. The chunk ends at the file's closing `#endif`. Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata and is not Ceph filesystem code.

## Purpose

`gc_10_1_0_sh_mask.h` is generated hardware metadata for AMD's GC 10.1.0 graphics IP. Driver code includes it with `gc_10_1_0_offset.h` and, where needed, `gc_10_1_0_default.h` so register helpers can address a register and update only the intended field bits.

This chunk serves three main purposes:

- It defines sample-delay bit layouts for shader-engine and shader-array units, especially the tail of `SE_SA0...` entries and the `SE_SA1...` entries for SX, PA, GL1, CB, DB, SC, RMI, GL1C, and WGP-local TA/TD/TCP blocks. These registers expose a 6-bit `SAMPLEDELAY` field plus reserved upper bits.
- It defines indexed SQ wave debug/status layouts in the `sqind` address block. These describe a selected shader wave's mode, status, trap status, hardware identity, GPR/LDS allocation, instruction-buffer state, program counter, instruction word, scheduler mode, VGPR offset, trap temporaries, execution mask, scratch/XNACK state, and SQ interrupt payload words.
- It defines indexed DIDT/EDC layouts in the `didtind` address block for the shader queue/sequencer (`SQ`), depth buffer/backend (`DB`), texture data (`TD`), and texture cache processor (`TCP`) clients. These fields control dynamic inductive droop mitigation, energy/current-delta throttling, stall insertion, release timing, stall patterns, thresholds, weights, status, overflow, rolling power delta, PCC performance counters, and per-client stall event counters.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The important interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- The matching register addresses live in `gc_10_1_0_offset.h`, usually as `ix...` indexed-register constants for this chunk.
- Consumers normally combine these constants through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, wave indirect read helpers, and DIDT indirect register helpers.

The sample-delay family is repetitive and intentionally uniform. Each covered `*_SAMPLEDELAY` register defines `SAMPLEDELAY` at bits `[5:0]` and `RESERVED` at bits `[31:6]`. The names encode physical graphics topology: shader engine (`SE`), shader array (`SA0`/`SA1`), WGP instance, and sub-block (`TA`, `TD`, `TCP`, plus shared blocks like `SX`, `PA`, `CB`, `DB`, `SC`, `RMI`, and `GL1*`).

The SQ wave block includes these notable register groups:

- `SQ_DEBUG_STS_GLOBAL` and `SQ_DEBUG_STS_LOCAL`: global and local wave-debug status, including busy/valid/stall/debug indicators and per-resource status.
- `SQ_WAVE_MODE`, `SQ_WAVE_STATUS`, and `SQ_WAVE_TRAPSTS`: floating-point mode bits, exception enables, halt/trap/export/GPR state, privilege/debug state, and trap/event status.
- `SQ_WAVE_HW_ID_LEGACY`, `SQ_WAVE_HW_ID1`, and `SQ_WAVE_HW_ID2`: location and identity fields such as wave, SIMD, WGP/CU, shader array, shader engine, queue, vmid, state id, and wave age/id details.
- `SQ_WAVE_GPR_ALLOC` and `SQ_WAVE_LDS_ALLOC`: per-wave VGPR/SGPR/LDS allocation metadata.
- `SQ_WAVE_IB_STS`, `SQ_WAVE_IB_DBG1`, `SQ_WAVE_IB_STS2`, `SQ_WAVE_INST_DW0`, and `SQ_WAVE_FLUSH_IB`: instruction-buffer status, debug, instruction word, and flush controls.
- `SQ_WAVE_PC_LO`, `SQ_WAVE_PC_HI`, `SQ_WAVE_M0`, `SQ_WAVE_EXEC_LO`, `SQ_WAVE_EXEC_HI`, `SQ_WAVE_FLAT_SCRATCH_LO`, `SQ_WAVE_FLAT_SCRATCH_HI`, `SQ_WAVE_FLAT_XNACK_MASK`, and `SQ_WAVE_TTMP0` through `SQ_WAVE_TTMP15`: full-width `DATA` views of selected wave scalar/debug state.
- `SQ_INTERRUPT_WORD_AUTO`, `SQ_INTERRUPT_WORD_ERROR`, and `SQ_INTERRUPT_WORD_WAVE`: interrupt payload fields for thread-trace, WLT, buffer status, error type/detail, wave id, SIMD/WGP/SA/SE location, VMID, privilege, and encoding.

The DIDT block is organized as repeated register families for `DIDT_SQ_*`, `DIDT_DB_*`, `DIDT_TD_*`, and `DIDT_TCP_*`:

- `*_CTRL0`, `*_CTRL1`, `*_CTRL2`, `*_CTRL_OCP`, and `*_CTRL3`: enable/reset/force controls, threshold fields, max/min power fields, short/long intervals, OCP max power, throttle trigger bits, power-level selection, stall-pattern selection, and local/combined enable controls.
- `*_STALL_CTRL`, `*_TUNING_CTRL`, `*_STALL_AUTO_RELEASE_CTRL`, `*_STALL_RELEASE_CNTL0`, `*_STALL_RELEASE_CNTL1`, and `*_STALL_RELEASE_CNTL_STATUS`: stall insertion policy, high/low delay fields, tuning levels, auto-release timers, release allowance limits, and release-control FSM state.
- `*_STALL_PATTERN_1_2`, `*_STALL_PATTERN_3_4`, `*_STALL_PATTERN_5_6`, and `*_STALL_PATTERN_7`: packed stall-pattern bit sequences used by DIDT throttling.
- `*_MPD_SCALE_FACTOR` and `*_WEIGHT0_3`, `*_WEIGHT4_7`, `*_WEIGHT8_11`: power-delta scaling and per-level weighting fields.
- `*_EDC_CTRL`, `*_EDC_THRESHOLD`, `*_EDC_STALL_PATTERN_*`, `*_EDC_TIMER_PERIOD`, `*_THROTTLE_CTRL`, `*_EDC_STALL_DELAY_*`, `*_EDC_STATUS`, `*_EDC_OVERFLOW`, `*_EDC_ROLLING_POWER_DELTA`, and `*_EDC_PCC_PERF_COUNTER`: EDC enable/reset/stall policy, thresholds, timer periods, throttle source enables, per-subunit delay tables, FSM/throttle level status, overflow counters, rolling power delta, and PCC performance counts.
- `DIDT_SQ_STALL_EVENT_COUNTER`, `DIDT_DB_STALL_EVENT_COUNTER`, `DIDT_TD_STALL_EVENT_COUNTER`, and `DIDT_TCP_STALL_EVENT_COUNTER`: full-width stall event counters for each DIDT client.

The DIDT families are mostly symmetrical, but not byte-for-byte identical. For example, DB exposes only `DIDT_DB_EDC_STALL_DELAY_1` in this visible range, while SQ, TD, and TCP expose delay registers 1 through 3.

## Control Flow

This header has no runtime control flow. Its behavior is compile-time substitution of numeric constants.

The implied runtime flow is in AMDGPU consumers:

1. Include the GC 10.1.0 offset and shift/mask headers for the active ASIC generation.
2. Select a register address, often an indexed `ix...` register for `sqind` or `didtind` blocks.
3. Read the current register value through the relevant SOC15, wave-indirect, or DIDT-indirect access path.
4. Use `__MASK` and `__SHIFT` constants, usually through a helper macro, to extract status fields or compose a read-modify-write update.
5. Sequence any enable/reset/stall/calibration/debug operation in higher-level GFX, KFD, debug, or power-management code.

For SQ wave state, consumers select a wave context and read the indexed registers for diagnostics, debug dumps, trap handling, or fault reporting. For DIDT/EDC state, power-management or initialization code programs thresholds, patterns, delays, and enables, then may poll status/counters. This header does not define selection order, polling timeouts, reset ordering, interrupt behavior, or read/write side effects.

## State And Persistence Behavior

The macros themselves are stateless and do not persist anything. They describe fields in GPU hardware registers.

Sample-delay registers are hardware configuration state for sampled signals across graphics pipeline sub-blocks. Their values are likely retained until graphics IP reset, ASIC reset, suspend/resume reinitialization, power-gating loss, firmware reprogramming, or explicit driver writes. The reserved bits must be preserved unless the hardware guide says otherwise.

SQ wave registers are volatile views of selected shader-wave state. Values can change as waves execute, stall, trap, flush, terminate, or are inspected by debug hardware. Many fields represent live status or debug windows rather than durable software-owned configuration.

DIDT and EDC registers hold hardware throttling policy and counters. Configuration fields may persist until reset or reprogramming; status, overflow, rolling-power, performance-counter, and stall-event fields are hardware-updated and may be sticky, clear-on-write, clear-on-read, saturating, or freely running depending on the register. The shift/mask header does not encode those access semantics, so consumers must rely on the register specification and established driver sequences.

## Dependencies And Integration Points

This chunk depends on the generated GC 10.1.0 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h` supplies matching register addresses such as `ixSQ_WAVE_MODE`, `ixSQ_INTERRUPT_WORD_ERROR`, `ixDIDT_SQ_CTRL0`, `ixDIDT_DB_CTRL0`, `ixDIDT_TD_CTRL0`, and `ixDIDT_TCP_CTRL0`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_default.h` supplies default/reset values for the same late `sqind` and `didtind` register families.
- AMDGPU GC 10.1 code, KFD queue/MQD code, GFXHUB v2.0 code, and Navi-family initialization code include this header as part of the ASIC register description.
- Register helper macros and indirect register accessors provide the actual MMIO/indexed-register read/write mechanism.

Integration points include shader wave dumps, trap/fault diagnostics, KFD/compute queue debugging, SQ interrupt decoding, graphics power management, droop-aware throttling, current/energy-delta throttling, performance counter collection, GPU reset restore paths, and suspend/resume or power-gating reinitialization. Older power-management code in the tree demonstrates the same DIDT/EDC pattern by reading `DIDT_TCP_EDC_CTRL`, updating fields such as `EDC_EN` and `EDC_SW_RST`, and writing the indexed register back.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong mask or shift compiles cleanly but can update the wrong hardware field, producing subtle shader-debug, interrupt-decoding, throttling, or performance behavior.
- This range begins mid-sample-delay family. Earlier `SE_SA0...` sample-delay entries are in the previous chunk, so final file-level research should merge adjacent chunks before claiming complete topology coverage.
- The `sqind` and `didtind` registers are indexed windows. Using the right field constants with the wrong selected wave, instance, client, or indirect address can return plausible but incorrect data.
- SQ wave fields are often live hardware state. Reading during wave scheduling, trap handling, reset, or GPU hang recovery can race with hardware changes and produce transient values.
- DIDT/EDC control fields are performance and reliability sensitive. Incorrect enable/reset/force-stall/throttle policy writes can cause unnecessary throttling, unstable power behavior, misleading counters, or workload-specific performance regressions.
- Repeated DIDT prefixes invite copy/paste mistakes. SQ, DB, TD, and TCP fields are similar but represent different hardware clients, and DB has fewer EDC stall-delay registers in this chunk.
- Reserved and unused fields appear throughout. Full-register writes that do not preserve reserved bits may alter undocumented hardware behavior.
- The header does not communicate access type. Some fields that look writable by name may be read-only status, self-clearing pulses, write-one-to-clear bits, hardware-owned counters, or sticky overflow indicators.
- Some interrupt and identity fields span high bits or encode several IDs in one register. Consumers must use the matching mask width and avoid signed or truncated intermediate values.

## Test Signals

Useful validation is mostly build, generated-data consistency, and hardware integration:

- Kernel build coverage for AMDGPU/KFD files that include `gc_10_1_0_sh_mask.h`, especially GC 10.1, GFXHUB v2.0, queue/MQD, and debug paths.
- Static comparison against AMD's authoritative generated GC 10.1.0 register database to confirm each `__SHIFT` and `__MASK` value and each register family's presence.
- Cross-checks that every register field in this chunk has a matching address macro in `gc_10_1_0_offset.h` and, where available, a default value in `gc_10_1_0_default.h`.
- Mechanical checks for mask/shift consistency: masks should align to shifts, repeated sample-delay registers should preserve the 6-bit `SAMPLEDELAY` layout, and repeated DIDT client families should match except for documented hardware omissions.
- Shader debug, trap, thread-trace, wave-dump, and GPU fault tests that exercise `SQ_WAVE_*` and `SQ_INTERRUPT_WORD_*` decoding.
- Power-management stress tests on GC 10.1/Navi10 hardware that exercise graphics load transitions, over-current or power-brake behavior, EDC/PCC controls, suspend/resume, GPU reset, and DIDT counter readback.
- Performance regression tests for shader, depth/backend, texture-data, and texture-cache-heavy workloads, since DIDT mistakes can present as unexpected throttling rather than functional failure.
- Runtime warning signals include bad wave IDs or PC values in debug dumps, incorrect SQ interrupt error decoding, GPU hang recovery regressions, persistent EDC overflow, unexpected stall event counts, thermal/power throttling anomalies, or workload-specific performance drops after DIDT programming changes.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002466`. It covers lines 42336-44165 and ends the source file. The final per-file research should merge this with earlier chunks for the complete `gc_10_1_0_sh_mask.h` register map, especially the preceding sample-delay entries and any earlier GC register families outside this tail segment.
