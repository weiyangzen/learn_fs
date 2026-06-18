# subset-b-009914 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/samldb.c -->
## sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/samldb.c

Purpose: `samldb.c` implements the Samba AD `samldb` LDB module, the central SAM/DSDB trigger layer for adds, modifies, deletes, renames, and selected extended operations. It fills in AD-derived attributes, rejects direct writes to computed or protected fields, allocates RIDs/SIDs, enforces object class and account-control invariants, validates schema additions, checks SPN and UPN uniqueness, redirects writes away from RODCs, and mediates delete/rename constraints.

Important APIs, types, and functions: The module is registered by `ldb_samldb_module_init()` with handlers for `add`, `modify`, `del`, `rename`, and `extended`. `struct samldb_ctx` carries the module, original request, current message, add type, SID, async step chain, and saved downstream reply. `samldb_add_step()`, `samldb_first_step()`, and `samldb_next_step()` build local state-machine sequences for multi-stage add processing. Key validators include `samldb_unique_attr_check()`, `samldb_sam_account_upn_clash()`, `samldb_sam_accountname_valid_check()`, schema ID helpers for `attributeID`, `governsID`, `lDAPDisplayName`, `linkID`, `mAPIID`, and `msDS-IntId`, `samldb_check_user_account_control_rules()`, `samldb_prim_group_trigger()`, `samldb_member_check()`, `samldb_spn_uniqueness_check()`, `samldb_fsmo_role_owner_check()`, and `samldb_verify_subnet()`. Extended handlers delegate RID pool and RID set work to `ridalloc_*`.

Control flow: `samldb_add()` copies the incoming add message, blocks special/protected writes, performs RODC referral checks, then dispatches by object class. User and group adds run primary group and object-class triggers before `samldb_fill_object()` schedules SID allocation, RODC/gMSA setup, sAMAccountName validation, and the actual child add. Class and attribute schema adds validate uniqueness, update schemaInfo, fill defaults such as `subClassOf`, `rdnAttId`, `schemaIDGUID`, `objectClassCategory`, syntax metadata, and then add plus post-check `defaultObjectCategory`. `samldb_modify()` rejects direct mutation of protected fields, computes expected new values, rewrites dependent attributes in-place, optionally emits a child modify request, and otherwise passes through. Delete checks prevent deleting groups that remain primary groups and protects low well-known RIDs. Rename performs a base-object search with recycled visibility, checks system/container/schema/config/domain move flags, then lets the next module run. Extended requests are matched by OID and otherwise passed down.

State and persistence behavior: The module does not own durable storage directly, but it mutates LDB requests that later persist through lower modules. It allocates RIDs from the RID allocator, derives `objectSid` from the domain SID, writes schemaInfo through `dsdb_module_schema_info_update()`, and uses the LDB opaque `SAMLDB_MSDS_INTID_OPAQUE` to cache the next `msDS-IntId` candidate across schema additions. It can add controls, notably `DSDB_CONTROL_PASSWORD_USER_ACCOUNT_CONTROL_OID`, so password modules see both requested and normalized UAC state. SPN auto-update can issue a same-module child modify before adding automatic SPN replacements.

Dependencies and integration points: This module depends heavily on DSDB helpers in `samdb.h`, `ldb_modules/util.h`, `ridalloc.h`, schema lookup APIs, ACL helpers, security descriptors/tokens, NDR SID encoding, gMSA password generation, and network address parsing. It relies on upstream ACL modules for access decisions but performs extra extended-right and privilege checks for UAC bits, `pwdLastSet`, `msDS-SecondaryKrbTgtNumber`, and delegation attributes. It integrates with RODC behavior by generating referrals unless replicated/dbcheck controls are present, and with schema modules by updating schemaInfo and expecting schema cache availability.

Risks: This file is a high-blast-radius compatibility layer. Small changes can alter Windows-compatible error codes, request flags, or generated attributes. The SPN alias collision logic depends on the order and interpretation of `sPNMappings`, and it performs a write-right probe by issuing a delete/add modify against the colliding object. The UAC and primary-group logic rewrites linked membership and depends on exact RID mappings. Schema ID generation probes both cache and database, so transaction boundaries and concurrent schema updates matter. RODC referral and sensitive-attribute gates are security-sensitive. CIDR validation intentionally enforces Windows-like quirks and canonical formatting, which may reject otherwise valid IP notation.

Test signals: Relevant coverage is likely in Samba AD LDAP/SAM tests such as account creation/modification, SPN uniqueness, primary group behavior, schema add/modify tests, RODC join paths, tombstone restore tests, and subnet object tests. The file itself has no local unit tests in this subset; regressions should be sought through end-to-end LDB module stack tests because most behavior depends on controls, security tokens, schema cache, and downstream modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/samldb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/schema_data.c -->
## sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/schema_data.c

Purpose: `schema_data.c` implements the `schema_data` LDB module. It protects schema writes, maintains prefix-map coverage for new schema OIDs, blocks invalid direct schema-root mutations, forbids schema deletes, and generates dynamic schema attributes returned in search results.

Important APIs, types, and functions: `schema_data_init()` records the schema DN and aggregate schema DN. `schema_data_add()`, `schema_data_modify()`, and `schema_data_del()` enforce schema-master and update-allowed rules unless replicated, dbcheck, or specific system controls apply. Generated attribute functions include `generate_objectClasses()`, `generate_attributeTypes()`, `generate_dITContentRules()`, `generate_extendedAttributeInfo()`, `generate_extendedClassInfo()`, and `generate_possibleInferiors()`. `schema_data_search()` wraps searches that request generated attributes, and `schema_data_search_callback()` injects generated values into aggregate or classSchema entries.

Control flow: Initialization delegates to the next module, resolves `ldb_get_schema_basedn()`, and builds `CN=Aggregate` schema DN state. Add requests ignore special DNs and replicated updates, ensure schema updates happen on the schema master or RODC path, require new schema objects to be direct children of the schema DN, and add missing prefix-map mappings for `attributeID` or `governsID`. Modify requests allow schema root writes only for non-constrained attributes unless AS_SYSTEM is present, then apply the same master/update gates for child entries. Delete requests normally reject schema deletion after master checks. Search requests are wrapped only when requested attributes match the generated list.

State and persistence behavior: The module stores only private DNs in module memory. Persistent changes are limited to prefix-map updates via `dsdb_create_prefix_mapping()` during add and normal downstream schema writes. Generated search attributes are not stored in the database; they are synthesized from the loaded `dsdb_schema` on demand.

Dependencies and integration points: It depends on the loaded DSDB schema, prefix-map helpers, schema description serialization helpers, `samdb_rodc()`, and LDB control handling. It pairs with `schema_load.c`, which supplies the schema cache, and with `samldb.c`, which performs more object-specific schema validation and schemaInfo updates.

Risks: Write gating is security and replication sensitive: relaxing master/update checks incorrectly could permit divergent schema edits. Prefix-map creation is persistence-affecting and must match the OID used by new schema objects. Generated attributes are based on in-memory schema state, so stale schema cache behavior can surface as incorrect LDAP search results. `possibleInferiors` depends on precomputed schema class data and is covered by a nearby Python test.

Test signals: The strongest direct signal is `tests/possibleinferiors.py` for generated `possibleInferiors`. Schema add/modify/delete behavior should be covered by Samba schema FSMO, replication, provisioning, and LDAP schema tests that exercise root schema writes, prefixMap updates, and generated aggregate attributes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/schema_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/schema_load.c -->
## sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/schema_load.c

Purpose: `schema_load.c` implements the `schema_load` LDB module. It opens schema metadata, loads `dsdb_schema` from the database, registers refresh callbacks, tracks transaction/read-lock state to avoid unsafe reloads, and writes schema-derived `@INDEXLIST` and `@ATTRIBUTES` records when needed.

Important APIs, types, and functions: `struct schema_load_private_data` tracks the module, transaction counters, metadata TDB handle, cached metadata sequence number, TDB seqnum, and pending index write flag. `schema_metadata_open()` opens `sam.ldb.d/metadata.tdb`. `schema_metadata_get_uint64()` reads and caches metadata keys such as `DSDB_METADATA_SCHEMA_SEQ_NUM`. `dsdb_schema_refresh()` decides whether to reload schema. `dsdb_schema_from_db()` loads dMD, attributeSchema, and classSchema records in one subtree search. `schema_load()`, `schema_load_init()`, transaction hooks, read-lock hooks, and `schema_load_extended()` form the module API.

Control flow: Init delegates downward, opens metadata, registers `dsdb_schema_refresh()` when metadata exists, forces an initial schema load through `dsdb_get_schema()`, and checks whether schema-derived index/attribute records need writing. Refresh skips reloads during normal read/write transactions unless the `dsdb_schema_refresh_expected` opaque is set, compares the metadata sequence number with `schema->metadata_usn`, and reloads only on change. The database load performs one search for schema root, attributes, and classes to avoid split-search races, identifies the schema root by `prefixMap`, builds the schema structure, and records the metadata USN. Transaction start attempts refresh and writes pending indices if required; transaction end/delete decrement counters.

State and persistence behavior: Persistent state lives in `sam.ldb.d/metadata.tdb` and the LDB `@INDEXLIST`/`@ATTRIBUTES` records. In-memory state caches metadata seqnums and transaction counters. The module installs a schema refresh function into the LDB context and can make reloaded schemas global via `dsdb_make_schema_global()`. It intentionally avoids refreshing during active transactions to prevent schema changes behind the transaction's view.

Dependencies and integration points: It uses TDB wrappers, loadparm TDB flags, DSDB schema construction functions, schema index writers, LDB module transaction/read-lock APIs, and extended operation OIDs `DSDB_EXTENDED_SCHEMA_LOAD` and `DSDB_EXTENDED_SCHEMA_UPDATE_NOW_OID`. It provides the schema cache used by `schema_data.c`, `samldb.c`, objectclass validation, and many DSDB helpers.

Risks: Reload timing is delicate. Refreshing too often during transactions can violate consistency, while failing to refresh after metadata changes yields stale LDAP/schema behavior. The metadata seqnum cache depends on TDB seqnum correctness. The single subtree search reduces race windows but makes schema load sensitive to missing `prefixMap` or malformed schema entries. Index writes occur on transaction start, so failures there can block otherwise unrelated transactions.

Test signals: Useful tests include schema modification followed by immediate lookups, metadata sequence number changes, provisioning with no preloaded schema, schema index reconciliation, and extended schema update operations. There is no direct local test here; failures usually appear as LDAP schema search errors, objectclass validation problems, or missing index records.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/schema_load.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/schema_util.c -->
## sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/schema_util.c

Purpose: `schema_util.c` provides utility functions for reading, writing, and updating the serialized `schemaInfo` attribute on the schema partition. It is not itself an LDB module; it is a helper used by schema-changing modules such as `samldb.c`.

Important APIs, types, and functions: Public helpers are `dsdb_module_schema_info_blob_read()`, `dsdb_module_schema_info_blob_write()`, and `dsdb_module_schema_info_update()`. Internal helpers `dsdb_schema_info_write_prepare()`, `dsdb_module_schema_info_read()`, and `dsdb_module_schema_info_write()` convert between LDB messages, NDR blobs, and `struct dsdb_schema_info`.

Control flow: Read locates the schema base DN, searches for `schemaInfo`, and transfers the blob into the caller's memory context. Write builds a replace modify message for `schemaInfo` and sends it through `dsdb_module_modify()`. Update obtains the local NTDS invocation ID, reads the existing schemaInfo or creates a default when missing, increments the revision, sets the invocation ID, and writes the updated blob back.

State and persistence behavior: The durable state is the `schemaInfo` attribute on the schema root. The helper deliberately does not update the in-memory `schema->schema_info` after writing because the surrounding transaction may still fail and because the schema object may be shared globally. The next schema reload observes the stored value.

Dependencies and integration points: It depends on DSDB common utilities, NDR DRS blob helpers, LDB module search/modify wrappers, and `samdb_ntds_invocation_id()`. `samldb_schema_info_update()` calls `dsdb_module_schema_info_update()` when classSchema or attributeSchema entries are added by originating writes.

Risks: Incorrect memory ownership around blobs could leave dangling data, so the read helper steals blob data into the caller's context. The update path must be called within a transaction by callers, otherwise schemaInfo could advance without the associated schema change. Error handling maps missing schemaInfo to a default only for update, while malformed blobs become operational errors.

Test signals: Schema extension tests should verify that schemaInfo revision and invocation ID change on originating schema updates, but not on replicated/provisioning paths that bypass updates. Tests should also cover missing initial schemaInfo and failed schemaInfo decoding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/schema_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/secrets_tdb_sync.c -->
## sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/secrets_tdb_sync.c

Purpose: `secrets_tdb_sync.c` implements the `secrets_tdb_sync` LDB module, which mirrors relevant `secrets.ldb` primary domain secret changes into the legacy `secrets.tdb` store at transaction commit time.

Important APIs, types, and functions: `struct secrets_tdb_sync_private` holds a linked list of changed DNs and a `db_context` for `secrets.tdb`. `struct secrets_tdb_sync_ctx` tracks a single add/modify/delete/rename operation. Operation hooks are `secrets_tdb_sync_add()`, `secrets_tdb_sync_modify()`, `secrets_tdb_sync_delete()`, and `secrets_tdb_sync_rename()`. `add_modified()` records primaryDomain messages. `ust_search_modified()` and callbacks detect `kerberosSecret` entries with `privateKeytab`. Transaction hooks start, prepare, commit, or cancel the `secrets.tdb` transaction.

Control flow: Adds, modifies, and renames first forward the operation to lower modules through child requests. When the lower operation completes, the module searches the affected DN for a `kerberosSecret` with `privateKeytab`; if found, it records the corresponding `primaryDomain` object for commit-time sync. Deletes search first, record deletion if applicable, then issue the downstream delete. During `prepare_commit`, all recorded messages are converted into `secrets_store_machine_pw_sync()` calls, including current and prior secrets, flatname, realm, salt principal, encryption types, object SID, timestamp, secure channel type, and delete flag.

State and persistence behavior: The LDB database is modified by downstream modules. This module keeps an in-memory per-transaction list of changed secret messages and opens a separate transaction on `secrets.tdb`. On successful prepare and end transaction, it commits the TDB transaction. On failure or deleted transaction, it cancels the TDB transaction and frees pending changes. Initialization derives the private directory from the LDB URL and initializes the secrets subsystem.

Dependencies and integration points: It depends on Samba credentials and Kerberos headers, `param/secrets.h`, source3 `secrets.h`, dbwrap transactions, DSDB module search helpers, and `secrets_store_machine_pw_sync()`. The module is a bridge between modern LDB secret records and older TDB consumers.

Risks: The file itself notes semi-async concerns: callbacks and synchronous credential/secrets operations are mixed. Consistency depends on the LDB transaction and the TDB transaction staying aligned across prepare, commit, and cancel. Only entries matching both primaryDomain and kerberosSecret/privateKeytab conditions are synced; schema or filter changes could silently desynchronize stores. Commit-time failures cancel the TDB transaction but cannot repair already completed lower-module work except by failing the LDB transaction.

Test signals: Good tests mutate, rename, and delete matching secret entries inside transactions and verify `secrets.tdb` contents after commit and rollback. Coverage should include non-matching entries, failures in `secrets_store_machine_pw_sync()`, and private directory derivation from `tdb://` URLs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/secrets_tdb_sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/show_deleted.c -->
## sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/show_deleted.c

Purpose: `show_deleted.c` implements the `show_deleted` LDB module, which hides deleted or recycled directory objects from normal searches and honors LDAP controls that request visibility of tombstones or recycled objects.

Important APIs, types, and functions: `struct show_deleted_state` caches whether recycle bin state needs refresh and whether it is enabled. `show_deleted_search()` rewrites search parse trees to exclude deleted/recycled entries when appropriate. `show_deleted_init()` registers `LDB_CONTROL_SHOW_DELETED_OID` and `LDB_CONTROL_SHOW_RECYCLED_OID` and initializes module state.

Control flow: Search requests for special DNs pass through unchanged. Without show-deleted or show-recycled controls, the module adds a `(!(isDeleted=TRUE))` filter. With controls present, it refreshes recycle-bin state if needed. If recycle bin is enabled and the caller did not request recycled objects, it excludes `isRecycled=TRUE`; otherwise it leaves the search tree unchanged. The rewritten search is issued as a child request and recognized controls are marked non-critical.

State and persistence behavior: The module has no durable state. It caches recycle-bin enabled status in module-private memory and refreshes lazily, tolerating missing feature objects during provisioning by assuming disabled. Query behavior is transient and expressed only by child search filters.

Dependencies and integration points: It depends on LDB parse trees, DSDB recycle-bin feature lookup, and LDAP show-deleted/show-recycled controls. Downstream modules execute the actual search. Rename and subtree modules use recycled visibility controls when they need internal access to deleted entries.

Risks: Incorrect filter rewriting can expose deleted/recycled objects or hide live ones. The recycle-bin state cache has a `need_refresh` guard to avoid recursion loops; moving that assignment could re-enter refresh logic. During provisioning, missing feature objects intentionally degrade to disabled behavior, which must remain compatible with startup order.

Test signals: Search tests should verify normal searches hide tombstones, show-deleted exposes deleted but not recycled objects when recycle bin is enabled, show-recycled exposes all states, and provisioning/startup without feature objects does not fail.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/show_deleted.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/subtree_delete.c -->
## sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/subtree_delete.c

Purpose: `subtree_delete.c` implements the `subtree_delete` LDB module. It prevents accidental deletion of non-leaf entries unless the tree-delete control is present, and recursively deletes children before the requested parent when tree delete is authorized.

Important APIs, types, and functions: The main handler is `subtree_delete()`, registered as the module `del` hook. `subtree_delete_init()` registers `LDB_CONTROL_TREE_DELETE_OID` with rootDSE. The module uses `dsdb_module_search()` to detect one-level children and `dsdb_module_del()` for recursive child deletion.

Control flow: Special DNs are passed through. For normal deletes, the module searches one level below the target. If there are no children, the request passes downstream unchanged. If children exist and the request lacks `LDB_CONTROL_TREE_DELETE_OID`, it returns `LDB_ERR_NOT_ALLOWED_ON_NON_LEAF`. With the control present, it deletes each child through the top module with AS_SYSTEM, TRUSTED, and DSDB_TREE_DELETE flags, preserving relax semantics when requested, then lets the original delete continue.

State and persistence behavior: The module stores no state. Persistence is the recursive sequence of downstream deletes. Children are deleted first because parent deletion happens only after recursive child calls complete and the original request reaches lower modules.

Dependencies and integration points: It relies on upstream ACL checks for delete-tree rights and then uses `DSDB_FLAG_AS_SYSTEM` because authorization is considered complete. It interacts with modules such as objectclass and samldb by starting recursive deletes at the top module so normal constraints still apply.

Risks: Recursive deletion order and flags are security-sensitive. Failing to start from the top module could bypass constraints; failing to pass trusted/system flags could cause authorized tree deletes to fail mid-tree. Error strings intentionally avoid DN output because older MMC clients mishandle some subtree delete errors.

Test signals: Tests should cover deleting leaves, rejecting non-leaf deletes without control, deleting nested subtrees with control, relax-control propagation, and failures from child constraints. Integration tests are more valuable than unit tests because behavior depends on module stack ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/subtree_delete.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/subtree_rename.c -->
## sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/subtree_rename.c

Purpose: `subtree_rename.c` implements the `subtree_rename` LDB module. It expands a base rename into a subtree rename by moving immediate children under the new base DN, with recursion achieved by re-entering the same module for child renames.

Important APIs, types, and functions: `struct subtree_rename_context` tracks the original request and whether the base object has been renamed. `subren_ctx_init()` allocates context. `subtree_rename()` builds a one-level search under the old DN. `subtree_rename_search_onelevel_callback()` first renames the base, then rewrites and renames each child DN.

Control flow: Special DNs pass through. A normal rename performs a one-level search with `SHOW_RECYCLED` so internal moves can see deleted/recycled children. In the first callback invocation, before processing child entries, the module renames the base through the next module. For each child entry, it removes the old base components from the child DN, appends the new base DN, and calls `dsdb_module_rename()` with `DSDB_FLAG_OWN_MODULE`; that re-enters this module for grandchildren. When the search completes, the original request is completed successfully.

State and persistence behavior: There is no durable module state. Persistence is a sequence of downstream rename operations that moves the root before children. The context's `base_renamed` boolean prevents repeated base renames while the search yields child entries.

Dependencies and integration points: It uses LDB search/rename APIs, DSDB rename wrappers, recycled-object controls, and downstream constraint modules such as `samldb.c`, which checks rename policy before subtree movement. It assumes module-stack recursion will handle deeper descendants.

Risks: The root-first order means failures while moving descendants can leave partial movement unless the surrounding LDB transaction rolls back all operations. DN rewriting must preserve relative child paths exactly. Re-entry with `DSDB_FLAG_OWN_MODULE` is central to recursive behavior; changing flags could either skip grandchildren or loop incorrectly.

Test signals: Tests should rename leaf and multi-level subtrees, verify descendants preserve relative names, include deleted/recycled child visibility cases, and force a descendant constraint failure to confirm transaction rollback semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/subtree_rename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/possibleinferiors.py -->
## sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/possibleinferiors.py

Purpose: `possibleinferiors.py` is a Samba test script that validates the generated `possibleInferiors` schema attribute against an independently constructed implementation of the AD algorithm.

Important APIs, types, and functions: The script parses a database or LDAP URL and optional class name, opens `samba.Ldb`, discovers `schemaNamingContext` from rootDSE, and compares `possible_inferiors_search()` with `possible_inferiors_constructed()`. Helper functions `supclasses()`, `auxclasses()`, `subclasses()`, and `posssuperiors()` build cached class relationships. `pull_classinfo()` reads all classSchema objects and prepares subclass maps. `test_class()` performs the assertion and exits nonzero on mismatch.

Control flow: After argument parsing and credential setup, the script connects to local LDB or remote LDAP, switching to paged searches for LDAP URLs. It reads rootDSE, loads class metadata from the schema partition, precomputes subclasses, then tests either all classes or the requested class. For each tested class, it searches the live generated `possibleInferiors`, constructs the expected sorted unique list by walking possible superiors and subclasses, and prints a detailed diff before exiting on failure.

State and persistence behavior: The script is read-only. Runtime state is an in-memory dictionary keyed by `ldapDisplayName`, with memoized lists for superclasses, auxiliary classes, possible superiors, and subclasses. It does not modify the database or write artifacts.

Dependencies and integration points: It depends on Samba Python bindings, `ldb`, Samba option/credential helpers, and the `schema_data` module's generated `possibleInferiors` behavior. The `--wspp` flag switches to a variant based on WSPP documentation, while default behavior follows observed Windows Server 2003/2008 behavior noted in comments.

Risks: The script shadows Python built-in names such as `list` and `set`, which is stylistically risky but localized. Recursive relationship expansion assumes schema class references are present in `classinfo`; malformed schemas could raise key errors. Because comparison is sorted unique strings, it validates membership but not original ordering or duplicate behavior. Remote LDAP results depend on credentials and server-side module stack configuration.

Test signals: Successful completion prints `Lists match OK`. Failures print both returned and constructed lists plus aligned differences for the tested class. This is a direct regression signal for `schema_data.c` `generate_possibleInferiors()` and related schema relationship generation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/possibleinferiors.py -->
