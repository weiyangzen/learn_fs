<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/eintr_unix.go -->
# sources/cloud-native/containerd/pkg/sys/eintr_unix.go

## Purpose
Unix helper to retry syscalls interrupted by signals.

## Important APIs, Types, And Functions
IgnoringEINTR loops a function until the returned error is not unix.EINTR.

## Control Flow
Callers pass a syscall closure; EINTR is swallowed and retried indefinitely.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Used by pidfdWaitid and checkPidFD waitid paths; copied from Go runtime behavior.

## Risks And Edge Cases
A closure that always returns EINTR will loop forever. Only exact unix.EINTR is retried.

## Test Signals
Covered indirectly by pidfd/unshare paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/eintr_unix.go -->
