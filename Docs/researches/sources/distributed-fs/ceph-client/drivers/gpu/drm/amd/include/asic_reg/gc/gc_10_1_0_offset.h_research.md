# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002444`: lines 1-2469, `Docs/researches/chunks/subset-b-002444_research.md`
- `subset-b-002445`: lines 2470-4973, `Docs/researches/chunks/subset-b-002445_research.md`
- `subset-b-002446`: lines 4974-7439, `Docs/researches/chunks/subset-b-002446_research.md`
- `subset-b-002447`: lines 7440-9943, `Docs/researches/chunks/subset-b-002447_research.md`
- `subset-b-002448`: lines 9944-11375, `Docs/researches/chunks/subset-b-002448_research.md`

## Chunk Research

### subset-b-002444: lines 1-2469

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h lines 1-2469

## Scope

This chunk covers the opening 2,469 lines of the generated AMD GC 10.1 register offset header. The source file is a macro-only hardware register map for the graphics/compute block in the AMDGPU driver tree. It starts with the MIT-style AMD copyright notice and the `_gc_10_1_0_OFFSET_HEADER` include guard, then defines register-offset symbols and matching `_BASE_IDX` symbols for the early GC address blocks.

The covered address blocks are:

- Global SQ debug status aliases before the first block: `mmSQ_DEBUG_STS_GLOBAL` at `0x10A9` and `mmSQ_DEBUG_STS_GLOBAL2` at `0x10B0`.
- `gc_sdma0_sdma0dec`, base address `0x4980`, starting at `mmSDMA0_DEC_START` and covering SDMA0 global, GFX, PAGE, and RLC0 through RLC7 queue register windows.
- `gc_sdma1_sdma1dec`, base address `0x6180`, starting at `mmSDMA1_DEC_START` and covering the matching SDMA1 global, GFX, PAGE, and RLC0 through RLC7 queue register windows.
- `gc_grbmdec`, base address `0x8000`, covering GRBM control, status, reset, trap, error, fence, and scratch registers.
- `gc_cpdec`, base address `0x8200`, covering command processor status, busy/stall counters, MEC control/header dump, command-index/data windows, ring read pointers, queue thresholds, and queue/ROQ/STQ/MEQ status registers.
- `gc_padec`, base address `0x8800`, covering primitive assembly, geometry/vertex-grouper/tessellation, work distributor, input assembler UTCL1, shader-array configuration, rasterizer/scan converter binner, FIFO, and enhancement registers.
- The beginning of `gc_sqdec`, base address `0x8c00`, through `mmSQ_SHADER_TBA_LO` at the end of this chunk.

Within this chunk there are 1,223 non-`_BASE_IDX` `mm*` register-offset macros and 1,200 matching `_BASE_IDX` macros. The small mismatch is intentional in the visible data: a few symbols in this range do not have an adjacent base-index macro, for example some doorbell log and GPU IOV violation log aliases.

## Purpose

The header provides compile-time symbolic names for GC 10.1 memory-mapped register offsets. AMDGPU and AMDKFD code use these symbols to avoid hard-coded numeric register offsets in ring setup, reset, interrupt, diagnostic, power-management, virtual-memory, and queue-management paths.

The values are offsets in the ASIC register namespace, not executable logic. For SOC15-era register access, consumers normally combine these offsets with IP block metadata using helpers/macros such as `SOC15_REG_OFFSET(GC, instance, mmREG)`, `SOC15_REG_ENTRY(...)`, `RREG32(...)`, `WREG32(...)`, or RLC-shadowed write helpers. SDMA-specific consumers also use arithmetic against the repeated SDMA windows, for example taking `mmSDMA0_RLC1_RB_CNTL - mmSDMA0_RLC0_RB_CNTL` as the stride between RLC queue register groups.

## Important APIs, Types, and Macros

This file defines no C types, functions, inline helpers, or data structures. Its API surface is the set of preprocessor symbols:

- Register-offset macros: `#define mm<name> <hex offset>`.
- Base-index macros: `#define mm<name>_BASE_IDX 0`.
- Address-block comments: `// addressBlock: ...` and `// base address: ...`, which document the source hardware block grouping but are not parsed by the C compiler.
- The include guard `_gc_10_1_0_OFFSET_HEADER`, which prevents duplicate macro definition within a translation unit.

Important macro families in this chunk:

- `mmSDMA0_*` and `mmSDMA1_*`: SDMA engine registers. These include engine control (`*_CNTL`, `*_CLK_CTRL`, `*_POWER_CNTL`), firmware/identity/status (`*_PROGRAM`, `*_STATUS*_REG`, `*_VERSION`, `*_UCODE_CHECKSUM`), error and EDC state (`*_EDC_*`, `*_ERROR_LOG`), UTCL1 translation and XNACK state (`*_UTCL1_*`), interrupt state (`*_INT_STATUS`), performance counters, GFX/PAGE ring controls, and repeated RLC queue registers.
- `mmSDMA_POWER_GATING`, `mmSDMA_PGFSM_CONFIG`, `mmSDMA_PGFSM_WRITE`, and `mmSDMA_PGFSM_READ`: shared SDMA power-gating FSM offsets appearing in the SDMA0 block.
- `mmGRBM_*`: graphics register bus manager controls and status. These include global busy/idle status (`mmGRBM_STATUS`, `mmGRBM_STATUS2`, `mmGRBM_STATUS_SE0` through `SE3`), soft reset, clock/power controls, read/write/IOV errors, trap controls, fence ranges, and scratch registers.
- `mmCP_*`: command processor, CPF, CPC, CE, ME, MEC, queue, and ring observability offsets. Representative symbols are `mmCP_CPC_STATUS`, `mmCP_CPF_STATUS`, `mmCP_MEC_CNTL`, `mmCP_STAT`, `mmCP_ME_CNTL`, `mmCP_ME_PREEMPTION`, `mmCP_RB*_RPTR`, `mmCP_CMD_INDEX`, `mmCP_CMD_DATA`, `mmCP_ROQ*_THRESHOLDS`, and `mmCP_*_STAT`.
- `mmVGT_*`, `mmGE_*`, `mmWD_*`, `mmIA_*`, `mmPA_*`, `mmCC_GC_*`, and `mmGC_USER_*`: front-end and primitive assembly/rasterization offsets used for graphics pipeline setup, shader-array configuration, binner tuning, input assembler translation status, FIFO depths, and geometry/tessellation controls.
- `mmSQ_*`, `mmSQC_CONFIG`, `mmLDS_CONFIG`, `mmSH_MEM_*`, `mmSP_CONFIG`, `mmSQG_*`, and `mmCC_GC_SHADER_RATE_CONFIG`: the start of the shader queue/SQ block, including global shader configuration, LDS/shared-memory setup, interrupt controls, shader-rate configuration, and SQG UTCL0 registers.

## Control Flow and Data Flow

There is no runtime control flow in this header. The practical flow is entirely through compile-time substitution:

1. A GC 10.1 source file includes the offset header, often alongside a corresponding `*_sh_mask.h` header that supplies bit masks and shifts.
2. Driver code passes a register macro to a register access macro or helper.
3. The access helper resolves the IP block base and instance, adds the register offset, and performs an MMIO read or write.
4. The hardware observes the read/write and changes GPU state, queue state, interrupt state, or diagnostic counters.

For SDMA queue programming, the offset table also encodes repeated layout. The GFX, PAGE, and RLC queue groups use repeated offsets for `RB_CNTL`, `RB_BASE`, `RB_RPTR`, `RB_WPTR`, `IB_*`, `DOORBELL`, `CONTEXT_STATUS`, `CSA_ADDR`, `PREEMPT`, `MINOR_PTR_UPDATE`, and `MIDCMD_*` registers. AMDKFD-style queue management can compute a queue-specific register window by adding a queue stride to `mmSDMA0_RLC0_*` symbols instead of enumerating every queue separately.

For diagnostics and reset, GRBM and CP status macros feed register dump tables and idle checks. The values let reset paths query whether GRBM, CP, CPF, CPC, MEC, or SDMA are busy/stalled and can support debug output after hangs.

## State and Persistence Behavior

The header itself has no persistent state. It is a static register schema.

The registers named by the macros represent hardware state with different lifetimes:

- SDMA ring state persists in GPU registers while the engine is active: ring base addresses, read/write pointers, indirect buffer pointers, doorbell settings, and context-save-area addresses.
- SDMA and CP status, busy, stalled, error, interrupt, EDC, and performance-counter registers are hardware-observed state that may change asynchronously as engines execute work.
- GRBM scratch registers can be used as temporary GPU-visible scratch state, but the header does not prescribe ownership or persistence semantics.
- Power-gating, clock-control, reset, and preemption registers change engine lifecycle state and may be reset by GPU reset, suspend/resume, or power-management transitions.
- Shader, primitive assembly, rasterization, and shader-array configuration registers influence pipeline behavior until overwritten or reset by driver/hardware sequencing.

Any persistence guarantee must be inferred from the relevant engine programming sequence, not from this header. The source file only fixes symbolic offsets.

## Dependencies and Integration Points

Direct dependencies are minimal:

- The file depends only on the C preprocessor and its include guard.
- It is intended to be included by AMDGPU/AMDKFD code for GC 10.1 ASICs, commonly with matching mask headers from the same generated register tree.
- `_BASE_IDX` macros integrate with SOC15 register-addressing helpers that expect a base-index argument for generated register symbols.

Observed integration points in the surrounding AMDGPU tree include:

- GPU reset and diagnostic register dump tables that reference `mmGRBM_STATUS*`, `mmCP_STAT`, `mmCP_STALLED_STAT*`, `mmCP_CPF_*`, `mmCP_CPC_*`, and `mmSDMA0_STATUS_REG`.
- SDMA engine setup code that writes SDMA control, power, clock, ring, IB, tiling, quantum, and interrupt/status registers through the `mmSDMA*` macro families.
- AMDKFD Arcturus queue management that programs SDMA RLC queues using `mmSDMA0_RLC0_*` and computed queue strides.
- SOC15 helper paths that wrap GC register names with `SOC15_REG_OFFSET(GC, 0, ...)` or `SOC15_REG_ENTRY(...)`.
- Shader/SQ setup or debug paths that read/write `mmSQ_CONFIG` and related SQ/SQG/shared-memory configuration registers.

Because this path is under `sources/distributed-fs/ceph-client/...`, it is a vendored or mirrored Linux/DRM source subtree inside this repository. The register header itself is not Ceph-specific; it belongs to the AMD GPU driver code carried by the source tree.

## Risks and Invariants

The main risk is silent hardware misprogramming. These numeric offsets are used in low-level MMIO paths; an incorrect value can write the wrong register, corrupt queue state, break power management, hide real diagnostics, or hang the GPU.

Important invariants:

- Register offsets must match the GC 10.1 hardware specification exactly.
- `_BASE_IDX` values must stay compatible with the SOC15 register-base tables used by the target ASIC generation.
- Repeated SDMA queue windows must preserve their layout and stride; code relies on arithmetic between adjacent queue families such as RLC0 and RLC1.
- SDMA0 and SDMA1 windows should remain aligned with their engine-specific offset ranges. A symbol copied into the wrong engine namespace can cause driver code to access the wrong SDMA instance.
- Aliases such as `mmCP_RB0_RPTR` and `mmCP_RB_RPTR` sharing the same offset are meaningful compatibility aliases and should not be deduplicated without checking all consumers.
- Generated formatting and symbol names are part of the include-time API. Renaming a macro is a source compatibility break even when the numeric value is unchanged.
- This chunk ends mid-`gc_sqdec`; downstream research/merge lanes must combine it with later chunks before treating the full source file as covered.

Manual edits are particularly risky because this file is generated-style data. Corrections should preferably come from the same register database/generator that produced the surrounding ASIC register headers.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware/driver integration signals:

- Full kernel or module build of the AMDGPU/AMDKFD subtree catches missing or renamed macro symbols.
- Warnings/errors from files using `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY`, `RREG32`, or `WREG32` with these symbols catch include-order or macro availability regressions.
- SDMA ring tests should exercise SDMA0/SDMA1 ring initialization, write-pointer updates, IB submission, preemption, and queue teardown.
- KFD compute queue tests should exercise the SDMA RLC queue windows, especially stride-based programming across RLC0 through RLC7.
- GPU reset/hang recovery tests should verify that GRBM, CP, CPF, CPC, and SDMA status dumps still read valid registers.
- Suspend/resume and runtime power-management tests should cover SDMA power/clock and GRBM power-control register access.
- Graphics pipeline smoke tests should catch PA/VGT/GE/WD/IA/SQ configuration mistakes through draw failures, shader launch failures, or hang diagnostics.
- Register dump comparison against known-good GC 10.1 hardware traces can detect offset drift that normal compilation cannot catch.

For this research task, the required output file exists at `Docs/researches/chunks/subset-b-002444_research.md` and is intentionally a chunk-level source-tree-aligned report, not the final per-file merged report.

### subset-b-002445: lines 2470-4973

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h lines 2470-4973

## Scope

This chunk covers lines 2470-4973 of the generated GFX10.1 GC register offset header. It is a hardware register map, not executable driver logic. The chunk contains 1,214 non-`_BASE_IDX` `mm*` register offset macros, plus the paired `*_BASE_IDX` macros used by SOC15 register-address helpers. The region starts mid-pair with `mmSQ_SHADER_TBA_LO_BASE_IDX` at line 2470, then continues with shader/SQ registers at offsets around `0x10bd`; it ends at line 4973 with `mmCP_IQ_WAIT_TIME3` and its paired base-index macro is outside this chunk.

The generated format is consistent with the rest of `gc_10_1_0_offset.h`: each hardware register is represented as a preprocessor constant such as `mmGCVM_CONTEXT0_CNTL 0x1620` and usually a companion `mmGCVM_CONTEXT0_CNTL_BASE_IDX 0`. Driver code combines these values with the GC IP instance and the SOC15 base table through helpers such as `SOC15_REG_OFFSET(GC, 0, ...)`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_SOC15_OFFSET`.

## Purpose

The purpose of this chunk is to provide the numerical MMIO offsets for a large portion of the Navi/GFX10.1 graphics and compute command, shader, texture, render backend, memory-translation, and VM register space. These constants are effectively an ABI between AMD's generated register database and the in-kernel AMDGPU/KFD code that programs GFX10.1 hardware.

The covered range is especially important because it includes:

- Shader queue/SQ debugging and thread trace controls, including watchpoints and thread-trace buffer programming.
- SPI shader processor interpolation, wave lifetime, per-stage shader program registers, and performance counters.
- Texture front-end, GDS, DB/CB/RB, GB tiling, and color/depth backend register offsets.
- GCVM/GCMC graphics VM context, invalidate, L2 cache, ATC, TLB, and protection-fault register offsets.
- GCEA address decode and memory-client routing controls.
- Shader register-space offsets for graphics and compute pipeline state.
- Command processor ring, interrupt, VMID, queue priority, context, suspend/resume, and microcode-entry-point registers.

## Address Blocks and Register Families

The chunk crosses multiple generated `addressBlock` sections:

| Lines | Address block | Base | Non-base macros | Main register families |
| --- | --- | ---: | ---: | --- |
| 2470-2574 | continued previous block | inherited | 52 | `SQ`, `SQC` shader control, watch, trace, counters, UTCL0 cache controls |
| 2577-2725 | `gc_shsdec` | `0x9000` | 74 | `SX`, `SPI` graphics setup, SPI config, wave lifetime, trap-screen bounds, SPI counters |
| 2729-2753 | `gc_tpdec` | `0x9400` | 12 | `TD`, `TCP`, `TA` texture pipe controls, DSM and scratch registers |
| 2757-2783 | `gc_gdsdec` | `0x9700` | 13 | `GDS` config, EDC counters, DSM, CSB registers |
| 2787-2983 | `gc_rbdec` | `0x9800` | 98 | `DB`, `CB`, `GB`, `CC`, `GC_USER` render backend, tiling, stutter, pipe/backend disable |
| 2987-3033 | `gc_gceadec2` | `0x9c00` | 23 | `GCEA` SDP, IO, probe, DSM, performance, misc controls |
| 3037-3043 | `gc_spipdec2` | `0x9c80` | 3 | `SPI` PQ event and SYS WIF controls |
| 3047-3069 | `gc_gceadec3` | `0x9dc0` | 11 | `GCEA` DRAM bank, arbitration, and SDP enable controls |
| 3073-3133 | `gc_rmi_rmidec` | `0x9e00` | 30 | `RMI` routing, scoreboards, UTCL1/TCIW errors, redundancy |
| 3137-3151 | `gc_pmmdec` | `0x9f80` | 7 | `PMM`, `GCR` power/performance and spare controls |
| 3155-3163 | `gc_utcl1dec` | `0x9fa0` | 4 | `UTCL1`, `GCRD` UTCL/SA target controls |
| 3167-3191 | `gc_gcatcl2dec` | `0xa000` | 12 | `GC_ATC_L2` ATC L2 address-translation cache controls |
| 3195-3265 | `gc_gcvml2pfdec` | `0xa100` | 35 | `GCVM_L2`, protection-fault, dummy page, context identity aperture, walker throttle |
| 3269-3675 | `gc_gcvml2vcdec` | `0xa200` | 203 | `GCVM_CONTEXT0..15`, invalidate engines 0-17, invalidate acknowledgements and ranges |
| 3679-3719 | `gc_gcvmsharedpfdec` | `0xa590` | 20 | `GCMC_VM`, shared VM MMIO apertures, FB/AGP/TLB reset requests |
| 3723-3739 | `gc_gcvmsharedvcdec` | `0xa600` | 8 | `GCMC_VM` framebuffer/AGP location, system aperture, L1 TLB control |
| 3743-4001 | `gc_gceadec` | `0xa800` | 129 | `GCEA` address-decode maps, DRAM remap, DSM, SDP/VCD, IO and spare controls |
| 4005-4023 | `gc_tcdec` | `0xac00` | 9 | `TCP`, `TCI` invalidate, address config, depth controls |
| 4027-4679 | `gc_shdec` | `0xb000` | 326 | `SPI_SHADER_*`, `COMPUTE_*`, `SPI_CSQ`, user data, resource, trap, dispatch, scratch |
| 4683-4973 | `gc_cppdec` | `0xc080` | 145 | `CP`, `CPC`, `CPG`, `CPF` EOP, rings, interrupts, VMID, queue priority, context, suspend/resume |

Dominant families by macro count are `SPI` (mostly shader program registers), `GCVM`/`GCMC` (graphics VM), `GCEA` (address decode), `CP`/`CPC` (command processor), `COMPUTE`, `GB`, `DB`, `RMI`, and `GDS`.

## Important APIs, Types, and Macros

This header does not define C types or functions. Its important exported API is the set of preprocessor constants consumed by AMDGPU and AMDKFD:

- `mmSQ_*` and `mmSQC_*`: shader queue/sequencer controls, debug watch registers, thread-trace buffer setup, LB counters, EDC counters, indirect index/data, shader TBA/TMA addresses, and SQC cache UTCL0 controls.
- `mmSPI_*`: shader processor interpolator and shader program register offsets. The chunk includes graphics-stage resource/user-SGPR/user-data groups such as `mmSPI_SHADER_PGM_RSRC4_PS`, `mmSPI_SHADER_PGM_LO_GS`, `mmSPI_SHADER_USER_DATA_PS_*`, and many `mmSPI_SHADER_USER_ACCUM_*` registers.
- `mmCOMPUTE_*`: compute shader command state such as `mmCOMPUTE_PGM_LO/HI`, `mmCOMPUTE_PGM_RSRC*`, dispatch dimensions, start coordinates, thread-management masks, user data, scratch, trap, restart, perf, and dispatch tunneling controls.
- `mmGCVM_*`: graphics VM context and invalidation registers. The chunk defines context 0-15 control, page-table base, start, and end address pairs; L2 cache and protection fault controls; invalidate engine semaphores, requests, acknowledgements, and address ranges.
- `mmGCMC_VM_*`: shared graphics-memory-controller VM aperture and TLB controls, including framebuffer and AGP location registers.
- `mmGC_ATC_L2_*`: ATC L2 cache control/status registers used by address-translation paths.
- `mmDB_*`, `mmCB_*`, `mmGB_*`, `mmCC_*`: render backend, depth buffer, color buffer, tile/macrotiling, stutter, and backend-disable offsets.
- `mmGCEA_*`: address decode, DRAM client/group maps, SDP, DSM, IO, probe, and performance-counter controls.
- `mmCP_*`, `mmCPC_*`, `mmCPG_*`, `mmCPF_*`: command processor EOP queue wait, ring buffer base/control/read-pointer/write-pointer, interrupt control/status, power, ECC, fetcher, queue priority, program-counter starts, context controls, VMID reset/preempt/status, and suspend/resume controls.
- `*_BASE_IDX`: base-index companions for each register. In this chunk all visible `*_BASE_IDX` values are `0`, meaning callers use SOC15 GC base segment index 0 for these offsets.

The sibling `gc_10_1_0_sh_mask.h` supplies bit masks and shifts for many of these offsets. The driver normally writes an offset macro together with a mask macro, for example reading `mmGCVM_CONTEXT0_CNTL`, modifying fields with `GCVM_CONTEXT0_CNTL__...` masks/shifts, then writing the same register back.

## Control Flow

There is no runtime control flow in this header. The practical control flow happens in consumers:

1. A GFX10.1 driver source includes `gc/gc_10_1_0_offset.h` and usually `gc/gc_10_1_0_sh_mask.h`.
2. A register macro is passed to a SOC15 helper. For direct MMIO, code uses `RREG32_SOC15(GC, 0, mm...)` or `WREG32_SOC15(GC, 0, mm..., value)`. For offsets stored in structs or packet payloads, code uses `SOC15_REG_OFFSET(GC, 0, mm...)`.
3. For repeated register groups, code computes distances from adjacent offset macros. A representative pattern in `gfxhub_v2_0_init()` computes `hub->ctx_distance = mmGCVM_CONTEXT1_CNTL - mmGCVM_CONTEXT0_CNTL` and similar distances for page-table bases and invalidate engines.
4. Runtime code then iterates over contexts, invalidation engines, rings, pipes, or queues by applying those distances with `WREG32_SOC15_OFFSET` or by storing absolute register offsets in `struct amdgpu_vmhub`.

The generated ordering is therefore semantically important. Even if no C loop exists in this file, several consumers assume that register instances are evenly spaced and ordered exactly as represented by this header.

## State and Persistence Behavior

The header itself has no persistent state, allocation, locking, or side effects. It describes persistent hardware state that survives in GPU registers until reset, reinitialization, context switch, or explicit driver programming. Important state categories represented by this chunk include:

- VM state: `mmGCVM_CONTEXT*` page-table roots, virtual address bounds, translation-control bits, invalidate engine requests/acks, and protection-fault status. These registers control GPU virtual-memory translation for graphics/compute traffic.
- Shader and compute state: `mmSPI_SHADER_*` and `mmCOMPUTE_*` registers describe currently programmed shader addresses, resources, scratch, user data, trap addresses, dispatch dimensions, and thread-management state.
- Debug and profiling state: `mmSQ_WATCH*`, `mmSQ_THREAD_TRACE_*`, `mmSQ_LB_*`, `mmSPI_WF_LIFETIME_*`, and performance-counter registers configure debug watchpoints, thread trace buffers, lifetime counters, and diagnostic counters.
- Command processor state: `mmCP_RB*`, `mmCP_INT_*`, `mmCP_EOPQ_*`, `mmCP_CONTEXT_CNTL`, `mmCP_VMID_*`, and `mmCPC_SUSPEND_*` program ring buffers, interrupt routing/status, queue priorities, VMID behavior, and suspend/context-save memory layout.
- Render backend and memory-routing state: `mmDB_*`, `mmCB_*`, `mmGB_*`, `mmGC_USER_*`, `mmRMI_*`, and `mmGCEA_*` configure tiling, backend masks, stutter behavior, memory route/decode settings, and redundancy.

Because these are register offsets, incorrect constants usually do not cause ordinary memory corruption in this header. Instead, they cause later driver code to write a valid value to the wrong hardware register or read a status bit from the wrong location. That can manifest as VM faults, queue hangs, corrupt rendering, failed reset, lost interrupts, broken debugger/profiler output, or invalid SR-IOV behavior.

## Dependencies

Direct dependencies are compile-time only:

- C preprocessor inclusion by AMDGPU/KFD source files.
- The SOC15 register-base infrastructure that interprets `GC`, instance `0`, and the `*_BASE_IDX` values.
- Bitfield macros in `gc_10_1_0_sh_mask.h`.
- Defaults in related generated headers such as `gc_10_1_0_default.h` when consumers reset registers to hardware default values before setting fields.

Representative consumers under `drivers/gpu/drm/amd` include:

- `amdgpu/gfx_v10_0.c`, which includes this header and programs CP graphics rings with offsets such as `mmCP_RB0_BASE`, `mmCP_RB0_BASE_HI`, `mmCP_RB0_CNTL`, and write/read pointer registers.
- `amdgpu/gfxhub_v2_0.c`, which includes this header and uses `mmGCVM_CONTEXT0_CNTL`, `mmGCVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32`, `mmGCVM_INVALIDATE_ENG0_REQ`, and related offsets to initialize the graphics VM hub.
- `amdgpu/gfxhub_v2_1.c`, which uses the same GFX10-family VM layout and stores/restores `mmGCVM_CONTEXT0_CNTL`-based state.
- `amdkfd/kfd_mqd_manager_v10.c` and `amdgpu/amdgpu_amdkfd_gfx_v10.c`, which use this generation's offsets and masks for KFD queue descriptors, HQD load/destroy/dump paths, and queue occupancy checks.
- Other GFX10-family modules including `amdkfd/kfd_device_queue_manager_v10.c`, `amdgpu/amdgpu_sdma.c`, `amdgpu/sdma_v5_0.c`, `amdgpu/mmhub_v2_0.c`, `amdgpu/mxgpu_nv.c`, and `amdgpu/nv.c`.

## Integration Points

Key integration points are hardware-programming paths rather than function calls from this header:

- Graphics VM initialization: `gfxhub_v2_0_enable_system_domain()` reads `mmGCVM_CONTEXT0_CNTL`, sets context-enable, depth, and retry fields, then writes it back. `gfxhub_v2_0_init()` stores SOC15 offsets for context page-table bases, invalidate engine registers, and protection-fault registers, and computes distances from adjacent macros.
- VM disable and invalidation: `gfxhub_v2_0_gart_disable()` disables all contexts by iterating over `mmGCVM_CONTEXT0_CNTL` with `hub->ctx_distance`. Any spacing error in the context macros would disable or modify the wrong context registers.
- Ring setup: `gfx_v10_0` programs CP ring state using `mmCP_RB0_*`, `mmCP_RB1_*`, `mmCP_RB2_*`, `mmCP_RB_WPTR_POLL_ADDR_*`, and `mmCP_RB_ACTIVE`. These offsets are central to command submission.
- KFD queue management: KFD v10 code includes this offset header with the matching mask header and uses the same generation's register vocabulary for HQD load/dump/destroy and MQD setup. Queue control correctness depends on CP/HQD register offsets aligning with firmware/hardware expectations.
- Shader dispatch and packet construction: code that builds compute or graphics packets uses shader and compute register offsets, often as packet payload register addresses. The `mmSPI_SHADER_*` and `mmCOMPUTE_*` ranges in this chunk are therefore part of command-stream ABI.
- Debug/profiling tools: SQ watch, thread trace, lifetime, and performance counter offsets integrate with developer tooling, hang diagnostics, and profiling paths. Misalignment may not be detected by basic boot tests but can break debug signal collection.

## Risks and Edge Cases

- Generated-header drift: these constants should match AMD's hardware register database for GC 10.1. Manual edits are high risk because a one-line offset change silently redirects MMIO.
- Chunk boundary risk: line 2470 is the `BASE_IDX` for a macro that begins before this chunk, and line 4973 is `mmCP_IQ_WAIT_TIME3` without its paired `BASE_IDX` line. Merge/reconciliation should account for pairs crossing chunk boundaries.
- Register instance spacing assumptions: VM context and invalidate-engine consumers compute distances from adjacent macros. If one member of a repeated group is missing, reordered, or assigned the wrong offset, loops that program 16 contexts or 18 invalidation engines can corrupt unrelated registers.
- Same-offset aliases: some registers deliberately share an offset, such as the visible `mmSQ_WREXEC_EXEC_HI` and `mmSQ_WREXEC_EXEC_LO` both mapped to `0x1151`. A naive duplicate-offset checker could flag legitimate aliases; validation should distinguish hardware aliases from accidental collisions.
- Base-index assumptions: all visible base-index values in the chunk are `0`. If a future ASIC revision moves some blocks to a different SOC15 base index, changing only offsets without base indexes would be incomplete.
- 32-bit/64-bit register pairs: many base address and range registers are split into LO/HI pairs, for example VM page-table bases, CP ring bases, SQ thread-trace buffers, and CPC suspend context-save addresses. Programming order, alignment, and shifting are handled by consumers, but wrong offsets break the pair.
- Security and isolation impact: GCVM context, protection fault, VMID, page table, invalidate, and suspend context-save offsets affect address translation and process isolation. Errors here can produce GPU memory faults, stale translations, incorrect VMID preemption, or queue state leakage across contexts.
- Diagnostics coverage gap: offsets used only by profiling, EDC, or debug paths may not be covered by ordinary rendering or compute smoke tests.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-behavior checks:

- Build coverage: compile AMDGPU/KFD with `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h` included by GFX10/KFD sources. Preprocessor failures catch missing macros but not wrong values.
- Register offset smoke checks: compare generated offsets against AMD's authoritative register database or known-good upstream header for GC 10.1. This is the most direct way to catch value drift.
- GFX ring bring-up: boot a GC 10.1 device and verify `gfx_v10_0` initializes CP rings without ring test timeout, especially paths programming `mmCP_RB0_BASE`, `mmCP_RB0_BASE_HI`, `mmCP_RB*_CNTL`, and pointer registers.
- VM/GART tests: exercise GART enable/disable, VM fault handling, and TLB invalidation. Good signs include successful `gfxhub_v2_0` initialization, no unexpected VM fault storms, and correct handling of invalid page faults.
- KFD compute queue tests: create/destroy AQL queues, dispatch compute kernels, and trigger preemption/CWSR where available. These paths stress CP/HQD, VMID, suspend, and compute program registers.
- Graphics rendering tests: run basic DRM/KMS and userspace rendering workloads that exercise SPI shader program state, DB/CB/RB backend state, GB tiling state, and command submission.
- Debug/profiling tests: run SQ thread trace, performance counter collection, and debugger watchpoint flows if available. These are needed to cover the SQ/SPI diagnostic registers that normal rendering may not touch.
- Suspend/reset tests: trigger GPU reset and system suspend/resume paths on supported hardware; observe CP, VM, and CPC suspend/context-save programming behavior.

## Research Notes

This chunk is source-tree-aligned to the original generated header and intentionally does not produce a final per-file report. The later merge lane should combine this with the neighboring chunks for `gc_10_1_0_offset.h`, especially because the line boundaries cut through register/base-index pairs at both ends.

### subset-b-002446: lines 4974-7439

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h lines 4974-7439

## Scope

This chunk is a generated AMD GC 10.1.0 register offset header slice. It covers lines 4974 through 7439 of `gc_10_1_0_offset.h` and contains 2,434 `#define` entries: 1,217 register offset macros and 1,217 matching `_BASE_IDX` macros inside this line range. The visible register namespace starts with the tail `_BASE_IDX` for `mmCP_IQ_WAIT_TIME3`, then the first complete offset macro in this chunk is `mmCPC_DDID_BASE_ADDR_LO` at `0x1e6b`. The chunk ends at `mmVGT_PRIMITIVE_TYPE 0x2242`; its `_BASE_IDX` partner is just after the requested range.

The file is declarative only. It has no functions, structs, enums, variables, branches, loops, local storage, locking, allocation, or direct MMIO. Its public API is the preprocessor macro namespace consumed by AMDGPU GC 10.x code through SOC15 register helpers.

## Purpose

`gc_10_1_0_offset.h` maps symbolic GC 10.1.0 register names to register offsets and base-address-selector indices. This chunk describes a large portion of the graphics command processor, shader processor interface, compute queue, global data share, graphics pipeline, color/depth, and user-data register windows.

The range crosses these generated address blocks:

- Lines 4974-5170 continue the preceding CP/CPC block with DDID, GFX HPD/HQD, DMA watch, ring-buffer doorbell, RCIU, UTCL1, soft reset, and CPC graphics control registers.
- `gc_spipdec`, base address `0xc700`, starts at line 5171 and covers SPI arbitration, work-class percentages, graphics debug/trap controls, compute queue reset, CU resource reservation, and shader resource-limit controls.
- `gc_cpphqddec`, base address `0xc800`, starts at line 5289 and covers CP HPD/HQD/MQD queue descriptors, PQ/IB/EOP/context-save/GDS/DDID/dequeue registers for compute queues.
- `gc_didtdec`, base address `0xca00`, starts at line 5437 and exposes DIDT indirect index/data controls.
- `gc_gccacdec`, base address `0xca10`, starts at line 5447 and covers GC CAC, DIDT, throttle, EDC, performance counters, and indirect CAC data ports.
- `gc_tcpdec`, base address `0xca80`, starts at line 5499 and covers TCP watchpoint, UTCL0, and performance-counter filter registers.
- `gc_gdspdec`, base address `0xcc00`, starts at line 5541 and covers GDS per-VMID base/size, GWS/OA ownership, reset, wave-id, context-switch status, and context-switch counters.
- `gc_gfxdec0`, base address `0x28000`, starts at line 5727 and switches to `_BASE_IDX 1`, covering DB, PA, COHER, CB, SPI, SX, VGT, IA, WD, GE, and other graphics pipeline state registers.
- `gc_gfxudec`, base address `0x30000`, starts at line 7011 and covers CP user-facing EOP, streamout, primitive/invocation counters, scratch, atomic/preop, semaphore, DMA, coherency, command-buffer, doorbell, metadata, indirect draw/dispatch, GDS backup, RLC perf, GRBM index, and early VGT user registers.

## Exported API Surface

There are no callable APIs or local types. The exported interface is a pair of generated macros for each register:

- `mm<REGISTER>`: the register offset within the selected GC address block.
- `mm<REGISTER>_BASE_IDX`: the base-address selector used by `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_ENTRY_STR`, `SOC15_REG_GOLDEN_VALUE`, and related AMDGPU helpers.

Important visible macro families include:

- `mmCP_*`, `mmCPC_*`, `mmCPF_*`, and `mmCPG_*`: command processor, compute/gfx queue descriptor, ring-buffer, doorbell, DDID, DMA, semaphore, coherency, scratch, streamout, EOP, counter, and metadata offsets.
- `mmCP_GFX_HQD_*` and `mmCP_HQD_*`: graphics and compute hardware queue descriptor registers used to initialize, deactivate, dump, and restore queues.
- `mmSPI_*`: shader processor interface arbitration, graphics debug/trap, compute queue reset, CU reservation, pixel-shader input controls, barycentric/interpolation controls, temporary-ring size, and shader format registers.
- `mmDIDT_*`, `mmGC_CAC_*`, `mmGC_DIDT_*`, `mmGC_THROTTLE_*`, `mmGC_EDC_*`, `mmEDC_*`, `mmPCC_*`, and `mmPWRBRK_*`: dynamic power, throttling, cumulative activity, error/droop, and related performance monitor register offsets.
- `mmTCP_*`: texture/cache pipe watchpoint and UTCL0/performance-filter offsets.
- `mmGDS_*`: global data share VMID range allocation, GWS/OA ownership, reset, compute max wave id, and context-switch status/counter offsets.
- `mmDB_*`, `mmCB_*`, `mmPA_*`, `mmVGT_*`, `mmIA_*`, `mmWD_*`, `mmGE_*`, `mmTA_*`, `mmCOHER_*`, and `mmSX_*`: fixed-function graphics state, depth/color buffer state, scissor/viewport/rasterization/sample state, vertex/geometry/tessellation state, render target layout, blend controls, and coherency destination base offsets.
- `mmRLC_*` and `mmGRBM_*`: late chunk entries for RLC GPM performance counters and graphics block indexing.

Several macro names alias the same numeric offset where hardware or software supports old/new names. Examples in this chunk include `mmCPC_DDID_*` and `mmCP_DDID_*`, `mmCP_HPD_MES_ROQ_OFFSETS` and `mmCP_HPD_ROQ_OFFSETS`, `mmCP_HQD_DMA_OFFLOAD` and `mmCP_HQD_OFFLOAD`, scheduler/status aliases around `mmCP_HQD_HQ_*`, and low/high aliases such as `mmCP_APPEND_DATA` and `mmCP_APPEND_DATA_LO`.

## Control Flow

This header has no local runtime control flow. Runtime behavior emerges when AMDGPU code includes this file and passes its macros through register helper layers:

1. `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c` includes both `gc/gc_10_1_0_offset.h` and `gc/gc_10_1_0_sh_mask.h`.
2. Register dump and diagnostics tables use macros from this range through `SOC15_REG_ENTRY_STR`, including CP HQD/GFX HQD queue registers.
3. Golden settings tables use graphics pipeline macros such as PA, SPI, TCP, and related GC registers with mask/value pairs.
4. Queue setup, teardown, and restore code uses `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`, and `REG_SET_FIELD` against macros from this chunk.
5. The actual sequencing, polling, masking, and field composition lives in `gfx_v10_0.c` and companion code; this header only supplies offsets and base indices.

The `_BASE_IDX` transition is important. CP/CPC/SPI/HQD/DIDT/CAC/TCP/GDS blocks in the early part of the chunk use base index `0`; `gc_gfxdec0` and `gc_gfxudec` register ranges use base index `1`. Consumers must preserve this pairing because the same offset value can mean different physical registers under different SOC15 base selectors.

## State And Persistence Behavior

This chunk stores no software state and persists nothing itself. It names hardware registers whose contents are owned by GC command processor, graphics pipeline, queue, cache, and shader hardware. Persistence and reset behavior are defined by the ASIC, firmware, power domains, and AMDGPU sequencing code, not by this header.

The named hardware state includes:

- Queue and command submission state: MQD/HQD base addresses, VMID, priorities, quantum, ring/pointer addresses, doorbell controls, active/dequeue status, IB controls, EOP buffers, context-save buffers, and DDID counters.
- Synchronization and memory operation state: scratch registers, append/atomic preop registers, semaphore wait/signal addresses, wait timeouts, DMA source/destination/command registers, coherency ranges, and command buffer sizes/bases.
- Graphics pipeline state: depth/stencil/color buffer bases and attributes, HTILE/DCC/FMASK metadata, scissor and viewport windows, sample locations and masks, rasterization and clip controls, shader input/interpolation formats, blend controls, primitive topology, streamout, tessellation, geometry, and draw/dispatch indirect addresses.
- GDS state: per-VMID GDS base/size, GWS and OA ownership, reset masks, compute wave-id limits, and context-switch counters.
- Debug and telemetry state: CP DMA watch registers, SPI graphics debug/trap controls, RLC GPM counters, GC CAC/DIDT/EDC/throttle counters, TCP performance filters, and CP/VGT/PA/SC invocation and primitive counters.

In `gfx_v10_0.c`, many registers from this range back real driver state transitions. For example, graphics MQD initialization reads and composes `mmCP_GFX_HQD_QUEUE_PRIORITY`, `mmCP_GFX_MQD_CONTROL`, `mmCP_GFX_HQD_VMID`, `mmCP_GFX_HQD_QUANTUM`, `mmCP_GFX_HQD_CNTL`, `mmCP_RB_DOORBELL_CONTROL`, and `mmCP_GFX_HQD_RPTR`. Compute queue initialization writes `mmCP_HQD_ACTIVE`, `mmCP_HQD_DEQUEUE_REQUEST`, PQ base/control/pointer registers, EOP base/control registers, MQD base/control registers, and doorbell controls. GDS clear and programming paths use offset arithmetic from `mmGDS_VMID0_BASE`, `mmGDS_VMID0_SIZE`, `mmGDS_GWS_VMID0`, and `mmGDS_OA_VMID0`.

## Dependencies And Integration Points

Syntactically this header depends only on the C preprocessor and its include guard from the full file. Semantically it must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h`, which defines matching register fields used with these offsets.
- AMD's generated GC 10.1.0 register database and address-block layout.
- SOC15 register helper macros in AMDGPU, especially helpers that combine hardware IP, instance, `mm...` offset, and `mm..._BASE_IDX`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c`, the direct consumer in this tree for GFX10 queue management, register dumps, golden settings, GDS setup, ring operations, and debug flows.
- GPU firmware and microcode expectations for CP/MEC/PFP/ME queue state, EOP handling, context save/restore, GDS allocation, and synchronization registers.
- UAPI-observable behavior through command submission, graphics and compute queue scheduling, KFD/AMDKFD integration, VMID/GDS assignment, preemption, reset, suspend/resume, and debug/register-dump paths.

Although the repository path includes `ceph-client`, this file is AMDGPU hardware metadata from a Linux kernel-style source tree. It does not implement Ceph, distributed filesystem behavior, network protocol handling, or persistent filesystem data structures.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong offset or base index compiles cleanly but directs MMIO reads or writes to the wrong register.
- Base-index mistakes are especially dangerous at the `gc_gfxdec0` and `gc_gfxudec` transitions. Many offsets in base index `1` are small values or high user offsets that only make sense under their correct address block.
- Queue descriptor registers are sequencing-sensitive. Wrong CP HQD/MQD/PQ/EOP/doorbell offsets can break queue activation, deactivation, preemption, ring pointer reporting, firmware handoff, or timeout recovery.
- The header exposes aliases for the same offset. Consumers must not assume every macro name identifies a unique register address when building dumps, validation lists, or generated documentation.
- Offset-only macros do not encode bitfields, access permissions, reset values, read-only/write-only behavior, write-one-to-clear behavior, sticky status, self-clearing behavior, clock-domain validity, or power-domain validity. Those semantics must come from the matching shift/mask header, hardware docs, and driver sequencing.
- Graphics state macros in the `gc_gfxdec0` block cover broad rendering state. Bad offsets can appear as subtle rendering corruption, hangs, incorrect depth/color resolves, blend/scissor bugs, or mode-specific failures rather than immediate compile errors.
- GDS offsets are used with register-offset arithmetic over VMIDs. A base offset or stride assumption error can corrupt the wrong VMID allocation or leave stale GWS/OA ownership after queue teardown.
- Counter, debug, and trap registers can affect diagnostics. Incorrect mappings can produce misleading register dumps, failed golden-setting programming, or debug traps that do not correspond to the failing hardware state.
- The chunk boundaries split macro pairs: line 4974 is only the previous register's `_BASE_IDX`, and line 7439 contains `mmVGT_PRIMITIVE_TYPE` without its following `_BASE_IDX`. Merge-time validation should tolerate these boundary artifacts while checking the full file for complete pairs.

## Test Signals

Useful validation is mostly compile-time, generation-time, and hardware-integration oriented:

- Build AMDGPU with GFX10 support so `gfx_v10_0.c` preprocesses successfully against `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h`.
- Mechanically verify that every complete `mm...` macro in the full file has the expected `mm..._BASE_IDX` partner, allowing this chunk's known start and end boundary splits.
- Cross-check this chunk against the authoritative GC 10.1.0 register database, especially address-block boundaries at `gc_spipdec`, `gc_cpphqddec`, `gc_didtdec`, `gc_gccacdec`, `gc_tcpdec`, `gc_gdspdec`, `gc_gfxdec0`, and `gc_gfxudec`.
- Diff generated offsets against nearby GC 10.x variants where the layout should be stable, while preserving known ASIC-specific deltas and aliases.
- Run or inspect GFX10 queue initialization, KIQ/compute queue setup, graphics queue setup, queue teardown, GPU reset, suspend/resume, and SR-IOV VF paths that read or write CP HQD/GFX HQD registers.
- Exercise GDS allocation and cleanup paths for compute queues and KFD workloads, checking `mmGDS_VMID0_*`, `mmGDS_GWS_VMID0`, and `mmGDS_OA_VMID0` offset arithmetic.
- Validate rendering and command submission workloads that stress DB/CB/PA/SPI/SX/VGT state, including depth/stencil, DCC/FMASK, scissor/viewport, MSAA sample locations, blend state, streamout, tessellation, indirect draw, and dispatch.
- Capture register dumps around hangs or resets and confirm CP HQD, CP GFX HQD, GDS, SPI trap, RLC perf, PA/CB/DB, and VGT registers decode at expected addresses.
- Run golden-settings programming paths for GFX10 ASIC variants and check for register-access faults or mismatches around PA, SPI, TCP, and related GC registers.

## Chunk Notes For Merge

This document covers only lines 4974-7439 of `gc_10_1_0_offset.h`. Earlier chunks should own the opening file license/include guard, earlier SDMA/RLC/GC blocks, and the register whose `_BASE_IDX` appears at line 4974. Later chunks should start by completing the `mmVGT_PRIMITIVE_TYPE_BASE_IDX` pair and continue the remaining `gc_gfxudec` and later GC 10.1.0 offset blocks. The final per-file report should treat the whole file as generated ASIC register-offset metadata consumed by AMDGPU GFX10 code, not as handwritten runtime control logic.

### subset-b-002447: lines 7440-9943

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h lines 7440-9943

## Purpose

This chunk is part of the generated AMD GC 10.1.0 register-offset map used by the amdgpu and amdkfd drivers. It contains preprocessor constants for memory-mapped graphics-core registers and their paired `_BASE_IDX` selectors. Driver code combines these constants with the SOC15 register-base table, for example through `SOC15_REG_OFFSET(GC, inst, mmRLC_CNTL)`, `RREG32_SOC15()`, and `WREG32_SOC15()`, to compute the final MMIO address for Navi/GC 10.1 hardware.

The range covers 1,214 register offset macros and 1,214 matching `_BASE_IDX` macros. It starts mid-block at the graphics pipeline/uconfig area with `mmVGT_INDEX_TYPE = 0x2243` and ends in the beginning of `gc_pwrdec` at `mmCGTS_SA0_WGP00_CU1_SIMD0_CTRL_REG = 0x5014`. All macros in this requested line range use base index `1`, meaning they are resolved against `adev->reg_offset[GC_HWIP][instance][1]` in SOC15-style accessors.

## Register Families In This Chunk

The opening pre-`gc_cprs64dec` portion continues an existing GC register block and includes:

- Draw/index/geometry setup: `mmVGT_INDEX_TYPE`, streamout filled-size registers, vertex index bounds, instance count/base ID, index buffer bases, primitive type state, and GE/VGT ring/offchip parameters.
- Rasterization and screen/trap controls: PA/SC line-stipple, screen extent, trap screen, and HP3D/P3D trap registers.
- Shader and cache debug/control: `mmSQ_THREAD_TRACE_USERDATA_*`, `mmSQC_CACHES`, `mmSQC_WRITEBACK`.
- Depth buffer and query counters: `mmDB_OCCLUSION_COUNT*_LOW/HI`, `mmDB_ZPASS_COUNT_LOW/HI`.
- GDS direct read/write/atomic windows and related atomics/completion registers.
- SPI and wave-limit remap registers, including `mmSPI_WAVE_LIMIT_CNTL_REMAP`.

Named address blocks beginning inside this chunk are:

- `gc_cprs64dec` at base `0x32000`: CP/MES program counter, instruction pointer, MQD base, header dump, queue ownership, VMID, scheduler/debug registers, MES performance counters, and RLC/CP-visible event/state registers.
- `gc_gusdec` at base `0x33000`: GUS command, credit, FIFO, retry, cache, read/write path, and XCD/EA/GC interface controls.
- `gc_gl1dec`, `gc_chdec`, and `gc_gl2dec` at bases `0x33400`, `0x33600`, and `0x33800`: GL1/GL2 arbitration, cache disable, bank selection, pipe steering, channel arbitration, and cache status/control registers.
- `gc_perfddec` at base `0x34000`: low/high result registers for CPG, CPF, CPC, CP, SPI, SQ, SX, TA, TD, TCP, TCC/GL2, CB, DB, PA, CH, GCEA, GCR, GUS, and GCMC/VM L2 performance counters.
- `gc_gcatcl2pfcntrdec`, `gc_gcvml2prdec`, `gc_gcvml2perfddec`, and `gc_gcatcl2perfddec`: small result-register blocks for GC ATC L2 and GCMC VM L2 counters.
- `gc_perfsdec` at base `0x36000`: select/control/mode registers that program the performance counters whose result registers appear in the preceding performance-data blocks.
- `gc_gcatcl2pfcntldec`, `gc_gcvml2pldec`, `gc_gcvml2perfsdec`, and `gc_gcatcl2perfsdec`: ATC/VM L2 performance-counter configuration, select, and mode registers.
- `gc_rlcdec` at base `0x3b000`: the main RLC block, including `mmRLC_CNTL`, firmware/program-counter state, save/restore control, GPU idle/status, safe-mode, performance monitors, SPM, SRM, SMU messaging, power-gating, CP table/DMA/AXI integration, scratch, and debug/capture registers.
- `gc_rlcrdec` at base `0x3b800`: RLC SPP CAM and PACE scratch address/data windows.
- `gc_rlcsdec` at base `0x3b980`: RLC sequence-controller decode registers, exception/general state, clock-gating/deep-sleep controls, IOV status, GRBM soft reset, interrupt handoff, WGP read/status, bootload status, and auxiliary registers.
- `gc_pwrdec` at base `0x3c000`: the first CGTS power/clock-gating and clock-monitor registers for shader-array/quadrant and early WGP/CU controls.

## Important APIs, Types, And Generated Constants

There are no C functions, structs, or runtime control-flow constructs in this chunk. The important API is the macro namespace:

- `mm<REGISTER>` constants hold register offsets such as `mmRLC_CNTL = 0x4c00`, `mmCP_MES_PRGRM_CNTR_START = 0x2800`, and `mmCGTS_STATUS_REG = 0x500c`.
- `mm<REGISTER>_BASE_IDX` constants select which per-IP base slot to add to the offset. Every paired macro in this range is `1`.
- The file-level include guard `_gc_10_1_0_OFFSET_HEADER` makes the generated map safe to include from multiple driver compilation units.

The macros are paired with sibling generated files in the same directory:

- `gc_10_1_0_sh_mask.h` supplies field shifts and masks for these registers.
- `gc_10_1_0_default.h` supplies reset/default values for many of the same register names.
- Other GC generations, such as `gc_10_3_0_offset.h`, carry similar names but sometimes different offsets; callers must include the header matching the IP version.

## Control Flow And Runtime Use

This header contributes only compile-time constants. Runtime control flow appears in its consumers. The standard path is:

1. A GC 10.1.0 driver source includes `gc/gc_10_1_0_offset.h`.
2. The source passes an `mm...` name to an accessor such as `RREG32_SOC15(GC, 0, mmRLC_CNTL)`.
3. `SOC15_REG_OFFSET` computes `adev->reg_offset[GC_HWIP][0][mmRLC_CNTL_BASE_IDX] + mmRLC_CNTL`.
4. The low-level MMIO read/write helper accesses the computed register address.

Direct consumers found in this tree include `amdgpu/gfx_v10_0.c`, KFD queue/MQD management for GFX10, gfxhub/mmhub/sdma/Navi glue, and virtualization-related Navi code. `gfx_v10_0.c` uses registers from this line range for debug/register dumps (`mmCP_MES_*`, `mmRLC_RLCS_*`), RLC enable/disable and status handling (`mmRLC_CNTL`), and RLC bootload polling (`mmRLC_RLCS_BOOTLOAD_STATUS`).

Command processor packet emission can also use these offsets indirectly. For registers that are programmed through packetized UCONFIG/context paths, callers often subtract packet start constants after `SOC15_REG_OFFSET` resolves the MMIO offset; that makes the exact `mm...` value observable in ring command streams, not only in direct MMIO.

## State And Persistence Behavior

The header itself stores no mutable state and performs no persistence. It names hardware state that persists in GPU registers until reset, power transition, firmware action, or explicit driver writes change it. The relevant state domains include:

- Draw/geometry command state, query counters, streamout counters, GDS windows, and SPI/SQ trace state.
- CP/MES scheduling and queue state, including MQD, VMID, program counter, scheduler, and debug state.
- GL1/GL2/GUS/cache configuration and performance-counter selection/result state.
- RLC firmware, save/restore, power-gating, clock-gating, scratch, interrupt, and bootload state.
- CGTS clock-gating and shader-array/WGP/CU clock-monitor state at the start of `gc_pwrdec`.

Because these names map to live MMIO registers, persistence is owned by the hardware and by the surrounding driver sequences. The same offset constant may be read-only, write-only, read/write, destructive-on-read, counter-like, or firmware-owned depending on the hardware register semantics documented outside this header.

## Dependencies And Integration Points

This chunk depends on the AMD-generated register database being internally consistent. Each register must have a matching `_BASE_IDX` macro and must align with the same register name in the mask/default headers when those files expose fields or defaults.

The main integration point is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15_common.h`, where `SOC15_REG_OFFSET` adds `reg##_BASE_IDX` and `reg` to `adev->reg_offset`. That means a bad offset or bad base index silently redirects all `RREG32_SOC15/WREG32_SOC15` operations for that register. The base-index value is not decorative; it selects the correct aperture within the GC IP block.

Other integration points include:

- GFX10 bring-up, suspend/resume, reset, RLC firmware boot, and power-management paths in `gfx_v10_0.c`.
- KFD queue and MQD programming paths that include the same GC 10.1.0 offsets.
- Performance-monitor programming, where select/mode registers in `gc_perfsdec` must correspond to result registers in `gc_perfddec`.
- Register dump and debug tables, where `SOC15_REG_ENTRY_STR` stores these symbolic names for diagnostics.
- ASIC generation selection in Navi/GC IP discovery code; including a neighboring generation's offset file can compile but target the wrong hardware address.

## Risks And Maintenance Notes

- Generated headers are easy to treat as inert, but an incorrect value changes real MMIO behavior. A single wrong `mmRLC_CNTL`, `mmRLC_RLCS_BOOTLOAD_STATUS`, or `mmCGTS_*` offset can break firmware boot, reset, power gating, or diagnostics.
- The chunk begins at line 7440 with `mmVGT_PRIMITIVE_TYPE_BASE_IDX`; the corresponding `mmVGT_PRIMITIVE_TYPE` macro is just before the chunk. Merge tooling should not infer that the logical register family starts at the chunk boundary.
- All macros in this line range use `_BASE_IDX 1`. If a future regeneration changes an offset into another SOC15 base segment, accessors will compile unchanged but compute different physical addresses.
- Many register names exist across GC 9, GC 10.1, GC 10.3, and later headers. Cross-generation copy/paste can produce values that look plausible while targeting the wrong IP version.
- Performance-counter families are split across result, select, mode, and configuration blocks. Mismatched counter-numbering between these blocks can produce misleading metrics rather than obvious driver failures.
- RLC and RLC_RLCS registers are firmware-sensitive. Writes outside the expected sequencing can race firmware, reset flows, power-gating transitions, or SR-IOV scheduling state.
- Several macros name windows or indirect address/data pairs, such as GDS windows, SPP CAM, PACE scratch, and RLC data windows. Correct usage requires ordering and polling behavior that is not represented in the offset header.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing checks:

- Build coverage for all GC 10.1.0 consumers, especially `gfx_v10_0.c`, KFD GFX10 queue/MQD code, and SOC15 register dump paths.
- Static checks that every non-`_BASE_IDX` macro in the chunk has a paired `_BASE_IDX` macro and that all pairs in this range remain base index `1` unless the SOC15 base table is intentionally updated.
- Header consistency checks that fields in `gc_10_1_0_sh_mask.h` and defaults in `gc_10_1_0_default.h` reference register names present in the offset header.
- Boot and reset tests on GC 10.1 hardware that exercise RLC enable/disable, RLC bootload status polling, GRBM idle checks, and safe-mode transitions.
- KFD queue creation/destruction tests that touch CP/MES and MQD-related registers from `gc_cprs64dec`.
- Perf-counter smoke tests that program select/mode registers and verify matching low/high result registers increment for CP/SPI/SQ/TCP/GL2/DB/PA/GUS/VM-L2 counter families.
- Suspend/resume and runtime power-management tests that exercise RLC, CGTS, clock-gating, and power-gating register paths.
- SR-IOV or virtualization tests for the RLC IOV, VM busy, scheduler block, and doorbell-monitor registers when that mode is supported.

### subset-b-002448: lines 9944-11375

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h lines 9944-11375

## Purpose

This chunk is the final slice of the generated AMD Graphics Core 10.1.0 register-offset header. It defines numeric register offsets and register-base indices for AMDGPU GC blocks; it does not contain executable driver logic. Consumers include the header to translate symbolic register names into MMIO register offsets (`mm*`) or indirect-register indices (`ix*`) used by AMDGPU register access helpers and generated register tables.

Although the repository path is under a local `ceph-client` source mirror, this file is GPU driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

The requested range contains 1,432 lines and 1,389 `#define` statements: 793 direct `mm*` register defines, 596 indirect `ix*` register-index defines, and 397 `_BASE_IDX` defines. It starts in the middle of the CGTS per-WGP control-register grid, after `mmCGTS_SA0_WGP00_CU1_SIMD0_CTRL_REG` was defined in the previous chunk, and ends at the file-level `#endif` after the DIDT indirect-register block.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, allocations, or direct MMIO operations in this range. The interface is entirely preprocessor constants:

- `mm<REGISTER>`: direct GC register offset used by AMDGPU MMIO access macros and generated register lists.
- `mm<REGISTER>_BASE_IDX`: register-base selector for direct-register access. Every `_BASE_IDX` in this chunk is `1`, matching the GC base segment used by these addresses.
- `ix<REGISTER>`: indirect-register index for indexed access spaces such as CAC, SPM, SQ, and DIDT.
- `// addressBlock: ...` comments: generated boundaries that identify the hardware register namespace or indirect aperture for the following defines.

The chunk covers these major groups:

- CGTS and CGTT clock-gating/control offsets before the first visible address-block marker. This includes `mmCGTS_SA*_WGP*_CU*_{SIMD0,SIMD1,TATD,TCP}_CTRL_REG` entries for shader-array/WGP/CU units, plus clock controls for SPI, PC, BCI, VGT, IA, WD, GS/NGG, PA, SC, SQ, SX, TD, TA, TCP, GDS, DB, CB, GL2, CP, RLC, RMI, GCR, UTCL1, GCEA, SE/GC CAC, GRBM, GL1, CH, GUS, and PH.
- `gc_hypdec` at base `0x3e000`: command processor, RLC, GRBM, interrupt-cookie, and GPU I/O virtualization registers. It includes ucode address/data pairs for PFP, CE, MEC, GPM, PACE, GPU_IOV, RLCV, RLCP; instruction/data cache base controls; MES instruction/data/local apertures and bounds; GRBM CAM and indexed SR controls; RLC GPU_IOV scheduling, status, reset, timer, doorbell, mask, interrupt, semaphore, checksum, scratch, and bootload registers.
- `gc_sdma0_sdma0hypdec` and `gc_sdma1_sdma1hypdec` at bases `0x3e200` and `0x3e280`: mirrored SDMA virtualization/ucode/VM context registers for SDMA0 and SDMA1, including `UCODE_ADDR`, `UCODE_DATA`, `VM_CTX_LO/HI`, `ACTIVE_FCN_ID`, `VM_CTX_CNTL`, `VIRT_RESET_REQ`, `VF_ENABLE`, `CONTEXT_REG_TYPE0..3`, and `VM_CNTL`.
- `gc_gcvmsharedhvdec` at base `0x3ea00`: shared GCVM virtualization aperture definitions. It maps per-VF framebuffer size/offset registers for VF0 through VF31, MARC base/relocation/length registers, IOMMU controls, PCIe ATS controls for the PF and VF0 through VF31, a GCUTCL2 clock-gating register, and shared active-function state.
- `gccacind`: indirect graphics-core clock/activity counter and power-control registers. It includes PCC and power-break stall-pattern controls, GC CAC ID/control/override, per-block activity weights, per-block accumulators, per-block override registers, stall/release/power-break LUTs, fixed-pattern performance counters, and hardware LUT update status.
- `secacind`: a small shader-engine CAC indirect block with SE CAC ID/control/override select/value registers.
- `spmglbind`: global SPM sample-delay indirect registers for CPG/CPC/CPF, GDS/GCR/PH/GE/GUS, CH/ATCL2/VML2, SDMA, GL2A, GL2C, EA, and CHC instances.
- `spmind`: shader-engine SPM sample-delay indirect registers for SPI, SQG, CBR/DBR, SA0/SA1 graphics subblocks, per-WGP TA/TD/TCP units, and GL1/CB/DB/SC/RMI paths.
- `sqind`: shader queue indirect debug and wave-state registers such as `ixSQ_DEBUG_STS_LOCAL`, wave mode/status/trap status, hardware IDs, GPR/LDS allocation, IB state, wave PC/instruction, TTMP registers, M0, EXEC, flat scratch, XNACK mask, and overlapping interrupt-word aliases.
- `didtind`: deterministic/dynamic induced throttling indirect registers for SQ, DB, TD, and TCP blocks. Each block exposes control, OCP, stall, tuning, auto-release, stall-pattern, scale-factor, release-count/status, weight, EDC threshold/timer/delay/status/overflow/rolling-delta/PCC counter, and final stall-event-counter indices.

## Control Flow

This header has no runtime control flow. Runtime behavior appears only after another AMDGPU source file includes the header and expands these macros:

1. A GC 10.1.0 consumer selects a direct `mm*` register offset or an indirect `ix*` register index.
2. For direct registers, the consumer pairs the offset with its `_BASE_IDX` and uses AMDGPU register helpers for reads, writes, read-modify-write operations, polling, register dumps, or generated initialization sequences.
3. For indirect registers, the consumer programs the appropriate selector/data aperture for the address block and uses the `ix*` value as the indexed register address.
4. Hardware, firmware, microcontrollers, and virtualization paths perform the actual clock-gating, cache, command-processor, SDMA, VM, CAC, SPM, SQ debug, or DIDT behavior.

The only sequencing implied by this chunk is external to the header. Examples include loading CP/RLC/SDMA microcode through address/data pairs, configuring MES apertures and bounds, selecting active virtual functions, programming GPU_IOV scheduling and resets, setting per-VF GCVM/ATS windows, sampling SPM counters, reading SQ wave state, and adjusting CAC/DIDT power-throttling tables.

## State And Persistence Behavior

The macros are stateless compile-time constants. They name hardware-visible state but do not store it. Register contents live in GPU hardware, firmware-owned SRAMs, indirect-register banks, or virtualization apertures and may be volatile, latched, write-one-to-clear, self-clearing, retained, or reset depending on the owning block.

State named by this chunk includes:

- Clock-gating and clock-control state across graphics front-end, shader, texture, cache, command-processor, RLC, memory, and hub blocks.
- Command-processor and RLC microcode addressing/data state, instruction/data cache base state, MES local aperture state, and RLC scratch/bootload/reset/checksum state.
- GPU I/O virtualization state: active function IDs, VF enable masks, scheduling registers, doorbell status/set/clear, VM busy status, interrupt status/disable/force, virtual reset requests, semaphores, SMU/RLC responses, and per-SDMA virtualized context registers.
- GCVM state: per-VF framebuffer size/offset registers, MARC base/relocation/length windows, IOMMU controls, and PCIe ATS controls.
- CAC and DIDT state: per-block activity weights, accumulators, overrides, stall/release/power-break patterns, EDC thresholds/timers/delays/status, rolling power deltas, and throttling/event counters.
- SPM and SQ debug state: global and per-shader-engine sample delays, wave execution/debug registers, temporary wave registers, program counter, EXEC mask, scratch/XNACK state, and interrupt-word aliases.

Persistence is hardware-defined and outside this header. Values can be initialized during GPU bring-up, rewritten by firmware or power-management code, reset during GPU reset or virtualization reset, reprogrammed during suspend/resume, and changed by debug/profiling flows. The header does not define reset values, access permissions, legal field encodings, locking rules, polling timeouts, or ownership between PF, VF, firmware, and host driver.

## Dependencies And Integration Points

This generated offset header must stay synchronized with the GC 10.1.0 register database and with companion shift/mask headers that describe bit fields for the same symbolic registers. Integration points include:

- AMDGPU GC 10.1.0 support code under `drivers/gpu/drm/amd/`, especially graphics, command processor, SDMA, RLC, MES, VM, virtualization, power management, profiling, and debug paths.
- Companion generated headers in `drivers/gpu/drm/amd/include/asic_reg/gc/`, such as GC 10.1.0 shift/mask headers and neighboring generation offset headers.
- Register-access helpers that combine `mm*` offsets, `_BASE_IDX` selectors, and field masks/shifts from companion headers.
- Microcode loading paths for CP PFP/CE/MEC, RLC GPM/PACE/GPU_IOV/RLCV/RLCP, and SDMA0/SDMA1.
- SR-IOV/GPU virtualization paths that manage VF enablement, active function IDs, per-VF framebuffer/ATS/MMIO state, virtual resets, doorbell status, scheduling, and interrupt reporting.
- Profiling, telemetry, and power-management flows using CAC, SPM, SQ wave debug, and DIDT indirect registers.

The range crosses multiple generated address spaces. Direct `mm*` offsets use the GC base-index convention, while `ix*` defines are offsets inside specific indirect register banks. Consumers must not mix these access methods.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong offset can compile cleanly while targeting the wrong GPU register.
- The file is generated. Manual edits risk divergence from AMD's register database, silicon documentation, firmware assumptions, and matching shift/mask headers.
- The first requested line is a continuation of the CGTS register family: `mmCGTS_SA0_WGP00_CU1_SIMD0_CTRL_REG` itself is in the previous chunk, while this chunk begins with its `_BASE_IDX`.
- Several symbols intentionally alias the same offset, such as `mmCP_ME_RAM_RADDR` and `mmCP_ME_RAM_WADDR`, `mmCP_MES_IC_BASE_*` and `mmCP_MES_MIBASE_*`, `mmCP_MES_DC_BASE_*` and `mmCP_MES_MDBASE_*`, `mmGRBM_CAM_*` and `mmGRBM_HYP_CAM_*`, and the SQ interrupt-word aliases at `0x20c0`. Deduplication tools must preserve aliases because different driver paths may use semantic names.
- Direct `mm*` and indirect `ix*` names are easy to confuse. Using an `ix*` value through a direct MMIO helper, or using an `mm*` offset through an indirect aperture, can silently access unrelated hardware.
- Virtualization registers are sensitive to PF/VF ownership, active-function selection, scheduling windows, doorbell status, and reset/interrupt handshakes. Incorrect offsets can break isolation or leave a VF stuck after reset.
- Microcode address/data pairs require ordered writes and hardware-specific handshakes. Offset mistakes may corrupt firmware load, cache base programming, or scratch/bootload state.
- CAC, SPM, SQ debug, and DIDT paths are diagnostic or power-management oriented and may be sampled or modified while hardware is active. Incorrect register definitions can produce misleading counters, over-throttle/under-throttle blocks, or disturb wave/debug state.
- The final chunk ends at the file `#endif`; there is no following chunk for this source file. The merged per-file report should note that this slice closes the header.

## Test Signals

Useful validation for this generated header and its consumers includes:

- Build AMDGPU configurations that include GC 10.1.0 support; missing or renamed macros should surface as compile failures in register-table, graphics, SDMA, RLC, VM, virtualization, or debug code.
- Mechanically compare the full header against the authoritative GC 10.1.0 register database, checking offset values, `_BASE_IDX` values, address-block boundaries, and intentional alias symbols.
- Cross-check each `mm*` register used by code with the matching shift/mask header for GC 10.1.0, especially CP/RLC/SDMA/GCVM/GPU_IOV/CAC/DIDT registers.
- Exercise boot, firmware loading, ring initialization, graphics queues, SDMA queues, MES paths, suspend/resume, GPU reset, and SR-IOV VF reset/enable flows on GC 10.1.0 hardware.
- Validate register dumps for CP/RLC/SDMA microcode address/data windows, MES apertures, GPU_IOV state, GCVM VF windows, PCIe ATS controls, and active function IDs against known-good hardware traces.
- Run profiling and telemetry checks that read SPM sample-delay registers, CAC accumulators/weights/overrides, SQ wave debug state, and DIDT counters without producing access faults or inconsistent decoded output.
- Watch for kernel logs indicating MMIO faults, ring test failures, firmware load failures, SDMA VM context failures, VM/IOMMU/ATS faults, stuck virtual resets, lost GPU_IOV interrupts, repeated doorbell-status errors, and abnormal power-throttling behavior.

## Cross-Chunk Notes

The previous chunk owns the beginning of the final direct-GC register group, including the `mmCGTS_SA0_WGP00_CU1_SIMD0_CTRL_REG` offset line immediately before this range. This chunk resumes at that symbol's `_BASE_IDX`, completes the remaining CGTS/CGTT direct offsets, covers the hypervisor, SDMA, GCVM, CAC, SPM, SQ, and DIDT address blocks, and closes `gc_10_1_0_offset.h` with `#endif`.
