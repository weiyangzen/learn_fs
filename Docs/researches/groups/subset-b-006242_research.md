<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_lblc.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_lblc.c

## Purpose
Implements the IPVS `lblc` scheduler, locality-based least connection. It caches each requested destination address to one real server so repeated requests for the same destination keep locality, while falling back to weighted least-connection selection when the cached server is unavailable or overloaded.

## Important APIs, Types, and Functions
The module registers `ip_vs_lblc_scheduler` through `register_ip_vs_scheduler()` and also registers per-netns sysctl state when `CONFIG_SYSCTL` is enabled. `struct ip_vs_lblc_entry` stores destination-address to `ip_vs_dest` mappings with an RCU callback. `struct ip_vs_lblc_table` is per-service scheduler state with hash buckets, a GC timer, entry counters, and a dead flag. `ip_vs_lblc_schedule()` is the scheduler entry point, `__ip_vs_lblc_schedule()` does weighted least-connection fallback, `ip_vs_lblc_new()` creates or replaces a cache entry, and `ip_vs_lblc_check_expire()` plus `ip_vs_lblc_full_check()` expire stale cache entries.

## Control Flow
Service bind calls `ip_vs_lblc_init_svc()`, allocating the hash table, initializing buckets, and arming a periodic timer. Scheduling first looks up `iph->daddr` in the cache. A cached destination is reused only when it is marked available, has positive weight, and `is_overloaded()` does not find a much less loaded peer. Otherwise the code scans the service destination list for the minimum `ip_vs_dest_conn_overhead(dest) / weight` using cross multiplication, then updates the destination-address cache under `svc->sched_lock`. The timer periodically does a full expiration every `COUNT_FOR_FULL_EXPIRATION` ticks or partial GC when entries exceed `max_size`.

## State and Persistence
State is in `svc->sched_data`, not persisted beyond service lifetime. Cache entries hold references to real servers through `ip_vs_dest_hold()` and release them in RCU callbacks via `ip_vs_dest_put_and_free()`. Per-netns `sysctl_lblc_expiration` defaults to 24 hours and controls full-expiry age; table pressure uses a shorter `ENTRY_TIMEOUT`. `timer_shutdown_sync()` and `ip_vs_lblc_flush()` clear service state on scheduler unbind.

## Dependencies and Integration Points
Depends on IPVS service/destination data structures, RCU hlist traversal, service scheduler locks, jiffies timers, hash helpers, netns sysctl registration, and the scheduler registry in `ip_vs_sched.c`. It integrates with destination availability and weight updates through the shared destination list and with user tuning through `/proc/sys/net/ipv4/vs/lblc_expiration`.

## Risks
Correctness depends on RCU lifetime of cached destinations and on decrementing `entries` for every deletion path. The cache can keep traffic pinned to a weak server until overload criteria trigger. Expiration and scheduling both touch hash buckets, so lock coverage around deletion and `dead` handling is important. IPv6 hashing folds all address words into one value, so collisions are expected and must remain harmless. Sysctls are hidden for unprivileged net namespaces by passing zero table size.

## Test Signals
Useful tests create an `lblc` service, repeatedly hit the same destination IP, and verify stable real-server selection until weight, overload, or availability changes. Exercise zero-weight quiescing, table expiry through `lblc_expiration`, service teardown under active cache entries, IPv4 and IPv6 destination keys, and logs from `ip_vs_scheduler_err()` when no destination is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_lblc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_lblcr.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_lblcr.c

## Purpose
Implements the IPVS `lblcr` scheduler, locality-based least connection with replication. Instead of caching one real server per destination address, it caches a set of real servers, allowing a hot destination to replicate across multiple servers and later shrink the set after inactivity.

## Important APIs, Types, and Functions
The module exposes `ip_vs_lblcr_scheduler` with `init_service`, `done_service`, and `schedule` callbacks, plus per-netns `lblcr_expiration` sysctl registration. `struct ip_vs_dest_set` and `struct ip_vs_dest_set_elem` manage the replicated server set with RCU list deletion. `struct ip_vs_lblcr_entry` maps a destination address to that set, while `struct ip_vs_lblcr_table` holds hash buckets, timer state, entry counters, and service backpointer. Key helpers are `ip_vs_dest_set_min()`, `ip_vs_dest_set_max()`, `ip_vs_dest_set_insert()`, `ip_vs_dest_set_erase()`, `ip_vs_lblcr_new()`, `ip_vs_lblcr_check_expire()`, and `ip_vs_lblcr_schedule()`.

## Control Flow
Service initialization allocates a hash table and starts periodic GC. On schedule, the code looks up `iph->daddr`; if an entry exists, it selects the weighted least loaded available server inside that entry's set. If the set has more than one server and has not been modified for the configured expiration interval, it removes the most loaded member to reduce replication. If the selected member is missing or overloaded, global weighted least-connection selection picks a new server and inserts it into the set. If no entry exists, global selection creates a new entry containing the selected server.

## State and Persistence
Per-service state is the LBLCR hash table in `svc->sched_data`. Each destination-set element holds an IPVS destination reference until RCU cleanup. `lastuse` controls whole-entry expiration and `set.lastmod` controls replicated-set shrinkage. The per-netns expiration sysctl defaults to 24 hours; table pressure expiration uses six-minute idle age. State is volatile and rebuilt from traffic.

## Dependencies and Integration Points
Uses IPVS scheduler registration, destination reference management, service locks, RCU list/hlist primitives, jiffies timers, kernel sysctl registration, and address/hash helpers from `net/ip_vs.h`. It is selected by services configured with scheduler name `lblcr`, and it observes real-server state through destination flags, weights, and active/inactive connection counters.

## Risks
The scheduler mixes RCU readers with locked mutation of entry lists and destination sets, so delayed frees and counter updates must stay paired. `ip_vs_dest_set_eraseall()` schedules RCU frees without resetting `set.size`, which is acceptable during entry destruction but would be risky if reused elsewhere. Replication can grow hot entries until shrink timers run. Global and per-set weighted comparisons must avoid zero-weight destinations. Cache expiry under traffic is timer-driven, so tests need to account for jiffies and delayed RCU reclamation.

## Test Signals
Validate that a repeated destination starts with one server, gains another when the cached server is overloaded, and later drops the most loaded replicated member after `lblcr_expiration`. Cover unavailable/zero-weight servers, IPv6 hash keys, full-table expiry, service removal, duplicate insertion protection, and error handling when all destinations are overloaded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_lblcr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_lc.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_lc.c

## Purpose
Implements the basic IPVS least-connection scheduler `lc`, selecting the available real server with the lowest connection overhead.

## Important APIs, Types, and Functions
`ip_vs_lc_schedule()` is the only scheduler operation. It scans `svc->destinations` and compares `ip_vs_dest_conn_overhead(dest)`, which weights active connections more heavily than inactive ones. `ip_vs_lc_scheduler` registers the module under scheduler name `lc`.

## Control Flow
On every scheduling request, the function traverses destinations under RCU list rules, skips overloaded servers and zero-weight quiesced servers, and tracks the destination with the smallest overhead. It returns `NULL` and emits `ip_vs_scheduler_err()` if no eligible destination exists. Module init and exit register and unregister the scheduler, with `synchronize_rcu()` after unregister.

## State and Persistence
This scheduler has no private per-service state. It relies entirely on live IPVS destination counters, flags, and weights. State changes are driven externally by connection tracking and service configuration.

## Dependencies and Integration Points
Depends on the IPVS scheduler registry, `struct ip_vs_service`, `struct ip_vs_dest`, RCU destination lists, atomic destination counters, and shared debug/error helpers. It is invoked by `ip_vs_schedule()` for services configured with scheduler `lc`.

## Risks
The algorithm ignores weights except for treating zero as quiesced, so heterogeneous backends should use `wlc`, `sed`, or related schedulers. It depends on accurate active/inactive counter transitions from protocol handlers. Tie-breaking favors the earliest destination in list order.

## Test Signals
Configure multiple real servers with different connection counters and verify the lowest overhead is chosen. Check zero-weight and `IP_VS_DEST_F_OVERLOAD` exclusion, no-destination error logs, and module load/unload registration messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_lc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_mh.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_mh.c

## Purpose
Implements the IPVS Maglev hashing scheduler `mh`. It builds a per-service lookup table from destination permutations and uses a hash of source address, and optionally source/destination port, to select a stable destination with minimal remapping when the destination set changes.

## Important APIs, Types, and Functions
`struct ip_vs_mh_state` stores the lookup table, temporary destination setup array, two hsiphash keys, GCD of weights, and right-shift compression. `struct ip_vs_mh_lookup` stores RCU destination pointers. `ip_vs_mh_init_svc()`, `ip_vs_mh_dest_changed()`, and `ip_vs_mh_done_svc()` manage per-service state. `ip_vs_mh_permutate()` computes Maglev offset/skip values, `ip_vs_mh_populate()` fills the lookup table, `ip_vs_mh_get()` and `ip_vs_mh_get_fallback()` select destinations, and `ip_vs_mh_schedule()` is the scheduler callback.

## Control Flow
Initialization allocates the lookup table, initializes deterministic hash secrets, computes weight GCD and shift, and populates the Maglev table. Destination add, delete, or update recomputes the weight compression and fully reassigns the lookup table. Scheduling chooses the client-side hash address based on packet direction; with `IP_VS_SVC_F_SCHED_MH_PORT`, it reads TCP/UDP/SCTP ports from the packet. It hashes into the lookup table and returns the destination if weight and overload flags permit. With `IP_VS_SVC_F_SCHED_MH_FALLBACK`, an unavailable bucket triggers a deterministic search for another usable bucket.

## State and Persistence
State is per-service and lasts while the scheduler is bound. Lookup entries hold real-server references; `ip_vs_mh_reset()` releases existing references before reassignment or teardown. Hash keys are fixed constants, so mapping is deterministic across instances with the same service configuration. Weight distribution uses `last_weight`, GCD, and a shift to fit large weights into the finite table.

## Dependencies and Integration Points
Uses IPVS scheduler flags, destination lists, destination reference management, RCU pointer access, `hsiphash`, bitmaps, GCD and bit helpers, and transport header parsing from SKBs. It integrates with IPVS service flags supplied by user configuration, especially fallback and port-sensitive hashing.

## Risks
`svc->num_dests > IP_VS_MH_TAB_SIZE` fails reassignment, so configured table size bounds service scale. Reassignment is a full-table operation and can fail allocation of the temporary bitmap or setup array. Port extraction returns zero for unsupported protocols or truncated headers, reducing entropy. Fixed hash secrets are stable but not random. Fallback changes strict Maglev affinity when a chosen destination is unavailable.

## Test Signals
Test deterministic selection for repeated source addresses, changed mapping after destination add/delete/update, weighted distribution with varied `last_weight`, fallback behavior for overloaded or zero-weight destinations, `mh-port` hashing differences, IPv6 folded-address hashing, and failure handling when destination count exceeds table size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_mh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_nfct.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_nfct.c

## Purpose
Bridges IPVS connection state with Netfilter conntrack. It adjusts conntrack reply tuples for IPVS NAT, creates expectations for related flows, confirms conntracks in IPVS hooks, and drops conntrack entries when an IPVS connection terminates.

## Important APIs, Types, and Functions
`ip_vs_update_conntrack()` alters unconfirmed conntrack reply tuples for NATed IPVS connections. `ip_vs_confirm_conntrack()` wraps `nf_conntrack_confirm()`. `ip_vs_nfct_expect_related()` allocates and installs related-flow expectations with `ip_vs_nfct_expect_callback()` as the expectation callback. `ip_vs_conn_drop_conntrack()` searches and kills the original client-to-virtual conntrack tuple. Debug macros format conntrack and IPVS tuples.

## Control Flow
When a packet is associated with a NAT IPVS connection, `ip_vs_update_conntrack()` exits unless conntrack exists, is unconfirmed and alive, the forwarding method is MASQ, the connection is not one-packet, and the packet is in the original direction. For outbound-inbound and inbound-outbound cases it rewrites the reply source or destination tuple to match the real or virtual endpoint, then calls `nf_conntrack_alter_reply()`. Expectations are installed from IPVS app helpers with optional wildcard source port; when conntrack creates the related flow, the callback finds the matching IPVS connection in either direction and alters the reply tuple accordingly.

## State and Persistence
The file owns no standalone state. It mutates existing `struct nf_conn` tuples and optional sequence-adjust extensions, and it relies on existing `struct ip_vs_conn` fields for endpoints, ports, forwarding method, flags, and app binding. Expectations live in conntrack until consumed or expired.

## Dependencies and Integration Points
Depends on Netfilter conntrack core, expectation, helper, sequence adjustment, zones, and tuple APIs. It integrates with IPVS NAT and app helper paths, especially FTP-like related connections, and with IPVS connection expiration through `ip_vs_conn_drop_conntrack()`.

## Risks
Tuple alteration is valid only before conntrack confirmation; late calls are intentionally ignored. Related-flow correctness depends on conntrack helper modules being installed for the same protocol and ports. Sequence-adjust extension allocation can fail and blocks tuple update for TCP app helpers. Only MASQ connections are altered, so other forwarding methods must not expect NAT-aware conntrack replies. The drop path uses default conntrack zone only.

## Test Signals
Exercise NATed TCP/UDP services with conntrack enabled, FTP active/passive related flows, confirmed versus unconfirmed conntracks, one-packet UDP services, app helper sequence adjustment, and connection expiration causing conntrack kill. Observe conntrack table tuples before and after IPVS hook processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_nfct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_nq.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_nq.c

## Purpose
Implements the IPVS never-queue scheduler `nq`, a two-speed adaptive load sharing algorithm that immediately selects an idle eligible server when one exists and otherwise falls back to shortest expected delay.

## Important APIs, Types, and Functions
`ip_vs_nq_dest_overhead()` computes expected overhead as active connections plus one. `ip_vs_nq_schedule()` scans destinations and selects either the first idle eligible destination or the minimum `(activeconns + 1) / weight` destination. `ip_vs_nq_scheduler` registers the scheduler under name `nq`.

## Control Flow
The scheduler iterates `svc->destinations`, skipping overloaded and zero-weight servers. If it sees a server with zero active connections, it returns that server immediately. Otherwise it compares expected load with cross multiplication to avoid floating point. If no server is eligible, it logs a scheduler error and returns `NULL`.

## State and Persistence
No private state is kept. Decisions are computed from current destination weights, flags, and active connection counters.

## Dependencies and Integration Points
Uses IPVS service destination lists, atomic counters, destination flags, module registration, and the common scheduler callback contract. It is useful for heterogeneous pools where idle resources should be consumed before queueing on busier servers.

## Risks
Immediate return on the first idle destination makes list order important among idle servers. The algorithm ignores inactive connections in its cost function. Weight changes are read atomically during traversal and may change between selection and connection creation.

## Test Signals
Test that any idle eligible server is preferred over non-idle lower weighted-delay choices, that overloaded and zero-weight servers are skipped, that weighted SED comparison is used when all servers are busy, and that no-destination paths emit rate-limited scheduler errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_nq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_ovf.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_ovf.c

## Purpose
Implements the IPVS overflow scheduler `ovf`. It keeps traffic on the highest-weight destination until its active connections exceed its weight, then overflows to the next highest eligible destination.

## Important APIs, Types, and Functions
`ip_vs_ovf_schedule()` is the scheduler callback. It compares destination weights, active connection counts, and overload flags. `ip_vs_ovf_scheduler` registers scheduler name `ovf`.

## Control Flow
Each schedule call scans all destinations. A destination is skipped if it is overloaded, has zero weight, or has active connections greater than its weight. Among remaining destinations, the highest weight wins. If no destination satisfies the threshold, the scheduler reports no destination available.

## State and Persistence
No scheduler-private state is maintained. Behavior depends only on live active connection counters and configured weights.

## Dependencies and Integration Points
Uses IPVS scheduler registration, service destination RCU traversal, atomic destination fields, and shared logging. It is invoked by the normal IPVS scheduler path for services using `ovf`.

## Risks
The algorithm uses active connections only, so it may be unsuitable for UDP-like traffic where active counts do not represent queued work. The comparison condition allows active connections equal to weight but rejects greater than weight. It is intentionally biased toward highest weights and may leave lower-weight servers idle until overflow.

## Test Signals
Verify highest-weight selection under threshold, overflow when active connections exceed weight, zero-weight and overload exclusion, equality-at-threshold behavior, and no-destination logging when every destination is over threshold.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_ovf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_pe.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_pe.c

## Purpose
Provides the registry for IPVS persistence engines. Persistence engines extract and compare protocol-specific persistence keys, such as SIP Call-ID, so IPVS templates can be keyed by data other than the client address.

## Important APIs, Types, and Functions
`__ip_vs_pe_getbyname()` looks up a persistence engine under RCU and takes a module reference. `ip_vs_pe_getbyname()` adds module autoload via `request_module("ip_vs_pe_%s", name)`. `register_ip_vs_pe()` and `unregister_ip_vs_pe()` add and remove engines from the global RCU list and adjust the IPVS module use count. The list is protected by `ip_vs_pe_mutex`.

## Control Flow
Consumers request an engine by name; the registry scans the RCU list and tries `try_module_get()` before returning a matching engine. If not found, module autoload is attempted and lookup repeats. Registration rejects duplicate names and links the engine with `list_add_rcu()`. Unregistration removes with `list_del_rcu()` and decrements the IPVS use count; callers are expected to synchronize RCU on module exit.

## State and Persistence
Global state is the `ip_vs_pe` list and module reference counts. No per-netns state is stored here. Registered engines persist until their module unregisters.

## Dependencies and Integration Points
Depends on Linux module reference counting, RCU list traversal, mutexes, and `ip_vs_use_count_inc/dec()`. It integrates with service configuration, connection template lookup, sync processing, and protocol-specific PE modules such as `ip_vs_pe_sip.c`.

## Risks
Callers must release returned engines with `ip_vs_pe_put()` or equivalent module put. Unregister does not validate list membership in this file, so registry users must obey lifecycle ordering. RCU grace periods are handled by provider modules, not centrally. Duplicate-name detection is the main consistency check.

## Test Signals
Load and unload a persistence engine, request it by name before and after module autoload, register duplicate names and expect failure, and verify module refcounts prevent unloading while an engine is in use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_pe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_pe_sip.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_pe_sip.c

## Purpose
Implements the SIP persistence engine for IPVS. It extracts the SIP Call-ID header from UDP SIP payloads and uses it as persistence data for connection templates, allowing all messages in a SIP dialog to map consistently.

## Important APIs, Types, and Functions
`ip_vs_sip_pe` registers PE name `sip`. `ip_vs_sip_fill_param()` parses a packet and fills `ip_vs_conn_param.pe_data`. `get_callid()` uses conntrack SIP parsing via `ct_sip_get_header()` to locate and validate the Call-ID. `ip_vs_sip_ct_match()` compares template connections against Call-ID data. `ip_vs_sip_hashkey_raw()` hashes Call-ID data for template lookup, `ip_vs_sip_show_pe_data()` exposes the data, and `ip_vs_sip_conn_out()` creates UDP outgoing connections through `ip_vs_new_conn_out()`.

## Control Flow
When persistence needs a SIP key, the fill function parses the IP header, rejects non-UDP traffic, linearizes the SKB, skips UDP header bytes, extracts Call-ID, validates maximum length and line termination, and copies the header value into `p->pe_data`. Template matching then checks address family, client address, virtual address and port, template flag, protocol, and exact persistence data. Module init registers the PE; module exit unregisters and waits for RCU readers.

## State and Persistence
The module has no mutable global state beyond registration. Per-connection persistence state is a copied Call-ID buffer stored in connection parameters and templates. The maximum data length is bounded by `IP_VS_PEDATA_MAXLEN`.

## Dependencies and Integration Points
Depends on IPVS PE registration, IPVS packet header parsing, SKB linearization, Jenkins hash, Netfilter SIP conntrack parser definitions, UDP header layout, and IPVS connection/template lookup. It works with the sync daemon because version 1 sync messages can carry PE name and PE data.

## Risks
Only UDP SIP is supported. `skb_linearize()` can fail and may be costly. Header parsing must handle folded or malformed SIP headers as implemented by conntrack SIP helpers; overly long or unterminated Call-ID values reject persistence and fall back to default behavior. `p->pe_data` allocation uses `GFP_ATOMIC`, so memory pressure can disable SIP persistence for a packet.

## Test Signals
Send SIP UDP requests with valid, missing, malformed, oversized, and differently cased Call-ID headers. Verify template reuse by Call-ID across client ports, fallback when parsing fails, sync of PE data to backup nodes, and no persistence for non-UDP SIP-like traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_pe_sip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_proto.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_proto.c

## Purpose
Implements the core IPVS protocol registry and per-netns protocol data setup. It registers protocol handlers for TCP, UDP, SCTP, AH, and ESP, provides lookup helpers, forwards timeout-change events, and supplies shared TCP/UDP packet debug formatting.

## Important APIs, Types, and Functions
Global registration uses `register_ip_vs_protocol()` and `unregister_ip_vs_protocol()` over `ip_vs_proto_table`. Per-netns data uses `register_ip_vs_proto_netns()` and `unregister_ip_vs_proto_netns()` with `struct ip_vs_proto_data`. Exported lookups are `ip_vs_proto_get()` and `ip_vs_proto_data_get()`. `ip_vs_protocol_timeout_change()` invokes each protocol's timeout-change hook. `ip_vs_state_name()` formats connection state names, and `ip_vs_tcpudp_debug_packet()` prints IPv4/IPv6 packet endpoint details.

## Control Flow
IPVS module init calls `ip_vs_protocol_init()`, registering compiled-in protocol structures and logging their names. Each network namespace calls `ip_vs_protocol_net_init()`, which allocates `ip_vs_proto_data` for each compiled protocol and lets the protocol initialize timeout tables or app lists. Cleanup walks each hash bucket and unregisters all per-netns data, then module cleanup removes global handlers.

## State and Persistence
Global protocol state is a fixed 32-bucket hash table keyed by protocol number. Per-netns state is stored in `netns_ipvs->proto_data_table`, including protocol-specific timeout tables, app counters, and app lists. State persists for the lifetime of the module or network namespace.

## Dependencies and Integration Points
Depends on compiled protocol objects from `ip_vs_proto_tcp.c`, `ip_vs_proto_udp.c`, `ip_vs_proto_sctp.c`, and `ip_vs_proto_ah_esp.c`. It integrates with connection creation, packet scheduling, app helpers, state-name reporting, sysctl timeout propagation, and proc/debug output.

## Risks
The global protocol table is intentionally unlocked because registration occurs only during module load/unload; adding dynamic protocol modules would require synchronization. Per-netns initialization must unwind correctly on allocation failure. The protocol log buffer is fixed at 64 bytes and assumes the compiled protocol list fits. Debug packet parsing has limited IPv6 extension-header awareness and reports fragments specially.

## Test Signals
Verify protocol registration logs, lookup by protocol number, netns creation and teardown, timeout table allocation failures, protocol cleanup unloading all handlers, `ip_vs_state_name()` for templates and unknown protocols, and debug output for truncated, fragmented, IPv4, and IPv6 packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_proto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_proto_ah_esp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_proto_ah_esp.c

## Purpose
Provides IPVS protocol handlers for IPsec AH and ESP related traffic. Since AH/ESP do not expose transport ports, the handlers associate them with existing ISAKMP UDP/500 connections rather than scheduling new services directly.

## Important APIs, Types, and Functions
`ah_esp_conn_fill_param_proto()` creates a UDP/500 connection parameter from the IP header, respecting inverse direction. `ah_esp_conn_in_get()` and `ah_esp_conn_out_get()` look up matching IPVS connections. `ah_esp_conn_schedule()` always accepts the packet without scheduling. `ip_vs_protocol_ah` and `ip_vs_protocol_esp` are compiled conditionally and provide the `struct ip_vs_protocol` entries.

## Control Flow
For inbound or outbound AH/ESP packets, the handler fills an ISAKMP-style parameter and searches the IPVS connection table. If no connection exists, debug logging records an unknown related packet and the packet is allowed to pass. The scheduling hook sets verdict `NF_ACCEPT` because AH/ESP is handled only as related traffic.

## State and Persistence
No local state or timeout table is owned by this file. AH/ESP association depends on existing IPVS UDP/500 connection entries and their lifetimes.

## Dependencies and Integration Points
Depends on IPVS protocol registration, connection lookup helpers, IP header direction helpers, Netfilter verdicts, and UDP/ISAKMP port conventions. It integrates with IPsec VPN load balancing where IKE creates the controlling connection and AH/ESP follows it.

## Risks
Mapping all AH/ESP to UDP/500 control state is coarse and cannot distinguish multiple security associations beyond addresses and direction. The code does not NAT AH/ESP payloads and provides no state transition handler. Unknown related traffic is accepted, so policy enforcement must be elsewhere.

## Test Signals
Create IPVS services for IKE and verify AH/ESP packets find the expected connection in both directions. Test absence of an ISAKMP connection, inverse header handling, AH-only and ESP-only builds, and debug logs for unknown related packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_proto_ah_esp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_proto_sctp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_proto_sctp.c

## Purpose
Implements SCTP protocol support for IPVS, including connection scheduling, SNAT/DNAT port rewrite, CRC handling, SCTP association state transitions, per-netns timeout tables, and SCTP application helper binding.

## Important APIs, Types, and Functions
`sctp_conn_schedule()` finds services for new SCTP associations. `sctp_snat_handler()` and `sctp_dnat_handler()` rewrite source or destination ports and recompute SCTP CRC when needed. `sctp_csum_check()` validates CRC32c. `sctp_events` maps SCTP chunk types to IPVS events, and `sctp_states` is the state transition table. `set_sctp_state()` and `sctp_state_transition()` update connection state and active/inactive counters. `sctp_register_app()`, `sctp_unregister_app()`, and `sctp_app_conn_bind()` manage app helpers. `ip_vs_protocol_sctp` registers the protocol contract.

## Control Flow
Scheduling inspects the SCTP header and first chunk. It schedules only INIT packets unless sloppy SCTP mode is enabled, rejects ABORT as a connection opener, and handles ICMP-embedded headers by reading the first four bytes of ports. NAT handlers ensure the SCTP header is writable, optionally invoke app helpers, rewrite the port, and recompute CRC unless GSO or hardware SCTP CRC offload keeps checksum work deferred. State transitions read the first chunk, detect bundled ABORT after COOKIE chunks where relevant, map chunk type to an event, adjust `NOOUTPUT` direction handling, update active/inactive counters, assure conntrack controls on establishment, and set timeout from the per-netns table.

## State and Persistence
Per-netns state includes SCTP app hash tables and copied timeout table. Per-connection state includes IPVS SCTP state, timeout, old state, `NOOUTPUT`, inactive flag, and sequence/app metadata. The file owns static transition tables and timeout defaults.

## Dependencies and Integration Points
Depends on Linux SCTP headers, SCTP checksum support, IP/IPv6 checksum helpers, IPVS app helper APIs, IPVS service lookup, connection table lookups, sysctl sloppy SCTP, and Netfilter verdicts. It integrates with generic protocol registration in `ip_vs_proto.c`.

## Risks
Only the first chunk is inspected except for limited COOKIE plus ABORT detection, so unusual chunk bundling can affect state accuracy. CRC recomputation decisions depend on GSO and device `NETIF_F_SCTP_CRC`. `sctp_csum_check()` directly accesses `skb->data + sctphoff` after writability assumptions, so callers must ensure header presence. Sloppy mode permits scheduling non-INIT openers and can create broader matching behavior.

## Test Signals
Run SCTP association setup and shutdown through IPVS, including INIT, INIT-ACK, COOKIE-ECHO, COOKIE-ACK, DATA, SHUTDOWN, ABORT, and bundled COOKIE/ABORT cases. Validate NAT port rewrite and CRC, GSO/offload behavior, app helper binding, sloppy SCTP behavior, timeout state names, IPv6 fragments, and active/inactive counter transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_proto_sctp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_proto_tcp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_proto_tcp.c

## Purpose
Implements TCP protocol support for IPVS: new-connection scheduling, NAT port and checksum rewriting, TCP state tracking, per-netns timeout tables, secure TCP mode transitions, and TCP application helper binding.

## Important APIs, Types, and Functions
`tcp_conn_schedule()` locates a service and creates an IPVS connection for acceptable TCP openers. `tcp_snat_handler()` and `tcp_dnat_handler()` rewrite ports and update TCP checksums. `tcp_csum_check()` validates checksums before app payload mangling. `tcp_states` and `tcp_states_dos` are transition tables selected by `tcp_timeout_change()`. `set_tcp_state()` and `tcp_state_transition()` update connection state and active/inactive counters. `tcp_register_app()`, `tcp_unregister_app()`, `tcp_app_conn_bind()`, and `ip_vs_tcp_conn_listen()` provide helper and LISTEN-state support. `ip_vs_protocol_tcp` registers the protocol operations.

## Control Flow
Scheduling rejects RST openers and, unless sloppy TCP is enabled, non-SYN packets; ICMP paths only require embedded ports. A matching service may drop under overload via `ip_vs_todrop()`, schedule a real server, or invoke `ip_vs_leave()` on no destination. NAT handlers ensure TCP header writability, validate checksum before helper mangling, invoke app helpers, rewrite source or destination port, and choose fast incremental checksum, partial checksum adjustment, or full recomputation based on payload changes and SKB checksum mode. State transition reads TCP flags, applies input/output/input-only transition table rows, updates active/inactive counters, assures conntrack at ESTABLISHED, and refreshes timeout.

## State and Persistence
Per-netns TCP state is app helper hash tables, app counts, timeout table copy, and selected state table. Per-connection state includes TCP state, old state, timeout, flags, app binding, and destination counters. Static timeout defaults cover all IPVS TCP states.

## Dependencies and Integration Points
Depends on TCP/IP header helpers, IPv6 checksum support, IPVS app helper APIs, connection/service lookup, sysctls for sloppy and secure TCP, Netfilter verdicts, and the generic protocol registry. TCP app helpers are bound only for MASQ/NAT forwarding.

## Risks
State tables are dense and easy to regress, especially `NOOUTPUT` and secure TCP modes. App helper payload mangling changes checksum behavior and can require seqadj conntrack support elsewhere. Header parsing for ICMP-embedded packets sees only ports. Counter transitions depend on the active-state table matching protocol semantics. Sloppy mode can schedule midstream packets.

## Test Signals
Cover normal SYN/SYN-ACK/ACK establishment, FIN/RST teardown, secure TCP mode, sloppy TCP mode, Active FTP SYN+ACK scheduling, app helper NAT with checksum and sequence adjustments, IPv4/IPv6 checksum modes, CHECKSUM_PARTIAL/COMPLETE/NONE paths, LISTEN timeout setup, and active/inactive destination counter changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_proto_tcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_proto_udp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_proto_udp.c

## Purpose
Implements UDP protocol support for IPVS, including datagram service scheduling, NAT port and checksum rewriting, a simple timeout/state model, and UDP application helper binding.

## Important APIs, Types, and Functions
`udp_conn_schedule()` finds a virtual service by packet ports and schedules a connection. `udp_snat_handler()` and `udp_dnat_handler()` rewrite UDP source or destination ports. `udp_csum_check()` validates UDP checksums when present. `udp_register_app()`, `udp_unregister_app()`, and `udp_app_conn_bind()` manage UDP helpers. `udp_state_transition()` refreshes timeout and assures conntrack on output. `ip_vs_protocol_udp` registers the protocol.

## Control Flow
Scheduling extracts UDP ports from the packet or ICMP payload, drops truncated packets, finds a matching service by mark/protocol/address/port, optionally drops under IPVS overload, and calls `ip_vs_schedule()` or `ip_vs_leave()`. NAT handlers ensure header writability, invoke app helpers when present, rewrite the selected port, and update checksums. UDP with zero checksum avoids incremental checksum work except when full recomputation is forced by payload changes or partial checksum state. The state transition simply sets the normal UDP timeout.

## State and Persistence
Per-netns UDP state includes helper hash tables and a copied timeout table with a normal five-minute timeout. Per-connection state is minimal: timeout, app pointer, flags, and endpoint data. UDP has one normal state for state-name reporting.

## Dependencies and Integration Points
Depends on UDP/IP headers, IPv6 checksum helpers, IPVS service lookup and NAT app APIs, SKB checksum modes, Netfilter verdicts, and generic protocol registration. Helpers bind only for MASQ/NAT forwarding.

## Risks
UDP zero-checksum handling differs from TCP; full recomputation may create `CSUM_MANGLED_0`. Stateless UDP services depend on timeout tuning for connection table size. App helper mangling can force full checksum computation. ICMP handling only has embedded ports. Fragmented IPv6 packets bypass NAT header rewrite for non-first fragments.

## Test Signals
Test UDP service scheduling, one-packet services, zero and nonzero UDP checksums, IPv4/IPv6 NAT rewrite, CHECKSUM_PARTIAL/COMPLETE/NONE paths, app helper binding and payload changes, timeout refresh on traffic, overload drops, and truncated packet drops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_proto_udp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_rr.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_rr.c

## Purpose
Implements the basic IPVS round-robin scheduler `rr`, selecting the next eligible destination in service list order.

## Important APIs, Types, and Functions
`ip_vs_rr_init_svc()` stores the current list position in `svc->sched_data`. `ip_vs_rr_del_dest()` repairs that pointer when the current destination is deleted. `ip_vs_rr_schedule()` advances through destinations and picks the next non-overloaded positive-weight server. `ip_vs_rr_scheduler` registers callbacks for service init, destination deletion, and scheduling.

## Control Flow
Scheduling takes `svc->sched_lock`, starts from the saved position, scans forward with RCU list continuation, and wraps at most once to avoid looping forever if the previous destination was unlinked. On success it updates `svc->sched_data` to the selected destination's list node. If no eligible server is found, it releases the lock and logs a scheduler error.

## State and Persistence
The only private state is the current list pointer stored in `svc->sched_data`; it persists for the service scheduler binding and is adjusted on destination deletion. It does not store weights or counters.

## Dependencies and Integration Points
Uses IPVS service destination lists, service scheduler lock, destination flags and weights, scheduler registry, and RCU. It is used by services configured with scheduler `rr`.

## Risks
Correct pointer repair on deletion is critical because `sched_data` can point at a destination already unlinked from the active list. Selection ignores weights except zero-weight quiescing. List order controls distribution.

## Test Signals
Verify cyclic distribution across eligible destinations, skip of zero-weight and overloaded servers, deletion of the current destination, service with no destinations, and module unregister RCU synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_rr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_sched.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_sched.c

## Purpose
Provides the central registry and binding logic for IPVS schedulers. It lets services bind to scheduler modules, autoload schedulers by name, track module references, and format common scheduler error messages.

## Important APIs, Types, and Functions
`ip_vs_bind_scheduler()` calls a scheduler's `init_service()` and publishes it with RCU. `ip_vs_unbind_scheduler()` calls `done_service()`. `ip_vs_scheduler_get()` looks up a scheduler by name and autoloads `ip_vs_<name>` if needed. `ip_vs_scheduler_put()` releases module references. `register_ip_vs_scheduler()` and `unregister_ip_vs_scheduler()` manage the global list under `ip_vs_sched_mutex`. `ip_vs_scheduler_err()` prints service-specific rate-limited errors and is exported.

## Control Flow
Scheduler modules register their static `struct ip_vs_scheduler` during module init. Service configuration obtains a scheduler by name, which tries `try_module_get()` atomically while scanning the list. Binding initializes per-service scheduler data before assigning `svc->scheduler`. Unregister removes the scheduler from the list and decrements the IPVS use count; module exit code usually waits for RCU readers.

## State and Persistence
Global state is the `ip_vs_schedulers` list and module/IPVS use counts. Per-service state is owned by each scheduler but its lifecycle is initiated here. The registry persists for the IPVS module lifetime.

## Dependencies and Integration Points
Depends on Linux modules, request_module, mutexes, RCU pointer assignment, IPVS service structures, and IPVS global use counting. Every scheduler module in this subset registers through this file.

## Risks
Binding does not roll back partial scheduler init except by returning the init error; scheduler implementations must clean up their own failed init paths. `ip_vs_unbind_scheduler()` assumes the caller controls setting `svc->scheduler` to NULL. Registry uniqueness is name-based. Scheduler modules must synchronize RCU after unregistering if readers can still hold callbacks.

## Test Signals
Load schedulers by name, autoload missing modules, bind and unbind services, duplicate scheduler registration, unregister while services are draining, IPv4/IPv6/fwmark error formatting, and failure injection in scheduler `init_service()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_sed.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_sed.c

## Purpose
Implements the IPVS shortest expected delay scheduler `sed`. It selects the destination minimizing `(active connections + 1) / weight`, modeling the expected delay for the incoming connection.

## Important APIs, Types, and Functions
`ip_vs_sed_dest_overhead()` returns `activeconns + 1`. `ip_vs_sed_schedule()` finds the eligible server with the lowest weighted expected delay using cross multiplication. `ip_vs_sed_scheduler` registers scheduler name `sed`.

## Control Flow
The scheduler first finds an eligible non-overloaded positive-weight destination to seed the comparison, then continues scanning the destination list for a lower expected delay. If no eligible destination exists, it reports an error and returns `NULL`. Module init and exit register/unregister the scheduler and wait for RCU readers.

## State and Persistence
No private scheduler state exists. Decisions derive from current active connection counters and destination weights.

## Dependencies and Integration Points
Uses IPVS destination lists, atomic counters and weights, common scheduler registry, and debug logging. It is closely related to `nq`, but without the immediate idle-server shortcut.

## Risks
It ignores inactive connections entirely. The `+1` incoming-job model can prefer a higher-weight server even when raw active counts are higher. The initial seed path must skip zero-weight and overloaded destinations to avoid divide-by-zero-equivalent comparisons.

## Test Signals
Test weighted expected-delay choices across heterogeneous weights, all-busy versus idle cases, zero-weight quiescing, overload exclusion, and no-destination logs. Compare against `wlc` and `nq` for expected differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_sed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_sh.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_sh.c

## Purpose
Implements the IPVS source hashing scheduler `sh`. It maps a hash of the client-side source address, optionally including a port, to a fixed per-service bucket table for stable client affinity.

## Important APIs, Types, and Functions
`struct ip_vs_sh_state` contains a fixed bucket array of RCU destination pointers. `ip_vs_sh_reassign()` rebuilds bucket assignments according to destination list order and weights. `ip_vs_sh_get()` selects a bucket directly, while `ip_vs_sh_get_fallback()` searches deterministically when the selected server is unavailable. `ip_vs_sh_get_port()` extracts TCP/UDP/SCTP ports when port hashing is enabled. `ip_vs_sh_schedule()` is the scheduler callback, and `ip_vs_sh_scheduler` handles service init, teardown, destination changes, and schedule.

## Control Flow
Service initialization allocates state and fills buckets by walking destinations, repeating each destination by weight. Destination add/delete/update triggers full reassignment. Scheduling chooses `iph->saddr` or `iph->daddr` depending on inverse direction, optionally extracts a transport port, hashes into the bucket table, and returns the selected destination if available. If fallback flag is set, unavailable buckets trigger a bounded deterministic search through alternate hashes.

## State and Persistence
Per-service state is the bucket table in `svc->sched_data`. Each occupied bucket holds a destination reference, released during reassignment and teardown. The table is volatile and rebuilt on destination changes.

## Dependencies and Integration Points
Uses IPVS scheduler flags `IP_VS_SVC_F_SCHED_SH_PORT` and fallback, destination reference management, RCU, hash helpers, and SKB transport header parsing. It integrates with cache-bypass style deployments where strict affinity can intentionally return no destination when the assigned cache is unavailable.

## Risks
Table size is fixed by config and collision/weight behavior depends on bucket count. Reassignment repeats destinations by weight but does not validate negative or rapidly changing weights beyond atomic reads. Without fallback, a single unavailable bucket returns no destination even if other servers are healthy. Port extraction fails to zero on truncated headers.

## Test Signals
Verify stable client-to-server mapping, weight-influenced bucket counts, fallback on overloaded or zero-weight assigned servers, strict no-fallback behavior, destination add/delete reassignment, IPv6 folded hashing, port hashing, and RCU cleanup on service removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_sh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_sync.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_sync.c

## Purpose
Implements IPVS master/backup connection synchronization over multicast UDP. Master threads batch selected IPVS connection state into version 0 or version 1 sync messages; backup threads receive, validate, decode, and create or update local connection entries.

## Important APIs, Types, and Functions
Wire structs include `ip_vs_sync_conn_v0`, `ip_vs_sync_v4`, `ip_vs_sync_v6`, `ip_vs_sync_mesg_v0`, and `ip_vs_sync_mesg`. `ip_vs_sync_conn()` is the public sender for connection sync, with `ip_vs_sync_conn_v0()` for legacy format. `ip_vs_sync_conn_needed()` rate-limits syncs by state, thresholds, refresh period, retries, and persistence mode. `ip_vs_process_message()` and `ip_vs_process_message_v0()` receive messages. `ip_vs_proc_sync_conn()` parses one v1 connection, and `ip_vs_proc_conn()` creates or updates the IPVS connection. `start_sync_thread()` and `stop_sync_thread()` manage kernel threads, sockets, queues, and daemon state. `ip_vs_sync_net_init()` and `ip_vs_sync_net_cleanup()` initialize per-netns locks and stop daemons.

## Control Flow
On the master, protocol/state changes call `ip_vs_sync_conn()`. It skips one-packet connections, checks sync policy, computes message length including sequence options and persistence data, appends the connection to the current per-thread buffer, and queues full buffers for the master thread. Master threads dequeue buffers or flush old current buffers and send them with `kernel_sendmsg()`. On the backup, receive threads wait on UDP socket queues, read datagrams, validate size and sync ID, parse v1 or v0 format, validate protocol state, resolve persistence engines when PE data is present, then update or create IPVS connection entries and bind destinations if available.

## State and Persistence
Per-netns state includes master and backup configs, sync state flags, thread arrays, master per-thread queues, current sync buffers, locks, thread mask, and socket buffers. Sync message state is transient, but decoded backup connections persist in the IPVS connection table. Version 1 preserves IPv6, fwmark, timeout, persistence engine name/data, and sequence options; version 0 is IPv4 only and loses some template/fwmark fidelity.

## Dependencies and Integration Points
Depends on kernel sockets, multicast group join APIs, kthreads, delayed work, RCU connection/destination lookup, IPVS sysctls, persistence engine registry, protocol registry, and connection table allocation. It is controlled by IPVS daemon configuration and integrates with active connection state transitions in protocol handlers.

## Risks
The file combines wire-format parsing, socket lifecycle, and connection-table mutation, so bounds checks and lock ordering are critical. Version 1 optional parameter parsing must reject duplicate, oversized, mandatory unknown, or truncated parameters. Master queue growth is bounded by sysctls but allocation happens in atomic context. Backup destination binding assumes homogeneous pools for synced services. Thread startup holds RTNL and sync mutex with careful trylock ordering; error cleanup must stop partially started threads and release sockets. Multicast MTU and `sync_maxlen` determine message fragmentation risk.

## Test Signals
Run master/backup daemons with IPv4 and IPv6 multicast, multiple sync ports, sync ID filtering, version 0 and version 1 modes, TCP/SCTP/UDP state changes, persistence templates with SIP PE data, sequence options, fwmark services, daemon start/stop races, malformed datagrams, queue pressure, socket send `EAGAIN`, backup without preexisting services, and netns cleanup while daemons are running.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_twos.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_twos.c

## Purpose
Implements the IPVS power-of-two-random-choices scheduler `twos`. It randomly samples two weighted destinations and returns the one with lower connection overhead normalized by weight.

## Important APIs, Types, and Functions
`ip_vs_twos_schedule()` performs all scheduling. It uses `get_random_u32_below()` for random weighted picks, `ip_vs_dest_conn_overhead()` for load, and `ip_vs_twos_scheduler` for module registration.

## Control Flow
The scheduler first sums positive weights for non-overloaded destinations and records whether any eligible destination exists. It draws two random numbers in the inclusive weight range, walks the destinations again subtracting weights until each draw selects a destination, then compares `overhead / weight` via cross multiplication. If the second choice is better, it returns it; otherwise it returns the first choice.

## State and Persistence
No private state exists. Randomness and current destination counters drive each decision.

## Dependencies and Integration Points
Depends on IPVS destination counters and weights, RCU destination traversal, Linux random APIs, and scheduler registration. It is useful for large pools where full least-connection scans are more expensive than randomized sampling.

## Risks
The code adds one to `total_weight` before drawing, making boundary behavior important; if a draw remains beyond all cumulative weights, the initialized fallback choice can survive. Randomness makes exact distribution tests probabilistic. The comparison uses integer multiplication and assumes selected weights are positive.

## Test Signals
Use deterministic random stubbing or statistical tests to confirm weighted sampling and lower normalized overhead selection. Cover single-destination pools, all zero/overloaded destinations, large weights, and repeated scheduling distribution compared with WLC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_twos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_wlc.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_wlc.c

## Purpose
Implements the IPVS weighted least-connection scheduler `wlc`, selecting the eligible real server with the lowest connection overhead divided by destination weight.

## Important APIs, Types, and Functions
`ip_vs_wlc_schedule()` scans destinations and compares `ip_vs_dest_conn_overhead(dest) / weight` using cross multiplication. `ip_vs_wlc_scheduler` registers scheduler name `wlc`.

## Control Flow
The scheduler finds the first non-overloaded destination with positive weight and uses it as the initial least-loaded server. It then scans the remaining destinations, skipping overloaded ones, and chooses a new least server when `old_overhead * new_weight > new_overhead * old_weight`. It returns `NULL` with a scheduler error if no positive-weight destination exists.

## State and Persistence
No private state exists. It relies on live destination weight, active connection, inactive connection, overload, and refcount data.

## Dependencies and Integration Points
Uses IPVS destination lists, `ip_vs_dest_conn_overhead()`, atomic weights/counters, scheduler registration, and shared debug output. It is the weighted counterpart to `lc`.

## Risks
Weight reads are not locked against concurrent configuration changes, so a weight can change between initial filtering and later comparison. The second pass skips overload but does not explicitly skip zero weight in the comparison path, relying on destination state assumptions after the seeded positive weight. Distribution depends on accurate active/inactive counters.

## Test Signals
Test heterogeneous weights with controlled active/inactive counters, zero-weight quiescing, overload exclusion, no eligible destination, concurrent weight update behavior, and comparison against `lc` for equal weights.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_wlc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_wrr.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_wrr.c

## Purpose
Implements the IPVS weighted round-robin scheduler `wrr`. It cycles through destinations in list order while using maximum weight and GCD-derived weight steps to approximate weighted distribution.

## Important APIs, Types, and Functions
`struct ip_vs_wrr_mark` stores current list position `cl`, current required weight `cw`, maximum effective weight `mw`, and decrement interval `di`. `ip_vs_wrr_gcd_weight()` and `ip_vs_wrr_max_weight()` compute weight parameters. `ip_vs_wrr_init_svc()`, `ip_vs_wrr_dest_changed()`, and `ip_vs_wrr_done_svc()` manage per-service state. `ip_vs_wrr_schedule()` performs selection. `ip_vs_wrr_scheduler` registers init, done, add, delete, update, and schedule callbacks.

## Control Flow
Service initialization sets the current pointer to the list head and computes GCD, max effective weight, and current weight. Destination changes reset the pointer and recompute parameters under `svc->sched_lock`, adjusting `cw` to remain valid. Scheduling locks the service, scans forward from the current pointer for a destination with weight at least `cw` and not overloaded, then decrements `cw` by `di` and wraps as needed. It performs a final pass at weight threshold one to catch destinations whose weights changed below the old GCD.

## State and Persistence
Per-service state is the WRR mark stored in `svc->sched_data` and freed with RCU on unbind. It persists across scheduling calls to maintain position and current weight phase. Destination weights remain externally configured state.

## Dependencies and Integration Points
Depends on IPVS service locks, destination list traversal, GCD helper, RCU cleanup, scheduler registry, and atomic weights. Destination add/delete/update callbacks keep scheduler state aligned with the service pool.

## Risks
The algorithm is sensitive to concurrent weight changes, which the code partly mitigates with an effective max weight and final threshold-one pass. Pointer state can reference list head or destinations, so deletion and reassignment paths must reset it correctly. Overloaded destinations can cause the scan to wrap and eventually fail even if weights are positive.

## Test Signals
Validate weighted distribution ratios, GCD and max-weight recalculation after destination updates, zero and all-zero weights, overloaded destinations, deletion of current destination, dynamic weight reduction below GCD, and no-destination error messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_wrr.c -->
