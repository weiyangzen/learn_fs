# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table_helper.c

## Purpose
This file contains shared legacy command-table helper routines that translate Display Core enums and objects into ATOMBIOS encodings, and selects the DCE-family-specific helper table.

## Important APIs, Types, And Functions
- `dal_bios_parser_init_cmd_tbl_helper()` selects DCE60, DCE80, DCE110, or DCE112 helper tables by `enum dce_version`.
- `dal_cmd_table_helper_controller_id_to_atom()`, `*_transmitter_bp_to_atom()`, `*_encoder_mode_bp_to_atom()`, `*_clock_source_id_to_ref_clk_src()`, and `*_encoder_id_to_atom()` translate common IDs.
- `dal_cmd_table_helper_assign_control_parameter()` packs legacy `DIG_ENCODER_CONTROL_PARAMETERS_V2`.
- `phy_id_to_atom()`, `clock_source_id_to_atom_phy_clk_src_id()`, and `engine_bp_to_atom()` support newer transmitter and CRTC-source command parameters.

## Control Flow
Callers initialize `bp->cmd_helper` once by DCE version. Command-table handlers then call the function pointers or these exported helpers while building ATOM parameter blocks. Translation functions usually return `bool` for mappings with out parameters, or a default ATOM value with a debugger break on invalid inputs.

## State And Persistence
The file stores no mutable state. It assigns a pointer to a static helper table owned by DCE-family helper files. Parameter-packing functions mutate caller-provided ATOM structures.

## Dependencies And Integration Points
It depends on `atom.h`, display BIOS parser types, DCE-family helper headers, and `command_table_helper_struct.h`. It is central to `command_table.c` and DCE helper variants.

## Risks
Invalid mappings may return a default value after `BREAK_TO_DEBUGGER()`, allowing firmware programming with an unintended ID if callers do not handle failure. The DCE version switch must be kept current for newly supported ASIC versions. Conditional SI support under `CONFIG_DRM_AMD_DC_SI` changes coverage for DCE6.

## Test Signals
Compile-time signals include all helper table function pointers matching `struct command_table_helper`. Runtime signals are correct controller/encoder/transmitter mapping in VBIOS command traces, no debugger breaks on supported IDs, and successful light-up across DCE versions.
