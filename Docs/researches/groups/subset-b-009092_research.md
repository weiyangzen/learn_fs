# subset-b-009092 Research

Grouped source research for WiredTiger utility, verbose, verify, syscall, thread-stress, and shared test-utility files. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_util11.py

## Purpose

`test_util11.py` verifies the `wt list` utility against an initially empty database, a database with several tables, dropped-table cases, and the `-f` output-file option. It is a Python suite test built on `wttest.WiredTigerTestCase` and `suite_subprocess` so it can create tables through the API and then inspect `wt` subprocess output.

## Important APIs, Types, and Functions

The test class `test_util11` defines `populate`, `create_tables`, and `compare_two_files` helpers plus test methods for empty listing, normal listing, listing after partial/all drops, and custom file output. It uses `session.create`, `open_cursor`, `dropUntilSuccess`, `runWt`, `check_file_content`, and file comparison.

## Control Flow

Each test constructs table state, runs `wt list` with optional URI prefixes or `-c -f`, and compares stdout or a target file with an expected sorted table URI list.

## State and Persistence Behavior

The persistent state is WiredTiger table metadata and one inserted key/value in selected tables. Drop tests assert list output follows metadata removal. The `-f` case persists output in a named local file.

## Dependencies and Integration Points

Depends on the WiredTiger Python test framework, the `wt` binary wrapper in `suite_subprocess`, and metadata/listing behavior in the utility layer.

## Risks and Edge Cases

The final custom-output comparison currently calls `compare_two_files` without asserting its boolean result, so a regression could be missed unless the helper raises elsewhere. Expected output assumes deterministic list ordering.

## Test Signals

Good signals are exact output matches, empty stdout when custom output is requested, no listed dropped tables, and successful operation with both populated and empty objects.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_util12.py

## Purpose

`test_util12.py` exercises `wt write` for insert, overwrite, remove, and argument validation paths. It confirms subprocess writes are visible through a WiredTiger cursor and that invalid invocations report expected utility errors.

## Important APIs, Types, and Functions

The `test_util12` class defines table name/config constants and five test methods: `test_write`, `test_write_overwrite`, `test_write_remove`, `test_write_no_keys`, and `test_write_bad_args`. It uses `runWt`, `check_file_contains`, `session.create`, cursors, and `wiredtiger.WT_NOTFOUND`.

## Control Flow

Tests create a string-key/string-value table, run `wt write` with key/value arguments, reopen a cursor, and assert sorted cursor traversal. Negative cases run the utility with `failure=True` and inspect stderr for `usage:`, duplicate-key, or not-found messages.

## State and Persistence Behavior

The utility mutates table contents directly in the WiredTiger home. Overwrite mode replaces an existing value only with `-o`; remove mode deletes one key only with `-r`.

## Dependencies and Integration Points

Depends on `suite_subprocess` for process execution and on the command implementation for `write`, cursor insertion semantics, duplicate-key handling, and removal semantics.

## Risks and Edge Cases

The test is sensitive to cursor ordering and exact diagnostic wording. It covers string formats only and does not exercise binary/record-number key formats.

## Test Signals

Expected signals are final cursor contents, `WT_NOTFOUND` at end of scan, duplicate-key rejection without `-o`, not-found rejection for remove, and usage output for malformed argument counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util12.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_util13.py

## Purpose

`test_util13.py` validates `wt dump` and `wt load` preservation of non-default table configuration. It covers simple file, simple table, and complex table/column-group datasets through scenarios.

## Important APIs, Types, and Functions

The class uses `SimpleDataSet`, `ComplexDataSet`, and `make_scenarios`. Helpers `compare_config`, `compare_files`, and `load_recheck` parse dump headers, compare expected config subsets, load dump output into a separate home, and dump again for comparison.

## Control Flow

`test_dump_config` populates the scenario dataset, writes an expected header containing the current WiredTiger version and expected config lines, runs `wt dump`, compares header/config fields, loads the dump into `dump_dir`, opens a new connection there, and re-dumps to verify configuration round-trips.

## State and Persistence Behavior

The test persists the original dataset, creates `expect.out`, `dump.out`, `dump_dir`, and `newdump.out`, and relies on dump/load preserving schema metadata and data.

## Dependencies and Integration Points

Integrates with dataset helpers, `wiredtiger.wiredtiger_version`, the `wt dump`/`load` utilities, and metadata config serialization.

## Risks and Edge Cases

The config parser is deliberately simple and strips complex table `colgroups`/`columns`; nested config groups or format changes can break it. Expected dump text is version-sensitive and output-format-sensitive.

## Test Signals

Signals include matching dump header/config subset, successful `wt load`, successful cursor validation through `ds.check`, and matching re-dumped configuration.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util13.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_util14.py

## Purpose

`test_util14.py` tests the `wt truncate` command on a populated table and validates common error paths for missing, invalid, nonexistent, and duplicate URI arguments.

## Important APIs, Types, and Functions

`test_util14` has one method, `test_truncate_process`, using `session.create`, table existence checks, cursor inserts, `runWt`, `check_empty_file`, and `check_file_contains`.

## Control Flow

The test creates a table, inserts 1000 string rows, invokes `wt truncate table:<name>`, then uses `wt read` to confirm the table still exists but has no matching records. It then runs malformed truncate commands and checks stderr.

## State and Persistence Behavior

The table remains as metadata after truncate while its records are removed. Output and error files are reused for positive and negative command checks.

## Dependencies and Integration Points

Depends on `suite_subprocess`, `wt truncate`, `wt read`, WiredTiger table metadata, and row-store cursor behavior.

## Risks and Edge Cases

Exact error messages (`usage:`, `No such file or directory`, `not found`) are part of the assertion surface. The test only covers full-object truncation, not bounded cursor/key truncation.

## Test Signals

Strong signals are table existence after truncate, empty read stdout, expected not-found stderr for reads, and clear failure behavior for invalid truncate invocations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util14.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util15.py -->
# sources/storage-engines/wiredtiger/test/suite/test_util15.py

## Purpose

`test_util15.py` verifies the `wt alter` utility updates table metadata by changing `access_pattern_hint` from sequential to random.

## Important APIs, Types, and Functions

The single `test_alter_process` method creates a table, invokes `wt alter`, opens the `metadata:create` cursor, searches for the table metadata key, and checks the returned config string.

## Control Flow

The test performs two alter cycles. After each `runWt(["alter", uri, config])`, it reads metadata directly and asserts the new access-pattern setting appears in the stored create config.

## State and Persistence Behavior

The persistent state is table metadata in WiredTiger's metadata file; no table data is required. Metadata changes survive the subprocess boundary.

## Dependencies and Integration Points

Integrates the `wt alter` command, metadata cursor access, table existence helper, and string config representation.

## Risks and Edge Cases

The assertion is substring-based, so it does not detect duplicate conflicting settings. It covers only one alterable setting and does not test invalid configs or active cursors.

## Test Signals

Expected signals are successful utility exit and metadata containing `access_pattern_hint=sequential` and later `access_pattern_hint=random`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util15.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util17.py -->
# sources/storage-engines/wiredtiger/test/suite/test_util17.py

## Purpose

`test_util17.py` smoke-tests the `wt stat` utility at both connection and table scopes. It checks that plausible statistics are emitted without performing detailed statistic validation.

## Important APIs, Types, and Functions

`test_stat_process` creates a table, runs `wt stat`, and checks for connection-level `cursor: cursor create calls=` output. It then runs `wt stat table:<name>` and checks a cache-walk root-page line.

## Control Flow

After table creation, the test invokes the utility twice with different arguments and inspects a fixed output file for expected substrings.

## State and Persistence Behavior

The table metadata and initial empty btree provide the target for data-source statistics. Utility output is persisted to `wt-stat.out`.

## Dependencies and Integration Points

Depends on `suite_subprocess`, the `wt stat` command, statistics cursor formatting, and cache-walk statistics availability.

## Risks and Edge Cases

The cache-walk string can be brittle across statistic naming or output-format changes. This is a smoke test, not a semantic validation of stat values.

## Test Signals

Signals are nonempty statistic output containing known connection and table statistic labels.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util17.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util18.py -->
# sources/storage-engines/wiredtiger/test/suite/test_util18.py

## Purpose

`test_util18.py` tests `wt printlog` formatting, redaction, hexadecimal output, messages-only output, and LSN-range filtering under logging-enabled connections.

## Important APIs, Types, and Functions

The class uses scenario flag `print_user_data`, `conn_config`, `populate`, and `check_populated_printlog`. Test methods cover default printlog, `-x`, `-m`, and `-l` range behavior. It uses log cursors and `session.log_printf`.

## Control Flow

Each test creates/populates a table, optionally writes a log message, runs `wt printlog` with option combinations, and asserts whether JSON key/value fields or hex fields appear. The LSN test derives first, second, and last LSNs from a `log:` cursor and compares bounded outputs.

## State and Persistence Behavior

The test requires retained log files (`log=(enabled,file_max=100K,remove=false)`). It persists small key/value updates, log messages, and printlog output files for comparison.

## Dependencies and Integration Points

Integrates WiredTiger logging, log cursors, `wt printlog`, redaction policy controlled by `-u`, and output formatting.

## Risks and Edge Cases

The LSN cursor loop calls `c.next()` inside the loop body, which can skip records; the test still extracts a last LSN but depends on available log records. Output assertions are sensitive to JSON field spelling.

## Test Signals

Signals include expected user-data redaction, hex emission only when requested and unredacted, message-only suppression of data records, and equivalence between explicit first LSN and `1,0` range starts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util18.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util19.py -->
# sources/storage-engines/wiredtiger/test/suite/test_util19.py

## Purpose

`test_util19.py` validates `wt downgrade` compatibility behavior across combinations of initial creation release and requested downgrade release.

## Important APIs, Types, and Functions

The class defines scenario matrices for `create_release` and `downgrade_release`, `conn_config` to set initial compatibility/logging, and `test_downgrade` to populate records and inspect downgrade verbose output.

## Control Flow

For each scenario, the test opens a logging-enabled database, optionally with `compatibility=(release=...)`, inserts 100 records, runs `wt -C <config> downgrade -V <release>` without reopening the session, and checks whether verbose log compatibility text appears.

## State and Persistence Behavior

The command mutates database compatibility metadata and log compatibility state. Log files are retained to exercise downgrade compatibility transitions.

## Dependencies and Integration Points

Depends on compatibility configuration, the `wt downgrade` utility, logging compatibility levels, `verbose=[log]`, and scenario expansion.

## Risks and Edge Cases

The assertion checks verbose text rather than querying metadata directly. Exact compatibility-version mapping must stay synchronized with WiredTiger release rules.

## Test Signals

Expected signals are downgrade success and presence or absence of `WT_CONNECTION.reconfigure: ... COMPATIBILITY: Version now <n>` according to the target release.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util19.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util21.py -->
# sources/storage-engines/wiredtiger/test/suite/test_util21.py

## Purpose

`test_util21.py` ensures `wt dump file:WiredTigerHS.wt` can dump obsolete history-store data and that advancing oldest timestamp plus checkpoint does not unexpectedly remove clean obsolete history-store content.

## Important APIs, Types, and Functions

The class defines `conn_config='cache_size=50MB'`, `add_data_with_timestamp`, and `test_dump_obsolete_data`. It uses transactions with commit timestamps, connection timestamp setting, checkpoint, `runWt`, and `helper.compare_files`.

## Control Flow

The test creates a table, sets oldest timestamp, writes four timestamped value generations, checkpoints, sets stable timestamp to protect data across utility reopen, dumps the history store, advances oldest timestamp to 6, checkpoints again, dumps the history store again, and compares the dump files.

## State and Persistence Behavior

Persistent state includes table updates at timestamps 2, 3, 5, and 7 and resulting history-store records in `WiredTigerHS.wt`. Checkpoints make pages clean and stable timestamp protects state during `wt dump`.

## Dependencies and Integration Points

Integrates timestamp management, history store cleanup rules, checkpoints, and `wt dump` of an internal file.

## Risks and Edge Cases

The test assumes clean pages are not rewritten/cleaned during the second checkpoint. It is sensitive to history-store format and cleanup policy changes.

## Test Signals

The key signal is byte-equivalent dump output before and after oldest timestamp advancement.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util21.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util22.py -->
# sources/storage-engines/wiredtiger/test/suite/test_util22.py

## Purpose

`test_util22.py` checks help and option parsing for the `wt` utility and its subcommands. It ensures global help, command help, missing arguments, unknown commands, and illegal options report usage consistently.

## Important APIs, Types, and Functions

The `commands` list covers most `wt` subcommands except `copyright`. Test methods are `test_help_option`, `test_no_argument`, `test_unsupported_command`, and `test_unsupported_option`.

## Control Flow

The tests run `wt -?`, each `<command> -?`, `wt -h`, an unsupported command, and `-^` both globally and per command. They inspect a shared stderr file for `global_options:`, `options:`, or exact illegal/missing option messages.

## State and Persistence Behavior

No data persistence is required; state is stderr output from the utility parser.

## Dependencies and Integration Points

Depends on `suite_subprocess`, global option parsing, command dispatch, and per-command usage generation.

## Risks and Edge Cases

Exact parser wording is asserted, and the static command list must be updated when supported commands change.

## Test Signals

Signals are successful help invocations, expected failure for invalid options, and correct distinction between global help text and command-specific options text.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util22.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util23.py -->
# sources/storage-engines/wiredtiger/test/suite/test_util23.py

## Purpose

`test_util23.py` is a regression test for `wt verify` usage-path scratch-buffer handling. It verifies that a deliberately invalid command path reports usage without leaking a diagnostic scratch-buffer warning.

## Important APIs, Types, and Functions

The class defines `uri='file:test_util23.wt'`, command list `["-r", "verify", "-d", "dump_offsets", uri]`, and `test_verify_scratch_buffer`. It is skipped for the disaggregated hook because read-only utility connections are unsupported there.

## Control Flow

The test creates a file object, runs the command expecting failure, checks `errfile.txt` contains `usage:`, then reads the whole error file and asserts it does not contain `scratch buffer allocated and never discarded`.

## State and Persistence Behavior

The only persistent database state is the created file object; the main observed state is stderr from the utility failure path.

## Dependencies and Integration Points

Depends on `wt verify` option parsing, read-only `-r` global handling, diagnostics around scratch buffers, and `suite_subprocess`.

## Risks and Edge Cases

It is narrow and aimed at one leak diagnostic. It does not validate successful verify behavior.

## Test Signals

Expected signals are command failure with usage output and absence of the scratch-buffer diagnostic string.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util23.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_verbose01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_verbose01.py

## Purpose

`test_verbose01.py` defines shared verbose-test helpers and validates legacy verbose configuration without explicit verbosity levels. It covers flat and JSON output formats.

## Important APIs, Types, and Functions

`test_verbose_base` provides `expected_json_schema`, `validate_json_schema`, `validate_json_category`, `create_verbose_configuration`, and context manager `expect_verbose`. `test_verbose01` tests single category, multiple categories, no category, and invalid category behavior.

## Control Flow

`expect_verbose` cleans stdout, opens a new connection with `verbose=[...]` and optional `json_output=[message]`, yields it for operations, reads captured output, optionally parses JSON, matches category patterns, closes the connection, and cleans stdout again.

## State and Persistence Behavior

Tests create short-lived tables and cursors only to trigger verbose messages. Captured stdout is the principal state under inspection.

## Dependencies and Integration Points

Depends on `suite_subprocess`, `wttest` stdout capture, verbose categories such as `api`, `compact`, and `version`, and JSON event-handler formatting.

## Risks and Edge Cases

Output truncation is guarded by dropping the last line when the read cap is reached. Pattern matching validates category strings but not every field in flat messages.

## Test Signals

Signals are generated verbose output only for enabled categories, no output for empty verbose config, JSON schema compliance when requested, and a config error for an unknown category.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_verbose01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_verbose02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_verbose02.py

## Purpose

`test_verbose02.py` extends verbose configuration coverage to explicit verbosity levels. It verifies accepted level syntax and rejection of out-of-range levels.

## Important APIs, Types, and Functions

The class `test_verbose02` inherits `test_verbose_base`, uses flat/JSON scenarios, and defines `test_verbose_single`, `test_verbose_multiple`, and `test_verbose_level_invalid`.

## Control Flow

The single-category test opens connections with `api:1`, `api:0`, and `compact:0` through `compact:5`, performs table/cursor/compact operations, and checks whether expected verbose patterns appear. The multiple-category test exercises mixed level syntax such as `api:1,version`. Invalid tests assert `wiredtiger_open` raises for `api:-1` and `api:6`.

## State and Persistence Behavior

State is transient table activity plus captured stdout. The test repeatedly closes the default connection and opens new ones with different verbose configs.

## Dependencies and Integration Points

Depends on verbose level parsing, category-specific level filtering, `compact` verbose messages, JSON message support inherited from the base class, and `wiredtiger.WiredTigerError`.

## Risks and Edge Cases

The test assumes `api:0` currently produces no messages for its operations and that compact emits output at all tested levels. Changes in logging volume can affect expectations.

## Test Signals

Signals include output for enabled categories at valid levels, suppressed output at a non-emitting level, and parse errors for invalid levels.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_verbose02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_verbose03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_verbose03.py

## Purpose

`test_verbose03.py` verifies JSON encoding for event-handler messages and errors. It ensures generated JSON can be parsed, follows the expected schema, and carries the expected verbose category IDs.

## Important APIs, Types, and Functions

The class defines context manager `expect_event_handler_json`, plus `test_verbose_json_message` and `test_verbose_json_err_message`. It reuses schema/category validators from `test_verbose_base` and imports `wiredtiger` constants.

## Control Flow

The context manager cleans stdout or stderr, opens a connection with `json_output=[message]` or `json_output=[error]`, yields it, reads messages, parses each line as JSON, validates fields/types and categories, then closes and cleans. Tests trigger API/version messages with table operations and a default-category error by beginning a transaction with invalid read timestamp.

## State and Persistence Behavior

Only temporary tables and captured event-handler output are involved. Error output is explicitly read from stderr in the error-message test.

## Dependencies and Integration Points

Depends on JSON event output, verbose category constants, transaction timestamp validation, and stdout/stderr capture in the Python test harness.

## Risks and Edge Cases

The schema is strict for field names and types, so intentional schema changes require test updates. The error path catches the expected exception and validates emitted diagnostics indirectly.

## Test Signals

Signals are successful JSON parsing, schema validation, correct `WT_VERB_API`, `WT_VERB_VERSION`, or `WT_VERB_DEFAULT` category IDs, and clean resource closure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_verbose03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_verbose04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_verbose04.py

## Purpose

`test_verbose04.py` tests the special verbose category `all` and the public category enumeration API. It is skipped under tiered storage because tiered output changes the expected logs.

## Important APIs, Types, and Functions

The class derives from `test_verbose_base`, builds `all_verbose_categories` from `wiredtiger.wiredtiger_get_verbose_categories`, and defines `test_verbose_categories`, `test_verbose_all`, and `test_verbose_multiple`.

## Control Flow

`test_verbose_categories` compares returned categories with `WT_VERB_*` attributes except default/count sentinels. `test_verbose_all` opens connections with `all` at levels 0 through 5 and triggers table/cursor/compact operations. `test_verbose_multiple` combines `api`, `all`, and `version` to ensure category filtering follows precedence expectations.

## State and Persistence Behavior

The test creates short-lived tables to generate output and inspects captured stdout. No durable data state is validated beyond successful operations.

## Dependencies and Integration Points

Depends on category enumeration, `WT_VERB_NUM_CATEGORIES`, `all` parsing, level filtering, inherited JSON/flat validation, and compaction verbosity.

## Risks and Edge Cases

The category set must track the Python module constants exactly. The multiple-category expectation removes API/version from the all set and is sensitive to precedence semantics.

## Test Signals

Signals are category list equality, output matching any enabled verbose category under `all`, and correct suppression/selection when `all` is combined with explicit categories.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_verbose04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_verbose05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_verbose05.py

## Purpose

`test_verbose05.py` validates checkpoint-progress verbose logging volume. It ensures progress messages appear but are bounded for both small and large databases.

## Important APIs, Types, and Functions

The class uses `conn_config='statistics=(all),verbose=[checkpoint_progress:0]'`, size scenarios, helper `populate`, `WiredTigerCursor`, `statistic_uri`, and `stat.conn.checkpoint_pages_reconciled`.

## Control Flow

The test creates a small-page table, writes large string values, checkpoints, reads checkpoint pages reconciled as an upper-bound estimate, reads stdout, counts messages matching a checkpoint-progress regex, compares the count with logarithmic lower/upper bounds, cleans stdout, and disables verbose output.

## State and Persistence Behavior

Persistent state is the populated table and checkpoint output. The statistic cursor observes connection statistics after checkpoint.

## Dependencies and Integration Points

Depends on verbose checkpoint-progress logging, statistics cursors, checkpoint reconciliation, and Python helper cursors. It is skipped for disaggregated and tiered hooks because their checkpoint progress differs.

## Risks and Edge Cases

The log-count bounds depend on page counts and current progress throttling. Very small page counts can make logarithmic bounds tight.

## Test Signals

Signals are progress messages matching the expected text and a count between the computed lower and upper limits.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_verbose05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_verify.py -->
# sources/storage-engines/wiredtiger/test/suite/test_verify.py

## Purpose

`test_verify.py` is broad coverage for `wt verify` and `WT_SESSION.verify`, including empty/populated tables, corrupt pages, truncation, redaction, and verifying all tables.

## Important APIs, Types, and Functions

Helpers include `file_name`, `populate`, `check_populate`, `count_file_contains`, `open_and_position`, and `open_and_offset`. Test methods cover process/API success paths, checksum corruption at offsets/percentages, `read_corrupt`, dump-address diagnostics, zero-length/truncated files, redacted dump-pages output, and `verify -a`.

## Control Flow

Positive tests create tables, populate data, and verify through subprocess or API. Corruption tests close the connection via helper, overwrite or truncate table files, reopen when needed, run verify with diagnostic options, and inspect stdout/stderr. The redaction test inserts secret values, checkpoints, compares redacted and `-u` unredacted output.

## State and Persistence Behavior

This file directly mutates WiredTiger data files after closing the connection, so disk state is central. It relies on no checkpoints before initial object-name assumptions and uses checkpointing for redaction/all-table scenarios.

## Dependencies and Integration Points

Depends on filesystem access to `.wt` or tiered object names, `suite_subprocess`, diagnostic build gating, `helper.WiredTigerCursor`, API verify, utility verify, checksum reporting, and stderr/stdout pattern filtering.

## Risks and Edge Cases

Several corruption helpers are skipped for disaggregated storage. Offset selection may hit free space or parent pages, so assertions allow at least one checksum error rather than exact full coverage.

## Test Signals

Signals include successful verify on clean data, expected `WT_SESSION.verify` errors on corruption, dump-address read-failure messages, checksum diagnostics, no secret data in redacted output, secret data with `-u`, and abort behavior that stops after the first corrupted table.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_verify.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_verify2.py -->
# sources/storage-engines/wiredtiger/test/suite/test_verify2.py

## Purpose

`test_verify2.py` targets API verify edge cases around dirty trees, checkpoint requirements, empty-tree search behavior, and nonexistent tables.

## Important APIs, Types, and Functions

The class `test_verify2` defines table constants and three tests: `test_verify_ckpt`, `test_verify_search`, and `test_verify_empty`. It uses `session.verify`, timestamps, cursor search, `raisesBusy`, and ENOENT checking.

## Control Flow

`test_verify_ckpt` creates a table, sets stable timestamp, inserts data, expects verify to fail busy before checkpoint, checkpoints, then verifies successfully. `test_verify_search` searches an empty table for a missing key and verifies without checkpoint to ensure search did not dirty the btree. `test_verify_empty` verifies a nonexistent URI and expects ENOENT.

## State and Persistence Behavior

The tests focus on in-memory dirty state versus checkpoint-clean state. Stable timestamp is set before operations to satisfy timestamped-table expectations.

## Dependencies and Integration Points

Depends on `WT_SESSION.verify`, checkpoint dirty-clean transitions, cursor search behavior on deleted empty pages, and Python exception helpers.

## Risks and Edge Cases

It is API-only and does not cover utility behavior. The busy expectation depends on verify refusing dirty content.

## Test Signals

Signals are EBUSY before checkpoint, success after checkpoint, success after empty search without checkpoint, and ENOENT for missing object.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_verify2.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_verify_disagg.py -->
# sources/storage-engines/wiredtiger/test/suite/test_verify_disagg.py

## Purpose

`test_verify_disagg.py` verifies `SESSION.verify` semantics for disaggregated layered tables across leader and follower roles, including transient follower metadata/checkpoint states and history-store population.

## Important APIs, Types, and Functions

The disagg-decorated class uses scenarios for history-store fill and storage backends. Helpers include `leader_put_data`, `verify`, and `create_follower`; test methods cover normal leader/follower verify, missing leader table, follower without metadata, and follower without checkpoint.

## Control Flow

The main test creates a layered table on a leader, verifies empty state, creates a follower, checks ENOENT before checkpoint pickup, checkpoints and advances follower checkpoint, writes multiple timestamped generations, expects EBUSY for dirty leader data, checkpoints, advances the follower, and verifies both roles.

## State and Persistence Behavior

State spans leader/follower WiredTiger homes, disaggregated checkpoint metadata, layered stable/ingest components, optional history-store records, and timestamps.

## Dependencies and Integration Points

Depends on `helper_disagg` class decoration, generated disaggregated storage scenarios, `disagg_advance_checkpoint`, layered table block manager, timestamped commits, and verify's role-aware behavior.

## Risks and Edge Cases

Follower transient states are subtle: no metadata should return ENOENT, while a locally created layered URI without stable checkpoint should verify successfully by tolerating missing stable state. Dirty leader data must remain rejected.

## Test Signals

Signals are verify success/failure matching role and checkpoint state, ENOENT for missing metadata/table, EBUSY for dirty leader content, and successful follower verification after checkpoint advancement.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_verify_disagg.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_verify_disagg02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_verify_disagg02.py

## Purpose

`test_verify_disagg02.py` checks that verify detects duplicate btree IDs among stable files in disaggregated follower metadata.

## Important APIs, Types, and Functions

The disagg-decorated class defines leader/follower configs, layered table config, and `test_verify_duplicate_btree_ids`. It uses metadata cursors, raw access to `file:WiredTiger.wt`, regex validation, and `session.verify`.

## Control Flow

The test creates a layered table with data on the leader, checkpoints, opens a follower, advances the checkpoint, reads the stable file config to obtain an `id=...`, inserts a fake metadata key with the same config through the raw metadata file, runs verify expecting `WT_ERROR`, ignores expected metadata-corruption stderr, removes the fake entry, and closes the follower.

## State and Persistence Behavior

It deliberately corrupts follower local metadata by adding `file:fake_duplicate.wt_stable`, then cleans it up so teardown does not fail.

## Dependencies and Integration Points

Depends on disaggregated storage helpers, follower checkpoint advancement, metadata layout for stable files, raw metadata file cursor access, and verify's unique btree ID check.

## Risks and Edge Cases

The test reaches below normal metadata APIs, so metadata schema changes can affect it. Cleanup is required to keep later teardown verification healthy.

## Test Signals

Signals are a valid victim config with `id=`, verify raising `WT_ERROR`, and expected metadata corruption diagnostics.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_verify_disagg02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_verify_disagg03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_verify_disagg03.py

## Purpose

`test_verify_disagg03.py` verifies that opening a disaggregated follower with `verify_metadata=true` succeeds when checkpointed data includes later timestamped deletions of earlier writes.

## Important APIs, Types, and Functions

The class uses disaggregated storage scenarios, leader config, layered URI/table config, and `test_verify_metadata_follower_with_deletions`. It calls `disagg_get_complete_checkpoint_meta`, `conn.reconfigure`, `close_conn`, and `open_conn`.

## Control Flow

The test creates a layered table, writes all keys at timestamp 5 and checkpoints, overwrites them at timestamp 10 and checkpoints, deletes every other key at timestamp 15 and checkpoints, captures checkpoint metadata, reconfigures the connection from leader to follower to avoid shutdown checkpoint modification, closes it, and reopens as follower with `verify_metadata=true`.

## State and Persistence Behavior

The important state is checkpointed layered data containing multi-version keys and tombstones. The final follower open must be read-only with supplied checkpoint metadata.

## Dependencies and Integration Points

Depends on disaggregated helper fixtures, timestamped transactions, checkpoint metadata export, follower role configuration, and metadata verification at connection open.

## Risks and Edge Cases

The test covers a specific deletion-after-write pattern. It assumes stepping down before close prevents unwanted shutdown checkpoint changes.

## Test Signals

The primary signal is successful follower reopen with `verify_metadata=true`; any metadata verification error fails the test.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_verify_disagg03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_version.py -->
# sources/storage-engines/wiredtiger/test/suite/test_version.py

## Purpose

`test_version.py` is a connection/API smoke test for `wiredtiger.wiredtiger_version()`. It belongs to the connection API test group.

## Important APIs, Types, and Functions

The class `test_version` has a single `test_version` method that calls `wiredtiger.wiredtiger_version()`.

## Control Flow

The test obtains the version tuple/string data from the Python binding. The file is minimal; its main value is exercising the binding entry point under the suite harness.

## State and Persistence Behavior

No database state is created or persisted by this test.

## Dependencies and Integration Points

Depends on the WiredTiger Python extension exporting `wiredtiger_version` and the base `wttest.WiredTigerTestCase` setup.

## Risks and Edge Cases

The test appears incomplete in the visible source: it stores the returned version but has no explicit assertion in the shown method body, so it mainly detects call failure/import failure.

## Test Signals

The signal is successful execution of the version call without exception.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_version.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/syscall/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/syscall/CMakeLists.txt

## Purpose

This CMake file builds and registers the WiredTiger syscall trace test suite. It creates the base executable used by `.run` trace specifications and registers `syscall.py` as a CTest test.

## Important APIs, Types, and Functions

It calls `create_test_executable(test_wt2336_base SOURCES wt2336_base/main.c ADDITIONAL_FILES syscall.py ADDITIONAL_DIRECTORIES wt2336_base)`, `add_test(NAME test_syscall COMMAND python3 .../syscall.py)`, and sets `SKIP_RETURN_CODE 3`.

## Control Flow

At configure/build time, CMake builds the executable and copies the runner and test directory. At test time, CTest invokes the Python runner, which discovers `.run` files and compares system-call traces.

## State and Persistence Behavior

The build tree receives the executable, copied runner, and copied syscall test directories. Runtime scratch directories are managed by `syscall.py`.

## Dependencies and Integration Points

Integrates with WiredTiger's custom `create_test_executable` helper, CTest, Python 3, and environment-error skip semantics from the runner.

## Risks and Edge Cases

The skip return code is significant: runner exit code 3 is treated as an environment skip, not failure. Missing copied files or mismatched executable naming would prevent discovery.

## Test Signals

Signals are successful build of `test_wt2336_base` and a CTest `test_syscall` result of pass or skip-on-environment.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/syscall/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/syscall/syscall.py -->
# sources/storage-engines/wiredtiger/test/syscall/syscall.py

## Purpose

`syscall.py` is the command-line runner for WiredTiger syscall durability tests. It runs test executables under `strace` on Linux or `dtruss` on Darwin and compares captured system calls with preprocessed `.run` templates.

## Important APIs, Types, and Functions

Major types are `VariableContext`, `TestReturnCode`, `FileLine`, `Reader`, `FileReader`, `PreprocessedReader`, `HeadOpts`, `Runner`, and `SyscallCommand`. Important functions include `simplify_path`, `printfile`, `Runner.init`, `Runner.run`, `Runner.match_lines`, `Runner.match`, `Runner.call_compare`, argument/expression matching helpers, and `SyscallCommand.build_system_defines`.

## Control Flow

The script locates a usable WiredTiger build, parses CLI options, probes system macro values by compiling a small C program, discovers `.run` files, preprocesses each run file with `cc -E`, reads `SYSTEM`, `TRACE`, and `RUN` headers, runs the target executable under the tracer, and linearly matches trace output with fuzzy `...`, variable binding, `ASSERT_*`, and `OUTPUT` expectations.

## State and Persistence Behavior

It creates `WT_TEST.*` execution directories under the build syscall tree, writes stdout/stderr traces, optionally preserves failed or requested runs, and deletes successful scratch directories unless `--preserve` is set. It also temporarily creates `syscall_probe.c` and `syscall_probe`.

## Dependencies and Integration Points

Depends on `strace`, `dtruss`, `cc`, WiredTiger generated headers, `.run` files, CTest skip code 3 for environment issues, and built executables named `test_<directory>`.

## Risks and Edge Cases

Trace output is platform- and libc-sensitive, so templates need fuzzy matching. The `str_match` fuzzy branch appears to compare `s2.startswith(s2)`, which is tautological and may weaken matching for right-fuzzy strings. Environment issues such as macOS SIP are converted to skip.

## Test Signals

Signals include successful macro probe, successful target run, empty target stdout unless `OUTPUT` is expected, complete trace/template match, and preserved diagnostics on failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/syscall/syscall.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/syscall/wt2336_base/main.c -->
# sources/storage-engines/wiredtiger/test/syscall/wt2336_base/main.c

## Purpose

`wt2336_base/main.c` is a small syscall-test executable for WT-2336-style file-operation tracing. It performs a predictable sequence of WiredTiger API calls with marker output to stderr.

## Important APIs, Types, and Functions

It defines `fail(int ret)` and `main`. `main` calls `wiredtiger_open`, `WT_CONNECTION.open_session`, `WT_SESSION.create`, `WT_SESSION.drop`, and `WT_CONNECTION.close`. It uses `SEPARATOR` marker strings.

## Control Flow

The program prints marker lines before each major API operation, sleeps briefly to improve trace separation, opens a database with statistics logging, creates and drops `table:hello`, closes the connection, and exits. Any nonzero WiredTiger return calls `fail`.

## State and Persistence Behavior

It creates a WiredTiger home in the current directory, creates then drops a table, and leaves normal WiredTiger metadata/log/statistics artifacts for the syscall trace.

## Dependencies and Integration Points

Depends on `wt_internal.h`, WiredTiger C API, POSIX `usleep`, and the syscall runner matching stderr markers with expected syscalls.

## Risks and Edge Cases

The TODO comments indicate sparse in-source documentation. Trace timing and marker flushing are important; missing flushes could make comparisons harder.

## Test Signals

Signals are stderr separators interleaved with traced open/create/drop/close syscalls and zero process exit.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/syscall/wt2336_base/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/thread/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/thread/CMakeLists.txt

## Purpose

This CMake file builds the WiredTiger threaded stress smoke-test executable and registers it with CTest.

## Important APIs, Types, and Functions

It calls `create_test_executable(test_thread SOURCES file.c rw.c stats.c t.c EXECUTABLE_NAME "t" ADDITIONAL_FILES smoke.sh)`, then registers `add_test(NAME test_thread COMMAND .../smoke.sh)` and labels it `check`.

## Control Flow

CMake builds the multi-source executable as `t`, copies `smoke.sh`, and CTest invokes the shell script, which runs row and variable table stress variants.

## State and Persistence Behavior

Build state is the `t` binary and copied smoke script. Runtime database directories are created by the executable.

## Dependencies and Integration Points

Integrates with the test utility library, CTest, the custom executable helper, and `smoke.sh` assumptions about the binary name.

## Risks and Edge Cases

The explicit executable name is part of the shell contract. Renaming without updating `smoke.sh` breaks the test.

## Test Signals

Signals are successful binary build and CTest execution of the four smoke commands in `smoke.sh`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/thread/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/thread/file.c -->
# sources/storage-engines/wiredtiger/test/thread/file.c

## Purpose

`file.c` provides table/file creation and initial bulk-load support for the `test/thread` stress executable.

## Important APIs, Types, and Functions

It defines static `file_create(const char *name)` and exported `load(const char *name)`. It uses global `conn`, `ftype`, and `nkeys` from `thread.h`.

## Control Flow

`file_create` opens a session, builds a row-store (`key_format=u`) or variable-record (`key_format=r`) create config with page-size settings, creates the object tolerating `EEXIST`, and closes the session. `load` calls `file_create`, opens a bulk cursor, iterates keys from 1 to `nkeys`, formats row-store keys as zero-padded byte strings or record-number keys, formats values, inserts them, and closes the session.

## State and Persistence Behavior

It creates and populates WiredTiger file objects named by callers, usually `file:wt.%03d`. Bulk-load data forms the starting state for concurrent readers/writers.

## Dependencies and Integration Points

Depends on `thread.h`, global test options, WiredTiger sessions/cursors, `testutil_snprintf_len_set`, and `testutil_check`.

## Risks and Edge Cases

The code assumes a global open connection. Bulk cursor failure or duplicate object handling is fatal except `EEXIST` during create.

## Test Signals

Signals are successful creation, full initial load of `nkeys`, and later verification by `rw_start`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/thread/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/thread/rw.c -->
# sources/storage-engines/wiredtiger/test/thread/rw.c

## Purpose

`rw.c` drives concurrent read/write operations for the thread stress test. It allocates per-thread state, starts reader and writer threads, verifies resulting files, and prints operation counts.

## Important APIs, Types, and Functions

Key types/functions are `INFO`, `rw_start`, `reader_op`, `reader`, `writer_op`, `writer`, and `print_stats`. It uses WiredTiger sessions/cursors, random state, thread helpers, and global options such as `multiple_files`, `session_per_op`, `vary_nops`, `max_nops`, and `log_print`.

## Control Flow

`rw_start` prepares writer and reader `INFO` entries, creates/loads files, starts reader and writer threads, joins them, reports throughput, verifies each file, prints stats, and frees allocations. Reader threads search random keys; writer threads remove keys divisible by five and update others. Each thread either reuses one session/cursor or opens a session per operation.

## State and Persistence Behavior

State includes shared `run_info`, per-thread random generators and counters, table data mutated by concurrent removes/updates, optional log records, and final verified WiredTiger files.

## Dependencies and Integration Points

Depends on `thread.h`, `load`, `testutil_verify`, WiredTiger thread wrappers, random helpers, and global connection `conn`.

## Risks and Edge Cases

The throughput calculation multiplies `(readers + writers) * total_nops`, although `total_nops` already sums thread operations, which may overstate ops/sec. Concurrent remove of absent keys tolerates `WT_NOTFOUND`.

## Test Signals

Signals are all threads start/stop, no unexpected cursor errors, final verify succeeds, and per-thread read/remove/update counts are printed.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/thread/rw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/thread/smoke.sh -->
# sources/storage-engines/wiredtiger/test/thread/smoke.sh

## Purpose

`smoke.sh` is the CTest smoke driver for the thread stress executable.

## Important APIs, Types, and Functions

It is a POSIX shell script with `set -e` and four `$TEST_WRAPPER ./t ...` invocations.

## Control Flow

The script runs row-store mode, row-store mode with per-operation sessions and multiple files, variable-record mode, and variable-record mode with per-operation sessions and multiple files. Any command failure stops the script.

## State and Persistence Behavior

Each `t` invocation creates and removes its own WiredTiger work directory according to executable defaults.

## Dependencies and Integration Points

Depends on the built binary being named `t`, optional `TEST_WRAPPER`, and command-line options implemented by `t.c`.

## Risks and Edge Cases

It is intentionally small and only exercises reduced operation counts for the `-S -F -n 1000` variants. Environment must provide `TEST_WRAPPER` or allow it to expand empty.

## Test Signals

Signals are zero exit from all four stress invocations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/thread/smoke.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/thread/stats.c -->
# sources/storage-engines/wiredtiger/test/thread/stats.c

## Purpose

`stats.c` dumps connection and file statistics for the thread stress executable after each run.

## Important APIs, Types, and Functions

It defines `stats(void)`, opens `statistics:` and optionally `statistics:file:wt.000`, and writes `desc=pval` pairs to `__stats`.

## Control Flow

The function opens a session, creates the stats output file, scans the connection statistics cursor until `WT_NOTFOUND`, closes it, then if not in multiple-file mode scans file statistics for `FNAME` index 0 and closes the session/file.

## State and Persistence Behavior

The persistent output is `__stats`, overwritten with current statistic descriptions and printable values. It reads live statistics from the WiredTiger connection.

## Dependencies and Integration Points

Depends on `thread.h`, global `conn` and `multiple_files`, WiredTiger statistics cursors, and test utility error handling.

## Risks and Edge Cases

In multiple-file mode, it closes the output file but does not close the session in the visible control path, which may be a resource leak. It only emits file stats for single-file runs.

## Test Signals

Signals are successful cursor scans and a populated `__stats` file.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/thread/stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/thread/t.c -->
# sources/storage-engines/wiredtiger/test/thread/t.c

## Purpose

`t.c` is the main program for the WiredTiger thread stress test. It parses options, creates a test home, opens a connection, runs concurrent readers/writers, dumps stats, and shuts down cleanly.

## Important APIs, Types, and Functions

It defines global options/connection state plus `main`, `wt_connect`, `wt_shutdown`, `shutdown`, `handle_error`, `handle_message`, `onint`, and `usage`. It uses `__wt_getopt`, `testutil_work_dir_from_path`, `testutil_recreate_dir`, `wiredtiger_open`, `rw_start`, and `stats`.

## Control Flow

`main` initializes defaults, parses flags for config, multiple files, keys, logging, operation count, reader/writer counts, runs, per-operation sessions, file type, and varying ops. For each run it removes previous state, opens WiredTiger with statistics logging and event handler, starts read/write workload, writes stats, checkpoints and closes the connection.

## State and Persistence Behavior

State includes global configuration, the work directory, optional log file, connection statistics log on close, table data from workload, and cleanup on SIGINT or next run.

## Dependencies and Integration Points

Depends on `thread.h`, test utility work-directory/file helpers, event-handler callbacks, `rw_start`, `stats`, and WiredTiger connection/session APIs.

## Risks and Edge Cases

`vary_nops` is only allowed with multiple files. Signal cleanup removes the work directory. Event messages go to either the configured log file or stdout.

## Test Signals

Signals are process/run banners, successful workload completion, stats output, checkpoint on shutdown, and zero exit.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/thread/t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/thread/thread.h -->
# sources/storage-engines/wiredtiger/test/thread/thread.h

## Purpose

`thread.h` is the shared header for the thread stress executable. It centralizes file-name constants, global option declarations, file type enum, and cross-file function prototypes.

## Important APIs, Types, and Functions

It defines `FNAME`, `FNAME_STAT`, enum `__ftype { ROW, VAR }`, extern globals `conn`, `ftype`, `log_print`, `multiple_files`, `nkeys`, `max_nops`, `vary_nops`, `session_per_op`, and prototypes `load`, `rw_start`, and `stats`.

## Control Flow

There is no runtime flow in the header; it provides the compile-time contract among `t.c`, `file.c`, `rw.c`, and `stats.c`.

## State and Persistence Behavior

The declared globals carry process-wide runtime state. Constants name persistent WiredTiger files and the stats output file.

## Dependencies and Integration Points

Depends on `test_util.h` and `<signal.h>`, and is included by all thread-test implementation files.

## Risks and Edge Cases

Global mutable state keeps the small harness simple but couples all implementation files and makes concurrent multiple harness instances inside one process impossible.

## Test Signals

Compile-time signals are successful cross-file linkage and consistent option state across the stress harness.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/thread/thread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/utility/CMakeLists.txt

## Purpose

This CMake file builds the shared `test_util` static library used by WiredTiger C tests.

## Important APIs, Types, and Functions

It defines the `sources` list (`backup.c`, `disagg.c`, `file.c`, `lazyfs.c`, `misc.c`, `parse_opts.c`, `thread.c`, `tiered.c`, `util_modify.c`, `util_random.c`), creates `add_library(test_util STATIC ...)`, enables position-independent code, adds public include directories, links `wt::wiredtiger`, and conditionally includes/links Windows shims.

## Control Flow

At configure/build time, CMake assembles the static library and applies diagnostic compile flags. Consumers link test helper APIs through this target.

## State and Persistence Behavior

Build artifacts include `libtest_util` and propagated include paths. No runtime state is created by the CMake file itself.

## Dependencies and Integration Points

Integrates with the WiredTiger target, generated include/config directories, source include tree, Windows test support, and compiler diagnostic settings.

## Risks and Edge Cases

Adding helper source files requires updating this list. Include-directory order affects whether generated headers are found before source headers.

## Test Signals

Signals are successful compilation/linking of `test_util` and downstream tests resolving helper symbols.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/backup.c -->
# sources/storage-engines/wiredtiger/test/utility/backup.c

## Purpose

`backup.c` implements test helper routines for full and incremental backups, backup cleanup, backup ID discovery, and simple file copy into backup directories.

## Important APIs, Types, and Functions

Exports include `testutil_backup_create_full`, `testutil_backup_create_incremental`, `testutil_backup_force_stop`, `testutil_backup_force_stop_conn`, `testutil_last_backup_id`, `testutil_delete_old_backups`, `testutil_create_backup_directory`, and `testutil_copy_file`. Internal helper `__int_comparator` supports sorting backup IDs.

## Control Flow

Full backup creates `BACKUP_BASE<id>`, opens a backup cursor with incremental metadata enabled, copies each listed file, closes resources, and writes `full` and `done` sentinels. Incremental backup opens a source/destination incremental cursor, copies full files or changed ranges over a base copy, hard-links unchanged files on Unix, and writes `done`.

## State and Persistence Behavior

It creates, removes, renames, hard-links, and writes backup directories/files. Sentinel files mark full backups and completed backups; incomplete backup directories are removed by cleanup.

## Dependencies and Integration Points

Depends on WiredTiger backup cursors, `WT_BACKUP_FILE`/`WT_BACKUP_RANGE`, POSIX file I/O, `testutil_copy`, `testutil_exists`, `testutil_remove`, and backup naming macros from `test_util.h`.

## Risks and Edge Cases

Incremental range copying allocates a buffer sized to each range, which can be large. File descriptors use `> 0` checks, so descriptor 0 would not be closed, although normal opens here usually return higher descriptors. Cleanup keeps the latest full backup while deleting older excess backups.

## Test Signals

Signals include expected file/range counts, `done` sentinels, force-stop rejecting `backup:query_id`, and retained backup directory consistency.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/backup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/disagg.c -->
# sources/storage-engines/wiredtiger/test/utility/disagg.c

## Purpose

`disagg.c` provides C test helpers for disaggregated-storage configuration and failure-time preservation of layered table components.

## Important APIs, Types, and Functions

Exports are `testutil_disagg_storage_configuration` and `testutil_disagg_preserve`. Internal `preserve_copy_uri` copies raw records from one URI to another, optionally under a read timestamp. `LAYERED_PREFIX` identifies layered table metadata entries.

## Control Flow

Configuration helper fills extension and connection config strings when disagg is enabled, optionally appending key-provider extension config; otherwise it emits empty config. Preserve helper opens source sessions plus a destination WiredTiger home under a subdirectory, copies metadata, iterates layered metadata URIs, and copies ingest, stable, and layered views into regular preserve tables before checkpointing and closing the destination.

## State and Persistence Behavior

It writes config strings into caller buffers and creates a separate preserved WiredTiger database containing copied metadata and table contents. Timestamped reads can snapshot data at a divergence point.

## Dependencies and Integration Points

Depends on `TEST_OPTS`, testutil environment config macros, WiredTiger raw cursors, timestamp transactions, layered URI naming conventions, and `testutil_format_item`.

## Risks and Edge Cases

Missing component files are logged and skipped, not fatal. Destination table names avoid `.wt_ingest` and `.wt_stable` substrings because WiredTiger treats those specially.

## Test Signals

Signals are correctly formed disagg extension/connection configs and preserved metadata/ingest/stable/layered tables in the destination home after failure handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/disagg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/file.c -->
# sources/storage-engines/wiredtiger/test/utility/file.c

## Purpose

`file.c` is the shared filesystem helper implementation for WiredTiger tests. It provides recursive copy, fast copy, move, mkdir, recursive remove, existence checks, and sentinel file creation across Unix and Windows.

## Important APIs, Types, and Functions

Internal types are `file_info_t`, `file_callback_t`, and `copy_data`. Internal workers include `process_directory_tree`, `copy_on_file`, `copy_on_directory_enter`, `copy_on_directory_leave`, `remove_on_file`, and `remove_on_directory_leave`. Exports include `testutil_copy`, `testutil_copy_fast`, `testutil_move`, `testutil_copy_ext`, `testutil_mkdir`, `testutil_mkdir_ext`, `testutil_recreate_dir`, `testutil_remove`, `testutil_exists`, and `testutil_sentinel`.

## Control Flow

The core traversal function recursively stats/list directories and invokes callbacks for files and directory entry/leave. Copy helpers expand glob patterns, create destination directories when needed, copy regular files with buffered `pread`/`write` or Windows `CopyFileA`, optionally preserve timestamps, and optionally hard-link subtrees. Remove helpers traverse leaves before directories.

## State and Persistence Behavior

The file manipulates real filesystem state: copied trees, hard links, timestamps, created directories, removed paths, and empty sentinel files. It treats missing paths as acceptable for glob-style remove/copy no-match cases where configured.

## Dependencies and Integration Points

Depends on `test_util.h`, POSIX/Windows filesystem APIs, `glob`, `dirname`/`basename`, `utime`/`utimes`, process helpers for `cp`, and testutil assertion/error wrappers.

## Risks and Edge Cases

Only regular files are copied; special files are silently ignored. `testutil_copy_fast` shells out to `cp -R -p` on Unix, so behavior depends on system `cp`. Hard-link mode tracks depth based on matching prefixes and can share storage unexpectedly if misused.

## Test Signals

Signals are exact copied/removable directory trees, preserved timestamps when requested, successful recursive parent creation, ENOENT-safe existence checks, and sentinel file presence.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/lazyfs.c -->
# sources/storage-engines/wiredtiger/test/utility/lazyfs.c

## Purpose

`lazyfs.c` integrates tests with LazyFS, a Linux FUSE filesystem used to inject/cache filesystem behavior. It can locate LazyFS, create its config, mount/unmount it, send control commands, and set up/clean up a LazyFS-backed WiredTiger home.

## Important APIs, Types, and Functions

Functions include `lazyfs_is_implicitly_enabled`, `lazyfs_init`, `lazyfs_create_config`, `lazyfs_mount`, `lazyfs_unmount`, `lazyfs_command`, `lazyfs_clear_cache`, `lazyfs_display_cache_usage`, `testutil_lazyfs_setup`, `testutil_lazyfs_clear_cache`, and `testutil_lazyfs_cleanup`.

## Control Flow

Setup initializes LazyFS path relative to the current executable, canonicalizes the test home, creates a base directory, creates a temporary control FIFO path under `/tmp`, writes LazyFS config, and forks/execls LazyFS with a subdir module. The parent waits until the mount point is mounted. Cleanup unmounts through LazyFS scripts, waits for the child, and removes control/mount paths.

## State and Persistence Behavior

State lives in `WT_LAZY_FS` path fields, the LazyFS config/log/control files, the base backing directory, the mount point, and child process PID. Control commands write `lazyfs::<command>` lines to the control file.

## Dependencies and Integration Points

Linux-only paths depend on `/proc/self/exe`, `prctl(PR_SET_PDEATHSIG)`, fork/exec/wait, `is_mounted`, `testutil_system`, LazyFS build layout, and constants from `test_util.h`.

## Risks and Edge Cases

Non-Linux functions fail with ENOENT. Mounting requires LazyFS to be built at the expected relative path and may need FUSE permissions such as `allow_other`. The child kills the parent on setup errors to avoid orphaned mounts.

## Test Signals

Signals are successful mount detection, working cache control commands, LazyFS log/config creation, and clean unmount/removal during cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/lazyfs.c -->
