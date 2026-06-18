# Research: subset-b-009916

This grouped report covers Samba DSDB SAMDB module helpers, VLV pagination, SAMDB connection/security-token interfaces, and schema support files assigned to `subset-b-009916`. Each source file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/util.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/util.c

## Purpose
`util.c` is the shared helper layer for Samba AD DS LDB modules. It centralizes synchronous wrapper calls into the next, top, or current module; DSDB control attachment; common DN/GUID lookups; optional feature checks; partition USN metadata reads/writes; request callback chaining; dSHeuristics policy checks; single-valued modify analysis; schema objectClass helpers; and password-attribute scrubbing.

## Important APIs, Types, and Functions
The request wrappers are `dsdb_module_search_dn`, `dsdb_module_search_tree`, `dsdb_module_search`, `dsdb_module_extended`, `dsdb_module_modify`, `dsdb_module_rename`, `dsdb_module_add`, and `dsdb_module_del`. GUID/DN helpers include `dsdb_module_obj_by_guid`, `dsdb_module_dn_by_guid`, `dsdb_module_guid_by_dn`, `dsdb_module_reference_dn`, `dsdb_module_find_ntdsguid_for_computer`, and `dsdb_module_rid_manager_dn`. State and policy helpers include `dsdb_module_load_partition_usn`, `dsdb_module_save_partition_usn`, `dsdb_module_am_system`, `dsdb_module_am_administrator`, `dsdb_have_system_access`, `dsdb_check_samba_compatible_feature`, `dsdb_check_optional_feature`, `dsdb_recyclebin_enabled`, `dsdb_block_anonymous_ops`, `dsdb_user_password_support`, `dsdb_do_list_object`, `dsdb_attribute_authz_on_ldap_add`, and `dsdb_block_owner_implicit_rights`. Attribute/value helpers include the `dsdb_msg_constrainted_update_*` and `dsdb_module_constrainted_update_*` families, `dsdb_get_expected_new_values`, `dsdb_msg_add_get_single_value`, and `dsdb_msg_get_single_value`. Schema/object helpers include `dsdb_get_last_structural_class`, `dsdb_get_structural_oc_from_msg`, `dsdb_get_parent_class`, `dsdb_is_subclass_of`, `dsdb_fix_dn_rdncase`, `dsdb_make_object_category`, and `dsdb_remove_password_related_attrs`.

## Control Flow and Behavior
The wrapper functions allocate a temporary talloc context, build an LDB request with the appropriate default callback, attach DSDB controls via `dsdb_request_add_controls`, optionally mark the request trusted, dispatch to `ldb_next_request`, `ldb_request`, or the current module operation based on `DSDB_FLAG_NEXT_MODULE`, `DSDB_FLAG_TOP_MODULE`, or `DSDB_FLAG_OWN_MODULE`, then synchronously wait with `ldb_wait`. Search helpers enforce base-result counts where needed and reject cross-partition searches that combine a base DN with `DSDB_SEARCH_SEARCH_ALL_PARTITIONS`.

GUID helpers search across all partitions with recycled and storage-format visibility where needed, then use extended DN components to extract GUIDs. Partition USN helpers access the special `@REPLCHANGED` record under `DSDB_CONTROL_CURRENT_PARTITION_OID`; missing records are interpreted as zero on load, while save tries modify first and falls back to add. dSHeuristics helpers read the directory service object below Configuration and interpret fixed character offsets for anonymous blocking, userPassword support, List Object mode, attribute authorization on LDAP add, and owner implicit-right blocking.

## State and Persistence Behavior
Most helpers are transient request builders, but several touch persistent DSDB state. `dsdb_module_save_partition_usn` persists `uSNHighest` and optionally `uSNUrgent` into `@REPLCHANGED` for a partition. Optional feature checks read `msDS-EnabledFeature` references from the local NTDS Settings object and resolve feature GUIDs. Samba compatible feature checks read `@SAMBA_DSDB`. Constrained numeric updates build delete/add modify messages so callers can rely on backend compare semantics instead of blind replace. `dsdb_make_object_category` may preserve or strip extended DN components depending on the `DSDB_EXTENDED_DN_STORE_FORMAT_OPAQUE_NAME` opaque.

## Dependencies and Integration Points
The file depends on LDB request APIs, talloc, Samba DSDB controls, generated `util_proto.h`, `dsdb/common/util.h`, schema query APIs, security/session helpers, GUID and DN parsing, and Samba-specific controls from `samdb.h`. It is used broadly by modules such as ACL, objectclass, repl_meta_data, linked_attributes, schema modules, RID allocation, and operational modules that need to re-enter the LDB stack safely and consistently.

## Risks and Edge Cases
The wrapper flags must be mutually coherent; `DSDB_FLAG_OWN_MODULE` asserts when neither next nor top is selected. Synchronous waits inside module code can deadlock or violate async expectations if used in the wrong callback context. `dsdb_module_search_tree` only enforces `DSDB_SEARCH_ONE_ONLY` after the lower search has run, so expensive multi-result searches still happen. Partition USN save reuses request/control state around the modify-to-add fallback and depends on correct talloc lifetimes. dSHeuristics interpretation is positional and defaults to conservative behavior when the value is absent or too short. `dsdb_msg_get_single_value` models final single-valued state but intentionally leaves backend delete-value mismatch checking to lower layers. `dsdb_fix_dn_rdncase` mutates DN components in place and assumes uppercasing attribute names is always the desired normalization.

## Test Signals
Useful coverage includes wrapper dispatch for next/top/own module paths, control propagation, trusted marking, search count validation, GUID lookup over recycled/cross-partition objects, missing and existing `@REPLCHANGED` records, modify-to-add USN save fallback, feature checks with dangling feature DNs, dSHeuristics absent/short/explicit values, constrained numeric update compare failures, mixed ADD/DELETE/REPLACE value modeling, structural objectClass extraction, objectCategory generation with and without extended-DN storage, and password attribute removal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/util.h -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/util.h

## Purpose
`util.h` declares the DSDB LDB module helper interface and module-specific request flags used by the implementation in `util.c` and related helper sources.

## Important APIs, Types, and Functions
It forward-declares DSDB, security, NETLOGON, and extended-operation types; defines `enum system_control_strip_critical`; includes generated `util_proto.h`; and exposes flag constants `DSDB_FLAG_NEXT_MODULE`, `DSDB_FLAG_OWN_MODULE`, `DSDB_FLAG_TOP_MODULE`, `DSDB_FLAG_TRUSTED`, `DSDB_FLAG_REPLICATED_UPDATE`, and `DSDB_FLAG_FORCE_ALLOW_VALIDATED_DNS_HOSTNAME_SPN_WRITE`.

## Control Flow and Behavior
The header does not implement control flow. Its flags drive the dispatch and control-attachment branches in the helper implementation, selecting whether a helper re-enters the next module, top-level LDB stack, or current module operation and whether the resulting request is trusted or replication-related.

## State and Persistence Behavior
There is no runtime state. The persistent behavioral contract is ABI/API level: many LDB modules compile against these declarations and generated prototypes.

## Dependencies and Integration Points
It pulls in generated NDR misc/security types, DSDB common utilities, NETLOGON definitions, and the generated `dsdb/samdb/ldb_modules/util_proto.h`. It is included by DSDB module sources that need common request wrappers or policy helpers.

## Risks and Edge Cases
The high-bit flag values must not collide with common DSDB request flags consumed by `dsdb_request_add_controls`. Any signature drift in `util_proto.h` affects many modules. Callers must pass one of next, top, or own flags where helper implementations require an explicit dispatch target.

## Test Signals
Compile tests across DSDB modules are the main signal. Behavioral tests should verify that each flag maps to the intended request path and that added flags continue to be recognized by `dsdb_request_add_controls` or module helper code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/vlv_pagination.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/vlv_pagination.c

## Purpose
`vlv_pagination.c` implements Samba's LDB Virtual List View module. It handles the LDAP VLV request control by caching a sorted search result as object GUIDs, serving requested windows, and returning VLV response controls with a context ID for follow-up requests.

## Important APIs, Types, and Functions
`struct results_store` stores one cached VLV search: context ID, timestamp, GUID array, referrals, lower controls, copied VLV/sort details, and returned controls. `struct private_data` owns a fixed-size cache of `VLV_N_SEARCHES` stores per module connection. `struct vlv_context` binds an active request to a store. Core helpers are `new_store`, `vlv_search_by_dn_guid`, `save_referral`, `send_referrals`, `vlv_gt_eq_to_index`, `vlv_calc_real_offset`, `vlv_results`, `vlv_search_callback`, `copy_search_details`, `vlv_copy_down_controls`, `vlv_search`, `vlv_request_init`, and `ldb_vlv_init`.

## Control Flow and Behavior
`vlv_search` passes through requests without the VLV control. With VLV, it requires a server-sort control and clears VLV criticality locally. A zero-length context ID starts a new lower search that asks only for `objectGUID`, lets the normal sort control order those GUID-bearing entries, strips VLV/sort and ASQ from later per-GUID lookups, and collects entries in `vlv_search_callback`. A non-empty context ID searches the per-connection cache and either serves the cached result, passes through unknown noncritical cookies, or returns `LDAP_UNAVAILABLE_CRITICAL_EXTENSION` for unknown critical cookies.

`vlv_results` computes the target index either from a by-offset request using the Windows-compatible `vlv_calc_real_offset` formula or from a greater-than-or-equal assertion using binary search over the cached sorted GUIDs. It re-fetches each visible row by `<GUID=...>` using the original requested attributes, sends entries, appends a VLV response control, and reports target position/content count.

## State and Persistence Behavior
The module keeps volatile per-LDB-module cache state only. `VLV_N_SEARCHES` limits the number of concurrent cached searches per connection; `new_store` reuses empty slots or evicts the oldest timestamp. The cache stores GUIDs and control copies, not full entry payloads. Returned context IDs are process-local little memory copies of incrementing `uint32_t` values and are not durable across connections, process restarts, or module reinitialization.

## Dependencies and Integration Points
The module integrates with LDB search callbacks, VLV request/response controls, server-side sort controls, ASQ behavior, Samba GUID extraction, LDAP error codes, binary search helpers, and normal DSDB lower-module search behavior. It is built as the `ldb_vlv` module in `wscript_build_server` and registered with `ldb_vlv_init`.

## Risks and Edge Cases
The cache can become stale between the original GUID search and later page windows; missing entries are skipped and the window may be extended by one when possible. Greater-than-or-equal mode assumes the sort attribute exists and has at least one value in the per-GUID lookup; absent values would dereference an empty element. `vlv_copy_down_controls` allocates `num_ctrls` pointers but writes a NULL terminator after filtered controls; when no controls are filtered this requires room for `num_ctrls + 1`, so allocation size is a point to audit. Context ID comparison uses raw in-memory `uint32_t` bytes, which is fine intra-process but not portable as an external format. Unknown noncritical cookies silently fall through to the lower stack. The fixed cache size can evict active client cookies under concurrent use.

## Test Signals
Tests should cover no-VLV pass-through, VLV without sort failure, initial search and follow-up cookie flow, unknown cookie critical/noncritical behavior, by-offset edge cases including 0/0, denominator 0, denominator 1, and offset beyond end, greater-than-or-equal forward and reverse sorting, referral forwarding, stale/deleted objects, ASQ control stripping, cache eviction, and control preservation in final replies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/vlv_pagination.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/wscript_build -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/wscript_build

## Purpose
`wscript_build` defines the non-server build targets for DSDB LDB module helpers and selected cmocka selftests.

## Important APIs, Types, and Functions
It declares the private grouping library `dsdb-module`, subsystem `DSDB_MODULE_HELPERS` from `util.c`, `acl_util.c`, `schema_util.c`, and `netlogon.c`, subsystem `DSDB_MODULE_HELPER_RIDALLOC` from `ridalloc.c`, and binaries `test_unique_object_sids`, `test_encrypted_secrets_tdb`, and conditionally `test_encrypted_secrets_mdb`.

## Control Flow and Behavior
The build script registers helper subsystems and tests with waf. If AD DC build support is enabled, it processes the separate `server` build rule, which loads `wscript_build_server`.

## State and Persistence Behavior
There is no runtime state. Build artifacts and generated prototypes such as `util_proto.h` and `ridalloc.h` are produced by the Samba build system.

## Dependencies and Integration Points
`DSDB_MODULE_HELPERS` depends on `ldb`, `ndr`, `samdb-common`, and `samba-security`. The RID allocation helper depends on `MESSAGING`. The selftests depend on talloc, samdb, cmocka, gnutls, and backend-specific flags. This file is the entry point that makes `util.c` available to many DSDB modules.

## Risks and Edge Cases
Adding helper source files without updating subsystem dependencies can cause link failures only in selected build configurations. The LMDB encrypted-secrets test is conditional on `HAVE_LMDB`, so test coverage differs across environments. The AD DC gate controls whether server modules are built at all.

## Test Signals
Signals are successful waf configuration/build, generated prototypes, and selftest availability for `test_unique_object_sids` and encrypted-secrets TDB/LMDB variants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/wscript_build_server -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/wscript_build_server

## Purpose
`wscript_build_server` registers the AD DC server-side DSDB LDB modules and audit-related helper tests. It is included only from the AD DC build path.

## Important APIs, Types, and Functions
It defines `DSDB_MODULE_HELPERS_AUDIT`, cmocka audit/group-audit tests, and many `SAMBA_MODULE` targets including `ldb_samba_dsdb`, `ldb_samba_secrets`, `ldb_objectguid`, `ldb_repl_meta_data`, `ldb_schema_load`, `ldb_schema_data`, `ldb_samldb`, `ldb_rootdse`, `ldb_password_hash`, extended-DN modules, partition modules, objectclass modules, linked attributes, operational/managed password, ACL modules, dirsync, notification modules, `ldb_vlv`, `ldb_paged_results`, `ldb_unique_object_sids`, encrypted secrets, audit log modules, and `count_attrs`.

## Control Flow and Behavior
The script declaratively wires each module source to the `ldb` subsystem with an init function and module init name. Tests with error injection use linker wrapping for JSON helper functions. The VLV source in this work item is built as `ldb_vlv` with init function `ldb_vlv_init` and dependency `samdb-common`.

## State and Persistence Behavior
No runtime state is created by the script itself. It controls which shared/internal module artifacts exist in the build tree and which selftests can be run.

## Dependencies and Integration Points
The module dependency graph ties DSDB modules to `samdb`, `samdb-common`, `DSDB_MODULE_HELPERS`, `DSDB_MODULE_HELPERS_AUDIT`, security/NDR libraries, Kerberos, GSSAPI, messaging, GKDI/GMSA, audit logging, and cmocka tests. This file is the central integration point between source files under `ldb_modules` and Samba's AD DC runtime module stack.

## Risks and Edge Cases
Dependency omissions may only appear in partial builds or when optional libraries are disabled. Tests are AD DC/Jansson dependent, so non-AD builds do not exercise audit helpers. Some module names differ from source basenames, so renames require careful update of init functions and module registration names.

## Test Signals
Primary signals are successful AD DC waf builds, module loadability via `ldb_init_module`, and cmocka test execution for audit, group-audit, unique-object-SID, and encrypted-secrets targets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/wscript_build_server -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/samdb.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/samdb.c

## Purpose
`samdb.c` provides core SAM database connection helpers and AD security-token construction.

## Important APIs, Types, and Functions
`samdb_connect_url` connects to a SAM LDB URL with Samba wrappers, optional shared-context caching, global schema setup, and optional remote-address opaque state. `samdb_connect` is the `sam.ldb` convenience wrapper. `security_token_create` constructs a `security_token` from user SIDs, device SIDs, claims, session flags, and privilege policy.

## Control Flow and Behavior
`samdb_connect_url` always sets `LDB_FLG_DONT_CREATE_DB`, first attempts to reuse a cached wrapper when no remote address is supplied, then initializes and connects a new Samba LDB context. Remote-address connections are deliberately not added to the wrapper cache so audit/netlogon state remains per connection. The `SAMBA_LDB_WRAP_CONNECT_FLAG_NO_SHARE_CONTEXT` flag also bypasses cache insertion.

`security_token_create` initializes a token with claims-evaluation mode derived from loadparm, deduplicates user SIDs, tracks whether claims are valid and whether authentication is compounded, optionally deduplicates device SIDs, assigns simple privileges from well-known token class when requested, otherwise loads privileges from `privilege.ldb`, converts claims only when the Claims Valid SIDs are present, and emits token debug output.

## State and Persistence Behavior
Connection state may be shared through `ldb_wrap_find`/`ldb_wrap_add` unless remote address or no-share flags force uniqueness. `samdb_connect_url` sets the global schema for the context before connecting. Security tokens are in-memory state owned by the caller's talloc context; privilege data is read from persistent `privilege.ldb` through `samdb_privilege_setup`.

## Dependencies and Integration Points
The file integrates with `samba_ldb_init`, `samba_ldb_connect`, LDB wrapper caching, loadparm, auth session info, tsocket addresses, security SID helpers, claims conversion, local privilege setup, and generated SAMDB prototypes. It is central to AD DC code that needs a SAM LDB context or a fully populated access token.

## Risks and Edge Cases
Connection caching is intentionally disabled for remote-address-aware callers; accidentally passing NULL remote address can collapse distinct client contexts. The over-allocation comment in `security_token_create` is followed by immediate realloc growth during deduplication, so allocation behavior depends on realloc success. Device SIDs are considered only for compounded authentication. Claims are ignored unless the corresponding Claims Valid SID is present. Missing privilege DB access fails token creation unless simple privileges were requested.

## Test Signals
Coverage should include cached and uncached SAM DB connections, remote-address opaque storage, no-share flag behavior, connection error string paths, SID deduplication, system/anonymous/builtin-administrator simple privileges, privilege DB failure handling, compounded device SID handling, Claims Valid SID gating, and loadparm-controlled claims evaluation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/samdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/samdb.h -->
# sources/user-network-fs/samba/source4/dsdb/samdb/samdb.h

## Purpose
`samdb.h` is the public DSDB/SAMDB interface header. It defines internal DSDB controls, extended-operation OIDs, replication flags, password-change control payloads, schema and partition constants, opaque names, and feature names used across Samba AD DC modules.

## Important APIs, Types, and Functions
Important definitions include `enum dsdb_password_checked`, `struct dsdb_control_current_partition`, `DSDB_REPL_FLAG_*`, password-change and password-validation controls, metadata/security-descriptor propagation controls, dbcheck controls, GMSA and KDC smartcard reset controls, `struct dsdb_extended_replicated_object`, `struct dsdb_extended_replicated_objects`, partition/rid/schema extended-operation structures, OpenLDAP dereference control structures, `struct samldb_msds_intid_persistant`, extended-DN and encrypted-connection opaques, Samba compatible feature names, and `SAMBA_LDB_WRAP_CONNECT_FLAG_NO_SHARE_CONTEXT`.

## Control Flow and Behavior
The header does not implement code, but it defines the control and extended-operation vocabulary that drives behavior across the LDB module stack. Many controls are module-to-module tokens rather than public LDAP controls, and their criticality/data payload contracts are enforced by individual modules.

## State and Persistence Behavior
Several structures describe persistent or replicated state: replicated object batches, linked attributes, partition DNs, schema metadata sequence names, password policy data, transaction GUIDs, and feature records. Opaque-name constants define in-memory LDB context state such as extended-DN storage format, partition module messages, full join replication completion, and encrypted connection status.

## Dependencies and Integration Points
It includes LDB, generated NDR security/SAMR/DRSUAPI/DRSBLOBS types, schema definitions, auth session structures, DSDB DN utilities, GMSA crypto, DSDB common prototypes, and common flag definitions. This is a high-fanout header used by SAMDB code, LDB modules, replication, KDC/password code, dbcheck, schema, and operational modules.

## Risks and Edge Cases
OID constants are compatibility contracts; changing or reusing them can break module interoperability and persisted controls. Several comments note special-case or internal-only semantics, such as bypassing password hashing, dbcheck repairs, RODC local lockout changes, and tombstone restore behavior. The misspelled `samldb_msds_intid_persistant` type is part of source compatibility. Header fanout means small include changes can produce broad rebuild or dependency cycles.

## Test Signals
Compile coverage across AD DC modules is essential. Behavioral test signals come from replication extended operations, password-change paths, dbcheck fix modes, schema update/load operations, security descriptor propagation, GMSA updates, OpenLDAP dereference handling, and feature negotiation for sorted links, encrypted secrets, and LMDB level one.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/samdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/samdb_privilege.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/samdb_privilege.c

## Purpose
`samdb_privilege.c` loads local privilege and right assignments from Samba's `privilege.ldb` and applies them to a `security_token`.

## Important APIs, Types, and Functions
`privilege_connect` opens `privilege.ldb`. `samdb_privilege_setup_sid` searches privilege records for one SID and applies `privilege` values to a token. `samdb_privilege_setup` handles token-level shortcuts and iterates over all token SIDs.

## Control Flow and Behavior
System, anonymous, and NULL-SID-list tokens are handled without database access. Otherwise the function opens `privilege.ldb`, clears the token privilege mask, then searches each SID as LDAP-encoded NDR `objectSid`. Known privilege names are mapped with `sec_privilege_id`; unknown privilege strings are attempted as rights via `sec_right_bit`, with a debug warning for unrecognized zero mappings.

## State and Persistence Behavior
The persistent source of truth is `privilege.ldb`. The only mutated runtime state is the token's privilege/right bitmask. The database context and search allocations are temporary and freed before return.

## Dependencies and Integration Points
It depends on `ldb_wrap_connect`, generic DB search helpers, LDAP NDR SID encoding, security privilege/right mapping, and loadparm. It is called by `security_token_create` when simple privileges are not requested.

## Risks and Edge Cases
Failure to open `privilege.ldb` returns `NT_STATUS_INTERNAL_DB_CORRUPTION`, which can block token creation. Search results other than exactly one record are treated as no assignment, so duplicate privilege records are silently ignored. Unknown strings can map to right bit zero and only log a warning. Builtin Administrators does not get an unconditional shortcut here; that shortcut exists in the simple-privileges path in `samdb.c`.

## Test Signals
Tests should cover system/anonymous/no-SID shortcuts, missing privilege DB, SID with no record, SID with known privileges, SID with right names, unknown privilege strings, duplicate records, and tokens with multiple SIDs accumulating masks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/samdb_privilege.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/dsdb_dn.c -->
# sources/user-network-fs/samba/source4/dsdb/schema/dsdb_dn.c

## Purpose
`dsdb_dn.c` converts linked-attribute DSDB DNs between Samba's internal `struct dsdb_dn` representation and the DRS binary blob representation used for replicated linked attributes.

## Important APIs, Types, and Functions
The two exported functions are `dsdb_dn_la_to_blob` and `dsdb_dn_la_from_blob`. Both use `struct dsdb_syntax_ctx`, schema attribute syntax handlers, `drsuapi_DsReplicaAttribute`, `drsuapi_DsAttributeValue`, `ldb_message_element`, and `DATA_BLOB`.

## Control Flow and Behavior
`dsdb_dn_la_to_blob` initializes a default syntax context, linearizes the DSDB DN with extended components, wraps it as a one-value LDB element named after the schema attribute, and calls the attribute syntax `ldb_to_drsuapi` converter. It requires exactly one generated DRS value and returns that blob. `dsdb_dn_la_from_blob` builds a one-value DRS attribute around the input blob, calls `drsuapi_to_ldb`, requires exactly one LDB value, and parses it back through `dsdb_dn_parse` using the syntax LDAP OID.

## State and Persistence Behavior
The functions do not persist state directly. They define the conversion boundary for linked-attribute values that are stored or replicated elsewhere. Returned blobs and DNs are talloc-owned by the supplied memory context.

## Dependencies and Integration Points
The file depends on syntax conversion implementations from the schema layer, DSDB DN parsing/linearization, LDB module types, NDR/DRSUAPI types, and SAMDB schema metadata. It integrates with linked-attribute replication and metadata handling.

## Risks and Edge Cases
Correctness depends on the supplied schema attribute matching the linked DN syntax. Converter output counts other than one are treated as internal errors. `dsdb_dn_get_extended_linearized` must return a valid string for blob conversion; parse failure on the way back becomes a generic internal error. Memory ownership of `drs.value_ctr.values[0].blob` follows converter allocation and must remain valid under `mem_ctx`.

## Test Signals
Round-trip tests should cover normal DN, binary DN, string DN, deleted/extended DN components, malformed blobs, converter failures, zero/multiple converted values, and schema attributes with incompatible syntax.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/dsdb_dn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/prefixmap.h -->
# sources/user-network-fs/samba/source4/dsdb/schema/prefixmap.h

## Purpose
`prefixmap.h` declares the in-memory data structures for DSDB prefix maps, which translate between Active Directory ATTID values and OID prefixes.

## Important APIs, Types, and Functions
It defines `enum dsdb_attid_type` for PFM, INTID, reserved, and internal ATTID ranges; `struct dsdb_schema_prefixmap_oid` for one prefix-map entry with an id and partial binary OID; and `struct dsdb_schema_prefixmap` for the prefix array and length.

## Control Flow and Behavior
No code is implemented here. The range categories guide `schema_prefixmap.c` and `schema_query.c` decisions such as whether an ATTID resolves through the prefix map or the `msDS-IntId` index.

## State and Persistence Behavior
The structures are the in-memory representation of prefix maps persisted in the schema NC `prefixMap` attribute and transferred over DRSUAPI. Binary OID blobs are talloc-owned by the containing prefix map.

## Dependencies and Integration Points
The header depends on `DATA_BLOB` being available through including contexts and is included by `schema.h`. It is consumed by schema initialization, prefix-map conversion, syntax conversion, and query lookup code.

## Risks and Edge Cases
The enum ranges encode protocol semantics from MS-ADTS and must remain aligned with `dsdb_pfm_get_attid_type`. Shallow copies of prefix map entries share blob pointers, so callers must respect talloc ownership and lifetime.

## Test Signals
Compile coverage plus prefix-map round trips should verify ATTID range classification, copied prefix lifetimes, and DRS/LDB serialization compatibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/prefixmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/schema.h -->
# sources/user-network-fs/samba/source4/dsdb/schema/schema.h

## Purpose
`schema.h` defines Samba's core in-memory AD schema model: syntax converters, attribute objects, class objects, schema cache state, schema query enums, conversion targets, and the generated schema API include.

## Important APIs, Types, and Functions
Key types are `enum dsdb_dn_format`, `struct dsdb_syntax_ctx`, `struct dsdb_syntax`, `struct dsdb_attribute`, `struct dsdb_class`, `enum schema_set_enum`, `struct dsdb_schema_info`, `struct dsdb_schema`, `enum dsdb_attr_list_query`, `enum dsdb_schema_convert_target`, and `dsdb_schema_refresh_fn`. Attribute/class macros `DSDB_SCHEMA_COMMON_ATTRS`, `DSDB_SCHEMA_ATTR_ATTRS`, and `DSDB_SCHEMA_CLASS_ATTRS` define common LDB load lists.

## Control Flow and Behavior
The header has no executable control flow, but it defines callback contracts for syntax validation and conversion between LDB values and DRSUAPI attributes. `struct dsdb_schema` stores sorted accessor arrays used by binary-search query helpers, FSMO ownership/update state, reload metadata, OID-conversion policy, and schema resolution flags.

## State and Persistence Behavior
`struct dsdb_schema` is a long-lived in-memory cache of persisted schema NC content: prefix map, schemaInfo, linked lists of attributes/classes, sorted indexes, removed-object queues for duplicate handling, FSMO owner state, last-change timestamps, metadata USN, and relaxed OID conversion policy. `struct dsdb_attribute` and `struct dsdb_class` mirror LDAP schema objects plus computed/internal fields such as syntax pointers, LDB schema attributes, possible inferiors, and subclass order.

## Dependencies and Integration Points
The header includes `prefixmap.h` and generated `dsdb/schema/proto.h`, and is included by SAMDB, schema loaders, syntax converters, objectclass modules, replication, and schema query code. Its fields are populated by `schema_init.c`, indexed by schema set code, queried by `schema_query.c`, and formatted by schema description/conversion code.

## Risks and Edge Cases
Because many modules inspect structure fields directly, layout or semantic changes are high risk. Shallow schema copies share many pointed-to strings/blobs and require stable source lifetimes. The distinction between class categories 0/1/2/3, systemOnly, isDefunct, and computed lists drives object validation and must match AD semantics. Relaxed OID conversion and resolving-in-progress flags can hide temporary schema lookup failures during replication.

## Test Signals
Signals include schema load from LDB/DRS, sorted accessor setup, syntax conversion validation, objectClass sorting, possibleInferiors construction, schemaInfo/prefixMap round trips, FSMO owner detection, and module compile coverage against generated prototypes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/schema.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/schema_convert_to_ol.c -->
# sources/user-network-fs/samba/source4/dsdb/schema/schema_convert_to_ol.c

## Purpose
`schema_convert_to_ol.c` linearizes Samba's AD schema into OpenLDAP or Fedora DS schema text, applying caller-supplied mapping rules for skipped names, renamed attributes/classes, and remapped OIDs.

## Important APIs, Types, and Functions
The public entry point is `dsdb_convert_schema_to_openldap`. Internal mapping structures are `struct attr_map` and `struct oid_map`. `print_schema_recursive` emits object classes recursively from `top` down using `schema_class_description` and full attribute-list helpers.

## Control Flow and Behavior
`dsdb_convert_schema_to_openldap` parses the mapping text line by line, ignoring blanks and comments. Lines beginning with a digit map OIDs; nonnumeric `old:new` lines map attribute or objectClass names; bare names are skipped. It fetches the loaded schema from the LDB context, emits all non-skipped attributes with syntax/equality/substring data from the schema syntax table, then recursively emits class descriptions starting at `top`.

## State and Persistence Behavior
No schema state is changed. Output text is allocated under a temporary context, then stolen onto the LDB context before return. Mapping tables are transient.

## Dependencies and Integration Points
The file depends on loaded schema access, schema query helpers, schema description formatting, string-list utilities, locale/ctype functions, and talloc string append helpers. It is used by tooling or provisioning paths that need schema export for non-Samba LDAP backends.

## Risks and Edge Cases
The mapping parser ignores the last line if the mapping string is not newline-terminated because it stops when `strchr(line, '\n')` fails. Remapped OID/name pointers may point into the mutable mapping buffer, so output construction must complete before the temporary context is freed. Recursion assumes a sane class hierarchy below `top`. Skip/remap matching is case-insensitive, but generated schema validity depends on avoiding backend builtin conflicts and unsupported syntax OIDs.

## Test Signals
Tests should cover OpenLDAP and Fedora DS output modes, invalid target handling, skip lines, OID remaps, name remaps, class hierarchy recursion, missing `top`, syntax remapping, non-newline-terminated mapping text, and generated schema accepted by target parsers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/schema_convert_to_ol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/schema_description.c -->
# sources/user-network-fs/samba/source4/dsdb/schema/schema_description.c

## Purpose
`schema_description.c` formats DSDB schema attributes, classes, dITContentRules, and extended info into LDAP-style schema description strings.

## Important APIs, Types, and Functions
Attribute formatting is handled by `schema_attribute_description`, `schema_attribute_to_description`, and `schema_attribute_to_extendedInfo`. Class and rule formatting is handled by `schema_class_description`, `schema_class_to_description`, `schema_class_to_dITContentRule`, and `schema_class_to_extendedInfo`. The `APPEND_ATTRS` macro formats attribute lists with OpenLDAP line wrapping rules.

## Control Flow and Behavior
The generic description helpers build a parenthesized schema string by appending optional fields only when supplied: name, equality, substring, syntax, single-value, no-user-modification, ranges, property GUIDs, indexing, system-only, auxiliary classes, superclass, class category, must/may attributes, and schema GUID. The wrapper functions extract the relevant fields from `dsdb_attribute` or `dsdb_class`, use schema query helpers to compute inherited attributes where needed, and format AD schema subentry strings.

## State and Persistence Behavior
The file is pure formatting logic. It allocates returned strings on the caller's talloc context and does not mutate schema objects.

## Dependencies and Integration Points
It depends on `samdb.h`, NDR GUID helpers, schema query helpers, talloc append helpers, and DSDB schema constants. It feeds schema export, operational schema attributes, and human-readable schema introspection.

## Risks and Edge Cases
The formatter assumes names/OIDs are already valid and does not escape embedded quotes or special characters. `schema_attribute_to_description` assumes `attribute->syntax` is non-NULL. `schema_class_to_dITContentRule` does not guard a missing auxiliary class lookup before passing it to `dsdb_attribute_list`, so corrupt schema can crash. Formatting differences by target can affect backend parser acceptance.

## Test Signals
Tests should cover optional fields, multi-attribute wrapping, all objectClassCategory cases, AD schema subentry output, dITContentRule output with auxiliary classes, GUID/range/index/system-only extended info, unusual names requiring escaping, and missing syntax or auxiliary class error handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/schema_description.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/schema_filtered.c -->
# sources/user-network-fs/samba/source4/dsdb/schema/schema_filtered.c

## Purpose
`schema_filtered.c` decides whether a schema attribute is eligible for inclusion in a filtered replica, such as RODC filtered attribute set behavior.

## Important APIs, Types, and Functions
The policy list `never_in_filtered_attrs` names attributes that must not be in a filtered replica, including secret attributes via `DSDB_SECRET_ATTRIBUTES`. The exported predicate is `dsdb_attribute_is_attr_in_filtered_replica`.

## Control Flow and Behavior
The predicate rejects attributes that are `systemOnly`, critical by `schemaFlagsEx`, not replicated, required partial-set members, constructed, explicitly listed in `never_in_filtered_attrs`, or marked with `SEARCH_FLAG_RODC_ATTRIBUTE`. Anything else is considered eligible.

## State and Persistence Behavior
No state is persisted. The function reads immutable fields from a loaded `dsdb_attribute`; the policy list is static compile-time data.

## Dependencies and Integration Points
It depends on schema attribute structures, DSDB flag definitions, secret attribute macros, and search/schema flag constants. It integrates with replication and schema-management paths that validate or compute filtered attribute sets.

## Risks and Edge Cases
The deny list is exact string comparison and case-sensitive, unlike many LDAP attribute comparisons. Policy correctness depends on the static list staying aligned with Windows and Samba semantics. New secret or operational attributes must be added here or rejected through flags.

## Test Signals
Tests should cover each flag-based rejection, deny-list entries, secret attributes expansion, RODC attribute flag, ordinary eligible attributes, and case-variant attribute names if schema loading can preserve unusual case.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/schema_filtered.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/schema_inferiors.c -->
# sources/user-network-fs/samba/source4/dsdb/schema/schema_inferiors.c

## Purpose
`schema_inferiors.c` computes constructed schema fields related to class hierarchy and possible child object classes, especially `possibleInferiors` and `systemPossibleInferiors`.

## Important APIs, Types, and Functions
The exported entry point is `schema_fill_constructed`. Internal helpers are `schema_supclasses`, `schema_subclasses`, `schema_posssuperiors`, `schema_subclasses_recurse`, `schema_subclasses_order_recurse`, `schema_create_subclasses`, and `schema_fill_possible_inferiors`.

## Control Flow and Behavior
The code first clears temporary caches on every class. `schema_create_subclasses` builds direct subclass lists from each class's `subClassOf`, recursively expands subclass lists, initializes `subClass_order`, and walks from `top` to assign hierarchy depth. For each class, `schema_fill_possible_inferiors` scans all classes and includes non-abstract/non-auxiliary candidates whose computed possible superiors contain the current class. System-only candidates are excluded from `possibleInferiors` but retained in `systemPossibleInferiors`.

## State and Persistence Behavior
The function mutates in-memory computed fields on `struct dsdb_class`: `possibleInferiors`, `systemPossibleInferiors`, `subClass_order`, and temporary `tmp.*` lists. Temporary lists are freed after construction, while computed inferiors remain on the class objects.

## Dependencies and Integration Points
It depends on schema query by LDAP display name and Samba string-list helpers. The file documents that it is a C implementation of the logic in `dsdb/samdb/ldb_modules/tests/possibleInferiors.py`, making that Python test a direct oracle.

## Risks and Edge Cases
Missing `subClassOf` targets or missing `top` abort construction. Recursion assumes the class graph has no problematic cycles except `top SUP top`, which is special-cased. Many list operations do not check every allocation result after appends, so memory pressure can degrade into partial or NULL lists. Computed order drives objectClass sorting elsewhere, so incorrect hierarchy depth can affect validation.

## Test Signals
`possibleInferiors.py` is the key behavioral test. Additional tests should cover `top SUP top`, missing superclass, missing top, abstract/auxiliary exclusion, systemOnly split behavior, inherited possible superiors, subclass order, and schema reload recomputation from a clean cache.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/schema_inferiors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/schema_info_attr.c -->
# sources/user-network-fs/samba/source4/dsdb/schema/schema_info_attr.c

## Purpose
`schema_info_attr.c` implements creation, validation, parsing, serialization, and comparison for the AD `schemaInfo` value carried in schema NC metadata and DRS prefix maps.

## Important APIs, Types, and Functions
Public functions are `dsdb_schema_info_new`, `dsdb_schema_info_blob_new`, `dsdb_schema_info_blob_is_valid`, `dsdb_schema_info_from_blob`, `dsdb_blob_from_schema_info`, and `dsdb_schema_info_cmp`. The wire/storage format is `struct schemaInfoBlob`, whose marker is expected to be `0xFF`.

## Control Flow and Behavior
New schemaInfo objects default to revision zero and GUID zero. New blobs allocate 21 zeroed bytes and set byte zero to `0xFF`. Parsing validates length and marker, NDR-decodes the blob, and copies revision/invocation ID. Serialization builds a `schemaInfoBlob` and NDR-encodes it. Comparison validates the last DRS prefix-map mapping as schemaInfo and accepts local schema revisions newer than the remote, reports schema mismatch for older local revision, reports schema conflict for equal revision but different invocation ID, and otherwise succeeds.

## State and Persistence Behavior
The schemaInfo blob is durable schema metadata stored in the schema NC and included as the final special entry in DRS OID mapping counters. The functions allocate parsed structures/blobs on caller contexts and do not change the schema except through caller assignment.

## Dependencies and Integration Points
It depends on DSDB utilities, SAMDB definitions, module utilities, NDR DRSUAPI/DRSBLOBS definitions, and GUID helpers. It integrates with `schema_init.c` and `schema_prefixmap.c` for prefix-map load/export and replication schema compatibility checks.

## Risks and Edge Cases
Only marker and length are checked before NDR parse. Comparison requires at least one mapping and a final `id_prefix == 0` schemaInfo entry. Equal revisions with different invocation IDs are conflicts; newer local revisions are accepted, which may mask backward compatibility gaps. A NULL `schema->schema_info` would crash callers of comparison.

## Test Signals
Tests should cover new object/blob defaults, invalid NULL/short/long/wrong-marker blobs, NDR parse/push round trips, DRS mapping with missing or malformed final schemaInfo, local newer/older/equal revisions, invocation ID conflicts, and zero revision initial replication behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/schema_info_attr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/schema_init.c -->
# sources/user-network-fs/samba/source4/dsdb/schema/schema_init.c

## Purpose
`schema_init.c` creates, copies, loads, parses, and persists DSDB schema state from LDB and DRS prefix-map inputs.

## Important APIs, Types, and Functions
Schema allocation/copy APIs are `dsdb_new_schema` and `dsdb_schema_copy_shallow`. Prefix-map/schemaInfo APIs include `dsdb_load_prefixmap_from_drsuapi`, `dsdb_load_oid_mappings_ldb`, `dsdb_get_oid_mappings_drsuapi`, `dsdb_get_drsuapi_prefixmap_as_blob`, `dsdb_get_oid_mappings_ldb`, `dsdb_create_prefix_mapping`, `dsdb_write_prefixes_from_schema_to_ldb`, and `dsdb_read_prefixes_from_ldb`. Schema object parsers include `dsdb_attribute_from_ldb`, `dsdb_set_attribute_from_ldb_dups`, `dsdb_set_attribute_from_ldb`, `dsdb_set_class_from_ldb_dups`, `dsdb_set_class_from_ldb`, `dsdb_load_ldb_results_into_schema`, and `dsdb_schema_from_ldb_results`.

## Control Flow and Behavior
Schema creation starts with a zeroed schema. Shallow copy duplicates the prefix map and schemaInfo, memdups class/attribute records, and rebuilds sorted accessors. LDB prefix maps are parsed from `prefixMapBlob`, validated for DSDB version, converted through DRSUAPI prefix-map routines, and paired with validated `schemaInfo`. Prefix-map writes serialize the in-memory map back into the schema NC `prefixMap` attribute via `dsdb_replace` as system.

Attribute and class parsers use macros to read required and optional string, list, bool, uint32, GUID, and blob fields. Attribute parsing maps `attributeID` and `attributeSyntax` OIDs to ATTIDs, resolves syntax, creates an LDB schema attribute, and marks unique/single-valued/indexed flags. Class parsing maps `governsID`, reads superclass/containment/security fields, and adds the class. Duplicate-aware setters queue old schema objects for removal when a new object shares an ID.

`dsdb_schema_from_ldb_results` loads prefixMap and schemaInfo from the schema head, falls back to a default schemaInfo blob if absent, loads all attribute/class messages except the schema head, reads schema FSMO owner, and records whether the local NTDS Settings DN owns the schema FSMO.

## State and Persistence Behavior
The file mutates the in-memory `dsdb_schema` cache, including prefix map, schemaInfo, attributes, classes, sorted-accessor prerequisites, duplicate-removal queues, FSMO state, and schema update policy. It also persists prefix-map updates to the schema partition. `dsdb_create_prefix_mapping` temporarily swaps `schema->prefixmap` to write a new map, then restores the original so later schema reload observes disk state.

## Dependencies and Integration Points
It depends on NDR prefix-map/schemaInfo formats, ASN.1 BER OID helpers, DSDB prefix-map conversion, schema syntax lookup, LDB schema syntax registration, dlink lists, loadparm, `dsdb_replace`, schema accessor setup, and SAMDB DN helpers. It is used by schema FSMO loading, provisioning, replication schema update paths, and schema set/global schema code.

## Risks and Edge Cases
Required fields return `WERR_INVALID_PARAMETER` when absent; DRS replication can supply `name` instead of `cn`, which is specially handled. Prefix-map creation modifies persistent schema state inside a transaction-sensitive path and relies on a later reload to refresh the original schema object. The `GET_BLOB_LDB` macro steals blob data into the parsed object, so message lifetimes and talloc ownership matter. Confidential indexed attributes are deliberately not marked indexed to avoid timing leaks. Missing `schemaInfo` is tolerated with a generated default, but missing `prefixMap` is fatal. Shallow schema copies share many referenced strings and blobs.

## Test Signals
Tests should cover schema load from provision LDIF and live LDB, prefixMap/schemaInfo parse and write round trips, DRS prefix-map load, new prefix creation, required-field failures, `name` fallback for replicated objects, syntax resolution failures, confidential indexed attributes, duplicate replacement queues, FSMO owner detection, update-allowed loadparm, and shallow-copy accessor rebuilds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/schema_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/schema_prefixmap.c -->
# sources/user-network-fs/samba/source4/dsdb/schema/schema_prefixmap.c

## Purpose
`schema_prefixmap.c` implements the DSDB prefix-map algorithms that translate between object/attribute OIDs and DRS ATTID values, and convert prefix maps between internal and DRSUAPI forms.

## Important APIs, Types, and Functions
Public APIs include `dsdb_pfm_get_attid_type`, `dsdb_schema_pfm_new`, `dsdb_schema_pfm_copy_shallow`, `dsdb_schema_pfm_add_entry`, `dsdb_schema_pfm_find_binary_oid`, `dsdb_schema_pfm_find_oid`, `dsdb_schema_pfm_make_attid`, `dsdb_schema_pfm_attid_from_oid`, `dsdb_schema_pfm_oid_from_attid`, `dsdb_schema_pfm_from_drsuapi_pfm`, `dsdb_drsuapi_pfm_from_schema_pfm`, and `dsdb_schema_pfm_contains_drsuapi_pfm`. Internal helpers include `_dsdb_schema_prefixmap_talloc`, `_dsdb_pfm_make_binary_oid`, `dsdb_schema_pfm_make_attid_impl`, and `_dsdb_drsuapi_pfm_verify`.

## Control Flow and Behavior
The initial prefix map is created from the standard AD prefix list defined by MS-DRSR. Full OIDs are BER-encoded, then truncated to a partial binary OID by removing the final subidentifier; that partial prefix is looked up in the map. ATTIDs are composed from the prefix-map entry ID in the high word and a low-word encoding of the final OID subidentifier, with a high bit marker when the subidentifier exceeds 14 bits. Read-only lookup fails if the OID prefix is absent, while make mode adds a new prefix entry and assigns either a nonconflicting remote ID or the next local ID.

OID-from-ATTID reverses that process for prefix-map ATTID ranges, reconstructing the BER OID and decoding it. DRSUAPI conversion verifies mapping arrays, optionally validates/parses a final schemaInfo entry, copies binary OID blobs into internal prefix-map entries, and can append schemaInfo when exporting. Containment comparison checks that a local prefix map contains every remote prefix, excluding the schemaInfo entry.

## State and Persistence Behavior
Prefix maps are in-memory arrays of talloc-owned binary OID prefixes, but they correspond to persisted schema NC `prefixMap` values and DRS replication mapping counters. `dsdb_schema_pfm_add_entry` mutates the map in place by reallocating the prefix array and duplicating the new blob under the map.

## Dependencies and Integration Points
The file depends on ASN.1 BER OID helpers, DRSUAPI/DRSBLOBS generated types, schemaInfo helpers, talloc data blobs, and Samba numeric parsing. It is called by schema initialization, schema syntax conversion, replication, and schema query ATTID resolution.

## Risks and Edge Cases
Only one- or two-byte final subidentifier encodings are handled when trimming and reconstructing OIDs; extremely large final subidentifiers could be invalid or mishandled. `dsdb_schema_pfm_oid_from_attid` rejects INTID/reserved/internal ranges, which must be resolved elsewhere. Shallow copies duplicate entry structs but not blob storage. DRS verification rejects empty OIDs and schemaInfo-like normal entries, but does not enforce unique IDs or prefixes. ATTID low-word truncation for large subidentifiers follows protocol behavior but can be surprising.

## Test Signals
Tests should cover ATTID range classification, standard prefix initialization, OID-to-ATTID and ATTID-to-OID round trips, absent prefix read-only failure, prefix addition and ID allocation, remote ID collision handling, DRS import/export with and without schemaInfo, malformed DRS maps, containment mismatch, and large final OID subidentifier behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/schema_prefixmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/schema_query.c -->
# sources/user-network-fs/samba/source4/dsdb/schema/schema_query.c

## Purpose
`schema_query.c` provides fast lookup and list-building helpers over a loaded DSDB schema, including attribute/class lookup by ID/OID/name, linked-attribute enumeration, full attribute-list computation, schemaIDGUID lookup, and objectClass ordering.

## Important APIs, Types, and Functions
Lookup APIs include `dsdb_attribute_by_attributeID_id`, `dsdb_attribute_by_attributeID_oid`, `dsdb_attribute_by_lDAPDisplayName`, `dsdb_attribute_by_lDAPDisplayName_ldb_val`, `dsdb_attribute_by_linkID`, `dsdb_attribute_by_cn_ldb_val`, `dsdb_class_by_governsID_id`, `dsdb_class_by_governsID_oid`, `dsdb_class_by_lDAPDisplayName`, `dsdb_class_by_lDAPDisplayName_ldb_val`, `dsdb_class_by_cn_ldb_val`, and `dsdb_lDAPDisplayName_by_id`. List helpers include `dsdb_linked_attribute_lDAPDisplayName_list`, `merge_attr_list`, `dsdb_attribute_list`, and `dsdb_full_attribute_list`. GUID helpers are `class_schemaid_guid_by_lDAPDisplayName` and `attribute_schemaid_guid_by_lDAPDisplayName`. `dsdb_sort_objectClass_attr` validates and sorts objectClass values.

## Control Flow and Behavior
Most lookups are binary searches over sorted arrays prepared elsewhere. `dsdb_attribute_by_attributeID_id` routes INTID-range IDs to the `attributes_by_msDS_IntId` index and ignores `0xFFFFFFFF` invalid placeholders. Attribute-list helpers merge may/must/system lists for one class, then recursively include auxiliary classes. Full lists are sorted case-insensitively and deduplicated.

`dsdb_sort_objectClass_attr` validates every supplied objectClass against the schema, rejects defunct classes, inserts `top` once, ensures missing superclass chain elements are present, then orders classes by `subClass_order` while placing structural/type-88 classes after auxiliary/abstract classes at the same hierarchy level. It writes a normalized output message element.

## State and Persistence Behavior
Lookup helpers are read-only against schema state. Attribute-list helpers allocate returned lists on caller contexts. ObjectClass sorting allocates new LDB values on the caller context and does not mutate the schema.

## Dependencies and Integration Points
The file depends on sorted schema accessor arrays, binary-search macros, string-list helpers, dlink lists, and subclass order computed by `schema_inferiors.c`/schema setup. It is used by schema validation, objectclass modules, schema description/export, replication conversion, and access-check code needing schemaIDGUIDs.

## Risks and Edge Cases
Sorted accessor arrays must be current; stale or unsorted arrays produce wrong lookup results. `strcasecmp_with_ldb_val` handles non-NUL-terminated LDB values but assumes string semantics. `dsdb_linked_attribute_lDAPDisplayName_list` sets a NULL terminator only if the allocated slot is not already NULL, which is fragile after `talloc_realloc`. Recursive auxiliary-class list building can loop if schema auxiliary relationships are cyclic. `dsdb_sort_objectClass_attr` relies on valid `subClass_order`; unknown parent chains or missing top can lead to NULL objectclass entries if earlier schema construction failed.

## Test Signals
Tests should cover every lookup index, INTID versus prefix-map ATTID routing, invalid ID handling, non-NUL LDB value lookup, linked-attribute list termination, may/must/system/full attribute lists with auxiliary classes and duplicates, schemaIDGUID lookup misses, objectClass sorting with missing parents, defunct/unknown classes, duplicate top, structural ordering, and cyclic auxiliary-class definitions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/schema_query.c -->
