# subset-b-009075 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compat03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compat03.py

Purpose: exercises WiredTiger compatibility parsing at database creation time, especially `compatibility=(release=...)`, `require_max`, and `require_min` against expected log-version ranges.

Important APIs and control flow: `test_compat03` inherits `WiredTigerTestCase` and `suite_subprocess`, builds a Cartesian scenario matrix with `make_scenarios`, creates a separate `TEST` home, assembles `wiredtiger_open` configuration strings with logging enabled, and decides whether the open should fail based on future releases, max/min ordering, and release/log compatibility. Successful scenarios open and close the connection; failing scenarios assert `WiredTigerError` with a version-incompatibility pattern.

State, persistence, and dependencies: the test creates a WiredTiger home and log-enabled database metadata but does not populate tables. It depends on `wiredtiger`, `wttest`, `suite_subprocess`, `wtscenario`, filesystem directory creation, and compatibility/log version mappings embedded in the test.

Integration points: covers the public `wiredtiger_open` compatibility API, log version selection, patch-version normalization, and startup validation before normal workload execution.

Risks and test signals: scenario expectations are tightly coupled to the release-to-log-version table; when adding releases, `future_logv`, default log version, and max/min lists must be updated together. Test pass/fail signals are correct rejection of impossible/future requirements and acceptance of legal compatibility combinations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compat03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compat04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compat04.py

Purpose: verifies that a database created at one compatibility release can be reconfigured to another release and then reopened with that release as both current and required maximum.

Important APIs and control flow: `conn_config()` creates the initial database with `config_base=true/false`, logging, and optional `compatibility=(release=...)`. `test_compat04()` creates a logged table, inserts 2000 integer records to force multiple log files, calls `self.conn.reconfigure('compatibility=(release=...)')`, closes the connection, and reopens with `compatibility=(release=...,require_max=...)`.

State, persistence, and dependencies: the persistent state is a logged WiredTiger home with table metadata and log files generated under different compatibility settings. Dependencies are `wttest`, `suite_subprocess`, `make_scenarios`, the WiredTiger connection reconfiguration path, and log compatibility code.

Integration points: exercises the upgrade/downgrade compatibility lane after initial creation, including `config_base` variants and patch-number parsing such as `3.0.0`.

Risks and test signals: the test assumes every listed release transition is legal; release table changes can invalidate expectations. Success is a clean reopen after reconfiguration with no data verification beyond successful log/database recovery, so failures usually identify compatibility metadata or log-version negotiation regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compat04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compat05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compat05.py

Purpose: checks backward-compatible log archive configuration aliases, verifying how `archive` and `remove` settings control log file deletion.

Important APIs and control flow: scenarios vary `log=(...,archive=...,remove=...)`. `conn_config()` enables logging with small `file_max`; `test_compat05()` populates 10000 rows through `SimpleDataSet`, asserts that a second log exists, checkpoints, then `check_remove()` polls up to 90 seconds for `WiredTigerLog.0000000001` to disappear.

State, persistence, and dependencies: the test persists log files in the WiredTiger home and relies on the background log removal/archive machinery after checkpoint. It depends on `SimpleDataSet`, `wttest`, `suite_subprocess`, filesystem `os.path.exists`, and time-based polling. It is skipped for tiered storage.

Integration points: targets compatibility of old `archive` spelling versus current `remove` semantics, including override ordering when both appear.

Risks and test signals: the one-second polling loop can be slow or timing-sensitive on loaded machines. A pass means the first log is retained or deleted exactly as the scenario declares; failures indicate config parsing precedence or log archive scheduling regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compat05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compress01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compress01.py

Purpose: smoke-tests block compression across file and table data sources with multiple compressor extensions.

Important APIs and control flow: scenario matrices combine URI type (`file:` or `table:`) with compressors (`nop`, `lz4`, `snappy`, `zlib`, `zstd`, `iaa`, plus compatibility names). `conn_extensions()` requests compressor extension loading and skips when missing. `test_compress()` creates a string-key/string-value object with `block_compressor`, inserts 100 mixed large/small values, reopens the connection to force disk reads, then searches every key and verifies exact values.

State, persistence, and dependencies: state lives in compressed WiredTiger pages on disk. The reopen boundary is central because it clears cached values and validates decompression from persisted pages. Dependencies are `wttest`, `make_scenarios`, extension loading, and the cursor insert/search API.

Integration points: covers compressor extension registration, table/file creation config, block manager compression/decompression, and compatibility with old raw-compression variants.

Risks and test signals: unavailable compressors skip scenarios, so coverage depends on build configuration. The signal is full value equality after reopen; failures point to compressor configuration, extension loading, page write/read, or value-boundary handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compress01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compress02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compress02.py

Purpose: verifies that zstd compression level can be changed after restart while existing tables remain readable using the original compression settings.

Important APIs and control flow: `conn_config()` starts with `builtin_extension_config={zstd={compression_level=6}}`. The test creates a zstd-compressed table, writes 1000 large values one transaction per key through `large_updates()`, verifies all values in `check()`, checkpoints, copies the WiredTiger home to `RESTART`, closes, and reopens the copy with compression level 9.

State, persistence, and dependencies: persisted table pages and metadata survive a simulated crash/restart via `copy_wiredtiger_home`. Dependencies are zstd extension loading, `SimpleDataSet`, `wttest.zstdtest`, checkpoint durability, and cursor iteration.

Integration points: exercises builtin extension configuration parsing, zstd compressor state, recovery/reopen, and metadata compatibility between old and new compressor levels.

Risks and test signals: only readability is asserted, not that newly written pages use the new level. A pass means data written at level 6 remains readable after reopening with level 9; failure indicates zstd config, metadata persistence, or restart/recovery issues.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compress02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config01.py

Purpose: adapter test that reuses `test_base03` while substituting scenario-generated session creation configuration strings.

Important APIs and control flow: `test_config01` subclasses `test_base03.test_base03` and overrides only `config_string()` to return `self.session_create_scenario.configString()`. The inherited base test creates data sources, populates records, and validates base cursor/table behavior under many `session.create` configuration combinations.

State, persistence, and dependencies: persistence behavior is inherited from `test_base03`; this file's only state is the active scenario object. It depends on `test_base03` and whatever session-create scenarios that base class defines.

Integration points: connects the generic base table tests to the WiredTiger configuration scenario framework. It is an integration shim rather than an independent workload.

Risks and test signals: because behavior lives in the base class, failures may be misattributed to this small file. The signal is inherited base-test success across generated create configurations; risks are scenario object API drift or base-class renaming.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config02.py

Purpose: validates `wiredtiger_open` home-directory resolution using explicit home arguments, `WIREDTIGER_HOME`, relative/absolute paths, and filesystem error cases.

Important APIs and control flow: setup disables the default connection/session open. `common_test()` optionally sets `WIREDTIGER_HOME`, opens with `create`, populates a table, and clears the environment in a `finally` block. Individual tests verify current directory, relative and absolute homes, explicit home taking precedence over environment, environment-only homes, missing directories, and non-writable directories.

State, persistence, and dependencies: each success path persists a `test_config02.wt` file in the selected home directory. Dependencies are `os.putenv`, `os.unsetenv`, directory permissions, `wiredtiger_open`, and cursor/table APIs. The suite skips tiered hooks because environment home selection conflicts with tiered behavior.

Integration points: targets the C/Python connection API boundary and environmental configuration handling.

Risks and test signals: permissions and environment APIs vary by platform, with Windows-specific skips. Pass/fail signals are correct file placement, empty unused env directory, and expected filesystem errors for missing or unwritable homes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config03.py

Purpose: probabilistically combines many `wiredtiger_open` configuration options to validate parser acceptance and expected rejection paths.

Important APIs and control flow: scenario generators vary cache size, create flag, error prefix, eviction target/trigger, multiprocess, session max, transactional, and verbose settings. `setUpConnectionOpen()` builds a config string from scenario attributes, predicts failures for no-create homes and invalid eviction ordering, asserts those failures, rewrites to a known-good config, then returns a successful connection for inherited `test_base03` work.

State, persistence, and dependencies: persisted state is the base test's database created under the generated connection config. Dependencies include `wtscenario.quick_scenarios`, `test_base03`, direct `wiredtiger.wiredtiger_open` for expected-failure checks, and `self.wiredtiger_open` for normal setup.

Integration points: tests connection config parsing plus base table/cursor behavior under broad config combinations.

Risks and test signals: the probabilistic prune means not every combination runs. Expected failure strings are platform-sensitive for missing homes. A good signal is both rejection of invalid configs and successful inherited data operations after repairing the config.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config04.py

Purpose: individually tests connection-level configuration options and parser edge cases.

Important APIs and control flow: helper methods open with `create,statistics=(fast)`, populate a table, read statistics, or check log-file placement. Tests cover cache size suffixes and min/max bounds, eviction percentage and absolute-size validation, dirty/update/checkpoint target ordering, unknown keys, malformed brackets/quotes/escapes, quoted valid configs, error prefixes, log paths, multiprocess, session max, default transactional behavior, and still-accepted removed LSM metadata options.

State, persistence, and dependencies: successful tests create tables and sometimes log files in default, relative, or absolute directories. Dependencies include `wiredtiger`, `wttest`, `stat.conn.cache_bytes_max`, filesystem directories, and optional hook awareness for tiered/disagg error-message matching.

Integration points: broad coverage of the public connection configuration grammar and semantic validation logic.

Risks and test signals: many assertions match error text and can be affected by hook-added configs. Removed LSM config acceptance is an upgrade compatibility signal. Failures usually reveal config parser, validation, stats, or log path regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config05.py

Purpose: tests multiple connection/session open constraints, session limits, exclusive create, and duplicate database management.

Important APIs and control flow: default setup is disabled so each test opens explicitly. Helpers populate and verify a simple string table. Tests cover normal single connection, `session_max=1`, exhausting sessions to produce `out of sessions`, `create,exclusive` followed by exclusive reopen failure, and opening the same home with `create` while another connection manages it.

State, persistence, and dependencies: state is a simple table in the WiredTiger home and one or two connection handles tracked by `close_conn()`. Dependencies are `wiredtiger`, `wttest`, session open/close, table creation, and cursor iteration.

Integration points: targets connection lifecycle management, session pool limits, exclusive home locking/metadata rules, and duplicate-open protection.

Risks and test signals: the session exhaustion test is skipped for tiered storage. Some tests intentionally leave the primary connection open to validate management conflicts. Pass signals are precise errors for too many sessions, existing database with exclusive open, and already-managed homes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config06.py

Purpose: validates `session.create` format configuration edge cases for key/value formats and disaggregated storage-tier restrictions.

Important APIs and control flow: `bad_session_config()` asserts invalid create configs. Tests reject unsupported `A` formats and zero-length string formats, then `format_string()` creates fixed-length `S`/`s` key/value formats of lengths 1, 4, and 10, inserts longer strings, and verifies truncation behavior. Default `S` and `s` behavior is checked separately. One test asserts ASC rejects `disaggregated=(storage_tier=cold)` outside the disagg hook.

State, persistence, and dependencies: each success path creates a single table and stores one key/value pair. Dependencies include `wiredtiger`, `wttest`, cursor indexing, and hook decorators.

Integration points: covers create-time format parsing, string truncation semantics, and disaggregated configuration validation.

Risks and test signals: fixed-length byte/string semantics differ between `S` and `s`, and Python string handling can hide truncation mistakes. Pass signals are invalid argument errors for bad formats and exact truncated values for valid fixed-length formats.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config07.py

Purpose: tests documented log file preallocation/extend sizing through the `file_extend` configuration.

Important APIs and control flow: scenarios vary `file_extend=(log=...)` across defaults, disabled preallocation, valid sizes, invalid too-small/too-large values, sizes above log file max, and mixed data/log extend config. The test closes the default connection, opens with logging and `file_max=1M`, rejects invalid extend sizes, otherwise populates 5000 records, checkpoints, and polls for a `*Prep*` preallocation file with the expected size.

State, persistence, and dependencies: persistent artifacts are log files and preallocated prep files in the home. Dependencies are `fnmatch`, `os.stat`, time polling, log manager preallocation, and WiredTiger checkpoint/log write paths.

Integration points: covers connection config parsing, logging, file extension/preallocation, and checkpoint-induced log activity.

Risks and test signals: timing-sensitive polling can fail on very slow systems, and filesystem allocation behavior may vary. The strongest signal is exact prep file size or correct invalid-config error.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config09.py

Purpose: tests hash bucket configuration and checkpoint dirty-handle skipping statistics.

Important APIs and control flow: `conn_config` sets `hash=(buckets=256,dhandle_buckets=1024),statistics=(fast)`. Helpers create 50 small tables, update half of them, checkpoint, and read connection stats. `test_config09_invalid()` rejects non-power-of-two bucket values. `test_config09()` verifies configured bucket stats, then asserts checkpoint applied handles are around half the table count, skipped handles are nonzero, and selected per-checkpoint stats reset rather than accumulate.

State, persistence, and dependencies: persistent state is many small tables with checkpointed clean/dirty states. Dependencies are `wiredtiger.stat`, statistics cursors, checkpoint internals, and hash configuration parsing. Tiered storage is skipped.

Integration points: exercises dhandle hash sizing and checkpoint optimization that avoids clean handles.

Risks and test signals: internal tables make exact counts impossible, so the test uses ranges. Failures point to hash validation, stats publication, dirty-table detection, or stat reset regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config10.py

Purpose: validates startup behavior when the `WiredTiger` version file is missing or empty, with and without salvage.

Important APIs and control flow: tests close the default connection, remove or truncate the `WiredTiger` file, and either expect a corruption/salvage-needed error, expect a stdout warning for an empty file, or reopen with `salvage=true` and assert the file is repopulated.

State, persistence, and dependencies: the central persistent object is the WiredTiger version file in the home. Dependencies are `os.remove`, `os.stat`, `wiredtiger_open`, `setUpConnectionOpen`, stdout pattern capture, and salvage startup logic.

Integration points: targets database-home bootstrap, version-file validation, corruption reporting, and salvage recovery path.

Risks and test signals: error text and stdout wording are part of the test surface. Pass signals are correct refusal of missing file without salvage, warning/recovery for empty file, and non-empty recreated version file with salvage.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config11.py

Purpose: tests session debug reconfiguration `debug=(release_evict_page=true)`, which evicts pages as they are released.

Important APIs and control flow: scenarios cover record-number and integer-row keys. The test creates an unlogged table, measures max cache size, inserts enough 4KB-ish values through a snapshot-isolation session to reach roughly 75% cache use, checkpoints to clean pages, reads all content without debug eviction and verifies cache stays high, then reconfigures the session and rereads to assert cache usage drops by more than half.

State, persistence, and dependencies: state includes many clean pages in cache and connection cache statistics. Dependencies are `SimpleDataSet`, `wiredtiger.stat`, `session.reconfigure`, snapshot transactions, and cache/eviction behavior.

Integration points: covers runtime session reconfiguration and debug eviction code paths that operate after page release.

Risks and test signals: cache-size thresholds are workload and eviction sensitive. The pass signal is relative cache usage before/after debug reconfiguration while all values remain readable.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config12.py

Purpose: tests verbose configuration validation warnings emitted under `debug_mode=(configuration=true)`.

Important APIs and control flow: `expect_verbose()` is a context manager that clears stdout, opens a connection with a config, yields it, reads stdout, splits verbose messages, and regex-matches each line against expected patterns. Tests verify default warnings, dirty target over target, dirty trigger over trigger, and updates trigger over eviction trigger, with parallel checks that `debug_mode=(configuration=false)` emits no warnings.

State, persistence, and dependencies: state is mostly stdout capture and transient connection handles; the test does not need durable data. Dependencies include regex matching, `wttest` stdout helpers, connection open/close, and configuration normalization/warning logic.

Integration points: validates diagnostic behavior, not just config acceptance. It covers automatic adjustment warnings for eviction-related settings.

Risks and test signals: warning text changes can break regexes; output truncation is handled by dropping a partial last line. Pass signals are warnings only when debug configuration validation is enabled and each message matching an expected category.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config12.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config13.py

Purpose: asserts that fixed-length column-store tables are rejected because FLCS is no longer supported.

Important APIs and control flow: `test_create_flcs()` attempts `session.create('table:flcs', 'value_format=8t,key_format=r')` and expects `WiredTigerError` with a fixed-length column-store deprecation message.

State, persistence, and dependencies: no table should be persisted on success because creation fails. Dependencies are the WiredTiger Python API, `wttest`, and create-time format validation.

Integration points: guards the public `session.create` API against accidentally re-enabling `8t` FLCS table creation.

Risks and test signals: this is intentionally narrow and message-sensitive. A pass is the exact rejection path; a failure would indicate either changed error text or unsupported FLCS creation becoming possible.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config13.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_corrupt01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_corrupt01.py

Purpose: verifies diagnostic output when a block is corrupted, expecting block byte dumps and checkpoint extent-list context.

Important APIs and control flow: the test creates a small-page table, inserts 10000 randomly sized values, checkpoints, removes even keys to create holes, checkpoints again, closes, runs `wt verify -d dump_address` into a file, parses a row-store leaf address, overwrites that offset with `BAD_VALUE`, reopens, reads until corruption is encountered, and finally expects close to raise. It ignores expected extent-list/checksum noise.

State, persistence, and dependencies: persistent state is deliberately corrupted `.wt` file bytes and verify dump output. Dependencies include random data generation, regex address parsing, `suite_subprocess.runWt`, binary file writes, verify/read paths, and `debug_mode=(corruption_abort=false)`.

Integration points: covers block manager verification, corruption detection, verbose diagnostic plumbing, and close-time handling after corruption.

Risks and test signals: address parsing depends on dump format, and direct byte corruption is storage-layout sensitive. Disaggregated storage is skipped. Pass signals are successful corruption injection and expected `WiredTigerError` while diagnostics contain tolerated patterns.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_corrupt01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cross_checkpoint_caching.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cross_checkpoint_caching.py

Purpose: tests disaggregated follower cross-checkpoint disk-image caching: unchanged pages should hit cache when scanning a later checkpoint.

Important APIs and control flow: the class is decorated with `disagg_test_class` and scenario-generated disaggregated storage. The leader creates a layered table with tiny page sizes, the follower opens the same object, the leader inserts 5000 rows and checkpoints, the follower advances and scans while measuring shared-disk miss/hit deltas, then the leader updates one row, checkpoints, and the follower scans again. The second scan must have misses for rewritten pages and hits for unchanged pages, with `second_hit == first_miss - second_miss`.

State, persistence, and dependencies: state spans leader/follower homes, disaggregated storage checkpoints, shared disk-image cache stats, and layered table pages. Dependencies are `helper_disagg`, `wiredtiger.stat`, and checkpoint advancement.

Integration points: targets disaggregated storage, follower checkpoint visibility, page-image cache accounting, and layered cursors.

Risks and test signals: page-size choices are tuned to avoid splits and preserve predictable rewritten paths. Failures indicate cache accounting, checkpoint advancement, or disaggregated page identity regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cross_checkpoint_caching.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor01.py

Purpose: basic smoke test for file/table cursors over row and column stores, including key/value state, forward/backward iteration, cursor duplication, and comparison.

Important APIs and control flow: scenarios cover `file:`/`table:` plus row/string and column/record-number formats. Helpers create and populate 10 records, assert unpositioned cursors have no key/value, iterate with `next()` or `prev()`, check `WT_NOTFOUND` at endpoints, duplicate positioned cursors via `open_cursor(None, cursor, None)`, and compare duplicate positions.

State, persistence, and dependencies: persistent state is a small object populated through cursor assignment. Dependencies are `wiredtiger`, `wttest`, `make_scenarios`, cursor URI exposure, `recno()`, and duplicate-cursor support. Layered/disagg hooks skip duplicate assertions.

Integration points: covers core WT_CURSOR positioning, `get_key`, `get_value`, endpoint reset semantics, duplication, and comparison for access methods.

Risks and test signals: duplicate support differs for layered tables. Pass signals are exact key/value order, no stale key/value after reset/endpoints, and equal duplicate cursor positions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor02.py

Purpose: uses `TestCursorTracker` to validate cursor insert/remove/iteration behavior on small row and column tables.

Important APIs and control flow: `create_session_and_cursor()` creates a table with row or record-number keys, seeds tracker state via `cur_initial_conditions`, and opens with `append`. Tests delete multiple adjacent positions, insert records around a position, move forward/backward, and exercise empty and one-record tables. Tracker helpers perform expected-position and content checks.

State, persistence, and dependencies: state is both persistent table content and the base tracker model of expected keys/values. Dependencies include `TestCursorTracker`, `wiredtiger.WT_NOTFOUND`, `make_scenarios`, and cursor append mode.

Integration points: covers cursor state transitions after remove/insert, boundary movement, empty table iteration, and both row and column access methods.

Risks and test signals: much behavior is hidden in the tracker base class; local failures may be caused by model drift. Pass signals are tracker-confirmed contents and correct `WT_NOTFOUND` at first/last on empty inputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor03.py

Purpose: extends cursor insert/remove/iteration testing to larger tables and varied key/value sizes.

Important APIs and control flow: inherits `TestCursorTracker`, with scenarios for row/column tables, 1000/10000 entries, and large value or key/value sizes up to 10000 bytes. It creates the table with scenario formats, seeds tracker state, opens with append, then runs multiple-remove and insert/remove sequences similar to cursor02 across larger data.

State, persistence, and dependencies: persistent state may include large keys and values, stressing page layout and cursor movement. Dependencies are `TestCursorTracker`, `make_scenarios`, inherited `config_string`, and WT cursor append/iteration APIs.

Integration points: covers access-method behavior under larger payloads and cardinalities, including insert ordering and removal navigation.

Risks and test signals: large scenarios increase runtime and cache/page pressure. Pass signals are tracker-valid forward/backward order and consistency after repeated modifications across both small and large records.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor04.py

Purpose: tests `search` and `search_near` semantics for row and column tables, including deleted keys and endpoint behavior.

Important APIs and control flow: creates 20 records with row or record-number keys, verifies direct cursor indexing for an existing key and `KeyError` for a missing key, checks `search_near` beyond the end returns the previous key, checks exact matches return 0, deletes keys 0, 5, 9, and 10, then verifies `search_near` around deleted positions returns valid neighboring keys using `expect_either()`.

State, persistence, and dependencies: state is a small table with selected tombstones. Dependencies are `wiredtiger`, `wttest`, `make_scenarios`, cursor `set_key`, `search_near`, `remove`, and record-number conversion.

Integration points: covers search positioning and compare-return semantics after deletions across row and column access methods.

Risks and test signals: `search_near` may legally choose either neighbor for gaps, so the test accepts both. Failures show incorrect boundary positioning, deleted-key visibility, or compare code handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor05.py

Purpose: validates cursor uninitialized/end-position behavior and iteration over tables with optional column groups.

Important APIs and control flow: scenarios cover row versus column keys, empty versus three-entry tables, and no/two/four column groups. The test builds a table with composite columns, creates colgroups when configured, populates rows, and calls `check_entries()` for forward and backward scans after initial unpositioned state, after next/prev endpoint round-trips, after reset, and after completed iteration.

State, persistence, and dependencies: persistent state includes main table rows and optional colgroup objects. Dependencies are `wttest`, `make_scenarios`, cursor tuple key/value APIs (`get_keys`, `get_values`), and column-group projection.

Integration points: covers cursor reset/uninitialized state, endpoint movement, full scans, composite row/table schemas, and colgroup-backed reads.

Risks and test signals: column and row cursors expose different key shapes, increasing assertion complexity. Pass signals are stable forward/backward ordering and no stale position after reset or endpoint traversal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor06.py

Purpose: tests runtime cursor `reconfigure()` for `overwrite` and read-only behavior across file/table, row/column, and complex datasets.

Important APIs and control flow: scenarios combine URI type, key/value format, and `SimpleDataSet` or `ComplexDataSet`. `test_reconfigure_overwrite()` repeatedly toggles `overwrite=0` and `overwrite=1`, asserting duplicate insert failure then success. `test_reconfigure_readonly()` verifies updates fail for cursors opened read-only and succeed otherwise. `test_reconfigure_invalid()` checks invalid reconfiguration keys produce `Invalid argument`.

State, persistence, and dependencies: persistent state is populated dataset content reused under different cursor configs. Dependencies are `wiredtiger`, datasets, `dropUntilSuccess`, cursor `reconfigure`, and hook skips for timestamp.

Integration points: covers cursor-level configuration mutability after open and its interaction with insert/update semantics.

Risks and test signals: dropping/recreating objects across scenarios must avoid stale handles. Pass signals are duplicate-key enforcement under overwrite false, write rejection under read-only, and invalid config rejection.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor07.py

Purpose: validates log cursor visibility for logged versus non-logged tables, including records in mixed transactions and after reopen.

Important APIs and control flow: logging is enabled with small log files and dsync. The test creates one logged table and two non-logged tables, writes 7000 binary values to the logged table and one non-logged table in the same transaction, writes the other non-logged table in a separate transaction, optionally reopens, scans `log:` cursor records, and counts only log values containing the logged-table binary payload.

State, persistence, and dependencies: state includes log files, table data, and optional recovery/reopen. Dependencies are `suite_subprocess`, `make_scenarios`, `open_cursor('log:')`, transaction APIs, and binary value handling.

Integration points: covers log cursor decoding, logging disabled per table, transaction log records across file boundaries, and recovery persistence.

Risks and test signals: the test assumes payload matching is unique enough to identify logged table records. Pass signal is exactly `nkeys` logged values and no contamination from non-logged tables.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor08.py

Purpose: tests log cursors when the log itself uses compression.

Important APIs and control flow: scenarios combine reopen/no-reopen with log compressors `nop`, `snappy`, `zlib`, and `none`. `conn_config()` enables compressed logging and dsync; `conn_extensions()` loads the compressor when needed. The test writes 500 string values containing control characters in one transaction, optionally reopens, scans `log:`, and counts log records whose value bytes contain the encoded payload.

State, persistence, and dependencies: persistent state is compressed log records and a table. Dependencies are compressor extension loading, log cursor record layout, transaction sync, and Python string-to-byte encoding.

Integration points: covers log compression/decompression visibility through the public log cursor interface.

Risks and test signals: missing compressor extensions skip scenarios. Pass signal is exact recovery of all expected values through log cursor after optional reopen.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor09.py

Purpose: regression test for WT-2217: `WT_CURSOR.insert` should not leave the cursor positioned with key/value set.

Important APIs and control flow: scenarios cover file/table, row/column, and complex datasets. The test populates 100 records, opens a cursor, assigns `cursor[ds.key(10)] = ds.value(10)` to perform an insert/update operation, then immediately calls `cursor.search()` without resetting a key and expects a `requires key be set` error.

State, persistence, and dependencies: state is a populated dataset and cursor key/value flags after insert. Dependencies include `SimpleDataSet`, `ComplexDataSet`, `wiredtiger`, and error-message assertions.

Integration points: targets cursor internal state cleanup after insert across access methods and complex table layouts.

Risks and test signals: this is narrow but important for API consistency. A pass means insert clears the required key state; a failure indicates stale key positioning or incorrect API state tracking.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor11.py

Purpose: tests cursor key/value/position state after remove and insert operations.

Important APIs and control flow: scenarios cover integer, record-number, and string keys over file, simple table, index table, and complex table datasets. Tests remove using a positioned cursor, remove without position, remove by setting a key after having a position, and insert a new key. They assert which state remains: positioned remove keeps key/position but value is unavailable, while unpositioned remove, keyed remove, and insert leave no usable key/value/position and next iteration starts correctly.

State, persistence, and dependencies: state is dataset content plus cursor internal key/value/position flags. Dependencies are dataset helpers, `make_scenarios`, `wiredtiger` exceptions, and cursor navigation APIs.

Integration points: covers WT_CURSOR post-operation contract, including indexes and complex tables.

Risks and test signals: expectations differ subtly by operation path. Pass signals are correct errors for unavailable key/value and successful subsequent iteration from expected records.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor12.py

Purpose: comprehensive smoke and recovery test for the `WT_CURSOR.modify` API over string and byte-array values.

Important APIs and control flow: scenario matrix covers file/table, record-number/string keys, and `S`/`u` values. A large modification table describes no-ops, replacement, growth, shrink, discard, gaps, overlap, and many modifications. Helpers convert bytes, build `wiredtiger.Modify` records, apply mods inside snapshot transactions, and confirm final values. Tests also reject modify under read-uncommitted/read-committed, verify persistence after reopen and crash-copy recovery, stress 50000 modifications to one value, and verify not-found behavior after delete or aborted/uncommitted insert.

State, persistence, and dependencies: state includes update chains, logged recovery copies, checkpointed pages, and value-format-specific bytes/strings. Dependencies are `copy_wiredtiger_home`, `SimpleDataSet`, random/string, and transaction isolation.

Integration points: covers modify API semantics, reconciliation, recovery, rollback visibility, and Python binding type conversion.

Risks and test signals: byte/string conversion and null padding are easy to regress. Pass signals are exact final values across in-memory, reopened, and recovered states plus correct WT_NOTFOUND/error behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor12.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor13.py

Purpose: large cursor-cache test suite covering cursor caching/reopen stats, inherited cursor workloads, verify/drop interactions, sweep behavior, and duplicate cursors.

Important APIs and control flow: `test_cursor13_base` reads cursor cache/reopen/sweep stats while filtering history-store noise and provides assertions around stat deltas. Several classes inherit existing cursor and checkpoint tests to run them with cache stats. `test_cursor13_reopens` toggles connection/session cache-cursor config and validates reopen/cache counts through repeated opens, dataset checks, reconfigure, and verify. Drop tests ensure cached cursors do not prevent drops once closed but open cursors do. Big/sweep tests create many URIs and randomly open/close hundreds of thousands of cursors, asserting cache/reopen and sweep stats. `cursor13_dup` duplicates positioned cursors repeatedly.

State, persistence, and dependencies: state spans cursor cache lists, dhandles, session config, stats, many table/file objects, and optional time-based sweeps. Dependencies include other test modules, `wiredtiger.stat`, datasets, random helper, and hook skips.

Integration points: covers cursor caching, data-handle lifecycle, verify/drop compatibility, session reconfigure, and stats accounting.

Risks and test signals: long-running and timing-sensitive sweep assertions can be noisy. Pass signals are expected stat deltas, successful drops after cached cursors, and no stale dhandle/cursor reuse failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor13.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor14.py

Purpose: stress-tests opening more than 64K cursors on a single data source.

Important APIs and control flow: scenarios cover file/table, row/record-number keys, and simple/complex datasets. The test populates 100 records, then loops 66000 times opening a cursor on the same URI without retaining or explicitly closing each handle.

State, persistence, and dependencies: persistent state is the populated dataset; transient state is a very large sequence of cursor opens in one session. Dependencies are `SimpleDataSet`, `ComplexDataSet`, `make_scenarios`, and cursor allocation internals.

Integration points: targets cursor id/handle limits and session cursor allocation paths beyond 16-bit thresholds.

Risks and test signals: because cursors are not stored, Python lifetime/garbage collection may affect actual simultaneous open count. A pass is no exception during the 66000 opens; failure would suggest cursor id overflow, resource leak, or allocation limit regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor14.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor15.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor15.py

Purpose: smoke-tests the cursor `read_once=true` configuration under small-cache table scans and cursor caching.

Important APIs and control flow: with `cache_size=1M`, the test creates a table tuned to roughly one 100KB page per document, inserts 20 large records, reopens to clear cache, then scans the table once with `read_once=true` and once with default cursor config without restarting between scans.

State, persistence, and dependencies: persistent state is 2MB of table data; transient state is cache pressure from scanning pages larger than cache capacity. Dependencies are `wttest`, table page-size config, cursor open config, and full-table iteration.

Integration points: covers `WT_READ_WONT_NEED`-style cursor behavior and compatibility with cursor caching/reuse.

Risks and test signals: there is no statistic assertion, so this is mainly a crash/regression smoke test. Pass signal is successful scans with and without `read_once` under constrained cache.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor15.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor16.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor16.py

Purpose: ensures final session close releases cached cursors and leaves zero cached cursor count.

Important APIs and control flow: connection enables cursor caching, fast stats, and in-memory mode. For 100 URIs, the main session creates tables and holds one open cursor per URI. Then 100 additional sessions each open/read/close a cursor for every URI, populating per-session cursor caches. Closing all auxiliary sessions should drain cached cursors; the test asserts `cursor_cached_count` is 0 before and after.

State, persistence, and dependencies: state is in-memory table data, many sessions, held dhandle references, and cursor cache statistics. Dependencies are `wiredtiger.stat`, session open/close, and key-format scenarios for row/var.

Integration points: covers cursor cache cleanup during session close and protection against swept dhandles while main cursors are open.

Risks and test signals: large session*URI count can be resource-heavy. Pass signal is exact zero cached cursor count after closing all sessions, indicating no final-close leak.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor16.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor17.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor17.py

Purpose: tests the `cursor.largest_key()` interface under deletes, timestamps, prepared updates, truncation, empty tables, and cursor positioning.

Important APIs and control flow: scenarios cover file/table row and variable-length column stores plus a complex table case. Helpers populate datasets. Tests delete the largest key and observe globally deleted behavior before/after eviction, insert uncommitted/aborted/timestamp-invisible/prepared larger keys and check `largest_key`, verify `largest_key` sets key but not value, check empty-table `WT_NOTFOUND`, and test fast/slow truncate interactions with timestamps.

State, persistence, and dependencies: state includes update chains, tombstones, evicted pages, timestamps, prepared transactions, and truncate records. Dependencies are datasets, `wiredtiger`, `timestamp_str`, `debug=(release_evict)`, and transaction APIs.

Integration points: covers largest-key calculation across memory, disk, visibility rules, and access methods.

Risks and test signals: several expectations intentionally expose physical largest keys even when logically invisible, so semantics are subtle. Hook skips prevent timestamp interference. Pass signals are exact returned keys and `WT_NOTFOUND` for empty data.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor17.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor18.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor18.py

Purpose: exhaustive version-cursor test for full updates, tombstones, history-store records, prepared updates, visibility filtering, cross-key iteration, and start-timestamp filtering.

Important APIs and control flow: row and variable column scenarios run with default and `cross_key=true` version cursor config. Helpers create a file, open `debug=(dump_version=(...))` cursors, and verify timestamp/type/prepare/flags/location/value fields. Tests cover in-memory update chains, on-disk pages after `debug=(release_evict)`, deletion combinations, history-store placement, multiple keys, cursor reuse, prepared full values and tombstones, visible-only skipping of invisible/prepared records, unpositioned iteration, concurrent inserts during traversal, and inclusive/exclusive start timestamp behavior.

State, persistence, and dependencies: state spans update chains, disk images, history store, timestamps, prepared transactions, tombstones, and version cursor internal scan state. Dependencies are `wiredtiger`, `wttest`, statically known value-field layout, and WT timestamp helpers.

Integration points: targets debug dump-version cursor semantics and history-store visibility across access methods.

Risks and test signals: expected numeric fields are tightly coupled to internal version-cursor encoding. Pass signals are exact field tuples, correct `WT_NOTFOUND`, and enforced cross-key/positioning rules.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor18.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor19.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor19.py

Purpose: tests version cursor output for `WT_CURSOR.modify` update chains.

Important APIs and control flow: row and variable-column scenarios create a file with string values. The test inserts an initial 100-character value at timestamp 1, applies several single-byte `wiredtiger.Modify` operations at timestamps 5, 10, and 15, evicts to force some versions to disk/history store, applies more modifies at timestamps 20 and 25, deletes at timestamp 30, then opens `debug=(dump_version=(enabled=true))` and verifies each version in descending order.

State, persistence, and dependencies: state includes modify deltas, full materialized values, history-store/on-disk locations, and a final tombstone. Dependencies are `wiredtiger.Modify`, timestamp commits, eviction cursor, and version cursor value-field layout.

Integration points: covers interaction between modify records, reconciliation/history store, and debug version cursor reporting.

Risks and test signals: expected `type` and `location` values are internal and can shift if version cursor schema changes. Pass signal is exact sequence of values and timestamps from newest to oldest ending in `WT_NOTFOUND`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor19.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor20.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor20.py

Purpose: tests duplicate-key error behavior and value state after inserting with `overwrite=false`.

Important APIs and control flow: scenarios cover row-string and variable-column keys, with in-memory and reopen/on-disk variants. The test populates a 100-row `SimpleDataSet`, optionally reopens, opens a cursor with `overwrite=false`, sets an existing key with a different value, asserts insert raises `WT_DUPLICATE_KEY`, and then asserts `get_value()` returns the existing stored value.

State, persistence, and dependencies: state is a populated table either in cache or read after reopen. Dependencies are `SimpleDataSet`, `suite_subprocess`, `wiredtiger`, cursor overwrite config, and duplicate-key error matching.

Integration points: covers insert duplicate handling and cursor value replacement semantics after failed insert across memory/disk.

Risks and test signals: semantics are subtle: after duplicate failure, cursor value should reflect the existing record, not the attempted value. Pass signal is duplicate error plus exact existing value.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor20.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor21.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor21.py

Purpose: tests cursor reposition support and statistics under forced eviction/reposition stress.

Important APIs and control flow: scenarios cover column and integer-row formats with reposition debug mode enabled or disabled. `conn_config()` enables all stats and optionally `debug_mode=[cursor_reposition=true],timing_stress_for_test=(evict_reposition)`. The test inserts 9999 integer values, then in separate transactions scans with `next`, `prev`, `search`, and `search_near`, checking each value and reading `stat.conn.cursor_reposition` between phases. Reposition scenarios require the stat to increase; non-reposition scenarios require zero.

State, persistence, and dependencies: state includes table records, cursor position restoration after eviction stress, and connection statistics. Dependencies are `wiredtiger.stat`, transaction APIs, cursor navigation/search APIs, and timing stress configuration.

Integration points: covers cursor repositioning machinery during forward/backward/search traversal for row and column stores.

Risks and test signals: the test relies on stress hooks to trigger reposition consistently. Pass signals are correct values throughout traversal and reposition stat behavior matching the scenario.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor21.py -->
