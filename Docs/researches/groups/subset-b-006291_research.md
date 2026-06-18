# subset-b-006291 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/socket.c -->
# sources/distributed-fs/ceph-client/net/tipc/socket.c

## Purpose
Implements the AF_TIPC socket API for datagram, reliable datagram, sequenced packet, and stream sockets. It owns socket creation/registration, port-id allocation, bind/publish/withdraw, connection setup and teardown, group communication send paths, receive filtering, flow control, socket options, ioctl handling, and netlink/socket-diagnostic export.

## Important APIs, Types, And Functions
The private `struct tipc_sock` extends `struct sock` with a prebuilt TIPC header, port id, publication list, congestion state, block/message flow-control windows, peer address, group membership, multicast method, Nagle counters, and receive accounting. Public entry points include `tipc_socket_init`, `tipc_socket_stop`, `tipc_sk_rcv`, `tipc_sk_mcast_rcv`, `tipc_sk_reinit`, rhashtable init/destroy, netlink dump helpers, `tipc_sock_get_portid`, overload predicates, `tipc_sk_bind`, and `tsk_set_importance`. The proto ops tables (`msg_ops`, `packet_ops`, `stream_ops`) bind Linux socket operations to TIPC-specific send, receive, connect, listen, accept, poll, shutdown, option, and ioctl handlers.

## Control Flow And State
Creation validates socket type/protocol, allocates a `tipc_sock`, inserts it into the per-net rhashtable, initializes `phdr`, receive buffer limits, callbacks, timers, and connectionless droppable defaults. Send flow splits by group membership, address type, and socket type: connectionless sends build named/direct/multicast messages; stream and seqpacket sends rely on connected peer state, block flow control, Nagle aggregation, and `tipc_node_xmit`. Receive flow enters through `tipc_sk_rcv` or multicast cloning in `tipc_sk_mcast_rcv`, performs socket lookup by destination port, queues directly or through backlog, filters protocol/group/multicast/control messages, rejects invalid or overloaded input, and wakes readers. Connection state moves through open, listening, connecting, established, and disconnecting with explicit validation in `tipc_set_sk_state`, SYN/ACK handling, accept child creation, periodic probes, reconnect retry, FIN/error responses, and `tipc_node_add_conn`/`tipc_node_remove_conn`.

## Dependencies And Integration Points
This file integrates with the TIPC name table (`tipc_nametbl_*`), node/link transmit and MTU/capability queries, broadcast/multicast routing, group membership logic, generic netlink policies, socket diagnostics, tracepoints, sysctl receive memory values, and core Linux socket locking, wait queues, timers, rhashtable, RCU, and skb ownership. Socket publications feed service lookup and topology events; netlink dump helpers share the same socket hash iterator used by diagnostic tooling.

## Risks And Test Signals
Risk is concentrated around state transitions under socket locks, RCU hash lifetime, double-counted receive memory between backlog and receive queue, congestion wakeups paired with memory barriers, retransmitted SYNs under link congestion, group broadcast flow-control sequencing, and partial stream reads. Good signals include AF_TIPC bind/connect/listen/accept/socketpair tests, service publication dump tests, multicast/group unicast/anycast/broadcast tests, rcvbuf overload rejection, blocking/nonblocking send and receive timeout behavior, netlink socket/publication dumps, trace filtering, and teardown under queued traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/socket.h -->
# sources/distributed-fs/ceph-client/net/tipc/socket.h

## Purpose
Declares the public interface and shared flow-control constants for the TIPC socket implementation. It is the boundary used by TIPC core, netlink, diagnostics, topology server, trace code, and bearer receive paths to interact with sockets without exposing the private `struct tipc_sock` layout.

## Important APIs, Types, And Constants
The header defines legacy message-based flow-control values (`FLOWCTL_MSG_WIN`, `FLOWCTL_MSG_LIM`), block flow-control size (`FLOWCTL_BLK_SZ`), and receive buffer min/default/max constants. It forward-declares `struct tipc_sock` and exports lifecycle APIs (`tipc_socket_init`, `tipc_socket_stop`), receive dispatch (`tipc_sk_rcv`, `tipc_sk_mcast_rcv`), address reinitialization (`tipc_sk_reinit`), hash table setup/teardown, socket and publication netlink dump functions, socket-diagnostic fill/walk helpers, dump iterator start/done helpers, socket port lookup, overload predicates, bind, and importance setter.

## Control Flow And State
The header itself has no runtime state, but the constants directly shape socket receive-buffer sizing and the fallback path when peers do not advertise block flow control. The declared rhashtable and dump APIs imply per-network-namespace socket indexing, and `tipc_sk_rcv`/`tipc_sk_mcast_rcv` are the ingress bridge from lower TIPC routing into Linux socket queues.

## Dependencies And Integration Points
Includes `net/sock.h` and `net/genetlink.h`, so consumers can pass `struct sock`, `struct socket`, `struct sk_buff`, and netlink callback objects. `trace.h` calls `tipc_sk_dump`, `tipc_sock_get_portid`, and overload checks; `topsrv.c` uses `tipc_sk_bind` and `tsk_set_importance`; TIPC network namespace setup uses hash init/destroy.

## Risks And Test Signals
The main risk is contract drift: changing constants or prototypes can silently alter queue limits, diagnostics, or module init ordering across TIPC. Compile coverage with TIPC enabled, socket diagnostics, tracepoints, and topology server enabled is the primary signal. Runtime tests should exercise block-flow and legacy-flow peers because the constants here define both behavior families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/subscr.c -->
# sources/distributed-fs/ceph-client/net/tipc/subscr.c

## Purpose
Implements topology service subscriptions: creating subscription objects from user/kernel requests, matching name-table publications against subscribed ranges and filters, emitting events, handling subscription timeout, and unsubscribing.

## Important APIs, Types, And Functions
`tipc_sub_subscribe` validates and allocates `struct tipc_subscription`, normalizes endian-sensitive request fields, registers with the name table, and arms an optional timer. `tipc_sub_report_overlap` is called by name-table publication changes to filter by service range, scope, and `TIPC_SUB_PORTS`/`TIPC_SUB_SERVICE`, then queue events. `tipc_sub_unsubscribe` removes the subscription from the name table, cancels the timer, unlinks it from the subscriber connection, and drops its reference. `tipc_sub_get`/`tipc_sub_put` wrap the `kref`.

## Control Flow And State
Subscription creation copies both the raw user-format request into `evt.s` and a host-endian version into `s`. The event template is reused for found/withdrawn/timeout notifications, preserving user-endian output with `tipc_evt_write`. Timeout acquires `sub->lock`, emits a `TIPC_SUBSCR_TIMEOUT` event without a publication, and marks the subscription inactive so later publication events do not send duplicates. Overlap reporting also holds `sub->lock`, serializing publication events with timeout state.

## Dependencies And Integration Points
Depends on TIPC core allocation/logging, `name_table.h` publication subscription hooks, and `tipc_topsrv_queue_evt` for delivery to userspace or kernel subscribers. The name table owns the service-list membership while topology server connections own the subscriber-list membership.

## Risks And Test Signals
Risks include endian compatibility with old subscribers, racing timeout with publication events, reference lifetime across name-table and connection lists, and enforcing mutually exclusive `TIPC_SUB_PORTS`/`TIPC_SUB_SERVICE` semantics. Test signals include subscription create/cancel, service-range overlap edges, node-vs-cluster scope filters, timeout delivery, cancellation before timeout, and max subscription pressure through `topsrv.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/subscr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/subscr.h -->
# sources/distributed-fs/ceph-client/net/tipc/subscr.h

## Purpose
Defines the topology subscription object and endian conversion helpers used by the topology server and name table. It also declares subscription lifecycle APIs and topology-server namespace lifecycle functions.

## Important APIs, Types, And Macros
`struct tipc_subscription` contains the host-endian subscription, event template, `kref`, namespace pointer, optional timer, list nodes for name-table and subscriber ownership, connection id, inactive flag, and spinlock. `TIPC_MAX_SUBSCR` and `TIPC_MAX_PUBL` define topology-service scale limits. `TIPC_FILTER_MASK`, `tipc_sub_read`, `tipc_sub_write`, and `tipc_evt_write` preserve compatibility with clients that signal endian mode through filter bits.

## Control Flow And State
The header models dual ownership: subscriptions live simultaneously in a service/name-table list and a per-connection list. Timers and publication callbacks mutate the event template under `sub->lock`, while `kref` controls final deallocation. The endian macros are part of runtime behavior because they decide whether fields are byte-swapped based on filter bits.

## Dependencies And Integration Points
Includes `topsrv.h`, bringing topology server event delivery into the subscription contract. It forward-declares `publication` and `tipc_conn`, while `subscr.c`, `topsrv.c`, and name-table code use the list nodes and lifecycle functions together.

## Risks And Test Signals
Risk centers on list ownership conventions and endian macro assumptions. Tests should cover little-endian and compatibility-form requests, cancellation equality against raw `evt.s`, timer cancellation, and publication overlap reporting after connection close. Build coverage should ensure all topology service users include this header without circular type exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/subscr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/sysctl.c -->
# sources/distributed-fs/ceph-client/net/tipc/sysctl.c

## Purpose
Registers `/proc/sys/net/tipc` controls for receive memory sizing, name-table timeout, trace socket filtering, optional crypto parameters, key exchange enablement, and broadcast retransmission behavior.

## Important APIs, Types, And Functions
The static `tipc_table` defines `tipc_rmem`, `named_timeout`, `sk_filter`, optional `max_tfms` and `key_exchange_enabled` under `CONFIG_TIPC_CRYPTO`, and `bc_retruni`. `tipc_register_sysctl` installs the table under `init_net` via `register_net_sysctl`, and `tipc_unregister_sysctl` removes it through the saved table header.

## Control Flow And State
There is one module-level `tipc_ctl_hdr`. Register returns `-ENOMEM` if sysctl registration fails. Unregister assumes registration succeeded and tears down the table. Each sysctl points at global TIPC tunables declared in included subsystem headers; min/max handlers enforce coarse numeric lower/upper bounds where provided.

## Dependencies And Integration Points
Includes `core.h`, `trace.h`, `crypto.h`, `bcast.h`, and Linux sysctl support. `sysctl_tipc_rmem` feeds socket receive buffer defaults, `sysctl_tipc_sk_filter` gates trace events, crypto controls affect TIPC crypto worker allocation and key exchange, and `sysctl_tipc_bc_retruni` affects broadcast retransmission policy.

## Risks And Test Signals
Risks are invalid tunable ranges, mismatched handler types (`int` vs `unsigned long` vectors), global-only namespace behavior through `init_net`, and missing unregister during module failure paths. Test signals include sysctl registration/unregistration with TIPC module load/unload, read/write bounds for each file, trace filtering changes taking effect, and crypto-option compilation both enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/topsrv.c -->
# sources/distributed-fs/ceph-client/net/tipc/topsrv.c

## Purpose
Implements the TIPC topology server. It creates a kernel listening socket on `TIPC_TOP_SRV`, accepts userspace subscriber connections, receives subscription requests, queues topology events back to subscribers, supports in-kernel subscriptions, and manages per-network-namespace server lifetime.

## Important APIs, Types, And Functions
`struct tipc_topsrv` owns the connection idr, namespace pointer, ordered receive/send workqueues, accept work, listener socket, and server name. `struct tipc_conn` owns a topology connection, socket, flags, subscription list, outqueue, work items, and kref. Public functions are `tipc_topsrv_queue_evt`, `tipc_topsrv_kern_subscr`, `tipc_topsrv_kern_unsubscr`, `tipc_topsrv_init_net`, and `tipc_topsrv_exit_net`. Key internal functions handle connection allocation/lookup/close, subscription deletion, socket send/receive work, accept callbacks, listener creation, and namespace start/stop.

## Control Flow And State
Namespace init allocates the server, initializes idr and subscription count, creates ordered workqueues, then creates a critical-importance AF_TIPC SEQPACKET listener bound to the topology service. Listener data-ready queues accept work; accepted sockets get data-ready and write-space callbacks that schedule receive/send work. Receive work reads fixed-size `tipc_subscr` records, creates or cancels subscriptions, and closes malformed connections. Events are copied into `outqueue_entry` objects, sent nonblocking through `kernel_sendmsg`, and retried via write-space callbacks. Timeout events mark entries inactive and trigger subscription deletion after delivery. Shutdown clears callbacks, closes all connections, restores module references for the listener socket, destroys workqueues, idr, and server memory.

## Dependencies And Integration Points
Integrates with `subscr.c`, TIPC sockets (`tipc_sk_bind`, `tsk_set_importance`, `tipc_sk_rcv`), name-table subscriptions, core namespace `tipc_net`, Linux idr, workqueues, kernel sockets, module reference counts, and loopback delivery for kernel subscribers.

## Risks And Test Signals
Risk lies in async lifetime: idr lookup vs close, work items intentionally not flushed per connection, callback locking through `sk_callback_lock`, subscription count balance, and module reference adjustments for internally created sockets. Test signals include multiple concurrent subscribers, malformed short requests, cancel requests, timeout cleanup, send-buffer backpressure, namespace teardown with live connections, kernel subscription loopback delivery, and max-subscription rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/topsrv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/topsrv.h -->
# sources/distributed-fs/ceph-client/net/tipc/topsrv.h

## Purpose
Declares the topology server interface used by subscriptions, kernel topology clients, and TIPC namespace lifecycle code.

## Important APIs, Types, And Constants
The header defines `TIPC_SERVER_NAME_LEN` and topology subscription filter bits for cluster scope, node scope, and no-status behavior. It exposes `tipc_topsrv_queue_evt` for subscription event delivery, `tipc_topsrv_kern_subscr` for creating an in-kernel subscription bound to a local port id, and `tipc_topsrv_kern_unsubscr` for dropping that kernel subscription.

## Control Flow And State
The header does not define state, but the API implies event queueing by connection id and asynchronous delivery by the topology server. Kernel subscribers receive an allocated `conid` that must be passed back to unsubscribe; userspace subscribers are handled through sockets in `topsrv.c`.

## Dependencies And Integration Points
Includes `core.h` for TIPC core and network namespace types. `subscr.h` includes this header to route events, while code outside the topology server can use kernel subscription helpers without seeing `struct tipc_conn`.

## Risks And Test Signals
The major risk is semantic drift in filter bits or event delivery contracts between name table, subscription, and topology server code. Build tests should cover `CONFIG_TIPC` with topology service enabled. Runtime tests should create kernel subscriptions, emit publication events, and verify unsubscribe removes all per-connection subscription state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/topsrv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/trace.c -->
# sources/distributed-fs/ceph-client/net/tipc/trace.c

## Purpose
Provides concrete tracepoint support helpers for TIPC. It defines tracepoints by including `trace.h` under `CREATE_TRACE_POINTS`, owns the socket trace filter sysctl storage, and formats skbs and skb queues into compact trace buffers.

## Important APIs, Types, And Functions
`sysctl_tipc_sk_filter[5]` stores `(portid, sock type, name type, lower, upper)` filtering data consumed by `tipc_sk_filtering` in `socket.c`. `tipc_skb_dump` formats TIPC message header fields, user/type/size/node/seq/ack data, protocol-specific fields, optional skb metadata, and TIPC skb control block fields. `tipc_list_dump` summarizes skb queues, either head/tail or first/last five entries.

## Control Flow And State
Trace helper calls are synchronous from tracepoint fast-assign paths. They write into tracepoint-provided dynamic arrays sized by constants from `trace.h`, use `scnprintf` to avoid overflow, and avoid mutating packets. The only persistent state is the socket filter array, which sysctl updates can change at runtime.

## Dependencies And Integration Points
Depends on TIPC message accessors, skb control block layout, Linux tracepoint generation, and the sysctl table in `sysctl.c`. `trace.h` trace events call these helpers for socket, link, node, list, and skb dumps.

## Risks And Test Signals
Risk comes from formatting assumptions changing with message layout, trace buffer truncation hiding important fields, and trace helpers being called from sensitive paths. Test signals include enabling TIPC tracepoints via ftrace/perf, dumping null and non-null skbs/queues, verifying sysctl filter effects, and exercising link, socket, multicast, and overload paths while tracing is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/trace.h -->
# sources/distributed-fs/ceph-client/net/tipc/trace.h

## Purpose
Declares the TIPC tracepoint system, dump-size constants, symbolic event/state printers, helper prototypes, and trace event classes for skbs, skb lists, sockets, links, nodes, finite-state machines, and bearer device events.

## Important APIs, Types, And Macros
The header defines dump masks such as `TIPC_DUMP_TRANSMQ`, `TIPC_DUMP_SK_RCVQ`, and `TIPC_DUMP_ALL`; symbolic macros `state_sym`, `evt_sym`, and `dev_evt_sym`; helper prototypes for skb/list/socket/link/node dumps and socket filtering; event classes `tipc_skb_class`, `tipc_list_class`, `tipc_sk_class`, `tipc_link_class`, `tipc_link_transmq_class`, `tipc_node_class`, and `tipc_fsm_class`; and concrete events such as `tipc_sk_sendmsg`, `tipc_sk_filter_rcv`, `tipc_link_retrans`, `tipc_node_timeout`, and `tipc_l2_device_event`.

## Control Flow And State
The tracepoint declarations generate static tracepoints when included normally and definitions when included by `trace.c`. Conditional socket events call `tipc_sk_filtering`, while overload events add a second condition. Dynamic arrays are sized based on whether deep queue dumps are requested.

## Dependencies And Integration Points
Includes Linux tracepoint infrastructure and TIPC core, link, socket, and node headers. Trace calls are scattered through socket, link, node, bearer, and protocol receive paths, and `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` are set so kernel trace generation can find this header.

## Risks And Test Signals
Risks include tracepoint ABI churn, helper functions being unavailable under include-order changes, and expensive deep dumps on hot paths. Test signals include compiling with tracepoints enabled, enabling each event class through tracing, confirming socket filter conditions work, and checking that link/node FSM symbolic output matches actual state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/udp_media.c -->
# sources/distributed-fs/ceph-client/net/tipc/udp_media.c

## Purpose
Implements the UDP bearer media for TIPC. It maps TIPC media addresses to IPv4/IPv6 UDP endpoints, creates UDP tunnel sockets, transmits and receives TIPC packets over UDP, supports multicast and replicast peer discovery, and exports UDP bearer details through netlink.

## Important APIs, Types, And Functions
`struct udp_media_addr` stores protocol, port, and IPv4/IPv6 address in network byte order. `struct udp_replicast` stores a remote peer with a dst cache and RCU list node. `struct udp_bearer` ties a TIPC bearer to a UDP socket, interface index, cleanup work, and replicast list. The exported `udp_media_info` supplies generic media callbacks: send, enable, disable, address string/message conversion, and defaults. Public netlink helpers dump/add remote IPs and bearer data.

## Control Flow And State
Enable parses local and remote sockaddr netlink attributes, validates protocol match, finds the local device, autoconfigures node identity if needed, creates a UDP socket, installs `tipc_udp_recv` as the tunnel receive callback, initializes dst caches, joins multicast or adds an initial replicast peer, and attaches `udp_bearer` via RCU. Send expands headroom, marks the inner protocol as TIPC, then either unicasts/multicasts through `tipc_udp_xmit` or copies packets across the replicast peer list. Receive strips the UDP header, forwards packets to `tipc_rcv` if the bearer is up, and learns replicast peers from discovery packets when appropriate. Disable marks the socket dead, clears the bearer pointer, schedules cleanup outside rtnl, destroys dst caches, releases the UDP socket, synchronizes networking readers, and frees memory.

## Dependencies And Integration Points
Uses Linux UDP tunnel APIs, IPv4/IPv6 routing, multicast joins, dst caches, rtnl/RCU, TIPC bearer/netlink/core/node identity, and TIPC receive path. Netlink policies from `netlink.h` define accepted UDP options.

## Risks And Test Signals
Risks include RCU lifetime between bearer disable and receive, route-cache correctness under address changes, multicast scope/device selection, headroom expansion failures, replicated skb copy failures, peer-list races under rtnl, and IPv6 scope-id validation. Test signals include IPv4 and IPv6 UDP bearers, multicast and replicast setups, remote IP add/dump, device down cleanup, packet receive after disable, low-MTU rejection via header helper, and route/cache invalidation scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/udp_media.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/udp_media.h -->
# sources/distributed-fs/ceph-client/net/tipc/udp_media.h

## Purpose
Declares UDP bearer netlink helpers and an MTU validation helper when `CONFIG_TIPC_MEDIA_UDP` is enabled.

## Important APIs, Types, And Functions
The header exposes `tipc_udp_nl_bearer_add`, `tipc_udp_nl_add_bearer_data`, and `tipc_udp_nl_dump_remoteip` for generic TIPC netlink code to manage UDP bearer-specific remote endpoints. `tipc_udp_mtu_bad` checks whether an MTU can carry minimum TIPC bearer data plus IPv4 and UDP headers, logging a warning on invalid values.

## Control Flow And State
No persistent state is declared here. The inline MTU helper returns `false` for acceptable MTUs and `true` for too-low values, so callers can reject bearer configuration before runtime packet loss.

## Dependencies And Integration Points
Includes IP and UDP header definitions and depends on TIPC bearer/netlink types from includers. It is conditionally compiled only for UDP media support, so generic code must guard use through the same config.

## Risks And Test Signals
The main risk is validating only IPv4+UDP overhead even though the UDP media implementation also supports IPv6, where overhead differs. Tests should include bearer configuration at boundary MTUs, IPv4/IPv6 UDP media builds, and netlink remote-IP add/dump calls with and without UDP media enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/udp_media.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/Kconfig -->
# sources/distributed-fs/ceph-client/net/tls/Kconfig

## Purpose
Defines kernel configuration switches for kTLS core support, hardware offload, and legacy TCP stack bypass offload.

## Important Options
`CONFIG_TLS` is a tristate depending on `INET` and selecting crypto, AES, GCM, and `NET_SOCK_MSG`; it enables in-kernel symmetric TLS record handling. `CONFIG_TLS_DEVICE` is a bool depending on TLS and selecting decrypted-skb, xmit-validation, and RX queue mapping support for NIC TLS offload. `CONFIG_TLS_TOE` is a bool for legacy TCP offload engine semantics incompatible with normal Linux networking stack behavior.

## Control Flow And State
Kconfig has no runtime state, but it controls which objects and inline stubs are built. `TLS_DEVICE` gates `tls_device.c` and `tls_device_fallback.c`, plus real functions in `tls.h` instead of `-EOPNOTSUPP` stubs. `TLS_TOE` gates `tls_toe.o`.

## Dependencies And Integration Points
The selections ensure crypto AEAD primitives and socket-message infrastructure are present for software kTLS. Device offload selections enable decrypted skb tagging, xmit validation hooks, and socket RX queue mapping needed by NIC offload drivers.

## Risks And Test Signals
Risks include unexpected feature availability when TLS is modular, missing selected dependencies for device offload, and enabling TOE semantics in environments expecting normal TCP stack behavior. Test signals include allmodconfig/allyesconfig builds, TLS without device offload builds using `tls.h` stubs, and runtime kTLS setsockopt tests under software and hardware-offload configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/Makefile -->
# sources/distributed-fs/ceph-client/net/tls/Makefile

## Purpose
Builds the kTLS subsystem object set according to the selected kernel configuration.

## Important Build Rules
`obj-$(CONFIG_TLS) += tls.o` builds the aggregate TLS object. `tls-y` always includes `tls_main.o`, `tls_sw.o`, `tls_proc.o`, `trace.o`, and `tls_strp.o`. `tls-$(CONFIG_TLS_TOE)` adds `tls_toe.o`, and `tls-$(CONFIG_TLS_DEVICE)` adds `tls_device.o` plus `tls_device_fallback.o`. `CFLAGS_trace.o := -I$(src)` lets trace generation include local trace headers.

## Control Flow And State
There is no runtime state, but object composition controls which symbols are linked and which `tls.h` paths are live. Device offload support is all-or-nothing at build time for the implementation files, while runtime availability still depends on netdev features and driver `tlsdev_ops`.

## Dependencies And Integration Points
Integrates with kernel kbuild and the Kconfig options in the same directory. The aggregate `tls.o` is the module or built-in unit consumed by the networking stack.

## Risks And Test Signals
Risk is primarily build drift: adding APIs to `tls.h` without adding corresponding objects under the right config, or breaking trace include paths. Test signals include `CONFIG_TLS=m`, built-in TLS, TLS without device offload, TLS with TOE, and TLS with device offload builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls.h -->
# sources/distributed-fs/ceph-client/net/tls/tls.h

## Purpose
Defines internal kTLS interfaces, cipher metadata helpers, software/device offload prototypes, strparser contracts, record sequence helpers, and TLS record header/AAD construction helpers shared by TLS core, software, and device offload code.

## Important APIs, Types, And Functions
`struct tls_cipher_desc` describes nonce, IV, key, salt, tag, record sequence sizes and offsets, cipher name, offload capability, and crypto-info size. `get_cipher_desc` bounds cipher lookup. `crypto_info_iv/key/salt/rec_seq` compute typed offsets into user crypto-info structs. `struct tls_rec` models software TLS records with plaintext/encrypted sk_msgs, AEAD scatterlists, content type, AAD, IV, and inline AEAD request. The header declares context lifecycle, protocol initialization, software send/receive/resource APIs, device send/splice/write-space/offload APIs, cmsg processing, decrypt, fallback init, strparser APIs, and TX push helpers.

## Control Flow And State
Inline helpers manipulate record sequence state and record formatting. `tls_advance_record_sn` increments TX sequence and IV where TLS 1.2 GCM requires it, aborting on wrap. `tls_xor_iv_with_seq` handles TLS 1.3/ChaCha nonce behavior. `tls_fill_prepend` writes the TLS record header and explicit IV/nonce fields. `tls_make_aad` builds AEAD additional data differently for TLS 1.2 and 1.3. Under `CONFIG_TLS_DEVICE`, real device-offload prototypes are exposed; otherwise inline stubs return success for init/cleanup and `-EOPNOTSUPP` for offload setup.

## Dependencies And Integration Points
Depends on public `net/tls.h`, TLS protocol structures, `skmsg`, byte order helpers, AEAD users, and TLS strparser state. It is the central private API boundary between `tls_main`, `tls_sw`, `tls_strp`, `tls_device`, and `tls_device_fallback`.

## Risks And Test Signals
Risks include cipher descriptor offset mistakes, record sequence wrap handling, TLS 1.2 vs TLS 1.3 header/AAD differences, config-stub mismatches, and shared helper changes affecting both software and hardware paths. Test signals include cipher setup for every supported cipher, TLS 1.2 and 1.3 send/receive, record sequence boundary tests, software-only builds, device-offload builds, and fallback encryption validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_device.c -->
# sources/distributed-fs/ceph-client/net/tls/tls_device.c

## Purpose
Implements kTLS hardware offload for TX and RX. It attaches TLS contexts to netdevices, builds TX record metadata for NIC encryption, tracks records for retransmission fallback, handles TX/RX resync, falls back when devices go down, and registers netdevice notifiers.

## Important APIs, Types, And Functions
Public functions include `tls_device_sk_destruct`, `tls_device_free_resources_tx`, `tls_offload_tx_resync_request`, `tls_device_sendmsg`, `tls_device_splice_eof`, `tls_get_record`, `tls_device_write_space`, `tls_device_rx_resync_new_rec`, `tls_device_decrypted`, `tls_set_device_offload`, `tls_set_device_offload_rx`, `tls_device_offload_cleanup_rx`, `tls_device_init`, and `tls_device_cleanup`. Global state includes `device_offload_lock`, `destruct_wq`, `tls_device_list`, `tls_device_down_list`, `tls_device_lock`, and `dummy_page`.

## Control Flow And State
TX offload validates the route netdev, hardware features, TLS 1.2, and offloadable cipher, initializes protocol info and fallback AEAD, creates a start-marker record, registers the flow with `tls_dev_add`, attaches the context, and installs `tls_validate_xmit_skb`. Sendmsg serializes on `tx_lock`, copies or splices user data into page fragments, closes records with tag placeholders and headers, pushes scatterlists through TCP, and records sequence ranges for retransmission. ACK cleanup deletes fully acknowledged records. RX offload allocates RX context, enables software RX parsing, adds the device flow, and uses resync modes for driver-requested, core-next-hint, and async request handling. Device-down handling blocks new offloads, moves contexts out of the active list, disables xmit offload, clears netdev pointers, sets degraded RX, synchronizes network readers, deletes driver contexts, and leaves final memory cleanup to socket destruction or refcount completion.

## Dependencies And Integration Points
Integrates with netdevice `tlsdev_ops`, TCP write sequencing and clean-acked callbacks, TLS software parser/decrypt fallback, xmit validation hooks, socket destructors, page fragments, scatterlists, RCU, refcounts, workqueues, and TLS tracepoints.

## Risks And Test Signals
Risk is high around context lifetime, device-down races, refcount/list transitions, partial records, retransmission of records already acked, RX mixed decrypted/ciphertext skbs, resync request wraparound, and fallback after route/device changes. Test signals include TX/RX offload setup failures, NIC down while traffic is active, retransmission over a non-offload device, splice/sendfile with zerocopy, partial writes and MSG_MORE/EOR validation, RX resync modes, socket close during notifier handling, and trace/stat increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_device_fallback.c -->
# sources/distributed-fs/ceph-client/net/tls/tls_device_fallback.c

## Purpose
Provides the software encryption fallback for kTLS TX device offload. It encrypts outgoing skbs when they are transmitted through a device that is not the offload device, after offload is degraded, or through explicit fallback helpers.

## Important APIs, Types, And Functions
The exported/public functions are `tls_validate_xmit_skb`, `tls_validate_xmit_skb_sw`, `tls_encrypt_skb`, and `tls_sw_fallback_init`. Internal helpers allocate AEAD requests, encrypt one or more records across scatterwalks, update TCP checksums, clone/complete replacement skbs, build input and output scatterlists, and perform the fallback transformation.

## Control Flow And State
Fallback initialization validates an offloadable cipher, allocates an async AEAD transform, sets the key, and configures authentication tag size. During xmit validation, packets sent through the original offload device or a bond master pass through unchanged; others enter `tls_sw_fallback`. The fallback locates the TLS record covering the skb TCP sequence via `tls_get_record`, accounts for any sync data before the packet payload, builds scatterlists from saved record frags plus the skb payload, allocates a replacement skb, encrypts records with AEAD using reconstructed IV/AAD/record sequence, copies headers, adjusts ownership and checksum state, releases temporary fragment references, and consumes or frees the original skb.

## Dependencies And Integration Points
Depends on `tls_device.c` record tracking, cipher descriptors and AAD helpers from `tls.h`, Linux crypto AEAD, scatterwalk, skb fragment reference helpers, TCP/IP checksum helpers, xmit validation hooks, and public `net/tls.h` context accessors.

## Risks And Test Signals
Risks include incorrect record lookup after ACK cleanup, sync-size edge cases for packets before offload start, scatterlist sizing with fragmented records and skbs, checksum ownership accounting, async crypto failure, partial record handling where auth tags are intentionally discarded from output, and route changes causing frequent fallback. Test signals include retransmits through non-offload devices, device down after TX offload, packets before the start marker, fragmented sendfile records, IPv4 and IPv6 checksum validation, AEAD setup failures, and comparing fallback ciphertext with normal software kTLS output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_device_fallback.c -->
