<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fib.h -->
# sources/distributed-fs/ceph-client/include/trace/events/fib.h

## Purpose
Defines IPv4 FIB lookup tracing for route-decision diagnostics.

## APIs, Control Flow, and State
The single `fib_table_lookup` event records table id, lookup error, output/input interface indexes, protocol, DS field derived from `flowi4_dscp`, scope, flow flags, source/destination IPv4 addresses, optional TCP/UDP ports, selected device name, and IPv4 or IPv6 gateway from `struct fib_nh_common`. It stores IPv4 and IPv6 gateway slots so IPv4 lookups through common nexthop objects can show either address family. No route state is persisted by the header; it snapshots `struct flowi4` and selected nexthop data after lookup.

## Dependencies, Integration, Risks, and Tests
Depends on `skbuff`, netdevice names, `flowi4`, DSCP helpers, `ip_fib.h`, nexthop common structures, and tracepoints. Integration points are IPv4 route table lookup, policy/routing diagnostics, nexthop selection, and packet-flow debugging. Risks include null nexthop handling, only decoding ports for TCP/UDP, route changes after trace emission, and gateway arrays needing initialization on all branches. Test signals include route lookup tracing for connected, gateway, unreachable, TCP/UDP, and non-TCP flows; multipath/nexthop tests; DSCP/tos checks; and namespace-specific route scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fib.h -->
