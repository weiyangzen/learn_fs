# sources/cloud-native/containerd/pkg/os/os.go

Purpose: injectable filesystem/OS abstraction plus real implementation for common operations.

Important APIs/types/functions: `OS` interface includes directory creation/removal, stat, symlink resolution, scoped symlink following, file copy/write, mount/unmount/lookup, and hostname. `RealOS` implements common methods: `MkdirAll`, `RemoveAll`, `Stat`, `FollowSymlinkInScope`, `CopyFile`, `WriteFile`, and `Hostname`.

Control flow: methods delegate to standard library or containerd helpers. `CopyFile` opens source and destination with requested permissions, copies contents, and closes files. `FollowSymlinkInScope` delegates to `fs.RootPath`.

State/persistence: performs real filesystem writes/removes/copies and host lookups.

Dependencies/integration: used by code that benefits from fakeable OS operations. Depends on `github.com/containerd/continuity/fs` and platform-specific files for symlink/mount behavior.

Risks: `CopyFile` can partially write destination if copy fails. File permissions and symlink scope behavior are security-sensitive. RealOS methods return raw errors with limited context in some cases.

Test signals: fake implementation under `pkg/os/testing` supports higher-level tests; platform-specific tests cover symlink resolution.
