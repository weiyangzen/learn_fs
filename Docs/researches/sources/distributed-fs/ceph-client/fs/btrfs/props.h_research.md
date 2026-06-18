# sources/distributed-fs/ceph-client/fs/btrfs/props.h

Purpose: exposes the Btrfs inode-property API used by xattr, inode-load, and inode-create paths.

Important APIs/types/functions: declares initialization, validation, ignore checks, setting, loading, and inheritance helpers: `btrfs_props_init()`, `btrfs_validate_prop()`, `btrfs_ignore_prop()`, `btrfs_set_prop()`, `btrfs_load_inode_props()`, and `btrfs_inode_inherit_props()`.

Control flow: no implementation flow. The prototypes indicate which paths need a transaction (`set` and `inherit`), which operate on loaded inode state (`validate`, `ignore`, `load`), and which require a caller-supplied path for scanning persisted xattr items.

State and persistence: no state in the header. It defines the boundary for code that mutates persisted property xattrs and runtime inode property flags.

Dependencies and integration: forward declarations keep this header independent of full inode/path/transaction definitions while making the property subsystem available across Btrfs.

Risks and test signals: prototype drift is the main risk. Build coverage of xattr, inode load, and create paths catches signature mismatches; behavior tests should focus on the implementation in `props.c`.
