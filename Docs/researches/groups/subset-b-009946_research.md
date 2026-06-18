# Research Group subset-b-009946

Grouped research for Samba LSA RPC server sources. Each source section is delimited for reconciliation into the corresponding source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/lsa/dcesrv_lsa.c -->
# sources/user-network-fs/samba/source4/rpc_server/lsa/dcesrv_lsa.c

## Purpose

`dcesrv_lsa.c` is the main Samba4 LSARPC endpoint implementation. It supplies most generated NDR server handlers for `lsarpc`, plus the remaining `dssetup` role query endpoint that depends on LSA policy state. The file handles LSA policy information queries, privilege and account-right enumeration/mutation, trusted-domain object lifecycle, secret storage, forest trust information, and server registration for LSARPC and DSSETUP.

The file relies on `lsa_init.c` for policy handle construction and on `lsa_lookup.c` for name/SID lookup calls. It includes `ndr_lsa_s.c` and `ndr_dssetup_s.c` to bind the static handler names into the generated RPC dispatch tables, then exports `dcerpc_server_lsa_init()` to register both endpoint servers.

## Important APIs, Types, and Functions

- `struct lsa_account_state`, `struct lsa_secret_state`, and `struct lsa_trusted_domain_state` are per-handle private state objects stored in `struct dcesrv_handle`.
- `dcesrv_interface_lsarpc_init_server()` optionally registers LSARPC on the Netlogon pipe when `lsa over netlogon` is enabled, then delegates to generated server init.
- `dcesrv_lsa_Close()`, `dcesrv_lsa_DeleteObject()`, and many handler stubs implement common handle and unsupported-op behavior.
- `dcesrv_lsa_QueryInfoPolicy2()` and wrapper `dcesrv_lsa_QueryInfoPolicy()` return domain, DNS, audit, quota, and role policy info from `lsa_policy_state`.
- `dcesrv_dssetup_DsRoleGetPrimaryDomainInformation()` maps Samba server role and domain state into DSSETUP role responses.
- Account and privilege handlers include `dcesrv_lsa_CreateAccount()`, `OpenAccount()`, `EnumAccounts()`, `EnumPrivs()`, `EnumPrivsAccount()`, `EnumAccountRights()`, `AddRemoveAccountRights()`, `AddPrivilegesToAccount()`, `RemovePrivilegesFromAccount()`, `GetSystemAccessAccount()`, and privilege name/value/display lookup helpers.
- Trusted-domain handlers include `CreateTrustedDomain*()`, `OpenTrustedDomain*()`, `SetInformationTrustedDomain()`, `SetTrustedDomainInfoByName()`, `QueryTrustedDomainInfo*()`, `EnumTrustDom()`, `EnumTrustedDomainsEx()`, and `DeleteTrustedDomain()`.
- Secret handlers include `CreateSecret()`, `OpenSecret()`, `SetSecret()`, and `QuerySecret()`.
- Forest trust handlers include `dcesrv_lsa_QueryFTI()`, `dcesrv_lsa_SetFTI()`, `lsaRQueryForestTrustInformation*()`, and `lsaRSetForestTrustInformation*()`.
- Trust authentication helpers include `get_trustdom_auth_blob()` for RC4/session-key protected blobs, `get_trustdom_auth_blob_aes()` for AES/HMAC protected Ex3 blobs, and `get_trustauth_inout_blob()` for NDR packing `trustAuthInOutBlob`.

## Control Flow

RPC entry points generally start by validating transport or pulling a typed handle via `DCESRV_PULL_HANDLE()`. Policy-oriented calls unwrap `LSA_HANDLE_POLICY`; account, secret, and trusted-domain calls unwrap their matching handle type. Output pointers are usually initialized to null or zero before validation so error paths do not leak stale values.

Trusted-domain creation flows through `dcesrv_lsa_CreateTrustedDomain_precheck()` and `dcesrv_lsa_CreateTrustedDomain_common()`. The precheck rejects missing names/SIDs, invalid trust attribute combinations, current-domain and BUILTIN collisions, unsupported within-forest/PIM trust creation, invalid account-domain SIDs, and NetBIOS names longer than 15 characters. The common function decodes auth blobs, checks for existing trustedDomain objects by DNS, flat name, and SID, creates the TDO under the System container, optionally writes forest trust info, optionally creates an inbound interdomain trust user, commits an LDB transaction, and returns an `LSA_HANDLE_TRUSTED_DOMAIN`.

Trusted-domain mutation flows through `setInfoTrustedDomain_base()`. It decodes the requested info level into a small set of updatable fields, verifies that the requested DNS/NetBIOS/SID tuple still names the target TDO, blocks trust type changes, permits only limited trust attribute changes, toggles `trustAuthIncoming`/`trustAuthOutgoing`, updates the interdomain trust user when inbound direction changes, and commits all DB changes in one transaction.

Secret operations bifurcate on names prefixed with `G$`. Global secrets are stored as `secret` objects in the AD System container and accessed with a system SAMDB connection; local secrets are stored in `secrets.ldb` under `cn=LSA Secrets`. `SetSecret()` decrypts incoming current/prior values using the RPC transport session key, rotates the previous value/time when an old value is omitted, and uses `dsdb_replace()`. `QuerySecret()` reads selected current/prior values/times and encrypts returned secret blobs with the same session key.

Forest trust set/query requires the current domain to be the forest root. Set additionally requires the server to be PDC, normalizes supplied forest trust records, verifies collisions against local xref data and other TDOs, supports check-only mode, and writes normalized `msDS-TrustForestTrustInfo` only when not in check-only mode.

## State and Persistence Behavior

Handles are transient server-side objects. Persistent state is held in:

- `sam.ldb`: domain object metadata, trustedDomain objects, global secrets, interdomain trust users, and forest trust blobs.
- privilege DB from `privilege_connect()`: LSA account rights and privileges keyed by `objectSid`.
- `secrets.ldb`: non-global LSA secrets.

Trusted-domain create, delete, and update paths use explicit LDB transactions when multiple records may change together. Secret update uses DSDB replace semantics. Account objects are mostly handle-only; account rights are the persistent portion.

Trust password handling stores current/previous incoming and outgoing auth arrays as NDR blobs in trustedDomain attributes. `get_trustauth_inout_blob()` pads previous auth arrays to match current count, preserving Windows-style current/previous shape.

## Dependencies and Integration Points

This file integrates with Samba's DCERPC server (`dcesrv_handle_create`, generated NDR server includes), SAMDB/DSDB utilities, privilege DB helpers, security descriptors and access checks, Kerberos/KDC policy helpers, GnuTLS crypto, trust routing and forest trust utilities, and loadparm server-role configuration. It depends on `lsa_policy_state` and `LSA_HANDLE_*` definitions from `lsa.h`.

Integration with Windows protocol behavior is visible in special status choices, resume-handle handling, unsupported opnum faulting, DSSETUP compatibility, trust record normalization, and support for Ex3 AES trusted-domain creation.

## Risks and Edge Cases

- Several access checks are incomplete or coarse. `OpenTrustedDomain_common()` has a TODO for access checks, and account handle creation grants requested access before later LDB operations fail or succeed.
- Cryptographic compatibility is sensitive. RC4 trust auth blob decryption is blocked when weak crypto is disallowed and the transport is not encrypted, while Ex3 uses AES/HMAC. Regression tests need both policy settings and transport protection variants.
- Secret APIs depend on correct session-key encryption/decryption and strict administrator/system authorization. Mistakes expose credential material.
- Trusted-domain updates intentionally reject many attribute changes. Future feature work must account for these explicit `INVALID_PARAMETER` paths and transaction rollback.
- Forest trust set is collision-sensitive and PDC-only. Bugs can corrupt cross-forest routing data or fail to report collisions in check-only mode.
- Numerous RPC operations deliberately fault with `DCERPC_FAULT_OP_RNG_ERROR`; generated IDL changes can accidentally expose an unsupported handler if names/signatures drift.
- Several paths depend on exact LDAP attribute names, including case variants such as `msDs-supportedEncryptionTypes` versus `msDS-SupportedEncryptionTypes`; schema behavior should be verified before editing.

## Test Signals

Strong signals include Samba RPC torture coverage for LSARPC policy query/open/close, account rights and privilege enumeration, secret create/open/set/query/delete with admin and non-admin callers, trusted-domain create/open/query/set/delete including inbound user creation, forest trust query/set collision cases, and endpoint registration with and without `lsa over netlogon`. Useful negative tests cover invalid handles, unsupported transports, invalid trust attributes, duplicate TDOs, weak-crypto-disabled unencrypted trust auth, and expected opnum faults.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/lsa/dcesrv_lsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/lsa/lsa.h -->
# sources/user-network-fs/samba/source4/rpc_server/lsa/lsa.h

## Purpose

`lsa.h` is the shared private header for the Samba4 LSA RPC endpoint implementation. It centralizes includes needed by the LSA server files, defines the policy-handle state structure, defines the internal handle type enum, and includes generated local prototypes.

## Important APIs, Types, and Functions

- `struct lsa_policy_state` is the central per-policy-handle state used across `lsa_init.c`, `dcesrv_lsa.c`, and `lsa_lookup.c`.
- `enum lsa_handle` assigns the private handle type tags `LSA_HANDLE_POLICY`, `LSA_HANDLE_ACCOUNT`, `LSA_HANDLE_SECRET`, and `LSA_HANDLE_TRUSTED_DOMAIN`.
- `#include "rpc_server/lsa/proto.h"` exposes generated prototypes for the LSA server implementation files.

`lsa_policy_state` contains:

- DCERPC handle pointer: `handle`.
- Database connections: `sam_ldb` and `pdb`.
- Frequently used DNs: domain, forest root, builtin, and system container.
- Domain naming and identity: NetBIOS domain name, DNS domain, forest DNS, domain SID, domain GUID, builtin SID, NT authority SID, creator-owner domain SID, and world domain SID.
- Domain mode and authorization state: `mixed_domain`, decoded policy security descriptor, and granted `access_mask`.

## Control Flow

This header does not implement control flow. Its structure layout drives how policy-open code initializes state, how main LSARPC handlers find databases and domain identity from a handle, and how lookup code determines local authority scopes.

## State and Persistence Behavior

The header defines in-memory state only. `lsa_policy_state` references persistent stores through `sam_ldb` and `pdb`, but it does not own persistence logic. The state is allocated by `dcesrv_lsa_get_policy_state()` and then either stored under a policy handle or cached on a schannel connection by handle-less lookup calls.

## Dependencies and Integration Points

The include list brings in DCERPC server types, common RPC helpers, auth/session types, SAMDB, LDAP NDR helpers, LDB error constants, security descriptor/SID helpers, auth crypto helpers, secrets DB access, LDB utility helpers, DSSETUP NDR definitions, and loadparm context. This makes the header intentionally broad: implementation files can include one private LSA header rather than repeating Samba subsystem includes.

## Risks and Edge Cases

- Because `lsa_policy_state` is shared across multiple files, field lifetime matters. Many fields are talloc children of the state, while handle and connection cache users hold references across RPC calls.
- Adding fields here increases coupling across the LSA implementation. New fields should be initialized in `dcesrv_lsa_get_policy_state()` or documented as lazily initialized.
- The private `enum lsa_handle` values must remain consistent with `dcesrv_handle_create()` and `DCESRV_PULL_HANDLE()` usage across files.

## Test Signals

Build coverage is the primary signal for this header because generated prototypes and broad includes will fail quickly on type drift. Runtime signals come indirectly from OpenPolicy, LookupNames/Sids, account, secret, and trusted-domain tests that exercise every `lsa_policy_state` field.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/lsa/lsa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/lsa/lsa_init.c -->
# sources/user-network-fs/samba/source4/rpc_server/lsa/lsa_init.c

## Purpose

`lsa_init.c` builds and opens LSA policy handles. It is responsible for connecting to SAMDB and the privilege DB, collecting stable domain metadata into `lsa_policy_state`, constructing the policy security descriptor, performing policy access checks, and implementing `OpenPolicy`, `OpenPolicy2`, and `OpenPolicy3`.

## Important APIs, Types, and Functions

- `DCESRV_LSA_POLICY_SD_SDDL` defines the Windows-compatible policy object security descriptor used for access checks.
- `dcesrv_lsa_policy_mapping` maps generic access bits to LSA policy-specific rights.
- `dcesrv_lsa_get_policy_state()` is the main initializer for `struct lsa_policy_state`.
- `dcesrv_lsa_OpenPolicy3()` supports revision negotiation and advertises `LSA_FEATURE_TDO_AUTH_INFO_AES_CIPHER`.
- `dcesrv_lsa_OpenPolicy2()` is the standard policy-open implementation.
- `dcesrv_lsa_OpenPolicy()` wraps `OpenPolicy2` for the older call shape.

## Control Flow

`dcesrv_lsa_get_policy_state()` allocates a zeroed state, connects to SAMDB as the caller, connects to the privilege DB, gets default and forest base DNs, queries the domain object for SID, GUID, mixed-domain flag, and FSMO owner, derives DNS names from canonical DNs, locates builtin and system containers, parses common authority SIDs, decodes the policy SDDL against the domain SID, maps generic access rights, and performs access checking. System-level callers bypass the descriptor to support local root/system use; other callers use `se_access_check()` and store the granted mask.

`OpenPolicy2()` and `OpenPolicy()` are restricted to `NCACN_NP` and `NCALRPC`. They reject non-null `attr->root_dir`, initialize the output handle to zero, call `dcesrv_lsa_get_policy_state()`, create a `LSA_HANDLE_POLICY`, steal the state under that handle, back-link `state->handle`, and return the wire handle.

`OpenPolicy3()` follows the same policy-state construction but first validates revision input. Version 1 returns revision 1 and the AES trusted-domain auth-info feature bit; other versions return `NT_STATUS_NOT_SUPPORTED`.

## State and Persistence Behavior

This file does not mutate persistent database records. It opens database connections and snapshots identity/configuration data into the policy state for use by subsequent calls. The policy security descriptor is decoded in memory and its DACL revision is forced to `SECURITY_ACL_REVISION_NT4`.

The policy state lifetime is tied to the created DCERPC handle unless callers such as handle-less lookup cache it separately on the connection.

## Dependencies and Integration Points

Key dependencies include `dcesrv_samdb_connect_as_user()`, `privilege_connect()`, LDB base DN helpers, `samdb_result_dom_sid()`, `samdb_result_guid()`, `samdb_search_dn()`, `samdb_system_container_dn()`, `sddl_decode()`, `se_map_generic()`, `security_acl_map_generic()`, `security_session_user_level()`, and `se_access_check()`.

The resulting state is consumed by all other LSA server areas: policy info queries, SID/name lookup, privilege DB operations, trusted-domain operations, DSSETUP role info, secrets, and forest trust handling.

## Risks and Edge Cases

- If SAMDB, privilege DB, domain DN, forest DN, builtin DN, or system DN cannot be opened or found, policy open fails and most LSARPC functionality is unavailable.
- The access check behavior intentionally grants system callers requested access outside the descriptor. Changes here can break local service callers.
- DNS domain and forest names are derived by truncating canonical DN strings at the first slash. DN format changes would affect returned policy info and lookup behavior.
- `OpenPolicy3()` feature negotiation is tightly coupled to trust-domain AES auth support in `dcesrv_lsa.c`.

## Test Signals

Test with named-pipe and local RPC transports, rejected non-named-pipe transports, null versus non-null `root_dir`, access masks including `MAXIMUM_ALLOWED`, administrator/system/user/anonymous tokens, OpenPolicy3 supported and unsupported versions, and environments with missing or malformed SAMDB metadata. Downstream policy query and lookup tests indirectly validate all initialized fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/lsa/lsa_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/lsa/lsa_lookup.c -->
# sources/user-network-fs/samba/source4/rpc_server/lsa/lsa_lookup.c

## Purpose

`lsa_lookup.c` implements LSARPC name-to-SID and SID-to-name translation. It supports all exposed LookupSids and LookupNames variants, including handle-based named-pipe/local calls and handle-less secure TCP calls. Resolution is layered through local predefined, builtin, account-domain, and remote winbind/trust-routing views.

## Important APIs, Types, and Functions

- `struct dcesrv_lsa_TranslatedItem` stores one lookup item, its resolved type/SID/name/authority, winbind index, completion flags, invalid SID marker, and parsed name hints.
- `struct dcesrv_lsa_Lookup_view` defines a pair of `lookup_sid` and `lookup_name` callbacks.
- `struct dcesrv_lsa_Lookup_view_table` maps an LSA lookup level to an ordered set of views.
- `dcesrv_lsa_lookup_name()` and `dcesrv_lsa_lookup_sid()` query SAMDB for one local account name or SID.
- `dcesrv_lsa_authority_list()` builds the output `lsa_RefDomainList` without duplicating authority names.
- `dcesrv_lsa_LookupSids_base_call()/finish()/map()/done()` implement the shared LookupSids engine.
- `dcesrv_lsa_LookupNames_base_call()/finish()/map()/done()` implement the shared LookupNames engine.
- Public handlers include `LookupSids`, `LookupSids2`, `LookupSids3`, `LookupNames`, `LookupNames2`, `LookupNames3`, and `LookupNames4`.
- `schannel_call_setup()` validates handle-less TCP calls and caches an implicit policy state on the connection.
- View implementations cover predefined SIDs/names, BUILTIN, local account domain, and winbind-backed trusted domains.

## Control Flow

LookupSids handlers normalize older and newer RPC shapes into an internal `lsa_LookupSids3` request. The base call validates lookup level, allocates domain and translated-name outputs, initializes one `TranslatedItem` per SID, stores SID and RID hints, and then iterates the selected view table. Each view may resolve an item, mark invalid SID, report none/some mapped, or return a real error. Unresolved remote items can cause a single asynchronous IRPC call to the winbind server. Finish builds the authority list, writes translated names, counts mapped items, and returns `NONE_MAPPED`, `STATUS_SOME_UNMAPPED`, `INVALID_SID`, or OK as appropriate.

LookupNames follows the same pattern but normalizes into `lsa_LookupNames4`. It parses each input into hints for `DOMAIN\principal`, `DOMAIN\`, UPN-style `principal@namespace`, isolated names, and null names. It validates lookup options, iterates views, optionally sends unresolved trusted-domain names to winbind, then maps the common `TranslatedSid3` output back into older `TranslatedSid` and `TranslatedSid2` structures by deriving RID values and special domain RID markers.

`schannel_call_setup()` is used by `LookupSids3` and `LookupNames4`, which do not take policy handles. It requires `NCACN_IP_TCP` and either Kerberos privacy or schannel authentication, then creates or retrieves a connection-cached policy state with access checks skipped.

View table selection depends on `lsa_LookupNamesLevel`: all views for `ALL`, account plus winbind for domain/global-catalog style levels, only account for primary-domain-only, and only winbind for forest-trust or RODC referral levels.

## State and Persistence Behavior

Lookup operations are read-only against SAMDB and trust-routing data. They allocate per-call state under the request memory context. Handle-less secure TCP lookups cache an implicit `lsa_policy_state` on the DCERPC connection to avoid reopening databases on each call.

Remote resolution uses an IRPC binding handle to the `winbind_server` task and marks the DCERPC call asynchronous until the callback receives results and invokes `dcesrv_async_reply()`.

## Dependencies and Integration Points

Local lookup depends on SAMDB searches over domain and builtin DNs, account-type mapping via `ds_atype_map()`, predefined SID helpers, loadparm role/name matching, and trust routing APIs such as `dsdb_trust_routing_table_load()`, `dsdb_trust_domain_by_name()`, `dsdb_trust_routing_by_name()`, and `dsdb_trust_domain_by_sid()`.

Remote lookup integrates with Samba messaging/IRPC, the generated LSA client table `ndr_lsa_c.h`, winbind server's LSARPC-compatible lookup calls, and DCERPC async reply machinery.

## Risks and Edge Cases

- Name parsing has many protocol-compatible corner cases: null names, `DOMAIN\`, isolated names, UPN suffixes, predefined names, and lookup-option restrictions. Small changes can alter Windows compatibility.
- Handle-less LookupSids3/LookupNames4 security is transport/auth dependent. Weakening `schannel_call_setup()` would expose domain lookup service over insecure TCP.
- Winbind referral is single-shot per base call. If a view creates an IRPC handle, all unresolved eligible items are batched; callback index mapping must stay correct.
- Within-forest trusts are mostly expected to resolve locally, with TODOs for multiple domains in a forest. Multi-domain forest behavior is an explicit gap.
- Status mapping is protocol-sensitive: `NONE_MAPPED`, `SOME_UNMAPPED`, `INVALID_SID`, and OK depend on counts and invalid SID markers.

## Test Signals

Useful tests include LookupNames and LookupSids across all protocol variants and lookup levels; predefined, BUILTIN, local domain, unknown, null, isolated, `DOMAIN\`, and UPN inputs; invalid SID inputs; handle-less TCP calls with schannel, Kerberos privacy, and rejected auth; winbind referral success, partial mapping, timeout, and failure; trusted-domain routing including forest-trust-only and RODC referral levels; and compatibility checks for older output structures' RID and sid-index mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/lsa/lsa_lookup.c -->
