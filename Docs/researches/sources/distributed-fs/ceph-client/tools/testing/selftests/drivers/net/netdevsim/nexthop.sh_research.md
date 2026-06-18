# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/nexthop.sh

Purpose: Provides extensive netdevsim nexthop offload/resource testing, including single nexthops, groups, resilient groups, bucket replacement, deletion, and replay after reload.

Important APIs/functions: Uses namespaced `ip nexthop`, `ip route`, `devlink resource`, `devlink dev reload`, and debugfs FIB failure controls. Helpers check nexthop textual output, occupancy, group membership, resilient bucket counts, idle timers, and injected bucket replace failures.

Control flow: Setup creates a netdevsim device in `testns1`, adds `dummy1` with an IPv4 address, and binds `IP`/`DEVLINK` prefixes. `xfail_on_slow tests_run` runs a large `ALL_TESTS` suite covering add/replace/delete for single nexthops, groups, resilient groups, resource overflow, invalid operations, single-member deletion, and reload/replay success/failure.

State and persistence: Mutates namespaced nexthop objects, routes, devlink nexthop resource size, debugfs fault injection, and dummy interface state. Tests generally flush nexthops after each scenario. Cleanup deletes namespace/device/module.

Dependencies and integration: Requires iproute2 nexthop support, devlink netdevsim resources, forwarding `lib.sh`, and kernel resilient nexthop APIs.

Risks: The suite is timing-sensitive for resilient idle timers and can be slow, hence `xfail_on_slow`. Text matching of `ip nexthop show` output is brittle. Resource counts must track netdevsim accounting exactly.

Test signals: PASS requires expected `trap` offload markings, resource occupancy after each mutation, rejected over-limit/replacement failures, correct resilient bucket counts, and restored nexthop state after successful reload.
