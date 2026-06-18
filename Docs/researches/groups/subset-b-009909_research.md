# subset-b-009909 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/extended_dn_out.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/extended_dn_out.c

## Purpose
`extended_dn_out.c` is an LDB search-response module that turns Samba DSDB storage DNs into client-visible DNs. It optionally injects `<GUID=...>` and `<SID=...>` components into returned object DNs, normalizes DN/RDN and attribute-name case, rewrites DN-valued attributes, and hides deleted or internal link values unless the caller has reveal-style controls. It is the output-side companion to `extended_dn_store.c`.

## Important APIs, types, and functions
The module private state is `struct extended_dn_out_private`, holding `dereference`, `normalise`, and `attrs`; only `normalise` and the store-format opaque are materially used in this file. `struct extended_search_context` carries the request, schema, injection flags, attribute-removal flags, and requested extended-DN type.

Key helpers are `copy_attrs()` and `add_attrs()` for safely extending a requested attribute list, `inject_extended_dn_out()` for setting `GUID` and optional `SID` extended components on `ares->message->dn`, and `fix_one_way_link()` for resolving one-way DN links by GUID so renamed targets are returned with current DN components. The main callback is `extended_callback()`, installed by `extended_dn_out_search()`. Module registration exports `ldb_extended_dn_out_module_init()` with ops named `extended_dn_out_ldb`.

## Control flow
`extended_dn_out_ldb_search()` calls `extended_dn_out_search()`. Special DNs bypass the module. The search path inspects `LDB_CONTROL_EXTENDED_DN_OID` and `DSDB_CONTROL_DN_STORAGE_FORMAT_OID`; if either requires extended output it records the requested `struct ldb_extended_dn_control` type and ensures `objectGUID` and possibly `objectSid` are requested from lower modules even if the client did not ask for them. Those temporary attributes are removed after DN injection.

`extended_callback()` forwards referrals and done replies, then processes each entry. It optionally normalizes the entry DN, injects GUID/SID, regenerates `distinguishedName`, and walks every schema-known DN-valued attribute. Deleted linked values and hidden backlinks are skipped unless reveal controls apply. DN values are parsed via `dsdb_dn_parse_trusted()`, one-way links are resolved by GUID, internal extended components are filtered to GUID/SID for ordinary callers, and values are replaced with either extended or plain linearized forms.

## State and persistence behavior
This module does not persist changes. It mutates transient reply messages and DN value blobs before forwarding them to the original request callback. Its only lasting process state is an LDB opaque, `DSDB_EXTENDED_DN_STORE_FORMAT_OPAQUE_NAME`, set during init to advertise that DNs are stored in extended form.

## Dependencies and integration points
The module depends on DSDB schema lookup, DN parsing and rendering helpers, `dsdb_fix_dn_rdncase()`, GUID/SID extended component helpers, and internal DSDB search flags such as `DSDB_SEARCH_SHOW_DELETED`, `DSDB_SEARCH_SHOW_RECYCLED`, and `DSDB_SEARCH_SHOW_DN_IN_STORAGE_FORMAT`. It registers `LDB_CONTROL_EXTENDED_DN_OID` with rootDSE and consumes reveal/storage-format controls. It integrates closely with linked-attribute handling, because it filters deleted/hidden link metadata and repairs one-way links for display.

## Risks and edge cases
Injection requires `objectGUID`; failure to extend the lower search attribute list causes an operations error. DN-valued attributes with invalid syntax abort the whole search with `LDB_ERR_INVALID_DN_SYNTAX`. One-way link repair may issue per-value searches across all partitions, so large result sets with many one-way links can be expensive. Filtering hidden backlinks depends on whether the caller explicitly requested the backlink attribute. Reveal controls intentionally expose otherwise hidden deleted/internal values for dbcheck-style repair paths.

## Test signals
Useful tests include searches with and without `LDB_CONTROL_EXTENDED_DN_OID`, searches requesting explicit attribute lists that omit `objectGUID`/`objectSid`, `distinguishedName` regeneration, hidden backlink filtering, deleted linked-value filtering with and without reveal controls, one-way link rename repair, invalid DN-valued attribute handling, and storage-format searches used by linked-attribute maintenance.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/extended_dn_out.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/extended_dn_store.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/extended_dn_store.c

## Purpose
`extended_dn_store.c` is the input-side extended-DN module. On add and modify operations, it finds DN-valued attributes, resolves each referenced object, and rewrites values into Samba's storage format containing GUID/SID metadata. It also implements foreign-security-principal handling for FPO-enabled attributes, allowing an input like `<SID=...>` to create or resolve a `foreignSecurityPrincipal` when policy permits.

## Important APIs, types, and functions
`struct extended_dn_context` tracks schema, module, original and rewritten requests, a linked list of pending DN replacement operations, and a cached trust routing table. Each pending replacement is `struct extended_dn_replace_list`, holding the parsed `dsdb_dn`, the value pointer to rewrite, a base search request, `fpo_enabled`, `require_object`, and `got_entry` flags.

`extended_dn_context_init()` creates request state. `extended_store_replace()` parses a DN value, decides whether the target must exist, builds a base search with `DSDB_SEARCH_SHOW_DN_IN_STORAGE_FORMAT`, and queues the operation. `extended_replace_callback()` drives the queue, rewriting values through `extended_replace_dn()` and finally issuing the rewritten add/modify request. `extended_dn_handle_fpo_attr()` implements the foreign SID path. Public module entry points are `extended_dn_add()`, `extended_dn_modify()`, and `ldb_extended_dn_store_module_init()`.

## Control flow
Adds and modifies bypass special DNs and no-schema cases. The module scans each message element; schema attributes that are not DN-valued or are `distinguishedName` are ignored. On the first relevant value, the request message is shallow-copied and a replacement add/modify request is built with `extended_final_callback()` to relay the final reply.

For each DN value, `extended_store_replace()` parses it with the attribute syntax OID. Self-references during add are skipped because the object cannot be found yet. Non-extended delete values are skipped because the delete already carries enough information. Otherwise a base search is queued to resolve the target into storage format. `extended_replace_callback()` processes each search in order. If the target is missing and required, it returns `WERR_DS_NAME_REFERENCE_INVALID`; if the target is optional, it clears the lower-layer error and proceeds. Once all values are processed, the copied request is sent down.

## State and persistence behavior
The module itself stores no durable state, but it rewrites inbound operations that will become persistent directory values. It may also persist a new `foreignSecurityPrincipal` object as system before rewriting the attribute value to the newly created DN. Its in-flight state is talloc-owned by the request.

## Dependencies and integration points
The code relies on DSDB schema metadata, `dsdb_dn_parse()`, `dsdb_dn_construct()`, `dsdb_module_search_dn()`, `dsdb_module_add()`, trust routing helpers, domain SID helpers, and controls such as `DSDB_CONTROL_DBCHECK_FIX_DUPLICATE_LINKS`, `DSDB_CONTROL_DBCHECK_FIX_LINK_DN_SID`, `LDB_CONTROL_RELAX_OID`, and `DSDB_CONTROL_DBCHECK`. FPO-enabled attributes are recognized by DRSUAPI ATTIDs for `member`, `msDS-MembersForAzRole`, `msDS-NeverRevealGroup`, and `msDS-RevealOnDemandGroup`; `msDS-NonMembers` is explicitly rejected.

## Risks and edge cases
Incorrect required-object decisions can either reject legal provisioning/dbcheck repairs or allow dangling links. FPO creation is security-sensitive: local-domain, BUILTIN, within-forest, and unsupported SID cases have distinct Windows-compatible errors. Request rewriting mutates copied values by pointer, so lifetime and talloc ownership are important. The module intentionally bypasses dbcheck duplicate-link/fix-SID controls to avoid interfering with repair operations.

## Test signals
Test normal add/modify of DN-valued attributes, deletion of DN values with and without extended components, missing targets under trusted/untrusted/relax/dbcheck contexts, self-references on add, FPO-enabled foreign SID creation, rejection of local/BUILTIN/within-forest missing SIDs, unsupported `msDS-NonMembers`, and coexistence with dbcheck link-fix controls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/extended_dn_store.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/group_audit.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/group_audit.c

## Purpose
`group_audit.c` logs changes to group membership and user primary groups. It is an LDB module named `group_audit_log` that wraps add and modify requests when logging is enabled, captures pre-operation state when needed, then emits human-readable logs, JSON audit records, and optional messaging notifications after the lower operation reports its final status.

## Important APIs, types, and functions
`struct audit_context` stores module-wide notification state: whether to send events and an `imessaging_context`. `struct audit_callback_context` stores the original request, module, pre-change member list or primary group RID, and a `log_changes` callback.

Core logging helpers include `audit_group_json()`, `audit_group_human_readable()`, `log_primary_group_change()`, `log_membership_change()`, and event-ID mappers `get_add_member_event()` / `get_remove_member_event()`. Difference calculation is handled by `get_parsed_dns()`, `dn_compare()`, and `log_membership_changes()`. Request wrappers are `set_group_membership_add_callback()`, `set_primary_group_add_callback()`, `set_group_modify_callback()`, and `set_primary_group_modify_callback()`. The common completion callback is `group_audit_callback()`.

## Control flow
`group_add()` and `group_modify()` skip replicated updates and do nothing unless human logging, JSON logging, or DSDB group-change notification is enabled. They inspect the request message for `member` or `primaryGroupID`. For membership modify, the module reads the current group with `member` and `groupType` in storage format/reveal-internals mode, stores the old member element, rebuilds the modify request with `group_audit_callback()`, and sends it down. On `LDB_REPLY_DONE`, the callback logs based on the final operation status.

Membership changes are logged by comparing sorted old and new DN arrays. Binary-equal values are ignored; GUID-equal values with changed `RMD_FLAGS` become removed or added events depending on deleted metadata; less/greater comparisons become removals/additions. Primary-group changes are logged by reading `primaryGroupID` and `objectSid`, constructing the primary group SID, resolving that group DN, and emitting a `PrimaryGroup` action. New users with a primary group also cause an added-to-group style event.

## State and persistence behavior
The module does not change directory data. Persistent side effects are audit outputs and optional messages sent with `audit_message_send()` under `DSDB_GROUP_EVENT_NAME` / `MSG_GROUP_LOG`. It uses transaction identifiers from `DSDB_CONTROL_TRANSACTION_IDENTIFIER_OID` when present, but does not manage transactions itself.

## Dependencies and integration points
It depends on Samba audit logging helpers, JSON utilities, Windows event ID constants, DSDB audit helpers for remote address/user SID/session ID/primary DN, parsed-DN utilities from linked attribute support, group type flags, and loadparm configuration `dsdb_group_change_notification`. It relies on lower modules preserving sorted storage-format member values.

## Risks and edge cases
The module deliberately avoids overhead unless logging or notifications are active. Audit quality depends on successful post-operation reads; if the final group cannot be read, it logs a generic failure instead of per-member deltas. There are likely copy/paste fragilities in request fields: some helper paths build modify/search requests using `req->op.add.message` where a modify message would normally be expected, which should be covered by tests. Parsing failures skip per-member audit to avoid breaking the directory operation after persistence.

## Test signals
Exercise add and modify membership changes for every group type to verify Windows event IDs, primary group changes on add and modify, replicated-update bypass, disabled logging bypass, JSON fields including transaction/session/remote/user SID, notification sending when configured, deleted/re-added link metadata via `RMD_FLAGS`, and failure paths when pre/post state reads fail.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/group_audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/instancetype.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/instancetype.c

## Purpose
`instancetype.c` enforces and defaults the Active Directory `instanceType` attribute. On add, it validates caller-specified values or adds `INSTANCE_TYPE_WRITE` when missing. On modify, it rejects changes to `instanceType` except when dbcheck is repairing data.

## Important APIs, types, and functions
The module has two operation handlers: `instancetype_add()` and `instancetype_mod()`. It uses `INSTANCE_TYPE_IS_NC_HEAD`, `INSTANCE_TYPE_WRITE`, and `INSTANCE_TYPE_UNINSTANT` from DS common flags, plus `DSDB_CONTROL_PARTIAL_REPLICA` and `DSDB_CONTROL_DBCHECK`. It builds rewritten add requests with `ldb_build_add_req()` and `samdb_msg_add_uint()`.

## Control flow
Special DNs bypass all logic. On add, if `instanceType` exists, the module requires exactly one value. Non-NC values may only be `0` or include `INSTANCE_TYPE_WRITE`. NC-head adds must include `WRITE`, except partial replica creation must include `UNINSTANT`. Valid supplied values pass through unchanged. If the attribute is absent, the module shallow-copies the message, adds `instanceType: INSTANCE_TYPE_WRITE`, builds a new add request, and sends it to the next module.

On modify, any `instanceType` element causes `LDB_ERR_CONSTRAINT_VIOLATION` unless `DSDB_CONTROL_DBCHECK` is present; otherwise the request passes through.

## State and persistence behavior
This module writes no private state. Its persistence impact is adding `instanceType` on new objects and preventing ordinary later changes. The added value is part of the downstream add request.

## Dependencies and integration points
It integrates with `new_partition.c` and `objectclass.c`, which also inspect `INSTANCE_TYPE_IS_NC_HEAD` for naming-context creation. Dbcheck can bypass the modify protection to repair inconsistent records.

## Risks and edge cases
The TODO notes that the default instance type is not fully calculated; it always uses `INSTANCE_TYPE_WRITE` for ordinary adds. Partial replica validation is narrow and depends on the presence of `DSDB_CONTROL_PARTIAL_REPLICA`. Misordered modules could cause `new_partition` or objectclass logic to see missing/defaulted values differently.

## Test signals
Test adds with no `instanceType`, valid and invalid non-NC values, NC-head values with and without `WRITE`, partial replica values with and without `UNINSTANT`, multi-valued `instanceType`, ordinary modify rejection, and dbcheck modify allowance.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/instancetype.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/lazy_commit.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/lazy_commit.c

## Purpose
`lazy_commit.c` advertises compatibility with the LDAP server lazy commit control by consuming it and forwarding an otherwise equivalent request. It does not implement deferred or relaxed durability; it simply marks `LDB_CONTROL_SERVER_LAZY_COMMIT` non-critical before passing the operation down.

## Important APIs, types, and functions
The single handler is `unlazy_op()`, wired into search, add, modify, delete, rename, generic request, and extended operation slots. It uses the appropriate `ldb_build_*_req()` helper for each operation and `dsdb_next_callback` for reply forwarding.

## Control flow
If the request lacks `LDB_CONTROL_SERVER_LAZY_COMMIT`, `unlazy_op()` returns `ldb_next_request(module, req)`. If present, it switches on `req->operation`, rebuilds a semantically equivalent child request with the same controls and payload, clears `control->critical`, and forwards the new request. Unsupported request types return `LDB_ERR_UNWILLING_TO_PERFORM`.

## State and persistence behavior
The module has no state and no direct persistence semantics beyond leaving the actual operation to lower modules. Its key behavior is to prevent a critical lazy-commit control from failing against backends that do not implement it.

## Dependencies and integration points
It depends only on LDB request builders and Samba's `dsdb_next_callback`. It should sit where controls can be consumed before a lower module rejects an unsupported critical control.

## Risks and edge cases
The name and control behavior can be misleading: callers may assume lazy commit semantics, but Samba performs normal commit behavior. Rebuilding every operation type must preserve controls, request ownership, and callback behavior; missing operation variants would cause compatibility failures.

## Test signals
Run each LDB operation type with and without `LDB_CONTROL_SERVER_LAZY_COMMIT`, including critical controls, and verify the lower operation succeeds normally, the control is marked non-critical, replies are propagated, and unsupported operations produce `LDB_ERR_UNWILLING_TO_PERFORM`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/lazy_commit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/linked_attributes.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/linked_attributes.c

## Purpose
`linked_attributes.c` maintains consistency between forward links and backlinks in Samba's AD database. It processes add/modify operations carrying `DSDB_CONTROL_APPLY_LINKS`, updates corresponding backlink attributes after the originating operation, repairs linked DN components during rename, and defers backlink modifications until transaction prepare-commit so targets created later in the same transaction can be resolved.

## Important APIs, types, and functions
Module private state is `struct la_private`, with per-transaction `struct la_private_transaction` and a `sorted_links` feature flag. A request uses `struct la_context`, which stores schema, original request, the source object DN, pending `struct la_op_store` add/delete operations, optional replace-context state, and saved lower-operation response controls. `la_store_op()` parses link values and records target GUID plus backlink name. `la_down_req()`, `la_add_callback()`, and `la_mod_del_callback()` wrap original operations. `la_queue_mod_request()`, `la_do_mod_request()`, and `la_do_op_request()` apply deferred backlink modifications. Rename repair is handled by `linked_attributes_fix_links()`, with slow and sorted-forward-link paths.

## Control flow
Adds and modifies skip special DNs, handle `LDB_CONTROL_VERIFY_NAME_OID`, and require `DSDB_CONTROL_APPLY_LINKS`; without it, replication metadata is assumed to have handled link maintenance. The module only processes even `linkID` forward links and maps them to odd backlink attributes with `dsdb_attribute_by_linkID(linkID ^ 1)`. Adds queue backlink adds. Modifies queue backlink adds/deletes; replace and delete-without-values trigger a base search to discover old values and queue deletions before the original modify.

The original operation is sent down first. On success, pending link work is queued into transaction-private state and the original reply is completed. During `prepare_commit`, the module walks queued contexts in original order, resolves target DNs by GUID, and performs backlink add/delete modifies as system-next-module operations. Renames search the object, inspect all linked attributes, find partner objects by GUID, update old DN components to the new DN, and write modified partner link values.

## State and persistence behavior
Backlink updates are persistent DSDB modifies, but they are deferred until transaction prepare-commit. `start_transaction` allocates the per-transaction list, `prepare_commit` applies queued link operations and frees it, and `del_transaction` discards it. This design lets forward links target objects created later in the same transaction while keeping original operation replies separate from deferred maintenance failures.

## Dependencies and integration points
The module depends heavily on schema link metadata, DSDB DN parsing, GUID lookup by DN, DN lookup by GUID, sorted-link parsing helpers, `DSDB_CONTROL_APPLY_LINKS`, verify-name controls, `SAMBA_SORTED_LINKS_FEATURE`, and transaction hooks. It coordinates with `repl_meta_data.c` for replicated link changes and with `extended_dn_out.c` for runtime filtering/repair of cases backlinks cannot cover.

## Risks and edge cases
Backlink operations can fail at prepare-commit after the visible operation appeared successful, so transaction error propagation is critical. Old unsorted databases use linear scans; sorted forward links use binary-search helpers but DN+Binary values require updating all equal-GUID neighbors. Missing backlink schema definitions are tolerated for Windows 2003 compatibility. Verify-name control handling can intentionally leave critical controls to force failure when a requested GC cannot be honored. Dangling forward links on delete are tolerated in specific cases.

## Test signals
Test add/modify/replace/delete of forward links, delete-without-values, transaction ordering where target is created later, rollback/discard behavior, rename repairs for backlinks and forward links, DN+Binary duplicate-GUID cases, sorted versus unsorted feature modes, missing partner schema, verify-name behavior on GC and non-GC servers, replicated-update paths without `DSDB_CONTROL_APPLY_LINKS`, and prepare-commit failure propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/linked_attributes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/managed_pwd.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/managed_pwd.c

## Purpose
`managed_pwd.c` constructs the confidential `msDS-ManagedPassword` attribute for Group Managed Service Accounts. It is not a normal LDB module ops table; it exports `constructed_msds_managed_password()` for the constructed-attribute framework, which adds the packed managed-password blob to a search result when policy permits.

## Important APIs, types, and functions
The core helper is `gmsa_managed_password()`. It consumes an `ldb_context`, result message, parent request, and reply object. It uses GMSA helpers such as `dsdb_account_is_gmsa()`, `gmsa_allowed_to_view_managed_password()`, `dsdb_gmsa_current_time()`, `gmsa_recalculate_managed_pwd()`, and `gmsa_pack_managed_pwd()`. It may attach a `DSDB_CONTROL_GMSA_UPDATE_OID` reply control containing `struct gmsa_update`.

## Control flow
The function first checks `DSDB_OPAQUE_ENCRYPTED_CONNECTION_STATE_NAME`; if the connection is known to be unencrypted, it returns an operations error mapped to `WERR_DS_CONFIDENTIALITY_REQUIRED`. Non-GMSA accounts return success without adding the attribute. RODC operation is rejected because password construction must occur on a writable DC. For GMSA objects, the account SID is read, access is checked, and unauthorized callers receive success with no constructed value.

If allowed, the function obtains current DSDB GMSA time, recalculates the managed password, and asserts a new password is available. When recalculation says physical database keys/IDs should be refreshed, it adds a non-critical `DSDB_CONTROL_GMSA_UPDATE_OID` control to the reply and steals the update object into reply lifetime. Finally it packs new and optional previous password buffers plus query/unchanged intervals and adds `msDS-ManagedPassword` to the result message.

## State and persistence behavior
The constructed attribute is transient search-result state. Actual database refresh is signaled through the reply control rather than performed here. This keeps attribute construction side-effect-light while letting the LDAP server or surrounding framework persist GMSA password updates.

## Dependencies and integration points
This code integrates with DSDB GMSA utilities, LDAP encrypted-connection state, RODC detection, access-control checks for managed password viewing, NDR-generated GMSA structures, and constructed-attribute dispatch declared in `managed_pwd.h`.

## Risks and edge cases
Confidentiality and authorization failures must avoid leaking timing or partial password data. Unauthorized non-errors are intentional: the attribute is simply absent. RODC behavior is currently a hard failure with a TODO to forward to a writable DC. Errors while adding the update control are ignored, which preserves read behavior but may skip refresh signaling.

## Test signals
Test encrypted versus unencrypted LDAP, non-GMSA objects, writable DC versus RODC, allowed and denied readers, password packing with and without previous password, update-control attachment and ownership, and failure paths from SID extraction, time lookup, recalculation, and packing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/managed_pwd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/managed_pwd.h -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/managed_pwd.h

## Purpose
`managed_pwd.h` declares the constructed-attribute hook for `msDS-ManagedPassword`. It provides the include guard and forward declaration needed by other DSDB LDB module code to call into `managed_pwd.c` without exposing GMSA implementation details.

## Important APIs, types, and functions
The header includes `<ldb.h>`, forward-declares `struct ldb_module`, and declares:

`int constructed_msds_managed_password(struct ldb_module *module, struct ldb_message *msg, enum ldb_scope scope, struct ldb_request *parent, struct ldb_reply *ares);`

The signature matches Samba's constructed-attribute callback shape: module context, result message to augment, search scope, parent request for controls/security context, and reply object for reply controls.

## Control flow
There is no executable control flow in the header. It establishes the ABI contract used by the constructed-attribute registration site and implemented in `managed_pwd.c`.

## State and persistence behavior
The header defines no state. Its declared function constructs transient result data and may signal later GMSA persistence through reply controls, as described in the C implementation.

## Dependencies and integration points
The header is intentionally minimal: it depends only on LDB types and is consumed by DSDB module code that wires constructed attributes. Keeping GMSA internals out of the header limits rebuild coupling and keeps policy in `managed_pwd.c`.

## Risks and edge cases
Any signature drift between the constructed-attribute dispatcher and this declaration would be a compile-time or runtime integration break. Because `enum ldb_scope` is accepted but not used in the implementation, future callers should not assume scope-specific behavior without changing both files.

## Test signals
Compile coverage is the primary signal. Functional tests should request `msDS-ManagedPassword` through the constructed-attribute path rather than calling the implementation helper directly, proving the declared ABI is correctly wired.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/managed_pwd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/netlogon.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/netlogon.c

## Purpose
`netlogon.c` implements CLDAP/netlogon request parsing and response construction against the Samba SAM database. It turns LDAP filter fields into domain/user lookup inputs and fills `struct netlogon_samlogon_response` variants for NT4, NT5, and NT5EX clients, including DC capability flags, site names, domain GUID, DNS names, and optional IPv4 address.

## Important APIs, types, and functions
`fill_netlogon_samlogon_response()` is the main response builder. It accepts SAM LDB context, domain identifiers, user/account-control hints, source address, requested netlogon version bits, loadparm context, output union, and a `fill_on_blank_request` compatibility flag. `parse_netlogon_request()` parses an `LDB_OP_AND` filter into `DnsDomain`, `Host`, `DomainGuid`, `DomainSid`, `User`, `NtVer`, and `AAC` fields.

The code uses DSDB domain/user/trust lookup helpers, loadparm configuration, interface selection helpers, site-name functions, domain functional level checks, and flag mapping from account-control bits to `userAccountControl`.

## Control flow
Response filling first normalizes a trailing dot in the DNS domain. It resolves the target domain by DNS name, NetBIOS name, domain GUID, domain SID, or blank request fallback. GUID input is parsed and encoded into binary filter form; SID input is string-filtered. Any resolved domain must match the local default base DN.

User handling then determines `user_known`. Account-control input is masked to allowed bits, except the `ACB_AUTOLOCK`/`UF_LOCKOUT` path is treated as a DNS trust-domain lookup. Ordinary users are searched under the domain, excluding disabled accounts and matching requested UAC bits. Blank user means known.

The function computes `server_type` flags from local roles and services: DS, PDC, GC, LDAP, KDC, time service, writable/RODC, DC functional level secret-domain flags, and DS version flags through 2016. It determines PDC names, DNS/forest names, server/client sites, closest-site flag, and a best IPv4 address for the source. Finally it zeroes the output union and fills the requested NT5EX-with-IP, NT5EX, NT5, or NT4 response.

`parse_netlogon_request()` requires an AND of equality terms, decodes GUID/SID NDR forms, defaults the domain to local DNS domain if no domain identifier is supplied, and defaults version to `NETLOGON_NT_VERSION_5`.

## State and persistence behavior
This file is read-only with respect to SAM database state. It performs searches and fills caller-owned response structures. It derives network/interface and loadparm state at request time.

## Dependencies and integration points
It integrates CLDAP server handling with SAM LDB, DSDB trust search, site topology, loadparm services, network interface selection, NDR GUID/SID decoding, and netlogon response structures generated from RPC IDL. User-known behavior is intentionally conservative because CLDAP user enumeration has security implications.

## Risks and edge cases
Domain resolution must not answer for non-local domains even if GUID/SID searches find something. Account-control masking is security-sensitive; overly broad filters could leak disabled or wrong-class account existence. IP selection is IPv4-only and falls back to `127.0.0.1` to match Windows behavior. Parser strictness means unexpected filter shapes return `NT_STATUS_UNSUCCESSFUL`.

## Test signals
Test domain lookup by DNS, NetBIOS, GUID, SID, trailing-dot DNS, blank request fallback, and mismatched domain rejection. Verify user-known behavior for disabled users, trust-domain `UF_LOCKOUT` queries, unknown users, and blank users. Check NT4/NT5/NT5EX/NT5EX-with-IP response layouts, server flags for PDC/GC/RODC/services/function levels, site closest flag, IPv4 fallback, and parser failures for non-AND or non-equality filters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/netlogon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/new_partition.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/new_partition.c

## Purpose
`new_partition.c` intercepts adds of naming-context heads and asks the partitions module to create the corresponding `@PARTITIONS` metadata before allowing the original add. It prevents duplicate partition entries by checking whether the target DN already exists.

## Important APIs, types, and functions
`struct np_context` tracks the module, original add request, existence-check search request, and extended partition-add request. `new_partition_add()` is the operation handler. `np_part_search_callback()` handles the nonexistence check and builds `DSDB_EXTENDED_CREATE_PARTITION_OID`. `np_part_mod_callback()` treats successful partition metadata update, or attribute/value-exists during metadata update, as permission to continue with the original add.

## Control flow
Special DNs bypass the module. For ordinary adds, the module only acts when `instanceType` exists and includes `INSTANCE_TYPE_IS_NC_HEAD`; non-NC adds pass through. Deleted partition objects are skipped. For NC-head adds, it builds a base search for the new DN with no attributes. If the search succeeds, the object already exists and the module returns `LDB_ERR_ENTRY_ALREADY_EXISTS`. If the search returns `LDB_ERR_NO_SUCH_OBJECT` and the final reply is done, it builds an extended operation containing `struct dsdb_create_partition_exop` with `new_dn`.

If the original add had `DSDB_CONTROL_PARTIAL_REPLICA`, the extended operation gets `DSDB_MODIFY_PARTIAL_REPLICA`. After the extended op completes, `np_part_mod_callback()` runs the original add.

## State and persistence behavior
The module itself has no durable private state. Its side effect is triggering partition metadata creation through the partitions module before the actual NC-head object is added. The original add persists only after metadata handling succeeds or reports an already-existing metadata value.

## Dependencies and integration points
It depends on `instanceType` semantics, DSDB extended operation `DSDB_EXTENDED_CREATE_PARTITION_OID`, `DSDB_CONTROL_PARTIAL_REPLICA`, and downstream partition module behavior. It coordinates with `instancetype.c` and `objectclass.c`, which also validate NC-head additions.

## Risks and edge cases
If module ordering means `instanceType` has not been added yet, this module will not detect a partition add. The existence search treats any success as duplicate object, which is intentional but makes exact lower-layer error mapping important. Deleted NC-head objects are skipped to avoid recreating deleted partition metadata during replication or repair.

## Test signals
Test ordinary adds, NC-head adds, duplicate target DN, deleted NC-head skip, partial replica control propagation, extended operation failure propagation, `LDB_ERR_ATTRIBUTE_OR_VALUE_EXISTS` tolerance in metadata update, and ordering with `instancetype`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/new_partition.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/objectclass.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/objectclass.c

## Purpose
`objectclass.c` enforces objectClass hierarchy, naming, parent-child constraints, DN normalization, objectCategory defaults, selected systemFlags rules, structural-class immutability, rename constraints, and delete protections. It is one of the central AD semantics modules for add, modify, rename, and delete operations.

## Important APIs, types, and functions
`struct oc_context` carries module/request/schema state, one or two search replies, and a continuation `step_fn`. `oc_init_context()` initializes it. `check_unrelated_objectclasses()` rejects unsatisfied abstract classes or disjoint structural class combinations. `get_search_callback()` is the common async search continuation. `fix_dn()` normalizes child DN components against the parent DN.

Operation paths are `objectclass_add()` / `objectclass_do_add()`, `objectclass_modify()` / `oc_modify_callback()` / `objectclass_do_mod()`, `objectclass_rename()` / `objectclass_do_rename()` / `objectclass_do_rename2()`, and `objectclass_delete()` / `objectclass_do_delete()`. Init registers `LDB_CONTROL_RODC_DCPROMO_OID` and stores the extended-DN store-format opaque.

## Control flow
Adds bypass special DNs and reject base-DN re-adds without NC-head `instanceType` by returning an LDAP referral. For normal children, the module searches the parent with show-recycled/system controls, normalizes the new DN, requires objectClass, sorts the class list, finds the structural class, validates RDN attribute compatibility, rejects system-only classes unless relax or special RODC DCPROMO applies, checks parent `systemPossibleInferiors`, validates or defaults `objectCategory`, applies default hiding and systemFlags rules, rejects direct `isCriticalSystemObject`, and forwards a rewritten add.

Modify first strips non-objectClass changes into a lower modify. If objectClass changes are present, older forest functional levels reject changes under standard NCs. After non-class changes succeed, it searches the stored objectClass, applies requested objectClass add/replace/delete semantics, resorts the list, ensures the structural class is unchanged, checks unrelated classes, and sends a final replace of objectClass.

Rename searches the new parent and old object, bypassing dbcheck. It validates RDN compatibility, allowed parent class, and prevents moving an object below itself. It then normalizes the new DN and forwards a rewritten rename. Delete searches the object unless relax is present and blocks deletion of this DC's nTDSDSA, this DC's RID Set, deleted objects by untrusted/non-system callers, protected crossRefs, objects with `SYSTEM_FLAG_DISALLOW_DELETE`, and critical system objects during tree-delete except selected SAM classes.

## State and persistence behavior
The module rewrites requests but stores no module-private durable data. Its persistent effects are normalized DNs, defaulted `objectCategory`, `showInAdvancedViewOnly`, and `systemFlags` on adds, and validated objectClass replacements on modifies.

## Dependencies and integration points
It depends on DSDB schema class metadata, possible inferior lists, objectCategory defaults, functional-level helpers, default/config/schema base DNs, system access controls, RODC DCPROMO control registration, and extended-DN storage format choices. It runs in concert with `objectclass_attrs.c`, which validates attribute allow/must lists after the operation.

## Risks and edge cases
AD compatibility rules are dense and order-sensitive. Parent searches include recycled objects to support DRS delete flows. The structural class pointer comparison assumes classes come from the same schema instance. SystemFlags behavior is intentionally class-specific and may miss obscure Windows rules. Rename/delete protection bypasses for dbcheck/relax are necessary but security-sensitive.

## Test signals
Test add with missing objectClass, invalid RDN, invalid parent class, system-only class with and without relax/RODC control, objectCategory default/validation under both extended-DN storage modes, systemFlags masks for schema/site/server/linkID cases, objectClass modify add/delete/replace with structural-class immutability, forest-level restrictions, rename parent/RDN/self-child checks, and delete protections for nTDSDSA, RID Set, crossRef, deleted objects, disallow-delete, and critical tree-delete.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/objectclass.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/objectclass_attrs.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/objectclass_attrs.c

## Purpose
`objectclass_attrs.c` validates entry attributes against schema and objectClass constraints. It checks that attributes exist, values match syntax, constructed/backlink/system-only attributes are not illegally written, names and values are normalized, delete-protected attributes remain present, required attributes exist, and schema attribute definitions are loadable before persistence is accepted.

## Important APIs, types, and functions
`struct oc_context` carries module/request/schema, a copied request message, the post-operation search result, and saved lower reply. `oc_validate_dsheuristics()` implements special string-position constraints. `oc_auto_normalise()` canonicalizes values using the syntax handler. `attr_handler()` performs pre-operation attribute validation and sends a copied add/modify. `oc_op_callback()` runs after the lower operation, searches the stored entry, and calls `attr_handler2()` for full objectClass allow/must validation. Module handlers are `objectclass_attrs_add()` and `objectclass_attrs_modify()`.

## Control flow
Adds and modifies bypass special DNs and no-schema cases. Modify with `DSDB_CONTROL_SEC_DESC_PROPAGATION_OID` is allowed only for a single `nTSecurityDescriptor` change and then bypasses the rest. Otherwise `attr_handler()` copies the request message, checks each element against schema, allows dbcheck to remove unknown attributes on modify, rejects direct backlink modification without relax/dbcheck, enforces systemOnly constraints with documented exceptions, validates syntax unless internal disable-validation is set or dbcheck is present, rejects constructed attributes, validates `dSHeuristics`, auto-normalizes values, and fixes attribute-name case.

After the lower add/modify returns done, `oc_op_callback()` searches the actual object with `nTSecurityDescriptor` and `*`, including show-recycled and reveal-internals controls. `attr_handler2()` reads final objectClass, blocks untrusted LDAP creation/change of `secret` and `trustedDomain`, builds full MUST/MAY attribute lists, enforces a hardcoded delete-protected attribute list when those attributes were part of the request, rejects attributes not allowed by the object's classes except harmless `parentGUID` and dbcheck repair cases, verifies replicated mandatory attributes are present unless the object is deleted, and validates new `attributeSchema` objects can be translated to `struct dsdb_attribute` with a known syntax.

## State and persistence behavior
The module has no durable private state. It validates by first letting the lower operation occur, then reading the resulting object and only completing the original request if final constraints pass. In a transactional LDB stack, a failure after lower modify should abort the operation.

## Dependencies and integration points
It depends on schema attributes and syntax handlers, DSDB full attribute list helpers, dbcheck/relax/restore tombstone/security descriptor propagation controls, system access checks, and objectClass sorting/defaulting performed by `objectclass.c` earlier in the stack.

## Risks and edge cases
Because full validation happens after lower persistence, correct transaction rollback is essential. SystemOnly rules have many exceptions and use schema-base comparison plus system access as a proxy for some AD upgrade states. Dbcheck bypasses are intentionally broad enough to repair broken entries but must not leak into normal LDAP writes. Constructed attributes return different LDAP errors on add versus modify.

## Test signals
Test unknown attributes, invalid syntax, auto-normalization, direct backlink modification, systemOnly writes with relax/dbcheck/restore/system access, constructed attributes on add/modify, `dSHeuristics` positional constraints, security descriptor propagation bypass, delete-protected attributes, missing mandatory attributes on live versus deleted objects, untrusted LSA objectclass rejection, schema attribute translation failures, and dbcheck repair allowances.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/objectclass_attrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/objectguid.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/objectguid.c

## Purpose
`objectguid.c` adds immutable identity and update metadata to directory objects. On add it generates `objectGUID`, `whenCreated`, `whenChanged`, `uSNCreated`, and `uSNChanged` when needed. On modify it updates `whenChanged` and `uSNChanged` while rejecting attempts to alter `objectGUID`.

## Important APIs, types, and functions
Helpers `add_time_element()` and `add_uint64_element()` append timestamp and uint64 attributes only when absent, using replace flags that are ignored for adds. `objectguid_add()` and `objectguid_modify()` are the operation handlers. `struct og_context` stores module/request pointers for child request ownership. Registration is through `ldb_objectguid_module_init()`.

## Control flow
Special DNs bypass the module. Add rejects any caller-specified `objectGUID` with `LDB_ERR_UNWILLING_TO_PERFORM`, shallow-copies the message, generates `GUID_random()`, adds it with `dsdb_msg_add_guid()`, fills created/changed timestamps from `time(NULL)`, asks the backend for `LDB_SEQ_NEXT`, and fills USN attributes if the sequence call succeeds. It then builds and sends a child add request.

Modify rejects `objectGUID` changes with `LDB_ERR_CONSTRAINT_VIOLATION`, copies the modify message, appends `whenChanged`, obtains the next sequence number when available, appends `uSNChanged`, and sends a child modify request.

## State and persistence behavior
The module has no private durable state but writes durable metadata attributes into add/modify requests. It depends on the backend sequence counter for USNs; if sequence retrieval fails, the operation still proceeds without adding USN fields.

## Dependencies and integration points
It integrates with DSDB message helpers, LDB sequence numbers, time formatting, and downstream replication metadata expectations. Other modules rely on `objectGUID` existing, especially extended-DN output/store and linked-attribute GUID resolution.

## Risks and edge cases
Proceeding when `ldb_sequence_number()` fails may create objects or modifications lacking USN metadata in backends that do not support sequences. The module only rejects explicit `objectGUID`; caller-supplied timestamp/USN values are preserved because helpers skip existing attributes. That may be intentional for provisioning/replication but is worth testing in untrusted paths.

## Test signals
Test add generation, add rejection with explicit `objectGUID`, modify rejection with explicit `objectGUID`, timestamp/USN defaulting, preservation of caller-supplied timestamp/USN fields, behavior when sequence numbers are unsupported, and downstream modules resolving newly generated GUIDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/objectguid.c -->
