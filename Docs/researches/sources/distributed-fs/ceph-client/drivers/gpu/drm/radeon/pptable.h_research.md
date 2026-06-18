# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/pptable.h

## Purpose
`pptable.h` defines packed AtomBIOS PowerPlay table layouts and constants used by Radeon power-management code. It describes thermal controllers, fan tables, platform capabilities, PowerPlay table revisions, state arrays, non-clock metadata, ASIC-specific clock-info records, clock/voltage dependency tables, leakage and phase-shedding tables, multimedia clock tables, PowerTune tables, and platform power-management data.

## Important APIs, Types, And Functions
The file is a data ABI header. Core types include `ATOM_PPLIB_POWERPLAYTABLE` through `ATOM_PPLIB_POWERPLAYTABLE5`, `ATOM_PPLIB_THERMALCONTROLLER`, `ATOM_PPLIB_FANTABLE*`, `ATOM_PPLIB_EXTENDEDHEADER`, `ATOM_PPLIB_STATE` and `ATOM_PPLIB_STATE_V2`, `StateArray`, `ClockInfoArray`, `NonClockInfoArray`, `ATOM_PPLIB_NONCLOCK_INFO`, clock info records for R600/RS780/Evergreen/SI/CI/Sumo, dependency and limit tables for clock/voltage, `ATOM_PPLIB_CAC_Leakage_Table`, `ATOM_PPLIB_PhaseSheddingLimits_Table`, VCE/UVD/SAMU/ACP tables, `ATOM_PPLIB_POWERTUNE_Table*`, and `ATOM_PPLIB_PPM_Table`.

## Control Flow
There is no direct control flow. Power-management code reads the BIOS PowerPlay table header, follows offsets to variable-length arrays, converts non-clock classifications into driver power-state classes, converts clock-info records into SCLK/MCLK/VDDC/VDDCI/PCIe settings, applies platform capability bits, and uses extended-header offsets to discover optional tables for fan, VCE, UVD, SAMU, ACP, PowerTune, leakage, and dependency data. Later DPM code translates those parsed records into SMC state tables and mailbox commands.

## State, Persistence, And Dependencies
The persistent source of truth is the AtomBIOS image. This header must match that firmware binary layout, so it uses `#pragma pack(1)`, BIOS integer typedefs (`UCHAR`, `USHORT`, `ULONG`), flexible arrays, and one-element trailing-array patterns. It depends on AtomBIOS common table headers and on consumers that validate revision, table size, entry size, offsets, and entry counts before dereferencing.

## Integration Points
`rv770_dpm.c`, `radeon_pm.c`, KV/CI-era DPM files, and other ASIC-specific PowerPlay parsers use these layouts to populate `struct radeon_power_state` and SMC tables. The classification and caps bits drive sysfs/profile selection, display/video state selection, AC/DC restrictions, dynamic refresh, PCIe lane/speed choices, and thermal/fan behavior. Optional multimedia tables integrate with UVD, VCE, SAMU, and ACP power management.

## Risks
This is BIOS ABI parsing, so malformed or unexpected offsets can lead to out-of-bounds reads if callers do not verify size. Many tables are variable-length and represented by flexible arrays or `entries[1]`, requiring careful bounds math. Revisions add fields by embedding previous table versions; code must use the actual table size and revision before reading newer offsets. `ATOM_PPLIB_SWSTATE_MEMORY_DLL_OFF` has an extra hex digit compared with nearby 32-bit flags, so consumers should confirm intended bit position. Packed BIOS structs can produce unaligned accesses if copied or cast carelessly on strict-alignment architectures. Comments show some partially modeled tables, such as VCE/UVD tables where nested arrays are commented out and consumers must manually walk the layout.

## Test Signals
Useful tests include parsing real BIOS PowerPlay tables across R600, RS780, Evergreen, SI, CI, Sumo, KV, and mobile/desktop variants; fuzzing table offsets/counts/revisions; validating derived power states and UI classes; fan table and thermal-controller detection; dependency-table voltage lookup; multimedia clock table lookup; PowerTune limit extraction; and suspend/resume transitions using parsed states.
