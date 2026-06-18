<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/unshare_linux.go -->
# sources/cloud-native/containerd/pkg/sys/unshare_linux.go

## Purpose
Creates a child process in a new user namespace, then unshares selected namespaces inside it while attributing namespace ownership to a target host UID.

## Important APIs, Types, And Functions
UnshareAfterEnterUserns, parseIDMapping, startProcessWithUserNamespace, startProcessWithUsernsLocked, pidfdWaitid, capSnapshot, getCurrentCaps, setCurrentCaps.

## Control Flow
Validates flags and mappings, requires pidfd support, locks an OS thread, temporarily sets effective UID, restores capabilities, starts /proc/self/exe ptraced with CLONE_NEWUSER plus unshare flags and pidfd, runs optional callback with pid, verifies liveness, then kills/waits via pidfd.

## State And Persistence
Creates temporary child process and kernel namespaces; no filesystem persistence except procfs observations. Uses thread-local credential changes carefully.

## Dependencies And Integration Points
Depends on Linux namespaces, capabilities, pidfds, IgnoringEINTR, and x/sys/unix. Used by tests and namespace setup requiring ownership semantics.

## Risks And Edge Cases
Very sensitive to kernel version, privileges, userns restrictions, capability restoration, and thread state. On errors before restoring UID the goroutine intentionally does not unlock the OS thread.

## Test Signals
unshare_linux_test.go covers valid unshare, child death, invalid flags, and namespace owner UID.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/unshare_linux.go -->
