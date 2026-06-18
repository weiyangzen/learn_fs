# subset-b-006241 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_core.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_core.c

## Purpose
`ip_vs_core.c` is the IP Virtual Server packet-processing core. It registers the module and per-network-namespace IPVS state, installs IPv4/IPv6 Netfilter hooks, schedules new virtual-service connections, rewrites packets for NAT/masquerade forwarding, handles ICMP/ICMPv6 errors and tunnel PMTU feedback, updates per-service/destination/global counters, and exposes shared resizable-hash-table helpers used by control and connection tables.

## Important APIs, types, and functions
Exported entry points include `ip_vs_proto_name()`, `ip_vs_init_hash_table()`, `ip_vs_rht_alloc()`, `ip_vs_rht_free()`, `ip_vs_rht_rcu_free()`, `ip_vs_rht_desired_size()`, `ip_vs_rht_set_thresholds()`, `ip_vs_rht_hash_linfo()`, `ip_vs_schedule()`, `ip_vs_leave()`, `ip_vs_checksum_complete()`, `ip_vs_nat_icmp()`, `ip_vs_new_conn_out()`, `ip_vs_register_hooks()`, and `ip_vs_unregister_hooks()`. The file relies heavily on `struct netns_ipvs`, `struct ip_vs_conn`, `struct ip_vs_service`, `struct ip_vs_dest`, `struct ip_vs_protocol`, `struct ip_vs_proto_data`, `struct ip_vs_iphdr`, and `struct ip_vs_rht`.

Key internal functions are `ip_vs_sched_persist()` for persistent templates, `handle_response()` for outgoing reply translation, `ip_vs_out_hook()` and `ip_vs_in_hook()` for Netfilter ingress/egress dispatch, `ip_vs_try_to_schedule()` for protocol-specific first-packet scheduling, `ip_vs_in_icmp()` / `ip_vs_out_icmp()` and IPv6 equivalents for error handling, `ipvs_udp_decap()` and `ipvs_gre_decap()` for tunnel-error parsing, and `__ip_vs_init()` / cleanup batches for namespace lifecycle.

## Control flow
Module init calls `ip_vs_control_init()`, protocol and connection-table init, registers pernet operations, then registers sockopt/generic-netlink control. Per netns, `__ip_vs_init()` wires `net->ipvs`, initializes estimator, control, protocol, app, connection, and sync subsystems. Device cleanup unregisters hooks and disables packet reception before sync cleanup; final cleanup flushes services and tears down connection/app/protocol/control/estimator state.

Incoming traffic enters `ip_vs_in_hook()` at local-in/local-out hooks. It rejects already-IPVS-marked packets, unsuitable packet types, backup-only namespaces, raw IPv4 NODEFRAG sockets, and unsupported protocols. ICMP/ICMPv6 packets are dispatched to special handlers. For TCP/SCTP first packets that match stale or unavailable connections, it may expire and reschedule according to `conn_reuse_mode` and `expire_nodest_conn`. If no connection exists, `ip_vs_try_to_schedule()` asks the protocol module to find a service and call `ip_vs_schedule()`. The chosen connection updates input stats/state, calls `cp->packet_xmit()`, optionally syncs to backup nodes, and drops its reference.

Outgoing traffic enters `ip_vs_out_hook()`. Existing outgoing connections are passed to `handle_response()`, which SNATs masqueraded replies via protocol `snat_handler`, rewrites source addresses, reroutes when `snat_reroute` is enabled, updates stats/state, marks conntrack/notrack, and accepts or steals the skb on failure. UDP real-server-initiated traffic can create outbound connections through persistence-engine `conn_out` callbacks. If no matching connection exists, `nat_icmp_send` may generate ICMP port unreachable back to real servers.

`ip_vs_schedule()` parses transport ports, avoids scheduling FTP data replies and local real-server replies, then either creates a persistent template plus child connection or invokes the bound scheduler for a one-shot destination. `ip_vs_leave()` handles the no-destination path by creating cache-bypass connections for fwmark services when configured, accepting non-control FTP traffic, dropping ICMP, or sending ICMP unreachable.

## State and persistence behavior
Persistent kernel state is per netns: enabled flag, hook mask, estimator/control/protocol/app/connection/sync state, service and connection hash tables, counters, sysctl-driven behavior, and sync state. Per packet, the code mutates skb headers, checksums, route dsts, `skb->ipvs_property`, and conntrack association. Connection objects keep protocol state, input/output packet counters, optional control/template links, destination bindings, and forwarding flags. Statistics are per-CPU counters plus estimator-derived rates. The resizable hash table stores bucket arrays, seqcounts, optional locks, thresholds, random hash key, and a `new_tbl` pointer to support two-table RCU resize windows.

## Dependencies and integration points
The file integrates with Linux Netfilter hooks, IPv4/IPv6 routing and defragmentation, ICMP/ICMPv6 generation, GUE/GRE/IPIP tunnel parsing, skb checksum helpers, conntrack integration through IPVS helpers, protocol modules through `ip_vs_proto_data_get()` and protocol callbacks, schedulers through `svc->scheduler`, persistence engines through `svc->pe`, sync daemon replication, and control-plane state from `ip_vs_ctl.c`. IPv6 paths are conditional on `CONFIG_IP_VS_IPV6`; protocol fast paths use indirect-call wrappers for TCP/UDP SNAT.

## Risks and edge cases
Packet ownership is delicate: several error paths call `kfree_skb()` or return `NF_STOLEN`, so callers must not touch the skb afterward. ICMP handling has many malformed/truncated-header exits and distinguishes tunnel errors from ordinary embedded-connection errors. Rescheduling stale connections must coordinate with conntrack; old conntrack can force a drop. Persistent FTP and fwmark templates use special zero-port and `IPPROTO_IP` matching. Hash-table resizing allows readers to see two tables and walkers may see duplicates. NAT rewrite requires writable skb data and correct checksum state. Hook registration is per address family and is tied to service count, so service add/delete races must preserve counters and hook masks.

## Test signals
High-value signals include IPv4 and IPv6 service add/remove causing hook registration/unregistration, NAT/DR/TUN/local forwarding smoke tests, persistent service template reuse, FTP-data and fwmark behavior, cache-bypass no-destination routing, ICMP/ICMPv6 unreachable and PMTU tunnel error forwarding, fragmented IPv4 defrag behavior, TCP/SCTP connection reuse and no-destination expiry, real-server-initiated UDP connection handling, sync-threshold packet replication, conntrack/notrack toggles, route-me-harder failures, and service/connection hash resize under concurrent lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_ctl.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_ctl.c

## Purpose
`ip_vs_ctl.c` is the IPVS administrative and control-plane implementation. It owns virtual-service and real-server destination configuration, service lookup tables, scheduler and persistence-engine binding, destination trash/reuse, statistics allocation and export, `/proc` and sysctl surfaces, legacy sockopt control, generic netlink control, sync-daemon commands, and per-netns control initialization/cleanup.

## Important APIs, types, and functions
Publicly used functions include `ip_vs_get_debug_level()`, `ip_vs_use_count_inc()`, `ip_vs_use_count_dec()`, `ip_vs_service_find()`, `ip_vs_has_real_service()`, `ip_vs_find_real_service()`, `ip_vs_find_tunnel()`, `ip_vs_find_dest()`, `ip_vs_dest_dst_rcu_free()`, `ip_vs_stats_init_alloc()`, `ip_vs_stats_alloc()`, `ip_vs_stats_release()`, `ip_vs_stats_free()`, `ip_vs_service_nets_cleanup()`, `ip_vs_control_net_init()`, `ip_vs_control_net_cleanup()`, `ip_vs_register_nl_ioctl()`, `ip_vs_unregister_nl_ioctl()`, `ip_vs_control_init()`, and `ip_vs_control_cleanup()`.

Important internal functions include `update_defense_level()`, `est_reload_work_handler()`, service hash/lookup helpers, `svc_resize_work_handler()`, `__ip_vs_update_dest()`, `ip_vs_add_dest()`, `ip_vs_edit_dest()`, `ip_vs_del_dest()`, `ip_vs_dest_trash_expire()`, `ip_vs_add_service()`, `ip_vs_edit_service()`, `ip_vs_del_service()`, `ip_vs_flush()`, proc seq emitters, `do_ip_vs_set_ctl()`, `do_ip_vs_get_ctl()`, and generic-netlink parse/fill/doit/dump handlers. Central types are `struct netns_ipvs`, `struct ip_vs_service`, `struct ip_vs_dest`, `struct ip_vs_stats`, `struct ip_vs_rht`, `struct ip_vs_service_user_kern`, `struct ip_vs_dest_user_kern`, `struct ip_vs_scheduler`, and `struct ip_vs_pe`.

## Control flow
Control-plane init registers a netdevice notifier. Per netns, `ip_vs_control_net_init()` initializes `service_mutex`, resize semaphore/work, real-server hash table, destination trash timer/list, service counters, estimator reload work, total stats, proc entries, and sysctl defaults. Sysctl init starts the total-stats estimator and schedules defense work. Cleanup flushes trash, cancels works/timers, unregisters sysctl/proc entries, and frees total stats through RCU.

Service creation through sockopt or netlink validates capability and arguments, acquires `service_mutex`, optionally allocates service/connection resizable hash tables, registers hooks for the address family when adding the first service, gets scheduler and persistence-engine modules, initializes stats and estimator, binds scheduler, updates service counters, hashes the service, queues resize work if needed, and enables the namespace plus estimator reload when the first service appears. Editing can replace scheduler and persistence engine under RCU, updating connection-out counters. Deletion unhashes the service, unregisters conntrack, stops estimators, unbinds scheduler/PE, unlinks all destinations, unregisters hooks when the last service for an address family is removed, and may drop or shrink the service table.

Destination add/edit validates weight, thresholds, tunnel settings, and address family, looks up existing destination, optionally reuses a matching destination from trash, starts its estimator, then updates forwarding flags, tunnel metadata, service binding, real-server hash membership, destination list membership, scheduler callbacks, route cache, and availability flags. Destination deletion unlinks from service, clears route cache, calls scheduler delete callback, stops its estimator, removes real-server hash membership, and puts the object into trash while existing connections drain.

The generic netlink path parses nested service/destination/daemon attributes, supports add/edit/delete/get/dump/flush/zero/config commands, and can expose 64-bit stats. The legacy sockopt path uses IPv4-compatible structs and exposes older service/destination/config operations. Procfs emits service tables, total stats, per-CPU stats, and internal bucket/status diagnostics.

## State and persistence behavior
The file persists all configured services and destinations in kernel memory per netns. Services live in an RCU resizable hash table keyed either by protocol/address/port or fwmark. Real servers also live in a fixed real-service hash for reverse lookups by masquerade/tunnel endpoints. Destinations removed from services are retained in `dest_trash` while references from live connections remain, preserving stats and allowing later reuse by the same service. Statistics allocate per-CPU counters and estimators for total, service, and destination objects. Sysctls mutate defense modes, sync settings, estimator configuration, connection/service hash load factors, backup-only behavior, ICMP scheduling, tunnel handling, conntrack, and related runtime behavior. Module use count is held while services exist.

## Dependencies and integration points
`ip_vs_ctl.c` is the bridge between userspace tools such as `ipvsadm` and the packet core. It depends on scheduler registration, persistence-engine lookup, protocol timeout tables, estimator threads, sync daemon start/stop, app/FTP conntrack registration, connection-table allocation and resizing, Netfilter hook registration from `ip_vs_core.c`, procfs, sysctl, netdevice notifier callbacks, RCU, generic netlink, and legacy `nf_sockopt_ops`. IPv6 support enables IPv6 address validation, defragmentation, route-local checks, and mixed-family tunnel destination handling.

## Risks and edge cases
Lock ordering is central: service changes use `service_mutex`, service resizing combines `svc_resize_sem`, seqcounts, bucket locks, and RCU, and some readers retry when `svc_table_changes` changes. Generic netlink and sockopt interfaces differ in address-family support and exposed stats widths. Mixed-family destination pools are only allowed for tunnel forwarding and are incompatible with sync daemons. Service-table walkers may miss or duplicate entries during resize. Destination trash must not free objects still referenced by connections. Scheduler and persistence-engine replacement must wait for RCU users before freeing old `sched_data`. The sysctl table relies on fixed index ordering matching initialization. Defense and estimator works must stop cleanly during namespace teardown. Netdevice-down route-cache cleanup walks RCU service/destination lists while resize can occur.

## Test signals
Useful tests include add/edit/delete/flush services through both generic netlink and legacy sockopt, IPv4/IPv6/fwm/null-port service lookup, scheduler/PE module missing and replacement paths, destination add/edit/delete/trash reuse, invalid weights/thresholds/tunnel ports/address families, mixed-family tunnel acceptance and sync rejection, hook registration count transitions, service-table grow/shrink with concurrent dumps/lookups, proc output sanity, sysctl validation for defense/sync/estimator/load-factor knobs, netdevice-down route-cache reset, zero stats for one service and all services, sync daemon start/stop/dump, and cleanup with live destination references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_ctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_dh.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_dh.c

## Purpose
`ip_vs_dh.c` implements the IPVS destination-hashing scheduler named `dh`. It maps each packet's destination IP address to one of a fixed number of scheduler buckets, where each bucket points at a real server destination. This is intended for cache-cluster style deployments where a given origin destination should consistently select the same cache server, often paired with IPVS cache-bypass when the chosen cache is unavailable.

## Important APIs, types, and functions
The local state types are `struct ip_vs_dh_bucket`, holding an RCU-protected `struct ip_vs_dest *`, and `struct ip_vs_dh_state`, holding the fixed bucket array plus an RCU head. Important functions are `ip_vs_dh_hashkey()`, `ip_vs_dh_get()`, `ip_vs_dh_reassign()`, `ip_vs_dh_flush()`, `ip_vs_dh_init_svc()`, `ip_vs_dh_done_svc()`, `ip_vs_dh_dest_changed()`, `is_overloaded()`, and `ip_vs_dh_schedule()`. The module registers `ip_vs_dh_scheduler` with scheduler callbacks for service init/done, destination add/delete, and scheduling.

## Control flow
When a service binds the scheduler, `ip_vs_dh_init_svc()` allocates scheduler state and calls `ip_vs_dh_reassign()` to fill the bucket array from the service's current destination list. Reassignment walks all buckets, drops any previous destination reference, and assigns destinations round-robin across buckets, taking a destination reference for every assigned bucket. Destination additions and deletions simply rebuild the whole fixed table. During scheduling, `ip_vs_dh_schedule()` hashes `iph->daddr`, fetches the bucket destination under RCU, rejects missing, unavailable, zero/negative-weight, or overloaded destinations, and returns the selected destination.

## State and persistence behavior
Scheduler state is per service in `svc->sched_data`. Every bucket holds a destination reference while assigned, so destinations are kept alive until bucket reassignment or scheduler teardown releases them. The table size defaults to 256 buckets unless `CONFIG_IP_VS_DH_TAB_BITS` changes it. The mapping is deterministic for a given destination-list ordering and destination address but is rebuilt wholesale when the destination set changes.

## Dependencies and integration points
The scheduler integrates with the common IPVS scheduler registry via `register_ip_vs_scheduler()` and `unregister_ip_vs_scheduler()`, service destination lists maintained by `ip_vs_ctl.c`, RCU destination access, destination refcount helpers, packet header data from `struct ip_vs_iphdr`, and generic scheduler error/debug helpers. IPv6 hashing folds the IPv6 address words before applying `hash_32()`.

## Risks and edge cases
The algorithm does not search for an alternate destination if the hashed bucket points to an unavailable, overloaded, or zero-weight real server; it returns NULL and relies on higher-level no-destination behavior such as cache bypass. Reassigning all buckets on every destination change is simple but can be disruptive and takes/release many references. Weighted behavior is not proportional: weights are only an eligibility check. IPv6 address folding can collide more aggressively than a full hash over all address bytes. Service list ordering affects the bucket map.

## Test signals
Test with stable source service/destination ordering to confirm repeatable destination-IP mapping, destination add/delete causing bucket reassignment, zero-weight and overloaded destinations returning no destination, IPv4 and IPv6 hash behavior, empty service tables, scheduler module load/unload with RCU grace, and cache-bypass behavior in the packet core when `dh` returns NULL for an unavailable cache.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_dh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_est.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_est.c

## Purpose
`ip_vs_est.c` implements IPVS rate estimation for total, service, and destination statistics. It periodically folds per-CPU packet/byte/connection counters into aggregate counters and exponentially smoothed rates for connections per second, packets per second, and bytes per second. It uses per-netns estimator kthreads, dynamic chain distribution, and reload logic driven by estimator sysctls.

## Important APIs, types, and functions
Externally used functions are `ip_vs_est_reload_start()`, `ip_vs_est_kthread_start()`, `ip_vs_est_kthread_stop()`, `ip_vs_start_estimator()`, `ip_vs_stop_estimator()`, `ip_vs_zero_estimator()`, `ip_vs_read_estimator()`, `ip_vs_estimator_net_init()`, and `ip_vs_estimator_net_cleanup()`. Important internals include `ip_vs_chain_estimation()`, `ip_vs_tick_estimation()`, `ip_vs_estimation_kthread()`, `ip_vs_est_set_params()`, `ip_vs_est_add_kthread()`, `ip_vs_est_update_ktid()`, `ip_vs_enqueue_estimator()`, `ip_vs_est_drain_temp_list()`, `ip_vs_est_calc_limits()`, and `ip_vs_est_calc_phase()`. The key data structures are embedded in `struct netns_ipvs`, `struct ip_vs_stats`, `struct ip_vs_estimator`, `struct ip_vs_est_kt_data`, and `struct ip_vs_est_tick_data`.

## Control flow
Stats objects call `ip_vs_start_estimator()` after their per-CPU counters are allocated. The estimator starts on `est_temp_list`, creating kthread-0 context if needed. Kthread tasks are only started after the first service enables IPVS; reload work starts, stops, or restarts tasks based on config generation and `run_estimation` state. Kthread 0 can enter calculation phase, benchmark a synthetic estimator chain, choose a chain length target, stop other tasks, move existing estimators back to the temporary list, apply new limits, and then drain the temporary list into tick chains.

Each estimator kthread sleeps around `IPVS_EST_TICK`, iterates rows in a ring of `IPVS_EST_NTICKS`, and estimates only chains present in that row. `ip_vs_chain_estimation()` sums all possible CPUs using `u64_stats_fetch_begin/retry`, updates aggregate `kstats`, calculates deltas since the previous sample, and applies a smoothing factor of 1/4. Packets/connections are stored scaled by 2^10, bytes by 2^5, then decoded by `ip_vs_read_estimator()`.

Stopping an estimator removes it either from `est_temp_list` or its assigned tick chain, updates chain length/full/available bookkeeping, frees empty tick data through RCU, destroys unused nonzero kthread contexts, and may request kthread-0 stop when all estimator work is gone. Netns cleanup stops all tasks, frees the kthread array, and destroys the estimator mutex.

## State and persistence behavior
All estimator state is in-memory per netns. `est_temp_list` buffers newly added or rebalanced estimators. `est_kt_arr` stores kthread contexts, each with tick rows, chain fullness bitmaps, current row, scheduling timer, count limits, and optional benchmark stats. `est_genid` and `est_genid_done` coordinate reloads; `est_calc_phase`, `est_chain_max`, `est_add_ktid`, and `est_max_threads` determine placement. Individual estimators retain last counter snapshots and scaled smoothed rates. Zeroing stats resets the estimator baseline and rates while preserving current aggregate counters.

## Dependencies and integration points
The estimator consumes per-CPU stats allocated by `ip_vs_ctl.c` and updated by packet paths in `ip_vs_core.c`. Sysctl handlers in `ip_vs_ctl.c` change CPU affinity, nice level, run/stop state, and maximum threads, then call `ip_vs_est_reload_start()`. Service and destination add/delete paths call start/stop. Procfs and netlink stats export call `ip_vs_read_estimator()`. It depends on kthreads, RCU hlist traversal, jiffies, cpumask and housekeeping CPU selection, mutexes shared with service/control logic, and `u64_stats` synchronization with softirq writers.

## Risks and edge cases
The code has subtle locking rules: `service_mutex` protects temporary list and many kthread array mutations, while `est_mutex` protects reload/config/task state. Kthread 0 is special and kept even when empty. Calculation phase intentionally stops other tasks and moves estimators without waiting for RCU grace because tasks are stopped. Estimator addition can fail and leave entries on the temporary list for later. Time drift is corrected if a thread wakes too late. CPU hotplug/frequency changes and cpulist restrictions influence benchmarked chain limits. Readers get smoothed rates that lag real counters by design.

## Test signals
Test adding/removing services and destinations to verify estimator lifecycle, total stats estimator startup before and after first service, proc/netlink rate output after traffic, zero-stat baseline behavior, `run_estimation` toggling, cpulist and nice sysctl reloads, kthread scaling with many estimators, deletion while estimators sit on `est_temp_list`, namespace cleanup with live estimator tasks, and high packet-rate per-CPU counter reads without torn 64-bit values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_est.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_fo.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_fo.c

## Purpose
`ip_vs_fo.c` implements the IPVS weighted failover scheduler named `fo`. It always chooses the available real server with the highest configured weight, making weight act as a priority rather than a load-sharing proportion.

## Important APIs, types, and functions
The main scheduler callback is `ip_vs_fo_schedule()`. The module defines `ip_vs_fo_scheduler` with name `fo`, module ownership, scheduler list head, and schedule callback. Lifecycle functions are `ip_vs_fo_init()` and `ip_vs_fo_cleanup()`, which register and unregister the scheduler.

## Control flow
For each new connection, the scheduler walks `svc->destinations` under the caller's RCU-side scheduler context. It tracks the highest positive weight seen so far, ignoring destinations marked `IP_VS_DEST_F_OVERLOAD`. If a candidate exists, it logs the selected server and returns it. If no destination has a weight greater than zero or all candidates are overloaded, it reports a scheduler error and returns NULL to the core scheduling path.

## State and persistence behavior
The scheduler has no per-service `sched_data` and no persistent state beyond module registration. It reads live destination flags and atomic weights each time scheduling is invoked. Active connection counts are only logged; they do not influence selection.

## Dependencies and integration points
It integrates with the IPVS scheduler registry, service destination lists from the control plane, RCU list traversal, atomic destination weights, `IP_VS_DEST_F_OVERLOAD`, debug logging, and the core scheduler contract that NULL means no destination is available.

## Risks and edge cases
Equal weights pick the first destination encountered because the comparison is strictly greater than the current high weight. A destination with weight zero is never selected. The scheduler ignores active/inactive connection counts and health beyond overload flag/weight, so priority failover is deterministic but not balancing. If the highest-priority server becomes overloaded, selection moves to the next lower non-overloaded weight.

## Test signals
Test ordering with distinct, equal, zero, and changing weights; overload flag transitions; empty destination lists; selected destination stability while active connection counts change; and module load/unload with scheduler lookup by name `fo`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_fo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_ftp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_ftp.c

## Purpose
`ip_vs_ftp.c` is the IPVS FTP application helper. It inspects FTP control connections, detects active and passive data-channel negotiation commands/responses, creates controlled IPVS connection entries for the related data connections, enables conntrack/NAT expectations, and rewrites passive server responses so clients connect to the virtual address and port instead of the real server.

## Important APIs, types, and functions
The module parameter `ports` controls which TCP control ports are registered, defaulting to 21. The main helpers are `ip_vs_ftp_data_ptr()`, `ip_vs_ftp_init_conn()`, `ip_vs_ftp_done_conn()`, `ip_vs_ftp_get_addrport()`, `ip_vs_ftp_out()`, and `ip_vs_ftp_in()`. The registered `struct ip_vs_app ip_vs_ftp` supplies `init_conn`, `done_conn`, `pkt_out`, and `pkt_in` callbacks. Per-netns lifecycle is handled by `__ip_vs_ftp_init()` and `__ip_vs_ftp_exit()`, with module-level `ip_vs_ftp_init()` and `ip_vs_ftp_exit()`.

## Control flow
When a matching FTP control connection is bound to the app, `ip_vs_ftp_init_conn()` marks the control connection with `IP_VS_CONN_F_NFCT` so conntrack can support later mangling/expectations. Incoming client-to-server packets are scanned only in established TCP state after ensuring a writable linear skb. `PASV` and `EPSV` commands store passive mode in `cp->app_data`. `PORT` and `EPRT` commands parse the client address/port and create or find a controlled active data connection from that client endpoint to the virtual service data port (`vport - 1`), targeting the same real server data port (`dport - 1`), then move that connection to TCP listen state.

Outgoing server-to-client packets are also processed only after the control connection is established. If `app_data` indicates a pending `PASV` or `EPSV`, the helper parses `227` or `229` response data, creates or finds a related passive data connection from the client to the virtual passive port, targets the real server address/port, and adds the control relationship. It then rewrites the server response to advertise the virtual address/port for PASV or the virtual port for EPSV using `nf_nat_mangle_tcp_packet()`, registers a related conntrack expectation with `ip_vs_nfct_expect_related()`, normalizes checksum state when needed, resets `app_data` to active, moves the data connection to listen state, and releases it.

`ip_vs_ftp_get_addrport()` parses old IPv4 comma-separated `PORT`/`227` payloads and extended delimiter-based `EPRT`/`EPSV` payloads. Extended parsing validates family compatibility and supports EPSV responses that omit address family and address while using a preset address from the real server.

## State and persistence behavior
The helper stores mode state in `cp->app_data` using small integer sentinel values for active, PASV, and EPSV. It creates controlled `struct ip_vs_conn` objects for data channels and links them to the FTP control connection with `ip_vs_control_add()`, so control lifetime and packet counters are related. It mutates skb payload bytes for passive responses through NAT helper APIs and intentionally leaves `diff` at zero because conntrack/NAT sequence adjustment already handles the payload-size change. Module state includes the configured port list and `exiting_module` flag used to decide whether per-netns exit should unregister the app.

## Dependencies and integration points
The file integrates with the IPVS application framework, IPVS connection lookup/creation, TCP state transitions, control-connection relationships, conntrack and NAT helper APIs, `nf_nat_mangle_tcp_packet()`, `nf_conntrack_expect`, skb linearization/writability, IPv4/IPv6 address parsers, and pernet registration. It depends on the core packet path invoking app `pkt_in` and `pkt_out` callbacks for registered TCP control ports.

## Risks and edge cases
Parsing is payload-string based and can return partial-match `-1` without buffering across packets, so split FTP commands may be missed until retransmission or later data. The helper only supports old `PORT`/`PASV` forms for IPv4, while `EPRT`/`EPSV` handle IPv4 or IPv6 with family validation. It assumes FTP data port is control port minus one for active mode. Payload mangling can fail under memory pressure and causes packet drop. Passive rewrite depends on conntrack being present; without a conntrack object the helper cannot rewrite and returns failure for that response path. `EPSV ALL` is not supported. The `exiting_module` guard means netns exit skips unregister unless module unload is in progress.

## Test signals
Test active FTP `PORT` and `EPRT` for IPv4/IPv6 family correctness, passive `PASV` and `EPSV` response rewrite, related connection creation and listen-state transition, conntrack expectation registration, checksum behavior after mangling, configured non-21 ports, malformed and partial FTP payloads, unsupported `EPSV ALL`, memory-pressure mangle failure, module unload/pernet cleanup, and NAT FTP service behavior requiring conntrack registration from the control plane.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_ftp.c -->
