# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn21/Makefile

## Purpose
Adds the DCN2.1 link encoder object to the AMD display build.

## Important APIs, Types, And Functions
Defines `DCN21 = dcn21_link_encoder.o`, expands it to `AMD_DAL_DCN21`, and appends to `AMD_DISPLAY_FILES`.

## Control Flow
Build-time object-list expansion only.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Connects the DCN2.1 link encoder implementation to the parent display build.

## Risks
If omitted, DCN2.1 resource construction will miss the link encoder constructor and function-table implementation.

## Test Signals
Build coverage for DCN2.1 ASIC configs and link-time resolution of `dcn21_link_encoder_construct`.
