<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ipv4_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ipv4_linux.go

## Purpose
Configures IPv4 bridge addressing, gateway selection, and loopback-address routing for hairpin/localhost behavior.

## Important APIs, Types, And Functions
`selectIPv4Address` chooses an existing address matching a selector or the first available address. `setupBridgeIPv4` assigns/reconciles the bridge IPv4 address and default gateway. `setupGatewayIPv4` validates and stores a configured default gateway. `setupLoopbackAddressesRouting` enables per-bridge `route_localnet`.

## Control Flow
Bridge IPv4 setup caches `AddressIPv4`, optionally lists existing IPv4 addresses, removes a mismatched selected address, adds the configured address, and stores the gateway for non-internal networks. Gateway setup checks containment and rejects internal networks. Loopback routing reads the sysctl and writes `1` if not already enabled.

## State And Persistence
State is kernel netlink IPv4 address state, cached bridge/gateway fields, and `/proc/sys/net/ipv4/conf/<bridge>/route_localnet`. The bridge driver's persisted network config supplies the desired address and gateway.

## Dependencies And Integration Points
Uses `netlink`, `types.CompareIPNet`, `errInvalidGateway`, `os`, `filepath`, and logging. Invoked by the bridge setup pipeline and port/hairpin behavior.

## Risks And Edge Cases
`selectIPv4Address` errors on an empty pool but setup ignores that error because no current address is acceptable. Internal networks cannot have a gateway. `route_localnet` changes can affect host loopback routing security for the bridge interface.

## Test Signals
Covered indirectly by bridge creation, existing bridge reuse, gateway, and port mapping tests; focused tests would check address replacement and route_localnet sysctl behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ipv4_linux.go -->
