# File Research: sources/cow-pools/bcachefs-tools/fs/snapshots/types.h

Defines in-memory snapshot subsystem types. `snapshot_t` stores state, parent, skiplist, depth, normalized children, subvol, tree, and a 128-bit ancestor bitmap. `snapshot_table` is an RCU flexible-array container.

Also defines dynamic-array aliases for snapshot ID lists and interior-deletion lists, `snapshot_delete` background-progress state, `bch_fs_snapshots` subsystem state including create lock and unlinked list, and `subvol_inum`. Comments document the page-cache dirtying race avoided by taking `create_lock` as a writer during snapshot creation.
