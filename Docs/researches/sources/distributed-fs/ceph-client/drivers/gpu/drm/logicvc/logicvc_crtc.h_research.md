# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_crtc.h

Purpose: declares the LogiCVC CRTC wrapper and public CRTC entry points.

Important APIs/types/functions: `struct logicvc_crtc` embeds `struct drm_crtc` and holds a pending vblank event pointer. Exports `logicvc_crtc_vblank_handler` and `logicvc_crtc_init`.

Control flow: the core probe path calls `logicvc_crtc_init`; the top-level IRQ handler calls `logicvc_crtc_vblank_handler`.

State and persistence: pending event state is stored between atomic commit and vblank IRQ. No persistent storage beyond runtime DRM object state.

Dependencies and integration points: forward-declares DRM pending event and `logicvc_drm`. Used by core DRM, IRQ, and interface/layer setup.

Risks and test signals: structure ownership assumes one CRTC per device. Test initialization order with primary layer present and vblank event delivery.
