# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce110/command_table_helper_dce110.c

## Purpose
This file defines the DCE10/DCE11 command-table helper vtable, mapping DC signal, HPD, PLL, action, and power-gating enums into ATOM values appropriate for DCE110-era VBIOS tables.

## Important APIs, Types, And Functions
- `dal_cmd_tbl_helper_dce110_get_table()` returns the static helper table.
- Static mappings include `signal_type_to_atom_dig_mode()`, `hpd_sel_to_atom()`, `dig_encoder_sel_to_atom()`, `clock_source_id_to_atom()`, `encoder_action_to_atom()`, and `disp_power_gating_action_to_atom()`.

## Control Flow
The mapping functions are switch-based and are referenced through `command_table_helper_funcs`. For DCE110 and later, `dig_encoder_sel_to_atom()` always returns zero because the link encoder programs DIG front-end selection outside these VBIOS commands.

## State And Persistence
The helper table is immutable static data. No runtime state is stored.

## Dependencies And Integration Points
It depends on `atom.h`, BIOS parser types, and the shared legacy helper functions from `command_table_helper.h`. It is selected by `dal_bios_parser_init_cmd_tbl_helper()` for DCE10 and DCE11.0.

## Risks
The helper table leaves some callbacks `NULL`, including legacy control parameter assignment and ref-clock source translation. Command paths requiring those callbacks must not be selected for DCE110. Defaults for unknown signal types fall back to DVI-style modes.

## Test Signals
Useful signals are successful UNIPHY transmitter programming on DCE110, correct HPD routing, no calls into NULL callbacks, and expected command parameters for DP MST, HDMI, DVI, and eDP links.
