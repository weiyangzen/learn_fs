# subset-b-009844 Research

This grouped report covers the Samba source3 registry backend, dispatch, object-container, and `.reg` import/export files assigned to `subset-b-009844`. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_backend_perflib.c -->
# sources/user-network-fs/samba/source3/registry/reg_backend_perflib.c

## Purpose
`reg_backend_perflib.c` implements a virtual registry backend for the Windows performance library keys. It synthesizes values for `HKLM\SOFTWARE\MICROSOFT\WINDOWS NT\CURRENTVERSION\PERFLIB` and the English `...\PERFLIB\009` child rather than storing those values directly in `registry.tdb`.

## Important APIs, Types, And Functions
The exported integration point is `struct registry_ops perflib_reg_ops`, with `.fetch_values` and `.fetch_subkeys`. `perflib_params()` adds `Base Index`, `Last Counter`, `Last Help`, and `Version` as `REG_DWORD` values using `reg_perfcount_get_base_index()`, `reg_perfcount_get_last_counter()`, and `reg_perfcount_get_last_help()`. `perflib_009_params()` adds `Counter` and `Help` as `REG_MULTI_SZ` buffers returned by `reg_perfcount_get_counter_names()` and `reg_perfcount_get_counter_help()`.

## Control Flow
`perflib_fetch_values()` duplicates and normalizes the requested key, then dispatches to one of the two value producers. Subkey enumeration is not virtualized; `perflib_fetch_subkeys()` delegates to `regdb_ops.fetch_subkeys()`, so stored database children remain visible under the dynamic path.

## State And Persistence
No values are persisted by this backend. Value contents are computed from the performance counter subsystem on each fetch. Temporary buffers from performance counter helpers are released with `SAFE_FREE()` when a positive buffer size is returned.

## Dependencies And Integration Points
The backend depends on `registry.h`, `reg_util_internal.h`, `reg_perfcount.h`, `reg_objects.h`, and the default `regdb_ops`. It is registered under `KEY_PERFLIB` by `reg_init_full.c`, after which the hook cache routes matching key handles through `perflib_reg_ops`.

## Risks And Test Signals
The path checks use `strncmp(path, KEY, strlen(path))`, which treats shorter prefixes as matches and should be exercised with exact key names, the `009` child, and malformed/partial paths. Tests should verify DWORD byte sizes, correct `REG_MULTI_SZ` payloads, empty counter helper behavior, and continued delegation of subkey enumeration to the registry database.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_backend_perflib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_backend_printing.c -->
# sources/user-network-fs/samba/source3/registry/reg_backend_printing.c

## Purpose
`reg_backend_printing.c` implements a virtual registry view for printer data. It maps accesses under `HKLM\SYSTEM\CURRENTCONTROLSET\CONTROL\PRINT\PRINTERS` onto Samba's stored Windows NT printer registry path `HKLM\SOFTWARE\MICROSOFT\WINDOWS NT\CURRENTVERSION\PRINT\PRINTERS`.

## Important APIs, Types, And Functions
The central type is the local `struct reg_dyn_tree`, a dispatch row containing a normalized path and optional fetch/store callbacks for subkeys and values. `printing_ops` exports the backend through `registry_ops`. `create_printer_registry_path()` normalizes an input key and, for the control-printers tree, builds the corresponding WinNT-printers path. `match_registry_path()` finds the best matching dispatch row in `print_registry[]`.

## Control Flow
Public registry operations enter `regprint_fetch_reg_keys()`, `regprint_store_reg_keys()`, `regprint_fetch_reg_values()`, or `regprint_store_reg_values()`. Each resolves the input key to a `print_registry[]` index. The only active row targets `KEY_CONTROL_PRINTERS` and routes through `key_printers_*()`, which either translate the requested subpath or fall back to the WinNT printers root. Missing callbacks produce failure for stores/fetch-subkeys and zero values for fetch-values on an otherwise matched key.

## State And Persistence
This backend does not own persistent state. Reads and writes are delegated to `regdb_ops` against the normalized WinNT printer key. It therefore presents an alternate registry namespace over data persisted by the default registry database backend.

## Dependencies And Integration Points
It depends on `registry.h`, `reg_util_internal.h`, path constants from the registry layer, and `regdb_ops`. `reg_init_full.c` installs `printing_ops` under `KEY_PRINTING "\\Printers"` while other printing-related paths remain directly backed by `regdb_ops`.

## Risks And Test Signals
Ordering in `print_registry[]` matters because the first prefix match wins. Tests should cover root printer enumeration, nested printer paths, writes through the control path reflecting in the WinNT path, path normalization and separator variants, and unknown paths returning `-1`/`False`. The translation helper uses normalized prefix checks but slices the original `key`; mixed-case or unusual slash inputs should be included in tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_backend_printing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_backend_prod_options.c -->
# sources/user-network-fs/samba/source3/registry/reg_backend_prod_options.c

## Purpose
`reg_backend_prod_options.c` provides a dynamic Product Options registry backend. Its main job is to synthesize the Windows `ProductType` value from Samba's configured server role.

## Important APIs, Types, And Functions
`prod_options_reg_ops` exports `.fetch_values` and `.fetch_subkeys`. `prod_options_fetch_values()` calls `lp_server_role()` and maps domain controller roles to `LanmanNT`, standalone servers to `ServerNT`, and domain members to `WinNT`. The value is added with `regval_ctr_addvalue_sz()` as `REG_SZ`. `prod_options_fetch_subkeys()` delegates enumeration to `regdb_ops`.

## Control Flow
When the registry dispatcher fetches values for the hooked Product Options key, this backend computes the role string, inserts `ProductType`, and returns the current value count. It does not inspect the requested key beyond receiving it from the hook machinery, relying on `reg_init_full.c` to bind it to `KEY_PROD_OPTIONS`.

## State And Persistence
The backend is read-only for dynamic values and persists nothing. Subkeys can still come from the default registry database because subkey fetches pass through to `regdb_ops`.

## Dependencies And Integration Points
It depends on `registry.h`, `reg_objects.h`, `lp_server_role()`, Samba role constants, and the default registry database operations. It is registered by `registry_init_full()` under `KEY_PROD_OPTIONS`.

## Risks And Test Signals
Role-to-string compatibility is the main behavior to protect. Tests should simulate or configure each server role and verify the exact `ProductType` string and `REG_SZ` encoding. A future enum value could silently leave `value_ascii` empty, so tests around all known roles are useful. Subkey delegation should also be checked if stored child keys are expected below this virtual path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_backend_prod_options.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_backend_shares.c -->
# sources/user-network-fs/samba/source3/registry/reg_backend_shares.c

## Purpose
`reg_backend_shares.c` implements a minimal virtual registry backend for Samba share-related keys. In its current form it exposes a top-level `Security` subkey below `KEY_SHARES` and intentionally rejects direct registry writes.

## Important APIs, Types, And Functions
The exported `shares_reg_ops` fills `.fetch_subkeys`, `.fetch_values`, `.store_subkeys`, and `.store_values`. `trim_reg_path()` strips the `KEY_SHARES` prefix and returns a heap-allocated remaining path. `shares_subkey_info()` adds the `Security` subkey only for the top-level key. `shares_value_info()` currently reports no top-level values. Store callbacks always return `False`.

## Control Flow
Registry dispatch reaches this backend only for paths under `KEY_SHARES`. Both fetch functions trim the prefix, determine whether the request is for the top level, and then populate the supplied container. Disabled `#if 0` blocks show earlier or planned handling for deeper share/printing subpaths, but no such logic is active.

## State And Persistence
No data is persisted and no writes are accepted. `trim_reg_path()` uses `SMB_STRDUP()` and callers release with `SAFE_FREE()`. The backend returns derived structure only, with no sequence-number or database interaction.

## Dependencies And Integration Points
It uses `registry.h`, `reg_objects.h`, and the `KEY_SHARES` constant. `reg_init_full.c` hooks it under `KEY_SHARES`, letting registry clients enumerate this virtual area while preventing registry-based mutation of share data.

## Risks And Test Signals
The main risk is the limited implementation being mistaken for a complete share registry model. Tests should verify top-level enumeration returns only `Security`, deeper paths currently return zero data, and both store paths fail. Boundary tests for `trim_reg_path()` should include exactly `KEY_SHARES`, `KEY_SHARES\...`, and shorter invalid strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_backend_shares.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_backend_smbconf.c -->
# sources/user-network-fs/samba/source3/registry/reg_backend_smbconf.c

## Purpose
`reg_backend_smbconf.c` provides the registry operations for Samba configuration stored below `KEY_SMBCONF`. It is primarily a wrapper around `regdb_ops` with a custom access check requiring disk-operator privilege.

## Important APIs, Types, And Functions
The exported `smbconf_reg_ops` implements fetch/store, create/delete subkey, security descriptor get/set, cache freshness checks, and access checks. `smbconf_reg_access_check()` requires `SEC_PRIV_DISK_OPERATOR` on the provided security token and grants `REG_KEY_ALL` when present. All other operations call through to the same method in `regdb_ops`.

## Control Flow
Registry callers access keys through the dispatcher, which invokes `smbconf_reg_ops` for hooked smbconf paths. Data operations are direct pass-throughs to the registry database. Authorization is the only substantive change: unlike the default security descriptor path, callers without disk-operator privilege are denied before a granted mask is returned.

## State And Persistence
Persistent state lives in the registry database backend. This file does not cache or store anything itself, but it participates in cache invalidation by delegating `subkeys_need_update` and `values_need_update` to `regdb_ops`.

## Dependencies And Integration Points
It depends on `registry.h`, `lib/privileges.h`, `SEC_PRIV_DISK_OPERATOR`, and `regdb_ops`. `reg_init_full.c` hooks it for the full registry, while `reg_init_smbconf.c` can initialize only a selected smbconf key for tools such as `net conf` and loadparm paths.

## Risks And Test Signals
Authorization tests are critical: privileged tokens should receive `REG_KEY_ALL`, while non-privileged tokens fail even for reads. Data operation tests should verify that create, delete, fetch, store, security descriptors, and update checks remain equivalent to `regdb_ops`. Because access checks unconditionally grant all access once the privilege is present, privilege assignment is the security boundary.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_backend_smbconf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_backend_tcpip_params.c -->
# sources/user-network-fs/samba/source3/registry/reg_backend_tcpip_params.c

## Purpose
`reg_backend_tcpip_params.c` synthesizes TCP/IP parameter registry values, replacing an older dynamic overlay for host identity data.

## Important APIs, Types, And Functions
`tcpip_params_reg_ops` exports `.fetch_values` and `.fetch_subkeys`. `tcpip_params_fetch_values()` adds `Hostname` from `myhostname()` and `Domain` from `get_mydnsdomname(talloc_tos())`, both through `regval_ctr_addvalue_sz()` as `REG_SZ`. `tcpip_params_fetch_subkeys()` delegates to `regdb_ops.fetch_subkeys()`.

## Control Flow
The hook cache routes `KEY_TCPIP_PARAMS` to this backend. Fetching values produces the two dynamic values and returns the container count. Subkey enumeration is passed to the persistent registry database.

## State And Persistence
The dynamic values are not persisted; they reflect current host and DNS-domain information at fetch time. Temporary allocation for the DNS domain uses the top-of-stack talloc context.

## Dependencies And Integration Points
The file depends on Samba host-name helpers, `registry.h`, `reg_objects.h`, and `regdb_ops`. It is registered from `reg_init_full.c` under `KEY_TCPIP_PARAMS`.

## Risks And Test Signals
Tests should verify correct `REG_SZ` encoding, behavior when no DNS domain is configured, and consistency with `myhostname()` changes in the test environment. Subkey delegation should be covered separately. If the DNS helper can return `NULL`, callers should ensure `regval_ctr_addvalue_sz()` behavior remains acceptable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_backend_tcpip_params.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_cachehook.c -->
# sources/user-network-fs/samba/source3/registry/reg_cachehook.c

## Purpose
`reg_cachehook.c` owns the registry hook cache: a path tree mapping registry key prefixes to `struct registry_ops` implementations. It lets the frontend find the correct backend for any registry key while falling back to the default database backend.

## Important APIs, Types, And Functions
`reghook_cache_init()` initializes the global `cache_tree` with `regdb_ops` as the default. `reghook_cache_add()` converts a key name into the path-tree format and inserts an ops pointer. `reghook_cache_find()` resolves a key name to the best matching ops pointer. `reghook_dump_cache()` prints the tree for diagnostics. The helper `keyname_to_path()` prepends a backslash because the path-tree implementation expects that shape.

## Control Flow
Initialization is idempotent: if `cache_tree` already exists, `reghook_cache_init()` returns success. Full or partial registry init calls `reghook_cache_add()` for each virtual backend. Later, registry open paths call `reghook_cache_find()` to select operations for a key handle.

## State And Persistence
The only state is the process-global `static struct sorted_tree *cache_tree`. It is in-memory and not persisted. Stored registry values remain in the backend selected by each ops pointer, usually `regdb_ops`.

## Dependencies And Integration Points
The file depends on `adt_tree.h` for `pathtree_init()`, `pathtree_add()`, `pathtree_find()`, and `pathtree_print_keys()`, plus `registry.h` and `reg_cachehook.h`. It is used by `reg_init_basic.c`, `reg_init_full.c`, and `reg_init_smbconf.c`.

## Risks And Test Signals
The cache has global lifetime and no explicit teardown in this file, so tests should isolate process state or reinitialize carefully. `reghook_cache_add()` assumes initialization has happened; direct calls before `reghook_cache_init()` risk null tree use. Tests should verify default fallback, longest-prefix matching, invalid parameter returns, duplicate/repeated initialization, and debug dump stability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_cachehook.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_cachehook.h -->
# sources/user-network-fs/samba/source3/registry/reg_cachehook.h

## Purpose
`reg_cachehook.h` declares the hook-cache interface used to register and resolve registry backends by key path.

## Important APIs, Types, And Functions
The header exposes `reghook_cache_init()`, `reghook_cache_add(const char *keyname, struct registry_ops *ops)`, `reghook_cache_find(const char *keyname)`, and `reghook_dump_cache(int debuglevel)`. It forward-relies on `WERROR` and `struct registry_ops` being visible through includers such as `registry.h`.

## Control Flow
Callers initialize the cache, add one or more key-to-ops mappings, then resolve key names during registry open/dispatch. The dump function is diagnostic and has no return value.

## State And Persistence
The header declares no data. Its implementation manages an in-memory process-global path tree and does not persist the hook map.

## Dependencies And Integration Points
Included by registry initialization modules and any code that needs hook lookup. It forms a small public boundary over `reg_cachehook.c` while hiding the `sorted_tree` implementation.

## Risks And Test Signals
The header has no direct include of `registry.h`, so include-order assumptions matter. Compile tests should cover consumers that include it after the necessary type definitions. API tests should focus on the implementation's invalid-parameter and default-backend behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_cachehook.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_db.h -->
# sources/user-network-fs/samba/source3/registry/reg_db.h

## Purpose
`reg_db.h` centralizes constants for Samba's internal registry database format and dbwrap/tdb flags.

## Important APIs, Types, And Functions
The header defines `REG_TDB_FLAGS` as `TDB_SEQNUM`, `REG_DBWRAP_FLAGS` as `DBWRAP_FLAG_NONE`, database format versions `REGDB_VERSION_V1`, `REGDB_VERSION_V2`, `REGDB_VERSION_V3`, and `REGDB_CODE_VERSION` as version 3. It also defines storage key prefixes: `REG_VALUE_PREFIX`, `REG_SECDESC_PREFIX`, and historical `REG_SORTED_SUBKEYS_PREFIX`.

## Control Flow
There is no executable control flow. The constants are consumed by the registry database backend when opening, migrating, and encoding entries in the persistent registry database.

## State And Persistence
This file directly describes persistent format state. `REGDB_CODE_VERSION` is the current database schema level, and the prefix strings shape how values and security descriptors are stored. Version comments indicate that V2 introduced normalized keys and V3 changed key-existence semantics while removing the sorted-subkeys cache.

## Dependencies And Integration Points
The constants are used by `reg_backend_db.c` and related registry database code. `TDB_SEQNUM` is important for sequence-number based cache freshness in higher layers.

## Risks And Test Signals
Changing these constants affects on-disk compatibility. Tests should cover database initialization, migration from older versions, sequence-number behavior, and lookup of values/security descriptors by prefix. Since V3 changed existence semantics, regression tests should include empty keys, keys with only values, and deleted subkey cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_db.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_dispatcher.c -->
# sources/user-network-fs/samba/source3/registry/reg_dispatcher.c

## Purpose
`reg_dispatcher.c` provides frontend wrapper functions that call the selected registry backend operations for an open key handle. It also supplies default registry security descriptor behavior when a backend does not implement its own.

## Important APIs, Types, And Functions
The public functions mirror `registry_ops`: `store_reg_keys()`, `store_reg_values()`, `create_reg_subkey()`, `delete_reg_subkey()`, `fetch_reg_keys()`, `fetch_reg_values()`, `regkey_access_check()`, `regkey_get_secdesc()`, `regkey_set_secdesc()`, `reg_subkeys_need_update()`, and `reg_values_need_update()`. `construct_registry_sd()` builds the fallback security descriptor with read access for Everyone and full access for Builtin Administrators and System. `reg_generic_map` maps generic access to registry-specific rights.

## Control Flow
Most wrappers check `key->ops` and the relevant function pointer, call it if present, and otherwise return `false`, `-1`, `WERR_NOT_SUPPORTED`, or `WERR_ACCESS_DENIED`. `regkey_access_check()` gives root mode a full-access bypass, uses backend-specific access checks when present, otherwise gets a security descriptor, maps generic bits, and calls `se_access_check()`.

## State And Persistence
This file does not persist state. It is a dispatch layer over backend state and builds temporary security descriptors under the caller's talloc context. Freshness checks default to `true`, forcing callers to refresh if a backend does not provide sequence-aware logic.

## Dependencies And Integration Points
It depends on `registry.h`, `reg_dispatcher.h`, `system/passwd.h` for root-mode support, and Samba security helpers. Registry frontend code calls these wrappers after `reghook_cache_find()` has placed an ops pointer in `struct registry_key_handle`.

## Risks And Test Signals
Default security behavior is security-sensitive. Tests should cover root bypass, backend override, fallback descriptor ACEs, generic access mapping, denied requests, and failure to read backend security descriptors falling back only when appropriate. Wrapper tests should verify each missing callback returns the documented default and that update checks default to refresh-needed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_dispatcher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_dispatcher.h -->
# sources/user-network-fs/samba/source3/registry/reg_dispatcher.h

## Purpose
`reg_dispatcher.h` declares the registry frontend dispatch helpers implemented in `reg_dispatcher.c`.

## Important APIs, Types, And Functions
It exposes store, create/delete, fetch, access-check, security descriptor, and cache freshness functions for `struct registry_key_handle`, `struct regsubkey_ctr`, and `struct regval_ctr`.

## Control Flow
Callers use these declarations after opening a registry key handle. The implementation routes each operation through the handle's selected `registry_ops` table or applies a default.

## State And Persistence
The header contains no state. The implementation works against backend state and transient talloc-allocated security descriptors.

## Dependencies And Integration Points
The declarations assume registry core types, `WERROR`, `TALLOC_CTX`, `security_descriptor`, and `security_token` are available through surrounding includes. It is an internal boundary between registry frontend code and backend ops tables.

## Risks And Test Signals
Compile coverage should include consumers that include this header in normal registry translation units. Behavioral tests belong to `reg_dispatcher.c`, with emphasis on missing callback defaults and security descriptor fallback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_dispatcher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_format.c -->
# sources/user-network-fs/samba/source3/registry/reg_format.c

## Purpose
`reg_format.c` formats registry keys and values as `.reg` file lines. It can write to an arbitrary line callback, act as a `reg_parse_callback`, or write a complete encoded file with headers, optional BOM, and final local-variable comments.

## Important APIs, Types, And Functions
The opaque `struct reg_format` embeds a `reg_parse_callback` as its first field so it can be passed where parser callbacks are expected. Public formatters include `reg_format_new()`, `reg_format_file()`, `reg_format_key()`, `reg_format_value()`, `reg_format_value_delete()`, `reg_format_comment()`, and wrappers for `registry_key`, `registry_value`, and `regval_blob`. Helpers print hives and key segments with configurable case and separators. `reg_format_file_opt()` parses file options such as `regedit4`, `regedit5`, `enc`, `fileenc`, `strenc`, `flags`, `sep`, `head`, `nl`, and `bom`.

## Control Flow
Key formatting emits a blank line and a bracketed key, with `[-key]` for deletes. Value formatting chooses a compact textual form when possible: `REG_SZ` becomes a quoted string if zero-terminated UTF-16 and not forced to hex, `REG_DWORD` becomes `dword:%08x` when the size is four bytes, and other values become hex lists with line continuations. `REG_MULTI_SZ` and `REG_EXPAND_SZ` can be transcoded before hex output when a string encoding is configured.

## State And Persistence
Formatter state includes flags, separator, output callback, and an iconv descriptor from UTF-16. File-backed formatters own `FILE *`, newline bytes, file encoding converter, and close through a talloc destructor. The module writes persistent `.reg` files but does not alter Samba registry storage itself.

## Dependencies And Integration Points
It depends on `cbuf`, `srprs`, `reg_parse_internal`, registry value types, and Samba charset/iconv helpers. It is intentionally symmetric with `reg_parse.c`: a formatter can receive parse callbacks, and parser output can be directed into a formatter for conversion or normalization.

## Risks And Test Signals
Important risks include charset conversion failure, line-continuation correctness over the 76-column threshold, flag confusion (`REG_DWORD` checks `REG_FMT_HEX_SZ` in the code path), and lifecycle of file-backed destructors. Tests should round-trip keys and values through parser and formatter, cover default value `@`, key deletion, value deletion, UTF-16 `REG_SZ`, multi-line hex, custom separators/case, BOM output, and file close behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_format.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_format.h -->
# sources/user-network-fs/samba/source3/registry/reg_format.h

## Purpose
`reg_format.h` declares the public `.reg` formatter API and documents how formatter objects can also serve as parser callbacks.

## Important APIs, Types, And Functions
The header defines opaque `reg_format`, `reg_format_callback_writeline_t`, and `struct reg_format_callback`. It declares constructors `reg_format_new()` and `reg_format_file()`, high-level wrappers for `registry_key`, `registry_value`, and `regval_blob`, low-level `reg_format_key()` and `reg_format_value()`, deletion/comment helpers, and `reg_format_set_options()`. It defines flags `REG_FMT_HEX_SZ`, `REG_FMT_HEX_DW`, `REG_FMT_HEX_BIN`, `REG_FMT_HEX_ALL`, `REG_FMT_LONG_HIVES`, and `REG_FMT_SHORT_HIVES`.

## Control Flow
Consumers create a formatter with a line callback or output file, then call key/value functions. Because the implementation embeds a `reg_parse_callback`, the object can be used as a parser target to re-emit parsed input.

## State And Persistence
The header describes an opaque talloc-owned object. File-backed instances persist formatted registry data to disk; callback-backed instances delegate persistence to the provided writer.

## Dependencies And Integration Points
It forward-declares registry value/key structures and `regval_blob`, avoiding heavier includes for API users. It is paired with `reg_parse.h` for import/export round-trips and with `reg_import.h` for registry API adapters.

## Risks And Test Signals
The macro `REG_FMT_HEX_ALL` includes a trailing semicolon, which can surprise expression users. API tests should compile typical and flag-combination callers. Functional tests should verify documented return conventions, callback error propagation, and talloc ownership expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_format.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_import.c -->
# sources/user-network-fs/samba/source3/registry/reg_import.c

## Purpose
`reg_import.c` adapts parsed `.reg` events to registry mutation callbacks. It bridges `reg_parse` output to several possible value-setting APIs: raw blobs, `struct registry_value`, or `struct regval_blob`.

## Important APIs, Types, And Functions
The local `struct reg_import` embeds `struct reg_parse_callback` first, stores a `struct reg_import_callback`, and tracks the current `open_key`. `reg_import_adapter()` is the public constructor. Event handlers include `reg_parse_callback_key()`, `reg_parse_callback_val()`, `reg_parse_callback_val_registry_value()`, `reg_parse_callback_val_regval_blob()`, `reg_parse_callback_val_del()`, and `reg_parse_callback_comment()`.

## Control Flow
On a parsed key, the adapter closes any currently open key. Delete-key events call `deletekey()` and treat `WERR_FILE_NOT_FOUND` as success. Create/open events call `createkey()` and store the returned key handle. Parsed values are forwarded to the configured setter variant based on `setval_type`. Value deletes call `deleteval()`. Comments are logged and ignored.

## State And Persistence
Persistent changes are performed by user-supplied callbacks. The adapter owns only transient parser state and the current open-key pointer. Missing open/close/create/delete callbacks are replaced with no-op functions, but set-value callbacks are asserted for active setter modes.

## Dependencies And Integration Points
It depends on `reg_parse.h`, `reg_import.h`, `registry.h`, and `reg_objects.h`. It is designed to be passed as a `reg_parse_callback` to `reg_parse_file()` or `reg_parse_fd()`.

## Risks And Test Signals
The adapter assumes values appear after a successful key event; tests should check parser enforcement and callback behavior when `open_key` is null. Because missing set-value callbacks trigger assertions, misconfigured import code can abort rather than return an error. Tests should cover all three setter modes, key close ordering, delete-missing-as-success, value delete errors, and memory ownership for temporary `DATA_BLOB` and `regval_blob` objects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_import.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_import.h -->
# sources/user-network-fs/samba/source3/registry/reg_import.h

## Purpose
`reg_import.h` defines the callback contract used by `reg_import.c` to turn parsed `.reg` data into registry API operations.

## Important APIs, Types, And Functions
It declares callback typedefs for opening, closing, creating, deleting keys, deleting values, and setting values in three forms: raw blob, `struct registry_value`, or `struct regval_blob`. `struct reg_import_callback` groups these callbacks, a setter union, a `setval_type` enum (`NONE`, `BLOB`, `REGISTRY_VALUE`, `REGVAL_BLOB`), and opaque `data`. `reg_import_adapter()` creates the parser callback object.

## Control Flow
Import users populate `struct reg_import_callback`, choose a setter mode, create an adapter, and pass it to the `.reg` parser. The implementation supplies no-op defaults for non-value operations but requires the selected setter function for value import modes.

## State And Persistence
The header defines no state itself. Persistence is controlled entirely by callback implementations supplied by consumers.

## Dependencies And Integration Points
It includes `reg_parse.h` and forward-declares registry value/blob types. It is the public adapter boundary between parser code and registry mutation backends.

## Risks And Test Signals
Tests should compile each setter variant and validate callback signatures. Runtime tests should verify no-op defaults, selected setter assertions, and that callback private data is passed unchanged through all operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_import.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_init_basic.c -->
# sources/user-network-fs/samba/source3/registry/reg_init_basic.c

## Purpose
`reg_init_basic.c` implements common registry initialization and a basic initializer that sets up the database and hook cache without installing the full set of virtual backends.

## Important APIs, Types, And Functions
`registry_init_common()` calls `regdb_init()`, `reghook_cache_init()`, and `init_registry_data()`, returning a `WERROR`. `registry_init_basic()` logs, calls the common initializer, closes the registry database with `regdb_close()`, and returns the result.

## Control Flow
Initialization fails fast for database and hook-cache setup. Registry data initialization errors are logged and returned through `werr`. The basic initializer always closes the database after common initialization so later processes or callers can open it as needed.

## State And Persistence
This code initializes persistent registry database content through `init_registry_data()` and initializes the in-memory hook cache. It does not itself register virtual backends beyond the cache default established by `reghook_cache_init()`.

## Dependencies And Integration Points
It depends on `registry.h`, `reg_init_basic.h`, `reg_cachehook.h`, and `reg_backend_db.h`. Full and smbconf-specific initialization reuse `registry_init_common()`.

## Risks And Test Signals
Tests should cover failure propagation from `regdb_init()` and `reghook_cache_init()`, database closure after basic init, and idempotency when called more than once. Initialization should also be tested against an empty registry database to verify built-in keys and values are created.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_init_basic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_init_basic.h -->
# sources/user-network-fs/samba/source3/registry/reg_init_basic.h

## Purpose
`reg_init_basic.h` declares the common and basic registry initialization entry points.

## Important APIs, Types, And Functions
It exposes `registry_init_common()` and `registry_init_basic()`, both returning `WERROR`.

## Control Flow
Consumers call `registry_init_basic()` when they need database setup without all virtual hooks, or `registry_init_common()` when they will perform additional registration before closing the database.

## State And Persistence
The header has no state. Its implementation initializes persistent registry data and the in-memory hook cache.

## Dependencies And Integration Points
It is included by `reg_init_full.c` and `reg_init_smbconf.c` to share the common initialization path.

## Risks And Test Signals
Compile tests should ensure `WERROR` is visible through includers. Behavioral coverage belongs to the implementation, especially database close semantics and error propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_init_basic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_init_full.c -->
# sources/user-network-fs/samba/source3/registry/reg_init_full.c

## Purpose
`reg_init_full.c` initializes the registry with all available source3 virtual backends and default database-backed paths.

## Important APIs, Types, And Functions
It declares external `registry_ops` tables for printing, eventlog, shares, smbconf, netlogon parameters, product options, TCP/IP parameters, performance text, current version, perflib, and the default database. `struct registry_hook` pairs a key name with an ops table. `reg_hooks[]` is the authoritative registration list. `registry_init_full()` installs those hooks into the hook cache.

## Control Flow
`registry_init_full()` calls `registry_init_common()`, loops over `reg_hooks[]`, and calls `reghook_cache_add()` for each entry. If any hook insertion fails, initialization stops. At high debug levels it dumps the hook tree. The function closes the registry database before returning.

## State And Persistence
Persistent base registry data is initialized by the shared common path. The full initializer populates only the process-local hook cache; the hook map itself is not persisted.

## Dependencies And Integration Points
It depends on the backend ops symbols from multiple registry modules and on key constants from `registry.h`. It is the central integration point that determines which backend owns which registry subtree.

## Risks And Test Signals
Hook ordering matters for prefix matching, so tests should verify the selected backend for each registered key and representative child paths. Failure tests should cover hook-cache add errors and common-init errors. Build/link tests are also important because this file references many external backend symbols.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_init_full.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_init_full.h -->
# sources/user-network-fs/samba/source3/registry/reg_init_full.h

## Purpose
`reg_init_full.h` declares the full registry initialization entry point.

## Important APIs, Types, And Functions
It exposes `WERROR registry_init_full(void)`.

## Control Flow
Callers use this API when they need the registry database initialized and every configured virtual backend registered in the hook cache.

## State And Persistence
The header contains no state. The implementation initializes persistent registry data and process-local hook-cache mappings.

## Dependencies And Integration Points
It is consumed by daemon or service setup code that needs the complete registry view rather than a limited smbconf or basic view.

## Risks And Test Signals
Compile tests should ensure callers include the correct base registry types before this header. Runtime coverage belongs to `reg_init_full.c`, especially backend registration coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_init_full.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_init_smbconf.c -->
# sources/user-network-fs/samba/source3/registry/reg_init_smbconf.c

## Purpose
`reg_init_smbconf.c` initializes just the smbconf portion of the registry. It is intended for paths that do not need the full registry backend set, such as `net conf` and loadparm-related use.

## Important APIs, Types, And Functions
`registry_init_smbconf(const char *keyname)` defaults a null key to `KEY_SMBCONF`, calls `registry_init_common()`, ensures the target key exists through `init_registry_key()`, and registers `smbconf_reg_ops` for that key with `reghook_cache_add()`.

## Control Flow
The function performs common initialization first. If key initialization fails, it logs a level-1 error and returns. If hook registration fails, it logs a separate error. It closes the registry database before returning in all paths after common initialization.

## State And Persistence
It creates or verifies the persistent smbconf registry key and adds a process-local hook-cache mapping to `smbconf_reg_ops`. It does not register unrelated virtual backends.

## Dependencies And Integration Points
It depends on `registry.h`, `reg_cachehook.h`, `reg_backend_db.h`, `reg_init_basic.h`, and `smbconf_reg_ops`. It complements `registry_init_full()` with a narrower setup surface.

## Risks And Test Signals
Tests should cover null-key defaulting, custom key names, failure from common init, failure from key creation, and failure from hook-cache insertion. Access-control behavior should be tested through the smbconf backend after this initializer has registered it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_init_smbconf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_init_smbconf.h -->
# sources/user-network-fs/samba/source3/registry/reg_init_smbconf.h

## Purpose
`reg_init_smbconf.h` declares the narrow smbconf registry initialization API.

## Important APIs, Types, And Functions
It exposes `WERROR registry_init_smbconf(const char *keyname)`.

## Control Flow
Callers pass a specific registry key or `NULL` for the default `KEY_SMBCONF` path. The implementation initializes common registry state and registers the smbconf backend only for that path.

## State And Persistence
The header has no state. The implementation may create the named registry key in persistent storage and updates the in-memory hook cache.

## Dependencies And Integration Points
Used by configuration tooling and loadparm-related code that needs registry-backed smb.conf data without full registry initialization.

## Risks And Test Signals
Compile coverage should ensure `WERROR` is available. Runtime tests should validate the null default and custom-key hook registration in the implementation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_init_smbconf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_objects.c -->
# sources/user-network-fs/samba/source3/registry/reg_objects.c

## Purpose
`reg_objects.c` implements the in-memory containers used to pass registry subkeys and values between backends, dispatchers, and callers.

## Important APIs, Types, And Functions
It defines private `struct regval_blob`, `struct regval_ctr`, and `struct regsubkey_ctr`. Subkey APIs include init, reinit, sequence-number accessors, add/delete/existence, count, and indexed lookup. Value APIs include init, count, accessors for name/type/data/size, indexed and name lookup, compose, add/copy/delete, `REG_SZ` and `REG_MULTI_SZ` helpers, and sequence-number accessors.

## Control Flow
Subkey initialization allocates a talloc-owned container and an in-memory dbwrap rbtree for case-insensitive key-name lookup. Adding a subkey skips null and duplicate names, grows the pointer array, duplicates the name, hashes it with its index, and increments the count. Deleting looks up the index, removes the hash entry, shifts the array, and rehashes shifted entries. Value addition deletes any existing value with the same name, grows the pointer array, composes a new blob, and appends it.

## State And Persistence
Containers are talloc-owned transient state. Sequence numbers allow callers to compare container freshness against backend database sequence numbers. The subkey hash is an in-memory rbtree, not persistent storage.

## Dependencies And Integration Points
The file depends on registry types, dbwrap rbtree, TDB utility helpers, `util_reg` push functions, and string wrappers. Backends populate these containers in their fetch methods; database code and RPC/frontends consume them.

## Risks And Test Signals
Memory ownership and error recovery are the main risks. `regval_ctr_addvalue()` resets `num_values` to zero on allocation failure, which can discard existing logical contents. Subkey deletion does not shrink/free removed string slots because talloc context ownership handles lifetime. Tests should cover case-insensitive subkey existence, duplicate suppression, deletion and rehashing, value replacement, zero-length values, long value-name truncation through `fstring`, sequence numbers, and allocation-failure behavior where possible.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_objects.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_objects.h -->
# sources/user-network-fs/samba/source3/registry/reg_objects.h

## Purpose
`reg_objects.h` declares opaque registry value and subkey container APIs for source3 registry code.

## Important APIs, Types, And Functions
It forward-declares `struct regval_blob`, `struct regval_ctr`, and `struct regsubkey_ctr`, then exposes subkey container creation, reset, sequence numbers, add/delete/existence/count/indexed lookup, and value container creation, accessors, lookup, composition, add/copy/delete, string helpers, and sequence numbers.

## Control Flow
Users allocate containers with the init functions, pass them to backend fetch/store operations, inspect counts and entries, and free them through the talloc parent. The implementation requires the objects themselves to be talloc-allocated because internal data is attached to their talloc context.

## State And Persistence
The header describes transient in-memory containers. Sequence numbers expose backend freshness state but do not persist by themselves.

## Dependencies And Integration Points
Backends in this subset use the API to synthesize values and enumerate subkeys. Registry database and RPC-facing code use it as the common exchange format.

## Risks And Test Signals
Because structures are opaque, ABI users must not stack-allocate or embed them. Compile and runtime tests should cover correct init/free patterns, sequence-number handling, and all lookup paths. Tests should also validate string value helpers use Windows registry encodings as expected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_objects.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_parse.c -->
# sources/user-network-fs/samba/source3/registry/reg_parse.c

## Purpose
`reg_parse.c` parses Windows `.reg` files line-by-line or from a file descriptor and emits structured events through `struct reg_parse_callback`. It handles keys, key deletes, values, value deletes, comments, line continuations, and file/string charset conversion.

## Important APIs, Types, And Functions
The opaque `struct reg_parse` embeds `struct reg_format_callback` first so it can be used as a formatter writer. Public APIs are `reg_parse_new()`, `reg_parse_line()`, `reg_parse_fd()`, `reg_parse_file()`, and `reg_parse_set_options()`. Internal state values are `STATE_DEFAULT`, `STATE_KEY_OPEN`, `STATE_VAL_HEX_CONT`, and `STATE_VAL_SZ_CONT`. Primitive parsers include `srprs_key()`, `srprs_val_name()`, `srprs_val_dword()`, `srprs_val_sz()`, `srprs_val_hex()`, `srprs_val_hex_values()`, and comment/eol helpers.

## Control Flow
`reg_parse_line()` first handles continuation states, then recognizes empty lines, key lines, comments, a first-line header, or value assignments. Values are valid only after a key has opened. DWORDs are packed little-endian into the value buffer, quoted strings are converted from Unix to UTF-16LE with terminator, and hex values can continue over multiple lines. `reg_parse_fd()` reads bytes, guesses or applies file encoding, converts chunks to Unix charset, extracts complete lines, and feeds them to `reg_parse_line()`.

## State And Persistence
Parser state is transient and talloc-owned. It tracks current key, value name/type/blob, line number, return code, flags, and an optional converter for non-UTF-16 encoded string payloads. It does not persist registry changes; callbacks decide what to store.

## Dependencies And Integration Points
The file depends on `cbuf`, `srprs`, `reg_parse_internal`, `reg_parse.h`, `reg_format.h`, POSIX file APIs, and Samba iconv wrappers. It integrates with `reg_import.c` for mutation and `reg_format.c` for round-trip conversion.

## Risks And Test Signals
This is a high-risk parser surface. Tests should cover malformed lines, trailing garbage, values before keys, headers, comments, key deletes, default values, value deletes, DWORD endian encoding, empty and continued hex lists, continued quoted strings, file encodings with BOM/no BOM, chunk boundaries in `reg_parse_fd()`, fail-level behavior, and conversion failures. Fuzzing line parser primitives would be useful because they manipulate shared `cbuf` state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_parse.h -->
# sources/user-network-fs/samba/source3/registry/reg_parse.h

## Purpose
`reg_parse.h` declares the public parser API for registration-entry `.reg` files and documents the callback event model.

## Important APIs, Types, And Functions
It defines callback typedefs for key events, value events, value-delete events, and comments. `struct reg_parse_callback` groups those handlers with opaque `data`. It declares opaque `reg_parse`, `reg_parse_new()`, `reg_parse_line()`, `reg_parse_fd()`, `reg_parse_file()`, and `reg_parse_set_options()`.

## Control Flow
Users create a parser with callbacks and feed it lines, a file descriptor, or a filename. Parsed events are delivered in file order. The implementation supplies no-op callbacks when fields are null, so consumers can ignore event categories.

## State And Persistence
The parser object is talloc-owned and transient. Persistence happens only through callbacks supplied by consumers such as the import adapter.

## Dependencies And Integration Points
The header includes standard integer and boolean types and is used by `reg_import`, `reg_format`, and registry tooling. Its comment notes that parser objects can act as `reg_format_callback` implementations because of the implementation layout.

## Risks And Test Signals
Callback signatures are the compatibility boundary. Compile tests should cover callbacks with each event type. Runtime tests should validate return-value propagation, optional callbacks, and API behavior for null file callbacks in `reg_parse_fd()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_parse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_parse_dox.cfg -->
# sources/user-network-fs/samba/source3/registry/reg_parse_dox.cfg

## Purpose
`reg_parse_dox.cfg` is the Doxygen configuration for the registry import/export parser and formatter documentation set.

## Important APIs, Types, And Functions
The config names the project `Registry Import / Export`, optimizes output for C, extracts all documented and static symbols, and includes the parser/formatter/import files plus related `net_registry`, `cbuf`, and `srprs` sources. It enables HTML and LaTeX output, warnings, todo/test/bug/deprecated lists, preprocessing, include graphs in settings, and source-file listings. It does not enable XML, RTF, man, or dot processing.

## Control Flow
Doxygen consumes this file when run with the local compile command `doxygen reg_parse_dox.cfg`. Input is non-recursive and explicitly listed, so newly related files are invisible until added. Output directories use defaults except HTML under `html` and LaTeX under `latex`.

## State And Persistence
The file persists documentation-generation settings, not runtime registry state. Generated documentation is build output and depends on the local Doxygen version and source tree.

## Dependencies And Integration Points
It integrates with Doxygen 1.6-era settings and references local source files by relative name. The footer has editor local variables and a compile command.

## Risks And Test Signals
Because `INPUT` is explicit and relative, running from the wrong directory or renaming files breaks documentation generation. `HAVE_DOT = NO` means graph-related options are mostly inert. Tests/signals are a successful Doxygen run with warnings reviewed, expected HTML/LaTeX outputs present, and confirmation that all import/export sources intended for docs are in `INPUT`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_parse_dox.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_parse_internal.c -->
# sources/user-network-fs/samba/source3/registry/reg_parse_internal.c

## Purpose
`reg_parse_internal.c` provides shared helpers for `.reg` parsing and formatting: charset conversion, hive-name metadata and parsing, option parsing, BOM detection/writing, and case-adjusted cbuf output.

## Important APIs, Types, And Functions
`iconvert_talloc()` wraps `smb_iconv()` with talloc allocation and growth. `HIVE_INFO_*` constants and `HIVE_INFO[]` describe short/long hive names and handles. `srprs_hive()` parses short or long hive names, and `hive_info()` resolves a name. `smbreg_get_charset()` maps `dos` and `unix` aliases to loadparm charsets. `set_iconv()` opens/replaces converters. `srprs_option()` parses comma-separated option strings. `srprs_bom()` and `write_bom()` handle BOMs. `cbuf_puts_case()` writes text and applies preserve/upper/lower/title casing.

## Control Flow
Conversion allocates or reuses a destination buffer, retries on `E2BIG`, null-terminates with two zero bytes, and frees on unrecoverable errors. Hive parsing first recognizes `HK...` prefixes, then distinguishes long `HKEY_...` names from short names. Option parsing extracts key/value pairs and advances across commas. BOM handling scans a small static table.

## State And Persistence
The file owns static hive metadata and BOM metadata. It does not persist registry state. `set_iconv()` mutates caller-owned converter handles and closes prior descriptors to avoid leaks.

## Dependencies And Integration Points
It depends on `reg_parse_internal.h`, `cbuf`, `srprs`, `registry.h`, Samba charset configuration, and iconv. It is used by both parser and formatter implementations.

## Risks And Test Signals
Tests should cover conversion growth, invalid byte sequences, closing/replacing converters, each hive short/long spelling, option strings with quotes and missing values, every BOM entry, and casing modes. `srprs_option()` calls `srprs_quoted_string(ptr, ...)` while otherwise using local `pos`, so quoted option parsing should be specifically tested for pointer advancement.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_parse_internal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_parse_internal.h -->
# sources/user-network-fs/samba/source3/registry/reg_parse_internal.h

## Purpose
`reg_parse_internal.h` declares shared private helpers for registry parser/formatter code and abstracts native iconv use when available.

## Important APIs, Types, And Functions
It conditionally maps `smb_iconv_t`, `smb_iconv`, `smb_iconv_open`, and `smb_iconv_close` to native iconv symbols. It declares `iconvert_talloc()`, `struct hive_info`, external hive constants, `HIVE_INFO[]`, `hive_info()`, `srprs_hive()`, `smbreg_get_charset()`, `set_iconv()`, `srprs_option()`, `write_bom()`, `srprs_bom()`, `enum fmt_case`, and `cbuf_puts_case()`.

## Control Flow
Consumers use these APIs to set up encoding conversion, parse options and hive names, emit or consume BOMs, and format text case while writing to `cbuf`.

## State And Persistence
The header declares static metadata exported by the implementation but contains no mutable state. Converter state is owned by callers through `smb_iconv_t` handles.

## Dependencies And Integration Points
It includes `includes.h` and `system/iconv.h` and forward-declares `struct cbuf`. It is intentionally private to the parser/formatter implementation family, not a general registry API.

## Risks And Test Signals
Conditional iconv macro behavior should be compile-tested with native and Samba iconv configurations. API tests should cover each declared helper through `reg_parse_internal.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_parse_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_parse_prs.c -->
# sources/user-network-fs/samba/source3/registry/reg_parse_prs.c

## Purpose
`reg_parse_prs.c` implements a small parse/marshalling buffer API used by registry performance-counter RPC-style data. It manages an expandable talloc-backed byte buffer, alignment, endian-aware integer serialization, and byte-array streaming.

## Important APIs, Types, And Functions
Public functions include `prs_init()`, `prs_mem_free()`, `prs_alloc_mem()`, `prs_get_mem_context()`, `prs_grow()`, `prs_data_p()`, `prs_data_size()`, `prs_offset()`, `prs_set_offset()`, `prs_copy_data_in()`, `prs_align()`, `prs_align_uint64()`, `prs_mem_get()`, `prs_switch_type()`, `prs_uint16()`, `prs_uint32()`, `prs_uint64()`, and `prs_uint8s()`. `prs_debug()` and `tab_depth()` support structured debug output.

## Control Flow
`prs_init()` establishes marshalling or unmarshalling mode and optionally allocates an initial buffer. Marshalling mode can grow dynamic buffers on demand; unmarshalling refuses to grow and treats overrun as failure. Primitive serializers call `prs_mem_get()`, read or write values according to mode and endian flag, debug-print, and advance `data_offset`. Alignment functions pad with zero bytes in marshalling mode.

## State And Persistence
`prs_struct` owns transient buffer state: mode, endian flag, alignment, ownership, current offset, buffer size, requested growth size, data pointer, and talloc context. It does not persist data beyond the caller-managed buffer.

## Dependencies And Integration Points
It depends on Samba includes, `reg_parse_prs.h`, and `rpc_dce.h` endian/alignment constants. `reg_perfcount.h` references this API for performance counter retrieval.

## Risks And Test Signals
Tests should cover marshalling growth from zero, fixed-buffer unmarshalling overrun, offset setting, 4- and 8-byte alignment, little and big endian integer paths, uint64 low/high order, byte arrays in char and hex debug modes, and cleanup of dynamic buffers. Overflow risks around `data_offset + extra_space` and buffer-size doubling deserve boundary tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_parse_prs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_parse_prs.h -->
# sources/user-network-fs/samba/source3/registry/reg_parse_prs.h

## Purpose
`reg_parse_prs.h` declares the parse/marshalling stream structure and helpers used by registry performance-counter code.

## Important APIs, Types, And Functions
It defines `prs_struct` with mode, endian, alignment, dynamic ownership, offset, buffer size, growth size, buffer pointer, and talloc context. It defines `MARSHALL`, `UNMARSHALL`, `MARSHALLING()`, `UNMARSHALLING()`, `RPC_PARSE_ALIGN`, and `prs_init_empty()`. It declares buffer lifecycle, growth, offset, alignment, memory, mode-switch, and primitive streaming functions.

## Control Flow
Callers initialize a `prs_struct`, stream primitive values or bytes in marshalling/unmarshalling mode, inspect output with `prs_data_p()` and offsets, then free dynamic buffer memory with `prs_mem_free()` when appropriate.

## State And Persistence
The structure is caller-owned transient state. Dynamic buffer ownership is explicit through `is_dynamic` and `mem_ctx`.

## Dependencies And Integration Points
The API is included by performance counter registry headers and code needing RPC-like binary packing.

## Risks And Test Signals
Compile tests should ensure macro mode checks work in both directions. Runtime tests should cover dynamic and non-dynamic buffers, endian fields, alignment, and lifetime rules for `prs_alloc_mem()` versus `prs_mem_free()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_parse_prs.h -->
