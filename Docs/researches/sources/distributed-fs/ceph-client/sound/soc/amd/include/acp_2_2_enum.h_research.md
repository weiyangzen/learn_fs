# sources/distributed-fs/ceph-client/sound/soc/amd/include/acp_2_2_enum.h

## Purpose
`acp_2_2_enum.h` is a generated-style hardware enumeration header for AMD ACP/GPU-adjacent register documentation. It defines C `typedef enum` types and numeric symbolic values used to interpret or program register fields. Unlike `acp_2_2_d.h` and `acp_2_2_sh_mask.h`, it is not included by `sound/soc/amd/acp.h` in this tree, and no direct in-scope include use was found in the AMD ASoC subtree. It remains a source of hardware-documentation constants for ACP 2.2 related code or downstream users.

The contents are broader than audio-only ACP. They include debug block identifiers, surface endian and tiling modes, color/depth/image/buffer formats, memory/cache request modes, perfmon modes, surface layout enums, and ACP memory-power force/select controls.

## Important APIs, types, and constants
The file exports only enum types. Important families include:

- `DebugBlockId` plus `DebugBlockId_BY2`, `DebugBlockId_BY4`, `DebugBlockId_BY8`, and `DebugBlockId_BY16`, which encode debug block IDs at different grouping/stride granularities. These list many GPU blocks such as VMC, SRBM, GRBM, SDMA, SQ, TCP, TCC, TA, TD, LDS, and reserved/unused slots.
- Surface and memory layout enums: `SurfaceEndian`, `ArrayMode`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, `SampleSplitBytes`, `NumPipes`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `ShaderEngineTileSize`, `NumGPUs`, `MultiGPUTileSize`, `RowSize`, and `NumLowerPipes`.
- Render/data format enums: `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, `QuadExportFormatOld`, `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, and `IMG_NUM_FORMAT`.
- Tiling detail enums: `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, and `MacroTileAspect`.
- Cache/performance/system enums: `GATCL1RequestType`, `TCC_CACHE_POLICIES`, `MTYPE`, `PERFMON_COUNTER_MODE`, and `PERFMON_SPM_MODE`.
- ACP-relevant memory power enums: `MEM_PWR_FORCE_CTRL`, `MEM_PWR_FORCE_CTRL2`, `MEM_PWR_DIS_CTRL`, `MEM_PWR_SEL_CTRL`, and `MEM_PWR_SEL_CTRL2`.

There are no function prototypes, structs, macros, or inline helpers in this file.

## Control flow
There is no runtime control flow. If included, the C compiler makes these enum constants available to code that needs stable symbolic names for register-field values. Because this specific source tree does not show direct include usage for this header in the AMD audio subtree, its practical flow here is archival/generated hardware documentation rather than active execution.

## State and persistence behavior
The header has no software state and no persistence. The enum values describe possible hardware register field values. When used by callers, those values may influence persistent hardware state such as memory tiling configuration, cache policy, perfmon mode, or ACP memory power mode, but no such writes happen in this file.

## Dependencies and integration points
The header is self-contained apart from standard C enum syntax and its include guard. It pairs conceptually with the ACP2.2 offset and mask headers: offsets name registers, masks name bit fields, and enums can name legal field values. Within this repository snapshot, the direct integration is weak because `sound/soc/amd/acp.h` includes only `acp_2_2_d.h` and `acp_2_2_sh_mask.h`.

The broader integration point is generated AMD hardware register documentation. Downstream code that programs debug, tiling, format, perfmon, or ACP memory-power fields can include this header to avoid raw numeric literals.

## Risks and edge cases
Because these are hardware ABI values, changing names or numeric assignments can break register programming even when C compilation succeeds. The debug-block lists contain many `UNUSED` and reserved entries; using those as valid hardware targets could produce undefined hardware behavior. The file also mixes audio-adjacent ACP memory-power enums with graphics/display-oriented surface and format enums, so maintainers should not assume every enum is meaningful to the ALSA ACP drivers.

Another risk is dead/stale documentation: lack of current in-tree users means build tests may not catch accidental breakage until an external user includes it.

## Test signals
Test signals are mostly compile and hardware validation in code that includes this header:

- A full kernel build with any user that includes `acp_2_2_enum.h` catches syntax and renamed-type breakage.
- Static searches should confirm whether enum values are actively consumed before refactoring.
- Hardware tests for any driver using these values should validate register programming against expected modes, especially memory-power mode transitions and perfmon/debug block selection.
