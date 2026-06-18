# sources/distributed-fs/ceph-client/lib/kunit/kunit-test.c

Purpose: self-tests the core KUnit infrastructure rather than product code. It validates try/catch behavior, fault catching when enabled, managed resources, deferred actions, logging, status transitions, `current->kunit_test`, KUnit-managed devices/drivers, and static stubs.

Important APIs/types/functions: `kunit_try_catch_test_context`, `kunit_test_resource_context`, `kunit_resource_test_*`, `kunit_log_test`, `kunit_status_*`, `kunit_current_*`, `kunit_device_*`, and `kunit_stub_test`. It registers suites through `kunit_test_suites()`.

Control flow: each suite creates focused KUnit cases. Try/catch cases initialize `struct kunit_try_catch`, run either a normal or throwing callback, and assert whether catch ran. Resource cases allocate, remove, destroy, and clean nested resources to verify reference and LIFO cleanup rules. Device tests register KUnit devices/drivers and assert devm cleanup and probe/remove paths.

State/persistence: uses in-memory fake KUnit contexts, resource lists, action counters, log streams, `current->kunit_test`, and temporary device-model registrations. It intentionally calls `kunit_cleanup()` on fake tests.

Dependencies/integration: depends on `kunit/test.h`, `kunit/resource.h` behavior indirectly, KUnit device helpers, string streams, static stubs, kernel device model, and optional `CONFIG_KUNIT_FAULT_TEST` and `CONFIG_KUNIT_DEBUGFS`.

Risks: several cases mutate `current->kunit_test` and fake resource lists; failures in cleanup can mask later assertions. Fault tests depend on architecture/config behavior. Device tests rely on bus registration/refcount correctness.

Test signals: the file is itself a test signal. Passing suites indicate KUnit core error handling, cleanup ordering, logs, device helpers, and static stub lifecycle are internally consistent.
