# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_module.c

## Purpose
Defines the i915 kernel module initialization and exit sequence, including KMS disable checks, subsystem module setup, PCI driver registration, selftests, and perf sysctl registration.

## Important APIs, types, and functions
Key functions are `i915_check_nomodeset()`, `i915_init()`, and `i915_exit()`. `init_funcs[]` is an ordered table of init/exit pairs for active tracking, contexts, GEM contexts, objects, requests, scheduler, VMA, VMA resources, mock selftests, PCI driver, and perf sysctl.

## Control flow
Init iterates `init_funcs[]`, unwinding previously initialized entries in reverse order on negative error. Positive return is treated as an early successful exit only for entries without exit callbacks. `init_progress` records how far init reached, and module exit unwinds from `init_progress - 1` down to zero. `i915_check_nomodeset()` handles deprecated `i915.modeset` and global firmware-only `nomodeset` behavior.

## State and persistence
Global `init_progress` persists module initialization depth. Registered subsystem caches, PCI driver state, and perf sysctls persist until module exit or unwind.

## Dependencies and integration points
Depends on many i915 subsystem module init/exit APIs, `i915_modparams`, DRM firmware-driver-only mode detection, PCI registration, selftest configuration, and module metadata macros.

## Risks
Ordering is important: later subsystems may depend on earlier slab/cache/context/request infrastructure. Positive early exits with exit callbacks are warned because partial teardown would be undefined. Deprecated modeset handling must preserve historical boot behavior.

## Test signals
Module load/unload, failure injection at each init stage to verify unwind, `nomodeset` and `i915.modeset=0/-1/1` boot cases, selftest failures, and perf sysctl registration cleanup.
