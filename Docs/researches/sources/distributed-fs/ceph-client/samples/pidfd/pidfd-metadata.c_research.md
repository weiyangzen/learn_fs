# sources/distributed-fs/ceph-client/samples/pidfd/pidfd-metadata.c

Purpose: demonstrates obtaining a pidfd with `CLONE_PIDFD` and safely opening metadata for the child through procfs.

Important APIs/functions: `clone` with `CLONE_PIDFD`, architecture-specific `__clone2` fallback for ia64, `pidfd_send_signal` syscall wrapper, `open` on `/proc/<pid>`, `openat(procfd, "status", ...)`, and `wait`.

Control flow: main creates a child that prints its pid and exits, receives a pidfd from `clone`, opens `/proc/<pid>` as a directory, verifies the pid has not been recycled by calling `pidfd_send_signal(pidfd, 0, NULL, 0)`, opens `status` relative to the proc directory fd, copies that status file to stdout, closes descriptors, and waits for the child.

State and persistence: child process, pidfd descriptor, proc directory fd, and status fd while the program runs.

Dependencies and integration: Linux pidfd syscalls, procfs fdinfo, clone semantics, and signal delivery.

Risks: syscall numbers and fallback definitions vary across architectures/libc versions. The child exits quickly, so the proc entry must be opened before reaping; the pidfd liveness check handles `EPERM` as a still-existing process.

Test signals: run on a pidfd-capable kernel, verify child pid output followed by `/proc/<pid>/status` content, and verify unsupported kernels report missing `CLONE_PIDFD`.
