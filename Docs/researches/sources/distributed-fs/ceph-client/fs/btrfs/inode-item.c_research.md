# sources/distributed-fs/ceph-client/fs/btrfs/inode-item.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/inode-item.c` implements Btrfs inode item helpers for inode references/backreferences, extended inode references, empty inode item insertion, inode lookup, and truncation/removal of inode-associated items and file extents. It is used by directory/link management, inode creation/deletion, free-space cache inode truncation, and file truncate paths. The file was read as a complete 733-line implementation.

## Important APIs, Types, and Functions

Exported lookup/search helpers are `btrfs_find_name_in_backref`, `btrfs_find_name_in_ext_backref`, and `btrfs_lookup_inode_extref`. Reference mutation APIs are `btrfs_insert_inode_ref` and `btrfs_del_inode_ref`; internally they may call `btrfs_insert_inode_extref` or `btrfs_del_inode_extref` when standard inode ref items overflow or extended refs are required. Inode item helpers are `btrfs_insert_empty_inode` and `btrfs_lookup_inode`. The major truncate API is `btrfs_truncate_inode_items()`.

`btrfs_trace_truncate()` bridges truncation decisions into tracepoints for inline and regular file extents. `struct btrfs_truncate_control` is declared in the header and drives truncate behavior through fields such as inode, new size, target inode number, minimum key type, skip-ref-updates, clear-extent-range, and output accounting.

## Control Flow

Name lookup in regular backrefs scans the payload of a `BTRFS_INODE_REF_KEY` item, walking variable-length `struct btrfs_inode_ref` records until a name-length and name comparison matches. Extended backref lookup computes `btrfs_extref_hash(parent, name)` for the item key, searches the tree, and then scans collisions inside the item for matching parent and name.

Insertion first tries a regular inode ref item keyed by inode objectid and parent objectid. If the key exists, it appends a new variable-length ref unless the same name is already present. If insertion overflows the item and the filesystem has `EXTENDED_IREF`, it falls back to inserting/appending an extended inode ref keyed by hash. Deletion does the inverse: remove the regular ref if present, compact or delete the item, and if not found, search and delete the extended inode ref. Extended ref deletion aborts the transaction if the key exists but the named ref cannot be found, because that indicates unexpected metadata inconsistency.

`btrfs_lookup_inode()` is a wrapper around `btrfs_search_slot()` that handles the special root item lookup convention where callers may search for offset `-1` and accept the previous matching root item.

`btrfs_truncate_inode_items()` searches backward from the maximum key for an inode, deleting items with type greater than or equal to `control->min_type`. For file extents, it computes extent end, decides whether to delete or shrink based on `new_size`, handles regular/prealloc extents by updating `num_bytes` or preparing delayed extent reference drops, handles inline extents by shrinking unencoded inline data or returning `BTRFS_NEED_TRUNCATE_BLOCK` for encoded partial-inline truncation, optionally clears the inode file-extent range, batches adjacent item deletions, refills delayed-ref reservation when needed, and backs off with `-EAGAIN` for shareable roots after large deletion work.

## State and Persistence Behavior

All persistent state is stored in Btrfs btree items: inode items, inode ref items, inode extended ref items, root items, and file extent items. Regular and extended refs contain variable-length names stored directly inside item payloads. Truncation mutates file extent items, deletes btree items, queues delayed reference drops through `btrfs_free_extent()`, updates caller-visible counters in `btrfs_truncate_control`, and may clear ranges from the runtime inode file-extent map when operating on a real inode. It does not own long-lived state outside the btree and caller-provided control structure.

## Dependencies and Integration Points

Direct dependencies include `ctree.h`, `fs.h`, `messages.h`, `inode-item.h`, `disk-io.h`, `transaction.h`, `space-info.h`, `accessors.h`, `extent-tree.h`, and `file-item.h`. It integrates with fscrypt name strings, extent buffers, btree path/search/insert/delete/truncate/extend primitives, delayed refs, file-extent map clearing, inode byte accounting, tracepoints, root/shareable-state handling, and feature flags for extended inode refs.

## Risks and Edge Cases

Backref items are variable length, so item-size and memmove calculations must be exact to avoid corrupting adjacent refs. Extended refs use a CRC32C-derived hash and must scan collisions by parent and name. Filesystems without `EXTENDED_IREF` can hit `-EMLINK` when regular inode ref items overflow. Deleting an extref key that lacks the expected named ref is treated as filesystem inconsistency and aborts the transaction. Truncation has many corner cases: partial regular extents require aligned `num_bytes`, inline extents with compression/encryption/other encoding cannot be partially shrunk in place, delayed refs can exhaust reservation and force `-EAGAIN`, and `skip_ref_updates` must only be used when the caller has another way to handle extent refs. The comment `FIXME blocksize != 4096` near extent deletion is a useful audit signal for non-4K assumptions.

## Test Signals

Tests should cover hard-link creation/removal, duplicate-name insertion returning `-EEXIST`, fallback to extended refs under large ref arrays, hash-collision behavior for extrefs, deletion compaction of multi-ref items, root item lookup with offset `-1`, file truncation of regular/prealloc/inline extents, encoded inline partial truncate returning `BTRFS_NEED_TRUNCATE_BLOCK`, delayed-ref reservation pressure returning `-EAGAIN`, free-space cache inode truncation through `btrfs_truncate_free_space_cache()`, and fsck verification after crash injection around reference or truncate mutations.
