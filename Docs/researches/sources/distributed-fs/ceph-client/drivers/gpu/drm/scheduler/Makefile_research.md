## sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/Makefile

### Purpose

This Makefile builds the DRM GPU scheduler library object and conditionally descends into the KUnit test directory. It is the Kbuild entry point for scheduler core code shared by DRM drivers.

### Important APIs, Types, and Functions

There are no C APIs. `gpu-sched-y` aggregates `sched_main.o`, `sched_fence.o`, and `sched_entity.o` into the composite `gpu-sched.o`. `obj-$(CONFIG_DRM_SCHED)` includes the scheduler library when enabled, and `obj-$(CONFIG_DRM_SCHED_KUNIT_TEST)` includes `tests/`.

### Control Flow

Kbuild evaluates configuration symbols. If `CONFIG_DRM_SCHED=y` or `m`, the three core objects are linked into `gpu-sched.o`. If scheduler KUnit testing is enabled, the `tests` subdirectory is visited.

### State and Persistence Behavior

The file has no runtime state. Its persistent effect is build composition: exported symbols from the scheduler objects become available to DRM drivers only when the config selects this target.

### Dependencies and Integration Points

It integrates with Linux Kbuild, `CONFIG_DRM_SCHED`, `CONFIG_DRM_SCHED_KUNIT_TEST`, and the scheduler test Makefile.

### Risks and Edge Cases

Forgetting to add a new scheduler compilation unit here causes unresolved symbols or missing functionality. Enabling tests without the core scheduler config would be an invalid build setup unless guarded by Kconfig dependencies. License comments are inherited from the original AMD scheduler code while test files use SPDX in their subdirectory.

### Test Signals

Signals are successful allmodconfig/allyesconfig builds, module linkage when `CONFIG_DRM_SCHED=m`, and KUnit target discovery when `CONFIG_DRM_SCHED_KUNIT_TEST=y`.
