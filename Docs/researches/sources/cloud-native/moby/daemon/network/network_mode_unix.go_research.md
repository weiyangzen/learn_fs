# sources/cloud-native/moby/daemon/network/network_mode_unix.go

## Purpose
This non-Windows file defines Docker's Unix default network and predefined network detection.

## Important APIs, Types, And Functions
`defaultNetwork` is `network.NetworkBridge`. `isPreDefined` converts the name to `container.NetworkMode` and returns true for bridge, host, none, or default.

## Control Flow
The function is a simple predicate used through `IsPredefined`.

## State, Persistence, And Dependencies
No state or persistence. Dependencies are Docker API container and network type constants.

## Integration Points
Unix daemon network create/delete/filter behavior uses this definition to protect built-in networks and classify filters.

## Risks And Edge Cases
`NetworkMode.IsDefault()` is treated as predefined along with explicit bridge/host/none. User-defined networks that share unexpected aliases could be affected by `NetworkMode` semantics.

## Test Signals
`filter_test.go` relies on host/bridge/none being builtin on non-Windows.
