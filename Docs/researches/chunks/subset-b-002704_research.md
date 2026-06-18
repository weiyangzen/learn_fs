# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_7_2_enum.h lines 1-4779

## Scope

This chunk covers the opening 4,779 lines of the generated AMD GFX 7.2 enum header. The full file is 6,280 lines, so this slice starts at the license/include guard and ends inside the `VGT_EVENT_TYPE` enum after `Reserved_0x0E`. It contains 153 `typedef enum` blocks, 1,268 `#define` constants, and no functions, structs, storage definitions, branches, loops, locks, allocations, or direct register I/O.

The header is a hardware vocabulary map: symbolic names for register field values, packet/event values, performance counter selectors, shader instruction encodings, texture/resource descriptor fields, cache operation opcodes, and primitive assembly controls for the GFX 7.2-era AMD graphics core.

## Purpose

`gfx_7_2_enum.h` lets AMDGPU code program and decode GFX 7.2 hardware using named constants instead of raw numeric literals. It complements generated offset and shift/mask headers in the same ASIC register tree. Where the offset headers identify registers and the shift/mask headers identify bit positions, this file names legal values for many of those bitfields and for several packet, shader, texture, and performance-monitor encodings.

Major domains covered in this chunk are:

- Color buffer and render target state: `SurfaceNumber`, `SurfaceSwap`, `CBMode`, `SourceFormat`, `BlendOp`, `CombFunc`, `BlendOpt`, `CmaskCode`, and `CBPerfSel`.
- Command processor and address-space constants: CP ring/pipe/ME identifiers, CP/SPM perfmon states, semaphore/IQ result values, VMID width, and config/uconfig/persistent/context register ranges.
- Depth buffer and raster state: `ForceControl`, `ZSamplePosition`, `ZOrder`, `ZpassControl`, `ZModeForce`, `ZLimitSumm`, `CompareFrag`, `StencilOp`, `ConservativeZExport`, `DbPSLControl`, and the large DB `PerfCounter_Vals` table.
- Global graphics/per-shader-engine performance selectors: GRBM, per-SE GRBM, SU, SC, SPI, SQ, SQC, TC/TCC/TCA/TCS/TA/TD/TCP selector enums.
- Raster configuration fields: SE/SC/PKR/RB x/y/map selector enums and tiling table size constants.
- Shader processor fields and opcodes: SQ texture/resource enums, wave/thread-trace enums, indirect command/debug enums, exception IDs, instruction encoding masks, waitcnt/sendmsg field sizes, SGPR/VGPR/register IDs, SOP/VOP/SMRD/FLAT opcode values, comparison conditions, flat memory operations, atomics, and hardware register IDs.
- Texture, vertex, and resource descriptors: `TEX_*`, `VTX_*`, `TVX_*`, texture dimension/filter/aniso/border/depth compare fields, resource type, swizzles, data formats, sampler validity, and vertex fetch modes.
- Texture/cache operation and cache policy values: `TC_OP_MASKS`, `TC_OP`, CHUB/TC credit enums, `TC_NACKS`, `TCP_CACHE_POLICIES`, `TCP_CACHE_STORE_POLICIES`, and `TCP_WATCH_MODES`.
- Front-end primitive/event controls: `VGT_OUT_PRIM_TYPE`, `VGT_DI_PRIM_TYPE`, `VGT_DI_SOURCE_SELECT`, `VGT_DI_MAJOR_MODE_SELECT`, `VGT_DI_INDEX_SIZE`, and the beginning of `VGT_EVENT_TYPE`.

## Exported API Surface

The public surface is entirely compile-time C symbols:

- 153 named enums whose enumerators are intended to be written into specific ASIC register fields or compared against hardware-reported values.
- 1,268 preprocessor constants for values that are not modeled as enums, including register-space boundaries, shader instruction encoding masks, instruction opcodes, source/register IDs, field widths/shifts, special instruction IDs, cache operation masks, and hardware limits.
- An include guard, `GFX_7_2_ENUM_H`.

Important enum families include:

- Render/color fields: numeric format (`NUMBER_UNORM` through `NUMBER_FLOAT`), channel swap, color-buffer mode, blend factors/equations, fast-clear/fmask/decompress modes, and color-buffer performance selectors.
- CP/perf monitor fields: `CP_RING_ID`, `CP_PIPE_ID`, `CP_ME_ID`, `SPM_PERFMON_STATE`, `CP_PERFMON_STATE`, `CP_PERFMON_ENABLE_MODE`, `CPG_PERFCOUNT_SEL`, `CPF_PERFCOUNT_SEL`, `CPC_PERFCOUNT_SEL`, and `CP_ALPHA_TAG_RAM_SEL`.
- DB/PA/SC fields: depth/stencil compare and op values, Z ordering and forced-Z policy, DB performance selectors, pixel pipe counter IDs/stride, rasterizer/packer/render-backend mapping selectors, and scan converter performance selectors.
- SPI/SQ fields: shader export formats, sample/fog/point-sprite modes, shader-stage perf selectors, SQ texture/resource descriptors, wave types, thread trace token/mode/capture settings, indirect debug command modes, exception and interrupt encoding, RAT export instructions, instruction buffer states, and memory alignment modes.
- Texture/cache fields: texture descriptor enums mirror sampler and image resource state, while `TC_OP` names read/write, L1/L2 invalidate/writeback, 32/64-bit atomics, return/no-return atomics, and denorm-flushing variants.
- VGT draw interface fields: primitive topology, index size, source selection, major mode, output primitive type, and initial event IDs.

There are no callable APIs in this chunk. Consumers include the header and feed constants into register programming macros, packet builders, debug/performance-counter setup, or generated initialization tables.

## Control Flow And State Behavior

This header has no software control flow. The runtime behavior comes from driver code that uses these values when programming GFX hardware.

The values in this chunk describe several hardware state machines:

- Color/depth pipeline state: CB mode, blend, compare, stencil, fast clear, fmask decompress, Z ordering, and conservative Z export values determine how render targets and depth/stencil surfaces are processed.
- Command submission and context state: ring, pipe, ME, VMID, register-space range, semaphore, IQ, and perfmon values describe CP-visible queues, contexts, and monitoring state. The `CONFIG_SPACE`, `UCONFIG_SPACE`, `PERSISTENT_SPACE`, and `CONTEXT_SPACE` ranges are especially relevant to register shadowing and context switching.
- Performance monitoring state: numerous `*_PERF_SEL` tables select which internal signal a hardware counter observes. The file does not configure counters itself; it only supplies selector values.
- Shader execution/debug state: SQ constants name wave types, thread trace token classes, indirect command operations (`HALT`, `RESUME`, `KILL`, `DEBUG`, `TRAP`), exception classes, hardware register IDs, instruction encodings, and opcodes used by shader debug, disassembly, trap, and performance tooling.
- Texture/cache state: texture/resource descriptor enums and TC/TCP/TCC selectors control or observe cache access type, locality policy, atomics, invalidation/writeback, descriptor formats, and texture addressing/filtering behavior.
- Primitive assembly state: VGT draw-interface enums define primitive topology, index size, source selection, major mode, and event encodings that command streams can use to drive front-end synchronization and draw setup.

No software-owned state is persisted by this file. Hardware state programmed with these constants persists according to ASIC rules: context registers may be saved/restored by CP/RLC context management, persistent register ranges may survive context switches, and caches/performance counters/events retain or reset state according to register writes, power transitions, GPU reset, suspend/resume, and firmware behavior.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor and C enum support. The semantic dependency is AMD's generated GFX 7.2 register database; these numeric values must match the companion generated register headers for the same ASIC family, especially offset and shift/mask files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/`.

Direct include sites found in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik_sdma.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v6_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v7_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v7.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v6_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v8_0.c`

Those include sites place this enum namespace in the GFX6/GFX7/CIK graphics, SDMA, KFD compute, and display bring-up/debug compilation units. Some constants are likely consumed through macros, register tables, or generated code rather than direct textual references, so integration analysis should consider all files that include the header, not only direct enumerator-name matches.

The header also overlaps conceptually with later-generation generated enum files, such as `navi10_enum.h`, where many selector names reappear with generation-specific numeric values. Cross-generation code must not assume that a value copied from GFX 7.2 is valid for a different ASIC unless that generation's enum header confirms it.

## Risks

- Numeric drift is the central risk. These constants are hardware ABI values; a wrong enum value or opcode can write a legal-looking but incorrect bit pattern into a register or command stream.
- This chunk mixes unrelated domains in one global namespace. Common names such as `SQ_F`, `SQ_LT`, `SQ_EQ`, and repeated `RESERVED_*` patterns can collide with assumptions in handwritten code or make grep-based review misleading.
- The file does not encode read/write permissions, reserved-value hazards, per-ASIC feature masks, or whether a field is context, persistent, privileged, debug-only, PF-only, or safe for virtual functions. Callers must get those rules from the register spec and surrounding driver logic.
- Performance selector tables are dense and easy to shift accidentally. One inserted/missing selector in `CBPerfSel`, `PerfCounter_Vals`, `SC_PERFCNT_SEL`, `SQ_PERF_SEL`, `TC*_PERF_SEL`, or `TCP_PERFCOUNT_SELECT` can silently make profiling data meaningless.
- Shader instruction constants are especially sensitive. Incorrect `SQ_ENC_*` masks, opcode values, source/register IDs, waitcnt fields, flat memory opcodes, or RAT export opcodes can break disassembly, trap/debug handling, command-generated shaders, or low-level compute diagnostics.
- Cache operation constants such as `TC_OP_WBINVL1`, `TC_OP_WBINVL2`, `TC_OP_INVL2_VOL`, and atomic variants affect coherency and ordering. Misuse can cause stale memory, excessive invalidation, or incorrect atomic behavior.
- Primitive and event IDs are command-stream ABI values. Wrong `VGT_DI_PRIM_TYPE`, source selection, index size, or event type values can corrupt draw interpretation or synchronization.
- The chunk boundary splits `VGT_EVENT_TYPE`; a final per-file report must merge with later chunks before treating the event enum or include guard as complete.

## Test Signals

Useful validation is mostly build-time, generated-header, and hardware-integration oriented:

- Compile/preprocess the direct include users: `cik.c`, `cik_sdma.c`, `gfx_v6_0.c`, `gfx_v7_0.c`, `amdgpu_amdkfd_gfx_v7.c`, `dce_v6_0.c`, and `dce_v8_0.c`.
- Generated-header checks that enum values match AMD's GFX 7.2 register database and companion shift/mask headers, with special attention to dense selector ranges and shader opcode blocks.
- Static checks for duplicate or suspicious macro names in the global namespace, accidental reordering of perf selectors, and chunk-boundary integrity for `VGT_EVENT_TYPE`.
- Rendering tests on GFX7/CIK-era hardware covering blend modes, render target formats, fast clear/fmask decompress, depth/stencil compare and stencil ops, early/late Z, and primitive topology/index-size combinations.
- Command processor and KFD tests covering rings, pipes, ME selection, VMID/context programming, queue dispatch, preemption, semaphore/IQ paths, and CP/SPM performance monitoring.
- Shader diagnostics and compute tests covering SQ thread trace, traps, exception reporting, flat memory loads/stores/atomics, waitcnt behavior, RAT exports, SGPR/VGPR limits, and wave debug commands.
- Texture/cache tests covering image and buffer formats, sampler clamp/filter/aniso/depth-compare modes, swizzle selection, cache policy, L1/L2 invalidation/writeback, volatile accesses, and atomics with and without return values.
- Performance counter smoke tests that program representative CB, DB, GRBM, SU, SC, SPI, SQ/SQC, TCC/TCA/TCS, TA, TD, and TCP selectors and verify plausible nonzero/zero behavior under targeted workloads.

## Chunk Notes For Merge

This document intentionally covers only lines 1-4,779 of `gfx_7_2_enum.h`. The source file continues after this chunk with the rest of `VGT_EVENT_TYPE` and additional generated enum/define content before the include guard closes. The final per-file document should treat this file as one generated hardware ABI map for AMD GFX 7.2 register-field, command/event, shader, texture, cache, and performance-monitor constants, not as executable driver logic.
