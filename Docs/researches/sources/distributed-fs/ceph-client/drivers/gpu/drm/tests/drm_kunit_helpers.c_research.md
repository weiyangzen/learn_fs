# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_kunit_helpers.c

## Purpose
Shared helper library for DRM KUnit tests. It creates mock devices, DRM devices, atomic states, primary planes, CRTCs, connector enable commits, and auto-destroyed display modes so individual DRM tests can exercise real DRM helper code without a hardware driver.

## Important APIs, Types, And Functions
`drm_kunit_helper_alloc_device()` and `drm_kunit_helper_free_device()` wrap KUnit mock device registration. `__drm_kunit_helper_alloc_drm_device_with_driver()` allocates a DRM device with a supplied driver and initializes mode config with atomic helper config funcs. `drm_kunit_helper_atomic_state_alloc()` allocates a `drm_atomic_state`, attaches the acquire context, and registers a KUnit cleanup action. `drm_kunit_helper_create_primary_plane()` and `drm_kunit_helper_create_crtc()` build managed mock plane/CRTC objects with default atomic funcs when callbacks are omitted. `drm_kunit_helper_enable_crtc_connector()` performs a real atomic commit enabling a CRTC/connector route. `drm_kunit_add_mode_destroy_action()` and `drm_kunit_display_mode_from_cea_vic()` manage display-mode lifetimes.

## Control Flow
Device allocation flows through KUnit device resources and `__devm_drm_dev_alloc()`, followed by `drmm_mode_config_init()`. Plane/CRTC creation chooses default formats/modifiers/callbacks when callers pass `NULL`, then uses DRM managed allocation/initialization and helper attachment. Connector enablement allocates atomic state, gets connector and CRTC states, sets CRTC routing and mode, marks the CRTC enabled/active, and commits.

## State And Persistence
All state is test-scoped and managed by KUnit or DRMM actions. Atomic states are reference-counted and released by cleanup callbacks. Display modes created for tests are destroyed by KUnit actions. No persistent storage is used.

## Dependencies And Integration Points
The file exports GPL symbols consumed by many DRM KUnit suites. It depends on DRM atomic, managed device allocation, EDID/mode helpers, KUnit resources, KUnit mock devices, and platform-device support. Its default mode-config funcs wire mock devices into standard `drm_atomic_helper_check()` and `drm_atomic_helper_commit()`.

## Risks And Maintenance Notes
Mock defaults must stay compatible with DRM helper assumptions. A notable maintenance hazard is `drm_kunit_helper_create_primary_plane()` passing `default_plane_modifiers` to `__drmm_universal_plane_alloc()` even when a custom `modifiers` argument is supplied, which means custom modifiers would be ignored unless fixed. Assertions inside helper constructors abort tests on allocation/init failures, so helper changes can affect many suites at once.

## Test Signals
Signals are mostly downstream: tests should be able to allocate devices, create planes/CRTCs, enable connector routes, and clean resources without leaks or stale refs. Direct failure signals are KUnit assertions on allocation/init, atomic commit return codes, and mode-destroy action registration results.
