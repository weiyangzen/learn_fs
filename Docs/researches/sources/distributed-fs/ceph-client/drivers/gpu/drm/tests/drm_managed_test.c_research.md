# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_managed_test.c

## Purpose
KUnit tests for DRM managed action lifetime behavior. The suite verifies both explicit `drmm_release_action()` execution and automatic action execution when a DRM device is unregistered and its parent mock device is freed.

## Important APIs, Types, And Functions
`struct managed_test_priv` stores the mock `drm_device`, an `action_done` flag, and a waitqueue. `drm_action()` is the managed callback that sets the flag and wakes waiters. `drm_test_managed_release_action()` registers, explicitly releases, waits, and unregisters. `drm_test_managed_run_action()` registers and relies on device teardown to run the action. `drm_managed_test_init()` allocates the KUnit mock device and DRM device through `drm_kunit_helpers`.

## Control Flow
Each test registers `drm_action` with `drmm_add_action_or_reset()`, registers the DRM device, then triggers the action either explicitly or by `drm_dev_unregister()` plus `drm_kunit_helper_free_device()`. A waitqueue timeout of 100 ms bounds the assertion that the action was observed.

## State And Persistence
State is transient in `managed_test_priv`. The comment notes that the DRM device cannot be embedded in `priv` because the action flag must outlive the DRM/device release sequence. No persistent storage exists.

## Dependencies And Integration Points
The suite integrates DRM managed resource APIs, DRM device registration, the KUnit helper mock device, Linux waitqueues, and KUnit resource allocation. It exercises the action path used by DRM drivers to bind cleanup to `drm_device` lifetime.

## Risks And Maintenance Notes
The 100 ms timeout is intentionally small and can be fragile on very slow KUnit environments. Incorrect lifetime changes in DRM managed cleanup could either skip the action or free backing memory before the wait observes completion. Manual mock-device freeing inside tests must stay aligned with KUnit auto-cleanup semantics to avoid double cleanup.

## Test Signals
Passing signals are zero return from `drmm_add_action_or_reset()` and `drm_dev_register()`, positive waitqueue timeout return after action execution, and no teardown crash. Failing signals include timed-out wait, registration errors, or cleanup lifetime assertions.
