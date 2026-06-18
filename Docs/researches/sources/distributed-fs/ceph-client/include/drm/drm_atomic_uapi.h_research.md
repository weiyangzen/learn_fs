# sources/distributed-fs/ceph-client/include/drm/drm_atomic_uapi.h

## Purpose
This header declares the small API used to mutate atomic state in ways that mirror userspace-visible KMS relationships: CRTC mode, plane CRTC/framebuffer/color pipeline attachment, and connector CRTC routing.

## Important APIs, types, and functions
The exported functions are `drm_atomic_set_mode_for_crtc`, `drm_atomic_set_mode_prop_for_crtc`, `drm_atomic_set_crtc_for_plane`, `drm_atomic_set_fb_for_plane`, `drm_atomic_set_colorop_for_plane`, and `drm_atomic_set_crtc_for_connector`. They update object state while maintaining references and derived fields expected by the atomic core.

## Control Flow
Users of this API first acquire the relevant object state through `drm_atomic_get_*_state`, then call setters to change relationships. The full transaction is later validated by atomic check hooks and committed or rolled back by the atomic core.

## State and Persistence
The setters modify only the pending atomic state. Effects become persistent hardware and userspace-visible state only if the containing `drm_atomic_state` commits successfully. Framebuffer and mode property setters must manage object references correctly across replacement and abort paths.

## Dependencies and Integration Points
It integrates with CRTC mode blobs, display modes, plane framebuffers, colorop pipelines, connector routing, and the atomic IOCTL/property decoding layer.

## Risks and Test Signals
Risks include direct field mutation by drivers bypassing reference management, mode-blob lifetime mistakes, connector/plane CRTC mismatches, and colorop assignment without adding affected colorops. Tests should cover replacing modes and framebuffers repeatedly, disabling planes and connectors by setting NULL, aborting after setters, and validating that getters/reporting reflect the pending state only after commit.
