## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_opp_regamma_v.c

Purpose: DCE11 underlay regamma LUT and piecewise-linear gamma programming. It configures gamma regions, powers LUT memories for programming, writes RGB/delta LUT entries, and selects regamma mode.

Important APIs: `dce110_opp_program_regamma_pwl_v`, `dce110_opp_power_on_regamma_lut_v`, and placeholder `dce110_opp_set_regamma_mode_v`. Helpers include `power_on_lut`, `set_bypass_input_gamma`, `regamma_config_regions_and_segments`, and `program_pwl`.

Control flow: PWL programming writes start/end/region descriptors from `pwl_params`, bypasses input gamma, forces gamma memory on, streams `hw_points_num` RGB and delta values through `GAMMA_CORR_LUT_DATA`, sets mode 1, then returns memory control to automatic. Power control toggles input/regamma memory fields in `DCFEV_MEM_PWR_CTRL`.

State and persistence: region descriptors, LUT contents, gamma mode, and memory power fields persist in hardware. Dependencies are `pwl_params`, DCE transform wrappers, and DCE11 color-management registers. Risks include a likely bug in `configure_regamma_mode` building a value but writing zero, the no-op `dce110_opp_set_regamma_mode_v`, bounded but weak memory-power polling, and no guard against oversized `hw_points_num`. Test signals are gamma ramp accuracy, LUT programming under power gating, color-management bypass behavior, and regression checks for mode selection.
