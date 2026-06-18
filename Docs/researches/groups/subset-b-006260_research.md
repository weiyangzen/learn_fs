# Research Group subset-b-006260

This grouped report covers the requested packet, Phonet, psample, and PSP source files. Each source file has a separate marker-wrapped section so the reconciliation lane can split the report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/packet/af_packet.c -->
# sources/distributed-fs/ceph-client/net/packet/af_packet.c

## Purpose
`af_packet.c` implements Linux AF_PACKET raw packet sockets, including legacy `SOCK_PACKET`, `SOCK_RAW` and `SOCK_DGRAM` packet sockets, classic queued receive, memory-mapped TPACKET RX/TX rings, fanout groups, device membership management, procfs reporting, and PF_PACKET module/per-net registration. It is the user/kernel boundary for sniffers, packet injectors, zero-copy capture/transmit tools, and packet fanout consumers.

## Important APIs, types, and functions
The file builds on `struct packet_sock`, `struct packet_ring_buffer`, `struct packet_fanout`, and `struct packet_rollover` from `internal.h`. Socket operations are exported through `packet_ops` and `packet_ops_spkt`, family creation through `packet_family_ops`, and per-net `/proc/net/packet` support through `packet_net_ops`.

Receive entry points are `packet_rcv_spkt()`, `packet_rcv()`, and `tpacket_rcv()`. `packet_rcv()` queues cloned/truncated skbs on the normal receive queue after BPF filtering, address metadata setup, drop accounting, and conntrack/dst cleanup. `tpacket_rcv()` writes directly into user-mmaped TPACKET frames or V3 blocks, handling snap length, offsets, VLAN/checksum/timestamp metadata, optional copy fallback, and frame/block ownership transitions.

Transmit entry points are `packet_sendmsg_spkt()`, `packet_snd()`, and `tpacket_snd()`. `packet_snd()` allocates an skb from the message iterator, optionally parses virtio-net headers, builds L2 headers for DGRAM sockets, validates MTU and headers, and calls `packet_xmit()`. `tpacket_snd()` walks TX ring frames marked `TP_STATUS_SEND_REQUEST`, builds skb fragments backed by mapped ring pages, marks frames `TP_STATUS_SENDING`, and returns them to userspace in `tpacket_destruct_skb()`.

Ring setup and mmap are centralized in `packet_set_ring()`, `alloc_pg_vec()`, `free_pg_vec()`, and `packet_mmap()`. TPACKET_V3 block logic uses `init_prb_bdqc()`, `prb_open_block()`, `prb_dispatch_next_block()`, `prb_retire_current_block()`, and `prb_retire_rx_blk_timer_expired()` to manage block fill, timeout retirement, and user/kernel ownership.

Fanout support is implemented by `fanout_add()`, `packet_rcv_fanout()`, the `fanout_demux_*()` helpers, `fanout_set_data_*()` for CBPF/EBPF fanout programs, and `fanout_release()`. Socket/device attachment is controlled by `packet_do_bind()`, `__register_prot_hook()`, `__unregister_prot_hook()`, and `packet_notifier()`.

## Control flow and state
Creation requires `CAP_NET_RAW`, allocates `packet_sock` via `sk_alloc()`, initializes `bind_lock`, `pg_vec_lock`, pending TX refcounts, protocol hooks, cached-device RCU pointer, and optionally registers the packet hook immediately when the protocol is nonzero. Binding under `bind_lock` resolves the requested device/protocol, unregisters any old hook with `synchronize_net()` when needed, updates `po->prot_hook`, `po->ifindex`, `po->num`, and `po->cached_dev`, then registers the hook if the device is usable.

Normal receive flow rejects loopback and wrong namespace traffic, adjusts headers according to socket type and device header visibility, runs socket BPF, enforces receive memory, snapshots source metadata into `PACKET_SKB_CB`, trims to snap length, queues the skb, and wakes waiters. TPACKET receive follows the same filtering and header adjustment, but reserves a ring frame/block, copies packet bytes into mapped memory, writes per-version headers, publishes status with memory barriers and cache flushes, and updates packet/drop stats.

TPACKET_V3 state is block-oriented. The current block starts as `TP_STATUS_KERNEL`, packet additions update `nxt_offset`, `prev`, `BLOCK_NUM_PKTS`, and `BLOCK_LEN`, and block retirement publishes `TP_STATUS_USER` plus loss/timeout flags. A soft hrtimer periodically retires partially filled blocks. If userspace has not returned the next block, `prb_freeze_queue()` marks the queue frozen and increments `tp_freeze_q_cnt`; later receive or timer activity reopens the block when ownership returns.

Transmit flow chooses between ring and non-ring paths. The ring path serializes with `pg_vec_lock`, resolves the target device from the cached bind or send address, parses per-frame packet length/offsets, builds an skb using ring pages as frags, optionally converts virtio-net metadata, marks the frame as sending, queues/direct-xmits, advances the TX ring head, and relies on the skb destructor to restore frame availability and wake blocked senders.

Lifecycle cleanup removes the socket from the per-net list, unregisters hooks, drops cached device references, flushes multicast memberships, tears down RX/TX rings while holding the socket lock, releases fanout membership after `synchronize_net()`, purges queues, frees pending refcounts, and drops the final sock reference.

## State and persistence behavior
State is in-memory only: socket configuration, multicast memberships, ring pages, fanout groups, cached device references, and stats live in kernel memory and disappear when sockets/modules/net namespaces are destroyed. `/proc/net/packet` is a read-only live view. `PACKET_STATISTICS` is clear-on-read for drops and packet counts. Mapped ring pages persist while the socket and VMAs are alive; `mapped` prevents unsafe ring reconfiguration.

Concurrency relies on `bind_lock` for packet hook/device/protocol state, `pg_vec_lock` for ring pointer and mmap reconfiguration, sk receive/write queue locks for ring head/status operations, RCU for live packet hooks and cached devices, `fanout_mutex` plus per-fanout spinlocks for group membership, and refcounts/completions for TX ring pending packets.

## Dependencies and integration points
The file integrates with the netdevice packet tap API (`dev_add_pack`, `__dev_remove_pack`), netdevice notifier chain, rtnetlink-visible devices, BPF socket filters, optional fanout BPF programs, netfilter egress when qdisc bypass is enabled, virtio-net header helpers, VLAN helpers, timestamping/error queue APIs, per-net procfs, generic datagram receive/poll, and capability checks. It depends on UAPI packet socket definitions such as `struct tpacket_req`, `TP_STATUS_*`, `PACKET_*` sockopts, and `sockaddr_ll`.

## Risks and edge cases
This file has high race and memory-safety sensitivity. Important risks include ring ownership races across userspace mmap and softirq receive, stale device pointers during unregister/down/up events, fanout membership changes while packets are in flight, V3 block timeout races with `skb_copy_bits()`, integer overflow in ring geometry, and status publication ordering between kernel and userspace. The code uses explicit barriers, cache flushes, RCU synchronization, and busy checks, but changes in these areas need careful packetdrill/selftest coverage.

User-controlled ring geometry, offsets, virtio-net header size, multicast requests, fanout options, and raw frame bytes are heavily validated; regressions could expose kernel memory corruption or packet injection bugs. Another operational risk is behavior compatibility: AF_PACKET is used by tcpdump, container runtimes, DHCP tools, traffic generators, and security agents, so changes to header offsets, auxdata, VLAN metadata, or fanout semantics can break existing tooling.

## Test signals
Useful tests include AF_PACKET kselftests, packet socket fanout tests, mmap RX/TX ring tests for TPACKET_V1/V2/V3, BPF filter and fanout CBPF/EBPF tests, VLAN auxdata checks, qdisc bypass/netfilter egress checks, netdev unregister/down/up while sockets are bound, namespace isolation tests, and stress tests with concurrent mmap close, ring reconfiguration, poll, send, and receive. Runtime signals include `/proc/net/packet`, `PACKET_STATISTICS`, drop counters, fanout rollover stats, `strace` of packet sockopts, and packet capture validation under tcpdump/libpcap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/packet/af_packet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/packet/diag.c -->
# sources/distributed-fs/ceph-client/net/packet/diag.c

## Purpose
`diag.c` implements SOCK_DIAG monitoring for AF_PACKET sockets. It lets userspace dump packet socket state over `NETLINK_SOCK_DIAG`, including socket identity, packet-specific flags, multicast memberships, ring configuration, fanout configuration, memory info, and optionally attached filter info.

## Important APIs, types, and functions
The module registers `packet_diag_handler` for `AF_PACKET`. `packet_diag_handler_dump()` validates `struct packet_diag_req`, rejects unsupported protocol filtering, and starts a dump through `netlink_dump_start()`. `packet_diag_dump()` walks `net->packet.sklist` under `sklist_lock` and calls `sk_diag_fill()` for each socket.

`sk_diag_fill()` writes the base `packet_diag_msg`, socket cookie, inode, packet protocol, and requested attributes. Helper functions populate specific attributes: `pdiag_put_info()` maps `packet_sock` fields and flags into `packet_diag_info`; `pdiag_put_mclist()` serializes `packet_mclist` entries under RTNL; `pdiag_put_ring()` and `pdiag_put_rings_cfg()` report RX/TX ring geometry and V3 block settings under `pg_vec_lock`; `pdiag_put_fanout()` reports fanout id/type under `fanout_mutex`.

## Control flow and state
The module is query-only. A dump request enters `packet_diag_handler_dump()`, then `packet_diag_dump()` iterates the per-net packet socket list using `cb->args[0]` as a cursor. Each socket is encoded into a netlink message, and if the skb fills, the cursor is updated so a later dump callback resumes at the next socket.

No persistent state is created beyond registering the handler at module load. Diagnostic output is a snapshot of live socket state, with locking chosen to match the owning subsystem: packet socket list mutex for enumeration, RTNL for multicast list reads, `pg_vec_lock` for ring reads, and `fanout_mutex` for fanout reads.

## Dependencies and integration points
This file depends directly on `internal.h` for `packet_sock`, ring, fanout, and flag helpers. It integrates with the generic sock_diag framework, netlink dump control, packet socket per-net state initialized by `af_packet.c`, and capability checks in `sock_diag_put_filterinfo()` for filter visibility.

## Risks and edge cases
The main risks are snapshot consistency and privilege leakage. Ring/fanout/membership state can change during dumps, so helpers use local locks but do not provide a single global atomic snapshot. Filter dumping is gated by `may_report_filterinfo`, derived from `CAP_NET_ADMIN`; regressions could expose BPF details to unprivileged callers. Netlink sizing paths must cancel partial messages on `-EMSGSIZE` to avoid malformed dumps.

## Test signals
Tests should open AF_PACKET sockets with combinations of memberships, rings, fanout, filters, and aux/origdev/vnet flags, then query `ss`, `sock_diag`, or custom netlink clients. Expected signals are correct dump continuation across small receive buffers, correct permission-dependent filter attributes, correct V3 ring fields, and absence of races while sockets are closing or changing fanout/ring configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/packet/diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/packet/internal.h -->
# sources/distributed-fs/ceph-client/net/packet/internal.h

## Purpose
`internal.h` defines the private AF_PACKET data model shared by the packet socket implementation and packet sock_diag module. It contains packet socket state, mmap ring descriptors, fanout group layout, rollover stats, multicast membership records, and flag helpers.

## Important APIs, types, and functions
`struct packet_mclist` tracks per-socket device memberships for multicast, promiscuous, allmulti, and unicast filters, including reference count and deferred removal list node. `struct tpacket_kbdq_core` is the TPACKET_V3 kernel block descriptor queue state: block array, current block, sequence, offsets, timeout, feature flags, and fill-in-progress lock. `struct packet_ring_buffer` abstracts RX/TX ring geometry, backing page vector, pending TX refcounts, and either V1/V2 RX owner map or V3 block queue.

`struct packet_fanout` represents a fanout group with net namespace, id, type, flags, member count, BPF program or round-robin counter, group packet hook, and flexible member socket array. `struct packet_rollover` stores rollover distribution counters and recent-flow history. `struct packet_sock` embeds `struct sock` first and adds packet-specific state including fanout pointer, stats, rings, bind and ring locks, flags, ifindex, protocol, rollover, multicast list, mapped VMA count, TPACKET settings, completion, cached netdev pointer, packet hook, and drop counter.

The header exports `fanout_mutex`, `PACKET_FANOUT_MAX`, `pkt_sk()`, `enum packet_sock_flags`, `packet_sock_flag_set()`, and `packet_sock_flag()`.

## Control flow and state
This header has no executable control flow beyond inline flag helpers. Its state definitions drive ownership and synchronization in `af_packet.c`: `packet_sock` lifetime is tied to socket lifetime, ring memory is swapped in/out under locks, V3 block queue state is updated under receive queue lock plus block fill rwlock, and fanout groups are protected by the global fanout mutex plus per-group spinlock.

## Dependencies and integration points
The structures use kernel networking primitives such as `struct sock`, `struct sk_buff`, `struct packet_type`, `struct net_device`, `possible_net_t`, RCU pointers, refcounts, hrtimers, completions, and UAPI TPACKET stats/version types. `diag.c` reads these fields to expose monitoring state.

## Risks and edge cases
Because these structures are shared across hot-path packet receive/transmit and diagnostics, layout or semantic changes can break cacheline-sensitive code, lock ordering, RCU access rules, or userspace-visible status behavior. The union in `packet_ring_buffer` means code must correctly distinguish V1/V2 owner maps from V3 block queues. `struct packet_sock` embeds `struct sock` first, so that invariant must be preserved for container casts.

## Test signals
Compile-time coverage should catch missing includes and layout references. Runtime validation comes indirectly from AF_PACKET socket creation, ring setup, fanout tests, sock_diag dumps, and stress tests that exercise close, mmap, fanout membership, and netdevice teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/packet/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/phonet/Kconfig -->
# sources/distributed-fs/ceph-client/net/phonet/Kconfig

## Purpose
This Kconfig entry defines `CONFIG_PHONET`, the tristate option for the Nokia Phonet protocol family. It controls compilation of the core Phonet stack and the Phonet pipe endpoint module.

## Important APIs, types, and functions
There are no C APIs in this file. The important interface is the `PHONET` symbol, user-visible prompt, help text, and module naming note. When enabled as a module, the core module is called `phonet`.

## Control flow and state
Kconfig selection determines whether `net/phonet/Makefile` builds `phonet.o` and `pn_pep.o`. There is no runtime state.

## Dependencies and integration points
The option is standalone in this file and is consumed by the Makefile and by C code guarded through the kernel configuration. It enables a protocol stack used for Nokia modem/phone communication and Maemo cellular data support.

## Risks and edge cases
The main risk is configuration discoverability and dependency accuracy. Because this protocol is specialized and security-sensitive, accidentally enabling it broadens kernel attack surface through PF_PHONET sockets and rtnetlink controls. Missing dependencies would surface as build failures.

## Test signals
Build matrix coverage should include `CONFIG_PHONET=n`, `m`, and `y`, verifying that socket family registration, module aliases, and dependent objects are present only when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/phonet/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/phonet/Makefile -->
# sources/distributed-fs/ceph-client/net/phonet/Makefile

## Purpose
The Makefile maps `CONFIG_PHONET` to Phonet object builds. It builds the core `phonet.o` aggregate and the pipe endpoint `pn_pep.o` aggregate.

## Important APIs, types, and functions
`obj-$(CONFIG_PHONET) += phonet.o pn_pep.o` includes both modules when Phonet is enabled. `phonet-y` links `pn_dev.o`, `pn_netlink.o`, `socket.o`, `datagram.o`, `sysctl.o`, and `af_phonet.o`; `pn_pep-y` links `pep.o` and `pep-gprs.o`.

## Control flow and state
There is no runtime control flow. Link composition determines which initialization functions land in each module: core protocol family/device/datagram/sysctl code in `phonet.o`, and pipe protocol plus GPRS netdev adapter in `pn_pep.o`.

## Dependencies and integration points
The file integrates Kbuild with the Kconfig symbol and reflects a module split where the core can autoload transport protocol modules through PF_PHONET protocol aliases.

## Risks and edge cases
Changing object membership can alter module load ordering and symbol availability. For example, `pep-gprs.o` depends on PEP helpers from `pep.o`, while core `af_phonet.o` calls `isi_register()` from `datagram.o`.

## Test signals
Build `CONFIG_PHONET=y` and `CONFIG_PHONET=m`, inspect linked symbols/modules, and verify module autoload aliases for PF_PHONET datagram and pipe protocols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/phonet/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/phonet/af_phonet.c -->
# sources/distributed-fs/ceph-client/net/phonet/af_phonet.c

## Purpose
`af_phonet.c` implements the PF_PHONET protocol family core. It manages Phonet transport protocol registration, socket creation, Phonet link-layer header operations, outbound Phonet packet construction, inbound packet dispatch/routing/error responses, packet tap registration, and module initialization/exit.

## Important APIs, types, and functions
Protocol registration uses the RCU-protected `proto_tab[]`, `phonet_proto_register()`, `phonet_proto_unregister()`, `phonet_proto_get()`, and `phonet_proto_put()`. Socket family creation is `pn_socket_create()`, which selects default datagram or pipe protocol, autoloads missing protocol modules, checks socket type, allocates a `pn_sock` or `pep_sock`, and installs protocol ops.

Header operations are `pn_header_create()` and `pn_header_parse()`, exported as `phonet_header_ops`. Outbound packet construction uses `pn_skb_send()`, `pn_send()`, and `pn_raw_send()`. Inbound packet handling is `phonet_rcv()`, registered as a `packet_type` for `ETH_P_PHONET`. Error helpers `send_obj_unreachable()` and `send_reset_indications()` generate Common Message responses for undeliverable local objects when `can_respond()` allows it.

## Control flow and state
Socket creation requires `CAP_SYS_ADMIN`, resolves a `struct phonet_protocol`, allocates a PF_PHONET sock with that protocol's `struct proto`, initializes base `pn_sock` fields, calls protocol `init()`, and releases the module reference.

Outbound flow in `pn_skb_send()` chooses a device based on bound device, local-address loopback, resource routing, explicit route, or default Phonet device. It derives a source address with `phonet_address_get()`, fills the Phonet header in `pn_send()`, adds a device header for non-loopback traffic, and queues through `dev_queue_xmit()` or `netif_rx()` for loopback.

Inbound flow in `phonet_rcv()` clones as needed, validates and trims to the Phonet length field, extracts destination sockaddr, delivers broadcasts to broadcast sockets, resolves resource-routed packets by resource table, delivers local packets by object/port lookup, sends object-unreachable/reset indications for missing local endpoints, or routes nonlocal packets via `phonet_route_output()`. Routing re-adds the Phonet header, prevents same-device loops, expands headroom for device headers, and transmits.

Module initialization initializes per-net/device state, socket hashes, PF_PHONET family, packet tap, sysctl, and datagram protocol. Exit reverses this sequence and unregisters the packet tap and devices.

## State and persistence behavior
State includes the transport protocol table, PF_PHONET registration, packet tap registration, and sysctl/device state owned by other files. It is kernel memory only and disappears on module unload. Protocol table entries are protected by `proto_tab_lock` for updates and RCU for readers; module references prevent unloading while a protocol is selected for socket creation.

## Dependencies and integration points
This file integrates with netdevice packet taps (`dev_add_pack`), Phonet device/address/route helpers from `pn_dev.c`, socket lookup/resource helpers from `socket.c`, datagram registration from `datagram.c`, sysctl, and module autoload via `request_module("net-pf-%d-proto-%d", ...)`.

## Risks and edge cases
Risks include malformed Phonet length handling, loopback races after address deletion, route loops, source address selection failures, and error-response amplification. `can_respond()` is important to avoid replying to error messages. `phonet_proto_register()` registers the proto before inserting it in `proto_tab`; if the table slot is busy, the current code returns an error without unregistering the proto, so registration callers and module load paths are sensitive to duplicate protocol attempts.

## Test signals
Tests should cover socket creation permission checks, default protocol selection, module autoload, local datagram delivery, broadcast delivery, resource routing, route forwarding, address deletion race with loopback skb, route loop detection, MTU/length validation, and expected Common Message errors for unreachable local objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/phonet/af_phonet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/phonet/datagram.c -->
# sources/distributed-fs/ceph-client/net/phonet/datagram.c

## Purpose
`datagram.c` implements the ISI datagram transport for PF_PHONET `SOCK_DGRAM` sockets. It provides send/receive/ioctl/close behavior and registers the `PN_PROTO_PHONET` protocol with the Phonet core.

## Important APIs, types, and functions
The protocol object is `pn_proto`, with callbacks `pn_sock_close()`, `pn_ioctl()`, `pn_init()`, `pn_sendmsg()`, `pn_recvmsg()`, `pn_backlog_rcv()`, `pn_sock_hash()`, `pn_sock_unhash()`, and `pn_sock_get_port()`. `pn_dgram_proto` binds `pn_proto` to `phonet_dgram_ops` and `SOCK_DGRAM`. Module-facing registration is through `isi_register()` and `isi_unregister()`.

## Control flow and state
`pn_sendmsg()` validates message flags and `sockaddr_pn`, allocates an skb with `MAX_PHONET_HEADER` headroom, copies the user payload, and delegates header/device routing to `pn_skb_send()`. `pn_recvmsg()` receives a datagram with `skb_recv_datagram()`, extracts the source Phonet sockaddr, copies data with truncation support, fills `msg_name`, and frees the skb. `pn_backlog_rcv()` queues received skbs to the socket receive queue or drops them on failure.

`pn_ioctl()` supports `SIOCINQ` and resource bind/unbind ioctls (`SIOCPNADDRESOURCE`, `SIOCPNDELRESOURCE`), delegating resource table updates to `socket.c`.

## State and persistence behavior
The file itself stores no global runtime state. Per-socket state lives in `struct pn_sock` and socket queues. `pn_destruct()` purges the receive queue when the final socket reference is gone.

## Dependencies and integration points
It depends on the Phonet core send path (`pn_skb_send()`), common socket hash/port/resource helpers in `socket.c`, generic datagram receive helpers, and PF_PHONET protocol registration in `af_phonet.c`.

## Risks and edge cases
The main risks are user payload copy errors, flag compatibility, datagram truncation semantics, resource ioctl authorization through delegated helpers, and ensuring skb ownership/drop paths are correct when `pn_skb_send()` fails. Since send requires an explicit destination, callers get `-EDESTADDRREQ` when `msg_name` is absent.

## Test signals
Exercise datagram send/receive between local Phonet sockets, invalid flags, short or wrong-family sockaddr, truncation and `MSG_TRUNC`, `SIOCINQ`, resource add/delete, receive queue pressure, and module registration/unregistration of `PN_PROTO_PHONET`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/phonet/datagram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/phonet/pep-gprs.c -->
# sources/distributed-fs/ceph-client/net/phonet/pep-gprs.c

## Purpose
`pep-gprs.c` adapts a Phonet pipe endpoint socket into a point-to-point network device carrying IPv4/IPv6 packets. It is the `PNPIPE_ENCAP_IP` implementation used by PEP sockets for GPRS-style data connectivity.

## Important APIs, types, and functions
`struct gprs_dev` binds a PEP socket to a `struct net_device` and stores original socket callbacks. Netdevice callbacks are `gprs_open()`, `gprs_close()`, and `gprs_xmit()` via `gprs_netdev_ops`; setup is `gprs_setup()`. Socket callbacks are `gprs_state_change()`, `gprs_data_ready()`, and `gprs_write_space()`. Public functions are `gprs_attach()` and `gprs_detach()`.

`gprs_type_trans()` classifies received payloads as IPv4 or IPv6. `gprs_recv()` converts PEP data skbs into netif RX skbs, including a frag-list wrapper for misaligned payloads. `gprs_xmit()` validates outbound skb protocol, transfers ownership to the PEP socket, sends with `pep_write()`, updates netdev stats, and gates the netdev TX queue based on `pep_writeable()`.

## Control flow and state
Attach allocates and registers a `gprs%d` netdev, then under the socket lock verifies no existing `sk_user_data`, rejects closed/listening/dead sockets, installs callback overrides, stores the adapter in `sk_user_data`, releases the socket, and takes an extra socket reference. Detach restores original callbacks under the lock, unregisters the netdev, and drops the socket reference.

Inbound flow is callback-driven: PEP data readiness drains `pep_read()` until empty, orphans each skb, and passes it to `gprs_recv()` for protocol classification and `netif_rx()`. Outbound flow is netdev-driven: `ndo_start_xmit` sends only IPv4/IPv6, calls `pep_write()`, updates stats, stops the queue, and wakes it again if PEP credits allow.

## State and persistence behavior
Runtime state persists while the socket is attached: `sk_user_data` points to `gprs_dev`, netdev private data points back to the socket, and overridden callbacks route socket events into netdev queue/carrier behavior. No disk persistence exists. Close paths in `pep.c` call `gprs_detach()` when `pn->ifindex` is set.

## Dependencies and integration points
The file depends on PEP helpers (`pep_writeable()`, `pep_write()`, `pep_read()`), netdevice registration, IP/EtherType definitions, and TCP state constants used by PEP. It exposes a netdev of type `ARPHRD_PHONET_PIPE`, with `NETIF_F_FRAGLIST` support and no hardware header.

## Risks and edge cases
Key risks are socket callback hijacking/restoration races, attach/detach lifetime ordering, misaligned PEP data, nested frag-list cleanup, netdev stats consistency, and TX queue wake/stop correctness with PEP credit flow control. `gprs_attach()` registers the netdev before taking the socket lock, so failures after registration must unregister correctly.

## Test signals
Tests should enable `PNPIPE_ENCAP_IP`, verify a `gprs%d` device appears and disappears, send IPv4/IPv6 through the device, reject non-IP protocols, exercise PEP close/reset behavior, check queue wake on credits, test attach failure on already attached/dead/listening sockets, and validate RX stats/drop counters for malformed payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/phonet/pep-gprs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/phonet/pep.c -->
# sources/distributed-fs/ceph-client/net/phonet/pep.c

## Purpose
`pep.c` implements the Phonet Pipe End Point protocol (`PN_PROTO_PIPE`) for PF_PHONET `SOCK_SEQPACKET` sockets. It provides pipe connection setup, accept/connect semantics, flow-control negotiation, control request handling, data transfer, pipe removal/disconnect, socket options, and optional GPRS netdev encapsulation support.

## Important APIs, types, and functions
Protocol registration is `pep_register()`/`pep_unregister()` around `pep_pn_proto` and `pep_proto`. Socket callbacks include `pep_sock_close()`, `pep_sock_accept()`, `pep_sock_connect()`, `pep_ioctl()`, `pep_init()`, `pep_setsockopt()`, `pep_getsockopt()`, `pep_sendmsg()`, `pep_recvmsg()`, `pep_do_rcv()`, `pep_sock_unhash()`, and common Phonet hash/port helpers.

Packet formatting helpers are `pep_alloc_skb()`, `pep_reply()`, `pep_indicate()`, `pipe_handler_request()`, `pipe_handler_send_created_ind()`, `pep_accept_conn()`, `pep_reject_conn()`, and `pep_ctrlreq_error()`. Flow-control helpers include `pipe_negotiate_fc()`, `pipe_rcv_created()`, `pipe_rcv_status()`, `pipe_grant_credits()`, `pipe_start_flow_control()`, `pep_writeable()`, `pipe_skb_send()`, `pep_write()`, and `pep_read()`.

Receive dispatch is split between listening/unconnected routing in `pep_do_rcv()`, connected accepted sockets in `pipe_do_rcv()`, and active connector handling in `pipe_handler_do_rcv()`.

## Control flow and state
PEP maps protocol state to TCP-style socket states: `TCP_CLOSE` unused, `TCP_LISTEN` listener, `TCP_SYN_SENT` connection or enable pending, `TCP_SYN_RECV` connected but disabled, `TCP_ESTABLISHED` enabled, and `TCP_CLOSE_WAIT` disconnected. `struct pep_sock` stores listener link, child pipe hlist, control request queue, pipe handle, peer type, flow-control mode, TX credits, RX credits, initial enable state, alignment mode, and optional GPRS ifindex.

Server-side flow starts with a listening socket receiving `PNS_PEP_CONNECT_REQ` in `pep_do_rcv()`, queuing it on the listener accept queue. `pep_sock_accept()` dequeues the request, parses sub-blocks, validates requested state and duplicate pipe handle, allocates a child sock, initializes connected pipe state, sends a connect response with supported flow controls, and links the child under the listener hlist.

Client-side connect sends `PNS_PEP_CONNECT_REQ` through `pipe_handler_request()` and sets `TCP_SYN_SENT`; `pipe_handler_do_rcv()` processes `PNS_PEP_CONNECT_RESP`, negotiates flow controls, sends created indication, and transitions to `TCP_SYN_RECV` or `TCP_ESTABLISHED` depending on `init_enable`. Enable requests similarly wait for enable response and indication.

Data receive handles `PNS_PIPE_DATA` and `PNS_PIPE_ALIGNED_DATA` by stripping pipe headers, applying RX credits when flow-safe, queueing skbs, and waking readers. Data send requires `MSG_EOR`, waits for established state and positive TX credits, prepends the correct pipe data header, decrements credits atomically, and restores credits on send failure. Control requests are queued separately on `ctrlreq_queue` and exposed through OOB/urgent receive behavior.

Close sends disconnect/remove requests for active pipes, sets `TCP_CLOSE`, detaches any GPRS netdev, and drops the extra self reference taken around `sk_common_release()`.

## State and persistence behavior
All state is per socket and memory resident. Listener sockets own child pipe hlist membership. Accepted child sockets hold a reference on the listener until unhash. Flow-control credits are runtime counters; stats are mainly socket drops and queue lengths. `PNPIPE_ENCAP` can create a netdev whose lifetime is tied to the socket option and socket close.

## Dependencies and integration points
`pep.c` depends on PF_PHONET common socket plumbing, `pn_skb_send()`, Phonet sockaddr helpers, generic socket queue/wait APIs, TCP state constants, and the GPRS adapter in `pep-gprs.c`. It registers as a separate `pn_pep` module and can be autoloaded by PF_PHONET protocol requests.

## Risks and edge cases
Risks include state-machine mismatches, credit underflow/overgrant, child/listener lifetime errors, control queue growth, skb ownership after reply/error paths, and blocking connect/send wait behavior under signals or close. The `pep_setsockopt()` expression `if (!pn->ifindex == !val)` is logically intentional but easy to misread; changes there can break attach/detach idempotence. GPRS attachment requires careful lock release and reacquisition because it calls netdev registration code.

## Test signals
Test listener accept, duplicate pipe handles, invalid connect sub-blocks, active connect/enable success and failure, disconnect/reset/disable indications, one-credit and multi-credit flow control, TX blocking and `MSG_DONTWAIT`, OOB control requests, `SIOCINQ`, `SIOCPNENABLEPIPE`, `PNPIPE_HANDLE`, `PNPIPE_INITSTATE`, `PNPIPE_ENCAP`, listener unhash with children, and module autoload/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/phonet/pep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/phonet/pn_dev.c -->
# sources/distributed-fs/ceph-client/net/phonet/pn_dev.c

## Purpose
`pn_dev.c` manages Phonet addresses, Phonet-capable netdevices, simple Phonet routes, per-network-namespace Phonet state, procfs entries, netdevice notifier integration, and initialization/exit of Phonet device infrastructure.

## Important APIs, types, and functions
`struct phonet_net` stores a `phonet_device_list` and `phonet_routes` table per net namespace. Address/device functions include `phonet_device_list()`, `phonet_device_get()`, `phonet_address_add()`, `phonet_address_del()`, `phonet_address_get()`, and `phonet_address_lookup()`. Route functions include `phonet_route_add()`, `phonet_route_del()`, `phonet_route_get_rcu()`, and `phonet_route_output()`.

Initialization and teardown are `phonet_device_init()` and `phonet_device_exit()`. Per-net callbacks are `phonet_init_net()` and `phonet_exit_net()`. Device notifier logic is in `phonet_device_notify()`, with helpers `phonet_device_autoconf()`, `phonet_device_destroy()`, and `phonet_route_autodel()`.

## Control flow and state
Per namespace, Phonet devices are kept in an RCU list guarded by `pndevs.lock`; each device entry has a bitmap of 64 possible 6-bit addresses. Adding an address finds or allocates the device entry and sets `addr >> 2`. Deleting clears the bit and removes the device entry when no addresses remain. Address lookup scans registered/up devices under RCU.

Source address selection prefers an address on the target device matching the destination address high bits, then falls back to the first address on the device, then recursively tries another default Phonet device. `phonet_device_get()` returns the first registered/up device with a held reference.

Routes are a 64-entry RCU table keyed by `daddr >> 2`, protected for updates by `routes.lock`. Add stores a device and takes a reference. Delete clears the slot but leaves synchronization and `dev_put()` to the caller. Device unregister destroys address state, emits address deletion notifications, removes routes pointing to the device, waits for RCU, emits route deletion notifications, and drops route-held device references.

`phonet_device_init()` registers pernet state, global `/proc/net/pnresource`, netdevice notifier, and rtnetlink handlers. Exit unregisters rtnetlink handlers, notifier, pernet state, and procfs.

## State and persistence behavior
Address and route state is in kernel memory and per net namespace except the pnresource proc entry in init_net. It is not persistent across module unload or namespace/device teardown. Device references held by routes are explicitly managed and released after RCU grace periods.

## Dependencies and integration points
The file integrates with netdevice registration/unregistration, private Phonet autoconfiguration ioctl `SIOCPNGAUTOCONF`, rtnetlink notification helpers in `pn_netlink.c`, procfs seq operations from `socket.c`, and Phonet routing decisions in `af_phonet.c`.

## Risks and edge cases
Risks include address bitmap shift semantics (`addr >> 2`), device reference leaks in route add/delete/autodel, RCU lifetime of device entries, missing notifications on failure paths, and default route fallback selecting unexpected devices. `phonet_exit_net()` warns if device entries remain, so teardown ordering with netdevices matters.

## Test signals
Test adding/deleting addresses via rtnetlink, automatic address config on ARPHRD_PHONET registration, route add/delete/dump, device unregister cleanup of addresses/routes, namespace isolation, source address selection, default route fallback, procfs entries, and refcount leak detection under repeated add/delete/unregister cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/phonet/pn_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/phonet/pn_netlink.c -->
# sources/distributed-fs/ceph-client/net/phonet/pn_netlink.c

## Purpose
`pn_netlink.c` implements the rtnetlink control plane for Phonet addresses and routes. It handles RTM_NEWADDR/DELADDR/GETADDR and RTM_NEWROUTE/DELROUTE/GETROUTE for `PF_PHONET`, and emits multicast notifications when addresses or routes change.

## Important APIs, types, and functions
Address handling uses `addr_doit()`, `getaddr_dumpit()`, `fill_addr()`, `phonet_address_notify()`, and `ifa_phonet_policy`. Route handling uses `route_doit()`, `route_dumpit()`, `fill_route()`, `rtm_phonet_notify()`, and `rtm_phonet_policy`. `phonet_rtnl_msg_handlers[]` declares the rtnetlink handlers, and `phonet_netlink_register()` registers them with `rtnl_register_many()`.

## Control flow and state
Address add/delete requests require both `CAP_NET_ADMIN` and `CAP_SYS_ADMIN`, parse `IFA_LOCAL`, require the low two address bits to be zero, resolve the target device by ifindex under RCU, call `phonet_address_add()` or `phonet_address_del()`, and notify `RTNLGRP_PHONET_IFADDR` on success. Dumps walk each Phonet device and each set address bit using callback cursors for device and address position.

Route add/delete requests require the same capabilities, parse `RTA_DST` and `RTA_OIF`, require main-table unicast routes and aligned 6-bit destination addresses, resolve the output device, and call `phonet_route_add()` or `phonet_route_del()`. Successful delete waits for RCU and drops the route-held device reference. Dumps iterate all 64 route slots and emit route messages for populated entries.

## State and persistence behavior
This file does not own persistent state; it mutates address and route state in `pn_dev.c` and emits live netlink notifications. Dump cursors are stored in `netlink_callback->args` only for the duration of a dump.

## Dependencies and integration points
It integrates with rtnetlink, Phonet device/route helpers, netlink capability checks, netlink multicast groups `RTNLGRP_PHONET_IFADDR` and `RTNLGRP_PHONET_ROUTE`, and per-net socket namespace resolution through `sock_net(skb->sk)`.

## Risks and edge cases
Risks include capability policy regressions, address alignment validation, route delete reference handling, dump cursor correctness, and netlink message sizing. Because handlers use `RTNL_FLAG_DOIT_UNLOCKED`/`DUMP_UNLOCKED`, underlying helpers must provide their own locking and RCU protection.

## Test signals
Use `ip`/rtnetlink tests or custom netlink clients to add/delete/dump Phonet addresses and routes, verify notifications, reject unaligned addresses, reject wrong table/type, enforce capabilities, exercise partial dumps with small skb buffers, and run concurrent route/device unregister stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/phonet/pn_netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/phonet/socket.c -->
# sources/distributed-fs/ceph-client/net/phonet/socket.c

## Purpose
`socket.c` provides common PF_PHONET socket operations, global socket lookup tables, port allocation, resource binding, procfs sequence output, and shared datagram/stream `proto_ops`. It is the address/port/resource registry used by the datagram and PEP protocols.

## Important APIs, types, and functions
Core ops include `pn_socket_release()`, `pn_socket_bind()`, `pn_socket_autobind()`, `pn_socket_connect()`, `pn_socket_accept()`, `pn_socket_getname()`, `pn_socket_poll()`, `pn_socket_ioctl()`, `pn_socket_listen()`, and `pn_socket_sendmsg()`. Exported protocol ops are `phonet_dgram_ops` and `phonet_stream_ops`.

Socket hash functions are `pn_sock_init()`, `pn_hash_list()`, `pn_find_sock_by_sa()`, `pn_deliver_sock_broadcast()`, `pn_sock_hash()`, `pn_sock_unhash()`, and `pn_sock_get_port()`. Resource functions are `pn_find_sock_by_res()`, `pn_sock_bind_res()`, `pn_sock_unbind_res()`, and `pn_sock_unbind_all_res()`. Procfs seq operations are `pn_sock_seq_ops` and `pn_res_seq_ops`.

## Control flow and state
The global `pnsocks` hash table has 16 buckets protected by `pnsocks.lock` for mutation and RCU for lookup. Binding validates AF_PHONET address, checks local address availability, locks the socket, prevents rebinding, allocates a port under `port_mutex`, writes source object/resource, and hashes the socket. Autobind binds to an anonymous address/port; importantly, it only treats `-EINVAL` as "already bound" when the socket actually has a nonzero port, preventing false success after state-related bind failures.

Connect autobinds, validates destination sockaddr, checks socket state, stores destination object/resource, calls the protocol-specific connect callback, waits while `TCP_SYN_SENT` unless nonblocking or interrupted, and maps final protocol state to `SS_CONNECTED` or an errno. Listen autobinds and moves the socket to `TCP_LISTEN`. Accept delegates to the protocol accept callback and grafts the returned sock to the new socket.

`pn_socket_poll()` combines receive queue, PEP control request queue, close/hup state, send buffer, and PEP TX credits. `pn_socket_ioctl()` handles `SIOCPNGETOBJECT` by choosing a device and local source address, then delegates other commands to `sk_ioctl()`.

Resource binding is limited to init_net and `CAP_SYS_ADMIN`. The 256-entry `pnres` RCU table maps Phonet resource ids to sockets with held references. Unhash removes normal hash membership, unbinds all resources, and waits for RCU before final release.

## State and persistence behavior
Socket hash and resource tables are global in-memory state. Port allocation uses a static rotating `port_cur` and sysctl-provided local port range. Procfs exposes live socket and resource snapshots. No state persists across module unload.

## Dependencies and integration points
This file integrates with Phonet address lookup/device selection in `pn_dev.c`, PEP fields for stream poll behavior, datagram/PEP protocol callbacks, sysctl port range from `sysctl.c`, procfs registration from `pn_dev.c`, and generic socket helpers.

## Risks and edge cases
Risks include global hash namespace behavior, port collision races, RCU/refcount lifetime for resource sockets, bind/autobind state handling, and assumptions that stream sockets are PEP sockets in `pn_socket_poll()`. The fixed autobind behavior is a key test point because treating all `-EINVAL` binds as success can leave sockets without ports and later crash.

## Test signals
Test bind/autobind, port range exhaustion, explicit port conflict, local address validation, connect blocking/nonblocking/interrupted paths, listen/accept, broadcast delivery, resource bind/unbind in init_net and non-init namespaces, procfs socket/resource output, `SIOCPNGETOBJECT`, and the autobind `-EINVAL` regression case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/phonet/socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/phonet/sysctl.c -->
# sources/distributed-fs/ceph-client/net/phonet/sysctl.c

## Purpose
`sysctl.c` implements `/proc/sys/net/phonet/local_port_range`, the runtime tunable used by Phonet automatic port allocation.

## Important APIs, types, and functions
`phonet_get_local_port_range()` exports a lockless-reader API using a seqlock. `proc_local_port_range()` validates sysctl reads/writes with `proc_dointvec_minmax()`, enforces `min <= max`, and updates the range via `set_local_port_range()`. `phonet_sysctl_init()` and `phonet_sysctl_exit()` register/unregister the sysctl table.

## Control flow and state
The default dynamic range is `0x40..0x7f`, with accepted values bounded by `0..1023`. Readers loop with `read_seqbegin()`/`read_seqretry()` until they see a consistent range. Writers copy through a temporary table so invalid writes do not partially update global state, then publish both values under `write_seqlock()`.

## State and persistence behavior
`local_port_range` is global in-memory state for init_net sysctl registration. It affects future automatic port allocation in `pn_sock_get_port()` but does not rebind existing sockets. It is not persistent across reboot/module unload unless userspace reapplies sysctl settings.

## Dependencies and integration points
The main consumer is `pn_sock_get_port()` in `socket.c`. The sysctl path is registered by `phonet_init()` in `af_phonet.c` and removed during module exit.

## Risks and edge cases
Risks include invalid range handling, seqlock misuse, and namespace expectations. The sysctl is registered under `init_net`, so it is global rather than per network namespace. Port range changes can cause allocation failures if all ports in the range are occupied.

## Test signals
Read/write `/proc/sys/net/phonet/local_port_range`, reject reversed ranges and values outside `0..1023`, verify concurrent readers see consistent pairs, and confirm autobind chooses ports within the configured range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/phonet/sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/psample/Kconfig -->
# sources/distributed-fs/ceph-client/net/psample/Kconfig

## Purpose
This Kconfig entry defines `CONFIG_PSAMPLE`, the tristate option for the packet-sampling generic netlink channel.

## Important APIs, types, and functions
There are no C APIs here. The important interface is the `PSAMPLE` menuconfig symbol, prompt, default `n`, help text, and module naming note (`psample`).

## Control flow and state
Kconfig controls whether `net/psample/Makefile` builds `psample.o`. There is no runtime state in this file.

## Dependencies and integration points
The symbol enables the exported `psample_group_*` and `psample_sample_packet()` APIs used by networking components that sample packets and forward metadata to userspace.

## Risks and edge cases
Enabling psample adds a generic netlink family and multicast channels. Configuration regressions would show up as missing symbols for drivers/features that depend on packet sampling or as unwanted attack surface in minimal builds.

## Test signals
Build with `CONFIG_PSAMPLE=n/m/y`, verify module generation and exported symbols, and run generic netlink family discovery when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/psample/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/psample/Makefile -->
# sources/distributed-fs/ceph-client/net/psample/Makefile

## Purpose
The Makefile maps `CONFIG_PSAMPLE` to the `psample.o` object.

## Important APIs, types, and functions
`obj-$(CONFIG_PSAMPLE) += psample.o` is the only build rule. It creates either built-in or module psample support according to the Kconfig symbol.

## Control flow and state
There is no runtime control flow. Build inclusion controls availability of the generic netlink packet sampling channel and exported APIs.

## Dependencies and integration points
The rule is consumed by Kbuild and must stay aligned with the Kconfig symbol and `psample.c` module metadata.

## Risks and edge cases
Risks are limited to build integration: wrong object name or symbol would break module builds or users of exported psample APIs.

## Test signals
Compile with `CONFIG_PSAMPLE=m` and confirm `psample.ko`; compile built-in and disabled variants for link coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/psample/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/psample/psample.c -->
# sources/distributed-fs/ceph-client/net/psample/psample.c

## Purpose
`psample.c` implements a generic netlink channel for packet samples and associated metadata. Kernel producers obtain a sample group, emit truncated packet bytes plus metadata to multicast listeners, and release the group when no longer used.

## Important APIs, types, and functions
Global group state is `psample_groups_list` guarded by `psample_groups_lock`. The generic netlink family is `psample_nl_family`, with config and sample multicast groups. Group APIs are `psample_group_get()`, `psample_group_take()`, and `psample_group_put()`, exported GPL. Dump support uses `psample_nl_cmd_get_group_dumpit()` and `psample_group_nl_fill()`. Notifications use `psample_group_notify()`, `psample_group_create()`, and `psample_group_destroy()`.

The sample emission API is `psample_sample_packet()`, exported GPL. Optional tunnel metadata support is under `CONFIG_INET` through `psample_tunnel_meta_len()`, `psample_ip_tun_to_nlattr()`, and `__psample_ip_tun_to_nlattr()`.

## Control flow and state
A producer calls `psample_group_get(net, group_num)`, which creates a group if needed, increments its refcount, links it globally, and multicasts a new-group notification. `psample_group_put()` decrements the refcount and destroys/notifies/frees via RCU at zero. Group dump iterates groups in the caller's net namespace.

Sampling first checks whether any listeners exist on the sample multicast group for the group namespace. It computes metadata size, includes tunnel metadata if present, clamps packet data length to `trunc_size` and the 64 KiB psample netlink size limit, allocates a generic netlink skb, writes ifindex/sample rate/original size/group/sequence/traffic class/latency/timestamp/protocol/tunnel/user-cookie/probability attributes, copies packet bytes into `PSAMPLE_ATTR_DATA`, and multicasts to listeners.

## State and persistence behavior
Groups are global in-memory objects keyed by `(net, group_num)`, with a simple integer refcount and per-group sequence counter. Sequence increments on each emitted sample. Objects are freed via `kfree_rcu()`. There is no persistent state.

## Dependencies and integration points
The file integrates with generic netlink, net namespaces, multicast listener checks, skb data copying, IP tunnel metadata (`dst_metadata`/`ip_tunnel_info`), and external packet sampling producers. The sample multicast group requires `CAP_NET_ADMIN` for listeners via `GENL_MCAST_CAP_NET_ADMIN`.

## Risks and edge cases
Risks include netlink size calculation underflow when metadata approaches `PSAMPLE_MAX_PACKET_SIZE`, group refcount misuse by producers, spinlock-held notification allocation constraints, tunnel metadata length mismatches, and sequence races if samples are emitted concurrently for the same group without locking around `group->seq++`. The code intentionally returns silently when no listeners exist to keep producers cheap.

## Test signals
Use generic netlink clients to dump groups, subscribe to config/sample multicast groups, validate group create/destroy notifications, emit samples with and without listeners, test truncation boundaries, user cookies, probability flag, tunnel metadata for IPv4/IPv6/Geneve/ERSPAN, namespace filtering, and concurrent producers hitting the same group.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/psample/psample.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/psp/Kconfig -->
# sources/distributed-fs/ceph-client/net/psp/Kconfig

## Purpose
This Kconfig entry defines `CONFIG_INET_PSP`, the bool option for kernel PSP Security Protocol support.

## Important APIs, types, and functions
There are no C APIs here. The important configuration interface is `INET_PSP`, which depends on `INET` and selects `SKB_DECRYPTED`, `SKB_EXTENSIONS`, and `SOCK_VALIDATE_XMIT`.

## Control flow and state
When enabled, Kbuild includes the PSP core object aggregate from the Makefile. The selected symbols enable skb extension and transmit-validation infrastructure required by PSP.

## Dependencies and integration points
The option enables networking core PSP support, generic netlink controls, socket association logic, and driver-facing PSP device registration APIs. Help text links to the PSP architecture specification.

## Risks and edge cases
Because PSP changes TCP packet encapsulation/decapsulation behavior and exposes netlink controls, enabling it changes networking security surface. Missing selects would cause build or runtime failures around skb metadata and decrypted-state handling.

## Test signals
Build with `INET_PSP=y` and disabled. Verify selected dependencies, generic netlink family presence, and driver-facing symbol availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/psp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/psp/Makefile -->
# sources/distributed-fs/ceph-client/net/psp/Makefile

## Purpose
The Makefile maps `CONFIG_INET_PSP` to the PSP object aggregate.

## Important APIs, types, and functions
`obj-$(CONFIG_INET_PSP) += psp.o` enables PSP, and `psp-y := psp_main.o psp_nl.o psp_sock.o psp-nl-gen.o` links the core, netlink implementation, socket association implementation, and generated netlink tables.

## Control flow and state
There is no runtime flow. Object membership determines the built-in PSP subsystem composition; PSP is a bool option, not a module in this Makefile.

## Dependencies and integration points
The Makefile must stay aligned with `Kconfig`, `psp_main.c` initialization, generated netlink code, and non-listed implementation files (`psp_nl.c`, `psp_sock.c`) that provide declarations referenced by headers and generated ops.

## Risks and edge cases
Incorrect object ordering or missing objects would produce unresolved symbols for generated netlink callbacks, socket association helpers, or device registration APIs.

## Test signals
Build `CONFIG_INET_PSP=y`, confirm `psp_main.o`, `psp_nl.o`, `psp_sock.o`, and `psp-nl-gen.o` are linked, and check that disabling the option removes PSP symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/psp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/psp/psp-nl-gen.c -->
# sources/distributed-fs/ceph-client/net/psp/psp-nl-gen.c

## Purpose
`psp-nl-gen.c` is generated YNL kernel code from `Documentation/netlink/specs/psp.yaml`. It defines PSP generic netlink policies, split operation tables, multicast groups, and the `psp_nl_family` object registered by `psp_main.c`.

## Important APIs, types, and functions
The file exports `psp_keys_nl_policy` and defines per-command policies for device get/set, key rotation, RX association, TX association, and stats get. `psp_nl_ops[]` maps PSP commands to generated policy metadata plus implementation callbacks declared in `psp-nl-gen.h`, such as `psp_device_get_locked()`, `psp_assoc_device_get_locked()`, `psp_device_unlock()`, `psp_nl_dev_get_doit()`, `psp_nl_tx_assoc_doit()`, and dump handlers.

`psp_nl_mcgrps[]` defines `mgmt` and `use` multicast groups. `psp_nl_family` sets family name/version, `netnsok`, `parallel_ops`, module owner, split ops, and multicast groups.

## Control flow and state
Runtime control is generic-netlink driven. For each command, the family applies the generated attribute policy, optional pre-doit lock/acquire callback, implementation callback, and post-doit unlock callback. Dump operations skip pre/post for the entries that only provide dumpit. No mutable state is stored in this file beyond generic netlink family registration state owned by the netlink core.

## Dependencies and integration points
This file depends on UAPI definitions in `<uapi/linux/psp.h>` and implementation callbacks in `psp_nl.c` plus locking helpers declared in the generated header. It is registered by `genl_register_family(&psp_nl_family)` in `psp_main.c`.

## Risks and edge cases
Generated files should not be hand-edited; drift from the YAML spec can break user/kernel ABI. Policy bounds are security critical: device ids require minimum 1, enabled version mask is limited to `0xf`, association version is max 3, and TX keys are nested under `psp_keys_nl_policy`. `parallel_ops = true` makes callback locking discipline important.

## Test signals
Use YNL/generated userspace tests to validate every command policy, missing/invalid attributes, dump behavior, multicast group discovery, parallel command locking, and regeneration from `psp.yaml` producing no unexpected diff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/psp/psp-nl-gen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/psp/psp-nl-gen.h -->
# sources/distributed-fs/ceph-client/net/psp/psp-nl-gen.h

## Purpose
`psp-nl-gen.h` is the generated header for the PSP generic netlink family. It declares policies, operation callback prototypes, multicast group indexes, and the external family object.

## Important APIs, types, and functions
The header declares `psp_keys_nl_policy`, pre/post callbacks `psp_device_get_locked()`, `psp_assoc_device_get_locked()`, and `psp_device_unlock()`, command handlers for device get/set, key rotate, RX/TX association, and stats get/dump, plus `enum { PSP_NLGRP_MGMT, PSP_NLGRP_USE }` and `extern struct genl_family psp_nl_family`.

## Control flow and state
There is no runtime control flow. The declarations connect generated op-table entries in `psp-nl-gen.c` with implementation functions in `psp_nl.c` and registration in `psp_main.c`.

## Dependencies and integration points
The header includes generic netlink and UAPI PSP definitions. It is included by `psp_main.c` and implementation files that need the family or policy declarations.

## Risks and edge cases
Like the generated C file, it should not be edited directly. Prototype drift from implementations or YAML regeneration can break builds or ABI behavior. Multicast group enum ordering must match the generated family group array.

## Test signals
Build coverage catches prototype mismatches. Regeneration tests should compare generated output. Runtime netlink tests validate that callback implementations line up with declared command handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/psp/psp-nl-gen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/psp/psp.h -->
# sources/distributed-fs/ceph-client/net/psp/psp.h

## Purpose
`psp.h` is the private PSP subsystem header shared by the core, netlink, and socket association implementation. It declares global device registry state, core helper prototypes, association helpers, and inline PSP device reference helpers.

## Important APIs, types, and functions
The header declares `extern struct xarray psp_devs` and `extern struct mutex psp_devs_lock`. Core helpers include `psp_dev_free()` and `psp_dev_check_access()`. Netlink notification is `psp_nl_notify_dev()`. Association helpers include `psp_assoc_create()`, `psp_dev_get_for_sock()`, `psp_dev_tx_key_del()`, `psp_sock_assoc_set_rx()`, `psp_sock_assoc_set_tx()`, and `psp_assocs_key_rotated()`.

Inline helpers `psp_dev_get()`, `psp_dev_tryget()`, `psp_dev_put()`, and `psp_dev_is_registered()` implement refcount handling and registered-state checks. `psp_dev_is_registered()` asserts the instance lock is held and treats non-NULL `ops` as registered.

## Control flow and state
The header itself has no complex flow. Its inline `psp_dev_put()` calls `psp_dev_free()` on the final reference, tying refcount lifetime to xarray removal and RCU freeing in `psp_main.c`.

## Dependencies and integration points
It includes `net/psp.h` for public PSP structs, networking namespace/socket headers, list/mutex/lockdep primitives, and is included by PSP implementation files. It defines the lock ordering convention used in `psp_main.c`: global `psp_devs_lock` before per-device `psd->lock`.

## Risks and edge cases
Risks center on lifetime and locking. Callers must not call `psp_dev_is_registered()` without holding `psd->lock`, must balance successful gets with puts, and must respect xarray plus RCU lifetime rules. Changing `psp_dev_put()` semantics affects every PSP device/association path.

## Test signals
Build coverage plus lockdep-enabled tests for netlink device lookup, driver unregister while netlink/socket associations hold references, key deletion paths, and final RCU freeing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/psp/psp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/psp/psp_main.c -->
# sources/distributed-fs/ceph-client/net/psp/psp_main.c

## Purpose
`psp_main.c` implements the core PSP device registry, driver-facing device create/unregister APIs, PSP key size helper, packet encapsulation, packet receive decapsulation, and subsystem initialization. PSP here is UDP-encapsulated TCP protection metadata with driver-managed crypto/key operations.

## Important APIs, types, and functions
Global registry state is `DEFINE_XARRAY_ALLOC1(psp_devs)` and `psp_devs_lock`. Driver APIs include `psp_dev_create()`, `psp_dev_unregister()`, and the internal finalizer `psp_dev_free()`. Visibility checking is `psp_dev_check_access()`. `psp_key_size()` maps PSP versions to AES-GCM/GMAC key sizes.

Packet transmit helpers are `psp_dev_encapsulate()` and private `psp_write_headers()`. Receive helper is `psp_dev_rcv()`. Initialization is `psp_init()`, which initializes the global mutex and registers the generated generic netlink family.

## Control flow and state
`psp_dev_create()` validates mandatory driver capability/operation callbacks, allocates and initializes `struct psp_dev`, assigns a cyclic 16-bit id in `psp_devs`, locks the instance, notifies netlink listeners of device add, publishes `netdev->psp_dev` with RCU, and returns with a refcount of one. `psp_dev_unregister()` takes global then instance locks, notifies delete, stores NULL in the xarray to prevent id reuse while references remain, moves active/previous associations to stale, deletes TX keys for stale associations, clears the netdev RCU pointer, nulls ops/private data to mark unregistered, unlocks, and drops the device reference. `psp_dev_free()` erases the id and frees via RCU after the final put.

`psp_dev_encapsulate()` grows headroom by `PSP_ENCAP_HLEN`, moves the Ethernet/IP header earlier, changes IPv4/IPv6 next protocol to UDP, updates lengths and IPv4 checksum, marks inner TCP metadata, sets encapsulation, and writes UDP/PSP headers. `psp_write_headers()` chooses a UDP source port from the socket hash and local port range when a socket is present, otherwise uses `udp_flow_src_port()`, then writes destination port, UDP length, and fixed PSP header fields.

`psp_dev_rcv()` validates Ethernet/VLAN plus IPv4/IPv6 plus UDP PSP default port, validates linear header availability, computes full PSP header length from `hdrlen`, adds `SKB_EXT_PSP`, records SPI/dev id/generation/version, updates outer IP next header and length to the protected inner protocol, moves L2/L3 headers to remove UDP+PSP headers, pulls the skb, and optionally strips the trailing ICV.

## State and persistence behavior
Device registry state is in-memory, global, xarray-backed, and RCU/refcount protected. PSP device registered/unregistered state is represented by `psd->ops` under `psd->lock` and `netdev->psp_dev` RCU pointer. Associations are list-based under the device lock. Packet metadata persists only in skb extensions for received packets.

## Dependencies and integration points
The file integrates with netdevice `psp_dev` pointers, generic netlink family from `psp-nl-gen.c`, PSP UAPI/public structs from `net/psp.h`, UDP/IP helpers, socket port range/hash logic, skb extensions, xarray, RCU, and driver callback interfaces for configuration, key rotation, SPI allocation, TX key add/delete, and stats.

## Risks and edge cases
Key risks are device lifetime and id reuse during unregister, lock ordering, encapsulation headroom/header movement bugs, IPv4/IPv6 length/checksum correctness, unsupported protocols, malformed PSP header lengths, CHECKSUM_COMPLETE limitations, and `pskb_trim()` failure handling on ICV strip. Receive accepts only already-authenticated packets by contract, so callers must enforce authentication before `psp_dev_rcv()`.

## Test signals
Test driver registration validation, cyclic id allocation, netlink add/delete notifications, unregister with active associations, refcount/RCU lifetime under concurrent netlink operations, `psp_key_size()` for all versions, IPv4 and IPv6 encapsulation byte layout, UDP source port stability per TCP flow, receive decapsulation with VLAN, optional PSP header length, ICV stripping, malformed protocol/port/header cases, and skb extension contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/psp/psp_main.c -->
