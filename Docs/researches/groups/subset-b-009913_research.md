# Research: subset-b-009913

Grouped research for Samba source4 DSDB LDB modules covering OID resolution, RID allocation, RootDSE behavior, Samba3 compatibility mapping, Samba3 SID allocation, DSDB module-stack construction, and secrets.ldb module-stack construction. Each section preserves the source path and is wrapped for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/resolve_oids.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/resolve_oids.c

## Purpose
`resolve_oids.c` implements the `resolve_oids` LDB module. Its job is to accept LDAP filters, requested attribute lists, add messages, and modify messages that use numeric schema OIDs for selected schema attributes, then rewrite them to Samba DSDB `lDAPDisplayName` forms before passing the request down the module stack. This mainly supports schema-related attributes where clients may refer to classes or attributes by OID but the database stores and indexes display names.

## Important APIs, Types, And Functions
The detection path is split from the mutation path. `resolve_oids_need_value()` checks whether a value looks like an OID and resolves it against the in-memory `dsdb_schema` for class-valued attributes such as `objectClass`, `subClassOf`, `auxiliaryClass`, `systemPossSuperiors`, and `possSuperiors`, or attribute-valued attributes such as `systemMustContain`, `systemMayContain`, `mustContain`, and `mayContain`. `resolve_oids_parse_tree_need()`, `resolve_oids_element_need()`, and `resolve_oids_message_need()` recursively determine whether a search tree or message requires rewriting.

`resolve_oids_replace_value()` performs the value rewrite from class `governsID` OID or attribute `attributeID` OID to the resolved `lDAPDisplayName`. `resolve_oids_parse_tree_replace()`, `resolve_oids_element_replace()`, and `resolve_oids_message_replace()` rewrite attribute names and values in shallow copies. The public module operations are `resolve_oids_search()`, `resolve_oids_add()`, and `resolve_oids_modify()`, registered by `ldb_resolve_oids_module_init()`.

## Control Flow
For search requests, the module exits early if no schema is loaded or if the base DN is special. It first scans the parse tree for OID-looking attribute names or values that the schema can resolve, then scans the requested attribute list for numeric attribute OIDs. If no rewrite is needed, the original request is passed through unchanged. Otherwise the module creates a `resolve_oids_context`, shallow-copies the parse tree and attribute list, keeps the schema alive with a talloc reference, rewrites the copied tree and attributes, builds a replacement search request, and proxies replies through `resolve_oids_callback()`.

Add and modify paths follow the same pattern: skip when no schema or special DN, scan the message for resolvable OID values, shallow-copy the message, rewrite element names and values in the copy, build a replacement add or modify request, and pass it down. Replies are forwarded as entries, referrals, or done replies without additional transformation.

## State And Persistence
The module has no persistent state. It uses request-scoped talloc allocations and references the current DSDB schema. Persistent effects happen only in lower modules after the rewritten add or modify request succeeds. The code intentionally avoids rewriting special control entries.

## Dependencies And Integration Points
This module depends on `dsdb_get_schema()`, `dsdb_attribute_by_attributeID_oid()`, `dsdb_attribute_by_lDAPDisplayName()`, `dsdb_class_by_governsID_oid()`, schema `attributeID_id` constants from DRSUAPI, LDB parse-tree structures, and LDB request builders. It is placed early in the Samba DSDB stack by `samba_dsdb.c`, before `rootdse` and schema-loading dependent modules, so later modules see canonical display-name attributes and values.

## Risks And Test Signals
The main risk is silent pass-through when an OID cannot be resolved: invalid OIDs remain unchanged and later modules decide whether to reject them. Rewriting is limited to syntax `oMSyntax == 6` and a fixed set of attribute IDs, so new schema attributes that also need OID-to-name conversion require code changes. The shallow-copy approach relies on replacement values pointing at schema-owned strings whose lifetime is protected by the talloc reference. Tests should cover search filters with OID attribute names, equality and comparison values, requested attribute OIDs, add/modify messages using class and attribute OIDs, unknown OIDs, special DNs, missing schema, and ensuring values for `governsID`, `attributeID`, and `attributeSyntax` are not incorrectly rewritten.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/resolve_oids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/ridalloc.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/ridalloc.c

## Purpose
`ridalloc.c` implements helper routines for RID Set and RID Manager handling in the Samba AD DC. It allocates individual RIDs from the local DC's RID Set, creates RID Set objects when needed, obtains fresh RID pools from the RID Manager FSMO, and services the DRS extended operation used by a RID Manager to allocate pools for another DC.

## Important APIs, Types, And Functions
`struct ridalloc_ridset_values` is the local normalized form of `rIDAllocationPool`, `rIDPreviousAllocationPool`, `rIDNextRID`, and `rIDUsedPool`. `ridalloc_get_ridset_values()` reads those fields from an LDB message, while `ridalloc_set_ridset_values()` emits constrained updates with `dsdb_msg_constrainted_update_uint64()` and `dsdb_msg_constrainted_update_uint32()`, omitting unchanged or absent sentinel values.

`ridalloc_poke_rid_manager()` sends `MSG_DREPL_ALLOCATE_RID` to the local `dreplsrv` service so replication can ask the remote RID Manager for a new pool asynchronously. `ridalloc_rid_manager_allocate()` consumes 500 RIDs from `rIDAvailablePool` on the RID Manager object using a constrained update. `ridalloc_create_rid_set_ntds()` creates a `CN=RID Set` child under a DC machine account and links it through `rIDSetReferences`. Public helpers include `ridalloc_create_own_rid_set()`, `ridalloc_new_own_pool()`, `ridalloc_allocate_rid()`, and `ridalloc_allocate_rid_pool_fsmo()`.

## Control Flow
Individual RID allocation starts in `ridalloc_allocate_rid()`. It locates this DC's RID Set with `samdb_rid_set_dn()` and creates it if the reference is missing. It reads the current RID Set values, initializes `rIDPreviousAllocationPool` and `rIDNextRID` on first use, increments `rIDNextRID` on subsequent use, and switches to `rIDAllocationPool` when the previous pool is exhausted. If no standby pool is available, it calls `ridalloc_new_own_pool()`; that routine either updates locally when this DC owns the RID Manager FSMO or pokes `dreplsrv` and returns `LDB_ERR_UNWILLING_TO_PERFORM`.

When the active pool is more than half exhausted and no standby pool exists, `ridalloc_allocate_rid()` proactively tries to obtain a standby pool. A remote-manager `LDB_ERR_UNWILLING_TO_PERFORM` is treated as non-fatal in this early-refresh case because the asynchronous poke has been sent. The final RID Set update is a constrained modify as system, which protects against lost updates if another allocator changed the same values.

`ridalloc_allocate_rid_pool_fsmo()` is the remote-allocation path called by the DRS `DSDB_EXTENDED_ALLOCATE_RID_POOL` operation. It resolves the destination DSA GUID to an NTDS object, finds the server's machine account, creates the RID Set if missing, validates optional `fsmo_info` against the current allocation pool for idempotence, takes a new pool from the RID Manager, and writes it into the remote DC's RID Set.

## State And Persistence
Persistent state lives in directory objects: the RID Manager's `rIDAvailablePool`, each DC machine account's `rIDSetReferences`, and each RID Set's allocation fields. The file itself stores no durable process state. Messaging to `dreplsrv` is asynchronous and advisory; the database changes are made through LDB constrained updates and `DSDB_FLAG_AS_SYSTEM` where ownership or security descriptors matter.

## Dependencies And Integration Points
The code depends on DSDB module helper APIs, Samba messaging and IRPC (`imessaging_client_init()`, `irpc_servers_byname()`, `imessaging_send()`), loadparm context, GUID/NTDS helpers, RID Manager DN helpers, and DRS FSMO extended-operation types. It integrates with `samldb` for object creation that needs RIDs, with replication for remote pool requests, and with the RID Manager FSMO ownership model.

## Risks And Test Signals
RID allocation correctness depends on constrained updates and retry behavior in callers; this file returns conflicts/errors but does not loop internally. `ridalloc_rid_manager_allocate()` allocates fixed 500-RID pools and must correctly pack low/high 32-bit halves. Edge cases include exhausted `rIDAvailablePool`, missing `serverReference`, missing or corrupt RID Set attributes, stale NTDS GUID cache, remote RID Manager unavailability, and idempotent DRS retries with `fsmo_info`. Tests should simulate first RID allocation, pool rollover, half-pool refresh, local versus remote FSMO behavior, RID Set creation security, `rIDAvailablePool` exhaustion, constrained-update conflicts, and DRS remote allocation for both new and existing RID Sets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/ridalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/rootdse.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/rootdse.c

## Purpose
`rootdse.c` implements Samba's `rootdse` LDB module. It virtualizes the LDAP RootDSE entry, filters controls and unauthenticated operations, maintains registered controls and partitions for RootDSE output, handles selected RootDSE modify commands such as schema refresh and FSMO transfer, and wraps transactions to keep long-running asynchronous RootDSE operations from blocking the main event loop.

## Important APIs, Types, And Functions
`struct rootdse_private_data` stores registered control OIDs, naming context DNs, anonymous-operation policy, and transaction event-context state. `struct rootdse_context` carries the original request plus an optional packed NetLogon response. Attribute helpers `do_attribute()` and `do_attribute_explicit()` decide whether dynamic attributes should be returned.

`rootdse_add_dynamic()` is the central RootDSE result decorator. It adds dynamic values such as `serverName`, `dnsHostName`, `ldapServiceName`, `currentTime`, `supportedControl`, `namingContexts`, `supportedSASLMechanisms`, `highestCommittedUSN`, schema counts, `validFSMOs`, `vendorVersion`, functionality levels, `isGlobalCatalogReady`, `tokenGroups`, and `netlogon`. It also expands DN-valued attributes for the extended-DN control. Request path functions include `rootdse_search()`, `rootdse_add()`, `rootdse_modify()`, `rootdse_rename()`, `rootdse_delete()`, `rootdse_extended()`, and `rootdse_request()`. Special command helpers include `rootdse_schemaupdatenow()`, `rootdse_enableoptionalfeature()`, `rootdse_enable_recycle_bin()`, `rootdse_schemaupgradeinprogress()`, and `rootdse_become_master()`.

## Control Flow
Every public operation first applies `rootdse_filter_operations()` and `rootdse_filter_controls()` where appropriate. Untrusted anonymous callers can only perform base searches on the null DN when blocking is enabled. Untrusted clients lose non-critical unregistered controls and receive `LDB_ERR_UNSUPPORTED_CRITICAL_EXTENSION` for critical unregistered controls. Registered critical controls are made non-critical except DIRSYNC, VLV, and server-side sort, because those modules must see and consume criticality themselves.

RootDSE search only intercepts base searches on the null DN. It optionally handles explicit `netlogon` requests by parsing the filter and constructing a CLDAP-style NetLogon blob, then searches the stored `@ROOTDSE` record and decorates the reply in `rootdse_callback()`. Searches for other bases pass through unchanged.

RootDSE add, rename, and delete reject operations directly targeting the null DN and pass non-null DNs down. RootDSE modify dispatches by attribute name: `schemaUpdateNow` calls the DSDB schema refresh extended operation, `become*` attributes trigger asynchronous FSMO role transfer through `dreplsrv`, `enableOptionalFeature` currently supports recycle bin enablement, and `schemaUpgradeInProgress` returns success as a placeholder for connection-level relaxed constraints. Unknown RootDSE modify attributes fail with unwilling-to-perform.

Transactions are wrapped by `rootdse_start_trans()`, `rootdse_end_trans()`, and `rootdse_del_trans()`. On transaction start, the module creates a private event context and installs it into the LDB context. FSMO transfer deliberately deletes the transaction, switches the request handle to the global event context, sends an async IRPC `drepl_takeFSMORole` request, and restarts a transaction in the completion callback so surrounding wrappers can finish cleanly.

## State And Persistence
Registered controls and partitions are process-local module private state populated by LDB internal register requests. Functionality-level values are cached in LDB opaques during init after reads from the default NC, partitions object, and local NTDS settings. Durable changes occur when RootDSE commands call lower modules: recycle bin enablement modifies `msDS-EnabledFeature` on the NTDS settings object and requested scope, schema refresh updates schema state through an extended operation, and FSMO transfer is delegated to `dreplsrv`.

## Dependencies And Integration Points
The module integrates with authentication session info, security-token checks, DSDB module search/modify helpers, CLDAP NetLogon parsing and response packing, loadparm, tsocket remote-address state, schema and functional-level helpers, LDB registered-control/partition operations, extended-DN controls, Samba IRPC messaging, and DRS role-transfer RPC. `samba_dsdb.c` places this module near the front of the DSDB stack because RootDSE request interception and control filtering must happen before most backend modules.

## Risks And Test Signals
Risk areas include access-control filtering for untrusted requests, accidental exposure of internal controls, RootDSE dynamic attribute parity with AD clients, extended-DN expansion failure behavior, event-context restoration on transaction errors, and asynchronous FSMO transfer cleanup. `dsdb_module_we_are_master()` reads `fSMORoleOwner` but calls `samdb_dn_is_our_ntdsa()` on the role object DN rather than the local owner DN, so FSMO reporting deserves targeted regression coverage. Tests should cover anonymous base search versus other operations, registered and unregistered critical controls, RootDSE dynamic attributes with explicit and wildcard attr lists, netlogon filter handling, schemaUpdateNow opaque reset on failure, recycle-bin permission and functional-level checks, RODC rejection for FSMO transfer, and transaction event-context restoration across success and failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/rootdse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/samba3sam.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/samba3sam.c

## Purpose
`samba3sam.c` implements the `samba3sam` LDB map module, a compatibility layer that presents Samba4-style SAM attributes over a Samba3 LDAP backend schema. It maps object classes, renames attributes, converts SID and password-hash formats, generates primary group fields, and ignores many AD-only attributes that cannot be represented in the Samba3 schema.

## Important APIs, Types, And Functions
Conversion helpers include `generate_primaryGroupID()` and `generate_sambaPrimaryGroupSID()` for translating between `primaryGroupID` and `sambaPrimaryGroupSID`; `convert_uid_samaccount()` for `sAMAccountName` from `uid`; `lookup_homedir()`, `lookup_gid()`, and `lookup_uid()` for POSIX passwd-derived fields; `encode_sid()` and `decode_sid()` for textual `sambaSID` to binary `objectSid`; and `bin2hex()`/`hex2bin()` for Samba password hashes.

`samba3_objectclasses[]` maps local classes such as `user`, `group`, and `domain` to remote `posixAccount`, `posixGroup`, `sambaGroupMapping`, `sambaSAMAccount`, and `sambaDomain`. `samba3_attributes[]` is the main mapping table, using `LDB_MAP_RENAME`, `LDB_MAP_CONVERT`, `LDB_MAP_GENERATE`, `LDB_MAP_KEEP`, and `LDB_MAP_IGNORE`. `samba3sam_init()` calls `ldb_map_init()`. The file also registers `show_deleted_ignore`, a small test-support module that marks show-deleted and show-recycled controls non-critical before passing searches down.

## Control Flow
The runtime control flow is mostly supplied by the generic `ldb_map` framework. During module init, Samba registers the object-class and attribute maps under the `samba3sam` name. For mapped searches and updates, the framework invokes the declared converters and generators. SID conversions use NDR push/pull of `struct dom_sid`; password conversions use smbpasswd helper functions for 16-byte hash to 32-hex-character conversion.

Generated `primaryGroupID` parses the RID suffix from `sambaPrimaryGroupSID`. Generated `sambaPrimaryGroupSID` pulls the domain SID from binary `objectSid`, removes the final RID authority, and appends `primaryGroupID`. POSIX-derived conversions call `getpwnam()` based on `unixName`/`uid` input and return empty values on lookup failure.

## State And Persistence
The module itself has no durable state. Persistent reads and writes go to the remote Samba3-compatible LDAP backend through the mapping layer. Conversion outputs are request-scoped talloc values. Calls to `getpwnam()` depend on local NSS state, so results can vary with system account configuration rather than directory contents alone.

## Dependencies And Integration Points
This file depends on `ldb_map`, POSIX passwd APIs, NDR security structures, DOM SID utilities, SAMR password hash structures, and Samba3 helper functions. It integrates with tests and migration paths that need Samba4 LDAP semantics over old Samba3 schemas rather than the normal DSDB module stack.

## Risks And Test Signals
The largest risks are lossy mappings and local NSS dependency. Many AD attributes are ignored, so callers may believe writes succeeded even though the Samba3 backend cannot persist the fields. `generate_sambaPrimaryGroupSID()` mutates the decoded SID by decrementing `num_auths`, which assumes a normal domain SID plus RID layout. Password hash conversion must reject malformed lengths and invalid hex. Tests should cover object-class mapping, SID encode/decode, primary group generation in both directions, hash conversion round-trips, missing `getpwnam()` entries, ignored attribute behavior, and show-deleted/show-recycled control criticality handling for the test module.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/samba3sam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/samba3sid.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/samba3sid.c

## Purpose
`samba3sid.c` implements the `samba3sid` LDB module. It auto-populates `sambaSID` on added Samba3-style `posixAccount` and `posixGroup` entries by allocating the next RID from a `sambaDomain` object's legacy RID counters.

## Important APIs, Types, And Functions
`samba3sid_next_sid()` searches all partitions for the single `sambaDomain` matching the configured SAM name, reads `sambaNextRid`, `sambaNextUserRid`, `sambaNextGroupRid`, and `sambaSID`, picks the highest available counter, increments it, builds a textual SID, and constrained-updates `sambaNextRid`. `samba3sid_add()` intercepts add requests, filters out special DNs and non-user/group object classes, skips entries that already have `sambaSID`, shallow-copies the add message, adds the generated `sambaSID`, and builds a replacement add request.

## Control Flow
On add, the module only acts for entries with `objectClass=posixAccount` or `objectClass=posixGroup` and without a supplied `sambaSID`. SID generation searches for exactly one domain object. It treats `sambaNextRid` as the previous RID, following the legacy Samba3 passdb algorithm, and updates only `sambaNextRid` after choosing the new RID. The modified add request uses `dsdb_next_callback()` to forward completion.

## State And Persistence
Persistent state is the Samba3 domain object's RID counter and the new entry's `sambaSID`. The counter update uses `dsdb_module_constrainted_update_uint32()` to guard against concurrent updates of `sambaNextRid`. The module itself has no private persistent state.

## Dependencies And Integration Points
The module depends on DSDB module search/update helpers, loadparm `lpcfg_sam_name()`, Samba security SID string conventions, and LDB add request builders. It is intended for Samba3 LDAP compatibility stacks rather than normal AD RID allocation; normal AD allocations use `ridalloc.c`.

## Risks And Test Signals
The compatibility algorithm only updates `sambaNextRid`, even when `sambaNextUserRid` or `sambaNextGroupRid` supplied the highest value, matching legacy behavior but worth preserving explicitly. It requires exactly one matching `sambaDomain`, a valid `sambaSID`, and at least one RID counter. Tests should cover supplied SID pass-through, non-user/group pass-through, missing domain, multiple domains, missing counters, constrained-update conflicts, highest-counter selection, and concurrent add attempts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/samba3sid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/samba_dsdb.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/samba_dsdb.c

## Purpose
`samba_dsdb.c` implements the bootstrap LDB module that constructs Samba's full DSDB module chain at runtime. It lets provisioned databases keep a stable top-level module while Samba changes internal module ordering and feature handling. The file also registers `dsdb_flags_ignore`, a helper module that strips internal DSDB metadata flags before passing add/modify messages down.

## Important APIs, Types, And Functions
`read_at_rootdse_record()` reads `@ROOTDSE` for naming context attributes needed to configure partition module routing. `prepare_modules_line()` builds `modules` attribute values of the form `backendDN:module1,module2,...` for the partition module's opaque configuration message. `check_required_features()` validates that `@SAMBA_DSDB` required features are known to this Samba version. `samba_dsdb_init()` is the central initializer: it registers Samba LDB handlers, checks DSDB feature records, builds the ordered module list, prepares partition-module configuration, loads the module list in reverse for LDB, installs it as the next chain, and initializes the chain under a read lock.

`dsdb_flags_ignore_fixup()` shallow-copies add/modify messages and removes `DSDB_FLAG_INTERNAL_FORCE_META_DATA` from element flags; if an element only carried that flag and has no values, it removes the element. `dsdb_flags_ignore_add()` and `dsdb_flags_ignore_modify()` rebuild requests with the fixed message. `ldb_samba_dsdb_module_init()` registers both `samba_dsdb` and `dsdb_flags_ignore`.

## Control Flow
Initialization first registers DSDB syntax/handler support and constructs DNs for `@SAMBA_DSDB`, `@INDEXLIST`, and the partition control record. If `@SAMBA_DSDB` exists, required features are checked against the features this code understands. Old compatible features are pruned depending on whether `@INDEXLIST` says Samba feature options are supported; modifications are wrapped in direct lower-module transactions.

The final DSDB module list is assembled in semantic order: `resolve_oids`, `rootdse`, notification/schema/load/lazy commit and query-control modules, `extended_dn_store`, `extended_dn_in`, audit/objectclass/security/password/samldb/instancetype modules, TDB/link modules such as `repl_meta_data`, `encrypted_secrets`, `operational`, `linked_attributes`, `extended_dn_out_ldb`, and final notification/partition modules. Because LDB loads lists in reverse, the code reverses the final list before `ldb_module_load_list()`.

Partition configuration is built from `@ROOTDSE`: one line routes the schema naming context through `schema_data` plus backend modules, and one wildcard line routes other backends through the backend module list. The resulting message is stored in the `DSDB_OPAQUE_PARTITION_MODULE_MSG_OPAQUE_NAME` opaque, also used by gMSA code as proof of local DB access.

## State And Persistence
The module stores the constructed partition configuration as an LDB opaque and rewires the in-memory module chain. It may persistently modify `@SAMBA_DSDB` compatible-feature values during startup cleanup. Otherwise state is process-local and derived from database control records. `dsdb_flags_ignore` has no durable state; it only normalizes request flags.

## Dependencies And Integration Points
This file is the integration point for nearly the whole DSDB LDB stack. It depends on LDB module loading, DSDB module helpers, Samba feature constants, `@ROOTDSE`, `@SAMBA_DSDB`, `@INDEXLIST`, partition module opaques, encrypted secrets feature flags, LMDB feature flags, and Samba handler registration. Ordering is critical because downstream modules assume prior modules have expanded object classes, resolved DNs, enforced ACLs, generated metadata, or routed partitions.

## Risks And Test Signals
Module ordering is the main risk: moving entries can break security, schema loading, linked attributes, or partition routing. Feature-gate handling is another risk, especially refusing databases with unknown required features and pruning compatible features without losing data needed by older/newer versions. `indexlist_dn` has a defensive check typo that tests `samba_dsdb_dn` after allocating `indexlist_dn`; allocation-failure tests would catch this pattern. Tests should cover bootstrap on empty and existing databases, unknown required features, compatible-feature cleanup with and without `@INDEXLIST`, exact module order, partition opaque contents, read-lock cleanup on init failure, and `dsdb_flags_ignore` add/modify behavior for empty and non-empty forced-metadata elements.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/samba_dsdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/samba_secrets.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/samba_secrets.c

## Purpose
`samba_secrets.c` implements the `samba_secrets` LDB bootstrap module for `secrets.ldb`. Like `samba_dsdb`, it keeps the database-facing module name stable while constructing the real internal module chain at runtime.

## Important APIs, Types, And Functions
`samba_secrets_init()` is the only operational function. It defines the secrets stack as `update_keytab`, `secrets_tdb_sync`, `objectguid`, and `rdn_name`, reverses that list for `ldb_module_load_list()`, appends the resulting chain ahead of the backend module, installs it with `ldb_module_set_next()`, and calls `ldb_next_init()`. `ldb_samba_secrets_module_init()` registers the module.

## Control Flow
During init, the module counts the static module list, allocates a reversed array, loads the modules with the current next module as backend, frees temporary memory, sets the loaded chain as this module's next pointer, and then initializes the rest of the chain. Errors from allocation or module loading return immediately.

## State And Persistence
The module does not directly read or write secrets. Its state is the in-memory LDB module chain. Durable behavior is delegated to loaded modules: keytab updates, TDB synchronization, objectGUID handling, and RDN name maintenance.

## Dependencies And Integration Points
It depends on LDB module loading APIs and the availability of `update_keytab`, `secrets_tdb_sync`, `objectguid`, and `rdn_name` modules. It is specific to `secrets.ldb`, not the main AD DSDB.

## Risks And Test Signals
Risk is concentrated in module availability and ordering. If the reversed-load convention changes or one named module is missing, secrets DB initialization fails. Tests should verify the constructed order, failure on missing module names, successful init against a minimal secrets.ldb backend, keytab sync behavior through the loaded chain, and objectGUID/RDN maintenance on add and rename operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/samba_secrets.c -->
