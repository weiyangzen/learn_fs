# subset-b-006219 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/key/af_key.c -->
# sources/distributed-fs/ceph-client/net/key/af_key.c

## Purpose
Implements the kernel PF_KEYv2 socket family (`PF_KEY`, protocol `PF_KEY_V2`) and registers it as an XFRM key-manager bridge. It lets privileged userspace key managers create, update, delete, dump, and monitor IPsec security associations and policies through RFC2367/KAME-style SADB messages. It also translates XFRM kernel events back into PF_KEY notifications for registered sockets.

## Important APIs, types, and functions
- `struct netns_pfkey` stores the per-net namespace PF_KEY socket hlist and socket count.
- `struct pfkey_sock` extends `struct sock` with registration bits, promiscuous mode, dump walk state, a dump skb, and `dump_lock`.
- `pfkey_create`, `pfkey_release`, and `pfkey_ops` provide the socket-family surface. Creation requires `CAP_NET_ADMIN`, `SOCK_RAW`, and `PF_KEY_V2`.
- `parse_exthdrs`, `verify_address_len`, `verify_key_len`, and `verify_sec_ctx_len` validate SADB extension structure, duplicate extension use, lengths, families, key sizes, and security contexts.
- `pfkey_msg2xfrm_state` and `__pfkey_xfrm_state2msg` are the central bidirectional conversion routines between SADB SA messages and `struct xfrm_state`.
- `pfkey_spdadd`, `pfkey_spddelete`, `pfkey_spdget`, `pfkey_spddump`, and `pfkey_compile_policy` handle SPD policy import/export through `struct xfrm_policy`.
- `pfkey_funcs[]` dispatches SADB message types to handlers such as `SADB_GETSPI`, `SADB_ADD`, `SADB_DELETE`, `SADB_REGISTER`, `SADB_DUMP`, and SPD commands.
- `pfkeyv2_mgr` registers callbacks with XFRM: `.notify`, `.acquire`, `.compile_policy`, `.new_mapping`, `.notify_policy`, `.migrate`, and `.is_alive`.

## Control flow
`pfkey_sendmsg` copies a userspace message into an skb, validates the base `sadb_msg` with `pfkey_get_base_msg`, serializes XFRM configuration under `net->xfrm.xfrm_cfg_mutex`, broadcasts a clone to promiscuous PF_KEY sockets, parses extensions, and dispatches through `pfkey_funcs`. Errors are converted into unicast PF_KEY error replies by `pfkey_error`.

SA operations parse SADB addresses, algorithms, lifetimes, NAT-T data, mode, reqid, and security context into XFRM state, then call `xfrm_state_add`, `xfrm_state_update`, `xfrm_state_delete`, `xfrm_alloc_spi`, or lookup helpers. Policy operations build selectors from source/destination SADB addresses, parse embedded `sadb_x_ipsecrequest` templates, then call XFRM policy insert/delete/by-id/walk helpers. Dump operations store a long-lived XFRM walk in `pfkey_sock.dump` and resume from `pfkey_recvmsg` when receive buffer pressure allows.

XFRM callbacks flow in the other direction. Kernel SA and policy events call `pfkey_send_notify` or `pfkey_send_policy_notify`, which compose SADB messages and broadcast them to all or registered PF_KEY sockets. Acquire events allocate a sequence number and include algorithm proposal combinations derived from XFRM template masks.

## State and persistence behavior
State is runtime-only and namespaced. Per-net state is the PF_KEY socket hlist and socket counter. Per-socket state includes registration bitmask, promiscuous mode, and a resumable dump walker. Persistent IPsec state lives in XFRM state and policy databases, not in this file. Reference behavior depends on socket queues, RCU hlist traversal, `pfkey_mutex` for list mutation, and `dump_lock` for dump walker lifetime. `/proc/net/pfkey` is created per namespace when procfs is enabled.

## Dependencies and integration points
This file depends heavily on XFRM core (`xfrm_state_*`, `xfrm_policy_*`, algorithm descriptors, XFRM manager registration), LSM XFRM security hooks, net namespaces, procfs, sockets/skbs, RCU, and IPv4/IPv6 sockaddr support. It integrates with legacy key managers such as setkey/racoon-style PF_KEY users, while coexisting with newer netlink XFRM APIs. Module init registers `key_proto`, pernet state, the socket family, and the XFRM manager; exit unregisters them in reverse.

## Risks and edge cases
The largest risk surface is untrusted binary SADB parsing and length arithmetic. The code does substantial minimum-length, alignment, duplicate-extension, family, prefix, key, and security-context validation, but every conversion path remains sensitive to malformed extension combinations. Dump state is backpressure-sensitive and must terminate correctly on socket destruction. PF_KEY is marked deprecated and scheduled for removal in 2027, so new work should avoid expanding this interface. Migration support is conditional on `CONFIG_NET_KEY_MIGRATE`; policy expiration notifications are effectively stubbed.

## Test signals
Useful signals include PF_KEY socket creation permission/type/protocol failures, SADB error replies for malformed messages, successful `SADB_REGISTER` supported-algorithm replies, add/update/delete/get/dump behavior reflected in XFRM state, SPD add/delete/get/dump behavior, acquire/expire/flush broadcasts to registered sockets, `/proc/net/pfkey` output, namespace teardown warnings, and fuzzing of SADB extension parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/key/af_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l2tp/Kconfig -->
# sources/distributed-fs/ceph-client/net/l2tp/Kconfig

## Purpose
Defines the Kconfig entry points for the kernel L2TP subsystem. The menu controls the core L2TP data-plane support, debugfs visibility, L2TPv3 support, L2TP-over-IP sockets, and L2TPv3 Ethernet pseudowires.

## Important symbols
- `L2TP` is a tristate depending on `INET` and selecting `NET_UDP_TUNNEL`; it builds the core data-plane support.
- `L2TP_DEBUGFS` is a tristate depending on `L2TP && DEBUG_FS`; it builds `l2tp_debugfs`.
- `L2TP_V3` is a bool depending on `L2TP`; it gates L2TPv3-only features.
- `L2TP_IP` is a tristate depending on `L2TP_V3`; it enables plain IP protocol 115 L2TPv3 sockets.
- `L2TP_ETH` is a tristate depending on `L2TP_V3`; it enables Ethernet pseudowire net devices.

## Control flow and build impact
This file does not execute code directly. It shapes compilation through `Makefile`: core support follows `CONFIG_L2TP`, netlink follows `CONFIG_L2TP_V3`, IP/IP6 follows `CONFIG_L2TP_IP`, Ethernet follows `CONFIG_L2TP_ETH`, and debugfs follows `CONFIG_L2TP_DEBUGFS`.

## State and persistence behavior
No runtime state is stored here. The configuration choices persist in the kernel build configuration and decide whether corresponding code is built in, modular, or omitted.

## Dependencies and integration points
The configuration text documents that the kernel handles only L2TP data packets while userspace handles the control protocol. `L2TP_IP` affects firewall/protocol expectations because plain L2TP-over-IP uses IP protocol number 115. `L2TP_ETH` exposes virtual Ethernet interfaces suitable for IP assignment or bridging.

## Risks and test signals
Risk is primarily configuration mismatch: enabling pseudowire userspace without `L2TP_V3`, using plain IP encapsulation without `L2TP_IP`, or expecting debugfs files without `DEBUG_FS` and `L2TP_DEBUGFS`. Test signals are generated config dependencies, module availability, and Kbuild selection of the expected objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l2tp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l2tp/Makefile -->
# sources/distributed-fs/ceph-client/net/l2tp/Makefile

## Purpose
Maps L2TP Kconfig symbols to kernel objects and ensures the core source is compiled with the local include path.

## Important build rules
- `obj-$(CONFIG_L2TP) += l2tp_core.o` builds the core.
- `CFLAGS_l2tp_core.o += -I$(src)` makes local headers such as `trace.h` visible.
- `obj-$(subst y,$(CONFIG_L2TP),$(CONFIG_PPPOL2TP)) += l2tp_ppp.o` forces PPPoL2TP module behavior to follow core L2TP when core is modular.
- Similar `subst` rules build `l2tp_ip.o`, `l2tp_netlink.o`, `l2tp_eth.o`, and `l2tp_debugfs.o`.
- `l2tp_ip6.o` is added only when `CONFIG_IPV6` is non-empty and `CONFIG_L2TP_IP` is enabled.

## Control flow and integration
This is a Kbuild integration file. It ensures optional modules align with core L2TP linkage so optional pieces are not built in a way that cannot link to core support.

## State and persistence behavior
No runtime state is present. The only persistent effect is build graph structure.

## Risks and test signals
The main risk is modularity mismatch across core and optional L2TP pieces. Build matrix tests should cover built-in and module variants for `L2TP`, `PPP`, `L2TP_IP`, `L2TP_V3`, `L2TP_ETH`, `L2TP_DEBUGFS`, and `IPV6`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l2tp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l2tp/l2tp_core.c -->
# sources/distributed-fs/ceph-client/net/l2tp/l2tp_core.c

## Purpose
Provides the L2TP core data plane and lifetime management shared by L2TP pseudowires and encapsulations. It owns tunnel/session registries, packet receive sequencing and reordering, transmit header construction, UDP encapsulation hooks, asynchronous teardown, and per-net cleanup.

## Important APIs, types, and functions
- Per-net `struct l2tp_net` contains tunnel IDR, v2/v3 session IDRs, a v3 collision hash table, and locks.
- `l2tp_tunnel_get`, `l2tp_tunnel_get_next`, `l2tp_session_get`, `l2tp_session_get_next`, and `l2tp_session_get_by_ifname` provide refcounted lookup APIs.
- `l2tp_tunnel_create`/`l2tp_tunnel_register` and `l2tp_session_create`/`l2tp_session_register` implement two-phase construction.
- `l2tp_tunnel_delete` and `l2tp_session_delete` schedule asynchronous workqueue teardown.
- `l2tp_udp_encap_recv` is the UDP tunnel receive hook installed on UDP sockets.
- `l2tp_recv_common` parses cookies, sequence numbers, offsets, and queues valid payloads for pseudowire callbacks.
- `l2tp_xmit_skb` builds L2TP/UDP/IP or L2TP/IP headers, transmits through the tunnel socket, and updates stats.

## Control flow
Registration first reserves an IDR slot, validates or creates a tunnel socket, optionally installs UDP tunnel callbacks, then publishes the tunnel through IDR replacement. Session registration locks both the tunnel list and per-net session registry, rejects sessions when the tunnel is closing, handles L2TPv3 session-id collisions for UDP encapsulation through a collision hlist, links the session to the tunnel list, and publishes it in the proper IDR.

Receive flow for UDP begins in `l2tp_udp_encap_recv`: the UDP header is pulled, the L2TP version and data/control bit are parsed, control frames pass to userspace, data frames look up the session, version and optional v3 cookie/sublayer linearity are checked, then `l2tp_recv_common` validates cookies, negotiates sequence behavior, handles v2 offset fields, pulls the payload, queues by sequence, and invokes the pseudowire `recv_skb` callback in order.

Transmit flow starts at a pseudowire calling `l2tp_xmit_skb`. The core grows headroom, prepends v2 or v3 L2TP headers, optionally prepends UDP, calculates checksum policy, checks socket state under the socket lock, queues to IPv4 or IPv6 output, and updates tunnel/session counters.

## State and persistence behavior
Runtime state is held in per-net IDRs and htables, per-tunnel session lists and stats, and per-session cookies, sequence numbers, reorder queues, callbacks, and stats. State is not persisted outside the kernel. Lifetime is controlled by refcounts plus RCU freeing. Deletion is idempotent through `dead` bits and completes on the `l2tp` workqueue. Namespace pre-exit queues tunnel deletions and flushes the workqueue twice to process tunnel then session work.

## Dependencies and integration points
The core integrates with UDP tunnel infrastructure, IPv4/IPv6 transmit paths, XFRM policy checks indirectly through sockets, net namespaces, IDR, RCU, workqueues, tracepoints, and pseudowire modules via callbacks in `struct l2tp_session`. `l2tp_netlink.c` drives management creation/deletion, `l2tp_eth.c` supplies an Ethernet pseudowire, `l2tp_ip.c`/`l2tp_ip6.c` supply plain IP encapsulation sockets, and PPPoL2TP uses the same exported APIs.

## Risks and edge cases
High-risk areas are concurrent teardown versus lookup, v3 session-id collision handling, socket ownership/state checks during transmit, malformed short packets before `pskb_may_pull`, reorder queue expiry and sequence resynchronization, and namespace cleanup leaks. The code includes lock ordering (`tunnel->list_lock` then per-net session lock), refcounted lookups, RCU list traversal, and WARNs for unexpected non-empty IDRs.

## Test signals
Tests should exercise tunnel/session create-register-delete under UDP and IP encapsulation, duplicate IDs, v3 collision behavior, UDP control-frame pass-through, data-frame delivery, cookie mismatch drops, sequence required/optional modes, reorder timeout behavior, TX stats/error stats, module unload, and net namespace teardown with empty IDR assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l2tp/l2tp_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l2tp/l2tp_core.h -->
# sources/distributed-fs/ceph-client/net/l2tp/l2tp_core.h

## Purpose
Declares the internal L2TP core contracts shared by the core, management layer, pseudowire drivers, and IP encapsulation modules. It defines tunnel/session structures, configuration structures, statistics, callback interfaces, exported APIs, and small helpers.

## Important APIs and types
- `struct l2tp_stats` contains atomic TX/RX packet, byte, error, sequencing, cookie, out-of-order, and invalid counters.
- `struct l2tp_session_cfg` and `struct l2tp_tunnel_cfg` carry netlink or kernel-created configuration into core creation paths.
- `struct l2tp_session` stores IDs, cookies, L2-specific type, sequence state, reorder queue, list/hash nodes, callbacks, stats, and private pseudowire storage.
- `struct l2tp_tunnel` stores tunnel IDs, version, encapsulation, stats, namespace, tunnel socket, session list, refcount, and delete work.
- `struct l2tp_nl_cmd_ops` lets pseudowire modules plug session create/delete behavior into generic netlink.
- Export declarations cover tunnel/session lookup, lifecycle, RX/TX helpers, netlink pseudowire registration, IP-encap ioctl helper, and socket-to-tunnel lookup.

## Control flow contracts
The header documents that lookup APIs return referenced objects. Creation is two-phase: allocate/create then register. Destruction is asynchronous through delete helpers. Pseudowires receive packets through `recv_skb`, clean up through `session_close`, and optionally render debugfs-specific state through `show`.

## State and persistence behavior
The structures describe in-kernel runtime state only. There is no disk persistence. The `priv[]` flexible array allows pseudowire modules to attach session-local state with the same lifetime as the core session. Inline helpers compute L2-specific lengths, tunnel destination MTU, XFRM usage, and ensure optional v3 cookie/sublayer bytes are linear in an skb.

## Dependencies and integration points
The header depends on socket, dst, refcount, optional XFRM, skb, and L2TP UAPI definitions. It is the central integration point between `l2tp_core.c`, `l2tp_netlink.c`, `l2tp_debugfs.c`, `l2tp_eth.c`, `l2tp_ip.c`, `l2tp_ip6.c`, and PPPoL2TP.

## Risks and test signals
Contract risks include callers failing to drop lookup references, pseudowires deleting sessions without honoring asynchronous lifetime, and header-length/cookie/L2-specific configuration changes not followed by `l2tp_session_set_header_len`. Tests should check refcount balance, callback invocation, MTU/header computations, and v3 optional-data linearization on nonlinear skbs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l2tp/l2tp_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l2tp/l2tp_debugfs.c -->
# sources/distributed-fs/ceph-client/net/l2tp/l2tp_debugfs.c

## Purpose
Exposes L2TP tunnel and session runtime state through debugfs at `l2tp/tunnels`. It is diagnostic-only and renders core and pseudowire state through a seq_file iterator.

## Important APIs, types, and functions
- `rootdir` holds the debugfs directory dentry.
- `struct l2tp_dfs_seq_data` stores the opener's net namespace, namespace tracker, tunnel/session iteration keys, and current referenced objects.
- `l2tp_dfs_seq_start`, `l2tp_dfs_seq_next`, `l2tp_dfs_seq_stop`, and `l2tp_dfs_seq_show` implement seq_file iteration.
- `l2tp_dfs_seq_tunnel_show` prints tunnel IDs, socket addresses, encap type, session count, refcounts, and stats.
- `l2tp_dfs_seq_session_show` prints session IDs, pseudowire type, sequence state, refcount, config, cookies, stats, and invokes `session->show`.

## Control flow
Opening the file allocates iterator state and derives the network namespace from the current PID. Seq iteration alternates between a tunnel row and its session rows by using `l2tp_tunnel_get_next` and `l2tp_session_get_next`, dropping references from the previous element before advancing. The show path emits a header for `SEQ_START_TOKEN`, then tunnel or session detail. Release drops the tracked namespace and iterator memory.

## State and persistence behavior
No L2TP state is modified. The only local state is per-open iterator memory and the global debugfs dentry. References are held only while iterating and are dropped in `stop` or while advancing. Output reflects live in-kernel counters and may change between reads.

## Dependencies and integration points
Depends on debugfs, seq_file, net namespaces, socket address formatting, and the L2TP core lookup APIs. Pseudowires can extend session output through `session->show`; `l2tp_eth.c` uses this to print the interface name when debugfs support is enabled.

## Risks and test signals
Risks are reference leaks in iterator transitions, namespace lifetime handling, and stale pointers while sessions/tunnels are deleted concurrently. Test signals include successful creation/removal of `debugfs/l2tp/tunnels`, correct per-namespace output, stable reads while tunnels/sessions are created or deleted, and presence of pseudowire-specific lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l2tp/l2tp_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l2tp/l2tp_eth.c -->
# sources/distributed-fs/ceph-client/net/l2tp/l2tp_eth.c

## Purpose
Implements the L2TPv3 Ethernet pseudowire. It creates one virtual Ethernet net_device per L2TP Ethernet session, transmits Ethernet frames through `l2tp_xmit_skb`, and injects received L2TP payloads into the network stack as Ethernet frames.

## Important APIs, types, and functions
- `struct l2tp_eth` is netdev private state and points to the core session.
- `struct l2tp_eth_sess` is session private state and stores the RCU-protected net_device pointer.
- `l2tp_eth_dev_setup`, `l2tp_eth_dev_init`, and `l2tp_eth_dev_uninit` configure the Ethernet net_device, random MAC, stats, lockdep classes, and RCU pointer clearing.
- `l2tp_eth_dev_xmit` sends outbound frames via `l2tp_xmit_skb`.
- `l2tp_eth_dev_recv` validates `ETH_HLEN`, resets outer tunnel metadata, forwards the skb to the net_device, and updates stats.
- `l2tp_eth_create` is the netlink pseudowire create callback.
- `l2tp_eth_delete` unregisters the net_device on session close.

## Control flow
Module init registers `l2tp_eth_nl_cmd_ops` for `L2TP_PWTYPE_ETH`. Netlink session creation calls `l2tp_eth_create`, which creates a core session with private storage, allocates and configures a net_device, sets session callbacks, registers the session and device under RTNL, stores the device name in the session, publishes the RCU device pointer, and pins the module. TX from the netdev calls the core transmit path. RX from the core callback strips tunnel metadata and forwards the frame through `dev_forward_skb`.

## State and persistence behavior
State is runtime-only: one net_device plus one core session per pseudowire. The device pointer in session private data is RCU protected and cleared during netdev uninit. The module reference is incremented on successful create and decremented after unregister in delete. MTU is adjusted from tunnel destination MTU, IP/UDP overhead, Ethernet header, and L2TP session header length.

## Dependencies and integration points
Depends on the L2TP core, generic netlink pseudowire registration, net_device APIs, RTNL, Ethernet helpers, RCU, per-cpu dstats, and tunnel socket MTU helpers. Debugfs integration is optional through `session->show`.

## Risks and test signals
Risks include create/delete races between session and device registration, MTU under/overflow when route MTU is unknown or small, RCU pointer lifetime, module reference balance, and handling malformed short Ethernet payloads. Test signals include netlink creation producing an `l2tpeth*` interface, successful bridge/IP use, TX/RX stats movement, unregister on session delete, custom ifname handling, and debugfs interface output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l2tp/l2tp_eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l2tp/l2tp_ip.c -->
# sources/distributed-fs/ceph-client/net/l2tp/l2tp_ip.c

## Purpose
Implements IPv4 plain L2TPv3-over-IP encapsulation using IP protocol 115. It registers an IPv4 datagram socket protocol for userspace control frames and a network protocol handler for incoming L2TP/IP packets.

## Important APIs, types, and functions
- Per-net `struct l2tp_ip_net` holds socket hash and bind tables protected by `l2tp_ip_lock`.
- `struct l2tp_ip_sock` extends `inet_sock` with local and peer L2TP connection IDs.
- `l2tp_ip_recv` is the IPv4 protocol handler for IPPROTO_L2TP.
- `l2tp_ip_bind`, `l2tp_ip_connect`, `l2tp_ip_getname`, `l2tp_ip_sendmsg`, and `l2tp_ip_recvmsg` implement the socket behavior.
- `l2tp_ioctl` implements shared `SIOCOUTQ` and `SIOCINQ` support and is exported for IPv6.

## Control flow
Incoming packets first require at least four bytes. A nonzero first word is a data session ID, so the handler looks up the L2TPv3 session globally, checks optional v3 fields are linear, and calls `l2tp_recv_common`. A zero first word marks a control frame; the handler strips it, validates the L2TP control header shape, extracts the tunnel ID, finds a bound userspace socket by local/remote address, ingress interface, and connection ID, checks XFRM policy, resets conntrack, and queues the skb to the socket.

Userspace must bind before connect because there are no ports and autobind is disabled. Sendmsg creates a packet with a zero session-id word before the user control payload, routes to either a supplied destination or connected peer, and transmits through `ip_queue_xmit`.

## State and persistence behavior
State is per-net socket tables plus per-socket local/peer connection IDs and normal inet socket state. No persistent state is stored. Destroying a socket purges write queue state and asks the core to delete any tunnel using that socket.

## Dependencies and integration points
Depends on IPv4 protocol registration (`inet_add_protocol`), datagram socket registration, route lookup, XFRM IPv4 policy checks, conntrack reset, net namespaces, and L2TP core session lookup/RX handling. Core static tunnel creation uses this socket family for plain IP encapsulation.

## Risks and test signals
Risks include bind-table collisions, incorrect control/data classification, short packets, missing session ref drops on discard paths, route failures in sendmsg, and socket destroy racing with tunnel teardown. Test signals include AF_INET/SOCK_DGRAM/IPPROTO_L2TP socket creation, bind/connect/getname, control-frame send/receive, data-frame delivery to pseudowires, XFRM policy drops, bind duplicate `EADDRINUSE`, and namespace exit table warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l2tp/l2tp_ip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l2tp/l2tp_ip6.c -->
# sources/distributed-fs/ceph-client/net/l2tp/l2tp_ip6.c

## Purpose
Implements IPv6 plain L2TPv3-over-IP encapsulation using IP protocol 115. It mirrors the IPv4 L2TP/IP module with IPv6-specific bind, routing, flowlabel, control-message, and receive-option handling.

## Important APIs, types, and functions
- Per-net `struct l2tp_ip6_net` stores IPv6 L2TP socket and bind tables.
- `struct l2tp_ip6_sock` extends `inet_sock` with L2TP connection IDs and embeds `ipv6_pinfo`.
- `l2tp_ip6_recv` is the IPv6 protocol handler.
- `l2tp_ip6_bind`, `l2tp_ip6_connect`, `l2tp_ip6_getname`, `l2tp_ip6_sendmsg`, and `l2tp_ip6_recvmsg` implement IPv6 socket operations.
- `l2tp_ip6_push_pending_frames` writes the required zero session-id control prefix before flushing pending IPv6 frames.

## Control flow
Receive classification matches IPv4: nonzero first word is a data session ID delivered through L2TP core; zero first word is a userspace control frame. Control delivery validates header bits, extracts the tunnel ID, finds a bound socket by IPv6 local/remote address, ingress interface, and connection ID, checks XFRM IPv6 policy, resets conntrack, and queues the skb.

Bind rejects mapped and multicast addresses, handles link-local scope IDs and device lookup, checks address ownership, records the local connection ID, and moves the socket to the bind table. Connect rejects multicast peers, supports mapped-address multicast validation, requires prior bind, stores peer connection ID, and refreshes the bind table. Sendmsg builds IPv6 flow state, handles cmsgs, flowlabels, options, scope, route lookup, optional neighbor confirmation, appends data with a 4-byte transport prefix, and pushes pending frames unless `MSG_MORE`.

## State and persistence behavior
State is runtime-only in per-net tables and per-socket IDs, IPv6 addresses, options, pending frames, and normal socket caches. Destroy flushes pending IPv6 frames and requests core tunnel deletion for any tunnel using the socket.

## Dependencies and integration points
Depends on IPv6 protocol registration (`inet6_add_protocol`), IPv6 datagram routing/options/flowlabel helpers, XFRM IPv6 policy checks, L2TP core, net namespaces, and the shared `l2tp_ioctl` from the IPv4 module.

## Risks and test signals
Risks include scope handling for link-local addresses, option/flowlabel lifetime, pending-frame cleanup, mapped-address corner cases, bind table uniqueness, and race-free tunnel deletion on socket destroy. Test signals include AF_INET6/SOCK_DGRAM/IPPROTO_L2TP sockets, link-local bind with and without scope, control send/receive, `MSG_ERRQUEUE`, data delivery, route/no-route errors, XFRM policy behavior, and net namespace cleanup warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l2tp/l2tp_ip6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l2tp/l2tp_netlink.c -->
# sources/distributed-fs/ceph-client/net/l2tp/l2tp_netlink.c

## Purpose
Implements the generic netlink management interface for L2TP. It lets privileged userspace create, delete, modify, get, and dump tunnels and sessions, emits multicast notifications, and dispatches pseudowire-specific session creation/deletion through registered command ops.

## Important APIs, types, and functions
- `l2tp_nl_family` defines the generic netlink family, policies, operations, namespace support, and multicast group.
- `l2tp_nl_cmd_ops[]` maps pseudowire type to `struct l2tp_nl_cmd_ops` registered by modules such as `l2tp_eth`.
- Tunnel commands: `l2tp_nl_cmd_tunnel_create`, `_delete`, `_modify`, `_get`, `_dump`.
- Session commands: `l2tp_nl_cmd_session_create`, `_delete`, `_modify`, `_get`, `_dump`.
- `l2tp_nl_tunnel_send` and `l2tp_nl_session_send` serialize live kernel state and stats into netlink attributes.
- `l2tp_nl_register_ops` and `l2tp_nl_unregister_ops` export pseudowire registration.

## Control flow
Tunnel creation validates required IDs, protocol version, encapsulation, and either a userspace fd or static source/destination address attributes. It allocates and registers a core tunnel, then multicasts a create notification. Delete/get/modify first acquire a referenced tunnel from the core and then notify, delete, or serialize it.

Session creation validates tunnel existence, local/peer session IDs, pseudowire type, L2TPv2 PPP-only restriction, optional v3 L2-specific/cookie/ifname settings, sequence flags, LNS mode, and reorder timeout. It autoloads a pseudowire module when possible, calls the registered pseudowire `session_create`, looks up the newly created core session, and emits a notification. Delete finds by ifname or tunnel/session ID, notifies, then calls the pseudowire delete op when available. Modify updates sequence, LNS, and timeout fields and recomputes header length when send sequencing changes.

## State and persistence behavior
The file owns the runtime pseudowire ops table under the genl lock but stores tunnel/session state in L2TP core. Netlink dumps persist cursor keys in `cb->ctx`. Notifications are transient multicast messages. No disk persistence exists.

## Dependencies and integration points
Depends on generic netlink, L2TP UAPI attributes/commands, net namespaces, L2TP core lifecycle and lookup APIs, UDP/IP socket address accessors, optional IPv6 handling, and pseudowire modules. All mutating management operations require `GENL_UNS_ADMIN_PERM`; noop is unprivileged.

## Risks and test signals
Risks include incomplete strict validation because ops use `GENL_DONT_VALIDATE_STRICT`, attribute combinations that create invalid static tunnel sockets, pseudowire module autoload races, session deletion after notification failure, stats serialization buffer limits, and stale dump cursors during concurrent deletion. Test signals include netlink create/delete/get/dump for UDP and IP tunnels, IPv4/IPv6 address attributes, session creation for Ethernet and PPP types, module autoload, permission failures, multicast notifications, and dump consistency under concurrent changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l2tp/l2tp_netlink.c -->
