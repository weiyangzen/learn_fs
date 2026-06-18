# Research: subset-b-009940

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/wins/wins_dns_proxy.c -->
# sources/user-network-fs/samba/source4/nbt_server/wins/wins_dns_proxy.c

## Purpose

`wins_dns_proxy.c` implements the WINS server fallback path that answers selected NetBIOS name queries by resolving the requested name through the host resolver. It is used when a WINS lookup misses and `wins dns proxy` is enabled, allowing client or server NetBIOS names to be proxied to ordinary host-name resolution.

## Important APIs, Types, and Functions

The public entry point is `nbtd_wins_dns_proxy_query()`. It allocates `struct wins_dns_proxy_state`, steals the incoming `nbt_name_packet`, copies the source socket address, creates a `resolve_context`, adds the host resolution method, and starts `resolve_name_send()`. Completion is handled by `nbtd_wins_dns_proxy_handler()`, which calls `resolve_name_recv()` and replies with `nbtd_name_query_reply()` or `nbtd_negative_name_query_reply()`.

## Control Flow

The server builds async state under the name socket, carries the packet and source address into the resolver callback, and runs the request on the nbtd service event context. A successful resolver result is wrapped in a one-element string list and sent as a positive NetBIOS query reply with zero TTL and currently fixed `nb_flags`. Allocation, address-copy, context, resolver, or resolution failures all fall through to a negative name query reply.

## State and Persistence Behavior

This file does not persist state. The only state is the talloc-owned async request state and packet ownership transferred into it. The packet lifetime must last until either the resolver callback sends a reply or setup failure sends a negative reply synchronously.

## Dependencies and Integration Points

It integrates with `nbt_server`, `winsdb.h`, `winsserver.h`, Samba composite async contexts, `resolve_context`, `resolve_name_send/recv`, socket address helpers, and the service task event loop. It is called by `nbtd_winsserver_query()` after an LDB WINS miss for `NBT_NAME_CLIENT` and `NBT_NAME_SERVER` names.

## Risks and Edge Cases

The reply uses `nb_flags = 0` with a TODO, so node/group semantics from DNS are not represented. Only the host resolver method is added, which intentionally avoids recursive WINS behavior but makes behavior depend on local resolver configuration. A setup failure after stealing the packet into `s` still replies using the original `packet` pointer; the talloc hierarchy keeps the object alive, but this ownership pattern is worth care during future edits.

## Test Signals

Useful tests include WINS misses with DNS proxy disabled and enabled, successful host resolution, resolver timeout/failure, allocation-failure paths, and verifying that only client/server NetBIOS name types use DNS proxy. Packet lifetime can be stressed with async resolver delays.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/wins/wins_dns_proxy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/wins/wins_hook.c -->
# sources/user-network-fs/samba/source4/nbt_server/wins/wins_hook.c

## Purpose

`wins_hook.c` implements the optional WINS hook script feature. After WINS database add, modify, or delete operations commit, this code builds a shell command describing the record change and runs the configured script asynchronously in a child process.

## Important APIs, Types, and Functions

`wins_hook()` is the public function. `wins_hook_action_string()` maps `WINS_HOOK_ADD`, `WINS_HOOK_MODIFY`, and `WINS_HOOK_DELETE` to the command action words `add`, `refresh`, and `delete`. The hook command includes the script path, action, NetBIOS name, name type, expire time, and each stored address from `rec->addresses`. It calls `winsdb_addr_list_length()` to downgrade a modify with no addresses into delete semantics.

## Control Flow

The function returns immediately when no script is configured. It validates `rec->name->name` so only alphanumeric characters and `._-` are allowed, then allocates a temporary talloc context, formats the command, appends addresses, ignores `SIGCHLD`, forks, and executes `/bin/sh -c <cmd>` in the child. The parent frees the temporary context and does not wait for the child.

## State and Persistence Behavior

No Samba database state is persisted here. The function affects process state by setting `SIGCHLD` to `SIG_IGN`, which is global to the process. Child execution is fire-and-forget, and hook failures are not reported back to the WINS transaction because calls happen after database commit in `winsdb_add()`, `winsdb_modify()`, and `winsdb_delete()`.

## Dependencies and Integration Points

It depends on WINS DB record structures, talloc, libc process APIs, signal handling, and filesystem/system headers. Its integration point is the WINS DB write layer, which passes `h->hook_script` from loadparm `lpcfg_wins_hook()`.

## Risks and Edge Cases

The script path is injected directly into a shell command and is not shell-escaped; configuration must be trusted. The record name is validated, but address strings and script path are not escaped. Setting `SIGCHLD` process-wide can affect unrelated server code. The child does not close inherited file descriptors, noted by a TODO. The parent ignores script exit status, so operational failure is only visible through external script-side logging.

## Test Signals

Tests should cover disabled hooks, add/modify/delete command strings, modify-with-empty-address conversion to delete, invalid names suppressing execution, fork failure behavior, and hook argument handling for multiple addresses. Process-level tests should ensure no zombies and inspect side effects of `SIGCHLD` changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/wins/wins_hook.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/wins/wins_ldb.c -->
# sources/user-network-fs/samba/source4/nbt_server/wins/wins_ldb.c

## Purpose

`wins_ldb.c` defines the `wins_ldb` LDB module used by `wins.ldb`. Its current role is to attach a `winsdb_handle` to the LDB context and provide a verification hook for WINS records before add/modify operations reach storage.

## Important APIs, Types, and Functions

The module entry point is `ldb_wins_ldb_module_init()`, which registers `ldb_wins_ldb_module_ops`. `wins_ldb_init()` creates a `struct winsdb_handle` with caller `WINSDB_HANDLE_CALLER_ADMIN` and a local owner address. `wins_ldb_verify()` intercepts `LDB_ADD` and `LDB_MODIFY`, retrieves the opaque `winsdb_handle`, skips special DNs, and dispatches based on `h->caller`.

## Control Flow

Initialization resolves `winsdb:local_owner` from loadparm; if absent, it loads interfaces and uses the first IPv4 address, falling back to `0.0.0.0`. It stores the handle as LDB opaque `winsdb_handle`. During add/modify, trusted callers `NBTD` and `WREPL` pass straight through; admin callers currently log a TODO warning and also pass through. Missing opaque state or unknown caller returns an LDB error.

## State and Persistence Behavior

The module stores a talloc-owned `winsdb_handle` in LDB opaque state. It does not directly persist WINS records, but it participates in every add/modify pipeline once listed in the `@MODULES` record of `wins.ldb`. The handle contains `local_owner`, caller identity, and the LDB context pointer.

## Dependencies and Integration Points

It depends on LDB module APIs, `winsdb.h`, Samba loadparm, interface discovery, and network helpers. `winsdb_connect()` ensures this module is present in `@MODULES` and reopens the database so the module is active.

## Risks and Edge Cases

Actual admin verification is still a TODO, so malformed admin writes may be accepted until lower layers detect corruption. If no loadparm opaque is present, `lpcfg_parm_string()` and interface loading assumptions can fail indirectly. The module trusts NBTD and WREPL callers, so their record construction invariants remain critical.

## Test Signals

Good tests include module initialization with explicit owner, interface-derived owner, and no-interface fallback; add/modify with each caller type; special DN bypass; missing opaque handle failure; and malformed admin records once verification is implemented.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/wins/wins_ldb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/wins/winsclient.c -->
# sources/user-network-fs/samba/source4/nbt_server/wins/winsclient.c

## Purpose

`winsclient.c` implements Samba nbtd's WINS client behavior for registering interface names with configured WINS servers and periodically refreshing those registrations. It is separate from the local WINS server path and acts on `nbtd_iface_name` records owned by local interfaces.

## Important APIs, Types, and Functions

The exported API is `nbtd_winsclient_register()`. Internal helpers include `wins_socket()` for selecting the primary name socket, `nbtd_wins_start_refresh_timer()`, `nbtd_wins_refresh()`, `nbtd_wins_refresh_handler()`, `nbtd_wins_register_handler()`, and `nbtd_wins_register_retry()`. State structs wrap `struct nbt_name_register_wins` and `struct nbt_name_refresh_wins` requests.

## Control Flow

Registration builds a WINS register request from the interface name, configured WINS server list, NBT port, local address list, flags, and TTL, then starts `nbt_name_register_wins_send()`. Timeout schedules a retry after `nbtd:wins_retry`; protocol errors mark the name conflicting or log failure; success marks the name active, stores the responding WINS server, records current time, and schedules refresh. Refresh uses the remembered WINS server, refreshes at `min(nbtd:max_refresh_time, ttl/2)`, and on timeout restarts registration from scratch.

## State and Persistence Behavior

State is in memory on `struct nbtd_iface_name`: `nb_flags`, `wins_server`, `registration_time`, and timers. There is no persistent database update in this file. The WINS server string returned by the client library is talloc-moved into the interface name after carefully stealing any old string into the temporary request state.

## Dependencies and Integration Points

It depends on nbtd interface structures, `winsserver.h`, tevent timers, generated NBT request structures, `cli-nbt`, service task event context, loadparm WINS configuration, and `nbtd_address_list()`. Startup and interface registration code invoke this when local names need WINS registration.

## Risks and Edge Cases

Timeout handling differs between register and refresh: register retries later, refresh immediately starts registration over. Non-timeout errors do not retry, which can leave a name inactive or stale until external registration is triggered. If no local addresses are available, registration and refresh silently free state. The use of the first nbtd interface socket assumes that primary interface routing is acceptable for all WINS client requests.

## Test Signals

Tests should cover successful registration, timeout retry, refresh success, refresh timeout re-registration, rejected rcode marking conflict, missing address list, multiple configured WINS servers, and refresh timer calculation with `nbtd:max_refresh_time` and TTL boundaries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/wins/winsclient.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/wins/winsdb.c -->
# sources/user-network-fs/samba/source4/nbt_server/wins/winsdb.c

## Purpose

`winsdb.c` is the core WINS database access layer for Samba's source4 nbtd and WREPL paths. It maps NetBIOS names to LDB DNs, decodes and encodes WINS record attributes, manages version allocation, updates address lists, applies expiration semantics, and performs transactional add, modify, delete, and connect operations for `wins.ldb`.

## Important APIs, Types, and Functions

Public APIs include `winsdb_connect()`, `winsdb_get_maxVersion()`, `winsdb_set_maxVersion()`, `winsdb_lookup()`, `winsdb_record()`, `winsdb_add()`, `winsdb_modify()`, `winsdb_delete()`, and address-list helpers `winsdb_addr_list_make()`, `winsdb_addr_list_add()`, `winsdb_addr_list_remove()`, `winsdb_addr_list_check()`, `winsdb_addr_list_length()`, and `winsdb_addr_string_list()`. Important internals are `winsdb_dn()`, `winsdb_nbt_name()`, `winsdb_addr_decode()`, `ldb_msg_add_winsdb_addr()`, `winsdb_message()`, and `winsdb_check_or_add_module_list()`.

## Control Flow

Lookup computes an LDB DN from the `nbt_name`, searches the base DN, and converts the returned message with `winsdb_record()`. Record decoding reconstructs the name from DN components, validates name/scope length, reads record metadata, decodes each `address` value, filters locally owned expired active addresses, and releases active records with no remaining active addresses. Add and modify start LDB transactions, optionally allocate a new version with `winsdb_set_maxVersion(h, 0)`, optionally take ownership, encode the record to an LDB message, and commit. Delete removes the DN in a transaction. After successful commits, WINS hooks are called.

## State and Persistence Behavior

Persistent state is stored in `wins.ldb` under DNs composed from scope, name, and type. `CN=VERSION` stores `maxVersion`; `@MODULES` stores the `wins_ldb` module list. Dynamic addresses are stored as strings containing address, owner, and expire time, while static records store only the address string and receive maximum expiration during decode. Transactions protect version and record updates, although `winsdb_set_maxVersion()` starts its own transaction and is called inside add/modify transactions.

## Dependencies and Integration Points

The file depends on LDB, LDB wrap, generated NBT/WREPL enums, talloc, loadparm, interface discovery, time helpers, string conversion helpers, and talloc-aware sorting. It is used by `winsserver.c`, WREPL code, the `wins_ldb` module, and hook support. `winsdb_connect()` creates the database handle, obtains `wins_hook`, configures `LDB_FLG_NOSYNC` when requested, ensures the module list exists, reopens the database if needed, and sets the `winsdb_handle` opaque.

## Risks and Edge Cases

Address records are capped at 25, with registration replacing the oldest replica first and replication updates ignored at capacity. `winsdb_addr_decode()` mutates the LDB value buffer by inserting NULs at separators. Expiration is applied during decode for locally owned addresses rather than by a separate cleanup pass. `winsdb_set_maxVersion()` has nested transaction implications when called from add/modify. Corrupt DB records produce `NT_STATUS_INTERNAL_DB_CORRUPTION` and debug output. Static records override expiration, and unique records with multiple addresses are rewritten as multihomed during message encoding.

## Test Signals

Strong tests include DN round trips with scope/name/type, old address-string compatibility, dynamic address encode/decode, static records, address cap and sorting rules, expiration of locally owned versus replica SGROUP addresses, unique-to-MHOMED conversion, maxVersion allocation and monotonic updates, module-list insertion and reopen, hook invocation after commit, and transaction rollback on add/modify/delete failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/wins/winsdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/wins/winsdb.h -->
# sources/user-network-fs/samba/source4/nbt_server/wins/winsdb.h

## Purpose

`winsdb.h` defines the public data structures, flags, caller identities, hook actions, and generated prototypes for Samba's WINS database layer. It is the shared contract between nbtd WINS server/client code, WREPL paths, the LDB module, and hook integration.

## Important APIs, Types, and Functions

Important types are `struct winsdb_addr`, `struct winsdb_record`, `enum winsdb_handle_caller`, `struct winsdb_handle`, and `enum wins_hook_action`. Flags `WINSDB_FLAG_ALLOC_VERSION` and `WINSDB_FLAG_TAKE_OWNERSHIP` control write behavior. The header includes `winsdb_proto.h`, which provides prototypes for the implementation functions in `winsdb.c` and `wins_hook.c`.

## Control Flow

The header has no executable control flow, but it defines how callers construct records before database writes: fill a `winsdb_record`, pass ownership/version flags, and let the implementation allocate version IDs or local owner when needed. Caller identity on `winsdb_handle` feeds into the `wins_ldb` module verification path.

## State and Persistence Behavior

`struct winsdb_record` mirrors persistent LDB WINS records: name, WREPL type/state/node, static bit, expiration, version, owner, registered-by debug field, and a NULL-terminated list of `winsdb_addr` entries. `struct winsdb_handle` carries the persistent LDB context, caller class, local owner address, and hook script path.

## Dependencies and Integration Points

It relies on NBT and WREPL generated types already included by users, LDB forward declarations, tevent forward declarations, and source4 nbtd code. It is included by WINS DB implementation, server logic, WACK logic, DNS proxy, and the LDB module.

## Risks and Edge Cases

The header exposes raw struct fields rather than opaque accessors, so callers must maintain invariants such as NULL-terminated address lists, valid WREPL state/type combinations, address count limits, and correct talloc ownership. The caller enum is security-relevant because module verification policy changes based on it.

## Test Signals

Compile-time signals are generated prototype freshness and all WINS users building against the same structure definitions. Runtime tests should validate that records assembled by nbtd and WREPL satisfy the invariants consumed by `winsdb_message()` and `winsdb_record()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/wins/winsdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/wins/winsserver.c -->
# sources/user-network-fs/samba/source4/nbt_server/wins/winsserver.c

## Purpose

`winsserver.c` implements the core WINS server request path for NetBIOS name registration, refresh, query, release, WACK conflict challenges, and server startup. It translates NBT packets into WINS DB operations and Windows-compatible registration/query/release behavior.

## Important APIs, Types, and Functions

Public entry points are `wins_server_ttl()`, `nbtd_winsserver_request()`, and `nbtd_winsserver_init()`. Key helpers include `wrepl_type()`, `wins_register_new()`, `wins_update_ttl()`, `wins_sgroup_merge()`, `wins_register_wack()`, `wins_wack_allow()`, `wins_wack_deny()`, `wack_wins_challenge_handler()`, `nbtd_winsserver_register()`, `nbtd_winsserver_query()`, `nbtd_winsserver_release()`, and `nbtd_wins_randomize1Clist()`.

## Control Flow

Request dispatch ignores broadcasts and disabled WINS state, then handles query, register/refresh/multihome-register, and release opcodes. Registration validates special NetBIOS names, checks duplicate WACKs, looks up existing records, creates new records, refreshes TTLs, merges special groups, rejects incompatible static or group records, or starts WACK challenges for conflicting unique/multihomed owners. Query rejects master-browser 0x1D, optionally prepends 0x1B to 0x1C results, returns group wildcard addresses, randomizes 0x1C lists when configured, falls back to DNS proxy for eligible misses, and sends positive or negative replies. Release verifies ownership by source address, mutates active/released/tombstone state, updates expiration and ownership for replication cases, and always sends a positive release reply to match Windows behavior.

## State and Persistence Behavior

Persistent state is in `wins.ldb` via `winsdb_add()`, `winsdb_modify()`, and `winsdb_delete()`. In-memory WACK state is linked on `iface->wack_queue` and removed by destructor. Startup stores WINS configuration intervals and a connected `winsdb_handle` in `nbtsrv->winssrv`, choosing the local owner from `winsdb:local_owner` or the first IPv4 interface.

## Dependencies and Integration Points

It depends on nbtd packet/socket helpers, WINS DB APIs, WACK helper `wins_challenge_send()`, LDB, loadparm, interface utilities, resolver/DNS proxy, talloc list helpers, and generated NBT/WREPL constants. It registers the IRPC name `wins_server` at initialization and is built into the `NBTD_WINS` subsystem.

## Risks and Edge Cases

The registration branch contains a duplicated `new_type == WREPL_TYPE_GROUP` condition where the second check likely intended `SGROUP`. `nbtd_winsserver_init()` reads `" tombstone_timeout"` with a leading space in the parameter name, which may prevent intended config override. WACK allow deletes and re-adds records if the old owner no longer holds the name; races are guarded by version/owner re-lookup but remain subtle. Release only checks source address, with a TODO about packet additional address verification. Address iteration while removing entries must be handled carefully.

## Test Signals

Tests should cover name-type validation for 0x1B/0x1C/0x1D/0x1E, static record handling, unique conflicts and WACK allow/deny, duplicate WACK suppression, multihomed and special group registration, TTL clamping, query group and 1C behavior, DNS proxy fallback, release from owner versus non-owner, tombstone ownership transitions, and startup with/without WINS enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/wins/winsserver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/wins/winsserver.h -->
# sources/user-network-fs/samba/source4/nbt_server/wins/winsserver.h

## Purpose

`winsserver.h` declares the WINS server runtime structure and the WACK/challenge IO contract used by WINS server and WREPL integration. It also includes generated `winsserver_proto.h` prototypes.

## Important APIs, Types, and Functions

`struct wins_server` holds the connected `winsdb_handle` and timing configuration for min/max renew interval, tombstone interval, and tombstone timeout. `struct wins_challenge_io` describes async name-query challenges to current owners: input server, NBT port, event context, name, and owner addresses; output address list returned by the challenged owner.

## Control Flow

The header has no executable flow. `winsserver.c` fills `wins_server` during nbtd startup and passes `wins_challenge_io` to `wins_challenge_send()` in `winswack.c`. WREPL IRPC proxy code also uses this IO model to request challenges through nbtd.

## State and Persistence Behavior

`wins_server` points at persistent WINS DB state through `wins_db` and holds in-memory configuration copied from loadparm. `wins_challenge_io` is request-scoped and talloc-owned by callers; outputs are stolen by receivers during `wins_challenge_recv()`.

## Dependencies and Integration Points

It depends on `winsdb_handle`, nbtd server declarations, tevent context, and NBT name structures. The generated prototype include connects server, client, WACK, and DNS proxy source files.

## Risks and Edge Cases

Because the config struct is simple public state, all users must agree on units and ownership. Challenge IO assumes `num_addresses` and `addresses` are consistent and non-empty; callers must validate before starting async work.

## Test Signals

Build signals include generated prototype correctness for `NBTD_WINS`. Runtime signals are WINS startup storing expected intervals and WACK challenge send/recv preserving address arrays across async callbacks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/wins/winsserver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/wins/winswack.c -->
# sources/user-network-fs/samba/source4/nbt_server/wins/winswack.c

## Purpose

`winswack.c` implements secure WINS challenge and release-demand helpers. WINS registration conflict handling uses challenges to ask existing owners whether they still hold a name, and WREPL uses IRPC proxy wrappers so NBT server sockets on port 137 can receive replies from Windows servers that ignore the source port.

## Important APIs, Types, and Functions

Public functions are `wins_challenge_send()`, `wins_challenge_recv()`, `nbtd_proxy_wins_challenge()`, and `nbtd_proxy_wins_release_demand()`. Internal async helpers include `wins_challenge_handler()`, `wins_release_demand_send()`, `wins_release_demand_recv()`, `wins_release_demand_handler()`, `proxy_wins_challenge_handler()`, and `proxy_wins_release_demand_handler()`.

## Control Flow

`wins_challenge_send()` builds a composite context and sends an NBT name query to the first current-owner address using the interface chosen by `nbtd_find_request_iface()`. Timeout advances to the next address and retries until an owner replies or the address list is exhausted. `wins_challenge_recv()` returns the owner-reported address list on success. Release demand follows a similar address iteration model with NBT release packets and timeout/retry behavior tuned for one versus multiple addresses. IRPC handlers translate generated proxy request arrays into local IO structures, start the async operation, defer the IRPC reply, and send the result in the callback.

## State and Persistence Behavior

No persistent database state is changed directly. State is held in composite contexts, `wins_challenge_state`, `wins_release_demand_state`, and IRPC proxy state. Successful challenge outputs transfer address ownership to the caller via talloc.

## Dependencies and Integration Points

It depends on nbtd interface lookup, NBT name query/release client APIs, composite async helpers, loadparm NBT port, service task event context, generated IRPC structures, and messaging via `irpc_send_reply()`. `winsserver.c` uses the challenge path for WACK conflict decisions; WREPL code uses proxy calls.

## Risks and Edge Cases

The challenge path assumes at least one address; callers must ensure non-empty address arrays. Timeouts advance sequentially, so large address lists increase WACK latency. Some failures map to internal errors rather than trying alternate routing. IRPC wrappers contain TODOs around PIDL inline IPv4 arrays and manually steal address strings, making ownership sensitive.

## Test Signals

Tests should cover first-address success, timeout failover, all-address timeout, interface lookup failure, challenge reply address propagation, release-demand timeout profiles, IRPC deferred replies, zero/invalid address input, and WINS registration conflict behavior that consumes these results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/wins/winswack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/wscript_build -->
# sources/user-network-fs/samba/source4/nbt_server/wscript_build

## Purpose

`source4/nbt_server/wscript_build` declares the waf build targets for the source4 NetBIOS-over-TCP server, including WINS database support, WINS server/client logic, datagram handlers, the main NBT server subsystem, and the service module.

## Important APIs, Types, and Functions

The script uses `bld.SAMBA_SUBSYSTEM()` and `bld.SAMBA_MODULE()`. Key targets are `WINSDB`, `ldb_wins_ldb`, `NBTD_WINS`, `NBTD_DGRAM`, `NBT_SERVER`, and `service_nbtd`. Autoproto outputs include `wins/winsdb_proto.h`, `wins/winsserver_proto.h`, `dgram/proto.h`, and `nbt_server_proto.h`.

## Control Flow

At build time, WINS DB sources `winsdb.c` and `wins_hook.c` form `WINSDB`; `wins_ldb.c` forms an LDB module; WINS server/client/WACK/DNS proxy sources form `NBTD_WINS`; datagram sources form `NBTD_DGRAM`; interface/register/query/nodestatus/defense/packet/IRPC sources form `NBT_SERVER`; and `nbt_server.c` is registered as `service_nbtd`. All targets are gated by `bld.AD_DC_BUILD_IS_ENABLED()`.

## State and Persistence Behavior

The file persists build graph metadata and generated prototype headers. It does not run runtime state, but its dependency graph determines which WINS/NBT features are linked into AD DC builds.

## Dependencies and Integration Points

Dependencies include `ldb`, `ldbsamba`, `netif`, `samba-hostconfig`, `samba-util`, `cli-nbt`, `WINSDB`, `LIBCLI_DGRAM`, `DSDB_MODULE_HELPERS`, `service`, `LIBNMB`, and `process_model`. The LDB module is external to the `ldb` subsystem while `service_nbtd` integrates with Samba's service framework.

## Risks and Edge Cases

Build gating means non-AD-DC builds may not compile these sources, so changes require AD DC matrix coverage. Autoproto freshness is required because C files include generated headers. Dependency drift can surface as missing symbols in service or LDB-module linkage.

## Test Signals

Signals include a successful AD DC build, generated prototype headers matching source exports, `ldb_wins_ldb` module loadability, and `service_nbtd` starting with `NBTD_WINS` and `NBTD_DGRAM` linked.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntp_signd/ntp_signd.c -->
# sources/user-network-fs/samba/source4/ntp_signd/ntp_signd.c

## Purpose

`ntp_signd.c` implements Samba's NTP signing daemon service. It listens on a Unix-domain socket, accepts length-prefixed NTP signing requests, looks up the requested trust account in SAMDB, and returns a signed NTP packet using the account's NT hash.

## Important APIs, Types, and Functions

The service registration entry point is `server_service_ntp_signd_init()`, which registers `ntp_signd_task_init()`. Connection handling uses `ntp_signd_accept()`, `ntp_signd_call_loop()`, `ntp_signd_call_writev_done()`, and `ntp_signd_terminate_connection()`. Packet processing is in `ntp_signd_process()`, with `signing_failure()` creating protocol failure replies. Runtime structs are `struct ntp_signd_server`, `struct ntp_signd_connection`, and `struct ntp_signd_call`.

## Control Flow

Task init creates the strict socket directory, opens SAMDB with `system_session()`, constructs `<ntp_signd_socket_directory>/socket`, and binds a stream service. Accept converts the existing socket to a tstream, creates a send queue, and starts reading 4-byte length-prefixed PDUs. Each call strips the length header, NDR-decodes `sign_request`, rejects unsupported operations or protocol versions with a signing-failure reply, constructs a SID from the domain SID plus `key_id & 0x7fffffff`, searches SAMDB for a user object, verifies it is enabled and a trust account, obtains `unicodePwd`, appends key ID and MD5(NT hash || packet) to the packet, NDR-encodes `signed_reply`, queues the write, and immediately starts the next read.

## State and Persistence Behavior

Persistent data is read from SAMDB but not modified. Per-service state holds the task and SAMDB handle. Per-connection state holds stream, send queue, and owning service pointer. Each request allocates input/output blobs and iovecs under `ntp_signd_call`, freed after write completion.

## Dependencies and Integration Points

It integrates with Samba service/task/stream infrastructure, tstream, generated `ndr_ntp_signd`, SAMDB and DSDB search helpers, auth/system sessions, SID utilities, GnuTLS hash helpers, loadparm socket directory/options, and Unix permissions. The build script links it with `samdb`, NDR, tsocket, GnuTLS helpers, and service infrastructure.

## Risks and Edge Cases

The signing algorithm uses MD5 because it matches the protocol, so callers must not treat it as a general modern signature primitive. Access control relies on Unix socket directory permissions and account-type checks. Unsupported protocol operations return protocol failure replies, while disabled/non-trust accounts return access denied and terminate the connection through the caller loop. The code adjusts `call->in.data` past the header without preserving the original pointer, which is acceptable for request scope but should not be reused for freeing. Long or malformed PDUs depend on tstream framing limits outside this file.

## Test Signals

Tests should cover socket directory creation and permissions, valid trust-account signing, unknown SID, duplicate SID search results, disabled account, non-trust account, missing `unicodePwd`, unsupported op/version, malformed NDR, multiple requests on one connection, write failure termination, and exact signed packet layout including key ID and 16-byte digest.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntp_signd/ntp_signd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntp_signd/wscript_build -->
# sources/user-network-fs/samba/source4/ntp_signd/wscript_build

## Purpose

`source4/ntp_signd/wscript_build` declares the Samba service module for the NTP signing daemon.

## Important APIs, Types, and Functions

It uses `bld.SAMBA_MODULE()` to build `service_ntp_signd` from `ntp_signd.c`, in subsystem `service`, with init function `server_service_ntp_signd_init`.

## Control Flow

At build time, the target is emitted only when `bld.AD_DC_BUILD_IS_ENABLED()` is true. Runtime service registration is delegated to the init function in `ntp_signd.c`.

## State and Persistence Behavior

The script only persists build metadata. It controls whether the NTP signing service is part of the AD DC build graph and which libraries it links against.

## Dependencies and Integration Points

Dependencies are `samdb`, `NDR_NTP_SIGND`, `LIBTSOCKET`, `LIBSAMBA_TSOCKET`, `GNUTLS_HELPERS`, and `samdb-common`. The module is non-internal so the service framework can load/register it.

## Risks and Edge Cases

Build coverage is AD-DC gated. Missing or misordered dependencies would surface as link failures for SAMDB, generated NDR, tstream, or GnuTLS hash helpers.

## Test Signals

Signals include successful AD DC build, service module load, and startup of `ntp_signd` with generated `server_service_ntp_signd_init` symbol resolved.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntp_signd/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/cifs/vfs_cifs.c -->
# sources/user-network-fs/samba/source4/ntvfs/cifs/vfs_cifs.c

## Purpose

`vfs_cifs.c` implements the source4 NTVFS `cifs` backend, a CIFS-on-CIFS proxy filesystem. It accepts NTVFS file-share operations from Samba clients and forwards them to an upstream SMB/CIFS server using the raw SMB client library.

## Important APIs, Types, and Functions

The module init entry point is `ntvfs_cifs_init()`. Runtime state is `struct cvfs_private`, `struct cvfs_file`, and `struct async_info`. Important operations include `cvfs_connect()`, `cvfs_disconnect()`, `cvfs_open()`, `cvfs_close()`, `cvfs_read()`, `cvfs_write()`, `cvfs_lock()`, `cvfs_notify()`, `cvfs_cancel()`, path/file info operations, directory/search operations, trans/trans2, and helper callbacks such as `async_open()`, `async_simple()`, and `oplock_handler()`.

## Control Flow

Tree connect parses the requested share name, reads share options such as `cifs:server`, credentials, machine-account, S4U2Proxy, remote share, generic mapping, and trans2 mapping, then establishes an upstream SMB connection with `smb_composite_connect_send/recv()`. Operations set the upstream session PID, verify the transport is connected, translate NTVFS handles to upstream fnums, and either call synchronous `smb_raw_*` functions or, when allowed, start async raw requests and complete through callbacks that update `req->async_states`. Open creates an NTVFS handle and associates it with the upstream fnum; close removes it from the local list. Oplock breaks from upstream are translated to `ntvfs_send_oplock_break()`.

## State and Persistence Behavior

There is no local filesystem persistence. State tracks the upstream tree, transport, pending async requests, open fnum-to-NTVFS handle mappings, and configuration booleans. Disconnect destroys pending requests and backend state. File contents, metadata, locks, and notifies are persisted or managed by the upstream server.

## Dependencies and Integration Points

It depends on raw SMB client APIs, SMB composite connect, credentials/auth, Kerberos S4U2Proxy support, NTVFS operation registration, loadparm/share options, resolve context, dlink list helpers, and smbXcli connection checks. It registers as an `NTVFS_DISK` backend named `cifs`.

## Risks and Edge Cases

Close removes a file mapping before the upstream close completes, with a comment questioning whether that is ideal on failure. Many operations rely on macros mutating caller IO structures to replace NTVFS handles with fnums. `cvfs_logoff()` is a no-op because the backend cannot implement it correctly. `cvfs_copy()` and `cvfs_lpq()` are unsupported; `cvfs_trans()` is denied; `cvfs_trans2()` may be not implemented when mapping is enabled. Async cancellation only works when a matching pending request exists. Upstream disconnect marks the NTVFS request for close and returns disconnected.

## Test Signals

Tests should cover connect options for explicit credentials, machine account, delegated credentials, and S4U2Proxy; open/read/write/close handle mapping; upstream disconnect; async completion and cancellation; oplock break forwarding; notify with no timeout; generic open/read/write/lock/close mapping; unsupported copy/lpq/trans behavior; and close failure effects on local handle state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/cifs/vfs_cifs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/common/brlock.c -->
# sources/user-network-fs/samba/source4/ntvfs/common/brlock.c

## Purpose

`brlock.c` is the backend-dispatch wrapper for source4 NTVFS byte-range locking. It exposes the public brlock API while delegating implementation to a selected `struct brlock_ops`, defaulting to the TDB backend.

## Important APIs, Types, and Functions

Public functions are `brlock_set_ops()`, `brlock_init()`, `brlock_create_handle()`, `brlock_lock()`, `brlock_unlock()`, `brlock_remove_pending()`, `brlock_locktest()`, `brlock_close()`, and `brlock_count()`. The global static `ops` points at the active backend.

## Control Flow

`brlock_init()` initializes the default TDB ops via `brl_tdb_init_ops()` if no backend has been installed, then calls `ops->brl_init()`. All other functions are thin pass-throughs to the corresponding backend method.

## State and Persistence Behavior

The only state in this file is the process-global backend ops pointer. Persistent lock state is owned by the backend, normally `brlock_tdb.c` using a temporary cluster DB.

## Dependencies and Integration Points

It depends on `ntvfs_common.h`, messaging, IRPC, cluster helpers, and loadparm types through the backend interface. NTVFS disk backends use this API to create lock contexts and handles for open files.

## Risks and Edge Cases

The process-global `ops` is mutable and not synchronized; test or alternate backend injection must happen before concurrent use. There are no NULL checks in pass-through calls after initialization, so backend installation must be complete and correct.

## Test Signals

Tests should verify default TDB backend selection, alternate backend injection through `brlock_set_ops()`, and that public API calls dispatch exactly once to the expected ops.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/common/brlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/common/brlock.h -->
# sources/user-network-fs/samba/source4/ntvfs/common/brlock.h

## Purpose

`brlock.h` defines the backend operations interface for source4 NTVFS byte-range locking and declares backend selection helpers.

## Important APIs, Types, and Functions

The central type is `struct brlock_ops`, containing function pointers for init, handle creation, lock, unlock, pending-lock removal, lock tests, close cleanup, and count. It declares `brlock_set_ops()` and `brl_tdb_init_ops()`.

## Control Flow

The header has no runtime flow, but it defines the dispatch contract implemented by `brlock_tdb.c` and consumed by `brlock.c`.

## State and Persistence Behavior

The interface abstracts backend state in `struct brl_context` and `struct brl_handle`. Callers treat those as opaque and rely on the backend to persist or remove byte-range lock records.

## Dependencies and Integration Points

It includes `libcli/libcli.h` for `NTSTATUS` and lock-type declarations, and is included through `ntvfs_common.h` by NTVFS common users.

## Risks and Edge Cases

ABI is internal but pointer signatures must remain synchronized with wrappers and backends. The interface exposes raw `void *notify_ptr` for pending-lock notifications, so callers and backends must agree on lifetime and messaging semantics.

## Test Signals

Compile-time tests should catch signature drift. Runtime tests should exercise every ops slot through the public wrapper and verify pending notification pointer round trips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/common/brlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/common/brlock_tdb.c -->
# sources/user-network-fs/samba/source4/ntvfs/common/brlock_tdb.c

## Purpose

`brlock_tdb.c` implements the TDB-backed byte-range locking service for source4 NTVFS. It stores locks in a cluster-capable temporary DB keyed by a file identity blob and emulates Windows/NT byte-range locking semantics, including pending locks and retry notifications.

## Important APIs, Types, and Functions

Backend ops are registered by `brl_tdb_init_ops()`. Internal types include `struct brl_context`, `struct lock_context`, `struct lock_struct`, and `struct brl_handle`. Important functions include `brl_tdb_init()`, `brl_tdb_create_handle()`, `brl_tdb_lock()`, `brl_tdb_unlock()`, `brl_tdb_remove_pending()`, `brl_tdb_locktest()`, `brl_tdb_close()`, `brl_tdb_count()`, `brl_tdb_conflict()`, `brl_tdb_conflict_other()`, `brl_tdb_overlap()`, and notification helpers.

## Control Flow

Init opens the `brlock` cluster temp DB. Each lock operation fetches and locks the file-key record, validates the range, builds a `lock_struct`, checks conflicts against existing serialized locks, appends on success, and stores the updated array. Pending locks first attempt the real read/write lock while holding the record lock to avoid a race, then store a pending entry if the real lock cannot be granted. Unlock finds an exact matching write lock first, then any non-pending matching lock, removes it, notifies overlapping pending locks, and stores or deletes the record. Close removes all locks for the handle and notifies pending holders.

## State and Persistence Behavior

Persistent runtime state is in `brlock.tdb` records whose values are linear arrays of `struct lock_struct`. Handles cache the file key, NTVFS handle, and last failed lock to reproduce Windows error-code behavior. Pending locks store `notify_ptr` and target server ID for `MSG_BRL_RETRY` imessaging notifications.

## Dependencies and Integration Points

It depends on dbwrap, cluster DB helpers, imessaging, NTVFS handles, generated lock enums, and loadparm. NTVFS file backends use it through `brlock.c` for SMB lock/unlock/read/write conflict checks.

## Risks and Edge Cases

The record value stores raw structs, including pointers, so it is suited to Samba runtime temp DB use and same-binary interpretation, not durable cross-version storage. Stale process detection is a TODO, so locks from dead servers may persist until cleanup semantics elsewhere handle them. `brl_tdb_notify_all()` checks `locks->lock_type` instead of `locks[i].lock_type`, which looks suspicious. Error-code compatibility for repeated failed locks is intentionally subtle. Wrapped 64-bit lock ranges are rejected.

## Test Signals

Tests should cover read/read sharing, write conflicts, same-context exceptions, invalid wrapped ranges, pending lock retry notification, unlock exact-match rules, close cleanup, count, SMB1 versus SMB2 error-code differences, high-offset conflict behavior, and dead/stale lock scenarios in clustered setups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/common/brlock_tdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/common/init.c -->
# sources/user-network-fs/samba/source4/ntvfs/common/init.c

## Purpose

`init.c` provides the initialization entry point for the NTVFS common support subsystem.

## Important APIs, Types, and Functions

The only exported function is `ntvfs_common_init()`, which calls `sys_notify_init()`.

## Control Flow

Subsystem initialization delegates directly to the system notify backend initializer and returns its `NTSTATUS`.

## State and Persistence Behavior

No state is persisted by this file. Any state allocation or backend registration occurs inside the sys-notify layer.

## Dependencies and Integration Points

It includes `ntvfs/sysdep/sys_notify.h` and is built into the `ntvfs_common` subsystem with brlock, opendb, and notify support.

## Risks and Edge Cases

Failure in `sys_notify_init()` prevents common NTVFS initialization. Since the file does no logging or fallback, diagnostics depend on the sys-notify implementation.

## Test Signals

Build and startup tests should confirm `ntvfs_common_init()` is called and that sys-notify backends initialize successfully across supported platforms.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/common/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/common/notify.c -->
# sources/user-network-fs/samba/source4/ntvfs/common/notify.c

## Purpose

`notify.c` implements Samba source4's shared change-notify database for NTVFS. It records directory change-notify waiters in a cluster-capable temp DB, integrates optional OS-level notification backends, and sends matching events back to waiting server instances over imessaging.

## Important APIs, Types, and Functions

Public APIs are `notify_init()`, `notify_add()`, `notify_remove()`, and `notify_trigger()`. Internal structures include `struct notify_context` and `struct notify_list`. Important helpers include `notify_load()`, `notify_save()`, `notify_add_array()`, `notify_remove_all()`, `notify_send()`, `notify_handler()`, `sys_notify_callback()`, `notify_lock()`, and `notify_unlock()`.

## Control Flow

Initialization honors share option `notify:enable`, opens the `notify` cluster temp DB with sequence numbers, registers `MSG_PVFS_NOTIFY`, and creates a sys-notify context. Adding a watch locks the DB, loads the cached NDR `notify_array` if the sequence changed, normalizes trailing `/.`, records an in-memory callback, lets sys-notify consume supported filter bits, and stores remaining filters in the shared array by path depth. Triggering reloads if needed, walks path depths, skips depths whose aggregate masks cannot match, uses binary search in sorted entries for candidate paths, and sends matching events through imessaging.

## State and Persistence Behavior

Runtime persistent state is the shared `NOTIFY_KEY` record in `notify.tdb`, NDR-encoded as `struct notify_array`. Local state includes callback list entries and sys-notify handles. The destructor deregisters messaging and removes all entries for the local server from the DB.

## Dependencies and Integration Points

It depends on dbwrap, NDR notify structures, imessaging, cluster server IDs, sys-notify backends, share options, talloc sorting, and util TDB helpers. Filesystem backends call `notify_add()` for change notify requests and `notify_trigger()` when filesystem events occur.

## Risks and Edge Cases

The fast path is subtle: path length calculations use pointer differences while iterating slash positions, so boundary cases matter. `notify_handler()` matches incoming events by `private_data` pointer, which is only meaningful for the target process that registered it. If sys-notify handles some but not all filters, the remaining filters must be stored correctly or events are lost. DB corruption in NDR decode disables notification loading for that trigger.

## Test Signals

Tests should cover disabled notify, add/remove at multiple depths, trailing `/.` normalization, recursive versus non-recursive filters, sys-notify partial handling, trigger path boundary cases, sequence-number cache refresh, messaging callback delivery, destructor cleanup, and many watchers sorted by path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/common/notify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/common/ntvfs_common.h -->
# sources/user-network-fs/samba/source4/ntvfs/common/ntvfs_common.h

## Purpose

`ntvfs_common.h` is the aggregate public header for source4 NTVFS common services. It exposes common notify, byte-range lock, and open-database interfaces to NTVFS backends.

## Important APIs, Types, and Functions

It forward-declares `struct notify_event` and `struct notify_entry`, includes `ntvfs/ntvfs.h`, `brlock.h`, `opendb.h`, and generated `proto.h`.

## Control Flow

The header has no executable control flow. It organizes declarations so modules can include one common header for brlock, opendb, notify, and subsystem initialization prototypes.

## State and Persistence Behavior

The header itself has no state. It exposes opaque context and lock types whose implementations persist runtime state in temp cluster databases.

## Dependencies and Integration Points

It is included by `brlock.c`, `brlock_tdb.c`, `opendb.c`, `opendb_tdb.c`, `notify.c`, and NTVFS backends. It binds the common subsystem's generated prototypes into consumers.

## Risks and Edge Cases

As an aggregate header, changes can increase rebuild scope or introduce include cycles. Generated `proto.h` must stay synchronized with implementation exports.

## Test Signals

Compile-time coverage from all NTVFS common and backend targets is the primary signal. Include-order tests are useful because this header pulls together several interfaces.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/common/ntvfs_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/common/opendb.c -->
# sources/user-network-fs/samba/source4/ntvfs/common/opendb.c

## Purpose

`opendb.c` is the backend-dispatch wrapper for source4 NTVFS open-file database services. It exposes public APIs for share-mode checks, open registration, close cleanup, pending-open notifications, delete-on-close, write-time tracking, and oplock management.

## Important APIs, Types, and Functions

Public functions include `odb_set_ops()`, `odb_init()`, `odb_lock()`, `odb_get_key()`, `odb_can_open()`, `odb_open_file()`, `odb_open_file_pending()`, `odb_close_file()`, `odb_remove_pending()`, `odb_rename()`, `odb_get_path()`, `odb_set_delete_on_close()`, `odb_set_write_time()`, `odb_get_file_infos()`, `odb_update_oplock()`, and `odb_break_oplocks()`.

## Control Flow

Like `brlock.c`, `odb_init()` installs default TDB ops via `odb_tdb_init_ops()` if no backend is selected, then delegates. All other functions pass through to the active backend. The intended calling flow is explicit in comments: callers lock a file key with `odb_lock()`, call `odb_can_open()`, then call `odb_open_file()` with the same lock handle if opening is permitted.

## State and Persistence Behavior

This file stores only a process-global `struct opendb_ops *ops`. Persistent open-file state is owned by the backend, normally `opendb_tdb.c` using `openfiles` cluster temp DB records.

## Dependencies and Integration Points

It depends on NTVFS contexts, cluster IDs, loadparm, and `ntvfs_common.h`. Disk backends use this wrapper to coordinate open/share semantics across server instances.

## Risks and Edge Cases

The global backend pointer is mutable without synchronization. Since pass-throughs do not guard against NULL after initialization, alternate backend tests must set a complete ops table. The protocol contract requiring `odb_can_open()` before `odb_open_file()` is enforced by the backend, not the wrapper.

## Test Signals

Tests should verify default backend selection, alternate ops injection, dispatch for every wrapper, and enforcement of the can-open-before-open sequence through the TDB backend.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/common/opendb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/common/opendb.h -->
# sources/user-network-fs/samba/source4/ntvfs/common/opendb.h

## Purpose

`opendb.h` defines the backend operations interface for the NTVFS open-file database and the small structure used to notify clients about oplock breaks.

## Important APIs, Types, and Functions

The central type is `struct opendb_ops`, with function pointers for init, lock, key retrieval, open registration, pending-open registration/removal, close, rename, path lookup, delete-on-close, write time, file info lookup, share-mode checks, oplock update, and oplock breaks. `struct opendb_oplock_break` contains a file handle pointer and break level. It declares `odb_set_ops()` and `odb_tdb_init_ops()`.

## Control Flow

The header defines the dispatch contract implemented by `opendb_tdb.c` and called by `opendb.c`. There is no executable flow.

## State and Persistence Behavior

Backend state is abstracted through opaque `struct odb_context` and `struct odb_lock` pointers. The interface models persistent runtime open-file records and caller-held DB locks.

## Dependencies and Integration Points

It is included by `ntvfs_common.h` and depends on NTVFS, NT time, oplock, and access-mask types through existing includes. Messaging handlers use `opendb_oplock_break` payloads for `MSG_NTVFS_OPLOCK_BREAK`.

## Risks and Edge Cases

Function pointer signatures must remain consistent with wrapper and backend implementations. `void *file_handle` and `void *private_data` are process-local identifiers sent through persistent records or messages, so lifetime and server identity checks are critical.

## Test Signals

Compile-time coverage should catch signature drift. Runtime tests should verify oplock-break payload interpretation and all operations through the wrapper/backend path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/common/opendb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/common/opendb_tdb.c -->
# sources/user-network-fs/samba/source4/ntvfs/common/opendb_tdb.c

## Purpose

`opendb_tdb.c` implements the TDB-backed source4 NTVFS open-file database. It coordinates share-mode enforcement, delete-on-close, pending-open retry notifications, write-time state, and oplock/lease behavior across server instances.

## Important APIs, Types, and Functions

Backend registration is `odb_tdb_init_ops()`. Internal types are `struct odb_context` and `struct odb_lock`. Important functions include `odb_tdb_init()`, `odb_tdb_lock()`, `odb_tdb_get_key()`, `odb_pull_record()`, `odb_push_record()`, `share_conflict()`, `odb_tdb_open_can_internal()`, `odb_tdb_can_open()`, `odb_tdb_open_file()`, `odb_tdb_open_file_pending()`, `odb_tdb_close_file()`, `odb_tdb_remove_pending()`, `odb_tdb_update_oplock()`, `odb_tdb_break_oplocks()`, `odb_tdb_rename()`, `odb_tdb_get_path()`, `odb_tdb_set_delete_on_close()`, `odb_tdb_set_write_time()`, and `odb_tdb_get_file_infos()`.

## Control Flow

Init opens the `openfiles` cluster temp DB, reads share oplock settings, and creates a sys-lease context. Lock fetches and locks a file-key record, then decodes an NDR `opendb_file` or initializes an empty record. `odb_tdb_can_open()` checks batch oplocks, delete pending state, delete-on-close conflict, share conflicts, exclusive oplocks, and records a pending `opendb_entry` for the subsequent open. `odb_tdb_open_file()` finalizes that entry, grants an oplock level based on existing opens and attribute-only access, sets up a sys lease if possible, appends the entry, and stores the NDR record. Close removes the matching entry, propagates delete-on-close, removes leases, sends pending-open retry messages, and deletes or updates the DB record.

## State and Persistence Behavior

Runtime persistent state is NDR-encoded `struct opendb_file` in `openfiles.tdb`, keyed by caller-provided file identity blobs. Records contain path, entries, pending opens, delete-on-close, open write time, and changed write time. Oplock breaks use imessaging to the server that owns the open; sys leases mirror oplock state to the local OS when available.

## Dependencies and Integration Points

It depends on dbwrap, cluster DB helpers, generated `ndr_opendb`, NTVFS contexts, imessaging, sys-lease backends, share options, access masks, and oplock constants. Disk backends call it through `opendb.c` before and after filesystem opens and closes.

## Risks and Edge Cases

Callers must call `odb_can_open()` and `odb_open_file()` with the same lock handle; otherwise `odb_open_file()` returns internal error. Batch and exclusive oplock handling intentionally returns `NT_STATUS_OPLOCK_NOT_GRANTED` to make callers retry after breaks. Attribute-only access bypasses some oplock breaks and suppresses oplock grants. Pending-open messages are sent and cleared on close or oplock update. Pointer-valued file handles and fd pointers are stored in NDR records with server IDs, so they are meaningful only to the owning process.

## Test Signals

Tests should cover share conflicts for read/write/delete masks and streams, delete pending, delete-on-close with existing opens, can-open/open sequencing, oplock grant downgrade rules, batch/exclusive/level2 break paths, pending-open retry messages, lease setup/update/remove, rename/path lookup, write-time force semantics, and final delete path when last open closes with delete-on-close.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/common/opendb_tdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/common/wscript_build -->
# sources/user-network-fs/samba/source4/ntvfs/common/wscript_build

## Purpose

`source4/ntvfs/common/wscript_build` declares the `ntvfs_common` subsystem containing shared NTVFS support for initialization, byte-range locking, open-file database, and change notification.

## Important APIs, Types, and Functions

It uses `bld.SAMBA_SUBSYSTEM()` with source files `init.c`, `brlock.c`, `brlock_tdb.c`, `opendb.c`, `opendb_tdb.c`, and `notify.c`, and generates `proto.h`.

## Control Flow

At build time it creates one subsystem target named `ntvfs_common` with private dependencies and public dependencies needed by consumers.

## State and Persistence Behavior

The script stores build metadata only. It determines that common runtime state implementations using DB wrappers, NDR records, sys notify, and sys leases are linked together.

## Dependencies and Integration Points

Private dependencies are `util_tdb` and `tdb-wrap`. Public dependencies are `NDR_OPENDB`, `NDR_NOTIFY`, `sys_notify`, `sys_lease`, and `share`, making those interfaces available to downstream NTVFS modules.

## Risks and Edge Cases

Generated `proto.h` freshness matters because `ntvfs_common.h` includes it. Missing public dependencies can break consumers that include the common header but do not link the implementation directly.

## Test Signals

Signals include successful build of `ntvfs_common`, generation of `proto.h`, and downstream NTVFS backends linking against brlock, opendb, notify, sys-notify, and sys-lease symbols.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/common/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/ipc/ipc_rap.c -->
# sources/user-network-fs/samba/source4/ntvfs/ipc/ipc_rap.c

## Purpose

`ipc_rap.c` implements the IPC named-pipe RAP transaction dispatcher for legacy LAN Manager style APIs. It decodes RAP transaction parameters, dispatches supported calls, marshals fixed data records and string heaps, and returns SMB trans2 response buffers.

## Important APIs, Types, and Functions

The public entry point is `ipc_rap_call()`. Internal types include `struct rap_call`, `struct rap_string_heap`, and `struct rap_heap_save`. Helper APIs include `new_rap_srv_call()`, `rap_srv_pull_word()`, `rap_srv_pull_dword()`, `rap_srv_pull_string()`, `rap_srv_pull_bufsize()`, `rap_srv_pull_expect_multiple()`, `rap_push_string()`, `_rap_netshareenum()`, `_rap_netserverenum2()`, and `api_Unsupported()`. Supported commands are `NetShareEnum` and `NetServerEnum2`.

## Control Flow

`ipc_rap_call()` creates a RAP call context from incoming trans params/data, pulls call number, parameter descriptor, and data descriptor, creates NDR push contexts, finds a command by numeric RAP ID, and runs its handler. Each handler validates descriptors and level, calls the semantic RAP server function, then loops through available results, saving data/heap offsets before each item and rolling back if the fixed data area collides with the descending string heap. The final response prepends RAP status and convert offset, appends handler parameters, writes fixed data, then writes heap strings in reverse order.

## State and Persistence Behavior

The file has no persistent state. Per-call state stores NDR pull/push cursors, descriptor strings, output status, receive buffer sizes, and string heap bookkeeping. Output is written into `trans->out`.

## Dependencies and Integration Points

It depends on generated RAP NDR types, raw SMB trans structures, libndr, tevent/loadparm context, and server functions implemented in `rap_server.c`. It is part of the IPC NTVFS backend path that handles RAP over SMB transactions.

## Risks and Edge Cases

Descriptor parsing is strict and advances descriptor pointers as it reads. String heap overflow handling relies on correct rollback of NDR data offsets and heap state. `RAPNDR_FLAGS` includes a trailing semicolon in the macro body, which works in assignments but is stylistically fragile. Unsupported commands return RAP status `NERR_notsupported` with success NTSTATUS. Buffer-size and convert-offset compatibility are legacy-sensitive.

## Test Signals

Tests should cover NetShareEnum levels 0 and 1, NetServerEnum2 levels 0 and 1, invalid descriptors, invalid levels, small output buffers causing partial enumeration, unsupported call numbers, string heap ordering, empty comments, and malformed incoming NDR.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/ipc/ipc_rap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/ipc/rap_server.c -->
# sources/user-network-fs/samba/source4/ntvfs/ipc/rap_server.c

## Purpose

`rap_server.c` provides the semantic server-side implementations behind the RAP dispatcher. It currently enumerates configured shares and returns an empty server enumeration result.

## Important APIs, Types, and Functions

Public functions are `rap_netshareenum()` and `rap_netserverenum2()`. `rap_netshareenum()` uses share APIs `share_get_context()`, `share_list_all()`, `share_get_config()`, `share_string_option()`, and `dcesrv_common_get_share_type()`. `rap_netserverenum2()` initializes success output with zero available servers.

## Control Flow

Share enumeration initializes output status and availability, obtains a share context, lists all share names, allocates a `union rap_share_info` array sized to the initial count, and iterates names. For each share whose config still exists, it copies the share name into the RAP fixed field, sets reserved byte, calculates share type, stores the comment string, frees the config, and increments the kept count. If a service disappears between list and config fetch, it logs a warning and skips it. Server enumeration just returns success with no entries.

## State and Persistence Behavior

This file reads share configuration but does not persist changes. Output arrays and strings are allocated under the caller-provided talloc context and consumed by `ipc_rap.c` for marshalling.

## Dependencies and Integration Points

It depends on Samba share configuration APIs, generated RAP types, generated SRVSVC/DCERPC types, RPC common share helpers, loadparm, and IPC prototypes. It is called only by RAP transaction handlers.

## Risks and Edge Cases

Inside the loop, most fields are written through `r->out.info[j]`, but `reserved1`, `share_type`, and `comment` are assigned via `r->out.info[i]`; if a prior share disappears and `j != i`, output can contain gaps or mismatched data. Share names are truncated with `strlcpy()` into fixed RAP fields. `rap_netserverenum2()` is a stub and may surprise clients expecting browse lists.

## Test Signals

Tests should cover normal share enumeration, disappearing shares during enumeration, long share names, comments and share types, no shares, and NetServerEnum2 empty-success behavior. A regression test should verify output indexing when one listed share cannot be configured.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/ipc/rap_server.c -->
