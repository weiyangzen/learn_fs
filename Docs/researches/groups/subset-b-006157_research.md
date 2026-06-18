# Group Research: subset-b-006157

Grouped research for the listed batman-adv routing, send, throughput meter, tracing, and translation-table files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/routing.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/routing.c

## Purpose
Implements the receive-side routing logic for batman-adv packets after a hard interface has accepted a frame. It validates packet shapes, updates originator routes, selects next hops, handles ICMP echo/TTL/throughput-meter traffic, forwards or decapsulates unicast, TVLV, fragment, broadcast, and multicast packets, and coordinates with translation-table, DAT, BLA, fragmentation, and multicast subsystems before handing payloads to the mesh interface.

## Important APIs And Functions
Public entry points are `batadv_update_route`, `batadv_window_protected`, `batadv_check_management_packet`, `batadv_recv_icmp_packet`, `batadv_recv_unicast_packet`, `batadv_recv_unicast_tvlv`, `batadv_recv_unhandled_unicast_packet`, `batadv_recv_frag_packet`, `batadv_recv_bcast_packet`, optional `batadv_recv_mcast_packet`, and `batadv_find_router`. Internal helpers include `_batadv_update_route`, `batadv_recv_my_icmp_packet`, `batadv_recv_icmp_ttl_exceeded`, `batadv_check_unicast_packet`, `batadv_last_bonding_get`, `batadv_last_bonding_replace`, `batadv_route_unicast_packet`, `batadv_reroute_unicast_packet`, and `batadv_check_unicast_ttvn`.

## Control Flow
Route updates replace an originator's per-interface router under `orig_node->neigh_list_lock`, take a reference on the new neighbor, drop the old router after the RCU pointer swap, and delete global TT entries when a route disappears. Router selection starts with `batadv_orig_router_get`; if bonding is enabled for first-hop traffic it rotates among similar-or-better per-interface candidates using `orig_node->last_bonding_candidate`.

ICMP receive validates unicast Ethernet addressing and local destination, appends record-route data when present, locally answers echo requests, dispatches `BATADV_TP` packets to `batadv_tp_meter_recv`, generates TTL exceeded responses for traceroute-style echo requests, or decrements TTL and forwards through `batadv_send_skb_to_orig`. Unicast receive verifies the local outer destination, checks and possibly repairs stale TTVN state through the translation table, drops BLA backbone duplicates, lets DAT snoop ARP/DHCP, and finally either delivers with `batadv_interface_rx` or forwards. Fragment receive may forward oversized fragments, buffer/merge fragments, and re-enter `batadv_batman_skb_recv` for assembled packets. Broadcast receive enforces broadcast outer destination, rejects self-originated traffic, applies duplicate and reset-window checks, queues rebroadcast, filters BLA backbone traffic, then snoops DAT and delivers locally. Multicast receive parses TVLV payload, lets multicast TVLV handlers decide forwarding/local delivery, and accounts multicast counters.

## State And Persistence
State is volatile kernel state: originator router RCU pointers, neighbor/originator refcounts, bonding candidate pointers, broadcast sequence windows, per-originator reset timestamps, packet counters, and skb contents. The file does not persist to disk. It mutates skb headers in place after `skb_cow`/linearization, updates checksums for TTVN rerouting, decrements TTLs, and consumes or frees skbs according to kernel ownership conventions.

## Dependencies And Integration Points
Depends on `originator`, `send`, `translation-table`, `fragmentation`, `distributed-arp-table`, `bridge_loop_avoidance`, `tp_meter`, `tvlv`, `mesh-interface`, `hard-interface`, `bitarray`, and batman-adv algorithm callbacks. It is the receive integration point between lower hard-interface packet demux and upper mesh-interface delivery. It also drives route cleanup in TT on route deletion and uses DAT/BLA decisions to suppress duplicate or bridged traffic.

## Risks
Correctness depends on strict skb ownership: most forwarding helpers consume the skb, while local error exits must free it exactly once. Stale TTVN repair can misroute if TT state is inconsistent or if checksum adjustment is missed after header edits. Bonding candidate rotation touches RCU-protected ifinfo/router objects and is refcount-sensitive. Broadcast duplicate protection depends on sequence arithmetic and reset windows. Several handlers linearize packets and may drop under memory pressure. TTL-exceeded return-code translation appears easy to misread because transmit and receive status constants differ.

## Test Signals
Best signals are kernel build coverage across `CONFIG_BATMAN_ADV_MCAST`, packet-injection tests for malformed headers, self-originated broadcasts, TTL expiry, TTVN mismatch rerouting, roaming clients, DAT/BLA filtering, fragment merge/forward cases, and bonding path selection. Runtime counters (`BATADV_CNT_FORWARD`, broadcast, fragment, multicast counters) plus batman-adv debug logs can validate forwarding decisions in integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/routing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/routing.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/routing.h

## Purpose
Declares the receive-side routing API shared by batman-adv packet dispatchers and related modules. It exposes management-packet validation, route updates, packet receive handlers for major batman-adv packet classes, router lookup, and sequence-window restart protection.

## Important APIs And Types
The header exports `batadv_check_management_packet`, `batadv_update_route`, `batadv_recv_icmp_packet`, `batadv_recv_unicast_packet`, `batadv_recv_frag_packet`, `batadv_recv_bcast_packet`, `batadv_recv_unicast_tvlv`, `batadv_recv_unhandled_unicast_packet`, `batadv_find_router`, and `batadv_window_protected`. `batadv_recv_mcast_packet` is either the real multicast handler when `CONFIG_BATMAN_ADV_MCAST` is enabled or an inline stub that frees the skb and returns `NET_RX_DROP`.

## Control Flow
There is no executable control flow beyond the multicast-disabled inline. The declarations define the ownership contract that receive handlers consume or free skbs and return `NET_RX_*` status. Callers use `batadv_find_router` before send-side forwarding and `batadv_window_protected` when validating sequence-number windows.

## State And Persistence
The header owns no state. Its inline multicast fallback consumes the skb immediately when multicast support is absent.

## Dependencies And Integration Points
Includes `main.h`, `linux/skbuff.h`, and `linux/types.h`, tying the API to core batman-adv private structures and kernel skb handling. It is included by packet dispatch code, send logic needing router lookup, and modules that validate management packets or sequence restart windows.

## Risks
The main risk is API contract drift: receive handlers must preserve skb ownership expectations, and the multicast stub means code paths must not assume multicast packets survive when the feature is disabled. Changes to function signatures ripple broadly through packet dispatch and send-side routing.

## Test Signals
Compilation with and without `CONFIG_BATMAN_ADV_MCAST` is the primary direct signal. Integration tests should verify unsupported multicast packets are dropped cleanly in non-mcast builds and handled by the implementation in mcast builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/routing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/send.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/send.c

## Purpose
Implements the transmit and forwarding queue side of batman-adv. It wraps payloads in batman-adv headers, resolves next hops through originator or translation-table state, sends prepared packets on hard interfaces, fragments oversized unicast traffic, queues delayed broadcast/OGMv1 forwarding packets, retransmits broadcasts, and purges outstanding work during interface or mesh teardown.

## Important APIs And Functions
Transmit APIs include `batadv_send_skb_packet`, `batadv_send_broadcast_skb`, `batadv_send_unicast_skb`, `batadv_send_skb_to_orig`, `batadv_send_skb_prepare_unicast_4addr`, `batadv_send_skb_unicast`, `batadv_send_skb_via_tt_generic`, and `batadv_send_skb_via_gw`. Queue APIs include `batadv_forw_packet_alloc`, `batadv_forw_packet_free`, `batadv_forw_packet_steal`, `batadv_forw_packet_ogmv1_queue`, `batadv_forw_bcast_packet`, `batadv_send_bcast_packet`, `batadv_forw_packet_is_rebroadcast`, and `batadv_purge_outstanding_packets`. Internal queue helpers manage forwarding lists and delayed work.

## Control Flow
Prepared packets go through `batadv_send_skb_packet`, which verifies active/up hard interface state, pushes an Ethernet header, fills source/destination/protocol, sets skb device/protocol metadata, and calls `dev_queue_xmit`. Unicast sending uses `batadv_find_router`; if fragmentation is enabled and the skb exceeds the next-hop MTU, it delegates to `batadv_frag_send_packet`, otherwise it sends to the selected neighbor. Higher-level payload APIs push `BATADV_UNICAST` or `BATADV_UNICAST_4ADDR` headers, set destination originator and TTVN, optionally lower TTVN for roaming clients, and then route to the originator.

Broadcast forwarding clones the skb per outgoing hard interface, suppresses unnecessary rebroadcasts based on neighbor/originator topology, sends immediately when possible, and queues remaining retransmissions on `bat_priv->forw_bcast_list`. Delayed work clones the saved skb, transmits it, decrements `num_bcasts`, requeues while broadcasts remain, or steals and frees the forwarding packet. Purge logic atomically steals matching broadcast and OGMv1 forwarding packets from global lists, cancels delayed work synchronously, and frees claimed packets.

## State And Persistence
State is in-memory only: queued `batadv_forw_packet` objects, delayed-work items, `bcast_queue_left`/`batman_queue_left` capacity counters, per-skb broadcast counters, interface refcounts, and optional BATMAN_V last-unicast timestamps for hardif neighbors. The file follows a consume-on-send pattern: most send helpers consume the skb regardless of success, and queued forwarding packets own their skb until freed.

## Dependencies And Integration Points
Depends on `routing` for next-hop selection, `translation-table` for client lookup and roaming flags, `gateway_client` for gateway forwarding, `fragmentation`, `distributed-arp-table`, `originator`, `hard-interface`, `mesh-interface`, and the batman-adv event workqueue. It is used by receive forwarding, upper-layer mesh-interface transmit paths, TVLV unicast sending, ICMP/TP meter replies, and broadcast flood handling.

## Risks
Skb ownership and clone semantics are the highest risk: callers must not touch skbs after helpers consume or queue them, and cloned broadcast skbs may make original data non-writable. Forwarding packet stealing prevents requeue-after-free races but relies on correct list lock use and `cleanup_list` markers. Queue capacity must be restored exactly once. Broadcast suppression depends on hard-interface neighbor topology and can cause under-flooding if topology state is stale. Purge sleeps through `cancel_delayed_work_sync`, so callers must not hold incompatible locks.

## Test Signals
Useful tests include skb ownership/failure injection around headroom expansion, inactive/down hard-interface sends, unicast fragmentation threshold behavior, TT and gateway lookup failure, broadcast queue saturation, delayed retransmission counts, DAT drop behavior in queued broadcasts, and purge during active delayed work. Counters, debug logs, and lockdep/KASAN are important runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/send.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/send.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/send.h

## Purpose
Declares batman-adv transmit and forwarding-queue helpers. It is the shared contract for modules that need to send prepared packets, encapsulate payloads for unicast/4-address forwarding, queue broadcasts, or purge delayed forwarding packets.

## Important APIs And Types
The header declares forwarding packet lifecycle functions (`batadv_forw_packet_alloc`, `batadv_forw_packet_free`, `batadv_forw_packet_steal`, `batadv_forw_packet_ogmv1_queue`, `batadv_forw_packet_is_rebroadcast`), raw send helpers (`batadv_send_skb_packet`, `batadv_send_broadcast_skb`, `batadv_send_unicast_skb`, `batadv_send_skb_to_orig`), broadcast queue helpers (`batadv_forw_bcast_packet`, `batadv_send_bcast_packet`, `batadv_purge_outstanding_packets`), and unicast encapsulation/lookup helpers (`batadv_send_skb_prepare_unicast_4addr`, `batadv_send_skb_unicast`, `batadv_send_skb_via_tt_generic`, `batadv_send_skb_via_gw`). Inline wrappers `batadv_send_skb_via_tt` and `batadv_send_skb_via_tt_4addr` bind common packet type/subtype values.

## Control Flow
The inline wrappers simply forward to `batadv_send_skb_via_tt_generic` with `BATADV_UNICAST` or `BATADV_UNICAST_4ADDR`. All other behavior is implemented in `send.c`; the header documents lookup-by-TT and encapsulate-then-send semantics.

## State And Persistence
The header owns no state. It exposes APIs that operate on skbs, forwarding packet objects, hard-interface/originator/neighbor refcounted structures, and queue locks.

## Dependencies And Integration Points
Includes `main.h`, kernel skb/spinlock/compiler/types headers, and `uapi/linux/batadv_packet.h` for packet constants. It is consumed by routing, TVLV, ICMP/TP meter, fragmentation, and upper transmit paths.

## Risks
The public API encodes skb ownership implicitly: most send helpers consume skbs. Misunderstanding the inline wrappers can lead to wrong packet subtype or stale destination hints. Signature changes have broad impact because send helpers sit on hot data and control paths.

## Test Signals
Compilation catches signature drift. Packet-level tests should exercise both inline wrappers, especially 4-address subtype propagation and TT lookup with and without `dst_hint`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/send.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/tp_meter.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/tp_meter.c

## Purpose
Implements the batman-adv throughput meter, an ICMP-based active measurement facility driven from netlink/batctl. It creates sender and receiver sessions, sends synthetic payload traffic through normal batman-adv unicast routing, ACKs received byte ranges, estimates RTT/RTO, applies TCP-like slow start/congestion avoidance/NewReno fast recovery, reports completion or errors to userspace, and tears sessions down safely.

## Important APIs And Functions
Public APIs are `batadv_tp_meter_init`, `batadv_tp_start`, `batadv_tp_stop`, `batadv_tp_stop_all`, and `batadv_tp_meter_recv`. Important internals include `batadv_tp_session_cookie`, `batadv_tp_cwnd`, `batadv_tp_update_cwnd`, `batadv_tp_update_rto`, `batadv_tp_batctl_notify`, `batadv_tp_list_find`, `batadv_tp_list_find_session`, `batadv_tp_vars_release`, `batadv_tp_list_detach`, sender cleanup/shutdown/finish/timer functions, `batadv_tp_send_msg`, `batadv_tp_recv_ack`, `batadv_tp_avail`, `batadv_tp_send`, `batadv_tp_start_kthread`, receiver timer/shutdown, `batadv_tp_send_ack`, `batadv_tp_handle_out_of_order`, `batadv_tp_ack_unordered`, `batadv_tp_init_recv`, and `batadv_tp_recv_msg`.

## Control Flow
`batadv_tp_start` generates a session id and ICMP uid, rejects inactive meshes, duplicate destination sessions, and `BATADV_TP_MAX_NUM` overflow, allocates a sender `batadv_tp_vars`, initializes cwnd/RTO/session state, adds it to `bat_priv->tp_list`, schedules finish work, and starts `kbatadv_tp_meter`. The sender thread resolves the destination originator and primary interface, arms the RTO timer, schedules test-length completion, and sends `BATADV_TP_MSG` packets while the congestion window has room. ACK processing updates RTT/RTO, resets timers, tracks duplicate ACKs, performs fast retransmit/recovery, advances `last_acked`, increases cwnd, accounts total acknowledged bytes, and wakes the sender.

Receiver flow starts when a `BATADV_TP_MSG` with `BATADV_TP_FIRST_SEQ` arrives. It creates a receiver session if one does not exist, arms an inactivity timer, tracks `last_recv`, stores out-of-order ranges in a sorted list, advances contiguous received bytes, and sends cumulative ACKs echoing the sender timestamp. `batadv_tp_meter_recv` dispatches TP MSG versus ACK and consumes the skb. Stop paths mark senders not-sending, wake or wait for completion, detach receivers, shutdown timers, and synchronize RCU users.

## State And Persistence
All state is volatile per mesh: `bat_priv->tp_list`, `tp_num`, per-session refcounts, role, other endpoint, session bytes, ICMP uid, `sending`, `last_sent`, `last_acked`, `last_recv`, duplicate ACK count, fast recovery state, cwnd/ss_threshold/RTO/SRTT/RTTVAR, unacked out-of-order list, timers, waitqueue, completion, delayed finish work, and a global prerandom payload buffer. No disk persistence exists; userspace receives session result notifications over netlink.

## Dependencies And Integration Points
Depends on `send` for normal routed transmission, `originator` and `hard-interface` for endpoint resolution, `netlink` for throughput meter notifications, the batman-adv event workqueue, kernel kthreads/timers/completions/waitqueues, and `uapi/linux/batadv_packet.h`/`batman_adv.h` TP constants. Receive integration is via `routing.c` ICMP `BATADV_TP` handling.

## Risks
Session lifetime is complex: list membership, timer references, kthread references, and caller references must be balanced. Sender shutdown uses `atomic_dec_and_test(&sending)`, so double-stop races must not underflow into inconsistent reasons. RTO and sequence arithmetic intentionally exercise wrap-around near `BATADV_TP_FIRST_SEQ`; incorrect comparisons can break measurements. Receiver creation requires the first sequence packet, so loss of the first packet prevents session setup. `BATADV_TP_REASON_CANT_SEND` is treated as non-fatal in the sender loop, which can spin through transient routing failures until timeout. Out-of-order list growth is bounded only by traffic/session behavior and memory allocation success.

## Test Signals
Strong signals include start/stop duplicate and max-session tests, injected kthread/allocation failures, ACK-driven cwnd/RTO transitions, duplicate ACK fast recovery, timeout backoff to unreachable, sequence wrap-around, receiver out-of-order merging, inactivity timeout cleanup, netlink result notifications, and `batadv_tp_stop_all` under live sender/receiver sessions. Lockdep, KASAN, and timer/workqueue race tests are especially relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/tp_meter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/tp_meter.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/tp_meter.h

## Purpose
Declares the public throughput-meter API used by netlink control paths and ICMP receive routing. It keeps session start/stop/all-stop and packet receive handling separated from callers.

## Important APIs And Types
Exports `batadv_tp_meter_init`, `batadv_tp_start`, `batadv_tp_stop`, `batadv_tp_stop_all`, and `batadv_tp_meter_recv`. Callers provide `struct batadv_priv`, destination MAC addresses, test length, session cookie storage, stop reason, or an skb containing a TP ICMP packet.

## Control Flow
There is no executable logic in the header. Implementations create sender sessions, stop one or all sessions, initialize global prerandom data, or consume received TP packets.

## State And Persistence
The header owns no state. It exposes APIs that mutate `bat_priv` throughput-meter session lists and consume skbs in the implementation.

## Dependencies And Integration Points
Includes `main.h`, `linux/skbuff.h`, and `linux/types.h`. It is included by routing for ICMP TP dispatch and by control-plane code that starts/stops measurements.

## Risks
The key contract is that `batadv_tp_meter_recv` consumes the skb and start/stop calls are asynchronous with respect to the sender kthread. Callers must pass stable destination addresses and interpret returned cookies as session identifiers for userspace reporting, not as object references.

## Test Signals
Compilation catches interface drift. Integration tests should verify netlink start/stop calls reach these APIs and that routed TP packets are consumed exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/tp_meter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/trace.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/trace.c

## Purpose
Materializes batman-adv tracepoints by defining `CREATE_TRACE_POINTS` before including `trace.h`. This is the single compilation unit that instantiates the trace event definitions declared in the header.

## Important APIs And Functions
No functions are defined directly. The important side effect is generation of tracepoint symbols for events in `trace.h`, currently `batadv_dbg`.

## Control Flow
There is no runtime control flow in this file. Build-time include ordering causes Linux tracepoint macros to emit definitions rather than declarations.

## State And Persistence
No local state or persistence. Tracepoint state is managed by the kernel tracing subsystem when enabled.

## Dependencies And Integration Points
Depends entirely on `trace.h` and the Linux tracepoint infrastructure. It integrates batman-adv debug logging with ftrace/perf-style tracing.

## Risks
Tracepoint instantiation must happen in exactly one compilation unit. Removing or duplicating this file can cause missing symbols or duplicate definitions. Include path changes in `trace.h` can break trace generation.

## Test Signals
Kernel/module build with tracing enabled is the primary signal. Runtime signal is the presence of batman-adv trace events under tracing facilities and successful event enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/trace.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/trace.h

## Purpose
Defines batman-adv trace events, currently a `batadv_dbg` tracepoint that mirrors formatted batman-adv debug messages into the kernel tracing subsystem. It also provides no-op inline trace functions when batman-adv tracing is disabled.

## Important APIs And Types
Defines `TRACE_SYSTEM batadv` and `TRACE_EVENT(batadv_dbg, TP_PROTO(struct batadv_priv *bat_priv, struct va_format *vaf), ...)`. The event records mesh device name, driver/module name, and the formatted debug message through tracepoint string/vstring fields. It sets `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE trace` before including `<trace/define_trace.h>`.

## Control Flow
With `CONFIG_BATMAN_ADV_TRACING`, Linux trace macros generate event declarations or definitions depending on whether `CREATE_TRACE_POINTS` is set. Without tracing, the header overrides `TRACE_EVENT` to emit static inline dummy `trace_<name>` functions, allowing call sites to compile without runtime tracing.

## State And Persistence
No batman-adv state is persisted. Enabled trace events write formatted records to kernel tracing buffers managed outside this module.

## Dependencies And Integration Points
Includes `main.h`, netdevice, percpu, printk, and tracepoint headers. It is included by logging code and by `trace.c` for tracepoint instantiation. The event reads `bat_priv->mesh_iface->name`, so call sites must provide a valid mesh interface.

## Risks
Formatted trace strings depend on `va_format` lifetime and valid `bat_priv->mesh_iface`. Trace header guard and `TRACE_HEADER_MULTI_READ` handling must follow kernel tracing rules. The disabled-tracing macro override must stay compatible with trace macro call syntax.

## Test Signals
Builds with tracing enabled and disabled are required. Runtime tests can enable the `batadv:batadv_dbg` event, trigger batman-adv debug logs, and verify device/driver/message fields appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/translation-table.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/translation-table.c

## Purpose
Implements the batman-adv translation table, which maps non-mesh client MAC/VLAN pairs to local presence or remote originators. It tracks local clients and changes, maintains global client-to-originator state learned from OGMs and TVLV responses, computes CRCs for consistency, handles roaming advertisements, answers and issues TT requests, exposes local/global TT state over netlink dumps, and manages periodic purging plus slab caches.

## Important APIs And Functions
Public APIs include `batadv_tt_init`, `batadv_tt_free`, `batadv_tt_local_add`, `batadv_tt_local_remove`, `batadv_tt_local_dump`, `batadv_tt_global_dump`, `batadv_tt_global_hash_find`, `batadv_tt_global_entry_release`, `batadv_tt_global_hash_count`, `batadv_tt_global_del_orig`, `batadv_transtable_search`, `batadv_is_my_client`, `batadv_is_ap_isolated`, `batadv_tt_local_commit_changes`, `batadv_tt_global_client_is_roaming`, `batadv_tt_local_client_is_roaming`, `batadv_tt_local_resize_to_mtu`, `batadv_tt_add_temporary_global_entry`, `batadv_tt_global_is_isolated`, `batadv_tt_cache_init`, and `batadv_tt_cache_destroy`.

Major internal groups are hash/refcount helpers, local event/change tracking, TVLV local/global data preparation, netlink dump helpers, global originator-subentry management, purge/free paths, AP-isolation lookup, CRC generation and validation, TT request/response generation, OGM and unicast TVLV handlers, roaming advertisement throttling, and local commit logic.

## Control Flow
Local learning uses `batadv_tt_local_add`: it resolves ingress device/hardif, refreshes existing entries, clears pending/roam states when a client reappears, enforces packet-size limits for full TT responses, allocates a local entry, links VLAN state, marks NEW/NOPURGE/WIFI/ISOLA flags, inserts into the local hash, records an ADD event, and sends roaming advertisements to previous global originators when the client moved. Local removal marks older committed clients as PENDING with a DEL event, or immediately removes NEW entries. Commit clears NEW flags, purges pending clients, recomputes local CRCs, increments local TTVN once per interval, updates the TT TVLV container, and saves the last changeset for future diff responses.

Global learning adds or updates global entries with per-originator subentries, sync flags, VLAN counts, temporary-client handling, local conflict removal, and roaming state transitions. `batadv_transtable_search` optionally checks AP isolation, finds the global entry for a destination, and chooses the best originator by comparing routers through the active algorithm. OGM TVLV handling applies single-step diffs when TTVN and CRCs line up; otherwise it sends TT requests for diffs or full tables. Unicast TVLV handling answers requests locally or for other originators when cached data and CRCs are sufficient, forwards unresolved requests/responses, and processes responses by replacing or diff-updating global tables. Roaming TVLV handling adds a ROAM global entry for the advertised client.

Periodic work purges timed-out local entries into pending state, removes timed-out roaming or temporary globals, expires outstanding TT requests, and clears roaming-rate records. Free paths unregister TVLV handlers/containers, cancel delayed work, destroy local/global hashes, free request/change/roam lists, and release the last changeset.

## State And Persistence
All state is in-memory kernel mesh state. Local state lives in `bat_priv->tt.local_hash`, per-VLAN local counts/CRCs, `tt.vn`, `changes_list`, `local_changes`, `last_changeset`, and commit/changeset locks. Global state lives in `tt.global_hash`, `batadv_tt_global_entry` records, per-entry originator lists, per-originator VLAN counts/CRCs, `orig_node->last_ttvn`, and cached `orig_node->tt_buff`. Request throttling uses `tt.req_list`; roaming throttling uses `tt.roam_list`. Object allocation uses module-wide kmem caches initialized at module init. No disk persistence exists.

## Dependencies And Integration Points
Depends on `hash`, `originator`, `tvlv`, `netlink`, `bridge_loop_avoidance`, `hard-interface`, `mesh-interface`, CRC32C, jhash, RCU, krefs, spinlocks, delayed work, and UAPI packet/netlink attributes. It integrates with routing for TTVN rerouting and client lookup, send paths for TT-based unicast selection, BLA for backbone filtering, VLAN/AP isolation policy, netlink dumps for userspace inspection, and OGM/TVLV propagation for distributed synchronization.

## Risks
This file is highly concurrency-sensitive: hash buckets use locks, lookups use RCU and krefs, global entries contain separately locked originator lists, and commit/request/roam paths have their own locks. TTVN wrap-around means CRC validation is essential; missing or oversized diffs force requests, but TT fragmentation is not implemented and responses may intentionally truncate to packet-size limits. Local/global conflict and roaming handling can create transient stale entries used for rerouting consistency. Packet-size limits can reject new local clients or force purges. Netlink dumps must maintain cursor state across partial messages. Global cache teardown must unregister TVLV handlers before freeing tables to avoid use-after-free.

## Test Signals
Important signals include local add/remove/commit cycles with NEW/PENDING/ROAM flags, VLAN count and CRC updates, full-table size limit handling, resize-to-MTU forced purges, global add/delete with multiple originators, best-originator selection, AP isolation decisions, temporary client timeout, roaming advertisement rate limiting, TT request throttling and timeout, OGM diff versus full-table request decisions, response handling for full and diff tables, netlink dump continuation, and init/free error unwind. Lockdep, KASAN, RCU stall detection, and packet-level multi-node mesh tests are especially valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/translation-table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/translation-table.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/translation-table.h

## Purpose
Declares the translation-table API used across batman-adv for client learning, lookup, netlink dumps, route cleanup, AP isolation, roaming checks, MTU resizing, temporary entries, and module cache lifecycle.

## Important APIs And Types
Exports initialization/free functions (`batadv_tt_init`, `batadv_tt_free`, `batadv_tt_cache_init`, `batadv_tt_cache_destroy`), local table operations (`batadv_tt_local_add`, `batadv_tt_local_remove`, `batadv_tt_local_dump`, `batadv_tt_local_commit_changes`, `batadv_tt_local_resize_to_mtu`), global table operations (`batadv_tt_global_dump`, `batadv_tt_global_del_orig`, `batadv_tt_global_hash_find`, `batadv_tt_global_hash_count`, `batadv_tt_add_temporary_global_entry`, `batadv_tt_global_is_isolated`), lookup/policy helpers (`batadv_transtable_search`, `batadv_is_my_client`, `batadv_is_ap_isolated`, roaming checks), and the inline `batadv_tt_global_entry_put` kref release wrapper.

## Control Flow
The only executable code is `batadv_tt_global_entry_put`, which is null-safe and releases the embedded common kref through `batadv_tt_global_entry_release`. The rest of the header defines cross-module contracts for the implementation in `translation-table.c`.

## State And Persistence
The header owns no state. It exposes refcounted `batadv_tt_global_entry` pointers and functions that mutate `bat_priv->tt` in-memory state.

## Dependencies And Integration Points
Includes `main.h`, kref, netdevice, netlink, skb, and types headers. It is included by routing, send, mesh-interface, netlink, originator cleanup, and other modules that need client-to-originator mapping or TT policy decisions.

## Risks
Callers receiving `batadv_tt_global_entry *` from lookup APIs must eventually use `batadv_tt_global_entry_put`; leaking or double-putting these refcounted objects can corrupt global TT state. API users also need to respect VLAN-aware lookups and distinguish local, global, roaming, temporary, and isolated clients.

## Test Signals
Compilation catches declaration drift. Runtime/API tests should pair every global lookup with a put, exercise VLAN-specific lookups, and verify route deletion calls remove matching originator TT entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/translation-table.h -->
