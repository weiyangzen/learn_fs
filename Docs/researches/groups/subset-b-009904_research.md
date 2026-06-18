<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/util.c -->
# sources/user-network-fs/samba/source4/dsdb/common/util.c

## Purpose
This file is the broad source4 DSDB/SAMDB utility layer for Samba AD DC code. It wraps common LDB searches and mutations, converts LDAP attributes into Samba security and SAMR data types, builds DNs for standard AD containers, caches local domain/server identity values on the `ldb_context`, drives password validation and password modification requests, handles replication metadata helpers, adds DSDB-specific controls to LDB operations, and provides smaller account/default/lockout helpers used by SAMDB modules, DRS replication, authentication, provisioning, and SAMR-compatible code.

## Important APIs, Types, and Functions
Search/result helpers include `samdb_search_domain()`, `samdb_search_string[_v]()`, `samdb_search_dn()`, `samdb_search_dom_sid()`, `samdb_search_uint()`, `samdb_search_int64()`, `samdb_search_string_multiple()`, `dsdb_search_dn()`, `dsdb_search_by_dn_guid()`, `dsdb_search()`, and `dsdb_search_one()`. The `samdb_result_*` family decodes attributes into `struct ldb_dn`, `struct dom_sid`, `struct auth_SidAttr`, `struct GUID`, `NTTIME`, `struct samr_Password`, `struct samr_LogonHours`, account flags, and `lsa_BinaryString` parameter data. Message builders include `samdb_msg_add_dom_sid()`, add/delete value helpers, integer/hash/account/logon-hours/parameter setters, and `samdb_msg_set_uint()`.

DN and identity helpers include `samdb_*_dn()` constructors for schema/config/default-domain containers, GKDI root key DNs, `samdb_domain_sid()`, `samdb_domain_guid()`, `samdb_ntds_settings_dn()`, `samdb_ntds_objectGUID()`, `samdb_ntds_invocation_id()`, `samdb_server_dn()`, `samdb_server_site_dn()`, RID manager/RID set references, site lookup helpers, `samdb_domain_to_dn()`, DNS-domain conversion, `dsdb_find_dn_by_guid()`, `dsdb_find_guid_by_dn()`, `dsdb_find_sid_by_dn()`, and `dsdb_find_dn_by_sid()`. Replication helpers include `dsdb_loadreps()`, `dsdb_savereps()`, `dsdb_load_partition_usn()`, UDV loading in v1/v2 forms, replica cursor comparators, RODC checks, FSMO role lookup, partial-replica NC creation, and DSA GUID validation.

Password and account helpers include `samdb_check_password()`, `samdb_set_password()`, `samdb_set_password_sid()`, `gmsa_system_password_update_request()`, `dsdb_effective_badPwdCount()`, `samdb_result_effective_badPwdCount()`, `dsdb_update_bad_pwd_count()`, `dsdb_user_obj_set_defaults()`, `dsdb_user_obj_set_account_type()`, `dsdb_user_obj_set_primary_group_id()`, `dsdb_is_protected_user()`, and `dsdb_account_is_trust()`. Request/mutation wrappers are `dsdb_request_add_controls()`, `dsdb_request_has_control()`, `dsdb_add()`, `dsdb_modify()`, `dsdb_delete()`, `dsdb_replace()`, and `dsdb_autotransaction_request()`. Error helpers are `dsdb_werror_at()` and `dsdb_ldb_err_to_ntstatus()`.

## Control Flow, State, and Persistence
Most helpers allocate temporary talloc contexts, run an LDB search or build an LDB message/request, steal only the caller-visible result into the caller context, and free scratch state before returning. `dsdb_search()` is the central controlled search wrapper: it builds a request from scope/base/filter/attrs, applies DSDB controls, waits synchronously, enforces `DSDB_SEARCH_ONE_ONLY` when requested, and optionally retries up to five times when `DSDB_SEARCH_UPDATE_MANAGED_PASSWORDS` causes stale gMSA keys to be derived and written before re-searching. `dsdb_add()`, `dsdb_modify()`, and `dsdb_delete()` build operation requests, attach controls, and execute them through `dsdb_autotransaction_request()`, which starts and commits/cancels an LDB transaction around the request.

Several values are cached or forced as LDB opaques: `cache.domain_sid`, `cache.domain_guid`, `forced.ntds_settings_dn`, `cache.ntds_guid`, `cache.invocation_id`, `cache.am_rodc`, `cache.dns_host_name`, and functional-level opaques. These are in-memory per-`ldb_context` state, not durable DB records, but they affect later reads on that context. Persistent state changes happen through LDB add/modify/delete operations: password changes, trust-auth updates, replication metadata writes, functional-level and operating-system updates, partial-replica NC creation, bad-password counter updates, and object default/type/group fields.

Password update flow is layered. `samdb_set_password_request()` builds a modify request that replaces either `clearTextPassword` or `unicodePwd`, adds old-password-checked, smart-card reset, hash-values, trust-permit, and password-change-status controls as needed, and installs `samdb_set_password_callback()` to capture the returned status control. `samdb_set_password_internal()` submits the request, extracts reject/domain data, and maps LDAP errors and embedded WERROR text into NTSTATUS values. `samdb_set_password_sid()` wraps that in a transaction, finds the user by SID, validates `userAccountControl`, handles interdomain trust-account `trustAuthIncoming` rotation when relevant, calls the internal password setter with trust permission, and commits.

## Dependencies and Integration
The file depends on LDB core/module APIs, Samba talloc, generated NDR types for security/misc/DRS blobs, DSDB/SAMDB headers, LDAP NDR helpers, loadparm, gMSA/GKDI helpers, Samba process execution and event APIs for password scripts, flag mappings between AD and SAM account/group semantics, access-list parsing for site subnets, NTSTATUS/WERROR conversion, and auth/security structures. It is an integration point for SAMDB modules, provisioning, password hash modules, SAMR emulation, DRS replication, KDC/gMSA password maintenance, RODC filtering, and DC startup functional-level validation.

## Risks
This file sits on high-impact identity, authorization, password, and replication paths. Key risks are incorrect control flags changing access checks or replication visibility, stale per-context opaque caches after DB/config changes, silent defaulting when attributes are absent, and broad NTSTATUS mappings that can hide exact LDAP causes. Password paths are especially sensitive because script execution, environment variables, trust password history/version handling, hash-vs-plaintext mode, and password-change controls must line up with password_hash module expectations. `dsdb_objects_have_same_nc()` returns `true` on NC lookup errors, which is fail-open for callers using it as a cross-NC guard. `samdb_result_acct_flags()` disables accounts when a computed attribute is missing, which is safe but can be surprising in tests. `dsdb_search()` asserts that all-partition searches do not use a base DN, so misuse can abort in debug/assert builds.

## Test Signals
Useful signals include controlled LDB search wrappers with every DSDB flag, `DSDB_SEARCH_ONE_ONLY` zero/multiple-result errors, add/modify/delete transaction commit and rollback, domain SID/GUID/NTDS cache population and explicit setters, password policy script success/failure/timeout, plaintext and hash password changes, wrong-password and password-restriction mappings, trust-account password rotation with version mismatch, gMSA managed password update retry, RODC/non-RODC branches, functional-level updates including refusal below domain/forest level, SID/GUID extended-DN parsing, NC-root discovery for normal, extended, missing, local, and remote-like DNs, replication blob load/save parse errors, UDV sorting/local cursor injection, badPwdCount lockout thresholds including administrator/trust exemptions, and account default/type/primary group generation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/util.h -->
# sources/user-network-fs/samba/source4/dsdb/common/util.h

## Purpose
This header defines shared DSDB utility constants and a small public surface used by source4 DSDB/SAMDB code. Its main role is to provide the flag bitmask consumed by `dsdb_request_add_controls()` and wrappers such as `dsdb_search()`, `dsdb_add()`, `dsdb_modify()`, and `dsdb_delete()`, plus common secret/password attribute lists and LDB opaque names for session information.

## Important APIs, Types, and Functions
The `DSDB_SEARCH_*`, `DSDB_MODIFY_*`, and `DSDB_FLAG_*` constants map high-level DSDB operation needs to LDB controls. Examples include all-partition search, show deleted/recycled objects, extended DN display, reveal internals, relax/permissive modify, as-system execution, tree delete, provisioning, bypass-password-hash, no-global-catalog, partial replica modify, bypass last-set, replicated link handling, untrusted request marking, and managed-password refresh. `DSDB_SECRET_ATTRIBUTES_EX`, `DSDB_SECRET_ATTRIBUTES`, `DSDB_PASSWORD_ATTRIBUTES`, and `DSDB_AUTHENTICATION_ATTRIBUTES` define sensitive or authentication-relevant attribute lists used by modules and filtering logic. The header declares `dsdb_werror_at()` and convenience macros `dsdb_werror()` and `dsdb_module_werror()`. It also defines `struct dsdb_ldb_dn_list_node`, a linked-list node carrying a partition DN.

## Control Flow, State, and Persistence
There is no runtime control flow in the header. Its flags become runtime behavior only when passed into `dsdb_request_add_controls()` in `util.c`. `DSDB_SESSION_INFO` and `DSDB_NETWORK_SESSION_INFO` name LDB opaque values that other DSDB modules use to pass session/authentication context through the LDB layer. The secret/password/authentication attribute macros do not persist state themselves, but they centralize which attributes are treated as secret or password-adjacent in replication, logging, and filtering code.

## Dependencies and Integration
The header includes `libcli/util/werror.h`, forward-declares `struct GUID` and `struct ldb_context`, and assumes broader Samba include order for LDB and talloc-related types used elsewhere. It is included by `util.c`, SAMR utilities, group expansion, and DSDB modules that need common flags or error-reporting wrappers. The comments note that module-specific high bits for these flags live in `dsdb/samdb/ldb_modules/util.h`, so callers must treat the bit space as shared.

## Risks
The primary risk is flag drift: adding a flag here without implementing it in `dsdb_request_add_controls()` or colliding with module-function high bits can make callers believe a control was applied when it was not. The secret-attribute list is security-sensitive; omissions can leak password or trust material to RODCs/logs/replication paths, while over-inclusion can unnecessarily suppress legitimate attributes. Because many callers combine flags with bitwise OR, test coverage should catch invalid or contradictory combinations.

## Test Signals
Build coverage should catch missing declarations. Runtime tests should verify each public `DSDB_*` flag results in the expected LDB control, secret/password attribute lists match RODC and password logging expectations, `dsdb_werror()` formats WERROR codes into LDB errstrings with call-site data, and `DSDB_MARK_REQ_UNTRUSTED` affects request trust state without requiring an LDB control object.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/util_groups.c -->
# sources/user-network-fs/samba/source4/dsdb/common/util_groups.c

## Purpose
This file implements nested group expansion for source4 DSDB authentication. Given a DN value, it walks transitive `memberOf` links and accumulates the SIDs and SID attributes that should appear in an authorization token or membership result.

## Important APIs, Types, and Functions
The exported function is `dsdb_expand_nested_groups(struct ldb_context *sam_ctx, struct ldb_val *dn_val, bool only_childs, const char *filter, TALLOC_CTX *res_sids_ctx, struct auth_SidAttr **res_sids, uint32_t *num_res_sids)`. It consumes an extended-DN value, expects SID components in those extended DNs, queries `groupType` and `memberOf`, and appends `struct auth_SidAttr` entries with `SE_GROUP_DEFAULT_FLAGS` plus `SE_GROUP_RESOURCE` when `GROUP_TYPE_RESOURCE_GROUP` is set.

## Control Flow, State, and Persistence
The function initializes the result count when the caller's SID array is NULL, validates that a SAM context exists, parses the input DN from the LDB value, extracts the `SID` extended component, minimizes the DN, and searches the object. With `only_childs=true`, it performs a base `dsdb_search_dn()` that does not add the starting object to the result; otherwise it searches with the caller-supplied filter and considers adding the object's SID before recursing. It tolerates missing SIDs for non-SAM objects and missing objects, including a special fallback for foreignSecurityPrincipal SID-DNs that can fail due to duplicate same-SID objects outside the main domain partition. Duplicate entries are avoided with `sids_contains_sid_attrs()`, but the check is a linear O(n) scan for each candidate. The function is read-only; all state is returned through the caller's talloc-owned SID array.

## Dependencies and Integration
It depends on auth SID attribute structures, LDB DN parsing, DSDB extended-DN SID parsing from `util.c`, `dsdb_search()`/`dsdb_search_dn()`, Samba security flags, and AD group-type constants. It integrates with token construction and membership expansion callers that need domain-local/resource-group attributes and nested `memberOf` traversal in source4 authentication.

## Risks
Recursive traversal can become expensive on deep or dense membership graphs, and duplicate detection is O(n^2) overall. Correct behavior depends on callers requesting `DSDB_SEARCH_SHOW_EXTENDED_DN` so `memberOf` values contain SID components. If corrupt extended DN data is present, the function returns corruption-like NTSTATUS errors and token creation can fail. The foreignSecurityPrincipal fallback intentionally hides some no-such-object cases, which is useful for compatibility but can obscure directory inconsistency.

## Test Signals
Tests should cover a user DN expanded only through parent groups, direct group expansion including the group itself, nested groups with duplicates, domain-local/resource-group SID attributes, foreignSecurityPrincipal fallback by SID, non-SAM objects without SIDs, corrupt extended SID components, filter mismatch returning no SID, missing `sam_ctx`, and deep nesting/performance behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/util_groups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/util_links.c -->
# sources/user-network-fs/samba/source4/dsdb/common/util_links.c

## Purpose
This file provides helpers for comparing and locating linked-attribute DNs stored in DSDB. It supports replication-compatible ordering by NDR GUID byte order, lazy parsing of trusted DN values, and binary-search lookup of existing links by GUID plus optional link metadata/extra-part comparison.

## Important APIs, Types, and Functions
`ndr_guid_compare()` serializes two `struct GUID` values into fixed NDR blobs and compares the raw blob bytes, matching DRS replication ordering rather than `GUID_compare()` ordering. `really_parse_trusted_dn()` converts a stored `struct ldb_val` into a trusted `struct dsdb_dn`, extracts its `GUID` extended component, and fills a `struct parsed_dn`. `get_parsed_dns_trusted()` allocates an array of `struct parsed_dn` entries and stores value pointers without parsing immediately. `parsed_dn_find()` searches a sorted parsed-DN array for a target GUID and returns exact and next insertion-point pointers. The static comparator `la_guid_compare_with_trusted_dn()` lazily parses database-side DNs and optionally compares `dsdb_dn->extra_part` exactly or by prefix.

## Control Flow, State, and Persistence
The common path builds a `compare_ctx` containing the target GUID, LDB context, LDAP syntax OID, optional extra part, partial-prefix length, and error field. `BINARY_ARRAY_SEARCH_GTE()` calls the comparator, which parses entries on demand and sets `ctx.err` if parsing fails. If a target GUID is all zero, `parsed_dn_find()` cannot use the sorted GUID key; it logs the replication edge case, requires a target DN, linearly parses and compares by DN, and if no match is found returns the beginning of the list as the insertion point. The helpers do not write persistent state; they mutate only the caller-owned parsed array by caching parsed `dsdb_dn` and `guid` fields.

## Dependencies and Integration
The code depends on DSDB DN parsing (`dsdb_dn_parse_trusted()`), extended-DN GUID extraction, NDR GUID serialization, Samba binary-search helpers, data-blob comparison, and LDB DN comparison. It is used by linked-attribute and replication metadata paths that must preserve Windows/DRS sort order for link values and identify links efficiently during add/delete/update processing.

## Risks
Correctness depends on the input array already being sorted with the same NDR GUID ordering. Parse errors are reported through a compare-function side channel where zero can mean either equality or error, so callers must check the final returned LDB code. Prefix matching of `extra_part` is intentional but easy to misuse if the caller expects full metadata equality. NULL GUID fallback is best-effort and can place an unknown deleted link at the start of the list, so replication edge cases should be logged and tested.

## Test Signals
Tests should compare `ndr_guid_compare()` against known NDR byte-order examples, lazy parsing success and failure, binary search exact hit/miss/insertion point, extra-part exact comparison, partial extra-part prefix comparison, all-zero GUID with matching and missing target DN, all-zero GUID without target DN returning an operations error, and behavior when a stored trusted DN lacks a GUID component.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/util_links.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/util_links.h -->
# sources/user-network-fs/samba/source4/dsdb/common/util_links.h

## Purpose
This header exposes the shared data structures used by DSDB linked-attribute search helpers. It lets callers prepare parsed-DN arrays and comparator context while hiding most implementation details in `util_links.c`.

## Important APIs, Types, and Functions
`struct compare_ctx` carries the target GUID, LDB context, talloc context, LDAP syntax OID, error code, invocation ID, extra-part blob, partial extra-part length, and comparison mode for linked-attribute searches. `struct parsed_dn` stores a lazily parsed `struct dsdb_dn`, the extracted GUID, and the original LDB value pointer. The only declared function is `get_parsed_dns_trusted(TALLOC_CTX *mem_ctx, struct ldb_message_element *el, struct parsed_dn **pdn)`, which builds the array shell from an LDB message element.

## Control Flow, State, and Persistence
There is no runtime logic in the header. The structures are caller-owned talloc state used during a single linked-attribute operation. `parsed_dn` intentionally permits deferred parsing by leaving `dsdb_dn` NULL until `util_links.c` needs the GUID or DN.

## Dependencies and Integration
The header assumes surrounding Samba includes provide `struct GUID`, `struct ldb_context`, `TALLOC_CTX`, `DATA_BLOB`, `bool`, `struct dsdb_dn`, `struct ldb_val`, and `struct ldb_message_element`. It is paired with `util_links.c` and integrated into DSDB link metadata/replication modules that need a common representation of link values.

## Risks
Because only `get_parsed_dns_trusted()` is declared here, any caller using `struct compare_ctx` directly is tightly coupled to `util_links.c` internals. The header relies on include order for type definitions. Mismanaging the lifetime of `struct ldb_message_element` values referenced by `parsed_dn.v` can leave dangling pointers.

## Test Signals
Build tests should cover include order through real DSDB modules. Runtime link tests should verify that arrays from `get_parsed_dns_trusted()` remain valid while the source LDB message is alive, are safely empty for zero values, and interact correctly with `parsed_dn_find()` in the implementation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/util_links.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/util_samr.c -->
# sources/user-network-fs/samba/source4/dsdb/common/util_samr.c

## Purpose
This file implements SAMR-style account, group, alias, membership, and RID lookup helpers on top of the source4 DSDB/SAMDB LDB database. It is used by the SAMR server and by `pdb_samba4` migration/compatibility code to create AD objects with SAM-compatible semantics.

## Important APIs, Types, and Functions
`dsdb_add_user()` creates a user or computer account for exact account flags `ACB_NORMAL`, `ACB_WSTRUST`, or `ACB_SVRTRUST`, optionally forcing an object SID for migration, and returns the new DN and optional SID. `dsdb_add_domain_group()` creates a security group under `CN=Users` and returns its SID and DN. `dsdb_add_domain_alias()` creates a domain-local security group alias by setting `groupType` to `GTYPE_SECURITY_DOMAIN_LOCAL_GROUP`. `dsdb_enum_group_mem()` reads a group's `member` attribute with extended DNs and returns member SIDs, skipping non-SAM members without SIDs. `dsdb_lookup_rids()` maps RIDs under a domain SID to SAM account names and LSA SID types using `sAMAccountType`.

## Control Flow, State, and Persistence
`dsdb_add_user()` creates a temporary context, LDAP-escapes the account name, starts a transaction, checks for an existing user with the same `sAMAccountName`, chooses object class and well-known container based on account flags, strips trailing `$` from computer CNs, sets disabled/password-not-required UAC bits, resolves the Users/Computers/Domain Controllers container by well-known GUID, builds an add message, optionally adds a forced `objectSID`, calls `ldb_add()`, searches the new object for `objectSid` and `userAccountControl`, commits, and steals results to the caller. On most failures it cancels the transaction and maps LDB errors to SAMR-facing NTSTATUS values.

`dsdb_add_domain_group()` checks for duplicates, builds `CN=<group>,CN=Users,<defaultDN>`, adds `sAMAccountName` and `objectClass=group`, calls `ldb_add()`, then searches the new object's `objectSid`. It does not explicitly wrap its add and lookup in a transaction. `dsdb_add_domain_alias()` does use a transaction around duplicate check, add, SID lookup, and commit. `dsdb_enum_group_mem()` searches a group base DN for `member` with extended DNs, parses each member DN value, extracts the `SID` component into a caller-owned array, and compacts out contacts/non-SAM objects by incrementing the output count only on SID success. `dsdb_lookup_rids()` loops over each RID, builds a `<SID=...>` DN, searches for `sAMAccountName=*`, maps `sAMAccountType` through `ds_atype_map()`, and returns all/some/none mapped status.

## Dependencies and Integration
The file depends on `dsdb/samdb/samdb.h`, `dsdb/common/util.h`, AD account flag mappings, Samba security SIDs, well-known container GUIDs, LDB transactions/search/add operations, and `ds_atype_map()`. It integrates with SAMR create/open/enumerate flows and migration paths that need source4 AD objects to behave like SAM database users, computers, groups, aliases, and RID lookup targets.

## Risks
Creation helpers rely on pre-checks plus LDB uniqueness; duplicate races are handled by add failures, but only user and alias paths are transaction-wrapped. Some error paths in `dsdb_add_user()` return `NT_STATUS_FOOBAR` for malformed trust-account names, which is imprecise. The alias duplicate search filter appears malformed (`"(sAMAccountName=%s)(objectclass=group))"` lacks an outer `&(`), so duplicate detection may depend on downstream parser behavior rather than the intended conjunction. `dsdb_add_domain_alias()` allocates `msg->dn` on `mem_ctx` while most scratch state is on `tmp_ctx`, which is intentional for stealing but broadens lifetime before commit. Membership enumeration trusts extended DN SID components; missing or corrupt components affect results.

## Test Signals
Tests should cover normal user creation, workstation/server trust creation requiring trailing `$`, invalid account flags including domain trust rejection, forced SID migration, duplicate user/group/alias handling, access-denied and unwilling-to-perform mappings, transaction rollback on user/alias failure, group creation SID retrieval, alias groupType persistence, group membership with users, contacts, foreign security principals, and corrupt member DNs, plus `dsdb_lookup_rids()` for all mapped, some mapped, none mapped, missing `sAMAccountName`, and unknown `sAMAccountType`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/util_samr.c -->
