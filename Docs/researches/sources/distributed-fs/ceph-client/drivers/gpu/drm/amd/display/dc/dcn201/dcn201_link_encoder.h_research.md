# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_link_encoder.h

## Purpose
Declares the DCN201 link encoder constructor and extends DPCS register/mask lists for DCN201 PHY and DP alt-mode fields.

## Important APIs, Types, And Functions
`DPCS_DCN201_MASK_SH_LIST` extends common DPCS masks with raw-lane override, DP alt-disable/DP4, per-lane pstate/MPLL, lane width/rate, and ref clock fields. `DPCS_DCN201_REG_LIST` extends common DCN2 DPCS registers with raw-lane indexed override registers. `dcn201_link_encoder_construct()` is the exported constructor.

## Control Flow
No executable flow. Register macros are expanded by resource code and consumed by the `.c` implementation and inherited helpers.

## State And Persistence
No state in the header. The register lists describe hardware state relevant to link PHY programming.

## Dependencies And Integration Points
Includes `dcn20/dcn20_link_encoder.h` and reuses DPCS/DCN2 link encoder macro infrastructure. Used by DCN201 resource code.

## Risks
The register/mask list must stay aligned with both DCN201 ASIC headers and inherited DCN20 helper expectations. Incorrect DP alt-mode fields can cause bad USB-C link-cap reporting.

## Test Signals
Compile coverage of macro expansion, DP-alt-mode detection, lane-cap reporting, and link training with DCN201 registers.
