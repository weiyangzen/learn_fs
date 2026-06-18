# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_3_0_1_enum.h

## Purpose

`oss_3_0_1_enum.h` is a generated AMDGPU OSS 3.0.1 enumeration header. It assigns hardware-defined numeric values to interrupt source ranges, performance-monitor selectors, debug block IDs, tiling modes, address-configuration fields, image/buffer/color/depth formats, cache and memory-type policies, and memory-power controls. It contains no executable logic; it is a compile-time ABI contract between driver code and register fields described by the OSS 3.0.1 register pack.

The values in this file are not arbitrary software enums. They are the literal bitfield encodings expected by GPU registers and packets. Changing them would change hardware behavior.

## Important APIs, Types, And Enums

The file exports C `typedef enum` declarations only. There are no functions, macros, structs, or data definitions.

Major enum groups:

- `IH_CLIENT_ID` defines interrupt source ID ranges for display controller, VGA, CAP, VIP, ROM, BIF, SAM, SRBM, UVD, VMC, RLC, PDMA, and clock-gating sources.
- `IH_PERF_SEL` defines interrupt-handler performance counter events such as cycles, idle, input idle, per-client IH stalls, ring-buffer idle/full/overflow, pointer writeback/wrap events, memory-controller write events, and BIF edge events.
- `SEM_PERF_SEL` defines semaphore performance events for cycles/idle, request signals and waits from SDMA/UVD/VCE/ACP/ISP/VP8/CPG/CPC clients, offload and poll waits for CPC engines, memory-controller read/write traffic, ATC requests/returns/XNACKs, and invalidations.
- `SRBM_PERFCOUNT1_SEL`, `SYS_GRBM_GFX_INDEX_SEL`, and `SRBM_GFX_CNTL_SEL` define SRBM performance and block-selection values for BIF, SDMA, IH, memory controller pieces, SEM, UVD, VMC, VCE, ACP, ISP, VP8, SMU, SAMMSP, and test paths.
- `SDMA_PERF_SEL` defines SDMA performance events for ring/IB idle and full status, pointer polling/writeback, execution idle, MC reads/writes, semaphore/interrupt handshakes, copy-engine stalls, GFX/RLC selection, context switching, doorbells, burst arbiter routes, F32/CE L1 events, ATCL2 invalidation/XNACK/ACK/free/send events, DMA L1/MC sends, L1 idle and invalidation wait states, and XNACK timeouts.
- `DebugBlockId` is a dense debug block ID table from `0x0` through `0xfe`, covering top-level blocks and many per-instance shader, texture, color buffer, depth buffer, TCP, TCC, TA, TD, and LDS instances. `DebugBlockId_BY2`, `DebugBlockId_BY4`, `DebugBlockId_BY8`, and `DebugBlockId_BY16` provide coarser grouped encodings.
- Surface and address layout enums include `SurfaceEndian`, `ArrayMode`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, `SampleSplitBytes`, `NumPipes`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `ShaderEngineTileSize`, `NumGPUs`, `MultiGPUTileSize`, `RowSize`, and `NumLowerPipes`.
- Render, depth, and format enums include `ColorTransform`, `CompareRef`, `ReadSize`, `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, `QuadExportFormatOld`, `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, and `IMG_NUM_FORMAT`.
- Tiling/cache/memory policy enums include `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, `BankWidthHeight`, `MacroTileAspect`, `GATCL1RequestType`, `TCC_CACHE_POLICIES`, and `MTYPE`.
- Perfmon and memory power enums include `PERFMON_COUNTER_MODE`, `PERFMON_SPM_MODE`, `SurfaceTiling`, `SurfaceArray`, `ColorArray`, `DepthArray`, `ENUM_NUM_SIMD_PER_CU`, `MEM_PWR_FORCE_CTRL`, `MEM_PWR_FORCE_CTRL2`, `MEM_PWR_DIS_CTRL`, `MEM_PWR_SEL_CTRL`, and `MEM_PWR_SEL_CTRL2`.

Some enumerator names are intentionally generic or generated, such as `RESERVED0` and `RESEVERED0`. Because C enumerator names live in the ordinary identifier namespace, this file should not be mixed casually with other generated enum headers that define the same names.

## Control Flow

There is no local control flow. Consumers use these enum constants as values written into register fields or as decoded values read from hardware state:

- Performance monitor setup code can select `IH_PERF_SEL`, `SEM_PERF_SEL`, `SRBM_PERFCOUNT1_SEL`, or `SDMA_PERF_SEL` values before reading corresponding counter result registers from the address header.
- SRBM/GRBM routing code can use `SYS_GRBM_GFX_INDEX_SEL` and `SRBM_GFX_CNTL_SEL` values when selecting a target block or routing register access through SRBM windows.
- Surface, tiling, format, and address configuration code can use the format and tiling enums when constructing register field values for display, memory controller, texture, color, depth, or buffer/image descriptors.
- Debug and perf tooling can use `DebugBlockId*` values to select a debug block or compact block group for broadcast or aggregation modes.

In this repository snapshot, direct `#include` use of `oss_3_0_1_enum.h` is not visible in the same way as `oss_3_0_1_d.h`; it is part of the generated OSS 3.0.1 register pack and may be consumed indirectly, conditionally, or by out-of-tree/generated code that programs these fields.

## State And Persistence Behavior

The header itself is stateless. Its values describe possible hardware state:

- Perf selector enums become state when written to perfmon select/control registers; counters then accumulate according to the selected event until reset or reprogrammed.
- Format and tiling enums become persistent descriptor or register fields for surfaces, buffers, images, render targets, depth buffers, and address calculations.
- Debug block IDs become selection state in debug/broadcast registers.
- Memory power enums become control state that can force or disable memory power behavior until changed or reset.

Because the constants are hardware encodings, persistence and lifetime are owned by the target register, descriptor, firmware command, or packet field that stores them.

## Dependencies

The header depends only on the C preprocessor/include system and its include guard `OSS_3_0_1_ENUM_H`. Runtime users depend on:

- Matching OSS 3.0.1 address and mask headers, especially `oss_3_0_1_d.h` and `oss_3_0_1_sh_mask.h`, for register addresses and field placement.
- Register access helpers such as `RREG32`, `WREG32`, `REG_SET_FIELD`, and `REG_GET_FIELD` when values are written to or read from MMIO registers.
- Higher-level AMDGPU surface, tiling, memory, perfmon, debug, and interrupt code that knows which enum type applies to a given field.

The values are ASIC-generation-specific. Similar enum names in `oss_3_0_enum.h` or newer generated headers may not be interchangeable.

## Integration Points

Expected integration points are the generated OSS register family and AMDGPU ASIC-specific code paths:

- `oss_3_0_1_d.h` names the registers whose fields may accept values from this enum header.
- `oss_3_0_1_sh_mask.h` names the bit ranges into which these enum values are packed.
- IH, SEM, SRBM, and SDMA perfmon code can combine this header's selector enums with the perfmon control/result registers.
- Surface and memory-layout setup code can use the tiling, format, pipe, bank, and row enums when programming descriptors or hardware registers for OSS 3.0.1-era devices.
- Debug tooling can use the full and grouped debug-block ID enums to select hardware blocks without using magic numbers.

## Risks

- Enum values are hardware ABI. Renumbering, deduplicating, or "cleaning up" reserved entries can silently break register programming.
- The header defines many globally visible enum constants with generic names. Including multiple generated enum headers in one translation unit may cause duplicate enumerator or typedef-name conflicts.
- The typo `RESEVERED0` in `SYS_GRBM_GFX_INDEX_SEL` is generated source. Correcting the spelling would be an API change for any code that references the generated name.
- Similar enum names exist across ASIC generations but can have different event sets or numeric encodings. Cross-generation reuse can produce valid C code that programs invalid hardware values.
- Some enums have reserved gaps or values that are valid only for particular blocks, pipe counts, or surface modes. Callers must validate against the target register and ASIC capability rather than assuming every enum member is legal in every context.
- Format and tiling constants affect memory interpretation. Wrong values can corrupt scanout, texture fetches, render targets, depth/stencil access, compression metadata, or DMA copies.

## Test Signals

- Compile tests should include any translation unit that uses this header alone and with its matching address/mask headers, catching duplicate-name or missing-name regressions.
- Perfmon tests should program representative IH, SEM, SRBM, and SDMA selector values and verify counters change under matching workloads.
- Surface-layout tests should cover linear, tiled, PRT, depth, color, buffer, image, FMASK, compressed, and endian-sensitive formats where applicable.
- Debug tooling tests should confirm `DebugBlockId` and grouped `BY2/BY4/BY8/BY16` values select the expected hardware blocks in register traces.
- Cross-generation tests should prevent accidental substitution of `oss_3_0_1_enum.h` with `oss_3_0_enum.h` or newer SOC15 enum headers in ASIC-specific code.
- Hardware register dumps and known-good traces are useful acceptance signals because many failures from wrong enum values are behavioral rather than compile-time errors.
