<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/provider.go -->
# sources/cloud-native/moby/daemon/libnetwork/cnmallocator/provider.go

## Purpose
Implements the SwarmKit network allocator provider for CNM/libnetwork, including driver validation and VXLAN port configuration.

## Important APIs, Types, And Functions
`Provider` holds a plugin getter. `NewProvider` constructs it. `ValidateIPAMDriver`, `ValidateIngressNetworkDriver`, and `ValidateNetworkDriver` validate nil/default, built-in, overlay ingress, and plugin drivers. `validatePluginDriver` rejects missing plugin stores, lookup failures, and legacy v1 plugins. `SetDefaultVXLANUDPPort` delegates to overlay utilities.

## Control Flow
Validation allows nil drivers, requires a name when a driver object is present, accepts known built-ins/default IPAMs, otherwise performs plugin lookup by endpoint type and rejects v1 plugins.

## State And Persistence
Provider state is just the plugin getter reference. VXLAN port changes affect overlay utility configuration outside this file.

## Dependencies And Integration Points
Bridges SwarmKit provider interfaces with libnetwork driver/IPAM plugin types, default IPAM, overlay utils, and gRPC status codes.

## Risks And Edge Cases
Without a plugin getter, only built-in drivers validate. Validation proves lookup and version only; it does not prove plugin runtime correctness or allocator support. Ingress remains restricted to overlay.

## Test Signals
`provider_test.go` checks nil and empty-name validation status. Broader behavior is covered by SwarmKit allocator tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/provider.go -->
