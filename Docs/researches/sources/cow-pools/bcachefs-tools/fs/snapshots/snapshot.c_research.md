# File Research: sources/cow-pools/bcachefs-tools/fs/snapshots/snapshot.c

Implements core snapshot-tree operations and includes extensive design documentation. It defines snapshot-tree text/validation/lookup/create helpers, accelerated ancestor checks using skiplists plus 128-ID ancestor bitmaps, and slow early-recovery fallback walks.

The in-memory snapshot table is RCU-managed and indexed by reversed snapshot IDs. Snapshot triggers populate table entries, state, parent/children, subvol/tree/depth/skip data, ancestor bitmaps, and queue dead-snapshot deletion when `WILL_DELETE` appears.

Also implements snapshot-tree traversal, snapshot lookup, overwrite detection, snapshot-ID allocation for new trees or child pairs, initial snapshot table read, empty-interior cleanup scheduling, snapshot subsystem init/exit, and textual tree reports with per-snapshot accounting/path output.
