# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_drv.c

Purpose: core PCI DRM driver for Loongson display controllers. It handles DRM driver ops, PCI probe/remove/shutdown, VRAM discovery, TTM/GEM init, KMS object creation, IRQ/vblank setup, client setup, and PM suspend/resume.

Important APIs/types/functions: `lsdc_drm_driver`, `lsdc_modeset_init`, `lsdc_mode_config_init`, `lsdc_get_dedicated_vram`, `lsdc_create_device`, `lsdc_pci_probe/remove/shutdown`, `lsdc_drm_freeze`, and PM ops.

Control flow: PCI probe selects a chip descriptor, enables bus mastering and DMA mask, enables PCI device, creates DRM device, locates GPU BAR2 VRAM via sibling PCI device, removes conflicting framebuffers, initializes TTM/GEM, maps DC BAR0 registers, initializes mode config and KMS objects through descriptor hooks, resets mode config, registers VGA arbitration, starts polling, optionally initializes vblank and shared IRQ, registers DRM device, and starts clients. Suspend unpins VRAM BOs, evicts VRAM, suspends mode config, saves PCI state, disables device, and powers down; resume restores state, re-enables device, and resumes mode config.

State and persistence: `struct lsdc_device` stores PCI devices, descriptor, TTM device, MMIO base, VRAM/GTT ranges, display pipes, GEM object list, IRQ status, and pinned memory counters. Hardware state is restored through DRM helper resume and CRTC resets.

Dependencies and integration points: depends on PCI, aperture conflict removal, VGA arbitration, DRM atomic/KMS/fbdev TTM/GEM helpers, local TTM/GEM, descriptor function tables, module `loongson_vblank`, and IRQ handlers.

Risks and test signals: VRAM discovery assumes GPU at BDF 00:06.0 and DC at 00:06.1. Suspend unpins all VRAM BOs and must not race with userspace. Test both PCI IDs, missing sibling GPU, framebuffer takeover, IRQ sharing, vblank disabled mode, suspend/resume, and PRIME/dumb buffer flows.
