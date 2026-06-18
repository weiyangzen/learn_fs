<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gem.h

## Purpose

This header defines the GMA500 GEM object wrapper and public GEM/memory-management API.

## Important APIs, Types, And Functions

`struct psb_gem_object` embeds `struct drm_gem_object` and stores a GTT `resource`, `offset`, `in_gart` reference count, `stolen` flag, `mmapping` flag, and backing `pages`. `to_psb_gem_object()` converts from DRM GEM object. Declared functions are `psb_gem_create()`, `psb_gem_pin()`, `psb_gem_unpin()`, `psb_gem_mm_init()`, `psb_gem_mm_fini()`, and `psb_gem_mm_resume()`.

## Control Flow

The header has no executable flow. Display, cursor, fbdev, and dumb-buffer paths create and pin objects through these declarations.

## State And Persistence

The object fields encode persistent allocation and mapping state: GTT resource ownership, GPU-visible offset, pin lifetime, stolen backing, mmap lifetime, and system pages. These fields drive cleanup and resume reconstruction.

## Dependencies And Integration Points

It includes Linux kernel and DRM GEM definitions and is used by framebuffer, fbdev, display, GTT, and PSB driver core files.

## Risks And Test Signals

Risks include manual refcount semantics in `in_gart`, conflating mmap lifetime with pin lifetime, and GTT resource exposure to non-GTT code. Test signals are compile coverage, object create/free, pin/unpin nesting, stolen versus shmem objects, and resume restoration of objects with non-null `pages`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gem.h -->
