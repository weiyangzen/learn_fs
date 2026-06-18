<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gem.c

## Purpose

This file implements GMA500 GEM object allocation, pinning into the GTT and video MMU, dumb-buffer creation, GEM mmap fault handling, stolen-memory setup, and GEM/GTT resource restoration on resume.

## Important APIs, Types, And Functions

Exported functions are `psb_gem_pin()`, `psb_gem_unpin()`, `psb_gem_create()`, `psb_gem_dumb_create()`, `psb_gem_mm_init()`, `psb_gem_mm_fini()`, and `psb_gem_mm_resume()`. Internal helpers include `psb_gem_free_object()`, `psb_gem_fault()`, `psb_gem_mm_populate_stolen()`, and `psb_gem_mm_populate_resources()`. Object callbacks are `psb_gem_object_funcs` and `psb_gem_vm_ops`.

## Control Flow

Creation rounds size to pages, allocates a `psb_gem_object`, reserves GTT address space from stolen or system range, initializes a private stolen GEM object or normal GEM shmem object, and restricts normal mappings to DMA32 pages. Pinning locks the DMA reservation, no-ops for already mapped/stolen objects, gets pages, marks them WC, inserts PTEs into the hardware GTT and driver MMU at `gatt_start + offset`, stores pages, and increments `in_gart`. Unpin decrements, removes MMU/GTT mappings when the last non-stolen pin drops, restores WB caching, and releases pages. Mmap faults pin once and map either stolen PFNs or backing pages directly. MM init maps stolen memory WC and prepopulates stolen pages in the GTT; resume validates stolen size and repopulates stolen and still-pinned resources.

## State And Persistence

`psb_gem_object` stores GEM base, resource, GTT offset, pin count, stolen flag, mmap pin flag, and backing pages. `drm_psb_private` stores stolen base/size, vram mapping, mmap mutex, and GTT tree. Hardware state includes GTT entries and MMU page-directory mappings. Mmap pins intentionally persist until object destruction.

## Dependencies And Integration Points

It depends on DRM GEM, VMA manager, DMA reservations, Linux page cache/cache-attribute helpers, GTT helpers, PSB MMU helpers, PCI stolen-memory register `PSB_BSM`, and fbdev/CRTC paths that allocate or pin buffers.

## Risks And Test Signals

Risks include permanently pinned mmap objects, correct cache attribute restoration, GTT space exhaustion, 32-bit DMA constraints, stolen-size calculation from GTT physical start, and resume ordering with GTT re-enable/clear. Test signals are dumb-buffer create/mmap/page faults, framebuffer display pin/unpin, stolen fbdev allocation, object destruction with mmap pins, suspend/resume with pinned buffers, and GTT/MMU PTE validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gem.c -->
