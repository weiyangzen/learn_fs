# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_opp.h

## Purpose
Defines the DCN3 OPP register-list macro for resource code that needs DCN30 output pixel processor registers.

## Important APIs, Types, And Functions
`OPP_REG_LIST_DCN30(id)` combines DCN10 OPP registers, DPG registers, and `FMT_422_CONTROL`, matching the DCN201-style OPP register set for DCN3.

## Control Flow
No executable flow.

## State And Persistence
No software state. The macro describes hardware register addresses to be stored in generated OPP register descriptor structures elsewhere.

## Dependencies And Integration Points
Includes `dcn20/dcn20_opp.h` for inherited OPP register macros. Used by DCN30 resource construction or OPP implementation code outside this subset.

## Risks
The header only provides a register list and no constructor or type definitions, so consumers must combine it with inherited DCN20 OPP structures. Any DCN30-specific OPP fields beyond this list must be added elsewhere.

## Test Signals
Compile-time macro expansion in DCN30 resource code and runtime OPP format/DPG/FMT_422 register readback.
