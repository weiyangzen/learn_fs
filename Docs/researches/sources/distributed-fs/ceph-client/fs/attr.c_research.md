# sources/distributed-fs/ceph-client/fs/attr.c

Purpose: Implements generic VFS attribute-change permission checks, inode metadata copying, size-limit validation, setuid/setgid stripping, and `notify_change()` dispatch to filesystem `setattr`.

Important APIs and functions: `setattr_should_drop_sgid()`, `setattr_should_drop_suidgid()`, `setattr_prepare()`, `inode_newsize_ok()`, `setattr_copy()`, `may_setattr()`, and `notify_change()` are exported core helpers. Internal `chown_ok()` and `chgrp_ok()` implement idmapped permission logic; `setattr_copy_mgtime()` handles multigrain timestamp updates.

Control flow: `notify_change()` requires the inode locked, runs immutable/append/touch checks, rejects chmod on symlinks, truncates timestamps, evaluates killpriv and setid stripping, validates idmapped uid/gid mappings, calls LSM `security_inode_setattr()`, breaks delegations unless delegated, then invokes the filesystem `->setattr` or `simple_setattr()`. Successful changes generate fsnotify and security post hooks.

State and persistence: The file mutates in-memory inode uid/gid/mode/timestamps through `setattr_copy()`; actual persistence is delegated to each filesystem's setattr implementation. It also sends `SIGXFSZ` when extending beyond `RLIMIT_FSIZE` and protects swapfiles from truncation.

Dependencies and integration points: Central VFS dependency used by filesystem setattr paths, idmapped mounts, user namespaces, capabilities, LSM, fsnotify, file delegation, verity, swapfile protection, and timestamp infrastructure.

Risks: Permission behavior must preserve longstanding Unix semantics while supporting idmapped mounts. Incorrect ordering can allow privilege retention, invalid id mappings, or delegation races. Symlink chmod rejection is a deliberate compatibility/security stance.

Test signals: chown/chgrp under idmapped and non-idmapped mounts, chmod setgid clearing, setuid/setgid kill on write, truncate past rlimit/s_maxbytes, swapfile truncate denial, verity truncate denial, invalid uid/gid mapping `-EOVERFLOW`, delegation `-EWOULDBLOCK`, and multigrain timestamp updates.
