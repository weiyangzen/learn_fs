# File Research: sources/block-storage/lvm2/lib/activate/fs.c

## Role

`fs.c` implements activation-private filesystem fallback operations for LVM device nodes and symlinks. Its main job is to maintain `/dev/<vg>/<lv>` symlinks to `/dev/mapper/<dm-name>` when udev is unavailable, incomplete, or configured for verification/fallback, and to synchronize those operations with libdevmapper udev cookies.

## Core Behavior

- `_mk_dir()` creates the VG directory under the configured device directory with the device-directory umask and SELinux context preparation.
- `_rm_dir()` removes an empty VG directory after LV symlink removal.
- `_rm_blks()` removes legacy block devices in a VG directory when cleaning up LVM1 device artifacts.
- `_mk_link()` creates or repairs the LV symlink, removes obsolete LVM1 group files and LVM2 links when safe, checks udev-created links when requested, and falls back to direct `symlink()`.
- `_rm_link()` removes an LV symlink after verifying it is actually a symlink.
- `_do_fs_op()` applies add, delete, or rename operations.

## Operation Stacking

When LVM is in a prioritized section, `_fs_op()` queues operations in `_fs_ops` instead of executing them immediately. `_stack_fs_op()` coalesces conflicting add/delete/rename operations, especially when udev is expected to create or remove links. `_pop_fs_ops()` later executes and frees all queued operations.

The file tracks counts by operation type in `_count_fs_ops` and uses `_other_fs_ops()` to decide whether pending non-delete operations exist. `fs_has_non_delete_ops()` exposes that state to activation code so open-count checks can wait for device names to settle.

## Udev Cookie Handling

- `_fs_cookie` starts as `DM_COOKIE_AUTO_CREATE` and is shared with libdevmapper tree operations.
- `fs_ensure_cookie()` creates a udev cookie only when udev sync is enabled and no cookie is active.
- `fs_get_cookie()` and `fs_set_cookie()` transfer cookie state between `fs.c` and `dev_manager.c`.
- `fs_unlock()` waits for udev processing when no devices are suspended, resets the cookie, releases libdm resources, and flushes stacked fs operations.
- `fs_set_create()` records that activation created nodes, causing `fs_has_non_delete_ops()` to report pending create-like work.

## Public Functions

- `fs_add_lv()`, `fs_del_lv()`, `fs_del_lv_byname()`, and `fs_rename_lv()` are the device-link operations used by `dev_manager.c`.
- `fs_ensure_cookie()`, `fs_get_cookie()`, `fs_set_cookie()`, `fs_set_create()`, `fs_has_non_delete_ops()`, and `fs_unlock()` coordinate with activation and libdm.

## Risks and Invariants

- Direct link creation/removal is intentionally conservative: existing non-symlink/non-block files block creation, and non-symlinks are not removed as LV links.
- Udev fallback correctness depends on checking the device number of the udev-created symlink target against the DM target path.
- Queued operation coalescing must preserve final filesystem state across prioritized sections; rename handling is explicitly marked as imperfect.
- `fs_unlock()` skips syncing while devices are suspended, preventing device-name synchronization from racing suspended tables.
