# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/devlink_lib.sh

## Purpose
`devlink_lib.sh` is a shared shell library for forwarding selftests that need devlink resources, shared-buffer state, trap/policer statistics, trap actions, and devlink port discovery. It is not a standalone test; it provides helpers and performs up-front capability checks.

## Important APIs, Functions, and Control Flow
On source, the library resolves `DEVLINK_DEV` from `DEVLINK_DEV` env or from the first test interface, verifies it is registered and PCI-backed, records `DEVLINK_VIDDID`, and skips if iproute2 lacks `resource`, `trap`, or `dev info` support. Resource helpers include `devlink_resource_names_to_path`, `devlink_resource_get`, `devlink_resource_size_get/set`, `devlink_resource_occ_get`, and `devlink_reload`.

Shared-buffer helpers save, set, and restore port-pool thresholds, pool size/thtype, and traffic-class bind pool/threshold. They store originals in associative array `DEVLINK_ORIG` to allow explicit restore after reinterpretation-sensitive changes. Trap helpers enumerate traps/groups, read trap type/action/group/metadata, set trap or group action, read rx packet/byte/drop counters, test idle stats, enable/disable all traps, run exception/drop behavior checks, clean up packet generators and tc filters, and test stat increments. Policer helpers read policer count, rate, burst, dropped counter, and group policer binding. Port helpers map netdev to devlink port, locate CPU port, and read shared-buffer cell/pool sizes.

## State, Dependencies, Integration Points, and Risks
State includes devlink device selection, saved shared-buffer attributes, trap actions, group actions, policer counters, and potentially pending resource sizes until `devlink_reload`. Dependencies include `devlink`, `jq`, `lspci`, `udevadm`, `tc_check_packets`, `kill_process`, and kselftest `check_err`/`check_fail`. Since the library exits with kselftest skip codes during source-time capability checks, consumers must source it only when devlink hardware is expected. A notable code risk is that `devlink_resource_size_set` reports `$size` in its error message even though the local variable is `new_size`.

## Test Signals
Consumers get reusable pass/fail signals through return codes and helper assertions: trap stats idle/non-idle, dropped packet counters, tc packet absence for drop tests, resource occupancy/size values, and restored shared-buffer settings.
