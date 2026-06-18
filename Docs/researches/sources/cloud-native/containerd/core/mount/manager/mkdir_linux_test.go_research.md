<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/mkdir_linux_test.go -->
# sources/cloud-native/containerd/core/mount/manager/mkdir_linux_test.go

Purpose: Linux test coverage for the mkdir transformer.

Important APIs/types/functions: `TestMkdirHandler` creates a temp allowed root, opens it with `os.OpenRoot`, constructs a `mkdir` transformer, and passes a mount carrying `X-containerd.mkdir.path=<dir>:<mode>:<uid>:<gid>`.

Control flow: the test invokes `Transform`, then stats the requested directory and checks that it exists with the requested permissions. It uses current uid/gid so the unimplemented chown path is not triggered.

State and persistence: writes a real directory under a temporary root and verifies filesystem mode.

Dependencies and integration points: validates `os.Root`-relative creation expected when `manager.go` runs `mkdir/...` transforms before the actual mount.

Risks covered: confirms the happy path for explicit mode parsing and allowed-root lookup. It does not cover nested paths, overlapping roots, unsupported chown/chmod, invalid option syntax, or path traversal attempts.

Test signals: local filesystem test, not a real mount test. It gives confidence that internal options can prepare overlay directories without passing through to `mount_linux.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/mkdir_linux_test.go -->
