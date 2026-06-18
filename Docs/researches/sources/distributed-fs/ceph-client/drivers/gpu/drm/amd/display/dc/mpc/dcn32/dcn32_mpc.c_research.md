# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.c

## Purpose
This file implements the DCN3.2 MPC variant. It keeps DCN3 plane, DWB, CSC, denorm, OGAM, and gamut-remap behavior, but moves shaper and 3D LUT programming from shared RMU units into per-MPCC movable color-management (`MPCC_MCM`) blocks and adds a post-blend 1D LUT programming path.

## Important APIs, types, and functions
Key functions include `mpc32_mpc_init`, `mpc32_power_on_blnd_lut`, `mpc32_program_post1dlut`, `mpc32_program_shaper`, `mpc32_program_3dlut`, all supporting RAM A/B settings and PWL data writers, `mpc32_set_3dlut_mode`, and `dcn32_mpc_construct`. The `dcn32_mpc_funcs` table points generic MPC operations to inherited DCN1/DCN2/DCN3 helpers while overriding `program_shaper`, `program_3dlut`, and `program_1dlut`.

## Control flow and state
Initialization calls `mpc3_mpc_init` and configures MCM and OGAM memory low-power mode when debug flags allow it. Post-1D LUT programming selects the inactive bank, powers memory, writes transfer-function region registers and PWL entries, appends a final base value, then enables mode 2 and selects RAM A or B. Shaper programming is similar but targets `MPCC_MCM_SHAPER_*` registers. 3D LUT programming chooses the inactive 3D LUT RAM bank, writes four tetrahedral RAM sections using write masks, programs the LUT size, and may power memory back down.

## Dependencies and integration points
Dependencies include DCN30 headers and color helpers, conversion utilities, register helpers, and inherited MPC functions. The implementation is used through the generic MPC interface and is also reused by DCN401 for the low-level MCM memory-population routines.

## State and persistence behavior
DCN3.2 removes RMU acquisition/release from the function table because MCM state is per MPCC. Runtime state is in MPCC_MCM mode, select, memory power, LUT index/data, and movable location registers, plus software MPCC structures initialized with `mpc3_init_mpcc`. There is no persistent storage beyond hardware state across modesets or driver lifetime.

## Risks
The shaper settings guard region programming with `if (curve)`, but still assumes valid corner points and LUT data arrays. 12-bit 3D LUT programming reads pairs, so odd entry counts would be unsafe. Power-on helpers break into the debugger on memory state failures but do not return errors. `mpc32_set_3dlut_mode` hardcodes movable CM location to pre-blend and has a TODO for true movable support.

## Test signals
Useful validation includes post-1D LUT enable/disable with both banks, shaper and 3D LUT programming while toggling memory low-power flags, visual color transform correctness for 9-cube and 17-cube LUTs, no corruption when programming multiple MPCCs independently, and function-table checks confirming RMU callbacks are intentionally `NULL`.
