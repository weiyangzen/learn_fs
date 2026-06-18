# subset-b-008349 research

Grouped research for SELinux libsemanage source files under `sources/security-integrity/selinux/libsemanage/src`. Each section is bounded for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/fcontext_internal.h -->
# sources/security-integrity/selinux/libsemanage/src/fcontext_internal.h

Purpose: declares the internal file-context record hooks that connect the public `semanage_fcontext_*` APIs to libsemanage's generic database layer. It includes public fcontext local/policy headers, `sepol/policydb.h`, and the internal database/handle definitions.

Important APIs/types/functions: exports `SEMANAGE_FCONTEXT_RTABLE`, `fcontext_file_dbase_init`, `fcontext_file_dbase_release`, and `semanage_fcontext_validate_local`. The record table is implemented in `fcontext_record.c`; the file backend is implemented in `fcontexts_file.c`; local validation lives in `fcontexts_local.c`.

Control flow and integration: backend setup code calls `fcontext_file_dbase_init` to bind read-only/read-write file paths to the fcontext record table and file parser/printer. Commit validation can call `semanage_fcontext_validate_local` with a `sepol_policydb_t` to ensure locally configured contexts are policy-valid before flush.

State/persistence: this header owns no state; it defines the ABI between record, text-file, local, and policy database implementations. Risks are signature drift against implementation files and using the local validator without a loaded policydb. Test signals are compile coverage and fcontext modify/query/list/commit tests that exercise parser, record table, and validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/fcontext_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/fcontext_record.c -->
# sources/security-integrity/selinux/libsemanage/src/fcontext_record.c

Purpose: implements libsemanage's native file-context record object because file-context records are not simple direct aliases to a sepol record type. A record stores a matching expression, object type, and optional SELinux context.

Important APIs/types/functions: defines `struct semanage_fcontext` and `struct semanage_fcontext_key`; implements key create/extract/free, `semanage_fcontext_compare`, `semanage_fcontext_compare2`, creation, expression setters/getters, type setters/getters, `semanage_fcontext_get_type_str`, context setters/getters, clone/free, and `SEMANAGE_FCONTEXT_RTABLE`.

Control flow: key creation duplicates expression strings and records the object type. Comparisons sort by expression first and type second. `semanage_fcontext_create` initializes type to `SEMANAGE_FCONTEXT_ALL`; setters duplicate or clone owned data. `semanage_fcontext_clone` constructs a fresh record then deep-copies expression and context.

State/persistence: records are heap-owned; expression and context ownership is internal to the record after setters. Persistence is indirect through file/local/policy database tables. Dependencies include `debug.h`, `semanage_context_clone/free`, and the generic `record_table_t` contract.

Risks: NULL input is mostly not guarded, so callers must provide valid expressions and contexts. `set_con` clones the input context, so callers must still free their original. Tests should cover deep-copy behavior, key comparison order, `<<none>>` context handling through file parsing, and all object-type string mappings.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/fcontext_record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/fcontexts_file.c -->
# sources/security-integrity/selinux/libsemanage/src/fcontexts_file.c

Purpose: provides the text-file backend for file-context records. It translates between `file_contexts.local` style lines and `semanage_fcontext_t` records for `dbase_file`.

Important APIs/functions: `type_str` maps internal fcontext type constants to file-context tokens; `fcontext_print` emits expression, type token, and either a context string or `<<none>>`; `fcontext_parse` parses one non-comment record; `SEMANAGE_FCONTEXT_FILE_RTABLE` registers parser/printer; `fcontext_file_dbase_init/release` bind the backend to `SEMANAGE_FILE_DTABLE`.

Control flow: parsing skips blank/comment lines, fetches the regex expression, optionally recognizes an object type token (`-d`, `--`, etc.), treats an unrecognized second token as the context, converts context text with `semanage_context_from_string`, and requires trailing whitespace/end-of-line via `parse_assert_space`. Printing uses `semanage_context_to_string` only when a context exists.

State/persistence: persistence is the read-only/read-write file pair provided to `dbase_file_init`. The parser mutates a caller-created record. Dependencies are `parse_utils`, `database_file`, fcontext record APIs, and context conversion.

Risks: parser behavior intentionally allows omitted type by falling through to context processing; malformed spacing or invalid contexts abort the record. Tests should include each file type token, omitted type, `<<none>>`, comments/blank lines, invalid context diagnostics, and round-trip print/parse.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/fcontexts_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/fcontexts_local.c -->
# sources/security-integrity/selinux/libsemanage/src/fcontexts_local.c

Purpose: exposes local file-context modification APIs over the generic database layer. This is the write-side surface for local fcontext overrides.

Important APIs/functions: `semanage_fcontext_modify_local`, `del_local`, `query_local`, `exists_local`, `count_local`, `iterate_local`, `list_local`, plus `semanage_fcontext_validate_local`. The helper `validate_handler` checks each local context against a `sepol_policydb_t`.

Control flow: CRUD wrappers obtain `semanage_fcontext_dbase_local(handle)` and delegate to `dbase_*`. Validation iterates local records; if a record has a non-NULL context, it calls `sepol_context_check` against the policydb and reports the expression/type on failure.

State/persistence: local records persist through the local fcontext database configured in the handle. Validation does not write state; it is a pre-commit safety check.

Dependencies/integration: used by commit flows and by public fcontext APIs; relies on `handle.h` inline database selectors, `database.h`, and libsepol context validation. Risks include local records with NULL contexts being accepted and error reporting depending on successful context string conversion. Test signals include local modify/delete/query and commit rejection for invalid context types/users/roles.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/fcontexts_local.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/fcontexts_policy.c -->
# sources/security-integrity/selinux/libsemanage/src/fcontexts_policy.c

Purpose: provides read-only policy-view APIs for file contexts and generated home-directory file contexts.

Important APIs/functions: `semanage_fcontext_query`, `exists`, `count`, `iterate`, `list`, and `semanage_fcontext_list_homedirs`. All normal policy APIs delegate to `semanage_fcontext_dbase_policy(handle)`; homedir listing delegates to `semanage_fcontext_dbase_homedirs(handle)`.

Control flow: functions are thin database dispatchers with no parsing or validation logic. They rely on the handle having initialized policy fcontext databases during connection.

State/persistence: reads policy plus local merged view from the policy fcontext database, and reads generated homedir contexts from the separate homedir database slot. It does not modify persistent state.

Dependencies/integration: called by consumers such as `genhomedircon.c` to test home-directory path conflicts and by Python wrapper tests to list fcontexts. Risks are incorrect database slot selection and caller misuse before connection. Tests should list policy fcontexts, query by key, and verify `list_homedirs` sees generated homedir output when enabled.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/fcontexts_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/genhomedircon.c -->
# sources/security-integrity/selinux/libsemanage/src/genhomedircon.c

Purpose: generates the temporary `file_contexts.homedirs` file from SELinux user mappings, passwd/group data, existing fcontext policy, and a homedir template. It is a commit-time integration point between user/seuser records, fcontext queries, policydb context validation, and host account discovery.

Important types/functions: `genhomedircon_user_entry_t` captures login/user/home/level/prefix data; `genhomedircon_settings_t` carries paths, handle, policydb, and fallback user. Key helpers include `ignore_setup/free`, `get_shell_list`, `fcontext_matches`, `parse_uid_config`, `get_home_dirs`, template predicates, `replace_all`, `extract_context`, `check_line`, `write_contexts`, `setup_fallback_user`, `add_user`, `get_group_users`, `get_users`, `write_context_file`, and exported `semanage_genhomedircon`.

Control flow: `semanage_genhomedircon` builds settings, configures ignored directories, opens the temporary homedir fcontext output, then calls `write_context_file`. That function loads template subsets, writes a generated header, prepares a fallback default user, discovers home roots, writes fallback HOME_ROOT/HOME_DIR contexts per root, writes default username/user templates, then expands real users from seuser mappings. User expansion sorts seusers, resolves SELinux users, handles `%group` mappings, collects passwd entries, applies precedence for explicit user mappings, substitutes placeholders, rewrites context user/MLS/role, validates each generated context against the policydb, and emits only valid lines.

State/persistence: reads `/etc/default/useradd`, `/etc/libuser.conf`, `/etc/login.defs`, `/etc/shells`, passwd and group databases, the temporary homedir template, and fcontext policy. Writes only `semanage_path(SEMANAGE_TMP, SEMANAGE_STORE_FC_HOMEDIRS)`. Global ignored directory state is in `ignore_head` and is cleared before return.

Risks: host NSS data and config files make output environment-dependent; invalid UID config falls back with warnings; group mappings can conflict; template context extraction assumes final whitespace-delimited field is the context; memory cleanup paths are complex. Test signals should cover disabled passwd scanning, ignored dirs, UID fallback parsing, `%group` expansion, explicit user precedence, MLS-enabled context rewrite, invalid template contexts, and conflict detection against existing fcontexts.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/genhomedircon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/genhomedircon.h -->
# sources/security-integrity/selinux/libsemanage/src/genhomedircon.h

Purpose: declares the internal homedir file-context generation entry point used by libsemanage commit/build logic.

Important API: `semanage_genhomedircon(semanage_handle_t *sh, sepol_policydb_t *policydb, int usepasswd, char *ignoredirs)`. The include of `utilities.h` supplies shared utility/list declarations and indirectly the semanage handle context used by the implementation.

Control flow/integration: callers pass the active semanage handle, loaded policydb, whether passwd scanning should be used, and a semicolon-separated ignored directory list from configuration. The implementation writes generated contexts into the temporary store.

State/persistence: no state in the header. The implementation reads account/config files and writes `file_contexts.homedirs`. Risks are ABI mismatch with the implementation and passing a mutable `ignoredirs` string because the implementation tokenizes it with `strtok_r`. Test signals are compile coverage and commit paths that generate homedir contexts with and without passwd scanning.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/genhomedircon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/handle.c -->
# sources/security-integrity/selinux/libsemanage/src/handle.c

Purpose: implements the public handle lifecycle and connection/transaction controls for libsemanage. It creates handles, parses configuration, owns the libsepol handle, selects stores, and dispatches backend operations through `semanage_policy_table`.

Important APIs/functions: `semanage_set_root`, `semanage_root`, `semanage_handle_create_with_path`, `semanage_handle_create`, setters for rebuild/reload/checks/store behavior, `semanage_get_hll_compiler_path`, dontaudit/tunable/cache settings, default priority accessors, `semanage_select_store`, `semanage_set_store_root`, `semanage_is_managed`, `semanage_mls_enabled`, `semanage_connect`, `semanage_access_check`, `semanage_disconnect`, `semanage_handle_destroy`, `semanage_begin_transaction`, and `semanage_commit`.

Control flow: handle creation allocates zeroed state, parses config, creates a sepol handle, installs the message relay, sets defaults such as priority 400, reload behavior based on SELinux status, file-context checks enabled, and commit lock timeout. Connection currently supports direct stores and delegates to direct backend functions. Transactions require a connected handle; commit delegates to backend commit and clears transaction/module flags afterward.

State/persistence: handle state includes connection flags, transaction flags, module modification flag, policy options, config, sepol handle, backend function table, and database slots. `private_semanage_root` is process-global. Persistent policy changes occur through backend commit, not directly here.

Risks: several setters assert allocation success and cannot return allocation errors; unsupported connection types fail at runtime; global root is not thread-local. Test signals include create/destroy, direct connect/disconnect, transaction idempotence, priority validation, compiler path lowercasing, and commit rejection without a transaction.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/handle.h -->
# sources/security-integrity/selinux/libsemanage/src/handle.h

Purpose: defines the internal `struct semanage_handle`, database slot numbering, and inline selectors for local, policy, homedir, and active databases.

Important types/macros: `DBASE_COUNT` is 24. Slot macros distinguish local modifications (`DBASE_LOCAL_*`), policy plus local merged views (`DBASE_POLICY_*`), generated homedir fcontexts, and active booleans. The handle contains error callback fields, direct backend union, `sepolh`, parsed config, priority, connection/transaction flags, policy options, backend function table, and `dbase_config_t dbase[DBASE_COUNT]`.

Control flow/integration: nearly every local/policy API uses the inline selectors in this header to obtain the correct `dbase_config_t` before delegating to `dbase_*`. Backend connection initializes these slots; commit code flushes and merges selected slots.

State/persistence: this header defines the in-memory state graph that mediates persistent local store files, policydb views, and active kernel policy state. It does not allocate or free itself.

Risks: slot order is a hard internal contract; adding a database requires updating `DBASE_COUNT`, selectors, backend initialization, merge/flush lists, and tests. Test signals are broad integration tests for each object family and compile warnings that catch selector/slot mismatches.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/handle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibendport_internal.h -->
# sources/security-integrity/selinux/libsemanage/src/ibendport_internal.h

Purpose: declares internal hooks for InfiniBand end port records. It connects public ibendport APIs to record, file, local, and policydb backends.

Important APIs: `SEMANAGE_IBENDPORT_RTABLE`, `ibendport_file_dbase_init/release`, `ibendport_policydb_dbase_init/release`, `semanage_ibendport_validate_local`, and `semanage_ibendport_compare2_qsort`.

Control flow/integration: file-store initialization is used for local modifications; policydb initialization binds to the active/tmp kernel policy; local validation detects duplicate end-port entries; qsort comparator supports validation ordering.

State/persistence: no state in the header. Persistent state lives in local ibendport text stores and kernel policydb views. Risks are stale declarations versus implementation and missing validation invocation before commit. Test signals include compile coverage, duplicate ibdev/port rejection, and policydb query/list operations.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibendport_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibendport_record.c -->
# sources/security-integrity/selinux/libsemanage/src/ibendport_record.c

Purpose: wraps libsepol InfiniBand end-port record APIs in libsemanage names and record-table form.

Important APIs/functions: compare/compare2/qsort wrappers, key create/extract/free, ib device name get/set, port get/set, context get/set, create/clone/free, and `SEMANAGE_IBENDPORT_RTABLE`.

Control flow: every object operation delegates to the corresponding `sepol_ibendport_*` function, passing `handle->sepolh` where libsepol needs allocation/error context. The record table lets generic database code clone, compare, key, and free records without knowing ibendport internals.

State/persistence: the file owns no state beyond returned heap objects from libsepol. Persistence is provided by ibendport file and policydb backends. Dependencies include `sepol/ibendport_record.h`, `sepol/context_record.h`, `handle.h`, and `database.h`.

Risks: comments mention Pkey despite representing end ports, which can mislead maintainers. Validity checks for duplicate port entries happen in local validation, not setters. Tests should cover key construction, qsort ordering, device name allocation/free expectations, context set/get, and database CRUD using this record table.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibendport_record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibendports_file.c -->
# sources/security-integrity/selinux/libsemanage/src/ibendports_file.c

Purpose: implements text parsing and printing for `ibendportcon` local records.

Important functions: `ibendport_print`, `ibendport_parse`, `SEMANAGE_IBENDPORT_FILE_RTABLE`, `ibendport_file_dbase_init`, and release. The record format is `ibendportcon <ibdev> <port> <context>`.

Control flow: parsing requires the literal header, device name, integer port, and non-`<<none>>` context. It converts context text with `semanage_context_from_string`, sets fields on a caller-created record, and validates trailing parse state. Printing retrieves a newly allocated ibdev name string and context string, emits a single line, then frees both.

State/persistence: used by `dbase_file` for local ibendport stores. It mutates parse target records and writes to a supplied stream. Risks include rejecting `<<none>>`, integer parsing accepting only unsigned-looking values through `parse_fetch_int`, and cleanup correctness on partial parse failure. Tests should cover round-trip, bad headers, invalid contexts, missing fields, and duplicate detection in local validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibendports_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibendports_local.c -->
# sources/security-integrity/selinux/libsemanage/src/ibendports_local.c

Purpose: exposes local InfiniBand end-port CRUD APIs and enforces no duplicate `(ibdev_name, port)` records.

Important APIs/functions: local modify/delete/query/exists/count/iterate/list wrappers and `semanage_ibendport_validate_local`.

Control flow: CRUD delegates to `semanage_ibendport_dbase_local(handle)`. Validation lists local records, sorts them with `semanage_ibendport_compare2_qsort`, then scans neighboring records with matching device names. If two records share the same port, it reports an `already exists` error.

State/persistence: local records are persisted through the local ibendport database. Validation allocates name strings from libsepol getters and frees all listed records before returning.

Risks: memory cleanup depends on freeing transient strings each loop; only same-device duplicates are checked. If compare order changes, the neighbor scan assumption could break. Tests should cover empty list, unique ports on same device, same port on different devices, duplicate same device/port, and error paths from getter failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibendports_local.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibendports_policy.c -->
# sources/security-integrity/selinux/libsemanage/src/ibendports_policy.c

Purpose: provides policy-view read APIs for InfiniBand end-port records.

Important APIs: `semanage_ibendport_query`, `exists`, `count`, `iterate`, and `list`.

Control flow: each function selects `semanage_ibendport_dbase_policy(handle)` and calls the generic database operation. There is no parsing or validation logic here.

State/persistence: reads the active/tmp policydb-backed ibendport view initialized by `ibendports_policydb.c`. It does not modify persistent state.

Dependencies/integration: used by consumers of the public semanage ibendport policy API and by Python/binding tests where present. Risks are using before handle connection or missing backend initialization. Test signals are query/list/count against a policy containing ibendportcon rules.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibendports_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibendports_policydb.c -->
# sources/security-integrity/selinux/libsemanage/src/ibendports_policydb.c

Purpose: binds InfiniBand end-port records to the libsepol policydb backend.

Important APIs/functions: `SEMANAGE_IBENDPORT_POLICYDB_RTABLE`, `ibendport_policydb_dbase_init`, and `ibendport_policydb_dbase_release`. The policydb table maps modify/query/count/exists/iterate to `sepol_ibendport_*`.

Control flow: initialization calls `dbase_policydb_init` with active and temporary kernel policy paths, the ibendport record table, and the ibendport policydb operation table, then sets `dconfig->dtable` to `SEMANAGE_POLICYDB_DTABLE`.

State/persistence: reads from `SEMANAGE_ACTIVE/SEMANAGE_STORE_KERNEL` and writes/merges against `SEMANAGE_TMP/SEMANAGE_STORE_KERNEL` during transactions. Risks include path selection errors and lack of `.add`/`.set` entries, so callers must use supported modify semantics. Test signals include policydb initialization, list/count, and local merge through `semanage_base_merge_components`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibendports_policydb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibpkey_internal.h -->
# sources/security-integrity/selinux/libsemanage/src/ibpkey_internal.h

Purpose: declares internal hooks for InfiniBand partition key records.

Important APIs: `SEMANAGE_IBPKEY_RTABLE`, `ibpkey_file_dbase_init/release`, `ibpkey_policydb_dbase_init/release`, `semanage_ibpkey_validate_local`, and `semanage_ibpkey_compare2_qsort`.

Control flow/integration: local stores use the file backend; policy views use the policydb backend; commit validation uses the local validator to reject overlapping pkey ranges per subnet prefix.

State/persistence: no state. Persistent data lives in local ibpkey text files and policydb records. Risks are declaration drift and qsort comparator misuse. Tests should include parser/backend initialization, range overlap rejection, and policy query/list behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibpkey_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibpkey_record.c -->
# sources/security-integrity/selinux/libsemanage/src/ibpkey_record.c

Purpose: wraps libsepol InfiniBand P_Key record APIs for libsemanage and exposes them through `record_table_t`.

Important APIs/functions: compare/compare2/qsort, key create/extract/free, subnet prefix string and byte getters/setters, low/high getters, pkey/range setters, context getters/setters, create/clone/free, and `SEMANAGE_IBPKEY_RTABLE`.

Control flow: the implementation delegates directly to `sepol_ibpkey_*` with `handle->sepolh` when needed. The qsort comparator dereferences record pointers and uses libsepol ordering, which local validation relies on to detect neighboring overlaps.

State/persistence: object memory is owned by libsepol allocation routines. Persistence is through the file and policydb backends. Risks include callers setting invalid ranges; overlap semantics are enforced later in local validation. Test signals include single pkey and range setup, subnet prefix string/byte conversion, context assignment, and record table CRUD.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibpkey_record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibpkeys_file.c -->
# sources/security-integrity/selinux/libsemanage/src/ibpkeys_file.c

Purpose: implements parser/printer support for `ibpkeycon` local records.

Important functions: `ibpkey_print`, `ibpkey_parse`, `SEMANAGE_IBPKEY_FILE_RTABLE`, `ibpkey_file_dbase_init`, and release. Records are printed as `ibpkeycon <subnet_prefix> <pkey|low - high> <context>`.

Control flow: parsing requires header and subnet prefix, then parses either a single integer pkey or a hyphenated range with optional spaces around the hyphen. It rejects `<<none>>` contexts, sets the record range or pkey, and requires clean trailing parse state. Printing emits either a single pkey or range based on low/high equality.

State/persistence: used by `dbase_file` for local ibpkey stores. Dependencies are parse utilities, context conversion, and ibpkey record wrappers.

Risks: range bounds are not validated here for ordering or overlap; that is handled by libsepol setters and local validation. Tests should include compact and spaced ranges, single pkeys, invalid contexts, bad prefixes, malformed hyphens, and round-trip persistence.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibpkeys_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibpkeys_local.c -->
# sources/security-integrity/selinux/libsemanage/src/ibpkeys_local.c

Purpose: provides local InfiniBand P_Key CRUD APIs and validates that local ranges do not overlap for the same subnet prefix.

Important APIs/functions: local modify/delete/query/exists/count/iterate/list wrappers and `semanage_ibpkey_validate_local`.

Control flow: CRUD delegates to `semanage_ibpkey_dbase_local(handle)`. Validation lists and sorts local records, then for each record finds the next record with the same subnet prefix bytes. Because sort order is by subnet and lower bound, `low2 <= high` signals overlap.

State/persistence: local records persist in the local ibpkey database. Validation is read-only except for allocations during list/getter calls.

Risks: the function allocates subnet prefix strings but does not visibly initialize/free both string pointers in all loop paths, so leak/error-path tests are useful. Correctness depends on libsepol compare ordering. Tests should cover adjacent non-overlapping ranges, true overlap, different subnet prefixes, empty lists, and malformed local files.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibpkeys_local.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibpkeys_policy.c -->
# sources/security-integrity/selinux/libsemanage/src/ibpkeys_policy.c

Purpose: provides policy-view read APIs for InfiniBand P_Key records.

Important APIs: `semanage_ibpkey_query`, `exists`, `count`, `iterate`, and `list`.

Control flow: each function retrieves `semanage_ibpkey_dbase_policy(handle)` and delegates to the generic database operation.

State/persistence: reads from the policydb-backed ibpkey database initialized for the handle. It does not mutate stores.

Dependencies/integration: public libsemanage APIs and any bindings use this layer to inspect policy P_Key contexts. Risks are missing handle connection or backend setup. Test signals include list/count/query with policy records and behavior on absent keys.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibpkeys_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibpkeys_policydb.c -->
# sources/security-integrity/selinux/libsemanage/src/ibpkeys_policydb.c

Purpose: binds ibpkey records to libsepol policydb operations.

Important APIs/functions: `SEMANAGE_IBPKEY_POLICYDB_RTABLE`, `ibpkey_policydb_dbase_init`, and `ibpkey_policydb_dbase_release`. The table maps modify/query/count/exists/iterate to `sepol_ibpkey_*`.

Control flow: initialization calls `dbase_policydb_init` with active/tmp kernel policy paths, `SEMANAGE_IBPKEY_RTABLE`, and the policydb operation table, then sets `SEMANAGE_POLICYDB_DTABLE`.

State/persistence: participates in policydb transaction state, reading active policy and writing/modifying the tmp policy during merges. Risks are unsupported add/set table entries and path misconfiguration. Tests should cover backend init/release and local ibpkey merge into policydb during commit.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ibpkeys_policydb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/iface_internal.h -->
# sources/security-integrity/selinux/libsemanage/src/iface_internal.h

Purpose: declares internal network interface record hooks.

Important APIs: `SEMANAGE_IFACE_RTABLE`, `iface_policydb_dbase_init/release`, `iface_file_dbase_init/release`.

Control flow/integration: the file backend parses local `netifcon` records; the policydb backend exposes policy records; local and policy wrappers use the record table for generic database operations.

State/persistence: no state. Persistent data lives in local interface text stores and policydb records. Risks are missing a local validation hook compared with ports/ibpkeys; context validity is mainly enforced by parsing/policydb checks. Test signals include file parser round-trip and policy/local CRUD.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/iface_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/iface_record.c -->
# sources/security-integrity/selinux/libsemanage/src/iface_record.c

Purpose: wraps libsepol network-interface record APIs for libsemanage.

Important APIs/functions: compare/compare2/qsort, key create/extract/free, name get/set, interface context get/set, message context get/set, create/clone/free, and `SEMANAGE_IFACE_RTABLE`.

Control flow: operations are mostly direct calls to `sepol_iface_*`; the record table allows generic database code to clone, compare, key, and free interface records.

State/persistence: record allocation and owned strings/contexts are managed by libsepol. Persistence is through `interfaces_file.c` and `interfaces_policydb.c`.

Risks: qsort comparator is static because no local overlap validation uses it outside the record table. Callers must set both ifcon and msgcon before printing/persisting. Tests should cover name keying, context setters, clone/free, and parser behavior when one context is missing or invalid.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/iface_record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/interfaces_file.c -->
# sources/security-integrity/selinux/libsemanage/src/interfaces_file.c

Purpose: text backend for local network-interface `netifcon` records.

Important functions: `iface_print`, `iface_parse`, `SEMANAGE_IFACE_FILE_RTABLE`, `iface_file_dbase_init`, and release. Format is `netifcon <name> <ifcon> <msgcon>`.

Control flow: parser verifies the header, reads interface name, parses and rejects NULL/`<<none>>` interface and message contexts, sets both contexts, and requires valid trailing parse state. Printer converts both contexts to strings and emits one line.

State/persistence: local interface state is read/written through `dbase_file`. Dependencies include parse utilities, context conversion, interface record wrappers, and `database_file`.

Risks: both contexts are mandatory; partial setter failure must free the temporary context. Tests should cover valid round-trip, invalid header, missing message context, `<<none>>`, invalid context string, and whitespace/comment handling.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/interfaces_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/interfaces_local.c -->
# sources/security-integrity/selinux/libsemanage/src/interfaces_local.c

Purpose: local network-interface CRUD wrappers over the handle's local interface database.

Important APIs: `semanage_iface_modify_local`, `del_local`, `query_local`, `exists_local`, `count_local`, `iterate_local`, and `list_local`.

Control flow: every function selects `semanage_iface_dbase_local(handle)` and delegates to the corresponding `dbase_*` routine. No local duplicate or context validation is performed in this file.

State/persistence: modifies or reads local interface records that are later flushed by commit component logic. Dependencies are `iface_internal.h`, `handle.h`, and `database.h`.

Risks: correctness relies on generic database key uniqueness and parser/context checks elsewhere. Test signals include write/restore cycles in wrapper tests, local query/list/count, and commit flush of interface changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/interfaces_local.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/interfaces_policy.c -->
# sources/security-integrity/selinux/libsemanage/src/interfaces_policy.c

Purpose: policy-view read APIs for network-interface records.

Important APIs: `semanage_iface_query`, `exists`, `count`, `iterate`, and `list`.

Control flow: thin wrappers select `semanage_iface_dbase_policy(handle)` and delegate to generic database methods.

State/persistence: reads policydb-backed interface data and does not modify stores. Dependencies are the handle database selector and the initialized policydb backend.

Risks: no local error handling beyond generic database return codes. Test signals include listing interfaces through C and Python bindings, querying absent/present keys, and count consistency with iteration.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/interfaces_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/interfaces_policydb.c -->
# sources/security-integrity/selinux/libsemanage/src/interfaces_policydb.c

Purpose: connects interface records to libsepol policydb operations.

Important APIs/functions: `SEMANAGE_IFACE_POLICYDB_RTABLE`, `iface_policydb_dbase_init`, and `iface_policydb_dbase_release`. It maps modify/query/count/exists/iterate to `sepol_iface_*`.

Control flow: initialization passes active and temporary kernel policy paths to `dbase_policydb_init` along with interface record and policydb operation tables, then sets the database table to `SEMANAGE_POLICYDB_DTABLE`.

State/persistence: policydb transaction state is handled by the generic policydb backend. Risks include typo-level comments only, unsupported add/set operations, and dependency on correct semanage store paths. Tests should initialize/release the backend and merge local interface modifications into tmp policydb.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/interfaces_policydb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/libsemanage.pc.in -->
# sources/security-integrity/selinux/libsemanage/src/libsemanage.pc.in

Purpose: pkg-config template for consumers linking against libsemanage.

Important fields: defines `prefix`, `exec_prefix`, `libdir`, `includedir`, `Name`, `Description`, `Version`, project `URL`, `Requires.private` on `libselinux libsepol`, public `Libs: -L${libdir} -lsemanage`, private libraries `-laudit -lbz2`, and public include flags.

Control flow/build integration: configure/build tooling substitutes `@prefix@`, `@libdir@`, `@includedir@`, and `@VERSION@` to produce `libsemanage.pc`. Build systems use it for compiler/linker discovery.

State/persistence: no runtime state. The file affects installed metadata and downstream builds. Risks include missing private dependencies for static linking or incorrect substitution paths. Test signals are `pkg-config --cflags --libs libsemanage`, static link checks requiring private libs, and installed version consistency.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/libsemanage.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/modules.c -->
# sources/security-integrity/selinux/libsemanage/src/modules.c

Purpose: implements public module-management APIs, module info/key object helpers, module path construction, validation, and checksum computation.

Important APIs/functions: install/install_file/extract/remove/list wrappers, legacy upgrade compatibility, `semanage_module_info_*`, `semanage_module_key_*`, `semanage_module_get_path`, `semanage_module_get_enabled`, `set_enabled`, `semanage_string_to_priority`, validators for priority/name/enabled/lang extension, module info/list-all/install-info/remove-key APIs, `semanage_hash_to_checksum_string`, and `semanage_module_compute_checksum`.

Control flow: mutating module APIs require a connected handle and open a transaction automatically if needed, then set `sh->modules_modified` before delegating to the backend function table. Info/key setters validate inputs and duplicate owned strings. Path generation chooses active versus tmp module roots based on `sh->is_in_transaction` and composes priority/name/hll/cil/lang_ext/disabled paths. Checksum computation extracts module data, hashes it with SHA-256, and unmaps extracted data.

State/persistence: persistent module state lives in the semanage module store and is mutated by backend functions. This file owns heap strings in module info/key structs and updates handle transaction/module flags.

Risks: callers must destroy/free created structs correctly; validation regexes are hand-coded; automatic transaction start changes handle state; checksum assumes extracted data is mmap-backed and uses `munmap`. Tests should cover validators, path truncation, transaction auto-start, backend dispatch failure when disconnected, clone/destroy ownership, checksum length query, and install/remove/list flows.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/modules.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/modules.h -->
# sources/security-integrity/selinux/libsemanage/src/modules.h

Purpose: internal module-management declarations shared by handle, policy, direct backend, and module implementation code.

Important types/APIs: `struct semanage_module_info` with priority/name/lang_ext/enabled; `struct semanage_module_key` with priority/name; init/clone/validation helpers; `semanage_string_to_priority`; module path type enum for priority/name/hll/cil/lang_ext/disabled; `semanage_module_get_path`; checksum constants and `semanage_hash_to_checksum_string`; legacy upgrade/install-base declarations.

Control flow/integration: backend-independent code uses these structs as module identifiers and metadata. Direct store code uses the path enum to derive on-disk module layout paths.

State/persistence: the structs own heap strings but this header only declares layout and functions. Risks include ABI/layout changes and path enum mismatch with `modules.c`. Test signals are compile coverage, public module API tests, and path generation for all enum values.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/modules.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/node_internal.h -->
# sources/security-integrity/selinux/libsemanage/src/node_internal.h

Purpose: declares internal network-node record hooks.

Important APIs: `SEMANAGE_NODE_RTABLE`, `node_file_dbase_init/release`, `node_policydb_dbase_init/release`, `semanage_node_validate_local`, and `semanage_node_compare2_qsort`.

Control flow/integration: local stores use the file backend; policy views use the policydb backend; qsort comparator supports sorted node handling, especially during merge or validation paths.

State/persistence: no state in the header. Persistent data is in local node text stores and policydb. Risks include a declared `semanage_node_validate_local` without an implementation in the listed `nodes_local.c`, which should be checked elsewhere in the tree or build. Test signals include compile/link coverage and node parser/policydb CRUD.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/node_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/node_record.c -->
# sources/security-integrity/selinux/libsemanage/src/node_record.c

Purpose: wraps libsepol network node record APIs for libsemanage.

Important APIs/functions: compare/compare2/qsort, key create/extract/free, address and mask get/set in string and byte forms, protocol get/set/string, context get/set, create/clone/free, and `SEMANAGE_NODE_RTABLE`.

Control flow: methods delegate to `sepol_node_*`, passing the semanage handle's sepol handle where required. Protocol string mapping is delegated to libsepol. The record table is consumed by generic file and policydb databases.

State/persistence: node objects are allocated/freed by libsepol wrappers. Persistence is through `nodes_file.c` and `nodes_policydb.c`.

Risks: address/mask setters require matching protocol semantics; parse code must set protocol before address/mask. Tests should cover IPv4 and IPv6 addresses/masks, byte getters, key extraction, clone/free, and sorting behavior used by merge operations.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/node_record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/nodes_file.c -->
# sources/security-integrity/selinux/libsemanage/src/nodes_file.c

Purpose: text backend for local `nodecon` records.

Important functions: `node_print`, `node_parse`, `SEMANAGE_NODE_FILE_RTABLE`, `node_file_dbase_init`, and release. Format is `nodecon <ipv4|ipv6> <addr> <mask> <context>`.

Control flow: parser verifies header, maps protocol string to `SEMANAGE_PROTO_IP4/IP6`, sets protocol, parses address and mask using protocol-aware setters, parses a non-NULL context, and requires clean trailing parse state. Printer retrieves address and mask strings, converts context to string, and emits one line.

State/persistence: used by `dbase_file` for local node stores. Dependencies include parse utilities, node record wrappers, context conversion, and database file backend.

Risks: invalid protocol/address/mask/context aborts the record; `<<none>>` is rejected. Tests should cover IPv4, IPv6, invalid protocol, invalid netmask for protocol, missing context, comments/blank lines, and round-trip serialization.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/nodes_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/nodes_local.c -->
# sources/security-integrity/selinux/libsemanage/src/nodes_local.c

Purpose: local network-node CRUD wrappers over the handle's local node database.

Important APIs: `semanage_node_modify_local`, `del_local`, `query_local`, `exists_local`, `count_local`, `iterate_local`, and `list_local`.

Control flow: each function selects `semanage_node_dbase_local(handle)` and delegates to generic database operations. There is no overlap or context validator in this file.

State/persistence: local node records are modified/read and later flushed by commit components. Integration is with `policy_components.c`, which sorts node local records before merging into policy.

Risks: any declared local validation must be implemented elsewhere or not linked; this file itself performs no validation beyond generic database semantics. Test signals include local modify/query/delete/list and commit merge ordering for node records.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/nodes_local.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/nodes_policy.c -->
# sources/security-integrity/selinux/libsemanage/src/nodes_policy.c

Purpose: policy-view read APIs for network node records.

Important APIs: `semanage_node_query`, `exists`, `count`, `iterate`, and `list`.

Control flow: thin wrappers select `semanage_node_dbase_policy(handle)` and call generic database routines.

State/persistence: reads policydb-backed node data. It does not mutate stores.

Dependencies/integration: public semanage node APIs and Python tests use this layer to inspect node contexts. Risks are use before connection and absent policydb backend setup. Test signals include list/query/count on IPv4 and IPv6 nodecon policies.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/nodes_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/nodes_policydb.c -->
# sources/security-integrity/selinux/libsemanage/src/nodes_policydb.c

Purpose: connects node records to libsepol policydb operations.

Important APIs/functions: `SEMANAGE_NODE_POLICYDB_RTABLE`, `node_policydb_dbase_init`, and release. The table maps modify/query/count/exists/iterate to `sepol_node_*`.

Control flow: initialization supplies active/tmp kernel policy paths, the node record table, and policydb operation table to `dbase_policydb_init`, then sets `SEMANAGE_POLICYDB_DTABLE`.

State/persistence: participates in active/tmp policydb transaction handling. Risks include unsupported add/set operations and dependence on correct semanage store path setup. Tests should cover init/release, policy list/count, and local node merge with sorted ordering.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/nodes_policydb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/parse_utils.c -->
# sources/security-integrity/selinux/libsemanage/src/parse_utils.c

Purpose: shared line-oriented parsing utilities for libsemanage text database backends.

Important APIs/functions: `parse_init`, `parse_release`, `parse_open`, `parse_close`, `parse_dispose_line`, `parse_skip_space`, `parse_assert_noeof`, `parse_assert_space`, `parse_assert_ch`, `parse_assert_str`, `parse_optional_ch`, `parse_optional_str`, `parse_fetch_int`, and `parse_fetch_string`.

Control flow: `parse_skip_space` advances within the current line, disposes exhausted lines, reads new lines with `getline`, strips newline, skips leading whitespace/comments/blanks, and stores both working and original copies. Assertions report filename/line/original text. Fetch helpers extract non-empty strings or decimal integers up to delimiters/whitespace.

State/persistence: `parse_info_t` owns the current line buffers and input stream pointer. `parse_open` treats missing files as success with no stream, enabling absent optional local stores. It uses `fopen(..., "re")` and `__fsetlocking(..., FSETLOCKING_BYCALLER)`.

Risks: parser is not thread-safe per `FILE` without external locking; `parse_optional_str` assumes `info->ptr` is non-NULL; negative integers are rejected by initial digit check. Tests should cover comments, blank files, EOF, missing files, delimiters, trailing whitespace, malformed ints, and diagnostic line numbers.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/parse_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/parse_utils.h -->
# sources/security-integrity/selinux/libsemanage/src/parse_utils.h

Purpose: declares the shared parsing state and helper APIs used by file-backed record parsers.

Important types/APIs: `parse_info_t` stores line number, original/working line buffers, current pointer, filename, file stream, and caller parse argument. It declares lifecycle, stream, whitespace/comment skipping, assertion, optional token, integer, and string fetch helpers.

Control flow/integration: `*_file.c` parsers receive a `parse_info_t`, call `parse_skip_space`, then consume tokens using this API. `parse_arg` allows backend-specific auxiliary state, although these files mostly do not use it.

State/persistence: no persistent state beyond parser fields. Risks include the typo in the declaration parameter name `hgandle`, which is harmless but can confuse readers, and callers needing to respect ownership of fetched strings. Test signals are compile coverage and parser tests for all database text formats.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/parse_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/policy.h -->
# sources/security-integrity/selinux/libsemanage/src/policy.h

Purpose: defines the backend dispatch table for policy/store operations and declares backend-independent component merge/commit functions.

Important types/APIs: `struct semanage_policy_table` contains function pointers for serial, destroy, disconnect, begin transaction, commit, module install/install_file/extract/remove/list, enabled status, module info/list-all/install-info/remove-key. It also declares `semanage_base_merge_components` and `semanage_commit_components`.

Control flow/integration: `handle.c` and `modules.c` call these function pointers after connection selects a backend, currently direct store. Backend implementations populate the table to simulate polymorphism in C.

State/persistence: no state in the header, but function pointers mediate all persistent policy/module operations. Risks include NULL function pointers for unsupported operations and ABI changes when adding backend capabilities. Test signals are backend connection tests, module operation dispatch, and commit/transaction flows.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/policy_components.c -->
# sources/security-integrity/selinux/libsemanage/src/policy_components.c

Purpose: merges local component databases into the policy database and flushes component databases during commit.

Important functions: `clear_obsolete`, `load_records`, `semanage_base_merge_components`, and `semanage_commit_components`. Mode flags are `MODE_SET`, `MODE_MODIFY`, and `MODE_SORT`.

Control flow: base merge iterates an ordered component table: users, ports, interfaces, booleans, seusers, nodes, ibpkeys, and ibendports. It caches source/destination databases, lists local records, optionally sorts records, clears obsolete destination entries for set-style booleans, then loads each record via set or modify. Commit components flushes local/policy/active database slots in a fixed order and drops caches on failure.

State/persistence: merge mutates the temporary policydb view; commit flushes local and active stores. Ordering matters because records can have policy dependencies. Dependencies include handle database selectors, generic database tables, module definitions, and debug logging.

Risks: the component arrays are hard-coded and must be updated when new database slots are added. Error paths rely on table-specific key/free semantics. Tests should cover local boolean obsolete clearing, sorted node merge, port/ibpkey overlap validation before merge, flush failure cache dropping, and commit with each component family.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/policy_components.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/port_internal.h -->
# sources/security-integrity/selinux/libsemanage/src/port_internal.h

Purpose: declares internal network-port record hooks.

Important APIs: `SEMANAGE_PORT_RTABLE`, `port_file_dbase_init/release`, `port_policydb_dbase_init/release`, `semanage_port_validate_local`, and `semanage_port_compare2_qsort`.

Control flow/integration: file backend parses local `portcon` records; policydb backend binds to libsepol; local validator uses qsort comparator to reject overlaps before merge.

State/persistence: no state. Persistent records live in local port text stores and policydb. Risks are declaration drift and missing validation invocation. Test signals include parser round-trip, overlap validation, and policydb list/query.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/port_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/port_record.c -->
# sources/security-integrity/selinux/libsemanage/src/port_record.c

Purpose: wraps libsepol network port record APIs for libsemanage and generic database use.

Important APIs/functions: compare/compare2/qsort, key create/extract/free, protocol get/set/string, low/high getters, single port and range setters, context get/set, create/clone/free, and `SEMANAGE_PORT_RTABLE`.

Control flow: all operations delegate to `sepol_port_*`. The qsort comparator is exported for local overlap validation. The record table is consumed by file and policydb database layers.

State/persistence: object state is held in libsepol port records. Persistence is through local file and policydb backends.

Risks: setters do not by themselves prevent overlapping ranges; local validation must run. Tests should cover protocol values tcp/udp/dccp/sctp, single and ranged ports, context assignment, key extraction, and sort ordering.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/port_record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ports_file.c -->
# sources/security-integrity/selinux/libsemanage/src/ports_file.c

Purpose: text backend for local `portcon` records.

Important functions: `port_print`, `port_parse`, `SEMANAGE_PORT_FILE_RTABLE`, `port_file_dbase_init`, and release. Format is `portcon <tcp|udp|dccp|sctp> <port|low - high> <context>`.

Control flow: parser validates header and protocol, parses a single port or hyphenated range with special spacing rules, rejects `<<none>>` contexts, sets context, and requires valid trailing parse state. Printer emits the protocol string, single/range numeric field, and context string.

State/persistence: used by `dbase_file` for local port stores. Dependencies include parse utilities, port record wrappers, context conversion, and database file backend.

Risks: overlap is not checked here; malformed spacing around ranges can change parse outcome; negative ports are rejected by integer parsing. Tests should cover all protocols, single/range forms, invalid context, invalid protocol, malformed ranges, comments/blanks, and round-trip output.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ports_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ports_local.c -->
# sources/security-integrity/selinux/libsemanage/src/ports_local.c

Purpose: local port CRUD wrappers and range-overlap validator.

Important APIs/functions: local modify/delete/query/exists/count/iterate/list wrappers and `semanage_port_validate_local`.

Control flow: CRUD delegates to `semanage_port_dbase_local(handle)`. Validation lists local ports, sorts them with `semanage_port_compare2_qsort`, then scans for the next record with matching protocol. If the next low bound is less than or equal to the current high bound, an overlap error is reported.

State/persistence: local port records persist through the local port database and are flushed during commit. Validation reads and frees listed records.

Risks: assumes sort order groups protocol and ascending low bound; only nearest same-protocol neighbor is checked based on that invariant. Tests should include overlapping same-protocol ranges, adjacent non-overlap, different protocols, empty/singleton lists, and commit rejection behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ports_local.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ports_policy.c -->
# sources/security-integrity/selinux/libsemanage/src/ports_policy.c

Purpose: policy-view read APIs for network port records.

Important APIs: `semanage_port_query`, `exists`, `count`, `iterate`, and `list`.

Control flow: each function selects `semanage_port_dbase_policy(handle)` and delegates to generic database operations.

State/persistence: reads policydb-backed port data only. Dependencies are handle database selectors and initialized policydb backend.

Risks: no extra validation or transformation is performed, so correctness is in the record/policydb layers. Test signals include list/query/count with tcp/udp/dccp/sctp policy records and absent-key behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ports_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ports_policydb.c -->
# sources/security-integrity/selinux/libsemanage/src/ports_policydb.c

Purpose: binds port records to libsepol policydb operations.

Important APIs/functions: `SEMANAGE_PORT_POLICYDB_RTABLE`, `port_policydb_dbase_init`, and release. The table maps modify/query/count/exists/iterate to `sepol_port_*`.

Control flow: initialization calls `dbase_policydb_init` with active/tmp kernel policy paths, `SEMANAGE_PORT_RTABLE`, and policydb operation table, then sets `SEMANAGE_POLICYDB_DTABLE`.

State/persistence: reads active policy and modifies temporary policy during transaction merge. Risks include unsupported add/set operations and dependence on correct store path initialization. Tests should cover backend init/release, policy list/count, and local port merge after validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/ports_policydb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/pywrap-test.py -->
# sources/security-integrity/selinux/libsemanage/src/pywrap-test.py

Purpose: manual/smoke test driver for the Python semanage bindings. It can list and optionally modify modules, users, seusers, ports, fcontexts, interfaces, booleans, active booleans, and nodes.

Important types/functions: custom `Usage`, `Status`, and `Error` exceptions; `Tests` selection state; read tests such as `test_modules`, `test_users`, `test_ports`, `test_fcontexts`, `test_interfaces`, `test_booleans`, `test_abooleans`, `test_nodes`; write tests for user/seuser/port/fcontext/interface/boolean/active boolean/node; and `main` option parsing/handle lifecycle.

Control flow: `main` parses short and long options, creates a semanage handle, checks managed status, connects, dispatches selected tests, disconnects, and destroys the handle. Read tests list records and print selected fields. Write tests create a record, save an existing local value if present, begin a transaction, modify and commit, begin a second transaction, then delete or restore the old value and commit again.

State/persistence: read tests inspect policy/local/active state. Write tests intentionally mutate the semanage store and active boolean state, then try to restore. Dependencies are the generated `semanage` Python module and a managed SELinux system.

Risks: script returns `2` even after successful execution because `main` always returns 2; write tests can affect real policy if restore fails; option string and long option names are uneven. Test signals are primarily manual binding coverage, not hermetic CI. Safer tests should run in an isolated store/root.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/pywrap-test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/semanage.conf -->
# sources/security-integrity/selinux/libsemanage/src/semanage.conf

Purpose: sample/default libsemanage configuration file controlling policy store connection and policy generation settings.

Important settings: `module-store = direct` is active. Comments document source/direct/socket/TCP store modes. `policy-version` and `target-platform` are shown as optional commented settings.

Control flow/integration: `semanage_conf_parse` reads this style of file during handle creation. The resulting `semanage_conf_t` controls direct backend selection, policy version, target platform, and many additional settings declared in `semanage_conf.h`.

State/persistence: configuration is read at runtime and influences where/how libsemanage connects and commits. This file does not write state.

Risks: comments mention connection types not implemented by `handle.c` in this source subset; misconfiguration can make `semanage_connect` fail. Test signals include parsing default config, direct connection setup, and overrides for policy version/target platform in config parser tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/semanage.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/semanage_conf.h -->
# sources/security-integrity/selinux/libsemanage/src/semanage_conf.h

Purpose: declares the parsed libsemanage configuration structure and parser/destructor APIs.

Important types/APIs: `semanage_conf_t` holds store type/path/root, compiler directory, server port, policy version, target platform, booleans for expansion/save/cache/relabel behavior, unknown handling, file mode, bzip settings, ignored directories for genhomedircon, external program lists, and module output program paths. `external_prog_t` is a linked list of path/args commands. APIs are `semanage_conf_parse` and `semanage_conf_destroy`.

Control flow/integration: handle creation parses this config and later code reads fields for direct store selection, compiler path construction, genhomedircon behavior, setfiles/sefcontext_compile invocations, and module cache policy.

State/persistence: the parsed config is heap-owned by `semanage_handle_t` and destroyed with the handle. Risks include ownership of many string fields and linked lists, defaults when options are absent, and keeping struct fields synchronized with parser and sample config. Test signals include parser default values, destroy leak checks, ignoredirs propagation, and external program list parsing.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/semanage_conf.h -->
