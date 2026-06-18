# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_info.c

## Purpose

This file implements allocation and release of `struct fb_info` objects and optional driver-private data. The complete 80-line source was read.

## Important APIs, Types, and Functions

The exported APIs are `framebuffer_alloc(size_t size, struct device *dev)` and `framebuffer_release(struct fb_info *info)`.

## Control Flow

Allocation computes padding so private data is long-aligned after `struct fb_info`, zero-allocates the combined block, sets `info->par` when requested, stores the parent device pointer, initializes rotation hint and blank state, and initializes the backlight curve mutex when enabled. Release ignores NULL, warns and returns if the embedded refcount is nonzero, destroys the backlight mutex when enabled, and frees the allocation.

## State and Persistence Behavior

The allocated `fb_info` and private data are in-memory state only. The function initializes default blanking state to unblanked and rotation hint to -1.

## Dependencies and Integration Points

It is used by nearly all fbdev drivers before registering a framebuffer. It depends on fbdev struct layout, slab allocation, refcount discipline from registration/open paths, and optional backlight mutex state.

## Risks and Edge Cases

Drivers must call `framebuffer_release()` only after unregistering and dropping all references; otherwise the WARN path intentionally leaks rather than freeing a live object. The padding macro assumes long alignment is sufficient for private data.

## Test Signals

Test allocation with zero and nonzero private sizes, alignment of `info->par`, default field initialization, backlight mutex init/destroy under config, release with NULL, and release with artificially nonzero refcount.
