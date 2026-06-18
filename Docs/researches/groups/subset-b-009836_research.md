# subset-b-009836 research

Grouped research for the Samba `source3/nmbd` packet, logon, browse announcement, subnet, response-record, sync-list, WINS proxy, and WINS server files in this work item. Each section is source-tree aligned and bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_packets.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_packets.c

## Purpose
`nmbd_packets.c` is the central packet I/O and dispatch layer for Samba's NetBIOS name daemon. It initializes the unexpected packet side server, builds outbound NetBIOS name packets and datagram mailslot frames, queues inbound packets, validates and routes NMB requests/responses, retransmits expected-response records, and drives socket polling for all configured IPv4 broadcast, unicast, and datagram sockets.

## Important APIs, types, and functions
- `nmbd_init_packet_server` creates the `nb_packet_server` used for packets that nmbd decides not to consume directly.
- `get_nb_flags` and `set_nb_flags` encode/decode the NetBIOS flags byte used in NB resource records.
- `queue_register_name`, `queue_wins_refresh`, `queue_register_multihomed_name`, `queue_release_name`, `queue_query_name`, `queue_query_name_from_wins_server`, and `queue_node_status` are the public queuing APIs for outbound NMB operations. They create a packet, initiate transmission, and attach a `response_record`.
- `reply_netbios_packet` constructs NMB replies for normal name service and WINS paths, including query, status, registration, release, WACK, and error replies.
- `queue_packet`, `run_packet_queue`, `listen_for_packets`, and `send_mailslot` form the runtime event loop boundary.
- Internal helpers such as `create_and_init_netbios_packet`, `create_and_init_additional_record`, `send_netbios_packet`, `validate_nmb_packet`, `validate_nmb_response_packet`, `find_subnet_for_nmb_packet`, `process_dgram`, and `retransmit_or_expire_response_records` carry most of the routing and safety policy.

## Control flow
Outbound name-service requests start by creating a packet with a generated transaction id, opcode-specific flags, and a destination subnet or WINS server address. Registration, refresh, release, and multihomed registration attach an additional NB record containing flags and the source IP being registered. Successful sends are wrapped in `response_record` objects so later responses and timeouts can call operation-specific callbacks.

Inbound packets are read by `listen_for_packets`. The function builds or refreshes a static listen array from `ClientNMB`, `ClientDGRAM`, and all subnet sockets, optionally adds the async DNS fd, arms a `tevent` timeout, and then queues each readable UDP packet after duplicate suppression and source filtering. `run_packet_queue` drains that queue: NMB packets go to request or response processing; datagrams go to mailslot dispatch.

NMB requests are validated, mapped to a subnet, then dispatched to either WINS handlers or normal name-service handlers. NMB responses are matched by transaction id against response records, have their retry count cancelled, and call the record's response callback. Datagram processing verifies the destination name is one nmbd owns, checks SMB transaction framing and length boundaries, then dispatches browse, LANMAN, and NETLOGON mailslots.

## State and persistence behavior
The file keeps process-local state only: `packet_queue`, `name_trn_id`, `packet_server`, `rescan_listen_set`, and static listen-array state. Persistent effects happen through called modules: response records are held on subnet lists, WINS changes are written by WINS code, and browse data is written elsewhere. Packet lifetime is controlled by `locked`; loopback paths deep-copy packets into `packet_queue`, and response records lock sent packets until the record is removed.

## Dependencies and integration points
This code depends on `nmbd.h` data structures (`packet_struct`, `nmb_packet`, `dgram_packet`, `subnet_record`, `response_record`), subnet globals from `nmbd_subnetdb.c`, response-record helpers from `nmbd_responserecordsdb.c`, WINS handlers from `nmbd_winsserver.c`, normal request handlers from `nmbd_incomingrequests.c`, browse/logon handlers, async DNS, Samba socket utilities, `tevent`, and the `libsmb/unexpected` packet dispatch path.

## Risks and edge cases
- Datagram parsing uses historical SMB offset conventions, including a negative four-byte adjustment before `dgram->data`; bounds checks around `smb_vwv12`, `len`, and `MAX_DGRAM_SIZE` are critical.
- The listen array assumes broadcast sockets are stored immediately after their unicast partner when selecting `send_fd` for replies.
- `response_record` callbacks can remove records while timeout traversal is running, so the restart and `in_expiration_processing` logic prevents use-after-free and recursion.
- Loopback handling depends on correct `locked` semantics and `copy_packet` behavior.
- `queue_query_name` only selects the first active WINS server/tag when the unicast subnet has zero address, which is a known architectural limitation.
- Duplicate suppression is per event-loop iteration and keyed only by packet type, source IP, and packet id.

## Test signals
The most useful signals are integration tests that exercise nmbd registration/query/release, WINS registration conflicts, browser announcements, mailslot logon replies, duplicate broadcast packets, and timeout/retry behavior. Static review should focus on packet length guards, response-record lock/unlock balance, and correct subnet selection for WINS vs broadcast traffic.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_packets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_processlogon.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_processlogon.c

## Purpose
`nmbd_processlogon.c` handles domain logon and domain-controller discovery datagrams received on the NETLOGON mailslots. It decodes NBT netlogon requests, builds the proper legacy or NT4-style response structures, and sends them back as NetBIOS datagram mailslot replies when this Samba instance is acting as a domain controller.

## Important APIs, types, and functions
- `process_logon_packet` is the exported entry point called from the datagram packet dispatcher.
- `delay_logon` checks `init logon delayed hosts` configuration against the client name and address.
- `delayed_init_logon_handler` requeues a locked packet after a `tevent` timer expires.
- Local `sam_database_info` is defined but not used by this file.
- The file relies on generated NDR helpers for `nbt_netlogon_packet` and `nbt_netlogon_response`.

## Control flow
`process_logon_packet` first finds the outgoing local interface for the peer and exits if domain logons are disabled. It decodes the source NetBIOS name and unmarshals the request blob through NDR. It then switches on the request command. `LOGON_REQUEST` returns a `LOGON_RESPONSE2` containing the PDC name. `LOGON_PRIMARY_QUERY` answers only when `domain master` is enabled. `LOGON_SAM_LOGON_REQUEST` returns an NT4 SAM logon response and optionally delays initial empty-user replies by locking the packet and scheduling a timer. Unknown or unsupported commands are logged and ignored.

## State and persistence behavior
The file does not persist state. Its only long-lived behavior is delayed packet ownership: an initial logon packet may be marked `locked`, retained by the timer callback, and then requeued to be processed again. Response content is generated from current runtime configuration such as NetBIOS name, workgroup, domain-master setting, and delay lists.

## Dependencies and integration points
This file integrates with `nmbd_packets.c` via `send_mailslot` and `queue_packet`, the global event loop via `nmbd_event_context`, Samba loadparm accessors, interface lookup helpers, generated NDR netlogon code, and the datagram dispatcher that calls it for `NET_LOGON_MAILSLOT` and `NT_LOGON_MAILSLOT`.

## Risks and edge cases
- Delayed packets depend on correct `locked` handling; mishandling could leak packets or double-free them after requeue.
- The code is only valid for IPv4 `iface_ip` results and returns if no matching outgoing interface is found.
- Empty usernames are treated as initial logons for delay policy; changes to request semantics could alter client-visible logon timing.
- Responses are legacy/NT4 oriented and intentionally sparse compared with modern CLDAP or Kerberos discovery.

## Test signals
Useful tests send NBT netlogon mailslot packets for `LOGON_REQUEST`, `LOGON_PRIMARY_QUERY`, and `LOGON_SAM_LOGON_REQUEST`, with domain-controller mode toggled and delayed-host configuration enabled. Assertions should cover response command/type fields, source/destination mailslot names, PDC/workgroup strings, and the delayed requeue path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_processlogon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_proto.h -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_proto.h

## Purpose
`nmbd_proto.h` is the manually maintained cross-module prototype header for the `source3/nmbd` subsystem. It exposes the functions that let the daemon's name registration, packet routing, WINS, browsing, election, subnet, workgroup, server-list, async DNS, and logon modules call each other.

## Important APIs, types, and functions
- Packet APIs include `queue_*` request builders, `reply_netbios_packet`, `listen_for_packets`, `run_packet_queue`, `retransmit_or_expire_response_records`, and `send_mailslot`.
- WINS APIs include `initialise_wins`, `packet_is_for_wins_server`, `wins_process_*`, `find_name_on_wins_subnet`, `wins_write_database`, and WINS record storage helpers.
- Browse APIs include announcement sending, browser sync, election processing, workgroup/server list management, and remote browse synchronization.
- Name-list APIs expose local name creation, lookup, TTL updates, IP-list mutation, and registration/release success paths.
- Subnet APIs expose normal subnet creation, special subnet iteration, and WINS-client detection.

## Control flow
The header has no executable control flow, but it defines the compile-time linkage graph: packet dispatch calls incoming request/WINS/logon/browse functions; WINS code calls name-query helpers and packet reply functions; announcement and sync code call workgroup and server-list functions; main-loop code calls packet, DNS, election, expiration, and persistence functions.

## State and persistence behavior
The header declares functions that mutate global daemon state but stores no data itself. The exposed functions collectively manage subnet lists, response lists, workgroup/server lists, WINS TDB state, browse.dat/wins.dat persistence, async DNS queues, and event-loop packet queues.

## Dependencies and integration points
Every prototype depends on shared structs and callback typedefs from `nmbd.h` and Samba common headers. This header is the integration surface that compensates for the C subsystem's many mutually dependent modules. The duplicated `queue_dns_query` and `kill_async_dns_child` declarations are visible maintenance artifacts.

## Risks and edge cases
- Prototype drift can silently break builds or hide ABI mismatches in this tightly coupled C subsystem.
- Duplicate declarations make it easier to miss signature changes in async DNS functions.
- Because many APIs operate on global singleton subnet records and lists, the header exposes broad mutation capability rather than narrow ownership boundaries.

## Test signals
The primary signal is a full Samba build with warnings enabled, because this header is compile-time glue. Linkage tests should include configurations with and without async DNS/WINS paths where possible. Runtime coverage comes indirectly from nmbd integration tests that exercise the declared packet, WINS, browse, and logon entry points.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_responserecordsdb.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_responserecordsdb.c

## Purpose
`nmbd_responserecordsdb.c` owns the in-memory database of expected responses for outbound NetBIOS name-service operations. It creates, stores, finds, and removes `response_record` entries attached to subnet records so incoming responses and retry/timeout processing can find the right callbacks and packet state.

## Important APIs, types, and functions
- `make_response_record` allocates and initializes a response record from a sent packet and callback set.
- `remove_response_record` safely removes a response record, frees user data through custom destructors when present, unlocks and frees the held packet, and decrements `num_response_packets`.
- `find_response_record` searches all broadcast subnets, the unicast subnet when configured, and the WINS server subnet.
- `is_refresh_already_queued` detects duplicate queued refreshes for a name.
- `num_response_packets` is the global count used by packet polling to shorten event-loop waits when responses are pending.

## Control flow
Packet senders call `make_response_record` after successful transmission. The record stores the transaction id from the packet header, all response/timeout/success/fail callbacks, optional copied user data, retry interval/count, next retry time, and a locked pointer to the sent packet. Inbound responses call `find_response_record`; timeout handling later removes or retries records through `remove_response_record` or callback-specific logic.

## State and persistence behavior
All state is process-local and hangs from `subnet_record->responselist`. Records own their `userdata` copy and their locked packet. The file intentionally searches before freeing in `remove_response_record` because historical paths could attempt to remove the same record twice. There is no disk persistence.

## Dependencies and integration points
The file depends on `nmbd.h`, list macros, packet allocation/freeing helpers, subnet iteration macros, and callback typedefs. It is used by `nmbd_packets.c`, name registration/query/release modules, WINS proxy, and WINS server conflict-query logic.

## Risks and edge cases
- Incorrect userdata `copy_fn` or `free_fn` implementations can leak or free nested packet pointers incorrectly.
- Response ids are 16-bit transaction ids, so matching is scoped only by list search rather than cryptographic uniqueness.
- Double-remove tolerance avoids one class of crash but can hide ownership bugs.
- `num_response_packets` must stay balanced or the main loop can poll too aggressively or too slowly.

## Test signals
Tests should validate successful response matching, timeout removal, retry cancellation after first response, duplicate remove safety, userdata deep-copy/free behavior, and refresh de-duplication. Instrumented integration tests around name registration and WINS conflict checks are especially valuable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_responserecordsdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_sendannounce.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_sendannounce.c

## Purpose
`nmbd_sendannounce.c` builds and sends NetBIOS datagram announcements for SMB browser service discovery. It announces local servers, local master browser state, workgroups, LanMan compatibility records, remote announce targets, remote browse sync targets, and removal notifications during shutdown.

## Important APIs, types, and functions
- `send_browser_reset` and `broadcast_announce_request` send direct browser control datagrams.
- `announce_my_server_names` emits normal host/local-master/workgroup announcements on each broadcast subnet.
- `announce_my_lm_server_names` emits legacy LanMan announcements when configured or when LM clients are detected.
- `reset_announce_timer` forces earlier domain-master announcements.
- `announce_myself_to_domain_master_browser` triggers DMB announcement and sync when this host is an LMB and WINS client.
- `announce_my_servers_removed` sends zero-type removal announcements during shutdown.
- `announce_remote` and `browse_sync_remote` implement `remote announce` and `remote browse sync` configuration.

## Control flow
The public timer-driven functions inspect subnet workgroups and server records, decide whether the relevant interval has elapsed, build browser payloads with the expected command byte/word layout, then send them through `send_mailslot`. Normal host announcements ramp from one minute toward a twelve-minute interval and reset when `needannounce` is set. Remote announce parsing walks configured `IP[/WORKGROUP]` tokens and sends announcements for all configured NetBIOS names. Remote browse sync sends a master announcement only if this node is the local master browser for its workgroup on the first subnet.

## State and persistence behavior
The file mutates in-memory browser timing state: `work->needannounce`, `work->announce_interval`, `work->lastannounce_time`, static `announce_timer_last`, and static remote announce/sync timestamps. It consumes `updatecount` from the server-list database as the browser update counter. Persistent browser list output is handled in `nmbd_serverlistdb.c`, not here.

## Dependencies and integration points
This module depends on `send_mailslot`, subnet/workgroup/server-list structures, `my_netbios_names`, loadparm values such as `lm announce`, `lm interval`, `remote announce`, `remote browse sync`, and browser-sync functions from `nmbd_browsesync.c`. It uses generated service type constants and Samba string helpers for uppercase NetBIOS names and bounded comments.

## Risks and edge cases
- Browser datagram payloads are fixed-format; off-by-one errors in `push_string_check` or interval units would affect legacy browser interoperability.
- `FIRST_SUBNET` is used for some remote operations and source IPs, so unusual multi-interface deployments may announce a nonideal address.
- LanMan auto mode depends on `found_lm_clients`; environments with silent LM clients may not get legacy announcements.
- Shutdown removal only announces known local names in current workgroup lists.

## Test signals
Useful tests inspect emitted mailslot payloads for host, local master, workgroup, LM, remote announce, remote browse sync, reset, and removal paths. Timer tests should check interval ramping, `needannounce` reset behavior, and the local-master/domain-master gating conditions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_sendannounce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_serverlistdb.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_serverlistdb.c

## Purpose
`nmbd_serverlistdb.c` manages per-workgroup server records and writes Samba's browser service list cache. It adds, updates, expires, removes, de-duplicates, and serializes `server_record` entries into `browse.dat` for consumers such as `smbd`.

## Important APIs, types, and functions
- `remove_all_servers`, `remove_server_from_workgroup`, `create_server_on_workgroup`, `find_server_in_workgroup`, `update_server_ttl`, and `expire_servers` manage the in-memory server list on a `work_record`.
- `write_browse_list_entry` writes one formatted browser cache row.
- `write_browse_list` is the persistence entry point that writes the server list cache when forced or when subnet work changed.
- `updatecount` is the global browser update counter used by announcement code.

## Control flow
Incoming browse announcements or sync completions create/update server records through this file. TTL updates clamp remote records to `lp_max_ttl`, multiply normal TTLs by three for death time, and keep Samba-owned names permanent. Periodic or forced writes first dump workgroups, check `work_changed`, increment `updatecount`, write a temporary cache file, output the local workgroup, merge Samba's own names across subnets, then walk each subnet/workgroup/server while suppressing duplicates. The temp file replaces `browse.dat` by unlink/rename.

## State and persistence behavior
The authoritative runtime state is each `work_record->serverlist` and `subnet_record->work_changed`. `write_browse_list` persists a derived view to `cache_path(SERVER_LIST)`. It resets `work_changed` flags after writing and updates static `lasttime` to avoid excessive writes.

## Dependencies and integration points
This file integrates with workgroup lookup from `nmbd_workgroupdb.c`, local name enumeration from `nmbd_mynames.c`, server type constants, loadparm server-string substitution, cache-path helpers, and announcement code through `updatecount` and server records.

## Risks and edge cases
- The output format is legacy text consumed by other Samba pieces; field order and quoting matter.
- Duplicate suppression gives precedence to broadcast-subnet records over unicast sync records, which can hide newer remote data.
- `write_browse_list` unlinks and renames without fsync; abrupt power loss could lose the cache file.
- `create_server_on_workgroup` treats duplicate creation as a bug rather than updating in place.

## Test signals
Tests should cover TTL clamping/expiration, duplicate server suppression across subnets, self-name merge behavior, `work_changed` driven writes, forced writes, and `browse.dat` formatting. Integration tests can validate that browser clients see expected server/workgroup records after announcements and syncs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_serverlistdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_subnetdb.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_subnetdb.c

## Purpose
`nmbd_subnetdb.c` constructs and manages nmbd's subnet database. It opens IPv4 UDP sockets for normal broadcast subnets, creates special unicast, remote-broadcast, and WINS-server subnet records, and provides subnet iteration helpers used by packet routing and response timeout processing.

## Important APIs, types, and functions
- Global subnet roots are `subnetlist`, `unicast_subnet`, `remote_broadcast_subnet`, and `wins_server_subnet`.
- `make_normal_subnet` creates a socket-backed `NORMAL_SUBNET` from an interface.
- `create_subnets` waits for IPv4 non-loopback interfaces, creates normal subnets, then creates special subnets.
- `close_subnet` closes sockets and removes a normal subnet from the global list without freeing the record.
- `we_are_a_wins_client`, `get_next_subnet_maybe_unicast`, and `get_next_subnet_maybe_unicast_or_wins_server` guide iteration across special subnets.

## Control flow
Startup calls `create_subnets`. It waits until at least one IPv4 non-loopback interface exists, loops through all interfaces while ignoring IPv6 and loopback entries, and calls `make_normal_subnet` for each. Normal subnet creation binds NMB and DGRAM UDP sockets on the interface IP, optionally binds explicit broadcast sockets, enables broadcast, and marks sockets nonblocking. After normal subnets exist, it creates socketless special subnets. If Samba is a WINS server, the unicast subnet gets the first IPv4 interface address and a WINS-server subnet is created.

## State and persistence behavior
The module owns process-global subnet records and socket descriptors. It does not persist data to disk. Subnet records hold mutable child state owned by other modules, including name lists, workgroup lists, response lists, and change flags. `close_subnet` intentionally does not free records because response records may still reference them.

## Dependencies and integration points
It depends on interface discovery/loading, socket helpers, loadparm settings (`nmbd bind explicit broadcast`, WINS server/client configuration), `global_nmb_port`, and linked-list macros. It is consumed by packet listening/routing, name registration, WINS, browser database code, and any loop using `FIRST_SUBNET` or `NEXT_SUBNET_*` macros.

## Risks and edge cases
- nmbd is IPv4-only here; lack of IPv4 non-loopback interfaces makes startup wait and retry.
- Socket creation failure on one interface aborts subnet creation.
- Special subnets are not on `subnetlist`, so every enumeration path must use the correct helper macro.
- `close_subnet` removes but does not free records, which avoids dangling response references but can leak until process exit.

## Test signals
Signals include startup tests with multiple IPv4 interfaces, loopback-only systems, bind-interface-only modes, explicit broadcast binding, WINS server/client combinations, and subnet iteration tests that verify unicast/WINS special records are included only where expected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_subnetdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_synclists.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_synclists.c

## Purpose
`nmbd_synclists.c` implements asynchronous browse-list synchronization with remote browse servers. It forks children that connect over SMB/NBT to a remote IPC$ share, run NetServerEnum calls, write temporary sync results, and later merges completed results into the unicast subnet's workgroup and server lists.

## Important APIs, types, and functions
- `sync_browse_lists` starts one asynchronous sync operation and records it in a linked list of `sync_record` entries.
- `sync_check_completion` detects finished child processes and merges their result files.
- `sync_child` performs the remote SMB connection, anonymous session setup, IPC$ tree connect, and NetServerEnum calls.
- `complete_sync` reads a child result file; `complete_one` applies one workgroup or server row.
- `callback` is the NetServerEnum callback that writes rows to the child output file.

## Control flow
Callers request a sync for a workgroup/server/IP. The parent skips self IPs, allocates a `sync_record`, creates a unique lock-directory filename, links the record into `syncs`, forks, and returns. The child opens the output file, connects to the remote server using forced NBT transport, negotiates SMB up to NT1, performs anonymous IPC$ access, enumerates domains and optionally servers, writes quoted rows, and exits. Periodic completion checks detect exited children, parse output rows, update or create workgroups/servers on `unicast_subnet`, delete the file, and free the record.

## State and persistence behavior
Runtime state is the `syncs` linked list and per-sync temporary files named `sync.N` in the lock directory. Merge results mutate the unicast subnet's workgroup and server lists with max TTLs. Temporary files are deleted after successful read; failed child setup can leave an empty file until completion cleanup.

## Dependencies and integration points
The file integrates with Samba client libraries (`cli_connect_nb`, `smbXcli_negprot`, `cli_session_setup_anon`, `cli_tree_connect`, `cli_NetServerEnum`), workgroup/server-list APIs, lock-directory configuration, process management helpers, and string/token parsing utilities.

## Risks and edge cases
- Forked children isolate blocking SMB calls but require correct child reaping and temp-file cleanup.
- The global `fp` is process-global but only used inside the child after fork; future threading would make that unsafe.
- Sync result parsing depends on quoted token format matching `callback`.
- SMB1/NT1 and anonymous IPC$ requirements may fail against hardened modern servers.
- `process_exists_by_pid` based completion can race with pid reuse in long-running processes.

## Test signals
Tests should cover child-output parsing, server/workgroup merge behavior, self-IP skip, failed connection cleanup, and stale sync file handling. Integration coverage needs a controllable SMB browse server that returns domain and server lists over NBT port 139.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_synclists.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_winsproxy.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_winsproxy.c

## Purpose
`nmbd_winsproxy.c` implements WINS proxy behavior for broadcast name queries. When a broadcast client asks for a name not known locally, nmbd can query its configured WINS server, cache the result on the original broadcast subnet as a proxy name, and answer the original broadcast query when appropriate.

## Important APIs, types, and functions
- `make_wins_proxy_name_query_request` is the exported entry point. It packages the original subnet and packet into userdata and starts a unicast WINS query.
- `wins_proxy_name_query_request_success` caches successful WINS answers and replies to the original packet.
- `wins_proxy_name_query_request_fail` logs WINS lookup failure.
- `wins_proxy_userdata_copy_fn` and `wins_proxy_userdata_free_fn` deep-copy and free the original packet held while the async query is outstanding.

## Control flow
The caller passes the broadcast subnet, incoming packet, and queried name. The file builds custom userdata containing the subnet pointer and incoming packet pointer, with copy/free hooks. `query_name` on `unicast_subnet` sends the actual WINS query. On success, the callback extracts NB flags/IPs from the returned resource record, adds a `WINS_PROXY_NAME` record to the original broadcast subnet, suppresses a reply if any returned IP is on the same subnet as the requester, and otherwise replies to the saved original packet with the returned rdata.

## State and persistence behavior
The file persists no disk state. It mutates the broadcast subnet's in-memory name list by adding WINS proxy cache entries with one-hour default TTL or `lp_max_ttl` for permanent WINS responses. The original packet is deep-copied and locked in userdata until callback cleanup.

## Dependencies and integration points
It integrates with name querying (`query_name`), name-list insertion/lookup, packet replies, NetBIOS flag helpers, subnet masks, WINS client configuration through the unicast subnet, and response-record userdata ownership rules.

## Risks and edge cases
- If a WINS response contains multiple IPs, all rdata entries must parse correctly in six-byte chunks.
- Reply suppression for same-subnet IPs avoids duplicate answers but still caches the name; incorrect subnet masks can suppress valid replies.
- The userdata union uses manual sizing and pointer serialization, so structure-size mistakes would corrupt saved pointers.
- Packet deep-copy/free must stay balanced with response-record lifecycle.

## Test signals
Good tests simulate successful and failed WINS responses, single and multi-IP rdata, same-subnet suppression, cache insertion as `WINS_PROXY_NAME`, and cleanup of the saved packet after response-record removal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_winsproxy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_winsserver.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_winsserver.c

## Purpose
`nmbd_winsserver.c` implements Samba nmbd's WINS server. It stores WINS records in `wins.tdb`, imports/exports the legacy `wins.dat` text file, handles WINS name registration/refresh/query/release/multihomed registration packets, maintains WINS record lifecycle states, invokes optional hooks on changes, and periodically ages and writes the database.

## Important APIs, types, and functions
- TDB conversion helpers: `wins_record_to_name_record`, `name_record_to_wins_record`, and `name_to_key`.
- Storage APIs: `find_name_on_wins_subnet`, `wins_store_changed_namerec`, `add_name_to_wins_subnet`, `remove_name_from_wins_namelist`, and `dump_wins_subnet_namelist`.
- Initialization and routing: `initialise_wins` and `packet_is_for_wins_server`.
- Request handlers: `wins_process_name_refresh_request`, `wins_process_name_registration_request`, `wins_process_multihomed_name_registration_request`, `wins_process_name_query_request`, and `wins_process_name_release_request`.
- Response helpers: `send_wins_name_query_response`, registration/release response helpers, and WACK handling.
- Maintenance: `fetch_all_active_wins_1b_names`, `initiate_wins_processing`, `wins_write_name_record`, and `wins_write_database`.

## Control flow
Startup opens `state_path("wins.tdb")`, stores the database version, adds Samba self names, and imports valid `wins.dat` rows that still have enough TTL. Incoming unicast WINS packets are selected by `packet_is_for_wins_server` and dispatched from the packet layer. Refresh requests update active records, take ownership of replicas when needed, or fall back to registration if missing. Registration handles static-name protection, group vs unique policy, special 0x1c and 0x1d behavior, owner conflict WACK/query challenges, and record creation. Multihomed registration follows similar checks but can add IPs after querying the existing owner. Queries return active records, special `*<1b>` domain master browser lists, or optional DNS proxy results. Releases validate source IP ownership, remove one IP for multi-IP 0x1c names, or mark records released with extinction TTL.

## State and persistence behavior
The authoritative WINS database is `wins_tdb`; the in-memory `wins_server_subnet->namelist` is used as temporary/cache material for fetched records and special traversals. Records carry NB flags, source, death/refresh times, version id, WINS owner IP, WINS state flags, and IP arrays. `wins_hook` stores changed records and optionally runs an external command for add/refresh/delete events. Periodic processing moves records through active, released, tombstoned, and deleted states and writes `wins.dat` in a background child at most every 120 seconds when requested.

## Dependencies and integration points
This file depends on TDB packing/unpacking, Samba name-list operations, packet reply helpers, name-query helpers for conflict challenges, async DNS proxying, loadparm TTL/hook/WINS settings, state-path helpers, child process handling, and subnet globals. It is the WINS-specific branch reached from `nmbd_packets.c` and feeds query responses to WINS proxy/name service code.

## Risks and edge cases
- WINS record packing is binary and versioned only by convention; field order and key encoding must remain stable for existing `wins.tdb`.
- `name_to_key` uses a static buffer, so callers must not retain or concurrently reuse the returned key across nested operations.
- Many paths fetch a malloced temporary record from TDB and then remove it from the subnet list; ownership and `data.ip` freeing are easy to get wrong.
- Group 0x1c lists are capped to avoid oversized NetBIOS replies, with special preservation logic for 0x1b PDC addresses.
- WACK/conflict resolution locks original packets across asynchronous query callbacks.
- `wins_hook` builds and runs a shell command after validating only the NetBIOS name characters; hook configuration remains security-sensitive.
- Background `wins_write_database` forks and reopens TDB; failures are logged but do not stop the parent.

## Test signals
High-value tests cover TDB serialization round trips, legacy `wins.dat` import/export, registration of unique/group/0x1c/0x1d names, refresh ownership changes, conflict WACK and query-success/query-fail paths, multihomed additions, special `*<1b>` queries, DNS proxy fallback, release state transitions, periodic active-to-released-to-tombstoned-to-delete aging, hook invocation gating, and maximum multi-IP query response sizing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_winsserver.c -->
