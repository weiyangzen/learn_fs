# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_fb.h

## Purpose

`armada_fb.h` declares the Armada framebuffer wrapper and framebuffer creation APIs shared by the DRM master, fbdev, and plane code.

## Important APIs, Types, And Functions

`struct armada_framebuffer` embeds `struct drm_framebuffer` and adds 8-bit hardware `fmt` and `mod` fields. `drm_fb_to_armada_fb()` converts from DRM framebuffer to wrapper. `drm_fb_obj()` obtains the first GEM object as an Armada GEM object. The header declares `armada_framebuffer_create()` and `armada_fb_create()`.

## Control Flow

The header itself has no control flow. Its conversion helpers are used by framebuffer and plane paths to access hardware format state and backing GEM objects. Creation functions are implemented in `armada_fb.c` and called from mode-config and fbdev setup.

## State And Persistence Behavior

The wrapper stores persistent per-framebuffer hardware format metadata derived at creation time. It does not own allocation state directly beyond the embedded DRM framebuffer's GEM references.

## Dependencies And Integration Points

The header depends on DRM framebuffer types and local Armada GEM declarations through including code. It connects `armada_fb.c`, `armada_fbdev.c`, and scanout/plane code.

## Risks And Edge Cases

The `drm_fb_obj()` macro assumes the first object is an Armada GEM object and that all relevant planes share that object. This matches current framebuffer creation restrictions but would need revision for true multi-object planar buffers.

## Test Signals

Compile coverage, framebuffer creation tests, plane scanout using `fmt`/`mod`, and fbdev setup validate this small contract.
