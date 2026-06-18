<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seccomp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/seccomp.h

Purpose: defines the seccomp syscall and notification ABI for strict/filter mode, filter flags, BPF return actions, seccomp data passed to filters, user notification structures, and notification fd ioctls.

Important APIs, types, and functions: modes include disabled, strict, and filter. Operations include setting strict/filter mode and querying action or notification sizes. Filter flags include TSYNC, log, speculation allow, new listener, TSYNC_ESRCH, and killable receive wait. Return actions range from kill/trap/errno/user-notif/trace/log/allow with masks for action and data bits. `struct seccomp_data` is the BPF input. Notification ABI uses `seccomp_notif_sizes`, `seccomp_notif`, `seccomp_notif_resp`, `seccomp_notif_addfd`, and ioctls for receive, send, ID validity, addfd, and notification-fd flags.

Control flow: userspace installs a BPF filter with seccomp or prctl. On syscall entry, the kernel evaluates filters and applies the least-permissive action. For `SECCOMP_RET_USER_NOTIF`, a supervising process reads notifications from a listener fd, optionally injects fds, validates IDs, and sends responses.

State and persistence behavior: filters attach to tasks and optionally synchronize across thread groups. User notification IDs and listener fds are runtime kernel state. The structs are transient ioctl/syscall payloads.

Dependencies and integration points: includes compiler/type definitions and integrates with classic BPF filters, ptrace/audit/logging, no_new_privs, process/thread lifecycle, and container supervisors.

Risks and edge cases: `SECCOMP_USER_NOTIF_FLAG_CONTINUE` is explicitly unsafe as a standalone security policy because syscall pointer arguments can change while supervised. Stacked filters, TSYNC failure handling, notification ID races, and addfd atomicity require careful validation. Return action ordering must remain least-permissive.

Test signals: seccomp selftests for all actions, TSYNC and TSYNC_ESRCH, listener creation, notification receive/send/ID_VALID/addfd/set flags, stacked filters, ptrace interactions, fatal signal wait behavior, and BPF `seccomp_data` arch/args correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seccomp.h -->
