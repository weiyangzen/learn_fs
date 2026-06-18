# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn30/dcn30_optc.c

## Purpose
`dcn30_optc.c` specializes OPTC behavior for DCN3.0. It updates lock-register programming, supports expanded ODM combine up to four OPPs, extended blank-color registers, DRR trigger-window/change-limit controls, output mux selection, pending-status queries, and optional DMUB-mediated DRR min/max updates.

## Important APIs, types, and functions
Important functions are `optc3_triplebuffer_lock()`, `optc3_lock_doublebuffer_enable()`, `optc3_lock_doublebuffer_disable()`, `optc3_lock()`, `optc3_set_out_mux()`, `optc3_program_blank_color()`, `optc3_set_drr_trigger_window()`, `optc3_set_vtotal_change_limit()`, `optc3_set_dsc_config()`, `optc3_set_odm_bypass()`, `optc3_set_odm_combine()`, `optc3_get_optc_double_buffer_pending()`, `optc3_get_otg_update_pending()`, `optc3_get_pipe_update_pending()`, `optc3_wait_drr_doublebuffer_pending_clear()`, `optc3_set_vtotal_min_max()`, `optc3_tg_init()`, and `dcn30_timing_generator_init()`.

## Control flow
DCN30 locks select the OTG instance through `OTG_GLOBAL_CONTROL2`, program keepout, and trace lock state. Double-buffer locking computes start/end X/Y windows from current blank starts and fixed offsets, programs DIG update location, enables global update lock, and sets vupdate keepout. ODM bypass clears segments 1-3 and sets H timing division with `OTG_H_TIMING_DIV_MODE`. ODM combine accepts two or four OPPs, computes memory masks, programs segment selectors, segment width, and timing division as `opp_cnt - 1`. DRR min/max writes can be redirected through `dc_dmub_srv_drr_update_cmd()` when DMUB mclk switching is active and FAMS is enabled.

## State and persistence behavior
State is volatile register state plus `optc1->opp_count`. DMUB-mediated DRR updates also depend on runtime DC capability/debug state, but no persistent storage is used.

## Dependencies and integration points
The file depends on DCN10 and DCN20 helpers, `dcn30_optc.h`, `dc_dmub_srv`, DML/DCN30 headers, tracing, ODM/DSC/DRR interfaces, and DC debug/capability flags. It integrates with wide-display ODM, DMUB refresh-rate control, update-lock sequencing, DSC, CRC, and diagnostics.

## Risks and edge cases
Fixed lock-window offsets assume sufficient blanking; small blank intervals can underflow the programmed coordinates. Four-OPP combine memory masks are derived from OPP ids and must avoid overlap. DMUB DRR update behavior diverges from direct register writes, so debug flags change hardware programming path. `triplebuffer_unlock` reuses the DCN20 implementation while lock is DCN30-specific.

## Test signals
Two- and four-way ODM combine, ODM bypass with 4:2:0/DSC 4:2:2 native formats, lock/double-buffer update timing, blank color with extended high bits, DMUB and non-DMUB DRR paths, pending-status readback, DSC config, and output mux tests are important.
