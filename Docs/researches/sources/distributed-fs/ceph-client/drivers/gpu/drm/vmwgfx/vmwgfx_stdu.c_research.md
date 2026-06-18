# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_stdu.c

Purpose: Implements vmwgfx Screen Target Display Units, the KMS path that maps DRM CRTC/encoder/connector/planes to SVGA guest-backed screen targets and updates them from BO- or surface-backed framebuffers.

Important APIs/types: `struct vmw_screen_target_display_unit`, `struct vmw_stdu_dirty`, `enum stdu_content_type`, DRM function tables, `vmw_kms_stdu_init_display()`, `vmw_kms_stdu_surface_dirty()`, and `vmw_kms_stdu_readback()`.

Control flow: Mode setup blanks/destroys the old target, enables SVGA, and defines a new target at connector GUI coordinates. Plane prepare chooses same-display, proxy-surface, or BO content, creates/pins scanout GB surfaces when needed, and propagates dumb-buffer dirty ranges. Atomic update binds the display surface and emits either CPU blit plus update-image commands or SVGA surface-copy/update commands.

State/persistence: Per-DU state tracks defined target, display surface, content type, dimensions, bytes-per-pixel, and coordinates. Plane state tracks pinned user object and content type. Hardware state persists in SVGA screen-target definitions until blank/destroy.

Dependencies/integration: DRM atomic/damage/vblank, `vmwgfx_vkms`, validation helpers, GB surface allocation, BO CPU blit, cursor plane code, and SVGA FIFO commands.

Risks/test signals: Validate proxy pin balance, mode memory caps, damage propagation for dumb buffers, vkms CRC surface handoff, multi-monitor coordinate changes, disable/blank paths, and low-memory failures.
