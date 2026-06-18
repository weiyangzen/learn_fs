# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_3_0_enum.h

## Purpose

`oss_3_0_enum.h` is a generated-style AMD GPU register documentation header for the OSS 3.0 hardware block. It contains only `typedef enum` definitions and a conventional include guard, with no functions, macros, global objects, or executable code. Its role is to give C code symbolic names for fixed numeric encodings used by OSS 3.0-era AMD ASIC register fields, interrupt source identifiers, performance monitor selectors, surface and buffer formats, tiling modes, debug block IDs, cache policies, and memory power-control values.

The file is ABI- and hardware-contract oriented: the enum values are not arbitrary software identifiers. They represent bitfield payloads and selector values that firmware, hardware blocks, debug infrastructure, and kernel register programming must agree on exactly.

## Important APIs, Types, and Constants

This header exports a large set of plain C enum typedefs:

- `IH_CLIENT_ID`: interrupt-handler client source ID ranges for blocks such as DC, VGA, CAP, VIP, ROM, BIF, SRBM, UVD, VMC, RLC, PDMA, and CG.
- `IH_PERF_SEL`: interrupt-handler performance-counter selectors, including cycle/idle events, client stall signals, ring-buffer fullness/overflow/wrap/writeback signals, memory-controller write activity, BIF edge signals, and SR-IOV virtual-function-specific ring-buffer events for VF0 through VF15.
- `SRBM_PERFCOUNT1_SEL`, `SYS_GRBM_GFX_INDEX_SEL`, and `SRBM_GFX_CNTL_SEL`: system register bus and graphics-index selection values for routing or observing blocks such as BIF, SDMA instances, IH, VMC, UVD, VCE, ACP, SMU, SAM, ISP, and test targets.
- `SDMA_PERF_SEL`: SDMA performance selector values covering ring-buffer state, indirect-buffer state, execution idle, SRBM register sends, memory-controller reads/writes, semaphore and interrupt handshakes, packet counts, copy-engine activity, context changes, doorbells, and read/write byte-address router activity.
- Surface layout and address configuration enums: `SurfaceEndian`, `ArrayMode`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, `SampleSplitBytes`, `NumPipes`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `ShaderEngineTileSize`, `NumGPUs`, `MultiGPUTileSize`, `RowSize`, `NumLowerPipes`, `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, `BankWidthHeight`, and `MacroTileAspect`.
- Debug block enums: `DebugBlockId` is the OSS 3.0 debug-client map, while `DebugBlockId_OLD`, `DebugBlockId_BY2`, `DebugBlockId_BY4`, `DebugBlockId_BY8`, and `DebugBlockId_BY16` preserve alternate or compressed debug block ID layouts. These cover graphics, memory, display, UVD/VCE, SDMA, shader, texture/cache, color/depth buffer, and reserved slots.
- Render and image format enums: `ColorTransform`, `CompareRef`, `ReadSize`, `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, `QuadExportFormatOld`, `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, and `IMG_NUM_FORMAT`.
- Cache, memory, and performance monitor control enums: `GATCL1RequestType`, `TCC_CACHE_POLICIES`, `MTYPE`, `PERFMON_COUNTER_MODE`, `PERFMON_SPM_MODE`, `SurfaceTiling`, `SurfaceArray`, `ColorArray`, `DepthArray`, `ENUM_NUM_SIMD_PER_CU`, `MEM_PWR_FORCE_CTRL`, `MEM_PWR_FORCE_CTRL2`, `MEM_PWR_DIS_CTRL`, `MEM_PWR_SEL_CTRL`, and `MEM_PWR_SEL_CTRL2`.

The enum values are mostly small hexadecimal constants intended to be written into register fields. Several enums deliberately contain gaps, `RESERVED_*` entries, or generation-specific spellings. For example, `SDMA_PERF_SEL` skips from `MC_RD_NO_POLL_IDLE` at `0x15` to semaphore selectors beginning at `0x18`, and the debug ID families explicitly encode reserved positions to preserve hardware numbering.

## Control Flow

There is no runtime control flow. Including this header only makes typedef names and enum constants visible to a translation unit. Any behavior emerges in downstream code that uses these constants to compose register values, decode hardware status, program performance counters, select debug blocks, or describe surface metadata.

The only compile-time flow is the include guard:

- `OSS_3_0_ENUM_H` prevents duplicate type and enumerator definitions when the file is included more than once.
- The guard does not include other headers and does not depend on conditional feature macros.

## State and Persistence Behavior

This file owns no runtime state and performs no persistence. Its values may influence persistent or semi-persistent GPU state when used elsewhere:

- Register programming can latch enum values into GPU registers until reset or reprogramming.
- Surface and tiling values may describe buffer layouts shared with firmware, command streams, memory managers, or userspace-visible GPU objects.
- Performance monitor selectors can determine what counters accumulate while profiling is active.
- Debug block IDs can affect which hardware block is addressed by debug or trace registers.
- Memory power-control values can request or disable dynamic memory power behavior when written by a power-management path.

Because the source is a header of constants, persistence concerns are indirect: a wrong constant can persist in hardware state or buffer metadata after being written by consumers.

## Dependencies

The header has no source-level dependencies beyond the C compiler's support for enum typedefs. It does not include Linux kernel headers, AMD helper headers, or standard library headers.

Its semantic dependencies are external:

- OSS 3.0 AMD ASIC register documentation defines the numeric meaning of each enumerator.
- Register address and field-mask headers in the same `asic_reg/oss` family are expected to provide the bit positions and register offsets that pair with these enum payloads.
- Kernel DRM/AMDGPU code, firmware interfaces, command submission paths, debug tooling, or performance-monitor code must use the constants only for compatible hardware generations.

A repository scan found no direct include of this exact `oss_3_0_enum.h` under the local AMD/Radeon driver tree, but same-named enum families appear in newer AMD headers such as `soc24_enum.h`. That indicates this file is part of the generation-specific register-description corpus and may be retained for compatibility, generated coverage, or hardware support not currently wired by direct textual include in this source snapshot.

## Integration Points

Likely integration points are hardware-register programming sites that need stable symbolic encodings:

- Interrupt handling and diagnostics can use `IH_CLIENT_ID` and `IH_PERF_SEL` values to map source IDs and select interrupt-handler performance events.
- SDMA setup, diagnostics, or profiling code can use `SDMA_PERF_SEL` values for SDMA performance counters.
- SRBM/GRBM routing code can use `SRBM_PERFCOUNT1_SEL`, `SYS_GRBM_GFX_INDEX_SEL`, and `SRBM_GFX_CNTL_SEL` to select a hardware block or observe bus activity.
- Surface creation, command stream construction, memory management, and display/render paths can use the tiling, array, endian, format, and numeric-format enums to encode resource descriptors.
- Debug or trace code can use the `DebugBlockId*` families to select hardware debug clients at different aggregation granularities.
- Performance monitoring can combine `PERFMON_COUNTER_MODE`, `PERFMON_SPM_MODE`, cache policy, request type, and memory type values with block-specific register fields.
- Power-management code can use the `MEM_PWR_*` enums to express force, disable, and dynamic-selection requests for memory power states.

The file sits under `drivers/gpu/drm/amd/include/asic_reg/oss`, so consumers are expected to be AMD GPU kernel code or generated register headers rather than generic Ceph/distributed filesystem logic. The `sources/distributed-fs/ceph-client` prefix is repository layout context; this particular file is imported Linux DRM AMD GPU driver material.

## Risks and Edge Cases

- Numeric drift is the primary risk. Changing an enum value, inserting a new value without explicit assignment, or renaming a value used by generated register code can silently program the wrong hardware field.
- Generation mismatch is dangerous. These constants are for OSS 3.0; using them with another ASIC generation that has shifted encodings can break interrupts, profiling, surface layout, debug routing, or power behavior.
- Reserved values must remain reserved unless hardware documentation says otherwise. Some enums intentionally expose reserved slots to keep later values aligned with hardware numbering.
- The misspelled `RESEVERED0` enumerator in `SYS_GRBM_GFX_INDEX_SEL` is part of the exported spelling. Fixing it could break source compatibility for consumers that already refer to that name.
- The debug block maps are dense and easy to confuse. `DebugBlockId`, `DebugBlockId_OLD`, and the `BY2/BY4/BY8/BY16` variants are not interchangeable even when names look related.
- Some enum names are very generic, such as `ArrayMode`, `ColorFormat`, `SurfaceFormat`, and `MTYPE`. Including this header in broad scopes can collide with other generated AMD enum headers that define same typedef or enumerator names.
- There are no compile-time range checks. Downstream code must ensure values fit the target field width and that descriptor fields use the right enum family.

## Test Signals

Useful validation signals for changes involving this header are mostly build-time and hardware-facing:

- Full kernel or AMDGPU subtree compilation catches duplicate typedefs, renamed enumerators, and syntax errors.
- Static scans can verify every enumerator has an explicit numeric assignment, preserving generated hardware values across formatting or regeneration.
- Register-header generation diffs should show only expected OSS 3.0 documentation changes; unexpected value churn is a red flag.
- Unit or selftest coverage in consumers should verify descriptor packing for surface formats, tiling modes, image/buffer numeric formats, and memory type fields.
- Hardware bring-up or emulator tests should exercise interrupt delivery, SDMA performance counter selection, SRBM/GRBM block routing, debug block selection, and power-management register programming on OSS 3.0-compatible ASICs.
- For profiling paths, compare selected events against known idle/busy workloads: `*_IDLE`, ring-buffer full/overflow, writeback, and SDMA packet selectors should move predictably.
- For resource descriptors, render/copy/display tests using linear, 1D/2D/3D tiled, depth, color, compressed, and FMASK formats are good end-to-end signals that format and tiling encodings still match hardware expectations.
