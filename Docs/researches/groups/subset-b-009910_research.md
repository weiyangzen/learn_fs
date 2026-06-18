# subset-b-009910 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/operational.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/operational.c

## Purpose

`operational.c` implements the Samba DSDB LDB `operational` module. It intercepts LDAP searches and makes Active Directory operational and constructed attributes appear with Windows-compatible behavior without storing most of them directly. It rewrites filters for searchable aliases such as `createTimeStamp` and `modifyTimeStamp`, expands requested attribute lists with hidden dependencies, post-processes returned entries, strips sensitive or helper attributes, and constructs values such as `tokenGroups`, `parentGUID`, `msDS-isRODC`, `msDS-KeyVersionNumber`, `msDS-User-Account-Control-Computed`, `msDS-UserPasswordExpiryTimeComputed`, `msDS-ResultantPSO`, and `msDS-ManagedPassword`.

The module is read-path focused. It registers only `.search` and `.init_context` handlers and depends on surrounding write-side modules to maintain stored attributes such as `whenCreated`, `whenChanged`, `objectSid`, `primaryGroupID`, `pwdLastSet`, `lockoutTime`, `replPropertyMetaData`, and PSO links.

## Important APIs, Types, and Tables

`struct operational_data` stores lazy module state, currently the aggregate schema DN used for `subSchemaSubEntry` and the schema aggregate special case for `modifyTimeStamp`.

`struct operational_context` is per-search state: original request, search scope, requested attrs, possibly rewritten parse tree, control flags, lists of attributes to remove and construct, cached smart-card password-expiry policy, and a cached current time.

`enum search_type` controls group SID expansion for `tokenGroups`, global/universal token groups, no-GC-acceptable token groups, and account groups used by PSO lookup.

`struct op_attributes_replace` and the `search_sub[]` table are the main behavior map. For each constructed/alias attribute, the table declares the requested attribute name, the backend replacement attribute if any, extra dependencies to fetch, and an optional constructor. `operational_search()` uses this table to expand the downstream request, and `operational_search_post_process()` uses it to add final attributes.

`operational_remove[]` defines attributes to remove from results. It always removes synthetic `parentGUID`, conditionally hides `nTSecurityDescriptor`, hides `msDS-KeyVersionNumber` unless bypass-operational control allows it, and removes replication metadata and DSDB secret attributes unless explicitly requested.

Key constructors include `construct_canonical_name()`, `construct_primary_group_token()`, `construct_token_groups*()`, `construct_parent_guid()`, `construct_modifyTimeStamp()`, `construct_subschema_subentry()`, `construct_msds_isrodc()`, `construct_msds_keyversionnumber()`, `construct_msds_user_account_control_computed()`, `construct_msds_user_password_expiry_time_computed()`, `construct_resultant_pso()`, and the imported `constructed_msds_managed_password()`.

PSO support is split across `pso_is_supported()`, `get_pso_count()`, `pso_search_by_sids()`, `pso_find_best()`, and `get_pso_for_user()`. Group SID expansion is centralized in `get_group_sids()` via `dsdb_expand_nested_groups()`.

## Control Flow

`operational_search()` is entered for normal searches, but special DNs bypass the module. The function allocates an `operational_context`, checks the filter parse tree for searchable operational aliases, and shallow-copies/replaces the parse tree only when needed. It records whether `LDB_CONTROL_SD_FLAGS_OID` and `LDB_CONTROL_BYPASS_OPERATIONAL_OID` are present.

It then walks the requested attribute list. If a requested attribute matches `search_sub[]`, the module records a replacement operation, adds any dependency attributes to the downstream attribute list, and substitutes the stored backend attribute where applicable. This is performance-sensitive: the table order intentionally allows `msDS-ResultantPSO` to be constructed before other attributes that can reuse it.

The downstream request is built with `ldb_build_search_req_ex()` and `operational_callback()`. For every entry, the callback calls `operational_search_post_process()`, which first removes attributes selected by `operation_get_op_list()`, then constructs requested attributes through constructors or by copying replacement attrs, and finally removes helper attrs that were added only to make construction possible unless the caller explicitly requested them or requested `*`.

Constructed attributes often perform additional internal searches. Examples: `construct_parent_guid()` checks whether the object is an NC head and searches the parent for `objectGUID`; `construct_msds_isrodc()` walks nTDSDSA/server/computer relationships; PSO-backed password/lockout attributes inspect direct PSO application, group membership, and the Password Settings Container.

## State and Persistence Behavior

The module persists no database state. Its only module-private state is the lazily cached aggregate schema DN. Per-request state is talloc-owned by the request. Expensive values such as the current time and `msDS-ExpirePasswordsOnSmartCardOnlyAccounts` are cached only for the lifetime of one search request.

Even though it does not write state, it interprets persistent DSDB state heavily: domain functional level, password policies, PSO objects, replicated property metadata, group memberships, security descriptors, schema timestamps, and gMSA managed-password material.

## Dependencies and Integration Points

The module integrates with the LDB module chain through `ldb_build_search_req_ex()`, `ldb_next_request()`, `ldb_module_send_entry()`, referrals, and module completion callbacks. It relies on DSDB helper APIs from `samdb.h`, `util.h`, managed password construction, NDR parsing of `replPropertyMetaDataBlob`, SID helpers from auth/security code, and schema/domain helpers such as `dsdb_functional_level()`, `dsdb_find_nc_root()`, `samdb_aggregate_schema_dn()`, and `dsdb_gmsa_current_time()`.

LDAP controls are important integration points. `LDB_CONTROL_SD_FLAGS_OID` changes whether `nTSecurityDescriptor` is retained. `LDB_CONTROL_BYPASS_OPERATIONAL_OID` allows direct exposure of `msDS-KeyVersionNumber`.

## Risks and Edge Cases

Constructed attributes are easy to break by changing dependency lists. Missing `objectClass`, `objectSid`, `primaryGroupID`, `pwdLastSet`, `userAccountControl`, or PSO fields can silently produce no value or fall back to domain defaults.

`tokenGroups` requires BASE scope; broader searches return operations errors if the attribute is requested. Group expansion and PSO lookup can be expensive and may recursively search large memberships.

The parse-tree replacement logic only covers attributes in `parse_tree_sub[]`; constructed attributes that are not searchable remain post-processing only. Shallow parse-tree copies and talloc references rely on the original request tree remaining alive.

Password expiry and lockout calculations depend on negative AD interval semantics and boundary handling for `INT64_MIN`/`INT64_MAX`. Small arithmetic mistakes here would create security-visible account-state bugs.

`msDS-KeyVersionNumber` depends on parsing replication metadata and a hard-coded `DRSUAPI_ATTID_unicodePwd` lookup. Corrupt metadata can turn a search into an operational error.

Secret-attribute hiding is centralized in `operational_remove[]`; additions to DSDB secret attributes must continue to flow into this list.

## Test Signals

Relevant tests should cover searching by `createTimeStamp`/`modifyTimeStamp` filters, requested constructed attributes with and without `*`, SD flags behavior, bypass-operational behavior for key version number, token group BASE-scope enforcement, parentGUID on NC heads and non-NC children, RODC detection across nTDSDSA/server/computer paths, PSO precedence and GUID tie-breaking, smart-card-only password expiry policy at functional levels below and at 2016, lockout duration fallback to domain defaults, and secret attribute suppression. Regression tests should verify helper attributes added for construction are stripped unless explicitly requested.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/operational.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/paged_results.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/paged_results.c

## Purpose

`paged_results.c` implements Samba's DSDB LDB module for the LDAP paged-results control. It accepts searches with `LDB_CONTROL_PAGED_RESULTS_OID`, caches the complete result identity set for an initial search, and returns subsequent pages by re-searching each result by GUID. This preserves a stable page sequence while allowing the returned entry content and DN to reflect current database state, matching observed Windows behavior for moved objects.

The module rejects incompatible VLV+simple-paged combinations and registers the paged-results control in rootDSE during initialization.

## Important APIs and Types

`struct private_data` is module-private state. It tracks the next string cookie ID, the count of active result stores, and a doubly linked list of `results_store` objects.

`struct results_store` is the persistent per-cookie page state. It contains the cookie, timestamp, cached referrals, response controls from the initial search, an array of result GUIDs, saved downstream controls, saved requested attrs, current index `last_i`, and a shallow copy/string representation of the original filter.

`struct paged_context` is per-request state holding the original request, page size, selected store, and final controls to return.

Main functions are `new_store()`, `store_destructor()`, `paged_search()`, `paged_search_callback()`, `paged_results()`, `paged_search_by_dn_guid()`, `paged_results_copy_down_controls()`, `paged_controls_same()`, `paged_attrs_same()`, and `paged_request_init()`.

## Control Flow

`paged_search()` first checks for the paged-results control. Requests without it pass through unchanged. It rejects malformed control data and rejects concurrent VLV requests with `LDB_ERR_UNSUPPORTED_CRITICAL_EXTENSION`. Page size is normalized so negative sizes from oversized client values become `0x7fffffff`.

For an initial request with zero-length cookie, a page size of zero is invalid. The module creates a new store, ensures the downstream search includes an extended-DN control so each returned DN contains a GUID component, and sends a downstream search requesting no user attributes. The original filter is shallow-copied into the store and also serialized as a string for continuation validation. Requested attrs and non-paged/non-ASQ controls are copied into the store. `ldb_save_controls()` removes the paged control from the downstream request.

`paged_search_callback()` receives the full initial result set. For each entry it extracts the GUID extended DN component and appends it to a dynamically growing GUID array. Referrals are saved in a linked list. On done, it shrinks the GUID array, saves response controls, calls `paged_results()` to emit the first page, and completes the original request.

For continuation requests, `paged_search()` finds the matching cookie in the store list. It validates that the filter string, non-paged controls, and requested attribute set match the original request. It promotes the store in the LRU list, treats page size zero as abandon/success, and otherwise calls `paged_results()`.

`paged_results()` advances through the cached GUID array until it has sent the requested page size or exhausted the store. Each GUID is re-searched using a BASE search on `<GUID=...>` and the original filter. Missing/deleted entries are skipped without failing the page. Referrals are emitted as soon as possible. The returned paged control contains the cookie and total result count when more pages remain, or an empty cookie when the page sequence is exhausted.

## State and Persistence Behavior

All state is in-memory and talloc-owned by the module. There is no disk persistence and no cross-process cookie sharing. The module caps active stores at 10, matching the default MaxResultSetsPerConn behavior noted in comments; creating the eleventh store frees the list tail. Stores also carry timestamps, but no aging policy is implemented beyond the LRU cap.

Because only GUIDs are cached, page continuation observes current object content and may skip deleted objects. The original filter remains applied during per-GUID rehydration, so entries that no longer match can also disappear from later pages.

## Dependencies and Integration Points

The module depends on LDB request/control APIs, extended DN control, GUID extraction via `GUID_from_ndr_blob()`, Samba linked-list macros, LDAP result/control constants, and talloc ownership. It cooperates with ASQ by excluding ASQ controls from copied continuation controls because ASQ changes search semantics. It uses rootDSE control registration via `ldb_mod_register_control()`.

The module must appear at a point in the LDB stack where the initial search can produce extended DNs with GUID components and where per-GUID searches can re-enter lower modules safely.

## Risks and Edge Cases

The in-memory cookie namespace is per module instance and monotonically increments `uint32_t`; very long-lived processes could wrap cookie IDs. There is no timeout cleanup despite stored timestamps.

Continuation validation uses `ldb_filter_from_tree()` string equality, set-like requested-attribute comparison, and custom control comparison. Differences in semantically equivalent filter serialization or duplicate attrs may affect compatibility. `paged_attrs_same()` checks attrs from the first list are present in the second but does not compare lengths, so duplicate or extra continuation attrs need careful consideration.

The initial search caches all GUIDs before returning the first page, so very large result sets consume memory proportional to the full result count. The GUID array grows by doubling and has overflow protection near `INT_MAX/2`, but the module still has no configurable result-store memory budget.

`paged_results_copy_down_controls()` steals controls/control data into the store. This works with the original request lifetime assumptions but is sensitive to callers that construct unusual non-talloc control trees.

Per-GUID re-searches are synchronous (`ldb_request()` plus `ldb_wait()` per entry), so large pages can incur significant latency and repeated lower-stack work.

## Test Signals

Tests should cover initial and continuation paging, abandon with size zero and non-empty cookie, invalid initial size zero, VLV conflict rejection, changed filter/control/attrs rejection, deleted and moved objects between pages, referral preservation, result count/cookie behavior on final page, LRU eviction after more than 10 active stores, requests lacking extended-DN input control, oversized page sizes, and ASQ interaction. Memory tests should exercise large result sets and store destruction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/paged_results.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/partition.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/partition.c

## Purpose

`partition.c` is the runtime router for Samba DSDB partitioned LDB databases. It decides which backend partition receives each request, fans searches or extended operations out to multiple partitions when required, replicates configured special DNs to all partitions, enforces cross-partition rename rules, and coordinates transactions, commit preparation, aborts, read locks, and global sequence-number requests across the primary metadata DB, partition backends, and `metadata.tdb`.

This file is the core execution half of the partition module; `partition_init.c` builds the partition list and `partition_metadata.c` supplies the metadata TDB used for locking and sequence numbers.

## Important APIs and Types

`struct partition_context` tracks a logical caller request split into one or more partition requests. It holds the original request, the generated per-partition requests, completion counts, and queued referrals.

`struct part_request` pairs a target module with the cloned request to run there.

`partition_request()` wraps `ldb_next_request()` with optional trace logging showing the current partition control.

`find_partition()` chooses a `dsdb_partition` by DN, honoring `DSDB_CONTROL_CURRENT_PARTITION_OID` when supplied by upstream modules such as replication metadata.

`partition_prep_request()` clones a search/add/modify/delete/rename/extended request for a specific partition, preserves caller controls except current-partition handling, adds `DSDB_CONTROL_CURRENT_PARTITION_OID` when appropriate, and adjusts a search base to the partition root if the caller searched above that partition.

Request handlers are `partition_search()`, `partition_add()`, `partition_modify()`, `partition_delete()`, `partition_rename()`, and `partition_extended()`.

Transaction and locking APIs exported to the module ops are `partition_start_trans()`, `partition_prepare_commit()`, `partition_end_trans()`, `partition_del_trans()`, `partition_read_lock()`, and `partition_read_unlock()`.

Sequence helpers include `partition_primary_sequence_number()`, `partition_sequence_number_from_partitions()`, and `partition_sequence_number()`.

## Control Flow

For writes, `partition_add()`, `partition_modify()`, and `partition_delete()` delegate to `partition_replicate()`. If a special DN appears in the configured replicate list, `partition_copy_all()` sends the operation to the primary chain, then `partition_copy_all_callback_action()` fetches the resulting object and add/modifies or deletes it in every partition so replicated metadata stays aligned. Otherwise `partition_replicate()` finds the target partition and prepares one request for that backend; unmatched DNs fall through to the main LDB chain.

`partition_rename()` finds the old and new partitions before routing. If the rename crosses partition boundaries, it returns `LDB_ERR_AFFECTS_MULTIPLE_DSAS`; otherwise it routes based on the old DN.

Search routing is more complex. `partition_search()` first honors explicit current-partition controls. It then interprets domain-scope, phantom-root, and no-global-catalog controls, clearing handled search-option bits before forwarding. Special DNs and uninitialized state pass through. Empty-base searches require phantom-root and otherwise fail. With phantom-root, the module matches exact partition roots, parent searches over partition roots, and child searches under a partition. Without phantom-root, it finds the containing partition and may generate LDAP referrals for child partitions unless domain-scope or BASE scope suppresses them. Partial-replica partitions are skipped when `DSDB_CONTROL_NO_GLOBAL_CATALOG` makes them invisible.

`partition_req_callback()` multiplexes replies. Entries and referrals are forwarded immediately. Done replies advance to the next prepared partition request, and only the final done completes the original request. If a current-partition control exists and the operation is single-partition or an entry reply, it adds that control to the reply so upstream modules can identify the backend used.

`partition_extended()` handles schema-update-now by incrementing metadata schema sequence, handles LDB sequence-number requests from `metadata.tdb`, creates partitions via `partition_create()`, and otherwise fans extended operations out to all partitions.

## State and Persistence Behavior

Runtime state comes from `struct partition_private_data` defined in `partition.h`: sorted partition list, replicate-DN list, metadata handle, module selection records, metadata sequence, transaction nesting count, optional forced module config, and backend store type.

Transactions are global across all backends. Start order is metadata.tdb transaction, top-level DB transaction, reload partition metadata, then each partition transaction. Prepare order matches start order. End/abort order is reverse for partition DBs, then top-level DB, then metadata.tdb. The comments explain why metadata.tdb is used as the effective global lock: TDB read/write locks block each other in the way MDB locks do not, and sequence updates force meaningful prepare-commit locking.

Read locks follow the same ordering: reload partition metadata first, then metadata.tdb read lock, top-level DB read lock, then each partition read lock. Unlock reverses that order.

Global sequence numbers are served from `metadata.tdb` through `partition_metadata_sequence_number()` and `partition_metadata_sequence_number_increment()`. Older sum-of-partitions logic remains as migration/fallback helper.

## Dependencies and Integration Points

This file is tightly integrated with LDB module ops, DSDB partition controls, LDB search-option controls, loadparm DNS domain settings for referrals, DSDB extended operations, transaction/read-lock module callbacks, and the initialization/metadata helpers declared through `partition_proto.h`.

It assumes the partition list is sorted by DN so search routing can stop after the nearest matching partition. It relies on `partition_init.c` for partial-replica flags and replicate DN lists and on `partition_metadata.c` for lock/sequence semantics.

## Risks and Edge Cases

Lock ordering is the highest-risk area. Any new path that locks a backend outside the documented metadata/top-level/partition order can deadlock or expose inconsistent cross-partition reads.

`partition_read_lock()` has a failure path that unlocks partition and top-level DB locks but does not explicitly call `partition_metadata_read_unlock()` after a metadata lock succeeds and a later lock fails. That may be intentional or covered by surrounding semantics, but it is a code path worth targeted review because the success path always expects metadata unlock in `partition_read_unlock()`.

Search referral generation depends on string containment checks against DN text to remove less-specific referrals. DN formatting or escaping changes could affect referral pruning.

Cross-partition copy-all for special DNs performs synchronous add/modify/delete operations after the primary request completes. Failures midway can leave partitions inconsistent unless the surrounding transaction reliably aborts all touched backends.

The module allows unmatched non-special write DNs to fall through to the main LDB chain, with a TODO suggesting an error might be more appropriate. Changes there could affect provisioning and special internal records.

The current-partition control affects routing and reply metadata; incorrect control data can force operations to unexpected partitions.

## Test Signals

Tests should cover single-partition writes, special-DN replication to all partitions, deletion of special DNs, modify operations that delete attributes, cross-partition rename rejection, phantom-root searches, domain-scope suppression of referrals, empty-base behavior with and without phantom-root, no-GC behavior with partial replicas, current-partition control routing and reply controls, extended operation fan-out, schema update sequence increments, metadata-backed sequence number next/highest, transaction rollback after a partition start failure, prepare/end failure propagation, and read-lock/read-unlock ordering under concurrent readers and writers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/partition.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/partition.h -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/partition.h

## Purpose

`partition.h` is the shared internal header for the Samba DSDB partition module implementation. It pulls in the required LDB, TDB, DSDB, utility, locale, and loadparm headers, defines the core private data structures used across `partition.c`, `partition_init.c`, and `partition_metadata.c`, and includes the generated `partition_proto.h` prototypes.

This header is not a public API in the general Samba sense; it is the private contract among the partition module compilation units.

## Important Types

`struct dsdb_partition` represents one backend naming context. It contains the top module used to send requests into that backend chain, the `dsdb_control_current_partition` payload identifying the partition DN, the backend URL, the original `@PARTITION` record blob used to detect newly added partitions, and a `partial_replica` flag used for global-catalog/no-GC search routing.

`struct partition_module` maps an optional partition DN to a module list. A `NULL` DN represents the default module list. `partition_init.c` uses these records to decide which module chain to load for each backend.

`struct partition_metadata` wraps the metadata TDB handle plus in-memory counters for active metadata transactions and recursive read locks.

`struct partition_private_data` is the module-private state shared by all partition implementation files. It contains the sorted partition array, the special-DN replicate list, metadata state, per-partition module mappings, cached primary metadata sequence, global transaction nesting count, an optional forced module configuration message supplied by the higher Samba4 module, and the backend DB store type such as `tdb`.

## Integration Points

The header includes `tdb_wrap.h` because metadata storage is explicitly TDB-backed, even when partition databases may be other backends. It includes `dsdb/samdb/samdb.h` and `dsdb/samdb/ldb_modules/util.h` for DSDB controls, extended operations, and module helper APIs used throughout the implementation.

`partition_proto.h` is generated and supplies cross-file prototypes, so function additions in any implementation file must be reflected by the build's prototype generation process.

## State and Persistence Behavior

The structures in this header define both runtime and persistence-facing state. `backend_url`, `orig_record`, `partial_replica`, and `backend_db_store` are derived from persistent `@PARTITION` metadata. `partition_metadata` points at the persistent `sam.ldb.d/metadata.tdb`. `metadata_seq`, `in_transaction`, and `read_lock_count` are process-local coordination values layered on top of persistent state.

Memory ownership is talloc-based. Most child objects are allocated under `partition_private_data`, individual `dsdb_partition` objects, or their control structures. Correct talloc parentage matters because partitions and their module chains are long-lived module-private state.

## Risks and Edge Cases

Because this header defines shared structs directly, changes are high blast-radius. Adding fields can require updates to initialization, reload, transaction, copy, and teardown paths across all three implementation files.

The sorted partition array and `orig_record` comparison are implicit contracts: routing code assumes ordering, while reload code uses original record blobs to skip already loaded partitions. If DN normalization or record encoding changes, both contracts need review.

`partial_replica` drives visibility under `DSDB_CONTROL_NO_GLOBAL_CATALOG`; incorrect initialization can leak or hide global catalog data.

`partition_metadata` counters must stay consistent with actual TDB transaction/read-lock state. Since the counters are defined here and manipulated across files, mismatched increment/decrement logic can lead to deadlocks or transaction errors.

## Test Signals

Structural test signals are indirect: partition initialization should build correctly sorted `dsdb_partition` arrays, module selection should honor explicit and default `partition_module` records, metadata initialization should populate `partition_metadata`, transaction/read-lock nesting should leave counters balanced, and partial-replica flags should affect search routing. Build tests should ensure `partition_proto.h` remains synchronized after changing cross-file functions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/partition.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/partition_init.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/partition_init.c

## Purpose

`partition_init.c` initializes and refreshes the Samba DSDB partition module's backend list. It reads the `@PARTITION` record, parses partition DNs, replicate entries, per-partition module chains, partial-replica markers, and backend store type, opens backend databases, loads their module chains, registers partitions with rootDSE, and implements the extended operation used to create a new partition.

This file converts persistent partition metadata into the runtime `partition_private_data` that `partition.c` uses for routing and locking.

## Important APIs and Functions

`partition_load_replicate_dns()` parses the `replicateEntries` attribute into validated `ldb_dn` objects for special records that should be copied to every partition.

`partition_load_modules()` parses `modules` values of the form `DN:module,list` or `*:module,list` into `partition_module` entries. `find_modules_for_dn()` later selects the exact DN module list or the default list.

`partition_reload_metadata()` searches `@PARTITION` for `partition`, `replicateEntries`, `modules`, `partialReplica`, and `backendStore`, then refreshes replicate and module mappings. It can use a forced module message from the Samba4 wrapper instead of DB-stored module declarations.

`new_partition_from_dn()` creates a `dsdb_partition`: it computes a relative backend path, creates the backend directory when writable, builds the backend URL, connects the backend, loads the configured module list, initializes the chain, wraps it in a synthetic `partition_next` module, and starts a transaction on the new backend if the partition module is already in a transaction.

`add_partition_to_data()` appends a partition, sorts the partition list by DN, and registers the partition with rootDSE through `partition_register()`.

`partition_reload_if_required()` compares the primary sequence number with cached `metadata_seq`; when changed, it initializes metadata TDB, reloads `@PARTITION`, creates any newly declared partitions, detects partial replicas, and preserves canonical DN case by searching the new backend root.

`new_partition_set_replicated_metadata()` copies configured special metadata records from the main partition into a new backend, replacing existing records when necessary.

`partition_create()` handles `DSDB_EXTENDED_CREATE_PARTITION_OID`: it adds a new `partition` value to `@PARTITION`, optionally records `partialReplica`, creates the backend, copies replicated metadata, and inserts the new runtime partition.

`partition_init()` performs initial reload, registers domain-scope and search-options controls, and then calls the next module init.

## Control Flow

Reload is sequence-driven. `partition_reload_if_required()` obtains the primary sequence number and returns early if unchanged. On change, it ensures `metadata.tdb` exists, reads `@PARTITION`, refreshes metadata fields, and iterates `partition` attribute values. Existing partitions are skipped first by exact original record blob comparison and then by DN comparison.

Partition values can include an explicit `DN:filename.ldb` suffix. Without a filename, the code generates one from the DN, using plain DN text only for a narrow safe character set and base64 encoding otherwise. `partition_create()` uses a similar but URL-escaped filename under `sam.ldb.d/`.

After opening a new backend, the code searches the backend root with no attrs. If found, it replaces the control DN with the case-preserved DN from the database. It then marks partial replicas based on `partialReplica` values and adds/registers the partition.

The create-partition extended operation first reloads metadata to avoid stale state, checks whether the partition already exists, modifies `@PARTITION` if needed, creates the backend runtime object, copies replicated metadata, and only then publishes it into the module-private partition array.

## State and Persistence Behavior

Persistent inputs are the `@PARTITION` record and the backend databases it names. Persistent writes occur when `partition_create()` modifies `@PARTITION` and when `new_partition_set_replicated_metadata()` populates records in a newly created backend. `partition_reload_if_required()` also initializes `sam.ldb.d/metadata.tdb` through `partition_metadata_init()` if it is missing.

Runtime state is talloc-owned by `partition_private_data`. `metadata_seq` tracks the primary DB sequence that last drove reload. `orig_record` stores the exact partition attribute value to distinguish already loaded partition records.

If reload or creation happens while a global transaction is active, `new_partition_from_dn()` starts a transaction on the new backend so later transaction end/abort calls remain balanced.

## Dependencies and Integration Points

The file depends on DSDB module search helpers, LDB backend connection/loading APIs, generated module-list parsing, rootDSE partition registration, `ldb_relative_path()`, loadparm-backed backend options, `ldb_wrap.h`, filesystem directory creation, URL/base64 escaping helpers, and partition metadata helpers.

It is coupled to `partition.c` through sorted partition ordering and to `partition_metadata.c` through sequence-driven reload and metadata TDB initialization.

## Risks and Edge Cases

Parsing `@PARTITION` is sensitive. Invalid DNs, malformed `modules` records without `:`, unsafe filenames, or missing module mappings fail initialization/reload. Since partitions can be discovered during locks/transactions, failure paths must preserve transaction balance.

Filename generation intentionally avoids shell metacharacters and path traversal. Changes here need security review because partition values ultimately influence backend paths.

`partition_reload_if_required()` only adds new partitions; it does not remove partitions whose metadata disappeared. That may be deliberate for long-lived process safety, but it matters for any future dynamic removal work.

The initial metadata TDB migration path creates the DB but relies on later sequence increment logic to populate sequence values. Sequence-number consumers must tolerate zero.

`new_partition_set_replicated_metadata()` performs delete/re-add replacement for existing replicated metadata. Midway failures can leave a new partition partially initialized unless enclosed by transaction behavior.

## Test Signals

Tests should cover valid and invalid `@PARTITION` parsing, explicit and generated backend filenames, module mapping with exact DN and default `*`, forced module messages, reload no-op when sequence is unchanged, discovering a new partition after sequence change, partial-replica marking, canonical DN case replacement, rootDSE registration, create-partition with and without partial-replica control, copied replicated metadata including replacement of existing records, transaction-active partition creation, read-only initialization, and error paths for missing backend modules or invalid replicate DNs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/partition_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/partition_metadata.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/partition_metadata.c

## Purpose

`partition_metadata.c` manages `sam.ldb.d/metadata.tdb` for the DSDB partition module. The TDB stores global sequence metadata, including `SEQ_NUM` and the schema sequence key, and provides the lock semantics used by `partition.c` to coordinate reads and commits across multiple independently locked partition databases.

The file intentionally uses TDB for metadata even when partition backends can be different database types, because the partition module relies on TDB read/write lock blocking semantics for cross-partition consistency.

## Important APIs and Functions

`partition_metadata_get_uint64()` fetches a TDB key, parses it as an unsigned 64-bit decimal value, and returns a caller-provided default if the key does not exist.

`partition_metadata_set_uint64()` stores a decimal unsigned 64-bit value using `TDB_INSERT` or `TDB_MODIFY`.

`partition_metadata_inc_schema_sequence()` increments `DSDB_METADATA_SCHEMA_SEQ_NUM` inside an active metadata transaction, falling back from modify to insert when the key is missing.

`partition_metadata_open()` opens `sam.ldb.d/metadata.tdb`, optionally creating `sam.ldb.d`, applying loadparm TDB flags plus `TDB_SEQNUM`, respecting `LDB_FLG_NOSYNC`, and mapping permission errors to `LDB_ERR_INSUFFICIENT_ACCESS_RIGHTS`.

`partition_metadata_init()` allocates `partition_metadata`, opens the DB if present, or creates it as a migration path when missing.

`partition_metadata_sequence_number()` returns `SEQ_NUM` under a full partition read lock so the sequence observed is not ahead of the visible partition state.

`partition_metadata_sequence_number_increment()` requires an active metadata transaction, initializes `SEQ_NUM` from the older sum-of-partitions sequence if the stored value is zero, increments it, and stores the result.

`partition_metadata_read_lock()` and `partition_metadata_read_unlock()` implement recursive read-lock accounting around `tdb_lockall_read()`/`tdb_unlockall_read()`, avoiding lock operations while a TDB transaction is active.

`partition_metadata_start_trans()`, `partition_metadata_prepare_commit()`, `partition_metadata_end_trans()`, and `partition_metadata_del_trans()` wrap TDB transaction start, prepare, commit, and cancel while maintaining `in_transaction`.

## Control Flow

Initialization is lazy. Callers ensure `partition_private_data` exists, then `partition_metadata_init()` creates the metadata wrapper and attempts an existing open. If the file is missing, it creates the directory/file and leaves sequence keys to be filled by later transaction-time increments.

Sequence reads call back up to `partition_read_lock()`, which locks all databases in the ordering defined by `partition.c`, then reads `SEQ_NUM` defaulting to zero, and unlocks. Sequence increments are only allowed inside a metadata transaction. If `SEQ_NUM` is zero, the code obtains the legacy sum of primary and partition sequence numbers and inserts that as the starting value before incrementing.

Schema sequence increments mirror regular sequence handling but use `DSDB_METADATA_SCHEMA_SEQ_NUM` and are triggered by the schema-update extended operation in `partition.c`.

Transaction functions are thin wrappers around TDB APIs, but their counters are part of the module's correctness contract. Prepare does not decrement the transaction count; commit/cancel do.

## State and Persistence Behavior

Persistent state lives in `sam.ldb.d/metadata.tdb`. Values are stored as decimal strings rather than binary integers. The primary key in this file is `SEQ_NUM`; schema sequence uses the DSDB metadata schema sequence key from Samba headers.

Process-local state includes the `tdb_wrap` pointer, `in_transaction`, and `read_lock_count`. `read_lock_count` allows nested read locks to avoid repeated TDB lock calls and ensures only the outermost unlock releases the TDB read lock when no transaction is active.

## Dependencies and Integration Points

The file depends on TDB/TDB wrap, loadparm TDB flags, `ldb_relative_path()`, filesystem `stat()`/`mkdir()`, Samba string-to-integer conversion, and functions implemented in `partition.c` such as `partition_read_lock()` and `partition_sequence_number_from_partitions()`.

It is called by partition transaction/read-lock paths and by partition extended operations for sequence number and schema update handling.

## Risks and Edge Cases

All mutation APIs require `data->metadata->in_transaction > 0`. Calling sequence increments outside the partition transaction flow fails with operations errors.

`partition_metadata_set_uint64()` chooses strict insert or modify. Missing-key modify failures are handled explicitly for schema sequence but not for regular post-initialization increments after the zero migration path. Any unexpected key loss after initialization could surface as an operations error.

Read-lock accounting assumes balanced lock/unlock calls. `partition_metadata_read_unlock()` decrements even when the count is not one; underflow or unlock-without-lock would corrupt the counter and can cause mismatched TDB locking.

`partition_metadata_sequence_number()` recursively enters the higher-level partition read-lock path from metadata code. This is intentional for visibility consistency, but changes to lock ordering can create deadlocks.

The error string in the parse failure path contains a typo (`converision`), which is harmless but visible in diagnostics.

Creation mode uses `O_CREAT` but opens read/write and mode `0660`; deployments with unexpected permissions can fail initialization before partitions are available.

## Test Signals

Tests should cover opening existing metadata, creating missing metadata during migration, permission-denied mapping, reading absent `SEQ_NUM` as zero, incrementing sequence within and outside transactions, initializing zero sequence from legacy partition sums, schema sequence insert-then-modify behavior, transaction prepare/commit/cancel counter balance, nested metadata read locks, sequence reads under concurrent writer transactions, `LDB_FLG_NOSYNC` flag propagation, and recovery from TDB store/fetch errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/partition_metadata.c -->
