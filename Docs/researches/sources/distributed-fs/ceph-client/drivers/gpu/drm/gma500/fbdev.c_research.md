<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/fbdev.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/fbdev.c

## Purpose

This file implements fbdev emulation support for GMA500 when DRM fbdev emulation is enabled. It allocates a stolen-memory-backed GEM framebuffer for the console, maps it into fbdev, and provides fb mmap/destroy callbacks.

## Important APIs, Types, And Functions

The exported probe is `psb_fbdev_driver_fbdev_probe()`. Local pieces are `psb_fbdev_vm_fault()`, `psb_fbdev_fb_mmap()`, `psb_fbdev_fb_destroy()`, `psb_fbdev_fb_ops`, and an empty `drm_fb_helper_funcs` table.

## Control Flow

Fbdev probe adjusts packed 24 bpp requests to 32 bpp, computes fourcc/pitch/size, allocates a stolen GEM object named `"fb"`, falls back from >16 bpp to 16 bpp on stolen-memory `-EBUSY`, creates a GEM handle and DRM client buffer, links fb helper state, maps `info->screen_base` directly to `dev_priv->vram_addr + offset`, fills fb info, sets physical smem and MMIO ranges, clears the framebuffer, then drops the temporary GEM handle and object reference. Mmap only accepts zero offset, sets VM flags, and faults physical stolen-memory PFNs through `vmf_insert_mixed()`.

## State And Persistence

Persistent fbdev state lives in `drm_fb_helper`, `drm_client_buffer`, `fb_info`, and the stolen GEM object referenced by the framebuffer. Hardware-visible state is the stolen memory contents and GTT allocation. The fbdev mapping is noncached and maps physical stolen memory directly.

## Dependencies And Integration Points

It depends on DRM fb helper/client APIs, GMA GEM allocation, PCI resource reporting, and stolen-memory mapping initialized by `psb_gem_mm_init()`. It is conditionally linked by the Makefile.

## Risks And Test Signals

Risks include vm fault mapping all VMA pages starting at adjusted address, direct stolen-memory access cache attributes, limited fallback only on `-EBUSY`, and correct teardown of helper/client/buffer references. Test signals are fbcon at 16/32 bpp, mmap from `/dev/fb*`, stolen-memory exhaustion, mode changes through fbdev, destroy/unload, and fbdev-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/fbdev.c -->
