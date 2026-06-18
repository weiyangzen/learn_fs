# sources/cloud-native/containerd/core/metadata/snapshot_suite_test.go

Purpose: runs containerd's generic snapshotter tests against the metadata snapshotter wrapping the native snapshotter backend.

Important APIs and helpers: `newTestSnapshotter` creates a native snapshotter root, opens a metadata bbolt DB, wraps the native backend with `metadata.NewDB(...).Snapshotter("native")`, and returns cleanup. `TestMetadata` invokes `testsuite.SnapshotterSuite`.

Control flow: the test skips on Windows and requires root because the generic suite needs mount-capable snapshotter behavior. It creates isolated temporary roots for native snapshot data and metadata DB.

State and persistence: exercises real native snapshotter state plus metadata DB mapping state. Cleanup closes both wrapped snapshotter and DB.

Dependencies and integration: depends on `plugins/snapshots/native`, bbolt, `snapshots/testsuite`, testutil root checks, and the public metadata package. It is an integration-level signal rather than a white-box test.

Risks: root and platform requirements mean this suite is skipped in many CI contexts. Failures may originate from native snapshotter behavior, metadata wrapper behavior, kernel mount behavior, or environment.

Test signals: broad contract coverage for the metadata snapshotter as an implementation of the snapshotter interface.
