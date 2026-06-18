# sources/distributed-fs/ceph-client/fs/jffs2/build.c

## Purpose
`build.c` builds the in-memory JFFS2 filesystem model during mount. It allocates eraseblock structures, initializes block lists, scans the flash medium into inode caches and raw node references, reconstructs directory link counts and parent relationships, removes unlinked/dead inode trees, initializes xattr and summary subsystems, rotates block lists for wear leveling, and computes free-space/GC trigger thresholds.

## Important APIs, types, and functions
The external mount entry is `jffs2_do_mount_fs()`. Internal traversal helpers are `first_inode_chain()`, `next_inode()`, and `for_each_inode`. Build phases are implemented by `jffs2_build_filesystem()`, `jffs2_build_inode_pass1()`, `jffs2_build_remove_unlinked_inode()`, and `jffs2_calc_trigger_levels()`. Key types are `struct jffs2_sb_info`, `struct jffs2_eraseblock`, `struct jffs2_inode_cache`, `struct jffs2_full_dirent`, and `struct jffs2_raw_node_ref`.

## Control flow
`jffs2_do_mount_fs()` initializes `free_size`, computes `nr_blocks`, allocates `c->blocks` with `vzalloc()` or `kzalloc()`, initializes each eraseblock offset/free size, sets up all block-state lists, initializes `highest_ino` and summary state, calls `jffs2_sum_init()`, then calls `jffs2_build_filesystem()`. On success it computes trigger levels and returns. On failure it exits the summary subsystem and frees block storage.

`jffs2_build_filesystem()` sets `JFFS2_SB_FLAG_SCANNING`, calls `jffs2_scan_medium()`, clears scanning, dumps block lists for debug, then sets `JFFS2_SB_FLAG_BUILDING`. Pass 1 iterates all inode caches with `scan_dents`, resolves child inode caches for dirents, marks missing-child raw nodes obsolete, stores `fd->ic`, increments child `pino_nlink`, marks directory children, and flags possible hard-linked directories.

Pass 2 scans for inode caches with zero `pino_nlink` and calls `jffs2_build_remove_unlinked_inode()`. That function marks all raw nodes for the inode obsolete, walks child dirents if the inode was a directory, decrements child link counts, and pushes newly unlinked children onto a `dead_fds` list for iterative cleanup instead of recursion. Pass 2a drains `dead_fds` and repeats removal for children that reached zero links.

The final pass frees temporary `scan_dents`. For directories, it converts `pino_nlink` from a link count to the parent inode number and logs errors if hard-linked directories remain. Then it builds the xattr subsystem, clears the building flag, rotates lists for wear leveling, and returns success.

## State and persistence behavior
This file primarily reconstructs volatile mount state from persistent flash nodes. It marks obsolete raw nodes for missing children and dead inodes, but actual deletion/freeing of inode caches is deferred to erase code after nodes are completely gone. `scan_dents` are temporary mount-build structures; final directory parent information is stored in `pino_nlink` for directories after build. The block lists initialized here (`clean`, `dirty`, `very_dirty`, `erasable`, `erasing`, `free`, `bad`, and others) become the runtime allocation/erase/GC state.

Trigger levels persist only in memory but govern future writes and GC: deletion reserve, write reserve, background GC threshold, GC merge threshold, bad-block GC threshold, very-dirty trigger, and dirty-space no-space cutoff. Calculations scale with flash size, sector size, eraseblock count, and whether obsolete nodes can be marked on medium.

## Dependencies and integration points
`build.c` depends on scan code (`jffs2_scan_medium()`), node obsolescence (`jffs2_mark_node_obsolete()`), inode-cache lookup/freeing, raw-node reference freeing, full-dirent allocation/freeing, xattr subsystem build/clear, summary init/exit, list rotation, and MTD geometry in `jffs2_sb_info`. It is called from mount/superblock setup before background GC and normal operations rely on the reconstructed lists and inode caches.

## Risks and edge cases
Mount build must tolerate stale dirents, deletion dirents (`ino == 0`), missing child inode caches, dead directories with children, and old hard-linked directory artifacts. Incorrect link counting can retain deleted trees or delete live nodes. The overloaded `pino_nlink` field changes meaning from link count to parent inode for directories, so phase ordering matters. Error cleanup must free all `scan_dents` and clear xattrs without double-freeing raw node structures. Large flash devices can require vmalloc for eraseblock arrays, and all passes use `cond_resched()` to avoid long mount-time stalls.

## Test signals
Test mounting clean images, images with stale dirents to missing inodes, deleted directories with nested children, hard-linked directory artifacts, large directories, large flash requiring vmalloc, xattr subsystem build failure, summary init failure, scan failure cleanup, block-list initialization correctness, trigger-level calculations for small/large media, and wear-level list rotation.
