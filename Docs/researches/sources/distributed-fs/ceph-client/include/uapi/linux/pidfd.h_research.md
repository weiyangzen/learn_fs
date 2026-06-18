<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pidfd.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pidfd.h

Purpose: defines the userspace ABI for pid file descriptors, including `pidfd_open()` flags, `pidfd_send_signal()` targeting flags, namespace lookup ioctls, and structured process metadata retrieval.

Important APIs and types: `PIDFD_NONBLOCK`, `PIDFD_THREAD`, and kernel-only `PIDFD_STALE`/`PIDFD_AUTOKILL` describe pidfd creation semantics. `PIDFD_SIGNAL_THREAD`, `PIDFD_SIGNAL_THREAD_GROUP`, and `PIDFD_SIGNAL_PROCESS_GROUP` select signal delivery scope. `struct pidfd_info` is a versioned ioctl payload with `mask`, pid/tgid/ppid, credential IDs, cgroup id, exit status, coredump data, and `supported_mask`. `PIDFD_GET_*_NAMESPACE` ioctls return namespace file descriptors, and `PIDFD_GET_INFO` is an `_IOWR` query using `PIDFS_IOCTL_MAGIC`.

Control flow: userspace obtains a pidfd, optionally sends scoped signals, or calls ioctls against the pidfs file. For `PIDFD_GET_INFO`, userspace sets `mask` and passes a structure size implied by the ioctl ABI; the kernel fills only supported and size-covered fields and reflects valid fields in `mask`.

State and persistence: the header stores no state. Runtime state is process lifetime, pid namespace membership, credentials, coredump bookkeeping, and pidfs file lifetime. Returned metadata can be stale immediately after the ioctl, but is documented as correct for the intended process at execution time.

Dependencies and integration points: depends on Linux integer types, `fcntl` flag values, and ioctl encoding. Integrates with pidfs, process namespaces, signal delivery, cgroup identifiers, coredump reporting, and pidfd-aware process supervisors.

Risks and test signals: risks include ABI version drift, userspace failing to validate returned `mask`, stale-process assumptions, namespace fd permission mistakes, and signal scope confusion. Test with pidfd self constants, exited tasks, thread vs process-group signaling, short/old `pidfd_info` sizes, namespace ioctls across namespaces, and coredump/exit reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pidfd.h -->
