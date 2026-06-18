# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_2_4_enum.h

## Purpose
`oss_2_4_enum.h` defines named numeric values for OSS 2.4 register fields and related GPU programming domains. It turns raw field encodings into C enum constants for interrupt client ranges, perf monitor selectors, SRBM/GRBM target selectors, SDMA performance events, tiling/addressing modes, debug block IDs, color/depth/surface formats, cache policies, memory types, and perf counter modes.

Although stored under the OSS register directory, the enum catalog is broader than OSS-only control registers. It includes shared register-field encodings used by graphics, memory layout, HDP addressing, and debug/performance plumbing on the same ASIC generation.

## Important APIs, Types, and Functions
- There are no functions or structs. The API is a set of `typedef enum` types with stable integer values matching hardware field encodings.
- Interrupt/perf enums: `IH_CLIENT_ID` maps client source ID ranges for DC, VGA, CAP, VIP, ROM, BIF, SAM, SRBM, UVD, VMC, RLC, PDMA, and CG; `IH_PERF_SEL`, `SRBM_PERFCOUNT1_SEL`, and `SDMA_PERF_SEL` define event selectors written into perf-control fields.
- Routing/select enums: `SYS_GRBM_GFX_INDEX_SEL` and `SRBM_GFX_CNTL_SEL` select blocks for indirect GRBM/SRBM controls, including BIF, SDMA0/1, UVD, VCE0/1, ACP, SMU, SAMMSP/SAMSCP, ISP, test, and additional SDMA instances.
- Tiling/address enums: `SurfaceEndian`, `ArrayMode`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, `SampleSplitBytes`, `NumPipes`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `ShaderEngineTileSize`, `NumGPUs`, `MultiGPUTileSize`, `RowSize`, `NumLowerPipes`, `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, `BankWidthHeight`, and `MacroTileAspect`.
- Debug enums: `DebugBlockId` gives a dense newer client block map; `DebugBlockId_OLD` preserves the older debug block ID map; `DebugBlockId_BY2`, `DebugBlockId_BY4`, `DebugBlockId_BY8`, and `DebugBlockId_BY16` provide reduced block ID maps for stride/grouped debug selection.
- Format enums: `ColorTransform`, `CompareRef`, `ReadSize`, `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, `QuadExportFormatOld`, `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, and `IMG_NUM_FORMAT`.
- Miscellaneous hardware-policy enums: `GATCL1RequestType`, `TCC_CACHE_POLICIES`, `MTYPE`, `PERFMON_COUNTER_MODE`, `PERFMON_SPM_MODE`, `SurfaceTiling`, `SurfaceArray`, `ColorArray`, `DepthArray`, and `ENUM_NUM_SIMD_PER_CU`.

## Control Flow
This header has no executable paths. Control flow in consumers uses these enum constants as values shifted into register fields or compared against decoded field values. For example, an SDMA perf setup path can pick an `SDMA_PERF_SEL_*` selector, shift it into `SDMA0_PERFMON_CNTL__PERF_SEL*`, then write the register address from `oss_2_4_d.h`. Debug paths use the debug block ID enums to select hardware blocks before reading debug data.

## State and Persistence Behavior
The enum constants themselves are immutable compile-time symbols. They represent state encodings stored in GPU registers, ring packets, debug selectors, or tiling descriptors. Once a consumer writes one of these values to hardware, the selected performance event, debug block, memory tiling mode, format, or cache policy remains active according to the lifetime of the associated register or command until overwritten, reset, or consumed by hardware.

## Dependencies and Integration Points
- The enum values are meaningful only with register masks from `oss_2_4_sh_mask.h` and address definitions from `oss_2_4_d.h`.
- AMDGPU code also uses generic helper macros such as `REG_SET_FIELD`, so enum constants often appear as the value operand while mask headers provide the exact field placement.
- Graphics and memory-layout enum families need to stay consistent with packet formats, tiling/address library logic, and ASIC register documentation, even when this header is not directly included by every consumer.
- The header is guarded by `OSS_2_4_ENUM_H`, so it can be included by ASIC-specific code without duplicate type definitions.

## Risks
- Hardware enum values are ABI-like. Renumbering an enum to make it look cleaner would program different hardware behavior.
- Several enums include reserved or legacy names. Removing them can break code that preserves old debug layouts or handles reserved encodings defensively.
- Typographical artifacts such as `RESEVERED0` are part of the published symbol surface; fixing spelling without aliases can be source-incompatible.
- The file mixes unrelated domains. A consumer can compile while using the wrong enum family for a field if the value width happens to fit, so review must verify the target register field, not just C type compatibility.

## Test Signals
- Compile AMDGPU with warnings enabled to catch missing enum names or duplicate type definitions.
- Static review should verify each enum value against the OSS 2.4 hardware register database, especially selector enums and format/tiling encodings.
- Runtime test signals include valid interrupt source decoding, perf counters counting the selected event, debug reads targeting the expected block, and correct rendering/compute memory layout for surfaces using these format and tiling values.
- Negative signals include nonsensical perf counts, unreadable debug blocks, corrupted surfaces, failed VM/cache operations, or command processor faults after format or tiling changes.
