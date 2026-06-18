# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/pg/dcn42/dcn42_pg_cntl.c

## Purpose
Implements the DCN42 power-gating controller. It extends the DCN35 model with explicit memory and DIO domains, DCCG clock interactions, global FGC gating suppression around some power-on transitions, and DCN42-specific resource state bookkeeping.

## Important APIs, Types, and Functions
Public controls include `pg_cntl42_dsc_pg_control()`, `pg_cntl42_hubp_dpp_pg_control()`, `pg_cntl42_hpo_pg_control()`, `pg_cntl42_io_clk_pg_control()`, `pg_cntl42_plane_otg_pg_control()`, `pg_cntl42_mpcc_pg_control()`, `pg_cntl42_opp_pg_control()`, `pg_cntl42_optc_pg_control()`, `pg_cntl42_mem_pg_control()`, `pg_cntl42_dio_pg_control()`, `pg_cntl42_init_pg_status()`, `pg_cntl42_create()`, and `dcn42_pg_cntl_destroy()`.

## Control Flow and State
Control functions follow the same status-check, skip-flag, IP-request-enable, config-write, and status-poll pattern as DCN35. DSC power-on enables DSC clocks through DCCG before PG changes and disables them after power-down. DSC, HUBP/DPP, HPO, and DIO power-on temporarily disable global FGC gating when supported, then restore it. IO clock domain 22 tracks DCCG, DCOH, and DCIO; memory domain 23 tracks DCHUBBUB and DCHVM; plane/OTG domain 24 waits for all stream/MPCC/OPP/OPTC state to be off before gating; DIO domain 26 is separate from IO clock control. `pg_res_enable` and `pg_pipe_res_enable` are initialized from hardware status in `pg_cntl42_init_pg_status()`.

## Dependencies and Integration Points
Includes `reg_helper.h`, `core_types.h`, `dcn42_pg_cntl.h`, and `dccg.h`. The vtable omits a debug print hook and adds `mem_pg_control` and `dio_pg_control`. Higher-level DC power management calls these through `struct pg_cntl_funcs`.

## Risks and Test Signals
Risks include DCCG callback NULL handling, global FGC gating not being restored, mismatched software cached state, domain 26 DIO sequencing, and power-down dependency checks that are too strict or too weak. Tests should cover each domain, DSC clock enable/disable, DIO and IO clock separation, memory power gating, aggregate plane/OTG gating, debug flag bypass, and resume status reconstruction.
