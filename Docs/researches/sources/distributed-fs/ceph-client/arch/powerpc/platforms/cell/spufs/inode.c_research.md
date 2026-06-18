# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/inode.c

Purpose: implements the spufs filesystem: inode allocation, context/gang directory creation, mount option parsing, root setup, and module initialization/exit.

Important APIs: `spufs_create()` is the syscall-facing creation entry. `spufs_mkdir()` creates a context directory and fills it from `file.c` descriptors. `spufs_create_context()` validates flags, isolation support, NOSCHED privilege, gang liveness, and affinity constraints. `spufs_create_gang()` creates gang directories. Mount support is provided through `spufs_init_fs_context`, `spufs_parse_param`, `spufs_fill_super`, and `spufs_get_tree`.

Control flow: context creation allocates an inode and `spu_context`, stores the context in `SPUFS_I(inode)`, populates files, optionally adds debug entries, opens the created directory as an fd, and rolls back via recursive removal on failure. Directory release removes the subtree and calls `spu_forget()`. Affinity setup validates neighbor context relationships and available SPUs before linking affinity lists.

State and dependencies: uses a slab cache for `spufs_inode_info`, `spufs_sb_info` for the debug mount flag, device tree `/spu-isolation` loader data, scheduler init/exit, syscall registration, and VFS helpers. Risks include partial-create rollback, affinity race conditions, mount option ownership, and isolated loader lifetime. Test signals include mount options, `spu_create` flag validation, context fd close cleanup, gang close behavior, debug mount contents, and module load/unload.
