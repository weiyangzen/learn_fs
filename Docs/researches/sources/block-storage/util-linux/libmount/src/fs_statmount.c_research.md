# File Research: sources/block-storage/util-linux/libmount/src/fs_statmount.c

This file adapts Linux `listmount/statmount` support into `libmnt_fs`. It provides a shared `libmnt_statmnt` object for buffer reuse, default masks, and on-demand fetching control, then applies kernel `ul_statmount` data into existing filesystem entries.

Key entry points:

- `mnt_new_statmnt()`, `mnt_ref_statmnt()`, `mnt_unref_statmnt()`.
- `mnt_statmnt_set_mask()` configures the default statmount mask.
- `mnt_statmnt_disable_fetching()` temporarily disables lazy statmount fetches to avoid recursion.
- `mnt_fs_refer_statmnt()` attaches shared statmount settings to a filesystem entry.
- `mnt_fs_get_statmnt()` returns the attached statmount settings.
- `mnt_fs_fetch_statmount()` fetches and applies kernel mount-node data.

Important behavior:

- When `HAVE_STATMOUNT_API` is absent, construction fails with `ENOSYS` and fetch returns `-ENOTSUP`.
- `apply_statmount()` fills only missing fields: fstype, target, root, source, propagation, classic/unique IDs, parent IDs, namespace ID, devno, VFS options, and FS options.
- VFS options are synthesized from `MOUNT_ATTR_*` flags (`ro/rw`, `nosuid`, `nodev`, `noexec`, `nodiratime`, `nosymfollow`, and atime mode).
- Superblock options are synthesized from `SB_*` flags (`ro/rw`, `sync`, `dirsync`, `lazytime`), while `STATMOUNT_MNT_OPTS` options are unmangled into `fs_optstr`.
- `mnt_fs_fetch_statmount()` ORs explicit masks with shared default masks, skips already-fetched bits via `fs->stmnt_done`, derives `uniq_id` from the target path if needed, and can reuse the shared `libmnt_statmnt` buffer.

Dependencies and interactions:

- Used by `fs.c` getters under `HAVE_STATMOUNT_API`.
- Depends on low-level `ul_statmount()`, `mnt_id_from_path()`, option-string append helpers, unmangling, and kernel statmount/mount-attr constants.

Risk notes:

- The code computes a namespace ID variable but calls `ul_statmount()` with namespace argument `0`; this appears intentional or incomplete depending on the `ul_statmount` wrapper contract.
- `fs->stmnt_done` is ORed with the requested mask even after errors, which can suppress repeated attempts for the same mask.
- Lazy getter behavior means an apparently simple field access can fail to populate data if the mountpoint path is unavailable.
