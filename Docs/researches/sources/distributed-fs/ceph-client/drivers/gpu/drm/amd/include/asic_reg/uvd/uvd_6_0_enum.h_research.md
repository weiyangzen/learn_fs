# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_6_0_enum.h

## Purpose

`uvd_6_0_enum.h` is a generated enum catalog for UVD 6.0 and related AMDGPU register programming. It assigns stable symbolic names to hardware ABI values: firmware command opcodes, debug block selectors, surface tiling and addressing modes, color/depth/buffer/image formats, cache policies, memory types, performance monitor modes, and memory power-control states. It declares 64 `typedef enum` types and no functions or state.

## Important APIs, Types, And Macros

Key types include `UVDFirmwareCommand` for fence/trap/address/display/bitstream/EOD commands; `DebugBlockId` and `_BY2`/`_BY4`/`_BY8`/`_BY16` variants for debug mux selection; surface/addressing enums such as `ArrayMode`, `PipeTiling`, `BankTiling`, `NumPipes`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `NumGPUs`, and `RowSize`; format enums such as `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, and `IMG_NUM_FORMAT`; tiling detail enums such as `MicroTileMode`, `TileSplit`, `PipeConfig`, `NumBanks`, and bank dimensions; and cache/perf/power enums such as `GATCL1RequestType`, `TCC_CACHE_POLICIES`, `MTYPE`, `PERFMON_COUNTER_MODE`, `PERFMON_SPM_MODE`, and `MEM_PWR_*`.

## Control Flow And Data Flow

This header has no control flow. Driver code chooses enum values, shifts/masks them into register fields or firmware command payloads, and hardware or firmware interprets the numeric value. `UVDFirmwareCommand` is the most UVD-specific path because it maps software decode command intent into the UVD firmware protocol.

## State And Persistence Behavior

Enum declarations hold no runtime state. Persistence occurs when a value is written into a register, descriptor, context, or firmware command stream. Those values can affect persistent tiling interpretation, format interpretation, cache behavior, memory routing, power mode, debug selection, or performance counter configuration.

## Dependencies And Integration Points

The file only requires C enum support. It integrates with UVD firmware command submission, `uvd_6_0_sh_mask.h` field composition, GPU address/tiling setup, memory and cache policy code, debug block selection, performance monitor setup, and power management.

## Risks And Edge Cases

The numeric enum values are hardware ABI values; renumbering reserved entries can break programming while compiling cleanly. Debug block variants must match the target register width. Generic enum names may collide semantically with other ASIC generations. Format and tiling values must fit the destination field width. Reserved values should not be used without a documented workaround.

## Test Signals

Use compile coverage, generated enum diffs, firmware command tests for fences/traps/EOD and bitstream/display address commands, decode tests with tiled and linear surfaces, format compatibility tests, debug/perf selector smoke tests, and memory power transition tests.
