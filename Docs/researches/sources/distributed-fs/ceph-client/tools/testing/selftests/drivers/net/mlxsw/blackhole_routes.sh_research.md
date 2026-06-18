
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/blackhole_routes.sh`

## Purpose
Tests that mlxsw blackhole routes are offloaded and that packets matching them are dropped by the ASIC rather than trapped/dropped by the kernel.

## Important APIs, Types, And Functions
- `h1_create()`, `h2_create()`, and `router_create()` build a routed two-host topology with IPv4/IPv6 addresses and default routes.
- `ping_ipv4()` and `ping_ipv6()` are baseline connectivity checks.
- `blackhole_ipv4()` and `blackhole_ipv6()` add blackhole routes, install skip-hw tc filters to detect kernel-trapped packets, and verify offload/drop behavior.

## Control Flow
Setup enables forwarding and VRFs, brings router ports up, and assigns addresses. Baseline ping tests run first. Blackhole tests add a route, wait until it is marked offloaded, send ping expected to fail, then assert the skip-hw tc filter saw zero packets.

## State And Persistence
Mutates routes, tc clsact/qdisc/filter state, interface addresses, link state, forwarding, and VRFs. Cleanup deletes filters/routes within each test and tears down router/host configuration via trap.

## Dependencies And Integration Points
Depends on forwarding shell libraries, `tc_common.sh`, mlxsw-capable hardware, `wait_for_offload`, tc flower counters, and ping helpers.

## Risks
If the route is not offloaded in time, the test fails before traffic validation. The zero-packet tc check assumes the skip-hw filter would see packets if they reached software.

## Test Signals
Pass requires route offload marking, failed pings to blackholed destinations, and zero matching packets on the software tc filter.
