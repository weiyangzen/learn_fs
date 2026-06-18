<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fib6.h -->
# sources/distributed-fs/ceph-client/include/trace/events/fib6.h

## Purpose
Defines IPv6 FIB lookup tracing for route diagnostics.

## APIs, Control Flow, and State
The `fib6_table_lookup` event records IPv6 table id, route error from `ip6_rt_type_to_error()`, output/input interfaces, flow label, traffic class, scope, flags, source and destination IPv6 addresses, TCP/UDP ports when applicable, protocol, route type, output device name, and gateway. It treats the namespace null route as an all-zero gateway and otherwise records `res->nh->fib_nh_gw6` when a nexthop exists. The header stores no routing state; it snapshots `struct fib6_result`, `struct fib6_table`, and `struct flowi6`.

## Dependencies, Integration, Risks, and Tests
Depends on IPv6 address helpers, `flowi6`, `ip6_fib.h`, namespace IPv6 null-entry state, netdevice names, and tracepoints. Integration points are IPv6 route lookup, policy routing diagnostics, nexthop and gateway resolution, and protocol/port-sensitive flows. Risks include leaving gateway contents undefined if a non-null route has no nexthop, only capturing ports for TCP/UDP, and interpreting route errors without full policy context. Test signals include IPv6 route lookup traces for local, gateway, unreachable, TCP/UDP and ICMPv6 flows, flow-label/tclass checks, netns null-route cases, and nexthop deletion races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fib6.h -->
