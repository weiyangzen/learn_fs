# sources/cloud-native/containerd/core/diff/apply/apply_linux_test.go

Purpose: unit test for Linux overlay mount option parsing.

Important test: `TestGetOverlayPath` verifies a mount option list with `upperdir`, colon-separated `lowerdir`, and `workdir` yields the expected upper path and two lower parents, then verifies missing `upperdir` returns an error.

Control flow and state: pure parsing test, no filesystem or mount operations.

Dependencies and integration: covers helper used by `apply_linux.go` overlay fast path.

Risks: does not test malformed lowerdir, multiple upperdir entries, escaping, user namespace branch, archive application, or syncfs behavior.

Test signals: useful guard for the most important overlay option extraction invariant.
