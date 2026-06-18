# sources/distributed-fs/ceph-client/lib/kunit/debugfs.h

Purpose: internal KUnit debugfs interface header with enabled declarations and disabled no-op stubs.

Important APIs: `kunit_debugfs_create_suite`, `kunit_debugfs_destroy_suite`, `kunit_debugfs_init`, and `kunit_debugfs_cleanup`.

Control flow: preprocessor selects real declarations under `CONFIG_KUNIT_DEBUGFS`; otherwise static inline no-op functions compile callers without conditional code.

State and persistence: no direct state.

Dependencies and integration: includes `kunit/test.h`; consumed by KUnit core and debugfs implementation.

Risks: no-op stubs mean callers must not rely on debugfs side effects when config is disabled.

Test signals: build matrix with `CONFIG_KUNIT_DEBUGFS=y/n` and link checks for callers.
