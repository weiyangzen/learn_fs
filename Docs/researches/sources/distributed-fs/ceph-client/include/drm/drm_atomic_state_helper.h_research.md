# sources/distributed-fs/ceph-client/include/drm/drm_atomic_state_helper.h

## Purpose
This header declares default reset, duplicate, and destroy helpers for atomic CRTC, plane, connector, private-object, and bridge state. It lets drivers subclass state structures while reusing the core copy/reset/destruction semantics for common fields.

## Important APIs, types, and functions
The CRTC APIs are `__drm_atomic_helper_crtc_state_reset`, `__drm_atomic_helper_crtc_reset`, `drm_atomic_helper_crtc_reset`, duplicate helpers, and destroy helpers. Plane and connector sections mirror this pattern, with TV-specific connector reset/check/margin helpers. Private object helpers initialize and duplicate base private state. Bridge helpers duplicate, destroy, and reset `drm_bridge_state`.

## Control Flow
Drivers call the double-underscore helpers when they allocate a subclassed state and need the base portion initialized or copied. Non-underscored helpers are suitable as direct vtable hooks for drivers that do not add private fields. Destroy helpers release common references held by state before driver-specific cleanup completes.

## State and Persistence
The state is transient atomic KMS state, but it owns references to persistent objects such as framebuffers, property blobs, writeback jobs, and connector/bridge state. Correct duplication and destruction determine whether aborted atomic checks, failed commits, and hot-unplug paths leak or use freed resources.

## Dependencies and Integration Points
It connects the object vtables in CRTC, plane, connector, private-object, and bridge definitions to the atomic core declared in `drm_atomic.h`. It is used by drivers implementing `atomic_duplicate_state`, `atomic_destroy_state`, and reset callbacks.

## Risks and Test Signals
Main risks are subclass drivers forgetting to call base duplicate/destroy helpers, copying stale pointers without taking references, TV connector defaults not being reset, and bridge atomic hooks lacking a valid reset state. Tests should force allocation failure during duplicate, abort atomic checks, reset objects during mode-config reset, exercise TV margin/property validation, and hot-unplug connectors or bridges with pending duplicated states.
