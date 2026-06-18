# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn20/dcn20_mpc.h

## Purpose
This header defines the DCN2.0 Multiple Plane Compositor register interface and public helper surface. It extends the DCN1 MPC base with MPCC blend gain, output gamma, output CSC, denormalization, and MPCC OGAM memory power control registers. The file is mostly macro infrastructure that feeds generated register, shift, and mask tables for ASIC-specific compilation units.

## Important APIs, types, and functions
The main type is `struct dcn20_mpc`, which embeds `struct mpc` and stores `mpcc_in_use_mask`, `num_mpcc`, and pointers to DCN2 register, shift, and mask tables. `struct dcn20_mpc_registers`, `struct dcn20_mpc_shift`, and `struct dcn20_mpc_mask` are produced from `MPC_REG_VARIABLE_LIST_DCN2_0` and `MPC_REG_FIELD_LIST_DCN2_0`. Public entry points include `dcn20_mpc_construct`, `mpc2_update_blending`, `mpc2_set_denorm`, `mpc2_set_denorm_clamp`, `mpc2_set_output_csc`, `mpc2_set_ocsc_default`, `mpc2_set_output_gamma`, `mpc2_assert_idle_mpcc`, `mpc2_assert_mpcc_idle_before_connect`, and `mpc20_power_on_ogam_lut`.

## Control flow and state
The header does not implement control flow itself; it declares operations used by DCN2 and inherited by later generations. The macros enumerate per-MPCC registers for OGAM RAM A/B region metadata, LUT index/data writes, blend gains, memory power, and per-OPP CSC/denorm controls. Runtime state is split between software bookkeeping in `struct dcn20_mpc` and hardware state in indexed MPC/MPCC/OGAM registers. There is no disk persistence; state survives only as driver memory plus programmed hardware registers.

## Dependencies and integration points
The file depends on `dcn10/dcn10_mpc.h`, AMD DC register helper conventions (`SRII`, `SR`, `SF`), `MAX_MPCC`, `MAX_OPP`, and common color-management types such as `pwl_params`, `mpc_denorm_clamp`, and `mpc_output_csc_mode`. It is an integration layer for display core resource construction and for later DCN30/DCN32/DCN401 headers that reuse or extend DCN2 field lists.

## Risks
The macro lists must match hardware register naming exactly; missing or misordered fields silently corrupt generated register tables. OGAM LUT programming is banked, so mismatched A/B register groups can update the inactive or wrong RAM. Power control fields must be valid before LUT writes or gamma programming can fail on powered-down memory. Bounds are implied by callers and array sizes, so invalid MPCC or OPP indices are a high-impact risk.

## Test signals
Useful signals are successful DC bring-up, no register access faults during `dcn20_mpc_construct`, correct blend gain changes, color-depth denorm behavior across 6/8/10/12 bpc modes, default and coefficient CSC programming, output gamma enable/disable, and debug/assert coverage for MPCC idle transitions before connect/disconnect.
