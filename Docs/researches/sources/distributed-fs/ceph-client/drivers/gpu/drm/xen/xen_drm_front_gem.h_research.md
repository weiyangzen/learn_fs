# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_gem.h

## Purpose

`xen_drm_front_gem.h` declares the GEM helper interface used by the Xen PV frontend DRM driver.

## Important APIs, Types, And Functions

It declares create, PRIME import, SG-table export, page-array access, free, vmap, and vunmap functions, with forward declarations for DRM, DMA-buf, SG, and iosys-map types.

## Control Flow

No runtime flow exists in the header.

## State And Persistence Behavior

No state is owned by the header; it describes operations on GEM objects allocated by the implementation.

## Dependencies And Integration Points

It connects `xen_drm_front.c` and DRM driver callbacks to the GEM implementation without exporting the private `struct xen_gem_object`.

## Risks And Test Signals

Risks are declaration drift and mismatched callback signatures. Module link and PRIME/dumb-buffer build coverage validate it.
