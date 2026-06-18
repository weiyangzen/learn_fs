# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front.c

## Purpose

`xen_drm_front.c` is the Xen PV display frontend core. It handles XenBus lifecycle, backend state transitions, DRM device creation, dumb-buffer allocation, grant-shared display-buffer protocol requests, framebuffer attach/detach, page flips, and cleanup of backend-visible resources.

## Important APIs, Types, And Functions

The central state is `struct xen_drm_front_info` and internal `struct xen_drm_front_dbuf`. Public cross-file operations include `xen_drm_front_mode_set()`, `xen_drm_front_dbuf_create()`, `xen_drm_front_fb_attach()`, `xen_drm_front_fb_detach()`, `xen_drm_front_page_flip()`, `xen_drm_front_on_frame_done()`, and `xen_drm_front_gem_object_free()`. XenBus entry points are `xen_drv_probe()`, `xen_drv_remove()`, and `displback_changed()`.

## Control Flow

Probe initializes DMA mask, allocates frontend state, and switches the frontend to `Initialising`. On backend `InitWait`, it reads XenStore config, creates and publishes event channels, then moves to `Initialised`. On backend `Connected`, it marks channels connected and creates/registers the DRM device. DRM dumb create builds a GEM object, shares its pages or backend allocation directory with `XENDISPL_OP_DBUF_CREATE`, then exposes the handle. Framebuffer creation calls into this file for `FB_ATTACH`; KMS mode enable and flips send `SET_CONFIG` and `PG_FLIP` requests. Disconnect/unplug tears down DRM, channels, display buffers, and XenBus state.

## State And Persistence Behavior

Persistent state includes XenBus device pointer, event-channel pairs, parsed config, DRM private state, an `io_lock`, and `dbuf_list` entries containing cookies and `xen_front_pgdir_shbuf` grant-directory state. Backend-visible resources persist until explicit destroy/detach or disconnect. Backend-allocated buffers release local grants before destroy; frontend-allocated buffers keep local resources until after destroy attempt.

## Dependencies And Integration Points

It depends on XenBus, Xen display protocol `displif`, `xen-front-pgdir-shbuf`, DRM GEM/modeset core, simple KMS, and helper modules in this directory. It integrates with `xen_drm_front_evtchnl.c` for rings, `xen_drm_front_cfg.c` for XenStore, `xen_drm_front_gem.c` for pages, and `xen_drm_front_kms.c` for frame-done delivery.

## Risks And Test Signals

Risks include backend timeouts, stale grant mappings on abnormal guest/backend death, races between handle publication and backend buffer creation, cookie reuse because cookies are kernel pointers cast to `u64`, and complicated XenBus reconnect behavior. Test with frontend- and backend-allocated buffers, backend restart, module remove, dumb create failure injection, framebuffer lifecycle, page flips with frame-done events, and Xen page-size mismatch rejection.
