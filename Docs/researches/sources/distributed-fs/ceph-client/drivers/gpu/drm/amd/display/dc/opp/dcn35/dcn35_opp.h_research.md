# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn35/dcn35_opp.h

## Purpose
`dcn35_opp.h` declares the DCN3.5 OPP register extension over DCN20, adding top clock-control and ABM-control registers plus the fine-grain clock-gating field.

## Important APIs, types, and functions
Key macros are `OPP_REG_VARIABLE_LIST_DCN3_5`, `OPP_MASK_SH_LIST_DCN35()`, and `OPP_DCN35_REG_FIELD_LIST()`. Types are `struct dcn35_opp_registers`, `struct dcn35_opp_shift`, and `struct dcn35_opp_mask`. Prototypes expose `dcn35_opp_construct()`, `dcn35_opp_set_fgcg()`, and `dcn35_opp_read_reg_state()`.

## Control flow
The header has no executable control flow. It defines a layout compatible with DCN20 plus DCN35 additions, enabling the C file to delegate most behavior to DCN20.

## State and persistence behavior
Runtime state is stored in OPP hardware registers. The header itself only describes register addresses and field masks.

## Dependencies and integration points
It includes `dcn20/dcn20_opp.h` and integrates with DCN35 resource construction, clock-gating policy, ABM diagnostics, and the common OPP function interface.

## Risks and edge cases
The anonymous struct in `OPP_DCN35_REG_FIELD_LIST()` must remain compatible with how the implementation casts to DCN20 metadata. Missing DCN35-specific mask fields would make FGC G programming a no-op or corrupt another field.

## Test signals
Compile coverage, DCN35 register-table initialization, FGC G toggling, and OPP readback validation are sufficient signals.
