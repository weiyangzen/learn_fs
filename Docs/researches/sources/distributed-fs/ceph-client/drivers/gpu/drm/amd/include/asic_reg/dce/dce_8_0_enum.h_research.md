# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_8_0_enum.h

## Purpose

`dce_8_0_enum.h` is a generated-style AMD DCE 8.0 register enumeration header. It contains no executable driver logic; it provides C `typedef enum` declarations whose numeric constants are hardware register-field encodings for DCE 8.0-era AMD display and GPU register programming.

The file is protected by `DCE_8_0_ENUM_H` and belongs with the companion DCE 8.0 register address and shift/mask headers in the same folder: `dce_8_0_d.h` and `dce_8_0_sh_mask.h`. In this source tree, DCE 8.0 display and power-management code directly includes those address/mask headers, while the enum header provides the symbolic value vocabulary corresponding to AMD's register documentation. The broader repository path is under a Ceph-client source mirror, but this file itself is Linux DRM/AMDGPU hardware metadata and does not implement Ceph filesystem behavior.

## Important APIs, Types, and Constants

The file exports enum types only. It defines no functions, structs, inline helpers, variables, or non-guard macros. The exported groups are:

- Surface and address layout enums: `SurfaceEndian`, `ArrayMode`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, `SampleSplitBytes`, `NumPipes`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `ShaderEngineTileSize`, `NumGPUs`, `MultiGPUTileSize`, `RowSize`, and `NumLowerPipes` encode endian swapping, linear/tiled/PRT/3D array modes, pipe/bank topology, interleave sizes, shader-engine tiling, multi-GPU tiling, and row/lower-pipe fields.
- Debug block enums: `DebugBlockId` maps DCE/GCN debug clients such as UVD, VCE, XDMA, SMU, GRBM, RLC, CP, SCF, PC, VGT, SX, CB, IA, BCI, PA, SPI, SDMA, IH, SRBM, HDP, ACP, memory controllers, VMC, GMCON, GDC, WD, and SDMA instances. `DebugBlockId_OLD` is a larger legacy table that includes TCP, DB, TCC, SPS, TA, TD, and MCD ranges. `DebugBlockId_BY2`, `DebugBlockId_BY4`, `DebugBlockId_BY8`, and `DebugBlockId_BY16` are reduced selector tables for narrower or stride-based debug selector fields.
- Depth, stencil, comparison, compression, and export enums: `CompareRef`, `ReadSize`, `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, and `QuadExportFormatOld` encode compare functions, read granularity, depth/stencil formats, CMASK clear/alpha modes, and pixel export encodings.
- Color, surface, buffer, image, and numeric format enums: `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, and `IMG_NUM_FORMAT` define packed integer, floating-point, normalized/scaled/signed/unsigned, sRGB, block-compressed, FMASK, and reserved format values. `SurfaceFormat` is the broadest surface table and includes BC1 through BC7, APC formats, `CTX1`, and several `FMT_RESERVED_*` values.
- Tile-geometry enums: `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, `BankWidthHeight`, and `MacroTileAspect` describe color/depth tiles, display versus non-display micro-tiling, tile split size, sample split count, pipe layout, bank count, bank dimensions, and macro-tile aspect.
- Cache and performance enums: `TCC_CACHE_POLICIES`, `PERFMON_COUNTER_MODE`, and `PERFMON_SPM_MODE` encode TCC cache policy selection, performance counter accumulation/sample/max/dirty cycle modes, and streaming performance monitor width/clamp/test modes.
- Small display/surface metadata enums: `SurfaceTiling`, `SurfaceArray`, `ColorArray`, and `DepthArray` encode linear versus tiled surfaces and 1D/2D/3D/slice surface forms for color or depth fields.

Many type and enumerator names are intentionally generic, such as `ArrayMode`, `SurfaceFormat`, `DebugBlockId`, `PERFMON_COUNTER_MODE`, `FMT_BC7`, and `ARRAY_2D_TILED_THIN1`. Similar names appear in sibling ASIC headers, including GCA and later DCE generation enum files. These are not namespaced C symbols, so their include boundaries matter.

## Control Flow

There is no runtime control flow. The only control structure is the include guard:

1. `#ifndef DCE_8_0_ENUM_H`
2. `#define DCE_8_0_ENUM_H`
3. enum typedef declarations
4. `#endif /* DCE_8_0_ENUM_H */`

Runtime behavior is supplied by consumers that write AMDGPU registers through MMIO helper paths. Those consumers compose register values using address macros from `dce_8_0_d.h`, field masks and shifts from `dce_8_0_sh_mask.h`, and, where this enum header is included, named constants from `dce_8_0_enum.h`. The header itself performs no validation that a value is used with the correct register field; a wrong enum value can compile cleanly because the hardware contract is encoded only in the numeric literals and companion register documentation.

## State and Persistence Behavior

This header owns no mutable software state. It has no static storage, allocation, locking, I/O, firmware interaction, sysfs/debugfs surface, or persistent files.

The constants are stateful only indirectly. When driver code writes these values into GPU registers, the resulting hardware state can persist until a later register write, block reset, suspend/resume reinitialization, or full GPU reset. Examples include surface layout state, scanout or render format state, debug bus block selection, performance counter mode, cache policy, tiling geometry, and memory-addressing interpretation.

The numeric assignments are therefore ABI-like within the generated ASIC register interface. Renaming a symbol is a source-compatibility change; changing a numeric value is a hardware programming change that can alter displayed pixels, memory swizzling, debug routing, or performance counter behavior.

## Dependencies and Integration Points

The header is syntactically self-contained C and does not include other files. Its practical dependencies are external and contractual:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_8_0_d.h` provides DCE 8.0 register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_8_0_sh_mask.h` provides DCE 8.0 register field masks and shifts.
- DCE 8.0 consumers in this tree include the companion address/mask headers in files such as `amdgpu/dce_v8_0.c`, `amdgpu/cik.c`, `amdgpu/gmc_v7_0.c`, `amdgpu/gfx_v7_0.c`, `display/dc/dce80/dce80_timing_generator.c`, `display/dc/irq/dce80/irq_service_dce80.c`, `display/dc/resource/dce80/dce80_resource.c`, `display/dc/hwss/dce80/dce80_hwseq.c`, GPIO translation/factory code under `display/dc/gpio/dce80/`, and CI power-management code under `pm/powerplay/`.
- `amdgpu/dce_v8_0.c` includes `gca/gfx_7_2_enum.h`, which defines overlapping GCN surface/format enums. This is an integration signal that DCE 8.0 code in this tree may rely on GCA enum definitions for shared surface and format programming rather than including `dce_8_0_enum.h` directly.
- Sibling generated enum headers such as `dce_10_0_enum.h`, `dce_11_0_enum.h`, `dce_11_2_enum.h`, `gfx_7_2_enum.h`, and `gfx_8_0_enum.h` define many same-named types or enumerators for adjacent ASIC generations.

The values in this file are meaningful only when paired with the matching generation's register fields. Cross-generation reuse should be treated as a hardware-interface decision, not a mechanical C refactor.

## Risks and Sharp Edges

- Hardware ABI drift: the values are exact register-field encodings. Off-by-one edits or swapped values can select different tiling modes, pixel formats, debug clients, cache policies, or perf monitor modes without producing a compile-time error.
- Namespace collisions: broad enum names and unscoped enumerators collide with similar generated headers. Including multiple incompatible ASIC enum headers in one translation unit can produce duplicate typedef/enumerator errors or encourage invalid assumptions that same names always mean same hardware values.
- Reserved encodings: many format and selector tables include `RESERVED` entries. A named reserved value is still not necessarily safe to program.
- Format table confusion: `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, and `IMG_DATA_FORMAT` share many similar-looking names but target different hardware fields. Reusing a value across tables can program the wrong interpretation.
- Reduced debug tables: the `_BY2`, `_BY4`, `_BY8`, and `_BY16` debug block enums are not equivalent aliases for `DebugBlockId`; they are stride-reduced mappings. Generic debug code must choose the table matching the field width and selector encoding.
- Generated-header maintenance: formatting, spelling, ordering, and reserved slots likely trace back to AMD register-generation input. Manual cleanup can break generated diffability or source compatibility.
- Direct-include ambiguity: source search in this tree shows many DCE 8.0 users of `_d.h` and `_sh_mask.h`, but no direct C include of `dce_8_0_enum.h` outside metadata/research paths. That lowers active compile coverage for this specific header and raises the chance that stale enum drift would go unnoticed unless generated-header checks include it.

## Test Signals

Useful validation for this file is mostly compile-time, generated-data, and hardware-runtime oriented:

- Compile a minimal translation unit that includes `dce/dce_8_0_enum.h` by itself to verify syntax, include guard closure, and typedef/enumerator validity.
- Compile relevant AMDGPU DCE 8.0 paths with their normal include set, especially `amdgpu/dce_v8_0.c`, DCE80 Display Core timing/IRQ/resource/GPIO/HWSS files, and CI power-management files. This detects integration conflicts if the enum header is added to a consumer that already includes overlapping ASIC enum headers.
- Compare the file against the authoritative AMD DCE 8.0 register-generation source or a known-good upstream header. Numeric literal changes, enum reordering, reserved-slot edits, or renamed legacy symbols should be reviewed as hardware contract changes.
- For tiling and format edits, test framebuffer scanout, cursor surfaces, endian handling, linear versus tiled modes, color/depth formats, block-compressed/image formats where applicable, and suspend/resume reprogramming on matching DCE 8.0 hardware.
- For debug/perf edits, verify debug block routing and performance counter/SPM mode selection choose the expected hardware blocks and counter behaviors.
- For cache and surface addressing edits, exercise memory tiling, pipe/bank configuration, tile split/sample split, and cache policy paths through register readback or hardware validation tests.
- Static checks can flag duplicate names across included ASIC enum headers, unexpected numeric changes against generated baselines, and use of reserved format/select values in driver code.
