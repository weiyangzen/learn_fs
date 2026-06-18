# sources/distributed-fs/ceph-client/fs/cachefiles/namei.c

## Purpose
`namei.c` owns CacheFiles path walking, directory creation/pinning, backing object lookup/creation/opening, tmpfile commit, object burial/culling, and active-inode marking.

## Important APIs, Types, and Functions
Important APIs include `cachefiles_unmark_inode_in_use`, `cachefiles_get_directory`, `cachefiles_put_directory`, `cachefiles_bury_object`, `cachefiles_delete_object`, `cachefiles_create_tmpfile`, `cachefiles_look_up_object`, `cachefiles_commit_tmpfile`, `cachefiles_cull`, and `cachefiles_check_in_use`. Important local helpers include active mark/unmark functions, `cachefiles_unlink`, `cachefiles_create_file`, `cachefiles_open_file`, and `cachefiles_lookup_for_cull`.

## Control Flow
Directory setup uses `start_creating`, creates missing directories after space and LSM checks, marks directory inodes with `S_KERNEL_FILE` to block culling/removal, verifies directory operations and xattr support, and returns pinned dentries. Object lookup searches the fanout directory for the cooked object name, buries weird non-regular entries, opens regular files with `O_DIRECT`, initializes on-demand state, checks xattr coherency, and creates tmpfiles for missing or stale objects. New objects are unlinked tmpfiles until commit. Commit starts a create lookup, removes any stale conflicting entry, links the tmpfile into place, and clears the tmpfile flag. Burial unlinks files directly or renames directories into the graveyard with unique names. Cull and inuse commands look up candidates while rejecting in-use `S_KERNEL_FILE` inodes.

## State and Persistence Behavior
Persistent state is the backing directory tree: root `cache`, `graveyard`, volume directories, fanout directories, object files, linked tmpfiles, and graveyard entries. Runtime active state is encoded by `S_KERNEL_FILE` on backing inodes so userspace culling and CacheFiles object access do not collide. Release counters are updated when active objects are unmarked.

## Dependencies and Integration Points
The file uses VFS helper protocols (`start_creating`, `end_creating`, `start_removing`, `start_renaming_dentry`), LSM path checks, CacheFiles xattrs, object size/content state from `interface.c`, culling thresholds from `cache.c`, on-demand initialization, tracepoints, and FS-Cache kill reasons.

## Risks and Edge Cases
Inode marking is central: missed unmarking can make entries permanently uncullable, while missed marking can let userspace remove active cache files. Tmpfile commit races with another creator and must loop by unlinking stale entries. Directory burial must avoid mountpoints and directory loops. `cachefiles_check_in_use` depends on lookup helpers that may return with parent locks held, making lock discipline important.

## Test Signals
Test new object creation, stale xattr replacement, weird file type burial, tmpfile commit races, culling busy and idle objects, directory and file unlink errors, graveyard rename collision retries, mountpoint rejection, and active-inode mark/unmark leak detection.
