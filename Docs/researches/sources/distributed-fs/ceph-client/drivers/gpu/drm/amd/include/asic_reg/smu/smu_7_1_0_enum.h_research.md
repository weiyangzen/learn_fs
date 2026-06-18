# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_0_enum.h

## Purpose

`smu_7_1_0_enum.h` is the generated enum/value companion for the SMU 7.1.0 ASIC register set. It defines numeric constants and C enum types for values that are written to, or interpreted from, hardware fields and SMU firmware interfaces. The file is static metadata, not executable logic.

The header complements `smu_7_1_0_d.h` and `smu_7_1_0_sh_mask.h`: the `_d.h` file supplies register addresses, `_sh_mask.h` supplies field positions and masks, and this file supplies named values for those fields. The values cover SMC firmware messages, ROM/version constants, surface and memory tiling modes, debug block identifiers, data/number formats, cache policies, and perfmon modes.

## Important APIs, Types, And Constants

The file exports both macro constants and `typedef enum` types.

Important macro constants:

- Address/range metadata: `CG_SRBM_START_ADDR`, `CG_SRBM_END_ADDR`, `RCU_CCF_DWORDS0`, `RCU_CCF_BITS0`, `RCU_CCF_DWORDS1`, `RCU_CCF_BITS1`, `RCU_SAM_BYTES`, `RCU_SAM_RTL_BYTES`, `RCU_SMU_BYTES`, and `RCU_SMU_RTL_BYTES`.
- Key/SAMU metadata: `KEYS_CHAIN_ADR`, `SAMU_KEY_SADR`, and `SAMU_KEY_EADR`.
- SMC firmware messages: `SMC_MSG_TEST`, PHY/DDI/cascade PLL power messages, `SMC_MSG_CONFIG_LCLK_DPM`, cache flush messages, BAPM/TDC/LPM/HTC/thermal/voltage/TDP control messages, `SMC_MSG_EN_PM_CNTL`, `SMC_MSG_DIS_PM_CNTL`, `SMC_MSG_CONFIG_NBDPM`, loadline messages, `SMC_MSG_RESET`, and `SMC_MSG_VOLTAGE`.
- Firmware/version metadata: `SMC_VERSION_MAJOR`, `SMC_VERSION_MINOR`, `SMC_HEADER_SIZE`, and `ROM_SIGNATURE`.

Important enum families:

- Surface layout and tiling: `SurfaceEndian`, `ArrayMode`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, `SampleSplitBytes`, `NumPipes`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `ShaderEngineTileSize`, `NumGPUs`, `MultiGPUTileSize`, `RowSize`, `NumLowerPipes`, `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, `BankWidthHeight`, `MacroTileAspect`, `SurfaceTiling`, `SurfaceArray`, `ColorArray`, and `DepthArray`.
- Debug block maps: `DebugBlockId`, `DebugBlockId_OLD`, `DebugBlockId_BY2`, `DebugBlockId_BY4`, `DebugBlockId_BY8`, and `DebugBlockId_BY16`. These provide full and stride-compressed block IDs for debug/perf infrastructure across graphics, memory, display, video, SMU, and other blocks.
- Render/format encodings: `CompareRef`, `ReadSize`, `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, `QuadExportFormatOld`, `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, and `IMG_NUM_FORMAT`.
- Cache and performance monitoring: `TCC_CACHE_POLICIES`, `PERFMON_COUNTER_MODE`, and `PERFMON_SPM_MODE`.

The type names are intentionally broad and shared across generated ASIC headers. Including many generated enum headers into the same translation unit could collide on common typedef names such as `SurfaceFormat` or `DebugBlockId`, so these headers are normally selected carefully by ASIC generation.

## Control Flow

There is no control flow in this header. Runtime behavior appears when consumers use these values:

1. A caller chooses an enum value or `SMC_MSG_*` command.
2. The value is packed into a register field using masks/shifts from a matching `*_sh_mask.h` header, or sent through an SMU mailbox register from the matching `_d.h` header.
3. Hardware or firmware interprets the raw numeric value according to the SMU 7.1.0 contract.

For the SMC message constants, the expected control flow is the mailbox flow seen in SMU code: write argument data if required, write a message ID, poll the response field, and handle success, unsupported-message, or failure codes. The enum constants themselves do not define timeout, retry, or error-handling policy.

## State And Persistence Behavior

The header stores no state. The values it defines classify state owned elsewhere:

- `SMC_MSG_*` values drive transitions inside SMU firmware, such as enabling/disabling power-management control, configuring DPM, flushing caches, resetting firmware, or changing voltage-related state.
- Format and tiling enum values describe persistent metadata in command streams, buffer descriptors, surface descriptors, or register fields interpreted by the GPU.
- Debug block IDs and perfmon modes describe hardware selection state for debug/performance counter registers.
- Version and ROM signature constants describe expected firmware/image metadata and are useful for validating firmware tables.

Incorrect values can persist indirectly when written into hardware tables, firmware SRAM, descriptors, or registers. The header itself has no save/restore behavior.

## Dependencies And Integration Points

Direct source dependencies are minimal: this is standalone C preprocessor and enum syntax protected by `SMU_7_1_0_ENUM_H`.

Integration dependencies include:

- Register addresses in `smu_7_1_0_d.h` and bit masks in `smu_7_1_0_sh_mask.h`.
- SMU and power-management code that sends messages through `mmSMC_MESSAGE_*`, `mmSMC_RESP_*`, and `mmSMC_MSG_ARG_*` registers.
- Firmware interfaces that expect specific `SMC_MSG_*` command IDs and `SMC_VERSION_*` metadata.
- Graphics address-library or register-programming code that interprets tiling, pipe, bank, surface format, and numerical format values.
- Debug/perf tooling that uses debug block IDs and perfmon mode constants to select hardware blocks and counter behavior.

A tree search found this exact header only as a generated file, not as a direct include in the local AMDGPU subtree. Adjacent generated enum headers define the same broad type families for other blocks and revisions, so use is likely revision-selected or retained as part of a complete generated register snapshot.

## Risks

- The values are ABI-like hardware and firmware contracts. Renumbering any enum member or `SMC_MSG_*` macro can silently program a different mode or send a different firmware command.
- Broad typedef names such as `SurfaceFormat`, `PipeConfig`, and `DebugBlockId` can collide if multiple generated enum headers are included together without generation-specific isolation.
- Several debug block enums encode related views of the same block space at different strides (`OLD`, `BY2`, `BY4`, `BY8`, `BY16`). Consumers must choose the table matching the relevant hardware field width or sampling granularity.
- Reserved values are explicit and should not be reused without matching hardware documentation. Treating reserved entries as free extension points would risk undefined hardware behavior.
- SMC message constants in this file are not the same namespace as all `PPSMC_MSG_*` values used by higher-level powerplay code. Mixing command families without checking the target firmware interface can produce unsupported or dangerous messages.
- Since there is no direct consumer in the scanned tree, accidental changes may escape ordinary compilation unless generated-header validation or hardware-specific builds exercise SMU 7.1.0.

## Test Signals

Useful validation signals include:

- Compile tests for any configuration that includes SMU 7.1.0 enum headers, especially translation units that include adjacent ASIC headers where typedef-name collisions could surface.
- Static comparison against generated register specifications or known-good adjacent headers to verify enum values have not drifted.
- Runtime mailbox tests on matching hardware for core `SMC_MSG_*` commands, checking response codes and kernel logs for unsupported-message or failed-message results.
- Graphics mode-setting, buffer/surface, and tiling tests that exercise `ArrayMode`, `PipeConfig`, format, and numeric-format encodings.
- Debug/perf counter smoke tests that select debug blocks and perfmon modes, ensuring block IDs map to expected hardware counters.
- Firmware/ROM validation tests that verify `SMC_VERSION_MAJOR`, `SMC_VERSION_MINOR`, `SMC_HEADER_SIZE`, and `ROM_SIGNATURE` match the firmware blobs expected for SMU 7.1.0.
