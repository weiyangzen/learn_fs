# sources/distributed-fs/ceph-client/lib/kunit/executor_test.c

Purpose: self-tests KUnit executor filtering and attribute-filter behavior.

Important tests/helpers: `parse_filter_test`, `filter_suites_test`, `filter_suites_test_glob_test`, `filter_suites_to_empty_test`, `parse_filter_attr_test`, `filter_attr_test`, `filter_attr_empty_test`, `filter_attr_skip_test`, plus fake suite allocation and suite-set cleanup helpers.

Control flow: tests create fake suites over dummy cases, invoke `kunit_filter_suites()` with glob or attribute filters, register cleanup with KUnit actions, and assert resulting suite/test counts, names, and skip status.

State and persistence: fake suites are KUnit-managed allocations; copied suite sets are freed through registered actions. Some tests use mutable local filter strings because parser mutates input.

Dependencies and integration: included directly by `executor.c` for built-in KUnit test builds and registered as suite `kunit_executor_test`.

Risks: fake cases only validate filtering metadata, not real execution; direct inclusion means static executor helpers are visible but can complicate build boundaries; expected skip behavior relies on mutation in attribute filtering.

Test signals: this file is the primary regression signal for executor filter semantics and empty-set handling.
