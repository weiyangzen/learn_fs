# Group Research: group_1664_reactos_sources_windows_reactos_drivers_filesystems_btrfs_send_c_so_f57319fca458

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/send.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/send.c

## Role In The Filesystem

`send.c` implements the ReactOS/WinBtrfs Btrfs send-stream producer. It turns a read-only subvolume, optionally compared against a parent snapshot and clone sources, into Btrfs send commands that user mode reads through `read_send_buffer`. The file is in subset A because it sits directly inside the Windows Btrfs filesystem driver and bridges on-disk Btrfs metadata, snapshot differencing, data reads, compression handling, and kernel/user streaming.

The implementation is not a generic serializer alone. It owns the full send operation lifecycle: privilege validation, source/parent/clone validation, background system-thread creation, tree traversal, inode/ref/extent/xattr diffing, data emission, buffer backpressure, cancellation checks, and teardown.

## Main Data Structures

- `send_dir`: tracks known directory inodes, parent links, path names, timestamps, dummy/orphan state, and children already deleted during collision handling.
- `orphan`: tracks temporary orphan names for files or directories that must be created or moved before their final path is safe.
- `deleted_child`: remembers names deleted from a directory so later old refs are not redundantly unlinked.
- `ref`: normalized inode reference collected from `TYPE_INODE_REF` or `TYPE_INODE_EXTREF`, pointing to a `send_dir` plus a name.
- `pending_rmdir`: queues directory removals that must wait until higher-numbered child inodes have been processed.
- `send_ext`: buffered extent metadata copied from `TYPE_EXTENT_DATA` items for later comparison and write/clone emission.
- `send_context`: operation state shared by the producer thread and reader, including root/parent/clone roots, send buffer, directory/orphan lists, pending removals, current inode state, and synchronization objects.

`send_context.lastinode` is the central per-inode accumulator. It tracks whether the current inode is new, deleting, a file, its metadata, old metadata, final path/orphan state, refs/oldrefs, and extents/oldextents.

## Send Command Encoding

The low-level command helpers are:

- `send_command`: reserves and initializes a `btrfs_send_command`.
- `send_command_finish`: fills command length and CRC32C checksum over the command record.
- `send_add_tlv`: appends typed TLV payloads.
- `send_add_tlv_path`: computes a full path from `send_dir` parent links and appends it as a TLV.

Commands emitted include subvolume/snapshot headers, object creation, rename, link, unlink, rmdir, clone, write, truncate, chmod, chown, utimes, set xattr, and remove xattr.

The buffer model uses:

- `MAX_SEND_WRITE = 0xc000`, limiting individual data writes to 48 KiB.
- `SEND_BUFFER_LENGTH = 0x100000`, a 1 MiB producer buffer threshold.
- Extra allocation wiggle room of `SEND_BUFFER_LENGTH + 2 * MAX_SEND_WRITE`.

## Path And Orphan Handling

The send stream must produce valid operations even when Btrfs item order does not match path dependency order. This file handles that with temporary orphan names and dummy directories.

Important helpers:

- `uint64_to_char`: decimal integer formatting for temporary names.
- `get_orphan_name`: creates names like `o<inode>-<generation>-<index>` and probes both current and parent roots to avoid collisions in the subvolume root.
- `add_orphan`: keeps the orphan list sorted by inode.
- `find_send_dir`: resolves or creates `send_dir` objects; when only parent snapshot information is available it may create dummy directories.
- `found_path`: either renames an orphan into its final path or links an additional hardlink to the current inode.

For new inodes, `send_inode` often creates the object first under a temporary orphan name, then later `flush_refs` moves it to the final path once references are known. This allows stream order to remain valid under renames, collisions, hardlinks, and directories whose parents appear later.

## Inode Processing

`send_inode` handles `TYPE_INODE_ITEM` differences and initializes `lastinode`.

Cases include:

- Deleted inode: records old generation, mode, and flags from parent.
- Existing/new inode: records uid, gid, mode, size, timestamps, flags, file classification, and previous metadata if available.
- Subvolume root inode: initializes `root_dir`.
- New non-root inode: emits a creation command under an orphan name:
  - `BTRFS_SEND_CMD_MKSOCK`
  - `BTRFS_SEND_CMD_SYMLINK`
  - `BTRFS_SEND_CMD_MKNOD`
  - `BTRFS_SEND_CMD_MKDIR`
  - `BTRFS_SEND_CMD_MKFIFO`
  - `BTRFS_SEND_CMD_MKFILE`

Symlinks are read via `send_read_symlink`, which expects inline extent data and returns an empty target if symlink data is not inline.

`finish_inode` flushes pending refs and extents, emits truncate/chown/chmod/utimes as needed, handles pending rmdirs, frees per-inode lists, and resets `lastinode`.

## Reference Diffing

`send_inode_ref` and `send_inode_extref` normalize both classic inode refs and extended refs into `ref` entries. They also create dummy/orphan directories when the referenced parent directory has not yet appeared in traversal order.

`flush_refs` is one of the most important routines in the file. It compares current refs against old refs and decides whether to:

- Rename an orphan to a final path.
- Emit hardlink commands.
- Emit rename commands for moved/renamed directories.
- Emit unlink commands for removed refs.
- Emit rmdir commands immediately or queue them in `pending_rmdirs`.
- Move colliding paths out of the way using `make_file_orphan`.

Directory handling is special because directory removes must respect child ordering. The file queries the old parent tree with `get_dir_last_child`, then either removes immediately or queues a `pending_rmdir` keyed by last child inode.

## Extent Diffing And Data Emission

`send_extent_data` collects current and parent extent records for regular files, validating:

- Minimum item sizes.
- No unsupported encryption.
- No unsupported encoding.
- Compression type is none, zlib, LZO, or Zstd.
- Regular extents include `EXTENT_DATA2`.
- Inline extents are large enough for decoded data when uncompressed.

`flush_extents` turns accumulated extents into write or clone commands.

For parent-differential sends:

- `add_ext_holes` inserts synthetic sparse-hole extents so current and old extent lists cover comparable ranges.
- `sync_ext_cutoff_points` splits extents with `divide_ext` so current and old extent boundaries align.
- Unchanged inline or regular extents are skipped.

For changed data:

- Inline uncompressed extents are written directly.
- Inline compressed extents are decompressed before writing.
- Sparse extents emit zero-filled writes.
- Regular uncompressed extents are read from disk in 48 KiB chunks, with checksum loading unless `BTRFS_INODE_NODATASUM` is set.
- Regular compressed extents are read, decompressed into memory, and emitted in 48 KiB writes.

Clone optimization is attempted before raw writes:

- `try_clone` inspects extent backrefs in the extent tree.
- `try_clone_edr` matches backrefs against the parent or supplied clone roots.
- `send_add_tlv_clone_path` reconstructs the source inode path inside the clone root.
- A clone command is emitted only when offsets and lengths meet sector alignment constraints.

## Xattr Diffing

`send_xattr` emits xattr operations for `TYPE_XATTR_ITEM`.

Cases:

- Current only: emit `BTRFS_SEND_CMD_SET_XATTR` for each packed `DIR_ITEM`.
- Parent only: emit `BTRFS_SEND_CMD_REMOVE_XATTR`.
- Both: build an `xattr_cmp` list, match names, compare values, then emit set/remove operations only for differences.

The xattr parser carefully walks packed `DIR_ITEM` records and validates each record length before use.

## Traversal And Snapshot Differencing

`send_thread` performs the actual send generation.

Initial setup:

- Increments `send_ops` counters on root, parent, and clone roots.
- Acquires the tree lock exclusively.
- Flushes subvolume FCBs.
- Forces pending writes through `do_write` if needed.
- Frees cached trees.
- Converts the tree lock to shared mode for traversal.

Without a parent snapshot, it walks the root tree in key order and processes relevant item types.

With a parent snapshot, it walks both trees in sorted key order:

- Uses `skip_to_difference` to skip shared tree blocks by address.
- Handles equal keys as modified/same items.
- Handles keys only in the current root as additions.
- Handles keys only in the parent root as deletions.
- Finishes an inode whenever traversal moves to a higher object id.

Relevant item types:

- `TYPE_INODE_ITEM`
- `TYPE_INODE_REF`
- `TYPE_INODE_EXTREF`
- `TYPE_EXTENT_DATA`
- `TYPE_XATTR_ITEM`

A special inode-item generation comparison detects replacement of an inode with the same object id but different generation, treating the old inode as deleted before creating the new one.

## Buffering, Synchronization, And Cancellation

The producer thread and user reader coordinate with two events:

- `context->buffer_event`: producer signals data is available.
- `send->cleared_event`: reader signals buffer space has been consumed.

`wait_for_flush` releases the tree lock while waiting for the reader, then reacquires it and re-finds traversal keys. It verifies that readonly subvolumes did not change by checking the key found after reacquisition.

Cancellation is checked after buffer waits and major flush operations through `send->cancelling`.

`read_send_buffer`:

- Validates the caller and `SE_MANAGE_VOLUME_PRIVILEGE`.
- Waits for `buffer_event`.
- Copies up to caller buffer length.
- Slides remaining data down if partially consumed.
- Clears the producer buffer and signals `cleared_event` when fully consumed.
- Returns `STATUS_END_OF_FILE` after the send completes successfully, or the stored send status on failure.

## Public Entry Points

`send_subvol` starts a send operation. It validates:

- File object and FCB/CCB presence.
- Caller has `SE_MANAGE_VOLUME_PRIVILEGE`.
- Target is a subvolume root and not the filesystem root.
- Target is readonly unless the mounted Vcb is readonly.
- Optional parent handle is a different readonly subvolume on the same device.
- Optional clone handles are readonly subvolume roots on the same device.
- No send is already active on the CCB.

It allocates `send_context`, send buffer, `send_info`, initializes lists/events, emits the subvolume/snapshot header, creates the kernel send thread, registers it in `Vcb->send_ops`, and returns.

`read_send_buffer` is the paired read side described above.

## Error Handling And Cleanup

The file consistently returns NTSTATUS values and logs with `ERR`, `WARN`, and `TRACE`. Common failures include allocation failure, malformed Btrfs items, unsupported compression/encryption/encoding, failed tree lookups, read/checksum failures, invalid handles, privilege failures, and readonly subvolume mutation detection.

The `send_thread` `end:` path releases kernel resources:

- Orphan list.
- Directory list and deleted child names.
- Thread handle.
- CCB send pointer.
- Send operation list entry.
- Send buffer.
- Clone array.
- Send counters.
- Context object.

One notable cleanup limitation: several mid-setup error paths in `send_subvol` free `context` and `data` but must be read carefully around clone allocation. Most clone validation failures free `clones`; the send buffer allocation failure path frees `context` but does not free `clones` if clone handles were accepted earlier, which is a potential leak candidate worth verifying against surrounding code revisions.

## Dependencies

This file depends heavily on Btrfs driver infrastructure from `btrfs_drv.h` and related modules:

- Tree lookup and traversal: `find_item`, `find_next_item`, `skip_to_difference`.
- CRC32C: `calc_crc32c`.
- Data IO/checksums: `read_data`, `load_csum`.
- Compression: `zlib_decompress`, `lzo_decompress`, `zstd_decompress`.
- Extent metadata helpers: `get_extent_data_len`, `get_extent_data_refcount`.
- FCB/subvolume helpers: `flush_subvol_fcbs`, `do_write`, `free_trees`.
- Windows kernel primitives: pool allocation, resources, events, system threads, object handles, privilege checks.

## Risks And Review Notes

- The file is correctness-sensitive because send streams must be replayable and path operations must be topologically valid.
- Buffer flushing temporarily releases `tree_lock`; the key revalidation is essential and should remain covered by tests.
- Path length fields are `uint16_t`, matching send TLV limits, but callers should be aware of possible truncation or overflow if very deep paths exceed send-stream limits.
- Extent handling has many arithmetic paths involving decoded size, logical offsets, compressed sizes, and file size truncation; boundary tests matter.
- Clone path reconstruction follows one inode ref path, not necessarily all possible hardlink paths.
- Malformed metadata mostly returns internal errors rather than trying to recover.
- Compressed regular extents are fully decompressed into memory before chunked output, which can be memory-heavy for large decoded extents.
- There is a probable allocation cleanup issue if `context->data` allocation fails after `clones` has been allocated.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/send.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/sha256.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/sha256.c

## Role In The Filesystem

`sha256.c` provides a standalone SHA-256 implementation used by the Btrfs driver. It is public-domain code from `https://github.com/amosnier/sha-2`, adapted into the driver source tree. The file exports one hashing routine, `calc_sha256`, and contains no Windows-specific driver calls.

This belongs to subset A because Btrfs supports SHA-256 as a checksum algorithm in modern filesystem formats, and this file is part of the local Windows filesystem driver implementation.

## Main API

```c
void calc_sha256(uint8_t* hash, const void* input, size_t len)
```

Inputs:

- `hash`: caller-provided 32-byte output buffer.
- `input`: pointer to bytes in RAM.
- `len`: input length in bytes.

Output:

- Writes the SHA-256 digest in big-endian byte order.

The routine assumes the full input is already resident in memory. It does not stream from disk or maintain reusable hash state across calls.

## Internal Constants And State

Constants:

- `CHUNK_SIZE = 64`: SHA-256 operates on 512-bit blocks.
- `TOTAL_LEN_LEN = 8`: SHA-256 padding appends a 64-bit bit-length.
- `k[]`: the standard 64 SHA-256 round constants.

`struct buffer_state` tracks chunk production:

- `p`: current input pointer.
- `len`: remaining input bytes.
- `total_len`: original input length.
- `single_one_delivered`: whether the `0x80` padding byte has been emitted.
- `total_len_delivered`: whether final length bytes have been emitted.

The file intentionally avoids `bool` for older C compatibility.

## Chunk And Padding Flow

`init_buf_state` initializes the chunk iterator.

`calc_chunk` fills one 64-byte chunk at a time:

1. If at least 64 input bytes remain, it copies a raw chunk.
2. Otherwise it copies remaining input bytes.
3. It appends the single `0x80` bit byte if not already emitted.
4. If there is enough room, it zero-pads and writes the 64-bit big-endian bit length.
5. If not enough room remains, it zero-pads the current chunk and emits the length in a later chunk.

The bit length is calculated from `size_t total_len` and stored as `len * 8` in big-endian form. The comments explicitly note that non-byte-aligned bit strings are unsupported.

## Compression Function

`calc_sha256` implements standard SHA-256:

- Initializes hash words to the standard initial constants.
- For each chunk, initializes working variables `a..h`.
- Processes 64 rounds.
- Uses a 16-word circular message schedule instead of a 64-word array to reduce stack usage.
- Adds working variables back into the hash state.
- Emits the final digest as eight big-endian 32-bit words.

`right_rot` performs 32-bit rotate-right and is only used with nonzero counts below 32, preserving defined C behavior.

## Dependencies

The file only includes:

- `<stdint.h>`
- `<string.h>`

It uses standard integer types and `memcpy`/`memset`. It does not depend on `btrfs_drv.h`, pool allocation, locks, or kernel APIs.

## Limitations And Review Notes

- The implementation is RAM-only; it cannot incrementally hash large disk-backed data without the caller buffering it.
- The length parameter is bytes, not bits; arbitrary bit-length messages are unsupported.
- The length encoding is based on `size_t`, so practical maximum input length is platform-dependent and not a full abstract 2^64-bit message length interface.
- There is a FIXME noting possible future use of x86 SHA extensions.
- The function has no explicit null pointer checks; callers must provide valid buffers.
- The code is compact and easy to compare against SHA-256 test vectors. Basic tests should cover empty input, `"abc"`, one-block boundary inputs, and multi-block inputs.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/sha256.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/treefuncs.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/treefuncs.c

## Role In The Filesystem

`treefuncs.c` implements core in-memory Btrfs tree operations for the ReactOS/WinBtrfs driver. It loads B-tree nodes from disk, caches them, traverses sorted items, inserts and deletes logical tree items, manages rollback state, and commits batched metadata updates.

This is foundational driver code. Higher-level modules such as send, read/write, extent management, directory handling, and filesystem control rely on these routines to navigate and mutate Btrfs roots safely under the driver tree lock.

## Tree Loading And Cache Registration

`load_tree` converts a raw node buffer into an in-memory `tree` object.

For leaf nodes:

- Validates the item array fits inside the configured node size.
- Allocates one `tree_data` per `leaf_node`.
- Stores item key, size, and a pointer into the raw buffer for item data.
- Tracks aggregate tree payload size.
- Keeps the raw buffer as `t->buf`.

For internal nodes:

- Validates the internal item array fits.
- Allocates one `tree_data` per `internal_node`.
- Stores child address and generation in `treeholder`.
- Does not keep a leaf data buffer.

For both:

- Copies the tree header.
- Initializes parent/root/paritem pointers.
- Initializes write/new-address/extent-update flags.
- Adds the tree to `Vcb->trees`.
- Adds it to `Vcb->trees_hash`, using `trees_ptrs` buckets based on the high byte of a CRC32C hash of the tree address.

`do_load_tree` allocates a node-sized buffer, reads the tree block with `read_data`, serializes child load through either the parent tree mutex or root load lock, then delegates to `do_load_tree2`.

`do_load_tree2` avoids duplicate loads by checking `tree_holder->tree` before calling `load_tree`.

## Tree Freeing

`free_tree` releases one tree:

- Clears the parent item’s `treeholder.tree`.
- Frees inserted leaf item data.
- Returns `tree_data` entries to the lookaside list.
- Removes the tree from global tree lists and hash buckets.
- Clears the root holder if this is the root tree.
- Frees the raw leaf buffer and nonpaged mutex state.

`free_trees_root` frees all cached trees for a specific root level-by-level from leaves upward.

`free_trees` frees all cached trees, then reaps file references and FCBs.

The level-by-level strategy matters because parent/child pointers and root holders must not be left pointing into freed children.

## Traversal Helpers

Local helpers:

- `first_item`
- `last_item`
- `prev_item`
- `next_item`

Public traversal:

- `find_item`
- `find_item_to_level`
- `find_next_item`
- `find_prev_item`
- `skip_to_difference`

`find_item_in_tree` performs the core search. It walks sorted `tree_data` entries, descends through internal nodes as needed, lazy-loads child trees, and respects ignored/deleted items unless the caller asks to include them.

Important behavior:

- If an exact leaf item is ignored and ignored items should be hidden, the function searches backward for a visible predecessor, then forward for a visible successor.
- `find_item_to_level` can stop at an internal level instead of descending to leaves.
- If `find_item_to_level` returns `STATUS_NOT_FOUND`, it still initializes `tp->tree` to the root tree and `tp->item` to `NULL`.

`find_next_item` moves forward in key order across leaves, loading right-hand child paths as needed. It can skip ignored items.

`find_prev_item` moves backward in key order. A FIXME notes it does not support an ignore flag.

`skip_to_difference` is optimized for snapshot comparison. Given traverse pointers in two roots, it climbs until the shared tree address diverges, then advances to the next differing leaf item. This lets send-style code skip whole shared B-tree subtrees.

## Single-Item Insert And Delete

`insert_tree_item` inserts one leaf item into a root:

- Looks up the target key with ignored items visible.
- Handles insertion into an empty tree.
- Rejects an already-present non-ignored item.
- Allocates a `tree_data` entry from the lookaside list.
- Inserts before/after the found item based on key comparison.
- Places a replacement before ignored duplicates so live entries sort before deleted versions.
- Updates `num_items`, tree size, write flags, `Vcb->need_write`, and generations up the parent chain.
- Revives ignored parent items if insertion makes a previously hidden subtree visible.

`delete_tree_item` marks an item ignored rather than immediately unlinking it:

- Sets `item->ignore`.
- Marks tree and Vcb dirty.
- Decrements `num_items`.
- Subtracts item size from aggregate tree size.
- Updates generations up the parent chain.

This lazy-delete model lets later insertion/collision code reason about old and new versions before final writeout.

## Rollback Support

`add_rollback` appends rollback records to a caller-owned list.

`clear_rollback` frees rollback records without applying them. It frees payloads for extent and space rollback types.

`do_rollback` applies rollback records in reverse order. Supported rollback types include:

- Inserted extent: mark ignored, update changed extent refs, subtract inode blocks.
- Deleted extent: unignore, update changed extent refs, add inode blocks.
- Added/subtracted free space: reverse space-list mutation and update chunk usage.

For chunk space rollback, the routine acquires the chunk lock, applies the current rollback, then coalesces and applies earlier rollback records for the same chunk before releasing the lock. This avoids repeated lock cycling and preserves chunk accounting consistency.

## Batch List Structure

Batched metadata changes are grouped by root:

- `batch_root` owns one root and indexed sublists.
- `batch_item_ind` contains a list of `batch_item`s.
- `clear_batch_list` frees all batch roots, sublists, and batch items.

`commit_batch_list` drains batch roots and calls `commit_batch_list_root`.

`commit_batch_list_root` flattens the indexed sublists into one sorted `items` list, then applies items to the in-memory tree.

Batch operations include:

- Generic insert/delete.
- Delete whole inode.
- Delete all extent data for an inode.
- Delete free-space ranges.
- Directory item insert/delete.
- Xattr set/delete.
- Inode ref insert/delete.
- Extended inode ref insert/delete.

## Collision Handling For Packed Items

`handle_batch_collision` resolves batch operations whose key already exists.

Packed Btrfs items may store multiple logical records under one key, so collision does not always mean failure. This function handles:

- `Batch_SetXattr`: replace existing xattr by name or append it.
- `Batch_DirItem`: append a packed directory item.
- `Batch_InodeRef`: append a packed inode ref, or convert to `INODE_EXTREF` if it would exceed max item size and extended refs are enabled.
- `Batch_InodeExtRef`: append an extended inode ref.
- `Batch_DeleteDirItem`: remove one packed dir item, possibly replacing the item with a shorter inserted copy.
- `Batch_DeleteInodeRef`: remove one packed inode ref; if absent and extended refs are enabled, enqueue a matching extended-ref delete.
- `Batch_DeleteInodeExtRef`: remove one packed extended inode ref.
- `Batch_DeleteXattr`: remove one packed xattr by name.
- `Batch_Delete`: mark existing item deleted.

When an existing packed item is modified but not fully deleted, the function allocates a new shorter or longer data buffer, creates a replacement `tree_data`, marks the old item ignored, and updates tree item counts/sizes.

`add_delete_inode_extref` is a helper for the compatibility path where a requested inode-ref delete must be represented as an extended-ref delete.

## Batch Commit Flow

Inside `commit_batch_list_root`:

1. Find the tree position for the current batch key.
2. Determine the end key for the current leaf range with `find_tree_end`.
3. Handle range-delete operations specially:
   - `Batch_DeleteInode` marks all items with the target object id ignored.
   - `Batch_DeleteExtentData` marks all extent data items for an inode ignored.
   - `Batch_DeleteFreeSpace` marks free-space keys in a range ignored.
4. For normal operations, allocate a new `tree_data` unless it is a delete-only operation.
5. Insert into the current tree or call `handle_batch_collision`.
6. Consume subsequent batch items that fit before the current tree end key, applying them in-place without repeated root searches.
7. Update parent generations and revive ignored parent items.
8. Free consumed batch items at the end.

This design amortizes tree searches by applying adjacent sorted operations to the same loaded leaf when possible.

## Locking And Concurrency Assumptions

Many public functions are annotated or named for use under `Vcb->tree_lock`.

- `find_item` and traversal functions require the tree lock held.
- Insert, delete, and batch commit require the tree lock held exclusively.
- Tree load uses per-tree fast mutexes or root load locks to prevent duplicate child loads.
- Global tree cache insertion/removal uses `Vcb->trees_list_mutex`.
- Rollback space operations acquire chunk locks when updating per-chunk free-space accounting.

The file assumes callers obey lock ownership. It does not generally try to make tree mutation safe without the exclusive tree lock.

## Error Handling

The file returns `NTSTATUS` for operations that can fail and uses boolean returns for traversal convenience.

Common failures:

- Pool allocation failure.
- Invalid or oversized node item arrays.
- Overlarge item payloads.
- Read failure from disk.
- Unexpected duplicate key.
- Unsupported packed-item growth beyond node item limits.
- Malformed/truncated packed records.
- Missing tree paths.

The code logs errors but often leaves deeper recovery to the caller. Batch commit failures can occur after some in-memory mutations, which is why rollback support in surrounding write paths is important.

## Dependencies

Key dependencies from the wider driver:

- `btrfs_drv.h` for tree/root/item structures, batch operation enums, rollback structures, Btrfs item structs, locks, and helper prototypes.
- `crc32c.h` for tree address hash bucketing and extended ref key hashing.
- `read_data` for loading tree blocks.
- `keycmp` for Btrfs key ordering.
- `update_changed_extent_ref`, `get_chunk_from_address`, `space_list_add2`, `space_list_subtract2`, chunk locks, and inode/extent accounting helpers.
- Windows kernel allocation, lookaside lists, fast mutexes, resources, and list primitives.

## Risks And Review Notes

- Tree item data for loaded leaves points into the raw tree buffer; inserted or replacement item data has separate ownership. Correct use of `td->inserted` is critical for freeing.
- Lazy deletion through `ignore` makes traversal semantics subtle. Callers must choose ignore behavior intentionally.
- `find_prev_item` explicitly lacks ignore handling, which can matter for callers expecting visible-only reverse traversal.
- Several packed-item delete paths assume record walking remains within validated lengths; they mostly validate but should be fuzz-tested with malformed metadata.
- Batch collision logic performs many manual buffer reallocations and size recalculations; off-by-one errors here can corrupt tree state.
- The `Batch_InodeRef` overflow conversion to extended refs depends on incompat flags and sorted insertion into the remaining batch list.
- Batch commit applies multiple mutations before freeing the batch list; error paths should be reviewed together with caller rollback guarantees.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/treefuncs.c -->