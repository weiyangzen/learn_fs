# sources/cloud-native/moby/daemon/network/network_mode_windows.go

## Purpose
This Windows file defines Docker's Windows default network and predefined network detection.

## Important APIs, Types, And Functions
`defaultNetwork` is `network.NetworkNat`. `isPreDefined` returns true for any `container.NetworkMode` that is not user-defined.

## Control Flow
The predicate delegates to `container.NetworkMode(network).IsUserDefined()`, negating the result.

## State, Persistence, And Dependencies
No mutable state or persistence. Dependencies are Docker API container and network type constants.

## Integration Points
Windows daemon network create/delete/filter behavior uses this broader predefined definition.

## Risks And Edge Cases
The Windows predicate is broader than Unix and may classify more modes as predefined. The shared wrapper notes a TODO to align platform behavior.

## Test Signals
No tests in this subset target the Windows implementation directly.
