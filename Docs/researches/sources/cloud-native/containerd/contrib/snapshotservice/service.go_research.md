# sources/cloud-native/containerd/contrib/snapshotservice/service.go

Purpose: adapter exposing a `snapshots.Snapshotter` as the containerd snapshots gRPC API server.

Important APIs: `FromSnapshotter` returns a `snapshotsapi.SnapshotsServer`. Methods map RPC requests to snapshotter calls: `Prepare`, `View`, `Mounts`, `Commit`, `Remove`, `Stat`, `Update`, server-streaming `List`, `Usage`, and optional `Cleanup`.

Control flow and state: the service holds only the wrapped snapshotter. It translates labels into `snapshots.WithLabels`, commit parent into `snapshots.WithParent`, mount slices through `mount.ToProto`, snapshot info through `proxy.InfoToProto/InfoFromProto`, and native errors through `errgrpc.ToGRPC`. `List` buffers up to 100 `Info` entries per response.

Dependencies and integration: integrates with `api/services/snapshots/v1`, core `mount`, core `snapshots`, snapshot proxy conversion helpers, and `errdefs`/`errgrpc`.

Risks: `List` returns raw walk errors without `errgrpc.ToGRPC`, unlike most unary methods. `Cleanup` only works for snapshotters implementing `snapshots.Cleaner`. Update mask handling trusts proto paths. Batching size is fixed.

Test signals: `service_test.go` specifically verifies `Commit` passes parent and labels via options; broader RPC methods are not covered here.
