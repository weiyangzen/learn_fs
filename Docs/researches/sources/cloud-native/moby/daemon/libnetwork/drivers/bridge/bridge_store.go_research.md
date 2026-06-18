<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/bridge_store.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/bridge_store.go

## Purpose
Implements datastore persistence and live-restore hydration for bridge networks and endpoints. It restores network configuration, endpoint membership, endpoint firewall rules, and host port reservations after daemon restart.

## Important APIs, Types, And Functions
`driver.initStore` calls `populateNetworks` then `populateEndpoints`. `storeUpdate` and `storeDelete` wrap `datastore` atomic put/delete operations. `networkConfiguration` and `bridgeEndpoint` implement `datastore.KVObject` with `Key`, `KeyPrefix`, `Value`, `SetValue`, index/existence methods, `New`, and `CopyTo`. Custom `MarshalJSON` and `UnmarshalJSON` preserve legacy storage format. `bridgeNetwork.restorePortAllocations` replays saved endpoint port mappings.

## Control Flow
Startup lists saved `networkConfiguration` objects, recreates each network through `createNetwork`, then lists `bridgeEndpoint` objects, attaches each endpoint to its restored network, re-adds per-endpoint firewall rules, and re-reserves port mappings. Stale endpoints whose network no longer exists are deleted from the store.

## State And Persistence
Network state is stored under `bridge/<network-id>` and endpoint state under `bridge-endpoint/<endpoint-id>`. JSON encodes IP networks and IPs as strings, joins trusted interfaces with `:`, uses the historical `HostIP` key for IPv4 host SNAT, and normalizes restored operational `HostPortEnd` to `HostPort` to avoid reallocating a different port during live-restore.

## Dependencies And Integration Points
Depends on `datastore`, `portmapperapi`, `types`, OpenTelemetry span/baggage helpers, containerd logging, and `nftabler` cleaner integration. It coordinates with `createNetwork`, `firewallerNetwork.AddEndpoint`, `addPortMappings`, and endpoint/network maps maintained by the bridge driver.

## Risks And Edge Cases
JSON unmarshalling uses map assertions for required historical fields, so missing or malformed persisted state can panic or fail hard. Optional nested endpoint configs are decoded from `nil` if absent, with a TODO noting that fields may be unintentionally nullified. Port restore warns but leaves containers inaccessible if prior host ports cannot be reserved.

## Test Signals
Covered by bridge marshalling and endpoint operational-info tests. Useful additional signals are live-restore tests with stale endpoints, pre-27 port range state, missing optional JSON fields, and cross-firewaller cleanup after switching between iptables and nftables.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/bridge_store.go -->
