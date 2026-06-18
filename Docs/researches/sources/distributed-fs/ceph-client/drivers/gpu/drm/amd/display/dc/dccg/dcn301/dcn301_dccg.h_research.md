# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn301/dcn301_dccg.h

## Purpose
`dcn301_dccg.h` defines the reduced DCN 3.0.1 DCCG register/mask list and declares its create function.

## Important APIs And Macros
`DCCG_REG_LIST_DCN301` includes DPP DTO control/params for DPP0-3, refclk, dispclk frequency change control, memory global power request, microsecond/millisecond time base, and two gate-disable registers. `DCCG_MASK_SH_LIST_DCN301` maps DPP DTO enable/DB fields, DTO phase/modulo, and refclk fields. `dccg301_create` is the constructor declaration.

## Control Flow And State
The macros shape generation-specific register tables consumed by the constructor and inherited DCN2 functions.

## Dependencies And Integration Points
It includes `dcn20/dcn20_dccg.h`. It integrates with DCN301 resource construction and shared DCCG helpers.

## Risks
The mask list is narrower than the register list and narrower than the inherited function table capabilities. Any call path using fields not listed for DCN301 must be avoided or backed by tables from another macro. DPP count is fixed to four in this list.

## Test Signals
Compile-time resource table construction, DPP DTO programming for four pipes, refclk init, and clock-gating/memory-low-power paths are relevant.
