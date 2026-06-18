# sources/distributed-fs/lizardfs/src/nfs-ganesha/ds.c

## Purpose
Implements pNFS data-server handle operations for the LizardFS FSAL.

## Important APIs, Types, And Functions
Registers DS operations in `lzfs_fsal_ds_handle_ops_init`: make handle, handle release, read, write, commit, read_plus, write_plus, pDS release, and permission setup. Internal helpers include `lzfs_int_openfile`, which lazily opens/caches a `liz_fileinfo_t`, and `lzfs_int_clear_fileinfo_cache`, which retires expired fileinfo cache entries.

## Control Flow
`lzfs_fsal_make_ds_handle` decodes a wire handle containing an inode, applies endian correction, allocates `lzfs_fsal_ds_handle`, and initializes Ganesha DS state. DS read/write/commit resolve the export from `ds_hdl->pds->mds_fsal_export`, lazily open the file with no request credentials, extract cached fileinfo, call `liz_cred_read`, `liz_cred_write`, or `liz_cred_flush`, and translate errors to NFSv4 status. Release returns any acquired cache entry, finalizes the DS handle, frees it, and opportunistically clears expired cache entries.

## State And Persistence Behavior
The DS handle stores inode and optional cache entry. The export-level `fileinfo_cache` reuses open LizardFS fileinfo handles across DS operations, bounded by max entries and timeout. Writes persist through LizardFS write/flush semantics; stable writes call flush when requested.

## Dependencies And Integration Points
Depends on Ganesha FSAL/pNFS APIs, `context_wrap`, `lzfs_internal`, and `fileinfo_cache`. It integrates with pNFS MDS layout data emitted by `mds_handle.c` and `mds_export.c`.

## Risks And Edge Cases
DS operations pass `cred == NULL`, creating root-like contexts; that is intentional for data-server access but must match the security model. `lzfs_int_openfile` erases cache entries when open fails but callers must not release erased handles afterward. `read_plus` and `write_plus` are explicitly unsupported. Commit returns success when lazy open fails, assuming there is no descriptor to flush; that can hide unexpected cache/open failures.

## Test Signals
No direct unit test in subset. pNFS read/write/commit integration tests and cache eviction tests are needed.
