# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_enum.h

## Purpose

`bif_5_1_enum.h` is a generated AMD GPU register documentation header for the BIF 5.1 hardware generation. It does not implement executable behavior. Its role is to publish C enum names for numeric values that can be written into, or decoded from, hardware register fields described by the BIF 5.1 register-address and shift/mask headers.

The file is guarded by `BIF_5_1_ENUM_H` and contains only `typedef enum` declarations. The values cover several hardware vocabularies used by AMDGPU-family blocks: debug block identifiers, address/surface tiling modes, render and texture formats, buffer/image data and number formats, cache and memory type policy fields, performance monitor modes, surface array modes, and memory power-control selections.

## Important APIs, Types, and Constants

This header exports no functions, structs, macros, or storage. Its public interface is the enum type namespace:

- `DebugBlockId` maps detailed debug/performance block IDs from `DBG_BLOCK_ID_RESERVED = 0x0` through `DBG_BLOCK_ID_UNUSED46 = 0xfe`. It includes graphics, memory, DMA, interrupt, command processor, shader, texture, color/depth backend, cache, local data store, and many reserved or unused ID slots.
- `DebugBlockId_BY2`, `DebugBlockId_BY4`, `DebugBlockId_BY8`, and `DebugBlockId_BY16` provide coarser debug block ID tables for grouped selection granularities. Their enumerators keep the same domain naming with suffixes such as `_BY2`, `_BY4`, `_BY8`, and `_BY16`.
- `SurfaceEndian`, `ArrayMode`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, `SampleSplitBytes`, `NumPipes`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `ShaderEngineTileSize`, `NumGPUs`, `MultiGPUTileSize`, `RowSize`, and `NumLowerPipes` describe memory layout and address-configuration field values.
- `ColorTransform`, `CompareRef`, `ReadSize`, `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, `QuadExportFormatOld`, `ColorFormat`, and `SurfaceFormat` describe graphics pipeline and render-target/depth/stencil format fields.
- `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, and `IMG_NUM_FORMAT` define buffer and image resource descriptor encodings. `IMG_DATA_FORMAT` includes standard scalar/vector, packed, depth/stencil, block-compressed, FMASK, and reinterpretation-style values through `IMG_DATA_FORMAT_32_AS_32_32_32_32 = 0x3f`.
- `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, `BankWidthHeight`, and `MacroTileAspect` describe surface tiling metadata used by address-library style calculations and register programming.
- `GATCL1RequestType`, `TCC_CACHE_POLICIES`, and `MTYPE` describe translation/cache request behavior, texture cache policy, and memory type encodings.
- `PERFMON_COUNTER_MODE` and `PERFMON_SPM_MODE` define performance monitor counter accumulation/sample modes and streaming performance monitor packing/clamping/test modes.
- `SurfaceTiling`, `SurfaceArray`, `ColorArray`, `DepthArray`, and `ENUM_NUM_SIMD_PER_CU` provide compact surface shape and hardware topology values.
- `MEM_PWR_FORCE_CTRL`, `MEM_PWR_FORCE_CTRL2`, `MEM_PWR_DIS_CTRL`, `MEM_PWR_SEL_CTRL`, and `MEM_PWR_SEL_CTRL2` define memory power-control request, disable, and dynamic-mode selections.

The numeric values are hardware ABI data. Callers should treat each enum value as a register-field encoding, not as an ordinary software-owned enum that can be reordered or freely extended.

## Control Flow

There is no runtime control flow in this file. The only control structure is the preprocessor include guard:

1. If `BIF_5_1_ENUM_H` is already defined, the compiler skips the header.
2. Otherwise the guard is defined and the enum declarations become visible to the including translation unit.
3. The file ends with `#endif /* BIF_5_1_ENUM_H */`.

Runtime behavior happens in consumers that combine these values with BIF or graphics register field masks and shifts. A typical caller chooses an enum value, shifts it into a field defined by a companion `*_sh_mask.h` header, and writes the resulting DWORD through the AMDGPU register-access layer. Decode paths may read a register field and compare it with these symbolic values for debug output, validation, or table selection.

## State and Persistence Behavior

The header is stateless. It creates compile-time type and enumerator names only.

The state represented by the values lives in GPU hardware registers and resource descriptors. Examples include debug block selector fields, tiling/address configuration registers, texture or buffer descriptor format fields, color/depth export controls, performance monitor counters, cache policy controls, and memory power-management registers. Those hardware fields persist according to the target block's reset and power domains, not according to this header. Reset, suspend/resume, BACO or other low-power transitions, firmware initialization, and driver register writes can all change the actual hardware state.

The enum declarations provide no locking, range validation, register ordering, timeout handling, or persistence guarantees. Those properties must be supplied by the driver code that programs the registers.

## Dependencies

This file has no include dependencies beyond the C preprocessor and compiler support for C enums. Its practical dependencies are hardware-contract and naming dependencies:

- `bif_5_1_d.h` supplies BIF 5.1 register addresses that may contain fields using some of these encodings.
- `bif_5_1_sh_mask.h` supplies BIF 5.1 field masks and shifts; consumers need masks/shifts to place an enum value into the correct bit range.
- Other AMDGPU generated enum headers, such as broad-generation headers under `drivers/gpu/drm/amd/include`, define many of the same global enum type names for other ASIC generations. This means include selection and build configuration matter because the enum names are not namespaced by C.
- AMDGPU register-access helpers and table-driven initialization code are the eventual consumers when these symbolic values are turned into MMIO, indirect, descriptor, or command-table data.
- Hardware documentation/generation scripts are an implicit dependency. Manual changes should preserve the numeric encodings exactly unless the hardware specification changes.

## Integration Points

The local AMD tree includes sibling BIF 5.1 address and shift/mask headers from files such as `amdgpu/uvd_v6_0.c`, `amdgpu/iceland_ih.c`, `amdgpu/tonga_ih.c`, and `amdgpu/cz_ih.c`. Those direct sites use `bif_5_1_d.h` and `bif_5_1_sh_mask.h`; this enum header provides the symbolic field-value layer that can be paired with those headers when generated register definitions are consumed.

Important integration patterns are:

- Debug/perf tooling can use `DebugBlockId` and the grouped `DebugBlockId_BY*` enums to select GPU blocks for debug bus, performance, or trace-related register fields.
- Surface setup, address calculations, and resource descriptor programming use the tiling, array, pipe, bank, tile split, and format enums to match hardware layouts.
- Graphics pipeline state programming uses format, compare, color transform, CMASK, export, depth, stencil, buffer, and image encoding enums to produce field values expected by the GPU.
- Performance monitoring setup uses `PERFMON_COUNTER_MODE` and `PERFMON_SPM_MODE` when programming counter or streaming performance monitor controls.
- Cache/memory management and power code may use `GATCL1RequestType`, `TCC_CACHE_POLICIES`, `MTYPE`, and memory power-control enums when building register values.

Because these enums are globally named, they integrate best when included through a generation-specific path chosen by the ASIC support code. Mixing multiple generated enum headers with overlapping type names in one translation unit can produce duplicate type-definition errors.

## Risks and Edge Cases

- Numeric drift is high impact. Changing an enum value can silently program a different hardware mode, corrupt a resource descriptor, select the wrong debug block, break surface addressing, or destabilize power/performance controls.
- The enum type names are not C-namespaced. Several later global ASIC enum headers define similar or identical names such as `PERFMON_COUNTER_MODE`, `SurfaceEndian`, `ArrayMode`, `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, and `MEM_PWR_FORCE_CTRL`; including incompatible generated headers together can cause compile failures or force consumers into fragile include ordering.
- C enums do not enforce register field width. A value can still be shifted into a field that is too small or semantically unrelated if caller code uses the wrong mask/shift pair.
- Many values represent reserved, unused, or generation-specific encodings. Treating reserved entries as valid modes can expose undefined hardware behavior.
- Similar-looking domains are not interchangeable. For example, `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, and `IMG_DATA_FORMAT` share some conceptual format names but target different register or descriptor fields.
- Grouped debug block enums are not simple type aliases for `DebugBlockId`; they are separate compressed tables. Code must not convert between `DebugBlockId` and `DebugBlockId_BY2`/`BY4`/`BY8`/`BY16` by arithmetic unless the hardware documentation explicitly permits it.
- Generated headers are easy to audit incorrectly because they contain long flat tables. Duplicate-looking names and reserved slots may be intentional hardware ABI placeholders.

## Test Signals

Useful validation signals for changes involving this header are mostly compile-time and hardware-integration oriented:

- Build AMDGPU configurations that include BIF 5.1-era ASIC support to catch missing, renamed, or duplicate enum definitions.
- Build translation units that include adjacent generated headers to catch global enum-name collisions after include changes.
- Static checks should compare enum names and values against the authoritative generated source or hardware XML/spec input, especially for large tables such as `DebugBlockId`, `SurfaceFormat`, and `IMG_DATA_FORMAT`.
- Register programming tests on matching hardware should cover driver probe, interrupt handling, UVD/GFX initialization, resource descriptor setup, display or render-target allocation, suspend/resume, reset, and low-power transitions.
- Performance-monitor smoke tests should verify that selected `PERFMON_COUNTER_MODE` and `PERFMON_SPM_MODE` values produce expected counter behavior and do not wedge the monitored block.
- Format and tiling validation can come from rendering, compute buffer/image access, block-compressed texture sampling, depth/stencil operations, and multisample/FMmask paths.
- Failure signals include GPU hangs after register programming, invalid tiling or format interpretation, corrupted render/depth output, broken debug/performance counter selection, memory power-state transition failures, and compiler errors from conflicting generated enum definitions.
