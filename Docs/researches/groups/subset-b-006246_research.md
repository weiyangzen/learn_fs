# Research: subset-b-006246

This grouped report covers the requested netfilter flow-table, logging, lwtunnel, and NAT implementation files. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_core.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_core.c

Purpose: Implements the core `nf_flowtable` lifecycle and software flow cache for nftables flow offload. It allocates `struct flow_offload` objects from conntrack tuples, inserts both directions into an rhashtable, refreshes offload timeouts, reconciles conntrack state on teardown, drives garbage collection, and coordinates optional hardware offload.

Important APIs and functions: `flow_offload_alloc()` captures original/reply tuples and NAT flags from an `nf_conn`; `flow_offload_route_init()` copies route/device/encapsulation metadata from `struct nf_flow_route`; `flow_offload_add()`, `flow_offload_lookup()`, `flow_offload_refresh()`, `flow_offload_teardown()`, and `flow_offload_free()` are the main exported software-cache operations. `nf_flow_table_init()`, `nf_flow_table_free()`, `nf_flow_table_cleanup()`, and `nf_flow_table_gc_run()` own table setup, teardown, device cleanup, and GC. `nf_flow_snat_port()` and `nf_flow_dnat_port()` are shared packet-path NAT port mutators.

Control flow: module init creates the flow slab, registers per-net state/procfs, initializes offload workqueues, and registers BPF flow helpers. A flow is allocated from conntrack, route-filled, inserted twice in the rhashtable, and optionally queued for hardware offload. The delayed GC work iterates only original-direction entries, extends conntrack timeouts for active flows, tears down expired/dying/custom-GC flows, requests hardware delete/stats updates, and finally removes software entries once hardware state is dead.

State and persistence: State is in `flowtables`, each `nf_flowtable` rhashtable, per-flow flags (`NF_FLOW_SNAT`, `NF_FLOW_DNAT`, `NF_FLOW_HW`, `NF_FLOW_CLOSING`, teardown bits), route dst references, and per-net percpu stats. There is no durable persistence; all state is kernel memory tied to module/per-net/table lifetime.

Dependencies and integration: Depends on conntrack tuple/status/timeouts, nftables flowtable types, `rhashtable`, `dst_entry` routing, per-net procfs, and the offload/BPF support implemented by sibling files. Device cleanup is called by netdevice events through exported `nf_flow_table_cleanup()`.

Risks: The high-risk areas are RCU/rhashtable lifetime, dual tuple insertion rollback, dst reference ownership, conntrack timeout reconciliation after bypassing normal conntrack, hardware-offload pending/dead flag ordering, and TCP close/reopen state fixup. Tests should stress bidirectional lookup, NATed TCP/UDP flow expiry, device removal, module unload with pending offload work, and offload stats refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_inet.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_inet.c

Purpose: Registers nftables flowtable types for IPv4, IPv6, and mixed `NFPROTO_INET`, and provides the mixed-family hook dispatcher.

Important APIs and functions: `nf_flow_offload_inet_hook()` decodes the packet L2/encapsulation protocol from `skb->protocol`, VLAN, or PPPoE and dispatches to `nf_flow_offload_ip_hook()` or `nf_flow_offload_ipv6_hook()`. `nf_flow_rule_route_inet()` dispatches hardware rule construction to IPv4 or IPv6 route-action builders. Static `nf_flowtable_type` instances wire `.init`, `.setup`, `.action`, `.free`, and `.hook` into nftables.

Control flow: module init registers IPv4, IPv6, then inet flowtable types; exit unregisters in reverse. Runtime packets enter the configured flowtable hook, protocol detection peels one VLAN/PPPoE classification layer, then the family-specific datapath handles lookup and forwarding.

State and persistence: The file itself stores only static type descriptors. Real table state is allocated by `nf_flow_table_core.c`. No persistent state exists beyond registration lifetime.

Dependencies and integration: Integrates nftables flowtable registration with the family-specific hooks in `nf_flow_table_ip.c`, route rule builders in `nf_flow_table_offload.c`, and table lifecycle helpers in `nf_flow_table_core.c`.

Risks: Misclassification of VLAN/PPPoE packets leads to missed offload rather than packet corruption because unknown protocols return `NF_ACCEPT`. Test signals include module alias loading for AF_INET/AF_INET6/NFPROTO_INET, IPv4/IPv6 dispatch under VLAN and PPPoE, and unregister behavior with active nftables flowtable configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_inet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_ip.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_ip.c

Purpose: Implements the software fast path for IPv4 and IPv6 flowtable forwarding. It parses tuples from incoming packets, validates packet eligibility, applies NAT rewrites, pops and pushes VLAN/PPPoE/IP tunnel encapsulation, updates counters, and transmits by direct L2, neighbour lookup, or xfrm output.

Important APIs and functions: Exported hooks are `nf_flow_offload_ip_hook()` and `nf_flow_offload_ipv6_hook()`. Tuple builders `nf_flow_tuple_ip()` and `nf_flow_tuple_ipv6()` parse TCP/UDP/GRE tuples. `nf_flow_offload_forward()` and `nf_flow_offload_ipv6_forward()` perform common validation, state checks, NAT, TTL/hop-limit decrement, and accounting. Encapsulation helpers include `nf_flow_encap_pop()`, `nf_flow_encap_push()`, `nf_flow_vlan_push()`, `nf_flow_pppoe_push()`, `nf_flow_tunnel_ipip_push()`, and `nf_flow_tunnel_ip6ip6_push()`.

Control flow: A hook builds a context from input device and possible tunnel/encap offset, extracts a tuple, and calls `flow_offload_lookup()`. On a hit, it checks MTU/GSO, TCP FIN/RST/SYN closing state, dst cache validity, and skb writability. It refreshes the flow timeout, removes ingress encapsulation, applies SNAT/DNAT address and port rewrites, decrements TTL/hop-limit, updates conntrack accounting when enabled, and sends the skb through xfrm, neighbour-derived L2, or direct cached L2 addresses. Misses and non-offloadable packets continue through normal netfilter.

State and persistence: Packet-local state lives in `struct nf_flowtable_ctx` and `struct nf_flow_xmit`; persistent flow state is in `struct flow_offload_tuple` fields created by the core/path code. The datapath mutates skb headers and may set flow teardown/closing flags.

Dependencies and integration: Uses conntrack accounting, route/dst/neighbour APIs, GSO segmentation, IPv4/IPv6 tunnel helpers, VLAN/PPPoE helpers, and NAT port helpers exported by core. It is invoked by `nf_flow_table_inet.c` and referenced by nftables flowtable types.

Risks: This is a critical packet mutation path. Risk areas include checksum correctness for NAT, skb linearity/writability, handling of fragments/options/extension headers, tunnel MTU adjustments, GSO segmentation when adding encapsulation, neighbour lifetime, xfrm skb control block setup, and returning `NF_STOLEN` only after ownership transfer. Test signals should cover IPv4/IPv6 TCP and UDP with SNAT/DNAT, VLAN and PPPoE ingress/egress, IPIP/IP6IP6 tunnels, xfrm flows, PMTU/GSO boundaries, TCP FIN/RST teardown, and malformed/truncated packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_ip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_offload.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_offload.c

Purpose: Converts software flowtable entries into TC flower hardware-offload rules and manages asynchronous add, delete, and stats workqueues for offloaded flows.

Important APIs and functions: `nf_flow_rule_route_ipv4()` and `nf_flow_rule_route_ipv6()` build action lists for L2 rewrite, VLAN/PPPoE/tunnel actions, NAT mangles, checksum updates, and redirect. `nf_flow_offload_add()`, `nf_flow_offload_del()`, and `nf_flow_offload_stats()` queue work. `nf_flow_table_offload_setup()` binds or unbinds a flowtable to a netdevice or indirect offload provider. `nf_flow_table_offload_init()` and `_exit()` manage the three workqueues.

Control flow: Rule allocation builds a dissector/match from the flow tuple, including ingress ifindex, VLAN keys, IPv4/IPv6 addresses, L4 protocol, TCP FIN/RST mask, ports, and optional lwt tunnel keys. Route-action builders append decap/encap, Ethernet source/destination mangles, VLAN/PPPoE actions, IP/port NAT mangles, checksum actions for IPv4 NAT, and redirect. Work handlers call driver block callbacks with `FLOW_CLS_REPLACE`, `FLOW_CLS_DESTROY`, or `FLOW_CLS_STATS`, then update conntrack `IPS_HW_OFFLOAD_BIT`, flow timeout, accounting, and flow hardware lifecycle flags.

State and persistence: Persistent state is workqueue pointers, `flowtable->flow_block`, block callback lists protected by `flow_block_lock`, per-flow hardware flags, and transient `struct flow_offload_work`. There is no durable persistence.

Dependencies and integration: Integrates with TC flower (`TC_SETUP_CLSFLOWER`, `TC_SETUP_FT`), netdevice `ndo_setup_tc`, indirect flow block offload, lwtunnel metadata, conntrack accounting, and the core GC state machine. If software hardware offload is disabled, setup falls back to XDP mapping.

Risks: Hardware rule parity with software forwarding is subtle. Risks include action array overflow (`NF_FLOW_RULE_ACTION_MAX`), leaking dev references held by redirect actions, stale neighbour MACs, bidirectional flag differences, races around `NF_FLOW_HW_PENDING`, stats double-accounting, and cleanup of indirect block callbacks. Tests should bind/unbind devices, exercise driver failure paths, compare software and hardware NAT/VLAN/tunnel behavior, and unload with pending add/delete/stats work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_path.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_path.c

Purpose: Builds `struct nf_flow_route` metadata from nftables packet context, conntrack tuples, routes, neighbours, and netdevice forwarding paths so flows can be installed into the software and hardware flowtable paths.

Important APIs and functions: Exported `nft_flow_route()` computes both directions. `nft_default_forward_path()` initializes dst and xmit type. `nft_dev_fill_forward_path()` validates Ethernet devices and neighbour reachability before calling `dev_fill_forward_path()`. `nft_dev_path_info()` converts path-stack entries into ingress device, output device, encapsulation, tunnel, MAC, and GSO metadata. `nft_flow_tunnel_update_route()` resolves tunnel routes.

Control flow: `nft_flow_route()` holds the current skb dst, routes the opposite direction from conntrack tuple data, initializes both route tuples, then tries to refine neighbour xmit paths into direct L2 forwarding where the discovered ingress device is present in the nft flowtable hook list. Bridge, VLAN, PPPoE, DSA, and tunnel path entries are interpreted into route metadata consumed by core/datapath/offload code.

State and persistence: The file populates caller-provided `nf_flow_route`; it does not own long-lived state. It does take dst references that are later transferred and released by flow allocation/free.

Dependencies and integration: Depends on nftables packet info and hook lists, conntrack tuples, `nf_route()`, neighbour state, `dev_fill_forward_path()`, bridge/VLAN/PPPoE path descriptors, and flowtable hardware-offload flags.

Risks: Bad route metadata can send fast-path packets to the wrong device or with wrong encapsulation. Important risks include neighbour validity races, dst reference ownership, direct forwarding only when flowtable hooks cover the discovered ingress device, bridge VLAN pop/push accounting, single-tunnel limitation, and preserving GSO segmentation needs for PPPoE. Test signals include routed, bridged, VLAN-stacked, PPPoE, DSA, tunnel, and xfrm paths with device removal and neighbour invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_procfs.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_procfs.c

Purpose: Exposes per-CPU flowtable workqueue counters through `/proc/net/stat/nf_flowtable` for each network namespace.

Important APIs and functions: `nf_flow_table_init_proc()` creates the proc entry using `proc_create_net()`. `nf_flow_table_fini_proc()` removes it. The seq operations iterate possible CPUs and print `count_wq_add`, `count_wq_del`, and `count_wq_stats` from `net->ft.stat`.

Control flow: The seq start function emits a header at position zero, then advances through `cpu_possible()` CPUs. `show` formats one row per CPU. Per-net init in core allocates the percpu stats before creating the proc entry.

State and persistence: Reads percpu `struct nf_flow_table_stat` in the target net namespace. No persistent state is stored in this file.

Dependencies and integration: Integrated by `nf_flow_table_core.c` pernet init/exit and incremented/decremented by `nf_flow_table_offload.c` workqueue scheduling/completion.

Risks: Main risks are proc entry lifecycle ordering relative to percpu allocation/free and counter consistency under concurrent updates. Test signals include reading the proc file with and without hardware-offload work, network namespace create/destroy, and CPU hotplug scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_procfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_xdp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_xdp.c

Purpose: Maintains an RCU-protected mapping from net devices to flowtables for XDP/non-hardware-offload flowtable setup.

Important APIs and functions: `nf_flowtable_by_dev()` returns the first flowtable associated with a device under caller-held RCU read lock. `nf_flowtable_by_dev_insert()` adds a flowtable element to the per-device list, creating the hashtable node if needed. `nf_flowtable_by_dev_remove()` removes a flowtable association and frees empty device nodes after `synchronize_rcu()`. `nf_flow_offload_xdp_setup()` handles bind/unbind commands.

Control flow: Setup bind inserts `(dev -> flowtable)` under `nf_xdp_hashtable_lock`; unbind removes matching list entries and tears down an empty bucket node after readers quiesce. Lookup hashes the device pointer and returns the first registered flowtable.

State and persistence: State is an in-memory hashtable keyed by `struct net_device *` address and lists of `struct flow_offload_xdp_ft`. It is not persisted.

Dependencies and integration: Called from `nf_flow_table_offload_setup()` when hardware offload is not enabled. XDP users call `nf_flowtable_by_dev()` to locate the flowtable for a device.

Risks: The mapping assumes a device should belong to a single flowtable but stores a list and returns the first element, so duplicate binds can be surprising. Other risks are pointer-key lifetime, RCU list deletion, memory allocation failure during bind, and ensuring unbind is called before device memory reuse. Test signals include bind/unbind, duplicate bind ordering, concurrent lookup/removal, and netdevice teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_xdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_hooks_lwtunnel.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_hooks_lwtunnel.c

Purpose: Provides sysctl-controlled enablement for netfilter hooks in lightweight tunnel paths.

Important APIs and functions: `nf_hooks_lwtunnel_sysctl_handler()` reads or writes the `nf_hooks_lwtunnel` sysctl. Internal helpers `nf_hooks_lwtunnel_get()` and `nf_hooks_lwtunnel_set()` access the static key `nf_hooks_lwtunnel_enabled`. `netfilter_lwtunnel_init()` and `netfilter_lwtunnel_fini()` register/unregister per-net sysctl tables when `CONFIG_SYSCTL` is enabled.

Control flow: Reads report whether the static key is active. Writes pass through `proc_dointvec_minmax()` with 0/1 bounds. Enabling turns on the static branch; disabling after enable returns `-EBUSY`, making the feature effectively one-way for the boot/module lifetime.

State and persistence: State is the global static branch plus per-net sysctl table registrations. There is no durable persistence.

Dependencies and integration: Depends on `CONFIG_LWTUNNEL`, `CONFIG_SYSCTL`, static key declared in lwtunnel headers, and `net->nf.nf_lwtnl_dir_header` storage. Prototypes are exposed via `nf_internals.h`.

Risks: The one-way enable behavior must be visible to userspace; tests should assert that enabling succeeds, disabling after enable fails with `EBUSY`, per-net sysctl tables allocate/free correctly, and builds without sysctl return no-op init/fini.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_hooks_lwtunnel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_internals.h -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_internals.h

Purpose: Internal netfilter header collecting private cross-file declarations and conntrack netlink tuple-filter bit definitions used inside `net/netfilter`.

Important APIs and types: Defines `CTA_FILTER_F_*` bitmasks and `CTA_FILTER_FLAG()` for conntrack netlink filtering. Declares `nf_queue_nf_hook_drop()`, `netfilter_log_init()`, optional lwtunnel init/fini, and raw hook-entry insert/delete helpers.

Control flow: Header-only declarations; no runtime control flow.

State and persistence: No state. Constants encode filter bit layout that must remain consistent with users of conntrack netlink attributes.

Dependencies and integration: Included by `nf_log.c`, `nf_hooks_lwtunnel.c`, `nf_nat_core.c`, and other internal netfilter compilation units needing non-public symbols. It bridges core hook manipulation and subsystem initialization without exposing these helpers as public UAPI.

Risks: Since it is internal, mismatches between declarations and implementation prototypes are build-time failures. Semantic risk is accidental reuse or renumbering of filter flags. Test signals are allmodconfig-style builds with and without `CONFIG_LWTUNNEL`, and conntrack netlink filter tests covering every declared flag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_internals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_log.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_log.c

Purpose: Implements the generic netfilter logger registry, per-net logger selection, proc/sysctl controls, and shared bounded log-buffer helpers used by concrete logger modules.

Important APIs and functions: Registry operations are `nf_log_register()`, `nf_log_unregister()`, `nf_log_is_registered()`, `nf_logger_find_get()`, and `nf_logger_put()`. Per-net selection uses `nf_log_set()`, `nf_log_unset()`, `nf_log_bind_pf()`, and `nf_log_unbind_pf()`. Packet emission goes through `nf_log_packet()` or `nf_log_trace()`. Buffer helpers are `nf_log_buf_open()`, `nf_log_buf_add()`, and `nf_log_buf_close()`. `netfilter_log_init()` registers per-net proc/sysctl setup.

Control flow: Logger providers register a `struct nf_logger` per protocol family/type. Packet logging selects either an explicit logger type from `loginfo` or the per-net bound logger, formats the prefix, and calls the provider callback under RCU. Procfs iterates per-family logger bindings. Sysctl write accepts a logger name or `NONE` and updates the per-net RCU pointer.

State and persistence: Global state is `loggers[NFPROTO_NUMPROTO][NF_LOG_TYPE_MAX]`, protected by `nf_log_mutex` and read under RCU, plus `sysctl_nf_log_all_netns`. Per-net state lives in `net->nf.nf_loggers[]` and sysctl/proc headers. The emergency log buffer is a singleton fallback when allocation fails.

Dependencies and integration: Concrete loggers such as `nf_log_syslog.c` register here. nftables/iptables logging targets call `nf_log_packet()` or module-get helpers. Per-net lifecycle uses procfs and sysctl infrastructure.

Risks: Risks include RCU pointer lifetime, module refcount races, emergency buffer use with bottom halves disabled, sysctl table duplication/free for non-init netns, prefix truncation, and global `nf_log_all_netns` exposure. Tests should cover logger registration conflicts, namespace-specific binding, module unload while logging, proc/sysctl read/write, allocation failure fallback, and trace logging without explicit `loginfo`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_log_syslog.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_log_syslog.c

Purpose: Provides the built-in syslog-style netfilter packet logger implementations for ARP, IPv4, IPv6, bridge, and netdev families.

Important APIs and functions: Static logger callbacks include `nf_log_arp_packet()`, `nf_log_ip_packet()`, `nf_log_ip6_packet()`, `nf_log_netdev_packet()`, and `nf_log_unknown_packet()`. Header renderers include `dump_arp_packet()`, `dump_ipv4_packet()`, `dump_ipv6_packet()`, `nf_log_dump_tcp_header()`, `nf_log_dump_udp_header()`, `dump_mac_header()`, and `nf_log_dump_packet_common()`. Module init registers loggers globally and binds them as defaults per net namespace.

Control flow: On log callback, the module rejects non-init-net logs unless `sysctl_nf_log_all_netns` allows them, opens an `nf_log_buf`, emits common IN/OUT/bridge physical device fields, decodes MAC/VLAN when requested, then decodes family-specific headers and L4 fields. IPv4 and IPv6 ICMP error logging recurses once into the embedded packet. Init registers pernet defaults first, then global logger providers; exit unregisters both.

State and persistence: Stores static `nf_logger` descriptors and default loginfo. Per-net default bindings are maintained through `nf_log_set()`/`nf_log_unset()`. Output is transient kernel log text.

Dependencies and integration: Uses the generic logger core, xt_LOG log flags, skb header accessors, bridge netfilter physical device helpers, IPv4/IPv6/ARP/TCP/UDP/ICMP parsers, and syslog printk output from `nf_log_buf_close()`.

Risks: Packet parsing must tolerate truncation and fragments without reading past skb data. Other risks include log flooding from namespaces, recursive ICMP decode bounds, IPv6 extension header loops/truncation, UID/GID lookup under RCU, MAC header assumptions for tunnel devices, and fixed log buffer size truncation. Test signals include LOG target output for ARP/IPv4/IPv6/netdev/bridge, fragments, malformed short packets, TCP options, IPv6 extension headers, ICMP embedded packets, UID logging, VLAN tags, and namespace sysctl gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_log_syslog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_amanda.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_amanda.c

Purpose: NAT helper for the Amanda backup conntrack helper. It rewrites embedded dynamic port text in UDP control packets and sets expectations so related TCP data connections follow the master NAT mapping.

Important APIs and functions: `help()` is installed through the RCU hook `nf_nat_amanda_hook` and registered via `struct nf_conntrack_nat_helper`. It uses `nf_nat_exp_find_port()`, `nf_nat_mangle_udp_packet()`, and `nf_nat_follow_master()`.

Control flow: When the conntrack Amanda helper detects a port field, NAT helper saves the original expected TCP port, forces the expected connection direction to original, sets `expectfn`, finds an available port, rewrites the decimal port string inside the UDP payload, and accepts. On port exhaustion or mangle failure it logs through conntrack helper facilities, unexpects as needed, and drops.

State and persistence: Static helper registration and an RCU function pointer are the only module state. Expectations live in conntrack.

Dependencies and integration: Depends on Amanda conntrack parser, generic NAT helper mangle functions, conntrack expectations, and NAT follow-master setup.

Risks: Risks are payload offset correctness, UDP length/checksum recalculation, expectation cleanup on failure, and decimal buffer sizing. Test signals should include Amanda control messages with same-port and remapped-port expectations, port exhaustion, checksum verification, and module unload synchronization with RCU hook users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_amanda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_bpf.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_bpf.c

Purpose: Exposes an unstable BPF kfunc allowing XDP and TC-BPF conntrack allocation paths to attach initial NAT source or destination mapping information before conntrack insertion.

Important APIs and functions: `bpf_ct_set_nat_info()` validates IPv4/IPv6 conntrack objects, builds an `nf_nat_range2` from address and optional positive port, and calls `nf_nat_setup_info()`. `register_nf_nat_bpf()` registers the BTF kfunc ID set for `BPF_PROG_TYPE_XDP` and `BPF_PROG_TYPE_SCHED_CLS`.

Control flow: A BPF program obtains a referenced `nf_conn___init`, calls the kfunc with address/port/manip type, and the kernel initializes NAT state on the unconfirmed conntrack. Registration occurs from NAT core init.

State and persistence: No local runtime state beyond static BTF kfunc descriptors. NAT state is stored in the conntrack extension/status.

Dependencies and integration: Depends on conntrack BPF allocation types, BTF kfunc registration, NAT core, and the fact that the object is not yet confirmed.

Risks: The interface is explicitly unstable, but kernel safety still depends on BTF type restrictions, unconfirmed conntrack state, family validation, and port byte-order handling. Test signals include verifier-accepted XDP/SCHED_CLS programs setting source and destination NAT, invalid family rejection, random-port behavior for non-positive ports, and failure when NAT setup returns drop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_core.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_core.c

Purpose: Core NAT engine for conntrack-backed tuple mapping. It selects unique NAT tuples, stores NAT state in conntrack, maintains a by-source mapping hash, registers per-net NAT hook indirection, supports ctnetlink/BPF/session decode integration, and cleans NAT state on module removal.

Important APIs and functions: `nf_ct_nat_ext_add()`, `nf_nat_setup_info()`, `nf_nat_alloc_null_binding()`, `nf_nat_packet()`, and `nf_nat_inet_fn()` are central exported entry points. Tuple selection is handled by `get_unique_tuple()`, `find_appropriate_src()`, `find_best_ips_proto()`, and `nf_nat_l4proto_unique_tuple()`. Collision handling uses `nf_nat_used_tuple_new()` and `nf_nat_used_tuple_harder()`. Hook registration is via `nf_nat_register_fn()` and `nf_nat_unregister_fn()`.

Control flow: NAT setup is allowed only on unconfirmed conntracks. It inverts the reply tuple into the current forward tuple, selects a unique mapped tuple within the requested range, alters the reply tuple, sets NAT status bits, adds seqadj when helpers need payload-size adjustment, and inserts source mappings into `nf_nat_bysource`. At packet time, `nf_nat_inet_fn()` initializes NAT through registered NAT rule hooks or null binding for new/related flows, then calls `nf_nat_packet()` to apply manipulation. Register functions lazily create per-family hook arrays whose private entries point to user NAT hooks.

State and persistence: Global state includes `nf_nat_bysource`, hash size/random key, per-bucket locks, NAT proto mutex, and RCU `nf_nat_hook`. Per-net state stores NAT hook arrays and users. Conntrack stores NAT extension, reply tuple, status bits, bysource node, and optional seqadj. No durable persistence exists.

Dependencies and integration: Integrates deeply with conntrack core, zones, helper expectations, netfilter hook infrastructure, ctnetlink NAT attribute parsing, xfrm session decode, BPF NAT kfunc registration, and protocol packet manipulation in `nf_nat_proto.c`.

Risks: Major risks are tuple collision races, source-map hash lifetime, offloaded/time-wait connection eviction, NAT setup after confirmation, hook indirection RCU lifetime, null-binding cleanup on module unload, range randomization/offset correctness, and sequence-adjust extension allocation. Test signals include high-concurrency tuple allocation, port range exhaustion, persistent/random/offset ranges, zones, helper seqadj, ctnetlink-created NAT, unregister while hooks are active, module unload cleanup, and xfrm decode after NAT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_ftp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_ftp.c

Purpose: NAT helper for FTP control channels. It rewrites PORT/PASV/EPRT/EPSV address and port payloads and sets conntrack expectations for related FTP data channels.

Important APIs and functions: `nf_nat_ftp()` is installed in `nf_nat_ftp_hook`. `nf_nat_ftp_fmt_cmd()` formats replacement payloads for classic IPv4 comma syntax, EPRT IPv4/IPv6, and EPSV. The helper uses `nf_nat_exp_find_port()`, `nf_nat_mangle_tcp_packet()`, and `nf_nat_follow_master()`.

Control flow: Given a parsed FTP command/reply span and expectation, it chooses the address from the packet destination in the opposite direction, saves the expected port, sets expectation direction and follow-master callback, tries to reserve a port, formats the replacement command, rewrites the TCP payload with sequence adjustment, and accepts. On failure it logs, removes the expectation, and drops.

State and persistence: Static NAT helper registration plus the RCU hook pointer. A legacy `ports` module parameter only emits an informational warning.

Dependencies and integration: Depends on FTP conntrack parsing, generic NAT helper payload mangle/seqadj, conntrack expectation handling, and NAT core.

Risks: Risks include replacement size and sequence adjustment correctness, IPv6 EPRT formatting, expectation direction for active/passive modes, helper cleanup on mangle failure, and preserving compatibility with legacy module parameters. Test signals include active FTP PORT, passive PASV/EPSV, EPRT for IPv4/IPv6, altered port allocation, checksum/seqadj validation, and unload under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_ftp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_helper.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_helper.c

Purpose: Provides generic NAT helper support for payload rewriting, TCP sequence adjustment, UDP length/checksum update, follow-master expectation NAT setup, and expectation port reservation.

Important APIs and functions: `__nf_nat_mangle_tcp_packet()` rewrites TCP payload spans and optionally records sequence adjustment. `nf_nat_mangle_udp_packet()` rewrites UDP payload spans and updates UDP length/checksum. `nf_nat_follow_master()` configures related conntracks to use the master flow's NAT mapping. `nf_nat_exp_find_port()` tries to register an expectation at a requested or random replacement port.

Control flow: Payload mangle first ensures the skb is writable and expandable, then `mangle_contents()` memmoves trailing data, inserts replacement bytes, adjusts skb length and IP/IPv6 total length, recalculates transport checksums, and optionally records seqadj. Follow-master sets source mapping to the master's opposite destination and destination mapping to the master's opposite source plus saved protocol port. Port finding repeatedly calls `nf_ct_expect_related()` until success or bounded attempts fail.

State and persistence: No local persistent state. It mutates skb contents and conntrack expectation/NAT/seqadj state.

Dependencies and integration: Used by protocol-specific helpers such as FTP, IRC, and Amanda. Depends on skb mutation APIs, conntrack helpers/expectations, NAT core, and seqadj extension support.

Risks: High-risk behavior includes packet expansion under GFP_ATOMIC, memmove bounds, IPv4/IPv6 length recalculation, checksum correctness after payload size changes, TCP sequence adjustment alignment, and expectation cleanup by callers. Tests should exercise larger/smaller/same-size replacements, no-tailroom expansion, IPv4/IPv6 TCP and UDP checksums, seqadj across subsequent packets, and port collision exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_irc.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_irc.c

Purpose: NAT helper for IRC DCC messages. It rewrites embedded IPv4 address and port text in IRC control traffic and sets expectations for related DCC connections.

Important APIs and functions: `help()` is installed via `nf_nat_irc_hook`, uses `nf_nat_exp_find_port()`, formats `"<addr_as_u32> <port>"`, calls `nf_nat_mangle_tcp_packet()`, and sets `nf_nat_follow_master()` as the expectation callback.

Control flow: The helper uses the reply-direction destination address as the externally visible address, saves the expected TCP port, forces expectation direction to reply, reserves a port, rewrites the matched DCC payload span, and accepts. On port or mangle failure it logs, unexpects if needed, and drops.

State and persistence: Static NAT helper registration, RCU hook pointer, and a warning-only legacy `ports` module parameter. Expectations live in conntrack.

Dependencies and integration: Depends on IRC conntrack parser, TCP payload mangle/seqadj helper, conntrack expectations, and NAT core.

Risks: The helper only handles IPv4 numeric DCC address syntax, so parser/helper alignment is important. Other risks are payload buffer sizing, sequence adjustment after replacement, expectation direction, and RCU hook teardown. Test signals include DCC CHAT/SEND variants, changed port allocation, port exhaustion, checksum/seqadj validation, and module unload while parser references the hook.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_irc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_masquerade.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_masquerade.c

Purpose: Implements IPv4/IPv6 MASQUERADE source NAT and notifier-driven cleanup of conntracks bound to disappearing devices or addresses.

Important APIs and functions: `nf_nat_masquerade_ipv4()` and `nf_nat_masquerade_ipv6()` select the outgoing interface source address and call `nf_nat_setup_info()`. `nf_nat_masquerade_inet_register_notifiers()` and `_unregister_notifiers()` manage shared notifier registration. Cleanup scheduling uses `nf_nat_masq_schedule()`, `iterate_cleanup_work()`, `device_cmp()`, and `inet_cmp()`.

Control flow: For new/related postrouting packets, IPv4 selects a source address with `inet_select_addr()` and IPv6 with `ipv6_dev_get_saddr()`, records `masq_index` in the NAT extension when available, builds a range with `NF_NAT_RANGE_MAP_IPS`, and delegates setup to NAT core. Device-down or address-removal notifier callbacks schedule bounded background work to iterate conntrack and remove entries matching the interface or address.

State and persistence: Global state includes notifier refcount under `masq_mutex`, atomic worker count, and static notifier blocks. Per-conntrack state stores `nat->masq_index`. Work items hold netns references and optional address filters.

Dependencies and integration: Used by nftables/iptables masquerade expressions. Depends on NAT core, conntrack cleanup iterator, netdevice and inet/inet6 address notifier chains, and per-net lifetime tracking.

Risks: Risks include worker storms from address churn, skipped cleanup when allocation/module ref fails, refcount underflow/overflow, netns lifetime, IPv4 zero-source special case, address selection failure, and cleanup matching reply tuple destination. Test signals include IPv4 and IPv6 masquerade, device down flush, individual address removal, many concurrent notifier events, namespace teardown, and notifier register/unregister nesting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_masquerade.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_ovs.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_ovs.c

Purpose: Provides NAT execution support for Open vSwitch and TC conntrack action paths outside the normal netfilter hook traversal.

Important APIs and functions: Exported `nf_ct_nat()` applies requested or existing NAT to an skb/conntrack and returns the performed manipulations in `action`. Internal `nf_ct_nat_execute()` mirrors IPv4/IPv6 NAT hook logic, including ICMP/ICMPv6 related reply translation and new-flow NAT initialization.

Control flow: `nf_ct_nat()` ensures a NAT extension exists for unconfirmed conntracks, determines the manipulation type from existing NAT status or requested action bits, then calls `nf_ct_nat_execute()`. For related ICMP errors it calls the protocol-specific reply translators. For new flows it initializes NAT from `range` or null binding. It then calls `nf_nat_packet()` and may apply both source and destination NAT when status bits require it.

State and persistence: No local state. It mutates conntrack NAT extension/status and skb headers, and reports action bits to the caller.

Dependencies and integration: Used by OVS and TC conntrack code. Depends on skb protocol helpers, NAT core, NAT protocol translation functions, and conntrack status/confirmation state.

Risks: Because it emulates hook-specific behavior, hooknum/maniptype mapping must stay aligned with `HOOK2MANIP()`. Risks include double NAT ordering, related ICMP handling, unconfirmed extension allocation failure, action bit reporting, and `commit` semantics for related flows. Test signals include OVS/TC ct NAT for new and established flows, combined SNAT+DNAT, ICMP/ICMPv6 errors, VLAN protocol skb detection, and non-commit related behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_ovs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_proto.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_proto.c

Purpose: Implements packet-header manipulation for NAT across IPv4, IPv6, TCP, UDP, SCTP, ICMP, ICMPv6, and GRE, plus family-specific NAT hook wrappers and registration helpers.

Important APIs and functions: `nf_nat_manip_pkt()` is the core exported manipulator used by NAT core. `nf_nat_csum_recalc()` supports helper payload rewrites. `nf_nat_icmp_reply_translation()` and `nf_nat_icmpv6_reply_translation()` translate outer and embedded packets in related error messages. Exported registration helpers are `nf_nat_ipv4_register_fn()`, `nf_nat_ipv4_unregister_fn()`, `nf_nat_ipv6_register_fn()`, `nf_nat_ipv6_unregister_fn()`, and inet variants when enabled.

Control flow: Protocol-specific functions ensure skb writability, update address/port/id fields, and adjust checksums. `nf_nat_manip_pkt()` inverts the opposite conntrack tuple to produce the target tuple and dispatches to IPv4 or IPv6 manipulation. IPv4 and IPv6 hook wrappers handle related ICMP errors before calling `nf_nat_inet_fn()`, drop stale dst after DNAT, reroute local output when destination changes, orphan early-demux sockets when local-in source/port changes, and redo xfrm lookup when NAT changes flow keys.

State and persistence: The file has static hook operation arrays for IPv4 and IPv6. Runtime state is in conntrack and skb headers; no local mutable persistent data.

Dependencies and integration: Called by `nf_nat_core.c`, OVS/TC NAT support, helpers needing checksum recalculation, and family NAT registration paths. Depends on conntrack tuples, IPv4/IPv6 routing, xfrm, checksum APIs, SCTP checksum support, GRE/PPTP types, and netfilter hook priorities.

Risks: This is a high-risk packet rewrite layer. Risks include checksum correctness for partial and complete checksums, inner ICMP translation bounds, IPv6 extension header parsing, fragments with unavailable L4 headers, GRE version behavior, SCTP checksum recomputation, route/xfrm refresh after NAT, socket early-demux invalidation, and family registration mismatches. Test signals include every supported L4 protocol, IPv4/IPv6 SNAT/DNAT in each hook, ICMP error translation, fragmented IPv6, local output reroute, xfrm policy lookup after NAT, and helper-driven checksum recalculation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_proto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_redirect.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_redirect.c

Purpose: Implements REDIRECT destination NAT for IPv4 and IPv6 by mapping packets to a local address on the receiving interface or loopback for locally generated packets.

Important APIs and functions: Internal `nf_nat_redirect()` builds a destination NAT range around a selected address and calls `nf_nat_setup_info()`. Exported `nf_nat_redirect_ipv4()` selects loopback for local-out or the first IPv4 address on the ingress device for prerouting. Exported `nf_nat_redirect_ipv6()` selects loopback for local-out or a usable scoped IPv6 address on the ingress device. `nf_nat_redirect_ipv6_usable()` filters tentative, mapped, and wrong-scope addresses.

Control flow: The public helpers assert valid hook numbers, choose `newdst`, return `NF_DROP` if no usable ingress address exists, then delegate to generic NAT setup with `NF_NAT_MANIP_DST` while preserving original protocol range constraints.

State and persistence: No local mutable state except the static IPv6 loopback constant. NAT state is stored in conntrack by NAT core.

Dependencies and integration: Used by redirect targets/expressions. Depends on RCU inet device access, IPv6 address device locking, address scope helpers, and NAT core.

Risks: Address selection is intentionally simple and can drop when an interface has no usable address. Risks include IPv6 tentative/optimistic handling, scope filtering, RCU/locking around interface address lists, and preserving port range flags. Test signals include local-out and prerouting redirect for IPv4/IPv6, no-address drop, tentative IPv6 address filtering, link-local/global scope matching, and port-preserving redirects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_redirect.c -->
