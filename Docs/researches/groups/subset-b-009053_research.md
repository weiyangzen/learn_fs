<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/testsuite.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/testsuite.py

Purpose: Provides vendored `testtools` suite helpers for walking, filtering, sorting, fixture-wrapping, and concurrently running `unittest`-style tests.

Important APIs/types/functions: `iterate_tests` recursively flattens suites. `ConcurrentTestSuite` runs suite partitions from `make_tests` on threads and serializes result forwarding through `ThreadsafeForwardingResult`. `ConcurrentStreamTestSuite` runs `(case, route_code)` workers and forwards `StreamResult` queue events. `FixtureSuite` wraps a suite with fixture setup/cleanup. `filter_by_ids` mutates or delegates filtering. `sorted_tests` detects duplicate case ids and returns a sorted `unittest.TestSuite`.

Control flow: Concurrent runners create one thread per generated sub-suite, push completion or stream events into a `Queue`, and stop child results if the controller raises. Runner exceptions are converted into `ErrorHolder` failures.

State and persistence behavior: State is in thread maps, queues, and suite `_tests`; there is no persistence.

Dependencies and integration points: Depends on `unittest`, `threading`, `queue`, and `testtools` result decorators. Used by vendored testtools users and WiredTiger Python tests that import the bundled library.

Risks and test signals: Filtering mutates private `_tests`; concurrent workers must honor `shouldStop`; duplicate ids intentionally raise. Exercise with duplicate-id suites, custom suite filtering, broken worker runs, and stream event ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/testsuite.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/__init__.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/__init__.py

Purpose: Public facade for vendored `testtools.twistedsupport`.

Important APIs/types/functions: Re-exports `succeeded`, `failed`, `has_no_result`, `AsynchronousDeferredRunTest`, `AsynchronousDeferredRunTestForBrokenTwisted`, `SynchronousDeferredRunTest`, `CaptureTwistedLogs`, `assert_fails_with`, and `flush_logged_errors`.

Control flow: Import-only module; consumers receive symbols from `_matchers` and `_runtest`.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Integrates Twisted `Deferred` assertions and test runners into the bundled testtools package. WiredTiger receives it as third-party test infrastructure rather than production code.

Risks and test signals: Public `__all__` controls compatibility. Missing or renamed imports break downstream tests at import time; import smoke tests with Twisted installed are the main signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_deferred.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_deferred.py

Purpose: Utility layer for inspecting already-fired Twisted `Deferred` objects in synchronous tests.

Important APIs/types/functions: `DeferredNotFired` reports an unfired deferred. `extract_result` converts a fired deferred into a return value or raised failure. `ImpossibleDeferredError` guards impossible success+failure observations. `on_deferred_result` preserves the deferred result while dispatching to success, failure, or no-result callbacks. `failure_content` converts a Twisted `Failure` to testtools `TracebackContent`.

Control flow: Functions attach callbacks/errbacks that record observed results, then inspect the recorded lists immediately.

State and persistence behavior: State is temporary callback-captured lists; deferred result propagation is preserved by returning captured values.

Dependencies and integration points: Uses Twisted `Failure`/`Deferred` concepts and `testtools.content.TracebackContent`; consumed by `_matchers` and `_runtest`.

Risks and test signals: Designed only for synchronous deferreds; using it with reactor-driven deferreds raises `DeferredNotFired`. Tests should cover success, failure, no-result, and failure traceback detail preservation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_deferred.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_deferreddebug.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_deferreddebug.py

Purpose: Fixture for toggling Twisted debugging in vendored testtools.

Important APIs/types/functions: `DebugTwisted` is a `fixtures.Fixture` that monkey-patches `twisted.internet.defer.Deferred.debug` and `twisted.internet.base.DelayedCall.debug`.

Control flow: `_setUp` installs two `MonkeyPatch` fixtures; fixture cleanup restores original values.

State and persistence behavior: Temporarily mutates Twisted class-level debug flags for the fixture lifetime only.

Dependencies and integration points: Used by `_spinner.Spinner` when async test runners request debug mode.

Risks and test signals: Global class mutation can leak if cleanup fails. Fixture lifecycle tests should verify flags are restored after success and failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_deferreddebug.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_matchers.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_matchers.py

Purpose: Matchers for asserting the immediate state and result of synchronous Twisted `Deferred`s.

Important APIs/types/functions: `has_no_result` returns singleton `_NoResult`; `succeeded(matcher)` wraps a matcher against a successful result; `failed(matcher)` wraps a matcher against a Twisted `Failure`. Internal mismatch messages include failure traceback content where useful.

Control flow: Each matcher delegates to `on_deferred_result`, selecting mismatch-producing handlers for unexpected success, failure, or no-result states.

State and persistence behavior: No persistent state; failure matchers add a no-op errback to suppress unhandled failure logging after the matcher has consumed it.

Dependencies and integration points: Builds on `_deferred` and `testtools.matchers.Mismatch`; exposed through `twistedsupport.__init__`.

Risks and test signals: These matchers assume synchronous deferreds. Important tests cover no-result, success mismatch, failure mismatch with traceback detail, and preservation/suppression behavior for Twisted failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_matchers.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_runtest.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_runtest.py

Purpose: Testtools `RunTest` implementations for test cases whose setup, test method, teardown, or cleanups return Twisted `Deferred`s.

Important APIs/types/functions: `SynchronousDeferredRunTest` runs already-fired deferreds without the reactor. `AsynchronousDeferredRunTest` spins a reactor through `Spinner`, captures Twisted logs, flushes logged errors, runs async cleanups, and reports success only after reactor cleanup. `AsynchronousDeferredRunTestForBrokenTwisted` adds obligatory reactor iterations. `CaptureTwistedLogs`, `flush_logged_errors`, `run_with_log_observers`, `assert_fails_with`, and `UncleanReactorError` support logging and assertion behavior.

Control flow: Async runs call setup, test, teardown, forced failure checks, and cleanups through deferred chains; `_blocking_run_deferred` translates spinner timeout/no-result into test failures; unhandled deferred errors and reactor junk become test errors.

State and persistence behavior: Temporarily sets `case.reactor`, mutates Twisted log observers, records details on the test case, and manages global `_log_observer`.

Dependencies and integration points: Depends on Twisted reactor/log/trial internals, fixtures, and testtools `RunTest`; exposed by `twistedsupport`.

Risks and test signals: Sensitive to Twisted private APIs, global log observers, timeouts, and reactor cleanup. Tests should cover timeout, logged errors, unhandled deferred failures, async cleanup failures, and stale reactor junk.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_runtest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_spinner.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_spinner.py

Purpose: Low-level reactor spinner used to run asynchronous Twisted tests inside synchronous testtools control flow.

Important APIs/types/functions: `not_reentrant`/`ReentryError` prevent recursive spinner entry. `trap_unhandled_errors` monkey-patches `defer.DebugInfo` to collect unhandled deferred failures. `Spinner.run` schedules the user function, spins the reactor until completion or timeout, restores signals and `reactor.stop`, and cleans delayed calls/selectables/threadpool. Exceptions include `TimeoutError`, `NoResultError`, and `StaleJunkError`.

Control flow: `run` saves signal handlers, schedules timeout and test function, substitutes `reactor.stop` with `crash`, starts the reactor, extracts success/failure, then cancels leftover reactor resources into `_junk`.

State and persistence behavior: Maintains `_success`, `_failure`, `_timeout_call`, `_saved_signals`, `_junk`, and `_spinning`; no persistence across process runs.

Dependencies and integration points: Uses Twisted reactor, `IReactorThreads`, `Failure`, and `DebugTwisted`; consumed by `_runtest`.

Risks and test signals: Global monkey-patching and reactor mutation are fragile. Tests need coverage for timeout, nested run rejection, signal restoration, stale junk detection, and threadpool cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_spinner.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/utils.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/utils.py

Purpose: Deprecated compatibility module for old `testtools.utils` imports.

Important APIs/types/functions: Emits a `DeprecationWarning` directing callers to import `iterate_tests` from `testtools.testsuite`.

Control flow: Warning is emitted at import time.

State and persistence behavior: No state.

Dependencies and integration points: Depends only on Python `warnings`; compatibility shim for older third-party code in the vendored package.

Risks and test signals: Does not re-export `iterate_tests`, so callers expecting the legacy symbol may fail. Import tests should verify warning behavior and compatibility expectations for this vendored release.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/utils.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/tox.ini -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/tox.ini

Purpose: Vendored `testtools` tox matrix for running its upstream test suite.

Important APIs/types/functions: Defines environments `py36` through `py312` plus `pypy3`; installs editable package with `sphinx`, `setuptools>=61`, `setuptools-scm`, and extras `test` and `twisted`; command is `python -W once -m testtools.run testtools.tests.test_suite`.

Control flow: Tox creates each interpreter environment and runs the single testtools suite command.

State and persistence behavior: Tox creates local virtualenv/build state outside source logic.

Dependencies and integration points: Relevant only when validating the vendored third-party package; not part of WiredTiger CMake tests.

Risks and test signals: Interpreter availability and old Python support are host-sensitive. The test signal is a full tox run or targeted current-interpreter run of `testtools.tests.test_suite`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/tox.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/CMakeLists.txt

Purpose: Top-level WiredTiger test directory CMake dispatcher.

Important APIs/types/functions: Adds common test subdirectories (`utility`, `checkpoint`, `cursor_order`, `fops`, `huge`, `manydbs`, `csuite`, `packing`), conditionally adds `catch2` under `HAVE_UNITTEST`, and POSIX-only suites under `WT_POSIX`. It also gates `cppsuite`, `model`, and LLVM fuzz tests.

Control flow: Configure-time platform and feature flags decide which test trees are compiled.

State and persistence behavior: No runtime state; creates build graph state in CMake.

Dependencies and integration points: Integrates WiredTiger test families with CMake feature variables such as `WT_WIN`, `WT_POSIX`, `ENABLE_CPPSUITE`, `ENABLE_MODEL`, and `ENABLE_LLVM`.

Risks and test signals: Platform gates can hide missing tests on Windows or non-POSIX builders. Configure checks should verify intended subdirectories are present for each build variant.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/catch2/CMakeLists.txt

Purpose: Builds the `catch2-unittests` executable and registers it as the `unittest` CTest target.

Important APIs/types/functions: Defines `unittests` differently for assertion-overriding builds versus normal builds; includes block, cross-checkpoint-cache, cursor, extension, sub-level-error, truncate, live-restore, wrapper, and utility sources. Uses `create_test_executable`, links `Catch2::Catch2`, conditionally defines `KEY_PROVIDER_EXTENSION`, and adds POSIX dependency `wiredtiger_dir_store`.

Control flow: CMake branches on `HAVE_UNITTEST_ASSERTS` and `WT_WIN`, then composes `unittest_sources`.

State and persistence behavior: Build-only state; generated executable runs tests under CTest label `check;unittest`.

Dependencies and integration points: Pulls in shared helpers like `block/util_block.cpp` and all files in this work item; integrated by parent `test/CMakeLists.txt`.

Risks and test signals: Source-list drift is easy when adding tests. The signal is successful configure/build plus `ctest -R unittest` or direct `catch2-unittests [tag]`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/api/test_block_api_misc.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/api/test_block_api_misc.cpp

Purpose: Catch2 tests for miscellaneous block manager API methods: address validation/stringification, header size, map status, size, and statistics.

Important APIs/types/functions: Helpers `check_bm_stats`, `test_addr_invalid`, and `test_addr_string` exercise `WT_BM::stat`, `addr_invalid`, and `addr_string`. Tests call `__wti_bm_method_set`, `setup_bm`, `__wt_block_addr_pack`, `bm.write`, `bm.size`, and `__wt_block_close`.

Control flow: Each section opens or initializes a `WT_BM`, packs synthetic address cookies, invokes the relevant block-manager API, checks derived values, and closes/drops the backing file where needed.

State and persistence behavior: Creates `test.wt` in the current working directory and updates live block statistics and extent-list state through actual block-manager setup.

Dependencies and integration points: Depends on block test helpers, mock sessions, WiredTiger block internals, filesystem paths, and extent utilities.

Risks and test signals: Tests know address cookie internals and include a disabled panic scenario. Important signals are stats consistency after writes, zero-size address handling, and filesystem cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/api/test_block_api_misc.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/api/test_block_api_write.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/api/test_block_api_write.cpp

Purpose: Validates block manager `write_size`, `write`, and `read` behavior with real file I/O.

Important APIs/types/functions: `addr_cookie` stores packed addresses. `validate_block_contents` compares raw `__wt_read` data and `bm->read` data. `validate_write_block` unpacks cookies, checks checksums, flags, offset alignment, and block headers. `test_validate_cookies` rereads earlier writes.

Control flow: Tests create a block manager file, exercise size rounding, write single and multiple strings of varying sizes, validate checksummed and non-checksummed writes, and test `os_cache_dirty_max` flush behavior.

State and persistence behavior: Creates and drops `test.wt`; mutates `bm.block->fh->written`, block size, and connection read statistics.

Dependencies and integration points: Uses `setup_bm`, `create_write_buffer`, mock sessions, item wrappers, and low-level WiredTiger block/file APIs.

Risks and test signals: File-system side effects and buffer/header assumptions are the main risks. Signals include address-cookie validity, read I/O stat increments, checksum/header correctness, and cleanup after writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/api/test_block_api_write.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_bitstring.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_bitstring.cpp

Purpose: Unit tests for WiredTiger bitstring macros and range-setting behavior.

Important APIs/types/functions: Exercises `__bit_byte`, `__bit_mask`, `__bitstr_size`, and `__bit_nset`.

Control flow: Macro tests check fixed input/output mappings. `__bit_nset` sections initialize an eight-byte vector and verify byte contents after aligned and non-aligned bit ranges are set.

State and persistence behavior: Only local vectors; no persistence.

Dependencies and integration points: Includes `wt_internal.h`; protects shared bit manipulation primitives used by block and other WiredTiger subsystems.

Risks and test signals: Off-by-one and byte-boundary errors are the key risks. Test signal is exact byte values for first/last/middle unaligned ranges.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_bitstring.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_addr.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_addr.cpp

Purpose: Unit tests for block address cookie packing and unpacking.

Important APIs/types/functions: Helpers call `__wt_block_addr_pack`, `__wt_block_addr_unpack`, and `__wt_vunpack_uint`, checking transformed offset/size/checksum values and selected hard-coded packed bytes.

Control flow: Test sections pack all-zero, zero-size, normal, manually verified, and negative-cast inputs against a `WT_BLOCK` with `allocsize=1`.

State and persistence behavior: Local `WT_BLOCK`, `WT_BM`, byte buffers, and vectors only.

Dependencies and integration points: Exercises WiredTiger variable-length integer packing and block address encoding used by block manager read/write paths.

Risks and test signals: Tests depend on internal cookie representation and tiered object id assumptions. Signals are round-trip correctness, zero-size normalization, and non-acceptance of expected bytes for negative casts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_addr.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_bitflip.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_bitflip.cpp

Purpose: Tests single-bit corruption diagnosis for block checksum mismatches.

Important APIs/types/functions: `checksum_fixture` initializes `__wt_process.checksum`; tests call `__wt_checksum` and `__ut_block_bitflip_detect` with `WT_BITFLIP_MAX_SIZE` limits.

Control flow: Sections compute a correct checksum, flip one or more bits, run detection, and validate found bit positions or false results for unsupported cases.

State and persistence behavior: Local byte vectors; process-level checksum function may be initialized once.

Dependencies and integration points: Covers block read checksum diagnostic helper used for detecting likely memory corruption.

Risks and test signals: CRC collisions mean multiple-bit case only asserts non-crash. Strong signals include first/middle/last byte positions, all bit positions, size limit behavior, and data restoration after probing.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_bitflip.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_ckpt.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_ckpt.cpp

Purpose: Tests block checkpoint helper rounding and block modification bitstring growth.

Important APIs/types/functions: Calls `__wt_rduppo2` and `__ut_ckpt_mod_blkmod_entry`; uses `block_mods` wrapper and mock sessions.

Control flow: Rounding tests verify power-of-two alignment and invalid non-power-of-two behavior. Block-mod tests initialize empty `WT_BLOCK_MODS`, record an offset/length, and check resulting `nbits` and `bitstring` allocation.

State and persistence behavior: Local wrapper-owned `WT_BLOCK_MODS` state; no persistent files.

Dependencies and integration points: Covers checkpoint block-mod tracking, especially the WT-6366 edge that requires extra bit allocation.

Risks and test signals: Boundary at bit 256 and invalid power-of-two arguments are key. Tests should run under normal Catch2 unit target.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_ckpt.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_file.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_file.cpp

Purpose: Tests block open/close behavior, configuration parsing, block hash reference management, file handle setup, and read-only/sync close paths.

Important APIs/types/functions: Validation helpers check `WT_BLOCK`, `WT_FH`, config-derived fields, connection block lock state, and hash removal. Tests call `__wt_block_manager_create`, `__wt_block_open`, `__wti_bm_close_block`, and `__wt_block_manager_drop`.

Control flow: Opens the same file twice to check reference counts, closes handles, tries allocation-size and block-allocation config variants, validates missing config failures, and tests read-only and sync-on-close paths.

State and persistence behavior: Creates `test.wt` and `test2.wt`, mutates connection block hash and block file references.

Dependencies and integration points: Uses `mock_session`, `config_parser`, filesystem current path, block manager internals, and connection block lock.

Risks and test signals: Disabled null-close segmentation test and FIXME around free pattern show known fragility. Signals include no leaked block hash entries, correct ref counts, and unlocked connection block lock after operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_file.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_other.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_other.cpp

Purpose: Tests miscellaneous block header byte-swap helpers and sweep eligibility.

Important APIs/types/functions: Calls `__wt_block_header_byteswap_copy`, in-place byte swap through same helper, and `__wt_block_eligible_for_sweep`.

Control flow: Sections set known header values, verify little-endian no-op or big-endian swapped constants, ensure source headers remain unchanged when copying, and check local/remote object id sweep rules.

State and persistence behavior: Local `WT_BLOCK_HEADER`, `WT_BLOCK`, and `WT_BM` only.

Dependencies and integration points: Protects on-disk block header portability and tiered/local block sweep behavior.

Risks and test signals: Endianness-specific expectations must compile on both byte orders. Sweep tests signal that remote blocks are never swept and local blocks require object id not above flushed id.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_other.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_session_bms.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_session_bms.cpp

Purpose: Tests block manager session allocation, preallocation, and cleanup across combined extent and size caches.

Important APIs/types/functions: Calls `__wti_block_ext_prealloc` and unit wrapper `__ut_block_manager_session_cleanup`; validates with `validate_ext_list` and `validate_size_list`.

Control flow: Tests allocate a block manager session when absent, grow existing caches, clean up null and non-null sessions, and inject fake cache counts to force `WT_ERROR`.

State and persistence behavior: Mutates `WT_SESSION_IMPL::block_manager`, `WT_BLOCK_MGR_SESSION::ext_cache_cnt`, and `sz_cache_cnt`.

Dependencies and integration points: Uses mock sessions and block helper validation. Exercises per-session block manager cache ownership.

Risks and test signals: Manual freeing and fake count injection can expose ownership bugs. Signals are correct nulling of `session_impl->block_manager` and error return on inconsistent cache counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_session_bms.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_session_ext.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_session_ext.cpp

Purpose: Tests extent-node allocation, preallocation, cache reuse, free, and discard behavior in block manager sessions.

Important APIs/types/functions: Exercises `__ut_block_ext_alloc`, `__ut_block_ext_prealloc`, `__wti_block_ext_alloc`, `__wti_block_ext_free`, and `__ut_block_ext_discard`.

Control flow: Sections allocate directly, preallocate different cache sizes, allocate from null manager sessions, pop cached extents, clear junk `next` pointers, push frees onto cache, and discard to a maximum count.

State and persistence behavior: Mutates `WT_BLOCK_MGR_SESSION::ext_cache`, `ext_cache_cnt`, and `WT_EXT::next` chains.

Dependencies and integration points: Uses `mock_session` and shared extent validators; covers block extent cache internals.

Risks and test signals: Cache count underflow, stale next pointers, and inconsistent counts are primary risks. Signals include expected cache list length and `WT_ERROR` on fake over-count discard.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_session_ext.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_session_size.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_session_size.cpp

Purpose: Tests size-node allocation, preallocation, cache reuse, free, and discard behavior for block manager sessions.

Important APIs/types/functions: Calls `__ut_block_size_alloc`, `__ut_block_size_prealloc`, `__wti_block_size_alloc`, `__wti_block_size_free`, and `__ut_block_size_discard`.

Control flow: Mirrors extent-cache tests for `WT_SIZE`: allocate empty nodes, grow cache to requested size, reuse cached nodes even with zero count or junk links, push freed nodes, and discard down to target maximums.

State and persistence behavior: Mutates `WT_BLOCK_MGR_SESSION::sz_cache`, `sz_cache_cnt`, and `WT_SIZE::next`.

Dependencies and integration points: Uses `wt_internal.h`, mock sessions, and shared size validators; protects block free-space size skiplist cache.

Risks and test signals: Incorrect cache counts or stale links can lead to leaks or corrupted freelists. Test signal is exact cache length and `WT_ERROR` for fake count mismatch.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_session_size.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list.cpp

Purpose: Tests extent and size skiplist search primitives used by block free-space management.

Important APIs/types/functions: Local wrappers allocate raw `WT_EXT`/`WT_SIZE` nodes. Tests call `__ut_block_off_srch_last`, `__ut_block_off_srch`, `__ut_block_first_srch`, and `__ut_block_size_srch`.

Control flow: Builds empty, single-entry, and three-entry skiplist layouts, invokes search helpers, and verifies returned stack pointers or first-fit status.

State and persistence behavior: Local heap-allocated wrappers only; no WiredTiger file state.

Dependencies and integration points: Uses `utils_extlist` validation and mock sessions for first-fit search. These helpers underpin extent insert/remove/merge behavior.

Risks and test signals: Pointer-to-pointer stack correctness is subtle, especially with alternate skip offsets. Signals include exact stack locations for empty, exact-match, after-maximum, and skip-offset searches.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list_insert_block.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list_insert_block.cpp

Purpose: Tests block-aware extent-list merge, remove, append, and file-size extension helpers.

Important APIs/types/functions: Calls `__ut_block_merge`, `__ut_block_off_remove`, `__ut_block_append`, and `__ut_block_extend`; uses `off_size_expected`, `off_expected`, and `block_append_test` fixtures.

Control flow: Sections insert/merge adjacent extents, remove by offset with optional returned node, append adjacent/non-adjacent extents, and extend block size including invalid/overflow cases.

State and persistence behavior: Mutates local `WT_EXTLIST` entries/bytes/last and local `WT_BLOCK::size`; no real file extension.

Dependencies and integration points: Uses mock sessions, `utils_extlist`, and block internals. Several sections start with `BREAK`, so harness macro behavior determines whether they run normally.

Risks and test signals: Adjacent coalescing and overflow are the main risks. `BREAK` markers are a test-execution risk; CI should confirm these sections are not unexpectedly trapping.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list_insert_block.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list_insert_wo_block.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list_insert_wo_block.cpp

Purpose: Tests extent insertion helpers that do not require a `WT_BLOCK`.

Important APIs/types/functions: Calls `__ut_block_ext_insert` with preallocated `WT_EXT` and `__ut_block_off_insert` with offset/size pairs.

Control flow: Inserts into empty lists and then inserts out-of-order extents, verifying sorted offset order after each insert.

State and persistence behavior: Mutates local `WT_EXTLIST` skiplist, bytes, and entries; frees through `extlist_free`.

Dependencies and integration points: Uses mock sessions, `alloc_new_ext`, and `verify_off_extent_list`; supports the lower layer used by merge/remove tests.

Risks and test signals: Ordering and skiplist pointer maintenance are key. Sections include `BREAK`, so automated test runs should verify macro configuration.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list_insert_wo_block.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list_search.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list_search.cpp

Purpose: Tests neighbor-pair and overlap search helpers for extent lists.

Important APIs/types/functions: Calls `__ut_block_off_srch_pair` and, under `HAVE_DIAGNOSTIC`, `__ut_block_off_match`.

Control flow: Builds empty and populated extent lists, searches offsets before, at, between, and after known extents, and verifies before/after nodes. Diagnostic tests check empty, adjacent, contained, boundary, and overlapping ranges.

State and persistence behavior: Local `WT_EXTLIST` mutation and cleanup only.

Dependencies and integration points: Uses mock sessions and `utils_extlist`; overlap detection is important for diagnostic validation of free-space list consistency.

Risks and test signals: Boundary-touching ranges must not be treated as overlap unless bytes intersect. `BREAK` markers and `HAVE_DIAGNOSTIC` gating affect coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list_search.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/util_block.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/util_block.cpp

Purpose: Shared Catch2 helper implementations for block manager tests.

Important APIs/types/functions: Validates and frees `WT_EXT`/`WT_SIZE` nodes and caches; `create_write_buffer` prepares aligned write buffers with block header space; `setup_bm` initializes mock block manager file operations, creates/opens a block file, installs block manager methods, parses config, and initializes checkpoint extent lists; `test_and_validate_write_size` checks allocation-size rounding.

Control flow: Helpers use `REQUIRE` assertions, allocate WiredTiger buffers, set up actual block files, and validate cache chains.

State and persistence behavior: Creates backing files via `__wt_block_manager_create`, opens `WT_BLOCK`, mutates `WT_BM`, `WT_BLOCK_MGR_SESSION`, and `WT_ITEM` buffers.

Dependencies and integration points: Used by block API/session tests; depends on `mock_session`, `config_parser`, and WiredTiger block internals.

Risks and test signals: Because helpers assert internally, failures point here even when caller logic is wrong. Buffer sizing assumes `write_size` always rounds up one allocation unit.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/util_block.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/util_block.h -->
# sources/storage-engines/wiredtiger/test/catch2/block/util_block.h

Purpose: Declarations for shared block manager Catch2 helpers.

Important APIs/types/functions: Declares extent/size validation/free helpers, `create_write_buffer`, `setup_bm`, and `test_and_validate_write_size`.

Control flow: Header-only declarations; implementation lives in `util_block.cpp`.

State and persistence behavior: No state directly, but APIs expose mutating helper contracts for `WT_BM`, `WT_ITEM`, session block-manager caches, and test files.

Dependencies and integration points: Included by block API and unit tests; includes `wt_internal.h` and `mock_session.h`.

Risks and test signals: Signature changes affect many block tests. Build failures in `catch2-unittests` are the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/util_block.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/utils_extlist.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/utils_extlist.cpp

Purpose: Debug, allocation, cleanup, and verification utilities for block extent-list tests.

Important APIs/types/functions: Implements `operator<` for `off_size`, printing helpers, `alloc_new_ext`, `get_off_n`, `ext_free_list`, `size_free_list`, `extlist_free`, `verify_empty_extent_list`, `verify_off_extent_list`, and stream operators for `off_size`, `WT_EXT`, and `WT_EXTLIST`.

Control flow: Allocation wraps `__wti_block_ext_alloc`; cleanup frees only top-level skiplist chains; verification iterates level 0 and compares offsets/sizes/bytes.

State and persistence behavior: Allocates and frees `WT_EXT`/`WT_SIZE` test nodes and mutates extlist heads during cleanup.

Dependencies and integration points: Used by all extent-list tests; depends on Catch2 `INFO`/`REQUIRE` and WiredTiger block allocation helpers.

Risks and test signals: Cleanup must avoid double-freeing nodes referenced by multiple skip levels. Diagnostic print helpers improve failure triage but can hide ownership mistakes if verification is incomplete.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/utils_extlist.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/utils_extlist.h -->
# sources/storage-engines/wiredtiger/test/catch2/block/utils_extlist.h

Purpose: Type and function declarations for extent-list test utilities.

Important APIs/types/functions: Defines `utils::off_size` with `end()`, `utils::off_size_expected`, declarations for print/allocation/search/free/verify helpers, `operator<`, and stream operators.

Control flow: Header contains lightweight constructors and declarations only.

State and persistence behavior: No direct state; declared helpers manage `WT_EXTLIST` and node lifetime in tests.

Dependencies and integration points: Included by block extent-list and block API tests; centralizes expected offset/size data structures.

Risks and test signals: `off_size::end()` assumes nonzero size. Type changes can ripple through many test vectors; compilation of block Catch2 tests is the key signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/utils_extlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/create_test.sh -->
# sources/storage-engines/wiredtiger/test/catch2/create_test.sh

Purpose: Developer script to create boilerplate Catch2 unit test files and insert them into `test/catch2/CMakeLists.txt`.

Important APIs/types/functions: Parses optional `-m module`, validates test name with `[a-z][_a-z0-9]+`, writes a C++ template including `wt_internal.h` and mock session helper, sorts existing test file entries, inserts a new CMake source line with `sed`, and runs `dist/s_all`.

Control flow: Fails on bad argument counts, invalid names, or existing files; otherwise creates the file under `tests` or `tests/<module>`, updates CMake, runs style/all-generation script, and prints manual next steps.

State and persistence behavior: Creates a `.cpp` test file and modifies `CMakeLists.txt`; runs repository maintenance script.

Dependencies and integration points: Depends on Bash, `sed`, `grep`, sorted shell arrays, and WiredTiger `dist/s_all`.

Risks and test signals: Uses `echo >` and `sed -i`, so failed insertion can partially modify files. Run from the expected directory and inspect CMake diff afterward.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/create_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/cross_checkpoint_caching_test_env.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/cross_checkpoint_caching_test_env.cpp

Purpose: Implements a real WiredTiger environment for cross-checkpoint shared disk cache tests.

Important APIs/types/functions: Constructor opens `DB_HOME`, creates a table, opens a cursor, borrows the cursor dhandle, installs a dummy disaggregated page-log handle, initializes shared disk cache, and marks it active. Destructor destroys cache, clears state, closes cursor, clears dhandle, and drops table. Methods expose `session`, `stats`, `btree_id`, `put`, and `bucket_size`.

Control flow: `put` allocates page-sized data, initializes `WT_PAGE_BLOCK_META`, calls `__wt_shared_dsk_cache_put`, frees duplicate data on collision, and returns the cache item.

State and persistence behavior: Creates/drops `table:cross_checkpoint_caching_test` in `DB_HOME`, mutates connection cache state and disaggregated-storage sentinel.

Dependencies and integration points: Used by get/put/release tests; depends on `connection_wrapper`, WiredTiger cache internals, and Catch2 assertions.

Risks and test signals: Borrowed dhandle and dummy disagg sentinel are delicate. Signals include destructor cleanup, no lingering table, correct active/off cache state, and bucket-count correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/cross_checkpoint_caching_test_env.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/cross_checkpoint_caching_test_env.h -->
# sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/cross_checkpoint_caching_test_env.h

Purpose: Declares the reusable cross-checkpoint cache test fixture.

Important APIs/types/functions: Constants `CROSS_CHECKPOINT_CACHING_TEST_HASH_SIZE` and `CROSS_CHECKPOINT_CACHING_TEST_DATA_SIZE`; class `cross_checkpoint_caching_test_env` with disabled copying, accessors, `put`, and `bucket_size`.

Control flow: Header declares fixture lifecycle managed by constructor/destructor in the `.cpp`.

State and persistence behavior: Holds `connection_wrapper`, `WT_SESSION_IMPL *`, `WT_CURSOR *`, and disaggregation sentinel.

Dependencies and integration points: Included by all cross-checkpoint cache unit tests; pulls in Catch2 and `connection_wrapper`.

Risks and test signals: Fixture owns real connection/cursor resources. Build and runtime cleanup tests are important to avoid DB_HOME contamination across Catch2 sections.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/cross_checkpoint_caching_test_env.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/unit/test_cross_checkpoint_caching_get.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/unit/test_cross_checkpoint_caching_get.cpp

Purpose: Tests shared disk cache lookup behavior across address, address-size, file-id, and hash-collision cases.

Important APIs/types/functions: Uses `cross_checkpoint_caching_test_env::put`, `bucket_size`, `stats`, `btree_id`, and direct `__wt_shared_dsk_cache_get`.

Control flow: Tests miss on empty cache, hit increments `ref_count`, different address/size/file id misses, repeated hits accumulate stats/refcounts, forced same-bucket collisions distinguish by address, and same address with different file ids resolves by current btree id.

State and persistence behavior: Mutates cache hash buckets, item `ref_count`, connection stats, and temporarily changes `S2BT(session)->id`.

Dependencies and integration points: Integrates with real WiredTiger connection fixture and shared disk cache internals.

Risks and test signals: Direct btree id mutation must be restored. Signals are hit/miss stat counters, nulling of miss output, and exact item identity under collisions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/unit/test_cross_checkpoint_caching_get.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/unit/test_cross_checkpoint_caching_put.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/unit/test_cross_checkpoint_caching_put.cpp

Purpose: Tests insertion and collision semantics for cross-checkpoint shared disk cache entries.

Important APIs/types/functions: Uses fixture `put`, `bucket_size`, `__wt_shared_dsk_cache_get`, and manual `S2BT(session)->id` changes.

Control flow: Inserts new items, verifies retrievability, repeats same address/file id to ensure existing item is returned with incremented `ref_count`, inserts different addresses in one bucket, and inserts same address under different file ids as distinct entries.

State and persistence behavior: Mutates shared disk cache buckets and item reference counts; changes btree id within tests.

Dependencies and integration points: Covers `__wt_shared_dsk_cache_put` behavior via fixture abstraction.

Risks and test signals: Hash-size `1` forces collisions and stresses equality checks. Signals are bucket sizes, inserted flag, item identity, fid, addr, and refcount values.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/unit/test_cross_checkpoint_caching_put.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/unit/test_cross_checkpoint_caching_release.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/unit/test_cross_checkpoint_caching_release.cpp

Purpose: Tests release and eviction semantics for shared disk cache items.

Important APIs/types/functions: Calls `__wt_shared_dsk_cache_release` and `__wt_shared_dsk_cache_get` through the cross-checkpoint fixture.

Control flow: Releases items with `ref_count > 1`, verifies zero refcount removes entries, ensures releasing one item in a collision bucket leaves others, balances repeated gets with releases, and tests same-address/different-file-id removal.

State and persistence behavior: Mutates item `ref_count`, bucket membership, hit/miss stats, and temporary btree ids.

Dependencies and integration points: Exercises shared disk cache lifecycle against real connection/cache state.

Risks and test signals: Use-after-free is avoided by inspecting buckets after final release rather than dereferencing freed item. Signals include bucket size, null miss output, surviving item identity, and refcount countdown.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/unit/test_cross_checkpoint_caching_release.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cursors/api/test_bulk_cursor.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/cursors/api/test_bulk_cursor.cpp

Purpose: Tests cursor, bulk cursor, checkpoint, drop, transaction, and cache-destroy interactions.

Important APIs/types/functions: Helpers insert raw key/value pairs, run checkpoint/drop in threads, print diagnostics, check transaction modifications, report cache status, and drive `cache_destroy_memory_check`, `cursor_test`, and `multiple_drop_test`.

Control flow: Opens connections and sessions, creates `table:cursor_test`, begins transactions, opens regular or bulk cursors, inserts sample values where allowed, attempts checkpoints/drops in same or second thread, and commits or rolls back with expected results.

State and persistence behavior: Creates/drops tables in `DB_HOME`, mutates transactions, dhandles, cache counters, and cursor lifecycle state.

Dependencies and integration points: Uses public WiredTiger API, internal cursor raw setters, wrappers, item wrappers, and `std::thread`.

Risks and test signals: Threading uses the same session pointer, which targets specific contention behavior. Several non-bulk variants are commented out. Signals are expected `EINVAL`, `EBUSY`, successful rollback/commit, and repeated force-drop stability.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cursors/api/test_bulk_cursor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cursors/unit/test_bounds_restore.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/cursors/unit/test_bounds_restore.cpp

Purpose: Tests cursor bounds flag save/restore logic.

Important APIs/types/functions: Calls `__wt_cursor_bounds_save` and `__wt_cursor_bounds_restore`; validates `WT_CURSOR::flags` against an original snapshot.

Control flow: Initializes a mock `WT_CURSOR` and `WT_CURSOR_BOUNDS_STATE`, sets upper/lower and inclusive bound flags in separate sections, saves state, restores state, and verifies flags.

State and persistence behavior: Uses scratch buffers on a real session from `connection_wrapper`; frees lower/upper bound scratch in one section.

Dependencies and integration points: Covers cursor bound state helper used by search/positioning paths.

Risks and test signals: Memory cleanup for saved bounds is important. Signals are exact preservation of inclusive and non-inclusive flag bits.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cursors/unit/test_bounds_restore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cursors/unit/test_cursor_get_raw_key_value.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/cursors/unit/test_cursor_get_raw_key_value.cpp

Purpose: Tests `WT_CURSOR::get_raw_key_value` against normal cursor key/value retrieval and unsupported cursor types.

Important APIs/types/functions: Helpers initialize `WT_ITEM`, insert raw key/value pairs with `__wt_cursor_set_raw_key/value`, validate `get_key`/`get_value`, and validate `get_raw_key_value` with optional null key/value output pointers.

Control flow: Creates `table:cursor_test`, inserts five records, iterates with standard getters, iterates with raw getter including key-only/value-only calls, and opens a dump-version cursor on the underlying file to expect `ENOTSUP`.

State and persistence behavior: Creates table/file in `DB_HOME`, opens/closes cursors and session.

Dependencies and integration points: Uses WiredTiger public API plus internal raw cursor helpers and wrappers.

Risks and test signals: Raw `WT_ITEM` data is compared as C strings, so formats must remain string-compatible. Signals include ordered iteration, `WT_NOTFOUND` at end, null pointer handling, and unsupported version cursor error.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cursors/unit/test_cursor_get_raw_key_value.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/ext/test_checkpoint_meta_version.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/ext/test_checkpoint_meta_version.cpp

Purpose: Tests disaggregated checkpoint metadata version parsing and compatibility validation.

Important APIs/types/functions: Fixture builds a mock session; tests call `__ut_disagg_validate_checkpoint_meta_version` and compare `version`/`compatible_version` with `WT_DISAGG_CHECKPOINT_META_VERSION_DEFAULT`.

Control flow: Sections parse explicit version pairs, missing fields, only one field, forward-incompatible versions, illegal compatible-version newer than version, and multiple incompatible configs.

State and persistence behavior: Local mock session and output integers only; no persistent metadata write.

Dependencies and integration points: Covers extension/disaggregated metadata compatibility logic used when reading checkpoint metadata strings.

Risks and test signals: Forward compatibility checks must distinguish `ENOTSUP` from invalid config `EINVAL`. Signals are defaulting behavior for old metadata and rejection of too-new reader requirements.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/ext/test_checkpoint_meta_version.cpp -->
