# subset-b-005628 Research

Grouped source research for Btrfs tree modification logging, unique u64 list helpers, UUID tree maintenance, and fs-verity storage integration. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tree-mod-log.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/tree-mod-log.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/tree-mod-log.c` implements Btrfs' tree modification log: a transient, in-memory history of interior-tree and root changes used to give backref and extent walkers a consistent older view while concurrent writers mutate subvolume and extent trees. The file was read as a complete 1146-line source file for this report.

## Important APIs, Types, and Functions

Core private state is `struct tree_mod_elem`, an rb-tree node keyed by extent-buffer logical address and sequence, and `struct tree_mod_root`, the compact old-root pointer/level payload for root replacement records. `tree_mod_elem` carries the operation (`enum btrfs_mod_log_op`), slot, generation, and one of three payloads: removed/replaced key and block pointer, move metadata, or old-root metadata.

Public entry points include `btrfs_get_tree_mod_seq()` and `btrfs_put_tree_mod_seq()` for reader blockers, mutator logging functions `btrfs_tree_mod_log_insert_key()`, `btrfs_tree_mod_log_insert_move()`, `btrfs_tree_mod_log_insert_root()`, `btrfs_tree_mod_log_eb_copy()`, and `btrfs_tree_mod_log_free_eb()`, reconstruction helpers `btrfs_tree_mod_log_rewind()`, `btrfs_get_old_root()`, `btrfs_old_root_level()`, and status helper `btrfs_tree_mod_log_lowest_seq()`.

Important private helpers include `tree_mod_dont_log()`, `tree_mod_need_log()`, `alloc_tree_mod_elem()`, `tree_mod_log_insert()`, `tree_mod_log_search()`, `tree_mod_log_search_oldest()`, `tree_mod_log_oldest_root()`, and the static rewind engine `tree_mod_log_rewind()`.

## Control Flow

Readers that need a stable historical tree view initialize a `struct btrfs_seq_list`, call `btrfs_get_tree_mod_seq()`, perform their backref walk or tree iteration using that sequence, and eventually call `btrfs_put_tree_mod_seq()`. The get path increments `fs_info->tree_mod_seq`, links the blocker into `fs_info->tree_mod_seq_list`, and sets `BTRFS_FS_TREE_MOD_LOG_USERS`; the put path removes the blocker and frees rb-tree entries older than the lowest remaining blocker.

Writers call logging functions from Btrfs tree mutation paths before or around operations such as COW root replacement, key replacement, pointer insertion/removal, node splitting, node balancing, and extent-buffer copying. Each log function first performs a cheap `tree_mod_need_log()` test, preallocates records outside the write lock, then rechecks with `tree_mod_dont_log()` while holding `fs_info->tree_mod_log_lock`. If no blockers remain, allocations are discarded and the operation proceeds without logging; if blockers remain and allocation failed, the mutator returns an error.

The rb-tree ordering is by logical address and then descending sequence for a given logical block. Search helpers find either the newest record at or above a minimum sequence or the oldest record at or above that sequence. Rewind starts from the most recent relevant operation and walks forward through rb-next entries for the same logical block, applying the inverse of each logged operation until it reaches the requested historical time. Root reconstruction first follows `BTRFS_MOD_LOG_ROOT_REPLACE` records to locate the old root logical address and level, reads or allocates an extent buffer when necessary, then replays node-level changes.

## State and Persistence Behavior

The tree modification log is memory-only state under `btrfs_fs_info`: `tree_mod_seq`, `tree_mod_seq_list`, `tree_mod_log`, `tree_mod_log_lock`, and the users flag. It is not persisted to disk and is pruned when sequence blockers disappear. Logged records copy just enough btree node/root metadata to undo pointer-array changes for historical readers; leaf modifications are intentionally skipped, and `skip_eb_logging()` restricts logging to non-leaf extent buffers from the extent tree and filesystem trees.

The code allocates records with `GFP_NOFS` and carefully stages allocations before taking the write lock. Rewind allocates cloned or dummy extent buffers, transfers read locks to the returned buffer, and frees the current buffer when a rewind buffer is produced. Old-root reads may read tree blocks from disk when the old root still exists and needs to be cloned before replay.

## Dependencies and Integration Points

This file depends on Btrfs accessors, extent-buffer helpers, rb-trees, read/write locks, fs-info flags, tree block validation, and btree mutation code. It is integrated heavily from `ctree.c` mutation paths, while `backref.c` obtains tree-mod sequences for historical reference walking and `delayed-ref.c` queries the lowest active sequence to coordinate delayed refs. The header is included by Btrfs tree and backref code that needs either to log mutations or to retrieve old roots.

## Risks and Edge Cases

The ordering and replay logic are correctness-critical: an incorrect sequence order, missing move/remove record, or bad slot arithmetic can corrupt the reconstructed historical node and mislead backref accounting. Memory allocation failures are tolerated only when logging is no longer required after the lock recheck; otherwise mutators must fail. Root replacement is special because records are keyed by the new root logical address but may reconstruct an older root logical address and level.

The code uses `BUG_ON`, `ASSERT`, and `WARN_ON` around invariants such as slot bounds, move ranges, and node item counts. Rewind tracks `max_slot` separately from `nritems` to catch invalid memmoves during historical replay. Races are handled by rechecking the latest tree-mod record after cloning an old block in `btrfs_get_old_root()`, but that path remains sensitive to concurrent logging between search, read, and clone.

## Test Signals

Useful signals include fstests covering qgroups, backref walking, delayed refs, snapshot deletion, balance, relocation, and send/receive under concurrent metadata mutation. Targeted tests should exercise node splits/merges, root promotion/replacement, `btrfs_tree_mod_log_eb_copy()` left and right pushes, low-memory failures after a tree-mod blocker exists, and historical reads while writers modify extent and filesystem trees. Kernel warning-free runs are important because many bad states are surfaced through `WARN_ON`, `BUG_ON`, and tree checker failures rather than ordinary return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tree-mod-log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tree-mod-log.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/tree-mod-log.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/tree-mod-log.h` declares the Btrfs tree modification log interface shared by tree mutation, backref, delayed-ref, and historical tree-walk code. The file was read as a complete 58-line header for this report.

## Important APIs, Types, and Functions

The header defines `struct btrfs_seq_list`, the caller-owned sequence blocker object placed on `fs_info->tree_mod_seq_list`, plus `BTRFS_SEQ_LIST_INIT` and `BTRFS_SEQ_LAST`. `enum btrfs_mod_log_op` names all mutation records the implementation can replay: key replacement, add, remove, remove while freeing, remove while moving, key moves, and root replacement.

Declared functions cover sequence lifetime (`btrfs_get_tree_mod_seq()`, `btrfs_put_tree_mod_seq()`), mutation logging (`btrfs_tree_mod_log_insert_root()`, `btrfs_tree_mod_log_insert_key()`, `btrfs_tree_mod_log_free_eb()`, `btrfs_tree_mod_log_eb_copy()`, `btrfs_tree_mod_log_insert_move()`), historical reconstruction (`btrfs_tree_mod_log_rewind()`, `btrfs_get_old_root()`, `btrfs_old_root_level()`), and global state query (`btrfs_tree_mod_log_lowest_seq()`).

## Control Flow

The header has no executable control flow. It establishes the protocol: callers that need historical consistency hold a `btrfs_seq_list` blocker, mutators log operations with the enum values that correspond to the mutation they are about to perform, and readers pass the captured sequence to old-root or rewind helpers.

## State and Persistence Behavior

The only state shape exposed here is `struct btrfs_seq_list`, which stores a list node and sequence number. The actual log records, rb-tree, locks, and pruning policy remain private to `tree-mod-log.c`. All state is volatile memory and does not encode an on-disk format.

## Dependencies and Integration Points

The header includes `<linux/list.h>` and forward declares Btrfs and extent-buffer types to keep include dependencies small. It is consumed by `ctree.c` for metadata mutation logging, by backref code for sequence acquisition and old-root lookup, and by delayed-ref code for lowest-sequence coordination.

## Risks and Edge Cases

The public enum values are tied to replay semantics in `tree-mod-log.c`; adding or reordering uses without implementing inverse replay would break historical reconstruction. Callers must initialize `btrfs_seq_list.seq` to zero before first use and must pair get/put calls or old records will remain pinned. Mutator callers must pass the correct operation type and slot before changing the extent buffer.

## Test Signals

Compile coverage should catch signature drift between callers and implementation. Runtime coverage should include backref and qgroup tests that acquire blockers while `ctree.c` performs every declared mutation type. Static analysis should confirm get/put pairing and that no caller logs leaf buffers unnecessarily.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tree-mod-log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/ulist.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/ulist.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/ulist.c` implements Btrfs' generic unique-list container for `u64` values with an auxiliary `u64` payload. It supports graph/tree traversal without revisiting the same logical node, which is important in Btrfs backref, relocation, qgroup, and send paths where recursive traversal would risk kernel stack exhaustion. The file was read as a complete 298-line source file for this report.

## Important APIs, Types, and Functions

Exported functions are `ulist_init()`, `ulist_release()`, `ulist_reinit()`, `ulist_alloc()`, `ulist_prealloc()`, `ulist_free()`, `ulist_add()`, `ulist_add_merge()`, `ulist_del()`, and `ulist_next()`. Private rb-tree helpers are `ulist_node_val_key_cmp()`, `ulist_rbtree_search()`, `ulist_rbtree_erase()`, `ulist_node_val_cmp()`, and `ulist_rbtree_insert()`.

The implementation maintains both a linked list and an rb-tree. The rb-tree provides uniqueness/search by `val`; the list provides iteration order and allows newly-added elements to appear in an ongoing traversal.

## Control Flow

Initialization creates an empty list, empty rb-root, zero node count, and no preallocated node. Adds first search the rb-tree. If the value already exists, `ulist_add_merge()` optionally returns the existing aux through `old_aux` and returns 0 without modifying the stored aux. If the value is new, it consumes `ulist->prealloc` when present or allocates a fresh node, initializes `val` and `aux`, inserts it into the rb-tree, appends it to the tail list, increments `nnodes`, and returns 1.

Deletion searches by value, verifies that both value and aux match, erases the rb-node, unlinks the list entry, frees the node, and decrements `nnodes`. Iteration uses `struct ulist_iterator.cur_list` as a cursor into the list. `ulist_next()` returns NULL for an empty list or after the cursor reaches the list head; otherwise it advances to the next list entry and returns the containing `ulist_node`.

## State and Persistence Behavior

`ulist` state is entirely in memory. `ulist_release()` frees all allocated nodes and any preallocated spare node, resets the rb-root, and reinitializes the list head; `ulist_reinit()` performs release then init for reuse. `ulist_prealloc()` stores one zeroed spare node to avoid a future allocation in contexts that may need predictable add behavior. No state is persisted to disk.

## Dependencies and Integration Points

The file depends on kernel slab allocation, list and rb-tree APIs, and Btrfs assertion/messaging headers. It is used by `backref.c` for parent/root/reference enumeration, `qgroup.c` for qgroup graph and changed-range tracking, `relocation.c` for reference traversal, `send.c` for root-id sets, and `extent-io-tree.c`/`extent_io.h` for extent state change sets.

## Risks and Edge Cases

The container is not internally synchronized; callers must provide write locking for mutation and read locking for iteration when sharing across threads. `ulist_add_merge()` deliberately ignores a new aux for duplicate values, so callers that expect aux updates must handle duplicates explicitly. Iteration order is unspecified and should not be treated as sorted or insertion-stable beyond the guarantee that newly appended nodes can be seen by the current enumeration.

`ulist_add_merge_ptr()` in the header stores pointers through `u64`; this implementation must preserve `u64` aux values exactly, including on 32-bit builds where the wrapper handles conversion. A failed allocation leaves the container unmodified. `ulist_del()` requires both `val` and `aux` to match, which can surprise callers that intend value-only deletion.

## Test Signals

Unit-style tests should cover duplicate add, aux preservation, `old_aux` return, preallocation consumption, add-during-iteration, delete by matching and nonmatching aux, release/reinit reuse, and allocation failure. System-level signals are qgroup/backref/relocation/send tests that traverse graphs with cycles or shared references without duplicate processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/ulist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/ulist.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/ulist.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/ulist.h` declares the Btrfs unique `u64` list container used for iterative graph and tree walks. The file was read as a complete 77-line header for this report.

## Important APIs, Types, and Functions

The header defines `struct ulist_iterator` with a list cursor, `struct ulist_node` with `val`, `aux`, list node, and rb-tree node, and `struct ulist` with node count, list head, rb-root, and one preallocated node. It declares the lifecycle, mutation, deletion, and iteration functions implemented in `ulist.c`.

It also defines `ulist_add_merge_ptr()`, a pointer-friendly inline wrapper around `ulist_add_merge()`. On 32-bit builds it uses an intermediate `u64`; on 64-bit builds it casts the pointer storage directly through the aux pointer.

## Control Flow

There is no standalone runtime flow in the header. Callers initialize or allocate a `ulist`, add values while traversing, initialize an iterator with `ULIST_ITER_INIT()`, repeatedly call `ulist_next()`, and finally release/free the list.

## State and Persistence Behavior

The structs describe volatile in-memory traversal state only. `nnodes` tracks current membership, `nodes` is the iteration list, `root` is the uniqueness index, and `prealloc` is an optional spare node for future insertion.

## Dependencies and Integration Points

The header includes kernel `types`, `list`, and `rbtree` definitions. It is included by Btrfs backref, qgroup, relocation, send, and extent I/O code that needs duplicate suppression for logical addresses, root ids, qgroup ids, or extent ranges.

## Risks and Edge Cases

Callers must not assume internal locking, sorted iteration, or aux replacement on duplicate add. Pointer aux usage must only store pointer values that are valid for the lifetime of traversal. `ULIST_ITER_INIT()` must be called before first iteration, especially when stack-allocated iterators are reused.

## Test Signals

Compile coverage on both 32-bit and 64-bit configurations is useful for the pointer wrapper. Runtime tests should verify that public struct initialization and `ULIST_ITER_INIT()` interoperate with add-during-iteration behavior used by Btrfs graph walks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/ulist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/uuid-tree.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/uuid-tree.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/uuid-tree.c` maintains the Btrfs UUID tree, an auxiliary metadata tree mapping subvolume UUIDs and received UUIDs to root object ids. It supports lookup consistency, send/receive and ioctl workflows, cleanup of stale mappings, and initial UUID tree creation/rescan. The file was read as a complete 566-line source file for this report.

## Important APIs, Types, and Functions

Public functions are `btrfs_uuid_tree_add()`, `btrfs_uuid_tree_remove()`, `btrfs_uuid_tree_check_overflow()`, `btrfs_uuid_tree_iterate()`, `btrfs_uuid_scan_kthread()`, and `btrfs_create_uuid_tree()`. Private helpers include `btrfs_uuid_to_key()`, `btrfs_uuid_tree_lookup()`, `btrfs_uuid_iter_rem()`, and `btrfs_check_uuid_tree_entry()`.

UUIDs are converted to Btrfs keys by interpreting the first and second 64-bit chunks as little-endian `objectid` and `offset`, with the supplied UUID item type as `key.type`. UUID-tree item payloads are arrays of little-endian `u64` subvolume ids.

## Control Flow

`btrfs_uuid_tree_add()` first checks whether the UUID/type/subid tuple already exists. If not, it inserts a new item containing one subid or extends an existing item and appends the subid. `btrfs_uuid_tree_remove()` searches with transaction intent, scans the item payload for the subid, deletes the whole item when it was the only entry, or memmoves following entries down and truncates the item.

`btrfs_uuid_tree_check_overflow()` searches an existing UUID item and returns `-EOVERFLOW` if appending one more subid would exceed the leaf data size. This allows ioctl paths to reject duplicate/overflow-prone received UUID operations before starting a modification that would later fail in the add path.

`btrfs_uuid_tree_iterate()` walks UUID-tree items forward, validates item sizes, reconstructs the UUID from the key, and checks every subid against the referenced subvolume root. Stale entries are removed in a short transaction, then the search restarts because the btree changed. `btrfs_uuid_scan_kthread()` walks the tree root for live root items, reads each root item, and adds non-empty normal and received UUIDs to the UUID tree in small transactions. `btrfs_create_uuid_tree()` creates the UUID tree, commits it, then starts the rescan kthread.

## State and Persistence Behavior

Unlike the other helper containers in this group, the UUID tree is persistent on-disk Btrfs metadata stored under `BTRFS_UUID_TREE_OBJECTID`. Items are keyed by UUID-derived key fields and type, and values are packed arrays of root ids. The code mutates this tree in normal Btrfs transactions and updates `fs_info->uuid_root`.

The scan thread is coordinated with `fs_info->uuid_tree_rescan_sem`, notices filesystem closing, and sets `BTRFS_FS_UPDATE_UUID_TREE_GEN` after a complete scan so generation tracking can be updated. Stale mapping removal is persistent and transaction-backed.

## Dependencies and Integration Points

This file uses Btrfs transaction, ctree search/insert/extend/truncate/delete helpers, path management, root lookup/reference handling, unaligned UUID helpers, kthreads, and fs closing checks. Callers include subvolume creation in `transaction.c`, UUID changes and received-subvolume handling in `ioctl.c`, root rename/exchange behavior in `inode.c`, and mount/open cleanup in `disk-io.c`.

## Risks and Edge Cases

UUID item sizes must be aligned to `sizeof(u64)`; malformed sizes are warned about and treated as missing/stale. Append operations can overflow a leaf, so callers should use the overflow check when user-visible operations need preflight validation. Removal performs in-item memmove and truncation, so offset and size arithmetic must remain exact. The iterate path intentionally restarts after deletion to avoid stale path state, which is correct but can be expensive if many stale entries exist.

The scan thread uses small transactions and must exit cleanly on filesystem closing. Failure to set or clear the rescan semaphore would block future scans. `btrfs_uuid_tree_lookup()` warns on missing `uuid_root`, so callers must only use the add/remove API after UUID tree creation or with filesystems that have the tree available.

## Test Signals

Useful tests include subvolume create/delete, snapshot, send/receive, setting received UUID, UUID collision and duplicate-subid scenarios, leaf-overflow preflight, mount-time UUID tree creation/rescan, stale-entry cleanup after deleted roots, and forced close during rescan. Corruption tests should cover misaligned UUID item sizes and missing referenced roots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/uuid-tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/uuid-tree.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/uuid-tree.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/uuid-tree.h` declares the public interface for Btrfs UUID tree maintenance. The file was read as a complete 21-line header for this report.

## Important APIs, Types, and Functions

The header forward declares `struct btrfs_trans_handle` and `struct btrfs_fs_info`, then exports add/remove, overflow-check, iteration, tree creation, and scan-thread functions: `btrfs_uuid_tree_add()`, `btrfs_uuid_tree_remove()`, `btrfs_uuid_tree_check_overflow()`, `btrfs_uuid_tree_iterate()`, `btrfs_create_uuid_tree()`, and `btrfs_uuid_scan_kthread()`.

## Control Flow

There is no executable control flow in the header. It separates transaction-bound update calls from filesystem-wide scan/create calls so callers can either mutate mappings inside an existing transaction or trigger maintenance over the entire UUID tree.

## State and Persistence Behavior

The header exposes persistent metadata operations but no state layout. The implementation stores UUID mappings in the on-disk UUID tree and uses `fs_info->uuid_root` as the runtime root pointer.

## Dependencies and Integration Points

Consumers are Btrfs transaction, ioctl, inode, and disk-io paths that create roots, change received UUIDs, exchange roots, validate UUID tree entries, and build the UUID tree when needed. The header includes only kernel types and relies on forward declarations for low include cost.

## Risks and Edge Cases

Callers must supply a valid transaction for add/remove and must ensure the UUID tree exists before using the update APIs. Overflow checks are advisory and must be paired with the same UUID/type that will be appended. `btrfs_uuid_scan_kthread()` is exported for kthread startup but still expects a `btrfs_fs_info *` data argument.

## Test Signals

Compile coverage should catch API drift across transaction/ioctl/inode/disk-io users. Runtime coverage should verify add/remove behavior in existing transactions and UUID tree creation plus asynchronous scan startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/uuid-tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/verity.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/verity.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/verity.c` implements Btrfs support for the generic fs-verity operations. It stores fs-verity descriptors and Merkle tree bytes as dedicated Btrfs btree items in the file's filesystem tree while caching Merkle pages in the inode mapping at synthetic offsets past EOF. The file was read as a complete 800-line source file for this report.

## Important APIs, Types, and Functions

The public exported symbols are `btrfs_drop_verity_items()`, `btrfs_get_verity_descriptor()`, and `btrfs_verityops`. Private helpers include `merkle_file_pos()`, `drop_verity_items()`, `write_key_bytes()`, `read_key_bytes()`, `del_orphan()`, `rollback_verity()`, `finish_verity()`, `btrfs_begin_enable_verity()`, `btrfs_end_enable_verity()`, `btrfs_read_merkle_tree_page()`, and `btrfs_write_merkle_tree_block()`.

On disk, descriptor metadata uses `BTRFS_VERITY_DESC_ITEM_KEY`: offset 0 stores `struct btrfs_verity_descriptor_item`, and offsets starting at 1 store the opaque fs-verity descriptor bytes. Merkle tree bytes use `BTRFS_VERITY_MERKLE_ITEM_KEY` with byte offsets starting at 0.

## Control Flow

Enabling verity begins with `btrfs_begin_enable_verity()`, called through fs-verity. It requires the inode lock, rejects encrypted inodes, rejects concurrent enable attempts via `BTRFS_INODE_VERITY_IN_PROGRESS`, drops any stale verity items, starts a transaction, adds an orphan item, and sets the in-progress runtime flag.

While fs-verity builds the Merkle tree, `btrfs_write_merkle_tree_block()` writes each block to `BTRFS_VERITY_MERKLE_ITEM_KEY` items through `write_key_bytes()`, which chunks data into up to 2 KiB btree items and uses a small transaction per item. At the end, `btrfs_end_enable_verity()` either rolls back on a NULL descriptor/error path or calls `finish_verity()`. Finish writes the descriptor header and descriptor blob, marks the inode `BTRFS_INODE_RO_VERITY`, syncs inode flags, updates the inode, deletes the verity orphan, clears the in-progress bit, and sets the filesystem read-only compatible verity bit.

Reading uses `btrfs_get_verity_descriptor()` as a two-pass descriptor API: size query when `buf_size == 0`, then exact descriptor read. Merkle reads use `btrfs_read_merkle_tree_page()`, which computes the synthetic cache index past EOF, looks up or allocates a folio in the file mapping, reads one page of Merkle bytes from btree items via `read_key_bytes()`, zero-fills short reads, marks the folio uptodate, and returns the page to fs-verity.

Rollback clears cached pages past EOF, clears in-progress, drops descriptor and Merkle items, clears the inode verity ro flag, updates the inode, and deletes the orphan. `btrfs_drop_verity_items()` is also used by inode orphan cleanup paths for interrupted enables.

## State and Persistence Behavior

Persistent state lives in filesystem-tree items keyed by inode objectid plus descriptor or Merkle key type. Verity completion also persists the inode ro flag and the filesystem compat-ro verity feature bit. The orphan item is persistent crash-recovery state for an in-progress enable; it lets Btrfs identify and clean partial verity metadata if enable fails or is interrupted.

Runtime state includes `BTRFS_INODE_VERITY_IN_PROGRESS`, page-cache folios at synthetic post-EOF offsets, inode `i_flags` synchronized from Btrfs ro flags, and fs-verity's calls through `struct fsverity_operations`. `merkle_file_pos()` rounds `i_size` up to 64 KiB so cached Merkle pages are beyond the last possible data page even with 64 KiB pages and checks `s_maxbytes` overflow.

## Dependencies and Integration Points

This file depends on the generic fs-verity API, Btrfs transactions, orphan handling, inode flag synchronization, btree item accessors, extent-buffer reads/writes, filemap/folio APIs, and superblock feature bits. `super.c` installs `btrfs_verityops` as `sb->s_vop`; `inode.c` invokes `btrfs_drop_verity_items()` during orphan cleanup; `accessors.h` provides descriptor item accessors; and Btrfs ioctl/inode paths rely on the inode verity flag state after completion.

## Risks and Edge Cases

Enable is a multi-transaction operation that can run out of space partway through a large Merkle tree. The orphan/in-progress protocol is the main protection against persistent partial state, so failures in rollback are escalated with filesystem errors. Encryption is explicitly unsupported because descriptor and Merkle items are stored as metadata rather than file data.

`read_key_bytes()` allows short reads; descriptor reads convert short descriptor blobs to `-EIO`, while Merkle page reads zero-fill missing tail bytes. Descriptor reserved fields and oversized descriptor sizes are treated as corruption (`-EUCLEAN`). Synthetic Merkle cache offsets must not overflow `s_maxbytes`, especially for large files. `write_key_bytes()` can leave earlier chunks written if a later insert fails, so callers must rely on rollback/drop paths.

## Test Signals

Useful tests include generic fs-verity enable/measure/read verification on Btrfs, enable failure injection during Merkle and descriptor writes, crash/orphan cleanup during in-progress enable, large-file Merkle offset overflow checks, descriptor size query/read mismatch, encrypted inode rejection, page-cache reuse of Merkle folios, and inode flag persistence across remount. Btrfs-specific tests should verify that partial verity items are dropped and that the compat-ro feature bit is set only after successful finish.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/verity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/verity.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/verity.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/verity.h` declares the Btrfs fs-verity integration points and provides disabled-configuration stubs. The file was read as a complete 35-line header for this report.

## Important APIs, Types, and Functions

When `CONFIG_FS_VERITY` is enabled, the header includes `<linux/fsverity.h>`, declares `extern const struct fsverity_operations btrfs_verityops`, and exposes `btrfs_drop_verity_items()` and `btrfs_get_verity_descriptor()`. When the option is disabled, it provides inline stubs: dropping verity items succeeds as a no-op and descriptor lookup returns `-EPERM`.

## Control Flow

There is no executable control flow beyond compile-time selection. Enabled builds route superblock fs-verity operations to `verity.c`; disabled builds let callers compile while making descriptor access fail and cleanup harmless.

## State and Persistence Behavior

The header owns no state. It gates access to persistent descriptor/Merkle items and runtime fs-verity operations based on kernel configuration.

## Dependencies and Integration Points

The header forward declares `struct inode` and `struct btrfs_inode`. It is included by Btrfs superblock setup and inode/orphan code that must either use real fs-verity support or compile cleanly without it.

## Risks and Edge Cases

Callers must handle `-EPERM` from the disabled stub and must not assume `btrfs_verityops` exists unless `CONFIG_FS_VERITY` is enabled. Cleanup paths can safely call `btrfs_drop_verity_items()` in both configurations, but only enabled builds remove actual on-disk verity metadata.

## Test Signals

Build coverage with `CONFIG_FS_VERITY=y` and disabled configurations should verify both branches. Runtime fs-verity tests apply only to enabled builds; disabled builds should reject descriptor operations cleanly while preserving normal Btrfs behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/verity.h -->
