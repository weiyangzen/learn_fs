# sources/distributed-fs/ceph-client/include/drm/drm_dumb_buffers.h

Purpose: Declares the helper for calculating legacy dumb-buffer pitch and size according to hardware pitch and allocation alignment requirements.

Important APIs, types, and functions: Exposes `drm_mode_size_dumb(struct drm_device *dev, struct drm_mode_create_dumb *args, unsigned long hw_pitch_align, unsigned long hw_size_align)`.

Control flow: A driver's `dumb_create` path can call this helper to validate and fill `pitch` and `size` in the userspace `drm_mode_create_dumb` request before allocating backing memory with GEM, TTM, DMA, VRAM, or another allocator.

State and persistence: No state is stored here. The helper contributes to userspace-visible buffer metadata returned by dumb-buffer IOCTLs.

Dependencies and integration points: Integrates with `struct drm_driver.dumb_create`, `struct drm_mode_create_dumb`, and the DRM device. It is typically used by simple display drivers or storage-specific dumb create helpers.

Risks and test signals: Risks include overflow in width/height/bpp multiplication, insufficient alignment for hardware scanout, and ABI-visible pitch/size mismatches. Test minimum and maximum dimensions, unusual depths/bpps, alignment boundaries, overflow rejection, and framebuffer creation from returned dumb buffers.
