# subset-b-005940 research

This grouped report covers Linux networking headers under `sources/distributed-fs/ceph-client/include/net/`. Each section title preserves the source path and is wrapped for reconciliation into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/flow.h -->
# sources/distributed-fs/ceph-client/include/net/flow.h

Purpose: defines the generic routing-flow descriptors used by IPv4 and IPv6 output lookups. `struct flowi_common` carries shared selector state: output/input ifindex, L3 master device, mark, DSCP, scope, protocol, flags, security id, UID, multipath hash, and tunnel id. `struct flowi4` and `struct flowi6` add address-family fields and the `union flowi_uli` L4 selector union for ports, ICMP, mobility header, and GRE key. `struct flowi` overlays common, IPv4, and IPv6 views for APIs that route either family.

Important APIs: `flowi4_init_output()` fully initializes an IPv4 lookup key, including loopback input index, DSCP conversion from TOS, UID, ports, and zeroed tunnel/multipath fields. `flowi4_update_output()` retargets address/output-interface fields after a previous lookup. `flowi4_to_flowi()`, `flowi6_to_flowi()`, and common accessors rely on the union layout. `__get_hash_from_flowi6()` exports IPv6 hash derivation into flow keys.

Control flow and state: this header is mostly value construction. Callers allocate these descriptors on stack or in cork/socket state, initialize them, then pass them into route, xmit, and reply paths. There is no persistent storage here; persistence comes from copied socket fields such as marks, UIDs, ports, and tunnel identifiers.

Dependencies and integration: depends on `inet_dscp.h`, `in6.h`, atomic/container helpers, and Linux UID types. It integrates with `ip.h`, `inet_sock.h`, IPv6 routing, tunnel output, policy routing, and flow hashing.

Risks: partial initialization is dangerous because route lookups consume many flags and selectors. The IPv4 address grouping and alignment comments are ABI-like assumptions used by fast copy/hash paths. Tests should cover route lookup behavior with marks, DSCP/TOS, bound devices, transparent/HDRINCL flags, tunnel ids, and IPv6 flow hashing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/flow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/flow_dissector.h -->
# sources/distributed-fs/ceph-client/include/net/flow_dissector.h

Purpose: declares the packet flow-dissection key model used by classifiers, hashing, BPF flow dissectors, receive steering, and offload rules. It defines small typed key structs for control metadata, basic protocol ids, VLAN/CVLAN, MPLS, tunnel options, IPv4/IPv6/TIPC addresses, ARP, ports and ranges, ICMP, Ethernet addresses, TCP flags, IP TOS/TTL, ingress metadata, conntrack, hash, PPPoE, L2TPv3, IPsec, and CFM.

Important APIs/types: `enum flow_dissector_key_id` is the central key namespace. `struct flow_dissector` stores `used_keys` and per-key offsets into an arbitrary target container. `struct flow_keys` is the common hash-oriented container with basic, tags, VLAN, keyid, ports, ICMP, and final address union. `dissector_uses_key()` tests key availability; `skb_flow_dissector_target()` computes a typed target pointer from offsets. Hash/digest helpers include `flow_hash_from_keys()`, `flow_hash_from_keys_seed()`, `make_flow_keys_digest()`, `flow_get_u32_src()`, and `flow_get_u32_dst()`.

Control flow and state: callers configure a `flow_dissector` with offsets, run packet parsing elsewhere, and then read only keys whose bits are set. Inline helpers set MPLS-used bits, clear key-control/basic storage, and report whether L4 entropy is present via ports or IPv6 flow label. BPF attachment validation is exposed under `CONFIG_BPF_SYSCALL`.

Dependencies and integration: uses Linux fixed-width types, IPv6 addresses, siphash alignment, Ethernet and tc flower UAPI flags. It is consumed directly by `flow_offload.h`, classifiers, skb hashing, BPF, GRO/RPS paths, and tunnel-aware matching.

Risks: `used_keys` is a 64-bit bitset, so key count growth must preserve capacity. Offset/key-id mismatches corrupt output containers. Tunnel option length is capped at 255. Test signals include flower classifier matches for each key, first-fragment and encapsulation parsing flags, BPF attach checks, flow hash stability, and digest uniqueness under address/port changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/flow_dissector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/flow_offload.h -->
# sources/distributed-fs/ceph-client/include/net/flow_offload.h

Purpose: defines the kernel traffic-control flow offload contract between classifiers/actions and hardware or indirect offload drivers. It wraps dissector keys as mask/key pairs, enumerates action ids, models action entries, flow rules, stats, flow blocks, block callbacks, classifier commands, and standalone offloaded actions.

Important APIs/types: `struct flow_match_*` pairs map directly onto flow dissector key structs. `flow_rule_match_*()` functions extract typed match views. `enum flow_action_id` covers accept/drop/trap/goto, redirect/mirred ingress/egress, VLAN/MPLS/PPPoE edits, tunnel encap/decap, mangle/add/csum/mark/ptype/priority/queue/sample/police/conntrack/gate/jump/pipe/continue. `struct flow_action_entry` stores action-specific union data, cookies, stats preference, destructor hooks, and user cookies. `flow_rule_alloc()` and `offload_action_alloc()` allocate flexible-array rules/actions.

Control flow and state: offload setup builds a `flow_rule` from match and action arrays, checks driver support, then binds callbacks into `struct flow_block`. Inline checks reject mixed hardware-stat modes, unsupported control flags, and unsupported encapsulation flags with netlink extended ACKs. `flow_stats_update()` accumulates packets, bytes, drops, max last-used time, and used hardware-stat mode.

Dependencies and integration: depends on lists, netlink, flow dissector, net devices, qdiscs, tc setup types, tunnel info, conntrack flowtables, psample, and action-gate entries. It is the bridge between tc flower/action code and NIC driver callbacks, including indirect device registration.

Risks: flexible-array sizing, action union interpretation, refcounted block callbacks, and list movement are high-risk. Drivers must not accept unsupported masks silently. Tests should exercise every action id translation, mixed hardware stats rejection, block bind/unbind lifetimes, callback refcounts, indirect offload registration, and extack messages for unsupported control flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/flow_offload.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/fou.h -->
# sources/distributed-fs/ceph-client/include/net/fou.h

Purpose: declares Foo-over-UDP and Generic UDP Encapsulation helper hooks for tunnel transmit paths. It provides length calculation and header-build entry points for encapsulating an skb according to `struct ip_tunnel_encap`.

Important APIs: `fou_encap_hlen()` and `gue_encap_hlen()` report the encapsulation header length. `__fou_build_header()` and `__gue_build_header()` build protocol-specific headers, update the next protocol and source port, and consume a type selector. `register_fou_bpf()` registers BPF integration for FOU processing.

Control flow and state: the header is declarative; transmit code computes header length, reserves/pushes space, and calls the builder. No persistent state is defined here. State lives in tunnel configuration, skb metadata, UDP tunnel sockets, and optional BPF registration.

Dependencies and integration: pulls in `skbuff.h`, `flow.h`, `gue.h`, `ip_tunnels.h`, and `udp.h`. It integrates with IP tunnel encapsulation, remote checksum handling via GUE, and UDP tunnel receive/transmit paths.

Risks: header length and build functions must agree exactly or tunnel packets will be malformed. Protocol and source-port output parameters are side effects that route/NAT/checksum code may rely on. Tests should cover FOU and GUE tunnel transmit with checksum offload, BPF registration availability, malformed tunnel config, and GSO/GRO interaction with UDP encapsulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/fou.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/fq.h -->
# sources/distributed-fs/ceph-client/include/net/fq.h

Purpose: declares reusable fair-queueing data structures used by wireless and qdisc-style code that embeds fair queue logic. The design groups packet queues into traffic “tins” and per-flow queues, with DRR++ deficit accounting.

Important types: `struct fq_flow` owns a queue, backlog bytes, deficit, owner tin, and list node. `struct fq_tin` owns new/old flow lists, a default collision flow, backlog counters, collision/overlimit/flow counters, and transmit statistics. `struct fq` owns the flow array, flow bitmap, tin backlog list, spinlock, queue and memory limits, quantum, global backlog, overlimit/overmemory counters, and collision count. Callback typedefs let embedders provide dequeue, free, and filter behavior.

Control flow and state: this header only defines storage and callback contracts; `fq_impl.h` supplies inline/static implementation to includers. All mutable queue state is in memory under `fq->lock`. There is no on-disk persistence.

Dependencies and integration: depends on skb queues, spinlocks, and Linux list/bitmap conventions. It integrates with MAC/qdisc code that wants common flow hashing and deficit round-robin without a standalone object file.

Risks: callers must initialize every queue/list/counter consistently before using `fq_impl.h` helpers. Flow collisions fall back to `default_flow`, so tests need multiple tins with identical flow indexes. Test signals include limit enforcement, memory accounting, fairness between new and old flows, filter/drop callbacks, and lockdep coverage around `fq->lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/fq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/fq_impl.h -->
# sources/distributed-fs/ceph-client/include/net/fq_impl.h

Purpose: provides static fair-queue implementation helpers to be embedded by includers that define their own enqueue/dequeue policy. It implements removal accounting, DRR++ tin dequeue, hash classification, collision handling, overlimit drops, and reset/filter operations.

Important APIs/functions: `__fq_adjust_removal()` updates tin, flow, global packet, and memory counters and clears bitmap/list membership when a flow drains. `fq_flow_dequeue()` pops one skb. `fq_flow_drop()` drops up to half a flow queue, capped at 32 packets. `fq_tin_dequeue()` walks new then old flows, refills deficits by `fq->quantum`, demotes new flows, and updates tx counters. `fq_flow_idx()` maps skb hash to the flow array. `fq_flow_classify()` detects cross-tin collisions and uses `tin->default_flow`. `fq_find_fattest_flow()` selects the largest backlog flow for pressure drops. `fq_tin_enqueue()` enqueues skb chains and enforces limits.

Control flow and state: all helpers assert `fq->lock`. Enqueue marks skbs off-list before queueing, increments backlog/memory, and drops fattest flows when packet or memory limits are exceeded. Dequeue loops until it finds an eligible nonempty flow or all lists drain.

Dependencies and integration: includes `fq.h`; relies on skb queue primitives, bitmaps, list management, lockdep, and caller-provided free/filter/dequeue callbacks.

Risks: counter drift is the main failure mode; every enqueue/drop/dequeue must mirror byte, packet, and truesize accounting. Default-flow collision behavior can hide unfairness. Tests should verify draining removes bitmap/list entries, overlimit/overmemory counters increment, chained skb enqueue works, filter callbacks can drop safely, and DRR deficit prevents starvation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/fq_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/garp.h -->
# sources/distributed-fs/ceph-client/include/net/garp.h

Purpose: declares Generic Attribute Registration Protocol support, used by applications such as GVRP over STP-like link-layer control. It models GARP PDUs, applicant state machines, per-device applicants, and application registration.

Important APIs/types: wire structs include `garp_pdu_hdr`, `garp_msg_hdr`, and variable-length `garp_attr_hdr`. `enum garp_attr_event`, `enum garp_applicant_state`, `enum garp_event`, and `enum garp_action` encode the registration state machine. `struct garp_attr` stores registered attributes in an rb-tree. `struct garp_application` wraps an STP protocol descriptor. `struct garp_applicant` holds the app, device, join timer, spinlock, skb queue, pending PDU, GID tree, and RCU hook. Public APIs register/unregister applications, initialize/uninitialize applicants on devices, and request join/leave for an attribute.

Control flow and state: join/leave requests enqueue state-machine work for a device applicant. Attributes persist in memory under the applicant lock and are reclaimed by RCU. Timers drive join transmission; skb control block storage is accessed through `garp_cb()`.

Dependencies and integration: depends on Ethernet types, `net/stp.h`, net devices, timers, rbtrees, RCU, and skb queues. It integrates with bridge/VLAN registration protocols.

Risks: variable-length attributes and skb control-block reuse require strict bounds. State-machine transitions must be covered for every event/action pair. Tests should include duplicate joins, leaves of absent attributes, timer-driven PDU generation, application unregister while applicants exist, RCU lifetime, and malformed PDU parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/garp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/gen_stats.h -->
# sources/distributed-fs/ceph-client/include/net/gen_stats.h

Purpose: declares generic scheduler/statistics helpers for exporting traffic statistics through rtnetlink and maintaining rate estimators. It supports basic byte/packet counters, queue stats, app-specific xstats, compatibility `tc_stats`, and estimator lifecycle.

Important APIs/types: `struct gnet_stats_basic_sync` stores byte and packet counters with `u64_stats_sync` for lockless 64-bit updates. `struct gnet_dump` tracks the skb, lock, tail attribute, compatibility flags, xstats, and tc stats during a stats dump. Copy/add APIs include `gnet_stats_copy_basic()`, `_basic_hw()`, `_queue()`, `_app()`, and their add variants. Estimator APIs include `gen_new_estimator()`, `gen_kill_estimator()`, `gen_replace_estimator()`, `gen_estimator_active()`, and `gen_estimator_read()`.

Control flow and state: callers initialize counters, start a dump with `gnet_stats_start_copy*()`, append basic/rate/queue/app stats, then finish with `gnet_stats_finish_copy()`. Estimators are RCU pointers updated under a supplied lock and read into 64-bit samples.

Dependencies and integration: uses Linux gen_stats UAPI, sockets, rtnetlink, packet scheduler definitions, skb/nlattr, spinlocks, per-CPU counters, and RCU. It integrates with qdiscs, tc actions, and offload stats.

Risks: concurrent stats writers need sync helpers; direct field writes are safe only for non-concurrent storage. Compat attributes must remain aligned with older tc userspace. Tests should exercise 32-bit counter consistency, per-CPU aggregation, estimator replace/kill under RCU, hardware stats copy, and netlink dump failure unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/gen_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/genetlink.h -->
# sources/distributed-fs/ceph-client/include/net/genetlink.h

Purpose: declares the in-kernel Generic Netlink family and message construction API. It lets kernel subsystems define named families, operations, multicast groups, per-socket private storage, validation policy, namespace behavior, and request/reply/notification helpers.

Important APIs/types: `struct genl_family` is the central registration object with name, version, max attributes, policy, ops arrays, split ops, multicast groups, hooks, module owner, and socket-private callbacks. `struct genl_info` carries request metadata, parsed attributes, namespace, context, and extack. Operation forms include `genl_small_ops`, `genl_ops`, and `genl_split_ops`. Message helpers include `genlmsg_put()`, `genlmsg_iput()`, `genlmsg_put_reply()`, `genlmsg_end()`, `genlmsg_cancel()`, `genlmsg_parse()`, `genlmsg_new()`, `genlmsg_reply()`, multicast/unicast helpers, listener/error helpers, and dump accessors.

Control flow and state: families register globally through `genl_register_family()` and unregister later. Requests are parsed and dispatched under either a global genl lock or parallel ops. Replies allocate an skb, put a genl header, fill attributes, end, and unicast/multicast. Dump callbacks access `genl_dumpit_info`.

Dependencies and integration: depends on netlink, network namespaces, UAPI genetlink, xarrays for per-socket private storage, and extack. It is used by modern kernel control planes including IOAM, TLS handshake, wireless, tunnels, and filesystems needing netlink control.

Risks: validation policy changes are userspace ABI. Multicast group indexes are offsets, not absolute ids. `parallel_ops` shifts locking to the family. Tests should cover strict/deprecated parsing, missing required attrs, multicast group bounds, namespace targeting, per-socket private init/destroy, dump consistency, and unregister while sockets/listeners exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/genetlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/geneve.h -->
# sources/distributed-fs/ceph-client/include/net/geneve.h

Purpose: defines Geneve tunnel wire headers and minimal device integration. Geneve carries a UDP destination port, virtual network identifier, OAM/critical bits, and variable-length options.

Important APIs/types: `GENEVE_UDP_PORT` is 6081. `struct geneve_opt` represents one option header with class, type, reserved bits, length, and flexible data. `GENEVE_CRIT_OPT_TYPE` identifies critical option type bit. `struct genevehdr` contains version, option length, OAM/critical flags, protocol type, 24-bit VNI, reserved byte, and option data. `netif_is_geneve()` detects rtnetlink devices whose kind is `"geneve"`. Under `CONFIG_INET`, `geneve_dev_create_fb()` creates a fallback device.

Control flow and state: this header only describes on-wire layout and device detection. Runtime state lives in Geneve net devices, UDP sockets, tunnel metadata, and options parsed elsewhere.

Dependencies and integration: includes `udp_tunnel.h`, and integrates with tunnel offload, flower encap-option matching, routing, and netdev rtnl link ops.

Risks: bitfield layout is endian-sensitive and option length units must match protocol expectations. Critical options need explicit handling to avoid accepting unsupported semantics. Tests should cover encode/decode of VNI and option length, OAM/critical flags, device-kind detection, fallback device creation, offload matching on Geneve options, and malformed option truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/geneve.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/gre.h -->
# sources/distributed-fs/ceph-client/include/net/gre.h

Purpose: declares Generic Routing Encapsulation header formats, protocol registration, parsing, device helpers, and inline transmit header construction.

Important APIs/types: `gre_base_hdr` contains flags and encapsulated protocol; `gre_full_hdr` adds checksum/reserved/key/sequence fields. `struct gre_protocol` supplies receive and error handlers. `gre_add_protocol()` and `gre_del_protocol()` register handlers by GRE version. Device helpers detect `gretap` and `ip6gretap`, while `gretap_fb_dev_create()` creates a fallback device. `gre_parse_header()` extracts tunnel packet info. Inline helpers map between IP tunnel flags and GRE flags, calculate header length, and build an skb GRE header.

Control flow and state: transmit code computes optional fields from tunnel flags, pushes the header, sets inner protocol and transport header, writes optional sequence/key/checksum from the end backward, and configures checksum offload if needed. Protocol handler state is registered externally.

Dependencies and integration: depends on skbuffs and `ip_tunnels.h`; integrates with IP tunnel devices, GSO types `SKB_GSO_GRE*`, checksum offload, rtnetlink, and receive protocol dispatch.

Risks: optional-field ordering and header length must match flags exactly. Checksum behavior differs for GSO GRE checksum and CHECKSUM_PARTIAL. Tests should cover all flag combinations, checksum and no-checksum GRE, key/sequence parsing, gretap device kind, malformed short headers, and tunnel offload metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/gre.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/gro.h -->
# sources/distributed-fs/ceph-client/include/net/gro.h

Purpose: declares Generic Receive Offload control metadata and helpers for aggregating compatible skbs before the stack processes them. It includes checksum validation/conversion, remote checksum handling, recursion guards, protocol dispatch declarations, network flush decisions, and normal-list batching.

Important APIs/types: `struct napi_gro_cb` overlays `skb->cb` with fragment pointers, data offsets, flush/count/proto fields, checksum state, encapsulation mark, recursion counter, list mode, and L3 offsets. `NAPI_GRO_CB()` accesses it. `call_gro_receive*()` enforce `GRO_RECURSION_LIMIT`. Header helpers manage GRO offsets and fast/slow pulls. Checksum macros validate pseudo-header checksums and mark checksum-unnecessary state. `skb_gro_remcsum_process()` and cleanup handle remote checksum adjustment. Flush helpers compare IPv4/IPv6 headers. `gro_normal_one()` batches normal skbs up to `net_hotdata.gro_normal_batch`.

Control flow and state: GRO receive callbacks advance `data_offset`, validate headers/checksums, compare candidate packets, set flush bits for incompatible packets, and eventually merge or pass normal skbs up. State is per-skb in the control block and per-NAPI in `gro_node`.

Dependencies and integration: depends on IP/IPv6, UDP, checksum, skbuff, `hotdata.h`, netdevice GRO nodes, indirect calls, and packet offloads.

Risks: skb control-block ownership, recursion, checksum conversion, and encapsulated offset handling are fragile. Tests should include nested tunnels, remote checksum offload, CHECKSUM_COMPLETE and CHECKSUM_UNNECESSARY paths, IPv4 ID flush logic, IPv6 traffic-class flush, batching threshold, and malformed TCP header lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/gro.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/gro_cells.h -->
# sources/distributed-fs/ceph-client/include/net/gro_cells.h

Purpose: declares per-CPU GRO cells used by virtual or tunnel devices to feed received skbs into GRO safely and scalably.

Important APIs/types: `struct gro_cells` contains a per-CPU pointer to `struct gro_cell` storage. `gro_cells_init()` allocates/initializes cells for a net device, `gro_cells_receive()` queues an skb into the appropriate cell/GRO path, and `gro_cells_destroy()` tears them down.

Control flow and state: this header only exposes lifecycle and receive entry points. Runtime state is per-CPU, tied to the device, and destroyed when the owning device exits. Receive code uses the per-CPU cell to avoid global contention before normal GRO/NAPI processing.

Dependencies and integration: depends on skbuffs, slab allocation, and netdevice definitions. It integrates with tunnel devices and virtual netdevices that do not receive packets from hardware NAPI directly.

Risks: teardown must not race with in-flight receive. Per-CPU allocation failures and device unregister paths need coverage. Tests should exercise init/receive/destroy, CPU migration stress, device down/unregister with queued skbs, and GRO aggregation behavior through tunnel devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/gro_cells.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/gso.h -->
# sources/distributed-fs/ceph-client/include/net/gso.h

Purpose: declares Generic Segmentation Offload helpers and per-skb GSO control metadata for splitting large skbs, including tunneled packets.

Important APIs/types: `struct skb_gso_cb` is stored at offset 32 in `skb->cb` and tracks MAC/data offset, encapsulation level, checksum accumulator, and checksum start. `skb_tnl_header_len()` computes tunnel header length from MAC offsets. `gso_pskb_expand_head()` expands headroom and adjusts stored offsets. `gso_reset_checksum()` records checksum state unless remote checksum offload is active. `gso_make_checksum()` builds a segment checksum from transport header to stored checksum start. Segmentation entry points include `__skb_gso_segment()`, `skb_gso_segment()`, Ethernet/MAC segment helpers, length validators, and `skb_gso_error_unwind()`.

Control flow and state: segmentation paths initialize control block state, possibly expand headroom, segment according to features, validate resulting lengths, and unwind skb headers on errors. State is transient in skb control block and checksum fields.

Dependencies and integration: depends on skbuff and netdev feature flags. It integrates with TCP/UDP segmentation, GRE/Geneve/GUE tunnels, checksum offload, and device transmit feature negotiation.

Risks: control-block offset overlap with other skb users, headroom expansion offset adjustment, and remote checksum exceptions are critical. Tests should cover tunnel and non-tunnel GSO, partial checksums, remcsum, segmentation failure unwind, MTU/mac-length validation, and devices with limited feature flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/gso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/gtp.h -->
# sources/distributed-fs/ceph-client/include/net/gtp.h

Purpose: defines GPRS Tunneling Protocol constants and wire headers for GTPv0, GTPv1-U, extension headers, and PDU session metadata.

Important APIs/types: port constants are `GTP0_PORT` 3386 and `GTP1U_PORT` 2152. Message constants include echo request/response and TPDU. `gtp0_header`, `gtp1_header`, and `gtp1_header_long` are packed protocol headers. `gtp_ie`, `gtp0_packet`, and `gtp1u_packet` represent recovery information-element packets. `gtp_pdu_session_info` stores 5G PDU type and QFI. `netif_is_gtp()` detects rtnetlink devices with kind `"gtp"`. Extension-header flags and `gtp_ext_hdr` describe optional GTP1 fields.

Control flow and state: this header is layout-only. Runtime tunnel/session state lives in GTP netdevices, PDP/session tables, UDP sockets, and rtnetlink configuration.

Dependencies and integration: depends on netdevice, types, and rtnetlink. It integrates with mobile-core tunnel devices, UDP encapsulation, packet parsing, and traffic classification/offload matching.

Risks: packed headers require careful unaligned access and length validation. GTPv1 optional flags control presence of sequence, N-PDU, and extension headers. Tests should cover v0/v1 header parsing, extension-header chains, device-kind detection, PDU session info extraction, malformed/truncated packets, and endian correctness of TEID/length fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/gtp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/gue.h -->
# sources/distributed-fs/ceph-client/include/net/gue.h

Purpose: defines Generic UDP Encapsulation header layout and validation helpers for standard and private option flags.

Important APIs/types: `struct guehdr` overlays the first word with version, control bit, header length, protocol/control type, and standard flags. `GUE_FLAG_PRIV` indicates a private flags extension. `GUE_PFLAG_REMCSUM` defines the remote-checksum private option. `guehdr_flags_len()` computes standard option length; `guehdr_priv_flags_len()` currently returns zero for known private flags; `validate_gue_flags()` checks unknown standard/private flags and ensures option lengths fit the header length.

Control flow and state: receive or transmit code reads `hlen`, derives option length, validates supported flags, and then parses optional private flags at the end of the standard option area. No persistent state is stored here.

Dependencies and integration: uses architecture byteorder and Linux types. It integrates with FOU/GUE tunnel headers, GRO remote checksum handling, and UDP tunnel offload.

Risks: bitfield layout is endian-dependent, and `validate_gue_flags()` performs pointer arithmetic into option data, so callers must ensure the base header and option area are present. Tests should include unknown standard/private flags, too-short options, remote checksum flag handling, control-vs-data headers, and both endian configurations where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/gue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/handshake.h -->
# sources/distributed-fs/ceph-client/include/net/handshake.h

Purpose: declares the kernel TLS handshake service interface, backed by generic netlink, for offloading handshake negotiation to a userspace agent while kernel sockets wait for completion.

Important APIs/types: `tls_done_func_t` is the async completion callback returning status and peer key serial. `struct tls_handshake_args` carries socket, callback, caller data, peer name, timeout, keyring, certificate/private-key serials, and up to five peer ids. Client and server entry points cover anonymous, X.509, and PSK modes: `tls_client_hello_*()` and `tls_server_hello_*()`. Lifecycle helpers include `tls_handshake_cancel()`, `tls_handshake_close()`, `tls_get_record_type()`, and `tls_alert_recv()`.

Control flow and state: a caller fills args, starts a handshake with allocation flags, and receives completion asynchronously. Cancellation is keyed by `struct sock`; close is keyed by `struct socket`. Record-type and alert helpers inspect ancillary data/messages after TLS is active.

Dependencies and integration: uses sockets, sock, msghdr/cmsghdr, key serials, GFP flags, and generic netlink service implementation. It is relevant to in-kernel consumers such as NFS/RPC-over-TLS and any distributed filesystem transport adopting kernel TLS.

Risks: async lifetime of socket and caller data must outlive completion or cancellation. Key serial zero has sentinel meanings. Tests should cover timeout, cancel vs completion races, missing keyring/certs, PSK and X.509 modes, close during pending handshake, alert parsing, and userspace agent failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/handshake.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/hotdata.h -->
# sources/distributed-fs/ceph-client/include/net/hotdata.h

Purpose: groups read-mostly networking fast-path globals into `struct net_hotdata` to improve cache locality. It includes protocol/offload registrations, skb caches, RPS state, deferred skb queues, and common sysctl-derived budget/limit values.

Important APIs/types: `struct skb_defer_node` stores a lockless deferred skb list and count, cacheline-aligned per CPU. `struct net_hotdata` contains IPv4/IPv6 packet offloads and protocol descriptors when INET is enabled, global offload list, skb slab caches, RPS tables/mask, per-CPU defer nodes, GRO normal batch, netdev budgets, backlog, qdisc burst/weights, max skb fragments, defer max, and per-CPU memory reserve. Macros expose hash secrets through protocol/offload fields.

Control flow and state: this header declares the global `net_hotdata`; runtime initialization populates protocol tables, caches, budgets, and sysctl values. Fast paths read these fields frequently, often through `READ_ONCE()`.

Dependencies and integration: depends on linked lists, netdevice, protocol/offload definitions, and optional RPS types. It integrates with GRO batching, protocol lookup, hash functions, skb allocation, and network sysctls.

Risks: because fields are global fast-path state, false sharing and unsynchronized mutation can hurt performance or correctness. Tests should exercise sysctl updates, GRO batch thresholds, protocol registration, RPS enabled/disabled builds, hash secret initialization, and deferred skb pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/hotdata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/hwbm.h -->
# sources/distributed-fs/ceph-client/include/net/hwbm.h

Purpose: declares a hardware buffer manager pool abstraction for drivers that manage reusable receive buffers outside the normal skb allocation path.

Important APIs/types: `struct hwbm_pool` tracks capacity, fragment size, current buffer count, a construction callback, a mutex protecting the count, and private driver data. Under `CONFIG_HWBM`, functions free a buffer back to the pool, refill the pool, and add buffers. Without the option, stubs compile away and return success.

Control flow and state: drivers initialize a pool, call add/refill to allocate buffers, and call `hwbm_buf_free()` when a buffer returns. Persistent state is in the pool object and driver-private data; the mutex serializes buffer counter changes.

Dependencies and integration: depends on Linux mutexes, GFP allocation flags, and driver receive paths. It integrates with network drivers and page/fragment recycling logic.

Risks: config-disabled stubs can hide missing runtime behavior in builds without HWBM. Buffer constructors must match fragment size and hardware DMA requirements. Tests should include refill failure, concurrent free/refill, constructor errors, pool exhaustion, config-on/off builds, and driver teardown with outstanding buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/hwbm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/icmp.h -->
# sources/distributed-fs/ceph-client/include/net/icmp.h

Purpose: declares IPv4 ICMP error/reporting interfaces and statistics macros. It lets IP and transport protocols send ICMP errors, handle received ICMP, convert ICMP errors to errno/fatal state, and maintain per-net ICMP counters.

Important APIs/types: `struct icmp_err` maps ICMP codes to `errno` and fatality; `icmp_err_convert[]` is the exported table. Stats macros increment ICMP and per-message counters. `__icmp_send()` is the main send helper with mark override; `icmp_send()` wraps it with zero mark. `icmp_ndo_send()` has a real or stub implementation depending on `CONFIG_IP_ROUTE_NH_FDB`. Receive/error/init functions include `icmp_rcv()`, `icmp_err()`, `icmp_init()`, `icmp_out_count()`, and `icmp_build_probe()`.

Control flow and state: protocols call send helpers when rejecting packets or reporting path errors. Receive path dispatches ICMP to error handlers and updates counters. State is per-network-namespace SNMP MIB data plus socket/error side effects.

Dependencies and integration: depends on Linux ICMP UAPI, `inet_sock.h`, SNMP, and `ip.h`. It integrates with IPv4 input/output, route error handling, PMTU discovery, and transport error queues.

Risks: ICMP generation must avoid loops, respect rate limits elsewhere, and preserve marks where needed. Tests should cover stats increments, errno mapping, PMTU errors, `icmp_ndo_send()` config variants, probe building, and malformed ICMP receive packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/icmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ieee80211_radiotap.h -->
# sources/distributed-fs/ceph-client/include/net/ieee80211_radiotap.h

Purpose: defines the radiotap metadata ABI used by 802.11 monitor-mode frames. It enumerates presence bits and field encodings for legacy, HT/VHT/HE/EHT, timestamp, AMPDU, LSIG, vendor namespaces, TLVs, and zero-length PSDU metadata.

Important APIs/types: `struct ieee80211_radiotap_header` contains version, pad, length, and present bitmaps. Numerous enums define `ieee80211_radiotap_presence`, flags, channel flags, RX/TX flags, MCS/VHT/HE/HE-MU/EHT fields, timestamp units/flags, LSIG fields, and vendor/TLV structures. `ieee80211_get_radiotap_len()` reads the little-endian `it_len` from raw data.

Control flow and state: this header is ABI/layout definition only. Producers build a radiotap header with present bits and aligned fields; consumers parse based on presence bitmaps and total length. There is no persistent kernel state here.

Dependencies and integration: depends on kernel unaligned helpers and fixed types. It integrates with mac80211, cfg80211, monitor interfaces, packet capture tools, and userspace sniffers.

Risks: radiotap is user-visible ABI; enum values and field layouts must not drift. Variable presence bitmaps and vendor/TLV fields need strict bounds and alignment handling. Tests should parse/build representative legacy, VHT, HE, HE-MU, EHT, vendor, and TLV headers, verify little-endian length reads, and fuzz truncated/misaligned headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ieee80211_radiotap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ieee802154_netdev.h -->
# sources/distributed-fs/ceph-client/include/net/ieee802154_netdev.h

Purpose: declares IEEE 802.15.4 netdevice MAC header formats, address conversion helpers, skb control metadata, MAC parameters, link-layer security callbacks, and MLME operations.

Important APIs/types: header structs model beacon, MAC command, security, frame-control, association, disassociation, and composite frame types. Enums cover frame version, addressing mode, association status, and disassociation reason. APIs push/pull/peek headers and MAC command payloads, compute max payload/header length, and compare/convert addresses. `struct ieee802154_mac_cb` overlays skb control data. `ieee802154_mac_params` stores PAN/channel/CSMA and timing parameters. `ieee802154_llsec_ops` and `ieee802154_mlme_ops` define security and management operations.

Control flow and state: transmit callers build an `ieee802154_hdr`, push it into an skb, and pass to device code. Receive callers pull or peek headers, initialize `mac_cb`, and dispatch MLME/security operations. Persistent state lives in netdevice/private WPAN PHY, MAC parameters, and security tables, not this header.

Dependencies and integration: depends on AF IEEE802154, netdevice, skbuff, Linux IEEE802154 types, and cfg802154. It integrates with low-rate wireless drivers and 6LoWPAN stacks.

Risks: variable address modes and security headers make length calculation error-prone. skb control-block size must hold `ieee802154_mac_cb`. Tests should cover all addressing modes, short/extended address conversion, beacon/MAC command push-pull round trips, security callbacks, MLME operations, scan types, and malformed/truncated frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ieee802154_netdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ieee8021q.h -->
# sources/distributed-fs/ceph-client/include/net/ieee8021q.h

Purpose: maps IETF DSCP and IEEE 802.1Q traffic types/classes. It provides a common enum and conversion hooks for QoS classification.

Important APIs/types: `enum ieee8021q_traffic_type` names traffic types such as best effort, background, excellent effort, critical applications, video, voice, internetwork control, and network control. `SIMPLE_IETF_DSCP_TO_IEEE8021Q_TT()` maps DSCP by the upper traffic-class bits. When `CONFIG_INET` is enabled, `ietf_dscp_to_ieee8021q_tt()` and `ieee8021q_tt_to_tc()` are extern functions; otherwise inline stubs provide simple mapping and `-EINVAL`.

Control flow and state: callers convert DSCP to an 802.1Q traffic type, then map the traffic type to a traffic class based on number of queues. No persistent state is declared.

Dependencies and integration: depends on errno and DSCP conventions. It integrates with qdisc, VLAN/priority mapping, DCB-like traffic classes, and drivers exposing multiple queues.

Risks: config-disabled behavior differs from full mapping, especially traffic-class conversion. Tests should cover DSCP boundary values, invalid queue counts, `CONFIG_INET` and non-INET builds, and expected queue selection for QoS-sensitive traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ieee8021q.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/if_inet6.h -->
# sources/distributed-fs/ceph-client/include/net/if_inet6.h

Purpose: defines IPv6 per-interface address, multicast, anycast, and device state structures. It is the main header for `inet6_dev` and `inet6_ifaddr` state.

Important APIs/types: `struct inet6_ifaddr` stores IPv6 address, peer, timers, prefix lengths, scope, flags, lifetimes, timestamps, route pointer, device pointer, hash/list nodes, and refcount/RCU. Multicast structures include socket source filters, per-device multicast entries, and anycast entries. `struct inet6_dev` stores device pointer, address/multicast/anycast lists, sysctl/devconf pointers, stats, token, stable secret, locks, timers, ND/RS/RA state, refcounts, and RCU. Inline helpers map IPv6 multicast addresses to Ethernet, ARCnet, InfiniBand, and GRE multicast link-layer forms.

Control flow and state: address configuration code adds/removes `inet6_ifaddr` objects under locks and RCU; timers manage DAD, lifetimes, and multicast reports. `inet6_dev` persists as per-netdevice IPv6 state until device teardown.

Dependencies and integration: depends on SNMP, IPv6, refcounting, netdevice, timers, RCU, and device configuration. It integrates with IPv6 addrconf, multicast listener discovery, neighbor discovery, routing, and socket source selection.

Risks: address lifetime timers, RCU teardown, and multicast source-filter lists are race-prone. Tests should cover address add/delete, DAD, temporary/stable privacy addresses, multicast joins/leaves, stats access, link-layer multicast mapping, device unregister, and refcount leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/if_inet6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ife.h -->
# sources/distributed-fs/ceph-client/include/net/ife.h

Purpose: declares Intermediate Functional Block Encapsulation metadata helpers used by tc actions to attach or remove metadata TLVs around Ethernet frames.

Important APIs: when `CONFIG_NET_IFE` is enabled, `ife_encode()` and `ife_decode()` add/remove IFE encapsulation and return data pointers/metadata length. TLV helpers decode, encode, and advance metadata entries: `ife_tlv_meta_decode()`, `ife_tlv_meta_encode()`, and `ife_tlv_meta_next()`. When disabled, inline stubs return `NULL` or zero.

Control flow and state: encode/decode operates directly on skb data, while TLV helpers walk variable-length metadata. No persistent state is declared in this header.

Dependencies and integration: depends on Ethernet device helpers, rtnetlink, and UAPI IFE definitions. It integrates with tc IFE actions and metadata classifiers/actions.

Risks: disabled stubs can make callers silently skip behavior. TLV parsing must validate lengths and end pointers to avoid overreads. Tests should cover encode/decode round trips, multiple TLVs, malformed TLV lengths, metadata length accounting, config-disabled stubs, and tc action integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ife.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/inet6_connection_sock.h -->
# sources/distributed-fs/ceph-client/include/net/inet6_connection_sock.h

Purpose: declares IPv6-specific helpers for connection-oriented INET sockets. It complements `inet_connection_sock.h` with IPv6 route and transmit operations.

Important APIs: `inet6_csk_route_socket()` resolves a route for an existing socket and flow. `inet6_csk_route_req()` resolves a route for a request socket/child creation path. `inet6_csk_xmit()` transmits an skb for a connected IPv6 socket using a generic `flowi`.

Control flow and state: TCP/connection-oriented IPv6 code builds a `flowi6`, resolves dst entries for sockets or SYN requests, then transmits through `inet6_csk_xmit()`. Persistent state lives in the `sock`, request socket, dst cache, and IPv6 cork/options structures.

Dependencies and integration: forward-declares flow, request, skb, sock, and sockaddr types. It integrates with TCPv6, MPTCP/ULP paths, route lookup, request socket creation, and common inet connection timers/state.

Risks: wrong flow construction or route reuse can send with stale source address, mark, or bound device. Tests should cover IPv6 connect/listen/SYN-ACK routing, bound device and l3mdev behavior, PMTU changes, flow-label/tclass propagation, and transmit errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/inet6_connection_sock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/inet6_hashtables.h -->
# sources/distributed-fs/ceph-client/include/net/inet6_hashtables.h

Purpose: declares IPv6 socket lookup and hash helpers for established, listener, reuseport, BPF sk_lookup, and skb-steal paths.

Important APIs/types: `inet6_init_ehash_secret()` initializes hash secret. `__inet6_ehashfn()` combines local and foreign IPv6 hashes, ports, and net hash. Lookup APIs include `__inet6_lookup_established()`, `inet6_lookup_reuseport()`, `inet6_lookup_listener()`, `inet6_lookup_run_sk_lookup()`, `__inet6_lookup()`, `__inet6_lookup_skb()`, and `inet6_lookup()`. `inet6_steal_sock()` mirrors IPv4 skb socket stealing and may switch to reuseport. `inet6_match()` validates namespace, addresses, ports, and bound-device constraints.

Control flow and state: receive code first tries an attached skb socket, handles prefetched TCP listeners/UDP closed sockets via reuseport, then falls back to established lookup and listener lookup. Refcount behavior differs for established versus listener sockets and must be tracked by callers.

Dependencies and integration: depends on IPv6 address types, jhash, inet sock, IPv6 helpers, per-net hash secret, reuseport, BPF sk_lookup, and device index functions.

Risks: refcounted and non-refcounted returns are easy to misuse. Bound device and v4-mapped address matching affect isolation. Tests should cover established/listener fallbacks, reuseport selection, BPF sk_lookup overrides, skb stolen sockets, refcount failure, l3mdev/sdif matching, and IPv4-mapped IPv6 sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/inet6_hashtables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/inet_common.h -->
# sources/distributed-fs/ceph-client/include/net/inet_common.h

Purpose: declares common IPv4/INET socket operations shared by stream and datagram protocols, plus GRO/GSO hooks and control-socket lifecycle.

Important APIs/types: exported `inet_stream_ops` and `inet_dgram_ops` are protocol operation tables. Socket operation declarations cover release, connect, accept, send/recv, shutdown, listen, bind, getname, ioctl, control-socket create/destroy, receive error, and socket destruct. Bind flags control address-no-port, locking, BPF-originated bind, and capability checks. GRO/GSO functions include `inet_gro_receive()`, `inet_gro_complete()`, and `inet_gso_segment()`. Indirect-call macros optimize GRO callback dispatch.

Control flow and state: socket syscalls enter these common helpers, which then delegate to protocol-specific `struct proto` hooks. Control sockets are created for kernel internal protocols and destroyed by `inet_ctl_sock_destroy()`. Persistent state lives in `struct sock` and derived `inet_sock`.

Dependencies and integration: depends on socket, netdev features, indirect-call wrappers, and `net/sock.h`. It integrates with TCP, UDP, RAW, ping sockets, GRO/GSO, and BPF bind paths.

Risks: bind flag combinations alter security and port allocation semantics. Common helpers affect all INET protocols, so regressions are broad. Tests should cover stream/datagram connect, bind variants, listener accept, shutdown, error queue receive, GRO/GSO paths, control-socket lifecycle, and BPF bind behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/inet_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/inet_connection_sock.h -->
# sources/distributed-fs/ceph-client/include/net/inet_connection_sock.h

Purpose: defines the common state and helpers for connection-oriented INET sockets, especially TCP-like protocols. It extends `inet_sock` with accept queue, bind buckets, retransmit/delayed-ACK/keepalive timers, PMTU probing, congestion control, ULP hooks, and address-family operations.

Important APIs/types: `struct inet_connection_sock_af_ops` provides AF-specific transmit, header rebuild, dst set, connection request, SYN receive child creation, socket options, and MTU reduction hooks. `struct inet_connection_sock` holds timers, RTO values, PMTU cookie, congestion-control private area, delayed ACK state, MTU probe state, user timeout, and ULP data. Helpers schedule/clear ACKs, initialize/clear/reset transmit timers, accept children, get ports, route requests/children, manage request queues, start/stop listening, update PMTU, ping-pong mode, and initialize locks.

Control flow and state: listen paths allocate request sockets, hash them, complete hashdance into children, and queue accepted sockets. Established paths manage timers and congestion/ACK state. State is long-lived in the socket and protected by socket locks, timers, memory barriers, and request-queue locks.

Dependencies and integration: depends on inet/request sock, timers, poll, sockptr, congestion control, ULP, TCP states, and IPv4/IPv6 AF ops.

Risks: timer state transitions and request queue accounting are race-prone. Congestion private size is fixed. Tests should cover SYN queue add/drop/hashdance, timer reset/clear, delayed ACK scheduling, PMTU update, accept queue polling, ULP presence, ping-pong counters, and close/destroy cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/inet_connection_sock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/inet_dscp.h -->
# sources/distributed-fs/ceph-client/include/net/inet_dscp.h

Purpose: defines a bitwise-distinct DSCP type and helpers for converting between IP DS fields and DSCP values.

Important APIs/types: `typedef u8 __bitwise dscp_t` prevents accidental mixing with raw bytes. `INET_DSCP_MASK` selects the upper six DS bits, while `INET_ECN_MASK` is provided externally in IP ECN headers. `INET_DSCP_LEGACY_TOS_MASK` covers legacy TOS precedence-style bits. `inet_dsfield_to_dscp()` masks a DS field into a DSCP, `inet_dscp_to_dsfield()` converts back to a byte with ECN cleared, and `inet_validate_dscp()` checks raw values.

Control flow and state: callers convert TOS/traffic-class values when storing flow keys or socket DSCP fields. There is no persistent state.

Dependencies and integration: depends on Linux types and is included by `flow.h`, `ip.h`, `inet_sock.h`, and QoS mapping code. It integrates with route lookup, socket TOS settings, tc classifiers, and ECN helpers.

Risks: DSCP and ECN bits share the same octet; callers must avoid losing ECN when only DSCP should change. Tests should cover all DSCP ranges, ECN-preserving callers, invalid raw values, bitwise type warnings, and flow/socket DSCP propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/inet_dscp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/inet_ecn.h -->
# sources/distributed-fs/ceph-client/include/net/inet_ecn.h

Purpose: declares Explicit Congestion Notification helpers for IPv4, IPv6, TCP, tunnels, and skb encapsulation. It centralizes ECN codepoint tests, CE marking, decapsulation rules, and congestion propagation.

Important APIs/functions: helpers classify ECN bits as not-ECT, ECT(0), ECT(1), or CE, test capability, and set CE in IP/IPv6 headers or skbs. Tunnel helpers implement RFC-style ingress/egress ECN handling, including `INET_ECN_encapsulate()`, `INET_ECN_decapsulate()`, and IPv4/IPv6 variants. TCP helpers inspect or clear ECN state in TCP headers. The header also provides skb-level functions to mark CE and update checksums.

Control flow and state: transmit encapsulation combines inner and outer ECN values; receive decapsulation validates combinations and may drop or propagate CE. Persistent state is not stored here, but packet headers and skb metadata are mutated.

Dependencies and integration: integrates with IP, IPv6, TCP, tunnels, GRO/GSO, and fragmentation ECN tables. It is used by tunnel devices and congestion-aware transports.

Risks: incorrect ECN propagation can cause congestion-signal loss or invalid CE combinations. Header checksum updates are required when IPv4 TOS changes. Tests should cover every inner/outer ECN matrix, CE marking checksums, non-ECT tunnel decap behavior, TCP ECN flags, GSO/GRO interactions, and fragmented packet ECN reassembly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/inet_ecn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/inet_frag.h -->
# sources/distributed-fs/ceph-client/include/net/inet_frag.h

Purpose: declares common IPv4/IPv6 fragment queue infrastructure. It provides per-netns fragment directories, fragment queue objects, fragment family operations, memory accounting, ECN combination support, insertion return codes, and reassembly helpers.

Important APIs/types: `struct fqdir` stores thresholds, timeout, max distance, dead flag, rhashtable, atomic memory use, destroy work, and free list. `struct inet_frag_queue` stores v4/v6 keys, timer, lock, refcount, rb-tree fragments, tail/run pointers, timestamp, length/meat, flags, max size, directory, and RCU. `struct inet_frags` defines constructor/destructor/expire callbacks, cache, rhashtable params, refcount, and completion. APIs initialize/finalize families and directories, find/kill/destroy queues, flush queues, insert fragments, prepare/finish reassembly, and pull the head skb.

Control flow and state: receive paths find or create a queue, insert fragments by offset into an rb-tree, track meat/len/flags and memory, then reassemble when complete or flush/expire on timeout/memory pressure. State persists in per-netns rhashtables until complete/expired.

Dependencies and integration: depends on rhashtable, timers, rbtrees, refcounts, completion, and drop reasons. It integrates with IPv4/IPv6 defrag, conntrack, bridge, AF_PACKET, and virtual-server users.

Risks: overlap handling, memory accounting, queue refcounts, and expiration races are high-risk. Tests should cover duplicate/overlap returns, ECN table combinations, high/low threshold pruning, namespace exit, timer expiry, reassembly coalescing, and drop reasons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/inet_frag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/inet_hashtables.h -->
# sources/distributed-fs/ceph-client/include/net/inet_hashtables.h

Purpose: defines IPv4/common INET bind, listen, established, and connect hash infrastructure for TCP/UDP-like sockets.

Important APIs/types: hash structures include `inet_ehash_bucket`, `inet_bind_bucket`, `inet_bind2_bucket`, bind hash buckets, listener buckets, and `inet_hashinfo`. Helpers compute bind and port/address hashes, allocate/free per-net hashinfo, create/destroy/find bind buckets, decide when bhash2 applies, update/reset bound source address, bind/hash/unhash sockets, inherit ports, and look up established/listener sockets. Lookup helpers include skb stealing, reuseport lookup, BPF sk_lookup, combined port/address macros, and `inet_match()`.

Control flow and state: bind inserts sockets into local-port and optionally port/address tables, with fastreuse flags to avoid expensive scans. Receive lookup tries established sockets, then listeners, with special handling for attached skb sockets and reuseport. Connect chooses ephemeral ports and checks time-wait conflicts through hash callbacks. Persistent state is in hash tables, buckets, socket nodes, refcounts, and RCU/nulls lists.

Dependencies and integration: depends on inet connection sock, sock, route, IP, TCP states, refcounting, byteorder, per-net hash secrets, BPF, and reuseport.

Risks: hash/list/refcount correctness is critical for socket demux and port reuse. Tests should cover bind conflict rules, bhash2 source-specific binds, wildcard listeners, reuseport, skb-steal, TCP_NEW_SYN_RECV/TIME_WAIT transitions, port inheritance, namespace isolation, and concurrent hash/unhash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/inet_hashtables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/inet_sock.h -->
# sources/distributed-fs/ceph-client/include/net/inet_sock.h

Purpose: defines `struct inet_sock`, IPv4 request/cork/options structures, socket flags, and helpers shared by INET protocols.

Important APIs/types: `struct ip_options` and `ip_options_rcu` store IPv4 options. `struct inet_request_sock` extends request sockets with addresses, ports, TCP option negotiation flags, mark, and IPv4/IPv6 options. `struct inet_cork` and `inet_cork_full` persist packet-building state while a socket is corked. `struct inet_sock` embeds `struct sock` first, optional IPv6 info, address/port aliases, flags, source address, options, IPID counter, TOS/TTL/PMTU/multicast fields, local port range, multicast list, and cork. Flag helpers manipulate `inet_flags`, and conversion helpers handle full sockets, request sockets, and time-wait exclusion.

Control flow and state: socket create/configure paths set options and flags; transmit paths read cork and address fields; receive lookup uses address/port aliases. `inet_sk_state_load()` pairs with state stores for lockless readers. Request helpers derive mark and bound device from listener/sysctls.

Dependencies and integration: depends on flow, DSCP, sock, request sock, TCP states, l3mdev, and netns hash. It underpins TCP, UDP, RAW, ping, IPv6 dual-stack, and route lookup.

Risks: first-member layout and alias macros are structural contracts. Atomic flag and state access must respect concurrency. Tests should cover socket option flags, corked sends, request mark/bound-device inheritance, nonlocal bind validation, full-socket conversion, checksum-conversion counters, and IPv4/IPv6 dual-stack fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/inet_sock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/inet_timewait_sock.h -->
# sources/distributed-fs/ceph-client/include/net/inet_timewait_sock.h

Purpose: defines the compact INET TIME_WAIT socket representation and lifecycle helpers. It keeps enough 4-tuple, bind, mark, routing, timestamp, and policy state to enforce protocol TIME_WAIT semantics with lower memory use than a full socket.

Important APIs/types: `struct inet_timewait_sock` begins with `sock_common` and aliases family, state, refcount, hash nodes, addresses, ports, cookie, and net namespace. Additional fields store mark, substate, receive scale, source port, transparency, flowlabel/TOS, txhash, priority, entry timestamp, timer, bind buckets, optional PSP association, and optional xmit validation hook. APIs allocate/free/put, bind-unhash, schedule hashdance into time-wait, schedule/reschedule/deschedule timers, purge hash tables, and get/set namespace.

Control flow and state: connection close creates a time-wait object from the full socket, hashes it, schedules its timer, and eventually frees it after timeout or purge. State persists in bind/established hash tables and timer lists until expiry.

Dependencies and integration: depends on inet sock, sock, TCP states, timewait core, timers, workqueue, atomics, and inet hashinfo. It integrates with TCP close, connect conflict checks, port reuse, and namespace cleanup.

Risks: time-wait hashdance must not lose bind bucket references. Timer and refcount races can leak or use-after-free. Tests should cover allocation from full socket, hashdance, reschedule/deschedule, purge during namespace exit, bind unhash, reuse decisions, and optional validate-xmit hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/inet_timewait_sock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/inetpeer.h -->
# sources/distributed-fs/ceph-client/include/net/inetpeer.h

Purpose: declares the inet peer cache, a per-destination store for long-lived peer metadata such as route metrics, ICMP rate limiting, redirects, and fragment receive ids.

Important APIs/types: `struct inetpeer_addr` stores IPv4 or IPv6 keys with family. `struct inet_peer` is an rb-tree node containing destination address, metrics, rate tokens, redirect count, last rate time, either atomic fragment id or RCU hook, deletion time, and refcount. `struct inet_peer_base` owns the rb-tree, seqlock, and total count. Helpers set/get IPv4/IPv6 keys, compare peer addresses, get peers by generic/v4/v6 key, put peers, test ICMP rate limit allowance, and invalidate a tree.

Control flow and state: callers look up or create peers in a base, mutate metrics/rate state while referenced, then put. Unreferenced peers can be queued for RCU deletion, at which point the `rid` storage is unavailable. State persists in memory across packets for a destination.

Dependencies and integration: depends on IPv6, jiffies, spinlocks/seqlocks, rtnetlink, atomics, and route metrics. It integrates with IPv4/IPv6 routing, ICMP rate limiting, redirects, and fragmentation id generation.

Risks: rb-tree ordering, refcount/RCU reuse of storage, and seqlock updates are delicate. Tests should cover v4/v6 key comparisons, peer get/put races, metrics initialization, ICMP rate token behavior, tree invalidation, and fragment id access before deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/inetpeer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ioam6.h -->
# sources/distributed-fs/ceph-client/include/net/ioam6.h

Purpose: declares IPv6 In-situ OAM namespace/schema state and event/trace helpers. IOAM carries telemetry data inside IPv6 packets.

Important APIs/types: `struct ioam6_namespace` is an rhashtable/RCU object with optional schema pointer, namespace id, narrow data, and wide data. `struct ioam6_schema` is another rhashtable/RCU object with linked namespace, id, length, header, and flexible data. `struct ioam6_pernet_data` stores a mutex and namespace/schema rhashtables. `ioam6_pernet()` returns per-net IOAM data when IPv6 is enabled. APIs find namespaces, fill trace data into an skb, compute trace node length, initialize/exit core and iptunnel support, and emit IOAM generic-netlink events.

Control flow and state: netlink/config code creates namespaces and schemas under the per-net mutex, packet paths look up namespaces and fill trace data, and events notify userspace. State persists per network namespace in rhashtables and is reclaimed via RCU.

Dependencies and integration: depends on IPv6, IOAM UAPI/genl headers, rhashtable, skbuff, network namespaces, and tunnel code. It integrates with IPv6 extension headers, lightweight tunnels, and Generic Netlink control.

Risks: schema/namespace RCU lifetimes and trace length calculations must match packet space. Tests should cover namespace/schema add/delete, trace fill for input/output, node length for all trace bits, IPv6-disabled builds, tunnel init/exit, and netlink event emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ioam6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ip.h -->
# sources/distributed-fs/ceph-client/include/net/ip.h

Purpose: central IPv4 networking header for packet metadata, output/input prototypes, fragmentation, corked sends, stats, PMTU/MTU helpers, IPID selection, multicast address mapping, defrag users, options, cmsg handling, and socket option wrappers.

Important APIs/types: `struct inet_skb_parm` overlays `skb->cb` for IPv4 flags, ingress ifindex, options, and frag max size. `struct ipcm_cookie` carries sendmsg control state. `ip_ra_chain` stores router-alert sockets. Fragment helpers use `ip_fraglist_iter` and `ip_frag_state`. Core APIs include `ip_rcv()`, `ip_local_deliver()`, `ip_output()`, `ip_do_fragment()`, `ip_queue_xmit()`, `ip_append_data()`, `ip_make_skb()`, `ip_send_skb()`, datagram connect, unicast reply, defrag, forward, options, cmsg, sockopt, and error helpers.

Control flow and state: receive enters `ip_rcv()`, may defrag, route, deliver locally/forward, and update MIB counters. Send paths build `flowi4`, append/cork payload into write queues, make skbs, select IPID, set checksums/options, fragment if needed, and output. PMTU helpers choose MTU from route, sysctls, device MTU, and lwtunnel headroom.

Dependencies and integration: depends on inet sock, route, SNMP, flow, flow dissector, netns hash, lwtunnel, DSCP, dst metrics, ICMP, and proc/sysctl optional code.

Risks: skb control-block aliasing, PMTU policy, IP options, fragmentation, and checksum/IPID updates are high risk. Tests should cover sendmsg cmsg, cork/flush, fragmentation with DF/PMTU, defrag users, route scope, multicast MAC mapping, options echo/compile, error queues, stats counters, and sysctl-influenced behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ip6_checksum.h -->
# sources/distributed-fs/ceph-client/include/net/ip6_checksum.h

Purpose: declares IPv6 pseudo-header checksum helpers for TCP, UDP, GSO, and skb checksum setup.

Important APIs/functions: `csum_ipv6_magic()` computes the IPv6 pseudo-header checksum unless provided by architecture code. `ip6_compute_pseudo()` computes an skb pseudo checksum from IPv6 source/destination, payload length, and protocol. `tcp_v6_check()` and `udp_v6_check()` are protocol-specific wrappers. `__tcp_v6_send_check()` initializes a TCP checksum field and skb checksum start/offset for transmit offload. `tcp_v6_gso_csum_prep()` prepares a TCPv6 GSO skb by zeroing payload length and setting pseudo checksum for length zero. `udp6_set_csum()` configures UDPv6 checksum behavior, including no-check cases.

Control flow and state: transmit paths call these helpers before handing skbs to checksum offload or software checksum completion. State mutated is in packet headers and skb checksum metadata.

Dependencies and integration: depends on byteorder, generic checksums, `ip.h`, IPv6 and TCP headers. It integrates with TCPv6, UDPv6, GSO, GRO pseudo checksum validation, and device checksum offload.

Risks: IPv6 UDP checksums are generally mandatory, so no-check handling must be explicit. GSO length-zero pseudo checksums must match segmentation code. Tests should cover TCPv6/UDPv6 checksum correctness, CHECKSUM_PARTIAL setup, GSO prep, zero-length payloads, no-check UDP paths, and architecture-provided checksum variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ip6_checksum.h -->
