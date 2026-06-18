<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/dir.c -->
# sources/distributed-fs/ceph-client/fs/vboxsf/dir.c

Purpose: Implements vboxsf directory file operations, dentry revalidation, lookup, create, mkdir, atomic open, unlink/rmdir, rename, and symlink inode operations.

Important APIs, types, and functions: Defines `vboxsf_dir_fops`, `vboxsf_dentry_ops`, and `vboxsf_dir_iops`. Key helpers are `vboxsf_dir_open()`, `vboxsf_dir_emit()`, `vboxsf_dir_iterate()`, `vboxsf_dentry_revalidate()`, `vboxsf_dir_lookup()`, `vboxsf_dir_create()`, `vboxsf_dir_atomic_open()`, `vboxsf_dir_unlink()`, `vboxsf_dir_rename()`, and `vboxsf_dir_symlink()`.

Control flow: Opening a directory sends a host create/open request for the dentry, verifies `SHFL_FILE_EXISTS`, reads all entries into `vboxsf_dir_info`, and closes the host handle. Iteration walks buffered variable-sized `shfl_dirinfo` records and emits fake inode numbers based on position. Lookup stats the host path and instantiates a new VFS inode when found. Create and atomic open issue `SHFL_FN_CREATE`, instantiate dentries from returned host attributes, and optionally retain a host file handle for the opened file. Removal, rename, and symlink convert dentries to shared-folder paths and call the corresponding host wrappers.

State and persistence: Directory listings are cached only for the opened directory file. Persistent changes happen on the VirtualBox host shared folder via create/remove/rename/symlink host calls. Parent inodes set `force_restat` after mutations so later revalidation refreshes cached attributes.

Dependencies and integration points: Depends on `utils.c` for path conversion, inode allocation, stat, and revalidation; `file.c` for handle wrapping during atomic open; and `vboxsf_wrappers.c` for host HGCM calls. Integrates with VFS dcache, dentry operations, name lookup, and inode operation tables.

Risks and test signals: Risks include corrupt host directory records, fake inode overflow, stale dentries under host-side changes, path conversion failures, incorrect directory-versus-file rename flags, symlink support differences, and leaked handles on error. Test readdir with many and malformed names, NLS conversion failures, negative and positive dentry revalidation, exclusive create, atomic open create, unlink/rmdir/symlink, rename over existing targets, and parent timestamp restat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/dir.c -->
