# subset-b-005935 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/af_vsock.h -->
# sources/distributed-fs/ceph-client/include/net/af_vsock.h

## Purpose

`af_vsock.h` defines the in-kernel AF_VSOCK socket object, transport interface, global lookup tables, tap hooks, receive helpers, BPF integration hooks, and network-namespace mode helpers used by `net/vmw_vsock/af_vsock.c` and transport drivers. It is the contract between the common vsock socket layer and transports such as virtio, VMCI, Hyper-V, and loopback.

## Important APIs, Types, and Functions

`struct vsock_sock` embeds `struct sock` first and adds local/remote `sockaddr_vm`, table links, trust/owner metadata, stream/listener state, delayed works for connect/pending/close paths, peer shutdown flags, buffer sizing, and transport-private `trans`. `struct vsock_transport` is the central vtable: lifecycle, connection, datagram, stream, seqpacket, notification, shutdown, CID lookup, `read_skb`, and zero-copy capability callbacks. `vsock_core_register()` and `vsock_core_unregister()` publish a transport with feature flags for host-to-guest, guest-to-host, datagram, and local service. Table helpers cover bound/connected insertion, removal, lookup, pending/accept queues, transport assignment, CID lookup, and linger.

The tap API uses `struct vsock_tap`, `vsock_add_tap()`, `vsock_remove_tap()`, and `vsock_deliver_tap()` to mirror vsock traffic to monitor devices. Receive helpers cover connectible and datagram sockets. Namespace helpers expose global/current mode reads, child mode locking, and cross-namespace reachability checks.

## Control Flow

Common socket operations allocate a `vsock_sock`, assign a transport, add it to bound or connected hash tables under `vsock_table_lock`, and then call the selected `vsock_transport` callbacks for transport-specific packet movement. Listener flow is modeled through pending and accept queues: children remain pending until the handshake completes, then move to the accept queue. Stream and seqpacket I/O routes through the vtable while notification callbacks let transports adjust poll and blocking behavior around enqueue/dequeue. Namespace reachability is evaluated by comparing `struct net` vsock modes before allowing cross-namespace communication.

## State and Persistence Behavior

There is no filesystem persistence. State lives in socket objects, global bound/connected tables, delayed work items, tap registrations, and per-net vsock mode fields. `owner`, `trusted`, and cached peer datagram fields are deliberately immutable after create/destruct because they are read without the socket lock. Buffer sizes are protected by `lock_sock(sk)`.

## Dependencies and Integration Points

The header depends on Linux sockets, workqueues, credentials, sk_buffs, BPF psock support when enabled, `netns/vsock.h`, UAPI `vm_sockets.h`, and `vsock_addr.h`. Transport drivers implement `struct vsock_transport`; userspace observes the ABI through AF_VSOCK sockets; optional taps integrate with net devices and monitor paths.

## Risks and Edge Cases

The global tables require correct `vsock_table_lock` discipline; stale table links can expose sockets after teardown. Transport callbacks must honor lock context, especially notification callbacks where comments document `sk_lock` ownership. Namespace helpers treat `NULL` as global mode, which is convenient but easy to misuse in new code. Cross-namespace policy depends on the child mode lock being set consistently. Zero-copy and BPF hooks are conditional and must degrade cleanly when unsupported.

## Test Signals

Exercise bind/connect/accept teardown races, pending-to-accept transitions, stream/dgram/seqpacket routing per transport, transport unregister with connected sockets, tap add/remove and delivery, BPF proto update/restore when enabled, namespace mode combinations, CID routing/fallback, linger/close delayed work, and MSG_ZEROCOPY allow/deny behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/af_vsock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ah.h -->
# sources/distributed-fs/ceph-client/include/net/ah.h

## Purpose

`ah.h` provides the small shared IPsec Authentication Header support contract used by IPv4/IPv6 AH implementations. It defines AH transform data and a helper to locate the AH header in an skb.

## Important APIs, Types, and Functions

`struct ah_data` stores full and truncated Integrity Check Value lengths plus the `struct crypto_ahash *` transform used to compute or verify authentication data. `ip_auth_hdr()` casts `skb_transport_header(skb)` to `struct ip_auth_hdr *`, relying on callers to have already positioned the transport header at the AH header.

## Control Flow

This header has no independent control flow. AH input/output code prepares the skb transport offset, retrieves `ip_auth_hdr()`, and uses `ah_data` from xfrm state to authenticate packet bytes through the crypto ahash API.

## State and Persistence Behavior

No persistent state is defined here. `ah_data` is per-transform runtime state owned by the xfrm/IPsec stack and freed with the transform state.

## Dependencies and Integration Points

It depends on `linux/skbuff.h`, the crypto ahash forward declaration, and the UAPI/internal IP authentication header definition. It integrates with xfrm state, IPv4/IPv6 AH packet processing, and the crypto API.

## Risks and Edge Cases

`ip_auth_hdr()` performs a raw cast with no length validation; callers must ensure skb header offsets and linear access are valid. Incorrect ICV truncation lengths or ahash allocation failures are handled outside this header but are central to AH correctness.

## Test Signals

Validate AH packets with full/truncated ICVs, malformed short skbs, wrong transport header offsets, crypto transform allocation failures, and IPv4/IPv6 xfrm state setup with multiple algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ah.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/aligned_data.h -->
# sources/distributed-fs/ceph-client/include/net/aligned_data.h

## Purpose

`aligned_data.h` centralizes high-contention networking counters into `struct net_aligned_data`, with fields cacheline-aligned on SMP builds to reduce false sharing.

## Important APIs, Types, and Functions

`struct net_aligned_data` always contains `atomic64_t net_cookie`. When `CONFIG_INET` is enabled it also contains cacheline-aligned `tcp_memory_allocated` and `udp_memory_allocated`. The global instance `net_aligned_data` is exported for networking code that needs these shared counters.

## Control Flow

There are no functions. Runtime code atomically updates or reads counters through the global object. Cacheline attributes affect layout and contention behavior rather than logical flow.

## State and Persistence Behavior

The counters are process-lifetime kernel memory only. They persist across namespaces and sockets while the kernel runs, but not across reboot. Atomic operations provide update safety; no file-backed persistence exists.

## Dependencies and Integration Points

The header depends on atomic types and cacheline alignment attributes from Linux headers. It integrates with core networking cookie allocation and, when enabled, INET TCP/UDP memory accounting.

## Risks and Edge Cases

Adding new fields without `____cacheline_aligned_in_smp` can reintroduce false sharing. Code must treat these as global counters, not per-net namespace state. Counter semantics depend on atomic type width and initialization in the corresponding definition.

## Test Signals

Check layout with and without SMP and `CONFIG_INET`, concurrent TCP/UDP memory accounting stress, net cookie uniqueness/monotonicity expectations, and performance regressions from cacheline sharing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/aligned_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/amt.h -->
# sources/distributed-fs/ceph-client/include/net/amt.h

## Purpose

`amt.h` defines the Automatic Multicast Tunneling netdevice data model, wire headers, state machines, timers, limits, and device-identification helpers used by the AMT gateway/relay implementation.

## Important APIs, Types, and Functions

The header defines AMT message types for discovery, advertisement, request, membership query/update, multicast data, and teardown; set-operation/filter/action/status enums for multicast membership handling; and gateway events. Packed wire structs model each AMT header using endian-sensitive bitfields and nonces/MAC fields. `struct amt_dev` is the main netdevice-private state with the outer device, stream device, namespace, socket pointer, global lock, relay tunnel list, GRO cells, discovery/request/secret/event work, ports, IPs, nonce, MAC, IGMP/MLD query parameters, capacity limits, and gateway event queue.

Relay state is represented by `struct amt_tunnel_list`, `struct amt_group_node`, and `struct amt_source_node`, with spinlocks, delayed GC/source/group timers, RCU heads, hash buckets, nonce/key/MAC fields, and source/group counts. Helpers include `netif_is_amt()` for rtnl link kind detection and `amt_gmi()` to compute the group membership interval from query variables.

## Control Flow

Gateway flow starts with discovery and request work, records received advertisements/queries through status transitions, and queues AMT events in `amt_events` for the event work handler. Relay flow receives discovery/request/update/data messages, allocates or looks up tunnel/group/source nodes, schedules timers for garbage collection and membership expiry, and encapsulates/decapsulates multicast traffic between UDP AMT and the stream device. Header unions allow handlers to parse only the layouts valid for gateway or relay direction.

## State and Persistence Behavior

There is no durable storage. Runtime state is concentrated in `struct amt_dev`, tunnel/group/source RCU lists, socket pointer, GRO cells, work items, nonce/MAC/key material, and timer-backed membership state. Membership and tunnel state expires through delayed work; relay/gateway configuration persists only while the netdevice exists.

## Dependencies and Integration Points

The header depends on siphash/jhash, netdevice, rtnetlink, GRO cells, sockets, IPv4 and optional IPv6 addresses, RCU, delayed work, and UDP/IP header layouts. It integrates as an rtnl link kind named `amt`, with multicast routing/IGMP/MLD behavior and netdevice packet paths.

## Risks and Edge Cases

Packed endian bitfields are fragile across compiler/architecture assumptions and must match AMT wire format exactly. Tunnel/group/source objects mix spinlocks, RCU, and delayed work; missed cancellation or freeing can become use-after-free. Capacity limits (`max_groups`, `max_sources`, `max_tunnels`, event queue length) need enforcement under load. Nonce/MAC/key handling must avoid accepting spoofed updates. IPv6 fields are conditional, so dual-stack code must handle disabled IPv6 builds.

## Test Signals

Test all AMT message parsers, endian layouts, discovery/request retries, nonce mismatch, response MAC validation, gateway and relay status transitions, tunnel/group/source timeout cleanup, maximum group/source/tunnel limits, event queue overflow, GRO delivery, netdevice teardown with pending work, IPv6-enabled and IPv6-disabled builds, and `netif_is_amt()` kind matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/amt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/arp.h -->
# sources/distributed-fs/ceph-client/include/net/arp.h

## Purpose

`arp.h` exposes IPv4 ARP neighbor-table operations, ARP packet creation/transmission helpers, multicast address mapping, ioctl handling, and fast neighbor lookup helpers.

## Important APIs, Types, and Functions

`arp_tbl` is the global ARP `neigh_table`. `arp_hashfn()` hashes an IPv4 key with the device pointer and per-table random seed. `__ipv4_neigh_lookup_noref()` maps loopback/point-to-point lookups to `INADDR_ANY` and performs a no-reference neighbor lookup when `CONFIG_INET` is enabled. `__ipv4_neigh_lookup()` wraps that lookup with RCU and increments the neighbor refcount if possible. `__ipv4_confirm_neigh()` confirms reachability without taking a caller-visible reference. Exported functions cover initialization, ioctls, packet send/create/xmit, multicast mapping, device down cleanup, and forced invalidation.

## Control Flow

IPv4 output or neighbor users call lookup helpers under RCU to find ARP entries. Successful referenced lookups survive beyond the RCU read-side critical section; no-ref lookups are transient. ARP packet paths use `arp_create()` to build an skb and `arp_xmit()` or `arp_send()` to transmit. Device teardown calls `arp_ifdown()` to flush neighbor state.

## State and Persistence Behavior

ARP entries live in the neighbor table and age according to neighbor subsystem timers. No filesystem persistence exists. Refcounts and RCU protect neighbor lifetimes; loopback/point-to-point devices intentionally share `INADDR_ANY` lookup semantics.

## Dependencies and Integration Points

The header depends on net devices, `if_arp.h`, hashing, neighbor core, RCU, and IPv4 configuration. It integrates with IPv4 routing/output, device lifecycle, userspace ARP ioctls, and multicast hardware-address mapping.

## Risks and Edge Cases

No-ref lookups are only safe inside RCU read-side sections. Callers that ignore the loopback/point-to-point key rewrite may see surprising aliasing. Hash quality depends on per-table randomization and device pointer hashing. `CONFIG_INET=n` stubs return `NULL`, so code must handle absence of ARP.

## Test Signals

Exercise referenced and no-ref lookups, loopback and point-to-point key behavior, refcount failure races, ARP send/create for request/reply, multicast mapping per device type, ioctl add/delete/query, device down cleanup, invalidation with and without force, and `CONFIG_INET` disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/arp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ax25.h -->
# sources/distributed-fs/ceph-client/include/net/ax25.h

## Purpose

`ax25.h` provides minimal AX.25 networking constants for callers that need AX.25 address length and protocol identifiers.

## Important APIs, Types, and Functions

It includes UAPI `linux/ax25.h` and defines `AX25_ADDR_LEN` as 7 and `AX25_P_IP` as `0xCC`, the PID used for IP over AX.25.

## Control Flow

There is no runtime control flow. Protocol code uses these constants when parsing, building, or validating AX.25 frames.

## State and Persistence Behavior

No state or persistence is defined.

## Dependencies and Integration Points

The header integrates with AX.25 packet handling and any IP-over-AX.25 code that needs the address and PID constants.

## Risks and Edge Cases

The header is intentionally tiny; risk is mostly misuse of the constants in code that expects variable-length or extended AX.25 address fields. Any broader AX.25 state machine lives elsewhere.

## Test Signals

Validate frame builders/parsers use 7-byte addresses and `0xCC` for IP payloads, including malformed short address fields and non-IP PID values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ax25.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ax88796.h -->
# sources/distributed-fs/ceph-client/include/net/ax88796.h

## Purpose

`ax88796.h` defines platform data for the AX88796/NS8390-style Ethernet driver and an exported reinitialization hook used by board-specific code.

## Important APIs, Types, and Functions

Platform flags describe EEPROM availability, whether the MAC comes from the device, 93CX6 EEPROM usage, or platform-provided MAC address. `struct ax_plat_data` supplies bus word length, default DCR/RCR/GPOC register values, optional register offset table, optional platform MAC pointer, optional block input/output callbacks, and an optional `check_irq()` callback for shared/board-gated interrupt handling. `ax_NS8390_reinit()` is exported for xsurf100 integration.

## Control Flow

At probe time the driver consumes platform data to choose register layout, MAC source, EEPROM path, and I/O functions. Packet TX/RX may use board-specific `block_output()` and `block_input()` callbacks instead of defaults. IRQ handling can call `check_irq()` to decide whether the device likely asserted an interrupt.

## State and Persistence Behavior

No persistent state is stored here. Platform data is static or firmware-provided board configuration. EEPROM contents, if present, are external device state handled by the driver.

## Dependencies and Integration Points

The header depends on platform devices, net devices, sk_buffs, Linux integer types, the AX88796 driver, NS8390 core behavior, and board files or platform glue such as xsurf100.

## Risks and Edge Cases

Bad `wordlength`, register offsets, or default register values can make the device inaccessible. MAC source flags must be mutually coherent; a platform MAC pointer is meaningful only with `AXFLG_MAC_FROMPLATFORM`. Optional block I/O callbacks must match the board bus semantics and skb layout. `check_irq()` returning false incorrectly can lose interrupts.

## Test Signals

Test each MAC source path, EEPROM and 93CX6 modes, 8-bit and 16-bit word lengths, custom register offsets, default and custom block I/O callbacks, shared IRQ filtering, reinitialization via `ax_NS8390_reinit()`, and invalid platform-data combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ax88796.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bareudp.h -->
# sources/distributed-fs/ceph-client/include/net/bareudp.h

## Purpose

`bareudp.h` exposes a single helper for identifying Bare UDP tunnel netdevices by rtnl link kind.

## Important APIs, Types, and Functions

`netif_is_bareudp()` checks that `dev->rtnl_link_ops` exists and that its `kind` string equals `"bareudp"`.

## Control Flow

Callers use the helper in packet, offload, or configuration paths that need Bare UDP-specific behavior. The helper performs no locking itself; callers must hold or otherwise rely on valid netdevice lifetime.

## State and Persistence Behavior

No state is defined. It reads netdevice metadata registered by the Bare UDP rtnl link implementation.

## Dependencies and Integration Points

The header depends on `netdevice.h`, basic types, and rtnetlink link operations. It integrates with Bare UDP tunnel devices and generic networking code that branches by netdevice kind.

## Risks and Edge Cases

String-based kind checks are simple but depend on stable rtnl link naming. `rtnl_link_ops` can be `NULL` for ordinary devices; the helper handles that. Lifetime and locking are external to the helper.

## Test Signals

Check true results for Bare UDP devices, false results for ordinary devices and devices with `NULL` link ops, behavior during device unregister paths, and callers that need RTNL or RCU protection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bareudp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/bluetooth.h -->
# sources/distributed-fs/ceph-client/include/net/bluetooth/bluetooth.h

## Purpose

`bluetooth.h` is the common in-kernel Bluetooth header for protocol numbers, socket options, address types, logging helpers, common socket state, skb control blocks, skb allocation/send helpers, and subsystem initialization entry points.

## Important APIs, Types, and Functions

The header defines AF/PF Bluetooth values, Bluetooth protocol numbers (`BTPROTO_L2CAP`, `BTPROTO_HCI`, `BTPROTO_SCO`, `BTPROTO_ISO`, and others), socket options for security, deferred setup, flushable traffic, power, channel policy, voice, MTU, PHY, mode, packet status, ISO QoS, codec selection, ISO BASE, and packet sequence numbers. It defines ISO QoS structures for unicast and broadcast, codec capability layouts, `enum bt_sock_state`, `bdaddr_t`, address type helpers, and address copy/compare/swap helpers.

`struct bt_sock` embeds `struct sock` and adds accept queue, parent pointer, flags, and skb metadata callbacks. `struct bt_skb_cb` overlays `skb->cb` with packet type, activity/status/sequence metadata, and protocol-specific L2CAP/HCI/MGMT/control data. Helpers allocate Bluetooth skbs with `BT_SKB_RESERVE`, copy sendmsg payloads into one skb or a fragment list, convert Bluetooth status/errno values, manage HCI socket flags, initialize Bluetooth sockets/sysfs/procfs/debugfs, and initialize or stub L2CAP/SCO/ISO/MGMT subsystems depending on configuration.

## Control Flow

Bluetooth protocol modules register socket families with `bt_sock_register()`, allocate sockets through `bt_sock_alloc()`, and share recvmsg/poll/ioctl/wait helpers. Send paths use `bt_skb_sendmsg()` or `bt_skb_sendmmsg()` to reserve protocol headroom, enforce MTU chunking, copy from the userspace iterator, and attach socket priority. Accepting protocols use `bt_accept_enqueue()`, `bt_accept_unlink()`, and `bt_accept_dequeue()`. Subsystem init functions bring up HCI socket, L2CAP, SCO, ISO, MGMT, sysfs, and procfs pieces.

## State and Persistence Behavior

There is no durable storage. Runtime state lives in Bluetooth sockets, skb control blocks, accept queues, proc/debugfs/sysfs registrations, and protocol subsystem globals. Address and QoS structures are ABI data passed between kernel and userspace.

## Dependencies and Integration Points

The header depends on Linux sockets, sk_buffs, poll, seq_file, ethtool timestamp reporting, optional debug support, and Bluetooth HCI/L2CAP/SCO/ISO/MGMT modules. It is included widely by Bluetooth core, socket protocols, monitor/control code, and drivers.

## Risks and Edge Cases

`bt_skb_sendmmsg()` can return the first skb even if later fragment allocation fails, leaving partial data semantics to callers. `bt_skb_cb` shares limited skb control space; all protocols must respect the overlay. Address type validation distinguishes only BR/EDR, LE public, and LE random. Flexible-array ABI structs need strict length validation in socket option handlers. Conditional SCO/ISO stubs must free skbs and return clear errors when features are disabled.

## Test Signals

Test socket option ABI sizes, address type validation, sendmsg and multi-fragment send paths, shutdown/error handling in `bt_skb_send_alloc()`, accept queue operations, skb control block preservation through HCI/L2CAP paths, debug logging enablement, subsystem init/cleanup under `CONFIG_BT_BREDR` and `CONFIG_BT_LE`, and proc/sysfs/debugfs registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/bluetooth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/coredump.h -->
# sources/distributed-fs/ceph-client/include/net/bluetooth/coredump.h

## Purpose

`coredump.h` defines Bluetooth HCI device firmware/controller devcoredump state and the optional APIs drivers use to collect, append, complete, abort, and time out dumps.

## Important APIs, Types, and Functions

`struct hci_devcoredump` tracks support, state (`IDLE`, `ACTIVE`, `DONE`, `ABORT`, `TIMEOUT`), timeout, allocated dump buffer pointers, skb dump queue, work items, and driver callbacks for triggering dump collection, building a dump header, and notifying state changes. With `CONFIG_DEV_COREDUMP`, exported functions include reset, RX work, timeout work, register, init allocation, append skb, append repeated pattern, complete, and abort. Without devcoredump support, inline stubs return `-EOPNOTSUPP` or no-op.

## Control Flow

Drivers register callbacks, initialize a dump buffer, append dump fragments into the buffer via queued skb processing, and call complete or abort. Timeout work transitions a stuck collection to timeout. State-change notifications let drivers synchronize firmware dump mode with the core.

## State and Persistence Behavior

Dump state is per `hci_dev` in memory. The final devcoredump may be exposed through the kernel devcoredump mechanism, but this header stores only transient collection buffers and workqueue state. Timeout defaults to ten seconds.

## Dependencies and Integration Points

The header depends on HCI device definitions, sk_buffs, workqueues, delayed work, and `CONFIG_DEV_COREDUMP`. It integrates with Bluetooth HCI drivers and the generic devcoredump subsystem.

## Risks and Edge Cases

Buffer pointer arithmetic (`head`, `tail`, `end`) must remain bounded by `alloc_size`. Dump fragments arriving after abort/timeout need safe rejection. Drivers must handle `-EOPNOTSUPP` when devcoredump is disabled. Work cancellation during device unregister is critical to avoid accessing freed `hci_dev`.

## Test Signals

Test successful dump registration/init/append/complete, append overflow, append pattern lengths, abort during active collection, timeout path, reset after completion, unregister with pending dump work, and disabled-configuration stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/coredump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/hci.h -->
# sources/distributed-fs/ceph-client/include/net/bluetooth/hci.h

## Purpose

`hci.h` is the primary Bluetooth Host Controller Interface wire-format and constants header. It describes controller/device events, bus types, quirks, device/socket/controller flags, timeouts, packet types, command opcodes and parameters, event payloads, packet headers, handle packing helpers, and LE/ISO/channel-sounding structures.

## Important APIs, Types, and Functions

The file defines maximum HCI frame sizes, link key size, HCI device and notify events, bus identifiers, a large quirk enum used by drivers before or during registration, device/socket/controller flag enums, standard timeouts, HCI packet types, ACL/SCO/eSCO/ISO packet flags, link types, LMP and LE feature bits, link policy/mode/security constants, EIR/advertising data types, HCI error codes, and invalid sentinel values.

Command definitions include BR/EDR inquiry/connection/authentication, local host/controller setup, buffer/codec queries, LE advertising/scanning/connection/privacy/data-length/PHY commands, extended advertising and periodic advertising, PAST, ISO CIG/CIS/BIG/BIS setup, ISO data path setup, LE host features, LE all-feature pages, and LE Channel Sounding commands. Event structures cover command complete/status, connection, disconnection, authentication/encryption, inquiry, remote feature/name/version, LE meta events, extended advertising reports, periodic advertising, CIS/BIG events, channel sounding events, vendor events, and stack-internal events. Inline helpers return packet headers from skbs, pack/unpack opcodes and handles, pack/unpack ISO flags and data lengths, and encode 24-bit little-endian values.

## Control Flow

HCI core and drivers build command skbs using the opcode and command-parameter structs, submit them to the controller, and parse events using the matching event structs. Event handling updates `hci_dev` and `hci_conn` state declared in `hci_core.h`, feeds upper protocols, completes synchronous requests, and notifies monitor/control sockets. The quirk and feature constants gate which commands are sent during setup, scan, advertising, connection, security, and ISO flows.

## State and Persistence Behavior

This header declares no storage. The constants and packed structs define runtime state exchanged over the HCI transport. Feature bits, quirks, command masks, and event payloads become persistent only as fields in `struct hci_dev` or `struct hci_conn` in other files; controller settings may persist in hardware depending on the command and device firmware.

## Dependencies and Integration Points

It depends on Bluetooth address types from `bluetooth.h` and Linux integer/endian annotations. It is consumed by HCI core, management, sockets, monitor, drivers, SCO/L2CAP/ISO, and users of raw HCI packets. It must match the Bluetooth Core Specification ABI exactly.

## Risks and Edge Cases

Packed structs with flexible arrays require exact skb length validation before access. Some event structs contain zero-length arrays for variable channel-sounding reports; parser code must compute offsets manually and defensively. Quirk flags are behavior-changing and often must be set before `hci_register_dev()`. Feature/command mask helpers elsewhere assume bytes and bit positions from this header are correct. Endian conversion is explicit through `__le*`; direct host-order use would corrupt wire data.

## Test Signals

Test command serialization sizes and endianness, event parser bounds for every flexible-array payload, opcode and handle pack/unpack round trips, LE extended advertising and periodic advertising report parsing, ISO data flag/length decoding, Channel Sounding variable reports, quirk-gated setup command selection, raw HCI socket monitor output, and interoperability against known controller traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/hci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/hci_core.h -->
# sources/distributed-fs/ceph-client/include/net/bluetooth/hci_core.h

## Purpose

`hci_core.h` defines the Bluetooth HCI core object model and internal APIs: devices, connections, channels, discovery cache, keys, advertising instances, monitoring, command queues, management hooks, capability macros, protocol callbacks, and socket/monitor send paths.

## Important APIs, Types, and Functions

Core data types include `struct hci_dev`, `struct hci_conn`, `struct hci_chan`, `struct hci_conn_params`, discovery/inquiry entries, security key lists (`link_key`, `smp_ltk`, `smp_irk`, `smp_csrk`, blocked keys, OOB data), advertising instances, advertising monitors, codec lists, and connection hash counters. `struct hci_dev` is the large per-controller state object: identity addresses, features, command masks, defaults, buffers and MTUs, workqueues, command/sync queues, rx/raw/cmd queues, request wait state, discovery/suspend/advertising/privacy state, connection hash, key/accept/resolving lists, stats, devcoredump, rfkill, debugfs, driver callbacks, and optional MSFT/AOSP/LED data.

Inline helpers initialize/clear discovery filters, add/delete/list RCU connection hash entries, lookup connections by handle/address/role/ISO identifiers/PA/BIG state, manage device and connection references, schedule delayed disconnects when connection holds drop, dispatch connect/disconnect/security/key/role callbacks, classify RPAs and identity addresses, validate LE connection parameters, and map HCI link types to L2CAP/SCO/ISO protocol indications. Exported prototypes cover device allocation/registration/open/close/reset, frame receive, ioctls, inquiry cache, key and address-list management, connection creation/security/PHY/update/abort, advertising instances and monitors, HCI command/data send, management channel registration, sysfs, and MGMT event reporting.

## Control Flow

Driver probe allocates and fills `hci_dev`, sets quirks/callbacks, and registers it. Open/setup populates command masks, features, addresses, MTUs, keys, advertising defaults, and scan parameters, usually through synchronous command helpers. Incoming transport frames enter `hci_recv_frame()` and are dispatched by packet type to event, ACL, SCO, or ISO handling. Event handling updates device/connection state, completes commands, updates discovery cache, resolves security transitions, and calls upper protocol indications. Connection creation uses the hash/list helpers, delayed works for timeouts/idle/disconnect, and protocol callbacks into L2CAP/SCO/ISO. Management sockets observe settings, discovery, pairing, key, advertising, suspend, and monitor events through the many `mgmt_*` hooks.

## State and Persistence Behavior

All state is in kernel memory attached to the HCI device, connection devices, queues, lists, delayed work, and registered callbacks. Link keys, LTKs, IRKs, OOB data, connection parameters, and advertising instances are represented in memory here and may be persisted by userspace management policy, but this header itself provides only runtime containers and notifications. RCU protects connection hash and key-like lists; device/connection lifetimes use `struct device` refs plus separate connection hold counts.

## Dependencies and Integration Points

The header depends on IDR/IDA, LEDs, RCU/SRCU, spinlocks, mutexes, workqueues, rfkill, sk_buffs, `hci.h`, driver command extensions, sync command helpers, HCI sockets, and devcoredump. It integrates with Bluetooth drivers, HCI sockets, MGMT, L2CAP, SCO, ISO, sysfs, debugfs, rfkill, suspend notifiers, and optional MSFT/AOSP extensions.

## Risks and Edge Cases

Several inline lookup helpers return pointers found under RCU after dropping the read lock; callers must ensure object lifetime through surrounding locking/ref rules. The comment around `hci_conn_get()` versus `hci_conn_hold()` documents a subtle split between object lifetime and physical connection lifetime, including a FIXME about hold counts dropping below zero. Many capability macros trust command/feature array offsets. Workqueue cancellation during unregister, suspend, and close is high risk. LE/ISO lookup helpers must distinguish listen, pending, PA, BIS, CIG, and BIG states correctly. Connection parameter validation prevents invalid controller commands but must remain aligned with Bluetooth timing rules.

## Test Signals

Test device register/open/setup/close/unregister, receive dispatch for event/ACL/SCO/ISO/diag, command timeout and sync cancellation, connection hash add/delete/lookups under RCU, key/IRK/LTK/OOB list add/remove/clear, LE connection parameter validation, discovery cache aging/filtering/name resolution, advertising instance and monitor lifecycle, suspend/resume notifier states, rfkill, devcoredump setup, management notifications, and disabled SCO/ISO configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/hci_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/hci_drv.h -->
# sources/distributed-fs/ceph-client/include/net/bluetooth/hci_drv.h

## Purpose

`hci_drv.h` defines an HCI driver-private command/event channel layered on Bluetooth HCI packet handling, allowing common and driver-specific commands to be sent to HCI drivers.

## Important APIs, Types, and Functions

`struct hci_drv_cmd_hdr` and `struct hci_drv_ev_hdr` carry little-endian opcode and length. Standard driver events include command status and command complete, with status values for success, unspecified error, unknown command, and invalid parameters. `HCI_DRV_OP_READ_INFO` returns driver name plus supported command opcodes in `struct hci_drv_rp_read_info`. Driver-specific commands are grouped under `HCI_DRV_OGF_DRIVER_SPECIFIC`. The processing API includes `hci_drv_cmd_status()`, `hci_drv_cmd_complete()`, and `hci_drv_process_cmd()`. `struct hci_drv_handler` binds a handler function to expected data length, and `struct hci_drv` holds common and driver-specific handler tables.

## Control Flow

An HCI driver packet is parsed by `hci_drv_process_cmd()`, routed to either common or specific handler tables by opcode group, length-checked, executed, and completed through status or complete events back to the HCI device path.

## State and Persistence Behavior

No persistent state is defined. Handler tables are static driver data referenced by `struct hci_dev`. Responses are transient skbs/events.

## Dependencies and Integration Points

The header depends on Bluetooth common and HCI headers. It integrates with `struct hci_dev` through the `hci_drv` pointer in `hci_core.h`, and with monitor/socket paths through HCI driver packet types.

## Risks and Edge Cases

Opcode namespaces must not collide between common and driver-specific handlers. Length validation relies on accurate `data_len` values. Flexible supported-command arrays in `READ_INFO` require careful allocation. Unknown commands must return defined driver status rather than leaking kernel errors directly.

## Test Signals

Test common `READ_INFO`, unsupported opcodes, invalid lengths, driver-specific routing, command status versus complete emission, long driver names at the 32-byte limit, and monitor visibility of HCI driver packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/hci_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/hci_mon.h -->
# sources/distributed-fs/ceph-client/include/net/bluetooth/hci_mon.h

## Purpose

`hci_mon.h` defines the Bluetooth HCI monitor record header and monitor opcode payloads used by the kernel monitor channel and tools such as `btmon`.

## Important APIs, Types, and Functions

`struct hci_mon_hdr` is a packed 6-byte header containing opcode, controller index, and payload length. Monitor opcodes cover controller index lifecycle, command/event packets, ACL/SCO/ISO TX/RX, open/close, index info, vendor diagnostics, system notes, user logging, control channel traffic, and HCI driver TX/RX. `struct hci_mon_new_index` carries controller type, bus, address, and short name; `struct hci_mon_index_info` carries address and manufacturer.

## Control Flow

HCI core emits monitor records when controllers appear/disappear, sockets open/close, commands/events/data pass through HCI, and diagnostic/control/user logging records are generated. Consumers parse `hci_mon_hdr` then dispatch by opcode to the corresponding fixed or packet payload.

## State and Persistence Behavior

No persistent state is stored here. Monitor packets are transient observations of HCI activity.

## Dependencies and Integration Points

The header depends on Bluetooth address types and endian annotations. It integrates with HCI monitor sockets, control sockets, driver diagnostic packet paths, and userspace tracing tools.

## Risks and Edge Cases

Payload length must be validated against the monitor opcode before parsing. The name field is marked `__nonstring`, so consumers must not assume NUL termination. New opcodes require userspace tooling updates.

## Test Signals

Validate monitor header sizes, new/delete index records, packet direction opcodes for ACL/SCO/ISO/driver traffic, control channel open/close/command/event records, non-NUL names, and malformed short monitor frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/hci_mon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/hci_sock.h -->
# sources/distributed-fs/ceph-client/include/net/bluetooth/hci_sock.h

## Purpose

`hci_sock.h` defines the userspace-facing HCI socket ABI: socket options, control-message flags, sockaddr layout, HCI channels, packet filters, ioctls, device/connection statistics, and inquiry request structures.

## Important APIs, Types, and Functions

Socket options include `HCI_DATA_DIR`, `HCI_FILTER`, and `HCI_TIME_STAMP`, with CMSG flags for direction and timestamps. `struct sockaddr_hci` selects HCI device and channel (`RAW`, `USER`, `MONITOR`, `CONTROL`, `LOGGING`), with `HCI_DEV_NONE` as wildcard/no-device. `struct hci_filter` and `struct hci_ufilter` contain packet type masks, event masks, and opcode filters. Ioctl constants cover device up/down/reset/stat, device/connection/auth queries, raw/scan/auth/encrypt/packet/link/MTU settings, block/unblock address, and inquiry. Request/response structs model device stats/info, connection info/list, authentication info, and inquiry parameters.

## Control Flow

HCI sockets bind to a device/channel through `sockaddr_hci`, optionally install filters, and send/receive raw or channel-specific HCI traffic. Ioctl handlers in HCI core use these structures to control controller state, query devices/connections, adjust legacy settings, and trigger inquiry.

## State and Persistence Behavior

The header itself stores no state. Socket filters and channel bindings are per-socket runtime state; device stats and flags are snapshots of `hci_dev` state. Ioctls can change controller runtime configuration but do not directly persist to disk.

## Dependencies and Integration Points

It depends on Bluetooth address types and Linux ioctl encoding. It integrates with AF_BLUETOOTH/HCI sockets, HCI core device management, monitor/control/logging channels, and legacy userspace tools.

## Risks and Edge Cases

Filter masks differ between kernel `unsigned long` and fixed-width userspace filter structures, so compat handling matters. Flexible arrays in list/query structs require strict user length validation. Many ioctls are privileged or legacy and can race with device unregister/open/close. Channel semantics differ significantly; raw/user/control/monitor/logging must enforce permissions and isolation.

## Test Signals

Test bind to each channel, wildcard device behavior, filter mask conversion including compat, timestamp/direction CMSG delivery, every ioctl with invalid and valid userspace buffers, device unregister during socket operations, inquiry cache flush flag, block/unblock address, and permission checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/hci_sock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/hci_sync.h -->
# sources/distributed-fs/ceph-client/include/net/bluetooth/hci_sync.h

## Purpose

`hci_sync.h` declares the synchronous HCI command/request framework and higher-level synchronous Bluetooth state-update helpers used by HCI core and management code.

## Important APIs, Types, and Functions

`struct hci_request` holds an HCI device, a command queue, and an error accumulator. `struct hci_cmd_sync_work_entry` queues a work function, data pointer, optional destroy callback, and list node. Sync command APIs allocate and send commands, wait for command complete/status or a specific event, optionally associate a socket, and return skbs or status. Queue APIs initialize/clear/cancel sync state, submit/queue/run work entries, find/cancel/dequeue entries, and provide once-only variants. Higher-level helpers cover EIR/class/name/SSP, random address selection, advertising data and instances, periodic advertising, passive/active scan updates, RSSI/TX power/clock reads, SC/LE host support, reset/open/close/powered transitions, discoverable/connectable/discovery, suspend/resume, connection abort/connect/cancel/update, CIS/BIG/PA operations, PAST, remote LE features, ACL packet type changes, and LE PHY changes.

## Control Flow

Callers serialize sync command work with `hdev->req_lock` and command-sync workqueues. A sync helper builds one or more HCI commands, waits for completion or status with timeout, and updates core state through the event path. Comments explicitly warn that `*_sync` functions must not be called with `hdev->lock` held because received events may try to acquire that lock, causing deadlock.

## State and Persistence Behavior

No persistent storage is declared. Runtime state is `hci_dev` request queues, wait queues, sync work lists, command skbs, status/result fields, and command timeout behavior. Operations can change controller configuration such as advertising, scanning, power, and connection state.

## Dependencies and Integration Points

The header depends on HCI core/device structures, sk_buffs, workqueues, sockets, and HCI command/event definitions. It integrates with management operations, setup/open/close, LE advertising/scanning, privacy, ISO, and connection management.

## Risks and Edge Cases

Deadlock risk is explicit if sync calls run while holding `hdev->lock`. Queue-once semantics depend on matching function/data/destroy triples. Cancellation must invoke destroy callbacks exactly once with a meaningful error. Timeout handling must free returned skbs and leave command state consistent. Socket-associated commands need correct attribution and cleanup if the socket closes.

## Test Signals

Test sync command success/status/error/timeout, expected-event matching, cancellation and cancel-sync paths, queue/run/once/dequeue behavior, destroy callback invocation, lockdep for `hdev->lock` misuse, advertising/scan/discovery helpers, suspend/resume, connection abort/connect/update, ISO CIG/BIG/PA helpers, and socket-associated command cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/hci_sync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/iso.h -->
# sources/distributed-fs/ceph-client/include/net/bluetooth/iso.h

## Purpose

`iso.h` defines Bluetooth ISO socket defaults and address structures for connected isochronous and broadcast isochronous sockets.

## Important APIs, Types, and Functions

`ISO_DEFAULT_MTU` is 251 and `ISO_MAX_NUM_BIS` is 31. `struct sockaddr_iso_bc` holds broadcast address, address type, advertising SID, number of BIS indexes, and the BIS list. `struct sockaddr_iso` contains socket family, peer address, address type, and an optional flexible broadcast address extension.

## Control Flow

ISO socket code receives these sockaddr structures during bind/connect/listen-style operations, validates address type and broadcast fields, and maps them to HCI ISO/CIS/BIS connection setup through HCI core.

## State and Persistence Behavior

No state is stored here. Address structures are transient ABI inputs/outputs for sockets.

## Dependencies and Integration Points

The header depends on Bluetooth address definitions and integrates with ISO socket code, HCI ISO connection management, CIS/BIS setup, and broadcast synchronization.

## Risks and Edge Cases

The flexible `iso_bc` extension requires careful sockaddr length validation. `bc_num_bis` must not exceed `ISO_MAX_NUM_BIS`. Broadcast and unicast address semantics differ and must not be conflated. Default MTU must stay aligned with HCI ISO payload limits.

## Test Signals

Test unicast and broadcast sockaddr lengths, maximum and zero BIS counts, invalid address types, SID handling, default MTU use, and mapping to HCI CIS/BIS connection helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/iso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/l2cap.h -->
# sources/distributed-fs/ceph-client/include/net/bluetooth/l2cap.h

## Purpose

`l2cap.h` defines the Bluetooth L2CAP protocol constants, wire structures, channel/connection state, retransmission/flow-control state machines, socket private data, timer helpers, and public L2CAP core APIs.

## Important APIs, Types, and Functions

The header defines default MTUs, flush/ERTM/window/retransmission/monitor/ack/connect/info/move/security timeouts, socket address and options, link-mode bits, signaling command codes, feature masks, FCS options, fixed channels, control-field masks/shifts, supervisory/SAR values, rejection/result/status codes, PSM/CID ranges, configuration option structures, ERTM/streaming/LE/ext-flow modes, QoS/EFS data, LE credit-based and enhanced credit-based connection/reconfigure structures, and info/move/update messages.

`struct l2cap_chan` is the per-channel state object: HCI connection pointer, kref, nesting, state, source/destination addresses and CIDs, MTUs, mode/type/policy/security, configuration buffers/counters, FCS/window/retransmission/MPS/credit settings, receive availability, TX/RX state, config/connection flags, sequence numbers, SDU reassembly, remote/local flow specs, delayed timers, TX/SREJ/retransmission queues, global/connection lists, protocol private data, ops table, and mutex. `struct l2cap_ops` lets socket or fixed-channel users provide callbacks for new connections, receive, teardown, close, state changes, ready/defer/resume/suspend/shutdown, send timeout, peer PID, skb allocation, and filtering. `struct l2cap_conn` binds an HCI connection/channel to L2CAP-level MTU, feature/fixed-channel state, info timer, RX reassembly, TX ident allocator, pending RX work, SMP channel, channel list, users, lock, and kref.

Inline helpers manage channel locks, delayed timer hold/put pairing, sequence arithmetic, and no-op/default ops. Exported APIs initialize sockets, identify L2CAP sockets, defer responses, add PSM/SCID, create/close/connect/reconfigure/send channels, mark busy/RX availability, check security, initialize ERTM, add/list/delete channels, manage connection refs, and register L2CAP users.

## Control Flow

L2CAP receives ACL data from HCI, reassembles L2CAP PDUs, dispatches signaling commands on fixed channels, creates/configures connection-oriented channels, and passes payloads to `l2cap_ops`. Connection setup negotiates PSM/CID, MTU, RFC mode, FCS, extended windows, EFS, and credit parameters before channels become ready. ERTM and streaming paths use TX/RX states, sequence numbers, SREJ/retransmission queues, and retrans/monitor/ack timers. LE credit-based channels track local/remote credits and can use enhanced credit-based multi-CID setup. Timer helpers intentionally hold channel refs while delayed work is pending.

## State and Persistence Behavior

All state is runtime-only in L2CAP channels, HCI-backed L2CAP connections, socket private data, queues, delayed work, sequence lists, and registered users. Channel refs use `kref`; timer scheduling adds/releases references to keep channels alive. No file-backed persistence exists.

## Dependencies and Integration Points

The header depends on Bluetooth common/HCI types, sk_buffs, atomics, unaligned helpers, mutexes, krefs, IDA, workqueues, and sockets. It integrates with HCI ACL receive/send, SMP, ATT, RFCOMM, fixed channels, LE credit sockets, BR/EDR sockets, and Bluetooth management/security.

## Risks and Edge Cases

Timer ref pairing is subtle: setting a timer that was not already pending holds the channel, and clearing a pending timer drops it. Sequence arithmetic depends on `tx_win_max + 1` and must match normal versus extended control fields. Flexible arrays in enhanced credit structures require length checks and maximum CID enforcement. `__set_ack_timer(c)` references `chan->ack_timer` in the macro body, so call sites must provide a visible `chan` identifier despite the `c` parameter. ERTM/SREJ/retransmission state has many race-prone transitions with local/remote busy flags.

## Test Signals

Test BR/EDR and LE connect/config/disconnect flows, fixed channels, dynamic PSM and SCID allocation, MTU/MPS/window/FCS negotiation, ERTM retransmission and SREJ behavior, streaming mode, LE credits and enhanced credit multi-CID limits, reconfigure validation, timer hold/put balance, busy/RX availability backpressure, security checks, HCI disconnect cleanup, malformed signaling PDUs, and disabled/forced ERTM or ECRED module parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/l2cap.h -->
