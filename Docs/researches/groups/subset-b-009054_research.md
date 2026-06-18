# subset-b-009054 Research

Grouped research for the WiredTiger Catch2 sources in subset B. Each source file is documented in its own marker-delimited section so the reconciliation step can split this report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/ext/test_key_provider.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/ext/test_key_provider.cpp

## Purpose
Exercises the test key-provider extension and WiredTiger disaggregated-storage key-provider integration. The file covers extension initialization/configuration, pull-mode key rotation, push-mode `WT_KEY_PROVIDER::set_key`, pending crypt-key queue ordering, checkpoint key selection/pruning, and full pending-key cleanup.

## Important APIs, Types, And Functions
`kp_fixture` owns a `connection_wrapper`, `WT_SESSION`, extension init pointer, and raw `KEY_PROVIDER`. `kp_init` calls `wiredtiger_extension_init` or the built-in extension initializer, then reads `WT_CONNECTION_IMPL::key_provider`. `kp_reset` terminates the provider and clears the connection field. `kp_load_key`, `kp_get_key`, and `push_key` wrap `load_key`, two-phase `get_key`, `on_key_update`, and push-mode `set_key`. `validate_chosen_key` and `validate_pending_queue` inspect `WT_DISAGG_PENDING_CRYPT_KEY` entries. The tests call `WT_CONNECTION::set_key_provider`, `WT_CONNECTION::set_timestamp`, `__ut_disagg_select_pending_crypt_key`, `__ut_disagg_prune_pending_crypt_keys`, and `__wti_disagg_pending_crypt_key_clear`.

## Control Flow
The fixture opens an in-memory WiredTiger database and session, initializes the extension on demand, and tears it down in RAII style. Early sections validate null, empty, custom, and invalid config. Pull-mode sections force expiration by moving `key_time`, then verify `get_key` transitions `CURRENT -> PENDING -> READ` and `on_key_update` either commits the new LSN/state or leaves a failed read pending. Push-mode sections configure `version=1`, push key bytes with timestamps, assert monotonic and stable-timestamp constraints, then exercise checkpoint selection and pruning over the pending queue.

## State And Persistence Behavior
The tests directly inspect volatile connection state: provider fields, `WT_CONN_KEY_PROVIDER_PUSH`, `KEY_STATE_*`, current key bytes, LSN, key age, and the disaggregated pending crypt-key tail queue. They simulate persistence boundaries by invoking checkpoint selection/prune helpers, but do not write real disaggregated checkpoint metadata. Queue cleanup is explicit to avoid fixture destruction seeing stale entries.

## Dependencies And Integration Points
Depends on Catch2, `ext/test/key_provider/key_provider.h`, `connection_wrapper`, `utils::shared_library`, `wiredtiger.h`, and `wt_internal.h`. It integrates extension ABI behavior with core connection configuration, disaggregated-storage timestamp checks, and checkpoint crypt-key selection helpers.

## Risks And Edge Cases
Risks are stale raw provider pointers, manual clearing of `conn_impl->key_provider`, memory returned by `get_key` that must be freed, and direct mutation of internals that can hide lifecycle errors if cleanup is missed. The test intentionally covers invalid config strings, one-shot expiration semantics, queueing failures, non-monotonic timestamps, stable-timestamp rejection, empty push input, selection before the first key, and pruning an empty or fully covered queue.

## Test Signals
Catch2 assertions validate every state transition and queue shape. Failure signals include `EINVAL` for bad config or invalid push timestamps, unchanged LSN on queueing failure, exact queue order after pushes/prunes, and selected key timestamp/bytes for checkpoint timestamps.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/ext/test_key_provider.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/ext/test_key_provider_header.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/ext/test_key_provider_header.cpp

## Purpose
Tests the on-page crypt header format used by the key-provider/disaggregated encryption path. It verifies header layout, packing, checksum generation, validation failures, and backward/forward compatibility for v1, current, and future-sized headers.

## Important APIs, Types, And Functions
`build_crypt_page` hand-builds a `WT_CRYPT_HEADER`, byte-swaps it, copies the requested header size into a `WT_ITEM`, and writes a checksum. `kp_header_fixture` allocates a key buffer with header headroom using `__wt_buf_initsize`, exposes `kp_crypt_key_buffer`, and normalizes a copied header with `kp_copy_crypt_key_buffer`. Tests call `__ut_disagg_set_crypt_header`, `__ut_disagg_validate_crypt`, `__wt_crypt_header_byteswap`, `__wt_checksum`, and `wiredtiger_crc32c_func`.

## Control Flow
The fixture initializes a mock session and crypt key buffer. Layout tests assert structure size and offsets. Packing tests place a header before the payload and validate signature, version, compatible version, header size, crypt payload size, timestamp, total item size, and checksum. Validation tests mutate the header or item size to cover good unpack, future writer version, incompatible compatible-version, too-small item, too-small header, header bigger than buffer, and bad checksum. Compatibility tests build a 16-byte v1 header, a future version with current-compatible requirements, a longer future header, and a boundary compatible-version equal to the reader version.

## State And Persistence Behavior
State is in `WT_CRYPT_KEYS::keys` and heap-allocated unpacked headers returned by validation. The file models persisted page bytes by writing binary headers into `WT_ITEM`; no disk I/O is performed. Timestamp defaults to zero for old v1 headers that lack the appended field.

## Dependencies And Integration Points
Depends on `wt_internal.h`, Catch2, and `mock_session`. It integrates with crypt header constants such as `WT_CRYPT_HEADER_SIGNATURE`, `WT_CRYPT_HEADER_VERSION`, `WT_CRYPT_HEADER_COMPATIBLE_VERSION`, and `WT_CRYPT_HEADER_MIN_SIZE`.

## Risks And Edge Cases
The main risk is compatibility drift in the serialized header. Tests catch offset/size changes, checksum mismatches, accepting future writer versions only when compatible, rejecting pages requiring a newer reader, and preserving older v1 pages.

## Test Signals
Positive signals are zero returns from `__ut_disagg_validate_crypt` and exact unpacked field matches. Negative signals are `ENOTSUP` for incompatible reader requirements and `EIO` for malformed size/checksum cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/ext/test_key_provider_header.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fh_lock_close_sync.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fh_lock_close_sync.cpp

## Purpose
Smoke-tests live-restore file-handle `fh_lock`, `fh_sync`, write+sync, and close behavior. The file deliberately avoids re-testing lower-level POSIX semantics and focuses on API forwarding through the live-restore handle wrapper.

## Important APIs, Types, And Functions
Uses `live_restore_test_env`, `create_file`, `WTI_LIVE_RESTORE_FS::iface.fs_open_file`, and `WT_FILE_HANDLE` methods `fh_lock`, `fh_sync`, `fh_write`, and `close`. It downcasts to `WTI_LIVE_RESTORE_FILE_HANDLE` to set `allocsize` before writing.

## Control Flow
The test creates matching source and destination files, opens a destination data file through the live-restore file system, locks and unlocks it, verifies re-entrant locking succeeds, syncs with no writes, writes a 4096-byte buffer, syncs again, and closes the handle.

## State And Persistence Behavior
The only persistent effect is a write to the destination backing file. Source is present to allow live-restore open behavior, but this test does not inspect migration bitmap state.

## Dependencies And Integration Points
Depends on `utils_live_restore.h` and the mock session wrapper transitively. It integrates with the live-restore file system implementation and underlying file handle operations.

## Risks And Edge Cases
The test covers re-entrant locks and sync-after-write. It does not test double-close because the implementation aborts, and it does not verify lock exclusion across threads.

## Test Signals
All file handle calls must return zero. A failure indicates live-restore wrapper forwarding, write setup, or handle lifecycle regression.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fh_lock_close_sync.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fh_read_write.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fh_read_write.cpp

## Purpose
Tests live-restore `fh_read` and `fh_write` selection between source and destination backing files, including partially migrated pages and writes beyond the tracked bitmap range.

## Important APIs, Types, And Functions
`init_file_handle` opens a live-restore data file, configures `allocsize`, `nbits`, and allocates `bitmap` with `__bit_alloc`. The test uses `WTI_LIVE_RESTORE_FILE_HANDLE::iface.fh_read/fh_write`, direct `destination->fh_read`, direct `source->fh_read`, and helper file creation/removal.

## Control Flow
With a source file present, the test first verifies reads come from source before migration. It simulates background migration by writing source bytes to destination for a non-page-aligned length, then checks full migrated pages, one partial page, user writes that override destination without modifying source, and writes partially or completely beyond the bitmap. A second section removes the source, confirms writes/readbacks operate only on destination, and verifies `source == nullptr`.

## State And Persistence Behavior
The bitmap records which allocation slots have been written/migrated. Destination contents change for simulated migration and user writes; source contents remain unchanged in the source-present section. Writes past the original bitmap extend destination-visible data without source involvement.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, `live_restore_test_env`, WiredTiger bit operations, and the live-restore file-handle implementation. It interacts with source/destination handles beneath the wrapper to verify physical backing contents.

## Risks And Edge Cases
Important edge cases are page-size larger than allocsize, file size not divisible by page size, partial migration inside a page, missing source, writes crossing bitmap end, and writes wholly beyond bitmap end. The test assumes manual bitmap sizing matches `file_size / allocsize`.

## Test Signals
Expected vectors of source, dummy, and written characters must match both wrapper reads and underlying destination/source reads. Source mutation, wrong fallback source/destination selection, or mishandled out-of-bitmap writes fail the test.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fh_read_write.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fh_size.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fh_size.cpp

## Purpose
Verifies that a live-restore file handle's `fh_size` always reports the destination file size once the file has been opened, regardless of source presence, migration state, or tombstone file presence.

## Important APIs, Types, And Functions
`fh_size_wrapper` opens a data file through `WTI_LIVE_RESTORE_FS::iface.fs_open_file`, calls `WTI_LIVE_RESTORE_FILE_HANDLE::iface.fh_size`, and closes it. `test_fh_size` prepares `DEST/SOURCE`, `MIGRATING/NOT_MIGRATING`, and `STOP/NO_STOP` cases using `WTI_LIVE_RESTORE_STATE_*` and `WTI_LIVE_RESTORE_STOP_FILE_SUFFIX`.

## Control Flow
For each permutation, the helper removes old test files, creates a destination file of size 10, optionally creates a source file of size 100, sets migration state, optionally creates a stop file, opens the handle, reads size, and asserts it is the destination size.

## State And Persistence Behavior
The destination file is the authoritative size once opened. Source and tombstone files only affect open/existence decisions elsewhere, not this handle-level size path.

## Dependencies And Integration Points
Depends on `utils_live_restore.h` and the shared live-restore environment. It integrates with file-handle open and size methods.

## Risks And Edge Cases
Covers all boolean combinations of source, migration, and stop file while destination exists. It intentionally does not test absent destination because open either creates it or fails before handle-level `fh_size`.

## Test Signals
Every permutation must return `DEST_FILE_SIZE`. Any source-size or tombstone-driven result indicates a regression in handle-level size semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fh_size.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fh_truncate.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fh_truncate.cpp

## Purpose
Tests live-restore `fh_truncate`, especially how truncation updates destination file size and marks bitmap bits for truncated ranges.

## Important APIs, Types, And Functions
`init_file_handle` opens a live-restore file and initializes `allocsize`, `nbits`, and `bitmap`. `validate_bitmap` uses `__bit_ffs` and `__bit_test` to assert that bits from the first truncated allocation slot onward are set. The test calls `fh_size`, `fh_truncate`, and `close`.

## Control Flow
The test creates a source file, opens the destination handle, confirms initial size, truncates to the same length, shrinks by two allocation slots, extends within the original length, extends beyond original length, clears the bitmap to simulate no migration, extends beyond bitmap with no bit changes, then shrinks partially within bitmap and validates marked bits.

## State And Persistence Behavior
Destination file length changes on each truncate. The live-restore bitmap marks truncated portions as filled so later reads do not fetch stale source bytes for deleted ranges. Extending beyond bitmap range does not mark unavailable bitmap bits.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, WiredTiger bit-string helpers, and the live-restore file-handle implementation.

## Risks And Edge Cases
Key edges are no-op truncate, shrink, growth after shrink, growth beyond original source-backed bitmap, a fully clear bitmap, and truncation partly inside tracked bitmap. The test assumes at least one set bit for `validate_bitmap`.

## Test Signals
Sizes must match requested truncation lengths, and bitmap validation must show expected first-set bit and all following bits set for shrunk ranges.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fh_truncate.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fs_directory_list.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fs_directory_list.cpp

## Purpose
Tests live-restore directory listing as a unified view over destination and source directories. It verifies deduplication, tombstone hiding, subdirectory handling, prefix filtering, and temporary-file filtering.

## Important APIs, Types, And Functions
`directory_list` wraps `WTI_LIVE_RESTORE_FS::iface.fs_directory_list` and `fs_directory_list_free`, returning a `std::set<std::string>`. `file_list_equals` removes standard WiredTiger metadata files before comparison. `directory_list_subfolder` and `directory_list_prefix` specialize the wrapper.

## Control Flow
Each Catch2 section creates a fresh `live_restore_test_env`, mutates files in source and/or destination, calls directory listing, and compares normalized sets. Scenarios cover destination-only files, source-only files, files in both, mixed backing locations, tombstones hiding source files, subfolder names, missing and existing subfolders, nested subdirectories, listing within a subdirectory, prefix filtering, and ignoring `.lr_tmp` temporary files.

## State And Persistence Behavior
The unified directory view is derived from physical files in `WT_LR_DEST` and `WT_LR_SOURCE`. Tombstones are stop files in the destination and suppress source entries without removing source data. Temporary live-restore files are filtered from results.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, `<set>`, and WiredTiger file-name constants such as `WT_METAFILE`, `WT_METADATA_TURTLE`, and `WT_HS_FILE`. It integrates with both live-restore directory-list and free APIs.

## Risks And Edge Cases
Important risks include duplicate names when a file exists in both directories, stale source entries after destination tombstones, returning children instead of subdirectory names, incorrect ENOENT behavior for subfolders, and leaking `dirlist` allocations. Prefix tests include empty prefix, exact prefix, suffix-only mismatch, long prefix, and temporary-file names.

## Test Signals
Expected sets must match after metadata-file removal, and missing subfolder listing must return `ENOENT`. Any leaked temporary file, duplicate behavior issue, or tombstone visibility bug changes the result set.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fs_directory_list.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fs_exist.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fs_exist.cpp

## Purpose
Tests `fs_exist` in live restore across every combination of destination presence, source presence, migration state, and destination tombstone presence.

## Important APIs, Types, And Functions
`file_exists` calls `WTI_LIVE_RESTORE_FS::iface.fs_exist` on the destination-path form visible to WiredTiger. `test_file_exists` prepares combinations using `HasDest`, `HasSource`, `IsMigrating`, and `HasStop`.

## Control Flow
For each permutation, existing artifacts are removed, destination/source/stop files are created as requested, the live-restore state is set to background migration or complete, and `fs_exist` is called. The test then asserts the expected boolean result.

## State And Persistence Behavior
Destination files always make the logical file exist. Source-only files exist only while background migration is active and no tombstone exists. Once migration is complete, source-only files are invisible because they should have been copied already.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, live-restore state constants, and stop-file suffix behavior.

## Risks And Edge Cases
The complete 16-permutation matrix guards against regressions where tombstones are ignored, completed migration still exposes source-only files, or destination files are hidden by tombstones.

## Test Signals
The expected booleans are the signal: all no-file cases false, source-only migrating without stop true, source-only with stop false, and all destination-present cases true.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fs_exist.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fs_open_file.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fs_open_file.cpp

## Purpose
Tests live-restore `fs_open_file` for regular files and directories. It verifies creation, source-to-destination materialization, nested source paths, tombstone rejection, and directory-only destination semantics.

## Important APIs, Types, And Functions
`open_file` wraps `WTI_LIVE_RESTORE_FS::iface.fs_open_file` and checks the expected return. `validate_lr_fh` checks destination handle presence, optional source/bitmap absence for directories, destination name, and `back_pointer`.

## Control Flow
The regular-file section checks ENOENT for missing files, destination creation with `WT_FS_OPEN_CREATE`, opening destination-only files, source-only files that create a destination copy, nested source files with automatic destination subdirectory creation, files in both locations, and tombstoned source files returning ENOENT. The directory section checks missing directories and source-only directories return ENOENT, while destination-present directories open successfully with no source handle or bitmap.

## State And Persistence Behavior
Opening a source-only regular file creates a destination-side file and any needed destination subdirectories. Directory opens do not create destination directories because WiredTiger expects directories to be created outside this path. Tombstones in destination suppress source files.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, `WT_FS_OPEN_FILE_TYPE_REGULAR`, `WT_FS_OPEN_FILE_TYPE_DIRECTORY`, and live-restore handle internals.

## Risks And Edge Cases
Risks include creating directories in cases where WiredTiger should not, failing to create nested destination paths for source files, ignoring tombstones, and leaving invalid source or bitmap state for directory handles.

## Test Signals
Expected return codes (`0` or `ENOENT`), destination existence checks, handle fields, and source/bitmap nullness for directories provide coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fs_open_file.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fs_remove_rename.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fs_remove_rename.cpp

## Purpose
Tests live-restore `fs_remove` and `fs_rename`, especially tombstone creation while background migration is active and no-tombstone behavior after live restore completes.

## Important APIs, Types, And Functions
`stop_file_exists` checks for `WTI_LIVE_RESTORE_STOP_FILE_SUFFIX`. Tests use `WT_FILE_SYSTEM::fs_remove`, `fs_rename`, the underlying `os_file_system` for comparison, and `WTI_LIVE_RESTORE_STATE_*`.

## Control Flow
Remove tests cover destination-only removal creating a stop file, removing missing files, source-only with existing stop failing, source-only without destination succeeding by tombstoning destination path, recreating and removing a same-name destination file, completed-state removal without tombstone, completed-state source-only failure, and source+destination removal preserving source. Rename tests cover destination-only rename creating old and new stop files, missing source failing, source-only rename rejected as `EINVAL`, rename over an existing destination, and completed-state rename without tombstones.

## State And Persistence Behavior
During background migration, stop files persist logical deletion/rename intent in the destination so source files do not reappear. Source files are not removed. After live restore is complete, remove/rename operate like normal file-system calls without generating tombstones.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, stop-file suffix constants, live-restore file-system methods, and underlying OS file-system methods.

## Risks And Edge Cases
Risks include exposing deleted source files, removing source data by mistake, failing to tombstone rename destinations, and producing tombstones after completion. Rename source-only returns `EINVAL`, which distinguishes live-restore logical constraints from OS ENOENT behavior.

## Test Signals
Return codes, physical existence checks, tombstone existence checks, and source preservation checks verify expected behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fs_remove_rename.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fs_size.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fs_size.cpp

## Purpose
Tests live-restore file-system-level `fs_size` over all combinations of destination file, source file, migration state, and tombstone file.

## Important APIs, Types, And Functions
`file_size` calls `WTI_LIVE_RESTORE_FS::iface.fs_size` on a destination-path file name. `test_file_size` prepares the four-factor state matrix with `DEST_FILE_SIZE`, `SOURCE_FILE_SIZE`, and live-restore state constants.

## Control Flow
The test removes stale files, conditionally creates destination/source/stop files, sets migration state, calls `fs_size`, and verifies return code and size. It enumerates all relevant permutations.

## State And Persistence Behavior
Destination is authoritative when present. Source-only files are visible and sized from source only during background migration and only if no stop file exists. Completed migration hides source-only files. Tombstones make source-only files look absent.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, live-restore file-system API, and stop-file naming.

## Risks And Edge Cases
The matrix catches divergence between `fs_exist` and `fs_size` semantics, including source visibility after completion, stop-file suppression, and destination precedence over source.

## Test Signals
Expected `ENOENT` or `0` return plus exact size (`SOURCE_FILE_SIZE` or `DEST_FILE_SIZE`) is asserted for each case.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fs_size.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/live_restore_test_env.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/live_restore/live_restore_test_env.cpp

## Purpose
Implements the shared live-restore Catch2 test environment. It creates a valid WiredTiger backup-like source directory, reopens the destination with live restore enabled, and exposes path helpers for destination, source, and tombstone files.

## Important APIs, Types, And Functions
`live_restore_test_env::live_restore_test_env` removes old `WT_LR_DEST` and `WT_LR_SOURCE`, creates a non-live-restore database, opens a `backup:` cursor, copies listed files into source, removes destination, then opens a live-restore connection with `live_restore=(enabled=true,path=WT_LR_SOURCE,threads_max=0),statistics=(fast)`. `dest_file_path`, `source_file_path`, and `tombstone_file_path` build backing paths.

## Control Flow
Construction has two phases: create and copy a baseline backup, then reopen using live restore. The backup cursor yields URIs that are copied from destination to source. After the live-restore connection opens, the environment stores `session` and casts the connection file system to `WTI_LIVE_RESTORE_FS`.

## State And Persistence Behavior
The fixture creates and deletes real directories under the test working directory. Source persists as the backup input; destination is recreated as the live database home. Migration threads are disabled, giving tests direct control over migration effects.

## Dependencies And Integration Points
Depends on `live_restore_test_env.h`, `connection_wrapper`, `testutil_remove`, `testutil_mkdir`, `testutil_copy`, backup cursors, and live-restore configuration.

## Risks And Edge Cases
The fixture assumes backup cursor entries can be copied directly and that test names do not collide outside the fixed `WT_LR_*` directories. Manual file manipulation in tests relies on `threads_max=0` to prevent background interference.

## Test Signals
The constructor uses `REQUIRE` on session, cursor, key retrieval, and copy steps. Any environment setup regression fails before individual live-restore tests run.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/live_restore_test_env.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/live_restore_test_env.h -->
# sources/storage-engines/wiredtiger/test/catch2/live_restore/live_restore_test_env.h

## Purpose
Declares the reusable live-restore test environment class and includes the C/C++ dependencies needed by live-restore Catch2 tests.

## Important APIs, Types, And Functions
`utils::live_restore_test_env` exposes constants `DB_DEST` and `DB_SOURCE`, members `WTI_LIVE_RESTORE_FS *lr_fs`, `std::unique_ptr<connection_wrapper> conn`, and `WT_SESSION_IMPL *session`, plus constructor and path helper methods.

## Control Flow
The header has no runtime control flow beyond class declaration. Test files include it directly or through `utils_live_restore.h` and construct the environment at section or test scope.

## State And Persistence Behavior
The declared class owns a WiredTiger connection wrapper and session pointer and references the live-restore file system for the connection. Path helpers model persistent backing files in destination/source directories.

## Dependencies And Integration Points
Includes Catch2, shared test utilities, `wt_internal.h`, `test_util.h`, `live_restore_private.h`, and `connection_wrapper`. It bridges C live-restore internals into C++ Catch2 tests.

## Risks And Edge Cases
The header exposes raw internal pointers for tests to mutate, which is intentional but can bypass production invariants. Include order matters because it pulls internal C headers inside `extern "C"`.

## Test Signals
No direct tests exist for the header alone; all live-restore tests validate it by constructing `live_restore_test_env` and using its members.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/live_restore_test_env.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/unit/test_live_restore_bitmap_encode_decode.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/live_restore/unit/test_live_restore_bitmap_encode_decode.cpp

## Purpose
Tests live-restore bitmap hex encoding and decoding for several bitmap lengths, byte patterns, and an empty bitmap case.

## Important APIs, Types, And Functions
`test_data` stores expected hex string, bit count, and bitmap bytes. The test calls `__ut_live_restore_encode_bitmap`, `__ut_live_restore_decode_bitmap`, `__wt_readlock`, `__wt_readunlock`, `__wt_buf_free`, and live-restore `fs_open_file`.

## Control Flow
For each test bitmap, the test creates a source file large enough to produce the desired bitmap size, opens a live-restore file handle, manually assigns `bitmap` and `nbits`, encodes under the handle read lock, compares encoded hex for nonzero bitmaps, decodes back into the handle, compares bytes, closes the handle, removes files, deletes the test bitmap, and clears the buffer.

## State And Persistence Behavior
The bitmap is transient memory attached to the live-restore file handle. Encoding stores a hex string in a `WT_ITEM`; decoding replaces/initializes bitmap state based on encoded metadata. Files exist only to satisfy live-restore open semantics.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, `mock_session`, `item_wrapper`, and live-restore bitmap helper functions exposed through unit-test wrappers.

## Risks And Edge Cases
Edge cases include zero bits, bit counts not divisible by eight, high/low nibble ordering, and ensuring encode is only decoded when `nbits != 0`, matching production behavior.

## Test Signals
The encoded string must match expected hex and decoded bytes must match the original bitmap for nonempty cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/unit/test_live_restore_bitmap_encode_decode.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/unit/test_live_restore_bitmap_filling_bit_range.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/live_restore/unit/test_live_restore_bitmap_filling_bit_range.cpp

## Purpose
Tests `__ut_live_restore_fh_fill_bit_range`, which marks live-restore bitmap bits corresponding to byte ranges that have been filled in destination.

## Important APIs, Types, And Functions
`filling_data` stores `allocsize`, `nbits`, backing bitmap vector, and offset/length ranges. `is_bit_in_range` maps byte ranges to bit offsets, and `is_valid_bitmap` compares every bit against expected range membership. The test calls `__ut_live_restore_fh_fill_bit_range` under a write lock.

## Control Flow
The test creates a dummy `WTI_LIVE_RESTORE_FILE_HANDLE` with non-null source, initializes an rwlock, iterates through range scenarios, assigns bitmap state, fills each range, checks the bitmap, unlocks, and finally destroys the lock.

## State And Persistence Behavior
Only in-memory bitmap bits are modified. No real files are opened. The non-null source pointer ensures encoding/filling logic follows the live-restore source-backed path.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, `mock_session`, WiredTiger bit-string sizing, and live-restore private helpers.

## Risks And Edge Cases
Covers single-slot ranges, multi-slot ranges, last-slot plus beyond-end ranges, fully out-of-range fills, entire bitmap fills, overlapping ranges, and varied allocsizes. It guards against off-by-one errors in `(offset + length - 1) / allocsize`.

## Test Signals
Every bit in the bitmap must equal expected range membership after filling. Any incorrect bit set/clear fails `is_valid_bitmap`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/unit/test_live_restore_bitmap_filling_bit_range.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/unit/test_live_restore_compute_read_end_bit.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/live_restore/unit/test_live_restore_compute_read_end_bit.cpp

## Purpose
Tests `__ut_live_restore_compute_read_end_bit`, which determines the last contiguous clear bitmap bit that can be read from source in one migration/read operation.

## Important APIs, Types, And Functions
`compute_read_end_bit_test` builds a bitmap with a clear run and stores allocsize, nbits, buffer size, file size, and first clear bit. `is_valid_end_bit` independently computes the expected end bit using `WTI_BITMAP_END`, `WTI_BIT_TO_OFFSET`, `WTI_OFFSET_TO_BIT`, and `__bit_test`.

## Control Flow
For each scenario, the test creates a destination file of the scenario size, opens a live-restore file handle, attaches the bitmap and geometry, calls `__ut_live_restore_compute_read_end_bit`, validates the result with the independent implementation, closes the handle, and removes the file.

## State And Persistence Behavior
The bitmap is allocated in each scenario and attached to the handle. File size is real and constrains the maximum readable bit, modeling truncation and extension relative to bitmap length.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, live-restore private macros/helpers, and file-handle open behavior.

## Risks And Edge Cases
Covers single clear bit, clear runs capped by buffer size, clear runs to bitmap end, read size smaller than allocsize, file larger than bitmap, and file smaller than bitmap. It targets boundary mistakes in byte/bit conversions.

## Test Signals
`__ut_live_restore_compute_read_end_bit` must return zero and its end bit must match the independent scan bounded by bitmap end, read window, and file size.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/unit/test_live_restore_compute_read_end_bit.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/unit/test_live_restore_fill_hole.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/live_restore/unit/test_live_restore_fill_hole.cpp

## Purpose
Tests `__ut_live_restore_fill_hole`, the live-restore background migration primitive that copies source bytes into destination for clear bitmap regions and marks them filled.

## Important APIs, Types, And Functions
`fill_hole_test` builds bitmap scenarios. `is_valid_fill` verifies destination bytes and bitmap bits for a single fill. `generate_bitmap` creates arbitrary bitmap states from integers, and `verify_fill_complete` validates complete migration. Tests call `__ut_live_restore_fill_hole`, `fh_read`, file-handle open/close, and WiredTiger bit helpers.

## Control Flow
The single-call section sets up source/destination files, attaches scenario bitmaps, locks the handle, calls fill-hole once, checks `finished`, `read_offset`, and filled data, then cleans up. The multiple-call section iterates many bitmap values, repeatedly calls fill-hole under a write lock until `finished`, then verifies all originally clear bits were copied from source and originally set bits stayed as destination dummy bytes.

## State And Persistence Behavior
The function mutates destination file contents and live-restore bitmap state. Source remains the authoritative data source for holes. `read_offset` tracks where a migration read occurred, and `finished` reports no clear bits remain.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, live-restore file handles, bit allocation/free, locking, and source/destination backing file operations.

## Risks And Edge Cases
Tests cover clear runs of length one, buffer-capped runs, clear runs to bitmap end, buffer smaller than allocsize, already-complete bitmaps, empty initial bitmaps, all-set bitmaps, and many pseudo-random bitmap shapes. It is sensitive to bit/byte offset conversion and preserving user-written destination regions.

## Test Signals
Expected filled length, `finished` state, `read_offset`, bitmap bits, and destination bytes must match. The complete pass requires no clear bits left and correct source/destination character provenance.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/unit/test_live_restore_fill_hole.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/utils_live_restore.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/live_restore/utils_live_restore.cpp

## Purpose
Implements small live-restore test utilities for opening live-restore file handles and creating test files with controlled contents.

## Important APIs, Types, And Functions
`open_lr_fh` verifies the supplied destination path starts with `env.DB_DEST`, then calls `WTI_LIVE_RESTORE_FS::iface.fs_open_file` with data-file type and optional flags. `create_file` asserts the path does not already exist, writes `len` copies of `fill_char` using `std::ofstream`, and closes the stream.

## Control Flow
Both helpers are straight-line wrappers. `open_lr_fh` derives file-system/session pointers from `live_restore_test_env`; `create_file` builds a string and writes it.

## State And Persistence Behavior
`open_lr_fh` returns a live-restore handle without closing it. `create_file` writes real files in source or destination directories for tests.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, `live_restore_test_env`, `testutil_exists`, and live-restore file-system open behavior.

## Risks And Edge Cases
`open_lr_fh` guards against accidentally opening a source path through the live destination API. `create_file` refuses overwriting existing files, so tests must remove stale artifacts explicitly.

## Test Signals
Failures are expressed through Catch2 `REQUIRE` in helper assertions or returned file-open status checked by callers.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/utils_live_restore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/utils_live_restore.h -->
# sources/storage-engines/wiredtiger/test/catch2/live_restore/utils_live_restore.h

## Purpose
Declares live-restore test enums and helper functions shared by API and unit tests.

## Important APIs, Types, And Functions
Defines `HasDest`, `HasSource`, `IsMigrating`, and `HasStop` enums for permutation tests. Declares `create_file` and `open_lr_fh`.

## Control Flow
The header contains declarations only. Test files include it to share consistent setup vocabulary and helper APIs.

## State And Persistence Behavior
The enums model persistent file-system state combinations; helper declarations operate on real source/destination files through the implementation file.

## Dependencies And Integration Points
Includes `<string>` and `live_restore_test_env.h`, so it also exposes live-restore internals to tests.

## Risks And Edge Cases
Because helpers use fixed enum names like `DEST`, `SOURCE`, and `STOP`, the header is convenient but broad in namespace scope within `utils`. Future tests should avoid ambiguous imports.

## Test Signals
No direct tests; correctness is indirect through all live-restore API/unit tests that compile and use these declarations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/live_restore/utils_live_restore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/main.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/main.cpp

## Purpose
Provides the Catch2 test runner entry point for the WiredTiger Catch2 suite and cleans the default test home before running tests.

## Important APIs, Types, And Functions
Defines `CATCH_CONFIG_RUNNER`, includes Catch2, includes `utils.h`, and implements `main` by calling `utils::wiredtiger_cleanup(DB_HOME)` before `Catch::Session().run(argc, argv)`.

## Control Flow
Startup removes leftovers from previous crashed or failed runs, then delegates argument parsing and test execution to Catch2.

## State And Persistence Behavior
The only persistent side effect is cleanup of `DB_HOME`. It does not create connections itself.

## Dependencies And Integration Points
Integrates Catch2's custom runner mode with WiredTiger test utility cleanup.

## Risks And Edge Cases
Shared `DB_HOME` cleanup is useful but can remove state a developer expected to inspect after a failed test if rerun immediately.

## Test Signals
The process exit code is Catch2's run result after cleanup succeeds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/main.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_acquire_release_macros.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_acquire_release_macros.cpp

## Purpose
Compile- and runtime-tests WiredTiger acquire/release atomic macros across integer widths, including barrier macro variants and type-size constraints.

## Important APIs, Types, And Functions
`TEST_ACQUIRE_TYPE` checks `__wt_atomic_load_<type>_acquire` and `WT_ACQUIRE_READ_WITH_BARRIER`. `TEST_RELEASE_TYPE` checks `__wt_atomic_store_<type>_release` and `WT_RELEASE_WRITE_WITH_BARRIER`. Typedefs map macro suffixes to C++ types.

## Control Flow
Macro-generated Catch2 tests initialize values, load/store through atomic macros, and compare results. A final test demonstrates casting a hash-defined value to satisfy release macro type-size checks.

## State And Persistence Behavior
Only stack variables are mutated; no persistence or shared threads are involved.

## Dependencies And Integration Points
Depends on Catch2 and `wt_internal.h`. It integrates with architecture/compiler-specific atomic macro expansions.

## Risks And Edge Cases
The main signal is compilation: previous issues involved clang failures for non-`uint64_t` sizes. Runtime checks guard truncation and barrier variants.

## Test Signals
Values loaded/stored must equal originals for `uintmax`, 64-, 32-, 16-, and 8-bit types. The cast workaround must compile and preserve the `int8_t` value.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_acquire_release_macros.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_assertions.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_assertions.cpp

## Purpose
Tests optional diagnostic assertion configuration and reconfiguration in non-diagnostic WiredTiger builds. It verifies which assertion macros fire, return, or panic depending on `extra_diagnostics` categories.

## Important APIs, Types, And Functions
Defines assertion-result sentinel values and `DIAGNOSTIC_FLAGS`. Wrapper functions call `WT_RET_ASSERT`, `WT_ERR_ASSERT`, `WT_RET_PANIC_ASSERT`, and `WT_ASSERT_OPTIONAL`, then inspect `WT_SESSION_IMPL::unittest_assert_hit/msg`. Helpers `all_diag_asserts_off/on`, `configured_asserts_abort`, and `configured_asserts_off` validate category state. Tests use `connection_wrapper`, `WT_CONNECTION::reconfigure`, `EXTRA_DIAGNOSTICS_ENABLED`, `WT_ASSERT`, and `WT_ASSERT_ALWAYS`.

## Control Flow
Tests first fail fast if compiled with `HAVE_DIAGNOSTIC`, because this suite requires diagnostics off. Connection-config sections open with diagnostics off/on/all/specific categories and assert macro outcomes. Reconfigure sections test empty, missing, invalid, valid, and transition configurations.

## State And Persistence Behavior
State lives in connection diagnostic bitmasks and the unit-test assertion fields in the session. Reconfigure mutates live connection settings. There is no durable persistence.

## Dependencies And Integration Points
Depends on Catch2, WiredTiger public/internal headers, `utils.h`, and `connection_wrapper`. It tests config parsing and assertion macro integration.

## Risks And Edge Cases
Risks include false positives under diagnostic builds, assertion flags not being cleared between calls, invalid reconfigure partially mutating state, and category transitions failing to clear old bits.

## Test Signals
Expected outcomes are exact sentinel values, diagnostic category booleans, and assertion messages. Invalid reconfigure must fail and leave diagnostics off.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_assertions.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_cell_fast_truncate_unpack.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_cell_fast_truncate_unpack.cpp

## Purpose
Tests packing and unpacking of fast-truncate page-deletion information from address-delete cells, including committed and prepared deletion metadata.

## Important APIs, Types, And Functions
`build_ft_addr_del_cell` manually creates a `WT_CELL_ADDR_DEL` with optional `WT_CELL_PREPARE`, transaction ID, timestamps/prepared ID, and zero-length address cookie. `build_prepared_addr_cell` creates a regular prepared addr cell. `setup_mock_session` initializes mock block-manager operations and base write generation. Tests call `__wt_cell_unpack_addr` and `__wt_cell_pack_addr`.

## Control Flow
Tests unpack hand-built committed and prepared fast-truncate cells, then pack committed and prepared `WT_PAGE_DELETED` structures and unpack them again. A final test verifies a prepare flag on a non-fast-truncate addr cell marks the page-level time aggregate as prepared instead of populating page deletion info.

## State And Persistence Behavior
All cell bytes are in local `WT_CELL` buffers, modeling on-disk address cells. Prepared fast-truncate pack requires connection/table flags `WT_CONN_PRESERVE_PREPARED` and `WT_BTREE_DISAGGREGATED`.

## Dependencies And Integration Points
Depends on `mock_session`, `wt_internal.h`, variable-length integer packing, `WT_PAGE_DELETED`, `WT_TIME_AGGREGATE`, and page header flags like `WT_PAGE_FT_UPDATE`.

## Risks And Edge Cases
Guards against mixing prepared timestamp/prepared ID with commit timestamps, incorrectly marking page aggregate prepare for fast-truncate deletion, and losing `selected_for_write` or committed state on round trip.

## Test Signals
`CHECK` assertions verify transaction IDs, timestamps, prepared IDs, prepare state, committed flag, selected-for-write, and `unpack.ta.prepare`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_cell_fast_truncate_unpack.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_cell_prepared_time_window.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_cell_prepared_time_window.cpp

## Purpose
Tests cell validity-window packing/unpacking for prepared time-window metadata, including start-prepared, stop-prepared, both-prepared, regular, and empty windows.

## Important APIs, Types, And Functions
`create_test_time_window` builds `WT_TIME_WINDOW` values with commit/durable timestamps and optional prepared fields. `pack_time_window` calls `__cell_pack_value_validity`. `unpack_time_window` wraps the packed validity bytes inside a mock `WT_CELL_VALUE` and calls `__wt_cell_unpack_kv`. `compare_time_windows` compares all relevant fields.

## Control Flow
Each test creates a mock session, enables `WT_CONN_PRESERVE_PREPARED`, sets up block-manager operations and `base_write_gen`, builds a time window, packs it, unpacks it, and compares. The empty test checks compact packed size.

## State And Persistence Behavior
The file models on-disk cell bytes in memory. It does not write to disk but depends on page header write generation to avoid obsolete cleanup paths during unpack.

## Dependencies And Integration Points
Depends on Catch2, `mock_session`, `wt_internal.h`, `WT_TIME_WINDOW`, cell packing/unpacking internals, and preserve-prepared connection behavior.

## Risks And Edge Cases
Risks include losing prepared IDs/timestamps during packing, mishandling same-transaction start/stop prepared windows, and breaking regular non-prepared time windows while adding prepared metadata.

## Test Signals
Packed empty window size must be one byte; all nonempty scenarios must unpack to field-equivalent `WT_TIME_WINDOW` structures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_cell_prepared_time_window.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_checkpoint_skip.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_checkpoint_skip.cpp

## Purpose
Tests `__ut_checkpoint_skip_ckptlist`, which decides whether checkpoint work can be skipped based on the checkpoint list shape, names, and deletion flags.

## Important APIs, Types, And Functions
`make_ckpt` initializes `WT_CKPT` entries and sentinel entries. Tests call `__ut_checkpoint_skip_ckptlist` with arrays terminated by a null name.

## Control Flow
Each test builds a small checkpoint list and checks the skip decision for empty lists, single entries, matching/different last names, internal `WT_CHECKPOINT.N` prefixes, multiple deletions, and one deletion with matching last-two names.

## State And Persistence Behavior
Only in-memory checkpoint arrays are used. The behavior models metadata checkpoint list interpretation and potential space-reclamation decisions.

## Dependencies And Integration Points
Depends on Catch2 and `wt_internal.h`. It integrates with checkpoint metadata naming and `WT_CKPT_DELETE`.

## Risks And Edge Cases
Risks include skipping when deletions should reclaim space, comparing generated internal checkpoint names too literally, or requiring two entries when a list has fewer.

## Test Signals
Boolean return values must match each named scenario: skip only when the last relevant checkpoints are equivalent and deletion constraints allow it.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_checkpoint_skip.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_config.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_config.cpp

## Purpose
Tests decimal integer parsing for WiredTiger config values, including boundaries, overflow/underflow, length-limited input, whitespace, signs, and stopping at non-digits.

## Important APIs, Types, And Functions
The test directly calls `__wti_config_parse_dec(const char *, size_t, char **)` and checks parsed `int64_t`, `errno`, and `endptr`.

## Control Flow
Sections cover no conversion, exact `INT64_MAX/MIN`, one-less-than-boundaries, out-of-range positive/negative/long values, limited length, non-digit stops, leading blanks, explicit positive/negative signs, and signed zero.

## State And Persistence Behavior
No persistent state. `errno` is explicitly reset for range tests and expected to report `ERANGE`.

## Dependencies And Integration Points
Depends on `wiredtiger.h`, `wt_internal.h`, and C string/errno behavior. It validates parser semantics used by broader config handling.

## Risks And Edge Cases
The key risks are overflow clamping, underflow clamping, `endptr` placement under bounded length, and treating whitespace/signs consistently.

## Test Signals
Expected parsed value, `errno`, and `endptr` position are asserted in each section.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_config.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_crc32.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_crc32.cpp

## Purpose
Tests WiredTiger CRC32C function pointers for empty input, seeded empty input, known vectors, long data, and incremental seeded computation.

## Important APIs, Types, And Functions
Uses `wiredtiger_crc32c_func()` and `wiredtiger_crc32c_with_seed_func()` to obtain function pointers. Builds vectors and strings for known checksums.

## Control Flow
The test asserts empty buffers produce zero or preserve the seed, checks known byte patterns, constructs a repeated long string, verifies its checksum, then recomputes the same checksum incrementally by feeding chunks with the previous CRC as seed.

## State And Persistence Behavior
No persistence. Random seed is used only for checking seeded zero-length input returns the seed.

## Dependencies And Integration Points
Depends on Catch2, `<ctime>`, `<cmath>`, vectors/strings, and `wt_internal.h`. It validates the selected platform CRC implementation through the public function pointer accessor.

## Risks And Edge Cases
Covers null pointers with zero length, seed preservation, all-zero/all-one bit patterns, and chunked computation equivalence.

## Test Signals
Exact checksum constants must match, including final incremental checksum `0x47a00ee5`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_crc32.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_disagg_block_header_version.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_disagg_block_header_version.cpp

## Purpose
Tests disaggregated block-header compatible-version checks to ensure readers compare a page's required compatible version against the current reader version, not the reader's oldest compatible version.

## Important APIs, Types, And Functions
Calls `__ut_block_disagg_header_version_compatible` with constants `WT_BLOCK_DISAGG_COMPATIBLE_VERSION` and `WT_BLOCK_DISAGG_VERSION`.

## Control Flow
The test asserts compatibility for version `1`, the build's compatible version, and the build's current version, then asserts rejection for one greater than current version.

## State And Persistence Behavior
No state. The test models persisted block header compatible-version values.

## Dependencies And Integration Points
Depends on Catch2 and `wt_internal.h`. It guards disaggregated block read compatibility logic.

## Risks And Edge Cases
The bug targeted here only appears when `WT_BLOCK_DISAGG_VERSION` advances beyond `WT_BLOCK_DISAGG_COMPATIBLE_VERSION`; the test is future-proofed for that macro divergence.

## Test Signals
Boolean compatibility results must match current-reader capability boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_disagg_block_header_version.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_disagg_meta_config.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_disagg_meta_config.cpp

## Purpose
Tests parsing of disaggregated storage checkpoint metadata, crypt key metadata, legacy metadata format, and metadata version/compatible-version handling.

## Important APIs, Types, And Functions
`disagg_fixture` holds sample `checkpoint`, `timestamp`, and `key_provider` config fragments and a mock session. Tests call `__wt_disagg_parse_meta`, `__wti_disagg_parse_crypt_meta`, and `__ut_disagg_parse_version_and_check`.

## Control Flow
Metadata parsing sections cover all fields, missing optional key provider, missing required fields, null/empty metadata, truncated length, unknown keys under future version, and unknown keys under matching version. Crypt metadata sections cover well-formed page ID/LSN extraction and malformed values/missing fields/unsupported version. Legacy sections parse newline-separated checkpoint+timestamp metadata and invalid timestamp cases. Version sections check valid, incompatible, missing version, missing compatible version, and default version when omitted.

## State And Persistence Behavior
All parsed fields in `WT_DISAGG_METADATA` are views into the input buffer with lengths, not durable copies. Timestamp strings are parsed from hex. No disk state is written.

## Dependencies And Integration Points
Depends on `wt_internal.h`, `mock_session`, `utils.h`, string streams/views, and disaggregated checkpoint turtle constants.

## Risks And Edge Cases
Risks include accepting malformed crypt metadata, reading past provided buffer length, mishandling unknown keys for future metadata, rejecting legacy metadata, and accepting incompatible versions.

## Test Signals
Return codes (`0`, `EINVAL`, `ENOTSUP`), exact string views, parsed timestamps, page IDs, LSNs, and default version fields are asserted.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_disagg_meta_config.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_error.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_error.cpp

## Purpose
Tests error-preservation and error-priority behavior for `WT_TRET` and `WT_TRET_ERROR_OK`.

## Important APIs, Types, And Functions
Uses `WT_DECL_RET`, `WT_TRET`, and `WT_TRET_ERROR_OK` with WiredTiger error codes including `WT_PANIC`, `WT_RUN_RECOVERY`, `WT_ERROR`, `WT_DUPLICATE_KEY`, `WT_NOTFOUND`, `WT_RESTART`, and `WT_CACHE_FULL`.

## Control Flow
Sections initialize `ret` to different values, invoke the macro with a new status, and assert the resulting priority. `WT_TRET_ERROR_OK` additionally treats a configured acceptable error as success.

## State And Persistence Behavior
Only a local `ret` variable is mutated. No persistence or connection state is involved.

## Dependencies And Integration Points
Depends on Catch2, `wiredtiger.h`, and `wt_internal.h`. It validates common cleanup/error-chaining macros used throughout WiredTiger.

## Risks And Edge Cases
Risks include panic/recovery priority being overwritten incorrectly, benign errors not being suppressed by `WT_TRET_ERROR_OK`, or special statuses behaving like generic errors.

## Test Signals
The final `ret` value in each section must match the macro's intended priority rules.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_error.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_futex.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_futex.cpp

## Purpose
Tests WiredTiger futex wait/wake wrappers for single wake, timeout, waking one of multiple waiters, wake-all, and multiple separate wakes.

## Important APIs, Types, And Functions
`waiter` wraps `__wt_futex_wait`, records return, errno, and wake value, and classifies errors/timeouts/awakened/spurious wakeups. `wake_signal`, `wake_one`, and `wake_all` describe `__wt_futex_wake` calls. `futex_tester` manages futex word state, threads, waiter creation, delayed wake, joining, and result inspection.

## Control Flow
Each test creates a tester, starts waiter threads on an expected futex value with timeout, optionally delays and sends wake signals, joins threads, and checks outcomes. Inspection allows spurious wakeups but requires no lost signals or unexpected timeout counts.

## State And Persistence Behavior
State is an in-memory futex word and thread-local waiter results. No persistence. Atomic store uses Windows `InterlockedExchange` or GCC `__atomic_store_n`.

## Dependencies And Integration Points
Depends on threading, chrono, algorithms, Catch2, and `wt_internal.h`. It exercises platform futex abstraction behavior.

## Risks And Edge Cases
Concurrency tests are timing-sensitive and account for spurious wakeups. They guard against lost signals, incorrect wake values, wake-all not reaching all waiters, and timeouts that should have been wakes.

## Test Signals
`inspect_waiters` must return `AsExpected`. Non-timeout errors, unexpected timeout counts, or unmatched wake values fail the test.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_futex.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_intpack.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_intpack.cpp

## Purpose
Tests integer packing macros and variable-length integer pack/unpack functions from WiredTiger's intpack implementation.

## Important APIs, Types, And Functions
Wrapper functions isolate return-from-macro behavior for `WT_SIZE_CHECK_PACK` and `WT_SIZE_CHECK_UNPACK`. `wt_leading_zeros_wrapper` wraps `WT_LEADING_ZEROS`. Helpers call `__wt_vpack_posint`, `__wt_vunpack_posint`, `__wt_vpack_negint`, `__wt_vunpack_negint`, `__wt_vpack_int`, and `__wt_vunpack_int`.

## Control Flow
Tests check macro constants across integer widths, bit extraction and size checks, leading-zero behavior, positive integer encodings, negative integer encodings, signed integer compact encodings for one- and two-byte ranges, and larger values including ENOMEM for insufficient buffers.

## State And Persistence Behavior
All data is in local vectors and pointers. The packed byte arrays model persisted cell/config integer encodings but are not written to disk.

## Dependencies And Integration Points
Depends on Catch2 and `wt_internal.h`. It validates low-level binary format helpers used across storage metadata and page cells.

## Risks And Edge Cases
Risks include signed/unsigned macro type surprises, buffer-size enforcement returning wrong codes, leading-zero behavior for zero and small types, and byte-order/marker regressions in variable-length encodings.

## Test Signals
Exact byte arrays, unpacked values, and error codes (`ENOMEM`, `EINVAL`) are asserted.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_intpack.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_layered_incomplete_table.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_layered_incomplete_table.cpp

## Purpose
Tests recovery/open behavior for incomplete layered-table metadata in disaggregated storage, covering leader/follower roles and missing ingest/stable file metadata entries.

## Important APIs, Types, And Functions
`build_cfg` builds wiredtiger_open config with palite page-log extension and disaggregated role. `prepare_db` creates a complete layered table, then optionally removes `file:<table>.wt_ingest` and/or `file:<table>.wt_stable` metadata via `__wt_metadata_remove`. `try_reopen` calls `wiredtiger_open`; `reopen_aborts` forks a child and detects abort/nonzero exit.

## Control Flow
On non-Windows builds, tests prepare a home directory for each scenario, reopen as leader or follower, and assert success or abort. Leader requires both ingest and stable entries. Follower requires ingest but allows missing stable. Abort cases are isolated in child processes so `WT_ASSERT_ALWAYS` does not kill the Catch2 runner.

## State And Persistence Behavior
This test creates real WiredTiger homes and persists metadata changes across close/reopen. Metadata surgery is done in a follower connection before data handles are opened, avoiding active-handle close panics.

## Dependencies And Integration Points
Depends on Unix `fork/wait/signal`, `connection_wrapper`, test utilities, palite page-log extension path, disaggregated storage config, layered table metadata, and `__metadata_clean_incomplete_table` behavior.

## Risks And Edge Cases
Risks include role-specific requirements drifting, metadata removal while handles are active, Catch2 signal handlers interfering with abort detection, and platform incompatibility; the file is disabled on Windows.

## Test Signals
Successful reopens must return zero; invalid metadata combinations must abort or exit nonzero in the child. Homes are cleaned after each section.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_layered_incomplete_table.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_layered_ingest_uri.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_layered_ingest_uri.cpp

## Purpose
Tests deriving a layered table URI from an ingest constituent file URI.

## Important APIs, Types, And Functions
Calls `__ut_layered_derive_layered_uri(WT_SESSION_IMPL *, const char *, WT_ITEM *)` with a mock session and output buffer.

## Control Flow
Valid sections pass `file:<name>.wt_ingest` and assert output `layered:<name>`. Invalid sections check missing `file:` prefix, missing `.wt_ingest` suffix, wrong prefix, and stable suffix.

## State And Persistence Behavior
The function writes derived URI bytes into a `WT_ITEM` buffer that is freed with `__wt_buf_free`. No persistence.

## Dependencies And Integration Points
Depends on `mock_session`, `wt_internal.h`, and layered table naming conventions.

## Risks And Edge Cases
Guards against accepting malformed source URIs or deriving from stable constituent files. Names with underscores and digits are accepted.

## Test Signals
Valid inputs return zero and exact output strings; invalid inputs return `EINVAL`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_layered_ingest_uri.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_mock_session.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_mock_session.cpp

## Purpose
Directly tests basic mock-session event-handler behavior used by many internal Catch2 tests.

## Important APIs, Types, And Functions
Uses `mock_session::build_test_mock_session`, `add_callback_message`, `get_last_message`, and the mock session's `WT_EVENT_HANDLER` callbacks `handle_error` and `handle_message`.

## Control Flow
The test creates a mock session, pushes a message manually, retrieves it, obtains the event handler, invokes error and message callbacks with new strings, checks the last message each time, and asserts unsupported callbacks are null.

## State And Persistence Behavior
State is the mock session's in-memory callback-message queue or last-message store. No persistence.

## Dependencies And Integration Points
Depends on Catch2, `wiredtiger.h`, and the `mock_session` wrapper. It supports tests that expect WiredTiger error/message callbacks to be capturable.

## Risks And Edge Cases
Ensures the mock handler exposes only implemented callbacks and records both error and message paths.

## Test Signals
Exact message strings must be returned after direct insertion and callback invocation; `handle_close`, `handle_general`, and `handle_progress` must be null.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_mock_session.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_page_log_handle.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_page_log_handle.cpp

## Purpose
Tests disaggregated connection configuration for page-log handles, including optional key-provider page-log handle construction and destruction.

## Important APIs, Types, And Functions
Mock functions implement `WT_PAGE_LOG::pl_open_handle`, `terminate`, and `WT_PAGE_LOG_HANDLE::plh_close`. `setup_page_log_queue` allocates a mock `WT_PAGE_LOG`, wraps it in `WT_NAMED_PAGE_LOG`, and inserts it into `conn_impl->ext.pagelogqh`. Tests call `__wti_disagg_conn_config`, `__wti_disagg_destroy`, `__wti_conn_remove_page_log`, and `__wti_layered_table_manager_destroy`.

## Control Flow
The fixture builds a mock session/connection, initializes required spinlocks, installs the mock page log, and runs sections for handle construction without a key provider, construction with a dummy key provider, and destruction of preinstalled meta/key-provider handles. Cleanup removes page logs, destroys layered table manager state, and destroys locks.

## State And Persistence Behavior
All state is in the mock connection's disaggregated-storage fields and extension page-log queue. No durable page-log writes are performed.

## Dependencies And Integration Points
Depends on `mock_session`, `wiredtiger.h`, disaggregated storage configuration, page-log extension queues, spinlocks, and layered table manager cleanup.

## Risks And Edge Cases
The test expects `__wti_disagg_conn_config` to return `EINVAL` while still constructing certain handles, so it guards partial-initialization cleanup. It also catches missing key-provider handle creation when `conn_impl->key_provider` is set.

## Test Signals
Handle pointers must be non-null or null as expected, and destroy must null out `page_log_meta` and `page_log_key_provider`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_page_log_handle.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_pow.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_pow.cpp

## Purpose
Tests small power-of-two utility functions used throughout WiredTiger.

## Important APIs, Types, And Functions
Calls `__wt_log2_int`, `__wt_ispo2`, and `__wt_rduppo2`.

## Control Flow
Separate test cases check log2 floor results, power-of-two predicates, and rounding up to a power-of-two multiple. Inputs include zero, small exact powers, non-powers, high 32-bit boundaries, and invalid non-power alignment values.

## State And Persistence Behavior
No state or persistence.

## Dependencies And Integration Points
Depends on Catch2 and `wt_internal.h`. These utilities are general low-level helpers.

## Risks And Edge Cases
Documents intentional behavior that zero returns `0` for log2 and true for `ispo2`. `rduppo2` returns zero when the alignment argument is not a power of two.

## Test Signals
Exact integer return values are asserted for every input.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_pow.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_prepare_mod_sort.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_prepare_mod_sort.cpp

## Purpose
Tests transaction modification sorting via `__ut_txn_mod_compare`, ensuring operations sort by btree ID, key/recno, and keyedness rules needed for prepared transaction handling.

## Important APIs, Types, And Functions
Helpers include `has_key`, `__mod_ops_sorted`, `rand_non_keyd_type`, `init_btree`, `init_op`, `init_key`, `random_keys`, and `allocate_key_space`. Tests call `__wt_qsort` with `__ut_txn_mod_compare` over arrays of `WT_TXN_OP`.

## Control Flow
Scenarios cover basic column operations with non-keyed ops, row operations with non-keyed ops, mixed row/column/non-keyed ops, btree ID ordering, keyedness ordering, many row-store keys over two btrees, and column-store recno ordering. Tests allocate scratch keys where needed, sort, validate ordering, and free buffers.

## State And Persistence Behavior
All btrees, operations, and keys are in-memory test structures. `connection_wrapper` sessions provide scratch-buffer allocation for row keys.

## Dependencies And Integration Points
Depends on `wiredtiger.h`, `wt_internal.h`, `utils.h`, `item_wrapper`, `connection_wrapper`, and transaction operation internals.

## Risks And Edge Cases
Risks include non-keyed operations disrupting comparisons, row-key lexicographic ordering, column recno ordering, randomized duplicate btree IDs/keys, and comparator behavior across btree types.

## Test Signals
After sorting, `__mod_ops_sorted` must return true for each scenario. Scratch buffers are freed before assertion where needed.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_prepare_mod_sort.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_rec_upd_select.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_rec_upd_select.cpp

## Purpose
Tests `__wti_rec_upd_select`, the reconciliation helper that chooses which update from an update chain should be written, pruned, or tracked under snapshot/pinned timestamp constraints.

## Important APIs, Types, And Functions
`create_test_update` allocates `WT_UPDATE` via `__wt_upd_alloc` and sets transaction/timestamp/prepare fields. `create_update_chain` links newest-first updates. `check_update` validates selected updates. `setup_reconcile_context` initializes `WTI_RECONCILE`, and `create_test_insert` allocates a `WT_INSERT` with an update chain. `RecUpdSelectFixture` builds a mock session, transaction globals, transaction object, and row-leaf page.

## Control Flow
The basic selection test configures snapshot isolation and a three-update chain, then checks in-memory trees select the oldest writeable update while non-in-memory reconciliation selects the newest. The prune test sets `rec_prune_timestamp` and confirms in-memory reconciliation skips an update at the prune timestamp. The prepared/aborted test verifies in-memory reconciliation skips prepared and aborted updates while eviction on non-in-memory can select the prepared update and still tracks max transaction/timestamp.

## State And Persistence Behavior
State is synthetic reconciliation/session/page/update structures. The test mutates transaction snapshot fields, btree flags, reconcile flags, and update chains. No page is persisted; it models reconciliation decisions before writing.

## Dependencies And Integration Points
Depends on `mock_session`, `wt_internal.h`, `reconcile_private.h`, `reconcile_inline.h`, update allocation/free helpers, transaction visibility state, and reconciliation constants.

## Risks And Edge Cases
Risks include selecting pruned updates, mishandling prepared/aborted updates, different in-memory versus disk reconciliation semantics, and failing to maintain `r.max_txn`/`r.max_ts` while skipping writes. Manual cleanup is required for update chains, inserts, and saved update state.

## Test Signals
`__wti_rec_upd_select` must return zero, selected updates must match expected tuple fields, and reconcile max transaction/timestamp tracking must match the newest relevant update.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_rec_upd_select.cpp -->
