<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_rebar.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_rebar.c

## Purpose

`xe_pci_rebar.c` handles optional Resizable BAR setup for the local-memory BAR. It either forces the VRAM BAR to a module-parameter size or grows it to the largest supported size before the main device probe starts using local memory.

## Important APIs and Functions

The exported function is `xe_pci_rebar_resize(struct xe_device *xe)`. Private `resize_bar()` converts a byte size to PCI ReBAR encoding, calls `pci_resize_resource()`, and logs success or BIOS/platform guidance on failure. `xe_pci_rebar_resize()` reads `xe_modparam.force_vram_bar_size`, inspects `LMEM_BAR`, validates supported sizes with PCI ReBAR helpers, verifies a root bus memory resource above 4 GiB, disables PCI memory decoding, resizes, reassigns unassigned bus resources, and restores the PCI command register.

## Control Flow and State

The function is called during PCI probe after early device info exists and before full device probing. Negative `force_vram_bar_size` disables resizing. Zero means "grow to maximum if larger than current." A positive value requests a specific MiB size. Persistent state is PCI resource sizing and assigned bus resources; the Xe object only provides logging, module parameters, and PCI device access.

## Dependencies and Integration Points

It depends on Linux PCI ReBAR APIs, BAR constants from `xe_bars.h`, module parameters, and Xe logging helpers. It is integrated directly into `xe_pci_probe()`.

## Risks and Test Signals

Resizing PCI resources is platform-sensitive. Failure paths are non-fatal, so later VRAM behavior depends on the existing BAR aperture. The root-resource scan only accepts memory resources above 4 GiB, matching large BAR requirements. Tests should cover disabled, forced-supported, forced-unsupported, grow-to-max, already-large-enough, missing-root-resource, resize failure, and command register restoration after resize attempts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_rebar.c -->
