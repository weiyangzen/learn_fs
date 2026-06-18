# subset-b-007784 Research

Grouped research for the listed OpenAFS libadmin PTS admin implementation, libadmin samples, and `afscp` test harness files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/pts/afs_ptsAdmin.c -->
# sources/distributed-fs/openafs/src/libadmin/pts/afs_ptsAdmin.c

## Purpose
Implements the public libadmin Protection Server (PTS) administration API declared in `afs_ptsAdmin.h`. It validates admin cell handles, translates PTS names and IDs, wraps ubik PR RPCs for user/group create/delete/rename/modify/member operations, and exposes iterator-style list APIs for memberships, owned groups, all users, and all groups.

## Important APIs, Types, And Functions
Public entry points include `pts_GroupMemberAdd`, `pts_GroupOwnerChange`, `pts_GroupCreate`, `pts_GroupGet`, `pts_GroupDelete`, `pts_GroupMaxGet`, `pts_GroupMaxSet`, `pts_GroupMemberListBegin/Next/Done`, `pts_GroupMemberRemove`, `pts_GroupRename`, `pts_GroupModify`, `pts_UserCreate`, `pts_UserDelete`, `pts_UserGet`, `pts_UserRename`, `pts_UserModify`, `pts_UserMaxGet`, `pts_UserMaxSet`, `pts_UserMemberListBegin/Next/Done`, `pts_OwnedGroupListBegin/Next/Done`, `pts_UserListBegin/Next/Done`, and `pts_GroupListBegin/Next/Done`. Internal helpers include `IsValidCellHandle`, `TranslatePTSNames`, `TranslateTwoNames`, `TranslateOneName`, `TranslatePTSIds`, `EntryDelete`, `GetGroupAccess`, `SetGroupAccess`, `GetUserAccess`, `SetUserAccess`, and `IsAdministrator`.

## Control Flow
Most functions follow a common pattern: cast the opaque `cellHandle` to `afs_cell_handle_p`, validate it with `CellHandleIsValid` plus PTS-specific fields, validate caller arguments, translate names through `ubik_PR_NameToID`, execute one PR RPC, map RPC status into `afs_status_t`, and free any ubik-allocated arrays before returning boolean success. Group and user getters call `ubik_PR_ListEntry`, decode PTS flag bits into libadmin access enums, then translate owner and creator IDs back to names with `string_PR_IDToName`. Modify functions build `PR_SF_*` masks and call `ubik_PR_SetFieldsEntry`.

Membership iteration is split between two models. Group/user membership lists are fetched in one `ubik_PR_ListElements` RPC during `Begin`, translated to names immediately, and `Next` just copies from an in-memory namelist under a per-iterator mutex. Owned-group and all-user/all-group listings use the generic `afs_admin_iterator_t` from adminutil; their RPC callbacks page through `ubik_PR_ListOwned` or `ubik_PR_ListEntries`, translate/cache batches, and let `IteratorNext` deliver one name at a time.

## State And Persistence
The file does not persist data locally; all durable state is in the PTS database reached through the cell handle's ubik PR client. Transient state includes ubik `namelist`, `idlist`, and `prlist` buffers, custom membership iterators with magic values and pthread mutexes, and generic admin iterator private structs (`owned_group_list_t`, `pts_list_t`). The mutation APIs change PTS entries, max user/group IDs, flags, memberships, owners, and names on the server.

## Dependencies And Integration Points
It depends on `afs_AdminInternal.h` for cell handles, iterator machinery, magic constants, and cached-item sizing; `afs_AdminErrors.h` for libadmin status codes; `afs_utilAdmin.h` for shared admin conventions; and `ptint.h`/`ptserver.h` for PR RPC types/constants. Integration is through libadmin clients that already opened a cell with a valid PTS connection.

## Risks And Test Signals
There are visible maintenance risks: `TranslateTwoNames` checks `names.namelist_val[0]` twice, so the second name length guard appears wrong; `MemberListBegin` receives custom error codes but hardcodes group-name errors in some branches; and several paths trust caller output buffers to be at least `PTS_MAX_NAME_LEN`. Iterator cleanup must free ubik-allocated arrays exactly once. Test signals should cover invalid handles, too-long first and second names, user/group create with explicit and generated IDs, membership add/remove, flag decoding/encoding, owner/creator translation, admin quota reporting, exhausted iterators returning `ADMITERATORDONE`, and cleanup after failed ubik calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/pts/afs_ptsAdmin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/pts/afs_ptsAdmin.h -->
# sources/distributed-fs/openafs/src/libadmin/pts/afs_ptsAdmin.h

## Purpose
Defines the public libadmin PTS administration interface. It names maximum PTS string/list sizes, exposes user and group access enums, declares user/group result and update structures, and prototypes all user, group, membership, ownership, and listing operations implemented by `afs_ptsAdmin.c`.

## Important APIs, Types, And Functions
The key constants are `PTS_MAX_NAME_LEN` and `PTS_MAX_GROUPS`, intentionally matching ptserver limits. `pts_UserEntry_t` and `pts_GroupEntry_t` carry IDs, owner/creator names, membership counts, quotas, and access settings. `pts_UserUpdateEntry_t` is gated by `PTS_USER_UPDATE_GROUP_CREATE_QUOTA` and `PTS_USER_UPDATE_PERMISSIONS`; `pts_GroupUpdateEntry_t` contains the five group permission fields. The API surface is the `pts_*` function family for create/get/modify/delete/rename/max-ID/list operations.

## Control Flow
Callers open an admin cell elsewhere, call the appropriate `pts_*` operation with that opaque handle, and inspect the boolean return plus optional `afs_status_t`. List APIs use the standard `Begin`/`Next`/`Done` pattern and pass an opaque iterator pointer between calls.

## State And Persistence
The header stores no state. Its structures describe snapshots or updates for persistent PTS database entries, while iterator IDs are opaque transient handles allocated by the implementation.

## Dependencies And Integration Points
The header includes `afs/param.h` and `afs/afs_Admin.h`, uses `ADMINAPI` linkage, and is consumed by libadmin callers and tests. The constants and enum semantics must remain aligned with `ptserver` and `afs_ptsAdmin.c` bit encoding.

## Risks And Test Signals
The main risks are ABI drift, enum value changes that break flag translation, and callers underallocating buffers for `Next` outputs. Compile coverage plus API tests for every declared function are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/pts/afs_ptsAdmin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/Makefile.in -->
# sources/distributed-fs/openafs/src/libadmin/samples/Makefile.in

## Purpose
Builds the libadmin sample command programs for cache-manager, RX debug, and RX statistics APIs. It is an Autoconf template that pulls in OpenAFS build configuration and pthread settings, links each sample statically against the admin and RPC libraries, and installs the RX statistics sample tools.

## Important APIs, Types, And Functions
`SAMPLEPROGS` enumerates the 21 sample binaries. `SAMPLELIBS` links admin utility, client, vos, bos, afsrpc, auth, kauth, cmd, util, ubik, opr, and crypto support libraries. Individual targets use `$(LT_LDRULE_static)` with roken, crypt, and pthread libraries. `CFLAGS_rxstat_query_peer.o` and `CFLAGS_rxstat_query_process.o` opt those objects out of warnings-as-errors.

## Control Flow
`all`, `test`, and `tests` build all sample programs. Each program target depends on its object and shared sample libraries. `install` places only the `rxstat_*` tools into `${sbindir}`; `dest` installs those same tools into `${DEST}/etc`; `clean` removes libtool products, objects, binaries, and core files.

## State And Persistence
The makefile creates build outputs in the sample directory and installs selected binaries. It does not generate runtime state.

## Dependencies And Integration Points
It depends on top-level configured variables such as `TOP_LIBDIR`, `TOP_OBJDIR`, `LIB_roken`, `LIB_crypt`, `MT_LIBS`, and install paths. It integrates sample programs with the broader OpenAFS libadmin, RX, ubik, command-parser, and crypto libraries.

## Risks And Test Signals
Risks include stale library ordering, missing new sample programs in install lists, and warning suppressions masking real query-sample type issues. Test signals are successful `make all`, `make install DESTDIR=...`, and execution of representative CM, rxdebug, and rxstat samples against a test service.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/cm_client_config.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/cm_client_config.c

## Purpose
Demonstrates querying a cache manager's client configuration through the libadmin CM statistics interface.

## Important APIs, Types, And Functions
The file defines `Usage`, `ParseArgs`, and `main`. It uses `afsclient_Init`, `afsclient_NullCellOpen`, `afsclient_CMStatOpenPort`, `util_CMClientConfig`, `afsclient_CMStatClose`, and `afsclient_CellClose`. The main data structure is `afs_ClientConfig_t`.

## Control Flow
The program accepts `<host> <port>`, validates the port in the 1..65535 range, initializes libadmin, opens a null cell handle, opens an RX connection to the cache-manager stats port, fetches configuration, closes the connection and cell, then prints version, cache count, chunk size, cache size, settime, and memory-cache fields.

## State And Persistence
It persists nothing. Runtime state is the parsed server name/port, a null cell handle, an RX connection, status code, and one configuration snapshot.

## Dependencies And Integration Points
It depends on roken, pthread on NT, RX headers, `afs_clientAdmin.h`, and `afs_utilAdmin.h`. It integrates with a remote cache manager that supports the CM stats RPCs.

## Risks And Test Signals
The sample exits immediately on errors and does not close already-open handles on later failures. It prints only the v1 union fields, so newer config versions would need updates. Test signals are correct usage rejection, out-of-range port rejection, successful `util_CMClientConfig`, and clean output against a known cache manager.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/cm_client_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/cm_list_cells.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/cm_list_cells.c

## Purpose
Demonstrates iterating over the cell database known by a cache manager through libadmin utility CM stats calls.

## Important APIs, Types, And Functions
The program uses `Usage`, `ParseArgs`, and `main`, then calls `afsclient_Init`, `afsclient_NullCellOpen`, `afsclient_CMStatOpenPort`, `util_CMListCellsBegin/Next/Done`, `afsclient_CMStatClose`, and `afsclient_CellClose`. It prints `afs_CMListCell_t` records and `UTIL_MAX_CELL_HOSTS` server addresses.

## Control Flow
After host/port parsing and CM stats connection setup, it starts a cell-list iterator, loops until `util_CMListCellsNext` fails, prints each cell name with nonzero server addresses, validates the terminal status is `ADMITERATORDONE`, closes the iterator, connection, and cell.

## State And Persistence
No persistent state is written. The iterator state is owned by the util layer and released by `Done`; the sample holds one current `afs_CMListCell_t`.

## Dependencies And Integration Points
It integrates with the OpenAFS cache manager's CM stats service and admin utility iterator API. Network address printing assumes the returned address value is in display-ready big-endian order.

## Risks And Test Signals
Failure exits can leak handles/iterators. The address output is manual byte shifting, which is easy to misread if address byte order changes. Tests should cover iterator completion, empty cell lists, multi-host cells, and error status when `Next` stops for reasons other than `ADMITERATORDONE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/cm_list_cells.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/cm_local_cell.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/cm_local_cell.c

## Purpose
Demonstrates retrieving the local cell name reported by a remote cache manager.

## Important APIs, Types, And Functions
The functions are `Usage`, `ParseArgs`, and `main`. The sample uses `afsclient_Init`, `afsclient_NullCellOpen`, `afsclient_CMStatOpenPort`, `util_CMLocalCell`, `afsclient_CMStatClose`, and `afsclient_CellClose`, with output stored in `afs_CMCellName_t`.

## Control Flow
The program parses `<host> <port>`, initializes libadmin, opens a null cell and CM stats connection, calls `util_CMLocalCell`, closes resources, and prints the returned cell name with the target host and port.

## State And Persistence
No durable state is touched. Runtime state is limited to one connection, one cell handle, and a cell-name buffer.

## Dependencies And Integration Points
It depends on the client admin and utility admin libraries and the cache manager stats RPC endpoint. It is a small executable built by the samples makefile.

## Risks And Test Signals
The same early-exit leak pattern applies. Test signals are argument validation, successful local-cell retrieval from a running cache manager, and a failed call to an inactive or wrong port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/cm_local_cell.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/cm_server_prefs.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/cm_server_prefs.c

## Purpose
Demonstrates listing cache-manager server preference ranks over the CM stats interface.

## Important APIs, Types, And Functions
The file defines `Usage`, `ParseArgs`, and `main`, and uses `afsclient_Init`, `afsclient_NullCellOpen`, `afsclient_CMStatOpenPort`, `util_CMGetServerPrefsBegin/Next/Done`, `afsclient_CMStatClose`, and `afsclient_CellClose`. Each row is an `afs_CMServerPref_t` with `ipAddr` and `ipRank`.

## Control Flow
After connecting to the selected host and port, `main` starts the preference iterator, prints an address/rank header, loops through every preference, checks for `ADMITERATORDONE`, closes the iterator and resources, and exits.

## State And Persistence
It reads a transient snapshot of cache-manager ranking state and writes only stdout/stderr. Iterator ownership belongs to the util layer.

## Dependencies And Integration Points
It uses libadmin CM stat connections and the utility admin server-preference iterator. It integrates with the same sample build infrastructure as the other CM samples.

## Risks And Test Signals
Manual IP formatting and fail-fast cleanup are the main risks. Tests should compare output against a cache manager with known server preferences, including multiple ranks and an empty preference table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/cm_server_prefs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_basic_stats.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_basic_stats.c

## Purpose
Demonstrates retrieving basic RX debug counters from a target RX service.

## Important APIs, Types, And Functions
The program defines `Usage`, `ParseArgs`, and `main`, opens an RX debug handle with `afsclient_RXDebugOpenPort`, calls `util_RXDebugBasicStats`, closes with `afsclient_RXDebugClose`, and prints fields from `afs_RXDebugBasicStats_t`.

## Control Flow
It parses a host and port, initializes libadmin, opens the RX debug connection, fetches basic stats, closes the handle, and prints packet counts, call counts, connection counts, packet pools, and related basic RX runtime values.

## State And Persistence
The sample reads live RX runtime state and persists nothing. The only owned resources are the RX debug handle and local stats struct.

## Dependencies And Integration Points
It depends on RX/rxstat headers, client admin connection helpers, and util admin RX debug APIs. It is useful as a smoke test for service `rxdebug` support.

## Risks And Test Signals
It assumes the target supports the requested debug RPC and that fields match the printed struct version. Test signals are port validation, successful stats retrieval, and expected failure against a non-RX or non-debug service.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_basic_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_conns.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_conns.c

## Purpose
Demonstrates listing RX debug connection records from a target service.

## Important APIs, Types, And Functions
It uses `util_RXDebugSupportedStats` to detect supported connection detail, `util_RXDebugConnectionsBegin/Next/Done` to iterate, and `afsclient_RXDebugOpenPort/Close` for the debug handle. Local output structures include connection details and supported-value flags.

## Control Flow
After parsing and opening the RX debug handle, the sample queries supported stats, starts the connection iterator, optionally retries with a reduced detail request if the target cannot provide all connection data, prints each connection's host/port/cid/call/security/user fields, closes the iterator, and closes the handle.

## State And Persistence
No persistent changes occur. Runtime state consists of an iterator and one current connection record.

## Dependencies And Integration Points
It integrates with RX debug service APIs and uses support discovery to adapt to older or limited RX implementations. It is linked by the libadmin samples makefile.

## Risks And Test Signals
Compatibility risk centers on supported-stat negotiation and struct-version assumptions. Tests should include a service with active and idle connections, unsupported extended stats, iterator completion, and failure when the debug endpoint is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_conns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_peers.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_peers.c

## Purpose
Demonstrates iterating RX debug peer records for a remote RX service.

## Important APIs, Types, And Functions
The sample uses `afsclient_RXDebugOpenPort`, `util_RXDebugPeersBegin/Next/Done`, and `afsclient_RXDebugClose`. It prints `afs_RXDebugPeer_t` data plus `afs_RXDebugPeerStats_t` support flags returned with each iteration.

## Control Flow
`main` parses host/port, initializes libadmin, opens RX debug, starts peer iteration, prints each peer's address, port, packet/rtt/congestion/window statistics where supported, verifies `ADMITERATORDONE`, then closes the iterator and handle.

## State And Persistence
The program is read-only and transient. Iterator state lives in util admin; output is a live snapshot of RX peer state.

## Dependencies And Integration Points
It depends on RX debug support in the target service and the libadmin utility iterator abstraction.

## Risks And Test Signals
The main risks are assuming optional peer statistics are present and incomplete cleanup on failures. Good signals include output for services with multiple peers, older services with fewer supported fields, and no-peer iterator completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_peers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_rx_stats.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_rx_stats.c

## Purpose
Demonstrates retrieving detailed RX runtime statistics from an RX debug endpoint.

## Important APIs, Types, And Functions
The core calls are `afsclient_RXDebugOpenPort`, `util_RXDebugRxStats`, and `afsclient_RXDebugClose`. The returned data includes `afs_RXDebugRxStats_t` and supported-stat metadata.

## Control Flow
The sample parses target host/port, initializes libadmin, opens RX debug, calls `util_RXDebugRxStats`, closes the handle, and prints available counters, timings, and packet statistics according to the supported-stat flags.

## State And Persistence
It reads live RX process counters and writes no state. Local state is one handle and one stats snapshot.

## Dependencies And Integration Points
It integrates with RX debug stats RPCs and sample build libraries for client/admin utility support.

## Risks And Test Signals
Version and support-bit handling are the primary concerns. Tests should cover services with full stats, partial stats, and unsupported debug calls, plus port validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_rx_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_supported_stats.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_supported_stats.c

## Purpose
Demonstrates querying which RX debug statistic classes a target service supports.

## Important APIs, Types, And Functions
It defines `Usage`, `ParseArgs`, and `main`, and calls `afsclient_Init`, `afsclient_RXDebugOpenPort`, `util_RXDebugSupportedStats`, and `afsclient_RXDebugClose`. The output is an `afs_RXDebugStats_t` support mask/record.

## Control Flow
After argument validation, the program opens RX debug on the supplied host/port, fetches supported-stat information, closes the handle, and prints whether basic, version, peer, connection, and RX stats are available.

## State And Persistence
No state is modified. It reads capability information from the remote RX service.

## Dependencies And Integration Points
It provides a compatibility probe for the other `rxdebug_*` samples and depends on libadmin RX debug utility APIs.

## Risks And Test Signals
The sample relies on support fields staying aligned with util admin definitions. Tests should query both modern and older services and ensure unsupported classes are reported rather than causing later detailed calls to be attempted blindly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_supported_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_version.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_version.c

## Purpose
Demonstrates retrieving the version string exposed by an RX debug endpoint.

## Important APIs, Types, And Functions
The sample uses `afsclient_RXDebugOpenPort`, `util_RXDebugVersion`, and `afsclient_RXDebugClose`, with a local version string buffer.

## Control Flow
It parses `<host> <port>`, initializes libadmin, opens RX debug, asks for the version string, closes the handle, and prints the target and returned version.

## State And Persistence
The program is read-only and retains only a transient RX debug handle and stack buffer.

## Dependencies And Integration Points
It is the smallest RX debug smoke test and integrates with RX debug service support through libadmin.

## Risks And Test Signals
Risks are buffer-size assumptions and fail-fast cleanup. Test signals are successful version output from an RX debug capable daemon and clear failure for a closed or wrong port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_version.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_clear_peer.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxstat_clear_peer.c

## Purpose
Implements a sample `rxstat clear peer` command that clears peer RPC statistics on a selected RX service.

## Important APIs, Types, And Functions
The command handler `rxstat_clear_peer` is registered by `main` through `cmd_CreateSyntax`. It uses `cmd_OptionAsString`, `cmd_OptionAsInt`, `cmd_OptionAsFlag`, `afsclient_Init`, `afsclient_TokenPrint` or `afsclient_TokenGetExisting`, `afsclient_CellOpen`, `afsclient_RPCStatOpenPort`, `util_RPCStatsClear`, `afsclient_RPCStatClose`, `afsclient_CellClose`, and `afsclient_TokenClose`.

## Control Flow
The command requires `-cell`, `-server`, and `-port`, with optional `-localauth`. It validates the port, obtains server tickets from the local keyfile or existing user tokens, opens the cell and RPC stats connection, clears all peer counters via `RXSTATS_ClearPeerRPCStats` and `AFS_RX_STATS_CLEAR_ALL`, then closes resources.

## State And Persistence
It mutates remote RX peer-stat counters by resetting them. Local state is only authentication, cell, and connection handles.

## Dependencies And Integration Points
It depends on the OpenAFS `cmd` parser, server config directory `AFSDIR_SERVER_ETC_DIR`, RX stats constants, and authenticated libadmin RPC stats APIs.

## Risks And Test Signals
It always clears all peer counters and has no partial-clear option. Failure paths may leave earlier handles open. Tests should verify auth modes, port range rejection, peer counters resetting to zero, and permission failure with insufficient tokens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_clear_peer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_clear_process.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxstat_clear_process.c

## Purpose
Implements a sample `rxstat clear process` command that clears process-level RPC statistics on a selected RX service.

## Important APIs, Types, And Functions
The structure mirrors `rxstat_clear_peer.c`, but `util_RPCStatsClear` is invoked with `RXSTATS_ClearProcessRPCStats`. Command options are `-cell`, `-server`, `-port`, and optional `-localauth`.

## Control Flow
The handler parses command options, validates the UDP port, gets either local-auth or existing tokens, opens the execution cell and RPC stats connection, clears all process counters with `AFS_RX_STATS_CLEAR_ALL`, and closes the connection, cell, and token.

## State And Persistence
The only durable effect is resetting process RPC stats on the remote server. No local files are modified.

## Dependencies And Integration Points
It integrates with authenticated RX stats admin RPCs and the `cmd` command parser. The build installs it as one of the shipped rxstat sample tools.

## Risks And Test Signals
Risks match the peer clear sample: broad all-counter reset, incomplete cleanup on intermediate failure, and auth dependency. Test signals are successful reset of process counters, unchanged peer counters, and expected authorization failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_clear_process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_disable_peer.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxstat_disable_peer.c

## Purpose
Implements a sample command to disable collection of peer RPC statistics on a selected RX service.

## Important APIs, Types, And Functions
The handler `rxstat_disable_peer` uses the same command/auth/connection setup as the clear commands and calls `util_RPCStatsStateDisable(conn, RXSTATS_DisablePeerRPCStats, &st)`.

## Control Flow
It parses `-cell`, `-server`, `-port`, and `-localauth`; validates port; obtains a token; opens the cell and RPC stats port; disables peer stats collection; closes all handles; and returns command-parser status.

## State And Persistence
It changes remote in-process RX stats collection state for peer counters. The persistence duration depends on the target daemon's RX stats implementation, not this sample.

## Dependencies And Integration Points
It depends on RX stats service support and administrative authorization. It is linked and optionally installed by `samples/Makefile.in`.

## Risks And Test Signals
Disabling stats can hide later observability, so tests should restore state afterward. Signals include query-before/query-after showing peer stats disabled, process stats unaffected, and failure with invalid auth or unsupported target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_disable_peer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_disable_process.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxstat_disable_process.c

## Purpose
Implements a sample command to disable process-level RPC statistics collection on a selected RX service.

## Important APIs, Types, And Functions
It uses `cmd` parsing, libadmin token/cell helpers, `afsclient_RPCStatOpenPort`, and `util_RPCStatsStateDisable` with `RXSTATS_DisableProcessRPCStats`.

## Control Flow
The command opens an authenticated RPC stats connection to `-server -port`, switches process stats collection off, and closes token, cell, and connection handles.

## State And Persistence
It mutates remote RX stats collection state for process counters. No local persistent state is written.

## Dependencies And Integration Points
The file integrates with the same rxstat command family and OpenAFS admin token model as the peer disable sample.

## Risks And Test Signals
Tests should confirm process state transitions to disabled, peer state remains independent, invalid ports are rejected, and missing privileges fail cleanly. Cleanup leaks on early return remain a sample-code risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_disable_process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_enable_peer.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxstat_enable_peer.c

## Purpose
Implements a sample command to enable peer RPC statistics collection on a selected RX service.

## Important APIs, Types, And Functions
The command handler calls `util_RPCStatsStateEnable(conn, RXSTATS_EnablePeerRPCStats, &st)` after the standard `cmd` option parsing, token acquisition, cell open, and RPC stats connection sequence.

## Control Flow
It validates `-port`, obtains local-auth or existing tokens for `-cell`, opens `-server` at the requested port, enables peer stat collection, closes connection/cell/token, and returns zero on success.

## State And Persistence
The remote daemon's peer-stat collection state is changed. Local state is transient.

## Dependencies And Integration Points
It depends on OpenAFS admin authentication, RX stats service support, and command-parser registration in `main`.

## Risks And Test Signals
Signals include query state changing from disabled to enabled, later `rxstat_get_peer` producing counters, and proper rejection of unauthorized or unsupported targets. Early errors can skip cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_enable_peer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_enable_process.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxstat_enable_process.c

## Purpose
Implements a sample command to enable process-level RPC statistics collection on a selected RX service.

## Important APIs, Types, And Functions
The handler is identical in structure to the peer enable command but calls `util_RPCStatsStateEnable` with `RXSTATS_EnableProcessRPCStats`.

## Control Flow
Command parsing gathers `-cell`, `-server`, `-port`, and `-localauth`; the handler validates the port, opens authenticated admin state, enables process stats, and closes the opened handles.

## State And Persistence
It changes the remote service's process-stat collection state. No local data is persisted.

## Dependencies And Integration Points
It is part of the installed rxstat sample suite and depends on libadmin client/util APIs plus RX stats constants.

## Risks And Test Signals
Tests should query process state before and after enable, check that peer state is not accidentally changed, and verify auth and port validation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_enable_process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_get_peer.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxstat_get_peer.c

## Purpose
Implements a sample command to retrieve and print peer-level RX RPC statistics from a target service.

## Important APIs, Types, And Functions
`GetPrintStrings` maps RX interface IDs to human-readable interface names and generated function-name arrays (`RXAFS_function_names`, `PR_function_names`, `VL_function_names`, `BOZO_function_names`, etc.). `rxstat_get_peer` opens a null cell and RPC stats connection, starts `util_RPCStatsGetBegin(conn, RXSTATS_RetrievePeerRPCStats, ...)`, loops with `util_RPCStatsGetNext`, and closes with `util_RPCStatsGetDone`.

## Control Flow
The command accepts `-server` and `-port`. Each returned `afs_RPCStats_t` represents one function index. When index zero appears, the sample prints a new header including remote peer address, port, server/client role, and interface name. For each function it prints invocation counts, bytes sent/received, queue timing, and execution timing, or `Never invoked`.

## State And Persistence
It is read-only. Iterator state is transient and owned by util admin until `Done`.

## Dependencies And Integration Points
It directly includes many RPC interface headers to access function-name arrays and stat-index constants. It integrates with RX stats retrieval RPCs and the OpenAFS `cmd` parser.

## Risks And Test Signals
Risk lies in keeping interface ID mappings and function-count arrays aligned with generated RPC headers. Unknown function indexes are handled, but unknown interfaces only get numeric labels. Tests should retrieve stats from services exposing several interfaces, verify address/role formatting, and check `ADMITERATORDONE` handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_get_peer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_get_process.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxstat_get_process.c

## Purpose
Implements a sample command to retrieve process-level RX RPC statistics from a target service.

## Important APIs, Types, And Functions
Like `rxstat_get_peer.c`, it maps interface IDs through `GetPrintStrings`, but process stats omit the remote host address in the header. The core APIs are `afsclient_RPCStatOpenPort`, `util_RPCStatsGetBegin` with `RXSTATS_RetrieveProcessRPCStats`, `util_RPCStatsGetNext`, `util_RPCStatsGetDone`, and `afsclient_RPCStatClose`.

## Control Flow
The command parses `-server` and `-port`, validates the port, opens a null-cell RPC stats connection, iterates all process stats records, starts a new interface heading when `func_index == 0`, prints function names and timing/counter data, validates iterator completion, and closes resources.

## State And Persistence
The program reads remote process counters and does not modify them.

## Dependencies And Integration Points
It depends on generated RPC interface symbol arrays from fileserver, callback, ptserver, ubik, vldb, bos, kas, and volserver headers. It is built as a standalone sample.

## Risks And Test Signals
Risks are generated-header drift and zero-index grouping assumptions. Tests should compare output with enabled process stats, disabled stats behavior, unknown interface handling, and iterator cleanup on completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_get_process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_get_version.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxstat_get_version.c

## Purpose
Implements a sample command to query the RX stats interface version from a selected service.

## Important APIs, Types, And Functions
`rxstat_get_version` uses `cmd_OptionAsString`, `cmd_OptionAsInt`, `afsclient_Init`, `afsclient_NullCellOpen`, `afsclient_RPCStatOpenPort`, `util_RPCStatsVersionGet`, `afsclient_RPCStatClose`, and `afsclient_CellClose`.

## Control Flow
The command requires `-server` and `-port`, validates the port, opens a null cell and RPC stats connection, retrieves `afs_RPCStatsVersion_t`, closes resources, and prints the version number.

## State And Persistence
It is read-only and creates no persistent state.

## Dependencies And Integration Points
It integrates with libadmin RPC stats connection handling and the OpenAFS command parser.

## Risks And Test Signals
The sample is a low-impact compatibility check. Signals are correct version output from known RX stats services, failure on unsupported endpoints, and no resource leaks under normal completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_get_version.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_query_peer.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxstat_query_peer.c

## Purpose
Implements a sample command to query whether peer RPC statistics collection is enabled on a target RX service.

## Important APIs, Types, And Functions
The handler calls `util_RPCStatsStateGet(conn, RXSTATS_QueryPeerRPCStats, &state, &st)` and prints an `afs_RPCStatsState_t` as enabled or disabled.

## Control Flow
`main` registers `-server` and `-port` with the command parser. The handler validates the port, initializes libadmin, opens a null cell and RPC stats connection, queries peer stats state, closes the connection and cell, and returns command status.

## State And Persistence
No mutation occurs. It reads remote peer-stat collection state.

## Dependencies And Integration Points
It is a diagnostic companion to the peer enable/disable/clear/get samples and depends on RX stats query support.

## Risks And Test Signals
Tests should verify state matches after enable/disable operations, invalid ports fail, and unsupported services return a meaningful libadmin status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_query_peer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_query_process.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxstat_query_process.c

## Purpose
Implements a sample command to query whether process RPC statistics collection is enabled on a target RX service.

## Important APIs, Types, And Functions
The file mirrors `rxstat_query_peer.c` but passes `RXSTATS_QueryProcessRPCStats` to `util_RPCStatsStateGet`.

## Control Flow
The command registers required `-server` and `-port` options, validates the port, opens a null-cell RPC stats connection, queries process stats state, prints enabled/disabled, and closes handles.

## State And Persistence
It is read-only and does not alter local or remote counters.

## Dependencies And Integration Points
It depends on libadmin client/util APIs, RX stats constants, and the command parser. It pairs with the process enable/disable/get/clear commands.

## Risks And Test Signals
Test signals include correct state transitions after process enable/disable, behavior with disabled stats, and clean error returns for unavailable endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_query_process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/Makefile.in -->
# sources/distributed-fs/openafs/src/libadmin/test/Makefile.in

## Purpose
Builds the `afscp` libadmin test driver and its command modules.

## Important APIs, Types, And Functions
`AFSCPLIBS` links admin utility, client, bos, vos, kas, pts, afsrpc, auth, cmd, kauth, opr, ubik, util, and crypto libraries. `AFSCPOBJS` lists command modules: `bos.o`, `client.o`, `kas.o`, `pts.o`, `util.o`, and `vos.o`. The `afscp` target links those with `afscp.o`.

## Control Flow
`all`, `test`, and `tests` build `afscp`. `CFLAGS_client.o = @CFLAGS_NOERROR@` suppresses warning-as-error for the client test module. `install` and `dest` are no-ops. `clean` removes libtool files, objects, the `afscp` binary, and core files.

## State And Persistence
Build products are generated in the test directory. No runtime state is managed by the makefile.

## Dependencies And Integration Points
It integrates the libadmin subsystem tests into the OpenAFS build and links all major admin libraries because `afscp` exercises BOS, client, KAS, PTS, util, and VOS command families.

## Risks And Test Signals
Risks include library-order fragility, hidden client-module warnings, and no install target for external test packaging. Signals are successful `make tests`, successful static link, and running `afscp` subcommands against a configured test cell.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/afscp.c -->
# sources/distributed-fs/openafs/src/libadmin/test/afscp.c

## Purpose
Provides the main `afscp` test driver for libadmin command modules. It initializes libadmin, registers shared before/after hooks, installs command syntaxes for BOS, client, KAS, PTS, util, and VOS tests, and dispatches the selected command.

## Important APIs, Types, And Functions
Global state is `void *cellHandle`, `void *tokenHandle`, and `existing_tokens`. `MyBeforeProc` interprets common auth arguments and opens the token/cell handles. `MyAfterProc` closes them. `SetupCommonCmdArgs` appends common options at `USER_PARAM` through `USEEXISTTOKENS_PARAM`. `main` calls `afsclient_Init`, `cmd_SetBeforeProc`, `cmd_SetAfterProc`, `Setup*AdminCmd`, and `cmd_Dispatch`.

## Control Flow
Each subcommand that calls `SetupCommonCmdArgs` gets `-authuser`, `-authpassword`, `-authcell`, `-execcell`, `-noauth`, and `-usetokens`. Before command execution, the hook rejects incompatible auth combinations, defaults missing auth/exec cells to the local cell, obtains no-auth, existing, or password-derived tokens, and opens the execution cell. After the command, it closes the global handles.

## State And Persistence
The driver itself persists nothing, but it creates authenticated token and cell handles around each command. Subcommands may mutate remote AFS state through those handles. `existing_tokens` is a process-global flag set by the before hook.

## Dependencies And Integration Points
It depends on the OpenAFS command parser, client admin token/cell APIs, utility error translation via `common.h`, and setup functions declared in sibling command-module headers.

## Risks And Test Signals
There is a bug-prone path for `-noauth`: `auth_cell` is not initialized before `afsclient_TokenGetNew` if no auth cell was accepted, since `-noauth` also rejects `-authcell`. Password auth requires `-authuser`; there is no interactive prompt. Test signals should cover every auth mode, incompatible-option errors, default local-cell resolution, after-hook cleanup, and all setup modules appearing in `afscp help`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/afscp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/bos.c -->
# sources/distributed-fs/openafs/src/libadmin/test/bos.c

## Purpose
Implements the BOS-related `afscp` subcommands. It wraps libadmin BOS APIs for process management, admins, keys, cell/host configuration, executable deployment, restart schedules, logs, auth mode, arbitrary commands, and salvage operations.

## Important APIs, Types, And Functions
Utility helpers include `GetIntFromString`, local token parsing helpers, `ktime_ParsePeriodic`, print helpers for process state/type/info, key info, and restart time. Command handlers include `DoBosProcessCreate`, `DoBosFSProcessCreate`, `DoBosProcessDelete`, `DoBosProcessExecutionStateGet/Set/SetTemporary`, `DoBosProcessNameList`, `DoBosProcessInfoGet`, `DoBosProcessParameterList`, `DoBosProcessNotifierGet`, `DoBosProcessRestart`, `DoBosProcessAllStop/Start/WaitStop/WaitTransition/StopAndRestart`, `DoBosAdminCreate/Delete/List`, `DoBosKeyCreate/Delete/List`, `DoBosCellSet/Get`, `DoBosHostCreate/Delete/List`, `DoBosExecutableCreate/Revert/TimestampGet/Prune/RestartTimeSet/RestartTimeGet`, `DoBosLogGet`, `DoBosAuthSet`, `DoBosCommandExecute`, `DoBosSalvage`, and `SetupBosAdminCmd`.

## Control Flow
Every command opens a BOS server handle with `bos_ServerOpen(cellHandle, -server, &bos_server, &st)`, validates command-specific options, calls one libadmin BOS operation, prints output for getters/listers, and usually closes the server. List commands use `Begin/Next/Done` iterators and verify `ADMITERATORDONE`. Restart-time commands parse human-readable time tokens into `bos_RestartTime_t`. Key creation derives a key from the current cell name and a string through `kas_StringToKey`.

## State And Persistence
Most handlers mutate persistent BOS server state: `BosConfig`, `UserList`, `KeyFile`, `CellServDB`, executable files, restart schedules, auth requirement, or salvager side effects. `DoBosLogGet` dynamically grows a local buffer while reading remote log contents. The command module itself stores only stack-local state.

## Dependencies And Integration Points
It depends on `bos.h`, `common.h`, `afs_bosAdmin.h`, `afs_clientAdmin.h`, `afs_utilAdmin.h`, `kas_StringToKey`, `cmd`, pthread/RX headers, and global `cellHandle` from `afscp.c`. It is registered by `SetupBosAdminCmd`.

## Risks And Test Signals
Several bugs are visible: `DoBosCellSet` reads `as->parms[SERVER]` into `cell` instead of the `CELL` parameter, `Print_bos_ProcessState_p` tests `BOS_PROCESS_OK` as a bit even though the comment says it is zero, `Print_bos_RestartTime_p` contains duplicated `NOW` condition text in this checkout, and some getter paths do not close `bos_server` before returning. The time parser has fixed 256-byte token buffers. Tests should cover every command syntax, server open/close, iterator completion, cell-set correctness, key conversion, restart time parse/format round trips, log growth on `ADMMOREDATA`, and high-risk mutating operations in a disposable test cell.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/bos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/bos.h -->
# sources/distributed-fs/openafs/src/libadmin/test/bos.h

## Purpose
Declares the BOS command registration function for the `afscp` test driver and pulls in the headers needed by BOS command implementations.

## Important APIs, Types, And Functions
The only explicit declaration is `SetupBosAdminCmd(void)`. The header includes OpenAFS standards, stdlib/stdio/string/errno, pthread, RX/rxstat, BOS/util/client admin headers, cellconfig, cmd, and `common.h`.

## Control Flow
`afscp.c` calls `SetupBosAdminCmd` during startup so `bos.c` can register all BOS subcommands with the command parser.

## State And Persistence
The header stores no state. It exposes access to global handles from `common.h` and the admin APIs that can mutate BOS server state.

## Dependencies And Integration Points
It is shared between `afscp.c` and `bos.c`, coupling the BOS command module to the common auth setup and OpenAFS command-parser environment.

## Risks And Test Signals
The broad include set can hide missing includes in `bos.c`, but compile success of both the module and `afscp` is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/bos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/client.c -->
# sources/distributed-fs/openafs/src/libadmin/test/client.c

## Purpose
Implements the client-related `afscp` subcommands. It exercises libadmin client APIs for local cell lookup, mount point creation, AFS server discovery, RX stats state/list/clear/version operations, and cache-manager stats queries.

## Important APIs, Types, And Functions
The file defines interface-function mappings for RXAFS, RXAFSCB, BOZO, KAA/KAM/KAT, PR, RXSTATS, ubik disk/vote, VL, and volserver interfaces, including NT-specific `pthread_once` initialization. Command handlers include `DoClientLocalCellGet`, `DoClientMountPointCreate`, `DoClientAFSServerGet`, `DoClientAFSServerList`, `DoClientRPCStatsStateGet/Enable/Disable`, `DoClientRPCStatsList`, `DoClientRPCStatsClear`, `DoClientRPCStatsVersionGet`, `DoClientCMGetServerPrefs`, `DoClientCMListCells`, `DoClientCMLocalCell`, `DoClientCMClientConfig`, and `SetupClientAdminCmd`.

## Control Flow
Client commands use the global authenticated `cellHandle` prepared by `afscp.c`. RPC stats commands convert `-process` either to an `afs_stat_source_t` through a prefix match or to a numeric port, convert `-stat_type` to peer/process, open the proper RPC stats connection, then query, enable, disable, list, clear, or get version. Listing prints interface headers and per-function counters. CM commands open the cache-manager stats port, iterate server preferences or cells, or fetch local-cell/config snapshots. `SetupClientAdminCmd` registers every syntax and attaches common auth options.

## State And Persistence
Many operations are read-only, but mount point creation writes into AFS namespace state and RX stats enable/disable/clear mutates remote service stats state. Local transient state includes RX connections, iterators, function-list mappings, and output structs.

## Dependencies And Integration Points
It depends on generated RPC interface headers for function names, `afs_clientAdmin.h`, `afs_utilAdmin.h`, RX/rxstat, cellconfig, bosint, ubik, and `common.h`. It integrates the standalone sample patterns into one command-driven test harness.

## Risks And Test Signals
Visible risks include a typo in the enum value `afs_proc_tESS_STATS`, prefix matching that accepts abbreviated process names and may be ambiguous, no port range enforcement in `GetStatPortFromString`, duplicated `afs_uint32 taddr` declaration in `Print_afs_CMServerPref_p` in this checkout, and some `printf` calls using `as->parms[PORT].items->data` even when `-port` is optional and absent. Tests should cover every registered syntax, optional port defaults, named and numeric process selection, peer/process stats transitions, partial clear flags, mount point creation, iterator completion, and Windows function-list initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/client.h -->
# sources/distributed-fs/openafs/src/libadmin/test/client.h

## Purpose
Declares the client command registration function for the `afscp` test driver and includes the API surface needed by client command implementations.

## Important APIs, Types, And Functions
The header declares `SetupClientAdminCmd(void)` and includes OpenAFS standards, pthread, RX/rxstat, admin, client admin, util admin, cellconfig, cmd, and `common.h`.

## Control Flow
`afscp.c` calls `SetupClientAdminCmd` after installing common before/after hooks. `client.c` then registers all client and RX stats command syntaxes.

## State And Persistence
The header has no state. Through included declarations, client commands can use global `cellHandle`/`tokenHandle` from `common.h` and may mutate remote stats state or AFS namespace state.

## Dependencies And Integration Points
It is the module boundary between the generic `afscp` driver and the client command implementation.

## Risks And Test Signals
Risks are limited to declaration drift and over-broad includes. The relevant signal is a clean `afscp` build and visible client commands in the command parser.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/common.h -->
# sources/distributed-fs/openafs/src/libadmin/test/common.h

## Purpose
Provides shared error macros, common command-argument indexes, and global handle declarations for the `afscp` libadmin test modules.

## Important APIs, Types, And Functions
`ERR_EXT` prints an error string and exits. `ERR_ST_EXT` translates an `afs_status_t` through `util_AdminErrorCodeTranslate`, prints message, symbolic text, and numeric code, then exits. `CommonParm_t` fixes parser offsets for `-authuser`, `-authpassword`, `-authcell`, `-execcell`, `-noauth`, and `-usetokens`. The header declares `SetupCommonCmdArgs`, `cellHandle`, and `tokenHandle`.

## Control Flow
Command modules call `SetupCommonCmdArgs(ts)` after adding command-specific options. Runtime hooks in `afscp.c` use the shared indexes to parse auth options and initialize the declared global handles before handlers run.

## State And Persistence
The header declares but does not define `cellHandle` and `tokenHandle`. The macros exit the process immediately on failures, so cleanup is intentionally coarse in this test harness.

## Dependencies And Integration Points
It depends on `util_AdminErrorCodeTranslate` being available via module includes. It ties all `afscp` command modules to the same auth/cell setup convention.

## Risks And Test Signals
Immediate `exit(1)` can skip module-local cleanup, and hard-coded parameter offsets require command modules not to collide with common options. Tests should confirm common options appear at the expected offsets and translated status output is meaningful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/common.h -->
