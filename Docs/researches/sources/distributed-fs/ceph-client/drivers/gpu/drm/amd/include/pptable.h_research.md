# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/pptable.h

## Purpose

`pptable.h` defines the packed ATOMBIOS PowerPlay table ABI used by AMDGPU legacy power-management code. It is not an algorithmic implementation; it is a binary layout contract for parsing firmware-provided performance, voltage, thermal, fan, PCIe, multimedia, and platform power data.

The file uses `_PPTABLE_H` and wraps all definitions in `#pragma pack(1)`, then restores packing with `#pragma pack()`. That packing is central: most structures map directly onto byte streams read from BIOS tables.

## Important APIs, Types, And Data

Major exported structure families:

- Thermal and fan metadata: `ATOM_PPLIB_THERMALCONTROLLER`, `ATOM_PPLIB_FANTABLE` through `ATOM_PPLIB_FANTABLE5`, and controller constants such as `ATOM_PP_THERMALCONTROLLER_*` plus fan parameter flags.
- Main PowerPlay table revisions: `ATOM_PPLIB_POWERPLAYTABLE`, `ATOM_PPLIB_POWERPLAYTABLE2`, `ATOM_PPLIB_POWERPLAYTABLE3`, `ATOM_PPLIB_POWERPLAYTABLE4`, and `ATOM_PPLIB_POWERPLAYTABLE5`. Later versions extend earlier versions by embedding the previous version as `basicTable*` and adding offsets or power fields.
- Extended offsets: `ATOM_PPLIB_EXTENDEDHEADER` points to VCE, UVD, SAMU, PPM, ACP, PowerTune, SCLK/VDDGFX dependency, and VQ budgeting subtables.
- State and non-clock descriptors: `ATOM_PPLIB_STATE`, `ATOM_PPLIB_STATE_V2`, `StateArray`, `ClockInfoArray`, `NonClockInfoArray`, `ATOM_PPLIB_NONCLOCK_INFO`, and `ATOM_PPLIB_THERMAL_STATE`.
- ASIC clock formats: `ATOM_PPLIB_R600_CLOCK_INFO`, `ATOM_PPLIB_RS780_CLOCK_INFO`, `ATOM_PPLIB_EVERGREEN_CLOCK_INFO`, `ATOM_PPLIB_SI_CLOCK_INFO`, `ATOM_PPLIB_CI_CLOCK_INFO`, `ATOM_PPLIB_SUMO_CLOCK_INFO`, `ATOM_PPLIB_KV_CLOCK_INFO`, and `ATOM_PPLIB_CZ_CLOCK_INFO`.
- Dependency and limit tables: `ATOM_PPLIB_Clock_Voltage_Dependency_*`, `ATOM_PPLIB_Clock_Voltage_Limit_*`, `ATOM_PPLIB_CAC_Leakage_*`, and `ATOM_PPLIB_PhaseSheddingLimits_*`.
- Multimedia and power subtables: VCE, UVD, SAMU, ACP, PowerTune, PPM, and VQ budgeting record/table structures.

Important macro groups include platform capabilities in `ulPlatformCaps`, non-clock classification flags, `ulCapsAndSettings` PCIe/display/video flags, R600 clock flags, RS780 voltage/sideport/HT constants, PPM design constants, and VQ display config constants.

Several structures use flexible arrays annotated with `__counted_by`, such as `ucClockStateIndices[]`, `clockInfoIndex[]`, `entries[]`, and `nonClockInfo[]`. Consumers must combine the count fields with table offsets and entry sizes rather than using `sizeof` as a complete allocation size.

## Control Flow

There is no function-level control flow in this header. The runtime flow happens in parsers:

1. AMDGPU locates an ATOMBIOS PowerPlay table and casts or copies the bytes into one of the packed `ATOM_PPLIB_POWERPLAYTABLE*` layouts.
2. The parser checks `usTableSize`, data revision, and structure size before accessing fields added by later revisions.
3. Offset fields such as `usStateArrayOffset`, `usClockInfoArrayOffset`, `usNonClockInfoArrayOffset`, `usFanTableOffset`, dependency-table offsets, and extended-header offsets are added to the base table pointer.
4. Counted arrays and entry-size fields determine how many records to walk.
5. Parsed data is translated into DPM states, voltage dependencies, fan policy, PCIe link policy, multimedia clock limits, PowerTune limits, and platform capability flags.

Direct integration found in this tree includes `include/atombios.h`, `pm/powerplay/hwmgr/processpptables.c`, and legacy DPM files such as `pm/legacy-dpm/legacy_dpm.c`, `si_dpm.c`, and `kv_dpm.c`. `legacy_dpm.c` walks clock-voltage dependency records, table revision extensions, CAC leakage, phase shedding, and other offsets defined here.

## State And Persistence Behavior

The header itself stores no mutable state. It defines how persistent firmware data is interpreted. The underlying data comes from ATOMBIOS/VBIOS and remains the platform's power-management policy source for the booted device. Driver consumers derive runtime state from it: available performance states, clock/voltage dependencies, fan curves, thermal-controller behavior, platform capability bits, PowerTune budgets, and multimedia clock constraints.

Because structures are packed ABI definitions, changing field order, width, packing, or offset semantics would change how persistent BIOS bytes are decoded and can break existing firmware tables.

## Dependencies

This header depends on ATOMBIOS scalar aliases and common table types such as `UCHAR`, `USHORT`, `ULONG`, and `ATOM_COMMON_TABLE_HEADER`, supplied through surrounding AMDGPU ATOMBIOS headers. It also depends on compiler support for packed pragmas, flexible arrays, and the kernel's `__counted_by` annotation in newer hardened builds.

Practical dependencies include all legacy PowerPlay/DPM parsers that trust these definitions, firmware/BIOS table producers that populate the same binary layouts, and any diagnostics that dump or validate PowerPlay table contents.

## Integration Points

`pptable.h` is included from `atombios.h`, making its ABI visible to broader AMDGPU ATOMBIOS consumers. It is directly used by legacy PowerPlay and DPM parser code to build runtime power states. `processpptables.c` is a central integration point for parsing PowerPlay tables, while `legacy_dpm.c`, `si_dpm.c`, and `kv_dpm.c` consume specific revisions and dependency tables.

The table contents feed clock selection, voltage control, fan and thermal handling, PCIe link choices, multimedia engine limits, PowerTune enforcement, and OverDrive-style maximum clock reporting. Bugs here therefore cross module boundaries between firmware parsing, power management, thermal control, display/video capabilities, and hardware bring-up.

## Risks

The highest risk is ABI drift. `#pragma pack(1)` is required; removing or changing it would alter offsets and corrupt parsing. Extending structures without updating size checks, offsets, and revision handling can make old BIOS tables appear to contain fields that are not present. Flexible arrays and offset-based subtables require strict bounds checking because the data source is firmware-provided bytes.

Integer unit mistakes are also risky. The file mixes units such as 10 kHz-style split clock fields, MHz comments for older tables, milliwatts, centigrade hundredths, PWM hundredths of a percent, and milliohm scaled values. Misinterpreting a field can cause unstable clocks, unsafe voltage decisions, bad fan response, or incorrect power caps.

The use of nested versioned structures (`POWERPLAYTABLE2` through `5`) creates compatibility risk: consumers must check `usTableSize` before touching later fields such as dependency offsets, CAC leakage, TDP limits, and load-line slope. Count fields and entry-size fields must be trusted only after validating that the computed range stays inside the table.

## Test Signals

Compile tests should cover legacy DPM and PowerPlay parsers with packed layout warnings enabled. Runtime signals include successful parsing of known VBIOS PowerPlay tables across R600, RS780, Evergreen, SI, CI, Sumo, Kaveri, and Carrizo-era devices; correct DPM state enumeration; valid fan table loading; sane voltage dependency tables; and stable PowerTune limits.

Negative tests should feed truncated or malformed tables and verify that parsers reject out-of-bounds offsets and impossible counts. Hardware signals include stable boot clocks, DPM transitions, suspend/resume, thermal response, PCIe link changes, UVD/VCE/ACP/SAMU clock constraints, and absence of overclock/OverDrive limit regressions.
