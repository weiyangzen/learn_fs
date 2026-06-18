# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/hw_stats_l3.sh

## Purpose

Minimal mlxsw L3 hardware statistics monitor test.

## Important APIs, Types, and Functions

Uses `hw_stats_monitor_test` from `lib.sh` with a cableless switch port (`NETIF_NO_CABLE`). The sole test, `l3_monitor_test`, toggles an IPv4 address on the port while monitoring L3 hardware statistics support.

## Control Flow

There is no topology setup beyond `setup_wait`. The test invokes the shared monitor helper with an address-add command and matching address-delete command, then relies on the helper to observe the expected hardware statistics events or state changes.

## State and Persistence Behavior

State is limited to adding and removing `192.0.2.1/28` on the selected switch port and any monitor process started by the helper.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Because the file is tiny and delegates almost all behavior, failures usually point to shared helper behavior, unavailable `NETIF_NO_CABLE`, unsupported L3 stats, or address cleanup failure.

## Test Signals

Signals are the shared `hw_stats_monitor_test` result and the kselftest exit status.
