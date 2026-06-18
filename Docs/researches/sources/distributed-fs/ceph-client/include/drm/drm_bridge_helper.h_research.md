# sources/distributed-fs/ceph-client/include/drm/drm_bridge_helper.h

## Purpose
This header declares a bridge helper for resetting the CRTC associated with a bridge pipeline. It provides a narrow bridge-to-modeset utility for recovery or disable paths.

## Important APIs, types, and functions
The only function is `drm_bridge_helper_reset_crtc(struct drm_bridge *bridge, struct drm_modeset_acquire_ctx *ctx)`.

## Control Flow
Callers pass a bridge and modeset acquire context; the implementation locates the related pipeline/CRTC and performs a reset through normal modeset locking rules.

## State and Persistence
No state is declared here. Any persistent effect is a CRTC state/hardware reset performed by the implementation through KMS helpers.

## Dependencies and Integration Points
It depends on bridge objects and modeset acquire contexts. It integrates bridge drivers with core CRTC reset behavior while respecting modeset lock acquisition.

## Risks and Test Signals
Risks include deadlocks from incorrect acquire context use, resets on detached bridges, and failure to handle bridges without an active CRTC. Tests should cover reset on active and inactive pipelines, bridge detach during reset, ww-mutex retry paths, and error propagation when the CRTC cannot be acquired.
