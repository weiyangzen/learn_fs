# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_crtc.c

Purpose: implements the single LogiCVC CRTC, including mode timing programming, control-signal polarity, vblank event management, IRQ-driven page-flip completion, and CRTC registration.

Important APIs/types/functions: `logicvc_crtc_init`, `logicvc_crtc_vblank_handler`, CRTC helper callbacks `mode_valid`, `atomic_begin`, `atomic_enable`, `atomic_disable`, and CRTC funcs for vblank enable/disable.

Control flow: atomic enable computes porch/sync/active timing fields from adjusted mode and writes LogiCVC timing registers. It configures HSYNC/VSYNC/DE and clock polarity from mode flags and connector bus flags, resets internal state through `LOGICVC_DTYPE_REG`, enables vblank, and captures pending flip events. Atomic begin handles events for already-active CRTCs; atomic disable shuts off vblank/control bits and sends leftover events synchronously. IRQ handling calls `logicvc_crtc_vblank_handler`, which invokes DRM vblank handling and sends stored events.

State and persistence: `struct logicvc_crtc` stores the DRM CRTC and one pending `drm_pending_vblank_event`. Hardware timing/control registers persist until reprogrammed or reset.

Dependencies and integration points: depends on regmap, DRM atomic/vblank helpers, connector bus flags through `logicvc->interface`, primary layer from `logicvc_layer_get_primary`, and OF graph port 1.

Risks and test signals: event handling must pair `drm_crtc_vblank_get/put`; missed IRQs can hang page flips. Test modesets with positive/negative sync flags, panel bus flags, page flips on active and enabling CRTCs, disable with pending event, and vblank interrupt masking.
