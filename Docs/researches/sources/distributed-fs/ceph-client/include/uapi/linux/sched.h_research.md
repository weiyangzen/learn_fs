<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sched.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/sched.h

Purpose: defines process creation, namespace, clone3, and scheduler policy/flag UAPI constants.

Important APIs, types, and functions: clone flags include traditional `CLONE_*` bits for VM, FS, files, signal handlers, pidfd, vfork, parent, thread, namespaces, TLS, TID pointers, cgroups, IO, and `CLONE_NEWTIME`. Clone3-only flags include `CLONE_CLEAR_SIGHAND`, `CLONE_INTO_CGROUP`, `CLONE_AUTOREAP`, `CLONE_NNP`, `CLONE_PIDFD_AUTOKILL`, and `CLONE_EMPTY_MNTNS`. `struct clone_args` is the extensible clone3 argument block with aligned 64-bit fields. Scheduler constants define normal, FIFO, RR, batch, idle, deadline, and ext policies plus `SCHED_RESET_ON_FORK` and sched_attr flag masks.

Control flow: libc or container runtimes pass legacy clone flags or `struct clone_args` to the kernel. The kernel validates flag combinations, creates processes/threads/namespaces/cgroup membership, and later scheduler syscalls use policy and flag constants to update task scheduling behavior.

State and persistence behavior: process, namespace, pidfd, cgroup, signal, VM, and scheduler state live in task structures. `clone_args` is copied at syscall entry and versioned by size constants, allowing extension without breaking old userspace.

Dependencies and integration points: depends on Linux fixed-width types. It integrates with `clone`, `clone3`, `unshare`, sched_setattr/getattr, pidfds, namespaces, cgroups, and process supervisors.

Risks and edge cases: clone flags overlap with exit-signal low bits and some bits are syscall-specific. New `clone_args` fields must be appended and 64-bit aligned. Invalid combinations such as thread without shared signal semantics or namespace constraints must be rejected by syscall code.

Test signals: clone3 size-version tests, pidfd and cgroup cloning, namespace creation, invalid flag combination selftests, scheduler flag validation, and compatibility tests for legacy clone/unshare bit overlap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sched.h -->
