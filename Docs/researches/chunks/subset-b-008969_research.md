# sources/storage-engines/wiredtiger/src/config/config_def.c lines 1-4049

## Chunk Scope

This chunk is the generated front portion of WiredTiger's main configuration definition file. The file starts with `DO NOT EDIT: automatically built by dist/api_config.py`, includes `wt_internal.h`, defines shared choice-string constants, and then emits `WT_CONFIG_CHECK` arrays plus per-array jump tables for public API methods, metadata records, and several `wiredtiger_open` variants.

The researched span is `sources/storage-engines/wiredtiger/src/config/config_def.c:1-4049`. It ends in the middle of `confchk_wiredtiger_open_usercfg`; the `config_entries` registry and helper functions such as `__wt_conn_config_init`, `__wt_conn_config_discard`, and `__wt_conn_config_match` are later in the same generated file and are outside this chunk.

## Purpose

The chunk provides the static schema that WiredTiger uses to validate configuration strings. Each `WT_CONFIG_CHECK` row describes one legal key: its name, textual type, optional validation callback, textual constraints, nested subconfiguration table, compiled type enum, generated key id, integer min/max bounds, and legal choice set. The matching jump table narrows key lookup by first character before binary search.

The generated data covers:

- Connection APIs: `WT_CONNECTION.close`, `debug_info`, `load_extension`, `open_session`, `query_timestamp`, `reconfigure`, `rollback_to_stable`, `set_key_provider`, and `set_timestamp`.
- Cursor APIs: `WT_CURSOR.bound` and `WT_CURSOR.reconfigure`.
- Session APIs: alter, begin/commit/rollback/prepare/timestamp transactions, checkpoint, compact, create, drop, log flush, open cursor, publish, query timestamp, salvage, and verify.
- Metadata schemas: `colgroup_meta`, `file_config`, `file_meta`, `index_meta`, `layered_meta`, `object_meta`, `table_meta`, `tier_meta`, and `tiered_meta`.
- Open-time connection schemas: reusable subconfig tables and the main `wiredtiger_open`, `wiredtiger_open_all`, `wiredtiger_open_basecfg`, and partial `wiredtiger_open_usercfg` definitions.

## Important APIs, Types, and Data Structures

`WT_CONFIG_CHECK` is the central type. In `src/include/config.h`, it contains `name`, `type`, `checkf`, `checks`, `subconfigs`, `subconfigs_entries`, `subconfigs_jump`, `compiled_type`, `key_id`, `min_value`, `max_value`, and `choices`. The tables in this chunk populate those fields directly.

`WT_CONFIG_COMPILED_TYPE_*` values encode runtime type expectations:

- `BOOLEAN` accepts boolean values or numeric 0/1.
- `CATEGORY` recursively validates a nested key/value struct using `subconfigs`.
- `FORMAT` is used for format strings such as `key_format` and `value_format`; these rows call `__wt_struct_confchk`.
- `INT` enforces numeric type and optional min/max bounds.
- `LIST` expects a structured/list value when non-empty and may restrict members through `choices`.
- `STRING` accepts any config value as string-like text, with optional choice checks.

Choice constants such as `__WT_CONFIG_CHOICE_snapshot`, `__WT_CONFIG_CHOICE_all`, `__WT_CONFIG_CHOICE_recovery`, `__WT_CONFIG_CHOICE_data`, and `__WT_CONFIG_CHOICE_log` are emitted once and reused through `confchk_*_choices` arrays. This gives validation and compiled configuration code stable pointer identities for common values, including boolean normalization in the compilation path.

Jump tables have type `uint8_t[WT_CONFIG_JUMP_TABLE_SIZE]`. They map ASCII first characters to the start/end offsets in a sorted `WT_CONFIG_CHECK` array. Runtime validation uses these offsets to restrict `bsearch` to the relevant contiguous slice instead of searching the full table.

## Configuration Families

### Connection and Session APIs

The first part defines compact method-level schemas. Examples include:

- `confchk_WT_CONNECTION_close` with `debug.skip_checkpoint`, `final_flush`, `leak_memory`, and `use_timestamp`.
- `confchk_WT_CONNECTION_open_session` and `confchk_WT_SESSION_reconfigure`, which share cursor-cache, cache wait, debug, isolation, and prefetch options.
- `confchk_WT_CONNECTION_reconfigure`, a large runtime-reconfiguration schema for cache, checkpointing, debug mode, disaggregated storage, eviction, logging, statistics, tiered storage, timing stress, and verbose controls.
- Transaction tables for begin, commit, rollback, prepare, timestamp, and prepared-id APIs. These validate timestamp strings, isolation choices, ignore-prepare modes, sync options, operation timeouts, priorities, and prepared transaction identifiers.
- `confchk_WT_SESSION_open_cursor`, which validates cursor behavior flags, checkpoint reads, debug dump-version controls, incremental backup cursor options, dump formats, raw mode, read-only mode, targets, and statistics choices.

### Creation and Metadata Schemas

`confchk_WT_SESSION_create` defines create-time schema for object layout and storage behavior: allocation sizes, access pattern hints, block allocation/manager/compressor, cache residency, checksums, column/key/value formats, encryption, disaggregated options, import, LSM, page sizes, prefix compression, tiered storage, and timestamp usage policy.

The metadata tables mirror or extend create-time schemas for persisted metadata records:

- `confchk_colgroup_meta` and `confchk_table_meta` validate high-level table/column-group metadata.
- `confchk_file_config` is a create-like file configuration schema.
- `confchk_file_meta`, `confchk_object_meta`, `confchk_tier_meta`, and `confchk_tiered_meta` include persisted checkpoint, object id, live-restore, flush timestamp/time, readonly/tiered object markers, version, tier lists, and tier cache/bucket fields.
- `confchk_index_meta` adds index-specific `extractor`, `immutable`, and format fields.
- `confchk_layered_meta` includes disaggregated and stable-layer metadata fields.

These tables are important because they validate metadata strings loaded from WiredTiger metadata, not only user-supplied API configuration.

### Open-Time Schemas

The `wiredtiger_open` portion builds many reusable subconfig tables before the main open schemas. Notable nested groups include:

- `block_cache`: enablement, cache-on-write/checkpoint behavior, NVRAM path, cache sizing, hash sizing, overhead, and type.
- `checkpoint` and `checkpoint_cleanup`: periodic checkpoint timing, log-size threshold, cleanup method, file wait, and wait interval.
- `debug_mode`: crash injection, corruption abort behavior, checkpoint/log retention, eviction and cursor stress toggles, page history, realloc behavior, rollback error, tiered flush behavior, and disaggregated address-cookie upgrade controls.
- `disaggregated`: role, checkpoint metadata, drain threads, local file action, page log, last materialized LSN, and destructive reset acknowledgment.
- `eviction`, `file_manager`, `heuristic_controls`, `history_store`, `io_capacity`, `load_control`, `operation_tracking`, `page_delta`, `rollback_to_stable`, `shared_cache`, `statistics_log`, `tiered_storage`, `transaction_sync`, and `prefetch`.
- `chunk_cache`, including capacity, chunk size, hash size, storage type choices (`FILE` or `DRAM`), and insertion/eviction controls.
- `compatibility`, `encryption`, `hash`, `live_restore`, and `log`.

`confchk_wiredtiger_open` includes administrative and environment flags such as `backup_restore_target`, `buffer_alignment`, `builtin_extension_config`, `compile_configuration_count`, `config_base`, `create`, `direct_io`, `extensions`, `file_extend`, `hazard_max`, `in_memory`, `mmap`, `multiprocess`, `precise_checkpoint`, `preserve_prepared`, `readonly`, `salvage`, session sizing, environment usage, `verify_metadata`, and `write_through`.

`confchk_wiredtiger_open_all`, `confchk_wiredtiger_open_basecfg`, and `confchk_wiredtiger_open_usercfg` are close variants that differ in which keys are legal for all/open-base/user configuration contexts. In this chunk, `wiredtiger_open_usercfg` is visible through `page_delta` at line 4049; its remaining keys continue after the chunk.

## Control Flow

This generated file does not execute control flow by itself. Its tables are consumed by validation and configuration compilation paths:

1. A caller obtains a `WT_CONFIG_ENTRY` for a method, usually through `WT_CONFIG_REF(session, name)` or by method-name lookup.
2. `__wt_config_check` receives the entry and config string. It skips work if there is no config/check array, or if the string is already recognized as compiled configuration.
3. `__config_check` parses each key/value pair, validates that the key token is an id/string, and searches the entry's `WT_CONFIG_CHECK` array.
4. `__config_check_search` uses the generated jump table and the first character of the key to bound a binary search over the sorted check array.
5. The selected row's `compiled_type` drives type validation. `CATEGORY` recurses into `subconfigs`; `LIST` and `STRING` may consult `choices`; `INT` checks numeric type and min/max bounds; `FORMAT` rows defer detailed structure validation through callbacks such as `__wt_struct_confchk`.
6. If a row has a validation callback or choice set, those checks run after basic type validation.

The configuration compilation path in `src/conf/conf_compile.c` also depends on the same rows. It uses compiled types to choose `WT_CONFIG_ITEM_TYPE`, normalizes boolean values to shared choice strings, binds placeholders for precompiled config strings, and invokes `__wt_conf_check_one` against row-level constraints.

## State and Persistence Behavior

The chunk contains static immutable data. It does not mutate connection, session, metadata, or file state directly.

Its persistence relevance comes from the schemas it defines:

- Metadata validation tables are applied to persisted metadata strings for files, objects, tables, tiers, tiered metadata, indexes, column groups, and layered/disaggregated records.
- Open-time options such as `config_base`, `compatibility`, `log`, `tiered_storage`, `disaggregated`, `live_restore`, and `encryption` determine how later connection setup reads or writes durable files and metadata.
- Generated `key_id` fields align with generated `WT_CONF_ID_*` identifiers in `conf_keys.h`; compiled configuration stores parsed values by these ids for fast access.

Because these tables are generated, the durable contract is the source data in `dist/api_data.py` plus generator behavior in `dist/api_config.py`. Manual edits to this file would be overwritten and risk desynchronizing `config_def.c`, `config.h` entry indices, and `conf_keys.h` ids.

## Dependencies and Integration Points

Direct compile-time dependencies in this chunk include:

- `wt_internal.h`, which brings in `WT_CONFIG_CHECK`, `WT_CONFIG_ENTRY`, `WT_CONFIG_COMPILED_TYPE_*`, size macros such as `WT_KILOBYTE` and `WT_TERABYTE`, and validation callbacks.
- `__wt_struct_confchk`, referenced by format keys.
- Generated config ids and entry indices from `src/include/conf_keys.h` and `src/include/config.h`.
- `WT_CONFIG_JUMP_TABLE_SIZE`, `INT64_MIN`, and `INT64_MAX` for jump table sizing and unconstrained bounds.

Runtime integration points include:

- `src/config/config_check.c` for API and metadata validation.
- `src/conf/conf_compile.c` for precompiled configuration parsing and binding.
- `src/config/config_api.c` for extension-provided configuration checks.
- Connection open/reconfigure code in `src/conn/conn_api.c`, which consumes keys validated by the `wiredtiger_open*` and connection reconfigure tables.
- Public API wrappers that call `__wt_config_check` through generated `WT_CONFIG_ENTRY_*` identifiers.

## Risks and Maintenance Notes

- The arrays must remain sorted by key name for jump-table-bounded binary search. Generator bugs or manual edits that break sorting can make valid keys fail validation.
- `subconfigs_entries` must match the number of non-sentinel rows in the referenced subconfig table. A mismatch can narrow searches incorrectly or expose rows from the wrong range.
- Choice arrays must stay synchronized with textual `choices=[...]` strings. The text is mostly documentary for diagnostics/generation, while runtime enforcement uses the `choices` pointer array.
- Min/max bounds use expanded unit macros such as `10LL * WT_TERABYTE`; overflow or inconsistent units would silently change accepted ranges.
- Reused `key_id` values allow common concepts such as `enabled`, `name`, `log`, `verbose`, and timestamp fields to compile consistently across APIs. Incorrect ids would affect compiled configuration lookup even when textual validation passes.
- The assigned chunk cuts off inside `confchk_wiredtiger_open_usercfg`, so research for final registry entries and config initialization/discard helpers must come from later chunks.

## Test Signals

Useful validation signals for this chunk are broad configuration tests rather than unit tests of individual rows:

- API tests that pass invalid keys, wrong types, out-of-range integers, and invalid choice values through public methods should fail with `EINVAL`.
- Metadata tests that load or create table/file/index/object/tiered metadata exercise the metadata tables.
- Connection tests using `wiredtiger_open` with `config_base`, `compatibility`, logging, backup/readonly, live-restore, disaggregated, tiered storage, encryption, cache sizing, and statistics options exercise the open schemas.
- Python suite references to `config_base=false`, compatibility releases, readonly opens, base configuration files, timestamp/log settings, and backup scenarios are especially relevant because those keys are validated here before deeper connection behavior runs.
- Generated-file consistency checks should rerun `dist/api_config.py` and verify no drift in `src/config/config_def.c`, `src/include/config.h`, and `src/include/conf_keys.h`.
