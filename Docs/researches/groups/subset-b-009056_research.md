# subset-b-009056 Research

Grouped source research for WiredTiger checkpoint workers, compatibility tests, and cppsuite harness files. Each section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/checkpoint/workers.c -->
# sources/storage-engines/wiredtiger/test/checkpoint/workers.c

Purpose: Implements the worker side of the checkpoint stress test: table creation, worker-thread startup, random transactional updates across all configured tables, and timestamp/prepared-transaction behavior used by compatibility and recovery validation.

Important APIs/types/functions: `start_workers` initializes modify replacement data, creates tables via `create_table`, starts `g.nworkers` threads, and joins them. `worker` is the thread entry point, while `real_worker` owns the session, cursor array, transaction loop, timestamp handling, and cursor reopen behavior. `worker_op`, `worker_no_ts_delete`, and `modify_build` encapsulate per-key data operations.

Control flow: tables are created before worker launch; each worker opens a snapshot-isolation session and one cursor per table, then loops until `g.opts.running` is false or `g.nops` is reached unless a stop timestamp is configured. Each iteration picks a key in the thread's key range, optionally performs a no-timestamp delete transaction, performs the same logical operation on every table, and periodically commits or rolls back. Timestamp mode may use global clock locking or deterministic reserved timestamps for predictable replay; prepared transactions get prepare/durable/commit or rollback timestamps.

State and persistence: creates WiredTiger tables using row or column key format, optionally disabling logging for timestamped tests and using disaggregated layered tables. Persistent table data is intentionally stressed through inserts, modifies, range removes, checkpoints, rollbacks, prepared transactions, and cursor reopen paths. Global state comes from `g`, including timestamp locks, stable timestamp, operation count, table cookies, and worker thread data.

Dependencies/integration: depends on `test_checkpoint.h`, WiredTiger sessions/cursors, `test_util`, WT thread helpers, and global checkpoint-test options. The compatibility release script invokes the checkpoint binary to generate and verify data across branches.

Risks and test signals: key risks are timestamp-ordering bugs, inconsistent cross-table transactions, missed `WT_ROLLBACK`/`WT_PREPARE_CONFLICT` handling, cursor state bugs after range removes, and unsafe interaction with oldest/stable movement. Progress prints, fatal `testutil_check` assertions, verification mode in the checkpoint binary, and cross-version compatibility runs are the primary signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/checkpoint/workers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/compatibility/common/compatibility_common.py -->
# sources/storage-engines/wiredtiger/test/compatibility/common/compatibility_common.py

Purpose: Provides common path, clone, build, and subprocess helpers for the Python compatibility suite.

Important APIs/types/functions: `branch_path` resolves either `this` or a checked-out branch under `COMPATIBILITY_TEST`; `branch_build_path` derives a deterministic build directory and appends sanitized build-config keys; `system` raises on nonzero shell command exit; `prepare_branch` clones/pulls a branch, validates supported build config keys, copies current `CMakePresets.json`, selects `linux-gcc` or `linux-v4-gcc`, configures CMake/Ninja, and builds.

Control flow: module import establishes `TEST_DIR`, `DIST_TOP_DIR`, and Python/third-party paths without importing `wiredtiger`. `prepare_branch` optionally clones, interprets `standalone`, creates a build directory if no Ninja build exists, then runs `ninja` every time.

State and persistence: persistent state is the branch checkout and build tree on disk. Build directory names encode configuration, avoiding collisions between standalone and non-standalone builds.

Dependencies/integration: imports branch metadata from `compatibility_config`, uses `test_util.setup_3rdparty_paths`, shells out to `git`, `cmake`, and `ninja`, and is called by `compatibility_test.prepare_tests`.

Risks and test signals: shell-string command construction requires sanitized build config values and quoted paths; only CMake-era branches are supported here. Failures surface as raised exceptions from `system` or unsupported config keys, before compatibility tests run.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/compatibility/common/compatibility_common.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/compatibility/common/compatibility_config.py -->
# sources/storage-engines/wiredtiger/test/compatibility/common/compatibility_config.py

Purpose: Centralizes branch lists and checkout-directory configuration for Python compatibility tests, importing branch policy from the shell `meta/versions.sh` file.

Important APIs/types/functions: `WTBranches` holds `SUITE_RELEASE_BRANCHES` as `WTVersion` objects. `extract_versions` reads `versions.sh`, regexes `export SUITE_RELEASE_BRANCHES="..."`, removes line continuations, splits branches, constructs `WTVersion` instances, filters invalid entries, and raises if no expected variable is found. `__bool__` validates that a usable suite branch list exists.

Control flow: at import time, `META_DIR` is derived beside the file, `BRANCHES` is populated from `versions.sh`, and `BRANCHES_DIR` is set to `COMPATIBILITY_TEST`.

State and persistence: no runtime persistence; the file maps durable branch policy in `versions.sh` into Python objects.

Dependencies/integration: depends on `compatibility_version.WTVersion` for validation/ordering and is consumed by `compatibility_common` and `compatibility_test`.

Risks and test signals: the regex is tied to exported shell variable shape and currently reads only `SUITE_RELEASE_BRANCHES`. Bad branch strings are silently filtered, but an entirely missing/empty suite list raises. Any new version-list variable needed by Python tests must be explicitly added here.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/compatibility/common/compatibility_config.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/compatibility/common/compatibility_version.py -->
# sources/storage-engines/wiredtiger/test/compatibility/common/compatibility_version.py

Purpose: Defines a comparable branch/version object for compatibility scenario generation.

Important APIs/types/functions: `WTVersion.__init__` recognizes `this`, `develop`, and exact `mongodb-X.Y` branch names. Rich comparison methods order versions by group and numeric major/minor, with `this` higher than `develop`, and `develop` higher than numbered branches. `__bool__`, `__eq__`, `__hash__`, and `__str__` support filtering, set membership, and display.

Control flow: construction parses and records validity; comparisons are pure value comparisons. String equality is supported in `__eq__` to simplify membership checks.

State and persistence: instances persist branch name, validity, group, major, and minor in memory only.

Dependencies/integration: used by `compatibility_config`, scenario generation, and tests that define version boundaries such as FLCS or chunk-cache deprecation.

Risks and test signals: `this` is marked valid only briefly before the `else` tied to `develop` can invalidate it, so the intended `this > develop > mongodb-*` behavior should be tested carefully. Invalid versions are falsey and can be filtered away without an explicit diagnostic.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/compatibility/common/compatibility_version.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/compatibility/compatibility_test_for_releases.sh -->
# sources/storage-engines/wiredtiger/test/compatibility/compatibility_test_for_releases.sh

Purpose: Legacy shell orchestrator for WiredTiger release compatibility testing across branch pairs, including import compatibility, format verification, checkpoint verification, patch-version upgrade/downgrade, dirty restart, standalone release, and pair-coverage self-test modes.

Important APIs/types/functions: version helpers parse `mongodb-X.Y`; `build_branch` clones/checks out a branch/tag, chooses CMake or autoconf, applies toolchain/preset choices, and builds required artifacts. `create_configs`, `run_format`, `run_test_checkpoint`, `verify_test_format`, `verify_test_checkpoint`, `upgrade_downgrade`, `test_dirty_restart`, `test_upgrade_to_branch`, and `import_compatibility_test` implement the main test phases. `generate_compat_pairs` builds policy-driven branch pairs and `run_pair_tests` validates invariants without builds.

Control flow: command-line flags select exactly one mode. The script creates `test-compatibility-run`, sources `meta/versions.sh`, builds relevant branches, creates format configs, generates data with format/checkpoint tests, verifies backward and forward compatibility, and optionally alternates format binaries for upgrade/downgrade. Newer-branch mode uses generated version-aware pairs for format and upgrade/downgrade, while checkpoint tests still walk the configured release chain.

State and persistence: creates clone/build directories named after branches or tags, per-branch format configs, `RUNDIR.*` homes, backups, imported files, and downloaded WT-8395 test data. It also mutates existing run directories during upgrade/downgrade and dirty restart tests.

Dependencies/integration: depends on git tags/branches, external GitHub clones, CMake/autoconf/make, Snappy/reverse-collator/rotn extensions, `wt`, `test/format`, and `test/checkpoint`. It shares release lists with Python compatibility via `meta/versions.sh`.

Risks and test signals: high-risk areas include branch-list drift, shell quoting/path assumptions, destructive cleanup of the run root, reliance on network and tags, and compatibility config keys that older branches reject. Success is signaled by all invoked build/test/verify commands completing under `set -e`; `-T` provides a cheap structural guard for pair generation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/compatibility/compatibility_test_for_releases.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/compatibility/meta/versions.sh -->
# sources/storage-engines/wiredtiger/test/compatibility/meta/versions.sh

Purpose: Single source of truth for release branch sets used by both shell and Python compatibility tests.

Important APIs/types/functions: exports `SUITE_RELEASE_BRANCHES`, `IMPORT_RELEASE_BRANCHES`, `NEWER_RELEASE_BRANCHES`, `PATCH_VERSION_UPGRADE_DOWNGRADE_RELEASE_BRANCHES`, `TEST_CHECKPOINT_RELEASE_BRANCHES`, and `UPGRADE_TO_LATEST_UPGRADE_DOWNGRADE_RELEASE_BRANCHES`.

Control flow: no execution beyond environment-variable exports. Maintainers add new branches to every relevant list in newer-to-older order and run the shell pair self-test after changing `NEWER_RELEASE_BRANCHES`.

State and persistence: persistent branch policy lives in the exported strings; consumers expand them into arrays or `WTVersion` objects.

Dependencies/integration: sourced by `compatibility_test_for_releases.sh` and parsed by `compatibility_config.py`.

Risks and test signals: missing a branch in one list can silently reduce coverage for a mode. Order matters for sequential checkpoint verification and upgrade paths. The `compatibility_test_for_releases.sh -T` self-test is the explicit signal for pair-policy validity.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/compatibility/meta/versions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/compatibility/suite/compatibility_test.py -->
# sources/storage-engines/wiredtiger/test/compatibility/suite/compatibility_test.py

Purpose: Python unittest harness for running compatibility test methods under different WiredTiger branch builds and Python bindings.

Important APIs/types/functions: `CompatibilityTestCase` extends the WiredTiger abstract test case. `run_method_on_branch` generates a temporary Python script that rewires `sys.path`, imports branch-specific `wiredtiger`, recreates class and instance state via pickle, calls `finishSetupIO`, and invokes a selected method in a subprocess. `assert_captured_output_contains` checks captured stdout/stderr files. `make_branch_scenarios`, `add_branch_pair_scenarios`, `global_setup`, `prepare_tests`, `run_tests`, and `run` prepare branches, build scenarios, and execute suites.

Control flow: global setup initializes test dirs, IO, random state, and current WiredTiger path. Preparation discovers required build configs, builds every suite branch/config combination, validates test-declared older/newer branch constraints, and combines branch-pair scenarios with any test-local scenarios. Each compatibility test then executes branch-specific phases in child interpreters.

State and persistence: creates per-test directories, temporary scripts under the test dir, branch build trees, captured output files, and serialized test attributes. Temporary scripts are removed only after successful subprocess execution.

Dependencies/integration: uses `compatibility_common`, `WTVersion`, `abstract_test_case`, `testtools`, `test_result`, `test_util`, `wtscenario`, branch-specific Python bindings, and Python `unittest`.

Risks and test signals: pickling test state can miss non-picklable or intentionally skipped attributes; subprocess failures leave scripts for diagnosis. Scenario validation catches unsupported branches early. Success is standard unittest success after all generated branch pairs pass.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/compatibility/suite/compatibility_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/compatibility/suite/test_chunkcache_deprecate.py -->
# sources/storage-engines/wiredtiger/test/compatibility/suite/test_chunkcache_deprecate.py

Purpose: Validates upgrade behavior when a database with chunk-cache configuration is opened on a branch where chunk cache is deprecated.

Important APIs/types/functions: `test_chunkcache_deprecate` gates execution by `WTVersion` boundaries. `on_older_branch` creates a database with `chunk_cache=(enabled=false,capacity=1GB)`, writes 100 rows, and closes it. `on_newer_branch_disabled` verifies open succeeds with a warning and data remains readable. `_set_basecfg_chunkcache_enabled` flips `WiredTiger.basecfg` between enabled/disabled. `on_newer_branch_enabled` and `chunk_cache_enabled_unsupported` expect clean `ENOTSUP`.

Control flow: older branches before chunk-cache introduction skip; deprecated branches directly test unsupported enabled config; crossing the deprecation boundary runs create, open-with-warning, mutate basecfg, then open-fails.

State and persistence: persists chunk-cache settings in `WiredTiger.basecfg` and table rows in the shared test home across branch-specific subprocesses.

Dependencies/integration: uses `CompatibilityTestCase.run_method_on_branch`, `WTVersion`, Python `wiredtiger`, `errno`, and captured-output checks.

Risks and test signals: exact warning/error text is part of the test signal, so message churn can fail tests. Manual basecfg replacement assumes a simple `enabled=` token. Data verification prevents false positives where open succeeds but upgraded contents are unusable.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/compatibility/suite/test_chunkcache_deprecate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/compatibility/suite/test_flcs_deprecate.py -->
# sources/storage-engines/wiredtiger/test/compatibility/suite/test_flcs_deprecate.py

Purpose: Tests fixed-length column-store deprecation across branch upgrades.

Important APIs/types/functions: `test_flcs_deprecate` compares branch pairs against `mongodb-8.3`. `flcs_table_creation_unsupported` expects FLCS table creation to raise `ENOTSUP` on deprecated branches. `on_older_branch` creates a `key_format=r,value_format=8t` table and populates rows. `on_newer_branch` expects opening the old FLCS database to fail with a panic signal.

Control flow: pairs already at or past the deprecation version test creation failure; pairs crossing from pre-deprecation to deprecated run older-branch creation then newer-branch open failure.

State and persistence: the FLCS table is persisted in the test home by the older branch and reopened by the newer branch.

Dependencies/integration: uses the compatibility subprocess harness, `WTVersion`, Python `wiredtiger`, and `errno`.

Risks and test signals: assertions compare exception strings using substring-style membership against `wiredtiger_strerror`, so exact error formatting matters. The expected newer open failure is severe (`WT_PANIC`), making the test sensitive to future deprecation semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/compatibility/suite/test_flcs_deprecate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/compatibility/suite/test_wt10533.py -->
# sources/storage-engines/wiredtiger/test/compatibility/suite/test_wt10533.py

Purpose: Regression test for checkpoint handling during downgrade when many checkpoints force monotonic checkpoint time far ahead of wallclock time.

Important APIs/types/functions: `test_checkpoint_downgrade` runs a newer-branch phase followed by an older-branch phase. `on_newer_branch_test_checkpoint_downgrade` creates a table, writes initial rows, and creates many checkpoints. `on_older_branch_test_checkpoint_downgrade` opens with compatibility/statistics config, starts a backup cursor, writes large batches across more checkpoints, copies backup files, reopens the backup, and verifies initial rows.

Control flow: newer branch creates the starting database and checkpoint history; older branch continues writing and checkpointing while a backup cursor is active, materializes a backup, and validates backup readability.

State and persistence: persists the database home, checkpoint metadata, statistics logs, backup directory, copied WiredTiger files, and table contents across branch-specific subprocesses.

Dependencies/integration: uses `CompatibilityTestCase`, Python `wiredtiger`, filesystem `os/shutil`, captured test output, and branch scenario generation.

Risks and test signals: large row/checkpoint counts make the test expensive but targeted. Backup copying assumes files returned by `backup:` are copyable by name from the current home. Data verification of the original rows is the final compatibility signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/compatibility/suite/test_wt10533.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/cppsuite/CMakeLists.txt

Purpose: Defines the cppsuite test harness static library and executable test targets.

Important APIs/types/functions: `add_library(cppsuite_test_harness STATIC ...)` compiles harness sources from bound, common, component, main, storage, and util directories. `create_test_executable` produces `run`, `test_live_restore`, `csuite_style_example_test`, and `test_disagg_failover_perf`. `add_test` registers ctest entries and labels smoke-test targets.

Control flow: the harness library is built first, gets the cppsuite include directory, compiler diagnostics, `test_util`, and `-DEXTSUBPATH=""`; executables link it. Antithesis builds additionally link `wt::voidstar`.

State and persistence: creates build artifacts and ctest metadata only.

Dependencies/integration: integrates cppsuite into the top-level CMake test framework and relies on `create_test_executable` from the parent build system.

Risks and test signals: every listed source must remain in sync with the harness source tree. `ctest -L cppsuite` or `ctest -R cppsuite` is the build/test signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/create_test.sh -->
# sources/storage-engines/wiredtiger/test/cppsuite/create_test.sh

Purpose: Scaffolds a new cppsuite test source, config file, run dispatch entries, and test-data metadata.

Important APIs/types/functions: validates the test name with `^[a-z][_a-z0-9]+$`, checks target files do not exist, copies `test_template.cpp` and `test_template_default.txt`, rewrites placeholder names with `sed`, inserts includes/dispatch/all-test entries into `tests/run.cpp`, adds metadata to `dist/test_data.py`, and runs `dist/s_all`.

Control flow: fails early for missing/invalid/existing inputs, performs text substitutions, updates multiple registry files, then runs formatting/regeneration.

State and persistence: creates `tests/<name>.cpp` and `configs/<name>_default.txt`; mutates `tests/run.cpp` and `dist/test_data.py`.

Dependencies/integration: depends on template files, GNU-style `sed -i`, and the `s_all` distribution script.

Risks and test signals: textual insertion anchors can break if templates or registry layout change. The script is intentionally mutating and should be run from the cppsuite directory. `s_all` success is the primary generated-code/test-data signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/create_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/bound/bound.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/bound/bound.cpp

Purpose: Implements a small value object for applying one WiredTiger cursor bound.

Important APIs/types/functions: constructors create an empty bound, explicit key/lower/inclusive bound, or random key bound with optional forced first character. `get_config` formats `bound=lower|upper,inclusive=true|false`; `get_key` and `get_inclusive` expose state; `apply` sets the cursor key and calls `cursor->bound`; `clear` resets to empty/default.

Control flow: random constructors use thread-local `random_generator`; `apply` is immediate and fatal on WT error via `testutil_check`.

State and persistence: holds `_key`, `_inclusive`, and `_lower_bound` in memory only. It changes cursor-bound state but does not persist data.

Dependencies/integration: depends on `bound.h`, `random_generator`, `constants`, `scoped_cursor`, and `test_util`.

Risks and test signals: random-key generation is nondeterministic unless higher-level tests seed behavior elsewhere. Applying an empty/default bound would set an empty key, so callers must construct meaningful bounds. Cursor-bound WT return codes are asserted.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/bound/bound.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/bound/bound.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/bound/bound.h

Purpose: Declares the cppsuite cursor-bound helper.

Important APIs/types/functions: `class bound` exposes constructors for explicit and random bounds, `get_config`, `get_key`, `get_inclusive`, `clear`, and `apply(scoped_cursor&)`.

Control flow: interface separates bound construction from cursor application, allowing tests to store and apply lower/upper bounds later.

State and persistence: private state is bound key string, inclusivity flag, and lower/upper flag. Persistence is limited to subsequent cursor behavior after `apply`.

Dependencies/integration: includes `src/storage/scoped_cursor.h`; used by `bound_set` and bound-related tests.

Risks and test signals: no validation in the declaration for key format or empty keys; correctness depends on implementation assertions and WT cursor-bound behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/bound/bound.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/bound/bound_set.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/bound/bound_set.cpp

Purpose: Implements paired lower/upper cursor bounds, including prefix-range construction.

Important APIs/types/functions: `bound_set(bound lower, bound upper)` stores a pair. `bound_set(const std::string &key)` creates an inclusive lower bound at `key` and an exclusive upper bound by incrementing the last byte of the key copy. `apply` applies both bounds to a cursor. Getters return references to lower and upper bounds.

Control flow: prefix constructor derives the upper bound eagerly; `apply` sets the key for each bound and calls `cursor->bound` twice with fatal checking.

State and persistence: keeps two in-memory `bound` objects and mutates cursor-bound state when applied.

Dependencies/integration: uses `bound`, `scoped_cursor`, and `test_util`; provides a convenience layer for prefix scans in tests.

Risks and test signals: prefix construction assumes a non-empty key and simple byte increment; overflow or collation-specific ordering can make the range wrong. WT cursor-bound errors are test failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/bound/bound_set.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/bound/bound_set.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/bound/bound_set.h

Purpose: Declares a helper for applying lower and upper cursor bounds together.

Important APIs/types/functions: `class bound_set` deletes the default constructor, accepts two `bound` objects or a prefix key, exposes `apply`, `get_lower`, and `get_upper`.

Control flow: callers construct a complete bound pair before application.

State and persistence: owns lower and upper `bound` objects; applying affects the target cursor's range state.

Dependencies/integration: includes `bound.h` and `scoped_cursor.h`; used by cppsuite tests that need bounded scans.

Risks and test signals: no API-level validation for lower/upper consistency. Tests must assert resulting scan contents, not just successful bound application.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/bound/bound_set.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/common/constants.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/common/constants.cpp

Purpose: Defines shared string constants for cppsuite component names, configuration keys, WiredTiger timestamp/config keys, and internal tracking table names.

Important APIs/types/functions: exports names such as `METRICS_MONITOR`, `OPERATION_TRACKER`, `TIMESTAMP_MANAGER`, config keys like `CACHE_SIZE_MB`, `OP_RATE`, `TRACKING_KEY_FORMAT`, timestamp keys like `commit_timestamp`, and table names `table:operation_tracking` and `table:schema_tracking`.

Control flow: no runtime logic; constants are initialized as static storage.

State and persistence: constants influence runtime configuration parsing and persistent table names but hold no mutable state.

Dependencies/integration: matches declarations in `constants.h` and is used throughout components, database setup, operation tracking, and metrics.

Risks and test signals: key-name drift breaks config parsing at runtime. Compile/link failures catch missing declarations; config tests catch semantic mismatches.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/common/constants.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/common/constants.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/common/constants.h

Purpose: Declares shared constants and preprocessor macros for cppsuite configuration and WiredTiger extension paths.

Important APIs/types/functions: declares component/config/timestamp constants, `DEFAULT_FRAMEWORK_SCHEMA`, statistics URI, tracking tables, and macros for Snappy compressor and reverse collator configuration/paths.

Control flow: header-only declarations and macros are consumed by many harness files during compilation.

State and persistence: macro values shape table creation configs and extension loading paths; tracking table constants define persistent metadata table names.

Dependencies/integration: imported by component, database, metrics, timestamp, and operation-tracking code; linked to definitions in `constants.cpp`.

Risks and test signals: `EXTSUBPATH` differs between CMake and autoconf layouts, so build definitions must match extension paths. Table/config key renames require synchronized defaults in test config metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/common/constants.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/common/logger.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/common/logger.cpp

Purpose: Implements synchronized cppsuite logging with timestamp, thread id, and log level.

Important APIs/types/functions: `get_time` formats UTC-like timestamp strings with nanosecond suffix from `high_resolution_clock`. `logger::log_msg` checks `trace_level`, validates level bounds, builds a message with TID and level, locks a static mutex, and writes errors to stderr and other levels to stdout.

Control flow: logging is skipped when requested level is above current `trace_level`. Message construction happens before acquiring the output lock; actual stream writes are serialized.

State and persistence: mutable static `logger::trace_level` and `logger::include_date`; no file persistence.

Dependencies/integration: depends on `test_util`, C++ streams, thread ids, and `LOG_LEVELS`; used across the harness for diagnostics.

Risks and test signals: per-line locking can be expensive at trace level. Timestamp uses localtime for calendar fields but appends `Z`, which can mislead interpretation. Assertions catch invalid trace levels and time formatting failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/common/logger.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/common/logger.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/common/logger.h

Purpose: Declares log-level constants and the non-instantiable `logger` utility.

Important APIs/types/functions: defines `LOG_ERROR`, `LOG_WARN`, `LOG_INFO`, and `LOG_TRACE`; declares `get_time`; exposes static `trace_level`, `include_date`, and `log_msg`.

Control flow: callers use numeric levels to gate messages through `logger::log_msg`.

State and persistence: static configuration controls global logging behavior during a process.

Dependencies/integration: included by components, thread manager, metrics, and database code.

Risks and test signals: changing level values requires updating the implementation's `LOG_LEVELS` array. Logging is a diagnostic signal, not a validation mechanism.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/common/logger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/common/random_generator.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/common/random_generator.cpp

Purpose: Implements thread-local random data generation for test keys, values, and choices.

Important APIs/types/functions: `instance` returns a `thread_local` singleton. `generate_random_string` repeats the chosen character set, shuffles, and truncates. `generate_pseudo_random_string` walks the character set from a random start for more-compressible output. `generate_bool`, `generate_integer`, `get_distribution`, and `get_characters` provide typed random helpers.

Control flow: constructors seed `std::mt19937` from `std::random_device`; invalid `characters_type` reaches `testutil_die`.

State and persistence: each thread owns generator state and distributions; no persisted seed, so runs are not reproducible by default.

Dependencies/integration: used by bounds, database random collection selection, timestamp read selection, and workload generation.

Risks and test signals: lack of deterministic seeding can complicate replay. `generate_random_string` can allocate large temporary repeated strings. Invalid enum use is fatal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/common/random_generator.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/common/random_generator.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/common/random_generator.h

Purpose: Declares the cppsuite random-generator singleton and character-set options.

Important APIs/types/functions: `characters_type` selects pseudo-alphanumeric or alphabet-only data. `random_generator::instance`, string generators, `generate_bool`, and templated `generate_integer` are the public API.

Control flow: singleton copy/assignment are deleted; integer generation uses a uniform distribution over caller-supplied bounds.

State and persistence: owns a Mersenne Twister, distributions, and character constants per thread in the implementation.

Dependencies/integration: included by data-generation and workload helpers.

Risks and test signals: callers must pass valid min/max bounds and choose appropriate string mode for keys versus compressible values. There is no explicit test hook for seeding.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/common/random_generator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/common/thread_manager.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/common/thread_manager.cpp

Purpose: Implements ownership and joining of worker threads used by cppsuite components.

Important APIs/types/functions: destructor logs an error if a stored thread remains joinable, joins it, deletes all thread pointers, and clears the vector. `join` waits until each thread is joinable, logs trace messages while waiting, then joins.

Control flow: `join` must be called by owners during normal finish; destructor is a safety net.

State and persistence: owns heap-allocated `std::thread` pointers in memory only.

Dependencies/integration: used by `workload_manager` to fan out operation threads; logs via `logger`.

Risks and test signals: heap-allocated thread pointers require destructor discipline. Waiting for `joinable()` is unusual because a newly constructed `std::thread` is joinable immediately; a hang here would signal corrupted/null thread state. Destructor error log indicates lifecycle misuse.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/common/thread_manager.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/common/thread_manager.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/common/thread_manager.h

Purpose: Declares a simple thread owner for cppsuite workloads.

Important APIs/types/functions: `add_thread` templated helper allocates a `std::thread` with forwarded callable/args and stores it; `join` joins all workers; destructor cleans up.

Control flow: callers add all worker threads, later call `join`, then allow destruction.

State and persistence: stores `std::vector<std::thread *>`.

Dependencies/integration: used by components that need fan-out, especially workload execution.

Risks and test signals: raw pointer ownership increases leak/double-delete risk if future code mutates `_workers`; no API for clearing after join means destructor still deletes joined thread objects.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/common/thread_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/component.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/component/component.cpp

Purpose: Implements the base lifecycle for cppsuite components.

Important APIs/types/functions: constructor records config/name, reads `enabled`, and computes sleep interval from config. `load` asserts enabled and logs. `run` loops while `_running`, calling virtual `do_work` and sleeping. `end_run` flips `_running` false. `finish` asserts not running and logs. Destructor deletes the owned configuration.

Control flow: expected order is load, run in a thread, end_run, finish. Derived components override `do_work` and sometimes `run`, `load`, or `finish`.

State and persistence: owns `_config`, `_name`, `_enabled`, `_running`, and `_sleep_time_ms`; no direct persistence.

Dependencies/integration: all cppsuite components inherit from this class and use `constants`/`logger`.

Risks and test signals: `_running` is `volatile bool`, not atomic, so cross-thread stop signaling relies on limited guarantees. Assertions catch lifecycle misuse in debug/assert-enabled builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/component.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/component.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/component/component.h

Purpose: Declares the common four-stage component interface for cppsuite.

Important APIs/types/functions: `component` exposes `load`, `run`, `end_run`, pure virtual `do_work`, `enabled`, and `finish`; copy/assignment are deleted.

Control flow: subclasses are expected to perform setup in `load`, work in a run loop, respond to `end_run`, and validate/clean up in `finish`.

State and persistence: holds enable/running flags, throttle interval, owned config pointer, and component name.

Dependencies/integration: uses `configuration`; inherited by timestamp manager, metrics monitor, operation tracker, and workload manager.

Risks and test signals: config ownership is transferred into the component, so callers must not reuse/delete it. Subclasses overriding `run` must preserve lifecycle expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/component.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/metrics_monitor.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/component/metrics_monitor.cpp

Purpose: Samples runtime and postrun metrics, validates configured bounds, and exports selected performance metrics.

Important APIs/types/functions: `get_stat_field` maps configured stat names to WT stat ids. `metrics_monitor::get_stat` reads one statistic from a statistics cursor. `load` constructs stat checkers for cache size, database size, history-store inserts, and checkpoint-cleanup pages, then opens a `statistics:` cursor. `do_work` checks runtime stats. `finish` records saved metrics and validates postrun min/max limits.

Control flow: after base component load, subconfigs define which stats are runtime/postrun/save. Runtime checks happen each loop; final checks happen once in `finish`.

State and persistence: owns a session/cursor and vector of `statistics` objects. Saved metrics are accumulated in `metrics_writer` and written later to JSON.

Dependencies/integration: depends on `connection_manager`, `statistics` subclasses, `database`, constants, and WiredTiger stat ids.

Risks and test signals: only recognized stat names can be mapped by `get_stat_field`. Postrun failures log detailed min/max/actual and call `testutil_die`; runtime failures fail immediately.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/metrics_monitor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/metrics_monitor.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/component/metrics_monitor.h

Purpose: Declares the metrics-monitor component and stat cursor helper.

Important APIs/types/functions: `metrics_monitor` inherits `component`, exposes static `get_stat`, overrides `load`, `do_work`, and `finish`, and stores test name, database reference, session, cursor, and stat-checker list.

Control flow: standard component lifecycle with runtime checks during `do_work` and final checks in `finish`.

State and persistence: keeps active WiredTiger session/cursor state while running; may persist metrics through `metrics_writer`.

Dependencies/integration: includes configuration, database, scoped session/cursor, and statistics interfaces.

Risks and test signals: lifetime of `_database` must outlive the monitor. Statistics cursor availability depends on connection configuration enabling statistics where needed.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/metrics_monitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/metrics_writer.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/component/metrics_writer.cpp

Purpose: Implements collection and JSON output of performance metrics.

Important APIs/types/functions: `metrics_writer::instance` returns a process singleton. `output_perf_file` writes `<test_name>.json` containing one object with `info.test_name` and a metrics array. The templated `add_stat` implementation is in the header.

Control flow: metrics are appended during monitor finish; output is generated on demand and trims the trailing comma if metrics exist.

State and persistence: `_stats` holds JSON fragments in memory; output persists to a JSON file in the current working directory.

Dependencies/integration: used by `metrics_monitor` for saved stats and likely top-level test runners for final output.

Risks and test signals: metric names are not JSON-escaped beyond simple string concatenation, so unusual names could produce invalid JSON. An empty metric list still produces a valid empty array.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/metrics_writer.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/metrics_writer.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/component/metrics_writer.h

Purpose: Declares the singleton metrics writer used for performance JSON generation.

Important APIs/types/functions: `add_stat<T>` accepts arithmetic values only, locks `_stat_mutex`, builds a JSON metric fragment, and appends it. `output_perf_file` writes accumulated metrics.

Control flow: thread-safe appends allow multiple components to save stats before one output pass.

State and persistence: stores stat fragments in `_stats` guarded by a mutex; final file persistence is in the implementation.

Dependencies/integration: included by `metrics_monitor`.

Risks and test signals: no reset API, so multiple tests in one process could share metrics unless process/test runner isolates use. Compile-time `static_assert` catches non-arithmetic metric values.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/metrics_writer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/operation_tracker.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/component/operation_tracker.cpp

Purpose: Tracks schema and row operations in logged WiredTiger tables and periodically sweeps obsolete row-operation history.

Important APIs/types/functions: constructor builds operation tracking table config from configured key/value formats. `load` creates schema and operation tracking tables, opens cursors, and creates a dedicated sweep session/cursor. `do_work` scans the operation table backwards, finds globally visible updates per collection/key at or before oldest timestamp, and removes older obsolete records in no-timestamp transactions. `save_schema_operation`, `save_operation`, and `set_tracking_cursor` persist create/delete and row operation metadata.

Control flow: schema operations are restricted to create/delete; row operation saves reject schema events. Sweeping only runs for the default operation table schema, preserving user-defined validation data for custom schemas.

State and persistence: persists `table:schema_tracking` and `table:operation_tracking` with logging enabled. In-memory state includes sessions/cursors, table config, compression flag, and timestamp manager reference.

Dependencies/integration: depends on `connection_manager`, `timestamp_manager`, constants, `scoped_session/cursor`, and `test_util`; database and workload operations call into it.

Risks and test signals: sweep logic assumes reverse ordering by collection/key/timestamp and default key/value formats. It uses `volatile` running state from `component`. Any unexpected cursor error is fatal; trace logs show obsolete/global update decisions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/operation_tracker.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/operation_tracker.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/component/operation_tracker.h

Purpose: Declares operation tracking schemas, operation enum, and the tracking component interface.

Important APIs/types/functions: macros define default row-operation and schema-operation key/value formats and schema table config. `tracking_operation` enumerates create, custom, delete collection, delete key, and insert. `operation_tracker` exposes table-name getters, lifecycle overrides, schema and row operation save APIs, and virtual `set_tracking_cursor` for custom schemas.

Control flow: callers attach the tracker to database/workload components, then saves happen during schema and data operations while the component sweeps in its own loop.

State and persistence: owns table names/configs, sessions/cursors, compression flag, and timestamp manager reference.

Dependencies/integration: inherits `component`, includes scoped storage wrappers and timestamp manager.

Risks and test signals: custom tracking formats disable default sweeping, which can grow tables. The virtual cursor setter is the extension point for non-default operation tracking, so overrides must match table format exactly.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/operation_tracker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/cache_limit.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/cache_limit.cpp

Purpose: Implements a statistic checker for cache usage as a percentage of configured maximum cache bytes.

Important APIs/types/functions: constructor delegates to `statistics` with no single WT stat field. `get_value` reads image bytes, other bytes, and max bytes from the connection statistics cursor and returns `(image+other)*100/max`. `check` fails if use percentage exceeds configured `max`.

Control flow: called by metrics monitor during runtime or finish depending on config.

State and persistence: no state beyond inherited min/max/name flags; reads live statistics only.

Dependencies/integration: uses `metrics_monitor::get_stat`, WiredTiger stat ids, logger, and `test_util`.

Risks and test signals: asserts max cache bytes is positive and multiplication stays within `INT64_MAX`. A high cache percentage fails immediately with a detailed fatal message.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/cache_limit.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/cache_limit.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/cache_limit.h

Purpose: Declares the cache-limit statistic specialization.

Important APIs/types/functions: `cache_limit` inherits `statistics`, overrides `check` and `get_value`, and is constructed from config plus stat name.

Control flow: metrics monitor treats it through the base `statistics` interface.

State and persistence: inherited configuration state only; no persisted data.

Dependencies/integration: includes configuration, scoped cursor, and base statistics.

Risks and test signals: callers should configure sensible max bounds because this checker ignores base `field` and computes a derived percentage.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/cache_limit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/database_size.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/database_size.cpp

Purpose: Implements a filesystem-backed statistic for total database file size.

Important APIs/types/functions: `collection_name_to_file_name` maps `table:name` to `DEFAULT_DIR/name.wt`. `get_file_names` collects all database collection files plus history store and metadata files. `get_db_size` sums `stat` sizes, allowing `ENOENT`. `check` fails if size exceeds configured max; `get_value` returns size as `int64_t`.

Control flow: metrics monitor invokes it without needing a WT statistics cursor. Windows currently logs that checking is not implemented but the implementation references a differently cased logger in the disabled block.

State and persistence: reads persistent WT files from disk; holds a database reference for collection names.

Dependencies/integration: depends on `database`, filesystem `stat`, WT internal file constants, logger, and `test_util`.

Risks and test signals: assumes table URIs map directly to `.wt` files under `DEFAULT_DIR`, which may not hold for all data sources or disaggregated layouts. Missing files are tolerated only as `ENOENT`; size-limit failures are fatal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/database_size.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/database_size.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/database_size.h

Purpose: Declares the database-size statistic specialization.

Important APIs/types/functions: `database_size` inherits `statistics`, overrides `check` and `get_value`, and has private helpers for database size and file-name enumeration.

Control flow: metrics monitor invokes it as a `statistics` object, but it ignores the passed stats cursor.

State and persistence: stores a reference to the in-memory database model and reads persisted WT files.

Dependencies/integration: includes configuration, database, scoped cursor, and statistics base.

Risks and test signals: database reference lifetime must exceed the statistic object; file layout assumptions should be revisited for new storage modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/database_size.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/statistics.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/statistics.cpp

Purpose: Implements the generic statistic bound checker used by metrics monitor.

Important APIs/types/functions: constructor reads `max`, `min`, `postrun`, `runtime`, and `save` from configuration. `check` reads a stat via `metrics_monitor::get_stat` and fails if outside min/max. `get_value` returns the current stat. Getters expose all configuration fields.

Control flow: metrics monitor decides when to call `check` and whether to save or postrun-validate based on the getter flags.

State and persistence: stores stat id, bounds, name, and mode flags in memory; no persistence.

Dependencies/integration: depends on configuration keys, logger, metrics monitor, and scoped cursor.

Risks and test signals: error text says post-run even for runtime checks, which can be diagnostically confusing. Any out-of-range value is fatal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/statistics.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/statistics.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/statistics.h

Purpose: Declares the base class for metric/statistic validation.

Important APIs/types/functions: `statistics` has constructors, virtual `check`, virtual `get_value`, and getters for stat field, min/max, name, and mode flags.

Control flow: subclasses may override `check` and `get_value` for derived metrics while preserving the base config contract.

State and persistence: protected fields hold all checker state.

Dependencies/integration: included by metrics monitor and specialized statistic classes.

Risks and test signals: base class assumes integer stat values and fixed min/max bounds; tests needing non-integer or multi-field semantics require subclassing.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/statistics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/timestamp_manager.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/component/timestamp_manager.cpp

Purpose: Manages test timestamps and advances WiredTiger stable/oldest timestamps within configured lag windows.

Important APIs/types/functions: `decimal_to_hex` and `hex_to_decimal` convert timestamp formats. `load` reads oldest/stable lag seconds and shifts them into the high 32 timestamp bits. `do_work` computes current logical time, advances stable and oldest when lag windows expire, calls `connection_manager::set_timestamp`, and updates local atomics after WT is updated. `get_next_ts` combines steady-clock seconds with an atomic increment. `get_valid_read_ts` returns a random timestamp between oldest and just before stable.

Control flow: the component run loop periodically calls `do_work`. Timestamp publication order is intentional: set WT timestamps first, then update local oldest/stable values used by sweep/read helpers.

State and persistence: maintains `_increment_ts`, `_oldest_ts`, `_stable_ts`, and lag windows in memory; persists timestamp state into the WiredTiger connection.

Dependencies/integration: depends on `connection_manager`, `configuration`, random generator, logger, and WT timestamp types. Operation tracking uses `get_oldest_ts`; database/workload operations use `get_next_ts`.

Risks and test signals: steady-clock timestamps are process-relative, not wall-clock. `get_valid_read_ts` can race with oldest advancement but relies on timestamp rounding. Assertions catch oldest/stable inversion and hex parse failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/timestamp_manager.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/timestamp_manager.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/component/timestamp_manager.h

Purpose: Declares the timestamp-manager component and timestamp utility APIs.

Important APIs/types/functions: exposes conversion helpers, lifecycle overrides, `get_next_ts`, `get_oldest_ts`, and `get_valid_read_ts`. Private `get_time_now_s` returns seconds shifted into timestamp high bits.

Control flow: used both as a periodic component and as a service object for other components.

State and persistence: atomic increment and oldest timestamp plus stable timestamp and lag windows.

Dependencies/integration: inherits `component` and uses WT timestamp/test utility types.

Risks and test signals: `_stable_ts` is not atomic while readers may call `get_valid_read_ts`; current code assumes acceptable benign races. Lag configs must be nonnegative.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/timestamp_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/workload_manager.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/component/workload_manager.cpp

Purpose: Populates the database and starts configured workload operation threads.

Important APIs/types/functions: constructor wires config, database operation implementation, timestamp manager, and database. `set_operation_tracker` attaches tracking. `run` builds `operation_configuration` objects for background compact, checkpoint, custom, insert, read, remove, and update; populates the database; creates barriers and `thread_worker` objects; and launches operation functions through `thread_manager`. `finish` calls each worker's `finish`, joins threads, and logs completion.

Control flow: unlike the base component, `run` does one-time population and thread launch, then returns while worker threads continue. The top-level test later calls `finish` to stop/join workers.

State and persistence: owns thread workers, thread manager, database operation pointer, database reference, timestamp/operation tracker pointers, and `_db_populated` flag. Workload operations persist actual database contents.

Dependencies/integration: depends on `operation_configuration`, `thread_worker`, `database_operation`, `connection_manager`, `barrier`, and logger.

Risks and test signals: `do_work` asserts false because this component should not use base run-loop semantics. Thread and config lifetimes are delicate: operation configs are deleted after worker construction, so workers must not retain raw config pointers beyond construction. Join success and worker finish are the key lifecycle signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/workload_manager.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/workload_manager.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/component/workload_manager.h

Purpose: Declares the component responsible for executing database workloads.

Important APIs/types/functions: `workload_manager` overrides `run`, `finish`, and `do_work`, exposes `get_database`, `db_populated`, and `set_operation_tracker`, and stores worker/thread orchestration state.

Control flow: top-level tests use it as the workload phase owner rather than a periodic component.

State and persistence: holds database reference, database operation pointer, timestamp manager pointer, operation tracker pointer, worker vector, thread manager, and population flag.

Dependencies/integration: includes configuration, database operation, thread worker, and thread manager.

Risks and test signals: destructor deletes workers but not the database operation or timestamp manager, so ownership is external for those pointers. Tests should verify `db_populated` before validation phases that assume existing data.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/component/workload_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/collection.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/main/collection.cpp

Purpose: Implements the in-memory collection model's key-count operations.

Important APIs/types/functions: constructor stores immutable `name` and `id` and initializes `_key_count`. `get_key_count` returns the atomic key count. `increase_key_count` atomically increments it.

Control flow: callers read key count before inserting contiguous new keys and increment only after commit.

State and persistence: key count is in-memory metadata mirroring persistent table contents; table contents are persisted elsewhere.

Dependencies/integration: used by `database` and workload operations to choose valid key ranges.

Risks and test signals: atomic increment does not alone prevent logical conflicts if multiple insertion threads extend the same collection concurrently; the header documents the expected single-threaded extension pattern.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/collection.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/collection.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/main/collection.h

Purpose: Declares the in-memory representation of one test collection.

Important APIs/types/functions: `collection` stores immutable public `name` and `id`, deletes copy/assignment, and exposes `get_key_count` and `increase_key_count`.

Control flow: documents the required pattern for contiguous key creation: read current count, insert keys at/above it, then increment after successful commit.

State and persistence: private atomic `_key_count` represents modeled row count.

Dependencies/integration: owned by `database` and used by workload operations.

Risks and test signals: model consistency depends on workloads updating key count only after durable commit and coordinating inserts per collection.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/collection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/configuration.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/main/configuration.cpp

Purpose: Wraps WiredTiger config parsing and merges test-specific user configuration with generated default configuration.

Important APIs/types/functions: constructors load defaults via `__wt_test_config_match` or wrap a nested `WT_CONFIG_ITEM`. `get_*` and optional variants retrieve typed values through templated `get`. `get_throttle_ms` parses rates ending in `ms`, `s`, or `m`. `merge_default_config` recursively overlays user values onto default values. `split_config` tokenizes key/value pairs while respecting nested `()` and `[]`, sorts by key, and validates empty/malformed entries.

Control flow: top-level construction merges config then opens a WT config parser. Typed getters validate WT item types before conversion. Nested subconfigs allocate new `configuration` objects for component ownership.

State and persistence: owns config string and `WT_CONFIG_PARSER`; no direct persistence, but parsed values drive database/table/component behavior.

Dependencies/integration: depends on WT config parser, generated test config metadata, constants, logger, and `test_util`. Used throughout cppsuite components.

Risks and test signals: recursive merge assumes sorted key order and that user subconfigs start with `(`. `get_throttle_ms` uses substring matching, so malformed strings can throw or be misread. Parser/type errors fail fast through `testutil_die`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/configuration.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/configuration.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/main/configuration.h

Purpose: Declares cppsuite's typed configuration wrapper and utility string splitter.

Important APIs/types/functions: `split_string` splits non-empty tokens on a delimiter. `configuration` exposes typed getters for bool, int, string, list, and subconfig values, optional getter variants, and `get_throttle_ms`.

Control flow: callers request required config values and receive fatal errors for missing/mistyped keys; optional methods return defaults or null/empty values.

State and persistence: stores merged configuration and WT parser pointer.

Dependencies/integration: includes `wiredtiger.h` and is consumed by all component and main harness code.

Risks and test signals: returned subconfigs are heap allocated and ownership is transferred to callers/components. List parsing is simple comma splitting after bracket removal and does not handle escaped commas.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/configuration.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/crud.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/main/crud.h

Purpose: Provides inline CRUD helpers that translate WiredTiger cursor return codes into transaction state for workload operations.

Important APIs/types/functions: `crud::insert`, `crud::update`, and `crud::remove` set cursor key/value as needed, invoke the WT cursor method, mark the `transaction` for rollback on `WT_ROLLBACK`, return false for retry/abort handling, and die on unhandled errors.

Control flow: helpers are intended to be called inside a transaction object that can later roll back if any operation sees `WT_ROLLBACK`.

State and persistence: successful calls mutate persistent table data through the cursor. On rollback conflicts they only mark in-memory transaction state.

Dependencies/integration: depends on `scoped_cursor`, `transaction`, `wiredtiger.h`, and `test_util`.

Risks and test signals: `WT_NOTFOUND` on remove/update is treated as an unhandled fatal error, so callers must choose existing keys or handle search separately. Rollback handling is explicit and observable via transaction state.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/crud.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/database.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/main/database.cpp

Purpose: Implements the in-memory database/collection model and creates WiredTiger collections.

Important APIs/types/functions: `build_collection_name` returns `table:collection_<id>`. `add_collection` locks, validates create config, assigns an id, inserts a `collection`, creates the WT table, and records a schema operation if tracking is enabled. `add_existing_collections` seeds the model for reopened databases without creating tables. `get_collection`, `get_random_collection`, `get_collection_count`, `get_collection_names`, and `get_collection_ids` query model state. `set_timestamp_manager`, `set_operation_tracker`, and `set_create_config` wire dependencies and table config.

Control flow: collection creation is serialized by `_mtx`; random selection requires at least one collection. Compression, reverse collator, and disaggregated layered settings are appended to `DEFAULT_FRAMEWORK_SCHEMA`.

State and persistence: `_collections` and `_next_collection_id` track in-memory model state; `session->create` persists tables; operation tracker persists schema metadata with a timestamp.

Dependencies/integration: depends on `collection`, constants, random generator, scoped session, timestamp manager, operation tracker, and WT session API.

Risks and test signals: `add_collection` assumes timestamp manager is set when operation tracker is present. `get_random_collection` chooses ids from `0..count-1`, assuming collection ids are contiguous and never deleted from the model. `testutil_die/assert` catch missing config and invalid ids.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/database.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/database.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/main/database.h

Purpose: Declares the cppsuite database model, a thread-safe map of collection ids to collection metadata plus creation/tracking configuration.

Important APIs/types/functions: public API covers collection creation, seeding existing collections, lookup/random selection, collection count/name/id listing, and dependency/config setters.

Control flow: callers configure create options and dependency pointers before adding collections; workload operations query the model during execution.

State and persistence: holds create config string, timestamp manager pointer, operation tracker pointer, next id, collection map, and mutex. Persistent table creation is implemented in the source file.

Dependencies/integration: includes `collection` and `operation_tracker`; used by workload manager, database operations, metrics, and validators.

Risks and test signals: pointer dependencies are non-owning and asserted to be set only once. Model and persistent database can diverge if table creation succeeds but later model/tracking assumptions fail; tests rely on validation and operation tracking to catch that.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/database.h -->
