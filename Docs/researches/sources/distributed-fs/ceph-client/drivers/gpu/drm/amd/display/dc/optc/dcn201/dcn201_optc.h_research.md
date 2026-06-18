# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn201/dcn201_optc.h

## Purpose
`dcn201_optc.h` declares the DCN2.0.1 OPTC register list and mask/shift additions. It is a smaller DCN20-derived contract for hardware that exposes selected global-control, GSL, vupdate keepout, DSC, ODM, width, and DWB source fields.

## Important APIs, types, and functions
Key macros are `TG_COMMON_REG_LIST_DCN201()` and `TG_COMMON_MASK_SH_LIST_DCN201()`. The only prototype is `dcn201_timing_generator_init()`.

## Control flow
The header has no executable flow. It supplies register metadata for `dcn201_optc.c`.

## State and persistence behavior
Only volatile register metadata is described; no persistent state is defined.

## Dependencies and integration points
It includes `dcn20/dcn20_optc.h` and integrates with DCN201 timing-generator construction and shared DCN10/DCN20 helper code.

## Risks and edge cases
The mask list repeats `OPTC_DWB1_SOURCE_SELECT` and omits some DCN20 fields such as `OPTC_NUM_OF_INPUT_SEGMENT`, matching the reduced implementation. Callers must not assume full DCN20 ODM source readback.

## Test signals
Compile coverage, DCN201 register-table initialization, DSC/width programming, DWB source references, and triplebuffer behavior validate the header.
