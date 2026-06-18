# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_atomic_uapi.c

## Purpose
`drm_atomic_uapi.c` is the marshalling layer between DRM atomic userspace APIs and kernel atomic state. It implements atomic property get/set, the `DRM_IOCTL_MODE_ATOMIC` ioctl, explicit fencing, DPMS compatibility, and helper setters used by legacy paths and drivers constructing atomic updates internally.

## Important APIs, Types, and Functions
Exported setters include `drm_atomic_set_mode_for_crtc()`, `drm_atomic_set_mode_prop_for_crtc()`, `drm_atomic_set_crtc_for_plane()`, `drm_atomic_set_fb_for_plane()`, `drm_atomic_set_colorop_for_plane()`, and `drm_atomic_set_crtc_for_connector()`. Property dispatch is split across CRTC, plane, connector, and colorop set/get helpers. `drm_atomic_set_property()` is the central typed setter; `drm_atomic_get_property()` is the exported getter. `drm_mode_atomic_ioctl()` parses the userspace ioctl arrays and chooses check-only, blocking commit, or nonblocking commit. Explicit fence handling uses `struct drm_out_fence_state`, `setup_out_fence()`, `prepare_signaling()`, and `complete_signaling()`.

## Control Flow
The ioctl rejects unsupported devices, clients without atomic capability, bad flags, unsupported async flips, reserved fields, and invalid test-only/event combinations. It allocates an atomic state, initializes a modeset acquire context, parses object/property/value arrays from userspace, validates property values, obtains typed object states, and applies properties. It then prepares events/out-fences, marks async flips if requested, calls check-only or commit, handles `-EDEADLK` by clearing state and retrying after lock backoff, and finally installs or cancels fences/events.

CRTC mode setters replace mode blobs and update `enable`. Plane and connector CRTC setters update CRTC masks and references. Plane setters handle framebuffer lookup, input fences, rectangles, alpha/blend/rotation/zpos/color/damage/scaling/hotspot properties. Connector setters handle CRTC routing, TV, link-status, HDR, content protection, HDCP type, writeback, max BPC, privacy screen, colorspace, and driver properties.

## State and Persistence Behavior
This file mutates staged atomic state, not live object state. References to framebuffers, blobs, fences, writeback jobs, connectors, and sync files are owned by that staged state until commit or cleanup. OUT_FENCE_PTR is pessimistically written with `-1` first and replaced by a real FD only after a sync file is created and the ioctl succeeds. Writeback FB/out-fence properties are one-shot from userspace's perspective. Link-status and content-protection enforce special rules: userspace cannot downgrade GOOD to BAD or set content protection directly to ENABLED.

## Dependencies and Integration Points
The file integrates the DRM ioctl layer, mode objects and properties, atomic state core, framebuffer lookup, sync_file/DMA fence, event reservation, vblank events, writeback connectors, colorop/color pipeline infrastructure, property blobs, and modeset lock backoff. Drivers integrate through standard object properties plus optional `atomic_set_property`/`atomic_get_property` hooks and plane `atomic_async_check`.

## Risks
This is a userspace boundary, so pointer, FD, and reference handling are security-sensitive. Mistakes can leak FDs, expose inaccessible objects, mishandle failed out-fences, or corrupt staged state. Async-flip restrictions must remain tight because the path does not permit arbitrary modeset or geometry changes. Blob-size validation must match each property exactly, especially color LUT/CTM, HDR metadata, damage clips, and colorop data. Historical behavior for DPMS, link-status, and content protection is compatibility-sensitive.

## Test Signals
Primary signals are IGT atomic UAPI tests for capability gating, invalid flags, property values, blob sizes, object permissions, test-only, nonblocking commits, async flips, in/out fences, writeback, event delivery, and `-EDEADLK` retries. Additional signals include FD-leak checks on failing commits, compositor atomic modesetting, Android explicit-sync workloads, HDR/color-management tests, and KASAN/KMSAN runs against malformed user arrays.
