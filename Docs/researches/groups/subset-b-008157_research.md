# Research: subset-b-008157

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_aggregate.c -->
# sources/object-store/daos/src/vos/tests/vts_aggregate.c

## Purpose

`vts_aggregate.c` is the main cmocka coverage for VOS aggregation and discard behavior. It builds synthetic single-value and extent-value histories, runs `vos_aggregate()` or `vos_discard()` over chosen epoch ranges, and verifies both the visible logical value and, where deterministic, the number of surviving physical records. It also covers checksum aggregation, object/key punches, delete records, NVMe merge selection, flat dkey object layouts, and aggregation timestamp encoding.

## Important APIs, Types, And Functions

The file exports `run_discard_tests()` and `run_aggregate_tests()`. Its central test model is `struct agg_tst_dataset`, which records the OID/type, update epoch range, aggregation/discard epoch range, recx layout, expected view buffer, expected physical record count, and flags for discard/delete behavior.

`update_value()` and `fetch_value()` wrap the common VOS I/O helpers from `vts_io.h`, constructing dkeys, akeys, `daos_iod_t`, and `d_sg_list_t`. They also toggle test flags such as `TF_PUNCH`, `TF_DELETE`, `TF_USE_VAL`, `TF_USE_CSUMS`, and occasionally `TF_ZERO_COPY`. `phy_recs_nr()` uses `vos_iterate()` with `VOS_ITER_SINGLE` or `VOS_ITER_RECX` to count physical entries. `generate_view()` captures the logical value expected before compaction, while `verify_view()` checks post-aggregation fetch results and physical record counts.

`aggregate_basic_lb()` is the core driver: it writes one update per epoch, optionally injects punches/deletes, snapshots the expected value, runs `vos_discard()` or `vos_aggregate()`, then verifies. `aggregate_multi()` applies randomized workloads across multiple objects, dkeys, and akeys. The punch helpers (`do_punch()`, `agg_punches_test_helper()`) exercise object, dkey, and akey punches. `removal_stress_case()` drives complicated delete-record compaction patterns.

## Control Flow

The cmocka arrays split discard cases (`VOS451`-`VOS469`) from aggregate cases (`VOS401`-`VOS437`). Most tests create a dataset, populate epoch/record shape, and call a shared driver. SV tests vary confined epoch ranges, full-range cleanup, random punch/yield, and multiple-key workloads. EV tests vary disjoint, adjacent, overlapping, fully covered, merge-window-spanning, random, checksum, and delete-record scenarios.

Longer tests include `aggregate_14()`, which repeatedly fills a pool and aggregates to observe storage recovery, and `aggregate_34()`, which skips when NVMe is unavailable and compares scan-only versus force-merge behavior. `aggregate_35()` is a pure unit test for `vos_feats_agg_time_get()` and `vos_feats_agg_time_update()`.

## State And Persistence Behavior

The suite deliberately creates persistent VOS pool/container state via the shared I/O fixture, mutates records across epochs, and then checks that aggregation/discard only changes physical representation where allowed. Full-range discard expects object disappearance via `lookup_object()`. Repeated update/aggregate tests query pool space before and after aggregation. Fail locations such as `DAOS_VOS_AGG_RANDOM_YIELD` and `DAOS_VOS_AGG_MW_THRESH` force scheduler-yield and merge-window paths.

## Dependencies And Integration Points

The file depends on `vts_io.h`, VOS internals, container server definitions, cmocka assertions, DAOS dkey/akey helpers, VOS object/update/fetch/punch APIs, VOS iterators, fail injection, GC waiting, and pool query/stat structures. It integrates directly with the test runner through `setup_io()` and `teardown_io()`.

## Risks And Test Signals

The highest-risk areas are randomized workloads, fail-injection-dependent paths, large pool fills, and assumptions about physical record counts after compaction. Some expected counts are intentionally `-1` when physical layout is nondeterministic. `aggregate_22()` also protects conditional fetch/update semantics across aggregation. Passing signals include stable logical fetches before/after compaction, expected object nonexistence after full discard, no infinite iterator loop, checksum-safe aggregation, and correct timestamp feature encoding.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_aggregate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_array.c -->
# sources/object-store/daos/src/vos/tests/vts_array.c

## Purpose

`vts_array.c` implements a small DAOS-array-like abstraction on top of raw VOS object operations. It is not a cmocka suite itself; it is a test utility used by other VOS tests that need array semantics without involving the full DAOS array layer.

## Important APIs, Types, And Functions

`struct vts_metadata` stores the object magic, record size, records per dkey stripe, and akey size. `struct vts_array` is the open handle state: OID, container handle, array and metadata IODs, dkey/akey backing buffers, recx and iov arrays, I/O chunk size, metadata, and a zero buffer used for extending size.

The exported API is `vts_array_alloc()`, `vts_array_free()`, `vts_array_open()`, `vts_array_reset()`, `vts_array_close()`, `vts_array_set_size()`, `vts_array_get_size()`, `vts_array_set_iosize()`, `vts_array_write()`, `vts_array_punch()`, and `vts_array_read()`. Internally, `array_init()`, `array_open()`, and `array_fini()` manage handle memory. `update_meta()` and `fetch_meta()` persist metadata as a single value under dkey zero/akey zero. `update_array()` and `fetch_array()` build one or more recxs for a single stripe.

## Control Flow

Allocation generates a `DAOS_OT_DKEY_UINT64` object ID, initializes a temporary array descriptor, and writes metadata at the creation epoch. Opening fetches metadata at `DAOS_EPOCH_MAX`, validates `ARRAY_MAGIC`, allocates per-open buffers, and returns a cookie-style `daos_handle_t`.

Reads, writes, and punches split logical array offsets into stripes of `vm_per_key` elements. Each stripe is stored under dkey `stripe + 1`, with the configured akey length. Partial stripe writes become `vos_obj_update()` calls with recxs. Whole-stripe punches call `vos_obj_punch()` on the dkey; partial punches call `update_array()` with `iod_size` zero. Size discovery uses `vos_obj_query_key()` with `DAOS_GET_DKEY | DAOS_GET_RECX | DAOS_GET_MAX`.

## State And Persistence Behavior

The abstraction persists only VOS object data: metadata single value and array extents partitioned by numeric dkeys. Open handles are process-local cookies and are invalidated by `array_fini()` clearing the magic. `vts_array_reset()` punches the whole object at an earlier epoch, writes new metadata at a later epoch, closes the old handle, and reopens it.

## Dependencies And Integration Points

It depends on `vts_io.h`, `vts_array.h`, VOS object update/fetch/query/punch/delete APIs, DAOS I/O descriptor types, and DAOS allocation/assertion helpers. The interface in `vts_array.h` lets test code model DAOS array behavior while staying in standalone VOS.

## Risks And Test Signals

The main risks are pointer arithmetic on `void *`, correct stripe boundary math, and allocation error cleanup. There is a likely copy/paste bug in `array_open()`: after allocating `va_iovs`, it checks `array->va_recx == NULL` instead of `array->va_iovs == NULL`. The utility has no direct tests in this file, so downstream array-like tests are the signal.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_array.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_array.h -->
# sources/object-store/daos/src/vos/tests/vts_array.h

## Purpose

`vts_array.h` declares the VOS test-array helper API implemented in `vts_array.c`. The comments describe it as a convenience library for DAOS-array-like behavior on one standalone VOS target.

## Important APIs And Types

The header includes `<daos_srv/vos.h>` and exposes only opaque `daos_handle_t` array handles and `daos_unit_oid_t` object IDs. The lifecycle API is `vts_array_alloc()`, `vts_array_open()`, `vts_array_reset()`, `vts_array_close()`, and `vts_array_free()`. The data API is `vts_array_set_iosize()`, `vts_array_set_size()`, `vts_array_get_size()`, `vts_array_write()`, `vts_array_punch()`, and `vts_array_read()`.

## Control Flow And Integration

Callers allocate an array object in a VOS container at a creation epoch, open it into a handle, optionally tune I/O chunking, then perform epoch-addressed reads, writes, punches, and size changes. Reset requires a punch epoch lower than the recreate epoch. Free deletes the underlying VOS object.

## State And Persistence Behavior

The header intentionally hides `struct vts_array`; state lives in the implementation and in VOS object metadata. All operations are epoch-aware, so callers can test MVCC/aggregation behavior over array-like records.

## Dependencies, Risks, And Test Signals

This is a narrow test helper contract. Risks come from callers assuming full DAOS array semantics; the implementation is simpler and stores metadata/data through raw VOS. Test signal is indirect: any suite using these functions should prove stripe splitting, size queries, and punch behavior.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_array.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_checksum.c -->
# sources/object-store/daos/src/vos/tests/vts_checksum.c

## Purpose

`vts_checksum.c` validates checksum storage and retrieval for VOS array records and unit-tests EVT checksum helper functions. It ensures VOS returns checksum metadata aligned with fetched physical bio vectors, correctly handles holes, and marks corrupted extents so fetch fails with checksum errors.

## Important APIs, Types, And Functions

`struct extent_key` captures container handle, object ID, and generated dkey/akey buffers. `extent_key_from_test_args()` maps `io_test_args` into VOS keys and OID. `struct recx_config`, `struct expected_biov`, and `struct test_case_args` describe update/fetch extents, checksum counts, expected bio-vector prefix/suffix trimming, and hole counts.

`csum_for_arrays_test_case()` is the core harness. It builds `dcs_iod_csums`, writes array extents with `vos_obj_update()`, uses `vos_fetch_begin()` to inspect the VOS I/O handle, and compares returned `dcs_ci_list` checksums against the original `dcs_csum_info` buffers via `cia_idx` helpers. Corruption tests use `vos_iterate()` plus `VOS_ITER_PROC_OP_MARK_CORRUPT` and verify `BIO_ADDR_IS_CORRUPTED()`.

EVT helper tests cover `evt_csum_count()`, `evt_csum_buf_len()`, `evt_entry_align_to_csum_chunk()`, and `evt_entry_csum_update()`.

## Control Flow

Ten checksum array cases cover single chunks, multiple extents, one extent fetched as many, many fetched as one, partial chunk fetches, sequential extents, and holes. Two corruption cases mark single-value and array-value records corrupted, then expect `vos_obj_fetch()` to return `-DER_CSUM`.

The helper tests are run in a second cmocka group. They construct minimal `evt_root`, `evt_context`, `evt_extent`, and `evt_entry` structures directly, avoiding VOS pool state for pure arithmetic and pointer-adjustment behavior.

## State And Persistence Behavior

Array checksum tests persist data and checksum blobs into VOS at epoch 1. Fetch state is observed through the internal bio descriptor and checksum list before `vos_fetch_end()`. Corruption tests mutate persistent bio addresses through iterator processing, then confirm the corruption marker survives iteration and changes fetch results.

## Dependencies And Integration Points

The file includes DAOS checksum types, `evt_priv.h`, and `vts_io.h`. It integrates with `setup_io()`/`teardown_io()` and touches VOS update/fetch begin/end, iterator processing, bio vectors, checksum list accessors, and EVT-private checksum helpers.

## Risks And Test Signals

Important risks include off-by-one checksum chunk alignment, missing checksums for partial fetches, holes incorrectly receiving checksums, and corrupted data still being readable. Passing signals are exact bio-vector prefix/suffix lengths, exact checksum byte equality, expected checksum-list counts, and `-DER_CSUM` after corruption marking.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_checksum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_common.c -->
# sources/object-store/daos/src/vos/tests/vts_common.c

## Purpose

`vts_common.c` provides shared fixture and resource helpers for VOS tests. It creates temporary pool files, initializes standalone VOS state, creates/destroys pools and containers, and manages reusable I/O credit buffers.

## Important APIs, Types, And Functions

The file exports `vts_file_exists()`, `vts_alloc_gen_fname()`, `vts_pool_fallocate()`, `vts_ctx_init()`, `vts_ctx_fini()`, `dts_ctx_init()`, `dts_ctx_fini()`, `dts_credit_take()`, and `dts_credit_return()`. Global `vos_path` and `gc` select file names; `oid_cnt` is reset during context initialization.

`vts_ctx_init()` is a compact pool/container fixture based on `struct vos_test_ctx`. It creates a pool file name, removes stale files, generates pool/container UUIDs, calls `vos_pool_create()`, `vos_cont_create()`, and `vos_cont_open()`, recording setup progress in `tc_step`. `vts_ctx_fini()` unwinds based on `tc_step`.

`dts_ctx_init()` is the broader I/O fixture for `struct credit_context`: initialize DAOS debug, call `vos_self_init()`, open/create pool, open/create container, then allocate credit buffers. `dts_ctx_fini()` reverses those steps. `vts_credits_init()` allocates each credit's value buffer; `dts_credit_take()` and `dts_credit_return()` manage the available-credit slots.

## Control Flow

The fixture code uses explicit state machines (`TCX_*` and `DTS_INIT_*`) so partial initialization can be unwound safely. Pool initialization fallocates an SCM file, then chooses create or open based on `tsc_create_pool()`. Container initialization similarly creates conditionally and always opens. Finalization falls through from the highest initialized step to clean lower layers.

## State And Persistence Behavior

Pool state is file-backed under `vos_path`, with generated `vpool.N` names. `vts_pool_fallocate()` creates a 256 MiB file, while `pool_init()` allocates `tsc_scm_size`. Destroy paths call VOS pool/container close and destroy operations; test files are freed/destroyed by callers. Credit state is in memory and must have no in-use credits at finalization.

## Dependencies And Integration Points

The file depends on Linux file APIs, fallocate, DAOS/VOS public and internal headers, DAOS debug initialization, cmocka assertions, and `vts_common.h`. It is the foundation used by container, GC, I/O, DTX, ilog, and aggregation tests.

## Risks And Test Signals

Risks include leaked file descriptors, incomplete cleanup after setup failure, stale files, and mismatched credit accounting. The test signal is mostly fixture reliability: suites can create/destroy isolated pools repeatedly without leftover containers, memory buffers, or pool files.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_common.h -->
# sources/object-store/daos/src/vos/tests/vts_common.h

## Purpose

`vts_common.h` is the shared declarations and constants header for VOS tests. It defines common pool sizes, global fixture variables, test context structures, runner entry points, and DTX helper declarations.

## Important APIs, Types, And Functions

The header declares `struct vos_test_ctx`, `enum vts_ops_type`, pool-size macros (`VPOOL_256M`, `VPOOL_1G`, `VPOOL_2G`, `VPOOL_3G`, `VPOOL_SIZE`), and `FAULT_INJECTION_REQUIRED()`. It exposes fixture functions from `vts_common.c` and runner functions for pool, container, discard, aggregate, DTX, GC, persistent memory, I/O, timestamp, ilog, checksum, MVCC, WAL, evtree, tree, mark, and command tests.

It also declares `vts_dtx_begin()` and `vts_dtx_end()`, plus inline `vts_dtx_begin_ex()`, which begins a DTX and then overrides epoch bound and modification count before reinitializing reserved DTX state.

## Control Flow And Integration

Most test files include this header directly or indirectly through `vts_io.h`. Suite mains can call the `run_*_tests()` functions without knowing each file's static cmocka arrays. Test code uses `FAULT_INJECTION_REQUIRED()` to skip fault-injection-only cases when the build lacks support.

## State And Persistence Behavior

The header exposes globals such as `vos_path`, `gc`, `g_force_checksum`, `g_force_no_zero_copy`, `last_dkey`, and `last_akey`, making test behavior configurable across files. The DTX helper mutates a `struct dtx_handle` after attach, so it is tightly coupled to VOS internals.

## Risks And Test Signals

Because this header centralizes test runner declarations, signature drift will break build-time integration. The inline DTX helper relies on `vos_dtx_rsrvd_init()` succeeding after fields are modified; failures are caught by cmocka assertions in tests that use it.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_container.c -->
# sources/object-store/daos/src/vos/tests/vts_container.c

## Purpose

`vts_container.c` tests VOS container lifecycle APIs: create, open, query, close, destroy, UUID iteration, anchor reprobe, and handle reference counting.

## Important APIs, Types, And Functions

`struct vc_test_args` stores a pool file, pool UUID/handle, operation sequences for up to `VCT_CONTAINERS` containers, opened handles, container UUIDs, and an anchor flag. `co_ops_run()` executes per-container operation sequences using `vos_cont_create()`, `vos_cont_open()`, `vos_cont_query()`, `vos_cont_close()`, and `vos_cont_destroy()`.

Setup/teardown create and destroy one VOS pool via `vts_pool_fallocate()`, `vos_pool_create()`, `vos_pool_close()`, and `vos_pool_destroy()`. `co_uuid_iter_test()` directly prepares a `VOS_ITER_COUUID` iterator and validates every created container UUID is returned, optionally fetching an anchor and probing it back into the iterator.

## Control Flow

The suite has five cmocka cases. `VOS100` creates 100 containers and lets teardown destroy leftovers. `VOS101` runs create/open/query/close/destroy for all containers. `VOS102` and `VOS103` create containers, then iterate UUIDs without and with anchor reprobe. `VOS104` opens the same container 100 times, confirms destroy returns `-DER_BUSY`, closes all handles, and then destroys successfully.

## State And Persistence Behavior

All state is under a single temporary pool file. Container UUIDs are generated per test and cleared on destroy. Teardown defensively destroys any UUID still present and removes the pool file if it remains. Query tests assert newly created containers have zero objects and zero used bytes.

## Dependencies And Integration Points

The file uses `vts_common.h`, VOS internals, cmocka, UUID APIs, and VOS iterator APIs. It integrates with the broader runner through `run_co_test()`.

## Risks And Test Signals

Risks are reference leaks, iterator anchor invalidation, and cleanup failure after partial test execution. Passing signals include all lifecycle calls returning zero, query counters staying zero, iterator count matching `VCT_CONTAINERS`, and `-DER_BUSY` while open handles exist.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_container.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_dtx.c -->
# sources/object-store/daos/src/vos/tests/vts_dtx.c

## Purpose

`vts_dtx.c` tests distributed transaction visibility and bookkeeping in VOS. It covers prepared/committed/aborted DTX records, punch visibility, committed/aborted idempotence, committable cache behavior, iteration visibility, and DTX aggregation.

## Important APIs, Types, And Functions

`vts_init_dte()` builds a minimal `dtx_entry` with one target membership and a unique XID. `vts_dtx_begin()` allocates a `struct dtx_handle`, fills leader fields, initializes share lists, reserves DTX state, and attaches it with `vos_dtx_attach()`. `vts_dtx_end()` frees share peers, finalizes reserved state, detaches, and frees memory.

`vts_dtx_prep_update()` prepares common key, IOD, SGL, recx, epoch, and dkey hash state for either single-value or extent-value updates. `vts_dtx_commit_visibility()` and `vts_dtx_abort_visibility()` are the primary visibility harnesses.

## Control Flow

Tests `dtx_6`-`dtx_9` write with a prepared DTX, confirm data is invisible, commit it, confirm visible, then prepare a key/object punch and verify visibility changes only after commit. Tests `dtx_10`-`dtx_13` do the same for abort: an aborted update or punch must not affect the previously visible data.

`dtx_14` verifies double-commit is harmless and committed DTX cannot be aborted. `dtx_15` verifies double-abort/commit-after-abort does not reveal aborted data. `dtx_16` uses fault injection to simulate non-leader fetch behavior and checks `vos_dtx_mark_committable()` makes prepared data readable from the CoS cache. `dtx_17` iterates dkeys and sees only committed DTXs until the remaining transactions are committed. `dtx_18` commits ten DTXs, aggregates committed DTX metadata, checks committed stats drop to zero, and verifies data remains readable.

## State And Persistence Behavior

The tests write real VOS records under transactional metadata. Prepared DTXs must hide data and punches; commit and abort mutate DTX state and visibility. DTX aggregation removes committed DTX metadata while preserving data records. `sleep(3)` in `dtx_18` gives commit statistics enough time to age before aggregation.

## Dependencies And Integration Points

The file depends on DAOS DTX server internals, VOS types, `vts_io.h`, Murmur hashing, HLC timestamps, fail injection, VOS DTX APIs, object punch/update/fetch, and iterators. It exports `run_dtx_tests()` and helper functions declared by `vts_common.h`.

## Risks And Test Signals

Risks include DTX handle lifetime leaks, incorrect visibility for prepared records, punches becoming visible too early, iterator leakage of uncommitted dkeys, and aggregation removing needed data. Passing signals are memory equality/inequality around fetches, exact commit/abort return codes, expected iterator found sets, and `vos_dtx_check()` returning `-DER_NONEXIST` after aggregation.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_dtx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_evtree.c -->
# sources/object-store/daos/src/vos/tests/vts_evtree.c

## Purpose

`vts_evtree.c` is a focused unit test for EVT descriptor validation. It checks that `evt_desc_is_valid()` rejects null descriptors, descriptors with invalid magic, and descriptors with an unexpected DTX local ID.

## Important APIs, Types, And Functions

The file constructs three static `struct evt_desc` instances: invalid magic, invalid DTX LID, and valid. `evt_desc_is_valid_test()` asserts the expected boolean result for each. `run_evtree_tests()` registers the single cmocka case.

## Control Flow, State, And Persistence

There is no VOS fixture, persistent pool, or tree allocation. The test is pure in-memory validation of descriptor fields against caller-supplied `DTX_LID_VALID`.

## Dependencies And Integration Points

It includes public EVT headers and `evt_priv.h`, plus cmocka. The suite name is fixed to `"evtree"` and does not use the `cfg` argument.

## Risks And Test Signals

The risk is narrow but important: accepting stale or corrupt evtree descriptors could allow invalid metadata traversal. Passing signal is exact rejection/acceptance for the four basic descriptor cases.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_evtree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_gc.c -->
# sources/object-store/daos/src/vos/tests/vts_gc.c

## Purpose

`vts_gc.c` stress-tests VOS garbage collection for deleted keys, objects, and containers. It builds large object/key/akey populations, deletes at different levels, manually tightens GC, and compares VOS-reported GC statistics with expected counts.

## Important APIs, Types, And Functions

`struct gc_test_args` owns a `credit_context` fixture and a boolean selecting single-value versus array-value updates. `gc_add_stat()` and `gc_print_stat()` maintain expected `struct vos_gc_stat` counters. `gc_obj_update()` writes either a single value through `vos_obj_update()` or an array value through zero-copy `vos_update_begin()`, `bio_iod_prep()`, `bio_iod_post()`, and `vos_update_end()`.

`gc_obj_prepare()` creates many objects, dkeys, akeys, and records. `gc_wait_check()` repeatedly calls `vos_gc_pool_tight()` until credits are available, then queries `vos_pool_query()` and compares `pif_gc_stat` to expected counters. `gc_key_run()`, `gc_obj_run()`, `gc_obj_run_destroy()`, and `gc_cont_run()` drive key, object, object-with-container-destroy, and container deletion scenarios.

## Control Flow

The cmocka cases cover key GC, object GC, object GC for array/bio records, container GC, destroying a container with outstanding objects, and object GC after closing/reopening a container. `gc_setup()` creates a 2 GiB SCM / 4 GiB NVMe-style fixture with 16 reusable credits; under Valgrind, object and dkey counts are reduced.

Each test resets fail locations, resets VOS GC counters with `VOS_PO_CTL_RESET_GC`, populates data, deletes the target level, enables GC fail-location forcing (`DAOS_VOS_GC_CONT` or `DAOS_VOS_GC_CONT_NULL`), and checks counters.

## State And Persistence Behavior

The tests create persistent pool/container state via `dts_ctx_init()`, update many VOS records, delete records or containers, and inspect GC statistics persisted in pool info. Array-mode updates intentionally write arbitrary data through bio paths because only allocation/freeing behavior matters.

## Dependencies And Integration Points

The file depends on `vts_io.h`, DAOS API headers, VOS pool/control/query APIs, object delete/key delete, container lifecycle, zero-copy bio internals, fail injection, and common credit helpers. It exports `run_gc_tests()`.

## Risks And Test Signals

Risks include counter drift, GC starvation, reopen-specific cleanup bugs, bio extent leaks, and mismatch between expected logical deletes and physical frees. Passing signals are exact `vos_gc_stat` matches, successful pool tightening, no leaked credit buffers, and successful cleanup in teardown.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_gc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_ilog.c -->
# sources/object-store/daos/src/vos/tests/vts_ilog.c

## Purpose

`vts_ilog.c` tests VOS incarnation log behavior: update, punch replacement, abort, persist, aggregate, discard, validation, and version-cache changes. It uses a fake transaction-status layer so ilog code can be exercised without full DTX service state.

## Important APIs, Types, And Functions

`ilog_alloc_root()` and `ilog_free_root()` allocate/free an `ilog_df` root through `umem_tx_begin()`/`umem_tx_end()`. Fake transaction support is built from `struct fake_tx_entry`, global `fake_tx_list`, `current_status`, and `current_tx_id`. The callbacks in `ilog_callbacks` implement status lookup, same-transaction detection, log add, and log delete using an `lru_array`.

`struct entries` models the expected ilog sequence. `entries_init()` creates the LRU array and expected-entry buffer. `entries_set()` updates the expected sequence, and `entries_check()` runs `ilog_fetch()` and compares epoch and punch bits. `do_update()` wraps `ilog_update()` and encodes when an update should be appended to the expected model. `version_cache_fetch_helper()` checks `ilog_version_get()` increments only when expected.

## Control Flow

`ilog_test_update()` creates/open an ilog, inserts updates, upgrades same-epoch updates to punches, persists a transaction, verifies same-epoch conflict return codes, and appends many records with mixed statuses. `ilog_test_abort()` aborts existing and non-existing IDs, repeatedly inserts and aborts entries, and checks a destroyed/reallocated ilog cannot be opened. `ilog_test_persist()` persists entries out of order and validates visible log content.

`ilog_test_aggregate()` commits fake transactions, aggregates epoch ranges, and expects old entries to collapse to the correct surviving update or punch, eventually returning an empty-log signal. `ilog_test_discard()` runs similar aggregation with discard semantics, where ranges are removed instead of compacted. `ilog_is_valid_test()` directly constructs embedded and array ilog roots in a VMEM umem instance and verifies DTX LID/epoch matching behavior.

## State And Persistence Behavior

The tests allocate real umem-backed ilog roots from the VOS pool fixture. Fake transaction entries persist only in memory but are linked to ilog entry offsets and epochs. Persist, abort, aggregate, and destroy paths must delete fake tx entries so `fake_tx_list` is empty at the end. Version cache assertions detect missing or spurious ilog version bumps.

## Dependencies And Integration Points

The file depends on `vts_io.h`, VOS internals, `ilog_internal.h`, umem, LRU arrays, cmocka, and the common I/O fixture. It exports `run_ilog_tests()`, with `setup_ilog()` allocating `struct entries` in `io_test_args->custom`.

## Risks And Test Signals

Risks include leaked fake transaction entries, incorrect same-epoch conflict handling, aborted prepared entries staying visible, aggregation removing the wrong punch/update, and invalid ilog roots being accepted. Passing signals include exact fetched entry sequences, expected return codes (`-DER_ALREADY`, `-DER_TX_RESTART`, `-DER_NONEXIST`, empty-log return `1`), version changes only on mutation, and empty fake transaction lists after cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_ilog.c -->
