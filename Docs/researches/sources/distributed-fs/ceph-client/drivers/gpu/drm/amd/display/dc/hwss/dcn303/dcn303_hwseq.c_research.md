# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn303/dcn303_hwseq.c

## Purpose
Provides no-op DCN303 power-gating hooks because DCN303 removes the PG registers used by related generations.

## Important APIs, Types, and Functions
Exports `dcn303_dpp_pg_control`, `dcn303_hubp_pg_control`, `dcn303_dsc_pg_control`, and `dcn303_enable_power_gating_plane`. All parameters are explicitly cast to void.

## Control Flow
Each function immediately returns after void-casting arguments and documenting that PG registers are removed.

## State and Persistence Behavior
No software or hardware state is changed.

## Dependencies and Integration Points
Patched into inherited DCN30 tables by `dcn303_init.c`. This prevents generic DCN30/DCN20 PG code from touching nonexistent registers.

## Risks and Test Signals
Risk is power leakage or missing required power transitions if a future DCN303 revision reintroduces PG controls. Test signal is stable boot/modeset/suspend without register access faults when PG hooks are invoked.
