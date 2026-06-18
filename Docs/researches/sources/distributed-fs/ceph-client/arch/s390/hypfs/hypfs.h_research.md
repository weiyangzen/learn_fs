<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs.h -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs.h

Purpose: Central header for s390 hypfs, defining filesystem modes, exported creation helpers, diagnostic init/exit interfaces, and the common debugfs file callback model.

Important APIs/types/functions: Defines `REG_FILE_MODE`, `UPDATE_FILE_MODE`, and `DIR_MODE`; declares `hypfs_mkdir()`, `hypfs_create_u64()`, `hypfs_create_str()`, LPAR and VM init/create/exit functions, `hypfs_diag0c_init/exit()`, `hypfs_sprp_init/exit()`, and `hypfs_fs_init()`. Defines `struct hypfs_dbfs_data` and `struct hypfs_dbfs_file`.

Control flow: Header wrappers use `IS_ENABLED(CONFIG_S390_HYPFS_FS)` so the core can call `hypfs_fs_init()` regardless of whether the mounted filesystem view is compiled.

State and persistence: `struct hypfs_dbfs_file` persists per-debugfs-file metadata, callback pointers, lock, and dentry. `struct hypfs_dbfs_data` is per-read generated data.

Dependencies and integration points: Shared by all hypfs implementation files and by `inode.c`. It bridges diagnostic producers and the common debugfs reader in `hypfs_dbfs.c`.

Risks: Callback contracts are important: `data_create()` must set buffer, free pointer, and size consistently; `data_free()` must match allocation method. Incorrect mode constants affect hypfs file permissions.

Test signals: Build checks across config variants, debugfs file reads, mounted hypfs tree creation, and callback allocation/free fault injection.

Source read size: 82 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs.h -->
