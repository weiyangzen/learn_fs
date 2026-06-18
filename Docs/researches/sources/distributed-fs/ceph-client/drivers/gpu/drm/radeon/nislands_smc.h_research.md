# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/nislands_smc.h

## Purpose
`nislands_smc.h` defines the packed host-side data layout used to communicate Northern Islands dynamic power-management state to the SMC firmware. It describes performance levels, software states, voltage masks, CAC tables, memory-controller register tables, DRAM timing tables, SPLL divider tables, and SMC firmware-header offsets.

## Important APIs, Types, And Functions
The header exports packed structs, not functions. Key types are `PP_NIslands_Dpm2PerfLevel` and `PP_NIslands_DPM2Parameters` for DPM2/TDP tuning; `NISLANDS_SMC_SCLK_VALUE`, `NISLANDS_SMC_MCLK_VALUE`, and `NISLANDS_SMC_VOLTAGE_VALUE` for PLL and voltage programming; `NISLANDS_SMC_HW_PERFORMANCE_LEVEL` for one hardware level; `NISLANDS_SMC_SWSTATE`, `NISLANDS_SMC_SWSTATE_SINGLE`, and `NISLANDS_SMC_STATETABLE` for firmware state tables; `PP_NIslands_CACTABLES` and `SMC_NISLANDS_MC_TPP_CAC_TABLE` for power estimation; `SMC_NIslands_MCRegisters` and `SMC_NIslands_MCArbDramTimingRegisters` for memory-controller programming; and `SMC_NISLANDS_SPLL_DIV_TABLE` for firmware clock lookup.

## Control Flow
There is no executable control flow. Runtime DPM code fills these structures from BIOS PowerPlay tables, calculated PLL values, voltage dependencies, and memory timing, writes them to SMC SRAM at offsets advertised by the firmware header, and then sends SMC messages to switch or enable states. The flexible `NISLANDS_SMC_SWSTATE.levels[]` and the fixed `driverState` plus `dpmLevels[]` arrangement allow the host to present a driver-selected sequence of levels to firmware.

## State, Persistence, And Dependencies
The file uses `#pragma pack(push, 1)` because the structures are firmware ABI, not normal kernel-only data. State persists in SMC SRAM and is interpreted by microcode after host upload. It depends on fixed-width integer types and on common SMC/PowerPlay flags from `ppsmc.h` and BIOS parsing code. The firmware-header offset constants such as `NISLANDS_SMC_FIRMWARE_HEADER_stateTable`, `cacTable`, `mcRegisterTable`, and `spllTable` define where the driver discovers SMC SRAM destinations.

## Integration Points
Northern Islands DPM code uses these layouts when constructing SCLK/MCLK, voltage, CAC, memory timing, and state tables. The register field names mirror hardware registers from `nid.h`, letting code copy calculated register values directly into firmware-facing tables. The structures are also tied to AtomBIOS PowerPlay data from `pptable.h`, which supplies clock, voltage, platform, and classification inputs.

## Risks
The dominant risk is ABI drift: padding, type-size, endian, or layout changes would corrupt SMC SRAM interpretation. Flexible arrays and fixed maximums (`NISLANDS_MAX_SMC_PERFORMANCE_LEVELS_PER_SWSTATE`, `SMC_NISLANDS_MC_REGISTER_ARRAY_SIZE`, `SMC_NISLANDS_MC_REGISTER_ARRAY_SET_COUNT`) require strict bounds in producers. Many fields are raw precomputed register values, so validation must happen before upload. CAC and voltage-mask tables can affect thermal and power limits, making unit or scaling mistakes hardware-visible. Because this is shared with firmware, comments and names are not enough; byte offsets must remain stable.

## Test Signals
High-value tests include DPM enable/disable on NI cards, SMC state-table upload verification, SCLK/MCLK switching, voltage-mask transitions, UVD/display watermark changes, memory-clock transition tests using MC register tables, suspend/resume DPM restoration, thermal/CAC throttling behavior, and compile-time or runtime size/offset checks against firmware expectations.
