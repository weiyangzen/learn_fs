# Research Group: subset-b-009065

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/alter.c -->
# sources/storage-engines/wiredtiger/test/format/alter.c

## Purpose
`alter.c` supplies the format-test worker that periodically calls `WT_SESSION::alter` on a randomly selected table. Its only mutated metadata is `access_pattern_hint`, alternating between `none` and `random`, so it stresses metadata alter paths without changing cache-residency settings that could make eviction impossible in small-cache runs.

## Important APIs, Types, And Functions
The file exports `WT_THREAD_RET alter(void *)`, declared in `format.h` and launched as an auxiliary worker when `ops.alter` is enabled. It uses `SAP` for session event-handler private data, `TABLE` from the global table array, `g.wts_conn`, `g.extra_rnd`, `g.workers_finished`, and helpers `wt_wrap_open_session`, `wt_wrap_close_session`, `mmrand`, `table_select`, and `trace_msg`.

## Control Flow
The thread opens a WiredTiger session, then loops until `g.workers_finished`. Each iteration chooses a 1-10 second period, builds an alter config string, toggles the next value, selects a table using non-data RNG selection, traces start/stop, and retries while the return is nonzero and not `EBUSY`. After the attempt, it sleeps in one-second increments so shutdown is responsive.

## State And Persistence Behavior
The state change is persisted in WiredTiger metadata for the chosen object through `session->alter`. The thread keeps only local counters and the next access-hint boolean. It does not write format config files or data records.

## Dependencies And Integration Points
It depends on the shared `format.h` globals, inline RNG/table helpers, and WiredTiger metadata API. Backup/checkpoint/compact threads may race with this metadata operation, and `EBUSY` is treated as an expected collision signal rather than a test failure.

## Risks And Test Signals
The main risk is broadening alter settings to options with stronger cache or data-format effects; the current code intentionally avoids cache-resident toggles. Useful signals are trace lines for alter start/stop, frequent `EBUSY` under metadata pressure, and the absence of fatal `session.alter` errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/alter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/backup.c -->
# sources/storage-engines/wiredtiger/test/format/backup.c

## Purpose
`backup.c` implements hot backup testing for format runs, including full backups, block incremental backups, restart recovery of incremental backup source IDs, copying of format-specific files, and verification by opening and verifying the backup copy.

## Important APIs, Types, And Functions
The exported worker is `WT_THREAD_RET backup(void *)`. Static helpers include `check_copy`, `copy_blocks`, `copy_format_files`, `restore_backup_info`, `save_backup_info`, and the `ACTIVE_FILES` list utilities. It uses WiredTiger backup cursors (`session->open_cursor("backup:")`), duplicate incremental backup cursors, `WT_BACKUP_RANGE` and `WT_BACKUP_FILE`, `__wt_copy_and_sync`, `wts_open`, `wts_verify`, and `wts_close`.

## Control Flow
The worker opens a session, initializes two alternating active-file lists, optionally restores the previous incremental backup ID/list on reopen, and then sleeps before each backup cycle. Backup work is serialized with named-checkpoint work through `g.backup_lock`. A full backup creates or refreshes `BACKUP`, copies `CONFIG` and `CONFIG.keylen*`, opens a backup cursor, copies each key either as a whole file or via `copy_blocks`, closes the cursor, releases the lock, prunes files no longer active, saves incremental metadata, and verifies the resulting backup in a separate `CHECK.<id>` directory. Incremental mode periodically restarts with a full backup.

## State And Persistence Behavior
The file persists backup content under `g.home/BACKUP`, verification copies under `CHECK.<id>`, and restart metadata in `BACKUP_INFO` using an atomic temporary-file rename. Incremental block copies use raw `open`, `lseek`, `read`, and `write` into the backup directory, while full-file copies rely on WiredTiger/test utility copy helpers. Active file lists represent backup membership so removed source files are unlinked from the backup.

## Dependencies And Integration Points
It integrates with configuration values `backup`, `backup.incremental`, `backup.incr_granularity`, and `backup.live_restore`; with checkpoint through `g.backup_lock`; with format config persistence through copied `CONFIG` files; and with verification via `wts_prepare_discover` and `wts_verify`. It also uses global `g.backup_id` and `g.backup_incr`, which are set by config parsing.

## Risks And Test Signals
Risks include stale incremental IDs after uncheckpointed metadata, partial system-call copies, active-file pruning mistakes, and backup/checkpoint metadata races. Expected test signals include trace messages for backup cursor open/copy/verify, tolerated `EBUSY` on backup cursor open, `ENOENT` causing incremental restart skip, and fatal verification failures if a backup cannot be reopened or verified.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/backup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/bulk.c -->
# sources/storage-engines/wiredtiger/test/format/bulk.c

## Purpose
`bulk.c` loads initial table content for format tests. It supports normal bulk append, non-bulk insert fallback, mirrored table loading from a base cursor, timestamped transaction batches, adaptive row-count reduction on cache pressure, and an initial checkpoint for durability.

## Important APIs, Types, And Functions
The public entry point is `void wts_load(void)`. Core helpers are `table_load`, `bulk_begin_transaction`, `bulk_commit_transaction`, and `bulk_rollback_transaction`. It uses `TABLE`, `SAP`, `WT_CURSOR`, `WT_ITEM`, key/value generation helpers, `read_op`, `wt_wrap_open_cursor`, timestamp helpers, `config_single`, and `config_print`.

## Control Flow
`wts_load` loads the single table or, in multi-table mode, first loads the base mirror and then each remaining table. `table_load` opens a session, optionally opens the base mirror cursor, decides whether `bulk,append` is legal, initializes key/value buffers, optionally begins a timestamped transaction, and iterates through configured rows. Row-store keys are generated; values either come from `val_gen` or the base mirror. Inserts are traced when bulk tracing is enabled. On `WT_CACHE_FULL` or `WT_ROLLBACK` for non-mirror loads, it rolls back any active batch, reduces insert/write percentages in favor of deletes, and shortens the configured row count.

## State And Persistence Behavior
Successful inserts populate WiredTiger tables. Timestamped loads advance `g.timestamp`, assign read/commit timestamps, and call `timestamp_once` so oldest/stable timestamps move and cache is not pinned. If the load exits early, it rewrites `runs.rows` in the in-memory config and persists a new `CONFIG`. After loading, `table->rows_current` is initialized and non-in-memory runs take a checkpoint.

## Dependencies And Integration Points
Bulk loading depends on configuration normalized by `format_config.c`, disaggregated-storage state, mirror configuration, transaction timestamp configuration, and value/key generators. It integrates with later operation threads by establishing `rows_current`, with mirror verification by making mirrored tables byte-compatible, and with recovery by checkpointing loaded data.

## Risks And Test Signals
Important risks are using bulk load with reverse collators or disaggregated storage, mismatched mirror loads, timestamp batches pinning cache, and silent row-count drift after cache-full handling. Test signals include progress tracking every early 10 rows or later 5K rows, trace bulk records, row-count rewrites in `CONFIG`, and assertion failures if a mirrored table cannot load matching rows.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/bulk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/checkpoint.c -->
# sources/storage-engines/wiredtiger/test/format/checkpoint.c

## Purpose
`checkpoint.c` configures WiredTiger library checkpoints and implements the format checkpoint worker. It tests ordinary checkpoints, named checkpoints, named checkpoint drops, tiered `flush_tier` checkpoints, backup/checkpoint serialization, and checkpoint verification.

## Important APIs, Types, And Functions
It exports `void wts_checkpoints(void)` and `WT_THREAD_RET checkpoint(void *)`. It uses `WT_CONNECTION::reconfigure`, `WT_SESSION::checkpoint`, `wts_verify_mirrors`, `lock_try_writelock`, `lock_writeunlock`, `mmrand`, and config values for checkpoint wait/log size and tiered flush frequency.

## Control Flow
`wts_checkpoints` delays enabling WiredTiger's internal checkpoint server until after initial load, then reconfigures the connection if `checkpoint=wiredtiger`. The worker opens a session and loops until shutdown. Every cycle chooses either `flush_tier`, a named checkpoint, a drop-all named-checkpoint operation, or an unnamed checkpoint. Named checkpoint operations try to acquire `g.backup_lock` so they do not conflict with backup cursor semantics. After checkpoint completion, expected `EBUSY` is tolerated only for cases where named checkpoint metadata can race. Mirrored content is verified at the checkpoint name unless disaggregated storage disables checkpoint cursors.

## State And Persistence Behavior
Checkpoints persist table state and optionally create/drop named snapshots in WiredTiger metadata. Tiered storage flushes object state to the configured storage source. The file does not persist format-side files, but it directly affects recovery and backup visibility.

## Dependencies And Integration Points
The worker depends on `g.checkpoint_config`, `g.tiered_storage_config`, `g.disagg_storage_config`, `g.backup_lock`, and generated configuration values. It coordinates with backup, tiered storage, mirror verification, and disaggregated storage limitations.

## Risks And Test Signals
Risks include checkpoint-induced cache pressure during initial load, backup starvation if locking is wrong, unsupported named checkpoints for tiered/disaggregated tables, and false failures from sweep-server `EBUSY`. Signals include trace start/stop lines with checkpoint config, mirror verification failures, and assertions when unexpected return codes occur.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/checkpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/checksum.c -->
# sources/storage-engines/wiredtiger/test/format/checksum.c

## Purpose
`checksum.c` computes a deterministic FNV-1a hash across all known row-store tables at the stable timestamp. It is used by disaggregated multi-node validation to compare leader and follower database contents.

## Important APIs, Types, And Functions
The exported function is `uint64_t checksum_database(WT_SESSION *)`. Static helpers are `checksum_key`, `checksum_value`, and `checksum_table`, with `struct checksum_table_arg` carrying the session and rolling hash. It uses `tables_apply`, `atou32`, `wt_wrap_begin_transaction`, `session->timestamp_transaction_uint`, `wt_wrap_open_cursor`, and cursor iteration.

## Control Flow
`checksum_database` initializes the FNV hash and applies `checksum_table` to every table. Each table checksum asserts row-store type, begins a read transaction, pins the read timestamp to `g.stable_timestamp`, opens a cursor, walks records in key order, hashes the numeric key portion after any configured prefix, hashes the value bytes, closes the cursor, and rolls back the read transaction.

## State And Persistence Behavior
The function is read-only. It opens timestamped read transactions but never commits, writes, or persists files. Its output hash is stored by callers, notably the shared-memory `DISAGG_MULTI_DB_HASH` in multi-node disaggregated tests.

## Dependencies And Integration Points
It depends on row-store key encoding, `BTREE_PREFIX_LEN`, stable timestamp maintenance, and the table list. It integrates directly with `format_disagg.c` for leader/follower validation.

## Risks And Test Signals
Risks include applying it to column-store tables, hashing at a stale or unset stable timestamp, and key parsing assumptions if key format changes. The primary test signal is a matching leader/follower hash; mismatches cause disaggregated validation failure and optional preservation of layered tables.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/checksum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/compact.c -->
# sources/storage-engines/wiredtiger/test/format/compact.c

## Purpose
`compact.c` provides foreground and background compaction workers for format. It exercises `WT_SESSION::compact` on selected tables and repeatedly toggles the background compaction server.

## Important APIs, Types, And Functions
The file exports `WT_THREAD_RET background_compact(void *)` and `WT_THREAD_RET compact(void *)`. It uses `session->compact`, `table_select`, `wt_wrap_open_session`, `mmrand`, `GV(BACKGROUND_COMPACT_FREE_SPACE_TARGET)`, and `GV(COMPACT_FREE_SPACE_TARGET)`.

## Control Flow
`background_compact` starts shortly after run start, then every ten minutes randomly enables or disables background compaction with a configured free-space target. On shutdown it always attempts to disable background compaction. `compact` starts within 15 seconds, then every 23 seconds chooses a table and runs foreground compaction with `free_space_target`.

## State And Persistence Behavior
Both workers affect WiredTiger file layout and free-space reclamation. They do not modify logical records or format config files. Background compaction also changes connection-level compaction server state and is explicitly disabled during teardown.

## Dependencies And Integration Points
Compaction is enabled or disabled by `format_config.c` based on in-memory, tiered, and disaggregated storage constraints. Foreground compaction collides naturally with checkpoints, alter, eviction, and workload writes. Background compaction state is also tracked conceptually by global format configuration.

## Risks And Test Signals
Expected return codes include `EBUSY` for races, `ETIMEDOUT` for long compactions, `WT_CACHE_FULL`, and `WT_ROLLBACK`. Unexpected return codes are assertion failures. Risks are enabling compaction for unsupported storage modes, failing to disable the background server, and treating normal contention as fatal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/compact.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/config.sh -->
# sources/storage-engines/wiredtiger/test/format/config.sh

## Purpose
`config.sh` is the generator for the format configuration schema. It writes `format_config.h` and `format_config_def.c` from one ordered list of configuration records, assigning stable numeric offsets used by `GV`, `GVS`, `TV`, and `TVS` macros.

## Important APIs, Types, And Functions
The script emits the `CONFIG` struct, `C_*` flags, `V_GLOBAL_*` and `V_TABLE_*` offset defines, `V_ELEMENT_COUNT`, and `CONFIG configuration_list[]`. It requires `clang-format` and runs `../../dist/s_clang_format` on the generated files.

## Control Flow
The script first writes the header prefix. It then streams a here-document of configuration entries into `format_config_def.c`. For every line beginning with `{"`, it derives an uppercase tag from the config name, chooses `GLOBAL` or `TABLE` based on `C_TABLE`, appends the generated offset to the C initializer, writes a matching `#define` to the header, and increments the offset counter. It appends the sentinel record and final element count, then formats both generated files.

## State And Persistence Behavior
It overwrites generated files in the current `test/format` directory. The ordering of entries is persistent ABI-like state for format's in-memory `CONFIGV` arrays; reordering without regenerating all dependent code would break offset lookups.

## Dependencies And Integration Points
The generated outputs are included by `format.h` and consumed heavily by `format_config.c` and all workers using `GV`/`TV`. The schema spans backup, checkpoints, compression, disaggregation, transaction, workload, stress, tiered storage, and WiredTiger open settings.

## Risks And Test Signals
Risks include missing `clang-format`, accidental manual edits to generated outputs, mismatched offset order, and incorrect `C_TABLE` flags producing wrong global/table access macros. Signals are deterministic regenerated diffs, successful formatting, and compilation failures if the generated enum names drift from code references.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/config_compat.c -->
# sources/storage-engines/wiredtiger/test/format/config_compat.c

## Purpose
`config_compat.c` maps legacy format configuration names to the current dotted schema so old `CONFIG` files remain runnable.

## Important APIs, Types, And Functions
It defines `struct compat_list`, a static mapping array, and exports `void config_compat(const char **namep)`. The function receives a pointer to a config string and may redirect it to a static conversion buffer.

## Control Flow
`config_compat` ignores strings without `=`. For assignment strings, it compares the left-hand side including the equals sign against each legacy `orig` pattern. On match, it builds `current + original_value_suffix` in a static buffer and updates the caller's pointer.

## State And Persistence Behavior
The function has no durable state. It uses a single static `conv[100]`, so callers must consume the converted string before another conversion. The converted name then flows into normal config parsing and persistence through `config_single` and `config_print`.

## Dependencies And Integration Points
It is called early in `config_single`, before `config_find`, allowing the rest of the parser to operate only on the current schema. It integrates with backward-compatible output in `config_print_one`, which can also print historic names for selected settings.

## Risks And Test Signals
Risks include static buffer truncation if a mapped assignment grows beyond 100 bytes, missing aliases for old configs, and prefix mistakes because matching includes the equals sign but not full string tokenization beyond that. Signals are old `CONFIG` files parsing without unknown-key warnings and converted settings appearing under current names in output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/config_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/follower.c -->
# sources/storage-engines/wiredtiger/test/format/follower.c

## Purpose
`follower.c` implements disaggregated-storage follower checkpoint pickup. It polls the configured page log, fetches checkpoint metadata, enforces timestamp safety, and reconfigures a follower connection to a newer checkpoint.

## Important APIs, Types, And Functions
Important functions are `follower_fetch_full_metadata`, `follower_try_pickup_checkpoint`, `follower_read_latest_checkpoint`, and exported worker `WT_THREAD_RET follower(void *)`. It uses `WT_PAGE_LOG`, `WT_PAGE_LOG_HANDLE`, `WT_PAGE_LOG_GET_COMPLETE_CHECKPOINT_ARGS`, `WT_DISAGG_METADATA`, `__wt_disagg_parse_meta`, `timestamp_query`, `conn->reconfigure`, and `conn->get_page_log`.

## Control Flow
The worker opens a session and page-log handle, then loops until `g.workers_finished`. Each cycle clears prior checkpoint metadata, calls `pl_get_complete_checkpoint`, tolerates `WT_NOTFOUND`, and if metadata changed from `g.checkpoint_metadata`, tries to pick it up. Pickup fetches full metadata by reading the metadata page at `metadata_lsn`, parses `oldest_timestamp`, compares it with the follower pinned timestamp, and only reconfigures when safe. The loop sleeps 1-3 seconds between polls.

## State And Persistence Behavior
The follower stores the last accepted checkpoint metadata string in `g.checkpoint_metadata` and changes the WiredTiger connection's disaggregated checkpoint state with `conn->reconfigure`. It allocates/free checkpoint metadata buffers and full metadata buffers but writes no format files.

## Dependencies And Integration Points
It depends on disaggregated page-log configuration, transaction timestamps, pinned timestamp queries, PALI metadata IDs, and global leader/follower state. `format_disagg.c` calls `follower_read_latest_checkpoint` during role switch from leader to follower.

## Risks And Test Signals
Risks include picking a checkpoint whose oldest timestamp is newer than pinned, stale metadata comparison with fixed-size `g.checkpoint_metadata`, page-log implementations without complete-checkpoint support, and memory ownership mistakes around `WT_ITEM.mem`. Signals include follower pickup/skip messages, `WT_NOTFOUND` polling, and validation failures after role switching or multi-node comparison.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/follower.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format.h -->
# sources/storage-engines/wiredtiger/test/format/format.h

## Purpose
`format.h` is the central contract for the WiredTiger format test program. It defines shared constants, generated configuration integration, table/global runtime state, worker thread state, operation enums, and prototypes used across the format source tree.

## Important APIs, Types, And Functions
Key types are `CONFIGV`, `LANE`, `READ_SCAN_ARGS`, `RWLOCK`, `SAP`, `TABLE`, `DISAGG_MULTI_DB_HASH`, `GLOBAL`, `SNAP_OPS`, `SNAP_STATE`, and `TINFO`. Important macros include extension library paths, `BACKUP_INFO_FILE`, `BACKUP_MAX_COPY`, `FORMAT_OPERATION_REPS`, `SESSION_PREFETCH_CFG_*`, `GV/GVS/NTV/NTVS/TV/TVS`, trace flags, checkpoint constants, and `LANE_NUMBER`. It declares all major worker and utility functions.

## Control Flow
The header itself has no runtime flow, but it shapes the program: configuration values live in `tables[0]` for globals and defaults, table-specific values live in `tables[1..ntables]`, workers use `GLOBAL g`, and operation threads use `TINFO` snapshots/cursors/counters. Including `format_inline.h` at the end makes common operations inline across all format files.

## State And Persistence Behavior
`GLOBAL` owns connection handles, home paths, backup IDs, RNG state, timestamp state, disaggregated multi-node handles, checkpoint metadata, and mode booleans. `TABLE` owns URI, type, row counts, key/value generation state, mirror flag, page sizing, and the full `CONFIGV` array. These structures are in-memory, while selected fields drive persisted `CONFIG`, backup metadata, checkpoints, and WiredTiger metadata.

## Dependencies And Integration Points
It depends on WiredTiger internal/test headers through `test_util.h`, generated `format_config.h`, POSIX signal/socket/resource headers, and pthread/WiredTiger lock APIs. It is included by every researched C file and is the integration point among config parsing, workload operations, backup, checkpoint, compaction, disaggregation, timestamping, replay, tracing, and verification.

## Risks And Test Signals
Risks are macro misuse across global/table offsets, assumptions about table slot 0, shared global state races, and ABI drift between generated config offsets and `CONFIGV` arrays. Compile errors, assertion failures in accessor helpers, and inconsistent config dumps are the strongest signals of contract breakage.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format.sh -->
# sources/storage-engines/wiredtiger/test/format/format.sh

## Purpose
`format.sh` is the shell harness for repeatedly running the compiled format binary. It supports smoke tests, randomized stress options, abort/recovery testing, directories of configs, parallel jobs, optional live recording, timeout handling, failure categorization, and cleanup of successful run directories.

## Important APIs, Types, And Functions
The script defines `usage`, `msg`, `fatal_msg`, `verbose`, `force_quit_reason`, `shuffle`, `skip_known_errors`, `categorize_failure`, `report_failure`, `report_running_configs`, `wait_for_process`, `resolve`, `format`, and `check_timer`. It uses `nohup setsid`, `/proc`, `pstree`, `kill`, `grep`, `sed`, `awk`, and optional recording tools.

## Control Flow
After parsing options, the script resolves absolute paths for home and config, changes to the build directory, validates the format and `wt` binaries, and enters a scheduler loop. The loop starts jobs until the parallel limit or total/smoke/config-directory limits are reached, periodically calls `resolve`, handles elapsed-time limits, and exits when no work remains or a force-quit condition drains running jobs.

## State And Persistence Behavior
Each job writes `RUNDIR.N.log` and usually `RUNDIR.N/CONFIG`. Successful jobs are removed. Failed jobs are retained and marked with `format.sh-status`. Abort/recovery jobs copy the directory to `.RECOVER`, rerun recovery, and remove artifacts on success. Out-of-space conditions trigger reporting of still-running configurations.

## Dependencies And Integration Points
The harness assumes a WiredTiger build tree with `./t`, `../../wt`, and config files. It passes `quiet=1` to jobs, can inject trace flags, abort mode, split stress flags, environment variables, and user config overrides. It is independent from the C runtime but drives the main stress-test execution pattern.

## Risks And Test Signals
Risks include shell quoting around `format_binary`, stale log PID parsing, process-group kill behavior, disk exhaustion, and unknown exits being classified as script problems. Signals include counts of successful/failed jobs, retained failed directories, categorized config excerpts, abort/recovery rerun logs, and explicit out-of-space reports.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format_config.c -->
# sources/storage-engines/wiredtiger/test/format/format_config.c

## Purpose
`format_config.c` is the runtime configuration engine for format. It parses explicit config assignments, randomizes unset options, creates table entries, normalizes incompatible feature combinations, sizes cache, records RNG seeds, and writes the final reproducible `CONFIG`.

## Important APIs, Types, And Functions
Public functions include `config_random_generators`, `config_run`, `config_error`, `config_print`, `config_file`, `config_clear`, and `config_single`. Major static passes include `config_random`, `config_table`, `config_cache`, `config_checkpoint`, `config_compression`, `config_disagg_storage`, `config_transaction`, `config_mirrors`, `config_pct`, `config_tiered_storage`, `config_backup_incr`, and `config_in_memory_reset`.

## Control Flow
Config input flows through `config_file` and `config_single`, where optional `tableN.` prefixes extend the table array, legacy names are converted, type-specific parsing validates strings/booleans/powers-of-two/ranges, and `CONFIGV.set` records explicitness. `config_run` then randomizes remaining globals, bounds expensive realloc-debug runs, configures in-memory mode, applies `config_table` to all tables, disables temporarily unsupported salvage, runs storage/transaction/backup/checkpoint/compression/encryption/mirror/statistics/compaction cleanup passes in a deliberate order, sizes cache last, adjusts run length, and reseeds RNGs for predictable replay.

## State And Persistence Behavior
The module mutates `tables`, `ntables`, `TABLE.v[]`, table URIs/page sizes/types, and many `GLOBAL` booleans/counters such as `g.backup_incr`, `g.checkpoint_config`, `g.disagg_storage_config`, `g.transaction_timestamps_config`, `g.operation_timeout_ms`, and `g.base_mirror`. `config_print` persists the final global and per-table values to `g.home_config` unless reopening.

## Dependencies And Integration Points
It depends on `configuration_list` generated by `config.sh`, `config_compat`, replay capability queries, timestamp constraints, extension build flags for compressors, and macros from `format.h`. Every worker depends on the normalized output: backup needs incremental state, checkpoint needs mode, bulk needs table rows/types, disaggregation needs role/page-log state, and operations need percentages.

## Risks And Test Signals
Risks include order-sensitive normalization, explicit/random flag confusion, off-by-one table scans, stale generated offsets, and silently disabling user-requested features. Signals are `WARN` messages, `CONFIG` output, `config_error` listings, parser fatal errors for illegal combinations, and reproducibility when recorded random seeds are reused.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format_config.h -->
# sources/storage-engines/wiredtiger/test/format/format_config.h

## Purpose
`format_config.h` is the generated header that defines the format configuration schema in C form: the `CONFIG` descriptor, config flags, global/table offset constants, and total element count.

## Important APIs, Types, And Functions
It defines `C_TYPE_MATCH`, `CONFIG`, flags `C_BOOL`, `C_IGNORE`, `C_POW2`, `C_STRING`, `C_TABLE`, `C_TYPE_ROW`, `C_TYPE_VAR`, and `C_ZERO_NOTSET`, `V_MAX_TABLES_CONFIG`, all `V_GLOBAL_*` and `V_TABLE_*` offsets, and `V_ELEMENT_COUNT`.

## Control Flow
There is no runtime control flow. The constants are generated in the same order as `configuration_list[]`, then compiled into all code that indexes `TABLE.v[]` or `tables[0]->v[]`.

## State And Persistence Behavior
The header defines the layout size and index positions for each `CONFIGV` array embedded in every `TABLE`. It does not persist files at runtime, but changes to offsets alter how persisted config names map to in-memory values.

## Dependencies And Integration Points
It is generated by `config.sh`, included by `format.h`, and must match `format_config_def.c`. Access macros such as `GV(BACKUP)` and `TV(BTREE_KEY_MAX)` paste these names to retrieve the correct offset.

## Risks And Test Signals
Risks are manual edits, mismatch with `format_config_def.c`, wrong global/table prefix, and stale `V_ELEMENT_COUNT`. Signals are compile errors for missing offsets, runtime misconfiguration, and regenerated diffs after running `config.sh`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format_config_def.c -->
# sources/storage-engines/wiredtiger/test/format/format_config_def.c

## Purpose
`format_config_def.c` is the generated definition of `CONFIG configuration_list[]`, the ordered schema table that drives parsing, randomization, validation, help/error output, and final config printing.

## Important APIs, Types, And Functions
The file defines only `CONFIG configuration_list[]`. Each entry has a name, description, flags, minimum value, random maximum, explicit maximum, and generated offset. Entries cover assertions, backup, block cache, btree shape, cache, checkpoints, debug/stress flags, disaggregation, disk, logging, operations, prefetch, runs, statistics, tiered storage, transactions, and WiredTiger open settings.

## Control Flow
Consumers iterate from `configuration_list[0]` until the `{NULL, NULL, ...}` sentinel. `format_config.c` uses flags to decide whether entries can be randomized directly, whether they are strings, table-scoped, type-specific, or require special handling.

## State And Persistence Behavior
The list is read-only compiled data. Its order and offsets define the in-memory `CONFIGV` layout for every table. Its descriptions are emitted by `config_error`, and names are emitted by `config_print`.

## Dependencies And Integration Points
It is generated from `config.sh` and must stay synchronized with `format_config.h`. It includes `format.h` to use flags, offset constants, and macros such as `MEGABYTE`, `M`, and `RTS_THREADS_MAX`.

## Risks And Test Signals
Risks include schema/order mismatch, incorrect bounds causing invalid random values, wrong `C_IGNORE` classification bypassing special logic, and feature defaults that create unsupported combinations. Signals are parser failures, warnings during normalization, and compile-time failures when offset names do not exist.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format_config_def.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format_disagg.c -->
# sources/storage-engines/wiredtiger/test/format/format_disagg.c

## Purpose
`format_disagg.c` manages disaggregated-storage test orchestration, including multi-node leader/follower setup, output redirection, interprocess synchronization, optional hash validation, role switching, and teardown.

## Important APIs, Types, And Functions
Key functions are `disagg_setup_multi_node`, `disagg_teardown_multi_node`, `disagg_sync_multi_node`, `disagg_is_multi_node`, `disagg_is_mode_switch`, and `disagg_switch_roles`. Static helpers include `disagg_redirect_output` and `disagg_multi_sync_point`. It uses `fork`, `socketpair`, `mmap`, `munmap`, `freopen`, `dup2`, `wts_reopen`, `follower_read_latest_checkpoint`, `timestamp_sync_threads_commit_ts`, and `wts_verify_mirrors`.

## Control Flow
Setup checks whether multi-node disaggregation is enabled, creates leader/follower home directories when not reopening, initializes shared page-log home and shared hash memory, creates a socket pair, and forks. The child becomes follower, rewrites config to follower mode, changes home, redirects output, and keeps one socket end. The parent becomes leader, redirects output, and tracks the child PID. Synchronization writes and reads one byte on the socket. Validation computes per-node database hashes, synchronizes, optionally preserves mismatch state, synchronizes again, then asserts equality. Role switching toggles `g.disagg_leader`; stepping down reopens as follower and picks up a checkpoint, while stepping up reconfigures to leader, advances timestamps, checkpoints, and verifies mirrors.

## State And Persistence Behavior
The file persists node logs as `leader.out` and `follower.out`, creates `follower/` under the run home, shares `DISAGG_MULTI_DB_HASH` through anonymous shared memory, and mutates global role/page-log/sync fields. Role switch and sync operations persist WiredTiger checkpoints and disaggregated metadata through reconfiguration and checkpoints.

## Dependencies And Integration Points
It depends on config normalization for `disagg.page_log`, `disagg.multi`, `disagg.mode`, `disagg.multi_validation`, and `disagg.preserve`; on `checksum_database`; on follower checkpoint pickup; on timestamp and verification subsystems; and on POSIX process/socket APIs.

## Risks And Test Signals
Risks include forked process divergence, socket deadlocks, shared-memory cleanup leaks, follower timeout during teardown, role-switch checkpoint gaps, and hash mismatches. Signals include leader/follower logs, synchronization track messages, preserved disagg state on mismatch, child process timeout, and mirror/hash assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format_disagg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format_disagg_multi.sh -->
# sources/storage-engines/wiredtiger/test/format/format_disagg_multi.sh

## Purpose
`format_disagg_multi.sh` is an interactive tmux harness for running format in multi-node disaggregated mode and watching leader/follower logs side by side.

## Important APIs, Types, And Functions
The script defines `msg`, `fatal_msg`, `onintr`, and `usage`. It parses `-h/--home`, `-c/--config`, `-v/--validation`, `-r/--rows`, and `-o/--ops`. It uses `tmux`, `tput`, `tail -F`, and the local `./t` binary.

## Control Flow
The script selects either a custom config or defaults to `../../../test/format/CONFIG.disagg` plus injected settings `disagg.multi=1`, `runs.predictable_replay=1`, validation flag, row range, and operation range. It kills any prior tmux session with the fixed session name, starts a run window executing `./t`, opens a logs window, tails `leader.out`, splits a second pane for `follower/follower.out`, configures pane titles/layout/mouse/status, then attaches.

## State And Persistence Behavior
The harness does not modify source files. It causes the format binary to create or reuse the selected run home and logs under `leader.out` and `follower/follower.out`. It owns tmux session state named `format_disagg_multi_node`.

## Dependencies And Integration Points
It assumes it is run from a build directory with `./t`, that `tmux` and terminal color capabilities exist, and that the C disaggregated setup will create the expected log files. It complements `format_disagg.c` by making manual multi-node runs observable.

## Risks And Test Signals
Risks include fixed tmux session-name collision, indefinite waits for log files if startup fails before log creation, color setup failures in noninteractive terminals, and quoting limitations in the constructed tmux command. Signals are live leader/follower log panes and the underlying format program exit shown in the run pane.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format_disagg_multi.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format_inline.h -->
# sources/storage-engines/wiredtiger/test/format/format_inline.h

## Purpose
`format_inline.h` contains small, high-use inline helpers and trace macros shared by format workers. It wraps WiredTiger cursor/transaction/lock behavior with format-specific retry, timeout, RNG, table-selection, and tracing policy.

## Important APIs, Types, And Functions
Important helpers include `read_op`, `rng`, `mmrand`, `random_sleep`, `tables_apply`, `table_maxv`, `table_sumv`, `table_select`, `table_select_type`, `wt_wrap_open_cursor`, `table_cursor`, `wt_wrap_begin_transaction`, `key_gen`, `key_gen_insert`, and `lock_*` wrappers. It defines `FORMAT_PREPARE_TIMEOUT`, `trace_msg`, `trace_uri_op`, and `trace_op`.

## Control Flow
`read_op` dispatches cursor reads and waits out `WT_PREPARE_CONFLICT` until a 120-second timeout. RNG helpers centralize random choice and bounded random sleeps. Table helpers abstract single-table versus multi-table layout. Cursor open retries on metadata `EBUSY`. Transaction begin injects `operation_timeout_ms` and retries `WT_CACHE_FULL`. Lock wrappers dispatch to WiredTiger or pthread read-write locks according to `RWLOCK.lock_type`. Trace macros emit verbose messages and optional transaction snapshot details when trace flags are set.

## State And Persistence Behavior
The helpers mostly mutate in-memory session/cursor/lock state. `wt_wrap_begin_transaction` affects transaction state but does not commit. `table_cursor` lazily stores cursors in `TINFO`. Key generation writes caller-provided `WT_ITEM` buffers. No files are written directly.

## Dependencies And Integration Points
The header depends on `format.h` types and globals, WiredTiger internal lock/random/session APIs, and testutil assertions. It is included at the end of `format.h`, making its helpers available to all format source files.

## Risks And Test Signals
Risks include infinite waits if prepare conflicts do not resolve before timeout, biased or shared RNG use in the wrong operation class, cursor reuse mismatches when table IDs change, and lock-type initialization errors. Signals include prepare-conflict timeout assertions, `open_cursor` failures after `EBUSY` retry, transaction begin failures, and verbose trace output when flags are enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format_inline.h -->
