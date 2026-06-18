# sources/distributed-fs/ceph-client/lib/kunit/attributes.c

Purpose: implements KUnit test and suite attributes, attribute printing, attribute filter parsing, and filtering of suite test cases by attributes.

Important APIs/types: internal `struct kunit_attr`, `kunit_attr_filter_name`, `kunit_print_attr`, `kunit_get_filter_count`, `kunit_next_attr_filter`, and `kunit_filter_attr_tests`. Supported attributes are `speed`, `module`, and `is_init`.

Control flow: attribute descriptors provide get/to-string/filter/default/print functions. Filters parse comma-separated expressions by locating an operator from `<`, `>`, `!`, or `=`, temporarily NUL-terminating the name, and returning a filter pointing into the mutable input string. Filtering copies the suite, allocates a new test-case array, evaluates default, suite, and case values, includes matching tests, or marks nonmatching tests skipped when action is `skip`.

State and persistence: static attribute descriptor table is immutable after init. Filtering allocates copied suites/test arrays and may mutate original test case status when skip action is used.

Dependencies and integration: depends on KUnit test and attributes headers, string comparison, logging, and suite iteration. Executor code chains glob filtering with these attribute filters.

Risks: filter parsing mutates the input string and requires writable storage; skip action mutates original `struct kunit_case` before copying; string filters only allow `=` and `!=`; empty filtered suites return NULL and must be treated as no match rather than allocation failure.

Test signals: executor self-tests cover filter count, parsing, attribute matching, empty results, and skip behavior.
