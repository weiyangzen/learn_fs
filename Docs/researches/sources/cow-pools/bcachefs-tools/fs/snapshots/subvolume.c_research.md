# File Research: sources/cow-pools/bcachefs-tools/fs/snapshots/subvolume.c

Implements subvolume validation, fsck repair, lookup, creation, unlink, deletion, and upgrade initialization. Check paths verify subvolume-to-snapshot links, root subvolume parent rules, `subvolume_children` index entries, root inode existence and `bi_subvol`, and master-subvolume consistency for non-snapshot subvolumes.

Bkey ops validate positions, snapshot IDs, and root inode fields; triggers maintain the `subvolume_children` btree when filesystem path parents change. Lookup helpers can report missing subvolumes by scheduling inode checks.

Deletion reparents snapshot-subvolume creation children, clears master-subvolume references if needed, deletes the subvolume key, and marks the associated snapshot node deleted. Unlink first marks a subvolume unlinked and schedules pagecache eviction before deletion. Creation allocates a new subvolume slot and either creates a new snapshot tree or splits an existing snapshot node into two children.
