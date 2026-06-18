# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_gem.c

Purpose: implements Loongson GEM object functions on top of TTM BOs, dumb buffer creation, PRIME import/export pinning, vmap/mmap, BO tracking, and debugfs BO listing.

Important APIs/types/functions: `lsdc_gem_object_funcs`, `lsdc_gem_object_create`, `lsdc_prime_import_sg_table`, `lsdc_dumb_create`, `lsdc_gem_init`, and `lsdc_show_buffer_object`.

Control flow: GEM creation calls `lsdc_bo_create`, clears new non-imported BOs, assigns object funcs, and adds the BO to the tracked list. Dumb creation computes size/pitch with descriptor alignment, rejects buffers larger than half VRAM, creates VRAM GEM, and returns a handle. PRIME import creates a GTT-domain BO using the dma-buf reservation and marks it shared. vmap pins, TTM-vmaps, reference-counts mappings, and unpins on final vunmap. mmap delegates to TTM and drops GEM ref.

State and persistence: `ldev->gem.objects` tracks driver-created BOs under mutex. Each `lsdc_bo` carries vmap count, map, sharing count, and TTM state.

Dependencies and integration points: depends on local TTM BO helpers, DRM GEM/PRIME/dumb APIs, dma-resv, and debugfs.

Risks and test signals: BO list removal must be handled by TTM code outside this file; leaks show in debugfs. Dumb error print shifts by pages while labelling MiB. Test dumb create/map, PRIME import/export, vmap/vunmap nesting, mmap, BO debugfs, and large allocation rejection.
