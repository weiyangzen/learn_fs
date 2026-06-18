# File Research: sources/cow-pools/bcachefs-tools/fs/snapshots/check_snapshots.c

Implements snapshot fsck/recovery checks. It validates `snapshot_tree` keys against root snapshot nodes and master subvolumes, repairing or deleting bad tree records and choosing replacement master subvolumes when needed.

Snapshot checks verify parent/child backpointers, subvolume links, snapshot-tree pointers, depth fields, and skiplist ancestors. Repairs can clear invalid subvol references, recreate/repair snapshot tree pointers, update depths, regenerate skiplist entries, and sort skiplists.

It can reconstruct missing single-node snapshot trees by scanning snapshot-aware btrees, recreating snapshot nodes when possible, and requiring recovery passes before deleting keys in missing snapshots. `__bch2_check_key_has_snapshot()` deletes keys in definitively deleted snapshots and carefully gates deletion for missing snapshots behind consistency/reconstruction checks.
