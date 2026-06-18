# sources/cloud-native/containerd/contrib/snapshotservice/service_test.go

Purpose: unit test for `snapshotservice.service.Commit` option propagation.

Important types/functions: `mockSnapshotter` implements `snapshots.Snapshotter` and captures `commitOpts`. `TestCommitParentOption` drives four cases: parent only, no parent, labels plus parent, and labels only.

Control flow and state: the test creates the service via `FromSnapshotter`, calls `Commit`, applies captured options to a `snapshots.Info`, and compares resulting `Parent` and `Labels`.

Dependencies and integration: uses the snapshots API request type and core snapshot option functions. It exercises only local adapter behavior, not a real gRPC transport.

Risks: label validation checks only expected keys when labels are present and does not assert absent labels for nil cases. Other service methods, error translation, `List` batching, and `Cleanup` are uncovered.

Test signals: good regression coverage for a subtle API addition: preserving `CommitSnapshotRequest.Parent` into `snapshots.WithParent`.
