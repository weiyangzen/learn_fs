## sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/tests/Makefile

### Purpose

This Makefile builds the DRM scheduler KUnit test module.

### Important APIs, Types, and Functions

There are no runtime APIs. `drm-sched-tests-y` combines `mock_scheduler.o` and `tests_basic.o`; `obj-$(CONFIG_DRM_SCHED_KUNIT_TEST)` emits `drm-sched-tests.o`.

### Control Flow

Kbuild includes the test object only when scheduler KUnit testing is enabled. The parent scheduler Makefile descends into this directory under the same config.

### State and Persistence Behavior

The file has no runtime state. Its persistent build effect is making mock scheduler infrastructure and basic tests available to KUnit.

### Dependencies and Integration Points

It depends on Kbuild, `CONFIG_DRM_SCHED_KUNIT_TEST`, and the source files named in `drm-sched-tests-y`. It integrates with the parent DRM scheduler build and the kernel KUnit runner.

### Risks and Edge Cases

Adding a new test source without listing it here leaves it unbuilt. If the config is enabled without required scheduler/KUnit dependencies, the build will fail elsewhere. Whitespace uses continuation lines, so future edits need normal Kbuild syntax.

### Test Signals

Signals are successful KUnit builds and execution of the DRM scheduler test suite, especially mock scheduler and basic scheduling tests.
