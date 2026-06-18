<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_switcheroo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_switcheroo.c

## Purpose
Registers i915 as a VGA switcheroo client and implements power-state transitions for hybrid graphics systems.

## Important APIs, types, and functions
- `i915_switcheroo_register()` and `i915_switcheroo_unregister()` wrap `vga_switcheroo_register_client()` and unregister.
- `i915_switcheroo_set_state()` powers the GPU on/off through i915 switcheroo resume/suspend paths.
- `i915_switcheroo_can_switch()` allows switching only when DRM is initialized, display state is present, and open count is zero.
- `i915_switcheroo_ops` supplies `set_gpu_state` and `can_switch`.

## Control flow
On switch-on, the code marks DRM switch power state changing, forces PCI D0 because i915 resume does not do it here, calls `i915_driver_resume_switcheroo()`, then marks power on. On switch-off, it marks changing, calls `i915_driver_suspend_switcheroo()` with a suspend message, and marks power off. Guards reject transitions before i915/display initialization.

## State and persistence
Updates `i915->drm.switch_power_state`; the actual device power/display/GEM state is managed by the driver suspend/resume helpers. Registration persists with the PCI device until unregister.

## Dependencies and integration points
Depends on Linux VGA switcheroo, PCI power management, DRM switch power states, i915 driver suspend/resume hooks, and display-device presence detection.

## Risks
`open_count` checking is intentionally racy and avoids `drm_global_mutex` due to load-path lock inversion. Switching before display initialization or while userspace has the device open can fail or disrupt users.

## Test signals
Hybrid laptop switcheroo tests, runtime suspend/resume logs, open-file switch rejection, PCI D-state changes, display reprobing after switch-on, and suspend/resume regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_switcheroo.c -->
