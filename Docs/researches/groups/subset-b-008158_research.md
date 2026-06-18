# subset-b-008158 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_io.c -->
# sources/object-store/daos/src/vos/tests/vts_io.c

## Purpose
`vts_io.c` is the central VOS object IO test suite and shared implementation behind the declarations in `vts_io.h`. It creates the reusable `io_test_args` fixture, generates object IDs and keys for multiple DAOS object-class key layouts, and exercises the VOS update, fetch, punch, iteration, query-key, checksum, zero-copy, object-index, and object-cache paths. The file is test-facing but reaches into internal VOS, BIO, checksum, DTX, and object-cache APIs to validate persistence-tree behavior below the public object API layer.

## Important APIs, Types, And Functions
The key exported helpers are `setup_io`, `teardown_io`, `test_args_reset`, `vts_key_gen`, `set_iov`, `gen_rand_epoch`, `gen_oid`, `gen_oid_stable`, `inc_cntr`, `io_test_obj_update`, `io_test_obj_fetch`, and `run_io_test`. Static fixture state includes `vts_epoch_gen`, `vts_cntr`, fixed integer akey values, `last_dkey`, `last_akey`, and `vts_nest_iterators`.

`test_args_init` initializes a `vos_test_ctx`, chooses object type-dependent key sizing, prepares fixed akeys for single-value and array modes, and records the generated pool filename. `setup_io` also creates a VOS timestamp table with `vos_ts_table_get(true)`, while `teardown_io` frees/reallocates it before finalizing the VOS test context.

The main IO wrapper pair abstracts normal and zero-copy paths. `io_test_obj_update` optionally computes checksums, supports array remove when `TF_DELETE` is set, calls `vos_obj_update` for ordinary writes, or drives `vos_update_begin`, `bio_iod_prep`, `bio_iod_copy`, `bio_iod_post`, and `vos_update_end` for zero-copy writes. `io_test_obj_fetch` similarly chooses ordinary fetch via `io_test_vos_obj_fetch` or a zero-copy fetch path using `vos_fetch_begin`, BIO copy from persistent media, and `vos_fetch_end`. `io_test_vos_obj_fetch` additionally verifies fetched checksum metadata through `ds_csum_add2iod`, `ds_iom_create`, and `daos_csummer_verify_iod`.

## Control Flow
`run_io_test` first runs integer-object-class tests with `DAOS_OT_MULTI_UINT64`, then runs general IO and iterator suites over caller-provided object types. `run_oclass_tests` derives readable key-type labels, runs `io_tests`, then runs `iterator_tests` twice with nested iterator mode disabled and enabled. `run_single_class_tests` runs object-index, object-cache, key-query, large single-value, and checksum metadata tests.

The common update/fetch flow is `io_update_and_fetch_dkey`: generate dkey/akey unless overwriting or punching, configure either `DAOS_IOD_SINGLE` or `DAOS_IOD_ARRAY`, write through `io_test_obj_update`, update counters, fetch through `io_test_obj_fetch`, and compare buffers and record size. This powers simple one-key, many-key, overwrite, near-epoch, and iterator setup tests.

Iterator control flow is split by hierarchy. `io_obj_iter_test` prepares a dkey iterator, optionally sets fixed akey filters and anchor probes, then calls `io_akey_iterate`, which may set parent iterator handle for nested iteration and calls `io_recx_iterate`. Range and reverse-range tests create epochs around a selected range and assert only in-range records are enumerated. `vos_iterate_test` exercises the higher-level recursive iterator API with filter, pre, and post callbacks that request yield, skip, and abort actions, then checks exact callback counts.

## State And Persistence Behavior
The fixture creates and destroys real VOS pool/container state through `vts_ctx_init` and `vts_ctx_fini`. The tests rely on persisted object trees, epoch visibility, punches, and holes. Key state is deliberately reused through `last_dkey` and `last_akey` for overwrite and punch scenarios. Stable OID generation uses deterministic prime increments to support broad conditional collision-like coverage in other suites.

Object-cache tests manipulate the thread-local object cache (`vos_tls_get`, `vos_obj_cache_create`, `vos_obj_cache_destroy`) and validate hold/release conflicts for discard, aggregation, visible read, and create intents across two containers. Key-query tests build integer-key trees, punch records, akeys, dkeys, and objects, and validate `vos_obj_query_key` min/max dkey/akey/recx results and max-write epoch behavior. Checksum tests validate both single-value checksum fetch and array recx checksum metadata, including the case where recx entries have no stored checksums and the checksum info list must be empty.

## Dependencies And Integration Points
The file depends on `vts_io.h`, `vts_array.h`, `vts_common.h` transitively, DAOS object/checksum APIs, server checksum helpers, VOS internals, BIO helpers, CMocka, and DTX helpers such as `vts_dtx_begin`/`vts_dtx_end`. It integrates with the broader VOS test runner through `run_io_test`, which supplies object types and key counts. Other VOS tests reuse the exported fixture and helper wrappers.

## Risks And Test Signals
The suite is intentionally broad and can be expensive: `VTS_IO_KEYS` reaches 100K unless tracing or Valgrind reduces it, and `gang_sv_test` allocates 27 MB buffers. Many tests assume exact iterator callback counts, epoch ordering, and object tree behavior, so legitimate iterator implementation changes require test updates. The zero-copy paths touch internal BIO descriptors directly, which is useful coverage but tightly couples the tests to VOS/BIO internals. Strong signals include CMocka assertions for return codes, buffer equality, iterator counts, `-DER_NONEXIST`, `-DER_REC2BIG`, checksum identity, and transactional punch/query behavior.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_io.h -->
# sources/object-store/daos/src/vos/tests/vts_io.h

## Purpose
`vts_io.h` is the shared interface for the VOS IO-oriented test suites. It centralizes constants, flags, fixture state, counters, and helper prototypes used by `vts_io.c`, punch-model tests, MVCC tests, corruption-mark tests, aggregation tests, and array helpers.

## Important APIs, Types, And Functions
The header defines update/fetch sizing constants such as `UPDATE_DKEY_SIZE`, `UPDATE_AKEY_SIZE`, `UPDATE_BUF_SIZE`, `UPDATE_REC_SIZE`, checksum buffer sizes, and the default IO key counts. `enum vts_test_flags` controls test behavior for iterator anchors, zero-copy, overwrite, punch, record extents, fixed akeys, value/checksum use, deletion, and disabled tests.

`struct io_test_args` is the central fixture passed through CMocka state. It stores the VOS test context, current object ID, optional additional container UUID/handle, epoch range lower bound, flags, default dkey/akey strings and sizes, custom test-private state, object type, container creation step, and replay/checkpoint failure toggles. `struct vts_counter` tracks dkeys, fixed-akey dkeys, oids, and punch operations for iterator verification.

Declared helper APIs include object and epoch generation (`gen_rand_epoch`, `gen_oid`, `reset_oid_stable`, `gen_oid_stable`), counter updates, fixture setup/teardown, argument reset, key generation, simple iov setup, and object update/fetch wrappers. It also declares `update_value` and `fetch_value` from `vts_aggregate.c`.

## Control Flow
The header itself has no runtime control flow beyond the inline `hash_key`. Test files include it to share fixture setup, generate compatible object/key layouts, and call `io_test_obj_update`/`io_test_obj_fetch` instead of open-coding all VOS IO variants. `hash_key` interprets integer keys as a `uint64_t` when requested and otherwise uses `d_hash_string_u32`.

## State And Persistence Behavior
The important state contract is the shape of `io_test_args`: each test starts with a VOS pool/container in `ctx`, uses `oid` and type-aware dkey/akey fields to address persistent trees, and may attach per-test data through `custom`. The flags influence whether the backing VOS operation writes arrays or single values, checksums, zero-copy BIO data, deletion/removal records, and iterator anchor handling.

## Dependencies And Integration Points
The header pulls in CMocka, DAOS common/VOS server APIs, `vos_obj.h`, and `vos_internal.h`, so users of this fixture can test internal VOS behavior rather than only public client APIs. It is included by `vts_io.c`, `vts_mark.c`, `vts_mvcc.c`, `vts_pm.c`, and other VOS tests.

## Risks And Test Signals
Because this header exposes internal VOS types into many tests, changes to `struct io_test_args`, flag bits, or helper prototypes have broad compile and behavioral impact. Integer-key hashing assumes the iov buffer is at least eight bytes when `flag` is set. The test signal is mostly indirect: successful compilation of all dependent tests and correct runtime behavior of the shared fixture wrappers.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_mark.c -->
# sources/object-store/daos/src/vos/tests/vts_mark.c

## Purpose
`vts_mark.c` tests `vos_obj_mark_corruption` and the behavior of VOS after marking objects, dkeys, or akeys as corrupted. It verifies validation errors, propagation of `-DER_DATA_LOSS` to fetch/update/punch, allowed repeated marks, behavior for nonexistent targets, discard and aggregation interactions, and direct delete behavior used by DDB-style repair flows.

## Important APIs, Types, And Functions
`vts_mark_update` is the main setup helper. It optionally creates a new object and dkey, generates dkey/akey/value buffers, configures a single-value IOD, and performs `vos_obj_update`. `vts_mark_prep_sgl` prepares a one-iov scatter/gather list for reads or writes. The test bodies are `vts_mark_1` through `vts_mark_5`, with `vts_mark_discard` and `vts_mark_delete` as reusable scenario helpers.

## Control Flow
`vts_mark_1` covers object-level corruption. It first verifies invalid argument combinations, marks an existing object corrupted, confirms fetch/update/punch return `-DER_DATA_LOSS`, repeats the mark successfully, then marks a nonexistent object and verifies it becomes a corrupted object visible to data-loss checks.

`vts_mark_2` covers dkey corruption. It rejects invalid empty or null dkeys, marks an existing dkey, checks data-loss errors on fetch/update/punch for that dkey, proves another dkey under the same object still works, and marks a nonexistent dkey successfully.

`vts_mark_3` covers akey corruption. It rejects invalid akeys, marks multiple akeys including a nonexistent one, confirms corrupted akeys reject fetch/update/punch, and proves a separate akey under the same dkey remains readable.

`vts_mark_4` calls `vts_mark_discard` for object, flat KV key, and integer akey cases. The helper marks corruption, asserts forced aggregation fails with `-DER_DATA_LOSS`, then discards the object or dkeys and verifies existence-check fetch returns `-DER_NONEXIST`. `vts_mark_5` calls `vts_mark_delete` for corrupted object, dkey, and akey deletion and confirms direct delete/key-delete removes the target.

## State And Persistence Behavior
The tests create persistent VOS object tree entries, mark corruption at different hierarchy levels, and verify that corruption state blocks normal IO until discard or delete removes it. `vts_mark_discard` uses epoch ranges and forced aggregation flags to prove aggregation refuses to merge corrupted state, while `vos_discard` can clear it. The flat KV case expects akey-level corruption to fail with `-DER_NO_PERM` and then falls back to dkey-level corruption.

## Dependencies And Integration Points
The file depends on DAOS common/VOS types and the shared `vts_io.h` fixture. It integrates with CMocka through `mark_tests` and `run_mark_tests`, using `setup_io` and `teardown_io`. It exercises VOS APIs `vos_obj_update`, `vos_obj_fetch`, `vos_obj_punch`, `vos_obj_mark_corruption`, `vos_aggregate`, `vos_discard`, `vos_obj_del_key`, and `vos_obj_delete`.

## Risks And Test Signals
The tests encode exact error-code contracts for corrupted data paths. A risk is that they rely on sleeps around aggregation/discard, which can add runtime and may hide timing assumptions. Strong signals include `-DER_INVAL` for invalid mark arguments, `-DER_NO_PERM` for flat akey marks, `-DER_DATA_LOSS` while corruption exists, successful repeat and nonexistent-target marking, and `-DER_NONEXIST` after discard/delete.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_mark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_mvcc.c -->
# sources/object-store/daos/src/vos/tests/vts_mvcc.c

## Purpose
`vts_mvcc.c` is a matrix-driven test suite for VOS multi-version concurrency control rules. It validates read/write conflict behavior, conditional operations, timestamp-only reads, listings, key queries, punches, distributed transactions, delayed commit/in-progress behavior, and epoch uncertainty checks against the MVCC rules documented in the VOS README.

## Important APIs, Types, And Functions
`struct tx_helper` tracks a current DTX handle, saved XID, operation counts, write counts, operation sequence, epoch uncertainty bound, and skip-commit state. `struct mvcc_arg` provides unique path/object generation, fail-fast behavior, base epoch, and delayed-commit control.

The operation model is `struct op`, combining operation name, type (`T_R`, `T_RTU`, `T_RW`, `T_W`), read/write hierarchy levels (`L_C`, `L_O`, `L_D`, `L_A`), read/write state predicates, and an `op_func_t`. The `operations` table lists fetches, conditional fetches, list operations, existence checks, max/min key queries, read timestamp updates, conditional updates, conditional punches, plain update, and plain punches.

Helper functions such as `set_path`, `set_oid`, `set_dkey`, `set_akey`, and `set_value` make deterministic overlapping hierarchy paths. `start_tx` and `stop_tx` lazily create DTX handles and commit, save, or clean them up. Wrappers `tx_fetch`, `tx_update`, `tx_punch`, `tx_list`, and `tx_query` adapt VOS APIs to the operation table.

## Control Flow
`conflicting_rw` iterates every read/read-timestamp/readwrite operation against every readwrite/write operation. `conflicting_rw_exec` generates overlapping paths and runs empty and nonempty cases across five epoch/transaction shapes: read epoch greater than write epoch, equal epochs in different TXs, equal epochs in the same TX, read epoch less than write epoch, and delayed commit for readwrite reads. `conflicting_rw_exec_one` prepares data when required, computes expected read and write results, handles known excluded DAOS-4698 cases when punch propagation is disabled, and verifies `-DER_TX_RESTART`, `-DER_EXIST`, `-DER_NONEXIST`, or `-DER_INPROGRESS` as appropriate.

`uncertainty_check` iterates every plain write against every non-read-timestamp operation. `uncertainty_check_exec` runs each pair with writes at the uncertainty bound committed, at the bound uncommitted, and above the bound. `uncertainty_check_exec_one` prepares nonempty state, executes the write under a DTX with a bound, then checks the later operation for restart, existence predicate failure, or success. Punches get special handling because parent punch prevention and read timestamp side effects can also produce `-DER_TX_RESTART`.

## State And Persistence Behavior
Each case uses a unique integer object/key path encoded from the matrix index and string path such as `coda`, so operations overlap at container, object, dkey, or akey levels while avoiding unintended cross-case collisions. The tests intentionally leave some DTXs uncommitted, save XIDs, later commit them, and rerun blocked operations to validate transition from in-progress to final conflict result. Read timestamp update operations use `VOS_OF_FETCH_SET_TS_ONLY`, and uncertainty checks use `th_epoch_bound` to validate timestamp uncertainty behavior.

## Dependencies And Integration Points
The file depends on `vts_io.h` for the VOS fixture and DTX helpers and `vts_array.h` through the test environment. It integrates through `run_mvcc_tests`, which reads `DAOS_DKEY_PUNCH_PROPAGATE` to decide whether DAOS-4698 excluded cases apply, and `CMOCKA_TEST_ABORT` for fail-fast behavior. It exercises `vos_obj_fetch_ex`, `vos_obj_update_ex`, `vos_obj_punch`, `vos_iterate`, `vos_obj_query_key`, `vos_dtx_commit`, and `vos_dtx_cleanup`.

## Risks And Test Signals
This suite produces a large matrix and is sensitive to exact MVCC semantics. Some TODOs in the file note that transaction begin/commit and epoch flow could be simplified, so the current harness is powerful but complex. Expected failures are exact error codes: `-DER_TX_RESTART` for stale/conflicting writes, `-DER_INPROGRESS` for delayed commit visibility, `-DER_EXIST`/`-DER_NONEXIST` for conditionals, and success when epochs or bounds permit the operation. The printed case identifiers are important diagnostics when a matrix entry fails.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_mvcc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_pm.c -->
# sources/object-store/daos/src/vos/tests/vts_pm.c

## Purpose
`vts_pm.c` is the VOS punch-model and conditional-operation test suite. It validates array size and punch behavior through `vts_array`, object/dkey/akey/recx punch visibility, conditional update/fetch/punch semantics, minor-epoch punch ordering, aggregation after removals and uncommitted records, EC-size query behavior, and stress scenarios with many transactions and keys.

## Important APIs, Types, And Functions
`struct pm_info` stores the array object ID, array handle, epoch, and fixed update/fetch/fill buffers for array tests. `pm_setup` allocates and opens a VOS test array; `pm_teardown` closes and frees it. `struct counts` plus `count_cb`, `vos_check`, `vos_check_obj`, `vos_check_dkey`, `vos_check_akey`, and `vos_check_recx` provide recursive iterator assertions for visible and punched entries.

Array helpers include `array_set_get_size`, `array_size_write`, `array_read_write_punch_size`, and typed wrappers `array_1` through `array_4`. Punch-model helpers include `punch_model_test`, `simple_multi_update`, `object_punch_and_fetch`, `sgl_test`, `remove_test`, `small_sgl`, `minor_epoch_punch_sv`, `minor_epoch_punch_array`, and `minor_epoch_punch_rebuild`.

Conditional helpers are `obj_punch_op`, `cond_dkey_punch_op`, `cond_akey_punch_op`, `cond_fetch_op_`, `cond_updaten_op_`, and `cond_update_op_`. Stress and transaction helpers include `multiple_oid_cond_test`, `many_keys`, `test_inprogress_parent_punch`, `struct vos_ioreq`, `do_punch`, `do_io`, `many_tx`, `execute_op`, `uncommitted_parent`, `test_uncommitted_key`, and `test_multiple_key_conditionals_common`.

## Control Flow
`run_pm_tests` runs two CMocka groups: broad punch-model tests and PMDK/conditional tests. The array tests repeatedly reset array layout parameters, write data, read it back, shrink logical size with punches, and verify holes are filled with the sentinel fill buffer. `punch_model_test` layers updates and akey/dkey/object punches at successive epochs, checks fetch visibility before and after punches, validates recursive iterator counts with and without `VOS_IT_PUNCHED`, and verifies `vos_obj_query_key` max recx and max-write results.

The conditional suite first exercises single dkey/akey predicates, object punches, conditional fetches both with and without DTX, duplicate akey rejection, and many deterministic OIDs. Multi-key conditional tests use `DAOS_COND_PER_AKEY` to combine per-IOD akey predicates with dkey predicates, with and without explicit DTX commit. `many_tx` generates deterministic pseudo-random operations across object/dkey/akey grids, keeps a ring of in-flight transactions, periodically commits older DTXs, aggregates older epoch ranges, deletes objects, and repeats the run.

Minor-epoch tests create multi-op DTXs where update and punch share a major epoch but differ by operation sequence. They verify that a same-transaction punch hides the earlier minor update, array updates after punches remain visible where expected, and rebuild replay flags (`VOS_OF_REPLAY_PC`) order punch and update correctly.

## State And Persistence Behavior
The file is almost entirely about persistent state transitions. It checks that logical array size is represented through punches, punched entries may or may not be visible to iterators based on flags, holes preserve old fill values, object-level punches mask older children, and later updates after punches reestablish visibility. `remove_test` directly calls `vos_obj_array_remove` over epoch ranges and confirms aggregation preserves the same hole/data layout. Uncommitted-parent tests ensure later commits of parent punches or child updates resolve visibility correctly after DTX commit and aggregation.

EC-size simulation uses special recx indexes with `DAOS_EC_PARITY_BIT` and `VOS_GET_RECX_EC` to verify object size calculations across parity records, data holes, punched stripes, later parity, and merged holes. Conditional and many-transaction tests maintain prepared, committed, and skipped transaction states to exercise conflict and existence handling.

## Dependencies And Integration Points
The suite depends on `vts_io.h`, `vts_array.h`, VOS object/update/fetch/punch/query/aggregate APIs, DTX helper APIs, DAOS conditional flags, iterator APIs, and CMocka. It uses `setup_io`/`teardown_io` as the group fixture and per-test `test_args_reset` to isolate persistent pool state. `DAOS_ON_VALGRIND` reduces buffer/key counts for runtime control.

## Risks And Test Signals
This file contains expensive stress paths (`many_keys`, `many_tx`, `multiple_oid_cond_test`, EC simulation) and exact visibility expectations across complicated punch and DTX ordering. It is sensitive to changes in under-punch prevention, minor-epoch encoding, aggregation, object query-key semantics, and conditional flag interpretation. Strong signals include exact return-code assertions (`-DER_NONEXIST`, `-DER_EXIST`, `-DER_TX_RESTART`, `-DER_INPROGRESS`, `-DER_REC2BIG`, `-DER_NO_PERM`), buffer equality against expected holes/data, iterator counts for punched and visible entries, and EC object size values after each simulated stripe transition.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_pm.c -->
