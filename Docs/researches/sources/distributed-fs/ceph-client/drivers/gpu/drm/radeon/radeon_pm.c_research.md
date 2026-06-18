# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_pm.c

## Purpose

`radeon_pm.c` is the Radeon KMS driver's central power-management implementation. It coordinates legacy profile-based reclocking, legacy dynamic power management (`dynpm`), newer DPM power-state selection, sysfs knobs, hwmon telemetry/control, thermal work, suspend/resume, and debugfs reporting. The code translates user policy, AC/battery status, display topology, video-engine activity, thermal events, and ASIC capability callbacks into hardware clock, voltage, fan, and display-configuration changes.

## Important APIs, Functions, And Types

- `radeon_pm_get_type_index()` scans `rdev->pm.power_state[]` for a requested `enum radeon_pm_state_type` instance and falls back to `default_power_state_index`. R600/Evergreen code uses it when deriving profile tables from BIOS power states.
- `radeon_pm_acpi_event_handler()` reacts to ACPI power events. In DPM mode it updates `rdev->pm.dpm.ac_power` and toggles Aruba BAPM when available; in profile/auto mode it recalculates the profile and reclocks.
- Legacy profile helpers: `radeon_pm_update_profile()`, `radeon_set_power_state()`, `radeon_pm_set_clocks()`, `radeon_pm_compute_clocks_old()`, and `radeon_dynpm_idle_work_handler()`.
- DPM helpers: `radeon_dpm_single_display()`, `radeon_dpm_pick_power_state()`, `radeon_dpm_change_power_state_locked()`, `radeon_dpm_enable_uvd()`, `radeon_dpm_enable_vce()`, and `radeon_pm_compute_clocks_dpm()`.
- Lifecycle entry points: `radeon_pm_init()`, `radeon_pm_late_init()`, `radeon_pm_suspend()`, `radeon_pm_resume()`, and `radeon_pm_fini()`.
- User/monitoring interfaces are created through device attributes `power_profile`, `power_method`, `power_dpm_state`, `power_dpm_force_performance_level`, hwmon sensor attributes (`temp1_input`, `pwm1`, `freq1_input`, `in0_input`, etc.), and debugfs `radeon_pm_info`.
- The file depends heavily on state embedded in `struct radeon_device`: `rdev->pm`, `rdev->pm.dpm`, rings/fences, CRTC state, BIOS-derived power tables, firmware presence, and ASIC callback tables under `rdev->asic->pm` and `rdev->asic->dpm`.

## Control Flow

Initialization starts in `radeon_pm_init()`. It applies a DPM quirk table, chooses `PM_METHOD_DPM` or `PM_METHOD_PROFILE` based on GPU family, module parameter policy, firmware availability, IGP/dGPU status, and stability quirks, then dispatches to `radeon_pm_init_dpm()` or `radeon_pm_init_old()`. The old path initializes default/current clocks, reads ATOM or COMBIOS power modes, builds profile tables, registers hwmon when an internal thermal sensor exists, and initializes delayed `dynpm` work. The DPM path requires ATOM BIOS data, initializes hwmon and thermal work, calls the ASIC-specific DPM init/setup/enable callbacks, records boot/current/requested power states, and exposes debugfs.

`radeon_pm_late_init()` creates sysfs files after core PM setup. DPM exposes DPM state and forced-performance attributes plus legacy compatibility attributes; profile mode exposes legacy `power_profile` and `power_method` when multiple power states exist. This split matters because userspace-visible controls depend on both the selected PM method and whether DPM successfully enabled.

Legacy profile changes flow from sysfs or display topology updates into `radeon_pm_compute_clocks_old()`. It rebuilds `active_crtcs` and `active_crtc_count`, chooses profile indices via `radeon_pm_update_profile()`, then calls `radeon_pm_set_clocks()`. `radeon_pm_set_clocks()` takes `mclk_lock` and `ring_lock`, waits for each ready ring to drain with `radeon_fence_wait_empty()`, unmaps VRAM BO CPU mappings, takes vblank references for active CRTCs, and calls `radeon_set_power_state()`. The actual transition clamps requested SCLK/MCLK to defaults, optionally adjusts voltage/PCIe/misc before or after clock changes, waits for vblank in flicker-sensitive paths, and updates current indices/clocks only after programming succeeds. Display bandwidth/watermark data is refreshed after the switch.

`dynpm` is a delayed-work loop. `radeon_dynpm_idle_work_handler()` counts outstanding fences across ready rings every `RADEON_IDLE_LOOP_MS`; sustained queued work plans an upclock and idle periods plan a downclock after `RADEON_RECLOCK_DELAY_MS`. It then calls `radeon_pm_get_dynpm_state()` and `radeon_pm_set_clocks()` when the action timeout expires, rescheduling itself while active.

DPM clock computation flows through `radeon_pm_compute_clocks_dpm()`. It rebuilds new active CRTC masks/counts, counts high-pixel-clock connectors, refreshes AC power status, and calls `radeon_dpm_change_power_state_locked()` under `pm.mutex`. DPM power selection maps user states and internal overrides to BIOS power-state classifications: UVD, thermal, ACPI, ULV, boot, 3D performance, battery, balanced, and performance. Fallbacks walk from more specialized states to safer broad states when no exact BIOS match exists. A power-state change takes `mclk_lock` and `ring_lock`, calls ASIC pre-change hooks, updates bandwidth/display configuration, drains rings, programs the state with `radeon_dpm_set_power_state()`, runs post hooks, updates current display and power-state bookkeeping, and reapplies forced performance levels. Thermal activity forces low performance while preserving the user's requested forced level.

UVD/VCE integration sets `uvd_active`, `vce_active`, stream counters, and VCE level under `pm.mutex`, then recomputes clocks unless the ASIC supports direct UVD powergating. Thermal work selects internal thermal state or returns to the user state based on temperature thresholds or interrupt direction, toggles `thermal_active`, and recomputes clocks.

Suspend and resume split by PM method. Legacy suspend pauses active `dynpm` and cancels delayed work; legacy resume restores default clocks/voltages for Barts-Cayman MC firmware cases, resets current PM bookkeeping, restarts `dynpm` when needed, and recomputes clocks. DPM suspend disables DPM and resets current/requested state to boot; DPM resume redoes ASIC setup and enable, falling back to default clocks/voltages if DPM resume fails.

## State And Persistence Behavior

Most state is runtime-only in `rdev->pm` and the hardware registers programmed through ASIC callbacks. The file persists no state to disk. Important persistent-in-memory fields include:

- Legacy profile fields: `profile`, `profile_index`, `requested_power_state_index`, `requested_clock_mode_index`, `current_power_state_index`, `current_clock_mode_index`, `current_sclk`, `current_mclk`, `current_vddc`, `current_vddci`.
- Display state snapshots: `active_crtcs`, `active_crtc_count`, `req_vblank`, and DPM equivalents `new_active_crtcs`, `current_active_crtcs`, `new_active_crtc_count`, `single_display`, and `high_pixelclock_count`.
- DPM policy/state: `dpm.state`, `dpm.user_state`, `dpm.forced_level`, `dpm.ac_power`, `dpm.uvd_active`, `dpm.vce_active`, `dpm.thermal_active`, `current_ps`, `requested_ps`, and `boot_ps`.
- Work state: `dynpm_state`, `dynpm_planned_action`, `dynpm_action_timeout`, `dynpm_can_upclock`, `dynpm_can_downclock`, and delayed/workqueue objects.
- User-visible sysfs and hwmon objects are registered/unregistered at runtime; `sysfs_initialized` prevents duplicate sysfs creation.

Synchronization uses `pm.mutex` for PM policy and DPM state, `pm.mclk_lock` around memory-clock-sensitive regions, `ring_lock` while draining rings and programming transitions, vblank reference counting to keep vblank interrupts alive during transitions, and work cancellation on method changes/suspend/fini.

## Dependencies And Integration Points

The file integrates with Linux DRM/KMS (`drm_for_each_crtc`, vblank helpers, debugfs), TTM/GEM BO tracking (`rdev->gem.objects`, `ttm_bo_unmap_virtual()`), power-supply AC status, hwmon, PCI IDs, firmware gates (`rlc_fw`, `smc_fw`, `mc_fw`), ATOM/COMBIOS power-table parsing, Radeon rings/fences, display bandwidth code, and many ASIC-specific callbacks. `radeon_acpi.c` calls `radeon_pm_acpi_event_handler()`. Other Radeon display/clock files call `radeon_pm_get_type_index()` through the public declaration in `radeon.h`, while this private header only exposes the ACPI handler.

## Risks And Edge Cases

- Reclocking is sensitive to display timing. The code tries to avoid flicker by waiting for vblank, refusing some DPM single-display paths when vblank is too short or refresh is at least 120 Hz, and taking vblank refs, but modeset races can still produce "no vblank, can glitch" paths.
- Ring drain failures in legacy `radeon_pm_set_clocks()` abort without resetting the GPU, leaving recovery to higher layers. DPM ring-drain calls ignore return values while already in the transition.
- Sysfs setters use prefix `strncmp()` checks, so trailing text after a valid prefix may be accepted in several attributes.
- PX/switchable graphics checks prevent some sysfs/hwmon reads and writes while the ASIC is powered off; missing these checks in new interfaces would risk touching powered-down hardware.
- DPM fallback selection can choose broad performance/battery states when BIOS-specific internal states are missing. That is safer than NULL, but it may change power or thermal behavior on unusual BIOS tables.
- The DPM quirk table disables default DPM on known unstable boards only when policy permits; adding/removing quirks changes field stability.
- Fan control exposes percent-to-255 conversions and optional read/write modes depending on ASIC callback availability; partial callback implementations can create read-only or write-only attributes.
- Lifecycle ordering is important: sysfs/hwmon/debugfs objects must not outlive the backing `rdev`, delayed work must be canceled, and DPM must be disabled before freeing `pm.power_state`.

## Test Signals

Useful signals include successful build coverage with relevant Radeon Kconfig options, sysfs presence/absence for `power_profile`, `power_method`, `power_dpm_state`, and `power_dpm_force_performance_level`, hwmon attribute visibility matching DPM/fan/voltage callback support, debugfs `radeon_pm_info` output in both DPM and legacy modes, suspend/resume on DPM and profile GPUs, PX powered-off sysfs/hwmon error behavior, AC-plug/unplug events changing `ac_power` and selected states, UVD/VCE workloads triggering internal states, thermal interrupts forcing low performance, multi-monitor/high-refresh modes avoiding unsafe mclk changes, and ring-drain failure paths not deadlocking `ring_lock` or `mclk_lock`.
