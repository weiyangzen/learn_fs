# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn31/dcn31_init.c

## Purpose
Installs DCN31 HWSS tables. It inherits broad DCN30/DCN21/DCN20 behavior but replaces init, system context, infoframes, reset, power gating, Z10, static-screen control, HPO setup, and underflow debug integration for DCN31.

## Important APIs, Types, and Functions
Exports `dcn31_hw_sequencer_construct(struct dc *dc)`. Public table key entries include `init_hw = dcn31_init_hw`, `update_info_frame = dcn31_update_info_frame`, `set_static_screen_control = dcn31_set_static_screen_control`, `init_sys_ctx = dcn31_init_sys_ctx`, `z10_restore`, `z10_save_init`, `setup_hpo_hw_control`, and `get_underflow_debug_data = dcn30_get_underflow_debug_data`. Private table key entries include `reset_hw_ctx_wrap = dcn31_reset_hw_ctx_wrap`, `enable_power_gating_plane = dcn31_enable_power_gating_plane`, `hubp_pg_control = dcn31_hubp_pg_control`, `dsc_pg_control = dcn31_dsc_pg_control`, and `setup_hpo_hw_control`.

## Control Flow
Constructor assigns static public and private tables. Runtime flow is fully indirect through the table.

## State and Persistence Behavior
Persists DCN31 table selection. No file-local state.

## Dependencies and Integration Points
Includes DCE110, DCN10, DCN20, DCN21, DCN30, DCN301, and DCN31 HWSEQ headers. Used by DCN31 ASIC initialization and as a base for DCN314 behavior.

## Risks and Test Signals
Risks come from mixing DCN31 init/reset with older DCN20 bandwidth and DCN30 color/writeback. Test mode-set, HPO/DP2, Z10, power gating, static screen, writeback, ABM/backlight, and underflow debug on DCN31.
