# Group Research: group_210_bcachefs_sources_cow_pools_bcachefs_fs_bcachefs_data_reconcile_work__6da3d66bc57a

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/work.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/work.c

Background reconcile worker implementation for bcachefs. It converts scan cookies and reconcile work btree entries into move-path data updates, stripe repairs, option propagation scans, and pending retries.

Key entry points:
- `bch2_set_reconcile_needs_scan_trans()`, `bch2_set_reconcile_needs_scan()`, `bch2_set_fs_needs_reconcile()` enqueue scan cookies in `BTREE_ID_reconcile_scan`.
- `bch2_set_reconcile_needs_scan_pre()` and `bch2_set_reconcile_needs_scan_post()` bracket option changes with in-flight scan-cookie registration so a scan that overlaps an incomplete option change cannot clear the cookie.
- `bch2_extent_reconcile_pending_mod()` toggles the embedded reconcile `pending` bit for extents or btree nodes.
- `bch2_reconcile_start()`, `bch2_reconcile_stop()`, `bch2_fs_reconcile_init()`, and `bch2_fs_reconcile_exit()` manage the reconcile kthread, rhashtable state, and optional power notifier.
- `bch2_reconcile_status_to_text()` and `bch2_reconcile_scan_pending_to_text()` expose runtime state for status/debug output.

Core flow:
- Scan cookies encode filesystem-wide, metadata-only, pending, stripes, device, or inode scans. Scans update reconcile option state by walking btrees, backpointers, stripe keys, or a single inode’s extents.
- `reconcile_set_data_opts()` derives `data_update_opts` from an extent’s `bch_extent_reconcile` entry: target, checksum, compression, replica changes, EC add/drop, pointer kill masks, and flags such as `BCH_WRITE_must_ec`.
- Direct extents are processed through `bch2_move_extent()`. Stripe keys go through `bch2_stripe_repair()`. Btree-node reconcile work is reached through backpointers.
- Work phases run in fixed order: scan cookies, high-priority btree work, high-priority physical work, high-priority logical work, normal btree/physical/logical work, then pending work.
- Rotational physical work is fanned out per online rotational device so `reconcile_*_phys` work is consumed in device LBA order.

Important invariants:
- In-flight option-change scan cookies must not be deleted by the reconcile thread.
- Pending work is skipped unless a pending scan cookie was seen during the pass.
- Transaction restarts are either handled locally or treated as fatal in paths where they should have been suppressed.
- Reconcile only runs when mounted writable, `reconcile_enabled` is set, and AC-only policy permits it.
- EC stripe retries wait until older move IO has drained before retrying block evacuation work.

Dependencies and interactions:
- Uses btree iterators/update, write buffer flushing, moving context, data update/write, copygc, EC stripe repair, backpointer lookup, inode option lookup, reflink option propagation, progress reporting, power-supply notifications, and trace events.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/work.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/work.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/work.h

Public interface for the reconcile worker and scan-cookie API.

Key contents:
- Defines `RECONCILE_SCAN_TYPES()` and `struct reconcile_scan` for fs, metadata, pending, stripes, device, and inode scans.
- Declares `bch2_reconcile_opts[]` string table.
- Defines `struct opt_change_scope`, its cleanup class, and `BCH_OPT_CHANGE_SCANS_MAX`.
- Declares scan enqueue helpers, pre/post option-change helpers, pending mutation, status rendering, thread lifecycle, and fs init/exit functions.
- Provides inline `bch2_reconcile_wakeup()` which increments `c->reconcile.kick` and wakes the RCU-protected thread.
- Provides inline `bch2_reconcile_pending_wakeup()` to enqueue a pending scan cookie and wake the worker.

Important invariants:
- `opt_change_scope` is intentionally cleanup-managed so failed option changes do not leak in-flight scan-cookie registrations.
- Waking uses RCU around `c->reconcile.thread` because stop/start synchronize with wakeups.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/work.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/reflink.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/reflink.c

Implements reflink pointer validation/text, indirect extent lookup, refcount triggers, reflink creation/remap, and reflink fsck/GC refcount repair.

Key entry points:
- `bch2_reflink_p_validate()`, `bch2_reflink_p_to_text()`, `bch2_reflink_p_merge()` implement bkey operations for `KEY_TYPE_reflink_p`; merging is currently disabled.
- `bch2_reflink_v_validate()` and `bch2_reflink_v_to_text()` handle indirect extent values in the reflink btree.
- `bch2_indirect_inline_data_validate()` and `bch2_indirect_inline_data_to_text()` support reflinked inline data.
- `bch2_lookup_indirect_extent()` follows a reflink pointer into `BTREE_ID_reflink`, repairs missing-range state when requested, and returns the indirect data key plus offset.
- `bch2_trigger_reflink_p()`, `bch2_trigger_reflink_v()`, and `bch2_trigger_indirect_inline_data()` maintain refcounts and delete zero-ref indirect extents.
- `bch2_remap_range()` implements clone/remap by converting source data to indirect extents and inserting destination reflink pointers.
- `bch2_gc_reflink_start()` and `bch2_gc_reflink_done()` build/check the GC refcount table and repair wrong refcounts.

Important invariants:
- `REFLINK_P_IDX` must not be smaller than `front_pad`; indirect values must not exceed `REFLINK_P_IDX_MAX`.
- Reflink pointer triggers walk the full referenced range, including `front_pad` and `back_pad`, so split indirect extents do not leak refcounts.
- Missing indirect data in the live range sets `REFLINK_P_ERROR`; missing ranges only in padded regions shrink pads instead.
- Indirect extents with refcount zero are transformed to deleted keys before normal extent triggers run.
- Source extent conversion snapshots IO options into the new indirect extent’s reconcile entry so background reconcile does not use filesystem defaults for shared data.
- `bch2_remap_range()` uses write refs, snapshot lookup, extent punching for holes, and regular extent update to maintain destination inode size/sector accounting.

Dependencies and interactions:
- Uses btree transactions, extent helpers, reconcile trigger helpers, write extent update, inode/subvolume lookup, fsck error reporting, enumerated write refs, and the reflink GC genradix table.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/reflink.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/reflink.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/reflink.h

Header for reflink bkey operations, indirect extent helpers, remap, and reflink GC.

Key contents:
- Declares validate/text/merge/trigger functions for `reflink_p`.
- Defines `bch2_bkey_ops_reflink_p` with validation, text, merge, trigger, and 16-byte minimum value.
- Declares validate/text/trigger functions for `reflink_v` and defines `bch2_bkey_ops_reflink_v`, including pointer swabbing.
- Declares validate/text/trigger functions for `indirect_inline_data` and defines its bkey ops.
- Provides `bkey_is_indirect()`, `bkey_refcount_c()`, and `bkey_refcount()` helpers for refcount-bearing indirect keys.
- Declares `bch2_lookup_indirect_extent()`, `bch2_remap_range()`, `bch2_gc_reflink_start()`, and `bch2_gc_reflink_done()`.

Important invariants:
- Only `KEY_TYPE_reflink_v` and `KEY_TYPE_indirect_inline_data` expose refcount pointers through the helper functions.
- Reflink pointer and value bkey ops are kept separate because pointer keys live in extents while value keys live in the reflink btree.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/reflink.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/reflink_format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/reflink_format.h

On-disk format definitions for reflink pointer keys, indirect extent values, and indirect inline data.

Key contents:
- `struct bch_reflink_p` stores a packed `idx_flags`, `front_pad`, and `back_pad`.
- Bitfields define `REFLINK_P_IDX`, `REFLINK_P_ERROR`, and `REFLINK_P_MAY_UPDATE_OPTIONS`.
- `struct bch_reflink_v` stores a 64-bit refcount followed by normal extent entries.
- `struct bch_indirect_inline_data` stores a 64-bit refcount followed by inline data bytes.

Important invariants:
- `front_pad` and `back_pad` remember the full indirect range referenced when a reflink pointer was created; this is required to preserve refcount correctness after the indirect extent is split.
- `REFLINK_P_MAY_UPDATE_OPTIONS` gates whether inode IO options may propagate to shared indirect extents.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/reflink_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/update.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/update.c

Shared data update engine used by move-path consumers such as copygc, reconcile, promote, self-heal, and scrub.

Key entry points:
- `bch2_data_update_in_flight()` checks the update rhashtable to avoid unsafe overlapping updates at the same `bbpos`.
- `ptr_mask_remap()` remaps pointer masks from an original extent to a split/reassembled extent.
- `bch2_data_update_index_update()` merges newly written replicas back into the live extent key after IO completes.
- `bch2_data_update_read_done()` transitions a completed read into write submission, scrub completion, or no-write repair.
- `bch2_can_do_data_update()` predicts whether a requested move can allocate enough durability and, for mandatory EC, whether stripe allocation is feasible.
- `bch2_data_update_init()` initializes a `struct data_update`, computes replicas needed, takes device refs, locks nocow buckets, and prepares read/write bios.
- `bch2_data_update_exit()`, `bch2_fs_data_update_init()`, and `bch2_fs_data_update_exit()` clean up individual updates and the global in-flight table.

Core behavior:
- Index updates compare the current extent with the saved old extent, cut both old/new keys to the overlapping range, drop killed/conflicting pointers, append newly written pointers, and re-run reconcile tagging before committing.
- IO-error handling can rewrite from remaining replicas, drop failed pointers without a write, or record scrub journal repairs for no-repair scrub mode.
- Unwritten extents are converted by allocating replacement unwritten pointers and updating the index without data IO.
- Durability checks distinguish user data from btree data, target-constrained writes from whole-filesystem fallback, copygc from other updates, and cached pointers from durable replicas.
- Mixed checksummed/non-checksummed extents use checksum paranoia: reads prefer the specific replica being rewritten and may rewrite only one non-cached pointer at a time.

Important invariants:
- Non-copygc updates are excluded by any in-flight update at the same position; copygc only excludes other copygc.
- Device refs are stored in `cas[]` and must not be re-derived from `c->devs[]` during cleanup because device removal may clear lookup slots while refs still pin devices.
- Updates must not replace non-cached durable data with cached data.
- During option-change windows, an update that would reduce durability can force emergency read-only.
- Nocow locks are acquired after btree locks are dropped and released on all error paths.

Dependencies and interactions:
- Uses btree transactions, extent mutation helpers, write path, read bios, foreground allocator capacity checks, EC stripe-head checks, copygc wakeups, reconcile pending marking, nocow locking, scrub repair journal, and debug trace events.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/update.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/update.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/update.h

Public types and APIs for data update/move operations.

Key contents:
- Defines `BCH_DATA_UPDATE_TYPES()` for other, copygc, reconcile, promote, self-heal, scrub, and scrub_no_repair.
- `struct data_update_opts` carries pointer kill masks, EC kill masks, extra replicas, target, read device/flags, write flags, commit flags, and checksum paranoia.
- `struct data_update` stores saved old key, options, in-flight hash state, device refs, moving-context links, read bio, write op, and allocated bvecs.
- `struct promote_op` embeds a `data_update` plus work item and inline bvec storage for read promotion.
- Declares text/debug helpers, in-flight lookup, index update, read completion, feasibility checks, EC allocation failure handling, init/exit, pointer-mask remap, and fs init/exit.

Important invariants:
- `cas[]` is parallel to extent pointers and records held device refs.
- `data_update` owns both read and write state because move-path operations read an existing extent then write replacement replicas.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/update.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/write.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/write.c

Main bcachefs data write implementation. It includes extensive inline documentation for the write path, read path, EC, reflink, reconcile, move path, copygc, and scrub, followed by the implementation of COW writes, inline writes, encoded data writes, nocow writes, replica submission, and index updates.

Key entry points:
- `bch2_sum_sector_overwrites()` computes inode-sector and disk-sector deltas for an extent overwrite.
- `bch2_extent_update()` updates extents and inode accounting atomically, including reconcile tagging.
- `bch2_submit_wbio_replicas()` submits one bio per extent pointer/device, cloning bios for additional replicas.
- `bch2_write_point_do_index_updates()` serializes post-IO index updates per write point.
- `bch2_write()` is the closure entry point for foreground writes and move writes.
- `bch2_write_op_error()`, `__bch2_write_op_to_text()`, and `bch2_write_op_to_text()` provide error/status rendering.
- `bch2_fs_io_write_init()` and `bch2_fs_io_write_exit()` manage biosets.

Core behavior:
- COW writes allocate sectors through the foreground allocator, optionally compress/encrypt/checksum/bounce data, append extent keys, submit writes, then update the btree after IO completes.
- Encoded data moves may reuse existing encoded extents when compatible; otherwise compressed data is decompressed, decrypted if needed, rechecksummed, recompressed/re-encrypted, and rewritten.
- Inline writes store small file-tail data directly in `KEY_TYPE_inline_data`.
- Nocow writes try to overwrite existing writable, unencoded, non-EC extents in place; stale pointers, snapshots, incompatible extents, or alignment issues fall back to COW.
- Write errors drop failed pointers from insert keys when possible, allowing degraded writes; total failure returns data write IO error.
- Per-write-point queues track state and defer index updates to `btree_update_wq` or `copygc.wq`.

Important invariants:
- Extent updates always update the inode, even when only `bi_journal_seq` changes, so fsync correctness is preserved.
- Misaligned writes are rejected.
- `nochanges` and failed write refs stop writes before allocation/submission.
- Encryption nonces are derived from extent version state; encrypted data cannot be blindly rechecksummed as unencrypted data.
- Nocow writes require per-bucket nocow locks and valid bucket generations after btree locks are dropped.
- Move writes use `bch2_data_update_index_update()` instead of the foreground default index update path.

Dependencies and interactions:
- Uses allocator/write points/open buckets, btree extent updates, inode/subvolume lookup, checksum/compression/encryption helpers, EC writepoint buffers, nocow locking, data update, async object debug lists, journal-sensitive inode updates, and device latency/accounting.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/write.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/write.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/write.h

Public write-path API and small helpers.

Key contents:
- Includes checksum and write type definitions.
- Defines `to_wbio()` container helper.
- Declares bounce-page pool helpers, replica bio submission, write error logging, overwrite accounting, and extent update.
- Provides `index_update_wq()` to route copygc writes to `copygc.wq` and other writes to `btree_update_wq`.
- Defines `bch2_write_op_init()` initializer for `struct bch_write_op`.
- Declares `bch2_write`, `bch2_write_point_do_index_updates()`, write flag string table, write-op text helpers, and fs write init/exit.
- Provides `wbio_init()` to clear the embedded write-bio state while preserving the containing bio.

Important invariants:
- `bch2_write_op_init()` establishes safe defaults: no flags, no error, default checksum/compression from inode opts, normal watermark, empty device/open bucket lists, `POS_MAX`, and no disk reservation.
- `index_update_wq()` keeps copygc index work on its own queue.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/write.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/write_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/write_types.h

Core write-path structures and write flag definitions.

Key contents:
- Defines `BCH_WRITE_FLAGS()` and corresponding bit flags: allocation behavior, cached/data-encoded/page ownership, device targeting, EC requirement, inline write marker, ENOSPC checking, sync/move/in-worker/submitted state, and unwritten conversion.
- `struct bch_write_bio` embeds `struct bio` plus filesystem/device refs, parent split bio pointer, submit metadata, failure state, device id, nocow bucket, and state bits.
- `struct bch_write_op` is the full write operation: closure, completion callback, async debug index, status/error fields, checksum/compression/replica options, target/write point, inode/subvolume/position/version, encoded CRC, reservation, open buckets, inode size/sector deltas, insert keylist, flush mask, and embedded first `bch_write_bio`.

Important invariants:
- `bch_write_bio.ca` doubles as “we hold an IO ref” state and is stashed so completion does not re-derive a device pointer after removal.
- `struct bch_write_bio` must be last in `struct bch_write_op`.
- `inline_keys` provides initial storage for up to two maximum-size extent keys.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/write_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/debug/async_objs.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/debug/async_objs.c

Optional debugfs support for live asynchronous bcachefs objects when `CONFIG_BCACHEFS_ASYNC_OBJECT_LISTS` is enabled.

Key entry points:
- Object renderers adapt promote ops, read bios, write ops, btree read bios, and btree write bios to a common `obj_to_text` callback.
- `bch2_async_obj_list_open()` initializes a `dump_iter` for a selected async object list.
- `bch2_async_obj_list_read()` iterates the `fast_list` from the saved cursor, renders each object, and flushes the print buffer to userspace.
- `bch2_fs_async_obj_debugfs_init()` creates the `async_objs` debugfs directory and one read-only file per async object list.
- `bch2_fs_async_obj_init()` initializes all fast lists and callback pointers.
- `bch2_fs_async_obj_exit()` destroys the fast lists.

Important invariants:
- The file is compiled only under `CONFIG_BCACHEFS_ASYNC_OBJECT_LISTS`.
- `dump_iter.iter` is used as the persistent fast-list cursor across reads.
- All list files share `bch2_dump_release()` and `bch2_debugfs_flush_buf()` from the general debugfs implementation.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/debug/async_objs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/debug/async_objs.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/debug/async_objs.h

Header for optional async object list debugging.

Key contents:
- Under `CONFIG_BCACHEFS_ASYNC_OBJECT_LISTS`, defines helpers/macros to add and remove objects from per-filesystem `fast_list` instances.
- Declares debugfs init, exit, and init functions.
- Without the config option, all public helpers compile to no-ops and init returns success.

Important invariants:
- `async_object_list_add()` stores the returned fast-list index in the caller-provided `idx`.
- `async_object_list_del()` clears the stored index after removal.
- The no-config stubs preserve call-site simplicity with zero runtime behavior.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/debug/async_objs.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/debug/async_objs_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/debug/async_objs_types.h

Type definitions for async object debug lists.

Key contents:
- Defines `BCH_ASYNC_OBJ_LISTS()` for promote, rbio, write_op, btree_read_bio, and btree_write_bio.
- Defines `enum bch_async_obj_lists` ending with `BCH_ASYNC_OBJ_NR`.
- Defines `struct async_obj_list`, containing a `fast_list`, object-to-text callback, and list index.

Important invariants:
- The enum order must match callback assignment and debugfs file creation in `async_objs.c`.
- `idx` lets a list recover its containing `bch_fs` from `c->async_objs[idx]`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/debug/async_objs_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/debug/debug.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/debug/debug.c

General bcachefs debug and debugfs implementation. Provides btree dumps, transaction diagnostics, journal pin reporting, write-point reporting, node-scan reporting, and on-disk btree node rendering.

Key entry points:
- `bch2_btree_node_ondisk_to_text()` reads a btree node from its selected device, verifies checksums, decrypts bsets, and prints packed keys as stored on disk.
- `bch2_debugfs_flush_buf()` streams `printbuf` contents to userspace while preserving partially flushed data.
- `bch2_dump_open()` and `bch2_dump_release()` allocate/free `dump_iter` state for most debugfs files.
- `bch2_read_btree()`, `bch2_read_btree_formats()`, and `bch2_read_bfloat_failed()` dump btree keys, btree node formats, and bfloat diagnostics.
- `bch2_cached_btree_nodes_read()` dumps cached btree nodes from the rhashtable.
- `bch2_btree_transactions_read()`, `btree_transaction_stats_read()`, and `btree_deadlock_to_text()` expose live transaction state, stats, backtraces, and deadlock checks.
- `bch2_journal_pins_read()`, `bch2_btree_updates_read()`, `bch2_write_points_read()`, and `bch2_btree_node_scan_read()` expose journal pins, pending btree updates, allocator write points, and discovered node-scan entries.
- `bch2_fs_debug_init()` creates per-filesystem debugfs files/directories, including async object debugfs and per-btree subdirectories.
- `bch2_debug_init()`, `bch2_debug_exit()`, and `bch2_fs_debug_exit()` manage global and per-filesystem debugfs roots.

Important invariants:
- Most btree debug reads return nothing until `BCH_FS_may_go_rw` because multithreaded btree access is unsafe while journal-key gap-buffer recovery is still mutating state.
- Long debugfs reads preserve cursor state in `dump_iter` and repeatedly flush to avoid unbounded userspace copies.
- Live transaction traversal uses SRCU, `seqmutex`, sorted pointer order, and refcount checks to survive concurrent transaction changes.
- On-disk btree rendering validates checksum type and checksum before decrypting/printing each bset.
- Debugfs initialization tolerates missing/failed debugfs dentries by returning early.

Dependencies and interactions:
- Uses btree cache/iter/locking/read/update/node-scan helpers, extent read-device selection, journal reclaim/pin reporting, data update text helpers, async object debugfs, inode/fs init state, Linux debugfs, seq files, and bio submission.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/debug/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/debug/debug.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/debug/debug.h

Public debug/debugfs interface for bcachefs.

Key contents:
- Declares `bch2_btree_node_ondisk_to_text()`.
- Under `CONFIG_DEBUG_FS`, defines `struct dump_iter` shared by debugfs readers.
- Declares buffer flushing, dump release, per-filesystem debug init/exit, and global debug init/exit.
- Without `CONFIG_DEBUG_FS`, provides no-op stubs and success return for `bch2_debug_init()`.

Important invariants:
- `dump_iter` carries filesystem/list/btree selection, cursor positions, print buffer, userspace destination, request size, and accumulated return count.
- Async object debugfs reuses `dump_iter`, `bch2_debugfs_flush_buf()`, and `bch2_dump_release()`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/debug/debug.h -->