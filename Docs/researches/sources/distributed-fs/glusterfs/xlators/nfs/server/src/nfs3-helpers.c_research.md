# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs3-helpers.c

## Purpose

`nfs3-helpers.c` is the NFSv3 protocol utility layer. It converts Gluster/POSIX metadata and errors into NFSv3 XDR structures, prepares decode buffers to avoid SunRPC heap churn, builds READDIR/READDIRPLUS lists, maps logging severity, resolves file handles to `loc_t`, and checks export authorization for NFS operations.

## Important APIs, types, and functions

- Error/attribute conversion: `nfs3_errno_to_nfsstat3()`, `nfs3_cbk_errno_status()`, `nfs3_stat_to_fattr3()`, `nfs3_stat_to_post_op_attr()`, `nfs3_stat_to_pre_op_attr()`, and `nfs3_stat_to_wcc_data()`.
- Inode/device mapping: `nfs3_iatt_gfid_to_ino()` honors `nfs.enable-ino32`; `nfs3_map_deviceid_to_statdev()` sets `ia_dev`.
- XDR argument preparation: many `nfs3_prep_*args()` functions pre-seed handle/name pointers before decode.
- Reply filling: `nfs3_fill_*res()` functions populate lookup/getattr/fsinfo/access/readdir/fsstat/create/setattr/mkdir/symlink/readlink/mknod/remove/rmdir/link/rename/read/write/commit/pathconf responses.
- Directory helpers: `nfs3_fill_entry3()`, `nfs3_fill_entryp3()`, `nfs3_free_readdir3res()`, `nfs3_free_readdirp3res()`, and cookie verification.
- Logging: per-operation loglevel functions, `nfs3_loglevel()`, and `nfs3_log_*_call/res()` helpers.
- Resolution/auth: `nfs3_fh_resolve_and_resume()`, root/inode/entry hard-resolution callbacks, and `nfs3_fh_auth_nfsop()`.

## Control flow

Protocol handlers typically prepare argument structs, decode RPC XDR, validate/map a file handle, initialize call state, and call `nfs3_fh_resolve_and_resume()`. Resolution starts with root lookup if needed, then either resolves an inode by GFID or an entry by parent GFID plus basename. It first tries inode-table state and falls back to hard lookup using `nfs_gfid_loc_fill()` or `nfs_entry_loc_fill()`. Completion callbacks update `resolve_ret`, copy stats, link inodes into the table, fix generation context, and resume the original operation callback.

Reply helpers are mostly straight-line: zero the result, set status, return early on failure, map device IDs into stats, convert attrs/WCC data, attach file handles, and set NFS constants such as FSINFO sizes or PATHCONF limits. READDIR builders walk Gluster `gf_dirent_t` lists until the requested count/maxcount is reached and allocate NFS entry chains that must later be freed.

## State and persistence behavior

The file maintains transient per-request state through `nfs3_call_state_t`; persistent protocol identity remains in file handles and inode-table entries. It mutates inode-table state during hard resolution and readdirplus handle generation. It uses root-looked-up flags in `nfs3_state` to avoid repeated root lookups. It does not write durable storage.

## Dependencies and integration points

Dependencies include NFSv3 XDR types, `nfs3.h`, file-handle code, `nfs-fops`, inode wrappers, generic loc helpers, mount auth, Gluster iatt/list/memory/logging utilities, and RPC request/transport APIs. It is called heavily by `nfs3.c` operation handlers and feeds all NFSv3 wire responses.

## Risks and edge cases

- `nfs3_extract_nfs3_fh()` copies `data_len` bytes into a fixed struct without an explicit size check in this helper; callers must validate decoded handle size.
- READDIR sizing is approximate and allocates one object per entry; partial allocation failure returns a shorter list without an explicit error status.
- `nfs3_fh_to_post_op_fh3()` allocates a copied handle and depends on the matching free helper for READDIRPLUS.
- Cookie verification intentionally does not enforce `cookieverf == fd_t address` because of VMware client behavior, weakening stale-cookie detection.
- Resolution has multiple async branches where a failure becomes `EFAULT` if helper return values are unexpected.
- The per-operation loglevel tables are large and duplicated; future status additions can drift across operations.

## Test signals

Tests should cover errno-to-NFS status mapping, zero-filled stat suppression, ino32 hashing, all major reply fillers, WCC data, create/setattr mode translation, READDIR/READDIRPLUS list construction and cleanup, root `.`/`..` inode funging, cookie verification, invalid/stale handle paths, hard GFID and entry resolution, root lookup caching, export auth failures returning access/rofs semantics, and loglevel selection for expected errors.
