# sources/distributed-fs/ceph-client/lib/kunit/executor.c

Purpose: discovers, filters, lists, runs, and optionally shuts down after KUnit suites registered in linker sections.

Important APIs/state: module/core parameters `action`, `autorun`, `filter_glob`, `filter`, `filter_action`, and `kunit_shutdown`; getters for action/filter values; `kunit_filter_suites`, `kunit_free_suite_set`, `kunit_exec_run_tests`, `kunit_exec_list_tests`, `kunit_merge_suite_sets`, and built-in `kunit_run_all_tests`.

Control flow: glob filters are parsed into suite and optional test globs, then suites are copied with only matching test cases. Attribute filters from `attributes.c` are applied sequentially to copied suites. Built-in execution merges init and normal suite linker sections, marks init suites, checks `kunit_enabled()`, applies filters, then runs tests, lists tests, or lists tests with attributes based on `action`. Shutdown parameter can poweroff/halt/reboot after execution.

State and persistence: parameters persist as runtime configuration. Filtering allocates copied suite sets and may mark test cases skipped through attribute filtering. Init suite `is_init` flags are set in merged arrays.

Dependencies and integration: depends on linker-section suite arrays, glob matching, module parameters, KUnit core, attribute filtering, and reboot APIs.

Risks: filter strings must be writable for attribute parsing; empty filtered sets are valid; ownership of copied vs linker-section suite arrays differs and cleanup must match; unknown actions only log errors; shutdown behavior is powerful and must be explicit.

Test signals: `executor_test.c` covers glob parsing, suite/test filtering, empty sets, attribute filters, and skip action; boot-time KTAP output and `kunit.py` listing modes validate integration.
