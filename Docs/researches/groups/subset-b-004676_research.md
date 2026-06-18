# subset-b-004676 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/geneve.c -->
## sources/distributed-fs/ceph-client/drivers/net/geneve.c

### Purpose
`geneve.c` implements the Linux rtnetlink `geneve` virtual net_device and UDP tunnel endpoint for Generic Network Virtualization Encapsulation. It supports fixed endpoint tunnels and collect-metadata tunnels used by controllers such as Open vSwitch, IPv4 and IPv6 outer transport, per-network-namespace device and socket tracking, UDP tunnel offload announcements, GRO/GSO handling, ECN handling, and exported fallback device creation through `geneve_dev_create_fb()`.

### Important APIs, Types, And Functions
Key local state is split across `struct geneve_net`, `struct geneve_sock`, `struct geneve_dev`, and `struct geneve_config`. `geneve_net` owns per-netns device and socket lists. `geneve_sock` wraps one UDP socket, a reference count, collect-metadata/GRO-hint attributes, and a VNI hash table. `geneve_dev` is the netdev private area and stores IPv4/IPv6 socket RCU pointers, GRO cells, and the configured `ip_tunnel_info`.

Important entry points are `geneve_newlink()`, `geneve_changelink()`, `geneve_dellink()`, `geneve_open()`, `geneve_stop()`, `geneve_xmit()`, `geneve_udp_encap_recv()`, `geneve_gro_receive()`, `geneve_gro_complete()`, `geneve_fill_metadata_dst()`, and `geneve_dev_create_fb()`. Link registration is via `struct rtnl_link_ops geneve_link_ops`; runtime netdev operations are in `geneve_netdev_ops`.

Helper groups include VNI conversion and lookup (`vni_to_tunnel_id()`, `tunnel_id_to_vni()`, `geneve_lookup*()`), socket lifecycle (`geneve_socket_create()`, `geneve_sock_add()`, `geneve_sock_release()`), encapsulation (`geneve_build_header()`, `geneve_build_skb()`, `geneve_xmit_skb()`, `geneve6_xmit_skb()`), and netlink parsing/reporting (`geneve_validate()`, `geneve_nl2info()`, `geneve_fill_info()`).

### Control Flow
Creation starts in `geneve_newlink()`: defaults are prepared, netlink attributes are parsed by `geneve_nl2info()`, duplicate and collect-metadata conflicts are rejected by `geneve_configure()`, and the device is registered and linked into the per-netns list. `geneve_open()` creates or reuses UDP sockets for IPv4, IPv6, or both when collect metadata is enabled. Each opened socket gets UDP tunnel callbacks and stores a `geneve_sock` in `sk_user_data`.

RX enters through UDP encapsulation callbacks. `geneve_udp_encap_recv()` validates the Geneve base header and version, looks up the device by VNI/source address unless the socket is metadata mode, validates inner protocol policy, pulls the outer headers, optionally processes post-decap GRO hints, and calls `geneve_rx()`. `geneve_rx()` creates tunnel metadata when needed, rejects unsupported critical options outside metadata mode, converts Ethernet payloads with `eth_type_trans()` or sets packet host fields for inherited protocols, performs ECN decapsulation, then submits through GRO cells or directly to `netif_rx()` for hinted encapsulated packets.

TX starts in `geneve_xmit()`, which either consumes `skb_tunnel_info()` for collect-metadata mode or the static device config. IPv4 and IPv6 transmit paths perform VLAN/IP preparation, source port selection, route lookup with optional dst cache, PMTU checks and local EMSGSIZE loopback, TTL/TOS/DF selection, Geneve header construction, option copying, offload preparation, and final UDP tunnel send.

GRO flow parses Geneve headers and options in `geneve_gro_receive()`. A private netdev-class option can carry nested header hints for double encapsulation; the code validates offsets, protocols, checksums, and flow equivalence before handing the inner protocol to Ethernet or typed GRO callbacks.

### State And Persistence Behavior
All state is in kernel memory. Per-netns lists persist while the net namespace lives. Socket sharing is reference-counted by destination port, family, and GRO-hint setting. Device lookup from RX uses RCU-protected VNI hash lists. `dst_cache` persists route choices per `ip_tunnel_info` until reset. `geneve_changelink()` quiesces TX/RX by nulling RCU socket pointers and socket `sk_user_data`, synchronizes with in-flight users, updates config, then restores pointers.

There is no disk persistence. User-visible configuration is reflected through rtnetlink attributes from `geneve_fill_info()`.

### Dependencies And Integration Points
The driver integrates with rtnetlink, net namespaces, UDP tunnel sockets, `dst_metadata`, `ip_tunnel_info`, GRO cells, `udp_tunnel_*` transmit helpers, netdev notifier events for UDP tunnel offload port push/drop, ethtool driver info, IPv6 conditionals, and Open vSwitch style fallback creation exported as GPL.

### Risks
Risk areas are strict option and header length validation, collect-metadata exclusivity on a UDP port, RCU socket lifetime during changelink and teardown, GRO-hint trust boundaries, PMTU fallback behavior, IPv6 zero checksum choices, and compatibility with devices using `inner_proto_inherit`. Another important edge is shared socket attributes: sockets are reused only when family, port, and GRO-hint match, while `collect_md` is stored on the shared socket and guarded by config-level exclusivity.

### Test Signals
Useful signals include `ip link add type geneve` permutations for IPv4, IPv6, VNI, port range, DF, TTL/TOS, metadata, `inner_proto_inherit`, and GRO hint; duplicate tunnel and metadata-on-same-port rejection; packet RX/TX for Ethernet and inherited inner protocols; PMTU and ICMP generation; ECN decapsulation logging and stats; UDP tunnel offload notifier behavior; namespace teardown; and OVS collect-metadata fallback creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/geneve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/gtp.c -->
## sources/distributed-fs/ceph-client/drivers/net/gtp.c

### Purpose
`gtp.c` implements the Linux `gtp` virtual network device for GTP-U tunneling as used by GSM/3GPP packet core networks. It supports GTPv0 and GTPv1-U, IPv4 and IPv6 subscriber PDP contexts, optional kernel-created UDP sockets, userspace-supplied sockets, generic-netlink PDP management, echo request/response support for kernel-created sockets, and per-netns device tracking.

### Important APIs, Types, And Functions
`struct gtp_dev` is the netdev private state: UDP sockets for GTP0 and GTP1-U, role, hash tables, per-netns list linkage, restart count, and socket ownership. `struct pdp_ctx` represents one active subscriber tunnel, with version-specific TID/TEI state, MS address, peer address, selected socket, device pointer, and TX sequence. PDP contexts are indexed in two RCU hash tables, one by tunnel ID and one by MS address. `struct gtp_net` tracks devices per namespace.

Runtime datapath functions are `gtp_encap_recv()`, `gtp0_udp_encap_recv()`, `gtp1u_udp_encap_recv()`, `gtp_rx()`, `gtp_dev_xmit()`, `gtp_build_skb_ip4()`, `gtp_build_skb_ip6()`, and the outer builders `gtp_build_skb_outer_ip4()` and `gtp_build_skb_outer_ip6()`. Management functions include `gtp_newlink()`, `gtp_dellink()`, `gtp_encap_enable()`, `gtp_create_sockets()`, `gtp_genl_new_pdp()`, `gtp_genl_del_pdp()`, `gtp_genl_get_pdp()`, `gtp_genl_dump_pdp()`, and `gtp_genl_send_echo_req()`.

### Control Flow
Device creation runs through rtnetlink. `gtp_newlink()` parses role, hash size, restart count, and socket mode. It allocates PDP hash tables, either creates bound UDP sockets or attaches encapsulation callbacks to userspace-provided UDP sockets, adjusts MTU/headroom for IPv6 sockets, registers the netdev, and links it into the netns list.

RX begins in `gtp_encap_recv()`, which uses UDP `encap_type` to dispatch to v0 or v1-U parsing. The v0 path checks flags, handles echo messages when sockets are kernel-created, validates TPDU type, identifies inner IPv4/IPv6, finds a PDP by TID and family, and calls `gtp_rx()`. The v1 path similarly handles echo messages, optional sequence/N-PDU/extension header length, extension-header parsing, TEI lookup, and decapsulation. `gtp_rx()` verifies the inner MS address against the PDP and device role, pulls GTP plus UDP headers, resets packet headers, accounts RX stats, and injects with `__netif_rx()`.

TX from the virtual device checks headroom and inner IP availability, then looks up a PDP by source or destination MS address depending on SGSN/GGSN role. It routes to the PDP peer using the PDP socket family, enforces circular route and PMTU checks, pushes a GTPv0 or GTPv1 header, and sends over UDP tunnel helpers. GTPv0 increments a per-PDP sequence counter and includes flow/TID; GTPv1 uses the outgoing TEI.

Generic-netlink commands manage PDP state. `GTP_CMD_NEWPDP` validates version-specific required attributes, resolves the target link and socket, and calls `gtp_pdp_add()`. That function rejects inconsistent address families, detects duplicate MS or TEID/TID entries, supports limited update semantics without replace, and inserts new contexts into both hash tables under RCU. Delete and get paths resolve by link plus MS address or tunnel ID. Multicast notifications are emitted for new/delete and echo responses.

### State And Persistence Behavior
PDP contexts are dynamic in-memory state only. They persist until generic-netlink deletion, device deletion, socket destruction, or namespace teardown. Each context holds a reference to its UDP socket and is freed with `call_rcu()`. Userspace-supplied sockets are held with `sock_hold()` and released when encapsulation is disabled. Kernel-created sockets are released through `udp_tunnel_sock_release()`. A random jhash seed is initialized at module load.

### Dependencies And Integration Points
The driver depends on UDP tunnel socket callbacks, rtnetlink link kind `gtp`, generic netlink family `gtp`, net namespace generic storage, IPv4/IPv6 routing, ICMP/ICMPv6 PMTU signaling, RCU hlist traversal, and UAPI attributes from `<linux/gtp.h>`. Userspace control planes configure PDP contexts through generic netlink and may either own UDP sockets or ask the kernel to create them.

### Risks
Risk areas include RCU lifetime around PDP deletion and generic-netlink get/delete, update semantics when one of the MS or tunnel-key entries exists but not both, address family mismatches between peer attributes and socket family, IPv6 PDP prefix assumptions that only compare the first 64 bits, extension header parsing bounds, echo behavior differences between kernel-created and userspace-owned sockets, and PMTU handling for nested tunnels. In `gtp_dev_xmit()`, IPv6 outer transmit uses unioned route storage, so regression tests should cover that path carefully.

### Test Signals
Exercise rtnetlink creation with userspace FDs and `IFLA_GTP_CREATE_SOCKETS`, IPv4 and IPv6 local sockets, GGSN and SGSN roles, invalid roles/hash sizes, PDP add/update/delete/get/dump for GTPv0 and GTPv1, duplicate MS and TEI/TID conflicts, IPv6 prefix validation, TPDU RX decapsulation, TX encapsulation for both inner families and outer socket families, PMTU/ICMP behavior, echo request/response multicast notifications, and namespace/device teardown with active PDP contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/gtp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/hyperv/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/hyperv/Kconfig

### Purpose
This Kconfig entry exposes `CONFIG_HYPERV_NET`, the Microsoft Hyper-V virtual network driver, as a tristate option. It is the build-time gate for the `hv_netvsc` module or built-in driver.

### Important APIs, Types, And Functions
There are no C APIs in this file. The important symbol is `HYPERV_NET`. It depends on `HYPERV_VMBUS` and selects `UCS2_STRING` and `NLS`, which are required by the broader Hyper-V/RNDIS support stack.

### Control Flow
Kconfig evaluation enables this option only when Hyper-V VMBus support is available. If selected as built-in or module, the Makefile in the same directory builds `hv_netvsc.o`.

### State And Persistence Behavior
The file contributes only kernel configuration state. It has no runtime persistence, but the selected value determines whether the Hyper-V network driver is present in the built kernel or modules.

### Dependencies And Integration Points
The direct integration point is the kernel Kconfig system and the local Makefile. Runtime driver code depends on VMBus, so the `depends on HYPERV_VMBUS` relationship is the critical safety gate.

### Risks
The main risk is dependency drift: if runtime code adds new library or subsystem requirements, this Kconfig must select or depend on them. A missing dependency would show up as build failures when `HYPERV_NET=m/y`.

### Test Signals
Build matrix checks should include `HYPERV_NET=n`, `m`, and `y` with `HYPERV_VMBUS` enabled, and ensure the option is not offered or cannot be selected without VMBus support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/hyperv/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/hyperv/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/hyperv/Makefile

### Purpose
This Makefile wires `CONFIG_HYPERV_NET` to the composite `hv_netvsc.o` driver object.

### Important APIs, Types, And Functions
There are no runtime APIs. The important build variables are `obj-$(CONFIG_HYPERV_NET)` and `hv_netvsc-y`. The composite object includes `netvsc_drv.o`, `netvsc.o`, `rndis_filter.o`, `netvsc_trace.o`, and `netvsc_bpf.o`.

### Control Flow
When `CONFIG_HYPERV_NET` is enabled, Kbuild creates `hv_netvsc.o` from the listed component objects and either links it into vmlinux or emits a module, depending on the tristate value.

### State And Persistence Behavior
The file controls build composition only. It has no runtime state or persistence.

### Dependencies And Integration Points
It integrates with Kbuild and the `HYPERV_NET` symbol from `Kconfig`. The object list defines the module boundary shared by datapath, RNDIS filter, tracepoints, and XDP/BPF support.

### Risks
Any new source file for the Hyper-V net driver must be added here or it will not build. Removing or renaming objects must be coordinated with exported symbols across the component files.

### Test Signals
Compile with `CONFIG_HYPERV_NET=m` and inspect that one `hv_netvsc.ko` is produced with all component object code linked. Built-in compile should also succeed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/hyperv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/hyperv/hyperv_net.h -->
## sources/distributed-fs/ceph-client/drivers/net/hyperv/hyperv_net.h

### Purpose
`hyperv_net.h` is the shared internal ABI and state header for the Hyper-V NetVSC driver. It defines NDIS/RNDIS structures, NVSP protocol messages, buffer sizing constants, per-device and per-channel state, stats structures, XDP hooks, and function prototypes shared by `netvsc.c`, `netvsc_drv.c`, `rndis_filter.c`, and `netvsc_bpf.c`.

### Important APIs, Types, And Functions
The most important runtime structures are `struct hv_netvsc_packet`, `struct netvsc_device_info`, `struct rndis_device`, `struct net_device_context`, `struct netvsc_channel`, and `struct netvsc_device`. `hv_netvsc_packet` is compact enough for `skb->cb` and carries send-buffer, DMA, queue, and packet accounting metadata. `netvsc_device` stores negotiated NVSP version, VMBus shared receive/send buffers and GPADLs, channel table, RNDIS extension, queue counts, and teardown flags. `netvsc_channel` stores per-channel NAPI, receive copy buffer, multi-send and receive-completion rings, RSC aggregation state, XDP program, XDP RX queue, and per-channel stats.

The header also defines NVSP versions and message structs from init through v6 packet-direct messages, RNDIS request/response packet formats, NDIS RSS and offload definitions, receive-side coalescing state, and helpers such as `netvsc_rqstor_size()` and `netvsc_get_hash()`.

### Control Flow
The header itself has no executable control flow beyond inline helpers. Its definitions describe the driver flow: VMBus/NVSP negotiation creates a `netvsc_device`, RNDIS initializes the virtual NIC, channels use NAPI for host ring processing, RNDIS packets move over NVSP messages, and XDP hooks can process receive data or transmit frames. The inline `netvsc_get_hash()` chooses full L4 hashing or address-only hashing based on configured hash policy and packet protocol, setting a software hash when needed.

### State And Persistence Behavior
State declared here is runtime-only and owned by the driver. Persistent host/guest protocol state exists only for the lifetime of the VMBus device. Notable synchronization primitives include RCU pointers for `nvdev`, VF netdev, and XDP programs; completions for channel init and VF association; wait queues for drain/subchannel open; atomics for queue sends/open channels; and per-CPU/stat sync structures.

### Dependencies And Integration Points
The header depends on Linux Hyper-V VMBus APIs, RNDIS definitions, netdevice, XDP, jhash, VLAN/checksum/offload UAPI, and NDIS/NVSP protocol constants. It is the integration contract between core VMBus transport (`netvsc.c`), RNDIS control (`rndis_filter.c`), user-facing netdev logic (`netvsc_drv.c`), and XDP support (`netvsc_bpf.c`).

### Risks
Risk concentrates in packed protocol layouts and size/offset constants. Any ABI drift can break host communication. Buffer-size constants must match host expectations, especially receive/send sections and maximum transfer page ranges. RCU-managed pointers and BPF program references require careful ownership. `netvsc_get_hash()` must preserve Azure host hashing limitations for fragmented UDP traffic.

### Test Signals
Compile-time layout coverage, sparse/packed-structure warnings, and cross-file build tests are critical. Runtime signals include successful NVSP negotiation, RNDIS initialization, multi-channel RSS setup, checksum/LSO/RSC offload negotiation, VF association, XDP attach/detach, and channel teardown without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/hyperv/hyperv_net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/hyperv/netvsc.c -->
## sources/distributed-fs/ceph-client/drivers/net/hyperv/netvsc.c

### Purpose
`netvsc.c` is the core VMBus/NVSP datapath for the Hyper-V synthetic network driver. It negotiates protocol version with the host, allocates and shares receive/send buffers through GPADLs, opens channels, sends and receives RNDIS packets over VMBus, handles TX completions and RX completions, supports subchannels and VF datapath switching, and performs teardown.

### Important APIs, Types, And Functions
External entry points include `netvsc_device_add()`, `netvsc_device_remove()`, `netvsc_send()`, `netvsc_poll()`, `netvsc_channel_cb()`, `netvsc_alloc_recv_comp_ring()`, `netvsc_dma_unmap()`, and `netvsc_switch_datapath()`. Internal setup and teardown helpers are `alloc_net_device()`, `netvsc_connect_vsp()`, `negotiate_nvsp_ver()`, `netvsc_init_buf()`, revoke/teardown helpers for send and receive GPADLs, and `free_netvsc_device_rcu()`.

TX helpers include `netvsc_get_next_send_section()`, `netvsc_copy_to_send_buf()`, `netvsc_dma_map()`, `netvsc_build_mpb_array()`, `netvsc_send_pkt()`, and multi-send batching in `netvsc_send()`. RX helpers include `netvsc_receive()`, `rndis_filter_receive()` integration, receive-completion ring management, `netvsc_receive_inband()`, `netvsc_send_table()`, `netvsc_send_vf()`, and `netvsc_process_raw_pkt()`.

### Control Flow
Device add allocates `netvsc_device`, initializes all channel slots and XDP RX queues, adds and enables primary-channel NAPI, opens the VMBus channel, negotiates the newest supported NVSP version, sends NDIS version/config, initializes shared receive and send buffers, and publishes `nvdev` with RCU. Buffer initialization allocates guest memory, establishes GPADLs, sends NVSP buffer messages, waits for host completions, validates host-provided section sizes/counts, and initializes send-section and receive-completion rings.

TX through `netvsc_send()` first rejects destroyed devices, chooses direct send for control/XDP traffic, otherwise attempts to batch small packets into a pre-shared send buffer. It may copy all data, copy only the RNDIS header, or send page buffers directly. `netvsc_send_pkt()` builds an NVSP RNDIS packet message, maps page buffers through DMA bounce buffers in isolation VMs, sends either MPB descriptors or in-band packets, tracks outstanding queue sends, and stops/wakes TX queues based on VMBus ring availability. TX completion releases send-buffer slots, updates stats, unmaps DMA, consumes SKBs, and wakes queues or drain waiters.

RX uses `netvsc_channel_cb()` to defer host-ring processing to NAPI. `netvsc_poll()` iterates VMBus descriptors until budget, processes completions, transfer-page RX packets, and in-band messages, flushes XDP redirects, sends queued RX completions to the host, and re-enables host interrupts when appropriate. `netvsc_receive()` validates NVSP and transfer-page metadata, checks receive-buffer bounds, forwards each RNDIS packet to `rndis_filter_receive()`, and enqueues one completion for the transfer page descriptor.

Teardown revokes host-visible buffers, nulls the RCU `nvdev`, disables and deletes NAPI for all channels, closes VMBus, tears down GPADLs in the host-version-specific order, and frees memory after an RCU grace period.

### State And Persistence Behavior
All state is per VMBus device and in memory. Shared send/receive buffers persist until revoke/GPADL teardown. `send_section_map` is a bitmap allocator for host-visible send sections. Each channel holds outstanding send count, pending multi-send batch state, receive-completion ring indices, RSC/XDP state, and stats. `destroy` and `tx_disable` gate queue wakeup and drain behavior. There is no disk persistence.

### Dependencies And Integration Points
The file integrates with Hyper-V VMBus packet APIs, GPADL memory sharing, RNDIS filter code, netdevice NAPI and queue APIs, XDP RX queue registration, DMA mapping for isolation VMs, tracepoints, VF association messages, and NVSP protocol structures from `hyperv_net.h`.

### Risks
Risk areas include host message length validation, GPADL revoke/teardown ordering across host versions, send-buffer bitmap concurrency, multi-send batching ownership of SKBs and send sections, DMA cleanup on all send failure paths, NAPI disable/delete ordering, transfer-page range bounds, receive-completion ring overflow, RCU publication of `nvdev`, and datapath switching while a VF is appearing or disappearing.

### Test Signals
Important tests include driver load/unload on multiple Hyper-V host versions, NVSP version fallback, isolation VM DMA path, send-buffer batching and direct page-buffer TX, TX ring low/high water queue stop/wake, RX transfer-page bounds rejection, receive completion backpressure, RNDIS packet processing, XDP redirect flushing, subchannel setup fallback, VF association and datapath switching, and teardown under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/hyperv/netvsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/hyperv/netvsc_bpf.c -->
## sources/distributed-fs/ceph-client/drivers/net/hyperv/netvsc_bpf.c

### Purpose
`netvsc_bpf.c` adds XDP/BPF support to the Hyper-V NetVSC driver. It attaches and detaches XDP programs across NetVSC receive channels, propagates XDP programs to an associated VF when possible, executes XDP on received packets copied from NetVSC RSC state, and implements `ndo_xdp_xmit` by either forwarding to the VF or converting XDP frames into SKBs for synthetic transmit.

### Important APIs, Types, And Functions
Main entry points are `netvsc_run_xdp()`, `netvsc_xdp_get()`, `netvsc_xdp_set()`, `netvsc_vf_setxdp()`, `netvsc_bpf()`, and `netvsc_ndoxdp_xmit()`. `netvsc_xdp_fraglen()` computes aligned SKB fragment requirements. `netvsc_ndoxdp_xmit_fm()` converts one `xdp_frame` into an SKB and sends it through the existing NetVSC transmit path via `netvsc_xdp_xmit()`.

### Control Flow
On receive, `netvsc_run_xdp()` reads the channel's RCU BPF program pointer. If no program is attached, it returns `XDP_PASS`. Otherwise it validates the packet length against MTU plus Ethernet header, allocates a page, prepares an `xdp_buff` with `NETVSC_XDP_HDRM` headroom, copies packet data from `nvchan->rsc`, runs the program, and handles actions. `XDP_PASS` and `XDP_TX` keep the page for later handling; `XDP_REDIRECT` calls `xdp_do_redirect()`, marks the channel for flush, and updates stats; drops and aborted/invalid actions free the page and update or trace error state.

XDP attach uses `netvsc_bpf()` for `XDP_SETUP_PROG`. `netvsc_xdp_set()` rejects MTUs that would exceed a page-backed XDP buffer and rejects LRO, increments program references for all channels, publishes the program to every channel with RCU assignment, and drops old references. If a VF is present, `netvsc_vf_setxdp()` propagates the program through the VF's `ndo_bpf`; failures roll back the synthetic attachment.

`netvsc_ndoxdp_xmit()` first prefers the VF path when the VF is running, carrier is up, netpoll is not active, the VF supports XDP transmit, and the active datapath is VF. Otherwise it selects a synthetic TX queue by CPU, converts frames to SKBs, computes NetVSC hash metadata, records RX queue, calls `netvsc_xdp_xmit()`, and updates XDP TX stats.

### State And Persistence Behavior
Attached programs are stored as RCU pointers in every `netvsc_channel`. Program references are explicitly acquired for additional channels and released on replacement. Per-channel RX stats record XDP drops, redirects, TX, packets, and bytes; TX stats record `xdp_xmit`. There is no persistent storage beyond runtime netdev and channel state.

### Dependencies And Integration Points
The file integrates with Linux XDP core APIs, BPF program reference management, netdevice `ndo_bpf` and `ndo_xdp_xmit`, RCU, VF representor/associated netdev handling from `net_device_context`, NetVSC synthetic transmit helpers, and RNDIS receive state via `nvchan->rsc`.

### Risks
The receive path copies packet data into a newly allocated page for XDP, so allocation failure and MTU/page-size limits are central. Program propagation must keep synthetic and VF state consistent on failure. Reference balancing across multiple channels is sensitive to `nvdev->num_chn`. XDP redirect requires a later flush in `netvsc_poll()`. The fallback XDP transmit path converts frames to SKBs, so performance and ownership semantics differ from native zero-copy XDP.

### Test Signals
Test XDP attach/detach with and without a VF, attach rejection with LRO enabled, MTU too large rejection, channel-count reference handling, XDP actions PASS/DROP/ABORTED/REDIRECT/TX, redirect flush behavior, `ndo_xdp_xmit` VF forwarding and synthetic fallback, netpoll disabling the VF fast path, and teardown while programs are attached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/hyperv/netvsc_bpf.c -->
