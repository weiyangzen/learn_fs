<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/port_mapping_linux_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/port_mapping_linux_test.go

## Purpose
Validates bridge port mapping behavior across IPv4/IPv6, NAT/routed gateway modes, docker-proxy, rootless port drivers, host-port ranges, defaults, loopback, and cleanup failures.

## Important APIs, Types, And Functions
`TestPortMappingConfig` and `TestPortMappingV6Config` exercise full driver flow. `TestAddPortMappings` contains the large table for `addPortMappings`. Helpers include `loopbackUp`, `newIPNet`, `proxyCall`, `mockPortDriverClient`, and `stubPortMapper`.

## Control Flow
Tests create isolated namespaces, install stub or real NAT/routed port mappers, optionally mock `startProxy`, construct bridge networks/endpoints, call `addPortMappings` or full `Join`/`ProgramExternalConnectivity`, then verify returned mappings, firewall stub ports, proxy calls, port driver state, logs, and release behavior.

## State And Persistence
State includes allocated ports from `portallocator`, temporary listening sockets for busy-port simulation, fake proxy maps, mock rootless open-port maps, and endpoint operational port mapping. All are reset per test namespace.

## Dependencies And Integration Points
Uses `nat` and `routed` port mapper packages, rootless port driver client interface, `netlink`, `netnsutils`, `storeutils`, `logrus`, and the stub firewaller.

## Risks And Edge Cases
The table covers high-risk cases: host port exhaustion, first port busy, same host port across multiple host IPs, NAT disabled with specific host addresses, no proxy for IPv6-to-IPv4, rootless IPv6 unsupported, release errors from proxies, and IPv4-mapped addresses.

## Test Signals
Passing tests signal correct binding expansion, stable selected host ports, expected log warnings for ignored mappings, correct proxy lifecycle, correct rootless child host IPs, and complete cleanup through `releasePorts`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/port_mapping_linux_test.go -->
