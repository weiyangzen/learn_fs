# sources/storage-engines/wiredtiger/src/config/config_def.c - chunk subset-b-008970 research

Chunk scope: lines 4050-4830 of `sources/storage-engines/wiredtiger/src/config/config_def.c`. This is chunk 2 of 2 for `config_def.c`, an auto-generated WiredTiger configuration definition file built by `dist/api_config.py`.

## Purpose

This chunk completes the generated configuration metadata used by WiredTiger's configuration parser, validator, and optional compiled-configuration fast path. It covers the tail of `confchk_wiredtiger_open_usercfg`, the jump table for that check array, the full `config_entries[]` catalog for public/internal configuration methods, and the small runtime helpers that attach the static catalog to a connection.

The main role of the chunk is declarative rather than algorithmic: it maps method names such as `WT_SESSION.create`, metadata schemas such as `file.meta`, and connection-open variants such as `wiredtiger_open_usercfg` to default configuration strings, validation arrays, jump tables, stable method IDs, and precompiled configuration sizing metadata. Runtime code elsewhere uses this table to avoid hand-maintained per-method parsing rules.

## Important APIs, Types, and Functions

- `confchk_wiredtiger_open_usercfg` tail: lines 4050-4128 complete validation for user-visible `wiredtiger_open_usercfg` options. The visible keys include `precise_checkpoint`, `prefetch`, `preserve_prepared`, `readonly`, `rollback_to_stable`, `salvage`, `session_max`, `session_scratch_max`, `session_table_cache`, `shared_cache`, `statistics`, `statistics_log`, `tiered_storage`, `timing_stress_for_test`, `transaction_sync`, `verbose`, `verify_metadata`, and `write_through`. Category keys point to subconfig arrays defined earlier in the file, list keys point to generated choice arrays, and integer keys carry min/max bounds.
- `confchk_wiredtiger_open_usercfg_jump`: lines 4130-4135 define a 128-entry ASCII jump table. `WT_CONFIG_JUMP_TABLE_SIZE` is 128, and the lookup path uses the first key character to skip into sorted check arrays before binary search.
- `config_entries[]`: lines 4137-4784 define the static `WT_CONFIG_ENTRY` catalog. Each entry contains method/schema name, base/default configuration string, `WT_CONFIG_CHECK` array pointer, number of checks, check jump table, stable method ID, optional compiled-config sizing, and a boolean `compilable` flag.
- `__wt_conn_config_init(WT_SESSION_IMPL *session)`: lines 4786-4805 allocates `conn->config_entries` as an array of pointers, then copies pointers to every static `config_entries[]` element through the NULL terminator.
- `__wt_conn_config_discard(WT_SESSION_IMPL *session)`: lines 4807-4815 frees the per-connection pointer array allocated by init. It does not free the static entries themselves.
- `__wt_conn_config_match(const char *method)`: lines 4817-4830 linearly searches the static catalog and returns the matching entry by method string, or `NULL` if absent. This is a general lookup helper for callers that do not already have the generated numeric `WT_CONFIG_ENTRY_*` index.

The data types are declared in `src/include/config.h`: `WT_CONFIG_CHECK` describes a single key's type, range, choices, subconfigs, and compiled key ID; `WT_CONFIG_ENTRY` describes one method/configuration namespace. `WT_CONFIG_REF(session, n)` indexes `S2C(session)->config_entries` by generated `WT_CONFIG_ENTRY_*` constants. `WT_CONF_SIZING_INITIALIZE` and `WT_CONF_SIZING_NONE` come from `src/include/conf.h`; the former records stack/array sizes for APIs that support the compiled configuration path.

## Catalog Coverage

The `config_entries[]` table in this chunk covers several families:

- Connection API methods: extension registration, `WT_CONNECTION.close`, `debug_info`, `load_extension`, `open_session`, `query_timestamp`, `reconfigure`, `rollback_to_stable`, `set_key_provider`, and `set_timestamp`.
- Cursor/session API methods: cursor bound/reconfigure plus session alter, transaction, checkpoint, compact, create, drop, cursor-open, timestamp, salvage, truncate, verify, and related no-config methods.
- Metadata schema entries: `colgroup.meta`, `file.config`, `file.meta`, `index.meta`, `layered.meta`, `object.meta`, `table.meta`, `tier.meta`, and `tiered.meta`. These defaults mirror durable metadata fields such as checkpoint strings, live-restore state, tiered object state, object version, table/index formats, logging, encryption, disaggregated storage, and timestamp assertions.
- Connection-open variants: `wiredtiger_open`, `wiredtiger_open_all`, `wiredtiger_open_basecfg`, and `wiredtiger_open_usercfg`. These share many defaults but intentionally differ in fields such as `config_base`, `create`, `exclusive`, `in_memory`, `use_environment`, `use_environment_priv`, and `version` availability.

The stable method IDs in this table match the generated `WT_CONFIG_ENTRY_*` macros in `src/include/config.h`. This matters because callers on hot paths use numeric entries such as `WT_CONFIG_ENTRY_WT_SESSION_begin_transaction` rather than string search, and the compiled-configuration arrays in `src/conf/conf_compile.c` are parallel to this table.

## Control Flow

Generation flow is external to this C file: `dist/api_config.py` walks the API metadata, emits `WT_CONFIG_CHECK` arrays and jump tables, then writes `config_entries[]` sorted by method name with generated slot IDs. The same generator writes corresponding `WT_CONFIG_ENTRY_*` defines, so generated order must remain consistent across `config_def.c` and `config.h`.

Startup flow through this chunk is small but important. During connection initialization, `__wt_conn_config_init` allocates a per-connection pointer array sized to `WT_ELEMENTS(config_entries)`, assigns it to `conn->config_entries`, and fills it with pointers to the static entries including the NULL terminator. Later API paths use `WT_CONFIG_REF(session, name)` to resolve the entry for parsing, validation, and compiled default lookup.

Config validation flow is table-driven. Given a `WT_CONFIG_ENTRY`, the parser checks user strings against `entry->checks`, `entry->checks_entries`, and `entry->checks_jump`. Scalar entries validate type, min/max, and optional choices. Category entries recurse into their `subconfigs` arrays and subconfig jump tables. List entries validate tokens against choice arrays such as `confchk_verbose16_choices` and `confchk_timing_stress_for_test5_choices`.

Compiled configuration flow uses the same entry table. `src/conf/conf_compile.c` allocates `conn->conf_api_array` parallel to `conn->config_entries`, asserts `centry->method_id == i`, and precompiles default strings for entries marked `compilable`. In this chunk, `WT_CURSOR.bound`, `WT_SESSION.begin_transaction`, and `WT_SESSION.reconfigure` are explicitly marked compilable with sizing derived from their generated `WT_CONF_API_TYPE` layouts.

## State and Persistence Behavior

This chunk does not directly persist data, open files, or mutate on-disk metadata. Its persistent impact is indirect: the default strings and validation rules here define which configuration fields can be stored in WiredTiger metadata and which user-supplied connection/session strings are accepted at runtime.

The durable metadata-related entries are especially state-sensitive. `file.meta`, `object.meta`, `tier.meta`, and `tiered.meta` include checkpoint metadata, live-restore bitmap state, object/tier timestamps, tiered storage settings, version fields, readonly/tiered-object flags, and logging/encryption settings. Changes to these generated defaults or validation arrays can affect metadata compatibility and recovery behavior even though this chunk itself is static data.

In-memory state is limited to `WT_CONNECTION_IMPL.config_entries`: a connection-owned array of pointers into static read-only metadata. Allocation failure in `__wt_conn_config_init` returns through `WT_RET`. Cleanup is a single `__wt_free` call in `__wt_conn_config_discard`.

## Dependencies and Integration Points

- `wt_internal.h` pulls in the internal declarations for `WT_SESSION_IMPL`, `WT_CONNECTION_IMPL`, `WT_CONFIG_ENTRY`, `WT_CONFIG_CHECK`, memory helpers, and macros such as `S2C`, `WT_RET`, `WT_ELEMENTS`, and `__wt_free`.
- `src/include/config.h` defines `WT_CONFIG_CHECK`, `WT_CONFIG_ENTRY`, `WT_CONFIG_JUMP_TABLE_SIZE`, compiled type constants, `WT_CONFIG_REF`, and generated `WT_CONFIG_ENTRY_*` indexes.
- `src/include/conf.h` defines compiled-configuration sizing macros used by selected entries.
- `src/conf/conf_compile.c` consumes `conn->config_entries`, `method_id`, `compilable`, and sizing fields to build parallel compiled-default arrays.
- Parser/checking code in the `src/conf` area consumes check arrays, jump tables, choice arrays, min/max bounds, and category subconfigs for runtime validation.
- Public and internal API implementations use the generated method indexes to fetch base strings and check metadata for each API call.
- `dist/api_config.py` is the authoritative generator. Manual edits to this C file would be overwritten and are explicitly discouraged by the file header.

## Risks and Edge Cases

- Generated table/order drift is high impact. If `config_entries[]` order, `method_id`, generated `WT_CONFIG_ENTRY_*` macros, or compiled config arrays become inconsistent, direct indexed lookup can return the wrong configuration schema. `conf_compile.c` asserts `centry->method_id == i`, but non-compiled paths also rely on the same ordering contract.
- Default strings and check arrays must stay semantically aligned. A default key present in an entry's base string but missing from its check array, or vice versa, can cause startup validation failures or allow unsupported fields.
- Open-configuration variants are deliberately similar but not identical. Accidentally adding a field to `wiredtiger_open`, `wiredtiger_open_all`, `wiredtiger_open_basecfg`, or `wiredtiger_open_usercfg` without preserving their intended differences can expose internal-only settings to users or hide needed base settings.
- The jump tables assume 7-bit ASCII key names and sorted check arrays. Any generator bug that violates ordering or key-character assumptions degrades lookup correctness.
- `__wt_conn_config_match` is linear over the static catalog. That is acceptable for infrequent string-name lookup, but hot API paths should use generated numeric indexes through `WT_CONFIG_REF`.
- `__wt_conn_config_init` allocates an array including the NULL terminator. Consumers that iterate until `method == NULL` depend on that terminator being copied.
- Several entries govern test/failpoint-style options such as `timing_stress_for_test`, crash points, and debug modes. Incorrect validation choices can silently remove test coverage hooks or expose unintended diagnostic behavior.
- Metadata entries include compatibility-sensitive fields such as format versions, tiered metadata, checkpoint LSNs, live-restore fields, and disaggregated state. Generator changes require compatibility review, not just compile success.

## Test Signals

There are no direct unit tests inside this generated C file. Relevant test and validation signals are indirect:

- Regeneration checks should run the WiredTiger dist/generation workflow and verify that `config_def.c` and `src/include/config.h` remain synchronized with `dist/api_config.py` output.
- Build/compile coverage catches missing symbols for choice arrays, subconfig arrays, jump tables, and `WT_CONF_SIZING_INITIALIZE` types.
- Configuration parser tests exercise accepted/rejected strings through `WT_CONFIG_CHECK` metadata, especially category recursion and list choices for verbose/statistics/timing stress options.
- Connection startup tests exercise `__wt_conn_config_init` allocation and later cleanup through normal open/close flows.
- Compiled configuration tests should cover entries marked `compilable`, because those depend on the sizing fields and the parallel `method_id` indexing contract.
- Metadata compatibility and recovery tests are the primary signal for changes to `file.meta`, `object.meta`, `tier.meta`, and `tiered.meta` defaults.

## Cross-Chunk Notes

Chunk 1 contains the bulk of the generated `WT_CONFIG_CHECK` arrays and choice lists referenced here. The final per-file merge should connect those earlier validation definitions to this chunk's catalog entries, because this chunk is where all per-method schemas become reachable through `config_entries[]` and connection initialization.
