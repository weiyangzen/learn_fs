# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/sysfs_engines.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/sysfs_engines.h

### Purpose
`sysfs_engines.h` declares the i915 engine sysfs registration entry point.

### Important APIs, Types, And Functions
It forward-declares `struct drm_i915_private` and declares `intel_engines_add_sysfs(struct drm_i915_private *i915)`.

### Control Flow
There is no runtime flow; the include guard protects the declaration.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
It owns no state. It integrates GT/device setup code with `sysfs_engines.c`. Risks are limited to declaration mismatch. Compile-time users provide the test signal.
