<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/tve200_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/tve200_drv.c

Purpose: Provides TVE200 platform-driver probe/remove/shutdown, DRM driver registration, mode-config setup, bridge/panel discovery, clocks/MMIO/IRQ acquisition, and fbdev client setup.

Important APIs/types/functions: `tve200_modeset_init()` configures mode limits, finds a panel/bridge, creates a panel bridge, initializes the display pipe, attaches the bridge, initializes vblank, resets mode config, and starts polling. `tve200_probe()` allocates private and DRM device state, enables PCLK, gets TVE clock, maps registers, requests IRQ, initializes modeset, registers DRM, and starts a default RGB565 client. `tve200_remove()` unregisters and cleans up. `tve200_drm_driver` uses GEM DMA and fbdev DMA helper ops.

Control flow: Probe is a staged resource-acquisition sequence with unwind labels for PCLK and DRM device references. Modeset init removes the panel bridge and cleans mode config on failure. Remove unregisters DRM, atomically shuts down KMS, removes panel bridge, cleans mode config, disables PCLK, and drops the DRM reference.

State and persistence: Runtime state lives in `drm->dev_private`, mapped registers, clocks, bridge/panel references, and DRM mode objects. No persistent storage exists.

Dependencies and integration points: Integrates platform bus, OF matching (`faraday,tve200`), DRM atomic/KMS helpers, panel bridge, GEM DMA, fbdev DMA, vblank, Linux clocks, IRQ, and ioremap helpers.

Risks and test signals: Risks include requiring a panel bridge only, clock unwind correctness, panel bridge cleanup, shutdown ordering, and default format compatibility. Tests should cover probe deferral/errors, module load/unload, DT binding with panel, IRQ request failure, and atomic shutdown on remove/shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/tve200_drv.c -->
