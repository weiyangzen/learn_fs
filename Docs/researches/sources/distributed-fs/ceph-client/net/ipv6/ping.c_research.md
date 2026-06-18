# sources/distributed-fs/ceph-client/net/ipv6/ping.c

Purpose: Implements IPv6 datagram ping sockets (`SOCK_DGRAM`, `IPPROTO_ICMPV6`) and their proc reporting glue, adapting common ping infrastructure to IPv6 routing, options, and ICMPv6 frame generation.

Important APIs, types, and functions: `ping_v6_sendmsg()` is the send path. `ping_v6_pre_connect()` runs cgroup connect BPF after address length validation. `pingv6_prot` and `pingv6_protosw` register the protocol and socket operations. Proc support provides `/proc/net/icmp6` through seq operations. `pingv6_init()` wires real IPv6 callback functions into `pingv6_ops`; `pingv6_exit()` restores dummy callbacks and unregisters.

Control flow: Send validates the user ICMP header through `ping_common_sendmsg()`, resolves destination from `msg_name` or connected state, chooses output interface from scope, bind, sticky pktinfo, multicast/unicast defaults, rejects mapped/scopeless invalid cases, processes ancillary IPv6 control messages, builds `flowi6` including ICMP type/code and security classification, looks up a route, builds a `pingfakehdr`, selects hop limit, appends data under socket lock using `ip6_append_data()`, then pushes pending frames through `icmpv6_push_pending_frames()` or flushes on error.

State and persistence: Socket state includes normal `inet_sock`/`ipv6_pinfo`, bound device, sticky pktinfo, flow label, corked pending frames, and ping port allocation. Global `pingv6_ops` callback pointers are updated at module/subsystem init and restored on exit. Proc entries are per-net.

Dependencies and integration: Depends on common ping code, IPv6 datagram connect/control/routing, cgroup BPF, ICMPv6, raw IPv6 socket ops, procfs, and pernet lifecycle.

Risks and test signals: Risks include scope/oif validation, control-message option handling, pending-frame cleanup on errors, BPF pre-connect bounds, and callback replacement during init/exit. Tests should cover connected and unconnected sends, link-local scope IDs, multicast oif, ancillary hop-limit/tclass/pktinfo, BPF connect programs, route errors, proc listing, and checksum/sequence correctness.
