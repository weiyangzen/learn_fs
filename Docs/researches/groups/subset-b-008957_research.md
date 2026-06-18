# subset-b-008957 research

Grouped research report for the WiredTiger strict CMake helpers, examples, and collator extension files in subset B. Each file section is delimited for deterministic source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/strict/strict_flags_helpers.cmake -->
# sources/storage-engines/wiredtiger/cmake/strict/strict_flags_helpers.cmake

Purpose: defines CMake helper functions that centralize strict compiler diagnostic flags for WiredTiger builds. `get_gnu_base_flags`, `get_clang_base_flags`, and `get_cl_base_flags` parse exactly one language selector (`C` or `CXX`), choose the matching CMake compiler version variable, build a list of warning/error flags, and return it through a parent-scope output variable.

Important APIs and control flow: each function uses `cmake_parse_arguments(PARSE_ARGV ...)`, rejects unknown arguments, rejects simultaneous C and CXX selection, and emits `message(FATAL_ERROR)` on missing language. GNU flags include `-Werror` plus version-gated warnings from GCC 5 through 8, with selected `-Wno-*` relaxations. Clang flags mostly suppress diagnostics incompatible with existing WiredTiger code or platforms, with Darwin-specific and version-specific exceptions. MSVC uses `/WX`, `/we4100`, and `/GS`.

State and dependencies: no persistent state is written. Integration depends on `CMAKE_C_COMPILER_VERSION`, `CMAKE_CXX_COMPILER_VERSION`, `WT_DARWIN`, and consumers applying the returned flag list, typically through diagnostic CMake variables.

Risks: unquoted `if(${...})` conditions assume parse variables are always defined as boolean-like strings. Compiler version comparisons can silently skip flags for vendor-specific version schemes. Relaxations such as reserved identifier suppressions are intentional technical debt tied to WT-11788.

Test signals: configure-time failure paths catch malformed helper use. Build matrix coverage across GCC, Clang, Apple Clang, Darwin, and MSVC is the meaningful validation signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/strict/strict_flags_helpers.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/examples/CMakeLists.txt

Purpose: wires the example subtree into the build and preserves legacy executable layout expected by some examples.

Important APIs and control flow: `add_subdirectory(c)` delegates C example target creation. `add_custom_command(OUTPUT wt ...)` copies `$<TARGET_FILE:wt>` into `${CMAKE_CURRENT_BINARY_DIR}/wt`, and `add_custom_target(sym_wt_examples ALL ...)` makes the copy part of the default build.

State and persistence: writes a copied `wt` binary in the examples binary directory. No source state is modified.

Dependencies and integration: depends on the `wt` target and CMake generator expressions. This is specifically integrated with examples, such as backup/log examples, that run `../../wt` relative to their own binary directory to match the historical autoconf layout.

Risks: if the target file path or relative runtime layout changes, examples using hard-coded `../../wt` can fail even when compilation succeeds. The custom command output name `wt` can collide with generated files in the same binary directory if layout changes.

Test signals: building the `sym_wt_examples` target and running examples that invoke `../../wt` verifies both the copy and relative path compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/examples/c/CMakeLists.txt

Purpose: declares the C example programs as build/test targets using the repository's `define_c_test` helper.

Important APIs and control flow: each example target maps one source file to a test directory and passes `-h $<SHELL_PATH:$<TARGET_FILE_DIR:target>/WT_HOME>` so the program uses a per-target home. POSIX-only examples (`ex_backup`, `ex_log`, `ex_smoke`) declare `DEPENDS "WT_POSIX"`. Non-MSVC builds link `ex_encrypt` and `ex_file_system` with `-rdynamic` so local extension entry points can be resolved at runtime.

State and persistence: generated tests create WT_HOME directories under their target binary folders and may create additional test directories during execution. The CMake file itself stores no runtime state.

Dependencies and integration: depends on the test helper macro, target generator expressions, WiredTiger libraries, and platform feature variable `WT_POSIX`. `-rdynamic` is an integration requirement for examples using `extensions=(local=...)`.

Risks: adding a new local-extension example without `-rdynamic` on ELF platforms can produce runtime extension lookup failures. POSIX gating must stay aligned with code using shell utilities, file descriptors, or POSIX threading.

Test signals: CMake configuration should enumerate all targets, and `ctest`/example execution validates per-target home isolation and platform gating.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_access.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_access.c

Purpose: minimal C walkthrough for creating and reading a string-key/string-value table.

Important APIs and control flow: `main` obtains a home directory via `example_setup`, then calls `access_example`. The example opens a connection with `wiredtiger_open(home, NULL, "create,statistics=(all)", &conn)`, opens a session, creates `table:access` with `key_format=S,value_format=S`, opens a cursor, inserts `key1/value1`, resets the cursor, scans with `next`, reads with `get_key`/`get_value`, and closes the connection.

State and persistence: persists one table and one record under the configured WT_HOME. Cursor state is reset before scanning, and connection close implicitly closes session/cursor handles.

Dependencies and integration: depends on `test_util.h` helpers (`example_setup`, `error_check`, `scan_end_check`) and the public WiredTiger C API. Snippet markers feed documentation extraction.

Risks: intentionally simple error behavior exits through `error_check`; it is not an example of recovery from failures. The table name overlaps with statistics examples but per-test home isolation prevents conflicts.

Test signals: target execution should print `Got record: key1 : value1` and terminate after `WT_NOTFOUND`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_all.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_all.c

Purpose: broad API sampler used to populate WiredTiger API reference snippets and to compile/run representative calls across connection, session, cursor, transaction, statistics, packing, checkpoint, extension, checksum, and version APIs.

Important APIs and control flow: `main` opens a logged, statistical connection, then `connection_ops` registers a sample collator, reconfigures eviction, validates configuration, configures method-specific options, opens a session, and closes the connection. `session_ops` creates/drops tables with multiple storage options, alters/compacts/salvages/truncates/verifies, checkpoints, and delegates to `cursor_ops`, `cursor_statistics`, `pack_ops`, and `transaction_ops`. Cursor examples cover metadata/statistics cursors, duplicate cursors, overwrite configuration, named checkpoints, comparison/equality, append record numbers, reserve, modify, update, remove, and error reporting. Transaction examples cover commit/rollback, isolation, prepare/commit timestamps, reset_snapshot, pinned range, timestamp setters, query_timestamp, and rollback_to_stable.

State and persistence: creates many temporary tables in WT_HOME, writes records, checkpoints, changes connection/session settings, registers an in-process collator, and manipulates timestamps. Several documentation-only extension/compression examples are excluded by `MIGHT_NOT_RUN`.

Dependencies and integration: depends on public WiredTiger APIs, `test_util.h`, documentation snippet markers, and the `wt` build environment. The collator and method-configuration snippets show extension integration patterns.

Risks: because it is a snippet aggregator, call ordering is fragile; earlier table creation and inserted keys are prerequisites for later cursor operations. Some examples intentionally reference nonportable paths or unavailable extensions behind preprocessor guards. Timestamp examples require valid transaction sequencing.

Test signals: successful execution without assertion validates that documented snippets remain compileable and mostly runnable. Documentation extraction should preserve all `/*! [...] */` regions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_all.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_backup.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_backup.c

Purpose: integration example for full and block-based incremental backup with logging enabled.

Important APIs and control flow: global constants define the source home, backup homes, log path, output dumps, table URIs, and ID range. `setup_directories` prepares full and incremental backup directories. `add_work` inserts batches into `table:main` and, on even iterations, `table:extra`. `take_full_backup` opens `backup:` with either full or initial incremental configuration, copies listed files, and tracks file lists. `take_incr_backup` queries existing IDs via `backup:query_id`, opens `backup:` with `incremental=(src_id,this_id[,consolidate])`, duplicates the cursor per file with `incremental=(file=...)`, and applies whole-file or range copies using `open`, `lseek`, `read`, and `write`. `compare_backups` shells out to `../../wt -R ... dump main` and `cmp`.

State and persistence: creates WT_BLOCK, per-iteration full/incremental homes, log directories, dump outputs, persistent incremental backup ID metadata, and file-list memory state. It verifies ID persistence across close/reopen and then uses `force_stop=true` to remove incremental metadata.

Dependencies and integration: requires POSIX shell utilities and file APIs, the copied `../../wt` binary, logging, checkpoints, and backup cursors.

Risks: path assumptions and shell commands are platform-sensitive. File list removal uses broad `rm WT_BLOCK_LOG_*` patterns. Range-copy correctness depends on offsets, sizes, and descriptor lifecycle.

Test signals: every iteration must compare full and incremental dumps as identical; final reopen must fail to open incremental backup after forced stop and `WiredTiger.backup.block` must be absent.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_backup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_call_center.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_call_center.c

Purpose: maps a moderate SQL-style customer/call schema into WiredTiger tables, column groups, and indexes.

Important APIs and control flow: declares `CUSTOMER` and `CALL` structs, opens a connection/session, creates `table:customers` with record-number keys, named columns, and `main`/`address` column groups, then creates `index:customers:phone`. It appends sample customers. It creates `table:calls` with composite value fields and `index:calls:cust_date` on `(cust_id,call_date)`, then appends calls. Query one opens `index:customers:phone(id,name)` and searches by phone. Query two opens `index:calls:cust_date(cust_id,call_type,notes)`, uses `search_near` with `(cust_id + 1, 0)`, possibly backs up, then scans previous records to emulate `ORDER BY call_date DESC LIMIT 3`.

State and persistence: persists two tables, two indexes, customer column groups, and sample rows. Cursor position and `exact` from `search_near` drive reverse index traversal.

Dependencies and integration: uses WiredTiger schema projection syntax and `test_util.h`. Demonstrates SQL-to-WiredTiger modeling for documentation.

Risks: assumes sample customer IDs generated by append start at 1. Reverse traversal must stop when `cust_id` changes; otherwise adjacent customers could be printed.

Test signals: output should include the customer lookup and up to three recent call records for customer 1.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_call_center.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_col_store.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_col_store.c

Purpose: demonstrates column-store tables, column groups, indexes, updates, removals, projections, and basic analytics over synthetic weather data.

Important APIs and control flow: defines `WEATHER` with numeric and fixed-string fields. `main` creates `table:weather` with record-number keys, a structured value format, named columns, and several column groups. It generates 100 random records, appends them, prints all rows through a projected table cursor, creates hour and country indexes, calculates min/max temperature over a time range, converts temperatures through the `colgroup:weather:temperature` cursor, recalculates min/max, computes per-country averages through `index:weather:country`, removes Australian rows through the location column group, and recomputes averages.

State and persistence: persists weather rows split across column groups and maintains secondary indexes after creation. `generate_data` seeds from process ID, so content varies per run. Updates through a column group mutate the stored table values; deletes through a column group remove records.

Dependencies and integration: depends on `test_util.h`, standard C random/string/assert APIs, WiredTiger column group/index semantics, and `WT_MIN`/`WT_MAX`.

Risks: `average_data` divides by `count` without guarding zero after a successful initial search; if search finds a country key but later filtering yields zero, this would fail. Random data makes output nondeterministic. Fixed string widths require countries/days to fit.

Test signals: successful scans should terminate with `WT_NOTFOUND`, temperature conversion should update values, and averages after `remove_country` should no longer include AUS records.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_col_store.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_config_parse.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_config_parse.c

Purpose: demonstrates standalone parsing of WiredTiger-compatible configuration strings.

Important APIs and control flow: `main` opens a `WT_CONFIG_PARSER` over a constant configuration string with `wiredtiger_config_parser_open`. It demonstrates parser creation/close, `parser->get` for `page_size`, `parser->next` iteration over top-level keys, dot-shorthand lookup of nested `log.file_max`, and nested traversal by opening a sub-parser over a `WT_CONFIG_ITEM_STRUCT`.

State and persistence: no database is opened and no persistent state is written. Parser handles are opened and closed repeatedly around each snippet.

Dependencies and integration: uses `WT_CONFIG_ITEM`, `WT_CONFIG_PARSER`, `WT_CONFIG_ITEM_NUM`, `WT_CONFIG_ITEM_STRUCT`, `WT_NOTFOUND`, and `test_util.h`. It is useful for extension and tooling code that must parse the same syntax as WiredTiger APIs.

Risks: returned `WT_CONFIG_ITEM` string fields are length-delimited; the example prints with precision, which is correct. Any future config syntax changes should keep parser examples aligned.

Test signals: output should list top-level settings, print the converted `log file max`, enumerate nested log fields, and end parser loops with `WT_NOTFOUND`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_config_parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_cursor.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_cursor.c

Purpose: focused cursor API example covering scans, bounds, search/search_near, insert/update/remove, projections, statistics cursors, and debug version cursors.

Important APIs and control flow: helper functions operate on a passed `WT_CURSOR`: forward and reverse scans loop to `WT_NOTFOUND`, `cursor_bound` sets a lower bound, `cursor_search` and `cursor_search_near` show positioning semantics, and mutation helpers set key/value before insert/update/remove. `version_cursor_dump` opens a debug dump-version file cursor and extracts transaction/timestamp metadata fields. `main` opens a connection with fast stats, creates a projected `table:world`, opens table/projection/statistics cursors, then creates `table:map` and runs mutation and scan helpers before opening `file:map.wt` with `debug=(dump_version=(enabled=true))`.

State and persistence: creates `world` and `map` tables, inserts/removes/reinserts `foo`, and reads version metadata from the backing file. Cursor reset/positioning state is explicit between operations.

Dependencies and integration: depends on WiredTiger cursor ABI and debug cursor support. Uses `test_util.h` for setup and error handling.

Risks: version cursor field order is tightly coupled to WiredTiger debug cursor value format. `cursor_bound` is declared but not used in `main`, so bound behavior is compile-checked only if externally referenced.

Test signals: successful helper calls, scan termination at `WT_NOTFOUND`, and valid version cursor unpacking show cursor API compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_cursor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_data_source.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_data_source.c

Purpose: demonstrates how to register a custom `WT_DATA_SOURCE` and implement the data-source/cursor callback surfaces used by WiredTiger extensions.

Important APIs and control flow: `my_data_source_init` stores the `WT_EXTENSION_API`. Data source callbacks (`my_create`, `my_drop`, `my_open_cursor`, `my_rename`, `my_truncate`, `my_checkpoint`, etc.) mostly return success but illustrate extension calls. `my_create` demonstrates error/message printing, Windows error mapping, scratch allocation/free, and strerror. `MY_CURSOR` embeds `WT_CURSOR` first, and `my_open_cursor` allocates it, populates cursor method pointers, reads extension config values, resolves collator config, demonstrates metadata insert/remove/search/update, and returns the cursor. `main` registers `my_dsrc` under `dsrc:` and adds custom method configuration entries of boolean, int, string, and list types with validation.

State and persistence: registers an in-process data source and method configuration on the connection. Metadata examples mutate WiredTiger metadata records, though the demo sequence removes/searches/updates an illustrative key.

Dependencies and integration: depends on `wiredtiger_ext.h`, `WT_EXTENSION_API`, and the extension ABI requirement that public interface structs be the first field in custom structs.

Risks: many callbacks are stubs and not a durable data source. `my_open_cursor` may leak allocated cursor memory if later snippet calls fail. Metadata search after removal is demonstrative and would fail in real flow without surrounding state.

Test signals: compile/link coverage of all callback signatures and successful `add_data_source`/`configure_method` calls.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_data_source.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_encrypt.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_encrypt.c

Purpose: implements and exercises a local rotate-N encryptor extension, including encrypted logs, per-table encryption configuration, custom key IDs, and restart verification.

Important APIs and control flow: `MY_CRYPTO` embeds `WT_ENCRYPTOR` first and tracks rotation, calls, key ID, and password. `rotate_encrypt` reserves checksum/IV header space, copies input, applies `do_rotate`, writes fixed checksum/IV bytes, and reports expansion. `rotate_decrypt` strips header and reverses rotation. `rotate_sizing`, `rotate_customize`, and `rotate_terminate` implement sizing, per-object customization via `keyid`/`secretkey`, and cleanup. `add_my_encryptors` registers `rotn` through `connection->add_encryptor`. `main` opens with `extensions=[local=(entry=add_my_encryptors)]`, writes/read-walks encrypted log records, creates encrypted and unencrypted tables, verifies bad key ID failure, inserts identical rows into all tables, closes/reopens, and verifies decrypted table/log reads match.

State and persistence: persists encrypted table files and encrypted logs in WT_HOME. Customized encryptors hold allocated key/password strings until termination. Restart forces disk reads and decryption.

Dependencies and integration: requires `-rdynamic`/local extension symbol visibility, logging, WiredTiger encryption hooks, and `test_util.h`.

Risks: checksum and IV are fixed placeholders and not secure. `rotate_encrypt` sets `*result_lenp = dst_len` rather than the actual used `src_len + CHKSUM_LEN + IV_LEN`, acceptable only as demo behavior if buffers are sized exactly. Key management is illustrative.

Test signals: unknown key ID must fail, log cursor must find messages before and after restart, and all encrypted/unencrypted table cursors must return identical keys and values.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_encrypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_event_handler.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_event_handler.c

Purpose: demonstrates custom WiredTiger event handling for errors and messages.

Important APIs and control flow: `CUSTOM_EVENT_HANDLER` embeds `WT_EVENT_HANDLER` first and adds an `app_id`. `handle_wiredtiger_error` casts back to the custom type, prints app/session/error/message context, and exits on `WT_PANIC`. `handle_wiredtiger_message` prints app/session/message context. `config_event_handler` initializes callback pointers, leaves unsupported callbacks as `NULL`, opens WiredTiger with the handler, deliberately calls `open_session` with invalid isolation to trigger error handling, and closes the connection.

State and persistence: creates a WT_HOME connection but the main purpose is callback behavior; no table data is persisted.

Dependencies and integration: uses the public `WT_EVENT_HANDLER` callback ABI and `test_util.h`.

Risks: fatal error handling calls `exit(1)`, which is acceptable for example code but not a reusable library pattern. The deliberate invalid call ignores its return value because the handler output is the test signal.

Test signals: run output should contain the expected error message bracketed by the example's `expect` and `end` lines, and connection close should succeed.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_event_handler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_extending.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_extending.c

Purpose: demonstrates registering custom collators directly with a WiredTiger connection.

Important APIs and control flow: defines a case-insensitive `WT_COLLATOR` using `strcasecmp`, and a `PREFIX_COLLATOR` struct that embeds `WT_COLLATOR` first plus a `maxlen` configuration field. `__compare_prefixes` casts the base collator pointer back to `PREFIX_COLLATOR` and compares only the first `maxlen` bytes. `main` opens a connection, registers `nocase` and `prefix10`, opens a session, leaves room for application work, and closes.

State and persistence: registers collators for the connection lifetime. No table data is created by the visible example.

Dependencies and integration: depends on the collator ABI and the "interface first" embedding convention. Uses `test_util.h` and platform availability of `strcasecmp`.

Risks: string comparators assume keys are C strings; they are not safe for arbitrary binary `WT_ITEM` keys with embedded NUL bytes. Prefix comparison can intentionally collapse distinct keys over the configured prefix, which has schema consequences.

Test signals: successful `add_collator` calls compile and run. Real validation would create indexed tables using the collators and verify ordering/search semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_extending.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_extra_diagnostics.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_extra_diagnostics.c

Purpose: demonstrates enabling and updating WiredTiger extra diagnostic checks at runtime.

Important APIs and control flow: `main` obtains WT_HOME and then branches on `HAVE_DIAGNOSTIC`. In diagnostic builds, diagnostics are always enabled, and configuring `extra_diagnostics=[key_out_of_order]` is asserted to return `EINVAL`. In non-diagnostic builds, it opens with `extra_diagnostics=[key_out_of_order]` and then reconfigures the connection to `extra_diagnostics=[txn_visibility]`, implicitly disabling omitted diagnostics.

State and persistence: opens a connection and mutates runtime connection diagnostic configuration. No explicit table state is created.

Dependencies and integration: depends on build-time `HAVE_DIAGNOSTIC`, WiredTiger connection configuration, `conn->reconfigure`, and `test_util.h`.

Risks: the non-diagnostic branch does not close the connection before returning, so it relies on process cleanup. Diagnostic options are version/configuration sensitive, so example expectations must track supported option names and diagnostic-mode semantics.

Test signals: diagnostic builds must observe `EINVAL`; non-diagnostic builds must open and reconfigure successfully.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_extra_diagnostics.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_file_system.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_file_system.c

Purpose: implements an in-memory custom `WT_FILE_SYSTEM`/`WT_FILE_HANDLE` extension and uses it to back a WiredTiger table.

Important APIs and control flow: `DEMO_FILE_SYSTEM` embeds `WT_FILE_SYSTEM` first, stores a global rwlock, counters, handle queue, and extension API. `DEMO_FILE_HANDLE` embeds `WT_FILE_HANDLE` first, tracks owning FS, queue node, refcount, buffer, buffer capacity, and logical size. `demo_file_system_create` parses custom extension config, initializes callback tables, and calls `conn->set_file_system`. Filesystem callbacks implement open, directory listing/free, existence, remove, rename, size, and termination. File callbacks implement close, lock, read, size, sync, truncate, and write. `main` loads the local extension with `early_load=true`, creates `table:fs`, inserts 1000 rows, rescans and verifies ordered keys, then closes.

State and persistence: file contents live only in heap buffers for the connection lifetime. Counters are printed at termination. A WT_HOME directory is created only as an anchor; storage is redirected through the custom FS.

Dependencies and integration: requires POSIX pthread rwlocks, TAILQ macros from included test/util headers, local extension symbol visibility, early extension loading, and WiredTiger file-system ABI.

Risks: a single global write lock serializes all I/O and schema activity. The directory prefix check compares prefix against the full name, which is simplistic. `memset(entries + allocated * sizeof(*entries), ...)` uses pointer arithmetic incorrectly for an array of pointers. The implementation supports only one open reference per file.

Test signals: insertion/rescan of 1000 ordered keys validates basic read/write/size/open behavior, and termination counters show file lifecycle coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_file_system.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_get_last_error.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_get_last_error.c

Purpose: demonstrates the `WT_SESSION.get_last_error` API for retrieving detailed session error state.

Important APIs and control flow: `main` sets up WT_HOME, opens a connection and session, prepares `err`, `sub_level_err`, and `err_msg`, calls `session->get_last_error(session, &err, &sub_level_err, &err_msg)`, prints all three returned values, and closes the connection.

State and persistence: no table state is created. The session-level last-error fields are read immediately after opening the session, so the example primarily shows API shape rather than a populated failure case.

Dependencies and integration: uses `test_util.h` and public connection/session APIs. It integrates with documentation that explains verbose session error information.

Risks: because no failing session operation precedes `get_last_error`, output may represent a no-error/default state. Consumers copying the pattern should call it after an API failure on the same session.

Test signals: successful execution and stable printed fields validate ABI compatibility. A stronger test would trigger a known session error and assert the primary and sub-level error codes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_get_last_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_hello.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_hello.c

Purpose: smallest canonical C example for opening a WiredTiger database and session.

Important APIs and control flow: `main` calls `example_setup`, opens a connection with `wiredtiger_open(home, NULL, "create", &conn)`, opens a session with `conn->open_session`, does no table work, and closes the connection. The close call implicitly closes the open session.

State and persistence: creates a WT_HOME database directory and metadata files. No user table data is created.

Dependencies and integration: depends on `test_util.h` for setup/error handling and the public WiredTiger C API.

Risks: intentionally omits cleanup, explicit session close, and any transactional or schema behavior. It should not be treated as an operational template beyond connection/session lifecycle basics.

Test signals: successful open/session/close proves basic library linkage and runtime initialization under the example harness.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_hello.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_log.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_log.c

Purpose: demonstrates logging, log cursors, application log records, replaying row-put operations into a second database, and searching logs by LSN.

Important APIs and control flow: `main` creates two homes, opens `home1` with logging and removal disabled, creates `table:logtest`, inserts 10 auto-commit records and 5 transaction records, writes an application log message, closes/reopens, then calls `simple_walk_log` and `walk_log`. `simple_walk_log` opens `log:`, prints key/value fields, and enforces a minimum record count. `walk_log` opens a second logged copy, scans log records, tracks a saved LSN, replays `WT_LOGOP_ROW_PUT` records for non-metadata file IDs through a raw cursor into the copy under transactions, compares tables, then resets/searches the log cursor to the saved LSN and scans from there.

State and persistence: creates two database homes and logged table state. Log files persist because `remove=false`.

Dependencies and integration: requires POSIX target gating, `test_util_system`, log cursor value layout, raw table cursor behavior, and the `WT_LOGREC_*`/`WT_LOGOP_*` constants.

Risks: replay logic only handles row-put records and intentionally skips metadata. It assumes log record ordering and transaction boundaries via `opcount == 0`. It is not a general log recovery implementation.

Test signals: log walk count must meet `count_min`; replayed copy must compare identical to the original; LSN search must return the saved file/offset.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_pack.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_pack.c

Purpose: demonstrates the standalone structure packing and unpacking helpers.

Important APIs and control flow: `main` opens a connection/session, calls `wiredtiger_struct_size(session, &size, "iii", 42, 1000, -9)`, conditionally notes where larger allocation would occur, packs three integers into a fixed buffer with `wiredtiger_struct_pack`, then unpacks them back into `i`, `j`, and `k` with `wiredtiger_struct_unpack`.

State and persistence: only opens a database and session; no table data is created. The packed buffer is stack-local.

Dependencies and integration: depends on the WiredTiger packing format syntax, session context, and `test_util.h`. The example complements raw cursor examples that unpack key/value `WT_ITEM` buffers.

Risks: the fixed buffer is safe only because size is checked before packing; real code must allocate if required. Format strings and C destination types must stay aligned.

Test signals: successful size/pack/unpack calls validate the packing API and integer format handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_pack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_process.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_process.c

Purpose: minimal example for opening WiredTiger in multi-process mode.

Important APIs and control flow: `main` uses `example_setup`, opens a connection with `wiredtiger_open(home, NULL, "create,multiprocess", &conn)`, opens one session, does placeholder work, and closes the connection.

State and persistence: creates a WT_HOME configured for multi-process access. No table data is created by the example.

Dependencies and integration: depends on WiredTiger's `multiprocess` connection configuration and `test_util.h`.

Risks: it does not actually spawn multiple processes or demonstrate coordination, locking, or workload isolation. It validates the configuration path, not concurrent behavior.

Test signals: successful open/session/close with `multiprocess` enabled. Deeper validation would require independent processes sharing the same home.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_schema.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_schema.c

Purpose: demonstrates schema features: named columns, column groups, simple/composite/immutable indexes, raw cursors, and projected access.

Important APIs and control flow: defines `POP_RECORD` sample data. `main` creates `table:poptable` with record-number keys, value format `5sHQ`, named columns, and `main`/`population` column groups. It creates simple `country`, composite `country_plus_year`, and immutable `year` indexes. It appends sample rows, scans and updates populations, lists rows normally and in raw mode via `wiredtiger_struct_unpack`, reads through both column groups, searches simple and composite indexes, and closes.

State and persistence: persists population rows, column-group storage, and indexes. Updates increment every population after insertion, so later reads observe modified state.

Dependencies and integration: uses format-string packing semantics, index projection syntax, and `test_util.h`.

Risks: fixed-width country strings require padded search keys such as `"AU\0\0\0"` and `"USA\0\0"`. Immutable index correctness depends on not updating indexed `year` values.

Test signals: normal/raw scans must agree, column group lookups for record 2 must return expected fields, and simple/composite index searches must succeed.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_schema.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_smoke.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_smoke.c

Purpose: standalone smoke test proving headers and libraries link without the example test utility layer.

Important APIs and control flow: includes only standard headers and `wiredtiger.h`. `main` removes and recreates `WT_HOME` via `system`, opens WiredTiger with `create`, closes the connection, and reports errors with `wiredtiger_strerror`.

State and persistence: deletes and recreates a local `WT_HOME`; creates basic WiredTiger metadata; no user tables are written.

Dependencies and integration: intentionally avoids `test_util.h` so it validates a minimal external-client build. CMake marks it POSIX-dependent because it shells out to `rm`/`mkdir`.

Risks: destructive `rm -rf WT_HOME` is safe only in the example's working directory. It does not validate sessions, schema, or cursor APIs.

Test signals: successful compile/link/run establishes basic include/library linkage and connection lifecycle.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_smoke.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_stat.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_stat.c

Purpose: demonstrates database, table, session, direct-key, and derived statistics queries.

Important APIs and control flow: helper `print_cursor` iterates a statistics cursor and prints nonzero values. `print_database_stats`, `print_file_stats`, and `print_session_stats` open `statistics:`, `statistics:table:access`, and `statistics:session`. `print_overflow_pages` seeks `WT_STAT_DSRC_BTREE_OVERFLOW`. `get_stat` positions a stats cursor by statistic key. `print_derived_stats` computes fragmentation from checkpoint/file size and write amplification from app bytes versus filesystem writes. `main` opens with `statistics=(all)`, creates `table:access`, inserts one row, checkpoints, prints all categories, and closes.

State and persistence: persists one table and checkpoint. Statistics are runtime/database state and may be cleared or vary by build/configuration.

Dependencies and integration: depends on generated/stat header constants such as `WT_STAT_DSRC_BLOCK_CHECKPOINT_SIZE` and the statistics cursor schemas.

Risks: integer fragmentation calculation uses integer division, so small ratios may truncate. Statistics availability and values depend on configuration and workload; zero values are intentionally suppressed.

Test signals: stats cursors should open and iterate to `WT_NOTFOUND`, direct stat lookup should succeed, and derived-stat calculations should not divide by zero.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_thread.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_thread.c

Purpose: demonstrates using one `WT_CONNECTION` from multiple threads, with one session/cursor per thread.

Important APIs and control flow: `main` creates `table:access`, inserts one row, closes the setup session, then starts `NUM_THREADS` worker threads using `__wt_thread_create`. Each `scan_thread` opens its own session and cursor on the shared connection and scans all records, printing each key/value. The main thread joins all workers with `__wt_thread_join` and closes the connection.

State and persistence: persists a single row. Thread state is isolated by per-thread sessions and cursors; the connection is shared.

Dependencies and integration: depends on WiredTiger internal test thread wrappers (`wt_thread_t`, `__wt_thread_create`, `__wt_thread_join`) via `test_util.h`, plus public session/cursor APIs.

Risks: worker sessions/cursors are not explicitly closed before thread return, relying on connection close. The workload is read-only after setup and does not demonstrate concurrent writes or transaction conflicts.

Test signals: all threads should print the inserted row and terminate without errors other than expected scan `WT_NOTFOUND`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_tiered.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_tiered.c

Purpose: demonstrates tiered storage using the local `dir_store` storage source.

Important APIs and control flow: helper `add_data` inserts integer keys; `show_data` scans and prints a table. `platform_supported` skips Windows. `main` builds an open config with `tiered_storage=(bucket,bucket_prefix,local_retention,name=dir_store)` and loads `libwiredtiger_dir_store.so`, creates home and bucket directories, opens the connection, creates one local-only table with `tiered_storage=(name=none)` and one default tiered table, inserts batches, performs a normal checkpoint, inserts more, performs `checkpoint("flush_tier=(enabled)")`, scans both tables, inserts more, performs another normal checkpoint, and scans again.

State and persistence: creates local WT_HOME files and a bucket subdirectory containing tiered objects after flush. The tiered table may span local and object storage after later writes.

Dependencies and integration: requires non-Windows platform support, built `dir_store` extension at a relative build path, filesystem directories, and WiredTiger tiered storage configuration.

Risks: hard-coded `BUILD_DIR "../../../"` assumes a build/run layout. It does not verify object contents directly. Local retention and flush behavior can change with tiered-storage implementation details.

Test signals: scans of local and tiered tables should show all inserted keys independent of whether data resides locally or in the bucket after `flush_tier`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_tiered.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_verbose.c -->
# sources/storage-engines/wiredtiger/examples/c/ex_verbose.c

Purpose: demonstrates verbose message configuration and message callbacks.

Important APIs and control flow: defines `handle_wiredtiger_message`, which prints the session pointer and message. `config_verbose` initializes a `WT_EVENT_HANDLER` with only `handle_message`, opens WiredTiger with `verbose=[api:1,all:0,version,write:2]`, then makes API calls (open session, create table, open cursor, insert row, close cursor) to trigger verbose messages before closing.

State and persistence: creates `table:verbose` and inserts `foo/bar`. Verbose output is emitted through the callback, not persisted by this example.

Dependencies and integration: depends on verbose category syntax and the `WT_EVENT_HANDLER` ABI. Uses `test_util.h`.

Risks: verbose category names and levels are version-sensitive. Message volume is controlled by config and may change as APIs emit different diagnostics.

Test signals: output should include verbose messages between the example's `expect` and `end` markers, and all API calls should succeed.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/c/ex_verbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/python/ex_access.py -->
# sources/storage-engines/wiredtiger/examples/python/ex_access.py

Purpose: Python binding equivalent of the simple access example.

Important APIs and control flow: removes and recreates `WT_HOME`, opens a connection with `wiredtiger_open('WT_HOME', 'create')`, opens a session, creates `table:T` with string key/value formats, opens a cursor, inserts `key1/value1` using `set_key`, `set_value`, and `insert`, resets the cursor, iterates it with Python cursor iteration, prints records, and closes the connection.

State and persistence: recreates a local WT_HOME and persists one table/record. Cursor iteration wraps WiredTiger cursor movement in Python binding semantics.

Dependencies and integration: depends on the Python `wiredtiger` module and filesystem access. Snippet markers are documentation-oriented.

Risks: `os.system('rm -rf WT_HOME')` is destructive relative to the working directory. The script does not use `try/finally`, so failures can leave handles open until process exit.

Test signals: execution should print `Got record: key1 : value1` and close cleanly.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/python/ex_access.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/python/ex_stat.py -->
# sources/storage-engines/wiredtiger/examples/python/ex_stat.py

Purpose: Python binding example for querying and deriving WiredTiger statistics.

Important APIs and control flow: `main` recreates WT_HOME, opens with `statistics=(all)`, creates `table:access`, writes one row via item assignment, checkpoints, prints `WIREDTIGER_VERSION_STRING`, then calls helper functions. `print_database_stats` and `print_file_stats` open statistics cursors. `print_overflow_pages` indexes the table stats cursor by `stat.dsrc.btree_overflow`. `print_derived_stats` reads block and cursor-byte stats through `stat.dsrc` constants and computes fragmentation and write amplification. `print_cursor` iterates with `next()` and prints nonzero printable values.

State and persistence: creates one table and checkpoint; statistics reflect the runtime/database state after the insert.

Dependencies and integration: depends on Python `wiredtiger` bindings, the `stat` constant namespace, and filesystem cleanup.

Risks: destructive `rm -rf WT_HOME`; no exception-safe cleanup. The fragmentation output format has `%%%s`, resulting in a literal percent sign before the computed value. Statistics values can vary by build and storage behavior.

Test signals: statistics cursors should iterate, direct stat indexing should work, and derived calculations should avoid divide-by-zero guards.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/examples/python/ex_stat.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/ext/CMakeLists.txt

Purpose: top-level build integration for WiredTiger loadable extensions.

Important APIs and control flow: adds subdirectories for compressor, collator, encryptor, storage-source, page-log, and test extensions. POSIX-only extensions are gated by `WT_POSIX`, and `ENABLE_PALITE` controls the palite page-log extension. It creates an umbrella `wiredtiger_ext` target, iterates a known list of extension targets, checks whether each target exists and is a `MODULE_LIBRARY`, and adds it as a dependency.

State and persistence: no runtime state; it produces module library build targets and an aggregate build target.

Dependencies and integration: depends on each extension subdirectory declaring expected target names. `wiredtiger_ext` allows runtime consumers that use `dlopen`/extension loading to depend on all available modules without maintaining duplicate lists.

Risks: the target list must stay synchronized with subdirectories and target names. Optional or platform-gated targets are handled gracefully by `if(TARGET ...)`, but a renamed extension would silently drop from the umbrella target.

Test signals: configuring and building `wiredtiger_ext` should build all available module libraries on the current platform.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/collators/reverse/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/ext/collators/reverse/CMakeLists.txt

Purpose: builds the reverse string collator as a loadable WiredTiger module.

Important APIs and control flow: sets `sources` to `reverse_collator.c`, creates `wiredtiger_reverse_collator` as a `MODULE` library, adds private include directories for source includes, generated includes, and generated config, and applies `${COMPILER_DIAGNOSTIC_C_FLAGS}`.

State and persistence: no runtime state; produces a module artifact for extension loading.

Dependencies and integration: depends on generated WiredTiger headers in the build tree and strict compiler flags from the broader CMake configuration. The target name is referenced by the top-level `wiredtiger_ext` umbrella.

Risks: include directory ordering must expose generated config before extension compilation. If target name changes, the umbrella dependency list must be updated.

Test signals: module compilation and successful runtime `load_extension`/extension initialization validate integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/collators/reverse/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/collators/reverse/reverse_collator.c -->
# sources/storage-engines/wiredtiger/ext/collators/reverse/reverse_collator.c

Purpose: implements a loadable collator named `reverse` that orders byte-string keys in reverse lexicographic order.

Important APIs and control flow: `collate_reverse` receives two `WT_ITEM` keys, compares the common prefix with `memcmp`, inverts the comparison result, and reverses length tie-breaks so shorter keys sort after longer keys under the reversed order. A static `WT_COLLATOR reverse_collator` points at this compare function. `wiredtiger_extension_init` registers it via `connection->add_collator(connection, "reverse", &reverse_collator, NULL)`.

State and persistence: no mutable extension state; the static collator lives for process lifetime. Registered collator state is connection-local.

Dependencies and integration: depends on `wiredtiger_ext.h`, module loading convention `wiredtiger_extension_init`, and schemas/indexes configured to use `collator=reverse`.

Risks: the comparator treats keys as raw bytes and is safe for binary data, but reverse ordering must remain strict and transitive. No terminate callback is needed because no allocation occurs.

Test signals: loading the extension and creating/searching an index with `collator=reverse` should show descending byte order.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/collators/reverse/reverse_collator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/collators/revint/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/ext/collators/revint/CMakeLists.txt

Purpose: builds the reverse-integer collator extension as a loadable module.

Important APIs and control flow: sets `sources` to `revint_collator.c`, creates `wiredtiger_revint_collator` as a `MODULE` library, adds private include paths for source and generated headers/config, and applies `${COMPILER_DIAGNOSTIC_C_FLAGS}`.

State and persistence: no runtime state; produces a module artifact.

Dependencies and integration: depends on build-generated WiredTiger headers and is listed by the top-level extension umbrella as `wiredtiger_reverse_int_collator`, which should be checked for consistency with this target name.

Risks: there is a target-name mismatch risk: this file defines `wiredtiger_revint_collator`, while the top-level umbrella list references `wiredtiger_reverse_int_collator`. If no alias exists elsewhere, the umbrella target will not depend on this module.

Test signals: direct target build should compile the module; umbrella target membership should be verified by inspecting CMake targets or building `wiredtiger_ext`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/collators/revint/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/collators/revint/revint_collator.c -->
# sources/storage-engines/wiredtiger/ext/collators/revint/revint_collator.c

Purpose: implements a loadable collator named `revint` for integer secondary indexes sorted descending by index key while preserving ascending primary-key ordering among duplicates.

Important APIs and control flow: `REVINT_COLLATOR` embeds `WT_COLLATOR` first and stores `WT_EXTENSION_API`. `revint_compare` unpacks each `WT_ITEM` with extension pack APIs using format `ii`, treating a missing primary key as `INT64_MIN` so a search key without a primary key sorts before duplicate index entries. It then reverses comparison of the first integer and compares primary integers normally. `revint_terminate` frees the allocated collator. `wiredtiger_extension_init` allocates/configures the collator, stores the extension API, registers it as `revint`, and frees on registration failure.

State and persistence: per-extension allocated collator state lasts until WiredTiger calls terminate. No table data is written by the extension itself.

Dependencies and integration: depends on `wiredtiger_ext.h`, extension pack/unpack stream APIs, integer key schemas, and module loading conventions.

Risks: only valid for index keys and primary keys encoded as integers. Error paths must close pack streams correctly; the implementation handles several but depends on API behavior when the second integer is absent. Ordering must remain compatible with search semantics for duplicate keys.

Test signals: extension load, index creation with `collator=revint`, duplicate index-key searches, and cursor iteration order validate behavior and missing-primary-key handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/collators/revint/revint_collator.c -->
