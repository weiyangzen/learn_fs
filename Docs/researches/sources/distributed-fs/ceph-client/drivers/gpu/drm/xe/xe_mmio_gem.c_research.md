
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mmio_gem.c

## Purpose

`xe_mmio_gem.c` wraps a page-aligned physical MMIO region in a private DRM GEM object so authorized userspace can mmap a selected register window through a DRM fake offset. It exists for narrow cases where exposing hardware registers is intentional.

## Important APIs, Types, and Functions

- `struct xe_mmio_gem`: private GEM object containing `drm_gem_object base` and starting `phys_addr`.
- Public API: `xe_mmio_gem_create()`, `xe_mmio_gem_mmap_offset()`, and `xe_mmio_gem_destroy()`.
- GEM callbacks: `xe_mmio_gem_free()`, `xe_mmio_gem_mmap()`, and `xe_mmio_gem_vm_fault()`.
- Hot-unplug fallback: `xe_mmio_gem_vm_fault_dummy_page()` maps a zero dummy page when `drm_dev_enter()` fails.

## Control Flow

Creation validates page alignment, initializes a private GEM object, creates a fake mmap offset, and allows only the creating `drm_file` to use the VMA node. mmap validates exact size and shared mapping, forces noncached IO PFNMAP flags, and defers PFN insertion to the fault handler. Fault handling maps each page of the physical MMIO range, or maps a zero dummy page over the whole VMA after unplug/removal.

## State and Persistence Behavior

The object stores only `phys_addr` and GEM base metadata. VMA-node permissions persist until object destruction. Dummy pages are registered with DRM managed cleanup on the device.

## Dependencies and Integration Points

It depends on DRM GEM private objects, DRM VMA offset management, `drm_dev_enter()` for hot-unplug safety, Linux VM PFN insertion, and Xe device typing. Callers must decide which MMIO regions are safe to expose.

## Risks and Edge Cases

- This is security-sensitive: exposing the wrong register page can compromise stability or isolation.
- `xe_mmio_gem_destroy()` directly frees the GEM object; callers must ensure no remaining references require normal GEM refcount release behavior.
- mmap requires exact object size and shared mapping, while comments describe userspace passing matching length.
- Fault handler maps the entire VMA on each fault, which is simple but could repeat work.

## Test Signals

Tests should cover alignment rejection, fake offset creation, VMA permission enforcement, exact-length mmap, PFN insertion, dummy-page behavior on simulated unplug, and denial of unauthorized file access.
