# sources/cloud-native/containerd/plugins/services/mounts/service.go

## Purpose
Registers the gRPC mount manager service for activating, deactivating, inspecting, updating, and listing managed mounts.

## Important APIs, Types, And Functions
`service` wraps `mount.Manager` and implements `Register`, `Activate`, `Deactivate`, `Info`, `Update`, and `List`.

## Control Flow
Startup gets the mount manager plugin. Activate maps temporary and label options, converts proto mounts, delegates to `mm.Activate`, and returns activation info. Deactivate, Info, and Update forward to the manager. List streams converted activation info records to the client.

## State And Persistence
Mount activation state is managed by the mount manager and persisted in its DB. The service itself is stateless.

## Dependencies And Integration Points
Requires mount manager plugin, core mount/proxy conversion helpers, errgrpc, logging, and gRPC registration.

## Risks
Streaming list stops on first send error. Activation can create kernel mounts and persistent manager records, so errors must be interpreted through manager semantics.

## Test Signals
No direct tests in this subset.
