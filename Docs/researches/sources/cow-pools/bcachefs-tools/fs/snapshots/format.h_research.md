# File Research: sources/cow-pools/bcachefs-tools/fs/snapshots/format.h

Defines on-disk subvolume, snapshot, and snapshot-tree records. `bch_subvolume` stores flags, snapshot ID, root inode, creation parent, filesystem-path parent, and creation time. Flags encode read-only, snapshot-subvolume, and unlinked state.

`bch_snapshot` stores flags, parent, two children, subvol, tree ID, depth, three skiplist entries, and birth time. Flags encode `WILL_DELETE`, `SUBVOL`, `DELETED`, and `NO_KEYS`. `bch_snapshot_tree` records master subvolume and root snapshot for a persistent snapshot-tree identity.
