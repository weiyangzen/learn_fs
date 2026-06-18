<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_0_enum.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_0_enum.h

## Purpose
`bif_5_0_enum.h` is a generated AMD ASIC enum header associated with the BIF 5.0 register set. Despite its BIF path, it contains broad register-field value enums used across GPU register programming: surface layout, tiling/address configuration, debug block selection, export and pixel formats, buffer/image formats, cache policy, performance monitor modes, and memory power-control values.

The file provides symbolic names for numeric field encodings. It does not implement logic or directly access hardware. Consumers use these values when constructing register fields defined in generated mask headers or when decoding register values read from the GPU.

## Important APIs, Types, and Constants
The public surface is a set of typedef enums under the `BIF_5_0_ENUM_H` include guard. There are no functions, structs, macros, or data objects.

Important enum families include:

- Endian and tiling basics: `SurfaceEndian`, `ArrayMode`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, and `SampleSplitBytes`.
- Address-library style configuration values: `NumPipes`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `ShaderEngineTileSize`, `NumGPUs`, `MultiGPUTileSize`, `RowSize`, `NumLowerPipes`, `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, `BankWidthHeight`, and `MacroTileAspect`.
- Debug mux selectors: `DebugBlockId`, `DebugBlockId_OLD`, and downsampled `DebugBlockId_BY2`, `_BY4`, `_BY8`, and `_BY16`. These map many GPU blocks and replicated instances to packed debug block identifiers.
- Render/depth/color values: `ColorTransform`, `CompareRef`, `ReadSize`, `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, `QuadExportFormatOld`, `ColorFormat`, and `SurfaceFormat`.
- Buffer and image descriptors: `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, and `IMG_NUM_FORMAT`, including unorm/snorm/scaled/int/float/sRGB numeric modes and common compressed/fmask image encodings.
- Cache, request, and performance values: `GATCL1RequestType`, `TCC_CACHE_POLICIES`, `MTYPE`, `PERFMON_COUNTER_MODE`, and `PERFMON_SPM_MODE`.
- Surface array and hardware-size constants: `SurfaceTiling`, `SurfaceArray`, `ColorArray`, `DepthArray`, and `ENUM_NUM_SIMD_PER_CU`.
- Memory power-control enums: `MEM_PWR_FORCE_CTRL`, `MEM_PWR_FORCE_CTRL2`, `MEM_PWR_DIS_CTRL`, `MEM_PWR_SEL_CTRL`, and `MEM_PWR_SEL_CTRL2`.

## Control Flow
There is no executable control flow. The include guard prevents duplicate typedef definitions during compilation.

Runtime behavior appears only where other driver code includes a matching enum header and writes enum values into hardware fields. For example, tiling and surface-format enums feed GPU memory layout and render/depth/color descriptor programming; debug block enums feed debug mux selection; performance monitor enums select accumulation/sample/SPM modes; memory power enums select low-power force, disable, and dynamic policy fields.

## State and Persistence Behavior
The enum header has no local state and no persistence. Its values describe encodings that may be stored in GPU registers, command streams, descriptors, or driver-side register programming structures by consuming code.

When consumed, the resulting hardware state can persist until reprogrammed or reset. Examples include surface tiling descriptors, debug mux selections, performance counter modes, cache memory-type policy, and memory power-control request or policy fields. Because this header supplies values without masks or accessors, it does not validate that an enum value is legal for a particular register field width or ASIC variant.

## Dependencies and Integration Points
The header has no include dependencies beyond the preprocessor. It is paired conceptually with generated address and field headers such as `bif_5_0_d.h` and `bif_5_0_sh_mask.h`, but it can also mirror enum definitions found in other generated block headers.

Search in this tree shows many equivalent enum names in generated GMC, GCA, DCE, OSS, SMU, UVD, and later top-level ASIC enum headers. Direct implementation includes of `bif_5_0_enum.h` are not prominent in this checkout, which suggests the file is primarily generated hardware-specification data available for consumers that need BIF 5.0-era symbolic encodings, while many active call sites use sibling block-specific enum headers or literal field values.

Integration points include address-library tiling calculations, command submission and packet/register construction, debug register selection, performance monitor setup, render/depth/color format programming, buffer/image descriptor encoding, memory-cache policy setup, and low-power memory control fields.

## Risks and Edge Cases
The main risk is enum-value drift from the hardware specification. Incorrect numeric values can create invalid descriptors, misprogram tiling, select the wrong debug block, corrupt format interpretation, break performance counter modes, or request the wrong memory power state.

The enum names are globally broad and repeated across generated headers. Including multiple ASIC enum headers in the same C translation unit can create duplicate typedef or enumerator-name conflicts if guards and include selection are not controlled. This is especially visible for names such as `SurfaceEndian`, `DebugBlockId`, `ColorFormat`, and `SurfaceFormat`.

Some enum values are reserved or legacy compatibility mappings. Callers should not treat every named value as valid for every register generation or feature path. The debug block downsampled enums (`BY2`, `BY4`, `BY8`, `BY16`) intentionally collapse or skip instances and must match the debug mux mode being programmed. Format enums for buffers and images are similar but not interchangeable because their valid ranges and compressed/fmask encodings differ.

The file provides encodings, not field placement. A caller still needs the matching mask/shift constants and must avoid shifting a value into a field that is too small or semantically unrelated.

## Test Signals
Useful validation is mostly compile-time and hardware-facing:

- Build configurations that include this header should catch duplicate enum definitions, syntax errors, and prototype/header conflicts.
- Static checks can verify that enum values written into fields fit the field masks from the corresponding generated `*_sh_mask.h` headers.
- Tiling/address tests should validate linear, 1D/2D/3D tiled, PRT, pipe/bank, tile split, sample split, and macro-tile configurations on matching ASICs.
- Render and memory tests should exercise color/depth/stencil/surface, buffer, and image format descriptors, including compressed and fmask formats where supported.
- Debug and diagnostics should confirm that debug block selectors map to the intended block instance and that downsampled selector modes behave consistently.
- Performance monitor tests should validate counter accumulation, active-cycle, max, sample, and SPM modes.
- Power-management validation should cover memory light sleep, deep sleep, shutdown force requests, dynamic policy selection, and disable controls where corresponding registers exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_0_enum.h -->
