# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/one_armed_router.sh

## Purpose

One-armed router test proving bridge RIF forwarding and forwarding-mark behavior for IPv4 and IPv6.

## Important APIs, Types, and Functions

Creates H1/H2 VRFs connected to two switch ports enslaved to one bridge with multiple router addresses. Tests are `ping_ipv4`, `ping_ipv6`, `fwd_mark_ipv4`, and `fwd_mark_ipv6`. It uses TC `skip_hw`/`skip_sw` counters and mausezahn UDP traffic.

## Control Flow

Setup disables redirects, enables forwarding, creates a bridge with the SWP1 MAC, enslaves both switch ports, assigns both subnets to the bridge RIF, and installs clsact on both ports. Ping tests validate basic reachability. Forwarding-mark tests inject UDP packets that are trapped at ingress because of loopback error but must be hardware-forwarded through the egress port, not software-forwarded.

## State and Persistence Behavior

State includes bridge/RIF addresses, VRFs, routes, sysctls for redirects, TC filters, and generated traffic. Cleanup removes filters, bridge, routes, sysctls, forwarding, and VRFs.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

The test relies on loopback-error trapping while preserving ASIC forwarding metadata. TC counter interpretation is subtle: ingress `skip_hw` should see trapped packets, egress `skip_sw` should see hardware-forwarded packets, and egress `skip_hw` should stay zero for software forwarding.

## Test Signals

Signals are IPv4/IPv6 ping success and three TC counter checks per protocol proving trap plus hardware forwarding behavior.
