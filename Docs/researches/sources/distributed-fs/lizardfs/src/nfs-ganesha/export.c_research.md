# sources/distributed-fs/lizardfs/src/nfs-ganesha/export.c

## Purpose
Implements export-level operations for the LizardFS FSAL: export teardown, path lookup, wire-handle conversion, object-handle creation, filesystem dynamic info, static capability accessors, and state allocation/free.

## Important APIs, Types, And Functions
`lzfs_fsal_export_ops_init` fills `struct export_ops`. Key operations include `lzfs_fsal_release`, `lzfs_fsal_lookup_path`, `lzfs_fsal_wire_to_host`, `lzfs_fsal_create_handle`, `lzfs_fsal_get_fs_dynamic_info`, static info accessors such as maxread/maxwrite/ACL support, and `lzfs_fsal_alloc_state`/`lzfs_fsal_free_state`.

## Control Flow
Lookup path normalizes Ganesha export paths, validates the requested path begins with `ctx_export->fullpath`, handles root specially, then uses `liz_cred_lookup` from `SPECIAL_INODE_ROOT` and creates a FSAL handle if needed. Wire handles are inode-sized blobs with endian correction. Create-handle fetches attributes for the inode and builds an object handle. Release detaches export, frees root handle, drains fileinfo cache while releasing underlying LizardFS file handles, destroys the LizardFS instance, and frees export memory.

## State And Persistence Behavior
Owns export lifetime state: root handle, `liz_t` instance, optional pNFS fileinfo cache, and static operation tables. Runtime persistence is remote LizardFS state; this file manages local cleanup.

## Dependencies And Integration Points
Depends on Ganesha FSAL config/commonlib, `common/special_inode_defs.h`, `context_wrap`, `lzfs_internal`, and `fileinfo_cache` APIs. It composes with `main.c` export creation and `handle.c` object operations.

## Risks And Edge Cases
Path prefix validation is string-based and depends on exact `fullpath` normalization. Root lookup sets `*pub_handle` but still proceeds to call `liz_cred_lookup`, so root attrs can be refreshed but unnecessary errors could affect root path resolution. Release must drain cache entries only after marking cache max/timeout zero; leaks or double releases would affect long-running Ganesha processes.

## Test Signals
Export creation/destruction, path lookup under subfolder exports, handle serialization round trips, and statfs behavior are key integration signals.
