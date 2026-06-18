# subset-b-008968 Research

Grouped research for WiredTiger configuration API, validation, and merge/collapse implementation files. Each section preserves the original source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/config/config_api.c -->
# sources/storage-engines/wiredtiger/src/config/config_api.c

## Purpose

`config_api.c` is the public and connection-facing API layer for WiredTiger configuration parsing and extensible configuration definitions. It provides the `wiredtiger_config_parser_open` public helper, the `wiredtiger_config_validate` public validation helper, connection lifetime cleanup for dynamically allocated configuration metadata, and `__wt_configure_method`, which lets extensions add or override configuration options on existing API methods.

The file is deliberately thin around parsing itself: iteration and lookup are delegated to the core config parser helpers, while validation is delegated to `__wt_config_check`. Its main responsibilities are object lifetime, entry lookup, event-handler setup for standalone validation, and atomic replacement of connection configuration entries.

## Important APIs, Types, and Functions

`wiredtiger_config_parser_open(WT_SESSION *, const char *, size_t, WT_CONFIG_PARSER **)` allocates a `WT_CONFIG_PARSER_IMPL`, installs a static method table, stores the session, initializes both a `WT_CONFIG_ITEM` for lookup and a `WT_CONFIG` iterator for sequential traversal, and returns it as the public `WT_CONFIG_PARSER`.

`__config_parser_close`, `__config_parser_next`, and `__config_parser_get` implement the public parser methods. `close` frees the implementation via the stored session, `next` calls `__wt_config_next`, and `get` calls `__wt_config_subgets` against the whole saved config item.

`wiredtiger_config_validate` calls the private `__config_validate` wrapper with `__wt_conn_config_match`, so it validates a supplied config string against a named WiredTiger API’s generated configuration entry.

`__config_validate` accepts either a real session or an event handler, rejects the invalid combination of both, creates a minimal dummy connection/session when only an event handler is supplied, resolves the named `WT_CONFIG_ENTRY`, and invokes `__wt_config_check`.

`__wt_configure_method` implements `WT_CONNECTION.configure_method`. It appends a new default setting to an existing method’s base config, creates a replacement `WT_CONFIG_CHECK` array with one new or replacement check, validates the supplied config under the new rules, stores all newly allocated memory on the connection free-on-close list, and atomically publishes the new `WT_CONFIG_ENTRY *`.

`__config_add_checks` parses a check string such as `min=...`, `max=...`, and `choices=...` into the runtime fields on `WT_CONFIG_CHECK`: `min_value`, `max_value`, and a NULL-terminated `choices` array. For structured choice lists it enumerates each element and duplicates the raw choice strings.

`__conn_foc_add` and `__wt_conn_foc_discard` maintain and drain `WT_CONNECTION_IMPL::foc`, the connection-level free-on-close list used for dynamically installed configuration metadata.

The key types come from `src/include/config.h`: `WT_CONFIG_PARSER_IMPL` contains the public interface, `WT_SESSION_IMPL *`, `WT_CONFIG`, and `WT_CONFIG_ITEM`; `WT_CONFIG_ENTRY` names a method, base config string, generated check table, jump table, and compile metadata; `WT_CONFIG_CHECK` describes a single allowed key, including compiled type, optional checker callback, subconfig table, min/max bounds, and choices.

## Control Flow

Parser creation is linear: set output to `NULL`, cast the public session to `WT_SESSION_IMPL *`, allocate one parser, assign the static vtable, copy a bounded `WT_CONFIG_ITEM`, initialize a bounded `WT_CONFIG`, then publish the result. Later `next` advances the iterator, while `get` searches within the saved item without mutating the iterator state.

Validation first establishes an error-reporting context. With a real session it uses the connection attached to that session. With only an event handler it fabricates enough `WT_CONNECTION_IMPL` and `WT_SESSION_IMPL` state to route messages through `__wt_event_handler_set`. Then it requires non-NULL `name` and `config`, looks up the method either in static generated entries or the connection’s mutable `config_entries`, and finally calls `__wt_config_check`.

`__config_add_checks` initializes broad numeric bounds, iterates over the `check` descriptor string, and handles three recognized keys. `min` and `max` are parsed with `strtoll` and require the whole config value to be numeric. `choices` requires a value; if the value is a struct it first counts elements, allocates `count + 1` pointers, then duplicates each raw element; otherwise it allocates two pointers and stores one duplicated choice. Choice strings and the choice pointer array are registered for connection-close cleanup.

`__wt_configure_method` validates arguments and maps user-facing type strings to compiled type constants. It finds the target method in `conn->config_entries`, takes `conn->api_lock`, allocates a replacement entry, builds a new base string as `old_base,new_config`, extracts the new key name by truncating at `=`, copies all existing checks except a replaced key of the same name, fills the new check, validates the new config against the new entry, adds all allocated chunks to the free-on-close list, and publishes with `WT_RELEASE_WRITE_WITH_BARRIER`. Error cleanup is local until ownership is transferred to the free-on-close list.

## State and Persistence Behavior

The parser object owns only its small implementation allocation. It does not copy the input config string; both the `WT_CONFIG_ITEM` and iterator point at caller-provided memory. Callers must keep the config bytes alive until the parser is closed.

`wiredtiger_config_validate` has no durable side effects. The dummy connection path is stack-backed and exists solely for event dispatch during a standalone validation call.

`__wt_configure_method` mutates live connection state by replacing one pointer in `conn->config_entries`. Old and new configuration metadata can remain reachable by lock-free readers, so old dynamically allocated objects are intentionally retained until connection close. The free-on-close list is therefore a connection-lifetime persistence mechanism for memory, not on-disk configuration. The new base config influences future API config defaults and validation for the lifetime of the connection.

The source file has one surprising runtime side effect: `__config_add_checks` writes `entry->method` and `cp->name` to `stderr`. If this is compiled into normal builds, configuring methods may emit unexpected output outside WiredTiger’s event system.

## Dependencies and Integration Points

This file depends on `wt_internal.h` for allocation (`__wt_calloc_one`, `__wt_calloc_def`, `__wt_strdup`, `__wt_strndup`, `__wt_free`), parser initialization and traversal (`__wt_config_init`, `__wt_config_initn`, `__wt_config_subinit`, `__wt_config_next`, `__wt_config_subgets`, `__wt_config_subgetraw`), error macros, spin locks, connection access (`S2C`), and release-store barriers.

It integrates with generated config definitions in `config_def.c`. `__wt_conn_config_init` copies static `config_entries` into `conn->config_entries`, and `__wt_conn_config_match` searches the static list for validation without a live connection. `__wt_configure_method` updates the connection copy.

It integrates with `config_check.c` through `__wt_config_check`, which consumes the `WT_CONFIG_ENTRY` and `WT_CONFIG_CHECK` structures prepared or selected here.

Public integration points are declared in `wiredtiger.h.in`: applications and tests use `wiredtiger_config_parser_open` and `wiredtiger_config_validate`; extensions reach parser helpers through `config_ext.c`; tests in `test/csuite/config/main.c` and `test/cppsuite/src/main/configuration.cpp` create parsers over full and nested config strings.

## Risks and Edge Cases

The parser borrows config memory. Passing a temporary buffer and using the parser after the buffer is freed will produce invalid reads.

`__config_validate` rejects supplying both a session and an event handler because the handler would be ignored. Callers expecting the passed handler to override session behavior will get `EINVAL`.

`__wt_configure_method` intentionally ignores `uri`, so added options become valid for the entire method rather than a specific data source. This can mask misspelled or unsupported options for implementations that do not consume them.

`__conn_foc_add` ignores allocation failures. If the free-on-close list cannot grow, dynamically allocated config metadata can leak. The code comments accept this because `configure_method` is rare.

`__wt_configure_method` depends on pointer-sized atomic publication and connection-close cleanup to avoid locking readers. Any future change that frees old entries earlier would risk use-after-free by lock-free config readers.

`__config_add_checks` does not reject unknown check-string keys; it silently ignores anything except `min`, `max`, and `choices`. If a caller misspells a check directive, validation may be weaker than intended.

The `fprintf(stderr, ...)` in `__config_add_checks` is a behavioral risk for libraries and tests that expect no direct stderr output.

`__wt_strdup(session, check, &newcheck->checks)` is called after `newcheck->checks = check`; if the public `check` argument is optional and passed as `NULL`, this relies on `__wt_strdup` accepting NULL or will fail/crash depending on allocator helper semantics. The validation path handles `checks == NULL`, but the duplication call should be considered when changing API contracts.

## Test Signals

Existing parser behavior is exercised by `test/csuite/config/main.c`, which opens parsers, iterates config entries, recursively parses structs, and compares compiled config results against parser lookups. `test/cppsuite/src/main/configuration.cpp` also opens parsers for full and nested configs.

Useful targeted tests for this file include parser lifetime and NULL-output behavior, validation with session-only, event-handler-only, and invalid session-plus-handler inputs, unknown API name errors, `configure_method` replacement of an existing key, choice/min/max validation for dynamically added keys, and verification that dynamically configured methods continue to validate correctly after concurrent readers observe either the old or new entry.

Tests should also cover direct extension-facing use through `config_ext.c`, because extension parser wrappers delegate to `wiredtiger_config_parser_open`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/config/config_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/config/config_check.c -->
# sources/storage-engines/wiredtiger/src/config/config_check.c

## Purpose

`config_check.c` validates application-supplied WiredTiger configuration strings against a `WT_CONFIG_ENTRY` check table. It enforces allowed key names, expected value types, nested category schemas, custom checker callbacks, numeric min/max limits, and enumerated choices. This is the central runtime validation path used by public validation helpers and many API entry points unless a compiled configuration string can be trusted directly.

The file is performance-sensitive. Generated configuration tables can include sorted check arrays and ASCII jump tables, so validation can avoid scanning an entire method’s check table for every key.

## Important APIs, Types, and Functions

`__wt_config_check(WT_SESSION_IMPL *, const WT_CONFIG_ENTRY *, const char *, size_t)` is the exported validator. It returns success immediately for a NULL config, an entry with no check table, or a compilable config string that is already recognized as compiled for this connection. Otherwise it delegates to `__config_check`.

`__config_check` parses the supplied string with `__wt_config_init` or `__wt_config_initn`, iterates key/value pairs with `__wt_config_next`, validates each key and value against the matching `WT_CONFIG_CHECK`, recurses for category/subconfiguration values, runs optional checker callbacks, and enforces min/max and choices.

`__config_check_search` locates a `WT_CONFIG_CHECK` for a parsed key. For dynamic or unsized tables (`entries == 0`) it linearly scans until a NULL name. For generated tables it uses the first character and `checks_jump` to narrow the range, then calls `bsearch` with `__config_check_compare`.

`__config_check_compare` compares a parsed `WT_CONFIG_ITEM` key to a check name while respecting the parsed key length, preventing prefix matches from being accepted as full key matches.

`__wt_config_get_choice` checks whether a parsed item matches any string in a NULL-terminated `choices` list.

The important data contract is `WT_CONFIG_CHECK`: `name`, human-readable `type`, optional `checkf`, raw `checks`, optional `subconfigs`, generated `subconfigs_entries` and jump table, `compiled_type`, numeric bounds, and `choices`. `WT_CONFIG_ENTRY` supplies the check array, check count, jump table, and `compilable` flag.

## Control Flow

`__wt_config_check` is a gate. It deliberately treats missing inputs as successful because many callers make fast validation calls without first checking whether there is any config or check array. If a config has already been precompiled and the entry permits compiled configs, validation is skipped.

`__config_check` initializes a parser over either a NUL-terminated string or a bounded byte range. For each item, it first requires the key token type to be string or identifier. It searches for a matching check entry and fails with `EINVAL` on unknown keys.

Type enforcement is driven by `check->compiled_type`. Booleans accept native boolean tokens plus numeric 0 or 1; categories recurse into `check->subconfigs` over the value’s byte range; formats and strings do not add parser-level type restrictions; integers require `WT_CONFIG_ITEM_NUM`; lists require either an empty value or a struct. Unknown compiled types are treated as internal schema errors and return `EINVAL`.

After type checking, `checkf` is invoked if present. If `check->checks` is NULL, no min/max/choice validation is performed. Otherwise the value’s numeric `val` is compared with `min_value` and `max_value`, and configured `choices` are enforced. Structured choice values are iterated and every element must be found in the allowed choice list; scalar choices check the value directly.

Parser termination converts `WT_NOTFOUND` into success, preserving other parser errors.

## State and Persistence Behavior

This file does not own persistent state or mutate connection configuration. It reads immutable or connection-lifetime `WT_CONFIG_ENTRY` and `WT_CONFIG_CHECK` data and uses stack parser state. Recursive category validation re-enters the same logic with subconfig tables and a bounded view of the nested value.

The only durable effect is indirect: accepting or rejecting configuration controls whether callers proceed with API operations, connection open, schema changes, metadata updates, or dynamic method configuration. Error messages are delivered through the session’s error/event handling path.

Compiled configuration is an important state interaction. If `entry->compilable` is true and `__wt_conf_is_compiled(S2C(session), config)` returns true, this validator trusts that the string has already passed compilation-time checks and skips parsing.

## Dependencies and Integration Points

`config_check.c` depends on the core parser (`__wt_config_init`, `__wt_config_initn`, `__wt_config_next`, `__wt_config_subinit`), error macros, generated config metadata, `bsearch`, and compiled config detection from the `conf` subsystem.

It is called by `wiredtiger_config_validate` and `__wt_configure_method` in `config_api.c`, by connection open and reconfigure paths in `conn_api.c`, and by API macros in `src/include/api.h` via compiled-config setup. Generated entries and jump tables are produced in `config_def.c` and declared through `config.h`.

It aligns with `src/include/conf_inline.h`, where compiled config values use similar min/max and choice validation in `__wt_conf_check_one`; changes to validation semantics should be kept consistent across parsed and compiled paths.

## Risks and Edge Cases

Boolean validation intentionally accepts numeric 0 and 1. This matches existing parser behavior and compiled config tests, but it can surprise callers expecting only textual booleans.

Category validation maps any recursive `EINVAL` to `badtype`, then produces a generic expected-type message. Other errors propagate. This can reduce diagnostic specificity for nested unknown keys or invalid nested values.

For `WT_CONFIG_COMPILED_TYPE_STRING` and `WT_CONFIG_COMPILED_TYPE_FORMAT`, parser-level type restrictions are minimal. Any required semantic checks must live in `checkf` or choice metadata.

Min/max comparisons use `v.val` whenever `check->checks` is non-NULL. Check metadata must only install numeric bounds where the parsed value’s `val` is meaningful, or else non-numeric values could be compared against default numeric fields.

Structured choices reuse the local variable `v` for nested elements, so error messages for an invalid structured choice report the nested choice token as the value and the outer key as the key. This is intentional but worth preserving when refactoring.

The jump-table path assumes generated check arrays are sorted by key and that `checks_jump` bounds are valid for the table. Bad generator output can produce false unknown-key failures or out-of-range searches.

Keys beginning with non-ASCII or `0x7f` and above bypass the jump table range and fail as unknown. This matches the `WT_CONFIG_JUMP_TABLE_SIZE` 7-bit ASCII contract.

The fast path for compiled configs requires a non-NULL session. A NULL session cannot use `S2C(session)`, so standalone validation parses normally.

## Test Signals

Existing signals include public validation call sites, connection open/reconfigure validation, and config parser/compiled-config tests in `test/csuite/config/main.c`. Those tests explicitly account for numeric boolean input being converted to canonical booleans in compiled output.

Useful direct tests include unknown key rejection in both generated and dynamic `entries == 0` tables, prefix-key rejection, bounded non-NUL-terminated config validation, boolean numeric acceptance and invalid numeric rejection, integer/list/category type mismatches, nested category unknown key failures, min/max bounds, scalar and structured choices, custom `checkf` failures, and compiled-config skip behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/config/config_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/config/config_collapse.c -->
# sources/storage-engines/wiredtiger/src/config/config_collapse.c

## Purpose

`config_collapse.c` builds canonical configuration strings from ordered config layers. It has two related but distinct behaviors. `__wt_config_collapse` performs a shallow collapse using the first config string as the key universe and later strings as overrides. `__wt_config_merge` performs a deeper merge by flattening nested named structures, sorting all discovered entries, selecting the last value for each key, optionally stripping selected values, and reconstructing a nested config string.

These helpers are used when WiredTiger needs a newly allocated configuration string for metadata, schema, connection, tiered-storage, and utility paths.

## Important APIs, Types, and Functions

`__wt_config_collapse(WT_SESSION_IMPL *, const char **cfg, char **config_ret)` walks only `cfg[0]`, resolves each key’s final value across the full NULL-terminated config stack with `__wti_config_get`, appends `key=value,` into a scratch buffer, strips the trailing comma, and returns an allocated copy.

`WT_CONFIG_MERGE_ENTRY` stores one flattened key/value pair: duplicated key string, duplicated value string, generation number, and `strip` flag. The generation makes sorting stable for identical keys so later config layers win.

`WT_CONFIG_MERGE` owns the dynamically grown array of merge entries.

`__config_merge_scan` parses one config string, preserves quotes for string keys and values, rejects keys containing the separator character `[`, flattens nested named structures using separator-delimited key paths, detects whether struct values should be recursively merged, and appends scalar or unmergeable entries to the merge array.

`__config_merge_format_next` recursively reconstructs a config string from the sorted flattened entries. It skips superseded entries, treats nested keys as substructures, discards empty stripped levels, skips entries marked `strip`, and appends final `key=value,` fragments.

`__config_merge_format` allocates the output formatting buffer, starts recursive formatting at the root prefix, strips the final comma, and duplicates the result.

`__config_merge_cmp` sorts entries by flattened key and then generation.

`__wt_config_tiered_strip` is a convenience wrapper that strips `tiered_storage=(shared=)` from the merged output before metadata persistence.

`__wt_config_merge(WT_SESSION_IMPL *, const char **cfg, const char *cfg_strip, const char **config_ret)` is the exported deep merge entry point. It scans all config strings in least-to-most-preferred order, scans optional strip config last with `strip=true`, sorts, formats, frees the temporary entries, and returns the allocated merged config string.

## Control Flow

`__wt_config_collapse` starts with `*config_ret = NULL`, allocates a scratch buffer, initializes a parser over the first/default config string, and loops through default keys. For each key it validates the key token type, asks `__wti_config_get` for the effective value across all config strings, extends string keys and values to include surrounding quotes when present, and appends a comma-delimited assignment. The expected parser termination is `WT_NOTFOUND`; any other parser result is returned. The function handles an empty default config by returning an allocated empty string.

`__config_merge_scan` is the input flattening phase for deep merge. It parses one config string, creates scratch key and value buffers, and for each item constructs a flattened key as either `key` or `parent[key`. If the value is a struct, it recurses only when the struct has named fields, detected by `=` in the value, or when a previous flattened entry proves the same key has been a struct before. This second rule handles cases such as `log=(enabled)` overriding a previous named struct. Unnamed structs such as checkpoint LSN tuples are treated as scalar values and not decomposed.

`__wt_config_merge` scans normal config layers first and a strip layer last. Because every inserted entry gets a monotonically increasing generation, the final sort by key/generation places strip requests and later overrides after earlier defaults for the same flattened key.

`__config_merge_format_next` walks sorted entries. It skips earlier identical keys and earlier scalar entries replaced by later nested keys. When the next separator introduces a nested level, it appends `name=(`, recurses with the nested prefix, strips the nested trailing comma, appends `),`, and then removes the entire level if recursion produced an empty `()`. It skips entries marked for stripping and appends remaining scalar entries using the suffix after the current prefix.

## State and Persistence Behavior

All outputs are newly allocated strings owned by the caller. Temporary scratch buffers and merge arrays are freed before return. The functions do not mutate connection-global state.

The output strings often become persisted metadata or connection configuration state through callers. Integration searches show collapse/merge usage in metadata checkpoint updates, cursor metadata reads, schema create/alter, import, connection dhandle setup, connection reconfigure/open, tiered handle logic, compact config stripping, and `wt load`.

`__wt_config_tiered_strip` is explicitly persistence-oriented: it removes tiered storage fields that should not be stored in metadata, currently `tiered_storage=(shared=)`.

Ordering is canonicalized differently by the two APIs. Collapse preserves the order of keys in the first config string and drops any keys absent from that first string. Merge sorts flattened keys lexicographically before formatting, so output order is deterministic but not input-order preserving.

## Dependencies and Integration Points

This file depends on parser helpers (`__wt_config_init`, `__wt_config_next`, `__wti_config_get`), scratch buffers (`__wt_scr_alloc`, `__wt_scr_free`), dynamic buffers (`__wt_buf_fmt`, `__wt_buf_catfmt`), allocation helpers (`__wt_realloc_def`, `__wt_strndup`, `__wt_free`), `__wt_qsort`, and `WT_CONFIG_PRESERVE_QUOTES`.

Public declarations are in `src/include/extern.h`, with `__wt_config_merge` exported with default visibility. The export is used outside the immediate config module, including utilities and tiered/schema/connection code.

The behavior depends on tokenizer details from `config.h`: string item pointers can be expanded one byte backward and one byte forward by `WT_CONFIG_PRESERVE_QUOTES` when the original token was quoted.

Callers include `meta_ckpt.c`, `cur_metadata.c`, `schema_create.c`, `schema_alter.c`, `bt_import.c`, `conn_dhandle.c`, `conn_tiered.c`, `conn_reconfig.c`, `conn_api.c`, `conn_compact.c`, `tiered_handle.c`, and `utilities/util_load.c`.

## Risks and Edge Cases

`__wt_config_collapse` never emits keys that are absent from `cfg[0]`. That is intentional for default-driven collapse but dangerous if callers expect later config strings to introduce new keys.

Collapse does not merge nested structures. A later `key=(k4=v4)` replaces an earlier `key=(k2=v2,k3=v3)` as a whole.

Merge uses `[` as an internal separator and rejects source keys containing it. The comment notes this is not completely safe because JSON quoting could allow literal separator characters in application-controlled key namespaces.

The heuristic for deciding whether a struct is mergeable depends on `=` in the value or prior entries with the same prefix. This preserves unnamed tuple structs, but ambiguous values can behave differently depending on earlier config layers.

`__config_merge_format_next` relies on sorted flattened key order and separator placement to recurse correctly. Changes to the separator, sort comparator, or key construction must be coordinated.

Strip behavior is generation-based. Strip configs are scanned last so they override previous values; scanning strips earlier would silently fail to remove later values.

`__config_merge_cmp` returns only `1` or `-1` for equal keys based on generation and never returns `0` for two entries with the same key/generation. Since generation is unique per inserted entry this is stable enough, but duplicate generation bugs would violate comparator expectations.

Both APIs preserve quotes by adjusting parsed item spans. This assumes parser-provided string pointers have valid adjacent quote bytes as documented by `WT_CONFIG_PRESERVE_QUOTES`.

Error messages for invalid key types use `%s` with `k.str` in this file, while parsed keys are length-delimited. If malformed input produces a non-NUL-terminated key span for that error path, diagnostics may read past the token.

## Test Signals

Useful existing signals come from schema/metadata/tiered/connection tests that compare persisted metadata strings and from `test/csuite/config/main.c`, which recursively validates parser-visible merged configuration results against ordered inputs.

Targeted tests should cover collapse preserving first-config key order and dropping later-only keys, collapse replacing nested structs wholesale, merge combining named nested fields, merge preserving unnamed structs such as `(1,0)`, override precedence across multiple layers, scalar-to-struct and struct-to-scalar replacement, quote preservation for string keys and values, strip removal of scalar and nested keys, empty nested levels being removed after strip, separator-character rejection, and tiered-storage strip behavior for metadata-safe output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/config/config_collapse.c -->
