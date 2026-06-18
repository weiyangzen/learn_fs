# Research: subset-b-006251

Grouped research for nftables/netfilter source files under `sources/distributed-fs/ceph-client/net/netfilter`. Each section is bounded for deterministic reconciliation into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_compat.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_compat.c

Purpose: this module exposes legacy x_tables matches and targets as nftables expressions named `match` and `target`, plus an nfnetlink compatibility query subsystem. It bridges nftables rule evaluation into `xt_match`/`xt_target` callbacks while preserving xtables family, hook, proto, revision, and user-info ABI expectations.

Important APIs/types/functions: `union nft_entry` supplies family-specific fake xtables entries; `nft_compat_set_par()`, `nft_target_set_tgchk_param()`, and `nft_match_set_mtchk_param()` populate xtables parameter structures. `nft_target_select_ops()` and `nft_match_select_ops()` dynamically allocate per-extension `nft_expr_ops` with `ops->data` pointing to the requested xt module. Large match private data uses `struct nft_xt_match_priv` to store separately allocated `info`. `nfnl_compat_get_rcu()` reports the best available extension revision over `NFNL_SUBSYS_NFT_COMPAT`.

Control flow: select_ops validates netlink attributes, requests the xt module, allocates ops, and chooses eval/destroy/dump handlers. Init copies userspace info with xt alignment padding, parses optional `NFTA_RULE_COMPAT`, waits for pending xt destructors, and calls `xt_check_match()` or `xt_check_target()`. Eval converts xt verdicts to nft verdicts, including bridge-specific ebtables verdict translation. Validate checks families, base-chain hooks, xt hook masks, and `nat` chain dependency. Destroy calls xt destructors, drops module references, and frees dynamic ops/info.

State/persistence: expression state is xt private info plus module references. The nfnetlink subsystem and expression types are registered at module init. Risks are mostly ABI and lifetime risks: wrong alignment, missing module_put, stale async xt destructor side effects, invalid hook/table dependency, and bridge verdict mismatch. Test signals include creating nft rules that wrap iptables, ip6tables, ebtables, and arptables extensions, revision query tests, LOG/NFLOG autoload tests, large match info tests, invalid hook/family rejection, and delete/reload cycles checking xt destructor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_connlimit.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_connlimit.c

Purpose: implements the nftables `connlimit` expression and `NFT_OBJECT_CONNLIMIT` object for limiting rule traversal by the number of concurrent conntrack entries associated with packets.

Important APIs/types/functions: `struct nft_connlimit` stores an `nf_conncount_list`, limit, and invert flag. `nft_connlimit_do_eval()` is shared by expression and object evaluation. `nft_connlimit_do_init()` allocates the count list, parses `NFTA_CONNLIMIT_COUNT` and `NFT_CONNLIMIT_F_INV`, initializes conntrack namespace usage with `nf_ct_netns_get()`, and `nft_connlimit_do_destroy()` releases it. Clone and GC support are provided by `nft_connlimit_clone()`, `nft_connlimit_destroy_clone()`, and `nft_connlimit_gc()`.

Control flow: eval calls `nf_conncount_add_skb()` for the current skb. `-EEXIST` is treated as a soft signal to run `nf_conncount_gc_list()` and refresh the count; other errors drop the packet. The current list count is compared with `limit`, xor `invert`; matches that exceed the policy set `NFT_BREAK`, so later expressions in the rule do not run.

State/persistence: state is the allocated `nf_conncount_list`, its live count/cache, and mutable object limit/invert fields updated with `WRITE_ONCE()`. Expressions are flagged `NFT_EXPR_STATEFUL | NFT_EXPR_GC`. Dependencies include conntrack count/core/zones and nf_tables object/expr registration. Risks include stale count if GC is not run often, resource failure causing packet drops, clone semantics intentionally not sharing live counts, and object updates changing policy while old tracked entries remain. Test signals: limit boundary tests, invert behavior, object update behavior, clone/transaction rollback cleanup, conntrack namespace unload, GC after closed connections, and failure injection for list allocation or `nf_conncount_add_skb()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_connlimit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_counter.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_counter.c

Purpose: provides nftables packet/byte counters as both stateful expressions and named objects. The counter observes each packet and accumulates `skb->len` and packet count with per-CPU storage.

Important APIs/types/functions: `struct nft_counter` holds per-CPU `u64_stats_t` counters; `struct nft_counter_percpu_priv` points to the percpu allocation. `nft_counter_do_eval()` updates counters under `local_bh_disable()` and per-CPU `u64_stats_sync`. `nft_counter_fetch()`, `nft_counter_reset()`, and `nft_counter_fetch_and_reset()` aggregate and optionally reset for dump. Offload support is represented by `nft_counter_offload()` and `nft_counter_offload_stats()`.

Control flow: init allocates per-CPU counters and seeds the current CPU from optional netlink packet/byte values. Eval increments local CPU fields. Dump aggregates all possible CPUs using seqcount retry; reset uses `nft_counter_lock` to serialize fetch and subtract. Clone snapshots aggregate totals into a new percpu counter. Hardware offload stats are folded into the local CPU counter.

State/persistence: counters are runtime state with optional initial values and reset-on-dump behavior. No module init function appears here; exported `nft_counter_type`, `nft_counter_obj_type`, and `nft_counter_init_seqcount()` are integrated by core nf_tables code. Risks include 32-bit torn reads if seqcounts are wrong, reset races, negative totals due to signed accumulator type, and offload stats double-accounting if drivers report deltas incorrectly. Test signals include concurrent traffic on multiple CPUs, dump/reset semantics, initial value load, clone preserving totals, object and expression parity, offload stats injection, and KCSAN-style checks around `u64_stats_sync`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_counter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_ct.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_ct.c

Purpose: implements nftables conntrack expressions (`ct`, `notrack`) and conntrack-related objects for helpers, timeouts, and expectations. It is the main nftables integration layer for reading and modifying `nf_conn` state.

Important APIs/types/functions: `nft_ct_get_eval()` reads state, direction, status, marks, secmarks, expiration, helper name, labels, accounting counters, tuple fields, protocol, zone, and ID. `nft_ct_set_eval()` updates marks, secmarks, labels, and event masks. `nft_ct_set_zone_eval()` attaches a conntrack template zone before tracking. `nft_notrack_eval()` marks packets untracked. Object paths include `nft_ct_timeout_obj_eval()`, `nft_ct_helper_obj_eval()`, and `nft_ct_expect_obj_eval()`.

Control flow: `nft_ct_select_ops()` chooses get, set, fast-get, or zone-set ops from `NFTA_CT_DREG/SREG` and key. Init validates key-specific register sizes and direction requirements, acquires conntrack namespace refs, enables accounting for byte/packet keys, and acquires label/template resources under optional config. Eval either stores values into registers, modifies the current unconfirmed/confirmed conntrack, creates timeout/helper/expect extensions, or sets verdicts to `NFT_BREAK`/`NF_DROP` on missing state or allocation failure. Module init registers `ct`, `notrack`, helper, expect, and optional timeout object types.

State/persistence: persistent state includes expression key/register metadata, per-net conntrack references, optional connlabels refs, per-CPU zone templates protected by `nft_ct_pcpu_mutex`, helper module refs, timeout blobs freed by RCU, and expectation policy. Risks include subtle confirmed vs unconfirmed restrictions, missing netns/module ref release, template reuse while skbs are queued, config-dependent key availability, NAT sequence-adjust extension failure, and timeout/helper lifetime under RCU. Test signals: read all CT keys across IPv4/IPv6/inet, set mark/label/eventmask, zone before tracking, notrack behavior, helper assignment with NAT, expectation creation limits/timeouts, timeout object parse/dump, namespace teardown, module unload, and retpoline fast-path equivalence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_ct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_ct_fast.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_ct_fast.c

Purpose: provides `nft_ct_get_fast_eval()`, a small exported fast evaluation helper used when mitigation/retpoline builds want direct code paths for common conntrack get keys.

Important APIs/types/functions: the single exported function reads `struct nft_ct` private data, calls `nf_ct_get()`, and writes common values to the nft register file. It supports `NFT_CT_STATE`, `NFT_CT_DIRECTION`, `NFT_CT_STATUS`, and conditionally `NFT_CT_MARK` and `NFT_CT_SECMARK`.

Control flow: state is always reported even when no conntrack exists, mapping to tracked, untracked, or invalid state bits. For all other keys, missing conntrack sets `NFT_BREAK`. Unsupported keys trigger `WARN_ON_ONCE(1)` and break evaluation. The function is compiled only when `CONFIG_NFT_CT` is enabled and is exported with `EXPORT_SYMBOL_GPL`.

State/persistence: no local state is allocated; it reads the skb's conntrack pointer and expression metadata. Dependencies are nf_tables core register helpers and nf_conntrack. Risks are divergence from `nft_ct_get_eval()` semantics, especially READ_ONCE handling for mark in the full path versus direct field reads here, and accidental selection for unsupported keys. Test signals include comparing outputs between fast and normal get ops for all supported keys, no-ct and untracked skbs, config combinations for mark/secmark, and warning assertions for invalid dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_ct_fast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_dup_netdev.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_dup_netdev.c

Purpose: implements the netdev-family nftables `dup` expression that duplicates a packet to an egress interface while rule evaluation continues.

Important APIs/types/functions: `struct nft_dup_netdev` stores the source register containing the output ifindex. `nft_dup_netdev_eval()` reads that ifindex and calls `nf_dup_netdev_egress()`. `nft_dup_netdev_offload()` maps the same action to `FLOW_ACTION_MIRRED` through `nft_fwd_dup_netdev_offload()`.

Control flow: init requires `NFTA_DUP_SREG_DEV` and validates a register load of `sizeof(int)`. Eval performs the duplication without changing the verdict. Dump emits the source register. Offload action reports that this expression is a hardware action. Module init registers an expression type limited to `NFPROTO_NETDEV`.

State/persistence: state is only the register index; no per-packet persistence beyond the cloned/transmitted skb in `nf_dup_netdev_egress()`. Dependencies include nf_tables offload, netdev duplication helpers, and netdev-family hook support. Risks include invalid ifindex values in the register, recursion/loop behavior delegated to duplication helpers, offload mismatch between mirror and software duplicate, and using the expression outside netdev family. Test signals: duplicate to valid and invalid devices, ingress/egress netdev chains, continued rule evaluation after duplication, offload rule generation, and module unload/register cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_dup_netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_dynset.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_dynset.c

Purpose: implements dynamic nft set mutation from packet rules. It can add/update/delete set elements, optionally map data, timeout state, and per-element expressions.

Important APIs/types/functions: `struct nft_dynset` stores the target `nft_set`, extension template, operation, key/data registers, timeout, invert flag, expression array, and set binding. `nft_dynset_new()` constructs a new element with key/data/timeout and cloned element expressions. `nft_dynset_eval()` drives delete or set `update()` operations. Init is the large validator that binds the set, parses expressions, prepares extensions, and enforces set capability flags.

Control flow: init runs under `commit_mutex`, looks up the set by name/id, rejects object/constant/non-updatable sets, validates operation and timeout compatibility, parses key and optional map data registers, and either accepts provided element expressions or clones the set defaults. Eval deletes directly for `NFT_DYNSET_OP_DELETE`; otherwise it calls the set backend's `update()`. Existing elements can have timeout expiration refreshed and element expressions evaluated. Misses produce `NFT_BREAK` unless inverted.

State/persistence: persistent state is the bound set reference plus cloned element-expression templates. Runtime state lives in the set: elements, timeouts, expression private state, and `set->nelems`. Dependencies include nft set backends, nf_tables set binding lifecycle, register parsing, and expression cloning. Risks include atomic allocation failure on packet path, set size accounting leaks, expression compatibility with set-declared expressions, timeout overflow, and transaction activation/deactivation reference bugs. Test signals: add/update/delete paths, maps and non-maps, timeout refresh, invert behavior, anonymous/named set binding, element expressions with multiple slots, full set failure, and transaction rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_dynset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_exthdr.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_exthdr.c

Purpose: implements nftables `exthdr` operations for extracting, testing, modifying, or stripping IPv6 extension headers, IPv4 options, TCP options, SCTP chunks, and optionally DCCP options.

Important APIs/types/functions: `struct nft_exthdr` stores type, offset, length, operation, dreg/sreg, and flags. Eval variants include `nft_exthdr_ipv6_eval()`, `nft_exthdr_ipv4_eval()`, `nft_exthdr_tcp_eval()`, `nft_exthdr_tcp_set_eval()`, `nft_exthdr_tcp_strip_eval()`, `nft_exthdr_sctp_eval()`, and optional `nft_exthdr_dccp_eval()`. `nft_exthdr_select_ops()` dispatches by `NFTA_EXTHDR_OP`.

Control flow: init validates register direction, bounded u8 offset/len, present flag, and protocol-specific constraints. IPv6 uses `ipv6_find_hdr()`. IPv4 copies options, compiles them with `__ip_options_compile()`, and supports SSRR/LSRR/RR/RA. TCP option read walks option lengths defensively; set ensures writable skb, supports 2/4 byte writes, avoids increasing MSS, and updates TCP checksum; strip replaces option bytes with NOP and adjusts checksum. SCTP walks padded chunks. DCCP only supports presence and logs a deprecation warning on selection.

State/persistence: expression state is pure metadata; packet mutation occurs only for TCP set/strip. Dependencies include skb header access, checksum helpers, IP option parsing, TCP/SCTP/DCCP header formats, and nf_tables registers. Risks include malformed option lengths, skb linearization/writable failures, checksum drift, fragmentation handling, unsupported IPv4 option types, and DCCP removal. Test signals: present/value modes for each protocol, malformed zero-length TCP options, MSS non-increase rule, checksum validation after set/strip, fragmented packets breaking safely, SCTP padding, IPv6 extension lookup, and invalid op/register combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_exthdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_fib.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_fib.c

Purpose: provides shared generic helpers for nftables FIB/routing-table lookup expressions used by IPv4, IPv6, inet, and netdev frontends.

Important APIs/types/functions: exported `nft_fib_policy` validates `NFTA_FIB_DREG`, result, and flags. `nft_fib_validate()` enforces hook placement based on result and input/output interface flags. `nft_fib_init()` validates source/destination and iif/oif flag combinations and sets destination register width. `nft_fib_dump()` serializes expression configuration. `nft_fib_store_result()` stores output interface index/name or presence boolean.

Control flow: init requires nonzero flags, exactly one of source/destination, and not both iif/oif. Result `OIF` and `OIFNAME` reject OIF input flags and select register sizes of `int` or `IFNAMSIZ`; `ADDRTYPE` stores a u32. Validate maps result and flag direction to legal nf hook masks and calls `nft_chain_validate_hooks()`.

State/persistence: no dynamic state; expression state is `struct nft_fib` in private data. Dependencies are backend evaluators (`nft_fib4_eval`, `nft_fib6_eval`, type variants) declared in `nft_fib.h`, netdevice naming, and nf_tables register parsing. Risks include mismatched frontend/backend family assumptions, invalid flag combinations, stale device names if backend passes null dev, and hook validation regressions. Test signals: all result modes, present flag behavior, invalid flag combinations, hook placement by input/output path, dump round trips, IPv4/IPv6 backend parity, and no-route cases returning zero/empty output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_fib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_fib_inet.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_fib_inet.c

Purpose: registers the inet-family `fib` expression and dispatches runtime evaluation to IPv4 or IPv6 FIB helpers based on packet family.

Important APIs/types/functions: `nft_fib_inet_eval()` inspects `nft_pf(pkt)` and `priv->result`, then calls `nft_fib4_eval()`, `nft_fib4_eval_type()`, `nft_fib6_eval()`, or `nft_fib6_eval_type()`. The expression ops reuse shared `nft_fib_init()`, `nft_fib_dump()`, and `nft_fib_validate()`.

Control flow: module init registers `nft_fib_inet_type` for `NFPROTO_INET`. Eval only handles `NFPROTO_IPV4` and `NFPROTO_IPV6`; unknown packet families set verdict `NF_DROP`. Result dispatch separates output-interface/name lookups from address-type lookups.

State/persistence: state is the shared `struct nft_fib`; no inet-specific allocation. Dependencies are the generic `nft_fib.c` helpers and IPv4/IPv6 backend modules. Risks include dropping packets with unexpected family instead of breaking, backend availability/config differences, and result enum drift between generic init and dispatch. Test signals: inet table rules matching IPv4 and IPv6 traffic, addrtype vs oif/oifname results, unknown family behavior, module registration, and validation inherited from generic FIB helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_fib_inet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_fib_netdev.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_fib_netdev.c

Purpose: registers the netdev-family `fib` expression and dispatches routing lookups based on the skb Ethernet protocol.

Important APIs/types/functions: `nft_fib_netdev_eval()` switches on `ntohs(pkt->skb->protocol)` for `ETH_P_IP` and `ETH_P_IPV6`, checks `ipv6_mod_enabled()` for IPv6, and calls the same IPv4/IPv6 backend functions used by inet. Ops reuse `nft_fib_init()`, `nft_fib_dump()`, and `nft_fib_validate()`.

Control flow: module init registers `nft_fib_netdev_type` for `NFPROTO_NETDEV`. Eval handles IPv4 and enabled IPv6; unsupported protocols or disabled IPv6 set `NFT_BREAK`, allowing rule traversal to stop without forcing a drop. Result dispatch mirrors inet: oif/oifname versus addrtype.

State/persistence: no dynamic state beyond `struct nft_fib` expression data. Dependencies include netdev hooks, IPv6 module state, shared FIB helpers, and skb protocol classification. Risks include protocol parsing after VLAN/encapsulation if packet info was not normalized, result semantics differing from inet on unsupported protocols (`NFT_BREAK` vs drop), and hook validation inherited from generic helpers. Test signals: netdev ingress/egress rules for IPv4, IPv6 enabled/disabled, non-IP frames, all result types, present flag behavior, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_fib_netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_flow_offload.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_flow_offload.c

Purpose: implements the `flow_offload` expression that promotes eligible established flows into an nf_flow_table for software or hardware fast path.

Important APIs/types/functions: `struct nft_flow_offload` stores a referenced `nft_flowtable`. `nft_flow_offload_eval()` performs eligibility checks, route creation, `flow_offload_alloc()`, `flow_offload_route_init()`, and `flow_offload_add()`. `flow_offload_ct_tcp()` relaxes conntrack TCP window validation because conntrack will miss offloaded packets. A netdevice notifier calls `nf_flow_table_cleanup()` on `NETDEV_DOWN`.

Control flow: validate limits use to IPv4/IPv6/inet forward hooks. Init looks up the named flowtable, increments its use count, and gets conntrack namespace support. Eval skips secpath and IPv4 options, requires conntrack, allows established TCP, UDP, and limited GRE, rejects helpers, seq adjust, NAT clash, unconfirmed entries, and already-offloaded entries. It sets `IPS_OFFLOAD_BIT`, computes routes, allocates/adds a flow, and clears the bit plus releases dsts on failures. Failures break rule evaluation.

State/persistence: expression state references the flowtable and conntrack namespace; runtime state is per-connection `IPS_OFFLOAD_BIT` and flowtable entries. Dependencies include conntrack core/extend, flowtable route helpers, netdevice notifier, and forward-chain placement. Risks include leaked offload bits on unusual failure paths, stale flows after device down, NAT/GRE eligibility gaps, TCP validation side effects, and flowtable use restoration during transactions. Test signals: established TCP/UDP offload, skipped secpath/IP options, helper/NAT-clash rejection, route allocation failure cleanup, device-down cleanup, forward-hook validation, flowtable delete transactions, and hardware bidirectional flag behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_flow_offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_fwd_netdev.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_fwd_netdev.c

Purpose: implements netdev-family `fwd` expressions for redirecting packets to an egress device or forwarding through neighbor resolution to a supplied next-hop address.

Important APIs/types/functions: `struct nft_fwd_netdev` stores the output ifindex register; `nft_fwd_netdev_eval()` calls `nf_fwd_netdev_egress()` and returns `NF_STOLEN`. `struct nft_fwd_neigh` stores device, address, and nfproto registers; `nft_fwd_neigh_eval()` decrements IPv4 TTL or IPv6 hop limit, resolves the device, adjusts headroom, and calls `neigh_xmit()`. Offload uses `nft_fwd_dup_netdev_offload()` with `FLOW_ACTION_REDIRECT`.

Control flow: `nft_fwd_select_ops()` chooses neighbor forwarding when `NFTA_FWD_SREG_ADDR` is present, otherwise simple netdev forwarding. Simple init only parses device register. Neighbor init requires device, address, and nfproto, validates IPv4/IPv6 address width, then parses registers. Validate restricts hooks to netdev ingress/egress.

State/persistence: state is register metadata only; packet path mutates skb device, redirected flag, ingress ifindex, TTL/hop-limit, timestamp, and ownership via stolen verdict/neigh transmit. Dependencies include nf_dup_netdev helpers, neighbor tables, RCU dev lookup, flow offload structures, and netdev hooks. Risks include recursion limit handling, skb headroom expansion stealing/dropping semantics, TTL/hop-limit underflow, invalid ifindex, and software/offload redirect mismatch. Test signals: ifb-style redirect, neighbor forwarding for IPv4/IPv6, nonmatching protocol breaks, TTL one drops, invalid device drops, headroom expansion failure, ingress/egress validation, and hardware offload generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_fwd_netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_hash.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_hash.c

Purpose: implements nftables `hash` expression variants for deterministic Jenkins hashing over register data and symmetric skb flow hashing, writing a bounded value into a destination register.

Important APIs/types/functions: `struct nft_jhash` stores source/destination registers, input length, seed, autogen seed flag, modulus, and offset. `struct nft_symhash` stores destination register, modulus, and offset. `nft_jhash_eval()` uses `jhash()` plus `reciprocal_scale()`. `nft_symhash_eval()` uses `__skb_get_hash_symmetric_net()`. `nft_hash_select_ops()` chooses `NFT_HASH_JENKINS` or `NFT_HASH_SYM`.

Control flow: Jenkins init requires source register, destination register, length, and modulus; validates nonzero length/modulus and offset overflow; parses source register load; uses provided seed or generates a random seed not dumped back. Symmetric init requires dreg and modulus, validates offset overflow, and stores u32. Dump emits all public parameters and hides autogenerated seed.

State/persistence: jhash with autogenerated seed is per-expression module-lifetime state that affects rule reproducibility after reload. Symhash has only modulus/offset. Dependencies include jhash, skb flow hashing, net namespace aware symmetric hash, and register parsing. Risks include offset+modulus overflow, zero modulus, hidden random seed making dump/restore semantic differences, and input length crossing register boundaries if parser validation changes. Test signals: explicit seed reproducibility, autogenerated seed omission in dumps, modulus distribution, offset boundaries near u32 max, symmetric hash stable across flow directions, invalid type rejection, and register width validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_immediate.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_immediate.c

Purpose: implements the nftables `immediate` expression that copies an immediate value or verdict into a destination register, including jump/goto chain binding and offload of simple accept/drop verdicts.

Important APIs/types/functions: `struct nft_immediate_expr` is used from nf_tables core. `nft_immediate_eval()` calls `nft_data_copy()`. `nft_immediate_init()` parses `NFTA_IMMEDIATE_DATA`, determines value vs verdict by destination register, validates register storage, and binds jump/goto chains. Lifecycle functions `activate`, `deactivate`, and `destroy` handle bound-chain transaction semantics.

Control flow: init acquires data and optional chain binding. Activate holds data references and, for bound chains, activates all expressions in the target chain and clears pending deletion state. Deactivate handles prepare-error, prepare, commit, and abort-style phases differently: unbinds or deactivates bound chains, deletes chain list entries, and decrements use counts where appropriate. Destroy releases bound-chain rules if construction failed or a bound chain was deleted. Validate recurses into jump/goto chains with level tracking. Offload maps immediate verdict accept/drop to flow actions or records register constants for later offload expressions.

State/persistence: expression state is immediate data, register length, and references to chains/data objects. Dependencies include nf_tables transaction phases, chain binding, data init/release/hold, rule activation, and flow offload context. Risks include chain use count imbalance, recursion validation bugs, incorrect data release on commit vs rollback, and offload accepting only simple verdicts. Test signals: immediate scalar values, verdict accept/drop, jump/goto to bound chains, transaction rollback at each phase, recursive chain validation, delete bound chain cleanup, dump round trip, and offload register propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_immediate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_inner.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_inner.c

Purpose: implements the nftables `inner` expression wrapper that parses encapsulated/tunnel packet headers and evaluates an embedded `payload` or `meta` expression against the inner packet context.

Important APIs/types/functions: `struct nft_inner` stores flags, tunnel header size/type, embedded expression type, and an embedded `__nft_expr` private area for payload/meta data. Per-CPU `nft_pcpu_tun_ctx` caches `struct nft_inner_tun_ctx` under a local lock. Parsing helpers include `nft_inner_parse_tunhdr()`, `nft_inner_parse_l2l3()`, `nft_inner_parse()`, and cache save/restore helpers.

Control flow: eval first obtains an inner offset via `nft_payload_inner_offset()`. If packet info lacks a reusable full inner context or type differs, it parses tunnel header, optional L2, network header, and transport header offsets. It handles GRE directly, UDP tunnel headers, Geneve option length, Ethernet/VLAN, IPv4 fragmentation, and IPv6 extension traversal. Then it calls `nft_payload_inner_eval()` or `nft_meta_inner_eval()` on the embedded expression and stores the context for subsequent expressions on the same skb.

State/persistence: expression state is the embedded inner expression and parsing configuration; runtime cache is per-CPU and keyed by skb pointer. Dependencies include payload/meta inner ops, tunnel protocol headers, IPv4/IPv6 parsing, VLAN/Geneve/GRE helpers, and local BH locking. Risks include stale cache if skb pointer reuse collides, unsupported embedded expression types, malformed tunnel headers, incorrect offset for Geneve options, and fragment handling. Test signals: GRE and UDP tunnel packets, Geneve options, L2-present and network-only modes, IPv4 fragments, IPv6 extension headers, embedded payload and meta protocol/l4proto reads, cache reuse across multiple inner expressions, and invalid `NFTA_INNER_NUM`/hdrsize/type rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_inner.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_last.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_last.c

Purpose: implements the stateful nftables `last` expression that records whether a rule was hit and the jiffies timestamp of the last hit.

Important APIs/types/functions: `struct nft_last` stores `jiffies` and `set`; `struct nft_last_priv` points to an allocated `nft_last`. `nft_last_init()` supports optional restore from `NFTA_LAST_SET` and elapsed milliseconds. `nft_last_eval()` updates the timestamp and set flag with `READ_ONCE`/`WRITE_ONCE`. `nft_last_dump()` reports whether set and elapsed milliseconds since last hit.

Control flow: init allocates state and, if userspace says the value is set, converts milliseconds to jiffies and backdates the timestamp. Eval writes current `jiffies` if changed and sets the flag. Dump detects time wrap/clock anomaly with `time_before(jiffies, last_jiffies)` and clears the state if the stored time is in the future. Clone duplicates the state into a new allocation.

State/persistence: this is explicitly `NFT_EXPR_STATEFUL`; state lives in a heap allocation rather than expression inline data. Dependencies include jiffies conversion helpers and netlink dump padding. Risks include races on non-atomic multi-field consistency, jiffies wrap/future timestamp clearing, clone preserving old timestamps, and restore values beyond representable jiffies. Test signals: first hit, repeated hit elapsed time, dump before/after hit, restore from netlink, clone behavior, future timestamp handling, and concurrent packet/dump access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_last.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_limit.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_limit.c

Purpose: implements nftables rate limiting as both expressions and named objects, supporting packet-rate and byte-rate token buckets with optional inverted matching.

Important APIs/types/functions: `struct nft_limit` contains the spinlock, last timestamp, and tokens. `struct nft_limit_priv` stores bucket parameters and flags. `nft_limit_eval()` is the shared token-bucket engine. Packet mode wraps it in `struct nft_limit_priv_pkts` with precomputed per-packet cost; byte mode computes cost from `skb->len`. Object and expression select_ops choose packet or byte variants from `NFTA_LIMIT_TYPE`.

Control flow: init parses rate/unit/burst/flags, checks multiplication/addition overflow, applies default packet burst of 5, computes maximum tokens, allocates a bucket, and initializes timestamp/tokens. Eval locks with `spin_lock_bh()`, replenishes by elapsed ns up to max, subtracts cost if possible, and returns whether to set `NFT_BREAK` considering invert. Dump emits rate, unit seconds, burst, type, and flags. Clone creates a fresh full bucket, not a copy of current token level.

State/persistence: state is mutable token count and last-time per expression/object; objects allow shared rate state between rules. Dependencies are ktime, spinlocks, netlink parsing, and nf_tables object registration. Risks include overflow in byte cost multiplication, clock jumps, clone semantics resetting bucket fullness, invert confusion, and object size inconsistency between packet and byte ops. Test signals: packet and byte limits, burst behavior, invert, zero/overflow rate or unit, concurrent packet paths, object sharing, clone/reset behavior, dump round trip, and module registration rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_limit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_log.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_log.c

Purpose: implements the nftables `log` expression for syslog, nfnetlink log, and audit logging of matching packets.

Important APIs/types/functions: `struct nft_log` contains `nf_loginfo` and a prefix pointer. `nft_log_eval()` either calls `nft_log_eval_audit()` for audit level or `nf_log_packet()` for logger backends. `nft_log_modprobe()` requests `nf_log_syslog` or `nfnetlink_log` when logger lookup needs module loading. Init parses prefix, group, snaplen, qthreshold, log level, and flags.

Control flow: init defaults to `NF_LOG_TYPE_LOG`; specifying group switches to ULOG and forbids log flags. Prefix is allocated unless absent, in which case a static empty string is used. Syslog level defaults to warning and must not exceed audit. Non-audit paths acquire a logger with `nf_logger_find_get()` and may return `-EAGAIN` after module request. Eval emits audit records with skb mark and nf skb data, or calls logger backend with hook/device context. Destroy frees dynamic prefix and drops logger references except audit.

State/persistence: expression state is logging configuration, prefix allocation, and logger reference. Dependencies include audit, nf_log, netlink log, module autoloading, and family-specific logger availability. Risks include prefix ownership mistakes, invalid level/group combinations, logger ref imbalance, audit path bypassing logger refs, and logging from packet context under memory pressure. Test signals: syslog and NFLOG modes, audit mode with audit disabled/enabled, prefix length limits, module autoload, invalid group+level/flags combinations, dump round trip, and unload after logger use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_lookup.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_lookup.c

Purpose: implements nftables set lookup expressions, including map value extraction and verdict-map validation.

Important APIs/types/functions: `struct nft_lookup` stores the bound set, source/destination registers, map/invert flags, and binding. `nft_set_do_lookup()` is exported and wraps backend lookup with a base-sequence retry to avoid missing elements across commits. Under retpoline mitigation, `__nft_set_do_lookup()` dispatches directly to known backend lookup functions. `nft_lookup_eval()` performs lookup, catchall fallback, optional map data copy, and element expression update.

Control flow: init looks up the set by name/id and next generation mask, validates key register load, parses invert, validates map destination rules, rejects anonymous maps used only as existence checks, sets binding flags, and binds the set. Eval computes found xor invert; if false, it tries catchall, otherwise breaks. For found extensions, map data is copied to the destination register and set element expressions are updated. Validate walks verdict maps and validates catchall verdicts.

State/persistence: expression state is a set binding; runtime state remains in the set, including dynamic expressions/timeouts. Dependencies include all set backends, nf_tables generation sequencing, set catchall, map datatypes, and transaction activation/deactivation. Risks include missed lookup during generation changes if retry logic regresses, invalid map/invert combinations, anonymous map lifetime, verdict map validation gaps, and retpoline dispatch drift when set backends change. Test signals: positive/negative/inverted lookup, map data extraction, named map lookup-only, anonymous map rejection, catchall entries, concurrent set update lookup retry, verdict map validation, and deactivate/activate/destroy transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_masq.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_masq.c

Purpose: implements nftables `masq` NAT expression for IPv4, IPv6, and inet families, using the outgoing interface address with optional protocol port ranges.

Important APIs/types/functions: `struct nft_masq` stores NAT flags and optional proto min/max source registers. `nft_masq_eval()` builds `nf_nat_range2` and calls `nf_nat_masquerade_ipv4()` or `nf_nat_masquerade_ipv6()`. Family-specific destroy functions release conntrack namespace references. Module init registers IPv6 and inet variants conditionally, IPv4 always, and masquerade inet notifiers.

Control flow: validate requires NAT chain dependency and postrouting hook. Init parses range flags, optional proto registers, defaults max to min, and gets conntrack namespace support for the expression family. Eval loads proto range if configured and dispatches by packet family. Dump emits flags and registers. Init rollback unregisters previously registered families and notifiers on failure.

State/persistence: state is fixed expression metadata and conntrack namespace reference; NAT binding is stored in conntrack by nf_nat masquerade helpers. Dependencies include nf_nat, nf_nat_masquerade, conntrack netns support, NAT chain validation, and family config options. Risks include notifier registration ordering bugs, unsupported family warning path, proto register width mistakes, NAT hook misuse, and IPv6/inet conditional registration inconsistencies. Test signals: IPv4/IPv6/inet masquerade, proto range min-only and min/max, postrouting-only validation, non-NAT chain rejection, notifier cleanup on module unload, interface address changes, and dump/restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_masq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_meta.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_meta.c

Purpose: implements nftables `meta` get/set expressions, inner-meta support, offload matching for selected metadata, and optional secmark objects.

Important APIs/types/functions: `nft_meta_get_eval()` reads skb length, ethertype, nfproto, l4proto, priority, mark, interfaces, socket uid/gid, route classid, secmark, packet type, CPU, cgroup classid, random, xfrm secpath, interface kind, time, and secpath input device. `nft_meta_set_eval()` writes mark, priority, packet type, nftrace, and secmark. `nft_meta_get_init()` and `nft_meta_set_init()` choose register widths. `nft_meta_inner_eval()` supports inner protocol/l4proto for `nft_inner`.

Control flow: select_ops requires exactly one of dreg/sreg and defers bridge family to bridge meta module when needed. Get eval may update packet info for VLAN/PPPoE before protocol/l4proto reads. Several keys can break on missing device, socket, dst, cgroup, or xfrm context. Set init increments the static trace branch for `NFTRACE`, and destroy decrements it. Validation restricts secpath, sdif, and packet-type set to hooks where semantics are valid. Offload supports protocol, l4proto, iif, and iiftype by populating flow dissector matches. Optional secmark object translates security context to secid, refcounts secmark support, and writes skb secmark on eval.

State/persistence: expression state is key/register metadata plus static branch state for nftrace. Secmark objects store allocated context string and computed secid. Dependencies include skb metadata, socket/file credentials under RCU assumptions, netdevices, dst, cgroup, xfrm, security hooks, nf_tables offload, and inner tunnel context. Risks include missing context causing `NFT_BREAK`, static key imbalance, stale secmark labels after policy reload until dump reset recomputes, offload coverage mismatch, and packet-info mutation for VLAN/PPPoE. Test signals: each meta key by family/hook, socket uid/gid closed-socket races, nftrace enable/disable, secpath/sdif hook validation, pkttype set validation, secmark object lifecycle, inner meta via tunnels, and offload match translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_meta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_nat.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_nat.c

Purpose: implements generic nftables `nat` expression for SNAT and DNAT, including IPv4/IPv6 address ranges, protocol port ranges, netmap mode, and inet-family dispatch.

Important APIs/types/functions: `struct nft_nat` stores register indexes, manipulation type, family, and range flags. `nft_nat_setup_addr()`, `nft_nat_setup_proto()`, and `nft_nat_setup_netmap()` build an `nf_nat_range2`. `nft_nat_eval()` calls `nf_nat_setup_info()` for the current conntrack. `nft_nat_validate()` enforces family, NAT chain dependency, and hook masks for SNAT vs DNAT.

Control flow: init requires type and at least address or proto range, maps userspace SNAT/DNAT to `NF_NAT_MANIP_SRC/DST`, validates family compatibility with table family, parses address and proto min/max registers, sets NAT range flags, merges user flags, and gets conntrack namespace support. Eval builds range from current registers; netmap combines current packet address with configured min/max mask; verdict becomes the return from `nf_nat_setup_info()`. Inet eval only runs when packet family matches configured family or family is inet.

State/persistence: expression state is fixed register/family/type metadata and conntrack namespace reference. NAT mappings persist in conntrack entries, not in the expression. Dependencies include nf_conntrack, nf_nat, IP header access, NAT base-chain semantics, and inet conditional registration. Risks include calling eval with null conntrack, address-family/register length mismatch, netmap mask errors, invalid hook acceptance, and inet no-op behavior for mismatched packet family. Test signals: SNAT/DNAT hook validation, IPv4/IPv6 address and port ranges, min-only range defaults, netmap, inet mixed traffic, no-ct behavior, dump/restore, and module init rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_nat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_numgen.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_numgen.c

Purpose: implements nftables `numgen` expression variants for incremental and random bounded number generation.

Important APIs/types/functions: `struct nft_ng_inc` stores destination register, modulus, heap-allocated atomic counter, and offset. `nft_ng_inc_gen()` advances the counter with `atomic_cmpxchg()` and wraps at modulus. `struct nft_ng_random` stores destination register, modulus, and offset; `nft_ng_random_gen()` uses `get_random_u32()` and `reciprocal_scale()`. `nft_ng_select_ops()` dispatches by `NFTA_NG_TYPE`.

Control flow: select_ops requires dreg, modulus, and type. Incremental init parses optional offset, validates nonzero modulus and offset overflow, allocates the counter, initializes it to `modulus - 1` so first generated value is offset, and validates register store. Random init validates the same modulus/offset constraints and destination register but allocates no state. Eval writes the generated u32 to the destination register. Dump emits dreg, modulus, type, and offset.

State/persistence: incremental state is the shared atomic counter per expression; random has no mutable state. Dependencies include kernel random APIs, atomic operations, reciprocal scaling, and nf_tables register parsing. Risks include counter allocation failure, modulo distribution expectations, offset overflow, first-value semantics, and concurrent wrap behavior. Test signals: incremental sequence starting at offset, wrap at modulus, concurrent packet increments without duplicates beyond modulo cycle, random value range, invalid zero modulus/overflow rejection, dump/restore, and type dispatch errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_numgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_objref.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_objref.c

Purpose: implements nftables `objref` expressions that invoke named stateful objects directly or select objects from object maps.

Important APIs/types/functions: immediate mode stores a `struct nft_object *` in expression private data and `nft_objref_eval()` calls `obj->ops->eval()`. `nft_objref_map` stores an object set, key source register, and binding; `nft_objref_map_eval()` looks up a set element, falls back to catchall, extracts `nft_set_ext_obj()`, and evaluates that object. `nft_objref_validate_obj_type()` applies special hook/family validation for synproxy objects.

Control flow: select_ops chooses map mode if set source register plus set name/id are present, or immediate mode if object name/type are present. Immediate init looks up the object by name/type in the next generation and increments its use count; activate/deactivate restore/decrement use around transactions. Map init looks up an object set, validates `NFT_SET_OBJECT`, parses the key register, and binds the set. Map lifecycle activates/deactivates/destroys the set binding.

State/persistence: expression state holds object refs or set bindings. Runtime object state is owned by the target object type. Dependencies include nft object registry, set lookup exported by `nft_lookup.c`, catchall object maps, transaction use counters, and synproxy hook constraints. Risks include use-count imbalance, object type mismatch in maps, missing catchall causing `NFT_BREAK`, and validation gaps for object types with hook restrictions. Test signals: immediate counter/quota/limit object references, object map lookup and catchall, synproxy validation, transaction rollback, object deletion while referenced, invalid set/object types, and dump round trip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_objref.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_osf.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_osf.c

Purpose: implements nftables passive OS fingerprint expression `osf` for IPv4 TCP SYN packets, writing a genre or genre:version string to a register.

Important APIs/types/functions: `struct nft_osf` stores destination register, TTL matching mode, and flags. `nft_osf_eval()` validates IPv4, TCP, non-fragment, SYN-only packets, calls `nf_osf_find()` against `nf_osf_fingers`, and pads the result into `NFT_OSF_MAXGENRELEN`. `nft_osf_validate()` restricts use to IPv4/inet prerouting, local-in, and forward hooks.

Control flow: init requires destination register, accepts TTL values 0..2, accepts only `NFT_OSF_F_VERSION`, and validates a destination register store of the fixed OSF string length. Eval breaks for unsupported family/protocol/fragments/non-SYN or missing TCP header. If no fingerprint matches, it writes `"unknown"`; with version flag it formats genre and version, otherwise genre only. Dump emits TTL, flags, and dreg.

State/persistence: expression state is fixed metadata; fingerprint data is global OSF data outside this file. Dependencies include IPv4 and TCP header parsing, nfnetlink OSF fingerprint tables, and nf_tables register storage. Risks include IPv4-only behavior in inet tables, reliance on loaded fingerprint database, string truncation/padding, endian oddity in flags dump, and fragmented SYN handling. Test signals: known and unknown fingerprints, version flag formatting, TTL modes, non-SYN/TCP/IPv4 break behavior, fragment rejection, hook validation, fixed-length register writes, and dump/restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_osf.c -->
