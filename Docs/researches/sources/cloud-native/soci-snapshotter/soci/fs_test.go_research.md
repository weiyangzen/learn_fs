# sources/cloud-native/soci-snapshotter/soci/fs_test.go

Purpose: this file tests root-directory creation behavior for SOCI filesystem setup.

Important tests: `TestEnsureSnapshotterRootPath` has two subtests. The first creates a parent `var/lib`, calls `EnsureSnapshotterRootPath` for a missing `soci-snapshotter-grpc` child, and verifies the child exists. The second pre-creates the root and verifies the function returns success and leaves it present.

Control flow and state: tests use `t.TempDir()` for isolation and real filesystem operations through `os.MkdirAll` and `os.Stat`. They validate existence only.

Dependencies and integration points: exercises `soci/fs.go` and indirectly documents that callers need parent directories to exist when passing a nested custom root.

Risks and gaps: no assertion checks the intended mode, so the comment claiming `0711` versus implementation `0700` is not caught. There is no test for empty root/default path, inaccessible parent, existing file instead of directory, or permission preservation on existing directories.

Test signal quality: narrow but useful for the basic create/no-op cases.
