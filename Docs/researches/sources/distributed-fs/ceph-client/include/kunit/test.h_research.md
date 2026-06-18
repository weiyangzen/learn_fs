<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/test.h -->
# sources/distributed-fs/ceph-client/include/kunit/test.h

## Purpose
`test.h` is the main KUnit public API. It defines test cases, suites, running test state, suite registration, test-managed allocation helpers, logging, skip/fail mechanics, expectations, assertions, and parameterized-test helpers.

## Important APIs, types, and functions
Core types include `enum kunit_status`, `enum kunit_speed`, `struct kunit_attributes`, `struct kunit_case`, `struct kunit_suite`, `struct kunit_suite_set`, `struct kunit_params`, and `struct kunit`. Registration macros include `KUNIT_CASE*`, `kunit_test_suites()`, `kunit_test_suite()`, and init-section variants. Runtime APIs include `kunit_init_test()`, `kunit_run_tests()`, suite filtering/listing helpers, `kunit_cleanup()`, `kunit_kmalloc_array()`, `kunit_kfree()`, `kunit_kstrdup_const()`, `kunit_vm_mmap()`, `kunit_mark_skipped()`, and `kunit_skip()`. Assertion families include `KUNIT_EXPECT_*` and `KUNIT_ASSERT_*` for booleans, integers, pointers, strings, memory, NULL, and error pointers.

## Control flow
Suites are registered by placing pointers in dedicated ELF sections. The executor filters and runs suites, invoking optional suite init/exit and per-test init/exit. Expectations record failures and continue; assertions route through `__kunit_do_failed_assertion()` and then abort via `__kunit_abort()` / `kunit_try_catch_throw()`. Parameter generators lazily provide values and descriptions for repeated case execution.

## State and persistence behavior
`struct kunit` owns per-case mutable state: status, resources, logs, parameter value/index, last-seen location, parent context, and private fixture data. `struct kunit_suite` stores suite-wide status comments, debugfs/log pointers, and init status. Test-managed allocations persist until cleanup unless released early.

## Dependencies and integration points
The API depends on KUnit assertion definitions, try/catch, list/spinlock/slab/string helpers, module infrastructure, static keys, and linker sections. It integrates with debugfs logging, TAP-style output, module load/unload, boot-time built-in test execution, and memory mapping helpers.

## Risks and test signals
Risks include side effects in assertion expressions, continuing after failed expectations when code required an assertion, parameter arrays with stale lifetime, resources touched from multiple threads without cleanup synchronization, and linker-section registration mistakes. Test signals include KUnit selftests, compile coverage of assertion macro type handling, suite filtering/listing behavior, skip output, resource cleanup after aborts, and parameterized test enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/test.h -->
