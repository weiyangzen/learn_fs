# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_display.c

Purpose: Implements Nouveau's DRM display core glue: mode_config setup, display engine construction/destruction, framebuffer validation/creation, hotplug work, vblank/scanning helpers, suspend/resume, property creation, and dumb-buffer allocation.

Important APIs/functions: `nouveau_display_create/destroy/init/fini/suspend/resume()`, `nouveau_display_hpd_resume()`, `nouveau_display_vblank_enable/disable()`, `nouveau_display_scanoutpos()`, `nouveau_framebuffer_new()`, `nouveau_user_framebuffer_create()`, `nouveau_framebuffer_get_layout()`, and `nouveau_display_dumb_create()`. Internal helpers decode and validate NVIDIA format modifiers, check blocklinear sizes, create DRM properties, and process HPD work.

Control flow: Display creation allocates `struct nouveau_display`, initializes DRM mode_config, sets max dimensions by GPU family, initializes polling, constructs nvif display unless modeset is disabled, delegates to nv04 or nv50 display creation, resets mode_config, initializes vblank/CRC, and registers ACPI notification. Init enables HPD/IRQ events before calling generation-specific init and enabling polling. Fini shuts down modesets if needed, blocks events, cancels HPD work for non-runtime teardown, disables polling, and delegates generation-specific fini. Suspend stores atomic state when applicable before fini; resume reinitializes and restores atomic state.

State/persistence: `drm->display` holds nvif display, property pointers, generation-private data, suspend atomic state, and supported format modifiers. HPD pending bits live in `drm` and connector state. Framebuffers retain GEM object references through DRM framebuffer lifecycle.

Dependencies/integration: Uses DRM atomic/helper/framebuffer/vblank/probe APIs, ACPI video notifier, nvif display/head methods, Nouveau GEM/BO, connector and CRTC wrappers, nv50 display/CRC/tile helpers, runtime PM in HPD work, and generation-specific display implementations.

Risks/test signals: Framebuffer modifier validation must match BO kind/tile layout and prevent out-of-bounds scanout. HPD work must balance runtime PM and mode_config locking. Suspend/resume must preserve atomic state and not leave events enabled. Test with linear and blocklinear framebuffers, YUV overlay restrictions pre-NV50, hotplug storms, ACPI reprobe, runtime suspend, vblank timing, dumb buffers, and headless devices.
