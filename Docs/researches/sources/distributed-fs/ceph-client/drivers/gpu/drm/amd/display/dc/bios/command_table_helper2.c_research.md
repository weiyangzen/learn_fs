# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table_helper2.c

## Purpose
This file provides the atomfirmware-era helper selection and shared enum translation functions for `command_table2.c`.

## Important APIs, Types, And Functions
- `dal_bios_parser_init_cmd_tbl_helper2()` selects helper tables for DCE and DCN versions, using the DCE112 helper2 table for DCE11.2+, DCE12, and all listed DCN versions.
- `dal_cmd_table_helper_controller_id_to_atom2()`, `*_transmitter_bp_to_atom2()`, `*_encoder_mode_bp_to_atom2()`, `*_clock_source_id_to_ref_clk_src2()`, and `*_encoder_id_to_atom2()` provide firmware-parser mappings.

## Control Flow
The DCE/DCN version switch assigns a static helper table pointer and returns whether the version was explicitly recognized. Translation helpers use switch statements and return failure for unsupported IDs.

## State And Persistence
No mutable state is stored. The selected helper table pointer becomes parser state in the caller.

## Dependencies And Integration Points
It depends on `ObjectID.h`, `atomfirmware.h`, BIOS parser types, and DCE helper table providers. It integrates directly with `command_table2.c` DMUB/VBIOS parameter construction.

## Risks
The default case assigns a DCE112 helper2 table but returns `false`, which can be surprising if callers use the pointer after a failed init result. Some legacy mappings are TODO-disabled, such as underlay controller and DCPLL ref-clock source. Unsupported IDs trigger debugger breaks and can return default object IDs.

## Test Signals
Runtime coverage should verify helper initialization return values for every DCN version listed in the switch. Command-table2 operations should be checked for correct controller, encoder, and clock-source encoding on DCN hardware.
