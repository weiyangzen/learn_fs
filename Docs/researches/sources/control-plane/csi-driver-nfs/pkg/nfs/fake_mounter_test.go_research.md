# sources/control-plane/csi-driver-nfs/pkg/nfs/fake_mounter_test.go

Purpose: verifies the fake mounter's sentinel-driven success and error behavior.

Important APIs and helpers: `TestMount`, `TestMountSensitive`, and `TestIsLikelyNotMountPoint` install `fakeMounter` into a `mount.SafeFormatAndMount` and call the mount interface methods directly.

Control flow: each table includes source-error, target-error, and success cases. `IsLikelyNotMountPoint` cases cover an injected error path, default not-mounted behavior, and a sentinel path that reports already mounted.

State and persistence behavior: no external state is written. The tests replace the node server's mounter with an in-memory fake and compare returned errors with expected `fmt.Errorf` values.

Dependencies and integration points: depends on `getTestNodeServer` from node tests, `mount.SafeFormatAndMount`, and the fake mounter implementation. It protects the assumptions used by node publish/unpublish tests.

Risks: exact error comparison makes message edits visible. The fake does not emulate sensitive option handling or mount table mutation beyond returning errors.

Test signals: focused signal that all sentinel branches in `fake_mounter.go` behave as expected.
