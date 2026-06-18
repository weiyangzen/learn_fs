# sources/distributed-fs/ceph-client/tools/testing/selftests/net/gre_ipv6_lladdr.sh

## Purpose

This selftest verifies IPv6 link-local address generation and multicast route creation on GRE and GRETAP devices for multiple address-generation modes and underlay endpoint combinations.

## Important APIs, Types, and Functions

The script sources `lib.sh` and defines `exit_cleanup_all`, `setup_basenet`, `check_ipv6_device_config`, `test_gre_device`, `test_gre4`, `test_gre6`, and `usage`. It uses `ip link add type gre/ip6gre/gretap/ip6gretap`, per-interface `net.ipv6.conf.*.addr_gen_mode`, `stable_secret`, and route/address inspection.

## Control Flow

The script creates one namespace, enables loopback underlay addresses, then tests IPv4-underlay GRE and GRETAP and IPv6-underlay IP6GRE and IP6GRETAP. For each tunnel type, it iterates `eui64`, `none`, `stable-privacy`, and `random` modes across fixed local/remote and `any` endpoint combinations. Each device is brought up, checked, brought down, link-local generation is disabled and then re-enabled while up, checked again, and deleted.

## State and Persistence Behavior

All state is temporary inside `NS0`: loopback underlay addresses, one `gretest` device at a time, sysctl values for `addr_gen_mode` and `stable_secret`, link-local addresses, and kernel local multicast routes. The exit trap removes the namespace.

## Dependencies and Integration Points

It depends on GRE, IP6GRE, GRETAP, IP6GRETAP, IPv6 sysctl support, namespace helpers, and kernel local multicast route generation. It integrates with IPv6 interface address generation logic for tunnel netdevices.

## Risks and Edge Cases

The `none` mode expects no link-local address but still expects the ff00::/8 multicast route to exist. Stable privacy mode requires a configured `stable_secret`. The test uses grep matching for `stable-privacy` in address output, so output format changes can affect it.

## Test Signals

Each scenario logs two checks: initial configuration after link-up and update after re-enabling generation on an already-up device. Success means expected presence or absence of `fe80::` and presence of an ff00::/8 local multicast route for `gretest`.
