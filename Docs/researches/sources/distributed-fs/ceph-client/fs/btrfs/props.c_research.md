# sources/distributed-fs/ceph-client/fs/btrfs/props.c

Purpose: implements Btrfs inode properties stored as `btrfs.*` xattrs. The current handler set supports the inheritable `btrfs.compression` property and maps xattr values to in-memory inode compression flags and persisted xattr items.

Important APIs/types/functions: `struct prop_handler` describes each property with validate, apply, extract, ignore, and inheritance hooks. Public entry points are `btrfs_props_init()`, `btrfs_validate_prop()`, `btrfs_ignore_prop()`, `btrfs_set_prop()`, `btrfs_load_inode_props()`, and `btrfs_inode_inherit_props()`. Compression-specific hooks are `prop_compression_validate()`, `prop_compression_apply()`, `prop_compression_ignore()`, and `prop_compression_extract()`.

Control flow: initialization hashes handlers by Btrfs name hash. Validation rejects malformed or unknown xattr names, then delegates to the handler. Setting a property writes or removes the backing xattr with `btrfs_setxattr()` and applies the in-memory state; if apply fails after write, it rolls the xattr back. Loading inode props scans xattr items for matching handler names and applies values. Inheritance copies inheritable properties from a parent inode to a new inode when supported, reserving extra metadata only after the first property.

State and persistence: persistent state lives in xattr tree items. Runtime state includes `BTRFS_INODE_HAS_PROPS`, inode compression/nocompress flags, and `inode->prop_compress`. Compression values can set filesystem incompat bits for LZO or ZSTD.

Dependencies and integration: integrates xattr handling, inode creation, transactions, compression helpers, directory item parsing, metadata reservation, and Btrfs inode runtime flags.

Risks and test signals: the handler hash depends on xattr name hashing matching item offsets during iteration. `btrfs_set_prop()` removes the xattr on apply failure but does not restore a previous value. Inheritance assumes one current property for reservation sizing. Test signals include valid and invalid compression values, property deletion, ignored inode modes, inherited directory compression, mount-time inode property reload, rollback on injected apply failure, and metadata reservation failures when more properties are added.
