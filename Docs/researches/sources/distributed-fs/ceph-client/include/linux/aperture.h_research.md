# sources/distributed-fs/ceph-client/include/linux/aperture.h

## Purpose
Declares helpers for graphics/framebuffer aperture ownership and removal of conflicting framebuffer or VGA devices.

## Important APIs, Types, And Functions
When `CONFIG_APERTURE_HELPERS` is enabled, the API includes `devm_aperture_acquire_for_platform_device()`, `aperture_remove_conflicting_devices()`, `__aperture_remove_legacy_vga_devices()`, and `aperture_remove_conflicting_pci_devices()`. Stubs return success when helpers are disabled. `aperture_remove_all_conflicting_devices()` is an inline wrapper over the full resource range.

## Control Flow, State, And Persistence
The helpers coordinate device ownership around memory apertures. They may unregister or remove existing framebuffer/graphics devices so a new driver can safely claim display memory. Devm acquisition persists until the platform device is detached.

## Dependencies And Integration Points
Uses `linux/types.h` and forward declarations for PCI and platform devices. Integrates DRM, fbdev, VGA legacy cleanup, platform display drivers, and resource management.

## Risks And Test Signals
Disabled stubs returning success can allow callers to skip conflict removal in unsupported configs. Runtime risks include removing the wrong framebuffer range or leaving active legacy VGA owners. Tests should cover DRM driver probe over EFI/simplefb, overlapping aperture ranges, platform devm release, PCI VGA removal, and config-disabled builds.
