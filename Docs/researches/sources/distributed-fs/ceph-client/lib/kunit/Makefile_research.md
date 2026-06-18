# sources/distributed-fs/ceph-client/lib/kunit/Makefile

Purpose: maps KUnit configuration symbols to object files for the core framework, hooks, self-tests, and examples.

Important targets: `kunit.o` aggregates `test.o`, `resource.o`, `user_alloc.o`, `static_stub.o`, `string-stream.o`, `assert.o`, `try-catch.o`, `executor.o`, `attributes.o`, `device.o`, and `platform.o`; `debugfs.o` is conditional; `hooks.o` is built-in whenever KUnit is enabled; self-tests include `kunit-test.o`, `platform-test.o`, built-in-only `string-stream-test.o` and `assert_test.o`; examples build from `kunit-example-test.o`.

Control flow: standard kbuild `obj-$(CONFIG_...)` and `kunit-objs` aggregation select objects according to config values.

State and persistence: no runtime state; build artifact composition is the persistent effect.

Dependencies and integration: integrates Kconfig symbols with kbuild and ensures hook symbols exist even if KUnit itself is modular.

Risks: built-in-only test object constraints must match code assumptions; adding new KUnit core files requires updating the aggregate list; hook build rule must remain available for `test-bug` integration.

Test signals: built-in vs module builds, `CONFIG_KUNIT_DEBUGFS` matrix, `CONFIG_KUNIT_TEST=y/m`, and link checks for hook symbols.
