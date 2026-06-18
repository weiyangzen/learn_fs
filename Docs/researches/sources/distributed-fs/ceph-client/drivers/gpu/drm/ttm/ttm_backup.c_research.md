# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_backup.c

Purpose: shmem-backed page backup service used by TTM pool shrinking and TT backup/restore. It converts page indices to nonzero handles, writes page contents into shmem, copies them back, drops backed-up ranges, and reports available swap-backed capacity.

Important APIs and functions: `ttm_backup_shmem_create()` creates a shmem file. `ttm_backup_backup_page()` reads or creates a shmem folio at an index, marks it accessed/dirty, copies the source page, optionally starts writeback with `shmem_writeout()`, and returns a handle. `ttm_backup_copy_page()` reads a folio by handle and copies it into a destination page. `ttm_backup_drop()` truncates the page range for a handle. `ttm_backup_fini()` drops the file reference. `ttm_backup_bytes_avail()` exports approximate backup space based on swap pages.

State and persistence: data persists in an anonymous shmem file until dropped or `fput()`. Handles are `idx + 1` so zero can represent no content or error-like state. Dirty/writeback state is managed at folio level.

Dependencies and integration: used by `ttm_pool_backup()`, `ttm_pool_restore_and_alloc()`, and shrinking paths. It depends on shmem, folios, swap accounting, and page copy helpers.

Risks and test signals: reclaim-context callers must respect `__GFP_FS` and `__GFP_IO` constraints documented in comments. `ttm_backup_bytes_avail()` is approximate, so backup attempts can still fail. Local test coverage is indirect through TT swap and BO swapout tests, while partial backup/restore failures rely on pool fault-injection paths.
