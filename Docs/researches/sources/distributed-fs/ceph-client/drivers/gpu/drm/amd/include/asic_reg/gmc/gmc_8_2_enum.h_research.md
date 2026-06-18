# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_8_2_enum.h

## Purpose

`gmc_8_2_enum.h` is a generated-style enumeration catalog for GMC 8.2 and closely related AMD GPU hardware blocks. It translates packed register field values into C enum names for debug-block IDs, surface/texture/buffer formats, tiling layouts, address configuration, memory/cache policies, performance-monitor modes, and memory power-control requests. Unlike `gmc_8_2_d.h`, it does not map register addresses; it maps valid field values that are written into or decoded from hardware registers.

The file is effectively a hardware ABI document in C syntax. The values are significant because they match bitfield encodings expected by GPU command processors, memory-controller registers, tiling/address libraries, debug infrastructure, and performance-monitor setup.

## Important APIs, Types, And Constants

This header defines typedef enums only; it declares no functions and owns no storage.

Major enum families:

- `DebugBlockId`, `DebugBlockId_BY2`, `DebugBlockId_BY4`, `DebugBlockId_BY8`, and `DebugBlockId_BY16` enumerate debug-block routing IDs at different grouping granularities. Values cover major GPU blocks such as VMC, PDMA, CG, SRBM, GRBM, RLC, IH, SQ, SDMA, GDS, CP, VGT, TCC, TCP, CB, DB, TA, TD, LDS, and many per-instance or reserved IDs.
- Surface layout and address configuration enums include `ArrayMode`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, `SampleSplitBytes`, `NumPipes`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `ShaderEngineTileSize`, `NumGPUs`, `MultiGPUTileSize`, `RowSize`, `NumLowerPipes`, `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, `BankWidthHeight`, and `MacroTileAspect`.
- Render, depth, color, and export format enums include `ColorTransform`, `CompareRef`, `ReadSize`, `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, `QuadExportFormatOld`, `ColorFormat`, and `SurfaceFormat`.
- Buffer and image view enums include `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, and `IMG_NUM_FORMAT`.
- Memory/cache/performance enums include `GATCL1RequestType`, `TCC_CACHE_POLICIES`, `MTYPE`, `PERFMON_COUNTER_MODE`, `PERFMON_SPM_MODE`, `SurfaceTiling`, `SurfaceArray`, `ColorArray`, `DepthArray`, and `ENUM_NUM_SIMD_PER_CU`.
- Memory power-control enums include `MEM_PWR_FORCE_CTRL`, `MEM_PWR_FORCE_CTRL2`, `MEM_PWR_DIS_CTRL`, `MEM_PWR_SEL_CTRL`, and `MEM_PWR_SEL_CTRL2`.

The enum names are the public interface. Their numeric assignments must remain aligned with the hardware register specification and with sibling generated headers for related blocks.

## Control Flow

There is no executable control flow. The enums affect runtime behavior only when a consumer writes or decodes a register/packet field with one of these values. Typical downstream flows are:

- A consumer selects an enum value for a tiling, format, cache policy, or performance counter mode.
- Field packing macros from matching `*_sh_mask.h` headers shift the value into the correct register bitfield.
- Register access or command-stream emission writes the packed value to hardware.
- Hardware interprets the numeric value according to the ASIC register definition.

The header itself does not validate combinations. For example, it does not enforce that a `SurfaceFormat` is compatible with a particular `ArrayMode`, `TileSplit`, or render target path.

## State And Persistence Behavior

The enum declarations have no mutable state and no persistence. State appears only when enum values are embedded in hardware registers, command packets, or driver-side cached mode structures. Once written, those hardware fields can persist until replaced, reset, or power-state restored.

Sensitive state represented by these values includes:

- Surface layout and swizzle choices that determine how memory addresses map to pipes, banks, rows, and tiles.
- Pixel, depth/stencil, buffer, image, and export formats used by render, texture, scanout, and compression paths.
- Debug block selection and performance-monitor capture modes.
- Memory cacheability/type and memory power-state force/disable/select controls.

## Dependencies

The file is syntactically standalone. Practical dependencies are:

- Consumers must pair these enum values with the correct register definitions and shift/mask macros from the same ASIC generation.
- Tiling and surface format use must agree with address-calculation code, userspace ABI expectations, and command-stream packet formats for the targeted ASIC.
- Debug and performance-monitor consumers must use the correct debug-block grouping enum (`BY2`, `BY4`, `BY8`, `BY16`) for the register field width and multiplexing mode being programmed.

No direct include of `gmc_8_2_enum.h` was found in the focused AMDGPU consumer search for this work item, but the same enum names and values are duplicated across nearby generated ASIC headers (`gmc_8_1_enum.h`, GCA, DCE, SMU, UVD, and later SOC enum headers). That pattern indicates this file is part of the generated hardware-description surface, even when not directly pulled into a current compilation unit in this tree.

## Integration Points

Likely integration points are code that programs or decodes:

- GFX8 tile mode and macro-tile registers, which use `ArrayMode`, `PipeConfig`, `TileSplit`, `SampleSplit`, bank width/height, and macro aspect encodings.
- Render target, depth/stencil, image, and buffer descriptors that use `SurfaceFormat`, `ColorFormat`, `DepthFormat`, `ZFormat`, `StencilFormat`, `BUF_*`, and `IMG_*` values.
- Debug/performance infrastructure that selects `DebugBlockId*`, `PERFMON_COUNTER_MODE`, and `PERFMON_SPM_MODE`.
- Memory-controller and cache-policy setup that uses `GATCL1RequestType`, `TCC_CACHE_POLICIES`, and `MTYPE`.
- Memory power management that uses the `MEM_PWR_*` request, disable, and select enums.

The presence of equivalent enum blocks in neighboring generated headers means consumers may include a block-specific enum header rather than this GMC copy. That reduces direct include pressure but increases the risk of duplicate type names if multiple enum headers defining the same typedefs are included in one C translation unit.

## Risks

- Numeric enum values are hardware encodings. Changing names, removing reserved values, or renumbering entries can silently misprogram registers while still compiling.
- Many typedef names are generic (`ArrayMode`, `SurfaceFormat`, `PipeConfig`, `ColorFormat`, `MTYPE`). Including multiple generated enum headers in the same translation unit can create type redefinition conflicts if include boundaries are not controlled.
- Reserved and unused debug IDs are explicitly represented. Consumers must not treat every enum value as a valid programmable target on all ASIC variants.
- Format and tiling enums describe values, not valid combinations. Invalid pairings can produce rendering corruption, VM faults, cache incompatibilities, or hangs.
- The debug-block grouping variants (`BY2`, `BY4`, `BY8`, `BY16`) look similar but encode different compressed ID spaces; using the wrong one can route debug/perf collection to the wrong block.

## Test Signals

Useful validation signals include:

- Compile coverage for any translation unit that includes this file, especially alongside other generated ASIC enum headers, to catch typedef name collisions.
- Register/command-packet tests that verify packed enum values match expected bit patterns for tiling, formats, perfmon modes, memory type, and power-control fields.
- Rendering and compute tests that exercise representative surface formats, buffer/image formats, tiled and linear array modes, and depth/stencil modes.
- Address-library or tiling conformance checks comparing expected pipe/bank/tile layout against hardware behavior.
- Debug/perfmon smoke tests that select known blocks and confirm counters or traces are sourced from the intended hardware block.
- Power-management tests that cover light sleep, deep sleep, shutdown force requests, and dynamic memory power-control selection on matching GMC 8.2 hardware.
