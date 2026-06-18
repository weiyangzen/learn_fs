# Group Research: group_526_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_z_dde37cfcce1d

Scope: illumos-gate ZFS headers under `usr/src/uts/common/fs/zfs/sys`, all listed in `Docs/research_subset_a.md`. All 34 source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/arc_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/arc_impl.h

Read status: complete, 876 lines.

Purpose: private ARC/L2ARC implementation definitions. This header defines ARC state accounting, ARC callback records, split ARC buffer headers, persistent L2ARC on-disk metadata, L2ARC device state, encrypted-buffer header state, and the large ARC kstat surface.

Key structures and APIs:
- `arc_state_t` tracks per-state evictable lists and sizes for ARC data and metadata.
- `arc_callback_t` and `arc_write_callback_t` carry async read/write completion callbacks and associated ARC buffer state.
- `l1arc_buf_hdr_t`, `l2arc_buf_hdr_t`, `arc_buf_hdr_crypt_t`, and `arc_buf_hdr_t` define the memory-optimized ARC header layout, including L1-only, L2ARC-only, and encryption-specific fields.
- Persistent L2ARC metadata is described by `l2arc_dev_hdr_phys_t`, `l2arc_log_blkptr_t`, `l2arc_log_ent_phys_t`, and `l2arc_log_blk_phys_t`, with compile-time size/alignment checks.
- `l2arc_dev_t` stores per-cache-device write pointer state, persistent-log metadata, rebuild flags, and log-block accounting.
- `arc_stats_t` exposes ARC/L2ARC hit/miss, eviction, size, compression, rebuild, and memory-pressure counters.

Important implementation constraints:
- ARC buffers can live in anon, MRU, MFU, MRU ghost, MFU ghost, or L2ARC-only states; only unreferenced list-linked buffers can be evicted/deleted.
- Metadata and data are tracked separately for policy and accounting.
- L2ARC persistence depends on byte-order-aware magic values and packed property fields manipulated through bitfield macros.
- Several ARC sizing variables are aliases over kstat fields, avoiding duplicated shadow state.

Dependencies: `arc.h`, `multilist.h`, SPA/ZIO block and checksum definitions, ABD buffers, refcounts, kstats, and bitfield helpers.

Research notes:
- This is a central private ABI for `arc.c`, `zdb`, and L2ARC rebuild/write paths.
- The persistent L2ARC structs are on-disk format sensitive and guarded by `CTASSERT`.
- `l2arc_log_blkptr_valid()` is exported for `zdb.c`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/arc_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/bitops.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/bitops.h

Read status: complete, 90 lines.

Purpose: generic 32-bit and 64-bit bitfield encode/decode/get/set helpers used throughout ZFS packed metadata fields.

Key definitions:
- `BF32_DECODE`, `BF64_DECODE`, `BF32_ENCODE`, `BF64_ENCODE` implement low/length field extraction and insertion.
- `BF32_GET`, `BF64_GET`, `BF32_SET`, `BF64_SET` provide direct bitfield access with assertion checks.
- `BF32_GET_SB`, `BF64_GET_SB`, `BF32_SET_SB`, `BF64_SET_SB` add shifted-and-biased encodings for fields such as block sizes.

Important implementation constraints:
- Set macros assert value range and field bounds.
- Shift/bias variants assert power-of-two alignment and nonnegative biased value.
- The macros use `ASSERT3U`/`ASSERT3S` and `_NOTE(CONSTCOND)` to avoid lint issues.

Dependencies: `zfs_context.h`, especially `P2PHASE`, `IS_P2ALIGNED`, and assertion macros.

Research notes:
- These macros are foundational for packed fields in ARC/L2ARC, DDT keys, block pointers, and similar metadata.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/bitops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/blkptr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/blkptr.h

Read status: complete, 39 lines.

Purpose: declares helpers for embedded block pointer encoding and decoding.

Key APIs:
- `encode_embedded_bp_compressed()` writes compressed embedded data into a `blkptr_t`.
- `decode_embedded_bp_compressed()` extracts compressed embedded payload data.
- `decode_embedded_bp()` decodes an embedded block pointer into a caller buffer.

Dependencies: `spa.h` for `blkptr_t` and block pointer constants; `zio.h` for compression enum types.

Research notes:
- This is a narrow interface for embedded block pointer handling, used where small payloads are stored directly inside a block pointer instead of separate allocated blocks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/blkptr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/bplist.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/bplist.h

Read status: complete, 57 lines.

Purpose: in-memory linked list wrapper for `blkptr_t` values.

Key structures and APIs:
- `bplist_entry_t` stores one block pointer plus list linkage.
- `bplist_t` stores a mutex and list head.
- `bplist_itor_t` is an iterator callback receiving a block pointer and transaction.
- `bplist_create()`, `bplist_destroy()`, `bplist_append()`, and `bplist_iterate()` manage list lifecycle and traversal.

Dependencies: `zfs_context.h`, `spa.h`, `dmu_tx_t`.

Research notes:
- Used for pending deadlists and other transient collections of block pointers.
- The interface is memory-resident and transaction-aware only through iterator callbacks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/bplist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/bpobj.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/bpobj.h

Read status: complete, 95 lines.

Purpose: defines persistent block-pointer object storage, typically used for deadlists and deferred frees.

Key structures and APIs:
- `bpobj_phys_t` is the bonus-buffer physical summary: number of block pointers, byte/compressed/uncompressed totals, and subobject counts.
- `bpobj_t` is the in-core opened object, with lock, objset/object id, entries-per-block, feature flags, physical pointer, and dbufs.
- Allocation/free/open/close APIs include `bpobj_alloc()`, `bpobj_alloc_empty()`, `bpobj_free()`, `bpobj_open()`, `bpobj_close()`.
- Iteration and enqueue APIs include `bpobj_iterate()`, `bpobj_iterate_nofree()`, `bpobj_enqueue()`, and `bpobj_enqueue_subobj()`.
- Space-query APIs include `bpobj_space()`, `bpobj_space_range()`, and `bpobj_is_empty()`.

Dependencies: DMU objects/transactions, SPA block pointers, TXG, ZIO, ZFS context.

Research notes:
- Supports older physical sizes (`BPOBJ_SIZE_V0`, `BPOBJ_SIZE_V1`) and optional compressed/subobject accounting.
- Forms a major building block for dataset deadlists and pool free/obsolete block tracking.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/bpobj.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/bptree.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/bptree.h

Read status: complete, 65 lines.

Purpose: persistent tree/list of block pointers with birth-TXG and traversal-resume metadata, used for deferred block processing.

Key structures and APIs:
- `bptree_phys_t` records begin/end counters and byte/compressed/uncompressed totals.
- `bptree_entry_phys_t` stores a `blkptr_t`, a minimum birth TXG for deletion eligibility, and a `zbookmark_phys_t` resume point.
- `bptree_alloc()`, `bptree_free()`, `bptree_is_empty()` manage object lifecycle.
- `bptree_add()` records a block pointer and accounting.
- `bptree_iterate()` processes entries, optionally freeing them.

Dependencies: SPA block pointers, ZIO bookmarks, DMU transactions.

Research notes:
- Similar role to `bpobj`, but with per-entry traversal resume support.
- Used by asynchronous destroy/deferred free flows.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/bptree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/bqueue.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/bqueue.h

Read status: complete, 54 lines.

Purpose: bounded blocking queue abstraction with byte-size accounting.

Key structures and APIs:
- `bqueue_t` stores a list, lock, producer/consumer condition variables, current size, max size, and node offset.
- `bqueue_node_t` supplies embedded linkage and item size.
- `bqueue_init()`, `bqueue_destroy()`, `bqueue_enqueue()`, `bqueue_dequeue()`, and `bqueue_empty()` manage queue use.

Dependencies: `zfs_context.h`.

Research notes:
- The node offset lets callers embed `bqueue_node_t` inside arbitrary payload structs.
- Queue capacity is tracked by logical item size, not just item count.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/bqueue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/btree.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/btree.h

Read status: complete, 249 lines.

Purpose: public interface and structural definitions for ZFS’s generic in-memory B-tree.

Key structures and APIs:
- `zfs_btree_hdr_t`, `zfs_btree_core_t`, and `zfs_btree_leaf_t` define internal node layouts.
- `zfs_btree_index_t` identifies a node/offset/before-position for search and insertion.
- `zfs_btree_t` stores root, height, element size, leaf capacity, element/node counts, bulk-load state, and comparator.
- Lifecycle APIs: `zfs_btree_init()`, `zfs_btree_fini()`, `zfs_btree_create()`, `zfs_btree_destroy()`, `zfs_btree_clear()`.
- Lookup/navigation APIs: `zfs_btree_find()`, `zfs_btree_first()`, `zfs_btree_last()`, `zfs_btree_next()`, `zfs_btree_prev()`, `zfs_btree_get()`.
- Mutation APIs: `zfs_btree_add()`, `zfs_btree_add_idx()`, `zfs_btree_remove()`, `zfs_btree_remove_idx()`.
- Cleanup/verification APIs: `zfs_btree_destroy_nodes()`, `zfs_btree_numnodes()`, `zfs_btree_verify()`.

Important implementation constraints:
- Returned element pointers and indexes are internal and invalidated by insertion, removal, and node destruction.
- Elements are stored exactly once; core nodes hold real elements, not copies of leaf elements.
- Comparator must return exactly `-1`, `0`, or `+1`.
- Supports optimized bulk in-order insertion via `bt_bulk`.

Dependencies: `zfs_context.h`.

Research notes:
- Useful for arbitrary sortable in-memory data with lower overhead than AVL in some workloads.
- Header documents invariants in detail, especially around node fullness and mutation invalidation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/cityhash.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/cityhash.h

Read status: complete, 41 lines.

Purpose: declaration for a small CityHash-derived hash helper.

Key API:
- `uint64_t cityhash4(uint64_t, uint64_t, uint64_t, uint64_t);`

Dependencies: `zfs_context.h`.

Research notes:
- The header includes the upstream Google permissive license notice and a Delphix copyright.
- It exposes only a four-word 64-bit hash function, not the full CityHash API.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/cityhash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dbuf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dbuf.h

Read status: complete, 450 lines.

Purpose: private DMU buffer implementation interface. Defines dbuf state, dirty records, in-core dbuf layout, hash table layout, cache policy macros, and internal dbuf lifecycle/read/write APIs.

Key structures and APIs:
- Read flags include `DB_RF_MUST_SUCCEED`, `DB_RF_CANFAIL`, `DB_RF_NOPREFETCH`, `DB_RF_NEVERWAIT`, `DB_RF_CACHED`, and `DB_RF_NO_DECRYPT`.
- `dbuf_states_t` models the dbuf state machine: search sentinel, uncached, fill, nofill, read, cached, evicting.
- `dbuf_dirty_record_t` records per-TXG dirty state and distinguishes indirect dirty children from leaf data/override/raw-encryption parameters.
- `dmu_buf_impl_t` wraps public `dmu_buf_t` with objset/dnode/parent/hash metadata, block identity, state locks, ARC buffer pointer, holds, dirty records, AVL/list cache linkage, user callback data, and eviction flags.
- `dbuf_hash_table_t` exposes the global dbuf hash table shape for mdb.
- Core APIs cover hold/find/read/prefetch/refcount/release, dirtying, ARC buffer assignment/loaning, embedded writes, dirty-list syncing, block-pointer release, parent locking, remap checks, free ranges, and cache initialization.

Important implementation constraints:
- `db_rwlock` protects indirect/meta-dnode tree structure; documented ordering is dnode structure lock before dbuf lock.
- `db_mtx` protects mutable buffer state, holds, data pending, dirty records, cache status, and user fields.
- Dbuf cacheability is derived from objset primary/secondary cache policy and metadata classification.
- Dnode access uses `dnode_handle_t` plus `zrlock` macros to survive dnode movement.

Dependencies: DMU, SPA, TXG, ZIO, ARC, refcounts, zrlock, multilist.

Research notes:
- This header is the main boundary between public DMU buffers, ARC storage, and dnode block-tree structure.
- Debug macros integrate dbuf and block pointer information into dataset-level debug logging.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dbuf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/ddt.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/ddt.h

Read status: complete, 255 lines.

Purpose: deduplication table definitions for on-disk keys/phys records, in-core entries/tables, object operations, stats, repair, and sync.

Key structures and APIs:
- DDT currently declares `DDT_TYPE_ZAP`; classes are ditto, duplicate, and unique.
- `ddt_key_t` stores checksum plus packed logical size, physical size, compression, and encryption state.
- `ddt_phys_t` stores up to `SPA_DVAS_PER_BP` DVAs, refcount, and physical birth TXG.
- `ddt_entry_t` is the in-core dedup entry with all physical variants, lead ZIOs, repair ABD, loading state, condition variable, and AVL linkage.
- `ddt_t` stores per-checksum dedup state, object ids, histograms, cached histograms, object stats, and AVL linkage.
- `ddt_ops_t` abstracts backend object operations: create/destroy/lookup/prefetch/update/remove/walk/count.
- APIs cover object lookup/info/walk, block pointer/key/phys conversion, refcount changes, histogram/stat aggregation, dedup ratio/space queries, ditto-copy decisions, compression, table lookup/prefetch/remove, repair lifecycle, create/load/unload/sync, and backend update.

Important implementation constraints:
- Packed `ddk_prop` uses `BF64_*` macros and is on-disk format sensitive.
- `DDE_GET_NDVAS()` reduces available DVAs when encrypted.
- DDT object type/class search order is encoded in enum ordering.

Dependencies: sysmacros/types, ZFS fs definitions, ZIO, DMU, bitfield helpers, ABD.

Research notes:
- `ddt_zap_ops` is the declared backend.
- DDT ties checksum identity, physical block replicas, dedup stats, and repair workflows together.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/ddt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu.h

Read status: complete, 1091 lines.

Purpose: primary public Data Management Unit interface for consumers. It defines DMU object types, objset operations, buffer holds/users, transaction lifecycle, read/write APIs, object and objset stats, sync writes, traversal, diff, and CRC support.

Key definitions:
- `dmu_object_byteswap_t` enumerates byteswap strategies.
- `DMU_OT()` encodes new object types with byteswap, metadata, and encryption flags.
- `dmu_object_type_t` lists legacy fixed on-disk object types and newer `DMU_OTN_*` encoded variants.
- TXG assignment flags: `TXG_NOWAIT`, `TXG_WAIT`, `TXG_NOTHROTTLE`.
- `dmu_buf_t` is the public buffer shape: object, offset, size, data pointer.
- MOS directory ZAP names are declared as `DMU_POOL_*` constants.
- `dmu_buf_user_t` defines dbuf client eviction callback state.
- `dmu_object_info_t`, `dmu_object_type_info_t`, `dmu_object_byteswap_info_t`, and `dmu_objset_stats_t` define metadata query results.
- `zgd_t` and `dmu_sync_cb_t` support synchronous write completion.

Major API areas:
- Objset lifecycle: hold/own/release/disown/create/clone/snapshot/find/remap.
- Object lifecycle: alloc/claim/reclaim/free/next/set block size/set checksum/set compression/remap.
- Bonus/spill buffer access and mutation.
- Buffer holds, array holds, refcounts, dbuf users, user eviction waiting, block pointer access, dirty marking, and raw crypto parameter setting.
- Transaction creation, holds, assignment, wait, commit, abort, callback registration, and netfree marking.
- Data operations: range free, read/write, uio read/write, page write, prealloc, ARC buffer request/assign/return, raw conversion, xuio helpers, prefetch.
- Object/objset info and space/stat queries.
- Dataset/listing helpers, objset user pointer registration, txg lookup.
- `dmu_sync()`, offset hole/data search, object wait-synced, init/fini, objset traversal, `dmu_diff()`.

Important implementation constraints:
- Public comments define transaction ordering: create transaction, hold possible modified objects, assign to TXG, then modify buffers.
- Dbuf users must not reference the dbuf from eviction callbacks because callbacks run after eviction processing has begun and without dbuf mutex guarantees.
- `DMU_MAX_ACCESS` caps one operation including metadata at 32 MiB.
- New on-disk object types should use encoded `DMU_OTN_*` instead of extending fixed enum values.

Dependencies: ZFS context, credentials, ZFS property types, compression/priority enums, SPA/ZIO/dsl/dnode forward declarations.

Research notes:
- This is the highest-level interface in the group and is consumed by ZPL, ZVOL, ZAP, DSL, SPA, send/receive, and tools.
- Many declarations are implemented across multiple `.c` files, not a single DMU implementation file.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_impl.h

Read status: complete, 303 lines.

Purpose: private DMU implementation definitions, especially lock-order documentation, xuio stats, send-stream aggregation state, and internal object helpers.

Key contents:
- Large lock-order comment documents ordering and protected fields across ARC, bplist, refcount, txg, zfetch, objset, dnode, dbuf, dsl_dir, dsl_dataset, dirty records, and pool config locks.
- `dmu_xuio_t` tracks extended-uio ARC buffers and iovec state.
- `xuio_stats_t` exposes loaned/copy/no-copy read/write buffer stats.
- `dmu_pendop_t` tracks pending aggregated send stream operations.
- `dmu_sendarg_t` stores state for send-stream generation, including output vnode/fd/off, objset, checksum, GUID/TXG range, pending free/freeobjects aggregation, feature flags, resume state, and begin/end flags.
- Internal helpers: `dmu_object_zapify()`, `dmu_object_free_zapified()`, `dmu_buf_hold_noread()`.

Dependencies: txg internals, ZIO, dnode, ZFS context/ioctl, DMU types.

Research notes:
- The lock-order section is critical when analyzing deadlock risks in DMU/dbuf/dnode/DSL code.
- Send stream internals here complement the public declarations in `dmu_send.h` and `dmu.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_objset.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_objset.h

Read status: complete, 268 lines.

Purpose: private objset physical and in-core definitions plus objset implementation APIs.

Key structures and APIs:
- `objset_phys_t` stores the meta dnode, ZIL header, type/flags, encryption MACs, and optional user/group/project accounting dnodes across V1/V2/V3 physical sizes.
- `objset_t` stores dataset/spa links, physical buffer, encryption state, special dnode handles, ZIL pointer, tunable property cache, root block pointer, sync state, dirty dnode lists, object allocation hints, user-used locking, user pointer, SA state, and upgrade task state.
- Macros detect physical feature availability by objset buffer size and expose special dnodes.
- Public/internal APIs cover hold/own/release/disown, ownership refresh, stats/space, find/prefetch, dbuf eviction, sync, create/open/evict, user quota updates/upgrades, encryption compatibility checks, name parsing, dirty space accounting, and init/fini.

Important implementation constraints:
- Special dnodes have no parent and are exempt from dnode movement but still use handles for uniform dbuf access.
- `os_rootbp` points to a block pointer protected by the dataset’s `ds_bp_rwlock`.
- Object allocation uses both `os_obj_lock` and per-CPU next-object hints.
- User/group/project accounting objects are guarded by `os_userused_lock`.

Dependencies: SPA, ARC, TXG, dnode, ZIO, ZIL, SA, ZFS ioctl/property types.

Research notes:
- This header bridges objset physical layout, DMU object allocation, ZIL, quota accounting, and dataset encryption state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_objset.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_recv.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_recv.h

Read status: complete, 71 lines.

Purpose: receive-side DMU send stream interface.

Key structures and APIs:
- `recv_clone_name` extern identifies clone receive naming support.
- `dmu_recv_cookie_t` carries receive state: target dataset/snapshot names, begin record pointers, flags for newfs/byteswap/force/resumable/raw/clone/spill, GUID map, raw key nvlist, checksum, snapshot object ids, IV-set GUID, owner, and credential.
- `dmu_recv_begin()` validates/prepares a receive.
- `dmu_recv_stream()` consumes stream data from a vnode/offset and supports cleanup/action handle plumbing.
- `dmu_recv_end()` finalizes receive state.
- `dmu_objset_is_receiving()` tests whether an objset is in receive mode.

Dependencies: integer types, DSL crypto, SPA, vnode, nvlist, credentials, replay record forward declarations.

Research notes:
- Supports resumable and raw encrypted receives through cookie fields and crypto nvlist handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_recv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_send.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_send.h

Read status: complete, 53 lines.

Purpose: send-side DMU stream interface.

Key APIs:
- `dmu_send()` sends a dataset snapshot stream by name, optionally incremental from another snapshot, with embedded/large-block/compressed/raw stream options and resume object/offset support.
- `dmu_send_estimate()` and `dmu_send_estimate_from_txg()` estimate stream size.
- `dmu_send_obj()` sends by pool and snapshot object ids.

Dependencies: integer types, SPA, vnode, dataset and replay-record forward declarations.

Research notes:
- Complements internal `dmu_sendarg_t` in `dmu_impl.h`.
- Supports resumable send and feature-controlled stream formats.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_send.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_traverse.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_traverse.h

Read status: complete, 78 lines.

Purpose: block tree traversal interface for datasets, destroyed datasets, and pools.

Key definitions and APIs:
- `blkptr_cb_t` callback receives SPA, ZIL, block pointer, bookmark, containing dnode physical pointer, and caller argument.
- Traversal flags include pre/post visiting, metadata/data prefetch, hard traversal, and no-decrypt traversal.
- `TRAVERSE_VISIT_NO_CHILDREN` is a special callback return value to skip children.
- APIs: `traverse_dataset()`, `traverse_dataset_resume()`, `traverse_dataset_destroyed()`, `traverse_pool()`.

Important implementation constraints:
- `TRAVERSE_NO_DECRYPT` allows callers to receive raw encrypted dnodes instead of logical decrypted data, because encrypted dnode blocks have encrypted bonus buffers but unencrypted structural fields.

Dependencies: ZFS context, SPA, ZIO, dataset/dnode/ZIL/ARC forward declarations.

Research notes:
- Used by send, scrub, space accounting, deadlist processing, and diagnostic traversal paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_traverse.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_tx.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_tx.h

Read status: complete, 153 lines.

Purpose: private DMU transaction structure definitions and DMU-internal transaction APIs.

Key structures and APIs:
- `dmu_tx_t` stores hold list, objset/dir/pool, assigned TXG, last snapshot/tried TXGs, TXG handle, temp reservation cookie, needed assignment hold, callbacks, sync-placeholder flag, netfree flag, start time, dirty wait/delay flags, and error.
- `dmu_tx_hold_type` enumerates hold kinds: new object, write, bonus, free, zap, space, spill.
- `dmu_tx_hold_t` records per-hold dnode, space/memory refcounts, type, and arguments.
- `dmu_tx_callback_t` stores commit/abort callback entries.
- Public APIs are redeclared from `dmu.h`; SPA-only and DMU-only helpers include `dmu_tx_create_assigned()`, `dmu_tx_create_dd()`, `dmu_tx_is_syncing()`, `dmu_tx_private_ok()`, `dmu_tx_add_new_object()`, `dmu_tx_dirty_buf()`, and `dmu_tx_hold_space()`.

Important implementation constraints:
- A transaction is handled by one thread, so `dmu_tx_t` itself needs no synchronization.
- `DMU_TX_DIRTY_BUF` is active only in debug builds.

Dependencies: DMU, TXG, refcount, dsl pool/dir/dnode/dbuf forward declarations.

Research notes:
- This header exposes the internal accounting model behind public transaction holds.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_tx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_zfetch.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_zfetch.h

Read status: complete, 81 lines.

Purpose: DMU sequential-read prefetch tracking interface.

Key structures and APIs:
- `zfetch_t` owns a read/write lock, list of streams, owning dnode, and stream count.
- `zstream_t` tracks expected next block id, next prefetched block id, next indirect-prefetch block id, lock, timing, list linkage, parent fetch, and pending block refcount.
- Global tunable extern: `zfetch_array_rd_sz`.
- Lifecycle APIs: `zfetch_init()`, `zfetch_fini()`, `dmu_zfetch_init()`, `dmu_zfetch_fini()`.
- `dmu_zfetch()` observes accesses and may issue data/metadata prefetch.

Dependencies: ZFS context, dnode forward declaration, refcounts.

Research notes:
- Tightly connected to dnode access and dbuf prefetch, but isolated behind a small state structure embedded in `dnode_t`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_zfetch.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dnode.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dnode.h

Read status: complete, 603 lines.

Purpose: defines physical and in-core dnode layout, dnode constants, large-dnode support, dnode handles, allocation/free/sync APIs, cacheability macros, and dnode kstats.

Key definitions:
- Hold flags: `DNODE_MUST_BE_ALLOCATED`, `DNODE_MUST_BE_FREE`, `DNODE_DRY_RUN`.
- Offset search flags: `DNODE_FIND_HOLE`, `DNODE_FIND_BACKWARDS`, `DNODE_FIND_HAVELOCK`.
- Fixed constants define dnode sizes, indirect block shift limits, object/offset limits, dnodes per block/level, maximum levels, bonus sizes, slot sentinels, and spill pointer location.
- Dnode flags track used-byte encoding, user/group/project accounting, and spill block pointer presence.
- Large dnode comments explain variable-size dnodes from 512 bytes to 16 KiB and the relationship between on-disk `dn_extra_slots` and in-memory `dn_num_slots`.

Key structures and APIs:
- `dnode_phys_t` is the on-disk dnode: type, block shifts, levels, block pointer count, bonus type, checksum/compression, flags, data block size, bonus length, extra slots, max block id, used space, padding protected by MACs, block pointers/bonus/spill union.
- `dnode_t` is the in-core dnode: structure lock, objset/object/dbuf/handle/phys pointers, cached physical fields, next-TXG pending field arrays, dirty links, dirty records, free ranges, TXG/refcount state, dbuf AVL tree, bonus dbuf, spill state, sync write parent zio, old/new id accounting state, and embedded zfetch state.
- `dnode_handle_t` uses `zrlock_t` to protect dnode moves.
- `dnode_children_t` attaches child dnode handles to a meta-dnode dbuf user.
- `free_range_t` records block ranges pending free.
- APIs cover special dnode open/close, bonus/spill mutation, hold/ref/release, try-claim, dirty/sync, allocate/reallocate/free, byteswap/verify, level/block-size changes, free ranges, space accounting, new block ids, block-free lookup, init/fini, hole/data search, dbuf/bonus eviction, interior slot freeing, and remap checks.

Important implementation constraints:
- `dn_struct_rwlock` protects tree structure and pending structural changes.
- `dn_dbufs` can contain duplicate logical dbufs when evicting, so lookup uses walks/search sentinel semantics instead of direct AVL uniqueness by logical key.
- Handles prevent dnode movement from invalidating dbuf-owned dnode access.
- Dnode MAC coverage matters for encrypted datasets; new fields in protected padding require crypto path review.

Dependencies: ZFS context, AVL, SPA, TXG, ZIO, refcount, zfetch, zrlock, multilist.

Research notes:
- This is the core object metadata header for DMU object storage.
- `dnode_stats_t` provides detailed counters for dnode hold allocation/free paths, allocation races, buffer eviction, and dnode movement.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dnode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_bookmark.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_bookmark.h

Read status: complete, 69 lines.

Purpose: DSL bookmark physical format and management interface.

Key structures and APIs:
- `zfs_bookmark_phys_t` stores bookmarked dataset GUID, creation TXG/time, redaction-related reserved fields, referenced/compressed/uncompressed byte stats, freed-before-next-snap stats, and raw-send IV-set GUID.
- Physical size constants: `BOOKMARK_PHYS_SIZE_V1`, `BOOKMARK_PHYS_SIZE_V2`.
- APIs: `dsl_bookmark_create()`, `dsl_get_bookmarks()`, `dsl_get_bookmarks_impl()`, `dsl_bookmark_destroy()`, `dsl_bookmark_lookup()`.

Dependencies: ZFS context, DSL dataset.

Research notes:
- Bookmark format already reserves fields for redacted send/receive and raw sends.
- Stored as on-disk ZAP entries.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_bookmark.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_crypt.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_crypt.h

Read status: complete, 235 lines.

Purpose: DSL encryption key management and SPA keystore interface.

Key structures and APIs:
- On-disk crypto key ZAP names include suite, GUID, IV, MAC, master key, HMAC key, root dsl_dir object, refcount, and version.
- `dsl_wrapping_key_t` stores loaded wrapping key state for an encryption root: keyformat, PBKDF2 salt/iters, crypto key, refcount, and owning dsl_dir object.
- `dcp_cmd_t` describes crypto parameter commands for raw receive, new key, inherit, and forced variants.
- `dsl_crypto_params_t` packages command, encryption algorithm, keylocation, and wrapping key.
- `dsl_crypto_key_t` stores a loaded DSL crypto key: holds, derived encryption key, wrapping key, and on-disk object.
- `dsl_key_mapping_t` maps dataset object id to DSL crypto key for zio-layer encryption/decryption lookup.
- `spa_keystore_t` owns AVL trees and locks for DSL keys, dataset mappings, and wrapping keys.
- APIs cover crypto param creation/free, dataset crypto stats, keylocation validation, keystore init/fini, wrapping key load/unload, key mapping create/remove/ref/release/lookup, raw receive key population/check/sync, change-key check/sync, rename/promote crypto checks, encrypted objset create checks/sync, key create/clone/destroy, salt lookup, MAC generation/verification, objset MAC, and data encrypt/decrypt via ABD.

Dependencies: DMU transactions, DMU object types, ZIO crypt, SPA, DSL dataset/dir.

Research notes:
- The header captures both administrative key lifecycle and data-path cryptographic entry points.
- Dataset object ids are the bridge between DSL key mapping and zio block encryption.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_crypt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_dataset.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_dataset.h

Read status: complete, 488 lines.

Purpose: DSL dataset physical/in-core definitions and dataset lifecycle/accounting APIs.

Key structures and APIs:
- Dataset flags track inconsistency, no-promote, unique-byte accuracy, deferred destroy, case-insensitive dataset, and create-no-dirty.
- `DS_FIELD_*` strings define extensible ZAP fields for bookmarks, large dnodes, resumable receive state, remap deadlist, and encrypted snapshot IV-set GUID.
- `dsl_dataset_phys_t` stores directory linkage, previous/next snapshot linkage, snapshot names object, child count, creation time/TXG, deadlist object, referenced/compressed/uncompressed/unique bytes, fsid/guid, flags, root block pointer, clone/properties/userrefs objects, and padding.
- `dsl_dataset_t` stores dbuf user, root block pointer lock, immutable dir/object/fsid/snapshot/key mapping state, previous snapshot, bookmarks object, deadlists, remap deadlist, dirty/synced links, object/open/userref/owner/quota/reservation/sendstream/resume/prop/feature state, and snapname.
- Argument structs support promote, rollback, and snapshot operations.
- APIs cover hold/own/release/disown, key mapping, create, snapshot, promote, clone swap, rename snapshots, temporary snapshots, block pointer/spa access, sync, block born/kill/remapped, dirtying, stats getters, quota/refreservation setters, long holds, clone-swap/snapshot internals, snap lookup/remove, zapification, resumable receive detection, rollback, remap deadlist management, per-dataset feature activation/deactivation/query, and debug logging.

Important implementation constraints:
- `ds_bp_rwlock` protects `ds_phys->ds_bp`.
- Long holds prevent dataset destruction after config lock is dropped.
- `ds_remap_deadlist` tracks physical DVAs remapped away from indirect vdevs for obsolete-count accounting.
- Per-dataset features use `ds_feature[]` and `ds_feature_activation[]`.

Dependencies: DMU, SPA, TXG, ZIO, bplist, DSL synctask, deadlist, refcount, rrwlock, DSL crypto, feature definitions.

Research notes:
- This is the central DSL object for snapshots, clones, send/receive resume state, quota/refreservation accounting, deadlists, and per-dataset features.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_dataset.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_deadlist.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_deadlist.h

Read status: complete, 89 lines.

Purpose: persistent deadlist abstraction for blocks no longer referenced by a dataset but still relevant to snapshot lineage.

Key structures and APIs:
- `dsl_deadlist_phys_t` stores used/compressed/uncompressed totals and padding.
- `dsl_deadlist_t` stores objset/object, AVL tree, physical dbuf, lock, and old-format `bpobj_t`.
- `dsl_deadlist_entry_t` maps minimum TXG to a `bpobj_t`.
- APIs open/close/alloc/free, insert block pointers, add/remove TXG keys, clone up to a TXG, query total/range space, merge another deadlist, move a bpobj into the deadlist, and test open state.

Dependencies: `bpobj.h`, ZFS context, DMU objects/transactions.

Research notes:
- Supports both current tree-based format and old bpobj-only format.
- Used heavily by dataset snapshot/clone/destroy accounting.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_deadlist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_deleg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_deleg.h

Read status: complete, 91 lines.

Purpose: ZFS delegated administration permission names and DSL delegation APIs.

Key definitions and APIs:
- Permission string constants include create, destroy, snapshot, rollback, clone, promote, rename, mount, share, send, receive, allow, userprop, vscan, quota/used/object-quota variants, hold, release, diff, bookmark, remap, load-key, change-key, and project quota/used variants.
- APIs: `dsl_deleg_get()`, `dsl_deleg_set()`, `dsl_deleg_access()`, `dsl_deleg_access_impl()`, `dsl_deleg_set_create_perms()`, allow/unallow checks, delegation ZAP destroy, and `dsl_delegation_on()`.

Dependencies: DMU, DSL pool, ZFS context, credentials.

Research notes:
- Delegatable property names are also valid delegated permissions.
- This header is the permission vocabulary for administrative checks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_deleg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_destroy.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_destroy.h

Read status: complete, 68 lines.

Purpose: dataset and snapshot destruction interfaces.

Key APIs:
- Snapshot destruction: `dsl_destroy_snapshots_nvl()`, `dsl_destroy_snapshot()`, check/sync implementations, and sync-task wrappers.
- Head dataset destruction: `dsl_destroy_head()`, `dsl_destroy_head_check_impl()`, `dsl_destroy_head_sync_impl()`, check/sync wrappers.
- `dsl_destroy_inconsistent()` handles inconsistent dataset destruction.
- Argument structs carry snapshot name/defer flag and head dataset name.

Dependencies: nvlist, DSL dataset, DMU transaction forward declarations.

Research notes:
- Exposes both public entry points and check/sync pieces for DSL synctask execution.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_destroy.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_dir.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_dir.h

Read status: complete, 212 lines.

Purpose: DSL directory physical/in-core definitions and namespace/space-accounting APIs.

Key structures and APIs:
- Extensible ZAP fields include filesystem count, snapshot count, last remap TXG, and crypto key object.
- `dd_used_t` partitions used space into head, snapshots, children, child reservation, and refreservation.
- `dsl_dir_phys_t` stores head dataset object, parent/origin/children ZAP links, used/compressed/uncompressed bytes, quota/reservation, properties/delegation objects, flags, used breakdown, clones object, and padding.
- `dsl_dir_t` stores dbuf user, object, crypto object, pool, dbuf, dirty link, parent, lock, property callbacks, snapshot cmtime, origin txg, temporary reservations, expected dirty space, and name.
- APIs cover hold/release/name/create, space/stat getters, origin/count/remap TXG getters, stats export, available-space calculation, dirty/sync, temp reservations, will/did-use accounting, space transfer, quota/reservation setters, fs/snapshot limit activation/check/count adjust, last remap TXG update, rename, transfer feasibility, clone detection, refreservation updates, snapshot cmtime, zapification, and debug logging.

Important implementation constraints:
- `dd_parent` is protected by pool config lock.
- `dd_lock` protects property callbacks, snap cmtime, origin txg, temp reservations, expected dirty space, and name.
- Temporary reservations are per TXG.

Dependencies: DMU, DSL pool, DSL synctask, refcount, ZFS context, DSL crypto.

Research notes:
- DSL dirs are the namespace and hierarchical accounting layer above datasets.
- Reserved internal names include `$MOS`, `$ORIGIN`, `$FREE`, and `$LEAK`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_pool.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_pool.h

Read status: complete, 195 lines.

Purpose: DSL pool state and pool-wide sync/dirty-space/configuration APIs.

Key structures and APIs:
- Dirty-data tunables are declared as externs.
- `zfs_blkstat_t` and `zfs_all_blkstats_t` store block statistics by level and object type.
- `dsl_pool_t` stores SPA, meta objset, root/MOS/free/leak dirs, origin snapshot, taskqs, meta root block pointer, temporary userrefs object, free/bptree/empty/obsolete block pointer objects, scan state, dirty-space counters, MOS deltas, delayed transaction wakeup time, TXG state/lists, sync task queues, config rrwlock, and block stats.
- APIs cover init/open/close/create/sync/sync_done, sync-context detection, adjusted/unreserved space, dirty/undirty space, block free/free_sync, origin creation, clone upgrades, MOS/checkpoint space accounting, config lock enter/exit/held checks, dirty-delay decision, taskq access, user hold/release, tmp userref cleanup, special dir open, pool hold/release, and obsolete bpobj lifecycle.

Important implementation constraints:
- `dp_config_rwlock` protects administrative changes and is only write-held in syncing context.
- Dirty space is tracked per-TXG plus total.
- Sync tasks, early sync tasks, dirty datasets, dirty ZILs, and dirty dirs are TXG lists.

Dependencies: SPA, TXG internals, ZFS context, ZIO, dnode, DDT, ARC, bpobj, bptree, rrwlock, DSL synctask, MMP.

Research notes:
- This is the central coordination object for DSL syncing, dirty throttling, config locking, and pool-level deferred frees.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_pool.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_prop.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_prop.h

Read status: complete, 124 lines.

Purpose: DSL property lookup, inheritance, setting, and callback interface.

Key structures and APIs:
- `dsl_prop_changed_cb_t` callbacks receive a new integer value and must not call into DMU or DSL.
- `dsl_prop_record_t` tracks a property name and callback list under a dsl_dir.
- `dsl_prop_cb_record_t` links callback registrations to property records and datasets.
- Argument structs support property get/set synctasks.
- APIs initialize/finalize dsl_dir property state, register/unregister/notify callbacks, get properties by dataset name/dataset/dir, get all/received props, set properties through check/sync paths, set integer/string props, inherit props, predict inherited values, track received-properties availability, and add typed property values to nvlists.

Dependencies: DMU, DSL pool, ZFS context, DSL synctask.

Research notes:
- This header owns the inheritance/callback control plane for dataset properties.
- Callback restriction is important for avoiding recursive DSL/DMU entry.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_prop.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_scan.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_scan.h

Read status: complete, 190 lines.

Purpose: scrub/resilver/deferred-free scan state and control interface.

Key structures and APIs:
- `dsl_scan_phys_t` is the on-disk resumable scan state; all members are `uint64_t` for byteswap, and it includes function/state, queue object, TXG bounds, current pass bounds, times, byte progress, errors, DDT class/bookmark, traversal bookmark, and flags.
- Flags include dataset revisit and scrub paused.
- `dsl_scan_t` stores in-memory scan state: pool, restart/done TXGs, sync timing, deferred-free mode, async destroy flags, sorted scan flags, checkpoint/suspend state, root zio/taskq, prefetch controls/queue, per-TXG stats, cached physical state, dataset queue, and pending bytes.
- APIs cover module init/fini, pool scan init/fini/sync, scan cancel/start, vdev assessment, scrub/resilver status and pause/resume, resilver restart, dataset instability, DDT entry scanning, dataset destroyed/snapshotted/clone-swapped notifications, active/paused checks, freed-block notification, scan IO queue destroy, and vdev transfer.

Important implementation constraints:
- Most persistent scan progress is on disk so scans can resume after reboot/panic.
- In-memory state controls suspension, checkpointing, sorted sequential scan behavior, prefetching, and deferred-free traversal.
- `DSL_SCAN_FLAGS_MASK` persists only selected flags.

Dependencies: ZFS context, ZIO, DDT, bplist, pool/dataset/dmu_tx forward declarations.

Research notes:
- Ties together scrub, resilver, async destroy, DDT scanning, and deferred free handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_scan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_synctask.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_synctask.h

Read status: complete, 127 lines.

Purpose: DSL sync task framework definitions and space-check policy enum.

Key structures and APIs:
- Function typedefs define check, sync, and signal callbacks.
- `zfs_space_check_t` policies range from normal space checks through reserved/extra-reserved/destroy/channel-program checks to no-check/discard-checkpoint behavior.
- `dsl_sync_task_t` stores TXG list node, pool, TXG, expected space, space-check policy, check/sync funcs, arg, error, and no-waiter flag.
- APIs: `dsl_sync_task_sync()`, `dsl_sync_task()`, `dsl_sync_task_nowait()`, `dsl_early_sync_task()`, `dsl_early_sync_task_nowait()`, and `dsl_sync_task_sig()`.

Important implementation constraints:
- Space-check enum documents slop-space thresholds and why destructive operations may still need checks when checkpoints exist.
- Sync tasks separate preflight validation from syncing-context mutation.

Dependencies: TXG, ZFS context, DSL pool forward declaration, DMU transactions.

Research notes:
- This is the common framework behind many administrative DSL operations such as create, destroy, property set, and key changes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_synctask.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_userhold.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_userhold.h

Read status: complete, 57 lines.

Purpose: dataset user hold and release interface.

Key APIs:
- `dsl_dataset_user_hold()` applies named holds from an nvlist, with optional cleanup minor and error nvlist.
- `dsl_dataset_user_release()` releases named holds.
- `dsl_dataset_get_holds()` exports holds for a dataset.
- `dsl_dataset_user_release_tmp()` releases temporary holds for a pool.
- `dsl_dataset_user_hold_check_one()` and `dsl_dataset_user_hold_sync_one()` expose per-hold check/sync helpers.

Dependencies: nvpair/types, DSL pool/dataset and DMU transaction forward declarations.

Research notes:
- User holds prevent snapshot destruction; temporary holds are tied to cleanup minors.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_userhold.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/hkdf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/hkdf.h

Read status: complete, 29 lines.

Purpose: declares HKDF-SHA512 key derivation helper.

Key API:
- `hkdf_sha512()` derives an output key from key material, salt, info, and requested output length.

Dependencies: `sys/types.h`.

Research notes:
- Used by encryption/key derivation code paths.
- Header is intentionally minimal and does not expose implementation details.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/hkdf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/metaslab.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/metaslab.h

Read status: complete, 142 lines.

Purpose: metaslab allocation/free/class/group interface for SPA space allocation.

Key structures and APIs:
- `metaslab_ops_t` contains the allocation strategy callback `msop_alloc`.
- Global `zfs_metaslab_ops` points to active allocation operations.
- Per-metaslab APIs cover init/fini, unflushed TXG and estimated condensed size state, sorting by flushed status, memory used by unflushed changes, load/unload/flush, allocated-space query, sync/sync_done/reassess, and largest allocatable extent.
- Allocation flags include hint favor/avoid, gang header/child, async allocation, no throttle, must reserve, and fastwrite.
- Allocation/free/claim APIs include `metaslab_alloc()`, `metaslab_alloc_dva()`, `metaslab_free()`, `metaslab_free_concrete()`, `metaslab_free_dva()`, `metaslab_free_impl_cb()`, `metaslab_unalloc_dva()`, `metaslab_claim()`, `metaslab_claim_impl()`, and `metaslab_check_free()`.
- Stats/trace APIs initialize/finalize metaslab stats and allocation trace lists.
- Class APIs create/destroy/validate classes, verify histograms, report fragmentation/expandable/allocated/space/dspace/deferred values, throttle reserve/unreserve, and evict old metaslabs.
- Group APIs create/destroy/activate/passivate groups, check initialized state, query space/fragmentation, verify/remove histograms, decrement/verify allocation, recalculate weight/sort metaslabs, disable/enable metaslabs, and set selected TXG.
- `metaslab_space_update()` adjusts vdev/class space accounting.

Dependencies: SPA, space map, TXG, ZIO, AVL.

Research notes:
- This is the allocator-facing API that SPA/ZIO use to reserve, allocate, free, claim, and account DVAs.
- `metaslab_debug_load` is exported as a debug control.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/metaslab.h -->