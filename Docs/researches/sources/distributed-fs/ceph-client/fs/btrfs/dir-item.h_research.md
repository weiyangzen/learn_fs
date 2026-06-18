# sources/distributed-fs/ceph-client/fs/btrfs/dir-item.h

## Purpose

`dir-item.h` declares the internal Btrfs directory and xattr item API plus the CRC32C-based name hash helper. It is consumed by directory operations, xattr code, inode operations, delayed inode flushing/logging, and lookup/delete paths.

## Important APIs, Types, and Functions

The header declares directory collision checking, primary dir item insertion, primary dir item lookup, exact dir-index lookup, scanning dir-index search, one-name deletion, xattr insertion and lookup, and subitem name matching. The inline `btrfs_name_hash()` hashes a byte name with `crc32c((u32)~1, name, len)`.

## Control Flow

There is no major runtime control flow beyond the inline hash helper. The declared functions express the split between hash-based directory/xattr items and index-based directory items.

## State and Persistence Behavior

The header owns no state. Its functions operate on transaction handles, roots, btree paths, inode identifiers, and filesystem name strings to read or mutate persistent tree items.

## Dependencies and Integration Points

Dependencies include Linux types, CRC32C, fscrypt strings, Btrfs keys/paths/inodes/roots/transactions, and the on-disk `btrfs_dir_item` format declared elsewhere. Integration points are lookup, create, unlink, rename, xattrs, readdir indexes, and delayed inode secondary index insertion.

## Risks and Edge Cases

The hash helper is not collision-free, so users of this API must always perform exact name matching. Path ownership and transaction/mod flags are caller-controlled; misuse can leave paths locked or search without required COW for modification.

## Test Signals

Compile coverage should catch signature drift across directory and xattr users. Behavioral tests should include hash collisions, encrypted names, xattr item limits, index lookup/search, and deletion from overflow directory items.
