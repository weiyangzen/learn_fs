# sources/distributed-fs/ceph-client/fs/btrfs/dir-item.c

## Purpose

`dir-item.c` implements Btrfs directory item and xattr item insertion, lookup, collision checking, name matching, and deletion. Btrfs stores names under hash keys; a single tree item can contain multiple `btrfs_dir_item` records when names hash to the same key, so the file includes overflow handling for extending existing items and scanning subitems by name.

## Important APIs, Types, and Functions

Public APIs are `btrfs_insert_xattr_item()`, `btrfs_insert_dir_item()`, `btrfs_lookup_dir_item()`, `btrfs_check_dir_item_collision()`, `btrfs_lookup_dir_index_item()`, `btrfs_search_dir_index_item()`, `btrfs_lookup_xattr()`, `btrfs_match_dir_item_name()`, and `btrfs_delete_one_dir_name()`. The key helper is `insert_with_overflow()`, which inserts an empty item or extends an existing hash-collision item after verifying no exact name match exists.

## Control Flow

Insertion builds a key from directory inode/xattr objectid, item type, and `btrfs_name_hash()`. Xattr insertion validates name plus data length against the filesystem xattr limit, inserts/extends the item, fills a zero location key and xattr flags, and writes name/data bytes. Directory insertion inserts the name-hash item, marks encrypted names with `BTRFS_FT_ENCRYPTED`, writes the pointed-to inode key and name, then queues the secondary `BTRFS_DIR_INDEX_KEY` through delayed inode code unless the root is the tree root.

Lookup uses `btrfs_search_slot()` through `btrfs_lookup_match_dir()`, then scans the item payload with `btrfs_match_dir_item_name()`. Collision checking returns success for no hash item, `-EEXIST` for an exact name, `-EOVERFLOW` if extending the hash-collision item would exceed leaf capacity, or an underlying search error. Directory index search can either look up an exact index/name pair or scan index items from offset zero until a matching name is found.

Deletion removes one subitem from a hash item. If the subitem length equals the whole item, it deletes the tree item. Otherwise it memmoves following subitems over the removed record and truncates the item.

## State and Persistence Behavior

This file directly mutates Btrfs tree leaves inside transactions. Directory hash items and xattr items are persistent on commit; secondary directory index insertions are queued as delayed items and persisted by delayed-inode flushing. No independent long-lived state is kept in this file.

## Dependencies and Integration Points

Dependencies include ctree search/insert/delete/truncate helpers, extent buffer accessors, transaction handles, disk key conversion, CRC32C name hashing, fscrypt name strings, delayed inode secondary index insertion, and Btrfs directory item accessors. It is used by inode operations, xattr code, lookup/unlink/rename, readdir, and logging paths.

## Risks and Edge Cases

Hash collisions require exact subitem scanning; callers must not treat a found key as a found name. Leaf capacity limits can return `-EOVERFLOW` even when the hash key exists. Directory insertion can have a primary insert result and a delayed-index insert result; collision on the primary name jumps to secondary insertion logic. Encrypted directories set a file-type flag in the directory item. Deletion pointer arithmetic must correctly compute subitem lengths including xattr data payloads.

## Test Signals

Tests should include colliding names, xattrs near maximum size, duplicate directory names, deletion from single-subitem and multi-subitem hash items, encrypted directory entries, tree-root directory entries that skip delayed indexes, lookup by hash and by directory index, and leaf-full collision overflow.
