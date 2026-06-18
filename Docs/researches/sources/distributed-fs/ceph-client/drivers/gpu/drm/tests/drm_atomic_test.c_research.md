# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_atomic_test.c

## Purpose

`drm_atomic_test.c` provides a focused KUnit test for `drm_atomic_get_connector_for_encoder()`, verifying that an enabled encoder can be resolved back to its currently attached connector through atomic state and modeset locking.

## Important APIs, Types, and Functions

- `struct drm_atomic_test_priv` embeds a test DRM device, primary plane, CRTC, encoder, and connector.
- `create_device()` creates the minimal DRIVER_MODESET/DRIVER_ATOMIC test device, plane, CRTC, encoder, connector, helper hooks, attachment, and mode-config reset.
- `drm_test_drm_atomic_get_connector_for_encoder()` enables the CRTC/connector on a CEA VIC 16 mode and then calls `drm_atomic_get_connector_for_encoder()`.

## Control Flow

The test allocates a KUnit DRM device, obtains a 1080p CEA mode, initializes a modeset acquire context, enables the CRTC/connector with retry on `-EDEADLK`, drops/finalizes locks, creates a fresh acquire context, calls `drm_atomic_get_connector_for_encoder()` with retry on `-EDEADLK`, and expects the returned connector pointer to equal the test connector.

## State and Persistence Behavior

All state is KUnit-scoped. DRM managed objects are reset through `drm_mode_config_reset()`. The enabled connector/encoder state persists only for the lifetime of the test case.

## Dependencies and Integration Points

It depends on DRM atomic, atomic state helpers, atomic UAPI, encoder, KUnit helpers, and modeset helper vtables. It tests the DRM core atomic helper's ability to inspect current committed state under proper locking.

## Risks and Edge Cases

The test covers one encoder and one connector only. It does not test disconnected connectors, multiple connectors, disabled encoders, clone mode, or error cases beyond deadlock retry. Future changes to helper locking need to preserve the acquire-context retry pattern.

## Test Signals

The `drm_test_atomic_get_connector_for_encoder` KUnit suite should pass and return the exact connector pointer after an enabled atomic commit.
