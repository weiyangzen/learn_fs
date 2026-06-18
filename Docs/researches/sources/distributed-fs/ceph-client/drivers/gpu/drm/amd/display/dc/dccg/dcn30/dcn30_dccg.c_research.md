# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn30/dcn30_dccg.c

## Purpose
`dcn30_dccg.c` implements DCN 3.0 DCCG object creation. Functionally it reuses the DCN2 DCCG behavior while enabling DCN3 register table extensions through the constructor inputs.

## Important APIs And Functions
`dccg3_funcs` maps all operations to DCN2 implementations: DPP DTO update, refclk frequency, FIFO override, OTG add/drop, init, refclk setup, clock gating, memory low power, and S0i3 marker check. `dccg3_create` and `dccg30_create` both allocate `struct dcn_dccg`, initialize base context/function table, and store register/shift/mask pointers.

## Control Flow And State
Creation is allocation plus table/function pointer setup. Runtime behavior is inherited through the function table. There is no DCN3-specific register programming in this file beyond accepting DCN3 register tables.

## Dependencies And Integration Points
It includes `reg_helper.h`, `core_types.h`, and `dcn30_dccg.h`. It integrates with DCN3 resource construction and DCCG register definitions for HDMI character clock and PHY symbol clocks.

## Risks
Using DCN2 functions on DCN3 assumes the register-table macros map all accessed fields compatibly. Separate `dccg3_create` and `dccg30_create` are equivalent, so callers must not infer behavior differences from the names. Allocation failure must be handled by resource construction.

## Test Signals
DCN3 display bring-up, DPP DTO programming, HDMI/DP clock behavior, clock gating, memory low power, and constructor coverage for both create names are expected signals.
