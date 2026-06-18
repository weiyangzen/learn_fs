# Research: subset-b-006203

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/route.c -->
# sources/distributed-fs/ceph-client/net/ipv4/route.c

## Purpose

This file is the IPv4 route resolution and route-dst implementation for the kernel networking stack. It builds and validates `struct rtable` destinations for input, output, multicast, broadcast, local, unreachable, blackhole, redirect, PMTU, and netlink `RTM_GETROUTE` paths. It also owns IPv4 route-related dst operations, route cache statistics proc files, per-next-hop exception state for redirects/PMTU, IP ID generation, multipath hash selection, per-net route sysctls, route generation IDs, and inet peer allocation.

## Important APIs, Types, and Functions

- `ipv4_dst_ops` and `ipv4_dst_blackhole_ops`: `struct dst_ops` instances for normal IPv4 dst entries and blackhole dst entries. They provide check, MTU, MSS, PMTU update, redirect, neighbour lookup, and destroy hooks.
- `ip_tos2prio`: exported DS/TOS-to-traffic-priority table.
- `rt_cache_stat`: per-CPU route statistics exposed through proc when `CONFIG_PROC_FS` is enabled.
- `__ip_select_ident()`: exported IP identification generator using per-net siphash keys and global randomized id buckets.
- `struct fib_nh_exception` helpers: `update_or_create_fnhe()`, `find_exception()`, `rt_bind_exception()`, `ip_del_fnhe()`, and `fnhe_flush_routes()` maintain per-nexthop exceptions for redirect gateway and path MTU.
- Redirect and PMTU APIs: `ip_rt_send_redirect()`, `ipv4_redirect()`, `ipv4_sk_redirect()`, `ipv4_update_pmtu()`, `ipv4_sk_update_pmtu()`, and internal `__ip_do_redirect()` / `__ip_rt_update_pmtu()`.
- Route lookup APIs: `ip_route_input_noref()`, `ip_route_use_hint()`, `ip_route_output_key_hash()`, `ip_route_output_key_hash_rcu()`, `ip_route_output_flow()`, `rt_dst_alloc()`, `rt_dst_clone()`, and `ipv4_blackhole_route()`.
- Multipath support under `CONFIG_IP_ROUTE_MULTIPATH`: `fib_multipath_hash()` and helpers for L3, L4, inner, outer, and custom hash field policies.
- Netlink route query support: `inet_rtm_valid_getroute_req()`, `inet_rtm_getroute_build_skb()`, `inet_rtm_getroute()`, `rt_fill_info()`, and `fib_dump_info_fnhe()`.
- Sysctl and init hooks: `sysctl_route_net_init()`, `netns_ip_rt_init()`, `rt_genid_init()`, `ipv4_inetpeer_init()`, `ip_rt_init()`, and `ip_static_sysctl_init()`.

## Control Flow

Input routing enters through `ip_route_input_noref()`, takes RCU, and calls `ip_route_input_rcu()`. Multicast destinations are handled first through `ip_route_input_mc()` after IGMP membership / multicast-forwarding checks. Other packets go to `ip_route_input_slow()`, which rejects martian source/destination cases, builds a `flowi4`, optionally does early flow dissection, performs `fib_lookup()`, handles broadcast/local/unreachable cases, and creates or reuses an input `rtable`. Forwarded unicast traffic is routed by `ip_mkroute_input()` and `__mkroute_input()`, which validate source addresses, determine redirect eligibility, bind any nexthop exception, cache the route if safe, and attach the dst to the skb.

Output routing enters through `ip_route_output_key_hash()` or the RCU variant. The function normalizes source, destination, output interface, loopback, multicast, broadcast, and local-route cases before doing `fib_lookup()` and `fib_select_path()`. `__mkroute_output()` then validates the egress device, handles route-localnet restrictions, recognizes broadcast/multicast/local special cases, checks per-nexthop or per-CPU cached routes, allocates an `rtable`, sets output/input functions, binds lwtunnel state, and caches or marks the route uncached.

Redirect handling starts with dst callback `ip_do_redirect()` or exported wrappers `ipv4_redirect()` and `ipv4_sk_redirect()`. They build a `flowi4`, validate the ICMP redirect code, old gateway, device policy, secure redirects, on-link constraints, and neighbour state. Valid redirects update per-nexthop exception gateway state and can kill the current dst. `ip_rt_send_redirect()` sends outbound ICMP redirects with inet-peer rate/backoff state.

PMTU updates use the same per-nexthop exception mechanism. `ip_rt_update_pmtu()` and socket-specific wrappers build a flow key, route if needed, clamp below the namespace minimum PMTU when configured, and update one or all multipath nexthop exceptions. Socket update flow also deals with locked sockets, stale dsts, xfrm dst paths, and replacing `sk_dst_cache` when a new route is needed.

Netlink `RTM_GETROUTE` builds a synthetic IPv4 skb so the normal input or output route lookup engine can be reused. Strict requests are validated by `inet_rtm_valid_getroute_req()`. The response is either cloned route information from `rt_fill_info()` or an exact FIB match through `fib_dump_info()` when `RTM_F_FIB_MATCH` is requested.

Initialization in `ip_rt_init()` allocates IP ID hash storage, initializes uncached route lists, allocates route accounting if configured, creates dst caches, initializes devinet/FIB/XFRM/proc/netlink/sysctl/pernet components, and registers route generation and inet peer per-net operations.

## State and Persistence Behavior

Route state is mostly in memory and scoped by dst entries, FIB nexthops, and network namespaces. Cached input routes live in `nhc_rth_input`; cached output routes live in per-CPU `nhc_pcpu_rth_output`; routes that fail cache insertion or have no FIB info are linked into per-CPU `rt_uncached_list`. `rt_genid` invalidates dsts after route cache flushes, and `fnhe_genid` invalidates nexthop exceptions. Per-nexthop exceptions persist redirect gateway, PMTU, lock state, expiration, and cached input/output dst pointers until timeout, generation change, deletion, or RCU free.

The file also owns global randomized IP ID bucket arrays (`ip_idents`, `ip_tstamps`) and per-net siphash keys used to avoid simple global ID inference. Inet peer bases are allocated per network namespace and store redirect/error rate state. Proc and sysctl state exposes counters and tunables; writes to route flush sysctl bump both route and exception generation IDs.

## Dependencies and Integration Points

This code sits between the IPv4 FIB/rules engine, dst cache, neighbour/ARP, ICMP, XFRM, lwtunnel, multicast routing, procfs, sysctl, netlink/rtnetlink, net namespaces, and device configuration. It relies heavily on `fib_lookup()`, `fib_select_path()`, `fib_validate_source()`, `fib_multipath_hash_from_keys()`, device configuration macros such as `IN_DEV_FORWARD()` and `IN_DEV_ROUTE_LOCALNET()`, neighbour helpers for IPv4/IPv6 nexthops, and dst lifetime primitives. TCP and ICMP depend on its exported PMTU/redirect and route output helpers.

## Risks and Edge Cases

- Concurrency is delicate: exception tables use a single spinlock plus RCU; route caches use lockless `cmpxchg`; uncached lists are per-CPU with bottom-half locks; dst device references must be preserved on cache replacement and flush.
- Redirect and PMTU exception state can stale routes if generation IDs, expiration checks, or `dst.obsolete` transitions are wrong.
- Martian filtering, `route_localnet`, L3 master devices, proxy ARP, broadcast forwarding, and multicast forwarding all have policy-specific branches that can create security regressions if reordered.
- Multipath hash policies affect flow distribution and ICMP error behavior; custom hash fields must handle absent inner headers and `FLOWI_FLAG_ANY_SPORT` randomization.
- Netlink strict validation must keep `RTM_GETROUTE` from accepting unsupported attributes while maintaining legacy non-strict behavior.
- Namespace sysctl registration mutates table data pointers for non-init namespaces; pointer adjustment and cleanup must remain paired.

## Test Signals

Strong signals include IPv4 forwarding/local delivery tests, martian source/destination tests, multicast and broadcast routing tests, PMTU discovery with multipath and locked MTU routes, ICMP redirect accept/reject behavior, route cache flush/sysctl behavior, `ip route get` netlink tests with strict attributes and `RTM_F_FIB_MATCH`, XFRM route output, lwtunnel redirect paths, L3 master/VRF routes, route namespace creation/destruction, and stress tests for concurrent FIB updates, dst invalidation, and device teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/route.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/syncookies.c -->
# sources/distributed-fs/ceph-client/net/ipv4/syncookies.c

## Purpose

This file implements IPv4 TCP SYN cookie generation and validation. It allows a listening TCP socket to complete a handshake without retaining the original SYN request when the SYN queue recently overflowed. The code encodes the peer tuple, time window, selected MSS index, and selected TCP options into the SYN-ACK sequence number and, when timestamps are available, low bits of the echoed timestamp.

## Important APIs, Types, and Functions

- `syncookie_secret[2]`: lazily initialized siphash keys used by `cookie_hash()`.
- `cookie_init_timestamp()`: encodes window scaling, SACK, and ECN option state into low timestamp bits while keeping the initial timestamp no greater than the current TCP timestamp.
- `secure_tcp_syn_cookie()` and `check_tcp_syn_cookie()`: core cookie encode/decode logic. They combine tuple hash, client sequence number, minute counter, and 24-bit data field.
- `msstab[]`: sorted MSS encoding table with four common MSS values.
- `__cookie_v4_init_sequence()` / `cookie_v4_init_sequence()`: generate IPv4 SYN cookie sequence numbers and round the advertised MSS down to the encoded MSS bucket.
- `__cookie_v4_check()`: validates ACK sequence number and returns decoded MSS or 0.
- `cookie_timestamp_decode()`: restores timestamp-carried TCP options while enforcing current sysctl policy for timestamps, SACK, and window scaling.
- `cookie_tcp_reqsk_init()` and `cookie_tcp_reqsk_alloc()`: reconstruct `request_sock` state from the ACK and decoded options.
- `cookie_tcp_check()`: validates syncookie, parses TCP options, handles timestamp offsets, and allocates a rebuilt request.
- `cookie_v4_check()`: top-level IPv4 listener path that validates syncookie ACKs, runs security hooks, computes route/window state, and creates the child socket.
- `tcp_get_cookie_sock()`: invokes the address-family `syn_recv_sock()` callback and attaches the rebuilt request/child socket.
- Optional BPF path: `cookie_bpf_check()` uses an already attached BPF-created request sock when `CONFIG_BPF` support is enabled.

## Control Flow

Cookie creation happens during SYN-ACK construction. `__cookie_v4_init_sequence()` chooses the largest `msstab` entry not exceeding the original MSS, stores the table index as the data payload, and returns a sequence number from `secure_tcp_syn_cookie()`. If timestamps are used, `cookie_init_timestamp()` stores option bits in the low six timestamp bits.

Cookie validation starts in `cookie_v4_check()` for a listener receiving an ACK. It first checks that syncookies are enabled and the packet is an ACK without RST. The BPF cookie path is used when available; otherwise `cookie_tcp_check()` rejects packets if the SYN queue has not recently overflowed, validates the sequence cookie through `__cookie_v4_check()`, counts success/failure stats, parses options, subtracts the secure timestamp offset if present, decodes timestamp-carried options, and allocates a reconstructed request.

After a request exists, `cookie_v4_check()` fills IPv4 local/remote addresses, saves IP options, invokes LSM request hooks, applies TCP-AO syncookie handling, performs an IPv4 route lookup to recover dst metrics, recomputes the initial receive window, checks ECN/AccECN eligibility, and calls `tcp_get_cookie_sock()` to create the established child socket. On failure it frees the request or drops the skb with a specific drop reason.

## State and Persistence Behavior

The design intentionally avoids retaining per-SYN state. Persistent state is limited to process lifetime secrets, minute-granularity cookie time, TCP listener/sysctl configuration, network statistics, route metrics looked up at ACK time, and reconstructed `request_sock` / child socket state after successful validation. Timestamp option encoding preserves only a compact subset of the original SYN options: send window scale, SACK permission, ECN, and the fact that timestamps were negotiated.

## Dependencies and Integration Points

The file depends on TCP core request-socket and option parsing code, IPv4 headers and route lookup, siphash secure sequence helpers, TCP ECN helpers, MPTCP request allocation when enabled, TCP-AO syncookie handling, BPF kfunc integration, LSM hooks, dst metrics, and per-net IPv4 TCP sysctls. The route lookup integration is important because the original SYN dst was discarded and the child socket still needs a valid route and metric-derived receive window.

## Risks and Edge Cases

- The cookie data field is only 24 bits after the count, so MSS and options are intentionally lossy; adding options requires careful encoding compatibility.
- `MAX_SYNCOOKIE_AGE` and minute counter arithmetic decide acceptance windows; off-by-one errors can admit stale cookies or reject valid ACKs.
- Timestamp option decoding must reject options disabled after the SYN-ACK, especially SACK, timestamps, and window scaling.
- The ACK is trusted only after cookie validation; route lookup, LSM hooks, TCP-AO, MPTCP, and BPF-created request paths each have distinct cleanup paths.
- `tcp_synq_no_recent_overflow()` prevents accepting cookies when the listener is not under recent pressure; changing this condition affects spoofing exposure and normal handshakes.
- Recomputed window and ECN state may differ from the original SYN path because no original request state is retained.

## Test Signals

Useful coverage includes SYN flood tests with `tcp_syncookies` enabled, valid/invalid/stale cookie ACK validation, MSS bucket round-down behavior, timestamp option restoration for SACK/window-scale/ECN, sysctl toggles between SYN-ACK and ACK, listener route lookup failure, LSM rejection, TCP-AO and MPTCP enabled paths, BPF syncookie request paths, and stats updates for `SYNCOOKIESRECV` and `SYNCOOKIESFAILED`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/syncookies.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/sysctl_net_ipv4.c -->
# sources/distributed-fs/ceph-client/net/ipv4/sysctl_net_ipv4.c

## Purpose

This file registers and validates the `/proc/sys/net/ipv4` sysctl surface for global and per-network-namespace IPv4, TCP, UDP, ICMP, IGMP, FIB, multipath, ping, CIPSO, and related networking settings. It provides custom handlers for settings that need validation, derived display values, namespace pointer adjustment, key parsing, side effects, or netevent notifications.

## Important APIs, Types, and Functions

- Bounds and constants at file scope define sysctl min/max values for port ranges, TTL, TCP retry counts, MSS, RTO, TCP PLB, ECN modes, ping group IDs, hash table sizing, and ICMP extension masks.
- `set_local_port_range()` and `ipv4_local_port_range()`: read/write ephemeral port range, enforce ordering and non-overlap with privileged ports, and warn once for same-parity endpoints.
- `ipv4_privileged_ports()`: validates `ip_unprivileged_port_start` against the current local port range.
- `inet_get_ping_group_range_table()`, `set_ping_group_range()`, and `ipv4_ping_group_range()`: expose ping socket group range with seqlock protection and user namespace GID translation.
- `ipv4_fwd_update_priority()`: writes forwarding priority sysctl and emits `NETEVENT_IPV4_FWD_UPDATE_PRIORITY_UPDATE`.
- Congestion-control handlers: `proc_tcp_congestion_control()`, `proc_tcp_available_congestion_control()`, and `proc_allowed_congestion_control()`.
- TCP Fast Open handlers: `sscanf_key()`, `proc_tcp_fastopen_key()`, and `proc_tfo_blackhole_detect_timeout()`.
- Read-only derived handlers: `proc_tcp_available_ulp()`, `proc_tcp_ehash_entries()`, and `proc_udp_hash_entries()`.
- Multipath handlers under `CONFIG_IP_ROUTE_MULTIPATH`: `proc_fib_multipath_hash_policy()`, `proc_fib_multipath_hash_fields()`, `proc_fib_multipath_hash_init_rand_seed()`, `proc_fib_multipath_hash_set_seed()`, and `proc_fib_multipath_hash_seed()`.
- `ipv4_table[]`: init-net/global sysctls such as orphan limits, inet peer settings, `tcp_mem`, CIPSO, available ULP, `udp_mem`, and FIB sync memory.
- `ipv4_net_table[]`: large per-net sysctl table for ICMP, ping, ECN, demux, TTL, ports, PMTU, bind behavior, TCP tuning, syncookies, multipath, UDP, FIB notifications, PLB, and RTO settings.
- `ipv4_sysctl_init_net()` / `ipv4_sysctl_exit_net()`: per-net registration and cleanup.
- `sysctl_ipv4_init()`: initcall that registers init-net global table, initializes multipath random seed, and registers per-net sysctl operations.

## Control Flow

At boot, `sysctl_ipv4_init()` registers `ipv4_table` under `net/ipv4` for `init_net`, initializes the multipath seed helper, and registers `ipv4_sysctl_ops`. For each network namespace, `ipv4_sysctl_init_net()` either uses the static `ipv4_net_table` for `init_net` or duplicates it for child namespaces. In child namespaces it adjusts every non-null `.data` pointer from `init_net` storage to the current `struct net`, while entries with no data pointer are treated as global views and made read-only. The table is registered under `net/ipv4`, local reserved port bitmap storage is allocated, and multipath hash seed state is initialized.

On sysctl reads and writes, generic handlers handle most scalar values with min/max enforcement. Custom handlers copy current state into temporary storage, call the generic parser, then commit only valid updates. Some writes trigger side effects: local port range updates use `WRITE_ONCE()`, ping group writes use a seqlock, TFO timeout resets active blackhole disable counters, multipath hash changes notify listeners through `NETEVENT_IPV4_MPATH_HASH_UPDATE`, and forwarding priority changes notify route users.

On namespace teardown, `ipv4_sysctl_exit_net()` frees the reserved port bitmap, unregisters the sysctl header, and frees the duplicated table.

## State and Persistence Behavior

Most state is stored in `struct net.ipv4` fields, so values persist for the lifetime of the network namespace and are isolated per namespace after pointer adjustment. Some settings are global or init-net-only through `ipv4_table`. `ip_local_reserved_ports` is an allocated bitmap per namespace. Ping group range uses a seqlock-protected pair of `kgid_t`. Multipath hash seed stores both the user-provided seed and the effective seed; a zero user seed maps to a boot-random seed. TCP Fast Open key writes update cipher state rather than storing raw text in this file.

## Dependencies and Integration Points

The file integrates with the generic sysctl framework, network namespace lifecycle, TCP congestion-control registry, TCP Fast Open cipher management, TCP ULP registry, TCP and UDP hash tables, ICMP/FIB/IGMP/PING/CIPSO state, netevent notifier chains, user namespace GID conversion, seqlocks, and many `struct net.ipv4` fields consumed throughout IPv4, TCP, UDP, and routing code. The `tcp_syncookies` sysctl exposed here directly gates the syncookie path in `syncookies.c`; multipath sysctls affect route hashing in `route.c`.

## Risks and Edge Cases

- Pointer adjustment for duplicated namespace tables is broad; entries with unusual `.data` semantics, such as `.data = &init_net`, require custom handlers that understand the table layout.
- Port range and privileged port validation must remain consistent in both directions to avoid overlapping unprivileged and ephemeral ranges.
- User namespace GID conversion can produce invalid kgids; invalid or reversed ping ranges intentionally become empty.
- String handlers allocate temporary buffers; missing NUL bounds or malformed TFO keys must fail without partially replacing keys.
- Read-only derived sysctls for child namespace hash tables use negative values to signal shared global tables; tests should preserve that ABI.
- Multipath hash policy, fields, and seed updates have immediate route-selection effects and must notify route users.
- Several entries are config-gated; table shape and proc availability vary by kernel configuration.

## Test Signals

Test signals include namespace creation/destruction with sysctl registration, pointer isolation across netns, write validation for `ip_local_port_range` and `ip_unprivileged_port_start`, ping group range with user namespace mappings, congestion-control read/write permissions, TFO key parsing for one and two keys, TFO blackhole timeout counter reset, derived TCP/UDP hash entry display in init and child namespaces, multipath policy/field/seed notifications, config-gated sysctl presence, reserved port bitmap behavior, and representative min/max enforcement for TCP, ICMP, UDP, and FIB knobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/sysctl_net_ipv4.c -->
