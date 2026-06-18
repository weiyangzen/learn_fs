# subset-b-008348 Research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/example/test_fcontext.c -->

# sources/security-integrity/selinux/libsemanage/example/test_fcontext.c

Purpose: provides a small example program that creates a local file-context mapping through the libsemanage public API. It demonstrates handle creation, access checking, connection, fcontext key construction, existence checking, record creation, context parsing, and local modification.

Important APIs/types/functions: uses `semanage_handle_create`, `semanage_access_check`, `semanage_connect`, `semanage_fcontext_key_create`, `semanage_fcontext_exists`, `semanage_fcontext_create`, `semanage_context_from_string`, `semanage_fcontext_set_con`, `semanage_fcontext_set_type`, and `semanage_fcontext_modify_local`.

Control flow: `main` expects a context string in `argv[1]` and a path expression in `argv[2]`, connects to semanage, rejects an already-existing regular-file mapping, builds a new fcontext record, assigns the parsed context, and stores it in the local database.

State and persistence behavior: it writes only the local fcontext customization cache; there is no explicit `semanage_begin_transaction` or `semanage_commit`, so as an example it is incomplete for durable installation on many backends. It frees the fcontext key and record on the success path but leaks the handle and context.

Dependencies and integration points: includes public libsemanage headers and `sepol/sepol.h`. It is useful as an API smoke example for file-context operations and mirrors command-line `semanage fcontext -a` behavior at a low level.

Risks: no `argc` validation before indexing `argv[1]`/`argv[2]`, incomplete cleanup on most error paths, no disconnect/destroy, no commit, and hard-coded regular-file type. Test signals are successful duplicate detection, context-string parsing failures, local fcontext query after commit when completed, and sanitizer warnings for argument misuse or leaks.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/example/test_fcontext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/Makefile -->

# sources/security-integrity/selinux/libsemanage/include/Makefile

Purpose: installs libsemanage public headers into the configured include tree. It is intentionally minimal because header generation and compilation happen in `src/Makefile`.

Important APIs/targets: variables are `PREFIX` and `INCDIR`, defaulting to `/usr` and `$(PREFIX)/include/semanage`. The `install` target creates `$(DESTDIR)$(INCDIR)` and installs every `semanage/*.h` file mode `0644`. `all` is a no-op.

Control flow: a packaging build descends into this directory, invokes `make install`, creates the include directory if needed, and copies the header set with `install`.

State and persistence behavior: writes only installed header files under `DESTDIR`; it does not generate headers or track dependency timestamps beyond make's target execution.

Dependencies and integration points: used by top-level SELinux userspace packaging and depends on the public header directory layout. It must stay aligned with `src/libsemanage.pc.in` include paths and the umbrella `semanage.h` header.

Risks: `$(wildcard semanage/*.h)` silently omits missing headers and includes any accidental header added in that folder. Test signals are staged installs verifying the complete public ABI header set and correct destination paths.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/boolean_record.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/boolean_record.h

Purpose: defines the public opaque record API for a policy boolean record. It separates key construction/comparison from mutable record fields so the same object model can be used by local files, policydb views, joins, and language bindings.

Important APIs/types/functions: declares the opaque record type `semanage_bool_t`, its key type, key create/extract/free helpers, `compare`/`compare2`, field getters and setters, and create/clone/free routines. The main identity is `semanage_bool_key_t` keyed by boolean name; booleans carry a name and enabled/disabled integer value.

Control flow: clients allocate a record with the create API, fill fields with setters, derive or create a key, then pass both to local modify/set/query APIs. Query and list APIs return records that follow the same free routine. Clone APIs deep-copy nested strings, arrays, and contexts where applicable.

State and persistence behavior: the header itself has no persistence, but setter ownership rules define what later database backends will persist. Setters take a `semanage_handle_t` for allocation, validation, message reporting, and libsepol interop.

Dependencies and integration points: used by object-specific local/policy headers, generic database method tables, direct commit validators, `semanage.h`, man pages, and SWIG wrapping. Context-bearing records integrate with `context_record.h`.

Risks: callers must not free borrowed getter strings or nested context pointers unless the API documents ownership through an output allocation. Range/protocol/type constants must stay ABI-stable. Test signals include key equality ordering, clone independence, setter validation, round-trip parse/print, and correct cleanup on allocation failure.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/boolean_record.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/booleans_active.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/booleans_active.h

Purpose: declares access to active kernel boolean state, which is distinct from local default boolean customizations and policydb boolean declarations.

Important APIs/types/functions: exports `semanage_bool_set_active`, `query_active`, `exists_active`, `count_active`, `iterate_active`, and `list_active` over `semanage_bool_key_t` and `semanage_bool_t`. `set_active` changes the live value; the remaining functions inspect active booleans.

Control flow: callers connect a handle, construct a boolean key, and read or update active state. Implementations route through an active-database backend that reads SELinux active boolean names and commits a complete boolean list back to libselinux.

State and persistence behavior: active boolean updates target the running system state and are not the same as persistent local policy defaults. The active database caches a list during operations and writes values through the active backend when flushed.

Dependencies and integration points: depends on the boolean record API and the handle abstraction; integrates with `booleans_active.c`, `booleans_activedb.c`, libselinux active boolean calls, and tools that need immediate boolean toggles.

Risks: callers can confuse active values with persistent local values. Complete-list commits must preserve unrelated booleans. Test signals include live boolean query/set behavior, count/list parity with SELinux active state, and no persistence unless corresponding local defaults are also modified.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/booleans_active.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/booleans_local.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/booleans_local.h

Purpose: declares the local-store CRUD surface for `policy boolean` records. These functions operate on administrator overrides in the writable semanage store rather than directly exposing the compiled policy view.

Important APIs/types/functions: exports `semanage_bool_modify_local`, `del_local`, `query_local`, `exists_local`, `count_local`, `iterate_local`, and `list_local` over ``semanage_bool_key_t`` and ``semanage_bool_t`` values. The list/query APIs allocate records for the caller to free with the matching record free routine.

Control flow: callers create or extract a key, optionally begin a transaction, call the local operation, and commit through `semanage_commit`. The implementation routes through the handle's local `dbase_config_t` and the generic database wrappers, so cache loading and transaction entry happen below this header.

State and persistence behavior: modify/delete calls affect local customization files under the direct store sandbox and are made durable only after the enclosing semanage commit installs the sandbox. Query/count/list read the cached local database and do not change persistent policy state.

Dependencies and integration points: depends on `semanage/handle.h` and the corresponding record header. It integrates with direct API component commits, local file databases, validators, and tools such as `semanage` that manage overrides.

Risks: the API assumes callers pass keys matching the record identity and manage returned allocations. Missing transaction discipline can leave writes cached but not installed. Test signals are local override add/delete/query scenarios, commit/reload behavior, and validation failures for malformed or overlapping local records.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/booleans_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/booleans_policy.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/booleans_policy.h

Purpose: declares read-only accessors for `policy boolean` records as seen in the policy database. This is the policy/base view paired with the writable local override API.

Important APIs/types/functions: exports `semanage_bool_query`, `exists`, `count`, `iterate`, and `list` over ``semanage_bool_key_t`` and ``semanage_bool_t``. The APIs use `semanage_handle_t` for backend selection and return cloned record objects owned by the caller.

Control flow: after `semanage_connect`, callers create a key or enumerate the database. The implementation forwards to the policy `dbase_config_t`, which may read a policy file or attach to an in-memory `sepol_policydb_t` during commit.

State and persistence behavior: these calls are observational. They populate or reuse database caches but do not write local files or the installed policy. Returned lists are snapshots, not live database views.

Dependencies and integration points: depends on the object record header and the semanage handle. It is consumed by management tools, SWIG bindings, validators, and direct commit merge code that needs to compare local overrides against base policy state.

Risks: iteration callbacks cannot safely mutate the underlying database and must clone records they retain. Test signals include query/list/count parity with policy contents, callback early-exit behavior, allocation cleanup, and accurate visibility after policy rebuilds.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/booleans_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/context_record.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/context_record.h

Purpose: defines the public opaque record API for a SELinux security context record. It separates key construction/comparison from mutable record fields so the same object model can be used by local files, policydb views, joins, and language bindings.

Important APIs/types/functions: declares the opaque record type `semanage_context_t`, its key type, key create/extract/free helpers, `compare`/`compare2`, field getters and setters, and create/clone/free routines. The main identity is no separate key; fields are user, role, type, and MLS range; contexts can be parsed from and serialized to strings.

Control flow: clients allocate a record with the create API, fill fields with setters, derive or create a key, then pass both to local modify/set/query APIs. Query and list APIs return records that follow the same free routine. Clone APIs deep-copy nested strings, arrays, and contexts where applicable.

State and persistence behavior: the header itself has no persistence, but setter ownership rules define what later database backends will persist. Setters take a `semanage_handle_t` for allocation, validation, message reporting, and libsepol interop.

Dependencies and integration points: used by object-specific local/policy headers, generic database method tables, direct commit validators, `semanage.h`, man pages, and SWIG wrapping. Context-bearing records integrate with `context_record.h`.

Risks: callers must not free borrowed getter strings or nested context pointers unless the API documents ownership through an output allocation. Range/protocol/type constants must stay ABI-stable. Test signals include key equality ordering, clone independence, setter validation, round-trip parse/print, and correct cleanup on allocation failure.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/context_record.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/debug.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/debug.h

Purpose: exposes libsemanage's public message-reporting API. It lets applications inspect the current message context and install a printf-style callback or suppress messages.

Important APIs/types/functions: defines message levels `SEMANAGE_MSG_ERR`, `WARN`, and `INFO`; declares `semanage_msg_get_level`, `get_channel`, `get_fname`, and `semanage_msg_set_callback`. The callback receives caller data, the semanage handle, and a format string.

Control flow: internal code emits messages through debug macros, which populate level/channel/function fields on the handle and invoke the registered callback. The public getters let the callback inspect that state while formatting or routing output.

State and persistence behavior: purely in-memory per-handle state. Installing a callback changes runtime reporting only and has no policy-store side effects.

Dependencies and integration points: used by public applications, SWIG bindings, the internal `debug.h` macros, and the relay handler that forwards libsepol messages into libsemanage callbacks.

Risks: callbacks must be printf-compatible and avoid unsafe reentrant libsemanage operations. Passing NULL suppresses messages, which can hide actionable errors. Test signals include callback invocation level/function metadata, default formatting, suppression behavior, and preservation of `errno` across message emission.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/fcontext_record.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/fcontext_record.h

Purpose: defines the public opaque record API for a file-context regex record. It separates key construction/comparison from mutable record fields so the same object model can be used by local files, policydb views, joins, and language bindings.

Important APIs/types/functions: declares the opaque record type `semanage_fcontext_t`, its key type, key create/extract/free helpers, `compare`/`compare2`, field getters and setters, and create/clone/free routines. The main identity is `semanage_fcontext_key_t` keyed by expression and file type; file types include all, regular, directory, character, block, socket, symlink, and pipe.

Control flow: clients allocate a record with the create API, fill fields with setters, derive or create a key, then pass both to local modify/set/query APIs. Query and list APIs return records that follow the same free routine. Clone APIs deep-copy nested strings, arrays, and contexts where applicable.

State and persistence behavior: the header itself has no persistence, but setter ownership rules define what later database backends will persist. Setters take a `semanage_handle_t` for allocation, validation, message reporting, and libsepol interop.

Dependencies and integration points: used by object-specific local/policy headers, generic database method tables, direct commit validators, `semanage.h`, man pages, and SWIG wrapping. Context-bearing records integrate with `context_record.h`.

Risks: callers must not free borrowed getter strings or nested context pointers unless the API documents ownership through an output allocation. Range/protocol/type constants must stay ABI-stable. Test signals include key equality ordering, clone independence, setter validation, round-trip parse/print, and correct cleanup on allocation failure.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/fcontext_record.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/fcontexts_local.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/fcontexts_local.h

Purpose: declares the local-store CRUD surface for `file-context` records. These functions operate on administrator overrides in the writable semanage store rather than directly exposing the compiled policy view.

Important APIs/types/functions: exports `semanage_fcontext_modify_local`, `del_local`, `query_local`, `exists_local`, `count_local`, `iterate_local`, and `list_local` over ``semanage_fcontext_key_t`` and ``semanage_fcontext_t`` values. The list/query APIs allocate records for the caller to free with the matching record free routine.

Control flow: callers create or extract a key, optionally begin a transaction, call the local operation, and commit through `semanage_commit`. The implementation routes through the handle's local `dbase_config_t` and the generic database wrappers, so cache loading and transaction entry happen below this header.

State and persistence behavior: modify/delete calls affect local customization files under the direct store sandbox and are made durable only after the enclosing semanage commit installs the sandbox. Query/count/list read the cached local database and do not change persistent policy state.

Dependencies and integration points: depends on `semanage/handle.h` and the corresponding record header. It integrates with direct API component commits, local file databases, validators, and tools such as `semanage` that manage overrides.

Risks: the API assumes callers pass keys matching the record identity and manage returned allocations. Missing transaction discipline can leave writes cached but not installed. Test signals are local override add/delete/query scenarios, commit/reload behavior, and validation failures for malformed or overlapping local records.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/fcontexts_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/fcontexts_policy.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/fcontexts_policy.h

Purpose: declares read-only accessors for `file-context` records as seen in the policy database. This is the policy/base view paired with the writable local override API.

Important APIs/types/functions: exports `semanage_fcontext_query`, `exists`, `count`, `iterate`, and `list` over ``semanage_fcontext_key_t`` and ``semanage_fcontext_t``. The APIs use `semanage_handle_t` for backend selection and return cloned record objects owned by the caller. The policy file-context API also exposes `semanage_fcontext_list_homedirs` for generated home-directory file contexts.

Control flow: after `semanage_connect`, callers create a key or enumerate the database. The implementation forwards to the policy `dbase_config_t`, which may read a policy file or attach to an in-memory `sepol_policydb_t` during commit.

State and persistence behavior: these calls are observational. They populate or reuse database caches but do not write local files or the installed policy. Returned lists are snapshots, not live database views.

Dependencies and integration points: depends on the object record header and the semanage handle. It is consumed by management tools, SWIG bindings, validators, and direct commit merge code that needs to compare local overrides against base policy state.

Risks: iteration callbacks cannot safely mutate the underlying database and must clone records they retain. Test signals include query/list/count parity with policy contents, callback early-exit behavior, allocation cleanup, and accurate visibility after policy rebuilds.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/fcontexts_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/handle.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/handle.h

Purpose: declares the central libsemanage connection and transaction handle API. Every public database, module, debug, and policy operation flows through `semanage_handle_t`.

Important APIs/types/functions: defines `semanage_handle_t`, connection type enum values, handle create/destroy, store selection, connect/disconnect, begin transaction, commit, access checks, MLS query, root/store-root setters, reload/rebuild/check flags, dontaudit and tunable flags, default priority, compiler lookup, and module-cache controls.

Control flow: callers create a disconnected handle, optionally select a store and configure flags, connect to the backend, perform reads or begin writes, and commit or disconnect. Writer APIs may implicitly begin a transaction if one is not already held.

State and persistence behavior: the handle owns connection state, config, backend function table, locks, caches, message callback state, and commit options. Persistent effects occur only through backend commit/install logic; many setters just influence the next commit.

Dependencies and integration points: included by nearly all public headers and implemented by handle/direct API internals. It is the ABI boundary for direct store management, future policy server types, SWIG bindings, and command-line tools.

Risks: `semanage_handle_destroy` does not disconnect, so callers must disconnect connected handles first. Configuration setters have ordering constraints before connect. Test signals include connect/disconnect idempotence, lock acquisition, implicit transaction behavior, commit sequence numbers, flag effects on rebuild/reload, and access-check results.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/handle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/ibendport_record.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/ibendport_record.h

Purpose: defines the public opaque record API for a InfiniBand end-port context record. It separates key construction/comparison from mutable record fields so the same object model can be used by local files, policydb views, joins, and language bindings.

Important APIs/types/functions: declares the opaque record type `semanage_ibendport_t`, its key type, key create/extract/free helpers, `compare`/`compare2`, field getters and setters, and create/clone/free routines. The main identity is `semanage_ibendport_key_t` keyed by IB device name and port; records bind an IB device/port pair to a context.

Control flow: clients allocate a record with the create API, fill fields with setters, derive or create a key, then pass both to local modify/set/query APIs. Query and list APIs return records that follow the same free routine. Clone APIs deep-copy nested strings, arrays, and contexts where applicable.

State and persistence behavior: the header itself has no persistence, but setter ownership rules define what later database backends will persist. Setters take a `semanage_handle_t` for allocation, validation, message reporting, and libsepol interop.

Dependencies and integration points: used by object-specific local/policy headers, generic database method tables, direct commit validators, `semanage.h`, man pages, and SWIG wrapping. Context-bearing records integrate with `context_record.h`.

Risks: callers must not free borrowed getter strings or nested context pointers unless the API documents ownership through an output allocation. Range/protocol/type constants must stay ABI-stable. Test signals include key equality ordering, clone independence, setter validation, round-trip parse/print, and correct cleanup on allocation failure.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/ibendport_record.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/ibendports_local.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/ibendports_local.h

Purpose: declares the local-store CRUD surface for `InfiniBand end-port` records. These functions operate on administrator overrides in the writable semanage store rather than directly exposing the compiled policy view.

Important APIs/types/functions: exports `semanage_ibendport_modify_local`, `del_local`, `query_local`, `exists_local`, `count_local`, `iterate_local`, and `list_local` over ``semanage_ibendport_key_t`` and ``semanage_ibendport_t`` values. The list/query APIs allocate records for the caller to free with the matching record free routine.

Control flow: callers create or extract a key, optionally begin a transaction, call the local operation, and commit through `semanage_commit`. The implementation routes through the handle's local `dbase_config_t` and the generic database wrappers, so cache loading and transaction entry happen below this header.

State and persistence behavior: modify/delete calls affect local customization files under the direct store sandbox and are made durable only after the enclosing semanage commit installs the sandbox. Query/count/list read the cached local database and do not change persistent policy state.

Dependencies and integration points: depends on `semanage/handle.h` and the corresponding record header. It integrates with direct API component commits, local file databases, validators, and tools such as `semanage` that manage overrides.

Risks: the API assumes callers pass keys matching the record identity and manage returned allocations. Missing transaction discipline can leave writes cached but not installed. Test signals are local override add/delete/query scenarios, commit/reload behavior, and validation failures for malformed or overlapping local records.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/ibendports_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/ibendports_policy.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/ibendports_policy.h

Purpose: declares read-only accessors for `InfiniBand end-port` records as seen in the policy database. This is the policy/base view paired with the writable local override API.

Important APIs/types/functions: exports `semanage_ibendport_query`, `exists`, `count`, `iterate`, and `list` over ``semanage_ibendport_key_t`` and ``semanage_ibendport_t``. The APIs use `semanage_handle_t` for backend selection and return cloned record objects owned by the caller.

Control flow: after `semanage_connect`, callers create a key or enumerate the database. The implementation forwards to the policy `dbase_config_t`, which may read a policy file or attach to an in-memory `sepol_policydb_t` during commit.

State and persistence behavior: these calls are observational. They populate or reuse database caches but do not write local files or the installed policy. Returned lists are snapshots, not live database views.

Dependencies and integration points: depends on the object record header and the semanage handle. It is consumed by management tools, SWIG bindings, validators, and direct commit merge code that needs to compare local overrides against base policy state.

Risks: iteration callbacks cannot safely mutate the underlying database and must clone records they retain. Test signals include query/list/count parity with policy contents, callback early-exit behavior, allocation cleanup, and accurate visibility after policy rebuilds.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/ibendports_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/ibpkey_record.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/ibpkey_record.h

Purpose: defines the public opaque record API for a InfiniBand P_Key context record. It separates key construction/comparison from mutable record fields so the same object model can be used by local files, policydb views, joins, and language bindings.

Important APIs/types/functions: declares the opaque record type `semanage_ibpkey_t`, its key type, key create/extract/free helpers, `compare`/`compare2`, field getters and setters, and create/clone/free routines. The main identity is `semanage_ibpkey_key_t` keyed by subnet prefix and low/high pkey range; records support string and byte forms for subnet prefixes.

Control flow: clients allocate a record with the create API, fill fields with setters, derive or create a key, then pass both to local modify/set/query APIs. Query and list APIs return records that follow the same free routine. Clone APIs deep-copy nested strings, arrays, and contexts where applicable.

State and persistence behavior: the header itself has no persistence, but setter ownership rules define what later database backends will persist. Setters take a `semanage_handle_t` for allocation, validation, message reporting, and libsepol interop.

Dependencies and integration points: used by object-specific local/policy headers, generic database method tables, direct commit validators, `semanage.h`, man pages, and SWIG wrapping. Context-bearing records integrate with `context_record.h`.

Risks: callers must not free borrowed getter strings or nested context pointers unless the API documents ownership through an output allocation. Range/protocol/type constants must stay ABI-stable. Test signals include key equality ordering, clone independence, setter validation, round-trip parse/print, and correct cleanup on allocation failure.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/ibpkey_record.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/ibpkeys_local.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/ibpkeys_local.h

Purpose: declares the local-store CRUD surface for `InfiniBand P_Key` records. These functions operate on administrator overrides in the writable semanage store rather than directly exposing the compiled policy view.

Important APIs/types/functions: exports `semanage_ibpkey_modify_local`, `del_local`, `query_local`, `exists_local`, `count_local`, `iterate_local`, and `list_local` over ``semanage_ibpkey_key_t`` and ``semanage_ibpkey_t`` values. The list/query APIs allocate records for the caller to free with the matching record free routine.

Control flow: callers create or extract a key, optionally begin a transaction, call the local operation, and commit through `semanage_commit`. The implementation routes through the handle's local `dbase_config_t` and the generic database wrappers, so cache loading and transaction entry happen below this header.

State and persistence behavior: modify/delete calls affect local customization files under the direct store sandbox and are made durable only after the enclosing semanage commit installs the sandbox. Query/count/list read the cached local database and do not change persistent policy state.

Dependencies and integration points: depends on `semanage/handle.h` and the corresponding record header. It integrates with direct API component commits, local file databases, validators, and tools such as `semanage` that manage overrides.

Risks: the API assumes callers pass keys matching the record identity and manage returned allocations. Missing transaction discipline can leave writes cached but not installed. Test signals are local override add/delete/query scenarios, commit/reload behavior, and validation failures for malformed or overlapping local records.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/ibpkeys_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/ibpkeys_policy.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/ibpkeys_policy.h

Purpose: declares read-only accessors for `InfiniBand P_Key` records as seen in the policy database. This is the policy/base view paired with the writable local override API.

Important APIs/types/functions: exports `semanage_ibpkey_query`, `exists`, `count`, `iterate`, and `list` over ``semanage_ibpkey_key_t`` and ``semanage_ibpkey_t``. The APIs use `semanage_handle_t` for backend selection and return cloned record objects owned by the caller.

Control flow: after `semanage_connect`, callers create a key or enumerate the database. The implementation forwards to the policy `dbase_config_t`, which may read a policy file or attach to an in-memory `sepol_policydb_t` during commit.

State and persistence behavior: these calls are observational. They populate or reuse database caches but do not write local files or the installed policy. Returned lists are snapshots, not live database views.

Dependencies and integration points: depends on the object record header and the semanage handle. It is consumed by management tools, SWIG bindings, validators, and direct commit merge code that needs to compare local overrides against base policy state.

Risks: iteration callbacks cannot safely mutate the underlying database and must clone records they retain. Test signals include query/list/count parity with policy contents, callback early-exit behavior, allocation cleanup, and accurate visibility after policy rebuilds.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/ibpkeys_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/iface_record.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/iface_record.h

Purpose: defines the public opaque record API for a network interface context record. It separates key construction/comparison from mutable record fields so the same object model can be used by local files, policydb views, joins, and language bindings.

Important APIs/types/functions: declares the opaque record type `semanage_iface_t`, its key type, key create/extract/free helpers, `compare`/`compare2`, field getters and setters, and create/clone/free routines. The main identity is `semanage_iface_key_t` keyed by interface name; records store separate interface and message contexts.

Control flow: clients allocate a record with the create API, fill fields with setters, derive or create a key, then pass both to local modify/set/query APIs. Query and list APIs return records that follow the same free routine. Clone APIs deep-copy nested strings, arrays, and contexts where applicable.

State and persistence behavior: the header itself has no persistence, but setter ownership rules define what later database backends will persist. Setters take a `semanage_handle_t` for allocation, validation, message reporting, and libsepol interop.

Dependencies and integration points: used by object-specific local/policy headers, generic database method tables, direct commit validators, `semanage.h`, man pages, and SWIG wrapping. Context-bearing records integrate with `context_record.h`.

Risks: callers must not free borrowed getter strings or nested context pointers unless the API documents ownership through an output allocation. Range/protocol/type constants must stay ABI-stable. Test signals include key equality ordering, clone independence, setter validation, round-trip parse/print, and correct cleanup on allocation failure.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/iface_record.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/interfaces_local.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/interfaces_local.h

Purpose: declares the local-store CRUD surface for `network interface` records. These functions operate on administrator overrides in the writable semanage store rather than directly exposing the compiled policy view.

Important APIs/types/functions: exports `semanage_iface_modify_local`, `del_local`, `query_local`, `exists_local`, `count_local`, `iterate_local`, and `list_local` over ``semanage_iface_key_t`` and ``semanage_iface_t`` values. The list/query APIs allocate records for the caller to free with the matching record free routine.

Control flow: callers create or extract a key, optionally begin a transaction, call the local operation, and commit through `semanage_commit`. The implementation routes through the handle's local `dbase_config_t` and the generic database wrappers, so cache loading and transaction entry happen below this header.

State and persistence behavior: modify/delete calls affect local customization files under the direct store sandbox and are made durable only after the enclosing semanage commit installs the sandbox. Query/count/list read the cached local database and do not change persistent policy state.

Dependencies and integration points: depends on `semanage/handle.h` and the corresponding record header. It integrates with direct API component commits, local file databases, validators, and tools such as `semanage` that manage overrides.

Risks: the API assumes callers pass keys matching the record identity and manage returned allocations. Missing transaction discipline can leave writes cached but not installed. Test signals are local override add/delete/query scenarios, commit/reload behavior, and validation failures for malformed or overlapping local records.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/interfaces_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/interfaces_policy.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/interfaces_policy.h

Purpose: declares read-only accessors for `network interface` records as seen in the policy database. This is the policy/base view paired with the writable local override API.

Important APIs/types/functions: exports `semanage_iface_query`, `exists`, `count`, `iterate`, and `list` over ``semanage_iface_key_t`` and ``semanage_iface_t``. The APIs use `semanage_handle_t` for backend selection and return cloned record objects owned by the caller.

Control flow: after `semanage_connect`, callers create a key or enumerate the database. The implementation forwards to the policy `dbase_config_t`, which may read a policy file or attach to an in-memory `sepol_policydb_t` during commit.

State and persistence behavior: these calls are observational. They populate or reuse database caches but do not write local files or the installed policy. Returned lists are snapshots, not live database views.

Dependencies and integration points: depends on the object record header and the semanage handle. It is consumed by management tools, SWIG bindings, validators, and direct commit merge code that needs to compare local overrides against base policy state.

Risks: iteration callbacks cannot safely mutate the underlying database and must clone records they retain. Test signals include query/list/count parity with policy contents, callback early-exit behavior, allocation cleanup, and accurate visibility after policy rebuilds.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/interfaces_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/modules.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/modules.h

Purpose: declares the public policy module management API for installing, removing, extracting, listing, enabling, and describing semanage modules.

Important APIs/types/functions: exports legacy install/remove/list/extract calls plus structured `semanage_module_info_t` and `semanage_module_key_t` create/destroy/get/set APIs. `semanage_module_install_info`, `get_module_info`, `list_all`, `set_enabled`, and `remove_key` support priority, module name, language extension, and enabled state.

Control flow: module operations are transaction-scoped. Callers create a key or info object, fill priority/name/lang/enabled fields, install raw module bytes or files, remove by name/key, extract mapped source or CIL bytes, and commit to compile/link/install the store.

State and persistence behavior: installs write module payloads under priority/name directories in the semanage module store, optionally compressed. Enable state is stored per module name across priorities. Extraction maps stored module data for the caller to unmap.

Dependencies and integration points: depends on `handle.h`, `stdint.h`, and `sys/types.h`; implemented mostly by `direct_api.c`; wrapped by SWIG; consumed by semodule-like tools and direct commit checksum logic.

Risks: ownership is mixed: info/key structs require destroy plus free, extracted blobs require `munmap`, and invalid modinfo can return distinct negative codes. Test signals include priority sorting, enable/disable across priorities, compressed module install/extract, invalid metadata rejection, and rebuild triggering on module changes.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/modules.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/node_record.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/node_record.h

Purpose: defines the public opaque record API for a network node context record. It separates key construction/comparison from mutable record fields so the same object model can be used by local files, policydb views, joins, and language bindings.

Important APIs/types/functions: declares the opaque record type `semanage_node_t`, its key type, key create/extract/free helpers, `compare`/`compare2`, field getters and setters, and create/clone/free routines. The main identity is `semanage_node_key_t` keyed by address, mask, and IP protocol family; records support IPv4/IPv6 string and byte address forms.

Control flow: clients allocate a record with the create API, fill fields with setters, derive or create a key, then pass both to local modify/set/query APIs. Query and list APIs return records that follow the same free routine. Clone APIs deep-copy nested strings, arrays, and contexts where applicable.

State and persistence behavior: the header itself has no persistence, but setter ownership rules define what later database backends will persist. Setters take a `semanage_handle_t` for allocation, validation, message reporting, and libsepol interop.

Dependencies and integration points: used by object-specific local/policy headers, generic database method tables, direct commit validators, `semanage.h`, man pages, and SWIG wrapping. Context-bearing records integrate with `context_record.h`.

Risks: callers must not free borrowed getter strings or nested context pointers unless the API documents ownership through an output allocation. Range/protocol/type constants must stay ABI-stable. Test signals include key equality ordering, clone independence, setter validation, round-trip parse/print, and correct cleanup on allocation failure.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/node_record.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/nodes_local.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/nodes_local.h

Purpose: declares the local-store CRUD surface for `network node` records. These functions operate on administrator overrides in the writable semanage store rather than directly exposing the compiled policy view.

Important APIs/types/functions: exports `semanage_node_modify_local`, `del_local`, `query_local`, `exists_local`, `count_local`, `iterate_local`, and `list_local` over ``semanage_node_key_t`` and ``semanage_node_t`` values. The list/query APIs allocate records for the caller to free with the matching record free routine.

Control flow: callers create or extract a key, optionally begin a transaction, call the local operation, and commit through `semanage_commit`. The implementation routes through the handle's local `dbase_config_t` and the generic database wrappers, so cache loading and transaction entry happen below this header.

State and persistence behavior: modify/delete calls affect local customization files under the direct store sandbox and are made durable only after the enclosing semanage commit installs the sandbox. Query/count/list read the cached local database and do not change persistent policy state.

Dependencies and integration points: depends on `semanage/handle.h` and the corresponding record header. It integrates with direct API component commits, local file databases, validators, and tools such as `semanage` that manage overrides.

Risks: the API assumes callers pass keys matching the record identity and manage returned allocations. Missing transaction discipline can leave writes cached but not installed. Test signals are local override add/delete/query scenarios, commit/reload behavior, and validation failures for malformed or overlapping local records.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/nodes_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/nodes_policy.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/nodes_policy.h

Purpose: declares read-only accessors for `network node` records as seen in the policy database. This is the policy/base view paired with the writable local override API.

Important APIs/types/functions: exports `semanage_node_query`, `exists`, `count`, `iterate`, and `list` over ``semanage_node_key_t`` and ``semanage_node_t``. The APIs use `semanage_handle_t` for backend selection and return cloned record objects owned by the caller.

Control flow: after `semanage_connect`, callers create a key or enumerate the database. The implementation forwards to the policy `dbase_config_t`, which may read a policy file or attach to an in-memory `sepol_policydb_t` during commit.

State and persistence behavior: these calls are observational. They populate or reuse database caches but do not write local files or the installed policy. Returned lists are snapshots, not live database views.

Dependencies and integration points: depends on the object record header and the semanage handle. It is consumed by management tools, SWIG bindings, validators, and direct commit merge code that needs to compare local overrides against base policy state.

Risks: iteration callbacks cannot safely mutate the underlying database and must clone records they retain. Test signals include query/list/count parity with policy contents, callback early-exit behavior, allocation cleanup, and accurate visibility after policy rebuilds.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/nodes_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/port_record.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/port_record.h

Purpose: defines the public opaque record API for a network port context record. It separates key construction/comparison from mutable record fields so the same object model can be used by local files, policydb views, joins, and language bindings.

Important APIs/types/functions: declares the opaque record type `semanage_port_t`, its key type, key create/extract/free helpers, `compare`/`compare2`, field getters and setters, and create/clone/free routines. The main identity is `semanage_port_key_t` keyed by low/high port and protocol; protocol constants cover UDP, TCP, DCCP, and SCTP.

Control flow: clients allocate a record with the create API, fill fields with setters, derive or create a key, then pass both to local modify/set/query APIs. Query and list APIs return records that follow the same free routine. Clone APIs deep-copy nested strings, arrays, and contexts where applicable.

State and persistence behavior: the header itself has no persistence, but setter ownership rules define what later database backends will persist. Setters take a `semanage_handle_t` for allocation, validation, message reporting, and libsepol interop.

Dependencies and integration points: used by object-specific local/policy headers, generic database method tables, direct commit validators, `semanage.h`, man pages, and SWIG wrapping. Context-bearing records integrate with `context_record.h`.

Risks: callers must not free borrowed getter strings or nested context pointers unless the API documents ownership through an output allocation. Range/protocol/type constants must stay ABI-stable. Test signals include key equality ordering, clone independence, setter validation, round-trip parse/print, and correct cleanup on allocation failure.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/port_record.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/ports_local.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/ports_local.h

Purpose: declares the local-store CRUD surface for `network port` records. These functions operate on administrator overrides in the writable semanage store rather than directly exposing the compiled policy view.

Important APIs/types/functions: exports `semanage_port_modify_local`, `del_local`, `query_local`, `exists_local`, `count_local`, `iterate_local`, and `list_local` over ``semanage_port_key_t`` and ``semanage_port_t`` values. The list/query APIs allocate records for the caller to free with the matching record free routine.

Control flow: callers create or extract a key, optionally begin a transaction, call the local operation, and commit through `semanage_commit`. The implementation routes through the handle's local `dbase_config_t` and the generic database wrappers, so cache loading and transaction entry happen below this header.

State and persistence behavior: modify/delete calls affect local customization files under the direct store sandbox and are made durable only after the enclosing semanage commit installs the sandbox. Query/count/list read the cached local database and do not change persistent policy state.

Dependencies and integration points: depends on `semanage/handle.h` and the corresponding record header. It integrates with direct API component commits, local file databases, validators, and tools such as `semanage` that manage overrides.

Risks: the API assumes callers pass keys matching the record identity and manage returned allocations. Missing transaction discipline can leave writes cached but not installed. Test signals are local override add/delete/query scenarios, commit/reload behavior, and validation failures for malformed or overlapping local records.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/ports_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/ports_policy.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/ports_policy.h

Purpose: declares read-only accessors for `network port` records as seen in the policy database. This is the policy/base view paired with the writable local override API.

Important APIs/types/functions: exports `semanage_port_query`, `exists`, `count`, `iterate`, and `list` over ``semanage_port_key_t`` and ``semanage_port_t``. The APIs use `semanage_handle_t` for backend selection and return cloned record objects owned by the caller.

Control flow: after `semanage_connect`, callers create a key or enumerate the database. The implementation forwards to the policy `dbase_config_t`, which may read a policy file or attach to an in-memory `sepol_policydb_t` during commit.

State and persistence behavior: these calls are observational. They populate or reuse database caches but do not write local files or the installed policy. Returned lists are snapshots, not live database views.

Dependencies and integration points: depends on the object record header and the semanage handle. It is consumed by management tools, SWIG bindings, validators, and direct commit merge code that needs to compare local overrides against base policy state.

Risks: iteration callbacks cannot safely mutate the underlying database and must clone records they retain. Test signals include query/list/count parity with policy contents, callback early-exit behavior, allocation cleanup, and accurate visibility after policy rebuilds.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/ports_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/semanage.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/semanage.h

Purpose: umbrella public header for libsemanage. It aggregates handle, modules, debug, record, local database, policy database, and active boolean APIs into one include.

Important APIs/types/functions: includes the handle and module APIs first, then record definitions for booleans, users, seusers, contexts, interfaces, ports, InfiniBand keys/endports, and nodes, followed by local/policy database headers and active boolean access.

Control flow: applications that include this header can compile against the whole public API without tracking per-object headers. The header itself performs no logic; ordering matters to satisfy opaque type dependencies.

State and persistence behavior: no runtime state. Its persistence impact is ABI/API exposure: anything included here is part of the broad public surface and is seen by SWIG exception generation.

Dependencies and integration points: used by examples, bindings, documentation, package consumers, and `exception.sh`, which compiles this header to discover extern integer-returning functions for Python exception wrappers.

Risks: adding a header here expands public API visibility and may affect generated bindings. Missing an object header makes the umbrella incomplete. Test signals are clean compilation of a program including only `semanage/semanage.h`, SWIG generation success, and installed-header completeness.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/semanage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/seuser_record.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/seuser_record.h

Purpose: defines the public opaque record API for a login-to-SELinux-user mapping record. It separates key construction/comparison from mutable record fields so the same object model can be used by local files, policydb views, joins, and language bindings.

Important APIs/types/functions: declares the opaque record type `semanage_seuser_t`, its key type, key create/extract/free helpers, `compare`/`compare2`, field getters and setters, and create/clone/free routines. The main identity is `semanage_seuser_key_t` keyed by login name; records store Linux login name, SELinux user name, and MLS range.

Control flow: clients allocate a record with the create API, fill fields with setters, derive or create a key, then pass both to local modify/set/query APIs. Query and list APIs return records that follow the same free routine. Clone APIs deep-copy nested strings, arrays, and contexts where applicable.

State and persistence behavior: the header itself has no persistence, but setter ownership rules define what later database backends will persist. Setters take a `semanage_handle_t` for allocation, validation, message reporting, and libsepol interop.

Dependencies and integration points: used by object-specific local/policy headers, generic database method tables, direct commit validators, `semanage.h`, man pages, and SWIG wrapping. Context-bearing records integrate with `context_record.h`.

Risks: callers must not free borrowed getter strings or nested context pointers unless the API documents ownership through an output allocation. Range/protocol/type constants must stay ABI-stable. Test signals include key equality ordering, clone independence, setter validation, round-trip parse/print, and correct cleanup on allocation failure.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/seuser_record.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/seusers_local.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/seusers_local.h

Purpose: declares the local-store CRUD surface for `login mapping` records. These functions operate on administrator overrides in the writable semanage store rather than directly exposing the compiled policy view.

Important APIs/types/functions: exports `semanage_seuser_modify_local`, `del_local`, `query_local`, `exists_local`, `count_local`, `iterate_local`, and `list_local` over ``semanage_seuser_key_t`` and ``semanage_seuser_t`` values. The list/query APIs allocate records for the caller to free with the matching record free routine.

Control flow: callers create or extract a key, optionally begin a transaction, call the local operation, and commit through `semanage_commit`. The implementation routes through the handle's local `dbase_config_t` and the generic database wrappers, so cache loading and transaction entry happen below this header.

State and persistence behavior: modify/delete calls affect local customization files under the direct store sandbox and are made durable only after the enclosing semanage commit installs the sandbox. Query/count/list read the cached local database and do not change persistent policy state.

Dependencies and integration points: depends on `semanage/handle.h` and the corresponding record header. It integrates with direct API component commits, local file databases, validators, and tools such as `semanage` that manage overrides.

Risks: the API assumes callers pass keys matching the record identity and manage returned allocations. Missing transaction discipline can leave writes cached but not installed. Test signals are local override add/delete/query scenarios, commit/reload behavior, and validation failures for malformed or overlapping local records.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/seusers_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/seusers_policy.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/seusers_policy.h

Purpose: declares read-only accessors for `login mapping` records as seen in the policy database. This is the policy/base view paired with the writable local override API.

Important APIs/types/functions: exports `semanage_seuser_query`, `exists`, `count`, `iterate`, and `list` over ``semanage_seuser_key_t`` and ``semanage_seuser_t``. The APIs use `semanage_handle_t` for backend selection and return cloned record objects owned by the caller.

Control flow: after `semanage_connect`, callers create a key or enumerate the database. The implementation forwards to the policy `dbase_config_t`, which may read a policy file or attach to an in-memory `sepol_policydb_t` during commit.

State and persistence behavior: these calls are observational. They populate or reuse database caches but do not write local files or the installed policy. Returned lists are snapshots, not live database views.

Dependencies and integration points: depends on the object record header and the semanage handle. It is consumed by management tools, SWIG bindings, validators, and direct commit merge code that needs to compare local overrides against base policy state.

Risks: iteration callbacks cannot safely mutate the underlying database and must clone records they retain. Test signals include query/list/count parity with policy contents, callback early-exit behavior, allocation cleanup, and accurate visibility after policy rebuilds.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/seusers_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/user_record.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/user_record.h

Purpose: defines the public opaque record API for a SELinux user record. It separates key construction/comparison from mutable record fields so the same object model can be used by local files, policydb views, joins, and language bindings.

Important APIs/types/functions: declares the opaque record type `semanage_user_t`, its key type, key create/extract/free helpers, `compare`/`compare2`, field getters and setters, and create/clone/free routines. The main identity is `semanage_user_key_t` keyed by SELinux user name; records store label prefix, MLS level/range, and a role set.

Control flow: clients allocate a record with the create API, fill fields with setters, derive or create a key, then pass both to local modify/set/query APIs. Query and list APIs return records that follow the same free routine. Clone APIs deep-copy nested strings, arrays, and contexts where applicable.

State and persistence behavior: the header itself has no persistence, but setter ownership rules define what later database backends will persist. Setters take a `semanage_handle_t` for allocation, validation, message reporting, and libsepol interop.

Dependencies and integration points: used by object-specific local/policy headers, generic database method tables, direct commit validators, `semanage.h`, man pages, and SWIG wrapping. Context-bearing records integrate with `context_record.h`.

Risks: callers must not free borrowed getter strings or nested context pointers unless the API documents ownership through an output allocation. Range/protocol/type constants must stay ABI-stable. Test signals include key equality ordering, clone independence, setter validation, round-trip parse/print, and correct cleanup on allocation failure.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/user_record.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/users_local.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/users_local.h

Purpose: declares the local-store CRUD surface for `SELinux user` records. These functions operate on administrator overrides in the writable semanage store rather than directly exposing the compiled policy view.

Important APIs/types/functions: exports `semanage_user_modify_local`, `del_local`, `query_local`, `exists_local`, `count_local`, `iterate_local`, and `list_local` over ``semanage_user_key_t`` and ``semanage_user_t`` values. The list/query APIs allocate records for the caller to free with the matching record free routine.

Control flow: callers create or extract a key, optionally begin a transaction, call the local operation, and commit through `semanage_commit`. The implementation routes through the handle's local `dbase_config_t` and the generic database wrappers, so cache loading and transaction entry happen below this header.

State and persistence behavior: modify/delete calls affect local customization files under the direct store sandbox and are made durable only after the enclosing semanage commit installs the sandbox. Query/count/list read the cached local database and do not change persistent policy state.

Dependencies and integration points: depends on `semanage/handle.h` and the corresponding record header. It integrates with direct API component commits, local file databases, validators, and tools such as `semanage` that manage overrides.

Risks: the API assumes callers pass keys matching the record identity and manage returned allocations. Missing transaction discipline can leave writes cached but not installed. Test signals are local override add/delete/query scenarios, commit/reload behavior, and validation failures for malformed or overlapping local records.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/users_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/users_policy.h -->

# sources/security-integrity/selinux/libsemanage/include/semanage/users_policy.h

Purpose: declares read-only accessors for `SELinux user` records as seen in the policy database. This is the policy/base view paired with the writable local override API.

Important APIs/types/functions: exports `semanage_user_query`, `exists`, `count`, `iterate`, and `list` over ``semanage_user_key_t`` and ``semanage_user_t``. The APIs use `semanage_handle_t` for backend selection and return cloned record objects owned by the caller.

Control flow: after `semanage_connect`, callers create a key or enumerate the database. The implementation forwards to the policy `dbase_config_t`, which may read a policy file or attach to an in-memory `sepol_policydb_t` during commit.

State and persistence behavior: these calls are observational. They populate or reuse database caches but do not write local files or the installed policy. Returned lists are snapshots, not live database views.

Dependencies and integration points: depends on the object record header and the semanage handle. It is consumed by management tools, SWIG bindings, validators, and direct commit merge code that needs to compare local overrides against base policy state.

Risks: iteration callbacks cannot safely mutate the underlying database and must clone records they retain. Test signals include query/list/count parity with policy contents, callback early-exit behavior, allocation cleanup, and accurate visibility after policy rebuilds.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/include/semanage/users_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/man/Makefile -->

# sources/security-integrity/selinux/libsemanage/man/Makefile

Purpose: installs libsemanage manual pages for section 3 API documentation and section 5 configuration files, including localized variants.

Important APIs/targets: variables include `PREFIX`, `MANDIR`, `MAN3SUBDIR`, `MAN5SUBDIR`, `MAN3DIR`, `MAN5DIR`, and `LINGUAS`. `install` creates target man directories, installs `man3/*.3` and `man5/*.5`, then repeats for each language with `lang/man3` or `lang/man5` subdirectories.

Control flow: package builds invoke `make install`; the target stages English man pages first and conditionally stages translated pages only when the relevant directories exist.

State and persistence behavior: writes documentation files under `$(DESTDIR)$(MANDIR)` and does not modify source files. `all` is intentionally empty.

Dependencies and integration points: used by top-level SELinux userspace installation. It must stay aligned with public headers and API behavior so generated packages ship matching docs.

Risks: glob install failures can occur if expected `man3` or `man5` files are absent. The loop assumes shell semantics and unquoted variables. Test signals include staged package inspection for all man sections and language-specific directory layouts.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/man/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/Makefile -->

# sources/security-integrity/selinux/libsemanage/src/Makefile

Purpose: builds libsemanage static/shared libraries, pkg-config metadata, generated lexer/parser sources, SWIG Python and Ruby bindings, and install artifacts.

Important APIs/targets: defines Python/Ruby discovery variables, install directories, `LIBA`, `LIBSO`, `LIBPC`, SWIG targets, generated files, `SRCS/OBJS/LOBJS`, compiler flags, `all`, `pywrap`, `rubywrap`, `install`, wrapper installs, `relabel`, `clean`, and `distclean`. It generates `conf-scan.c` with flex and `conf-parse.c/.h` with bison.

Control flow: normal builds compile all C sources except generated wrappers, compile parser/lexer with `-Werror` filtered out, archive `libsemanage.a`, link `libsemanage.so.2` against libsepol, libselinux, audit, and bzip2, then create the `libsemanage.so` symlink. Wrapper targets depend on the library and generated SWIG C.

State and persistence behavior: writes object files, PIC objects, generated parser/lexer/SWIG files, shared/static libraries, pkg-config file, and installed library/config/binding files under `DESTDIR`. `distclean` removes generated binding and parser products.

Dependencies and integration points: integrates C compiler, flex, bison, SWIG, pkg-config, Python sysconfig, Ruby RbConfig, libselinux, libsepol, libaudit, and bz2. The version script and soname define exported ABI.

Risks: toolchain discovery is host-sensitive, generated sources can become stale, parser warnings are intentionally tolerated, and `-z defs` catches unresolved symbols only in shared builds. Test signals are clean static/shared builds, wrapper imports, pkg-config metadata correctness, install staging, and ABI symbol-map checks.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/boolean_internal.h -->

# sources/security-integrity/selinux/libsemanage/src/boolean_internal.h

Purpose: internal aggregation header for boolean record and database backend implementations. It connects the public boolean APIs to the generic database framework.

Important APIs/types/functions: declares `SEMANAGE_BOOL_RTABLE` and init/release pairs for file, policydb, and active boolean databases: `bool_file_dbase_init`, `bool_policydb_dbase_init`, and `bool_activedb_dbase_init`.

Control flow: backend setup code includes this header, initializes the appropriate `dbase_config_t`, then the public boolean APIs route through generic database wrappers to the selected backend.

State and persistence behavior: no state in the header, but the declared backends cover persistent local boolean files, policydb boolean declarations, and active kernel boolean state. Release functions free backend-specific cache/config allocations.

Dependencies and integration points: includes public boolean local/policy/active headers plus `database.h` and internal `handle.h`. It is the coordination point for `boolean_record.c`, `booleans_file.c`, `booleans_policydb.c`, and `booleans_activedb.c`.

Risks: backend table mismatches would surface as incorrect CRUD behavior across all boolean APIs. Test signals include all three boolean views initializing, querying, listing, and releasing without leaks or cross-view confusion.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/boolean_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/boolean_record.c -->

# sources/security-integrity/selinux/libsemanage/src/boolean_record.c

Purpose: implements `semanage_bool_t` and `semanage_bool_key_t` as thin wrappers around libsepol boolean records while adding semanage-specific name substitution for alternate policy roots.

Important APIs/types/functions: exports key create/extract/free, comparisons, name/value getters and setters, create/clone/free, qsort comparator, and the `SEMANAGE_BOOL_RTABLE` generic record table.

Control flow: most functions delegate directly to `sepol_bool_*`. `semanage_bool_set_name` temporarily adjusts the libselinux policy root to the semanage selected store, applies `selinux_boolean_sub`, restores the original root, and stores the substituted name in the sepol record.

State and persistence behavior: record objects are heap-backed libsepol values. Persistent effects occur only when records are later written through file, policydb, or active backends. The temporary policy-root switch is process-global and must be restored carefully.

Dependencies and integration points: depends on libsepol boolean records, libselinux policy-root/boolean substitution APIs, semanage root/store config, and the generic database method table.

Risks: policy-root switching is sensitive to errors and thread safety. `semanage_bool_set_name` requires a valid SELinux policy root and can fail before allocating a substituted name. Test signals include name substitution under alternate roots, clone/free ownership, qsort ordering, and no leaked or stuck policy root on failures.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/boolean_record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/booleans_active.c -->

# sources/security-integrity/selinux/libsemanage/src/booleans_active.c

Purpose: implements the public active-boolean API by forwarding operations to the handle's active boolean database configuration.

Important APIs/types/functions: `semanage_bool_set_active`, `query_active`, `exists_active`, `count_active`, `iterate_active`, and `list_active` call `dbase_set`, `dbase_query`, `dbase_exists`, `dbase_count`, `dbase_iterate`, and `dbase_list`.

Control flow: each function retrieves `semanage_bool_dbase_active(handle)` and delegates to the generic database wrapper. Writes enter the active database write path; reads enter the read-only path.

State and persistence behavior: state is managed by the active database backend, which reads and commits complete active boolean lists. These calls affect live SELinux boolean state rather than local default files.

Dependencies and integration points: includes the public active header, `boolean_internal.h`, and `database.h`; integrates with `booleans_activedb.c` and libselinux active boolean APIs through the backend.

Risks: thin forwarding leaves correctness dependent on active backend initialization and wrapper transaction checks. Test signals are active set/query/list calls and error propagation from inaccessible SELinux active state.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/booleans_active.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/booleans_activedb.c -->

# sources/security-integrity/selinux/libsemanage/src/booleans_activedb.c

Purpose: implements the active boolean database backend, adapting libselinux active boolean state to the generic linked-list database API.

Important APIs/types/functions: defines `bool_read_list`, `bool_commit_list`, `SEMANAGE_BOOL_ACTIVEDB_RTABLE`, `bool_activedb_dbase_init`, and `bool_activedb_dbase_release`.

Control flow: `bool_read_list` calls `security_get_boolean_names`, allocates semanage boolean records, sets names and active values with `security_get_boolean_active`, and returns an array. `bool_commit_list` converts records to name/value arrays and calls `security_set_boolean_list`. Init wraps the read/commit functions in `dbase_activedb_init`.

State and persistence behavior: the backend caches active booleans in memory through the generic active database. Flush writes the full list back to the running SELinux kernel state; it is not a persistent local-policy write.

Dependencies and integration points: depends on libselinux active boolean APIs, `SEMANAGE_BOOL_RTABLE`, `database_activedb`, and semanage error reporting.

Risks: partial allocation failures require freeing names, values, records, and arrays. Full-list commits can overwrite concurrent active changes. Test signals include accurate count/list, set-active round trips, failure cleanup, and behavior when SELinux is disabled or inaccessible.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/booleans_activedb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/booleans_file.c -->

# sources/security-integrity/selinux/libsemanage/src/booleans_file.c

Purpose: implements boolean record parsing and printing for the local file-backed boolean database.

Important APIs/types/functions: `bool_print` writes `name=value`; `bool_parse` parses names, `=`, and values accepting true/false case variants or integer 0/1; `SEMANAGE_BOOL_FILE_RTABLE` supplies the file extension table; init/release wrap `dbase_file_init` and `dbase_file_release`.

Control flow: the generic file database reads lines into parse info, creates a boolean record via `SEMANAGE_BOOL_RTABLE`, and calls `bool_parse`. Parsed names go through `semanage_bool_set_name`, values are validated, and trailing space/end-of-line is asserted. Printing is the reverse for flush.

State and persistence behavior: local boolean defaults persist in text files under the semanage store. The backend caches records in memory, marks modifications, and rewrites the writable file on flush/commit.

Dependencies and integration points: depends on parse utilities, debug macros, file database backend, and boolean record substitution logic.

Risks: malformed values, invalid lines, or name-substitution failures abort parsing. Rewriting all records means printer correctness affects persistence. Test signals include parse round trips for true/false/0/1, malformed-value diagnostics, EOF handling, and commit file contents.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/booleans_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/booleans_local.c -->

# sources/security-integrity/selinux/libsemanage/src/booleans_local.c

Purpose: implements public local boolean CRUD as thin wrappers over the generic local boolean database.

Important APIs/types/functions: exports `semanage_bool_modify_local`, `del_local`, `query_local`, `exists_local`, `count_local`, `iterate_local`, and `list_local`.

Control flow: each function obtains `semanage_bool_dbase_local(handle)` and forwards to `dbase_modify`, `dbase_del`, `dbase_query`, `dbase_exists`, `dbase_count`, `dbase_iterate`, or `dbase_list`.

State and persistence behavior: modifications update the local boolean override cache and are persisted through the normal semanage transaction commit. Reads observe the local defaults, not necessarily live active values.

Dependencies and integration points: depends on `boolean_internal.h` and `database.h`; participates in direct commit where local boolean changes are merged into the policydb/kernel policy.

Risks: all behavioral validation is delegated to the database and record layers. Test signals include local default add/delete/query, commit merge into kernel policy, and distinction from active boolean operations.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/booleans_local.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/booleans_policy.c -->

# sources/security-integrity/selinux/libsemanage/src/booleans_policy.c

Purpose: implements public policy boolean read APIs by forwarding to the policy boolean database.

Important APIs/types/functions: `semanage_bool_query`, `exists`, `count`, `iterate`, and `list` wrap generic database read operations on `semanage_bool_dbase_policy(handle)`.

Control flow: connected callers invoke a policy read function, the wrapper enters the read-only database path, caches/resyncs the policy backend as needed, and returns cloned boolean records or counts.

State and persistence behavior: read-only observation of boolean declarations and defaults in the policydb. It may fill caches but never writes store files.

Dependencies and integration points: connects public `booleans_policy.h` to `booleans_policydb.c` through `database.c` wrappers. Used by management tools and validators that need base policy state.

Risks: stale cache detection depends on database serials. Test signals include query/list parity with policydb contents, iterate callback behavior, and correct visibility after rebuild.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/booleans_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/booleans_policydb.c -->

# sources/security-integrity/selinux/libsemanage/src/booleans_policydb.c

Purpose: adapts libsepol policydb boolean helpers into the semanage generic policydb database framework.

Important APIs/types/functions: defines `SEMANAGE_BOOL_POLICYDB_RTABLE` with sepol boolean add/modify/set/query/count/exists/iterate function pointers, plus `bool_policydb_dbase_init` and `bool_policydb_dbase_release`.

Control flow: init calls `dbase_policydb_init` with the generic boolean record table and policydb extension table; release delegates to `dbase_policydb_release`.

State and persistence behavior: the resulting backend reads or mutates an attached or cached `sepol_policydb_t`. In direct commit, local boolean changes are merged into this policydb before the kernel policy is written.

Dependencies and integration points: depends on libsepol `bools.h`, `SEMANAGE_BOOL_RTABLE`, and `database_policydb`. It is the policy-side counterpart to the local file and active backends.

Risks: function-pointer table correctness is critical because generic wrappers assume uniform semantics. Test signals are policydb add/modify/query/list behavior and successful merge of local boolean overrides during commit.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/booleans_policydb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/compressed_file.c -->

# sources/security-integrity/selinux/libsemanage/src/compressed_file.c

Purpose: centralizes reading, unmapping, and writing CIL/module files that may be bzip2-compressed.

Important APIs/types/functions: internal helpers `bzip` and `bunzip`; public/internal APIs `map_compressed_file`, `unmap_compressed_file`, and `write_compressed_file` over `struct file_contents`.

Control flow: mapping first tries to open and inspect the file, detects bzip magic, either memory-maps uncompressed files or decompresses streams into allocated memory, and records whether the data was compressed. Writing either writes raw bytes or compresses through libbz2 according to configuration on the handle.

State and persistence behavior: maps uncompressed files with `mmap` and stores decompressed content in heap memory. `unmap_compressed_file` chooses `munmap` versus `free` based on the `compressed` flag. Writes replace file contents at the requested path.

Dependencies and integration points: depends on bzlib, mmap, stdio, semanage config fields `bzip_blocksize`/`bzip_small`, and direct module install/extract code.

Risks: compressed and mapped lifetime paths differ; incorrect `compressed` bookkeeping causes invalid free/unmap. Decompression grows buffers dynamically and must guard allocation failure. Test signals include compressed/uncompressed round trips, zero-length files, corrupt bzip streams, and cleanup under failure.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/compressed_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/compressed_file.h -->

# sources/security-integrity/selinux/libsemanage/src/compressed_file.h

Purpose: declares the internal possibly-compressed file abstraction used for module and CIL payload handling.

Important APIs/types/functions: `struct file_contents` contains uncompressed `data`, `len`, and a `compressed` discriminator. Declares `map_compressed_file`, `unmap_compressed_file`, and `write_compressed_file`.

Control flow: callers map a path, use the returned uncompressed memory, and always release with `unmap_compressed_file`. Writers pass raw bytes and let the implementation apply configured compression.

State and persistence behavior: the struct describes transient mapped or allocated memory. `write_compressed_file` is the only persistent operation and writes to the provided path using handle configuration.

Dependencies and integration points: includes `sys/mman.h`, `sys/types.h`, and internal `handle.h`; consumed by `direct_api.c` module install/extract paths.

Risks: callers must not mix ordinary `free`/`munmap` with this abstraction. Test signals are clean map/unmap for both compressed and uncompressed files and writer output readable by `map_compressed_file`.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/compressed_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/conf-parse.y -->

# sources/security-integrity/selinux/libsemanage/src/conf-parse.y

Purpose: bison grammar and implementation for parsing `semanage.conf`, creating a populated `semanage_conf_t` with defaults and user overrides.

Important APIs/types/functions: grammar tokens cover store settings, policy version, target platform, booleans such as `expand-check` and `optimize-policy`, bzip options, external command blocks, and verifier blocks. C helpers include `semanage_conf_parse`, `semanage_conf_destroy`, `semanage_error`, `parse_module_store`, `parse_store_root_path`, `parse_compiler_path`, and `new_external_prog`.

Control flow: `semanage_conf_parse` allocates defaults, opens the config file if present, invokes the lexer/parser, destroys lexer state, and returns defaults when the file cannot be read. Grammar actions validate values and update the current global config, aborting on fatal parse errors.

State and persistence behavior: parser state uses file-global `current_conf`, `new_external`, and `parse_errors`, so it is explicitly not thread-safe. It allocates strings and linked lists for external commands; destroy frees all owned members.

Dependencies and integration points: integrates with flex output from `conf-scan.l`, libsepol policy version limits, libselinux policy root, semanage utilities, and direct commit configuration.

Risks: global parser state limits concurrency; duplicate string assignments must free previous values; some errors increment parse count but continue until abort boundaries. Test signals include default config when missing, validation errors for each option, command-block path requirements, and leak-free destroy after partial parses.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/conf-parse.y -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/conf-scan.l -->

# sources/security-integrity/selinux/libsemanage/src/conf-scan.l

Purpose: flex lexer for `semanage.conf`. It recognizes option names, command block headers, assignment delimiters, and string arguments for the bison parser.

Important APIs/types/functions: returns tokens such as `MODULE_STORE`, `STORE_ROOT`, `COMPILER_DIR`, `VERSION`, `LOAD_POLICY_START`, `SETFILES_START`, verifier starts, `PROG_PATH`, `PROG_ARGS`, `BLOCK_END`, and `ARG`. Helpers `my_strdup` and `my_qstrdup` duplicate unquoted and quoted arguments.

Control flow: comments and whitespace are ignored. Seeing `=` switches to an `arg` start condition so the rest of the value line is captured as one argument, with quoted empty strings represented as NULL.

State and persistence behavior: lexer state is generated flex state plus allocated `ARG` strings passed to parser actions, which are responsible for freeing them. It does not persist configuration itself.

Dependencies and integration points: includes generated `conf-parse.h`; compiled by `src/Makefile` before the parser object; consumed exclusively by `conf-parse.y`.

Risks: unquoted argument trimming mutates the matched buffer before duplicating; quoted values do not trim internal whitespace. Test signals include quoted empty values, comments, unknown characters, all recognized option tokens, and scanner destruction after parsing.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/conf-scan.l -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/context_record.c -->

# sources/security-integrity/selinux/libsemanage/src/context_record.c

Purpose: implements public semanage context helpers as wrappers around libsepol security-context records.

Important APIs/types/functions: exports getters/setters for user, role, type, MLS range, create/clone/free, `semanage_context_from_string`, and `semanage_context_to_string`.

Control flow: field operations delegate to `sepol_context_*` with `handle->sepolh`. String parsing creates a context from a SELinux context string; serialization returns an allocated string for the caller.

State and persistence behavior: contexts are heap objects embedded in higher-level records such as file contexts, ports, nodes, interfaces, and InfiniBand records. They are persisted only when their owning record is written to a backend.

Dependencies and integration points: depends on libsepol context APIs and semanage handles. It is a shared building block across most context-bearing record types.

Risks: getter pointers are borrowed; setters can fail on allocation or invalid components. Test signals include string round trips, clone independence, MLS handling, and cleanup of nested contexts in owning records.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/context_record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database.c -->

# sources/security-integrity/selinux/libsemanage/src/database.c

Purpose: provides generic public-facing database wrappers that enforce initialization, cache entry, and read/write transaction mode before dispatching to backend method tables.

Important APIs/types/functions: internal `assert_init`, `enter_ro`, `exit_ro`, and `enter_rw`; exported wrappers `dbase_modify`, `dbase_set`, `dbase_del`, `dbase_query`, `dbase_exists`, `dbase_count`, `dbase_iterate`, and `dbase_list`.

Control flow: write wrappers enter read-write mode, which implicitly begins a transaction, caches the backend, and dispatches. Read wrappers enter read-only mode, cache the backend, dispatch, and then call `semanage_exit_read_lock`.

State and persistence behavior: wrapper calls can populate backend caches and mark them modified through backend operations. Actual persistence occurs later via backend flush during commit.

Dependencies and integration points: sits between every object-specific API and file/policydb/active/join backends. Relies on handle transaction/read-lock helpers and `dbase_config_t` method tables.

Risks: incorrect dconfig initialization is fatal to all callers. Iteration has documented reentrancy restrictions. Test signals include implicit transaction start for writes, read lock balancing on errors, cache refresh behavior, and generic error propagation.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database.h -->

# sources/security-integrity/selinux/libsemanage/src/database.h

Purpose: defines libsemanage's generic record and database polymorphism interfaces.

Important APIs/types/functions: declares opaque `record_t`, `record_key_t`, and `dbase_t`; `record_table_t` for create/key/compare/clone/free operations; `dbase_table_t` for CRUD, iteration/listing, cache/drop/flush, modification status, and record-table retrieval; `dbase_config_t`; and generic wrapper prototypes.

Control flow: each object/backend pair supplies record and database method tables. Public object APIs call the generic wrappers with a configured backend, which call method-table operations after cache/transaction setup.

State and persistence behavior: the header specifies ownership: keys and input data remain caller-owned, query/list results become caller-owned, and caches belong to backends. Persistence semantics are delegated to each backend's `flush` implementation.

Dependencies and integration points: included by every backend and internal object implementation. It is the architectural center that lets booleans, users, ports, nodes, and other records share file, policydb, join, and active database logic.

Risks: method tables are ABI-internal but semantically strict; a bad comparator or clone routine can corrupt list ordering or ownership. Test signals include generic CRUD conformance across all backends and memory ownership under error paths.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database_activedb.c -->

# sources/security-integrity/selinux/libsemanage/src/database_activedb.c

Purpose: implements a generic active-state database backend using the linked-list cache machinery plus record-specific read and commit callbacks.

Important APIs/types/functions: `dbase_activedb_cache`, `dbase_activedb_flush`, `dbase_activedb_init`, `dbase_activedb_release`, and `SEMANAGE_ACTIVEDB_DTABLE`.

Control flow: cache calls the record active table's `read_list`, prepends each returned record into the linked-list cache, frees the temporary array, and records the current serial. Flush lists cached records and calls `commit_list`, then clears the modified flag.

State and persistence behavior: caches active records in memory; flush writes the active backend's complete list to runtime state. There is no file path or policydb persistence in this generic layer.

Dependencies and integration points: depends on `database_llist` for CRUD/list/cache management and a `record_activedb_table_t` supplied by object-specific code such as active booleans.

Risks: full-list flush semantics can lose concurrent active changes. Test signals include cache load, modify then flush, drop/reload, and cleanup on partial cache failures.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database_activedb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database_activedb.h -->

# sources/security-integrity/selinux/libsemanage/src/database_activedb.h

Purpose: declares the generic active database adapter interface.

Important APIs/types/functions: defines `record_activedb_table_t` with `read_list` and `commit_list` callbacks, opaque `dbase_activedb_t`, init/release functions, and `SEMANAGE_ACTIVEDB_DTABLE`.

Control flow: object-specific code supplies callbacks, initializes an active database, and then uses normal generic database wrappers through the returned table.

State and persistence behavior: the adapter owns an in-memory list cache and delegates persistence to `commit_list`, usually affecting live kernel or process state rather than store files.

Dependencies and integration points: includes `database.h` and internal `handle.h`; used by active boolean support.

Risks: callback ownership of arrays and records must match the adapter's expectations. Test signals include backend init/release and full list commit behavior.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database_activedb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database_file.c -->

# sources/security-integrity/selinux/libsemanage/src/database_file.c

Purpose: implements a generic line-oriented file database backend on top of the linked-list cache.

Important APIs/types/functions: `dbase_file_cache`, `dbase_file_flush`, `dbase_file_init`, `dbase_file_release`, and `SEMANAGE_FILE_DTABLE`.

Control flow: cache opens the read-only path if present, creates records via the record table, repeatedly calls the record file parser until `STATUS_NODATA`, and prepends parsed records into the cache. Flush opens the writable path and prints each cached record through the record file table.

State and persistence behavior: caches file records in memory with modification tracking. Flush rewrites the writable database file, so output ordering and complete-list printing define persistence.

Dependencies and integration points: uses `parse_utils`, `database_llist`, debug reporting, stdio, and object-specific parse/print tables such as booleans and other local store record files.

Risks: parser errors abort cache construction; flush failures can leave persistent files stale or partially written depending on file handling. Test signals include missing read-only files, malformed lines, successful rewrite, and cache serial resync.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database_file.h -->

# sources/security-integrity/selinux/libsemanage/src/database_file.h

Purpose: declares the generic file-backed database interface.

Important APIs/types/functions: `record_file_table_t` supplies a `parse` callback from `parse_info_t` into a record and a `print` callback from record to `FILE *`; `dbase_file_init`, `dbase_file_release`, and `SEMANAGE_FILE_DTABLE` expose the backend.

Control flow: object-specific code combines its generic `record_table_t` with a file parse/print table, then generic CRUD operates against the linked-list cache and flushes through the printer.

State and persistence behavior: file backends persist complete record sets to writable text files and cache parsed read-only contents in memory.

Dependencies and integration points: includes stdio, `parse_utils.h`, `database.h`, and internal `handle.h`. Used for local customizations such as booleans and other semanage text databases.

Risks: parse callbacks must return `STATUS_NODATA` on EOF and handle NULL streams. Test signals are parser/printer round trips and robust handling of empty or absent files.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database_join.c -->

# sources/security-integrity/selinux/libsemanage/src/database_join.c

Purpose: implements a virtual database that joins two component databases into one record view and splits modifications back into the components.

Important APIs/types/functions: `dbase_join_cache`, `dbase_join_flush`, `dbase_join_init`, `dbase_join_release`, and `SEMANAGE_JOIN_DTABLE`; uses a `record_join_table_t` with `join` and `split` callbacks.

Control flow: cache loads both component databases, merges ordered records by key, joins matching or single-sided entries, and stores joined records in a linked-list cache. Flush splits each joined record into component records, clears the component databases, repopulates them, and flushes components separately.

State and persistence behavior: the join cache is derived state. Persistence happens only through split records written to the underlying component dbases during flush.

Dependencies and integration points: depends on `database_llist`, generic component `dbase_config_t`s, and record comparators. Used where public records span base and extra local data, notably SELinux users.

Risks: comparator consistency across joined record types is essential. Split/flush errors can leave component caches modified but not durable. Test signals include one-sided joins, matching joins, sorted list output, component clear/repopulate, and rollback/drop-cache behavior.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database_join.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database_join.h -->

# sources/security-integrity/selinux/libsemanage/src/database_join.h

Purpose: declares the generic virtual join database interface.

Important APIs/types/functions: defines placeholder `record1_t` and `record2_t`, opaque `dbase_join_t`, `record_join_table_t` callbacks `join` and `split`, `dbase_join_init`, `dbase_join_release`, and `SEMANAGE_JOIN_DTABLE`.

Control flow: object-specific code supplies two component database configs and callbacks that can combine or split records. Generic database wrappers then expose the joined view as if it were a normal database.

State and persistence behavior: the join database caches synthesized records; persistent writes are delegated back into the two component databases on flush.

Dependencies and integration points: includes `database.h` and `handle.h`. It supports composite record models while preserving existing file/policydb backends.

Risks: callbacks must tolerate NULL component records and preserve key ordering. Test signals include joins with missing left/right sides and successful split persistence.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database_join.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database_llist.c -->

# sources/security-integrity/selinux/libsemanage/src/database_llist.c

Purpose: provides the common in-memory linked-list cache implementation for generic database backends.

Important APIs/types/functions: implements cache prepend/drop/resync serial, exists/add/set/modify/count/query/iterate/delete/clear/list, and helper cache lookup over `cache_entry_t` nodes.

Control flow: operations locate records by comparator, clone input records into cache entries, update links and size, mark modification state, and return cloned records for query/list. `add` prepends without duplicate checks; `modify` replaces or adds; `set` requires existing records.

State and persistence behavior: owns cloned record data in linked nodes, cache size, cache serial, and modified flag. It does not write durable storage; higher backends use it before flushing to files, active state, or policydb.

Dependencies and integration points: used by file, active, join, and policydb caching paths. Relies on object-specific record tables for clone, free, and comparison semantics.

Risks: list mutation and ownership are central; double-free or stale links would affect every backend. Test signals include CRUD ordering, modified flag transitions, query/list clone ownership, delete head/tail/middle cases, and cache drop cleanup.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database_llist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database_llist.h -->

# sources/security-integrity/selinux/libsemanage/src/database_llist.h

Purpose: declares the linked-list cache structure and helpers shared by multiple database backends.

Important APIs/types/functions: defines `cache_entry_t`, `dbase_llist_t`, inline init/modified/rtable helpers, and exported cache/drop/CRUD/list functions.

Control flow: backend init embeds or allocates a `dbase_llist_t`, initializes it with a record table and dbase table, then delegates generic operations to this helper layer.

State and persistence behavior: tracks `cache`, `cache_tail`, `cache_sz`, `cache_serial`, and `modified`. Persistent storage is outside this layer; serials detect resync needs after commits.

Dependencies and integration points: includes `database.h` and `handle.h`; used by `database_file.c`, `database_activedb.c`, `database_join.c`, and `database_policydb.c`.

Risks: all callers depend on consistent modified and serial behavior. Test signals include init/drop idempotence, serial refresh, and cache size correctness after each mutation.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database_llist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database_policydb.c -->

# sources/security-integrity/selinux/libsemanage/src/database_policydb.c

Purpose: implements a generic policydb backend, adapting object-specific libsepol policydb operations to the semanage database interface.

Important APIs/types/functions: cache/drop/set-serial/needs-resync/flush/init/release/attach/detach helpers; generic add/set/modify/delete/clear/query/exists/count/iterate/list operations; `SEMANAGE_POLICYDB_DTABLE`.

Control flow: cache creates and reads a `sepol_policydb_t` from paths when not attached, iterates object records into the linked-list cache, and tracks serials. During commit, attach binds the backend to a shared output policydb; operations call record policydb callbacks and update the cache. Detach drops attachment state.

State and persistence behavior: owns optional cached policydb, linked-list cache, modification flag, path references, and attach state. Flush writes changes into the policydb object; writing policy files is handled elsewhere.

Dependencies and integration points: depends on libsepol policydb APIs, generic linked-list caching, semanage path/serial logic, and object-specific `record_policydb_table_t` implementations.

Risks: attached mode intentionally prevents normal drop/flush assumptions; incorrect detach could leave dangling policydb pointers. Test signals include file-backed policy reads, attached merge behavior, count/list/query accuracy, and resync after commit serial changes.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database_policydb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database_policydb.h -->

# sources/security-integrity/selinux/libsemanage/src/database_policydb.h

Purpose: declares the generic policydb adapter API and object-specific policydb method table shape.

Important APIs/types/functions: defines `record_policydb_table_t` callbacks for add, modify, set, query, count, exists, and iterate over `sepol_policydb_t`; declares `dbase_policydb_init`, `attach`, `detach`, `release`, and `SEMANAGE_POLICYDB_DTABLE`.

Control flow: object-specific policydb code supplies callback tables; the generic backend handles caching, attachment, and common database semantics.

State and persistence behavior: backend state can be path-backed or attached to a shared in-memory policydb. Persistence to disk is indirect through direct API policy writes.

Dependencies and integration points: includes libsepol handle/policydb headers plus semanage database and handle internals. Used by booleans and other policy-backed record families.

Risks: callbacks must be consistent with generic record comparison and clone semantics. Test signals include policydb adapter initialization for each record family and attach/detach during direct commit.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/database_policydb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/debug.c -->

# sources/security-integrity/selinux/libsemanage/src/debug.c

Purpose: implements public and internal message handlers for libsemanage diagnostics.

Important APIs/types/functions: exports `semanage_msg_get_level`, `get_channel`, `get_fname`, `semanage_msg_default_handler`, and `semanage_msg_relay_handler`.

Control flow: getters read the message metadata currently stored on the semanage handle. The default handler formats messages to stderr with level/channel/function context. The relay handler receives libsepol messages and forwards them through semanage's callback mechanism.

State and persistence behavior: only transient per-handle message metadata is read or written. The implementation preserves `errno` through macro emission in internal headers.

Dependencies and integration points: works with public `semanage/debug.h`, internal `debug.h`, libsepol debug callbacks, and any application-installed callback.

Risks: formatting code runs during error paths and must avoid clobbering diagnostics. Test signals include default output for each level, relay from sepolh, NULL callback suppression, and getter values inside callbacks.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/debug.h -->

# sources/security-integrity/selinux/libsemanage/src/debug.h

Purpose: internal debug and status helper header for libsemanage implementation files.

Important APIs/types/functions: defines status constants `STATUS_SUCCESS`, `STATUS_ERR`, and `STATUS_NODATA`; macro `msg_write`; convenience macros `ERR`, `INFO`, and `WARN`; and declarations for default and relay handlers.

Control flow: implementation files call `ERR(handle, ...)` and related macros. The macro stores message metadata on the handle, invokes the configured callback, and restores `errno` afterward.

State and persistence behavior: affects only handle message fields and callbacks; no store persistence.

Dependencies and integration points: includes public debug API, libsepol debug, errno, stdio, and internal handle layout. Used broadly by parser, database, and direct API code.

Risks: macros require a valid internal handle pointer and use `__FUNCTION__`. Test signals are preserved `errno`, correct metadata, and no callback call when suppressed.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/direct_api.c -->

# sources/security-integrity/selinux/libsemanage/src/direct_api.c

Purpose: implements the direct libsemanage backend that manipulates the local SELinux policy module store, transaction sandbox, module files, linked/kernel policy artifacts, local customizations, validation, and install/reload behavior.

Important APIs/types/functions: defines the direct backend policy table; connection/management/access functions; lock cleanup; transaction begin; module install, install_file, extract, remove, list, enable, info, list_all, install_info, and remove_key operations; HLL-to-CIL compilation helpers; checksum comparison/writing; and the large `semanage_direct_commit` policy rebuild/install pipeline.

Control flow: `semanage_direct_connect` loads config, validates/creates store layout, initializes local/policy/active databases, and installs the direct method table. Begin transaction copies active store state into a sandbox and takes the transaction lock. Module operations write, remove, or inspect module files inside the sandbox and mark modules modified. Commit flushes composite local data, decides whether rebuild is needed from explicit flags, module changes, checksums, missing computed files, and local changes, compiles HLL modules when needed, loads CIL into a CIL DB, builds a libsepol policydb, emits file contexts/seusers/user extras, attaches policydb-backed dbases, merges local components, validates file contexts, seusers, ports, ibpkeys, and ibendports, writes policy and auxiliary files, optionally runs genhomedircon, installs the sandbox, reloads policy when configured, removes temporaries, detaches dbases, and releases locks.

State and persistence behavior: manages active store files, sandbox temporary directories, lock file descriptors, module payloads by priority/name/lang extension, checksum files, linked and kernel policy files, file_contexts, seusers, users_extra, generated homedir contexts, and local customization databases. Persistent changes are staged in the sandbox and installed atomically by the direct backend rather than written immediately by individual API calls.

Dependencies and integration points: integrates libsepol, CIL, libselinux paths and reloads, module compression, HLL compiler discovery, external verifier programs from semanage.conf, generic database backends, component merge/validate helpers, file copying, checksums, and public module/handle APIs.

Risks: this is the highest-blast-radius file in the subset. Risks include lock leaks, stale sandbox cleanup, process-global umask changes, checksum false negatives, HLL compiler subprocess failures, partial install or validation failures, attached policydb lifetime mistakes, concurrent store mutation, and subtle rebuild-skip decisions. Test signals include transaction lock behavior, module install/remove/list/extract, enable toggles, checksum-based rebuild skipping, external verifier failure handling, commit rollback/cleanup, generated file contexts/seusers correctness, genhomedircon output, policy reload controls, and sanitizer/leak coverage on every cleanup path.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/direct_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/direct_api.h -->

# sources/security-integrity/selinux/libsemanage/src/direct_api.h

Purpose: declares the internal direct-store backend entry points and direct handle extension.

Important APIs/types/functions: `struct semanage_direct_handle` stores active and transaction lock file descriptors; declares `semanage_direct_connect`, `semanage_direct_is_managed`, `semanage_direct_access_check`, and `semanage_direct_mls_enabled`.

Control flow: handle connection code selects the direct backend, allocates direct state, acquires locks as needed, and dispatches through the direct policy table implemented in `direct_api.c`.

State and persistence behavior: the direct handle tracks lock file descriptors protecting active store and transaction state. Persistent behavior is implemented in the direct backend's sandbox, module, and commit functions.

Dependencies and integration points: included by handle internals and `direct_api.c`. It is the direct backend counterpart to the public store selection API.

Risks: lock descriptor lifecycle must match connect/disconnect and transaction boundaries. Test signals include is-managed checks, access checks, lock release on disconnect, and MLS detection.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/direct_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/exception.sh -->

# sources/security-integrity/selinux/libsemanage/src/exception.sh

Purpose: generates SWIG Python exception wrappers for libsemanage functions that return negative integer error codes.

Important APIs/functions: shell function `except` emits a `%exception` block; the script compiles `../include/semanage/semanage.h` with `-aux-info`, falls back from `$CC` to `gcc`, extracts `extern int` function names with awk, emits wrappers, and removes temporary files.

Control flow: `src/Makefile` runs this script to produce `semanageswig_python_exception.i`. Each discovered integer-returning function gets a wrapper that checks `result < 0`, raises `PyErr_SetFromErrno(PyExc_OSError)`, and calls `SWIG_fail`.

State and persistence behavior: writes generated SWIG interface text to stdout and temporary `temp.o`/`temp.aux` files in the working directory, then deletes them.

Dependencies and integration points: depends on a compiler supporting GCC `-aux-info` or fallback gcc, public umbrella header completeness, awk, shell, Python/SWIG generated bindings.

Risks: clang fallback depends on gcc availability; parsing compiler aux output is fragile and may miss or mis-handle signatures. Test signals include generated exception file containing all public `extern int` APIs and successful SWIG Python build.

<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/exception.sh -->
