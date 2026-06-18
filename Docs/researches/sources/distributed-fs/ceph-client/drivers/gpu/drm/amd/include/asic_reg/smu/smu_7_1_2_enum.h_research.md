# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_2_enum.h

## Purpose

`smu_7_1_2_enum.h` is a generated AMDGPU constant and enum header for the SMU 7.1.2 hardware/software interface. It supplies numeric values used with SMU mailbox commands, firmware/ROM metadata, RCU/SFP/key address ranges, graphics memory tiling, surface and buffer formats, debug block selection, performance-monitor modes, cache/memory attributes, and memory power-control fields.

The file does not implement behavior. It defines the symbolic values that driver code writes into SMU, graphics, memory, debug, or power-management registers described by companion address and mask headers. The include guard is `SMU_7_1_2_ENUM_H`.

## Important APIs, Types, And Macros

The public interface consists of preprocessor constants and C `typedef enum` definitions. There are no functions, structs, global variables, or inline helpers.

Important macro groups include:

- `CG_SRBM_START_ADDR` and `CG_SRBM_END_ADDR`: clock-generator SRBM aperture bounds.
- `RCU_CCF_*`, `RCU_SAM_*`, and `RCU_SMU_*`: reset/control-unit chain size and bit-count metadata.
- `SFP_*`, `SAMU_KEY_*`, and `SMU_KEY_*`: security/fuse/key chain address ranges.
- `SMC_MSG_*`: SMC firmware command IDs, including PHY lane on/off, DDI PHY on/off, cascade PLL on/off, x16 power-off, LCLK DPM configuration, cache flushes, VPC accumulator, BAPM, TDC limit, LPMx, HTC limit, thermal, voltage, TDP, PM enable/disable, NBDPM, load-line adjustment, reset, and voltage commands.
- `SMC_VERSION_MAJOR`, `SMC_VERSION_MINOR`, `SMC_HEADER_SIZE`, and `ROM_SIGNATURE`: firmware/header/ROM metadata constants.

Important enum groups include:

- Surface layout and tiling: `SurfaceEndian`, `ArrayMode`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, `SampleSplitBytes`, `NumPipes`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `ShaderEngineTileSize`, `NumGPUs`, `MultiGPUTileSize`, `RowSize`, `NumLowerPipes`, `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, `BankWidthHeight`, and `MacroTileAspect`.
- Debug block selection: `DebugBlockId` plus legacy or compressed lookup forms `DebugBlockId_OLD`, `DebugBlockId_BY2`, `DebugBlockId_BY4`, `DebugBlockId_BY8`, and `DebugBlockId_BY16`. These enumerate graphics, memory, display, DMA, video, SMU, RLC, GRBM/SRBM, cache, texture, render-backend, and other hardware blocks.
- Render/depth/color formats: `ColorTransform`, `CompareRef`, `ReadSize`, `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, `QuadExportFormatOld`, `ColorFormat`, and `SurfaceFormat`.
- Texture/buffer formats: `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, and `IMG_NUM_FORMAT`, including integer, normalized, scaled, floating-point, packed, block-compressed, FMASK, and reserved values.
- Cache, memory, and performance controls: `GATCL1RequestType`, `TCC_CACHE_POLICIES`, `MTYPE`, `PERFMON_COUNTER_MODE`, and `PERFMON_SPM_MODE`.
- Surface array forms and hardware constants: `SurfaceTiling`, `SurfaceArray`, `ColorArray`, `DepthArray`, and `ENUM_NUM_SIMD_PER_CU`.
- Memory power control: `MEM_PWR_FORCE_CTRL`, `MEM_PWR_FORCE_CTRL2`, `MEM_PWR_DIS_CTRL`, `MEM_PWR_SEL_CTRL`, and `MEM_PWR_SEL_CTRL2`.

## Control Flow And Data Flow

The header has no runtime control flow. It participates in driver data flow by giving names to values that are encoded into registers, packets, tables, or firmware messages:

1. SMU code selects an `SMC_MSG_*` ID, writes any required argument through an SMC message-argument register from `smu_7_1_2_d.h`, posts the message, and polls a response register.
2. Graphics or memory-management code selects enum values such as `ARRAY_2D_TILED_THIN1`, `ADDR_SURF_P8_32x32_16x16`, `FMT_BC7`, `IMG_NUM_FORMAT_SRGB`, `MTYPE_CC`, or `TCC_CACHE_POLICY_STREAM` when programming fields in registers or descriptors.
3. Debug/performance code writes `DebugBlockId*`, `PERFMON_COUNTER_MODE`, or `PERFMON_SPM_MODE` values into block-selection or performance-monitor fields.
4. Power-management code uses memory power enum values to request light sleep, deep sleep, shutdown, disable, or dynamic selection behavior.

The driver must combine these values with the correct register addresses and field shifts/masks from companion generated headers. The enum names alone do not identify which register field accepts each value.

## State And Persistence Behavior

This header stores no state and performs no persistence. The constants become persistent only when consumers write them into hardware registers, firmware mailboxes, descriptor tables, or SMU-owned power-management tables.

Stateful hardware behavior described indirectly by these values includes:

- Firmware command state selected by `SMC_MSG_*` values.
- Security/fuse/key and ROM metadata ranges described by the top-level macros.
- Surface, texture, buffer, color, depth, stencil, compression, and tiling state encoded in graphics descriptors or registers.
- Debug block selection and performance-monitor accumulation/sample modes.
- Cache/memory attributes such as TCC policy, GATCL1 request type, and memory type.
- Memory power policy, including forced light sleep, deep sleep, shutdown, disabled control, and dynamic policy selection.

The enum values are effectively part of the binary hardware ABI. Changing one value changes what the kernel asks the ASIC or firmware to do.

## Dependencies And Integration Points

The file depends only on standard C enum syntax and the preprocessor. It is intended to be included with generated SMU address and field headers, especially `smu_7_1_2_d.h` and matching `*_sh_mask.h` files.

Integration points include:

- AMDGPU SMU/PowerPlay firmware message paths using `SMC_MSG_*`, `SMC_VERSION_*`, and `SMC_HEADER_SIZE`.
- Register programming that needs tiling, array, pipe/bank, row, macro-tile, and surface format values.
- Address-library or tiling calculations that translate hardware configuration into descriptors.
- Graphics pipeline setup for color/depth/stencil/CMASK/export/read-size/compare fields.
- Texture and buffer descriptor construction for `BUF_*` and `IMG_*` data and numeric formats.
- Debug and perf tooling that selects hardware blocks and counter/SPM modes.
- Cache, memory-translation, and memory-type setup using `GATCL1RequestType`, `TCC_CACHE_POLICIES`, and `MTYPE`.
- Memory and SRAM power-management controls using the `MEM_PWR_*` enum families.

## Risks And Edge Cases

- The values are generated hardware ABI constants. Renumbering, deleting, or substituting enum members can create silent runtime misprogramming rather than compile failures.
- Many enum names are shared conceptually with other ASIC generations but may not have identical numeric values. Consumers must include the version-correct header for SMU 7.1.2.
- Several enums contain reserved values. Driver code should avoid programming reserved encodings unless a hardware workaround explicitly requires them.
- `DebugBlockId`, `DebugBlockId_OLD`, and the `BY2`/`BY4`/`BY8`/`BY16` variants are related but not interchangeable. They represent different block-id maps or compressed block-id spaces.
- Format enums have overlapping-looking concepts across `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, and `IMG_DATA_FORMAT`. Using a value from the wrong enum family can encode a legal number with the wrong meaning.
- SMU message IDs only name commands. Correct behavior still depends on argument format, mailbox channel, firmware readiness, response handling, and the target firmware version.
- Power-control enum values can affect SRAM or memory power states. Incorrect selection may cause latency, data retention, or stability issues.
- C enums are unscoped, so all enumerators enter the global namespace. Collisions with other generated headers are possible if incompatible ASIC enum headers are included together.

## Test Signals

Useful validation signals for changes involving this header include:

- Compile AMDGPU configurations that include SMU 7.1.2 enum headers, catching missing names and global enumerator collisions.
- Diff constants and enum values against the canonical generated SMU 7.1.2 source.
- Run SMU firmware handshake tests for representative `SMC_MSG_*` commands, including PM enable/disable, reset, voltage, TDC/TDP, thermal, BAPM, NBDPM, load-line, and cache-flush messages.
- Exercise display/graphics workloads that cover linear, 1D/2D/3D tiled, PRT, thick/thin, pipe/bank, and macro-tile configurations.
- Validate texture, render-target, depth/stencil, CMASK, FMASK, block-compressed, SRGB, integer, normalized, scaled, and floating-point format programming.
- Run debug/performance monitor tests that select block IDs and use accumulation, active-cycle, dirty, sample, SPM clamp/no-clamp, and test modes.
- Test cache/memory attributes and GATCL1 request types under VM, cache-coherency, and translation-shootdown scenarios.
- Exercise memory power-management transitions with light-sleep, deep-sleep, shutdown, disable, and dynamic policy values during suspend/resume and high-load workloads.
