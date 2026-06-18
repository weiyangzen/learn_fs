# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn201/dcn201_dccg.h

## Purpose
`dcn201_dccg.h` declares the DCN 2.0.1 DCCG create function.

## Important APIs
`dccg201_create` takes a `dc_context` and generation-specific register, shift, and mask tables and returns a `struct dccg *`.

## Control Flow And State
There is no implementation in the header. It inherits the shared `struct dcn_dccg` shape from `dcn20_dccg.h`.

## Dependencies And Integration Points
It includes `dcn20/dcn20_dccg.h`. DCN201 resource construction code uses this declaration to instantiate the generation-specific DCCG.

## Risks
The header exposes only construction; destruction uses the shared `dcn_dccg_destroy`. Correct table selection is external.

## Test Signals
Compile/link coverage for DCN201 resources and constructor invocation are the main signals.
