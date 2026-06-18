# subset-b-006155 research

Grouped research for the batman-adv files listed in work item `subset-b-006155`. Each section title preserves the source path and is wrapped with the exact split markers required by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bridge_loop_avoidance.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/bridge_loop_avoidance.c research

Purpose: implements batman-adv bridge loop avoidance (BLA) when `CONFIG_BATMAN_ADV_BLA` is enabled. It tracks backbone gateways per VLAN, claims client MAC/VLAN ownership, filters duplicate broadcasts crossing the same LAN and mesh, emits claim protocol ARP frames, and reports loops that BLA cannot resolve.

Important APIs and functions: public entry points are `batadv_bla_init()`, `batadv_bla_free()`, `batadv_bla_rx()`, `batadv_bla_tx()`, `batadv_bla_is_backbone_gw()`, `batadv_bla_is_backbone_gw_orig()`, `batadv_bla_check_bcast_duplist()`, netlink dump functions, `batadv_bla_status_update()`, `batadv_bla_update_orig_address()`, and DAT-facing `batadv_bla_check_claim()`. Internal hash callbacks `batadv_choose_claim()`, `batadv_choose_backbone_gw()`, and compare helpers key claims by client MAC plus VID and backbone gateways by originator MAC plus VID. Reference release paths use `kref` and `kfree_rcu()`.

Control flow: initialization creates claim and backbone hashtables, initializes duplicate tracking and group identity, and schedules delayed periodic work. TX calls first detect and consume BLA claim ARP frames, then decides whether a local packet may enter the mesh based on claim ownership. RX handles mesh-originated frames, blocks multicast while claim requests are pending, deduplicates multicast-in-unicast traffic, claims unclaimed source MACs, and drops traffic owned by another gateway. Claim processing parses ARP/VLAN headers, validates BLA magic and group membership, updates local backbone state, and dispatches CLAIM, UNCLAIM, ANNOUNCE, REQUEST, or LOOPDETECT frames. Periodic work purges expired claims/backbone gateways, sends announcements, sends loopdetect frames on all local backbone VLANs, and releases startup request suppression after grace periods.

State and persistence: all state is in memory under `bat_priv->bla`. `claim_hash` stores `struct batadv_bla_claim` entries with a `backbone_gw` reference protected by `backbone_lock`. `backbone_hash` stores `struct batadv_bla_backbone_gw` entries with CRC, last-seen jiffies, request counters, and loop report work. Duplicate broadcast state is a bounded ring with CRCs and timestamps. State is not persisted; it is regenerated from observed BLA frames and primary interface updates.

Dependencies and integration: depends on generic batman-adv hash helpers, originator lookup, translation table cleanup, hard-interface primary selection, netlink attributes, ARP/VLAN helpers, `batadv_event_workqueue`, and logging. It integrates with DAT by allowing DAT replies only when BLA says the node owns or may answer for the MAC. It integrates with main uevents by reporting unresolved loops with `BATADV_UEV_BLA/BATADV_UEV_LOOPDETECT`.

Risks: packet ownership is subtle because `batadv_bla_rx()` consumes and frees skb on handled paths while `batadv_bla_tx()` only reports handled. RCU and kref ordering is critical for claim/backbone teardown. CRC based duplicate detection can collide, though bounded by source checks and timeout. VLAN parsing intentionally drops QinQ BLA claim frames. A missing primary interface or disabled BLA changes many paths from filtering to allow. The code depends on correct lock ordering between hash bucket locks, claim `backbone_lock`, and backbone `crc_lock`.

Test signals: exercise enabling/disabling BLA, primary interface MAC changes, VLAN tagged and untagged claims, duplicate broadcast suppression, multicast-in-unicast duplicate paths, request/announce CRC mismatch recovery, netlink dumps for claims/backbones, and loopdetect uevent emission. KASAN/KCSAN/lockdep are useful because most failures are refcount, RCU, or nested lock regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bridge_loop_avoidance.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bridge_loop_avoidance.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/bridge_loop_avoidance.h research

Purpose: declares the BLA public interface and provides no-op stubs when `CONFIG_BATMAN_ADV_BLA` is disabled. It is the integration contract between BLA and routing, DAT, bridge ingress/egress, netlink, and hard-interface lifecycle code.

Important APIs and types: `batadv_bla_is_loopdetect_mac()` recognizes locally administered loopdetect source MACs beginning with `ba:be`. Enabled builds export RX/TX filters, backbone checks, duplicate-list checks, primary address updates, status updates, init/free, netlink dump functions, and DAT-only claim checks. `BATADV_BLA_CRC_INIT` defines the initial CRC value for claim table synchronization. Disabled builds inline safe defaults: filtering functions return false, dump functions return `-EOPNOTSUPP`, init returns success, and `batadv_bla_check_claim()` returns true.

Control flow and state behavior: the header has no storage, but its stubs define global feature behavior. With BLA off at compile time, callers can still invoke the same functions and will generally continue forwarding traffic without BLA filtering or diagnostics. With BLA on, callers must honor boolean return values: RX/TX paths treat true as consumed or handled.

Dependencies and integration: includes `main.h` and kernel network/skbuff/netlink types. DAT is conditionally coupled through `batadv_bla_check_claim()`, letting DAT avoid answering for clients claimed by another backbone gateway. Netlink command handlers depend on the dump prototypes.

Risks: the disabled stub for `batadv_bla_init()` returns `1`, which is non-negative and therefore treated as success by callers checking `< 0`; code that assumes exact zero would be wrong. The boolean contract differs by caller context, so documentation and tests need to verify whether true means "skb consumed" or simply "do not process further".

Test signals: build both with and without `CONFIG_BATMAN_ADV_BLA`; compile DAT combinations; verify non-BLA builds still link all callers; verify bridge traffic is not filtered by BLA stubs; verify netlink dump commands return unsupported when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bridge_loop_avoidance.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/distributed-arp-table.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/distributed-arp-table.c research

Purpose: implements the Distributed ARP Table (DAT), a batman-adv DHT-like cache mapping IPv4 addresses and VLAN IDs to client MAC addresses. It snoops ARP and DHCPACK traffic, answers some ARP requests from cache, forwards DHT GET/PUT messages to selected originators, and suppresses redundant ARP broadcast fallback.

Important APIs and functions: public entry points include `batadv_dat_init()`, `batadv_dat_free()`, `batadv_dat_status_update()`, ARP snoopers for outgoing/incoming requests and replies, DHCPACK snoopers, `batadv_dat_drop_broadcast_packet()`, and `batadv_dat_cache_dump()`. Internal state management uses `batadv_dat_entry_add()`, `batadv_dat_entry_hash_find()`, `__batadv_dat_purge()`, `batadv_hash_dat()`, and candidate selection functions. Packet parsers include ARP field accessors, `batadv_arp_get_type()`, VLAN-aware `batadv_dat_get_vid()`, and DHCP validation helpers.

Control flow: init allocates a 1024-bucket DAT hash, starts a 10-second purge timer, registers DAT TVLV handlers, and advertises capability based on `distributed_arp_table`. Outgoing ARP requests add the sender mapping, answer locally if a valid non-local cache entry exists and BLA allows it, or forward a DAT GET to up to three DHT candidates. Incoming ARP requests add the sender mapping and answer from local cache using TT or 4addr forwarding depending on the encapsulation. ARP replies add both source and destination mappings and propagate PUT messages. DHCPACK snooping extracts server/client address data and inserts it, using a generated ARP reply as the PUT payload. Broadcast fallback suppression drops non-rebroadcast ARP requests when the cache already has the answer.

State and persistence: `bat_priv->dat.hash` contains `struct batadv_dat_entry` records with IP, VID, MAC, last-update jiffies, hash node, RCU lifetime, and kref. Entries expire after `BATADV_DAT_ENTRY_TIMEOUT`. Originator DAT addresses are deterministic hashes of originator MACs; the local DAT address is derived from the primary interface MAC. No state persists across interface or module teardown.

Dependencies and integration: relies on originator tables and DAT capability bits, TVLV registration, hard-interface primary selection indirectly, BLA claim checks, translation table delivery, `send` helpers for unicast 4addr transport, netlink dump attributes, `batadv_event_workqueue`, and statistics counters. It is IPv4 ARP focused; DHCP parsing covers IPv4 server source addresses and DHCPACK fields while packet detection handles Ethernet/VLAN/IP/UDP layout.

Risks: ARP parsing uses offsets into mutable skb data after `pskb_may_pull()`, so header length updates must stay consistent. `batadv_dat_entry_hash_find()` compares only IP after choosing a hash that includes VID; this is safe inside the chosen bucket but easy to break if hashing changes. DHT candidate selection walks the originator hash and must release every selected `orig_node`. Local ARP reply injection can surprise bridge setups, which the code mitigates by avoiding replies for local clients. DHCP options parsing lacks option overload support and must avoid malformed option-length overrun.

Test signals: ARP request/reply flows with and without VLAN tags, local client suppression, BLA claim conflict suppression, DAT disabled mode, candidate selection with fewer than three DAT-capable originators, cache expiry and netlink dumps, DHCPACK learning, malformed ARP/DHCP skbs, and broadcast fallback prevention after cache hits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/distributed-arp-table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/distributed-arp-table.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/distributed-arp-table.h research

Purpose: declares DAT integration points and compile-time stubs. It lets routing, bridge, TT, netlink, and DHCP gateway paths call DAT code without scattering `#ifdef CONFIG_BATMAN_ADV_DAT` throughout the codebase.

Important APIs and types: when enabled it defines `BATADV_DAT_ADDR_MAX`, ARP/DHCP snooping prototypes, `batadv_dat_drop_broadcast_packet()`, init/free, status update, netlink dump, and `batadv_dat_inc_counter()`. Inline helpers `batadv_dat_init_orig_node_addr()` and `batadv_dat_init_own_addr()` derive DAT ring addresses from originator or primary interface MAC addresses using `batadv_choose_orig()`.

Control flow and state behavior: the header itself stores no state. Enabled inline address initialization mutates `orig_node->dat_addr` and `bat_priv->dat.addr`. Disabled stubs return false for snoopers/drop decisions, no-op status and address initialization, return success for init, and `-EOPNOTSUPP` for netlink cache dumps.

Dependencies and integration: includes `main.h`, `originator.h`, netdevice/netlink/skbuff types, and batman packet UAPI types. The header directly exposes DAT counters for received unicast 4addr subtypes and keeps ethtool statistics updates close to packet receive code.

Risks: callers must understand ownership semantics of boolean returns: several enabled functions free or consume skbs on true, while disabled stubs never do. Address initialization depends on a valid primary interface. Counter helper silently ignores non-DAT subtypes.

Test signals: build all DAT on/off combinations, ensure no unresolved references in disabled builds, verify address hashes are assigned after primary interface changes, validate `batadv_dat_inc_counter()` increments GET/PUT RX counters only, and verify netlink DAT cache dump is unsupported when DAT is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/distributed-arp-table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/fragmentation.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/fragmentation.c research

Purpose: implements batman-adv layer-2 fragmentation and reassembly for unicast payloads that exceed next-hop MTU. It fragments outbound skbs, buffers inbound fragments per originator and sequence number, merges complete chains, forwards fragments without merging when the next hop cannot carry the merged payload, and purges stale fragment chains.

Important APIs and functions: public functions are `batadv_frag_purge_orig()`, `batadv_frag_skb_buffer()`, `batadv_frag_skb_fwd()`, and `batadv_frag_send_packet()`. Internal helpers include `batadv_frag_clear_chain()`, `batadv_frag_size_limit()`, `batadv_frag_init_chain()`, `batadv_frag_insert_packet()`, `batadv_frag_merge_packets()`, and `batadv_frag_create()`.

Control flow: outgoing fragmentation computes a max fragment size from the outgoing hard-interface MTU capped by `BATADV_FRAG_MAX_FRAG_SIZE`, refuses packets requiring more than `BATADV_FRAG_MAX_FRAGMENTS`, grabs the primary interface to fill originator address, then splits from the skb tail into numbered `BATADV_UNICAST_FRAG` packets. Incoming buffering linearizes fragments, selects a per-originator bucket by sequence number modulo `BATADV_FRAG_BUFFER_COUNT`, clears any chain with a different sequence number, inserts fragments in descending number order, validates aggregate size and total size consistency, and hands a complete chain to merge. Merge expands the first skb, strips the fragment header, restores the Ethernet header, then appends payloads from remaining fragments.

State and persistence: fragment state lives under each `batadv_orig_node->fragments[]` entry, with a spinlock, hlist, sequence number, timestamp, size, and total size. Stale entries are purged via `batadv_frag_purge_orig()` and `batadv_frag_check_entry()` from the header. State is bounded by buffer count, max fragments, and max total size, and it is purely in memory.

Dependencies and integration: uses `originator` router lookup, `send` helpers, hard-interface primary selection, batman packet UAPI, per-mesh counters, skb allocation/manipulation, jiffies timeouts, and MTU values from the next-hop hard interface. `hard-interface.c` accounts for fragment headers in headroom and MTU calculations.

Risks: skb ownership is strict: failed insert frees the fragment skb, successful buffer sets caller skb to NULL unless merged, and send consumes fragments. Fragment order and `total_size` validation prevent malformed reassembly but duplicate fragment numbers drop the new fragment. GRO frag_list linearization on send can be costly. Forward-without-merge depends on correct next-hop MTU and decrements TTL directly.

Test signals: packets around MTU boundaries, exactly 1 and 16 fragments, over-16 fragment refusal, duplicate and out-of-order fragments, mismatched total sizes, timeout purge, forwarding fragments when merged size exceeds next-hop MTU, skb with frag_list, priority propagation, and stats counters for TX/FWD bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/fragmentation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/fragmentation.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/fragmentation.h research

Purpose: declares the fragmentation subsystem API and provides the inline timeout predicate used by originator cleanup code.

Important APIs and types: `batadv_frag_purge_orig()` purges per-originator fragment buffers using an optional predicate; `batadv_frag_skb_fwd()` may forward a fragment without reassembly; `batadv_frag_skb_buffer()` buffers and possibly merges a received fragment; `batadv_frag_send_packet()` fragments and sends an oversized skb. `batadv_frag_check_entry()` tests whether a non-empty chain has exceeded `BATADV_FRAG_TIMEOUT`.

Control flow and state behavior: the header has no storage. Its inline predicate reads `fragment_list` and `timestamp` from `struct batadv_frag_table_entry`, tying the implementation to per-originator fragment state initialized elsewhere in `types.h` and originator setup.

Dependencies and integration: includes `main.h`, kernel list/skbuff types, and depends on `batadv_has_timed_out()` plus fragmentation constants in `main.h`. It is consumed by receive routing, originator purge, and send paths.

Risks: callers must hold the correct chain lock when using timeout checks in contexts where the list can mutate. The API uses pointer-to-pointer skb ownership for buffering, which is easy to misuse if a caller continues to reference a consumed skb.

Test signals: compile with receive/send users, verify timeout purge invokes `batadv_frag_check_entry()`, check caller behavior for merged, buffered, and failed outcomes, and run lockdep around fragment purge while traffic is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/fragmentation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/gateway_client.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/gateway_client.c research

Purpose: manages gateway client behavior: tracking announced gateways, selecting the best current gateway through routing-algorithm hooks, emitting gateway uevents, parsing DHCP packets for gateway-related forwarding, and detecting DHCP requests sent to an outdated gateway.

Important APIs and functions: public functions include `batadv_gw_get_selected_gw_node()`, `batadv_gw_get_selected_orig()`, `batadv_gw_reselect()`, `batadv_gw_check_client_stop()`, `batadv_gw_election()`, `batadv_gw_check_election()`, `batadv_gw_node_update()`, `batadv_gw_node_delete()`, `batadv_gw_node_free()`, `batadv_gw_dump()`, `batadv_gw_dhcp_recipient_get()`, and `batadv_gw_out_of_range()`. `batadv_gw_node_release()` owns kref teardown.

Control flow: TVLV processing in gateway common calls `batadv_gw_node_update()` to add, update, or remove gateway nodes. `batadv_gw_check_election()` sets a reselect flag when a candidate can beat the current gateway. `batadv_gw_election()` runs in client mode, asks `algo_ops->gw.get_best_gw_node()` for the best gateway, validates router and interface info, emits ADD/DEL/CHANGE uevents, and swaps `bat_priv->gw.curr_gw` under `gw.list_lock`. DHCP parser walks Ethernet, optional VLAN, IPv4/IPv6, UDP, and BOOTP/DHCP fields and returns whether a packet targets a server or client. `batadv_gw_out_of_range()` uses TT and gateway list lookup to decide if a unicast DHCP request targets a gateway with TQ worse than the current gateway by more than `BATADV_GW_THRESHOLD`.

State and persistence: `bat_priv->gw.gateway_list` is an RCU hlist protected for writes by `gw.list_lock`, with `generation` tracking netlink dump consistency. `curr_gw` is an RCU pointer with kref ownership. Each `batadv_gw_node` references an originator and stores announced down/up bandwidth in tenths of Mbit. All state is rebuilt from TVLV announcements and is not persisted.

Dependencies and integration: depends on routing algorithm gateway hooks, originator and neighbor lookups, TT search for DHCP destination, netlink, hard-interface primary selection for dumps, logging, and `batadv_throw_uevent()`. It is coupled to gateway_common TVLV registration and to routing paths that need DHCP-aware gateway handling.

Risks: current gateway replacement must balance references on both old and new nodes. Updates remove nodes when down bandwidth reaches zero and must reselect if the removed node was current. DHCP parsing modifies `header_len` as it advances, so callers must pass initialized offsets and expect skb data may be pulled. `batadv_gw_out_of_range()` subtracts TQ values and compares threshold; type widths and ordering matter.

Test signals: gateway add/update/remove TVLVs, gateway client mode transitions, uevent ADD/DEL/CHANGE generation, routing algorithm hooks missing or returning NULL, netlink dump with inactive primary interface, IPv4/IPv6 DHCP to server/client parsing, VLAN DHCP parsing, and out-of-range detection under controlled TQ differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/gateway_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/gateway_client.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/gateway_client.h research

Purpose: declares gateway client APIs for gateway election, gateway node lifecycle, DHCP parsing, netlink dumping, and out-of-range checks.

Important APIs and types: prototypes cover client stop/reselect/election, selected originator and gateway retrieval, node update/delete/free/release/get, `batadv_gw_dump()`, `batadv_gw_out_of_range()`, and `batadv_gw_dhcp_recipient_get()`. The inline `batadv_gw_node_put()` decrements a gateway node kref using `batadv_gw_node_release()`.

Control flow and state behavior: the header does not store state but defines reference ownership: any returned `batadv_gw_node` or selected originator must be released by the caller. The DHCP parser communicates both classification and, for server-to-client DHCP, the client hardware address.

Dependencies and integration: includes `main.h`, kref, netlink, skbuff, batman packet UAPI. It is used by TVLV code, routing paths, hard-interface teardown, and netlink command handlers.

Risks: mismatched get/put calls leak or prematurely free gateway nodes. Callers must invoke election only when routing algorithm gateway hooks are valid and must not assume DHCP parser leaves `header_len` unchanged.

Test signals: compile all gateway users, reference leak checks around selected gateway get/put, DHCP parser callers with malformed skbs, and gateway node removal while current gateway is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/gateway_client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/gateway_common.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/gateway_common.c research

Purpose: implements gateway TVLV advertisement and reception common to gateway server/client modes. It registers the gateway TVLV handler, publishes local server bandwidth when needed, and translates incoming TVLVs into gateway node updates.

Important APIs and functions: public functions are `batadv_gw_tvlv_container_update()`, `batadv_gw_init()`, and `batadv_gw_free()`. Internal `batadv_gw_tvlv_ogm_handler_v1()` parses incoming gateway TVLV values or absence notifications.

Control flow: container update reads `bat_priv->gw.mode`. OFF and CLIENT unregister the local gateway TVLV; SERVER reads atomic down/up bandwidth, converts to network order, and registers a `BATADV_TVLV_GW` version 1 container. The OGM handler treats CIFNOTFND or too-short values as zero bandwidth, sanitizes zero down/up values as removal, calls `batadv_gw_node_update()`, and requests election in client mode when a nonzero gateway is seen. Init initializes selection class through `algo_ops->gw.init_sel_class()` when available or defaults to 1, then registers the OGM handler with CIFNOTFND. Free unregisters local container and handler.

State and persistence: this file stores no own state, but mutates TVLV containers and gateway node state under `bat_priv->gw`. Gateway advertisements reflect current atomic mode/bandwidth values and are regenerated when settings change.

Dependencies and integration: depends on TVLV registration, gateway client node/election functions, atomic gateway settings, and batman packet gateway TVLV structures. It is called from mesh init/free and from settings code that changes gateway mode or bandwidth.

Risks: malformed or short TVLVs must always remove capability, not retain stale gateway nodes. Zero bandwidth is treated as gateway removal. Client election is only triggered on nonzero announcements, so removal paths rely on `batadv_gw_node_update()` to mark reselection if needed.

Test signals: switch gateway mode off/client/server, bandwidth zero/nonzero, receive valid/short/missing gateway TVLVs, verify TVLV registration/unregistration, and confirm client mode election is triggered on new viable gateway announcements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/gateway_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/gateway_common.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/gateway_common.h research

Purpose: exposes common gateway declarations and user-visible gateway mode names. It is the small shared header between mesh initialization, sysfs/netlink settings code, and gateway client logic.

Important APIs and types: defines `enum batadv_bandwidth_units` with kbit and mbit units, string constants for OFF, CLIENT, and SERVER gateway modes, and prototypes for TVLV container update, gateway init, and gateway free.

Control flow and state behavior: no state is stored here. The mode name constants must remain aligned with user-facing configuration parsing elsewhere. `batadv_gw_init()` and `batadv_gw_free()` are lifecycle hooks called from mesh init/free.

Dependencies and integration: includes `main.h` for `struct batadv_priv`. The declarations connect gateway mode configuration, TVLV advertisement, and gateway client tracking.

Risks: changing string constants can break userspace configuration expectations. Bandwidth unit enum changes must stay aligned with parsers/formatters outside this file.

Test signals: build gateway configuration code, test parsing/display of gateway mode names, and verify init/free lifecycle remains paired during mesh interface creation/destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/gateway_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/hard-interface.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/hard-interface.c research

Purpose: manages physical or lower netdevices used as batman-adv hard interfaces. It tracks valid devices globally, enslaves/unen-slaves them to mesh interfaces, handles netdevice notifier events, selects the primary interface, recalculates MTU/headroom, detects Wi-Fi characteristics, and prevents batman-over-batman configurations.

Important APIs and functions: public functions include `batadv_hardif_release()`, `batadv_hardif_get_by_netdev()`, real-netdev helpers, Wi-Fi predicates, `batadv_hardif_enable_interface()`, `batadv_hardif_disable_interface()`, `batadv_hardif_min_mtu()`, `batadv_update_min_mtu()`, and `batadv_hardif_no_broadcast()`. Static helpers cover parent traversal, interface validity, Wi-Fi flag evaluation, primary selection/address update, activation/deactivation, headroom recalculation, hard-interface add/remove, and notifier dispatch.

Control flow: netdevice REGISTER or POST_TYPE_CHANGE creates a `batadv_hard_iface` for valid Ethernet devices. Enabling links the lower device to a mesh upper, calls routing algorithm enable hooks, installs the ETH_P_BATMAN packet handler, warns about MTU limits, checks duplicate MACs, activates immediately if the lower device is up, recalculates mesh headroom, and calls enabled hooks. NETDEV_UP activates inactive hardifs; DOWN/GOING_DOWN deactivates; UNREGISTER/PRE_TYPE_CHANGE removes from the global list and disables/removes; CHANGEMTU updates mesh MTU; CHANGEADDR updates algorithm MAC state and DAT/BLA primary-derived addresses; CHANGEUPPER reevaluates Wi-Fi flags. Disabling removes packet handler, possibly selects a new primary, calls algorithm disable, purges originator/outstanding packet references, unlinks upper/lower devices, and may stop gateway client mode when only one interface remains.

State and persistence: global `batadv_hardif_list` and `batadv_hardif_generation` track all recognized lower devices. Each hard interface holds netdev references, mesh pointer, state enum, neighbor list, OGM mutex, broadcast count, Wi-Fi flags, hop penalty, packet type registration, and algorithm private state. State is in memory and follows netdevice lifetime via notifier events and RCU/kref teardown.

Dependencies and integration: depends on netdevice notifier APIs, rtnl locking, mesh-interface helpers, BLA and DAT address updates, gateway client stop, originator purge, send queue purge, translation table MTU resizing, algorithm hooks, bat_v initialization, and logging. It is the entry point that installs `batadv_batman_skb_recv()` packet reception for hard interfaces.

Risks: lifecycle ordering is fragile: packet handlers and upper links must be removed before references are released. Primary interface swaps update DAT/BLA identity and can purge BLA state if old primary is missing. Parent recursion must avoid veth mutual-parent loops and batman-over-batman. MTU calculation must avoid underflow when no active interface exists and must account for fragmentation. Notifier callbacks run in kernel networking context and must respect RTNL/RCU rules.

Test signals: add/remove lower interfaces, register/unregister/type-change, up/down transitions, primary failover, duplicate MAC warnings, Wi-Fi direct/indirect flag changes, MTU changes with fragmentation on/off, batman-on-batman rejection, veth pair parent handling, and packet reception after disable to catch stale packet_type references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/hard-interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/hard-interface.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/hard-interface.h research

Purpose: declares hard-interface states, broadcast avoidance return codes, lifecycle APIs, lookup helpers, and primary-interface access.

Important APIs and types: `enum batadv_hard_if_state` models not-in-use, to-be-removed, inactive, active, and to-be-activated. `enum batadv_hard_if_bcast` tells broadcast code whether forwarding is unnecessary because there is no recipient, only the forwarder, only the originator, or whether broadcast is OK. Exports include the notifier block, real netdev lookup, Wi-Fi predicates, hardif lookup, enable/disable, MTU update, kref release, and broadcast avoidance. Inline `batadv_hardif_put()` and `batadv_primary_if_get_selected()` encode reference handling.

Control flow and state behavior: `batadv_primary_if_get_selected()` uses RCU to read `bat_priv->primary_if` and returns a kref-protected hard interface or NULL. Callers must release it with `batadv_hardif_put()`. The header's enums define legal lifecycle transitions used by the implementation and by callers checking activity.

Dependencies and integration: includes `main.h`, kref, netdevice, RCU, and basic kernel types. It is included by most packet, routing, DAT, BLA, and gateway modules because hard-interface ownership is central to all receive/send paths.

Risks: forgetting to put selected or looked-up hard interfaces leaks references. Checking only non-NULL without checking `if_status` can route through inactive devices. Broadcast avoidance enum values are consumed as policy, so adding values requires updating switch-like callers.

Test signals: compile with all users, reference leak testing around primary selection, activity checks for netlink dumps, and broadcast avoidance behavior for zero, one, and multiple neighbors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/hard-interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/hash.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/hash.c research

Purpose: implements allocation, initialization, destruction, and lockdep class assignment for batman-adv's small generic hlist hashtable wrapper.

Important APIs and functions: `batadv_hash_new()` allocates the wrapper, bucket array, and per-bucket spinlock array with `GFP_ATOMIC`; `batadv_hash_destroy()` frees those allocations; `batadv_hash_set_lock_class()` assigns one lockdep class to all bucket locks in a table. Static `batadv_hash_init()` initializes each hlist and spinlock and resets the generation counter.

Control flow: allocation is staged so failures free earlier allocations. New hashes are returned empty with `size` set and `generation` zero. Destruction intentionally frees only the table structure and lock arrays; callers must purge contained entries before destroying. Lock class assignment is used by BLA when claim and backbone tables can be locked in nested contexts.

State and persistence: no global state. Each allocated `struct batadv_hashtable` owns arrays and a generation counter. Contents are managed by callers through inline add/remove helpers in `hash.h`.

Dependencies and integration: used by BLA claim/backbone tables, DAT cache, originator/translation-table style modules, and netlink dump consistency via `generation`. Depends on kernel hlist, spinlock, lockdep, and slab allocation.

Risks: `batadv_hash_destroy()` does not walk buckets, so failing to purge entries leaks caller-owned objects and may leave RCU callbacks unscheduled. `GFP_ATOMIC` allocation can fail under pressure. Size zero is not guarded here and would break choose callbacks via modulo, so callers must request positive sizes.

Test signals: allocation failure injection, destroy after caller purge, nested lockdep paths using `batadv_hash_set_lock_class()`, generation changes through add/remove, and users with large bucket counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/hash.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/hash.h research

Purpose: defines the generic batman-adv hashtable abstraction and inline add/remove operations used by feature modules that need RCU hlist buckets plus per-bucket spinlocks.

Important APIs and types: callback typedefs define key comparison, bucket selection, and optional free callback shape. `struct batadv_hashtable` contains the bucket table, lock array, size, and atomic generation. External functions allocate, destroy, and set lock classes. Inline `batadv_hash_add()` checks for duplicates under the selected bucket lock, inserts with `hlist_add_head_rcu()`, and increments generation. Inline `batadv_hash_remove()` selects a bucket, deletes the first matching node with `hlist_del_rcu()`, increments generation, and returns the removed node pointer.

Control flow and state behavior: callers provide both key data and the hlist node being inserted or removed. Compare callbacks receive existing nodes and key data; choose callbacks must be deterministic and return an index less than `size`. The table does not own object memory; removed nodes must be converted back to containing objects and released by the caller.

Dependencies and integration: includes `main.h`, atomic, hlist/rculist, spinlock, and lockdep. Generation is used by netlink dump code to mark consistency while iterating under bucket locks.

Risks: `batadv_hash_remove()` assumes a non-NULL hash and valid size, unlike `batadv_hash_add()` which checks NULL. Callers must not pass stack data nodes for inserted objects. Duplicate detection depends entirely on compare correctness. RCU deletion requires caller-managed grace-period safe freeing.

Test signals: duplicate insert returns 1, null add returns -1, remove missing returns NULL, generation increments exactly on successful insert/remove, lockdep catches nested table locking, and RCU readers can find/ref objects safely during concurrent delete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/log.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/log.c research

Purpose: provides the debug logging backend for `CONFIG_BATMAN_ADV_DEBUG` builds by emitting formatted messages to the batman-adv tracepoint.

Important APIs and functions: `batadv_debug_log()` takes `bat_priv` and a printf-style format, wraps the variadic arguments in `struct va_format`, calls `trace_batadv_dbg()`, and returns 0.

Control flow and state behavior: there is no buffering or persistent storage in this file. Filtering and rate limiting happen in macros from `log.h` before this function is called. The tracepoint consumer decides where messages are observed.

Dependencies and integration: includes `trace.h` and `log.h`. It is reached by `batadv_dbg()`, `batadv_info()`, and `batadv_err()` when debug logging is enabled and the relevant log level bit is set.

Risks: because it forwards a live `va_list` through `va_format`, tracepoint formatting must happen during the function call. The function always returns success, so callers cannot detect trace backend failures.

Test signals: debug build compilation, dynamic tracepoint enablement, log level filtering via `log.h`, formatted messages with MAC/IP specifiers, and ensuring no calls are emitted when debug is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/log.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/log.h research

Purpose: defines batman-adv debug log levels and logging macros that route messages to the debug trace backend and kernel log.

Important APIs and types: `enum batadv_dbg_level` defines bit flags for BATMAN, ROUTES, TT, BLA, DAT, MCAST, TP_METER, and ALL. Debug builds declare setup/cleanup and `batadv_debug_log()`, and implement `_batadv_dbg()` as a log-level and optional `net_ratelimit()` gate. Non-debug builds provide no-op setup/cleanup and no-op `_batadv_dbg()`. `batadv_dbg()`, `batadv_dbg_ratelimited()`, `batadv_info()`, and `batadv_err()` are the main call sites.

Control flow and state behavior: `_batadv_dbg()` reads `bat_priv->log_level` atomically and calls `batadv_debug_log()` only if the requested type bit is enabled. `batadv_info()` and `batadv_err()` always write to kernel log with mesh interface name and also send the message to debug logging under `BATADV_DBG_ALL`.

Dependencies and integration: includes `main.h`, atomic, bitops, compiler, and printk. Used across packet, gateway, BLA, DAT, hard-interface, and routing modules for diagnostics.

Risks: `batadv_info()` and `batadv_err()` evaluate `netdev_priv(_netdev)` and require a valid mesh netdev. Debug macros compile away in non-debug builds, so side effects inside arguments must be avoided. `BATADV_DBG_ALL` is fixed to 255 and must cover defined bits.

Test signals: debug and non-debug builds, log level sysfs/netlink controls, ratelimited flood behavior, info/error kernel log prefixing, and no side effects from disabled debug statements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/main.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/main.c research

Purpose: is the central module lifecycle and mesh-interface coordinator for batman-adv. It initializes global algorithm, packet receive dispatch, netdevice/netlink integration, creates the shared event workqueue, initializes per-mesh subsystems, and provides common helpers for packet priority, VLAN IDs, counters, receive dispatch, and uevents.

Important APIs and functions: module entry/exit are `batadv_init()` and `batadv_exit()`. Public mesh lifecycle functions are `batadv_mesh_init()` and `batadv_mesh_free()`. Other public helpers include `batadv_is_my_mac()`, `batadv_max_header_len()`, `batadv_skb_set_priority()`, `batadv_batman_skb_recv()`, receive handler register/unregister, `batadv_get_vid()`, `batadv_vlan_ap_isola_get()`, and `batadv_throw_uevent()`.

Control flow: module init creates TT cache, initializes global hardif list and algorithms, installs default receive handlers, initializes protocol variants and TP meter, creates the single-thread `bat_events` workqueue, registers netdevice notifier, RTNL link ops, and generic netlink family. Mesh init initializes many spinlocks/lists, then brings up originator, TT, bat_v, BLA, DAT, gateway, and multicast subsystems; failures unwind in reverse order and mark mesh inactive. Mesh free marks deactivating, purges queued packets, stops TP sessions, frees gateway nodes, v mesh, DAT, BLA, multicast, TT, originator, gateway TVLVs, and per-cpu counters. Receive dispatch validates hard-interface reference, skb shareability, minimum header, Ethernet header, mesh active state, interface active state, and compatibility version before zeroing `skb->cb` and calling `batadv_rx_handler[packet_type]`.

State and persistence: global state includes `batadv_hardif_list`, `batadv_hardif_generation`, `batadv_rx_handler[256]`, and `batadv_event_workqueue`. Per-mesh state in `bat_priv` is initialized from scratch for each mesh netdev and is in-memory only. Uevents are generated from transient state and sent via the mesh netdev kobject.

Dependencies and integration: integrates all major modules: algorithms, bat_iv, bat_v, BLA, DAT, gateway, hard-interface, mesh-interface, multicast, netlink, originator, routing, send, TP meter, and TT. Receive handlers for BCAST, MCAST, unicast variants, ICMP, TVLV, and fragments are registered in the local handler table. Uevent strings serve gateway and BLA userspace notifications.

Risks: init/free ordering is critical because subsystems share originator and TT data. Receive handler registration is global and returns busy if a type is already owned. `batadv_batman_skb_recv()` treats routing-logical drops as `NET_RX_SUCCESS`, so tests need internal counters/logs. `batadv_get_vid()` can pull skb data and returns no-tag for priority-tag VID 0. `batadv_throw_uevent()` allocates with `GFP_ATOMIC` and must free partial environments on all failure paths.

Test signals: module load/unload, mesh creation failure injection at each subsystem, receive of invalid version/short skb/inactive hardif, receive handler registration conflicts, VLAN tag extraction including VID 0, priority mapping from VLAN/IP/IPv6 DSCP, uevent generation for gateway and BLA, and RCU barrier cleanup on module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/main.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/main.h research

Purpose: central batman-adv header defining driver identity, protocol constants, timing values, feature limits, common enums, global declarations, and widely used inline helpers/macros.

Important APIs and types: defines source version, driver metadata, TQ/throughput constants, TTL, purge and TT/DAT/BLA/fragmentation timeouts, aggregation limits, queue lengths, `enum batadv_mesh_state`, `enum batadv_uev_action`, `enum batadv_uev_type`, gateway threshold, fragment limits, DAT candidate markers, and debug `pr_fmt`. It declares global hardif list/generation, event workqueue, mesh lifecycle, receive functions, counter helpers, VLAN/AP isolation and uevent helpers. Inline helpers include `batadv_print_vid()`, `batadv_compare_eth()`, `batadv_has_timed_out()`, sequence-number comparison macros, and per-cpu counter updates.

Control flow and state behavior: constants in this header shape behavior across modules: BLA periodic/timeout windows, DAT entry lifetime, fragment buffer limits, OGM/TT work periods, gateway election threshold, and queue sizes. The sequence macros implement wraparound comparisons using two's-complement assumptions. `BATADV_SKB_CB()` reserves skb control-buffer layout for batman-adv private metadata.

Dependencies and integration: includes many kernel networking headers, batman packet UAPI, `types.h`, and recursively includes `main.h` due to existing code structure. It is included by almost every batman-adv C file. Constants are consumed by BLA, DAT, fragmentation, hard-interface MTU calculations, gateway selection, routing, translation table, multicast, and logging.

Risks: changing constants has broad behavioral impact and can silently alter network convergence, memory pressure, or packet compatibility. `BATADV_MAX_MTU` depends on `batadv_max_header_len()` and must stay consistent with packet structure build checks in `main.c`. Sequence macros rely on operands of same type and intentionally enforce that through pointer comparison. `batadv_add_counter()` uses per-cpu storage and assumes `bat_priv->bat_counters` has been allocated.

Test signals: compile-time structure size checks, builds across 32/64-bit, sequence wraparound unit tests, timeout behavior using jiffies wrap simulation, MTU calculations with fragmentation, per-cpu counter access under traffic, and feature combinations for BLA/DAT/MCAST/debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/main.h -->
