# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn30/dcn30_init.c

## Purpose
Installs DCN 3.0 HWSS dispatch tables, adding DCN30 color, init, infoframe, AV mute, writeback, DMData, MALL, hardware release, pattern generation, bandwidth, pending-update, and underflow-debug hooks on top of DCN20/DCN21 behavior.

## Important APIs, Types, and Functions
Exports `dcn30_hw_sequencer_construct(struct dc *dc)`. Public table additions include `program_gamut_remap = dcn30_program_gamut_remap`, `init_hw = dcn30_init_hw`, `update_info_frame = dcn30_update_info_frame`, `disable_pixel_data = dcn20_disable_pixel_data`, `prepare_bandwidth = dcn30_prepare_bandwidth`, `set_avmute = dcn30_set_avmute`, writeback hooks, `program_dmdata_engine = dcn30_program_dmdata_engine`, `apply_idle_power_optimizations`, `does_plane_fit_in_mall`, `hardware_release`, `wait_for_all_pending_updates`, and `get_underflow_debug_data`. Private additions include DCN30 input/output transfer functions, `program_all_writeback_pipes_in_tree`, and `set_blend_lut`.

## Control Flow
Construction copies static tables into `dc` and `dc->hwseq`. Runtime flow comes from indirect calls through those tables.

## State and Persistence Behavior
Persists DCN30 function selection. No additional local state.

## Dependencies and Integration Points
Includes DCE110, DCN10, DCN20, DCN21, and DCN30 HWSEQ headers. It is a base constructor reused directly by DCN302 and DCN303 before they patch power-gating hooks.

## Risks and Test Signals
Risks include missing `power_down_on_boot` compared with earlier generations and broad changes to writeback, color, and MALL behavior. Test with full DCN30 boot/modeset, color, writeback, MALL, DP/HDMI metadata, and power management.
