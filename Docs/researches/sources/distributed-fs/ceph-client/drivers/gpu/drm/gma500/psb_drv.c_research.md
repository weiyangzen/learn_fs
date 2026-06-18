# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_drv.c

## Purpose
This is the main PCI/DRM driver entry point for GMA500/GMA600/GMA3600/GMA3650. It matches PCI IDs to chip ops, removes conflicting firmware framebuffers, allocates the DRM device/private state, maps MMIO resources, initializes chip/memory/display/IRQ subsystems, registers with DRM, and tears everything down on remove.

## Important APIs, Types, and Functions
Important functions are `psb_pci_probe()`, `psb_driver_load()`, `psb_driver_unload()`, `psb_device_release()`, `psb_do_init()`, `psb_spank()`, `gma_remove_conflicting_framebuffers()`, `psb_pci_remove()`, `psb_init()`, and `psb_exit()`. Key objects are `pciidlist`, `psb_gem_fops`, the `drm_driver`, and the `pci_driver`.

## Control Flow
Probe removes firmware devices, enables PCI, allocates `drm_psb_private`, stores drvdata, calls `psb_driver_load()`, registers DRM, and starts DRM clients. Load maps VDC/SGX/AUX/LPC resources, sets up OpRegion and chip ops, initializes power, scratch page, GTT, GEM MM, SGX MMU/page directories, soft-resets SGX, maps stolen memory into the SGX MMU, binds PD contexts, registers ACPI video, initializes vblank/IRQs/modeset/polling, then enables backlight and ASLE if an internal panel exists.

## State and Persistence Behavior
Driver-private state spans PCI resource mappings, chip ops, GTT/GEM/MMU state, stolen memory, scratch page cache attributes, IRQ masks, register save areas, OpRegion, backlight, modeset objects, and platform-specific aux/LPC devices. Unload reverses backlight, modeset, IRQ, chip, OpRegion, MMU, GEM, GTT, page/cache, MMIO, PCI references, BIOS, and power initialization.

## Dependencies and Integration Points
This file integrates nearly every local subsystem: GTT, GEM, MMU, chip ops for PSB/Oaktrail/CDV, power, IRQ, framebuffer helpers, Intel BIOS, OpRegion, ACPI video, DRM core, PCI, and aperture conflict removal.

## Risks
Load error paths are broad and rely on `psb_driver_unload()` tolerating partially initialized state. Some failures after setup return directly instead of going through `out_err`. The driver keeps runtime PM awake by design. AUX fallback can point `aux_reg` at `vdc_reg`; unload must avoid double-unmap semantics. Hardware init uses magic SGX reset and base registers.

## Test Signals
Signals include PCI ID matching for all families, no firmware framebuffer conflict, successful DRM registration, initialized vblank/IRQ/modeset/backlight, SGX MMU stolen-memory mapping, clean remove/unload after partial and full probes, and suspend/resume callbacks through `psb_pm_ops`.
