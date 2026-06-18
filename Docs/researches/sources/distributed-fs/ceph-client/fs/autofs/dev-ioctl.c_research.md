# sources/distributed-fs/ceph-client/fs/autofs/dev-ioctl.c

Purpose: Implements the `/dev/autofs` miscellaneous-device ioctl control plane used by automount daemons to manage covered autofs mounts and reconnect to busy mount trees.

Important APIs and functions: `_autofs_dev_ioctl()` validates and dispatches device ioctls. Command handlers implement version/protocol queries, open/close mount control fds, ready/fail wait release, pipefd reset, catatonic mode, timeout updates, requester lookup, expire, ask-umount, and is-mountpoint checks. `autofs_dev_ioctl_init()` and `autofs_dev_ioctl_exit()` register/deregister the misc device.

Control flow: The dispatcher checks ioctl type/range, restricts most commands to `CAP_SYS_ADMIN`, copies a variable-sized `struct autofs_dev_ioctl`, validates version and path rules, looks up the handler through a nospec-protected table index, obtains the referenced autofs file when needed, enforces oz-mode except catatonic, runs the handler, then copies the fixed header back to userspace. Mount discovery climbs mount stacks with `find_autofs_mount()`.

State and persistence: Handlers mutate autofs superblock state: daemon pipe, `oz_pgrp`, mount namespace id, catatonic flag, global or per-dentry expiry timeouts, and wait queue release status. Returned fields include ioctlfd, requester uid/gid, may-umount, mountpoint device, and covering superblock magic.

Dependencies and integration points: Integrates with miscdevice, fdtable helpers, VFS path lookup and mount traversal, autofs wait/expire code, mount namespace identity, daemon pipe preparation, capability checks, and uapi ioctl structures.

Risks: ABI validation is security critical: path strings must be bounded and terminated, command indexes must be nospec-safe, and non-admin commands limited. `setpipefd` must only revive catatonic mounts and must reject PID namespace changes.

Test signals: Version mismatch, missing/invalid path, openmount by device, closemount, ready/fail tokens, setpipefd while non-catatonic, requester through covered mounts, expire loop returning `-EAGAIN`, ismountpoint with and without ioctlfd, compat ioctl, and non-admin denial.
