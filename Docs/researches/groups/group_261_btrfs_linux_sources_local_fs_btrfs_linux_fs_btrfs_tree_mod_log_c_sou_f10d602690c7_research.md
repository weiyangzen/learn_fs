# Group Research: group_261_btrfs_linux_sources_local_fs_btrfs_linux_fs_btrfs_tree_mod_log_c_sou_f10d602690c7

Scope: `Docs/research_subset_a.md`

This group covers Btrfs kernel source files for tree modification history, unique u64 worklists, UUID indexing, and fs-verity metadata storage. The source tree `sources/local-fs/btrfs-linux` is included in subset A.

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tree-mod-log.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tree-mod-log.c

Implements the Btrfs tree modification log, a sequence-numbered reverse-operation log used to reconstruct older views of internal tree nodes and roots while backref/extents code is walking metadata concurrently with tree updates.

Key entry points:
- `btrfs_get_tree_mod_seq()` registers a tree-mod-log user, assigns a blocker sequence, and enables `BTRFS_FS_TREE_MOD_LOG_USERS`.
- `btrfs_put_tree_mod_seq()` unregisters a user and garbage-collects log entries older than the lowest remaining blocker sequence.
- `btrfs_tree_mod_log_insert_key()` records key pointer add/remove/replace operations for an internal extent buffer slot.
- `btrfs_tree_mod_log_insert_move()` records an internal node key-range move and any overwritten keys that must be restored when rewinding.
- `btrfs_tree_mod_log_insert_root()` records root replacement and, optionally, removal of the old root's internal-node keys while freeing.
- `btrfs_tree_mod_log_eb_copy()` logs key pointer transfers between internal nodes, including source/destination shifts around the copied range.
- `btrfs_tree_mod_log_free_eb()` logs removal of all key pointers from an internal extent buffer before it is freed.
- `btrfs_tree_mod_log_rewind()` returns a read-locked extent buffer representing the given block as of `time_seq`, cloning or creating a dummy buffer as needed.
- `btrfs_get_old_root()` and `btrfs_old_root_level()` reconstruct an old root node or root level for a historical sequence.
- `btrfs_tree_mod_log_lowest_seq()` exposes the oldest active blocker sequence.

Core mechanics:
- Each `tree_mod_elem` stores the affected block logical address, a monotonically increasing `seq`, an operation type, slot metadata, and operation-specific payload.
- The log is an rb-tree ordered by logical address and sequence. For a matching logical block, newer sequence entries sort before older ones because insertion descends left when `cur->seq < tm->seq`.
- Logging is skipped when there are no active users, for leaf buffers, and for trees outside the extent tree and filesystem trees. This keeps the log focused on metadata views needed by backref/extent walking.
- Allocation is intentionally done before taking the write lock when possible. After allocation, `tree_mod_dont_log()` rechecks whether logging is still needed while acquiring `tree_mod_log_lock`.
- Logged operations are forward mutations, but rewind applies the inverse: removed key pointers are restored, added key pointers are removed, replaced key pointers are reset to old values, and moves are copied back.
- Root replacement is special: it maps the new root logical address back to the old root logical address/level/generation so callers can follow a chain of root replacements.
- `tree_mod_log_oldest_root()` walks root replacement entries to identify the oldest predecessor relevant for a requested sequence.
- Rewinding a freed internal node may allocate a dummy extent buffer and repopulate it from logged key removals rather than reading the block from disk.

Important invariants:
- Callers must hold/log around structural internal-node mutations before the mutation becomes visible to concurrent old-view readers.
- Only internal nodes are rewound; leaves return unchanged because `skip_eb_logging()` omits level-0 buffers.
- `fs_info->tree_mod_log_lock` protects both the rb-tree and active sequence blocker list.
- Log records older than the minimum active blocker sequence are no longer needed and may be freed.
- `tree_mod_log_rewind()` tracks `max_slot` separately from `nritems` to detect invalid reverse memmoves during move replay.
- Root replacement replay must treat the logged logical address as the new root address while the payload points at the old root.

Filesystem relevance:
- This is a concurrency support layer for Btrfs metadata consistency. It lets long-running backref, extent, and root-history lookups observe a coherent older tree topology while balancing, COW, root promotion, and delayed-ref activity mutate live trees.

Notable risks:
- Missing a log insertion around an internal-node mutation can make old-root/backref reconstruction inconsistent.
- Ordering of multi-entry operations matters; partial insertion failures erase already inserted entries to avoid corrupt rewind state.
- Several paths use `BUG_ON()`, `ASSERT()`, and warnings for impossible or corrupt replay states, so malformed log state can escalate beyond a recoverable error.
- The code deliberately avoids logging many trees and all leaves; changing callers or use cases requires revalidating those skip rules.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tree-mod-log.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tree-mod-log.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tree-mod-log.h

Declares the public interface and operation vocabulary for Btrfs tree modification logging.

Key declarations:
- `struct btrfs_seq_list` represents one active tree-mod-log user and stores its sequence number in a list node.
- `BTRFS_SEQ_LIST_INIT()` initializes a sequence-list element with `seq = 0`.
- `BTRFS_SEQ_LAST` is the sentinel maximum sequence value.
- `enum btrfs_mod_log_op` defines logged mutation kinds: key replace/add/remove, key remove while freeing, key remove while moving, key range move, and root replacement.
- Public APIs cover sequence acquisition/release, key/root/move/free/copy logging, rewinding an extent buffer, fetching an old root, querying an old root level, and obtaining the lowest active sequence.

Core mechanics:
- The header exposes only opaque `extent_buffer`, `btrfs_fs_info`, `btrfs_path`, and `btrfs_root` references, keeping log internals private to `tree-mod-log.c`.
- Callers pass `enum btrfs_mod_log_op` for key-level mutations so the implementation can store the old key pointer data and later replay the inverse operation.

Important invariants:
- A caller-owned `btrfs_seq_list` must have `seq == 0` before first registration if it expects to be inserted as a new blocker.
- Callers must eventually pair `btrfs_get_tree_mod_seq()` with `btrfs_put_tree_mod_seq()` so stale log entries can be reclaimed.
- The exported insertion helpers are intended for internal tree node/root structure changes, not data leaves.

Filesystem relevance:
- This header is the contract used by Btrfs tree manipulation code to preserve historical metadata views for backref and extent logic.

Notable risks:
- Misusing operation types at call sites can make rewind apply the wrong inverse operation.
- Forgetting to release a sequence blocker can pin tree modification log memory.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tree-mod-log.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/ulist.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/ulist.c

Implements `ulist`, a small Btrfs helper collection for unique `u64` values with optional `u64` auxiliary data, rb-tree lookup, and list-based enumeration.

Key entry points:
- `ulist_init()` initializes an already allocated list object.
- `ulist_release()` frees all list nodes and the optional preallocated node but leaves the base `struct ulist` storage owned by the caller.
- `ulist_reinit()` releases current contents and resets the object for reuse.
- `ulist_alloc()` / `ulist_free()` allocate and free dynamic `struct ulist` instances.
- `ulist_prealloc()` reserves one zeroed node for a later insertion that may need to avoid allocation failure.
- `ulist_add()` inserts a value only if absent.
- `ulist_add_merge()` inserts a value or, if present, returns the existing auxiliary value through `old_aux`.
- `ulist_del()` removes a node only when both value and auxiliary value match.
- `ulist_next()` iterates list nodes and guarantees nodes added during iteration will be reached later in the same traversal.

Core mechanics:
- The rb-tree provides uniqueness and lookup by `val`; the linked list provides stable append-order traversal for graph/tree worklists.
- Insertions first search the rb-tree. Existing values return `0`; newly inserted values return `1`; allocation failures return `-ENOMEM`.
- `ulist->prealloc` is consumed by the next successful insertion path and cleared, otherwise insertion allocates with the caller-provided GFP mask.
- Deletion erases the rb-node, unlinks the list node, frees it, and decrements `nnodes`.
- Iteration stores the current list position in `struct ulist_iterator`; callers initialize it with `ULIST_ITER_INIT()`.

Important invariants:
- Locking is external. Writers need write-side locking when shared; iteration needs caller-provided read-side protection.
- `val` is the uniqueness key; `aux` is payload and is not considered by normal add/lookup.
- `ulist_del()` is stricter than lookup and requires both `val` and `aux` to match before deleting.
- `ulist_release()` does not explicitly reset `nnodes`; `ulist_reinit()` follows it with `ulist_init()` when full reuse state is needed.

Filesystem relevance:
- Btrfs uses ulist-style structures for non-recursive traversal of metadata/reference graphs where logical addresses or ids fit in `u64` and repeated visits must be suppressed.

Notable risks:
- The collection is not internally synchronized.
- Iterator validity depends on callers not deleting the current node unexpectedly during traversal.
- `ulist_add_merge_ptr()` in the header casts pointers through `u64`; the 32-bit branch preserves the public signature but pointer-sized assumptions remain important.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/ulist.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/ulist.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/ulist.h

Declares the `ulist` unique-`u64` collection used by Btrfs traversal code.

Key declarations:
- `struct ulist_iterator` holds a current list position for `ulist_next()`.
- `struct ulist_node` stores `val`, `aux`, a linked-list node, and an rb-tree node.
- `struct ulist` stores `nnodes`, the list head, rb-tree root, and one optional preallocated node.
- APIs cover initialization, release, reuse, allocation/free, preallocation, add, add-with-existing-aux-return, delete, and iteration.
- `ulist_add_merge_ptr()` is a pointer-oriented wrapper for storing pointer payloads in `aux`.
- `ULIST_ITER_INIT()` initializes an iterator before traversal.

Core mechanics:
- The public data structure intentionally exposes both list and rb-tree nodes, matching kernel-style lightweight containers.
- `ulist_add_merge_ptr()` handles pointer payloads differently on 32-bit and 64-bit builds to preserve the `u64` backing storage API.

Important invariants:
- `ulist_node.val` is the unique key.
- `ulist_node.aux` is caller-defined metadata and may encode ids, logical addresses, or pointers.
- Callers must provide locking if a ulist is accessed concurrently.

Filesystem relevance:
- This header provides a reusable primitive for Btrfs graph walks that need "visit once, enumerate all" behavior without recursion.

Notable risks:
- Because the structure layout is public, direct field manipulation by callers could bypass rb-tree/list consistency if not disciplined.
- Pointer payload use through `aux` must account for architecture width and lifetime of the pointed-to objects.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/ulist.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/uuid-tree.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/uuid-tree.c

Implements the Btrfs UUID tree, an index from subvolume UUID or received UUID to subvolume root ids, plus creation, scanning, validation, and stale-entry cleanup.

Key entry points:
- `btrfs_uuid_tree_add()` adds a root id to the UUID item for a given UUID/type pair.
- `btrfs_uuid_tree_remove()` removes a root id from a UUID item and deletes the whole item when it was the last id.
- `btrfs_uuid_tree_check_overflow()` checks whether adding another root id would exceed maximum leaf item capacity.
- `btrfs_uuid_tree_iterate()` walks UUID-tree items and removes stale subvolume UUID entries.
- `btrfs_uuid_scan_kthread()` scans root items and populates the UUID tree after creation.
- `btrfs_create_uuid_tree()` creates the UUID tree root, commits it, and starts the rescan kthread.

Core mechanics:
- `btrfs_uuid_to_key()` maps a 16-byte UUID into a Btrfs key by storing the first 8 bytes in `objectid`, the key type in `type`, and the second 8 bytes in `offset`, using unaligned little-endian loads.
- UUID tree item payloads are packed arrays of little-endian `u64` subvolume/root ids.
- `btrfs_uuid_tree_lookup()` searches for a UUID/type key and scans the item payload for a specific subid.
- Adding first tries lookup to avoid duplicates. New UUID/type pairs insert an item; existing pairs extend the item and append the new subid.
- Removal searches with transaction intent, finds the matching subid payload entry, memmoves later ids over it, and truncates the item, or deletes the item when only one id existed.
- Iteration reconstructs UUID bytes from key objectid/offset, validates referenced subvolume roots, and deletes entries whose root is gone or whose UUID no longer matches the root item.
- The scan kthread walks tree-root `BTRFS_ROOT_ITEM_KEY` items, filters live subvolume roots, and writes non-empty `uuid` and `received_uuid` values to the UUID tree in small transactions.

Important invariants:
- UUID item sizes must be aligned to `sizeof(u64)`; unaligned sizes are warned about and treated as invalid/skipped.
- The UUID tree root must exist for add/remove/check operations; missing roots trigger `WARN_ON_ONCE()` and `-EINVAL`.
- Only `BTRFS_UUID_KEY_SUBVOL` and `BTRFS_UUID_KEY_RECEIVED_SUBVOL` are semantically validated by stale-entry checks.
- Overflow prevention must account for `struct btrfs_item` plus current payload plus one `u64` within the leaf data size.
- The rescan semaphore is released when the scan kthread exits, and `BTRFS_FS_UPDATE_UUID_TREE_GEN` is set only after successful non-closing scans.

Filesystem relevance:
- The UUID tree is a metadata index for subvolume identity and received-subvolume identity. It supports efficient lookup and maintenance of UUID-to-root-id mappings used by ioctl/subvolume workflows.

Notable risks:
- Corrupt item lengths are tolerated with warnings but can leave entries skipped rather than repaired in place.
- The iteration cleanup restarts searches after removals, which is correct but can be expensive if many stale entries exist.
- Scan population uses separate transactions while walking root items; error handling must carefully release paths and end transactions.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/uuid-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/uuid-tree.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/uuid-tree.h

Declares the Btrfs UUID tree management API.

Key declarations:
- `btrfs_uuid_tree_add()` and `btrfs_uuid_tree_remove()` update UUID/type to subid mappings inside a transaction.
- `btrfs_uuid_tree_check_overflow()` checks if an additional subid can fit in an existing UUID item.
- `btrfs_uuid_tree_iterate()` validates and cleans UUID tree contents.
- `btrfs_create_uuid_tree()` creates the UUID tree and starts initial population.
- `btrfs_uuid_scan_kthread()` is the worker entry point for scanning roots into the UUID tree.

Core mechanics:
- The header keeps transaction and filesystem structs opaque and exposes only the high-level UUID tree operations.
- UUID types are passed as `u8`, matching Btrfs key type values for subvolume and received-subvolume UUID entries.

Important invariants:
- Add/remove callers must supply an active transaction handle.
- The `uuid` pointer must address a full Btrfs UUID-sized byte array.
- `subid` is the root/subvolume id stored in the UUID tree item payload.

Filesystem relevance:
- This is the interface used by root/subvolume management code to maintain the on-disk UUID index.

Notable risks:
- The API assumes callers understand which UUID key type they are maintaining; type confusion would create valid-looking but semantically wrong index items.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/uuid-tree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/verity.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/verity.c

Implements Btrfs support for Linux fs-verity operations by storing verity descriptors and Merkle tree bytes as dedicated items in the inode's filesystem tree.

Key entry points:
- `btrfs_drop_verity_items()` removes all descriptor and Merkle tree items for an inode.
- `btrfs_get_verity_descriptor()` reads and validates the Btrfs descriptor-size wrapper and generic fs-verity descriptor blob.
- `btrfs_verityops` wires Btrfs into fs-verity with begin/end enable, descriptor read, Merkle page read, and Merkle block write callbacks.
- `btrfs_begin_enable_verity()` prepares enabling by rejecting encrypted files, dropping stale verity items, adding an orphan item, and setting `BTRFS_INODE_VERITY_IN_PROGRESS`.
- `btrfs_end_enable_verity()` finalizes or rolls back depending on whether fs-verity supplies a descriptor.
- `btrfs_read_merkle_tree_page()` reads Merkle bytes from Btrfs items into page-cache folios positioned past EOF.
- `btrfs_write_merkle_tree_block()` writes Merkle blocks into Btrfs verity Merkle items.

Core mechanics:
- Descriptor metadata uses keys `[ino, BTRFS_VERITY_DESC_ITEM_KEY, offset]`; offset `0` stores `struct btrfs_verity_descriptor_item`, and offset `1` onward stores the opaque fs-verity descriptor.
- Merkle data uses keys `[ino, BTRFS_VERITY_MERKLE_ITEM_KEY, offset]`, where offsets are byte offsets into the Merkle tree.
- `write_key_bytes()` writes arbitrary byte ranges into multiple Btrfs items, splitting inserts into at most 2 KiB chunks for leaf-size friendliness.
- `read_key_bytes()` reads sequential item payloads from a key type and offset, supporting count-only mode, buffer-copy mode, and folio-copy mode with forward readahead.
- `merkle_file_pos()` rounds `i_size` up to a 64 KiB boundary and uses that logical position only for page-cache placement of Merkle pages.
- `drop_verity_items()` walks backward from offset `U64_MAX` deleting all items of a given verity key type for the inode.
- Enable is protected by a normal orphan item so interrupted or failed verity setup can be cleaned up rather than leaving partial Merkle/descriptor state.
- `finish_verity()` writes the descriptor wrapper/blob, sets `BTRFS_INODE_RO_VERITY`, syncs inode flags, deletes the orphan item, clears the in-progress bit, and sets the filesystem read-only compatible `VERITY` bit.
- `rollback_verity()` truncates cached Merkle pages, clears in-progress state, drops verity items, removes the inode verity flag, updates the inode, and deletes the verity orphan.

Important invariants:
- Verity enable requires the inode lock; begin/end/rollback assert this.
- Btrfs currently rejects fs-verity enable on encrypted inodes.
- Descriptor wrapper reserved fields must remain zero, and descriptor size must fit in `INT_MAX`.
- A successful descriptor read must return exactly the true descriptor size; short reads become `-EIO`.
- Merkle page-cache positions must not exceed `s_maxbytes`; overflow checks guard both reads and writes.
- Partial Merkle pages are zero-filled after short reads before being marked uptodate.
- Rollback errors are treated as filesystem errors because partial verity state could otherwise persist.

Filesystem relevance:
- This file integrates authenticity verification for Btrfs regular files while preserving Btrfs' normal inode size semantics by storing fs-verity metadata as btree items instead of past-EOF file extents.

Notable risks:
- Writing Merkle data can be lengthy and space-consuming, so failure paths are intentionally complex and depend on orphan cleanup.
- `write_key_bytes()` and `read_key_bytes()` require strictly sequential item offsets for descriptor/Merkle blobs; gaps produce short reads or failure at higher layers.
- Cache placement past EOF is synthetic; overflow and truncation interactions must remain aligned with fs-verity expectations.
- Future Btrfs encryption support must account for encrypting descriptor and Merkle items, as noted in the file comments.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/verity.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/verity.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/verity.h

Declares Btrfs fs-verity integration points and provides stubs when fs-verity support is disabled.

Key declarations:
- With `CONFIG_FS_VERITY`, exports `btrfs_verityops`, `btrfs_drop_verity_items()`, and `btrfs_get_verity_descriptor()`.
- Without `CONFIG_FS_VERITY`, `btrfs_drop_verity_items()` is an inline no-op returning `0`, and `btrfs_get_verity_descriptor()` returns `-EPERM`.

Core mechanics:
- The header includes `<linux/fsverity.h>` only for fs-verity builds and `<linux/errno.h>` for stub builds.
- It forward-declares `struct inode` and `struct btrfs_inode` to keep dependencies minimal.

Important invariants:
- Callers can invoke `btrfs_drop_verity_items()` unconditionally; behavior compiles to a no-op when fs-verity is unavailable.
- Descriptor access is explicitly denied when fs-verity is not configured.

Filesystem relevance:
- This header is the compile-time boundary between Btrfs core inode/orphan paths and optional fs-verity support.

Notable risks:
- Build-configuration behavior differs: cleanup calls silently succeed without fs-verity, while descriptor reads fail with permission-style error.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/verity.h -->