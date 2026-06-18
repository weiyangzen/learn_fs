# Research: subset-b-003409

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_0_d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_0_d.h

## Purpose

`smu_7_1_0_d.h` is a generated AMD SMU 7.1.0 register-definition header. It exports preprocessor constants that bind symbolic register names to the numeric MMIO, indirect-index, SRAM-table, thermal, power-management, ROM, fuse, and GPIO addresses for this ASIC generation. The file contains no executable code; its value is as a compile-time hardware contract used by register access helpers elsewhere in the AMDGPU power-management and SMU paths.

The header is guarded by `SMU_7_1_0_D_H` and is paired conceptually with `smu_7_1_0_sh_mask.h` for bitfield masks/shifts and with `smu_7_1_0_enum.h` for command and field-value encodings. It follows the local ASIC-register convention where `mm*` names identify directly addressed MMIO registers and `ix*` names identify indirect registers or indexed table locations reached through an SMU/GCK/ROM index/data window.

## Important APIs, Types, And Constants

This file does not define C functions, structs, or enums. Its API surface is the set of `#define` register constants.

Important exported groups include:

- Indirect SMU/GCK/ROM windows: `mmGCK_SMC_IND_INDEX`, `mmGCK_SMC_IND_DATA`, `mmSMC_IND_INDEX`, `mmSMC_IND_DATA`, numbered aliases such as `mmSMC_IND_INDEX_0` through `mmSMC_IND_INDEX_7`, and ROM aliases such as `mmROM_SMC_IND_INDEX`.
- SMU mailbox registers: `mmSMC_MESSAGE_0` through `mmSMC_MESSAGE_11`, `mmSMC_RESP_0` through `mmSMC_RESP_11`, and `mmSMC_MSG_ARG_0` through `mmSMC_MSG_ARG_11`. These form the host-to-SMC command channel used by driver code that writes an argument, writes a message ID, then polls a response register.
- SMC system-control and scratch/register addresses: `ixSMC_SYSCON_RESET_CNTL`, `ixSMC_SYSCON_CLOCK_CNTL_*`, `ixSMC_SYSCON_MISC_CNTL`, `ixSMC_SYSCON_MSG_ARG_0`, `ixSMC_PC_C`, and `ixSMC_SCRATCH9`.
- Clock-generation and PLL registers: `ixCG_DCLK_CNTL`, `ixCG_VCLK_CNTL`, `ixCG_ECLK_CNTL`, `ixCG_ACLK_CNTL`, `ixCG_SPLL_FUNC_CNTL*`, `ixSPLL_CNTL_MODE`, `ixCG_SPLL_SPREAD_SPECTRUM*`, `ixMPLL_BYPASSCLK_SEL`, `ixCG_CLKPIN_CNTL*`, `ixTHM_CLK_CNTL`, and `ixMISC_CLK_CTRL`.
- Fuse and firmware/status registers: `ixRCU_UC_EVENTS`, `ixRCU_MISC_CTRL`, `ixCC_*_FUSES`, `ixSMU_MAIN_PLL_OP_FREQ`, `ixSMU_STATUS`, `ixSMU_FIRMWARE`, `ixSMU_INPUT_DATA`, and `ixSMU_EFUSE_0`.
- Large contiguous SRAM/table maps: `ixDPM_TABLE_1` through `ixDPM_TABLE_506`, `ixMCARB_DRAM_TIMING_TABLE_1` through `ixMCARB_DRAM_TIMING_TABLE_144`, `ixMC_REGISTERS_TABLE_1` through `ixMC_REGISTERS_TABLE_113`, `ixFAN_TABLE_1` through `ixFAN_TABLE_9`, `ixSOFT_REGISTERS_TABLE_1` through `ixSOFT_REGISTERS_TABLE_30`, `ixPM_FUSES_1` through `ixPM_FUSES_19`, and `ixSMU_PM_STATUS_0` through `ixSMU_PM_STATUS_127`.
- Thermal and fan registers: `ixCG_THERMAL_INT_ENA`, `ixCG_THERMAL_INT_CTRL`, `ixCG_THERMAL_INT_STATUS`, `ixCG_THERMAL_CTRL`, `ixCG_THERMAL_STATUS`, `ixCG_FDO_CTRL*`, `ixCG_TACH_CTRL`, `ixCG_TACH_STATUS`, `ixTHM_TMON*_RDIL*_DATA`, `ixTHM_TMON*_RDIR*_DATA`, and TMON interrupt/debug registers.
- Power-management control registers: `ixGENERAL_PWRMGT`, `ixCNB_PWRMGT_CNTL`, `ixSCLK_PWRMGT_CNTL`, `ixTARGET_AND_CURRENT_PROFILE_INDEX`, `ixCG_FREQ_TRAN_VOTING_*`, `ixCG_ACPI_CNTL`, `ixSCLK_DEEP_SLEEP_CNTL*`, `ixLCLK_DEEP_SLEEP_CNTL*`, `ixCG_ULV_PARAMETER`, and `ixSCLK_MIN_DIV`.
- ROM-control/data registers: `ixROM_CNTL`, `ixPAGE_MIRROR_CNTL`, `ixROM_STATUS`, `ixROM_INDEX`, `ixROM_DATA`, `ixROM_START`, `ixROM_SW_CNTL`, `ixROM_SW_STATUS`, `ixROM_SW_COMMAND`, and `ixROM_SW_DATA_1` through `ixROM_SW_DATA_64`.

## Control Flow

There is no runtime control flow inside this header. Downstream control flow is implicit in the mailbox and indirect-register patterns:

1. Code selects an indirect SMC address by writing an `ix*` address to one of the `mmSMC_IND_INDEX_*` registers.
2. Code transfers data through the matching `mmSMC_IND_DATA_*` register.
3. For SMC commands, code optionally writes an argument to `mmSMC_MSG_ARG_0`, clears or checks `mmSMC_RESP_0`, writes a command ID to `mmSMC_MESSAGE_0`, and polls `mmSMC_RESP_0` until firmware returns a nonzero result.

Nearby consumers show the expected pattern. `pm/powerplay/smumgr/smu7_smumgr.c` uses SMU7 index/data and mailbox names in helpers such as `smu7_copy_bytes_to_smc()`, `smu7_send_msg_to_smc()`, and `smu7_send_msg_to_smc_with_parameter()`. The legacy `kv_smc.c` path uses equivalent SMU 7.0.0 constants in the same pattern, confirming the intended integration shape for this register family.

## State And Persistence Behavior

The header itself owns no mutable state and performs no persistence. The constants address persistent or semi-persistent hardware and firmware state:

- SMC SRAM and table regions hold firmware-owned DPM, memory-controller, fan, fuse, soft-register, and status data.
- `ixDPM_TABLE_*`, `ixMCARB_DRAM_TIMING_TABLE_*`, `ixMC_REGISTERS_TABLE_*`, and related table constants are offsets into firmware-visible storage, not host memory allocations.
- Mailbox registers are transient command/response state shared between the host driver and the SMC firmware.
- Fuse and ROM constants expose hardware configuration or firmware image data that may be read as stable device configuration, but writes to control registers can affect hardware behavior immediately.

Because these constants are direct hardware contracts, they should be treated as immutable for a given ASIC revision unless regenerated from authoritative register documentation.

## Dependencies And Integration Points

The file depends only on the C preprocessor and include-guard mechanics. Its real dependencies are external hardware contracts:

- The SMU 7.1.0 ASIC register map supplies the numeric addresses.
- Register-access macros and helpers such as `RREG32`, `WREG32`, `cgs_read_register()`, `cgs_write_register()`, `cgs_read_ind_register()`, and higher-level `PHM_*` field helpers consume these constants.
- `smu_7_1_0_sh_mask.h` supplies masks/shifts for fields at the addresses defined here.
- `smu_7_1_0_enum.h` supplies command IDs and enumerated field values that may be written through the mailbox or into related fields.
- Adjacent generated headers for `smu_7_0_0`, `smu_7_1_1`, `smu_7_1_2`, and `smu_7_1_3` provide compatible but revision-specific maps. Selecting the wrong revision can produce valid C that accesses the wrong hardware locations.

No exact `#include "smu/smu_7_1_0_d.h"` consumer was found in the scanned AMDGPU subtree, while the adjacent versioned headers are actively included by power-management code. This suggests this header is part of the generated ASIC-register inventory and may be selected indirectly, conditionally, or kept for completeness of supported revisions.

## Risks

- Address drift is the primary risk. A single incorrect constant can make the driver read or write the wrong MMIO or indirect register, causing power-management failures, firmware hangs, thermal/fan misbehavior, or GPU instability.
- The repeated table ranges are mechanically regular but easy to corrupt in manual edits. For example, `ixDPM_TABLE_*`, `ixSMU_PM_STATUS_*`, and ROM data ranges must remain contiguous 4-byte strides unless the hardware spec says otherwise.
- Mailbox aliasing is subtle. Multiple symbolic names share the same numeric index/data addresses for different blocks or instances. A change that appears to remove duplication can break code readability or generated-header parity.
- This header defines only addresses, not access ordering, locking, polling timeouts, or bitfield masks. Callers must still use the correct register access domain and the corresponding `*_sh_mask.h` field definitions.
- Because no direct consumer was found in this tree, compile coverage may not catch accidental changes unless a configuration or generated include path selects the 7.1.0 revision.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration signals:

- Build configurations that include SMU 7.1.0 headers should compile without duplicate-name or missing-mask errors.
- Static checks can verify contiguous ranges keep a 4-byte stride for the generated tables and that mailbox index/data pairs remain matched.
- Runtime SMU smoke tests on matching hardware should confirm SMC SRAM reads/writes, firmware message send/poll behavior, DPM table access, thermal status reads, and fan/ROM access continue to work.
- Kernel logs from SMU mailbox paths are important: unsupported or failed message responses after a register-map change are strong regression signals.
- Cross-checking against the adjacent `smu_7_1_0_sh_mask.h` should confirm every field mask is associated with an address constant expected by consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_0_d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_0_enum.h -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_0_enum.h -->
