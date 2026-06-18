# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_processpptables.h

## Purpose

This header declares the Vega10 PowerPlay table parser interface and the BIOS I2C-line identifier mappings needed to translate PowerTune monitor lines into DAL/SMC line values.

## Important APIs, Types, and Functions

`enum Vega10_I2CLineID` defines BIOS line IDs for DDC1 through DDC6, shared SCL/SDA, and VGA DDC. The `Vega10_I2C_*` macros map those IDs to hardware line constants used by `get_scl_sda_value` in the C file. Exports include `vega10_pptable_funcs`, `vega10_get_number_of_powerplay_table_entries`, `vega10_get_powerplay_table_entry`, and `vega10_baco_set_cap`.

## Control Flow, State, and Persistence

The header does not own memory or state. Its function table export drives hwmgr initialization/fini, while the state-entry callback interface lets the broader PowerPlay stack interpret BIOS state records without exposing parser internals as public structs.

## Dependencies and Integration Points

It includes `hwmgr.h` for `struct pp_hwmgr`, `struct pp_power_state`, and `struct pp_table_func`. `vega10_hwmgr.c` assigns `hwmgr->pptable_func` to `vega10_pptable_funcs` and uses the entry accessors while building state tables. The I2C macros integrate with PowerTune table revisions that encode only a line ID rather than separate SCL/SDA values.

## Risks and Test Signals

The numeric I2C constants are hardware contracts and should match DAL/SMC expectations. Tests should cover each enum-to-SCL/SDA mapping, default mapping to zero for unknown IDs, ABI compatibility of the callback signature, and successful linkage of all exported parser functions.
