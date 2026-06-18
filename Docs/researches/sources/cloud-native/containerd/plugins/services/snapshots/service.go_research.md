# sources/cloud-native/containerd/plugins/services/snapshots/service.go

## Purpose
This file implements the gRPC snapshots service, multiplexing requests to named snapshotter instances.

## Important APIs, Types, And Functions
The gRPC plugin ID is `snapshots`. `service` stores `map[string]snapshots.Snapshotter` and implements `Prepare`, `View`, `Mounts`, `Commit`, `Remove`, `Stat`, `Update`, streaming `List`, `Usage`, and `Cleanup`. `getSnapshotter` validates snapshotter names.

## Control Flow
Initialization obtains the map from the `services.SnapshotsService` plugin. Each RPC looks up the requested snapshotter, converts labels and mount/info/usage protobufs through `mount` and `proxy` helpers, calls the core snapshotter, and converts errors with `errgrpc`. `List` batches walk results into responses of up to 100 infos.

## State And Persistence
The service owns no snapshot state. State persists inside each snapshotter and in metadata stores. `Cleanup` is exposed only when the snapshotter implements `snapshots.Cleaner`.

## Dependencies And Integration Points
It integrates snapshotter core interfaces, snapshotter proxy conversions, gRPC streaming, metadata-provided snapshotter map, and plugin registration.

## Risks
Missing or unloaded snapshotters are returned as invalid argument, not not found. `Commit` can set parent through options when provided, so callers must preserve correct parent semantics. `List` errors are returned directly for some paths, while most unary errors are converted with `errgrpc`.

## Test Signals
No direct tests here. Snapshotter suites for individual backends indirectly exercise service-compatible behavior, but not this gRPC adapter.
