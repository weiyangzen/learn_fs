# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn401/dcn401_mpc.c

## Purpose
This file implements the DCN4.01 MPC function table and newer color-management controls. It reuses DCN32 MCM LUT writers, adds generic LUT populate/mode/read-write-control callbacks, adds movable color-management location selection, supports 3D LUT fast-load status/select, and expands gamut remap to OGAM plus first and second MCM gamut-remap blocks.

## Important APIs, types, and functions
Important functions are `mpc401_update_3dlut_fast_load_select`, `mpc401_get_3dlut_fast_load_status`, `mpc401_set_movable_cm_location`, `mpc401_populate_lut`, `mpc401_program_lut_mode`, `mpc401_program_lut_read_write_control`, `mpc_program_gamut_remap`, `mpc_read_gamut_remap`, `mpc401_set_gamut_remap`, `mpc401_get_gamut_remap`, `mpc401_get_lut_mode`, and `dcn401_mpc_construct`. The `dcn401_mpc_funcs` table adds the new generic LUT and fast-load callbacks while retaining DCN32 shaper, 3D LUT, and 1D LUT operations.

## Control flow and state
`mpc401_populate_lut` separates memory population from mode selection. For 1D and shaper LUTs it powers/configures the target RAM bank and delegates to DCN32 helpers; for 3D LUT it writes the four tetrahedral RAM partitions without selecting the active mode. `mpc401_program_lut_mode` enables or disables one MCM LUT class and switches RAM bank or size. `mpc401_program_lut_read_write_control` prepares the selected bank and bit depth for host writes. Gamut remap programming chooses the relevant block, writes coefficient set A or B, then updates that block's mode selector.

## Dependencies and integration points
The file depends on `dcn401_mpc.h`, `mpc.h`, conversion helpers, DCN10 color matrix helpers, and DCN32 LUT helper routines. It integrates with newer display color-management code through generic `populate_lut`, `program_lut_mode`, `program_lut_read_write_control`, and `get_lut_mode` callbacks rather than only the legacy `program_3dlut` style.

## State and persistence behavior
Software state is initialized in `struct dcn401_mpc` and MPCC arrays. Hardware state includes MCM LUT mode/current fields, bank selects, 3D LUT size, fast-load select/status, movable location, OGAM gamut remap, and two MCM gamut remap blocks. State is volatile and coordinated by double-buffered A/B coefficient and LUT banks.

## Risks
The 3D LUT populate path assumes that read/write control and bank selection have been prepared by the caller; wrong sequencing can write the wrong bank. Fast-load status exposes underflow flags but does not itself recover. `mpc401_cm_lut_size_to_3dlut_size` asserts on unsupported sizes. Gamut remap switch statements initialize only fields relevant to supported mode selections, so invalid enum values can lead to no-op programming with limited diagnostics.

## Test signals
Useful tests include generic LUT populate followed by explicit mode switch, `get_lut_mode` readback for shaper/1D/3D LUTs, fast-load select and done/underflow status reads, movable CM before/after selection, gamut remap set/get for all three block IDs, and regression checks that DCN32 inherited programming still works through the DCN4.01 function table.
