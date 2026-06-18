# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_l3_drops.sh

## Purpose

mlxsw devlink L3 drop-trap coverage for malformed, invalid, disabled-RIF, and blackhole routed packets.

## Important APIs, Types, and Functions

Builds a two-host routed topology with IPv4 and IPv6 defaults through SW router ports. Important helpers are `ping_check`, protocol-specific packet constructors, `devlink_trap_drop_test`, `devlink_trap_action_set`, `devlink_trap_rx_packets_get`, and TC flower filters. Tests cover non-IP frames, unicast DIP over multicast DMAC, loopback and multicast SIP/DIP, corrupted IPv4/IPv6 headers, limited broadcast SIP, reserved/interface-local IPv6 multicast destinations, blackhole routes/nexthops, and ingress/egress RIF-disabled traps.

## Control Flow

The script establishes VRFs, enables forwarding, configures router-port addresses, and uses H1 to inject packets toward H2 while egress filters on RP2 identify dropped traffic. Generic tests validate normal ping first, then set trap actions, inject malformed or policy-dropped packets, and assert trap/drop behavior. RIF-disabled tests temporarily create a bridge/RIF state, remove or alter it while traffic is active, and compare devlink trap packet/byte counters.

## State and Persistence Behavior

Runtime state includes forwarding sysctls, VRFs, IPv4/IPv6 routes, blackhole routes, nexthops, TC filters, devlink trap action/stat state, bridge devices used to create/remove RIFs, and background traffic processes.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

The largest risks are false negatives from route convergence delay, neighbor resolution, TC filter protocol mismatch, or trap stats not settling before comparison. RIF-disabled cases are order-sensitive because bridge deletion/deslavement must create the exact disabled ingress or egress RIF condition. Packet payload constructors use fixed header bytes, so kernel parser changes can invalidate expected trap names.

## Test Signals

Test signals are successful baseline pings, trap counter growth for each invalid condition, TC drop hits, and cleanup restoring trap actions and forwarding/VRF state.
