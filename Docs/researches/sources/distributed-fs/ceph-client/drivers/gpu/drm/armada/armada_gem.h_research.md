# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_gem.h

## Purpose

`armada_gem.h` defines the Armada GEM object wrapper and declarations for GEM allocation, backing, mapping, dumb-buffer, PRIME, import, and lookup helpers.

## Important APIs, Types, And Functions

`struct armada_gem_object` embeds `struct drm_gem_object` and stores CPU address, physical address, device address, mapped flag, linear allocator node, small backing page, imported sg table, and an update callback/data pointer. `drm_to_armada_gem()` converts from base GEM object. Declarations cover free, linear backing, CPU mapping, private allocation, dumb create, PRIME export/import, import mapping, and `armada_gem_object_lookup()`.

## Control Flow

The header itself has no runtime control flow. `armada_gem_object_lookup()` calls `drm_gem_object_lookup()` and converts the result to the Armada wrapper. Other functions are implemented in `armada_gem.c` and called by framebuffer, fbdev, cursor, ioctl, and PRIME paths.

## State And Persistence Behavior

The struct defines all persistent per-buffer backing state. `addr` indicates CPU accessibility, `phys_addr`/`dev_addr` support MMIO scanout and mmap fault insertion, `mapped` gates scanout framebuffer creation, `linear`/`page`/`sgt` identify backing type, and `update` allows CPU writes to trigger hardware cursor reloads.

## Dependencies And Integration Points

The header depends on DRM GEM types and is included by Armada CRTC, framebuffer, fbdev, and driver code. It integrates custom GEM ioctls with core DRM GEM handles and PRIME.

## Risks And Edge Cases

Consumers must respect backing-type invariants: not every object has `addr`, not every object is scanout-mapped, and imported objects need explicit mapping before framebuffer use. The update callback pointer must be cleared before cursor object release to avoid use-after-free callbacks.

## Test Signals

Compile coverage, GEM handle lookup tests, cursor object lifetime tests, imported object scanout mapping, dumb-buffer creation, and object free coverage for page/linear/imported cases validate the header contract.
