# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 30050-32601

## Purpose

This chunk is generated AMD GC 11.0.0 register bitfield metadata. It contains no executable C code; it exports preprocessor `__SHIFT` and `_MASK` constants used by AMDGPU and AMDKFD code to compose, preserve, write, and decode memory-mapped graphics-core registers for this ASIC generation. The companion register-address definitions live in `gc_11_0_0_offset.h`.

The selected range is centered on graphics-core performance-monitoring registers. It starts in the tail of the `gc_gfxdec` performance counter data registers, switches into the `gc_perfsdec` address block, and then defines selector/control fields for command-processor, GRBM, geometry, rasterizer, shader, cache, texture, GDS, GCEA, and thread-trace performance facilities. The path is under a Ceph source mirror, but this file is AMD GPU hardware metadata rather than filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, callbacks, locks, allocations, or direct MMIO operations in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a register field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register mask for that field.
- Callers combine these macros with `reg*`/`mm*` address macros from `gc_11_0_0_offset.h` and low-level helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `REG_GET_FIELD`, `REG_SET_FIELD`, or equivalent register programming helpers.

Major register groups in this chunk:

- Counter value registers: low/high 32-bit halves for many performance counters, including `GE2_DIST`, `GE2_SE`, `PA_SU`, `PA_SC`, `SPI`, `PC`, `SQ`, `SQG`, `SX`, `GCEA`, `GDS`, `TA`, `TD`, `TCP`, `GL2C`, `GL2A`, `GL1C`, `CHC`, `CHCG`, `CB`, `DB`, `RLC`, `RMI`, `GCR`, `PA_PH`, `UTCL1`, `GL1A`, `GL1H`, `CHA`, and `GUS`. Most expose full-width `PERFCOUNTER_LO` or `PERFCOUNTER_HI` masks.
- Command-processor performance selection: `CPG_PERFCOUNTER*_SELECT`, `CPC_PERFCOUNTER*_SELECT`, and `CPF_PERFCOUNTER*_SELECT` fields select event IDs and counter modes, with `SPM_MODE` fields for streaming performance monitoring paths.
- Global performance monitor control: `CP_PERFMON_CNTL` defines `PERFMON_STATE`, `SPM_PERFMON_STATE`, `PERFMON_ENABLE_MODE`, and `PERFMON_SAMPLE_ENABLE`.
- CP windowing and latency selectors: `CPF_TC_PERF_COUNTER_WINDOW_SELECT`, `CPG_TC_PERF_COUNTER_WINDOW_SELECT`, `CPC_TC_PERF_COUNTER_WINDOW_SELECT`, and the corresponding `*_LATENCY_STATS_SELECT` registers define index, enable, clear, and always-on bits for transaction counter windows and latency-stat windows.
- Draw-window counters: `CP_DRAW_OBJECT`, `CP_DRAW_OBJECT_COUNTER`, `CP_DRAW_WINDOW_MASK_HI`, `CP_DRAW_WINDOW_HI`, `CP_DRAW_WINDOW_LO`, and `CP_DRAW_WINDOW_CNTL` define draw/object counting and window enable/clear/object filters.
- GRBM selectors: `GRBM_PERFCOUNTER0_SELECT`, `GRBM_PERFCOUNTER1_SELECT`, per-shader-engine selectors `GRBM_SE0_PERFCOUNTER_SELECT` through `GRBM_SE6_PERFCOUNTER_SELECT`, and high selector registers expose event selection plus many busy/clean user-defined mask bits for DB, CB, geometry, texture, shader, scan converter, PA, RLC, BCI, TCP, UTCL1, GL1, SEDC, and RMI style blocks.
- Per-block performance counter selectors: repeated `*_PERFCOUNTERn_SELECT` and `*_SELECT1` layouts for `GE1`, `GE2_DIST`, `GE2_SE`, `PA_SU`, `PA_SC`, `SPI`, `PC`, `SQ`, `SQG`, `SX`, `GDS`, `TA`, `TD`, `TCP`, and the start of `GL2C`. These expose event slots (`PERF_SEL`, `PERF_SEL1`, `PERF_SEL2`, `PERF_SEL3`) and counter/performance modes (`CNTR_MODE`, `PERF_MODE`, `PERF_MODE1`, `PERF_MODE2`, `PERF_MODE3`).
- TCP filtering: `TCP_PERFCOUNTER_FILTER`, `TCP_PERFCOUNTER_FILTER2`, and `TCP_PERFCOUNTER_FILTER_EN` define texture-cache performance-filter fields for buffer/flat/dimensional operations, data and number formats, swizzle mode, sample count, opcode type, GLC/SLC, compression, and address mode matching.
- SQ/SQG controls: `SQ_PERFCOUNTER_CTRL`, `SQG_PERFCOUNTER_CTRL`, `SQ_PERFCOUNTER_CTRL2`, `SQG_PERFCOUNTER_CTRL2`, and `SQG_PERF_SAMPLE_FINISH` expose shader-stage enables, ME/pipe disable masks, force-enable/VMID-enable controls, and sample-finish status.
- Shader thread trace: `SQ_THREAD_TRACE_BUF0_BASE/SIZE`, `SQ_THREAD_TRACE_BUF1_BASE/SIZE`, `SQ_THREAD_TRACE_CTRL`, `SQ_THREAD_TRACE_MASK`, `SQ_THREAD_TRACE_TOKEN_MASK`, `SQ_THREAD_TRACE_WPTR`, `SQ_THREAD_TRACE_STATUS`, `SQ_THREAD_TRACE_STATUS2`, draw/marker counters, and `SQ_THREAD_TRACE_DROPPED_CNTR` define buffer placement, trace capture mode, token filtering, selected SIMD/WGP/SA/wave types, write pointer state, ownership/busy/error status, buffer-full/lost-packet flags, and trace accounting counters.
- GCEA result/control registers: `GCEA_PERFCOUNTER2_SELECT`, `GCEA_PERFCOUNTER2_SELECT1`, `GCEA_PERFCOUNTER2_MODE`, `GCEA_PERFCOUNTER0_CFG`, `GCEA_PERFCOUNTER1_CFG`, and `GCEA_PERFCOUNTER_RSLT_CNTL` select GCEA events and configure/clear performance result handling.

The requested line range ends at `GL2C_PERFCOUNTER0_SELECT1__PERF_MODE3__SHIFT`; the corresponding `GL2C_PERFCOUNTER0_SELECT1` masks are immediately after the chunk boundary and must be covered by the next chunk.

## Control Flow

This header chunk has no runtime control flow. Runtime behavior comes from GC 11 driver code that includes the generated offset and mask headers:

1. A GC 11.0.0 consumer includes `gc/gc_11_0_0_offset.h` and `gc/gc_11_0_0_sh_mask.h`.
2. The consumer selects the register address from the offset header and the field layout from this mask header.
3. It builds register values with shifts/masks or decodes readback values from MMIO.
4. AMDGPU/AMDKFD register helpers perform the actual direct or indexed register access while the relevant GFX, KFD, RLC, MES, debug, profiling, or firmware path owns sequencing.

The chunk describes how performance counters, filters, thread-trace buffers, and performance control/status registers are encoded. It does not describe when profiling can be enabled, how counters are reserved between clients, how power-gated blocks are awakened, or which writes are safe while the GPU is executing. Those rules live in the consuming driver code, firmware contracts, and hardware programming guide.

## State And Persistence Behavior

The file stores no software state and persists nothing. It only names bit ranges for hardware state.

The hardware state represented here is mostly profiling and debug state:

- Counter data registers hold live or latched low/high counter values for many graphics sub-blocks.
- Selector registers persist chosen event IDs and counter modes until reset, power transition, or reprogramming.
- `CP_PERFMON_CNTL` controls global perfmon/SPM enable and sample state.
- CP draw-window and latency selectors gate what draws, windows, and latency-stat buckets are counted.
- GRBM selectors and user-defined busy masks influence global-busy performance observations.
- TCP filters restrict texture/cache performance events to matching request attributes.
- SQ/SQG controls select shader stages, VMIDs, and ME/pipe participation in shader performance sampling.
- SQ thread-trace buffer registers hold GPU buffer base/size, write pointer, capture mode, token inclusion/exclusion, and status/error/full/lost-packet indicators.
- GCEA registers select and control geometry/command-engine-adjacent counter result handling.

Persistence is hardware-defined. Some fields are ordinary configuration, some are read-only counters or status, some are clear/enable bits, and some can be sticky until explicitly cleared or until reset. The macros alone do not identify access type, reset value, side effects, or ownership, so callers must preserve unrelated bits and follow hardware-specific ordering.

## Dependencies And Integration Points

The direct companion dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h`, which supplies the matching register offsets and base indices. Pairing this mask file with another generation's offset header is unsafe even when names overlap.

Observed GC 11.0.0 include users in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v11.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_display.c`

Integration points include GFX 11 initialization, KFD debug/profiling support, MES scheduling interaction, RLC/IMU golden-register programming, performance counter reservation and sampling, shader thread tracing, GPU reset/recovery, suspend/resume, runtime power management, and hardware validation. Related semantic definitions for thread-trace token types and modes appear in generation-wide enum headers, while this chunk supplies the GC 11.0.0 register packing.

## Risks And Edge Cases

- Header/offset mismatch is the main correctness risk. These names are similar across GC generations, but field widths and bit positions can change.
- The macros are untyped integer constants. Misusing a mask with the wrong register can compile cleanly while corrupting profiling control or decoding the wrong hardware state.
- Many counter data registers use `0xFFFFFFFFL` full-width masks. Those often represent readback counters, not safe whole-register write values.
- Low/high counter halves can race with live counter increments. Consumers that need coherent 64-bit values may need hardware latching, stop/sample controls, or retry logic outside this header.
- Selector registers pack several event slots and modes into one word. Whole-register writes can unintentionally change another selected event, mode, SPM setting, or reserved field.
- `CP_PERFMON_CNTL` and SQ/SQG control bits affect global profiling state. Incorrect sequencing can disturb other profiling clients, lose samples, or leave counters enabled during reset/power transitions.
- Thread-trace buffer base/size fields are hardware-facing GPU addresses and sizes. Incorrect address alignment, size encoding, double-buffer configuration, or VMID selection can lead to lost packets, write errors, full buffers, or traces owned by the wrong VMID.
- `SQ_THREAD_TRACE_STATUS`/`STATUS2` fields include busy, owner, write-error, buffer-full, packet-lost, and buffer-issue indicators. Ignoring those fields can make trace data look valid when it is incomplete.
- TCP filter fields are split between value registers and enable bits. Programming only the filter value or only the enable mask can yield unexpectedly broad or narrow sampling.
- GRBM and per-SE masks expose a large number of user-defined busy-mask bits. Incorrect masks can make global-busy metrics misleading and hide or exaggerate unit activity.
- The chunk boundary cuts through `GL2C_PERFCOUNTER0_SELECT1`; the masks for the final four shift fields are outside this work item. Merge/reconciliation must combine adjacent chunks for a complete per-file view.

## Test Signals

Useful validation is mostly build coverage, generated-header consistency, and hardware/profiling behavior:

- Build coverage for GC 11 AMDGPU, AMDKFD, MES, IMU, SOC21, and display paths that include `gc_11_0_0_sh_mask.h`.
- Generated-header checks that every field has coherent shift/mask pairs, masks do not overlap within a register except documented aliases, and every register in this chunk has a matching offset entry in `gc_11_0_0_offset.h`.
- Static checks that code uses the GC 11.0.0 offset and mask headers together and does not combine same-named fields from older `gc_9_*`, `gc_10_*`, or `gca/gfx_*` headers.
- Performance-counter smoke tests that program representative CP, GRBM, SQ/SQG, SPI, PC, TCP, GDS, and cache counter selectors, run known workloads, stop/sample counters, and verify nonzero/plausible low/high readback.
- Coherency tests for low/high counter reads under load, especially where counters can roll over while being sampled.
- TCP filter tests that toggle individual filter-enable bits and verify matching workloads affect only the intended filtered counters.
- Shader thread-trace tests that program buffer base/size, trace masks, token masks, double-buffer/high-water controls, collect traces, and assert that status/error/full/lost-packet fields match the captured data.
- Reset, suspend/resume, and runtime power-management tests while profiling or thread tracing is active, checking that counters are disabled or restored according to driver policy and do not hang after recovery.
- Regression signals include saturated or permanently zero counters, bad high/low counter stitching, unexpected `SQ_THREAD_TRACE_STATUS` write errors, buffer-full/lost-packet flags during small traces, VMID ownership mismatches, profiling interference between clients, and hangs isolated to GC 11 performance-monitoring paths.
