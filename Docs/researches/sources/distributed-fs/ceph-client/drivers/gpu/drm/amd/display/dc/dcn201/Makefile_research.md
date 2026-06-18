# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/Makefile

## Purpose
Adds DCN2.0.1 MPC, OPP, and link encoder objects to the AMD display build.

## Important APIs, Types, And Functions
Defines `DCN201 = dcn201_mpc.o dcn201_opp.o dcn201_link_encoder.o`, creates `AMD_DAL_DCN201`, and appends it to `AMD_DISPLAY_FILES`.

## Control Flow
Build-time object-list expansion only.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Integrates the DCN201-specific compositor, output pixel processor, and link encoder implementations into the parent display build.

## Risks
Missing any of these objects causes resource construction or function-table symbol failures for DCN201 ASICs. The directory is small and reuses DCN20 code heavily, so build-list mistakes may not be obvious until hardware-specific configs are built.

## Test Signals
Kernel/module build for DCN201 targets should include all three objects and resolve their constructors.
