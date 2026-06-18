# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 27456-30093

## Scope

This chunk is a generated AMDGPU ASIC register bitfield header slice for GC 10.3.0. It covers the tail of a GUS SDP tag-reserve register, the remaining GUS/GL1/CH/GL2 control and status fields in this region, a large set of graphics-core performance counter data registers, VM L2 and SDMA performance counter data registers, and the beginning of the performance-counter selector block through `SQ_PERFCOUNTER15_SELECT`.

The source is declarative C preprocessor data only. It exports `*_SHIFT` and `*_MASK` constants used by AMDGPU register access helpers to encode and decode fields in MMIO register values.

## Purpose

The definitions in this chunk let AMDGPU code manipulate individual fields in GC 10.3.0 registers without hard-coding bit positions at call sites. The covered registers fall into several functional groups:

- GUS/SDP fabric credits, request policy, latency sampling, error status, L1 traffic counters, floating-point atomic logging, and write-response FIFO thresholding.
- GL1/CH/GL2 cache and channel control, arbitration status, burst/pipe steering, invalidation/reset controls, metadata/compression behavior, address match controls, and load-balance counters.
- Performance counter readback registers for command processor, GRBM, geometry, primitive assembly, shader processor, shader queue, texture/cache, color/depth, RLC, RMI, UTCL, GCR, SDMA, and VM L2 blocks.
- Performance counter select/control registers that choose events, counter modes, SPM modes, latency stat indexes, draw windows, and busy-mask qualification for the same hardware blocks.

## Important Exports

This chunk contributes 2,119 `#define` entries. Each register field follows the local generated naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit index.
- `<REGISTER>__<FIELD>_MASK` gives the already-shifted field mask.

Representative control/status exports include:

- `GUS_SDP_VCC_RESERVE0/1` and `GUS_SDP_VCD_RESERVE0/1`: 6-bit virtual-channel credit reservations, with `DISTRIBUTE_POOL` in the `*_RESERVE1` registers.
- `GUS_SDP_REQ_CNTL`: request pass-predicate overrides for reads, writes, atomics, DRAM chaining, and inner-domain mode.
- `GUS_MISC`, `GUS_MISC2`, `GUS_MISC3`: arbitration priority, link manager timing, early SDP behavior, L1/perf masks, FP atomic enable/logging, and clock-gating related bits.
- `GUS_LATENCY_SAMPLING` and `GUS_ERR_STATUS`: sampler selection for DRAM/IO/read/write/atomic/VC traffic and SDP response/error status bits including clear and busy-on-error controls.
- `GL1C_STATUS`, `GL1C_UTCL0_CNTL2`, `GL1C_UTCL0_STATUS`, `GL1C_UTCL0_RETRY`: GL1 cache/UTCL status, fault/retry/PRT detection, invalidation, snoop, page-size, and clock-gating controls.
- `CH_ARB_CTRL`, `CH_DRAM_BURST_CTRL`, `CHC_CTRL`, `CHC_STATUS`, `CHCG_CTRL`, `CHCG_STATUS`: channel arbitration, burst gathering controls, cache/client controls, protection fault handling, and status.
- `GL2C_CTRL`, `GL2C_CTRL2`, `GL2C_WBINVL2`, `GL2C_SOFT_RESET`, `GL2C_CM_CTRL1`: GL2 cache/coherency, writeback/invalidate completion, reset halting, compression/metadata, prefetch, arbitration, and volatile-mode controls.
- `GL2_PIPE_STEER_0/1`, `GL1_PIPE_STEER`, `CH_PIPE_STEER`: pipe-to-channel steering bitfields.

Representative performance counter exports include:

- `*_PERFCOUNTER*_LO` and `*_PERFCOUNTER*_HI` readback registers across CP (`CPG`, `CPC`, `CPF`), `GRBM`, `GE1`, `GE2_DIST`, `GE2_SE`, `PA_SU`, `PA_SC`, `SPI`, `SQ`, `SX`, `GCEA`, `GDS`, `TA`, `TD`, `TCP`, `GL2C`, `GL2A`, `GL1C`, `CHC`, `CHCG`, `CB`, `DB`, `RLC`, `RMI`, `UTCL1`, `GCR`, `PA_PH`, `GL1A`, `CHA`, and `GUS`.
- `GCMC_VM_L2_PERFCOUNTER_*`, `GCUTCL2_PERFCOUNTER_*`, and `GCVML2_PERFCOUNTER2_*` for VM L2 performance readback.
- `SDMA0` through `SDMA3` `PERFCNT_PERFCOUNTER_*` and `PERFCOUNTER0/1_*` readback registers.
- `CPG/CPC/CPF_*_SELECT`, `GRBM_*_SELECT`, `GE1/GE2_*_SELECT`, `PA_SU/PA_SC_*_SELECT`, `SPI_*_SELECT`, and `SQ_PERFCOUNTER0_SELECT` through the `SQ_PERFCOUNTER15_SELECT` marker for selecting counted events and modes.

## Address Blocks And Boundaries

The chunk starts at line 27456 inside the previous GUS group with only `GUS_SDP_TAG_RESERVE1__VC7_MASK`; the corresponding comment and other fields are in the previous chunk. It then defines 48 additional GUS registers before explicit address blocks begin.

Address blocks visible in this chunk:

- `gc_gl1dec`: 7 GL1/GL1C registers.
- `gc_chdec`: 12 CH/CHA/CHC/CHCG registers.
- `gc_gl2dec`: 23 GL2C/GL2A pipe, address-match, cache, reset, and load-balance registers.
- `gc_perfddec`: 267 performance-counter data/readback registers.
- `gc_gcvml2prdec`: 4 VM L2/UTCL2 performance readback registers.
- `gc_gcvml2perfddec`: 4 additional GCVML2 performance counter data registers.
- `gc_sdma0_sdma0perfddec`, `gc_sdma1_sdma1perfddec`, `gc_sdma2_sdma2perfddec`, `gc_sdma3_sdma3perfddec`: 6 performance readback registers per SDMA engine.
- `gc_perfsdec`: 97 performance selector/control registers in this slice, ending at the `SQ_PERFCOUNTER15_SELECT` comment on line 30093.

The chunk ends before the `SQ_PERFCOUNTER15_SELECT` field macros, which begin on line 30094, and before `SQ_PERFCOUNTER_CTRL`. A merge pass must treat `SQ_PERFCOUNTER15_SELECT` as split across chunks.

## Control Flow

There is no runtime control flow in this header. Control flow is imposed by external AMDGPU code that:

1. Reads or constructs a 32-bit register value.
2. Uses `FIELD_PREP`, `REG_SET_FIELD`, `REG_GET_FIELD`, or equivalent AMDGPU bitfield helpers with these masks and shifts.
3. Writes the encoded value to a GC 10.3.0 MMIO register or decodes readback/status/performance data.

For counters, a common external flow is: program a `*_SELECT` register, enable/control the perfmon state, sample or stop the counter, then read paired `*_LO`/`*_HI` values. For cache and fabric controls, external flows typically program policy bits, poll status bits such as busy/done/fault flags, and issue clear/reset/invalidate operations.

## State And Persistence

The header itself has no persistent state. The state represented by these constants lives in hardware registers:

- Control registers such as `GUS_MISC`, `GL2C_CTRL`, `CHC_CTRL`, and `CP_PERFMON_CNTL` persist in GPU hardware until reset, power transitions, firmware programming, or driver reconfiguration.
- Status and error registers such as `GUS_ERR_STATUS`, `GL1C_STATUS`, and `CHC_STATUS` expose transient or sticky hardware state; some include explicit clear bits.
- Counter registers expose sampled hardware counters. Their values depend on counter-selection programming, perfmon enable state, reset/clear operations, and the hardware block being measured.
- Address-match and pipe-steering registers affect hardware routing/filter behavior and can change the meaning of later memory/cache traffic.

Because these are pure macros, no software state is allocated, reference-counted, locked, or serialized here.

## Dependencies

This chunk depends on the broader generated AMDGPU register ecosystem:

- Companion GC 10.3.0 address headers provide register offsets; this file only provides field masks and shifts.
- AMDGPU register helper macros/functions consume the `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` naming convention.
- The definitions are ASIC-specific and must match the GC 10.3.0 hardware spec and firmware expectations.
- No C includes appear in this file before the chunk; the only top-level structure is the include guard `_gc_10_3_0_SH_MASK_HEADER`.

## Integration Points

Likely consumers include AMDGPU initialization, debugfs/perfmon, RLC/firmware setup, VM/cache management, performance monitoring, and diagnostic paths under `drivers/gpu/drm/amd/`. Integration is by macro name, so compile-time breakage is immediate if a consumer references a missing or renamed field.

The performance-counter data and selector definitions integrate especially with code that exposes GPU metrics, configures streaming performance monitor modes, filters draw windows, or reads block-local counters for profiling. Cache/fabric definitions integrate with low-level GPU bring-up, reset, coherency, flush/invalidate, and error-reporting paths.

## Risks

- Incorrect mask/shift values can silently program wrong hardware bits, causing cache coherency failures, bad performance data, hangs, or misreported faults.
- Split chunk boundaries are risky: this chunk includes only the mask for `GUS_SDP_TAG_RESERVE1__VC7` and only the comment for `SQ_PERFCOUNTER15_SELECT`; the adjacent chunks are required for complete register-level research.
- Many register families are repetitive. Mechanical edits can accidentally change one instance while leaving related engines or counters inconsistent.
- Several fields control reset, invalidation, coherency, protection fault, prefetch, volatile, and atomic behavior; misuse by consumers can affect correctness, not only metrics.
- Counter high registers sometimes contain both counter bits and compare values, for example `*_PERFCOUNTER_HI__COUNTER_HI` plus `COMPARE_VALUE`; consumers must not assume every high register is a plain 32-bit extension.

## Test Signals

Useful validation signals for this chunk are compile-time and hardware-facing:

- Build the AMDGPU driver with GC 10.3.0 support and treat undefined macro references or duplicate definitions as failures.
- Compare generated masks and shifts against the authoritative GC 10.3.0 register database used to generate the header.
- Exercise perfmon/debugfs paths that program `*_SELECT` registers and read `*_LO`/`*_HI` counter pairs across CP, GRBM, SPI, SQ, SDMA, VM L2, GL1/GL2, CB/DB, and RLC/RMI blocks.
- Run cache/VM stress tests that trigger GL1/GL2 invalidation, VM fault/retry reporting, SDMA traffic, and graphics workloads while checking for GPU hangs or fault-status regressions.
- For static checks, verify paired field definitions have coherent masks and shifts and that adjacent chunks complete the split `GUS_SDP_TAG_RESERVE1` and `SQ_PERFCOUNTER15_SELECT` definitions.
