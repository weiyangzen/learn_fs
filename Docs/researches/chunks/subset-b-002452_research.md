# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 7636-10058

## Purpose

This chunk is a generated AMD GC 10.1.0 shift/mask header segment. It contains C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for graphics-core hardware registers. The constants are consumed by AMDGPU and AMDKFD code together with the companion offset header; they are not executable logic by themselves.

The requested range covers 2,423 lines with 2,175 `#define` entries: 1,087 shift macros and 1,088 mask macros, plus 238 register or address-block comment markers. It starts at the mask half of `PA_SC_TILE_STEERING_CREST_OVERRIDE`, then covers GC register blocks for shader queues (`gc_sqdec`), shader processor interpolation/input (`gc_shsdec`), texture/data path control (`gc_tpdec`), global data share (`gc_gdsdec`), and render backend/raster memory layout (`gc_rbdec`). It ends after the complete `GB_TILE_MODE24` group; `GB_TILE_MODE25` begins in the next chunk.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMD GPU hardware metadata. It has no Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, runtime variables, includes, locks, allocations, or direct MMIO calls in this range. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit of a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the full bit mask for extracting, composing, or updating that field.
- Consumers typically combine these constants with `gc_10_1_0_offset.h` register addresses and AMDGPU helper macros such as `REG_GET_FIELD`, `WREG32_SOC15`, and `SOC15_REG_GOLDEN_VALUE`.

Important register families in this chunk are:

- PA/SC tile steering tail: `PA_SC_TILE_STEERING_CREST_OVERRIDE` masks describe one-RB override enable, shader-engine, render-backend, shader-array selection, and forced tile-steering override use. The corresponding shifts are just before this chunk.
- Shader queue and scalar cache setup: `SQ_CONFIG`, `SQC_CONFIG`, `LDS_CONFIG`, `SQ_RANDOM_WAVE_PRI`, `SQG_STATUS`, `SQ_FIFO_SIZES`, `SQ_ARB_CONFIG`, and `SQ_RUNTIME_CONFIG` define shader queue tuning, cache sizing, busy hysteresis, scheduling, retry/sleep, FIFO sizing, and status fields.
- Shader memory configuration: `SH_MEM_BASES` and `SH_MEM_CONFIG` define private/shared base fields and address-mode, alignment-mode, default memory type, retry mode, instruction prefetch, illegal-instruction check, and instruction-cache GL1 behavior. These fields are directly used by AMDKFD and GFX initialization when programming queue process state.
- SQ diagnostics and commands: `SQ_DSM_CNTL`, `SQ_DSM_CNTL2`, `SP_CONFIG`, `SQ_INTERRUPT_AUTO_MASK`, `SQ_INTERRUPT_MSG_CTRL`, `SQ_SHADER_TBA_*`, `SQ_SHADER_TMA_*`, `SQ_WATCH0..3_*`, `SQ_THREAD_TRACE_*`, `SQ_IND_*`, `SQ_CMD`, `SQ_TIME_*`, `SQ_LB_*`, `SQ_EDC_*`, and `SQ_WREXEC_*` cover DSM/error injection, shader trap memory, watchpoints, thread trace buffer programming/status/counters, indirect wave inspection, wave command dispatch, timing, load-balance counters, EDC counters, and WR execution address fields.
- UTCL0 and cache controls: `SQG_UTCL0_CNTL1/2`, `SQC_ICACHE_UTCL0_CNTL1/2`, `SQC_DCACHE_UTCL0_CNTL1/2`, and matching status registers expose GPUVM response/fault modes, VMID invalidation, force-miss/in-order behavior, FIFO/cache-size reductions, EDC disable, snoop and invalidate options, and fault/retry/PRT status.
- SPI/shader input control: `SX_DEBUG_1`, `SPI_PS_MAX_WAVE_ID`, `SPI_START_PHASE`, `SPI_GFX_CNTL`, `SPI_USER_ACCUM_VMID_CNTL`, `SPI_CONFIG_CNTL`, `SPI_CONFIG_CNTL_1/2`, `SPI_DSM_*`, `SPI_EDC_CNT`, `SPI_WAVE_LIMIT_CNTL`, lifetime limit/status registers, SPI load-balance counters, GDS credits, SX export/scoreboard sizes, CSQ wave-active counters, and trap-screen registers describe shader input scheduling, wave limits, debug/golden tuning, statistics, and per-process trap-screen memory bounds.
- Texture/data path control: `TD_CNTL`, `TD_STATUS`, `TD_POWER_CNTL`, `TD_DSM_*`, `TD_SCRATCH`, `TA_POWER_CNTL`, `TA_CNTL`, `TA_CNTL_AUX`, `TA_STATUS`, and `TA_SCRATCH` define sampler/data-path precision, float and gather modes, stall tuning, power/clock behavior, DSM injection, texture credits, deterministic sampler behavior, anisotropy controls, FIFO empty/busy status, and scratch fields.
- Global Data Share: `GDS_CONFIG`, `GDS_CNTL_STATUS`, `GDS_ENHANCE`, protection fault registers, VM protection fault registers, EDC counters, OA DED/PHY/pipe counters, DSM control, and `GDS_WD_GDS_CSB` describe GDS address/configuration, command/status, interrupt or watchdog behavior, VMID/client fault capture, EDC accounting, error injection, and debug readback.
- Render backend and depth buffer: `DB_DEBUG`, `DB_DEBUG2`, `DB_DEBUG3`, `DB_DEBUG4`, stutter controls, credits, watermarks, subtile controls, free cachelines, FIFO depths, last-of-burst behavior, ring control, memory arbitration watermarks, RMI/BC GL2 cache control, exception control, DFSM config/watchdog/flush controls, and fine-grain clock-gating SRAM/interface controls expose depth/stencil compression, HiZ/HiS, cache, coherency, burst, flush, clock, and watchdog tuning.
- Raster/backend address and tile layout: `CC_RB_REDUNDANCY`, `CC_RB_BACKEND_DISABLE`, `GB_ADDR_CONFIG`, `GB_BACKEND_MAP`, `GB_GPU_ID`, `CC_RB_DAISY_CHAIN`, `GB_ADDR_CONFIG_READ`, and `GB_TILE_MODE0` through `GB_TILE_MODE24` describe render-backend enablement, backend mapping, GPU ID, pipe/interleave/SE/RB layout, and indexed tile-mode fields such as array mode, pipe config, tile split, micro-tile mode, and sample split.

Most masks are 32-bit constants with an `L` suffix. Many registers are performance, diagnostics, or bring-up controls rather than normal hot-path state. Access type, reset values, write-one-to-clear behavior, self-clearing semantics, and valid power or clock domains are not encoded here.

## Control Flow

This header has no runtime control flow. It participates in a compile-time-to-runtime chain:

1. GFX10 AMDGPU and AMDKFD source files include `gc/gc_10_1_0_offset.h` and `gc/gc_10_1_0_sh_mask.h`.
2. Driver code builds register values by shifting symbolic field values with `__SHIFT` macros, masking or extracting values with `_MASK` macros, or using generated field helper macros.
3. Runtime sequencing in AMDGPU and AMDKFD writes or reads the associated MMIO registers during GPU initialization, golden-register programming, queue setup, KFD process setup, reset/resume, fault handling, profiling, and diagnostics.
4. Hardware and firmware implement the actual state machines for shader scheduling, memory translation, thread tracing, trap handling, texture/data-path processing, GDS operation, depth/stencil render-backend behavior, and tile/address mapping.

The macros here only describe bit layout. They do not enforce legal values, ordering, barriers, polling intervals, or ASIC-specific golden settings.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible fields whose persistence is governed by the GPU:

- Queue and process configuration state includes shader memory address mode, alignment, retry behavior, prefetch policy, trap base/mask addresses, watchpoint addresses/control, and SQ command fields.
- Debug/profiling state includes SQ thread-trace buffer base/size/write-pointer, trace masks, trace control/status, dropped and marker counters, indirect inspection indices/data, SQ and SPI load-balance counters, wave lifetime limits/status, and CSQ wave-active counters.
- Cache and virtual-memory state includes UTCL0 response/fault modes, VMID invalidation selectors/toggles, force miss/in-order flags, per-cache status bits, and GPUVM fault/retry/PRT indicators.
- Error handling state includes SQ, SPI, TD, and GDS DSM/error-injection controls, EDC counters, fatal/uncorrectable flags, protection-fault status, fault client and VMID capture, and render-backend exception controls.
- Graphics pipeline state includes SPI wave limits and shader input controls, texture sampler precision/determinism/power controls, GDS credits and command/status, depth-buffer compression/cache/coherency tuning, DB flush and watchdog controls, render-backend disable/redundancy state, address layout, backend map, and tile-mode tables.

Configuration fields usually remain until driver reprogramming, context or queue updates, power-gating transitions, suspend/resume, GPU reset, or ASIC reset. Status, fault, trace, counter, watchdog, and interrupt-like fields may be latched, clear-on-write, sampled, self-clearing, or valid only while the corresponding shader, texture, GDS, render-backend, or cache block is powered and clocked. Those semantics must come from hardware documentation and the runtime code, not this generated mask file.

## Dependencies And Integration Points

The direct compile-time dependency is the C preprocessor. The semantic dependency is AMD's GC 10.1.0 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h` supplies matching addresses such as `mmSQ_CONFIG`, `mmSPI_GFX_CNTL`, `mmTD_CNTL`, `mmGDS_CONFIG`, `mmDB_DEBUG`, `mmGB_ADDR_CONFIG`, and `mmGB_TILE_MODE24`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c` includes this header and uses these fields for default `SH_MEM_CONFIG`, golden-register programming for `DB_DEBUG*`, `SPI_CONFIG_CNTL_1`, `TA_CNTL_AUX`, and `GB_ADDR_CONFIG`, and runtime decoding of `GB_ADDR_CONFIG` fields such as pipe count, compressed fragments, RB-per-SE, shader-engine count, and pipe interleave size.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10.c` programs `mmSH_MEM_CONFIG` and emits `mmSQ_CMD` for KFD/GFX10 integration.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v10.c` builds queue-process `SH_MEM_CONFIG` values using this chunk's alignment and initial instruction prefetch shifts.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v10.c`, `kfd_packet_manager_v9.c`, `gfxhub_v2_0.c`, `mxgpu_nv.c`, `sdma_v5_0.c`, `mmhub_v2_0.c`, and `nv.c` include the same generated GC headers for broader GFX10/KFD/Navi integration.

Behaviorally, this range sits under several user-visible GPU features: compute process dispatch, memory model setup, wavefront control, shader trap/watchpoint/debugging, profiling/thread trace, GDS use, texture sampling correctness, depth/stencil rendering, render-backend topology, tiling/addressing, reset handling, and power-management tuning.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong bit position can compile cleanly while corrupting adjacent hardware fields or silently decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register source, the companion offset header, firmware expectations, and silicon behavior.
- The chunk starts with only the mask definitions for `PA_SC_TILE_STEERING_CREST_OVERRIDE`; its shift definitions are in the previous chunk. Whole-register analysis must merge across that boundary.
- The chunk ends cleanly after `GB_TILE_MODE24`; `GB_TILE_MODE25` and later tile modes are in the next chunk. Tile-mode table validation must account for the split.
- Several similarly named SQ, SQC, SQG, and SPI fields have different scopes. Mixing shader-queue, scalar-cache, UTCL0, and shader-input fields can produce hard-to-debug compute, graphics, or profiling failures.
- `SH_MEM_CONFIG` is shared by graphics and KFD process setup. Incorrect address, alignment, retry, or prefetch fields can affect compute memory semantics, XNACK/retry behavior, process isolation, and trap/debug behavior.
- Thread trace and indirect SQ access registers combine buffer address/size, masks, status, and command/index fields. Bad masks can overrun profiling buffers, target the wrong VMID or wave, or misreport dropped trace data.
- Fault and clear/status fields in UTCL0, GDS, DB, and EDC groups can be latched or side-effectful. Treating them as ordinary read/write fields risks losing fault evidence, leaving interrupts stuck, or clearing counters unintentionally.
- Render-backend debug and depth/stencil fields often disable optimizations or force cache/coherency behavior. Bad golden values or wrong masks can cause rendering corruption, hangs, performance regressions, or power regressions.
- `GB_ADDR_CONFIG` and `GB_TILE_MODE*` define memory layout and tiling interpretation. Errors can break framebuffer, texture, or render-target addressing across ASIC variants and may only reproduce with specific RB/SE/pipe configurations.
- Many controls are ASIC stepping and power-domain sensitive. A mask that appears harmless on one Navi/GFX10 variant can be invalid or reserved on another.

## Test Signals

Useful validation combines generated-header checks, build coverage, and GFX/KFD runtime tests:

- Build AMDGPU with GFX10 and AMDKFD enabled so includes from `gfx_v10_0.c`, `amdgpu_amdkfd_gfx_v10.c`, and KFD queue/MQD managers compile against `gc_10_1_0_sh_mask.h`.
- Statically verify that complete register groups in this chunk have matching shift and mask definitions, while allowing the known boundary case where `PA_SC_TILE_STEERING_CREST_OVERRIDE` shifts are outside this range.
- Cross-check complete register groups against `gc_10_1_0_offset.h`, especially `SQ_CONFIG`, `SH_MEM_CONFIG`, `SQ_CMD`, `SPI_CONFIG_CNTL`, `TA_CNTL_AUX`, `GDS_CONFIG`, `DB_DEBUG*`, `GB_ADDR_CONFIG`, and `GB_TILE_MODE0..24`.
- Diff repeated register families, such as `SQ_WATCH0..3`, `SQ_THREAD_TRACE_BUF0/1`, `SPI_WF_LIFETIME_LIMIT_0..9`, `SPI_WF_LIFETIME_STATUS_0..20`, `SPI_CSQ_WF_ACTIVE_COUNT_0..7`, and `GB_TILE_MODE0..24`, to catch generator drift.
- Run GFX10 boot, modeset, suspend/resume, GPU reset, and golden-register initialization paths; failures can indicate DB/SPI/TA/GB masks or offsets no longer match runtime programming.
- Run AMDKFD compute queue creation and dispatch tests that cover `SH_MEM_CONFIG`, `SQ_CMD`, trap handling, and VMID/process memory behavior.
- Exercise shader debugging, watchpoints, trap-screen setup, profiling, and SQ thread trace where available; inspect trace buffers, dropped counters, marker counters, indirect wave data, and status fields for sane decoding.
- Exercise graphics workloads with depth/stencil, HiZ/HiS, MSAA, varied render-target tile modes, multiple RB/SE layouts, and reset/recovery scenarios to catch `DB_*`, `GB_ADDR_CONFIG`, and `GB_TILE_MODE*` issues.
- Use register dumps on failures to confirm `REG_GET_FIELD` and update helpers decode `GB_ADDR_CONFIG`, `SH_MEM_CONFIG`, GDS protection faults, UTCL0 fault status, DB exceptions, and EDC counters with the expected masks.

## Cross-Chunk Notes

The previous chunk owns the `PA_SC_TILE_STEERING_CREST_OVERRIDE` shift definitions and earlier PA/SC registers. This chunk contributes that register's masks, then covers full logical blocks from `gc_sqdec`, `gc_shsdec`, `gc_tpdec`, `gc_gdsdec`, and the start of `gc_rbdec` through `GB_TILE_MODE24`. The next chunk should continue the render-backend tile-mode table at `GB_TILE_MODE25`. The later merge/reconciliation lane should combine these boundaries before making whole-file claims about complete PA/SC and GB tile-mode coverage.
