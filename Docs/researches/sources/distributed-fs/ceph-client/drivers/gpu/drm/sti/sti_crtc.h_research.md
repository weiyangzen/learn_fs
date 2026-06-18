# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_crtc.h

Purpose: Declares the CRTC-facing interface for mixer-backed STI CRTCs.

Important APIs: `sti_crtc_init()` creates a DRM CRTC around a mixer, primary plane, and cursor plane. `sti_crtc_vblank_cb()` is the VTG notifier callback installed by the compositor. `sti_crtc_is_main()` tells output encoders whether an encoder is driven by the main or auxiliary mixer path.

Control/state: The header deliberately hides mixer internals while exposing the small integration surface needed by compositor and TVOUT. The vblank callback signature follows the Linux notifier API and receives the DRM CRTC as callback data through VTG registration.

Dependencies/integration: Forward declares DRM and STI structs to avoid broad header coupling. It is used by compositor setup and by TVOUT encoder programming to choose main/aux sync routing.

Risks/test signals: Any change in mixer-to-CRTC embedding or notifier data must preserve these contracts. Compile and atomic modeset tests catch most integration failures.
