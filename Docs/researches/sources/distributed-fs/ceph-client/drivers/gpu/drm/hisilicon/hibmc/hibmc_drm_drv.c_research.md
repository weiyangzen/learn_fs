# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_drv.c

Purpose: top-level PCI DRM driver for HIBMC. It owns PCI probe/remove/shutdown, DRM driver registration, VRAM helper setup, KMS initialization, MMIO mapping, hardware reset/power setup, MSI interrupt registration, and suspend/resume entry points.

Important APIs/functions: `hibmc_pci_probe()` allocates the DRM device, enables PCI, loads hardware/KMS, registers DRM, and starts client setup. `hibmc_load()` maps hardware, initializes VRAM, KMS, vblank, MSI, and mode config state. `hibmc_kms_init()` configures mode limits, initializes DE, optional DP, and VGA VDAC. `hibmc_msi_init()` requests vblank IRQ and optional threaded DP HPD IRQ. `hibmc_set_power_mode()` and `hibmc_set_current_gate()` are shared power helpers.

Control flow: module PCI registration dispatches probe. Probe removes conflicting apertures, enables PCI master, calls `hibmc_load()`, then `drm_dev_register()`. Error paths call `hibmc_unload()`. Interrupt vector 0 handles vblank directly; vector 1, when allocated, reads DP interrupt status, clears it, and wakes the threaded HPD handler.

State and persistence: `struct hibmc_drm_private` embeds DRM device, plane, CRTC, VGA, DP, and MMIO pointer. Hardware power/gate/MMIO state persists until shutdown or reset. Driver state is runtime-only.

Dependencies and integration points: depends on PCI, aperture, DRM atomic/GEM/VRAM/fbdev helpers, vblank core, HIBMC DE/VDAC/DP modules, and DP register definitions for probing and interrupt status.

Risks: DP is initialized conditionally by reading `HIBMC_DP_HOST_SERDES_CTRL`; false positives/negatives affect connector exposure. If only one MSI vector is allocated, DP HPD interrupt is not requested. `dev->mode_config.funcs` is assigned through a cast. Power-gate sequences are hardware-sensitive.

Test signals: PCI bind/unbind, aperture takeover, VRAM mapping, KMS object creation, vblank IRQ, optional DP IRQ, suspend/resume, fbdev client setup, and failure injection in each init stage.
