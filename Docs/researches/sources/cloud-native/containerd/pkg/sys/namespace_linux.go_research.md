<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/namespace_linux.go -->
# sources/cloud-native/containerd/pkg/sys/namespace_linux.go

## Purpose
Linux helper for retrieving the owning user namespace file descriptor for another namespace fd.

## Important APIs, Types, And Functions
GetUsernsForNamespace performs ioctl NS_GET_USERNS and wraps the returned fd as *os.File.

## Control Flow
Calls raw SYS_IOCTL on the provided fd and returns an os.File named under /proc/<pid>/fd/<fd>.

## State And Persistence
Returns a live fd the caller must close; no persistent state.

## Dependencies And Integration Points
Used by namespace ownership tests and code that needs userns relationships. Depends on x/sys/unix and syscall.

## Risks And Edge Cases
Requires Linux kernel support for ioctl_ns. Returned fd leaks if callers forget Close.

## Test Signals
namespace_linux_test.go validates netns-to-userns and parent userns relationships under root/kernel gates.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/namespace_linux.go -->
