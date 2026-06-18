# Research: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephfilesystem.go

Purpose: fake typed client for `CephFilesystem` resources.

Important APIs/types/functions: private `fakeCephFilesystems`, embedded `FakeClientWithList[*CephFilesystem, *CephFilesystemList]`, and `newFakeCephFilesystems`.

Control flow: creates the fake generic client with GVR `cephfilesystems`, kind `CephFilesystem`, object/list constructors, list-meta copier, and conversions between list items and pointer slices.

State and persistence behavior: no local persistence. State is in the shared fake action log and object tracker when installed by the fake clientset.

Dependencies and integration points: returned by `FakeCephV1.CephFilesystems(namespace)` and used by filesystem controller tests.

Risks: fake does not validate filesystem pool, MDS, mirroring, or status behavior. Tests that depend on real API validation should use envtest or integration coverage.

Test signals: action/GVR assertions for `cephfilesystems`, object tracker CRUD/list behavior, and watch tests for controllers using filesystem watches.
