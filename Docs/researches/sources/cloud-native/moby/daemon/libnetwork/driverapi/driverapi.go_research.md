<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/driverapi/driverapi.go -->
# sources/cloud-native/moby/daemon/libnetwork/driverapi/driverapi.go

## Purpose
Defines libnetwork's Go interfaces between the controller and network drivers, optional driver capabilities, and network/endpoint information contracts.

## Important APIs, Types, And Functions
`Driver` covers network/endpoint create/delete, operational info, join/leave, type, and built-in status. Optional interfaces include `NetworkAllocator`, `TableWatcher`, `ExtConner`, `IPv6Releaser`, and `GwAllocChecker`. Info interfaces include `NetworkInfo`, `InterfaceInfo`, `InterfaceNameInfo`, and `JoinInfo`. `Registerer`, `Capability`, `IPAMData`, `ObjectType`, and `IsValidType` define registration and metadata contracts.

## Control Flow
The controller calls these interfaces during network creation, endpoint creation, sandbox join/leave, external connectivity changes, IPv6 release, and swarm allocation. Drivers call back into info interfaces to set MAC/IP/interface names, gateways, routes, and gossip table entries.

## State And Persistence
No direct state. Implementations may persist through driver stores, networkdb table entries, or controller datastore.

## Dependencies And Integration Points
This is the integration boundary for bridge, overlay, remote plugins, CNM allocator, networkdb table watching, and IPAM data exchange.

## Risks And Edge Cases
Interfaces are broad and some optional behavior is discovered by type assertion. Drivers must honor call ordering and rollback assumptions. `NetworkPluginEndpointType` ties Go contracts to plugin endpoint naming.

## Test Signals
Driver conformance tests, bridge/overlay integration tests, and remote plugin tests validate correct contract implementation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/driverapi/driverapi.go -->
