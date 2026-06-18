# sources/distributed-fs/ceph-client/tools/testing/selftests/net/icmp_redirect.sh

## Purpose

This selftest validates IPv4 and IPv6 ICMP redirect route exceptions and their interaction with PMTU exceptions, legacy routes, nexthop objects, and optional VRF routing. It models a host initially routed through `r1` to reach `h2`, then changes `r1` to forward back through the host-facing network via `r2`, causing redirects toward `h1`.

## Important APIs, Types, and Functions

The script sources `lib.sh` and defines logging helpers, `run_cmd`, `get_linklocal`, `cleanup`, `create_vrf`, `setup`, `change_h2_mtu`, `check_exception`, `run_ping`, route helpers for legacy and nexthop-object modes, `check_connectivity`, `do_test`, and `usage`. It uses `ip route get`, `ip nexthop`, VRF devices, bridges, sysctls for redirects and forwarding, ping/ping6, and MTU changes.

## Control Flow

The main path selects a ping6 binary, parses `-p`/`-v`, then runs four scenarios: legacy routing without VRF, legacy routing with VRF, nexthop-object routing without VRF if supported, and nexthop-object routing with VRF. Each scenario rebuilds namespaces and topology, installs initial routes, verifies connectivity, changes `r1` routes to trigger redirects, sends pings, checks cached redirect exceptions, lowers MTU to create PMTU exceptions, resets routes, checks cleanup of exceptions, then tests MTU-before-redirect ordering.

## State and Persistence Behavior

State is temporary namespaces `h1`, `h2`, `r1`, `r2`; veth links; bridge `br0`; optional VRF `red` with table 1111; IPv4/IPv6 addresses and routes; sysctls for redirects/forwarding; nexthop objects in new mode; route cache exceptions; and MTU settings on the h2/r2 link. Cleanup removes namespaces between scenarios.

## Dependencies and Integration Points

It depends on network namespaces, bridge, VRF, IPv4/IPv6 forwarding, ICMP redirects, route exception cache behavior, PMTU handling, optional nexthop object support, and `ping`. It integrates with kernel route exception formatting and redirect acceptance logic.

## Risks and Edge Cases

Assertions parse `ip route get` output strings such as `cache <redirected> expires ... mtu ...`, so output format changes can cause false failures. IPv6 redirect checks are marked XFAIL-capable in some cases through `log_test`'s fourth argument. VRF mode rewrites rule priority 0 lookup behavior and must be isolated by namespace cleanup. Link-local gateway discovery is required for IPv6 redirects.

## Test Signals

Success is counted through `log_test`: IPv4 and IPv6 redirect exceptions appear when expected, PMTU exceptions appear with MTU 1300, reset routes clear redirect/MTU cache state, MTU plus redirect ordering preserves both attributes, and basic connectivity remains intact after redirects and resets.
