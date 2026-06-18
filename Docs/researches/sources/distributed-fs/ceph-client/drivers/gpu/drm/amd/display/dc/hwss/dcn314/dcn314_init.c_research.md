# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn314/dcn314_init.c

## Purpose
Installs DCN314 HWSS tables. It builds on DCN31 init/reset/HPO/Z10 behavior and DCN30 color/writeback behavior, while adding DCN314 link disable, pixel-rate divider calculation, ODM, DSC/plane/DPP PG, DPP root-clock, DCCG K1/K2, and FIFO resync hooks.

## Important APIs, Types, and Functions
Exports `dcn314_hw_sequencer_construct(struct dc *dc)`. Public table additions include `disable_link_output = dcn314_disable_link_output` and `calculate_pix_rate_divider = dcn314_calculate_pix_rate_divider`; it keeps `init_hw = dcn31_init_hw`, `update_info_frame = dcn31_update_info_frame`, `init_sys_ctx = dcn31_init_sys_ctx`, Z10, HPO, DCN30 writeback/color, and DCN21 backlight/power hooks. Private table additions include `enable_power_gating_plane = dcn314_enable_power_gating_plane`, `dpp_root_clock_control`, `dpp_pg_control`, `update_odm`, `dsc_pg_control`, `calculate_dccg_k1_k2_values`, and `resync_fifo_dccg_dio`.

## Control Flow
Constructor assigns static public/private tables. Later mode-set and link paths call through these hooks to get DCN314-specific clock, DSC, ODM, PG, and link-disable handling.

## State and Persistence Behavior
Persists DCN314 function table selection. No local state.

## Dependencies and Integration Points
Includes DCE110, DCN10, DCN20, DCN21, DCN30, DCN301, DCN31, and DCN314 HWSEQ headers. It is the high-level integration point for `dcn314_hwseq.c`.

## Risks and Test Signals
The table mixes multiple generations, so missed overrides can silently use older behavior. Test DCN314-specific ODM/DSC, DP2, pixel-rate divider, FIFO resync, DPP root clock, link disable, and all inherited DCN31/DCN30 paths.
