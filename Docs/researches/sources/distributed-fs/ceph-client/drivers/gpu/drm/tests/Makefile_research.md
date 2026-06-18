# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/Makefile

## Purpose

This Makefile lists DRM KUnit test objects built when DRM KUnit configuration options are enabled. It wires helper tests and a broad set of DRM core/helper unit tests into the kernel build.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_DRM_KUNIT_TEST_HELPERS)` builds `drm_kunit_helpers.o`.
- `obj-$(CONFIG_DRM_KUNIT_TEST)` builds atomic, bridge, connector, damage, DP MST, exec, format, framebuffer, GEM shmem, HDMI state, managed, MM, modes, plane/probe helper, rect, sysfb, and fixed-point tests.
- `CFLAGS_drm_mm_test.o := $(DISABLE_STRUCTLEAK_PLUGIN)` disables structleak plugin for the DRM MM test object.

## Control Flow

There is no runtime control flow. Kbuild evaluates the configuration symbols and compiles the listed objects into the relevant test module/built-in target.

## State and Persistence Behavior

No persistent runtime state is owned here. The file controls build inclusion of test objects.

## Dependencies and Integration Points

It integrates with Linux Kbuild, DRM KUnit configuration options, and source files in the same tests directory. The test source files in this work item are included through the `CONFIG_DRM_KUNIT_TEST` object list.

## Risks and Edge Cases

Adding a test source without listing it here leaves it unbuilt. Removing or renaming an object breaks configured builds. Per-object CFLAGS should stay narrowly scoped because they alter compiler hardening behavior.

## Test Signals

`make`/KUnit builds with `CONFIG_DRM_KUNIT_TEST=y/m` and `CONFIG_DRM_KUNIT_TEST_HELPERS=y/m` should include all listed test suites. Build logs should show `drm_mm_test.o` compiled with structleak disabled only for that object.
