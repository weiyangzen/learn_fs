# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/power/power_helpers.c

Purpose: implements ABM/DMCU/DMUB backlight configuration helpers, PSR/Replay configuration helpers, eDP panel capability workarounds, DSC slice-height checks, and custom backlight capability export.

Important APIs: exported functions include `dmub_init_abm_config`, `dmcu_load_iram`, `is_psr_su_specific_panel`, `mod_power_calc_psr_configs`, `init_replay_config`, `mod_power_only_edp`, `psr_su_set_dsc_slice_height`, Replay coasting/frame-skip setters, `calculate_replay_link_off_frame_count`, `fill_custom_backlight_caps`, and `reset_replay_dsync_error_count`.

Control flow: ABM paths build 256-byte IRAM/config tables from fixed reduction tables, aggressiveness sets, gamma curves, and caller backlight LUTs. Version-specific fillers handle ABM 2.0, 2.2, and 2.3/2.4 layouts and endian selection. DMUB config copies packed table fields into a 32-bit-aligned config struct before calling ABM functions. PSR config computes vblank and line time from stream timing, converts DPCD setup time into microseconds, and decides frame-capture indication and SDP deadline.

State and persistence: mutates `link->psr_settings`, `link->replay_settings`, `psr_config`, ABM firmware/config buffers, and caller-provided ACPI backlight caps. Static tables encode persistent policy curves and panel workarounds.

Dependencies and integration: depends on DMCU/ABM hardware function tables, `resource_pool`, DC stream/link/core types, DPCD caps, Replay and PSR config structures, and ACPI backlight caps.

Risks: IRAM layouts are fixed-size firmware contracts; endian mistakes or reserve-area writes can break firmware behavior. Backlight LUT size is assumed valid and indexed without explicit zero-size guards. Timing arithmetic divides by pixel clock-derived values. Panel-specific PSR-SU workarounds are fragile and sink-ID dependent.

Test signals: ABM config for all versions/sets/endian modes, LUT boundary sizes and monotonic curves, DMCU uninitialized behavior, PSR timing deadline arithmetic, eDP DSC slice granularity, Replay frame-skip divide-by-zero guards, panel workaround IDs, and custom backlight caps size calculation.
