# subset-b-009078 Research

Grouped research for WiredTiger Python suite tests covering encryption, environment/home handling, last-error reporting, eviction, export, hazard pointers, and history-store behavior. Each section preserves the original source path for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_encrypt04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_encrypt04.py

## Purpose

Exercises mismatched connection and object encryption configurations, proving that WiredTiger either rejects incompatible encryption metadata or can still read data when the effective encryptor, key id, and secret key match.

## Important APIs, Types, and Functions

Defines `test_encrypt04`, scenario matrices for two open phases, `conn_extensions`, an overridden `setUpConnectionOpen`, deterministic `create_records`/`check_records`, and `check_okay`. It uses the `rotn` encryptor, optional `fileinclear`, and a forced `rotn_force_error` path.

## Control Flow

The test creates encrypted or clear table data under phase 1, switches instance fields to phase 2, reopens the connection, and decides success from exact equality of encryptor name, key id, and secret. On successful reopen it verifies the original records and, for changed table-level settings that remain readable, appends a second batch and verifies both batches after another reopen.

## State and Persistence Behavior

Persistence is central: records are forced through close/reopen so encrypted pages must be read from disk. Random keys and values are deterministic via seed 0. `expect_forceerror` and `got_forceerror` track whether both scenario halves selected the extension error injection path.

## Dependencies and Integration Points

Depends on `wttest`, `suite_subprocess`, `make_scenarios`, the WiredTiger extension loader, and the test-only `rotn` encryptor. It integrates with connection open configuration, table-level encryption metadata, extension customization, and stderr expectations.

## Risks and Maintenance Signals

The scenarios depend on probabilistic assumptions about wrong-key decryption not accidentally producing plausible pages, mitigated by secret keys and large randomized records. Error matching for forced decrypt failures looks for `-1000` in exception strings. It skips if extensions are unavailable.

## Test Signals

Strong signals are reopen success/failure, exact record round trips after disk flush, rejection of mismatched metadata, successful mixed clear/encrypted table behavior where allowed, and explicit assertion that forced extension errors were observed only for the intended pair.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_encrypt04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_encrypt05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_encrypt05.py

## Purpose

Validates that encryption configuration parsing rejects quoted escaped control characters embedded in key ids instead of silently accepting malformed encryption material.

## Important APIs, Types, and Functions

Defines `test_encrypt05`, the `escaped_characters` scenario list for newline, carriage return, tab, and backspace, `conn_extensions`, `conn_config`, and `test_encrypt`.

## Control Flow

The default connection opens with valid `rotn` encryption. Each scenario builds a malformed `encryption=(name=rotn,keyid="11<escaped>")` config and calls `reopen_conn`. A `WiredTigerError` is expected to mention invalid argument; afterward the test reopens with an empty config to avoid teardown using the intentionally bad configuration.

## State and Persistence Behavior

No user data is persisted. State is the connection configuration under test and the harness stderr ignore rule for the parser diagnostic.

## Dependencies and Integration Points

Uses the `wiredtiger` Python API, `wttest`, `make_scenarios`, and the `rotn` encryptor extension. It targets the WiredTiger configuration parser and encryption customization path.

## Risks and Maintenance Signals

The test only asserts when an exception is raised; if malformed input ever succeeds, the body does not explicitly fail before the valid reopen. The diagnostic text is partially normalized through stderr ignores, so wording changes may need updates.

## Test Signals

Signals are exception type, presence of `Invalid argument`, and teardown safety via a clean reopen.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_encrypt05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_encrypt06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_encrypt06.py

## Purpose

Checks that enabled encryption does not leave table data, key names, value names, column group content, or index content visible as clear text in WiredTiger files.

## Important APIs, Types, and Functions

Defines `test_encrypt06` with scenario products over storage layouts and encryptor configurations. Important helpers are `conn_extensions`, `conn_config`, `encrypt_table_params`, `match_string_in_file`, `match_string_in_rundir`, `visible_data`, and `visible_name`.

## Control Flow

For each scenario it creates two tables with named key/value columns, optional column groups, and optional indexes. It inserts patterned keys and values, closes the connection to force files to disk, then scans every run-directory file for known plaintext strings. Matched scenarios assert visibility exactly from table/system encryption settings; unmatched child object scenarios apply conservative no-leak checks.

## State and Persistence Behavior

Persistence is tested by raw file inspection after close. The test intentionally searches both data payload markers and schema-name markers, accounting for metadata/system encryption and the special case where column groups move key names out of data files.

## Dependencies and Integration Points

Depends on `os`, `wttest`, `make_scenarios`, `rotn`, optional `sodium`, table/colgroup/index creation, connection-level encryption, and per-object encryption configuration. It is skipped for tiered storage.

## Risks and Maintenance Signals

Raw substring scans can produce false positives if unrelated files contain the marker strings, though the markers are distinctive. Unmatched child-object behavior documents a current conservative expectation rather than the full theoretical API semantics.

## Test Signals

Signals are absence or presence of plaintext markers in on-disk files across system, table, index, and column-group encryption combinations, including sodium system encryption.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_encrypt06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_encrypt07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_encrypt07.py

## Purpose

Runs the general salvage regression suite against an encrypted database, ensuring salvage can locate and repair damaged encrypted pages when the test's damage marker is transformed through the encryptor.

## Important APIs, Types, and Functions

`test_encrypt07` subclasses `test_salvage01.test_salvage01`, overrides `uri`, encryption configuration, `conn_extensions`, `conn_config`, `rot13`, and `moreinit`, and re-declares parent salvage tests with tiered skips.

## Control Flow

The inherited salvage tests create data, damage files, and invoke salvage through API and process paths. This subclass loads `rotn` with key id 13 and adjusts `self.uniquebytes` in `moreinit` to the rot13-encoded byte sequence so the inherited damage logic can find the physical encrypted marker.

## State and Persistence Behavior

State and persistence are inherited from salvage: table data is written to disk, damaged, salvaged, and re-read. This subclass only changes encryption state and the damage-search bytes.

## Dependencies and Integration Points

Depends on `codecs`, `wttest`, the sibling `test_salvage01` module, and the `rotn` encryptor extension. It integrates salvage, extension loading, and inherited suite subprocess behavior.

## Risks and Maintenance Signals

The test is tightly coupled to `test_salvage01` internals, especially `uniquebytes` setup. Changes in the parent damage strategy or rotn behavior require coordinated updates.

## Test Signals

Signals are the inherited salvage API, damaged API, and process-damaged assertions running under encrypted storage; tiered mode is skipped.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_encrypt07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_encrypt08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_encrypt08.py

## Purpose

Covers system-level libsodium encryption configuration errors, especially invalid or unsupported key specifications passed to the encryptor customize method.

## Important APIs, Types, and Functions

Defines `test_encrypt08`, sodium test key constant, `encrypt_type` scenarios for missing key, key id, duplicate key specs, non-hex key, and wrong key length, plus `conn_extensions` and `test_encrypt`.

## Control Flow

The harness initially opens without encryption so exceptions can be caught explicitly. Each scenario reopens with `encryption=(name=sodium,<bad config>)` and asserts a `WiredTigerError` matching the expected sodium diagnostic.

## State and Persistence Behavior

There is no table data; persistence behavior is limited to connection reopen behavior and extension initialization state.

## Dependencies and Integration Points

Depends on `wiredtiger`, `wttest`, `make_scenarios`, and the optional `sodium` encryptor extension. It targets connection-level encryption parsing and extension customization.

## Risks and Maintenance Signals

The test assumes sodium is available or skipped by extension loading. It intentionally avoids `conn_config`; if WiredTiger later rejects reopen-with-different-encryption earlier, the test setup may need an overridden open path.

## Test Signals

Signals are scenario-specific exception regexes for no key, key IDs unsupported, duplicate key mechanisms, non-hex secrets, and wrong key length.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_encrypt08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_encrypt09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_encrypt09.py

## Purpose

Covers per-table libsodium encryption configuration errors and documents how table encryption differs from system encryption, especially around unsupported `secretkey` table options.

## Important APIs, Types, and Functions

Defines `test_encrypt09`, sodium key constant, per-file `encrypt_type` scenarios, `conn_extensions`, `conn_config`, and `test_encrypt`.

## Control Flow

The connection opens with valid system sodium encryption. The test attempts to create a file object with `encryption=(name=sodium,<scenario>)`. The no-key case succeeds because no separate encryptor is generated; keyid is rejected by sodium; `secretkey` scenarios fail earlier as unknown per-table configuration.

## State and Persistence Behavior

State is object-creation metadata only. Successful no-key creation persists a file object using inherited system encryption behavior.

## Dependencies and Integration Points

Depends on the `wiredtiger` API, `wttest`, scenario generation, and the sodium extension. It integrates system encryption setup with object-level create configuration.

## Risks and Maintenance Signals

Several expected failures are parser-level, not extension-level, by current design. If per-table secret keys become supported, the expected errors and coverage intent will change.

## Test Signals

Signals are successful create for no-key and regex-matched `WiredTigerError` failures for unsupported key id and per-table secretkey attempts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_encrypt09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_env01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_env01.py

## Purpose

Tests WiredTiger home-directory selection from explicit home arguments, `WIREDTIGER_HOME`, `use_environment`, and privileged `use_environment_priv`. The class/comment still use an older `test_priv01` name, but the source file is the environment test.

## Important APIs, Types, and Functions

Defines `test_priv01`, overrides connection/session setup to let each test open manually, and provides `populate_and_check`, `checkfiles`, `checknofiles`, and `common_test`.

## Control Flow

Each case creates candidate home directories, sets or unsets `WIREDTIGER_HOME`, opens WiredTiger with a home argument or config flag, writes a small table, and checks which directory received the `.wt` file. Privileged tests branch on `os.getuid() != os.geteuid()` to validate protected environment use.

## State and Persistence Behavior

Persistence is observed through filesystem placement of `test_priv01.wt`. Environment variables are reset in `finally` to avoid leaking process state between tests.

## Dependencies and Integration Points

Depends on Unix `os` APIs, `wiredtiger`, `wttest`, and the connection open wrapper. It is skipped for tiered and Windows-specific behavior is skipped in `setUp`.

## Risks and Maintenance Signals

`checknofiles` counts files in a directory but uses `os.path.isfile(nm)` against the current directory, so it relies on simple empty directory layouts. Full privileged-path coverage only occurs when run setuid/root-like.

## Test Signals

Signals are successful readback from the selected home, expected privilege error text, and file existence/nonexistence checks in explicit and environment homes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_env01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_error_info01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_error_info01.py

## Purpose

Validates `WT_SESSION.get_last_error()` state for ordinary success, background compaction reconfiguration errors, and two drop-related `EBUSY` reasons.

## Important APIs, Types, and Functions

`test_error_info01` inherits `error_info_util` and `compact_util`. Helpers trigger success, `WT_BACKGROUND_COMPACT_ALREADY_RUNNING`, `WT_UNCOMMITTED_DATA`, and `WT_DIRTY_DATA`; test methods assert POSIX errno, WiredTiger sub-level reason, and message.

## Control Flow

The success path creates/inserts/searches a table. Error paths start background compaction, attempt forbidden compact reconfiguration, attempt drop with an open uncommitted transaction, or commit dirty data and drop before checkpoint. Alternating/doubling tests call those methods repeatedly to ensure the last-error slot updates after every API call.

## State and Persistence Behavior

State lives in the session's last-error fields plus table transactional state. Cleanup rolls back or checkpoints/drops as needed to keep the test home usable.

## Dependencies and Integration Points

Depends on `wiredtiger`, `errno`, `time`, `open_cursor`, `error_info_util.assert_error_equal`, and background compact utilities.

## Risks and Maintenance Signals

Dirty-data timing uses `sleep(1)` to let oldest id accounting move. Reusing test methods inside alternating tests means those methods must fully clean their data state.

## Test Signals

Signals are exact major error code, sub error code, and human-readable reason for success, background compaction, uncommitted data, and dirty data, across repeated transitions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_error_info01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_error_info02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_error_info02.py

## Purpose

Exercises `get_last_error()` for `WT_ROLLBACK` sub-reasons: cache overflow, write conflicts, and oldest-pinned transaction eviction rollback.

## Important APIs, Types, and Functions

Defines `test_error_info02` with methods for cache overflow, update-list write conflict, timestamp visibility conflicts at start/stop, and oldest-for-eviction. It uses `error_info_util.assert_error_equal`.

## Control Flow

Each method creates a table and constructs a rollback source: tiny cache and eviction pressure, two sessions updating the same key, eviction of invisible disk updates, remove/insert conflicts, or an old transaction holding cache hostage. The caught public exception string is generic `WT_ROLLBACK`; the test then asserts the session's detailed sub-reason.

## State and Persistence Behavior

State spans concurrent sessions, transactions, read visibility, eviction-triggering cursors, and connection reconfiguration. Some tests switch `self.session` to the session that actually saw the error.

## Dependencies and Integration Points

Depends on `wiredtiger`, `time`, `wttest` skip hooks, and the error-info utility. It integrates transaction conflict handling, cache eviction, and rollback reason reporting.

## Risks and Maintenance Signals

The cache-overflow path is skipped for disaggregated mode and may depend on cache timing. Large values and sleeps can make runtime or flakiness sensitive to environment performance.

## Test Signals

Signals are exact sub-error constants `WT_CACHE_OVERFLOW`, `WT_WRITE_CONFLICT`, and `WT_OLDEST_FOR_EVICTION` after rollback-producing API calls.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_error_info02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_error_info03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_error_info03.py

## Purpose

Covers `get_last_error()` details for `EBUSY` drop failures caused by specific locks, backup cursors, data handles, uncommitted data, and dirty data.

## Important APIs, Types, and Functions

`test_error_info03` inherits `error_info_util`, configures timing stress, and defines lock-holder helpers, drop helpers, and tests for checkpoint, schema, table, backup, dhandle, uncommitted, and dirty conflicts.

## Control Flow

The lock tests start threads that hold locks through `session.alter` or index/table cursor activity, then concurrently attempt `drop(..., lock_wait=0...)`. Backup and dhandle tests keep a backup cursor or object cursor open. Transactional tests use uncommitted or recently committed data before drop.

## State and Persistence Behavior

State includes live threads, held locks, backup cursor handles, open data handles, and transactional dirty/uncommitted content. The test relies on timing stress settings and sleeps to place operations in the intended lock windows.

## Dependencies and Integration Points

Depends on `wiredtiger`, `wtthread`, `time`, `errno`, `wttest`, `open_cursor`, and `error_info_util`. It is skipped for disaggregated mode because `Session.alter` is unsupported.

## Risks and Maintenance Signals

Thread scheduling and timing-stress points are central; changes to schema lock acquisition order can alter the observed sub-reason. Some cursors are intentionally kept open until after assertions.

## Test Signals

Signals are `errno.EBUSY` plus exact sub-reasons for checkpoint lock, schema lock, table lock, backup, dhandle, uncommitted data, and dirty data.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_error_info03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_error_info04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_error_info04.py

## Purpose

Ensures successful commit and rollback calls that are pulled into eviction do not accidentally persist internal eviction errors into `get_last_error()`.

## Important APIs, Types, and Functions

Defines `test_error_info04`, a low-cache/dirty-eviction connection config, and two tests: `test_commit_transaction_skip_save` and `test_rollback_transaction_skip_save`.

## Control Flow

Each test opens 100 sessions, inserts large values in active transactions, lowers `cache_max_wait_ms`, then commits or rolls back all transactions. After every successful transaction end it asserts the last error is success (`0`, `WT_NONE`).

## State and Persistence Behavior

State includes many concurrent sessions with large dirty updates and connection-level eviction pressure. The intended persistence behavior is negative: successful transaction APIs must reset/keep last-error success despite eviction participation.

## Dependencies and Integration Points

Depends on `wiredtiger`, `error_info_util`, and transaction/cache reconfiguration paths.

## Risks and Maintenance Signals

The workload assumes 100 large transactions reliably trigger application eviction. It validates the session-level `get_last_error` view used by the inherited utility, not every temporary eviction sub-error internally generated.

## Test Signals

Signals are successful commit/rollback return codes and immediate `WT_NONE` last-error assertions under eviction pressure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_error_info04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_eviction01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_eviction01.py

## Purpose

Regression test for evicting update chains that contain only aborted updates, ensuring dirty eviction makes progress and does not block indefinitely.

## Important APIs, Types, and Functions

Defines `test_eviction01`, `get_stat`, and `test_eviction`; uses `SimpleDataSet`, `wiredtiger.stat.conn.cache_eviction_dirty`, and `cache_eviction_blocked_no_progress`.

## Control Flow

The test populates 100 rows, then repeatedly begins a transaction, updates nearly every row with a byte value, and rolls the transaction back. After 499 rollback-heavy iterations it checks eviction stats.

## State and Persistence Behavior

The workload creates long aborted update chains in cache without durable logical changes. Persistence is not the goal; eviction and cache state cleanup are.

## Dependencies and Integration Points

Depends on `wttest`, `SimpleDataSet`, and connection statistics.

## Risks and Maintenance Signals

Stat-based assertions can be sensitive to eviction scheduling, though the large iteration count is intended to force activity. It does not verify individual key values after rollback.

## Test Signals

Signals are dirty eviction count greater than zero and blocked-no-progress count equal to zero.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_eviction01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_eviction02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_eviction02.py

## Purpose

Verifies clean eviction removes obsolete time-window metadata within configured per-checkpoint cleanup limits.

## Important APIs, Types, and Functions

`test_eviction02` inherits `eviction_util`, sets scenario-specific `heuristic_controls`, and uses `populate`, `evict_cursor_tw_cleanup`, timestamp helpers, and statistics `cache_eviction_dirty_obsolete_tw`.

## Control Flow

Across ten rounds it inserts more timestamped data, makes it stable, checkpoints it clean, advances oldest so prior time windows become obsolete, then forces clean eviction. It tracks per-iteration cleanup deltas and final data-source/connection stats.

## State and Persistence Behavior

State is timestamped page metadata rather than user-visible values. Checkpoints reset the cleanup budget, and stats accumulate cleanup work at data-source and connection scope.

## Dependencies and Integration Points

Depends on `eviction_util`, `wiredtiger.stat`, scenario generation, statistics logging, and heuristic controls.

## Risks and Maintenance Signals

Eviction may not clean work every iteration, so the test only bounds diffs and requires eventual work. The threshold allows stale stat buffer tolerance.

## Test Signals

Signals are zero cleanup when disabled, bounded cleanup when enabled, and final positive btree/connection cleanup stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_eviction02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_eviction03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_eviction03.py

## Purpose

Confirms obsolete time-window cleanup reduces the average on-disk page footprint after eviction rewrites pages.

## Important APIs, Types, and Functions

Defines `verify_dump_pages`, `derive_avg_disk_footprint`, and `test_eviction03`; inherits `eviction_util` and `suite_subprocess` to run `wt verify -d dump_pages`.

## Control Flow

The test creates three tables, populates timestamped data, checkpoints and closes, dumps page disk sizes, reopens with high obsolete time-window cleanup limits, advances oldest, evicts pages, reopens, dumps again, and compares average `dsk_mem_size` per table.

## State and Persistence Behavior

Persistence is the core signal: page images are measured before and after cleanup through the external `wt` utility. Timestamp advancement makes time-window metadata obsolete.

## Dependencies and Integration Points

Depends on diagnostic builds, `wiredtiger.diagnostic_build`, regex parsing, `statistics.mean`, `eviction_util`, and the `wt` subprocess wrapper.

## Risks and Maintenance Signals

The test skips non-diagnostic builds and relies on debug dump output format. Average size comparisons can be affected by page layout changes unrelated to time-window metadata.

## Test Signals

Signals are successful dump-page verification and average disk footprint strictly decreasing for every table.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_eviction03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_eviction04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_eviction04.py

## Purpose

Checks reconciliation performs in-memory restoration when eviction encounters invisible updates.

## Important APIs, Types, and Functions

Defines `test_eviction04`, `conn_config`, `get_stat`, and `test_eviction`, using data-source stat `cache_write_restore_invisible`.

## Control Flow

One session commits key 1, then starts but does not commit key 2. Another debug cursor evicts the page positioned at key 1. The test asserts reconciliation restored invisible content in memory.

## State and Persistence Behavior

State includes a committed update, an uncommitted/invisible update, and an eviction-triggered reconciliation pass. The uncommitted transaction is committed after the stat check.

## Dependencies and Integration Points

Depends on `wttest`, `wiredtiger.stat`, statistics logging, and debug cursor `release_evict`. Skipped for disaggregated mode.

## Risks and Maintenance Signals

It is stat-based and assumes debug eviction succeeds. It tests a minimal single-page scenario rather than broad workloads.

## Test Signals

Signal is data-source `cache_write_restore_invisible` greater than zero after eviction.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_eviction04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_eviction05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_eviction05.py

## Purpose

Validates eviction maximum page-size statistics for clean, dirty, and update pages, and verifies per-checkpoint maximum stats reset at checkpoint.

## Important APIs, Types, and Functions

Defines `test_eviction05`, `conn_config`, `get_stat`, and `test_eviction_page_size_stats`; uses connection stats for maximum clean, dirty, and updates page size per checkpoint.

## Control Flow

The test creates and commits a row, evicts it while dirty/update state is present, checks dirty/update max stats increased and clean did not, reads the clean page back, evicts it again, checks clean stat increased, then checkpoints and expects all per-checkpoint max stats to reset to zero.

## State and Persistence Behavior

State is connection-level statistic accounting across eviction events and a checkpoint boundary. User data is minimal.

## Dependencies and Integration Points

Depends on `wiredtiger.stat`, `wttest`, debug `release_evict`, and statistics logging. Skipped for disaggregated mode.

## Risks and Maintenance Signals

The opening comment says database-run stats are not reset, but the assertions check per-checkpoint stats reset to zero; documentation drift may confuse maintainers.

## Test Signals

Signals are expected nonzero/zero page-size stat transitions and reset after checkpoint.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_eviction05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_excl.py -->
# sources/storage-engines/wiredtiger/test/suite/test_excl.py

## Purpose

Tests `session.create` semantics for `exclusive=true` and `exclusive=false` on file and table URIs, including tiered-storage scenario handling.

## Important APIs, Types, and Functions

Defines `test_create_excl` with scenario products over tiered storage sources and URI types, using `TieredConfigMixin`, `gen_tiered_storage_sources`, and `make_scenarios`.

## Control Flow

For each valid scenario it creates an object exclusively, verifies exclusive re-create fails, verifies non-exclusive re-create succeeds, and creates two new objects with exclusive and non-exclusive configs.

## State and Persistence Behavior

Persistence state is object metadata existence. No data rows are inserted.

## Dependencies and Integration Points

Depends on `wiredtiger`, `wttest`, tiered helper mixin, and session create configuration parsing. Tiered file URIs are skipped because unsupported.

## Risks and Maintenance Signals

The test asserts exception type but not error message. It only covers create idempotence, not drop/recreate or concurrent create races.

## Test Signals

Signals are `WiredTigerError` for exclusive existing object and success for non-exclusive existing or new objects.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_excl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_export01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_export01.py

## Purpose

Tests basic `backup:export` behavior: creation/removal of `WiredTiger.export`, propagation into a copied home, and correctness after restarting from an exported backup.

## Important APIs, Types, and Functions

Defines `test_export01` using `TieredConfigMixin`, `copy_wiredtiger_home`, `gen_tiered_storage_sources`, `make_scenarios`, `os`, and `shutil`. Main tests are `test_export` and `test_export_restart`.

## Control Flow

`test_export` creates three tables, inserts rows, checkpoints, opens `backup:export`, copies the home, asserts `WiredTiger.export` exists while cursor is open, closes cursor, and verifies the file is removed from home but retained in backup. `test_export_restart` copies an export backup, reopens it, creates a new table, drops an old table, opens export again, and inspects file contents.

## State and Persistence Behavior

Persistence spans home copying, backup cursor lifetime, restart into a backup directory, and export metadata updates after create/drop. Tiered scenarios flush tiers where applicable; restart is skipped for tiered.

## Dependencies and Integration Points

Depends on helper copy logic, WiredTiger backup cursor integration, filesystem operations, checkpoints, and tiered storage hooks.

## Risks and Maintenance Signals

The content check only searches for table-name substrings. Backup-copy fidelity and export file generation are sensitive to cursor lifetime and tiered flush timing.

## Test Signals

Signals are export file existence/removal, backup copy retention, restart usability, and `exportc` present while dropped `exportb` is absent.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_export01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hazard.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hazard.py

## Purpose

Stress-regression test for dynamic growth and cleanup of a session's hazard pointer array.

## Important APIs, Types, and Functions

Defines `test_hazard` with a single method that uses `SimpleDataSet` and many open cursors.

## Control Flow

It populates a 1000-row table, opens 10,000 cursors on the same session, positions each on key 10 to pin a page and allocate a hazard pointer, stores cursors, then closes them all.

## State and Persistence Behavior

State is in-memory hazard pointer allocation and release; data persistence is incidental through dataset population.

## Dependencies and Integration Points

Depends on `wttest`, `SimpleDataSet`, cursor search, and internal hazard pointer management.

## Risks and Maintenance Signals

The test has no explicit stat assertions; success is no crash, no allocation failure, and no teardown leak. It is a coarse stress signal.

## Test Signals

Signal is completion of massive cursor open/search/close cycle without errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hazard.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_home.py -->
# sources/storage-engines/wiredtiger/test/suite/test_home.py

## Purpose

Covers connection home metadata APIs: `is_new`, `get_home`, and creation of `WiredTiger.basecfg` depending on `config_base`.

## Important APIs, Types, and Functions

Defines three test classes: `test_isnew`, `test_gethome`, and `test_base_config`.

## Control Flow

`test_isnew` checks a fresh connection is new, closes/reopens `.` and checks false. `test_gethome` checks default home `.` and a separately created directory. `test_base_config` asserts default base config exists, then opens another home with `config_base=false` and asserts no base config file.

## State and Persistence Behavior

Persistence is observed by closing/reopening connections and checking filesystem artifacts. The base config test opens an additional connection manually.

## Dependencies and Integration Points

Depends on `os`, `wttest`, connection open wrappers, and WiredTiger connection methods `is_new` and `get_home`.

## Risks and Maintenance Signals

The tests assume harness home is `.` and that base configuration is created during default test setup. It does not inspect base config contents.

## Test Signals

Signals are boolean API results and existence/nonexistence of `WiredTiger.basecfg`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_home.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs01.py

## Purpose

Broad history-store durability test for updates and modifies across checkpoints, crash-style backup recovery, precise versus fuzzy checkpoint behavior, and timestamp visibility.

## Important APIs, Types, and Functions

Defines scenario products over key formats and `precise_checkpoint`. Helpers include `large_updates`, `large_modifies`, `durable_check`, and `get_stat`; uses `wiredtiger.Modify` and history-store stats.

## Control Flow

The test inserts 10k rows, checkpoints, holds an old reader while applying large updates so checkpoint writes old versions to history store, verifies stats and recovery, repeats with modify chains, then applies timestamped updates beyond stable timestamp and checks recovered visibility before and after advancing stable.

## State and Persistence Behavior

State spans user table pages, history-store inserts, stable/oldest timestamps, long-running readers, and backup-copy recovery into `BACKUP`. Precise checkpoints keep unstable updates in memory where fuzzy checkpoints may move them to HS.

## Dependencies and Integration Points

Depends on `copy_wiredtiger_home`, `SimpleDataSet`, `wiredtiger.stat`, scenario generation, and timestamp helpers. Disaggregated mode skips the fuzzy durable check.

## Risks and Maintenance Signals

Stat exactness is tied to row counts and reconciliation behavior. Backup recovery checks only first cursor value, not every row.

## Test Signals

Signals are exact HS insert/key/update stats, recovered values after simulated recovery, and stable timestamp visibility across checkpoint modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs02.py

## Purpose

Tests truncate visibility when history-store entries and timestamped updates coexist.

## Important APIs, Types, and Functions

Defines `large_updates`, a scanning `check` helper with expected value/count tuples, and scenarios for string-row and column-store key formats.

## Control Flow

It creates a main and extra table, writes one-third of rows at timestamp 1, pins oldest/stable, writes all rows at timestamp 100, forces pages out through updates to the extra table, truncates the first half of the main table at timestamp 200, then reads at timestamps 1, 100, and 200.

## State and Persistence Behavior

State includes timestamped row versions, history-store content pushed by cache pressure, and a range tombstone/truncate committed at a later timestamp.

## Dependencies and Integration Points

Depends on `SimpleDataSet`, `wttest`, scenario generation, timestamped transactions, and session truncate.

## Risks and Maintenance Signals

The `check` helper assumes scan order groups values exactly according to expected counts. It validates returned value runs more than individual key boundaries.

## Test Signals

Signals are full visibility at ts100, earlier value preservation at ts1, and half-table visibility after truncate at ts200.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs03.py

## Purpose

Ensures checkpoints do not perform excessive history-store reads when only a small amount of new work needs reconciliation.

## Important APIs, Types, and Functions

Defines `test_hs03`, `get_stat`, and `large_updates`; uses connection stats `cache_write_hs` and `cache_hs_read` across column, integer row, and string row formats.

## Control Flow

The test loads a large table, checkpoints, pins stable low, performs 10k timestamped updates to create history-store pressure, checkpoints, then advances stable through small increments. For each increment it updates one record, checkpoints, and measures history-store reads during that checkpoint.

## State and Persistence Behavior

State is history-store volume plus checkpoint read accounting. The cache is intentionally small to make history overflow the cache.

## Dependencies and Integration Points

Depends on `SimpleDataSet`, fast statistics, scenario generation, and timestamp controls.

## Risks and Maintenance Signals

The allowed HS read bound is heuristic (`<=200`) because eviction and checkpoint concurrency can skew behavior. The first `assertGreaterEqual(hs_writes, 0)` is a weak sanity check.

## Test Signals

Signal is bounded `cache_hs_read` growth for small checkpoint increments after a large HS workload.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs04.py

## Purpose

Verifies configuration and reconfiguration of history-store `file_max`, including in-memory mode where HS disk settings are ignored.

## Important APIs, Types, and Functions

Defines `WT_MB`, scenario products for initial file max, reconfigured file max, and `in_memory`, plus `conn_config`, `get_stat`, and `test_hs`.

## Control Flow

The connection opens with optional `history_store=(file_max=...)` and optional `in_memory`. The test creates a table, checks `cache_hs_ondisk_max`, reconfigures `history_store.file_max`, expects either a below-minimum error or updated stat, and repeats in-memory expectations.

## State and Persistence Behavior

State is configuration-derived connection statistic state. No history-store workload is generated.

## Dependencies and Integration Points

Depends on `wiredtiger`, `wttest`, scenario generation, connection reconfigure, and `stat.conn.cache_hs_ondisk_max`.

## Risks and Maintenance Signals

It validates stat values, not actual file-size enforcement. Minimum boundary expectations assume 99MB remains below the configured lower bound.

## Test Signals

Signals are exact stat values for default/100MB/0, rejection of too-low reconfigure, and ignored HS settings under in-memory mode.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs06.py

## Purpose

Large collection of history-store read regressions covering direct HS reads without memory spikes, modify reconstruction, prepared updates, same-timestamp updates, multiple modifies, instantiated modifies, and reconciliation of modifies from HS.

## Important APIs, Types, and Functions

Defines `test_hs06` with helpers `get_stat`, `get_non_page_image_memory_usage`, and `create_key`, and eight test methods using `wiredtiger.Modify`, checkpoint cursors, prepared transactions, and read timestamps.

## Control Flow

The methods create timestamped full values and modify chains, checkpoint/evict them into history store, then read historical versions. Some tests read checkpoints at explicit debug timestamps, some verify prepare conflicts or between commit/durable reads, and others force cache pressure with an extra table before reading reconstructed values.

## State and Persistence Behavior

State includes data-store page images, HS full updates and reverse deltas, prepared updates, same-timestamp update chains, stable/oldest timestamps, and memory usage stat `cache_bytes_other`.

## Dependencies and Integration Points

Depends on `wiredtiger.Modify`, fast stats, scenario key formats, checkpoint cursor debug config, prepared transaction APIs, and cache pressure from small caches.

## Risks and Maintenance Signals

The memory-spike assertion uses a loose doubled threshold. Comments contain old `las` terminology. Workloads are heavy and rely on eviction/checkpoint behavior rather than direct HS inspection.

## Test Signals

Signals are exact historical values at timestamps, prepare conflict exceptions, successful read between commit/durable timestamps, and bounded non-page memory growth.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs07.py

## Purpose

Tests that the history-store sweep server removes obsolete entries while preserving correct visible data after repeated update/modify cycles.

## Important APIs, Types, and Functions

Defines `large_updates`, `check`, and `test_hs` across column and integer row formats with a small cache and high eviction update triggers.

## Control Flow

The test writes 10k rows at timestamp 1, pins oldest/stable, pushes pages out with an extra table, advances timestamps, sleeps for sweep cleanup, then repeats cycles of modifies and full updates at later timestamps 200 and 300, each time checking reads after sweep.

## State and Persistence Behavior

State includes obsolete HS records, sweep-server cleanup timing, oldest/stable timestamp advancement, and extra-table eviction pressure.

## Dependencies and Integration Points

Depends on `time.sleep`, `wiredtiger.Modify`, `SimpleDataSet`, scenario generation, and the background history-store sweep server.

## Risks and Maintenance Signals

The three 10-second sleeps make runtime long and environment-dependent. It does not assert sweep stats directly; correctness after sweep is the main signal.

## Test Signals

Signals are successful full-table scans at expected values after timestamp advancement and sweep windows, plus ignored long-eviction stdout warnings.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs08.py

## Purpose

Verifies modify insertion into the history store, including when modifies are preserved, reconstructed, or squashed during checkpoint.

## Important APIs, Types, and Functions

Defines `test_hs08`, `get_stat`, and `test_modify_insert_to_hs`; uses `wiredtiger.Modify`, `cache_write_hs`, and `cache_hs_write_squash`.

## Control Flow

A single key starts with a 1000-byte value, then receives several timestamped append/replace modifies separated by checkpoints. The test reads at timestamps 3, 4, 5, 7, and 8, then applies multiple modifies in the same transaction and across transactions to verify squash accounting under same and different timestamps.

## State and Persistence Behavior

State is a focused single-key HS chain containing full updates, reverse modifies, and squashed modify records. Checkpoints trigger HS writes and stat updates.

## Dependencies and Integration Points

Depends on `wiredtiger.Modify`, all statistics, scenario key formats, timestamped transactions, and checkpoint `use_timestamp=true`.

## Risks and Maintenance Signals

Squash stat assertions are exact for some phases and monotonic for HS writes; internal squash policy changes may require updating counts. Single-key coverage is precise but narrow.

## Test Signals

Signals are exact values at historical timestamps, increasing HS write stats, and expected squash counts for same-timestamp modifies.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs09.py

## Purpose

Inspects checkpoint images to ensure the newest committed version is written to the data store and the second-newest committed version is written to the history store, excluding uncommitted/prepared updates.

## Important APIs, Types, and Functions

Defines `check_ckpt_hs`, which opens checkpoint cursors on the user table and `file:WiredTigerHS.wt`, and tests uncommitted, prepared, newest-version, and deleted-version cases.

## Control Flow

Each test writes timestamped versions, optionally leaves an uncommitted or prepared update on top, checkpoints, then scans the checkpoint data file and history store. HS tuples are checked for update type, value bytes, start timestamp, and stop timestamp.

## State and Persistence Behavior

State includes checkpoint-visible data-store records and raw HS table entries. Prepared updates use `ignore_prepare` semantics on checkpoint cursors.

## Dependencies and Integration Points

Depends on direct `WiredTigerHS.wt` cursor schema, scenario key formats, prepared transaction APIs, and checkpoint cursor behavior.

## Risks and Maintenance Signals

Direct HS tuple layout and update type numeric constants are internal and fragile. The delete test uses expected data value `0` as a sentinel to avoid comparing removed rows.

## Test Signals

Signals are checkpoint data values, HS standard update values and timestamps, absence of tombstone/birthmark update types, and exclusion of uncommitted/prepared top updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs10.py

## Purpose

Regression test for reading modify histories correctly after eviction forces the original page out of cache.

## Important APIs, Types, and Functions

Defines `test_hs10` with `get_stat` and `test_modify_insert_to_hs`, using small cache, one eviction thread, and column/integer row scenarios.

## Control Flow

It writes a base value and three timestamped modifies, checkpoints, fills another table with many records to force eviction of the first table, then reads key 1 at timestamps 3, 4, and 5 through different cursors.

## State and Persistence Behavior

State is a single-key modify chain persisted through checkpoint and later reloaded from HS/data-store after cache pressure.

## Dependencies and Integration Points

Depends on `wiredtiger.Modify`, scenario generation, timestamped reads, and cache pressure from a second table.

## Risks and Maintenance Signals

The extra-table writes rely on cache pressure instead of an explicit eviction stat. `get_stat` is unused.

## Test Signals

Signals are exact reconstructed values `value1+A`, `value1+AB`, and `value1+ABC` after eviction pressure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs11.py

## Purpose

Tests how no-timestamp updates or deletions clear obsolete history-store records, and contrasts that with timestamped removals that should not clear HS content the same way.

## Important APIs, Types, and Functions

Defines a large scenario matrix over key format, update/deletion, long-running transaction, final modify, row count, and insert/update-list location. Helpers include `create_key`, `get_stat`, and `evict_cursor`.

## Control Flow

The first test writes timestamped versions 1-4, optionally evicts them, optionally adds a timestamp 5 modify and long reader, then applies no-timestamp changes to even keys, checkpoints, evicts, adds timestamp 10 updates, and reads historical timestamps. The second performs timestamped removals at 10 and verifies older visibility without HS truncation.

## State and Persistence Behavior

State includes HS records on insert or update lists, globally visible versus pinned no-timestamp updates, optional modify records, and statistic `cache_hs_key_truncate_onpage_removal`.

## Dependencies and Integration Points

Depends on `wiredtiger.Modify`, statistics, scenario generation, `wttest.transaction`, and debug eviction cursors.

## Risks and Maintenance Signals

The scenario matrix is large and mutates `self.timestamps` when modifies are enabled, which can be subtle across scenarios. It assumes even/odd key partitioning for expectations.

## Test Signals

Signals are historical read values/notfound outcomes at each timestamp and HS truncate stat greater than zero only for no-timestamp deletion clearing.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs12.py

## Purpose

Verifies reverse modifies that append or prepend string content remain visible to an older snapshot after later updates and eviction.

## Important APIs, Types, and Functions

Defines `test_hs12` with one test across column and integer row formats, using `wiredtiger.Modify` offsets beyond end and at start.

## Control Flow

It inserts two values, modifies key 1 by appending `A` at offset 130 and key 2 by prepending `AB`, confirms another session sees those values, starts a long transaction in that session, updates key 1 to a new value, evicts the page with `release_evict`, and checks the older session still sees the modified historical values.

## State and Persistence Behavior

State includes non-timestamped snapshots, reverse modify reconstruction, and eviction while an older transaction pins visibility.

## Dependencies and Integration Points

Depends on `wiredtiger.Modify`, scenario key formats, multiple sessions, and debug eviction cursor behavior.

## Risks and Maintenance Signals

The declared `valuebig` is unused. The test focuses on one append and one prepend case, not broad offset coverage.

## Test Signals

Signals are older-snapshot values `value1 + A` and `AB + value1` after eviction.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs12.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs13.py

## Purpose

Tests reverse modify traversal after eviction when an older snapshot should reconstruct the first modified value despite newer modifies and full updates.

## Important APIs, Types, and Functions

Defines `test_hs13` with one method using `wiredtiger.Modify`, two sessions, and debug eviction.

## Control Flow

The test inserts a large value, applies a modify that prepends `A`, confirms another session sees it, starts that session's transaction, then applies a second modify and a full replacement. After evicting the page, the older transaction searches key 1 and must still see `A + value1`.

## State and Persistence Behavior

State is a historical snapshot anchored before later updates, plus HS/reverse-delta state created by eviction of the page.

## Dependencies and Integration Points

Depends on scenario key formats, modify API, cursor snapshots, and `release_evict`.

## Risks and Maintenance Signals

`value3` is unused. The regression is narrow but targets a historically delicate reverse-modify traversal path.

## Test Signals

Signal is exact older value after eviction despite newer modify/full-update chain.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs13.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs14.py

## Purpose

Performance regression test ensuring point-in-time reads with mostly invisible history-store records are not an order of magnitude slower than reads where HS records are visible.

## Important APIs, Types, and Functions

Defines `test_hs14`, `create_key`, and one workload across column and string row formats. It uses wall-clock `time.time`.

## Control Flow

It writes multiple versions per key, checkpoints to populate HS, measures scanning at read timestamp 3 where value3 is visible, then deletes at timestamp 5 and reinserts at 10, checkpoints again, and measures reads at timestamp 9 where keys are not found because HS entries are invisible.

## State and Persistence Behavior

State is a large HS population with visible and invisible windows. The persistence effect is checkpointed HS content; the metric is scan latency.

## Dependencies and Integration Points

Depends on timestamped transactions, checkpoints, `wiredtiger.WT_NOTFOUND`, and wall-clock timing.

## Risks and Maintenance Signals

Wall-clock tests can be noisy; the threshold is deliberately loose at 10x. It detects gross regressions rather than small performance changes.

## Test Signals

Signal is `invisible_hs_latency < visible_hs_latency * 10` with correct value/notfound assertions during scans.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs14.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs15.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs15.py

## Purpose

Ensures eviction does not clear history-store content a second time after checkpoint has already handled an update without timestamp.

## Important APIs, Types, and Functions

Defines `test_hs15`, `create_key`, and a single timestamp/no-timestamp interaction workload across column and string row formats.

## Control Flow

The test inserts a no-timestamp base value, adds many timestamped rows for eviction pressure, modifies key 1 at timestamp 1, updates it at timestamp 2, advances oldest, checkpoints, then updates key 1 and many other keys at timestamp 3. It reads key 1 at timestamps 1, 2, and 3.

## State and Persistence Behavior

State includes a no-timestamp base update, timestamped modify/update records, checkpoint cleanup, and later eviction pressure that must not over-clear HS records.

## Dependencies and Integration Points

Depends on `wiredtiger.Modify`, timestamp helpers, small cache, and scenario generation.

## Risks and Maintenance Signals

The test does not directly verify eviction happened; it relies on many inserts into a small cache. It is a specific regression sequence.

## Test Signals

Signals are exact values at timestamps 1, 2, and 3 after checkpoint and later pressure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs15.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs16.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs16.py

## Purpose

Regression test that checkpointing does not panic when a no-timestamp update is inserted into history-store-related reconciliation state while another session pins visibility.

## Important APIs, Types, and Functions

Defines `test_hs16`, `create_key`, and one test across column/string row formats.

## Control Flow

It writes key 1 without timestamp, writes timestamped values at 1 and 2, opens another session with an active transaction to make a later no-timestamp update non-globally visible, applies that no-timestamp update, then checkpoints.

## State and Persistence Behavior

State is a mixed timestamp/no-timestamp chain with a second session holding a transaction. The expected behavior is simply successful checkpoint.

## Dependencies and Integration Points

Depends on small cache, scenario generation, transaction `no_timestamp=true`, multiple sessions, and checkpoint reconciliation.

## Risks and Maintenance Signals

There are no value or stat assertions; it is a no-crash regression. The code appears to set key 2 through `cursor` rather than `cursor2`, but its role is to keep session2 active.

## Test Signals

Signal is checkpoint completion without panic or exception.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs16.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs18.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs18.py

## Purpose

Comprehensive older-reader regression suite for interactions between timestamped updates, no-timestamp updates, modifies, tombstones, history-store eviction, and snapshot readers.

## Important APIs, Types, and Functions

Defines helpers `create_key`, `check_value`, `update_kv`, `start_txn`, and `evict_key`. Test methods cover a base scenario, read timestamp behavior, tombstone ignoring, multiple older readers, multiple missing timestamps, and modifies.

## Control Flow

Each method creates one-key version chains, starts long-running transactions at carefully chosen points, evicts pages with debug cursors, applies no-timestamp and timestamped updates/modifies, then verifies old cursors still read their expected versions. The modifies case also checkpoints to update internal last-running state before eviction.

## State and Persistence Behavior

State includes several concurrent sessions with pinned snapshots, HS entries created by eviction, no-timestamp globally visible updates, timestamped updates, tombstones, and reverse modifies.

## Dependencies and Integration Points

Depends on `wiredtiger.Modify`, `wttest`, scenario generation, multiple sessions, timestamped reads, and debug eviction.

## Risks and Maintenance Signals

The tests are intricate and rely on exact snapshot timing. Some comments acknowledge changed visibility for timestamp readers after eviction, so expectations encode nuanced internal behavior.

## Test Signals

Signals are exact per-session values before and after eviction across older readers, timestamp readers, missing timestamp chains, tombstone handling, and modify reconstruction.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs18.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs19.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs19.py

## Purpose

Regression test for reconstructing historical modify chains when a newer modify could otherwise be incorrectly used as the base during history-store rewrite/eviction.

## Important APIs, Types, and Functions

Defines `test_hs19`, `create_key`, and one scenario across column/string row formats.

## Control Flow

It starts with a no-timestamp base, applies modifies at timestamps 2 and 3, pins reconciliation state with another session, adds a large append modify at 4, a selected on-disk modify at 5, checkpoints, adds another modify at 6, evicts the page, then reads at timestamps 2, 3, and 4.

## State and Persistence Behavior

State includes a sequence of modifies in HS/data-store, a pinned transaction on a junk table, stable/oldest at 1, and eviction of a dirty page after checkpoint.

## Dependencies and Integration Points

Depends on `wiredtiger.Modify`, scenario generation, checkpoint `use_timestamp=true`, debug eviction, and multi-session timing.

## Risks and Maintenance Signals

The expected timestamp 4 reconstruction is manually assembled and includes append semantics that are easy to get wrong. It is a narrow but high-value corruption regression.

## Test Signals

Signals are exact reconstructed values at timestamps 2, 3, and 4 after checkpoint plus eviction.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs19.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs20.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs20.py

## Purpose

Ensures reverse modifies in the history store are not reconstructed using an on-page overflow value as the wrong base.

## Important APIs, Types, and Functions

Defines `test_hs20`, key factory functions for column/string row formats, extra rollback allowance, and one workload using `leaf_value_max=10B` to force overflow values.

## Control Flow

The test inserts large overflow values at timestamp 2, appends modifies at 3 and 4, writes many additional rows to force eviction, replaces the original keys with smaller values at 5, checkpoints, then reads the timestamp 3 version of the first ten keys.

## State and Persistence Behavior

State includes overflow value storage, HS reverse modify records, eviction pressure from 100k rows, and checkpointed current disk images.

## Dependencies and Integration Points

Depends on `wiredtiger.Modify`, small-cache eviction, overflow item configuration, platform-specific stdout ignore on Darwin, and scenario generation.

## Risks and Maintenance Signals

Runtime is heavy due to 100k inserts and small cache. The test has no direct HS stat checks; correctness is historical read reconstruction.

## Test Signals

Signals are exact timestamp-3 reads of `value1 + B` for all original keys after overflow/eviction/checkpoint.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs20.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs21.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs21.py

## Purpose

Tests that idle data handles with active history can be swept/closed without losing historical visibility or changing run write generation during the same process lifetime.

## Important APIs, Types, and Functions

Defines `large_updates`, `check`, `parse_run_write_gen`, and `test_hs`; uses file-manager close settings, connection stats, metadata parsing, and ten tables.

## Control Flow

The test creates ten tables, records each file's `run_write_gen`, writes half-row values at timestamp 2, opens a long-running reader at timestamp 2, writes full-row values at timestamp 100, advances stable, repeatedly checkpoints and polls sweep stats until handles close, then verifies the old reader still sees timestamp 2 data and current reads see timestamp 100 data. It also checks run write gen stability outside disaggregated mode.

## State and Persistence Behavior

State spans multiple table handles, active history newer than oldest, long-running read transactions across handle close/reopen, metadata run-write generation, and sweep statistics.

## Dependencies and Integration Points

Depends on `SimpleDataSet`, `wiredtiger.stat`, metadata cursors, regex parsing, file-manager sweep configuration, and timestamps. Skipped for tiered storage.

## Risks and Maintenance Signals

Polling for sweep closure is timing-sensitive. `final_numfiles=3` assumes only metadata, HS, and lock files remain open. Disaggregated mode relaxes run-write-gen assertion due to a FIXME.

## Test Signals

Signals are sweep close stats, preserved historical reads after handle closure, current data reads, and unchanged run write generation where applicable.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs21.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs24.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs24.py

## Purpose

Races no-timestamp fixes with history-store checkpointing to ensure crash recovery sees consistent data-store and history-store checkpoints.

## Important APIs, Types, and Functions

Defines `test_hs24` scenarios over key formats and timing stress (`checkpoint_slow` or `history_store_checkpoint_delay`), `moresetup`, `missing_ts_deletes`, `missing_ts_commits`, and two race tests.

## Control Flow

Both tests write two timestamped versions per row, set stable timestamp, launch a worker thread that performs no-timestamp deletes or commits across all rows, checkpoint while that thread runs, join it, then simulate crash restart. Post-restart reads at timestamps 5/4 or 4 validate that checkpoint state is internally consistent despite partial race progress.

## State and Persistence Behavior

State includes concurrent no-timestamp operations, timing-stressed checkpoint/HS checkpoint windows, crash-restart recovery, and timestamped historical reads.

## Dependencies and Integration Points

Depends on `wtthread`, `simulate_crash_restart`, `wiredtiger.WT_NOTFOUND`, scenario generation, timing stress config, and multi-session worker threads.

## Risks and Maintenance Signals

The race window is encouraged by sleep and timing stress, not fully deterministic. Assertions allow a prefix-like split between rows affected before checkpoint and rows not affected, using `newer_data_visible` transitions.

## Test Signals

Signals are successful crash restart and consistent historical visibility: newer data implies older HS version exists, missing newer data implies older read is also not found or sees only allowed pre-checkpoint values.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs24.py -->
