# Research: subset-b-009945

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/drsuapi/getncchanges.c -->
# sources/user-network-fs/samba/source4/rpc_server/drsuapi/getncchanges.c

## Purpose
`getncchanges.c` implements the server side of `IDL_DRSGetNCChanges`, the core Active Directory replication RPC that returns changed objects, linked attributes, highwatermark progress, prefix mappings, and selected extended-operation results. It is the largest and most stateful part of this subset: normal replication can span multiple client calls, while extended operations such as RID allocation, object replication, secret replication, and FSMO owner changes are handled as special single-response cycles.

The file is responsible for translating LDB database records into DRSUAPI wire objects, enforcing replication access checks, filtering attributes through highwatermarks, uptodateness vectors, partial attribute sets, RODC filtered attribute behavior, and packaging linked attributes in Windows-compatible order. It also coordinates with `drsuapi_UpdateRefs()` when a client requests reference maintenance via replication flags.

## Important APIs, Types, and Functions
- `dcesrv_drsuapi_DsGetNCChanges()` is the public RPC handler. It pulls the DRS bind handle, normalizes request level 8 to level 10, checks source state and permissions, builds or resumes replication state, emits one chunk of objects and links, and updates output highwatermarks and UTD vectors.
- `struct drsuapi_getncchanges_state` is persistent replication-cycle state stored on `b_state->getncchanges_full_repl_state` for full replication. It tracks GUIDs to send, processed count, NC root identity, schema-NC status, GET_ANC/GET_TGT flags, min/max USNs, last/final highwatermarks, final UTD vector, linked attributes pending, and an optional object GUID cache.
- `struct getncchanges_repl_chunk` is per-call state. It caps object and link counts, tracks timeout budget, carries the linked list of response objects, and controls immediate linked-attribute emission.
- `get_nc_changes_build_object()` converts an LDB message into `drsuapi_DsReplicaObjectListItemEx`, loads `replPropertyMetaData`, filters changed attributes, converts LDAP syntax values into DRS attributes, applies secret processing/encryption, and validates attribute IDs.
- `get_nc_changes_filter_attrs()` implements attribute inclusion logic based on local USN, UTD vector, partial attribute set, RODC secret handling, RDN exclusion, and upgraded linked-attribute suppression.
- `get_nc_changes_add_links()` and `get_nc_changes_add_la()` collect forward linked attributes from extended DN values and build `drsuapi_DsReplicaLinkedAttribute` records with replication metadata.
- `getncchanges_get_sorted_array()` sorts linked attributes according to MS-DRSR CompareLinks ordering using NDR-form source/target GUIDs, attid, and active/deleted state.
- `getncchanges_add_ancestors()` and `getncchanges_chunk_add_la_targets()` support `DRSUAPI_DRS_GET_ANC` and `DRSUAPI_DRS_GET_TGT`, ensuring parent objects and linked-attribute targets are known to the client before dependent objects or links are sent.
- Extended-operation helpers include `getncchanges_rid_alloc()`, `getncchanges_repl_secret()`, `getncchanges_repl_obj()`, and `getncchanges_change_master()`.
- Permission classifiers `dcesrv_drsuapi_is_reveal_secrets_request()` and `dcesrv_drsuapi_is_gc_pas_request()` decide whether the request needs `GET_ALL_CHANGES` or can be satisfied by filtered-attribute rights.

## Control Flow
`dcesrv_drsuapi_DsGetNCChanges()` initializes the level-6 response, maps request revision 8 to request revision 10 when needed, creates a per-call chunk, rejects outbound replication from an RODC source, validates selected extended-operation destination DSA GUIDs, and requires `GUID_DRS_GET_CHANGES` on the request NC root. It then evaluates outbound replication disablement, partial attribute prefix maps, GC PAS access, and secret-reveal access. RODC callers have write-replication flags stripped.

The handler normalizes invocation-id and highwatermark semantics. A zero `source_dsa_invocation_id` is replaced with the local invocation id; a mismatched source invocation id resets the request highwatermark because the supplied HWM is not valid for this source. Full-sync requests discard the input UTD vector.

For ordinary replication, the handler may reuse `b_state->getncchanges_full_repl_state`. It invalidates that state if the caller switches NC roots or supplies a highwatermark different from the previous server output. There is a compatibility path for Entra ID Connect/Azure AD clients that zero `reserved_usn`; the code temporarily restores the saved value and continues only if the remaining highwatermark fields match.

When starting a new cycle, the handler resolves the naming context or extended-operation DN, verifies that ordinary replication targets an NC head, performs the requested extended-operation side effect if any, allocates `struct drsuapi_getncchanges_state`, and promotes it to bind-state lifetime only for non-extended full replication. It obtains the DCE/RPC session key for encrypted attributes.

Object collection happens once per replication cycle when `getnc_state->guids` is still unset. Normal replication searches for records with `uSNChanged >= min_usn + 1`, optionally applies a configured `drs:object filter`, critical-only filtering, base scope for async replication, or base scope for single-object exops. RID allocation uses a special collection path to return the RID Manager, the destination RID set, and destination server object in fixed order. Collected objects are reduced to GUID, DN, and USN, sorted by USN or by ancestor order for Samba 4.5 emulation, and stored as GUIDs to avoid holding full records across multiple calls.

Each call then prepares output naming-context data and prefix mappings, converts remote partial attribute sets into sorted local attids, optionally sends the NC root first, resumes pending GET_TGT linked-target checks, and loops over unsent GUIDs until object, link, or time limits are hit. Each GUID is re-searched by extended DN to fetch full current attributes. The object can be skipped if already sent as an ancestor. Otherwise it is built, added to the chunk, and its links are collected. The highwatermark advances only for messages whose `uSNChanged` is not greater than the cycle's initial maximum USN.

After object iteration, the handler sets object output fields, may call `drsuapi_UpdateRefs()` if requested by `DRSUAPI_DRS_ADD_REF` or `DRSUAPI_DRS_REF_GCSPN`, emits linked attributes either at the end of the cycle or immediately when configured/GET_TGT is active, and updates continuation state. Extended operations suppress final UTD and new-HWM output. Completed ordinary cycles return the final highwatermark and final UTD vector and then free the persistent state.

## State and Persistence Behavior
The file has two explicit state lifetimes. `struct getncchanges_repl_chunk` lives for one RPC call and enforces chunk size and work-time boundaries. `struct drsuapi_getncchanges_state` can persist across multiple full replication RPC calls on the DRS bind handle, holding the sorted GUID list, pending linked attributes, last returned highwatermark, and object cache.

Persistent state is deliberately not touched by extended operations. The comments call out that Azure AD Connect can interleave `REPL_OBJ` with full replication, so exops are treated as single-response cycles that must not reset the full replication cursor. On final ordinary response, the state is stolen to the per-call memory context and `b_state->getncchanges_full_repl_state` is cleared.

Database persistence occurs in several places. Secret replication can update `msDS-RevealedUsers` on the destination machine account inside an LDB transaction. RID allocation invokes the `DSDB_EXTENDED_ALLOCATE_RID_POOL` extended operation in a transaction. FSMO owner transfer modifies `fSMORoleOwner` in a transaction. `drsuapi_UpdateRefs()` can persist `repsTo` changes when a GetNCChanges request asks to add replication references.

The object cache for GET_ANC/GET_TGT uses `db_open_rbt()` and stores serialized GUID keys via dbwrap. It is per-replication-cycle memory-backed state, not durable storage.

## Dependencies and Integration Points
The code sits at the intersection of DCE/RPC, Samba DSDB, LDB, schema conversion, security, and replication services. It includes generated NDR DRSUAPI and DRS blob definitions, DSDB schema and utility APIs, security token helpers, DRS client utilities, dbwrap, sorting helpers, and the DCE/RPC server framework.

Key DSDB/LDB integrations include `drsuapi_search_with_extended_dn()`, `dsdb_search_dn()`, `drs_ObjectIdentifier_to_dn_and_nc_root()`, `dsdb_get_schema()`, `dsdb_get_oid_mappings_drsuapi()`, `dsdb_load_udv_v2()`, `dsdb_loadreps()`, and syntax-specific `ldb_to_drsuapi()` conversion functions. Security integration is through `drs_security_access_check_nc_root()`, `drs_security_access_check()`, session-token user levels, `samdb_rodc()`, and DRS extended rights GUIDs.

Replication side effects integrate with `updaterefs.c` through `drsuapi_UpdateRefs()`. Password/secret handling integrates with `drsuapi_encrypt_attribute()`, `drsuapi_process_secret_attribute()`, the DCE/RPC session key, RODC filtered attribute set helpers, and `samdb_confirm_rodc_allowed_to_repl_to()`.

## Risks and Edge Cases
- This is security-sensitive code. Incorrect classification of secret requests, GC PAS requests, or partial attribute mappings can leak secret attributes or deny legitimate replication.
- Highwatermark continuity is subtle. The file intentionally detects stale or unexpected continuation highwatermarks, but also carries an Azure AD compatibility exception for zeroed `reserved_usn`; changes here can break replication paging or cause duplicates/loss.
- The object list is collected once as GUIDs and then each object is re-searched later. That reduces memory but creates race windows with tombstone expunge or concurrent changes. The code skips disappeared objects but must avoid advancing the HWM past unseen changes.
- Linked attribute processing depends on upgraded link metadata in extended DNs. Missing `RMD_*` components, hanging targets, recycled targets, or inconsistent `uSNChanged` versus `RMD_LOCAL_USN` can cause internal errors or skipped links.
- GET_ANC and GET_TGT use a per-cycle object cache to avoid duplicate sends. Cache misuse can omit necessary ancestors or targets, while disabling the Samba 4.5 emulation changes ordering expectations.
- Secret replication both returns sensitive data and writes `msDS-RevealedUsers`. Transaction handling must keep the audit trail consistent with what is sent.
- Configured limits (`drs:max object sync`, `drs:max link sync`, `drs:max work time`, immediate link sync, object filter, GET_TGT support) directly affect paging behavior and interoperability.
- Several TODOs and comments admit imperfect behavior, including NC size reporting and incomplete extended-operation support.

## Test Signals
Useful tests should exercise normal multi-page replication with stable HWM/UTD progression, a stale highwatermark restart, the Azure AD `reserved_usn` compatibility path, prefix-map and partial-attribute-set conversion, GC PAS-only requests, and secret-request denial/allowance for RWDC and RODC callers. Linked-attribute tests should cover active/deleted links, recycled targets, hanging targets, sort order, immediate link sync, GET_TGT target inclusion, and GET_ANC ancestor ordering. Extended-op tests should cover RID allocation success/failure, FSMO owner transfer errors, `REPL_OBJ`, `REPL_SECRET`, outbound replication disabled, and RODC source rejection. Regression tests should verify that interleaved exops do not clear an in-progress full replication state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/drsuapi/getncchanges.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/drsuapi/updaterefs.c -->
# sources/user-network-fs/samba/source4/rpc_server/drsuapi/updaterefs.c

## Purpose
`updaterefs.c` implements `IDL_DRSUpdateRefs`, the RPC used to add or remove a destination DSA from an NC's `repsTo` list. It also exposes `drsuapi_UpdateRefs()` as an internal helper so other replication code, notably `DsGetNCChanges`, can re-establish monitoring references without going back through the public RPC handler.

The file validates request shape and NC identity, enforces topology-management access in the RPC entry point, updates `repsTo` transactionally, and asks `dreplsrv` to refresh after successful changes.

## Important APIs, Types, and Functions
- `struct repsTo` wraps the `repsFromToBlob` array and count loaded from the `repsTo` attribute.
- `uref_check_dest()` loads current `repsTo` and checks whether the destination DSA GUID already exists, returning `REF_ALREADY_EXISTS` or `REF_NOT_FOUND` unless combined add/delete or `GETCHG_CHECK` semantics allow idempotence.
- `uref_add_dest()` appends a version-1 `repsFromToBlob`, copies the caller-provided `repsFromTo1`, propagates `DRSUAPI_DRS_REF_GCSPN`, and saves the modified `repsTo`.
- `uref_del_dest()` removes all matching destination GUID entries from `repsTo`, compacts the array with `memmove()`, saves the result, and handles idempotent delete behavior.
- `drsuapi_UpdateRefs()` is the shared implementation used by RPC and internal callers. It validates input, resolves the requested object identifier to an NC root, applies add/delete updates inside an LDB transaction, and sends an IRPC refresh to `dreplsrv`.
- `dcesrv_drsuapi_DsReplicaUpdateRefs()` is the public RPC wrapper. It pulls the DRS bind handle, checks request level, enforces `GUID_DRS_MANAGE_TOPOLOGY`, validates non-admin DSA ownership, and delegates to `drsuapi_UpdateRefs()`.

## Control Flow
The RPC handler accepts only level 1. It checks topology-management access against the request naming context. If the caller is below administrator level, it requires that `dest_dsa_guid` belongs to the caller's SID via `dsdb_validate_dsa_guid()`. On success it calls the shared helper with the server messaging and event contexts.

`drsuapi_UpdateRefs()` first chooses `sam_ctx_system` when available, otherwise the normal SAM DB context. It rejects an all-zero destination GUID, a missing DNS name, and requests that specify neither add nor delete. It converts the supplied object identifier to both a normalized DN and NC root, then requires them to match. This prevents callers from updating references on arbitrary child objects.

The helper performs a preflight `uref_check_dest()` before opening a transaction. Existing/not-found errors are suppressed only when `DRSUAPI_DRS_GETCHG_CHECK` makes the operation idempotent. Inside the transaction it performs delete first, then add, based on option bits. A failure cancels the transaction and returns the underlying WERROR. A successful commit is followed by a best-effort IRPC `dreplsrv_refresh` notification.

## State and Persistence Behavior
The durable state is the NC root's `repsTo` attribute in the DSDB. Updates are written through `dsdb_savereps()` inside an LDB transaction. Add/delete in a single request is supported and delete runs first, which lets callers replace an existing reference with updated flags/data.

The `drepl_refresh_state` exists only long enough to send an IRPC refresh. If `dreplsrv` is not running or allocation fails, the function returns `WERR_OK` after the database commit; refresh is best effort and not part of the transaction.

## Dependencies and Integration Points
This file depends on the DCE/RPC server framework, DSDB SAM APIs, DRSUAPI NDR types, security/session helpers, IRPC generated client stubs, and Samba messaging. It integrates with `getncchanges.c` because `DsGetNCChanges` can call `drsuapi_UpdateRefs()` when clients set `DRSUAPI_DRS_ADD_REF` or `DRSUAPI_DRS_REF_GCSPN`. It also integrates with `dreplsrv` via `irpc_binding_handle_by_name()` and `dcerpc_dreplsrv_refresh_r_send()`.

## Risks and Edge Cases
- Request options are bitwise and can request both add and delete. The behavior is intentional, but tests must verify replacement semantics and idempotence under `GETCHG_CHECK`.
- `uref_del_dest()` removes every matching GUID, not just the first. That is probably correct cleanup behavior, but it can hide prior duplication issues.
- Refresh notification is best effort. A successful return does not prove `dreplsrv` observed the change immediately.
- The helper trusts `dest_dsa_dns_name` after only NULL validation; comments note that length validation is missing.
- Non-admin ownership validation happens only in the RPC wrapper. Internal callers must already have performed appropriate access checks before invoking `drsuapi_UpdateRefs()`.

## Test Signals
Tests should cover invalid parameters, non-NC object rejection, add of new `repsTo`, duplicate add, delete of existing reference, delete of missing reference, add+delete replacement, `GETCHG_CHECK` idempotence, `DRS_REF_GCSPN` flag propagation, transaction rollback on save failure, non-admin DSA ownership rejection, and a successful path with and without a running `dreplsrv` IRPC endpoint.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/drsuapi/updaterefs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/drsuapi/writespn.c -->
# sources/user-network-fs/samba/source4/rpc_server/drsuapi/writespn.c

## Purpose
`writespn.c` implements `IDL_DRSWriteAccountSpn`, allowing clients to add, replace, or delete `servicePrincipalName` values on an account object. The handler normally relies on DSDB access checks, but it contains a narrow system-context override for machine self-service SPN updates when the requested SPN refers to the caller's own `dNSHostName`.

## Important APIs, Types, and Functions
- `writespn_check_spn()` validates whether a non-admin/non-DC caller should be allowed to modify an SPN through `sam_ctx_system`. It checks the target object's `objectSid`, `dNSHostName`, and the Kerberos principal structure of the requested SPN.
- `dcesrv_drsuapi_DsWriteAccountSpn()` is the RPC handler. It supports request level 1, constructs an LDB modify message for `servicePrincipalName`, selects add/replace/delete flags, chooses system or normal SAM context, calls `dsdb_modify()`, and returns the operation status in `res1.status`.

## Control Flow
The handler pulls the DRS bind handle, allocates the level-specific result union, and only accepts level 1. It builds an LDB DN from `req->object_dn`; an invalid DN produces a successful top-level return with `res1.status = WERR_OK`, matching existing behavior.

For each requested SPN string, it calls `writespn_check_spn()`. That helper rejects NULL SPNs, searches the target DN for `objectSid` and `dNSHostName`, compares the target SID with the caller's primary SID, parses the SPN as a no-realm Kerberos principal, requires exactly two components, and compares the second component case-insensitively with the target `dNSHostName`. Any failure marks the batch as not eligible for system override, but the SPN is still added to the modify message.

After collecting values, the handler maps the DRS SPN operation to LDB modification flags: add, replace, or delete. If every SPN passed the narrow self-service check and `sam_ctx_system` is available, it modifies with system context; otherwise it uses the normal user context. `dsdb_modify()` is called with `DSDB_MODIFY_PERMISSIVE`. Failure is reported as `WERR_ACCESS_DENIED` in the embedded result while the RPC function itself returns `WERR_OK`.

## State and Persistence Behavior
The only durable state is the `servicePrincipalName` attribute on the requested account object. There is no explicit transaction in this file; persistence is delegated to `dsdb_modify()`. The function is stateless across calls and allocates request-scoped objects with talloc.

## Dependencies and Integration Points
The file depends on the DCE/RPC server framework, DSDB SAM APIs, Kerberos parsing (`smb_krb5_init_context_basic()`, `krb5_parse_name_flags()`, `smb_krb5_princ_component()`), security token/session helpers, and generated DRSUAPI types. Its access behavior depends heavily on DSDB ACL enforcement for the normal context and on `sam_ctx_system` availability for the self-service override.

## Risks and Edge Cases
- The override is batch-wide: one failing SPN causes the whole modification to use normal permissions, but all values remain in the LDB message. Tests should verify mixed valid/invalid SPN behavior.
- `writespn_check_spn()` only validates the second principal component against `dNSHostName`; it does not restrict the service class beyond requiring a two-component principal, despite the comment describing `SERVICE/dnshostname`.
- Invalid target DNs return success with no change, which may be intentional interoperability behavior but can mask caller mistakes.
- The RPC top-level result is often `WERR_OK` even when the embedded operation status is `WERR_ACCESS_DENIED`; callers must inspect `res1.status`.
- Kerberos parse and memory cleanup paths are security-sensitive because a parsing bug could incorrectly allow system-context modification.

## Test Signals
Tests should cover add, replace, and delete operations; invalid request levels; invalid object DNs; NULL SPN values; caller SID mismatch; missing `dNSHostName`; malformed principals; principals with too many or too few components; case-insensitive hostname match; mixed SPN batches; operation with and without `sam_ctx_system`; and DSDB ACL failure reflected in `res1.status`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/drsuapi/writespn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/echo/rpc_echo.c -->
# sources/user-network-fs/samba/source4/rpc_server/echo/rpc_echo.c

## Purpose
`rpc_echo.c` implements Samba's test/demo DCE/RPC echo endpoint. It provides simple IDL methods that exercise scalar returns, array allocation, pointer handling, union selection, enum marshalling, nested structures, double pointers, and asynchronous reply support.

## Important APIs, Types, and Functions
- `dcesrv_interface_rpcecho_bind()` delegates bind authorization to `dcesrv_interface_bind_allow_connect()`.
- `dcesrv_echo_AddOne()` returns the input integer plus one.
- `dcesrv_echo_EchoData()` copies an input byte buffer to an output buffer using `talloc_memdup()`.
- `dcesrv_echo_SinkData()` accepts data and discards it.
- `dcesrv_echo_SourceData()` allocates `len` bytes and fills them with increasing byte values.
- `dcesrv_echo_TestCall()` duplicates a string.
- `dcesrv_echo_TestCall2()` allocates a union and fills different arms based on request level.
- `dcesrv_echo_TestEnum()`, `dcesrv_echo_TestSurrounding()`, and `dcesrv_echo_TestDoublePointer()` cover enum, nested pointer, and triple-dereference cases.
- `dcesrv_echo_TestSleep()` either blocks with `sleep()` or schedules a tevent timer and returns asynchronously, depending on `DCESRV_CALL_STATE_FLAG_MAY_ASYNC`.

## Control Flow
Most calls are direct request-to-response transformations. The server binds without special checks. Data-returning functions allocate outputs on the RPC memory context and return `NT_STATUS_NO_MEMORY` when allocation fails. `TestCall2` switches on `r->in.level` and returns `NT_STATUS_INVALID_LEVEL` for unknown union arms.

`TestSleep` is the only stateful control path. If async replies are not permitted, it sleeps synchronously for the requested number of seconds and returns that value. If async is allowed, it allocates `echo_TestSleep_private`, stores the call state and request pointer, schedules `echo_TestSleep_handler()` on the call's event context, marks the call with `DCESRV_CALL_STATE_FLAG_ASYNC`, and returns zero immediately. The timer later writes `r->out.result` and calls `dcesrv_async_reply()`.

## State and Persistence Behavior
The endpoint has no durable state. Per-call allocations are attached to `mem_ctx`. Async sleep state is held in talloc memory owned by the request context until the timer fires. No database, file, or global state is modified.

## Dependencies and Integration Points
The file integrates with the generated echo NDR server stubs via `#include "librpc/gen_ndr/ndr_echo_s.c"`. It depends on the DCE/RPC server framework, talloc allocation conventions, and tevent for asynchronous sleep. It also includes `system/filesys.h` for `sleep()`.

## Risks and Edge Cases
- `SourceData()` fills a `uint8_t` array from an unsigned integer loop, so values wrap after 255 by design or by C conversion.
- `TestDoublePointer()` carefully checks the first two pointer levels before triple dereference; generated NDR pointer semantics are important here.
- `TestSleep()` trusts the requested seconds value; very large sleeps can tie up a synchronous worker or schedule long-lived async state.
- This endpoint allows connect binds and is intended for testing; exposing it in production-like configurations should be deliberate.

## Test Signals
Useful tests are mostly NDR/RPC conformance checks: zero-length and nonzero `EchoData`, allocation failure simulation, `SourceData` content, all `TestCall2` levels and invalid level, NULL and non-NULL surrounding structures, double-pointer NULL combinations, synchronous sleep behavior, async timer reply behavior, and bind accessibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/echo/rpc_echo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/epmapper/rpc_epmapper.c -->
# sources/user-network-fs/samba/source4/rpc_server/epmapper/rpc_epmapper.c

## Purpose
`rpc_epmapper.c` implements the server side of the endpoint mapper pipe. It enumerates registered RPC interfaces and maps abstract interface towers to concrete endpoint towers for clients trying to discover where and how to bind to services.

Only lookup, map, and lookup-handle-free are implemented. Insert, delete, inquiry, management delete, and authenticated map operations fault with `DCERPC_FAULT_OP_RNG_ERROR`.

## Important APIs, Types, and Functions
- `dcesrv_interface_epmapper_bind()` allows clients to bind to the endpoint mapper.
- `struct dcesrv_ep_iface` pairs an interface name with an `epm_tower`.
- `build_ep_list()` walks `dce_call->conn->dce_ctx->endpoint_list`, duplicates each endpoint binding, sets the abstract syntax to each registered interface syntax id, builds a tower, and returns a talloc array of available endpoint/interface pairs.
- `dcesrv_epm_Lookup()` pages through the built endpoint list using a DCE/RPC context handle of type `HTYPE_LOOKUP`.
- `dcesrv_epm_Map()` parses a client-supplied tower, validates transfer syntax, determines transport, searches available towers for matching transport and abstract syntax, and returns the concrete tower.
- `dcesrv_epm_LookupHandleFree()` frees a lookup context handle and zeros the output handle.

## Control Flow
`Lookup` pulls or creates an `HTYPE_LOOKUP` handle. On the first call, it allocates a small `rpc_eps` state object on the handle and fills it with all registered endpoints from `build_ep_list()`. It returns at most `max_ents` entries, each with a zero object UUID, interface annotation, and tower pointer. It then advances the internal array pointer and decrements the count. When no entries remain, it returns `EPMAPPER_STATUS_NO_MORE_ENTRIES`, zeros the wire handle, and frees the server handle.

`Map` builds a fresh endpoint list for the call, prepares default output containers, and rejects missing towers, zero `max_towers`, or towers with fewer than three floors. It extracts the abstract syntax from floor 0 and transfer syntax from floor 1, requires NDR transfer syntax, and derives the transport from the tower. It then scans available endpoint towers for matching transport and abstract syntax. On success it returns one tower; on failure it sets `num_towers` to zero and clears the tower pointer.

## State and Persistence Behavior
There is no durable persistence. Lookup state is stored in a DCE/RPC handle between paged `Lookup` calls. `build_ep_list()` snapshots the current endpoint list into talloc memory for that handle or call. `Lookup` mutates the saved pointer by advancing it, so the original base pointer is no longer directly retained after paging.

## Dependencies and Integration Points
The file depends on generated epmapper NDR types, DCE/RPC binding/tower helpers, endpoint registration data in `dcesrv_context`, and DCE/RPC handle macros. It is an integration point for every registered RPC endpoint because discovery output comes from `dce_ctx->endpoint_list`.

## Risks and Edge Cases
- `build_ep_list()` returns zero on allocation failures and also skips tower-build failures after logging. Callers see an empty or partial endpoint list rather than a detailed error.
- `Lookup` advances `eps->e` after each page; this is simple but means the saved pointer no longer points to the allocation base. Talloc ownership still comes from the handle allocation, but future changes must not free the advanced pointer directly.
- `Map` allocates output tower containers before validating input and returns `NO_MORE_ENTRIES` for many malformed inputs rather than a more specific fault.
- Only NDR transfer syntax is supported. Requests using unsupported transfer syntax or unknown transport are silently mapped to no entries.
- Unsupported management methods fault, so clients expecting dynamic registration APIs will not work.

## Test Signals
Tests should cover endpoint enumeration over multiple `Lookup` pages, handle exhaustion and handle-free behavior, empty endpoint lists, malformed towers, non-NDR transfer syntax, unknown transport floors, successful map by abstract syntax and transport, transport mismatch, abstract syntax mismatch, and unsupported operations faulting with operation-range errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/epmapper/rpc_epmapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/eventlog/dcesrv_eventlog6.c -->
# sources/user-network-fs/samba/source4/rpc_server/eventlog/dcesrv_eventlog6.c

## Purpose
`dcesrv_eventlog6.c` is a minimal server stub for the Windows EventLog6 RPC interface. Most operations are intentionally unimplemented and fault with `DCERPC_FAULT_OP_RNG_ERROR`. Two methods return success: `EvtRpcRegisterLogQuery`, which creates placeholder handles, and `EvtRpcQueryNext`, which returns `WERR_OK` without populating event data.

The file exists to expose enough of the generated interface for limited client compatibility or test coverage, not to provide a complete event log service.

## Important APIs, Types, and Functions
- `dcesrv_eventlog6_EvtRpcRegisterLogQuery()` creates two generic DCE/RPC handles via `dcesrv_handle_create()`: one query handle and one operation-control handle. It returns their wire handles.
- `dcesrv_eventlog6_EvtRpcQueryNext()` returns `WERR_OK` directly.
- All other static `dcesrv_eventlog6_*` methods call `DCESRV_FAULT(DCERPC_FAULT_OP_RNG_ERROR)`, including subscription, clear/export, render, seek, close, cancel, config, channel, publisher, metadata, and display-name operations.
- The generated server dispatch table is included through `librpc/gen_ndr/ndr_eventlog6_s.c`.

## Control Flow
Every RPC operation is a small static handler matching generated NDR prototypes. Most handlers immediately raise an operation-range fault. `EvtRpcRegisterLogQuery` allocates a server handle for `r->out.handle`, allocates a second server handle for `r->out.opControl`, and returns `WERR_OK` if both allocations succeed. `EvtRpcQueryNext` returns success without any visible validation, handle lookup, result count setup, or event buffer population in this source file.

## State and Persistence Behavior
There is no event log persistence and no backing query state. The only state created is generic DCE/RPC handle state from `dcesrv_handle_create()`, but no private data is attached to the handles. There is no explicit close implementation; `EvtRpcClose` faults rather than freeing handles.

## Dependencies and Integration Points
The file depends on the DCE/RPC server framework, generated EventLog6 NDR definitions, and common RPC server helpers. It integrates with generated dispatch by including `ndr_eventlog6_s.c`. It does not integrate with a log database, filesystem event log files, registry channel configuration, publisher metadata store, or access-control checks in this implementation.

## Risks and Edge Cases
- Returning success from `EvtRpcQueryNext` without event data may confuse clients that expect output fields to be meaningful. The generated marshalling layer may zero defaults, but semantic completeness is absent.
- `EvtRpcRegisterLogQuery` creates handles with type `0` and no private payload, so later operations cannot distinguish or validate query versus operation-control state in this file.
- `EvtRpcClose` and `EvtRpcCancel` fault, so clients cannot explicitly release or cancel the placeholder handles through this interface.
- Because most operations fault as operation-range errors, client compatibility depends on whether clients tolerate the stub behavior.
- There are no explicit access checks; the practical risk is limited by the lack of implemented data access, but any future implementation must add authorization around channel/query operations.

## Test Signals
Tests should verify that each unimplemented operation faults consistently, `EvtRpcRegisterLogQuery` returns two non-null handles on success and handles allocation failure, `EvtRpcQueryNext` returns `WERR_OK` with expected generated default outputs, and clients do not leak server handles indefinitely when close/cancel are unavailable. Compatibility tests with Windows eventlog clients should assert the exact observed behavior expected from this stub.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/eventlog/dcesrv_eventlog6.c -->
