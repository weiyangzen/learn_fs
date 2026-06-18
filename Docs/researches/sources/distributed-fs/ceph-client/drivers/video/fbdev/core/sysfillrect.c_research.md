<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/sysfillrect.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/sysfillrect.c

## Purpose

`sysfillrect.c` is the system-memory wrapper for packed-pixel framebuffer rectangle fills. It validates that the framebuffer is expected to be virtually addressable and then delegates to the generic fill implementation. The file was read as a complete 30-line source.

## Important APIs, Types, and Functions

The single exported API is `sys_fillrect(struct fb_info *p, const struct fb_fillrect *rect)`. It includes `sysmem.h` and `fb_fillrect.h`, with optional byte pixel reversal via `CONFIG_FB_SYS_REV_PIXELS_IN_BYTE`.

## Control Flow

`sys_fillrect()` checks for `FBINFO_VIRTFB`; missing support produces a one-time warning. It then calls `fb_fillrect(p, rect)`.

## State and Persistence Behavior

No file-local state exists. The operation mutates framebuffer memory according to `rect`; warning suppression state belongs to the common warning helper.

## Dependencies and Integration Points

Framebuffer drivers use this as `fbops->fb_fillrect` for CPU-addressable packed-pixel framebuffers. Fbcon clear and margin paths commonly reach this helper through driver fbops.

## Risks and Edge Cases

The helper should not be used for non-virtual framebuffers. Correct raster operation, color interpretation, clipping, and bpp handling are delegated to `fb_fillrect()`.

## Test Signals

Test fill rectangles across bpp modes, ROP_COPY and other supported rops, reversed-pixel config, warning behavior without `FBINFO_VIRTFB`, and fbcon clear/margin workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/sysfillrect.c -->
