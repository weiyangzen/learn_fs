# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/ethtool_lanes.sh

## Purpose

Validates mlxsw support for ethtool lane selection with autonegotiation and forced link modes.

## Important APIs, Types, and Functions

Uses `lib.sh` and shared `ethtool_lib.sh`. Important helpers are `check_lanes`, `check_unsupported_lanes`, `max_speed_and_lanes_get`, `search_linkmode`, `autoneg`, and `autoneg_force_mode`. It queries supported link modes, maximum speed/lane combinations, and applies ethtool settings on paired ports.

## Control Flow

Setup maps two netifs, brings them into a usable state, and reads driver-reported lane data. The autoneg test searches for matching advertised modes and verifies lane counts. The forced-mode test selects a concrete speed/lane link mode and checks both accepted and unsupported lane requests.

## State and Persistence Behavior

State consists of ethtool link-mode/autoneg settings on the test ports. Cleanup is mostly inherited from shared helpers and relies on the test environment restoring link settings between runs.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced. It additionally depends on the ethtool selftest helper library.

## Risks and Edge Cases

Risk comes from hardware module capabilities, link partner behavior, supported mode naming, and lane reporting differences across Spectrum generations. A port without matching supported modes can produce skips or false failures.

## Test Signals

Signals are accepted ethtool configuration changes for supported lane counts, rejected unsupported lane counts, and final lane/speed checks from ethtool output.
