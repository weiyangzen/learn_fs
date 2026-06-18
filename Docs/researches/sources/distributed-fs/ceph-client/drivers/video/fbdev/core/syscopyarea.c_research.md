<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/syscopyarea.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/syscopyarea.c

## Purpose

`syscopyarea.c` is the system-memory wrapper for packed-pixel framebuffer area copy. It warns if used on a framebuffer not marked as virtual-address accessible, then delegates to the generic copy implementation. The file was read as a complete 30-line source.

## Important APIs, Types, and Functions

The single exported API is `sys_copyarea(struct fb_info *p, const struct fb_copyarea *area)`. It includes `sysmem.h` and `fb_copyarea.h`, with optional `FB_REV_PIXELS_IN_BYTE` enabled by `CONFIG_FB_SYS_REV_PIXELS_IN_BYTE`.

## Control Flow

Each call checks `p->flags & FBINFO_VIRTFB`. If absent, it emits a one-time warning. It then calls `fb_copyarea(p, area)`.

## State and Persistence Behavior

No local state is owned. The warning state is managed by the fb warning helper. The operation mutates framebuffer memory described by `fb_info`.

## Dependencies and Integration Points

Framebuffer drivers use this as `fbops->fb_copyarea` when screen memory is CPU-addressable system memory. It integrates with generic packed-pixel copy macros and optional bit-reversal configuration.

## Risks and Edge Cases

Using this on MMIO-only or otherwise non-virtual framebuffer memory is unsafe. Correct clipping and overlap behavior depends on `fb_copyarea()` and valid `area` fields.

## Test Signals

Test with `FBINFO_VIRTFB` set and unset, overlapping copies, reversed-pixels-in-byte config, different bpp modes, and fbcon scroll paths that call copyarea.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/syscopyarea.c -->
