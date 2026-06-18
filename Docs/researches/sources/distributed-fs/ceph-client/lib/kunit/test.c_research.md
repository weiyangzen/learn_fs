# sources/distributed-fs/ceph-client/lib/kunit/test.c

Purpose: core KUnit runtime: suite initialization, test execution, KTAP reporting, assertion failure handling, parameterized tests, resource cleanup, module integration, and KUnit-owned allocations.

Important APIs/types/functions: `kunit_run_tests()`, `__kunit_test_suites_init()`, `__kunit_test_suites_exit()`, `kunit_init_test()`, `kunit_cleanup()`, `__kunit_do_failed_assertion()`, `__kunit_abort()`, `kunit_array_gen_params()`, `kunit_kmalloc_array()`, `kunit_kfree()`, `kunit_kstrdup_const()`, module notifier `kunit_module_notify()`, and `kunit_run_lock`.

Control flow: suite init creates debugfs state, optional suite init runs, KTAP suite start is printed, each case is initialized and run. Test bodies and cleanup are each wrapped in `kunit_try_catch_run()` kthreads so aborts, faults, and timeouts become test failures. Parameterized tests generate subcases and emit nested KTAP. Module notifications filter suites and run/list tests according to KUnit action settings.

State/persistence: manages module params `enable`, `timeout`, and `stats_enabled`; global suite counter; `current->kunit_test`; suite/case logs; per-test resource lists; debugfs suites; and module suite arrays after filtering.

Dependencies/integration: integrates KUnit attributes/filtering/executor, debugfs, device bus init, hook installation, try/catch, string streams, module notifier, tainting, and kernel allocators.

Risks: cleanup callbacks can delete arbitrary resources, so cleanup loops from the tail one item at a time. Mutating module suite arrays requires valid address checks at exit. Timeout scaling depends on speed attributes. Some parameter init/exit paths are TODO for try/catch coverage.

Test signals: `kunit-test.c` directly validates major runtime pieces; all KUnit tests rely on this file's KTAP output and status propagation.
