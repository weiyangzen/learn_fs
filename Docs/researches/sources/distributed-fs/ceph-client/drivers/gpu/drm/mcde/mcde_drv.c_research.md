## sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_drv.c

### Purpose

`mcde_drv.c` is the MCDE DRM platform driver. It allocates the DRM device, powers and clocks the MCDE block for probing, validates hardware revision, populates and binds DSI components, initializes DRM mode configuration, registers the device, and handles remove/shutdown.

### Important APIs, types, and functions

Important objects are `mcde_drm_driver`, `mcde_mode_config_funcs`, `mcde_mode_config_helpers`, component master ops, `mcde_driver`, and module init/exit functions. Main routines are `mcde_probe()`, `mcde_drm_bind()`, `mcde_modeset_init()`, `mcde_irq()`, `mcde_drm_unbind()`, `mcde_remove()`, and `mcde_shutdown()`.

### Control flow

Module init registers child component drivers first, then the MCDE platform driver. Probe allocates `struct mcde`, enables EPOD/VANA regulators and the main MCDE clock, maps MMIO, requests IRQ, reads and verifies PID `0x03000800`, disables/clears IRQs, populates DT child devices, builds a component match for DSI children, then deliberately powers EPOD off before registering the component master. Bind initializes mode config, binds components, finds a DSI or fallback DPI bridge, initializes vblank and the display pipe, attaches the bridge, registers the DRM device, and starts DRM clients. Remove/unbind unregister DRM, shut down atomic state, unbind components, and release clocks/regulators.

### State and persistence behavior

Device state persists in devm-managed `struct mcde`, regulators, clocks, MMIO mapping, IRQ, component relationships, and DRM mode objects. EPOD is toggled during probe to reset the display subsystem; display enable later re-powers it.

### Dependencies

It depends on Linux component framework, platform/OF population, regulators, clocks, IRQ/MMIO, DRM atomic/GEM DMA/fbdev/client helpers, bridge/panel helpers, and MCDE display/DSI internals.

### Integration points

The driver matches `ste,mcde`. It owns the top-level IRQ and delegates display IRQ handling to `mcde_display_irq()`. Component matching binds `mcde_dsi_driver` children. Mode setup falls back to a direct DPI panel or bridge if no DSI bridge is installed.

### Risks

Only one hardware revision is accepted. If no DSI components match, probe fails before DPI fallback can be used because component matching is mandatory. Probe has careful power-state transitions; failures after EPOD is disabled require special cleanup. Bridge selection is intentionally simple and assumes one output path.

### Test signals

Signals include module load/unload, DT probing with DSI child nodes, DPI fallback, PID rejection on unsupported hardware, IRQ request and clearing, DRM device registration, fbdev/client setup, shutdown blanking, and regulator/clock balance under probe failure paths.
