# sources/distributed-fs/ceph-client/include/linux/icmpv6.h

## Purpose
Defines in-kernel IPv6 ICMP helper entry points, config-gated send wrappers, error conversion, parameter-problem reporting, flow initialization, and ICMPv6 error classification.

## Important APIs, Types, And Functions
`icmp6_hdr()` accesses the ICMPv6 header from an skb. With IPv6 enabled, `icmp6_send()`, `icmpv6_send()`, `icmpv6_ndo_send()`, and `ip6_err_gen_icmpv6_unreach()` generate ICMPv6 errors; without IPv6, wrappers compile to no-ops. Other externs include `icmpv6_init()`, `icmpv6_cleanup()`, `icmpv6_err_convert()`, `icmpv6_param_prob_reason()`, and `icmpv6_flow_init()`. `icmpv6_is_err()` classifies destination unreachable, packet-too-big, time exceeded, and parameter problem.

## Control Flow
Protocol paths call `icmpv6_send()` with type/code/info, which forwards to `icmp6_send()` using IPv6 skb control block state. NAT-enabled builds can use a specialized ndo send path; otherwise a zeroed `inet6_skb_parm` is supplied. Parameter-problem helpers add a drop reason before emitting the ICMPv6 response.

## State And Persistence
No state is owned by the header. Runtime state is in skb control blocks, IPv6 routing/flow structures, per-net ICMPv6 implementation state, sockets, and module init/cleanup.

## Dependencies And Integration Points
Depends on skb, IPv6, netdevice, UAPI ICMPv6, netfilter NAT config, flowi6, sockets, and drop reasons. Integrates with IPv6 input/output, routing, neighbor discovery, socket errors, netfilter, and network-device transmit error paths.

## Risks
Disabled IPv6 builds silently drop send calls via no-op stubs, so callers must not depend on side effects. ICMPv6 generation is sensitive to skb ownership, control-block initialization, rate limiting, source address selection, and avoiding ICMP errors in response to invalid packets.

## Test Signals
IPv6 enabled/disabled builds, ICMPv6 error generation, packet-too-big and PMTU behavior, NAT ndo send paths, parameter-problem drop reasons, error conversion to errno, and malformed skb/control-block tests.
