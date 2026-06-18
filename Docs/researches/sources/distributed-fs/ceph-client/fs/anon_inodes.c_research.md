# sources/distributed-fs/ceph-client/fs/anon_inodes.c

Purpose: Provides the anonymous inode infrastructure used by kernel subsystems that need file descriptors without real filesystem objects.

Important APIs and functions: `anon_inode_getfile()`, `anon_inode_getfile_fmode()`, and `anon_inode_getfd()` create files/fds backed by the singleton anonymous inode. `anon_inode_create_getfile()` and `anon_inode_create_getfd()` allocate unique anon inodes with LSM security initialization. `anon_inode_make_secure_inode()` is exported for secure inode creation. `anon_inode_getattr()` masks file type bits for legacy userspace expectations.

Control flow: `anon_inode_init()` mounts `anon_inodefs` and allocates the singleton inode at fs init time. Internal `__anon_inode_getfile()` pins the file-operations module, either reuses the singleton inode or creates a secure inode, allocates a pseudo file on the anon mount, assigns mapping and private data, and unwinds module/inode refs on error. FD helpers wrap the file helper with `FD_ADD()`.

State and persistence: Global read-mostly state consists of `anon_inode_mnt` and `anon_inode_inode`. Per-created files persist caller-provided `private_data`, file ops, flags, and optionally a unique inode security context. No disk persistence exists.

Dependencies and integration points: Uses pseudo filesystem helpers, `alloc_anon_inode()`, `alloc_file_pseudo()`, LSM `security_inode_init_security_anon()`, module ownership, and fd allocation helpers. Many subsystems such as eventfd, epoll, io_uring-like interfaces, and KVM-style devices rely on this pattern.

Risks: Module refcounting must pair with file release paths. Secure anon inodes intentionally clear `S_PRIVATE` and invoke LSM policy, so callers must pass correct context inodes. Legacy stat behavior masks `S_IFMT`, which is unusual compared with normal inodes.

Test signals: Singleton file/fd creation, custom `f_mode`, secure inode creation with LSM allow/deny, module owner failure, getattr mode masking, d_path dynamic names, and cleanup after `alloc_file_pseudo()` errors.
