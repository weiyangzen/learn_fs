<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/wait.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/wait.h

Purpose: defines wait-family option flags and waitid selector constants exposed to userspace.

Important APIs and types: wait flags include `WNOHANG`, `WUNTRACED`/`WSTOPPED`, `WEXITED`, `WCONTINUED`, `WNOWAIT`, and Linux-specific `__WNOTHREAD`, `__WALL`, and `__WCLONE`. waitid selectors include `P_ALL`, `P_PID`, `P_PGID`, and `P_PIDFD`.

Control flow, state, and persistence: process-management syscalls consume these flags to decide which child state changes to report and whether to reap. No state is stored in this header.

Dependencies and integration points: used by libc, wait4/waitid syscall wrappers, pidfd APIs, and kernel exit/reaping logic.

Risks and test signals: risks include conflicting libc definitions, pidfd selector compatibility, and misuse of Linux-private flags. Test waitpid/waitid behavior for exited, stopped, continued, clone, thread-group, and pidfd children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/wait.h -->
