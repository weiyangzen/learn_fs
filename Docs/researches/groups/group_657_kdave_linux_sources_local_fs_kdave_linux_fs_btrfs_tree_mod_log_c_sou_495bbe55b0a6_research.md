# Group Research: group_657_kdave_linux_sources_local_fs_kdave_linux_fs_btrfs_tree_mod_log_c_sou_495bbe55b0a6

Scope checked against `Docs/research_subset_a.md`: `sources/local-fs/kdave-linux` is in subset A. All eight listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tree-mod-log.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/tree-mod-log.c

## Purpose

`tree-mod-log.c` implements Btrfs' tree modification log: a sequence-numbered, reversible log of B-tree node/root changes used to reconstruct older views of metadata trees while concurrent modification is happening.

Its main consumer is backreference and extent-walking logic that needs a consistent historical view of extent and filesystem trees. Rather than freezing all tree updates, callers register a tree-mod-log sequence blocker, mutations record reversible operations, and later readers rewind extent buffers or root nodes to the state visible at that sequence.

## Main Data Structures

`struct tree_mod_elem` is the private log record stored in `fs_info->tree_mod_log`, an rb-tree ordered by affected logical address and sequence number. It records:

- `logical`: affected tree block logical address, or the new root address for root replacement entries.
- `seq`: global tree modification sequence.
- `op`: one of `BTRFS_MOD_LOG_*`.
- `slot` and `generation`: affected node slot metadata.
- `slot_change`: saved key/blockptr for add/remove/replace reversal.
- `move`: source/destination/count metadata for key moves.
- `old_root`: old logical address and level for root replacement.

`struct tree_mod_root` stores old root identity for `BTRFS_MOD_LOG_ROOT_REPLACE`.

The global state is carried in `struct btrfs_fs_info`: `tree_mod_seq`, `tree_mod_seq_list`, `tree_mod_log`, `tree_mod_log_lock`, and the `BTRFS_FS_TREE_MOD_LOG_USERS` flag.

## Sequence Lifecycle

`btrfs_get_tree_mod_seq()` registers a `struct btrfs_seq_list` blocker if it does not already have a sequence, appends it to `fs_info->tree_mod_seq_list`, sets `BTRFS_FS_TREE_MOD_LOG_USERS`, and returns the blocker sequence.

`btrfs_put_tree_mod_seq()` removes a blocker and prunes log records older than the lowest remaining blocker sequence. If the removed blocker was not the oldest active blocker, pruning is skipped because earlier readers may still need older log entries. When the blocker list becomes empty, `BTRFS_FS_TREE_MOD_LOG_USERS` is cleared.

This means tree-mod-log retention is driven by the oldest active reader, not by transaction boundaries.

## Logging Gate

`tree_mod_need_log()` cheaply checks whether logging might be needed. It rejects logging when there are no users or when the extent buffer belongs to a tree that does not need historical backref consistency.

`tree_mod_dont_log()` is the locking version. It takes `tree_mod_log_lock` for writing only if users exist and the affected buffer should be logged. Callers allocate records before this point, then re-check under the lock to avoid racing with the last blocker going away. If logging is no longer needed, allocation failures are ignored.

`skip_eb_logging()` excludes leaves and non-target trees. The file logs internal nodes from the extent tree and filesystem trees, because those are the trees needed for consistent extent/backref iteration.

## Log Insertion Paths

`tree_mod_log_insert()` assigns a fresh sequence and inserts the record into the rb-tree. For equal logical addresses, larger sequence numbers are placed toward the left side, matching the search logic used for newest/oldest lookup.

Public insertion helpers cover B-tree edit patterns:

- `btrfs_tree_mod_log_insert_key()` logs single key add/remove/replace-style operations.
- `btrfs_tree_mod_log_insert_move()` logs a contiguous key move and also logs overwritten destination slots when moving toward lower slots.
- `btrfs_tree_mod_log_eb_copy()` logs key copies between nodes, destination-side moves, source removals, and source-side compaction moves.
- `btrfs_tree_mod_log_free_eb()` logs all keys in a node as removed while freeing.
- `btrfs_tree_mod_log_insert_root()` logs root replacement and optionally logs removal of old-root keys.

Most insertion helpers allocate all needed records first, acquire the tree-mod-log write lock, insert records in a sequence that can later be rewound, and unwind any already-inserted records on failure.

## Search And Rewind

`tree_mod_log_search()` returns the newest log entry for a logical address at or newer than a minimum sequence. `tree_mod_log_search_oldest()` returns the oldest such entry. Both use `__tree_mod_log_search()` under `tree_mod_log_lock`.

`tree_mod_log_oldest_root()` follows `BTRFS_MOD_LOG_ROOT_REPLACE` links backward from the current root to find the oldest predecessor relevant to a sequence. Root replacement records are keyed by the new root address, so this helper walks from current root to old roots until it finds the earliest required root state.

`tree_mod_log_rewind()` applies inverse operations to an extent buffer while traversing log records in sequence order for the same logical address:

- Removed keys are restored with saved key/blockptr/generation.
- Replaced keys are restored.
- Added keys reduce item count because the inverse is removal.
- Move operations are reversed with `memmove_extent_buffer()`.
- Root replacement is ignored for non-root node rewind; root replacement is handled before choosing the buffer.

It tracks `max_slot` separately from item count to sanity-check move ranges during partial rewind states.

## Public Historical View APIs

`btrfs_tree_mod_log_rewind()` rewinds a locked extent buffer to a given sequence. If the buffer needs rewind, it clones the buffer or creates a dummy buffer for a node that was freed, releases the original, locks the replacement, replays inverse operations, and returns the rewound buffer locked.

`btrfs_get_old_root()` returns a locked extent buffer representing a root node as of `time_seq`. It may return the current root node, clone the current root, read and clone an old root from disk, or create a dummy extent buffer for a freed old root. It includes a race check after reading an old root because new tree-mod-log operations can be inserted between lookup and cloning.

`btrfs_old_root_level()` reports the historical level of a root at a sequence by checking the oldest root replacement record.

`btrfs_tree_mod_log_lowest_seq()` returns the oldest active blocker sequence or `0` if no users exist.

## Dependencies

This file depends on Btrfs core metadata helpers from `accessors.h`, tree buffer allocation/cloning/locking from `disk-io.h`, filesystem state from `fs.h`, diagnostics from `messages.h`, and structural checks from `tree-checker.h`.

It is tightly coupled to Btrfs internal node layout through helpers such as `btrfs_node_key()`, `btrfs_set_node_key()`, `btrfs_node_blockptr()`, `btrfs_set_node_blockptr()`, `btrfs_header_level()`, and `btrfs_header_nritems()`.

## Invariants And Risks

The core invariant is that every logged mutation must contain enough old state to reverse it and must be inserted in an order that matches rewind expectations. Bugs here can corrupt reconstructed metadata views, causing incorrect backref walks, false leak reports, missed references, or kernel assertions.

High-risk areas include move logging, `eb_copy()` multi-record rollback, dummy buffer creation for freed nodes, root replacement chains, and races between log search and reading old roots. The code relies on careful lock ordering: records are inserted under `tree_mod_log_lock`, extent buffers are cloned/read-locked separately, and readers replay records under the tree-mod-log read lock.

<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tree-mod-log.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tree-mod-log.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/tree-mod-log.h

## Purpose

`tree-mod-log.h` declares the public Btrfs tree modification log interface. It exposes the sequence-blocker type, operation enum, and APIs used by B-tree update code and historical metadata readers.

## Main Interfaces

`struct btrfs_seq_list` represents one tree-mod-log user. Callers initialize it with `BTRFS_SEQ_LIST_INIT`, obtain a sequence with `btrfs_get_tree_mod_seq()`, and release it with `btrfs_put_tree_mod_seq()`.

`BTRFS_SEQ_LAST` is the sentinel maximum sequence value used for pruning and sequence comparisons.

`enum btrfs_mod_log_op` defines reversible mutation kinds:

- `BTRFS_MOD_LOG_KEY_REPLACE`
- `BTRFS_MOD_LOG_KEY_ADD`
- `BTRFS_MOD_LOG_KEY_REMOVE`
- `BTRFS_MOD_LOG_KEY_REMOVE_WHILE_FREEING`
- `BTRFS_MOD_LOG_KEY_REMOVE_WHILE_MOVING`
- `BTRFS_MOD_LOG_MOVE_KEYS`
- `BTRFS_MOD_LOG_ROOT_REPLACE`

The file declares logging functions for key changes, node frees, root replacement, extent-buffer copy, key moves, root rewind, old-root lookup, old-root level lookup, and lowest active sequence lookup.

## Integration Role

This header is the contract between Btrfs tree mutation code and backref/history readers. Writers call insertion helpers around structural changes; readers hold a sequence blocker and later ask for old roots or rewound buffers.

## Dependencies And Constraints

The header forward-declares Btrfs types instead of including large internal headers, keeping compile dependencies low. It includes `<linux/list.h>` because `struct btrfs_seq_list` embeds `struct list_head`.

Correctness depends on callers using the enum values according to the actual mutation being performed. The implementation stores different fields for different operations, so mismatched operation types would make rewind unsafe.

<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tree-mod-log.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/ulist.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/ulist.c

## Purpose

`ulist.c` implements a small Btrfs utility container for unique `u64` values with an optional `u64` auxiliary payload. It supports insertion, deletion, and iteration while guaranteeing that a value is present at most once.

The intended use is non-recursive traversal of graphs or trees whose nodes are addressable by `u64`, especially metadata tree/block graph enumeration where recursion would be unsafe for kernel stack usage.

## Data Structure

A `struct ulist` combines:

- A linked list, `nodes`, used for iteration and append order.
- An rb-tree, `root`, used for efficient uniqueness lookup by `val`.
- A node count, `nnodes`.
- A single preallocated node slot, `prealloc`, used by callers that want to prepare one allocation before a critical path.

Each `struct ulist_node` stores `val`, `aux`, a list node, and an rb-tree node.

## Lifecycle APIs

`ulist_init()` initializes an externally allocated ulist.

`ulist_release()` frees all nodes and the preallocated spare node, then resets the rb-tree and list head. It does not free the `struct ulist` itself.

`ulist_reinit()` releases and reinitializes a ulist for reuse.

`ulist_alloc()` allocates and initializes a ulist.

`ulist_free()` releases all internal allocations and frees the ulist object. It is NULL-safe.

`ulist_prealloc()` allocates a spare `ulist_node` if one is not already present.

## Mutation APIs

`ulist_add()` inserts a value with auxiliary data and returns:

- `1` if inserted.
- `0` if the value already existed.
- `-ENOMEM` on allocation failure.

`ulist_add_merge()` is the implementation behind `ulist_add()`. If the value already exists and `old_aux` is supplied, it returns the existing auxiliary value through `old_aux` and ignores the new auxiliary value.

`ulist_del()` removes a node only when both `val` and `aux` match. It returns `0` for successful deletion and positive `1` when not found or when the auxiliary value does not match.

Internally, uniqueness is enforced by `ulist_rbtree_search()` and `ulist_rbtree_insert()` using `rb_find()` and `rb_find_add()`.

## Iteration

`ulist_next()` iterates through the linked-list order using a caller-owned `struct ulist_iterator`, initialized with `ULIST_ITER_INIT()` from the header. It returns NULL at end.

The implementation explicitly allows `ulist_add()` during enumeration. Newly appended items are guaranteed to appear later in the same running enumeration because iteration follows the list and insertions append to the tail.

No ordering guarantee is made beyond this traversal property; callers must not rely on numerical order.

## Locking And Dependencies

The file does not implement locking. Callers must provide external synchronization. Comments require write locking for mutation and read locking for iteration when an rwlock is used.

The implementation uses Linux slab allocation and rb-tree helpers, plus Btrfs `ASSERT`/`BUG_ON` diagnostics from `messages.h`.

## Invariants And Risks

The rb-tree and linked list must remain consistent. Every inserted node is in both structures, and every deletion removes it from both. `nnodes` is incremented after insertion and decremented after erase.

The preallocation path transfers ownership of `ulist->prealloc` into the tree and clears the spare pointer. If callers assume more than one reserved insertion, they can still hit `-ENOMEM`.

The container is intentionally narrow: it does not update auxiliary data for duplicates, does not sort iteration, and is unsafe without caller-provided locking.

<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/ulist.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/ulist.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/ulist.h

## Purpose

`ulist.h` declares the Btrfs unique-`u64` list container used for iterative graph/tree traversal without recursion. It defines the public structs and helper functions implemented in `ulist.c`.

## Public Types

`struct ulist_iterator` stores the current list position for `ulist_next()`.

`struct ulist_node` stores:

- `val`: the unique `u64` key.
- `aux`: auxiliary `u64` data associated with the first insertion.
- `list`: linked-list membership for iteration.
- `rb_node`: rb-tree membership for lookup.

`struct ulist` stores the node count, linked list, rb-tree root, and one preallocated spare node.

## Public APIs

The header declares lifecycle, mutation, deletion, and iteration functions:

- `ulist_init()`
- `ulist_release()`
- `ulist_reinit()`
- `ulist_alloc()`
- `ulist_prealloc()`
- `ulist_free()`
- `ulist_add()`
- `ulist_add_merge()`
- `ulist_del()`
- `ulist_next()`

`ULIST_ITER_INIT()` initializes an iterator by clearing its current list pointer.

## Pointer Auxiliary Helper

`ulist_add_merge_ptr()` wraps `ulist_add_merge()` for pointer auxiliary data. On 64-bit builds it casts the pointer directly through `u64`. On 32-bit builds it uses a temporary `u64` to preserve the helper signature while converting through `uintptr_t`.

## Integration Notes

This header exposes the internal struct layout, so callers can inspect `nnodes` or node fields directly after iteration. It keeps the implementation simple but means layout changes are source-visible.

The key behavioral constraint is external locking: the container itself provides no synchronization.

<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/ulist.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/uuid-tree.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/uuid-tree.c

## Purpose

`uuid-tree.c` manages Btrfs' UUID tree, a filesystem tree that maps subvolume UUIDs and received UUIDs to subvolume/root IDs. It supports lookup, insertion, removal, overflow checking, consistency cleanup, initial tree creation, and asynchronous scanning to populate the UUID tree.

This tree accelerates subvolume discovery by UUID and tracks both normal subvolume UUIDs and received-subvolume UUIDs used by send/receive workflows.

## Key Format

`btrfs_uuid_to_key()` converts a 16-byte UUID into a Btrfs key:

- `objectid`: little-endian first 8 bytes of UUID.
- `offset`: little-endian second 8 bytes of UUID.
- `type`: UUID item type, such as `BTRFS_UUID_KEY_SUBVOL` or `BTRFS_UUID_KEY_RECEIVED_SUBVOL`.

Each UUID tree item payload is a packed list of little-endian `u64` subvolume IDs. Multiple subvolumes can share the same UUID item key, so the payload can contain more than one subid.

## Lookup, Add, Remove

`btrfs_uuid_tree_lookup()` searches the UUID root for a key and scans the item payload for a given subid. It returns `0` when found, `-ENOENT` when not found, and negative errors for failures. It validates that the item size is aligned to `sizeof(u64)`.

`btrfs_uuid_tree_add()` first calls lookup to avoid duplicates. It inserts a new item when the UUID key is absent, or extends an existing item and appends the new subid when the key exists.

`btrfs_uuid_tree_remove()` searches with a transaction, finds the matching subid, and either deletes the whole item when it contains only one subid or compacts the payload with `memmove_extent_buffer()` and truncates the item.

## Capacity Check

`btrfs_uuid_tree_check_overflow()` determines whether another `u64` subid can be appended to an existing UUID item without exceeding leaf item capacity. If no item exists, insertion is allowed. If adding one `u64` plus item metadata would exceed `BTRFS_LEAF_DATA_SIZE()`, it returns `-EOVERFLOW`.

This is a preventive check for UUID collisions or repeated entries that would make a single item too large.

## Consistency Iteration

`btrfs_uuid_tree_iterate()` walks the UUID tree and validates entries for subvolume and received-subvolume UUID item types.

For each subid in a UUID item, it calls `btrfs_check_uuid_tree_entry()`:

- If the subvolume root does not exist, the entry is stale.
- For `BTRFS_UUID_KEY_SUBVOL`, the UUID must match `root_item.uuid`.
- For `BTRFS_UUID_KEY_RECEIVED_SUBVOL`, the UUID must match `root_item.received_uuid`.

Stale entries are removed by `btrfs_uuid_iter_rem()` in a small transaction, then the walk restarts from the adjusted key. The iterator also exits with `-EINTR` when the filesystem is closing.

## Initial Scan Thread

`btrfs_uuid_scan_kthread()` scans `fs_info->tree_root` for `BTRFS_ROOT_ITEM_KEY` items. For each live subvolume root item with a non-empty UUID or received UUID, it starts a transaction on `fs_info->uuid_root` and adds the appropriate UUID tree entries.

Important filtering rules:

- It skips non-root-item keys.
- It skips objectids outside the valid free/subvolume range, except `BTRFS_FS_TREE_OBJECTID`.
- It skips root items too small to contain `struct btrfs_root_item`.
- It skips roots with zero root refs.
- It checks `btrfs_fs_closing()` and yields with `cond_resched()`.

On successful completion that was not due to closing, it sets `BTRFS_FS_UPDATE_UUID_TREE_GEN`. It always releases `uuid_tree_rescan_sem` before exiting.

## UUID Tree Creation

`btrfs_create_uuid_tree()` starts a transaction on the tree root, creates `BTRFS_UUID_TREE_OBJECTID`, stores it in `fs_info->uuid_root`, commits the transaction, then launches `btrfs_uuid_scan_kthread()` to populate the new tree.

It holds `uuid_tree_rescan_sem` across kthread startup. If thread creation fails, it releases the semaphore and returns the error.

## Dependencies

The file depends on Btrfs transaction, root-tree, path/search, item manipulation, and extent-buffer APIs from `ctree.h`, `transaction.h`, `disk-io.h`, `fs.h`, `accessors.h`, and `ioctl.h`. It uses Linux `kthread`, UUID helpers, and unaligned little-endian accessors.

## Invariants And Risks

UUID item payloads must be `u64` aligned; malformed item sizes are warned and treated as not found/skipped. Add/remove operations assume UUID root existence and warn on unexpected insertion failures.

The consistency walk is intentionally restart-heavy after removals, prioritizing correctness over scan efficiency because stale UUID entries should be exceptional.

Risk areas are transaction sizing, path release/restart after item mutation, UUID item overflow, and shutdown interaction in the scan thread.

<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/uuid-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/uuid-tree.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/uuid-tree.h

## Purpose

`uuid-tree.h` declares Btrfs UUID tree operations for mapping subvolume UUIDs and received UUIDs to subvolume IDs.

## Public APIs

The header exposes:

- `btrfs_uuid_tree_add()` to add a UUID/type/subid mapping inside a transaction.
- `btrfs_uuid_tree_remove()` to remove a mapping inside a transaction.
- `btrfs_uuid_tree_check_overflow()` to preflight whether another subid can fit under a UUID key.
- `btrfs_uuid_tree_iterate()` to validate and clean UUID tree entries.
- `btrfs_create_uuid_tree()` to create and populate the UUID tree.
- `btrfs_uuid_scan_kthread()` as the worker entry point for initial population.

## Integration Notes

The header forward-declares `struct btrfs_trans_handle` and `struct btrfs_fs_info`, minimizing dependencies. Callers must pass valid UUID item types and manage transactions where required by the add/remove APIs.

<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/uuid-tree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/verity.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/verity.c

## Purpose

`verity.c` implements Btrfs support for Linux fs-verity through `struct fsverity_operations`. It stores fs-verity descriptors and Merkle tree data as dedicated Btrfs items in the file's filesystem tree, rather than storing them as file data past EOF.

The file handles verity enablement, rollback, descriptor read/write, Merkle tree item read/write, page-cache integration for Merkle pages, and cleanup of incomplete verity state.

## On-Disk Item Model

Btrfs uses two item key types under the inode objectid:

- Descriptor items: `[ inode objectid, BTRFS_VERITY_DESC_ITEM_KEY, offset ]`
- Merkle tree items: `[ inode objectid, BTRFS_VERITY_MERKLE_ITEM_KEY, offset ]`

Descriptor offset `0` stores `struct btrfs_verity_descriptor_item`, which records the descriptor size and reserved metadata. Descriptor bytes start at offset `1`.

Merkle tree items start at offset `0` and store opaque Merkle tree bytes. Btrfs does not interpret the Merkle tree data.

## Merkle Cache Position

`merkle_file_pos()` computes a synthetic file offset for caching Merkle tree pages in the inode page cache. It rounds `i_size` up to `MERKLE_START_ALIGN` (`65536`) so Merkle pages sit past EOF even on systems with 64K pages. It checks against `s_maxbytes` and returns `-EFBIG` on overflow.

This offset is for cache indexing only; Merkle data is stored in B-tree items.

## Item Drop And Byte IO Helpers

`drop_verity_items()` walks backward through all items of a key type for the inode and deletes them one by one in small transactions. It is used before enabling verity and during rollback.

`btrfs_drop_verity_items()` drops both descriptor and Merkle item types.

`write_key_bytes()` writes arbitrary bytes into one or more Btrfs items, inserting up to 2K bytes per item. Each item key uses the inode objectid, requested key type, and current byte offset. It starts and ends a transaction per inserted item.

`read_key_bytes()` reads sequential bytes from items of a given key type and offset. With `dest == NULL`, it counts bytes without copying. With `dest_folio`, it copies into a mapped folio and enables forward readahead on the path. It supports reads beginning in the middle of an item and stops on holes, non-sequential offsets, key mismatch, or tree end.

## Orphan Handling And Rollback

Verity enablement can write many Merkle items and may fail partway through. Btrfs guards the operation with an orphan item and a runtime `BTRFS_INODE_VERITY_IN_PROGRESS` bit.

`del_orphan()` deletes the verity orphan item but ignores zero-link inodes and treats `-ENOENT` as success.

`rollback_verity()` is called when enablement fails. It requires the inode lock, truncates cached pages past `i_size`, clears the in-progress bit, drops verity items, clears `BTRFS_INODE_RO_VERITY`, syncs inode flags, updates the inode, and deletes the orphan item. If rollback itself fails, it reports a filesystem error because the partial verity state may be unrecoverable.

## Enable Verity Flow

`btrfs_begin_enable_verity()` is the fs-verity begin hook. It rejects encrypted inodes, rejects concurrent enablement with `-EBUSY`, drops any stale verity items, adds an orphan item in a transaction, and sets `BTRFS_INODE_VERITY_IN_PROGRESS`.

`btrfs_end_enable_verity()` is the fs-verity end hook. If `desc == NULL`, fs-verity is reporting an earlier failure, so Btrfs rolls back. Otherwise it calls `finish_verity()` and rolls back if finalization fails.

`finish_verity()` writes the descriptor header item, writes the descriptor blob, starts a transaction, sets `BTRFS_INODE_RO_VERITY`, syncs inode flags, updates the inode, deletes the orphan, clears the in-progress bit, and sets the filesystem read-only compatibility bit `VERITY`.

## Descriptor Reading

`btrfs_get_verity_descriptor()` reads the descriptor header at descriptor key offset `0`, validates reserved fields, obtains the true descriptor size, and supports fs-verity's two-pass API:

- `buf_size == 0`: return descriptor size.
- `buf_size < true_size`: return `-ERANGE`.
- Otherwise read descriptor bytes from offset `1`.

It returns `-EUCLEAN` on invalid descriptor header state, `-EIO` on short descriptor reads, or the descriptor size on success.

## Merkle Tree Page Read

`btrfs_read_merkle_tree_page()` reads and caches one Merkle tree page for fs-verity. It translates the fs-verity page index into the synthetic page-cache index past EOF, then:

1. Looks for an existing folio in the inode mapping.
2. If present and uptodate, returns the requested page.
3. If present but not uptodate after locking, returns `-EIO`.
4. Allocates and adds a new folio with GFP constraints avoiding filesystem recursion.
5. Reads up to one page of Merkle bytes from `BTRFS_VERITY_MERKLE_ITEM_KEY` items.
6. Zero-fills any short read, marks the folio uptodate, unlocks it, and returns the page.

It checks both synthetic file position and page offset against `s_maxbytes`.

## Merkle Tree Write

`btrfs_write_merkle_tree_block()` is the fs-verity write hook for a Merkle tree block. It validates that the synthetic cache position plus Merkle offset and size do not exceed `s_maxbytes`, then writes the block into `BTRFS_VERITY_MERKLE_ITEM_KEY` items at the given Merkle byte offset.

## Exported Operations

`btrfs_verityops` binds Btrfs to the generic fs-verity layer:

- `begin_enable_verity = btrfs_begin_enable_verity`
- `end_enable_verity = btrfs_end_enable_verity`
- `get_verity_descriptor = btrfs_get_verity_descriptor`
- `read_merkle_tree_page = btrfs_read_merkle_tree_page`
- `write_merkle_tree_block = btrfs_write_merkle_tree_block`

## Dependencies

The file depends on Linux fs-verity, folio/page-cache, xattr/security includes, and Btrfs transaction/orphan/inode/accessor APIs. It uses `btrfs_start_transaction()`, `btrfs_insert_empty_item()`, `btrfs_del_items()`, `btrfs_truncate_item()`, `btrfs_update_inode()`, `btrfs_orphan_add()`, and `btrfs_del_orphan_item()`.

## Invariants And Risks

The central invariant is that a verity inode must not be left with partial descriptor/Merkle state unless it is guarded by the in-progress bit and orphan cleanup path. Successful finalization must atomically make the inode verity-read-only from the filesystem perspective and remove the orphan.

Risk areas include rollback failure, short or non-sequential item reads, synthetic page-cache index overflow, stale cached Merkle pages after failed enablement, and future encryption support because descriptor/Merkle items are metadata items rather than file data.

<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/verity.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/verity.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/verity.h

## Purpose

`verity.h` declares Btrfs fs-verity integration points and provides configuration-dependent stubs when fs-verity is disabled.

## CONFIG_FS_VERITY Enabled

When `CONFIG_FS_VERITY` is enabled, the header includes `<linux/fsverity.h>` and declares:

- `extern const struct fsverity_operations btrfs_verityops`
- `btrfs_drop_verity_items()`
- `btrfs_get_verity_descriptor()`

These are implemented in `verity.c` and used by Btrfs inode and cleanup paths.

## CONFIG_FS_VERITY Disabled

When fs-verity support is disabled, the header provides inline stubs:

- `btrfs_drop_verity_items()` returns `0`, making cleanup callers harmless.
- `btrfs_get_verity_descriptor()` returns `-EPERM`, preventing descriptor access without fs-verity support.

## Integration Notes

The header forward-declares `struct inode` and `struct btrfs_inode`, keeping dependencies minimal. It is the compile-time switch point that lets the rest of Btrfs call verity cleanup/access helpers without open-coding `#ifdef CONFIG_FS_VERITY` at every call site.

<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/verity.h -->