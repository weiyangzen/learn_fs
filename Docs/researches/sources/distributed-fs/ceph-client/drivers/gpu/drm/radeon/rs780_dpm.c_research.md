# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs780_dpm.c

## Purpose
`rs780_dpm.c` implements dynamic power management for RS780/RS880 integrated GPUs. It parses ATOM PowerPlay and integrated-system-info tables, constructs IGP power states, initializes SCLK and voltage-scaling hardware, handles DPM enable/disable and power-state transitions, reports current levels, and supports forced performance levels.

## Important APIs, Types, And Functions
Public callback functions are `rs780_dpm_init()`, `rs780_dpm_enable()`, `rs780_dpm_disable()`, `rs780_dpm_set_power_state()`, `rs780_dpm_setup_asic()`, `rs780_dpm_display_configuration_changed()`, `rs780_dpm_fini()`, `rs780_dpm_get_sclk()`, `rs780_dpm_get_mclk()`, `rs780_dpm_print_power_state()`, `rs780_dpm_debugfs_print_current_performance_level()`, `rs780_dpm_get_current_sclk()`, `rs780_dpm_get_current_mclk()`, and `rs780_dpm_force_performance_level()`. Internal helpers manage PLL divider programming, FVTHROT registers, voltage/PWM ranges, UVD clock ordering, PowerPlay table parsing, and display refresh parameters. `struct igp_power_info` and `struct igp_ps` are defined in `rs780_dpm.h`.

## Control Flow
`rs780_dpm_init()` allocates private power info, gets platform caps, parses PowerPlay states into `radeon_ps` plus `igp_ps`, and reads integrated-system-info fields for voltage control and UMA clock. `rs780_dpm_enable()` captures active CRTC/refresh, disables VBIOS power saving, rejects already-enabled dynamic PM, initializes R600 DPM parameter registers, starts dynamic PM, sets feedback-divider and PWM ranges, enables clock/voltage scaling, programs activity thresholds, and optionally enables graphics clock gating. Power-state changes update UVD clocks before or after engine scaling depending on direction, force max voltage, program new feedback-divider limits, select vblank source, reactivate scaling, and re-enable voltage scaling.

## State, Persistence, And Dependencies
Driver state is stored in `rdev->pm.dpm.priv`, `rdev->pm.dpm.ps`, current/requested/boot/uvd power-state pointers, and forced-level state. Hardware state includes FVTHROT control, feedback-divider, PWM, activity-threshold, SPLL bypass, CG_INTGFX_MISC, and graphics clock-gating registers. Dependencies include ATOM BIOS table parsing, R600 DPM helper functions, Radeon clock divider APIs, UVD clock programming, IRQ thermal state, debugfs `seq_file`, and `rs780d.h` register definitions.

## Integration Points
`radeon_asic.c` wires these functions into the RS780 DPM callback table. `rs690_bandwidth_update()` can query `radeon_dpm_get_sclk()` for low/high watermark calculations on RS780/RS880. The debug and print callbacks feed Radeon PM sysfs/debugfs reporting. UVD state classification uses shared R600 helpers.

## Risks
PowerPlay and integrated-system-info parsing assumes table offsets and entry sizes are valid; malformed BIOS data can cause init failure or bad clocks. Engine-clock scaling requires low/high/current dividers to share reference and post dividers, otherwise it returns `-EINVAL`. Voltage control is disabled when BIOS values are inconsistent, but PWM inversion and device-ID-specific defaults still carry board risk. Ordering around SPLL bypass, forced voltage, UVD clocks, and vblank selection is hardware-sensitive.

## Test Signals
Strong signals are successful DPM init/enable on RS780 and RS880 device IDs, correct parsed boot/UVD states, transitions between battery/performance/UVD profiles, forced low/high/auto behavior, debugfs current SCLK matching FVTHROT status, stable UVD playback during transitions, display reconfiguration refresh-threshold updates, suspend/resume with DPM disabled and re-enabled, and no thermal IRQ or clock-gating regressions.
