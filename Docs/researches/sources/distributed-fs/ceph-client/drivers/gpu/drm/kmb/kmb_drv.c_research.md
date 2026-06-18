<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_drv.c

## Purpose
Implements the Keem Bay platform DRM driver. It creates the DRM device, initializes clocks, MMIO, DSI host/bridge, mode config, CRTC/planes, LCD IRQ handling, runtime/system PM, framebuffer client setup, and teardown.

## Important APIs, types, and functions
Clock and hardware setup is split across `kmb_initialize_clocks()`, `kmb_display_clk_enable()`, `kmb_map_mmio()`, and `kmb_hw_init()`. DRM setup uses `kmb_setup_mode_config()` and `kmb_driver`. IRQ handling uses `handle_lcd_irq()`, `kmb_isr()`, `kmb_irq_reset()`, `kmb_irq_install()`, and `kmb_irq_uninstall()`. Platform lifecycle is `kmb_probe()` and `kmb_remove()`, with `kmb_pm_suspend()` and `kmb_pm_resume()` for PM.

## Control flow
Probe first locates the DSI endpoint and remote DSI platform device, registers a DSI host early through `kmb_dsi_host_bridge_init()`, and defers until the external bridge is available. It then allocates a managed DRM private, initializes DSI, maps LCD/MIPI MMIO, enables LCD/MIPI clocks and MSSCAM reset/clock bits, sets up mode config, installs the LCD IRQ, initializes polling, registers the DRM device, and starts the client setup. The LCD IRQ handler clears EOF, line compare, vertical compare, layer, and DMA error conditions. EOF applies deferred plane disables. Underflow recovery flushes FIFOs, disables DMA, and re-enables at a later vertical compare.

## State and persistence
`struct kmb_drm_private` stores LCD MMIO, clocks, CRTC, DSI pointer, IRQ lock, init display configuration, plane disable flags, underflow state, flush state, and the affected layer. Hardware state includes LCD interrupts, FIFO flush, DMA enables, MSSCAM clock/reset bits, and MIPI/LCD routing.

## Dependencies and integration points
Depends on OF graph wiring, reserved memory, syscon `intel,keembay-msscam`, DRM GEM DMA helpers, bridge connector support, the DSI helper file, and CRTC/plane files. The platform compatible is `intel,keembay-display`.

## Risks
Some setup calls ignore or squash errors, such as `kmb_initialize_clocks()` return in `kmb_hw_init()` and `kmb_dsi_encoder_init()` return assignment before CRTC port setup. Probe has global DSI host dependencies and defer-sensitive ordering. IRQ recovery is tightly coupled to plane update behavior and can drop plane updates while underflow recovery is active. Clock enable/disable is split between driver and CRTC paths and needs balanced sequencing.

## Test signals
Probe/defer with ADV7535 bridge, IRQ install/uninstall, fbdev client bring-up, reserved-memory configurations, DMA underflow injection, vblank counters, page flips during EOF, system suspend/resume, and driver remove should all be tested. Logs include clock rates, bridge attach, underflow notices, and IRQ errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_drv.c -->
