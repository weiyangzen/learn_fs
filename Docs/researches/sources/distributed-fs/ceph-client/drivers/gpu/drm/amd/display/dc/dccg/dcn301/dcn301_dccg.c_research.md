# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn301/dcn301_dccg.c

## Purpose
`dcn301_dccg.c` implements the DCN 3.0.1 DCCG constructor and function table. It reuses DCN2 DCCG behavior with a reduced DCN301 register table defined in the header.

## Important APIs And Functions
`dccg301_funcs` points to DCN2 implementations for DPP DTO update, refclk frequency, FIFO override, OTG add/drop, init, refclk setup, clock gating, memory low power, and S0i3 marker detection. `dccg301_create` allocates `struct dcn_dccg`, sets context and function table, and stores register/shift/mask pointers.

## Control Flow And State
There is no custom runtime branch in this file. State is the shared DCCG object and register table pointers.

## Dependencies And Integration Points
It includes `reg_helper.h`, `core_types.h`, and `dcn301_dccg.h`. It integrates with DCN301 resource creation and common DCCG hardware sequencing.

## Risks
DCN301 header tables omit some fields used by inherited functions, notably OTG add/drop and several dispclk/memory-low-power fields depending on exact macro use. If a reused function accesses a register not present for a concrete ASIC table, `REG(...)` may be zero or invalid. Resource code must pass tables compatible with the function table actually used.

## Test Signals
DCN301 display bring-up, DPP DTO updates, init/refclk behavior, and any path calling OTG add/drop or memory low-power should be validated on hardware or register mocks.
