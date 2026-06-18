# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_fbdev.c

## Purpose

`radeon_fbdev.c` implements the DRM fbdev helper backend for Radeon. It creates a pinned VRAM GEM object for fbcon, wraps it in a DRM framebuffer, maps it for CPU access, fills `fb_info`, manages runtime-PM references for fbdev opens, and destroys the pinned object when fbdev is torn down.

## Important APIs, Types, and Functions

- `radeon_fbdev_driver_fbdev_probe()` is the fbdev probe callback used by `RADEON_FBDEV_DRIVER_OPS`.
- `radeon_fbdev_create_pinned_object()` calculates pitch/size, creates a VRAM GEM object, optionally applies tiling/swap flags, pins it with legacy CRTC restrictions, and maps it.
- `radeon_fbdev_destroy_pinned_object()` unmaps, unpins, unreserves, and drops the GEM reference.
- `radeon_fbdev_fb_open()` and `radeon_fbdev_fb_release()` pair runtime PM get/put around fbdev users.
- `radeon_fbdev_fb_destroy()` finalizes the fb helper, unregisters/cleans the framebuffer, frees it, releases the pinned object, and releases the DRM client.

## Control Flow

Probe receives desired surface dimensions/depth, coerces 24 bpp to 32 bpp on AVIVO scanout hardware, converts legacy bpp/depth to a DRM format, creates the pinned object, allocates and initializes a Radeon framebuffer with `radeon_framebuffer_init()`, assigns helper funcs and fb ops, fills `fb_info`, computes the physical aperture address from BO GPU offset and VRAM aperture base, points `screen_base` at the mapped BO, clears the framebuffer with `memset_io()`, and logs mapping details.

## State and Persistence Behavior

Fbdev state is anchored in `drm_fb_helper`, `fb_info`, the DRM framebuffer, and the pinned Radeon BO. The BO remains pinned and CPU-mapped for console use until fbdev destruction. Runtime PM references persist while fbdev is open.

## Dependencies and Integration Points

The file depends on Linux fbdev, DRM fb helper, DRM GEM framebuffer helpers, Radeon GEM/BO creation, pitch alignment from `radeon_gem.c`, framebuffer initialization from `radeon_display.c`, runtime PM, and ASIC family checks. It is connected to the DRM driver through `RADEON_FBDEV_DRIVER_OPS` in `radeon_mode.h`.

## Risks and Edge Cases

- `fb_tiled` is hardcoded false but the code contains tiling paths; enabling it would need broad scanout and CPU mapping testing.
- 24 bpp on AVIVO is silently adjusted to 32 bpp.
- Legacy CRTC pinning restricts addresses to 27 bits; failures must unwind object state exactly once.
- Runtime PM open tolerates `-EACCES` but releases the PM reference for other failures.

## Test Signals

Test fbcon creation/destruction, low-VRAM format selection from driver probe, suspend/resume with fbcon, runtime PM open/release, panic/console writes to `screen_base`, legacy pre-AVIVO address restrictions, big-endian swap flag behavior, and error unwinding after create/pin/map failures.
