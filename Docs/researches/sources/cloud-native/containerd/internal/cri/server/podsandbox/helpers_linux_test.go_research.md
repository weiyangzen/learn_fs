# sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_linux_test.go

## Purpose

This Linux test file verifies cgroup path formatting and resilient removal of directories containing mounts.

## Important APIs, Types, and Functions

`TestGetCgroupsPath` checks regular cgroup parents, systemd slice parents, trailing slashes, and root. `TestEnsureRemoveAllWithMount` bind-mounts a temporary directory into another, runs `ensureRemoveAll`, and verifies the parent disappears.

## Control Flow

The mount cleanup test skips unless running as root, starts `ensureRemoveAll` in a goroutine, and fails if cleanup takes longer than five seconds.

## State and Persistence Behavior

The test creates temporary directories and a transient bind mount. Successful cleanup removes both the mountpoint and the containing directory.

## Dependencies and Integration Points

It depends on Linux `unix.Mount`, `os.Getuid`, and the helper functions in `helpers_linux.go`.

## Risks and Test Signals

The tests catch systemd cgroup formatting regressions and mount-removal hangs. They do not cover user namespace parsing or SELinux behavior, which are handled in other tests.
