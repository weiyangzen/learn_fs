<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/task_local_storage_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/task_local_storage_helpers.h

## Purpose
This userspace helper header provides a portable inline wrapper for the `pidfd_open` syscall used by task local storage selftests.

## Important APIs, Types, and Functions
It conditionally defines `__NR_pidfd_open` as 544 on alpha or 434 otherwise when libc headers lack it, and defines `static inline int sys_pidfd_open(pid_t pid, unsigned int flags)`.

## Control Flow
The wrapper directly calls `syscall(__NR_pidfd_open, pid, flags)` and returns the kernel result.

## State and Persistence
No persistent state is held. Successful calls return a pidfd file descriptor owned by the caller.

## Dependencies and Integration Points
It includes `unistd.h`, `sys/syscall.h`, and `sys/types.h`. It is used by userspace BPF selftests that need pidfds on systems whose libc may not expose the syscall number.

## Risks
Hard-coded syscall numbers must match architecture; the header handles alpha specially and assumes 434 for others. Callers must close returned fds.

## Test Signals
Successful compilation on older headers and successful pidfd creation at runtime indicate the helper is working.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/task_local_storage_helpers.h -->
