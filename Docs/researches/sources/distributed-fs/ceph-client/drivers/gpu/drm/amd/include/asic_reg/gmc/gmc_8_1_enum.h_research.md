# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_8_1_enum.h

## Purpose
`gmc_8_1_enum.h` is the generated-style value-domain catalog for GMC 8.1 and closely related graphics/memory register fields. It gives symbolic names to encoded integer values used in register fields and packet/state programming, including surface tiling, address configuration, debug block IDs, render target formats, image and buffer formats, cache modes, performance monitor modes, and memory power-control requests.

Unlike `gmc_8_1_d.h`, this file does not name register addresses. Its role is to make field payloads readable and stable so code can select values such as a tiling mode, pipe layout, debug block, or color format without hard-coding unexplained numeric encodings.

## Important APIs, Types, And Functions
The header exports 64 `typedef enum` types behind the `GMC_8_1_ENUM_H` include guard. It declares no functions, structs, global objects, or executable code.

Important enum groups include:

- Surface and tiling basics: `SurfaceEndian`, `ArrayMode`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, `SampleSplitBytes`, `SurfaceTiling`, `SurfaceArray`, `ColorArray`, and `DepthArray`.
- Addressing and macro-tiling layout: `NumPipes`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `ShaderEngineTileSize`, `NumGPUs`, `MultiGPUTileSize`, `RowSize`, `NumLowerPipes`, `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, `BankWidthHeight`, and `MacroTileAspect`.
- Debug block selectors: `DebugBlockId`, legacy `DebugBlockId_OLD`, and compressed/stride variants `DebugBlockId_BY2`, `DebugBlockId_BY4`, `DebugBlockId_BY8`, and `DebugBlockId_BY16`.
- Render, depth/stencil, and export values: `ColorTransform`, `CompareRef`, `ReadSize`, `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, `QuadExportFormatOld`, `ColorFormat`, and `SurfaceFormat`.
- Buffer and image resource formats: `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, and `IMG_NUM_FORMAT`.
- Cache, translation, and performance monitoring: `GATCL1RequestType`, `TCC_CACHE_POLICIES`, `MTYPE`, `PERFMON_COUNTER_MODE`, and `PERFMON_SPM_MODE`.
- Device-configuration and power values: `ENUM_NUM_SIMD_PER_CU`, `MEM_PWR_FORCE_CTRL`, `MEM_PWR_FORCE_CTRL2`, `MEM_PWR_DIS_CTRL`, `MEM_PWR_SEL_CTRL`, and `MEM_PWR_SEL_CTRL2`.

Representative values include `ARRAY_2D_TILED_THIN1` for tiling, `ADDR_SURF_P8_32x64_32x32` for pipe configuration, `FMT_BC7` and `IMG_DATA_FORMAT_BC7` for compressed formats, `PERFMON_COUNTER_MODE_ACCUM` for counters, `MTYPE_CC` for cacheable coherent memory type, and `FORCE_DEEP_SLEEP_REQUEST` for memory power control.

## Control Flow
The header has no runtime control flow. It affects control flow only when compiled code compares, switches on, or writes these enum values into hardware fields or command/state packets.

The debug-block enums are likely to feed diagnostic selection logic where a caller chooses a block ID and writes it to a debug selector register. The tiling and format enums feed address-library or register-field programming paths where the encoded value controls how memory is interpreted by the GPU. The power and performance enums feed low-power or counter-setup decisions where a selected symbolic state becomes a small integer written to a control field.

No direct include of `gmc_8_1_enum.h` was found in the checked AMDGPU source subtree during this research. That makes it a generated companion contract rather than an obviously active local implementation dependency, but the names and encodings still match the same ASIC generation's register-field vocabulary.

## State And Persistence Behavior
The header itself has no mutable state. The encoded values can become persistent hardware state when callers write them into registers, command buffers, context state, debug selectors, or power-management controls. Once programmed, those field values persist according to the owning register or command processor state until reset, context reprogramming, power transition, or explicit overwrite.

Some enum domains describe software-visible resource metadata rather than standalone hardware state. For example, tiling and image/buffer format values determine how surfaces, buffers, FMASK data, depth/stencil data, and compressed formats are interpreted. A mismatch between metadata and actual memory layout can persist as corrupted rendering or invalid memory interpretation even if the enum header itself is correct.

## Dependencies
This file has minimal syntactic dependencies, but semantic dependencies are strong:

- Register bitfields and packet definitions must allocate enough bits for the enum values used from this file.
- Address computation and surface layout code must agree with `ArrayMode`, `PipeConfig`, bank, row, tile split, and sample split encodings.
- Render, display, compute, and texture code must map DRM/KMS, Mesa, firmware, or kernel format concepts onto the correct `ColorFormat`, `SurfaceFormat`, `BUF_*`, and `IMG_*` values.
- Debug and performance tooling must choose the correct debug block ID family. The `DebugBlockId_OLD` and `*_BY2/BY4/BY8/BY16` variants are not interchangeable with the primary `DebugBlockId` list.
- Power-management code must pair `MEM_PWR_*` values with the correct GMC 8.1 memory-power registers and masks.

## Integration Points
The enum names mirror the field vocabulary used by the AMDGPU register headers in `include/asic_reg/gmc/` and by broader generation-specific AMD register catalogs. They integrate conceptually with GMC 8.1 address and mask headers: `gmc_8_1_d.h` names the register, `gmc_8_1_sh_mask.h` names the bit position, and this file names valid field payloads.

The address-format enums integrate with surface allocation and GPUVM setup because memory layout depends on pipe count, bank count, interleave size, tile split, macro-tile aspect, and array mode. The render/format enums integrate with color/depth/stencil state, buffer/image resource descriptors, and compression metadata. Debug block IDs integrate with register debug selectors and performance/debug dumps. Memory-power enums integrate with memory-controller power state transitions in SMU or BACO-style code.

Within the checked tree, direct users were not found by include-name search, so active local usage may be indirect, generated out, stale compatibility coverage, or available for out-of-tree/user-facing generated code. That absence is itself an integration signal: changes to this header should be treated as ABI-like register contract changes rather than refactors driven by local call-site compiler errors.

## Risks
The primary risk is numeric encoding drift. These enum values are hardware ABI, not arbitrary software choices. Renaming is usually harmless to generated users, but changing a numeric value can make a valid build program the wrong tiling, format, debug block, cache policy, performance mode, or power state.

Several domains contain reserved values and closely related names. `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, and `IMG_DATA_FORMAT` overlap conceptually but are not identical; using a color-buffer format where an image descriptor format is required can silently produce wrong resource interpretation. Similarly, `DebugBlockId`, `DebugBlockId_OLD`, and stride-compressed debug ID variants encode different selector spaces.

The enums are plain C enum typedefs with no strong type enforcement at register-write boundaries. Callers can cast or pass any integer to field helpers, and the compiler generally cannot prove that a value belongs to the field being programmed.

Portability risk also exists because enum names such as `SurfaceEndian`, `ArrayMode`, or `PipeConfig` can appear in other generation headers. Including multiple generated enum catalogs in one translation unit may create type-name collisions unless the surrounding code keeps generation-specific includes isolated.

## Test Signals
Build-time signals are successful compilation of any translation unit that includes this header, absence of typedef-name collisions with other ASIC generation enum headers, and successful static checks that field masks can represent the maximum enum values selected by code.

Runtime signals depend on the consuming field. For tiling/address enums, useful signals are correct surface allocation, scanout, rendering, texture sampling, and VM access across linear, 1D, 2D, 3D, PRT, and thick/thin tile modes. For format enums, signals include correct color/depth/stencil rendering, buffer/image load-store behavior, FMASK/MSAA behavior, and compressed BC/APC/CTX formats. For debug and perf enums, signals are meaningful block selection and counter readings. For memory-power enums, signals are stable low-power transitions, resume, BACO, and memory-controller wake without training or VM faults.
