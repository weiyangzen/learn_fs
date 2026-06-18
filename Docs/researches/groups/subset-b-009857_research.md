# subset-b-009857 research

Grouped research for Samba source3 Witness and Workstation RPC server code, RPC server build wiring, and rpcclient command modules for CLUSAPI, DFS, DRSUAPI, DSSETUP, ECHO, EPMAPPER, EVENTLOG, FSRVP, and IRemoteWinspool. Each section is source-tree aligned and bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/witness/srv_witness_nt.c -->
# sources/user-network-fs/samba/source3/rpc_server/witness/srv_witness_nt.c

## Purpose
`srv_witness_nt.c` implements Samba's server-side Witness RPC endpoint for Scale-Out File Server style notifications in CTDB clusters. It answers interface-list queries, accepts Witness v1/v2 registrations, persists registration metadata for other rpcd components, tracks CTDB IP ownership changes, and completes asynchronous `AsyncNotify` calls when resource, client-move, share-move, or forced responses are triggered.

## Important APIs, types, and functions
- `struct swn_service_globals` is the process-global Witness service state: DCE context, connection registration DB, server name, local CTDB VNN, cached interface list generation, registration list, and persistent registration TDB.
- `struct swn_service_interface` represents one advertised IPv4/IPv6 interface with group name, state, local/nonlocal flag, current VNN, and generation counters.
- `struct swn_service_registration` is the core registration object. It owns the policy handle, client/net/share identity, registered IP, queued notifications, usage expiry timer, forced unregister timer, messaging listener, and async notify queue.
- `swn_service_init_globals()` opens the in-memory connection DB and `rpcd_witness_registration.tdb` with mode `0600`, initializes CTDB callbacks, and installs the global destructor.
- `swn_service_reload_interfaces()` refreshes CTDB public/node IP state through `ctdbd_all_ip_foreach()` and marks disappeared interfaces unavailable before deleting them.
- `dcesrv_interface_witness_bind()` registers connection IPs with CTDB release-IP handling and requires DCERPC integrity or privacy on binds.
- `_witness_GetInterfaceList()`, `_witness_Register()`, `_witness_RegisterEx()`, `_witness_UnRegister()`, and `_witness_AsyncNotify()` are the exported RPC operations.
- `swn_server_registration_message_done()` consumes `MSG_RPCD_WITNESS_REGISTRATION_UPDATE` messages and converts rpcd-internal registration updates into queued Witness notifications.
- `swn_service_async_notify_send()`, `swn_service_async_notify_trigger()`, and `_witness_AsyncNotify_done()` implement queued async DCE/RPC completion.

## Control flow
Startup is lazy: bind, register, or interface-list calls invoke `swn_service_init_globals()` and then `swn_service_reload_interfaces()`. Interface reload increments a generation, reads CTDB IP assignments, filters loopback and link-local addresses, adds or updates interfaces, and notifies matching registrations when state, owner VNN, or local-interface status changes. CTDB `IPREALLOCATED` callbacks invalidate the cache and force a reload.

Registration validates protocol version, required strings, server net name, and numeric IP address. v2 additionally sanity-checks share name by requiring log escaping to preserve the string. After matching the IP to a known interface, `swn_server_registration_create()` allocates the registration, creates a policy handle, starts a filtered messaging read, creates a stopped async queue, installs expiry timers, links the registration into memory, and stores an NDR-encoded `rpcd_witness_registration` in `rpcd_witness_registration.tdb` keyed by the policy-handle GUID.

Async notification calls look up the policy handle, update usage, mark the DCERPC call asynchronous, and wait on the registration queue. Triggers are prioritized: forced responses first, then resource changes, client moves, share moves, and currently unimplemented IP notifications. Resource-change notifications use the registered IP as the resource name; move notifications enumerate matching interfaces by target node or target IP. Some non-available or moved-away cases schedule a five-second forced unregister so Windows clients re-register cleanly.

## State and persistence behavior
Runtime state is held under `swn_globals` and talloc-owned registration/interface lists. Persistent cross-process state is the lock-path `rpcd_witness_registration.tdb`, which contains sensitive client keys, account names, SIDs, endpoints, registration time, context handles, and requested registration parameters. Registration destruction stops the async queue, completes outstanding waiters with not-found behavior, deletes the TDB row, unlinks from the global list, and drops the policy handle. Connection IP registrations are tracked in an rbt DB keyed by connection pointer and are unregistered from CTDB in the connection destructor.

## Dependencies and integration points
This file integrates with CTDB (`ctdbd_all_ip_foreach`, IP reallocation and release-IP SRVIDs), Samba messaging, dbwrap/TDB, talloc, tevent queues/timers, DCE/RPC server internals, generated Witness and rpcd-witness NDR, policy handles, Samba address utilities, and loadparm configuration. It is enabled only when CTDB support is available through the build file's `RPC_WITNESS` and `rpcd_witness` definitions.

## Risks and edge cases
- The file manages async lifetime across policy handles, talloc destructors, tevent queues, CTDB callbacks, and DCE/RPC orphan/cancel paths; regressions can produce use-after-free, stuck async calls, or missed unregisters.
- `rpcd_witness_registration.tdb` contains sensitive data and must remain private and reliably cleaned on registration destruction.
- Interface changes deliberately emit transient unavailable states when VNN or locality changes, so notification ordering is protocol-sensitive.
- `swn_service_async_notify_send()` has a missing semicolon after `tevent_queue_add_entry(...)` in the inspected source, a direct compile-break signal if this exact tree is built.
- Share validation is intentionally permissive, so correctness relies on downstream rpcd update producers and client behavior.
- The five-second forced unregister workaround is tuned for observed Windows Server behavior and could be fragile across client versions.

## Test signals
Useful validation includes building with CTDB enabled, exercising Witness bind authentication levels, `GetInterfaceList`, v1/v2 register/unregister, orphaned/cancelled `AsyncNotify`, CTDB IP failover/reallocation, rpcd registration update messages for client/share move and forced responses, and checking that TDB rows are inserted and deleted. Cluster integration tests should verify Windows client re-registration after unavailable and moved-away notifications.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/witness/srv_witness_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/wkssvc/srv_wkssvc_nt.c -->
# sources/user-network-fs/samba/source3/rpc_server/wkssvc/srv_wkssvc_nt.c

## Purpose
`srv_wkssvc_nt.c` implements the source3 Workstation Service RPC server. Most legacy WKSSVC operations are explicit stubs, while workstation information, logged-on user enumeration, domain join, and domain unjoin operations have concrete behavior.

## Important APIs, types, and functions
- `struct dom_usr` stores user, domain, and login time for workstation user enumeration.
- `get_domain_userlist()` derives local logged-in users from Samba session records whose remote machine matches the local NetBIOS name.
- `create_wks_info_100()`, `create_wks_info_101()`, and `create_wks_info_102()` allocate workstation info structures from Samba version, NetBIOS name, workgroup, LAN root, and logged-on user count.
- `_wkssvc_NetWkstaGetInfo()` implements levels 100, 101, and 102 with progressively stricter access checks.
- `_wkssvc_NetWkstaEnumUsers()` implements levels 0 and 1 for non-AD-DC source3 service mode and requires Builtin Administrators membership.
- `_wkssvc_NetrJoinDomain2()` and `_wkssvc_NetrUnjoinDomain2()` decode encrypted admin credentials using the RPC session key, build libnet join/unjoin contexts, and call `libnet_Join()` or `libnet_Unjoin()` under root.
- The many `WERR_NOT_SUPPORTED` handlers set `p->fault_state = DCERPC_FAULT_OP_RNG_ERROR` for unsupported calls.

## Control flow
`NetWkstaGetInfo` switches on the requested level. Level 100 is available to anonymous callers, level 101 requires authenticated users, level 102 requires Builtin Administrators, and level 502 is denied. `NetWkstaEnumUsers` rejects AD DC mode, checks administrator membership, then returns an empty level-0 user list or a level-1 list built from session records and the configured password server.

`NetrJoinDomain2` validates domain, admin account, encrypted password, and caller privileges. It rejects insecure join and machine-password-passed flags, extracts a 16-byte session key, decodes the WKSSVC password buffer, splits the admin domain/user, creates ADS credentials, populates a `libnet_JoinCtx`, and runs the join as root. `NetrUnjoinDomain2` follows the same credential path, populates a `libnet_UnjoinCtx` using `lp_realm()`, ORs in `WKSSVC_JOIN_FLAGS_JOIN_TYPE`, and runs unjoin as root.

## State and persistence behavior
Info and enum calls allocate response structures only. Join/unjoin calls can persistently alter local domain membership, machine account state, and registry-backed Samba configuration when `lp_config_backend_is_registry()` is true. User enumeration reads current Samba session state but does not maintain its own cache.

## Dependencies and integration points
The implementation depends on DCE/RPC call/session state, Samba security tokens and privilege checks, session listing from `session.h`, loadparm values, ADS credential helpers, generated WKSSVC NDR, and libnet join/unjoin APIs. It is built as the `RPC_WKSSVC` subsystem with dependency `LIBNET`.

## Risks and edge cases
- Join/unjoin are high-impact operations and depend on correct privilege checks, session-key extraction, password decoding, and root boundary handling.
- `create_enum_users1()` increments `i` both in the loop and while assigning `other_domains`, which can skip entries and misreport `entries_read`; that is a code-level bug signal.
- The user enumeration model is an approximation of Windows workstation semantics and only sees local Samba sessions to the local server.
- Many unsupported calls intentionally fault with operation-range behavior, which clients may distinguish from plain `WERR_NOT_SUPPORTED`.

## Test signals
Tests should cover `NetWkstaGetInfo` levels and access denial paths, administrator-only user enumeration, AD DC rejection behavior, join/unjoin invalid parameter and privilege failures, bad session-key handling, encrypted password decode failures, and successful join/unjoin in an isolated domain test environment. Static or unit coverage should catch the level-1 enumeration loop increment issue.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/wkssvc/srv_wkssvc_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/wscript_build -->
# sources/user-network-fs/samba/source3/rpc_server/wscript_build

## Purpose
`wscript_build` defines the source3 RPC server build graph: the main DCERPC host binary, shared worker library, per-service rpcd helper binaries, RPC server framework subsystems, individual RPC service subsystems, Spotlight/mdssvc variants, and the aggregate `RPC_SERVICE` dependency set.

## Important APIs, types, and functions
- `bld.SAMBA_BINARY('samba-dcerpcd', ...)` builds the installed source3 DCERPC host.
- `bld.SAMBA_LIBRARY('RPC_WORKER', private_library=True, ...)` builds common worker support used by rpcd helpers.
- `bld.SAMBA3_BINARY(...)` defines installed service workers such as `rpcd_classic`, `rpcd_lsad`, `rpcd_spoolss`, `rpcd_epmapper`, `rpcd_fsrvp`, `rpcd_witness`, and `rpcd_mdssvc`.
- `bld.SAMBA3_SUBSYSTEM(...)` defines service libraries such as `RPC_DSSETUP`, `RPC_EPMAPPER`, `RPC_EVENTLOG`, `RPC_NETDFS`, `RPC_WKSSVC`, and `RPC_WITNESS`.
- Conditional build flags include `enabled=bld.env.with_ctdb` for Witness and `bld.env.spotlight_backend_es` for Elasticsearch-backed mdssvc sources and installed mappings.

## Control flow
The file is evaluated by waf during configuration/build. It first declares core RPC host and worker components, then service-specific worker binaries, then framework subsystems, then each RPC service subsystem. Finally it assembles `RPC_SERVICE`, which pulls together the classic in-process service set used by `rpcd_classic`, and defines the socket helper subsystem.

## State and persistence behavior
This file does not manage runtime state. Its persistent effect is the build artifact graph and install layout under `${SAMBA_LIBEXECDIR}` and `${SAMBA_DATADIR}`. Conditional settings decide whether CTDB Witness and Elasticsearch mdssvc support are compiled and installed.

## Dependencies and integration points
It is the integration point between source files under `source3/rpc_server/*`, generated NDR libraries, `smbd_base`, `RPC_WORKER`, service-specific dependencies such as `LIBNET`, `PRINTING`, `LIBCLI_WINREG_INTERNAL`, `samba-cluster-support`, and optional Spotlight/Elasticsearch dependencies.

## Risks and edge cases
- Missing dependencies here surface as link failures or runtime helper binaries without required service symbols.
- `rpcd_witness` and `RPC_WITNESS` are CTDB-gated; non-CTDB builds will not have Witness service support.
- The aggregate `RPC_SERVICE` includes many services but not every standalone rpcd binary, so changing service placement can affect classic vs external RPC worker behavior.
- Optional mdssvc source/dependency expansion must stay synchronized with installed data files.

## Test signals
Build validation should cover default builds, CTDB-enabled builds, and Spotlight Elasticsearch builds. Runtime smoke tests should verify expected rpcd binaries are installed and that `rpcd_classic` links the aggregate service set. Dependency graph tests or CI build matrices are the primary signal for this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_clusapi.c -->
# sources/user-network-fs/samba/source3/rpcclient/cmd_clusapi.c

## Purpose
`cmd_clusapi.c` adds `rpcclient` commands for Microsoft Cluster API operations. It can query cluster metadata, enumerate cluster objects, open resources/nodes, change resource online/offline state, and pause/resume cluster nodes.

## Important APIs, types, and functions
- Commands use generated `dcerpc_clusapi_*` client stubs from `ndr_clusapi_c.h`.
- `cmd_clusapi_open_cluster()`, `cmd_clusapi_get_cluster_name()`, `cmd_clusapi_get_cluster_version()`, `cmd_clusapi_get_cluster_version2()`, and `cmd_clusapi_get_quorum_resource()` query cluster-level information.
- `cmd_clusapi_create_enum()` and `cmd_clusapi_create_enumex()` create enumeration requests, with `CreateEnumEx` opening and closing a cluster handle.
- `cmd_clusapi_open_resource()`, `cmd_clusapi_online_resource()`, `cmd_clusapi_offline_resource()`, and `cmd_clusapi_get_resource_state()` operate on named resources, defaulting to `"Cluster Name"`.
- `cmd_clusapi_pause_node()` and `cmd_clusapi_resume_node()` operate on named nodes, defaulting to `"CTDB_NODE_0"`.
- `clusapi_commands[]` registers all commands as `RPC_RTYPE_WERROR` against `ndr_table_clusapi`.

## Control flow
Each command parses optional positional arguments, invokes one or more generated RPC stubs using `cli->binding_handle`, translates transport `NTSTATUS` failures to `WERROR`, checks operation-specific `WERROR` results, prints selected returned fields, and closes policy handles where required. Resource and node mutation commands first open a handle, perform the state change, and then close the handle.

## State and persistence behavior
Most commands are read-only, but `clusapi_online_resource`, `clusapi_offline_resource`, `clusapi_pause_node`, and `clusapi_resume_node` mutate remote cluster state. The module maintains no local persistent state beyond command output.

## Dependencies and integration points
This module integrates with `rpcclient` command registration, Samba DCE/RPC binding handles, generated CLUSAPI NDR client stubs, policy handles, and standard Samba error conversion helpers.

## Risks and edge cases
- State-changing commands can disrupt cluster resources or node participation if run against a production cluster.
- Some close calls ignore close failures; this is acceptable for a diagnostic tool but can hide cleanup problems.
- Argument parsing uses `sscanf`/defaults and does not validate extra arguments uniformly.
- `cmd_clusapi_get_resource_state()` checks `Status` after the state call even though the call's final operation result is stored separately, so output/error handling may miss some server failures.

## Test signals
Test with a controlled CTDB/cluster target: open/close cluster, query names/version/quorum, enumerate with different type masks, open resource, get state, and exercise online/offline or pause/resume only in disposable environments. Negative tests should cover nonexistent resources/nodes and permission-denied responses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_clusapi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_dfs.c -->
# sources/user-network-fs/samba/source3/rpcclient/cmd_dfs.c

## Purpose
`cmd_dfs.c` provides `rpcclient` commands for the DFS/NETDFS RPC interface. It checks DFS support, adds and removes DFS links, enumerates DFS namespaces, and fetches DFS entry information.

## Important APIs, types, and functions
- `cmd_dfs_version()` calls `dcerpc_dfs_GetManagerVersion()`.
- `cmd_dfs_add()` and `cmd_dfs_remove()` wrap `dcerpc_dfs_Add()` and `dcerpc_dfs_Remove()`.
- `display_dfs_info_1()`, `_2()`, `_3()`, `display_dfs_info()`, and `display_dfs_enumstruct()` print supported DFS info levels.
- `cmd_dfs_enum()` and `cmd_dfs_enumex()` prepare the correct `dfs_EnumArray*` union arm for levels 1, 2, 3, 4, 200, or 300 and call `Enum` or `EnumEx`.
- `cmd_dfs_getinfo()` calls `dcerpc_dfs_GetInfo()` and displays levels 1 to 3.
- `dfs_commands[]` registers the commands against `ndr_table_netdfs`.

## Control flow
Commands validate argument count, parse optional info levels with `atoi`, initialize the matching DFS union arm with `ZERO_STRUCT`, call the generated RPC stub, convert transport errors, and print returned entries only on successful `WERROR` results. Add/remove pass through caller-provided path, server, share, and comment values directly to the server.

## State and persistence behavior
Version, enum, enumex, and getinfo are read-only. `dfsadd` and `dfsremove` mutate the remote DFS namespace or referral configuration. There is no local persistence.

## Dependencies and integration points
The file depends on `rpcclient.h`, generated NETDFS client stubs, DFS NDR union types, and Samba NTSTATUS/WERROR conversion. It complements the server-side `RPC_NETDFS` subsystem declared in `source3/rpc_server/wscript_build`.

## Risks and edge cases
- Info levels 4, 200, and 300 can be requested for enumeration but display support only handles levels 1 to 3, so successful higher-level responses are not meaningfully printed.
- `display_dfs_enumstruct()` assumes count is the first field and reads through `info1`, which depends on compatible generated layout.
- State-changing add/remove commands perform no local validation of DFS path shape.
- `atoi` parsing silently maps invalid level strings to 0.

## Test signals
Use `dfsversion`, `dfsenum`, `dfsenumex`, and `dfsgetinfo` against a test DFS server at levels 1, 2, and 3. Mutation tests should add a disposable DFS link, verify it appears in enum/getinfo, then remove it and verify it disappears. Negative tests should include unsupported levels and invalid paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_dfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_drsuapi.c -->
# sources/user-network-fs/samba/source3/rpcclient/cmd_drsuapi.c

## Purpose
`cmd_drsuapi.c` adds `rpcclient` commands for Active Directory DRSUAPI operations: name cracking, domain-controller information queries, SPN writes, and replication change retrieval.

## Important APIs, types, and functions
- `cracknames()` builds a level-1 `DsCrackNames` request from caller-provided names and requested formats.
- `cmd_drsuapi_cracknames()` binds with `DRSUAPI_DS_BIND_GUID`, cracks one name to FQDN 1779 format, prints returned status/domain/result, and unbinds.
- `display_domain_controller_info_*()` helpers print info levels `01`, `1`, `2`, and `3`.
- `cmd_drsuapi_getdcinfo()` binds, sends `DsGetDomainControllerInfo`, and displays the returned level.
- `cmd_drsuapi_writeaccountspn()` parses `add`, `replace`, or `delete`, builds a `DsWriteAccountSpn` request, and sends it.
- `cmd_drsuapi_getncchanges()` negotiates bind extensions, resolves a default naming context when absent, chooses request level 8 or 5, calls `DsGetNCChanges` in a loop, and advances high-watermarks until `more_data` is false.

## Control flow
Every high-level command establishes a DRS bind handle and should unbind on exit. Name cracking and DC info are straightforward request/print flows. SPN writes validate the operation string and collect SPN names into an array before sending the request. `GetNCChanges` advertises many DRS extensions, inspects the server's returned extension set, derives a naming context via `cracknames()` when not supplied, obtains the binding auth session key, requests changes, handles compressed or uncompressed level-1/6 replies, and loops while the server reports more data.

## State and persistence behavior
Name cracking, DC info, and NC changes are read-only from the remote directory's perspective, although `GetNCChanges` can disclose replication data to authorized callers. `dswriteaccountspn` mutates the target AD object's service principal names. The client stores no persistent local state.

## Dependencies and integration points
The module depends on generated DRSUAPI client stubs, GUID helpers, DCE/RPC auth session key retrieval, Samba loadparm workgroup for default naming context resolution, and DRSUAPI replication structures. It is an rpcclient diagnostic/admin surface for AD replication protocols.

## Risks and edge cases
- DRSUAPI operations are security-sensitive; `GetNCChanges` can expose directory secrets when run with sufficient replication privileges, even though attribute decryption is compiled out in this file.
- Several early returns after a successful bind do not unbind, notably in default naming-context resolution failure paths.
- SPN writes can break service authentication if pointed at the wrong DN or operation.
- The code uses fixed codepage/language values in `cracknames()`.
- `GetNCChanges` has complex level/compression handling and must keep request level and high-watermark fields matched.

## Test signals
Test against a disposable AD DC with limited accounts: crack valid/invalid names, query DC info levels 1 to 3 and 01, add/replace/delete SPNs on a test object, and run `dsgetncchanges` with explicit and default naming contexts. Negative tests should cover insufficient privileges, unsupported extensions, bad DNs, and compressed reply variants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_drsuapi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_dssetup.c -->
# sources/user-network-fs/samba/source3/rpcclient/cmd_dssetup.c

## Purpose
`cmd_dssetup.c` provides a single `rpcclient` command for querying primary domain role information through the DSSETUP RPC interface.

## Important APIs, types, and functions
- `cmd_ds_dsrole_getprimarydominfo()` calls `dcerpc_dssetup_DsRoleGetPrimaryDomainInformation()` with `DS_ROLE_BASIC_INFORMATION`.
- It prints the machine role and whether Directory Service is running, including mixed/native mode when applicable.
- `ds_commands[]` registers the `LSARPC-DS` command group and `dsroledominfo` command as `RPC_RTYPE_WERROR` against `ndr_table_dssetup`.

## Control flow
The command takes no meaningful arguments, sends the DS role query through `cli->binding_handle`, converts transport errors to `WERROR`, returns server-side `werr` failures directly, and prints fields from `info.basic` on success.

## State and persistence behavior
The command is read-only and maintains no local or remote persistent state.

## Dependencies and integration points
The file depends on `rpcclient.h` and generated DSSETUP client stubs. It is part of rpcclient's LSARPC/DS administrative command surface.

## Risks and edge cases
- There is no explicit argument count validation, so extra arguments are ignored.
- Output is intentionally sparse and only covers the basic information level.
- Correctness depends on generated union layout for `union dssetup_DsRoleInfo`.

## Test signals
Run `dsroledominfo` against member servers, standalone servers, and AD DCs to verify role, DS-running, and mixed/native output. Negative tests should include servers without DSSETUP access or with denied credentials.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_dssetup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_echo.c -->
# sources/user-network-fs/samba/source3/rpcclient/cmd_echo.c

## Purpose
`cmd_echo.c` implements rpcclient commands for the test ECHO RPC interface. It is primarily a transport, marshalling, and server sanity-check tool.

## Important APIs, types, and functions
- `cmd_echo_add_one()` calls `dcerpc_echo_AddOne()` and prints the arithmetic result.
- `cmd_echo_data()` allocates input/output buffers, fills deterministic byte data, calls `EchoData`, and verifies round-trip equality.
- `cmd_echo_source_data()` calls `SourceData` and validates that the server produced the expected byte pattern.
- `cmd_echo_sink_data()` fills a buffer and sends it to `SinkData`.
- `echo_commands[]` registers `echoaddone`, `echodata`, `sinkdata`, and `sourcedata` as `RPC_RTYPE_NTSTATUS` against `ndr_table_rpcecho`.

## Control flow
Each command validates simple argument counts, parses optional sizes with `atoi`, allocates buffers with `SMB_MALLOC`, fills or checks byte patterns, invokes the generated ECHO stub, and frees buffers with `SAFE_FREE` on all exit paths.

## State and persistence behavior
All commands are stateless test calls. They allocate transient process memory and do not mutate persistent server state.

## Dependencies and integration points
The module depends on rpcclient command registration, generated rpcecho client stubs, Samba memory macros, and the server-side `RPC_RPCECHO` subsystem/build target used in selftests.

## Risks and edge cases
- Size parsing uses `atoi` into `uint32_t`; negative or very large input can become large allocations or wrap.
- Zero-size allocation behavior depends on `SMB_MALLOC`.
- The commands return `NT_STATUS_OK` for usage errors, which is common for rpcclient help behavior but weak for automation.

## Test signals
Run the commands against `rpcd_rpcecho` with zero, small, and moderate buffer sizes. Negative tests should include malformed size strings and intentionally unreachable echo service bindings. Memory checking is useful for large-size and allocation-failure paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_echo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_epmapper.c -->
# sources/user-network-fs/samba/source3/rpcclient/cmd_epmapper.c

## Purpose
`cmd_epmapper.c` implements rpcclient endpoint mapper commands. `epmmap` maps an interface and transport to endpoint towers, and `epmlookup` enumerates registered endpoint mapper entries.

## Important APIs, types, and functions
- `cmd_epmapper_map()` resolves an NDR interface name via `ndr_table_list()`, parses a transport name and optional object UUID, builds a tower from a synthetic binding, calls `dcerpc_epm_Map()`, converts returned towers back to bindings, and prints them.
- `cmd_epmapper_lookup()` repeatedly calls `dcerpc_epm_Lookup()` one entry at a time, prints object GUID, binding string, and annotation, and stops on `NO_MORE_ENTRIES`.
- `epmapper_commands[]` registers `epmmap` and `epmlookup` as `RPC_RTYPE_NTSTATUS` against `ndr_table_epmapper`.

## Control flow
`epmmap` defaults to `lsarpc` over `ncacn_np`, validates the interface and transport, builds a tower using a placeholder binding, sends the map request, checks endpoint mapper result codes, and iterates returned tower pointers. `epmlookup` maintains an `entry_handle` across loop iterations and frees a temporary context per returned entry.

## State and persistence behavior
Both commands are read-only and keep only transient local lookup state. The remote endpoint mapper's registration database is not modified.

## Dependencies and integration points
The file depends on generated EPMAPPER stubs, Samba binding parse/build helpers, NDR interface table registration, GUID helpers, and endpoint mapper status constants.

## Risks and edge cases
- `epmmap` relies on the local NDR table name matching user input; unknown names fail locally before contacting the server.
- The synthetic binding string `ncacn_np:127.0.0.1[0]` is only a tower construction seed, which can confuse future readers.
- `epmlookup` always returns `NT_STATUS_OK` after printing lookup errors, so automated callers need to parse output to detect partial failures.

## Test signals
Run `epmlookup` against Samba and Windows endpoint mappers and compare known service annotations/bindings. Run `epmmap` for `lsarpc`, `samr`, and other registered interfaces over supported transports, plus negative tests for unknown interface, unknown transport, and invalid UUID.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_epmapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_eventlog.c -->
# sources/user-network-fs/samba/source3/rpcclient/cmd_eventlog.c

## Purpose
`cmd_eventlog.c` provides rpcclient commands for Windows Event Log RPC operations: opening logs, reading records, querying record counters, writing test events, registering event sources, backing up logs, and querying log metadata.

## Important APIs, types, and functions
- `get_eventlog_handle()` opens a named log with `OpenEventLogW`.
- `cmd_eventlog_readlog()` reads records with `ReadEventLogW`, resizes the buffer on `BUFFER_TOO_SMALL`, decodes `EVENTLOGRECORD` structures with NDR, and prints debug dumps.
- `cmd_eventlog_numrecords()` and `cmd_eventlog_oldestrecord()` query counters.
- `cmd_eventlog_reportevent()` and `cmd_eventlog_reporteventsource()` write test information events.
- `cmd_eventlog_registerevsource()` registers and deregisters an event source named `rpcclient`.
- `cmd_eventlog_backuplog()` prefixes the requested path with `\\??\\` and calls `BackupEventLogW`.
- `cmd_eventlog_loginfo()` performs a two-step `GetLogInformation` buffer-size query.

## Control flow
Most commands validate arguments, open a log handle, call one or more generated eventlog RPC stubs, translate either transport or operation `NTSTATUS`, and close or deregister the handle on exit. Readlog loops backward/sequentially until the server returns end-of-file or another non-OK result, decoding records from the returned byte buffer using record length fields.

## State and persistence behavior
Read and query commands are read-only. Report-event commands append records to the remote event log, register-source touches server event-source state for the session, and backup-log writes a server-side backup file path. No local persistent state is stored.

## Dependencies and integration points
The module depends on generated EVENTLOG stubs and structures, LSA string initialization, NDR decoding of `EVENTLOGRECORD`, policy handles, and rpcclient command registration.

## Risks and edge cases
- Event writing and backup commands mutate remote state and can require administrative rights or valid server-local paths.
- `cmd_eventlog_registerevsource()` accepts a logname argument but does not use it when registering `rpcclient`.
- `cmd_eventlog_loginfo()` initially allocates a zero-length buffer and relies on server `BUFFER_TOO_SMALL` behavior.
- Readlog trusts record length fields from server data; NDR decode failure exits, but malformed lengths can still affect loop progress.
- Some error paths return without closing handles after transport errors inside read loops.

## Test signals
Against a test eventlog server, verify readlog buffer resizing, numrecords/oldestrecord output, reportevent/reporteventsource record creation, backup path handling, register/deregister behavior, and permission-denied cases. Fuzzing or malformed-server tests should target event record length parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_eventlog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_fss.c -->
# sources/user-network-fs/samba/source3/rpcclient/cmd_fss.c

## Purpose
`cmd_fss.c` implements rpcclient commands for the File Server Remote VSS Protocol (FSRVP). It checks shadow-copy support, creates and exposes shadow-copy sets, deletes exposed mappings, queries mappings, detects whether a path is shadow copied, and marks recovery complete.

## Important APIs, types, and functions
- `fss_errors[]`, `get_error_str()`, `struct fss_context_map`, `ctx_map[]`, and `map_fss_ctx_str()` translate FSRVP/HRESULT status and user context names.
- `cmd_fss_is_path_sup()` and `cmd_fss_get_sup_version()` query provider support and supported protocol versions.
- `cmd_fss_create_expose_parse()` parses context, read-only/read-write mode, and share arguments into UNC mapping requests.
- `cmd_fss_create_expose()` orchestrates `IsPathSupported`, `GetSupportedVersion`, `SetContext`, `StartShadowCopySet`, `AddToShadowCopySet`, `PrepareShadowCopySet`, `CommitShadowCopySet`, `ExposeShadowCopySet`, and `GetShareMapping`.
- `cmd_fss_abort()` aborts a shadow-copy set on mid-flow failures.
- `cmd_fss_delete()`, `cmd_fss_is_shadow_copied()`, `cmd_fss_get_mapping()`, and `cmd_fss_recov_complete()` wrap individual management calls.

## Control flow
The create/expose command is a multi-step transaction. It parses and validates the requested context and shares, extends the DCE/RPC timeout for slow VSS calls, verifies each share supports FSRVP, sets context, starts a set with a random client GUID, adds each share with random copy GUIDs, prepares and commits the set with long timeouts, exposes the set, then queries and prints each exposed mapping. If add, prepare, or commit fails after a set exists, it attempts `AbortShadowCopySet`.

## State and persistence behavior
Support/version/query commands are read-only. Create/expose creates remote shadow copies and exposed shares; delete removes exposed mappings; recovery-complete changes server-side shadow-copy-set state. Locally, only transient GUIDs and mapping arrays are stored.

## Dependencies and integration points
The module depends on generated FSRVP client stubs, HRESULT utilities, Samba GUID/time helpers, rpcclient server name fields, and DCE/RPC binding timeout control. It pairs with the source3 `RPC_FSS_AGENT` and `rpcd_fsrvp` build targets.

## Risks and edge cases
- Create/expose is a high-impact remote storage operation; partial failures can leave shadow copies or exposed mappings if abort is not reached or fails.
- Timeout units are transport-sensitive, and the code comments call out source3/source4 unit differences.
- UNC construction differs between `cli->srv_name_slash` and `cli->desthost`; inconsistent naming can affect server matching.
- `SupportedByThisProvider` is a pointer in generated output; the code assumes it is non-NULL on success.
- Context flags combine user context with `ATTR_AUTO_RECOVERY` for read-write mode, so parsing mistakes alter snapshot semantics.

## Test signals
Use a disposable FSRVP-capable server and share. Test support/version commands, create/expose for read-only and read-write contexts, multi-share sets, delete mapping, get mapping, has-shadow-copy, and recovery-complete. Failure injection should cover unsupported shares, prepare/commit timeout, abort failure, invalid GUIDs, and permission-denied responses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_fss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_iremotewinspool.c -->
# sources/user-network-fs/samba/source3/rpcclient/cmd_iremotewinspool.c

## Purpose
`cmd_iremotewinspool.c` adds rpcclient commands for the IRemoteWinspool async print RPC interface. It can open a printer asynchronously and query whether a core printer driver package is installed.

## Important APIs, types, and functions
- `cmd_iremotewinspool_async_open_printer()` builds a `winspool_AsyncOpenPrinter` request with printer name, datatype `RAW`, a devmode container, user-level client info, and an access mask defaulting to `PRINTER_ALL_ACCESS`.
- `cmd_iremotewinspool_async_core_printer_driver_installed()` builds a `winspool_AsyncCorePrinterDriverInstalled` request with a core driver GUID and architecture defaulting to XPSDRV/x64.
- Both commands call `dcerpc_binding_handle_call()` with `IREMOTEWINSPOOL_OBJECT_GUID`, `ndr_table_iremotewinspool`, and the relevant opnum.
- `iremotewinspool_commands[]` registers the commands as `RPC_RTYPE_WERROR`.

## Control flow
Open-printer validates required printer name, parses optional hex access mask, converts the IRemoteWinspool object GUID, initializes spoolss user-level info from `cli->printer_username`, fills the request, and performs a raw binding-handle call. Core-driver query validates optional arguments, converts both object and driver GUIDs, fills server/environment/version fields, performs the raw call, converts HRESULT failure to `WERROR`, and prints whether the driver is installed.

## State and persistence behavior
The commands are primarily read/query/open operations. Opening a printer creates a remote printer handle returned by the server, but this command only prints success and does not expose follow-up handle operations. No local persistent state is maintained.

## Dependencies and integration points
The file depends on generated Winspool/IRemoteWinspool NDR tables, spoolss initialization helpers, gensec/credentials headers, printer username stored in `rpc_pipe_client`, GUID helpers, HRESULT conversion, and rpcclient command registration.

## Risks and edge cases
- `AsyncOpenPrinter` requests `PRINTER_ALL_ACCESS` by default, which may fail under least-privilege accounts or be too broad for smoke tests.
- The returned printer handle is not closed by this command, so server-side cleanup relies on RPC context teardown.
- GUID parsing failures are mapped to `WERR_NOT_ENOUGH_MEMORY`, which is not semantically precise.
- The usage string for core-driver query says more than four arguments, but the command only consumes up to two user arguments after the command name.

## Test signals
Test against a print server with a known printer using default and reduced access masks, invalid printer names, valid/invalid core driver GUIDs, and alternate architecture strings. Leak/handle cleanup tests should observe server behavior after repeated async open calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_iremotewinspool.c -->
