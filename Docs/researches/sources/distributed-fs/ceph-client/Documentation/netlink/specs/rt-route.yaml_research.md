# sources/distributed-fs/ceph-client/Documentation/netlink/specs/rt-route.yaml

Purpose: this raw rtnetlink schema documents route configuration and route dumps for `RTM_GETROUTE`, `RTM_NEWROUTE`, and `RTM_DELROUTE`.

Important APIs, types, and functions: `rtmsg` is the fixed route header with family, destination/source prefix lengths, TOS, table, protocol, scope, route type, and flags. `rtm-type` enumerates unicast, local, broadcast, anycast, multicast, blackhole, unreachable, prohibit, throw, nat, and xresolve. `route-attrs` includes destination/source, input/output interface, gateway, priority, preferred source, nested metrics, multipath, table, mark, multicast forwarding stats, via/newdst, preference, encapsulation type/data, expiry, uid, TTL propagation, protocol and port selectors, nexthop id, and IPv6 flowlabel. Nested `metrics` maps RTAX lock, MTU, window, RTT, RTT variance, ssthresh, cwnd, advmss, reordering, hoplimit, initcwnd/initrwnd, features, rto-min, quickack, congestion-control algorithm, and fastopen-no-cookie.

Control flow: `getroute` value 26 supports a do lookup using selectors (`src`, `dst`, interfaces, protocol, ports, mark, uid, flowlabel) and a full dump with no attributes; replies are value 24 with all route attributes. `newroute` value 24 creates routes using the full attribute set. `delroute` value 25 deletes using the same set.

State and persistence: routes live in per-namespace FIB tables and persist until deletion, namespace teardown, device removal, or protocol owner cleanup. Metrics and encapsulation state are route attributes owned by the kernel routing stack.

Dependencies and integration: depends on `linux/rtnetlink.h`, FIB, nexthop, tunnel encapsulation, multipath, and iproute2-style route management.

Risks: many attributes are family-specific or table/protocol-specific; `multipath`, `via`, `encap`, and `mfc-stats` are binary and need external struct knowledge. Test signals include IPv4/IPv6 route add/get/del in a netns, metric nesting validation, route lookup with UID/ports/mark, and schema value parity with UAPI message numbers.
