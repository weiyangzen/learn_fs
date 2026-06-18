<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/seccomp.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/seccomp.h

Purpose: this header defines the seccomp syscall/prctl ABI for strict mode, BPF filter mode, filter flags, filter return actions, `struct seccomp_data`, and user-notification ioctls.

Important APIs/types: constants include `SECCOMP_MODE_*`, `SECCOMP_SET_MODE_*`, filter flags such as `TSYNC`, `LOG`, `NEW_LISTENER`, `WAIT_KILLABLE_RECV`, return actions from `SECCOMP_RET_KILL_PROCESS` through `SECCOMP_RET_ALLOW`, and return masks. Structs include `seccomp_data`, `seccomp_notif_sizes`, `seccomp_notif`, `seccomp_notif_resp`, and `seccomp_notif_addfd`. Ioctls include notification receive/send, ID validation, addfd, and fd flag setting.

Control flow: userspace installs filters with `seccomp(2)` or `prctl(PR_SET_SECCOMP)`. BPF programs inspect `seccomp_data` and return an action. If `SECCOMP_RET_USER_NOTIF` is used, a supervisor receives notifications, validates IDs, can inject fds, and replies with allow/error/value or continue flags.

State and persistence: filters stack on tasks and are inherited according to kernel rules. User-notification fds represent live supervisor state. The comments explicitly warn that `CONTINUE` is not safe as a standalone security policy due to TOCTOU on pointer arguments.

Dependencies/integration: depends on compiler and type headers; integrates with `prctl.h`, classic BPF filter loading, container sandboxes, syscall brokers, and tracing/debugging tools.

Risks and test signals: test action precedence, data mask extraction, TSYNC errors, listener fd behavior, notification ID validity, addfd atomic send, and unsafe `CONTINUE` cases. ABI risks are struct-size negotiation and correct signed ordering of return actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/seccomp.h -->
