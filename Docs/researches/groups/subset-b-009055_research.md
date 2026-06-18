# Research report: subset-b-009055

This grouped report covers the exact source files assigned to work item `subset-b-009055`. Each file section is bounded by reconciliation markers so it can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_reconciliation_tracking.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_reconciliation_tracking.cpp

Purpose: Catch2 regression tests for reconciliation overflow tracking internals. The file reaches into `src/reconcile/reconcile_private.h` and `reconcile_inline.h` through unit-test entry points such as `__ut_ovfl_track_init`, `__ut_ovfl_discard_verbose`, `__ut_ovfl_discard_wrapup`, `__ut_ovfl_reuse_wrapup`, `__ut_ovfl_reuse_wrapup_err`, plus production helper `__wti_ovfl_reuse_add`.

Important setup: `connection_wrapper` opens a real WiredTiger home so allocation/free paths run against a real session. `block_free_fail` and `setup_failing_bm` install a minimal `WT_BM` whose `free` method returns `EINVAL`, wiring it through `WT_BTREE`, `WT_DATA_HANDLE`, and `session->dhandle`.

Control flow: tests allocate zeroed `WT_PAGE` and `WT_PAGE_MODIFY`, initialize overflow tracking, exercise empty discard wrapup, then add an overflow reuse entry and force wrapup through the block-free failure branch. They clear `WT_OVFL_REUSE_INUSE` and `WT_OVFL_REUSE_JUST_ADDED` flags to make the entry eligible for reuse wrapup.

State and persistence: this is in-memory reconciliation state only. The key state is `page.modify->ovfl_track`, `page.memory_footprint`, and the session dhandle's block manager. Tests assert failed block frees restore memory footprint to zero and propagate `EINVAL`.

Dependencies/integration: depends on real WiredTiger connection lifecycle, internal reconciliation headers, block manager function pointers, `__wt_ovfl_reuse_free`, and `__wt_free`. Risks are high coupling to private layout and UT wrapper names. Test signals are direct `REQUIRE` checks for allocation, error propagation, and cleanup invariants.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_reconciliation_tracking.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_semaphore.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_semaphore.cpp

Purpose: Catch2 tests for WiredTiger semaphore primitives: `__wt_semaphore_init`, `__wt_semaphore_post`, `__wt_semaphore_wait`, and `__wt_semaphore_destroy`.

Important types/APIs: uses `WT_SEMAPHORE`, `WT_SESSION_IMPL`, `mock_session::build_test_mock_session`, C++ `std::thread`, `std::list`, and `std::atomic<int>` to validate both single-threaded counting semantics and wakeup behavior.

Control flow: the basic test covers init/destroy with zero and nonzero initial counts, post-then-wait, and multiple posts followed by multiple waits. The threaded test starts four waiter threads blocked on a zero-count semaphore, sleeps briefly to let them block, posts four times, joins threads, and verifies all waiters ran. A producer-consumer section posts ten units and consumes ten units.

State and persistence: no persistent state. Runtime state is the semaphore count plus `counter`. Correctness depends on semaphore wakeups not being lost and the mock session being sufficient for error reporting.

Dependencies/integration: integrates with WT portability synchronization code through `wt_internal.h`; the mock session supplies a minimal `WT_SESSION_IMPL`. Risks include timing sensitivity from the fixed 100 ms sleep and platform semaphore semantics. Test signals are successful return codes and final counter values.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_semaphore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_session_config.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_session_config.cpp

Purpose: Disabled Catch2 tests for internal session configuration parsing via `__ut_session_config_int`. The whole file is under `#ifdef ENABLE_DISABLED_TEST`, so it documents intended behavior but normally does not compile into the test target.

Important APIs/types: `mock_session`, `WT_SESSION_IMPL`, `F_ISSET`, session flags such as `WT_SESSION_IGNORE_CACHE_SIZE`, `WT_SESSION_CACHE_CURSORS`, debug flags, and `session->cache_max_wait_us`.

Control flow: `test_config_flag` builds `param=true` and `param=false`, asserts that `__ut_session_config_int` sets and clears flags, then feeds an invalid string and expects `EINVAL` plus an "Unbalanced" callback message while preserving the prior flag. The `cache_max_wait_ms` test verifies conversion to microseconds, zero behavior, invalid/unknown strings being ignored, negative input clamping to zero, and special handling where `cache_max_wait_ms=1` maps to `1`.

State and persistence: all state is transient in the mock session. It mutates session flags, callback messages, and `cache_max_wait_us`.

Dependencies/integration: tightly coupled to a unit-test wrapper around session config internals and mock event handler message capture. Risks are that disabled tests can drift from production behavior. Test signals, when enabled, are flag bit checks, numeric session field checks, and error-message observation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_session_config.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_single_thread_check.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_single_thread_check.cpp

Purpose: Diagnostic-only Catch2 test for `__wt_single_thread_check_start` assertion reporting when optional session fields are null.

Important conditions/APIs: compiled only when both `HAVE_DIAGNOSTIC` and `HAVE_UNITTEST_ASSERTS` are defined. Uses `mock_session`, `WT_SESSION_IMPL`, `session->thread_check.lock`, `__wt_spin_lock`, `__wt_spin_unlock`, `__wt_thread_id`, and unittest assertion capture fields `unittest_assert_hit` and `unittest_assert_msg`.

Control flow: the test sets `session->id`, manually takes the thread-check spin lock to force `__wt_spin_trylock` inside the check to return `EBUSY`, calls `__wt_single_thread_check_start`, then compares the captured assertion text to an exact string. The crafted expected string proves null name, last op, dhandle, and owning thread fields are rendered as `none`/`0` instead of crashing.

State and persistence: no persistent state. It mutates diagnostic lock state and assertion capture fields, then releases the lock.

Dependencies/integration: integrated with WiredTiger diagnostic assertion plumbing and thread-id formatting. Risks are exact-message brittleness across wording changes and platform thread id formatting. Test signals are assertion-hit flag and exact assertion message.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_single_thread_check.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_string_match.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_string_match.cpp

Purpose: Unit tests for string/config matching macros: `WT_STRING_LIT_MATCH`, `WT_CONFIG_LIT_MATCH`, `WT_STRING_MATCH`, and `WT_CONFIG_MATCH`.

Important APIs/types: uses `WT_CONFIG_ITEM` with explicit `str` and `len` to verify length-aware matching, including inputs that are not necessarily null-terminated. Literal macros require literal left operands; generic macros support variables.

Control flow: the test creates a `green` config item (`"green"`, length 5), an empty config item, literal/variable strings, and a guarded null pointer. Each section loops twice: first with `green.str` exactly `"green"`, then with `"greenery"` while retaining `green.len == 5`, proving comparisons honor the supplied length rather than C string termination. It checks shorter, longer, different, empty, and null-plus-zero-length cases.

State and persistence: no persistent state. The only mutation is changing `green.str` between loop iterations.

Dependencies/integration: depends on macro definitions in `wt_internal.h` and compiler behavior around literal macros. Risks include misuse of literal macros with non-literals, intentionally noted in comments. Test signals are boolean macro results for literal and variable paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_string_match.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_tailq.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_tailq.cpp

Purpose: Catch2 coverage for WiredTiger/BSD `TAILQ` macros through a small C++ wrapper.

Important types/functions: template `tailq_entry<T>` embeds `TAILQ_ENTRY`; `TestTailQWrapper<T>` owns a `TAILQ_HEAD`, implements `pushBack`, `removeValue`, `copyItemsFromTailQ`, and a destructor that drains/free entries.

Control flow: constructor initializes the queue with `TAILQ_HEAD_INITIALIZER`. `pushBack` allocates an entry with `malloc` and inserts at tail. `removeValue` walks from `TAILQ_FIRST`, stores `TAILQ_NEXT` before removal, removes/free the first matching value, and stops. `copyItemsFromTailQ` uses `TAILQ_FOREACH` to copy values into `std::list`.

State and persistence: state is heap entries linked through `_queue`. There is no storage persistence. Correctness includes preserving insertion order, removing only one match, no-op on missing values, and no-op removal from empty queue.

Dependencies/integration: depends on `TAILQ_*` macros from `wt_internal.h`. Risks include manual allocation without placement-new for nontrivial `T`; tests only instantiate `int`. Test signals compare copied lists against expected `std::list<int>` values and empty-list behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_tailq.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_verify_compare_page_id_lists.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_verify_compare_page_id_lists.cpp

Purpose: Unit tests for `__ut_verify_compare_page_id_lists`, the merge-compare helper that validates two sorted page-id arrays.

Important APIs/types: `run_compare` accepts vectors by value for btree ids and by value for PALI ids, then passes raw `uint64_t *` data and sizes to the internal helper using a mock session.

Control flow: the test checks exact matches, both empty, singleton match, and mismatch cases where either list is exhausted first, interleaved values differ, all entries mismatch, one side is empty, and multiple trailing entries differ. The helper is expected to return `0` only for exact equality and `EINVAL` for any mismatch.

State and persistence: no persistent state. The vectors are local inputs; the mock session is for helper logging/error context.

Dependencies/integration: integrates verification code for disaggregated page-id list comparison and depends on sorted-array semantics. Risks are that tests do not cover unsorted input or duplicate handling separately. Test signals are return codes from `__ut_verify_compare_page_id_lists`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_verify_compare_page_id_lists.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/api/test_sub_level_error_session_get_last_error.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/api/test_sub_level_error_session_get_last_error.cpp

Purpose: Public API test for `WT_SESSION::get_last_error`, focused on default session error-info state.

Important APIs/types: `connection_wrapper` opens a real connection, `conn->open_session` creates a public `WT_SESSION`, and `session->get_last_error` fills `err`, `sub_level_err`, and `err_msg`.

Control flow: the test creates a connection in the current directory with `create`, opens a session, calls `get_last_error` before any failure, and asserts default values: primary error `0`, sub-level error `WT_NONE`, and message `WT_ERROR_INFO_SUCCESS`.

State and persistence: the underlying connection creates WiredTiger files through `connection_wrapper`; error state is per-session and initially reset. No table data is created.

Dependencies/integration: validates that public API surfaces the internal `WT_ERROR_INFO` initialization contract. It depends on `utils_sub_level_error.h` only for shared declarations and on connection cleanup. Risks are minimal but it only covers defaults, not non-default API retrieval. Test signals are exact returned values from `get_last_error`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/api/test_sub_level_error_session_get_last_error.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/api/test_sub_level_error_strerror.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/api/test_sub_level_error_strerror.cpp

Purpose: Public API coverage for `wiredtiger_strerror` when passed WiredTiger sub-level error codes.

Important APIs/types: `check_error_code` converts an integer error code to `std::string` through `wiredtiger_strerror` and compares it to the expected symbolic description.

Control flow: one section iterates a vector of `(code, expected string)` pairs for all listed sub-level codes: `WT_NONE`, background compact already running, cache overflow, write conflict, oldest-for-eviction, backup/dhandle/schema/table/checkpoint/live-restore/disaggregated conflicts, uncommitted data, and dirty data.

State and persistence: stateless API mapping test; no connection/session is opened.

Dependencies/integration: integrates public error-code rendering with the sub-level error enum namespace. Risks are exact-string brittleness and incomplete coverage if new sub-level codes are added without updating this vector. Test signals are exact string comparisons.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/api/test_sub_level_error_strerror.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_api_end.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_api_end.cpp

Purpose: Unit tests for API-end macros preserving or resetting session last-error information: `API_END_RET` and `TXN_API_END`.

Important helpers/APIs: `api_call_with_error` wraps `SESSION_API_CALL_NOCONF`, optional `__wt_session_set_last_error`, and `API_END_RET`. `txn_api_call_with_error` wraps `SESSION_TXN_API_CALL` and `TXN_API_END`. Shared `check_error_info` verifies `WT_ERROR_INFO`.

Control flow: the test opens a real session, then exercises no-error, primary-error-only, error with message, repeated message, different messages, and EBUSY with different sub-level errors. It repeats analogous coverage for transaction API end paths.

State and persistence: state is `session_impl->err_info`. Successful API completion resets to success; errors without explicit messages produce `WT_ERROR_INFO_EMPTY`; explicit last errors preserve primary code, sub-code, and message through API-end macros. Connection files are created and cleaned by wrapper.

Dependencies/integration: depends on WiredTiger public connection/session and internal API macros. Risks include macro-flow fragility and exact behavior around repeated messages. Test signals are return codes plus `WT_ERROR_INFO` contents after each API call.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_api_end.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_compact.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_compact.cpp

Purpose: Regression tests for sub-level error handling in background compaction configuration paths, especially `__wt_background_compact_signal`.

Important APIs/types: real `WT_SESSION_IMPL`, `WT_CONNECTION_IMPL`, connection flags `WT_CONN_IN_MEMORY` and `WT_CONN_READONLY`, `conn_impl->background_compact.running/config`, and `WT_BACKGROUND_COMPACT_ALREADY_RUNNING`.

Control flow: sections check unsupported in-memory/readonly database returns `ENOTSUP` without changing last-error info; missing `background` config returns `WT_NOTFOUND`; `background=false` and `background=true` succeed; matching an already-running configuration succeeds; and attempting to reconfigure a running background compact with a different config returns `EINVAL` and records the sub-level error plus message.

State and persistence: mutates connection flags and background compact state. The test resets flags/config where needed so connection close remains valid. Error-info persistence is per session.

Dependencies/integration: tied to compaction config parser and connection state. Risks are manual mutation of internal connection fields and ownership of `background_compact.config` strings. Test signals include return codes and `check_error_info`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_compact.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_drop_conflict.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_drop_conflict.cpp

Purpose: Tests `WT_SESSION::drop` conflict paths that return `EBUSY` with specific sub-level errors and messages.

Important APIs/types: real connection/session wrappers, `prepare_session_and_error`, public cursor/drop APIs, lock macros `WT_WITH_CHECKPOINT_LOCK`, `WT_WITH_SCHEMA_LOCK`, `WT_WITH_TABLE_WRITE_LOCK`, and sub-level codes `WT_CONFLICT_BACKUP`, `WT_CONFLICT_DHANDLE`, `WT_CONFLICT_CHECKPOINT_LOCK`, `WT_CONFLICT_SCHEMA_LOCK`, `WT_CONFLICT_TABLE_LOCK`.

Control flow: first test creates a table and attempts drop while a backup cursor or table cursor remains open, covering simple tables, column-mapped tables, and POSIX tiered storage. Second test opens two sessions and attempts a lock-wait-zero drop while another session holds checkpoint, schema, or table write lock. Windows skips checkpoint/schema lock sections because spin lock behavior differs in same-thread tests.

State and persistence: creates/drop tables, cursors, optional tiered-storage home `WT_TEST`, and session error state. Cleanup closes cursors and drops tables after conflict checks.

Dependencies/integration: public schema/drop paths, backup cursor, tiered extension path, lock implementation, and test utility shell commands. Risks include platform-specific behavior, extension availability, and exact error messages. Test signals are `EBUSY` return plus exact `WT_ERROR_INFO`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_drop_conflict.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_drop_uncommitted_dirty.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_drop_uncommitted_dirty.cpp

Purpose: Tests dhandle-close/drop conflict sub-level errors for uncommitted or dirty table data.

Important APIs/types: `__wt_session_get_dhandle`, `__wt_conn_dhandle_close`, `__wt_session_release_dhandle`, `S2BT(session_impl)`, dhandle flag `WT_DHANDLE_IS_METADATA`, btree flag `WT_BTREE_BULK`, `WT_SESSION_LOCKED_SCHEMA`, and sub-level codes `WT_UNCOMMITTED_DATA` and `WT_DIRTY_DATA`.

Control flow: after creating a table and acquiring its file dhandle, sections vary visibility-check flag, `max_upd_txn`, schema lock, btree `modified`, bulk mode, and metadata handle flags. The expected EBUSY cases are only: visibility-check enabled with uncommitted txn state, and schema-locked close of a modified non-bulk non-metadata btree.

State and persistence: mutates internal btree/dhandle fields and session lock flags. At the end it resets `max_upd_txn`, `modified`, bulk and metadata flags, releases dhandle, and drops the table.

Dependencies/integration: tightly coupled to dhandle close logic and btree dirty/uncommitted checks. Risks include manual internal field manipulation and need for precise cleanup to avoid drop failures. Test signals are return codes and exact error-info triples.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_drop_uncommitted_dirty.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_is_valid_sub_level_error.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_is_valid_sub_level_error.cpp

Purpose: Unit test for `__wt_is_valid_sub_level_error`.

Important APIs/types: tests normal WiredTiger primary error codes and integer boundaries of the sub-level error range. The comment states valid sub-level codes range from `-32000` through `-32199` inclusive, with `WT_NONE` also valid.

Control flow: the test asserts normal codes such as `WT_ROLLBACK`, `WT_DUPLICATE_KEY`, `WT_ERROR`, `WT_NOTFOUND`, `WT_PANIC`, `WT_RESTART`, `WT_RUN_RECOVERY`, `WT_CACHE_FULL`, `WT_PREPARE_CONFLICT`, and `WT_TRY_SALVAGE` are not classified as sub-level errors. It then checks `WT_NONE`, lower/upper valid boundaries, and just-outside values.

State and persistence: no state or persistence; pure predicate testing.

Dependencies/integration: depends on the numeric allocation of primary and sub-level error namespaces. Risks are stale boundary assumptions if the reserved range changes. Test signals are boolean checks from `__wt_is_valid_sub_level_error`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_is_valid_sub_level_error.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_live_restore_conflict.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_live_restore_conflict.cpp

Purpose: Tests live-restore conflict reporting for backup cursor creation.

Important APIs/types: `utils::live_restore_test_env` supplies a live-restore-enabled connection, `prepare_session_and_error` opens a session and exposes `WT_ERROR_INFO`, and `session->open_cursor("backup:")` is expected to fail with `EINVAL`.

Control flow: within the section, the test prepares a session from the live-restore environment, attempts to open a backup cursor, asserts the cursor remains `NULL`, and checks `WT_CONFLICT_LIVE_RESTORE` with message "backup cannot be taken when live restore is enabled".

State and persistence: the live-restore environment owns the connection/home setup. The test mutates only session error state and a cursor output pointer.

Dependencies/integration: integrates live restore test environment, public backup cursor path, and sub-level error storage. Risks are dependency on live_restore fixture setup and exact message text. Test signals are `EINVAL`, null cursor, and exact error info.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_live_restore_conflict.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_msg_macros.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_msg_macros.cpp

Purpose: Unit tests for last-error message macros `WT_RET_SUB`, `WT_ERR_SUB`, `WT_RET_MSG`, and `WT_ERR_MSG`.

Important helpers/APIs: four small static functions invoke the macros against a `WT_SESSION_IMPL`. The `_SUB` variants set both primary and sub-level error; `_MSG` variants set primary error with `WT_NONE`.

Control flow: a real connection/session is opened, `err_info` is captured, and each section calls one helper with `EINVAL` and a message. Expected results are `EINVAL` return and error-info state matching the macro semantics. `_SUB` tests use `WT_BACKGROUND_COMPACT_ALREADY_RUNNING`; `_MSG` tests assert sub-level remains `WT_NONE`.

State and persistence: per-session `WT_ERROR_INFO` is the only meaningful state. Connection files are wrapper-managed.

Dependencies/integration: covers macro control-flow forms that either return immediately or jump to `err:`. Risks are low, but exact behavior depends on macro expansion and session error-message allocation. Test signals are return code and `check_error_info`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_msg_macros.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_nested_api_calls.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_nested_api_calls.cpp

Purpose: Tests how nested API calls affect session last-error state, especially `WT_NOTFOUND` handling inside top-level API flow.

Important APIs/types: `CURSOR_API_CALL`, `SESSION_API_CALL_NOCONF`, `WT_ERR_NOTFOUND_OK`, `WT_ERR`, `API_END_RET`, `__wt_session_set_last_error`, and a real table cursor.

Control flow: `cursor_api_call_with_notfound` simulates cursor `next` returning `WT_NOTFOUND` and optionally explicitly sets last error. `api_call_nested_with_notfound` invokes that nested cursor API either through `WT_ERR_NOTFOUND_OK` or `WT_ERR`, then optionally simulates a later `EINVAL`. Sections cover combinations of notfound-ok vs notfound-error, final error zero vs EINVAL, and nested explicit err_info vs implicit error-only return.

State and persistence: creates a table and cursor; session `err_info` is the core state. Explicitly set nested error info can be preserved across later top-level errors in selected paths.

Dependencies/integration: validates subtle API nesting rules, error discard behavior, and cursor/table setup. Risks are high semantic complexity and exact expected precedence. Test signals are top-level return code plus error-info content.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_nested_api_calls.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_rollback.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_rollback.cpp

Purpose: Broad regression tests for rollback-related sub-level errors in eviction, transaction blocking, modify reconstruction, and write conflicts.

Important APIs/types: `__wt_evict_app_assist_worker_check`, `__wti_evict_app_assist_worker`, `__txn_modify_block`, `__wt_txn_is_blocking`, `__wt_modify_reconstruct_from_upd_list`, `WT_ROLLBACK`, and sub-level codes `WT_CACHE_OVERFLOW`, `WT_OLDEST_FOR_EVICTION`, `WT_WRITE_CONFLICT`, `WT_MODIFY_READ_UNCOMMITTED`.

Control flow: sections configure internal connection cache/eviction state, txn mod counts, shared txn ids, operation timeout, transaction isolation, and update chains. They assert no error for safe eviction cases and prepared/unsupported blocking cases; assert `WT_ROLLBACK` with oldest-for-eviction when the transaction pins oldest id; assert cache overflow when app eviction times out; assert write conflict for invisible update; and assert read-uncommitted modify reconstruction rollback.

State and persistence: creates/drops a table for cursor/cache and write-conflict setup. Mutates connection cache, eviction flags, transaction snapshot fields, dhandle allocation, and `WT_UPDATE` structures.

Dependencies/integration: very coupled to internal eviction/transaction visibility code. Risks include fragile manual state fabrication and cleanup requirements. Test signals are return codes and exact `WT_ERROR_INFO`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_rollback.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_session_set_last_error.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_session_set_last_error.cpp

Purpose: Unit tests for `__wt_session_set_last_error` and `__wt_session_reset_last_error`.

Important APIs/types: real `WT_SESSION_IMPL`, `WT_ERROR_INFO`, sub-level codes including `WT_BACKGROUND_COMPACT_ALREADY_RUNNING`, `WT_CONFLICT_BACKUP`, `WT_UNCOMMITTED_DATA`, and `WT_DIRTY_DATA`.

Control flow: sections verify null-session reset is safe, reset initializes success values, set stores `EINVAL` plus sub-level code/message, subsequent set does not overwrite an existing error until reset, multiple set/reset cycles work for different primary/sub-level pairs, and a 1024-byte message is stored and compared.

State and persistence: only `session_impl->err_info` changes. Connection files are wrapper-managed. The non-overwrite behavior is the central persistence rule within a session error lifecycle.

Dependencies/integration: depends on error-message allocation/copy and reset freeing/replacing prior state. Risks include exact large-message behavior and non-overwrite semantics being surprising to callers. Test signals are `check_error_info` after each mutation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_session_set_last_error.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/utils_sub_level_error.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/utils_sub_level_error.cpp

Purpose: Shared Catch2 helper implementation for sub-level error tests.

Important functions: `utils::prepare_session_and_error` opens a public session from a `connection_wrapper`, asserts success, and returns both `WT_SESSION *` and a pointer to the internal `WT_ERROR_INFO`. `utils::check_error_info` compares primary error, sub-level error, and error message string.

Control flow: helpers are intentionally small and assertion-heavy. `prepare_session_and_error` relies on the wrapper's `WT_CONNECTION` and casts the opened session to `WT_SESSION_IMPL` to expose `err_info`. `check_error_info` performs three Catch2 `CHECK` assertions, including `strcmp` on the message.

State and persistence: opens sessions on real connections and exposes mutable per-session error state to tests. It does not own or close sessions; connection lifetime is managed by the caller's wrapper.

Dependencies/integration: used by API/drop/compact/rollback sub-level tests. Risks include raw pointer exposure and assuming `err_msg` is non-null when passed to `strcmp`. Test signals are helper assertions embedded in calling tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/utils_sub_level_error.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/utils_sub_level_error.h -->
## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/utils_sub_level_error.h

Purpose: Declaration header for shared sub-level error test helpers.

Important APIs/types: includes Catch2, `wt_internal.h`, and `connection_wrapper.h`; declares `utils::prepare_session_and_error(connection_wrapper *, WT_SESSION **, WT_ERROR_INFO **)` and `utils::check_error_info(WT_ERROR_INFO *, int, int, const char *)`.

Control flow/state: no runtime control flow beyond declarations. Its role is to standardize how tests open sessions and assert `WT_ERROR_INFO` triples.

Dependencies/integration: included by API and unit tests in `sub_level_error`. It creates a dependency from test files to the C++ connection wrapper and internal `WT_ERROR_INFO` type. Risks are broad rebuild coupling and potential namespace/helper name collisions if other test utilities add similar functions. Test signals are indirect through the implementation's Catch2 assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/utils_sub_level_error.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/test_insert_truncate_entry.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/truncate/test_insert_truncate_entry.cpp

Purpose: Integration-style Catch2 tests for follower layered-table truncate insertion through `__wt_insert_truncate_entry`.

Important fixtures/APIs: `follower_connection` opens a real disaggregated follower connection with PALite page log, creates `layered:test_truncate_list`, opens a layered cursor, begins a transaction, exposes `WT_LAYERED_TABLE`, and cleans transaction ops in its destructor. Helpers insert one or many entries and create GC-eligible committed entries.

Control flow: scenarios verify insertion returns 0, creates exactly one list entry, increments the layered table dhandle reference only when transitioning from empty to non-empty, preserves `session->dhandle`, stores start/stop keys and layered table pointer, preserves insertion order, registers `WT_TXN_OP_FOLLOWER_TRUNCATE`, allows duplicate ranges, stamps `txn_id`, leaves timestamps unset until commit, releases the truncate lock, and triggers garbage collection of an eligible old entry.

State and persistence: real WiredTiger home `WT_TEST.truncate_list`, layered table metadata, transaction op array, truncate queue, dhandle references, and ingest btree prune timestamp are mutated. No committed user data is the focus; the list state is.

Dependencies/integration: depends on PALite extension, disaggregated follower configuration, layered cursor layout, transaction op cleanup, and truncate GC. Risks include extension availability and internal casts. Test signals are list size/order, refs, txn op contents, timestamps, and lock release.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/test_insert_truncate_entry.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_table_truncate_clear.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_table_truncate_clear.cpp

Purpose: Unit tests for `__wt_layered_table_truncate_clear`.

Important APIs/types: uses `truncate_list_fixture`, `truncate_list_size`, `reference_count`, and `lock_is_released` over a mock `WT_LAYERED_TABLE` containing a `truncateqh` queue and `truncate_lock`.

Control flow: scenarios build either a two-entry truncate list or an empty list, call clear, then assert all entries are removed, dhandle reference count is decremented exactly once only for non-empty lists, empty clear is a no-op, and the truncate write lock is not leaked.

State and persistence: purely in-memory list entries and reference counts. `truncate_list_fixture` handles lock initialization/destruction and any remaining entries.

Dependencies/integration: validates clear behavior without a real connection. It depends on helper fixture semantics that acquire a dhandle reference on the first entry. Risks include helper-created shallow keys and direct internal reference counting. Test signals are list size, reference count, and ability to acquire write lock after clear.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_table_truncate_clear.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_table_truncate_gc.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_table_truncate_gc.cpp

Purpose: Unit tests for truncate-list garbage collection via `__ut_layered_table_truncate_gc`.

Important helpers/APIs: `insert_durable_entry` creates an entry through `truncate_list_fixture::add_entry` and commits it through `commit_entry`, stamping durable timestamp. GC is called with a prune timestamp.

Control flow: scenarios cover zero prune timestamp no-op, uncommitted entries retained, entries with `WT_TS_NONE` durable timestamp retained, durable timestamp above prune retained, entries at or below prune removed, multi-entry lists with eligible/ineligible/uncommitted combinations, empty-list no-op, reference count unchanged when list remains non-empty, and reference count decremented exactly once when GC empties the list.

State and persistence: in-memory `WT_TRUNCATE` queue, committed flag/timestamps, and dhandle reference count. No disk persistence.

Dependencies/integration: focuses on internal eligibility rules: committed, nonzero durable timestamp, durable <= prune. Risks are timestamp boundary off-by-one bugs and reference leaks on partial/complete removal. Test signals are list size, head durable timestamp, and reference count.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_table_truncate_gc.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_table_truncate_rollback.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_table_truncate_rollback.cpp

Purpose: Unit tests for rollback of follower truncate transaction operations through `__wti_layered_table_truncate_rollback`.

Important helpers/APIs: `make_op` creates a `WT_TXN_OP` of type `WT_TXN_OP_FOLLOWER_TRUNCATE`; `rollback_truncate` calls the rollback helper. Uses fixture queue helpers and reference-count/lock checks.

Control flow: scenarios verify rollback removes a single entry from the list, clears the op pointer, releases the dhandle reference when the list becomes empty, releases the truncate lock, and in a three-entry list removes only the targeted middle entry while preserving order and leaving other operation pointers and reference count unchanged.

State and persistence: in-memory truncate queue, transaction op pointer, and table reference count. No disk state.

Dependencies/integration: verifies transaction rollback cleanup for layered truncate list entries. Risks include dangling op pointers, removing wrong queue node, reference underflow on non-empty lists, and lock leaks. Test signals are list size/order, op pointer nulling, reference counts, and lock acquisition after rollback.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_table_truncate_rollback.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_truncate_visibility.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_truncate_visibility.cpp

Purpose: Detailed unit tests for follower layered-table truncate visibility, centered on `__wt_truncate_delete_visible_check`, commit apply, and rollback apply behavior.

Important fixture/APIs: `layered_truncate_visibility_fixture` builds a mock session, transaction shared list, `WT_TXN`, and `WT_LAYERED_TABLE` with truncate queue/lock. Helpers set reader snapshot state, set committer time point, add truncate entries with copied keys, and call visibility check.

Control flow: tests cover own uncommitted truncate visible, other uncommitted truncate invisible, committed truncate gated by read timestamp, overlapping ranges with different timestamps, commit stamping through `__wti_mark_committed_truncate_table_apply`, durable timestamp and snapshot-window visibility, overlap precedence when a newly committed range becomes visible, and rollback removal through `__wti_layered_table_truncate_rollback_apply`.

State and persistence: all state is mock in-memory: txn snapshot min/max, shared read timestamp, truncate txn id, start/durable timestamps, committed flag, copied keys, queue links, and references.

Dependencies/integration: touches internal transaction visibility semantics, layered table queue traversal, key-copy outputs, and rollback/commit apply callbacks. Risks include subtle precedence rules for overlapping ranges and exact snapshot-window fabrication. Test signals are return codes, matched start/stop buffers, timestamp fields, committed flag, queue order, and op pointer clearing.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_truncate_visibility.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/test_truncate_visible_check.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/truncate/test_truncate_visible_check.cpp

Purpose: Unit tests for `__wt_truncate_delete_visible_check` as a range-membership and output-buffer helper.

Important fixture/APIs: `TruncVisibleCheckFixture` builds a mock session, transaction shared list, `WT_TXN`, heap `WT_LAYERED_TABLE`, `truncateqh`, rwlock, and helper `add_truncate_entry` using globally visible `WT_TXN_NONE` entries with string-literal keys.

Control flow: sections test misses for empty list, keys before/after ranges, single-key neighbors, and gaps between ranges; hits for strict interior, inclusive start/stop boundaries, single-key exact match, multiple non-overlapping ranges, and overlapping ranges. Additional sections prove read lock release after hit/miss/empty, optional output params, deep-copy of matched start/stop keys, correct range selected, and untouched output buffers on miss.

State and persistence: in-memory truncate entries, WT item buffers allocated for output keys, and lock state. Destructor drains entries and frees session/table structures.

Dependencies/integration: narrower than the full visibility fixture; it assumes entries are globally visible and focuses on range comparison, buffer copy, and lock discipline. Risks include raw string-literal key storage and exact inclusive-boundary expectations. Test signals are return code, output buffer contents, and ability to take write lock.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/test_truncate_visible_check.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/test_truncate_write_conflict.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/truncate/test_truncate_write_conflict.cpp

Purpose: Comprehensive integration tests for layered-table truncate write-conflict detection: `__wt_layered_table_truncate_detect_write_conflict` for single keys and `__wt_layered_table_truncate_detect_non_ingest_write_conflict` for ranges.

Important fixtures/APIs: `write_conflict_fixture` opens a real disaggregated follower/PALite connection, creates a layered table, opens a cursor, exposes the layered table, and creates additional sessions. Helpers format keys, run operations in committed/rolled-back/uncommitted transactions, set read timestamps, and roll back on scope exit.

Control flow: single-key scenarios cover empty list, outside ranges, inside inclusive boundaries, single-key ranges, multiple ranges, committed ranges not conflicting, own uncommitted range not conflicting, overlapping committed/uncommitted ranges, lock release, and committed truncate becoming a conflict for readers whose read timestamp predates the truncate. Non-ingest range scenarios cover empty list, non-overlap, inclusive-boundary overlap, committed and own-uncommitted exemptions, lock release, timestamp-gated committed conflicts, single-key range overlap, multiple ranges, and mixed committed/uncommitted overlaps.

State and persistence: real WT home `WT_TEST.truncate_write_conflict`, table/cursor state, transaction lifecycles, truncate list, timestamps, locks, and dhandle references.

Dependencies/integration: depends on PALite extension, disaggregated follower mode, public transaction API, layered cursor casts, and truncate visibility. Risks are high setup cost, extension availability, timestamp semantics, and rollback cleanup. Test signals are `0` vs `WT_ROLLBACK` return codes and lock release.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/test_truncate_write_conflict.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/truncate_list_helpers.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/truncate/truncate_list_helpers.cpp

Purpose: Shared helper implementation for layered truncate-list tests.

Important functions/types: `make_item`, `as_view`, `truncate_list_head`, `truncate_list_size`, `lock_is_released`, `last_txn_op`, and `truncate_list_fixture`. The fixture owns a mock session, `WT_LAYERED_TABLE`, truncate queue, and truncate rwlock.

Control flow: `make_item` creates a shallow `WT_ITEM` view over a `std::string_view`; `as_view` reverses that view. `truncate_list_size` iterates `TAILQ_FOREACH`. `lock_is_released` attempts a write lock and releases it on success. The fixture constructor initializes table name, queue, and lock. Destructor drains any remaining entries, releases the dhandle reference if data existed, and destroys the lock. `add_entry` allocates `WT_TRUNCATE`, acquires a dhandle reference only for first entry, shallow-copies keys, inserts at tail, and checks size. `commit_entry` builds a temporary `WT_TXN` and applies commit stamping.

State and persistence: purely in-memory helper state. Key storage is shallow and assumes string literals/static lifetimes unless callers use copied buffers.

Dependencies/integration: underpins all truncate list unit tests and wraps production functions `__wti_mark_committed_truncate_table_apply` and lock/reference macros. Risks include reference accounting assumptions and shallow-key lifetime. Test signals are helper `CHECK`/`REQUIRE` assertions plus caller checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/truncate_list_helpers.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/truncate_list_helpers.hpp -->
## sources/storage-engines/wiredtiger/test/catch2/truncate/truncate_list_helpers.hpp

Purpose: Header for shared layered truncate-list test utilities.

Important declarations: `truncate_range` alias, `make_item`, `as_view`, `truncate_list_head`, `truncate_list_size`, `lock_is_released`, `last_txn_op`, and class `truncate_list_fixture` with accessors for session, layered table, reference count, `add_entry`, and `commit_entry`.

Control flow/state: no implementation flow, but the public fixture contract exposes a mock-backed `WT_SESSION_IMPL`, an initialized `WT_LAYERED_TABLE`, and helper operations that manipulate `WT_TRUNCATE` entries and transaction commit state.

Dependencies/integration: includes Catch2, `wt_internal.h`, and `wrappers/mock_session.h`, binding tests to WiredTiger internals and mock sessions. It is included by truncate clear, GC, rollback, insert, visibility, visible-check, and write-conflict tests. Risks are broad coupling to private `WT_LAYERED_TABLE`, `WT_TRUNCATE`, and transaction op layouts. Test signals are indirect through the helpers' use in scenario files.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/truncate_list_helpers.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/utils.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/utils.cpp

Purpose: Shared Catch2 utility implementation for WiredTiger C++ tests.

Important functions: `utils::throw_if_non_zero` throws `std::runtime_error` on nonzero return codes; `remove_wrapper` wraps `std::remove`; `utils::wiredtiger_cleanup` removes known WiredTiger files and the home directory; `utils::break_here` emits Catch2 `INFO` for debugger breakpoints.

Control flow: cleanup intentionally ignores removal errors and deletes a fixed list of files such as `WiredTiger`, `WiredTiger.turtle`, `WiredTiger.wt`, `WiredTigerHS.wt`, backup/cursor test files, and then the directory. `break_here` records source file, line, and function.

State and persistence: affects filesystem state under the supplied DB home by removing database files. `throw_if_non_zero` affects test control flow by raising exceptions.

Dependencies/integration: used by connection/mock wrappers and tests needing cleanup or dynamic library error handling. Risks include cleanup list drift as WiredTiger creates new files, and `remove` only removing empty directories. Test signals are exceptions or Catch2 info context.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/utils.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/utils.h -->
## sources/storage-engines/wiredtiger/test/catch2/utils.h

Purpose: Shared utility declarations and a small RAII wrapper for dynamic libraries.

Important APIs/types: defines `DB_HOME` as `test_db`, `BREAK` macro, functions `break_here`, `throw_if_non_zero`, `wiredtiger_cleanup`, and class `utils::shared_library`.

Control flow: `shared_library` constructor opens a library with `__wt_dlopen`, destructor closes it with `__wt_dlclose`, copy operations are deleted, and templated `get` resolves a symbol with `__wt_dlsym`, throwing on failure through `throw_if_non_zero`.

State and persistence: `shared_library` owns a `WT_DLH *` handle for the object's lifetime. Other utilities manage cleanup externally.

Dependencies/integration: included by C++ wrappers and tests, depends on `wt_internal.h` dynamic loading abstractions. Risks include using `nullptr` session with dlopen/dlclose and process-global dynamic loader behavior. Test signals are exceptions from failed WT dynamic-loader calls and breakpoint info through Catch2.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/block_mods.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/wrappers/block_mods.cpp

Purpose: Implementation of a simple RAII wrapper around `WT_CKPT_BLOCK_MODS` for tests.

Important functions: constructor calls `init_block_mods`; destructor frees `_block_mods.bitstring` with `__wt_buf_free` and `_block_mods.id_str` with `__wt_free`; `init_block_mods` zeroes all pointer, size, numeric, and flag fields.

Control flow: initialization is explicit rather than using `memset`, assigning every field of the public checkpoint-block-mods struct. Destruction assumes any owned buffer/id string were allocated by WT helpers compatible with null-session free.

State and persistence: owns only in-memory block modification metadata and associated buffer/string allocations. No filesystem persistence.

Dependencies/integration: used by tests needing an initialized `WT_CKPT_BLOCK_MODS` without manual cleanup. Risks include struct layout drift requiring updates to `init_block_mods`, and null-session free assumptions. Test signals are indirect: clients get a clean struct through `get_wt_block_mods`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/block_mods.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/block_mods.h -->
## sources/storage-engines/wiredtiger/test/catch2/wrappers/block_mods.h

Purpose: Header declaring the `block_mods` test wrapper for `WT_CKPT_BLOCK_MODS`.

Important API: class `block_mods` exposes constructor/destructor, `get_wt_block_mods`, private `init_block_mods`, and private `_block_mods` storage.

Control flow/state: no implementation flow in the header, but the contract is RAII ownership of the internal WT checkpoint block modifications structure. `get_wt_block_mods` returns a mutable pointer for test code.

Dependencies/integration: includes `wt_internal.h`, so consumers get full internal type definitions. Risks include exposing a mutable pointer that callers can populate inconsistently or with memory not compatible with the destructor. Test signals are indirect through tests using an initialized and automatically freed WT structure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/block_mods.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/config_parser.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/wrappers/config_parser.cpp

Purpose: Implementation of a test helper that converts a C++ map into a WiredTiger config array.

Important functions: constructor stores the map and initializes `_cfg` to nulls. `get_config_value` returns `_config_map.at(config)`. `insert_config` and `erase_config` mutate the map. `get_config_array` concatenates `key=value,` for every map entry, stores it in `_config_string`, sets `_cfg[0]` to `_config_string.data()`, and returns `_cfg`.

Control flow: map iteration gives sorted key order, so generated config strings are deterministic by key. The returned array is valid only while the parser object and `_config_string` remain unchanged.

State and persistence: in-memory map, generated string, and fixed three-slot C string array. No persistence.

Dependencies/integration: used by tests needing WiredTiger's `const char **` config input shape. Risks include trailing comma behavior, pointer invalidation after subsequent string/map changes, and `at` throwing on missing keys. Test signals are indirect through consumers that pass generated arrays to WT config APIs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/config_parser.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/config_parser.h -->
## sources/storage-engines/wiredtiger/test/catch2/wrappers/config_parser.h

Purpose: Header declaring `config_parser`, a map-backed builder for WiredTiger configuration arrays.

Important API: constructor from `std::map<std::string, std::string>`, `get_config_value`, `insert_config`, `erase_config`, and `get_config_array`.

Control flow/state: the header documents that WiredTiger expects comma-separated config strings and that this class controls construction from a map. It owns `_config_map`, `_config_string`, and `_cfg[3]`.

Dependencies/integration: includes `wt_internal.h` and standard map/string. Used where tests prefer structured mutation over hand-building config strings. Risks include exception behavior from missing map keys, lifetime of returned C pointers, and deterministic map ordering not matching insertion order. Test signals are indirect through successful config parsing in consumers.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/config_parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/connection_wrapper.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/wrappers/connection_wrapper.cpp

Purpose: RAII wrapper implementation for real WiredTiger connections used by Catch2 tests.

Important functions: constructor validates/creates the DB home directory, opens WiredTiger with `wiredtiger_open`, and stores both public and internal connection pointers. Destructor closes the connection and optionally calls `utils::wiredtiger_cleanup`. `create_session` opens a session and returns it as `WT_SESSION_IMPL *`. Accessors expose public/internal connection pointers.

Control flow: constructor checks `stat`, rejects an existing non-directory path, creates missing directory with `mkdir`, then opens with supplied config. Destructor throws through `throw_if_non_zero` if close fails. `create_session` does not check the return code explicitly.

State and persistence: owns a real database home and connection. It creates WiredTiger files and removes them unless `_do_cleanup` is cleared.

Dependencies/integration: central to tests that need real engine behavior. Risks include destructor throwing during stack unwinding, unchecked `open_session` return, and cleanup file-list incompleteness. Test signals are failures via thrown runtime errors or WT return assertions in callers.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/connection_wrapper.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/connection_wrapper.h -->
## sources/storage-engines/wiredtiger/test/catch2/wrappers/connection_wrapper.h

Purpose: Header for the real WiredTiger `connection_wrapper` test utility.

Important API: constructor takes DB home and optional config defaulting to `create`; destructor closes and cleans up; `create_session` returns a `WT_SESSION_IMPL *`; accessors return `WT_CONNECTION_IMPL *` and `WT_CONNECTION *`; `clear_do_cleanup` preserves the home directory.

Control flow/state: the class owns `_conn_impl`, `_conn`, `_db_home`, `_cfg_str`, and `_do_cleanup`. Header comments explain returned sessions are owned by the connection and need not be freed by callers.

Dependencies/integration: includes `wt_internal.h` and a Windows shim when needed. It is used by many tests requiring full WiredTiger, including sub-level error, reconciliation, and truncate integration tests. Risks include exposing internal pointers and tests relying on connection lifetime. Test signals are indirect through real connection/session operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/connection_wrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/item_wrapper.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/wrappers/item_wrapper.cpp

Purpose: Implementation of `item_wrapper`, a small RAII-style helper for read-only string-backed `WT_ITEM` values.

Important functions: constructor from `std::string` copies the string into `_string`, sets `_item.data` to `_string.c_str()`, size to `length + 1`, and clears allocation fields. Constructor from `const char *` delegates. Destructor nulls the item pointer and size.

Control flow: no dynamic allocation beyond `std::string`; WT item memory is not freed because it points into `_string`. Size includes the trailing null byte, which is useful for string values but can matter for byte-exact tests.

State and persistence: owns in-memory string storage and a `WT_ITEM` view into it. No persistence.

Dependencies/integration: simplifies tests that pass constant string items into WT internals. Risks include undefined behavior if consumers mutate `WT_ITEM.data`, lifetime ending when wrapper destructs, and size including null terminator. Test signals are indirect through consumers reading item data/size.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/item_wrapper.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/item_wrapper.h -->
## sources/storage-engines/wiredtiger/test/catch2/wrappers/item_wrapper.h

Purpose: Header declaring `item_wrapper`, a string-backed `WT_ITEM` helper for tests.

Important API: constructors from `std::string const &` and `const char *`, destructor, and `get_item` returning a mutable `WT_ITEM *`.

Control flow/state: the header documents that the wrapped `WT_ITEM` points at an internal `std::string` and is intended for constant read-only strings. Private state is `_item` and `_string`.

Dependencies/integration: includes public `wiredtiger.h` rather than full internals. Risks are caller mutation of read-only backing storage through the mutable pointer and use-after-destruction. Test signals are indirect through APIs receiving `WT_ITEM`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/item_wrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_connection.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_connection.cpp

Purpose: Implementation of a lightweight mock `WT_CONNECTION_IMPL` owner for tests that do not require a real WiredTiger home.

Important functions: `build_test_mock_connection` allocates zeroed `WT_CONNECTION_IMPL`, constructs `mock_connection`, and initializes stats. Destructor frees block/file hash arrays, destroys block lock if initialized, discards connection stats, and frees the connection. `setup_block_manager` initializes checksum, block/file hash tables and queues, spin locks, home path, and OS file-system layer. `setup_stats` initializes connection stats and flags and sets `default_session`.

State and persistence: in-memory connection internals only. Optional file-system layer can be initialized for block manager tests but does not open a real database.

Dependencies/integration: used by `mock_session` and tests needing internal connection fields. Depends on WT allocation, stat, spin, crc, and OS abstraction helpers. Risks include partial cleanup of initialized locks (`fh_lock` is initialized but destructor only checks `block_lock`), null-session allocation/free assumptions, and drift with `WT_CONNECTION_IMPL` layout. Test signals are indirect through mock-backed internal API calls.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_connection.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_connection.h -->
## sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_connection.h

Purpose: Header for `mock_connection`, an owned in-memory `WT_CONNECTION_IMPL`.

Important API: destructor, `get_wt_connection_impl`, `get_wt_connection`, static `build_test_mock_connection`, and `setup_block_manager`.

Control flow/state: class privately owns `_connection_impl` and exposes public/internal pointer views. Comments emphasize using mocks for speed when full connection behavior is unnecessary.

Dependencies/integration: includes `wt_internal.h` and is consumed by `mock_session`. Risks include exposing mutable internal connection state and consumers assuming more subsystems are initialized than the builder provides. Test signals are indirect through mock sessions and block-manager tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_connection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_session.cpp -->
## sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_session.cpp

Purpose: Implementation of a lightweight mock `WT_SESSION_IMPL` owner with event-handler capture.

Important functions: constructor installs `handle_wiredtiger_error`/`handle_wiredtiger_message` in an `event_handler_wrap`. Destructor cleans block manager session, terminates file system layer, frees dhandle/btree, error message, scratch buffers, and session. `build_test_mock_session` allocates session, builds mock connection, wires public connection pointer, and returns shared ownership. `setup_block_manager_session` initializes random state and block manager session. `setup_block_manager_file_operations` allocates dhandle/btree. Error/message handlers append callback messages to the mock.

State and persistence: owns in-memory session and shared mock connection. Captures messages in `_messages`; exposes `get_last_message`. No real DB home.

Dependencies/integration: underpins many internal unit tests. Risks include raw internal allocation/free, dhandle ownership assumptions, and `get_last_message` requiring at least one message. Test signals are internal API return codes and captured event messages.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_session.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_session.h -->
## sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_session.h

Purpose: Header for mock session support used across Catch2 internal tests.

Important declarations: free functions `handle_wiredtiger_error` and `handle_wiredtiger_message`, `event_handler_wrap`, and class `mock_session` with accessors for `WT_SESSION_IMPL` and `mock_connection`, callback message storage, static builder, block-manager setup helpers, and private owned pointers.

Control flow/state: the header defines the relationship between the WT event handler and the C++ mock through `event_handler_wrap::ms`. The class owns the session pointer and shared connection.

Dependencies/integration: includes `mock_connection.h` and `wt_internal.h`; used by semaphore, verify, truncate, and many misc tests. Risks are public exposure of mutable internals and message-list assumptions. Test signals are indirect through mock-backed internal functions and captured messages.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_session.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/checkpoint/CMakeLists.txt -->
## sources/storage-engines/wiredtiger/test/checkpoint/CMakeLists.txt

Purpose: Build and test-variant definition for the `test_checkpoint` executable.

Important declarations: `create_test_executable(test_checkpoint)` compiles `checkpointer.c`, `workers.c`, and `test_checkpoint.c`, and includes `recovery-test.sh` as an additional file. The target linker language is forced to CXX for sanitizer and extension runtime compatibility.

Control flow/integration: `define_test_variants` registers many named variants covering mixed tables, row store, variable-length column store, named checkpoints, prepare, timestamps, sweep stress, long-running SERVER-93028 cases, and disaggregated leader/PALite cases with precise checkpoint. Labels include `check`, `test_checkpoint`, `long_running`, and `check_disagg`.

State and persistence: build metadata only. Runtime persistence is controlled by the executable variants' flags.

Dependencies/integration: depends on WiredTiger test CMake helper macros and extension availability for disaggregated/PALite variants. Risks include variant flag drift from executable option parsing, long-running cache-size tuning, and forced C++ linkage assumptions. Test signals are CTest variant registrations and successful executable builds/runs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/checkpoint/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/checkpoint/checkpointer.c -->
## sources/storage-engines/wiredtiger/test/checkpoint/checkpointer.c

Purpose: Service-thread and verification logic for the checkpoint stress test.

Important functions/APIs: `start_threads`, `end_threads`, `clock_thread`, `checkpointer`, `real_checkpointer`, `set_flush_tier_delay`, `prepare_discover`, `verify_consistency`, `compare_cursors`, `diagnose_key_error`, `do_cursor_next`, and `do_cursor_prev`.

Control flow: `start_threads` sets initial stable timestamp, starts the checkpoint thread, and optionally starts a clock thread. The clock thread advances stable/oldest timestamps, with special predictable-replay handling. `real_checkpointer` waits for tables, opens a session, repeatedly verifies online data, chooses a verification timestamp, checkpoints or flushes tier, verifies checkpoint and timestamp views, advances oldest timestamp, and sleeps for tiered/sweep timing. `prepare_discover` claims pending prepared transactions after recovery for precise checkpoint. `verify_consistency` opens cursors over all tables, optionally at a checkpoint or read timestamp, and compares key/value streams.

State and persistence: mutates global `g` timestamps, running flag, service thread handles, tiered flush delay, and checkpoint files. It validates persistent checkpoint content across tables.

Dependencies/integration: relies on `GLOBAL g`, worker-created tables/data, WT timestamps, tiered utility APIs, checkpoint cursors, prepare discover cursors, and disagg limitations. Risks include concurrency races, timestamp boundary choices, checkpoint cursor unavailability in disagg, and diagnostic cursor side effects. Test signals are printed checkpoint/verification milestones and fatal `log_print_err` updates to `g.status`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/checkpoint/checkpointer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/checkpoint/recovery-test.sh -->
## sources/storage-engines/wiredtiger/test/checkpoint/recovery-test.sh

Purpose: Shell harness that repeatedly snapshots a running checkpoint test home and verifies copied homes recover cleanly.

Important flow: accepts config, home directory, and optional binary name (default `t`). It starts the binary with config and `-h home`, redirects output to `$home.out`, traps exit/signals to kill the child, waits until the output contains "Finished a checkpoint", then repeatedly `SIGSTOP`s the process, copies the home to backup, resumes the process, copies backup to recovery, and runs the binary in verify-only mode (`-t r -D -v -h recovery`). If the original config included `-e`, recovery also passes `-e -x`.

State and persistence: creates/removes `$home.backup`, `$home.recovery`, `$home.out`, and copies database files while the process is stopped. Final cleanup removes home and output.

Dependencies/integration: depends on POSIX signals, `grep`, `cp`, shell process control, and the checkpoint test's verify-only path. Risks include unsafe unquoted `$config`, copy races if STOP has not fully quiesced all threads, and platform limitations. Test signals are recovery binary exit status and loop completion when the child exits.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/checkpoint/recovery-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/checkpoint/test_checkpoint.c -->
## sources/storage-engines/wiredtiger/test/checkpoint/test_checkpoint.c

Purpose: Main driver for the checkpoint stress test executable.

Important functions/APIs: global `GLOBAL g`, `init_thread_data`, `main`, `wt_connect`, `wt_shutdown`, `cleanup`, event handlers, `log_print_err_worker`, `type_to_string`, and `usage`.

Control flow: `main` initializes defaults, parses options for table type/count, workers, operations, timestamps, precise checkpoint, prepare, replay, stress failpoints, cache config, verify-only, disagg, and home. It enforces option combinations, initializes random seeds and work directory, configures disagg requirements, then runs one or more iterations: cleanup, allocate cookies/table URIs, allocate thread data, connect, optionally verify-only with prepare discover, otherwise start service threads and workers, stop/join threads, free arrays, and close WT. Signal handling calls cleanup and exits.

State and persistence: owns global configuration, WT home, connection, table cookies, thread data, timestamps, prepared id, status, log file, and running flag. `wt_connect` builds the WT open config with logging, stats, cache/eviction settings, timing stress, sweep config, precise checkpoint/preserve prepared, tiered setup, and testutil open. `wt_shutdown` closes the connection and tiered hooks.

Dependencies/integration: integrates testutil option parsing, worker/checkpointer modules, WiredTiger public API, disagg/tiered utilities, and CMake variants. Risks include global mutable state, complex option interactions, fixed config buffer sizes, and cleanup after partial failures. Test signals are process exit status, stdout milestones, and logged errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/checkpoint/test_checkpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/checkpoint/test_checkpoint.h -->
## sources/storage-engines/wiredtiger/test/checkpoint/test_checkpoint.h

Purpose: Shared declarations, constants, and global state for the checkpoint stress test.

Important types/constants: `URI_BASE`, `ERR_KEY_MISMATCH`, `ERR_DATA_MISMATCH`, `table_type` enum (`MIX`, `ROW`, `COL`), `RESERVED_TIMESTAMPS_FOR_ITERATION`, `PRED_REPLAY_STABLE_PERIOD`, `COOKIE`, `THREAD_DATA`, and `GLOBAL`.

State model: `GLOBAL` contains shared `TEST_OPTS`, home, checkpoint name, connection, debug flag, key/op/table/worker counts, log/status, timing-stress booleans, timestamp state (`ts_oldest`, `ts_stable`, `stop_ts`), prepare/replay options, table cookies, thread data, clock lock, and service thread handles. `THREAD_DATA` stores per-thread id, key range, latest timestamp, and random states.

Dependencies/integration: includes `test_util.h` and declares functions implemented across `test_checkpoint.c`, `checkpointer.c`, and `workers.c`: thread lifecycle, logging, tiered delay, worker start, table type formatting, consistency verification, and prepare discovery.

Risks/test signals: this header centralizes global mutable state shared by many threads, so concurrency correctness depends on disciplined locking/atomic behavior in implementation files. It also fixes timestamp reservation formulas used by predictable replay. Signals are indirect through all checkpoint executable variants.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/checkpoint/test_checkpoint.h -->
