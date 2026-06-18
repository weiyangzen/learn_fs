# sources/distributed-fs/ceph-client/fs/btrfs/export.h

## Purpose
`export.h` declares the Btrfs exportfs interface and defines the packed file-handle payload used by `export.c`.

## Important APIs, types, and functions
The key type is packed `struct btrfs_fid`, containing child `objectid`, `root_objectid`, `gen`, optional `parent_objectid`, `parent_gen`, and optional `parent_root_objectid`. The header declares `btrfs_export_ops`, `btrfs_get_dentry`, and `btrfs_get_parent`.

## Control flow
Exportfs consumers call through `btrfs_export_ops`; direct Btrfs users can resolve a dentry by objectid/root/generation or ask for a dentry's parent. The packed struct layout is used by `export.c` to compute handle lengths in 32-bit words, so field order is part of the encoded ABI.

## State and persistence
The header stores no runtime state. Its file-handle layout persists in NFS/export clients and must remain compatible with existing handle decoding. Generation fields provide stale-handle detection against on-disk inode identity.

## Dependencies and integration points
It includes Linux `exportfs.h` and integer types, forward-declares VFS structures, and is consumed by Btrfs super/export setup plus any Btrfs code that needs direct parent/dentry resolution.

## Risks and test signals
Risks are ABI/layout changes to the packed handle, incorrect assumptions about alignment, and incomplete parent-root data for cross-subvolume reconnects. Test signals include handle encode/decode compatibility, NFS reconnect across kernel upgrades, cross-subvolume exports, and stale file-handle tests.
