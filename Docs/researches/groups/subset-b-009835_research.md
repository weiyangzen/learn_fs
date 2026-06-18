# subset-b-009835 Research

Grouped research for the listed Samba `source3/nmbd` files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_become_dmb.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_become_dmb.c

## Purpose
Implements the state machine for becoming a NetBIOS Domain Master Browser (DMB) for the configured workgroup. DMB ownership is represented by the `WORKGROUP<1b>` name. The file coordinates WINS-first registration when Samba is a WINS client and broadcast registration when it is not, then updates workgroup/server state so browser synchronization can use the new DMB role.

## Important APIs, Types, And Functions
The code operates on `struct subnet_record`, `struct work_record`, `struct server_record`, `struct nmb_name`, and asynchronous `struct response_record` callbacks from the name-query and registration layers. Public entry point `add_domain_names(time_t t)` periodically adds domain logon names and DMB names. Internal stages include `become_domain_master_browser_wins()`, `become_domain_master_browser_bcast()`, `become_domain_master_query_success()`, `become_domain_master_query_fail()`, `become_domain_master_stage1()`, `become_domain_master_stage2()`, and `become_domain_master_fail()`. It depends on the global `samba_nb_type` and macros such as `IS_DC`, `DOMAIN_NONE`, `DOMAIN_WAIT`, and `DOMAIN_MST`.

## Control Flow
`add_domain_names()` is timer-gated by `CHECK_TIME_ADD_DOM_NAMES`. If Samba is a domain controller it first calls `add_logon_names()`. If `lp_domain_master()` is true, it either queries/ registers `WORKGROUP<1b>` through WINS on `unicast_subnet`, or broadcasts per local subnet. Both paths query for an existing DMB name before registration. Query success is normally a conflict, but responses containing one of Samba's own IPs, all-ones broadcast, or zero are tolerated for compatibility with old Samba behavior and continue to stage 1. Query failure is expected unless a unicast WINS query returns an error other than `NAM_ERR`. Stage 1 sets `work->dom_state = DOMAIN_WAIT` and calls `register_name()` for `<1b>`. Stage 2 marks `DOMAIN_MST`, adds `SV_TYPE_NT | SV_TYPE_DOMAIN_MASTER`, flags `subrec->work_changed`, and either cascades WINS success to broadcast subnets or inserts the broadcast DMB name into `unicast_subnet`.

## State And Persistence
Primary mutable state is in `work->dom_state`, the local server record's service type bits, `work->dmb_name`, `work->dmb_addr`, and `subrec->work_changed`. Registration success also creates or updates `SELF_NAME` and `PERMANENT_NAME` records through `register_name()` and `insert_permanent_name_into_unicast()`. The namelist writer is signaled by `work_changed`; WINS/unicast name data ultimately persists in nmbd's namelist/WINS storage layers, not in this file.

## Dependencies And Integration Points
This file integrates with `nmbd_nameregister.c` for asynchronous name registration, `nmbd_namequery.c` for conflict probing, `nmbd_become_lmb.c` for `insert_permanent_name_into_unicast()`, `nmbd_logonnames.c` for `<1c>` logon names, and browser sync code that later reads `work->dmb_name` and `work->dmb_addr`. It uses configuration APIs including `lp_domain_master()`, `lp_workgroup()`, `lp_netbios_name()`, `we_are_a_wins_client()`, and interface helpers such as `first_ipv4_iface()`.

## Risks And Test Signals
Risk is concentrated in asynchronous state rollback: failures must clear `DOMAIN_WAIT`, remove `SV_TYPE_DOMAIN_MASTER`, and mark changed state consistently. Multi-interface DMB behavior depends on selecting the first IPv4 interface when WINS registration succeeds. Compatibility hacks for old Samba responses can hide real conflicts. Useful test signals include simulated WINS success/failure for `WORKGROUP<1b>`, broadcast conflict responses, verification that `work->dom_state` reaches `DOMAIN_MST`, and inspection of `namelist.debug` or browse lists after `subrec->work_changed`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_become_dmb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_become_lmb.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_become_lmb.c

## Purpose
Implements the local master browser (LMB) promotion and demotion paths for a workgroup on a broadcast subnet. LMB ownership is represented by the special `__MSBROWSE__<01>` group name and the `WORKGROUP<1d>` unique name. The file also maintains permanent unicast-subnet aliases so directed unicast queries for local-master names still resolve in broadcast-only configurations.

## Important APIs, Types, And Functions
Public APIs are `become_local_master_browser()`, `unbecome_local_master_browser()`, `insert_permanent_name_into_unicast()`, and `set_workgroup_local_master_browser_name()`. The main callbacks are `become_local_master_stage1()`, `become_local_master_stage2()`, `become_local_master_fail1()`, `become_local_master_fail2()`, `unbecome_local_master_success()`, `unbecome_local_master_fail()`, `release_msbrowse_name_success()`, and `release_msbrowse_name_fail()`. It manipulates `struct work_record::mst_state`, `ElectionCriterion`, `local_master_browser_name`, `struct server_record::serv.type`, and `struct name_record` entries.

## Control Flow
Promotion starts only when `lp_local_master()` is enabled and `AM_POTENTIAL_MASTER_BROWSER(work)` is true. `become_local_master_browser()` sets `MST_BACKUP`, raises election criterion bits, copies the workgroup into callback userdata, and registers `__MSBROWSE__<01>` as a group name. Stage 1 confirms the workgroup still exists, sets `MST_MSB`, mirrors the MSBROWSE name to `unicast_subnet`, then registers `WORKGROUP<1d>`. Stage 2 marks `MST_BROWSER`, updates server type bits from potential to master browser, sets the local master browser name to `lp_netbios_name()`, asks servers to announce if the list is small, mirrors `<1d>` to unicast, resets the announce timer, and logs the role transition.

Demotion sets `MST_UNBECOMING_MASTER`, releases `WORKGROUP<1d>`, releases `__MSBROWSE__<01>` if present, and immediately processes response records to avoid handling election traffic before the release path settles. Both release success and failure paths call `reset_workgroup_state()`, which clears master-browser bits, restores `MST_POTENTIAL` or `MST_NONE`, clears the local master name, removes the subnet IP from the unicast `<1d>` record, and optionally forces a new election.

## State And Persistence
The file updates workgroup state, election flags, server service type bits, and namelist entries. `insert_permanent_name_into_unicast()` uses the IP list of a unicast `PERMANENT_NAME` as a reference count across broadcast subnets. Removing a subnet role removes only that subnet IP, deleting the name if no IPs remain. `subrec->work_changed` signals browse-list persistence, while namelist changes are handled by the lower-level namelist routines.

## Dependencies And Integration Points
Promotion and demotion depend on `register_name()` and `release_name()` from the name registration/release modules, `find_workgroup_on_subnet()`, `find_server_in_workgroup()`, `find_name_on_subnet()`, and `remove_name_from_namelist()`. It is called from election logic after a win, from incoming local-master announcements when a conflict is detected, from browser reset handling, and from shutdown/role-change paths.

## Risks And Test Signals
Important risks include stale userdata in asynchronous callbacks, inconsistent unicast reference counting for multi-homed hosts, and forced demotion races with elections. Failure callbacks intentionally remove names and reset state even if network release fails; tests should verify that behavior. Useful signals are election-to-LMB transition logs, presence and removal of `__MSBROWSE__<01>` and `WORKGROUP<1d>` in namelists, `SV_TYPE_MASTER_BROWSER` bit changes, and browse-list rewrite triggers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_become_lmb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_browserdb.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_browserdb.c

## Purpose
Maintains the in-memory cache of local master browsers known to this nmbd when acting as a domain master browser. The cache drives later DMB-to-LMB browse-list synchronization and expires LMB entries that stop announcing themselves.

## Important APIs, Types, And Functions
The file owns global `struct browse_cache_record *lmb_browserlist`. Public functions are `create_browser_in_lmb_cache()`, `find_browser_in_lmb_cache()`, `update_browser_death_time()`, and `expire_lmb_browsers()`. Internal `remove_lmb_browser_entry()` unlinks and frees a cache node. Records store uppercased LMB name, workgroup, IP address, next `sync_time`, and `death_time`.

## Control Flow
`create_browser_in_lmb_cache()` allocates a record, schedules first sync one minute in the future, sets death time to `CHECK_TIME_MST_ANNOUNCE + 2` minutes, uppercases the browser and workgroup names, stores the IP, and appends the entry. `find_browser_in_lmb_cache()` performs a linear name lookup. `update_browser_death_time()` extends the entry when another master announcement arrives. `expire_lmb_browsers(t)` scans the list and removes entries whose death time is older than `t`.

## State And Persistence
All state is process-local memory. There is no disk persistence from this file. The cache acts as a derived view of incoming master-browser announcements. Expiry and synchronization state is time-based and lost on restart.

## Dependencies And Integration Points
`nmbd_incomingdgrams.c` calls `find_browser_in_lmb_cache()`, `create_browser_in_lmb_cache()`, and `update_browser_death_time()` when processing local-master announcements received by a DMB. `nmbd_browsesync.c` calls `expire_lmb_browsers()` and iterates `lmb_browserlist` to schedule `sync_browse_lists()` calls. It depends on Samba DLIST macros, allocation wrappers, `strupper_m()`, and timing constants.

## Risks And Test Signals
This cache is keyed only by browser name, so same-named LMBs in different workgroups or scopes would collide. Uppercase conversion failure frees the record and silently drops the cache update. Test signals include creating and refreshing announcements, observing `death_time` extension, expiry after timeout, and subsequent DMB-to-LMB sync attempts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_browserdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_browsesync.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_browsesync.c

## Purpose
Coordinates browser-list synchronization between local master browsers and domain master browsers. It covers three flows: a DMB periodically syncing from cached LMBs, an LMB finding and syncing with its DMB through WINS, and a DMB discovering/syncing with other DMB workgroups registered in WINS.

## Important APIs, Types, And Functions
Public timer/entry functions are `dmb_expire_and_sync_browser_lists()`, `announce_and_sync_with_domain_master_browser()`, `collect_all_workgroup_names_from_wins_server()`, and `sync_all_dmbs()`. Important internal functions include `sync_with_lmb()`, `announce_local_master_browser_to_domain_master_browser()`, `sync_with_dmb()`, `domain_master_node_status_success()`, `find_domain_master_name_query_success()`, `get_domain_master_name_node_status_success()`, and `find_all_domain_master_names_query_success()`.

## Control Flow
As a DMB, `dmb_expire_and_sync_browser_lists()` runs at most every 20 seconds, expires stale `lmb_browserlist` entries, and calls `sync_with_lmb()` for records whose `sync_time` has passed. `sync_with_lmb()` confirms that the matching unicast workgroup exists and that this server is actually the DMB before calling `sync_browse_lists()` against the LMB's `<20>` server name.

As an LMB, `announce_and_sync_with_domain_master_browser()` requires WINS client mode, then queries `WORKGROUP<1b>` on `unicast_subnet`. If the returned IP matches the cached DMB IP, it immediately announces and syncs. Otherwise it performs a node-status request against `WORKGROUP<1b>`, finds a non-group `<20>` name in the answer, caches that as `work->dmb_name`/`dmb_addr`, sends an `ANN_MasterAnnouncement` to `BROWSE_MAILSLOT`, and syncs.

For cross-workgroup discovery, `collect_all_workgroup_names_from_wins_server()` runs only for a DMB on the unicast subnet and at most every 15 minutes. It queries `*<1b>`, sends node-status requests to each returned DMB IP except itself, and adds discovered workgroups to the unicast subnet. `sync_all_dmbs()` runs at most every 5 minutes and randomly selects among known foreign workgroups to avoid exponential DMB-to-DMB sync traffic.

## State And Persistence
The file mutates `browse_cache_record::sync_time`, `work->dmb_name`, `work->dmb_addr`, `work->local_master_browser_name`, and the unicast workgroup list. It creates transient `userdata_struct` instances for async node-status callbacks. Persistent effects are indirect: newly created workgroups and changed browser lists may be written by workgroup/server database code.

## Dependencies And Integration Points
It integrates with `nmbd_browserdb.c` for LMB cache expiry, `nmbd_namequery.c` for WINS name queries, `nmbd_nodestatus.c` for node-status resolution, mailslot datagram sending, and the browser synchronization implementation behind `sync_browse_lists()`. It relies on WINS client configuration and on `AM_DOMAIN_MASTER_BROWSER()` to gate DMB-only work.

## Risks And Test Signals
Risks include stale cached DMB names, reliance on node-status parsing heuristics, and expensive WINS-wide discovery if throttling fails. The DMB-to-DMB randomization means tests must control randomness or assert probabilistic behavior carefully. Test signals include `ANN_MasterAnnouncement` packets, node-status callbacks extracting `<20>` and `<1b>` names, `sync_browse_lists()` invocations with correct `local`/`announce` flags, and throttling by the static `lastrun` fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_browsesync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_elections.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_elections.c

## Purpose
Implements NetBIOS browser election behavior for local master browser selection. It checks whether a master browser exists, initiates elections when needed, sends election mailslot datagrams, compares local and remote election criteria, and promotes or demotes Samba based on election results.

## Important APIs, Types, And Functions
Public functions are `check_master_browser_exists()`, `run_elections()`, `process_election()`, `check_elections()`, and `nmbd_message_election()`. Internal helpers include `send_election_dgram()`, `check_for_master_browser_success()`, `check_for_master_browser_fail()`, and `win_election()`. It uses `struct work_record` fields `RunningElection`, `needelection`, `ElectionCount`, `ElectionCriterion`, and `mst_state`, plus global `StartupTime`.

## Control Flow
`check_master_browser_exists()` runs periodically using `CHECK_TIME_MST_BROWSE`, dumps workgroup state, and queries `WORKGROUP<1d>` on each broadcast subnet where Samba is not already LMB. Query failure forces an election if `lp_local_master()` is enabled, otherwise it sends a zero-criterion election datagram to stimulate another host.

`check_elections()` scans workgroups and starts an election when `needelection` is set and the `WORKGROUP<1e>` name is registered locally. `run_elections()` sends election datagrams at most every two seconds for each running election. After four uncontested sends, it declares a win, clears `RunningElection`, and calls `become_local_master_browser()`.

`process_election()` parses incoming `ANN_Election` datagrams, finds the target workgroup, ignores workgroups other than `lp_workgroup()`, and uses `win_election()` to compare election version, criterion, uptime, and server name. If Samba wins comparison, it starts or continues an election. If Samba loses, it clears election flags and unbecomes LMB when currently master.

## State And Persistence
Election state is in-memory on `work_record`. Promotion/demotion effects are delegated to `nmbd_become_lmb.c`, which updates name registrations and server records. `nmbd_message_election()` lets internal Samba messaging force elections by setting `needelection`, resetting `ElectionCount`, and resetting master state according to `lp_local_master()`.

## Dependencies And Integration Points
This file depends on name querying, mailslot datagram sending, `WORKGROUP<1e>` registration from workgroup startup, and LMB promotion/demotion APIs. It consumes configuration from `lp_local_master()`, `lp_workgroup()`, `lp_netbios_name()`, and `lp_os_level()` indirectly through `ElectionCriterion` initialization.

## Risks And Test Signals
Election correctness depends on exact comparison order and on `WORKGROUP<1e>` registration gating sends. Time-based throttling and four-packet win logic are easy to regress. Test signals include forced election messages, incoming election packets with higher/lower criteria, demotion after losing while master, no election packets before `<1e>` registration, and promotion after four uncontested `run_elections()` cycles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_elections.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_incomingdgrams.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_incomingdgrams.c

## Purpose
Handles browser-service datagram payloads received on the NetBIOS datagram path, mostly mailslot `\\MAILSLOT\\BROWSE` announcements and requests. It updates workgroup/server browse databases, detects local-master conflicts, queues DMB synchronization, answers backup-browser list requests, processes diagnostic browser resets, and reacts to LanMan announcement traffic.

## Important APIs, Types, And Functions
Public packet handlers include `process_host_announce()`, `process_workgroup_announce()`, `process_local_master_announce()`, `process_master_browser_announce()`, `process_lm_host_announce()`, `process_get_backup_list_request()`, `process_reset_browser()`, `process_announce_request()`, and `process_lm_announce_request()`. Internal `send_backup_list_response()` builds `ANN_GetBackupListResp`. The disabled `tell_become_backup()` block documents an unused backup-browser promotion idea.

## Control Flow
Host announcements parse TTL, server name, server type, and comment, normalize wrong destination-name behavior from old clients, create or update workgroups and server records, or remove a server when type is zero. Workgroup announcements must target `__MSBROWSE__<01>` and update the workgroup TTL and local master name. Local-master announcements must target `WORKGROUP<1e>`; if Samba believes it is already LMB, it sends a Samba browser reset to the peer, unbecomes LMB, and forces a new election. Otherwise it updates the server record and `work->local_master_browser_name`.

`process_master_browser_announce()` is the DMB-facing path for LMB announcements. It verifies `lp_domain_master()`, finds the local workgroup, checks `AM_DOMAIN_MASTER_BROWSER()`, then creates or refreshes an `lmb_browserlist` cache entry that `nmbd_browsesync.c` will later sync. LanMan host announcements accept only OS/2 Warp version fields, then update browse records and set `found_lm_clients`. Backup-list requests are answered only for Samba's workgroup and only when addressed to `<1b>` while DMB or `<1d>` while LMB. Reset packets can force demotion and/or expire browse lists.

## State And Persistence
This file mutates `work_record` and `server_record` lists, TTLs, comments, local master names, `subrec->work_changed`, the global `found_lm_clients`, the LMB browser cache, and LMB/DMB role state through integration calls. Persistence is indirect through browse database writers triggered by `work_changed` and through name-release paths called during demotion.

## Dependencies And Integration Points
It depends on server/workgroup database helpers, election and LMB demotion APIs, `send_mailslot()`, `send_browser_reset()`, `create_browser_in_lmb_cache()`, `update_browser_death_time()`, and configuration such as `lp_workgroup()` and `lp_domain_master()`. It is the bridge between raw datagram dispatch and the higher-level browser state machines.

## Risks And Test Signals
Risks include accepting malformed legacy announcements, conflicts that cause unnecessary demotion/election churn, and buffer parsing assumptions for LanMan variable strings. Backup-list responses currently always include at least Samba's own name and do not enumerate real backup browsers due disabled code. Test signals include browse database changes after announcements, forced demotion on duplicate LMB announcement, DMB cache creation on master announcements, backup-list mailslot responses, reset behavior expiring non-permanent servers, and `found_lm_clients` toggling after LanMan traffic.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_incomingdgrams.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_incomingrequests.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_incomingrequests.c

## Purpose
Processes incoming NetBIOS name-service requests on port 137 for broadcast and local unicast behavior outside the WINS server request path. It responds to name release attempts against Samba-owned names, logs refresh/registration requests, builds node-status replies, resolves name queries from local namelists, and optionally acts as a WINS proxy.

## Important APIs, Types, And Functions
Public handlers are `process_name_release_request()`, `process_name_refresh_request()`, `process_name_registration_request()`, `process_node_status_request()`, and `process_name_query_request()`. Internal helpers are `send_name_release_response()`, `send_name_registration_response()`, and `status_compare()`. Core types are `struct packet_struct`, `struct nmb_packet`, `struct name_record`, and `struct subnet_record`.

## Control Flow
Name release handling requires broadcast input; unicast releases receive `FMT_ERR`. Broadcast group releases by other hosts are ignored, with a workaround for FTP OnNet clients that omit the group bit for `WORKGROUP<00>` and `<1e>`. If a release targets a `SELF_NAME` or `PERMANENT_NAME`, Samba rejects it with `ACT_ERR`; otherwise it stays silent.

Name refresh handling similarly rejects unexpected unicast refreshes and only logs broadcast refreshes. Name registration handling rejects unicast registrations, removes stale WINS proxy records before evaluating conflicts, rejects attempts to register over Samba-owned or group/unique-incompatible names, and updates existing non-owned unique records. For broadcast registration, silence is success.

Node status handling replies only when the requested name is a local self name. It builds a sorted list of active `SELF_NAME` and `PERMANENT_NAME` entries from the subnet and then the unicast subnet, filters magic names and browser suffixes where appropriate, removes duplicates, zeroes the statistics area, and sends a `NMB_STATUS` response. Name query handling searches the current subnet or all broadcast subnets for remote-broadcast input, suppresses expired records, replies to unicast queries and allowed broadcast cases, sorts returned IPs, launches WINS proxy lookup when configured, and avoids negative broadcast responses.

## State And Persistence
This module mostly reads state but can remove WINS proxy names, update existing remote unique name TTL/IP data, and trigger WINS proxy queries that later populate the namelist. It does not persist directly; namelist modifications set change flags through lower-level helpers.

## Dependencies And Integration Points
It relies on namelist APIs from `nmbd_namelistdb.c`, WINS proxy query creation, `reply_netbios_packet()`, NetBIOS flag encoding helpers, IP sort logic, and configuration `lp_wins_proxy()`, `we_are_a_wins_client()`, `lp_max_ttl()`, `lp_workgroup()`, and `lp_netbios_name()`. Query and node-status clients elsewhere in nmbd depend on these replies when WINS validates multihomed registrations or browsers discover peer names.

## Risks And Test Signals
Risk areas are packet structure assumptions, exact broadcast silence semantics, and avoiding duplicate replies when a WINS proxy name is on the requester's local subnet. Node-status output must remain bounded by `MAX_DGRAM_SIZE` and must avoid exposing statistics. Test signals include ACT_ERR on attempts to release Samba-owned names, no negative broadcast query responses, WINS proxy query creation on misses, correct node-status filtering/sorting, and directed unicast query behavior with recursion desired set.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_incomingrequests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_lmhosts.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_lmhosts.c

## Purpose
Loads static NetBIOS name mappings from an `lmhosts` file into nmbd namelists and provides lookup support for those static entries. The mappings supplement dynamic broadcast/WINS discovery, especially for remote names.

## Important APIs, Types, And Functions
Public APIs are `load_lmhosts_file(const char *fname)` and `find_name_in_lmhosts(struct nmb_name *, struct name_record **)`. It uses `startlmhosts()`, `getlmhostsent()`, and `endlmhosts()` from the lmhosts parser, `struct sockaddr_storage`, `struct in_addr`, `enum name_source LMHOSTS_NAME`, and `add_name_to_subnet()`.

## Control Flow
`load_lmhosts_file()` opens the file and iterates parsed entries under a talloc context. Non-IPv4 entries are skipped. For each IPv4 address, it chooses the first broadcast subnet whose mask matches the address; if none matches, it uses `remote_broadcast_subnet`. Entries without an explicit name type are inserted as both `<00>` and `<20>` permanent active names. Entries with a type are inserted as that exact type. `find_name_in_lmhosts()` checks only `remote_broadcast_subnet`, returns true only for active `LMHOSTS_NAME` records, and leaves normal subnet entries to the standard query path.

## State And Persistence
Loaded entries are inserted as `PERMANENT_TTL` and `LMHOSTS_NAME`, so they are not expired by normal TTL processing. The source file remains the authoritative persistence; in-memory records are rebuilt by loading.

## Dependencies And Integration Points
`nmbd_namequery.c` checks lmhosts before querying subnet namelists, giving static remote mappings priority. The module depends on subnet database globals, address matching helpers, and the local namelist implementation. It includes `../libcli/nbt/libnbt.h` for lmhosts parsing support.

## Risks And Test Signals
Only IPv4 entries are handled; IPv6 lmhosts data is ignored. Subnet selection based on broadcast subnet masks can place entries unexpectedly if interfaces overlap. Test signals include load behavior for default and explicit name types, remote-broadcast lookup precedence, skipped non-IPv4 entries, and permanent TTL visibility in `namelist.debug`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_lmhosts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_logonnames.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_logonnames.c

## Purpose
Registers and tracks the domain logon server internet group name `WORKGROUP<1c>` when Samba is configured as a domain controller. Successful registration makes Samba advertise logon/domain-control capabilities for the workgroup.

## Important APIs, Types, And Functions
Public entry point is `add_logon_names()`. Internal callbacks and helpers are `become_logon_server()`, `become_logon_server_success()`, and `become_logon_server_fail()`. The code updates `struct work_record::log_state`, the local `struct server_record::serv.type`, and uses `insert_permanent_name_into_unicast()` to mirror `<1c>` onto the unicast subnet.

## Control Flow
`add_logon_names()` iterates all subnets including unicast. For each workgroup matching `lp_workgroup()` with `LOGON_NONE`, it checks whether `WORKGROUP<1c>` is already a local self name. If not, it calls `become_logon_server()`, which sets `LOGON_WAIT` and registers `<1c>` as a group name using `samba_nb_type | NB_GROUP`. On success, the callback sets `LOGON_SRV`, marks server type as `SV_TYPE_NT | SV_TYPE_DOMAIN_MEMBER | SV_TYPE_DOMAIN_CTRL`, flags `work_changed`, inserts a permanent unicast `<1c>` name for the subnet IP, and logs the transition. On failure it clears `LOGON_NONE` and removes `SV_TYPE_DOMAIN_CTRL` if the server record is found.

## State And Persistence
State is held in `work->log_state`, server type bits, and namelist records for `WORKGROUP<1c>`. `subrec->work_changed` triggers browse/server-list persistence. The unicast mirror lets directed queries for `<1c>` resolve to each broadcast subnet where Samba provides logon service.

## Dependencies And Integration Points
The file is called by `add_domain_names()` in the DMB module when `IS_DC` is true. It depends on name registration callbacks, workgroup/server database helpers, `insert_permanent_name_into_unicast()` from LMB code, and configuration `lp_workgroup()`/`lp_netbios_name()`.

## Risks And Test Signals
If server records are missing, success/failure paths roll back only partially and log errors. Because `<1c>` is a group name, WINS and broadcast behavior differ from unique-name registration. Test signals include `LOGON_WAIT` to `LOGON_SRV` transition, server type bits after success/failure, presence of `WORKGROUP<1c>` on broadcast and unicast namelists, and no duplicate registration when the name already exists.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_logonnames.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_mynames.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_mynames.c

## Purpose
Initializes Samba's configured NetBIOS names and registers them, the workgroup names, and Samba magic names across broadcast and unicast subnets. It also releases WINS names and periodically refreshes WINS registrations.

## Important APIs, Types, And Functions
Public APIs are `nmbd_init_my_netbios_names()`, `my_netbios_names()`, `register_my_workgroup_one_subnet()`, `register_my_workgroup_and_names()`, `release_wins_names()`, and `refresh_my_names()`. Internal helpers include `add_unique_netbios_name()`, `my_name_register_failed()`, and `insert_refresh_name_into_unicast()`. It uses global `samba_nb_type`, `lp_netbios_name()`, `lp_netbios_aliases()`, `lp_workgroup()`, clustering configuration, and name registration/release APIs.

## Control Flow
`nmbd_init_my_netbios_names()` rebuilds a talloc array containing the primary NetBIOS name and unique aliases. `register_my_workgroup_one_subnet()` creates the configured workgroup on a subnet, adds magic Samba names, registers each configured name as `<20>`, `<03>`, and `<00>`, then initiates workgroup startup, which registers workgroup group names and election state. `register_my_workgroup_and_names()` runs that per subnet including unicast, then directly adds magic names and multihomed IPs to the unicast subnet for broadcast-only environments.

For each broadcast subnet, `insert_refresh_name_into_unicast()` adds local name types to unicast. In WINS-client mode these entries are `SELF_NAME` with bounded refresh TTL, otherwise they are permanent. Cluster addresses are appended to existing unicast name records when `lp_clustering()` is enabled. Workgroup `<00>` and `<1e>` group names and remote-broadcast Samba magic names are also added. `release_wins_names()` releases active unicast `SELF_NAME` records. `refresh_my_names()` walks unicast names and queues WINS refreshes when refresh times pass.

## State And Persistence
The file owns static `mynames` and populates subnet workgroup/namelist state. WINS-client unicast names use `death_time` and `refresh_time`; broadcast-only names are permanent mirrors. Refresh preemptively extends local death/refresh times after queuing a WINS refresh to prevent duplicate refreshes. Release marks names through the release module.

## Dependencies And Integration Points
This is a startup/shutdown/periodic maintenance hub. It depends on workgroup creation, name registration, namelist mutation, WINS refresh/release, cluster address parsing, and subnet globals. Later query, election, browser, and node-status behavior all rely on these names having been registered or mirrored.

## Risks And Test Signals
Risks include duplicate alias handling, conversion/registration failures that leave partial subnet state, incorrect unicast TTL mode depending on WINS configuration, and cluster IPs being appended repeatedly if initialization is rerun unexpectedly. Test signals include initialized alias list uniqueness, expected `<20>/<03>/<00>` registrations, unicast mirrors for each interface, WINS refresh queueing once per due record, release of unicast self names, and node-status visibility of configured aliases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_mynames.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_namelistdb.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_namelistdb.c

## Purpose
Provides the core in-memory NetBIOS name database used by nmbd subnets. It normalizes names, adds/removes/fetches records, updates TTLs and IP lists, implements standard registration/release callbacks, expires stale names, adds Samba magic names, and dumps name state for diagnostics.

## Important APIs, Types, And Functions
The file defines global `uint16_t samba_nb_type` and public functions `set_samba_nb_type()`, `remove_name_from_namelist()`, `find_name_on_subnet()`, `find_name_for_remote_broadcast_subnet()`, `update_name_ttl()`, `add_name_to_subnet()`, `standard_success_register()`, `standard_fail_register()`, `find_ip_in_name_record()`, `add_ip_to_name_record()`, `remove_ip_from_name_record()`, `standard_success_release()`, `expire_names()`, `add_samba_names_to_subnet()`, `dump_name_record()`, and `dump_all_namelists()`.

## Control Flow
`set_samba_nb_type()` chooses hybrid (`NB_HFLAG`) when Samba is a WINS server/client, otherwise broadcast (`NB_BFLAG`). `add_name_to_subnet()` allocates a `name_record`, uppercases the NetBIOS name and scope, sets active flags, marks the primary NetBIOS name permanent, copies IPs, sets source/death/refresh metadata, and either inserts into a normal subnet list or hands the record to WINS storage. `find_name_on_subnet()` uppercases the requested name, delegates WINS lookups when appropriate, and optionally filters to self/permanent names.

Standard callbacks update local state after async register/release operations. `standard_success_register()` creates or refreshes a `SELF_NAME`; `standard_fail_register()` removes a failed self name; `standard_success_release()` removes the released IP and deletes the record when no IPs remain. `expire_names()` skips WINS server subnet processing, extends expired self names by five minutes instead of deleting them, and removes other expired records. `add_samba_names_to_subnet()` inserts `*<00>`, `*<20>`, `__SAMBA__<20>`, and `__SAMBA__<00>`, using all interface IPs on unicast/WINS/remote-broadcast style subnets.

## State And Persistence
Normal subnet state is linked-list memory plus `subrec->namelist_changed`. WINS subnet state is persisted by WINS-specific helpers such as `add_name_to_wins_subnet()` and `wins_store_changed_namerec()`. `dump_all_namelists()` writes `namelist.debug` under the lock path for operational inspection.

## Dependencies And Integration Points
Every file in this subset uses this module directly or indirectly. It depends on `nmbd.h` data structures, Samba allocation/list macros, charset conversion helpers, WINS server storage functions, interface enumeration, and configuration TTLs. Registration, release, query, incoming-request, lmhosts, and browser-role modules all depend on its source and TTL semantics.

## Risks And Test Signals
Risks include name uppercase/conversion failures, IP-list allocation failures, inconsistent `namelist_changed` updates, self-name expiry extension hiding refresh bugs, and duplicate magic names if callers do not guard insertion. Test signals include add/find/remove by exact NetBIOS type/scope, self-only lookup filtering, WINS-subnet delegation, TTL refresh/death calculations, IP add/remove reference behavior, expiry of non-self names, and `namelist.debug` content after SIGHUP-style dumps.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_namelistdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_namequery.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_namequery.c

## Purpose
Implements asynchronous NetBIOS name query initiation, response handling, timeout handling, and local short-circuit lookup. It is the common query layer used by browser role transitions, WINS discovery, and other nmbd code that needs to resolve a NetBIOS name.

## Important APIs, Types, And Functions
Public APIs are `query_name()` and `query_name_from_wins_server()`. Internal functions are `query_name_response()`, `query_name_timeout_response()`, and `query_local_namelists()`. Callback typedefs come from `nmbd.h`: `query_name_success_function` and `query_name_fail_function`. It uses `struct response_record`, `struct res_rec`, and queued packet helpers `queue_query_name()` and `queue_query_name_from_wins_server()`.

## Control Flow
`query_name()` builds an `nmb_name`, checks lmhosts and the local subnet namelist first, and if found fabricates a `res_rec` from the local IP list before calling the success callback immediately. If no local record applies, it queues a network query with response and timeout callbacks. `query_name_from_wins_server()` skips local lookup and queues a directed WINS-server query.

`query_name_response()` suppresses retries after a response, handles WACK by delaying `repeat_time` and decrementing `num_msgs`, treats nonzero rcode as failure, validates successful answers, extracts the first returned IP, and calls success/failure callbacks only for the first response. Later duplicate responses are logged as multiple responses without invoking callbacks again. `query_name_timeout_response()` calls the fail callback only if no response was seen, then removes the response record.

## State And Persistence
The module mutates response-record retry fields (`repeat_count`, `repeat_time`, `num_msgs`) and removes response records on completion. It does not normally cache network query answers in namelists, though comments note that could be possible. Local short-circuit results are read-only.

## Dependencies And Integration Points
It integrates with lmhosts lookup, namelist lookup, packet queueing/retransmit infrastructure, WINS server querying, and all role/sync modules that pass query callbacks. DMB/LMB code relies on fail-code distinctions, especially `NAM_ERR` from WINS for absent names.

## Risks And Test Signals
Risks include callback reentrancy from local short-circuit success, stale response records kept after WACK, and only using the first IP from a multi-IP answer for callback arguments. Tests should cover immediate lmhosts/local success, network positive/negative responses, WACK delay behavior, timeout failure, duplicate response logging without duplicate callbacks, and directed WINS query queue failure handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_namequery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_nameregister.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_nameregister.c

## Purpose
Implements asynchronous registration and refresh of Samba-owned NetBIOS names. It covers broadcast registration, WINS registration, multihomed WINS registration across all interface IPs, WINS failover by tag, and refresh of existing WINS records.

## Important APIs, Types, And Functions
Public APIs are `register_name()` and `wins_refresh_name()`. Key internal functions are `register_name_response()`, `register_name_timeout_response()`, `wins_registration_timeout()`, `multihomed_register_name()`, `multihomed_register_one()`, and `wins_next_registration()`. It uses `struct nmb_name`, `struct response_record`, `struct userdata_struct`, name registration callbacks, WINS server tag APIs, and queued packet helpers for register/refresh operations.

## Control Flow
`register_name()` converts/truncates NetBIOS names safely into DOS charset limits, sets `NB_ACTIVE`, and chooses WINS multihomed registration when `subrec == unicast_subnet`; otherwise it queues a broadcast registration. Broadcast registration succeeds on timeout with no replies. A broadcast reply means conflict, except for the old Samba `WORKGROUP<1b>` compatibility hack that ignores specific `ACT_ERR` replies.

WINS registration expects a reply from the selected server. `register_name_response()` validates that answer and question names match, ignores responses from unexpected WINS IPs, handles WACK by delaying, marks WINS servers alive on valid unicast responses, and on success calls `standard_success_register()` plus caller success callback. On failure it calls the caller failure callback and `standard_fail_register()`.

Multihomed WINS registration pre-adds unique names to the unicast namelist because WINS servers may query the registering machine during validation. It collects broadcast subnet IPs, adds a unicast `SELF_NAME`, then sends the first IP to each WINS tag group. `wins_next_registration()` chains subsequent interface IP registrations or refreshes after each response. If all WINS servers for a source address are dead, timeout is treated as success so names remain in normal refresh mode.

## State And Persistence
The module mutates response-record retry state, WINS liveness state, and local namelists through standard callbacks. Unicast `SELF_NAME` records may be created before WINS has accepted them to satisfy WINS validation. Refreshes reuse the registration response path and update TTLs through namelist callbacks.

## Dependencies And Integration Points
It depends on packet queueing infrastructure, WINS server selection/failover APIs, namelist standard callbacks, charset conversion, subnet/interface enumeration, and callers in mynames, browser role, logon, and workgroup startup modules. `refresh_my_names()` in `nmbd_mynames.c` invokes `wins_refresh_name()`.

## Risks And Test Signals
Risks include premature unicast name insertion during WINS validation, callback behavior only attached to the last multihomed release/registration chain in some paths, name truncation surprises after DOS charset conversion, and treating all-WINS-down registration timeout as success. Test signals include broadcast conflict vs timeout success, WACK retry delay, response-source filtering, WINS failover tag rotation, multihomed sequential registrations for each interface IP, standard callbacks updating namelists, and refresh queueing per WINS tag.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_nameregister.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_namerelease.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_namerelease.c

## Purpose
Implements asynchronous release of Samba-owned NetBIOS names from broadcast subnets and WINS. It sends release packets for all IPs associated with a name, handles WINS tag groups, and updates local namelists through standard release callbacks.

## Important APIs, Types, And Functions
Public API is `release_name()`. Internal functions are `release_name_response()`, `release_name_timeout_response()`, and `wins_release_name()`. It uses `struct name_record`, `struct response_record`, release success/failure callbacks, `queue_release_name()`, `wins_srv_tags()`, `wins_srv_ip_tag()`, and `standard_success_release()`.

## Control Flow
`release_name()` only operates on active `SELF_NAME` records. It marks the record `NB_DEREG`, then chooses WINS release for `unicast_subnet` or broadcast release otherwise. Broadcast release queues one packet per known IP to the subnet broadcast address, attaching caller callbacks only to the last packet. WINS release iterates all WINS tag groups and all IPs, sending each release to the selected WINS server and again attaching caller callbacks only to the final queued release.

`release_name_response()` ignores broadcast responses, validates matching answer/question names for unicast replies, handles WACK by delaying, treats nonzero rcode as failure, and on success calls the caller success callback followed by `standard_success_release()`. `release_name_timeout_response()` treats every timeout as release success; for WINS it marks the server temporarily dead, calls success callback, updates namelist state, and removes the response record.

## State And Persistence
State changes are `NB_DEREG` on the local name, response-record retry state, WINS server liveness on timeout, and removal of released IPs from local name records. If the last IP is removed, the namelist record is deleted. Persistence is indirect through namelist/WINS storage change flags.

## Dependencies And Integration Points
LMB demotion, WINS shutdown, and browser-name cleanup call this module. It depends on the namelist standard release callback, queued packet infrastructure, and WINS server tag APIs. Release semantics are paired with registration state from `nmbd_nameregister.c` and namelist reference-count-like IP behavior from `nmbd_namelistdb.c`.

## Risks And Test Signals
Risks include considering timeouts successful even if a WINS server did not process the release, only notifying callers on the final queued release, and refusing to release non-`SELF_NAME` records such as permanent unicast mirrors. Test signals include `NB_DEREG` marking, multi-IP release packet count, WACK delay handling, failure callback on WINS rcode errors, local namelist IP removal after timeout, and WINS server death marking.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_namerelease.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_nodestatus.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd_nodestatus.c

## Purpose
Provides the asynchronous client-side node-status query helper. Other nmbd modules use it to ask a remote NetBIOS node for all registered names at an IP address, then parse the returned resource record in their own callbacks.

## Important APIs, Types, And Functions
Public API is `node_status(struct subnet_record *, struct nmb_name *, struct in_addr, node_status_success_function, node_status_fail_function, struct userdata_struct *)`. Internal callbacks are `node_status_response()` and `node_status_timeout_response()`. It uses queued packet helper `queue_node_status()`, `struct response_record`, and the node-status callback typedefs from `nmbd.h`.

## Control Flow
`node_status()` queues a node-status packet to the supplied IP and returns true only on queue/send failure. `node_status_response()` validates that answer and question names match, logs success, passes the entire answer resource record and source IP to the caller's success callback, then removes the response record. `node_status_timeout_response()` logs failure, invokes the caller fail callback if present, and removes the response record.

## State And Persistence
This module only owns transient response-record lifecycle. It does not parse, cache, or persist node-status data itself. Callers such as browse sync callbacks update `work->dmb_name`, `work->dmb_addr`, or create unicast workgroups based on the returned record.

## Dependencies And Integration Points
`nmbd_browsesync.c` uses node-status responses to map DMB IPs to `<20>` server names and to discover foreign `WORKGROUP<1b>` names. The helper depends on packet queueing/retransmit infrastructure and common NetBIOS name equality logic.

## Risks And Test Signals
Risk is mostly in strict answer-name validation and in relying on callers to parse variable node-status payloads safely. Test signals include successful callback delivery with unmodified `answers`, timeout fail callback execution, response-record removal in both paths, and queue failure returning true to callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd_nodestatus.c -->
