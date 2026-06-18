# Group Research: group_517_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_z_ddb5b0e3d0b8

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is in subset A. All six listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_tx.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_tx.c

## Purpose

Implements DMU transaction construction, hold declaration, write/free/ZAP/bonus/spill/SA space accounting, pre-assignment I/O error probing, transaction-group assignment, dirty-data throttling waits, temporary quota/reservation enforcement, commit/abort callback handling, and debug validation that dirty buffers were covered by a declared hold.

## Main Entry Points

- `dmu_tx_create_dd()`, `dmu_tx_create()`, `dmu_tx_create_assigned()`: allocate normal or already-assigned transactions.
- `dmu_tx_hold_write()`, `dmu_tx_hold_write_by_dnode()`, `dmu_tx_hold_remap_l1indirect()`: declare write-side modifications and estimate space.
- `dmu_tx_hold_free()`, `dmu_tx_hold_free_by_dnode()`: declare range frees and preload indirect metadata needed by syncing.
- `dmu_tx_hold_zap()`, `dmu_tx_hold_zap_by_dnode()`, `dmu_tx_hold_bonus()`, `dmu_tx_hold_spill()`, `dmu_tx_hold_space()`: declare metadata, ZAP, bonus, spill, and raw space needs.
- `dmu_tx_hold_sa_create()`, `dmu_tx_hold_sa()`: declare System Attribute object, registry, layout, bonus, and spill effects.
- `dmu_tx_assign()`, `dmu_tx_wait()`: assign to an open txg or wait/retry when blocked by dirty data, suspended pool state, dnode txg ownership, quota, or ENOSPC pressure.
- `dmu_tx_commit()`, `dmu_tx_abort()`, `dmu_tx_callback_register()`, `dmu_tx_do_callbacks()`: finish transactions and invoke callbacks.

## Control Flow And State

Each hold is represented by `dmu_tx_hold_t` on `tx_holds`, optionally referencing a held `dnode_t` and carrying two refcount-style estimates: `txh_space_towrite` and `txh_memory_tohold`. Hold setup increments `dn_holds`; once a tx is assigned, dnodes also track `dn_assigned_txg` and `dn_tx_holds` so open-context mutations do not collide with the previous quiescing txg.

Write and free holds do more than account bytes. `dmu_tx_count_write()` and `dmu_tx_hold_free_impl()` deliberately read partial data blocks and relevant level-1 indirect blocks before assignment so I/O errors are discovered before callers modify DMU state. ZAP holds account worst-case microzap/fatzap mutation costs and may perform a lookup to force target leaf reads.

`dmu_tx_try_assign()` opens a txg, attaches all dnode holds, totals write and memory estimates, converts the write estimate through `spa_get_worst_case_asize()`, and asks the owning `dsl_dir` for a temporary reservation. It returns `ERESTART` for cases the caller can wait through: dirty-data throttle, suspended pool, or a dnode still assigned to the previous txg. `dmu_tx_unassign()` unwinds partially assigned dnodes and txg holds.

Dirty-data throttling uses `dmu_tx_delay()`, a tunable curve based on `zfs_dirty_data_max`, `zfs_delay_min_dirty_percent`, `zfs_delay_scale`, and `zfs_delay_max_ns`. `dmu_tx_wait()` chooses between dirty-space CV waits plus delay, txg sync waits, pool resume waits, and dnode `dn_notxholds` waits.

## Dependencies

Depends on dnode/dbuf locking and reference accounting, ZIO reads, txg hold/release APIs, DSL pool and directory reservation logic, ZAP lookup behavior, SA layout/registry objects, SPA failmode and dirty-data throttle state, and zfs_refcount debugging machinery.

## Risks

This file sits on a core correctness boundary: callers must declare enough holds before mutation, and assignment/unassignment must not leak dnode tx holds or txg holds. The pre-assignment reads are performance-sensitive but also fault-tolerance-sensitive. Dirty-data delay math assumes `dirty < zfs_dirty_data_max`. Debug hold validation in `dmu_tx_dirty_buf()` encodes subtle allowances for bonus/spill blocks, block-size changes, and new indirect levels.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_tx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_zfetch.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_zfetch.c

## Purpose

Implements ZFS predictive prefetch stream tracking for dnodes. It detects sequential block access patterns, maintains per-dnode zfetch streams, issues speculative data and indirect-block prefetches, limits stream count and prefetch distance, and exports kstats for hit/miss and completion timing.

## Main Entry Points

- `zfetch_init()` / `zfetch_fini()`: create and destroy the `zfetchstats` kstat.
- `dmu_zfetch_init()` / `dmu_zfetch_fini()`: initialize and tear down a dnode's `zfetch_t`.
- `dmu_zfetch()`: predictive prefetch entry point called on block access.
- Internal helpers: `dmu_zfetch_stream_create()`, `dmu_zfetch_stream_remove()`, `dmu_zfetch_stream_orphan()`, `dmu_zfetch_stream_done()`.

## Control Flow And State

`dmu_zfetch()` exits immediately when predictive prefetch is disabled, indirect vdev mappings are not loaded, the access is the first block without the caller already holding the structure lock, or the file is too small to benefit. It then searches existing streams for an access that matches the expected next block, accepting either the exact next block or the previous prefetched block when alignment causes overlap.

A miss creates a new stream if the per-dnode stream limit allows it. Stream creation also reaps idle streams older than `zfetch_min_sec_reap`, unless they still have outstanding prefetch references. The effective max stream count is capped for small files so streams can plausibly be non-overlapping.

On a hit, the stream doubles its data prefetch distance up to `zfetch_max_distance` and separately doubles indirect prefetch distance up to `zfetch_max_idistance`. It updates stream block cursors under `zs_lock`, adds a reference count for expected async completions, drops zfetch locks, then issues `dbuf_prefetch_impl()` calls for level-0 data and level-1 indirect blocks. Completion callbacks update timing kstats and free orphaned streams once outstanding prefetches finish.

## Dependencies

Depends on dnode structure locks, dbuf prefetch, SPA indirect-vdev readiness, list/rwlock/mutex primitives, zfs_refcount for outstanding async prefetches, and kstat counters.

## Risks

The logic is concurrency-heavy despite being performance-oriented. Streams can outlive their parent zfetch structure, so orphaning and completion refcounts must stay balanced. The function intentionally drops locks before issuing prefetch I/O; stale stream state is handled by locked rechecks. Tunables directly affect wasted I/O versus sequential-read benefit.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_zfetch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dnode.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dnode.c

## Purpose

Implements in-core dnode lifecycle and open-context dnode operations: cache construction/destruction, byteswapping, allocation/reallocation, movable dnode support, dnode handle/slot management, object lookup and claiming, dirty marking, block-size and indirection changes, range-free tracking, used-space accounting, dbuf eviction, and sparse/hole/data scanning.

## Main Entry Points

- `dnode_init()` / `dnode_fini()`: create/destroy the `dnode_t` kmem cache and dnode kstats.
- `dnode_allocate()`, `dnode_reallocate()`, `dnode_free()`: allocate, reshape, or mark dnodes for freeing.
- `dnode_hold_impl()`, `dnode_hold()`, `dnode_try_claim()`, `dnode_add_ref()`, `dnode_rele()`: find, instantiate, claim, reference, and release dnodes.
- `dnode_setdirty()`: place a dnode on the objset dirty list and dirty its containing dbuf.
- `dnode_set_blksz()`, `dnode_set_nlevels()`, `dnode_new_blkid()`: update block geometry and top-level indirection state.
- `dnode_free_range()`, `dnode_block_freed()`: record block ranges to free in the syncing phase and query recent frees.
- `dnode_evict_dbufs()`, `dnode_evict_bonus()`: evict cached dbufs for a dnode.
- `dnode_next_offset()`: find next/previous hole, data, or sparse dnode-region offset.

## Control Flow And State

The file separates persistent `dnode_phys_t` from mutable in-core `dnode_t`. `dnode_create()` copies geometry/type/checksum/compression/bonus/spill state from disk, initializes zfetch, links regular objects into `os_dnodes`, and then publishes `dn_objset` as the final step so the kernel dnode-move callback sees only fully initialized dnodes. `dnode_destroy()` invalidates the pointer, unlinks from the objset, destroys bonus/zfetch state, handles objset eviction completion, and returns ARC metadata space.

Dnode slots are tracked per dnode block using `dnode_children_t` and one `dnode_handle_t` per slot. Handles can be `DN_SLOT_FREE`, `DN_SLOT_ALLOCATED`, `DN_SLOT_INTERIOR`, `DN_SLOT_UNINIT`, or an actual dnode pointer. `dnode_hold_impl()` initializes this state from the meta-dnode block, handles multi-slot dnodes, supports dry-run free claims, rejects interior-slot lookups, and carefully coordinates handle locks with the parent dbuf reference so instantiated dnodes cannot move or disappear.

Dirty state is txg-indexed. Open-context mutations store pending next values in `dn_next_*[txg & TXG_MASK]` and dirty the dnode for later syncing. Range frees are recorded in `dn_free_ranges[]` as block-id range trees after partial head/tail blocks are zeroed and relevant level-1 indirect dbufs are dirtied. This lets open context mark intent while syncing context later mutates block pointers and frees space.

`dnode_next_offset()` climbs up and down the block tree using fill counts to locate matching holes/data, with special handling for meta-dnode object allocation scans and the virtual hole at object end. It reads indirect blocks with `DB_RF_NO_DECRYPT` because dnode metadata inspection does not require decrypted payload.

The kernel-only dnode move path allows kmem to relocate inactive dnodes. It holds objset and dnode-handle locks, verifies active holds are no more than dbuf-owned holds, transfers dirty records, dbuf AVL entries, zfetch streams, handles, and back-pointers, then invalidates the old object.

## Dependencies

Depends on dbuf cache internals, dmu objset state, txg-indexed dirty lists, range trees, zfetch, ARC space accounting, SPA feature limits for large dnodes and block sizes, user/group/project accounting helpers, and zrl locks used by dnode handles.

## Risks

This is one of the most delicate files in the ZFS DMU. Correctness depends on exact ordering between dnode holds, parent dbuf holds, handle locks, dbuf AVL mutations, and dirty-list membership. Multi-slot dnode allocation must keep interior slots consistent with on-disk `dn_extra_slots`. Range-free tracking must dirty enough indirect metadata without instantiating dbufs that `dbuf_free_range()` assumes absent. Dnode moving is particularly sensitive to stale back-pointers and active reference misclassification.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dnode_sync.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dnode_sync.c

## Purpose

Implements syncing-context dnode writeback and block freeing. It applies pending dnode geometry/type/bonus/spill/maxblkid changes, increases indirection, frees block-pointer ranges recorded by open context, updates used-space accounting, evicts or undirties dbufs when freeing objects, activates large-dnode features, and drives child dbuf sync.

## Main Entry Points

- `dnode_sync()`: primary syncing-context entry for one dirty dnode.
- `dnode_increase_indirection()`: creates a new top indirect level and reparents cached children.
- `dnode_sync_free_range_impl()` / `dnode_sync_free_range()`: free recorded logical block ranges.
- `free_blocks()`, `free_children()`: kill dataset block pointers and recurse through indirect blocks.
- `dnode_sync_free()`: finish freeing an entire dnode.
- `dnode_evict_dbufs()`, `dnode_evict_bonus()`: evict cache state used by sync/free paths.
- `dnode_undirty_dbufs()`: drop dirty records for a dnode being freed.

## Control Flow And State

`dnode_sync()` starts by applying accounting flags and newly allocated dnode physical fields. It consumes txg-indexed pending fields from `dn_next_type`, `dn_next_blksz`, `dn_next_bonuslen`, `dn_next_bonustype`, `dn_next_indblkshift`, `dn_next_maxblkid`, and `dn_next_nblkptr`. Spill blocks are removed if explicitly requested or if the dnode is being freed.

Free ranges recorded in `dn_free_ranges[txgoff]` are walked before being vacated and destroyed. `dnode_sync_free_range_impl()` bounds the range to the persistent `dn_maxblkid`, recurses through indirect blocks, kills leaf block pointers with `dsl_dataset_block_kill()`, preserves hole birth metadata when the `hole_birth` feature is active, and optionally frees indirect blocks immediately when the entire dnode is being removed. For ordinary range frees, indirect blocks are usually left to later dbuf write logic so hole birth times are not lost when frees and writes target the same indirect block in one txg.

If a dnode needs more levels, `dnode_increase_indirection()` reads/releases the new top indirect block, copies old root block pointers into it, zeros the old root pointers, and reparents cached child dbufs to the new indirect. It observes dbuf lock ordering by finding children before holding the new parent's `db_rwlock`.

After pending structural changes and range frees, `dnode_sync()` writes dirty child dbufs with `dbuf_sync_list()`. If the dnode is being freed, `dnode_sync_free()` verifies all used bytes are gone, undirties records, evicts dbufs, zeros the physical dnode slots, frees interior slots, resets in-core type/maxblkid/free state, and releases the dirty hold.

## Dependencies

Depends on dbuf dirty records and sync, dataset deadlist/block-kill accounting, ZIO txg sync flow, ARC released buffers, range trees, dnode dirty state produced by `dnode.c`, SPA features `hole_birth` and `large_dnode`, and user accounting state in objsets.

## Risks

The file mutates persistent block pointers while syncing, so ordering is critical: free ranges must be processed before maxblkid updates, and indirection changes must happen before child dbuf sync. Freeing indirects is intentionally restricted because freeing and rewriting the same indirect block in one txg can otherwise lose hole birth metadata. Raw receive bypasses normal maxblkid truncation to preserve source-side cryptographic hashes. The `range_tree_walk()` plus later `range_tree_vacate()` pattern is deliberate because the callback drops `dn_mtx`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dnode_sync.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_bookmark.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_bookmark.c

## Purpose

Implements ZFS bookmark lookup, creation, listing, and destruction in the DSL layer. Bookmarks are per-dataset ZAP entries that record a snapshot GUID, creation txg, creation time, and, for newer encrypted datasets, an IV-set GUID used by raw send/receive validation.

## Main Entry Points

- `dsl_bookmark_lookup()`: resolve `dataset#bookmark`, fetch bookmark physical data, and optionally verify timeline ancestry.
- `dsl_bookmark_create()`: batch create bookmarks through a sync task.
- `dsl_get_bookmarks()` / `dsl_get_bookmarks_impl()`: list bookmarks and requested properties.
- `dsl_bookmark_destroy()`: batch destroy bookmarks through a sync task.
- Internal helpers: `dsl_bookmark_hold_ds()`, `dsl_dataset_bmark_lookup()`, `dsl_dataset_bookmark_remove()`.

## Control Flow And State

`dsl_bookmark_hold_ds()` parses a full bookmark name around `#`, validates the bookmark component with `zfs_component_namecheck()`, and holds the containing dataset. Case-insensitive datasets use normalized ZAP lookup/removal.

Creation checks that the target source is a snapshot, the destination bookmark filesystem exists, the destination is in the snapshot's timeline, and the bookmark does not already exist. Sync creates the per-dataset bookmark ZAP lazily, increments `SPA_FEATURE_BOOKMARKS`, zapifies the dataset to store `DS_FIELD_BOOKMARK_NAMES`, writes a `zfs_bookmark_phys_t`, and logs history. For encrypted snapshots with bookmark-v2 support and a present `DS_FIELD_IVSET_GUID`, it stores the larger v2 record and increments `SPA_FEATURE_BOOKMARK_V2`.

Listing iterates the bookmark ZAP and emits only requested properties: GUID, createtxg, creation time, and IV-set GUID. Destroy treats nonexistent datasets/bookmarks as already destroyed, records successes in a temporary nvlist during check, removes entries in sync, decrements bookmark-v2 when removing larger entries, and destroys the bookmark ZAP plus feature reference when the last bookmark is removed.

## Dependencies

Depends on DSL dataset/dir holds, MOS ZAP objects, normalized ZAP operations for case-insensitive datasets, sync tasks, SPA feature reference counts, encryption IV-set metadata, property nvlist helpers, and name validation.

## Risks

Batch operations intentionally collect per-bookmark errors while returning an aggregate failure. Feature reference counts must match creation/destruction of bookmark ZAPs and v2-sized entries. Timeline validation via `dsl_dataset_is_before()` is required so bookmarks cannot be used as unrelated send origins. Older shorter bookmark records are supported by zeroing the output structure before lookup.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_bookmark.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_crypt.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_crypt.c

## Purpose

Manages ZFS native encryption state in the DSL and SPA keystore. It handles wrapping keys, decrypted DSL crypto keys, dataset-to-key mappings, key load/unload/change-key workflows, encryption-root inheritance, clone/promote/rename constraints, encrypted dataset creation, raw encrypted receive/send key nvlists, key ZAP object lifecycle, keystatus/stat reporting, and block/object-set encryption MAC operations.

## Main Entry Points

- Crypto parameter handling: `dsl_crypto_params_create_nvlist()`, `dsl_crypto_params_free()`.
- Keystore lifecycle: `spa_keystore_init()`, `spa_keystore_fini()`.
- Wrapping-key operations: `spa_keystore_load_wkey()`, `spa_keystore_unload_wkey()`, `spa_keystore_load_wkey_impl()`, `spa_keystore_unload_wkey_impl()`.
- Key mapping operations: `spa_keystore_create_mapping()`, `spa_keystore_remove_mapping()`, `spa_keystore_lookup_key()`, `key_mapping_add_ref()`, `key_mapping_rele()`.
- Key changes: `spa_keystore_change_key_check()`, `spa_keystore_change_key_sync()`, `spa_keystore_change_key()`.
- Dataset rules: `dsl_crypto_can_set_keylocation()`, `dsl_dir_rename_crypt_check()`, `dsl_dataset_promote_crypt_check()`, `dsl_dataset_promote_crypt_sync()`, `dmu_objset_create_crypt_check()`, `dsl_dataset_create_crypt_sync()`.
- Raw receive/send: `dsl_crypto_recv_raw()`, `dsl_crypto_recv_key_check()`, `dsl_crypto_recv_key_sync()`, `dsl_crypto_recv_raw_objset_check()`, `dsl_crypto_recv_raw_objset_sync()`, `dsl_crypto_recv_raw_key_check()`, `dsl_crypto_recv_raw_key_sync()`, `dsl_crypto_populate_key_nvlist()`.
- DSL key objects and crypto operations: `dsl_crypto_key_create_sync()`, `dsl_crypto_key_clone_sync()`, `dsl_crypto_key_destroy_sync()`, `dsl_dataset_crypt_stats()`, `spa_crypt_get_salt()`, `spa_do_crypt_objset_mac_abd()`, `spa_do_crypt_mac_abd()`, `spa_do_crypt_abd()`.

## Control Flow And State

The SPA keystore has three AVL trees guarded by separate rwlocks: loaded wrapping keys keyed by encryption-root dsl_dir object, decrypted DSL crypto keys keyed by key ZAP object, and dataset-object mappings to crypto keys. Wrapping keys represent user-supplied keys and carry keyformat/salt/iters metadata. DSL crypto keys hold unwrapped master/HMAC key material and reference their wrapping key. Dataset mappings let ZIO/ARC look up a loaded key by objset id during I/O.

`dsl_crypto_params_create_nvlist()` parses encryption properties and ioctl crypto arguments, validates crypt/keyformat/keylocation/wrapping-key length, normalizes `encryption=on`, creates a wrapping key when raw key data is supplied, and removes encryption-only properties from the ordinary DSL property nvlist. Free paths zero and release key buffers when ownership is transferred with `unload`.

Loading a key validates the supplied wrapping key by opening and unwrapping the on-disk DSL crypto key ZAP, then initializes keyformat/salt/iters from disk and inserts the wrapping key. Unloading waits for txg I/O to finish, then removes a wrapping key only if its refcount is zero. Opening a DSL crypto key reads crypt suite, GUID, encrypted master key, encrypted HMAC key, IV, MAC, and optional version from the key ZAP, unwraps through `zio_crypt_key_unwrap()`, and caches the result.

Change-key sync recurses through children and clone references with `spa_keystore_change_key_sync_impl()`. It either rewrites the recorded encryption root object or rewraps each affected DSL crypto key with a new wrapping key. Forced variants update encryption-root metadata without requiring loaded keys. Normal variants require relevant keys loaded so data remains accessible and wrapped correctly.

Dataset creation either inherits a parent's wrapping key or creates a new encryption root. Clones share the origin's key object by incrementing the key ZAP refcount. Promotion can move encryption-root identity from origin to target when safe, copying keylocation and updating descendant crypto key root references. Rename checks prevent moving non-root encrypted datasets under a different encryption root.

Raw encrypted receive validates metadnode geometry, portable MAC, raw key nvlist fields, key version, keyformat/PBKDF2 consistency, and IV-set GUID continuity for incrementals unless `zfs_disable_ivset_guid_check` is set. Sync can create or update a raw objset, set raw write flags and object-set MACs, write raw key material exactly as provided, and activate encryption. `dsl_crypto_populate_key_nvlist()` exports the raw key ZAP fields plus metadnode properties and from/to IV-set GUIDs for raw send.

The bottom crypto helpers perform salt lookup, object-set MAC generation/verification, generic data MAC generation/verification, and encryption/decryption dispatch. `spa_do_crypt_abd()` borrows ABD buffers, obtains the dataset key mapping, generates random or dedup-derived salt/IV when encrypting, calls `zio_do_crypt_data()`, handles decryption fault injection except for dnode blocks, and carefully returns ABD buffers and key references on both success and error.

## Dependencies

Depends on DSL dataset/dir structures, MOS ZAP key objects, DSL properties, sync tasks, SPA feature flags, txg synchronization, zio crypto primitives, ABD buffer APIs, objset physical MAC fields, zvol hooks, raw receive machinery, nvlist helpers, and zfs_refcount/AVL/rwlock primitives.

## Risks

This file protects key material and must maintain exact reference lifetimes across three trees. Lock ordering around `sk_wkeys_lock`, `sk_dk_lock`, and `sk_km_lock` matters because I/O paths perform key lookup under reader locks. Key changes recurse through dataset trees and clone lists, so missed descendants would leave stale wrapping-root metadata. Raw receive is compatibility-sensitive: IV-set GUID checks, key version checks, metadnode geometry, and portable MACs must match send-side expectations. Error paths must zero generated salt/IV/MAC state and return ABD buffers correctly. The raw objset check contains a duplicated IV-set GUID validation block, which is behaviorally redundant but worth noting for maintenance.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_crypt.c -->