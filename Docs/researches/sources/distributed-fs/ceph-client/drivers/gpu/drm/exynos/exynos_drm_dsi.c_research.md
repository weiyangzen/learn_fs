# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_dsi.c

Purpose: this file is the Exynos glue around the shared Samsung DSIM MIPI-DSI bridge/host implementation. It supplies Exynos-specific host ops, creates a DRM encoder, and registers the DSIM host as a component.

Important APIs and data: `struct exynos_dsi` wraps the DRM encoder. `exynos_dsi_register_host()` allocates it, stores it in `dsim->priv`, sets `bridge.pre_enable_prev_first`, and adds component ops. `exynos_dsi_bind()` initializes the encoder and registers the MIPI DSI host. `exynos_dsi_host_attach()` attaches the DSIM bridge into the encoder chain, copies lane/format/mode flags from the MIPI DSI device, and updates the LCD CRTC `i80_mode` flag based on video vs command mode. `exynos_dsi_te_irq_handler()` forwards TE IRQs to the CRTC when video output is available.

Control flow: the platform driver's probe/remove are provided by `samsung_dsim_probe()` and `samsung_dsim_remove()`, with Exynos platform data selected by OF compatible. During host registration, component bind later creates the DRM encoder and registers the MIPI host. When a panel/device attaches, the bridge is attached, mode flags are stored, and hotplug is emitted if polling is enabled. Detach emits hotplug again. Unbind atomically disables the bridge and unregisters the host.

State and persistence: runtime state is in `samsung_dsim`, `exynos_dsi`, the DRM encoder, and the LCD CRTC `i80_mode` bit. There is no persistence.

Dependencies and integration points: depends on `drm/bridge/samsung-dsim.h`, DRM bridge/probe/simple encoder helpers, MIPI DSI host framework, component framework, and Exynos CRTC helpers. It integrates with MIC and FIMD through the LCD CRTC path and TE forwarding.

Risks: `exynos_dsi_host_attach()` calls `drm_bridge_attach()` without checking its return value. It assumes `exynos_drm_crtc_get_by_type()` returns a valid LCD CRTC and dereferences it directly. Unbind calls `dsim->bridge.funcs->atomic_disable()` directly, which assumes the bridge is initialized and its funcs are present.

Test signals: probe for each compatible platform data entry, panel attach/detach, command-mode DSI setting `i80_mode`, TE IRQ page flips, hotplug events, and component unbind during active display.
