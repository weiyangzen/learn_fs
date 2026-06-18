# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_driver.h

## Purpose
`intel_display_driver.h` declares the high-level display driver lifecycle and access-control API. It is the parent-driver facing contract for initializing, registering, suspending, resuming, and removing display support.

## Important APIs, Types, And Functions
The header declares probe phases (`probe_defer`, `init_hw`, `early_probe`, `probe_noirq`, `probe_nogem`, `probe`), registration/removal phases (`register`, `unregister`, `remove`, `remove_noirq`, `remove_nogem`), suspend/resume (`intel_display_driver_suspend()`, `intel_display_driver_resume()`, `__intel_display_driver_resume()`), and access controls (`enable_user_access`, `disable_user_access`, `suspend_access`, `resume_access`, `check_access`). It forward declares DRM atomic and modeset acquire state objects, `struct intel_display`, and `struct pci_dev`.

## Control Flow And State
The header encodes the lifecycle split used by the parent driver. The noirq/nogem/probe naming matters: callers must invoke phases in the correct order relative to IRQ install and GEM initialization, and remove phases must be paired with the corresponding successful probe phases. Access-control calls mutate `display->access` in the implementation.

## Dependencies And Integration Points
This file is included by parent driver code and reset code. The special `__intel_display_driver_resume()` declaration is explicitly an interface for display reset paths that need to restore duplicated atomic state with an existing modeset acquire context.

## Risks And Test Signals
Risks are primarily call-order mistakes and mismatched cleanup after partial failures. Build tests catch signature drift; runtime tests should exercise full probe/remove, no-display devices, suspend/resume, display reset, and user-access rejection paths during suspend/unload.
