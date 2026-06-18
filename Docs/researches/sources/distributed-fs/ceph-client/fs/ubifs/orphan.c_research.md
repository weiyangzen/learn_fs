<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/orphan.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/orphan.c

## Purpose
`orphan.c` manages inode numbers whose inode node has reached link count zero but whose storage must survive until open references are closed or crash recovery deletes them. It keeps an in-memory orphan tree/list during runtime, writes orphan nodes during commit, consolidates the fixed orphan area when space is low, and kills persisted orphans after unclean unmount.

## Important APIs, Types, and Functions
Public functions are `ubifs_add_orphan()`, `ubifs_delete_orphan()`, `ubifs_orphan_start_commit()`, `ubifs_orphan_end_commit()`, `ubifs_clear_orphans()`, and `ubifs_mount_orphans()`. Key private functions include `lookup_orphan()`, `orphan_delete()`, `avail_orphs()`, `tot_avail_orphs()`, `write_orph_node()`, `consolidate()`, `commit_orphans()`, `erase_deleted()`, `do_kill_orphans()`, and `kill_orphans()`. Runtime state lives in `c->orph_tree`, `orph_list`, `orph_new`, `orph_cnext`, `orph_dnext`, counters, `ohead_lnum/off`, and `orph_buf`.

## Control Flow
`ubifs_add_orphan()` allocates an orphan, inserts it into an rb-tree keyed by inode number, appends it to global and new lists, and enforces `c->max_orphans`. `ubifs_delete_orphan()` removes or defers deletion depending on whether the orphan is currently in a commit snapshot. Commit begins with `ubifs_orphan_start_commit()`, which moves all new orphans to a `cnext` chain, clears `orph_new`, and updates `no_orphs`.

`ubifs_orphan_end_commit()` writes pending orphan nodes via `commit_orphans()` and then frees delayed deletions. If the tail has insufficient room, `consolidate()` rewrites all non-new orphans from the beginning of the orphan area using atomic LEB changes and unmaps unused LEBs. Mount calls `ubifs_mount_orphans()`: clean writable mounts erase the orphan area, while unclean mounts scan orphan nodes with `kill_orphans()` and remove zero-link inodes from TNC.

## State and Persistence
Persistent orphan nodes contain `cmt_no` plus inode numbers; the high bit of `cmt_no` marks the last orphan node for that commit. This lets recovery ignore out-of-date LEBs after a fully marked newer commit. In-memory flags `new`, `cmt`, and `del` prevent losing orphans across commit/delete races. The fixed orphan area lies between LPT and main area, and `ohead_lnum/off` tracks append position.

## Dependencies and Integration Points
The file integrates with VFS unlink/open semantics, UBIFS commit sequencing, TNC removal (`ubifs_tnc_remove_ino()`), inode lookup (`ubifs_tnc_lookup()`), scanning/recovery (`ubifs_scan()`, `ubifs_recover_leb()`), master `no_orphs`, and debug index walks. Recovery ordering matters with `recovery.c` GC commit and `replay.c` TNC updates.

## Risks and Test Signals
Risks include orphan-area exhaustion, duplicate/missing orphan entries, incorrect `cmt_no` ordering, deletion during commit, O_TMPFILE/linkat rebirth, read-only recovery deferral, and corruption inside orphan LEBs. Tests should cover unlink-open-crash, multiple orphan nodes per commit, consolidation under pressure, clean mount clearing, unclean mount killing, out-of-date orphan LEBs, delayed deletion lists, and debug `dbg_check_orphans()` walks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/orphan.c -->
