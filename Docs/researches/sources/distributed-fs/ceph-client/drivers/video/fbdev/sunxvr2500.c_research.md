# sources/distributed-fs/ceph-client/drivers/video/fbdev/sunxvr2500.c

## Purpose
`sunxvr2500.c` is a simple PCI fbdev driver for Sun 3DLABS XVR-2500 and related boards. It maps the PCI framebuffer BAR, derives geometry from the associated OF node, and exposes the active firmware mode to fbdev.

## Important APIs, Types, and Functions
`struct s3d_info` tracks `fb_info`, `pci_dev`, OF node, framebuffer mapping/base/size, geometry, depth, and pseudo palette. Key functions are `s3d_get_props()`, `s3d_setcolreg()`, `s3d_set_fbinfo()`, `s3d_pci_register()`, and `s3d_init()`. The PCI ID table matches multiple 3DLABS device ids. `s3d_ops` uses default IOMEM operations plus colormap handling.

## Control Flow
Initialization honors `fb_modesetting_disabled("s3d")` and `fb_get_options("s3d")`, then registers the PCI driver. Probe first removes conflicting PCI aperture users, enables the device, allocates `fb_info`, locates the OF node with `pci_device_to_OF_node()`, requests BAR 1, reads `width`, `height`, and optional `depth`, computes line length from depth because OF `linebytes` is known unreliable, maps the framebuffer, initializes fbdev metadata and cmap, then registers the framebuffer.

## State and Persistence
State is per-device fbdev runtime state plus the BAR 1 mapping, cmap, and pseudo palette. The driver does not persist or restore hardware modes; it relies on existing firmware setup. It does not implement remove, blanking, panning, or mode changes.

## Dependencies and Integration Points
Dependencies include PCI, OF node association for PCI devices, aperture conflict removal, IOMEM mapping, and fbdev. It integrates with generic system firmware framebuffer handoff through `aperture_remove_conflicting_pci_devices()`.

## Risks and Edge Cases
Risk centers on assumptions about BAR 1, OF geometry, and supported depth. If depth is not 8/16/24/32, line length may remain unset. The absence of a remove callback means it is effectively system-lifetime. Truecolor pseudo-palette packing uses blue in the high byte and red at bit 8, matching this hardware path but easy to regress.

## Test Signals
Test PCI binding for listed IDs, aperture handoff, OF node absence, BAR request failure, 8/16/24/32 bpp line length, registered framebuffer geometry, palette behavior in truecolor, and boot disabling through `video=s3d:off` or modesetting disable.
