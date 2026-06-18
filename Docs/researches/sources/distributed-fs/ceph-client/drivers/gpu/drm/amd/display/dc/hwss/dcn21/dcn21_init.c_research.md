# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn21/dcn21_init.c

## Purpose
Installs the DCN 2.1 HWSS dispatch tables. It inherits most DCN20 behavior and adds DCN21 system-context initialization, optimized power-state transitions, ABM/backlight hooks, S0i3 and platform workarounds, and ABM support detection.

## Important APIs, Types, and Functions
Exports `dcn21_hw_sequencer_construct(struct dc *dc)`. Public table entries of note are `init_sys_ctx = dcn21_init_sys_ctx`, `optimize_pwr_state = dcn21_optimize_pwr_state`, `exit_optimized_pwr_state = dcn21_exit_optimized_pwr_state`, `set_backlight_level = dcn21_set_backlight_level`, `set_abm_immediate_disable = dcn21_set_abm_immediate_disable`, `set_pipe = dcn21_set_pipe`, and `is_abm_supported = dcn21_is_abm_supported`. Private additions include `s0i3_golden_init_wa = dcn21_s0i3_golden_init_wa` and `PLAT_58856_wa = dcn21_PLAT_58856_wa`.

## Control Flow
Constructor assigns the public and private tables. Runtime calls through table pointers compose DCN20 plane/stream/writeback behavior with DCN21 power, aperture, and backlight features.

## State and Persistence Behavior
Persists vtable selection in `dc`/`hwseq`; no local state. Selected hooks later mutate clocks, DMUB, ABM, link, and stream state.

## Dependencies and Integration Points
Depends on DCE110, DCN10, DCN20, and DCN21 HWSEQ implementations. It is the base behavior inherited by several later DCN init files.

## Risks and Test Signals
Risk lies in mixing inherited DCN20 behavior with DCN21-specific power/backlight hooks. Test signals include boot, S0i3, standby/resume, ABM panel control, writeback, DSC/ODM, DPMS workaround, and mode-set stability.
