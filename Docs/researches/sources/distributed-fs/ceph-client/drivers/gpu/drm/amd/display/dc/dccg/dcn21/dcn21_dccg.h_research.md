# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn21/dcn21_dccg.h

## Purpose
`dcn21_dccg.h` declares the DCN 2.1 DCCG create function.

## Important APIs
`dccg21_create` accepts a context and register/shift/mask tables and returns a `struct dccg *`.

## Control Flow And State
The header has no logic. The concrete implementation uses the shared DCN2 object layout and DCN21-specific function table.

## Dependencies And Integration Points
It relies on forward-visible `struct dccg`, `struct dc_context`, `struct dccg_registers`, `struct dccg_shift`, and `struct dccg_mask` definitions from included resource context. DCN21 resource creation is the integration point.

## Risks
Because the header does not include `dcn20_dccg.h` directly, include order must provide the DCCG table struct declarations before use.

## Test Signals
Compile/link coverage for DCN21 resources and constructor use are the main signals.
