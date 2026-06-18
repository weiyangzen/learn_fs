# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_backlight.c

## Purpose
`intel_backlight.c` implements i915 panel backlight control. It maps user brightness to hardware PWM ranges, abstracts multiple native PWM register layouts and external PWM chips, initializes panel backlight parameters from VBT/hardware, exposes a Linux backlight class device when enabled, and coordinates enable/disable/update with display modesets.

## Important APIs, Types, and Functions
- Scaling helpers `scale()`, `clamp_user_to_hw()`, `scale_hw_to_user()`, `intel_backlight_level_to_pwm()`, and `intel_backlight_level_from_pwm()` translate between user, logical hardware, and raw PWM levels.
- Platform get/set/enable/disable/setup callbacks exist for LPT/SPT PCH PWM, earlier PCH split PWM, i9xx/i965, VLV/CHV, BXT/GLK, CNP+, and external PWM.
- `intel_backlight_setup()` initializes `panel->backlight` state and marks the backlight present.
- `intel_backlight_enable()`, `intel_backlight_disable()`, and `intel_backlight_update()` are modeset-facing operations.
- `intel_backlight_set_acpi()` handles firmware/ACPI brightness requests.
- Backlight class functions register `intel_backlight`, update status, and read brightness when `CONFIG_BACKLIGHT_CLASS_DEVICE` is enabled.
- `intel_backlight_init_funcs()` chooses DSI DCS, DP AUX, native PWM, or external PWM implementations.

## Control Flow
Initialization selects backlight function tables based on connector type, platform, PCH type, and quirks. Setup reads existing PWM registers or external PWM state, falls back to VBT-derived PWM periods when registers are uninitialized, calculates minimum levels, reads current brightness, and stores logical level/enabled state. Modeset enable clamps the saved level to minimum and invokes platform enable. Disable updates the class device power state, marks disabled, and calls the platform disable path. User or ACPI updates lock `display->backlight.lock`, scale brightness, update cached level, and write hardware only when enabled.

## State and Persistence
State is stored in `connector->panel.backlight`: function pointers, PWM function pointers, min/max/current logical levels, PWM min/max, active-low and inversion attributes, controller index, combination mode, enabled/present flags, external `pwm_state`, class device pointer, and optional power hook. VBT-derived fields in `connector->panel.vbt.backlight` provide frequency, minimum brightness, controller, and backlight type. Hardware state lives in PWM duty/frequency/control registers or Linux PWM framework state.

## Dependencies and Integration Points
The file integrates Linux PWM, Linux backlight class, ACPI video policy, DRM modeset locking, i915 VBT data, panel power sequencing (`intel_pps_backlight_power`), DP AUX backlight, DSI DCS backlight, display RPM, quirks, PCI config LBPC on legacy combination mode, and register definitions from `intel_backlight_regs.h`.

## Risks
Brightness inversion combines module parameter and quirk behavior; off-by-one or min/max mistakes can make controls reversed or clamp to unusable brightness. Platform callbacks use different register units and enable ordering; writes before PWM enable intentionally do or do not stick depending on platform. VBT PWM frequency/minimum values may be bogus and are partially clamped. External PWM setup depends on VBT DSI PMIC/SoC selection. Backlight class callbacks lock the DRM connection mutex and display backlight mutex, so lock ordering must remain stable.

## Test Signals
KMS debug logs show selected backlight backend, initialized brightness, PWM frequency, controller, active-low state, and failed setup. Test native PWM platforms from gen2 through CNP+, VLV/CHV DSI external PWM, eDP AUX backlight fallback, ACPI brightness events during driver init, suspend/resume, vga_switcheroo skip path, class device reads/writes, inversion quirks, and VBT min/frequency edge cases.
