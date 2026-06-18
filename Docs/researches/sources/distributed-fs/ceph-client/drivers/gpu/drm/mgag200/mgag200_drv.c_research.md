# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_drv.c

## Purpose
Provides the mgag200 PCI DRM driver entry point, shared device preinitialization, VRAM probing, DRM driver registration, and PCI ID dispatch to chip-specific device factories.

## Important APIs, types, and functions
- Module parameter `modeset` gates driver registration through `drm_module_pci_driver_if_modeset`.
- `mgag200_init_pci_options()` writes Matrox PCI option registers.
- `mgag200_probe_vram()` probes usable VRAM by alias testing.
- `mgag200_device_preinit()` maps BAR1 MMIO and BAR0 VRAM, optionally using write-combine.
- `mgag200_device_init()` sets shared device info/functions, initializes the MMIO lock, enables MGA mode, RAM map, high page select, and disables interrupts.
- `mgag200_pci_probe()` dispatches PCI IDs to per-chip create functions and registers the DRM device.
- Remove/shutdown paths unregister and atomically shut down the DRM device.

## Control flow
Probe removes conflicting framebuffers, enables the PCI device, switches on the `enum mga_type` stored in the PCI ID table, calls the selected factory, registers the resulting DRM device, and starts the generic DRM client with XRGB8888. Chip factories perform PCI option setup, resource mapping, shared device init, chip register init, VRAM probe, mode config init, pipeline init, mode config reset, and polling setup.

## State and persistence
PCI driver data stores the DRM device. `struct mga_device` persists MMIO/VRAM resource mappings, available VRAM, locks, output objects, and selected device info/function tables. Hardware PCI options and core MGA registers persist beyond individual atomic commits.

## Dependencies and integration points
Depends on PCI, aperture conflict removal, DRM managed allocation, GEM shmem/fbdev helpers, DRM atomic helpers, and all per-chip factory functions declared in `mgag200_drv.h`. It is the root integration point for the whole mgag200 driver.

## Risks
VRAM probing writes test patterns into MMIO VRAM and relies on restoring sampled values; aliasing or unusual BAR sizing can misreport memory. Device type dispatch must match PCI IDs and object list. Write-combine mapping is performance-sensitive and has PREEMPT_RT implications. The driver forces XRGB8888 client setup due to known 24-bit depth issues on G200ER.

## Test signals
PCI bind/unbind, framebuffer handoff, module parameter behavior, BAR mapping failures, VRAM size logs, DRM device registration, fbdev/client startup, and shutdown during reboot or module unload are key signals.
