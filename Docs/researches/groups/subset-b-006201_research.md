# Research: subset-b-006201

Grouped worker report for IPv4 multicast routing, route metrics, IPv4 netfilter glue, and selected legacy iptables/arptables modules under `sources/distributed-fs/ceph-client/net/ipv4`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ipmr.c -->
# sources/distributed-fs/ceph-client/net/ipv4/ipmr.c

## Purpose
`ipmr.c` implements IPv4 multicast routing (`RTNL_FAMILY_IPMR`): multicast routing table creation, VIF lifecycle, multicast forwarding cache (MFC) insertion/deletion, unresolved cache upcalls to a routing daemon, PIM register handling, rtnetlink/proc observability, and packet forwarding from `ip_mr_input()` and `ip_mr_output()`.

## Important APIs, Types, And Functions
Core exported entry points are `ip_mr_init()`, `ip_mroute_setsockopt()`, `ip_mroute_getsockopt()`, `ipmr_ioctl()`, `ip_mr_input()`, `ip_mr_output()`, `ipmr_get_route()`, and compat ioctl helpers. The central state is `struct mr_table`, `struct vif_device`, and IPv4-specific `struct mfc_cache`, backed by an rhashtable keyed by `(origin, multicast group)`. Multiple-table builds add `fib_rules_ops` via `ipmr_rule_*()`, while single-table builds store `net->ipv4.mrt`. VIF management is in `vif_add()` and `vif_delete()`. MFC management is in `ipmr_mfc_add()`, `ipmr_mfc_delete()`, `ipmr_cache_unresolved()`, `ipmr_cache_resolve()`, and `mroute_clean_tables()`.

## Control Flow
Initialization allocates the `mfc_cache` slab, registers per-net state, netdevice notifier, optional PIM protocol handler, and rtnetlink handlers. Userspace opens a raw IGMP socket and drives `MRT_INIT`, VIF, MFC, PIM, assert, flush, and table options through `ip_mroute_setsockopt()`. Packet input looks up the multicast table with route rules, finds exact or wildcard MFC entries, queues unresolved packets for daemon upcall when needed, and otherwise fans packets out through VIFs with TTL thresholds and netfilter forward hooks. Local multicast output uses the same cache model when `IPSKB_MCROUTE` is set, otherwise falls back to normal multicast output.

## State And Persistence
State is per network namespace and in-memory only: `mr_table` lists/rhashtables, VIF array, unresolved queue, route socket pointer, PIM flags, counters, timers, notifier seq, and optional fib rules. Resolved entries are RCU/list/rhashtable managed; unresolved entries are protected by `mfc_unres_lock` and expire after roughly 10 seconds. Device references use RCU plus netdevice trackers; dynamically created tunnel/register netdevices are queued for unregister on cleanup.

## Dependencies And Integration Points
The file integrates raw socket router-alert delivery, rtnetlink route/link operations, fib rules, netdevice unregister notifiers, procfs files `ip_mr_vif` and `ip_mr_cache`, PIM v1/v2 protocol handlers, tunnel devices, netconf notifications, netfilter forward hooks, switchdev offload marks, and shared multicast helpers from `ipmr_base.c`.

## Risks
Major risks are concurrency and lifetime mistakes across RCU, RTNL, `mrt_lock`, `mfc_mutex`, and `mfc_unres_lock`; incorrect unresolved queue accounting; stale device pointers; malformed netlink validation; under/over-forwarding wildcard `(*,G)` or `(*,*)` entries; and subtle routing loops around wrong-IIF asserts, register VIFs, tunnel encapsulation, and local-output multicast routing.

## Test Signals
Useful tests include `MRT_*` socket option permission and length checks, VIF add/delete on normal, tunnel, and register VIFs, MFC add/delete/replace/proxy behavior, unresolved queue timeout and netlink error delivery, PIM register receive paths, `ip route get`/dump for `RTNL_FAMILY_IPMR`, procfs output, namespace teardown, device unregister cleanup, multicast forwarding counters, wrong-IIF assert generation, and netfilter hook interaction during forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ipmr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ipmr_base.c -->
# sources/distributed-fs/ceph-client/net/ipv4/ipmr_base.c

## Purpose
`ipmr_base.c` contains multicast-routing helpers shared by IPv4 `ipmr` and IPv6 `ip6mr`: VIF initialization, multicast routing table allocation/freeing, generic MFC lookup helpers, proc sequence traversal, rtnetlink route dump formatting, and fib notifier dump helpers.

## Important APIs, Types, And Functions
Key APIs are `vif_device_init()`, `mr_table_alloc()`, `mr_table_free()`, `mr_mfc_find_parent()`, `mr_mfc_find_any_parent()`, `mr_mfc_find_any()`, `mr_fill_mroute()`, `mr_table_dump()`, `mr_rtm_dumproute()`, and `mr_dump()`. Proc builds also export `mr_vif_seq_idx()`, `mr_vif_seq_next()`, `mr_mfc_seq_idx()`, and `mr_mfc_seq_next()`.

## Control Flow
Protocol-specific code allocates an `mr_table` with hash parameters, an expiration timer callback, and a table insertion callback. MFC lookup helpers search the protocol-supplied rhltable and apply parent/VIF wildcard semantics. Dump helpers walk resolved lists under RCU and unresolved lists under the caller-supplied spinlock, invoking a protocol-specific route-fill callback.

## State And Persistence
The file owns no persistent global state. It initializes fields inside `struct mr_table` and `struct vif_device`, queues table destruction through `queue_rcu_work()`, and reads per-MFC counters, TTL arrays, flags, and last-use timestamps when producing rtnetlink data.

## Dependencies And Integration Points
It depends on `linux/mroute_base.h`, rhashtable/rhltable APIs, RCU workqueues, seq_file, rtnetlink attributes, and fib notifier callbacks. IPv4 and IPv6 provide the address-specific key, fill, iteration, and locking pieces.

## Risks
Risks include lock imbalance in sequence traversal when switching from resolved to unresolved lists, incorrect dump cursor updates across multipart netlink dumps, stale VIF device pointers, and mismatch between protocol-specific rhashtable compare keys and generic lookup helpers.

## Test Signals
Tests should cover table allocation failure and cleanup, wildcard parent lookup semantics, route dump filtering by device and route type, unresolved-entry dump flags, proc iteration over empty and mixed resolved/unresolved tables, and fib notifier dumps containing VIF and MFC entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ipmr_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/metrics.c -->
# sources/distributed-fs/ceph-client/net/ipv4/metrics.c

## Purpose
`metrics.c` parses and allocates IPv4 FIB destination metrics from netlink route attributes, converting user-provided `RTAX_*` values into a refcounted `struct dst_metrics`.

## Important APIs, Types, And Functions
The internal parser is `ip_metrics_convert()`. The exported allocator is `ip_fib_metrics_init()`, which returns default metrics when no metrics attribute is supplied or a newly allocated metrics block on success.

## Control Flow
`ip_fib_metrics_init()` allocates zeroed metrics storage, then `ip_metrics_convert()` iterates nested netlink attributes. Numeric metrics must be `u32`; congestion-control algorithm metrics are string-resolved through TCP congestion-control registration. Selected values are clamped for MSS, MTU, and hoplimit. Feature masks are rejected if unknown bits are set. ECN-capable congestion algorithms set `DST_FEATURE_ECN_CA`.

## State And Persistence
Allocated metrics are in-memory route state with refcount initialized to one. The parser has no global state, but it consults TCP congestion-control registry state when resolving `RTAX_CC_ALGO`.

## Dependencies And Integration Points
The file integrates rtnetlink extended acknowledgements, `array_index_nospec()` bounds hardening, TCP congestion-control lookup, `dst_default_metrics`, and route creation paths that call `ip_fib_metrics_init()`.

## Risks
The main risks are ABI validation regressions, accepting unknown feature bits, forgetting to clamp legacy IPv4 limits, mishandling unknown congestion-control names, and leaks on parser failure.

## Test Signals
Exercise absent metrics, valid numeric metrics, invalid attribute lengths, out-of-range metric type, unknown feature bits, MSS/MTU/hoplimit clamping, known and unknown congestion-control names, ECN-CA feature propagation, and allocation failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/metrics.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter.c

## Purpose
`netfilter.c` provides IPv4-specific routing helpers used by netfilter modules after packet mangling or for route lookups from generic netfilter code.

## Important APIs, Types, And Functions
Exports are `ip_route_me_harder()` and `nf_ip_route()`. `ip_route_me_harder()` reroutes an skb after source/destination/TOS/mark changes and optionally performs XFRM lookup. `nf_ip_route()` wraps `ip_route_output_key()` for generic netfilter routing.

## Control Flow
`ip_route_me_harder()` derives a `flowi4` from the current IP header, socket, mark, L3 master, source address type, and early flow dissection, then installs a new dst. If XFRM is enabled and the packet has not already been transformed, it decodes and applies an XFRM route. Finally it expands headroom if the output device hard-header length increased.

## State And Persistence
No persistent state is owned. The function mutates the skb destination, may steal/drop dst references, and may expand skb headroom.

## Dependencies And Integration Points
Callers include mangle/NAT/queue/reject paths that need a packet rerouted after header or mark changes. It depends on FIB routing, L3 master devices, XFRM, flow dissector integration, and skb dst/headroom APIs.

## Risks
Risks include using a foreign source address incorrectly, missing XFRM policy application, returning with insufficient headroom, dst reference mistakes, and subtle behavior changes for locally generated packets using non-standard sources.

## Test Signals
Test mangle `LOCAL_OUT` reroute after mark, TOS, source, and destination changes; XFRM policy interaction; bound socket output interfaces; VRF/L3 master behavior; and failure paths for route lookup, XFRM lookup, and head expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/Kconfig -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/Kconfig

## Purpose
This Kconfig file declares IPv4 and ARP netfilter build options: defrag, legacy iptables/arptables, nftables IPv4/ARP support, IPv4 NAT helpers, duplicate/reject/log/socket/tproxy helpers, and legacy match/target/table modules.

## Important APIs, Types, And Functions
It defines options such as `NF_DEFRAG_IPV4`, `IP_NF_IPTABLES_LEGACY`, `IP_NF_IPTABLES`, `IP_NF_FILTER`, `IP_NF_NAT`, `IP_NF_MANGLE`, `IP_NF_RAW`, `IP_NF_SECURITY`, `IP_NF_ARPTABLES`, `IP_NF_ARPFILTER`, `IP_NF_ARP_MANGLE`, `NFT_*_IPV4`, `NF_NAT_H323`, and compatibility selectors for old target/match names.

## Control Flow
The file is declarative. Menu visibility depends on `INET && NETFILTER`; nftables entries are nested under `NF_TABLES`; legacy iptables tables are nested under `IP_NF_IPTABLES`; NAT helpers are nested under `NF_NAT`; ARP legacy options are separate at the end.

## State And Persistence
Kconfig choices persist in kernel configuration and determine whether corresponding objects are built-in, modular, or absent.

## Dependencies And Integration Points
It coordinates with the sibling Makefile and wider netfilter symbols such as `NETFILTER_XTABLES`, `NETFILTER_XTABLES_LEGACY`, `NF_CONNTRACK`, `NF_NAT`, `SECURITY`, `NFT_COMPAT`, and `SYN_COOKIES`.

## Risks
Risks include dependency cycles, accidentally enabling legacy modules when nftables-only configurations expect not to, missing selectors for helper functionality, and changing defaults that affect distro kernel module availability.

## Test Signals
Run representative `allnoconfig`, `defconfig`, legacy iptables, nftables-only, NAT-helper, and ARP-table configurations; verify expected modules appear in `.config` and Makefile object expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/Makefile -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/Makefile

## Purpose
The Makefile maps IPv4/ARP netfilter Kconfig symbols to object files and composite objects.

## Important APIs, Types, And Functions
It builds defrag, socket/tproxy, reject, NAT helpers, nftables IPv4 expressions, legacy iptables core and table instances, legacy matches/targets, legacy arptables core/table/target modules, and `nf_dup_ipv4.o`. `nf_nat_snmp_basic-y` demonstrates a composite module with generated ASN.1 support.

## Control Flow
Object selection follows `obj-$(CONFIG_...) += ...`; composite module prerequisites are declared before the corresponding `obj-*` line. Build order groups defrag/core helpers, NAT helpers, nft modules, legacy IP tables, matches, targets, ARP tables, and duplicate support.

## State And Persistence
No runtime state; it persists build composition in kbuild metadata.

## Dependencies And Integration Points
The file must stay aligned with Kconfig symbols and source filenames in this directory. It also integrates generated ASN.1 header dependencies for SNMP NAT.

## Risks
Risks are stale symbol/object mappings, missing composite dependencies, modules built without their Kconfig gate, and mismatches between backward-compatible Kconfig selector names and actual object names.

## Test Signals
Use `make net/ipv4/netfilter/` or kernel config matrix builds to verify each symbol selects the expected object, especially `IP_NF_IPTABLES_LEGACY`, table modules, ARP modules, `NF_NAT_H323`, `NF_DEFRAG_IPV4`, and nftables IPv4 modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/arp_tables.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/arp_tables.c

## Purpose
`arp_tables.c` is the legacy arptables core: it evaluates ARP xtables rules, validates and installs userspace-provided ARP table replacements, exposes sockopt ABIs, handles counters and compat conversion, and registers built-in standard/error targets.

## Important APIs, Types, And Functions
Exports are `arpt_alloc_initial_table()`, `arpt_do_table()`, `arpt_register_table()`, and `arpt_unregister_table()`. Important internals include `arp_packet_match()`, `translate_table()`, `mark_source_chains()`, `find_check_entry()`, `copy_entries_to_user()`, `do_replace()`, `do_add_counters()`, compat translate/copy helpers, `do_arpt_set_ctl()`, and `do_arpt_get_ctl()`.

## Control Flow
Packet evaluation pulls the full ARP header, matches opcode/hardware/protocol lengths, source/target hardware and IP addresses, and in/out interface masks, then executes standard jumps/returns or extension targets. Table replacement copies a user blob, validates entry sizes, hook/underflow offsets, rule graph loops, target modules, and counters, then atomically swaps it into the xt table. Sockopts gate all operations on `CAP_NET_ADMIN`.

## State And Persistence
Per-net xtables state is initialized by `xt_proto_init()`. Table state lives in `struct xt_table_info` with per-CPU counters, hook offsets, underflows, stack size, and installed target module references. State is in-memory and namespace-scoped.

## Dependencies And Integration Points
It integrates xtables core APIs, ARP netfilter family hooks, `nf_sockopt_ops`, module autoloading, vmalloc counters, compat syscall translation, and table instance modules such as `arptable_filter.c`.

## Risks
This is a high-risk userspace ABI parser. Risks include integer/offset validation bugs, loop detection errors, compat size conversion mistakes, counter snapshot races, module reference leaks, FireWire ARP target-address differences, and jump-stack overflow.

## Test Signals
Test malformed replacement blobs, hook and underflow validation, jump loops, unknown targets, compat 32-bit replace/get paths, counter add/get, standard verdicts, error target behavior, FireWire ARP matching, namespace init/exit, and table unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/arp_tables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/arpt_mangle.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/arpt_mangle.c

## Purpose
`arpt_mangle.c` implements the legacy ARP `mangle` target that rewrites ARP sender/target hardware and protocol addresses.

## Important APIs, Types, And Functions
The registered `xt_target` is named `mangle` for `NFPROTO_ARP`. `target()` performs payload rewriting based on `struct arpt_mangle` flags, and `checkentry()` validates flag and verdict combinations.

## Control Flow
At runtime the target ensures the skb is writable, walks the ARP payload using `ar_hln` and `ar_pln`, bounds-checks each requested field against fixed maximums and the skb tail, writes requested source/target fields, and returns the configured verdict (`DROP`, `ACCEPT`, or `XT_CONTINUE`).

## State And Persistence
No per-net state is owned. Persistent state is only the module registration and rule-provided `arpt_mangle` target data.

## Dependencies And Integration Points
It is invoked by `arp_tables.c` after ARP rule matching and is built for `IP_NF_ARP_MANGLE`. It depends on ARP header layout, skb writability helpers, and FireWire ARP special handling.

## Risks
Risks include malformed ARP length fields, non-linear skb write failures, target address rewriting on FireWire ARP, and invalid target verdicts.

## Test Signals
Test all four rewrite flags, mixed rewrites with `XT_CONTINUE`, invalid flags, invalid verdicts, short/truncated ARP packets, non-linear skbs, and FireWire target-hardware/protocol rewrite rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/arpt_mangle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/arptable_filter.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/arptable_filter.c

## Purpose
`arptable_filter.c` instantiates the legacy ARP `filter` table over ARP input, output, and forward hooks.

## Important APIs, Types, And Functions
The main objects are `packet_filter`, `arpfilter_ops`, `arptable_filter_table_init()`, `arptable_filter_net_pre_exit()`, `arptable_filter_net_exit()`, `arptable_filter_init()`, and `arptable_filter_fini()`.

## Control Flow
Module init allocates hook ops with `xt_hook_ops_alloc()` using `arpt_do_table()`, registers per-net exit hooks, and registers an xtables template. Each namespace gets an initial filter table through the template callback. Exit unregisters the template, pernet ops, and hook ops.

## State And Persistence
State is per namespace through the registered xt table. The module holds one static hook-ops array pointer shared as template data.

## Dependencies And Integration Points
It depends on `arp_tables.c`, xtables templates, ARP netfilter family hooks, and kfree-managed hook ops.

## Risks
Risks are init/exit ordering mistakes, hook-op allocation failure handling, and unregistering a table while hooks may still observe it.

## Test Signals
Test module load/unload, namespace creation/destruction, default table availability, ARP input/output/forward hooks, and cleanup under failed `register_pernet_subsys()` or `xt_register_template()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/arptable_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/ip_tables.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/ip_tables.c

## Purpose
`ip_tables.c` is the legacy IPv4 iptables core: it evaluates IPv4 xtables rules, validates and replaces userspace table blobs, manages match/target module references, exposes the legacy sockopt ABI, supports compat tasks, and registers built-in standard/error targets.

## Important APIs, Types, And Functions
Exports are `ipt_alloc_initial_table()`, `ipt_do_table()`, `ipt_register_table()`, and `ipt_unregister_table_exit()`. Major internals are `ip_packet_match()`, `trace_packet()`, `mark_source_chains()`, `find_check_match()`, `find_check_entry()`, `translate_table()`, `copy_entries_to_user()`, `do_replace()`, `do_add_counters()`, compat conversion helpers, and sockopt handlers.

## Control Flow
Packet traversal starts at the hook entry offset, matches source/destination masks, interfaces, protocol, fragment state, and all extension matches, updates per-CPU counters, then executes standard jumps/gotos/returns or extension targets. TRACE logging reconstructs chain/rule context when enabled. Replacement validates entry sizes, offsets, hooks, underflows, rule graph loops, match/target modules, and then swaps the table atomically through xtables core.

## State And Persistence
Per-net protocol state is initialized by `xt_proto_init()`. Installed table state is in `struct xt_table_info`: entries, counters, hook/underflow offsets, jump stack, and module refs. It is all in-memory and namespace-scoped.

## Dependencies And Integration Points
It integrates netfilter IPv4 hooks, xtables match/target registry, sockopts, proc/compat infrastructure, module autoloading, per-CPU seqcount counter snapshots, TRACE logging, and table instance modules such as filter, mangle, nat, raw, and security.

## Risks
This file has high ABI and memory-safety exposure. Risks include replacement blob validation gaps, compat offset mistakes, rule graph loop bugs, module reference leaks, counter races, jump stack corruption with TEE recursion, fragment handling surprises, and trace path assumptions.

## Test Signals
Exercise malformed table replacement, loop/goto/return chains, all standard verdicts, match/target module load failures, counter add/get, 32-bit compat replace/get, TEE recursion, TRACE logging, fragment matching, namespace lifecycle, and table unregister while packets are traversing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/ip_tables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/ipt_ECN.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/ipt_ECN.c

## Purpose
`ipt_ECN.c` implements the legacy IPv4 `ECN` target for the mangle table, modifying ECN bits in the IPv4 TOS field and optionally TCP ECE/CWR flags.

## Important APIs, Types, And Functions
The target is `ecn_tg_reg`. Important functions are `set_ect_ip()`, `set_ect_tcp()`, `ecn_tg()`, and `ecn_tg_check()`.

## Control Flow
The target applies configured IP ECN changes after making the IP header writable and updating the IPv4 checksum. If TCP flag operations are requested and the packet is TCP, it reads the TCP header, ensures it is writable, updates ECE/CWR bits, and adjusts the TCP checksum.

## State And Persistence
No mutable global state. Rule state is `struct ipt_ECN_info` stored in the installed xtables rule.

## Dependencies And Integration Points
It integrates with `ip_tables.c` target execution, mangle table restrictions, skb writable helpers, IPv4 and TCP checksum update helpers, and the target check path that verifies TCP-only operations.

## Risks
Risks include checksum update mistakes, truncated TCP headers, non-linear skb write failures, accepting TCP flag operations on non-TCP rules, and incorrect operation-mask validation.

## Test Signals
Test IP ECN-only rewrite, TCP ECE/CWR rewrite, no-op cases, truncated TCP packets, non-linear skbs, invalid operation bits, invalid ECN codepoints, and non-TCP rule rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/ipt_ECN.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/ipt_REJECT.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/ipt_REJECT.c

## Purpose
`ipt_REJECT.c` implements the IPv4 legacy `REJECT` target, converting filter-table rejections into ICMP unreachable responses or TCP resets before dropping the original packet.

## Important APIs, Types, And Functions
The registered target is `reject_tg_reg`. `reject_tg()` emits the selected response through `nf_send_unreach()` or `nf_send_reset()`. `reject_tg_check()` validates unsupported and TCP-specific modes.

## Control Flow
At packet traversal time the target switches on `struct ipt_reject_info.with`, emits an ICMP net/host/protocol/port/prohibited/admin unreachable or a TCP reset, and returns `NF_DROP`. Checkentry rejects obsolete `ECHOREPLY` and requires TCP protocol matching for `TCP_RESET`.

## State And Persistence
No persistent state beyond module registration and per-rule target data.

## Dependencies And Integration Points
It is restricted to the filter table and local-in/forward/local-out hooks. It depends on IPv4 reject helper functions and the iptables target check path.

## Risks
Risks include emitting resets for non-TCP traffic if validation regresses, wrong hook context passed to reject helpers, bridge-netfilter interactions, and accidentally supporting obsolete reject modes.

## Test Signals
Test each ICMP reject code, TCP reset only on valid TCP rules, invalid `ECHOREPLY`, hook restrictions, local-out and forward behavior, and interaction with packets already malformed enough for helper refusal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/ipt_REJECT.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/ipt_SYNPROXY.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/ipt_SYNPROXY.c

## Purpose
`ipt_SYNPROXY.c` implements the IPv4 legacy `SYNPROXY` target, intercepting TCP handshakes and using syncookies to protect back-end services from SYN floods.

## Important APIs, Types, And Functions
The target is `synproxy_tg4_reg`. Runtime logic is in `synproxy_tg4()`. Lifecycle validation is in `synproxy_tg4_check()` and `synproxy_tg4_destroy()`.

## Control Flow
The target validates the TCP checksum, parses TCP options, handles initial SYN packets by building and sending a SYNACK cookie, and handles pure ACK packets by validating the cookie and either stealing the skb or dropping it. Other packets continue through the rule set.

## State And Persistence
State is held in per-net synproxy structures and conntrack namespace references acquired during rule check and released at rule destruction. Per-rule settings are `struct xt_synproxy_info`.

## Dependencies And Integration Points
It depends on conntrack, `nf_synproxy`, TCP option parsing, syncookies, and IPv4 hooks for local-in and forward. Kconfig selects `NETFILTER_SYNPROXY` and `SYN_COOKIES`.

## Risks
Risks include conntrack reference leaks, accepting non-TCP rules, checksum parsing failures, option/cookie mismatch, statistics inaccuracies, and consuming or dropping skbs incorrectly.

## Test Signals
Test SYN, SYN+ACK-invalid, pure ACK cookie success/failure, bad checksum, malformed options, rule insertion/removal refcounts, namespace teardown, and forward/local-in hook behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/ipt_SYNPROXY.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/ipt_ah.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/ipt_ah.c

## Purpose
`ipt_ah.c` implements the IPv4 `ah` match, matching IPsec Authentication Header packets by SPI range.

## Important APIs, Types, And Functions
The match object is `ah_mt_reg`. `spi_match()` applies inclusive SPI range and inversion. `ah_mt()` extracts the AH header and evaluates the SPI. `ah_mt_check()` validates inversion flags.

## Control Flow
The match refuses non-first fragments, safely reads the AH header at `par->thoff`, hotdrops tiny packets when the header cannot be read, and compares the network-order SPI against the configured host-order range.

## State And Persistence
No global state. Rule state is `struct ipt_ah` in the xtables match data.

## Dependencies And Integration Points
It is registered for `NFPROTO_IPV4` with protocol `IPPROTO_AH`, and is called from `ip_tables.c` match traversal.

## Risks
Risks include fragment handling surprises, incorrect hotdrop behavior for tiny packets, endianness mistakes in SPI comparison, and invalid inversion flag acceptance.

## Test Signals
Test SPI range match, inverted match, boundary values, non-first fragments, truncated AH headers, non-AH rule rejection via xtables protocol gate, and invalid invflags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/ipt_ah.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/ipt_rpfilter.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/ipt_rpfilter.c

## Purpose
`ipt_rpfilter.c` implements an IPv4 reverse-path filter match for legacy iptables, checking whether a reply route for the packet source would use the incoming interface.

## Important APIs, Types, And Functions
The match is `rpfilter_mt_reg`. Runtime helpers are `rpfilter_get_saddr()`, `rpfilter_lookup_reverse()`, `rpfilter_is_loopback()`, and `rpfilter_mt()`. Validation is `rpfilter_check()`.

## Control Flow
Loopback packets pass immediately. Zeronet sources to broadcast/local multicast are accepted. Otherwise the match builds a reverse `flowi4` from packet source/destination, optional mark, DSCP, L3 master, and uid, then performs `fib_lookup()` and verifies route type and nexthop device, optionally allowing loose mode or local addresses.

## State And Persistence
No persistent state beyond per-rule `struct xt_rpfilter_info`.

## Dependencies And Integration Points
It is limited to PREROUTING in the raw or mangle tables. It depends on IPv4 FIB lookup, nexthop-device checking, L3 master/VRF support, and xtables match validation.

## Risks
Risks include route-policy mismatches, VRF/L3 master mistakes, mishandling multicast/broadcast/zeronet cases, accepting unknown flags, and unexpected behavior with mark-sensitive routing.

## Test Signals
Test strict and loose modes, invert flag, accept-local flag, valid-mark flag, loopback packets, zeronet broadcast/multicast packets, VRF input, non-unicast reverse routes, and rejection outside raw/mangle tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/ipt_rpfilter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/iptable_filter.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/iptable_filter.c

## Purpose
`iptable_filter.c` instantiates the legacy IPv4 `filter` table for local input, forwarding, and local output.

## Important APIs, Types, And Functions
Important objects are `packet_filter`, `filter_ops`, module parameter `forward`, `iptable_filter_table_init()`, `iptable_filter_net_init()`, and module init/exit routines.

## Control Flow
Module init allocates hook ops using `ipt_do_table()`, registers pernet ops, and registers an xtables template. Initial table creation adjusts the default FORWARD policy based on the `forward` module parameter. If forwarding default is accept, namespace init can defer table creation until template lookup; if false, it eagerly creates the table.

## State And Persistence
The installed xt table is per-net state. The static `forward` module parameter determines the initial FORWARD policy for newly created tables.

## Dependencies And Integration Points
It depends on `ip_tables.c`, xtables templates, IPv4 netfilter hooks, and module parameters.

## Risks
Risks include surprising default FORWARD policy behavior, init failure cleanup ordering, and per-net table creation differences based on the module parameter.

## Test Signals
Test module load with `forward=1` and `forward=0`, default chain policies, local-in/forward/local-out hook traversal, namespace lifecycle, and cleanup on partial init failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/iptable_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/iptable_mangle.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/iptable_mangle.c

## Purpose
`iptable_mangle.c` instantiates the legacy IPv4 `mangle` table and reroutes locally generated packets when rules change routing-relevant fields.

## Important APIs, Types, And Functions
Important functions are `ipt_mangle_out()`, `iptable_mangle_hook()`, `iptable_mangle_table_init()`, and module init/exit. The table is `packet_mangler`.

## Control Flow
All five IPv4 hooks use the mangle table. For `LOCAL_OUT`, the module snapshots source, destination, mark, and TOS before `ipt_do_table()`. If the packet is not dropped/stolen and any value changed, it calls `ip_route_me_harder()` and converts routing errors into `NF_DROP_ERR()`.

## State And Persistence
State is the per-net xt table plus static hook-ops pointer. It does not store packet history; reroute decisions are per packet.

## Dependencies And Integration Points
It integrates with `ip_tables.c`, `ip_route_me_harder()` from IPv4 netfilter glue, IPv4 route output, and all major IPv4 netfilter hooks at mangle priority.

## Risks
Risks include missing a route-affecting field change, unnecessary reroutes, incorrect handling of `NF_STOLEN`, route failure drops, and skb mutation by targets that changes header pointers.

## Test Signals
Test LOCAL_OUT changes to mark/TOS/source/destination, unchanged no-op rules, drop/stolen verdicts, route lookup failure, all hook registrations, and namespace cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/iptable_mangle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/iptable_nat.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/iptable_nat.c

## Purpose
`iptable_nat.c` instantiates the legacy IPv4 `nat` table and registers NAT lookup hooks that execute `ipt_do_table()` at destination and source NAT priorities.

## Important APIs, Types, And Functions
Key pieces are `struct iptable_nat_pernet`, `nf_nat_ipv4_table`, `nf_nat_ipv4_ops[]`, `ipt_nat_register_lookups()`, `ipt_nat_unregister_lookups()`, `iptable_nat_table_init()`, and pernet/module lifecycle functions.

## Control Flow
Table initialization registers the `nat` xt table, then clones the NAT hook templates, sets each hook `priv` to the xt table, and registers them through `nf_nat_ipv4_register_fn()`. On failure it unregisters previously installed hooks and tears down the table. Per-net pre-exit unregisters hooks before table removal.

## State And Persistence
Per namespace state stores the cloned hook ops pointer in `iptable_nat_pernet`; table entries are normal xtables state. Hooks are freed via RCU after unregister.

## Dependencies And Integration Points
It depends on `ip_tables.c`, `nf_nat`, pernet generic storage, xtables templates, and NAT priorities for PREROUTING, POSTROUTING, LOCAL_OUT, and LOCAL_IN.

## Risks
Risks include hook/table lifetime ordering, partial registration leaks, RCU freeing of hook arrays, NAT priority regressions, and failures when the table cannot be found after registration.

## Test Signals
Test module load/unload, namespace lifecycle, PREROUTING/LOCAL_OUT DNAT and POSTROUTING/LOCAL_IN SNAT paths, partial hook registration failure, and table unregister after NAT hook unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/iptable_nat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/iptable_raw.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/iptable_raw.c

## Purpose
`iptable_raw.c` instantiates the legacy IPv4 `raw` table, used at PREROUTING and LOCAL_OUT before most connection tracking decisions, optionally before defragmentation.

## Important APIs, Types, And Functions
Important objects are `raw_before_defrag`, `packet_raw`, `packet_raw_before_defrag`, `rawtable_ops`, `iptable_raw_table_init()`, and module lifecycle functions.

## Control Flow
Module init chooses the table priority based on `raw_before_defrag`, allocates hook ops with `ipt_do_table()`, registers pernet ops, and registers the template. Table init uses the same selected table metadata. Exit unregisters the template using the normal raw table descriptor and removes pernet state.

## State And Persistence
State is the per-net raw xt table. The module parameter `raw_before_defrag` persists for the module lifetime and affects hook priority for all namespaces.

## Dependencies And Integration Points
It integrates with `ip_tables.c`, IPv4 netfilter priorities `NF_IP_PRI_RAW` and `NF_IP_PRI_RAW_BEFORE_DEFRAG`, and legacy NOTRACK/TRACE style workflows.

## Risks
Risks include priority mismatch with conntrack defrag, module exit unregistering the wrong template descriptor when `raw_before_defrag` is set, and rule behavior differences for fragmented packets.

## Test Signals
Test load with and without `raw_before_defrag`, PREROUTING and LOCAL_OUT traversal, interaction with defrag/conntrack, namespace lifecycle, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/iptable_raw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/iptable_security.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/iptable_security.c

## Purpose
`iptable_security.c` instantiates the legacy IPv4 `security` table for MAC policy hooks after normal DAC-style filtering.

## Important APIs, Types, And Functions
Key objects are `security_table`, `sectbl_ops`, `iptable_security_table_init()`, pernet pre-exit/exit handlers, and module init/exit.

## Control Flow
The module allocates hook ops using `ipt_do_table()`, registers pernet cleanup, and registers a template that creates a default security table per namespace. It hooks local input, forward, and local output at `NF_IP_PRI_SECURITY`.

## State And Persistence
State is the per-net xt table plus static hook ops. Rules are in-memory and namespace-scoped.

## Dependencies And Integration Points
It depends on `SECURITY` Kconfig, `ip_tables.c`, xtables templates, and IPv4 netfilter hook priority ordering.

## Risks
Risks include priority/order regressions relative to LSM/MAC expectations, init cleanup mistakes, and table absence in configurations without legacy iptables support.

## Test Signals
Test module load/unload, default table creation, local-in/forward/local-out hooks, ordering relative to filter/mangle tables, namespace teardown, and failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/iptable_security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_defrag_ipv4.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_defrag_ipv4.c

## Purpose
`nf_defrag_ipv4.c` provides IPv4 netfilter defragmentation hooks, enabling conntrack and related modules to request per-namespace fragment reassembly at PREROUTING and LOCAL_OUT.

## Important APIs, Types, And Functions
Exports are `nf_defrag_ipv4_enable()` and `nf_defrag_ipv4_disable()`. Runtime helpers are `nf_ct_ipv4_gather_frags()`, `nf_ct_defrag_user()`, and `ipv4_conntrack_defrag()`. The global hook descriptor is `defrag_hook`.

## Control Flow
Enable increments a per-net user count under `defrag4_mutex`, registering hooks on the first user and detecting overflow. The hook skips sockets marked `NODEFRAG`, already tracked/untracked packets in relevant configs, and non-fragments. Fragments are passed to `ip_defrag()` with a user id derived from hook, bridge prerouting status, and conntrack zone. Disable decrements and unregisters hooks when the count reaches zero.

## State And Persistence
Persistent state is per-net `net->nf.defrag_ipv4_users` and the global RCU pointer `nf_defrag_v4_hook`. Fragment queues live in the IPv4 defrag subsystem.

## Dependencies And Integration Points
It integrates with conntrack, bridge netfilter, conntrack zones, IPv4 defrag, pernet exit cleanup, and generic defrag hook registration.

## Risks
Risks include user-count underflow/overflow, hooks left registered after namespace exit, wrong zone-specific defrag user, stealing skb ownership incorrectly on reassembly, and NODEFRAG bypass regressions.

## Test Signals
Test enable/disable reference counting, overflow guard, fragment reassembly in PREROUTING and LOCAL_OUT, bridge prerouting, conntrack zones, untracked/already-tracked packets, NODEFRAG sockets, and namespace exit with active users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_defrag_ipv4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_dup_ipv4.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_dup_ipv4.c

## Purpose
`nf_dup_ipv4.c` implements IPv4 packet duplication for netfilter users such as TEE/nft dup, cloning a packet and sending the clone to an alternate gateway/interface while the original continues.

## Important APIs, Types, And Functions
The exported API is `nf_dup_ipv4()`. Routing is handled by `nf_dup_ipv4_route()`.

## Control Flow
`nf_dup_ipv4()` disables bottom halves, refuses recursive duplication via `current->in_nf_duplicate`, copies the skb, clears conntrack on the copy, sets DF, decrements TTL for ingress/input hooks, routes the clone to the supplied gateway and optional output interface, and sends it with `ip_local_out()` under the recursion guard.

## State And Persistence
No persistent module state. It mutates only the cloned skb and temporarily sets `current->in_nf_duplicate`.

## Dependencies And Integration Points
It depends on IPv4 route output, skb cloning, conntrack reset/untracked marking, checksum/output path behavior, and netfilter duplicate callers.

## Risks
Risks include recursion loops, TTL underflow behavior, route lookup failure, conntrack accounting contamination if reset is missed, and clone MTU/DF side effects.

## Test Signals
Test duplication from PREROUTING, INPUT, FORWARD, OUTPUT, and POSTROUTING callers; route failure; specified output interface; conntrack state on clones; TTL decrement on ingress/input; and nested dup suppression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_dup_ipv4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_nat_h323.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_nat_h323.c

## Purpose
`nf_nat_h323.c` implements NAT payload rewriting and expectation setup for the H.323 conntrack helper, covering H.225/Q.931, H.245, RTP/RTCP, T.120, RAS, and call-forwarding addresses.

## Important APIs, Types, And Functions
The module publishes `nathooks` through `nfct_h323_nat_hook`. Key functions are `set_addr()`, `set_h225_addr()`, `set_h245_addr()`, `set_sig_addr()`, `set_ras_addr()`, `nat_rtp_rtcp()`, `nat_t120()`, `nat_h245()`, `nat_q931()`, `nat_callforwarding()`, and expectation callbacks `ip_nat_q931_expect()` and `ip_nat_callforwarding_expect()`.

## Control Flow
Payload rewriting uses TCP or UDP NAT mangle helpers and relocates data pointers after possible skb reallocation. Signaling helpers locate embedded transport addresses matching the current connection tuple and rewrite them to NAT-facing tuple addresses/ports. Media/control helpers configure conntrack expectations, allocate NAT ports, rewrite advertised addresses, and save mapped ports in H.323 master helper data. Expect callbacks apply source and destination NAT to related connections when they appear.

## State And Persistence
Persistent state includes registered helper expectation functions, the RCU NAT hook pointer, per-connection H.323 helper data (`sig_port`, `rtp_port` arrays), and conntrack expectation objects. No independent table or namespace state is owned here.

## Dependencies And Integration Points
It integrates tightly with `nf_conntrack_h323`, `nf_nat`, NAT mangle helpers, conntrack expectations, TCP/UDP payload parsing, RCU hook publication, and helper expectation function registry.

## Risks
Risks are high because this rewrites application payloads. Important risks include stale data pointers after mangle, failed paired RTP/RTCP expectation cleanup, NAT port exhaustion, incorrect direction handling, loopback-address workaround regressions, expectation callback NAT mistakes, and races around RCU hook unregister.

## Test Signals
Test TCP and UDP payload rewriting, H.225/H.245 address replacement, RAS signal address replacement, RTP/RTCP paired expectations including busy-port retries and cleanup, T.120 and Q.931 expectations, call forwarding expectations, port exhaustion, malformed payloads, helper unload with active readers, and related connection NAT mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_nat_h323.c -->
