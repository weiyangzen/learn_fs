# sources/distributed-fs/ceph-client/samples/vfio-mdev/mdpy-fb.c

## Purpose

This PCI framebuffer driver binds to the simple `mdpy` virtual PCI display device and registers a Linux framebuffer over BAR0.

## Important APIs, Types, and Functions

It defines fixed and variable framebuffer templates, `struct mdpy_fb_par` with pseudo palette, `mdpy_fb_setcolreg()`, `mdpy_fb_destroy()`, `mdpy_fb_probe()`, `mdpy_fb_remove()`, the PCI id table, and module init. It uses PCI region management, config-space reads, `ioremap`, `framebuffer_alloc`, `register_framebuffer`, `FB_DEFAULT_IOMEM_OPS`, and DRM format `DRM_FORMAT_XRGB8888`.

## Control Flow

Probe enables the PCI device, requests regions, reads format/width/height from vendor capability config offsets, validates XRGB8888 and sane dimensions, allocates `fb_info`, maps BAR0, fills fix/var screeninfo, assigns fbops and pseudo palette, then registers the framebuffer. Remove unregisters the framebuffer, unmaps BAR0, releases regions, and disables the device.

## State and Persistence Behavior

Framebuffer state lives in `fb_info`, mapped BAR0 memory, and `mdpy_fb_par` palette. The framebuffer device persists until PCI removal/module unload. Color register changes update only the pseudo palette.

## Dependencies and Integration Points

It integrates with PCI, fbdev, DRM fourcc definitions, and the mdpy virtual PCI ABI from `mdpy-defs.h`.

## Risks and Edge Cases

Only XRGB8888 is supported. Width/height are trusted after coarse range checks. `mdpy_fb_destroy()` unmaps `screen_base`, and remove also unmaps directly; fbdev destroy ordering should be verified to avoid double-unmap paths.

## Test Signals

Expose an mdpy mdev/PCI device, load the driver, confirm `fb%d registered`, write to `/dev/fb*`, and verify remove cleanup with no leaks or mapping warnings.
