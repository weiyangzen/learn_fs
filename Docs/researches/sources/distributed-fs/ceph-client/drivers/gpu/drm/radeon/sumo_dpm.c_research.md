<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumo_dpm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumo_dpm.c

## Purpose
`sumo_dpm.c` implements dynamic power management for Sumo/Palm APUs in the Radeon driver. It parses AtomBIOS integrated-system and PowerPlay tables, constructs Sumo-specific power-state data, programs SCLK DPM levels, voltage indices, deep-sleep dividers, GNB/NB policy, boost state, UVD clocks, thermal thresholds, and clock/power gating, and exposes the ASIC DPM callbacks registered in `radeon_asic.c`.

## Important APIs, types, and functions
- Public lifecycle callbacks: `sumo_dpm_init`, `sumo_dpm_setup_asic`, `sumo_dpm_enable`, `sumo_dpm_late_enable`, `sumo_dpm_disable`, `sumo_dpm_fini`.
- Power-state transition callbacks: `sumo_dpm_pre_set_power_state`, `sumo_dpm_set_power_state`, `sumo_dpm_post_set_power_state`, and `sumo_dpm_force_performance_level`.
- Query/debug callbacks: `sumo_dpm_get_sclk`, `sumo_dpm_get_mclk`, `sumo_dpm_get_current_sclk`, `sumo_dpm_get_current_mclk`, `sumo_dpm_get_current_vddc`, `sumo_dpm_print_power_state`, and `sumo_dpm_debugfs_print_current_performance_level`.
- Table helpers: `sumo_parse_sys_info_table`, `sumo_parse_power_table`, `sumo_parse_pplib_clock_info`, `sumo_parse_pplib_non_clock_info`, `sumo_construct_boot_and_acpi_state`, `sumo_construct_sclk_voltage_mapping_table`, `sumo_construct_vid_mapping_table`, and display-voltage table construction.
- Register programming helpers cover graphics/memory clock gating, graphics power gating, BSP/AT/TP/SSTP/VC timing, DPM level enable bits, SCLK dividers, VID fields, deep-sleep dividers, voltage scaling, ACPI/boot levels, thermal thresholds, and NB pstate forcing.
- SMU integration uses functions from `sumo_smc.c`: M3 arbiter initialization, power-gating initialization, boost timer setup, boost state enable, alt-VDDNB notification, TDP limit programming, and firmware version readback.

## Control flow
Initialization allocates `sumo_power_info`, sets conservative feature flags and Palm workarounds, parses the AtomBIOS integrated-system table revision 6, constructs SCLK/VID/display voltage maps, reads platform caps, parses PowerPlay states into `radeon_ps` plus `sumo_ps`, and enables DPM policy. ASIC setup initializes M3 arbiter data, reads SMC firmware version, programs ACPI SCLK/voltage, enables static ACPI PM, and hands display PHY control policy to the selected owner.

Enable programs boot state and BSP, resets/starts the activity monitor, programs trend parameters, activity thresholds, thermal throttling, DC timeout, voltage scaling, SSTP, VC, and CNB thermal overrides, starts SCLK DPM, waits for level 0, enables deep sleep, and initializes boost timer when supported. Late enable applies clock/power gating and thermal IRQ range setup. Disable reverses clock/power gating, deep sleep, VC, DPM enable, voltage scaling, and thermal IRQ state.

For power-state changes, `pre_set` copies the requested state and dynamically patches it for thermal states, boost/UI-performance states, battery/SD/HD NBPS1 forcing, minimum SCLK, deep-sleep dividers, and GNB slow policy. `set_power_state` sequences UVD clock changes relative to SCLK direction, disables boost, notifies alt-VDDNB when leaving forced NBPS1, forces level 0, programs new DPM levels, watermark/limit bits, BSP and activity thresholds, NB state, releases forced mode, sends post alt-VDDNB notifications, re-enables boost, and updates UVD clocks after SCLK changes if needed. `post_set` commits requested state as current.

## State and persistence behavior
Driver state lives in `rdev->pm.dpm.priv` as `struct sumo_power_info`, in allocated `rdev->pm.dpm.ps[]` entries with `struct sumo_ps` private data, and in cached `current_rps/current_ps` and `requested_rps/requested_ps`. Persistent hardware state is written through Sumo registers in `sumod.h`, including DPM level dividers, valid bits, VID fields, deep-sleep controls, thermal interrupt thresholds, clock/power gating, activity monitor timing, UVD clocks, and RCU boost/TDP registers. Parsed VBIOS data is copied into driver-owned structures and used across transitions until `sumo_dpm_fini` frees it.

## Dependencies and integration points
The implementation includes `radeon.h`, `radeon_asic.h`, `sumod.h`, `r600_dpm.h`, `cypress_dpm.h`, `sumo_dpm.h`, and `linux/seq_file.h`. It relies on AtomBIOS parsers, endian conversion helpers, Radeon MMIO macros, `r600_calculate_u_and_p`, UVD clock setup, thermal IRQ infrastructure, debugfs seq output, platform-cap parsing, and the ASIC callback table in `radeon_asic.c`.

## Risks and test signals
High-risk areas include VBIOS table revision assumptions, allocation cleanup on partial init failure, divider/VID bit programming, boost level 7 handling, forced-mode timing loops that do not report timeout errors, Palm power-gating workarounds, UVD clock ordering, and DPM state copies with private pointers. Test signals include Sumo/Palm boot with DPM enabled, debugfs current performance level, forced low/high/auto transitions, UVD playback while DPM changes, battery/performance/thermal PowerPlay states, thermal IRQ range programming, suspend/resume, and absence of SCLK/voltage stalls or GPU hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumo_dpm.c -->
