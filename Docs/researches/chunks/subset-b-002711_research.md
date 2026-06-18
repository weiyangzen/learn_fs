# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_enum.h lines 1-4749

## Scope

This chunk is the first 4,749 lines of the generated-style AMD GFX 8.0 enum/value header. It starts with the AMD license block and include guard, then defines C `typedef enum` groups and raw `#define` constants for register-field values, performance-counter select values, shader instruction encodings, resource descriptor encodings, texture/vertex fetch formats, and texture-cache operation/performance selectors.

There are no functions, structs, global variables, includes, allocations, locks, loops, callbacks, or runtime branches in this range. The selected range ends inside `TCC_PERF_SEL` after `TCC_PERF_SEL_CLIENT119_REQ`; that enum continues in the next chunk and should be reconciled there for full-file research.

Although the source path sits under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for AMD GFX 8.0 graphics IP. It is not Ceph filesystem logic.

## Purpose

`gfx_8_0_enum.h` gives AMDGPU code symbolic names for numeric values programmed into or decoded from GFX 8.0 registers and command/shader encodings. Companion offset and shift/mask headers identify register addresses and bit positions; this file supplies the value domains that go into those fields.

The chunk covers these main domains:

- Color-buffer and blend state: surface number formats, channel swaps, CB operating modes, blend factors, combine functions, blend optimizations, CMASK codes/addressing, and a large `CBPerfSel` selector set for CB/cache/DCC/blend events.
- Command processor and perfmon controls: ring, pipe, ME identifiers, stream/CP perfmon states, CP perfmon enable modes, CPG/CPF/CPC perf selectors, CP alpha tag RAM selection, semaphore/IQ interrupt constants, and register-space range constants.
- Depth/stencil and DB instrumentation: Z ordering/force modes, compare and stencil operations, conservative-Z export, DB PSL control, DB `PerfCounter_Vals`, pixel-pipe counter IDs, strides, and GB EDC/tiling constants.
- Graphics/rasterization blocks: GRBM and per-shader-engine perf selectors, SU and SC performance selector tables, raster configuration map selectors for shader engines, scan converters, packers, and render backends.
- SPI and SQ descriptors/debug/performance: SPI sampling/fog/point-sprite values, SPI performance selectors, shader export formats, clock-gating modes, texture resource and sampler values, wave/thread-trace token values, SQ performance selectors, indirect SQ commands, EDC source selection, rounding and interrupt encodings, export/RAT instruction values, wave-buffer status values, shader memory modes, and thread-trace start prefix.
- Shader ISA encoding constants: instruction encoding masks/fields, counts/offsets for VOP/SOP/SMEM/DS/MUBUF/MTBUF/MIMG/EXP/FLAT encodings, register IDs, literal/source selectors, waitcnt fields, instruction opcodes, data-share operations, image operations, flat operations, scalar/vector compare and arithmetic opcodes, DPP/SDWA controls, system messages, hardware register IDs, and trap-related IDs.
- Texture and vertex fetch domains: texture border/chroma/clamp/coordinate/depth/dimension/format/filter/request/sampler values; vertex clamp/fetch/type/memory request values; TVX data format, destination/source selectors, endian swap, fetch instructions, numeric format, surface mode, and data type.
- Texture cache and TCC domains: `TC_OP_MASKS`, `TC_OP` cache/atomic/invalidation operations, credit constants, `TC_NACKS`, and the beginning of `TCC_PERF_SEL`.

## Important APIs, Types, And Constants

The exported interface is entirely compile-time symbols:

- `typedef enum <Name> { ... } <Name>;` gives typed numeric value domains. The large selector enums include `CBPerfSel` with 396 entries, `PerfCounter_Vals` with 257 entries, `SU_PERFCNT_SEL` with 153 entries, `SC_PERFCNT_SEL` with 397 entries, `SPI_PERFCNT_SEL` with 197 entries, and `SQ_PERF_SEL` with 292 entries in this chunk.
- Raw `#define` constants fill gaps where the generator emitted individual numeric constants rather than enums. These include register-space boundaries (`CONFIG_SPACE_*`, `UCONFIG_SPACE_*`, `PERSISTENT_SPACE_*`, `CONTEXT_SPACE_*`), SQ decoder ranges, instruction encoding masks/fields, register names, opcodes, source selectors, and message IDs.
- Small state enums such as `SurfaceNumber`, `SurfaceSwap`, `CBMode`, `CompareFrag`, `StencilOp`, `SQ_TEX_CLAMP`, `SQ_RSRC_IMG_TYPE`, `SQ_WAVE_TYPE`, `TEX_DIM`, and `TVX_DATA_FORMAT` are the likely values packed into specific register fields or descriptors.
- Performance selector enums such as `CBPerfSel`, `CPG_PERFCOUNT_SEL`, `CPF_PERFCOUNT_SEL`, `CPC_PERFCOUNT_SEL`, `PerfCounter_Vals`, `GRBM_PERF_SEL`, `SU_PERFCNT_SEL`, `SC_PERFCNT_SEL`, `SPI_PERFCNT_SEL`, `SQ_PERF_SEL`, and the partial `TCC_PERF_SEL` provide mux values for hardware counters.
- Shader ISA constants are not C-callable APIs, but they are an ABI-like hardware contract for disassembly/debug, packet generation, trap/thread-trace decode, and shader-engine diagnostics.

Representative enum families and their starts in this chunk are:

- Lines 27-120: compact CB/surface/blend/CMASK value domains.
- Lines 125-531: CB perf selectors and CB perf filters.
- Lines 535-679: CP ring/pipe/ME/perf/tag selectors.
- Lines 706-1059: DB/Z/stencil/perf and GB EDC value domains.
- Lines 1066-1822: GRBM, SU, SC, raster-map, and CSDATA domains.
- Lines 1831-2079: SPI value domains and SPI perf selectors.
- Lines 2079-2708: SQ descriptor, thread-trace, performance, command, EDC, export/RAT, and memory-mode enums.
- Lines 2710-4124: SQ ISA-related `#define` constants.
- Lines 4126-4368: texture and vertex fetch enums.
- Lines 4374-4519: TC operation masks, TC operations, credit constants, and NACK values.
- Lines 4520-4749: start of TCC perf selector values.

## Control Flow

This header has no direct runtime control flow. The implied driver flow is:

1. Compile GFX 8.0 AMDGPU code with this enum header and companion register headers.
2. Select a register field or packet/descriptor field from the offset and shift/mask metadata.
3. Choose one of these symbolic values to pack into the field, or decode a hardware readback/performance-counter selector into a symbolic domain.
4. Program MMIO/context state, build command packets, configure performance counters, or decode shader/thread-trace/cache/debug data in the surrounding driver code.

All sequencing, locking, polling, reset ordering, cache invalidation ordering, context-save behavior, and userspace-facing semantics are outside this file. This chunk only supplies literal numeric contracts.

## State And Persistence Behavior

The file itself is stateless. The constants describe values that may become persistent or volatile state after surrounding AMDGPU code writes them to hardware registers, command packets, descriptors, or shader/debug configuration.

CB/DB/SPI/SQ/TC/TCC performance selector values persist in hardware performance-counter mux registers until reprogrammed, while the counters they select are dynamic hardware observations. Selector mistakes can make counters appear valid while measuring the wrong block, event, client, cache state, or pipeline stall.

Surface, blend, Z/stencil, texture, vertex fetch, resource descriptor, shader export, and cache operation values participate in rendering and compute state. Once written into a context register or descriptor, they remain part of the active graphics/compute state until overwritten or context-switched by the driver.

SQ instruction and register constants describe encoded shader instructions, source operands, wait counters, hardware registers, system messages, thread-trace tokens, and trap/debug IDs. These values affect debug decode, trap handling, thread-trace interpretation, and any tool or driver path that reasons about ISA encodings.

Register-space boundary constants (`CONFIG_SPACE_*`, `PERSISTENT_SPACE_*`, `CONTEXT_SPACE_*`, `SQ*DEC_*`) classify MMIO ranges. Incorrect range usage can misclassify context-saved, persistent, user-config, or decoder-owned registers.

The partial `TCC_PERF_SEL` state in this chunk is not complete; any consumer or report must combine it with the following lines before reasoning about the full TCC selector domain.

## Dependencies And Integration Points

This header depends on the generated GFX 8.0 register set staying synchronized:

- Matching GFX 8.0 offset and shift/mask headers define where these enum values are written or read.
- AMDGPU register helper macros and MMIO/PM4 paths pack these values into register fields.
- Graphics initialization, context setup, command submission, debugfs/hang-dump code, shader trap/thread-trace code, RAS/EDC paths, KFD-adjacent compute paths, and performance-monitor code can depend on the values indirectly.
- Userspace graphics and compute stacks depend on these constants through the kernel's programming of CB/DB/SPI/SQ/TC/TCC state, shader ABI expectations, and performance/debug outputs.

Important integration surfaces include CB blending/compression/DCC behavior, DB depth/stencil testing and counters, CP ring/pipe/ME targeting, GRBM/SU/SC/SPI/SQ/TCC performance monitoring, raster configuration, SPI shader export and resource limits, SQ descriptor construction, SQ thread-trace decoding, shader trap/debug handling, texture and vertex fetch descriptors, TC cache invalidation/writeback/atomic operations, and TCC cache/client-event attribution.

## Risks And Edge Cases

- Generated-header drift is the primary risk. Wrong numeric enum values compile cleanly but program incorrect hardware behavior or decode the wrong event.
- The chunk ends mid-`TCC_PERF_SEL`; treating the TCC selector list as complete from this file alone would miss later client and event selectors.
- Large performance-selector enums are dense and index-sensitive. A single off-by-one or duplicated value can silently shift metrics for CB, DB, SC, SPI, SQ, or TCC counters.
- Several constants share generic names such as `SQ_F`, `SQ_LT`, `SQ_EQ`, and are redefined in different opcode/compare contexts. Include order and macro namespace collisions are a maintenance risk because these are preprocessor symbols, not scoped enum members.
- Reserved values are explicitly named in many domains. Their presence does not make them safe to program; callers need hardware documentation for reserved fields.
- Cache/TCC/TC operations include invalidation, writeback, atomic, and NACK values. Misusing these can lead to coherency failures, lost writes, page/protection fault misdiagnosis, or incorrect recovery logic.
- Shader ISA encodings are hardware ABI material. Mistakes can break disassembly, debug traps, thread tracing, wave state decode, or any code that emits or validates instructions.
- Register-space constants separate config, user-config, persistent, and context ranges. Bad classification can corrupt context save/restore or allow state to leak across contexts.
- Texture/vertex format enums directly affect how memory bytes are interpreted. Wrong values can cause rendering corruption without obvious kernel errors.

## Test Signals

Useful validation is mostly build coverage, generated-data checks, and hardware/runtime behavior:

- Kernel build coverage for AMDGPU code paths that include `gfx_8_0_enum.h`.
- Mechanical comparison against AMD's authoritative GFX 8.0 register/ISA database for every enum and `#define` in lines 1-4749.
- Static checks that enum values are unique where the hardware domain expects uniqueness, that intentional aliases/holes are documented, and that the partial `TCC_PERF_SEL` is completed by the next chunk.
- Cross-checks that values in this header are used with matching fields in the GFX 8.0 offset and shift/mask headers.
- Rendering tests covering CB formats, swaps, blending, CMASK/DCC, depth/stencil compares, stencil ops, conservative Z, raster mapping, texture sampling, vertex fetch formats, and shader export formats.
- Compute and shader-debug tests covering SQ resource descriptors, waitcnt fields, trap/thread-trace tokens, shader ISA decode, system messages, hardware-register access, and flat/DS/SMEM/MIMG/MUBUF operation handling.
- Performance-monitor tests that select representative CB, CP, DB, GRBM, SU, SC, SPI, SQ/SQC, TC, and TCC events and verify nonzero/monotonic/plausible counters under targeted workloads.
- Cache and VM tests exercising TC invalidation/writeback operations, atomics, NACK/page/protection fault reporting, and TCC hit/miss/client request attribution.
- Runtime warning signals include GPU hangs after context setup, incorrect color/depth output, texture/vertex corruption, unexpected VM faults or missing faults, broken shader trap/thread-trace decode, impossible performance counters, and metrics attributed to the wrong hardware block.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002711`. It covers lines 1-4749 of `gfx_8_0_enum.h`. The final per-file research should merge this with later chunks, especially to complete `TCC_PERF_SEL` and the remaining GFX 8.0 enum/value domains after line 4749.
