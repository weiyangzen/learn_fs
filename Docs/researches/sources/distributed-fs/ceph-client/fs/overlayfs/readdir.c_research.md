# sources/distributed-fs/ceph-client/fs/overlayfs/readdir.c

## Purpose
`readdir.c` implements directory iteration for OverlayFS. It merges upper and lower directory entries, handles whiteouts and xwhiteouts, maintains a per-inode merged directory cache, translates inode numbers for xino and impure dirs, supports direct real-dir iteration when safe, and cleans work/index directories during mount and unlink paths.

## Important APIs, types, and functions
Core types are `struct ovl_cache_entry`, `struct ovl_dir_cache`, `struct ovl_readdir_data`, and `struct ovl_dir_file`. Exported functions include `ovl_cache_free()`, `ovl_dir_cache_free()`, `ovl_dir_real_file()`, `ovl_check_empty_dir()`, `ovl_cleanup_whiteouts()`, `ovl_check_d_type_supported()`, `ovl_workdir_cleanup()`, `ovl_indexdir_cleanup()`, and `ovl_dir_operations`.

Important internals include rb-tree lookup/add helpers, `ovl_fill_merge()`, `ovl_dir_read()`, `ovl_dir_read_merged()`, `ovl_cache_get()`, `ovl_cache_update()`, `ovl_cache_get_impure()`, `ovl_iterate_real()`, `ovl_iterate_merged()`, `ovl_iterate()`, `ovl_dir_llseek()`, and `ovl_dir_open()`.

## Control flow
Opening a directory stores an `ovl_dir_file` with the initial real file, whether the inode can be iterated directly, and whether the real file is upper. Iteration resets stale state when position is zero. Non-merge/real dirs can pass through to the real filesystem unless xino, parent merge, or impure state requires translation. Merged dirs build or reuse `ovl_dir_cache`: entries are read layer by layer using `iterate_dir()`, deduplicated by name (or casefolded name), and ordered so lowest-layer offsets remain relatively stable.

Whiteout detection is two-phase: character-device whiteout candidates are checked after reading, while xwhiteout regular files in marked directories can be deferred until emit time. `ovl_iterate_merged()` updates missing `d_ino` values and xwhiteout state lazily before `dir_emit()`. `llseek` proxies to the real file for real dirs and manipulates the cache cursor for merged dirs.

## State and persistence
The per-inode `ovl_dir_cache` stores entries, an rb-tree, refcount, and version. `OVL_I(inode)->version` is incremented by mutations in `util.c`, invalidating old caches. Impure directory caches are not refcounted the same way and may trigger best-effort removal of the `overlay.impure` xattr when no translated entries remain. Workdir/index cleanup mutates upper work directories and index entries using VFS unlink/rmdir/whiteout helpers.

## Dependencies and integration points
The file depends on lookup/path helpers from `namei.c`, flags and xattr helpers from `util.c`, upper operation wrappers from `overlayfs.h`, and copy-up/dir cleanup helpers from `dir.c`. `super.c` uses `ovl_check_d_type_supported()` and index/workdir cleanup during mount.

## Risks
Directory cache consistency depends on correct version increments and locking. Whiteout and xwhiteout handling must avoid exposing hidden lower entries. Inode-number translation can break user expectations if xino overflows or impure cache lookup fails. Cleanup helpers operate on persistent work/index directories and must avoid deleting valid index state.

## Test signals
Exercise merged readdir ordering, duplicate names across layers, whiteouts, xwhiteouts, casefolded names, `seekdir/telldir`, concurrent copy-up while iterating, impure dirs, xino remapping, `d_type` probing, empty-dir checks before rmdir, stale index cleanup, and workdir incompat feature handling.
