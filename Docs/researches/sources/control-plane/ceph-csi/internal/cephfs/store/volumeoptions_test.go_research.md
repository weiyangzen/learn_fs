# sources/control-plane/ceph-csi/internal/cephfs/store/volumeoptions_test.go

Purpose: focused unit tests for CephFS shallow-snapshot and read-only create-volume helpers in `volumeoptions.go`.

Important APIs/types/functions: tests `IsVolumeCreateRO()` and `IsShallowVolumeSupported()` using CSI `VolumeCapability` and `CreateVolumeRequest` fixtures. The cases cover `MULTI_NODE_READER_ONLY`, `SINGLE_NODE_READER_ONLY`, writer modes, volume content sources, and snapshot content sources.

Control flow: each table-driven test runs subtests in parallel. `TestIsVolumeCreateRO` checks whether access modes are classified as read-only. `TestIsShallowVolumeSupported` combines access mode classification with `VolumeContentSource_Snapshot` presence, confirming that volume sources and writer modes do not enable shallow snapshot backing.

State and persistence: no external state, no Ceph cluster, no filesystem, and no KMS dependencies. The tests only construct protobuf objects in memory.

Dependencies and integration points: validates helper behavior consumed by `NewVolumeOptions()` before backing snapshot resolution. It indirectly protects the semantics that shallow CephFS volumes are only allowed for read-only volumes sourced from snapshots.

Risks: coverage is intentionally narrow. It does not check nil requests, nil capabilities inside a request, mixed capability lists where one entry is read-only and another is writable, explicit `backingSnapshot` parameter parsing, or the later snapshot inheritance checks. The test names are somewhat repetitive ("valid access mode"/"Invalid request"), which can make failures less descriptive.

Test signals: useful as a fast signal for regression in access-mode classification. Broader constructor tests with fake Ceph/Journals would be needed to validate the rest of `volumeoptions.go`.
