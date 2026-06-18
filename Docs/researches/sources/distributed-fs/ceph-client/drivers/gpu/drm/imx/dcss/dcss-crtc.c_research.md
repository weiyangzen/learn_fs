<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-crtc.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-crtc.c

Purpose: Implements the DCSS DRM CRTC, vblank handling, atomic enable/disable/flush, and primary-plane creation.

Important APIs/types/functions: Public functions are `dcss_crtc_init()` and `dcss_crtc_deinit()`. Important callbacks include vblank enable/disable, atomic begin/flush/enable/disable, and `dcss_crtc_irq_handler()`.

Control flow: CRTC init creates the primary DCSS plane, initializes DRM CRTC with helper callbacks, gets the named vblank IRQ, and requests it disabled by default. Atomic enable gets runtime PM, programs subsampler and DTG timing when mode changes, enables DTG/SS, and arms the context loader. Atomic flush arms vblank events and kicks context loader if DTG is active. Atomic disable disables planes, sends pending events, schedules DTG/SS shutoff through context loader, waits for completion when mode changes or inactive, turns vblank off, and drops PM autosuspend ref.

State and persistence behavior: `struct dcss_crtc` stores plane pointers, vblank IRQ, and a flag controlling whether CTXLD kick IRQ can be disabled with vblank. It coordinates persistent CRTC state with DCSS hardware modules.

Dependencies: DRM atomic/vblank helpers, runtime PM, videomode conversion, DCSS DTG/SS/CTXLD APIs, and platform IRQs.

Integration points: Used by DCSS KMS setup. Vblank IRQ only reports vblank when DTG says valid and context-loader state is flushed.

Risks: Disable relies on context-loader callback completion; timeout logs but shutdown may proceed. Vblank arming depends on CTXLD flush state, so stuck context load can suppress vblank events.

Test signals: Atomic modeset/page-flip, vblank event delivery, suspend/autosuspend transitions, DTG shutoff timeout path, and plane disable on CRTC off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-crtc.c -->
