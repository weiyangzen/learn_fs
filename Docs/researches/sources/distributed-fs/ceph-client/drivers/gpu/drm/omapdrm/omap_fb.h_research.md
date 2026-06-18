# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_fb.h

Purpose: Declares the OMAP DRM framebuffer API used by mode config, planes, fbdev, and debugfs.

Important APIs/functions: Creation/init APIs build framebuffers from userspace file handles or existing GEM objects. Pin/unpin APIs prepare buffers for scanout. `omap_framebuffer_update_scanout()` converts framebuffer and plane state into one or two `omap_overlay_info` structures. `omap_framebuffer_supports_rotation()` reports TILER-backed rotation support. `omap_framebuffer_describe()` emits debugfs information.

Control flow: Main mode config uses `omap_framebuffer_create()` as `fb_create`; fbdev uses `omap_framebuffer_init()` around its BO; plane code pins and updates scanout; debugfs calls describe.

State and persistence: No state is stored in the header; framebuffer state is private to `omap_fb.c`.

Dependencies/integration: Forward-declares DRM, GEM, plane state, overlay info, and seq_file types. Included by `omap_drv.h` for broad driver use.

Risks and test signals: API callers must pin before using scanout DMA addresses and unpin when done. Build coverage plus plane/fbdev scanout tests validate the contract.
