# subset-b-005945 grouped research

Grouped research for Linux networking and MANA/MCTP/netfilter headers under `sources/distributed-fs/ceph-client/include/net`. Each section preserves the source path in the title and is delimited for deterministic source-tree-aligned splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mac802154.h -->
# sources/distributed-fs/ceph-client/include/net/mac802154.h

## Purpose
`mac802154.h` is the public in-kernel driver interface for IEEE 802.15.4 radios. It describes hardware capabilities, callback operations, frame-address helpers, endian conversion helpers, and registration/completion entry points used by low-level transceiver drivers and the mac802154 core.

## Important APIs, types, and functions
`struct ieee802154_hw`, `struct ieee802154_hw_addr_filt`, `enum ieee802154_hw_flags`, `enum ieee802154_hw_addr_filt_flags`, and `struct ieee802154_ops` are the central contracts. Exported declarations cover `ieee802154_alloc_hw`, `ieee802154_free_hw`, `ieee802154_register_hw`, `ieee802154_unregister_hw`, `ieee802154_rx_irqsafe`, `ieee802154_xmit_complete`, `ieee802154_xmit_error`, and `ieee802154_xmit_hw_error`. Inline helpers decode frame-control-address layout and convert unaligned 16/64-bit address byte orders.

## Control flow
Drivers allocate hardware with private storage, fill PHY and capability data, register with mac802154, then receive stack callbacks for start/stop, synchronous or asynchronous transmit, energy detect, channel setup, filtering, power, CCA, CSMA, retries, and promiscuous mode. RX can be delivered from IRQ context through `ieee802154_rx_irqsafe`; TX ownership returns through completion or error callbacks. Address helpers walk the skb MAC header based on source/destination addressing modes and intra-PAN compression.

## State and persistence
The header defines no persistent storage. Runtime state is in the allocated `ieee802154_hw`, the embedded `wpan_phy`, driver-private memory, skb ownership, PAN/address filter settings, and hardware flags. Several callbacks are documented as called with `pib_lock` held, so driver state must respect mac802154 locking.

## Dependencies and integration points
It depends on Linux skb APIs, `cfg802154`, 802.15.4 frame constants, unaligned access helpers, and device/module infrastructure. It integrates low-level radio drivers with the generic 802.15.4 netdevice/PHY stack.

## Risks and test signals
Risks include incorrect skb MAC-header bounds before address helper use, invalid address-mode decoding, endian conversion mistakes for 802.15.4 extended/short addresses, callback locking violations under `pib_lock`, deprecated synchronous transmit callbacks, and mismatched checksum-offload flags. Tests should cover all address-mode combinations, intra-PAN compression, IRQ RX delivery, TX completion/error ownership, feature-flag combinations, and register/unregister races.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mac802154.h` completely for this pass (489 lines, 15237 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mac802154.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/macsec.h -->
# sources/distributed-fs/ceph-client/include/net/macsec.h

## Purpose
`macsec.h` defines the MACsec Security Entity data model and offload callback ABI shared by the software MACsec driver, PHY offload providers, and MAC offload-capable netdevices.

## Important APIs, types, and functions
Important types are `sci_t`, `ssci_t`, `salt_t`, `pn_t`, `struct macsec_key`, RX/TX SC and SA structures, per-CPU stats structures, `struct macsec_secy`, `struct macsec_context`, and `struct macsec_ops`. Helper APIs include `macsec_pn_wrapped`, `macsec_send_sci`, `macsec_get_real_dev`, `macsec_netdev_is_offloaded`, `macsec_netdev_priv`, and `sci_to_cpu`.

## Control flow
MACsec control paths populate a `macsec_context` for device open/stop, SecY add/update/delete, RXSC/RXSA/TXSA updates, stats reads, and optional tag insertion. Packet-number state lives under SA spinlocks; SC/SA pointers are RCU-managed. Offload implementers use the same context union for MAC and PHY offload and return statistics through the union of stats pointers.

## State and persistence
State is runtime cryptographic and security-association state: keys and salts, next packet numbers, active flags, RCU/refcounted SC/SA lifetimes, per-CPU counters, replay protection settings, validation mode, ICV/key length, and offload metadata dst. No on-disk persistence exists; userspace configuration rebuilds state.

## Dependencies and integration points
It depends on crypto AEAD handles, netdevice/VLAN helpers, workqueue/RCU work, per-CPU u64 stats synchronization, and UAPI MACsec enums. It integrates with hardware drivers through `macsec_ops` exposed on devices or PHYs.

## Risks and test signals
Risks include PN wrap and XPN split-half handling, RCU/refcount teardown of active SAs, VLAN real-device private lookup, stats synchronization, mismatch between offload type and context union member, and SCI-insertion policy. Tests should exercise PN wrap callbacks, SA add/update/delete with `update_pn`, VLAN offload devices, RX/TX stats reads, `send_sci` policy with multiple RXSCs, and software/offload parity.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/macsec.h` completely for this pass (387 lines, 11011 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/macsec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mana/gdma.h -->
# sources/distributed-fs/ceph-client/include/net/mana/gdma.h

## Purpose
`gdma.h` is the core Microsoft Azure MANA GDMA hardware ABI and driver-internal interface. It defines request/response messages, queue formats, doorbells, DMA-region and memory-registration commands, capability negotiation, context state, and exported GDMA helper functions.

## Important APIs, types, and functions
Key types include `struct gdma_context`, `struct gdma_dev`, `struct gdma_queue`, `struct gdma_queue_spec`, `struct gdma_mem_info`, `struct gdma_resource`, `union gdma_doorbell_entry`, `struct gdma_req_hdr`, `struct gdma_resp_hdr`, queue WQE/CQE/EQE formats, and many HW command structs. Main functions are `mana_gd_init_req_hdr`, queue create/destroy/poll/ring helpers, work-request posting, resource-map allocation, DMA memory allocation/free, HWC request sending, debugfs registration, RDMA service events, suspend/resume, and logging policy.

## Control flow
The driver negotiates GDMA protocol/capability flags, lists and registers devices, creates DMA regions and queues, posts WQEs into SQ/RQ queues, rings doorbells, polls CQ/EQ owner-bit entries, and uses HWC commands for resource management. Queue head/tail semantics differ by queue type: SQ/RQ producer/consumer indexes are in 32-byte basic units, while EQ/CQ consume entries using owner bits.

## State and persistence
Persistent hardware-visible state includes queue IDs, doorbell IDs, PD IDs, GPA memory keys, DMA region handles, registered devices, MSI-X vectors, BAR mappings, and capability flags. Kernel runtime state includes xarray IRQ contexts, CQ tables, queue memory metadata, service workqueues, probe/service flags, and debugfs dentries. Hardware state survives until explicit destroy/deregister or PCI reset.

## Dependencies and integration points
It depends on PCI/device APIs, DMA mapping, netdevice types, auxiliary devices, xarray, debugfs, workqueues, completions, shared-memory bootstrap (`shm_channel.h`), and HWC (`hw_channel.h`). It is the common substrate for MANA Ethernet and MANA RDMA devices.

## Risks and test signals
Risks include bitfield ABI drift, natural-alignment assumptions for HW DATA structs, queue owner-bit wrap bugs, doorbell tail-unit mistakes, DMA page alignment and large-page capability negotiation, resource bitmap locking, HWC timeout/recovery handling, dynamic MSI-X allocation, and leaked hardware handles on partial failure. Tests should cover VF version negotiation, queue create/destroy, WQE post/ring, CQ/EQ wrap, DMA-region add-pages paths, suspend/resume, service EQEs, and capability-flag compatibility.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mana/gdma.h` completely for this pass (1021 lines, 22785 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mana/gdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mana/hw_channel.h -->
# sources/distributed-fs/ceph-client/include/net/mana/hw_channel.h

## Purpose
`hw_channel.h` defines the MANA hardware communication channel used to exchange management messages with the PF/firmware after shared-memory bootstrap.

## Important APIs, types, and functions
Important structures are HWC init unions, `struct hwc_rx_oob`, `struct hwc_tx_oob`, `struct hwc_work_request`, `struct hwc_dma_buf`, `struct hwc_cq`, `struct hwc_wq`, `struct hwc_caller_ctx`, and `struct hw_channel_context`. Public functions are `mana_hwc_create_channel`, `mana_hwc_destroy_channel`, and `mana_hwc_send_request`.

## Control flow
Channel creation builds bootstrap queues with fixed HWC init data IDs, maps DMA buffers for in-flight request/response messages, and wires CQ event callbacks. `mana_hwc_send_request` uses a semaphore and an inflight-resource map to reserve a message slot, posts a TX WQE with OOB routing to PF virtual queues, waits for completion with timeout, and copies the response into the caller buffer.

## State and persistence
Runtime state includes RX/TX GDMA queues, one CQ, DMA-backed in-flight request slots, caller completion context, PF destination queue IDs, negotiated maximum request/response sizes, and HWC timeout. There is no disk persistence; firmware-visible queue and DMA state is torn down by channel destruction.

## Dependencies and integration points
It depends on GDMA WQE/SGE/queue types, Linux completions, semaphores, device memory, and the shared memory channel that bootstraps initial HWC queue data. It integrates GDMA resource management and MANA NIC/RDMA commands.

## Risks and test signals
Risks include request/response size overflow, timeout recovery, stale `caller_ctx`, inflight slot leaks, OOB bitfield mismatch, CQ callback ordering, and bootstrap queue-depth assumptions. Tests should exercise channel create/destroy, parallel requests, timeout paths, PF reconfiguration events, and max-size boundary handling.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mana/hw_channel.h` completely for this pass (211 lines, 4133 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mana/hw_channel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mana/mana.h -->
# sources/distributed-fs/ceph-client/include/net/mana/mana.h

## Purpose
`mana.h` defines the Microsoft Azure Network Adapter Ethernet-facing data structures, hardware command ABI, queue objects, statistics, XDP hooks, RSS state, and public driver function declarations built on GDMA/HWC.

## Important APIs, types, and functions
Core types are `struct mana_context`, `struct mana_port_context`, `struct mana_txq`, `struct mana_rxq`, `struct mana_cq`, `struct mana_tx_qp`, TX/RX OOB and completion structs, ethtool hardware/PHY stats, queue object specs, and hardware command request/response structs. Declared APIs cover transmit, attach/detach/probe/remove, queue allocation, RSS config, vport config, XDP, stats queries, bandwidth clamp/shaper support, RX buffer preallocation, skb unmapping, and WQ object management.

## Control flow
Probe queries device config and vPort config, allocates EQ/CQ/SQ/RQ queues, configures vPorts, registers filters, and publishes netdevices. TX builds short or long OOB descriptors and GDMA SGLs, posts to SQs, and reclaims via TX CQEs. RX posts page-backed buffers, processes RX CQEs including coalesced completions, runs XDP, updates RSS/indirection state, and fences/destroys RQs during teardown. Management commands use GDMA request headers through the HWC path.

## State and persistence
State spans per-adapter ports, per-port vport handles, queue objects, RX object tables, RSS hash key and indirection table, XDP programs and page pools, preallocated RX buffers, vport use counts, link state work, debugfs nodes, software stats, queried hardware/PHY counters, and net shaper handles. Hardware-visible state includes queue regions, WQ objects, filters, vPort configuration, CQ moderation, and bandwidth clamp settings.

## Dependencies and integration points
It depends on GDMA/HWC, netdevice core, XDP/page_pool, ethtool, debugfs, workqueues, u64 stats sync, net shaper UAPI, and Linux DMA/skb APIs. It integrates Ethernet and RDMA personalities through common GDMA devices.

## Risks and test signals
Risks include hardware bitfield ABI mismatch, queue size and RX/TX buffer limits, short-form vport offset overflow, XDP/page-pool lifetime bugs, DMA unmap leaks, RSS table size constraints, stats count drift when structs change, CQE type handling gaps, queue reset races, and partial teardown after HWC timeout. Tests should cover probe/remove, attach/detach, multi-queue RSS, XDP drop/tx/redirect, TX GSO/checksum formats, RX coalesced CQEs, link changes, shaper bandwidth clamp, and suspend/resume recovery.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mana/mana.h` completely for this pass (1041 lines, 25117 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mana/mana.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mana/mana_auxiliary.h -->
# sources/distributed-fs/ceph-client/include/net/mana/mana_auxiliary.h

## Purpose
`mana_auxiliary.h` is a tiny bridge header defining the auxiliary-bus wrapper used to expose a MANA GDMA device as an auxiliary device.

## Important APIs, types, and functions
It includes `mana.h` and `<linux/auxiliary_bus.h>` and defines `struct mana_adev` with an embedded `struct auxiliary_device adev` and a pointer to the associated `struct gdma_dev`.

## Control flow
GDMA/MANA code can allocate or recover `mana_adev` around an auxiliary device so child drivers bind through the auxiliary bus while still reaching the GDMA device.

## State and persistence
It defines no behavior or persistence. Runtime state is the object lifetime of the auxiliary device and the referenced GDMA device.

## Dependencies and integration points
It depends on MANA core types and the Linux auxiliary bus. It integrates MANA Ethernet/RDMA child-device registration with the generic auxiliary-device framework.

## Risks and test signals
Risks are mostly lifetime-related: the embedded auxiliary device and `gdma_dev` pointer must remain valid across probe/remove and bus callbacks. Tests should cover auxiliary device registration, driver bind/unbind, and teardown ordering.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mana/mana_auxiliary.h` completely for this pass (10 lines, 223 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mana/mana_auxiliary.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mana/shm_channel.h -->
# sources/distributed-fs/ceph-client/include/net/mana/shm_channel.h

## Purpose
`shm_channel.h` defines the shared-memory bootstrap channel used by MANA to initialize or tear down the hardware communication channel before normal GDMA queues are available.

## Important APIs, types, and functions
It defines aperture geometry constants, `struct shm_channel`, and public functions `mana_smc_init`, `mana_smc_setup_hwc`, and `mana_smc_teardown_hwc`.

## Control flow
The driver initializes a shared-memory channel with a device and MMIO base, then uses setup to pass HWC EQ/CQ/RQ/SQ DMA addresses and an MSI-X index to firmware. Teardown optionally resets the VF and dismantles HWC bootstrap state.

## State and persistence
State is the device pointer and MMIO base plus firmware-visible bootstrap registers. There is no persistent software store; hardware retains setup until teardown or reset.

## Dependencies and integration points
It depends on MMIO access in the implementation and is included by GDMA context setup. It integrates PCI BAR shared-memory windows with HWC queue creation.

## Risks and test signals
Risks include aperture-size assumptions, wrong queue DMA addresses, reset-vs-no-reset teardown semantics, and MMIO ordering. Tests should cover VF bootstrap, teardown, reset paths, and invalid or missing shared-memory BAR mappings.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mana/shm_channel.h` completely for this pass (27 lines, 796 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mana/shm_channel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mctp.h -->
# sources/distributed-fs/ceph-client/include/net/mctp.h

## Purpose
`mctp.h` defines the kernel Management Component Transport Protocol core ABI: packet header helpers, socket state, tag/key lifetime rules, route and neighbour structures, and subsystem init/exit entry points.

## Important APIs, types, and functions
Important types are `struct mctp_hdr`, `struct mctp_sock`, `struct mctp_sk_key`, `struct mctp_skb_cb`, `struct mctp_flow`, `struct mctp_route`, `struct mctp_dst`, and `struct mctp_neigh`. Helpers classify EIDs, access skb headers/control blocks, allocate local tags, look up routes, send local output, add/remove local routes, manage default networks, and initialize route/neighbour/device subsystems.

## Control flow
Sockets bind local/peer EID and message type, allocate tags for request/response flows, and use `mctp_sk_key` lookup across per-socket and per-netns lists. Routing resolves destination network/EID to either direct device addressing or a gateway. Incoming packets set skb control metadata, match keys for sockets or reassembly, and may release device flow state through MCTP device operations.

## State and persistence
State is per-socket bind/tag lists and expiry timers, per-key reassembly skb chains and refcounts, per-netns route/key lists, per-device flow state, default network IDs, and RCU/refcounted routes/neighbours. Nothing is persisted outside runtime kernel objects.

## Dependencies and integration points
It depends on net namespaces, sockets, skb control blocks/extensions, netdevices, MCTP UAPI, timers, RCU, refcounts, and `mctpdevice.h`. It integrates sockets, routes, neighbours, and physical bindings.

## Risks and test signals
Risks include key lock ordering with netns `keys_lock`, tag expiry races, reassembly cleanup after socket unhash, skb control-block magic assumptions, route RCU lifetime, local/gateway route ownership, and MCTP flow extension leaks. Tests should cover tag allocation/drop, reply reassembly, socket close during reassembly, route add/remove on netdev unregister, extended address recvmsg, and broadcast/null/unicast EID checks.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mctp.h` completely for this pass (360 lines, 9743 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mctp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mctpdevice.h -->
# sources/distributed-fs/ceph-client/include/net/mctpdevice.h

## Purpose
`mctpdevice.h` defines the MCTP per-netdevice wrapper and the binding operations used by physical MCTP transports.

## Important APIs, types, and functions
It defines `struct mctp_dev`, `struct mctp_netdev_ops`, `MCTP_INITIAL_DEFAULT_NET`, and functions for netdevice registration, lookup under RTNL or generic access, refcount hold/put, and device-flow key set/release.

## Control flow
A physical transport registers a netdevice as MCTP-capable with binding type and optional flow release callback. The MCTP core looks up the wrapper, manages local EID address arrays under RTNL plus `addrs_lock`, and associates `mctp_sk_key` flow state with the device.

## State and persistence
Runtime state includes the backing netdevice pointer, MCTP net ID, physical binding, local EID array, refcount, RCU teardown, and optional transport operations. No persistent state exists.

## Dependencies and integration points
It depends on list/types/refcount headers, netdevice state from `mctp.h`, and physical binding enums. It integrates transport drivers with the MCTP route/socket core.

## Risks and test signals
Risks include refcount/RCU lifetime errors, address-array mutation without RTNL or lock protection, flow release callback ordering, and unregister while keys still reference the device. Tests should cover register/unregister, local EID updates, key flow set/release, and netdev teardown.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mctpdevice.h` completely for this pass (58 lines, 1363 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mctpdevice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mip6.h -->
# sources/distributed-fs/ceph-client/include/net/mip6.h

## Purpose
`mip6.h` declares the IPv6 Mobility Header wire structure and message type constants for Mobile IPv6 support.

## Important APIs, types, and functions
The main type is packed `struct ip6_mh`, containing next-header protocol, header length, type, reserved byte, checksum, and variable message data. Constants enumerate Binding Refresh Request, HoTI/CoTI, HoT/CoT, Binding Update, Binding ACK, and Binding Error.

## Control flow
There are no functions. IPv6 mobility code can cast validated packet payload to `struct ip6_mh`, inspect `ip6mh_type`, and dispatch to type-specific handling.

## State and persistence
The header defines no state. Packet state is transient in skbs and type-specific payloads after the header.

## Dependencies and integration points
It depends on skb and socket headers for consumers. It integrates with IPv6 extension-header and mobility-message processing.

## Risks and test signals
Risks include packed unaligned access, insufficient length validation before reading `data[]`, checksum coverage mistakes, and unknown type handling above `IP6_MH_TYPE_MAX`. Tests should cover truncated headers, every declared type, checksum validation, and endian-safe field reads.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mip6.h` completely for this pass (41 lines, 1016 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mip6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mld.h -->
# sources/distributed-fs/ceph-client/include/net/mld.h

## Purpose
`mld.h` defines IPv6 Multicast Listener Discovery v1/v2 packet layouts, option macros, queue limits, and the MLDv2 maximum-response-code decoder.

## Important APIs, types, and functions
Types include `struct mld_msg`, `struct mld2_grec`, `struct mld2_report`, and `struct mld2_query`. Macros alias ICMPv6 header fields, decode MLDv2 floating-point MRC/QQIC fields, and define queue/SKB limits. `mldv2_mrc` converts the query response code to milliseconds/ticks-style units.

## Control flow
IPv6 multicast code parses ICMPv6 MLD messages using the structs and flexible arrays. `mldv2_mrc` handles linear values below 32768 and RFC3810 exponent/mantissa encoding above that threshold.

## State and persistence
The header defines no persistent state; runtime state is in multicast listener code queues and skbs using these layouts.

## Dependencies and integration points
It depends on IPv6 address and ICMPv6 headers and the architecture byteorder bitfield macros. It integrates with `igmp6`/MLD receive and report generation.

## Risks and test signals
Risks include bitfield endian mismatch, flexible-array bounds, MRC exponent overflow expectations, MLDv1 compatibility threshold errors, and queue-limit assumptions. Tests should parse v1 and v2 queries/reports, max/min MRC encodings, little/big-endian builds, and truncated source lists.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mld.h` completely for this pass (117 lines, 2918 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mld.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mpls.h -->
# sources/distributed-fs/ceph-client/include/net/mpls.h

## Purpose
`mpls.h` provides minimal MPLS shim-header helpers for Ethernet protocol classification, skb network-header access, and label-stack-entry construction.

## Important APIs, types, and functions
It defines `MPLS_HLEN`, `struct mpls_shim_hdr`, `eth_p_mpls`, `mpls_hdr`, and `mpls_entry_encode`.

## Control flow
Callers identify MPLS unicast/multicast ethertypes, cast skb network header to an MPLS shim header, and encode label/traffic-class/bottom-of-stack/TTL into a big-endian 32-bit label stack entry.

## State and persistence
No state is stored. The only state is packet header data in skbs.

## Dependencies and integration points
It depends on Ethernet protocol constants, netdevice/skb declarations, and UAPI MPLS bit shifts. It integrates MPLS forwarding, tunnels, and protocol parsing.

## Risks and test signals
Risks include caller failure to ensure the skb has at least four bytes, label/TTL/TC range overflow before shifting, and BOS mistakes for stacked labels. Tests should cover ethertype matching, encode/decode vectors, boundary labels, TTL zero, and skb length validation in callers.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mpls.h` completely for this pass (45 lines, 943 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mpls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mpls_iptunnel.h -->
# sources/distributed-fs/ceph-client/include/net/mpls_iptunnel.h

## Purpose
`mpls_iptunnel.h` defines the lightweight-tunnel encapsulation payload used for MPLS IP tunnels.

## Important APIs, types, and functions
It defines `struct mpls_iptunnel_encap` with label count, TTL propagation/default TTL, and a flexible label array, plus `mpls_lwtunnel_encap` to cast `lwtunnel_state->data`.

## Control flow
MPLS tunnel code stores labels and TTL policy in lwtunnel state. Callers retrieve the typed encap data and push labels during output.

## State and persistence
State is embedded in `struct lwtunnel_state` and persists as long as the route/lwtunnel object exists. The header itself stores no global data.

## Dependencies and integration points
It depends on Linux types and lwtunnel infrastructure. It integrates MPLS route encapsulation with generic lightweight tunnels.

## Risks and test signals
Risks include flexible-array sizing, label count mismatch with allocated lwtunnel state, TTL propagation semantics, and unchecked casts. Tests should cover route creation with multiple labels, default TTL, propagation on/off, and malformed netlink attributes.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mpls_iptunnel.h` completely for this pass (25 lines, 481 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mpls_iptunnel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mptcp.h -->
# sources/distributed-fs/ceph-client/include/net/mptcp.h

## Purpose
`mptcp.h` is the core MPTCP interface header for TCP option generation/parsing, skb extension ownership, scheduler and path-manager plugin hooks, IPv6 support, BPF exposure, and disabled-build stubs.

## Important APIs, types, and functions
Important types are `struct mptcp_ext`, `struct mptcp_rm_list`, `struct mptcp_addr_info`, `struct mptcp_out_options`, `struct mptcp_sched_ops`, and `struct mptcp_pm_ops`. Exported functions include MPTCP init, option builders/parsers, option writer, diagnostics, request-sock helpers, reset-option helpers, blackhole detection, MPTCPv6 init/mapped handling, and BPF subflow conversion.

## Control flow
TCP handshake and established paths ask MPTCP helpers to reserve and populate options, parse incoming options, and write encoded options into the TCP header. skb extensions carry data sequence mapping, ACKs, checksum, FIN, reset, and frozen/copy state. Collapse/copy/move helpers preserve or compare extension state so TCP skb coalescing does not merge incompatible mappings.

## State and persistence
State is in MPTCP sockets/subflows, skb extensions, scheduler/path-manager registered lists, request-sock flags, and optional IPv6/BPF integration. The disabled configuration collapses calls into TCP fallback stubs.

## Dependencies and integration points
It depends on TCP, skb extensions, module/list infrastructure, IPv4/IPv6 address types, seq_file, and BPF when enabled. It integrates tightly with TCP transmit, receive, request-sock, diagnostics, and pluggable MPTCP policy modules.

## Risks and test signals
Risks include skb extension ownership transfer leaks, frozen extension copy semantics, collapse of incompatible data mappings, option-size accounting, 32/64-bit DSN/ACK mismatches, disabled-build fallback behavior, and scheduler/path-manager module lifetime. Tests should cover SYN/SYNACK/established options, skb clone/collapse/move, reset options, IPv6 mapped subflows, BPF lookup, and CONFIG_MPTCP off builds.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mptcp.h` completely for this pass (340 lines, 8052 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mptcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mrp.h -->
# sources/distributed-fs/ceph-client/include/net/mrp.h

## Purpose
`mrp.h` defines the Multiple Registration Protocol core data structures for applicants, applications, attributes, vector attribute parsing, and join/leave API used by MRP applications such as MVRP.

## Important APIs, types, and functions
Key types are PDU/message/vector headers, `struct mrp_skb_cb`, applicant/event/action enums, `struct mrp_attr`, `struct mrp_application`, `struct mrp_applicant`, and `struct mrp_port`. Functions register/unregister applications, init/uninit applicants, and request join/leave for attributes.

## Control flow
Applications register a packet type, multicast group address, version, and max attribute count. Per-device applicants keep timers, queues, current PDU, and an RB tree of MAD attributes. Join/leave requests update applicant state and enqueue PDUs; received vector events are decoded through skb control-block metadata.

## State and persistence
Runtime state includes per-port RCU applicant pointers, applicant timers, spinlock-protected queues and RB tree, active flag, current PDU, and per-attribute applicant state. No disk persistence exists.

## Dependencies and integration points
It depends on netdevice, skb, packet_type, timers, RB trees, spinlocks, and RCU. It integrates MRP applications with Ethernet multicast registration.

## Risks and test signals
Risks include skb control-block size assumptions, timer teardown races, RB tree duplicate handling, vector length/flag decoding, application unregister while applicants are active, and max attribute enforcement. Tests should cover register/unregister, per-device init/uninit, join/leave transitions, vector event decoding, timer-driven TX, and RCU teardown.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mrp.h` completely for this pass (148 lines, 3200 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mrp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ncsi.h -->
# sources/distributed-fs/ceph-client/include/net/ncsi.h

## Purpose
`ncsi.h` exposes the public Network Controller Sideband Interface state and functions used by NIC drivers that delegate management traffic/control to NCSI.

## Important APIs, types, and functions
It defines external device states, `struct ncsi_dev`, and enabled or stubbed functions for VLAN VID add/kill, device registration, start, stop, and unregister.

## Control flow
A netdevice driver registers an NCSI device with a notifier, starts it to select/configure an active package/channel, reacts to state/link callbacks, and stops/unregisters on teardown. Without `CONFIG_NET_NCSI`, calls return errors or no-ops.

## State and persistence
Runtime state is the NCSI state integer, link-up flag, back pointer to netdevice, and notifier handler. More detailed package/channel state lives in internal NCSI headers and implementation.

## Dependencies and integration points
It depends on netdevice and CONFIG_NET_NCSI. It integrates BMC/NCSI management channels with Ethernet drivers.

## Risks and test signals
Risks include callers not handling disabled stubs, state-machine transitions during suspend/config/probe, VLAN synchronization failures, and callback lifetime. Tests should cover enabled and disabled builds, register/start/stop/unregister order, link-up notifications, VLAN events, and suspend/config state transitions.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/ncsi.h` completely for this pass (72 lines, 1990 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ncsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ndisc.h -->
# sources/distributed-fs/ceph-client/include/net/ndisc.h

## Purpose
`ndisc.h` defines IPv6 Neighbor Discovery message layouts, option parsing hooks, link-layer address option helpers, neighbour lookup helpers, multicast mapping, send/update entry points, and MLD/IGMP6 lifecycle declarations.

## Important APIs, types, and functions
Important types are ND/RS/RA/RD message structs, `struct nd_opt_hdr`, `struct ndisc_options`, and `struct ndisc_ops`. Inline helpers dispatch device-specific `ndisc_ops`, compute option padding/space, extract LL address data, hash IPv6 neighbour keys, look up/confirm/create neighbours, and compute gateway neighbours. Declarations cover NDISC init/cleanup, receive, NS/NA/RS/redirect send, multicast mapping, and update paths.

## Control flow
Receive code parses options into `ndisc_options`, allows device-specific option parsers such as 6LoWPAN, updates neighbour cache entries, and handles router/prefix information. Send paths calculate link-layer option space, fill optional device data, and emit ICMPv6 NDISC packets. Lookup helpers use the global IPv6 neighbour table under RCU and refcount neighbours only when requested.

## State and persistence
State lives in the global `nd_tbl`, per-device `ndisc_ops`, neighbour entries, IPv6 device config, and parsed skb option structures. The header defines no persistent state of its own.

## Dependencies and integration points
It depends on IPv6, ICMPv6, netdevice, neighbour core, hashing, sysctl, and optional 802.15.4 6LoWPAN support. It integrates IPv6 neighbour discovery, SLAAC prefix processing, and link-layer-specific address option behavior.

## Risks and test signals
Risks include option length and padding bugs, device ops changing decisions between space calculation and fill, RCU/refcount misuse in no-ref lookup helpers, creating neighbours from fast paths, IPv6-disabled stub behavior, and hash collision assumptions. Tests should cover option parsing, InfiniBand padding, 6LoWPAN options, redirect option data, neighbour lookup/create/confirm, truncated packets, and sysctl change notifications.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/ndisc.h` completely for this pass (454 lines, 13796 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ndisc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/neighbour.h -->
# sources/distributed-fs/ceph-client/include/net/neighbour.h

## Purpose
`neighbour.h` is the generic neighbour-cache core interface shared by ARP, IPv6 NDISC, and other link-layer resolution users. It defines table, parameter, entry, proxy-entry, stats, lookup, update, output, sysctl, and sequencing contracts.

## Important APIs, types, and functions
Core types are `struct neigh_parms`, `struct neigh_statistics`, `struct neighbour`, `struct neigh_ops`, `struct pneigh_entry`, `struct neigh_hash_table`, `struct neigh_table`, and `struct neigh_seq_state`. APIs cover table init/clear, lookup/create/destroy, event sending, update, probe, address changes, interface teardown, output functions, parameter allocation/release, proxy neighbour operations, iteration, sysctl registration, reference helpers, and header-cache output helpers.

## Control flow
Protocol tables provide hash/equality/constructor/solicit/output callbacks. Lookups use RCU hash tables; creation initializes entries and queues unresolved packets. `neigh_event_send` updates usage and starts resolution when NUD state is not connected/delay/probe. Output chooses cached hardware header fast path when connected and available, otherwise calls the entry output op. GC, timers, managed lists, proxy queues, and sysctls are driven by the implementation.

## State and persistence
State is substantial and runtime-only: per-table hash/proxy tables, gc lists/work/timers, per-CPU stats, parameter lists and sysctls, per-neighbour NUD state, timers, skb queues, hardware address seqlock, refcounts, device trackers, and header cache. No persistent storage exists.

## Dependencies and integration points
It depends on netdevice, skb queues, timers, delayed work, RCU, refcount, seqlocks, rtnetlink, sysctl, seq_file, and `neighbour_tables.h`. It integrates with ARP, NDISC, bridge netfilter header-cache paths, and route output.

## Risks and test signals
Risks include RCU hash resize races, refcount underflow, NUD timer transitions, unresolved queue byte limits, header-cache headroom checks, sysctl parameter aliasing, device teardown with live entries, proxy queue handling, and lock ordering between table, neighbour, and device locks. Tests should cover lookup/create/update, GC thresholds, unresolved queue drops, output fast/slow paths, device down/carrier down, sysctl changes, proxy neighbours, and concurrent hash resize.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/neighbour.h` completely for this pass (617 lines, 17619 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/neighbour.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/neighbour_tables.h -->
# sources/distributed-fs/ceph-client/include/net/neighbour_tables.h

## Purpose
`neighbour_tables.h` centralizes numeric neighbour table identifiers.

## Important APIs, types, and functions
It defines `NEIGH_ARP_TABLE`, `NEIGH_ND_TABLE`, `NEIGH_NR_TABLES`, and `NEIGH_LINK_TABLE` as a pseudo table used by `neigh_xmit`.

## Control flow
There are no functions. Neighbour table registration and xmit users share the same enum values for indexing.

## State and persistence
No state is stored.

## Dependencies and integration points
It is included by `neighbour.h` and consumers that need stable table IDs.

## Risks and test signals
Risks are accidental renumbering or adding real tables after the pseudo table without updating array sizing. Tests are compile/build coverage and targeted users of ARP, ND, and link pseudo-table xmit paths.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/neighbour_tables.h` completely for this pass (12 lines, 253 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/neighbour_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_debug.h -->
# sources/distributed-fs/ceph-client/include/net/net_debug.h

## Purpose
`net_debug.h` provides netdevice-aware logging helpers, `netif_msg_*` gated driver logging macros, dynamic-debug integration, verbose-debug stubs, and optional debug-network warning macros.

## Important APIs, types, and functions
It declares `netdev_printk` and severity wrappers, defines `netdev_*_once`, `netdev_dbg`, `netdev_vdbg`, `netif_printk`, `netif_*`, `netif_dbg`, `netif_cond_dbg`, `netif_vdbg`, and `DEBUG_NET_WARN_ON*`.

## Control flow
Callers log with a netdevice context and severity. Dynamic debug builds route debug output through `dynamic_netdev_dbg`; DEBUG builds emit directly; normal builds type-check arguments through dead code. `netif_*` macros first check the driver's message bitmap via `netif_msg_type` helpers.

## State and persistence
Only `*_once` macros create static per-callsite booleans in `.data..once`. Otherwise the header has no runtime state.

## Dependencies and integration points
It depends on bug/warn infrastructure, kernel log levels, dynamic debug, and netdevice message-level helpers. It integrates all network drivers with consistent device-prefixed logging.

## Risks and test signals
Risks include side effects in arguments compiled out, incorrect message-type names, once-state not reset across module lifetime expectations, and debug warnings disappearing without CONFIG_DEBUG_NET. Tests should build with dynamic debug, DEBUG, VERBOSE_DEBUG, CONFIG_DEBUG_NET on/off, and verify message gating.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/net_debug.h` completely for this pass (159 lines, 5352 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_failover.h -->
# sources/distributed-fs/ceph-client/include/net/net_failover.h

## Purpose
`net_failover.h` defines the generic net failover private state and feature masks used to pair a standby virtual netdevice with a primary device of the same MAC.

## Important APIs, types, and functions
It defines `struct net_failover_info`, `net_failover_create`, `net_failover_destroy`, `FAILOVER_VLAN_FEATURES`, and `FAILOVER_ENC_FEATURES`.

## Control flow
A standby device creates a failover instance; the failover core tracks RCU primary and standby devices, aggregates stats, and migrates traffic/features as devices appear or disappear.

## State and persistence
Runtime state includes RCU primary/standby netdevice pointers, separate and aggregated rtnl stats, and a spinlock protecting stats updates.

## Dependencies and integration points
It depends on the generic failover framework and netdevice feature flags. It integrates virtio/netvsc-style failover devices with the network stack.

## Risks and test signals
Risks include RCU device lifetime, stats aggregation races, inconsistent feature masks, and MAC matching assumptions. Tests should cover primary add/remove, standby teardown, stats reads under traffic, VLAN/encap feature propagation, and failover during carrier changes.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/net_failover.h` completely for this pass (40 lines, 1023 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_failover.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_namespace.h -->
# sources/distributed-fs/ceph-client/include/net/net_namespace.h

## Purpose
`net_namespace.h` defines `struct net`, network namespace reference helpers, pernet operation registration, namespace ID helpers, sysctl registration, route generation counters, and `possible_net_t` abstraction.

## Important APIs, types, and functions
Important types are `struct net`, `possible_net_t`, and `struct pernet_operations`. APIs include netns copy/get/put variants, ownership lookup, barriers, namespace lookup by fd/pid/id, pernet subsystem/device registration, net sysctl registration, route/fnhe genid helpers, ref tracker helpers, and namespace iteration macros.

## Control flow
Namespace creation clones or reuses `init_net` depending on CONFIG_NET_NS. Subsystems register pernet init/exit callbacks; cleanup runs device exits before subsystem exits, with batch exit for RCU-heavy teardown. References use `ns_ref_*` plus optional trackers. `possible_net_t` stores per-object net pointers only when namespaces are enabled.

## State and persistence
`struct net` is the central persistent runtime container for per-netns lists, devices, sockets, protocol namespaces, netfilter/conntrack/nftables state, BPF, XFRM, MPLS, MCTP, vsock, sysctls, IDR namespace IDs, ref trackers, and route generation counters. State persists for the lifetime of the network namespace and is freed after passive references drain.

## Dependencies and integration points
It depends on many per-protocol netns headers, ns_common, idr/xarray, notifier, skbuff, sysctl, user namespaces, ref trackers, and optional CONFIG blocks. It integrates every network subsystem into namespace lifecycle management.

## Risks and test signals
Risks include wrong pernet registration class, cleanup ordering with devices/sockets still present, netns ref leaks, missing `maybe_get_net` checks on dying namespaces, route-genid invalidation gaps, CONFIG_NET_NS stubs masking bugs, and tracker misuse. Tests should cover namespace create/destroy under traffic, pernet init failure unwinds, device cleanup ordering, sysctl registration, ID allocation, and refcount-tracker diagnostics.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/net_namespace.h` completely for this pass (594 lines, 15046 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_namespace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_ratelimit.h -->
# sources/distributed-fs/ceph-client/include/net/net_ratelimit.h

## Purpose
`net_ratelimit.h` declares the global network ratelimit state shared by networking log sites.

## Important APIs, types, and functions
It exposes `extern struct ratelimit_state net_ratelimit_state` after including `<linux/ratelimit.h>`.

## Control flow
Callers pass the global state to ratelimit helpers when logging repeated network events.

## State and persistence
The state object is defined elsewhere and tracks ratelimit counters/timing globally for networking.

## Dependencies and integration points
It depends on kernel ratelimit infrastructure and integrates with net logging call sites.

## Risks and test signals
Risks are global suppression hiding per-device bursts and callers forgetting ratelimit checks. Tests should exercise repeated warnings and ratelimit reset behavior.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/net_ratelimit.h` completely for this pass (9 lines, 220 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_ratelimit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_shaper.h -->
# sources/distributed-fs/ceph-client/include/net/net_shaper.h

## Purpose
`net_shaper.h` defines the kernel-facing representation and driver operations for hardware traffic shapers managed through the net shaper UAPI.

## Important APIs, types, and functions
It defines binding types, `struct net_shaper_binding`, `struct net_shaper_handle`, `struct net_shaper`, and `struct net_shaper_ops` with `group`, `set`, `delete`, and `capabilities` callbacks.

## Control flow
The networking core serializes operations per device, tracks user-applied shaper configuration, calls driver `set` or `delete` for individual nodes, `group` to nest queue leaves under a scheduling node, and `capabilities` to report supported scopes/features.

## State and persistence
Runtime state is shaper handle/scope/id, parent linkage, rate/burst/priority/weight parameters, leaf counts for node scopes, and RCU lifetime. Device implementations mirror that state in NIC hardware.

## Dependencies and integration points
It depends on UAPI `net_shaper.h`, netdevice/devlink forward declarations, netlink extack, and optional device locking in `netdev_lock.h`. It integrates traffic shaping with netdevices and future devlink ports.

## Risks and test signals
Risks include unsupported nesting, handle uniqueness bugs, stale RCU shaper nodes, ambiguity between zero and unset values, and driver/core state divergence after partial failures. Tests should cover capabilities, set/delete, group creation, extack errors, queue-scope limits, and concurrent queue reconfiguration.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/net_shaper.h` completely for this pass (120 lines, 3571 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_shaper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_trackers.h -->
# sources/distributed-fs/ceph-client/include/net/net_trackers.h

## Purpose
`net_trackers.h` aliases optional network object reference trackers for netdevices and network namespaces.

## Important APIs, types, and functions
It typedefs `netdevice_tracker` and `netns_tracker` to `struct ref_tracker *` when the matching CONFIG tracker is enabled, otherwise to empty structs.

## Control flow
Code can declare tracker variables unconditionally and pass them to helpers; enabled builds allocate/free tracker records, disabled builds compile away storage.

## State and persistence
The header stores no state. Runtime tracker state lives in ref_tracker directories on netdevices/net namespaces when enabled.

## Dependencies and integration points
It depends on `<linux/ref_tracker.h>` and CONFIG_NET_DEV_REFCNT_TRACKER / CONFIG_NET_NS_REFCNT_TRACKER. It integrates leak diagnostics with network object lifetimes.

## Risks and test signals
Risks include helpers that assume pointer semantics in disabled builds and mismatched alloc/free pairs in enabled builds. Tests should build with trackers on/off and run leak/refcount diagnostics.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/net_trackers.h` completely for this pass (18 lines, 424 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_trackers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netdev_lock.h -->
# sources/distributed-fs/ceph-client/include/net/netdev_lock.h

## Purpose
`netdev_lock.h` provides helper wrappers around the per-netdevice instance lock, compatibility with RTNL-serialized operations, lockdep class setup, and ops-lock assertions.

## Important APIs, types, and functions
It defines `netdev_trylock`, assertion helpers, `netdev_need_ops_lock`, lock/unlock wrappers for ops and compatibility modes, lock transition helpers, `netdev_lock_cmp_fn`, `netdev_lockdep_set_classes`, `netdev_lock_dereference`, and `netdev_debug_event`.

## Control flow
Callers use per-device locking when queue management or net shaper ops require it; otherwise compatibility helpers fall back to RTNL. Lockdep classes and compare functions permit multiple device locks under RTNL while detecting unordered nesting elsewhere.

## State and persistence
State is the `net_device::lock`, request flags, queue management/net shaper ops presence, and lockdep metadata. The header itself does not store persistent data.

## Dependencies and integration points
It depends on lockdep, netdevice, rtnetlink, and optional net shaper support. It integrates new per-netdev operation locking with legacy RTNL code.

## Risks and test signals
Risks include missing locks for ops that require serialization, deadlocks when taking multiple device locks outside RTNL, stale assumptions about invisible/unregistered devices, and lockdep class setup omissions. Tests should cover queue/shaper ops with and without request_ops_lock, nested device removal, RCU protected dereferences, and CONFIG_DEBUG_NET_SMALL_RTNL builds.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netdev_lock.h` completely for this pass (138 lines, 3370 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netdev_lock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netdev_netlink.h -->
# sources/distributed-fs/ceph-client/include/net/netdev_netlink.h

## Purpose
`netdev_netlink.h` defines the small per-netdev netlink socket binding container used by netdev netlink plumbing.

## Important APIs, types, and functions
It defines `struct netdev_nl_sock` with a mutex and list of bindings.

## Control flow
Netlink code serializes binding changes under `lock` and stores subscribed/bound objects in `bindings`.

## State and persistence
Runtime state is the binding list and its mutex. No persistent or global state is declared here.

## Dependencies and integration points
It depends on Linux list and mutex definitions through included headers. It integrates netdev-specific netlink binding state with the core netlink implementation.

## Risks and test signals
Risks include lock ordering with rtnl/netdev locks and list lifetime during socket teardown. Tests should cover bind/unbind, socket close, and concurrent notifications.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netdev_netlink.h` completely for this pass (12 lines, 239 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netdev_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netdev_queues.h -->
# sources/distributed-fs/ceph-client/include/net/netdev_queues.h

## Purpose
`netdev_queues.h` defines queue configuration/statistics APIs, RX queue management operation contracts, and lockless TX queue stop/wake helper macros for drivers.

## Important APIs, types, and functions
Key types are `struct netdev_config`, `struct netdev_queue_config`, RX/TX queue stats structs, `struct netdev_stat_ops`, and `struct netdev_queue_mgmt_ops`. Functions and macros include `netdev_stat_queue_sum`, `netdev_queue_config`, `netif_rxq_has_unreadable_mp`, `netif_txq_try_stop`, `netif_txq_maybe_stop`, `__netif_txq_completed_wake`, subqueue wrappers, `netif_xmit_timeout_ms`, queue DMA-device lookup, create/lease/busy checks.

## Control flow
Stats callbacks gather base and active queue counters under the appropriate device/RTNL lock. Queue management allocates memory while closed, starts/stops queues while open, validates queue configs, and may create virtual queues. TX macros implement a single-producer/single-consumer stop/wake protocol with barriers paired through BQL or explicit memory barriers.

## State and persistence
State includes queue configs, driver per-queue memory, active RX/TX queue stats, BQL accounting, TX queue stopped state, descriptor indexes supplied by drivers, and optional queue leases. The header itself stores no globals.

## Dependencies and integration points
It depends on netdevice, netlink extack through declarations, BQL, jiffies, and netdev ops locking. It integrates modern queue control, stats, and zero-copy queue leasing.

## Risks and test signals
Risks include side effects in macro arguments due to multiple evaluation, wrong descriptor threshold selection, missing producer/consumer barriers, stats fields left undefined in base callbacks, queue config validation drift, and queue leasing lifetime. Tests should cover ring-full/ring-space races, BQL on/off, queue restart, per-queue stats totals, DMA device lookup, and virtual queue creation/lease.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netdev_queues.h` completely for this pass (393 lines, 13526 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netdev_queues.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netdev_rx_queue.h -->
# sources/distributed-fs/ceph-client/include/net/netdev_rx_queue.h

## Purpose
`netdev_rx_queue.h` defines the per-RX-queue object, sysfs attribute wrapper, RX queue index helpers, lease lookup, and restart/lease management functions.

## Important APIs, types, and functions
It defines `struct netdev_rx_queue`, `struct rx_queue_attribute`, `__netif_get_rx_queue`, `get_netdev_rx_queue_index`, lease direction enum, `__netif_get_rx_queue_lease`, `netdev_rx_queue_restart`, `netdev_rx_queue_lease`, and `netdev_rx_queue_unlease`.

## Control flow
Network core stores one `netdev_rx_queue` per RX queue with XDP RXQ info, optional RPS/XSK state, sysfs kobject, NAPI pointer, queue config, page-pool memory-provider parameters, and optional bidirectional lease link. Restart and lease helpers coordinate physical and virtual queues.

## State and persistence
Runtime state is per queue and ops-protected below the kobject/device fields: XDP/RPS/XSK/page-pool settings, NAPI binding, queue config, memory-provider params, lease pointer, and netdevice trackers.

## Dependencies and integration points
It depends on kobject/sysfs, netdevice, XDP, page_pool, RPS, and queue config types. It integrates RX queue sysfs, XDP, AF_XDP, page pools, and queue leasing.

## Risks and test signals
Risks include queue index calculation after resize, lease pointer lifetime, tracker mismatches, restarting an active queue with unreadable memory provider, and sysfs access during teardown. Tests should cover queue resize, sysfs reads/writes, XDP/XSK attach, queue lease/unlease both directions, and restart error paths.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netdev_rx_queue.h` completely for this pass (84 lines, 2301 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netdev_rx_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netevent.h -->
# sources/distributed-fs/ceph-client/include/net/netevent.h

## Purpose
`netevent.h` declares the generic networking notifier chain for neighbour updates, redirects, probe-timer updates, and route hash/forward priority changes.

## Important APIs, types, and functions
It defines `struct netevent_redirect`, `enum netevent_notif_type`, and functions to register, unregister, and call netevent notifiers.

## Control flow
Subsystems register notifier blocks. Producers call `call_netevent_notifiers` with an event code and typed payload such as `struct neighbour`, `struct netevent_redirect`, `struct neigh_parms`, or `struct net`.

## State and persistence
Notifier-chain state lives in the implementation. Payload state remains owned by the caller and is transient for the callback duration.

## Dependencies and integration points
It depends on notifier blocks and forward declarations for dst, neighbour, and net. It integrates routing, neighbour, and upper-layer consumers that react to topology/cache changes.

## Risks and test signals
Risks include wrong payload type for event IDs, notifier lifetime during module unload, callbacks sleeping in unsuitable context, and ordering assumptions. Tests should cover notifier registration/unregistration, every event type, and module unload while events fire.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netevent.h` completely for this pass (39 lines, 1068 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netevent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/br_netfilter.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/br_netfilter.h

## Purpose
`br_netfilter.h` exposes bridge netfilter helpers for attaching bridge skb extension state, protocol/header adjustment, hook threshold continuation, fake routing table lookup, pre-routing setup, and optional IPv6 bridge validation.

## Important APIs, types, and functions
It defines `nf_bridge_alloc`, `nf_bridge_update_protocol`, `br_nf_hook_thresh`, `nf_bridge_encap_header_len`, `nf_bridge_push_encap_header`, `br_nf_pre_routing_finish_bridge`, `bridge_parent_rtable`, `setup_pre_routing`, and IPv6 enabled/stub helpers.

## Control flow
Bridge netfilter paths allocate skb extension metadata, adjust encapsulation headers before/after L3 netfilter processing, continue hooks at a threshold, and use the bridge fake rtable for routing interactions. IPv6 bridge pre-routing validation is conditional on CONFIG_IPV6.

## State and persistence
State is attached to skb extensions and bridge port/bridge structures; no persistent state is defined here.

## Dependencies and integration points
It depends on bridge private headers, netfilter hook state, skb extensions, IPv6 optional support, and route table types. It integrates bridge forwarding with L3 netfilter.

## Risks and test signals
Risks include skb extension allocation failure, incorrect encap header push/pull, direct inclusion of bridge private internals, IPv6-disabled behavior, and bridge port RCU lifetime. Tests should cover IPv4/IPv6 bridged netfilter, VLAN/PPPoE encapsulation lengths, pre-routing finish, and CONFIG_BRIDGE_NETFILTER off builds.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/br_netfilter.h` completely for this pass (77 lines, 1904 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/br_netfilter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_conntrack_ipv4.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_conntrack_ipv4.h

## Purpose
`ipv4/nf_conntrack_ipv4.h` declares IPv4 L4 protocol trackers used by nf_conntrack.

## Important APIs, types, and functions
It exposes extern `nf_conntrack_l4proto` instances for TCP, UDP, ICMP, and optional SCTP/GRE.

## Control flow
The conntrack core and protocol initialization tables reference these declarations to parse IPv4 packets by L4 protocol.

## State and persistence
No state is stored here; protocol tracker objects are defined in implementation files.

## Dependencies and integration points
It depends on nf_conntrack L4 protocol definitions and CONFIG_NF_CT_PROTO_SCTP/GRE. It integrates IPv4 packet tracking with generic conntrack.

## Risks and test signals
Risks include missing optional protocol declarations in builds and mismatched protocol object initialization. Tests should build IPv4 conntrack with TCP/UDP/ICMP and optional SCTP/GRE modules.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_conntrack_ipv4.h` completely for this pass (23 lines, 754 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_conntrack_ipv4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_defrag_ipv4.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_defrag_ipv4.h

## Purpose
`ipv4/nf_defrag_ipv4.h` declares per-netns enable/disable hooks for IPv4 fragment reassembly needed by conntrack and netfilter users.

## Important APIs, types, and functions
It declares `nf_defrag_ipv4_enable` and `nf_defrag_ipv4_disable`.

## Control flow
Netfilter modules call enable when they need IPv4 defragmentation in a namespace and disable when releasing their reference.

## State and persistence
Reference/state tracking is in the implementation and per network namespace.

## Dependencies and integration points
It depends on `struct net` and integrates IPv4 fragment handling with netfilter/conntrack.

## Risks and test signals
Risks include unbalanced enable/disable, namespace teardown with active users, and fragment memory pressure. Tests should cover module load/unload, namespace lifecycle, fragmented IPv4 conntrack, and repeated enable calls.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_defrag_ipv4.h` completely for this pass (9 lines, 226 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_defrag_ipv4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_dup_ipv4.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_dup_ipv4.h

## Purpose
`ipv4/nf_dup_ipv4.h` declares the IPv4 packet duplication helper used by nftables/iptables dup actions.

## Important APIs, types, and functions
It declares `nf_dup_ipv4(struct net *, struct sk_buff *, unsigned int hooknum, const struct in_addr *gw, int oif)`.

## Control flow
Rules call the helper with a cloned or owned skb, hook number, optional gateway, and output interface; the implementation routes and emits the duplicate.

## State and persistence
The header has no state. Packet clone/routing state is transient in skb and route lookup.

## Dependencies and integration points
It depends on skb and IPv4 address UAPI. It integrates netfilter rule actions with IPv4 output.

## Risks and test signals
Risks include recursion, wrong hook context, route/oif lookup failures, and skb ownership confusion. Tests should duplicate packets from each relevant hook, with and without gateway/oif.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_dup_ipv4.h` completely for this pass (11 lines, 288 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_dup_ipv4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_reject.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_reject.h

## Purpose
`ipv4/nf_reject.h` declares IPv4 reject helpers for ICMP unreachable and TCP reset responses.

## Important APIs, types, and functions
It declares `nf_send_unreach`, `nf_send_reset`, `nf_reject_skb_v4_unreach`, and `nf_reject_skb_v4_tcp_reset`.

## Control flow
Netfilter reject expressions either send responses directly or build reject skbs for later emission based on hook, device, code, and original skb.

## State and persistence
No persistent state is defined; generated response skb state is transient.

## Dependencies and integration points
It depends on skb, IPv4, ICMP, and common nf_reject helpers. It integrates netfilter reject rules with IPv4 protocol response generation.

## Risks and test signals
Risks include malformed reset sequence/ack numbers, ICMP code selection, hook/device route context, fragmentation/DF handling, and responding to invalid packets. Tests should cover TCP reset, ICMP unreachable codes, local/forward hooks, invalid input packets, and namespace routing.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_reject.h` completely for this pass (23 lines, 792 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_reject.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_conntrack_ipv6.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_conntrack_ipv6.h

## Purpose
`ipv6/nf_conntrack_ipv6.h` declares the IPv6 ICMPv6 conntrack L4 protocol tracker.

## Important APIs, types, and functions
It exposes `nf_conntrack_l4proto_icmpv6`.

## Control flow
Conntrack protocol registration uses this object to track ICMPv6 packets and embedded errors.

## State and persistence
No state is stored in the header.

## Dependencies and integration points
It depends on conntrack L4 protocol definitions through consumers. It integrates IPv6 ICMP tracking with conntrack.

## Risks and test signals
Risks are build/link mismatches and ICMPv6 error tuple handling in implementation. Tests should include IPv6 conntrack with echo and error packets.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_conntrack_ipv6.h` completely for this pass (7 lines, 202 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_conntrack_ipv6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_defrag_ipv6.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_defrag_ipv6.h

## Purpose
`ipv6/nf_defrag_ipv6.h` declares IPv6 fragment reassembly hooks and per-netns fragment state used by conntrack/netfilter.

## Important APIs, types, and functions
It declares enable/disable, global init/cleanup, `nf_ct_frag6_gather`, and `struct nft_ct_frag6_pernet` containing sysctl header and fragment queue directory.

## Control flow
Users enable IPv6 defrag for a namespace. Packet paths call gather to reassemble or queue fragments before conntrack processing. Init/cleanup manage global IPv6 fragment infrastructure.

## State and persistence
Per-netns state includes fragment sysctl registration and fqdir. Runtime fragment queues live in the implementation.

## Dependencies and integration points
It depends on skb, types, `struct net`, fragment control types, and netfilter. It integrates IPv6 fragmentation with conntrack and nftables.

## Risks and test signals
Risks include fragment queue memory limits, namespace cleanup ordering, unbalanced enable/disable, overlapping fragment handling, and user identifier mismatches. Tests should cover fragmented IPv6 flows, namespace teardown, sysctl registration, and memory pressure.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_defrag_ipv6.h` completely for this pass (22 lines, 523 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_defrag_ipv6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_dup_ipv6.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_dup_ipv6.h

## Purpose
`ipv6/nf_dup_ipv6.h` declares the IPv6 packet duplication helper used by netfilter dup actions.

## Important APIs, types, and functions
It declares `nf_dup_ipv6(struct net *, struct sk_buff *, unsigned int hooknum, const struct in6_addr *gw, int oif)`.

## Control flow
Netfilter rules call the helper to route and transmit a duplicate IPv6 skb toward an optional gateway/output interface.

## State and persistence
No persistent state is defined.

## Dependencies and integration points
It depends on skb and IPv6 address declarations. It integrates nftables/iptables dup semantics with IPv6 routing.

## Risks and test signals
Risks include recursion, scope/oif selection, route failures, and skb ownership. Tests should cover link-local/global gateways, hook contexts, and oif-only duplication.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_dup_ipv6.h` completely for this pass (10 lines, 262 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_dup_ipv6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_reject.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_reject.h

## Purpose
`ipv6/nf_reject.h` declares IPv6 reject helpers for ICMPv6 unreachable and TCP reset responses.

## Important APIs, types, and functions
It declares `nf_send_unreach6`, `nf_send_reset6`, `nf_reject_skb_v6_tcp_reset`, and `nf_reject_skb_v6_unreach`.

## Control flow
Reject rules call these helpers to generate immediate responses or response skbs based on original packet, device, hook, and ICMPv6 code.

## State and persistence
No persistent state is stored.

## Dependencies and integration points
It depends on ICMPv6 and common nf_reject logic. It integrates IPv6 netfilter reject expressions with protocol-compliant error generation.

## Risks and test signals
Risks include extension-header parsing, reset sequence correctness, ICMPv6 rate/eligibility rules, hook routing context, and namespace handling. Tests should cover TCP reset, unreachable codes, extension headers, multicast/non-unicast suppression, and local/forward paths.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_reject.h` completely for this pass (21 lines, 696 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_reject.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_bpf_link.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_bpf_link.h

## Purpose
`nf_bpf_link.h` defines the BPF netfilter link attach context and conditional attach helper for BPF programs bound to netfilter hooks.

## Important APIs, types, and functions
It defines `struct bpf_nf_ctx` with hook state and skb pointers, and `bpf_nf_link_attach` or an `-EOPNOTSUPP` stub depending on CONFIG_NETFILTER_BPF_LINK.

## Control flow
BPF syscall attach code passes attributes and a program to `bpf_nf_link_attach`, producing a persistent link to a netfilter hook. BPF program context exposes the current skb and hook state.

## State and persistence
Link lifetime and hook registration state live in the implementation. The context is transient per invocation.

## Dependencies and integration points
It depends on BPF attr/prog forward declarations, nf_hook_state, skb, and CONFIG_NETFILTER_BPF_LINK. It integrates BPF link infrastructure with netfilter.

## Risks and test signals
Risks include disabled-build fallback handling, hook state lifetime, skb mutation safety, and link detach ordering. Tests should cover attach/detach, program execution, namespace hooks, and CONFIG off builds.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_bpf_link.h` completely for this pass (15 lines, 365 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_bpf_link.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack.h

## Purpose
`nf_conntrack.h` is the main netfilter connection tracking data model and public core API. It defines `struct nf_conn`, per-netns conntrack state, protocol-private storage, tuple access helpers, timeout/reference helpers, allocation/hash APIs, accounting refresh/kill APIs, and statistics macros.

## Important APIs, types, and functions
Important types include `union nf_conntrack_proto`, `struct nf_conntrack_net_ecache`, `struct nf_conntrack_net`, and `struct nf_conn`. Key helpers/functions include `nf_ct_get`, `nf_ct_put`, `nf_ct_netns_get/put`, hash allocation/resize, tuple parsing, refresh/acct/kill, iteration cleanup/destroy, allocation/free, template allocation, status tests, expiry helpers, `nf_conntrack_get_ht`, `nf_ct_set`, `nf_ct_pernet`, fragment helpers, and stats macros.

## Control flow
Packet paths attach conntrack pointers and info bits into skb nfct storage, create unconfirmed conntracks from tuples, optionally alter reply tuples before confirmation, insert into hash tables, refresh timeouts on traffic, deliver accounting/events, and destroy when refcount reaches zero or GC marks expired confirmed entries. Namespace users enable/disable protocol families to load conntrack hooks.

## State and persistence
State is per-connection refcount, lock, timeout, zone, original/reply tuple hashes, status bits, netns pointer, optional NAT/source hash, master expectation link, mark/secmark, extension area, and protocol-private data. Global/pernet state includes conntrack hash, generation seqcount, max count, and per-net counters/users/sysctls/events.

## Dependencies and integration points
It depends on net namespaces, skb nfct storage, tuple definitions, L4 protocol headers, NAT optional support, conntrack extensions, refcounts, atomics, and netfilter common UAPI. It integrates conntrack, NAT, helpers, expectations, events, labels, timeouts, and flow actions.

## Risks and test signals
Risks include refcount vs raw `nf_ct_get` confusion, timeout wrap/ordering, confirmed/unconfirmed hash invariants, hash resize under RCU, template misuse, loopback packet classification, namespace user leaks, and extension lifetime. Tests should cover new flow creation/confirmation, hash resize, GC expiry, skb attach/detach refs, template flows, namespace enable/disable, fragment handling, and accounting refresh.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack.h` completely for this pass (384 lines, 10754 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_acct.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_acct.h

## Purpose
`nf_conntrack_acct.h` defines optional packet/byte accounting extensions for conntrack entries and per-netns accounting controls.

## Important APIs, types, and functions
It defines `struct nf_conn_counter`, `struct nf_conn_acct`, find/add helpers, enabled/set helpers, `nf_ct_acct_add`, `nf_ct_acct_update`, and pernet init.

## Control flow
When per-netns accounting is enabled, new conntracks can allocate the ACCT extension. Packet paths update per-direction atomic counters through `nf_ct_acct_update`.

## State and persistence
State is per-conntrack ACCT extension counters and `net->ct.sysctl_acct` per-net setting. No disk persistence exists.

## Dependencies and integration points
It depends on conntrack, tuple common constants, extensions, and net namespace state. It integrates with conntrack timeout/refresh paths and sysctl configuration.

## Risks and test signals
Risks include extension missing when sysctl toggles after connection creation, atomic counter overhead, disabled CONFIG stubs, and direction indexing. Tests should cover accounting on/off, existing flows after toggles, both directions, and namespace isolation.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_acct.h` completely for this pass (81 lines, 1819 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_acct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_act_ct.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_act_ct.h

## Purpose
`nf_conntrack_act_ct.h` defines the conntrack extension used by the traffic-control `act_ct` action to remember ingress/egress interface indexes.

## Important APIs, types, and functions
It defines `struct nf_conn_act_ct_ext` and helpers to find, fill, and add the extension.

## Control flow
When `CONFIG_NET_ACT_CT` is enabled, TC action paths allocate the ACT_CT extension and fill the direction-specific ifindex from the skb device for init_net traffic.

## State and persistence
State is a two-entry ifindex array stored as a conntrack extension. The helper stores nothing when NET_ACT_CT is disabled or when not in `init_net`.

## Dependencies and integration points
It depends on conntrack, conntrack extensions, skb device state, and TC act_ct configuration. It integrates TC connection tracking with later flow/offload consumers.

## Risks and test signals
Risks include `nf_conn_act_ct_ext_add` not checking allocation before fill, init_net-only behavior surprises, skb without dev, and stale ifindexes after device removal. Tests should cover extension allocation, both directions, non-init netns behavior, and disabled builds.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_act_ct.h` completely for this pass (54 lines, 1350 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_act_ct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_bpf.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_bpf.h

## Purpose
`nf_conntrack_bpf.h` declares BTF/BPF registration hooks that expose conntrack and NAT kernel functions/types to BPF when supported.

## Important APIs, types, and functions
It defines wrapper `struct nf_conn___init` and conditional `register_nf_conntrack_bpf`, `cleanup_nf_conntrack_bpf`, and `register_nf_nat_bpf` declarations or no-op stubs.

## Control flow
Conntrack/NAT module init paths register BPF kfunc/type metadata only when the module or built-in configuration also has the required BTF debug info.

## State and persistence
Registration state is in BPF/kfunc implementation; the header has no state.

## Dependencies and integration points
It depends on Kconfig predicates, conntrack, NAT, BTF debug info, and BPF syscall support. It integrates conntrack/NAT with BPF programs.

## Risks and test signals
Risks include configuration matrix mistakes, module-vs-built-in BTF differences, and callers assuming registration happened. Tests should build builtin/module/no-BTF combinations and load BPF programs using conntrack kfuncs.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_bpf.h` completely for this pass (46 lines, 899 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_bpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_bridge.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_bridge.h

## Purpose
`nf_conntrack_bridge.h` declares a small registration ABI for bridge conntrack hook providers.

## Important APIs, types, and functions
It defines `struct nf_ct_bridge_info` with hook ops pointer/count and owning module, plus `nf_ct_bridge_register` and `nf_ct_bridge_unregister`.

## Control flow
Bridge conntrack code registers its hook operations and module owner with conntrack; unregister removes them during teardown.

## State and persistence
Registered bridge hook info is held by implementation. The header stores no state.

## Dependencies and integration points
It depends on module, netfilter hook ops, and Ethernet UAPI. It integrates bridge traffic with conntrack hooks.

## Risks and test signals
Risks include ops array lifetime, module owner mismatches, and unregister while hooks are active. Tests should cover bridge conntrack module load/unload and bridged IPv4/IPv6 flows.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_bridge.h` completely for this pass (19 lines, 398 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_core.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_core.h

## Purpose
`nf_conntrack_core.h` exposes conntrack core functions shared by standalone conntrack and compatibility users: packet entry, init/cleanup, tuple inversion/find, confirmation, locks, timeout/status mutation, and tuple printing.

## Important APIs, types, and functions
Key APIs are `nf_conntrack_in`, net/proto init-cleanup functions, `nf_ct_invert_tuple`, `nf_conntrack_find_get`, `__nf_conntrack_confirm`, inline `nf_conntrack_confirm`, `nf_confirm`, `print_tuple`, global lock arrays, `nf_conntrack_expect_lock`, `__nf_ct_set_timeout`, `__nf_ct_change_timeout`, `__nf_ct_change_status`, and `nf_ct_change_status_common`.

## Control flow
Netfilter hooks call `nf_conntrack_in`; later confirm hooks call `nf_conntrack_confirm`, which inserts unconfirmed conntracks and then delivers cached events when present. Timeout mutation stores relative time while unconfirmed and absolute jiffies once confirmed.

## State and persistence
State is in conntrack entries, global lock arrays, expect lock, per-net/protocol initialization, and cached event extensions.

## Dependencies and integration points
It depends on netfilter hooks, conntrack, event cache, and L4 protocol APIs. It integrates packet hook processing, hash confirmation, and event delivery.

## Risks and test signals
Risks include double confirmation, cached events delivered after skb nfct changes, timeout unit confusion, lock contention across 1024 locks, expectation lock ordering, and cleanup ordering. Tests should cover unconfirmed-to-confirmed transitions, event delivery, timeout changes pre/post confirmation, tuple find, and namespace cleanup.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_core.h` completely for this pass (108 lines, 3241 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_count.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_count.h

## Purpose
`nf_conntrack_count.h` declares helpers for counting concurrent conntracks per arbitrary key, used by match modules such as connlimit.

## Important APIs, types, and functions
It defines `struct nf_conncount_list`, opaque `struct nf_conncount_data`, and APIs to init/destroy data, count/add skb-derived connections, initialize/gc/free lists.

## Control flow
Consumers hash policy keys to lists. Packet evaluation counts existing live conntracks matching a key, optionally adds the skb's conntrack, and periodically garbage-collects dead entries from the list.

## State and persistence
Runtime state includes per-key lists with spinlock, last GC jiffies, current count, and last GC count plus global data hidden in implementation.

## Dependencies and integration points
It depends on conntrack tuples, zones, net namespace, skb, list, and spinlocks. It integrates conntrack with rule-level connection count limits.

## Risks and test signals
Risks include stale entries if GC misses dying conntracks, list lock contention, zone mismatch, key length errors, and count/add races. Tests should cover concurrent new connections, GC, zones, IPv4/IPv6 tuples, and destroy under active lists.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_count.h` completely for this pass (38 lines, 1179 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_count.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_ecache.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_ecache.h

## Purpose
`nf_conntrack_ecache.h` defines conntrack and expectation event-cache extensions, notifier registration, event report helpers, and per-net delayed work controls.

## Important APIs, types, and functions
It defines `enum nf_ct_ecache_state`, `struct nf_conntrack_ecache`, `struct nf_ct_event`, `struct nf_exp_event`, and `struct nf_ct_event_notifier`. Helpers find/exist/add ecache extensions, cache events, report immediate events, deliver cached events, report expectation events, initialize/finalize pernet ecache, and query delayed-work pending state.

## Control flow
If event listeners exist and the conntrack has an ecache extension, packet/update paths set event bits in the cache and optionally timestamp the first cached event. Confirmation or explicit reporting delivers masks to the registered per-net notifier. Destroy-event failures can be retried by delayed work.

## State and persistence
State is per-conntrack cache bitmask, event masks, missed count, portid, optional timestamp, per-net notifier pointer and delayed dying-list work. Disabled CONFIG builds compile to no-ops.

## Dependencies and integration points
It depends on conntrack, expectations, extensions, net namespace, local64 timestamps, and netlink event consumers. It integrates ctnetlink events, expectation notifications, and conntrack lifecycle.

## Risks and test signals
Risks include missing ecache extension causing silent event loss, event callback RCU/lifetime, timestamp renewal semantics, missed event accounting, destroy retry ordering, and disabled-build behavior. Tests should cover listener registration, cached vs immediate events, expectation events, destroy failure retry, timestamps, and no-listener fast path.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_ecache.h` completely for this pass (187 lines, 4924 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_ecache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_expect.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_expect.h

## Purpose
`nf_conntrack_expect.h` defines conntrack expectations used by helpers/NAT to preauthorize related connections.

## Important APIs, types, and functions
It defines global expectation hash sizing symbols, `struct nf_conntrack_expect`, `struct nf_conntrack_expect_policy`, class/flag constants, pernet/global init/fini, find/get/unlink/remove/iterate functions, allocation/init/put, and related-registration APIs.

## Control flow
Helpers allocate expectations from a master conntrack, initialize tuple/mask/protocol/class/NAT data, insert with `nf_ct_expect_related`, and later incoming packets find and optionally unlink matching expectations to create related conntracks and call `expectfn`.

## State and persistence
State includes expectation hash/list nodes, netns pointer, tuple/mask, optional zone, refcount, flags/class, helper pointers, master conntrack, timeout timer, optional NAT saved address/proto/dir, and global hash table/max counts.

## Dependencies and integration points
It depends on conntrack, zones, timers, RCU, helpers, NAT optional support, and expectation locks from core. It integrates helpers such as FTP/SIP with related-flow tracking.

## Risks and test signals
Risks include timer vs unlink races, master/helper lifetime, expectation hash exhaustion, zone matching semantics, NAT saved tuple mistakes, `NF_CT_EXP_F_SKIP_MASTER` reuse surprises, and ref leaks. Tests should cover helper-created expectations, timeout expiry, related flow creation, NAT expectations, zones, class limits, and iterate-destroy.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_expect.h` completely for this pass (157 lines, 4528 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_expect.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_extend.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_extend.h

## Purpose
`nf_conntrack_extend.h` defines the optional extension area layout for conntrack entries and the extension IDs used by helpers, NAT, seqadj, acct, events, timestamps, timeouts, labels, synproxy, and TC act_ct.

## Important APIs, types, and functions
It defines `enum nf_ct_ext_id`, `struct nf_ct_ext`, existence/find helpers, `nf_ct_ext_add`, global `nf_conntrack_ext_genid`, and `nf_ct_ext_bump_genid`.

## Control flow
Code checks whether an extension offset is present, finds it directly when generation is current, or uses the slower finder if generation changed. New extensions are appended to the aligned data area; genid invalidation prevents unsafe use of stale unconfirmed extensions after extension layout changes.

## State and persistence
State is per-conntrack extension offsets/length/generation and global extension generation ID. Extension payloads persist for the conntrack lifetime.

## Dependencies and integration points
It depends on conntrack, slab allocation, and all CONFIG-dependent extension users. It integrates optional conntrack features without bloating base `struct nf_conn`.

## Risks and test signals
Risks include extension ID order/layout changes, alignment and length overflow, using extension pointers after reallocation/genid bump, and CONFIG matrix gaps. Tests should add multiple extensions, bump genid, use unconfirmed and confirmed entries, and build with feature combinations.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_extend.h` completely for this pass (79 lines, 1797 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_extend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_helper.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_helper.h

## Purpose
`nf_conntrack_helper.h` defines the conntrack helper registration ABI, helper extension storage, expectation-class accounting, NAT-helper module names, and helper assignment/callback APIs.

## Important APIs, types, and functions
Key types are `struct nf_conntrack_helper`, `struct nf_conn_help`, `struct nf_ct_helper_expectfn`, and `struct nf_conntrack_nat_helper`. APIs find/module-get/put helpers, initialize/register/unregister one or many helpers, add helper extension, assign helpers, run helper callbacks, add helpers by name, destroy helper state, register expectation functions, log helper messages, and register NAT helper modules.

## Control flow
Protocol helpers register tuple match criteria, policies, callbacks, private data needs, and optional userspace queue/NAT module names. Conntracks that need helpers allocate `NF_CT_EXT_HELPER`, store helper pointers and expectation lists, and call helper `help` on packet traversal to inspect payload and create expectations.

## State and persistence
Runtime state includes global helper hash, helper refcounts/module refs, helper extension pointers, per-connection expectation lists and counts, fixed private data buffer, userspace queue config, and NAT helper list.

## Dependencies and integration points
It depends on conntrack, extensions, expectations, modules, netlink attributes, and NAT optional helpers. It integrates application-layer helpers with conntrack/NAT.

## Risks and test signals
Risks include helper private data exceeding 32 bytes, module ref leaks, automatic helper assignment policy, expectation count class limits, NAT helper module name mismatch, userspace helper queue errors, and callback invalidation. Tests should cover helper register/unregister, assignment, private data build checks, expectation creation, NAT helper load, userspace helpers, and unload with active conntracks.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_helper.h` completely for this pass (183 lines, 5736 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_l4proto.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_l4proto.h

## Purpose
`nf_conntrack_l4proto.h` defines the L4 protocol plugin ABI for conntrack and declares built-in TCP/UDP/ICMP/SCTP/GRE packet handlers, tuple conversion helpers, timeout netlink conversion, and per-net protocol state accessors.

## Important APIs, types, and functions
It defines `struct nf_conntrack_l4proto` with packet/drop, netlink tuple/protoinfo, timeout object, and procfs callbacks. It declares tuple extraction/inversion for ICMP/ICMPv6, error handlers, per-protocol packet handlers, per-net init functions, generic protocol object, `nf_ct_l4proto_find`, port tuple netlink helpers, invalid logging helpers, pernet accessors, TCP liberal/established helpers, and optional SCTP/GRE accessors.

## Control flow
Conntrack core finds an L4 proto by IP protocol, parses tuples, handles protocol-specific packet state, serializes/deserializes netlink attributes, and uses timeout object callbacks. Error packets are matched to inner tuples. TCP helpers can set liberal mode or check established/assured state.

## State and persistence
State lives in per-net protocol structs under `net->ct.nf_ct_proto`, per-conntrack protocol-private union, and protocol object callback tables. The header stores no globals beyond extern declarations.

## Dependencies and integration points
It depends on netlink/nla policy, conntrack, netns generic state, sysctl optional invalid logging, and protocol-specific UAPI state. It integrates L4 protocols with conntrack core and ctnetlink.

## Risks and test signals
Risks include tuple parsing at wrong data offsets, ICMP error inversion, netlink policy/size mismatch, timeout object conversion bugs, optional protocol CONFIGs, and callers using TCP helpers on non-TCP conntracks. Tests should cover TCP/UDP/ICMP/ICMPv6/SCTP/GRE flows, error packets, ctnetlink dump/restore, invalid logging, and timeout policies.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_l4proto.h` completely for this pass (227 lines, 7071 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_l4proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_labels.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_labels.h

## Purpose
`nf_conntrack_labels.h` defines the conntrack labels extension used by xt_connlabel/nftables to attach bit labels to connections.

## Important APIs, types, and functions
It defines `NF_CT_LABELS_MAX_SIZE`, `struct nf_conn_labels`, `nf_ct_labels_find`, `nf_ct_labels_ext_add`, `nf_connlabels_replace`, and per-net label usage get/put helpers.

## Control flow
When labels are in use in a namespace, new conntracks may allocate the labels extension. Rules find the extension directly, replace bits according to data/mask, and manage `labels_used` through get/put.

## State and persistence
State is a bitmap stored per conntrack and a per-net labels-used counter. No disk persistence exists.

## Dependencies and integration points
It depends on conntrack, extension internals, net namespace, and xt_connlabel UAPI limits. It integrates rule matching/setting labels with conntrack entries.

## Risks and test signals
Risks include direct extension lookup bypassing exported symbols, labels not allocated when usage count is zero, word/mask length mismatch, disabled CONFIG stubs, and flow dissector constraints. Tests should cover label get/put, extension allocation, replace masks, max bit, disabled builds, and existing flows before label enable.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_labels.h` completely for this pass (62 lines, 1709 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_labels.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_seqadj.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_seqadj.h

## Purpose
`nf_conntrack_seqadj.h` defines TCP sequence-number adjustment state and APIs used by NAT/helpers that modify payload length.

## Important APIs, types, and functions
It defines `struct nf_ct_seqadj`, `struct nf_conn_seqadj`, find/add helpers, `nf_ct_seqadj_init`, `nf_ct_seqadj_set`, `nf_ct_tcp_seqadj_set`, `nf_ct_seq_adjust`, and `nf_ct_seq_offset`.

## Control flow
When payload changes alter TCP sequence space, helpers initialize or update per-direction correction positions and offsets. Later packet paths adjust TCP sequence/ack numbers and checksums according to direction and sequence position.

## State and persistence
State is per-conntrack SEQADJ extension with two direction entries storing last correction position and before/after offsets.

## Dependencies and integration points
It depends on conntrack extensions and TCP skb manipulation in implementation. It integrates NAT helpers and synproxy with TCP stream correctness.

## Risks and test signals
Risks include off-by-one sequence position handling, signed offset overflow, missing extension allocation, checksum update mistakes, and retransmission interactions. Tests should cover payload expand/shrink, both directions, retransmits around correction point, checksum validation, and NAT helper flows.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_seqadj.h` completely for this pass (45 lines, 1400 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_seqadj.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_synproxy.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_synproxy.h

## Purpose
`nf_conntrack_synproxy.h` defines the optional conntrack extension for SYNPROXY state and helper logic to copy synproxy/seqadj requirements from templates.

## Important APIs, types, and functions
It defines `struct nf_conn_synproxy`, find/add helpers, and `nf_ct_add_synproxy`.

## Control flow
When a template conntrack has SYNPROXY enabled, new conntracks allocate both SEQADJ and SYNPROXY extensions so SYN cookie sequence/timestamp offsets can be tracked.

## State and persistence
State is per-conntrack initial sequence number, initial timestamp, and timestamp offset. Disabled builds return NULL/true stubs.

## Dependencies and integration points
It depends on seqadj, conntrack extensions, netns generic, and CONFIG_NETFILTER_SYNPROXY. It integrates SYNPROXY rule handling with conntrack TCP adjustment.

## Risks and test signals
Risks include partial allocation where seqadj succeeds and synproxy fails, disabled-build assumptions, timestamp offset mistakes, and template detection. Tests should cover template-to-flow allocation, allocation failure, SYN/SYNACK/ACK proxy handshake, and CONFIG off builds.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_synproxy.h` completely for this pass (48 lines, 1005 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_synproxy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_timeout.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_timeout.h

## Purpose
`nf_conntrack_timeout.h` defines named/custom timeout objects and conntrack timeout extension APIs.

## Important APIs, types, and functions
It defines `CTNL_TIMEOUT_NAME_MAX`, `struct nf_ct_timeout`, `struct nf_conn_timeout`, data/find/add/lookup helpers, `nf_ct_untimeout`, `nf_ct_set_timeout`, `nf_ct_destroy_timeout`, and RCU timeout hook callbacks.

## Control flow
Userspace can define named timeout policies. Conntracks allocate a timeout extension pointing via RCU to a timeout object, and protocol code looks up the per-protocol timeout array through `nf_ct_timeout_lookup`. Destroy paths detach references.

## State and persistence
State is per-conntrack timeout extension pointer, named timeout objects with L3/protocol and variable data, and global RCU hook table. No on-disk persistence is defined here.

## Dependencies and integration points
It depends on conntrack, extensions, L4 protocol definitions, net namespace, refcounts, and CONFIG_NF_CONNTRACK_TIMEOUT. It integrates ctnetlink timeout policies with conntrack protocol state.

## Risks and test signals
Risks include RCU pointer lifetime, protocol/object size mismatch, timeout name lookup failure, disabled stub returning `-EOPNOTSUPP`, and stale timeouts during namespace teardown. Tests should cover set/destroy, policy delete while flows reference it, protocol-specific timeout data, disabled builds, and namespace cleanup.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_timeout.h` completely for this pass (112 lines, 2679 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_timeout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_timestamp.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_timestamp.h

## Purpose
`nf_conntrack_timestamp.h` defines optional start/stop timestamp extension support for conntrack entries.

## Important APIs, types, and functions
It defines `struct nf_conn_tstamp`, find/add helpers, and `nf_conntrack_tstamp_pernet_init` or a stub.

## Control flow
When per-net timestamping is enabled, conntracks allocate a timestamp extension and implementation records start/stop times for reporting.

## State and persistence
State is per-conntrack start/stop 64-bit timestamps plus `net->ct.sysctl_tstamp` per-net enable flag.

## Dependencies and integration points
It depends on conntrack, tuple constants, extensions, and CONFIG_NF_CONNTRACK_TIMESTAMP. It integrates with ctnetlink/proc reporting of flow lifetimes.

## Risks and test signals
Risks include missing extension after sysctl toggles, timestamp source consistency, zero stop time interpretation, and disabled-build stubs. Tests should cover timestamp enable/disable, flow creation/destruction, reporting, and namespace isolation.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_timestamp.h` completely for this pass (47 lines, 1124 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_timestamp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_tuple.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_tuple.h

## Purpose
`nf_conntrack_tuple.h` defines the canonical conntrack tuple and tuple hash structures used to identify flows and expectations.

## Important APIs, types, and functions
It defines `NF_CT_TUPLE_L3SIZE`, `struct nf_conntrack_man`, `struct nf_conntrack_tuple`, `struct nf_conntrack_tuple_mask`, `struct nf_conntrack_tuple_hash`, tuple debug dump helpers, `NF_CT_DIRECTION`, and tuple equality/mask comparison helpers.

## Control flow
Tuple extraction fills manipulable source fields and fixed destination/protocol/direction fields. Conntracks store original and reply tuple hashes. NAT can manipulate source-side fields while fixed destination fields identify the reverse mapping. Expectations use masks for wildcard matching.

## State and persistence
No independent state is stored; tuples are embedded in conntracks, expectations, hashes, and stack lookup keys.

## Dependencies and integration points
It depends on netfilter address/protocol tuple UAPI, list nulls hash nodes, and inet address comparison helpers. It integrates conntrack hash lookup, NAT, ctnetlink, and expectations.

## Risks and test signals
Risks include direction included/excluded incorrectly for hashing, mask comparison gaps, IPv4/IPv6 address array length assumptions, endian mistakes in ports/keys, and debug-only dumps hiding issues. Tests should cover tuple equality/mask matching for IPv4/IPv6/TCP/UDP/ICMP/GRE/SCTP and original/reply directions.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_tuple.h` completely for this pass (190 lines, 4705 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_tuple.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_zones.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_zones.h

## Purpose
`nf_conntrack_zones.h` defines inline helpers for conntrack zones, including default-zone fallback, template-derived zones, mark-derived zones, direction matching, and equality.

## Important APIs, types, and functions
It defines `nf_ct_zone`, `nf_ct_zone_init`, `nf_ct_zone_tmpl`, `nf_ct_zone_add`, `nf_ct_zone_matches_dir`, `nf_ct_zone_id`, `nf_ct_zone_equal`, and `nf_ct_zone_equal_any`.

## Control flow
Conntrack allocation copies a selected zone into the entry when zones are enabled. Templates can request dynamic zone IDs from `skb->mark`. Lookups compare zone IDs only for directions enabled by the zone's direction mask; otherwise they fall back to the default zone.

## State and persistence
State is the optional `ct->zone` field and temporary stack zone objects. Disabled builds use the global default zone and equality always succeeds.

## Dependencies and integration points
It depends on conntrack zones common UAPI and `struct nf_conn`. It integrates nft/iptables zone selection with conntrack lookup.

## Risks and test signals
Risks include mark-derived zone surprises, direction-mask mistakes, disabled-build behavior, and templates passed as NULL to `nf_ct_zone`. Tests should cover explicit zones, mark zones, original/reply direction masks, default fallback, and CONFIG_NF_CONNTRACK_ZONES off.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_zones.h` completely for this pass (89 lines, 2040 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_zones.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_dup_netdev.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_dup_netdev.h

## Purpose
`nf_dup_netdev.h` declares netdev-family packet duplicate/forward helpers, recursion tracking, and nftables flow offload support for dup/fwd actions.

## Important APIs, types, and functions
It declares `nf_dup_netdev_egress`, `nf_fwd_netdev_egress`, `NF_RECURSION_LIMIT`, `nf_get_nf_dup_skb_recursion`, and `nft_fwd_dup_netdev_offload`.

## Control flow
Netdev nftables actions duplicate or forward packets to an output ifindex while recursion tracking prevents repeated reinjection loops. Non-RT builds store recursion counters in per-CPU softnet data; PREEMPT_RT uses current task net-xmit state.

## State and persistence
State is the recursion counter in softnet or task net_xmit state. Flow offload state is built in nft flow rule structures.

## Dependencies and integration points
It depends on nftables packet info, netdevice, scheduler/current task state, PREEMPT_RT configuration, and flow offload types. It integrates netdev ingress/egress nftables actions with packet transmission and hardware offload.

## Risks and test signals
Risks include recursion-limit bypass, PREEMPT_RT storage differences, skb ownership after egress, offload action mismatch, and ifindex validation. Tests should cover nested dup/fwd rules, RT and non-RT builds, invalid oif, flow offload generation, and loop prevention.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_dup_netdev.h` completely for this pass (29 lines, 753 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_dup_netdev.h -->
