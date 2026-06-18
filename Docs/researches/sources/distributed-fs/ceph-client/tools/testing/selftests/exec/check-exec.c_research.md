# sources/distributed-fs/ceph-client/tools/testing/selftests/exec/check-exec.c

## Purpose
C kselftest for `execveat(AT_EXECVE_CHECK)` and exec-related securebits (`SECBIT_EXEC_RESTRICT_FILE`, `SECBIT_EXEC_DENY_INTERACTIVE`, and locked variants). It verifies access checks for executable and non-executable files across mount/file modes and privilege levels, plus securebit mutability/inheritance.

## Important APIs, Types, And Functions
Uses raw `execveat` syscall with `AT_EMPTY_PATH | AT_EXECVE_CHECK`, `prctl(PR_SET/GET_SECUREBITS)`, libcap `cap_set_secbits`, `cap_set_proc`, tmpfs mounts, `memfd_create`, pipes, sockets, device nodes, and kselftest fixtures. Helpers include `drop_privileges()`, `test_secbits_set()`, `fill_exec_fd()`, `fill_exec_path()`, `test_exec_fd()`, and `test_exec_path()`.

## Control Flow
The `access` fixture creates a tmpfs test mount with variant-controlled `MS_NOEXEC` and file execute mode, regular file, directory, device nodes, FIFO, memfd, pipefd, and socket. Tests verify `AT_EXECVE_CHECK` returns success or `EACCES` without actually executing. The `secbits` fixture runs privileged and unprivileged variants, tests setting/unsetting legacy and exec securebits, and checks locked bits cannot be changed in parent or vfork child.

## State And Persistence
Creates and unmounts `./test-mount`, temporary files, memfds, pipes, sockets, and securebit state in the process/children. It drops privileges in selected test paths.

## Dependencies And Integration Points
Requires libcap, `false` helper binary, root/capability support for mount/device-node variants, new securebits definitions, and `AT_EXECVE_CHECK` UAPI.

## Risks
Fixture setup is invasive and can fail without mount privileges. `vfork` child assertions must exit promptly. Dropping capabilities is irreversible within that process path, so ordering relies on fixture isolation.

## Test Signals
Signals are exact `execveat` success/EACCES results for regular files and memfds, EACCES for non-regular files, expected `EPERM` for unprivileged securebit changes, and locked-bit inheritance behavior.
