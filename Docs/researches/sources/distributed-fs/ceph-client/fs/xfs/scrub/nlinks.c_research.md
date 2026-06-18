# sources/distributed-fs/ceph-client/fs/xfs/scrub/nlinks.c

## Purpose
`nlinks.c` implements live filesystem-wide inode link count scrub. Link counts are treated as derived summary metadata: the scrubber builds shadow counts by walking every inode and every directory entry, applies live directory updates via notifier hooks, and compares the resulting observations against `i_nlink` and directory parent/backreference invariants.

## Important APIs, Types, And Functions
The public setup and entry points are `xchk_setup_nlinks` and `xchk_nlinks`. They allocate `struct xchk_nlink_ctrs`, enable directory-entry fsgates, optionally prepare repair state through `xrep_setup_nlinks`, and call `xchk_setup_fs`.

The main phases are `xchk_nlinks_setup_scan`, `xchk_nlinks_collect`, and `xchk_nlinks_compare`. Collection uses `xchk_nlinks_collect_metafiles`, `xchk_nlinks_collect_dir`, `xchk_nlinks_collect_file`, `xchk_nlinks_collect_dirent`, and `xchk_nlinks_collect_pptr`. Comparison uses `xchk_nlinks_compare_inode`, `xchk_nlinks_compare_inum`, and `xchk_nlinks_comparison_read`.

`xchk_nlinks_update_incore` stores `struct xchk_nlink` records in an `xfarray`, using sparse loads and stores keyed by inode number. `careful_add` clamps counters to `U32_MAX` so overlarge observations become detectable without overflowing. `xchk_nlinks_live_update` shadows concurrent directory changes through `xfs_dir_hook`.

## Control Flow
Setup creates an `xfarray` large enough for the highest possible inode, initializes an iscan with retry behavior, installs the dirent hook, and registers deferred cleanup. Collection first accounts superblock-rooted metadata inodes, then cancels the transaction and uses an empty transaction while iterating all allocated inodes. Directories are locked with IOLOCK plus an ILOCK mode capable of reading data and parent-pointer forks, walked through `xchk_dir_walk`, and, on parent-pointer filesystems, xattr-walked for `XFS_ATTR_PARENT` records. Non-directories are only marked visited.

Comparison restarts with an empty transaction, walks allocated inodes through a second iscan, and compares observed totals to live inode state. A second pass walks unscanned shadow records to catch observations for inodes that could not be obtained, using AGI protection to distinguish absent inodes from races.

## State And Persistence Behavior
All observation state is in memory: `xfarray` records, two `xchk_iscan` cursors, a mutex, and the directory hook. Persistent state is not changed by scrub. The file sets scrub state flags such as corrupt, warning, xref corrupt, and incomplete. Cleanup aborts the iscan, removes hooks, destroys the array and mutex, and leaves repair able to reuse the shadow data only if the scrub phase completed enough to keep `sc->buf_cleanup` active.

## Dependencies And Integration Points
This file depends on inode scanning, sparse arrays, directory walking, parent-pointer xattr walking, temporary-file exclusion, tracepoints, scrub transactions, and orphanage/nlinks repair headers. It integrates with `scrub.c` through `xchk_nlinks`, with `nlinks_repair.c` by preserving collected data for repair, and with directory update hooks to maintain consistency on a live filesystem.

## Risks And Edge Cases
The major risk is false corruption from incomplete collection; the code aggressively sets `INCOMPLETE` when collection errors or hooks abort. Parent-pointer filesystems count backreferences from xattrs instead of dotdot entries. Filesystems without filetype information use backrefs as a fallback for directory child counts. Zapped directories or parent-pointer forks return busy/incomplete because repair of lower-level structures must run first. Missing or invalid inode numbers, malformed names, excessive link totals, orphaned linked inodes, and observations for absent inodes are all flagged.

## Test Signals
Useful tests include live rename/link/unlink churn during nlink scrub, parent-pointer and non-parent-pointer filesystems, ftype=0 behavior, corrupted `.` and `..` entries, zapped directory or attr forks, metadata inode accounting, link counts above `XFS_MAXLINK`, and races where an observed inode cannot be iget during comparison.
