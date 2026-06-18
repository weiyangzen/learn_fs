# File Research: sources/block-storage/util-linux/sys-utils/lsns.c

This file implements `lsns(8)`, the namespace inventory command. It builds an in-memory model of processes and namespaces by scanning `/proc`, reading `/proc/<pid>/stat`, `/proc/<pid>/ns/*`, open namespace file descriptors, nsfs bind mounts from `/proc/self/mountinfo`, and, when supported, namespace metadata from `NS_GET_*` ioctls.

The central types are `struct lsns`, `struct lsns_process`, and `struct lsns_namespace`. Processes carry per-namespace inode IDs, parent/owner namespace IDs, UID, command metadata, and namespace sibling links. Namespaces carry type, inode ID, process count, representative lowest PID, optional UID fallback, network namespace ID, and parent/owner relationship pointers.

Network namespaces receive extra handling through rtnetlink `RTM_GETNSID`, a small inode-to-netnsid cache, and optional socket namespace discovery with `pidfd_open()`, `pidfd_getfd()`, and `SIOCGSKNS`. When `USE_NS_GET_API` is available, the command can discover persistent or otherwise processless namespaces from nsfs fds and can connect parent/owner namespace trees.

Output is driven by libsmartcols. Column definitions cover namespace ID/type/path/process counts, representative PID/PPID/command/user, netnsid, nsfs mountpoints, parent namespace, and owner namespace. The command supports raw, JSON, no-heading, no-wrap, custom columns, hidden columns needed for `--filter`, namespace/process trees, parent/owner trees, `--persistent`, `--task`, namespace ID selection, and namespace type filtering.

Important behavior: default output becomes a process tree unless list mode is forced; selecting a namespace ID changes the default columns to process-oriented columns. Owner/parent tree modes require nsfs ioctl support. The code treats disappearing `/proc` tasks as normal races and suppresses many transient `EACCES`, `ENOENT`, and `ESRCH` failures so listing remains best-effort.
