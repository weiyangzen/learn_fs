# subset-b-009944 Samba RPC server research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/common/forward.c -->
# sources/user-network-fs/samba/source4/rpc_server/common/forward.c

Purpose: implements the common async forwarding bridge used by RPC server methods that delegate work to another Samba task over IRPC. The only exported entry point is `dcesrv_irpc_forward_rpc_call()`.

Important APIs and control flow: `dcesrv_irpc_forward_rpc_call()` checks that the incoming `dcesrv_call_state` permits async replies, resolves a named IRPC binding handle with `irpc_binding_handle_by_name()`, applies the caller security token to the IRPC handle, sends the NDR call by `dcerpc_binding_handle_call_send()`, marks the call with `DCESRV_CALL_STATE_FLAG_ASYNC`, and registers `dcesrv_irpc_forward_callback()`. The callback receives the IRPC completion, maps failures to `DCERPC_FAULT_CANT_PERFORM`, frees the subrequest, then calls `_dcesrv_async_reply()`.

State and persistence: no persistent storage. Runtime state is the talloc-owned `dcesrv_forward_state`, the pending tevent request, and mutations of `dce_call->state_flags` and `fault_code`.

Dependencies and integration: depends on tevent, generated DCE/RPC NDR tables, Samba messaging/IRPC, auth session info, and `dcesrv_imessaging_context()`. Used by DRSUAPI to forward replication and KCC operations to `dreplsrv` or `kccsrv`.

Risks and test signals: callers that cannot do async receive a fault. Failures in binding, allocation, security-token transfer, or send are reported as generic DCE/RPC faults, so tests should verify async vs sync caller behavior, timeout propagation, security token forwarding, and callback reply completion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/common/forward.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/common/loadparm.c -->
# sources/user-network-fs/samba/source4/rpc_server/common/loadparm.c

Purpose: builds the `dcerpc_server_info` structure from Samba loadparm configuration without forcing the parameter subsystem to depend on RPC server internals.

Important APIs and control flow: `_PUBLIC_ lpcfg_dcerpc_server_info()` allocates a zeroed `dcerpc_server_info`, references `lpcfg_workgroup()` as `domain_name`, and reads `server_info:version_major`, `version_minor`, and `version_build` with defaults `5`, `2`, and `3790`.

State and persistence: no writes. Values are derived from the active `loadparm_context` and returned as talloc-managed memory. The `domain_name` is a talloc reference to configuration-owned memory, not a duplicate.

Dependencies and integration: included by DNS server utilities to compose Windows-compatible DNS server version fields. The type comes from `rpc_server/common/common.h`; loadparm accessors come from `lib/param/param.h`.

Risks and test signals: no NULL check after `talloc_zero()`, so allocation failure would dereference NULL. Tests should cover default values, configured override values, and lifetime safety when the returned structure outlives temporary contexts. DNS server info tests should confirm the bit-packed version matches these fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/common/loadparm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/common/server_info.c -->
# sources/user-network-fs/samba/source4/rpc_server/common/server_info.c

Purpose: provides shared SRVSVC/server metadata helpers and central SAM database connection helpers for RPC server implementations.

Important APIs and control flow: server metadata helpers return platform id, server name normalization, server type flags, LAN root, user limits, announcement timers, license count, user path, and share-name validation. `dcesrv_common_get_server_type()` derives announce flags from `server_role`, optionally opens samdb as anonymous on AD DCs to decide PDC vs backup DC, and adds time-source/DFS flags from loadparm. `dcesrv_samdb_connect_session_info()` copies auth session info and remote address, opens samdb with those copies, and optionally stores audit session info in the LDB opaque `DSDB_NETWORK_SESSION_INFO`. `dcesrv_samdb_connect_as_system()` uses system credentials for writes needing elevated server authority while preserving caller audit details. `dcesrv_samdb_connect_as_user()` opens with the remote caller session.

State and persistence: metadata functions are mostly read-only with hardcoded compatibility values. SAM connection helpers do not write records but create live LDB contexts whose opaque audit state affects later audit logging.

Dependencies and integration: used by DNS, DRSUAPI, and other RPC servers. Depends on loadparm, SAMDB, auth/session utilities, roles, and tsocket address copying.

Risks and test signals: many SRVSVC values are hardcoded. Connection helper lifetimes are security-sensitive because copied session info must outlive the samdb context. Tests should cover anonymous/member/DC roles, PDC flag detection, invalid share-name characters, system vs user samdb access, and audit opaque propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/common/server_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/common/share_info.c -->
# sources/user-network-fs/samba/source4/rpc_server/common/share_info.c

Purpose: supplies common share metadata helpers for RPC share enumeration and query paths.

Important APIs and control flow: `dcesrv_common_get_share_permissions()`, `get_share_current_users()`, `get_share_dfs_flags()`, and `get_security_descriptor()` currently return hardcoded placeholder values. `dcesrv_common_get_share_type()` combines browseability with `SHARE_TYPE` to return disk, printer, IPC, and hidden flags. `dcesrv_common_get_share_path()` returns an empty path for IPC shares; otherwise it reads the share path, converts `/` to `\`, and prefixes it with `C:`.

State and persistence: read-only over `share_config`; no database writes. Returned strings are talloc-managed. Several comments state values should eventually come from an LDB database.

Dependencies and integration: depends on `param/share.h`, generated SRVSVC constants, and common share headers. These helpers feed SRVSVC-style RPC outputs.

Risks and test signals: path mapping is Windows-compatible but simplistic and assumes a `C:` drive prefix. Security descriptors are not exposed. Tests should cover IPC, printer, hidden/non-browseable, empty path, slash conversion, and NULL path allocation behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/common/share_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/dcerpc_server.c -->
# sources/user-network-fs/samba/source4/rpc_server/dcerpc_server.c

Purpose: Samba4 DCE/RPC server transport glue. It initializes RPC server modules, manages association groups, accepts stream connections, registers endpoint listeners, exposes messaging/server id helpers, prepares GENSEC auth, and terminates transports.

Important APIs and control flow: association-group helpers allocate random IDs in an IDR, validate transport compatibility, reference groups to connections, and remove them in destructors. `dcerpc_server_init()` runs static and shared `dcerpc_server` module initializers once. `dcesrv_sock_accept()` creates anonymous session info when needed, calls `dcesrv_endpoint_connect()`, installs stream transport callbacks, builds a tstream from named pipe or socket fd, handles NCALRPC peer credentials and system-token path mapping, then starts `dcesrv_connection_loop_start()`. Endpoint adders register Unix stream, NCALRPC, named pipe, and TCP sockets. `dcesrv_add_ep()` dispatches by binding transport. Auth helpers log successful authorization and start server-side GENSEC.

State and persistence: no durable storage, but it owns process runtime state: listener sockets, connection transport private data, send queues, talloc references, and association group counts/IDs.

Dependencies and integration: connects core `librpc/rpc/dcesrv_core.h` to Samba stream services, process models, socket/tstream, tsocket addresses, gensec, credentials, messaging, and module loading.

Risks and test signals: transport setup is high blast radius. Test binding to configured interfaces, wildcard TCP, NCALRPC default endpoint, named pipe endpoint validation, peer credential handling, association group reuse/rejection across transports, auth event logging, and cleanup of broken connections.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/dcerpc_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/dcerpc_server.h -->
# sources/user-network-fs/samba/source4/rpc_server/dcerpc_server.h

Purpose: public Samba4 RPC server header that exposes endpoint registration and connection-context helpers.

Important APIs/types: forward-declares `struct model_ops`; declares `dcesrv_add_ep()` for adding a configured endpoint to an event loop and process model; declares `_PUBLIC_ dcesrv_imessaging_context()` and `_PUBLIC_ dcesrv_server_id()` for retrieving the stream connection messaging context and server id from a `dcesrv_connection`.

State and persistence: no state; this is an interface contract.

Dependencies and integration: includes `librpc/rpc/dcesrv_core.h`, so users get core DCE/RPC server types. Implemented by `dcerpc_server.c`; used by forwarding, DNS server, DRSUAPI, common helpers, and other RPC server modules.

Risks and test signals: ABI/API changes affect modules. Compile coverage should include modules that register endpoints and those that retrieve messaging/server-id data for IRPC forwarding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/dcerpc_server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/dcerpc_server.pc.in -->
# sources/user-network-fs/samba/source4/rpc_server/dcerpc_server.pc.in

Purpose: pkg-config template for the DCE/RPC server library.

Important fields and flow: defines `prefix`, `exec_prefix`, `libdir`, `includedir`, and `modulesdir` substitution variables; names the package `dcerpc_server`; declares dependency `Requires: dcerpc`; emits `Version: @PACKAGE_VERSION@`; and links with `@LIB_RPATH@ -L${libdir} -ldcerpc-server`.

State and persistence: build-time metadata only. It is transformed by the build system into a `.pc` file consumed by downstream builds.

Dependencies and integration: coordinates external or internal consumers that need the DCE/RPC server library and modules directory.

Risks and test signals: stale library names or missing `Requires` entries break consumers at compile/link time. Build tests should validate pkg-config output after configure substitution and confirm `Libs` resolves the built shared library.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/dcerpc_server.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/dnsserver/dcerpc_dnsserver.c -->
# sources/user-network-fs/samba/source4/rpc_server/dnsserver/dcerpc_dnsserver.c

Purpose: implements the MS-DNSP DCE/RPC server endpoint. It serves DNS server/zone queries, zone creation/deletion, zone property resets, record enumeration, and record add/update/delete operations against Samba AD DNS data.

Important APIs and control flow: binding requires integrity. `dnsserver_connect()` creates per-connection `dnsserver_state`, opens samdb as the caller, initializes server info, enumerates fixed domain/forest DNS partitions, loads zones, initializes zone info, and caches the state with an interface magic. `dnsserver_query_server()` and `dnsserver_query_zone()` map many named properties to version-specific RPC output types. `dnsserver_operate_server()` implements `ZoneCreate` and validates many other operations as not implemented. `dnsserver_complex_operate_server()` supports property query, zone enumeration, directory partition enumeration, and partition info. `dnsserver_operate_zone()` implements dword property reset and DS zone delete. Enumeration paths search `dnsNode` records, build ordered trees, include optional additional A records, and return NDR-sized `DNS_RPC_RECORDS_ARRAY`. `dnsserver_update_record()` normalizes node names, rejects CNAME self-reference, and dispatches add, update, delete, or empty-node operations to `dnsdb.c`.

State and persistence: keeps cached partition/zone/serverinfo state per connection. Persistent writes happen through `dnsserver_db_create_zone()`, `dnsserver_db_delete_zone()`, `dnsserver_db_do_reset_dword()`, and record DB helpers. `dnsserver_reload_zones()` reconciles cached zones after zone create/delete.

Dependencies and integration: depends on `dnsserver.h`, generated DNS server NDR, common RPC/SAM helpers, AD DNS common utilities, LDB, and dlinklist.

Risks and test signals: many accepted operations return `WERR_CALL_NOT_IMPLEMENTED`; access-control FIXME remains on server configuration queries. Tests should cover client version differences, zone filters, root hints, additional-record expansion, CNAME loop rejection, permission failures, and cache reload after zone mutation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/dnsserver/dcerpc_dnsserver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/dnsserver/dnsdata.c -->
# sources/user-network-fs/samba/source4/rpc_server/dnsserver/dnsdata.c

Purpose: conversion and record-shaping utilities for DNS RPC data. It translates between MS-DNSP `dnsp_DnssrvRpcRecord` blobs stored in AD and `DNS_RPC_RECORD` structures returned over RPC, plus helper arrays, names, sorting, and tree building.

Important APIs and control flow: IP helpers copy IPv4 arrays and convert between legacy `IP4_ARRAY` and `DNS_ADDR_ARRAY`. `dns_split_name_components()` and `dns_split_node_name()` normalize zone-relative names. `dnsp_to_dns_copy()` converts stored records to RPC records, adding trailing dots for name-like records. `dns_to_dnsp_convert()` validates names when requested and strips trailing dots for stored data. Tree helpers build a limited DNS tree from LDB search results so enumeration can return a parent and direct children. `dns_fill_records_array()` parses each `dnsRecord` blob, filters by type and view flags, converts records, fixes flags for zone-root and glue data, and collects referenced names for additional data. `dns_name_compare()` sorts records by relevant child component.

State and persistence: no writes. It consumes LDB messages and allocates talloc-owned RPC result structures.

Dependencies and integration: used by `dcerpc_dnsserver.c` enumeration and by `dnsdb.c` record writes. Depends on generated `ndr_dnsp`, `ndr_dnsserver`, DNS common validation, and LDB messages.

Risks and test signals: name conversion and record matching are protocol-sensitive. `ip4_array_to_dns_addr_array()` appears to copy from the base IPv4 array pointer rather than the indexed element, a suspicious area for multi-address tests. Tests should cover all record types, invalid names, trailing-dot handling, IPv4/IPv6 mixed arrays, tree ordering, tombstoned records filtered upstream, and additional record collection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/dnsserver/dnsdata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/dnsserver/dnsdb.c -->
# sources/user-network-fs/samba/source4/rpc_server/dnsserver/dnsdb.c

Purpose: AD/LDB persistence layer for the DNS RPC server. It enumerates DNS partitions and zones, reads partition metadata, and mutates `dnsZone`/`dnsNode` objects and `dnsRecord`/`dNSProperty` attributes.

Important APIs and control flow: `dnsserver_db_enumerate_partitions()` constructs the fixed DomainDnsZones and ForestDnsZones partitions. `dnsserver_db_enumerate_zones()` searches `CN=MicrosoftDNS` for `dnsZone` objects, maps `RootDNSServers` to `.`, ignores trust anchors, and parses zone properties. `dnsserver_db_partition_info()` reports replica state and cross-reference DN. Mutating record helpers increment SOA serials via `dnsserver_update_soa()`, convert RPC records to DNSP blobs, assign rank, search for existing nodes, and add/replace/delete `dnsRecord` values. Deleting the last record deletes the node. Zone property reset rewrites matching `dNSProperty` blobs. Zone creation builds a security descriptor using DnsAdmins SID, creates `dnsZone` properties, and adds an `@` node with SOA and NS records. Zone deletion performs a transaction and tree delete.

State and persistence: this file owns persistent writes to samdb through `ldb_add`, `ldb_modify`, `ldb_delete`, `dsdb_delete`, and transactions. It also mutates in-memory `zoneinfo` during property reset.

Dependencies and integration: used by the RPC DNS dispatch layer. Depends on SAMDB, DSDB utilities, generated DNSP/security NDR, SDDL decode, domain SID lookup, and loadparm DNS domain.

Risks and test signals: SOA serial handling and duplicate detection are central. Tests should cover permissions, tombstoned node resurrection, duplicate records, SOA update failures, TTL-only updates, property parsing with malformed short properties, primary-only zone creation, security descriptor creation, and transaction rollback on zone delete failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/dnsserver/dnsdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/dnsserver/dnsserver.h -->
# sources/user-network-fs/samba/source4/rpc_server/dnsserver/dnsserver.h

Purpose: shared internal header for the Samba DNS RPC server.

Important APIs/types: defines `dnsserver_serverinfo`, `dnsserver_zoneinfo`, `dnsserver_partition`, `dnsserver_partition_info`, `dnsserver_zone`, and `dns_tree`. Declares data conversion functions from `dnsdata.c`, server/zone utility functions from `dnsutils.c`, and database functions from `dnsdb.c`.

State and persistence: structs represent per-connection server state, AD DNS partitions/zones, temporary parsed zone properties, and enumeration trees. Persistence itself is through declared `dnsserver_db_*` functions.

Dependencies and integration: includes generated DNSP/DNSServer IDL types, loadparm, and LDB. It is the coupling point among DNS RPC dispatch, data conversion, utility initialization, and database mutation.

Risks and test signals: changes to struct layout or prototypes affect all DNS server files. Compile and ABI checks should cover all consumers; behavioral tests should confirm `zoneinfo` defaults and DB helper contracts remain aligned.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/dnsserver/dnsserver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/dnsserver/dnsutils.c -->
# sources/user-network-fs/samba/source4/rpc_server/dnsserver/dnsutils.c

Purpose: initialization and lookup utilities for DNS RPC server state.

Important APIs and control flow: `fill_dns_addr_array()` builds `DNS_ADDR_ARRAY` data from configured Samba interfaces for listen addresses, supporting IPv4, IPv6, or mixed family. `dnsserver_init_serverinfo()` composes server-wide MS-DNSP properties from DCE/RPC server version info, loadparm DNS hostname/domain, samdb naming contexts, functional levels, listener addresses, and default DNS settings. `dnsserver_init_zoneinfo()` derives reverse-zone status, root-hints/cache behavior, primary-zone defaults, and applies parsed `dNSProperty` blobs through `dns_zoneinfo_load_zone_property()`. `dnsserver_find_zone()` compares names with Samba DNS equality. `dnsserver_name_to_dn()` builds child `DC=` DNs, mapping a zone name to `DC=@`. `dnsserver_zone_to_request_filter()` maps pseudo-zone names like `..AllZones` to request filter bitmasks.

State and persistence: no direct writes. It initializes talloc-owned server and zone info from configuration and samdb metadata.

Dependencies and integration: used during DNS RPC connection setup and zone mutations. Depends on interface enumeration, IP parsing, SAMDB naming context helpers, DNS common property loader, and common RPC loadparm version helper.

Risks and test signals: interface address encoding and pseudo-zone filters must match MS-DNSP expectations. Tests should cover no interfaces, IPv4/IPv6/mixed listeners, root zone defaults, reverse-zone detection, malformed zone properties, and each pseudo-zone request filter.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/dnsserver/dnsutils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/drsuapi/addentry.c -->
# sources/user-network-fs/samba/source4/rpc_server/drsuapi/addentry.c

Purpose: implements the DRSUAPI `DsAddEntry` RPC, used by replication partners to add directory objects, including special handling for new `nTDSDSA` objects.

Important APIs and control flow: `dcesrv_drsuapi_DsAddEntry()` pulls the DRS bind handle, requires `SECURITY_DOMAIN_CONTROLLER`, starts an LDB transaction for level 2 requests, commits origin objects with `dsdb_origin_objects_commit()` using `DSDB_REPL_FLAG_ADD_NCNAME`, fills the level 3 reply, calls `drsuapi_add_SPNs()`, and commits or cancels on failure. `drsuapi_add_SPNs()` scans added objects for `objectClass=ntDSDSA`, follows `serverReference`, reads the NTDS object GUID and server computer `dNSHostName`/`cn`, then permissively adds replication and LDAP SPNs to the referenced machine account.

State and persistence: writes replicated objects and servicePrincipalName values to samdb inside one transaction. Reply state includes added object identifiers and error data.

Dependencies and integration: depends on DRS bind state, SAMDB/DSDB replication commit helpers, security checks, loadparm DNS domain, and generated DRSUAPI NDR.

Risks and test signals: transaction integrity is critical because SPN failure cancels the add. Tests should cover non-DC access denial, unsupported levels, origin object commit failures, nTDSDSA with/without serverReference, duplicate SPNs under permissive modify, and transaction rollback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/drsuapi/addentry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/drsuapi/dcesrv_drsuapi.c -->
# sources/user-network-fs/samba/source4/rpc_server/drsuapi/dcesrv_drsuapi.c

Purpose: main DRSUAPI DCE/RPC server endpoint for Active Directory replication management, bind negotiation, DC metadata queries, selected local operations, and forwarding of replication/KCC work to internal tasks.

Important APIs and control flow: binding requires privacy. `dcesrv_drsuapi_DsBind()` creates `drsuapi_bind_state`, opens samdb as system for DC callers or as user for others, optionally opens system context for RODC secret replication, discovers local site/config GUIDs and replication epoch, records remote bind data, builds local supported-extension info, and returns a DCE handle. `DsUnbind` frees that handle. Replica add/del/mod/sync and KCC/get-info operations enforce DC-level access then forward asynchronously via `dcesrv_irpc_forward_rpc_call()` to `dreplsrv` or `kccsrv`. `DsCrackNames` dispatches to name/list helper implementations for supported formats. `DsRemoveDSServer` validates and optionally deletes an `NTDS Settings` subtree. `DsGetDomainControllerInfo` searches Sites for server objects and composes level 1/2/3 DC info including computer, NTDS, site, PDC, GC, and RODC fields. Unsupported calls fault with operation-range errors through `DRSUAPI_UNSUPPORTED`.

State and persistence: bind handles own `drsuapi_bind_state` and samdb contexts. Writes are limited in this file to `DsRemoveDSServer`; many other mutating replication operations are forwarded.

Dependencies and integration: uses generated DRSUAPI server boilerplate, common SAM helpers, DRS utilities, DSDB/SAMDB search helpers, IRPC messaging, and security/session APIs.

Risks and test signals: access control and forwarding semantics are security-sensitive. Tests should cover bind extension negotiation by request length, DC/RODC/user samdb selection, privacy enforcement, async vs sync forwarding timeouts, DC info levels, malformed site DNs, unsupported op faults, and delete behavior with `commit` false/true.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/drsuapi/dcesrv_drsuapi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/drsuapi/dcesrv_drsuapi.h -->
# sources/user-network-fs/samba/source4/rpc_server/drsuapi/dcesrv_drsuapi.h

Purpose: internal DRSUAPI server header shared by the main endpoint, add-entry implementation, get-changes implementation, update-ref code, and utility helpers.

Important APIs/types: defines `enum drsuapi_handle` with `DRSUAPI_BIND_HANDLE`; defines `drsuapi_bind_state` containing remote/local bind info, remote bind GUID, user samdb context, and optional system samdb context. Declares RPC method implementations for update refs, get NC changes, add entry, write account SPN, object identifier formatting, extended-DN search, security level/access checks, and secret attribute redaction.

State and persistence: the bind state is the per-handle runtime context for DRS calls. Persistence is delegated to implementations declared here.

Dependencies and integration: includes generated DRSUAPI IDL types, SAMDB, security tokens, and DCE/RPC call state. It is the contract between `dcesrv_drsuapi.c`, `addentry.c`, `drsutil.c`, and other DRS server modules.

Risks and test signals: handle type and bind state changes affect every DRS call. Compile coverage should include all DRS modules; behavioral tests should validate bind handle pull/create/free paths and system-context availability for RODC cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/drsuapi/dcesrv_drsuapi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/drsuapi/drsutil.c -->
# sources/user-network-fs/samba/source4/rpc_server/drsuapi/drsutil.c

Purpose: shared DRS server utilities for controlled LDB searches, caller authorization, secret attribute filtering, and extended-right access checks.

Important APIs and control flow: `drsuapi_search_with_extended_dn()` builds a search request manually, adds extended-DN, show-recycled, and reveal-internals controls, waits synchronously, and returns the result under the caller context. `drs_security_level_check()` optionally honors `drs:disable_sec_check`, otherwise compares the session security level against a required minimum and logs refused tokens. `drsuapi_process_secret_attribute()` removes values and clears originating change time for password, history, trust, and supplemental credential attributes. `drs_security_access_check()` and `drs_security_access_check_nc_root()` convert DRS object identifiers to DNs or NC roots, then call `dsdb_check_access_on_dn()` for an extended right, mapping denial to `WERR_DS_DRA_ACCESS_DENIED`.

State and persistence: no writes. It can alter in-memory replication attribute responses by redacting secret values.

Dependencies and integration: used by DRS get-changes/add-entry/update paths. Depends on DCE/RPC session info, loadparm, SAMDB/DSDB access checks, security tokens, and object identifier conversion helpers.

Risks and test signals: secret redaction and access checks protect sensitive replication data. Tests should cover disable flag behavior, domain-specific user levels, each secret ATTID, NULL DN denial, bad NC/DN conversion, recycled-object search visibility, and correct WERROR mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/drsuapi/drsutil.c -->
