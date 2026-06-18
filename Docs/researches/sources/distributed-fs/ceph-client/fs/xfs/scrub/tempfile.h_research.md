<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/tempfile.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/tempfile.h

Purpose: declares the repair temporary-file helper interface and provides no-op fallbacks needed by non-repair builds.

Important APIs and types: repair-enabled declarations cover temp inode creation/release, metadir tree adjustment, temp IOLOCK/ILOCK helpers, two-inode locking helpers, preallocation, block copyin callback type `xrep_tempfile_copyin_fn`, temp file copyin, size setting, transaction rolling, local-fork copyout, and tempfile identification. The callback type lets repair modules fill each mapped temp buffer with metadata-specific content while `tempfile.c` owns block mapping and writeback.

Control flow: callers create a tempfile during setup, use lock helpers while staging or exchanging content, and rely on dispatcher teardown to call `xrep_tempfile_rele()`. For non-repair builds, `xrep_tempfile_iolock_both()` simply locks the scrub target and `xrep_tempfile_adjust_directory_tree()`/`xrep_tempfile_rele()`/`xrep_is_tempfile()` collapse to no-op or false.

State and persistence: the header only declares operations; the implementation owns hidden inode state in `sc->tempip` and `sc->temp_ilock_flags`. Dependencies include `CONFIG_XFS_ONLINE_REPAIR`, `struct xfs_scrub`, XFS fork identifiers, file/block offset types, buffer pointers, and inode types.

Risks and test signals: the interface is lock-state sensitive, so signature or precondition changes must be reflected in all repair modules. Non-repair fallback behavior must remain sufficient for shared scrub code that compiles without repair. Test signals are compile coverage for repair-disabled builds and repairs that exercise create, prealloc, copyin, set-isize, exchange, local copyout, and teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/tempfile.h -->
