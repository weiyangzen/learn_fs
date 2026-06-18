# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn20/dcn20_opp.h

## Purpose
`dcn20_opp.h` defines DCN2.0 OPP register metadata and prototypes, extending DCN10 with DPG, FMT_422 left-edge, OPPBUF_CONTROL1, and DSC forward-state readback support.

## Important APIs, types, and functions
Important macros include `TO_DCN20_OPP()`, `OPP_DPG_REG_LIST()`, `OPP_REG_LIST_DCN20()`, `OPP_REG_VARIABLE_LIST_DCN2_0`, `OPP_DPG_MASK_SH_LIST()`, `OPP_MASK_SH_LIST_DCN20()`, and `OPP_DCN20_REG_FIELD_LIST()`. Types are `struct dcn20_opp_registers`, `struct dcn20_opp_shift`, `struct dcn20_opp_mask`, and `struct dcn20_opp`. Prototypes expose DPG programming/status, blank color, left-edge pixel programming, source count, register readback, and construction.

## Control flow
The header itself has no control flow. It expands register tables consumed by DCN20 implementation functions and by later generations such as DCN35.

## State and persistence behavior
The `dcn20_opp` object stores the base OPP, register metadata, and `is_write_to_ram_a_safe`. Display state is transient hardware register state.

## Dependencies and integration points
It includes `dcn10/dcn10_opp.h` and relies on AMD DC register macros and OPP interface types. It is the inheritance point for DCN35 OPP and an integration surface for DPG users.

## Risks and edge cases
DPG register fields must remain aligned with hardware headers. The DPG status field is double-buffer pending, not a full pattern-state audit. Derived generations must cast compatible register and mask/shift layouts.

## Test signals
Build coverage for DCN20 and DCN35, DPG pattern programming tests, FMT_422 left-edge tests, and register readback coverage validate this header.
