# sources/cloud-native/containerd/plugins/services/snapshots/snapshotters.go

## Purpose
`snapshotters.go` registers the service plugin that exposes all metadata-managed snapshotters to the gRPC snapshots service.

## Important APIs, Types, And Functions
The service plugin uses ID `services.SnapshotsService`, requires metadata, and returns `m.(*metadata.DB).Snapshotters()`.

## Control Flow
Initialization resolves the metadata DB and returns its snapshotter map.

## State And Persistence
No state is created here. The returned snapshotter map is owned by metadata DB wiring.

## Dependencies And Integration Points
It connects metadata DB plugin initialization to `plugins/services/snapshots/service.go`.

## Risks
The type assertion assumes the metadata plugin is the expected DB implementation. Availability of named snapshotters depends on prior snapshot plugin registration and metadata setup.

## Test Signals
No direct tests are in this subset. Daemon plugin initialization validates it.
