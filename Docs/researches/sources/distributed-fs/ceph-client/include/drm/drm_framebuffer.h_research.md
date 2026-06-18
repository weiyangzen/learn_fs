# sources/distributed-fs/ceph-client/include/drm/drm_framebuffer.h

Purpose: Defines DRM framebuffer objects, framebuffer callbacks, refcount helpers, list iteration, and AFBC framebuffer specialization used by KMS planes and userspace framebuffer IOCTLs.

Important APIs, types, and functions: Defines `struct drm_framebuffer_funcs`, `DRM_FRAMEBUFFER_HAS_HANDLE_REF()`, `struct drm_framebuffer`, `obj_to_fb()`, init/lookup/remove/cleanup/unregister APIs, `drm_framebuffer_get()`, `drm_framebuffer_put()`, `drm_framebuffer_read_refcount()`, `drm_framebuffer_assign()`, `drm_for_each_fb()`, `struct drm_afbc_framebuffer`, and `fb_to_afbc_fb()`. Framebuffer fields include device, mode object base/refcount, allocating process name, format, callbacks, per-plane pitches/offsets, modifier, dimensions, flags, internal flags, per-file list entry, and optional GEM backing objects.

Control flow: A driver's `fb_create` path validates a mode command, initializes a framebuffer, attaches backing storage, and registers it on the mode-config framebuffer list. Userspace and planes look up framebuffers by object ID; asynchronous scanout paths take references until hardware is done; removal unregisters userspace visibility before final put; destroy callbacks release backing objects and call core cleanup. Dirty callbacks allow userspace to signal changed regions.

State and persistence: Framebuffers are runtime KMS objects. They persist while referenced by userspace files, planes, commits, or drivers, and are released through refcounting. No disk persistence exists, but object IDs, format/modifier/pitch/offset metadata, and dirty semantics are userspace ABI state.

Dependencies and integration points: Depends on DRM FourCC format info, mode objects, files, GEM objects, clip rects, mode config framebuffer locks, plane state, and framebuffer creation callbacks. AFBC specialization integrates with ARM AFBC modifiers and GEM framebuffer helpers.

Risks and test signals: Risks include backing-object lifetime leaks, refcount imbalance during async flips, pitch/offset/modifier validation gaps, exposing handles through GETFB incorrectly, dirty callback coordinate errors, list iteration without `fb_lock`, and AFBC alignment/size mistakes. Test addfb/addfb2, framebuffer lookup after file close, page flip lifetime, remove while scanning out, dirtyfb IOCTL, multi-plane and modifier formats, AFBC metadata, and driver unload cleanup.
