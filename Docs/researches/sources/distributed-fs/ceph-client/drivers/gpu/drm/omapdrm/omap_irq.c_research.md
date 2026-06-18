# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_irq.c

Purpose: Manages DISPC interrupt installation, vblank/framedone toggling, synchronous waiters, and IRQ dispatch into CRTC error/vblank/framedone handlers.

Important APIs/types/functions: `struct omap_irq_wait` tracks wait queue, mask, and countdown. Public functions include `omap_irq_wait_init`, `omap_irq_wait`, `omap_irq_enable_framedone`, `omap_irq_enable_vblank`, `omap_irq_disable_vblank`, `omap_drm_irq_install`, and `omap_drm_irq_uninstall`.

Control flow: `omap_drm_irq_install` initializes wait state, builds a base IRQ mask for OCP errors, plane FIFO underflows, and manager sync-lost events, clears stale status, and registers `omap_irq_handler`. Vblank/framedone helpers update `priv->irq_mask` under `wait_lock` and rewrite DISPC IRQ enable bits together with all active waiter masks. The handler reads and clears status, flushes the posted write, dispatches per-pipe vsync/sync-lost/framedone events, logs OCP and underflow errors, decrements matching waiters, and wakes their queues.

State and persistence: Runtime state is `priv->irq_mask`, `priv->wait_list`, `priv->wait_lock`, and `priv->irq_enabled`. Wait objects are allocated per wait and freed after timeout or completion.

Dependencies and integration: Uses DISPC IRQ accessors, DRM vblank core, OMAP CRTC callbacks, and `omap_drm_private` pipe/plane bookkeeping.

Risks: `omap_irq_wait_init` does not check `kzalloc_obj` failure before dereference. `omap_irq_wait` returns `-1` instead of a standard errno on timeout. IRQ mask updates rely on callers respecting locking and DISPC runtime constraints. Underflow logging is ratelimited and only reports enabled underflow bits.

Test signals: Verify vblank enable/disable refcounting through DRM, framedone enable flow for atomic commits, waiter timeout and completion, IRQ uninstall idempotence, OCP and FIFO-underflow ratelimited logging, and multi-pipe dispatch to the correct CRTC index.
