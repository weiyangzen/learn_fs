# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_opp.c

## Purpose
Constructs the DCN201 output pixel processor and assigns an OPP function table largely inherited from OPP1/OPP2 helpers.

## Important APIs, Types, And Functions
`dcn201_opp_funcs` maps dynamic expansion, format programming, bit-depth reduction, stereo, pipe clock control, display pattern generator, DPG dimensions/status, blank color, left-edge extra pixel, and destroy operations to inherited functions. `dcn201_opp_construct()` initializes context, instance, function table, register map, shift map, and mask map.

## Control Flow
Construction is straight-line assignment. Runtime operations are handled by the inherited function pointers rather than local logic.

## State And Persistence
Software state is the initialized `dcn201_opp` object. Runtime hardware state is programmed by inherited OPP helpers using the stored register descriptors.

## Dependencies And Integration Points
Depends on `dm_services`, `dcn201_opp.h`, `reg_helper`, and inherited DCN10/DCN20 OPP helpers. Integrated by DCN201 resource construction for pipe output processing.

## Risks
Because all behavior delegates to inherited functions, register-list compatibility is critical. Any DCN201 hardware difference not represented by the register/mask maps can produce incorrect formatting or DPG behavior.

## Test Signals
Mode-set output formatting, bit-depth reduction, stereo, DPG pattern generation, blanking, and left-edge extra-pixel tests on DCN201 are relevant.
