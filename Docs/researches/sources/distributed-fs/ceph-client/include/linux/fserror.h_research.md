# sources/distributed-fs/ceph-client/include/linux/fserror.h

Purpose: declares the filesystem error reporting interface used to route I/O, media-loss, metadata, and shutdown errors to superblock-level reporting and fsnotify/filesystem callbacks.

Important APIs and types: `enum fserror_type` distinguishes buffered read/write, direct I/O read/write, data lost, and metadata errors. `struct fserror_event` packages async work, superblock, optional inode, byte range, error type, and negative errno. `fserror_mount()` and `fserror_unmount()` manage superblock error-reporting lifecycle. `fserror_report()` is the generic reporter, while inline helpers specialize common cases: `fserror_report_io()`, `fserror_report_data_lost()`, `fserror_report_file_metadata()`, `fserror_report_metadata()`, and `fserror_report_shutdown()`.

Control flow: code detecting an error calls a helper with the affected inode/superblock, range, type, error, and allocation mask. The event can be queued via its work item and later delivered to superblock error reporting, including `super_operations.report_error` when a filesystem supplies it.

State and persistence: events are transient in-memory records, but they report failures that may imply persistent corruption or data loss. `super_block.s_pending_errors` accounts in-flight reporting. Filesystems may persist additional health state in their callback.

Dependencies and integration points: depends on VFS superblock/inode types, workqueues, GFP allocation context, and the `report_error` callback in `struct super_operations`.

Risks and test signals: risks include reporting from reclaim/IO contexts with unsuitable GFP flags, losing range/type fidelity, flooding reports, and unmount races with queued events. Tests should inject buffered/direct I/O errors, metadata corruption reports, data-loss notifications, shutdown reporting, allocation failures, and unmount while events are pending.
