# sources/distributed-fs/ceph-client/security/inode.c

Purpose: implements `securityfs`, the kernel pseudo-filesystem used by security modules, and exposes a read-only `lsm` file listing active LSM names when security support is enabled.

Important APIs, types, and functions: exported functions are `securityfs_create_file()`, `securityfs_create_dir()`, `securityfs_create_symlink()`, and `securityfs_remove()`. Internal filesystem functions include `securityfs_fill_super()`, `securityfs_get_tree()`, `securityfs_init_fs_context()`, `securityfs_create_dentry()`, `remove_one()`, `lsm_read()`, and `securityfs_init()`.

Control flow: creation pins the singleton filesystem if no parent is supplied, allocates an inode, starts simplefs dentry creation, initializes file/dir/symlink operations and private data, makes the dentry persistent, and returns it. Removal recursively removes a dentry subtree while managing the pin count. `securityfs_init()` creates `/sys/kernel/security`, registers the filesystem, and creates `lsm`.

State and persistence: global `mount` and `mount_count` track singleton mount pins. Created dentries/inodes persist until explicit `securityfs_remove()`. `lsm_read()` lazily builds and caches a comma-separated active LSM string.

Dependencies and integration: depends on simplefs helpers, sysfs mount point creation, VFS/fs_context APIs, LSM active ID list, and module-exported securityfs consumers such as AppArmor, IMA, EVM, and other LSMs.

Risks and test signals: callers must remove created entries; no automatic module cleanup exists. Symlink targets stored in `i_link` require correct free handling. Test signals include creating/removing root and nested entries, symlink cleanup, mount pin balancing, and correct `/sys/kernel/security/lsm` content.
