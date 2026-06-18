# subset-b-006209 research

Grouped source research for IPv4 UDP, UDP tunnel/offload, IPv4 XFRM, and IPv6 build configuration files. Each section is delimited for reconciliation into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/udp.c -->
# sources/distributed-fs/ceph-client/net/ipv4/udp.c

## Purpose
This file is the main IPv4 UDP transport implementation. It owns UDP bind-port allocation, socket hash tables, unicast/multicast lookup, sendmsg/recvmsg, corking, checksum setup, receive queue memory accounting, tunnel encapsulation dispatch, proc/BPF iteration, per-net hash-table initialization, and the exported `udp_prot` protocol operations used by AF_INET datagram sockets.

## Important APIs, Types, and Functions
Key state is carried by `struct udp_table`, `struct udp_hslot`, `struct udp_sock`, `struct inet_sock`, `struct sk_buff`, `struct flowi4`, and per-net `net->ipv4.udp_table`. Important entry points include `udp_lib_get_port()`, `__udp4_lib_lookup()`, `udp_err()`, `udp_sendmsg()`, `udp_recvmsg()`, `udp_rcv()`, `udp_lib_unhash()`, `udp_lib_rehash()`, `udp_lib_setsockopt()`, `udp_lib_getsockopt()`, `udp_poll()`, `udp_abort()`, `udp_init()`, and proc iterator helpers.

## Control Flow
Bind flow chooses a random ephemeral port or validates a requested port under UDP hash locks, checks reuse/reuseport/device/source-address compatibility, then inserts the socket into primary and secondary hash chains. Lookup first tries exact four-tuple state, then secondary port-address chains, optional BPF socket lookup, wildcard sockets, and finally the primary hash to cover rehash races. Send flow resolves destination from `sendmsg()` or connected state, processes UDP/IP control messages and cgroup BPF, routes through IPv4, builds a UDP skb via `ip_make_skb()` or corked `ip_append_data()`, sets checksum/GSO state, and calls `ip_send_skb()`. Receive flow validates header length and checksum state, tries early-steal demux, dispatches multicast/broadcast fanout or unicast delivery, applies XFRM policy, encapsulation hooks, socket filter, pktinfo preparation, and queueing. `recvmsg()` drains the per-socket reader queue, validates or copies checksum, emits cmsgs, runs UDP4 recvmsg BPF address rewrite, and consumes/free skbs.

## State and Persistence Behavior
Persistent UDP state is the per-net/global hash table, per-socket port/address/four-tuple hash membership, reuseport group membership, cork state in `udp_sock`, cached RX dst, receive queues, per-NUMA producer queues, memory counters, tunnel callbacks, GRO state, and sysctl memory thresholds. Queue memory is explicitly moved between `sk_receive_queue` and `reader_queue`; forward allocation is reclaimed by UDP-specific destructors. Per-net init may allocate a private UDP hash table or fall back to the global one.

## Dependencies and Integration Points
The file integrates with IPv4 routing, IP options, ICMP errors, XFRM policy, netfilter-independent packet delivery, cgroup BPF hooks, socket filters, reuseport, RPS/NAPI busy poll, UDP tunnel callbacks, GRO/GSO helpers, procfs, BPF iterators, pernet operations, sysctls, and SNMP MIB accounting.

## Risks
The riskiest areas are lock ordering across primary/secondary/four-tuple hashes, reuseport detachment during rehash/unhash, receive memory accounting split across producer and reader queues, checksum validation during peek/truncate/error paths, tunnel encap return-code semantics, and correctness under connected-socket address changes. GSO rejects checksum-disabled and XFRM-transformed paths; changing these checks can create invalid wire packets.

## Test Signals
Useful signals include bind collision/reuseport tests, ephemeral port distribution, connected and wildcard lookup under address rehash, sendmsg with cork/GSO/IP options/BPF, ICMP PMTU and hard-error reporting, UDP GRO and tunnel encap receive, multicast fanout with device/source filters, checksum-drop accounting, proc/BPF socket iteration, per-net hash allocation fallback, and close/abort races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/udp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/udp_bpf.c -->
# sources/distributed-fs/ceph-client/net/ipv4/udp_bpf.c

## Purpose
This file adapts UDP sockets for sockmap/sk_msg BPF redirection. It swaps a UDP socket's protocol table to a BPF-aware clone that can receive bytes from a `sk_psock` ingress queue before falling back to normal UDP receive behavior.

## Important APIs, Types, and Functions
Important functions are `udp_bpf_recvmsg()`, `udp_bpf_update_proto()`, `udp_bpf_rebuild_protos()`, `udp_bpf_ioctl()`, `udp_msg_wait_data()`, and `sk_udp_recvmsg()`. It depends on `struct sk_psock`, `sk_msg_recvmsg()`, `sk_psock_get/put()`, `sock_replace_proto()`, `sock_map_close()`, `udp_prot`, and the saved IPv6 UDP proto pointer.

## Control Flow
When BPF attaches a psock, `udp_bpf_update_proto()` replaces the socket proto with a cloned proto whose close, recvmsg, readability, and ioctl methods are BPF-aware. `udp_bpf_recvmsg()` rejects error queue handling to normal inet errors, returns zero for zero-length reads, obtains the psock, drains `psock` ingress data first, waits on the socket waitqueue if only BPF data may arrive, and falls back to the original UDP receive path when the psock queue is empty. Restore puts the saved proto and write-space callback back.

## State and Persistence Behavior
The cloned protocol tables are static. IPv4 is built at late init from `udp_prot`; IPv6 is rebuilt lazily under `udpv6_prot_lock` if the saved IPv6 proto changes. Per-socket persistent state is the current proto pointer and saved psock callbacks, not packet data. Data remains in UDP receive queues or psock ingress queues.

## Dependencies and Integration Points
This integrates UDP with sockmap, sk_msg, psock lifecycle, socket waitqueues, UDP ioctl semantics, and IPv6 UDP when enabled. `udp_prot.psock_update_sk_prot` calls into this file from the base UDP proto.

## Risks
Risks include proto restoration races, stale IPv6 proto clones, incorrect `SIOCINQ` semantics when data is split between UDP queues and psock queues, and blocking receive behavior when UDP and psock queues change concurrently.

## Test Signals
Test sockmap attach/detach on IPv4 and IPv6 UDP, recvmsg priority between psock and UDP queues, blocking and nonblocking reads, zero-length reads, `MSG_ERRQUEUE`, `SIOCINQ`, socket close, and IPv6 proto rebuild after module init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/udp_bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/udp_diag.c -->
# sources/distributed-fs/ceph-client/net/ipv4/udp_diag.c

## Purpose
This module exposes UDP sockets through the inet sock_diag netlink interface. It supports dumping all matching UDP sockets, looking up a single socket, reporting queue sizes, and optionally destroying sockets when `CONFIG_INET_DIAG_DESTROY` is enabled.

## Important APIs, Types, and Functions
Key functions are `udp_diag_dump()`, `udp_diag_dump_one()`, `sk_diag_dump()`, `udp_diag_get_info()`, and `udp_diag_destroy()`. The file registers `udp_diag_handler`, uses `struct inet_diag_req_v2`, `inet_sk_diag_fill()`, `inet_diag_bc_sk()`, `sock_diag_check_cookie()`, `sock_diag_destroy()`, `__udp4_lib_lookup()`, and optionally `__udp6_lib_lookup()`.

## Control Flow
Dump requests iterate the UDP primary hash table from callback cursor state, hold each bucket lock, filter by namespace, family, state, source port, and destination port, then emit inet_diag netlink records. Single-socket lookup runs under RCU, takes a socket reference if still live, validates the diagnostic cookie, allocates a reply skb, fills it, and unicasts it to the requester. Destroy performs a similar lookup and cookie check, then aborts the socket with `ECONNABORTED`.

## State and Persistence Behavior
The module persists only its registered inet_diag handler. Cursor progress is stored in `cb->args`, while sockets remain owned by the UDP tables. It does not mutate UDP state except through the optional destroy path.

## Dependencies and Integration Points
It depends on inet_diag netlink, UDP hash-table locking, socket refcounts, net namespace ownership, CAP_NET_ADMIN checks for privileged diagnostic fields, and IPv6 lookup helpers when enabled.

## Risks
Lookup argument ordering differs between historical dump-one and destroy paths; mistakes can miss sockets or destroy the wrong one. Iteration must not hold bucket locks while netlink output overflows indefinitely. Cookie checks and refcount acquisition are the main protection against stale or reused socket pointers.

## Test Signals
Exercise `ss`/sock_diag dumps with filters, dump-one for IPv4 and IPv6, v4-mapped IPv6 destroy, cookie mismatch, netns isolation, queue-size reporting, CAP_NET_ADMIN attribute differences, and concurrent socket close during dump/destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/udp_diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/udp_offload.c -->
# sources/distributed-fs/ceph-client/net/ipv4/udp_offload.c

## Purpose
This file implements IPv4 UDP GSO, UFO compatibility, GRO, UDP tunnel segmentation, and UDP tunnel GRO dispatch. It is the offload bridge between the generic skb segmentation/GRO core, UDP sockets, and tunnel protocols such as VXLAN, GENEVE, FoU/GUE, and ESP-in-UDP.

## Important APIs, Types, and Functions
Important APIs include `skb_udp_tunnel_segment()`, `__udp_gso_segment()`, `udp4_ufo_fragment()`, `udp_gro_receive()`, `udp4_gro_receive()`, `udp_gro_complete()`, `udp4_gro_complete()`, `udp_tunnel_update_gro_lookup()`, `udp_tunnel_update_gro_rcv()`, and `udpv4_offload_init()`. State includes `udp_tunnel_gro_types`, static calls, per-net `udp_tunnel_gro`, `NAPI_GRO_CB`, `skb_shinfo()->gso_type`, and UDP socket `gro_receive/gro_complete` callbacks.

## Control Flow
Tunnel GSO temporarily strips the outer UDP/tunnel header, selects an inner segmenter by encapsulation type, segments the inner packet, then rebuilds the outer headers and checksum state on every segment. Plain UDP L4 GSO validates MSS and checksum-start geometry, optionally handles fraglist packets, segments with `skb_segment()`, fixes UDP length/checksum per segment, and preserves socket write accounting. GRO validates UDP checksum, detects tunnel sockets when encap is enabled, either aggregates plain UDP segments or calls a tunnel GRO callback, and completes aggregated packets as UDP L4 GSO or tunnel GSO.

## State and Persistence Behavior
Persistent state is small but global: tunnel GRO callback types and counts, a static call enabled only when exactly one tunnel GRO type exists, and per-net single-socket tunnel lookup hints. Per-packet state is encoded in skb headers, checksum mode, encapsulation flags, GRO control block fields, and GSO metadata.

## Dependencies and Integration Points
The code integrates with `inet_add_offload()`, generic GSO/GRO, net device checksum/offload features, UDP tunnel sockets, XFRM GRO callbacks, IPv6 offload tables for shared helpers, static branches/calls, and NAPI GRO recursion protection.

## Risks
Header offset restoration, checksum adjustment, fraglist geometry, and destructor/write-memory accounting are high-risk. Tunnel GRO callback registration must avoid dangling function pointers and must disable the static call when multiple tunnel types exist. GRO of packets that might actually be tunnels can corrupt inner streams if socket detection is wrong.

## Test Signals
Test UDP_SEGMENT transmit, fraglist GRO/GSO, software fallback when hardware lacks checksum/GSO, UDP tunnels with and without outer checksums, remcsum, IPsec/XFRM interaction, multiple tunnel GRO types, single-socket tunnel lookup updates, malformed UDP lengths, zero checksums, and device feature combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/udp_offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/udp_tunnel_core.c -->
# sources/distributed-fs/ceph-client/net/ipv4/udp_tunnel_core.c

## Purpose
This file provides common IPv4 UDP tunnel helpers for kernel tunnel drivers. It creates/binds/connects kernel UDP sockets, installs encapsulation callbacks, notifies NICs about tunnel ports, transmits UDP-encapsulated packets, releases tunnel sockets, builds tunnel receive metadata, and performs IPv4 route lookup for tunnel egress.

## Important APIs, Types, and Functions
Key exports are `udp_sock_create4()`, `setup_udp_tunnel_sock()`, `udp_tunnel_push_rx_port()`, `udp_tunnel_drop_rx_port()`, `udp_tunnel_notify_add_rx_port()`, `udp_tunnel_notify_del_rx_port()`, `udp_tunnel_xmit_skb()`, `udp_tunnel_sock_release()`, `udp_tun_rx_dst()`, and `udp_tunnel_dst_lookup()`. It uses `struct udp_port_cfg`, `struct udp_tunnel_sock_cfg`, `struct udp_tunnel_info`, `struct ip_tunnel_key`, `struct metadata_dst`, and `struct dst_cache`.

## Control Flow
Socket creation allocates a kernel AF_INET datagram socket, optionally binds to an interface, binds local address/port, optionally connects a peer, and sets transmit checksum policy. Setup clears multicast loopback, enables checksum conversion, stores user data and encap/GRO callbacks in `udp_sock`, enables UDP tunnel encap, registers GRO receive type, and adds the socket to fast GRO lookup if it is a wildcard kernel listener. Transmit prepends a UDP header, sets checksum via `udp_set_csum()`, clears IP options, and delegates to `iptunnel_xmit()`.

## State and Persistence Behavior
Persistent state lives on the kernel socket: user data, encap receive/error/destroy callbacks, GRO callbacks, encap type, checksum conversion, and global tunnel encap/GRO references. Route cache entries may persist in `dst_cache`. Release clears user data under RCU before shutdown and `sock_release()`.

## Dependencies and Integration Points
This file integrates tunnel drivers with UDP core, UDP tunnel NIC offload, IPv4 routing, dst metadata, ip tunnel transmit, checksum helpers, RCU socket user data, RTNL-protected netdevice iteration, and optional destination cache.

## Risks
Incorrect callback installation or release ordering can leave stale tunnel state reachable by receive paths. Wildcard GRO lookup is only valid for unconnected/unbound-device kernel sockets. Route lookup must reject circular routes back to the tunnel device. Checksum policy mismatches can break tunnel interoperability.

## Test Signals
Test tunnel socket create error unwinding, bind-ifindex, connected and unconnected sockets, setup/release under RCU readers, NIC add/drop notifications, `udp_tunnel_xmit_skb()` checksums, metadata source/destination ports, dst cache hits, no-route and circular-route errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/udp_tunnel_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/udp_tunnel_nic.c -->
# sources/distributed-fs/ceph-client/net/ipv4/udp_tunnel_nic.c

## Purpose
This file manages NIC hardware offload tables for UDP tunnel destination ports. It tracks tunnel port reference counts, queues add/delete operations, synchronizes them to drivers, supports shared hardware tables, handles replay after overflow, exposes dump helpers for ethtool netlink, and reacts to netdevice lifecycle events.

## Important APIs, Types, and Functions
Important types are `struct udp_tunnel_nic`, `struct udp_tunnel_nic_table_entry`, `struct udp_tunnel_nic_info`, `struct udp_tunnel_nic_table_info`, and `struct udp_tunnel_info`. Key functions include `__udp_tunnel_nic_add_port()`, `__udp_tunnel_nic_del_port()`, `udp_tunnel_nic_device_sync_work()`, `udp_tunnel_nic_register()`, `udp_tunnel_nic_unregister()`, `udp_tunnel_nic_flush()`, `udp_tunnel_nic_replay()`, dump helpers, and the exported ops table assigned to `udp_tunnel_nic_ops`.

## Control Flow
On netdevice register, the module validates driver capabilities, allocates per-table entries or joins shared state, stores `dev->udp_tunnel_nic`, and asks tunnel drivers to replay existing ports unless offloads are open-only. Add-port checks device state, static VXLAN special cases, tunnel type/family capability, and port/type collisions; it adjusts an existing entry or allocates a free one, marks add/delete flags, and schedules ordered work. Work runs under RTNL and the device mutex, calls driver `set_port`/`unset_port` or `sync_table`, records failures, and may request replay when missed tables get space. Unregister flushes hardware state and defers freeing while work is pending.

## State and Persistence Behavior
Persistent state is attached to each netdevice in `dev->udp_tunnel_nic` or shared through `udp_tunnel_nic_shared`. Entries store port, tunnel type, flags, use count, and driver-private hardware value. `missed`, `need_sync`, `need_replay`, and `work_pending` encode deferred reconciliation with hardware.

## Dependencies and Integration Points
The file depends on netdevice notifiers, RTNL, an ordered workqueue, ethtool tunnel dump attributes, tunnel driver replay callbacks, driver-provided UDP tunnel NIC info, and the global `udp_tunnel_nic_ops` pointer from the stub.

## Risks
Risks include shared-table lifetime, unregister while async work still references device state, failed hardware operations leaving dodgy entries, port collisions between tunnel types, replay deadlocks if called from notification context, and use-count overflow or underflow. Open-only devices require correct NETDEV_UP/GOING_DOWN flushing.

## Test Signals
Test register validation, add/delete reference counting, sync-by-port and sync-by-table drivers, hardware failure retry, missed-table replay, shared tables across devices, static IANA VXLAN handling, ethtool dump output, NETDEV_UP/GOING_DOWN behavior, and unregister with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/udp_tunnel_nic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/udp_tunnel_stub.c -->
# sources/distributed-fs/ceph-client/net/ipv4/udp_tunnel_stub.c

## Purpose
This tiny file defines and exports the global `udp_tunnel_nic_ops` indirection used by UDP tunnel code and NIC offload management.

## Important APIs, Types, and Functions
The only symbol is `const struct udp_tunnel_nic_ops *udp_tunnel_nic_ops`, exported GPL. The concrete ops table is installed by `udp_tunnel_nic.c` at late init and cleared at module exit.

## Control Flow
There is no runtime control flow beyond external modules reading or assigning the pointer under their own synchronization, normally RTNL in the NIC manager.

## State and Persistence Behavior
The pointer is process-global kernel state. NULL means no UDP tunnel NIC offload manager is registered; non-NULL points to the active ops.

## Dependencies and Integration Points
It depends on `net/udp_tunnel.h` for the ops type and allows tunnel core code to compile independently from the NIC manager implementation.

## Risks
Consumers must tolerate NULL and must synchronize against updates. Misordered module exit could expose stale ops if users do not follow the RTNL/registration contract.

## Test Signals
Build with UDP tunnel NIC support as built-in and modular, verify ops are NULL before init and cleared on exit, and confirm tunnel drivers handle absent ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/udp_tunnel_stub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/xfrm4_input.c -->
# sources/distributed-fs/ceph-client/net/ipv4/xfrm4_input.c

## Purpose
This file contains IPv4-specific XFRM/IPsec input finishing and ESP-in-UDP decapsulation support. It restores IPv4 transport headers after transform processing, reinjects packets through prerouting or GRO paths, and handles NAT-T keepalive/IKE/ESP distinction for UDP encapsulated ESP.

## Important APIs, Types, and Functions
Key functions are `xfrm4_transport_finish()`, `xfrm4_udp_encap_rcv()`, `xfrm4_gro_udp_encap_rcv()`, and `xfrm4_rcv()`. Internals include `xfrm4_rcv_encap_finish()`, `__xfrm4_udp_encap_rcv()`, `xfrm_trans_queue()`, `xfrm4_rcv_encap()`, `xfrm4_rcv_spi()`, and callbacks from UDP encap sockets.

## Control Flow
For transformed transport packets, `xfrm4_transport_finish()` restores the original protocol, updates total length/checksum, and either returns a protocol resubmit value, rebuilds MAC headers for GRO offload, or passes through IPv4 prerouting before `dst_input()`. UDP encap receive checks socket encap type, pulls enough bytes to inspect NAT-T payload, drops one-byte keepalives, passes IKE/non-ESP marker packets back to UDP, strips UDP/non-ESP marker bytes for ESP, and invokes XFRM input.

## State and Persistence Behavior
The file mostly mutates transient skb state: IP protocol, total length, transport offset, MAC/network headers, XFRM skb control blocks, and GRO control fields. Persistent socket state is read from `udp_sock->encap_type`.

## Dependencies and Integration Points
It integrates UDP encap sockets, XFRM core input, IPv4 routing, netfilter prerouting, ESP net offload GRO callbacks, skb offload metadata, and ICMP/error behavior from surrounding XFRM protocol code.

## Risks
Offset and length handling are critical; stripping the wrong bytes corrupts ESP or exposes IKE packets to XFRM. GRO paths must preserve full L2 headers for VLAN reinjection. Keepalive and non-ESP marker classification must remain compatible with NAT-T.

## Test Signals
Test ESP-in-UDP keepalive drop, IKE pass-through, ESP with and without non-ESP marker, malformed short skb, GRO ESP-in-UDP aggregation, async transport finish, netfilter-enabled and disabled builds, and VLAN/L2 header preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/xfrm4_input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/xfrm4_output.c -->
# sources/distributed-fs/ceph-client/net/ipv4/xfrm4_output.c

## Purpose
This file is the IPv4 XFRM output wrapper. It routes packets through postrouting netfilter and then into the generic XFRM output engine, while handling rerouted packets and local PMTU errors.

## Important APIs, Types, and Functions
The exported functions are `xfrm4_output()` and `xfrm4_local_error()`. The internal `__xfrm4_output()` checks `skb_dst(skb)->xfrm` and calls either `dst_output()` for rerouted non-XFRM packets or `xfrm_output()` for transform processing.

## Control Flow
`xfrm4_output()` invokes `NF_HOOK_COND()` at `NF_INET_POST_ROUTING` unless `IPSKB_REROUTED` is already set. After the hook, `__xfrm4_output()` continues transform output when an XFRM state is attached; otherwise it marks the skb rerouted and sends it through normal dst output. Local EMSGSIZE reporting chooses the inner IP header for encapsulated packets and reports through `ip_local_error()`.

## State and Persistence Behavior
No persistent state is owned. The file mutates skb flags and reports socket errors. XFRM state and dst lifetime are managed by the core dst/XFRM subsystems.

## Dependencies and Integration Points
It integrates IPv4 netfilter postrouting, dst output, generic XFRM output, IPv4 local error reporting, UDP/TCP socket port context through `inet_sk()`, and encapsulated skb inner headers.

## Risks
Reroute flag handling prevents recursive postrouting. Incorrect inner/outer header selection for local errors can report the wrong destination or port to applications. Missing XFRM detection can bypass transforms.

## Test Signals
Test transformed and non-transformed dsts, netfilter postrouting reroute, encapsulated PMTU errors, non-encapsulated PMTU errors, and recursion avoidance with `IPSKB_REROUTED`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/xfrm4_output.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/xfrm4_policy.c -->
# sources/distributed-fs/ceph-client/net/ipv4/xfrm4_policy.c

## Purpose
This file registers IPv4-specific XFRM policy support. It provides route lookup, source-address selection, XFRM dst construction, PMTU/redirect forwarding, per-net dst ops setup, sysctl registration, and boot-time initialization of IPv4 XFRM state/protocol/policy.

## Important APIs, Types, and Functions
Important functions are `xfrm4_dst_lookup()`, `xfrm4_get_saddr()`, `xfrm4_fill_dst()`, `xfrm4_update_pmtu()`, `xfrm4_redirect()`, `xfrm4_dst_destroy()`, `xfrm4_net_init()`, `xfrm4_net_exit()`, and `xfrm4_init()`. Key structures include `xfrm4_dst_ops_template`, `xfrm4_policy_afinfo`, `xfrm4_net_ops`, `struct xfrm_dst`, and `struct rtable`.

## Control Flow
Policy lookup builds a `flowi4` from XFRM lookup params, including destination, optional source, DSCP, mark, protocol, ports, and L3 master device, then calls IPv4 route output. Source selection reuses this route lookup and reads the chosen `fl4.saddr`. Dst fill copies route metadata into the XFRM dst, holds the output device, and links the route into the uncached list. Per-net init copies dst ops, initializes dst entries, and optionally registers `net/ipv4/xfrm4_gc_thresh`.

## State and Persistence Behavior
Persistent state is per-net `net->xfrm.xfrm4_dst_ops`, optional per-net sysctl header, and XFRM policy AF registration. XFRM dsts persist as route wrappers until destroyed, at which point metrics and uncached route list membership are cleaned up.

## Dependencies and Integration Points
The file depends on IPv4 routing, l3mdev, dst metrics/lifetime management, XFRM policy core, sysctl, pernet operations, IPv4 blackhole routes, and state/protocol initialization in sibling XFRM files.

## Risks
Incorrect route metadata copying can break PMTU, gateway, local/broadcast/multicast flags, or input-route behavior. Per-net sysctl tables must duplicate init-net storage correctly. Device refs and uncached list removal must balance.

## Test Signals
Test policy route lookup with marks, DSCP, source address, L3 master, ports, blackhole route fallback, PMTU/redirect forwarding, per-net sysctl registration and teardown, network namespace creation failure unwinding, and XFRM dst destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/xfrm4_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/xfrm4_protocol.c -->
# sources/distributed-fs/ceph-client/net/ipv4/xfrm4_protocol.c

## Purpose
This file is the IPv4 XFRM protocol multiplexer for ESP, AH, and IPComp. It registers IPv4 protocol handlers with the inet layer, maintains priority-ordered XFRM protocol handler chains, dispatches input/error/callback events, and registers IPv4 XFRM input AF info.

## Important APIs, Types, and Functions
Key exports are `xfrm4_rcv_encap()`, `xfrm4_protocol_register()`, and `xfrm4_protocol_deregister()`. Important internals are `xfrm4_esp_rcv/err()`, `xfrm4_ah_rcv/err()`, `xfrm4_ipcomp_rcv/err()`, `xfrm4_rcv_cb()`, `proto_handlers()`, `netproto()`, and the `esp4_handlers`, `ah4_handlers`, and `ipcomp4_handlers` RCU lists.

## Control Flow
Registration validates protocol support, inserts the handler by descending priority under `xfrm4_protocol_mutex`, and adds the inet protocol handler when the first XFRM handler for that protocol appears. Receive callbacks iterate the relevant RCU handler chain until a handler accepts the packet by returning something other than `-EINVAL`; otherwise ICMP port-unreachable is sent and the skb is freed. Deregistration removes the handler, unregisters the inet protocol when the chain becomes empty, unlocks, and waits for `synchronize_net()`.

## State and Persistence Behavior
Persistent global state is the RCU head pointer for each protocol's handler chain and the registered `xfrm_input_afinfo`. Handler objects are owned by provider modules; this file only links/unlinks them.

## Dependencies and Integration Points
It integrates with inet protocol registration, ICMP unreachable generation, XFRM input core callbacks, RCU, mutex serialization, ESP/AH/IPComp provider modules, and UDP encap input via `xfrm4_rcv_encap()`.

## Risks
Priority collision returns `-EEXIST`; bad ordering can route packets to the wrong transform implementation. Registering the inet protocol after unlocking can leave partial state if `inet_add_protocol()` fails. Deregistration must wait for RCU readers before module code unloads.

## Test Signals
Test handler priority order, duplicate priority rejection, register/deregister for ESP/AH/IPComp, unknown protocol rejection, no-handler ICMP behavior, encap receive with route lookup, error handler fallback, and concurrent receive during module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/xfrm4_protocol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/xfrm4_state.c -->
# sources/distributed-fs/ceph-client/net/ipv4/xfrm4_state.c

## Purpose
This file registers IPv4 address-family callbacks for XFRM state handling. It connects IPv4 state objects to IPv4 output, transport-finish, and local-error functions.

## Important APIs, Types, and Functions
The central object is `xfrm4_state_afinfo`, with family `AF_INET`, tunnel protocol `IPPROTO_IPIP`, `output = xfrm4_output`, `transport_finish = xfrm4_transport_finish`, and `local_error = xfrm4_local_error`. `xfrm4_state_init()` registers it through `xfrm_state_register_afinfo()`.

## Control Flow
Initialization is called from `xfrm4_init()` before policy/protocol registration. After registration, XFRM core can call back into IPv4-specific output and input finishing paths for IPv4 states.

## State and Persistence Behavior
Persistent state is the registered AF info in XFRM core. This file owns no dynamic memory and has no teardown path in this source.

## Dependencies and Integration Points
It depends on XFRM core registration and sibling IPv4 XFRM functions in `xfrm4_output.c` and `xfrm4_input.c`.

## Risks
The file is small, but incorrect callback wiring would break all IPv4 XFRM state output/input completion or local PMTU error reporting. Protocol mismatch would affect IPIP tunnel-mode handling.

## Test Signals
Boot-time XFRM IPv4 initialization, IPv4 ESP/AH state output, transport-mode finish, local EMSGSIZE delivery, and IPIP tunnel-mode state setup indirectly validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/xfrm4_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/xfrm4_tunnel.c -->
# sources/distributed-fs/ceph-client/net/ipv4/xfrm4_tunnel.c

## Purpose
This module implements the IPv4 IPIP XFRM tunnel type and registers IPv4 tunnel handlers for XFRM tunnel-mode packets. It supports IPsec tunnel transformations that encapsulate IPv4 in IPv4.

## Important APIs, Types, and Functions
Important functions are `ipip_init_state()`, `ipip_output()`, `ipip_xfrm_rcv()`, `xfrm_tunnel_rcv()`, `ipip_init()`, and `ipip_fini()`. Key objects are `ipip_type`, `xfrm_tunnel_handler`, and, when IPv6 is enabled, `xfrm64_tunnel_handler`.

## Control Flow
Module init registers the IPIP XFRM type for `AF_INET`, then registers an IPv4 tunnel handler and optionally an AF_INET6 tunnel handler. State initialization rejects non-tunnel mode and rejects UDP or other encapsulation because this IPIP type supplies its own IPv4 tunnel header. Output pushes the skb back to the network header; input returns the inner IPv4 protocol. Tunnel receive calls `xfrm4_rcv_spi()` using the source address as SPI-like tunnel selector.

## State and Persistence Behavior
Persistent state consists of registered XFRM type and tunnel handler records. Individual XFRM states get `props.header_len = sizeof(struct iphdr)` during init. There is no per-state private allocation.

## Dependencies and Integration Points
It integrates with XFRM type registration, IPv4 tunnel handler registration, module aliasing for XFRM type autoload, and optional IPv6-family tunnel handler registration for IPv6 interop paths.

## Risks
Allowing non-tunnel or encapsulated states would create invalid header expectations. Init failure unwinding must unregister earlier handlers. Receive selector behavior depends on source address matching the XFRM tunnel lookup contract.

## Test Signals
Test module load/unload, tunnel-mode IPIP state creation, rejection of transport-mode and encap states, IPv4-in-IPv4 tunnel packet receive, optional AF_INET6 handler registration, and failure unwinding if handler registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/xfrm4_tunnel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/Kconfig -->
# sources/distributed-fs/ceph-client/net/ipv6/Kconfig

## Purpose
This Kconfig file defines the IPv6 protocol configuration menu and feature symbols for IPv6 routing, address behavior, IPsec transforms, tunnels, multicast routing, Segment Routing, RPL, IOAM, FoU, ILA, and related dependencies.

## Important APIs, Types, and Functions
The important "API" is the set of configuration symbols: `IPV6`, `IPV6_ROUTER_PREF`, `IPV6_ROUTE_INFO`, `IPV6_OPTIMISTIC_DAD`, `INET6_AH`, `INET6_ESP`, `INET6_ESP_OFFLOAD`, `INET6_ESPINTCP`, `INET6_IPCOMP`, `IPV6_MIP6`, `IPV6_ILA`, `INET6_XFRM_TUNNEL`, `INET6_TUNNEL`, `IPV6_VTI`, `IPV6_SIT`, `IPV6_SIT_6RD`, `IPV6_TUNNEL`, `IPV6_GRE`, `IPV6_FOU`, `IPV6_MULTIPLE_TABLES`, multicast routing symbols, `IPV6_SEG6_*`, `IPV6_RPL_LWTUNNEL`, and `IPV6_IOAM6_LWTUNNEL`.

## Control Flow
The top-level `menuconfig IPV6` gates all nested options. Symbols express dependency and selection flow: IPsec transforms select generic XFRM crypto pieces, tunnel features select tunnel and dst-cache support, route-policy features select `FIB_RULES`, and Segment Routing/IOAM/RPL select lightweight tunnel and cache infrastructure.

## State and Persistence Behavior
Kconfig choices persist in the kernel `.config` and drive compile-time object inclusion. Defaults matter: IPv6 defaults on, SIT defaults module, several tunnel/offload helpers default from other networking symbols, and many advanced options default off.

## Dependencies and Integration Points
The file coordinates with IPv6 Makefile object selection, crypto API, XFRM, netfilter, lightweight tunnels, dst cache, multicast routing, GRE demux, FoU, stream parser, sockmap messaging, and documentation.

## Risks
Incorrect dependencies can allow link failures or silently omit required helpers. Over-broad `select` statements can force features unexpectedly. Defaulting IPv6 on affects build footprint for kernels using this source tree.

## Test Signals
Use randconfig/allmodconfig builds, targeted configs for each tunnel/IPsec feature, dependency checks with NETFILTER/XFRM disabled, module/built-in combinations, and verification that selected objects in the IPv6 Makefile match enabled symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/Makefile -->
# sources/distributed-fs/ceph-client/net/ipv6/Makefile

## Purpose
This Makefile maps IPv6 Kconfig symbols to built-in or modular objects for the Linux INET6 stack. It defines the core `ipv6.o` aggregate and conditionally includes protocol, routing, XFRM, tunnel, offload, netfilter, and utility objects.

## Important APIs, Types, and Functions
The key build variables are `obj-$(CONFIG_IPV6)`, `ipv6-y`, multiple `ipv6-$(CONFIG_...)` fragments, transform modules such as `ah6.o`, `esp6.o`, `ipcomp6.o`, tunnel modules such as `sit.o`, `ip6_tunnel.o`, `ip6_gre.o`, and always/INET-gated objects such as `addrconf_core.o`, `ip6_checksum.o`, `protocol.o`, and `ip6_offload.o`.

## Control Flow
When `CONFIG_IPV6` is enabled, the core aggregate includes AF_INET6, address config, routing, UDP/TCP/RAW/ICMPv6, extension headers, flow labels, Segment Routing, RPL, IOAM, and notifier code. Additional fragments are appended based on sysctl, XFRM, netfilter, procfs, SYN cookies, netlabel, SRv6, RPL, IOAM, and multicast routing symbols. Standalone modules are emitted for IPv6 IPsec transforms and tunnel drivers according to their tristate symbols.

## State and Persistence Behavior
The file has no runtime state; it persists build graph decisions. `obj-$(subst m,y,$(CONFIG_IPV6)) += inet6_hashtables.o` ensures hash-table support is built in when IPv6 is available as built-in or module. Inside the IPv6 guard, UDP tunnel and multicast snooping helpers are added when applicable.

## Dependencies and Integration Points
It must stay aligned with `Kconfig`, source file names, XFRM/INET object dependencies, netfilter subdirectories, and tunnel/offload helper providers shared with IPv4 UDP.

## Risks
Mismatched Kconfig-to-object mapping causes missing symbols or dead code. Core objects included unconditionally under `ipv6-y` must not depend on disabled optional features except through stubs. Module/built-in combinations for IPv6 plus XFRM or UDP tunnel helpers are especially sensitive.

## Test Signals
Run IPv6 disabled, built-in, and module builds; allmodconfig; XFRM on/off; NETFILTER on/off; tunnel feature modules; and link checks for `inet6_hashtables.o`, `ip6_udp_tunnel.o`, and transform modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/Makefile -->
