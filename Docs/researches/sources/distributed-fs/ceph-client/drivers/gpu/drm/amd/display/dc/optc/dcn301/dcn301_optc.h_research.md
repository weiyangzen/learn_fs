# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn301/dcn301_optc.h

## Purpose
`dcn301_optc.h` declares the DCN3.0.1 timing-generator initialization and the two DCN301-specific helper functions for manual trigger setup and DRR programming.

## Important APIs, types, and functions
The public prototypes are `dcn301_timing_generator_init()`, `optc301_setup_manual_trigger()`, and `optc301_set_drr()`.

## Control flow
There is no executable flow. The header exposes DCN301 overrides while including both DCN20 and DCN30 OPTC contracts.

## State and persistence behavior
No state is defined. Runtime state is controlled by the implementation through hardware registers.

## Dependencies and integration points
It includes `dcn20/dcn20_optc.h` and `dcn30/dcn30_optc.h`, making DCN301 a small specialization of the DCN30 function set with DCN20 helper compatibility.

## Risks and edge cases
The header intentionally adds no new register-list macros. Any DCN301-specific register differences must be handled by the included DCN30/DCN20 metadata or resource tables.

## Test signals
Compile coverage and runtime tests of the DCN301 DRR/manual-trigger overrides validate this header.
