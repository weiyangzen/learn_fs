# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_irq.h

Purpose: Declares the OMAPDRM IRQ interface for vblank, framedone, install/uninstall, and masked interrupt waits.

Important APIs/types/functions: Exposes opaque `struct omap_irq_wait`, vblank/framedone enable functions, IRQ install/uninstall functions, and wait init/wait functions.

Control flow: Consumers initialize a wait object for an IRQ mask and count, then call `omap_irq_wait` with a timeout. DRM core calls vblank hooks, and driver init/teardown calls install/uninstall.

State and persistence: No direct state; declared functions manipulate `omap_drm_private` interrupt masks and wait lists.

Dependencies and integration: Included by CRTC/driver code that needs DISPC interrupt services. Depends only on Linux integer types and forward-declared DRM types.

Risks: Opaque wait object lifetime is owned by `omap_irq_wait`; callers must not reuse or free it. Timeout return is implementation-specific `-1`.

Test signals: Header compile tests across modules, plus caller audits for balanced `omap_irq_wait_init`/`omap_irq_wait` use.
