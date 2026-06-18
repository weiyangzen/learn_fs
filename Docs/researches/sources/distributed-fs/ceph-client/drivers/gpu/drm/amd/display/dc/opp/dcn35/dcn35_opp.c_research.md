# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn35/dcn35_opp.c

## Purpose
`dcn35_opp.c` is a thin DCN3.5 OPP specialization. It reuses DCN20 construction and behavior while adding fine-grain clock-gating control and expanded register-state readback for ABM.

## Important APIs, types, and functions
The exported functions are `dcn35_opp_construct()`, `dcn35_opp_set_fgcg()`, and `dcn35_opp_read_reg_state()`. The file casts DCN35 register/shift/mask structures to DCN20-compatible structures for construction, then uses DCN35-specific register access macros for the additional fields.

## Control flow
Construction delegates directly to `dcn20_opp_construct()`. Fine-grain clock gating writes `OPP_FGCG_REP_DIS` in `OPP_TOP_CLK_CONTROL` with the inverse of the requested enable flag. Register-state readback reads DPG, FMT, ABM, pipe control, pipe CRC, OPPBUF, and DSC forward configuration.

## State and persistence behavior
No durable state is introduced. The extra state is hardware register state in `OPP_TOP_CLK_CONTROL` and `OPP_ABM_CONTROL`.

## Dependencies and integration points
The file depends on `dcn35_opp.h`, DCN20 OPP layout compatibility, `reg_helper`, and `struct dcn_opp_reg_state`. It integrates with power-management/clock-gating code and diagnostics that inspect ABM and OPP state.

## Risks and edge cases
The construction cast assumes DCN35 register, shift, and mask layouts begin with the DCN20 fields in the same order. Misuse of `enable` in `dcn35_opp_set_fgcg()` would invert clock-gating behavior. Readback assumes all registers are valid for the DCN35 instance.

## Test signals
DCN35 build and boot, FGC G enable/disable register checks, display mode-set with inherited DCN20 paths, ABM state readback, and power-gating regression tests are the main validation signals.
