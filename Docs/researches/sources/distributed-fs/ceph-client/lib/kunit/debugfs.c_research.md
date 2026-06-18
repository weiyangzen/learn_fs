# sources/distributed-fs/ceph-client/lib/kunit/debugfs.c

Purpose: exposes KUnit suite logs and manual run triggers through debugfs under `/sys/kernel/debug/kunit/<suite>/`.

Important APIs: `kunit_debugfs_init`, `kunit_debugfs_cleanup`, `kunit_debugfs_create_suite`, and `kunit_debugfs_destroy_suite`. File operations back `results` and `run` files.

Control flow: initialization creates the root directory. Suite creation allocates suite and per-test `string_stream` logs, enables auto-newline behavior, creates a suite directory, adds read-only `results`, and adds writable `run` unless the suite uses init sections. Reading results emits KTAP headers, per-test logs, suite log, and final suite status. Writing `run` invokes `__kunit_test_suites_init()` for that suite.

State and persistence: persistent state includes `debugfs_rootdir`, suite debugfs dentries, suite/test log streams, and stored last-run output until destroyed or overwritten by another run.

Dependencies and integration: depends on debugfs, seq_file, KUnit core, test-bug hooks, and `string-stream`. Called by KUnit suite lifecycle code when `CONFIG_KUNIT_DEBUGFS` is enabled.

Risks: partial log allocation rolls back streams but debugfs creation errors are not deeply handled; manual rerun excludes init suites; concurrent reading and logging relies on `string_stream` locking; debugfs may be absent or disabled.

Test signals: manual debugfs run/read smoke tests, KTAP parser validation, suite destruction leak checks, and config-disabled inline stub coverage from `debugfs.h`.
