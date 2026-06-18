<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/utils.c -->
# sources/distributed-fs/ceph-client/fs/vboxsf/utils.c

Purpose: Provides shared vboxsf utility code for inode allocation/initialization, host stat operations, inode revalidation, getattr/setattr, path and filename charset conversion, and directory listing buffers.

Important APIs, types, and functions: Exports `vboxsf_new_inode()`, `vboxsf_init_inode()`, `vboxsf_create_at_dentry()`, `vboxsf_stat()`, `vboxsf_stat_dentry()`, `vboxsf_inode_revalidate()`, `vboxsf_getattr()`, `vboxsf_setattr()`, `vboxsf_path_from_dentry()`, `vboxsf_nlscpy()`, `vboxsf_dir_info_alloc()`, `vboxsf_dir_info_free()`, and `vboxsf_dir_read_all()`.

Control flow: New inodes get cyclic IDR inode numbers and generation bumps on wraparound. Initialization maps SHFL mode bits to Linux mode bits, applies mount masks/overrides, selects regular/directory/symlink operation tables, sets owner ids, size, block counts, and timestamps. Revalidation stats the host when TTL expires or `force_restat` is set, reinitializes the inode, and invalidates cached pages when mtime advanced. Setattr opens the host object for attribute writes, sends separate information calls for mode/times and size, then restats. Path conversion builds root-relative raw dentry paths and optionally converts through the configured NLS table to UTF-8.

State and persistence: Maintains guest inode numbers in the superblock IDR, inode cached attributes, pagecache invalidation state, and directory-list buffers. Persistent effects occur on the host through `SHFL_INFO_SET` for mode, times, and size.

Dependencies and integration points: Depends on VFS inode/dentry/path APIs, NLS conversion, folio/pagecache invalidation, IDR, mount options from `vboxsf_sbi`, and host wrappers for create, fsinfo, and directory info.

Risks and test signals: Risks include mode/type mismatches during revalidation returning `-ESTALE`, stale pagecache when mtime granularity or host changes are odd, path buffer overflow, invalid UTF-8/NLS conversion, setattr partial updates, IDR wrap generation behavior, and directory buffer leaks. Test TTL and forced restat paths, host-side edits, chmod/truncate/utime, non-ASCII names, long paths, type changes under cached dentries, directory reads with `-EILSEQ`, and inode number reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/utils.c -->
