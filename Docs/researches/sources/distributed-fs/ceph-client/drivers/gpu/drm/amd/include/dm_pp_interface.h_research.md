# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/dm_pp_interface.h

## Purpose
This header defines the display-manager to PowerPlay/SMU interface for display configuration and clock requirements. It is the shared contract by which display code reports active displays, timing constraints, and requested clocks to AMDGPU power-management implementations.

## Important APIs, Types, And Data
`PP_MAX_CLOCK_LEVELS` and `MAX_NUM_CLOCKS` are both 16; `MAX_NUM_DISPLAY` is 32. `enum amd_pp_display_config_type` classifies link/display modes such as DP link rates, HDMI rates, LVDS, DVI, wireless, and VGA.

`struct single_display_configuration` records one display path: controller IDs, signal type, display state, primary and secondary transmitter PHY/lane maps, flags, display type, resolution, refresh, and pixel clock. `struct amd_pp_display_configuration` aggregates policy flags and derived limits such as NB pstate disable, CPU C-state/P-state constraints, display counts, minimum memory/core/bus clocks, vblank/line timing, multi-monitor sync state, DCEF/DC clock requirements, and up to 32 display records.

Clock query/request structures include `amd_pp_simple_clock_info`, `amd_pp_clock_info`, `amd_pp_clocks`, `pp_clock_levels_with_latency`, `pp_clock_levels_with_voltage`, and `pp_display_clock_request`. `enum PP_DAL_POWERLEVEL` and `enum amd_pp_clock_type` define power-level and clock-domain selectors; `amd_pp_f_clock` aliases `amd_pp_dcef_clock`.

## Control Flow
This header has no code. Display code fills configuration and clock-request structures, then DPM/PowerPlay/SMU functions consume them to set display clocks, memory clock constraints, stutter/deep-sleep policy, DCEF/DCF/DPP/SOC clocks, and latency-aware power states.

## State And Persistence
The primary persistent state is `adev->pm.pm_display_cfg` and SMU/PowerPlay display configuration copies. Values persist across display updates until replaced by a new configuration. Clock level arrays are bounded fixed-size buffers, avoiding dynamic allocation in this ABI.

## Dependencies And Integration Points
It includes `dm_services_types.h` for common display-manager types. Integration points include `amdgpu_dpm_internal.c`, legacy DPM, PowerPlay hardware managers, SW SMU, `kgd_pp_interface.h`, `amdgpu_dm_pp_smu.c`, and display mode-set paths that request clock changes.

## Risks
Units are mixed and must be preserved: pixel/display clocks are in kHz, some bandwidth/core-clock fields are in 10 kHz-derived units, and latencies are in microseconds. `MAX_NUM_DISPLAY`, `PP_MAX_CLOCK_LEVELS`, and `MAX_NUM_CLOCKS` require caller-side bounds checks. Incorrect `multi_monitor_in_sync`, vblank, or line-time data can choose unsafe memory-clock switching behavior and cause display underflow or hangs.

## Test Signals
Exercise single-monitor, multi-monitor synchronized and unsynchronized, HDMI, DP, eDP/LVDS, high refresh, deep-sleep, stutter, and memory-clock switching cases. Validate DPM/SMU logs, clock requests, underflow counters, suspend/resume behavior, and mode-set stability.
