# sources/distributed-fs/ceph-client/fs/xfs/scrub/parent_repair.c

## Purpose
`parent_repair.c` repairs parent relationships. On filesystems without parent-pointer xattrs, it finds the correct directory parent and resets `..`. On parent-pointer filesystems, it rebuilds the target file's parent-pointer xattr structure from all directory entries in the filesystem, preserves non-parent xattrs, atomically exchanges attr forks, adopts parentless files when possible, and fixes nondirectory link counts.

## Important APIs, Types, And Functions
`xrep_setup_parent` creates `struct xrep_parent`, a temporary file, and orphanage context. `xrep_parent` is the public repair entry. The main state object owns parent-pointer staging arrays/blobs, non-parent xattr staging arrays/blobs, temp exchange state, findparent/iscan/hook state, adoption state, name buffers, and counters.

Important routines include `xrep_parent_find_dotdot`, `xrep_parent_scan_dirtree`, `xrep_parent_live_update`, `xrep_parent_replay_updates`, `xrep_parent_reset_dotdot`, `xrep_parent_move_to_orphanage`, `xrep_parent_copy_xattrs`, `xrep_parent_rebuild_pptrs`, `xrep_parent_rebuild_tree`, `xrep_parent_set_nondir_nlink`, and `xrep_parent_setup_scan`.

## Control Flow
Setup enables dirent gates, creates a regular tempfile, and tries to attach orphanage. Without parent pointers, repair uses dcache and filesystem scanning through findparent to choose a parent, then resets dotdot if needed.

With parent pointers, repair allocates buffers and xfile staging, starts an inode scan with a live directory update hook, drops heavy locks and scans all directories for entries pointing to the target. Matching dirents are converted into parent-pointer add records. Live add/remove updates for already scanned directories are stashed too. Staged parent-pointer updates are periodically replayed into the tempfile to cap memory use.

After scanning, it copies all non-parent xattrs from the target to the tempfile, flushing staged xattrs as needed. If parent-pointer updates race with opportunistic flushing, it restarts the copy with stricter locking. It ensures both files have attr forks, allocates an exchange transaction, replays any final parent-pointer updates, swaps attr fork mappings with `xrep_xattr_swap`, resets the tempfile fork, and rolls to a clean transaction. It then discovers whether a parent exists, moves parentless files to the orphanage if allowed, resets dotdot for directories, and updates nondirectory nlink/unlinked-list state from parent-pointer counts.

## State And Persistence Behavior
Persistent effects include replaced parent-pointer attr forks, preserved non-parent xattrs, updated dotdot entries, orphanage adoption, unlinked-list changes, and nondirectory link-count changes. The attr fork replacement is atomic through the temp-exchange path and requires rmapbt plus exchange-range support. Staged state lives in `xfarray`/`xfblob` until flushed or teardown.

## Dependencies And Integration Points
This file integrates with findparent scanning, readdir, tempfile and tempexch helpers, orphanage adoption, xattr repair, parent-pointer APIs, directory update hooks, quota/unlinked-list APIs, and `reap.c` indirectly through xattr fork exchange cleanup. `xrep_parent` is wired as the repair handler for parent scrub.

## Risks And Edge Cases
The most important risks are live rename races, xattr copy races, attr fork absence, memory growth from many hardlinks or xattrs, parentless files when no orphanage is available, metadata-rooted files that intentionally lack parents, and transaction/lock ordering around IOLOCK, ILOCK, tempfile locks, and orphanage locks. Parent-pointer repair is unsupported without rmapbt and exchange-range.

## Test Signals
Tests should include parent-pointer rebuild during concurrent renames, files with many hardlinks, millions of xattrs or remote xattr values, missing attr forks, stale parent pointers, parentless files requiring adoption, nondirectory link count repair, directory dotdot reset, unsupported feature combinations, and interrupted repair before/after CHANGES are committed.
