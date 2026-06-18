# sources/distributed-fs/ceph-client/include/drm/drm_atomic.h

## Purpose
This header defines the core DRM atomic state model: reference-counted commit objects, the aggregate `drm_atomic_state`, per-object old/new state slots for CRTCs, planes, connectors, colorops, private objects, and bridge bus state. It is the central contract between userspace atomic IOCTL assembly, driver atomic check hooks, helper commit sequencing, and nonblocking commit lifetime management.

## Important APIs, types, and functions
Key types are `struct drm_crtc_commit`, `struct drm_atomic_state`, `struct drm_private_obj`, `struct drm_private_state`, `struct drm_private_state_funcs`, `struct drm_bus_cfg`, and `struct drm_bridge_state`. Important APIs allocate, initialize, clear, refcount, and free atomic states; get CRTC, plane, connector, colorop, private-object, and bridge states; add affected objects; run `drm_atomic_check_only`, `drm_atomic_commit`, and `drm_atomic_nonblocking_commit`; and dump state. Iterator macros expose old, new, and old/new state traversal for connectors, CRTCs, planes, colorops, and private objects.

## Control Flow
Atomic users gather mutable state with `drm_atomic_get_*_state`, run checks, then commit either synchronously or through `commit_work`. Helper-backed commits use `drm_crtc_commit` completions to separate hardware programming (`hw_done`), flip/event delivery (`flip_done`), and old-buffer cleanup (`cleanup_done`). After `drm_atomic_helper_swap_state`, object current-state pointers hold the new state while the atomic state retains the old state for disable, cleanup, and destruction paths.

## State and Persistence
The header defines in-memory KMS state only, but that state represents persistent hardware configuration and userspace-visible properties. `state_to_destroy` fields prevent old/new ownership confusion across swap and teardown. Private objects are tied to the DRM device lifetime and carry a modeset lock; shared private state in nonblocking commits must preserve commit ordering to avoid use-after-free.

## Dependencies and Integration Points
It depends on CRTC, plane, connector, encoder, colorop, property, modeset-lock, kref, completion, and bridge concepts. It integrates with `drm_atomic_helper.h`, bridge atomic state, connector writeback fences, userspace out-fences, `drm_mode_config_funcs`, and driver-private atomic extensions.

## Risks and Test Signals
Risk concentrates around state lifetime, stale old/new assumptions after swap, adding unrelated objects without `allow_modeset`, unsafe peeks via `__drm_atomic_get_current_plane_state`, private-object nonblocking ordering, and missed completion signaling. Tests should cover refcounted commit waits, nonblocking commits sharing private state, connector array bounds, old/new iterator behavior, bridge state retrieval, out-fence pointer handling, and modeset-needed calculation for mode, active, connector, and self-refresh transitions.
