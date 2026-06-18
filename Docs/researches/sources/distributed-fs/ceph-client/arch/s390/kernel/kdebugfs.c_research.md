# sources/distributed-fs/ceph-client/arch/s390/kernel/kdebugfs.c

Purpose: creates the architecture debugfs root directory for s390.

Important API and state: exports `struct dentry *arch_debugfs_dir` for other s390 code to place debugfs files under `/sys/kernel/debug/s390`. `arch_kdebugfs_init()` creates the directory at `postcore_initcall` time.

Control flow: initialization calls `debugfs_create_dir("s390", NULL)` and stores the returned dentry. There is no teardown path, matching kernel debugfs lifetime.

Dependencies and integration: used by files such as `hiperdispatch.c` for architecture-scoped debug counters. Depends only on debugfs, initcall ordering, and symbol export.

Risks and test signals: users must tolerate NULL when debugfs is disabled or creation fails. Test by mounting debugfs and checking `/sys/kernel/debug/s390`, plus callers that create children before/after postcore init.
