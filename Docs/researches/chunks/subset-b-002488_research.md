# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 30094-32558

## Purpose

This chunk is a middle slice of AMD's generated GC 10.3.0 shift/mask register-field header. It contains no executable C logic; it exports preprocessor constants that describe bit positions and masks for graphics core MMIO register fields. Driver code combines these constants with the companion GC 10.3.0 offset header to pack, unpack, and update individual fields through AMDGPU register helper macros.

The requested range contains 2,149 `#define` entries: 1,080 `__SHIFT` macros and 1,069 `_MASK` macros. The imbalance is an artificial chunk-boundary artifact: this slice ends after the first eleven `RLC_PG_CNTL` shift definitions, while the remaining `RLC_PG_CNTL` shifts and all `RLC_PG_CNTL` masks continue after line 32558.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU hardware metadata for GC/GFX blocks. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, allocation paths, or locks in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset used when constructing or decoding a register value.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate, clear, or preserve that field during register reads and writes.

The major register families in this range are:

- Shader/graphics-block performance counters: `SQ_PERFCOUNTER_CTRL`, `SQ_PERFCOUNTER_CTRL2`, and repeated `*_PERFCOUNTER*_SELECT`, `*_SELECT1`, `*_MODE`, `*_CFG`, and `*_RSLT_CNTL` families for `GCEA`, `SX`, `GDS`, `TA`, `TD`, `TCP`, `GL2C`, `GL2A`, `GL1C`, `CHC`, `CHCG`, `CB`, `DB`, `RMI`, `GCR`, `UTCL1`, `PA_PH`, `GL1A`, `CHA`, and `GUS`.
- Color/depth block filtering: `CB_PERFCOUNTER_FILTER` provides per-shader-engine/shader-array and windowing fields used to constrain CB performance-counter collection.
- RLC streaming performance monitor and accumulator control: `RLC_SPM_PERFMON_CNTL`, ring base high/low, ring size, segment sizes, ring read/write pointers, mux-select address/data registers, skew/sample-delay controls, accumulator data/control RAM address/data windows, `RLC_SPM_ACCUM_STATUS`, `RLC_SPM_ACCUM_CTRL`, `RLC_SPM_ACCUM_MODE`, thresholds, requested sample counts, 32-bit counter regions, virtualization pause/status, and GFX clock high/low counters.
- RLC perfmon and IOV performance plumbing: `RLC_PERFMON_CNTL`, `RLC_PERFCOUNTER[0-1]_SELECT`, `RLC_GPU_IOV_PERF_CNT_*`, and `RLC_PERFMON_CLK_CNTL`.
- VM L2 and GC UTCL2 performance counters under `addressBlock: gc_gcvml2pldec`: `GCMC_VM_L2_PERFCOUNTER[0-7]_CFG`, `GCMC_VM_L2_PERFCOUNTER_RSLT_CNTL`, `GCUTCL2_PERFCOUNTER[0-3]_CFG`, and `GCUTCL2_PERFCOUNTER_RSLT_CNTL`.
- GCVML2 perfs decoder fields under `addressBlock: gc_gcvml2perfsdec`: `GCVML2_PERFCOUNTER2_[0-1]_SELECT`, matching `SELECT1`, and `MODE` registers.
- Four SDMA performance-counter blocks under `gc_sdma0_sdma0perfsdec` through `gc_sdma3_sdma3perfsdec`: each has `SDMAx_PERFCNT_PERFCOUNTER[0-1]_CFG`, result control, misc control, and repeated `SDMAx_PERFCOUNTER[0-1]_SELECT/SELECT1` fields.
- RTAVFS control under `addressBlock: gc_grtavfsdec`: register address/data windows, read data, control/status, target frequency/voltage, soft reset, PSM control, and clock control.
- RLC core control under `addressBlock: gc_rlcdec`: `RLC_CNTL`, F32 microcode version, busy/status bits, memory sleep control, SMU/RLCV safe-mode handshakes, RLCV command, reference-clock timestamp, GPM timers, legacy interrupts, CP/RLC interrupt status, load-balance counters/control, MGCG control, GPU clock counters, GPM thread reset, CP DMA completion bits, RLCG doorbell control/status/data, CGTT/MGCG override, 32-bit GPU clock select/value, and the beginning of `RLC_PG_CNTL`.

## Control Flow

This header has no runtime control flow. It participates in runtime behavior through generated register access patterns:

1. GC 10.3.0-capable AMDGPU code includes `gc_10_3_0_offset.h` and this shift/mask header.
2. Register table macros and helper calls token-paste register and field names into offset, shift, and mask constants.
3. Runtime code reads or writes GC MMIO registers using helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, and block-specific wrappers.
4. Hardware-side sequencing is handled by consumers, not by this header: consumers must program counter selectors before enabling counters, configure SPM rings before sampling, poll status before consuming results, clear interrupt bits with the right semantics, and coordinate RLC/SMU/power-management handshakes with the relevant clocks and power domains active.

The chunk therefore describes field layout, not policy. It does not encode which registers are read-only, write-one-to-clear, self-clearing, privileged, clock-gated, or safe to access only in a particular IP state.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes hardware state in GC 10.3.0 registers:

- Performance-counter selection state, including event selectors, selector banks, counter modes, performance modes, compare modes/values, enable bits, clear bits, start/stop triggers, and saturation behavior.
- Shader-stage and pipe gating for SQ counters via `SQ_PERFCOUNTER_CTRL`, including per-stage enables for PS/VS/GS/ES/HS/LS/CS, counter rate, flush behavior, and per-ME/pipe disable bits.
- SPM ring and accumulator state, including ring base/size/read/write pointers, per-SE/global segment sizing, mux selector RAM windows, sample-delay/skew fields, accumulated sample counts, done/overflow/armed/in-progress bits, strobe controls, automatic accumulation/SPM modes, and virtualization pause status.
- VM L2, UTCL2, GCVML2, and SDMA performance-counter configuration and result-control state.
- RTAVFS state for indirect register access, target frequency/voltage, reset, PSM, and clock-control behavior.
- RLC firmware and control state, including enable/step/cache-disable bits, F32 thread microcode versions, busy flags, memory light/deep sleep timing, SMU/RLCV safe-mode command/response fields, timestamps, timers, load-balance counters, MGCG settings, clock counters, thread reset, CP DMA completion flags, doorbell mode/data/status, CGTT/MGCG overrides, and early power-gating fields.

Persistence is hardware-defined. Configuration fields usually persist until driver reprogramming, power-gating, suspend/resume, GPU reset, or ASIC reset. Status and interrupt fields may be transient, sticky, sampled, self-clearing, or write-one-to-clear depending on the underlying register. The generated shift/mask header does not document those access semantics.

## Dependencies And Integration Points

This chunk must remain synchronized with AMD's generated GC 10.3.0 register database and with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h`, which supplies the matching MMIO offsets.

Direct include users in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`, which includes the GC 10.3.0 offset and shift/mask headers for SMU/power-management interactions on VanGogh-class hardware.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c`, which includes this shift/mask header for shared SDMA register-field handling.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`, which includes GC 10.3.0 offsets and masks for KFD/GFX v10.3 integration.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`, which includes GC 10.3.0 register metadata for SDMA v5.2 programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`, which includes GC 10.3.0 metadata for GFXHUB/VM-related register access.

The strongest behavioral integration points for this specific chunk are GPU profiling/performance monitoring, SDMA performance-counter programming, VM/GFXHUB performance diagnostics, RLC SPM capture, RLC firmware/status polling, RLC/SMU power-management handshakes, clock/power-gating control, and RLCG doorbell handling.

## Risks And Edge Cases

- These constants are untyped preprocessor values. A wrong shift or mask can compile cleanly while touching the wrong MMIO bits, corrupting adjacent fields, missing interrupts, breaking power management, or producing invalid performance data.
- The file is generated metadata. Manual edits can diverge from AMD's authoritative register database, the matching offset header, firmware expectations, and ASIC documentation.
- Repeated perf-counter families are easy to validate incompletely. `SDMA0` working does not prove `SDMA1-3`; one `GL2*`/`GL1*`/`CH*` instance can carry a generator error while sibling blocks appear correct.
- Counter fields have width and mode differences. Some selectors carry four events through `SELECT`/`SELECT1`, while other counters expose fewer selector fields; generic setup code must not assume every block has the same arity.
- SPM and accumulator controls are sequencing-sensitive. Starting sampling before the ring base/size, segment sizes, mux selectors, delays, and accumulator mode are coherent can produce overflows, stale samples, bad write pointers, or stuck in-progress status.
- RLC control, safe-mode, timer, interrupt-clear, thread-reset, and power-gating fields may have side effects. Using masks without respecting required handshakes can hang RLC firmware, race SMU coordination, lose timer interrupts, or destabilize clock/power transitions.
- Doorbell and indirect data registers carry full 32-bit payloads. Incorrect low/high ordering or stale valid bits can mis-handle RLCG messages.
- The chunk ends inside `RLC_PG_CNTL`; any per-file merge must join the next chunk before making complete claims about RLC power-gating fields.

## Test Signals

Useful validation combines generated-header checks with hardware behavior:

- Build AMDGPU with GC 10.3.0, SDMA v5.2, GFXHUB v2.1, KFD GFX v10.3, and VanGogh SMU paths enabled. Missing or renamed macros should fail at compile time in direct include users and any register-table construction that references these fields.
- Mechanically verify that every field in lines 30094-32558 has a matching `__SHIFT` and `_MASK` pair where expected, while allowing the known chunk-boundary exception for the partial `RLC_PG_CNTL` group.
- Diff this range against AMD's authoritative GC 10.3.0 register database and neighboring generated GC/GFX10 headers where layouts are expected to match.
- Exercise GPU performance monitoring through perf/debug tooling on GC 10.3.0 hardware, covering SQ stage enables, CB/DB filters, GL1/GL2/cache counters, VM L2/UTCL2 counters, and counter start/stop/clear/saturation behavior.
- Exercise SDMA performance counters on all four SDMA instances, not only SDMA0, and compare selected events with expected DMA workload changes.
- Validate RLC SPM capture by programming ring base/size, segment sizing, mux selectors, sample intervals, accumulator mode, and then checking write-pointer movement, sample counts, done bits, overflow bits, and pause/resume behavior.
- Run suspend/resume, GPU reset, clock-gating, power-gating, and SMU/RLC safe-mode paths while watching for RLC busy bits that never clear, timer/interrupt storms, bad load-balance counters, broken doorbell status, or power-gating regressions.

## Cross-Chunk Notes

This slice starts immediately after the `SQ_PERFCOUNTER15_SELECT` group began in an earlier chunk and ends inside `RLC_PG_CNTL`. The final per-file research document should merge adjacent chunks before making whole-file claims about all SQ performance-counter selectors or the complete RLC power-gating register layout.
