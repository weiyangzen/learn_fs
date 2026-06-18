# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_probe_helper_test.c

## Purpose
KUnit tests for `drm_connector_helper_tv_get_modes()`. The suite verifies analog TV mode enumeration, preferred-mode ordering, and command-line TV mode override behavior for connectors with NTSC and/or PAL support.

## Important APIs, Types, And Functions
`struct drm_probe_helper_test_priv` holds a mock DRM device, mock device, and connector. `drm_probe_helper_test_init()` initializes an atomic-capable DRM device and a managed connector with atomic state funcs. `struct drm_connector_helper_tv_get_modes_test` defines supported TV modes, default mode, optional cmdline override, and expected mode constructors. Macros `TV_MODE_TEST` and `TV_MODE_TEST_CMDLINE` build parameter rows.

## Control Flow
For each parameter, the test optionally marks a command-line TV mode, creates TV mode properties with `drm_mode_create_tv_properties()`, attaches the default property to the connector, locks the mode-config mutex, calls `drm_connector_helper_tv_get_modes()`, counts probed modes, and compares the first two modes against expected constructors. The first expected mode must be preferred; the second, if any, must not.

## State And Persistence
State resides in connector properties, `connector->cmdline_mode`, and `connector->probed_modes`. Expected modes allocated for comparison are destroyed by KUnit actions. No persistent storage exists.

## Dependencies And Integration Points
The test integrates DRM connector state helpers, mode config TV properties, analog TV mode constructors from `drm_modes`, and probe helper mode-list behavior. It complements `drm_modes_test.c` by validating connector-level ordering and preferred flags rather than raw timings.

## Risks And Maintenance Notes
Mode ordering is policy-sensitive: default and command-line overrides intentionally affect the first/preferred mode. Property or cmdline semantics changes can break expectations even if timing generation remains correct. The test currently checks up to two modes because supported cases are NTSC/PAL only.

## Test Signals
Signals include returned mode count, probed mode list length, exact mode equality for preferred and secondary modes, preferred flag only on the first mode, and zero modes when no supported TV modes are configured.
