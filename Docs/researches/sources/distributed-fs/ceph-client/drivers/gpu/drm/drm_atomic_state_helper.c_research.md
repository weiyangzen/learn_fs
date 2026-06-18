# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_atomic_state_helper.c

## Purpose
`drm_atomic_state_helper.c` provides default reset, duplicate, destroy, and validation helpers for DRM atomic per-object state. Drivers use these as default CRTC, plane, connector, bridge, and private-object state hooks, or call the underscored helpers when subclassing core DRM state.

## Important APIs, Types, and Functions
CRTC helpers include `__drm_atomic_helper_crtc_state_reset()`, `__drm_atomic_helper_crtc_reset()`, `drm_atomic_helper_crtc_reset()`, duplicate helpers, and destroy helpers. Plane helpers initialize and manage rotation, alpha, blend mode, color encoding/range, zpos, color pipeline, cursor hotspots, framebuffers, fences, commits, and damage clips. Connector helpers reset, duplicate, destroy, and validate connector state, including TV margins/modes, HDR metadata, writeback jobs, connector refs, and commits. Private object and bridge helpers initialize/duplicate default `drm_private_state` and `drm_bridge_state`.

## Control Flow
Reset hooks allocate or install fresh zeroed state and seed default values. Duplicate hooks shallow-copy current state and then fix ownership by incrementing references and clearing transient fields such as fences, commits, events, writeback jobs, and change flags. Destroy hooks release every resource the state owns. TV check compares old/new connector TV fields and marks CRTC `mode_changed` or `connectors_changed` so the modeset path is used when required.

## State and Persistence Behavior
The helpers manage persistent `->state` pointers and temporary duplicate states inside `struct drm_atomic_state`. Defaults include opaque black CRTC background, rotate-0, opaque alpha, premultiplied blend mode, property-defined color encoding/range, zpos, normalized_zpos, and cursor hotspot values. Writeback jobs are one-shot and are intentionally not copied. Self-refresh active state is canceled in duplicated CRTC state so new updates wake the pipeline.

## Dependencies and Integration Points
The file depends on DRM atomic core, properties, connectors, CRTCs, planes, bridges, framebuffers, writeback, vblank, blend constants, DMA fences, and allocation helpers. It is used by the atomic commit path in `drm_atomic_helper.c` and by UAPI property handling in `drm_atomic_uapi.c`, which mutates the fields initialized and released here.

## Risks
The main risk is lifetime imbalance for blobs, framebuffers, connector refs, fences, writeback jobs, and commit objects. Because duplicate helpers use `memcpy()`, every new pointer field in a DRM state structure must be audited here. Changing reset defaults can break userspace-visible ABI. Drivers with subclassed state must extend the underscored helpers correctly or they can leak private allocations.

## Test Signals
Useful signals include successful `drm_mode_config_reset()`, IGT atomic property tests, suspend/resume using duplicated state, connector TV property modeset behavior, writeback job one-shot behavior, kmemleak cleanliness, and KASAN/KFENCE coverage over repeated commits, commit aborts, and device teardown.
