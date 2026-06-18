# Research Group: subset-b-006216

This grouped report covers the IPv6 route, RPL Segment Routing, and SRv6 tunnel/HMAC files requested for subset B. Each file section is delimited for deterministic reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/route.c -->
# sources/distributed-fs/ceph-client/net/ipv6/route.c

## Purpose

`route.c` is the IPv6 FIB front-end and dst-cache implementation. It turns route configuration, fib6 trie lookups, policy rules, nexthops, device state, PMTU updates, ICMP redirects, and rtnetlink/ioctl requests into usable `struct rt6_info` destination entries. It owns the AF_INET6 `dst_ops`, special unreachable/prohibit/blackhole route entries, per-net route sysctls/proc output, route netlink handlers, and lifecycle registration for IPv6 route support.

## Important APIs, Types, And Functions

The core externally visible APIs are `ip6_route_lookup()`, `rt6_lookup()`, `ip6_pol_route()`, `ip6_route_input_lookup()`, `ip6_route_input()`, `ip6_route_output_flags()`, `ip6_blackhole_route()`, `ip6_update_pmtu()`, `ip6_sk_update_pmtu()`, `ip6_redirect()`, `ip6_sk_redirect()`, `ip6_route_add()`, `ip6_del_rt()`, `ipv6_route_ioctl()`, `addrconf_f6i_alloc()`, `rt6_add_dflt_router()`, `rt6_get_dflt_router()`, `rt6_purge_dflt_routers()`, `rt6_sync_up()`, `rt6_sync_down_dev()`, `rt6_disable_ip()`, `rt6_mtu_change()`, `inet6_rt_notify()`, `fib6_rt_update()`, `fib6_info_hw_flags_set()`, `ip6_route_init()`, and `ip6_route_cleanup()`.

Key internal state is stored in `struct fib6_info`, `struct fib6_nh`, `struct fib6_result`, `struct rt6_info`, `struct rt6_exception`, and per-net `net->ipv6` fields. The file defines per-CPU `rt6_uncached_list` lists for uncached dsts, `rt6_exception_lock` for nexthop exception buckets, `ip6_dst_ops_template`, `ip6_dst_blackhole_ops`, and templates for null/prohibit/blackhole entries.

Lookup helpers include `fib6_table_lookup()`, `rt6_select()`, `fib6_select_path()`, `rt6_multipath_hash()`, `rt6_find_cached_rt()`, `ip6_create_rt_rcu()`, `ip6_rt_cache_alloc()`, and per-CPU cache helpers `rt6_get_pcpu_route()` / `rt6_make_pcpu_route()`. Mutation helpers include `fib6_nh_init()`, `ip6_route_info_create()`, `ip6_route_info_create_nh()`, `__ip6_ins_rt()`, `ip6_route_del()`, `ip6_route_multipath_add()`, and `ip6_route_multipath_del()`.

## Control Flow

Input lookup starts in `ip6_route_input()`, builds `flowi6` from the packet, performs early flow dissection for multipath hashing, and installs a no-ref dst from `ip6_route_input_lookup()`. That calls fib rules with `ip6_pol_route_input()`, which delegates to `ip6_pol_route()`. Output lookup follows `ip6_route_output_flags()`, which wraps `ip6_route_output_flags_noref()` under RCU and safely takes a dst ref unless the returned dst is already on the uncached list.

`ip6_pol_route()` performs policy-table lookup, then `fib6_table_lookup()`, then `fib6_select_path()` for ECMP/nexthop-object selection. It checks per-nexthop exception buckets first. If no exception is found, it either creates a special uncached clone for `FLOWI_FLAG_KNOWN_NH` or creates/uses a per-CPU route copy. `ip6_pol_route_lookup()` is a similar rule callback that returns a referenced `rt6_info` and creates a fresh dst when needed.

Route addition flows from rtnetlink `inet6_rtm_newroute()` or ioctl through `rtm_to_fib6_config()` / `rtmsg_to_fib6_config()`, `fib6_config_validate()`, `ip6_route_info_create()`, nexthop initialization, and `fib6_add()` under the table lock. Multipath add parses each `rtnexthop`, creates one `fib6_info` per nexthop, inserts them as siblings, then emits consolidated notifications and rolls back partial insertion on failure. Deletion locates matching fib6 nodes, optionally removes cached exceptions, and deletes one route or all siblings depending on gateway/multipath flags.

PMTU and redirect events create or update exception routes. `__ip6_rt_update_pmtu()` lowers metrics in place where safe, or allocates a route-cache clone and inserts it into a nexthop exception bucket. `rt6_do_redirect()` validates ICMPv6 Redirect constraints, updates neighbor state, creates a dynamic gateway/on-link cache exception, and notifies `NETEVENT_REDIRECT`.

## State And Persistence Behavior

Persistent route state lives in fib6 tables within each network namespace. Per-net special routes and sysctls are initialized by `ip6_route_net_init()`; late proc entries are created by `ip6_route_net_init_late()`. Per-CPU dst cache entries hang off nexthops and are invalidated by route generation IDs. Exception routes are per-nexthop hash buckets protected by `rt6_exception_lock` and RCU-freed, with randomized depth pruning to limit side-channel exposure. Uncached dsts are tracked per CPU so device teardown can replace references with `blackhole_netdev`.

Expiration is split across fib routes and dst clones: `RTF_EXPIRES` routes use `dst.expires` or `fib6_info->expires`; GC scans exception buckets and fib GC lists. PMTU exceptions set `RTF_MODIFIED` and expire after `ip6_rt_mtu_expires`. RA route information and default routers are added with finite or infinite lifetimes and are purged when RA policy no longer accepts them.

## Dependencies And Integration Points

This file integrates with `net/ipv6` FIB internals (`ip6_fib`, fib6 rules, nexthop objects), dst and xfrm, neighbor discovery, addrconf, l3mdev/VRF routing, rtnetlink, netdevice notifiers, lightweight tunnels, netevent notifiers, SNMP stats, procfs, sysctl, BPF iterators, and optional IPv6 subtrees, router preferences, multicast routing, multiple tables, and proc/BPF support. It also cooperates directly with lwtunnel encapsulations such as SRv6/RPL through `fib_nh_common_init()`, `lwtunnel_set_redirect()`, and `lwtunnel_headroom()`.

## Risks And Edge Cases

The main risks are lifetime and concurrency bugs: dst references are mixed with no-ref lookup paths, RCU-held `fib6_info` references, per-CPU route caches, and exception bucket mutation. Device unregister/down paths must reliably replace or release dst device references, especially for uncached routes. PMTU and redirect exceptions are security-sensitive because untrusted network events can create cached route state; the code validates redirect source/gateway, multicast targets, neighbor options, and PMTU bounds. Multipath route add/delete has partial failure rollback and notification ordering risks. Netlink parsing must reject unsupported IPv6 attributes, invalid gateway/local addresses, internal flags such as `RTF_CACHE`/`RTF_PCPU`, and inconsistent nexthop-object combinations.

## Test Signals

Useful signals are IPv6 route selftests via `ip -6 route add/del/get`, multipath and nexthop-object tests, PMTU tests that verify exception creation/expiration, ICMPv6 redirect tests, VRF/l3mdev link-scope tests, route dump filtering and cloned exception dumps, device down/unregister tests, RA default-router lifetime tests, and lockdep/KASAN/RCU validation under route churn. Runtime observability includes rtnetlink notifications, `/proc/net/ipv6_route`, `/proc/net/rt6_stats`, route sysctls, fib6 tracepoints, and BPF iterator output when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/route.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/rpl.c -->
# sources/distributed-fs/ceph-client/net/ipv6/rpl.c

## Purpose

`rpl.c` implements address compression and decompression for IPv6 RPL Source Routing Headers. It converts between expanded `struct ipv6_rpl_sr_hdr` segment address arrays and compressed segment data that omits the shared prefix with the packet destination address.

## Important APIs, Types, And Functions

The exported helpers are `ipv6_rpl_srh_decompress()` and `ipv6_rpl_srh_compress()`. They operate on `struct ipv6_rpl_sr_hdr`, `struct in6_addr`, and the `cmpri` / `cmpre` compression fields. Internal helpers are `ipv6_rpl_addr_decompress()`, `ipv6_rpl_addr_compress()`, `ipv6_rpl_segdata_pos()`, `ipv6_rpl_srh_calc_cmpri()`, and `ipv6_rpl_srh_calc_cmpre()`.

`IPV6_PFXTAIL_LEN(x)` computes the copied suffix length for an omitted prefix length, and `IPV6_RPL_BEST_ADDR_COMPRESSION` is the all-but-one-byte compression result used when a segment fully shares the destination prefix.

## Control Flow

Decompression copies fixed header fields, computes an expanded header length for `n + 1` full IPv6 addresses, clears compression fields, then reconstructs the first `n` addresses with `cmpri` and the final address with `cmpre`. Compression first finds the longest common prefix between the destination and all non-final segments (`cmpri`) and between the destination and final segment (`cmpre`). It then computes packed segment length and padding, copies fixed fields, stores compression values, and writes only the suffix bytes for each segment.

## State And Persistence Behavior

The file is stateless. It writes only caller-provided output buffers and does not allocate memory, retain references, or modify global/per-net state. Correctness depends on callers providing buffers sized for the compressed or decompressed result and a valid segment count `n`.

## Dependencies And Integration Points

It depends on `<net/rpl.h>` for the RPL SRH layout and is used by RPL lightweight tunnel code to compress the inline source routing header before inserting it into packets. The compression format is coupled to `rpl_iptunnel.c`, which validates uncompressed SRHs from netlink and then calls `ipv6_rpl_srh_compress()` while building packets.

## Risks And Edge Cases

The helpers trust the caller's segment count and buffer sizing, so validation must happen before entry. Prefix length arithmetic is byte-oriented, not bit-oriented; this matches the implementation's compressed-byte model but would be dangerous if used with arbitrary bit prefix lengths. The "best compression" value is 15 rather than 16, so a fully matching address still contributes one suffix byte. Header length and padding are recomputed during compression, so callers must not reuse stale lengths from partially initialized headers.

## Test Signals

Round-trip tests should cover no shared prefix, partial shared prefixes, full shared prefix, different final-segment compression, padding when compressed data is not 8-byte aligned, and segment counts of one and several hops. Integration tests should verify that RPL tunnel insertion produces valid packets that downstream RPL parsing can decompress to the original segment list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/rpl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/rpl_iptunnel.c -->
# sources/distributed-fs/ceph-client/net/ipv6/rpl_iptunnel.c

## Purpose

`rpl_iptunnel.c` registers the RPL lightweight tunnel encapsulation type and implements packet input/output handling that inserts an RPL Source Routing Header inline into IPv6 packets. It lets routes carry an RPL SRH through `LWTUNNEL_ENCAP_RPL`.

## Important APIs, Types, And Functions

The private tunnel state is `struct rpl_lwt`, containing a `dst_cache` and flexible `struct rpl_iptunnel_encap` SRH storage. Accessors `rpl_lwt_lwtunnel()` and `rpl_encap_lwtunnel()` decode `lwtunnel_state->data`.

Netlink/lwtunnel operations are implemented by `rpl_build_state()`, `rpl_destroy_state()`, `rpl_output()`, `rpl_input()`, `rpl_fill_encap_info()`, `rpl_encap_nlsize()`, and `rpl_encap_cmp()`, collected in `rpl_ops`. Module-level registration is through `rpl_init()` and `rpl_exit()`. Packet rewriting is centered on `rpl_do_srh_inline()` and `rpl_do_srh()`.

## Control Flow

`rpl_build_state()` accepts only AF_INET6 routes, parses nested `RPL_IPTUNNEL_SRH`, validates the SRH, allocates lwtunnel state, initializes a dst cache, copies the SRH, and marks the state for input and output redirects. Validation requires the byte length to match `hdrlen`, at least one segment, `segments_left * sizeof(in6_addr)` to match the segment payload length, no pre-existing RPL compression, no loop per `ipv6_chk_rpl_srh_loop()`, and a non-multicast final segment.

On output, `rpl_output()` gets a cached dst, calls `rpl_do_srh()`, and if no cached dst exists performs a fresh `ip6_route_output()` for the rewritten destination. It avoids caching if the new dst has the same lwtstate, preventing reference loops. It then swaps the skb dst and calls `dst_output()`. Input is similar but calls `ip6_route_input()`, forces a dst reference from the no-ref route, caches when safe, and hands the packet to `dst_input()`.

`rpl_do_srh_inline()` copies the old IPv6 header, builds an intermediate uncompressed RPL segment list by shifting configured segments and appending the original destination, compresses it relative to the first configured segment, grows headroom, rewrites the IPv6 header and routing header, sets `hdr->daddr` to the first segment, updates `payload_len`, transport header, and checksum state, and frees the temporary buffer.

## State And Persistence Behavior

Each lwtunnel state persists a validated SRH and one `dst_cache`. State is attached to routes and destroyed with `dst_cache_destroy()`. Cached routes are soft state and are deliberately not installed if they would form an lwtstate loop. The file does not own global state beyond registering/unregistering the encapsulation ops.

## Dependencies And Integration Points

It integrates with netlink attributes from `linux/rpl_iptunnel.h`, IPv6 route lookup/output/input, `dst_cache`, the lwtunnel core, and the RPL compression helpers in `rpl.c`. It is selected by route nexthop lightweight tunnel attributes and runs in both forwarding/input and local output paths depending on route use.

## Risks And Edge Cases

The main packet risks are malformed SRH lengths, insufficient headroom, checksum adjustment mistakes, and dst reference loops. Validation rejects compressed user-provided headers because this code expects to control compression during packet rewrite. The temporary buffer allocation size depends on `segments_left`; validation must ensure segment length and `segments_left` remain consistent. Input routing must force a reference after `ip6_route_input()` because that route path installs a no-ref dst.

## Test Signals

Tests should add IPv6 routes with `encap rpl` SRHs, verify invalid SRHs are rejected, send packets through input and output lwt paths, inspect resulting routing headers and destination rewrite, and confirm repeated traffic uses cache without dst loops. Fault-injection or KASAN tests around headroom growth and allocation failure would exercise the drop paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/rpl_iptunnel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/seg6.c -->
# sources/distributed-fs/ceph-client/net/ipv6/seg6.c

## Purpose

`seg6.c` is the core SRv6 control module. It validates SRH layout, extracts SRHs from packets, handles ICMP-invoking packet SRH metadata, exposes generic netlink commands for SRv6 HMAC keys and tunnel source address, initializes per-net SRv6 data, and registers the SRv6 tunnel/local subsystems.

## Important APIs, Types, And Functions

Exported helpers include `seg6_validate_srh()`, `seg6_get_srh()`, `seg6_icmp_srh()`, `seg6_init()`, and `seg6_exit()`. Per-net state is `struct seg6_pernet_data`, reached through `seg6_pernet(net)`, and contains a mutex, RCU-protected `tun_src`, and HMAC rhashtable when HMAC is configured.

Generic netlink handlers are `seg6_genl_sethmac()`, `seg6_genl_dumphmac_start()`, `seg6_genl_dumphmac()`, `seg6_genl_dumphmac_done()`, `seg6_genl_set_tunsrc()`, and `seg6_genl_get_tunsrc()`. They are registered under `seg6_genl_family` with admin permission flags for mutating/dumping protected state.

## Control Flow

`seg6_validate_srh()` verifies SRH type 4, exact encoded length, `segments_left` versus `first_segment` rules, and TLV bounds. For reduced SRH validation it permits `segments_left` to be at most `first_segment + 1`; otherwise it requires `segments_left <= first_segment`. It then walks trailing TLVs, ensuring every TLV header and declared length fits inside the SRH.

`seg6_get_srh()` uses `ipv6_find_hdr()` to locate a routing header, pulls enough skb data for the fixed and full SRH, reloads pointers after pull, and returns only a valid reduced-form SRH. `seg6_icmp_srh()` temporarily points the skb network header at the invoking packet inside an ICMP payload, calls `seg6_get_srh()`, records `IP6SKB_SEG6` and `srhoff` when found, then restores the original network header.

For HMAC configuration, `seg6_genl_sethmac()` validates key ID, secret length, algorithm, and optional secret. A zero secret length deletes a key; nonzero length replaces any existing key under the per-net mutex and inserts a prepared `seg6_hmac_info`. Dumping walks the per-net rhashtable with `rhashtable_walk_*`. Tunnel source updates allocate a new `in6_addr`, publish it with RCU, synchronize, then free the old pointer.

`seg6_init()` registers per-net state, generic netlink, SRv6 iptunnel ops, and SRv6 local behavior in order; failure unwinds in reverse. `seg6_exit()` unregisters local behavior, iptunnel ops, genl family, and per-net state.

## State And Persistence Behavior

State is per network namespace and allocated in `seg6_net_init()`. `tun_src` is RCU-protected and defaults to the all-zero address. HMAC information is stored in the per-net rhashtable initialized by `seg6_hmac_net_init()`. Generic netlink changes persist until key deletion, namespace teardown, or module cleanup. Per-net teardown frees HMAC state, tunnel source, and the container.

## Dependencies And Integration Points

The file depends on IPv6 packet parsing, generic netlink, `net/seg6.h`, `linux/seg6_genl.h`, optional `net/seg6_hmac.h`, and initialization hooks from `seg6_iptunnel` and `seg6_local`. The tunnel source is consumed by SRv6 iptunnel code when routes do not specify a per-route source.

## Risks And Edge Cases

SRH validation is security-critical because packet parsers and tunnel code rely on computed offsets. Incorrect reduced-header handling could accept impossible `segments_left` values or overrun TLVs. Generic netlink HMAC dumping exposes configured secrets to admin users, which is expected here but sensitive. `seg6_genl_get_tunsrc()` assumes `tun_src` exists after per-net initialization; per-net lifecycle ordering must preserve that invariant. HMAC code is compiled out cleanly by returning `-ENOTSUPP`, so callers must tolerate that.

## Test Signals

Good tests include SRH parser fuzzing, valid/reduced SRH extraction from nonlinear skbs, ICMP error metadata propagation, generic netlink set/get tunnel source, HMAC add/delete/dump with invalid lengths and algorithms, namespace create/destroy leak checks, and init unwind tests with fault injection in each registration step.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/seg6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/seg6_hmac.c -->
# sources/distributed-fs/ceph-client/net/ipv6/seg6_hmac.c

## Purpose

`seg6_hmac.c` implements SRv6 HMAC key storage, HMAC computation, inbound validation, and outbound HMAC TLV population. It supports SHA-1 and SHA-256 algorithms for SRH authentication material.

## Important APIs, Types, And Functions

The main exported APIs are `seg6_hmac_compute()`, `seg6_hmac_validate_skb()`, `seg6_hmac_info_lookup()`, `seg6_hmac_info_add()`, `seg6_hmac_info_del()`, `seg6_push_hmac()`, `seg6_hmac_net_init()`, and `seg6_hmac_net_exit()`. Key records are `struct seg6_hmac_info`, stored in a per-net rhashtable keyed by `hmackeyid`. `struct hmac_storage` provides a per-CPU ring buffer protected by `local_lock_t` for building the HMAC input text.

Internal helpers include `seg6_get_tlv_hmac()` for locating the fixed-position HMAC TLV at the end of an SRH, `seg6_hinfo_release()` / `seg6_free_hi()` for RCU freeing, and `rht_params` for rhashtable configuration.

## Control Flow

`seg6_get_tlv_hmac()` first checks that the SRH is long enough for the segment list plus HMAC TLV area, then requires `sr_has_hmac()`, locates the TLV 40 bytes before the encoded end of the SRH, and verifies type and length.

`seg6_hmac_compute()` builds the RFC-style authentication text from source address, first-segment, flags, big-endian key ID, and all segment addresses. It rejects inputs that exceed the fixed per-CPU ring buffer, disables bottom halves, locks the per-CPU buffer, copies the fields, runs the configured HMAC algorithm, zero-pads the SHA-1 result to the SRv6 HMAC field length, and unlocks. Unsupported algorithms trigger a one-time warning and `-EINVAL`.

`seg6_hmac_validate_skb()` reads the per-interface `seg6_require_hmac` policy. A positive value requires a TLV; a negative value disables validation; zero validates only if a TLV is present. When validation is required or present, it looks up the key under RCU, computes expected bytes, and uses `crypto_memneq()` for constant-time comparison.

`seg6_hmac_info_add()` prepares algorithm-specific key material before inserting into the rhashtable. Delete removes the key and RCU-frees it. `seg6_push_hmac()` finds the TLV, zeroes the output field, looks up the key, computes, and writes the HMAC for outbound packet construction.

## State And Persistence Behavior

HMAC keys persist per network namespace in `seg6_pernet_data->hmac_infos`. Records are looked up locklessly under RCU and removed with RCU freeing, while administrative mutation is serialized by callers in `seg6.c`. The compute buffer is per-CPU scratch state only and is not persisted. Per-net initialization creates the rhashtable, and exit frees all records through `rhashtable_free_and_destroy()`.

## Dependencies And Integration Points

This file depends on SRv6 core state from `seg6.c`, crypto helpers for SHA-1/SHA-256 HMAC, IPv6 skb layout, per-interface IPv6 configuration, and generic netlink-managed key records. `seg6_iptunnel.c` calls `seg6_push_hmac()` when adding outbound SRHs that carry an HMAC TLV, while SRH receive logic can call `seg6_hmac_validate_skb()` based on interface policy.

## Risks And Edge Cases

The HMAC input has a hard ring size limit that currently allows 14 segments; larger segment lists fail with `-EMSGSIZE`. Correctness depends on callers passing a validated SRH, because TLV positioning is computed from header fields. SHA-1 outputs are zero-padded, so comparison length remains fixed but security strength follows SHA-1. Key dumps elsewhere expose secrets to privileged generic netlink readers. The local lock and bottom-half disabling are important because compute can run in packet paths; removing them would corrupt per-CPU scratch data.

## Test Signals

Tests should cover SHA-1 and SHA-256 vectors, invalid algorithms, missing HMAC TLV, wrong TLV length/type, policies `require`, `optional`, and `ignore`, wrong key ID, tampered segment list/source address, max segment count boundary, and concurrent add/delete/validate under RCU with KASAN/lockdep enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/seg6_hmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/seg6_iptunnel.c -->
# sources/distributed-fs/ceph-client/net/ipv6/seg6_iptunnel.c

## Purpose

`seg6_iptunnel.c` implements SRv6 lightweight tunnel encapsulation for route nexthops. It inserts SRHs inline or encapsulates IPv4, IPv6, or Ethernet payloads inside an outer IPv6/SRH header, supports reduced encapsulation modes, optional per-route tunnel source addresses, HMAC population, dst caching, and netfilter hooks around lwtunnel processing.

## Important APIs, Types, And Functions

The private lwtunnel state is `struct seg6_lwt`, containing input/output `dst_cache` objects, a per-route `tunsrc`, and flexible `struct seg6_iptunnel_encap` data. The route-facing ops are `seg6_build_state()`, `seg6_destroy_state()`, `seg6_input()`, `seg6_output()`, `seg6_fill_encap_info()`, `seg6_encap_nlsize()`, and `seg6_encap_cmp()`, collected in `seg6_iptun_ops`. Registration is via `seg6_iptunnel_init()` and `seg6_iptunnel_exit()`.

Packet rewrite helpers are `__seg6_do_srh_encap()`, `seg6_do_srh_encap()`, `seg6_do_srh_encap_red()`, `__seg6_do_srh_inline()`, exported `seg6_do_srh_inline()`, and dispatcher `seg6_do_srh()`. Source and flow metadata helpers include `seg6_lwt_headroom()`, `set_tun_src()`, and `seg6_make_flowlabel()`.

## Control Flow

`seg6_build_state()` parses nested `SEG6_IPTUNNEL_SRH` and optional `SEG6_IPTUNNEL_SRC`, accepts AF_INET/AF_INET6 depending on mode, validates mode constraints, validates the SRH with `seg6_validate_srh(..., reduced=false)`, allocates state, initializes two dst caches, copies tunnel info, validates per-route source address, sets lwtunnel type/redirect flags/headroom, and returns the state.

`seg6_do_srh()` dispatches by mode. Inline mode requires an IPv6 skb and inserts the SRH after the existing IPv6 header. ENCAP/ENCAP_RED handles offloads, accepts IPv4 or IPv6 payloads, chooses `IPPROTO_IPV6` or `IPPROTO_IPIP`, pushes an outer IPv6 header and SRH, and changes skb protocol to IPv6. L2ENCAP modes require a valid MAC header, copy L2 bytes into the inner payload, and use `IPPROTO_ETHERNET`.

Full encapsulation pushes an outer IPv6 header plus SRH, inherits traffic class/hop-limit from IPv6 inner packets or initializes IPv6 control block for non-IPv6 payloads, sets the outer destination to the first segment, selects source by per-route source, per-net source, or dynamic address selection, optionally computes HMAC, fixes payload length and checksum. Reduced encapsulation omits the first SID from the SRH, and for one-SID/no-HMAC cases can skip the SRH entirely and put the SID directly in the outer destination.

Input and output paths both use separate dst caches. If a cache miss occurs, output builds a `flowi6` and calls `ip6_route_output()`, while input calls `ip6_route_input()` and forces a dst reference from the no-ref result. Both avoid caching when the resulting dst uses the same lwtstate, grow link-layer headroom as needed, install the new dst, and call `dst_input()` or `dst_output()`. When lwtunnel netfilter hooks are enabled, pre/post routing and local-out hooks wrap processing.

## State And Persistence Behavior

Route-attached lwtunnel state persists the SRH, mode, optional tunnel source, and caches until route teardown. Two caches are maintained so input and output route resolutions do not alias. Per-route source overrides per-net SRv6 `tun_src`, and dynamic source selection is fallback only. HMAC bytes are generated per packet and not stored in state. The module registers one lwtunnel encap type and owns no additional global mutable state.

## Dependencies And Integration Points

The file integrates with lwtunnel route attributes from `linux/seg6_iptunnel.h`, SRH validation and per-net data from `seg6.c`, optional HMAC from `seg6_hmac.c`, IPv6 route lookup, dst cache, offload helpers, netfilter lwtunnel static key, address selection, and lightweight tunnel headroom accounting used by IPv6 route MTU calculations.

## Risks And Edge Cases

High-risk areas are skb headroom manipulation, reduced SRH length calculations, HMAC recomputation after reduced-header edits, dst cache reference loops, offload handling, and protocol transitions for IPv4/L2 payloads. Inline mode is IPv6-only and rejects other protocols. Per-route tunnel source rejects any, multicast, and loopback addresses, but dynamic/per-net source still depends on address-selection success. Reduced mode can skip the SRH only in the one-SID/no-HMAC case; future TLVs or flags would need to revisit that assumption, as noted by the source comment.

## Test Signals

Tests should cover all five modes, IPv4 and IPv6 encap, L2 encap with and without MAC headers, reduced one-SID skip behavior, reduced multi-SID TLV copying, HMAC TLV population, per-route versus per-net tunnel source selection, invalid SRH/mode/source rejection, dst cache hit/miss and loop avoidance, netfilter hook enabled paths, GSO/offload handling, and packet capture validation of outer header, next-header, destination SID, payload length, and checksum state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/seg6_iptunnel.c -->
