# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/power.h

## Purpose
This header declares the GMA500 power-management interface used by driver load/unload, PCI PM callbacks, and register-access wrappers.

## Important APIs, Types, and Functions
It declares `gma_power_init()`, `gma_power_uninit()`, `gma_power_suspend()`, `gma_power_resume()`, `gma_power_begin()`, and `gma_power_end()`, with forward declarations for `struct device` and `struct drm_device`.

## Control Flow
There is no executable flow. The declared API supports a lifecycle of init, repeated begin/end guarded MMIO access, suspend/resume callbacks, and uninit.

## State and Persistence Behavior
The header owns no state. Implementations mutate runtime PM references, saved PCI/display state, and `drm_psb_private.pm_initialized`.

## Dependencies and Integration Points
It is included by display, LVDS, backlight, CRTC, and driver-core files that need power-safe hardware access. The suspend/resume declarations are used in the PCI driver PM ops.

## Risks
Callers must balance `gma_power_begin()` with `gma_power_end()` only when begin succeeds. Misuse can leak runtime PM references or access powered-down hardware.

## Test Signals
Build should verify all users see the declarations. Runtime test signals are balanced PM refs and absence of MMIO faults in callers using the wrappers.
