# subset-b-006215 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6table_mangle.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6table_mangle.c

Purpose: Implements the legacy IPv6 iptables `mangle` table module. It registers the table for all major IPv6 netfilter hooks so rules can alter packet metadata and selected IPv6 header fields before normal forwarding, input, output, or postrouting handling.

Important APIs, types, and functions: `packet_mangler` describes the `xt_table` named `mangle`, valid hooks, IPv6 family, module owner, and `NF_IP6_PRI_MANGLE` priority. `ip6t_mangle_out()` is the local-output special case. `ip6table_mangle_hook()` dispatches either to that special handling or directly to `ip6t_do_table()`. `ip6table_mangle_table_init()` allocates the initial `ip6t_replace` blob and registers the table per network namespace. Module setup uses `xt_hook_ops_alloc()`, `register_pernet_subsys()`, and `xt_register_template()`.

Control flow: module init allocates hook operations for the table and registers pernet/template callbacks. A namespace table init creates the empty initial ruleset and binds it to the preallocated hook ops. Runtime packets call `ip6table_mangle_hook()`. For `NF_INET_LOCAL_OUT`, the code snapshots source, destination, mark, hop limit, and the first 32 bits containing version/traffic class/flow label, runs the table, then calls `ip6_route_me_harder()` if routing-sensitive fields changed and the packet was not dropped or stolen. Other hooks just execute `ip6t_do_table()`.

State and persistence: Global module state is limited to `mangle_ops`. Per-net state is the registered xtables table/ruleset managed by ip6tables core. No durable persistence exists; rules live in kernel memory and are removed by namespace/module teardown.

Dependencies and integration: Depends on `ip6_tables`, generic xtables template registration, net namespace lifecycle, IPv6 routing repair via `ip6_route_me_harder()`, and netfilter hook priorities. It integrates with userspace through legacy ip6tables rule management.

Risks and test signals: Critical risk is failing to reroute after local-output mangling of addresses, mark, hop limit, traffic class, or flow label. Tests should cover local-output rules changing `MARK`, destination/source address, hop limit, and traffic class with route changes, plus namespace creation/destruction and module unload. Hook ordering should be checked against raw, conntrack, nat, and security priorities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6table_mangle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6table_nat.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6table_nat.c

Purpose: Provides the legacy IPv6 iptables `nat` table and wires table lookups into the IPv6 NAT hook registration API. It enables destination NAT in prerouting/local-output and source NAT in postrouting/local-input for legacy ip6tables users.

Important APIs, types, and functions: `struct ip6table_nat_pernet` stores per-net duplicated NAT hook ops. `nf_nat_ipv6_table` declares the table. `nf_nat_ipv6_ops[]` defines four hooks using `ip6t_do_table()` at NAT priorities. `ip6t_nat_register_lookups()` finds the table, duplicates hook ops, sets `priv` to the xt table, and registers each with `nf_nat_ipv6_register_fn()`. `ip6t_nat_unregister_lookups()` unregisters and RCU-frees them. `ip6table_nat_table_init()` registers the table then hook lookups.

Control flow: Module init registers pernet storage before template registration so `net_generic()` state exists during table creation. Namespace init allocates/registers the initial nat table and then registers NAT lookup hooks. Runtime NAT hook dispatch calls `ip6t_do_table()` with the xt table as `priv`. On partial registration failure, previously registered hooks are unwound and the ops array is `kfree_rcu()`'d. Teardown unregisters hook lookups first, then unregisters the xt table in pre-exit/exit phases.

State and persistence: Per-net state stores `nf_nat_ops`; the xt table holds the current ruleset. Hook ops are dynamically duplicated because `priv` points at a namespace-specific table. Rules and ops are volatile kernel state.

Dependencies and integration: Depends on `nf_nat`, `ip6_tables`, pernet generic IDs, RCU lifetime, and `nf_nat_ipv6_register_fn()` rather than direct `nf_register_net_hooks()`. Integrates with legacy ip6tables NAT targets and conntrack/NAT core.

Risks and test signals: Main risks are lifetime bugs around table lookup, hook op duplication, and RCU freeing; NAT also requires correct priority ordering relative to conntrack. Tests should exercise module load/unload across multiple netns, failure injection for hook registration, DNAT/SNAT/MASQUERADE-style rules, and concurrent packet traversal while a namespace exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6table_nat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6table_raw.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6table_raw.c

Purpose: Implements the legacy IPv6 iptables `raw` table for early packet classification, primarily to mark traffic as untracked before conntrack. It can run at the standard raw priority or, via module parameter, before defragmentation.

Important APIs, types, and functions: `packet_raw` and `packet_raw_before_defrag` are two `xt_table` definitions with the same name and hooks but different priorities. `raw_before_defrag` is a read-mostly module parameter. `ip6table_raw_table_init()` selects the table variant, allocates an initial table, and registers it with `rawtable_ops`. Module init allocates hooks through `xt_hook_ops_alloc()` and registers pernet/template lifecycle hooks.

Control flow: During module init, the module parameter selects the hook priority and emits an informational log if before-defrag mode is enabled. A namespace init uses the same table choice to create the empty ruleset. Runtime hook handling is direct `ip6t_do_table()` at prerouting and local-output.

State and persistence: Global state includes `raw_before_defrag` and `rawtable_ops`; per-net state is the xtables ruleset. The module parameter is fixed at load time. Rule state is in kernel memory only.

Dependencies and integration: Integrates with xtables, net namespace lifecycle, and netfilter hook ordering. The before-defrag variant interacts closely with IPv6 fragment handling and conntrack defrag because rule evaluation may see fragments that would otherwise be reassembled first.

Risks and test signals: The `ip6table_raw_fini()` unregisters the template using `&packet_raw`; this relies on xtables template handling by table name despite possible before-defrag registration. Tests should cover both module parameter values, `NOTRACK` behavior before conntrack, fragmented traffic visibility, per-net registration, and unload after active rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6table_raw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6table_security.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6table_security.c

Purpose: Implements the legacy IPv6 iptables `security` table for Mandatory Access Control policy rules that should be evaluated separately from ordinary discretionary filtering.

Important APIs, types, and functions: `security_table` defines the `xt_table` name, IPv6 family, valid hooks (`LOCAL_IN`, `FORWARD`, `LOCAL_OUT`), and `NF_IP6_PRI_SECURITY` priority. `sectbl_ops` stores allocated hook operations. `ip6table_security_table_init()` allocates the initial table and registers it. Pernet callbacks unregister in pre-exit/exit phases.

Control flow: Module init allocates hook ops using `ip6t_do_table()` as the hook, registers pernet operations, and registers an xtables template. Namespace initialization creates the default empty ruleset. Runtime packets at valid hooks run through `ip6t_do_table()`. Module exit reverses template, pernet, and hook-op allocation.

State and persistence: Only module-level hook ops and per-net xtables rulesets are kept. No on-disk persistence; userspace policy reload is required after reboot/module reload.

Dependencies and integration: Depends on ip6tables/xtables and MAC/security policy users such as SECMARK/CONNSECMARK workflows. Hook priority places it after normal filtering semantics expected by the security table.

Risks and test signals: Risks are mostly hook coverage and ordering. Tests should verify security table rule hits on local input, forwarding, and local output; namespace teardown with rules; and expected interaction with labels/marks used by LSM policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6table_security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_conntrack_reasm.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_conntrack_reasm.c

Purpose: Supplies IPv6 fragment reassembly for netfilter connection tracking and defragmentation users. It is parallel to the core IPv6 reassembly path but uses a netfilter-specific fragment cache, user keys, and sysctls under `net/netfilter`.

Important APIs, types, and functions: `nf_frags` is the module-wide `inet_frags` cache. `nf_frag_pernet()` retrieves per-net `struct nft_ct_frag6_pernet`. `nf_ct_frag6_gather()` is the exported entry point used by defrag hooks. Internal helpers include `fq_find()`, `nf_ct_frag6_queue()`, `nf_ct_frag6_reasm()`, and `find_prev_fhdr()`. Lifecycle exports are `nf_ct_frag6_init()` and `nf_ct_frag6_cleanup()`. Optional sysctls expose timeout/low/high thresholds.

Control flow: `nf_ct_frag6_gather()` ignores jumbo payloads, locates the fragment header and previous next-header field, rejects first fragments missing complete upper-layer headers, pulls the fragment header, and finds/creates a keyed queue. With the queue lock held, `nf_ct_frag6_queue()` validates offset/end, ECN, checksum state, last-fragment consistency, 8-byte alignment, and overlap/duplicate conditions before inserting into the generic fragment tree. When first and last fragments are present and `meat == len`, `nf_ct_frag6_reasm()` kills the queue, validates combined ECN, removes the fragment header, shifts headers, finishes generic reassembly, updates payload length/DS field/fragment metadata, and returns the completed skb.

State and persistence: Per-net fragment directory state stores live queues, memory thresholds, timeout, and sysctl header. Each queue tracks source/destination/id/user/iif, length, meat, ECN bits, max size, nhoffset, timestamps, and fragments. State is in-memory and timeout-driven only.

Dependencies and integration: Uses generic `inet_frags`, IPv6 fragment helpers, net namespace generic storage, RCU, queue spinlocks, sysctl, checksum helpers, and `IP6CB` metadata. It integrates through `nf_ct_frag6_gather()` with `nf_defrag_ipv6_hooks.c`.

Risks and test signals: High-risk areas include fragment overlap handling, first-fragment upper-layer truncation, ECN merge failure, checksum adjustment, queue memory accounting, and correct preservation/removal of extension headers. Tests should include duplicate fragments, overlaps, misaligned non-final fragments, oversize payloads, timeout expiry, link-local/multicast iif keying, conntrack zones/users, and successful reassembly feeding conntrack.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_conntrack_reasm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_defrag_ipv6_hooks.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_defrag_ipv6_hooks.c

Purpose: Registers IPv6 netfilter defragmentation hooks on demand and connects them to `nf_ct_frag6_gather()`. It lets conntrack and other users share defrag hooks with per-network-namespace reference counting.

Important APIs, types, and functions: `nf_ct6_defrag_user()` derives the fragment cache user from hook, conntrack zone, and bridge prerouting state. `ipv6_defrag()` is the hook callback. `ipv6_defrag_ops[]` registers prerouting and local-output hooks at `NF_IP6_PRI_CONNTRACK_DEFRAG`. `nf_defrag_ipv6_enable()` and `nf_defrag_ipv6_disable()` are exported reference-counted enable/disable APIs. `defrag_hook` is published through `nf_defrag_v6_hook`.

Control flow: Module init initializes conntrack fragment reassembly, registers pernet exit cleanup, and publishes the defrag hook pointer via RCU. Enabling locks `defrag6_mutex`, checks overflow, increments existing users, or registers both hooks and sets users to one. Runtime skips already tracked non-template packets and untracked packets, then calls `nf_ct_frag6_gather()`. `-EINPROGRESS` means the fragment was queued and returns `NF_STOLEN`; zero accepts; other errors drop. Disable decrements and unregisters hooks when the count reaches zero.

State and persistence: Per-net `net->nf.defrag_ipv6_users` is the reference count. Fragment queues live in `nf_conntrack_reasm.c`. The RCU-published global hook pointer has module lifetime.

Dependencies and integration: Depends on conntrack when enabled, bridge netfilter, conntrack zones, netfilter hook registration, RCU hook publication, and net namespace exit cleanup. It is the main integration point by which conntrack requests IPv6 defrag.

Risks and test signals: Risks include reference-count leaks, overflow behavior, stale hooks on netns exit, and incorrect skip logic for untracked or already tracked packets. Tests should repeatedly enable/disable from multiple users, run fragmented prerouting/local-output traffic, use conntrack zones and bridge prerouting, and unload while namespaces with active users exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_defrag_ipv6_hooks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_dup_ipv6.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_dup_ipv6.c

Purpose: Implements IPv6 packet duplication for TEE-like netfilter targets and nftables `dup`. It copies an skb, routes the copy toward a configured gateway/interface, and transmits it without consuming the original packet.

Important APIs, types, and functions: `nf_dup_ipv6()` is the exported duplication API. `nf_dup_ipv6_route()` builds a `flowi6`, performs `ip6_route_output()`, attaches the dst, sets output device/protocol, and reports route success. The module uses `current->in_nf_duplicate` as a recursion guard.

Control flow: `nf_dup_ipv6()` disables bottom halves, checks recursion, copies the skb with `GFP_ATOMIC`, clears conntrack state and marks it untracked when conntrack is enabled, decrements hop limit for prerouting/local-in duplicates, routes to the gateway, and emits through `ip6_local_out()`. On route or allocation failure it frees the copy. The original skb continues through its caller's rule path.

State and persistence: No persistent state. Temporary cloned skb state is adjusted: conntrack reset, optional hop-limit decrement, dst replacement, output dev, protocol, and recursion flag around output.

Dependencies and integration: Depends on IPv6 routing/output, netfilter hook numbers, conntrack reset helpers, and consumers in xt/nft duplication modules. It must integrate safely with local-output netfilter because the duplicated skb re-enters output.

Risks and test signals: Risks include recursion loops, hop-limit underflow behavior, route lookup to link-local gateways without correct oif, and copied skb metadata leakage. Tests should duplicate from prerouting and local-in, verify original delivery continues, verify conntrack is not inherited, test unreachable gateways, explicit oif, and rules that could recursively match duplicates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_dup_ipv6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_reject_ipv6.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_reject_ipv6.c

Purpose: Provides the IPv6 reject core used by iptables/nftables to synthesize TCP resets and ICMPv6 destination-unreachable packets for rejected traffic.

Important APIs, types, and functions: Exported functions include `nf_reject_skb_v6_tcp_reset()`, `nf_reject_skb_v6_unreach()`, `nf_send_reset6()`, and `nf_send_unreach6()`. Internal helpers validate IPv6 headers, locate/check TCP headers, verify checksums, construct IPv6/TCP/ICMPv6 headers, detect ICMPv6 unreachable loops, fill dsts, and handle bridged RST transmission.

Control flow: Reset generation validates the original IPv6 packet, extracts a non-RST TCP header through extension headers, verifies TCP checksum, builds a reversed IPv6 header, creates a minimal RST header with correct sequence/ack logic, attaches conntrack, marks the original conntrack closing, routes/xfrm-lookups output, and transmits via `ip6_local_out()` or direct bridge xmit when bridge netfilter metadata exists. Unreachable generation avoids replying to an unreachable, clips quoted payload to the IPv6 minimum MTU budget, verifies checksum, builds ICMPv6, computes the checksum, and either returns the skb or sends through `icmpv6_send()`.

State and persistence: No durable state. It mutates generated skbs, may attach conntrack from the original packet, and sets conntrack closing state for TCP resets. It also may temporarily attach a dst to an input skb before calling `icmpv6_send()`.

Dependencies and integration: Depends on IPv6 route/xfrm, checksum helpers, ICMPv6, TCP header parsing, bridge netfilter, conntrack helpers, security flow classification, and reject expression/target modules.

Risks and test signals: Risks include responding to malformed extension-header chains, bad checksum acceptance, RST sequence correctness, bridge MAC header correctness, and route/xfrm failure leaks. Tests should cover TCP SYN/data/RST input, ICMP unreachable suppression, fragmented/non-first packets, extension headers, bridged traffic, local-output rejects, xfrm policy routes, and invalid checksums.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_reject_ipv6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_socket_ipv6.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_socket_ipv6.c

Purpose: Provides slow-path IPv6 socket lookup for netfilter socket matching. It maps packets, including ICMPv6 errors quoting inner TCP/UDP headers, to local TCP/UDP sockets.

Important APIs, types, and functions: `nf_sk_lookup_slow_v6()` is exported. `extract_icmp6_fields()` parses ICMPv6 errors and extracts the quoted inner tuple. `nf_socket_get_sock_v6()` dispatches to `inet6_lookup()` for TCP and `udp6_lib_lookup()` for UDP.

Control flow: The lookup locates the transport header with `ipv6_find_hdr()` and rejects fragmented packets. For TCP/UDP it reads ports directly and computes data offset for TCP. For ICMPv6 it ignores informational messages, parses the quoted IPv6 header and extension headers, accepts only quoted TCP/UDP, and reverses tuple roles because the quoted source is local. If conntrack says the packet is an established/related reply for a completed SNAT flow, it substitutes the original source address/port to find the local socket. It then calls protocol-specific socket lookup using the incoming interface.

State and persistence: No persistent state. It uses conntrack state when present and borrows pointers to header-backed addresses, with a stack copy for quoted IPv6 headers.

Dependencies and integration: Depends on IPv6 header parsing, TCP/UDP hash lookup, conntrack NAT metadata, and netfilter socket match/tproxy users.

Risks and test signals: Risks include tuple reversal mistakes for ICMP errors, NAT reply handling, fragmented packet rejection, and safe header access with non-linear skbs. Tests should cover direct TCP/UDP packets, ICMPv6 errors quoting TCP/UDP, SNAT reply lookup, packets with extension headers, fragments, and missing/truncated headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_socket_ipv6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_tproxy_ipv6.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_tproxy_ipv6.c

Purpose: Implements IPv6 transparent proxy socket helpers for netfilter TPROXY. It selects local addresses, finds listener/established sockets, and handles TCP TIME_WAIT redirection.

Important APIs, types, and functions: Exported helpers are `nf_tproxy_laddr6()`, `nf_tproxy_handle_time_wait6()`, and `nf_tproxy_get_sock_v6()`. Lookups use `inet6_lookup_listener()`, `__inet6_lookup_established()`, and `udp6_lib_lookup()`.

Control flow: `nf_tproxy_laddr6()` returns a user-supplied local address unless it is unspecified; otherwise it scans the ingress device's IPv6 addresses under lock and selects the first non-tentative, non-deprecated address, falling back to the original destination. `nf_tproxy_handle_time_wait6()` parses TCP, and for bare SYNs to TIME_WAIT sockets attempts to find a listener at the proxy local address/port, replacing the TIME_WAIT socket if successful. `nf_tproxy_get_sock_v6()` dispatches TCP listener/established lookups or UDP lookup, then filters UDP results according to connected/wildcard state and requested lookup type.

State and persistence: No persistent module state. It manipulates socket references: listeners returned from listener lookup get a refcount bump, UDP sockets may be `sock_put()` if unsuitable, and TIME_WAIT sockets may be descheduled/released.

Dependencies and integration: Depends on IPv6 address configuration, TCP/UDP socket tables, TPROXY core enums, and ingress device context. Used by xt/nft transparent proxy rule implementations.

Risks and test signals: Risks include incorrect wildcard listener semantics, reference handling, TIME_WAIT replacement, and address selection on devices with tentative/deprecated addresses. Tests should cover TCP listener and established lookup, UDP connected versus wildcard sockets, SYN to TIME_WAIT, unspecified user local address, bound interface behavior, and truncated TCP headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_tproxy_ipv6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/nft_dup_ipv6.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/nft_dup_ipv6.c

Purpose: Registers the IPv6 nftables `dup` expression. The expression duplicates packets to an IPv6 gateway and optional output interface by calling the shared `nf_dup_ipv6()` helper.

Important APIs, types, and functions: `struct nft_dup_ipv6` stores source register numbers for the gateway address and optional device index. `nft_dup_ipv6_eval()` reads registers and invokes `nf_dup_ipv6()`. `nft_dup_ipv6_init()` validates and parses register loads. `nft_dup_ipv6_dump()` serializes expression state. `nft_dup_ipv6_type` registers family `NFPROTO_IPV6`, name `dup`, and netlink policy.

Control flow: Module init registers the expression type. Rule creation requires `NFTA_DUP_SREG_ADDR`; optional `NFTA_DUP_SREG_DEV` is parsed as an integer register. Packet evaluation casts register data to `struct in6_addr`, reads optional oif or `-1`, and duplicates the packet without setting a verdict. Module exit unregisters the expression.

State and persistence: Per-expression state is only the register selectors stored in nftables rule memory. Runtime packet copies are handled by `nf_dup_ipv6()`.

Dependencies and integration: Depends on nftables expression APIs, netlink register encoding, and `nf_dup_ipv6`. Integrates with nft rulesets and uses nft packet info for net namespace and hook number.

Risks and test signals: Risks are register size/type validation, endian/interface index interpretation, and propagation of duplication errors that are intentionally not reflected in verdict. Tests should create rules with/without device register, invalid netlink attributes, link-local gateways requiring oif, and verify original packet verdict flow continues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/nft_dup_ipv6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/nft_fib_ipv6.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/nft_fib_ipv6.c

Purpose: Implements IPv6 nftables `fib` expression evaluation, returning output interface, output interface name, or address type based on IPv6 FIB lookups and nft fib flags.

Important APIs, types, and functions: Exported evaluators are `nft_fib6_eval_type()` and `nft_fib6_eval()`. `nft_fib6_flowi_init()` maps nft flags and packet headers to `flowi6`. `nft_fib6_lookup()` wraps `fib6_lookup()`. Helper functions handle link-local lookup flags, l3mdev master devices, ICMPv6 skip behavior, and multipath sibling device matching. `nft_fib6_select_ops()` chooses expression ops based on requested result.

Control flow: Packet evaluation safely fetches the IPv6 header from the skb. Type evaluation builds a flow for destination or source reverse lookup, includes mark/iif/oif/l3mdev as requested, checks local address on a specific device, calls `fib6_lookup()`, maps reject/anycast/local/multicast/unicast/error cases to route types, and stores the type. Interface evaluation may fast-path `nft_fib_can_skip()`, skips certain unspecified-source ICMPv6 link-local cases, does the lookup, ignores reject/anycast/local routes, then stores either the nexthop device or the requested oif if any sibling route uses it.

State and persistence: Per-expression state is `struct nft_fib` from nft core. Runtime state is a stack `flowi6` and `fib6_result`; results are written to nft registers.

Dependencies and integration: Depends on nftables core, IPv6 FIB/routing, l3mdev, netdevice state, skb marks, and route type constants. Registered as family-specific expression alias `"fib"` for IPv6.

Risks and test signals: Risks include route result mapping differences, link-local oif handling, multipath sibling matching, l3mdev/VRF behavior, and safe skb header access. Tests should cover daddr/saddr lookups, mark-sensitive routing, iif/oif flags, local/anycast/reject routes, link-local destinations, VRFs, multipath, malformed short skbs, and `NFT_FIB_RESULT_*` op selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/nft_fib_ipv6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/nft_reject_ipv6.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/nft_reject_ipv6.c

Purpose: Registers the IPv6 nftables `reject` expression and maps nft reject actions to the IPv6 reject core.

Important APIs, types, and functions: `nft_reject_ipv6_eval()` dispatches based on `struct nft_reject` type. It calls `nf_send_unreach6()` for `NFT_REJECT_ICMP_UNREACH` and `nf_send_reset6()` for `NFT_REJECT_TCP_RST`. The expression type uses generic `nft_reject_init()`, `nft_reject_dump()`, and `nft_reject_validate()`.

Control flow: Module init registers the expression. On packet evaluation, the helper sends the appropriate reject packet when the type is supported, then always sets `regs->verdict.code = NF_DROP`. Unsupported types fall through to drop-only behavior. Module exit unregisters the expression.

State and persistence: Per-expression nft rule state stores reject type/code. No additional module state is kept.

Dependencies and integration: Depends on nftables expression APIs and `nf_reject_ipv6.c`. It integrates with nft chain hooks by using `nft_net()`, `nft_sk()`, `nft_hook()`, and the packet skb.

Risks and test signals: Risks are validation gaps for unsupported reject types, ensuring generated rejects are sent before drop, and correct hook/sk context. Tests should cover ICMPv6 unreachable codes, TCP reset from input/forward/local-output, invalid expression attributes, and packet drop verdict even when reject generation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/nft_reject_ipv6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/output_core.c -->
# sources/distributed-fs/ceph-client/net/ipv6/output_core.c

Purpose: Provides small IPv6 output helpers needed by static components and packet offload paths, including fragment ID selection, first-fragment-option location, and local output entry points.

Important APIs, types, and functions: Exported functions are `ipv6_proxy_select_ident()`, `ipv6_select_ident()`, `ip6_find_1stfragopt()`, `__ip6_local_out()`, and `ip6_local_out()`. `__ipv6_select_ident()` currently returns a random 32-bit ID. `ip6_find_1stfragopt()` scans extension headers and returns where a Fragment header should be inserted.

Control flow: ID helpers read addresses from parameters or skb headers and return a network-order random ID. `ip6_find_1stfragopt()` walks Hop-by-Hop, Routing, and Destination Options headers, respecting Mobile IPv6 HAO and routing-header ordering, and rejects malformed/oversize chains. `__ip6_local_out()` fixes payload length, initializes `IP6CB(skb)->nhoff`, passes through l3mdev output handling, sets protocol, and invokes the local-output netfilter hook with `dst_output` continuation. `ip6_local_out()` calls the lower helper and runs `dst_output()` when netfilter returns pass-through `1`.

State and persistence: No persistent state. It mutates skb payload length, control block next-header offset, protocol, and possibly skb returned by l3mdev processing.

Dependencies and integration: Depends on IPv6 header helpers, l3mdev, netfilter local-output hook, route dst output, and random number generation. It is a central integration point for generated IPv6 packets such as rejects, duplicates, raw sends, and ping.

Risks and test signals: Risks include incorrect extension-header insertion offsets, malformed option chain handling, and local-output hook return handling. Tests should cover header chains with hop/routing/destination options, Mobile IPv6 HAO when enabled, malformed short options, l3mdev enslaved devices, netfilter drop/stolen/pass verdicts, and UFO proxy ID selection on non-linear skbs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/output_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ping.c -->
# sources/distributed-fs/ceph-client/net/ipv6/ping.c

Purpose: Implements IPv6 datagram ping sockets (`SOCK_DGRAM`, `IPPROTO_ICMPV6`) and their proc reporting glue, adapting common ping infrastructure to IPv6 routing, options, and ICMPv6 frame generation.

Important APIs, types, and functions: `ping_v6_sendmsg()` is the send path. `ping_v6_pre_connect()` runs cgroup connect BPF after address length validation. `pingv6_prot` and `pingv6_protosw` register the protocol and socket operations. Proc support provides `/proc/net/icmp6` through seq operations. `pingv6_init()` wires real IPv6 callback functions into `pingv6_ops`; `pingv6_exit()` restores dummy callbacks and unregisters.

Control flow: Send validates the user ICMP header through `ping_common_sendmsg()`, resolves destination from `msg_name` or connected state, chooses output interface from scope, bind, sticky pktinfo, multicast/unicast defaults, rejects mapped/scopeless invalid cases, processes ancillary IPv6 control messages, builds `flowi6` including ICMP type/code and security classification, looks up a route, builds a `pingfakehdr`, selects hop limit, appends data under socket lock using `ip6_append_data()`, then pushes pending frames through `icmpv6_push_pending_frames()` or flushes on error.

State and persistence: Socket state includes normal `inet_sock`/`ipv6_pinfo`, bound device, sticky pktinfo, flow label, corked pending frames, and ping port allocation. Global `pingv6_ops` callback pointers are updated at module/subsystem init and restored on exit. Proc entries are per-net.

Dependencies and integration: Depends on common ping code, IPv6 datagram connect/control/routing, cgroup BPF, ICMPv6, raw IPv6 socket ops, procfs, and pernet lifecycle.

Risks and test signals: Risks include scope/oif validation, control-message option handling, pending-frame cleanup on errors, BPF pre-connect bounds, and callback replacement during init/exit. Tests should cover connected and unconnected sends, link-local scope IDs, multicast oif, ancillary hop-limit/tclass/pktinfo, BPF connect programs, route errors, proc listing, and checksum/sequence correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/proc.c -->
# sources/distributed-fs/ceph-client/net/ipv6/proc.c

Purpose: Implements IPv6 procfs statistics files: `/proc/net/sockstat6`, `/proc/net/snmp6`, and per-device `/proc/net/dev_snmp6/<dev>`.

Important APIs, types, and functions: `sockstat6_seq_show()` reports TCP6/UDP6/RAW6 socket usage and fragment cache usage. SNMP item arrays map visible names to IPv6, ICMPv6, and UDPv6 MIB entries. `snmp6_seq_show_item()`, `snmp6_seq_show_item64()`, and `snmp6_seq_show_icmpv6msg()` render counters. `snmp6_register_dev()` and `snmp6_unregister_dev()` manage per-device proc entries. `ipv6_misc_proc_init()` and `ipv6_misc_proc_exit()` register pernet proc lifecycle.

Control flow: Per-net init creates `sockstat6`, `snmp6`, then `dev_snmp6`, unwinding earlier entries on failure. `snmp6` rendering emits per-net IPv6 stats, ICMPv6 base stats, ICMPv6 message stats, and UDPv6 stats. Device rendering emits `ifIndex`, per-device IPv6 stats, per-device ICMPv6 stats excluding the host rate-limit item, and message stats. Per-net exit removes all entries.

State and persistence: Proc entries are per-net; device entries are stored in `idev->stats.proc_dir_entry`. Counter state lives in per-net/per-device MIB allocations and is only read here. No persistent storage.

Dependencies and integration: Depends on procfs seq APIs, network namespace lifecycle, IPv6 device state, SNMP counter batching helpers, and socket protocol in-use accounting for `tcpv6_prot`, `udpv6_prot`, and `rawv6_prot`.

Risks and test signals: Risks include proc entry lifetime during device/netns teardown, counter batching consistency, missing directories, and name formatting compatibility. Tests should create/destroy netns and IPv6 devices, read all proc files while traffic updates counters, verify failure unwinds with fault injection, and compare output names against expected userspace parsers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/protocol.c -->
# sources/distributed-fs/ceph-client/net/ipv6/protocol.c

Purpose: Maintains IPv6 protocol and offload dispatch tables for next-header handlers and GSO/GRO offload handlers.

Important APIs, types, and functions: `inet6_protos[MAX_INET_PROTOS]` stores RCU pointers to `struct inet6_protocol` handlers when IPv6 is enabled. `inet6_add_protocol()` and `inet6_del_protocol()` atomically install/remove a handler for a protocol number. `inet6_offloads[MAX_INET_PROTOS]` stores `struct net_offload` handlers, with `inet6_add_offload()` and `inet6_del_offload()` providing the same atomic registration pattern.

Control flow: Add operations use `cmpxchg()` to install only into an empty slot and return `0` on success or `-1` if occupied. Delete operations use `cmpxchg()` to clear only if the current pointer matches the caller's pointer, then call `synchronize_net()` so packet readers finish before module memory can disappear.

State and persistence: Global read-mostly RCU arrays hold registered handlers. State exists for kernel lifetime and is modified by protocol/offload modules; no persistent storage.

Dependencies and integration: Depends on RCU/network synchronization and protocol modules such as IPv6 fragment handling, TCP/UDP, and offload providers. Consumers read these tables during packet input and offload processing.

Risks and test signals: Risks are handler slot collisions, deleting the wrong pointer, and missing synchronization causing use-after-free. Tests should cover duplicate add failures, mismatched delete failures, module unload after unregister, packet traversal during unregister, and offload registration symmetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/protocol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/raw.c -->
# sources/distributed-fs/ceph-client/net/ipv6/raw.c

Purpose: Implements IPv6 raw sockets: demultiplexing inbound packets to raw sockets, receiving ICMPv6 errors, sending raw payloads or header-included IPv6 packets, socket options/ioctls, proc reporting, and protocol registration.

Important APIs, types, and functions: `raw_v6_hashinfo` is the raw socket hash table. `raw_v6_match()`, `raw6_local_deliver()`, `raw6_icmp_error()`, and `rawv6_rcv()` are externally relevant receive-path helpers. `rawv6_sendmsg()`, `rawv6_send_hdrinc()`, `rawv6_push_pending_frames()`, `rawv6_recvmsg()`, `rawv6_bind()`, sockopt helpers, and `rawv6_prot` define socket behavior. Optional Mobile IPv6 hooks register `mh_filter`.

Control flow: Inbound delivery hashes by protocol, scans matching sockets under RCU, applies address/device/multicast filters, enforces receive buffer limits, applies ICMPv6 or MH filters, clones the skb, and queues through `rawv6_rcv()`. Receive validates xfrm policy, resets conntrack, handles checksum state including raw checksum offsets, then queues to the socket. `recvmsg` handles error queue and PMTU notifications, copies/csum-validates data, fills `sockaddr_in6`, and emits control messages.

Send flow: `rawv6_sendmsg()` validates address/protocol/scope and flow label, processes control messages/options, selects source/destination/final destination, classifies security flow, looks up route, handles `MSG_CONFIRM`/`MSG_PROBE`, and either sends a user-supplied IPv6 header through `rawv6_send_hdrinc()` or appends data with `ip6_append_data()` and pushes pending frames with checksum insertion. Header-included send allocates an skb, copies the full packet from userspace, sets metadata, applies l3mdev output, and sends via local-output netfilter.

State and persistence: Per-socket state includes raw checksum enable/offset, ICMPv6 filter bitmap, bound device/address, IPv6 options, corked write queue, and drop counters. Global state includes the raw hash table and optional MH filter pointer. Proc entries are per-net when enabled.

Dependencies and integration: Depends on IPv6 routing/output, datagram controls, xfrm policy, netfilter local-output, raw socket common code, multicast membership checks, ICMPv6 error conversion, IPv6 mroute ioctls, procfs, and protocol switch registration.

Risks and test signals: High-risk areas include checksum offset validation/insertion across fragmented corked skbs, HDRINCL MTU and userspace header handling, scope/bind validation, RCU socket traversal, MH filter lifetime, and error queue semantics. Tests should cover ICMPv6 filter masks, checksum offsets including invalid odd/too-large values, HDRINCL sends, corked multi-fragment sends, PMTU/redirect errors, multicast delivery, bound-device matching with sdif, proc listing, compat ioctls, and concurrent socket close during delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/raw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/reassembly.c -->
# sources/distributed-fs/ceph-client/net/ipv6/reassembly.c

Purpose: Implements core IPv6 fragment reassembly for normal IPv6 input. It registers the Fragment header protocol handler, manages per-net fragment queues and sysctls, validates RFC 8200 fragment rules, reassembles completed datagrams, and reports errors/stats.

Important APIs, types, and functions: `ip6_frags` is the global `inet_frags` cache. `ipv6_frag_rcv()` is the `inet6_protocol` handler for `IPPROTO_FRAGMENT`. `fq_find()`, `ip6_frag_queue()`, and `ip6_frag_reasm()` manage queue lookup, fragment insertion, and reassembly. `ipv6_frag_init()` and `ipv6_frag_exit()` register the cache, protocol, sysctls, and pernet fragment directories. Sysctl helpers expose `ip6frag_high_thresh`, `ip6frag_low_thresh`, `ip6frag_time`, and deprecated `ip6frag_secret_interval`.

Control flow: `ipv6_frag_rcv()` rejects already reassembled packets, increments reassembly request stats, rejects jumbo payloads and short fragment headers, fast-paths atomic fragments by advancing transport header and marking `IP6SKB_FRAGMENTED`, validates that the first fragment contains all headers through an upper-layer header, finds the per-net queue, and calls `ip6_frag_queue()` under lock. Queueing validates offset/end bounds, ECN, checksum adjustment, final-fragment consistency, 8-byte alignment, non-empty payload, trimming, overlap/duplicate insertion, memory accounting, max size, first-fragment nhoffset, and completion. `ip6_frag_reasm()` removes the Fragment header, shifts headers, finishes generic reassembly, updates payload length, ECN, `IP6CB`, stats, and returns `1` so the protocol dispatch continues.

State and persistence: Per-net `net->ipv6.fqdir` stores active fragment queues, thresholds, timeout, and sysctl header. Each queue tracks fragment tree/tail, length, meat, ECN, max size, input interface, timestamps, and next-header offset. State is volatile and expires by timer or netns teardown.

Dependencies and integration: Uses generic `inet_frags`, IPv6 protocol dispatch tables, ICMPv6 parameter-problem generation, SNMP stats, sysctl, checksum helpers, RCU, and pernet lifecycle. It complements but is distinct from netfilter conntrack reassembly.

Risks and test signals: High-risk areas include overlap/drop behavior, ICMP pointer correctness for malformed fragments, atomic fragment handling, ECN merge failure, memory accounting, stat increments, and queue lifetime on namespace exit. Tests should cover complete reassembly, out-of-order fragments, duplicates, overlaps, non-8-byte non-final fragments, oversize payloads, truncated first fragments, atomic fragments, timeout expiry, sysctl threshold changes, link-local/multicast iif keying, and concurrent namespace teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/reassembly.c -->
