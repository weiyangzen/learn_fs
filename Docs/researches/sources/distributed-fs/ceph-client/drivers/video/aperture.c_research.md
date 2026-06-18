# sources/distributed-fs/ceph-client/drivers/video/aperture.c

## Purpose
`aperture.c` manages ownership of firmware-provided framebuffer memory ranges so native graphics drivers can evict generic framebuffer drivers cleanly before binding hardware.

## Important APIs, types, and functions
The internal `struct aperture_range` records owner device, physical base/size, list linkage, and detach callback. Public exports are `devm_aperture_acquire_for_platform_device`, `aperture_remove_conflicting_devices`, `__aperture_remove_legacy_vga_devices`, and `aperture_remove_conflicting_pci_devices`. Internal helpers include `overlap`, `devm_aperture_acquire`, `aperture_detach_platform_device`, and `aperture_detach_devices`.

## Control flow
Generic platform framebuffer drivers acquire an aperture during probe. Native drivers later call a remove-conflicting helper. That disables future sysfb registration, walks registered apertures under a mutex, detects overlapping ranges, removes them from the list, marks the range detached, and invokes the detach callback, currently `platform_device_unregister`. PCI callers iterate memory BARs and additionally remove legacy VGA resources for the default VGA adapter.

## State and persistence
State is the global `apertures` list protected by `apertures_lock`. Entries are device-managed allocations and are removed automatically when the owning device goes away, unless already detached. No state persists across boot.

## Dependencies and integration points
The file integrates with sysfb, platform devices, PCI BAR resources, VGA arbitration, legacy VGA framebuffer constants, and devres-managed lifetime. Graphics drivers call it before hardware initialization to avoid two drivers touching the same framebuffer.

## Risks and test signals
Risks include overlap arithmetic overflow (`base + size`), detach callback while holding the aperture mutex, stale device-managed release after forced detach, accidental removal of a non-conflicting device, and VGA console interactions. Test signals include sysfb handoff from EFI/VESA/simplefb to DRM, PCI default VGA removal, non-overlapping apertures, overlapping partial ranges, hot-unplug capable platform framebuffer drivers, and repeated acquire/remove sequences.
