# Research Group: subset-b-008971

This grouped report covers six WiredTiger source files and preserves each source path in its section title. The reconciliation lane can split each section using the `BEGIN_FILE_RESEARCH` and `END_FILE_RESEARCH` markers.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/config/config_ext.c -->
# sources/storage-engines/wiredtiger/src/config/config_ext.c

## Purpose

`config_ext.c` exposes WiredTiger configuration helpers through the extension API. It adapts external `WT_EXTENSION_API` calls to the internal configuration parser by resolving the caller's `WT_SESSION` to a `WT_SESSION_IMPL`, falling back to the connection default session when extensions call without an explicit session.

## Important APIs, Types, and Functions

- `__wt_ext_config_get`: external wrapper for looking up a key in a NULL-terminated configuration stack represented as `WT_CONFIG_ARG`.
- `__wt_ext_config_get_string`: external wrapper for looking up a key in one configuration string.
- `__wt_ext_config_parser_open`: exposes `wiredtiger_config_parser_open` to extensions for a raw configuration string and length.
- `__wt_ext_config_parser_open_arg`: opens a parser over the last non-NULL entry in a configuration stack.
- Key types are `WT_EXTENSION_API`, `WT_SESSION`, `WT_CONFIG_ARG`, `WT_CONFIG_ITEM`, and `WT_CONFIG_PARSER`.

## Control Flow

The lookup wrappers cast `wt_api->conn` to `WT_CONNECTION_IMPL`, cast the optional `WT_SESSION` to `WT_SESSION_IMPL`, and default to `conn->default_session` when the argument is NULL. `__wt_ext_config_get` returns `WT_NOTFOUND` for a NULL config stack, otherwise calls `__wt_config_gets`. `__wt_ext_config_get_string` directly calls `__wt_config_getones`. Parser-open wrappers either pass the raw string through or scan the config stack to the final entry and parse only that entry.

## State and Persistence Behavior

This file does not persist state. It reads configuration strings supplied by callers and returns parsed values or parser handles. The only connection state it depends on is `default_session`, used to route error handling and memory context when no session was provided.

## Dependencies and Integration Points

The file depends on `wt_internal.h`, internal config APIs such as `__wt_config_gets` and `__wt_config_getones`, and the public parser function `wiredtiger_config_parser_open`. It is wired into the extension API from `conn_api.c` through `__conn_get_extension_api`, which assigns these functions to `WT_EXTENSION_API.config_get`, `config_get_string`, `config_parser_open`, and `config_parser_open_arg`.

## Risks and Edge Cases

- `WT_CONFIG_ARG` is treated as `const char **`; callers must pass a valid NULL-terminated config stack.
- `config_parser_open_arg` intentionally parses only the final stack entry, not the merged view. Extensions needing effective value lookup should use `config_get`.
- Falling back to `default_session` is convenient but means extension calls without a session share the default session's error and scratch context.
- A NULL or empty config stack opens a parser with `p = NULL` and `len = 0`, relying on `wiredtiger_config_parser_open` to handle the empty stream.

## Test Signals

Coverage is indirect through extension tests that call `WT_EXTENSION_API` config helpers, parser tests for `wiredtiger_config_parser_open`, and integration paths that load collators, compressors, encryptors, storage sources, or file systems with extension configuration. Useful test signals include `WT_NOTFOUND` on NULL stacks, correct override behavior for stack lookups, and parser behavior for the last config string in a stack.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/config/config_ext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/config/test_config.c -->
# sources/storage-engines/wiredtiger/src/config/test_config.c

## Purpose

`test_config.c` is a generated configuration schema table for WiredTiger test workloads. It maps named test programs and scenarios to default configuration strings, compile-time validation descriptors, jump tables, sizing metadata, and the exported lookup function `__wt_test_config_match`.

## Important APIs, Types, and Functions

- `WT_CONFIG_CHECK`: describes allowed keys, value types, nested categories, constraints, compiled IDs, and numeric min/max bounds.
- `WT_CONFIG_ENTRY`: binds a method or test name to its default configuration string and validation table.
- `confchk_*_subconfigs`: nested schemas for metrics monitor, operation tracker, statistics, timestamp manager, workload manager, background compact, checkpoint, CRUD workload, and operation sizing fields.
- `confchk_*_jump`: generated jump tables sized by `WT_CONFIG_JUMP_TABLE_SIZE` to accelerate config key dispatch.
- `config_entries[]`: top-level mapping from test names such as `api_instruction_count_benchmarks`, `background_compact`, `bounded_cursor_perf`, `burst_inserts`, `cache_resize`, `hs_cleanup`, `operations_test`, `reverse_split`, and `search_near_*` to defaults and schemas.
- `__wt_test_config_match`: linear search by test name returning a `const WT_CONFIG_ENTRY *` or NULL.

## Control Flow

There is no runtime mutation beyond lookup. Configuration validation begins in consumers by calling `__wt_test_config_match(test_name)`. The function walks `config_entries` until `ep->method` is NULL, compares `test_name` with `strcmp`, and returns the matching static entry. The returned entry points to a default config string and a nested tree of `WT_CONFIG_CHECK` arrays. The core config validation code then uses the table and jump array to validate keys, types, categories, and bounds.

The generated schema is deeply shared. For example, common subconfigs such as `metrics_monitor`, `timestamp_manager`, and `workload_manager` are referenced by many test entries. Specialized entries add fields like `burst_duration` or `search_near_threads`, while most entries share the same broad operational template.

## State and Persistence Behavior

All state in this file is static const process memory. It does not read or write files, allocate memory, or persist anything. Its default configuration strings influence test database behavior when the corresponding test harness uses them, but this file itself is a schema and default catalog only.

## Dependencies and Integration Points

The file includes `wt_internal.h` and depends on generated config infrastructure from `dist/api_config.py`. It integrates with WiredTiger test and config machinery through `WT_CONFIG_ENTRY`, `WT_CONFIG_CHECK`, compiled config type enums, and the public internal lookup symbol `__wt_test_config_match`. It is not ordinary hand-written business logic; changes should normally be made in the generator inputs rather than in this generated C file.

## Risks and Edge Cases

- Because it is generated, manual edits are likely to be overwritten and can desynchronize schema metadata from generator sources.
- The linear lookup is simple and acceptable for a small static catalog, but duplicate names would silently select the first entry.
- Generated min/max bounds are enforcement points; incorrect bounds can make test workloads reject valid configs or accept unsafe values.
- Shared subconfig tables mean a change to one nested schema can affect many test entries.
- Default strings include nested categories and escaped line-split C strings; generator bugs here can produce valid C that is semantically invalid config.

## Test Signals

The file is itself test configuration data. Strong signals include successful config validation for every entry in `config_entries`, negative validation for out-of-range values such as invalid thread counts or key sizes, and harness tests that confirm `__wt_test_config_match` returns NULL for unknown tests. Build or generator tests should verify that `dist/api_config.py` can reproduce this file and that jump tables match their corresponding sorted key arrays.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/config/test_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/api_calc_modify.c -->
# sources/storage-engines/wiredtiger/src/conn/api_calc_modify.c

## Purpose

`api_calc_modify.c` implements WiredTiger's helper for representing a full value update as a compact list of `WT_MODIFY` operations. It compares an old byte string and a new byte string, finds large common regions, and emits replacement spans for the differing regions when the result fits caller-provided limits.

## Important APIs, Types, and Functions

- `wiredtiger_calc_modify`: public API wrapper accepting `WT_SESSION *`.
- `__wt_calc_modify`: internal implementation accepting `WT_SESSION_IMPL *`.
- `WT_MODIFY`: output entry containing target offset, old span size, and replacement bytes.
- `WT_CM_STATE`: local comparison state including old/new ranges, consumed pointers, max diff budget, and max entry count.
- `WT_CM_MATCH`: local match result with old pointer, new pointer, and match length.
- `__cm_fingerprint`: reads an 8-byte block as a hash-like fingerprint.
- `__cm_extend`: expands a candidate match forward and backward to its maximal equal byte span.
- `__cm_add_modify`: appends one `WT_MODIFY` and advances budget accounting.

## Control Flow

`__wt_calc_modify` rejects inputs shorter than `WT_CM_MINMATCH` because short values are not worth delta encoding. It initializes comparison state and treats `*nentriesp` as input capacity, then resets it to the output count. It first trims matching prefixes and suffixes using `__cm_extend`. If the remaining middle is too small for block matching, it emits one trailing replacement.

For the middle diff, it scans the new value one byte at a time while maintaining two fingerprint markers in the old value separated by a growing gap. When the new-side fingerprint matches either old-side marker, `__cm_extend` verifies and expands the match. A match shorter than `WT_CM_MINMATCH` is ignored. A useful match causes `__cm_add_modify` to emit the replacement bytes between the last consumed positions and the match, then the scan restarts after the matched region. At the end, any remaining old or new bytes are emitted as a final modify.

## State and Persistence Behavior

The algorithm is stateless outside the caller-provided output array. `WT_MODIFY.data.data` points into `newv->data`, so the new value memory must remain valid while the modify list is consumed. No database state is read or persisted. `maxdiff` is consumed as replacement bytes are emitted, and `*nentriesp` is rewritten to the number of generated entries.

## Dependencies and Integration Points

The file depends on internal utility macros and functions from `wt_internal.h`, including `WT_RET`, `WT_ASSERT`, `WT_MIN`, and error code conventions. It integrates with update paths that can store or transmit modify records rather than full values, and the public `wiredtiger_calc_modify` entry allows callers to request the same calculation from a `WT_SESSION`.

## Risks and Edge Cases

- `__cm_fingerprint` copies 8 bytes with `memcpy`; callers rely on prior bounds checks ensuring at least `WT_CM_BLOCKSIZE` bytes are readable.
- The function returns `WT_NOTFOUND` when the diff cannot fit `maxentries` or `maxdiff`, or when growing gap search exceeds the diff budget.
- `WT_MODIFY` entries borrow memory from `newv`; misuse after freeing or changing `newv` is unsafe.
- Matching is heuristic rather than a full optimal diff. It favors speed and compact-enough deltas over minimal edit scripts.
- The gap doubling logic can bail out on large shifts even when a possible diff exists, which is acceptable because callers can fall back to a full update.

## Test Signals

Unit tests should cover unchanged values, prefix/suffix-only changes, insertions, deletions, replacements, too-small inputs, max entry exhaustion, max diff exhaustion, and reconstruction of `newv` from `oldv` plus generated modifies. Fuzz or randomized differential tests are valuable: generate old/new byte arrays, call `__wt_calc_modify`, apply returned modifies, and assert exact reconstruction or an allowed `WT_NOTFOUND` fallback.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/api_calc_modify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/api_strerror.c -->
# sources/storage-engines/wiredtiger/src/conn/api_strerror.c

## Purpose

`api_strerror.c` maps WiredTiger and system error codes to human-readable strings. It preserves a mostly thread-safe path for constant strings while still supporting fallback formatting through `__wt_strerror` for cases that may need session-aware or platform-specific handling.

## Important APIs, Types, and Functions

- `__wt_wiredtiger_error`: returns constant strings for known WiredTiger main and sub-level errors, special-cases `ENOTSUP` and zero, delegates positive POSIX errors to `strerror`, and returns NULL for unknown negative values.
- `wiredtiger_strerror`: public non-thread-safe wrapper using a static buffer and `__wt_strerror`.
- `__wt_is_valid_sub_level_error`: validates WiredTiger sub-level error code range.
- Important codes include `WT_ROLLBACK`, `WT_DUPLICATE_KEY`, `WT_ERROR`, `WT_NOTFOUND`, `WT_PANIC`, `WT_RUN_RECOVERY`, `WT_CACHE_FULL`, `WT_PREPARE_CONFLICT`, `WT_TRY_SALVAGE`, and sub-level conflict or diagnostic codes such as `WT_WRITE_CONFLICT` and `WT_CONFLICT_BACKUP`.

## Control Flow

`__wt_wiredtiger_error` first checks WiredTiger primary error constants in a switch, then checks sub-level error constants in a second switch. If neither matches, it handles `ENOTSUP`, zero, and positive POSIX errors. Unknown negative errors return NULL so higher-level formatting can decide how to report them. `wiredtiger_strerror` always delegates to `__wt_strerror` with a static local buffer.

## State and Persistence Behavior

There is no persistent state. `wiredtiger_strerror` uses a process-wide static character buffer, making that wrapper non-thread-safe. `__wt_wiredtiger_error` returns constant strings or the system `strerror` pointer for positive errors.

## Dependencies and Integration Points

The file is generated by `dist/api_err.py` and includes `wt_internal.h`. It is used by public error reporting, session error reporting, extension error helpers, and any caller that needs stable text for WiredTiger-specific codes. It also encodes the valid sub-level error range used by error handling logic.

## Risks and Edge Cases

- Generated content must stay synchronized with the authoritative error definitions; missing codes degrade diagnostics.
- `wiredtiger_strerror` uses a static buffer and is explicitly non-thread-safe.
- `strerror` behavior varies across platforms, which is why the file special-cases `ENOTSUP` and zero.
- Unknown negative codes return NULL from `__wt_wiredtiger_error`; callers must handle that path.
- Sub-level error validation is range-based, so newly assigned codes must stay within `(-32200, -32000]`.

## Test Signals

Tests should assert exact strings for major WiredTiger codes, coverage for every generated sub-level code, positive POSIX fallback behavior, zero handling, `ENOTSUP` behavior on Windows and POSIX builds, and NULL for unknown negative values. A generator test should confirm this file is reproducible from `dist/api_err.py`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/api_strerror.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/api_version.c -->
# sources/storage-engines/wiredtiger/src/conn/api_version.c

## Purpose

`api_version.c` implements the public `wiredtiger_version` API. It returns the compiled WiredTiger version string and optionally writes major, minor, and patch components to caller-provided pointers.

## Important APIs, Types, and Functions

- `wiredtiger_version`: public function returning `WIREDTIGER_VERSION_STRING`.
- Version macros: `WIREDTIGER_VERSION_MAJOR`, `WIREDTIGER_VERSION_MINOR`, `WIREDTIGER_VERSION_PATCH`, and `WIREDTIGER_VERSION_STRING`.

## Control Flow

The function checks each output pointer for NULL before assignment, writes the corresponding macro value when present, and returns the version string unconditionally.

## State and Persistence Behavior

No runtime or persistent state is used. The result is entirely compile-time version metadata.

## Dependencies and Integration Points

The file includes `wt_internal.h` for version macros. `wiredtiger_version` is exposed as part of the public C API and is also assigned to `WT_EXTENSION_API.version` in `conn_api.c`, allowing extensions to query the running library version.

## Risks and Edge Cases

- Callers may pass any subset of NULL output pointers; this is supported.
- Version correctness depends on build-time macro generation.
- Extensions may use this for compatibility checks, so stale or mismatched version macros can cause confusing plugin behavior.

## Test Signals

Tests should call `wiredtiger_version` with all output pointers, with each pointer NULL, and with all pointers NULL. Assertions should compare returned components and string against build metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/api_version.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_api.c -->
# sources/storage-engines/wiredtiger/src/conn/conn_api.c

## Purpose

`conn_api.c` is the central implementation of the WiredTiger connection API. It binds the public `WT_CONNECTION` vtable, opens and closes database connections, configures connection-wide behavior, loads extensions, registers extension-provided components, manages early filesystem and encryption setup, coordinates startup and shutdown lifecycles, and exposes diagnostics, timestamps, sessions, and storage integrations.

## Important APIs, Types, and Functions

- Public entry point: `wiredtiger_open`.
- Public `WT_CONNECTION` method implementations: close, debug_info, reconfigure, get_home, compile_configuration, configure_method, is_new, open_session, query_timestamp, set_timestamp, rollback_to_stable, load_extension, add_data_source, add_collator, add_compressor, add_encryptor, set_file_system, add_page_log, add_storage_source, get_page_log, get_storage_source, set_context_uint, dump_error_log, set_key_provider, get_key_provider, and get_extension_api.
- Extension registries: `WT_NAMED_COLLATOR`, `WT_NAMED_COMPRESSOR`, `WT_NAMED_DATA_SOURCE`, `WT_NAMED_ENCRYPTOR`, `WT_KEYED_ENCRYPTOR`, `WT_NAMED_PAGE_LOG`, and `WT_NAMED_STORAGE_SOURCE`.
- Lifecycle helpers: `__wti_conn_ext_init`, `__wti_conn_ext_destroy`, `__wti_conn_backup_init`, `__wti_conn_backup_destroy`, `__conn_single`, `__conn_config_file_system`, `__conn_version_verify`, `__conn_startup_cleanup_and_verify`, and `__conn_write_base_config`.
- Config helpers: `__conn_config_file`, `__conn_config_env`, `__conn_hash_config`, `__conn_config_readonly`, `__conn_config_check_version`, `__wti_debug_mode_config`, `__wti_extra_diagnostics_config`, `__wt_verbose_config`, `__wti_timing_stress_config`, `__wti_json_config`, `__wti_heuristic_controls_config`, and `__wti_disagg_debug_mode_config`.

## Control Flow

`wiredtiger_open` initializes the library, allocates a `WT_CONNECTION_IMPL`, installs a static `WT_CONNECTION` method table, links the connection into the process list, and uses a dummy session until real sessions exist. It validates the application config, builds an initial config stack, determines early flags such as in-memory and read-only, sets the home directory, allocates hash tables, loads early extensions, configures the filesystem, verifies a clean startup directory, and claims exclusive ownership of the database home through process and file locking in `__conn_single`.

After that early phase, it builds the full config stack from defaults, compiled compatibility version, base config file, application config, user config file, environment config, and read-only overrides. It merges and stores the effective config, applies logging and diagnostics settings, sizes sessions, configures file extension and mmap behavior, handles prefetch and precise checkpoint compatibility, initializes compiled configuration and statistics, opens the real connection with `__wti_connection_open`, then loads non-early builtins and dynamic extensions. Encryption, logging compatibility, base config persistence, turtle and metadata initialization, optional metadata verification or salvage, prior metadata state, backup metadata, event notification, worker startup, recovery, startup cleanup, and final readiness flags follow in order.

`__conn_close` performs the reverse lifecycle carefully. It marks the connection no longer ready, rolls back active transactions, closes external sessions, temporarily sets minimal mode for final event handling and statistics, drains transaction activity, stops sweep, prefetch, live restore, background compact, checkpoint cleanup, checkpoint, and layered table manager services, runs transaction global shutdown and final checkpoint behavior, closes tiered storage with optional final flush, handles leak-memory configuration, records shutdown timing, and calls `__wti_connection_close`.

Registration methods allocate named wrapper objects and append them to connection queues under `api_lock` where needed. Removal methods walk queues, call terminate callbacks, release keyed or bucketed subobjects, and free wrapper memory. Configuration methods mostly parse named config entries and set connection flags or counters.

## State and Persistence Behavior

The file mutates nearly all connection-level state: home path, effective config string, extension queues, file system, key provider, encryption key cache, hash buckets, debug flags, verbose levels, timing stress flags, JSON output flags, cache cursor and checkpoint flags, prefetch settings, precise checkpoint and preserve prepared flags, read-only/in-memory/salvage flags, session array size, write-through settings, base configuration, compatibility versions, metadata state, backup state, readiness flags, and shutdown timing.

Persistent behavior includes reading `WiredTiger.basecfg`, `WiredTiger.config`, and `WIREDTIGER_CONFIG`; writing `WiredTiger.basecfg` through a temporary `WiredTiger.basecfg.set` file on database creation; creating and locking `WiredTiger.lock`; creating or validating the `WiredTiger` version file; initializing turtle and metadata files; optionally copying and salvaging metadata; dropping deprecated chunk cache metadata; and writing final checkpoint or tiered flush state during close.

## Dependencies and Integration Points

`conn_api.c` depends on broad WiredTiger internals: configuration parsing, OS filesystem adapters, dynamic loading, metadata, turtle files, schema operations, logging, recovery, timestamps, transaction management, checkpointing, eviction, sweep, prefetch, live restore, tiered/disaggregated storage, block cache, statistics, event handlers, call logging, and extension APIs. It integrates directly with generated config tables through `WT_CONFIG_BASE` and `WT_CONFIG_REF`, extension modules through `WT_CONNECTION` and `WT_EXTENSION_API`, and platform-specific filesystem implementations through `__wt_os_posix`, `__wt_os_win`, `__wt_os_inmemory`, and live restore filesystem setup.

## Risks and Edge Cases

- Startup order is fragile: early extensions must load before filesystem configuration, while encryption must wait until extensions have registered encryptors.
- Config stack precedence is central to correctness. Read-only overrides intentionally rewrite some settings, while other conflicts are rejected later.
- `__conn_single` mixes in-process checks, lock-file creation, byte locks, read-only exceptions, disaggregated mode, salvage behavior, and corruption detection; regressions can cause unsafe multi-process access or false startup failures.
- Extension registry operations rely on callback contracts. Missing encryptor callbacks, missing filesystem methods, or terminate/customize mismatches are validated in some paths but can still create cleanup complexity.
- Close ordering protects against races between sweep, sessions, checkpoints, transaction state, live restore, layered tables, and tiered storage; reordering can introduce use-after-free, leaked handles, or missed final checkpoints.
- Generated or persisted base configuration strips sensitive or run-specific fields. Incorrect filtering could persist secrets, persist nonportable runtime settings, or omit compatibility-critical settings.
- Error paths in `wiredtiger_open` must close partially initialized connections while preserving corruption signals such as `WT_TRY_SALVAGE`.

## Test Signals

High-value tests include open/close under normal, read-only, in-memory, salvage, exclusive, live restore, disaggregated, encrypted, and custom filesystem configurations; config precedence tests spanning application strings, base config files, user config files, and environment variables; extension registration and termination tests for collators, compressors, encryptors, data sources, page logs, storage sources, file systems, and key providers; lock-file and multi-process exclusion tests; metadata verify and salvage tests; final close ordering tests with active sessions and transactions; and failure-injection tests across partial startup to confirm cleanup, panic, and salvage-return behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_api.c -->
