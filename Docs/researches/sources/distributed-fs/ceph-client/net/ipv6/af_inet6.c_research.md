# sources/distributed-fs/ceph-client/net/ipv6/af_inet6.c

## Purpose
`af_inet6.c` registers and implements the PF_INET6 socket protocol family. It creates IPv6 sockets from the protocol-switch table, binds and names sockets, delegates send/receive/ioctl paths to protocol implementations, registers TCP/UDP/raw/ping IPv6 protocols, initializes per-net IPv6 MIB/proc/sysctl state, attaches the Ethernet IPv6 packet receiver, and orchestrates full IPv6 stack initialization and rollback.

## Important APIs, Types, and Functions
- Protocol switch state: `inetsw6[SOCK_MAX]` and `inetsw6_lock` hold `struct inet_protosw` entries used by `inet6_create()`. `inet6_register_protosw()` and `inet6_unregister_protosw()` are exported for protocols to add/remove socket handlers.
- Module parameters/defaults: `ipv6_defaults`, `disable_ipv6_mod`, `disable_ipv6`, and `autoconf` influence global IPv6 enablement and addrconf default behavior.
- Socket lifecycle: `inet6_create()`, `inet6_sock_destruct()`, `inet6_release()`, and `inet6_cleanup_sock()` allocate sockets, initialize IPv6 and IPv4-compatible fields, run protocol init, and release multicast, anycast, flowlabel, rx option, rx PMTU, and tx option state.
- Bind/name APIs: `__inet6_bind()`, `inet6_bind_sk()`, `inet6_bind()`, and `inet6_getname()` implement AF_INET6 bind semantics, v4-mapped support, scope-id handling, nonlocal bind policy, BPF hooks, and getsockname/getpeername.
- Operation tables: `inet6_stream_ops` and `inet6_dgram_ops` expose socket operations for stream and datagram protocols.
- I/O and control: `inet6_sendmsg()`, `inet6_recvmsg()`, `inet6_ioctl()`, and `inet6_compat_ioctl()` delegate to protocol methods, IPv6 route ioctl, addrconf address ioctl, SIT destination setup, and compat route conversion.
- Routing/options helpers: `inet6_sk_rebuild_header()` rebuilds cached IPv6 routes for connected sockets; `ipv6_opt_accepted()` decides whether received extension options should be surfaced.
- Namespace and stack init: `inet6_net_init()`, `inet6_net_exit()`, `ipv6_init_mibs()`, `ipv6_cleanup_mibs()`, `inet6_init()`, `ipv6_packet_init()`, and `ipv6_packet_cleanup()`.

## Control Flow
- `inet6_init()` is a `device_initcall`. It initializes protocol-switch lists and raw hash state, optionally exits early if the module is administratively disabled, then registers protocol slabs for TCPv6, UDPv6, rawv6, and pingv6.
- It initializes raw sockets before ICMP/IGMP/NDISC control sockets, registers PF_INET6 with `sock_register()`, registers per-net IPv6 state, initializes multicast routing, ICMPv6, neighbor discovery, IGMPv6, proc entries, IPv6 routing, flowlabels, anycast, addrconf, extension headers, fragmentation, UDP/TCP transports, packet receive hook, pingv6, CALIPSO, segment routing, RPL, IOAM, IGMP late init, and sysctls.
- Every init step has a reverse-order error label. Failure unwinds only components already initialized, unregisters rtnetlink handlers and PF_INET6, and unregisters protocol slabs.
- `inet6_create()` performs RCU lookup in the protocol switch table by socket type and requested protocol, tries module autoload twice for missing protocols, enforces raw-socket capability, allocates `struct sock`, initializes IPv6 defaults (`hop_limit`, multicast hops/loop/all, PMTU policy, flowlabel reflection, bindv6only), initializes IPv4-compatible fields, hashes fixed-number protocols, calls protocol-specific `init`, and runs cgroup socket-create BPF for userspace sockets.
- `__inet6_bind()` validates family, multicast/stream restrictions, privileged ports, socket state, v4-mapped/v6-only interactions, link-local scope-id requirements, device binding, local/nonlocal address policy through `ipv6_chk_addr()` or IPv4 address checks, updates IPv4 and IPv6 receive/source addresses, temporarily forces `sk_ipv6only` for non-any pure IPv6 binds, obtains the port, runs post-bind BPF, and sets userlocks.
- `inet6_ioctl()` routes IPv6 route add/delete to `ipv6_route_ioctl()`, address add/delete to `addrconf_add_ifaddr()` and `addrconf_del_ifaddr()`, SIT destination setup to `addrconf_set_dstaddr()`, and all other ioctls to protocol-specific handlers.

## State and Persistence Behavior
- Global in-memory state includes the protocol-switch lists, packet type registration, module parameters, and exported protocol op tables. Per-net state includes MIB allocations, IPv6 sysctls, proc entries, and flowlabel/idgen defaults.
- Per-socket state is stored in `struct ipv6_pinfo`, `struct inet_sock`, route cache, multicast/anycast lists, options, flowlabels, and BPF/userlock-observable fields.
- No disk persistence is implemented. Proc/sysctl entries reflect runtime namespace state and are cleaned up in `inet6_net_exit()` and init rollback.

## Dependencies and Integration Points
- Integrates nearly every IPv6 subsystem: TCPv6, UDPv6, rawv6, pingv6, ICMPv6, NDISC, IGMPv6, multicast routing, route tables, addrconf, anycast, flowlabels, extension headers, fragmentation, offload, CALIPSO, segment routing, RPL, IOAM, XFRM, cgroup BPF, LSM security flow classification, procfs, sysctl, and packet receive registration.
- Depends on `addrconf.c` for SIOCSIFADDR/SIOCDIFADDR/SIOCSIFDSTADDR and on `addrconf_core.c` address typing/bind helpers through `ipv6_addr_type()` and `ipv6_chk_addr()`.
- Exposes `inet6_stream_ops`, `inet6_bind`, `inet6_release`, `inet6_getname`, protocol-switch registration, and cleanup helpers to other kernel modules.

## Risks and Edge Cases
- Init/rollback ordering is critical. Later subsystems assume earlier control sockets, routes, proc state, packet hooks, and addrconf are available; rollback must mirror successful initialization exactly.
- Protocol-switch registration protects permanent entries from override and inserts new entries after the last permanent entry. Changing ordering can affect wildcard protocol resolution and module override behavior.
- Bind semantics are compatibility-sensitive: IPv4-mapped binds, v6-only sockets, link-local scope IDs, bound devices, nonlocal bind, BPF address mutation, and post-bind port rollback must remain aligned with AF_INET behavior.
- `IPV6_ADDRFORM` can change `sk->sk_prot`, so send/recv/ioctl paths intentionally `READ_ONCE()` the protocol pointer.
- Resource cleanup must drop option memory accounting, flowlabel lists, rx option SKBs, PMTU SKBs, multicast/anycast memberships, and per-net MIB/proc allocations without double-free.

## Test Signals
- Socket creation for TCP, UDP, raw, ping, wildcard protocol, unsupported protocol with module autoload, and raw capability failure.
- Bind tests for any, loopback, global, link-local with/without scope ID, multicast stream rejection, IPv4-mapped with v6-only on/off, bound device missing, nonlocal bind, privileged ports, `BIND_ADDRESS_NO_PORT`, and cgroup bind hooks.
- Ioctl tests for route add/delete, address add/delete, SIT destination address, compat route ioctl, and protocol-specific fallback.
- Init failure injection around each `inet6_init()` step to verify reverse cleanup and no leaked packet/proc/sysctl/proto registrations.
- Runtime observability through `/proc/net/{tcp6,udp6,anycast6,...}`, MIB counters, `ss -6`, `ip -6 route`, `ip -6 addr`, and packet receive on ETH_P_IPV6.
