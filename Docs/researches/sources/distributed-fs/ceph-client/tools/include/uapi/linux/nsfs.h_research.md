<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/nsfs.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/nsfs.h

Purpose: this UAPI header defines the user-visible namespace filesystem ABI used by tools that inspect namespace file descriptors, namespace IDs, and mount namespace metadata. It is a contract header, not executable code, and its behavior is implemented by kernel namespace and nsfs ioctl handlers.

Important APIs/types: the `NS_GET_*` ioctls return owning user namespaces, parent namespaces, namespace type, owner UID, namespace IDs, and pid/tgid translations across pid namespaces. `struct mnt_ns_info`, `struct nsfs_file_handle`, and `struct ns_id_req` are versioned request/response layouts with explicit size constants. `enum init_ns_ino`, `enum init_ns_id`, and `enum ns_type` encode stable IDs for initial namespaces and CLONE_NEW-style namespace type bits.

Control flow: callers open an nsfs fd, issue one of the ioctl requests, and interpret either an fd, integer, UID, u64 ID, or filled struct. The list/stat namespace interfaces use a request struct with size and filter fields so callers can negotiate layout versions.

State and persistence: the header defines no state itself; persistent state is kernel namespace lifetime and namespace IDs. The risk is ABI drift, so size fields and reserved/spare fields must be preserved.

Dependencies/integration: depends on `linux/ioctl.h` and `linux/types.h`; integrated by userspace namespace tools, checkpoint/restore, container runtimes, and tests using `ioctl(2)` on `/proc/*/ns/*` fds.

Risks and test signals: validate ioctl number stability, struct sizes (`MNT_NS_INFO_SIZE_VER0`, `NSFS_FILE_HANDLE_SIZE_VER0`, `NS_ID_REQ_SIZE_VER0`), pid namespace translation behavior, permission failures, and compatibility with older kernels that lack later ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/nsfs.h -->
