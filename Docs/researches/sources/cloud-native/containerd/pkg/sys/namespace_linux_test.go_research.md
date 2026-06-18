<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/namespace_linux_test.go -->
# sources/cloud-native/containerd/pkg/sys/namespace_linux_test.go

## Purpose
Root-only Linux tests for GetUsernsForNamespace.

## Important APIs, Types, And Functions
TestGetUsernsForNamespace plus getInode helper.

## Control Flow
The test creates a bind-mounted netns from a child process created by UnshareAfterEnterUserns, then asks the kernel for its owning userns and that userns parent.

## State And Persistence
Creates temp namespace bind mount and unmounts it with continuity testutil. Opens namespace fds that are closed by defer.

## Dependencies And Integration Points
Depends on kernel version >=4.9, root, unix.Mount, and UnshareAfterEnterUserns.

## Risks And Edge Cases
Environment-sensitive because it needs root, kernel support, and namespace operations.

## Test Signals
Directly verifies inode equality against /proc namespace files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/namespace_linux_test.go -->
