# sources/distributed-fs/ceph-client/tools/testing/selftests/power_supply/test_power_supply_properties.sh

## Purpose
Validates the Linux power_supply userspace ABI by checking per-device sysfs property files and matching uevent fields.

## Important APIs, Types, and Functions
Uses `count_tests()` plus helper functions from `helpers.sh` and KTAP functions from `ktap_helpers.sh`. It inspects properties such as `type`, `online`, `present`, `status`, `capacity`, voltage/current/charge/power/energy fields, model/manufacturer/serial, technology, and scope.

## Control Flow
The script selects all devices under `/sys/class/power_supply` or one named argument, sets a KTAP plan of 33 checks per supply, verifies device existence, tests mandatory name/type uevent fields, then runs optional file/range/list checks for each known ABI property before `ktap_finished`.

## State and Persistence
Runtime state is shell variables for selected supplies, `DEVNAME`, and sampled sysfs property values. It performs read-only sysfs access.

## Dependencies and Integration Points
Depends on the power_supply class ABI, KTAP helpers, `helpers.sh`, and basic shell utilities. It is installed by the local Makefile as a kselftest program.

## Risks and Test Signals
Test risk is that the fixed `NUM_TESTS=33` must be updated when checks change. The voltage range checks intentionally catch unit-scaling bugs but may be too narrow for unusual hardware.
