# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/fib_offload.sh

## Purpose

Tests IPv6 route offload indication on mlxsw for prefix, multipath, replacement, shared nexthop group, and insertion-rate cases.

## Important APIs, Types, and Functions

Defines TOR/spine topology helpers, `ipv6_offload_check`, route add/replace helpers, `ipv6_route_nexthop_group_share`, and `ipv6_route_rate`. It inspects `ip -6 route show` output for `offload` flags after route operations.

## Control Flow

Setup creates two TOR host ports and two spine router ports with IPv6 /64 links. Tests add prefix and multipath routes with different metrics and nexthops, append and replace them, ensure only the best metric is offloaded, and verify route flags after shared nexthop-group changes. The rate test stresses rapid route additions and checks eventual offload indication.

## State and Persistence Behavior

State consists of IPv6 addresses, route table entries, multipath nexthops, and device offload flags. Cleanup flushes test routes and tears down the topology.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Assertions rely on textual `ip route` output and a short sleep to avoid offload races. Slow hardware programming can make route flags appear late. Multipath replacement semantics in iproute2/kernel can append rather than replace in some cases, which the test intentionally documents and validates.

## Test Signals

Signals are counts from `ipv6_offload_check`, successful route flushes, and per-test `log_test` entries.
