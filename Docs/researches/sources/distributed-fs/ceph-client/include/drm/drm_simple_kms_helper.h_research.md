# sources/distributed-fs/ceph-client/include/drm/drm_simple_kms_helper.h

## Purpose
`drm_simple_kms_helper.h` declares the deprecated simple display pipe helpers that combine a CRTC, primary plane, encoder, and optional connector for very simple KMS drivers.

## Important APIs, types, and functions
`struct drm_simple_display_pipe_funcs` supplies callbacks for mode validation, enable/disable, atomic check/update, framebuffer prepare/cleanup/access, vblank enable/disable, and optional CRTC/plane state reset/duplicate/destroy hooks. `struct drm_simple_display_pipe` embeds `drm_crtc`, `drm_plane`, `drm_encoder`, connector pointer, and funcs pointer. APIs include `drm_simple_display_pipe_attach_bridge`, `drm_simple_display_pipe_init`, `drm_simple_encoder_init`, `__drmm_simple_encoder_alloc`, and `drmm_simple_encoder_alloc`.

## Control flow
A simple driver initializes the pipe with formats, modifiers, connector, and callbacks. Atomic helper paths call pipe callbacks to validate modes, prepare framebuffer access, enable or update scanout, and clean up. Bridge attachment wires the simple encoder path into bridge chains.

## State and persistence
State is embedded in the DRM objects that make up the pipe plus driver-private container data. It persists for the DRM device lifetime but does not survive unload/reprobe.

## Dependencies and integration points
It depends on DRM CRTC, encoder, and plane definitions. It integrates with atomic helpers, bridges, connectors, vblank helpers, and managed DRM allocation for simple encoders.

## Risks and test signals
Risks include using a deprecated helper for new complex hardware, insufficient atomic validation, framebuffer access callbacks mismatched with panic or dynamic buffer management, missing vblank hooks, and bridge/connector ownership confusion. Test signals include simple pipe init, bridge attach, enable/update/disable commits, framebuffer prepare/cleanup balance, vblank enable/disable, and managed encoder cleanup.
