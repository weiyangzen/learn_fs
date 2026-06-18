# subset-b-009936 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_become_dc.c -->
# sources/user-network-fs/samba/source4/libnet/libnet_become_dc.c

## Purpose
`libnet_become_dc.c` implements the source4 libnet orchestration for promoting an existing machine account into a domain controller. It follows the Windows 2003 style promotion sequence documented at the top of the file: CLDAP discovery, LDAP inspection and object preparation, DRSUAPI bind/add-entry, schema/config/domain replication, computer-account updates, and replica-reference publication. The exported API is asynchronous/synchronous pair `libnet_BecomeDC_send()`, `libnet_BecomeDC_recv()`, and `libnet_BecomeDC()`.

## Important APIs, Types, And Functions
The internal `struct libnet_BecomeDC_state` is the state carrier for the composite operation. It owns the `libnet_context`, CLDAP netlogon response, two LDAP connections, three DRSUAPI connection contexts, discovered domain/forest/source/destination DSA metadata, per-partition replication state, FSMO metadata, callback scratch structures, and flags such as `rodc_join` and `critical_only`.

`libnet_BecomeDC_send()` copies caller input into the state: domain DNS/NetBIOS/SID, source DSA address, destination NetBIOS name, derived destination DNS hostname, callbacks, and RODC flag. It then starts `becomeDC_send_cldap()`. `libnet_BecomeDC_recv()` waits and clears only the output structure; this file primarily reports errors through the composite status rather than populating `r->out.error_string`.

Discovery and LDAP helpers include `becomeDC_send_cldap()`, `becomeDC_recv_cldap()`, `becomeDC_ldap_connect()`, and many `becomeDC_ldap1_*()` probes. The probes read RootDSE, behavior versions, schema object version, Windows 2003 update revision, infrastructure/RID-manager FSMO owners, destination site object, destination computer object, and destination server object/backlink state. `becomeDC_check_options()` invokes the caller's optional callback after discovery but before mutation.

DRSUAPI helpers include `becomeDC_drsuapi_connect_send()`, `becomeDC_drsuapi_bind_send()`, `becomeDC_drsuapi_bind_recv()`, `becomeDC_drsuapi1_add_entry_send()`, `becomeDC_drsuapi_pull_partition_send()`, `becomeDC_drsuapi_pull_partition_recv()`, and `becomeDC_drsuapi_update_refs_send()`. The add-entry path constructs an `nTDSDSA` or `nTDSDSA-RO` object with encoded DRS attributes. The pull path chooses request level 8 when supported, otherwise level 5, and handles compressed/uncompressed level 1 and level 6 replies.

## Control Flow
The operation begins with a CLDAP/netlogon ping to the source DSA address on port 389. The response supplies forest/domain names, source DC names and site, and destination client site; an empty client site falls back to the server site. The first LDAP connection reads RootDSE and related objects, validates remote function levels against `ads:dc function level`, confirms site and computer objects, creates or reuses the server object, and ensures `serverReference` points at the destination computer.

After LDAP preparation, the first DRSUAPI connection binds with a W2K3 bind GUID and creates `CN=NTDS Settings,<server DN>` through `DsAddEntry`. The request includes security descriptor, object class/category, invocation ID, master NCs, schema location, behavior version, system flags, server reference, and RODC-specific options. On success, the returned NTDS object GUID is saved, `prepare_db` callback is invoked, and second/third DRSUAPI connections are established using the same binding string and association group.

The third DRSUAPI connection pulls schema and configuration partitions first. Each `DsGetNCChanges` reply updates high-watermark/source GUID state and calls the matching chunk callback (`schema_chunk`, `config_chunk`) when present. The code then opens a second LDAP connection, changes the computer account to `UF_SERVER_TRUST_ACCOUNT | UF_TRUSTED_FOR_DELEGATION`, moves the account into the Domain Controllers container, and starts domain partition replication. Domain replication first runs with `DRSUAPI_DRS_CRITICAL_ONLY`; after that completes it repeats without critical-only and without `DRSUAPI_DRS_GET_ANC`. Finally, `DsReplicaUpdateRefs` is issued for schema, config, and domain partitions, and the composite completes.

## State And Persistence Behavior
Persistent remote state changes are substantial: LDAP may create/modify the server object, DRSUAPI creates the NTDS Settings object, LDAP changes `userAccountControl`, LDAP moves the computer object to the Domain Controllers container, DRSUAPI pulls replicated data through callbacks that typically persist into a local database, and DRSUAPI publishes replica references. Local process state is held in talloc-owned composite memory and the caller's callbacks receive pointers into that state.

The partition high-watermarks are updated across `more_data` loops and are passed to the callback in `libnet_BecomeDC_StoreChunk`. The gensec session key for the pull connection is exposed to the chunk callback. Function-level compatibility is controlled by loadparm (`ads:dc function level`), while `become_dc:force krb5`, `become_dc:print`, and `repl:RODC` affect DRS binding and update-ref behavior.

## Dependencies And Integration Points
This file integrates with Samba's composite/tevent async framework, CLDAP netlogon ping helpers, LDB/samdb LDAP helpers, DRSUAPI generated RPC bindings, security descriptor/NDR encoders, GENSEC session-key access, loadparm, and tsocket address construction. The public contract is shaped by `libnet_become_dc.h`; the most important integration points are the caller-supplied `check_options`, `prepare_db`, and per-partition chunk callbacks.

## Risks
The workflow mutates real AD topology and account state before the full operation completes, so partial failure can leave server objects, NTDS Settings objects, account-control changes, or replication refs requiring cleanup. The code assumes many LDAP searches return exactly one object and maps deviations to generic invalid response errors. RODC handling is present but includes suspicious flag manipulation in config/domain replication paths that clears `schema_part.replica_flags` rather than the active partition flags. `libnet_BecomeDC_recv()` does not preserve a detailed output error string, so callers must rely on status/logging. Callback failures abort promotion after prior remote mutations. The DRS code also has compatibility complexity around compression levels, bind info lengths, and Kerberos-vs-NTLM behavior.

## Test Signals
Useful tests would exercise CLDAP discovery fallback for empty client site, function-level rejection, server-object collision/backlink handling, add-vs-replace `serverReference`, RODC add-entry attributes, multi-chunk replication high-watermark loops, callback error propagation, and update-ref options. Integration tests need a disposable AD domain because the code performs LDAP and DRSUAPI writes. Existing Samba promotion/provision tests and DRS replication tests are the likely signal sources; unit-level coverage can target pure request construction only with heavy mocking.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_become_dc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_become_dc.h -->
# sources/user-network-fs/samba/source4/libnet/libnet_become_dc.h

## Purpose
`libnet_become_dc.h` defines the public request, metadata, partition, chunk, and callback types consumed by `libnet_BecomeDC`. It is the contract between the generic libnet promotion orchestrator and the caller that validates options, prepares the local database, and stores replicated schema/config/domain chunks.

## Important APIs, Types, And Functions
`struct libnet_BecomeDC` is the top-level API object. Inputs include domain DNS/NetBIOS/SID, source DSA address, destination DSA NetBIOS name, callback table, and `rodc_join`. Output currently exposes `error_string`.

`struct libnet_BecomeDC_Domain`, `Forest`, `SourceDSA`, and `DestDSA` split caller input from constructed promotion metadata. Constructed fields include DNs, GUIDs, behavior versions, schema version, site GUID, computer/server/NTDS DNs, invocation ID, and account-control value.

`struct libnet_BecomeDC_Partition` describes a replicated naming context and tracks source/destination DSA GUIDs, source invocation ID, high-watermark, `more_data`, replica flags, and a `store_chunk` callback. `struct libnet_BecomeDC_StoreChunk` is the callback payload containing the promotion metadata, partition, original request pointers for levels 5/8/10, response pointers for counters 1/6, and the GENSEC session key.

`struct libnet_BecomeDC_Callbacks` supplies optional `check_options`, `prepare_db`, `schema_chunk`, `config_chunk`, and `domain_chunk` callbacks plus private data.

## Control Flow
The header mirrors the phases in the C file: discovery populates `Domain`, `Forest`, and `SourceDSA`; pre-mutation validation uses `CheckOptions`; DRS add-entry and local initialization use `PrepareDB`; replication uses the partition and chunk types. Callbacks return `NTSTATUS` or `WERROR`, allowing the orchestrator to abort when caller validation, local preparation, or storage fails.

## State And Persistence Behavior
The header does not persist data itself, but it defines the data passed to persistence callbacks. `prepare_db` is the hook for creating local database structures before replication, and each chunk callback is expected to persist replicated objects. The callback payload pointers are owned by the active promotion state, so consumers must copy any data they need beyond the callback lifetime.

## Dependencies And Integration Points
The file includes DRSUAPI generated declarations and references Samba security/domain types such as `dom_sid`, `GUID`, `DATA_BLOB`, `NTSTATUS`, and `WERROR`. It is included by libnet users that need domain-controller promotion and by the implementation file.

## Risks
Because the API exposes internal request/response pointers in `StoreChunk`, callers can accidentally retain short-lived memory or couple tightly to DRSUAPI levels. The top-level output has only `error_string`, while the implementation primarily reports through status. The callback contract must be honored carefully: returning success without durable storage may allow the promotion sequence to continue even though local replication state is incomplete.

## Test Signals
Compile-time tests should catch DRSUAPI type drift. Integration tests should verify callbacks receive populated domain/forest/source/destination metadata, correct partition DNs and high-watermarks, and correct RODC-vs-writable metadata across schema, config, and domain chunks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_become_dc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_domain.c -->
# sources/user-network-fs/samba/source4/libnet/libnet_domain.c

## Purpose
`libnet_domain.c` provides composite libnet helpers for opening, closing, and listing domains over SAMR and LSA RPC pipes. It centralizes handle acquisition and caches active SAMR/LSA policy/domain handles in `struct libnet_context` for reuse by user/group/lookup operations.

## Important APIs, Types, And Functions
Public APIs are `libnet_DomainOpenSamr_send/recv()`, `libnet_DomainOpenLsa_send/recv()`, generic `libnet_DomainOpen_send/recv()` plus synchronous `libnet_DomainOpen()`, matching close APIs for SAMR/LSA/generic close, and `libnet_DomainList_send/recv()` plus synchronous `libnet_DomainList()`.

`domain_open_samr_state` carries RPC connect state, SAMR connect/lookup/open/close requests, domain SID, handles, access mask, and monitor callback. `domain_open_lsa_state` carries LSA open policy state. `domain_list_state` carries SAMR enumeration state, resume handle, collected domain list, and monitor callback.

## Control Flow
SAMR open first ensures a SAMR pipe exists, using `libnet_RpcConnect_send()` to a DC when needed. If an existing domain handle is cached in `ctx->samr`, it returns immediately when domain name and access mask match; otherwise it closes the old handle before reconnecting. The normal SAMR sequence is `samr_Connect`, `samr_LookupDomain`, then `samr_OpenDomain`.

LSA open similarly ensures an LSA pipe, then sends `lsa_OpenPolicy2` with a security QoS block. Generic open dispatches by `io->in.type`.

Close operations validate that the requested domain matches the cached `ctx->samr.name` or `ctx->lsa.name`, issue `samr_Close` or `lsa_Close`, and clear cached handle/name/SID state on success. Domain listing connects to SAMR on a target host if needed, calls `samr_Connect`, loops over `samr_EnumDomains` while `STATUS_MORE_ENTRIES` is returned, accumulates domain names, closes the SAMR connect handle, and returns the list.

## State And Persistence Behavior
This file maintains process-local RPC state in `libnet_context`: SAMR/LSA pipes, connect handles, domain handles, domain SID/name, and access masks. It does not write persistent storage. The cached handles affect later operations in the same libnet context and must be closed or replaced when a different domain/access mask is needed.

## Dependencies And Integration Points
The implementation depends on Samba composite contexts, generated SAMR and LSA RPC clients, `libnet_RpcConnect`, policy-handle helpers, talloc ownership, and monitor messages (`mon_SamrConnect`, `mon_SamrLookupDomain`, `mon_SamrOpenDomain`, `mon_LsaOpenPolicy`, close/enumeration events). Higher-level group/user/lookup functions depend on these helpers and on prerequisite wrappers such as `samr_domain_opened()` and `lsa_domain_opened()`.

## Risks
The handle cache makes behavior stateful: stale or mismatched cached handles can cause invalid-parameter returns or unintended close/reopen sequences. Some TODO comments note missing null-pipe checks in close paths. SAMR open requests `SEC_FLAG_MAXIMUM_ALLOWED` for `samr_OpenDomain` instead of the caller access mask after connect, which may matter against restrictive servers. `DomainList` accumulates names but does not resolve SIDs despite the output structure carrying a SID string field. Enumeration closes the connect handle after each page path, so resume behavior depends on server semantics and caller reentry.

## Test Signals
Tests should cover cached-handle reuse, changing access mask/domain forcing close and reopen, LSA and SAMR close mismatch errors, domain listing across `STATUS_MORE_ENTRIES`, monitor event ordering, and failure propagation when RPC call status differs from transport status. Existing user/group tests indirectly exercise this file through prerequisite domain-open helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_domain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_domain.h -->
# sources/user-network-fs/samba/source4/libnet/libnet_domain.h

## Purpose
`libnet_domain.h` declares the request/result structures for opening, closing, and listing SAMR/LSA domains through libnet.

## Important APIs, Types, And Functions
`enum service_type` selects `DOMAIN_SAMR` or `DOMAIN_LSA`. `struct libnet_DomainOpen` contains input service type, domain name, and access mask, and returns a policy handle plus error string. `struct libnet_DomainClose` identifies which cached service/domain handle should be closed. `struct libnet_DomainList` takes a hostname and returns a count plus an array of `domainlist { sid, name }`. `struct msg_rpc_lookup_domain` is a monitor payload containing a domain name looked up over RPC.

## Control Flow
The structures map directly to `libnet_domain.c`: open dispatches by service type, close dispatches by service type, and list enumerates SAMR domain databases on a host. The header itself contains no logic.

## State And Persistence Behavior
The types carry handles and error strings but do not own persistent state. The implementation stores successful handles in `libnet_context`, so consumers of this header should treat the returned handle as part of a broader context-owned session.

## Dependencies And Integration Points
The header relies on generated/standard Samba types such as `policy_handle`. It is consumed by libnet modules that need a domain handle before performing SAMR/LSA operations, including group and lookup helpers.

## Risks
The output `domainlist.sid` field may be null depending on implementation path. Callers must set `type`, `domain_name`, and appropriate access masks, and must not assume the returned policy handle remains valid after `libnet_DomainClose`.

## Test Signals
Compile tests should catch enum/struct contract changes. Functional tests should verify SAMR and LSA open/close callers populate and clear these structures consistently and that domain-list consumers tolerate null SID strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_domain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_export_keytab.c -->
# sources/user-network-fs/samba/source4/libnet/libnet_export_keytab.c

## Purpose
`libnet_export_keytab.c` exports Kerberos keys from Samba's KDC database view into a keytab. It supports exporting all principals or a single principal, retaining or removing stale keytab entries, including only current or also historic keys, and gMSA key generation when direct key material is unavailable.

## Important APIs, Types, And Functions
The public API is `libnet_export_keytab()`. It initializes a Kerberos context, builds a Samba KDC base/db context from the libnet context and optional caller-provided `samdb`, chooses SDB flags, validates safe complete-keytab export behavior, and calls `sdb_kt_copy()`.

`sdb_kt_copy()` opens the target keytab for writing, fetches either one principal (`samba_kdc_fetch`) or iterates the KDC DB (`samba_kdc_firstkey`/`samba_kdc_nextkey`), optionally removes obsolete keytab entries, exports current and optionally old/older keysets, and handles gMSA key material through `smb_krb5_fill_keytab_gmsa_keys()`.

## Control Flow
For a single principal, the code parses the Kerberos principal name, fetches any matching SDB entry with `SDB_F_GET_ANY | sdb_flags`, exports its keys, and stops after one record. For full export, it iterates all KDC entries. Before a full export with stale-entry removal disabled, it refuses to write over an existing keytab file; if the file does not exist, stale retention is forced because there are no old entries to remove.

Each SDB entry is processed in a temporary talloc context. If stale entries should be removed, `smb_krb5_remove_obsolete_keytab_entries()` removes entries for that principal that do not match the current KVNO. For gMSA entries with no direct keys, the code generates keytab entries from gMSA password material and can treat missing user keys as non-fatal during full export. For normal entries, it checks whether each exact keytab entry already exists before adding it. Historic key export writes current keys at `kvno`, old keys at `kvno - 1`, and older keys at `kvno - 2`.

## State And Persistence Behavior
The persistent side effect is modification of the keytab named by `r->in.keytab_name`. When `keep_stale_entries` is false, obsolete keytab entries for exported principals may be removed. Complete export has a guard against overwriting an existing keytab unless stale entries are kept. The function reads KDC state from the configured Samba KDC DB context and may rely on current time for gMSA key validity.

## Dependencies And Integration Points
Dependencies include Samba Kerberos helpers, KDC DB glue/SDB iteration, gMSA utilities, Heimdal/MIT krb5 keytab APIs, `smb_krb5_*` keytab utilities, `samba_kdc_setup_db_ctx()`, and optional `samdb` with `DSDB_GMSA_TIME_OPAQUE`. The header `libnet_export_keytab.h` supplies the request structure.

## Risks
This path handles secret key material and writes keytabs, so permission, path, and overwrite behavior are security-sensitive. Full export without a local `samdb` can produce no keys except authorized gMSA cases; the error message explicitly calls this out. Historic KVNO handling assumes simple `kvno - 1` and `kvno - 2` mapping. Duplicate suppression depends on exact keytab-entry comparison. Failure paths preserve some detailed Kerberos errors but may return generic NT status codes.

## Test Signals
Tests should cover single-principal export, full export refusing existing files when stale entries would be removed, duplicate suppression, stale-entry cleanup, current-only vs historic-key export, gMSA export with/without authorization, missing key behavior with `keep_stale_entries`, and propagation of krb5 parse/open/add errors. Security tests should verify file overwrite and keytab path behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_export_keytab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_export_keytab.h -->
# sources/user-network-fs/samba/source4/libnet/libnet_export_keytab.h

## Purpose
`libnet_export_keytab.h` declares the request/result structure and function prototype for exporting Samba KDC keys into a Kerberos keytab.

## Important APIs, Types, And Functions
`struct libnet_export_keytab` has inputs `keytab_name`, optional `principal`, optional `samdb`, `keep_stale_entries`, `only_current_keys`, and `as_for_AS_REQ`. Output is `error_string`. The public function is `NTSTATUS libnet_export_keytab(struct libnet_context *ctx, TALLOC_CTX *mem_ctx, struct libnet_export_keytab *r)`.

## Control Flow
The header exposes two modes: a specific principal export when `principal` is non-null, and complete domain export when it is null. Flags influence whether stale keytab entries are retained, whether historic keys are exported, and whether KDC lookup uses AS-REQ semantics or administrative data semantics.

## State And Persistence Behavior
The structure identifies the keytab file that will be modified by the implementation and the database context to read from. The header itself has no persistence logic.

## Dependencies And Integration Points
The header includes `includes.h` and `libnet/libnet.h`, and references `struct ldb_context` for optional database input. It is used by command or provisioning paths that need service keys in a keytab.

## Risks
Callers must treat `keytab_name` as a write target containing secrets. Passing `principal == NULL` requests broad export. Misunderstanding `only_current_keys` or `keep_stale_entries` can either omit keys needed during rollover or retain unwanted old keys.

## Test Signals
API-level tests should verify all inputs are honored by `libnet_export_keytab.c`, especially null principal mode, `samdb` time handling for gMSA keys, and `error_string` population on failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_export_keytab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_group.c -->
# sources/user-network-fs/samba/source4/libnet/libnet_group.c

## Purpose
`libnet_group.c` implements source4 libnet operations for creating groups, retrieving group information, and listing domain groups over SAMR/LSA RPC. It follows the library's composite async pattern with synchronous wrappers.

## Important APIs, Types, And Functions
Public APIs are `libnet_CreateGroup_send/recv()` and `libnet_CreateGroup()`, `libnet_GroupInfo_send/recv()` and `libnet_GroupInfo()`, and `libnet_GroupList_send/recv()` and `libnet_GroupList()`.

`create_group_state` tracks the domain-open prerequisite and `libnet_rpc_groupadd` call. `group_info_state` supports lookup-by-name or lookup-by-SID, carrying `libnet_LookupName` and `libnet_rpc_groupinfo` requests. `grouplist_state` carries LSA domain info, SAMR group enumeration state, resume index, page size, and returned group array.

## Control Flow
Group creation first ensures a SAMR domain handle through `samr_domain_opened()`. If the prerequisite is already met it immediately sends `libnet_rpc_groupadd_send()`, otherwise it resumes from `continue_domain_opened()` after `libnet_DomainOpen_recv()`. Completion is just `libnet_rpc_groupadd_recv()` followed by `composite_done()`.

Group info first opens the SAMR domain. For `GROUP_INFO_BY_NAME`, it resolves the name through `libnet_LookupName_send()`, verifies the SID type is a domain group or alias, and then requests full group info by SID/name. For `GROUP_INFO_BY_SID`, it converts the provided SID to a string and calls groupinfo directly. Results copy group name, SID, member count, and description into the caller output.

Group list first ensures an LSA policy handle, queries `LSA_POLICY_INFO_DOMAIN` to obtain the domain SID, ensures a SAMR domain handle, then sends `samr_EnumDomainGroups`. It accepts OK, `STATUS_MORE_ENTRIES`, and `NT_STATUS_NO_MORE_ENTRIES` as successful enumeration states, builds SIDs by adding each returned RID to the queried domain SID, and returns resume index/count/groups.

## State And Persistence Behavior
Create group persists a new group account on the remote domain through SAMR. Info and list are read-only. The functions rely on and may populate cached SAMR/LSA domain handles in `libnet_context` through prerequisite helpers. Returned arrays and strings are talloc-moved to the caller memory context.

## Dependencies And Integration Points
Dependencies include `libnet_DomainOpen`, `libnet_LookupName`, SAMR/LSA generated RPC calls, `libnet_rpc_groupadd`, `libnet_rpc_groupinfo`, security SID helpers, and monitor callbacks. This file is structurally parallel to source4 user-management helpers.

## Risks
Group list returns only the current SAMR enumeration page; callers must use `resume_index` to continue on `STATUS_MORE_ENTRIES`. `libnet_GroupInfo_recv()` steals `s->lookup.out.sid` even for lookup-by-SID mode, where the lookup path is not populated, so SID output may be null despite successful info by SID. SID type filtering for lookup-by-name rejects non-group names but relies on LSA lookup returning accurate type. Remote mutation in create has no rollback if later receive/error handling fails.

## Test Signals
Tests should cover successful group creation, prerequisite domain-open paths both already-open and async-open, group info by name for domain groups and aliases, rejection of users/computers as `NT_STATUS_NO_SUCH_GROUP`, info by SID output fields, paged group listing with resume index, and all three accepted enumeration statuses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_group.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_group.h -->
# sources/user-network-fs/samba/source4/libnet/libnet_group.h

## Purpose
`libnet_group.h` declares libnet request/result structures for group creation, group information lookup, and group listing.

## Important APIs, Types, And Functions
`struct libnet_CreateGroup` takes group name and domain name, returning `error_string`. `enum libnet_GroupInfo_level` selects lookup by name or SID. `struct libnet_GroupInfo` takes domain name plus either `group_name` or `group_sid`, returning group name, SID, member count, description, and error string. `struct libnet_GroupList` takes domain name, page size, and resume index, returning count, next resume index, and an array of `grouplist { sid, groupname }`.

## Control Flow
The structures correspond to the create/info/list flows in `libnet_group.c`. Group-list callers are expected to handle paged enumeration by feeding `out.resume_index` back into `in.resume_index` when the status indicates more entries.

## State And Persistence Behavior
The header itself is declarative. The create request causes remote SAMR mutation in the implementation; info/list are read-only. Returned pointer fields are allocated under the caller's memory context by the receive wrappers.

## Dependencies And Integration Points
The header references Samba SID types and is consumed by libnet group-management callers and tests. It relies on `libnet/libnet.h` inclusion paths for core types.

## Risks
The union in `libnet_GroupInfo.in.data` must match the selected level. Callers must not assume `GroupList` returns all groups in one call. The group SID output for info-by-SID depends on implementation details and may need validation.

## Test Signals
Compile/API tests should cover both union variants. Functional tests should verify error-string population, paged list semantics, and correct SID/name fields in returned group arrays.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_group.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_join.c -->
# sources/user-network-fs/samba/source4/libnet/libnet_join.c

## Purpose
`libnet_join.c` implements domain join operations. It creates or reuses a machine/domain account over SAMR, sets its password and account flags, performs additional ADS/LDAP/DRSUAPI finishing for AD domains, and provides a convenience wrapper for joining the local machine as a member and storing local secrets.

## Important APIs, Types, And Functions
The main public functions are `libnet_JoinDomain()` and `libnet_Join_member()`. The important internal helper is `libnet_JoinADSDomain()`, called when `libnet_RpcConnect` discovered an AD realm.

`libnet_JoinDomain()` uses `libnet_RpcConnect` with `LIBNET_RPC_CONNECT_DC_INFO`, SAMR calls (`Connect`, `LookupDomain`, `OpenDomain`, `CreateUser2`, `LookupNames`, `OpenUser`, `DeleteUser`, `QueryUserInfo`, `GetUserPwInfo`), and `libnet_SetPassword()` with `LIBNET_SET_PASSWORD_SAMR_HANDLE`. `libnet_JoinADSDomain()` uses DRSUAPI `DsBind`/`DsCrackNames` and LDAP writes through LDB. `libnet_Join_member()` wraps `JoinDomain` for workstation trust accounts and calls `provision_store_self_join()`.

## Control Flow
`libnet_JoinDomain()` connects to a SAMR pipe either automatically by domain or through a specified binding. It ensures domain name and SID are known, opens the domain, and attempts `samr_CreateUser2` for the requested account name/type. If the user exists, it looks up and opens the user; when `recreate_account` is true, it deletes and recreates the account. It then queries account flags, verifies that existing trust type matches the requested account type, clears disabled/password-not-required bits, gets password policy, chooses caller-provided or generated password, and calls `libnet_SetPassword()` with `samr_UserInfo21` to set full name and account flags.

After SAMR success, the function fills output fields: join password, domain SID/name/realm, account SID, SAMR pipe/binding, user handle, error string, KVNO default, and server DN default. If a realm exists, `libnet_JoinADSDomain()` completes AD-specific steps. That helper switches the SAMR binding to sealed DRSUAPI over TCP when appropriate, binds, cracks the account SID to a DN, opens LDAP to the target host, reads the account's `msDS-KeyVersionNumber`, SPNs, DNS hostname, and GUID, writes `servicePrincipalName` and `dNSHostName`, attempts to set `msDS-SupportedEncryptionTypes`, cracks the domain name to a DN, stores account/domain DN/KVNO/GUID outputs, and invokes `libnet_JoinSite()` for server-trust joins.

`libnet_Join_member()` chooses or derives the local NetBIOS name, appends `$` for the account, calls `libnet_JoinDomain()` as `ACB_WSTRUST`, builds `provision_store_self_join_settings`, stores local join secrets via provisioning code, and moves selected outputs back to the caller.

## State And Persistence Behavior
Remote persistent effects include machine account creation/deletion/recreation, password reset, account-flag update, SPN and DNS hostname LDAP replacement, encryption-type update when supported, and possible site/server updates for DC joins through `libnet_JoinSite()`. Local persistent effects happen only in `libnet_Join_member()`, which writes self-join secrets including domain, realm, NetBIOS name, secure channel type, machine password, KVNO, and domain SID.

The function also returns live SAMR pipe/user handles by reparenting them to the caller context. Generated passwords are returned in output and then used for local secret storage by the member wrapper.

## Dependencies And Integration Points
Dependencies include SAMR and DRSUAPI generated RPC clients, `libnet_RpcConnect`, `libnet_SetPassword`, LDAP/LDB wrappers, samdb helpers, Kerberos encryption constants, credentials, loadparm, and provisioning secret-storage APIs. `libnet_join.h` defines the request/result structures. Site integration is delegated to `libnet_JoinSite()`.

## Risks
The join path has many partial-mutation points: account creation or deletion can succeed before password/SPN/site steps fail. `recreate_account` is destructive. Existing account type mismatches are rejected, but newly created accounts with unexpected type also fail after creation. ADS finishing assumes DRSUAPI `DsCrackNames` and LDAP writes are available; older or non-AD domains skip this only if no realm was discovered. SPN replacement writes only HOST SPNs built from NetBIOS and realm, which can overwrite pre-existing servicePrincipalName values through `dsdb_replace`. Error strings vary between detailed messages and null on allocation failures.

## Test Signals
Tests should cover automatic and specified-binding joins, new account creation, existing account reuse, account-type mismatch, destructive recreate, password-policy minimum length, caller-provided password, generated password, AD finishing with KVNO/account DN/domain DN outputs, encryption-type write tolerated on old schema, member join secret persistence, and failure cleanup expectations. Integration coverage requires a test DC because the code depends on real SAMR/DRSUAPI/LDAP semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_join.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_join.h -->
# sources/user-network-fs/samba/source4/libnet/libnet_join.h

## Purpose
`libnet_join.h` declares the public data structures for domain join operations and local join secret storage inputs.

## Important APIs, Types, And Functions
`enum libnet_Join_level` and `enum libnet_JoinDomain_level` distinguish automatic discovery from specified parameters. `struct libnet_JoinDomain` includes domain/account/netbios/binding/level/account-type/recreate/password inputs and rich outputs including join password, domain SID/name/realm, domain/account/server DNs, KVNO, SAMR pipe/binding/user handle, account SID, and account GUID.

`struct libnet_Join_member` is a smaller workstation-member join request with domain, optional NetBIOS name, level, and optional password, returning join password/domain SID/domain name. `struct libnet_set_join_secrets` describes data needed to store local secrets: domain, realm, NetBIOS/account names, secure-channel type, password, KVNO, and domain SID.

## Control Flow
The header supports the two-layer implementation: `JoinDomain` handles remote account join and AD finishing, while `Join_member` wraps it and stores local secrets. The secret structure is compatible with provisioning storage logic.

## State And Persistence Behavior
The header itself has no persistence behavior. Its structures carry secret data (`join_password`, `account_pass`) and live RPC handles. Implementations can mutate remote domain accounts and local secrets databases based on these fields.

## Dependencies And Integration Points
The header includes generated netlogon declarations for `netr_SchannelType` and references Samba SID, GUID, DCE/RPC pipe, binding, and policy-handle types. It is used by join commands, provisioning paths, and tests.

## Risks
Callers must protect password fields and manage returned handle lifetimes. `recreate_account` signals potentially destructive remote account replacement. `acct_type` must match SAMR account-control expectations. Automatic vs specified levels determine whether binding or domain discovery is used.

## Test Signals
API tests should verify field propagation from `libnet_JoinDomain()` and `libnet_Join_member()`, including KVNO/account GUID for AD joins and local secret settings for member joins. Security-oriented tests should ensure password fields are not logged unexpectedly by callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_join.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_lookup.c -->
# sources/user-network-fs/samba/source4/libnet/libnet_lookup.c

## Purpose
`libnet_lookup.c` implements libnet name and DC lookup helpers. It resolves NetBIOS hostnames to addresses, finds writable LDAP/DS DCs via CLDAP, and resolves account/group names to SIDs through LSA.

## Important APIs, Types, And Functions
Public APIs are `libnet_Lookup_send/recv()` and `libnet_Lookup()`, `libnet_LookupHost_send()` and `libnet_LookupHost()`, `libnet_LookupDCs_send/recv()` and `libnet_LookupDCs()`, and `libnet_LookupName_send/recv()` and `libnet_LookupName()`.

`lookup_state` carries the `nbt_name` and resolved address. `lookup_name_state` carries the LSA domain-open prerequisite, one-name `lsa_LookupNames` request, returned SID array/domain list, and monitor callback. `prepare_lookup_params()` initializes the single-name LSA lookup structures.

## Control Flow
`libnet_Lookup_send()` validates hostname input, builds an NBT name using the requested type, chooses either caller-provided `resolve_ctx` or `ctx->resolve_ctx`, and calls `resolve_name_send()`. Receive wraps the single resolved address in a one-element string list.

`libnet_LookupHost_send()` is a shortcut that forces `NBT_NAME_SERVER`. `libnet_LookupDCs_send()` maps the local workgroup name to the configured DNS domain, requests DCs with LDAP, DS, and writable flags using the configured netlogon ping protocol and optional `ctx->server_address`, and calls `finddcs_cldap_send()`. Receive returns one `nbt_dc_name` built from the CLDAP result address and PDC DNS name.

`libnet_LookupName_send()` ensures an LSA domain policy handle through `lsa_domain_opened()`, prepares a level-1 single-name `lsa_LookupNames` request, and sends it. Completion checks transport status, RPC result, and that returned SID count matches the requested name count. Receive constructs a full SID by adding the returned RID to the first referenced domain SID, then returns RID, SID type, SID pointer/string, and error string.

## State And Persistence Behavior
Lookup operations are read-only on remote systems. They may populate or reuse the cached LSA handle in `libnet_context` through the domain-open prerequisite. Results are allocated under the caller memory context. No local persistent storage is written.

## Dependencies And Integration Points
Dependencies include composite contexts, Samba resolve subsystem, finddc/CLDAP helpers, credentials/loadparm for DC discovery, generated LSA RPC bindings, security SID helpers, and `libnet_DomainOpen` prerequisite helpers. Group information uses `libnet_LookupName()` to translate group names before SAMR groupinfo.

## Risks
`LookupDCs` returns exactly one DC despite the plural API, reflecting `finddcs_cldap` output rather than a full list. Name lookup builds a SID only from the first referenced domain, which is appropriate for single-name lookup but would not generalize to multiple names. `Lookup_recv()` returns no error string in its structure. Null or missing domain/SID arrays can produce success with no SID when count is zero, so callers must inspect outputs.

## Test Signals
Tests should cover invalid hostname parameter handling, caller-provided vs context resolve context, host shortcut name type, workgroup-to-DNS-domain mapping in DC lookup, writable LDAP/DS DC filtering, LSA domain-open prerequisite paths, no-match lookup returning success with empty outputs, malformed SID-count response rejection, and integration with group lookup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_lookup.h -->
# sources/user-network-fs/samba/source4/libnet/libnet_lookup.h

## Purpose
`libnet_lookup.h` declares libnet data structures for host lookup, DC lookup, and name-to-SID lookup.

## Important APIs, Types, And Functions
`struct libnet_Lookup` takes hostname, NBT name type, and optional resolve context, returning address list. `struct libnet_LookupDCs` takes domain name and name type, returning DC count and `nbt_dc_name` array. `struct libnet_LookupName` takes account/group name plus domain name, returning SID pointer, RID, LSA SID type, SID string, and error string. `struct msg_net_lookup_dc` is a monitor payload for DC lookup messages.

## Control Flow
The structures correspond to `libnet_lookup.c`: generic hostname resolution, host shortcut resolution, CLDAP DC discovery, and LSA name lookup. `LookupName` callers should provide a domain name suitable for opening an LSA policy handle.

## State And Persistence Behavior
The header has no persistence behavior. Its outputs are read-only lookup results allocated by implementation receive functions.

## Dependencies And Integration Points
The declarations reference resolve contexts, NBT DC-name structures, SID types, and LSA SID type enums. They integrate with group/user/domain code that needs name resolution before SAMR operations.

## Risks
The address and DC outputs are pointer-based and depend on caller memory context lifetime. The plural DC lookup structure may contain only one DC from the current implementation. SID output may be null when no name match is found even if the wrapper reports a successful completed lookup.

## Test Signals
API tests should validate struct initialization and output ownership. Functional tests should cover hostname resolution, DC discovery, name lookup success and no-match behavior, and monitor payload correctness when used by callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet_lookup.h -->
