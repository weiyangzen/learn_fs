# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_activity_notify.sh

## Purpose
`bridge_activity_notify.sh` tests bridge FDB `activity_notify`, `inactive`, and `norefresh` semantics. It builds a simple two-host bridge topology and verifies transitions between inactive and active FDB states, as well as whether replacing an FDB entry refreshes its `updated` timestamp.

## Important APIs, Functions, and Types
The script sources forwarding `lib.sh` and uses `adf_*` helpers, `bridge`, `ip`, `jq`, `mausezahn` via `$MZ`, `busywait`, `slowwait`, and `bridge_ageing_time_get`. `setup_prepare()` maps four physical/netns test interfaces into `h1`, `swp1`, `swp2`, and `h2`, prepares VRFs, initializes hosts, and creates `br1`. `fdb_active_wait()` and `fdb_inactive_wait()` poll `bridge -d fdb get` for the `inactive` marker.

## Control Flow
After checking that `bridge fdb help` contains `activity_notify`, the script installs cleanup, prepares the topology, waits for setup, and runs `ALL_TESTS`: `new_inactive_test`, `existing_active_test`, and `norefresh_test`. The first test adds a static inactive entry with activity notifications, injects traffic from `h1`, and waits for it to become active. The second converts an existing dynamic entry into a static activity-notify entry with `norefresh`, then waits for bridge aging to mark it inactive. The third compares JSON `updated` time after replacement with and without `norefresh`.

## State and Persistence
State is limited to `br1`, its two bridge ports, host interface addresses, and FDB entries. The bridge is created with low aging time and multicast snooping disabled. The tests add and delete a fixed MAC address. Deferred state cleanup is handled by the forwarding library trap and explicit FDB deletion in each test.

## Dependencies and Integration Points
It integrates with the forwarding harness and requires support for the bridge FDB `activity_notify` keyword, JSON FDB output through `bridge -j`, and packet injection through `$MZ`. It also depends on ADF helper wrappers that abstract device operations for offload-capable environments.

## Risks
Timing-based state transitions can be sensitive to bridge aging configuration and system load. The script expects exact textual markers (`inactive`, `activity_notify`) in `bridge` output. If injected traffic is lost for reasons unrelated to FDB activity, the inactive-to-active transition will fail. The test uses one fixed MAC, so cleanup failure can contaminate subsequent tests in the same topology.

## Test Signals
Pass conditions are an inactive static entry becoming active after traffic, an active activity-notify entry becoming inactive after aging, and `updated` resetting only when replacement is performed without `norefresh`. Failures are reported through the forwarding harness `check_err`, `check_fail`, and `log_test`.
