# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcmap.c

## Purpose

This file implements fbdev colormap allocation, copying, userspace transfer, hardware programming, default palettes, and default palette inversion. The complete 363-line source was read.

## Important APIs, Types, and Functions

Exported APIs include `fb_alloc_cmap_gfp()`, `fb_alloc_cmap()`, `fb_dealloc_cmap()`, `fb_copy_cmap()`, `fb_cmap_to_user()`, `fb_set_cmap()`, `fb_set_user_cmap()`, `fb_default_cmap()`, and `fb_invert_cmaps()`. Static default palettes include 2-, 4-, 8-, and 16-color RGB arrays and `struct fb_cmap` wrappers.

## Control Flow

Allocation frees/reallocates cmap arrays when length changes, optionally allocates transparency, resets start/len, and copies an appropriate default cmap. Copy helpers compute overlapping ranges based on source/destination starts and lengths, then copy RGB and optional transparency arrays. `fb_set_cmap()` validates the start and callbacks, either calls driver `fb_setcmap()` or iterates entries through `fb_setcolreg()`, and copies the cmap into `info->cmap` on success. `fb_set_user_cmap()` allocates a kernel cmap, copies userspace arrays in, locks the fb, applies it, unlocks, and frees temporary arrays. `fb_invert_cmaps()` bitwise-inverts all static default palette arrays.

## State and Persistence Behavior

State includes allocated cmap arrays in each `fb_info` and static default palettes marked read-mostly. Palette changes affect in-memory fb state and hardware through driver callbacks. `fb_invert_cmaps()` permanently mutates the process-wide default arrays for the running kernel.

## Dependencies and Integration Points

It depends on fbdev driver callbacks `fb_setcolreg()` and `fb_setcmap()`, userspace copy helpers, allocation APIs, and fb locking. It is used by fbdev core ioctls, drivers during initialization, fbcon, and logo palette setup.

## Risks and Edge Cases

`fb_alloc_cmap()` uses `GFP_ATOMIC`, which may fail for larger palettes under pressure; `fb_alloc_cmap_gfp()` ORs `__GFP_NOWARN` into caller flags. `fb_set_cmap()` stops iterating when `fb_setcolreg()` returns nonzero but still returns `rc` initialized to zero, so partial programming can look successful for drivers using the per-register callback. `fb_set_user_cmap()` checks integer overflow with signed `int size`, but very large lengths still need careful bounds behavior. Default cmap inversion is global and irreversible except by another inversion.

## Test Signals

Test allocation/deallocation for lengths 0/2/4/8/16/256 with and without transparency, overlapping cmap copies, userspace get/set ioctls with partial faults, driver `fb_setcmap()` versus `fb_setcolreg()` paths, per-register failure behavior, default cmap selection thresholds, and invert/uninvert cycles.
