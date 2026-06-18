# sources/distributed-fs/ceph-client/drivers/video/fbdev/offb.c

## Purpose

`offb.c` is the Open Firmware framebuffer driver. It exposes firmware-initialized display memory as a generic fbdev device when no native driver has claimed the hardware, with special palette handling for several older ATI, IBM, AVIVO, and QEMU VGA devices. The source was read as a complete 726-line file.

## Important APIs, Types, and Functions

Per-device state is `struct offb_par`, containing palette MMIO addresses, palette type, blanked flag, pseudo palette, and framebuffer resource base/size. The main fbdev callbacks are `offb_setcolreg()`, `offb_blank()`, `offb_set_par()`, and `offb_destroy()` in `offb_ops`. Hardware discovery and setup are handled by `offb_map_reg()`, `offb_init_palette_hacks()`, `offb_init_fb()`, `offb_init_nodriver()`, `offb_probe_bootx_noscreen()`, and `offb_probe_display()`.

## Control Flow

Init checks `fb_get_options("offb")`, then registers a BootX noscreen platform driver and an OF display platform driver. Probe calls `offb_init_nodriver()`, which reads firmware properties for depth, width, height, linebytes, endianness, and framebuffer address, then uses OF address ranges and PCI heuristics to choose a memory address. It optionally enables the PCI device, applies a Valkyrie address quirk, and calls `offb_init_fb()`. `offb_init_fb()` reserves the framebuffer memory, allocates `fb_info`, sets fix/var fields from firmware geometry/depth, initializes palette hacks for 8-bpp displays or truecolor layouts for higher depth, maps framebuffer memory, allocates cmap, acquires the aperture for platform use, and registers fbdev. Runtime color and blanking callbacks write pseudo palettes or device-specific DAC/LUT registers. Remove unregisters; fbdev destroy releases mappings, memory region, cmap, and `fb_info`.

## State and Persistence Behavior

The driver preserves firmware-programmed display mode and only maps/programs memory, palette, and blanking-related registers. It does not allocate video memory. `par->blanked` tracks blank state so unblank can restore the cmap. `par->base` and `par->size` own the reserved memory region until destroy. No file-backed persistence exists.

## Dependencies and Integration Points

The driver depends on Open Firmware device-tree properties, OF address translation, PCI helpers, aperture conflict management, fbdev IOMEM helpers, and architecture endian handling. On PPC32 it can consume BootX `of_chosen` data. It is a fallback bridge between firmware boot graphics and Linux fbdev/console until native drivers take over.

## Risks and Edge Cases

Framebuffer address selection is explicitly heuristic because OF has no universal framebuffer address property. Palette hacks are device-name and compatibility-string based and can miss or mis-handle firmware variants. Some error paths in `offb_init_fb()` call `iounmap(par->cmap_adr)` only after `par` allocation; palette mappings must be valid or NULL. `fb_alloc_cmap()` return is not checked before registration. Depth support is limited to 8, 15, 16, and 32. The QEMU simple palette path depends on endian-specific OF I/O address representation.

## Test Signals

Test OF display nodes with `depth`, `width`, `height`, `linebytes`, `address`, `linux,bootx-*`, big/little-endian flags, and PCI ranges. Exercise 8-bpp palette writes for ATI/Rage128/Radeon/GXT2000/AVIVO/QEMU paths, truecolor pseudo palette at 15/16/32 bpp, blank/unblank cmap restoration, aperture conflicts with native drivers, and BootX noscreen fallback.
