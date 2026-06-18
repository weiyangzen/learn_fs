
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_control.sh`

## Purpose
Tests mlxsw devlink control-plane trap coverage for many protocol packets and control events. It sends crafted packets matching each registered control trap and verifies devlink trap stats increment under the right conditions.

## Important APIs, Types, And Functions
- Topology helpers create a routed two-host VRF setup through two router ports.
- `ALL_TESTS` enumerates traps for STP, LACP, LLDP, IGMP, MLD, DHCP, ARP, IPv6 neighbor discovery, BFD, OSPF, BGP, VRRP, PIM, route exceptions, router-alert options, IPv6 all-nodes/all-routers, PTP, tc sample/trap, and EAPOL.
- Payload builders such as `lacp_payload_get()`, `lldp_payload_get()`, `mld_payload_get()`, `icmpv6_header_get()`, router-alert helpers, and `eapol_payload_get()` produce raw mausezahn payload fragments.
- Most tests call `devlink_trap_stats_test <name> <trap> $MZ ...`.

## Control Flow
Setup enables forwarding, creates VRFs, addresses, and default routes. Each trap test crafts a packet with appropriate L2/L3/L4 headers and invokes the shared devlink stats checker. Some tests install temporary neighbors, dummy devices/routes, or tc clsact filters to trigger route exception, sample, or trap behavior.

## State And Persistence
Mutates router addresses/routes, neighbors, dummy links, tc clsact filters, and forwarding state. Temporary state is generally removed in the same test; global topology cleanup runs through trap.

## Dependencies And Integration Points
Depends on forwarding `lib.sh`, `devlink_lib.sh`, `mlxsw_lib.sh`, mausezahn, tc, devlink trap stats, and mlxsw Spectrum behavior. PTP tests call `mlxsw_only_on_spectrum 1`.

## Risks
The suite is broad and packet encodings are hand-crafted, so protocol format changes or mausezahn differences can break individual trap cases. Some local/external route tests include `sp=12345` where `dp` may have been intended, but the goal is trap triggering rather than payload delivery.

## Test Signals
Pass requires `devlink_trap_stats_test` to observe the expected trap stat delta for each crafted control packet or tc action case. Failures identify trap name and packet scenario.
