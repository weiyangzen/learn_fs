# subset-b-005950 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tcp_ecn.h -->
# sources/distributed-fs/ceph-client/include/net/tcp_ecn.h

## Purpose

`tcp_ecn.h` centralizes TCP ECN negotiation and feedback helpers, including classic RFC3168 ECN and Accurate ECN (AccECN). It is used by TCP input/output paths to decide what flags to put on SYN/SYN-ACK/data ACKs, how to validate feedback from peers and middleboxes, and how to maintain per-connection ECN counters in `struct tcp_sock`.

## Important APIs, types, and functions

The public configuration enums are `enum tcp_ecn_mode` and `enum tcp_accecn_option`. Important helpers include `tcp_ecn_send_syn()`, `tcp_ecn_rcv_syn()`, `tcp_ecn_send_synack()`, `tcp_ecn_make_synack()`, `tcp_ecn_rcv_synack()`, `tcp_ecn_rcv_ecn_echo()`, `tcp_ecn_queue_cwr()`, `tcp_ecn_accept_cwr()`, `tcp_accecn_set_ace()`, `tcp_ecn_received_counters()`, `tcp_accecn_option_init()`, `tcp_update_ecn_bytes()`, and `tcp_accecn_option_beacon_check()`. The Accurate ECN helpers encode/decode the ACE field from TCP `AE/CWR/ECE` bits and map 24-bit option counters to ECT(0), ECT(1), and CE byte counters.

## Control flow

Outbound active opens call `tcp_ecn_send_syn()` to consult `sysctl_tcp_ecn`, congestion-control requirements, BPF congestion-control ECN needs, and route ECN feature hints. If AccECN is requested, it sets `TCPHDR_AE`, enters pending mode, and records the transmitted SYN ECN codepoint. Passive opens call `tcp_ecn_rcv_syn()` to downgrade to classic ECN or accept AccECN based on the ACE bits and received IP ECN field. SYN-ACK construction uses `tcp_accecn_reflector_flags()` or classic ECE, while SYN-ACK reception selects disabled, RFC3168, or AccECN mode from the returned ACE field and fallback policy. After negotiation, receive paths call `tcp_ecn_received_counters()` to update CE packet counters, byte counters, ACK urgency, and AccECN option demand; transmit paths call `tcp_accecn_set_ace()` to reflect pending CE counts.

## State and persistence behavior

The header mutates transient connection state in `struct tcp_sock`: `ecn_flags`, `syn_ect_snt`, `syn_ect_rcv`, `received_ce`, `received_ce_pending`, `received_ecn_bytes[]`, `delivered_ecn_bytes[]`, `accecn_minlen`, `accecn_opt_demand`, `saw_accecn_opt`, `accecn_fail_mode`, timestamps, and previous ECN field tracking. It also sets ACK scheduling bits in `inet_connection_sock`. No persistent storage is owned here; state lasts for the TCP connection and is initialized/reset through helpers such as `tcp_accecn_init_counters()`.

## Dependencies and integration points

It depends on TCP core structures, SKB control blocks, `inet_ecn.h`, bitfield helpers, sysctls under `sock_net(sk)->ipv4`, congestion-control hooks, BPF congestion-control hooks, route features, and TCP option parsing. It integrates with handshake creation, SYN cookie validation (`cookie_accecn_ok()`), ACK generation, CWR handling, receive counter accounting, and option emission policy.

## Risks and test signals

Risks include invalid ACE interpretation during handshake fallback, wrong ECN transition validation after middlebox remarking, 24-bit counter wrap mistakes, off-by-one indexing into ECN byte arrays, excessive or missing ACK forcing on ECN edges, and accidentally setting CWR in AccECN mode. Tests should exercise active/passive opens for all `sysctl_tcp_ecn` modes, AccECN downgrade to RFC3168 and disabled, CE-on-SYN/SYN-ACK accounting, option zeroing detection, 24-bit counter wrap, CWR demand/withdrawal, and builds with congestion-control/BPF ECN requirements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tcp_ecn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tcp_states.h -->
# sources/distributed-fs/ceph-client/include/net/tcp_states.h

## Purpose

`tcp_states.h` defines the numeric values stored in TCP sockets' `sk_state` field and the matching bitmask constants used by TCP, inet diagnostics, polling, timers, and state tests.

## Important APIs, types, and functions

The anonymous state enum declares `TCP_ESTABLISHED`, `TCP_SYN_SENT`, `TCP_SYN_RECV`, `TCP_FIN_WAIT1`, `TCP_FIN_WAIT2`, `TCP_TIME_WAIT`, `TCP_CLOSE`, `TCP_CLOSE_WAIT`, `TCP_LAST_ACK`, `TCP_LISTEN`, `TCP_CLOSING`, `TCP_NEW_SYN_RECV`, `TCP_BOUND_INACTIVE`, and `TCP_MAX_STATES`. It also defines `TCP_STATE_MASK`, `TCP_ACTION_FIN`, and `TCPF_*` bitmask constants for each state.

## Control flow

There are no functions. The control-flow contract is that TCP state-machine code writes one of these numeric states to `sk_state`, while readers compare state values directly or use the `TCPF_*` masks to test allowed sets of states.

## State and persistence behavior

The header owns no state. Its numeric assignments are ABI-like within the kernel: changing them affects socket state tests, diagnostics, tracepoints, and any logic storing state masks.

## Dependencies and integration points

It is included by TCP, inet, time-wait, request-sock, diagnostics, and networking code that needs symbolic TCP state names. `TCP_BOUND_INACTIVE` is a pseudo-state for inet diagnostics rather than a normal TCP wire state.

## Risks and test signals

Risks are mostly compatibility and bitmask correctness. Reordering states or adding states without updating masks can break diagnostics and state transitions. Tests should cover TCP connection lifecycle states, inet_diag state reporting, mask-based filters, time-wait handling, and compile-time consumers expecting `TCP_MAX_STATES` at the end.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tcp_states.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tcx.h -->
# sources/distributed-fs/ceph-client/include/net/tcx.h

## Purpose

`tcx.h` defines the TCX attachment layer for BPF programs at traffic-control ingress and egress. It bridges netdevice TC hooks, `bpf_mprog` multi-program bundles, mini qdisc presence, and BPF link/program attach/query operations.

## Important APIs, types, and functions

Key types are `struct tcx_entry`, containing an RCU mini qdisc pointer, `bpf_mprog_bundle`, active miniq count, and RCU head, and `struct tcx_link`, wrapping `struct bpf_link` plus the target netdevice. Helpers include `tcx_set_ingress()`, `tcx_entry()`, `tcx_link()`, `tcx_entry_update()`, `tcx_entry_fetch()`, `tcx_entry_create()`, `tcx_entry_free()`, `tcx_entry_fetch_or_create()`, `tcx_skeys_inc()`/`dec()`, `tcx_miniq_inc()`/`dec()`, `tcx_entry_is_active()`, and `tcx_action_code()`. BPF syscall-facing declarations include `tcx_prog_attach()`, `tcx_link_attach()`, `tcx_prog_detach()`, `tcx_prog_query()`, and `tcx_uninstall()`.

## Control flow

Under `CONFIG_NET_XGRESS`, callers hold RTNL, fetch or create a `bpf_mprog_entry`, attach/detach programs through BPF syscall handlers, then publish ingress or egress entries with `rcu_assign_pointer()`. Updates synchronize after a/b entry swaps with `synchronize_rcu()`. On packet execution, TCX maps program return codes to `TCX_PASS`, `TCX_DROP`, `TCX_REDIRECT`, or `TCX_NEXT`; `TCX_PASS` also propagates `tc_classid` into `skb->tc_index`.

## State and persistence behavior

Persistent state lives on `struct net_device` RCU pointers `tcx_ingress` and `tcx_egress`, in the `bpf_mprog_bundle`, and in mini qdisc active counts. Global ingress/egress static-key accounting is adjusted with `tcx_skeys_inc()`/`dec()`. Entries are freed by RCU and must remain stable for readers during datapath execution.

## Dependencies and integration points

It depends on BPF core, BPF links, multi-program bundles, `sch_generic.h`, netdevice TC ingress/egress queues, RTNL locking, and optional `CONFIG_BPF_SYSCALL`. Without the needed config, attach/query helpers return `-EINVAL` and uninstall is a no-op.

## Risks and test signals

Risks include publishing entries without RTNL, freeing before RCU readers finish, mismatched miniq reference counts, static-key leaks, and incorrect action-code handling. Tests should cover attach/detach/query for ingress and egress, link lifetime, program chain replacement under traffic, miniq coexistence, disabled-config stubs, and BPF return-code mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tcx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/timewait_sock.h -->
# sources/distributed-fs/ceph-client/include/net/timewait_sock.h

## Purpose

`timewait_sock.h` declares the minimal allocator contract for protocol-specific time-wait sockets. It lets protocols describe the slab cache used for compact time-wait socket objects.

## Important APIs, types, and functions

The only defined type is `struct timewait_sock_ops`, with `twsk_slab`, `twsk_slab_name`, and `twsk_obj_size`. There are no functions in this header.

## Control flow

Protocol code supplies a `timewait_sock_ops` instance to time-wait allocation/teardown code elsewhere. The common time-wait infrastructure uses the slab cache and object size to allocate and free per-protocol time-wait sockets.

## State and persistence behavior

The header owns no state. The referenced `kmem_cache` persists while the protocol is registered; individual time-wait objects persist until their timers expire or are reclaimed.

## Dependencies and integration points

It includes slab, bug, and socket infrastructure. It integrates with TCP/DCCP-style time-wait implementations and generic socket lifetime code.

## Risks and test signals

Risks include an object size smaller than the concrete time-wait structure, stale slab pointers during protocol unload, and mismatched slab names in diagnostics. Tests should cover protocol init/exit, time-wait allocation/free, timer expiry, and memory-debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/timewait_sock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tipc.h -->
# sources/distributed-fs/ceph-client/include/net/tipc.h

## Purpose

`tipc.h` defines a small TIPC header helper for receive packet steering. It extracts an RPS key from a basic TIPC header, using source node identity for normal traffic and randomization for keepalive probe traffic.

## Important APIs, types, and functions

The file defines `KEEPALIVE_MSG_MASK`, `struct tipc_basic_hdr` containing four big-endian words, and `tipc_hdr_rps_key()`. The helper inspects word 0 and returns word 3 unless the message looks like a keepalive.

## Control flow

Receive-side steering code calls `tipc_hdr_rps_key()` with a parsed TIPC basic header. For normal messages the source node field gives stable flow affinity. For link keepalive/probe messages the helper generates random bytes so probes and replies are spread across CPUs instead of concentrating on a single source key.

## State and persistence behavior

The header owns no persistent state. Random keepalive keys are generated per call and do not persist.

## Dependencies and integration points

It depends on `linux/random.h`, endian conversion, and TIPC message layout. It integrates with network receive hashing/RPS and TIPC link protocol message handling.

## Risks and test signals

Risks include incorrect mask constants causing normal traffic to be randomized or keepalives to be pinned, wrong endian handling, and assuming the four-word header is present before calling. Tests should cover normal message keys, keepalive probe/probe-reply recognition, CPU distribution for keepalives, and short-packet validation in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tls.h -->
# sources/distributed-fs/ceph-client/include/net/tls.h

## Purpose

`tls.h` is the core kernel TLS (kTLS) internal API. It defines TLS record sizing, software TX/RX contexts, device offload TX/RX contexts, cipher/protocol state, socket ULP context storage, driver offload callbacks, resync protocols, and helper accessors used by the TCP data path and TLS device drivers.

## Important APIs, types, and functions

Important constants include `TLS_MAX_PAYLOAD_SIZE`, `TLS_MIN_RECORD_SIZE_LIM`, `TLS_HEADER_SIZE`, `TLS_TAG_SIZE`, sequence/IV/salt sizes, and configuration values `TLS_BASE`, `TLS_SW`, `TLS_HW`, and `TLS_HW_RECORD`. Key types are `struct tls_sw_context_tx`, `struct tls_sw_context_rx`, `struct tls_strparser`, `struct tls_record_info`, `struct tls_offload_context_tx`, `struct tls_offload_context_rx`, `struct tls_context`, `struct tls_prot_info`, `union tls_crypto_context`, `struct tlsdev_ops`, and `struct tls_offload_resync_async`. Helpers expose context access (`tls_get_ctx()`, `tls_sw_ctx_rx()`, `tls_offload_ctx_tx()`), feature checks (`tls_sw_has_ctx_tx()`/`rx()`, `tls_is_skb_tx_device_offloaded()`), driver-private state (`tls_driver_ctx()`), and RX/TX resync requests.

## Control flow

For software TLS, TX paths encrypt records through `aead_send`, manage `open_rec` and `tx_list`, and schedule delayed TX work. RX paths parse records through the TLS strparser, decrypt asynchronously when possible, queue decrypted data, and wake readers. For device offload, the core tracks record boundaries and calls driver operations to add/delete/resync TLS state. TX validation uses `sk_validate_xmit_skb` to decide whether to offload or fall back to software. RX offload resync is requested through atomic sequence/log fields so hardware and core can re-align after out-of-sync records.

## State and persistence behavior

Per-socket state persists in `inet_connection_sock.icsk_ulp_data` as `struct tls_context`. It carries protocol info, cipher contexts, TX/RX config, saved socket callbacks, crypto info, netdevice pointer, partially sent record state, flags, and reference count. Software contexts own crypto transforms, queues, pending counters, wait queues, and work items. Device contexts own record lists, driver-private state, netdev degradation/closure flags, and resync state. Lifetime is tied to the socket and RCU/refcount release.

## Dependencies and integration points

It depends on TCP, sockets, netdevice, net namespaces, strparser, crypto AEAD, UAPI TLS structures, RCU, workqueues, mutexes, and optional `CONFIG_TLS_DEVICE`. It integrates with TCP ULP setup, sendmsg/recvmsg/sendfile, socket destruction, netdevice TLS offload callbacks, hardware resync, and BPF/diagnostic readers of ULP data.

## Risks and test signals

Risks include stale ULP context reads, wrong crypto-info sizing, asynchronous encrypt/decrypt completion races, netdevice down transitions leaving `TLS_HW` degraded state, record-list lifetime bugs, timestamp/sequence resync errors, and missing memory barriers around TX sync flags. Tests should exercise software TLS send/receive, async crypto, key update pending, partial records, device add/delete, netdev down/up fallback, RX resync modes, TX validation fallback, and builds with `CONFIG_TLS_DEVICE` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tls_prot.h -->
# sources/distributed-fs/ceph-client/include/net/tls_prot.h

## Purpose

`tls_prot.h` provides TLS protocol number definitions used by kernel TLS and related parsers. It mirrors IANA TLS content type, alert level, and alert description values in a kernel header.

## Important APIs, types, and functions

The header defines anonymous enums for record content types (`TLS_RECORD_TYPE_*`), alert levels (`TLS_ALERT_LEVEL_WARNING`, `TLS_ALERT_LEVEL_FATAL`), and alert descriptions such as `TLS_ALERT_DESC_CLOSE_NOTIFY`, `BAD_RECORD_MAC`, `RECORD_OVERFLOW`, `HANDSHAKE_FAILURE`, `PROTOCOL_VERSION`, `INTERNAL_ERROR`, and `NO_APPLICATION_PROTOCOL`.

## Control flow

There is no executable control flow. Consumers compare parsed TLS record or alert bytes against these symbolic constants when classifying TLS data or generating alerts.

## State and persistence behavior

The header owns no state. Numeric values are wire protocol ABI and must remain stable.

## Dependencies and integration points

It has no local includes. It integrates with kTLS record handling, TLS offload code, protocol parsers, and any code that needs TLS alert/content names without pulling in larger TLS internals.

## Risks and test signals

Risks include numeric mismatch with IANA assignments, missing alert values needed by parsers, and treating TLS constants as kernel-private. Tests should verify parsed record content types and alert descriptions against known TLS frames and compile users without broader TLS headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tls_prot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tls_toe.h -->
# sources/distributed-fs/ceph-client/include/net/tls_toe.h

## Purpose

`tls_toe.h` defines the registration and socket hook contract for inline TLS TCP offload engine devices. It is separate from the kTLS netdevice offload structures and focuses on TOE-style listen/hash/unhash integration.

## Important APIs, types, and functions

The main type is `struct tls_toe_device`, containing a device name, global device list node, optional `feature`, `hash`, and `unhash` callbacks, a `release` callback, and a `kref`. Public functions are `tls_toe_bypass()`, `tls_toe_hash()`, `tls_toe_unhash()`, `tls_toe_register_device()`, and `tls_toe_unregister_device()`.

## Control flow

Inline TLS devices register a `tls_toe_device`. Socket hash/listen setup can call the device `hash` callback to program listen state and choose TOE behavior; socket teardown calls `unhash`; bypass logic can decide that a socket should avoid TOE handling. Unregistration drops the device from the list and releases references through the provided `kref` callback.

## State and persistence behavior

Device state persists in registered `tls_toe_device` objects and their reference counts. Per-socket state is external to this header and owned by the inline TLS driver/socket integration.

## Dependencies and integration points

It depends on list and kref primitives and forward-declares `struct sock`. It integrates with inline TLS drivers, TCP listen/hash lifecycle, and module registration.

## Risks and test signals

Risks include unregistering while sockets still hold references, nullable callback handling, device-name collisions, and incomplete cleanup of listen state. Tests should cover register/unregister, hash/unhash ordering, bypass behavior, refcount release, and concurrent socket close during device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tls_toe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/transp_v6.h -->
# sources/distributed-fs/ceph-client/include/net/transp_v6.h

## Purpose

`transp_v6.h` declares common IPv6 transport protocol initialization, control-message, and proc-format helpers. It is a shared contract for rawv6, udpv6, tcpv6, pingv6, IPv6 extension headers, and fragmentation setup.

## Important APIs, types, and functions

The header exports protocol objects `rawv6_prot`, `udpv6_prot`, `tcpv6_prot`, and `pingv6_prot`; init/exit functions for IPv6 extension headers, fragmentation, ping, raw, UDP, and TCP; control message helpers `ip6_datagram_recv_ctl()`, `ip6_datagram_recv_common_ctl()`, `ip6_datagram_recv_specific_ctl()`, and `ip6_datagram_send_ctl()`; and sequence-file helpers `__ip6_dgram_sock_seq_show()` plus `ip6_dgram_sock_seq_show()`. It also defines `LOOPBACK4_IPV6` and `IPV6_SEQ_DGRAM_HEADER`.

## Control flow

IPv6 stack initialization calls the init functions and unwinds with matching exit functions. Datagram receive paths populate ancillary data through common/specific control helpers. Send paths parse IPv6 cmsgs into `flowi6` and `ipcm6_cookie`. Proc seq readers call the wrapper to print socket state with current receive queue bytes.

## State and persistence behavior

The header owns no state. The declared protocol objects and module-level IPv6 transport registrations persist for the lifetime of the IPv6 stack. Proc display reflects live socket memory accounting.

## Dependencies and integration points

It depends on checksum and socket infrastructure and forward-declares IPv6 flow/control cookie types. It integrates with IPv6 datagram sockets, `/proc/net` sequence output, and transport module init/exit.

## Risks and test signals

Risks include init/exit ordering mismatches, cmsg parsing differences between common and protocol-specific paths, and proc output field drift. Tests should cover IPv6 UDP/TCP/raw/ping module init, send/recv control messages, proc socket listing, and builds without optional transports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/transp_v6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tso.h -->
# sources/distributed-fs/ceph-client/include/net/tso.h

## Purpose

`tso.h` provides helper state and APIs for software-assisted TCP segmentation offload in drivers, including header/data construction and DMA mapping of GSO payload regions.

## Important APIs, types, and functions

`struct tso_t` tracks the current frag index, segment size, data pointer, IPv4 ID, transport header length, IPv6 flag, and TCP sequence. Header/data helpers are `tso_count_descs()`, `tso_start()`, `tso_build_hdr()`, and `tso_build_data()`. `struct tso_dma_map` describes xmit-time DMA mapping state for linear and fragmented payloads, with IOVA and fallback per-region fields. `struct tso_dma_map_completion_state`, `tso_dma_map_init()`, `tso_dma_map_next()`, `tso_dma_map_count()`, `tso_dma_map_cleanup()`, `tso_dma_map_completion_save()`, and `tso_dma_map_complete()` support deferred unmap at completion.

## Control flow

Drivers call `tso_start()` for a GSO skb, loop over segments building headers and data chunks, and size TX descriptors with `tso_count_descs()`. For DMA, drivers initialize a map, request DMA chunks for each segment, save IOVA completion state in the TX ring, and later call `tso_dma_map_complete()` at completion. If the IOVA path was not used, the helper returns false and the driver must use its normal per-region unmap path.

## State and persistence behavior

`struct tso_t` is transient per xmit. `struct tso_dma_map` is xmit-time state, while `tso_dma_map_completion_state` persists in the driver ring until TX completion. DMA mappings persist until `tso_dma_map_cleanup()` or completion teardown.

## Dependencies and integration points

It depends on SKB/GSO, DMA mapping, IP headers, IOVA DMA helpers, and driver TX rings. It integrates with NIC drivers that do TSO in software or need generic GSO DMA mapping.

## Risks and test signals

Risks include undercounting descriptors, header buffer overflow beyond `TSO_HEADER_SIZE`, sequence/IP ID errors across segments, DMA mapping leaks on partial failure, and mixing IOVA and fallback cleanup paths. Tests should cover IPv4/IPv6 TSO, fragmented and linear skbs, last-segment handling, DMA map failure unwind, IOVA completion, and per-region fallback unmapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tun_proto.h -->
# sources/distributed-fs/ceph-client/include/net/tun_proto.h

## Purpose

`tun_proto.h` defines one-byte tunnel protocol identifiers shared by VXLAN-GPE and NSH-style encapsulations and converts them to and from Ethernet protocol values.

## Important APIs, types, and functions

Constants are `TUN_P_IPV4`, `TUN_P_IPV6`, `TUN_P_ETHERNET`, `TUN_P_NSH`, and `TUN_P_MPLS_UC`. Helpers are `tun_p_to_eth_p()` and `tun_p_from_eth_p()`.

## Control flow

Encapsulation code maps an inner protocol byte to an Ethernet protocol before passing packets into normal networking paths. Decapsulation or metadata construction maps an Ethernet protocol back to the compact tunnel value. Unknown protocols return zero.

## State and persistence behavior

The header owns no state. The mappings are static wire-protocol constants.

## Dependencies and integration points

It depends on Ethernet protocol definitions and kernel integer types. It integrates with VXLAN-GPE, NSH, MPLS tunnel metadata, and tunnel drivers that expose compact next-protocol fields.

## Risks and test signals

Risks include treating zero as a valid protocol, forgetting to update both mapping directions when adding a protocol, and mismatches with external tunnel registries. Tests should round-trip each supported protocol and verify unknown values fail closed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tun_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/udp.h -->
# sources/distributed-fs/ceph-client/include/net/udp.h

## Purpose

`udp.h` is the shared UDP core header for IPv4 and IPv6. It defines UDP socket hash tables, checksum helpers, socket initialization and receive queues, lookup/send/receive prototypes, GSO/GRO segmentation helpers, SNMP counters, proc iteration, encapsulation static keys, and BPF integration hooks.

## Important APIs, types, and functions

Key types are `struct udp_skb_cb`, `struct udp_hslot`, `struct udp_hslot_main`, `struct udp_table`, `struct udp_dev_scratch`, `struct udp_seq_afinfo`, and `struct udp_iter_state`. Important helpers include `udp_hashslot()`, `udp_hashslot2()`, hash4 helpers, `udp_lib_checksum_complete()`, `udp_csum_outgoing()`, `udp_csum()`, `udp_v4_check()`, `udp_csum_pull_header()`, `udp_lib_init_sock()`, `udp_drops_inc()`, `udp_flow_src_port()`, `udp_rqueue_get()`, `udp_sk_bound_dev_eq()`, `skb_recv_udp()`, `udp_skb_len()`, `udp_skb_csum_unnecessary()`, `copy_linear_skb()`, `udp_rcv_segment()`, and `udp_post_segment_fix_csum()`.

## Control flow

Socket creation calls `udp_lib_init_sock()` to initialize drop counters, reader queues, tunnel list nodes, forwarding thresholds, custom sockopt behavior, and per-NUMA producer queues. Bind/connect operations insert sockets into primary, secondary, and optionally connected-socket hash4 tables. Send paths use checksum helpers and push/flush pending frames. Receive paths perform early demux, checksum verification, queue accounting, possible GRO/GSO receive segmentation via `udp_rcv_segment()`, and dequeue through `__skb_recv_udp()`. Encapsulation users enable static keys so UDP receive can dispatch tunnel callbacks.

## State and persistence behavior

Persistent state includes global `udp_table`, per-socket `udp_sock` queues/counters/tunnel fields, per-net MIB counters, sysctl memory thresholds, static keys for encapsulation, and optional hash4 connected-socket tables. `udp_dev_scratch` stores short-lived per-SKB receive metadata in `skb->dev_scratch`.

## Dependencies and integration points

It depends on inet sockets, GSO, SNMP, IP, IPv6, poll, seq_file, indirect call wrappers, BPF, and NUMA allocation helpers. It integrates with IPv4/IPv6 UDP protocols, UDP-Lite style checksum paths, UDP tunnel receive/transmit, `/proc/net/udp*`, BPF psock updates, GRO/GSO, and socket sysctls.

## Risks and test signals

Risks include hash-table races during rehash/lookup, disabled `CONFIG_BASE_SMALL` hash4 assumptions, checksum state corruption after tunnel/GRO paths, wrong receive queue accounting with forward deficit, per-NUMA queue allocation failure, and static-key leaks for encapsulation. Tests should cover bind/connect/reconnect lookup, IPv4/IPv6 checksum success/failure, UDP_SEGMENT and GRO loopback cases, UDP tunnel decapsulation, proc output, memory pressure/drop counters, BPF psock proto update, and `CONFIG_BASE_SMALL` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/udp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/udp_tunnel.h -->
# sources/distributed-fs/ceph-client/include/net/udp_tunnel.h

## Purpose

`udp_tunnel.h` defines kernel UDP tunnel socket creation, receive callbacks, transmit helpers, GSO/offload handling, destination lookup, metadata construction, GRO registration, and NIC UDP tunnel port offload notification APIs.

## Important APIs, types, and functions

Key types include `struct udp_port_cfg`, callback typedefs for encap receive/error/GRO/destroy, `struct udp_tunnel_sock_cfg`, `enum udp_parsable_tunnel_type`, `struct udp_tunnel_info`, `struct udp_tunnel_nic_info`, `struct udp_tunnel_nic_shared`, and `struct udp_tunnel_nic_ops`. Important functions and helpers include `udp_sock_create4()`, `udp_sock_create6()`, `udp_sock_create()`, `setup_udp_tunnel_sock()`, `udp_tunnel_xmit_skb()`, `udp_tunnel6_xmit_skb()`, `udp_tunnel_handle_partial()`, `udp_tunnel_set_inner_protocol()`, `udp_tunnel_sock_release()`, `udp_tunnel_dst_lookup()`, `udp_tunnel6_dst_lookup()`, `udp_tun_rx_dst()`, `udp_tunnel_handle_offloads()`, `udp_tunnel_cleanup_gro()`, `udp_tunnel_encap_enable()`, and the `udp_tunnel_nic_*` helpers.

## Control flow

Tunnel drivers create AF_INET or AF_INET6 UDP sockets with `udp_port_cfg`, install callbacks with `setup_udp_tunnel_sock()`, and enable encapsulation dispatch. On transmit they perform route lookup, set UDP/IP encapsulation headers, handle offloads, and send through IPv4 or IPv6. On receive, the UDP layer calls encap/GRO callbacks based on the socket configuration. NIC offload management notifies devices about parsable tunnel ports through add/delete/reset/dump helpers under RTNL or device-specific locks.

## State and persistence behavior

Socket state stores encap type, callback pointers, and user data in `udp_sock`. Tunnel port offload state persists in netdevice UDP tunnel tables managed by the udp_tunnel module and optionally shared across devices. Static keys in UDP/UDPv6 persist while tunnel sockets are active. Destination caches may persist route lookup results.

## Dependencies and integration points

It depends on IP tunnel metadata, UDP core, IPv6 conditionally, netdevice notifier chains, dst cache, GRO, and NIC feature flags. It integrates with VXLAN, Geneve, VXLAN-GPE, XFRM UDP encapsulation, NIC RX tunnel port offloads, and tunnel metadata destinations.

## Risks and test signals

Risks include family mismatch in socket creation, checksum policy errors for IPv6 zero checksums, partial GSO flag stripping mistakes, overriding inner protocol for nested tunnels, best-effort NIC port notifications being treated as authoritative, and lock ordering around shared NIC tables. Tests should cover IPv4/IPv6 tunnel creation, callback install/destroy, encapsulated transmit with and without checksums, nested partial offload, GRO lookup cleanup, NIC port add/delete/reset, shared table bounds, and `!CONFIG_NET_UDP_TUNNEL` stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/udp_tunnel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/vsock_addr.h -->
# sources/distributed-fs/ceph-client/include/net/vsock_addr.h

## Purpose

`vsock_addr.h` declares address helper functions for VMware/virtio/hypervisor vSockets. It standardizes initialization, validation, comparison, bind-state tests, unbinding, and sockaddr casting for `sockaddr_vm`.

## Important APIs, types, and functions

Functions are `vsock_addr_init()`, `vsock_addr_validate()`, `vsock_addr_bound()`, `vsock_addr_unbind()`, `vsock_addr_equals_addr()`, and `vsock_addr_cast()`.

## Control flow

Socket bind/connect paths initialize and validate `sockaddr_vm` values, cast generic user sockaddr input to vSocket-specific addresses, compare endpoint identities, and mark addresses unbound when tearing down or rebinding.

## State and persistence behavior

The header owns no state. Helpers mutate caller-owned `sockaddr_vm` objects; persistence is in socket address fields maintained by the vSocket core.

## Dependencies and integration points

It depends on UAPI `linux/vm_sockets.h` and integrates with AF_VSOCK socket operations, transport-independent address handling, and user/kernel sockaddr validation.

## Risks and test signals

Risks include accepting malformed sockaddr lengths, confusing wildcard/unbound CID or port values, and comparing partially initialized addresses. Tests should cover valid/invalid user sockaddr casting, wildcard binding, unbind semantics, equality checks, and connect/bind error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/vsock_addr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/vxlan.h -->
# sources/distributed-fs/ceph-client/include/net/vxlan.h

## Purpose

`vxlan.h` defines VXLAN, VXLAN-GBP, VXLAN-GPE, and remote-checksum-offload wire layouts plus the kernel state structures for VXLAN sockets, devices, VNIs, forwarding entries, per-VNI stats, configuration, feature checks, and switchdev offload notifications.

## Important APIs, types, and functions

Wire structures include `struct vxlanhdr`, `struct vxlanhdr_gbp`, and `struct vxlanhdr_gpe`. Core state types include `struct vxlan_sock`, `union vxlan_addr`, `struct vxlan_rdst`, `struct vxlan_config`, `struct vxlan_vni_stats_pcpu`, `struct vxlan_vni_node`, `struct vxlan_vni_group`, and `struct vxlan_dev`. Helpers include `vxlan_dev_create()`, `vxlan_features_check()`, `vxlan_headroom()`, `vxlan_hdr()`, `vxlan_vni()`, `vxlan_vni_field()`, `vxlan_rco_start()`, `vxlan_rco_offset()`, `vxlan_compute_rco()`, `vxlan_get_sk_family()`, `vxlan_addr_any()`, `vxlan_addr_multicast()`, `netif_is_vxlan()`, `vxlan_fdb_find_uc()`, `vxlan_fdb_replay()`, `vxlan_fdb_clear_offload()`, `vxlan_flag_attr_error()`, `vxlan_fdb_nh_path_select()`, and `vxlan_build_gbp_hdr()`.

## Control flow

Netlink configuration creates a `vxlan_dev` with VNI, endpoints, UDP port, flags, aging, MTU, and offload settings. Receive sockets hash VNIs to VXLAN devices or per-VNI nodes. Transmit paths compute headroom, build VXLAN/VXLAN-GPE/GBP headers, select remote destinations from FDB or nexthop, and use UDP tunnel transmit helpers. Feature checks disable checksum/GSO features when encapsulated layout or inner protocol is not suitable. Switchdev users replay or clear FDB offload state through notifier-friendly structures.

## State and persistence behavior

Persistent state includes per-net VXLAN device lists, RCU pointers to IPv4/IPv6 sockets, VNI rhashtables, FDB/MDB rhashtables, aging timers, GRO cells, per-VNI percpu stats, destination caches, and VXLAN config flags. `vxlan_sock` and remote destinations are refcounted/RCU managed.

## Dependencies and integration points

It depends on VLAN protocol helpers, rhashtable, UDP tunnel APIs, dst metadata, RTNL, switchdev, nexthop, IPv4/IPv6, and netlink extack. It integrates with the VXLAN netdevice driver, UDP tunnel offload notifications, bridge/switchdev FDB offload, collect-metadata tunnels, and nexthop groups.

## Risks and test signals

Risks include endian mistakes in VNI field conversion, feature-offload acceptance for malformed encapsulation, incompatible flag combinations with VXLAN-GPE, RCU/refcount bugs in socket/VNI/FDB tables, remote-checksum offset overflow, and inaccurate per-VNI stats. Tests should cover VNI encode/decode on both endian modes, GBP/GPE header construction, IPv4/IPv6 and multicast endpoints, VNIFILTER, FDB replay/offload clear, nexthop path selection, feature fallback, aging timers, and netlink attempts to mutate immutable flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/vxlan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/wext.h -->
# sources/distributed-fs/ceph-client/include/net/wext.h

## Purpose

`wext.h` declares the Wireless Extensions core entry points and config-dependent stubs for ioctl handling, proc registration, private ioctl dispatch, wireless statistics, and commit handling.

## Important APIs, types, and functions

Under `CONFIG_WEXT_CORE`, it declares `wext_handle_ioctl()`, `compat_wext_handle_ioctl()`, `get_wireless_stats()`, and `call_commit_handler()`. Under `CONFIG_WEXT_PROC`, it declares `wext_proc_init()` and `wext_proc_exit()`. Under `CONFIG_WEXT_PRIV`, it declares private ioctl helpers `ioctl_private_call()`, `compat_private_call()`, and `iw_handler_get_private()`. Disabled stubs return `-EINVAL`, zero, no-op, or NULL macros as appropriate.

## Control flow

Userspace wireless ioctl requests enter `wext_handle_ioctl()` or the compat path, locate driver `iw_handler` callbacks, optionally invoke private handlers, then call commit handlers for deferred configuration. Proc support initializes per-net WEXT proc views.

## State and persistence behavior

The header owns no state. Runtime state is in wireless handler tables, netdevice state, per-net proc entries, and driver-provided statistics.

## Dependencies and integration points

It depends on `net/iw_handler.h` and integrates with legacy wireless drivers, netdevice ioctl dispatch, compat ioctl handling, and procfs.

## Risks and test signals

Risks include assuming WEXT is present when config stubs reject ioctls, compat pointer translation bugs, private ioctl table mismatches, and commit handlers not being called after configuration changes. Tests should cover normal/compat ioctls, disabled-config return values, proc init/exit, private command dispatch, and stats retrieval from legacy drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/wext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/x25.h -->
# sources/distributed-fs/ceph-client/include/net/x25.h

## Purpose

`x25.h` is the main internal header for the Linux X.25 packet layer. It defines X.25 packet constants, state machines, facilities, socket/neighbour/route/forwarding state, timers, queues, sysctls, and function prototypes across the X.25 implementation.

## Important APIs, types, and functions

Important constants cover address lengths, standard/extended sequence formats, packet types, condition bits, states, timer defaults, window/packet defaults, facility classes, and flags. Key types are `struct x25_route`, `struct x25_neigh`, `struct x25_sock`, `struct x25_forward`, and `struct x25_skb_cb`. Prototypes span address parsing, socket lookup/destruction, call request handling, LAPB receive, link control, facilities parsing/creation/negotiation, forwarding, input processing, output/kick/enquiry, routes, timers, sysctl registration, and proc init/exit. Inline lifetime helpers are `x25_neigh_hold()`/`put()` and `x25_route_hold()`/`put()`.

## Control flow

Inbound LAPB frames enter the X.25 device receive path, are associated with a neighbour, decoded, and dispatched to socket, link, or forwarding handlers. Call requests parse addresses and facilities, find routes/neighbours, and either create sockets or forward calls. Data transfer uses sequence numbers, ACK queues, fragment queues, interrupt queues, and timers for call/reset/clear/ACK holdback. Device up/down events establish or terminate links and clear routes/forwards as needed.

## State and persistence behavior

Persistent protocol state includes global socket, route, neighbour, and forwarding lists protected by rwlocks; per-neighbour link state, queue, T20 timer, facilities mask, and refcount; per-socket X.25 addresses, neighbour pointer, logical channel identifier, state, condition bits, sequence variables, timers, queues, facilities, call user data, and masks. Sysctls persist default timeout/forwarding settings.

## Dependencies and integration points

It depends on UAPI X.25 definitions, socket core, SKB queues, timers, refcounting, netdevices, LAPB device integration, procfs, and optional sysctl. It integrates with AF_X25 sockets, X.25 route management ioctls, neighbour/link management, packet forwarding, and device notifications.

## Risks and test signals

Risks include LCI reuse races, sequence/window validation errors, refcount leaks on route/neighbour objects, timer teardown races during socket destruction, malformed facilities overrunning bounded structures, and global list lock ordering issues. Tests should cover call setup/clear/reset, standard and extended sequence modes, facilities negotiation/limits, fragmentation/reassembly, forwarding by LCI/device, device down cleanup, sysctl registration, proc output, and memory-debug lifetime checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/x25.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/x25device.h -->
# sources/distributed-fs/ceph-client/include/net/x25device.h

## Purpose

`x25device.h` provides the link-layer type translation helper for X.25 netdevices. It prepares an incoming SKB as an X.25 host packet.

## Important APIs, types, and functions

The only helper is `x25_type_trans(struct sk_buff *skb, struct net_device *dev)`. It sets `skb->dev`, resets the MAC header, marks the packet as `PACKET_HOST`, and returns `ETH_P_X25`.

## Control flow

Device receive code calls `x25_type_trans()` before handing the skb to the network stack so the packet is classified as X.25 and associated with the receiving device.

## State and persistence behavior

The helper mutates transient SKB metadata only. It owns no persistent state.

## Dependencies and integration points

It depends on Ethernet, packet, X.25 if definitions, SKB, and netdevice types. It integrates with X.25 netdevice drivers and packet receive classification.

## Risks and test signals

Risks are small but include stale MAC header offsets, wrong packet type for non-host frames, or missing device assignment. Tests should verify receive classification, skb metadata after translation, and delivery to X.25 protocol handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/x25device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/xdp.h -->
# sources/distributed-fs/ceph-client/include/net/xdp.h

## Purpose

`xdp.h` defines the kernel XDP buffer/frame API for drivers, BPF execution, memory model registration, fragment support, XDP-to-SKB conversion, metadata kfuncs, RSS hash type reporting, and netdevice XDP feature flags.

## Important APIs, types, and functions

Core types are `enum xdp_mem_type`, `struct xdp_mem_info`, `struct xdp_rxq_info`, `struct xdp_txq_info`, `struct xdp_buff`, `struct xdp_frame`, `struct xdp_frame_bulk`, `struct xdp_attachment_info`, `enum xdp_rx_metadata`, `enum xdp_rss_hash_type`, and `struct xdp_metadata_ops`. Important helpers include `xdp_init_buff()`, `xdp_prepare_buff()`, `xdp_data_hard_end()`, `xdp_get_shared_info_from_buff()`, `xdp_get_buff_len()`, `xdp_buff_add_frag()`, `xdp_scrub_frame()`, `xdp_update_skb_frags_info()`, `xdp_convert_frame_to_buff()`, `xdp_update_frame_from_buff()`, `xdp_convert_buff_to_frame()`, `xdp_return_frame*()`, `xdp_flush_frame_bulk()`, RXQ/memory registration helpers, metadata validation helpers, feature flag setters, and `bpf_prog_run_xdp()`.

## Control flow

Drivers register `xdp_rxq_info`, attach a memory model, prepare an `xdp_buff` for each RX packet, run BPF through `bpf_prog_run_xdp()`, and then act on XDP_PASS/TX/REDIRECT/DROP. XDP_PASS may build an SKB from the buffer or frame. Redirect/TX paths convert buffers to `xdp_frame` objects, preserve enough memory-model information for remote free, and return memory via bulk page-pool queues. Fragmented XDP buffers store `skb_shared_info` at reserved tailroom and update SKB fields when converted.

## State and persistence behavior

RX queue info persists for the lifetime of a driver RX ring and must not be modified during NAPI polling. Memory registrations persist by `xdp_mem_info` IDs. `xdp_buff` is per-packet and NAPI-local; `xdp_frame` may outlive NAPI and therefore stores only memory type, not raw RXQ pointer. Feature flags persist on netdevices. Fragment flags and metadata pointers live in packet-local structures.

## Dependencies and integration points

It depends on BPF, netdevice, SKB shared info, page-pool memory, netlink feature enums, and optional `CONFIG_NET`. It integrates with NIC drivers, BPF dispatcher, cpumap/devmap redirects, AF_XDP zero-copy, XDP metadata kfuncs, SKB construction, and netdevice feature advertisement.

## Risks and test signals

Risks include drivers failing to reserve tailroom for `skb_shared_info`, insufficient headroom for `xdp_frame`, using RXQ pointers after NAPI lifetime, fragment count overflow, unreadable/pfmemalloc flag loss, invalid metadata alignment/length, and missing RCU protection when running BPF. Tests should cover RXQ registration/unregistration, all memory models, XDP_PASS/TX/REDIRECT/DROP, fragmented buffers, frame conversion failure paths, page-pool bulk return, metadata kfunc exposure, bond master redirect, and disabled `CONFIG_NET` stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/xdp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/xdp_priv.h -->
# sources/distributed-fs/ceph-client/include/net/xdp_priv.h

## Purpose

`xdp_priv.h` exposes the private XDP memory allocator structure used by `net/core/xdp.c` and trace events. It is not a broad driver API.

## Important APIs, types, and functions

The only type is `struct xdp_mem_allocator`, containing `struct xdp_mem_info`, an allocator pointer or page-pool pointer union, an rhashtable node, and an RCU head.

## Control flow

XDP core registers memory allocators in a hash table keyed by memory info, then lookup/return paths use the allocator or page pool to release packet memory. Tracepoints may inspect this shape.

## State and persistence behavior

Allocator entries persist while an XDP memory model is registered and are removed through RCU to protect concurrent readers.

## Dependencies and integration points

It depends on rhashtable and public `net/xdp.h`. It integrates with XDP memory registration, page-pool return paths, and XDP trace events.

## Risks and test signals

Risks include treating this private header as stable external API, freeing allocator entries before RCU readers finish, and mismatching union interpretation with `mem.type`. Tests should cover memory registration/unregistration, trace event builds, page-pool and non-page-pool allocator returns, and RCU lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/xdp_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/xdp_sock.h -->
# sources/distributed-fs/ceph-client/include/net/xdp_sock.h

## Purpose

`xdp_sock.h` defines AF_XDP socket and UMEM internal state, XSK map layout, socket lifecycle states, generic receive/redirect entry points, and TX metadata callbacks used by drivers and AF_XDP core.

## Important APIs, types, and functions

Key types are `struct xdp_umem`, `struct xsk_map`, `struct xdp_sock`, and `struct xsk_tx_metadata_ops`. AF_XDP functions under `CONFIG_XDP_SOCKETS` include `xsk_generic_rcv()`, `__xsk_map_redirect()`, `__xsk_map_flush()`, and `xsk_destruct_skb()`. Metadata helpers are `xsk_tx_metadata_to_compl()`, `xsk_tx_metadata_request()`, and `xsk_tx_metadata_complete()`.

## Control flow

AF_XDP setup creates UMEM, binds an `xdp_sock` to a netdevice queue, and optionally uses an XSK map for BPF redirect. Receive paths either enqueue XDP buffers to the socket or redirect through the map and later flush pending sockets. Generic TX builds SKBs from TX descriptors and can resume partially built packets through `xs->skb`. Driver TX paths inspect metadata at submission, request timestamp/checksum/launch-time offloads, save completion pointers, and fill completion timestamps when hardware completes.

## State and persistence behavior

`struct xdp_umem` persists pinned user memory, page array, chunk geometry, flags, users refcount, DMA list, and work item. `struct xdp_sock` embeds `struct sock`, RX/TX queues, UMEM/pool pointers, bound device/queue, zero-copy and scatter-gather flags, state enum, TX budget, drop stats, partial SKB, map membership, and control mutex. XSK maps store RCU socket pointers and atomic count.

## Dependencies and integration points

It depends on BPF maps, workqueues, AF_XDP UAPI, socket core, locks, MM, and optional `CONFIG_XDP_SOCKETS`. It integrates with BPF redirect maps, AF_XDP bind/send/recv, NIC zero-copy drivers, generic SKB fallback, and TX metadata UAPI.

## Risks and test signals

Risks include UMEM lifetime/refcount bugs, map updates racing with redirect, starvation if TX budget accounting fails, stale completion metadata pointers into user UMEM, unsupported metadata silently ignored, and disabled-config stubs returning different errors. Tests should cover bind/unbind, shared and non-shared UMEM, XSK map redirect/flush, generic receive/TX, partial multi-buffer TX resume, metadata timestamp/checksum/launch-time, and `CONFIG_XDP_SOCKETS` disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/xdp_sock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/xdp_sock_drv.h -->
# sources/distributed-fs/ceph-client/include/net/xdp_sock_drv.h

## Purpose

`xdp_sock_drv.h` is the driver-facing wrapper API for AF_XDP zero-copy support. It exposes pool sizing, DMA mapping, buffer allocation/free, multi-buffer fragment handling, raw descriptor address translation, metadata validation, and need-wakeup helpers.

## Important APIs, types, and functions

Important constants are `XDP_UMEM_MIN_CHUNK_SHIFT`, `XDP_UMEM_MIN_CHUNK_SIZE`, `NETDEV_XDP_ACT_XSK`, and `XDP_TXMD_FLAGS_VALID`. The driver-private callback descriptor is `struct xsk_cb_desc`. Wrappers include `xsk_tx_completed()`, `xsk_tx_peek_desc()`, `xsk_tx_peek_release_desc_batch()`, `xsk_tx_release()`, `xsk_get_pool_from_qid()`, wakeup setters/clearers, pool geometry helpers, `xsk_pool_dma_map()`/`unmap()`, DMA accessors, `xsk_buff_alloc()`/`alloc_batch()`/`can_alloc()`/`free()`, fragment helpers, raw data/DMA/context helpers, metadata helpers, and DMA sync helpers.

## Control flow

Drivers obtain an XSK pool for a queue, map UMEM pages for DMA, allocate XDP buffers from the fill ring, run RX/XDP, and free or redirect buffers. TX paths peek descriptors, translate user addresses to data/DMA plus optional metadata, prepare hardware descriptors, then report completions and release TX descriptors. Multi-buffer paths add fragments to the head buffer, maintain pool fragment lists, and free all fragments on packet completion.

## State and persistence behavior

Persistent state is in `struct xsk_buff_pool`: device/netdev pointers, queue ID, UMEM, fill/completion queues, free head arrays, DMA page array, chunk geometry, metadata length, need-wakeup cache, zero-copy limits, software checksum flag, and locks. Driver rings may persist completion metadata and DMA addresses until TX completion.

## Dependencies and integration points

It depends on `xdp_sock.h`, `xsk_buff_pool.h`, AF_XDP UAPI, DMA APIs, and `CONFIG_XDP_SOCKETS`. It integrates with NIC RX/TX queue setup, NAPI, DMA mapping, AF_XDP rings, XDP multi-buffer, and TX metadata offload.

## Risks and test signals

Risks include using zero helpers when AF_XDP is disabled, wrong frame size after reserving tailroom, DMA sync omissions, descriptor crossing non-contiguous pages, leaked fragment list entries, invalid metadata flags being silently ignored, and queue/pool lifetime races. Tests should cover pool lookup, DMA map/unmap, aligned and unaligned UMEM, multi-buffer RX/TX, descriptor boundary validation, need-wakeup behavior, metadata validation, and driver teardown with active sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/xdp_sock_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/xfrm.h -->
# sources/distributed-fs/ceph-client/include/net/xfrm.h

## Purpose

`xfrm.h` is the central internal header for Linux XFRM/IPsec. It defines security association state, policy database entries, mode/type registration, key-manager callbacks, replay protection, secpath metadata, route bundles, tunnel/interface hooks, hardware offload contracts, netlink/PF_KEY compatibility, NAT keepalive hooks, and policy/state lookup APIs.

## Important APIs, types, and functions

Core state types include `struct xfrm_state`, `struct xfrm_policy`, `struct xfrm_tmpl`, `struct xfrm_dst`, `struct sec_path`, `struct xfrm_offload`, `struct xfrm_dev_offload`, `struct xfrm_mgr`, `struct xfrm_type`, `struct xfrm_type_offload`, `struct xfrm_mode_cbs`, `struct xfrm_policy_afinfo`, `struct xfrm_state_afinfo`, protocol/tunnel handler structures, algorithm descriptors, `struct xfrm_translator`, and XFRM interface structs. Important helpers cover reference management (`xfrm_state_hold()`/`put()`, `xfrm_pol_hold()`/`put()`), address/selector matching, flow port extraction, policy checks, route forwarding checks, socket policy clone/free, state/policy lookup/add/update/delete/flush, replay check/advance, mode/type registration, offload validation, mark and if_id netlink attributes, and NAT keepalive lifecycle.

## Control flow

Outbound packets decode a flow, check socket and global policies, resolve templates to states, build an `xfrm_dst` bundle, and pass through mode/type output callbacks or offload validation. Inbound packets parse SPI/sequence, find a state, perform replay/auth/decrypt/type input, populate secpath, and then run policy verification. Missing states trigger key-manager acquire/report callbacks. State and policy netlink/PF_KEY changes allocate, initialize, insert, update, delete, or flush objects and send notifications. Device offload paths add state/policy to netdevices, validate transmit offload, resume async processing, and free offload resources on teardown.

## State and persistence behavior

Persistent state is per-net namespace XFRM SPD/SAD state plus per-object timers, lifetimes, replay windows, generation IDs, refcounts, locks, security contexts, algorithm/key material, encapsulation data, NAT keepalive state, and offload device references. `struct sec_path` is per-SKB metadata recording applied transforms and offload status. `xfrm_dst` route bundles cache route, path, child, policy and state references plus generation/cookie values. Timers drive replay notifications, hard/soft expiry, hold queues, and NAT keepalives.

## Dependencies and integration points

It depends on UAPI XFRM, PF_KEY, IPsec, IPv4/IPv6 routing, flow keys, dst entries, GRO cells, audit, netlink attributes, socket policy, SNMP statistics, netdevice offload ops, optional security labels, optional migration, optional user compat translation, and optional BTF/BPF registration. It integrates with ESP/AH/IPComp, IPIP/IPv6 tunnel modes, XFRM interfaces, UDP encapsulation, key managers, iproute2/netlink policy management, audit, hardware crypto/packet offload, and network namespaces.

## Risks and test signals

Risks are high because this header defines security-critical lifetime and policy contracts. Key issues include refcount/RCU mistakes in state/policy/dst/secpath objects, replay-window or ESN errors, selector/address matching bugs, policy bypass through `DST_NOPOLICY`/`IPSKB_NOPOLICY`, offload device reference leaks, netlink attribute length mistakes, algorithm clone allocation leaks, mode callback misuse, and disabled-config stubs accepting traffic when XFRM is absent. Tests should cover inbound/outbound IPsec for IPv4/IPv6, transport and tunnel modes, policy block/allow/acquire, socket policies, replay and ESN windows, lifetime expiry, NAT-T and keepalive, state/policy migration, hardware offload add/delete/resume, audit events, netlink/PF_KEY compatibility, XFRM interfaces, and config matrices with XFRM/offload/security/IPv6 disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/xfrm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/xsk_buff_pool.h -->
# sources/distributed-fs/ceph-client/include/net/xsk_buff_pool.h

## Purpose

`xsk_buff_pool.h` defines the AF_XDP buffer pool backing zero-copy UMEM access. It describes XDP buffer wrappers, DMA page maps, pool control/data-path fields, address translation, DMA sync, descriptor boundary checks, and handle reconstruction.

## Important APIs, types, and functions

Key types are `struct xdp_buff_xsk`, `struct xsk_dma_map`, `struct xsk_buff_pool`, and `struct xdp_desc_ctx`. Macros include `XSK_PRIV_MAX`, `XSK_CHECK_PRIV_TYPE()`, `XSK_TX_COMPL_FITS()`, and `XSK_NEXT_PG_CONTIG_MASK`. Core functions include `xp_create_and_assign_umem()`, `xp_assign_dev()`, `xp_assign_dev_shared()`, `xp_alloc_tx_descs()`, `xp_destroy()`, `xp_get_pool()`, `xp_put_pool()`, `xp_clear_dev()`, `xp_add_xsk()`, `xp_del_xsk()`, `xp_free()`, `xp_dma_map()`/`unmap()`, `xp_alloc()`/`alloc_batch()`/`can_alloc()`, `xp_raw_get_data()`, `xp_raw_get_dma()`, and `xp_raw_get_ctx()`. Inline helpers initialize buffer address/DMA, sync DMA, detect non-contiguous page crossing, parse multi-buffer descriptors, extract aligned/unaligned addresses, release heads, reconstruct UMEM handles, and test metadata enablement.

## Control flow

AF_XDP core creates a pool from UMEM, assigns it to a device queue, maps pages for DMA, and adds sockets. Drivers allocate `xdp_buff_xsk` heads, initialize data and DMA addresses from user descriptors, process RX/TX, and return heads to the pool. Address helpers convert descriptor handles to user virtual addresses and DMA addresses, while boundary checks prevent descriptors from spanning non-contiguous pages.

## State and persistence behavior

The pool persists across socket binding and holds device/netdev pointers, TX socket list, UMEM, work item, RX lock, free lists, fill/completion queues, DMA page array, buffer heads, TX descriptor cache, chunk geometry, metadata length, need-wakeup state, and free-head counters. DMA maps are refcounted and protected by RTNL list membership.

## Dependencies and integration points

It depends on AF_XDP UAPI, DMA mapping, BPF, public XDP types, netdevice/device/page declarations, and XSK queues. It integrates with AF_XDP core, zero-copy NIC drivers, XDP memory model registration, and TX metadata completion storage.

## Risks and test signals

Risks include incorrect unaligned address reconstruction, DMA page flag misuse, accepting descriptors crossing non-contiguous pages, free-head accounting imbalance, stale device pointers after teardown, and private callback storage overflow. Tests should cover pool create/assign/destroy, shared UMEM assignment, DMA map refcounts, aligned/unaligned descriptors, page-boundary validation, handle round trips, DMA sync, need-wakeup caching, TX descriptor allocation, and active socket removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/xsk_buff_pool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/pcmcia/ciscode.h -->
# sources/distributed-fs/ceph-client/include/pcmcia/ciscode.h

## Purpose

`ciscode.h` provides legacy PCMCIA manufacturer and product ID constants used by drivers and matching tables for known cards.

## Important APIs, types, and functions

The file contains `MANFID_*` and `PRODID_*` macros for vendors and products such as 3Com, Accton, Adaptec, Fujitsu, IBM, Intel, KME, Linksys, Megahertz, Motorola, Nokia, Olicom, Quatech, SMC, Socket, TDK, Xircom, and others. There are no types or functions.

## Control flow

There is no control flow. PCMCIA drivers or match tables compare CIS manufacturer/card IDs against these constants.

## State and persistence behavior

The header owns no state. Constants represent card identity values read from CIS tuples.

## Dependencies and integration points

It has no includes beyond guards and integrates with PCMCIA device ID tables, CIS parsing results, and legacy driver quirks.

## Risks and test signals

Risks include duplicate vendor IDs, product ID typos, and relying only on numeric IDs when product strings or fake CIS overrides are needed. Tests should validate known-card match tables, module alias generation, and behavior for devices with shared manufacturer IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/pcmcia/ciscode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/pcmcia/cisreg.h -->
# sources/distributed-fs/ceph-client/include/pcmcia/cisreg.h

## Purpose

`cisreg.h` defines offsets and bit masks for PCMCIA/CardBus configuration, status, pin replacement, socket/copy, extended status, function status, and zoomed-video indirect registers.

## Important APIs, types, and functions

Register offset macros include `CISREG_COR`, `CISREG_CCSR`, `CISREG_PRR`, `CISREG_SCR`, `CISREG_ESR`, IO base/size registers, CardBus function registers, and indirect register addresses. Bit masks include `COR_*`, `CCSR_*`, `PRR_*`, `SCR_*`, `ESR_*`, `CBFN_*`, `FEMR_*`, and `ICTRL0_*`.

## Control flow

PCMCIA core and drivers use these constants when reading or writing card configuration registers relative to `ConfigBase`. Control flows typically select a configuration option, enable a function/IRQ, acknowledge status, inspect ready/write-protect/battery events, or program indirect video registers.

## State and persistence behavior

The header owns no software state. It names hardware/card register bits whose values persist in the card until reset, power transition, or explicit write.

## Dependencies and integration points

It is standalone and integrates with PCMCIA CIS/configuration code, CardBus function status handling, power management, and legacy device drivers.

## Risks and test signals

Risks include writing wrong offsets for multifunction cards, confusing event and status bits, failing to clear/ack interrupts, and unsafe register writes during power transitions. Tests should cover configuration register programming, interrupt enable/ack, ready/write-protect event handling, CardBus function status, and suspend/resume reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/pcmcia/cisreg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/pcmcia/cistpl.h -->
# sources/distributed-fs/ceph-client/include/pcmcia/cistpl.h

## Purpose

`cistpl.h` defines PCMCIA/CardBus CIS tuple codes and parsed tuple data structures. It is the schema used by CIS parsers and drivers to interpret card memory/device geometry, identity, function type, function extensions, configuration tables, power/timing/IO/memory windows, and tuple iteration.

## Important APIs, types, and functions

The header defines tuple code constants `CISTPL_*`, `cisdata_t`, and parsed tuple structures including `cistpl_longlink_t`, `cistpl_checksum_t`, `cistpl_longlink_mfc_t`, `cistpl_altstr_t`, `cistpl_device_t`, `cistpl_vers_1_t`, `cistpl_jedec_t`, `cistpl_manfid_t`, `cistpl_funcid_t`, `cistpl_funce_t`, serial/modem extension types, LAN extension types, IDE extension types, `cistpl_bar_t`, `cistpl_config_t`, `cistpl_power_t`, `cistpl_timing_t`, `cistpl_io_t`, `cistpl_irq_t`, `cistpl_mem_t`, `cistpl_cftable_entry_t`, `cistpl_cftable_entry_cb_t`, `cistpl_device_geo_t`, `cistpl_vers_2_t`, `cistpl_org_t`, `cistpl_format_t`, `union cisparse_t`, and `tuple_t`.

## Control flow

CIS traversal code fills `tuple_t` from raw tuple storage, follows long links/multifunction links, then parses tuple payloads into `cisparse_t` members according to `TupleCode`. Drivers consume parsed manufacturer/function/configuration/facility data to pick resources, power settings, IO windows, IRQs, and quirks.

## State and persistence behavior

The header owns no runtime state. Parsed structures are transient parser outputs, while raw CIS content persists on the card. `tuple_t` fields such as link offset, CIS offset, tuple offset, and data length are parser iteration state.

## Dependencies and integration points

It is standalone aside from primitive typedef assumptions and integrates with PCMCIA CIS parsers, socket/card services, driver match logic, resource allocation, and fake CIS overrides.

## Risks and test signals

Risks include trusting tuple lengths into fixed arrays, confusing CardBus and 16-bit PCMCIA cftable forms, incorrect scaling for power/timing values, too many IO/memory windows, and malformed long-link loops. Tests should parse representative modem, LAN, IDE, memory, multifunction, and CardBus CIS images; fuzz tuple lengths; validate bounds against max arrays; and verify resource selection from cftable entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/pcmcia/cistpl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/pcmcia/device_id.h -->
# sources/distributed-fs/ceph-client/include/pcmcia/device_id.h

## Purpose

`device_id.h` provides initializer macros for PCMCIA driver device ID tables. The macros populate match flags, manufacturer/card IDs, product strings and hashes, function numbers, pseudo-function device numbers, and fake CIS override file names.

## Important APIs, types, and functions

Macros include `PCMCIA_DEVICE_MANF_CARD()`, `PCMCIA_DEVICE_FUNC_ID()`, product ID variants from `PCMCIA_DEVICE_PROD_ID1()` through `PCMCIA_DEVICE_PROD_ID1234()`, combined manufacturer/card/product macros, multifunction `PCMCIA_MFC_DEVICE_*` variants, pseudo multifunction `PCMCIA_PFC_DEVICE_*` variants, fake CIS override macros `PCMCIA_DEVICE_CIS_*`, `PCMCIA_MFC_DEVICE_CIS_*`, `PCMCIA_PFC_DEVICE_CIS_*`, and `PCMCIA_DEVICE_NULL`.

## Control flow

Drivers declare static PCMCIA ID tables with these macros. The PCMCIA core compares a device's parsed CIS fields against each entry's `match_flags`, IDs, hashes, function number, device number, and optional fake CIS requirement. Matching entries drive module autoloading and driver binding.

## State and persistence behavior

The header owns no mutable state. Macro output becomes static driver match-table data, and fake CIS file names persist as pointers in those entries.

## Dependencies and integration points

It is active only under `__KERNEL__` and depends on PCMCIA match flag and ID table structure definitions supplied by surrounding headers. It integrates with module alias generation, PCMCIA core matching, multifunction card handling, pseudo-function matching, and CIS override loading.

## Risks and test signals

Risks include passing incorrect product string hashes, missing terminators, choosing function vs device number matching incorrectly, stale fake CIS file names, and match flags that are too broad. Tests should cover module alias generation, table matching for manufacturer/card/product combinations, multifunction and pseudo-function devices, fake CIS override lookup, and null terminator handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/pcmcia/device_id.h -->
