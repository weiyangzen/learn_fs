<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_display.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_display.c

## Purpose
`virtgpu_display.c` implements VirtIO GPU KMS display objects: CRTCs, connectors, encoders, framebuffers, mode discovery/validation, scanout setup, and modeset initialization/finalization.

## Important APIs, Types, and Functions
Important public functions are `virtio_gpu_modeset_init()` and `virtio_gpu_modeset_fini()`. Internal callbacks cover CRTC mode set/enable/disable/flush, connector modes/detect/destroy, encoder no-ops, `vgdev_output_init()`, `virtio_gpu_framebuffer_init()`, and `virtio_gpu_user_framebuffer_create()`.

## Control Flow
Modeset init initializes mode_config, sets host-byte-order fb quirk, bounds modes to 32..8192, disables modifiers, creates output objects for each scanout, initializes vblank, and resets mode config. Each output gets primary/cursor planes, CRTC, connector, optional EDID property, virtual encoder, and default enabled 1024x768 info for output 0. Connector modes prefer EDID; otherwise they add generic modes and a preferred CVT mode matching host display info. CRTC flush marks modeset-needed and arms/sends vblank events. Plane update code performs actual scanout commands.

## State and Persistence Behavior
Persistent state is `virtio_gpu_output` per scanout, connector EDID, CRTC/encoder/connector/plane objects, and mode_config. `needs_modeset` bridges CRTC flush to plane update. Framebuffers own GEM references until destroyed.

## Dependencies and Integration Points
The file depends on DRM atomic, EDID, fb, vblank, simple KMS helpers, VirtIO GPU commands from `virtgpu_vq.c`, and planes from `virtgpu_plane.c`.

## Risks
`virtio_gpu_user_framebuffer_create()` returns `NULL` rather than `ERR_PTR(ret)` on framebuffer init failure, which is unusual for `fb_create`. Connector init/register return values are not all checked. Modeset and plane update are coupled because the protocol cannot fully separate them. Preferred-mode filtering is heuristic around host-provided dimensions.

## Test Signals
KMS tests should cover EDID and no-EDID modes, hotplug display-info updates, vblank events, addfb format restrictions, multi-scanout initialization, output disable scanout clearing, and framebuffer failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_display.c -->
