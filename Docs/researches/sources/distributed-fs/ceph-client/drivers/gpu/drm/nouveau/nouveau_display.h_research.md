# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_display.h

Purpose: Declares the Nouveau display core structure and public display/framebuffer APIs shared by DRM driver setup, connector code, CRTC code, and generation-specific display implementations.

Important APIs/types: `struct nouveau_display` stores private generation data, destructor/init/fini callbacks, nvif display object, DRM property pointers for dithering/underscan/procamp, saved atomic suspend state, and supported format modifiers. Public functions cover display lifecycle, HPD resume, vblank control, scanout position, dumb-buffer creation, HDMI mode setup, framebuffer layout decoding, framebuffer creation, and user framebuffer creation.

Control flow/state contract: `nouveau_display_create()` allocates and installs `drm->display`; generation-specific code fills callbacks and modifier lists; `nouveau_display_init/fini()` call the callbacks and manage common event/polling state; framebuffer helpers validate BO layout before DRM framebuffer registration.

Dependencies/integration: Includes Nouveau driver state, nvif display, and DRM framebuffer declarations. It is consumed by `nouveau_display.c`, connector property code, HDMI encoder setup, nv04/nv50 display paths, and GEM/dumb-buffer paths.

Risks/test signals: The callback table must be initialized consistently by generation-specific display creation before common lifecycle calls. Property pointers may be NULL depending on generation. Test signals include headless display creation, property availability by GPU generation, framebuffer modifier support, suspend/resume state restore, and vblank/scanout helper calls.
