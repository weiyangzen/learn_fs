# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn301/dcn301_init.c

## Purpose
Installs DCN 3.0.1 HWSS tables. It is a custom table largely based on DCN30 but uses `dcn10_init_hw`, retains `dcn10_power_down_on_boot`, and keeps bandwidth hooks closer to DCN20 while importing DCN30 color/writeback/metadata helpers and DCN21 optimized power hooks.

## Important APIs, Types, and Functions
Exports `dcn301_hw_sequencer_construct(struct dc *dc)`. Public table uses `dcn30_program_gamut_remap`, `dcn30_update_info_frame`, `dcn30_set_avmute`, DCN30 writeback and DMData engine, DCN21 backlight/power hooks, and `dcn30_wait_for_all_pending_updates`. Private table uses DCN30 input/output transfer and blend LUT, plus DCN30 writeback tree programming, while using DCN20 power gating and DSC/ODM hooks.

## Control Flow
Constructor assigns static tables. No runtime branches inside this file.

## State and Persistence Behavior
Persists function table selection. No independent state.

## Dependencies and Integration Points
Depends on DCE110, DCN10, DCN20, DCN21, DCN30, and placeholder DCN301 headers. Integrates inherited generation behavior for a DCN301 ASIC variant.

## Risks and Test Signals
The mixed inheritance is the main risk: init and bandwidth come from older paths while color/writeback/metadata come from DCN30. Test with boot, power-down-on-boot, writeback, DMData, color, ABM, optimized power state, and pending-update waits on DCN301.
