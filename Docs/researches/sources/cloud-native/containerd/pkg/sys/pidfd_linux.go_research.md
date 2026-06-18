<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/pidfd_linux.go -->
# sources/cloud-native/containerd/pkg/sys/pidfd_linux.go

## Purpose
Linux pidfd support probe used before pidfd-based namespace helpers.

## Important APIs, Types, And Functions
SupportsPidFD caches checkPidFD result. checkPidFD tests pidfd_open, pidfd_send_signal, and waitid(P_PIDFD) behavior.

## Control Flow
First call opens a pidfd for current process, sends signal 0, calls waitid expecting ECHILD, then marks supported; errors are logged and cached as false.

## State And Persistence
Process-global support boolean cached with sync.Once; no persistence.

## Dependencies And Integration Points
Used by UnshareAfterEnterUserns before relying on CLONE_PIDFD/P_PIDFD.

## Risks And Edge Cases
One-time negative cache means transient syscall restrictions persist for process lifetime. Logs at error level on unsupported kernels.

## Test Signals
Indirect coverage through unshare tests on kernel >=5.10.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/pidfd_linux.go -->
