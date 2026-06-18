# subset-b-006293 Research

Grouped code research for `sources/distributed-fs/ceph-client/net/vmw_vsock`. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/Kconfig -->
# sources/distributed-fs/ceph-client/net/vmw_vsock/Kconfig

## Purpose
`Kconfig` defines the build-time feature switches for Linux virtual sockets in this source tree. It exposes the common `VSOCKETS` address-family core, optional sock_diag monitoring, loopback transport, VMware VMCI transport, virtio transport and its shared implementation, and Hyper-V transport.

## Important APIs, Types, And Functions
This file contributes Kconfig symbols rather than C APIs. `VSOCKETS` builds the `vsock` core module. `VSOCKETS_DIAG` enables the PF_VSOCK monitoring interface used by `ss`. `VSOCKETS_LOOPBACK` and `VIRTIO_VSOCKETS` both select `VIRTIO_VSOCKETS_COMMON`, causing the shared virtio protocol implementation to be built. `VMWARE_VMCI_VSOCKETS` depends on `VMWARE_VMCI`, and `HYPERV_VSOCKETS` depends on `HYPERV_VMBUS`.

## Control Flow
Selection starts with `VSOCKETS`; transport entries are only meaningful when the core address family is enabled. Transport-specific symbols compile independent provider modules that later call `vsock_core_register()` from their module init paths. The common virtio option is hidden and selected by concrete users so shared helpers are not exposed as a manual user-facing transport.

## State And Persistence
The persistent state is kernel configuration state. Built-in versus module choices determine whether transports are always present or dynamically loadable. The default-enabled diagnostic and loopback choices affect what userspace observability and local communication features are present by default when VSOCKETS is selected.

## Dependencies And Integration Points
The symbols integrate with `Makefile` object selection in the same directory and with external subsystems: VMware VMCI, virtio, and Hyper-V VMBus. The module names in help text correspond to the objects built by `Makefile`.

## Risks And Edge Cases
Misconfigured dependencies can build a transport without its bus or hypervisor substrate, or build the core without any usable transport. Since only one transport can occupy each core feature slot at runtime, enabling multiple host/guest transports is safe at build time but may produce `-EBUSY` registration failures depending on runtime platform.

## Test Signals
Useful signals include allmodconfig/allnoconfig builds, module load tests for `vsock`, `vsock_diag`, `vmw_vsock_virtio_transport`, `vmw_vsock_vmci_transport`, `hv_sock`, and `vsock_loopback`, plus `ss -A vsock` behavior when `VSOCKETS_DIAG` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/Makefile -->
# sources/distributed-fs/ceph-client/net/vmw_vsock/Makefile

## Purpose
`Makefile` maps the vmw_vsock Kconfig symbols to kernel objects and defines which source files compose each loadable module. It is the build manifest for the AF_VSOCK core, diagnostics, VMCI, virtio, shared virtio code, Hyper-V, and loopback modules.

## Important APIs, Types, And Functions
The main build products are `vsock.o`, `vsock_diag.o`, `vmw_vsock_vmci_transport.o`, `vmw_vsock_virtio_transport.o`, `vmw_vsock_virtio_transport_common.o`, `hv_sock.o`, and `vsock_loopback.o`. The `vsock-y` composite includes `af_vsock.o`, `af_vsock_tap.o`, and `vsock_addr.o`, with `vsock_bpf.o` added when `CONFIG_BPF_SYSCALL` is set. VMCI includes `vmci_transport.o`, `vmci_transport_notify.o`, and `vmci_transport_notify_qstate.o`.

## Control Flow
Kbuild includes each object only when its `CONFIG_` symbol resolves to built-in or module. Composite targets gather several `.o` files into one module, so the AF_VSOCK core always carries address utilities and tap support, while optional BPF hooks are compiled into the core only on BPF-capable builds.

## State And Persistence
There is no runtime state here. The persistent effect is build composition: for example, virtio protocol state-machine code is separated into `vmw_vsock_virtio_transport_common.o`, allowing both real virtio and loopback/vhost-style users to share the same packet and credit logic.

## Dependencies And Integration Points
This file integrates directly with `Kconfig` symbols and with exported symbols in `af_vsock.c`, `af_vsock_tap.c`, and `virtio_transport_common.c`. It also defines module naming that userspace and modprobe configuration depend on.

## Risks And Edge Cases
The highest risk is silently omitting a companion object from a composite target. For VMCI, missing either notify implementation would break negotiated notification callbacks; for the core, missing `vsock_addr.o` or `af_vsock_tap.o` would create link failures or observability regressions.

## Test Signals
Build tests should cover built-in and modular variants for every symbol combination, especially `CONFIG_BPF_SYSCALL`, `VSOCKETS_LOOPBACK`, `VIRTIO_VSOCKETS_COMMON`, and VMCI. `modinfo` and module insertion can confirm the expected composite modules are emitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/af_vsock.c -->
# sources/distributed-fs/ceph-client/net/vmw_vsock/af_vsock.c

## Purpose
`af_vsock.c` is the core `AF_VSOCK` socket-family implementation. It registers the protocol family and `/dev/vsock`, owns generic socket lifecycle and operations for datagram, stream, and seqpacket sockets, maintains bound and connected socket lookup tables, selects a registered transport for each socket, implements accept/connect/shutdown/poll/send/receive/ioctl/socket-option behavior, and exposes per-network-namespace vsock mode sysctls.

## Important APIs, Types, And Functions
Persistent objects include `struct proto vsock_proto`, `vsock_bind_table`, `vsock_connected_table`, and the registered transport pointers `transport_h2g`, `transport_g2h`, `transport_dgram`, and `transport_local`. Exported helpers include `vsock_assign_transport()`, `vsock_find_bound_socket_net()`, `vsock_find_connected_socket_net()`, `vsock_create_connected()`, `vsock_insert_connected()`, `vsock_remove_sock()`, `vsock_stream_has_data()`, `vsock_stream_has_space()`, `vsock_linger()`, `vsock_core_register()`, and `vsock_core_unregister()`.

## Control Flow
Module init initializes lookup tables, registers `/dev/vsock`, registers the socket protocol and family, installs pernet sysctls, and prepares optional BPF protocol hooks. Socket creation chooses proto ops by type, allocates `struct vsock_sock`, initializes addresses, delayed work, credentials, buffer sizes, and inserts the socket into the unbound list; datagram sockets immediately receive a datagram transport.

`connect()` validates state, stores the remote address, assigns a transport based on CID and flags, autobinds a local port, sends the transport request, and either waits for `TCP_ESTABLISHED` or returns `-EINPROGRESS` with timeout work scheduled. Listen sockets accept transport-created child sockets from the accept queue. Send and receive paths are generic loops around transport callbacks for enqueue/dequeue, notification hooks, rcvlowat handling, zero-copy checks, and stream versus seqpacket semantics.

## State And Persistence
Core state is in `struct vsock_sock`: local/remote addresses, selected transport, pending/accept lists, shutdown flags, connect and cleanup delayed works, owner credentials, trust/cache state, buffer bounds, and transport-private `trans`. The global tables persist bound and connected sockets with reference counts taken for each list entry. Network namespaces persist `mode`, `child_ns_mode`, write-once child mode lock state, and `g2h_fallback` through `net->vsock`.

## Dependencies And Integration Points
The core depends on the Linux socket layer, skbuff queues, workqueues, credentials/capabilities, sysctl, misc devices, network namespaces, BPF sockmap hooks, and `uapi/linux/vm_sockets.h`. It is the integration point for VMCI, virtio, Hyper-V, loopback, vhost, sock_diag, BPF, and vsockmon taps via exported helpers and transport callbacks.

## Risks And Edge Cases
Critical risks are socket lifetime and lock ordering across listener/pending/accepted sockets, global table references, delayed connect and pending cleanup work, and transport module references. Transport reassignment during connect must release/destruct the previous transport while preserving bindings. Namespace mode checks protect local-mode containment; missing namespace-aware lookup in a transport forces global semantics. Send/receive loops must handle shutdown races, signal/timeout interruption, partial seqpacket sends, and zero-copy support negotiation.

## Test Signals
Useful coverage includes stream, seqpacket, and dgram socket creation; bind to explicit and auto ports; reserved-port permission checks; blocking and nonblocking connect timeout/cancel; listen/accept backlog and pending cleanup; poll readiness; `SO_VM_SOCKETS_*` and `SO_ZEROCOPY`; `SIOCINQ/SIOCOUTQ`; namespace `ns_mode` and `child_ns_mode`; transport register/unregister conflicts; module unload with open sockets; BPF sockmap redirection; and lockdep/KASAN/KCSAN around close and workqueue paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/af_vsock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/af_vsock_tap.c -->
# sources/distributed-fs/ceph-client/net/vmw_vsock/af_vsock_tap.c

## Purpose
`af_vsock_tap.c` implements packet tap support for AF_VSOCK monitoring devices. It lets vsock monitor drivers register `ARPHRD_VSOCKMON` net devices and receive cloned skbuffs for observed vsock traffic.

## Important APIs, Types, And Functions
The exported APIs are `vsock_add_tap()`, `vsock_remove_tap()`, and `vsock_deliver_tap()`. Registered taps are `struct vsock_tap` entries in the RCU-protected `vsock_tap_all` list, protected for mutation by `vsock_tap_lock`.

## Control Flow
A monitor calls `vsock_add_tap()` with a tap whose device type must be `ARPHRD_VSOCKMON`; the module reference is incremented and the tap is inserted with `list_add_rcu()`. Removal searches the list, deletes the entry with `list_del_rcu()`, waits for `synchronize_net()`, and drops the module reference. Transports call `vsock_deliver_tap()` with a callback that builds a monitor-format skb only when at least one tap exists, then each tap receives a cloned skb via `dev_queue_xmit()`.

## State And Persistence
Runtime state is the global tap list and module references held while a tap is registered. The delivered monitor packet is transient; the original transport packet remains owned by the caller.

## Dependencies And Integration Points
This file depends on net devices, RCU, skbuff cloning, and module reference counting. It integrates with `virtio_transport_common.c` through `virtio_transport_deliver_tap_pkt()`, which builds `vsockmon` headers before calling into the generic tap fanout.

## Risks And Edge Cases
Tap delivery runs under RCU and may be in atomic contexts, so allocation uses `GFP_ATOMIC` and failures silently skip clones. Incorrect device type registration is rejected. A delivery error breaks fanout early, so one failing tap can prevent later taps from observing a packet.

## Test Signals
Test signals include loading a vsockmon device, registering and unregistering taps under traffic, verifying cloned packets with tcpdump-like tooling, module unload after tap removal, and stress testing allocation failure and concurrent tap removal with KASAN/RCU diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/af_vsock_tap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/diag.c -->
# sources/distributed-fs/ceph-client/net/vmw_vsock/diag.c

## Purpose
`diag.c` implements the `sock_diag` interface for AF_VSOCK. It allows userspace tools such as `ss -A vsock` to dump open vsock sockets, their state, addresses, shutdown state, inode, and socket cookie.

## Important APIs, Types, And Functions
The main functions are `sk_diag_fill()`, `vsock_diag_dump()`, and `vsock_diag_handler_dump()`. The registered handler is `vsock_diag_handler` for family `AF_VSOCK`. It emits `struct vsock_diag_msg` replies in `SOCK_DIAG_BY_FAMILY` netlink messages and consumes `struct vsock_diag_req`.

## Control Flow
Initialization registers the sock_diag handler. A dump request with `NLM_F_DUMP` starts a netlink dump using `vsock_diag_dump()`. The dump walks first the bind table, then the connected table, using `cb->args[]` to persist table, bucket, and index across multipart netlink calls. It filters sockets by network namespace and requested state mask, skips connected-table sockets already seen in the bound table, and fills each matching record without taking `sk_lock` because `vsock_table_lock` pins list membership and lock ordering forbids nesting in the opposite direction.

## State And Persistence
The module owns no socket state. It reads the global vsock tables under `vsock_table_lock`. Netlink callback state persists only across a single multipart dump in `cb->args`.

## Dependencies And Integration Points
The file integrates with `af_vsock.c` exported tables and `vsock_table_lock`, the sock_diag netlink subsystem, network namespaces, and `uapi/linux/vm_sockets_diag.h`. It is enabled by `CONFIG_VSOCKETS_DIAG` and built as `vsock_diag`.

## Risks And Edge Cases
The main risks are duplicate reporting between bound and connected tables and lock-order violations. The implementation avoids duplicates for sockets present in both tables and intentionally reads fields locklessly while the global table lock keeps the socket alive. Very large socket sets depend on correct `cb->args` resume bookkeeping.

## Test Signals
Useful tests include `ss -A vsock` across listening, connecting, connected, and closed states; namespace filtering; state-mask filtering; multipart dumps with many sockets; module load/unload; and lockdep validation while sockets are concurrently connecting and closing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/hyperv_transport.c -->
# sources/distributed-fs/ceph-client/net/vmw_vsock/hyperv_transport.c

## Purpose
`hyperv_transport.c` implements the Hyper-V guest-to-host AF_VSOCK transport (`hv_sock`). It maps Linux vsock stream sockets to Hyper-V Sockets over VMBus pipe channels, using a fixed service GUID template where the vsock port occupies the first four bytes.

## Important APIs, Types, And Functions
Key state is `struct hvsock`, stored in `vsk->trans`, with service GUIDs, a `struct vmbus_channel`, current receive descriptor, pending payload offsets, and FIN state. Important functions include `hvs_open_connection()`, `hvs_close_connection()`, `hvs_connect()`, `hvs_shutdown()`, `hvs_release()`, `hvs_stream_enqueue()`, `hvs_stream_dequeue()`, `hvs_stream_has_data()`, `hvs_stream_has_space()`, and the `hvs_transport` callback table.

## Control Flow
Module init verifies VMBus protocol support, registers an `hv_driver`, then registers the transport as `VSOCK_TRANSPORT_F_G2H`. On an offered VMBus channel, `hvs_open_connection()` validates the service GUID, locates either a listening socket for host-initiated connects or a `TCP_SYN_SENT` client socket for guest-initiated connects, opens the channel with ring sizes derived from socket buffers, stores the socket as per-channel state, and moves the socket to `TCP_ESTABLISHED`. Host-initiated connections create a child vsock, assign the Hyper-V transport, insert it in the connected table, and enqueue it for accept.

Transmit copies user data into a page-sized `hvs_send_buf` and sends VMBus in-band packets with a small `vmpipe_proto_header`. Receive uses VMBus packet iterators and copies payload directly to the user message. A zero-length packet is FIN and sets peer shutdown. Close sends FIN, waits up to `HVS_CLOSE_TIMEOUT`, then removes the socket if the peer does not complete shutdown.

## State And Persistence
Per-socket state persists in `struct hvsock` and VMBus channel state. The transport does not support datagrams, seqpacket, MSG_PEEK, or local namespace mode. Ring buffer sizing is persistent for the channel lifetime and capped for host compatibility.

## Dependencies And Integration Points
The file depends on Hyper-V VMBus APIs, `hvhdk.h`, socket core callbacks, and the AF_VSOCK transport interface. It integrates with AF_VSOCK through `vsock_core_register()`, socket lookup helpers, connected table insertion, accept queue handling, and stream notification callbacks.

## Risks And Edge Cases
Risks include VMBus channel lifetime versus socket lifetime, host rescind callbacks racing with close, ring-buffer full handling that must reserve space for FIN, malformed packet length validation, and compatibility with older Windows hosts that require small ring buffers. Since `get_local_cid()` returns `VMADDR_CID_ANY`, binding and addressing semantics are narrower than VMCI or virtio.

## Test Signals
Test guest-to-host and host-to-guest connect/listen/accept on Hyper-V, FIN and rescind handling, send buffer pressure, receive of zero-length FIN, invalid service GUID rejection, hibernation suspend/resume dummies, old and new VMBus protocol versions, and module unload with active channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/hyperv_transport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/virtio_transport.c -->
# sources/distributed-fs/ceph-client/net/vmw_vsock/virtio_transport.c

## Purpose
`virtio_transport.c` is the virtio-vsock device driver and concrete guest-to-host transport. It owns virtqueue setup, transmit and receive workqueues, event handling, guest CID discovery, zero-copy capability checks, and registration of the virtio transport callbacks with the AF_VSOCK core.

## Important APIs, Types, And Functions
The central device object is `struct virtio_vsock`, containing RX/TX/event virtqueues, locks, work items, queued reply accounting, guest CID, seqpacket feature state, and scatterlist storage for TX. Important functions include `virtio_transport_send_pkt()`, `virtio_transport_send_pkt_work()`, `virtio_transport_rx_work()`, `virtio_vsock_vqs_init()`, `virtio_vsock_vqs_start()`, `virtio_vsock_vqs_del()`, `virtio_vsock_probe()`, `virtio_vsock_remove()`, and PM freeze/restore paths.

## Control Flow
Module init creates a percpu workqueue, registers the transport as `VSOCK_TRANSPORT_F_G2H`, and registers a virtio driver for `VIRTIO_ID_VSOCK`. Probe enforces one device per guest, allocates `struct virtio_vsock`, initializes queues and workers, discovers features such as `VIRTIO_VSOCK_F_SEQPACKET`, initializes virtqueues, assigns the RCU global `the_virtio_vsock`, fills RX/event queues, and enables TX processing.

Sends use a fast path that tries to lock the TX virtqueue and enqueue immediately; otherwise packets go to `send_pkt_queue` and `send_pkt_work`. TX completion consumes skbs and restarts queued sends. RX work drains RX buffers, validates packet and payload lengths, taps packets for monitoring, and calls `virtio_transport_recv_pkt()` in global namespace mode. Event work handles transport reset by refreshing guest CID and resetting connected sockets.

## State And Persistence
Global state is the RCU pointer `the_virtio_vsock` protected by `the_virtio_vsock_mutex`. Device state persists until removal or PM freeze, including queued replies used to throttle RX so reply packets do not exhaust the TX ring. Socket-specific state is mostly in `virtio_transport_common.c`.

## Dependencies And Integration Points
The driver depends on virtio core APIs, virtqueue callbacks, DMA-safe event buffers, workqueues, RCU, AF_VSOCK core registration, and shared virtio transport common helpers. It integrates with vsock taps and with connected-socket reset iteration on transport reset or device removal.

## Risks And Edge Cases
Important risks include global device replacement races, workqueue callbacks after virtqueue deletion, RX starvation when queued replies fill the ring, packet length validation before exposing payload, zero-copy packets larger than virtqueue capacity, and freeze/restore ordering. Virtio currently forces global namespace mode on receive because this transport path does not provide per-net context.

## Test Signals
Use virtio-vsock connect/send/recv tests, seqpacket feature negotiation, guest CID reset events, suspend/resume, hot remove, module unload, vsockmon packet capture, zero-copy send with large fragmented iovecs, queue pressure tests that force slow-path send, and lockdep/KASAN around device removal with active sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/virtio_transport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/virtio_transport_common.c -->
# sources/distributed-fs/ceph-client/net/vmw_vsock/virtio_transport_common.c

## Purpose
`virtio_transport_common.c` implements the shared virtio/vhost/loopback vsock packet protocol. It builds and parses virtio-vsock headers, manages stream and seqpacket receive queues, implements credit-based flow control, handles connection state packets, shutdown/reset/close timeouts, packet tapping, zerocopy skb construction, and exports callback implementations used by concrete virtio-style transports.

## Important APIs, Types, And Functions
Key APIs include `virtio_transport_do_socket_init()`, `virtio_transport_connect()`, `virtio_transport_shutdown()`, `virtio_transport_stream_enqueue()`, `virtio_transport_seqpacket_enqueue()`, `virtio_transport_stream_dequeue()`, `virtio_transport_seqpacket_dequeue()`, `virtio_transport_recv_pkt()`, `virtio_transport_release()`, `virtio_transport_destruct()`, `virtio_transport_read_skb()`, and credit helpers `virtio_transport_get_credit()`, `virtio_transport_put_credit()`, and `virtio_transport_inc_tx_pkt()`.

## Control Flow
Sending starts in `virtio_transport_send_pkt_info()`: resolve local and remote CIDs/ports, reserve credit from the per-socket TX window, choose zerocopy when allowed, split payload into `VIRTIO_VSOCK_MAX_PKT_BUF_SIZE` packets, initialize headers with current buffer allocation and forward count, and hand packets to the concrete transport's `send_pkt()`. Receive enters `virtio_transport_recv_pkt()`, validates type, locates a connected or bound socket with optional namespace context, updates peer credit state, and dispatches by socket state. Listening sockets create connected children and respond; connecting sockets accept `OP_RESPONSE` or reset; established sockets enqueue RW payloads, process credit updates/requests, or process shutdown/reset.

## State And Persistence
Per-socket state is `struct virtio_vsock_sock`: TX counters `tx_cnt`, `peer_fwd_cnt`, `peer_buf_alloc`, `bytes_unsent`, and RX counters `fwd_cnt`, `last_fwd_cnt`, `rx_bytes`, `buf_alloc`, `buf_used`, `rx_queue`, and `msg_count`. Close uses `vsk->close_work` and `close_work_scheduled`. Receive queues persist skbs until userspace dequeues or `read_skb()` consumes them.

## Dependencies And Integration Points
The file depends on AF_VSOCK core callbacks, `linux/virtio_vsock.h`, skbuff APIs, zero-copy message infrastructure, tracepoints, vsockmon tap delivery, and concrete `struct virtio_transport` providers such as virtio, vhost, and loopback. It exports many symbols consumed by those providers.

## Risks And Edge Cases
Credit accounting is the highest-risk area: reserved credits must be returned on partial send, peer buffer shrink must not underflow, RX queue accounting must match skb lifetimes, and credit updates must avoid stalls without spamming control packets. Connection handling must avoid replying to RST with RST, must remove sockets after full peer shutdown so port reuse works, and must handle sockets closed or reassigned before `lock_sock()`. Seqpacket message boundaries rely on `SEQ_EOM` and `msg_count`; small-packet coalescing must not cross message boundaries.

## Test Signals
Important tests include stream and seqpacket transfers with fragmentation, MSG_PEEK, MSG_TRUNC, MSG_EOR, `SO_RCVLOWAT`, large sends beyond peer credit, buffer-size updates, zero-copy completion and fallback copy, malformed type/op/length packets, reset-no-socket paths, close timeout, simultaneous shutdown, `read_skb()` consumers, vsockmon output, and KCSAN/lockdep around RX/TX locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/virtio_transport_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/vmci_transport.c -->
# sources/distributed-fs/ceph-client/net/vmw_vsock/vmci_transport.c

## Purpose
`vmci_transport.c` implements the VMware VMCI transport for AF_VSOCK. It supports VMCI datagrams and stream sockets, performs stream connection negotiation over VMCI datagram control packets, establishes VMCI queue pairs for data transfer, handles peer detach/resume events, enforces VMCI privilege restrictions, and registers VMCI as dgram plus host-to-guest or guest-to-host transport depending on platform callbacks.

## Important APIs, Types, And Functions
Important internal flows are `vmci_transport_recv_stream_cb()`, `vmci_transport_recv_pkt_work()`, `vmci_transport_recv_listen()`, `vmci_transport_recv_connecting_server()`, `vmci_transport_recv_connecting_client()`, `vmci_transport_recv_connecting_client_negotiate()`, and `vmci_transport_recv_connected()`. Data operations include `vmci_transport_dgram_bind()`, `vmci_transport_dgram_enqueue()`, `vmci_transport_dgram_dequeue()`, `vmci_transport_stream_enqueue()`, `vmci_transport_stream_dequeue()`, `vmci_transport_stream_has_data()`, and `vmci_transport_stream_has_space()`.

## Control Flow
Init creates a VMCI datagram handle for stream control packets, subscribes to queue-pair resumed events, registers the dgram transport feature, and registers a VMCI callback that later adds H2G or G2H features. Stream connect sends a `REQUEST2` with supported notify protocols or an old `REQUEST` under module override. A listener receiving a request creates a pending child, negotiates queue-pair size and notification protocol, sends `NEGOTIATE` or `NEGOTIATE2`, adds the child to the pending list, and schedules pending cleanup. The client receives negotiation, subscribes to detach events, allocates a queue pair, sends an `OFFER`, then waits for `ATTACH`. The server attaches to the offered queue pair, inserts the child in the connected table, sends `ATTACH`, and moves the child to the accept queue.

## State And Persistence
Per-socket VMCI state is `struct vmci_transport`: datagram handle, queue-pair handle and pointer, produce/consume sizes, detach subscription id, notification state, cleanup list node, socket pointer, and lock. Global state includes the stream control handle, queue-pair resumed subscription id, protocol override parameter, cleanup work/list, and the singleton `vmci_transport` callback table.

## Dependencies And Integration Points
The file depends on VMCI datagram, queue-pair, event, context, and privilege APIs; AF_VSOCK core lookup and queue helpers; and `vmci_transport_notify` implementations selected during protocol negotiation. It integrates with restricted VM privilege checks via socket owner credentials and with the AF_VSOCK core as dgram, H2G, or G2H transport.

## Risks And Edge Cases
The handshake is stateful and multi-packet, so failures must send RST and unwind pending refs, queue-pair handles, and detach subscriptions. Bottom-half VMCI callbacks fast-path notifications but defer most processing to workqueues; socket references and locks must be balanced across that boundary. Peer detach may arrive in different contexts and must avoid use-after-free with `trans->lock` and `trans->sk = NULL`. Old/new protocol fallback and the `PROTOCOL_OVERRIDE` module parameter can hide incompatibilities.

## Test Signals
Test VMCI stream connect/listen/accept, datagram bind/send/recv, old and new notification protocol negotiation, invalid packet type and size handling, restricted-context permission checks, queue-pair detach and resume events, pending connection cleanup, RST during connect, host and guest transport registration, module unload after sockets close, and lockdep/KASAN around detach callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/vmci_transport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/vmci_transport.h -->
# sources/distributed-fs/ceph-client/net/vmw_vsock/vmci_transport.h

## Purpose
`vmci_transport.h` defines the VMCI transport private protocol contract shared by `vmci_transport.c` and VMCI notification implementations. It describes control packet types, packet layouts, notification state structures, per-socket VMCI transport state, and exported notification-send helpers.

## Important APIs, Types, And Functions
Important definitions include `VMCI_TRANSPORT_PACKET_VERSION`, control resource IDs, notification protocol bits `VSOCK_PROTO_PKT_ON_NOTIFY` and `VSOCK_PROTO_ALL_SUPPORTED`, `enum vmci_transport_packet_type`, `struct vmci_transport_packet`, `struct vmci_transport_notify_pkt`, `struct vmci_transport_notify_pkt_q_state`, `union vmci_transport_notify`, and `struct vmci_transport`. Exported helpers include `vmci_transport_send_wrote_bh()`, `vmci_transport_send_read_bh()`, `vmci_transport_send_wrote()`, `vmci_transport_send_read()`, `vmci_transport_send_waiting_write()`, and `vmci_transport_send_waiting_read()`.

## Control Flow
The header itself has no executable control flow, but it defines the stream control vocabulary: request/negotiate/offer/attach establish queue pairs; wrote/read and waiting-read/waiting-write drive notification protocols; reset and shutdown tear connections down; request2/negotiate2 carry protocol bitmasks for newer notify schemes.

## State And Persistence
`struct vmci_transport` persists per socket in `vsk->trans`. It stores datagram and queue-pair handles, queue sizes, detach subscription id, negotiated notification state, selected notify ops, cleanup list linkage, a guarded socket pointer for asynchronous VMCI events, and a spinlock protecting that pointer.

## Dependencies And Integration Points
The header depends on VMCI definitions/API headers, `vsock_addr.h`, and `af_vsock.h`. Notification source files consume the packet and notify state layouts, while `vmci_transport.c` owns allocation, handshake, and data movement.

## Risks And Edge Cases
The packet layout is wire-visible within VMCI control datagrams, so version and field changes must preserve compatibility. The `vmci_trans()` macro assumes `vsk->trans` is a valid VMCI allocation; callers must only use it after successful transport assignment. Notification structures encode subtle waiting/read/write state that must stay consistent with the negotiated notify ops.

## Test Signals
Useful signals include build coverage for all VMCI transport sources, protocol negotiation between old and new packet types, layout/endian checks for `struct vmci_transport_packet`, notification wait/read/write behavior, and event-detach tests validating `struct vmci_transport` lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/vmci_transport.h -->
