# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib_nexthops.sh

## Purpose
`fib_nexthops.sh` is a Linux kselftest shell suite for the standalone nexthop object API and its interaction with IPv4 and IPv6 FIB routes. It creates three network namespaces (`me`, `peer`, `remote`) connected by multiple veth pairs, then exercises ordinary nexthops, nexthop groups, resilient nexthop groups, FDB nexthop groups, compatibility mode notifications, route attachment, live traffic, and stress loops. The opening topology models two parallel links from `me` to `peer` and a remote host network behind `peer`, allowing route resolution, multipath selection, and ping-based runtime validation.

## Important APIs, Functions, and Types
The script sources `lib.sh` for namespace helpers such as `setup_ns` and uses `ip`, `bridge`, `sysctl`, `ping`, `ip6tables`, `jq`, `mausezahn`, and shell built-ins. Core harness functions are `log_test()`, `run_cmd()`, `setup()`, `cleanup()`, `check_output()`, `check_nexthop()`, `check_nexthop_bucket()`, `check_route()`, and `check_route6()`. `get_linklocal()` extracts IPv6 link-local addresses from `ip -6 -br addr`. Feature checks include `check_nexthop_fdb_support()` and `check_nexthop_res_support()`.

Functional test entry points are split by family and feature: `basic()`, `basic_res()`, `ipv4_fcnal()`, `ipv6_fcnal()`, `ipv4_grp_fcnal()`, `ipv6_grp_fcnal()`, `ipv4_res_grp_fcnal()`, `ipv6_res_grp_fcnal()`, `ipv4_withv6_fcnal()`, `ipv4_fcnal_runtime()`, `ipv6_fcnal_runtime()`, FDB group tests, large group tests, multipath selection tests, compatibility-mode tests, and torture tests.

## Control Flow
Command-line flags select `TESTS` (`-t`, `-4`, `-6`) and behavior (`-p`, `-P`, `-v`, `-w`). Main validates root, `ip`, iproute2 nexthop support, and kernel nexthop support. For each selected test it calls `setup`, invokes the test function by name, and calls `cleanup`. Most tests create nexthops or routes, compare `ip` output against exact strings, then delete or flush state before proceeding.

The IPv4 and IPv6 paths are intentionally parallel but not identical. IPv6 includes route restrictions around IPv4 gateways, rpfilter default-route coverage, per-CPU dst reference regression checks, and IPv6 route output formatting. IPv4 includes IPv6 nexthop support, MPLS encap nexthops, default route selection, and IPv4-specific route deletion semantics. Resilient group tests validate bucket creation, bucket migration after member deletion or replacement, idle/unbalanced timer rendering, 16-bit weights, and large bucket dumps.

## State and Persistence
All networking state is transient and lives inside test namespaces. The script changes per-namespace sysctls for forwarding, multipath neighbor selection, link-down route ignoring, DAD behavior, and nexthop compatibility mode. Runtime scratch state includes monitor tempfiles in `/var/run`, a large temporary iproute batch file, counters (`nsuccess`, `nfail`, `nskip`, `ret`), and background process IDs during torture tests. Cleanup deletes namespaces and therefore should remove interfaces, routes, nexthops, neighbors, VXLAN devices, and iptables state created inside the namespace.

## Dependencies and Integration Points
The file integrates with the kselftest networking framework and `tools/testing/selftests/net/lib.sh`. It depends on a privileged kernel environment with network namespaces, veth, dummy/bridge/VXLAN/MPLS support for selected tests, modern iproute2 nexthop syntax, and optional `jq` and `mausezahn`. It returns kselftest skip code `4` when prerequisites are missing. The test is launched by the selftests make/kselftest harness but can also be run directly with `-t` to isolate a function.

## Risks
Exact string matching against `ip` output is sensitive to iproute2 formatting changes. Torture tests sleep for 300 seconds and spawn background loops, so interrupted runs can leave processes if cleanup is bypassed. Some skip paths return without logging through `log_test`, and optional dependencies make coverage environment-dependent. The script toggles `net.ipv4.nexthop_compat_mode` and expects to restore it; failure mid-test could affect subsequent tests in the namespace. FDB tests require specific bridge and VXLAN semantics and may fail on kernels lacking recent nexthop FDB features.

## Test Signals
Success is reported through `[ OK ]` lines and final pass/fail/skip totals. A substantive run covers nexthop creation/deletion/replacement, route references to `nhid`, group member updates after device down or nexthop deletion, resilient bucket dumps and migration, ping reachability through single and multipath routes, blackhole behavior, route notification line counts under compatibility mode, FDB nexthop attachment to bridge entries, neighbor-aware multipath selection, and long-running crash-free torture loops.
