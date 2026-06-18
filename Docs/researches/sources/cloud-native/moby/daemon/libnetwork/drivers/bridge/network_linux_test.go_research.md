<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/network_linux_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/network_linux_test.go

## Purpose
Tests bridge endpoint creation, joining, duplicate detection, IPv6 enablement behavior, and endpoint deletion in isolated Linux namespaces.

## Important APIs, Types, And Functions
Tests include `TestLinkCreate`, `TestLinkCreateTwo`, `TestLinkCreateNoEnableIPv6`, and `TestLinkDelete`. They use helper endpoint fixtures from `bridge_linux_test.go`, `newDriver`, `CreateNetwork`, `CreateEndpoint`, `Join`, and `DeleteEndpoint`.

## Control Flow
Each test creates a driver and bridge network, then exercises endpoint creation/join/delete. Assertions inspect veth source link existence, MTU inheritance, assigned endpoint IPs, configured gateways, duplicate endpoint errors, and nil IPv6 fields when IPv6 is not enabled.

## State And Persistence
State is temporary bridge/netlink/driver state plus temp datastore. No long-lived repository state is changed.

## Dependencies And Integration Points
Uses `drvregistry`, `netlabel`, `nlwrap`, `netnsutils`, and `storeutils`. Integrates driver API callbacks with netlink-created veth pairs and bridge network config.

## Risks And Edge Cases
Tests require namespace/netlink privileges. Duplicate endpoint handling checks error type and message. IPv6 IPAM data may be present even when bridge config disables IPv6, and the test ensures it is ignored.

## Test Signals
Passing tests signal correct endpoint lifecycle, duplicate endpoint rejection, gateway assignment, veth MTU propagation, IPv4/IPv6 address containment, and deletion error handling for empty IDs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/network_linux_test.go -->
