# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_pptable.h

## Purpose
`vega20_pptable.h` defines the packed AtomBIOS PowerPlay table format for Vega20. It bridges VBIOS-provided board policy data to the driver's parsed `phm_ppt_v3_information` and SMU `PPTable_t`.

## Important APIs, Types, and Functions
The key type is `ATOM_Vega20_POWERPLAYTABLE`, a packed structure containing the Atom common header, table revision and size, platform caps, thermal controller type, power limits, software shutdown temperature, power-saving clock table, OverDrive8 table, reserve fields, and embedded `PPTable_t smcPPTable`. Supporting types define OD8 feature/setting identifiers, `ATOM_VEGA20_OVERDRIVE8_RECORD`, `ATOM_VEGA20_POWER_SAVING_CLOCK_RECORD`, and PP clock identifiers.

## Control Flow
There is no executable control flow. `vega20_processpptables.c` reads these structures, validates revisions, copies OD8 arrays and power-saving clock ranges, extracts board power limits, and duplicates the embedded `smcPPTable` for later upload by `vega20_hwmgr.c`.

## State and Persistence
The structures describe persistent VBIOS data, but this header only defines its in-memory representation. Parsed copies live in `hwmgr->pptable` and `data->smc_state_table.pp_table`.

## Dependencies and Integration Points
It depends on AtomBIOS scalar typedefs (`UCHAR`, `USHORT`, `ULONG`) and `smu11_driver_if.h`'s `PPTable_t` through includers. It is tightly coupled to the firmware-supported `PPTABLE_V20_SMU_VERSION` checked by the parser.

## Risks
Packed layout must match VBIOS exactly. Revision/count mismatches can cause rejected PPTable initialization or misinterpreted OD ranges. OD8 enum ordering is mirrored by the hwmgr OD8 setting code, so drift between Atom table IDs and driver setting IDs is risky.

## Test Signals
Boot logs should not report unsupported PPTable format or version mismatch. OD8 sysfs ranges, thermal limits, fan maximum RPM, and power-saving clock limits should reflect board VBIOS values.
