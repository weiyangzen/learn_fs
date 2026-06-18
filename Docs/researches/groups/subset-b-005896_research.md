# subset-b-005896 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netdevice.h -->
## sources/distributed-fs/ceph-client/include/linux/netdevice.h

### Purpose
`netdevice.h` is the central Linux networking device contract. It defines `struct net_device`, its driver callback table, queue/NAPI state, hardware address lists, packet type registration, device notifier data, statistics helpers, feature negotiation helpers, transmit/receive entry points, and link-state helpers. It is not a Ceph-specific file; in this source tree it supplies the kernel networking ABI surface that Ceph-client code and its dependencies compile against.

### Important APIs, Types, and Functions
The most important type is `struct net_device`, which aggregates identity (`name`, `ifindex`, namespace), feature masks, MTU/header limits, per-queue arrays, RX/TX state, protocol private pointers, XDP and netfilter hook pointers, stats storage, lifecycle state, refcount tracking, sysfs/device metadata, and optional offload subsystems. `struct net_device_ops` is the driver-facing operations table with callbacks such as `ndo_open`, `ndo_stop`, `ndo_start_xmit`, queue selection, MTU/MAC changes, VLAN, SR-IOV, FDB/MDB, bridge, XDP, timestamping, tunnel, and offload hooks. `struct napi_struct` and `struct gro_node` define polling/GRO state, while `struct netdev_queue` defines TX queue locking, qdisc pointers, BQL/DQL accounting, watchdog timestamps, NUMA metadata, and optional XDP socket pool state.

Key inline helpers include `dev_queue_xmit()`, `dev_direct_xmit()`, `netdev_start_xmit()`, `netdev_get_tx_queue()`, `skb_get_tx_queue()`, NAPI add/schedule/complete/delete wrappers, TX queue stop/start/wake helpers, BQL accounting helpers, `netif_running()`, `netif_carrier_ok()`, `netif_oper_up()`, `netdev_priv()`, namespace helpers, refcount helpers (`netdev_hold`, `netdev_put`, legacy `dev_hold`, `dev_put`), hardware-header helpers, feature helpers (`net_gso_ok`, `skb_gso_ok`, `netif_needs_gso`, `netdev_intersect_features`), and type predicates such as `netif_is_bridge_port`, `netif_is_bond_master`, and `netif_is_macsec`.

### Control Flow
The header describes the common RX/TX control flow rather than implementing full paths. TX callers enter through `dev_queue_xmit()` or `dev_direct_xmit()`, select a queue, lock according to `lltx`, update `netdev_xmit.more`, call `ndo_start_xmit`, then update queue timestamps and BQL state if the packet is accepted. Queue state helpers manipulate `__QUEUE_STATE_DRV_XOFF`, `__QUEUE_STATE_STACK_XOFF`, and `__QUEUE_STATE_FROZEN` to coordinate drivers, qdiscs, watchdogs, and BQL. RX flow is represented through NAPI scheduling (`napi_schedule`, `napi_complete_done`), GRO delivery (`napi_gro_receive`, `napi_gro_frags`), receive entry points (`netif_rx`, `netif_receive_skb`), and optional RX handlers that can consume, redirect, force exact delivery, or pass skbs.

Lifecycle flow is expressed through allocation (`alloc_netdev_mqs`), registration (`register_netdevice`, `register_netdev`), open/close, notifier emission, namespace movement, unregister queues, and `free_netdev`. Link state transitions set bits in `dev->state` and trigger linkwatch. Address-list flows synchronize `uc`, `mc`, and `dev_addrs` lists to hardware through sync/unsync callbacks.

### State and Persistence
All state is in-memory kernel state. There is no durable persistence. Persistence-like behavior comes from long-lived registered `net_device` instances, per-net namespace device indexes/lists, sysfs exposure, refcount trackers, RCU-protected pointers, per-CPU statistics, and timers/work lists. The header is explicit about locking: hot-path fields are cacheline grouped; `dev->mtu` and GRO/GSO size fields are read locklessly with `READ_ONCE`; many writers require RTNL; device-local `dev->lock` protects selected queue/NAPI/device fields; address lists use `addr_list_lock`; NAPI deletion requires an RCU grace period; netfilter hooks and protocol pointers are RCU-protected.

### Dependencies and Integration Points
The header depends on core kernel primitives (`atomic`, `refcount`, `rcu`, `list`, `rbtree`, `hashtable`, `timer`, `workqueue`, percpu storage, mutex/spinlock APIs), skb and net namespace definitions, qdisc/scheduler concepts, uapi netdevice and rtnetlink structures, XDP/BPF, ethtool, DCB, VLAN, DSA, XFRM, TLS, MACsec, UDP tunnel offload, page pools, and netfilter ingress/egress hooks. Integration points include driver `ndo_*` tables, packet protocol handlers (`packet_type`), packet offload callbacks, netdevice notifier chains, upper/lower device graph helpers, rtnetlink/sysfs/ethtool interfaces, checksum/GSO/GRO subsystems, and XDP/AF_XDP.

### Risks
The main risks are synchronization and ownership errors. Drivers must stop TX queues before returning `NETDEV_TX_BUSY`; BQL byte accounting must match enqueue/completion counts; RCU-protected pointers and RX handlers must not be freed before grace periods; direct writes to `dev_addr` are guarded by shadow state; MTU and feature changes need RTNL/device locking; missing memory barriers around queue stop/completion can lead to stuck queues; refcount tracker misuse can leak or prematurely free devices; and malformed `ndo_*` implementations can corrupt packet ownership. `struct net_device` is highly configuration-dependent, so field assumptions across kernel versions or config options are fragile.

### Test Signals
Useful signals include successful compilation across relevant configs, driver bring-up/down tests, multi-queue TX/RX tests, NAPI scheduling and deletion tests with lockdep/RCU debugging, packet forwarding and GSO/GRO coverage, BQL watchdog and queue-stall tests, netdevice notifier sequencing, namespace move tests, address-list sync/unsync tests, XDP attach/detach tests, and runtime checks for warnings from `DEBUG_NET_WARN_ON_ONCE`, `WARN_ONCE`, lockdep, KASAN, and refcount tracking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netdevice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netdevice_xmit.h -->
## sources/distributed-fs/ceph-client/include/linux/netdevice_xmit.h

### Purpose
This small header defines per-execution-context transmit bookkeeping used by `netdevice.h` and the network transmit path. It isolates recursion and batching fields from the larger netdevice interface.

### Important APIs, Types, and Functions
The only concrete type is `struct netdev_xmit`. It contains `recursion` for nested transmit detection, `more` for batching/doorbell decisions exposed by `netdev_xmit_more()`, optional `skip_txqueue` for egress handling, optional mirred action nesting state (`sched_mirred_nest` plus `sched_mirred_dev[MIRRED_NEST_LIMIT]`), and optional `nf_dup_skb_recursion` for duplicate netdevice netfilter recursion control. `MIRRED_NEST_LIMIT` is set to four when mirred actions are enabled.

### Control Flow
The structure is embedded in per-CPU `softnet_data` on non-RT kernels and in current task state on PREEMPT_RT via helpers in `netdevice.h`. Transmit entry code increments/decrements recursion, sets `more` before calling driver `ndo_start_xmit`, and consults recursion fields to prevent unbounded re-entry from virtual devices, mirred actions, or netfilter duplication.

### State and Persistence
State is transient and scoped to a CPU or task. It is not persisted and should be treated as hot-path scratch state. Conditional fields mean layout changes with kernel config.

### Dependencies and Integration Points
The header depends on `CONFIG_NET_ACT_MIRRED`, `CONFIG_NET_EGRESS`, and `CONFIG_NF_DUP_NETDEV`, and forward-declares `struct net_device`. Its consumers are the transmit helpers, traffic-control mirred action code, egress path, and netfilter duplication path.

### Risks
Incorrect recursion accounting can cause stack overflow, packet loops, or false-positive drops. Incorrect `more` handling can delay TX doorbells or hurt batching. Config-dependent fields make direct layout assumptions unsafe.

### Test Signals
Exercise nested virtual-device transmission, mirred redirect/mirror chains, NF_DUP_NETDEV paths, PREEMPT_RT and non-RT builds, and batching behavior where `xmit_more` changes TX completion latency or throughput.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netdevice_xmit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter.h -->
## sources/distributed-fs/ceph-client/include/linux/netfilter.h

### Purpose
`netfilter.h` defines the in-kernel hook interface for packet filtering, NAT/conntrack integration hooks, checksum/route helpers, and fallback no-op behavior when netfilter is disabled. It is the dispatch contract between protocol paths, hook providers, conntrack/NAT modules, and packet continuations.

### Important APIs, Types, and Functions
Important types include `struct nf_hook_state` (hook number, protocol family, input/output devices, socket, net namespace, continuation), `nf_hookfn`, `struct nf_hook_ops` (registered hook metadata and priority), `struct nf_hook_entry`, `struct nf_hook_entries`, `struct nf_sockopt_ops`, `struct nf_nat_hook`, `struct nf_ct_hook`, `struct nfnl_ct_hook`, and `struct nf_defrag_hook`. Important helpers include `NF_DROP_GETERR`, `NF_DROP_REASON`, `nf_inet_addr_cmp`, `nf_inet_addr_mask`, `nf_hook_state_init`, `nf_hook`, `NF_HOOK`, `NF_HOOK_COND`, `NF_HOOK_LIST`, `nf_nat_decode_session`, and conntrack fallbacks such as `nf_ct_attach` and `nf_ct_get_tuple_skb`.

### Control Flow
Protocol code calls `nf_hook()` or `NF_HOOK*`. With jump labels enabled, constant hook sites can skip work if no hooks are registered. Otherwise the function enters RCU, selects the per-net hook array by protocol family, initializes `nf_hook_state`, and calls `nf_hook_slow()` or list variant. Return value `1` means the caller must continue with `okfn`; other verdicts indicate the hook consumed, queued, stolen, or dropped the skb. `NF_HOOK` and `NF_HOOK_COND` wrap this pattern and invoke `okfn` when allowed. NAT and conntrack integration is indirect through RCU-published hook tables.

### State and Persistence
State is per-net namespace hook arrays plus global RCU hook pointers for NAT, conntrack, netlink conntrack, and defragmentation. Hook arrays are read under RCU and updated by register/unregister APIs. There is no durable persistence; module registrations and per-net hook state exist for module/netns lifetimes.

### Dependencies and Integration Points
The header integrates with `sk_buff`, `net_device`, sockets, network namespaces, static keys, module ownership, netfilter verdict definitions, conntrack zones, `flowi`, NAT, defrag, and netlink conntrack. Device-level ingress/egress hooks referenced by `struct net_device` point back into this contract.

### Risks
Packet ownership is verdict-dependent and easy to get wrong: hooks returning stolen/queued/drop must own disposal, while return `1` requires the caller to continue. RCU hook pointer access must be respected. Hook priority ordering affects security behavior. The no-netfilter fallback changes control flow to unconditional `okfn`, so code must compile and behave with netfilter disabled.

### Test Signals
Register/unregister hooks under packet load with RCU debugging, verify hook priority ordering, exercise all verdicts including `NF_STOLEN` and drop-with-error, build with and without `CONFIG_NETFILTER`, test IPv4/IPv6/ARP/bridge family selection, and cover NAT/conntrack module load/unload paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/ip_set.h -->
## sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/ip_set.h

### Purpose
`ip_set.h` defines the kernel-side core API for ipset set types, elements, extensions, netlink parsing helpers, timeout handling, and match/add/delete/test operations used by xtables/nft integration.

### Important APIs, Types, and Functions
Core definitions include `enum ip_set_feature`, `enum ip_set_extension`, `enum ip_set_ext_id`, `struct ip_set_ext_type`, `struct ip_set_counter`, `struct ip_set_comment`, `struct ip_set_skbinfo`, `struct ip_set_ext`, `struct ip_set_adt_opt`, `struct ip_set_type_variant`, `struct ip_set_region`, `struct ip_set_type`, and `struct ip_set`. The header declares set type registration (`ip_set_type_register`, `ip_set_type_unregister`), reference APIs (`ip_set_get_byname`, `ip_set_put_byindex`, `ip_set_nfnl_get_byindex`, `ip_set_nfnl_put`), packet operations (`ip_set_add`, `ip_set_del`, `ip_set_test`), allocation and netlink helpers, extension helpers, address extractors, timeout helpers, and extension initializer macros `IP_SET_INIT_KEXT` and `IP_SET_INIT_UEXT`.

### Control Flow
Set-type modules register an `ip_set_type` with create policies and callbacks. A created `struct ip_set` points at a type and variant; packet path operations call `kadt`, userspace netlink operations call `uadt`, and both eventually use low-level `adt[]` functions. Variants own resizing, destroying, flushing, expiring, listing, and same-set comparison. Extensions are laid out inside element storage using offsets and are initialized/matched/destroyed through shared helpers. Timeout conversion normalizes user seconds into jiffies and permanent entries use zero.

### State and Persistence
Ip sets are in-memory per-net structures referenced by id/name. `struct ip_set` tracks lock, regular and netlink refs, type/variant, family, revision, enabled extensions, create flags, default timeout, element counts, dynamic extension size, element data size, extension offsets, and type-specific data. Comments use RCU storage; counters use atomic64; variants may use region locks. No durable storage is defined by this header.

### Dependencies and Integration Points
The header depends on IPv4/IPv6 headers, netlink attributes, netfilter address utilities, xtables action parameters, vmalloc-backed allocation, and uapi ipset definitions. It integrates with packet matches/targets, netlink create/ADT commands, set-type modules, timeout garbage collection, and skb metadata modification via skbinfo extensions.

### Risks
Risks include extension offset/size alignment mistakes, missing comment destruction, refcount misuse during swap/dump, timeout jiffies overflow, incorrect byte-order expectations for netlink attributes, set-type revision mismatch, region-lock races, and ADT semantics where positive/zero/negative returns have distinct meanings. Force-add and nomatch flags can alter expected behavior.

### Test Signals
Test create/add/delete/test/list/flush/destroy for every set type and revision, extension combinations (timeout/counter/comment/skbinfo), byte-order validation, timeout expiry and GC cadence, swap/list races, reference lifecycle through netlink dumps, and packet-path matching for IPv4/IPv6 source/destination dimensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/ip_set.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/ip_set_bitmap.h -->
## sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/ip_set_bitmap.h

### Purpose
This header provides bitmap ipset kernel constants layered on the uapi bitmap definitions.

### Important APIs, Types, and Functions
It defines `IPSET_BITMAP_MAX_RANGE` as `0x0000FFFF` and an enum of add-result sentinel values: `IPSET_ADD_STORE_PLAIN_TIMEOUT`, `IPSET_ADD_FAILED`, and `IPSET_ADD_START_STORED_TIMEOUT`.

### Control Flow
Bitmap set implementations use these values to constrain accepted ranges and to distinguish add failure from add paths that need to store timeout data. There are no functions in this header.

### State and Persistence
No state is declared. The constants affect in-memory bitmap set behavior in implementation files.

### Dependencies and Integration Points
It includes `uapi/linux/netfilter/ipset/ip_set_bitmap.h` and is consumed by bitmap ipset type implementations.

### Risks
Range-boundary mistakes can cause off-by-one bitmap allocation or element addressing bugs. The negative timeout sentinel must not be confused with normal positive add results.

### Test Signals
Boundary tests around range 0, 1, `0xffff`, and overflow; add tests with timeout-enabled and timeout-disabled bitmap sets; and user/kernel ABI compatibility tests for uapi bitmap attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/ip_set_bitmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/ip_set_getport.h -->
## sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/ip_set_getport.h

### Purpose
This header declares helpers for extracting L4 ports from IPv4/IPv6 packets for ipset match dimensions and defines which protocols carry ports.

### Important APIs, Types, and Functions
It declares `ip_set_get_ip4_port()` and, when IPv6 iptables is enabled, `ip_set_get_ip6_port()`. The fallback IPv6 inline returns `false` when IPv6 support is not built. `ip_set_proto_with_ports()` returns true for TCP, SCTP, UDP, and UDPLITE.

### Control Flow
Callers parse skb protocol state, ask the appropriate helper to extract source or destination port and protocol, and then gate port-dependent matching with `ip_set_proto_with_ports()`. IPv6 builds without `CONFIG_IP6_NF_IPTABLES` short-circuit unsupported extraction.

### State and Persistence
No persistent state is declared. Results are derived from packet headers.

### Dependencies and Integration Points
The header depends on `sk_buff`, basic kernel types, and uapi IP protocol constants. It integrates with ipset hash/list types that include port dimensions and with IPv4/IPv6 netfilter packet parsing.

### Risks
Fragmented, malformed, or non-initial L4 headers can make extraction fail. Build-time IPv6 support changes behavior. Protocols without ports must not be treated as matchable port keys.

### Test Signals
Packet tests for TCP/UDP/SCTP/UDPLITE source and destination ports, fragmented packets, non-port protocols, IPv6-enabled and IPv6-disabled builds, and short skb/header-boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/ip_set_getport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/ip_set_hash.h -->
## sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/ip_set_hash.h

### Purpose
This header supplies default sizing parameters for hash-based ipset implementations.

### Important APIs, Types, and Functions
Constants are `IPSET_DEFAULT_HASHSIZE` 1024, `IPSET_MIMINAL_HASHSIZE` 64, `IPSET_DEFAULT_MAXELEM` 65536, `IPSET_DEFAULT_PROBES` 4, and `IPSET_DEFAULT_RESIZE` 100. The misspelling `MIMINAL` is part of the exposed kernel macro name.

### Control Flow
Hash set implementations use these defaults during create-attribute parsing and resize/probing decisions. There are no functions.

### State and Persistence
No state is declared. The constants shape in-memory hash table allocation and growth.

### Dependencies and Integration Points
It includes the uapi hash ipset header and integrates with hash set type modules.

### Risks
Defaults affect memory consumption and lookup performance. Changing them can alter userspace-visible behavior and stress resize paths. Consumers must preserve the existing macro spelling.

### Test Signals
Create hash sets with omitted and explicit sizing attributes, fill to `maxelem`, trigger collision/probe and resize behavior, and validate memory use under default and minimum hash sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/ip_set_hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/ip_set_list.h -->
## sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/ip_set_list.h

### Purpose
This header supplies size limits for list-based ipset implementations.

### Important APIs, Types, and Functions
It defines `IP_SET_LIST_DEFAULT_SIZE` 8, `IP_SET_LIST_MIN_SIZE` 4, and `IP_SET_LIST_MAX_SIZE` 65536. There are no functions or structs.

### Control Flow
List set create paths use these constants to validate or default requested list capacity.

### State and Persistence
No state is declared. The constants constrain runtime list set storage.

### Dependencies and Integration Points
It includes the uapi list ipset header and is consumed by list set type implementations.

### Risks
Boundary validation must reject under-minimum and over-maximum sizes. Large lists can have lookup and dump costs.

### Test Signals
Create list sets with absent, minimum, below-minimum, maximum, and above-maximum size attributes; test add/delete/list behavior near capacity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/ip_set_list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/pfxlen.h -->
## sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/pfxlen.h

### Purpose
`pfxlen.h` provides prefix-length-to-mask helpers for ipset IPv4 and IPv6 network matching and range-to-CIDR conversion.

### Important APIs, Types, and Functions
It declares `ip_set_netmask_map[]`, `ip_set_hostmask_map[]`, and `ip_set_range_to_cidr()`. Inline helpers are `ip_set_netmask()`, `ip_set_netmask6()`, `ip_set_hostmask()`, `ip_set_hostmask6()`, `ip_set_mask_from_to()`, and `ip6_netmask()`.

### Control Flow
Callers convert a prefix length into network or host masks, apply masks to addresses, and use `ip_set_range_to_cidr()` to represent ranges as CIDR blocks. `ip6_netmask()` applies four 32-bit IPv6 mask words in place.

### State and Persistence
The only state is external constant mask tables. No mutable or durable state is declared.

### Dependencies and Integration Points
It depends on byteorder definitions, `union nf_inet_addr` from netfilter, and TCP/network headers. It integrates with ipset set types that support `net` dimensions or range compression.

### Risks
Prefix length must be validated before indexing tables; otherwise out-of-bounds reads are possible. IPv4 hostmask uses forced host-order conversion, so byte-order mistakes are easy. In-place IPv6 masking mutates the caller's address.

### Test Signals
Validate masks for prefix lengths 0, 1, 31/32, 127/128; test range-to-CIDR edge cases; check IPv4 byte order on little- and big-endian builds; and verify IPv6 in-place masking behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/pfxlen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_amanda.h -->
## sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_amanda.h

### Purpose
This header defines the NAT extension hook used by the AMANDA conntrack helper when it discovers related data connections.

### Important APIs, Types, and Functions
It defines `nf_nat_amanda_hook_fn`, a function type taking an skb, conntrack direction info, protocol offset, match offset/length, and an expectation. It declares the RCU-published hook pointer `nf_nat_amanda_hook`.

### Control Flow
The AMANDA helper parses control traffic, creates or updates an `nf_conntrack_expect`, and calls the NAT hook if present so NAT can rewrite payload and expectation details. Hook lookup must be under RCU in implementation code.

### State and Persistence
Only a global RCU function pointer is declared. Expectations and conntrack state live elsewhere and are in-memory only.

### Dependencies and Integration Points
It depends on netfilter, skb, and conntrack expectation APIs. Integration is between the AMANDA helper and NAT helper module.

### Risks
Payload offsets and lengths must match parsed control data, or NAT rewriting can corrupt packets. Hook lifetime requires RCU discipline. Expectation ownership and NAT updates must remain synchronized.

### Test Signals
AMANDA control-session tests with NAT enabled/disabled, malformed control payloads, module load/unload under traffic, expectation creation, and payload rewrite checksum validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_amanda.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_common.h -->
## sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_common.h

### Purpose
This header provides common conntrack kernel definitions: statistics, pointer tagging masks, the generic conntrack reference object, and lightweight get/put helpers.

### Important APIs, Types, and Functions
`struct ip_conntrack_stat` tracks counters for found, invalid, insert, insert failure, clash resolution, drops, early drops, errors, expectation lifecycle, search restarts, and long chains. `NFCT_INFOMASK` and `NFCT_PTRMASK` reserve low bits in conntrack skb pointers for info tags. `struct nf_conntrack` wraps `refcount_t use`. `nf_conntrack_destroy()` is declared, while `nf_conntrack_put()` and `nf_conntrack_get()` manage references.

### Control Flow
Users increment refs when attaching or sharing conntrack objects. `nf_conntrack_put()` decrements and calls `nf_conntrack_destroy()` when the refcount reaches zero. Pointer masks let skb metadata combine a pointer with small state flags.

### State and Persistence
Conntrack objects and stats are in-memory kernel state. This header does not define durable storage. Refcounts determine object lifetime.

### Dependencies and Integration Points
It depends on `refcount.h` and uapi conntrack common definitions. It integrates with skb conntrack attachment, netfilter conntrack core, and modules that want put/get without depending directly on full conntrack internals.

### Risks
Incorrect masking can corrupt tagged pointers. Refcount leaks or double puts can leak or destroy active conntrack objects. Stats updates need appropriate per-CPU or locking discipline in implementation files.

### Test Signals
Conntrack attach/detach lifetime tests, refcount saturation/debug checks, skb pointer-tag encode/decode tests, namespace teardown, and stat counter validation under connection churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_ftp.h -->
## sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_ftp.h

### Purpose
This header defines FTP conntrack helper state and the NAT hook used when FTP control messages advertise related data connections.

### Important APIs, Types, and Functions
It defines `FTP_PORT` 21, `NF_CT_FTP_SEQ_PICKUP`, `NUM_SEQ_TO_REMEMBER`, and `struct nf_ct_ftp_master`, which stores sequence positions after newlines for each direction and pickup flags useful for conntrackd. `nf_nat_ftp_hook_fn` describes the NAT callback arguments, including FTP command type, protocol offset, match offset/length, and expectation. `nf_nat_ftp_hook` is the RCU-published hook pointer.

### Control Flow
The FTP helper parses control commands, tracks newline sequence positions to find complete commands across packets, creates expectations for data connections, and optionally calls the NAT hook to rewrite addresses/ports in payload and adjust expectations.

### State and Persistence
Per-master helper state is stored in `nf_ct_ftp_master` and lives with the master conntrack entry. NAT hook pointer is global RCU state. No durable persistence is defined.

### Dependencies and Integration Points
It depends on netfilter, skb, conntrack expectations, uapi FTP helper definitions, and tuple direction definitions. It integrates with FTP helper parsing, NAT payload rewriting, and conntrackd sequence pickup.

### Risks
TCP stream segmentation and sequence tracking are subtle; wrong offsets can miss commands or corrupt payload. NAT sequence adjustment must match rewritten lengths. RCU hook access and expectation lifecycle must be correct.

### Test Signals
Active/passive FTP through NAT, commands split across packets, retransmissions, IPv4/IPv6 where supported, conntrackd pickup scenarios, NAT module unload, and checksum/sequence adjustment validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_ftp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_h323.h -->
## sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_h323.h

### Purpose
This header defines H.323 conntrack helper state and the NAT callback table used to rewrite H.225/H.245 transport addresses and install related expectations.

### Important APIs, Types, and Functions
It defines well-known ports `RAS_PORT` 1719 and `Q931_PORT` 1720, plus `H323_RTP_CHANNEL_MAX` 4. `struct nf_ct_h323_master` stores original/NATed signaling ports, RTP ports for media channels, and either RAS timeout or per-direction TPKT lengths. `get_h225_addr()` extracts a transport address from decoded data. `struct nfct_h323_nat_hooks` contains callbacks for setting H.245/H.225/signaling/RAS addresses and NATing RTP/RTCP, T.120, H.245, call forwarding, and Q.931. `nfct_h323_nat_hook` is RCU-published.

### Control Flow
The helper decodes H.323 control payloads using ASN.1 structures, extracts embedded transport addresses, creates expectations for related channels, and calls NAT hooks to rewrite embedded addresses/ports when NAT is active. The master state tracks negotiated ports and split TPKT handling across packet directions.

### State and Persistence
Per-master H.323 helper state lives with conntrack entries. NAT hooks are global RCU state. No durable persistence is defined.

### Dependencies and Integration Points
It depends on netfilter, skb, ASN.1 H.323 type definitions, conntrack expectations, and tuple direction uapi. It integrates H.225/Q.931/RAS/H.245 parsing with NAT rewriting and RTP/RTCP expectation management.

### Risks
H.323 embeds addresses deeply in ASN.1; decoder limits, offsets, and NAT rewrite lengths must be exact. IPv4-only limitations in the ASN.1 decoder affect address support. Split TPKT handling and multiple media channels can create stale or missing expectations. RCU NAT hook lifetime must be observed.

### Test Signals
H.323 call setup through NAT, RAS registration/admission, Q.931 signaling, H.245 tunneled and separate control, fast-start RTP/RTCP channels, T.120, call forwarding, fragmented/split TPKT packets, and NAT hook unload/reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_h323.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_h323_asn1.h -->
## sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_h323_asn1.h

### Purpose
This header declares the compact BER/PER decoder interface used by the H.323 conntrack/NAT helper. It intentionally decodes only the subset of H.225/H.235/H.245 objects needed for NAT and expectation handling.

### Important APIs, Types, and Functions
It defines `Q931`, whose message type enum includes Q.931 signaling messages and whose `UUIE` member is `H323_UserInformation`. Return codes are `H323_ERROR_NONE`, `H323_ERROR_STOP`, `H323_ERROR_BOUND`, and `H323_ERROR_RANGE`. Decode entry points are `DecodeRasMessage()`, `DecodeQ931()`, and `DecodeMultimediaSystemControlMessage()`.

### Control Flow
The H.323 helper passes packet payload buffers and sizes into the decoder. Successful decode populates static C structures from `nf_conntrack_h323_types.h`; stop/range/bound errors tell the helper whether parsing finished early or failed due to bounds/range checks. The decoder avoids allocation and is designed for packet-path use.

### State and Persistence
No persistent state is declared. Decoded objects are caller-provided stack or per-packet structures. The comments state the decoder uses static object descriptions but remains thread-safe and allocation-free.

### Dependencies and Integration Points
It depends on kernel integer types and generated H.323 type definitions. It integrates with H.323 conntrack parsing and NAT rewrite code.

### Risks
The decoder is deliberately incomplete: at most 30 fast-start entries and IPv4-only address support are documented limitations. Boundary and range errors must be treated as untrusted input handling, not normal success. ASN.1 schema drift can break parsing of newer endpoints.

### Test Signals
Decode valid/invalid RAS, Q.931, and H.245 messages; exercise buffer truncation, range violations, maximum fast-start entries, malformed PER lengths, and concurrent decode calls under packet load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_h323_asn1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_h323_types.h -->
## sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_h323_types.h

### Purpose
This generated header defines the reduced H.323/H.225/H.245 ASN.1 object model consumed by the H.323 conntrack decoder and NAT helper. It maps ASN.1 SEQUENCE and CHOICE nodes into C structs, enums, option bitmasks, and fixed-size arrays.

### Important APIs, Types, and Functions
Key address and media types include `TransportAddress`, `TransportAddress_ipAddress`, `H245_TransportAddress`, `UnicastAddress`, `DataProtocolCapability`, `DataApplicationCapability`, `DataType`, `H2250LogicalChannelParameters`, `OpenLogicalChannel`, `OpenLogicalChannelAck`, and `NetworkAccessParameters`. Q.931/H.225 UUIE types include `Setup_UUIE`, `CallProceeding_UUIE`, `Connect_UUIE`, `Alerting_UUIE`, `Facility_UUIE`, `Progress_UUIE`, `H323_UU_PDU`, and `H323_UserInformation`. RAS types include `GatekeeperRequest/Confirm`, `RegistrationRequest/Confirm`, `UnregistrationRequest`, `AdmissionRequest/Confirm`, `LocationRequest/Confirm`, `InfoRequestResponse`, and the top-level `RasMessage`.

### Control Flow
The decoder fills these structures according to ASN.1 choices and option bits. Helper code then checks `choice` discriminants and option masks to find embedded control addresses, media channels, fast-start logical channels, RAS addresses, and time-to-live values. Fixed `SEQUENCE OF` arrays cap fast-start/control entries at 30, H.245 control entries at 4, and some RAS address arrays at 10.

### State and Persistence
The structures are transient decoded representations, not persistent state. Options are represented as high-bit masks in enum values, and choices are represented by enum discriminants plus unions. No allocation or global mutable state is declared.

### Dependencies and Integration Points
It has no external includes beyond its guard and generated typedefs, but it is included by the ASN.1 decoder and H.323 conntrack helper. Its field names and limits must match the generated decoder tables and NAT traversal logic.

### Risks
Because this is generated and reduced, unsupported ASN.1 alternatives are represented only as choices without payloads. Fixed array caps can truncate or reject large messages. There is a duplicate `typedef struct H323_UserInformation` line in the file, which is unusual and should be watched for compiler tolerance. IPv6 address structs use `unsigned int ip/network`, reflecting the decoder's limited support and likely not a complete IPv6 representation. Changing enum order or option bits would break decoder compatibility.

### Test Signals
Compile the H.323 helper with strict warnings, decode representative H.225/Q.931/RAS/H.245 messages, validate fast-start and H.245 control array bounds, test all address-bearing message types used by NAT, and fuzz CHOICE/option combinations to ensure helpers ignore unsupported alternatives safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_h323_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_irc.h -->
## sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_irc.h

### Purpose
This header defines IRC conntrack helper NAT integration for DCC-style related connections.

### Important APIs, Types, and Functions
It defines `IRC_PORT` 6667, `nf_nat_irc_hook_fn`, and the RCU-published hook pointer `nf_nat_irc_hook`. The hook type receives skb, conntrack direction info, protocol offset, match offset/length, and an expectation.

### Control Flow
The IRC helper parses control traffic for embedded connection offers, creates an expectation, and calls the NAT hook when available to rewrite payload and expectation state for NAT traversal.

### State and Persistence
Only the global RCU hook pointer is declared here. Per-connection expectations and helper state live in conntrack structures elsewhere.

### Dependencies and Integration Points
It depends on netfilter, skb, and conntrack expectation APIs. It integrates the IRC helper with NAT rewriting.

### Risks
String parsing offsets must align with skb payload data; malformed or fragmented messages can cause missed expectations. NAT hook lifetime must be protected by RCU, and expectation ownership must match conntrack core rules.

### Test Signals
IRC DCC through NAT, fragmented control messages, malformed payloads, NAT disabled/enabled behavior, module unload under traffic, and checksum/sequence adjustment after payload rewrite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_irc.h -->
