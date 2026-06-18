# sources/distributed-fs/ceph-client/include/drm/drm_kunit_helpers.h

Purpose: declares KUnit helpers for constructing lightweight DRM devices and modeset objects in tests without requiring a full hardware driver.

Important APIs and types: device helpers allocate and free mock parent devices. `__drm_kunit_helper_alloc_drm_device_with_driver()` allocates a DRM device embedded at a caller-specified offset in a test container type using a supplied `drm_driver`. The `drm_kunit_helper_alloc_drm_device_with_driver()` macro provides type-safe container recovery. `__drm_kunit_helper_alloc_drm_device()` creates a managed test `drm_driver` from feature bits, and `drm_kunit_helper_alloc_drm_device()` wraps it. Additional helpers allocate atomic state, create primary planes and CRTCs, enable a CRTC/connector pair with a mode, register mode destruction actions, and build display modes from CEA VICs.

Control flow: tests allocate a parent `struct device`, allocate an embedded DRM device through devm-managed allocation, then create planes, CRTCs, connectors, modes, and atomic state. KUnit assertions inside inline allocation helpers fail the test immediately if a mock driver allocation fails.

State and persistence behavior: all resources are scoped to the KUnit test and/or devm lifetime of the mock parent device. Mode destruction can be registered as a KUnit cleanup action. The helpers intentionally keep state local to test contexts.

Dependencies and integration points: depends on KUnit, Linux device management, `drm_drv.h`, DRM atomic state, plane/CRTC/helper vtables, connector objects, and display mode helpers. It is an integration point for DRM unit tests that need realistic object initialization.

Risks: helper macros rely on correct container type/member/offset arguments. Feature-bit-only mock drivers may omit callbacks that tested code assumes exist. Tests must pair helper-created modes and atomic states with cleanup actions to avoid leaks detected by KUnit.

Test signals: KUnit suites using managed DRM device allocation, object construction failure paths, atomic state allocation, CRTC/connector enabling, CEA VIC conversion, and leak-free cleanup at test teardown.
