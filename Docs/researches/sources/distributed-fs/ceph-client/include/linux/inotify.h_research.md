<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/inotify.h -->
# sources/distributed-fs/ceph-client/include/linux/inotify.h

Purpose: Defines the kernel mask of all valid inotify bits around the UAPI inotify interface.

Important APIs/types/functions: Includes `uapi/linux/inotify.h` and defines `ALL_INOTIFY_BITS`, the OR of access, modify, attrib, close, open, move, create/delete, self-delete/move, unmount, queue-overflow, ignored, and modifier bits such as `IN_ONLYDIR`, `IN_DONT_FOLLOW`, `IN_EXCL_UNLINK`, `IN_MASK_ADD`, `IN_MASK_CREATE`, `IN_ISDIR`, and `IN_ONESHOT`.

Control flow: Inotify setup code uses the aggregate mask to validate requested watch masks before creating fsnotify marks.

State/persistence: Header owns no state; inotify marks and event queues live in fsnotify/inotify implementations.

Dependencies/integration: Integrates with fsnotify, file descriptors, inode watches, and UAPI masks.

Risks: Omitting a valid bit rejects legal userspace requests; including unsupported bits allows invalid watch configuration.

Test signals: inotify add/remove watch, invalid mask errors, ignored event handling, and fsnotify event delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/inotify.h -->
