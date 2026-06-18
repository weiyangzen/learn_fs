# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_kms.c

## Purpose

`xen_drm_front_kms.c` implements the Xen frontend's simple KMS pipeline: framebuffer creation/destruction with backend attach/detach, mode config, display enable/disable, page flip submission, frame-done event delivery, and per-connector simple display pipe setup.

## Important APIs, Types, And Functions

Public APIs are `xen_drm_front_kms_init()`, `xen_drm_front_kms_fini()`, and `xen_drm_front_kms_on_frame_done()`. Important helpers include `fb_create()`, `fb_destroy()`, `display_enable()`, `display_disable()`, `display_update()`, `display_send_page_flip()`, and `send_pending_event()`.

## Control Flow

KMS init initializes mode config, creates a simple display pipe for each configured connector, resets mode config, and starts polling. Framebuffer creation uses DRM GEM FB helpers then asks the backend to attach the framebuffer cookie. Display enable sends `SET_CONFIG` with framebuffer geometry and bpp; disable sends a zero config and releases any pending event. Atomic update captures the DRM event, sends page flip only for old-fb-to-new-fb transitions, schedules a timeout worker, and otherwise completes the event immediately. Backend frame-done IRQ cancels the timeout and sends the event.

## State And Persistence Behavior

Per-pipeline persistent state includes dimensions, connector, simple pipe, pending vblank event, delayed timeout work, and `conn_connected`. Mode config limits are fixed at 4095x2047. Pending events are protected by DRM `event_lock` and always drained on disable/fini.

## Dependencies And Integration Points

It depends on DRM atomic/simple-KMS/GEM framebuffer/vblank helpers, connector format declarations, and core Xen protocol functions. It receives frame-done notifications from event-channel IRQ handling.

## Risks And Test Signals

Risks include event leaks or double sends under timeout/IRQ races, treating page-flip failure as connector disconnect, fixed mode limits, and no real vblank initialization despite custom event handling. Test page-flip completion, timeout fallback, enable/disable transitions, framebuffer attach failure, connector poll after backend error, and multi-connector KMS setup.
