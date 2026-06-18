# Research: subset-b-008159

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_pool.c -->
# sources/object-store/daos/src/vos/tests/vts_pool.c

## Purpose
`vts_pool.c` is a cmocka test suite for the VOS pool lifecycle API. It validates pool creation against both pre-existing fallocated files and empty generated files, open/close/refcount behavior, destroy rules, pool query space accounting, exclusive-open locking, and data-format version compatibility. The tests exercise the same public VOS entry points used by higher VOS tests, but keep the scope at pool handles and pool metadata rather than object/container I/O.

## Important APIs, Types, And Functions
The central test fixture is `struct vp_test_args`, which owns generated pool filenames, operation sequences, create-mode flags, pool handles, and UUIDs. `pool_allocate_params()` allocates per-file operation arrays, handle slots, and UUID storage. `pool_set_param()` installs a sequence of `enum vts_ops_type` operations such as `CREAT`, `CREAT_OPEN`, `OPEN`, `CLOSE`, `DESTROY`, and `QUERY`.

`pool_ops_run()` is the generic executor. It dispatches operation sequences to `vos_pool_create_ex()`, `vos_pool_create()`, `vos_pool_open()`, `vos_pool_close()`, `vos_pool_destroy()`, and `vos_pool_query()`, then asserts expected zero returns and query invariants. The non-generic tests are `pool_ref_count_test()`, `pool_interop()`, `pool_open_excl_test()`, and `pool_interop_create_old()`.

## Control Flow
Each cmocka case starts with the common `setup()` allocation, a case-specific setup that builds the operation sequence, then either `pool_ops_run()` or a dedicated test body. `create_pools_test_construct()` creates one pool per CPU up to 16, so the create paths get light parallel-environment coverage without over-consuming bdev/aio file space. `pool_unit_teardown()` walks every configured pool, kills unfinished VOS pools via `vos_pool_kill()` if the sequence did not destroy them, removes files, and frees all arrays.

The lifecycle matrix covers create-only, create/open/close, create/destroy, create/open/query/close/destroy, create-open combined handle return, and fallocated versus generated-file backing. `pool_open_excl_test()` repeatedly recreates a pool to test all meaningful `VOS_POF_EXCL` conflicts: exclusive open with an existing opener, two exclusive openers, normal open with an exclusive opener, and create-open with exclusive flags.

## State And Persistence Behavior
The file is primarily concerned with durable pool metadata and handle state. It verifies that open handles hold a reference that makes `vos_pool_destroy()` return `-DER_BUSY` until all handles are closed. `pool_ops_run()` checks `vos_pool_query()` immediately after open: no containers, SCM total equal to `VPOOL_256M`, no NVMe space, free SCM below the raw total by at least `struct vos_pool_df`, and no NVMe free space.

WAL sizing is explicit for `vos_pool_create_ex()` through `VPOOL_TEST_WAL_SZ`, a 32 MiB WAL cluster-sized value. The tests do not replay WAL contents, but they ensure pool creation succeeds with WAL space in both fallocated and generated-file modes. `pool_interop()` and `pool_interop_create_old()` exercise persistent data-format version checks using fault injection and explicit version parameters.

## Dependencies And Integration Points
The suite depends on `vts_common.h` helpers for filename generation, fallocation, file existence checks, and `enum vts_ops_type`. It uses DAOS allocation/logging macros, UUID generation, cmocka assertions, and VOS internals from `vos_layout.h`, `daos_srv/vos.h`, and `vos_internal.h`. It also depends on fault-injection controls (`FAULT_INJECTION_REQUIRED()`, `daos_fail_loc_set()`) for interoperability cases.

`run_pool_test()` is the integration point registered with the broader VOS test runner. It formats a suite name with `dts_create_config()` and runs the `pool_tests` array under group setup/teardown.

## Risks And Edge Cases
Resource cleanup is important because unfinished pools can leave SMD_DEV/blob state; teardown calls `vos_pool_kill()` when the operation sequence did not finish with `DESTROY`. The operation executor assumes non-`QUERY` operations all succeed, so it is intentionally a positive-path matrix rather than a negative API validation suite. `create_pools_test_construct()` scales file count to CPU count, which improves coverage but can make failures dependent on local storage limits; the hard cap of 16 mitigates that.

The version tests require fault injection and may be skipped or invalid if fault injection is unavailable. The exclusive-open test reuses one UUID across repeated create/destroy cycles after regeneration once, relying on destroy to leave the pool path reusable.

## Test Signals
Primary pass signals are cmocka return codes from `run_pool_test()`. Useful behavioral assertions include `-DER_BUSY` for destroy with outstanding handles, `-DER_DF_INCOMPT` for injected incompatible pool format open, `-DER_INVAL` for too-old create version, successful open of `VOS_POOL_DF_2_4`, and `-DER_BUSY` for every exclusive-open conflict. Query assertions provide a regression signal for pool space accounting.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_tree.c -->
# sources/object-store/daos/src/vos/tests/vts_tree.c

## Purpose
`vts_tree.c` is a focused cmocka unit test for a VOS tree helper: `vos_irec_is_valid()`. It verifies the helper's NULL handling and DTX-local-ID matching behavior for internal record structures.

## Important APIs, Types, And Functions
The test uses `struct vos_irec_df`, specifically the `ir_dtx` field, and calls `vos_irec_is_valid(const struct vos_irec_df *, uint32_t)`. It defines `DTX_LID_VALID` and `DTX_LID_INVALID`, plus two static record fixtures: `valid` and `invalid_dtx_lid`.

`vos_irec_is_valid_test()` is the only test body. `tree_tests_all` registers it as `VOS1100: vos_irec_is_valid`, and `run_tree_tests()` invokes cmocka for the `tree` suite.

## Control Flow
The suite has no setup or teardown. It calls the helper three times: with a NULL record, with a non-NULL record whose `ir_dtx` differs from the caller's DTX local ID, and with a matching record. The expected results are false, false, and true.

## State And Persistence Behavior
There is no durable state, allocation, or tree mutation in this file. It is a pure unit check around interpretation of an in-memory VOS record descriptor. The persistence relevance is indirect: `vos_irec_is_valid()` is part of validating tree records that may be stored in persistent VOS layouts, so rejecting NULL or wrong-DTX records protects callers from treating unrelated on-media state as usable.

## Dependencies And Integration Points
The file includes cmocka headers and `vos_internal.h`, so it intentionally tests an internal helper rather than a public VOS API. `run_tree_tests()` is the external entry point used by the VOS test harness.

## Risks And Edge Cases
The coverage is intentionally narrow. It does not test boundary DTX IDs, special sentinel values, or records with other fields populated. Its value is as a regression tripwire for the exact validity predicate, especially NULL safety and equality against the supplied local DTX ID.

## Test Signals
A passing suite confirms that `vos_irec_is_valid(NULL, lid)` is false, a mismatched `ir_dtx` is false, and a matched `ir_dtx` is true. Any semantic change to the helper should be accompanied by updating this test because the expected truth table is explicit.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_ts.c -->
# sources/object-store/daos/src/vos/tests/vts_ts.c

## Purpose
`vts_ts.c` tests VOS timestamp-set caching and the generic LRU array implementation used underneath it. It validates positive and negative timestamp cache entries across VOS timestamp types, eviction and reuse semantics, multi-level LRU array behavior, callback ordering, and stress behavior under deterministic pseudo-random allocation/eviction.

## Important APIs, Types, And Functions
`struct ts_test_arg` owns a temporary `vos_ts_set`, old global timestamp table, per-type record arrays, and count metadata copied from `vos_ts_table`. Timestamp tests call `vos_ts_table_alloc()`, `vos_ts_table_get()`, `vos_ts_table_set()`, `vos_ts_set_allocate()`, `vos_ts_set_reset()`, `vos_ts_lookup()`, `vos_ts_alloc()`, `vos_ts_get_negative()`, `vos_ts_evict()`, and `vos_ts_set_free()`.

The LRU tests use `lrua_array_alloc()`, `lrua_alloc()`, `lrua_allocx_inplace()`, `lrua_lookup()`, `lrua_lookupx()`, `lrua_evict()`, `lrua_evictx()`, `lrua_array_aggregate()`, and `lrua_array_free()`. `struct lru_record` embeds magic fields and a pointer back to an `index_record`; callbacks `on_entry_init()`, `on_entry_evict()`, and `on_entry_fini()` verify lifecycle transitions.

## Control Flow
`run_ts_tests()` runs four cmocka cases. `lru_array_test()` fills a single LRU array past capacity, verifies only the newest entries remain, touches one older surviving entry to protect it from eviction, then explicitly evicts it. `lru_array_stress_test()` repeatedly inserts and evicts under patterned frequencies, then runs a deterministic random sequence and a callback lookup scenario that targets a historical eviction bug. `lru_array_multi_test()` runs the same iteration against a multi-level array, aggregates it, and tests extended key lookup with inplace entries.

`ilog_test_ts_get()` first calls `run_positive_entry_test()` for every `VOS_TS_TYPE_*`. Positive tests allocate entries, verify lookups return identical objects, ensure parent type lookup before child allocation, and test LRU eviction/reuse. It then evicts all entries from child to parent order and runs `run_negative_entry_test()` to validate negative cache behavior, including special type-zero allocation and misses for all previous records.

## State And Persistence Behavior
The timestamp table and LRU arrays are in-memory acceleration structures, not persistent storage. State correctness matters because VOS incarnation-log and timestamp lookup paths can make decisions based on cached entries. The tests verify `ts_init_count` progression, type-specific capacities, parent-child lookup dependencies, LRU replacement, negative entry reuse after reset, and that evicted entries become unavailable until reallocated.

The LRU callback tests use magic values to ensure initialized records remain intact and evicted/finalized records update their source `index_record` to `MAGIC1`. Multi-level aggregation verifies that array compaction does not lose lookup or eviction semantics.

## Dependencies And Integration Points
The file integrates with `vts_io.h`, `vos_internal.h`, `vos_ts.h`, DAOS allocation/assertion utilities, DTX ID generation (`daos_dti_gen_unique()`), and the cmocka VOS test runner. It temporarily replaces the process-global timestamp table and restores it in `ts_test_fini()`, so it depends on proper isolation from other tests.

## Risks And Edge Cases
The largest local risk is memory pressure: `VOS_TS_SIZE` is 8 MiB per timestamp type of `uint32_t` records, plus the `BIG_TEST` stress allocation. The stress test fixes `srand(1)` because arbitrary seeds can fail this deterministic expectation suite. The timestamp tests assume the table's per-type counts are large enough for `NUM_EXTRA` and index 20 access. Global table replacement must always restore `old_table`; setup failure paths free only partially initialized state.

## Test Signals
Passing signals include exact LRU capacity retention, callback-driven magic transitions, safe lookup from inside eviction callbacks, successful multi-level `lrua_array_aggregate()`, correct extended-key misses/hits, timestamp `ts_init_count` expectations, positive lookup identity, negative lookup misses, and correct object reuse after explicit `vos_ts_evict()`.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_wal.c -->
# sources/object-store/daos/src/vos/tests/vts_wal.c

## Purpose
`vts_wal.c` is the VOS-level WAL recovery test suite for metadata-on-SSD mode. It validates pool/container WAL replay, external checkpoint behavior, object update/fetch recovery across reopen, replay and checkpoint fault handling, key query/punch/update replay, metadata-bucket allocation/reclamation after restart, and phase-2 evictable bucket accounting.

## Important APIs, Types, And Functions
`struct wal_test_args` owns a cloned pool image and a 32 MiB copy buffer used by `save_pool()` and `restore_pool()` to simulate restart from a pre-operation VOS file while relying on WAL or checkpointed metadata blobs. The suite uses VOS pool/container APIs (`vos_pool_create()`, `vos_pool_open()`, `vos_pool_close()`, `vos_pool_destroy()`, `vos_cont_create()`, `vos_cont_open()`, `vos_cont_close()`, `vos_cont_destroy()`, `vos_pool_query()`), checkpoint APIs (`vos_pool_checkpoint_init()`, `vos_pool_checkpoint()`, `vos_pool_checkpoint_fini()`), object APIs (`vos_obj_update()`, `vos_obj_fetch()` through test helpers, `vos_obj_query_key()`, `vos_obj_punch()`), and aggregation (`vos_aggregate()`) for reclaim tests.

The memory-bucket portion exercises `umem_allot_mb_evictable()`, `umem_alloc_from_bucket()`, `umem_alloc()`, `umem_free()`, `umem_atomic_free()`, `umem_heap_gc()`, `umempobj_get_mbusage()`, `umempobj_get_heapusage()`, cache pin/unpin APIs, and page-cache statistics.

## Control Flow
`run_wal_tests()` first skips all tests unless `bio_nvme_configured(SMD_DEV_TYPE_META)` reports metadata-on-SSD support. It then runs pool/container WAL tests, basic single/extent-value I/O tests, object-type matrix I/O tests over `type_list`, an interrupt query/punch test for multi-uint64 objects, and memory-bucket tests when the backend is `DAOS_MD_BMEM_V2`.

The core recovery flow is repeated throughout: mutate VOS state, optionally checkpoint, close the pool, optionally set fault injection, reopen with `VOS_POF_EXTERNAL_CHKPT`, and then verify pool info, container handles, fetched object values, query-key results, or allocator accounting. `wal_pool_refill()` encapsulates close/reopen/refetch comparisons for object I/O tests and handles no-replay, fail-replay, checkpoint, and fail-checkpoint modes.

The later P2 and MB tests deliberately fill non-evictable and evictable memory buckets, free selected percentages, run GC, checkpoint during bulk allocation, reopen, and validate bucket reuse, MB usage accounting, page load/evict/miss stats, and object bucket IDs.

## State And Persistence Behavior
This file is heavily persistence-oriented. Pool cloning/restoration in `wal_tst_pool_cont()` clears local tmpfs-style state after WAL-producing operations, proving that container creation can be recovered from WAL replay. When checkpointing is enabled with `DAOS_WAL_NO_REPLAY`, tests prove checkpointed metadata alone is sufficient. `compare_pool_info()` checks container count, SCM/NVMe totals and free space, and VEA attributes before and after recovery.

Object tests cover small and large single values and extents, zero-copy modes, overwrite mode, many keys, many objects, and record-extent mode. The memory-bucket tests validate persistence of bucket IDs, usage counters, free-list reuse, spill-over evictable buckets, NEMB percentage configuration fixed at pool creation time, and post-restart page-cache behavior.

## Dependencies And Integration Points
The suite depends on VOS test helpers from `vts_io.h`, DAOS object type/key helpers, BIO/NVMe configuration, fault injection, DAOS environment variables (`DAOS_NEMB_EMPTY_RECYCLE_THRESHOLD`, `DAOS_MD_ON_SSD_NEMB_PCT`), VOS internals for handle-to-pool/container conversion, UMEM internals, and aggregation/GC helpers. It directly verifies integration among VOS, BIO WAL, metadata blobs, VEA space accounting, UMEM heap/cache, and the object tree layer.

## Risks And Edge Cases
The suite is storage-intensive: some setups allocate 1-2 GiB logical pool/blob sizes and run 10K-key loops. It is conditionally skipped outside MD-on-SSD mode, so non-MD-on-SSD CI does not exercise it. Fault-injection cases require FI support. The MB tests make detailed assumptions about bucket size, reserved non-evictable counts, backend type, page-cache stats, and GC timing; they include repeated GC calls and checkpoint intervals to reduce timing sensitivity.

Several tests rely on exact allocator preference ordering by utilization bands and exact cache stat increments after reopen/fetch. These are high-value regression signals but may need deliberate updates if allocator policy changes.

## Test Signals
Important pass signals include successful recovery with and without WAL replay, identical `vos_pool_info_t` before/after reopen, correct fetch data after restart for small/large SV/EV records, replay interruption returning `-DER_AGAIN` followed by successful retry, checkpoint failure returning `-DER_AGAIN`, query-key max dkey shifting after punch and back after update, MB usage equality across restart, free-block reuse after replay/checkpoint, and P2 bucket space returning to initial values after aggregation and GC.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_wal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/wal_ut.c -->
# sources/object-store/daos/src/vos/tests/wal_ut.c

## Purpose
`wal_ut.c` is a lower-level BIO WAL unit test suite. It bypasses VOS object operations and constructs fake `umem_wal_tx` transactions to validate WAL reserve, commit, replay, checkpoint, wraparound, large payload, multi-block transaction, and replay-hole behavior against BIO metadata contexts.

## Important APIs, Types, And Functions
`ut_mc_init()` and `ut_mc_fini()` create/open and close/destroy a BIO metadata context through `bio_mc_create()`, `bio_mc_open()`, `bio_mc_close()`, and `bio_mc_destroy()`. `struct ut_fake_tx` stores generated `umem_action` arrays, payload buffer, action indexes, payload size, and copy-pointer sizing. `ut_fake_wal_tx_ops` supplies `wtx_act_nr`, `wtx_payload_sz`, `wtx_act_first`, and `wtx_act_next` so `bio_wal_commit()` can serialize the fake transaction as if it came from UMEM.

`ut_tx_add_action()` generates `UMEM_ACT_COPY`, `UMEM_ACT_COPY_PTR`, `UMEM_ACT_ASSIGN`, `UMEM_ACT_MOVE`, `UMEM_ACT_SET`, `UMEM_ACT_SET_BITS`, and `UMEM_ACT_CLR_BITS` actions. `ut_replay_one()` validates replayed actions byte-for-byte, normalizing `COPY_PTR` replay to a `COPY` action with embedded payload. `ut_tx_array` and `ut_replay_multi()` track ordered replay of many transactions.

## Control Flow
Each test creates a 128 MiB meta/WAL/data context, commits one or more fake transactions with `bio_wal_reserve()` and `bio_wal_commit()`, closes and reopens the metadata context, then calls `bio_wal_replay()` with a validation callback. `wal_ut_single()` covers all supported action types. `wal_ut_many_acts()` sizes a transaction to span two and a half WAL blocks. `wal_ut_large_payload()` commits multiple 1 MiB copy-pointer payloads.

`wal_ut_multi()` commits ten transactions and verifies replay order and full action consumption. `wal_ut_checkpoint()` checkpoints at the midpoint and expects only transactions after the checkpointed ID to replay. `wal_ut_wrap()` and `wal_ut_wrap_many()` use `ut_fill_wal()` to fill and checkpoint enough large transactions to force WAL wraparound before replaying the final batch. `wal_ut_holes()` uses `DAOS_NVME_WAL_TX_LOST` fault injection and unmap support to simulate dropped transactions and verify replay skips holes until they are filled.

## State And Persistence Behavior
The persistent state under test is the WAL stream and its header/checkpoint metadata in BIO-managed blobs. Transaction IDs returned by `bio_wal_reserve()` are stored in fake transaction objects and compared during replay. Checkpointing via `bio_wal_checkpoint()` returns a non-zero purge size and advances the replay starting point. Wrap tests ensure old checkpointed WAL ranges can be reused without corrupting later replay.

The fake transaction payload buffer is rendered deterministically and referenced by copy-pointer actions; replay must persist the pointed-to data as inlined copy payload. `UMEM_ACT_CSUM` is explicitly unsupported in this unit test because BIO unit tests self-poll and do not model delayed NVMe checksum completion.

## Dependencies And Integration Points
The file depends on `bio_ut.h`, `bio_wal.h`, BIO metadata context setup from `ut_init()`/`ut_fini()`, cmocka, DAOS allocation/logging/fault-injection utilities, and SMD/NVMe behavior such as unmap support. `run_wal_tests()` registers the suite under a BIO unit-test setup/teardown pair, distinct from the VOS-level WAL suite of the same exported name in another test module.

## Risks And Edge Cases
The fake transaction object casts into `umem_wal_tx.utx_private`, so size/layout compatibility with the private area is assumed. Random action contents are seeded from `ut_args.bua_seed`, making tests deterministic only if setup initializes that seed consistently. Hole tests are skipped on devices without unmap support. Large payload and wrap tests consume significant memory and WAL capacity but are bounded by 128 MiB contexts and 800 KiB per large transaction.

## Test Signals
Strong signals include exact replayed action equivalence, replay action count matching commit action count, multi-transaction replay ordering, post-checkpoint replay count equal to transactions after the checkpoint, non-zero checkpoint purge size, wraparound replay of the most recent batch only, and no replay from WAL holes until a later transaction fills the missing position.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/wal_ut.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_aggregate.c -->
# sources/object-store/daos/src/vos/vos_aggregate.c

## Purpose
`vos_aggregate.c` implements VOS aggregation and discard. Aggregation removes obsolete versions, merges or deletes covered extent records, coalesces visible logical extents into new physical records, recalculates checksums, frees storage, updates the highest aggregated epoch, and yields cooperatively under credit limits. Discard removes data in an epoch range, optionally scoped to one object. The file is central to reclaim, snapshot deletion, VOS tree compaction, and metadata-on-SSD pressure handling.

## Important APIs, Types, And Functions
Public entry points are `vos_aggregate_enter()`, `vos_aggregate_exit()`, `vos_aggregate()`, and `vos_discard()`. `aggregate_enter()` and `aggregate_exit()` maintain container-level mutual exclusion flags for aggregation, discard, and object discard, and flush the WAL header when entering a mode.

`struct vos_agg_param` carries the container handle, current object ID, epoch filter, flags, error bits, UMEM pointer, yield callback, max SV epoch, skip flags, and `struct agg_merge_window`. `struct vos_agg_credits` limits scan/delete/merge work. `struct agg_merge_window` queues physical extent records (`agg_phy_ent`), removal records (`agg_rmv_ent`), visible logical entries (`agg_lgc_ent`), and I/O context (`agg_io_context`) for one evtree merge window.

Key callbacks are `vos_agg_filter()`, `vos_aggregate_pre_cb()`, and `vos_aggregate_post_cb()`. SV aggregation flows through `vos_agg_sv()` and `agg_del_sv()`. EV aggregation flows through `vos_agg_ev()`, `set_window_size()`, `join_merge_window()`, `flush_merge_window()`, `prepare_segments()`, `fill_segments()`, `insert_segments()`, and `cleanup_segments()`.

## Control Flow
`vos_aggregate()` asserts a valid epoch range, enters aggregation mode, chooses a filter epoch from HAE or `VOS_AGG_FL_FORCE_SCAN`, checks the container object-root aggregation timestamp, configures object iteration with `VOS_IT_PUNCHED`, `VOS_IT_RECX_COVERED`, `VOS_IT_FOR_PURGE`, and `VOS_IT_FOR_AGG`, initializes credits and merge-window lists, and calls `vos_iterate_obj()`. `-DER_BUSY` object conflicts trigger yield and retry. Checksum, no-space, and in-progress DTX states abort selected subtrees without blindly advancing HAE.

`vos_discard()` enters discard or object-discard mode, chooses iterator type and epoch expression from the supplied range, sets `VOS_IT_FOR_DISCARD`, and calls `vos_iterate()`. In discard mode value callbacks delete entries directly rather than building merge windows.

For EV aggregation, the sorted iterator emits logical records with visibility flags and original physical extents. `join_merge_window()` deletes fully covered intact records immediately, records remove entries, handles aborted/prepared DTX states, flushes the current window at thresholds or gaps, enqueues physical/logical entries, and flushes/closes on the iterator's last flag. `flush_merge_window()` decides whether work is worthwhile, prepares coalesced and truncated output segments, copies data, recalculates checksums, then transactionally deletes old evtree rectangles, inserts new rectangles, and publishes SCM/NVMe reservations.

## State And Persistence Behavior
Aggregation mutates persistent VOS trees and allocation state under UMEM transactions. `agg_del_sv()` wraps single-value deletion in `umem_tx_begin()`/`umem_tx_end()`. `insert_segments()` starts a transaction, publishes reserved SCM extents, updates physical-entry state for truncation, deletes old EV rectangles, processes removal records, inserts new evtree entries, clears the window, publishes NVMe reservations, and commits or aborts as a unit. On failure, `cleanup_segments()` cancels unpublished reservations.

Data movement uses BIO copy descriptors. `reserve_segment()` chooses SCM or NVMe via `vos_io_scm()` and reserves space through `vos_reserve_scm()` or `vos_reserve_blocks()`. `fill_one_segment()` builds source and destination BIO SGLs, widens reads when checksum chunks require extra bytes, verifies/recalculates checksums with `vos_csum_recalc_fn` through `vos_offload_exec()`, copies data, and updates aggregation metrics.

Container state includes `cd_hae`, `vc_in_aggregation`, `vc_in_discard`, `vc_obj_discard_count`, epoch ranges for active operations, no-space logging timestamps, and telemetry counters. `vos_aggregate()` updates HAE only when safe, and always calls `umem_heap_gc()` before returning.

## Dependencies And Integration Points
The implementation depends on VOS iterator APIs, object/key/ilog aggregation helpers (`oi_iter_*`, `vos_obj_iter_*`), evtree operations (`evt_insert()`, `evt_delete()`), BIO address/SGL/copy APIs, VEA/NVMe reservation publication, UMEM transactions and heap GC, checksum services, DTX state classification, DAOS fault injection, ABT yielding, and telemetry counters. It is directly exercised by VOS WAL/metadata-bucket tests that punch and aggregate objects to reclaim space.

## Risks And Edge Cases
Correctness risks cluster around partial physical extents, removal-record coalescing, checksum chunk alignment, transaction boundaries, and DTX conflict handling. Prepared entries return `-DER_TX_BUSY` and set skip flags to avoid orphaning parent tree state; aborted EV entries are deleted and cause iterator restart. No-space during aggregation is recorded without spamming logs, aborts current work, and avoids unsafe HAE advancement. Merge-window assertions and trace dumping are extensive because a sorted-iterator mismatch or stale visibility decision can corrupt evtree structure.

Large windows are bounded by byte threshold and `MW_MAX_MERGE_CNT` to limit WAL/local transaction size. `need_flush()` deliberately skips same-media coalescing when it would cost more than it saves, but forces flush for invisible data, removals, SCM-to-NVMe migration, holes, and forced merge. Discard and aggregation concurrency is restricted through container flags and WAL header flushes; object discard has separate counting but cannot overlap with full discard.

## Test Signals
Expected signals are indirect across VOS aggregation, discard, WAL, and metadata-bucket tests: obsolete SV/EV entries disappear, visible latest values remain fetchable, object/key trees collapse when empty, HAE advances only after successful safe aggregation, checksum errors return `-DER_CSUM`, no-space avoids corruption, in-progress DTX entries suppress parent aggregation, and storage usage decreases after punch plus `vos_aggregate()` followed by GC. Telemetry counters for scans, skips, deletes, merges, checksum errors, uncommitted entries, blocked retries, merge record counts, and merge bytes provide runtime observability.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_aggregate.c -->
