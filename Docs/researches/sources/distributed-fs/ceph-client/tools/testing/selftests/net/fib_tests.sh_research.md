# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib_tests.sh

## Purpose
`fib_tests.sh` is a broad Linux FIB behavior regression suite. It validates route lifetime and lookup behavior under device unregister, admin-down, carrier-down, suppress rules, nexthop validation, route add/replace semantics, netlink notifications, IPv6 garbage collection, route metrics, address-derived prefix route metrics, preferred source cleanup, IPv4 routes with IPv6 gateways, route mangling interactions, broadcast neighbor lookups, multipath receive-list behavior, multipath load balancing, and IPv6 RA-to-static route promotion.

## Important APIs, Functions, and Types
The script sources `lib.sh` and uses `ip`, `ping`, `ping6`, `tc`, `iptables`, `ip6tables`, `socat`, `mausezahn`, `jq`, `bc`, `perf`, and optional `ra6` / `rd6`. Harness functions include `log_test()`, `setup()`, `cleanup()`, `run_cmd()`, `check_expected()`, `check_route()`, and `check_route6()`. Route setup helpers (`route_setup()`, `forwarding_setup()`, `add_route()`, `add_route6()`) build reusable two- and three-namespace topologies. Feature probes include `ip_addr_metric_check()`, `socat_check()`, `iptables_check()`, `ip6tables_check()`, `ip_neigh_get_check()`, and `mpath_dep_check()`.

## Control Flow
Main installs `trap cleanup EXIT`, parses `-t`, `-p`, `-P`, and `-v`, checks root, `ip`, and `fibmatch` support, then dispatches symbolic test names from `TESTS`. Many tests call `setup()` or `route_setup()` internally and cleanup at the end. The first group exercises route removal or link-down marking when devices disappear or go down. Route add/replace tests use controlled veth topologies to assert exact `ip route` output after duplicate adds, appends, prepends, multipath conversion, invalid replacement attempts, metrics, and reject routes.

Later groups test source address deletion in default and VRF tables, IPv6 route garbage collection for expiring routes and redirect exceptions, RA-learned routes promoted by static addresses, route notification size with encapsulated multipath nexthops, DS Field matching without ECN sensitivity, socket traffic through sport/dport FIB rules despite mangle table marks, and multipath behavior using tracepoints or tc flower counters.

## State and Persistence
The script heavily mutates namespace-scoped state: sysctls, dummy and veth devices, VRFs, routes, neighbors, tc qdiscs/filters, iptables/ip6tables rules, and temporary service processes. It writes `errors.txt` in the current working directory during route monitor tests and uses temporary files for `socat` and `perf` output. Most state is removed through cleanup helpers, though comments note that system services such as `systemd-networkd` can interfere with RA timing.

## Dependencies and Integration Points
This file is integrated with kselftest and `lib.sh`. It depends on a privileged kernel with namespaces, dummy, veth, VRF, bridge-related tc helpers from the library, FIB tracepoints, and recent iproute2 `fibmatch`. Optional subtests require `socat`, `iptables`, `ip6tables`, `ip neigh get`, `mausezahn`, `jq`, `bc`, `perf`, and `ipv6toolkit` tools (`ra6`, `rd6`). It exercises kernel datapath behavior directly rather than mocking route tables.

## Risks
The suite is sensitive to exact `ip` output, kernel timing, and optional user-space tools. Some subtests sleep for route expiration or RA processing and can be flaky on slow or managed systems. `fib4_nexthop()` is only a placeholder, so IPv4 nexthop validation in `fib_nexthop_test()` is currently incomplete compared with IPv6. Monitor tests write `errors.txt` in the working directory; one IPv6 notify path leaves the removal commented. Long multipath tests require perf tracepoints and offload/GRO settings that may be unavailable.

## Test Signals
Signals include expected return codes from `ip route get fibmatch`, absence or presence of `dead linkdown`, exact route dump strings after add/replace, successful or failed pings through selected routes, netlink monitor output not containing `Message too long`, zero `expires` routes after GC, correct prefix-route metric ordering, correct removal of routes or preferred sources when addresses disappear, DSCP route matching independent of ECN bits, successful UDP traffic under matching FIB rules, and multipath counters showing both legs used.
