# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_gem.c

## Purpose

`xen_drm_front_gem.c` implements GEM object allocation, import, mmap, SG-table export, vmap/vunmap, and backend-allocated page handling for the Xen PV display frontend.

## Important APIs, Types, And Functions

Internal `struct xen_gem_object` extends `drm_gem_object` with page array, backend-allocation flag, and imported SG table. Public APIs are `xen_drm_front_gem_create()`, `xen_drm_front_gem_free_object_unlocked()`, `xen_drm_front_gem_get_pages()`, `xen_drm_front_gem_get_sg_table()`, `xen_drm_front_gem_import_sg_table()`, `xen_drm_front_gem_prime_vmap()`, and `xen_drm_front_gem_prime_vunmap()`.

## Control Flow

GEM creation rounds size to page boundaries and creates the GEM object. For backend allocation it allocates a page-pointer array and Xen unpopulated pages for grant mapping. For frontend allocation it obtains shmem-backed GEM pages. Mmap clears `VM_PFNMAP`, sets mixed/DONTEXPAND flags, uses normal cacheable protection, and inserts all pages with `vm_map_pages()`. PRIME import creates a GEM shell, converts SG entries to a page array, then shares the imported pages with the backend through `xen_drm_front_dbuf_create()`.

## State And Persistence Behavior

Object lifetime state includes page arrays, unpopulated pages or shmem pages, imported SG table references, and backend display-buffer state created by the core file. Freeing reverses those resources and releases the GEM object.

## Dependencies And Integration Points

It depends on DRM GEM/PRIME/shmem helpers, DMA-buf, scatterlists, Xen balloon/unpopulated pages, and core frontend buffer creation/free callbacks. The DRM driver uses it for dumb buffers and PRIME import/export.

## Risks And Test Signals

Risks include leaks on error paths in PRIME import after partial allocation, backend allocation grant mapping assumptions, page-attribute requirements on ARM Xen, and the FIXME that mmap installs pages eagerly without a fault handler. Test mmap CPU access, PRIME import/export, backend-allocated buffers, object free during unplug, SG offset handling, and allocation failure unwinding.
