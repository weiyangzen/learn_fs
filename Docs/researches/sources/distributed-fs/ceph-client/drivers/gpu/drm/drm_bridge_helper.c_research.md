# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_bridge_helper.c

## Purpose
`drm_bridge_helper.c` provides a bridge helper to reset the active CRTC pipeline feeding a bridge by wrapping `drm_atomic_helper_reset_crtc()`.

## Important APIs, Types, And Functions
The sole exported function is `drm_bridge_helper_reset_crtc(struct drm_bridge *bridge, struct drm_modeset_acquire_ctx *ctx)`. It uses `bridge->encoder`, `drm_atomic_get_connector_for_encoder()`, `connector->state->crtc`, and `drm_atomic_helper_reset_crtc()`.

## Control Flow
The helper locks `dev->mode_config.connection_mutex`, finds the connector associated with the bridge encoder, validates connector state, extracts the active CRTC, calls the atomic CRTC reset helper, unlocks, and returns the result. `-EDEADLK` is intentionally propagated for full atomic retry by the caller.

## State And Persistence
It owns no persistent state. It temporarily holds the connection mutex and triggers atomic helper state changes for the connected pipeline.

## Dependencies And Integration Points
It depends on DRM bridge, atomic connector lookup, modeset locks, and atomic helper reset code. Bridge drivers or pipeline recovery paths call it when an upstream CRTC path must be reset.

## Risks And Edge Cases
The function assumes an attached bridge with a valid encoder. Missing connector, missing connector state, or reset helper errors propagate. Callers must handle `-EDEADLK` correctly.

## Test Signals
Test attached reset success, no connector, connector without state, lock-deadlock retry signaling, and propagation of reset helper failures.
