# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce112/command_table_helper2_dce112.c

## Purpose
This file defines the firmware-parser helper vtable used for DCE11.2, DCE12, and DCN versions in `command_table_helper2.c`.

## Important APIs, Types, And Functions
- `dal_cmd_tbl_helper_dce112_get_table2()` returns the static helper table.
- Static mappings cover signal type to DIG mode, HPD selection, DIG encoder selection, combo PHY/display PLL IDs, encoder actions, display power-gating actions, DCE clock types, and transmitter color-depth ratios.
- The table uses `dal_cmd_table_helper_controller_id_to_atom2()`, `dal_cmd_table_helper_encoder_id_to_atom2()`, and `dal_cmd_table_helper_encoder_mode_bp_to_atom2()`.

## Control Flow
All mappings are switch-based. Combo PHY PLL IDs map to `ATOM_COMBOPHY_PLL*`, DFS maps to `ATOM_GCK_DFS`, and VCE/DP DTO map to `ATOM_DP_DTO`. DIG encoder selection returns zero because front-end selection is programmed elsewhere.

## State And Persistence
The file has no mutable state; it exposes an immutable helper table.

## Dependencies And Integration Points
It depends on `atom.h`, BIOS parser types, both legacy and firmware helper headers, and is selected by the firmware helper initializer for DCE11.2+ and DCN.

## Risks
Unsupported clock source IDs return failure, which can cause command-table operations to return `BADINPUT`. The helper lacks `assign_control_parameter` and ref-clock callbacks, so legacy paths must not use this table. Unknown color depths assert and return zero.

## Test Signals
Test by executing firmware command-table operations that require combo PHY PLLs, DP DTO, HDMI deep-color ratios, and DP MST signal modes on DCN hardware.
