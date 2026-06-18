# subset-b-006254

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_connmark.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_connmark.c

## Purpose
`xt_connmark.c` implements the x_tables `CONNMARK` target and `connmark` match. It copies, sets, saves, restores, and tests marks stored on `struct nf_conn`, allowing packet classification state to persist across packets in the same connection.

## Important APIs, Types, and Functions
The core target path is `connmark_tg_shift()`, wrapped by revision-specific `connmark_tg()` and `connmark_tg_v2()`. It consumes `struct xt_connmark_tginfo1` or `struct xt_connmark_tginfo2`, supports `XT_CONNMARK_SET`, `XT_CONNMARK_SAVE`, and `XT_CONNMARK_RESTORE`, and uses `ctmark`, `ctmask`, `nfmask`, `shift_dir`, and `shift_bits`. The match path is `connmark_mt()` using `struct xt_connmark_mtinfo1`. Registration happens through `connmark_tg_reg[]` and `connmark_mt_reg`.

## Control Flow, State, and Persistence
On each target invocation, `nf_ct_get()` retrieves the connection. Missing conntrack state leaves the packet untouched with `XT_CONTINUE`. SET rewrites `ct->mark` from the configured constant and mask, SAVE copies selected `skb->mark` bits into `ct->mark`, and RESTORE copies selected `ct->mark` bits back into `skb->mark`. Revision 2 optionally shifts the selected value before storage or restoration. Connection mark updates use `READ_ONCE()`/`WRITE_ONCE()` and emit `nf_conntrack_event_cache(IPCT_MARK, ct)` when the persistent conntrack mark changes.

## Dependencies and Integration Points
The module depends on conntrack namespace enablement through `nf_ct_netns_get()` and releases it through `nf_ct_netns_put()` in target and match destructors. It integrates with IPv4 and optional IPv6 iptables aliases and with conntrack event listeners that observe mark changes.

## Risks and Test Signals
Risks include mask/xor semantics being misunderstood as assignment, shifts losing bits before masks are applied, missing conntrack making targets no-ops, and concurrent readers observing only best-effort mark updates. Tests should cover SET/SAVE/RESTORE, all masks, both shift directions, IPv4 and IPv6 registration, no-conntrack packets, event emission on changed marks only, and inverted `connmark` matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_connmark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_conntrack.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_conntrack.c

## Purpose
`xt_conntrack.c` is the full-featured x_tables conntrack match. It matches connection state, direction, NAT status, original and reply tuples, protocol, ports, and expiration time, subsuming the simpler `state` match.

## Important APIs, Types, and Functions
`conntrack_mt()` is the shared matcher for revisions 1, 2, and 3 via `conntrack_mt_v1()`, `conntrack_mt_v2()`, and `conntrack_mt_v3()`. It consumes `struct xt_conntrack_mtinfo1`, `xt_conntrack_mtinfo2`, or `xt_conntrack_mtinfo3`. Helpers include `conntrack_addrcmp()`, `conntrack_mt_origsrc()`, `conntrack_mt_origdst()`, `conntrack_mt_replsrc()`, `conntrack_mt_repldst()`, `ct_proto_port_check()`, `ct_proto_port_check_v3()`, and `port_match()`.

## Control Flow, State, and Persistence
The match first calls `nf_ct_get()` and maps the result to `XT_CONNTRACK_STATE_BIT()`, `XT_CONNTRACK_STATE_UNTRACKED`, or `XT_CONNTRACK_STATE_INVALID`. When state matching is enabled it augments the state mask with SNAT/DNAT bits from `ct->status`. If no `nf_conn` exists, only state-only matches can succeed. Otherwise it checks direction via `CTINFO2DIR()`, masked original/reply addresses, protocol and ports, status bits, and `nf_ct_expires(ct) / HZ`. Revision 3 adds port ranges; older revisions compare exact tuple ports.

## Dependencies and Integration Points
The module pins conntrack support per network namespace and family through `nf_ct_netns_get()`/`nf_ct_netns_put()`. It reads `struct nf_conn` tuple hashes, status bits, protocol number, and expiration state, and registers an NFPROTO_UNSPEC match so the same code serves IPv4 and IPv6.

## Risks and Test Signals
Risks include inversion logic on every match flag, invalid/untracked state handling, IPv6 mask comparisons, byte-order differences between revision 2 exact ports and revision 3 port ranges, and expiration granularity in seconds. Tests should cover invalid, untracked, new, established, related, SNAT, DNAT, original/reply tuple matches, inverted address/status/protocol/port checks, IPv6 masks, v3 ranges, no-conntrack packets, and namespace teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_conntrack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_cpu.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_cpu.c

## Purpose
`xt_cpu.c` provides the `cpu` match, letting rules match the CPU currently processing the packet. It is intended for steering traffic across workers when RPS, IRQ affinity, or multiqueue NIC layouts make CPU selection meaningful.

## Important APIs, Types, and Functions
`cpu_mt()` compares `struct xt_cpu_info.cpu` with `smp_processor_id()`. `cpu_mt_check()` rejects unknown invert bits. `cpu_mt_reg` registers an NFPROTO_UNSPEC revision 0 match.

## Control Flow, State, and Persistence
There is no persistent state. Rule insertion validates `invert` as a single-bit boolean. Packet evaluation returns `(info->cpu == smp_processor_id()) ^ info->invert`.

## Dependencies and Integration Points
The module depends only on x_tables and per-CPU execution context. It can be used for IPv4 and IPv6 because registration is protocol-unspecified.

## Risks and Test Signals
Risks are operational rather than structural: CPU affinity can change with RPS, NAPI migration, softirq scheduling, or virtualization, so rule behavior may not map directly to ingress queue identity. Tests should pin traffic to known CPUs, validate inversion, reject malformed invert flags, and exercise IPv4 and IPv6 rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_dccp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_dccp.c

## Purpose
`xt_dccp.c` implements the deprecated `dccp` match for DCCP packets. It matches source and destination port ranges, DCCP packet type masks, and optional DCCP option presence.

## Important APIs, Types, and Functions
`dccp_mt()` is the match function. `dccp_find_option()` parses options using a global `dccp_optbuf` protected by `dccp_buflock`. `match_types()` and `match_option()` implement type and option subchecks. `dccp_mt_check()` validates `XT_DCCP_VALID_FLAGS` and inversion flags. `dccp_mt_reg[]` registers IPv4 and IPv6 matches with `.proto = IPPROTO_DCCP`.

## Control Flow, State, and Persistence
Fragments are rejected. The DCCP base header is read with `skb_header_pointer()`, and missing or malformed headers set `par->hotdrop`. Port, type, and option predicates are gated by `info->flags` and inverted by `info->invflags`. Option parsing uses `dh->dccph_doff` to derive the option span and walks one-byte and length-bearing options safely.

## Dependencies and Integration Points
The module depends on x_tables, IPv4/IPv6 iptables registration, `linux/dccp.h`, and skb header access helpers. `dccp_mt_init()` allocates the option buffer, warns once that the match is scheduled for removal in 2027, then registers both matches.

## Risks and Test Signals
Risks include option-length parsing on malformed packets, global option buffer contention, hotdrop behavior for truncated headers, and deprecation/removal impact on userspace rules. Tests should cover all flag combinations, invalid invflags, fragments, short headers, bogus data offsets, option search with one-byte and variable-length options, IPv4/IPv6 registration, allocation failure, and module unload freeing `dccp_optbuf`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_dccp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_devgroup.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_devgroup.c

## Purpose
`xt_devgroup.c` implements matching by Linux network device group for input and output interfaces. It supports policy based on administrative grouping rather than interface names.

## Important APIs, Types, and Functions
`devgroup_mt()` checks `xt_in(par)` and `xt_out(par)` against `struct xt_devgroup_info`. `devgroup_mt_check_hooks()` rejects rules whose requested direction is impossible for the hook mask, and `devgroup_mt_checkentry()` validates flags before delegating to the hook checker.

## Control Flow, State, and Persistence
The match checks requested input and output group fields independently. For each enabled side, it requires the corresponding device pointer to exist and compares `dev->group` masked by `src_mask` or `dst_mask`, applying `XT_DEVGROUP_INVERT_SRC` or `XT_DEVGROUP_INVERT_DST`. No state is persisted.

## Dependencies and Integration Points
The module integrates with x_tables hook metadata and `struct net_device.group`. It registers one NFPROTO_UNSPEC match with IPv4 and IPv6 aliases.

## Risks and Test Signals
Risks include hook misuse, missing device pointers in local paths, and masks accidentally matching broad groups. Tests should cover PREROUTING/INPUT source-side matching, OUTPUT/POSTROUTING destination-side matching, FORWARD both-side matching, invalid flags, unsupported hook masks, inversion, and device group changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_devgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_dscp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_dscp.c

## Purpose
`xt_dscp.c` implements DSCP and legacy TOS field matches for IPv4 and IPv6. It lets rules classify packets by differentiated-services or TOS bits in the IP header.

## Important APIs, Types, and Functions
`dscp_mt()` and `dscp_mt6()` compare IPv4 `ip_hdr(skb)->tos >> XT_DSCP_SHIFT` and IPv6 `ipv6_get_dsfield(ipv6_hdr(skb)) >> XT_DSCP_SHIFT` against `struct xt_dscp_info`. `tos_mt()` compares masked TOS through `struct xt_tos_match_info`. `dscp_mt_check()` rejects DSCP values above `XT_DSCP_MAX`.

## Control Flow, State, and Persistence
There is no persistent state. Packet evaluation reads the already-parsed network header, extracts DSCP or TOS, compares against configured values, and applies inversion.

## Dependencies and Integration Points
The module registers `dscp` matches for IPv4 and IPv6 plus a protocol-unspecified `tos` match. It uses x_tables, IPv4/IPv6 header helpers, and userspace UAPI match structures.

## Risks and Test Signals
Risks include confusing DSCP values with full TOS/traffic-class bytes, IPv6 traffic-class extraction, and invalid userspace DSCP values. Tests should cover all DSCP edge values, ECN bits not affecting DSCP comparison, TOS masks, inversion, IPv4 and IPv6 packets, and checkentry rejection of out-of-range DSCP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_dscp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_ecn.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_ecn.c

## Purpose
`xt_ecn.c` implements ECN matching for IPv4 and IPv6. It can match IP-layer ECN codepoints and TCP ECE/CWR flags.

## Important APIs, Types, and Functions
`match_tcp()` reads a TCP header and checks `XT_ECN_OP_MATCH_ECE` and `XT_ECN_OP_MATCH_CWR`. `match_ip()` and `match_ipv6()` compare ECN bits in IPv4 TOS or IPv6 traffic class. `ecn_mt4()` and `ecn_mt6()` combine those checks. `ecn_mt_check4()` and `ecn_mt_check6()` validate operation masks and require TCP protocol when TCP flag matching is requested.

## Control Flow, State, and Persistence
Packet evaluation first checks TCP flags if requested, using `skb_header_pointer()` and hotdropping truncated TCP headers. Then it checks the IP ECN bits when requested. All configured checks must succeed. The module stores no packet or rule state beyond the rule data.

## Dependencies and Integration Points
The module depends on x_tables, IPv4/IPv6 iptables entries for protocol validation, TCP header definitions, and traffic-class helpers. It registers family-specific `ecn` matches.

## Risks and Test Signals
Risks include allowing TCP flag matching without `-p tcp`, mishandling fragments or truncated TCP headers, and mixing ECN codepoints with DSCP bits. Tests should cover CE/ECT0/ECT1/not-ECT values, ECE/CWR combinations, non-TCP rules rejected when TCP checks are requested, IPv6 extension-header thoff behavior from x_tables, inversion by absence of options, and hotdrop on short TCP headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_ecn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_esp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_esp.c

## Purpose
`xt_esp.c` implements the `esp` match for IPsec ESP packets. It matches the ESP Security Parameters Index against a configured range.

## Important APIs, Types, and Functions
`esp_mt()` reads `struct ip_esp_hdr` at `par->thoff` and calls `spi_match()` for range and inversion logic. `esp_mt_check()` validates inversion flags. `esp_mt_reg[]` registers IPv4 and IPv6 matches with `.proto = IPPROTO_ESP`.

## Control Flow, State, and Persistence
The matcher rejects non-initial fragments, reads the ESP header through `skb_header_pointer()`, hotdrops truncated headers, converts SPI to host order, then checks `spis[0] <= spi <= spis[1]` with `XT_ESP_INV_SPI`. It persists no state.

## Dependencies and Integration Points
The module depends on x_tables, IPv4/IPv6 registration, and the IPsec ESP header definitions. It is a parser-only match; actual IPsec policy and state are handled elsewhere by xfrm.

## Risks and Test Signals
Risks include truncated ESP headers, fragment handling, endian errors on SPI, and rule confusion between ESP SPI and xfrm policy. Tests should cover SPI range boundaries, inverted ranges, fragments, tiny packets with hotdrop, IPv4/IPv6 rules, and invalid inversion flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_esp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_hashlimit.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_hashlimit.c

## Purpose
`xt_hashlimit.c` implements the stateful `hashlimit` match: a per-key token-bucket or rate-window limiter where keys can include source/destination address and source/destination port. It supports IPv4 and optional IPv6, packet and byte modes, multiple UAPI revisions, and `/proc/net/{ipt_hashlimit,ip6t_hashlimit}` visibility.

## Important APIs, Types, and Functions
Key state types are `struct hashlimit_net`, `struct dsthash_dst`, `struct dsthash_ent`, and `struct xt_hashlimit_htable`. Table lifecycle is handled by `htable_create()`, `htable_find_get()`, `htable_put()`, `htable_gc()`, and `htable_selective_cleanup()`. Entry lifecycle uses `dsthash_find()`, `dsthash_alloc_init()`, and `dsthash_free()`. Rate accounting is in `rateinfo_init()`, `rateinfo_recalc()`, `user2credits()`, `user2credits_byte()`, `user2rate()`, and `hashlimit_byte_cost()`. Packet matching is in `hashlimit_init_dst()` and `hashlimit_mt_common()`, wrapped by revision-specific match/check/destroy functions.

## Control Flow, State, and Persistence
Rule insertion validates masks, mode bits, intervals, overflow limits, and proc names, then reuses or creates a named table in the current net namespace. Table size defaults from RAM, is capped by `HASHLIMIT_MAX_SIZE`, and owns an RCU hash array plus deferrable garbage-collection work. Packet evaluation builds a masked key from requested IPv4/IPv6 addresses and ports, rejects non-first fragments when port hashing is needed, looks up or allocates a locked entry, refreshes expiry, recalculates credit/window state, then returns under-limit or over-limit according to `XT_HASHLIMIT_INVERT`.

## Dependencies and Integration Points
The module integrates with x_tables, per-net generic storage, procfs seq files, RCU hlist traversal, jhash, random hash seeds, slab allocation, delayed work, and IPv4/IPv6 extension-header helpers. `/proc` seq output reports expiry and rate state for each bucket using revision-appropriate display logic.

## Risks and Test Signals
High-risk areas are concurrent entry creation, RCU deletion, delayed-work teardown, overflow-prone credit conversion, byte-mode refill semantics, rate-match window math, IPv6 prefix masking, port hashing with fragments, and named table sharing across rules. Tests should cover revisions 1/2/3, packet and byte modes, rate-match interval behavior, burst handling, table reuse/refcounting, max/size clamps, proc creation/removal and seq reads, IPv4/IPv6 masks, fragmented packets causing hotdrop when ports are required, GC expiry, namespace teardown, and allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_hashlimit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_helper.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_helper.c

## Purpose
`xt_helper.c` implements matching on the conntrack helper assigned to a connection, allowing firewall rules to identify flows handled by helpers such as FTP or SIP.

## Important APIs, Types, and Functions
`helper_mt()` is the match function and `helper_mt_check()`/`helper_mt_destroy()` manage conntrack namespace references. The matcher uses `nf_ct_get()`, `nfct_help()`, and RCU dereferencing of `help->helper`. Rule data is `struct xt_helper_info`.

## Control Flow, State, and Persistence
The match retrieves the packet's connection, obtains helper extension state, and reads the assigned helper under RCU. If a helper name is configured, it compares the helper name with the requested string; otherwise it tests for helper presence. The configured invert bit flips the result. The module persists no helper state itself.

## Dependencies and Integration Points
It depends on conntrack helper infrastructure and x_tables registration. Checkentry pins conntrack support for the rule family so helper metadata is available while rules exist.

## Risks and Test Signals
Risks include helper assignment changes under RCU, null helper extensions, namespace reference leaks, and user expectation mismatch when automatic helper assignment is disabled. Tests should cover helper present/absent, exact helper names, inversion, no-conntrack packets, IPv4/IPv6 registration, and rule unload refcount release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_hl.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_hl.c

## Purpose
`xt_hl.c` implements IPv4 TTL and IPv6 Hop Limit matching. It supports equality, less-than, and greater-than comparisons against the packet header hop-count field.

## Important APIs, Types, and Functions
`ttl_mt()` handles IPv4 and `hl_mt6()` handles IPv6, both consuming `struct xt_hl_info`. `ttl_mt_check()` and `hl_mt6_check()` validate comparison mode. `hl_mt_reg[]` registers `ttl` for IPv4 and `hl` for IPv6.

## Control Flow, State, and Persistence
Each packet path reads the TTL or hop-limit byte from the network header and applies `XT_HL_EQ`, `XT_HL_NE`, `XT_HL_LT`, or `XT_HL_GT` style mode semantics as encoded by the UAPI. There is no persistent state.

## Dependencies and Integration Points
The module integrates with x_tables and IP header helpers. It is often paired with TTL/HL mangling targets elsewhere, but this file only matches.

## Risks and Test Signals
Risks are simple boundary and mode errors: TTL zero, 255, unsupported modes, and IPv4/IPv6 name differences. Tests should cover equality, not-equal/inverted mode, less-than, greater-than, invalid mode rejection, and both families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_hl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_ipcomp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_ipcomp.c

## Purpose
`xt_ipcomp.c` implements the `ipcomp` match for IP Payload Compression Protocol packets. It matches the Compression Parameter Index range.

## Important APIs, Types, and Functions
`comp_mt()` reads `struct ip_comp_hdr` and calls `cpi_match()` against `struct xt_ipcomp`. `comp_mt_check()` validates inversion flags. Registration covers IPv4 and IPv6 with `.proto = IPPROTO_COMP`.

## Control Flow, State, and Persistence
Non-initial fragments are ignored. The IPComp header is fetched with `skb_header_pointer()`, missing headers hotdrop the packet, and CPI is compared in host order against `spis[0]` and `spis[1]` with optional inversion. No state is stored.

## Dependencies and Integration Points
The module depends on x_tables, IPv4/IPv6 protocol registration, and IPComp header definitions. It complements but does not inspect xfrm policy or decompression state.

## Risks and Test Signals
Risks include truncation hotdrops, endian mistakes on CPI, fragments hiding the header, and confusion with ESP SPI matching. Tests should cover CPI boundaries, inversion, fragments, short headers, IPv4/IPv6, and invalid inversion flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_ipcomp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_iprange.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_iprange.c

## Purpose
`xt_iprange.c` implements source and destination IP address range matching for IPv4 and IPv6. It lets iptables rules match inclusive address intervals without requiring prefix-shaped masks.

## Important APIs, Types, and Functions
`iprange_mt4()` compares IPv4 source/destination addresses with `struct xt_iprange_mtinfo`. `iprange_mt6()` performs IPv6 comparisons using `memcmp()` over `struct in6_addr`. Registration is in `iprange_mt_reg[]`.

## Control Flow, State, and Persistence
The match checks each enabled flag independently: source range, destination range, and their inversion bits. IPv4 addresses are converted with `ntohl()` for numeric range comparison; IPv6 addresses use lexicographic network-byte-order comparison. The module keeps no state.

## Dependencies and Integration Points
It integrates with x_tables, IPv4/IPv6 header access, and UAPI range structures. It is protocol-family-specific because address width differs.

## Risks and Test Signals
Risks include IPv6 lexicographic range assumptions, inclusive boundary handling, inverted source/destination logic, and invalid ranges supplied by userspace. Tests should cover min, max, inside, outside, inverted checks, IPv4 endian boundaries, IPv6 low/high byte transitions, and source plus destination combined rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_iprange.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_ipvs.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_ipvs.c

## Purpose
`xt_ipvs.c` implements matching on Linux IPVS connection metadata. It lets firewall rules identify packets associated with virtual services, real servers, forwarding methods, and IPVS connection direction.

## Important APIs, Types, and Functions
The match path is `ipvs_mt()`, driven by `struct xt_ipvs_mtinfo`. It uses IPVS lookup helpers to find an `struct ip_vs_conn`, tests flags such as virtual address, virtual port, protocol, direction, method, and vport control, and releases IPVS connection references after evaluation. `ipvs_mt_check()` validates unsupported flags and family constraints.

## Control Flow, State, and Persistence
For each packet, the matcher asks IPVS whether the skb belongs to an IPVS connection in the configured direction. It then compares requested service tuple fields and method bits, applying inversion as encoded in the rule. The module itself persists no connection state; it observes IPVS-owned connection entries.

## Dependencies and Integration Points
It depends on IPVS being enabled, x_tables, IPv4/IPv6 address handling, and IPVS connection reference management. It is an integration bridge between iptables filtering and the IP virtual server load-balancing subsystem.

## Risks and Test Signals
Risks include stale assumptions about IPVS hook timing, connection reference leaks, mismatched direction flags, IPv4/IPv6 tuple comparison errors, and behavior when IPVS is not loaded or no connection exists. Tests should cover inbound and outbound IPVS packets, no-IPVS packets, virtual service address/port/protocol, real-server direction, forwarding method flags, inversion, IPv6 service tuples, and module dependency loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_ipvs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_l2tp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_l2tp.c

## Purpose
`xt_l2tp.c` implements matching for L2TP headers carried over UDP or directly over IP. It supports L2TPv2 and L2TPv3 fields such as tunnel id, session id, version, type, and optional sequence numbers.

## Important APIs, Types, and Functions
`struct l2tp_data` is the parsed temporary view. `l2tp_udp_mt()` parses UDP-encapsulated L2TP, `l2tp_ip_mt()` parses direct L2TP/IP, and `l2tp_mt4()`/`l2tp_mt6()` dispatch by family and protocol. `l2tp_match()` compares parsed data with `struct xt_l2tp_info`. `l2tp_mt_check()`, `l2tp_mt_check4()`, and `l2tp_mt_check6()` validate flags, hooks, and protocol rule requirements.

## Control Flow, State, and Persistence
The packet path rejects fragments, fetches UDP or L2TP headers with skb helpers, validates version-specific layouts, parses v2 flags and optional Ns/Nr fields, parses v3 session/tunnel identifiers, then applies enabled comparisons with inversion. Checkentry requires the enclosing iptables rule to specify UDP or L2TPIP and rejects v2 direct-IP mode. There is no persistent module state.

## Dependencies and Integration Points
The module depends on x_tables, IPv4/IPv6 iptables entry metadata, UDP headers, L2TP protocol constants, and hook masks for PREROUTING, INPUT, OUTPUT, and FORWARD.

## Risks and Test Signals
Risks include variable header length parsing, truncated UDP payloads, version confusion between v2 and v3, direct-IP restrictions, and sequence-field presence handling. Tests should cover UDP and direct-IP L2TPv3, L2TPv2 over UDP, fragments, short headers, tunnel/session id matching, flags and inversion, missing protocol rules rejected at checkentry, and IPv6 paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_l2tp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_length.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_length.c

## Purpose
`xt_length.c` implements matching on packet length. It supports IPv4 total length and IPv6 payload plus header length semantics for layer 3 packet size.

## Important APIs, Types, and Functions
`length_mt()` handles IPv4, `length_mt6()` handles IPv6, both consuming `struct xt_length_info`. `length_mt_reg[]` registers family-specific `length` matches.

## Control Flow, State, and Persistence
The matcher compares the packet length against configured `min` and `max` bounds and applies inversion. It stores no state and performs no allocation.

## Dependencies and Integration Points
It depends on x_tables and packet header length fields supplied by skb/IP header state. It is family-specific because IPv4 and IPv6 expose lengths differently.

## Risks and Test Signals
Risks include off-by-one boundary behavior, IPv6 length interpretation, and differences between skb length and IP total length under offloads or extension headers. Tests should cover exact min/max, below/above range, inversion, IPv4 total length, IPv6 payload length plus header, and malformed packets already rejected by earlier hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_length.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_limit.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_limit.c

## Purpose
`xt_limit.c` implements the classic global token-bucket `limit` match. It rate-limits matches for a rule, not per source or destination.

## Important APIs, Types, and Functions
`struct xt_limit_priv` stores spinlock-protected `prev` and `credit`. `limit_mt()` performs token accounting using `struct xt_rateinfo`. `user2credits()` converts userspace rates into internal credit units. `limit_mt_check()` allocates and initializes private state; `limit_mt_destroy()` frees it. Compat handlers translate 32-bit userspace layouts.

## Control Flow, State, and Persistence
On rule insertion, checkentry validates burst and overflow conditions, allocates `xt_limit_priv`, and initializes credit to the burst cap. Packet evaluation locks the private state, refills credit from elapsed jiffies up to `credit_cap`, and if enough credit is available subtracts `cost` and matches. The state persists for the life of the rule.

## Dependencies and Integration Points
The module integrates with x_tables match lifecycle and compat translation for mixed 32/64-bit userspace. It uses kernel jiffies and a per-rule spinlock.

## Risks and Test Signals
Risks include arithmetic overflow in rate conversion, compat pointer layout errors, rule sharing expectations, and jiffies wrap behavior. Tests should cover low and high rates, burst exhaustion and refill, SMP contention, compat from/to user conversion, destroy cleanup, invalid overflow inputs, and IPv4/IPv6 aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_limit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_mac.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_mac.c

## Purpose
`xt_mac.c` implements source MAC address matching for Ethernet-like packets.

## Important APIs, Types, and Functions
`mac_mt()` compares the skb's Ethernet source address with `struct xt_mac_info.srcaddr`. `mac_mt_reg[]` registers `mac` for IPv4 and IPv6 families.

## Control Flow, State, and Persistence
The matcher requires the packet to have a link-layer header and an Ethernet header. It compares `eth_hdr(skb)->h_source` to the configured address and applies inversion. No state is persisted.

## Dependencies and Integration Points
The module depends on x_tables, skb MAC header validity, and Ethernet header layout. It is meaningful primarily in ingress hooks where the original L2 source is present.

## Risks and Test Signals
Risks include using the match in hooks where MAC headers are absent or rewritten, non-Ethernet devices, and bridged/tunneled traffic expectations. Tests should cover matching and inverted MACs, no MAC header, short headers, IPv4/IPv6 aliases, and ingress versus local-output behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_mark.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_mark.c

## Purpose
`xt_mark.c` implements packet mark manipulation and matching. It provides the `MARK` target for `skb->mark` updates and the `mark` match for testing mark values.

## Important APIs, Types, and Functions
`mark_tg()` updates `skb->mark` using `struct xt_mark_tginfo2.mark` and `mask`. `mark_mt()` compares `(skb->mark & mask)` to the configured mark with optional inversion. `mark_tg_reg[]` registers target aliases for IPv4, IPv6, and ARP; `mark_mt_reg` registers the protocol-unspecified match.

## Control Flow, State, and Persistence
The target computes `(skb->mark & ~mask) ^ mark`, writes it to the skb, and continues traversal. The match reads the current mark and compares selected bits. Packet marks persist with the skb through later hooks and routing decisions but are not connection-persistent unless other modules save them.

## Dependencies and Integration Points
It integrates with routing, tc, policy routing, connmark, and other subsystems that consume `skb->mark`. Registration covers multiple x_tables families.

## Risks and Test Signals
Risks include xor/mask semantics, interactions with route lookup timing, mark overwrite order across tables, and ARP versus IP family differences. Tests should cover masked set, clear, toggled-looking cases, match inversion, multiple rules in sequence, IPv4/IPv6/ARP targets, and interaction with connmark save/restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_mark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_multiport.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_multiport.c

## Purpose
`xt_multiport.c` implements matching multiple TCP, UDP, UDP-Lite, SCTP, or DCCP ports in one rule, including optional port ranges in newer revisions.

## Important APIs, Types, and Functions
`ports_match_v0()`, `ports_match_v1()`, and the shared match functions evaluate `struct xt_multiport`, `xt_multiport_v1`, and protocol ports read from the transport header. `multiport_mt_check()` and `multiport_mt6_check()` validate that the enclosing rule protocol is one of the supported L4 protocols. `multiport_mt_reg[]` registers revisions for IPv4 and IPv6.

## Control Flow, State, and Persistence
Fragments are ignored because transport ports may be absent. The matcher reads source and destination ports, then evaluates the configured mode: source ports, destination ports, or either. Revision 1 supports ranges encoded by pflags. No state is persisted.

## Dependencies and Integration Points
It depends on x_tables, IPv4/IPv6 iptables rule metadata for protocol checks, `skb_header_pointer()`, and common transport header layouts where the first four bytes are source/destination ports.

## Risks and Test Signals
Risks include malformed port arrays, missing `-p` protocol checks, range encoding mistakes, fragment behavior, and protocol families with similar port layouts but different parser assumptions. Tests should cover TCP/UDP/UDPLite/SCTP/DCCP, source/destination/either modes, ranges, maximum port count, invalid protocols rejected, fragments, truncated transport headers, and inversion by surrounding rule semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_multiport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_nat.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_nat.c

## Purpose
`xt_nat.c` implements legacy x_tables `SNAT` and `DNAT` targets backed by nf_nat. It translates userspace NAT range structures into `nf_nat_range2` and invokes core NAT setup.

## Important APIs, Types, and Functions
`xt_nat_checkentry_v0()` and `xt_nat_checkentry()` acquire NAT hook support. `xt_nat_destroy()` releases it. `xt_nat_convert_range()` converts `struct nf_nat_ipv4_range` to `struct nf_nat_range2`. Target functions include IPv4 and IPv6 SNAT/DNAT variants for revision 0 and current revision, all registered in `xt_nat_target_reg[]`.

## Control Flow, State, and Persistence
Rule insertion enables NAT for the family and hook. On the first packet of a conntrack flow, target functions pass the configured range and manipulation direction to `nf_nat_setup_info()`. NAT state then persists in conntrack for subsequent packets; this file does not maintain separate tables.

## Dependencies and Integration Points
The module integrates with nf_nat, conntrack, x_tables targets, IPv4 and IPv6 NAT range UAPIs, and hook restrictions for source versus destination NAT. It is compatibility glue for iptables NAT semantics.

## Risks and Test Signals
Risks include hook misuse, revision 0 range conversion, IPv4/IPv6 range differences, missing conntrack/NAT support, and applying NAT after connection state is already committed. Tests should cover SNAT and DNAT in valid hooks, invalid hooks rejected, IPv4 revision 0 conversion, IPv6 ranges, persistent translation across flow packets, namespace cleanup, and failure paths in NAT support acquisition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_nat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_nfacct.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_nfacct.c

## Purpose
`xt_nfacct.c` implements the `nfacct` match, which attaches packet and byte accounting to named nfnetlink accounting objects.

## Important APIs, Types, and Functions
`nfacct_mt()` accounts matching packets through the object stored in `struct xt_nfacct_match_info`. `nfacct_mt_checkentry()` looks up and pins an accounting object by name, and `nfacct_mt_destroy()` releases it. Registration is via `nfacct_mt_reg`.

## Control Flow, State, and Persistence
Rule insertion resolves the configured accounting object and stores the pointer in match info. Every packet reaching the rule updates that object's packet and byte counters and returns true. Counters persist in nfnetlink accounting state, not in this module.

## Dependencies and Integration Points
The file depends on x_tables and `nfnetlink_acct`. It bridges iptables rule traversal with named accounting objects visible through nfnetlink tooling.

## Risks and Test Signals
Risks include missing accounting objects, refcount leaks, counter width/overflow expectations, and namespace object lifetime. Tests should cover successful lookup, missing object rejection, packet and byte increments, concurrent packets, destroy release, and IPv4/IPv6 protocol-unspecified use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_nfacct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_osf.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_osf.c

## Purpose
`xt_osf.c` implements passive operating-system fingerprint matching. It delegates TCP fingerprint classification to the nfnetlink OS fingerprint database.

## Important APIs, Types, and Functions
`xt_osf_match_packet()` is the match entry point. It consumes `struct xt_osf_info`, extracts match behavior flags, and calls the OS fingerprint matcher provided by `nfnetlink_osf`. `xt_osf_mt_reg` registers the `osf` match for IPv4 TCP traffic.

## Control Flow, State, and Persistence
The match evaluates packets against the loaded OS fingerprint table and optional TTL/logging behavior from userspace. The fingerprint database and learned/static signatures live in nfnetlink OSF state; this module does not persist its own table.

## Dependencies and Integration Points
It depends on x_tables, TCP/IP header parsing, and the nfnetlink OSF subsystem. Userspace must load fingerprints through nfnetlink tooling for meaningful matches.

## Risks and Test Signals
Risks include stale or absent fingerprints, TCP option parsing assumptions, TTL heuristics, and misleading results across NAT, middleboxes, or SYN proxies. Tests should cover known SYN fingerprints, unknown packets, database absent, TTL modes, logging flags, non-TCP rejection, and module dependency loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_osf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_owner.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_owner.c

## Purpose
`xt_owner.c` implements matching locally generated packets by socket owner credentials, socket existence, and supplementary group membership. It is intended for OUTPUT and POSTROUTING style local traffic policy.

## Important APIs, Types, and Functions
`owner_mt()` consumes `struct xt_owner_match_info`, reading `skb_to_full_sk(skb)`, socket file ownership, `kuid_t`, `kgid_t`, and `struct group_info`. `owner_check()` validates hook usage and flag combinations. Registration is NFPROTO_UNSPEC.

## Control Flow, State, and Persistence
Packet evaluation obtains the full socket if available. It checks socket-exists, UID range, GID range, and supplementary group membership as requested, applying individual inversion flags. No state is persisted; it observes current socket credential state.

## Dependencies and Integration Points
The module depends on socket ownership metadata, user namespaces for UID/GID comparisons, x_tables hook validation, and local output skb socket association. It cannot reliably classify forwarded traffic.

## Risks and Test Signals
Risks include missing skb sockets, credential changes after socket creation, namespace UID/GID mapping, supplementary group iteration cost, and misuse outside local hooks. Tests should cover owned local TCP/UDP packets, raw packets with no socket, UID/GID ranges, supplementary groups, inversion, invalid hooks, and user namespace mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_owner.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_physdev.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_physdev.c

## Purpose
`xt_physdev.c` implements bridge physical-device matching for packets traversing the bridge/netfilter path. It matches bridged status and physical input/output device names.

## Important APIs, Types, and Functions
`physdev_mt()` reads bridge netfilter skb metadata through `nf_bridge_info_get()` and compares `physindev`/`physoutdev` names from `struct xt_physdev_info`. `physdev_mt_check()` validates flags and warns or rejects impossible hook usage.

## Control Flow, State, and Persistence
The match first determines whether bridge metadata exists. It can match `--physdev-is-in`, `--physdev-is-out`, `--physdev-is-bridged`, and name/mask predicates for physical input and output devices. Device-name comparisons use masks to support wildcards. No state is persisted.

## Dependencies and Integration Points
It depends on bridge netfilter metadata and x_tables hook information. It is meaningful only when bridge netfilter support attaches physical-device context to skbs.

## Risks and Test Signals
Risks include behavior when bridge netfilter is disabled, local versus forwarded bridge packets, wildcard mask mistakes, stale device names, and hooks where physout is unavailable. Tests should cover bridged and non-bridged packets, physin/physout names and masks, is-in/is-out/is-bridged flags, inversion, invalid flag combinations, and bridge netfilter off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_physdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_pkttype.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_pkttype.c

## Purpose
`xt_pkttype.c` implements matching on skb packet type, such as host, broadcast, multicast, or otherhost.

## Important APIs, Types, and Functions
`pkttype_mt()` consumes `struct xt_pkttype_info` and compares against `skb->pkt_type`, with special handling for loopback broadcast/multicast presentation. `pkttype_mt_reg` registers the protocol-unspecified match.

## Control Flow, State, and Persistence
Each packet path reads `skb->pkt_type`, normalizes loopback behavior where needed, compares it with the configured packet type, and applies inversion. No state is persisted.

## Dependencies and Integration Points
It depends on skb link-layer classification assigned by drivers or receive paths. The match is usable across IPv4 and IPv6 because packet type is not IP-family-specific.

## Risks and Test Signals
Risks include driver differences in `pkt_type`, loopback behavior, VLAN/bridge transformations, and local-output skbs without meaningful ingress packet type. Tests should cover host, broadcast, multicast, otherhost, inversion, loopback broadcast/multicast, bridged traffic, and IPv4/IPv6 rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_pkttype.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_policy.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_policy.c

## Purpose
`xt_policy.c` implements matching on IPsec/xfrm policy and state. It can test whether a packet is protected or unprotected, inbound or outbound, and whether xfrm selectors match configured tunnel endpoints, SPI, protocol, mode, and reqid.

## Important APIs, Types, and Functions
`policy_mt()` is the top-level matcher. Helpers include `match_xfrm_state()`, `match_policy_in()`, and `match_policy_out()` operating on `struct xt_policy_info` and `struct xt_policy_elem`. `policy_mt_check_hooks()` and `policy_mt_check()` validate hook direction and element counts.

## Control Flow, State, and Persistence
For inbound packets the matcher inspects `skb_sec_path()` xfrm states. For outbound packets it checks the dst xfrm bundle. It supports strict ordered matching or any matching element, handles `XT_POLICY_MATCH_NONE`, and applies per-element inversion. The module persists no xfrm state.

## Dependencies and Integration Points
It depends on xfrm/IPsec state attached to skb security paths or dst entries, x_tables hook metadata, and IPv4/IPv6 address comparison. It is a filtering bridge into the kernel xfrm subsystem.

## Risks and Test Signals
Risks include hook direction mismatch, strict mode ordering, tunnel endpoint address family handling, bundle versus secpath differences, and packets with policy but no state or vice versa. Tests should cover inbound ESP/AH, outbound xfrm bundles, policy none, strict and non-strict multiple elements, reqid/SPI/proto/mode/tunnel addresses, inversion, IPv6, and invalid hook masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_quota.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_quota.c

## Purpose
`xt_quota.c` implements a countdown quota match. A rule matches until a configured byte quota is exhausted, optionally in inverted mode.

## Important APIs, Types, and Functions
`struct xt_quota_priv` stores a spinlock and remaining quota. `quota_mt()` decrements quota by `skb->len`. `quota_mt_check()` allocates private state from `struct xt_quota_info`, and `quota_mt_destroy()` frees it.

## Control Flow, State, and Persistence
On insertion, the configured quota is copied to per-rule private memory. Each packet locks the quota, checks whether enough bytes remain, subtracts packet length when it does, and returns match or inverted match. The remaining quota persists for the life of the rule and is not reset by time.

## Dependencies and Integration Points
The module integrates with x_tables rule lifecycle and skb length accounting. It is protocol-unspecified and can apply to IPv4 and IPv6.

## Risks and Test Signals
Risks include shared mutable state across CPUs, expectations around rule replacement resetting quota, skb length including headers, and large packet/quota boundary behavior. Tests should cover exact exhaustion, over-quota packet behavior, inversion, SMP contention, rule reload reset, destroy cleanup, and zero quota.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_quota.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_rateest.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_rateest.c

## Purpose
`xt_rateest.c` implements matching based on named netfilter rate estimators. It compares one estimator against constants or another estimator using bytes-per-second and packets-per-second rates.

## Important APIs, Types, and Functions
`xt_rateest_mt()` reads `struct xt_rateest_match_info`, fetches estimator rates, applies absolute or relative comparison modes, and supports delta calculations. `xt_rateest_mt_checkentry()` resolves and pins estimator objects; `xt_rateest_mt_destroy()` releases them.

## Control Flow, State, and Persistence
At rule insertion, named estimators are looked up and stored in match info. Packet evaluation snapshots current estimator values, optionally subtracts configured baselines, compares BPS/PPS fields according to mode, and returns the result with inversion as configured. Rate state is owned by the estimator subsystem.

## Dependencies and Integration Points
The module depends on x_tables and `xt_rateest` estimator objects created elsewhere. It is commonly used with the RATEEST target or traffic measurement rules.

## Risks and Test Signals
Risks include missing named estimators, refcount leaks, stale rate windows, signed/unsigned delta comparisons, and ambiguous combined BPS/PPS modes. Tests should cover constant threshold, estimator-vs-estimator, delta mode, less/greater/equal operators, BPS and PPS combinations, inversion, missing estimator rejection, and destroy release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_rateest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_realm.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_realm.c

## Purpose
`xt_realm.c` implements matching on the routing realm associated with the packet destination route.

## Important APIs, Types, and Functions
`realm_mt()` reads `dst->tclassid` from `skb_dst(skb)` and compares it with `struct xt_realm_info.id` and `mask`. `realm_mt_reg` registers an IPv4 alias match.

## Control Flow, State, and Persistence
Each packet must have a dst entry. The matcher applies the configured mask to the route class id and compares it with the requested id, then applies inversion. It does not persist any state.

## Dependencies and Integration Points
The module depends on route lookup having attached an skb dst and on routing realms/classids configured by routing policy. It integrates with x_tables and dst metadata.

## Risks and Test Signals
Risks include packets before route lookup, missing dst entries, policy routing changes, and mask/id confusion. Tests should cover matched and unmatched realms, inversion, no dst, masked subfields, local and forwarded routes, and route updates while rules remain loaded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_realm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_recent.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_recent.c

## Purpose
`xt_recent.c` implements the stateful `recent` match, maintaining per-net named lists of recently seen IPv4/IPv6 addresses with timestamp rings and optional TTL checks. It also exposes `/proc/net/xt_recent/*` for inspection and manual add/remove/flush operations.

## Important APIs, Types, and Functions
State is held in `struct recent_net`, `struct recent_table`, and `struct recent_entry`. Key helpers are `recent_entry_lookup()`, `recent_entry_init()`, `recent_entry_update()`, `recent_entry_remove()`, `recent_entry_reap()`, `recent_table_lookup()`, and `recent_table_flush()`. `recent_mt()` performs packet matching. `recent_mt_check_v0()` and `recent_mt_check_v1()` validate rules and create/reuse tables; `recent_mt_destroy()` releases references. Procfs support uses `recent_seq_*()` and `recent_mt_proc_write()`.

## Control Flow, State, and Persistence
Rule insertion validates exactly one of SET, REMOVE, CHECK, or UPDATE, validates modifiers such as TTL and REAP, sizes the timestamp ring from hit count, and creates a named table if needed. Packet evaluation masks source or destination address, optionally uses TTL/hop-limit, looks up the entry, and performs SET, REMOVE, CHECK, or UPDATE semantics. Tables maintain hash buckets plus an LRU list capped by `ip_list_tot`; timestamp rings persist until entry removal, table flush, namespace teardown, or module unload.

## Dependencies and Integration Points
The module uses per-net generic storage, procfs, seq_file, spinlock/mutex coordination, random jhash seeds, IPv4/IPv6 address helpers, and x_tables match lifecycle. Module parameters control table size, hash size, proc permissions, owner uid/gid, and backward-compatible packet-list sizing.

## Risks and Test Signals
High-risk areas are global lock contention, proc write parsing, table resize flush on larger hit counts, timestamp ring wrap, TTL adjustment for forwarded output packets, namespace proc cleanup before rule destruction, and memory sizing up to `XT_RECENT_MAX_NSTAMPS`. Tests should cover all operations, seconds/hitcount/reap combinations, TTL matching, masks, IPv4/IPv6 parsing in proc writes, add/remove/flush proc commands, LRU eviction, table sharing/refcounts, namespace teardown, invalid flags, and module parameter bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_recent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_repldata.h -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_repldata.h

## Purpose
`xt_repldata.h` is a small compatibility helper header for building replacement-table data used by iptables internals. It centralizes a static initializer pattern for x_tables replacement metadata.

## Important APIs, Types, and Functions
The header defines the `xt_repldata` structure initializer macro used by generated or static replacement-table definitions. It references x_tables concepts such as table name, valid hooks, entry counts, and hook/underflow offsets.

## Control Flow, State, and Persistence
There is no executable control flow. The header contributes compile-time data layout used by callers to initialize replacement structures. Any state belongs to the table replacement consumer.

## Dependencies and Integration Points
It depends on x_tables UAPI/internal structures and is included by table code that needs static replacement data. It is not a loadable module and has no runtime registration.

## Risks and Test Signals
Risks include structure layout drift across x_tables revisions, incorrect hook offset initialization by users, and alignment mismatches. Tests should be compile-focused: include the header in all intended table builds, validate replacement structure sizes and offsets, and run iptables table replacement tests that exercise hook and underflow arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_repldata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_sctp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_sctp.c

## Purpose
`xt_sctp.c` implements SCTP packet matching by source/destination port and chunk type conditions.

## Important APIs, Types, and Functions
`sctp_mt()` reads `struct sctphdr` and optional chunks. Chunk matching is handled by helpers for "all", "any", and "only" chunk semantics against `struct xt_sctp_info`. `sctp_mt_check()` validates flags and inversion masks. Registration covers IPv4 and IPv6 with `.proto = IPPROTO_SCTP`.

## Control Flow, State, and Persistence
Fragments are rejected. The matcher reads the SCTP common header, checks port ranges, then if chunk matching is requested walks the chunk list using length fields and validates chunk boundaries. It applies requested chunk type bitmaps and inversion. No state is persisted.

## Dependencies and Integration Points
The module depends on x_tables, SCTP header definitions, skb safe-copy helpers, and IPv4/IPv6 registration. It assumes transport-header offset is already computed by x_tables.

## Risks and Test Signals
Risks include malformed chunk lengths, zero-length chunk loops, truncated skbs, fragment behavior, and subtle all/any/only semantics. Tests should cover source/destination port boundaries, each chunk matching mode, inverted chunk matches, malformed chunk length, multiple chunks with padding, short headers hotdrop, fragments, and IPv4/IPv6 paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_sctp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_set.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_set.c

## Purpose
`xt_set.c` implements x_tables integration with ipset. It provides the `set` match and `SET` target across several revisions, supporting membership tests, add/delete operations, timeout/exist flags, counter matching, and skb mark/priority/queue mapping from set extensions.

## Important APIs, Types, and Functions
`match_set()` wraps `ip_set_test()`. Match revisions are `set_match_v0()`, `set_match_v1()`, `set_match_v3()`, and `set_match_v4()` with check/destroy helpers that pin set IDs through `ip_set_nfnl_get_byindex()` and release them through `ip_set_nfnl_put()`. Target revisions are `set_target_v0()`, `set_target_v1()`, `set_target_v2()`, and `set_target_v3()`. `ADT_OPT()` builds `struct ip_set_adt_opt` for test/add/delete/map operations.

## Control Flow, State, and Persistence
Match checkentry validates dimensions, converts revision 0 compatibility flags, and pins the referenced set. Packet evaluation builds ipset ADT options from rule family, dimensions, flags, counters, and timeouts, then returns membership with inversion and optional counter conditions. Targets optionally add to one set, delete from another, and revision 3 can map set extension data to `skb->mark`, `skb->priority`, or queue mapping after a map-set hit. Persistent set elements and counters are owned by ipset; this module only holds rule references.

## Dependencies and Integration Points
The file depends on x_tables, ipset core APIs, skb mark/priority/queue fields, and mangle-table hook restrictions for map-set. It registers IPv4 and IPv6 matches and targets for the supported revisions.

## Risks and Test Signals
Risks include set reference leaks on multi-set checkentry failure, revision compatibility flag conversion, dimension limit enforcement, timeout normalization, counter match semantics, map-set restricted hook/table use, and queue mapping bounds. Tests should cover each match and target revision, invalid set IDs, add/delete/map combinations, return-nomatch, counter comparisons, timeout capping, skbmark mask application, priority and queue mapping, cleanup on partial failures, and IPv4/IPv6 families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_set.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_socket.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_socket.c

## Purpose
`xt_socket.c` implements the `socket` match for transparent proxying. It matches packets that correspond to a local socket, optionally requiring transparent sockets, ignoring wildcard listeners, and restoring the socket mark to the skb.

## Important APIs, Types, and Functions
`socket_match()` handles IPv4, while `socket_mt6_v1_v2_v3()` handles IPv6. They use `nf_sk_lookup_slow_v4()` or `nf_sk_lookup_slow_v6()`, `sk_fullsock()`, `inet_sk_transparent()`, and `sock_gen_put()`. Checkentry functions `socket_mt_v1_check()`, `socket_mt_v2_check()`, and `socket_mt_v3_check()` validate flags and enable defragmentation through `socket_mt_enable_defrag()`.

## Control Flow, State, and Persistence
The matcher first uses `skb->sk` if it belongs to the current net namespace; otherwise it performs a socket lookup from packet tuple and input device. It rejects wildcard listeners unless `XT_SOCKET_NOWILDCARD` is set, rejects non-transparent sockets when requested, and can copy `sk_mark` into `skb->mark` with `XT_SOCKET_RESTORESKMARK`. Rule insertion enables IPv4/IPv6 defrag and destruction disables it. The module persists only defrag references.

## Dependencies and Integration Points
It integrates x_tables with socket lookup, TCP/UDP socket tables, transparent proxy socket options, skb marks, and nf_defrag for PREROUTING/LOCAL_IN hooks.

## Risks and Test Signals
Risks include socket reference handling, namespace mismatch, wildcard listener interception, transparent-only policy, mark restoration timing, and defrag enable/disable balancing. Tests should cover established sockets, nonzero-bound listeners, wildcard listeners with and without NOWILDCARD, transparent sockets, RESTORESKMARK, IPv4/IPv6, no socket match, namespace isolation, fragments requiring defrag, and invalid flag masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_state.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_state.c

## Purpose
`xt_state.c` implements the legacy `state` match for conntrack state. It is a smaller predecessor to `conntrack`.

## Important APIs, Types, and Functions
`state_mt()` consumes `struct xt_state_info`, calls `nf_ct_get()`, maps the conntrack info to state bits, and compares with `statemask`. `state_mt_check()` and `state_mt_destroy()` pin and release conntrack support.

## Control Flow, State, and Persistence
The matcher classifies packets as tracked conntrack state, untracked, or invalid. It returns whether the configured state mask contains the resulting bit. It does not inspect tuple fields or status beyond state and persists no state itself.

## Dependencies and Integration Points
The module depends on conntrack namespace enablement and x_tables. It registers an NFPROTO_UNSPEC match with IPv4 and IPv6 aliases.

## Risks and Test Signals
Risks include legacy semantics differing from `conntrack`, untracked versus invalid classification, and conntrack support reference management. Tests should cover NEW, ESTABLISHED, RELATED, INVALID, UNTRACKED, no conntrack, IPv4/IPv6, and unload after rules are removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_statistic.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_statistic.c

## Purpose
`xt_statistic.c` implements probabilistic and nth-packet matching. It supports random sampling and deterministic every-N packet selection.

## Important APIs, Types, and Functions
`struct xt_statistic_priv` stores nth-mode counter state with a spinlock. `statistic_mt()` handles `XT_STATISTIC_MODE_RANDOM` and `XT_STATISTIC_MODE_NTH`. `statistic_mt_check()` validates mode and allocates private state for nth mode; `statistic_mt_destroy()` frees it.

## Control Flow, State, and Persistence
Random mode compares a random 31-bit value against configured probability. Nth mode decrements or resets a shared counter under lock and matches when the configured packet interval is reached. Nth counter state persists for the life of the rule.

## Dependencies and Integration Points
The module depends on x_tables, kernel random number generation, and per-rule private memory. It is protocol-unspecified.

## Risks and Test Signals
Risks include probability scaling, shared nth state across CPUs, off-by-one packet intervals, and rule replacement resetting counters. Tests should cover random probability extremes, statistical distribution, nth every/packet offsets, inversion, SMP traffic, invalid modes, allocation failure, and destroy cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_statistic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_string.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_string.c

## Purpose
`xt_string.c` implements payload string matching using the kernel textsearch API. It supports configurable search algorithms and offsets.

## Important APIs, Types, and Functions
`string_mt()` calls `skb_find_text()` with a precompiled `struct ts_config`. `string_mt_check()` validates offsets and prepares the textsearch configuration from `struct xt_string_info`; `string_mt_destroy()` releases it with `textsearch_destroy()`.

## Control Flow, State, and Persistence
At rule insertion, userspace pattern and algorithm fields are compiled into a textsearch config. Packet evaluation searches the skb data between configured `from_offset` and `to_offset`; finding a match returns true unless inverted. The compiled textsearch config persists for the rule lifetime.

## Dependencies and Integration Points
The module depends on x_tables, skb text search support, and textsearch algorithm modules such as bm or kmp. It registers aliases for IPv4, IPv6, and ebtables-style use.

## Risks and Test Signals
Risks include offset validation, algorithm module availability, fragmented/nonlinear skb scanning, payload encoding assumptions, and expensive searches on large packets. Tests should cover several algorithms, match and no-match payloads, offsets, inversion, nonlinear skbs, invalid ranges, missing algorithms, and destroy cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_string.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_tcpmss.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_tcpmss.c

## Purpose
`xt_tcpmss.c` implements matching on the TCP Maximum Segment Size option.

## Important APIs, Types, and Functions
`tcpmss_mt()` consumes `struct xt_tcpmss_match_info`, reads `struct tcphdr`, walks TCP options, and compares an MSS option value against `mss_min` and `mss_max`. `tcpmss_mt_reg[]` registers IPv4 and IPv6 TCP-only matches.

## Control Flow, State, and Persistence
Fragments are ignored. The TCP header is fetched safely; truncated or malformed headers hotdrop. If no MSS option is present, the result is the configured invert value. If an MSS option is found with the correct length, the inclusive range comparison determines the result. No state is persisted.

## Dependencies and Integration Points
The module depends on x_tables, TCP option layout, skb header access, and protocol restriction to TCP. It only observes MSS; MSS clamping is implemented in a different target.

## Risks and Test Signals
Risks include malformed TCP data offsets, option length parsing, missing MSS on non-SYN packets, fragments, and range boundaries. Tests should cover SYN with MSS below/inside/above range, no MSS, inverted no-MSS behavior, short headers hotdrop, malformed doff, option padding, IPv4/IPv6, and fragments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_tcpmss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_tcpudp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_tcpudp.c

## Purpose
`xt_tcpudp.c` provides the core built-in matches for TCP, UDP, UDP-Lite, ICMP, and ICMPv6. It handles port ranges, TCP flag and option matching, and ICMP type/code matching.

## Important APIs, Types, and Functions
`tcp_mt()` matches TCP ports, flags, and optional TCP option presence using `tcp_find_option()`. `udp_mt()` matches UDP/UDP-Lite source and destination ports. `icmp_match()` and `icmp6_match()` match type/code ranges with `icmp_type_code_match()` and `icmp6_type_code_match()`. Checkentry functions validate inversion masks. `tcpudp_mt_reg[]` registers all protocol/family combinations.

## Control Flow, State, and Persistence
TCP and UDP paths reject fragments; TCP offset 1 fragments are hotdropped. Headers are read with `skb_header_pointer()`, and truncated requested headers hotdrop. TCP checks source/destination port ranges, masked flags, and requested option. UDP checks port ranges. ICMP and ICMPv6 check type/code ranges and inversion. The module stores no persistent state.

## Dependencies and Integration Points
It depends on x_tables, IPv4/IPv6 protocol registration, TCP/UDP/ICMP header definitions, and safe skb access. These matches are fundamental iptables protocol matches.

## Risks and Test Signals
Risks include hotdrop decisions for tinygrams, TCP option parsing, ICMP wildcard semantics differing between IPv4 and IPv6, inversion flag validation, and fragmented packets. Tests should cover TCP ports/flags/options, UDP and UDP-Lite ports, ICMP any and ranged codes, ICMPv6 type/code, invalid invflags, truncated headers, TCP offset-1 fragments, ordinary fragments, and IPv4/IPv6 registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_tcpudp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_time.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_time.c

## Purpose
`xt_time.c` implements time-of-day, date-range, weekday, and monthday matching for x_tables rules using wall-clock time.

## Important APIs, Types, and Functions
`time_mt()` is the matcher over `struct xt_time_info`. Calendar conversion is split across `localtime_1()`, `localtime_2()`, and `localtime_3()` using static day tables and `struct xtm`. `time_mt_check()` validates daytime and flags.

## Control Flow, State, and Persistence
Packet evaluation uses `ktime_get_real_seconds()` rather than skb timestamps, optionally adjusts by global `sys_tz`, checks date_start/date_stop, checks daytime including overnight ranges, optionally rewinds one day for contiguous overnight semantics, then checks weekday and monthday masks. No per-rule runtime state changes.

## Dependencies and Integration Points
It depends on x_tables, kernel real-time clock access, global timezone state, and UAPI masks. It registers an NFPROTO_UNSPEC match with IPv4/IPv6 aliases.

## Risks and Test Signals
Risks include wall-clock jumps, timezone configuration, y2038/y2106 expectations, overnight contiguous semantics, leap-year calendar conversion, and monthday bit numbering. Tests should cover date bounds, daytime bounds, overnight ranges with and without contiguous, weekdays, monthdays, leap days, timezone offsets, invalid flags, and time changes while packets traverse multiple rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_u32.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_u32.c

## Purpose
`xt_u32.c` implements arbitrary 32-bit packet content matching using a compact expression language from iptables `u32`.

## Important APIs, Types, and Functions
`u32_match_it()` interprets `struct xt_u32` tests, reading packet words with `skb_copy_bits()`. `u32_mt()` applies global inversion. `u32_mt_checkentry()` validates counts against fixed arrays in `struct xt_u32_test`.

## Control Flow, State, and Persistence
For each ANDed test, the interpreter reads an initial packet offset, applies a sequence of AND/left-shift/right-shift/AT operations, then checks whether the resulting value falls in any configured min/max range. Bounds and overflow checks prevent out-of-skb reads. The module stores no state.

## Dependencies and Integration Points
It depends on x_tables and skb byte-copy helpers. Because offsets are packet-relative, userspace expressions must account for IP header sizes and encapsulation.

## Risks and Test Signals
Risks include expression validation gaps, offset arithmetic overflow, nonlinear skb reads, endian assumptions, and user confusion over dynamic `@` offsets. Tests should cover simple fixed offsets, chained arithmetic, `@` indirection, multiple tests and ranges, inversion, boundary offsets at `skb->len - 4`, overflow attempts, invalid ntests/nnums/nvalues, and IPv4/IPv6 packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_u32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/Kconfig -->
# sources/distributed-fs/ceph-client/net/netlabel/Kconfig

## Purpose
`net/netlabel/Kconfig` defines the build-time option for the NetLabel subsystem, which provides explicit network packet labeling protocols such as CIPSO and RIPSO for Linux security modules.

## Important APIs, Types, and Functions
This file defines `config NETLABEL` as a boolean option. It depends on `SECURITY`, selects `CRC_CCITT` when IPv6 is enabled, defaults to `n`, and presents help text pointing users to kernel documentation and netlabel tools.

## Control Flow, State, and Persistence
There is no runtime control flow. The selected Kconfig value determines whether NetLabel objects are built into the kernel. Because it is boolean in this tree, NetLabel is built-in when enabled rather than a standalone module.

## Dependencies and Integration Points
The option gates compilation of the NetLabel source files in the directory and ties the subsystem to the broader Linux security framework. The IPv6 conditional CRC selection supports CALIPSO-style IPv6 labeling support.

## Risks and Test Signals
Risks include enabling NetLabel without the expected LSM policy users, missing CRC support for IPv6 label protocols, and assuming module unloadability when the option is boolean. Tests should cover Kconfig dependency resolution with and without `SECURITY`, IPv6 builds selecting CRC support, allnoconfig/default behavior, and successful compilation of NetLabel users when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/Makefile -->
# sources/distributed-fs/ceph-client/net/netlabel/Makefile

## Purpose
`net/netlabel/Makefile` defines the object composition for the NetLabel subsystem.

## Important APIs, Types, and Functions
The Makefile always includes base objects `netlabel_user.o`, `netlabel_kapi.o`, `netlabel_domainhash.o`, and `netlabel_addrlist.o`, management object `netlabel_mgmt.o`, protocol objects `netlabel_unlabeled.o` and `netlabel_cipso_v4.o`, and conditionally includes `netlabel_calipso.o` when `CONFIG_IPV6` is enabled after `subst m,y`.

## Control Flow, State, and Persistence
There is no runtime control flow. The build state determines which object files become part of the NetLabel built-in object list. IPv6 controls CALIPSO inclusion.

## Dependencies and Integration Points
This file integrates NetLabel source units with kbuild and mirrors the Kconfig boolean nature by using `obj-y`. It binds address-list, domain-hash, management, unlabeled, CIPSO, and CALIPSO implementation files into one subsystem.

## Risks and Test Signals
Risks include missing object additions when new NetLabel source files are introduced, CALIPSO being absent in non-IPv6 builds, and assuming modular object behavior. Tests should cover builds with IPv6 enabled/disabled, symbol availability for all listed objects, and dependency changes in Kconfig reflected here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_addrlist.c -->
# sources/distributed-fs/ceph-client/net/netlabel/netlabel_addrlist.c

## Purpose
`netlabel_addrlist.c` implements ordered IPv4 and IPv6 address-list helpers for NetLabel domain and protocol mappings. It supports longest-prefix-style search, exact search, add, remove, and audit formatting.

## Important APIs, Types, and Functions
IPv4 APIs are `netlbl_af4list_search()`, `netlbl_af4list_search_exact()`, `netlbl_af4list_add()`, `netlbl_af4list_remove_entry()`, `netlbl_af4list_remove()`, and `netlbl_af4list_audit_addr()`. IPv6 equivalents are compiled when `CONFIG_IPV6` is enabled: `netlbl_af6list_search()`, `netlbl_af6list_search_exact()`, `netlbl_af6list_add()`, `netlbl_af6list_remove_entry()`, `netlbl_af6list_remove()`, and `netlbl_af6list_audit_addr()`.

## Control Flow, State, and Persistence
Search walks RCU-protected lists and returns the first valid entry whose masked address matches; ordering by mask width makes the first hit the most specific. Add first checks for an exact duplicate, then inserts before the first less-specific entry or at the tail. Remove marks an entry invalid and unlinks with `list_del_rcu()`, leaving memory reclamation to callers after RCU safety. Audit helpers format address and prefix length into an audit buffer.

## Dependencies and Integration Points
The file depends on Linux list/RCU primitives, IPv4/IPv6 address helpers, and audit logging. It is used by NetLabel domain and unlabeled/CIPSO/CALIPSO management code that owns list locks and entry lifetimes.

## Risks and Test Signals
Risks include caller lock/RCU misuse, invalid entries remaining visible to unsafe iteration, duplicate detection relying on search ordering, non-contiguous mask prefix reporting, IPv6 conditional compilation, and memory lifetime after removal. Tests should cover longest-prefix lookup ordering, exact duplicate rejection, removal under RCU readers, IPv4 and IPv6 masks, empty lists, audit output with full and partial masks, and caller-side `synchronize_rcu()` before freeing removed entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_addrlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_addrlist.h -->
# sources/distributed-fs/ceph-client/net/netlabel/netlabel_addrlist.h

## Purpose
`netlabel_addrlist.h` declares NetLabel address-list structures, iteration macros, function prototypes, and audit stubs for IPv4 and optional IPv6 address lists.

## Important APIs, Types, and Functions
The core types are `struct netlbl_af4list` with `__be32 addr`, `__be32 mask`, `valid`, and `list`, and `struct netlbl_af6list` with `struct in6_addr addr`, `mask`, `valid`, and `list`. Macros include `netlbl_af4list_foreach()`, `netlbl_af4list_foreach_rcu()`, `netlbl_af4list_foreach_safe()`, and IPv6 equivalents, backed by `__af4list_valid()`, `__af4list_valid_rcu()`, `__af6list_valid()`, and `__af6list_valid_rcu()`.

## Control Flow, State, and Persistence
The inline helpers advance list iteration past entries whose `valid` flag has been cleared before RCU deletion completes. The macros provide normal, RCU, and safe traversal forms. Data persists in caller-owned list nodes; the header does not allocate or free memory.

## Dependencies and Integration Points
It depends on list and RCU primitives, IPv6 type definitions, and audit types. Function declarations connect users to `netlabel_addrlist.c`; audit functions compile to no-op stubs when `CONFIG_AUDIT` is disabled, and IPv6 declarations are conditional on `CONFIG_IPV6`.

## Risks and Test Signals
Risks include using non-RCU iteration under RCU-only protection, dereferencing the list head through `container_of()` if macros are misused, stale invalid entries, and missing audit/IPv6 functions under configuration changes. Tests should compile with IPv6 and audit enabled/disabled, exercise all traversal macros with invalid entries, verify prototypes match implementations, and run list removal scenarios under lockdep/RCU debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_addrlist.h -->
