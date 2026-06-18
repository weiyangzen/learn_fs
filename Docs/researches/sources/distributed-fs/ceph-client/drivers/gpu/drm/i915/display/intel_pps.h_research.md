# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pps.h

## Purpose
`intel_pps.h` declares the eDP panel power sequencing interface for the i915 display stack. It exposes lock helpers, VDD/panel power operations, backlight control, initialization/reset hooks, VLV/CHV pipe ownership helpers, debugfs setup, and a legacy PPS lock assertion helper.

## Important APIs And Control Flow
The most important interface is the `with_intel_pps_lock(dp)` macro, built on `intel_pps_lock()` and `intel_pps_unlock()`. Callers use it to obtain a display-core power wakeref and `display->pps.mutex` in the correct order.

Unlocked operations such as `intel_pps_vdd_on_unlocked()`, `intel_pps_vdd_off_unlocked()`, `intel_pps_on_unlocked()`, `intel_pps_off_unlocked()`, and `intel_pps_check_power_unlocked()` require the caller to hold the PPS lock. Locked wrappers such as `intel_pps_vdd_on()`, `intel_pps_vdd_off()`, `intel_pps_on()`, `intel_pps_off()`, `intel_pps_vdd_off_sync()`, `intel_pps_have_panel_power_or_vdd()`, and `intel_pps_wait_power_cycle()` acquire it internally.

Initialization APIs are split into early panel setup (`intel_pps_init()`), late VBT-aware setup (`intel_pps_init_late()`), encoder reset/reprogramming (`intel_pps_encoder_reset()`), and display MMIO-base setup (`intel_pps_setup()`). VLV/CHV-specific APIs expose pipe tracking, active-pipe reset, backlight initial-pipe selection, port enable/disable integration, and global reset of PPS state.

## State, Dependencies, Risks, And Test Signals
The header has no direct state storage, but its API controls persistent fields inside `struct intel_dp::pps` and global fields inside `struct intel_display::pps`. Correct lock choice is the main risk: using unlocked functions without the PPS lock can race delayed VDD-off work, power-domain wakeref updates, or PP_CONTROL programming.

The API is consumed by DP/eDP enable/disable, AUX, backlight, suspend/resume, and debugfs paths. Build tests plus eDP panel power/backlight and VLV/CHV port ownership tests exercise the declarations.
