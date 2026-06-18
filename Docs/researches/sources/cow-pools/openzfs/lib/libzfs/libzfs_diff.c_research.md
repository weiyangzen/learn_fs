# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_diff.c

## Scope

Implements `zfs diff` support by comparing snapshots, consuming kernel diff records, resolving object IDs to paths/stats, and printing added/removed/modified/renamed file entries.

## APIs And Behavior

- `zfs_show_diffs()` is the public entry point. It sets up snapshot names, mountpoints, a pipe, a worker thread, and invokes `ZFS_IOC_DIFF`.
- Snapshot parsing supports `fromsnap`, abbreviated `@snap`, `tosnap`, live dataset targets, clone-origin comparisons, and just-in-time temporary snapshots via `ZFS_IOC_TMP_SNAPSHOT`.
- `differ()` reads fixed-size `dmu_diff_record_t` records from the pipe and dispatches `DDR_FREE` and `DDR_INUSE` ranges.
- Object resolution uses `ZFS_IOC_OBJ_TO_STATS`; free-object traversal uses `ZFS_IOC_NEXT_OBJ`.
- Output helpers print type markers `+`, `-`, `M`, and `R`, optional timestamps, optional file-type classifiers, parseable separators, color for TTY output, and escaped path bytes unless no-mangle mode is set.
- Rename detection compares object generation, mode, ctime, link counts, and old/new paths.

## State And Dependencies

`differ_info_t` carries dataset/snapshot names, mountpoints, flags, pipe fds, cleanup fd, shares object, and deferred error state. The file depends on snapshot mountpoints under `/.zfs/snapshot/`, mnttab mount discovery, pthreads, pipe2, ZFS diff ioctls, and `find_shares_object()`.

## Risks And Invariants

The worker expects complete fixed-size records; short or malformed records become `EPIPE`/diff-data errors. Path discovery requires permissions and loaded encryption keys. Temporary snapshots depend on a cleanup fd. The implementation intentionally ignores non-ZPL objects and the shares object.
