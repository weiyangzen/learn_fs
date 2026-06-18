# Group Research: group_718_linux_sources_os_linux_linux_fs_btrfs_tree_mod_log_c_sources_os_linu_25822cf7a97e

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tree-mod-log.c -->
# File Research: sources/os/linux/linux/fs/btrfs/tree-mod-log.c

## Purpose

`tree-mod-log.c` implements Btrfs' tree modification log. The log gives long-running readers, especially backref and extent walkers, a stable historical view of internal tree nodes while concurrent operations split, move, replace, free, or promote tree blocks.

The implementation records reversible modifications to non-leaf extent buffers from the extent tree and filesystem trees. A caller obtains a sequence number before walking, writers append tree modification records while that sequence is active, and readers can rewind cloned extent buffers or root nodes back to the requested sequence.

## Core Data Model

`struct tree_mod_elem` is the private log record. It is keyed in an rb-tree by affected logical address and sequence number. Each record stores an operation code, slot, generation, and operation-specific payload:

- key slot changes keep the old key, block pointer, and generation.
- move records keep destination slot and item count.
- root replacement records keep the old root logical address and level.

`struct tree_mod_root` is a compact payload for root replacement history. The public `struct btrfs_seq_list` lives in the header and represents one active log user.

## Sequence Users and Garbage Collection

`btrfs_get_tree_mod_seq()` assigns a fresh sequence to a user that does not already have one, appends it to `fs_info->tree_mod_seq_list`, and sets `BTRFS_FS_TREE_MOD_LOG_USERS`.

`btrfs_put_tree_mod_seq()` removes a user and frees obsolete log records. If lower-sequence users remain, no cleanup is possible. Otherwise all log records with `tm->seq < min_seq` are removed from `fs_info->tree_mod_log`. If the last user leaves, the users flag is cleared and the cleanup threshold becomes `BTRFS_SEQ_LAST`.

`btrfs_tree_mod_log_lowest_seq()` exposes the oldest active sequence, returning 0 when there are no users.

## Logging Filters

`skip_eb_logging()` avoids logging leaves and trees that are irrelevant to the backref use case. Internal nodes from the extent tree and subvolume trees are logged; other trees are skipped.

`tree_mod_need_log()` is the cheap unlocked predicate used before allocation. `tree_mod_dont_log()` rechecks under `tree_mod_log_lock`; when it returns false, it leaves the write lock held so the caller can insert all records atomically relative to sequence users.

This two-step pattern avoids unnecessary allocations when no historical readers exist, while still handling races where readers appear or disappear between the first check and insertion.

## Log Insertion

`tree_mod_log_insert()` assigns a new sequence and inserts a record into the rb-tree. The tree's ordering is intentionally unusual: lower logical addresses go down the left branch, and for the same logical address lower sequence numbers also go left. The paired search helpers understand this order and find either the oldest or newest relevant record for a block.

Allocation helpers prepare records from current node slots before the live tree is modified:

- `alloc_tree_mod_elem()` captures a key pointer slot.
- `tree_mod_log_alloc_move()` captures a move operation.
- `tree_mod_log_free_eb()` inserts a whole set of removal records in reverse slot order.

## Recorded Tree Operations

`btrfs_tree_mod_log_insert_key()` logs a single key add, remove, replace, or related slot operation.

`btrfs_tree_mod_log_insert_move()` logs key movement within a node. When a move toward lower slots overwrites entries, it first logs the overwritten keys as `BTRFS_MOD_LOG_KEY_REMOVE_WHILE_MOVING`, then logs the move itself.

`btrfs_tree_mod_log_insert_root()` logs root replacement, optionally logging all removed children from the old root when the old root is being freed.

`btrfs_tree_mod_log_eb_copy()` logs a copy between internal extent buffers. It records destination-side movement, source removals, destination additions, and source-side movement in the order needed to reconstruct the previous state.

`btrfs_tree_mod_log_free_eb()` logs removal of every key pointer in an internal extent buffer that is being freed.

All multi-record paths allocate first, acquire `tree_mod_log_lock`, then either insert the complete group or unwind partial inserts on failure.

## Searching and Rewinding

`tree_mod_log_search_oldest()` returns the oldest log record for a block at or after a sequence. `tree_mod_log_search()` returns the newest such record. Both are built on `__tree_mod_log_search()`.

`tree_mod_log_oldest_root()` follows `BTRFS_MOD_LOG_ROOT_REPLACE` records backwards from the current root logical address to find the old root that corresponds to a historical sequence.

`tree_mod_log_rewind()` applies inverse operations from newest to oldest for one logical block until it reaches entries older than the requested sequence. It restores removed keys, undoes replacements, drops added keys, reverses moves with `memmove_extent_buffer()`, and ignores root replacement records for non-root rewinds. It also tracks a conservative `max_slot` to warn about invalid move ranges.

## Public Historical Views

`btrfs_tree_mod_log_rewind()` rewinds a read-locked extent buffer. If no matching record exists, or if the buffer is a leaf, it returns the original buffer. Otherwise it clones the buffer or allocates a dummy buffer for a block that had been freed, unlocks/releases the input buffer, locks the replacement, replays inverse log operations, and returns the rewound buffer.

`btrfs_get_old_root()` returns a read-locked root node as of a sequence. It handles root replacement specially: it may read the old root from disk, allocate a dummy buffer, or clone the current root, then replay relevant log entries. It rechecks the newest matching log entry after cloning a disk-read old root to avoid replaying a log sequence inconsistent with the cloned buffer's item count.

`btrfs_old_root_level()` is a lightweight helper that reports the historical root level for a sequence.

## Concurrency and Failure Behavior

The log uses `fs_info->tree_mod_log_lock` for both the rb-tree and sequence-user list. Writers hold it while inserting complete operation groups. Search and rewind hold the read side while walking log records.

Memory allocation is done before taking the write lock where possible. If allocation failed but the locked recheck shows logging is unnecessary, the function returns success. If logging is necessary, allocation failures propagate as `-ENOMEM`.

The code uses `BUG_ON`, `ASSERT`, and `WARN_ON` for invariants that indicate corrupt or inconsistent replay state, such as invalid slot counts or impossible sequence ordering.

## Filesystem Role

This file is a core consistency aid for Btrfs' copy-on-write metadata. It does not persist data on disk; it records transient in-memory history only while users hold tree mod sequences. Its correctness is essential for backref walking, delayed reference processing, send/relocation style tree reads, and other code that needs a coherent old view of metadata while writers continue modifying live trees.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tree-mod-log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tree-mod-log.h -->
# File Research: sources/os/linux/linux/fs/btrfs/tree-mod-log.h

## Purpose

`tree-mod-log.h` declares the public interface for Btrfs' in-memory tree modification log. It is included by code that either records tree mutations or requests historical views of tree blocks.

## Public Types

`struct btrfs_seq_list` represents one active tree mod log user. It contains a list node for `fs_info->tree_mod_seq_list` and the user's sequence number.

`BTRFS_SEQ_LIST_INIT()` initializes a static or stack sequence-list object with an empty list and zero sequence. `BTRFS_SEQ_LAST` is the maximum `u64`, used as the cleanup threshold when no older user remains.

`enum btrfs_mod_log_op` lists every operation that `tree-mod-log.c` can record:

- key replace, add, and remove.
- key removal while freeing a block.
- key removal while moving slots.
- key movement within a node.
- root replacement.

## Public API

The header exposes sequence lifetime helpers:

- `btrfs_get_tree_mod_seq()`
- `btrfs_put_tree_mod_seq()`
- `btrfs_tree_mod_log_lowest_seq()`

It exposes logging hooks for tree modification sites:

- `btrfs_tree_mod_log_insert_root()`
- `btrfs_tree_mod_log_insert_key()`
- `btrfs_tree_mod_log_free_eb()`
- `btrfs_tree_mod_log_eb_copy()`
- `btrfs_tree_mod_log_insert_move()`

It exposes historical read helpers:

- `btrfs_tree_mod_log_rewind()`
- `btrfs_get_old_root()`
- `btrfs_old_root_level()`

## Filesystem Role

The header is the contract between Btrfs tree modification code and readers that need stable old metadata. It intentionally keeps the private rb-tree record format hidden in `tree-mod-log.c`.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tree-mod-log.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/ulist.c -->
# File Research: sources/os/linux/linux/fs/btrfs/ulist.c

## Purpose

`ulist.c` implements a small Btrfs utility container for unique `u64` values with an optional `u64` auxiliary payload. It supports efficient duplicate checks through an rb-tree and iteration through an insertion-order linked list.

The file comments describe its main use case: non-recursive traversal of graphs or trees whose nodes are addressable as 64-bit values, avoiding repeated visits without consuming kernel stack through recursion.

## Container Structure

A `struct ulist` owns:

- `nodes`, a linked list for iteration.
- `root`, an rb-tree keyed by `val` for lookup.
- `nnodes`, the current element count.
- `prealloc`, one optional preallocated node for callers that need to avoid allocation in a later critical section.

Each `struct ulist_node` stores `val`, `aux`, one list node, and one rb-tree node.

## Lifetime Operations

`ulist_init()` initializes a caller-provided `struct ulist`.

`ulist_release()` frees all dynamically allocated nodes and the preallocated node, clears `prealloc`, resets the rb-tree, and reinitializes the list head. It is intended for statically or externally allocated `struct ulist` objects.

`ulist_reinit()` releases contents and then fully initializes the container for reuse.

`ulist_alloc()` allocates and initializes a `struct ulist`.

`ulist_free()` handles NULL, releases all contents, and frees the container itself.

`ulist_prealloc()` allocates a single spare node if none is already present.

## Lookup and rb-tree Helpers

`ulist_node_val_key_cmp()` defines rb-tree ordering by `val`. `ulist_rbtree_search()` uses `rb_find()` to find an existing node.

`ulist_rbtree_insert()` uses `rb_find_add()` and returns `-EEXIST` if a duplicate key already exists. The public add path searches first, so insertion asserts that duplicates are impossible.

`ulist_rbtree_erase()` removes a node from both the rb-tree and list, frees it, and decrements `nnodes`, with a `BUG_ON` guard against underflow.

## Add, Merge, and Delete

`ulist_add()` is a wrapper around `ulist_add_merge()` when the caller does not need the old auxiliary value.

`ulist_add_merge()` searches by `val`. If a node already exists, it optionally returns the existing `aux` through `old_aux` and returns 0. If not found, it consumes `prealloc` or allocates a node, stores `val` and `aux`, inserts into the rb-tree, appends to the linked list, increments `nnodes`, and returns 1. Allocation failure returns `-ENOMEM` and leaves the ulist unchanged.

`ulist_del()` removes an entry only when both `val` and `aux` match. It returns 0 for deletion and 1 when the value is absent or the auxiliary value differs.

## Iteration Semantics

`ulist_next()` walks the linked list using `struct ulist_iterator`. It returns NULL for an empty list or after the final element. The iteration order is the list order, not sorted rb-tree order.

The implementation permits callers to add new elements during enumeration; because new nodes are appended to the list, they will be reached by the running iterator.

## Concurrency Contract

The container performs no internal locking. The comments require caller-provided locking: write locking for mutation and read locking for iteration when rwlocks are used.

## Filesystem Role

`ulist` is a reusable support data structure for Btrfs graph-style algorithms, especially backref and extent relationship walks that need uniqueness, auxiliary metadata, and bounded stack usage.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/ulist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/ulist.h -->
# File Research: sources/os/linux/linux/fs/btrfs/ulist.h

## Purpose

`ulist.h` declares Btrfs' unique-`u64` list container. It exposes the data structures because callers commonly allocate `struct ulist` and iterators directly.

## Public Structures

`struct ulist_iterator` contains the current list cursor used by `ulist_next()`.

`struct ulist_node` is one element. It stores a unique `u64 val`, an auxiliary `u64 aux`, a linked-list node, and an rb-tree node.

`struct ulist` stores the element count, list head, rb-tree root, and optional preallocated node.

## Public API

The header declares:

- initialization and cleanup: `ulist_init()`, `ulist_release()`, `ulist_reinit()`, `ulist_alloc()`, `ulist_free()`.
- allocation preparation: `ulist_prealloc()`.
- mutation: `ulist_add()`, `ulist_add_merge()`, `ulist_del()`.
- iteration: `ulist_next()`.

`ULIST_ITER_INIT()` resets an iterator before enumeration.

## Pointer Auxiliary Helper

`ulist_add_merge_ptr()` adapts `ulist_add_merge()` for pointer auxiliary values. On 64-bit builds it casts the pointer storage directly through `u64 *`. On 32-bit builds it uses a temporary 64-bit value and converts through `uintptr_t`, avoiding an invalid direct 64-bit pointer alias.

## Filesystem Role

The header provides the public contract for a small Btrfs traversal helper. The type is intentionally simple: uniqueness comes from the rb-tree, traversal from the linked list, and synchronization from the caller.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/ulist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/uuid-tree.c -->
# File Research: sources/os/linux/linux/fs/btrfs/uuid-tree.c

## Purpose

`uuid-tree.c` implements Btrfs' UUID tree support. The UUID tree indexes subvolume UUIDs and received UUIDs so the filesystem can find subvolumes by UUID and keep that index consistent with the root tree.

Each UUID key maps one UUID and UUID-key type to a variable-length array of subvolume/root IDs stored as little-endian `u64` values.

## Key Format

`btrfs_uuid_to_key()` converts a 16-byte UUID to a Btrfs key:

- key type is the UUID item type, such as `BTRFS_UUID_KEY_SUBVOL` or `BTRFS_UUID_KEY_RECEIVED_SUBVOL`.
- objectid is the first little-endian 64 bits of the UUID.
- offset is the second little-endian 64 bits of the UUID.

The item payload is an array of subvolume IDs associated with that UUID.

## Lookup, Add, Remove

`btrfs_uuid_tree_lookup()` searches the UUID root for a UUID/type key and scans the item payload for a specific subvolume ID. It returns 0 when found, `-ENOENT` when absent, and negative errors for failures. It validates that item size is aligned to `sizeof(u64)` and warns on illegal sizes.

`btrfs_uuid_tree_add()` first calls lookup to avoid duplicate subvolume IDs. If the item does not exist, it inserts a new one with one `u64`. If the key exists, it extends the item and appends the new subvolume ID.

`btrfs_uuid_tree_remove()` searches the item under transaction context, scans for the matching subvolume ID, deletes the whole item if it was the only entry, or compacts the remaining payload with `memmove_extent_buffer()` and truncates the item.

`btrfs_uuid_tree_check_overflow()` checks whether appending one more `u64` to a UUID item would exceed the leaf data size. It returns `-EOVERFLOW` when the item cannot be extended.

## Consistency Checking

`btrfs_check_uuid_tree_entry()` validates a UUID-tree entry against the referenced subvolume root. For supported UUID item types, it loads the subvolume root by ID:

- missing root returns a positive value so the caller removes the stale UUID-tree entry.
- a UUID mismatch also returns a positive value.
- other lookup errors propagate as negative errors.

`btrfs_uuid_iter_rem()` wraps removal of one stale entry in a one-item transaction.

`btrfs_uuid_tree_iterate()` scans the UUID tree forward and validates every subvolume and received-subvolume UUID entry. Stale entries are removed, then the scan restarts from the current key. The function checks for filesystem shutdown and returns `-EINTR` if closing.

## UUID Tree Creation and Rescan

`btrfs_create_uuid_tree()` creates the UUID tree root in a transaction, commits it, then starts the `btrfs-uuid` kernel thread to populate the new tree from existing root items. It protects the rescan with `uuid_tree_rescan_sem`.

`btrfs_uuid_scan_kthread()` walks the tree root for `BTRFS_ROOT_ITEM_KEY` items representing live subvolumes. For each root item with a non-empty normal UUID or received UUID, it starts or reuses a transaction with two reserved items and adds corresponding UUID tree entries. It skips roots with zero refs and invalid objectid ranges.

On successful completion, if the filesystem is not closing, the thread sets `BTRFS_FS_UPDATE_UUID_TREE_GEN`. It always releases the rescan semaphore before returning.

## Error Handling

The file consistently treats malformed UUID item sizes as warnings and generally returns `-ENOENT` for those specific bad entries. Transaction start, path allocation, search, insert, extend, delete, and commit failures propagate as negative errors. Creation aborts the transaction if creating the tree root fails.

## Filesystem Role

The UUID tree is an auxiliary metadata index. It does not own subvolume lifetime; instead, it mirrors UUID fields from root items and provides repair/rescan paths to remove stale mappings and build the index when needed.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/uuid-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/uuid-tree.h -->
# File Research: sources/os/linux/linux/fs/btrfs/uuid-tree.h

## Purpose

`uuid-tree.h` declares the public interface for Btrfs UUID tree management.

## Public API

The header exposes mutation helpers:

- `btrfs_uuid_tree_add()`
- `btrfs_uuid_tree_remove()`

It exposes validation and maintenance helpers:

- `btrfs_uuid_tree_check_overflow()`
- `btrfs_uuid_tree_iterate()`

It exposes creation and asynchronous population hooks:

- `btrfs_create_uuid_tree()`
- `btrfs_uuid_scan_kthread()`

## Filesystem Role

The header is used by Btrfs code that updates root UUID metadata, checks whether UUID-tree items can grow, creates the UUID tree, or kicks/scans the UUID index for consistency.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/uuid-tree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/verity.c -->
# File Research: sources/os/linux/linux/fs/btrfs/verity.c

## Purpose

`verity.c` implements Btrfs' `struct fsverity_operations` backend. It stores fs-verity descriptors and Merkle tree bytes as dedicated Btrfs metadata items in the filesystem tree, while caching Merkle tree pages in the inode mapping at synthetic offsets past EOF.

The file deliberately differs from ext4/f2fs style past-EOF on-disk storage. Btrfs keeps verity data in btree items to avoid changing file size semantics and to fit its existing metadata model.

## On-Disk Layout

Descriptor items use keys of the form:

`[ inode objectid, BTRFS_VERITY_DESC_ITEM_KEY, offset ]`

At offset 0, Btrfs stores `struct btrfs_verity_descriptor_item`, including the descriptor size. Starting at offset 1, it stores the opaque fs-verity descriptor bytes.

Merkle tree items use keys of the form:

`[ inode objectid, BTRFS_VERITY_MERKLE_ITEM_KEY, offset ]`

Their offsets start at 0 and correspond to Merkle tree byte offsets. The payload is opaque to Btrfs.

## Merkle Cache Position

`merkle_file_pos()` computes the synthetic file offset used for caching Merkle tree pages in the inode page cache. It rounds `i_size` up to 64 KiB via `MERKLE_START_ALIGN` and rejects results beyond `s_maxbytes` with `-EFBIG`.

This keeps cached Merkle pages safely beyond the last possible data page, including systems with 64 KiB pages.

## Item Cleanup

`drop_verity_items()` deletes all items for one inode and one verity key type. It repeatedly searches backwards from offset `U64_MAX`, deletes one matching item per transaction, releases the path, and continues until no matching key remains.

`btrfs_drop_verity_items()` removes both descriptor and Merkle item types. It is used before enabling verity and during rollback.

## Item I/O Helpers

`write_key_bytes()` writes an arbitrary byte range into a sequence of Btrfs items. It inserts items of up to 2048 bytes, with keys advancing by the copied byte count. Each item is inserted and written in its own transaction.

`read_key_bytes()` reads a sequence of items starting at a requested offset. It supports three modes:

- count-only mode when `dest` is NULL.
- copying into a caller buffer.
- copying into a folio when reading Merkle tree pages.

It accepts starting in the middle of the first item, then requires subsequent items to be sequential. Short reads are allowed when items end before the requested length.

## Orphan and Rollback Handling

Enabling fs-verity can write a large Merkle tree, so Btrfs protects the whole operation with an orphan item.

`del_orphan()` removes the verity orphan item but ignores inodes with zero links and treats `-ENOENT` as success. This avoids conflicting with other orphan users such as unlink or `O_TMPFILE`.

`rollback_verity()` is called when enablement fails. It truncates cached Merkle pages past EOF, clears `BTRFS_INODE_VERITY_IN_PROGRESS`, drops verity items, clears the inode's verity ro flag, updates the inode, and deletes the orphan. If rollback cleanup itself fails, it reports filesystem errors because partial verity state is not recoverable.

## Enabling Verity

`btrfs_begin_enable_verity()` is the fsverity begin hook. It requires the inode lock, rejects encrypted files, rejects concurrent verity enablement with `-EBUSY`, drops stale verity items, adds an orphan item, and sets the in-progress runtime flag.

`finish_verity()` writes the descriptor-size item, writes the descriptor bytes, starts a transaction, sets `BTRFS_INODE_RO_VERITY`, syncs VFS inode flags, updates the inode item, deletes the orphan, clears the in-progress bit, and sets the filesystem read-only compatible `VERITY` bit.

`btrfs_end_enable_verity()` is the fsverity end hook. If fsverity passes a NULL descriptor, it rolls back. Otherwise it calls `finish_verity()` and rolls back on failure.

## Descriptor Reads

`btrfs_get_verity_descriptor()` reads the descriptor header item at offset 0, validates reserved fields and size, supports a size-query call when `buf_size == 0`, rejects undersized buffers with `-ERANGE`, then reads the descriptor blob from offset 1. It returns the true descriptor size or a negative error.

## Merkle Tree Reads and Writes

`btrfs_read_merkle_tree_page()` maps a Merkle page index to the synthetic post-EOF page-cache index. It first checks for an existing up-to-date folio. If absent, it allocates and adds a folio, reads up to one page of Merkle bytes from `BTRFS_VERITY_MERKLE_ITEM_KEY` items, zero-fills any short read, marks the folio uptodate, and returns the page.

`btrfs_write_merkle_tree_block()` validates that the synthetic Merkle cache position plus the requested Merkle range fits within `s_maxbytes`, then writes the block bytes into Merkle items through `write_key_bytes()`.

## fsverity Operations Table

`btrfs_verityops` wires Btrfs into the VFS fs-verity layer:

- `begin_enable_verity`
- `end_enable_verity`
- `get_verity_descriptor`
- `read_merkle_tree_page`
- `write_merkle_tree_block`

## Filesystem Role

This file is the bridge between generic fs-verity and Btrfs metadata. It handles Btrfs-specific storage, transactions, orphan protection, page-cache placement, rollback, and inode flag persistence while leaving descriptor and Merkle payload interpretation to the generic fs-verity layer.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/verity.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/verity.h -->
# File Research: sources/os/linux/linux/fs/btrfs/verity.h

## Purpose

`verity.h` declares the Btrfs fs-verity interface and provides stubs when `CONFIG_FS_VERITY` is disabled.

## CONFIG_FS_VERITY Enabled

When fs-verity support is compiled in, the header includes `<linux/fsverity.h>` and exposes:

- `btrfs_verityops`, the `struct fsverity_operations` instance implemented in `verity.c`.
- `btrfs_drop_verity_items()`, used to remove descriptor and Merkle metadata.
- `btrfs_get_verity_descriptor()`, used to retrieve the fs-verity descriptor for an inode.

## CONFIG_FS_VERITY Disabled

When fs-verity is not compiled in:

- `btrfs_drop_verity_items()` is an inline no-op returning 0.
- `btrfs_get_verity_descriptor()` returns `-EPERM`.

This lets common Btrfs code call cleanup and descriptor helpers without open-coding configuration checks everywhere.

## Filesystem Role

The header is the compile-time boundary for Btrfs fs-verity support. It keeps optional verity code isolated while preserving stable call sites for the rest of the filesystem.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/verity.h -->