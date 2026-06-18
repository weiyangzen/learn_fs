# Group Research: group_960_linux_stable_sources_os_linux_linux_stable_fs_btrfs_tree_mod_log_c_s_39462e0065c4

Scope: subset A from `Docs/research_subset_a.md`, covering the listed `sources/os/linux/linux-stable/fs/btrfs` files. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tree-mod-log.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/tree-mod-log.c

## Scope

This file implements Btrfs tree modification logging, which lets readers reconstruct older views of internal B-tree nodes and roots while concurrent tree mutations are happening. It records key pointer changes, moves, block frees, root replacements, and copy operations, then rewinds extent buffers to a requested sequence number.

## Public And Internal APIs Covered

- Sequence-user lifecycle: `btrfs_get_tree_mod_seq()`, `btrfs_put_tree_mod_seq()`, `btrfs_tree_mod_log_lowest_seq()`.
- Log insertion APIs: `btrfs_tree_mod_log_insert_key()`, `btrfs_tree_mod_log_insert_move()`, `btrfs_tree_mod_log_insert_root()`, `btrfs_tree_mod_log_eb_copy()`, `btrfs_tree_mod_log_free_eb()`.
- Rewind/query APIs: `btrfs_tree_mod_log_rewind()`, `btrfs_get_old_root()`, `btrfs_old_root_level()`.
- Internal helpers manage RB-tree insertion/search, allocation of `tree_mod_elem`, root ancestry lookup, and reverse replay.

## Control Flow And Behavior

- Active readers register a `btrfs_seq_list` entry and receive a monotonically increasing tree-mod sequence. The first active user sets `BTRFS_FS_TREE_MOD_LOG_USERS`; the last clears it.
- Dropping a sequence user prunes RB-tree log entries whose sequence is older than the lowest remaining active sequence.
- Logging is skipped when there are no users, for leaf extent buffers, and for trees outside the extent tree and filesystem/subvolume trees.
- Log entries are stored in `fs_info->tree_mod_log`, ordered by affected logical address and modification sequence. Root replacement entries are keyed by the new root logical address while carrying the old root address/level/generation.
- Mutation helpers allocate all needed log elements before taking the write lock, then recheck whether logging is still needed. Allocation failures are ignored if logging became unnecessary, but returned if a log user still exists.
- Key removals, replacements, additions, moves, extent-buffer frees, root swaps, and copy operations are represented as `BTRFS_MOD_LOG_*` operations.
- `tree_mod_log_rewind()` walks log entries from newest toward the target sequence and applies inverse operations to a cloned or dummy extent buffer.
- `btrfs_tree_mod_log_rewind()` returns the original read-locked buffer if no rewind is needed; otherwise it releases/frees the input and returns a newly read-locked rewind buffer.
- `btrfs_get_old_root()` finds the oldest logged predecessor of a root at a sequence, reads/clones/allocates the needed root buffer, restores header metadata for old roots, and replays logged changes.

## State And Data Structures

- `struct tree_mod_elem` stores RB linkage, logical address, sequence, operation type, slot/generation, and operation-specific payload.
- Payloads include old key/block pointer data, move destination/count, or old-root logical address and level.
- `fs_info->tree_mod_log_lock` protects both the active sequence list and the modification RB tree.
- Extent-buffer metadata accessors are used to save and restore node keys, block pointers, pointer generations, item counts, owners, levels, bytenrs, and backref revisions.

## Dependencies

- Btrfs core structures: `btrfs_fs_info`, `btrfs_root`, `extent_buffer`, tree roots, and filesystem flags.
- Tree accessors and buffer helpers from Btrfs accessors/disk-io/tree-checking code.
- Linux RB tree, list, atomic64 sequence counter, rwlock, and allocation APIs.

## Risks And Invariants

- Callers rely on exact sequence ordering; pruning too aggressively would break backref and extent iteration over old tree views.
- Only internal nodes are logged. Leaf rewind is intentionally skipped.
- The two-step `tree_mod_need_log()` / `tree_mod_dont_log()` pattern is important because logging may become unnecessary while allocations are being prepared.
- Reverse replay must keep `nritems` and slot movement consistent; invalid move ranges warn and can indicate deeper tree-mod-log corruption.
- Root replacement logging is special because the log is keyed by the new root while old-root reconstruction follows predecessor links.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tree-mod-log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tree-mod-log.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/tree-mod-log.h

## Scope

This header declares the Btrfs tree modification log interface used by tree mutation and old-root lookup paths.

## APIs And Constants

- Defines `struct btrfs_seq_list`, the per-user sequence-list element used to hold an active tree-mod-log read window.
- Provides `BTRFS_SEQ_LIST_INIT()` and `BTRFS_SEQ_LAST`.
- Defines `enum btrfs_mod_log_op` for key replacement/add/remove, remove while freeing, remove while moving, key moves, and root replacement.
- Declares all public tree-mod-log sequence, insertion, rewind, old-root, copy, move, free, and lowest-sequence helpers.

## Dependencies And Role

- Forward-declares Btrfs tree structures to keep the header lightweight.
- Included by Btrfs tree manipulation code that must emit log records before mutating internal tree blocks.

## Risks And Invariants

- Operation enum values encode the inverse replay cases implemented in `tree-mod-log.c`.
- `btrfs_seq_list.seq` must be initialized to zero before first registration, otherwise the user will not be added to the active list.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tree-mod-log.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/ulist.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/ulist.c

## Scope

This file implements `ulist`, a compact Btrfs utility structure for storing unique `u64` values with an auxiliary `u64`, supporting insertion, deletion, and enumeration. It is suited for graph/tree walks where recursion is undesirable due to kernel stack limits.

## Public And Internal APIs Covered

- Lifecycle: `ulist_init()`, `ulist_release()`, `ulist_reinit()`, `ulist_alloc()`, `ulist_prealloc()`, `ulist_free()`.
- Mutation: `ulist_add()`, `ulist_add_merge()`, `ulist_del()`.
- Iteration: `ulist_next()`.
- Internal RB-tree helpers search, insert, erase, and compare by `val`.

## Control Flow And Behavior

- Each node is linked into both a list and an RB tree. The RB tree enforces uniqueness and speeds lookup; the list drives iteration.
- `ulist_add_merge()` returns `0` if the value already exists, `1` if inserted, and `-ENOMEM` on allocation failure. If requested, it returns the old auxiliary value for existing entries.
- `ulist_prealloc()` reserves one node for later insertion, allowing callers to reduce allocation risk in constrained sections.
- `ulist_del()` removes an entry only when both `val` and `aux` match.
- `ulist_next()` advances a simple list iterator. Newly appended entries can appear in an ongoing traversal.

## State And Data Structures

- `struct ulist` tracks `nnodes`, list head, RB root, and one optional preallocated node.
- `struct ulist_node` carries `val`, `aux`, list linkage, and RB linkage.
- `struct ulist_iterator` stores the current list position only.

## Dependencies

- Linux slab allocation, lists, RB trees, and Btrfs assertion/message helpers.
- Caller-provided locking is required; write locking is needed for mutation and read locking is enough for iteration.

## Risks And Invariants

- The list and RB tree must stay synchronized for every insert/delete.
- `nnodes` is decremented with a `BUG_ON()` guard against underflow.
- Iteration order is intentionally unspecified and must not be treated as sorted or insertion-stable API.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/ulist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/ulist.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/ulist.h

## Scope

This header defines the Btrfs `ulist` data structures and function prototypes.

## APIs And Constants

- Defines `struct ulist_iterator`, `struct ulist_node`, and `struct ulist`.
- Declares lifecycle, preallocation, insertion/merge, deletion, and iteration functions.
- Provides `ulist_add_merge_ptr()` for storing pointer auxiliary data through the `u64 aux` field.
- Provides `ULIST_ITER_INIT()` to initialize iterators.

## Dependencies And Role

- Includes Linux integer types, lists, and RB trees.
- Used by Btrfs traversal code needing a uniqueness set with optional auxiliary state.

## Risks And Invariants

- `ulist_add_merge_ptr()` has a 32-bit compatibility path; callers must treat pointer auxiliary data carefully across architectures.
- The header documents that callers own locking; the implementation does not provide internal synchronization.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/ulist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/uuid-tree.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/uuid-tree.c

## Scope

This file implements Btrfs UUID tree maintenance. The UUID tree maps subvolume UUIDs and received UUIDs to subvolume/root IDs, supports add/remove/overflow checks, validates existing entries, scans roots to populate a new UUID tree, and creates the UUID tree when needed.

## Public And Internal APIs Covered

- Public operations: `btrfs_uuid_tree_add()`, `btrfs_uuid_tree_remove()`, `btrfs_uuid_tree_check_overflow()`, `btrfs_uuid_tree_iterate()`, `btrfs_uuid_scan_kthread()`, `btrfs_create_uuid_tree()`.
- Internal helpers: `btrfs_uuid_to_key()`, `btrfs_uuid_tree_lookup()`, `btrfs_uuid_iter_rem()`, `btrfs_check_uuid_tree_entry()`.

## Control Flow And Behavior

- UUID keys are derived by splitting the 16-byte UUID into little-endian `objectid` and `offset`, with key type indicating subvolume UUID or received-subvolume UUID.
- Add first checks for an existing UUID/subid pair. If absent, it inserts a new item or extends an existing item and appends the little-endian subvolume ID.
- Remove searches the UUID item, finds the matching subid, deletes the whole item if it was the only entry, or compacts and truncates the item otherwise.
- Overflow check verifies whether one more `u64` subid can fit in the leaf item.
- Iteration walks UUID tree items, validates subvolume UUID mappings against the referenced root item, and removes stale entries in their own short transactions.
- The scan kthread walks the tree root for live root items, skips deleted/unreferenced roots, and inserts non-empty UUID and received UUID mappings into the UUID tree.
- Creating the UUID tree starts a transaction, creates the dedicated UUID tree root, commits it, then starts the rescan kthread under `uuid_tree_rescan_sem`.

## State And Data Structures

- UUID tree items store a variable-length array of little-endian `u64` subvolume IDs.
- Valid item sizes must be aligned to `sizeof(u64)`.
- Root items supply `uuid`, `received_uuid`, root refs, and root IDs.
- `fs_info->uuid_root`, `tree_root`, `uuid_tree_rescan_sem`, and `BTRFS_FS_UPDATE_UUID_TREE_GEN` are central state.

## Dependencies

- Btrfs transaction, path, search, item insert/extend/truncate/delete, root lookup, and tree creation APIs.
- Linux kthread, UUID/unaligned helpers, and scheduler rescheduling.

## Risks And Invariants

- UUID item sizes must remain `u64` aligned; malformed sizes are warned and treated as lookup/removal failures or skipped during iteration.
- The UUID tree can contain multiple subids for one UUID key, so add/remove must preserve compact array layout.
- Iteration releases the path before modifying the tree and restarts search after removals to avoid stale path state.
- The scan kthread must stop cleanly on filesystem closing and always release the rescan semaphore.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/uuid-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/uuid-tree.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/uuid-tree.h

## Scope

This header declares the Btrfs UUID tree public interface.

## APIs

- Declares add/remove operations for UUID/subvolume-ID mappings.
- Declares overflow checking before adding another mapping.
- Declares full-tree validation/iteration, UUID tree creation, and the UUID scan kthread entry point.

## Dependencies And Role

- Forward-declares transaction and filesystem structures.
- Used by ioctl, root/subvolume, mount, and UUID tree setup paths that need to maintain or rebuild UUID mappings.

## Risks And Invariants

- Callers must pass the correct UUID key type; the implementation only validates recognized types during iteration/checking paths.
- Add/remove require an active transaction handle.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/uuid-tree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/verity.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/verity.c

## Scope

This file integrates Btrfs with fs-verity. It stores verity descriptors and Merkle tree data as dedicated Btrfs tree items, manages enable/rollback/finalization with orphan protection, and implements the `fsverity_operations` callbacks.

## Public And Internal APIs Covered

- Exported to Btrfs: `btrfs_drop_verity_items()`, `btrfs_get_verity_descriptor()`, `btrfs_verityops`.
- fs-verity callbacks: begin enable, end enable, get descriptor, read Merkle tree page, write Merkle tree block.
- Internal helpers: `merkle_file_pos()`, `drop_verity_items()`, `write_key_bytes()`, `read_key_bytes()`, `del_orphan()`, `rollback_verity()`, `finish_verity()`.

## Control Flow And Behavior

- Verity descriptor items use key type `BTRFS_VERITY_DESC_ITEM_KEY`; offset `0` stores a Btrfs descriptor-size item and offsets starting at `1` store the fs-verity descriptor blob.
- Merkle tree items use key type `BTRFS_VERITY_MERKLE_ITEM_KEY`, indexed from byte offset `0` in the Merkle tree.
- Merkle pages are cached in the inode mapping at a synthetic file position: file size rounded up to 64 KiB, ensuring the cache range is past EOF.
- Enabling verity rejects encrypted files, drops stale verity items, adds an orphan item, and sets `BTRFS_INODE_VERITY_IN_PROGRESS`.
- Merkle blocks are written as Btrfs items via `write_key_bytes()`, split into chunks up to 2 KiB.
- Finalization writes descriptor metadata and descriptor bytes, sets `BTRFS_INODE_RO_VERITY`, updates inode flags, deletes the orphan item, sets the filesystem read-only compat verity bit, and clears the in-progress flag.
- If fs-verity signals failure or finalization fails, rollback truncates cached Merkle pages, clears in-progress state, drops verity items, clears the inode verity flag, updates the inode, and deletes the orphan.
- Descriptor reads support the fs-verity two-pass size-then-data pattern and validate reserved fields and descriptor size.
- Merkle page reads populate the page cache from tree items, zero-fill short final pages, and return cached pages when already uptodate.

## State And Data Structures

- Uses inode runtime flag `BTRFS_INODE_VERITY_IN_PROGRESS` and read-only inode flag `BTRFS_INODE_RO_VERITY`.
- Uses `struct btrfs_verity_descriptor_item` to store descriptor size and reserved fields.
- Uses Btrfs item keys under the file inode objectid for both descriptor and Merkle data.
- Uses orphan items to recover or clean up interrupted verity enable operations.

## Dependencies

- Linux fs-verity API, folio/page-cache APIs, xattr/security includes, inode locking, and mapping allocation constraints.
- Btrfs transaction, orphan, tree item, inode update, extent-buffer read/write, and filesystem compat-ro feature helpers.

## Risks And Invariants

- Btrfs stores verity data outside file size, unlike ext4/f2fs, so cache-position overflow checks against `s_maxbytes` are required.
- Rollback errors are treated as filesystem-level errors because partially written verity metadata would be unsafe.
- `read_key_bytes()` requires sequential item offsets after the first copied item; gaps intentionally produce short reads.
- Orphan handling intentionally ignores zero-link inodes because unlink/tmpfile paths own their own orphan state.
- Encryption is currently unsupported for Btrfs fs-verity in this implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/verity.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/verity.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/verity.h

## Scope

This header declares Btrfs fs-verity integration points and provides stubs when fs-verity is disabled.

## APIs

- Under `CONFIG_FS_VERITY`, declares `btrfs_verityops`, `btrfs_drop_verity_items()`, and `btrfs_get_verity_descriptor()`.
- Without fs-verity, `btrfs_drop_verity_items()` returns success and `btrfs_get_verity_descriptor()` returns `-EPERM`.

## Dependencies And Role

- Includes `<linux/fsverity.h>` only when fs-verity support is enabled.
- Keeps callers buildable regardless of the fs-verity Kconfig setting.

## Risks And Invariants

- Disabled-build stubs intentionally do not expose descriptor data.
- Callers must account for `-EPERM` from `btrfs_get_verity_descriptor()` when fs-verity is not compiled in.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/verity.h -->