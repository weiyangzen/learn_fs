# sources/distributed-fs/ceph-client/lib/kunit/kunit-example-test.c

Purpose: example KUnit suite demonstrating expectations/assertions, skipping, suite/test fixtures, static stubs, private test data, resources, parameterized tests, dynamic parameter arrays, slow-test attributes, and init-section suites.

Important APIs/patterns: `KUNIT_EXPECT_*`, `KUNIT_ASSERT_*`, `kunit_skip`, `kunit_mark_skipped`, `kunit_activate_static_stub`, `kunit_deactivate_static_stub`, `KUNIT_ARRAY_PARAM`, `KUNIT_CASE_PARAM`, `KUNIT_CASE_PARAM_WITH_INIT`, `kunit_alloc_resource`, `kunit_find_resource`, `kunit_put_resource`, `kunit_register_params_array`, `KUNIT_CASE_SLOW`, `kunit_test_suites`, and `kunit_test_init_section_suites`.

Control flow: the main `example` suite runs suite init/exit around per-test init/exit and several cases. Static stub tests redirect `add_one()` to `subtract_one()`. Parameterized tests iterate over static and dynamically generated arrays, optionally using parent test resources. An init-section suite tests `__init` code but keeps suite/case metadata in `__refdata` for debugfs result access.

State and persistence: test state lives in `struct kunit`, `test->priv`, managed allocations/resources, active static stubs, parameter arrays, and suite metadata. Most state is automatically cleaned by KUnit at test or parameterized-test teardown.

Dependencies and integration: depends on KUnit core and static stub support. It is built under `CONFIG_KUNIT_EXAMPLE_TEST` as documentation-through-code and a smoke test for many KUnit features.

Risks: example tests intentionally include skipped cases; `example_params_test()` skips non-power-of-two values and then divides by the value, relying on skip abort semantics for zero; static stubs must be deactivated; dynamic parameter allocation must be tied to the correct parent context.

Test signals: running the example suite validates broad KUnit API behavior, KTAP output for skip/slow/parameterized cases, static stubs, resources, and init-suite support.
