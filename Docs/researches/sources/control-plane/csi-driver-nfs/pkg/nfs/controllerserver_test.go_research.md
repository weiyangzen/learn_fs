# sources/control-plane/csi-driver-nfs/pkg/nfs/controllerserver_test.go

Purpose: exercises the NFS CSI controller server behavior for dynamic volume creation/deletion, controller capabilities, volume and snapshot ID parsing, snapshot creation/deletion, volume expansion, cloning from volumes and snapshots, and compression compatibility.

Important APIs and helpers: `initTestController`, `initTestControllerWithOptions`, `TestCreateVolume`, `TestDeleteVolume`, `TestControllerGetCapabilities`, `TestNfsVolFromId`, `TestNewNFSVolume`, `TestCopyVolume`, `TestCreateSnapshot`, `TestDeleteSnapshot`, `TestControllerExpandVolume`, `matchCreateSnapshotResponse`, `TestCreateSnapshotWithoutCompression`, `TestCreateSnapshotWithDifferentShareInSnapshotClass`, `TestCopyVolumeFromUncompressedSnapshot`, `TestArchiveNameWithCompression`, and `TestGetNfsVolFromID`. The tests operate through `ControllerServer` plus fake Kubernetes mounters and temporary filesystem paths.

Control flow: the create-volume cases validate required names, mount capabilities, storage-class parameters, octal mount permissions, default subdirectory selection, and response volume context mutation. Delete cases validate invalid IDs as idempotent success, delete/retain/archive policy behavior, and path cleanup. Snapshot tests create source and snapshot directories, mount fake shares, write tar archives, and compare only meaningful snapshot fields while treating timestamp and size as presence signals. Clone tests dispatch through `copyVolume` into `copyFromVolume` or `copyFromSnapshot`, including missing source IDs and broken snapshot archives.

State and persistence behavior: the tests create real directories and tar files under `/tmp` and tear them down via `TestMain` or case cleanup. They verify the controller's state encoding rather than external persistence: old slash-delimited IDs, new hash-delimited IDs, UUID fields, on-delete policy suffixes, snapshot archive names, and internal working mount paths.

Dependencies and integration points: depends on the CSI protobuf API, gRPC status codes, `mount.FakeMounter`, Go tar/gzip packages, and filesystem operations. It integrates tightly with `controllerserver.go`, `nfs.go`, `utils.go`, and `tar.go` by asserting exact ID strings and path layouts.

Risks: tests rely on hard-coded `/tmp` paths, so parallel external runs can collide if names overlap. Some assertions use exact error values or status strings, which makes wording changes visible. Fake mounter behavior does not prove real NFS server semantics, mount propagation, quota behavior, or cross-platform archive behavior.

Test signals: strong signal for controller parameter validation, path traversal rejection, deletion policy semantics, snapshot compression and backward compatibility, source-volume vs snapshot-class share selection, and CSI capability advertisement. It does not cover list/get volume implementations because those are intentionally unimplemented.
