# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_pptable.h

## Purpose

This header is the packed Vega10 ATOMBIOS PowerPlay table schema. It defines platform capability flags, state classifications, voltage modes, and all subtable layouts consumed by the Vega10 PowerPlay parser.

## Important APIs, Types, and Functions

The root `ATOM_Vega10_POWERPLAYTABLE` contains fixed header fields and offsets to subtables: state, fan, thermal controller, SOC/MEM/GFX/DCEF/PIX/DISP/PHY clock dependencies, voltage lookups, multimedia dependencies, VCE states, PowerTune, hard limits, and PCIe levels. Dynamic-array structs model BIOS records with `ucNumEntries` plus trailing `entries[]`, including `ATOM_Vega10_State_Array`, clock dependency tables, voltage lookup tables, MM dependency tables, PCIe tables, and hard-limit tables. Fan and PowerTune tables have multiple revisions: fan table V1/V2/V3 and PowerTune V1/V2/V3. Macros define thermal-controller IDs, fan-parameter bits, platform caps such as BACO and hardware DC, UI classification values, DC/VariBright flags, table revision, and voltage modes.

## Control Flow, State, and Persistence

The file is declarative, but because it is wrapped in `#pragma pack(push, 1)`, every field layout is persistent ABI with VBIOS data. Parser code computes subtable addresses by adding little-endian offsets from the root table to the base pointer, then converts individual little-endian fields into host-side hwmgr structures.

## Dependencies and Integration Points

It depends on ATOM firmware scalar typedefs such as `UCHAR`, `USHORT`, `ULONG`, and `struct atom_common_table_header`. `vega10_processpptables.c` uses nearly every table here. `vega10_thermal.c` and `vega10_powertune.c` receive values that originated in these records through `phm_ppt_v2_information`, `phm_tdp_table`, and `hwmgr->thermal_controller`.

## Risks and Test Signals

Packing, flexible arrays, and revision-dependent record formats make bounds and offset validation critical. Parser tests should cover all supported fan and PowerTune revisions, zero offsets, zero-entry dependency tables, high/low endian conversions, excessive PCIe entries, hard-limit absence, and table-size validation against offsets before dereference. ABI drift in this header can break VBIOS parsing without compiler errors.
