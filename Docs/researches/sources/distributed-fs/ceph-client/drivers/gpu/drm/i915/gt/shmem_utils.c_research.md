# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/shmem_utils.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/shmem_utils.c

### Purpose
`shmem_utils.c` provides i915 helpers for creating shmem files from data or GEM objects, pin-vmapping shmem-backed files, and reading/writing file contents page by page.

### Important APIs, Types, And Functions
Exports are `shmem_create_from_data()`, `shmem_create_from_object()`, `shmem_pin_map()`, `shmem_unpin_map()`, `shmem_read_to_iosys_map()`, `shmem_read()`, and `shmem_write()`. Internals include `__shmem_rw()` and use `struct file`, `struct page`, `struct iosys_map`, and `struct drm_i915_gem_object`.

### Control Flow
Creation allocates a tmpfs file with `shmem_file_setup()` and writes initial data, or returns an existing shmem GEM filp with an extra ref. Non-shmem GEM objects are CPU-mapped, copied into a new shmem file, and unmapped. Mapping collects all pages, `vmap()`s them with `VM_MAP_PUT_PAGES`, and marks the mapping unevictable until unpinned. Read/write helpers iterate pages, kmap locally, copy, dirty on write, mark accessed, and drop page refs.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
Persistent state is the shmem file contents and temporary unevictable mapping state. Dependencies include tmpfs, page cache APIs, vmap, iosys-map copying, GEM shmem/lmem helpers, and optional included selftests. Integration points include GuC ADS golden-context copying and firmware/data staging that needs file-like shmem. Risks include file-size page alignment assumptions, `void *` pointer arithmetic, unevictable state leaks if unpin is skipped, and handling lmem with WC mappings. Test signals include `st_shmem_utils.c`, read/write round trips, map visibility of writes, and failure unwinds on page or vmap allocation errors.
