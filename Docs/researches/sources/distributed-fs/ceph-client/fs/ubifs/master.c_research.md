<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/master.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/master.c

## Purpose
`master.c` reads, validates, authenticates, and writes the UBIFS master node. The master node is the mount-time root of durable filesystem state: log head, index root, LPT root/head/table positions, GC LEB, counters, orphan flag, space statistics, and authentication hashes.

## Important APIs, Types, and Functions
Public functions are `ubifs_compare_master_node()`, `ubifs_read_master()`, and `ubifs_write_master()`. Private helpers are `mst_node_check_hash()`, `scan_for_master()`, and `validate_master()`. Important persistent type is `struct ubifs_mst_node`; important in-memory targets are fields in `struct ubifs_info` such as `zroot`, `lhead_lnum/off`, `ihead_lnum/off`, `lpt_lnum/off`, `nhead_lnum/off`, `ltab_lnum/off`, `lsave_lnum/off`, `lscan_lnum`, `lst`, `bi.old_idx_sz`, `cmt_no`, and `highest_inum`.

## Control Flow
`ubifs_read_master()` allocates `c->mst_node`, calls `scan_for_master()`, falls back to `ubifs_recover_master_node()` on `-EUCLEAN`, clears the recovery flag, copies little-endian master fields into `ubifs_info`, handles volume auto-resize, validates all ranges and counters, and initializes old-index debug checking. `scan_for_master()` scans both master LEBs, requires matching last master nodes at the same offset, ignores common headers and embedded HMAC differences when comparing, and verifies either the superblock master hash or node HMAC for authenticated filesystems.

`ubifs_write_master()` advances `c->mst_offs` by aligned master-node size, unmaps both master LEBs when wrapping, updates `highest_inum` and root-index hash, and writes the same master node to the two master LEBs with HMAC support.

## State and Persistence
Two master copies are maintained for recovery. The common header sequence number and CRC intentionally differ, so comparisons exclude that region; authenticated comparisons also account for HMAC differences. The master node stores the authoritative persistent pointers used by LPT, replay, orphan recovery, and index loading. The `UBIFS_MST_NO_ORPHS` flag becomes `c->no_orphs`; resize updates empty/free/dark totals in memory and in the master buffer for the next write.

## Dependencies and Integration Points
This file depends on scan/recovery (`ubifs_scan()`, `ubifs_recover_master_node()`), node/HMAC/hash helpers, dump/debug helpers, and validation constants from `ubifs.h`. Mount code in `super.c` calls `ubifs_read_master()` before LPT/replay/orphan processing and writes the master during mount/remount/unmount and commit completion.

## Risks and Test Signals
Key risks are accepting mismatched master copies, stale or invalid LPT/index/log pointers, authenticated hash/HMAC regressions, counter overflow near watermarks, resize accounting mistakes, and write wrap-around behavior. Tests should cover single-copy corruption, mismatched offsets, recovery marker handling, authenticated and unauthenticated images, invalid space-stat fields, small master LEB wrap, and resize from older `leb_cnt`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/master.c -->
