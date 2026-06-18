# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/Makefile

## Purpose

`vc4/Makefile` defines the VC4 driver object composition and conditionally includes debugfs and KUnit test files.

## Important APIs, Types, and Functions

- `vc4-y`: sorted list of core driver objects, including BO, CRTC, KMS, HDMI, HVS, IRQ, perfmon, plane, render validation, trace, TXP, V3D bridge, and validation code.
- `vc4-$(CONFIG_DRM_VC4_KUNIT_TEST)`: adds mock helpers and pixel-valve muxing tests.
- `vc4-$(CONFIG_DEBUG_FS)`: adds `vc4_debugfs.o`.
- `obj-$(CONFIG_DRM_VC4) += vc4.o`: builds the composite driver.

## Control Flow

Kbuild compiles the listed files into one module/built-in object according to configuration. KUnit tests become part of the driver object only when the test option is enabled.

## State and Persistence Behavior

No runtime state. Link composition determines which init/test symbols are present.

## Dependencies and Integration Points

The file must stay synchronized with Kconfig and internal symbol references. The test entries depend on production VC4 symbols and DRM KUnit helper availability.

## Risks and Edge Cases

Forgetting to add a new source file causes link failures or missing functionality. Since tests are linked into the main object, test-only code must remain guarded by Kconfig.

## Test Signals

Build `CONFIG_DRM_VC4` with and without debugfs and KUnit, verify object lists resolve, and run KUnit suites when enabled.
