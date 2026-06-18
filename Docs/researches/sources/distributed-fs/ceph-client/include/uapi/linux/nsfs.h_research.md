# sources/distributed-fs/ceph-client/include/uapi/linux/nsfs.h

Purpose: Defines ioctl and structure ABI for namespace file descriptors exposed by nsfs, including namespace discovery, owner lookup, PID translation, mount namespace iteration, and stable namespace IDs.

Important APIs/types/functions: Exports `NSIO`, `NS_GET_USERNS`, `NS_GET_PARENT`, `NS_GET_NSTYPE`, `NS_GET_OWNER_UID`, PID/TGID translation ioctls, `NS_MNT_GET_INFO`, `NS_MNT_GET_NEXT`, `NS_MNT_GET_PREV`, `NS_GET_MNTNS_ID`, and `NS_GET_ID`. Important layouts are `struct mnt_ns_info`, `struct nsfs_file_handle`, and `struct ns_id_req`, with version-size macros such as `MNT_NS_INFO_SIZE_VER0`, `NSFS_FILE_HANDLE_SIZE_VER0`, and `NS_ID_REQ_SIZE_VER0`. Enums define initial namespace inode numbers, initial namespace IDs, and `enum ns_type` bit masks matching `CLONE_NEW*` values.

Control flow: Userspace opens a namespace fd, then issues ioctls to derive related namespace fds, query namespace type/owner, translate PIDs between caller and target PID namespaces, enumerate mount namespaces, or retrieve IDs. The `ns_id_req` layout supports `statns(2)` and `listns(2)` style request filtering by namespace type and owning user namespace.

State and persistence behavior: The header owns no state. It exposes stable-ish namespace identity snapshots: inode numbers for init namespaces, 64-bit namespace IDs, mount counts, and owning user namespace IDs. Callers must treat namespace lifetime as fd-pinned and handle disappearance or permission failures during iteration.

Dependencies and integration points: Depends on `<linux/ioctl.h>` and `<linux/types.h>`. Integrates with procfs namespace links, pidfds/namespace fds, container runtimes, checkpoint/restore tooling, monitoring agents, and namespace-aware process managers.

Risks: ABI size fields must be honored for forward compatibility. PID translation can fail or return different visible IDs depending on caller namespace. Exposing namespace IDs and owner UIDs is security-sensitive and must preserve kernel permission checks. Mount namespace iteration can race namespace creation/destruction.

Test signals: Exercise ioctls from nested user, pid, net, and mount namespaces; verify `size` version handling; test PID/TGID translation in both directions; enumerate mount namespaces with `LISTNS_CURRENT_USER`; and validate permission failures for unprivileged callers.
