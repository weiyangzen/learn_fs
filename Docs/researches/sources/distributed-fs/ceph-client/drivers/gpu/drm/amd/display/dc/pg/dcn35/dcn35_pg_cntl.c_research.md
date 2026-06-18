# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/pg/dcn35/dcn35_pg_cntl.c

## Purpose
Implements the DCN35 power-gating controller. It controls PG domains for DSC, HUBP/DPP, HPO, IO clocks, plane/OTG aggregate resources, and DWB bookkeeping, while maintaining software-visible power state arrays in `struct pg_cntl`.

## Important APIs, Types, and Functions
Public functions include per-domain controls (`pg_cntl35_dsc_pg_control()`, `pg_cntl35_hubp_dpp_pg_control()`, `pg_cntl35_hpo_pg_control()`, `pg_cntl35_io_clk_pg_control()`, `pg_cntl35_plane_otg_pg_control()`, `pg_cntl35_mpcc_pg_control()`, `pg_cntl35_opp_pg_control()`, `pg_cntl35_optc_pg_control()`, `pg_cntl35_dwb_pg_control()`), `pg_cntl35_init_pg_status()`, `pg_cntl35_create()`, and `dcn_pg_cntl_destroy()`. Static helpers read domain status and print debug summaries.

## Control Flow and State
Each hardware PG control computes `DOMAIN_POWER_GATE` from `power_on`, checks debug flags and `idle_optimizations_allowed`, reads current `DOMAIN_PGFSM_PWR_STATUS`, avoids redundant transitions, enables `DC_IP_REQUEST_CNTL.IP_REQUEST_EN` if needed, writes the domain config, and polls for target status. DSC uses domains 16-19; HUBP/DPP use domains 0-3; IO clock uses domain 22; memory status uses domain 23; plane/OTG aggregate uses domain 24; HPO uses domain 25. Plane/OTG power-down only proceeds when MPCC, OPP, OPTC, stream, and DWB state indicate all related resources are disabled. Software state is cached in `pg_pipe_res_enable` and `pg_res_enable`.

## Dependencies and Integration Points
Includes `reg_helper.h`, `core_types.h`, `dcn35_pg_cntl.h`, and `dccg.h`. The `pg_cntl35_funcs` vtable is consumed by higher-level DC power management. It relies on `dc->debug` flags, `dc->res_pool->pipe_count`, and `dc->current_state` stream mappings.

## Risks and Test Signals
Risks include stale cached state blocking power-down, domain-number mismatches, skipped power-on when debug flags are intended only for power-down, and polling timeouts. Tests should exercise each domain, debug disable flags, idle optimization gating, all-pipe-off aggregate PG, and status initialization after boot/resume.
