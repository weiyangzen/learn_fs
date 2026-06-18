# sources/distributed-fs/ceph-client/fs/btrfs/export.c

## Purpose
`export.c` implements Btrfs export operations for file handles, primarily for NFS/exportfs. It encodes Btrfs inode/root/generation identity into stable file handles, resolves handles back to dentries, finds parents across normal directory entries and subvolume roots, and returns child names for reconnecting paths.

## Important APIs, types, and functions
The exported operations table is `btrfs_export_ops`. Key functions are `btrfs_encode_fh`, `btrfs_get_dentry`, `btrfs_fh_to_parent`, `btrfs_fh_to_dentry`, `btrfs_get_parent`, and `btrfs_get_name`. The code uses `struct btrfs_fid` from `export.h` and exportfs handle types `FILEID_BTRFS_WITHOUT_PARENT`, `FILEID_BTRFS_WITH_PARENT`, and `FILEID_BTRFS_WITH_PARENT_ROOT`.

## Control flow
Encoding stores the inode objectid, subvolume root objectid, and generation; when a parent is supplied it stores parent objectid/generation and, if parent and child are in different roots, the parent root id. Decoding validates handle length/type, then calls `btrfs_get_dentry`, which rejects reserved objectids, obtains the requested root with `btrfs_get_fs_root`, igets the inode, verifies generation when present, and returns an alias dentry. Parent lookup searches either `BTRFS_INODE_REF_KEY` in the current root or `BTRFS_ROOT_BACKREF_KEY` in the tree root for subvolume roots, then obtains the parent inode/dentry. Name lookup reads the inode-ref or root-ref name bytes from the relevant leaf and null-terminates them for exportfs reconnect.

## State and persistence
File handles persist outside the kernel in export clients and encode enough on-disk identity to detect stale inodes via generation mismatches. Runtime state is limited to allocated paths, held roots, iget references, and dentries. It relies on Btrfs root and inode items/backrefs as persistent metadata.

## Dependencies and integration points
The file integrates Btrfs with Linux exportfs through `struct export_operations`. It depends on root lookup from `disk-io.c`, inode loading from Btrfs inode code, tree searches, accessors for inode/root refs, dentry aliasing, and VFS inode generation. It is sensitive to Btrfs subvolume semantics because parent and child may belong to different roots.

## Risks and test signals
Risks include stale handle detection, incorrect handle length negotiation, cross-subvolume parent encoding, missing or corrupt inode/root backrefs, name buffer sizing by exportfs callers, and reserved objectid handling. The source snapshot contains an apparent duplicated `btrfs_iget` call in `btrfs_get_parent`; review should confirm whether this is an accidental duplication because it would affect reference handling if compiled as-is. Test signals include NFS export of regular files and subvolumes, reconnect after rename/snapshot/delete, stale generation handles, parent lookup across subvolume boundaries, malformed short handles, and filesystem corruption tests for missing backrefs.
