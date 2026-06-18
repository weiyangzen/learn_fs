<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/unshare_linux_test.go -->
# sources/cloud-native/containerd/pkg/sys/unshare_linux_test.go

## Purpose
Root-only Linux tests for UnshareAfterEnterUserns.

## Important APIs, Types, And Functions
TestUnshareAfterEnterUserns and subtests should work, killpid, invalid flags, and ownership; getNamespaceInode helper.

## Control Flow
Tests compare namespace inode changes, inspect uid/gid maps and setgroups, kill the child to verify liveness errors, pass invalid flags, and check NS_GET_OWNER_UID.

## State And Persistence
Creates short-lived namespace child processes and reads procfs namespace/map files.

## Dependencies And Integration Points
Requires root and kernel >=5.10. Depends on unix ioctl and /proc.

## Risks And Edge Cases
Highly environment-sensitive; failures may reflect host namespace policy rather than code regression.

## Test Signals
Direct integration coverage for the most complex sys helper.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/unshare_linux_test.go -->
