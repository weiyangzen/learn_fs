<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/super.c -->
# sources/distributed-fs/ceph-client/fs/vboxsf/super.c

Purpose: Registers the vboxsf filesystem, parses mount/reconfigure options, connects to the VirtualBox shared folder host service, maps a host share into a superblock, and manages superblock/inode caches.

Important APIs, types, and functions: Defines mount parameters `nls`, `uid`, `gid`, `ttl`, `dmode`, `fmode`, `dmask`, and `fmask`; module parameter `follow_symlinks`; `vboxsf_super_ops`; `vboxsf_context_ops`; and `vboxsf_fs_type`. Main functions are `vboxsf_parse_param()`, `vboxsf_fill_super()`, `vboxsf_alloc_inode()`, `vboxsf_free_inode()`, `vboxsf_put_super()`, `vboxsf_statfs()`, `vboxsf_setup()`, `vboxsf_get_tree()`, `vboxsf_reconfigure()`, `vboxsf_init_fs_context()`, module init, and module exit.

Control flow: Mount setup lazily creates the inode cache, connects to the guest device, selects UTF-8 and symlink behavior, parses options, loads NLS when needed, allocates a BDI id, maps the named host folder, stats the root, initializes a root inode, and attaches `vboxsf_sbi` to the superblock. Reconfigure updates options and reapplies them to the root inode. Unmount unmaps the host folder, frees BDI/NLS/IDR state, and destroys superblock private data. Module exit disconnects and destroys the inode cache once global setup was performed.

State and persistence: Runtime state includes global setup flags, inode slab cache, BDI id allocator, the host client connection, and per-superblock `vboxsf_sbi` with options, root handle, NLS table, inode IDR, and root host attributes. Host folder mappings persist until unmount.

Dependencies and integration points: Integrates with fs_context mount API, anonymous superblocks, VFS inode allocation/freeing, NLS, backing-device info, VirtualBox guest HGCM wrappers, module parameters, and module/filesystem registration.

Risks and test signals: Risks include partial mount cleanup leaks, old binary mount data rejection, NLS lifetime mistakes, root inode initialization failures, remount option drift, stale IDR entries before RCU inode freeing, and guest-device removal. Test mount/unmount loops, invalid option masks, non-UTF8 names, old mount helper data, missing VirtualBox guest device, symlink mode toggle, statfs, reconfigure, and module unload after active mounts are gone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/super.c -->
