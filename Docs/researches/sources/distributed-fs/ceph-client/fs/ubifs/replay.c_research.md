<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/replay.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/replay.c

## Purpose
`replay.c` reconstructs the in-memory view of uncommitted journal data during mount. It scans the log for bud references, scans/recover/authenticates bud LEBs, builds sequence-ordered replay entries, applies them to the TNC, updates bud lprops and journal write-buffer heads, and feeds size recovery when the filesystem was not cleanly unmounted.

## Important APIs, Types, and Functions
The main public function is `ubifs_replay_journal()`, with public validator `ubifs_validate_entry()`. Key local types are `struct replay_entry` and `struct bud_entry`. Important helpers include `take_ihead()`, `replay_log_leb()`, `validate_ref()`, `add_replay_bud()`, `replay_buds()`, `replay_bud()`, `authenticate_sleb()`, `insert_node()`, `insert_dent()`, `apply_replay_list()`, `apply_replay_entry()`, `inode_still_linked()`, `trun_remove_range()`, `set_buds_lprops()`, and `set_bud_lprops()`.

## Control Flow
`ubifs_replay_journal()` first marks the index head LEB taken and verifies `ihead_offs` matches LPT free space. It then walks the circular log from `lhead_lnum`, requiring the first node to be a commit-start node with the current commit number. `replay_log_leb()` validates reference nodes, updates the rolling log hash, creates `ubifs_bud` objects, and stops when it reaches old log data or empty space.

Each `replay_bud()` decides whether the bud is the last in its journal head; only last buds are recoverable after power cut. It scans or recovers the LEB, authenticates nodes when configured, converts inode/data/dent/xent/trunc nodes into replay entries, computes used/dirty/free bytes, and records maximum sqnum/inum. After all buds are scanned, entries are sorted by sqnum and applied to TNC. Deletions remove keys, inode deletions remove all inode keys unless a later O_TMPFILE relink exists, and truncation entries remove data-key ranges. Finally bud lprops are updated and journal write buffers seek to the recovered ends.

## State and Persistence
Replay does not directly persist new nodes; it reconstructs in-memory TNC, bud lists, dirty znodes, `max_sqnum`, `highest_inum`, lprops flags/free/dirty, write-buffer positions, `bi.uncommitted_idx`, and `size_tree` entries. Authentication nodes can cause unauthenticated tail nodes on the last bud to be ignored, but reject unauthenticated content in non-last buds.

## Dependencies and Integration Points
Replay depends on log format, scanner/recovery, HMAC/hash helpers, TNC add/remove APIs, lprops locking and LPT dirty lookup, journal-head write buffers, orphan/size recovery, key helpers, and master commit number/log pointers. It runs after master/LPT initialization and before mount completes, and its lprops changes influence GC and budgeting immediately.

## Risks and Test Signals
High-risk areas include log-end detection, duplicate/invalid reference nodes, sequence ordering, authenticated-tail handling, O_TMPFILE relink detection, truncation range math, bud lprops after GC-before-bud cases, and consistency between scan `endpt` and write-buffer seek positions. Tests should cover multi-head journal replay, corrupt last vs non-last buds, authenticated replay with missing auth node, dent/xent validation, unlink/relink sequences, truncation replay, GC'd bud starting at zero, and ENOSPC/budget behavior after replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/replay.c -->
