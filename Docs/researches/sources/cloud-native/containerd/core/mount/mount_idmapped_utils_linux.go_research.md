<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_idmapped_utils_linux.go -->
# sources/cloud-native/containerd/core/mount/mount_idmapped_utils_linux.go

Purpose: creates a pinnable user namespace file descriptor for idmapped mounts.

Important APIs/types/functions: `getUsernsFD` starts `/proc/self/exe` in a new user namespace with provided uid/gid maps and pidfd support; `pidfdWaitid` waits on a pidfd while ignoring EINTR.

Control flow: checks pidfd support, starts a traced reexec-like child with `CLONE_NEWUSER`, `Pdeathsig`, and `PidFD`; opens `/proc/<pid>/ns/user`; verifies the child is still alive with `PidfdSendSignal(0)`; returns the user namespace file while deferring child kill/wait and pidfd close.

State and persistence: returns an `*os.File` holding a kernel reference to the user namespace after the helper process has been killed and reaped.

Dependencies and integration points: used by `GetUsernsFD` in `mount_idmapped_linux.go`; depends on `pkg/sys.SupportsPidFD`, Linux pidfd syscalls, and user namespace clone privileges.

Risks: environment and security policy can block user namespace creation; if the child dies before namespace FD open/validation, the function fails. The helper path uses `/proc/self/exe`, so runtime execution context matters.

Test signals: idmapped tests and benchmarks exercise this helper under concurrent use and real kernel behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_idmapped_utils_linux.go -->
