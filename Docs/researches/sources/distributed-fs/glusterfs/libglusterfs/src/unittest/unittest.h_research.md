## sources/distributed-fs/glusterfs/libglusterfs/src/unittest/unittest.h

Purpose: this header adapts GlusterFS code for cmocka-based unit tests. Under `UNIT_TESTING`, it includes cmocka headers, redirects selected allocation macros, and replaces `assert` with cmocka's `mock_assert` mechanism so tests can expect assertion failures.

Important APIs and macros: it declares `mock_assert`, undefines `GF_CALLOC` and `GF_FREE`, maps them to `test_calloc` and `test_free`, and redefines `assert(expression)` to call `mock_assert`. Outside unit testing, `REQUIRE` and `ENSURE` are no-op contract markers used by tests and helper code.

Control flow: this file is entirely preprocessor-driven. In a unit-test build, source files including it get cmocka allocation tracking and assertion interception. In normal builds, the test contract macros disappear and no cmocka dependency is introduced.

State and persistence: no runtime state is stored here. Its state impact is indirect: allocations route through cmocka and asserts become catchable failures.

Dependencies and integration: integrates with cmocka and GlusterFS memory macros. It is a test harness boundary, not production code. Files such as `mem_pool_unittest.c` rely on it to make intentional asserts observable.

Risks: because it rewrites core macros, inclusion order matters. Any source that expects production `GF_CALLOC`, `GF_FREE`, or libc `assert` semantics in a unit-test build can behave differently. The duplicate `#ifdef UNIT_TESTING` nesting is redundant but harmless.

Test signals: compilation under both unit-test and non-unit-test configurations is the primary signal. Unit tests that use `expect_assert_failure` confirm the assert shim works.
