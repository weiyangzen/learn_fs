# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn302/dcn302_dccg.h

## Purpose
`dcn302_dccg.h` defines DCN 3.0.2 DCCG register and mask/shift macros as a small extension of the common DCN base list.

## Important APIs And Macros
`DCCG_REG_LIST_DCN3_02` expands the common DCN base registers and adds `DPPCLK4_DTO_PARAM`. `DCCG_MASK_SH_LIST_DCN3_02` expands common base fields and adds DPP4 DTO enable and DB enable fields.

## Control Flow And State
The header is declarative; concrete resource files use the macros to build DCCG register tables.

## Dependencies And Integration Points
It includes `dcn30/dcn30_dccg.h`, inheriting DCN3/DCN2 DCCG declarations and register macro infrastructure. It integrates with DCN302 resource creation.

## Risks
This header declares no constructor of its own, so DCN302 likely uses a shared DCN3 constructor. The list supports DPP4 in addition to the four common base DPP DTOs but does not add full six-pipe DCN2 fields. Resource code must match pipe count and call paths.

## Test Signals
Compile coverage for DCN302 resources, DPP4 DTO programming, and normal DCCG init/refclk/gating paths are important.
