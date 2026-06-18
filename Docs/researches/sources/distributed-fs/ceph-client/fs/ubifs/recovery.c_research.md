<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/recovery.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/recovery.c

## Purpose
`recovery.c` implements UBIFS crash recovery for master nodes, log/bud LEBs, index/LPT heads, deferred read-only cleanup, GC state, and inode-size inconsistencies. It accepts corruption patterns consistent with interrupted flash writes and rejects patterns that imply older or unrelated corruption.

## Important APIs, Types, and Functions
Public entry points are `ubifs_recover_master_node()`, `ubifs_write_rcvrd_mst_node()`, `ubifs_recover_leb()`, `ubifs_recover_log_leb()`, `ubifs_recover_inl_heads()`, `ubifs_clean_lebs()`, `ubifs_rcvry_gc_commit()`, `ubifs_recover_size_accum()`, `ubifs_recover_size()`, and `ubifs_destroy_size_tree()`. Important private helpers are `get_master_node()`, `write_rcvrd_mst_node()`, `is_last_write()`, `no_more_nodes()`, `fix_unclean_leb()`, `drop_last_group()`, `drop_last_node()`, `recover_head()`, `grab_empty_leb()`, `fix_size_in_place()`, and `inode_fix_size()`.

## Control Flow
Master recovery scans both master LEBs with `get_master_node()`, tolerates one last-write corruption area, chooses the newest valid consistent copy, and either writes a recovery-marked master immediately or stores it for later read-write remount. Generic LEB recovery scans nodes until empty/garbage/bad padding/corruption, verifies the problem is at the last plausible write, drops incomplete grouped nodes and special GC-head min-I/O content, pads/cleans the rest, and writes the fixed LEB unless mounted read-only.

`ubifs_recover_log_leb()` only permits recovery at the log end by comparing the next log LEB against the commit-start sequence. `ubifs_recover_inl_heads()` cleans index and LPT head locations left by half-completed commits. `ubifs_rcvry_gc_commit()` reconstructs a valid GC LEB, runs a commit to persist replay/orphan/size fixes, and may garbage-collect a dirty LEB into the GC head. Size recovery accumulates journal inode/data/truncation observations into an rb-tree, then removes data without an inode or grows inode sizes either in-place or through journal writes.

## State and Persistence
The file manipulates `rcvrd_mst_node`, `unclean_leb_list`, `gc_lnum`, journal-head write buffers, `size_tree`, pinned inodes, and master dirty/recovery flags. It deliberately avoids flash modification during read-only mount, recording pending cleanups for `ubifs_clean_lebs()` and `ubifs_write_rcvrd_mst_node()` when remounted writable.

## Dependencies and Integration Points
Recovery depends on scanner/node validation, UBI read/change/unmap APIs, journal heads, log commit-start nodes, lprops and GC selection, TNC lookup/removal, inode journal writes, LPT/master/orphan replay ordering, and authenticated node preparation. `super.c`, `replay.c`, and `orphan.c` call into these helpers during mount and remount.

## Risks and Test Signals
Risks are over-accepting real corruption, under-accepting valid power-cut tails, mishandling grouped nodes or GC head padding, failing read-only deferral, choosing the wrong master copy, and ordering GC/orphan/size commits incorrectly. Tests should use power-cut/failure-mode emulation across master writes, log tail writes, bud writes, GC head writes, index/LPT head writes, readonly-to-rw remount, orphan deletion, and inode-size replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/recovery.c -->
