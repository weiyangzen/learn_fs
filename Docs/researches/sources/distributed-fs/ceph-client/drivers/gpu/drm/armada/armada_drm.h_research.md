# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_drm.h

## Purpose

`armada_drm.h` defines shared private structures, helpers, variant operations, fbdev hooks, and debugfs declarations for the Armada DRM driver.

## Important APIs, Types, And Functions

Inline helpers include `armada_updatel()` for read/modify/write MMIO updates and `armada_pitch()` for 128-byte-aligned scanout pitch calculation. `struct armada_variant` defines per-variant `init`, `compute_clock`, `disable`, and `enable` callbacks. `struct armada_private` embeds `struct drm_device`, stores up to two CRTC pointers, a `drm_mm` linear allocator protected by `linear_lock`, shared plane property pointers, and debugfs root. The header declares `armada510_ops`, overlay creation, fbdev probe hook, and debugfs init functions.

## Control Flow

The header has no top-level control flow. Its helpers are called during framebuffer/dumb allocation, CRTC setup, variant programming, and register updates. Conditional macros provide fbdev driver ops only when fbdev emulation is configured.

## State And Persistence Behavior

`struct armada_private` defines the master DRM device state, especially the linear graphics-memory allocator used by GEM and the CRTC array used by components. Variant callbacks persist in each CRTC. `armada_updatel()` mutates hardware registers only when the value changes. `armada_pitch()` provides persistent ABI-visible pitch values returned to dumb-buffer callers.

## Dependencies And Integration Points

The header depends on Linux kfifo/io/workqueue includes, DRM device/mm/fb helper types, and local CRTC/GEM declarations. It integrates `armada_drv.c`, CRTC, GEM, framebuffer, fbdev, overlay, plane, and debugfs code.

## Risks And Edge Cases

`armada_pitch()` has special handling for 4bpp and aligns every pitch to 128 bytes; changing it affects userspace buffer layouts. `armada_updatel()` uses relaxed MMIO and no locking; callers must provide ordering and serialization. Conditional fbdev ops must remain synchronized with Makefile object selection.

## Test Signals

Build coverage with fbdev/debugfs enabled and disabled, dumb-buffer pitch tests for multiple bpp values, GEM allocator lockdep, register-update behavior, and probe with one or two CRTCs validate this shared contract.
