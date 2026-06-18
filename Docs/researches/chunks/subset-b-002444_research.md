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
