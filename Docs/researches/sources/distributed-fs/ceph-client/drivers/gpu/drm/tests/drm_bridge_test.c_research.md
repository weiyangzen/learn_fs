# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_bridge_test.c

## Purpose

`drm_bridge_test.c` provides KUnit coverage for DRM bridge helpers: retrieving current atomic bridge state, resetting an attached CRTC through a bridge for atomic and legacy bridges, and managed bridge allocation lifetime/reference behavior.

## Important APIs, Types, and Functions

- `struct drm_bridge_priv` embeds a bridge at a nonzero offset and tracks enable/disable counts plus private data.
- `struct drm_bridge_init_priv` holds the test DRM device, device-only allocation state, plane, CRTC, encoder, bridge, connector, and destroyed flag.
- `drm_test_bridge_init()` creates a minimal DRM atomic device, allocates a managed bridge, attaches it to an encoder, creates a bridge connector, attaches the connector, and resets mode config.
- `drm_test_drm_bridge_get_current_state_atomic()` commits an atomic bridge state and expects `drm_bridge_get_current_state()` to return it while locked.
- `drm_test_drm_bridge_get_current_state_legacy()` expects NULL for a non-atomic bridge.
- `drm_test_drm_bridge_helper_reset_crtc_*()` verifies reset CRTC power-cycles enabled bridges and fails cleanly for disabled atomic bridges.
- `drm_test_drm_bridge_alloc_basic()` and `_get_put()` verify `devm_drm_bridge_alloc()` destruction and bridge refcounting.

## Control Flow

Common setup allocates a KUnit device/DRM device, creates a plane/CRTC/encoder, allocates a bridge with either legacy or atomic funcs, adds/removes the bridge through KUnit cleanup actions, attaches it, creates a bridge connector, and resets mode config. State tests use atomic state allocation and commit with `-EDEADLK` retry. Reset tests enable a CRTC/connector using a CEA mode, call `drm_bridge_helper_reset_crtc()`, and assert callback counts. Allocation tests use a KUnit device directly and unregister it before or after holding an extra bridge reference.

## State and Persistence Behavior

Enable/disable counters and `destroyed` flag are test-local state. Managed bridge memory persists until the owning KUnit device unregisters and bridge references are dropped. Atomic bridge current state persists after commit until replaced, protected by `bridge->base.lock`.

## Dependencies and Integration Points

The tests depend on DRM bridge, bridge connector, bridge helper, atomic state helper, KUnit device helpers, and DRM KUnit helpers. They validate behavior of `drm_bridge_add/remove`, `drm_bridge_attach`, `drm_bridge_connector_init`, `drm_bridge_get_current_state`, `drm_bridge_helper_reset_crtc`, `devm_drm_bridge_alloc`, and bridge get/put.

## Risks and Edge Cases

- The legacy current-state test intentionally skips locking because non-atomic bridges do not initialize `bridge->base`; that assumption should remain documented if helper behavior changes.
- Reset tests cover one bridge in a simple pipeline, not bridge chains with mixed atomic/legacy behavior.
- Managed allocation tests rely on destroy callbacks firing exactly once when device and refs are released.

## Test Signals

KUnit suites `drm_test_bridge_get_current_state`, `drm_test_bridge_helper_reset_crtc`, and `drm_bridge_alloc` should pass. Signals include state pointer equality for atomic bridges, NULL for legacy current state, enable/disable counts changing from 1/0 to 2/1 on reset, disabled reset returning an error without callbacks, and destruction delayed by an extra bridge ref.
