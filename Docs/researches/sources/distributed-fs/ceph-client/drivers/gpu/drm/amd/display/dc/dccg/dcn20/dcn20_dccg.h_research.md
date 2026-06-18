# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn20/dcn20_dccg.h

## Purpose
`dcn20_dccg.h` defines the shared DCCG register/mask/shift table layout and DCN2 base API used by many later DCN DCCG variants.

## Important APIs, Types, And Macros
Register-list macros such as `DCCG_COMMON_REG_LIST_DCN_BASE`, `DCCG_REG_LIST_DCN2`, and mask/shift macros generate register tables for DPP DTO, refclk, dispclk change, OTG pixel rate, memory low power, and gate disable registers.

`DCCG_REG_FIELD_LIST` and generation extensions such as `DCCG3_REG_FIELD_LIST`, `DCCG31_REG_FIELD_LIST`, `DCCG314_REG_FIELD_LIST`, `DCCG32_REG_FIELD_LIST`, `DCCG35_REG_FIELD_LIST`, `DCCG401_REG_FIELD_LIST`, and `DCCG42_REG_FIELD_LIST` define a superset field table. `struct dccg_shift`, `struct dccg_mask`, and `struct dccg_registers` instantiate those field/register sets.

`struct dcn_dccg` embeds `struct dccg base` and points to register, shift, and mask tables. The header declares DCN2 functions for DPP DTO update, ref frequency, FIFO override, OTG pixel add/drop, init, refclk setup, clock gating, memory low power, S0i3 marker detection, object creation, and destruction.

## Control Flow And State
The header is declarative but drives runtime register access by shaping the tables consumed by `REG`, `FN`, and generation constructors. The superset register structure allows later generation code to share `struct dcn_dccg`.

## Dependencies And Integration Points
It includes `dccg.h` and is included by DCN201, DCN21, DCN30, DCN301, DCN302, DCN303, and other DCCG headers. Resource files provide concrete register lists and call create functions with generated tables.

## Risks
Macro-generated tables must match actual ASIC register definitions exactly. The shared superset struct can hide missing fields until runtime if a generation function accesses a zero/missing register. Array sizes use `MAX_PIPES` or fixed DPP count assumptions, so generation-specific pipe counts must align with list macros.

## Test Signals
Compile-time expansion for every DCN generation, register table sanity checks, hardware clock programming across generations, and static verification of field names against ASIC register headers are useful.
