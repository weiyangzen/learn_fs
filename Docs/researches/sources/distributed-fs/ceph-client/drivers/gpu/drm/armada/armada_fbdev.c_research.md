# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_fbdev.c

## Purpose

`armada_fbdev.c` implements fbdev emulation backing for the Armada DRM driver when `CONFIG_DRM_FBDEV_EMULATION` is enabled. It allocates a private linear GEM buffer, maps it for CPU access, wraps it in an Armada framebuffer, and initializes `fb_info`.

## Important APIs, Types, And Functions

The exported function is `armada_fbdev_driver_fbdev_probe()`, referenced through `ARMADA_FBDEV_DRIVER_OPS`. `armada_fb_ops` combines `FB_DEFAULT_IOMEM_OPS`, DRM fb helper ops, and a custom destroy hook. `armada_fbdev_fb_destroy()` finalizes the helper, destroys the framebuffer, and releases the DRM client.

## Control Flow

Fbdev probe builds a `drm_mode_fb_cmd2` from requested surface size/depth/bpp, computes pitch with `armada_pitch()`, allocates a private GEM object, backs it from linear memory, maps it with `armada_gem_map_object()`, creates an Armada framebuffer, drops the initial GEM reference, sets fbops and screen memory fields, stores helper callbacks/framebuffer, fills fb_info, and logs allocation details. Error paths drop GEM references on failed backing or mapping.

## State And Persistence Behavior

The fbdev buffer is a private, linear-backed GEM object with CPU mapping in `obj->addr`. `fb_info` stores physical start, length, screen size, and screen base. The framebuffer holds the long-lived reference after creation. Destroy tears down the fb helper, framebuffer, and client.

## Dependencies And Integration Points

The file depends on Linux fb APIs, DRM fb helper/client infrastructure, Armada pitch, GEM allocation/backing/mapping, and Armada framebuffer creation. It is conditionally compiled by the Makefile and exposed through driver ops in `armada_drm.h`.

## Risks And Edge Cases

The fbdev path requires contiguous linear graphics memory and a successful WC mapping. `armada_framebuffer_create()` may fail after GEM mapping; the code drops the initial GEM reference and relies on framebuffer lifetime only on success. The helper uses I/O-memory fb ops, so `FB_IOMEM_HELPERS` must be selected.

## Test Signals

Boot console/fbdev smoke tests, fbdev emulation enabled/disabled builds, framebuffer allocation at common depths, mmap/write/read through fbdev, cleanup on unregister, and memory-leak/refcount checks are useful signals.
