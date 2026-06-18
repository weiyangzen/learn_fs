<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rtnetlink.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/rtnetlink.sh

## Purpose

`rtnetlink.sh` is a broad kselftest shell harness for exercising rtnetlink-driven network configuration paths through iproute2. It creates a dummy base device and then runs many independent `kci_test_*` cases that cover routing rules, route lookup, address lifetime expiry, traffic control objects, tunnels, bridge/FDB/neighbour operations, VRF, XFRM/IPsec, MACsec, bonding, mngtmpaddr, address protocol fields, and operational state reporting.

## Important APIs, Types, and Functions

The script sources `lib.sh` for kselftest helpers such as `ksft_skip`, `setup_ns`, `cleanup_all_ns`, `require_command`, and `slowwait`. Its local helpers are `check_err`, `check_fail`, `run_cmd*`, `run_cmd_grep*`, and `end_test`, which maintain the per-test `ret` status while allowing the script to continue after failed commands. Test entry points are listed in `ALL_TESTS` and can be overridden with `-t`.

Important external APIs are `ip link`, `ip route`, `ip rule`, `ip addr`, `ip netconf`, `ip tunnel`, `ip xfrm`, `bridge fdb`, `ip neigh`, `tc`, `sysctl`, `ifconfig`, `jq`, `uuidgen`, `modprobe`, `udevadm`, `ping`, and debug/sysfs files for netdevsim. Several tests rely on rtnetlink extensibility exposed by iproute2: VXLAN/FOU/GRE/GRETAP/ERSPAN link kinds, `seg6` is not used here, but VRF, bridge, VLAN, MACsec, team, bond, and netdevsim all exercise netdevice and routing notifications.

## Control Flow

Startup requires `jq`, root privileges, and runnable `ip` and `tc`. `kci_test_rtnl` creates `test-dummy0`, iterates through `${TESTS:-$ALL_TESTS}`, invokes each named function, accumulates failures, and deletes the dummy device. Individual tests create and tear down local devices or temporary namespaces as needed.

The control flow is deliberately failure-tolerant. `run_cmd` records unexpected nonzero exit codes, `run_cmd_fail` records commands that unexpectedly succeed, and grep variants validate expected iproute2 output. Most tests use a local `ret=0` so failures are isolated to that test, then call `end_test` with a PASS/FAIL/SKIP line.

## State and Persistence Behavior

The script mutates kernel networking state: devices, routes, rules, XFRM states and policies, neighbours, FDB entries, sysctls, netdevsim instances, debugfs mounts, and temporary namespaces. Cleanup is mostly inline in each test, with a final dummy deletion. Some sysctls are saved/restored, such as `fib_multipath_hash_policy` and `promote_secondaries`; others are scoped to temporary namespaces.

Persistent risk is highest around tests that touch global state: XFRM flushes, debugfs/netdevsim device creation, module loading/unloading, and bridge/bond/team devices in the initial namespace. Most namespace-based tests reduce cross-test leakage.

## Dependencies and Integration Points

This is integrated into `tools/testing/selftests/net` and validates kernel rtnetlink handlers through user-facing iproute2 commands rather than direct netlink messages. It depends on optional kernel features and modules including dummy, bridge, VLAN, VRF, VXLAN, FOU, GRE/ERSPAN, MACsec, team, bonding, XFRM/IPsec offload, netdevsim, IPv6 temporary addresses, and neighbour/FDB protocol support.

## Risks and Edge Cases

The script is sensitive to iproute2 version, missing kernel modules, missing `ifconfig` or `jq`, root privileges, and system policy around debugfs/module loading. Tests that expect command failure can produce false results if iproute2 syntax changes. `run_cmd_common` executes commands from expanded strings, so unusual arguments with shell metacharacters would be unsafe, although inputs are hard-coded.

Concurrency-sensitive coverage includes IPv6 addrlabel add/delete races, interface alias sysfs writes, temporary IPv6 address regeneration, and netdev lock paths for MACsec/VLAN and team/bridge/macvlan. These are regression-oriented and may be timing-sensitive on slow machines.

## Test Signals

Success is a zero exit from `kci_test_rtnl` and per-case PASS lines. Meaningful signals include expected route/neighbour/FDB JSON or text output, cleaned-up address lifetimes, correct XFRM monitor line counts, successful IPsec offload accounting in netdevsim debugfs, expected failure of invalid VXLAN changes, correct address protocol filtering through `jq`, and tenant/device cleanup without residual links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rtnetlink.sh -->
