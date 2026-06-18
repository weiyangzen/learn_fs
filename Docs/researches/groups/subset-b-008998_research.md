# Research Report: subset-b-008998

Grouped research for WiredTiger transaction recovery/timestamp/truncate internals and `wt` utility command sources. Each section is delimited for deterministic split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/txn/txn_recover.c -->
## sources/storage-engines/wiredtiger/src/txn/txn_recover.c

Purpose: implements WiredTiger startup recovery. It scans metadata and log records, replays committed operations after checkpoints, reconstructs global timestamp state, repairs or rejects inconsistent metadata states, handles incremental backup metadata records, optionally runs rollback-to-stable, and forces a checkpoint so the next open has synchronized metadata and log state.

Important APIs/types/functions: `WT_RECOVERY_FILE` caches a metadata-discovered URI, recovery cursor, and checkpoint LSN by file ID. `WT_RECOVERY` carries recovery-wide state including file-id array, checkpoint/recovery LSN bounds, metadata-only and backup-only pass flags, disaggregated leader role, and missing-file reporting. Key helpers are `__recovery_cursor`, `__txn_op_apply`, `__txn_log_recover`, `__recovery_setup_file`, `__recovery_file_scan`, `__hs_exists_local`, and exported `__wt_txn_recover`. Recovery uses generated log unpackers such as `__wt_logop_row_put_unpack`, metadata helpers such as `__wt_metadata_search`, and transaction/checkpoint helpers such as `__wti_txn_checkpoint_logread`.

Control flow: recovery starts by opening an internal `txn-recover` session, registering the metadata file as file ID 0, and reading base write-generation metadata. If no logs exist or the metadata checkpoint LSN is max, it only scans metadata, possibly resets log numbering, checks the history store, and skips log replay. Otherwise it first runs a metadata or backup-only log scan, depending on whether the database was opened from backup, then scans metadata for live files and incomplete tables, validates the local history store, closes the metadata cursor, and runs the main log scan for non-metadata records. `__txn_log_recover` peeks log record type and dispatches checkpoint, commit, and system records. Commit records loop over operations; row/column puts, removes, modifies, and truncates are unpacked and applied through recovery cursors when their file checkpoint LSN requires replay. Timestamp log operations are unpacked only to advance the record cursor.

State and persistence behavior: the file-id array mirrors metadata state and determines whether a logged operation is applied, skipped as older than the file checkpoint, or ignored because the file disappeared. Metadata recovery is isolated by `WT_CONN_RECOVERING_METADATA` to avoid opening data files before metadata is consistent. Incomplete simple table metadata is force-dropped unless readonly; layered tables assert required ingest/stable metadata. Recovery sets `recovery_timestamp`, `meta_ckpt_timestamp`, `oldest_timestamp`, pinned timestamp, stable timestamp, checkpoint snapshot fields, and base write generation from checkpoint metadata. It may create/open the history store, start eviction threads to support replay and RTS, remove backup files, update dhandle write generations, and truncate logs for downgrade.

Dependencies and integration points: tightly integrated with log manager scans and LSN comparisons, metadata cursors, schema drop locks, history store configuration/salvage, rollback-to-stable, eviction, backup/incremental backup state, disaggregated storage role handling, file/tiered URI metadata, and connection recovery timeline/stat flags. Non-standalone builds set `unclean_shutdown` when table log records must be replayed and reject unclean upgrade from WiredTiger 10.0.0.

Risks: recovery correctness depends on accurately parsing file IDs and checkpoint LSNs from metadata; corruption there can skip required replay or replay stale records. Readonly mode must reject any database needing recovery because it cannot persist repair. Salvage deliberately ignores some log scan errors, so test expectations must distinguish salvage best-effort behavior from normal strict recovery. Timestamp initialization and RTS gating are high-risk because wrong stable/oldest/recovery values can expose unstable updates or remove valid history. Truncate replay uses duplicate cursors for bounded ranges and must close them on all paths. Disaggregated and precise-checkpoint bypass of RTS is a correctness boundary.

Test signals: recovery suites should cover clean shutdown, unclean log replay, metadata-only replay, backup opens, incremental backup ID force-stop records, readonly `WT_RUN_RECOVERY`, salvage with damaged logs/history store, incomplete simple table cleanup, layered table metadata assertions, missing data files, history store absent/present transitions, RTS execution/skipping, forced recovery checkpoint timing, downgrade log truncation, and upgrade rejection from unclean 10.0.0 databases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/txn/txn_recover.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/txn/txn_timestamp.c -->
## sources/storage-engines/wiredtiger/src/txn/txn_timestamp.c

Purpose: implements parsing, querying, publishing, clearing, and validation for transaction and global timestamps. It enforces WiredTiger's ordering rules for oldest/stable/durable/read/prepare/commit/rollback timestamps and keeps shared pinned/read/durable timestamp state visible to checkpoints, eviction, rollback-to-stable, and all-durable queries.

Important APIs/types/functions: public/internal entry points include `__wt_txn_parse_timestamp_raw`, `__wt_txn_parse_timestamp`, `__wt_txn_parse_prepared_id`, `__wti_txn_get_pinned_timestamp`, `__wt_txn_query_timestamp`, `__wti_txn_update_pinned_timestamp`, `__wt_txn_global_set_timestamp`, `__wti_txn_set_read_timestamp`, `__wt_txn_set_timestamp`, `__wt_txn_set_timestamp_uint`, `__wt_txn_set_prepared_id`, `__wt_txn_set_prepared_id_uint`, `__wti_txn_clear_durable_timestamp`, and `__wti_txn_clear_read_timestamp`. Private validators cover commit, durable, prepare, rollback, and prepared IDs.

Control flow: query functions parse the `get` configuration and either read session-local transaction fields or global timestamp fields. Global `all_durable` and pinned/oldest-reader queries walk `txn_shared_list` under the transaction global rwlock, using acquire barriers to read per-session shared timestamps. Global set first parses optional durable/oldest/stable/stable-disaggregated schema epoch fields, rejects backward movement unless `force` is supplied where allowed, enforces `oldest <= stable`, then updates global atomics under the write lock and refreshes the pinned timestamp. Per-transaction set parses config items in the second config string, applies commit before durable, then read, prepare, and rollback, publishes durable visibility, and optionally logs timestamp changes in debug table logging mode.

State and persistence behavior: this file mutates `WT_TXN_GLOBAL` atomics (`oldest_timestamp`, `stable_timestamp`, `durable_timestamp`, `pinned_timestamp`, disaggregated schema epoch flags, newest seen timestamp) and per-session `WT_TXN_SHARED` fields (`read_timestamp`, `pinned_durable_timestamp`). It updates `WT_TXN` time point fields and flags for first commit, commit, durable, prepare, rollback, and prepared ID. These are memory-resident concurrency-control state, but they determine what checkpoint/recovery/RTS can persist and what readers can see. Debug timestamp logging persists timestamp records only when table logging debug mode is enabled and the connection is not recovering.

Dependencies and integration points: depends on config parsing, timestamp hex/string helpers, transaction context checks, isolation level rules, global rwlocks, session array traversal, stats counters, debug diagnostics, disaggregated last checkpoint timestamp, and transaction log timestamp record generation. It integrates with recovery through `recovery_timestamp`, with backup checkpoint timestamp query through the hot-backup lock, and with prepared transaction semantics through prepare/commit/durable/rollback timestamp ordering.

Risks: races around global timestamp reads and updates are mitigated by rwlocks and atomic barriers, but comments still flag synchronization review around oldest/stable comparisons. `force` permits out-of-order oldest/stable states for MongoDB-specific scenarios, so downstream code must tolerate that after logging a stat. Prepared transaction roundup modes are intentionally narrow; using `roundup=prepared` during normal operation can create inconsistency. Durable timestamps for prepared IDs must be after the disaggregated last checkpoint timestamp or step-up drain can miss preserved prepared updates. Read timestamp rounding to oldest changes the caller's requested view and forces snapshot refresh.

Test signals: timestamp API tests should cover zero rejection, hex parsing, global query variants, all-durable with concurrent prepared/nonprepared transactions, pinned timestamp advancement and pin flags, oldest/stable monotonic errors, force behavior, read timestamp older than oldest with and without roundup, commit timestamp ordering against first commit/stable/oldest, durable-before-commit errors, prepare/commit/rollback exclusivity, prepared ID duplicate/zero errors, debug timestamp logging suppression during recovery, and disaggregated durable timestamp assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/txn/txn_timestamp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/txn/txn_truncate.c -->
## sources/storage-engines/wiredtiger/src/txn/txn_truncate.c

Purpose: maintains the in-memory truncate list used by disaggregated layered-table followers. It records follower-side range truncates, detects write conflicts with visible and not-yet-visible truncate ranges, marks truncate entries committed with timestamps, removes rolled-back entries, and garbage-collects entries once a picked-up checkpoint has made them durable.

Important APIs/types/functions: `WT_TRUNCATE_SEARCH_MODE` selects visible versus not-visible entries for searches. Exported/internal entry points include `__wt_insert_truncate_entry`, `__wt_layered_table_truncate_detect_write_conflict`, `__wt_layered_table_truncate_detect_non_ingest_write_conflict`, `__wt_truncate_delete_visible_check`, `__wti_mark_committed_truncate_table`, `__wti_layered_table_truncate_rollback`, `__wt_layered_table_truncate_clear`, and unit-test hook `__ut_layered_table_truncate_gc`. Core helpers are `__key_within_truncate_range`, `__truncate_search`, `__layered_table_truncate_gc`, `__truncate_entry_remove`, and `__disagg_truncate_apply`.

Control flow: inserting a truncate allocates `WT_TRUNCATE`, copies concrete start/stop keys, switches to the layered table ingest dhandle, registers a transaction operation via `__wt_txn_truncate`, then under the truncate write lock prunes old committed entries, acquires a dhandle reference if the queue was empty, and appends the entry. Reads and writes take the truncate read lock and walk the queue. Write conflict checks search not-visible entries; visible delete checks search committed visible entries and can copy the matching range back to the caller. Commit apply writes commit/durable timestamps into the entry and then stores `committed=true` with release ordering. Rollback apply removes the queue entry and frees it.

State and persistence behavior: the truncate queue is in `WT_LAYERED_TABLE.truncateqh`, protected by `truncate_lock`. Queue lifetime pins the layered dhandle by acquiring a reference when the first entry is inserted and releasing when the last is removed. Each entry stores start/stop keys, owning layered table, transaction ID, committed flag, start timestamp, and durable timestamp. Persistence is indirect: entries are removed when `S2BT(session)->prune_timestamp` indicates a checkpoint has picked up committed durable truncates. Slow follower truncate debug mode asserts that the list is not used.

Dependencies and integration points: depends on layered table metadata and locks, transaction operation registration, transaction visibility (`__wt_txn_visible`), key comparison with the layered table collator, dhandle acquisition/release, stats counters for layered truncate list activity, and error reporting via `WT_ROLLBACK`/`WT_WRITE_CONFLICT`. It is called from cursor/write paths that need conflict detection and version visibility for disaggregated follower truncates.

Risks: range overlap detection must be exact: point writes use key-within-existing-range, while non-ingest range writes also test whether an existing range starts within the new range. Missing either direction can allow writes into a pending truncate. Commit timestamp publication relies on release/acquire ordering around `committed`; readers must not inspect timestamps from an uncommitted entry. GC cannot prune committed entries without durable timestamps, so timestamp-less entries can retain dhandle references indefinitely. All range inputs are asserted concrete; callers must resolve open-ended ranges before insertion.

Test signals: tests should cover follower-only list behavior, leader returning `WT_NOTFOUND` for visible delete checks, slow-truncate debug bypass, overlapping and non-overlapping write conflict ranges, rollback removing entries and releasing references, commit making entries visible with timestamps, prune timestamp GC removing only committed durable entries at or before prune time, collator-aware key ordering, copied range ownership/freeing, and stats increments for search/GC paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/txn/txn_truncate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/CMakeLists.txt -->
## sources/storage-engines/wiredtiger/src/utilities/CMakeLists.txt

Purpose: defines the `wt` command-line utility target and its source list for the CMake build. It gathers the command dispatcher, individual command implementations, shared utility helpers, and optional Antithesis dependency into one executable.

Important APIs/types/functions: declares `sources` containing `util_main.c`, command files such as `util_dump.c`, `util_load.c`, `util_backup.c`, and shared files such as `util_misc.c` and `util_verbose.c`. It calls `add_executable(wt ${sources})`, applies `${COMPILER_DIAGNOSTIC_C_FLAGS}`, adds include paths for `src/include` and generated `config`, links `wt::wiredtiger`, optionally links `wt::voidstar`, sets `RUNTIME_OUTPUT_DIRECTORY` to `${CMAKE_BINARY_DIR}`, and installs the binary to `bin`/`${CMAKE_INSTALL_BINDIR}`.

Control flow: configure-time logic builds the source list, declares the target, configures compilation/linking, applies backward-compatible output placement expected by tests, and registers install rules. There is no runtime control flow in this file.

State and persistence behavior: affects build-system state: target source membership, include/link dependencies, output path, and install destination. The top-level runtime output placement is a compatibility contract for existing tests and examples that expect `wt` at the build root.

Dependencies and integration points: integrates with the main WiredTiger CMake target namespace, generated configuration headers, compiler diagnostic flag setup, Antithesis optional build flag, test harness expectations, and installation packaging.

Risks: omitting a command source from the list can compile a dispatcher reference without implementation or silently drop a utility subcommand. Moving `RUNTIME_OUTPUT_DIRECTORY` can break tests/scripts that execute `${CMAKE_BINARY_DIR}/wt`. The install rule uses both `RUNTIME DESTINATION bin` and `DESTINATION ${CMAKE_INSTALL_BINDIR}`; changes should be checked against CMake install semantics and packaging expectations.

Test signals: successful CMake configure/build of target `wt`, ability to run `${builddir}/wt -V`, command dispatch smoke tests, Antithesis-enabled builds when `ENABLE_ANTITHESIS` is set, and install packaging checks that place the binary in the expected bindir.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util.h -->
## sources/storage-engines/wiredtiger/src/utilities/util.h

Purpose: central header for the `wt` utility. It imports WiredTiger internals, declares shared global CLI state, exposes all command entry points, and declares helper routines for URI normalization, usage, errors, line reading, numeric parsing, memory allocation, and output-file handling.

Important APIs/types/functions: defines `ULINE` as a managed line buffer used by dump/load readers. Extern globals include `home`, `progname`, `usage_prefix`, `verbose`, `verbose_handler`, and WiredTiger getopt globals. Command prototypes include `util_alter`, `util_backup`, `util_compact`, `util_create`, `util_dump`, `util_list`, `util_load`, `util_loadtext`, `util_verify`, and others. Shared helpers include `util_err`, `util_cerr`, `util_flush`, `util_read_line`, `util_str2num`, `util_uri`, `util_usage`, allocation wrappers, and output-file open/close wrappers.

Control flow: this header does not execute code, but it defines the common command signature `int (WT_SESSION *, int, char *[])` used by `util_main.c` dispatch. Commands share the global getopt state and helper API declared here.

State and persistence behavior: exposes process-wide CLI state such as the active home directory and verbose mode. Helpers declared here affect persistence indirectly: `util_flush` forces loaded data to disk, `util_uri` determines which database object a command mutates, and allocation/output helpers control resource ownership.

Dependencies and integration points: depends on `wt_internal.h`, so utility code is allowed to call internal WiredTiger APIs as well as public `WT_SESSION`/`WT_CONNECTION` APIs. It is included by every utility command source and is the contract between command files and shared `util_misc.c`/`util_verbose.c`.

Risks: because this header exposes internal APIs and process globals, command implementations are tightly coupled and not reentrant. Misuse of `ULINE.mem` ownership or allocation wrappers can leak or double free. Any signature change must be coordinated across all command sources and the dispatcher.

Test signals: full utility target compilation is the main ABI signal. Runtime tests for usage/error output, URI normalization, input line handling, memory-error paths, and output-file close errors exercise the shared helper contract.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_alter.c -->
## sources/storage-engines/wiredtiger/src/utilities/util_alter.c

Purpose: implements `wt alter`, a thin CLI wrapper over `WT_SESSION.alter` for applying configuration changes to one or more URIs.

Important APIs/types/functions: `util_alter` parses only `-?`, validates that remaining arguments are URI/configuration pairs, and calls `session->alter(session, configp[0], configp[1])` for each pair. The static `usage` function documents `alter uri configuration ...`.

Control flow: after option parsing, argument count must be nonzero and even. The function walks the remaining argv two entries at a time. On the first `session->alter` failure it reports `session.alter: uri, config` with `util_err` and returns `1`; otherwise it returns `0`.

State and persistence behavior: alters metadata and object configuration through the WiredTiger session API. Whether changes are persisted, rejected, or require clean trees is enforced by the library. This wrapper does no URI defaulting; callers must pass the intended URI string.

Dependencies and integration points: dispatched from `util_main.c` under an already opened connection/session. Uses `__wt_getopt` global state and `util_usage`/`util_err`. It depends on WiredTiger session alter semantics for validation and locking.

Risks: it accepts arbitrary URI strings and config pairs without `util_uri` normalization, so shorthand table names are not expanded here. Partial success is possible: earlier pairs may have altered objects before a later pair fails. There is no transaction-like grouping of multiple alterations.

Test signals: usage tests for odd/missing arguments, successful alter of table configuration, error propagation for invalid config/URI, and multi-pair behavior where the loop stops on the first failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_alter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_backup.c -->
## sources/storage-engines/wiredtiger/src/utilities/util_backup.c

Purpose: implements `wt backup`, copying WiredTiger backup cursor files into a target directory, optionally restricted to named targets.

Important APIs/types/functions: `util_backup` parses `-t uri` options into a `target=(...)` backup cursor config string, opens `session->open_cursor(session, "backup:", ...)`, iterates file names from the backup cursor, and calls static `copy`. `copy` builds `directory/name` and uses internal `__wt_copy_and_sync` to copy and sync files safely.

Control flow: option parsing accumulates comma-separated quoted targets in a scratch buffer. Exactly one positional destination directory is required. After opening `backup:`, the command loops `cursor->next` and `cursor->get_key`; each file is copied, and `WT_NOTFOUND` terminates normally. Scratch memory is freed on all exits, but the cursor is not explicitly closed in this function and relies on session cleanup.

State and persistence behavior: creates filesystem copies of WiredTiger files in the supplied directory. The backup cursor stabilizes the list of files; `__wt_copy_and_sync` handles durability-sensitive copy behavior. The command does not create the destination directory and does not remove partial copies on failure.

Dependencies and integration points: integrates with WiredTiger backup cursor implementation, incremental/hot backup machinery in the engine, filesystem helpers, global `home` and `verbose` output, and `util_err`-style error reporting.

Risks: target config is assembled by quoting raw CLI target strings; unusual quotes or commas in URIs could stress config parsing. Destination path allocation is based on string lengths and assumes a simple slash separator. A mid-copy error leaves a partial backup directory for the operator to clean up. Not explicitly closing the backup cursor could delay release until session close, though the command exits immediately after.

Test signals: full backup smoke tests comparing copied files with a reopenable database, targeted backup tests for `-t`, missing destination argument usage, invalid target errors, verbose output, destination permission errors, and failure injection around `__wt_copy_and_sync`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_backup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_compact.c -->
## sources/storage-engines/wiredtiger/src/utilities/util_compact.c

Purpose: implements `wt compact`, exposing `WT_SESSION.compact` from the CLI for a single object URI with optional compact configuration.

Important APIs/types/functions: `util_compact` parses `-c config` and `-?`, normalizes the single positional argument through `util_uri(session, *argv, "table")`, and calls `session->compact(session, uri, config)`.

Control flow: after parsing, exactly one URI argument is required. The URI is allocated, used for the compact call, then freed. Errors are reported as `session.compact: uri`, and the function returns the WiredTiger return code.

State and persistence behavior: compaction can rewrite data files and reclaim space according to library configuration. This wrapper does not perform checkpoints or flushes itself; persistence and concurrency behavior are owned by `WT_SESSION.compact`.

Dependencies and integration points: dispatched from `util_main.c`; uses URI normalization, getopt, usage/error helpers, and the public session compact API. Global open flags such as readonly/recovery are handled before command execution.

Risks: compaction can be long-running and interacts with active database state; the CLI has no progress reporting beyond engine behavior. Passing arbitrary config strings relies on the library for validation. A shorthand name defaults to `table:`, which may surprise users intending a file URI unless they include a prefix.

Test signals: usage tests, compacting a table with and without config, invalid URI/config error propagation, readonly failure behavior, and file-size or statistics checks showing compaction did work when possible.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_compact.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_cpyright.c -->
## sources/storage-engines/wiredtiger/src/utilities/util_cpyright.c

Purpose: implements the `wt copyright` command by printing licensing and contact text.

Important APIs/types/functions: the single function `util_copyright` emits fixed strings to stdout using `printf`. It has no arguments and no return code.

Control flow: straight-line output of copyright, GPL notice, warranty disclaimer, GPL URL, and MongoDB contact text. Dispatch in `util_main.c` calls it directly and exits without opening a database.

State and persistence behavior: no database, filesystem, or process-global state is modified except stdout.

Dependencies and integration points: included in the utility build and dispatched by the `copyright` command case. It depends only on the C runtime and `util.h`.

Risks: text can drift from actual licensing policy or current copyright years. Since it prints directly, output errors are not checked and cannot influence exit status.

Test signals: `wt copyright` should run without a database home and print the expected stable notice. Packaging/legal review is the meaningful non-code validation signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_cpyright.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_create.c -->
## sources/storage-engines/wiredtiger/src/utilities/util_create.c

Purpose: implements `wt create`, creating a WiredTiger object from the CLI with optional session create configuration.

Important APIs/types/functions: `util_create` parses `-c config`, normalizes the single positional name with `util_uri(..., "table")`, and invokes `session->create(session, uri, config)`. `usage` documents `create [-c configuration] uri`.

Control flow: option parse, require exactly one argument, allocate normalized URI, call create, report `session.create: uri` on error, free URI, return the WiredTiger status.

State and persistence behavior: creates table/file/tiered/etc metadata and associated objects through the session API. `util_main.c` opens the connection with `create` config for this command, so the database home can be initialized if needed.

Dependencies and integration points: uses `util_uri` defaulting to table, `util_err`, and `WT_SESSION.create`. The broader create semantics depend on schema, metadata, logging, and recovery settings configured when the connection was opened.

Risks: defaulting unprefixed names to `table:` is convenient but requires explicit prefixes for other object types. Arbitrary config is passed through without CLI-level filtering. Failure after partial schema creation is handled by library schema code, not the wrapper.

Test signals: creating default table names, explicit URI prefixes, invalid config failures, create in a new home, duplicate object errors, and successful reopen/list after create.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_downgrade.c -->
## sources/storage-engines/wiredtiger/src/utilities/util_downgrade.c

Purpose: implements `wt downgrade`, reconfiguring a database's compatibility release through the connection API.

Important APIs/types/functions: `util_downgrade` requires `-V release`, formats `compatibility=(release=%s)` into a fixed buffer, obtains `session->connection`, and calls `conn->reconfigure(conn, config_str)`. Usage documents `downgrade -V release`.

Control flow: parse only `-V` and `-?`, reject extra positional arguments or missing release, build the compatibility config string, reconfigure the connection, and return `0` or `util_err` output.

State and persistence behavior: changes persistent compatibility metadata and can influence log/file removal and future open compatibility. It does not itself force checkpoints or close/reopen; `util_main.c` closes the connection after the command, allowing WiredTiger close processing to persist required state.

Dependencies and integration points: depends on `WT_CONNECTION.reconfigure` compatibility handling and the open connection/session from `util_main.c`. It interacts indirectly with recovery/log code that honors downgrade flags and forced log removal.

Risks: fixed 128-byte buffer assumes release strings are short; oversized strings fail via `__wt_snprintf`. The release string is not sanitized by the wrapper and relies on config validation. Downgrade is a high-impact operation that can restrict future access by newer features.

Test signals: valid release downgrade, missing/extra argument usage, invalid release rejection, close/reopen with downgraded compatibility, and log removal behavior when newer log files exist.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_downgrade.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_drop.c -->
## sources/storage-engines/wiredtiger/src/utilities/util_drop.c

Purpose: implements `wt drop`, removing a WiredTiger object by URI from the CLI.

Important APIs/types/functions: `util_drop` parses only `-?`, normalizes the single positional object through `util_uri(..., "table")`, and calls `session->drop(session, uri, "force")`.

Control flow: require one argument, allocate URI, invoke forced drop, report `session.drop: uri` on failure, free URI, and return the WiredTiger return code.

State and persistence behavior: deletes schema metadata and backing files through the session drop API. The hard-coded `force` config makes missing or partially damaged objects more permissive than a default drop, depending on library semantics.

Dependencies and integration points: uses `util_uri`, `util_err`, and public schema drop. It is dispatched after connection open and therefore observes global open modes like readonly, salvage, and recovery options.

Risks: forced drop is destructive and there is no confirmation prompt. Shorthand names default to tables. Any partial failure cleanup is delegated to WiredTiger schema code. In active systems, drop concurrency behavior is governed by the engine, not this wrapper.

Test signals: dropping an existing table, forced behavior for missing objects, readonly error propagation, shorthand and explicit URI handling, and list/reopen verification that metadata and files are gone.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_drop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_dump.c -->
## sources/storage-engines/wiredtiger/src/utilities/util_dump.c

Purpose: implements `wt dump`, including standard dump format, JSON dump format, pretty/hex dump cursor modes, checkpoint and timestamp reads, key/range/window selection, reverse scans, and an interactive explore mode that can inspect and mutate records.

Important APIs/types/functions: top-level `util_dump` parses options and opens dump cursors. Format helpers include `get_dump_type`, `dump_prefix`, `dump_suffix`, `dump_json_begin/end/separator/table_end`, `print_config`, `print_record`, `dump_config`, `dump_table_config`, `dump_table_parts_config`, and `dump_projection`. Data helpers include `dump_all_records`, `dump_record`, and `time_pair_to_timestamp`. Explore helpers manage command parsing and bookmarks through `dump_explore_*`. JSON constants come from `util_dump.h`.

Control flow: after parsing, the command validates format option compatibility, opens optional output, emits JSON envelope if needed, then loops over one URI or multiple URIs for JSON. For timestamp reads it starts a snapshot transaction with a read timestamp built from decimal or `(high,low)` input. It opens a cursor with `checkpoint=...` and `dump=<type>`, adjusts history store dump cursors to ignore tombstones when no timestamp is specified, prints metadata/config headers, applies optional cursor bounds, and dumps all records or a requested key/window. Explore mode bypasses file output and runs a command loop for cursor movement, search, bounds, insert/update/delete, bookmarks, metadata printing, and window changes.

State and persistence behavior: normal dump paths are read-only except for opening a read transaction when `-t` is used. Explore mode can mutate data with insert/update/delete. Output is written to stdout or an opened file and close errors are propagated. Dump metadata includes table config plus colgroup/index config. Projection dumps rewrite config to match projected value formats/columns. JSON output includes a version marker and table arrays expected by `util_load_json.c`.

Dependencies and integration points: integrates with dump cursor configuration (`dump=print|hex|pretty|pretty_hex|json`), metadata create cursor, WiredTiger config parser extension API, cursor bounds/search/search_near, history store cursor internals, JSON escaping helpers, `util_uri`, `util_str2num`, `util_open_output_file`, and load-side JSON/dump compatibility.

Risks: dump/load compatibility is format-sensitive; changing header strings, JSON structure, config printing, or projection rewriting can break `wt load`. Explore mode uses simple space tokenization, so keys/values containing spaces are awkward or unsupported. The `-k` JSON path rewrites the key as `"key0" : "..."`, tying behavior to dump cursor JSON key syntax. Cursor bounds are cleared only after use; errors in bound handling must not leave state for reused cursors. History store tombstone bypass reaches into dump cursor internals. Timestamp parsing accepts decimal or parenthesized pairs and can silently represent a different view if input is misunderstood.

Test signals: round-trip `wt dump | wt load`, JSON round-trip for multiple tables, hex/pretty output comparisons, checkpoint and timestamp dump snapshots, range lower/upper bounds, reverse scans, key search with and without `-n`, window truncation at table ends, projection dumps, history store dumps, output-file close errors, invalid option combinations, and explore-mode smoke tests for non-mutating and mutating commands.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_dump.h -->
## sources/storage-engines/wiredtiger/src/utilities/util_dump.h

Purpose: declares the JSON dump format marker and version constants shared by dump and JSON load code.

Important APIs/types/functions: defines `DUMP_JSON_VERSION_MARKER` as `WiredTiger Dump Version`, `DUMP_JSON_CURRENT_VERSION` as `1`, and `DUMP_JSON_SUPPORTED_VERSION` as `1`.

Control flow: no executable flow. `util_dump.c` emits the marker/current version in JSON output; `util_load_json.c` requires the marker and rejects versions newer than supported.

State and persistence behavior: controls serialized JSON dump compatibility. Changing these constants changes the accepted or emitted on-disk/interchange dump format.

Dependencies and integration points: included by both JSON-producing dump code and JSON-consuming load code. It is part of the implicit file-format contract for `wt dump -j` and `wt load -j`.

Risks: bumping `DUMP_JSON_CURRENT_VERSION` without updating parser support will make fresh dumps unloadable by the same utility. Accepting a supported version without parser changes can misload data if structure changed.

Test signals: JSON dump/load round trips should assert the marker is present, current version is emitted, supported version is accepted, and a higher version is rejected with `ENOTSUP`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_dump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_list.c -->
## sources/storage-engines/wiredtiger/src/utilities/util_list.c

Purpose: implements `wt list`, printing metadata object names and optionally full config and checkpoint details.

Important APIs/types/functions: `util_list` parses `-c`, `-f output`, `-v`, and optional URI. `list_print` scans `WT_METADATA_URI`. `list_print_checkpoint` reads checkpoint lists with `__wt_metadata_get_ckptlist`, obtains allocation size via `list_init_block`, decodes checkpoint addresses with `__wt_block_ckpt_decode`, and prints sizes via `list_print_size`.

Control flow: command normalizes optional URI through `util_uri`, opens optional output, and calls `list_print`. `list_print` scans metadata in key order, filters by URI prefix when supplied, suppresses system metadata/history store unless verbose/checkpoint output is requested, prints keys, and optionally prints checkpoint and config details. Missing requested URI returns a not-found message and exit code `1`. Checkpoint printing iterates checkpoints, prints name/time/size, decodes raw block checkpoint fields when available, and ignores decode errors after reporting them.

State and persistence behavior: read-only metadata inspection. It writes output to stdout or a user file and propagates close errors. It allocates/frees metadata config strings and checkpoint lists.

Dependencies and integration points: uses metadata cursor APIs, extension API metadata/config parser functions, block checkpoint decoding, WiredTiger size constants, utility output-file helpers, and `util_uri`. It depends on metadata config containing `allocation_size` for accurate checkpoint address decoding.

Risks: URI filtering is prefix-based, so a requested prefix can match multiple related metadata entries. Verbose/checkpoint modes expose internal system entries otherwise hidden. `ctime` output is locale/timezone sensitive. Checkpoint decode uses a dummy `WT_BLOCK` initialized mainly with allocation size, which the source itself notes as a kludge.

Test signals: listing empty/new homes, normal object listing excluding metadata/history store, verbose full schema output, checkpoint output for objects with multiple checkpoints, output redirection and close failure, URI filter not found, system entry visibility under `-v`/`-c`, and damaged checkpoint address handling that reports but continues.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_load.c -->
## sources/storage-engines/wiredtiger/src/utilities/util_load.c

Purpose: implements `wt load` for the classic WiredTiger dump format and dispatches JSON input to `util_load_json`. It reconstructs object metadata, optionally renames objects, applies command-line config overrides, creates objects, and inserts dumped key/value records.

Important APIs/types/functions: `util_load` parses `-a`, `-f`, `-j`, `-n`, `-r`, and config URI/string pairs. Classic dump helpers are `load_dump`, `config_read`, `config_reorder`, `config_update`, `config_rename`, `config_exec`, `config_list_add`, `config_list_free`, `format`, and `insert`. Global flags track append, rename target, command config, JSON mode, and no-overwrite.

Control flow: `util_load` redirects stdin if `-f` is supplied, rejects mutually exclusive append/no-overwrite, records extra config pairs, and either calls `util_load_json` or `load_dump`. `load_dump` reads and validates the three-line dump header plus paired metadata lines until `Data`, reorders table configs before dependent entries, applies rename/config updates, creates objects, opens a dump cursor with print/hex plus append/overwrite settings, validates append only for record-number keys, inserts alternating key/value lines, closes the cursor, and flushes the URI.

State and persistence behavior: creates schema objects and inserts records into the database. `config_update` removes persisted fields that must not be reused (`filename`, `id`, checkpoint fields, `source`, version, etc.) before create, preventing loaded objects from colliding with original storage identity. Rename rewrites table/file/tiered/colgroup/index URI names. `util_flush` is called after successful cursor close to force loaded content durable enough for command completion.

Dependencies and integration points: depends on `util_read_line` dump decoding, dump cursor insert modes, `__wt_config_merge`, schema create, cursor insert, JSON loader for `-j`, URI/config conventions emitted by `util_dump.c`, and `util_main.c` opening the connection with `create` for load commands.

Risks: command-global static flags make the implementation single-shot per process. Config matching for command overrides uses prefix matching and then rejects zero or multiple matches; ambiguous prefixes can fail. Rename mutates URI strings in place while searching colon separators and must preserve suffixes. The loader rejects key/value format changes but other config overrides can still create incompatible schemas. Partial load can leave created objects and inserted records when later insert fails.

Test signals: classic dump/load round trips for row and column stores, hex and print formats, append loads for record-number keys, no-overwrite duplicate failures, `-a`/`-n` mutual exclusion, rename of table with indices/colgroups, command config override matching and ambiguity errors, rejection of key/value format override, malformed dump headers, cursor close/flush failure propagation, and JSON dispatch.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_load.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_load.h -->
## sources/storage-engines/wiredtiger/src/utilities/util_load.h

Purpose: shared header for classic and JSON load implementations. It declares the config-list container, load config manipulation helpers, JSON load flags, and `util_load_json`.

Important APIs/types/functions: `CONFIG_LIST` stores a NULL-terminated array of alternating URI/config strings with entry and allocation counts. Functions declared here include `config_exec`, `config_list_add`, `config_list_free`, `config_reorder`, `config_update`, and `util_load_json`. Flags are `LOAD_JSON_APPEND` and `LOAD_JSON_NO_OVERWRITE`.

Control flow: no executable code, but it defines the shared interface allowing `util_load_json.c` to reuse classic load metadata creation and config override logic before inserting JSON records.

State and persistence behavior: `CONFIG_LIST` owns heap strings that eventually drive persistent schema creation. JSON flags map CLI behavior to cursor config (`append`, `overwrite=false`) in the JSON loader.

Dependencies and integration points: included by `util_load.c` and `util_load_json.c`, and indirectly tied to dump/load format compatibility. Flag generation comments indicate values are maintained by an automatic flag-value process.

Risks: callers must maintain alternating URI/config order and NULL termination or `config_exec`/update loops will walk invalid memory. Adding flags requires preserving generated value conventions. Since JSON and classic load share helpers, changes in config update behavior affect both formats.

Test signals: compile-time coverage by both loaders, config-list growth/free tests through large metadata inputs, JSON append/no-overwrite behavior, and classic/JSON round-trip tests that exercise shared reorder/update/create helpers.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_load.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_load_json.c -->
## sources/storage-engines/wiredtiger/src/utilities/util_load_json.c

Purpose: implements `wt load -j`, parsing JSON generated by `wt dump -j`, recreating object metadata, and inserting JSON dump cursor data.

Important APIs/types/functions: `JSON_INPUT_STATE` tracks current line, token pointer, peeked token metadata, raw key/value accumulation buffer, filename, and line number. Core parser helpers are `json_peek`, `json_expect`, `json_skip`, `json_strdup`, `json_kvraw_append`, `json_column_group_index`, `json_top_level`, and `json_data`. Entry point `util_load_json` initializes state and invokes `json_top_level`.

Control flow: `util_load_json` reads the first line and starts top-level parsing. `json_top_level` requires an opening object, then the version marker before any table. For each table, it skips to recognized markers (`config`, `colgroups`, `indices`, `data`), accepts metadata sections before `data`, builds a `CONFIG_LIST`, and when `data` arrives calls `json_data`. `json_data` reorders/updates config, creates objects, opens a `dump=json` cursor with append/no-overwrite flags, reconstructs raw key and value text by collecting token spans across lines, validates record-number keys are in order, and inserts each object. Token helpers support one-token lookahead and error messages with filename/line/position.

State and persistence behavior: creates schema and inserts records, then closes the cursor and flushes the loaded URI. Parser state owns line and raw buffers; `CONFIG_LIST` owns metadata strings. Serialized compatibility is governed by `DUMP_JSON_VERSION_MARKER` and `DUMP_JSON_SUPPORTED_VERSION`. Append mode skips setting cursor keys; no-overwrite maps to cursor `overwrite=false`.

Dependencies and integration points: tightly paired with `util_dump.c` JSON output and dump cursor JSON syntax. Reuses classic load helpers for reorder, config update, create, and command-line overrides. Depends on internal JSON token/string helpers, `util_read_line`, cursor dump JSON parsing, and `util_flush`.

Risks: `json_skip` searches for marker strings with `strstr`, so unexpected marker-like text in skipped regions could confuse parsing if the dump structure changes. Raw key/value reconstruction depends on token positions and inserted spaces; it is intentionally coupled to dump cursor expectations. Record-number validation requires contiguous ordered recnos unless append mode is used. The function frees config state both in `json_top_level` and after data; the current paths reset state, but ownership changes must be careful. Partial loads can persist objects/records before a later parse or insert error.

Test signals: JSON dump/load round trips for simple, indexed, and column-group tables; multiple table JSON files; supported and unsupported version markers; malformed token position diagnostics; strings with JSON escapes; multi-line key/value objects; record-number out-of-order rejection; append and no-overwrite flags; command-line rename/config overrides via shared helpers; and cursor close/flush error propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_load_json.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_loadtext.c -->
## sources/storage-engines/wiredtiger/src/utilities/util_loadtext.c

Purpose: implements `wt loadtext`, a simpler loader for flat text records into existing string-value row-store or record-number column-store objects.

Important APIs/types/functions: `util_loadtext` parses `-f` and a single URI. Static `text` opens a cursor with `append,overwrite`, validates formats, and calls static `insert`. `insert` reads key/value or value-only lines using `util_read_line` and inserts them through the cursor.

Control flow: optional `-f` redirects stdin. The command normalizes one URI with `util_uri`, then `text` opens a cursor. It requires `value_format == "S"` and key format either `"S"` or `"r"`. Row-store string keys read alternating key and value lines; record-number keys read only values and append them. After insertion it closes the cursor and flushes the URI.

State and persistence behavior: inserts or overwrites records in an existing object and flushes on success. For record-number column stores it appends new recnos. For string-key row stores it overwrites matching keys because the cursor was opened with overwrite.

Dependencies and integration points: uses public cursor insert, dump/text line decoding, `util_uri`, `util_flush`, and global verbose progress output. It is dispatched by `util_main.c`, which opens the connection with `create` even though the target object must already exist.

Risks: only supports simple string values and string or record-number keys. Input is line-oriented, so embedded newlines require whatever escaping `util_read_line` supports. On read errors inside `insert`, allocated buffers are not freed on the immediate return paths before the function exits, which is a small leak in a short-lived utility process. Partial loads remain if a later line or insert fails.

Test signals: loadtext into string-key tables with alternating lines, loadtext into record-number tables with value-only lines, format rejection for non-string values or unsupported key formats, file redirection errors, verbose progress every 100 inserts, cursor close/flush failure, and partial input EOF behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_loadtext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_main.c -->
## sources/storage-engines/wiredtiger/src/utilities/util_main.c

Purpose: main entry point and dispatcher for the `wt` command-line utility. It parses global options, builds the `wiredtiger_open` configuration, opens the connection/session, handles special modes such as recovery, salvage, readonly, metadata verify, encryption secret key, live restore, and disaggregated checkpoint pickup, then dispatches to subcommand handlers.

Important APIs/types/functions: global state includes `home`, `progname`, `usage_prefix`, `verbose`, and static `command`. `wt_explicit_zero` securely clears secret buffers. `util_disagg_pick_up_latest_checkpoint` obtains a page log, asks for the latest complete checkpoint, and reconfigures the connection with `disaggregated=(checkpoint_meta="...")`. `usage` prints global options and command list. `main` selects command function pointers. `util_uri` rejects unsupported cursor namespaces and prefixes shorthand names.

Control flow: `main` checks build/runtime WiredTiger version compatibility, parses global options, validates mutually exclusive log/recovery/salvage/readonly combinations, maps the command string to a handler and optional connection/session config, builds one open config string, opens WiredTiger, zeroes secret key copies, optionally exits after metadata verify, opens a session, picks up disaggregated follower checkpoint metadata, invokes the command, optionally applies backward compatibility release 3.3 on close, closes the connection, and returns shell success/failure. `copyright` and `-V` exit before database open.

State and persistence behavior: controls process-global home/verbose/program state and connection open behavior. Recovery mode choices map to `log=(recover=error|on)` or logging disabled; salvage/readonly/verify metadata/live restore/encryption are persisted or acted on by `wiredtiger_open`. Secret key strings are explicitly zeroed in argv, duplicated storage, and generated config buffers before free. Disaggregated checkpoint pickup can reconfigure connection metadata from page-log checkpoint metadata before command execution.

Dependencies and integration points: central integration point for every `util_*` command, `wiredtiger_open`, version API, global verbose event handler, page log extension API, connection/session reconfigure/open/close, command-specific connection configs (`create`, statistics, printlog logoff, verify prefetch), and utility memory/error helpers.

Risks: open config is manually size-calculated and formatted; missing length components would risk truncation, though `__wt_snprintf` errors are checked. Secret key handling is careful but includes temporary copies in command-line/config memory. Command dispatch is string/switch based, so new commands require updates here, `util.h`, and CMake sources. `util_uri` rejects `backup:`, `config:`, and `statistics:` for command operands, but commands that need those namespaces must bypass it. Disaggregated page-log checkpoint metadata is embedded in a quoted config string and depends on metadata escaping assumptions.

Test signals: global usage/version/copyright without a database, invalid option combination errors, opening with `-h`, `-C`, `-E`, `-R`, `-S`, `-r`, `-L`, `-m`, `-p`, and live restore options, secret-key zeroing under sanitizer or audit tests, dispatch for every listed command, create/load/loadtext opening new homes, printlog disabling logging, verify prefetch configs, disaggregated follower checkpoint pickup success/WT_NOTFOUND/missing method/failure, and `util_uri` prefix/default/rejection behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_main.c -->
