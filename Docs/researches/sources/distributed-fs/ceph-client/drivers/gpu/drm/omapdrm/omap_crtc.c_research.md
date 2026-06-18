# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_crtc.c

Purpose: Implements OMAP DRM CRTC objects, DISPC manager callbacks, atomic CRTC state, pending flip completion, vblank/framedone IRQ handling, manual DSI updates, color management, and CRTC creation.

Important APIs/functions: `omap_crtc_init()` allocates a CRTC for a pipeline/channel, initializes pending wait and manual update work, enables color management when DISPC supports gamma, and installs primary plane properties. DSS manager entry points set timings/config, enable/disable manager, start updates, and register framedone callbacks. IRQ entry points handle error, vblank, and framedone events. Atomic helpers validate mode/bandwidth, mirror legacy rotation/zpos to primary plane state, program gamma/CTM manager properties, trigger DISPC GO or manual update, and arm events.

Control flow: Encoder/output mode paths set `omap_crtc->vm`. Bridge enable calls manager enable, which writes timings and calls `omap_crtc_set_enabled()`. Atomic flush writes gamma/manager properties and, if enabled, marks a pending update, takes a vblank reference, and either triggers DISPC GO or schedules manual DSI update. Vblank/framedone IRQs send pending events, clear pending, drop vblank refs, and wake commit waiters.

State and persistence: `struct omap_crtc` tracks channel, pipeline, videomode, enabled/pending/event state, delayed work, and framedone callback. `struct omap_crtc_state` extends DRM state with legacy rotation/zpos shadows and `manually_updated`. No persistent storage exists.

Dependencies/integration: Depends on DRM atomic/vblank/color helpers, DISPC manager/IRQ APIs, OMAP plane properties, OMAP DSS outputs/DSI ops, and driver private bandwidth limits.

Risks and test signals: Pending state is protected by `event_lock` and commit waits timeout after 250 ms. HDMI bypasses normal enable wait because HDMI wrapper manages completion. Manual DSI updates do not trigger vsync and depend on framedone callback. Test atomic page flips, manual command-mode DSI dirty updates, HDMI enable, sync-lost handling on digit output, color CTM/gamma programming, suspend/resume, and bandwidth rejection.
