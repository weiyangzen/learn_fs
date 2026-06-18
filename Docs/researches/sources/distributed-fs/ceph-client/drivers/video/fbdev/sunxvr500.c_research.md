# sources/distributed-fs/ceph-client/drivers/video/fbdev/sunxvr500.c

## Purpose
`sunxvr500.c` supports Sun 3DLABS XVR-500 Expert3D-style PCI framebuffers. It uses the RAMDAC video layout registers to locate the active 8bpp framebuffer plane, mirrors drawing into two 8bpp buffers, and programs the RAMDAC CLUT.

## Important APIs, Types, and Functions
`struct e3d_info` contains PCI/OF identity, a spinlock, framebuffer and register mappings, RAMDAC base, 8bpp buffer offsets, geometry/depth, and pseudo palette. Key functions are `e3d_get_props()`, `e3d_clut_write()`, `e3d_setcolreg()`, `e3d_imageblit()`, `e3d_fillrect()`, `e3d_copyarea()`, `e3d_set_fbinfo()`, `e3d_pci_register()`, and `e3d_init()`. `e3d_ops` wraps generic cfb drawing with mirrored writes.

## Control Flow
Probe removes conflicting apertures, requires an OF node with `device_type` to skip secondary outputs, enables PCI, reads BAR0's configured base, maps BAR1 RAMDAC registers at offset `0x8000`, reads `RAMDAC_VID_8FB_0`, `RAMDAC_VID_8FB_1`, and `RAMDAC_VID_CFG`, computes the selected framebuffer physical address and the distance between 8bpp buffers, requests BAR0, reads OF geometry, computes pitch from RAMDAC line-size log2 and depth, maps the framebuffer, allocates cmap, and registers fbdev. Drawing callbacks lock, draw once at `screen_base`, temporarily advance `screen_base` by `fb8_buf_diff`, draw again, then restore it.

## State and Persistence
Runtime state includes the RAMDAC mapping, framebuffer mapping, offset calculations, spinlock-protected CLUT and mirrored drawing, cmap, and pseudo palette. Hardware-persistent state includes RAMDAC CLUT entries and framebuffer contents until reset or reprobed. No software state persists across driver lifetime.

## Dependencies and Integration Points
The driver depends on PCI, OF properties, aperture handoff, RAMDAC register layout, cfb helpers, and fbdev IOMEM mmap/read/write. It integrates with firmware mode setup and uses `device_type` as a primary-output filter.

## Risks and Edge Cases
The two-buffer rendering is explicitly a workaround for unknown WID/attribute behavior. `screen_base` is mutated under the driver spinlock, so any path bypassing those wrappers could see only one buffer. RAMDAC register assumptions and BAR offset arithmetic are hardware-specific. Unsupported depth can leave line length invalid. There is no remove callback, blanking callback, or dynamic mode set.

## Test Signals
Signals include probe on each listed PCI ID/subsystem, secondary-output rejection, RAMDAC 8FB offset calculation, visible updates for fill/copy/image paths, CLUT writes across 0..255, truecolor pseudo-palette entries, BAR failure unwinds, and fallback when depth/pitch properties are unusual.
