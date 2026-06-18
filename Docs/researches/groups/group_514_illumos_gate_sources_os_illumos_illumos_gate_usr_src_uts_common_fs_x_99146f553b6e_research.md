# Group Research: group_514_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_x_99146f553b6e

Scope: `Docs/research_subset_a.md`, specifically the listed files under `sources/os/illumos/illumos-gate`. Each source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/xattr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/xattr.c

## Scope

Implements the illumos generic extended-attribute/system-attribute vnode layer. The file provides GFS-backed synthetic XATTR directories and synthetic system-attribute files, while passing through ordinary extended-attribute operations to an underlying filesystem-provided XATTR directory when present.

Read completely: 1,758 lines.

## Core Model

Solaris/illumos exposes extended attributes as a special directory reached with `LOOKUP_XATTR`. This module handles the cases where system attributes are enabled, with or without real filesystem extended attributes:

- SYSATTR + XATTR: creates a translucent GFS directory that merges synthetic system attribute entries with entries from the real filesystem XATTR directory.
- SYSATTR only: creates a GFS-only directory containing system attribute view files.
- XATTR only: returns the underlying filesystem XATTR directory directly.
- Neither: returns `EINVAL`.

The synthetic directory contains two static entries:

- `VIEW_READONLY`, created by `xattr_mkfile_ro()`
- `VIEW_READWRITE`, created by `xattr_mkfile_rw()`

Each synthetic file stores an `xattr_view_t` and presents an XDR-encoded nvlist of selected file attributes.

## Main Entry Points

- `xattr_init()` builds vnode operation vectors for the synthetic xattr directory and system-attribute files.
- `xattr_dir_lookup()` is the public lookup path used by VFS lookup with `LOOKUP_XATTR`; it creates, races, or reuses `dvp->v_xattrdir`.
- `xattr_dir_vget()` reconstructs a synthetic xattr directory or sysattr file from an `xattr_fid_t`.
- `xattr_mkfile()`, `xattr_mkfile_ro()`, and `xattr_mkfile_rw()` create synthetic sysattr view vnodes.
- `xattr_sysattr_casechk()` detects case-insensitive name conflicts between real xattrs and reserved sysattr names.

## System Attribute File Operations

The `xattr_file_tops` vnode operations implement synthetic regular files:

- `xattr_file_open()` and `xattr_file_access()` reject writes to readonly views.
- `xattr_file_close()` clears locks and shares.
- `xattr_file_getattr()` fabricates regular-file attributes, copies ctime/mtime from the parent xattr directory, and computes file size by packing the nvlist.
- `xattr_file_read()` builds an nvlist using `xattr_fill_nvlist()`, packs it as XDR, and moves it to userspace.
- `xattr_file_write()` unpacks an XDR nvlist and applies mutable attributes through `VOP_SETATTR()` on the real parent object.
- `xattr_common_fid()` builds a fid from the real parent fid plus a synthetic directory/file offset.
- `xattr_file_pathconf()` reports no nested xattrs or sysattrs for the synthetic files.

`xattr_fill_nvlist()` maps illumos `f_attr_t` names to `xvattr_t` requests, obtains attributes from the real parent object, and emits nvlist entries. It handles boolean optional attributes, create time, generation, fsid, antivirus scanstamp, reparse/offline/sparse flags, and ephemeral owner/group SIDs via kidmap.

`xattr_file_write()` validates nvpair names, types, view mutability, and VFS support for ephemeral IDs before setting `xvattr_t` fields. It accepts boolean values, uint64 arrays, uint8 arrays, and nested SID nvlists.

## Directory Operations

The `xattr_dir_tops` vnode operations implement the synthetic/translucent directory:

- `xattr_dir_realdir()` lazily looks up and caches the underlying real XATTR directory, retaining its hold until inactive.
- `xattr_dir_open()` and `xattr_dir_close()` reject write-open and pass open/close to the real xattr directory if it exists.
- `xattr_dir_getattr()` uses real xattr directory attributes when available; otherwise fabricates a sticky world-writable directory and copies selected parent attributes.
- `xattr_dir_setattr()` forwards setattr to the real xattr directory when present; transient GFS-only setattr changes are ignored.
- `xattr_dir_access()` rejects write access to the synthetic directory and otherwise delegates to the real xattr directory when present.
- `xattr_dir_create()` forbids creating real xattrs with reserved sysattr names and can create the real xattr directory with `CREATE_XATTR_DIR`.
- `xattr_dir_remove()` forbids removing reserved sysattr entries and passes through real xattr removal.
- `xattr_dir_link()` rejects links from synthetic system-attribute files and passes other links to the real xattr directory.
- `xattr_dir_rename()` copies sysattrs when either endpoint is a reserved sysattr name; otherwise it renames in the real xattr directory.
- `xattr_dir_readdir()` emits static GFS sysattr entries first, then reads the real xattr directory if present.
- `xattr_dir_realvp()` exposes the cached real xattr directory.
- `xattr_dir_inactive()` releases the cached real xattr vnode and frees the GFS directory object.

`xattr_lookup_cb()` supports `gfs_vop_lookup()` by looking through the real xattr directory after static GFS entries are checked.

## State And Dependencies

Important local structures:

- `xattr_file_t`: `gfs_file_t` plus `xattr_view_t`.
- `xattr_dir_t`: `gfs_dir_t` plus cached `xattr_realvp`.

The implementation depends on VFS/vnode operations, GFS directory helpers, `xvattr_t` optional attributes, nvlist XDR packing, kidmap SID/ID mapping, pathname helpers, and vnode flags including `V_SYSATTR`, `V_XATTRDIR`, `VFS_XATTR`, `VFS_XID`, and `VFSFT_XVATTR`.

## Invariants And Risks

- Synthetic sysattr names are reserved. Real xattrs with exact reserved names are rejected, and case conflicts can be flagged in readdir.
- `LOOKUP_HAVE_SYSATTR_DIR` is critical in `xattr_dir_realdir()` to avoid recursive xattr lookup.
- Cached `xattr_realvp` lifetime is tied to the synthetic GFS directory and must be released only at inactive.
- The GFS xattr directory creation path handles races by destroying the loser vnode manually and using the existing `dvp->v_xattrdir`.
- Sysattr fid generation depends on parent fids plus stable synthetic offsets.
- `xattr_file_write()` has delicate nvlist cleanup paths; early returns after unpacking must free the nvlist to avoid leaks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/abd.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/abd.c

## Scope

Implements ZFS ARC Buffer Data, an abstraction over linear and scattered memory buffers used by ARC, ZIO, RAID-Z, and other consumers that need block-sized data without always requiring contiguous allocation.

Read completely: 1,177 lines.

## Core Model

An `abd_t` can be:

- Linear: one contiguous `zio_buf_alloc()` or `zio_data_buf_alloc()` buffer.
- Scattered: an array of fixed-size chunks from `abd_chunk_cache`.
- Offset/view ABD: a non-owning ABD that points into another ABD and increments the parent child refcount.
- External buffer wrapper: a non-owning linear ABD created from caller-provided memory.

Scattered ABDs reduce ARC memory fragmentation by allocating page-sized chunks rather than large contiguous buffers. Small allocations default to linear buffers based on `zfs_abd_scatter_min_size`.

## Main APIs

Lifecycle and allocation:

- `abd_init()` creates the ABD chunk cache and kstats.
- `abd_fini()` tears down kstats and the chunk cache.
- `abd_alloc()` allocates scattered by default unless disabled or below threshold.
- `abd_alloc_linear()` forces contiguous storage.
- `abd_alloc_for_io()` currently uses linear ABDs for block I/O.
- `abd_alloc_sametype()` matches another ABD’s storage style and metadata flag.
- `abd_free()` frees owning ABDs.
- `abd_get_offset()` and `abd_get_offset_size()` create non-owning views.
- `abd_get_from_buf()` wraps caller-owned memory.
- `abd_put()` releases non-owning ABD structures.

Ownership conversion:

- `abd_to_buf()` returns the raw buffer for linear ABDs.
- `abd_borrow_buf()` returns a raw buffer, allocating a temporary one for scattered ABDs.
- `abd_borrow_buf_copy()` copies scattered ABD content into the borrowed buffer.
- `abd_return_buf()` returns a borrowed buffer and asserts unchanged data for scattered ABDs.
- `abd_return_buf_copy()` copies modifications back before return.
- `abd_take_ownership_of_buf()` turns a non-owning linear ABD into an owning one.
- `abd_release_ownership_of_buf()` removes ownership and clears metadata tracking.

Iteration and data operations:

- `abd_iterate_func()` maps and walks one ABD over a range.
- `abd_iterate_func2()` walks two ABDs in equal-sized mapped segments.
- `abd_copy_to_buf_off()`, `abd_copy_from_buf_off()`, `abd_copy_off()`
- `abd_cmp_buf_off()`, `abd_cmp()`
- `abd_zero_off()`

RAID-Z helpers:

- `abd_raidz_gen_iterate()` maps parity ABDs and optional data ABD segments for generation callbacks.
- `abd_raidz_rec_iterate()` maps parity ABDs and reconstruction target ABDs for reconstruction callbacks.

## State And Tunables

- `zfs_abd_scatter_enabled`: toggles scatter allocation.
- `zfs_abd_scatter_min_size`: minimum size for scatter allocation.
- `zfs_abd_chunk_size`: fixed chunk size, default 4096; iteration asserts it has not changed for existing ABDs.
- `abd_stats`: kstats for struct bytes, scatter count/data/waste, and linear count/data.
- `abd_chunk_cache`: kmem cache for scatter chunks.

## Control Flow

`abd_alloc()` computes the required chunk count, allocates an `abd_t` sized for the chunk pointer array, allocates each chunk, sets ownership, initializes child refcounting, and updates kstats. `abd_free()` requires an owning root ABD and frees either the linear buffer or all scatter chunks.

Offset ABD construction copies chunk pointers for scattered parents and preserves a per-ABD offset into the first chunk. The parent’s child refcount is incremented for the viewed byte range, and `abd_put()` decrements it.

Iteration uses `struct abd_iter`, which tracks position, mapped address, and mapped length. Linear ABDs map as one remaining span; scattered ABDs map only the current chunk suffix. All copy, compare, zero, and RAID-Z operations build on this iterator.

## Dependencies

Depends on ZFS context allocation and assertions, ZIO buffer allocators, `zfs_refcount`, kstats, `kmem_cache`, `SPA_MAXBLOCKSIZE`, RAID-Z callback contracts, and kernel preemption guards around RAID-Z mapping loops.

## Invariants And Risks

- Only owning ABDs may be freed with `abd_free()`; non-owning ABDs must use `abd_put()`.
- Parent ABDs must outlive offset ABD children.
- Metadata accounting only applies when the ABD owns the underlying buffer.
- Borrowed buffers increment child refcounts and must be returned exactly once.
- `abd_return_buf()` asserts scattered borrowed buffers are unchanged; callers intending to modify must use the `_copy` variant.
- `zfs_abd_chunk_size` is effectively boot-time only for existing scattered ABDs; runtime changes panic through iterator assertions.
- RAID-Z iteration requires progressive, 512-byte-aligned mapped lengths except at valid terminal boundaries.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/abd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/aggsum.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/aggsum.c

## Scope

Implements aggregate-sum counters: fanned-out approximate counters optimized for very frequent updates and comparatively rare precise reads.

Read completely: 233 lines.

## Core Model

An `aggsum_t` has a global core with upper and lower bounds plus per-CPU buckets. Updates usually touch only the current CPU’s bucket. Buckets borrow capacity from the global bounds, allowing local deltas to be adjusted without taking the global lock on every operation.

## Main APIs

- `aggsum_init()` initializes bounds, global lock, bucket array, and per-bucket locks.
- `aggsum_fini()` destroys locks and frees buckets.
- `aggsum_lower_bound()` and `aggsum_upper_bound()` return approximate bounds without locking.
- `aggsum_add()` applies a signed delta to the current CPU bucket, borrowing more range if necessary.
- `aggsum_value()` flushes all buckets to return an exact value.
- `aggsum_compare()` compares the precise value to a target, flushing buckets only until the target is outside the bounds or equality is proven.

## Control Flow

`aggsum_add()` locks one bucket and applies the delta if it fits in the borrowed range. Otherwise it calls `aggsum_borrow()`, which takes the global lock and bucket lock, flushes current bucket state into global bounds, expands the bounds by `abs(delta * aggsum_borrow_multiplier)`, and records the borrowed capacity.

`aggsum_flush_bucket()` folds a bucket’s delta and borrowed range back into the global lower/upper bounds using atomic adds, because bound readers do not take the global lock.

## Dependencies

Uses illumos/ZFS mutexes, atomics, CPU sequence IDs, boot CPU count, kernel memory allocation, and assertion macros.

## Invariants And Risks

- Global bounds may be read locklessly, so updates to bounds use atomic operations.
- Exact reads are intentionally expensive because they flush every bucket.
- `aggsum_compare()` can be cheaper than `aggsum_value()` when bounds prove the comparison before all buckets are flushed.
- Best suited for write-heavy/read-light metrics; frequent exact reads defeat the design.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/aggsum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/blkptr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/blkptr.c

## Scope

Implements encoding and decoding for embedded-data ZFS block pointers, where small payloads are stored inside the `blkptr_t` rather than referenced by DVAs.

Read completely: 152 lines.

## Main APIs

- `encode_embedded_bp_compressed()` clears and initializes an embedded block pointer, records compression, byte order, logical size, physical size, and packs payload bytes into payload words.
- `decode_embedded_bp_compressed()` extracts the packed byte stream from an embedded block pointer.
- `decode_embedded_bp()` decodes and, if needed, decompresses an embedded payload into a caller-provided buffer.

## Control Flow

Encoding treats the payload as little-endian byte slots within selected 64-bit words of the block pointer. It skips non-payload words using `BPE_IS_PAYLOADWORD()`. Decoding reverses that process and optionally calls `zio_decompress_data_buf()` when compression is enabled.

## Dependencies

Uses block pointer bitfield macros from ZFS headers, embedded block pointer layout macros, ZIO compression constants, and the ZIO decompression helper.

## Invariants And Risks

- Compressed payload size must not exceed `BPE_PAYLOAD_SIZE`.
- Logical size must fit the caller buffer in `decode_embedded_bp()`, otherwise `ENOSPC` is returned.
- Compression metadata must be valid and within `ZIO_COMPRESS_FUNCTIONS`.
- Payload packing assumes byte-stream semantics independent of the block pointer’s byte order.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/blkptr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/bplist.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/bplist.c

## Scope

Implements a simple in-memory protected list of block pointers with append and destructive iteration.

Read completely: 77 lines.

## Main APIs

- `bplist_create()` initializes the mutex and list.
- `bplist_destroy()` destroys the list and mutex.
- `bplist_append()` allocates a list entry, copies a `blkptr_t`, and appends it under lock.
- `bplist_iterate()` repeatedly removes the head entry, invokes the caller callback, and frees the entry.

## Control Flow

Iteration removes entries while holding the list lock, drops the lock around the callback, then reacquires it for the next entry. This prevents callback work from blocking producers or other list operations longer than needed.

## State And Dependencies

Uses `bplist_t`, `bplist_entry_t`, illumos `list_t`, mutexes, `kmem_alloc/free`, block pointers, and callback type `bplist_itor_t`.

## Invariants And Risks

- `bplist_iterate()` is destructive: entries are removed and freed after callback invocation.
- The debug variable `bplist_iterate_last_removed` preserves the last removed entry address for callback debugging.
- Callback behavior must tolerate the entry being freed immediately after it returns.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/bplist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/bpobj.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/bpobj.c

## Scope

Implements persistent ZFS block-pointer objects, used to store block pointers and nested block-pointer subobjects with space accounting for deferred frees, deadlists, and related pool metadata.

Read completely: 617 lines.

## Main APIs

Allocation and lifetime:

- `bpobj_alloc_empty()` returns the pool-wide empty bpobj when the feature is enabled, creating and feature-activating it as needed.
- `bpobj_decr_empty()` decrements the empty-bpobj feature and frees the shared empty object when no longer active.
- `bpobj_alloc()` allocates a DMU object with bonus size based on pool version.
- `bpobj_free()` recursively frees subobjects, then frees the bpobj object.
- `bpobj_open()` validates object type and bonus type, holds the bonus buffer, initializes lock/state, and records feature-derived capabilities.
- `bpobj_close()` releases held buffers and destroys the lock.
- `bpobj_is_open()` and `bpobj_is_empty()` expose state checks.

Iteration:

- `bpobj_iterate()` iterates and removes entries.
- `bpobj_iterate_nofree()` iterates without removal.
- `bpobj_iterate_impl()` handles both modes and recursively descends subobjects.

Mutation:

- `bpobj_enqueue()` appends a block pointer and updates byte/compressed/uncompressed accounting.
- `bpobj_enqueue_subobj()` appends another bpobj as a subobject, drops empty subobjects, and may flatten one-block nested subobject arrays.

Accounting:

- `bpobj_space()` returns stored accounting when available, otherwise computes by scanning.
- `bpobj_space_range()` computes space for block births in `(mintxg, maxtxg]`.

## Control Flow

The object data area stores serialized block pointers. The bonus buffer stores `bpobj_phys_t` accounting and subobject metadata. `bpo_epb` is derived from the data block size.

`bpobj_iterate_impl()` walks block pointers in reverse index order. When freeing, it dirties the bonus buffer, subtracts block accounting, decrements the block count, and later frees the processed DMU range. If subobjects exist, it opens each recursively, optionally accounts before/after space, frees empty processed subobjects, decrements subobject count, and frees processed subobject-array ranges.

`bpobj_enqueue()` stores a compressed-friendly copy of the block pointer: embedded payloads are stripped while preserving relevant fields, non-dedup checksums are cleared, and fill count is dropped. It uses a cached data buffer for append locality.

`bpobj_enqueue_subobj()` avoids storing the shared empty bpobj, discards empty subobjects, and flattens sub-subobjects when their subobject array occupies a single block.

## Dependencies

Depends on DMU object allocation, bonus buffers, `dmu_buf_hold/rele`, `dmu_write`, `dmu_free_range`, `dmu_object_info/free`, ZAP pool-directory entries, SPA feature activation, block pointer size/accounting macros, pool version gates, and `dsl_pool_sync_context()`.

## Invariants And Risks

- The shared empty bpobj must not be modified or freed through ordinary bpobj paths.
- `bpobj_free()` assumes recursive subobject cleanup before freeing the parent object.
- When freeing entries, bytes/compressed/uncompressed counters must track every removed block pointer and subobject delta.
- Old pool versions may lack compressed/uncompressed accounting, forcing scan-based `bpobj_space()`.
- Reverse iteration and cached dbuf offsets assume append-only object layout.
- The stored bp may intentionally differ from the input bp to improve compression; accounting still uses the original bp.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/bpobj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/bptree.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/bptree.c

## Scope

Implements ZFS bptrees: persistent queues of root block pointers for destroyed datasets whose block trees are freed asynchronously by sync-time scanning.

Read completely: 302 lines.

## Core Model

A bptree object stores `bptree_entry_phys_t` records in object data and `bptree_phys_t` queue/accounting state in the bonus buffer. `bt_begin` and `bt_end` form a monotonically increasing queue window and reset only when the object is destroyed and recreated.

## Main APIs

- `bptree_alloc()` allocates and initializes a bptree object.
- `bptree_free()` asserts the queue and accounting are empty, then frees the object.
- `bptree_is_empty()` checks `bt_begin == bt_end`.
- `bptree_add()` appends a destroyed dataset root block pointer plus birth txg and space accounting.
- `bptree_iterate()` traverses queued destroyed dataset trees, optionally freeing blocks and recording progress.

## Control Flow

`bptree_add()` runs only in syncing context, writes a new entry at `bt_end`, increments `bt_end`, and updates byte/compressed/uncompressed counters.

`bptree_iterate()` holds the bonus buffer, optionally dirties it for freeing, then scans entries from `bt_begin` to `bt_end`. Each entry is traversed via `traverse_dataset_destroyed()` using `bptree_visit_cb()` to invoke the caller block-pointer function.

When freeing:

- Successful traversal advances `bt_begin` and frees the processed entry range.
- Nonzero traversal errors save the bookmark for resume.
- I/O-like errors (`EIO`, `ECKSUM`, `ENXIO`) can be recorded while continuing to later entries.
- If previous I/O errors prevent advancing `bt_begin`, later completed entries are marked no-op with `be_birth_txg = UINT64_MAX`.

If `zfs_free_leak_on_eio` is set, traversal uses `TRAVERSE_HARD` and final accounting may be zeroed when all entries are logically complete.

## Dependencies

Depends on DMU object/bonus/data operations, destroyed-dataset traversal, block accounting helpers, DSL pool scan/free behavior, sync-context transactions, ZFS debug logging, and global `zfs_free_leak_on_eio`.

## Invariants And Risks

- Freeing requires a syncing transaction.
- `bt_bytes`, `bt_comp`, and `bt_uncomp` must reach zero when all entries are complete.
- Bookmarks allow resumable destruction after errors or partial processing.
- I/O error policy differs between free and nofree traversal.
- The queue counters are monotonic within one object lifetime; consumers must not assume wraparound reset except after object recreation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/bptree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/bqueue.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/bqueue.c

## Scope

Implements a bounded blocking queue whose capacity is measured in caller-supplied item-size units rather than element count.

Read completely: 111 lines.

## Main APIs

- `bqueue_init()` initializes the embedded list, add/pop condition variables, mutex, node offset, size, and maximum size.
- `bqueue_destroy()` asserts the queue is empty and destroys synchronization primitives and list state.
- `bqueue_enqueue()` blocks until enough capacity exists, stores the item size in the embedded queue node, inserts at tail, and signals consumers.
- `bqueue_dequeue()` blocks until nonempty, removes the head item, subtracts its size, and signals producers.
- `bqueue_empty()` returns whether current used capacity is zero.

## Data Model

Queued objects must embed a `bqueue_node_t` at the offset supplied to `bqueue_init()`. `obj2node()` computes the embedded node address for a queued object.

## Dependencies

Uses illumos `list_t`, condition variables, mutexes, assertions, and caller-managed item storage.

## Invariants And Risks

- `item_size` must be greater than zero and less than `bq_maxsize`.
- Capacity accounting depends on each dequeued object’s embedded `bqn_size`.
- `bqueue_empty()` reads `bq_size` without taking the lock, so callers needing a synchronized answer must externally serialize.
- Destroy requires no queued items and no blocked producers/consumers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/bqueue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/btree.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/btree.c

## Scope

Implements the illumos ZFS generic B-tree container: creation, lookup, insertion, removal, iteration, destructive traversal, clearing, and optional verification/debug poisoning.

Read completely: 2,173 lines.

## Core Model

`zfs_btree_t` owns a comparator, element size, computed leaf capacity, root pointer, tree height, element/node counts, and `bt_bulk` state for append-heavy bulk insertion.

Node types are distinguished by `bth_first`:

- Core nodes have `bth_first == -1`, store separator elements and child pointers.
- Leaf nodes store actual elements in a movable window inside a fixed-size leaf allocation.

The implementation stores element bytes directly with `memcpy`/`memmove`; elements must be plain copyable values whose comparator defines a strict order.

## Main APIs

Lifecycle:

- `zfs_btree_init()` creates the leaf kmem cache.
- `zfs_btree_fini()` destroys the cache.
- `zfs_btree_create()` initializes a tree.
- `zfs_btree_destroy()` asserts the tree is empty.
- `zfs_btree_clear()` recursively frees all nodes.

Lookup and iteration:

- `zfs_btree_find()` searches for a value and optionally returns an insertion/removal index.
- `zfs_btree_first()` and `zfs_btree_last()` return boundary elements.
- `zfs_btree_next()` and `zfs_btree_prev()` advance from an index.
- `zfs_btree_get()` returns the element at an index.
- `zfs_btree_numnodes()` returns the element count despite the name.

Mutation:

- `zfs_btree_add()` finds an insertion point and inserts a new value.
- `zfs_btree_add_idx()` inserts at a known index.
- `zfs_btree_remove()` finds and removes a value.
- `zfs_btree_remove_idx()` removes at a known index.
- `zfs_btree_destroy_nodes()` destructively iterates all elements while freeing nodes as traversal finishes with them.

Verification:

- `zfs_btree_verify()` dispatches staged checks based on `zfs_btree_verify_intensity`.

## Control Flow

Lookup descends from the root, binary-searching core separators with `zfs_btree_find_in_buf()`, then searching the target leaf. During bulk mode, it optimizes for searches near the last leaf.

Insertion handles three cases:

- Empty tree: allocate a leaf root.
- Leaf insertion: grow the movable leaf window, or split the full leaf and insert a separator into the parent.
- Core insertion: replace the separator with the new value and insert the old separator into the first slot of the right subtree.

Leaf and core splits choose half-full distribution normally, or a roughly three-quarter/one-quarter distribution during bulk insertion. Parent insertion can recursively split core nodes and create a new root.

`zfs_btree_bulk_finish()` exits bulk mode by rebalancing underfull last leaf/core nodes from their left neighbors until occupancy invariants are restored.

Removal first converts core-node removal into leaf removal by replacing the separator with the predecessor from the left subtree. Leaf removal then shrinks in place when possible, borrows from a left or right sibling when available, or merges siblings and recursively removes a separator from the parent. Core removal uses the same borrow/merge strategy and can promote a child when the root collapses.

Iteration walks leaf-local entries first, then climbs parent links to find the next separator or descends into subtrees. The same helper supports `zfs_btree_destroy_nodes()` with a callback that frees nodes after traversal no longer needs them.

## Verification Levels

`zfs_btree_verify_intensity` controls cumulative checks:

- 1: uniform tree height and node count.
- 2: child parent pointers.
- 3: occupancy/count invariants and total element count.
- 4: strict ordering and separator correctness through comparator calls.
- 5: unused-memory poisoning checks in debug builds.

Debug poison uses `0x0f` for unused element bytes and `BTREE_POISON` for unused core child pointers.

## Dependencies

Depends on ZFS/illumos allocation, `kmem_cache`, assertions, panic/verify macros, `sys/btree.h` for structure layout and capacities, and `sys/bitops.h` alignment helpers.

## Invariants And Risks

- Comparator correctness is critical; ordering verification expects normalized negative/positive behavior in several places.
- `zfs_btree_index_t` values can be invalidated by structural mutations, especially bulk-finish and removal.
- Bulk mode temporarily relaxes non-root minimum occupancy for the final nodes.
- Split/merge paths must maintain parent pointers and separator values precisely.
- Borrowing is only implemented from siblings with the same parent.
- `zfs_btree_destroy_nodes()` invalidates normal tree operations until it completes and returns `NULL`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/cityhash.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/cityhash.c

## Scope

Provides a compact CityHash-derived 64-bit hash helper for four 64-bit words.

Read completely: 63 lines.

## Main APIs

- `cityhash4(uint64_t w1, uint64_t w2, uint64_t w3, uint64_t w4)` returns a 64-bit hash over four words.

## Implementation

The file defines two CityHash constants, a rotate helper, `cityhash_helper()` mixing function, and `cityhash4()`. `rotate()` explicitly avoids shifting by 64 when the shift value is zero.

## Dependencies

Depends only on `sys/cityhash.h` and fixed-width integer behavior.

## Invariants And Risks

- This is a non-cryptographic hash.
- Correctness depends on unsigned 64-bit overflow semantics.
- The implementation is intentionally specialized to four input words rather than a general byte-string CityHash API.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/cityhash.c -->