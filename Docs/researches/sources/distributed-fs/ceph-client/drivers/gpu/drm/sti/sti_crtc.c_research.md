# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_crtc.c

Purpose: Implements DRM CRTC behavior for STI mixers. Each `struct sti_mixer` embeds the DRM CRTC and the CRTC code controls clocks, VTG timing, mixer active area, plane commit flushing, and vblank notification.

Important APIs/functions: `sti_crtc_init()` calls `drm_crtc_init_with_planes()` and installs helper funcs. `sti_crtc_mode_set()` enables the compositor path clock, sets pixel-clock rate from mode clock, programs VTG timing, and configures mixer active video area. `sti_crtc_atomic_flush()` processes STI plane status transitions, programs mixer depth/status, commits HQVDP-backed VID state, and arms pending vblank events. `sti_crtc_vblank_cb()` bridges VTG top/bottom field events into `drm_crtc_handle_vblank()` and completes synchronized mixer shutdown.

Control flow: Atomic enable marks the mixer ready and enables DRM vblank. Atomic disable marks the mixer disabling and waits one vblank; final clock/background shutdown is deferred until the VTG callback observes that overlay planes are disabled. Plane flush recognizes `STI_PLANE_UPDATED` and `STI_PLANE_DISABLING`, updating mixer registers and plane status.

State/persistence: Mixer status is the CRTC state machine (`READY`, `DISABLING`, `DISABLED`). Plane statuses are consumed here to coordinate asynchronous disabling. Vblank events are stored in DRM CRTC state and armed under `event_lock`.

Dependencies/integration: Depends on DRM atomic helpers, vblank API, common clocks, `sti_compositor`, `sti_mixer`, `sti_vid`, and VTG notifier registration. Debugfs setup for compositor subdevices happens in CRTC late registration for CRTC index 0.

Risks/test signals: Shutdown correctness depends on every non-cursor overlay eventually reaching `STI_PLANE_DISABLED`. Missing VTG events can leave clocks enabled or CRTC stuck disabling. Test with atomic enable/disable, page-flip event delivery, vblank on/off, plane disable races, and mixer debugfs state.
