# sources/cloud-native/containerd/core/snapshots/proxy/proxy.go

## Purpose
Implements the `snapshots.Snapshotter` interface over the containerd snapshot gRPC API.

## APIs, Flow, State, Dependencies, Risks, And Tests
`NewSnapshotter` stores a `SnapshotsClient` and snapshotter name. Methods translate the snapshotter interface to RPCs: `Stat`, `Update`, `Usage`, `Mounts`, `Prepare`, `View`, `Commit`, `Remove`, `Walk`, `Close`, and `Cleanup`. Prepare/View/Commit apply local `snapshots.Opt` values into temporary `Info` to pass labels and parent. `Walk` consumes the streaming `List` RPC until EOF and calls the caller's walk function for each returned info.

The proxy has no local persistent state; remote snapshotter state is authoritative. Dependencies include snapshot service API, errgrpc, mount proto conversion, internal snapshots types, and protobuf field masks.

Integration points are remote containerd clients and services that expose snapshotters through gRPC. Risks include local option support limited to labels/parent, streaming errors mid-walk, callback errors aborting list processing, `Close` being a no-op, and remote cleanup semantics. Test signals are fake RPC mapping tests, walk streaming/EOF/error behavior, option propagation, and native error conversion.
